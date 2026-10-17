/* marginmail.ai — the little JavaScript the site uses. No cookies, no tracking, nothing stored in the browser.
   The only counts are anonymous daily totals (a page view, and video tour engagement below), never per person. */
(function () {
  'use strict';
  var ENDPOINT = 'https://join.marginmail.ai/join';
  var doc = document, root = doc.documentElement;
  var reduce = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var hasIO = 'IntersectionObserver' in window;

  /* ---- Marks and moments start once their block is at least half in view (or fills half the screen) ---- */
  function halfIn(en) {
    return en.isIntersecting && (en.intersectionRatio >= 0.5 || en.intersectionRect.height >= 0.5 * innerHeight);
  }
  var seenEls = doc.querySelectorAll('[data-seen]');
  if (hasIO && !reduce.matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (halfIn(en)) en.target.classList.add('seen');
        // .off pauses anything that loops (glow breathing, the star's glint) while it's off screen.
        en.target.classList.toggle('off', !en.isIntersecting);
      });
    }, { threshold: [0, 0.25, 0.5, 0.75, 1] });
    seenEls.forEach(function (el) { io.observe(el); });
  } else {
    seenEls.forEach(function (el) { el.classList.add('seen'); });
  }

  /* ---- Motion components (stack, live words, write it): play only while at least half in view ---- */
  doc.addEventListener('DOMContentLoaded', function () {
    var MM = window.MarginMotion || {};
    doc.querySelectorAll('[data-motion]').forEach(function (el) {
      var api = MM[el.getAttribute('data-motion')];
      if (!api || !hasIO) return;
      if (reduce.matches) return; // the component shows its own still frame
      api.seek(0);
      var started = false;
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (halfIn(en)) { started = true; api.play(); }
          else if (!en.isIntersecting && started) api.pause();
        });
      }, { threshold: [0, 0.5, 1] }).observe(el);
    });
  });

  /* ---- Query parameters: referral code and source tag (never stored) ---- */
  var params = new URLSearchParams(location.search);
  var outcome = params.get('joined') === '1' || params.get('already') === '1' || params.get('error');
  var refParam = outcome ? '' : (params.get('r') || params.get('ref') || '').trim().toLowerCase();
  var srcParam = (params.get('utm_source') || params.get('src') || params.get('s') || params.get('source') || '').trim().toLowerCase();
  if (!/^[a-z2-9]{8}$/.test(refParam)) refParam = '';
  srcParam = srcParam.replace(/[^a-z0-9._-]/g, '').slice(0, 64);

  /* ---- Engagement counts (video tour): one anonymous sendBeacon per event, added to that day's totals on our server.
     The same gates as the page-view beacon: nothing for automation, Do Not Track, Global Privacy Control, ?ab= previews
     or localhost (unless ?debug). No ID of any kind is sent; the server keeps counts per event, variant and device class.
     ?mmtest=1 marks events as tests (filed apart, never in the stats), and lets a ?ab= preview send them. ---- */
  var EVENT_URL = ENDPOINT.replace(/\/join$/, '/event');
  var testMode = params.has('mmtest');
  function meta(k) { var e = doc.querySelector('meta[name="' + k + '"]'); return e ? e.content : ''; }
  function countEvent(name, source) {
    try {
      var n = navigator;
      if ((window.__abPreview && !testMode) || n.webdriver || n.doNotTrack == '1' || n.globalPrivacyControl || !n.sendBeacon) return;
      if (/^(localhost|127\.)/.test(location.hostname) && !params.has('debug')) return;
      var w = innerWidth;
      n.sendBeacon(EVENT_URL, new Blob([JSON.stringify({
        e: name, s: source || '', p: meta('page-path') || location.pathname, v: meta('page-version'), x: window.__ab || '',
        d: w < 768 ? 'phone' : w < 1200 ? 'tablet' : 'desktop', t: testMode ? '1' : ''
      })], { type: 'text/plain' }));
    } catch (e) { /* counting never gets in the way */ }
  }
  // The animated hero tour (variant TOUR) reaching its last frame: once per page load, however often it's replayed.
  var heroTourDone = false;
  doc.addEventListener('marginmail:hero-tour-ended', function () {
    if (heroTourDone) return;
    heroTourDone = true;
    countEvent('hero_tour_complete');
  });

  /* ---- Signup forms ---- */
  var EMAIL = /^[^\s@]+@[^\s@.]+(\.[^\s@.]+)*\.[a-z]{2,63}$/i;
  var ICON_ERR = '<svg width="15" height="15" viewBox="0 0 15 15" aria-hidden="true"><circle cx="7.5" cy="7.5" r="6.4" fill="none" stroke="#B3261E" stroke-width="1.4"/><path d="M7.5 4.2V8.2" stroke="#B3261E" stroke-width="1.5" stroke-linecap="round"/><circle cx="7.5" cy="10.6" r=".9" fill="#B3261E"/></svg>';
  var MARK = '<svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true"><path d="M12 7H8V27H12" fill="none" stroke="#6F371B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" pathLength="1" class="dw" style="animation-duration:460ms;animation-delay:150ms"/><path d="M13.06 17.56L17.89 22.83L26.94 12.1" fill="none" stroke="#C2531F" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" pathLength="1" class="dw" style="animation-duration:360ms;animation-delay:620ms"/></svg>';

  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  function showError(form, html, isNote) {
    var msg = form.querySelector('.join-msg');
    msg.className = 'join-msg' + (isNote ? ' soft' : '');
    msg.innerHTML = html;
  }
  function clearError(form) {
    var msg = form.querySelector('.join-msg');
    msg.className = 'join-msg';
    msg.innerHTML = '';
    form.querySelector('input[type=email]').removeAttribute('aria-invalid');
  }

  function showResult(box, data) {
    var form = box.querySelector('form');
    var out = box.querySelector('.join-result');
    var html;
    if (data.status === 'already') {
      html = '<div class="result" tabindex="-1"><p class="rt">You’re already on the list.</p>' +
        '<p class="sub" style="font-size:14.5px;line-height:22px;margin-top:6px">There’s nothing else to do. We’ll email you when your invite is ready.</p></div>';
    } else {
      var pos = typeof data.position === 'number' ? '<p class="pos">You’re number <b>' + data.position.toLocaleString('en-US') + '</b> in line.</p>' : '';
      var share = '';
      if (data.referral_url) {
        var shown = String(data.referral_url).replace(/^https?:\/\//, '');
        share = '<hr><p class="share">Share your link to move up</p>' +
          '<p class="sub" style="margin-top:2px">Each friend who joins with your link moves you up the list.</p>' +
          '<div class="share-row"><label class="vh" for="' + form.id + '-link">Your referral link</label>' +
          '<input class="field" id="' + form.id + '-link" readonly value="' + esc(shown) + '" data-url="' + esc(data.referral_url) + '">' +
          '<button type="button" class="btn ghost copy">Copy</button></div><p class="vh copied-msg" aria-live="polite"></p>';
      }
      html = '<div class="result" tabindex="-1"><div class="top">' + MARK + '<div><p class="rt">You’re on the list.</p>' + pos + '</div></div>' +
        '<p class="sub">We’ll email you when your invite is ready. Until then, that’s the only email you’ll get from us.</p>' + share + '</div>';
    }
    out.innerHTML = html;
    form.hidden = true;
    box.classList.add('seen');
    var card = out.querySelector('.result');
    card.focus({ preventScroll: true });
    var copy = out.querySelector('.copy');
    if (copy) copy.addEventListener('click', function () {
      var input = out.querySelector('.share-row .field');
      var url = input.getAttribute('data-url');
      var done = function () {
        copy.textContent = 'Copied';
        out.querySelector('.copied-msg').textContent = 'Link copied';
        setTimeout(function () { copy.textContent = 'Copy'; out.querySelector('.copied-msg').textContent = ''; }, 2000);
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(done, function () { input.value = url; input.select(); doc.execCommand('copy'); done(); });
      } else { input.value = url; input.select(); try { doc.execCommand('copy'); } catch (e) {} done(); }
    });
    // Every other form on the page now says the same thing.
    doc.querySelectorAll('.joinbox').forEach(function (other) {
      if (other !== box && !other.querySelector('form').hidden) {
        other.querySelector('.join-result').innerHTML = '<div class="result"><p class="rt">You’re on the list.</p><p class="sub">We’ll email you when your invite is ready.</p></div>';
        other.querySelector('form').hidden = true;
      }
    });
  }

  doc.querySelectorAll('.joinbox').forEach(function (box) {
    var form = box.querySelector('form');
    var input = form.querySelector('input[type=email]');
    var btn = form.querySelector('button[type=submit]');
    var label = btn.textContent;
    input.addEventListener('input', function () { if (input.hasAttribute('aria-invalid')) clearError(form); });

    form.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = input.value.trim();
      if (!email) {
        input.setAttribute('aria-invalid', 'true');
        showError(form, ICON_ERR + '<span>Add your email to join the beta.</span>');
        input.focus();
        return;
      }
      if (!EMAIL.test(email)) {
        input.setAttribute('aria-invalid', 'true');
        showError(form, ICON_ERR + '<span>That doesn’t look like an email address. Check it and try again.</span>');
        input.focus();
        return;
      }
      clearError(form);
      btn.disabled = true;
      btn.textContent = 'Joining…';
      form.setAttribute('aria-busy', 'true');
      var body = {
        email: email,
        source: srcParam || form.getAttribute('data-source') || '',
        ref: refParam,
        hp: form.querySelector('input[name=hp]').value,
        page: location.pathname,
        v: (form.querySelector('input[name=v]') || {}).value || '',
        x: window.__abPreview ? '' : (window.__ab || (form.querySelector('input[name=x]') || {}).value || '')
      };
      var ctrl = 'AbortController' in window ? new AbortController() : null;
      var timer = ctrl ? setTimeout(function () { ctrl.abort(); }, 15000) : 0;
      fetch(ENDPOINT, {
        method: 'POST', mode: 'cors', credentials: 'omit', referrerPolicy: 'no-referrer',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
        signal: ctrl ? ctrl.signal : undefined
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) { return { status: r.status, body: j }; });
      }).then(function (res) {
        clearTimeout(timer);
        if (res.status === 200 && (res.body.status === 'joined' || res.body.status === 'already')) { showResult(box, res.body); return; }
        if (res.status === 400 && res.body.error === 'invalid_email') {
          input.setAttribute('aria-invalid', 'true');
          showError(form, ICON_ERR + '<span>That doesn’t look like an email address. Check it and try again.</span>');
          input.focus();
        } else if (res.status === 429) {
          showError(form, '<span><b>One moment.</b> <span>Too many tries in a row. Wait a minute and try again.</span></span>', true);
        } else {
          throw new Error('status ' + res.status);
        }
      }).catch(function () {
        clearTimeout(timer);
        showError(form, '<span><b>That didn’t go through.</b> <span>Please try again in a moment. If it keeps happening, write to <a href="mailto:hello@marginmail.ai">hello@marginmail.ai</a>.</span></span>', true);
      }).then(function () {
        btn.disabled = false;
        btn.textContent = label;
        form.removeAttribute('aria-busy');
      });
    });
  });

  // A plain form post (no JavaScript) comes back as /?joined=1&p=<position>&r=<code>, /?already=1 or /?error=<code>.
  if (outcome) {
    var first = doc.querySelector('.joinbox');
    if (first) {
      if (params.get('joined') === '1') {
        var code = (params.get('r') || '').toLowerCase();
        var pos = parseInt(params.get('p'), 10);
        showResult(first, { status: 'joined', position: pos > 0 ? pos : undefined,
          referral_url: /^[a-z2-9]{8}$/.test(code) ? 'https://marginmail.ai/?r=' + code : undefined });
      } else if (params.get('already') === '1') {
        showResult(first, { status: 'already' });
      } else {
        var f = first.querySelector('form');
        if (params.get('error') === 'invalid_email') {
          f.querySelector('input[type=email]').setAttribute('aria-invalid', 'true');
          showError(f, ICON_ERR + '<span>That doesn’t look like an email address. Check it and try again.</span>');
        } else if (params.get('error') === 'rate_limited') {
          showError(f, '<span><b>One moment.</b> <span>Too many tries in a row. Wait a minute and try again.</span></span>', true);
        } else {
          showError(f, '<span><b>That didn’t go through.</b> <span>Please try again in a moment. If it keeps happening, write to <a href="mailto:hello@marginmail.ai">hello@marginmail.ai</a>.</span></span>', true);
        }
      }
      // The outcome isn't a page: drop it from the address bar so a reload or a shared link starts clean.
      if (history.replaceState) history.replaceState(null, '', location.pathname + '#join');
    }
  }

  /* ---- Second easter egg: the page icon's star twinkles when you click it on the page you're on ---- */
  var brand = doc.querySelector('.nav .brand');
  if (brand) brand.addEventListener('click', function (e) {
    if (location.pathname !== '/') return;
    e.preventDefault();
    brand.classList.remove('twinkle'); void brand.offsetWidth; brand.classList.add('twinkle');
    scrollTo({ top: 0, behavior: reduce.matches ? 'auto' : 'smooth' });
  });

  /* ---- Header menu on phones: close on choose or Escape ---- */
  var menu = doc.querySelector('.nav-menu');
  if (menu) {
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) menu.open = false; });
    doc.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); } });
    doc.addEventListener('click', function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
  }

  /* ---- "Join the beta" links focus the field once they arrive ---- */
  doc.querySelectorAll('a[href="#join"],a[href="/#join"]').forEach(function (a) {
    if (a.getAttribute('href') === '/#join' && location.pathname !== '/') return;
    a.addEventListener('click', function () {
      var f = doc.querySelector('#join input[type=email]');
      if (f && !f.closest('form').hidden) setTimeout(function () { f.focus({ preventScroll: true }); }, reduce.matches ? 0 : 450);
    });
  });

  /* ---- Sticky Join bar on phones: shows once the hero form has scrolled away, hides near any form ---- */
  var bar = doc.querySelector('.stickybar');
  if (bar && hasIO) {
    var visible = new Set(), passedHero = false;
    var heroForm = doc.querySelector('#join') && doc.querySelector('#join').closest('.joinbox');
    var watch = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) visible.add(en.target); else visible.delete(en.target);
        if (en.target === heroForm && !en.isIntersecting && en.boundingClientRect.top < 0) passedHero = true;
        if (en.target === heroForm && en.isIntersecting) passedHero = false;
      });
      var show = passedHero && visible.size === 0;
      bar.classList.toggle('show', show);
      bar.setAttribute('aria-hidden', show ? 'false' : 'true');
      bar.querySelector('a').tabIndex = show ? 0 : -1;
    });
    doc.querySelectorAll('.joinbox, .foot').forEach(function (el) { watch.observe(el); });
  }

  /* ---- Easter egg: the star above the sun twinkles; press it and a paper plane crosses the morning ---- */
  doc.querySelectorAll('.egg-btn').forEach(function (b) {
    var scene = b.closest('.joy-scene');
    b.addEventListener('click', function () {
      scene.classList.remove('fly', 'twinkle');
      void scene.offsetWidth;
      scene.classList.add('twinkle', 'found');
      if (!reduce.matches) scene.classList.add('fly');
      setTimeout(function () { scene.classList.remove('twinkle'); }, 950);
    });
  });

  /* ---- Video tour pop-up (copy_home.VIDEO_TOUR). Opened by the hero link (variant A) or the tour's "See MarginMail in action"
     button (variant TOUR, via the marginmail:video-tour event). Nothing loads until it opens: the dialog, the poster, the
     captions and the MP4 are all created then. Native controls, captions on, no third parties, no cookies. Closing fires
     marginmail:video-tour-closed so the hero tour resumes. ---- */
  var vtCfgEl = doc.getElementById('video-tour-cfg'), vtCfg = null;
  try { vtCfg = vtCfgEl ? JSON.parse(vtCfgEl.textContent) : null; } catch (e) { vtCfg = null; }
  var vtLink = doc.querySelector('[data-video-tour]');
  // The TOUR variant has its own button in the chapter row, so the link under A's window steps aside.
  if (vtLink && window.__abHero && window.__abHero.video) vtLink.parentNode.hidden = true;
  var vtDlg = null, vtVid = null, vtOpener = null, vtOpen = false;
  // Per open: the first play, and each quarter milestone crossed while playing (sent at most once per open). A reopen
  // resumes where it left off, so milestones already behind the playhead at open time aren't counted again.
  var VT_MARKS = [[0.25, 'tour_25'], [0.5, 'tour_50'], [0.75, 'tour_75']];
  var vtRun = null;
  function vtProgress(ended) {
    if (!vtOpen || !vtRun || !vtRun.played) return;
    var d = vtVid.duration;
    if (!(d > 0) || !isFinite(d)) return;
    var p = ended ? 1 : vtVid.currentTime / d;
    VT_MARKS.forEach(function (m) {
      if (p >= m[0] && m[0] > vtRun.from && !vtRun.sent[m[1]]) { vtRun.sent[m[1]] = 1; countEvent(m[1]); }
    });
    if (ended && !vtRun.sent.tour_complete) { vtRun.sent.tour_complete = 1; countEvent('tour_complete'); }
  }
  function vtFocusables() {
    return Array.prototype.filter.call(vtDlg.querySelectorAll('button,video[controls],a[href]'), function (el) { return !el.hidden && el.offsetParent !== null; });
  }
  function vtBuild(c) {
    vtDlg = doc.createElement('dialog');
    vtDlg.className = 'vmodal';
    vtDlg.setAttribute('aria-labelledby', 'vm-title');
    vtDlg.innerHTML = '<div class="vm-panel"><div class="vm-head"><h2 class="vm-title" id="vm-title">' + esc(c.title || c.label) + '</h2>' +
      '<button type="button" class="vm-close" aria-label="' + esc((c.close || 'Close') + ' the video') + '">' +
      '<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><path d="M3 3L11 11M11 3L3 11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>' +
      '<span>' + esc(c.close || 'Close') + '</span></button></div>' +
      '<div class="vm-frame"><video controls playsinline preload="none" width="' + (c.w || 1920) + '" height="' + (c.h || 1080) + '" poster="' + esc(c.poster) + '">' +
      '<source src="' + esc(c.src) + '" type="video/mp4">' +
      '<track kind="captions" srclang="en" label="English" src="' + esc(c.vtt) + '" default>' +
      '<a href="' + esc(c.src) + '">Download the video (MP4)</a></video></div></div>';
    doc.body.appendChild(vtDlg);
    vtVid = vtDlg.querySelector('video');
    var showCaptions = function () { for (var i = 0; i < vtVid.textTracks.length; i++) if (vtVid.textTracks[i].kind === 'captions') vtVid.textTracks[i].mode = 'showing'; };
    vtVid.addEventListener('loadedmetadata', showCaptions);
    showCaptions();
    vtVid.addEventListener('playing', function () {
      if (!vtOpen || !vtRun || vtRun.played) return;
      vtRun.played = true;
      countEvent('tour_play');
    });
    vtVid.addEventListener('timeupdate', function () { vtProgress(false); });
    vtVid.addEventListener('ended', function () { vtProgress(true); });
    vtDlg.querySelector('.vm-close').addEventListener('click', vtClose);
    // Esc: the dialog's own cancel, routed through vtClose so focus and the tour come back.
    vtDlg.addEventListener('cancel', function (e) { e.preventDefault(); vtClose(); });
    // A click on the dim area around the panel closes it.
    vtDlg.addEventListener('click', function (e) { if (e.target === vtDlg) vtClose(); });
    vtDlg.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { e.preventDefault(); vtClose(); return; }
      if (e.key !== 'Tab') return;
      var f = vtFocusables();
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1], a = doc.activeElement;
      if (e.shiftKey && (a === first || !vtDlg.contains(a))) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && (a === last || !vtDlg.contains(a))) { e.preventDefault(); first.focus(); }
    });
  }
  function vtOpenPlayer(c, opener, source) {
    c = c && c.src ? c : vtCfg;
    if (!c || !c.src || vtOpen) return;
    if (!vtDlg) vtBuild(c);
    vtOpener = opener || doc.activeElement;
    // Where this open starts (a finished video restarts from 0 when played again).
    var d = vtVid.duration, at = d > 0 && isFinite(d) && !vtVid.ended ? vtVid.currentTime / d : 0;
    vtRun = { played: false, sent: {}, from: at >= 0.98 ? 0 : at };
    vtOpen = true;
    countEvent('tour_open', source);
    root.classList.add('vm-on');
    if (vtDlg.showModal) vtDlg.showModal(); else vtDlg.setAttribute('open', '');
    vtDlg.classList.toggle('still', reduce.matches);
    // The click that opened the player is the user's go-ahead to play with sound. With Reduce Motion on, it waits for Play.
    if (!reduce.matches) {
      var pr = vtVid.play();
      if (pr && pr.catch) pr.catch(function () { /* the browser said no; the Play button is right there */ });
    }
    vtVid.focus();
  }
  function vtClose() {
    if (!vtOpen) return;
    vtOpen = false;
    vtVid.pause();
    if (vtDlg.close) vtDlg.close(); else vtDlg.removeAttribute('open');
    root.classList.remove('vm-on');
    var back = vtOpener && doc.contains(vtOpener) ? vtOpener : doc.querySelector('.tour-ch .vt') || vtLink;
    if (back && back.focus) back.focus();
    doc.dispatchEvent(new CustomEvent('marginmail:video-tour-closed'));
  }
  if (vtLink) vtLink.addEventListener('click', function (e) {
    if (!vtCfg || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return; // new tab / download still work
    e.preventDefault();
    vtOpenPlayer(vtCfg, vtLink, 'hero_link');
  });
  doc.addEventListener('marginmail:video-tour', function (e) {
    var t = doc.activeElement && doc.activeElement.closest ? doc.activeElement.closest('.vt') : null;
    vtOpenPlayer(e.detail, t || doc.querySelector('.tour-ch .vt'), 'tour_button');
  });

  /* ---- The scroll sky: CSS scroll-driven animations where supported; otherwise a light rAF fallback ---- */
  var sky = doc.querySelector('.sky');
  var scrollTimeline = window.CSS && CSS.supports && CSS.supports('animation-timeline: scroll()');
  if (sky && !scrollTimeline && !reduce.matches) {
    var sx = sky.querySelector('.sx'), sy = sky.querySelector('.sy');
    var am = sky.querySelector('.am'), pm = sky.querySelector('.pm'), hz = sky.querySelector('.horizon');
    var ticking = false;
    var frame = function () {
      ticking = false;
      var max = root.scrollHeight - innerHeight;
      var p = max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0;
      var vh = innerHeight / 100, vw = innerWidth / 100;
      var rise = 90 - 46 * vh * Math.sin(Math.PI * p);
      sx.style.transform = 'translateX(' + (8 * vw + 84 * vw * p).toFixed(1) + 'px)';
      sy.style.transform = 'translateY(' + rise.toFixed(1) + 'px)';
      am.style.opacity = (0.05 * Math.max(0, 1 - p / 0.4)).toFixed(4);
      pm.style.opacity = (0.045 * Math.max(0, (p - 0.6) / 0.4)).toFixed(4);
      hz.style.opacity = (Math.min(1, Math.max(0, (p - 0.02) / 0.06)) * (1 - Math.max(0, (p - 0.96) / 0.04))).toFixed(3);
    };
    var onScroll = function () { if (!ticking) { ticking = true; requestAnimationFrame(frame); } };
    addEventListener('scroll', onScroll, { passive: true });
    addEventListener('resize', onScroll, { passive: true });
    frame();
  }
})();
