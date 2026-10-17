/*
 * MarginMail hero tour (A/B variant TOUR): a scripted product tour inside the hero window. Loaded only for that variant
 * (abv.py's apply script injects it after the static hero has painted). Plays once when the hero is seen (site.js adds
 * .seen / .off on the figure), pauses on hover or focus, rests on the last frame. Chapters under the window jump to any
 * beat; Replay appears at the end. Reduce Motion: one still frame (each chapter shows its own still). Phones get four beats.
 * Every scene element is timed with CSS (--d); the clock only advances beats, so pausing stops both together.
 */
(function () {
  'use strict';
  var cfg = window.__abHero || {};
  var fig = document.querySelector('.hero-shot');
  if (!fig || fig.__tour || !cfg.beats) return;
  fig.__tour = 1;
  var win = fig.querySelector('.win'), pic = fig.querySelector('.pic'), shot = pic.querySelector('img');
  var mq = matchMedia('(max-width: 767px)'), rm = matchMedia('(prefers-reduced-motion: reduce)');
  var COPY = {};
  cfg.beats.forEach(function (b) { COPY[b.id] = b; });

  // ------------------------------------------------------------------ small builders
  function E(cls, d, st, inner) {
    return '<div class="' + cls + '" style="' + (d != null ? '--d:' + d + 'ms;' : '') + (st || '') + '">' + (inner || '') + '</div>';
  }
  function box(l, t, w, h) {
    return 'position:absolute;left:' + l + 'px;top:' + t + 'px;' + (w != null ? 'width:' + w + 'px;' : '') + (h != null ? 'height:' + h + 'px;' : '');
  }
  function hand(txt, l, t, size, rot, d) {
    return E('hand a-fade', d, box(l, t) + 'font-size:' + size + 'px;transform:rotate(' + rot + 'deg)', txt);
  }
  function r2(v) { return Math.round(v * 10) / 10; }
  function wob(x) { return 0.8 * Math.sin(x / 41) + 0.45 * Math.sin(x / 13); }
  function stroke(dd, d, t, color, sw, extra) {
    return '<path d="' + dd + '" pathLength="1" class="a-dw" style="--d:' + d + 'ms;--t:' + t + 'ms" fill="none" stroke="' + (color || '#C2531F') +
      '" stroke-width="' + (sw || 2.4) + '" stroke-linecap="round" stroke-linejoin="round"' + (extra || '') + '/>';
  }
  // The Clay loop from marks.py (loop()), drawn once around (cx, cy).
  function loop(cx, cy, rx, ry, d, t) {
    var p = [], n = 64, s = -2.15, tot = 2 * Math.PI + 0.55, m = 16;
    for (var i = 0; i <= n; i++) {
      var a = s + tot * i / n, k = 1 + 0.035 * Math.sin(3 * a + 1) + 0.02 * i / n;
      p.push(r2(m + rx + rx * k * Math.cos(a) + 0.04 * rx * i / n) + ' ' + r2(m + ry + ry * k * Math.sin(a) - 0.06 * ry * i / n));
    }
    var w = 2 * (rx + m), h = 2 * (ry + m);
    return '<svg aria-hidden="true" viewBox="0 0 ' + w + ' ' + h + '" style="' + box(cx - rx - m, cy - ry - m, w, h) + '">' + stroke('M' + p.join('L'), d, t || 760) + '</svg>';
  }
  // A pencil underline under a phrase (stretches to its width).
  function underline(d) {
    var p = [];
    for (var x = 0; x <= 100; x += 5) p.push(x + ' ' + r2(4 + wob(x * 3) * 0.9 - (x / 100) * (x / 100) * 2.4));
    return '<svg aria-hidden="true" viewBox="0 0 100 8" preserveAspectRatio="none">' + stroke('M' + p.join('L'), d, 420, '#C2531F', 2) + '</svg>';
  }
  function star(cx, cy, r, d) {
    var s = '';
    for (var i = 0; i < 5; i++) {
      var a = (-90 + 72 * i) * Math.PI / 180;
      s += stroke('M' + r + ' ' + r + 'L' + r2(r + r * Math.cos(a)) + ' ' + r2(r + r * Math.sin(a)), d + 60 * i, 200, '#C2531F', 2.2);
    }
    return '<svg aria-hidden="true" viewBox="0 0 ' + 2 * r + ' ' + 2 * r + '" style="' + box(cx - r, cy - r, 2 * r, 2 * r) + '">' + s + '</svg>';
  }
  function av(ini, color, size) {
    return '<span class="tr-av" style="--av:' + color + (size ? ';font-size:' + size + 'px' : '') + '">' + ini + '</span>';
  }
  var AV = { AL: '#2c6e8f', MR: '#8a5a2b', IH: '#8f3d5c', NC: '#6b5e4f', LB: '#5e7a3a' };
  var KIND = { date: ['#E3E9FB', '#2C47A8'], file: ['#FBE3DD', '#A3291B'], promise: ['#EFE5FA', '#5E2894'] };
  function weekImg() {
    var w = cfg.week;
    return w ? '<img class="tr-bg" src="' + w.src + '" srcset="' + w.srcset + '" sizes="' + w.sizes + '" alt="" decoding="async">' : '<div class="tr-bg" style="background:#FAF7F2"></div>';
  }

  // Typed text: one span per character (each appears at its own --d, with a Clay caret while it's the newest).
  function typed(segs, t0, ms) {
    var h = '', t = t0, ends = {}, last = 0;
    segs.forEach(function (s) {
      var inner = '';
      for (var i = 0; i < s[0].length; i++) {
        inner += '<span class="a-ch" style="--d:' + t + 'ms">' + s[0][i].replace('&', '&amp;').replace('<', '&lt;') + '</span>';
        t += ms;
      }
      if (s[1]) {
        ends[s[1]] = t;
        inner = '<span class="tr-ph" style="--bg:' + KIND[s[1]][0] + '"><i style="--d:' + (t + 60) + 'ms"></i>' + inner + underline(t + 60) + '</span>';
      }
      h += inner;
    });
    last = h.lastIndexOf('class="a-ch" style="');
    h = h.slice(0, last) + 'class="a-ch" style="--c:1400ms;' + h.slice(last + 20);
    return { html: h, ends: ends, end: t };
  }

  // ------------------------------------------------------------------ beat 1: floating composer, live words in the margin
  function words(m) {
    var segs = m
      ? [['Can we meet '], ['Tuesday with Ava', 'date'], ['? Here’s '], ['the pricing deck', 'file'], ['. '], ['I’ll send the quote by Friday', 'promise'], ['.']]
      : [['Hi Marco, can we go over the labels '], ['Tuesday with Ava', 'date'], ['? Here’s '], ['the pricing deck', 'file'], ['. '], ['I’ll send the signed quote by Friday', 'promise'], ['.']];
    var ty = typed(segs, m ? 600 : 800, m ? 30 : 26);
    var G = m ? { x: 8, y: 8, w: 344, h: 221, fs: 11.5, tx: 10, ty: 62, tw: 194, mx: 212, my: 54, tops: [6, 60, 112] }
              : { x: 318, y: 100, w: 660, h: 446, fs: 16, tx: 20, ty: 122, tw: 400, mx: 440, my: 104, tops: [12, 124, 214] };
    function card(kind, i, body) {
      return E('tr-note a-in', ty.ends[kind] + 220, 'top:' + G.tops[i] + 'px;--bg:' + KIND[kind][0] + ';--fg:' + KIND[kind][1], body);
    }
    var notes = m
      ? card('date', 0, '<span class="k">Tue, Oct 20</span><div class="sl"><span>10:00</span><span>1:30</span></div>') +
        card('file', 1, '<span class="tr-pdf">PDF</span>pricing deck<div class="tr-sub">Attached</div>') +
        card('promise', 2, '<span class="k">Promise</span><br>Quote by Fri')
      : card('date', 0, '<span class="k">Tue, Oct 20</span><br>You and Ava are both free<div class="sl"><span>10:00</span><span>1:30</span><span>4:00</span></div>') +
        card('file', 1, '<span class="k">Attached</span><br><span class="tr-pdf">PDF</span>Fernhill pricing deck.pdf<div class="tr-sub" style="margin-top:.3em">1.2 MB</div>') +
        card('promise', 2, '<span class="k">Promise</span><br>Signed quote to Marco by Fri, Oct 16');
    var comp = '<div class="hd"><i></i><i></i><i></i><span style="margin-left:.4em">Reply to Marco</span></div>' +
      '<div class="tr-row"><span>To</span><span class="tr-chip">' + av('MR', AV.MR) + 'Marco Reyes</span>' + (m ? '' : '<span class="tr-sub">Tidewater Print</span>') + '</div>' +
      (m ? '' : '<div class="tr-row"><span>Subject</span><span>Re: Saltmarsh labels: revised quote</span></div>') +
      '<div class="tr-txt" style="' + box(G.tx, G.ty, G.tw) + '">' + ty.html + '</div>' +
      '<div class="tr-mrg" style="left:' + G.mx + 'px;right:0;top:' + G.my + 'px">' + notes + '</div>' +
      (m ? '' : '<div class="ft"><span>Live words · rules only, no AI</span><span class="tr-btn k">Send</span></div>');
    var h = (m ? '<div class="tr-bg" style="background:#F4EFE8"></div>' : E('ab a-pulse', 100, box(1030, 8, 97, 32) + 'border-radius:16px;box-shadow:0 0 0 3px rgba(194,83,31,.5)')) +
      E('tr-comp a-pop', m ? 150 : 300, box(G.x, G.y, G.w, G.h) + 'font-size:' + G.fs + 'px', comp) +
      (m ? '' : hand('found as you type', 520, 420, 30, -3, ty.end + 300));
    return { html: h, dur: ty.end + (m ? 1500 : 1800) };
  }

  // ------------------------------------------------------------------ beat 2: an invite arrives, the calendar opens on it
  function invite(m) {
    var ban = function (w) {
      return '<span class="tr-ico"></span><div style="min-width:0"><b>Lena Brandt</b> <span class="tr-sub">· now</span>' +
        '<div>Invitation: Saltmarsh shoot walkthrough</div><div class="tr-sub">Thu, Oct 15 · 11:00 – 11:45 AM</div></div>';
    };
    var keys = function (l, t, d) {
      return E('a-out', d + 1200, box(0, 0), E('tr-keys a-pop', d, box(l, t), '<span class="a-press" style="--d:' + (d + 550) + 'ms">A</span><span>M</span><span>D</span>'));
    };
    if (m) {
      var y = function (h) { return 46 + (h - 9) * 44; }, hrs = '';
      ['9 AM', '10', '11', '12 PM', '1'].forEach(function (s, i) {
        hrs += '<div class="tr-hr" style="top:' + y(9 + i) + 'px;left:8px">' + s + '</div><div class="tr-line" style="left:42px;right:8px;top:' + y(9 + i) + 'px"></div>';
      });
      var h = '<div class="tr-bg" style="background:#FCFAF7"></div><div class="ab" style="left:12px;top:12px;font-size:14px"><b>Thu, Oct 15</b> <span class="tr-sub">· Calendar</span></div>' + hrs +
        E('tr-ev b', null, box(46, y(9) + 1, 180, 18), '<b>Studio standup</b>') +
        E('tr-ev q', null, box(46, y(11) + 2, 180, 32), '<b>Saltmarsh shoot walkthrough</b><span>11:00 – 11:45 AM</span>') +
        E('a-out', 1000, box(0, 0), E('tr-ban a-drop', 100, box(30, 6, 300) + 'font-size:11px', ban())) +
        loop(136, y(11.4), 100, 25, 1200, 640) +
        keys(246, y(11) - 1, 1500) +
        E('tr-ev a-fade', 2200, box(46, y(11) + 2, 180, 32), '<b>Saltmarsh shoot walkthrough</b><span>11:00 – 11:45 AM</span>') +
        hand('accepted with A', 170, y(12) + 8, 21, -4, 2300);
      return { html: '<div style="font-size:12px">' + h + '</div>', dur: 3400 };
    }
    var d = '';
    d += E('ab a-move', 600, box(119, 11, 52, 27) + '--x:56px;border-radius:14px;background:rgba(194,83,31,.16)');
    d += E('a-out', 1100, box(0, 0), E('tr-ban a-slide', 100, box(780, 56, 340), ban()));
    d += E('ab a-fade', 1000, 'inset:0', weekImg());
    d += loop(683, 368, 100, 30, 1500, 700);
    d += keys(618, 396, 1800);
    d += E('tr-ev a-fade', 2550, box(607, 353, 152, 31) + 'font-size:10.5px', '<b>Saltmarsh shoot walkthrough</b><span>11:00 – 11:45 AM</span>');
    d += E('ab a-fade', 2600, box(513, 96) + 'background:#F7F4EF;border-radius:999px', '<span class="tr-pill">Needs answer · 2</span>');
    d += hand('accepted with A', 772, 402, 28, -4, 2700);
    return { html: d, dur: 3800 };
  }

  // ------------------------------------------------------------------ beat 3: everyone's calendar side by side, the free hour circled
  function findTime(m) {
    var G = m ? { x: 6, y: 6, w: 348, h: 225, rowh: 19, gt: 50, pad: 10, fs: 11 } : { x: 290, y: 88, w: 560, h: 490, rowh: 34, gt: 146, pad: 22, fs: 13 };
    var cols = [['You', 'NC', '#F3D9CF', [[0, .25], [2, 2.75], [5, 7]]],
                ['Ava', 'AL', '#D9E4F2', [[.5, 1.5], [2, 3], [4, 5.5]]],
                ['Marco', 'MR', '#E6DCF2', [[0, 1], [1.5, 2.75], [4.25, 5], [6.5, 8]]]];
    var hw = m ? 22 : 34, gw = G.w - 2 * G.pad - hw, cw = gw / 3, inner = '';
    ['9', '10', '11', '12', '1', '2', '3', '4'].forEach(function (s, i) {
      var yy = G.gt + i * G.rowh;
      inner += '<div class="tr-line" style="left:' + G.pad + 'px;right:' + G.pad + 'px;top:' + yy + 'px"></div><div class="tr-hr" style="left:' + (G.pad + 2) + 'px;top:' + (yy + 8) + 'px">' + s + '</div>';
    });
    cols.forEach(function (c, i) {
      var x = G.pad + hw + i * cw, b = '<div class="ab" style="left:4px;top:' + (G.gt - (m ? 17 : 24)) + 'px;font-weight:600;display:flex;gap:.4em;align-items:center">' + (m ? '' : av(c[1], AV[c[1]], 11)) + c[0] + '</div>';
      c[3].forEach(function (s) { b += '<div class="tr-busy" style="left:3px;right:3px;top:' + (G.gt + s[0] * G.rowh + 1) + 'px;height:' + ((s[1] - s[0]) * G.rowh - 2) + 'px;background:' + c[2] + '"></div>'; });
      inner += E(i === 0 ? 'ab a-in' : i === 1 ? 'ab a-in' : 'ab a-slide', (m ? 300 : 500) + i * 120, box(x, 0, cw, G.h), b);
    });
    var fy = G.gt + 3 * G.rowh;
    inner += E('tr-free a-in', m ? 1000 : 1300, box(G.pad + hw + 2, fy + 2, gw - 4, G.rowh - 4), '12:00 – 1:00 · everyone’s free');
    inner += loop(G.pad + hw + gw / 2, fy + G.rowh / 2, gw / 2 + 10, G.rowh * 0.95, m ? 1300 : 1700, 760);
    var head = m
      ? '<div class="ab" style="left:10px;top:8px"><b>Saltmarsh label review</b> <span class="tr-sub">· Thu, Oct 15 · 1 hr</span></div>'
      : '<div class="ab" style="left:22px;top:16px"><div class="tr-lbl">Find a time</div><div style="font:400 22px/1.3 var(--serif)">Saltmarsh label review</div><div class="tr-sub">Thu, Oct 15 · 1 hour · Google Meet</div></div>' +
        '<div class="ab" style="left:22px;top:84px;display:flex;gap:6px">' +
        E('tr-chip a-pop', 350, '', av('NC', AV.NC, 10) + 'You') + E('tr-chip a-pop', 450, '', av('AL', AV.AL, 10) + 'Ava Lindqvist') + E('tr-chip a-pop', 550, '', av('MR', AV.MR, 10) + 'Marco Reyes') + '</div>';
    var foot = m
      ? E('ab a-pop', 2300, 'left:' + (G.w - 168) + 'px;top:' + (G.gt + 8 * G.rowh + 4) + 'px', '<span class="tr-pill">✓ Hold placed · 12:00</span>')
      : '<div class="ab" style="left:22px;right:22px;bottom:18px;display:flex;justify-content:space-between;align-items:center">' +
        E('a-pop', 2600, '', '<span class="tr-pill">✓ Hold placed · Thu 12:00 PM</span>') + '<span class="tr-btn k">Send invite</span></div>';
    var sheet = E('tr-panel a-pop', m ? 0 : 150, box(G.x, G.y, G.w, G.h) + 'background:#fff;font-size:' + G.fs + 'px', head + inner + foot);
    if (m) return { html: '<div class="tr-bg" style="background:#F4EFE8"></div>' + sheet, dur: 3600 };
    return { html: weekImg() + E('tr-dim a-fade', 0) + sheet + hand('everyone’s free here', 862, 404, 28, -4, 2300), dur: 4000 };
  }

  // ------------------------------------------------------------------ beat 4: the calendar sidebar, dragged wider: 1 day becomes 3
  function wide() {
    var y = function (h) { return 96 + (h - 7) * 48; };
    var days = [
      ['Tue 13', [[9, 9.25, 'Studio standup', 'b'], [10, 10.75, 'Saltmarsh label review', ''], [12.25, 13.25, 'Lunch with Hugo', ''], [14, 15.5, 'Focus: Kiln proposal', 'st'], [16, 16.25, 'Press check call', '']]],
      ['Wed 14', [[9, 9.25, 'Studio standup', 'b'], [10, 11, 'Kiln moodboard review', 'b'], [13.5, 14.5, 'Type pairing session', ''], [15.5, 15.9, 'Saltmarsh: copy for tins', 'q']]],
      ['Thu 15', [[9, 9.25, 'Studio standup', 'b'], [11, 11.75, 'Saltmarsh shoot walkthrough', ''], [14, 16, 'Press slot: Saltmarsh labels', '']]]];
    function col(day, l, w, head) {
      var s = '';
      day[1].forEach(function (e) {
        s += '<div class="tr-ev ' + e[3] + '" style="left:calc(' + l + '% + 3px);width:calc(' + w + '% - 6px);top:' + (y(e[0]) + 1) + 'px;height:' + (Math.max(e[1] - e[0], .36) * 48 - 2) + 'px"><b>' + e[2] + '</b></div>';
      });
      if (head) s += '<div class="ab" style="left:calc(' + l + '% + 4px);top:64px;font-weight:600">' + day[0] + '</div>';
      return s;
    }
    var grid = '';
    for (var h = 7; h <= 19; h++) {
      grid += '<div class="tr-hr" style="left:8px;top:' + y(h) + 'px">' + (h > 12 ? h - 12 : h) + (h < 12 ? ' AM' : ' PM') + '</div><div class="tr-line" style="left:48px;right:8px;top:' + y(h) + 'px"></div>';
    }
    var one = E('ab a-out', 1450, 'left:48px;right:8px;top:0;bottom:0', col(days[0], 0, 100) + '<div class="tr-now" style="left:0;right:0;top:' + y(9.68) + 'px"></div>');
    var three = E('ab a-fade', 1450, 'left:48px;right:8px;top:0;bottom:0', col(days[0], 0, 33.33, 1) + col(days[1], 33.33, 33.33, 1) + col(days[2], 66.66, 33.34, 1) +
      '<div class="tr-now" style="left:0;width:33.33%;top:' + y(9.68) + 'px"></div>');
    var heads = E('ab a-out', 1450, 'left:16px;top:18px;font-size:15px', '<b>Today</b> <span class="tr-sub">Tue, Oct 13</span>') +
      E('ab a-fade', 1450, 'left:16px;top:18px;font-size:15px', '<b>3 days</b> <span class="tr-sub">Oct 13 – 15</span>');
    var handle = E('a-out', 2300, box(0, 0) + 'top:0;bottom:0', E('ab a-fade', 450, 'left:-1px;top:0;bottom:0;width:3px;border-radius:2px;background:var(--clay)') +
      E('ab a-fade', 300, box(-13, 330, 26, 26), '<svg viewBox="0 0 26 26" style="left:0;top:0;width:26px;height:26px"><path d="M2 13h22M7 8l-5 5 5 5M19 8l5 5-5 5" fill="none" stroke="#1D1B18" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'));
    var panel = E('tr-panel a-fade a-widen', 800, 'top:48px;right:8px;bottom:8px;--l0:896px;--l1:520px;background:#FCFAF7;overflow:visible', heads + grid + one + three + handle);
    return { html: panel + hand('pull it wider: three days', 352, 620, 28, -3, 2300), dur: 3400 };
  }

  // ------------------------------------------------------------------ beat 5: the Margins stack, a card turns over, then Done
  function stack(m) {
    var G = m ? { x: 0, y: 0, w: 360, h: 237, cx: 56, cy: 64, cw: 248, ch: 160, fs: 10.5 } : { x: 338, y: 48, w: 548, h: 682, cx: 54, cy: 190, cw: 440, ch: 290, fs: 14.5 };
    function front(kind, when, why, ini, who, org, q, acts) {
      return '<div class="h"><span class="tr-lbl">' + kind + '</span><span class="r">' + when + '</span></div><div class="w">' + why + ' · <u>Why this?</u></div>' +
        '<div class="p">' + av(ini, AV[ini]) + '<div><b>' + who + '</b><span>' + org + '</span></div></div>' + (m ? '' : '<q>' + q + '</q>') +
        '<div class="acts">' + acts + '</div>';
    }
    function card(i, faceF, faceB, d) {
      var depth = m ? ['none', 'translateY(-22px) scale(.95)', 'translateY(-44px) scale(.9)'] : ['none', 'translateY(-34px) scale(.95)', 'translateY(-68px) scale(.9)'];
      var mot = i === 0 ? 'tr-card a-done" style="inset:0;--d:' + (m ? 2600 : 2900) + 'ms'
        : 'tr-card a-rise" style="inset:0;--d:' + ((m ? 2950 : 3350) + i * 100) + 'ms;--f:' + depth[i] + ';--to:' + depth[i - 1];
      var flip = '<div class="tr-flip' + (faceB ? ' a-flip" style="--d:' + (m ? 700 : 800) + 'ms' : '') + '"><div class="tr-face">' + faceF +
        (i === 0 ? E('tr-stamp a-pop', m ? 2800 : 3100, '', 'Done') : '') + '</div>' + (faceB ? '<div class="tr-face bk">' + faceB + '</div>' : '') + '</div>';
      return E('ab a-in', d, box(G.cx, G.cy, G.cw, G.ch) + 'z-index:' + (3 - i), '<div class="' + mot + '">' + flip + '</div>');
    }
    var back = '<div class="h"><b>Re: Spring catalog shoot</b><span class="r">Oct 9</span></div><div class="w">You to Ava Lindqvist</div>' +
      '<p style="margin-top:.8em;font:1.05em/1.5 var(--serif)">Hi Ava,<br><span class="tr-mark" style="--d:' + (m ? 1200 : 1400) + 'ms">Could you confirm the shot list by Friday</span> so Lena can plan the light?<br>Thanks, Nora</p>';
    var cards = card(2, front('Request', 'Thursday', 'Marco asked for the signed proof', 'MR', 'Marco Reyes', 'Tidewater Print', 'Could you send the signed proof before Thursday so we can hold the press slot?', '<span class="tr-btn k">Reply</span>'), null, 100) +
      card(1, front('Meeting', 'Next week', 'Imogen asked for 30 minutes', 'IH', 'Imogen Hale', 'Kiln &amp; Co.', 'Could we find 30 minutes next week to talk through scope?', '<span class="tr-btn k">Find a time</span>'), null, 200) +
      card(0, front('Follow-up', '6 days', 'You asked Ava on Oct 9, no reply in 6 days', 'AL', 'Ava Lindqvist', 'Saltmarsh Coffee', 'Could you confirm the shot list by Friday so Lena can plan the light?', '<span class="tr-btn k">Nudge</span><span class="tr-btn">Not useful</span>'), back, 300);
    var head = m ? '<div class="ab" style="left:12px;top:10px"><b>Margins</b> <span class="tr-sub">· 3 need you</span></div>'
      : '<div class="ab" style="left:24px;top:22px"><div style="font:400 24px/1.2 var(--serif)">Margins</div><div class="tr-sub">3 need you · drag right for Done, left for the back of the stack</div></div>';
    var panel = E('tr-panel a-fade', 0, box(G.x, G.y, G.w, G.h) + 'background:#F7F4EF;font-size:' + G.fs + 'px;' + (m ? 'border-radius:0' : ''), head + cards);
    return { html: panel + (m ? hand('drag right: Done', 222, 196, 21, -4, 3100) : hand('drag right: Done', 620, 560, 30, -4, 3300)), dur: m ? 4200 : 4400 };
  }

  // ------------------------------------------------------------------ beat 6: a person's page (personal CRM), then rest
  function people() {
    function pc(l, w, d, title, rows) { return E('tr-pc a-in', d, box(l, 206, w, 200), '<div class="t">' + title + '</div>' + rows); }
    function li(a, b, c) { return '<div class="li"><div>' + a + (c ? '<em>' + c + '</em>' : '') + '</div><span>' + b + '</span></div>'; }
    var body = '<div class="ab tr-crumb" style="left:28px;top:22px">Companies › saltmarshcoffee.com › <b>Ava Lindqvist</b></div>' +
      '<div class="ab" style="left:28px;top:60px">' + av('AL', AV.AL, 36) + '</div>' +
      '<div class="ab" style="left:118px;top:56px"><div class="tr-name">Ava Lindqvist</div>' +
      '<div style="margin-top:6px">Head of Brand, <b>Saltmarsh Coffee</b> <span class="tr-sub">· ava@saltmarshcoffee.com</span></div>' +
      '<div class="tr-sub" style="margin-top:4px"><b style="color:var(--clayink)">12:41 PM for Ava</b><span style="position:relative;display:inline-block;width:24px;height:1em;vertical-align:-3px">' + star(13, 8, 7, 1100) + '</span>· Portland, Maine · Eastern time</div></div>' +
      '<div class="ab" style="right:28px;top:62px;display:flex;gap:6px"><span class="tr-btn">Email</span><span class="tr-btn k">Find a time</span></div>' +
      pc(28, 240, 450, 'Conversations', li('Saltmarsh label review', 'Today') + li('Copy for the single-origin bags', 'Oct 8') + li('Re: Spring catalog shoot', 'Oct 7')) +
      pc(280, 240, 550, 'Meetings', li('Saltmarsh label review', 'Tue', '10:00 – 10:45 AM') + li('Saltmarsh shoot walkthrough', 'Thu', '11:00 – 11:45 AM')) +
      pc(532, 234, 650, 'Tasks', li('<i class="tk"></i>Send the final shot list', 'Fri') + li('<i class="tk"></i>Holiday tins: three directions', 'Oct 23')) +
      E('tr-pc a-in', 800, box(28, 424, 738, 100), '<div class="t">Saltmarsh Coffee <span class="tr-sub" style="font-weight:400">· everyone at saltmarshcoffee.com, together</span></div>' +
        '<div style="display:flex;align-items:center;gap:10px;margin-top:10px">' + av('AL', AV.AL, 12) + '<span class="tr-av" style="--av:#B9AFA2;font-size:12px;margin-left:-14px">+2</span>' +
        '<span class="tr-sub">3 people · 14 conversations · next meeting Tue 10:00 AM</span></div>');
    return { html: E('tr-panel a-slide', 0, box(338, 48, 794, 682) + 'background:#F7F4EF;font-size:15px', body) + hand('it’s lunchtime for Ava', 736, 116, 28, -3, 1400), dur: 3200 };
  }

  var BUILD = { words: words, invite: invite, time: findTime, wide: wide, stack: stack, people: people };
  var ORDER = { d: ['words', 'invite', 'time', 'wide', 'stack', 'people'], m: ['words', 'invite', 'time', 'stack'] };

  // ------------------------------------------------------------------ layer, chapters, clock
  var layer = document.createElement('div');
  layer.className = 'tour';
  layer.setAttribute('role', 'img');
  var stage = document.createElement('div');
  stage.className = 'tour-st';
  layer.appendChild(stage);
  pic.appendChild(layer);
  var ch = document.createElement('div');
  ch.className = 'tour-ch';
  ch.setAttribute('role', 'group');
  ch.setAttribute('aria-label', cfg.label || 'Product tour chapters');
  fig.appendChild(ch);

  var mobile, list, dur = 1, btns, rp, cur = -1, t = 0, last = 0, raf = 0, started = false, ended = false;
  var hov = false, foc = false, keep = false, off = false, vid = false;

  function fit() {
    var W = mobile ? 360 : 1140, k = pic.clientWidth / W || 1;
    stage.style.width = W + 'px';
    stage.style.height = Math.round(pic.clientHeight / k) + 'px';
    stage.style.transform = 'scale(' + k + ')';
  }
  function setup() {
    mobile = mq.matches;
    list = ORDER[mobile ? 'm' : 'd'].filter(function (id) { return COPY[id]; });
    ch.innerHTML = list.map(function (id) { return '<button type="button"><span>' + COPY[id].label + '</span><i></i></button>'; }).join('') +
      '<button type="button" class="rp" hidden>' + (cfg.replay || 'Replay') + '</button>' +
      // Video tour: hidden unless the build sets copy_home.VIDEO_TOUR; js/site.js opens the pop-up player.
      '<button type="button" class="vt"' + (cfg.video ? '' : ' hidden') + '>' + (cfg.video && cfg.video.label || 'See MarginMail in action') + '</button>';
    btns = ch.querySelectorAll('button:not(.rp):not(.vt)');
    rp = ch.querySelector('.rp');
    btns.forEach(function (b, i) { b.addEventListener('click', function () { keep = true; go(i); }); });
    rp.addEventListener('click', function () { keep = true; go(0); btns[0].focus(); });
    ch.querySelector('.vt').addEventListener('click', function () {
      vid = true; sync();
      document.dispatchEvent(new CustomEvent('marginmail:video-tour', { detail: cfg.video }));
    });
    stage.innerHTML = '';
    cur = -1;
    fit();
    layer.setAttribute('aria-label', cfg.label || '');
  }
  function show(i) {
    var still = rm.matches, b = BUILD[list[i]](mobile), sc = document.createElement('div');
    sc.className = 'tour-sc' + (still ? ' still' : '');
    sc.innerHTML = b.html;
    var old = stage.querySelectorAll('.tour-sc:not(.leave)');
    if (old.length && !still) {
      stage.insertBefore(sc, stage.firstChild);
      old.forEach(function (o) { o.classList.add('leave'); o.addEventListener('animationend', function (e) { if (e.target === o) o.remove(); }); });
    } else {
      stage.querySelectorAll('.tour-sc').forEach(function (o) { o.remove(); });
      if (!still && mobile) sc.classList.add('enter');
      stage.appendChild(sc);
    }
    cur = i; t = 0; dur = b.dur;
    layer.setAttribute('aria-label', COPY[list[i]].aria);
    shot.setAttribute('aria-hidden', 'true');
    btns.forEach(function (bt, j) { if (j === i) bt.setAttribute('aria-current', 'step'); else bt.removeAttribute('aria-current'); });
    bars();
  }
  function bars() {
    btns.forEach(function (bt, j) {
      var p = ended || j < cur ? 1 : j === cur ? Math.min(1, t / dur) : 0;
      bt.querySelector('i').style.setProperty('--p', rm.matches ? (j === cur ? 1 : 0) : p.toFixed(3));
    });
  }
  function go(i) {
    ended = false; rp.hidden = true; started = true;
    show(i);
    sync();
  }
  function frame(now) {
    raf = 0;
    if (last) t += Math.min(now - last, 100);
    last = now;
    if (t >= dur) {
      if (cur < list.length - 1) show(cur + 1);
      else { ended = true; rp.hidden = false; bars(); return sync(); }
    }
    bars();
    sync();
  }
  function sync() {
    var p = hov || (foc && !keep) || off || vid || document.hidden;
    layer.classList.toggle('paused', p);
    if (p || ended || !started || rm.matches) { if (raf) cancelAnimationFrame(raf); raf = 0; last = 0; return; }
    if (!raf) raf = requestAnimationFrame(frame);
  }
  function start() {
    if (started) return;
    if (rm.matches) { started = true; show(0); return; }
    if (!fig.classList.contains('seen')) return;
    if (cfg.week && !mobile) { var pre = new Image(); pre.sizes = cfg.week.sizes; pre.srcset = cfg.week.srcset; pre.src = cfg.week.src; }
    go(0);
  }

  setup();
  if (window.ResizeObserver) new ResizeObserver(fit).observe(pic); else addEventListener('resize', fit);
  new MutationObserver(function () { off = fig.classList.contains('off'); start(); sync(); }).observe(fig, { attributes: true, attributeFilter: ['class'] });
  win.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') { hov = true; sync(); } });
  win.addEventListener('pointerleave', function () { hov = false; sync(); });
  ch.addEventListener('focusin', function () { foc = true; sync(); });
  ch.addEventListener('focusout', function (e) { if (!ch.contains(e.relatedTarget)) { foc = false; keep = false; sync(); } });
  document.addEventListener('visibilitychange', sync);
  // Closing the video hands focus back to its button in the chapter row; like a chapter click, that shouldn't hold the tour paused.
  document.addEventListener('marginmail:video-tour-closed', function () { vid = false; keep = true; sync(); });
  function reset() { if (raf) cancelAnimationFrame(raf); raf = 0; started = false; ended = false; setup(); start(); sync(); }
  (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(reset);
  (rm.addEventListener ? rm.addEventListener.bind(rm, 'change') : rm.addListener.bind(rm))(reset);
  start();
})();
