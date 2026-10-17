"""Hand-drawn marks (SVG strings) for marginmail.ai. Ported from the approved board generator (sitegen/common.py, parts.py)."""
import math, html
INK = '#1D1B18'; CLAY = '#C2531F'; MINK = '#6F371B'; RULE = '#E7DFD4'
# ---------------------------------------------------------------- hand-drawn marks (board 67 language)
def wob(x):
    return 0.8 * math.sin(x / 41) + 0.45 * math.sin(x / 13)

def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')

def _path(d, color, sw, dur, delay, opacity=None, dash=None):
    op = f' stroke-opacity="{opacity}"' if opacity else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    cls = '' if dash else ' pathLength="1" class="dw"'
    sty = '' if dash else f' style="animation-duration:{dur}ms;animation-delay:{delay}ms"'
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round"{op}{da}{cls}{sty}/>')

def underline(x0, x1, y, color=CLAY, sw=2.6, delay=900, swash=True):
    pts = []
    x = x0
    rise = 0
    while x <= x1:
        t = (x - x0) / max(1, x1 - x0)
        pts.append((x, y + wob(x) * 0.45 - t * t * 3.2))
        x += 6
    d = 'M' + 'L'.join(f'{f(px)} {f(py)}' for px, py in pts)
    if swash:
        w = x1 - x0
        d += f'L{f(x1 - 2)} {f(y - 4.6)}Q{f(x0 + w * .52)} {f(y + 9)} {f(x0 + w * .16)} {f(y + 6.5)}'
    return _path(d, color, sw, 520, delay)

def loop(cx, cy, rx, ry, color=CLAY, sw=2.4, delay=700, start=-2.15, over=0.55):
    pts = []
    n = 80
    total = 2 * math.pi + over
    for i in range(n + 1):
        a = start + total * i / n
        k = 1 + 0.035 * math.sin(3 * a + 1) + 0.02 * (i / n)
        pts.append((cx + rx * k * math.cos(a) + 0.04 * rx * (i / n), cy + ry * k * math.sin(a) - 0.06 * ry * (i / n)))
    d = 'M' + 'L'.join(f'{f(px)} {f(py)}' for px, py in pts)
    return _path(d, color, sw, 800, delay)

def arrow(sx, sy, ex, ey, bend=0.35, color=MINK, sw=2.1, delay=1300, head=10):
    mx, my = (sx + ex) / 2, (sy + ey) / 2
    dx, dy = ex - sx, ey - sy
    cx, cy = mx - dy * bend, my + dx * bend
    d = f'M{f(sx)} {f(sy)}Q{f(cx)} {f(cy)} {f(ex)} {f(ey)}'
    tx, ty = ex - cx, ey - cy
    L = math.hypot(tx, ty) or 1
    tx, ty = tx / L, ty / L
    hs = []
    for ang in (0.48, -0.42):
        ca, sa = math.cos(ang), math.sin(ang)
        bx, by = -(tx * ca - ty * sa), -(tx * sa + ty * ca)
        hs.append(f'M{f(ex + bx * head)} {f(ey + by * head)}L{f(ex)} {f(ey)}')
    return _path(d, color, sw, 420, delay) + _path(''.join(hs), color, sw, 160, delay + 420)

def check(cx, cy, s=1.0, color=CLAY, sw=2.6, delay=1000):
    pts = [(-11.2, 0.9), (-3.4, 9.4), (11.2, -7.9)]
    d = 'M' + 'L'.join(f'{f(cx + x * s)} {f(cy + y * s)}' for x, y in pts)
    return _path(d, color, sw, 360, delay)

def strike(x0, y0, x1, y1, color=CLAY, sw=2.4, delay=1200):
    d1 = f'M{f(x0)} {f(y0)}L{f(x1)} {f(y1)}'
    d2 = f'M{f(x1 - 2)} {f(y0 + 3)}L{f(x0 + 3)} {f(y1 - 1)}'
    return _path(d1, color, sw, 260, delay) + _path(d2, color, sw, 260, delay + 260)

