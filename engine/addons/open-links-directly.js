/* The tap-to-start screen stays. It is skipped only when the app is opened straight
   into a work (a search result or a link), so the reader is not hidden behind it. */
(function(){
  if (!/^#\/read\//.test(location.hash || '')) return;
  function skip(){ var e = document.documentElement; if (e.classList.contains('hv-intro')){ e.classList.remove('hv-intro'); e.classList.add('hv-lib3d-on'); var t = document.getElementById('hv-intro-title'); if (t) t.style.display = 'none'; } }
  skip(); document.addEventListener('DOMContentLoaded', skip);
})();
