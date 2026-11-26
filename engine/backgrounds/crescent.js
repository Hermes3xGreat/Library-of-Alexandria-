/* Crescent Scroll — animated background: the Fertile Crescent at dusk. A
   ziggurat and a domed city on the river, date palms, a camel caravan crossing
   the dunes, lamps in the windows; the crescent moon and the evening star over
   the desert. Same window.__hvLib3D / hvSetLib3D interface. */
(function(){
  if (window.__hvLib3D) return;
  var ID = 'hv-lib3d';
  var PAL = {
    light: { sky:['#f1dfc4','#e9bf98','#d99a7a'], moon:'#fff6dc', glow:'255,225,180', far:[190,150,140], mid:[160,112,96], near:[120,80,60], city:[120,84,80], water:[110,120,150], waterHi:'255,240,210', palm:[66,60,44], camel:[80,56,40], lamp:'rgba(255,210,120,0)', star:0 },
    sepia: { sky:['#eadcbc','#dcc29a','#c9a27c'], moon:'#fff3d6', glow:'240,210,160', far:[176,150,128], mid:[150,122,98], near:[112,88,66], city:[110,90,76], water:[120,120,120], waterHi:'250,236,206', palm:[70,62,44], camel:[82,62,44], lamp:'rgba(255,200,110,0)', star:0 },
    dark:  { sky:['#070814','#141533','#2a1e44'], moon:'#f4ecd2', glow:'200,190,255', far:[46,40,70], mid:[34,28,52], near:[20,16,30], city:[24,20,38], water:[22,26,52], waterHi:'200,200,255', palm:[10,10,16], camel:[12,10,16], lamp:'rgba(255,200,110,.95)', star:1 }
  };
  function theme(){ var t = document.documentElement.getAttribute('data-theme'); return (t === 'dark' || t === 'sepia') ? t : 'light'; }
  function rnd(seed){ var s = seed >>> 0; return function(){ s = (s + 0x6D2B79F5) | 0; var t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function rgb(c, a){ return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a == null ? 1 : a) + ')'; }
  var cv, cx, veil, W = 0, H = 0, DPR = 1, running = false, raf = 0, last = 0, T = 0, boost = 0, curTheme = '', frames = 0;
  var stars = [], palms = [], camels = { x: 0 }, HZ = 0, RIV = 0, dune = null, wins = [];

  function duneLine(seed, base, amp){
    var r = rnd(seed), k = [], i; for (i = 1; i <= 4; i++) k.push({ f: i * (0.5 + r()), a: amp / i, p: r() * 6.283 });
    return function(x){ var y = 0; for (var j = 0; j < k.length; j++) y += Math.sin(x / W * 6.283 * k[j].f + k[j].p) * k[j].a; return base + y; };
  }
  function build(){
    curTheme = theme();
    DPR = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    HZ = H * 0.6; RIV = H * 0.7;
    var r = rnd(321), i;
    stars = []; for (i = 0; i < Math.min(240, W * H / 2200); i++) stars.push({ x: r() * W, y: r() * HZ * 0.9, s: r() * 1.3 + 0.3, p: r() * 6.283 });
    palms = []; for (i = 0; i < Math.max(7, Math.round(W / 60)); i++) palms.push({ x: r() * W, h: H * (0.06 + r() * 0.06), lean: (r() - 0.5) * 0.3, p: r() * 6.283 });
    dune = duneLine(77, H * 0.86, H * 0.02);
    wins = []; for (i = 0; i < 26; i++) wins.push({ x: r(), y: r(), p: r() * 6.283 });
    camels.x = W * 0.1;
  }
  function ziggurat(g, x, base, w, P){
    g.fillStyle = rgb(P.city);
    var tiers = 4, h = w * 0.13;
    for (var i = 0; i < tiers; i++){ var tw = w * (1 - i * 0.22); g.fillRect(x - tw / 2, base - h * (i + 1), tw, h + 1); }
    g.fillRect(x - w * 0.06, base - h * tiers - h * 0.9, w * 0.12, h * 0.9);         // shrine on top
    g.beginPath(); g.moveTo(x - w * 0.04, base); g.lineTo(x - w * 0.02, base - h * 3); g.lineTo(x + w * 0.02, base - h * 3); g.lineTo(x + w * 0.04, base); g.fill();  // stair
  }
  function city(g, x0, x1, base, P){
    g.fillStyle = rgb(P.city);
    var x = x0, r = rnd(9), pts = [];
    while (x < x1){
      var w = 18 + r() * 34, h = 14 + r() * 30;
      g.fillRect(x, base - h, w, h);
      if (r() < 0.45){ g.beginPath(); g.arc(x + w / 2, base - h, w * 0.42, Math.PI, 0); g.fill(); g.fillRect(x + w / 2 - 1, base - h - w * 0.42 - 8, 2, 8); }   // dome + finial
      if (r() < 0.15){ g.fillRect(x + w * 0.4, base - h - 46, 6, 46); g.beginPath(); g.moveTo(x + w * 0.4 - 2, base - h - 46); g.lineTo(x + w * 0.4 + 3, base - h - 58); g.lineTo(x + w * 0.4 + 8, base - h - 46); g.fill(); }   // minaret
      pts.push([x, base - h, w, h]); x += w + 2 + r() * 6;
    }
    return pts;
  }
  function palm(g, x, y, h, lean, sway, col){
    g.strokeStyle = rgb(col); g.lineCap = 'round';
    var tx = x + lean * h + sway * h * 0.04, ty = y - h;
    g.lineWidth = Math.max(1.5, h * 0.05);
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + lean * h * 0.3, y - h * 0.5, tx, ty); g.stroke();
    g.lineWidth = Math.max(1, h * 0.03);
    for (var i = 0; i < 8; i++){
      var a = -Math.PI / 2 + (i - 3.5) * 0.42 + sway * 0.05, len = h * (0.45 + (i % 2) * 0.1);
      g.beginPath(); g.moveTo(tx, ty); g.quadraticCurveTo(tx + Math.cos(a) * len * 0.5, ty + Math.sin(a) * len * 0.5 - len * 0.1, tx + Math.cos(a) * len, ty + Math.sin(a) * len * 0.55 + len * 0.35); g.stroke();
    }
  }
  function camel(g, x, y, s, col, step){
    g.fillStyle = rgb(col); g.strokeStyle = rgb(col); g.lineWidth = 1.6 * s;
    g.beginPath(); g.ellipse(x, y - 14 * s, 12 * s, 6 * s, 0, 0, 6.283); g.fill();           // body
    g.beginPath(); g.ellipse(x - 2 * s, y - 20 * s, 6 * s, 5 * s, 0, 0, 6.283); g.fill();     // hump
    g.beginPath(); g.moveTo(x + 10 * s, y - 16 * s); g.quadraticCurveTo(x + 16 * s, y - 20 * s, x + 17 * s, y - 28 * s); g.stroke();  // neck
    g.beginPath(); g.ellipse(x + 19 * s, y - 28 * s, 3.4 * s, 2 * s, 0, 0, 6.283); g.fill();  // head
    var k = Math.sin(step) * 3 * s;
    [[-8, k], [-4, -k], [6, -k], [10, k]].forEach(function(l){ g.beginPath(); g.moveTo(x + l[0] * s, y - 10 * s); g.lineTo(x + l[0] * s + l[1], y); g.stroke(); });
  }
  function draw(dt){
    var P = PAL[curTheme], g = cx, i, x;
    var sky = g.createLinearGradient(0, 0, 0, HZ);
    sky.addColorStop(0, P.sky[0]); sky.addColorStop(0.6, P.sky[1]); sky.addColorStop(1, P.sky[2]);
    g.fillStyle = sky; g.fillRect(0, 0, W, H);
    if (P.star) for (i = 0; i < stars.length; i++){ var st = stars[i]; g.fillStyle = 'rgba(240,236,255,' + (0.3 + 0.5 * (0.5 + 0.5 * Math.sin(T * 1.1 + st.p))) + ')'; g.fillRect(st.x, st.y, st.s, st.s); }
    // crescent moon and the evening star
    var mx = W * 0.78, my = H * 0.17, mr = Math.min(W, H) * 0.045;
    var gl = g.createRadialGradient(mx, my, 0, mx, my, mr * 6); gl.addColorStop(0, 'rgba(' + P.glow + ',.45)'); gl.addColorStop(1, 'rgba(' + P.glow + ',0)');
    g.fillStyle = gl; g.fillRect(mx - mr * 6, my - mr * 6, mr * 12, mr * 12);
    var mc = draw.mc || (draw.mc = document.createElement('canvas')), ms = Math.ceil(mr * 2 + 4); mc.width = ms; mc.height = ms;
    var mg = mc.getContext('2d'); mg.fillStyle = P.moon; mg.beginPath(); mg.arc(ms / 2, ms / 2, mr, 0, 6.283); mg.fill();
    mg.globalCompositeOperation = 'destination-out'; mg.beginPath(); mg.arc(ms / 2 + mr * 0.42, ms / 2 - mr * 0.18, mr * 0.86, 0, 6.283); mg.fill();
    g.drawImage(mc, mx - ms / 2, my - ms / 2, ms, ms);
    g.fillStyle = P.moon; g.globalAlpha = 0.6 + 0.4 * Math.sin(T * 1.5);
    g.beginPath(); g.arc(mx - mr * 2.6, my + mr * 1.2, 2.2, 0, 6.283); g.fill(); g.globalAlpha = 1;
    // far desert
    g.fillStyle = rgb(P.far); g.beginPath(); g.moveTo(0, HZ); for (x = 0; x <= W; x += 10) g.lineTo(x, HZ - Math.sin(x / W * 5) * H * 0.012 - H * 0.01); g.lineTo(W, HZ + 2); g.lineTo(0, HZ + 2); g.fill();
    // ziggurat and the domed city on the far bank
    var zw = Math.min(W * 0.34, H * 0.24);
    ziggurat(g, W * 0.24, HZ + 4, zw, P);
    var pts = city(g, W * 0.42, W * 1.02, HZ + 4, P);
    g.fillStyle = P.lamp; g.globalAlpha = 0.85 + 0.15 * Math.sin(T * 3);
    for (i = 0; i < wins.length && pts.length; i++){ var b = pts[i % pts.length]; g.fillRect(b[0] + 3 + wins[i].x * (b[2] - 8), b[1] + 4 + wins[i].y * (b[3] - 10), 3, 4); }
    g.globalAlpha = 1;
    // river
    g.fillStyle = rgb(P.mid); g.fillRect(0, HZ + 4, W, RIV - HZ - 4);
    var ry0 = RIV - H * 0.03, ry1 = RIV + H * 0.03;
    g.fillStyle = rgb(P.water, 0.9); g.fillRect(0, ry0, W, ry1 - ry0);
    for (i = 0; i < 24; i++){
      var lx = (i * 113 + T * 14) % (W + 80) - 40, ly = ry0 + 5 + (i * 41 % 100) / 100 * (ry1 - ry0 - 8);
      g.strokeStyle = 'rgba(' + P.waterHi + ',' + (0.25 + 0.25 * Math.sin(T * 2 + i)) + ')'; g.lineWidth = 1;
      g.beginPath(); g.moveTo(lx, ly); g.lineTo(lx + 16 + (i % 3) * 7, ly); g.stroke();
    }
    // palms along the near bank
    for (i = 0; i < palms.length; i++){ var pm = palms[i]; palm(g, pm.x, ry1 + H * 0.012, pm.h, pm.lean, Math.sin(T * 0.8 + pm.p), P.palm); }
    // near dunes and the caravan
    g.fillStyle = rgb(P.near); g.beginPath(); g.moveTo(0, H); for (x = 0; x <= W; x += 8) g.lineTo(x, Math.max(ry1 + H * 0.03, dune(x))); g.lineTo(W, H); g.fill();
    camels.x += dt * (10 + boost * 30); if (camels.x > W + 160) camels.x = -160;
    var cs = Math.min(W, H) * 0.0016 + 0.5;
    for (i = 0; i < 4; i++){ var cxp = camels.x - i * 46 * cs; camel(g, cxp, dune(cxp) + 2, cs, P.camel, T * 4 + i); }
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
