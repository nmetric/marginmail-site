"""A small Markdown subset to HTML converter (stdlib only) for marginmail.ai content files.

Supports: front matter, ATX headings, paragraphs, **bold**, *em*, `code`, [links](url), bare URLs,
- / 1. lists, pipe tables and soft line breaks. Straight quotes become typographic quotes outside code.
Internal links to pages that don't exist yet are rendered as plain text and reported.
"""
import html
import re

WARNINGS = []


def front_matter(text):
    """Return (meta dict, body). Values: "quoted", [list], or bare."""
    meta = {}
    if not text.startswith('---\n'):
        return meta, text
    end = text.index('\n---\n', 4)
    for line in text[4:end].splitlines():
        if ':' not in line:
            continue
        k, v = line.split(':', 1)
        v = v.strip()
        if v.startswith('['):
            v = re.findall(r'"([^"]*)"', v)
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        meta[k.strip()] = v
    return meta, text[end + 5:]


def smart(s):
    """Typographic quotes for already-escaped text (no tags inside)."""
    s = re.sub(r'(^|[\s(\[{—–-])&quot;', r'\1“', s)
    s = s.replace('&quot;', '”')
    s = s.replace('&#x27;', "'")
    s = re.sub(r"(^|[\s(\[{—–-])'", r'\1‘', s)
    s = s.replace("'", '’')
    return s


class Inline:
    def __init__(self, known=None, page=''):
        self.known = known
        self.page = page

    def link_ok(self, url):
        if self.known is None or not url.startswith('/'):
            return True
        path = url.split('#')[0].split('?')[0]
        if path == '':
            return True
        if not path.endswith('/') and '.' not in path.rsplit('/', 1)[-1]:
            path += '/'
        return path in self.known

    def __call__(self, text):
        slots = []

        def keep(h):
            slots.append(h)
            return f'\x00{len(slots) - 1}\x00'

        def code(m):
            return keep(f'<code>{html.escape(m.group(1), quote=False)}</code>')
        text = re.sub(r'`([^`]+)`', code, text)

        def link(m):
            label, url = m.group(1), m.group(2).strip()
            inner = self(label)
            if not self.link_ok(url):
                WARNINGS.append(f'{self.page}: link to missing page {url} rendered as text')
                return keep(inner)
            ext = url.startswith('http')
            attrs = ' rel="noopener"' if ext else ''
            return keep(f'<a href="{html.escape(url)}"{attrs}>{inner}</a>')
        text = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', link, text)

        def bare(m):
            url = m.group(0).rstrip('.,;')
            tail = m.group(0)[len(url):]
            shown = re.sub(r'^https?://(www\.)?', '', url)
            if len(shown) > 60:
                shown = shown[:57] + '…'
            return keep(f'<a href="{html.escape(url)}" rel="noopener">{html.escape(shown)}</a>') + tail
        text = re.sub(r'https?://[^\s<>()]+', bare, text)

        text = html.escape(text, quote=True)
        text = smart(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', text)
        text = text.replace('→', '→')
        return re.sub(r'\x00(\d+)\x00', lambda m: slots[int(m.group(1))], text)


def slugify(s):
    s = re.sub(r'<[^>]+>', '', s).lower()
    s = re.sub(r'[’\'"“”]', '', s)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def split_row(line):
    line = line.strip()
    if line.startswith('|'):
        line = line[1:]
    if line.endswith('|'):
        line = line[:-1]
    return [c.strip() for c in line.split('|')]


def blocks(body):
    """Yield (kind, data) blocks: heading(level, text), para(lines), ul(items), ol(items), table(rows), code(lang, text)."""
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('```'):
            lang = line[3:].strip()
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].startswith('```'):
                buf.append(lines[j])
                j += 1
            yield 'code', (lang, '\n'.join(buf))
            i = j + 1
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            yield 'heading', (len(m.group(1)), m.group(2).strip())
            i += 1
            continue
        if line.lstrip().startswith('|'):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                cells = split_row(lines[i])
                if not all(re.fullmatch(r':?-{2,}:?', c) for c in cells if c):
                    rows.append(cells)
                i += 1
            yield 'table', rows
            continue
        if re.match(r'^\s*[-*]\s+', line):
            items = []
            while i < len(lines) and (re.match(r'^\s*[-*]\s+', lines[i]) or (lines[i].startswith('  ') and lines[i].strip() and items)):
                if re.match(r'^\s*[-*]\s+', lines[i]):
                    items.append(re.sub(r'^\s*[-*]\s+', '', lines[i]))
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            yield 'ul', items
            continue
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < len(lines) and (re.match(r'^\s*\d+\.\s+', lines[i]) or (lines[i].startswith('   ') and lines[i].strip() and items)):
                if re.match(r'^\s*\d+\.\s+', lines[i]):
                    items.append(re.sub(r'^\s*\d+\.\s+', '', lines[i]))
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            yield 'ol', items
            continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|\s*[-*]\s+|\s*\d+\.\s+|\s*\||```)', lines[i]):
            buf.append(lines[i])
            i += 1
        yield 'para', buf


def sections(body):
    """Split a page body into (h1, intro_blocks, [(h2 text, [blocks])])."""
    h1 = None
    intro = []
    secs = []
    for kind, data in blocks(body):
        if kind == 'heading' and data[0] == 1 and h1 is None:
            h1 = data[1]
            continue
        if kind == 'heading' and data[0] == 2:
            secs.append((data[1], []))
            continue
        (secs[-1][1] if secs else intro).append((kind, data))
    return h1, intro, secs


def render(blks, inline, table_class='tbl', h_offset=0):
    out = []
    for kind, data in blks:
        if kind == 'heading':
            lvl = min(6, data[0] + h_offset)
            out.append(f'<h{lvl} id="{slugify(data[1])}">{inline(data[1])}</h{lvl}>')
        elif kind == 'para':
            out.append('<p>' + '<br>'.join(inline(l.strip()) for l in data) + '</p>')
        elif kind == 'ul':
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in data) + '</ul>')
        elif kind == 'ol':
            out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in data) + '</ol>')
        elif kind == 'table':
            out.append(table(data, inline, table_class))
        elif kind == 'code':
            out.append(f'<pre><code>{html.escape(data[1], quote=False)}</code></pre>')
    return '\n'.join(out)


def table(rows, inline, cls='tbl'):
    head, body = rows[0], rows[1:]
    margin_col = next((i for i, c in enumerate(head) if re.search(r'\bMargin\b', c)), None)
    # A table whose first data column names apps (best-of) marks the Margin row instead.
    th = ''.join(f'<th scope="col"{" class=m" if i == margin_col else ""}>{inline(c)}</th>' if c else '<td></td>' for i, c in enumerate(head))
    trs = []
    for r in body:
        is_margin_row = margin_col is None and re.search(r'\bMargin\b', r[0] or '')
        cells = []
        for i, c in enumerate(r):
            cl = []
            if i == margin_col:
                cl.append('m')
            if i == 0:
                cells.append(f'<th scope="row">{inline(c)}</th>')
                continue
            cells.append(f'<td{(" class=" + chr(34) + " ".join(cl) + chr(34)) if cl else ""}>{inline(c)}</td>')
        trs.append(f'<tr{" class=mrow" if is_margin_row else ""}>' + ''.join(cells) + '</tr>')
    return (f'<div class="tblwrap" role="region" aria-label="Comparison table" tabindex="0"><table class="{cls}">'
            f'<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>')


def plain(text):
    """Markdown inline -> plain text (for JSON-LD and llms-full)."""
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return html.unescape(smart(html.escape(text.strip(), quote=True)))
