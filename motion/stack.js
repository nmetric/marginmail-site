/*
 * Margin motion: the Margins stack — cards deal in beside today's calendar, the top card (Marco's
 * request) is dragged right for Done and flies off, the next rises, turns over to show its email,
 * and turns back. Every frame is a pure function of t; the loop is 12 s.
 * Motion values from MarginKit/Sources/DesignSystem/MarginMotion.swift and MarginCardView.swift:
 * card spring (0.42, 0.8) for the rise, flip spring (0.35, 0.8), highlight ink (0.52 s, delay 0.22),
 * exits critically damped. Cards behind peek out above the top card so their kinds read (the app
 * keeps them as plain paper; the web version shows the strip so all three kinds are visible).
 */
(function () {
  'use strict';
  var NAME = 'stack';
  var D = 12000;
  var T = {
    deal: 260, dealGap: 130,
    dragStart: 2100, dragEnd: 3300,
    fly: 3330, flyDur: 560,
    flip: 4750, sweep: 5420, flipBack: 8150,
    out: 9500, outEnd: 10250
  };
  var STILL_T = 6800; // reduced motion: Marco's card done, Ava's card turned over to its email

  function cl(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }
  function pr(a, b, t) { return cl((t - a) / (b - a)); }
  function eio(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
  function eo(t) { return 1 - Math.pow(1 - t, 3); }
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
  var INK = bezier(0.3, 0.7, 0.3, 1);
  function setOp(el, v) { el.style.opacity = v <= 0.0005 ? '0' : v >= 0.9995 ? '1' : v.toFixed(4); }

  var roots = Array.prototype.slice.call(document.querySelectorAll('.mm-stack[data-motion="stack"]'));
  if (!roots.length) return;

  var inst = roots.map(function (root) {
    var cards = [0, 1, 2, 3].map(function (i) {
      var el = root.querySelector('.mm-st__card[data-card="' + i + '"]');
      return {
        el: el,
        flip: el.querySelector('.mm-st__flip'),
        content: el.querySelector('.mm-st__front .mm-st__content'),
        shade: el.querySelector('.mm-st__shade')
      };
    });
    return {
      root: root,
      cards: cards,
      wash: root.querySelector('.mm-st__wash'),
      done: root.querySelector('.mm-st__done'),
      hl: root.querySelector('.mm-st__hl')
    };
  });

  // Where a card sits at a (fractional) depth: higher and a little smaller further back, so each
  // card behind shows its kind and when above the one in front.
  function depthStyle(d) { return { y: -d * 2, s: 1 - d * 0.035, shade: Math.min(d, 3) * 0.035 }; }

  function renderOne(it, t) {
    var out = eio(pr(T.out, T.outEnd, t));          // the whole stack lifts away before the loop
    var gone = 1 - out;
    var rise = spring((t - T.fly) / 1000, 0.42, 0.8); // the cards behind move up one place
    var drag = eio(pr(T.dragStart, T.dragEnd, t));
    var flyP = pr(T.fly, T.fly + T.flyDur, t);

    for (var i = 0; i < 4; i++) {
      var c = it.cards[i];
      // Deal in from above, back card first (spring with a little overshoot).
      var deal = spring((t - (T.deal + (3 - i) * T.dealGap)) / 1000, 0.5, 0.72);
      var dealY = -70 * (1 - deal);                  // % of the card's height
      var dealR = (i % 2 ? -5 : 4) * (1 - deal);
      var depth = i === 0 ? 0 : i - rise;
      var ds = depthStyle(depth);
      var x = 0, rot = dealR, op = cl(deal * 3) * gone, lift = 0;

      if (i === 0) {
        // Dragged right with a slight rotation, then flies off.
        x = 40 * drag + 135 * Math.pow(flyP, 1.7);
        rot += 5 * drag + 10 * Math.pow(flyP, 1.4);
        lift = -0.35 * Math.sin(Math.PI * drag * 0.5);
        op *= 1 - pr(0.45, 1, flyP);
      }
      var flipIn = 0, flipAngle = 0;
      if (i === 1) {
        flipIn = spring((t - T.flip) / 1000, 0.35, 0.8) - spring((t - T.flipBack) / 1000, 0.35, 0.8);
        flipAngle = 180 * flipIn;
        lift = -0.3 * Math.sin(Math.PI * cl(Math.abs(flipIn)));
      }
      var pop = i === 1 ? 1 + 0.025 * Math.sin(Math.PI * cl(flipIn)) : 1;
      c.el.style.transform =
        'translate3d(' + x.toFixed(3) + '%,0,0) translateY(calc(' + dealY.toFixed(3) + '% + ' + (ds.y + lift - out * 0.6).toFixed(4) + 'em)) ' +
        'rotate(' + rot.toFixed(3) + 'deg) scale(' + (ds.s * pop).toFixed(4) + ')';
      setOp(c.el, op);
      c.flip.style.transform = 'rotateY(' + flipAngle.toFixed(3) + 'deg)';
      if (c.shade) setOp(c.shade, ds.shade);
      if (c.content) {
        // Cards behind show only the strip above the card in front (their kind and when).
        setOp(c.content, 1);
      }
    }

    // Done: a green wash and badge as the drag passes halfway.
    var badge = spring((t - (T.dragStart + 650)) / 1000, 0.32, 0.68);
    setOp(it.done, cl(badge * 1.5));
    it.done.style.transform = 'rotate(-8deg) scale(' + (0.6 + 0.4 * badge).toFixed(4) + ')';
    setOp(it.wash, 0.1 * cl(badge));

    // The asked sentence on the back is swept with the highlighter.
    if (it.hl) it.hl.style.setProperty('--sweep', INK(pr(T.sweep + 220, T.sweep + 740, t)).toFixed(4));
  }

  // ---- Loop: one clock, pure frames, paused off-screen / hidden / reduced motion ---------------
  var reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var t = 0, last = null, raf = 0, wantPlay = true, stillShown = false;
  var onScreen = new Set();
  var hasIO = 'IntersectionObserver' in window;

  function render(time, still) { stillShown = !!still; for (var i = 0; i < inst.length; i++) renderOne(inst[i], still ? STILL_T : time); }
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

  window.MarginMotion = window.MarginMotion || {};
  window.MarginMotion[NAME] = {
    duration: D,
    stillTime: STILL_T,
    seek: function (ms) {
      wantPlay = false;
      halt();
      t = ((ms % D) + D) % D;
      render(t, false);
    },
    play: function () { wantPlay = true; sync(); },
    pause: function () { wantPlay = false; halt(); }
  };

  render(t, reduce.matches);
  sync();
})();
