/* Scroll starter background: an astrolabe of the Scroll's own colour and symbol,
   slowly turning, with drifting light motes and rising symbols. Each new Scroll
   gets its own colours, symbol and layout (seeded from its id) until a bespoke
   background replaces it. Same window.__hvLib3D / hvSetLib3D interface as the
   other Scroll backgrounds. CONFIG is filled in by tools/new_scroll.py. */
(function(){
  if (window.__hvLib3D) return;
  var CONFIG = __BG_CONFIG__;
  var ID = 'hv-lib3d';
  function hex(h){ h = h.replace('#',''); return [parseInt(h.substr(0,2),16), parseInt(h.substr(2,2),16), parseInt(h.substr(4,2),16)]; }
  function mix(a, b, k){ return [Math.round(a[0]+(b[0]-a[0])*k), Math.round(a[1]+(b[1]-a[1])*k), Math.round(a[2]+(b[2]-a[2])*k)]; }
  function rgb(c, a){ return 'rgba('+c[0]+','+c[1]+','+c[2]+','+(a == null ? 1 : a)+')'; }
  function rnd(seed){ var s = seed >>> 0; return function(){ s = (s + 0x6D2B79F5) | 0; var t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function hash(str){ var h = 2166136261; for (var i = 0; i < str.length; i++){ h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return h >>> 0; }
  var C = hex(CONFIG.color), GOLD = [227,196,119], CREAM = [244,236,217], NIGHT = [8,10,20];
  var PAL = {
    light: { top: mix(CREAM, C, .10), mid: mix(CREAM, C, .22), bot: mix(CREAM, C, .38), line: mix(C, [30,30,40], .2), lineA: .30, glow: mix(GOLD, C, .25), mote: mix(GOLD, C, .4), glyph: C, glyphA: .16 },
    sepia: { top: [236,224,196], mid: mix([226,208,171], C, .14), bot: mix([214,190,148], C, .26), line: mix(C, [60,45,30], .4), lineA: .30, glow: [214,170,96], mote: [190,140,70], glyph: mix(C, [80,60,40], .4), glyphA: .16 },
    dark:  { top: NIGHT, mid: mix(NIGHT, C, .28), bot: mix(NIGHT, C, .52), line: mix(GOLD, C, .25), lineA: .34, glow: mix(GOLD, C, .2), mote: mix(GOLD, CREAM, .3), glyph: mix(GOLD, CREAM, .3), glyphA: .20 }
  };
  function theme(){ var t = document.documentElement.getAttribute('data-theme'); return (t === 'dark' || t === 'sepia') ? t : 'light'; }
  var R = rnd(hash(CONFIG.id || 'scroll'));
  var LAYOUT = { cx: .5 + (R() - .5) * .3, cy: .38 + R() * .12, spokes: 6 + Math.floor(R() * 7), rings: 3 + Math.floor(R() * 3), tilt: R() * 6.283, dir: R() < .5 ? -1 : 1 };
  var cv, cx, veil, W = 0, H = 0, DPR = 1, running = false, raf = 0, last = 0, T = 0, boost = 0, curTheme = '', frames = 0, motes = [], glyphs = [];

  function build(){
    curTheme = theme();
    DPR = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    var r = rnd(hash(CONFIG.id || 'scroll') + 7), n = Math.round(Math.min(90, W * H / 9000)), i;
    motes = []; for (i = 0; i < n; i++) motes.push({ x: r() * W, y: r() * H, s: .6 + r() * 1.8, v: 4 + r() * 10, ph: r() * 6.283 });
    glyphs = []; for (i = 0; i < 7; i++) glyphs.push({ x: r() * W, y: r() * H, s: 18 + r() * 34, v: 5 + r() * 7, ph: r() * 6.283 });
  }
  function astrolabe(g, P, t){
    var ox = W * LAYOUT.cx, oy = H * LAYOUT.cy, Rm = Math.min(W, H) * .42, i, k;
    var gl = g.createRadialGradient(ox, oy, 0, ox, oy, Rm * 1.6);
    gl.addColorStop(0, rgb(P.glow, curTheme === 'dark' ? .22 : .30)); gl.addColorStop(1, rgb(P.glow, 0));
    g.fillStyle = gl; g.fillRect(0, 0, W, H);
    g.strokeStyle = rgb(P.line, P.lineA); g.lineWidth = 1;
    for (k = 0; k < LAYOUT.rings; k++){                // concentric rings, each turning its own way
      var rr = Rm * (1 - k * .19), rot = LAYOUT.tilt + t * .012 * LAYOUT.dir * (k % 2 ? -1 : 1) * (1 + k * .3);
      g.beginPath(); g.arc(ox, oy, rr, 0, 6.283); g.stroke();
      var ticks = k === 0 ? 72 : 24 + k * 12;
      for (i = 0; i < ticks; i++){
        var a = rot + i / ticks * 6.283, long = i % (ticks / 12 | 0 || 1) === 0;
        var r1 = rr - (long ? 10 : 4);
        g.beginPath(); g.moveTo(ox + Math.cos(a) * r1, oy + Math.sin(a) * r1); g.lineTo(ox + Math.cos(a) * rr, oy + Math.sin(a) * rr); g.stroke();
      }
    }
    var rot0 = LAYOUT.tilt - t * .02 * LAYOUT.dir;         // the rete: spokes and an eccentric circle
    for (i = 0; i < LAYOUT.spokes; i++){
      var b = rot0 + i / LAYOUT.spokes * 6.283;
      g.beginPath(); g.moveTo(ox, oy); g.lineTo(ox + Math.cos(b) * Rm * .62, oy + Math.sin(b) * Rm * .62); g.stroke();
    }
    g.beginPath(); g.arc(ox + Math.cos(rot0) * Rm * .16, oy + Math.sin(rot0) * Rm * .16, Rm * .46, 0, 6.283); g.stroke();
    g.fillStyle = rgb(P.glyph, P.glyphA * 1.6);
    g.font = '600 ' + Math.round(Rm * .26) + 'px Cinzel, "EB Garamond", Georgia, serif';
    g.textAlign = 'center'; g.textBaseline = 'middle';
    g.fillText(CONFIG.glyph || '', ox, oy);
  }
  function draw(dt){
    var P = PAL[curTheme], g = cx, i;
    var sky = g.createLinearGradient(0, 0, 0, H);
    sky.addColorStop(0, rgb(P.top)); sky.addColorStop(.55, rgb(P.mid)); sky.addColorStop(1, rgb(P.bot));
    g.fillStyle = sky; g.fillRect(0, 0, W, H);
    astrolabe(g, P, T);
    g.textAlign = 'center'; g.textBaseline = 'middle';
    for (i = 0; i < glyphs.length; i++){                 // the Scroll's symbol, rising slowly
      var q = glyphs[i]; q.y -= q.v * dt * (1 + boost * 3); if (q.y < -60){ q.y = H + 60; q.x = Math.random() * W; }
      g.fillStyle = rgb(P.glyph, P.glyphA * (.5 + .5 * Math.sin(T * .4 + q.ph)));
      g.font = Math.round(q.s) + 'px "EB Garamond", Georgia, serif'; g.fillText(CONFIG.glyph || '', q.x + Math.sin(T * .3 + q.ph) * 14, q.y);
    }
    for (i = 0; i < motes.length; i++){                  // drifting motes of light
      var m = motes[i]; m.y -= m.v * dt; m.x += Math.sin(T * .5 + m.ph) * .15; if (m.y < -4){ m.y = H + 4; m.x = Math.random() * W; }
      g.fillStyle = rgb(P.mote, .25 + .35 * (.5 + .5 * Math.sin(T * 1.3 + m.ph)));
      g.beginPath(); g.arc(m.x, m.y, m.s, 0, 6.283); g.fill();
    }
  }
  function frame(now){
    raf = 0; if (!running) return;
    var dt = last ? Math.min(.05, (now - last) / 1000) : 0; last = now; T += dt; boost *= .96; frames++;
    draw(dt); raf = requestAnimationFrame(frame);
  }
  function start(){ running = true; if (!raf && !document.hidden){ last = 0; raf = requestAnimationFrame(frame); } }
  function stop(){ running = false; if (raf){ cancelAnimationFrame(raf); raf = 0; } }
  function resize(){ W = window.innerWidth; H = window.innerHeight; build(); draw(0); }
  function init(){
    if (window.__hvLib3D) return;
    cv = document.createElement('canvas'); cv.id = ID; cv.setAttribute('aria-hidden', 'true');
    cv.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;z-index:-2;pointer-events:none;display:block';
    cx = cv.getContext('2d', { alpha: false });
    if (!cx) return;
    document.body.insertBefore(cv, document.body.firstChild);
    veil = document.getElementById('hv-lib3d-veil');
    if (!veil){ veil = document.createElement('div'); veil.id = 'hv-lib3d-veil'; veil.setAttribute('aria-hidden', 'true'); document.body.insertBefore(veil, cv.nextSibling); }
    W = window.innerWidth; H = window.innerHeight; build(); draw(0);
    var rz = 0; window.addEventListener('resize', function(){ clearTimeout(rz); rz = setTimeout(resize, 160); });
    document.addEventListener('visibilitychange', function(){ if (document.hidden){ if (raf){ cancelAnimationFrame(raf); raf = 0; } } else if (running) start(); });
    try { new MutationObserver(function(){ if (theme() !== curTheme){ build(); draw(0); } }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] }); } catch (e) {}
    document.documentElement.classList.remove('hv-lib3d-off'); document.documentElement.classList.add('hv-lib3d-on');
    window.__hvLib3D = { canvas: cv, gl: null, scrolls: 0, stop: stop, start: start, boost: function(){ boost = 1; },
      _q: function(){ return { running: running, frames: frames, theme: curTheme, w: W, h: H }; }, _setShot: function(){} };
    start(); scope();
  }
  function isReading(){
    try {
      var r = document.querySelector('[data-view]'), v = r ? r.getAttribute('data-view') : null;
      if (v === 'article' || v === 'dict' || document.documentElement.classList.contains('hv-conc-open')) return true;
      var u = document.getElementById('reader-view'); if (u && u.classList.contains('open')) return true;
    } catch (e) {}
    return false;
  }
  var was = null;
  function sync(){
    var r = isReading(); if (r === was) return; was = r; var d = document.documentElement;
    if (r){ d.classList.add('hv-reading'); d.classList.remove('hv-lib3d-on'); stop(); }
    else { d.classList.remove('hv-reading'); d.classList.add('hv-lib3d-on'); start(); }
  }
  function watch(){
    var r = document.querySelector('[data-view]');
    if (r && !r.__hvScopeObs){ r.__hvScopeObs = new MutationObserver(sync); r.__hvScopeObs.observe(r, { attributes: true, attributeFilter: ['data-view'] }); }
    var v = document.getElementById('reader-view');
    if (v && !v.__hvScopeObs){ v.__hvScopeObs = new MutationObserver(sync); v.__hvScopeObs.observe(v, { attributes: true, attributeFilter: ['class'] }); }
  }
  function scope(){
    window.addEventListener('hashchange', function(){ watch(); sync(); }); window.addEventListener('popstate', function(){ watch(); sync(); });
    watch(); sync(); setTimeout(function(){ watch(); sync(); }, 700); setTimeout(function(){ watch(); sync(); }, 2500);
  }
  function enabled(){ try { return localStorage.getItem('hermes_lib3d') !== 'off' && !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); } catch (e) { return true; } }
  function boot(){ if (enabled()) init(); else document.documentElement.classList.add('hv-lib3d-off'); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
  window.hvSetLib3D = function(on){
    try { localStorage.setItem('hermes_lib3d', on ? 'on' : 'off'); } catch (e) {}
    var d = document.documentElement;
    if (on){ if (window.__hvLib3D){ d.classList.remove('hv-lib3d-off'); d.classList.add('hv-lib3d-on'); cv.style.display = 'block'; start(); } else init(); }
    else { stop(); if (cv) cv.style.display = 'none'; d.classList.remove('hv-lib3d-on'); d.classList.add('hv-lib3d-off'); }
    return !!on;
  };
  window.hvLib3DEnabled = function(){ try { return localStorage.getItem('hermes_lib3d') !== 'off'; } catch (e) { return false; } };
})();
