/* Americas Scroll — animated background: a Maya pyramid above the jungle.
   A stepped temple on its mound, mountains beyond, layered rainforest canopy,
   mist drifting through the trees, a river, macaws crossing, fireflies at dusk;
   the sun by day, the moon and the Milky Way by night. Same window.__hvLib3D /
   hvSetLib3D interface. */
(function(){
  if (window.__hvLib3D) return;
  var ID = 'hv-lib3d';
  var PAL = {
    light: { sky:['#dfeee8','#f2dfb8','#efc08a'], disc:'#f4a63a', glow:'255,200,120', mtn:[150,160,150], temple:[150,140,118], templeShade:[112,104,88], far:[94,124,96], mid:[62,96,66], near:[34,62,40], river:[96,140,140], mist:'240,244,236', bird:['#c8402e','#2f6fb0','#e2b23a'], fly:'255,240,150', galaxy:0 },
    sepia: { sky:['#e8e0c4','#e2cfa2','#d4ad7c'], disc:'#d9893a', glow:'240,190,120', mtn:[160,150,128], temple:[156,140,110], templeShade:[118,104,82], far:[118,124,94], mid:[88,98,70], near:[56,64,44], river:[120,130,116], mist:'244,236,216', bird:['#a8432f','#4a6a8a','#c89a3a'], fly:'255,230,150', galaxy:0 },
    dark:  { sky:['#03060c','#0a1424','#152338'], disc:'#eef0e6', glow:'200,220,255', mtn:[36,46,58], temple:[44,48,58], templeShade:[28,30,40], far:[18,30,30], mid:[12,22,20], near:[6,12,10], river:[18,32,44], mist:'150,170,190', bird:['#5a2a26','#2a3a5a','#5a4a26'], fly:'200,255,150', galaxy:1 }
  };
  function theme(){ var t = document.documentElement.getAttribute('data-theme'); return (t === 'dark' || t === 'sepia') ? t : 'light'; }
  function rnd(seed){ var s = seed >>> 0; return function(){ s = (s + 0x6D2B79F5) | 0; var t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function rgb(c, a){ return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a == null ? 1 : a) + ')'; }
  var cv, cx, veil, W = 0, H = 0, DPR = 1, running = false, raf = 0, last = 0, T = 0, boost = 0, curTheme = '', frames = 0;
  var stars = [], canopies = [], birds = [], flies = [], mists = [], HZ = 0;

  function canopy(seed, base, bump){
    var r = rnd(seed), xs = [], x = -20;
    while (x < 4000){ var rr = bump * (0.6 + r() * 0.8); xs.push([x, rr]); x += rr * (1.1 + r() * 0.6); }
    return { base: base, xs: xs };
  }
  function build(){
    curTheme = theme();
    DPR = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    HZ = H * 0.6;
    var r = rnd(1519), i;
    stars = []; for (i = 0; i < Math.min(320, W * H / 1600); i++){ var gx = r() * W; stars.push({ x: gx, y: r() * HZ * 0.95, s: r() * 1.3 + 0.2, p: r() * 6.283, band: Math.abs((gx / W) - 0.35 - r() * 0.05) < 0.12 }); }
    canopies = [canopy(11, HZ + H * 0.04, H * 0.035), canopy(23, HZ + H * 0.12, H * 0.05), canopy(37, H * 0.9, H * 0.07)];
    birds = []; for (i = 0; i < 3; i++) birds.push({ x: r() * W, y: H * (0.18 + r() * 0.2), v: 26 + r() * 14, c: i % 3, p: r() * 6.283 });
    flies = []; for (i = 0; i < 40; i++) flies.push({ x: r() * W, y: HZ + r() * (H - HZ), p: r() * 6.283, s: 0.8 + r() * 1.2 });
    mists = []; for (i = 0; i < 5; i++) mists.push({ x: r() * W, y: HZ + H * (0.02 + r() * 0.16), w: W * (0.3 + r() * 0.4), v: 3 + r() * 5 });
  }
  function drawCanopy(g, c, col){
    g.fillStyle = rgb(col); g.beginPath(); g.moveTo(0, H);
    for (var i = 0; i < c.xs.length; i++){ var p = c.xs[i]; if (p[0] > W + 60) break; g.lineTo(p[0], c.base); g.arc(p[0] + p[1] * 0.6, c.base, p[1] * 0.7, Math.PI, 0); }
    g.lineTo(W, H); g.closePath(); g.fill();
  }
  function temple(g, x, base, w, P){
    var tiers = 7, h = w * 0.085, i;
    for (i = 0; i < tiers; i++){
      var tw = w * (1 - i * 0.11), y = base - h * (i + 1);
      g.fillStyle = rgb(P.temple); g.fillRect(x - tw / 2, y, tw, h + 1);
      g.fillStyle = rgb(P.templeShade); g.fillRect(x + tw * 0.18, y, tw * 0.32, h + 1);   // shaded side
    }
    g.fillStyle = rgb(P.templeShade);                                                      // central stair
    g.beginPath(); g.moveTo(x - w * 0.09, base); g.lineTo(x - w * 0.05, base - h * tiers); g.lineTo(x + w * 0.05, base - h * tiers); g.lineTo(x + w * 0.09, base); g.fill();
    var top = base - h * tiers, sw = w * 0.22;
    g.fillStyle = rgb(P.temple); g.fillRect(x - sw / 2, top - h * 1.6, sw, h * 1.6);        // shrine
    g.fillStyle = rgb(P.templeShade); g.fillRect(x - sw * 0.12, top - h * 1.1, sw * 0.24, h * 1.1);   // doorway
    g.fillStyle = rgb(P.temple); g.fillRect(x - sw * 0.4, top - h * 2.6, sw * 0.8, h);       // roof comb
  }
  function draw(dt){
    var P = PAL[curTheme], g = cx, i, x;
    var sky = g.createLinearGradient(0, 0, 0, HZ);
    sky.addColorStop(0, P.sky[0]); sky.addColorStop(0.6, P.sky[1]); sky.addColorStop(1, P.sky[2]);
    g.fillStyle = sky; g.fillRect(0, 0, W, H);
    if (P.galaxy){
      for (i = 0; i < stars.length; i++){ var st = stars[i]; g.fillStyle = 'rgba(236,240,255,' + ((st.band ? 0.55 : 0.3) + 0.35 * Math.sin(T * 1.1 + st.p) * 0.5) + ')'; g.fillRect(st.x, st.y, st.s, st.s); }
      var mw = g.createLinearGradient(W * 0.15, 0, W * 0.6, HZ); mw.addColorStop(0, 'rgba(180,190,230,0)'); mw.addColorStop(0.5, 'rgba(180,190,230,.08)'); mw.addColorStop(1, 'rgba(180,190,230,0)');
      g.fillStyle = mw; g.fillRect(0, 0, W, HZ);
    }
    var sx = W * 0.8, sy = H * 0.2, sr = Math.min(W, H) * 0.05;
    var gl = g.createRadialGradient(sx, sy, 0, sx, sy, sr * 6); gl.addColorStop(0, 'rgba(' + P.glow + ',.5)'); gl.addColorStop(1, 'rgba(' + P.glow + ',0)');
    g.fillStyle = gl; g.fillRect(sx - sr * 6, sy - sr * 6, sr * 12, sr * 12);
    g.fillStyle = P.disc; g.beginPath(); g.arc(sx, sy, sr, 0, 6.283); g.fill();
    // mountains
    g.fillStyle = rgb(P.mtn); g.beginPath(); g.moveTo(0, HZ);
    for (x = 0; x <= W; x += 8) g.lineTo(x, HZ - H * 0.07 - Math.abs(Math.sin(x / W * 4.2 + 1)) * H * 0.07 - Math.sin(x / W * 11) * H * 0.012);
    g.lineTo(W, HZ); g.fill();
    // temple rising above the far canopy
    var tw = Math.min(W * 0.38, H * 0.26);
    temple(g, W * 0.3, HZ + H * 0.05, tw, P);
    drawCanopy(g, canopies[0], P.far);
    // mist
    for (i = 0; i < mists.length; i++){ var m = mists[i]; m.x += m.v * dt; if (m.x > W + m.w) m.x = -m.w;
      var mg = g.createRadialGradient(m.x, m.y, 0, m.x, m.y, m.w / 2); mg.addColorStop(0, 'rgba(' + P.mist + ',.28)'); mg.addColorStop(1, 'rgba(' + P.mist + ',0)');
      g.fillStyle = mg; g.fillRect(m.x - m.w / 2, m.y - m.w / 4, m.w, m.w / 2); }
    drawCanopy(g, canopies[1], P.mid);
    // river
    var ry = H * 0.8; g.fillStyle = rgb(P.river, 0.85);
    g.beginPath(); g.moveTo(0, ry); for (x = 0; x <= W; x += 10) g.lineTo(x, ry + Math.sin(x / W * 3 + T * 0.2) * 3); g.lineTo(W, ry + H * 0.04); g.lineTo(0, ry + H * 0.04); g.fill();
    drawCanopy(g, canopies[2], P.near);
    // macaws
    for (i = 0; i < birds.length; i++){
      var b = birds[i]; b.x += b.v * dt; if (b.x > W + 40) b.x = -40;
      var y = b.y + Math.sin(T * 0.8 + b.p) * 10, f = Math.sin(T * 7 + b.p) * 6;
      g.strokeStyle = P.bird[b.c]; g.lineWidth = 2.4; g.lineCap = 'round';
      g.beginPath(); g.moveTo(b.x - 12, y - f); g.quadraticCurveTo(b.x - 4, y - 3, b.x, y); g.quadraticCurveTo(b.x + 4, y - 3, b.x + 12, y - f); g.stroke();
      g.beginPath(); g.moveTo(b.x, y); g.lineTo(b.x - 16, y + 3); g.stroke();     // long tail
    }
    // fireflies
    for (i = 0; i < flies.length; i++){ var fl = flies[i]; fl.x += Math.sin(T * 0.6 + fl.p) * 0.4; fl.y += Math.cos(T * 0.5 + fl.p) * 0.3;
      g.fillStyle = 'rgba(' + P.fly + ',' + (curTheme === 'dark' ? 0.5 + 0.5 * Math.sin(T * 2 + fl.p) : 0.25 * (0.5 + 0.5 * Math.sin(T * 2 + fl.p))) + ')';
      g.beginPath(); g.arc(fl.x, fl.y, fl.s, 0, 6.283); g.fill(); }
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
