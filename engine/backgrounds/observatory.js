/* Descartes Scroll — animated background: a city of the Enlightenment at
   dusk. An observatory dome on its hill, roofs and spires along a river with
   an arched bridge, lamplit windows, a balloon drifting over, and at night the
   constellations drawn among the stars. Same window.__hvLib3D / hvSetLib3D
   interface. */
(function(){
  if (window.__hvLib3D) return;
  var ID = 'hv-lib3d';
  var PAL = {
    light: { sky:['#b9cfe0','#e8dcc8','#eec4a0'], disc:'#fff4d6', glow:'255,232,180', hill:[120,132,128], dome:'#e8e2d4', domeSh:'#b9b2a2', city:[[150,138,132],[128,118,116],[104,98,102]], roof:[92,70,66], river:[130,160,178], riverHi:'255,250,235', bridge:[112,100,96], bank:[70,78,66], win:'rgba(255,236,190,.4)', balloon:['#b4483c','#f1e4c4'], line:'rgba(0,0,0,0)', star:0 },
    sepia: { sky:['#dedac6','#e6d8b8','#d8b890'], disc:'#fff0cc', glow:'250,228,176', hill:[136,132,116], dome:'#ece4d0', domeSh:'#bdb29a', city:[[156,142,124],[134,122,108],[112,102,92]], roof:[98,78,64], river:[150,154,144], riverHi:'255,248,228', bridge:[118,104,90], bank:[84,80,60], win:'rgba(255,232,180,.4)', balloon:['#a8503c','#efe2c0'], line:'rgba(0,0,0,0)', star:0 },
    dark:  { sky:['#04060e','#0b1226','#1a2038'], disc:'#eeeadc', glow:'200,208,240', hill:[22,28,36], dome:'#8e8e98', domeSh:'#55555f', city:[[30,30,42],[22,22,32],[14,14,22]], roof:[12,12,18], river:[14,22,40], riverHi:'210,220,255', bridge:[10,10,16], bank:[6,8,10], win:'rgba(255,208,128,.95)', balloon:['#4a2a2e','#6a6458'], line:'rgba(190,200,255,.28)', star:1 }
  };
  function theme(){ var t = document.documentElement.getAttribute('data-theme'); return (t === 'dark' || t === 'sepia') ? t : 'light'; }
  function rnd(seed){ var s = seed >>> 0; return function(){ s = (s + 0x6D2B79F5) | 0; var t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function rgb(c, a){ return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a == null ? 1 : a) + ')'; }
  var cv, cx, veil, W = 0, H = 0, DPR = 1, running = false, raf = 0, last = 0, T = 0, boost = 0, curTheme = '', frames = 0;
  var stars = [], cons = [], rows = [], bal = { x: 0 }, RIV = 0, U = 1;

  function build(){
    curTheme = theme();
    DPR = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    RIV = H * 0.8; U = Math.min(W, H);
    var r = rnd(1637), i, k, x;
    stars = []; for (i = 0; i < Math.min(220, W * H / 2400); i++) stars.push({ x: r() * W, y: r() * H * 0.6, s: r() * 1.2 + 0.3, p: r() * 6.283 });
    cons = []; for (k = 0; k < 3; k++){ var cx0 = W * (0.42 + k * 0.2 + r() * 0.06), cy0 = H * (0.07 + r() * 0.1), pts = []; for (i = 0; i < 5; i++) pts.push([cx0 + (i - 2) * U * 0.035 + r() * U * 0.02, cy0 + (r() - 0.5) * U * 0.09]); cons.push(pts); }
    rows = [];
    for (k = 0; k < 3; k++){ var row = []; x = -20;
      while (x < W + 20){ var w = U * (0.05 + r() * 0.06), h = U * (0.05 + r() * 0.08) * (1 + k * 0.25); row.push({ x: x, w: w, h: h, t: r() < 0.14 ? 2 : (r() < 0.5 ? 1 : 0), win: [r(), r(), r(), r(), r(), r()] }); x += w + 1; }
      rows.push(row); }
    bal.x = W * 0.7;
  }
  function draw(dt){
    var P = PAL[curTheme], g = cx, i, j, k, x;
    var sky = g.createLinearGradient(0, 0, 0, RIV);
    sky.addColorStop(0, P.sky[0]); sky.addColorStop(0.6, P.sky[1]); sky.addColorStop(1, P.sky[2]);
    g.fillStyle = sky; g.fillRect(0, 0, W, H);
    if (P.star){
      for (i = 0; i < stars.length; i++){ var st = stars[i]; g.fillStyle = 'rgba(238,240,255,' + (0.3 + 0.5 * (0.5 + 0.5 * Math.sin(T * 1.1 + st.p))) + ')'; g.fillRect(st.x, st.y, st.s, st.s); }
      g.strokeStyle = P.line; g.lineWidth = 1; g.fillStyle = 'rgba(240,242,255,.9)';
      for (k = 0; k < cons.length; k++){ g.beginPath(); for (i = 0; i < cons[k].length; i++){ if (!i) g.moveTo(cons[k][i][0], cons[k][i][1]); else g.lineTo(cons[k][i][0], cons[k][i][1]); } g.stroke(); for (i = 0; i < cons[k].length; i++){ g.beginPath(); g.arc(cons[k][i][0], cons[k][i][1], 1.6, 0, 6.283); g.fill(); } }
    }
    var sx = W * 0.8, sy = H * 0.2, sr = U * 0.045;
    var gl = g.createRadialGradient(sx, sy, 0, sx, sy, sr * 6); gl.addColorStop(0, 'rgba(' + P.glow + ',.45)'); gl.addColorStop(1, 'rgba(' + P.glow + ',0)');
    g.fillStyle = gl; g.fillRect(sx - sr * 6, sy - sr * 6, sr * 12, sr * 12);
    g.fillStyle = P.disc; g.beginPath(); g.arc(sx, sy, sr, 0, 6.283); g.fill();
    // observatory hill (left, high — clear of the title)
    var ht = H * 0.27, ox = W * 0.24, dr = U * 0.085;
    g.fillStyle = rgb(P.hill); g.beginPath(); g.moveTo(-10, H); g.lineTo(-10, ht + H * 0.03); g.quadraticCurveTo(ox - dr * 2.2, ht + 1, ox - dr * 1.6, ht + 1); g.lineTo(ox + dr * 1.6, ht + 1); g.bezierCurveTo(ox + dr * 2.6, ht + 1, ox + W * 0.2, ht + H * 0.1, ox + W * 0.32, ht + H * 0.2); g.quadraticCurveTo(ox + W * 0.5, ht + H * 0.34, W * 0.95, RIV - H * 0.1); g.lineTo(W * 0.95, H); g.fill();
    g.fillStyle = P.domeSh; g.fillRect(ox - dr * 1.4, ht - dr * 0.06, dr * 2.8, dr * 0.1 + 2);   // foundation course, seated on the hilltop
    g.fillStyle = P.domeSh; g.fillRect(ox - dr * 1.25, ht - dr * 0.75, dr * 2.5, dr * 0.75);
    g.fillStyle = P.dome; g.fillRect(ox - dr * 1.25, ht - dr * 0.75, dr * 1.5, dr * 0.75);
    g.beginPath(); g.arc(ox, ht - dr * 0.75, dr, Math.PI, 0); g.fill();
    g.fillStyle = P.domeSh; g.beginPath(); g.moveTo(ox + dr * 0.12, ht - dr * 0.75); g.arc(ox, ht - dr * 0.75, dr, -0.12, -1.25, true); g.lineTo(ox + dr * 0.12, ht - dr * 0.75); g.fill();   // the open slit
    g.strokeStyle = P.domeSh; g.lineWidth = dr * 0.12; g.lineCap = 'round'; g.beginPath(); g.moveTo(ox + dr * 0.25, ht - dr * 1.15); g.lineTo(ox + dr * 1.15, ht - dr * 1.95); g.stroke();   // telescope
    g.fillStyle = P.win; g.fillRect(ox - dr * 0.9, ht - dr * 0.55, dr * 0.22, dr * 0.34); g.fillRect(ox - dr * 0.3, ht - dr * 0.55, dr * 0.22, dr * 0.34);
    // balloon
    bal.x -= dt * (5 + boost * 20); if (bal.x < -60) bal.x = W + 60;
    var bx = bal.x, by = H * 0.4 + Math.sin(T * 0.35) * H * 0.012, br = U * 0.038;
    g.fillStyle = P.balloon[0]; g.beginPath(); g.arc(bx, by, br, 0, 6.283); g.fill();
    g.beginPath(); g.moveTo(bx - br * 0.8, by + br * 0.55); g.lineTo(bx, by + br * 1.6); g.lineTo(bx + br * 0.8, by + br * 0.55); g.fill();
    g.fillStyle = P.balloon[1]; g.beginPath(); g.ellipse(bx, by, br * 0.38, br, 0, 0, 6.283); g.fill();
    g.fillStyle = rgb(P.roof); g.fillRect(bx - br * 0.24, by + br * 1.75, br * 0.48, br * 0.34);
    g.strokeStyle = rgb(P.roof); g.lineWidth = 0.8; g.beginPath(); g.moveTo(bx - br * 0.22, by + br * 1.75); g.lineTo(bx - br * 0.3, by + br * 1.2); g.moveTo(bx + br * 0.22, by + br * 1.75); g.lineTo(bx + br * 0.3, by + br * 1.2); g.stroke();
    // three rows of houses, with spires
    for (k = 0; k < rows.length; k++){
      var base = RIV - H * 0.045 + k * H * 0.02, row = rows[k], c = P.city[k];
      for (i = 0; i < row.length; i++){ var b = row[i];
        g.fillStyle = rgb(c); g.fillRect(b.x, base - b.h, b.w, b.h + H * 0.03);
        g.fillStyle = rgb(P.roof, 0.9);
        if (b.t === 2){ g.beginPath(); g.moveTo(b.x + b.w * 0.3, base - b.h); g.lineTo(b.x + b.w * 0.5, base - b.h - b.w * 1.5); g.lineTo(b.x + b.w * 0.7, base - b.h); g.fill(); }
        else if (b.t === 1){ g.beginPath(); g.moveTo(b.x - 1, base - b.h); g.lineTo(b.x + b.w / 2, base - b.h - b.w * 0.38); g.lineTo(b.x + b.w + 1, base - b.h); g.fill(); }
        else g.fillRect(b.x - 1, base - b.h - 3, b.w + 2, 4);
        g.fillStyle = P.win; for (j = 0; j < 6; j++) if (b.win[j] > (curTheme === 'dark' ? 0.5 : 0.15)) g.fillRect(b.x + b.w * (0.2 + (j % 2) * 0.42), base - b.h + 6 + Math.floor(j / 2) * b.h * 0.28, Math.max(2, b.w * 0.14), Math.max(3, b.h * 0.1)); }
    }
    // river and bridge
    g.fillStyle = rgb(P.river); g.fillRect(0, RIV, W, H - RIV);
    for (i = 0; i < 20; i++){ var ly = RIV + 8 + (i * 37 % 100) / 100 * (H - RIV - 30), lx = (i * 97 + T * 8) % (W + 60) - 30;
      g.strokeStyle = 'rgba(' + P.riverHi + ',' + (0.2 + 0.2 * Math.sin(T * 1.7 + i)) + ')'; g.lineWidth = 1; g.beginPath(); g.moveTo(lx, ly); g.lineTo(lx + 16, ly); g.stroke(); }
    var by0 = RIV + H * 0.03, bh = H * 0.07, n = Math.max(3, Math.round(W / (bh * 2.4))), aw = W / n;
    g.fillStyle = rgb(P.bridge); g.beginPath(); g.moveTo(0, by0); g.lineTo(W, by0); g.lineTo(W, by0 + bh);
    for (i = n - 1; i >= 0; i--){ g.lineTo(i * aw + aw * 0.88, by0 + bh); g.arc(i * aw + aw / 2, by0 + bh, aw * 0.38, 0, Math.PI, true); g.lineTo(i * aw, by0 + bh); }
    g.fill(); g.fillRect(0, by0 - 3, W, 4);
    g.fillStyle = P.win; for (i = 0; i <= n; i++){ g.beginPath(); g.arc(i * aw, by0 - 8, 2.2, 0, 6.283); g.fill(); }
    g.fillStyle = rgb(P.bank); g.fillRect(0, H * 0.965, W, H * 0.04);
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