def hline(x0, x1, y, color=INK, sw=1.5, delay=300, dur=1900, opacity=0.9):
    pts = []
    x = x0
    while x <= x1:
        pts.append((x, y + wob(x) * 0.5))
        x += 8
    return _path('M' + 'L'.join(f'{f(a)} {f(b)}' for a, b in pts), color, sw, dur, delay, opacity)

def circle(cx, cy, r, color=INK, sw=1.5, delay=500, dur=1900, opacity=0.75):
    pts = []
    n = 72
    for i in range(n + 2):
        a = -math.pi / 2 + 2 * math.pi * i / n
        rr = r * (1 + 0.012 * math.sin(5 * a))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return _path('M' + 'L'.join(f'{f(a)} {f(b)}' for a, b in pts), color, sw, dur, delay, opacity)

def note(text, x, y, rot=-3, size=23, delay=1500, anchor='left', width=None, write=False):
    """Caveat margin note (<= 6 words, no period). aria-hidden: it repeats the copy."""
    words = len(text.replace('<br>', ' ').split())
    assert words <= 6, text
    al = {'left': 'left', 'center': 'center', 'right': 'right'}[anchor]
    tx = {'left': '0', 'center': '-50%', 'right': '-100%'}[anchor]
    w = f'width:{width}px;' if width else 'white-space:nowrap;'
    cls = 'hand write' if write else 'hand fade'
    return (f'<div class="{cls}" aria-hidden="true" style="position:absolute;left:{x}px;top:{y}px;{w}'
            f'font-size:{size}px;line-height:1.02;text-align:{al};transform:translateX({tx}) rotate({rot}deg);'
            f'animation-delay:{delay}ms">{text}</div>')

