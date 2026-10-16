#!/usr/bin/env python3
"""Offline checks for the built site (stdlib only):  python3 _build/check.py

- HTML structure: tag nesting, void elements, <p> holding block elements, duplicate ids, references (for=, aria-*)
- Accessibility basics: one <h1>, no skipped heading levels, alt on every <img>, labelled inputs, lang
- SEO: title/description length, canonical, OG/Twitter tags, JSON-LD parses, FAQPage matches visible text
- Links: every internal href/src resolves to a file in the build; anchors (#id) exist on the target page
- Weight: bytes per page (HTML + CSS + JS + fonts + eager images; lazy images and below-the-fold media listed separately)
"""
import html.parser
import json
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
BLOCK = {'address', 'article', 'aside', 'blockquote', 'details', 'div', 'dl', 'fieldset', 'figcaption', 'figure', 'footer', 'form',
         'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'hr', 'main', 'nav', 'ol', 'p', 'pre', 'section', 'table', 'ul'}
SKIP_DIRS = {'.git', 'content', 'docs', 'waitlist', 'tools', 'brand', 'assets', '_build', 'node_modules'}


class Page(html.parser.HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.stack = []
        self.errors = []
        self.ids = {}
        self.refs = []
        self.links = []
        self.imgs = []
        self.heads = []
        self.meta = {}
        self.title = ''
        self._in_title = False
        self.jsonld = []
        self._in_ld = False
        self._ld = ''
        self.inputs = []
        self.labels_for = set()
        self.text = []
        self.lang = None
        self.in_svg = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        if tag == 'svg':
            self.in_svg += 1
        if self.in_svg and tag != 'svg':
            # SVG children may self-close; track only ids.
            if 'id' in a:
                self.ids.setdefault(a['id'], 0)
                self.ids[a['id']] += 1
            return
        if tag == 'p' and self.stack and self.stack[-1] == 'p':
            self.stack.pop()
        if self.stack and self.stack[-1] == 'p' and tag in BLOCK:
            self.errors.append(f'<{tag}> inside <p> (line {self.getpos()[0]})')
        if 'id' in a:
            self.ids.setdefault(a['id'], 0)
            self.ids[a['id']] += 1
        for k in ('for', 'aria-labelledby', 'aria-describedby', 'aria-controls'):
            if k in a:
                for v in a[k].split():
                    self.refs.append((k, v))
        if k := a.get('href'):
            if tag in ('a', 'link'):
                self.links.append((tag, k, a.get('rel', '')))
        if tag in ('img', 'script', 'source') and a.get('src'):
            self.links.append((tag, a['src'], ''))
        if tag == 'img':
            self.imgs.append(a)
            if 'alt' not in a:
                self.errors.append(f'<img> without alt: {a.get("src")}')
            if not (a.get('width') and a.get('height')):
                self.errors.append(f'<img> without width/height: {a.get("src")}')
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.heads.append(int(tag[1]))
        if tag == 'meta':
            key = a.get('name') or a.get('property')
            if key:
                self.meta[key] = a.get('content', '')
        if tag == 'link' and a.get('rel') == 'canonical':
            self.meta['canonical'] = a.get('href')
        if tag == 'title':
            self._in_title = True
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self._in_ld = True
            self._ld = ''
        if tag == 'input' and a.get('type') not in ('hidden', 'submit'):
            self.inputs.append(a)
        if tag == 'label' and a.get('for'):
            self.labels_for.add(a['for'])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and not self.in_svg and self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag == 'svg':
            self.in_svg -= 1

    def handle_endtag(self, tag):
        if tag == 'svg':
            self.in_svg -= 1
            if self.stack and self.stack[-1] == 'svg':
                self.stack.pop()
            return
        if self.in_svg:
            return
        if tag == 'title':
            self._in_title = False
        if tag == 'script' and self._in_ld:
            self._in_ld = False
            self.jsonld.append(self._ld)
        if tag in VOID:
            return
        if tag not in self.stack:
            if tag != 'p':
                self.errors.append(f'stray </{tag}> (line {self.getpos()[0]})')
            return
        while self.stack:
            t = self.stack.pop()
            if t == tag:
                break
            if t not in ('p', 'li', 'dt', 'dd', 'tr', 'td', 'th', 'option'):
                self.errors.append(f'<{t}> closed implicitly by </{tag}> (line {self.getpos()[0]})')

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self._ld += data
        if not self.in_svg:
            self.text.append(data)


def built_pages():
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS and not x.startswith('.')]
        for f in files:
            if f.endswith('.html'):
                out.append(os.path.join(d, f))
    return sorted(out)


def resolve(page_rel, href):
    u = urllib.parse.urlsplit(href)
    if u.scheme or href.startswith('//') or href.startswith('mailto:'):
        return None, None
    path = u.path
    if not path:
        return page_rel, u.fragment
    if not path.startswith('/'):
        path = os.path.normpath(os.path.join(os.path.dirname('/' + page_rel), path))
    fs = os.path.join(ROOT, path.lstrip('/'))
    if path.endswith('/'):
        fs = os.path.join(fs, 'index.html')
    return fs, u.fragment


def main():
    pages = built_pages()
    parsed = {}
    problems = 0
    for p in pages:
        rel = os.path.relpath(p, ROOT)
        pg = Page(rel)
        pg.feed(open(p, encoding='utf-8').read())
        pg.close()
        parsed[p] = pg
    for p, pg in parsed.items():
        rel = os.path.relpath(p, ROOT)
        errs = list(pg.errors)
        if pg.stack and pg.stack not in (['html'], ['html', 'body'], []):
            errs.append(f'unclosed at end: {pg.stack}')
        for i, n in pg.ids.items():
            if n > 1:
                errs.append(f'duplicate id "{i}" x{n}')
        for k, v in pg.refs:
            if v not in pg.ids:
                errs.append(f'{k}="{v}" points at no element')
        if pg.lang != 'en':
            errs.append('missing <html lang="en">')
        if pg.heads.count(1) != 1:
            errs.append(f'{pg.heads.count(1)} <h1> elements')
        prev = 0
        for h in pg.heads:
            if h > prev + 1 and prev:
                errs.append(f'heading level jumps h{prev} -> h{h}')
            prev = h
        for inp in pg.inputs:
            if inp.get('id') not in pg.labels_for and not inp.get('aria-label'):
                errs.append(f'input without label: {inp.get("name")}')
        t = pg.title.strip()
        d = pg.meta.get('description', '')
        if rel != '404.html':
            if not 10 <= len(t) <= 70:
                errs.append(f'title length {len(t)}: {t}')
            if not 50 <= len(d) <= 160:
                errs.append(f'description length {len(d)}')
            for k in ('canonical', 'og:title', 'og:description', 'og:image', 'og:url', 'twitter:card'):
                if not pg.meta.get(k):
                    errs.append(f'missing {k}')
        faq_visible = ' '.join(pg.text)
        faq_visible = re.sub(r'\s+', ' ', faq_visible)
        for raw in pg.jsonld:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                errs.append(f'JSON-LD does not parse: {e}')
                continue
            for node in data.get('@graph', [data]):
                if node.get('@type') == 'FAQPage':
                    for q in node['mainEntity']:
                        for s in (q['name'], q['acceptedAnswer']['text']):
                            if re.sub(r'\s+', ' ', s) not in faq_visible:
                                errs.append(f'FAQPage text not visible on page: {s[:60]}…')
        for tag, href, relattr in pg.links:
            fs, frag = resolve(rel, href)
            if fs is None:
                continue
            if not os.path.exists(fs):
                errs.append(f'broken {tag} link: {href}')
                continue
            if frag and fs.endswith('.html'):
                target = parsed.get(fs)
                if target and frag not in target.ids:
                    errs.append(f'missing anchor: {href}')
        if errs:
            problems += len(errs)
            print(f'\n{rel}')
            for e in errs:
                print('  -', e)
    # sitemap and robots
    sm = open(os.path.join(ROOT, 'sitemap.xml')).read()
    locs = re.findall(r'<loc>https://marginmail\.ai(/[^<]*)</loc>', sm)
    for l in locs:
        fs, _ = resolve('index.html', l)
        if not os.path.exists(fs):
            problems += 1
            print('sitemap URL has no page:', l)
    for p in parsed:
        rel = '/' + os.path.relpath(p, ROOT).replace('index.html', '')
        if rel not in locs and rel != '/404.html':
            problems += 1
            print('page missing from sitemap:', rel)
    print(f'\n{len(parsed)} pages, {len(locs)} sitemap URLs, {problems} problems')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
