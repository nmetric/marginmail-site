"""Page versions and A/B variants for marginmail.ai (stdlib only).

Page version: a short hash of a page's visible copy (text inside <main>, no CSS/JS/markup), emitted as
<meta name="page-version"> and sent with every visit count and signup, so stats can show conversion per version over
time. When a page's hash changes, build.py appends a line to content/versions.md (state in content/.versions.json).

A/B variants: an optional ```variants block in content/homepage.md. The page as written is variant A and is what the
HTML contains (crawlers and no-JS visitors see A). Each page view picks a variant at random by weight; nothing is
stored, so there's no cookie or localStorage, and a reload can show a different variant. Each view and signup is
counted with its variant id.

    ```variants
    # id | weight | headline | subhead | cta | note        (empty field = keep A's text)
    A | 1
    B | 1 | Find time in the margins of your day. | | |
    ```
Delete the rows (or the block) to stop a test.
"""
import datetime
import hashlib
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = os.path.join(ROOT, 'content', 'versions.md')
STATE = os.path.join(ROOT, 'content', '.versions.json')
FIELDS = ('headline', 'subhead', 'cta', 'note')


def visible_text(body_html):
    t = re.sub(r'<(script|style|svg)\b.*?</\1>', ' ', body_html, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def _first(pattern, body):
    m = re.search(pattern, body, re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<(svg)\b.*?</\1>|<[^>]+>', '', m.group(1), flags=re.S))).strip() if m else ''


class Versions:
    def __init__(self):
        self.state = {}
        if os.path.exists(STATE):
            try:
                self.state = json.load(open(STATE, encoding='utf-8'))
            except ValueError:
                self.state = {}
        self.changes = []

    def record(self, path, body):
        h = hashlib.sha256(visible_text(body).encode()).hexdigest()[:8]
        head = _first(r'<h1[^>]*>(.*?)</h1>', body)
        sub = _first(r'<p class="lead"[^>]*>(.*?)</p>', body) or _first(r'<div class="answer"[^>]*>\s*<p>(.*?)</p>', body)
        old = self.state.get(path)
        if not old or old.get('hash') != h:
            if not old:
                what = f'first recorded; headline “{head}”'
            else:
                bits = []
                if old.get('headline') != head:
                    bits.append(f'headline “{old.get("headline")}” → “{head}”')
                if old.get('subhead') != sub:
                    bits.append(f'subhead “{old.get("subhead", "")[:60]}…” → “{sub[:60]}…”')
                what = '; '.join(bits) or 'body copy changed (headline and subhead unchanged)'
            self.changes.append((path, h, what))
            self.state[path] = {'hash': h, 'headline': head, 'subhead': sub}
        return h

    def save(self):
        if not self.changes or not os.path.isdir(os.path.dirname(LOG)):
            return
        today = datetime.date.today().isoformat()
        new = not os.path.exists(LOG)
        with open(LOG, 'a', encoding='utf-8') as fh:
            if new:
                fh.write('# Page versions\n\nAppended by `_build/build.py` whenever a page\'s visible copy changes. The hash is sent with '
                         'every visit count and signup (`stats.sh --versions`).\n\n| Date | Page | Version | What changed |\n|---|---|---|---|\n')
            for path, h, what in self.changes:
                fh.write(f'| {today} | `{path}` | `{h}` | {what.replace("|", "/")} |\n')
        json.dump(self.state, open(STATE, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


class Variants:
    """Reads the ```variants block from content/homepage.md and renders the swap scripts."""

    def __init__(self, render_headline):
        self.rows = []
        self.render_headline = render_headline
        src = os.path.join(ROOT, 'content', 'homepage.md')
        text = open(src, encoding='utf-8').read() if os.path.exists(src) else ''
        m = re.search(r'```variants\n(.*?)```', text, re.S)
        if not m:
            return
        for line in m.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cells = [c.strip() for c in line.split('|')]
            vid = cells[0]
            if not re.fullmatch(r'[A-Za-z0-9]{1,8}', vid):
                raise SystemExit(f'homepage.md variants: bad id {vid!r}')
            try:
                weight = float(cells[1]) if len(cells) > 1 and cells[1] else 1.0
            except ValueError:
                raise SystemExit(f'homepage.md variants: bad weight in {line!r}')
            fields = {f: (cells[i + 2] if len(cells) > i + 2 else '') for i, f in enumerate(FIELDS)}
            self.rows.append({'id': vid.upper(), 'weight': weight, **fields})
        if self.rows and not any(r['id'] == 'A' for r in self.rows):
            self.rows.insert(0, {'id': 'A', 'weight': 1.0, **{f: '' for f in FIELDS}})

    def active(self):
        return len(self.rows) > 1

    def head_script(self):
        """Pick a variant before anything paints; hide the swappable nodes until the swap (only if not A)."""
        w = [[r['id'], r['weight']] for r in self.rows]
        return ('<style>.ab-pending [data-ab]{visibility:hidden}</style><script>(function(){var w=' + json.dumps(w) +
                ',t=0,i,r;for(i=0;i<w.length;i++)t+=w[i][1];r=Math.random()*t;for(i=0;i<w.length;i++){r-=w[i][1];if(r<0)break}'
                'var v=w[Math.min(i,w.length-1)][0],f=(new URLSearchParams(location.search).get("ab")||"").toUpperCase();'
                'for(i=0;i<w.length;i++)if(w[i][0]===f){v=f;window.__abPreview=1}'
                'window.__ab=v;if(v!=="A")document.documentElement.classList.add("ab-pending");'
                'setTimeout(function(){document.documentElement.classList.remove("ab-pending")},1500)})()</script>\n')

    def apply_script(self):
        """Runs right after the hero is parsed: swap its text, then the CTA buttons further down once the DOM is ready."""
        m = {}
        for r in self.rows:
            if r['id'] == 'A':
                continue
            d = {}
            if r['headline']:
                d['headline'] = self.render_headline(r['headline'])
            if r['subhead']:
                d['subhead'] = html.escape(r['subhead'], quote=False)
            if r['cta']:
                d['cta'] = html.escape(r['cta'], quote=False)
            if r['note']:
                d['note'] = html.escape(r['note'], quote=False)
            m[r['id']] = d
        return ('<script>(function(){var m=' + json.dumps(m, ensure_ascii=False).replace('</', '<\\/') + ',v=m[window.__ab];'
                'function s(){if(!v)return;document.querySelectorAll("[data-ab]").forEach(function(e){var k=e.getAttribute("data-ab");'
                'if(v[k]!=null)e.innerHTML=v[k]});document.querySelectorAll("input[name=x]").forEach(function(e){e.value=window.__abPreview?"":window.__ab})}'
                'function b(){if(!window.__abPreview)return;var d=document.createElement("div");d.textContent="Previewing variant "+window.__ab+" \\u00b7 not counted";'
                'd.style.cssText="position:fixed;right:12px;top:76px;z-index:9999;padding:6px 10px;border-radius:8px;background:#1f1d1a;color:#fff;font:12px/1.3 system-ui,sans-serif;opacity:.85;pointer-events:none";document.body.appendChild(d)}'
                's();document.documentElement.classList.remove("ab-pending");document.addEventListener("DOMContentLoaded",function(){s();b()})})()</script>')
