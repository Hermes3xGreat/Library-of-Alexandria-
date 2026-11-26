/* Egyptian Scroll — animated background: the Nile at Giza. Pyramids on the
   desert edge, dunes, palms along the river, a felucca drifting downstream,
   ibises crossing the sky; the sun low over the west by day, the moon and the
   stars of Nut by night. Same window.__hvLib3D / hvSetLib3D interface. */
(function(){
  if (window.__hvLib3D) return;
  var ID = 'hv-lib3d';
  var PAL = {
    light: { sky:['#f3e3c0','#f0cf98','#e9b679'], disc:'#e8892c', glow:'240,170,80', far:[214,176,124], mid:[196,150,96], near:[170,120,70], pyr:[201,160,104], pyrShade:[160,118,70], river:[70,128,140], riverHi:'255,236,190', palm:[62,70,44], boat:[70,52,36], sail:'244,234,210', bird:'rgba(40,36,30,.6)', mote:'230,190,120', stars:0 },
    sepia: { sky:['#eadcbc','#e2c896','#d6ac74'], disc:'#c9772e', glow:'214,150,80', far:[200,170,128], mid:[184,148,102], near:[158,120,78], pyr:[190,154,106], pyrShade:[148,112,72], river:[96,120,118], riverHi:'250,228,184', palm:[74,66,44], boat:[74,56,38], sail:'238,226,200', bird:'rgba(60,46,32,.55)', mote:'214,170,110', stars:0 },
    dark:  { sky:['#060a18','#0d1630','#1d2a4a'], disc:'#ece6cf', glow:'210,220,255', far:[38,40,62], mid:[30,30,48], near:[20,20,32], pyr:[54,54,80], pyrShade:[32,32,52], river:[26,44,72], riverHi:'210,220,255', palm:[10,12,18], boat:[12,12,18], sail:'200,205,225', bird:'rgba(200,205,225,.35)', mote:'200,210,255', stars:1 }
  };
  function theme(){ var t = document.documentElement.getAttribute('data-theme'); return (t === 'dark' || t === 'sepia') ? t : 'light'; }
  function rnd(seed){ var s = seed >>> 0; return function(){ s = (s + 0x6D2B79F5) | 0; var t = Math.imul(s ^ (s >>> 15), 1 | s); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function rgb(c, a){ return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a == null ? 1 : a) + ')'; }
  var cv, cx, veil, W = 0, H = 0, DPR = 1, running = false, raf = 0, last = 0, T = 0, boost = 0, curTheme = '', frames = 0;
  var stars = [], motes = [], birds = [], palms = [], dunes = [], boat = { x: 0 }, HZ = 0, RIV = 0;

  function duneLine(seed, base, amp){
    var r = rnd(seed), k = [], i; for (i = 1; i <= 5; i++) k.push({ f: i * (0.6 + r() * 0.8), a: amp / i * (0.6 + r() * 0.8), p: r() * 6.283 });
    return function(x){ var y = 0; for (var j = 0; j < k.length; j++) y += Math.sin(x / W * 6.283 * k[j].f + k[j].p) * k[j].a; return base + y; };
  }
  function build(){
    curTheme = theme();
    DPR = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    HZ = H * 0.58; RIV = H * 0.74;
    var r = rnd(1907), i;
    stars = []; for (i = 0; i < Math.min(220, W * H / 2500); i++) stars.push({ x: r() * W, y: r() * HZ * 0.95, s: r() * 1.4 + 0.3, p: r() * 6.283 });
    motes = []; for (i = 0; i < Math.min(70, W * H / 12000); i++) motes.push({ x: r() * W, y: HZ + r() * (H - HZ), v: 6 + r() * 14, s: 0.5 + r() * 1.2, p: r() * 6.283 });
    birds = []; for (i = 0; i < 5; i++) birds.push({ x: r() * W, y: H * (0.16 + r() * 0.22), v: 14 + r() * 10, s: 0.8 + r() * 0.5, p: r() * 6.283 });
    palms = []; for (i = 0; i < Math.max(6, Math.round(W / 70)); i++) palms.push({ x: r() * W, h: H * (0.09 + r() * 0.07), lean: (r() - 0.5) * 0.35, p: r() * 6.283, back: r() < 0.5 });
    palms.sort(function(a, b){ return (a.back ? 0 : 1) - (b.back ? 0 : 1); });
    dunes = [duneLine(11, HZ + H * 0.015, H * 0.012), duneLine(23, HZ + H * 0.06, H * 0.02), duneLine(37, H * 0.86, H * 0.025)];
    boat.x = W * 0.3;
  }
  function pyramid(g, cx0, base, w, P){
    var h = w * 0.62;
    g.fillStyle = rgb(P.pyr); g.beginPath(); g.moveTo(cx0 - w / 2, base); g.lineTo(cx0, base - h); g.lineTo(cx0 + w * 0.18, base); g.closePath(); g.fill();
    g.fillStyle = rgb(P.pyrShade); g.beginPath(); g.moveTo(cx0 + w * 0.18, base); g.lineTo(cx0, base - h); g.lineTo(cx0 + w / 2, base); g.closePath(); g.fill();
  }
  function palm(g, x, y, h, lean, sway, col){
    g.strokeStyle = rgb(col); g.fillStyle = rgb(col); g.lineCap = 'round';
    var tx = x + lean * h + sway * h * 0.04, ty = y - h;
    g.lineWidth = Math.max(1.5, h * 0.045);
    g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + lean * h * 0.3, y - h * 0.5, tx, ty); g.stroke();
    g.lineWidth = Math.max(1, h * 0.03);
    for (var i = 0; i < 8; i++){
      var a = -Math.PI / 2 + (i - 3.5) * 0.42 + sway * 0.05, len = h * (0.42 + (i % 2) * 0.1);
      var ex = tx + Math.cos(a) * len, ey = ty + Math.sin(a) * len * 0.55 + len * 0.35;
      g.beginPath(); g.moveTo(tx, ty); g.quadraticCurveTo(tx + Math.cos(a) * len * 0.5, ty + Math.sin(a) * len * 0.5 - len * 0.1, ex, ey); g.stroke();
    }
  }
  function draw(dt){
    var P = PAL[curTheme], g = cx, i, x;
    var sky = g.createLinearGradient(0, 0, 0, HZ);
    sky.addColorStop(0, P.sky[0]); sky.addColorStop(0.6, P.sky[1]); sky.addColorStop(1, P.sky[2]);
    g.fillStyle = sky; g.fillRect(0, 0, W, H);
    if (P.stars){ for (i = 0; i < stars.length; i++){ var st = stars[i]; g.fillStyle = 'rgba(235,240,255,' + (0.35 + 0.45 * Math.sin(T * 1.2 + st.p) * 0.5 + 0.25) + ')'; g.fillRect(st.x, st.y, st.s, st.s); } }
    // sun (moon at night), low in the west, its glow on the haze
    var sx = W * 0.8, sy = H * 0.2 + Math.sin(T * 0.05) * 3, sr = Math.min(W, H) * 0.05;
    var gl = g.createRadialGradient(sx, sy, 0, sx, sy, sr * 6);
    gl.addColorStop(0, 'rgba(' + P.glow + ',.55)'); gl.addColorStop(1, 'rgba(' + P.glow + ',0)');
    g.fillStyle = gl; g.fillRect(sx - sr * 6, sy - sr * 6, sr * 12, sr * 12);
    g.fillStyle = P.disc; g.beginPath(); g.arc(sx, sy, sr, 0, 6.283); g.fill();
    // far dunes and the three pyramids
    g.fillStyle = rgb(P.far); g.beginPath(); g.moveTo(0, H); for (x = 0; x <= W; x += 8) g.lineTo(x, dunes[0](x)); g.lineTo(W, H); g.fill();
    var pw = Math.min(W * 0.46, H * 0.3), base = dunes[0](W * 0.3) + 2;
    pyramid(g, W * 0.16, base + 3, pw * 0.6, P); pyramid(g, W * 0.36, base, pw, P); pyramid(g, W * 0.58, base + 4, pw * 0.78, P);
    g.fillStyle = rgb(P.mid); g.beginPath(); g.moveTo(0, H); for (x = 0; x <= W; x += 8) g.lineTo(x, dunes[1](x)); g.lineTo(W, H); g.fill();
    // the river with moving light
    var ry0 = RIV - H * 0.035, ry1 = RIV + H * 0.035;
    var rv = g.createLinearGradient(0, ry0, 0, ry1); rv.addColorStop(0, rgb(P.river, 0.95)); rv.addColorStop(1, rgb(P.river, 0.75));
    g.fillStyle = rv; g.beginPath(); g.moveTo(0, ry0); for (x = 0; x <= W; x += 10) g.lineTo(x, ry0 + Math.sin(x / W * 4 + 1) * 4); for (x = W; x >= 0; x -= 10) g.lineTo(x, ry1 + Math.sin(x / W * 3) * 5); g.closePath(); g.fill();
    for (i = 0; i < 26; i++){
      var lx = (i * 97 + T * 18) % (W + 80) - 40, ly = ry0 + 6 + (i * 37 % 100) / 100 * (ry1 - ry0 - 10);
      var near = Math.abs(lx - sx) < W * 0.25 ? 0.6 : 0.25;
      g.strokeStyle = 'rgba(' + P.riverHi + ',' + (near * (0.5 + 0.5 * Math.sin(T * 2 + i))) + ')'; g.lineWidth = 1.2;
      g.beginPath(); g.moveTo(lx, ly); g.lineTo(lx + 14 + (i % 3) * 8, ly); g.stroke();
    }
    // felucca drifting downstream
    boat.x += dt * (9 + boost * 30); if (boat.x > W + 60) boat.x = -60;
    var bx = boat.x, by = RIV + Math.sin(T * 1.4) * 1.5, bs = Math.min(W, H) * 0.0016 + 0.5;
    g.fillStyle = rgb(P.boat); g.beginPath(); g.moveTo(bx - 26 * bs, by - 4 * bs); g.quadraticCurveTo(bx, by + 6 * bs, bx + 26 * bs, by - 6 * bs); g.lineTo(bx - 26 * bs, by - 4 * bs); g.fill();
    g.fillRect(bx - 1 * bs, by - 52 * bs, 2 * bs, 48 * bs);
    g.fillStyle = 'rgba(' + P.sail + ',.95)'; g.beginPath(); g.moveTo(bx + 1 * bs, by - 50 * bs); g.lineTo(bx + 24 * bs, by - 8 * bs); g.lineTo(bx - 18 * bs, by - 10 * bs); g.closePath(); g.fill();
    // palms on both banks
    for (i = 0; i < palms.length; i++){
      var pm = palms[i], py = pm.back ? ry0 - 2 : ry1 + H * 0.02;
      palm(g, pm.x, py, pm.back ? pm.h * 0.8 : pm.h, pm.lean, Math.sin(T * 0.8 + pm.p), pm.back ? P.mid.map(function(c, k){ return Math.round((c + P.palm[k]) / 2); }) : P.palm);
    }
    // near desert
    g.fillStyle = rgb(P.near); g.beginPath(); g.moveTo(0, H); for (x = 0; x <= W; x += 8) g.lineTo(x, Math.max(ry1 + H * 0.03, dunes[2](x))); g.lineTo(W, H); g.fill();
    // ibises
    g.strokeStyle = P.bird; g.lineWidth = 1.4;
    for (i = 0; i < birds.length; i++){
      var b = birds[i]; b.x += b.v * dt; if (b.x > W + 30){ b.x = -30; }
      var f = Math.sin(T * 5 + b.p) * 4 * b.s, bxx = b.x, byy = b.y + Math.sin(T * 0.7 + b.p) * 6;
      g.beginPath(); g.moveTo(bxx - 9 * b.s, byy - f); g.quadraticCurveTo(bxx - 3 * b.s, byy - 2, bxx, byy); g.quadraticCurveTo(bxx + 3 * b.s, byy - 2, bxx + 9 * b.s, byy - f); g.stroke();
      g.beginPath(); g.moveTo(bxx, byy); g.lineTo(bxx + 7 * b.s, byy + 2 * b.s); g.stroke();
    }
    // drifting sand
    for (i = 0; i < motes.length; i++){
      var m = motes[i]; m.x += m.v * dt; m.y += Math.sin(T + m.p) * 0.1; if (m.x > W + 4) m.x = -4;
      g.fillStyle = 'rgba(' + P.mote + ',' + (0.25 + 0.3 * (0.5 + 0.5 * Math.sin(T * 1.7 + m.p))) + ')';
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
