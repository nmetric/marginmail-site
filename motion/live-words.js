/*
 * Margin motion: live words — a reply to Ava types itself; each phrase is recognized as it completes.
 * "Tuesday with Ava" (day + person) underlines, tints and opens both calendars' free times (a hold is
 * placed); "the pricing deck" tints as a file and attaches Pricing deck.pdf; "by Friday" tints as a
 * promise. Every frame is a pure function of t (render(t)); the loop is 13 s.
 * Motion values from MarginKit/Sources/DesignSystem/MarginMotion.swift: underline (0.3 s, 0.3/0.7/0.2/1),
 * highlight (0.52 s, delay 0.22), layer spring (0.42, 0.74), chipDrop (0.34, 0.62, delay 0.14),
 * exits critically damped at 65 % of the entrance.
 */
(function () {
  'use strict';
  var NAME = 'live-words';
  var D = 13000, FADE_START = 11500, FADE_END = 12250, TYPE_START = 520;

  // ---- Easing ---------------------------------------------------------------------------------
  function cl(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }
  function pr(a, b, t) { return cl((t - a) / (b - a)); }
  function eo(t) { return 1 - Math.pow(1 - t, 3); }
  function eio(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function spring(s, response, damping) {
    if (s <= 0) return 0;
    var w = 2 * Math.PI / response;
    if (damping >= 1) return 1 - Math.exp(-w * s) * (1 + w * s);
    var wd = w * Math.sqrt(1 - damping * damping);
    return 1 - Math.exp(-damping * w * s) * (Math.cos(wd * s) + damping * w / wd * Math.sin(wd * s));
  }
  function bezier(x1, y1, x2, y2) {
    function f(a1, a2, u) { return 3 * a1 * u * (1 - u) * (1 - u) + 3 * a2 * u * u * (1 - u) + u * u * u; }
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      var lo = 0, hi = 1, u = x;
      for (var i = 0; i < 22; i++) { u = (lo + hi) / 2; if (f(x1, x2, u) < x) lo = u; else hi = u; }
      return f(y1, y2, u);
    };
  }
  var UNDERLINE = bezier(0.3, 0.7, 0.2, 1);  // MarginMotion.underline
  var INK = bezier(0.3, 0.7, 0.3, 1);        // MarginMotion.highlight
  function hash(i) { var s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); }

  // ---- Instances ------------------------------------------------------------------------------
  var roots = Array.prototype.slice.call(document.querySelectorAll('.mm-live-words[data-motion="live-words"]'));
  if (!roots.length) return;

  // Splits the sentence into one span per character (layout stays fixed; typing reveals them).
  function prepare(root) {
    var p = root.querySelector('.mm-lw__text');
    var chars = [], phrases = [], text = '';
    function split(node, into) {
      var s = node.nodeValue, frag = document.createDocumentFragment();
      for (var i = 0; i < s.length; i++) {
        var c = document.createElement('span');
        c.className = 'mm-lw__ch';
        c.textContent = s[i];
        frag.appendChild(c);
        chars.push(c);
        text += s[i];
      }
      into.replaceChild(frag, node);
    }
    Array.prototype.slice.call(p.childNodes).forEach(function (node) {
      if (node.nodeType === 3) split(node, p);
      else if (node.nodeType === 1) {
        var start = chars.length;
        Array.prototype.slice.call(node.childNodes).forEach(function (n) { if (n.nodeType === 3) split(n, node); });
        phrases.push({ el: node, kind: node.getAttribute('data-kind'), start: start, end: chars.length });
      }
    });
    return { p: p, chars: chars, phrases: phrases, text: text };
  }

  // A natural, deterministic typing rhythm: ~70 ms a key, a beat between words, longer after a comma.
  function typingTimes(text) {
    var t = TYPE_START, out = [];
    for (var i = 0; i < text.length; i++) {
      var prev = text[i - 1], d = 46 + hash(i) * 44;
      if (prev === ' ') d += 18 + hash(i + 31) * 70;
      if (prev === ',') d += 240;
      if (i === 0) d = 0;
      t += d;
      out.push(Math.round(t));
    }
    return out;
  }

  var inst = roots.map(function (root) {
    var it = prepare(root);
    it.root = root;
    it.body = root.querySelector('.mm-lw__body');
    it.caret = root.querySelector('.mm-lw__caret');
    it.pop = root.querySelector('.mm-lw__pop');
    it.slots = Array.prototype.slice.call(root.querySelectorAll('.mm-lw__slot'));
    it.slotLabel = it.slots[1] ? it.slots[1].querySelector('em') : null;
    it.footA = root.querySelector('.mm-lw__foot-a');
    it.footB = root.querySelector('.mm-lw__foot-b');
    it.cursor = root.querySelector('.mm-lw__cursor');
    it.fileChip = root.querySelector('.mm-lw__chip--file');
    it.promiseChip = root.querySelector('.mm-lw__chip--promise');
    it.times = typingTimes(it.text);
    var end = it.times[it.times.length - 1];
    function rec(kind) {
      for (var i = 0; i < it.phrases.length; i++) if (it.phrases[i].kind === kind) return it.times[it.phrases[i].end - 1] + 160;
      return end + 160;
    }
    it.phrases.forEach(function (ph) { ph.rec = it.times[ph.end - 1] + 160; });
    // The timeline, derived once from the typing.
    it.T = {
      typed: end,
      file: rec('file'),
      promise: rec('promise'),
      popIn: end + 480,
      cursorIn: end + 480 + 1250,
      click: end + 480 + 2150,
      popOut: end + 480 + 4300
    };
    it.T.hold = it.T.click + 80;
    it.still = it.T.click + 1100; // reduced motion: everything recognized, the hold placed
    it.lastN = -1;
    it.m = null;
    return it;
  });

  function offsetIn(el, ancestor) {
    var x = 0, y = 0;
    while (el && el !== ancestor) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
    return { x: x, y: y };
  }

  // Measures (layout space, unaffected by transforms). Pure given the width.
  function layout(it) {
    var m = { chars: [] };
    for (var i = 0; i < it.chars.length; i++) {
      var c = it.chars[i], o = offsetIn(c, it.body);
      m.chars.push({ x: o.x, y: o.y, w: c.offsetWidth, h: c.offsetHeight });
    }
    var ph = it.phrases[0].el, po = offsetIn(ph, it.body);
    var bodyW = it.body.clientWidth, popW = it.pop.offsetWidth, popH = it.pop.offsetHeight;
    m.popX = Math.max(0, Math.min(po.x - 4, bodyW - popW - 2));
    m.popY = po.y + ph.offsetHeight + 6;
    var s = it.slots[1], so = offsetIn(s, it.pop);
    m.curFrom = { x: popW - 18, y: popH + 6 };
    m.curTo = { x: so.x + s.offsetWidth * 0.66, y: so.y + s.offsetHeight * 0.5 };
    it.m = m;
  }

  function setOp(el, v) { el.style.opacity = v <= 0.0005 ? '0' : v >= 0.9995 ? '1' : v.toFixed(4); }

  function renderOne(it, t) {
    if (!it.m) layout(it);
    var T = it.T, m = it.m;
    // After the fade the frame is the opening frame again (tt < 0), so the loop has no seam.
    var tt = t >= FADE_END ? t - D : t;
    var g = 1 - eio(pr(FADE_START, FADE_END, tt));

    // Typed characters.
    var n = 0;
    while (n < it.times.length && it.times[n] <= tt) n++;
    if (n !== it.lastN) {
      for (var i = 0; i < it.chars.length; i++) it.chars[i].classList.toggle('is-on', i < n);
      it.lastN = n;
    }
    setOp(it.p, g);

    // Recognized phrases: the ink underline draws in, then tints as its kind.
    it.phrases.forEach(function (ph) {
      var u = UNDERLINE(pr(ph.rec, ph.rec + 300, tt));
      var k = INK(pr(ph.rec + 220, ph.rec + 740, tt));
      ph.el.style.setProperty('--u', u.toFixed(4));
      ph.el.style.setProperty('--tint', k.toFixed(4));
    });

    // Caret: solid while keys land, a blink otherwise.
    var typing = tt >= it.times[0] - 40 && tt <= T.typed + 380;
    var blinkOn = (((t % 1060) + 1060) % 1060) < 580;
    var cx, cy, ch;
    if (n === 0) { cx = m.chars[0].x; cy = m.chars[0].y; ch = m.chars[0].h; }
    else { var c = m.chars[n - 1]; cx = c.x + c.w; cy = c.y; ch = c.h; }
    it.caret.style.height = ch + 'px';
    it.caret.style.transform = 'translate3d(' + cx.toFixed(2) + 'px,' + cy.toFixed(2) + 'px,0)';
    setOp(it.caret, (typing || blinkOn ? 1 : 0) * g);

    // Chips drop into the attachment row (chipDrop, delay 0.14 s).
    [[it.fileChip, T.file], [it.promiseChip, T.promise]].forEach(function (pair) {
      var s = spring((tt - pair[1] - 140) / 1000, 0.34, 0.62);
      setOp(pair[0], cl(s * 1.6) * g);
      pair[0].style.transform = 'translate3d(' + (-16 * (1 - s)).toFixed(2) + 'px,' + (-8 * (1 - s)).toFixed(2) + 'px,0) scale(' + (0.94 + 0.06 * cl(s)).toFixed(4) + ')';
    });

    // The free-times layer rises under "Tuesday with Ava" (layer spring), leaves critically damped.
    var pIn = spring((tt - T.popIn) / 1000, 0.42, 0.74);
    var pOut = spring((tt - T.popOut) / 1000, 0.42 * 0.65, 1);
    var pv = cl(pIn * 1.6) * (1 - cl(pOut)) * g;
    setOp(it.pop, pv);
    it.pop.style.visibility = pv > 0.001 ? 'visible' : 'hidden';
    it.pop.style.transform = 'translate3d(' + m.popX.toFixed(2) + 'px,' + (m.popY + 10 * (1 - pIn) + 6 * pOut).toFixed(2) + 'px,0) scale(' + (0.96 + 0.04 * pIn).toFixed(4) + ')';

    // Shared free times, staggered; 1:30 is picked and the hold is placed.
    var on = eo(pr(T.click, T.click + 260, tt));
    it.slots.forEach(function (s, i) {
      var a = spring((tt - (T.popIn + 300 + i * 110)) / 1000, 0.32, 0.82);
      var press = i === 1 ? 0.045 * Math.sin(Math.PI * pr(T.click - 70, T.click + 190, tt)) : 0;
      setOp(s, cl(a * 1.4));
      s.style.transform = 'scale(' + (0.9 + 0.1 * a - press).toFixed(4) + ')';
      if (i === 1) s.style.setProperty('--on', on.toFixed(4));
    });
    if (it.slotLabel) setOp(it.slotLabel, pr(T.click + 140, T.click + 420, tt));
    setOp(it.footA, 1 - pr(T.hold, T.hold + 220, tt));
    var fb = pr(T.hold + 120, T.hold + 420, tt);
    setOp(it.footB, fb);
    it.footB.style.transform = 'translate3d(0,' + (4 * (1 - eo(fb))).toFixed(2) + 'px,0)';

    // The pointer glides to 1:30 and clicks.
    var mv = eio(pr(T.cursorIn + 100, T.click - 120, tt));
    var px = lerp(m.curFrom.x, m.curTo.x, mv), py = lerp(m.curFrom.y, m.curTo.y, mv);
    var clickS = 1 - 0.14 * Math.sin(Math.PI * pr(T.click - 70, T.click + 150, tt));
    setOp(it.cursor, pr(T.cursorIn, T.cursorIn + 220, tt) * (1 - pr(T.click + 520, T.click + 820, tt)));
    it.cursor.style.transform = 'translate3d(' + px.toFixed(2) + 'px,' + py.toFixed(2) + 'px,0) scale(' + clickS.toFixed(4) + ')';
  }

  // ---- Loop: one clock, pure frames, paused off-screen / hidden / reduced motion ---------------
  var reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var t = 0, last = null, raf = 0, wantPlay = true, stillShown = false;
  var onScreen = new Set();
  var hasIO = 'IntersectionObserver' in window;

  function render(time, still) {
    stillShown = !!still;
    for (var i = 0; i < inst.length; i++) {
      renderOne(inst[i], still ? inst[i].still : time);
      if (still) setOp(inst[i].caret, 0);
    }
  }
  function step(now) {
    raf = 0;
    if (last !== null) t = (t + Math.min(now - last, 100)) % D;
    last = now;
    render(t, false);
    schedule();
  }
  function visible() { return !hasIO || onScreen.size > 0; }
  function schedule() {
    if (!raf && wantPlay && visible() && !document.hidden && !reduce.matches) raf = requestAnimationFrame(step);
  }
  function halt() { if (raf) cancelAnimationFrame(raf); raf = 0; last = null; }
  function sync() {
    halt();
    if (wantPlay && reduce.matches) { render(0, true); return; }
    schedule();
  }

  if (hasIO) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) onScreen.add(en.target); else onScreen.delete(en.target); });
      sync();
    }, { threshold: 0 });
    roots.forEach(function (r) { io.observe(r); });
  }
  document.addEventListener('visibilitychange', sync);
  if (reduce.addEventListener) reduce.addEventListener('change', sync);
  if ('ResizeObserver' in window) {
    var ro = new ResizeObserver(function () { inst.forEach(layout); render(t, stillShown); });
    roots.forEach(function (r) { ro.observe(r); });
  }

  window.MarginMotion = window.MarginMotion || {};
  window.MarginMotion[NAME] = {
    duration: D,
    stillTime: inst[0].still,
    seek: function (ms) {
      wantPlay = false;
      halt();
      t = ((ms % D) + D) % D;
      inst.forEach(layout);
      render(t, false);
    },
    play: function () { wantPlay = true; sync(); },
    pause: function () { wantPlay = false; halt(); }
  };

  inst.forEach(layout);
  render(t, reduce.matches);
  sync();
})();
