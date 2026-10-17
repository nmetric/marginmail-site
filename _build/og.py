#!/usr/bin/env python3
"""Render per-page social cards (1200x630 PNG) for comparison, guide and best-of pages.

    python3 _build/og.py        # then python3 _build/build.py picks them up

Uses the brand card's layout (brand/final/web/social-card.svg): ruled warm paper, the Clay margin rule, a pencil note in
the margin, the title in Newsreader with a Clay underline, the lockup and the domain. No third-party logos (trademark caution).
Renders with headless Chrome from a throwaway local server so the self-hosted fonts load. Needs Google Chrome; stdlib only.
"""
import functools
import html
import http.server
import os
import re
import shutil
import subprocess
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import md  # noqa: E402

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
TMP = os.path.join(HERE, '.og')

TEMPLATE = """<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="/css/site.css">
<style>
html,body{margin:0;background:#FAF7F2}
.c{position:relative;width:1200px;height:630px;overflow:hidden;background:#FAF7F2}
.r{position:absolute;left:0;right:0;height:2px;background:#EFE8DE}
.v{position:absolute;left:196px;top:0;bottom:0;width:4px;background:#C2531F}
.n{position:absolute;left:14px;top:178px;width:168px;text-align:center;font:500 34px/38px Caveat,'Bradley Hand',cursive;color:#6F371B;transform:rotate(-5deg)}
.t{position:absolute;left:248px;top:150px;width:880px;font:500 84px/90px Newsreader,Georgia,serif;font-variation-settings:'opsz' 72;letter-spacing:-.02em;color:#1D1B18}
.t .u{position:relative;white-space:nowrap}
.t svg{position:absolute;left:0;bottom:-16px;width:100%;height:22px;overflow:visible}
.s{position:absolute;left:250px;top:432px;width:860px;font:400 30px/40px -apple-system,BlinkMacSystemFont,'SF Pro Text',Inter,system-ui,sans-serif;color:#5C554B}
.l{position:absolute;left:250px;top:520px;height:60px}
.l svg{height:60px;width:auto;display:block}
.d{position:absolute;right:76px;top:540px;font:500 24px -apple-system,BlinkMacSystemFont,'SF Pro Text',Inter,system-ui,sans-serif;color:#8A8174}
</style></head><body><div class="c">
RULES<div class="v"></div><div class="n">NOTE</div>
<div class="t" id="t">TITLE</div><div class="s">SUB</div><div class="l">LOCKUP</div><div class="d">marginmail.ai</div></div>
<script>
// Fit the title: shrink until it is at most two lines and the subtitle has room.
var t=document.getElementById('t'), size=84;
function fit(){ t.style.fontSize=size+'px'; t.style.lineHeight=Math.round(size*1.07)+'px'; }
document.fonts.ready.then(function(){
  t.style.top='96px'; fit();
  while (t.getBoundingClientRect().height > 2*Math.round(size*1.07) + 4 && size > 44) { size -= 2; fit(); }
  t.style.top = (408 - t.getBoundingClientRect().height) + 'px';
  document.title='ready';
});
</script></body></html>"""


def underline(width):
    # The brand card's underline: a slightly rising pencil line with a swash back.
    pts = []
    x = 0
    while x <= width:
        y = 10 + 0.8 * __import__('math').sin(x / 41) * .45 - (x / max(1, width)) ** 2 * 3.2
        pts.append(f'{x:.0f} {y:.2f}')
        x += 6
    d = 'M' + 'L'.join(pts) + f'L{width - 2} 5.4Q{width * .52:.0f} 19 {width * .16:.0f} 16.5'
    return (f'<svg viewBox="0 0 {width + 8} 24" preserveAspectRatio="none"><path d="{d}" fill="none" stroke="#C2531F" stroke-width="5" '
            f'stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></svg>')


def cards():
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, 'content/comparisons'))):
        if not f.endswith('.md') or f == 'index.md':
            continue
        meta, body = md.front_matter(open(os.path.join(ROOT, 'content/comparisons', f), encoding='utf-8').read())
        h1 = re.search(r'^# (.+)$', body, re.M).group(1)
        name = re.sub(r'^MarginMail vs (.+?)[:,].*$', r'\1', md.plain(h1))
        if name == md.plain(h1):
            name = re.sub(r'^(?:An? )?(.+?) alternative.*$', r'\1', md.plain(h1))
        out.append((f'compare-{f[:-3]}', f'MarginMail and <span class="u">{html.escape(name)}{underline(300)}</span>',
                    'An honest comparison for the Mac: features, privacy, AI and price.', 'checked Oct 16, sources inside'))
    for f in sorted(os.listdir(os.path.join(ROOT, 'content/seo/pages'))):
        if not f.endswith('.md'):
            continue
        meta, _ = md.front_matter(open(os.path.join(ROOT, 'content/seo/pages', f), encoding='utf-8').read())
        text = md.plain(meta.get('og_image_text') or meta.get('h1'))
        words = text.split(' ')
        last = words.pop()
        title = f'{html.escape(" ".join(words))} <span class="u">{html.escape(last)}{underline(220)}</span>'
        note = 'fair, dated, sourced' if meta.get('section') == 'best' else 'a plain guide'
        out.append((f'{meta.get("section", "page")}-{meta["slug"]}', title, 'MarginMail: a native Mac email app for Gmail, with your calendar and people built in.', note))
    return out


def main():
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    lockup = open(os.path.join(ROOT, 'brand/final/lockup/lockup-horizontal-footer-40.svg'), encoding='utf-8').read()
    lockup = re.sub(r'<\?xml[^>]*\?>', '', lockup)
    rules = ''.join(f'<div class="r" style="top:{y}px"></div>' for y in (110, 202, 294, 386, 478, 570))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    handler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    prof = os.path.join(TMP, 'profile')
    try:
        for key, title, sub, note in cards():
            page = TEMPLATE.replace('RULES', rules).replace('NOTE', html.escape(note)).replace('TITLE', title).replace('SUB', html.escape(sub)).replace('LOCKUP', lockup)
            open(os.path.join(TMP, f'{key}.html'), 'w', encoding='utf-8').write(page)
            out = os.path.join(ROOT, 'og', f'{key}.png')
            subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--user-data-dir={prof}', '--force-device-scale-factor=1',
                            '--virtual-time-budget=3000', '--window-size=1200,630', f'--screenshot={out}',
                            f'http://127.0.0.1:{port}/_build/.og/{key}.html'], check=True, capture_output=True)
            print('og/' + key + '.png', os.path.getsize(out))
    finally:
        srv.shutdown()
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == '__main__':
    main()