def overlay(w, h, inner):
    return (f'<svg aria-hidden="true" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'style="position:absolute;left:0;top:0;overflow:visible;pointer-events:none">{inner}</svg>')

def glow(cx, cy, r, color='#F2BC5C', op=0.55, gid='g', delay=600, clip=None):
    c = f' clip-path="url(#{clip})"' if clip else ''
    return (f'<defs><radialGradient id="{gid}"><stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
            f'<stop offset=".35" stop-color="{color}" stop-opacity="{op/2}"/><stop offset="1" stop-color="{color}" stop-opacity="0"/>'
            f'</radialGradient></defs><circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#{gid})" class="fade breathe" '
            f'style="animation-delay:{delay}ms,{delay+2600}ms"{c}/>')

def esc(s):
    return html.escape(s, quote=False)

def promise_icon(i):
    s = 'fill="none" stroke="#1D1B18" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".85"'
    icons = [
        f'<rect x="5" y="6" width="22" height="8" rx="2" {s}/><rect x="5" y="17" width="22" height="8" rx="2" {s}/><path d="M3 29L29 3" {s}/>',
        f'<path d="M3 16C7 9.5 11 7 16 7s9 2.5 13 9c-4 6.5-8 9-13 9S7 22.5 3 16Z" {s}/><circle cx="16" cy="16" r="4" {s}/><path d="M4 28L28 4" {s}/>',
        f'<rect x="3" y="10" width="26" height="12" rx="6" {s}/><circle cx="10" cy="16" r="3.4" {s}/>',
        f'<path d="M4 15.5L28 5L22 27L15 18.5Z" {s}/><path d="M15 18.5L28 5" {s}/>',
    ]
    return f'<svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true">{icons[i]}</svg>'

def privacy_diagram(w=1140, h=300, vertical=False):
    """Diagram 7, "The path": your Mac <-> Google, optional dotted branch to your Claude, no MarginMail server."""
    lab = 'font-family:-apple-system,system-ui,sans-serif;font-size:15px;font-weight:600;fill:#1D1B18'
    sub = 'font-family:-apple-system,system-ui,sans-serif;font-size:13px;fill:#5C554B'
    I = 'stroke="#1D1B18" stroke-opacity=".85" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"'
    def mac(x, y):
        return (f'<rect x="{x-58}" y="{y-40}" width="116" height="74" rx="7" {I}/><rect x="{x-50}" y="{y-32}" width="100" height="58" rx="3" fill="#FFFFFF" stroke="none"/>'
                f'<path d="M{x-74} {y+40}H{x+74}L{x+66} {y+48}H{x-66}Z" {I}/>'
                f'<path d="M{x-28} {y-14}H{x+20}M{x-28} {y-2}H{x+30}M{x-28} {y+10}H{x+8}" stroke="#CBC3B8" stroke-width="3" stroke-linecap="round"/>'
                f'<path d="M{x-38} {y-20}H{x-42}V{y+16}H{x-38}" stroke="#6F371B" stroke-width="1.8" fill="none" stroke-linecap="round"/>')
    def cloud(x, y):
        return (f'<path d="M{x-46} {y+22}C{x-70} {y+22} {x-70} {y-8} {x-46} {y-8}C{x-44} {y-30} {x-14} {y-36} {x-2} {y-20}C{x+10} {y-38} {x+44} {y-32} {x+44} {y-6}'
                f'C{x+68} {y-6} {x+68} {y+22} {x+44} {y+22}Z" {I}/>')
    if not vertical:
        mx, my, gx, gy = 190, 120, w - 190, 120
        cx, cy = w / 2, 248
        sx, sy = w / 2, 56
        line = hline(mx + 92, gx - 92, my, sw=1.6, delay=300, dur=1200)
        arrows = (f'<path d="M{mx+100} {my-7}L{mx+90} {my}L{mx+100} {my+7}M{gx-100} {my-7}L{gx-90} {my}L{gx-100} {my+7}" {I}/>')
        branch = f'<path d="M{mx+40} {my+56}Q{mx+80} {cy} {cx-110} {cy}" fill="none" stroke="#1D1B18" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="2 6" stroke-linecap="round"/>'
        out = (f'<svg aria-label="Your Mac talks to Google directly. An optional dotted line goes to your own Claude. There is no MarginMail server." '
               f'role="img" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">'
               f'{mac(mx, my)}<text x="{mx}" y="{my+78}" text-anchor="middle" style="{lab}">Your Mac</text>'
               f'{cloud(gx, gy)}<text x="{gx}" y="{gy+6}" text-anchor="middle" style="{lab}">Google</text>'
               f'<text x="{gx}" y="{gy+58}" text-anchor="middle" style="{sub}">Gmail · Calendar · Contacts</text>'
               f'{line}{arrows}{branch}'
               f'<rect x="{cx-110}" y="{cy-26}" width="220" height="52" rx="12" fill="#fff" stroke="#1D1B18" stroke-opacity=".5" stroke-width="1.3" stroke-dasharray="3 5"/>'
               f'<text x="{cx}" y="{cy-3}" text-anchor="middle" style="{lab}">Your Claude</text><text x="{cx}" y="{cy+15}" text-anchor="middle" style="{sub}">if you turn it on</text>'
               f'<g opacity=".45"><rect x="{sx-88}" y="{sy-26}" width="176" height="50" rx="10" fill="none" stroke="#8A8174" stroke-width="1.3"/>'
               f'<text x="{sx}" y="{sy+5}" text-anchor="middle" style="{lab};fill:#8A8174">MarginMail server</text></g>'
               f'{strike(sx-96, sy-30, sx+96, sy+28, color=MINK, sw=2)}'
               f'<path d="M{mx+112} {my-46}V{my+40}" stroke="#6F371B" stroke-opacity=".5" stroke-width="1.3" stroke-dasharray="3 5"/>'
               f'{pixel(gx-96, my-18, mx+122, my-18)}'
               f'</svg>')
        return out, (sx, sy)
    # vertical (mobile): Mac on top, Google below, the direct line between; Claude (dotted) left, no server right.
    mx, my, gx, gy = w / 2, 70, w / 2, 410
    cx, cy = 78, 246
    sx, sy = w - 70, 246
    line = (f'<path d="M{mx} {my+92}L{gx} {gy-44}" {I} pathLength="1" class="dw" style="animation-duration:1200ms;animation-delay:300ms"/>'
            f'<path d="M{mx-6} {my+102}L{mx} {my+92}L{mx+6} {my+102}M{gx-6} {gy-54}L{gx} {gy-44}L{gx+6} {gy-54}" {I}/>')
    branch = f'<path d="M{mx-78} {my+48}Q{cx} {my+60} {cx} {cy-26}" fill="none" stroke="#1D1B18" stroke-opacity=".6" stroke-width="1.5" stroke-dasharray="2 6" stroke-linecap="round"/>'
    out = (f'<svg aria-label="Your Mac talks to Google directly. An optional dotted line goes to your own Claude. There is no MarginMail server." '
           f'role="img" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="display:block;overflow:visible">'
           f'{mac(mx, my)}<text x="{mx}" y="{my+76}" text-anchor="middle" style="{lab}">Your Mac</text>'
           f'{cloud(gx, gy)}<text x="{gx}" y="{gy+6}" text-anchor="middle" style="{lab}">Google</text>'
           f'<text x="{gx}" y="{gy+50}" text-anchor="middle" style="{sub}">Gmail · Calendar · Contacts</text>'
           f'{line}{branch}'
           f'<rect x="{cx-70}" y="{cy-26}" width="140" height="52" rx="12" fill="#fff" stroke="#1D1B18" stroke-opacity=".5" stroke-width="1.3" stroke-dasharray="3 5"/>'
           f'<text x="{cx}" y="{cy-3}" text-anchor="middle" style="{lab}">Your Claude</text><text x="{cx}" y="{cy+15}" text-anchor="middle" style="{sub}">if you turn it on</text>'
           f'<g opacity=".45"><rect x="{sx-62}" y="{sy-24}" width="124" height="46" rx="10" fill="none" stroke="#8A8174" stroke-width="1.3"/>'
           f'<text x="{sx}" y="{sy+5}" text-anchor="middle" style="{lab};fill:#8A8174;font-size:13.5px">MarginMail server</text></g>'
           f'{strike(sx-68, sy-28, sx+68, sy+26, color=MINK, sw=2)}'
           f'<path d="M{mx-40} {my+128}H{mx+60}" stroke="#6F371B" stroke-opacity=".5" stroke-width="1.3" stroke-dasharray="3 5"/>'
           f'{pixel(mx+22, gy-70, mx+22, my+138)}</svg>')
    return out, (sx, sy)

def sunrise_scene(w, h, ruleX, horizonY, sunR, title_size=30, gid='sr', note_txt=True):
    """Motion piece 8, "All clear", recreated inline: margin rule, pencil horizon, the sun draws in, warm light breathes,
    Clay check. Draws once; the glow breathes slowly. Reduce Motion shows the finished frame."""
    cx = (ruleX + w) / 2 if ruleX > 60 else w / 2
    cx = w / 2 + ruleX / 2
    clip = f'{gid}c'
    svg = (f'<svg aria-hidden="true" width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="position:absolute;left:0;top:0">'
           f'<defs><clipPath id="{clip}"><rect width="{w}" height="{horizonY}"/></clipPath>'
           f'<linearGradient id="{gid}r" x1="0" y1="0" x2="0" y2="{h}" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#6F371B" stop-opacity="0"/>'
           f'<stop offset=".15" stop-color="#6F371B" stop-opacity=".55"/><stop offset=".85" stop-color="#6F371B" stop-opacity=".55"/><stop offset="1" stop-color="#6F371B" stop-opacity="0"/></linearGradient></defs>'
           f'<path d="M{ruleX} 0V{h}" stroke="url(#{gid}r)" stroke-width="1.4" class="fade" style="animation-delay:100ms"/>'
           + glow(cx, horizonY - sunR * .2, sunR * 3.4, op=.6, gid=gid + 'g', delay=900, clip=clip)
           + glow(cx, horizonY + 10, sunR * 2.2, op=.16, gid=gid + 's', delay=1200)
           + f'<g clip-path="url(#{clip})">{circle(cx, horizonY + sunR * .22, sunR, delay=700, sw=1.5)}</g>'
           + hline(ruleX + 30, w - 40, horizonY, color='#6F371B', sw=1.6, delay=300, dur=1900)
           + check(cx, horizonY - sunR * .62, sunR / 40, color=MINK, delay=2300, sw=2.4)
           + f'<g tabindex="0" class="egg" aria-label="A star. Hover or click it.">' + f'<circle cx="{cx + sunR * .12}" cy="{horizonY - sunR * 1.6}" r="{sunR * .5}" fill="transparent"/>' + star(cx + sunR * .12, horizonY - sunR * 1.6, sunR * .24, delay=2700) + '</g>'
           + f'<g class="plane" style="--fx:{w - ruleX - 140}px;--fy:-{horizonY * .45:.0f}px;transform-box:fill-box"><path d="M{ruleX + 40} {horizonY - 70}l26 -9l-9 21l-4 -8z M{ruleX + 53} {horizonY - 74}l-4 8" fill="#fff" stroke="#6F371B" stroke-width="1.4" stroke-linejoin="round"/></g>'
           + '</svg>')
    return svg, cx

def composer_modes(scale=1.0):
    """Motion piece 6 recreated as three still frames: docked, floating, expanded. The inbox column stays."""
    W, H = int(340 * scale), int(212 * scale)
    s = scale
    def frame(mode):
        inbox = ''.join(f'<div style="height:{int(18*s)}px;margin:{int(6*s)}px {int(8*s)}px;border-radius:{int(4*s)}px;background:{"#F6E3D8" if i==1 else "#EFE8DE"}"></div>' for i in range(6))
        reader = (f'<div style="position:absolute;left:{int(100*s)}px;top:{int(10*s)}px;right:{int(10*s)}px;bottom:{int(10*s)}px;background:#fff;border-radius:{int(8*s)}px;box-shadow:0 0 0 1px #EBE3D8">'
                  + ''.join(f'<div style="height:{int(5*s)}px;width:{w}%;margin:{int(9*s)}px {int(12*s)}px 0;border-radius:3px;background:#E7DFD4"></div>' for w in (40, 86, 78, 64)) + '</div>')
        comp_style = {
            'docked': f'left:{int(110*s)}px;right:{int(20*s)}px;bottom:{int(18*s)}px;height:{int(70*s)}px',
            'floating': f'right:{int(18*s)}px;top:{int(26*s)}px;width:{int(130*s)}px;height:{int(96*s)}px;transform:rotate(-1.2deg)',
            'expanded': f'left:{int(104*s)}px;right:{int(14*s)}px;top:{int(14*s)}px;bottom:{int(14*s)}px',
        }[mode]
        comp = (f'<div style="position:absolute;{comp_style};background:#fff;border-radius:{int(9*s)}px;box-shadow:0 0 0 1.5px rgba(111,55,27,.55),0 10px 24px -10px rgba(60,40,20,.35)">'
                f'<div style="height:{int(5*s)}px;width:44%;margin:{int(11*s)}px {int(12*s)}px 0;border-radius:3px;background:#E7DFD4"></div>'
                f'<div style="height:{int(5*s)}px;width:70%;margin:{int(8*s)}px {int(12*s)}px 0;border-radius:3px;background:#E7DFD4"></div>'
                f'<div style="position:absolute;right:{int(8*s)}px;bottom:{int(8*s)}px;width:{int(30*s)}px;height:{int(12*s)}px;border-radius:{int(4*s)}px;background:#C2531F"></div></div>')
        return (f'<div style="position:relative;width:{W}px;height:{H}px;border-radius:{int(12*s)}px;background:#F4EFE8;box-shadow:0 0 0 1px rgba(60,40,20,.10);overflow:hidden">'
                f'<div style="position:absolute;left:0;top:0;bottom:0;width:{int(92*s)}px;padding-top:{int(4*s)}px">{inbox}</div>{reader}{comp}</div>')
    return [(m.capitalize(), frame(m)) for m in ('docked', 'floating', 'expanded')]

def decided_card(width=460, animate=False):
    rows = [('Decided', 'Copper foil on the front only. 4,000 units on the uncoated stock.'),
            ('Still open', 'Which press slot, if the proof is late.'),
            ('Waiting on', 'You, for the signed proof by Thursday.')]
    r = ''.join(f'<div class="{"tick" if animate else ""}" style="display:flex;gap:14px;padding:10px 0;border-top:1px solid #F0EAE1;animation-delay:{1400 + 450 * i}ms"><div style="width:84px;flex:none;font-size:12.5px;font-weight:600;color:var(--graphite)">{a}</div>'
                f'<div class="serif" style="font-size:16px;line-height:22px;font-variation-settings:\'opsz\' 16">{b}</div></div>' for i, (a, b) in enumerate(rows))
    return (f'<div style="width:{width}px;background:#fff;border-radius:14px;box-shadow:0 0 0 1px var(--rule),0 12px 30px -14px rgba(60,40,20,.2);padding:14px 18px 6px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><span class="lbl" style="color:var(--mink)">What’s been decided</span>'
            f'<span style="font-size:12px;color:var(--pencil)">Saltmarsh labels · 14 messages</span></div>{r}</div>')

def star(cx, cy, r, color=CLAY, sw=2.4, delay=1000):
    """The marginal star, drawn: five arms from the centre, 200 ms each, 60 ms stagger."""
    out = ''
    for i in range(5):
        a = math.radians(-90 + 72 * i)
        out += (f'<path d="M{f(cx)} {f(cy)}L{f(cx + r * math.cos(a))} {f(cy + r * math.sin(a))}" fill="none" stroke="{color}" '
                f'stroke-width="{sw}" stroke-linecap="round" pathLength="1" class="dw" style="animation-duration:200ms;animation-delay:{delay + 60 * i}ms"/>')
    return out

def marker(x0, x1, y, h, delay=900, op=.62):
    """A highlighter swipe: Marker at ~50%, multiply, slightly uneven."""
    pts = []
    x = x0
    while x <= x1:
        pts.append((x, y + wob(x) * .35))
        x += 10
    d = 'M' + 'L'.join(f'{f(a)} {f(b)}' for a, b in pts)
    return (f'<path d="{d}" fill="none" stroke="#F6D77A" stroke-opacity="{op}" stroke-width="{h}" stroke-linecap="round" '
            f'style="mix-blend-mode:multiply;animation-duration:520ms;animation-delay:{delay}ms" pathLength="1" class="dw"/>')

def card_mark(kind, delay):
    """The six manifesto marks, in MarginMail ink (the section's one Clay mark is the bracket beside the manifesto)."""
    T = 'font-family:Newsreader,Georgia,serif;font-size:16px;fill:#1D1B18'
    chip = 'fill="#fff" stroke="#E7DFD4"'
    if kind == 'circle':
        body = (f'<rect x="20" y="16" width="86" height="26" rx="7" {chip}/><text x="63" y="34" text-anchor="middle" style="{T};font-family:-apple-system,system-ui,sans-serif;font-size:12.5px;font-weight:600">Tue 2:30 PM</text>'
                f'<rect x="132" y="16" width="86" height="26" rx="7" {chip} opacity=".55"/><text x="175" y="34" text-anchor="middle" style="{T};font-family:-apple-system,system-ui,sans-serif;font-size:12.5px;opacity:.55">Tue 5:00 PM</text>'
                + loop(63, 29, 56, 21, color=MINK, sw=2, delay=delay))
    elif kind == 'star':
        body = f'<text x="40" y="35" style="{T}">12:41 PM for Ava</text>' + star(22, 29, 9, color=MINK, sw=2, delay=delay)
    elif kind == 'underline':
        body = f'<text x="8" y="31" style="{T}">Decided: copper foil, front only</text>' + underline(8, 214, 40, color=MINK, sw=2, delay=delay, swash=False)
    elif kind == 'arrow':
        body = (f'<rect x="10" y="10" width="92" height="38" rx="8" {chip}/><path d="M22 23H74M22 33H58" stroke="#CBC3B8" stroke-width="3" stroke-linecap="round"/>'
                + arrow(112, 32, 196, 26, bend=-.18, color=MINK, sw=2, delay=delay))
    elif kind == 'bracket':
        body = (''.join(f'<rect x="{30 + i*5}" y="{12 + i*12}" width="{150 - i*10}" height="9" rx="4.5" fill="#EFE8DE"/>' for i in range(3))
                + f'<path d="M22 6H12V52H22" fill="none" stroke="#6F371B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" pathLength="1" class="dw" style="animation-duration:460ms;animation-delay:{delay}ms"/>')
    elif kind == 'highlight':
        body = marker(10, 200, 29, 17, delay=delay) + f'<text x="10" y="35" style="{T}">Could you send the proof?</text>'
    return f'<svg aria-hidden="true" width="220" height="56" viewBox="0 0 220 56" style="display:block;overflow:visible">{body}</svg>'

def priv_icon(i):
    s = 'fill="none" stroke="#1D1B18" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".85"'
    icons = [
        f'<path d="M3 16C7 9.5 11 7 16 7s9 2.5 13 9c-4 6.5-8 9-13 9S7 22.5 3 16Z" {s}/><circle cx="16" cy="16" r="4" {s}/><path d="M4 28L28 4" {s}/>',
        f'<rect x="4" y="6" width="24" height="20" rx="3" {s}/><path d="M4 21L11 14L17 20L21 16L28 22" {s}/><rect x="20" y="9" width="3" height="3" {s}/>',
        f'<path d="M4 9H28V24H4Z" {s}/><path d="M4 9L16 18L28 9" {s}/><path d="M3 29L29 3" {s}/>',
        f'<rect x="5" y="6" width="22" height="8" rx="2" {s}/><rect x="5" y="17" width="22" height="8" rx="2" {s}/><path d="M3 29L29 3" {s}/>',
        f'<rect x="3" y="10" width="26" height="12" rx="6" {s}/><circle cx="10" cy="16" r="3.4" {s}/>',
        f'<path d="M5 9H13L15 12H27V25H5Z" {s}/><rect x="13" y="16" width="7" height="6" rx="1.4" {s}/><path d="M14.5 16V14.6a2 2 0 0 1 4 0V16" {s}/>',
    ]
    return f'<svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true" style="flex:none">{icons[i]}</svg>'

def detail_icon(i):
    """Line icons for The details, drawn like priv_icon: composer, Done, accounts, menu bar, notifications, fit."""
    s = 'fill="none" stroke="#1D1B18" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-opacity=".85"'
    icons = [
        f'<rect x="3" y="5" width="26" height="22" rx="3" {s}/><path d="M10 5V27" {s}/><rect x="14" y="16" width="12" height="8" rx="1.6" {s}/><path d="M17 20H23" {s}/>',
        f'<circle cx="16" cy="16" r="12" {s}/><path d="M10.5 16.5L14.5 20.5L22 12" {s}/>',
        f'<rect x="7" y="4" width="21" height="15" rx="2" {s}/><path d="M7 6L17.5 13L28 6" {s}/><rect x="3" y="12" width="21" height="15" rx="2" fill="#FBF8F4" stroke="none"/><rect x="3" y="12" width="21" height="15" rx="2" {s}/><path d="M3 14L13.5 21L24 14" {s}/>',
        f'<path d="M3 8H29" {s}/><rect x="17" y="12" width="12" height="15" rx="2" {s}/><path d="M17 16H29M20.5 10V13M25.5 10V13" {s}/><path d="M20 20H23M20 23H26" {s}/><circle cx="22" cy="5.5" r=".6" {s}/>',
        f'<path d="M9 22V15a7 7 0 0 1 14 0v7l2 3H7Z" {s}/><path d="M13.5 28a2.5 2.5 0 0 0 5 0" {s}/><path d="M16 5V8" {s}/>',
        f'<path d="M4 23C7 17 9 13 11 13s-1 9 2 9 4-8 6-8-1 7 2 7 4-3 7-4" {s}/><path d="M4 27H28" {s}/>',
    ]
    return f'<svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true" style="flex:none">{icons[i]}</svg>'

def two_cals(w=380, rowh=24):
    """Find time: your calendar and Ava's slide in side by side; the shared free hour gets circled (one Clay mark)."""
    hours = ['9', '10', '11', '12', '1', '2', '3', '4']
    top = 44; colw = (w - 64) // 2
    busy_you = [(0, 1), (2, 3), (4, 6)]
    busy_ava = [(.5, 1.5), (1.5, 2.75), (6, 8)]
    def col(x, blocks, cls, color, label, delay):
        b = ''.join(f'<div style="position:absolute;left:4px;right:4px;top:{top + a * rowh + 1}px;height:{(e - a) * rowh - 2}px;border-radius:5px;background:{color}"></div>' for a, e in blocks)
        return (f'<div class="{cls}" style="position:absolute;left:{x}px;top:0;width:{colw}px;height:{top + 8 * rowh}px;animation-delay:{delay}ms">'
                f'<div style="position:absolute;top:16px;left:6px;font-size:12px;font-weight:600;color:var(--graphite)">{label}</div>{b}</div>')
    grid = ''.join(f'<div style="position:absolute;left:0;right:0;top:{top + i * rowh}px;border-top:1px solid #F0EAE1"><span style="position:absolute;left:4px;top:2px;font-size:10px;color:var(--pencil)">{t}</span></div>' for i, t in enumerate(hours))
    fy = top + 3 * rowh
    free = (f'<div class="tick" style="position:absolute;left:36px;right:8px;top:{fy + 2}px;height:{rowh - 4}px;border-radius:5px;border:1.5px dashed #5E8A57;background:rgba(94,138,87,.10);'
            f'animation-delay:1500ms;font-size:10.5px;font-weight:600;color:#3E6A38;display:flex;align-items:center;padding-left:8px">12:00 – 1:00 · both free</div>')
    H = top + 8 * rowh + 10
    iw = w - 28
    mark = overlay(iw, H, loop(36 + (iw - 44) / 2, fy + rowh / 2, (iw - 44) / 2 + 8, rowh * .95, delay=2200))
    return (f'<div style="position:relative;width:{w}px;height:{H + 16}px;background:#fff;border-radius:14px;box-shadow:0 0 0 1px var(--rule),0 16px 40px -18px rgba(60,40,20,.28);padding:0">'
            f'<div style="position:absolute;left:14px;top:-0px;right:14px;height:{H}px">'
            f'{grid}{col(30, busy_you, "slideL", "#F3D9CF", "You", 200)}{col(30 + colw + 4, busy_ava, "slideR", "#D9E4F2", "Ava", 350)}{free}</div>'
            f'<div style="position:absolute;left:14px;top:0;right:14px">{mark}</div></div>')

_px_n = [0]

def pixel(x0, y0, x1, y1, delay=1800):
    """A 1×1 tracking pixel drifts toward the inbox, hits the margin line, bounces off and fades. One shot."""
    _px_n[0] += 1
    k = f'px{_px_n[0]}'
    dx, dy = x1 - x0, y1 - y0
    return (f'<style>@keyframes {k}{{0%{{transform:translate(0,0);opacity:0}}8%{{opacity:1}}62%{{transform:translate({dx}px,{dy}px);opacity:1}}'
            f'78%{{transform:translate({dx * .82:.0f}px,{dy * .82 - 18:.0f}px);opacity:.8}}100%{{transform:translate({dx * .7:.0f}px,{dy * .7 + 30:.0f}px);opacity:0}}}}'
            f'.{k}{{animation:{k} 2800ms cubic-bezier(.4,.1,.4,1) {delay}ms both}}</style>'
            f'<g class="px {k}"><rect x="{x0 - 3}" y="{y0 - 3}" width="6" height="6" fill="#1D1B18"/>'
            f'<text x="{x0}" y="{y0 - 9}" text-anchor="middle" style="font-family:-apple-system,system-ui,sans-serif;font-size:10px;fill:#8A8174">1×1</text></g>')

