/*
 * Margin motion: Write it — Claude drafts a reply to Marco in word batches (2–5 words a tick, like
 * model streaming) with a soft shimmer at the end; the state line goes "Claude is reading 4
 * messages…" → "Claude is writing…" → "Written by Claude on this Mac. Read it before you send." and
 * one DiffFlagChip appears ("Number not in the thread  $2,450"), its phrase tinted in the warning
 * color. Send is never pressed: sending stays with the user. Pure frames of t; the loop is 12 s.
 * Wording and chip styling from Apps/MarginMac/Compose/WritingStateLine.swift and
 * MarginKit/Sources/Compose/DraftDiffFlags.swift; springs from MarginMotion.swift.
 */
(function () {
  'use strict';
  var NAME = 'write-it';
  var D = 12000, FADE_START = 10500, FADE_END = 11250;
  var T = { press: 600, reading: 700, writing: 1900, streamStart: 2000 };

  function cl(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }
  function pr(a, b, t) { return cl((t - a) / (b - a)); }
  function eo(t) { return 1 - Math.pow(1 - t, 3); }
  function eio(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
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
  var INK = bezier(0.3, 0.7, 0.3, 1); // MarginMotion.highlight
  function hash(i) { var s = Math.sin(i * 91.7 + 47.3) * 43758.5453; return s - Math.floor(s); }
  function setOp(el, v) { el.style.opacity = v <= 0.0005 ? '0' : v >= 0.9995 ? '1' : v.toFixed(4); }

  var roots = Array.prototype.slice.call(document.querySelectorAll('.mm-write-it[data-motion="write-it"]'));
  if (!roots.length) return;

  // One span per word (whitespace stays as text, so wrapping is the final layout from the start).
  function splitWords(container) {
    var words = [];
    function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 3) {
          var frag = document.createDocumentFragment();
          n.nodeValue.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            var s = document.createElement('span');
            s.className = 'mm-wi__w';
            s.textContent = part;
            frag.appendChild(s);
            words.push(s);
          });
          node.replaceChild(frag, n);
        } else if (n.nodeType === 1 && !n.classList.contains('mm-wi__shimmer')) {
          walk(n);
        }
      });
    }
    walk(container);
    return words;
  }

  // Batches of 2–5 words, ticks of 130–260 ms: deterministic "streaming".
  function batches(count) {
    var out = [], t = T.streamStart, k = 0, i = 0;
    while (i < count) {
      var size = 2 + Math.floor(hash(k) * 4);
      for (var j = 0; j < size && i < count; j++, i++) out.push(t);
      t += 130 + Math.round(hash(k + 57) * 130);
      k++;
    }
    return out;
  }

  var inst = roots.map(function (root) {
    var body = root.querySelector('.mm-wi__body');
    var it = {
      root: root,
      body: body,
      words: splitWords(body),
      shimmer: root.querySelector('.mm-wi__shimmer'),
      flagged: root.querySelector('.mm-wi__flagged'),
      write: root.querySelector('.mm-wi__write'),
      wlIdle: root.querySelector('.mm-wi__wl--idle'),
      wlRun: root.querySelector('.mm-wi__wl--run'),
      wlDone: root.querySelector('.mm-wi__wl--done'),
      bar: root.querySelector('.mm-wi__bar'),
      fill: root.querySelector('.mm-wi__fill'),
      running: root.querySelector('.mm-wi__running'),
      pen: root.querySelector('.mm-wi__running .mm-wi__pen'),
      stRead: root.querySelector('.mm-wi__st--read'),
      stWrite: root.querySelector('.mm-wi__st--write'),
      written: root.querySelector('.mm-wi__written'),
      flag: root.querySelector('.mm-wi__flag'),
      m: null,
      lastN: -1
    };
    it.times = batches(it.words.length);
    var end = it.times[it.times.length - 1];
    it.T = { end: end, settled: end + 260, written: end + 320, tint: end + 700, flag: end + 900 };
    it.still = end + 2600; // reduced motion: the finished draft, provenance and flag
    return it;
  });

  function offsetIn(el, ancestor) {
    var x = 0, y = 0;
    while (el && el !== ancestor) { x += el.offsetLeft; y += el.offsetTop; el = el.offsetParent; }
    return { x: x, y: y };
  }
  function layout(it) {
    it.m = it.words.map(function (w) {
      var o = offsetIn(w, it.body);
      return { x: o.x, y: o.y, w: w.offsetWidth, h: w.offsetHeight };
    });
  }

  function renderOne(it, t) {
    if (!it.m) layout(it);
    var tt = t >= FADE_END ? t - D : t;           // after the fade: the opening frame again
    var g = 1 - eio(pr(FADE_START, FADE_END, tt));
    var S = it.T;

    // Words, batch by batch, each batch fading in.
    var n = 0;
    while (n < it.times.length && it.times[n] <= tt) n++;
    if (n !== it.lastN) {
      for (var i = 0; i < it.words.length; i++) it.words[i].classList.toggle('is-on', i < n);
      it.lastN = n;
    }
    for (var k = 0; k < it.words.length; k++) {
      var wt = it.times[k];
      if (wt <= tt && tt < wt + 260) setOp(it.words[k], eo(pr(wt, wt + 220, tt)) * g);
      else setOp(it.words[k], k < n ? g : 0);
    }

    // The soft shimmer after the last word while it streams.
    var streaming = tt >= T.streamStart - 120 && tt < S.settled;
    var sh = streaming ? (0.55 + 0.45 * Math.sin(tt / 170)) * pr(T.streamStart - 120, T.streamStart, tt) : 0;
    sh *= 1 - pr(S.end, S.settled, tt);
    var at = n === 0 ? { x: it.m[0].x, y: it.m[0].y, w: 0, h: it.m[0].h } : it.m[n - 1];
    it.shimmer.style.transform = 'translate3d(' + (at.x + at.w + 3).toFixed(2) + 'px,' + (at.y + at.h * 0.12).toFixed(2) + 'px,0)';
    it.shimmer.style.height = (at.h * 0.76).toFixed(2) + 'px';
    setOp(it.shimmer, sh * g);

    // The "Write it" chip: pressed, writing (progress), written.
    var press = Math.sin(Math.PI * pr(T.press - 60, T.press + 160, tt));
    it.write.style.transform = 'scale(' + (1 - 0.05 * press).toFixed(4) + ')';
    var running = pr(T.press, T.press + 180, tt) * (1 - pr(S.written, S.written + 220, tt));
    var done = pr(S.written, S.written + 240, tt) * g;
    setOp(it.wlIdle, cl(1 - running * g - done));
    setOp(it.wlRun, running * g);
    setOp(it.wlDone, done);
    var barOn = pr(T.press, T.press + 200, tt) * (1 - pr(S.settled + 100, S.settled + 400, tt));
    setOp(it.bar, barOn * g);
    if (tt < T.streamStart) {
      // Indeterminate while it reads: a 35% segment sweeping across.
      var ph = (((tt - T.reading) % 1100) + 1100) % 1100 / 1100;
      it.fill.style.transform = 'translate3d(' + (-35 + 135 * eio(ph)).toFixed(2) + '%,0,0) scaleX(.35)';
    } else {
      it.fill.style.transform = 'translate3d(0,0,0) scaleX(' + (n / it.words.length).toFixed(4) + ')';
    }

    // The state line: reading → writing, then the provenance line (layer spring, exit crossfade).
    var rIn = spring((tt - T.reading) / 1000, 0.42, 0.74);
    var rOut = pr(S.written - 40, S.written + 160, tt);
    setOp(it.running, cl(rIn * 1.5) * (1 - rOut) * g);
    it.running.style.transform = 'translate3d(0,' + (-6 * (1 - rIn)).toFixed(2) + 'px,0)';
    var toWrite = pr(T.writing, T.writing + 260, tt);
    setOp(it.stRead, 1 - toWrite);
    setOp(it.stWrite, toWrite);
    setOp(it.pen, 0.725 + 0.275 * Math.cos(Math.PI * Math.max(0, tt - T.reading) / 900));
    var wIn = spring((tt - S.written) / 1000, 0.42, 0.74);
    setOp(it.written, cl(wIn * 1.5) * g);
    it.written.style.transform = 'translate3d(0,' + (-6 * (1 - wIn)).toFixed(2) + 'px,0)';

    // The flag: the phrase inks in the warning tint, the chip drops in (chipDrop, delay 0.14 s).
    it.flagged.style.setProperty('--tint', (INK(pr(S.tint, S.tint + 520, tt)) * g).toFixed(4));
    var f = spring((tt - S.flag - 140) / 1000, 0.34, 0.62);
    setOp(it.flag, cl(f * 1.6) * g);
    it.flag.style.transform = 'translate3d(0,' + (-7 * (1 - f)).toFixed(2) + 'px,0) scale(' + (0.92 + 0.08 * f).toFixed(4) + ')';
  }

  // ---- Loop: one clock, pure frames, paused off-screen / hidden / reduced motion ---------------
  var reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var t = 0, last = null, raf = 0, wantPlay = true, stillShown = false;
  var onScreen = new Set();
  var hasIO = 'IntersectionObserver' in window;

  function render(time, still) {
    stillShown = !!still;
    for (var i = 0; i < inst.length; i++) renderOne(inst[i], still ? inst[i].still : time);
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
