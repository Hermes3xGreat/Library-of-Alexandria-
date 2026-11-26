/* An author with a single work opens that work straight away, instead of
   stopping at an author page that lists only one title. */
(function(){
  function books(){ try { return JSON.parse(document.getElementById('hermes-manifest').textContent).books || []; } catch (e) { return []; } }
  var cache = null;
  function only(author){
    if (!cache){ cache = {}; books().forEach(function(b){ var m = b.meta || {}; if (!m.author || m.hidden) return; (cache[m.author] = cache[m.author] || []).push(m.key); }); }
    var ks = cache[author]; if (!ks || !ks.length) return null;
    // other translations and original-language texts of the same work share its key stem
    var stem = function(k){ return k.replace(/-(b|c|e|gr|[a-h])$/, ''); }, first = stem(ks[0]);
    for (var i = 1; i < ks.length; i++) if (stem(ks[i]) !== first) return null;
    return ks[0];
  }
  function go(e){
    var t = e.target && e.target.closest ? e.target.closest('.hv-author-chip[data-author-group]') : null; if (!t) return;
    if (e.type === 'keydown' && e.key !== 'Enter' && e.key !== ' ') return;
    var key = only(t.getAttribute('data-author-group')); if (!key) return;
    e.preventDefault(); e.stopImmediatePropagation();
    location.hash = '#/read/' + encodeURIComponent(key);
  }
  window.addEventListener('click', go, true); window.addEventListener('keydown', go, true);
})();
