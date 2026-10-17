#!/usr/bin/env python3
"""Build marginmail.ai into the repo root (GitHub Pages serves it as-is).

    python3 _build/build.py

Python standard library only, plus macOS `sips` for image resizing. Sources:
  content/homepage.md v3 (copy, via _build/copy_home.py)   content/comparisons/*.md   content/seo/pages/*.md
  privacy/ and terms/ legal text (kept verbatim in _build/legal/)   brand/final/   assets/shots/   assets/motion/
Writes: index.html, compare/**, best/**, guides/**, privacy/, terms/, 404.html, img/, sitemap.xml, robots.txt,
llms.txt, llms-full.txt. css/, js/, fonts/ and motion/ are hand-written or copied, not generated.
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import copy_home as C  # noqa: E402
import marks as M  # noqa: E402
import md  # noqa: E402
import abv  # noqa: E402

SITE = 'https://marginmail.ai'
ENDPOINT = 'https://join.marginmail.ai/join'
BUILT = '2026-10-17'
DEFINITION = 'MarginMail is a native Mac email app for Gmail and Google Workspace, with a calendar and a personal CRM built in.'
FOOT_LINE = C.FOOT_LINE
FOOT_SMALL = C.FOOT_SMALL
_HASH = {}


def v(url):
    """Content-hash cache busting: '/css/site.css' -> '/css/site.css?v=<first 10 hex of sha256>'."""
    path = url.split('?')[0]
    if path not in _HASH:
        import hashlib
        with open(os.path.join(ROOT, path.lstrip('/')), 'rb') as fh:
            _HASH[path] = hashlib.sha256(fh.read()).hexdigest()[:10]
    return f'{path}?v={_HASH[path]}'


def version_css_fonts():
    """Stamp the font URLs inside css/site.css with their content hash (idempotent), before the CSS itself is hashed."""
    p = os.path.join(ROOT, 'css/site.css')
    css = open(p, encoding='utf-8').read()
    new = re.sub(r'url\((/fonts/[^)?]+)(?:\?v=[0-9a-f]+)?\)', lambda m: f'url({v(m.group(1))})', css)
    if new != css:
        open(p, 'w', encoding='utf-8').write(new)

esc = lambda s: html.escape(s, quote=True)


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(text)


# =============================================================== images (sips)
IMG = {}


def image(key, src, widths, crop=None, q=72):
    """Resize assets/shots/<src> (optionally cropped x,y,w,h) to img/<key>-<w>.jpg at each width."""
    srcp = os.path.join(ROOT, 'assets/shots', src)
    os.makedirs(os.path.join(ROOT, 'img'), exist_ok=True)
    out = []
    tmp = None
    if crop:
        x, y, w, h = crop
        tmp = os.path.join(ROOT, 'img', f'.crop-{key}.png')
        if not os.path.exists(tmp) or os.path.getmtime(tmp) < os.path.getmtime(srcp):
            # sips treats an offset of 0 as 'centre the crop', so 1 px is the closest it gets to the top-left corner.
            subprocess.run(['sips', '-s', 'format', 'png', '-c', str(h), str(w), '--cropOffset', str(max(1, y)), str(max(1, x)), srcp, '--out', tmp],
                           check=True, capture_output=True)
        base = tmp
    else:
        base = srcp
    bw, bh = [int(v) for v in re.findall(r'pixel(?:Width|Height): (\d+)', subprocess.run(
        ['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', base], check=True, capture_output=True, text=True).stdout)]
    for w in widths:
        rel = f'img/{key}-{w}.jpg'
        dst = os.path.join(ROOT, rel)
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(base):
            subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', str(q[w] if isinstance(q, dict) else q), '--resampleWidth', str(w), base, '--out', dst],
                           check=True, capture_output=True)
        out.append((w, None, '/' + rel))
    if tmp and os.path.exists(tmp):
        os.remove(tmp)
    IMG[key] = dict(srcs=out, w=bw, h=bh)
    return IMG[key]


def srcset(key):
    return ', '.join(f'{v(u)} {w}w' for w, _, u in IMG[key]['srcs'])


def pic(desk, mob, alt, sizes_d, sizes_m, cls='', eager=False, mob_media='(max-width: 767px)'):
    """<picture> with art direction: mob below 768 px, desk above. Width/height from the desktop image."""
    d, m = IMG[desk], IMG[mob] if mob else None
    load = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    dw = d['srcs'][0][0]
    dh = round(dw * d['h'] / d['w'])
    src = v(d['srcs'][0][2])
    s = '<picture>'
    if m:
        s += f'<source media="{mob_media}" srcset="{srcset(mob)}" sizes="{sizes_m}" width="{m["srcs"][0][0]}" height="{round(m["srcs"][0][0] * m["h"] / m["w"])}">'
    s += (f'<img{" class=" + chr(34) + cls + chr(34) if cls else ""} src="{src}" srcset="{srcset(desk)}" sizes="{sizes_d}" '
          f'width="{dw}" height="{dh}" alt="{esc(alt)}" {load}></picture>')
    return s


def build_images():
    image('margin-mac-email-app-gmail-calendar', 'split.png', [1140, 1710], q={1140: 70, 1710: 58})  # LCP: every candidate <= 250 KB
    image('margin-message-reply-bar-note', 'split-detail.png', [420, 716, 1074, 1368], q=72)
    image('margin-calendar-week-unanswered-invites', 'calendar-week.png', [1140, 2280], q=68)
    image('margin-needs-your-answer', 'needs-answer-detail.png', [716, 1074], q=72)
    image('margin-request-card-highlighted-ask', 'stack-detail.png', [560, 840, 1120], q=72)
    image('margin-person-page-crm', 'person.jpg', [720, 1440], q=70)
    image('margin-person-page-local-time', 'person-detail.jpg', [716, 1074], crop=(0, 0, 1400, 780), q=72)


# =============================================================== shared chrome
LOCK = ('<svg width="13" height="13" viewBox="0 0 13 13" aria-hidden="true"><rect x="2.5" y="5.6" width="8" height="6" rx="1.6" fill="none" stroke="#5C554B" stroke-width="1.3"/>'
        '<path d="M4.4 5.6V4.2a2.1 2.1 0 0 1 4.2 0v1.4" fill="none" stroke="#5C554B" stroke-width="1.3"/></svg>')

ORG = {"@type": "Organization", "@id": f"{SITE}/#org", "name": "MarginMail", "url": f"{SITE}/", "logo": f"{SITE}/logo.png",
       "email": "hello@marginmail.ai",
       "description": "MarginMail makes a native Mac email app for Gmail with a calendar and personal CRM built in."}
WEBSITE = {"@type": "WebSite", "@id": f"{SITE}/#site", "url": f"{SITE}/", "name": "MarginMail", "publisher": {"@id": f"{SITE}/#org"}, "inLanguage": "en"}


# Without JavaScript the endpoint redirects back to /?joined=1…#joined (or #already, #join-error); :target shows these.
NOJS_STATES = ('<div class="nojs-state result" id="joined" tabindex="-1"><p class="rt">You’re on the list.</p>'
               '<p class="sub">We’ll email you when your invite is ready. Until then, that’s the only email you’ll get from us.</p></div>'
               '<div class="nojs-state result" id="already" tabindex="-1"><p class="rt">You’re already on the list.</p>'
               '<p class="sub">There’s nothing else to do. We’ll email you when your invite is ready.</p></div>'
               '<div class="nojs-state result" id="join-error" tabindex="-1"><p class="rt">That didn’t go through.</p>'
               '<p class="sub">Check your email address and try again. If it keeps happening, write to '
               '<a href="mailto:hello@marginmail.ai">hello@marginmail.ai</a>.</p></div>')


def joinform(fid, source='', center=False, facts=False, label='Join the beta'):
    """The signup form. Works with JS (inline states); without JS it posts to the endpoint."""
    msg = f'{fid}-msg'
    return (f'<div class="joinbox">'
            f'<form class="join" id="{fid}" action="{ENDPOINT}" method="post" novalidate data-source="{esc(source)}">'
            f'<div class="join-row"><label class="vh" for="{fid}-email">Email address</label>'
            f'<input class="field" id="{fid}-email" type="email" name="email" autocomplete="email" inputmode="email" '
            f'placeholder="you@example.com" required aria-describedby="{msg} {fid}-priv">'
            f'<button class="btn" type="submit" data-ab="cta">{label}</button></div>'
            f'<div class="hp" aria-hidden="true"><label for="{fid}-hp">Leave this empty</label><input id="{fid}-hp" name="hp" tabindex="-1" autocomplete="off"></div>'
            + (f'<input type="hidden" name="source" value="{esc(source)}">' if source else '')
            + '<input type="hidden" name="page" value="__PATH__"><input type="hidden" name="v" value="__PV__">'
            + '<input type="hidden" name="x" value="__AB_DEFAULT__">' +
            f'<p class="join-msg" id="{msg}" role="status" aria-live="polite"></p>'
            f'<p class="priv" id="{fid}-priv">{LOCK}{C.PRIV_LINE}</p>'
            + (f'<p class="facts">{C.SMALL_LINE}</p>' if facts else '') +
            '</form><div class="join-result" role="status" aria-live="polite"></div>'
            + (NOJS_STATES if fid == 'join' else '') + '</div>')


def header(home=False):
    pre = '' if home else '/'
    return (f'<a class="skip" href="#main">Skip to content</a>'
            f'<header class="nav"><a class="brand" href="/" aria-label="MarginMail, home">{nav_lockup()}</a>'
            f'<nav class="nav-links" aria-label="Main"><a class="tl" href="{pre}#how">How it works</a><a class="tl" href="{pre}#privacy">Privacy</a>'
            f'<a class="tl" href="{pre}#faq">FAQ</a><a class="btn sm" href="{pre}#join">Join the beta</a>'
            f'<details class="nav-menu"><summary aria-label="Menu"><svg width="22" height="22" viewBox="0 0 22 22" aria-hidden="true"><path d="M3 7H19M3 15H19" stroke="#1D1B18" stroke-width="1.6" stroke-linecap="round"/></svg></summary>'
            f'<ul><li><a href="{pre}#how">How it works</a></li><li><a href="{pre}#privacy">Privacy</a></li><li><a href="{pre}#faq">FAQ</a></li></ul></details></nav></header>')


_NAV = []


def nav_lockup():
    """The nav lockup, inline so its star can twinkle (the second easter egg). The five Clay arms become <g class="navstar">."""
    if not _NAV:
        svg = open(os.path.join(ROOT, 'brand/final/lockup/lockup-horizontal-nav-28.svg'), encoding='utf-8').read()
        svg = re.sub(r'<\?xml[^>]*\?>', '', svg).strip()
        svg = re.sub(r'<title>.*?</title>', '', svg)
        arms = re.findall(r'<path d="M16\.6 9L[^"]*"[^>]*/>', svg)
        assert len(arms) == 5, 'nav lockup: expected five star arms'
        svg = svg.replace(arms[0], '<g class="navstar">' + arms[0], 1).replace(arms[-1], arms[-1] + '</g>', 1)
        svg = svg.replace('<svg ', '<svg aria-hidden="true" focusable="false" ', 1)
        _NAV.append(svg)
    return _NAV[0]


def moon():
    s = open(os.path.join(ROOT, 'brand/final/motifs/moon.svg')).read()
    d = re.search(r'<path d="([^"]+)"', s).group(1)
    return (f'<svg class="moon" viewBox="0 0 60 60" aria-hidden="true"><path d="{d}" fill="none" stroke="#1D1B18" stroke-opacity=".7" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" pathLength="1" class="dw" style="animation-duration:1600ms;animation-delay:300ms"/>'
            f'<circle cx="46" cy="16" r="1.4" fill="#C2531F" class="fade" style="animation-delay:1500ms"/></svg>')


def footer():
    links = [('Compare MarginMail', '/compare/'), ('Privacy', '/privacy/'), ('Terms', '/terms/'), ('Contact', 'mailto:hello@marginmail.ai')]
    return (f'<footer class="foot" data-seen>{moon()}<div class="in"><div><a class="brand" href="/" aria-label="MarginMail, home"><img src="{v("/img/brand/lockup-footer.svg")}" width="189" height="48" alt="MarginMail" loading="lazy"></a>'
            f'<p class="line">{FOOT_LINE}</p></div>'
            f'<div><nav aria-label="Footer"><ul>' + ''.join(f'<li><a href="{u}">{t}</a></li>' for t, u in links) + '</ul></nav>'
            f'<p class="fine">{FOOT_SMALL}</p></div></div></footer>')


def sky():
    """Fixed background layer: pencil horizon + a hand-drawn sun that rises and sets with scroll (see css .sky)."""
    hz = []
    x = 0
    while x <= 1600:
        hz.append((x, 6 + M.wob(x) * .6))
        x += 10
    segs = []
    # a few pencil lifts so the line reads hand-drawn
    for a, b in ((20, 520), (536, 1110), (1126, 1580)):
        pts = [p for p in hz if a <= p[0] <= b]
        segs.append('M' + 'L'.join(f'{M.f(px)} {M.f(py)}' for px, py in pts))
    horizon = (f'<svg class="horizon" viewBox="0 0 1600 12" preserveAspectRatio="none" aria-hidden="true">'
               f'<path d="{" ".join(segs)}" fill="none" stroke="#1D1B18" stroke-opacity=".13" stroke-width="1.3" stroke-linecap="round" vector-effect="non-scaling-stroke"/></svg>')
    pts = []
    n = 72
    for i in range(n + 2):
        a = -1.9 + 2 * 3.14159265 * i / n
        rr = 58 * (1 + 0.014 * __import__('math').sin(5 * a))
        pts.append((100 + rr * __import__('math').cos(a), 100 + rr * __import__('math').sin(a)))
    ring = 'M' + 'L'.join(f'{M.f(a)} {M.f(b)}' for a, b in pts)
    sun = (f'<svg class="sun" viewBox="0 0 200 200" aria-hidden="true"><defs><radialGradient id="skyglow"><stop offset="0" stop-color="#F2BC5C" stop-opacity=".16"/>'
           f'<stop offset=".45" stop-color="#F2BC5C" stop-opacity=".07"/><stop offset="1" stop-color="#F2BC5C" stop-opacity="0"/></radialGradient></defs>'
           f'<circle cx="100" cy="100" r="100" fill="url(#skyglow)"/><path d="{ring}" fill="none" stroke="#6F371B" stroke-opacity=".2" stroke-width="1.4" stroke-linecap="round"/></svg>')
    return (f'<div class="sky" aria-hidden="true"><div class="tint am"></div><div class="tint pm"></div>{horizon}'
            f'<div class="air"><div class="sx"><div class="sy">{sun}</div></div></div></div>')


# One anonymous page-view count per load (see the privacy policy, "Site visit counts"). No cookies, no IDs, nothing stored
# in the browser. Skipped for automation, Do Not Track / GPC, and localhost (unless ?debug).
BEACON = ('(function(){try{var n=navigator,l=location,q=new URLSearchParams(l.search),d=document;'
          'if(window.__abPreview||n.webdriver||n.doNotTrack=="1"||n.globalPrivacyControl||!n.sendBeacon||(/^(localhost|127\\.)/.test(l.hostname)&&!q.has("debug")))return;'
          'function M(k){var e=d.querySelector("meta[name="+k+"]");return e?e.content:""}'
          'addEventListener("load",function(){var r="";try{r=d.referrer?new URL(d.referrer).hostname:""}catch(e){}'
          'var w=innerWidth,b=JSON.stringify({p:M("page-path")||l.pathname,r:r,v:M("page-version"),x:window.__ab||"",'
          'us:q.get("utm_source")||q.get("s")||q.get("src")||"",um:q.get("utm_medium")||"",uc:q.get("utm_campaign")||"",'
          'rc:q.has("joined")?"":q.get("r")||q.get("ref")||"",d:w<768?"phone":w<1200?"tablet":"desktop"});'
          'n.sendBeacon("' + ENDPOINT.replace("/join", "/hit") + '",new Blob([b],{type:"text/plain"}))})}catch(e){}})();')


def head(title, desc, path, og_title=None, og_desc=None, og_alt=None, ld=None, extra='', motion=(), og_image='/og/margin-og.png'):
    url = SITE + path
    og_alt = og_alt or "MarginMail: Mail that knows what needs you. A native Mac email app for Gmail, with the handwritten note 'give your inbox some margin'."
    ldj = ''
    if ld:
        ldj = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/') + '</script>'
    mcss = ''.join(f'<link rel="stylesheet" href="{v(f"/motion/{m}.css")}">' for m in motion)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="msvalidate.01" content="1951CD811CAF01F1D35718A61772027D">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="page-version" content="__PV__">
<meta name="theme-color" content="#FAF7F2">
<meta name="color-scheme" content="light">
<meta name="application-name" content="MarginMail">
<meta name="apple-mobile-web-app-title" content="MarginMail">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="icon" href="{v('/favicon.svg')}" type="image/svg+xml">
<link rel="icon" href="{v('/favicon-32.png')}" sizes="32x32" type="image/png">
<link rel="icon" href="{v('/favicon-16.png')}" sizes="16x16" type="image/png">
<link rel="apple-touch-icon" href="{v('/apple-touch-icon.png')}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="MarginMail">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(og_title or title)}">
<meta property="og:description" content="{esc(og_desc or desc)}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(og_alt)}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(og_title or title)}">
<meta name="twitter:description" content="{esc(og_desc or desc)}">
<meta name="twitter:image" content="{SITE}{og_image}">
<meta name="twitter:image:alt" content="{esc(og_alt)}">
<link rel="preload" href="{v('/fonts/newsreader-latin.woff2')}" as="font" type="font/woff2" crossorigin>
{extra}<link rel="stylesheet" href="{v('/css/site.css')}">{mcss}
<script>document.documentElement.className+=' js'</script>
<script>{BEACON}</script>
{ldj}
</head>'''


def page(headhtml, body, home=False, motion=(), stickybar=False):
    m = re.search(r'<link rel="canonical" href="https://marginmail\.ai([^"]*)"', headhtml)
    path = m.group(1) if m else '/404'
    pv = versions.record(path, body)
    ab_on = home and AB.active()
    headhtml = headhtml.replace('__PV__', pv).replace('<script>document.documentElement', (AB.head_script() if ab_on else '') + '<script>document.documentElement', 1)
    body = body.replace('__PV__', pv).replace('__PATH__', path).replace('__AB_DEFAULT__', 'A' if ab_on else '')
    if ab_on:
        body = body.replace('<!--ab-apply-->', AB.apply_script(), 1)
    mjs = ''.join(f'<script src="{v(f"/motion/{m}.js")}" defer></script>' for m in motion)
    sb = ('<div class="stickybar" aria-hidden="true"><a class="btn" href="#join" tabindex="-1">Join the beta</a>'
          f'<p>{C.PRIV_LINE}</p></div>') if stickybar else ''
    return (f'{headhtml}\n<body>{sky()}<div class="page"><div class="mrule" aria-hidden="true"></div>{header(home)}'
            f'<main id="main">{body}</main>{footer()}</div>{sb}'
            f'<script src="{v("/js/site.js")}" defer></script>{mjs}\n</body>\n</html>\n')


# =============================================================== homepage
def svg_box(w, h, inner, cls='ov', extra=''):
    return f'<svg class="{cls}" viewBox="0 0 {w} {h}" aria-hidden="true"{extra}>{inner}</svg>'


def note(text, style, rot=-3, size=24, delay=1500, cls='note fade'):
    return (f'<p class="{cls}" aria-hidden="true" style="{style};font-size:{size}px;transform:rotate({rot}deg);'
            f'{"" if "transform-origin" in style else "transform-origin:left top;"}animation-delay:{delay}ms">{text}</p>')


def note_m(text, delay=1500):
    return f'<p class="note-m fade" data-seen aria-hidden="true" style="animation-delay:{delay}ms">{text}</p>'


def sec_head(d, width=600, hid=None):
    return (f'<div class="head" data-seen style="max-width:{width}px"><p class="lbl">{d["lbl"]}</p>'
            f'<h2 class="h2"{" id=" + chr(34) + hid + chr(34) if hid else ""}>{d["h"]}</h2>{note_m(d["note"])}'
            f'<p class="lead">{d["body"]}</p></div>')


def underline_svg(width, sw=2.6, delay=900):
    return (f'<svg viewBox="0 0 {width + 8} 24" preserveAspectRatio="none" aria-hidden="true">'
            f'{M.underline(4, width, 10, sw=sw, delay=delay)}</svg>')


def render_headline(text):
    """A variant headline in the hero's style: the last words carry the Clay underline."""
    words = text.split()
    k = min(3, max(1, len(words) // 2))
    return (f'{esc(" ".join(words[:-k]))} <span class="ul">{esc(" ".join(words[-k:]))}'
            f'{underline_svg(462, sw=3, delay=900)}</span>')


def hero_config(name):
    """What a hero-swap variant's page script needs (abv.Variants.apply_script). 'tour': the product tour in the hero window."""
    if name == 'tour':
        wk = 'margin-calendar-week-unanswered-invites'
        return {'css': v('/motion/tour.css'), 'js': v('/motion/tour.js'), 'label': C.TOUR['label'], 'replay': C.TOUR['replay'],
                'beats': [{'id': i, 'label': lbl, 'aria': aria} for i, lbl, aria in C.TOUR['beats']],
                'video': C.VIDEO_TOUR,  # None keeps the 'See MarginMail in action' button hidden (copy_home.VIDEO_TOUR)
                # The week render the Find time section already uses, same candidates and sizes, so the browser reuses it.
                'week': {'src': v(IMG[wk]['srcs'][0][2]), 'srcset': srcset(wk), 'sizes': '(min-width: 1200px) min(1140px, 100vw - 300px), calc(100vw - 112px)'}}
    raise SystemExit(f'unknown hero visual {name!r}')


versions = abv.Versions()
AB = abv.Variants(render_headline, hero_config)


def responsive_svg(svg):
    """Make a fixed-size board SVG fluid: keep its viewBox, drop width/height."""
    return re.sub(r'(<svg[^>]*?) width="[\d.]+" height="[\d.]+"', r'\1', svg, count=1).replace('style="display:block;overflow:visible"', '')


def component(name):
    return open(os.path.join(ROOT, f'assets/motion/{name}.html'), encoding='utf-8').read().strip()


def home():
    P = []
    # ---- Hero
    hero_sun = ('<svg class="hero-sun" data-seen viewBox="0 0 470 360" aria-hidden="true">'
                '<defs><clipPath id="hsky"><rect width="470" height="262"/></clipPath></defs>'
                + '<g class="rise">' + M.glow(250, 250, 210, op=.5, gid='hg', delay=500, clip='hsky') + '</g>'
                + f'<g clip-path="url(#hsky)"><g class="rise">{M.circle(250, 286, 74, delay=600, sw=1.5)}</g></g>'
                + M.hline(40, 440, 262, sw=1.6, delay=250, dur=1900)
                + M.hline(150, 330, 290, sw=1.2, delay=900, dur=900, opacity=.45)
                + M.hline(200, 290, 312, sw=1.1, delay=1300, dur=700, opacity=.3) + '</svg>')
    hero_sun = hero_sun.replace('class="hero-sun"', 'class="hero-sun d-only"')
    hero_sun_m = ('<svg class="hero-sun-m m-only" data-seen viewBox="0 0 220 80" aria-hidden="true"><defs><clipPath id="mh"><rect width="220" height="60"/></clipPath></defs>'
                  + '<g class="rise">' + M.glow(130, 56, 70, op=.45, gid='mhg', delay=400, clip='mh') + '</g>'
                  + f'<g clip-path="url(#mh)"><g class="rise">{M.circle(130, 66, 24, delay=500, sw=1.4)}</g></g>' + M.hline(40, 214, 60, sw=1.4, delay=200, dur=1600) + '</svg>')
    hero_arrow = svg_box(640, 200, M.arrow(600, 58, 528, 34, bend=.35, color=M.MINK, delay=1500), cls='hero-arrow')
    hero_up = svg_box(60, 46, M.arrow(30, 40, 46, 10, bend=-.3, delay=1500), cls='hero-up')
    shot = IMG['margin-mac-email-app-gmail-calendar']
    W = 1140
    IH = round(W * shot['h'] / shot['w'])
    hero_alt = ('MarginMail on a Mac: the inbox, Imogen Hale’s message from Kiln & Co. with the asked sentence, “Could we find 30 minutes '
                'next week to talk through scope?”, highlighted, the reply bar note “Wants 30 min next week on scope”, and today’s calendar.')
    marker = svg_box(W, IH, M.marker(.352 * W, .621 * W, .729 * IH, .019 * IH, delay=2200, op=.42), cls='ov t-up')
    P.append('<section class="sec hero" id="top"><div class="in">' + hero_sun + hero_sun_m +
             '<p class="lbl" style="margin-bottom:22px">Free during the beta · For Mac</p>'
             '<div class="h1wrap" data-seen><h1 class="h1" data-ab="headline">Mail that knows <span class="ul">what needs you.' + underline_svg(462, sw=3, delay=900) + '</span></h1>'
             f'<p class="hero-note write" data-ab="note" style="animation-delay:1300ms">{C.HERO_NOTE}</p>{hero_arrow}{hero_up}</div>'
             f'<p class="lead" data-ab="subhead">{C.HERO_SUB}</p>' + joinform('join', facts=True) +
             '<figure class="hero-shot" data-seen style="margin-left:0;margin-right:0"><div class="win"><div class="bar" aria-hidden="true"><i></i><i></i><i></i></div><div class="pic">'
             + pic('margin-mac-email-app-gmail-calendar', 'margin-message-reply-bar-note', hero_alt,
                   '(min-width: 1200px) min(1140px, 100vw - 300px), calc(100vw - 112px)', 'calc(100vw - 32px)', eager=True)
             + marker + '</div></div></figure></div></section><!--ab-apply-->')

    # ---- What is MarginMail?
    wi = C.WHAT_IS
    P.append(f'<section class="sec whatis" id="how"><div class="in"><h2 class="lbl">{wi["lbl"]}</h2>'
             f'<p class="lead"><b>{wi["lead"]}</b>{wi["rest"]}</p></div></section>')

    # ---- Manifesto + six cards
    m = C.MANIFESTO
    cards = ''
    for i, (kind, title, line, feats, nt) in enumerate(m['cards']):
        mark = M.card_mark(kind, 700 + i * 150).replace('width="220" height="56" viewBox', 'viewBox').replace('style="display:block;overflow:visible"', '')
        cards += (f'<div class="card mcard">{mark}<h3>{title}</h3><p>{line}</p><p class="feats">{feats}</p>'
                  f'<p class="hand fade" aria-hidden="true" style="animation-delay:{1300 + i * 150}ms">{nt}</p></div>')
    bracket = ('<svg class="bracket" viewBox="0 0 16 100" preserveAspectRatio="none" aria-hidden="true"><path d="M14 0H2V100H14" fill="none" stroke="#C2531F" '
               'stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" pathLength="1" class="dw" style="animation-duration:700ms;animation-delay:600ms"/></svg>')
    P.append(f'<section class="sec"><div class="in"><h2 class="lbl">{m["lbl"]}</h2>{note_m(m["note"])}'
             f'<div class="manifesto-text" data-seen>{bracket}<p>{m["text"]}</p>'
             + note(m['note'], 'left:-204px;top:190px;width:170px;white-space:normal', rot=-4) + '</div>'
             f'<div class="cards" data-seen>{cards}</div></div></section>')

    # ---- Margins & the stack
    d = C.S_STACK
    bm = ('<svg width="10" height="18" viewBox="0 0 10 18" aria-hidden="true"><path d="M8 2H3V16H8" fill="none" stroke="#6F371B" '
          'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    chips = ''.join(f'<div class="card chip"><h3 class="lbl">{bm}{k}</h3><q>{q.strip("“”")}</q></div>' for k, q in d['chips'])
    arrow_strip = svg_box(1000, 60, M.arrow(560, 36, 1050, 22, bend=-.06, color=M.CLAY, sw=2.6, delay=900), cls='ov d-only',
                          extra=' style="top:100%;height:60px"')
    P.append('<section class="sec alt"><div class="in">' + sec_head(d) +
             f'<div class="stack-fig motion" data-seen>{component("stack")}{arrow_strip}'
             + note(d['note'], 'right:calc(44% + 14px);top:calc(100% + 18px);text-align:right;transform-origin:right top', rot=-3) + '</div>'
             f'<div class="chips">{chips}</div><p class="body after">{d["below"]}</p></div></section>')

    # ---- One window: Split view (Oct 17, R2). The real render, plus a play-once moment: the cursor clicks Imogen's name and
    # her page opens over the reader; then A accepts Lena's invitation and its row leaves the list. One Clay mark (the
    # bracket over the three panes), one margin note. Reduce Motion: the end state, still. Coordinates are the 2880 px render's.
    d = C.S_SPLIT
    split_alt = ('MarginMail’s Split view on a Mac: the inbox, Imogen Hale’s message from Kiln & Co. and today’s calendar side by side. '
                 'Clicking her name opens her person page, with her local time and what she’s waiting on, and an unanswered '
                 'invitation in the inbox is accepted with the A key and files itself.')
    big = v(IMG['margin-mac-email-app-gmail-calendar']['srcs'][-1][2])
    av = f"background-image:url({big})"
    page_html = (
        '<div class="sv-page" aria-hidden="true"><p class="sv-crumb"><span>‹</span> Kiln &amp; Co. identity <span>›</span> <b>Imogen Hale</b></p>'
        f'<div class="sv-top"><i class="sv-av" style="{av}"></i><div><p class="sv-name">Imogen Hale</p>'
        '<p class="sv-role">Founder, <b>Kiln &amp; Co.</b></p><p class="sv-met">Introduced by Sofia Marin · Hudson, NY</p>'
        '<p class="sv-time"><i></i>Last contact today · 12:41 PM for Imogen</p></div>'
        '<p class="sv-btns"><span class="k">Email</span><span>Find a time</span></p></div>'
        '<div class="sv-cards"><div class="sv-card"><p class="sv-h">Timeline</p>'
        '<div class="sv-li"><b>Kiln &amp; Co. identity</b><span>Today 8:49 AM</span><em>Could we find 30 minutes next week to talk through scope?</em></div>'
        '<div class="sv-li"><b>Sofia Marin introduced you</b><span>Sun</span><em>Imogen, meet Nora. Fernhill did our boxes…</em></div>'
        '<p class="sv-h sv-h2">Notes</p><div class="sv-li"><em>Opening a second studio in the spring.</em></div></div>'
        '<div class="sv-side"><div class="sv-card"><p class="sv-h">Tasks</p><p class="sv-sub">Waiting on you</p>'
        '<div class="sv-task"><i></i><div><b>30 minutes next week on scope</b><span>Re: Kiln &amp; Co. identity</span></div></div></div>'
        '<div class="sv-card"><p class="sv-h">Contact</p><div class="sv-li"><span class="sv-k">Work email</span><b>imogen@kilnandco.com</b></div>'
        '<div class="sv-li"><span class="sv-k">Time zone</span><b>Eastern Time · 12:41 PM for Imogen</b></div></div></div></div></div>')
    cursor = ('<svg class="sv-cursor" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 2.5V19.2L9.3 15.1L12.2 21.6L15 20.4L12.2 14H18.3Z" '
              'fill="#1D1B18" stroke="#fff" stroke-width="1.4" stroke-linejoin="round"/></svg><i class="sv-click" aria-hidden="true"></i>')
    moment = (page_html
              + '<span class="sv-pill" aria-hidden="true">Accepted</span>'
              + f'<div class="sv-close" aria-hidden="true"><i class="sv-row"></i><div class="sv-move"><i style="background-image:url({big})"></i></div></div>'
              + '<div class="sv-keys" aria-hidden="true"><span class="a">A</span><span>M</span><span>D</span></div>' + cursor)
    pts = []
    x = 6
    while x <= 1134:
        pts.append((x, 4 + M.wob(x) * .5))
        x += 12
    brace = ('M3 22L5 6' + ''.join(f'L{M.f(px)} {M.f(py + 2)}' for px, py in pts) + 'L1135 7L1137 22')
    bracket = (f'<svg class="sv-bracket" viewBox="0 0 1140 26" preserveAspectRatio="none" aria-hidden="true">'
               + M._path(brace, M.CLAY, 2.6, 900, 6300).replace('<path ', '<path vector-effect="non-scaling-stroke" ') + '</svg>')
    P.append('<section class="sec" id="one-window"><div class="in">' + sec_head(d, 660) +
             f'<figure class="splitfig" data-seen>{bracket}'
             + note(d['note'], 'right:4px;top:-58px;text-align:right;transform-origin:right top', rot=-3, delay=7000)
             + '<div class="win"><div class="bar" aria-hidden="true"><i></i><i></i><i></i></div><div class="pic sv">'
             + pic('margin-mac-email-app-gmail-calendar', None, split_alt,
                   '(min-width: 1200px) min(1140px, 100vw - 300px), (min-width: 768px) calc(100vw - 112px), calc(100vw - 32px)', '', cls='sv-img')
             + moment + '</div></div></figure></div></section>')

    # ---- People & Companies
    d = C.S_PEOPLE
    pp = IMG['margin-person-page-crm']
    IW = 720
    IH = round(IW * pp['h'] / pp['w'])
    sx, sy = .536 * IW, .222 * IH
    people_alt = ('Ava Lindqvist’s person page in MarginMail: Head of Brand at Saltmarsh Coffee, her local time (12:41 PM), how you met, '
                  'notes, a timeline of recent mail and meetings, and her tasks.')
    P.append('<section class="sec alt"><div class="in"><div class="row" style="gap:20px">'
             f'<div class="col" style="flex:0 1 400px">{sec_head(d, 390)}</div>'
             f'<div class="col" style="flex:0 1 720px"><div style="position:relative" data-seen>'
             + pic('margin-person-page-crm', 'margin-person-page-local-time', people_alt, '(min-width: 1024px) 720px, calc(100vw - 112px)', 'calc(100vw - 32px)', cls='shot')
             + svg_box(IW, IH, M.star(sx + 10, sy - 2, 7, sw=2.2, delay=900) + M.arrow(.6 * IW, .14 * IH, sx + 22, sy - 8, bend=.25, delay=1400), cls='ov t-up')
             + svg_box(1400, 780, M.star(1222, 214, 13, sw=3, delay=900), cls='ov p-only')
             + note(d['note'], 'left:50%;top:5%', rot=-3, size=21, delay=1700) + '</div></div></div></div></section>')

    # ---- Find time
    d = C.S_TIME
    cal_alt = ('MarginMail’s calendar beside your mail: unanswered meeting invitations are marked, and Needs your answer gathers them, '
               'each with Accept, Maybe and Decline.')
    # The moment: A is pressed on the dashed (unanswered) Saltmarsh walkthrough, it turns solid, and a pencil note says so.
    accept = ('<div class="accept t-up" aria-hidden="true"><div class="ev">Saltmarsh shoot walkthrough<span>11:00 – 11:45 AM</span></div>'
              '<div class="keycaps"><span class="a">A</span><span>M</span><span>D</span></div>'
              + svg_box(26, 26, M.check(13, 13, .7, color=M.CLAY, sw=2.2, delay=1900), cls='chk')
              + '<p class="hand fade" style="animation-delay:2050ms">accepted</p></div>')
    P.append('<section class="sec"><div class="in"><div class="row">'
             f'<div class="col">{sec_head(d, 620)}</div>'
             f'<div class="cals t-up" data-seen>{M.two_cals(400, 24)}'
             + note(d['note'], 'right:6px;top:-40px;text-align:right;transform-origin:right top', rot=-3, delay=2600) + '</div>'
             f'<div class="cals p-only" data-seen>{M.two_cals(358, 22)}</div></div>'
             '<div class="calweek" data-seen><div class="pic">' + pic('margin-calendar-week-unanswered-invites', 'margin-needs-your-answer', cal_alt,
                                         '(min-width: 1200px) min(1140px, 100vw - 300px), calc(100vw - 112px)', 'calc(100vw - 32px)', cls='shot')
             + accept + '</div>' + '</div></div></section>')

    # ---- Live words
    d = C.S_LIVE
    a, b = d['sample']
    P.append('<section class="sec alt"><div class="in"><div class="row" style="gap:40px">'
             f'<div class="col" style="flex:0 1 440px">{sec_head(d, 440)}'
             f'<div class="sample" data-seen aria-hidden="true"><span class="ul">{a}{underline_svg(204, sw=2.6)}</span>{b}'
             + note(d['note'], 'left:-204px;top:8px;width:170px;white-space:normal', rot=-4) + '</div></div>'
             f'<div class="col motion" style="flex:0 1 660px">{component("live-words")}</div></div></div></section>')

    # ---- Skim it
    d = C.S_SKIM
    sk = IMG['margin-request-card-highlighted-ask']
    IW = 560
    IH = round(IW * sk['h'] / sk['w'])
    sw = .036 * IH
    marks = M.marker(.738 * IW, .937 * IW, .376 * IH, sw, delay=900) + M.marker(.07 * IW, .853 * IW, .421 * IH, sw, delay=1300)
    arr = M.arrow(-40, .421 * IH + 40, .05 * IW, .421 * IH + 8, bend=-.25, delay=1600)
    skim_alt = ('A Request card in MarginMail: Marco Reyes’s sentence, “Could you send the signed proof before Thursday so we can hold the press slot?”, '
                'is highlighted, and Why this? explains the card.')
    rows = [('Decided', 'Copper foil on the front only. 4,000 units on the uncoated stock.'),
            ('Still open', 'Which press slot, if the proof is late.'),
            ('Waiting on', 'You, for the signed proof by Thursday.')]
    decided = ('<div class="decided" data-seen role="group" aria-label="Example: What’s been decided"><div class="top"><span class="lbl">What’s been decided</span>'
               '<span class="src">Saltmarsh labels · 14 messages</span></div><dl>'
               + ''.join(f'<div class="r tick" style="animation-delay:{1400 + 450 * i}ms"><dt>{x}</dt><dd>{y}</dd></div>' for i, (x, y) in enumerate(rows))
               + '</dl></div>')
    P.append('<section class="sec"><div class="in"><div class="row rev">'
             f'<div class="col" style="flex:0 1 560px;position:relative">'
             f'<div style="position:relative" data-seen>{pic("margin-request-card-highlighted-ask", None, skim_alt, "(min-width: 1024px) 560px, calc(100vw - 32px)", "", cls="shot")}'
             + svg_box(IW, IH, marks) + svg_box(IW, IH, arr, cls='ov d-only')
             + note(d['note'], f'left:-196px;top:{(.421 * IH + 18) / IH * 100:.1f}%;width:160px;white-space:normal', rot=-4, delay=1800) + '</div></div>'
             f'<div class="col" style="flex:0 1 500px">{sec_head(d, 500)}{decided}</div></div></div></section>')

    # ---- Write it
    d = C.S_WRITE
    P.append('<section class="sec alt"><div class="in"><div class="row">'
             f'<div class="col" style="flex:0 1 500px">{sec_head(d, 500)}<p class="privline">{d["priv"]}</p></div>'
             f'<div class="col" style="flex:0 1 560px;position:relative"><div class="motion" data-seen style="position:relative">{component("write-it")}'
             + svg_box(560, 468, M.arrow(-36, -26, 36, 150, bend=-.32, delay=1400), cls='ov d-only')
             + note(d['note'], 'left:-70px;top:-66px', rot=-3, delay=1700) + '</div></div></div></div></section>')

    # ---- The details: six items, each led by a line icon (3 + 3)
    dd = C.DETAILS
    P.append(f'<section class="sec details"><div class="in"><h2 class="lbl">{dd["lbl"]}</h2><div class="dgrid">'
             + ''.join(f'<div>{M.detail_icon(i)}<div><h3>{x}</h3><p>{y}</p></div></div>' for i, (x, y) in enumerate(dd['items'])) + '</div></div></section>')

    # ---- Made for the Mac. Made for privacy.
    d = C.S_MACPRIV
    diag_d, _ = M.privacy_diagram(1140, 310)
    diag_m, _ = M.privacy_diagram(358, 470, vertical=True)
    diag_alt = ('Diagram: your Mac connects directly to Google, with an optional dotted line to your own Claude; a “MarginMail server” box is crossed out '
                'because there isn’t one, and a tracking pixel bounces off before it reaches the Mac.')
    fix = lambda s: responsive_svg(s).replace(re.search(r'aria-label="[^"]*"', s).group(0), f'aria-label="{esc(diag_alt)}"')
    points = ''
    for i, (t, b) in enumerate(d['points']):
        extra = ''
        if 'blocked' in t:
            pre, post = t.split('blocked')
            t = (f'{pre}<span class="circ">blocked<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'
                 + M.loop(50, 52, 64, 78, sw=2.4, delay=900).replace('<path ', '<path vector-effect="non-scaling-stroke" ') + f'</svg></span>{post}')
            extra = note(d['note'], 'left:120px;top:-34px', rot=-4, delay=1700)
        points += f'<div>{M.priv_icon(i)}<div><h3>{t}</h3><p>{b}</p></div>{extra}</div>'
    P.append('<section class="sec alt" id="privacy"><div class="in">' + sec_head(d, 700) +
             f'<div class="diagram" data-seen><div class="t-up">{fix(diag_d)}</div><div class="p-only" style="max-width:358px;margin:0 auto">{fix(diag_m)}</div></div>'
             f'<div class="pgrid" data-seen>{points}</div></div></section>')

    # ---- Moments of joy (+ the star easter egg)
    d = C.S_JOY

    def scene(w, h, rule, hy, r, gid, copy_top):
        svg, cx = M.sunrise_scene(w, h, rule, hy, r, gid=gid)
        svg = svg.replace(f'width="{w}" height="{h}" viewBox', 'viewBox').replace('style="position:absolute;left:0;top:0"', '')
        # The star is a real button laid over the drawing; drop the SVG's own focus target.
        svg = svg.replace('<g tabindex="0" class="egg" aria-label="A star. Hover or click it.">', '<g class="egg">')
        stx, sty = cx + r * .12, hy - r * 1.6
        btn = (f'<button class="egg-btn" type="button" style="left:{stx / w * 100:.2f}%;top:{sty / h * 100:.2f}%" '
               f'aria-label="A star in the drawing. Press it for a small surprise."></button>'
               f'<p class="psst" aria-hidden="true" style="left:calc({stx / w * 100:.2f}% + 26px);top:calc({sty / h * 100:.2f}% - 34px)">psst, tap the star</p>'
               f'<p class="thanks" aria-hidden="true" style="right:6%;top:{(hy * .32) / h * 100:.1f}%">thanks for looking around</p>')
        return (svg, btn)
    sd, bd = scene(1140, 540, 150, 300, 66, 'jsr', 63)
    sm, bm2 = scene(358, 400, 34, 196, 40, 'msr', 57)
    copy = ('<div class="joy-copy fade" aria-hidden="true" style="animation-delay:2600ms"><p class="t">A clear morning</p>'
            '<p class="s">4 done · 1 not useful · Next notes tomorrow morning</p><p class="c">Next: Saltmarsh label review at 10:00 AM</p>'
            '<p class="b">Back to your mail <kbd>esc</kbd></p></div>')
    joy_alt = 'An empty Margins stack: a line drawing of the sun rising over the horizon, a check mark, and the words “A clear morning.”'
    P.append('<section class="sec"><div class="in">' + sec_head(d, 640) +
             f'<div class="joy-scene t-up" data-seen role="group" aria-label="{esc(joy_alt)}">{sd}{copy}{bd}'
             + note(d['note'], 'left:1.9%;top:43.7%;width:116px;white-space:normal', rot=-4, size=25, delay=3000) + '</div>'
             f'<div class="joy-scene p-only" data-seen role="group" aria-label="{esc(joy_alt)}">{sm}{copy.replace("joy-copy", "joy-copy m")}{bm2}</div></div></section>')

    # ---- Second CTA
    P.append('<section class="sec alt cta"><div class="in center">'
             f'<h2 class="h2" data-seen>{esc(C.CTA["h"].rsplit(" ", 1)[0])} <span class="ul">{esc(C.CTA["h"].rsplit(" ", 1)[1])}{underline_svg(70, sw=3, delay=700)}</span></h2>'
             f'<p class="lead">{C.CTA["body"]}</p>' + joinform('join-end') + '</div></section>')

    # ---- FAQ
    qa = ''.join(f'<div><h3>{q}</h3><p>{a}</p></div>' for q, a in C.FAQ)
    P.append(f'<section class="sec faq" id="faq"><div class="in"><p class="lbl">FAQ</p><h2 class="h2">Questions</h2><div class="qa">{qa}</div></div></section>')

    plain = lambda s: re.sub(r'<[^>]+>', '', s)
    ld = {"@context": "https://schema.org", "@graph": [
        ORG, WEBSITE,
        {"@type": "SoftwareApplication", "@id": f"{SITE}/#app", "name": "MarginMail", "alternateName": "Margin Mail",
         "applicationCategory": "BusinessApplication", "applicationSubCategory": "Email client", "operatingSystem": "macOS 26 or later",
         "url": f"{SITE}/", "image": f"{SITE}/og/margin-og.png",
         "description": DEFINITION + ' It notes what needs you, helps you find meeting times as you type, and gives everyone you write to a page. '
                        'Its optional AI uses Apple Intelligence on your Mac or your own Claude when you click. There’s no MarginMail server, and the AI never sends email.',
         "publisher": {"@id": f"{SITE}/#org"},
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "description": "Free during the beta", "availability": "https://schema.org/PreOrder"},
         "featureList": ["Follow-up, meeting and request notes in the reply bar",
                         "The Margins stack: drag right for Done, left for the back of the stack, with Why this? on every card",
                         "Live words: dates, people, files and promises become actions as you type",
                         "Find a time with both calendars side by side; holds placed when you pick",
                         "Calendar built in: accept, maybe or decline invites with A, M or D",
                         "Split view: inbox, message, calendar and the person's page in one window",
                         "People and Companies: a private personal CRM with a page for everyone you write to, local time, and tasks that close themselves",
                         "Write it: drafts from your notes with your own Claude, on click; never sends",
                         "What's been decided: summaries of long threads",
                         "Request notes found on-device with Apple Intelligence",
                         "Multiple Gmail and Google Workspace accounts in one unified inbox",
                         "Menu bar agenda with Join",
                         "No MarginMail server, no analytics, no read receipts"]},
        {"@type": "WebPage", "@id": f"{SITE}/#webpage", "url": f"{SITE}/", "name": "MarginMail: Mail that knows what needs you · Gmail app for Mac",
         "isPartOf": {"@id": f"{SITE}/#site"}, "about": {"@id": f"{SITE}/#app"}, "dateModified": BUILT, "inLanguage": "en",
         "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + shot['srcs'][0][2]}},
        {"@type": "FAQPage", "@id": f"{SITE}/#faq", "mainEntity": [
            {"@type": "Question", "name": plain(q), "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in C.FAQ]}]}

    hd = IMG['margin-mac-email-app-gmail-calendar']
    hm = IMG['margin-message-reply-bar-note']
    preload = (f'<link rel="preload" as="image" imagesrcset="{srcset("margin-mac-email-app-gmail-calendar")}" '
               f'imagesizes="(min-width: 1200px) min(1140px, 100vw - 300px), calc(100vw - 112px)" media="(min-width: 768px)" fetchpriority="high">\n'
               f'<link rel="preload" as="image" imagesrcset="{srcset("margin-message-reply-bar-note")}" imagesizes="calc(100vw - 32px)" media="(max-width: 767px)" fetchpriority="high">\n')
    hh = head('MarginMail: Mail that knows what needs you · Gmail app for Mac',
              'MarginMail is a native Mac email app for Gmail with your calendar and a page for everyone you write to. Optional private AI that never sends. Free in beta.',
              '/', og_title='MarginMail: Mail that knows what needs you',
              og_desc='Give your inbox some margin. A native Mac email app for Gmail with your calendar and people built in. Private AI that never sends. Free during the beta.',
              ld=ld, extra=preload, motion=('stack', 'live-words', 'write-it'))
    write('index.html', page(hh, ''.join(P), home=True, motion=('stack', 'live-words', 'write-it'), stickybar=True))


# =============================================================== article pages (compare, best, guides)
PAGES = []  # (path, title, lastmod, kind)


def load(path):
    meta, body = md.front_matter(open(path, encoding='utf-8').read())
    return meta, body


def cta_from(blocks_list):
    """Find and remove the CTA line; returns (headline, sub, link)."""
    for sec_blocks in blocks_list:
        for i, (kind, data) in enumerate(list(sec_blocks)):
            text = ' '.join(data) if kind == 'para' else (' '.join(data) if kind == 'ul' else '')
            if kind == 'ul':
                for j, item in enumerate(data):
                    m = re.match(r'CTA:\s*\*(.+?)\*\s*→\s*`([^`]+)`', item)
                    if m:
                        del data[j]
                        if not data:
                            del sec_blocks[i]
                        return split_cta(m.group(1)) + (m.group(2),)
            m = re.match(r'\*\*CTA(?: block)?:\*\*\s*\*(.+?)\*\s*→\s*`([^`]+)`', text)
            if m:
                del sec_blocks[i]
                return split_cta(m.group(1)) + (m.group(2),)
    return ('Join the MarginMail beta.', 'Free during the beta.', '/#join')


def split_cta(t):
    i = t.find('Join the MarginMail beta')
    if i <= 0:
        return (t, '')
    return (t[:i].strip(), t[i:].strip())


def faq_items(sec_blocks):
    items = []
    for kind, data in sec_blocks:
        if kind == 'para' and data and re.match(r'^\*\*.+\*\*$', data[0].strip()):
            q = data[0].strip()[2:-2]
            a = ' '.join(l.strip() for l in data[1:])
            items.append((q, a))
    return items


def article(src, path, section_name, section_path, img_side=True):
    meta, body = load(src)
    h1, intro, secs = md.sections(body)
    known = KNOWN
    inline = md.Inline(known, path)
    sources_html, related_html, faqs = '', '', []
    secs = [s for s in secs if s[0] != 'JSON-LD']
    ld_extra = []
    m = re.search(r'## JSON-LD\s*```json\s*(\{.*?\})\s*```', body, re.S)
    if m:
        try:
            g = json.loads(m.group(1))
            nodes = g.get('@graph', [g])
            for n in nodes:
                t = n.get('@type')
                if t == 'FAQPage' or (t == 'SoftwareApplication' and n.get('@id', '').endswith('/#app')) or t == 'BreadcrumbList':
                    continue
                n.pop('@context', None)
                ld_extra.append(n)
        except json.JSONDecodeError as e:
            md.WARNINGS.append(f'{path}: JSON-LD not parsed ({e})')
    cta = cta_from([s[1] for s in secs] + [intro])
    out = []
    pair = []
    for title, blks in secs:
        low = title.lower()
        if low == 'faq':
            faqs = faq_items(blks)
            out.append(f'<section class="blk prose" aria-labelledby="{md.slugify(title)}"><h2 id="{md.slugify(title)}">FAQ</h2>'
                       + ''.join(f'<div class="fq"><h3>{inline(q)}</h3><p>{inline(a)}</p></div>' for q, a in faqs) + '</section>')
            continue
        if low == 'sources':
            sources_html = md.render(blks, inline)
            continue
        if low in ('related comparisons', 'internal links'):
            items = []
            for kind, data in blks:
                if kind == 'ul':
                    for it in data:
                        for lab, url in re.findall(r'\[([^\]]+)\]\(([^)]+)\)', it):
                            if inline.link_ok(url) and url != path and (url, lab) not in items:
                                items.append((url, lab))
                            elif not inline.link_ok(url):
                                md.WARNINGS.append(f'{path}: related link to missing page {url} dropped')
            related_html = ''.join(f'<li><a href="{u}">{inline(l)}</a></li>' for u, l in items)
            continue
        has_table = any(k == 'table' for k, _ in blks)
        cls = 'blk' + ('' if has_table else ' prose')
        if (low.startswith('where ') and low.endswith('better choice')) or low.startswith('margin is the better choice') or low.startswith("margin isn't the right choice"):
            pair.append(f'<section class="blk"><div class="boxed"><h2 id="{md.slugify(title)}">{inline(title)}</h2>{md.render(blks, inline)}</div></section>')
            if len(pair) == 2:
                out.append(f'<div class="pair">{"".join(pair)}</div>')
                pair = []
            continue
        if pair:
            out.append(''.join(pair))
            pair = []
        out.append(f'<section class="{cls}"><h2 id="{md.slugify(title)}">{inline(title)}</h2>{md.render(blks, inline, h_offset=0)}</section>')
    if pair:
        out.append(''.join(pair))

    crumbs = [('MarginMail', '/')]
    if section_path and section_path in known:
        crumbs.append((section_name, section_path))
    crumbs.append((md.plain(meta.get('h1') or h1).split(':')[0] if False else short_name(meta, h1), path))
    crumb_html = ('<nav class="crumbs" aria-label="Breadcrumb"><ol>' + ''.join(
        (f'<li><a href="{u}">{esc(t)}</a></li>' if u != path else f'<li aria-current="page">{esc(t)}</li>') for t, u in crumbs) + '</ol></nav>')

    intro_html = md.render(intro, inline)
    side = ''
    if img_side:
        side = ('<figure class="side" style="margin:0">' + pic('margin-message-reply-bar-note', None,
                'MarginMail on the Mac: Imogen Hale’s message with the asked sentence highlighted, and a note in the reply bar that reads “Wants 30 min next week on scope.”',
                '(min-width: 1024px) 420px, calc(100vw - 32px)', '', cls='shot') + '<figcaption>MarginMail on the Mac. Names are fictional.</figcaption></figure>')
    answer_note = (svg_box(660, 160, M.arrow(-60, 150, -8, 156, bend=-.3, delay=1300), cls='ov d-only')
                   + note('checked, sources below', 'left:-214px;top:120px;width:170px;white-space:normal', rot=-4, size=23, delay=1600))
    slug = meta.get('slug', path.strip('/').split('/')[-1])
    source_tag = re.search(r'[?&]s=([a-z0-9._-]+)', cta[2])
    source_tag = source_tag.group(1) if source_tag else f'{section_path.strip("/") or "page"}-{slug}'
    cta_h = cta[0] or 'Join the MarginMail beta.'
    words = cta_h.rsplit(' ', 1)
    cta_title = (f'{esc(words[0])} <span class="ul">{esc(words[1])}{underline_svg(max(60, 14 * len(words[1])), sw=2.6, delay=700)}</span>'
                 if len(words) == 2 else esc(cta_h))
    body_html = (f'<div class="sec art"><div class="in"><div class="art-top">{crumb_html}<div class="art-hero"><div class="main">'
                 f'<h1 class="h1 art">{inline(meta.get("h1") or h1)}</h1><div class="answer" data-seen>{intro_html}{answer_note}</div></div>{side}</div></div>'
                 + ''.join(out)
                 + (f'<div class="srcs"><section class="s"><h2>Sources</h2>{sources_html}</section>' if sources_html else '<div class="srcs">')
                 + (f'<nav class="r" aria-label="Related pages"><h2>Related</h2><ul>{related_html}</ul></nav>' if related_html else '') + '</div>'
                 f'<section class="ctabox" aria-label="Join the beta"><div><h2 data-seen>{cta_title}</h2>'
                 f'<p class="body sub">{esc(cta[1] or "Free during the beta.")}</p></div>{joinform("join", source=source_tag, label="Join the beta")}</section>'
                 '</div></div>')

    url = SITE + path
    bc = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t, "item": SITE + u} for i, (t, u) in enumerate(crumbs)]}
    faq_ld = {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": md.plain(q), "acceptedAnswer": {"@type": "Answer", "text": md.plain(a)}} for q, a in faqs]} if faqs else None
    graph = ld_extra or [{"@type": "WebPage", "@id": url, "url": url, "name": md.plain(h1),
                          "description": meta.get('meta_description', ''), "dateModified": meta.get('last_checked', BUILT),
                          "isPartOf": {"@id": f"{SITE}/#site"}, "about": [{"@id": f"{SITE}/#app"}]}]
    for n in graph:
        if n.get('@type') in ('WebPage', 'Article', 'CollectionPage') and 'breadcrumb' not in n:
            n['breadcrumb'] = {"@id": url + "#breadcrumb"}
    bc['@id'] = url + '#breadcrumb'
    ld = {"@context": "https://schema.org", "@graph": graph + [bc] + ([faq_ld] if faq_ld else [])}
    og_key = f'compare-{slug}' if path.startswith('/compare/') else f'{meta.get("section", "page")}-{slug}'
    og_kw = {}
    if os.path.exists(os.path.join(ROOT, 'og', f'{og_key}.png')):
        name = short_name(meta, h1)
        og_kw = dict(og_image=f'/og/{og_key}.png',
                     og_alt=(f'MarginMail and {name} compared, for the Mac, with dated sources.' if path.startswith('/compare/')
                             else f'{md.plain(meta.get("og_image_text") or h1)}. MarginMail, a native Mac email app for Gmail.'))
    hh = head(meta['title'], meta['meta_description'], path, og_title=md.plain(meta.get('og_image_text') or h1), ld=ld, **og_kw)
    write(path.strip('/') + '/index.html', page(hh, body_html))
    PAGES.append(dict(path=path, title=md.plain(h1), lastmod=meta.get('last_checked', BUILT), meta=meta, h1=h1, intro=intro, secs=secs, faqs=faqs, src=src))


def short_name(meta, h1):
    if meta.get('slug') and '/compare/' in meta.get('url', ''):
        name = re.sub(r'^MarginMail vs (.+?)[:,].*$', r'\1', md.plain(h1))
        if name == md.plain(h1):
            name = re.sub(r'^(?:An? )?(.+?) alternative.*$', r'\1', md.plain(h1))
        return name
    return md.plain(meta.get('h1') or h1).split(':')[0]


def compare_hub():
    src = os.path.join(ROOT, 'content/comparisons/index.md')
    meta, body = load(src)
    h1, intro, secs = md.sections(body)
    inline = md.Inline(KNOWN, '/compare/')
    secs = [s for s in secs if s[0] != 'JSON-LD']
    cta = cta_from([s[1] for s in secs])
    out = []
    for title, blks in secs:
        has_table = any(k == 'table' for k, _ in blks)
        out.append(f'<section class="blk{"" if has_table else " prose"}{" hubtbl" if has_table else ""}"><h2 id="{md.slugify(title)}">{inline(title)}</h2>{md.render(blks, inline)}</section>')
    guides = [p for p in GUIDES]
    if guides:
        out.append('<section class="blk prose"><h2 id="guides">Guides and roundups</h2><ul>'
                   + ''.join(f'<li><a href="{g["path"]}">{esc(g["name"])}</a>: {esc(g["desc"])}</li>' for g in guides) + '</ul></section>')
    body_html = (f'<div class="sec art"><div class="in"><div class="art-top"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">MarginMail</a></li><li aria-current="page">Compare</li></ol></nav>'
                 f'<div class="art-hero"><div class="main"><h1 class="h1 art">{inline(h1)}</h1><div class="answer">{md.render(intro, inline)}</div></div></div></div>'
                 + ''.join(out) +
                 f'<section class="ctabox" aria-label="Join the beta"><div><h2 data-seen>Join the MarginMail <span class="ul">beta.{underline_svg(70, delay=700)}</span></h2><p class="body sub">Free during the beta.</p></div>'
                 f'{joinform("join", source="compare-hub")}</section></div></div>')
    m = re.search(r'## JSON-LD\s*```json\s*(\{.*?\})\s*```', body, re.S)
    node = json.loads(m.group(1))
    node.pop('@context', None)
    node['breadcrumb'] = {"@id": f"{SITE}/compare/#breadcrumb"}
    bc = {"@type": "BreadcrumbList", "@id": f"{SITE}/compare/#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "MarginMail", "item": f"{SITE}/"},
        {"@type": "ListItem", "position": 2, "name": "Compare", "item": f"{SITE}/compare/"}]}
    hh = head(meta['title'], meta['meta_description'], '/compare/', og_title=md.plain(h1),
              ld={"@context": "https://schema.org", "@graph": [node, bc]})
    write('compare/index.html', page(hh, body_html))
    PAGES.append(dict(path='/compare/', title=md.plain(h1), lastmod=meta.get('last_checked', BUILT), meta=meta, h1=h1, intro=intro, secs=secs, faqs=[], src=src))


# =============================================================== legal, 404
def legal(slug, title, desc):
    raw = open(os.path.join(HERE, 'legal', f'{slug}.html'), encoding='utf-8').read()
    body = (f'<div class="sec legal"><div class="in"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="/">MarginMail</a></li>'
            f'<li aria-current="page">{esc(title)}</li></ol></nav><article class="doc" style="margin-top:22px">{raw}</article></div></div>')
    hh = head(f'{title} · MarginMail', desc, f'/{slug}/')
    write(f'{slug}/index.html', page(hh, body))
    m = re.search(r'Last updated ([A-Z][a-z]+ \d+, \d{4})', raw)
    PAGES.append(dict(path=f'/{slug}/', title=title, lastmod=LEGAL_DATES[slug], meta={}, h1=title, intro=[], secs=[], faqs=[], src=None))


LEGAL_DATES = {}


def extract_legal():
    """Pull the hand-written legal text out of the old pages once; keep it verbatim in _build/legal/."""
    os.makedirs(os.path.join(HERE, 'legal'), exist_ok=True)
    for slug in ('privacy', 'terms'):
        dst = os.path.join(HERE, 'legal', f'{slug}.html')
        if not os.path.exists(dst):
            s = open(os.path.join(ROOT, slug, 'index.html'), encoding='utf-8').read()
            m = re.search(r'<main class="doc">.*?</a>\s*(.*?)<footer>', s, re.S)
            if not m:
                raise SystemExit(f'{slug}: could not find the legal text; edit _build/legal/{slug}.html by hand')
            text = m.group(1).strip().replace('href="/terms"', 'href="/terms/"').replace('href="/privacy"', 'href="/privacy/"')
            open(dst, 'w', encoding='utf-8').write(text + '\n')
        raw = open(dst, encoding='utf-8').read()
        months = dict(January=1, February=2, March=3, April=4, May=5, June=6, July=7, August=8, September=9, October=10, November=11, December=12)
        m = re.search(r'Last updated ([A-Z][a-z]+) (\d+), (\d{4})', raw)
        LEGAL_DATES[slug] = f'{m.group(3)}-{months[m.group(1)]:02d}-{int(m.group(2)):02d}' if m else BUILT


def not_found():
    body = ('<div class="sec nf"><div class="in"><p class="lbl">404</p><h1 class="h1" style="margin-top:12px">We couldn’t find that page.</h1>'
            '<p class="lead" style="max-width:560px">It may have moved, or the link may have a typo.</p>'
            '<ul><li><a class="btn" href="/">Go to the homepage</a></li><li><a class="btn ghost" href="/compare/">Compare MarginMail</a></li>'
            '<li><a class="btn ghost" href="/#join">Join the beta</a></li></ul></div></div>')
    hh = head('Page not found · MarginMail', 'This page doesn’t exist. Go to the MarginMail homepage or compare MarginMail with other Mac mail apps.', '/404.html')
    hh = hh.replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">')
    hh = re.sub(r'<link rel="canonical"[^>]*>\n', '', hh)
    hh = hh.replace('<meta name="robots" content="noindex">', '<meta name="robots" content="noindex">\n<meta name="page-path" content="/404">')
    write('404.html', page(hh, body))


# =============================================================== robots, sitemap, llms
ROBOTS = """# marginmail.ai: everyone is welcome to read and quote these pages.

User-agent: *
Allow: /
Disallow: /api/

# Search engines
User-agent: Googlebot
Allow: /
User-agent: Bingbot
Allow: /
User-agent: Applebot
Allow: /
User-agent: DuckDuckBot
Allow: /

# AI search, answers and user-initiated fetches
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: Claude-SearchBot
Allow: /
User-agent: Claude-User
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Perplexity-User
Allow: /

# AI training and model-improvement crawlers
User-agent: GPTBot
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: CCBot
Allow: /
User-agent: meta-externalagent
Allow: /
User-agent: Amazonbot
Allow: /

Sitemap: https://marginmail.ai/sitemap.xml
"""


def sitemap():
    urls = [('/', BUILT)] + [(p['path'], p['lastmod']) for p in PAGES]
    order = {'/': 0, '/compare/': 1}
    urls.sort(key=lambda u: (order.get(u[0], 2 if u[0].startswith('/compare/') else 3 if u[0].startswith(('/best/', '/guides/')) else 4), u[0]))
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + ''.join(f'  <url><loc>{SITE}{u}</loc><lastmod>{d}</lastmod></url>\n' for u, d in urls) + '</urlset>\n')
    write('sitemap.xml', xml)
    write('robots.txt', ROBOTS)


LLMS_FACTS = """Key facts:
- Platform: macOS 26 or later, native SwiftUI app. iPhone companion app later.
- Accounts: Gmail and Google Workspace, multiple accounts in one unified inbox. iCloud and other providers later.
- Price: free during the beta. Pricing not yet announced.
- Privacy: MarginMail talks directly to Google from the Mac. No MarginMail server holds mail, credentials or usage data. No analytics in the app. No read receipts or open tracking.
- AI: optional. Tier 1 rules (no AI), Tier 2 Apple on-device (Request notes), Tier 3 the user's own Claude, signed in on the Mac, only on click (Write it, What's been decided); only that one conversation goes to Anthropic, under the user's own plan. AI never sends email.
- Shipped features: margin notes (Follow-ups, Meetings, Requests) shown in the reply bar; the Margins stack (drag right for Done, left for the back of the stack; "Why this?" on every card; a sunrise or another quiet scene when empty); live words (dates, people, files and promises become actions as you type, rules only); Write it (drafts from your notes and the thread, flags anything new); What's been decided (long-thread summary); in-window composer (docked, floating, expanded); Split view (inbox, message and today's calendar side by side; click a name for the person's page); calendar built in (unanswered invites marked, accept with A/M/D, answering files the email, Needs your answer list, find a time with holds); People and Companies, a private personal CRM (a page per person with conversations, meetings, notes, tasks that close themselves and local time; who's waiting on you; companies by domain; stored in the user's own Google account); menu bar agenda with Join; notifications per account (everything, needs you + VIPs, or nothing; quiet hours, Focus filters); Done instead of Archive.
- Not for: Windows, Android, Microsoft 365 or iCloud-only users (yet), shared team inboxes, open tracking.
- Contact: hello@marginmail.ai
"""


def strip_html(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s))


def llms():
    summary = (f'> {DEFINITION} It notes what needs you, keeps your calendar beside your inbox, and gives everyone you write to a page. '
               'AI is optional: Apple Intelligence on your Mac, or your own Claude if you opt in, only on click (that conversation goes to Anthropic under your own plan). There is no MarginMail server for your mail, '
               'no analytics in the app, and AI never sends. It is in beta and free during the beta.')
    pages = ['- [Home](https://marginmail.ai/): what MarginMail is and how to join the beta']
    for p in sorted(PAGES, key=lambda p: (not p['path'].startswith('/compare/'), p['path'] != '/compare/', p['path'])):
        label = 'Compare' if p['path'] == '/compare/' else p['title']
        desc = p['meta'].get('meta_description', '')
        pages.append(f'- [{label}]({SITE}{p["path"]})' + (f': {desc}' if desc and p['path'] == '/compare/' else ''))
    head_txt = f'# MarginMail\n\n{summary}\n\n{LLMS_FACTS}\n## Pages\n' + '\n'.join(pages) + '\n'
    write('llms.txt', head_txt)

    out = [f'# MarginMail\n\n{summary}\n\n{LLMS_FACTS}']
    out.append('## Home (https://marginmail.ai/)\n')
    out.append(f'### What is MarginMail?\n\n{strip_html(C.WHAT_IS["lead"] + C.WHAT_IS["rest"])}\n')
    out.append(f'### {C.MANIFESTO["lbl"]}\n\n{strip_html(C.MANIFESTO["text"])}\n')
    for d in (C.S_STACK, C.S_SPLIT, C.S_PEOPLE, C.S_TIME, C.S_LIVE, C.S_SKIM, C.S_WRITE, C.S_MACPRIV, C.S_JOY):
        txt = f'### {strip_html(d["lbl"])}: {strip_html(d["h"])}\n\n{strip_html(d["body"])}\n'
        if 'points' in d:
            txt += '\n' + '\n'.join(f'- {strip_html(t)} {strip_html(b)}' for t, b in d['points']) + '\n'
        if 'priv' in d:
            txt += f'\n{strip_html(d["priv"])}\n'
        out.append(txt)
    out.append('### FAQ\n\n' + '\n\n'.join(f'**{strip_html(q)}**\n{strip_html(a)}' for q, a in C.FAQ) + '\n')
    for p in PAGES:
        if not p['src'] or p['path'] in ('/privacy/', '/terms/'):
            continue
        meta, body = load(p['src'])
        body = re.sub(r'\n## JSON-LD.*', '\n', body, flags=re.S)
        body = re.sub(r'\n## (Internal links|Related comparisons)\n.*?(?=\n## |\Z)', '\n', body, flags=re.S)
        body = re.sub(r'^\s*[-*]?\s*\**CTA[^\n]*\n', '', body, flags=re.M)
        body = re.sub(r'^# ', '## ', body, count=1, flags=re.M)
        body = re.sub(r'^(#{2,5}) ', lambda m: '#' + m.group(1) + ' ', body[body.index('## '):], flags=re.M) if '## ' in body else body
        out.append(f'## {md.plain(p["h1"])} ({SITE}{p["path"]})\n\n' + body.split('\n', 1)[1].strip() + '\n')
    out.append(f'---\nFacts checked {BUILT}. Source: https://marginmail.ai\n')
    write('llms-full.txt', '\n'.join(out))


# =============================================================== brand files, main
def brand_files():
    os.makedirs(os.path.join(ROOT, 'img/brand'), exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, 'brand/final/lockup/lockup-horizontal-nav-28.svg'), os.path.join(ROOT, 'img/brand/lockup-nav.svg'))
    shutil.copyfile(os.path.join(ROOT, 'brand/final/lockup/lockup-horizontal-footer-40.svg'), os.path.join(ROOT, 'img/brand/lockup-footer.svg'))
    for n in ('stack', 'live-words', 'write-it', 'tour'):
        for ext in ('css', 'js'):
            shutil.copyfile(os.path.join(ROOT, f'assets/motion/{n}.{ext}'), os.path.join(ROOT, f'motion/{n}.{ext}'))


KNOWN = set()
GUIDES = []


def main():
    md.WARNINGS.clear()
    brand_files()
    version_css_fonts()
    build_images()
    extract_legal()
    comps = sorted(f for f in os.listdir(os.path.join(ROOT, 'content/comparisons')) if f.endswith('.md') and f != 'index.md')
    seo = sorted(f for f in os.listdir(os.path.join(ROOT, 'content/seo/pages')) if f.endswith('.md'))
    KNOWN.update(['/', '/compare/', '/privacy/', '/terms/'])
    for f in comps:
        KNOWN.add(f'/compare/{f[:-3]}/')
    for f in seo:
        meta, _ = load(os.path.join(ROOT, 'content/seo/pages', f))
        p = meta['url'].replace(SITE, '')
        KNOWN.add(p)
        GUIDES.append(dict(path=p, name=meta.get('h1', ''), desc=meta.get('meta_description', '').split('. ')[0].rstrip('.') + '.'))
    home()
    compare_hub()
    for f in comps:
        article(os.path.join(ROOT, 'content/comparisons', f), f'/compare/{f[:-3]}/', 'Compare', '/compare/')
    for f in seo:
        meta, _ = load(os.path.join(ROOT, 'content/seo/pages', f))
        p = meta['url'].replace(SITE, '')
        sec = meta.get('section', '')
        article(os.path.join(ROOT, 'content/seo/pages', f), p, {'best': 'Best of', 'guides': 'Guides'}.get(sec, sec), f'/{sec}/')
    legal('privacy', 'Privacy Policy', 'How MarginMail handles your data: no MarginMail server for your mail, no tracking, anonymous site visit counts, optional AI on your terms, and the waitlist.')
    legal('terms', 'Terms of Service', 'The terms for using MarginMail, the native Mac mail and calendar app, during its beta.')
    not_found()
    sitemap()
    llms()
    versions.save()
    if AB.active():
        print('A/B test running on /: ' + ', '.join(f"{r['id']} (weight {r['weight']:g})" for r in AB.rows))
    for w in md.WARNINGS:
        print('warning:', w)
    print(f'built {len(PAGES) + 1} pages')


if __name__ == '__main__':
    main()
