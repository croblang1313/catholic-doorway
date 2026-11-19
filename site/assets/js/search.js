/* CatholicDoorway site search. Index: /data/search-<lang>.json, built with the site.
   Each row is [title, url, snippet, page title]. */
(function () {
  'use strict';
  var LG = document.documentElement.lang, input = document.getElementById('site-q'), out = document.getElementById('search-results'), count = document.getElementById('search-count');
  if (!input || !out) return;
  var W = {
    en: { n1: ' result', n: ' results', none: 'Nothing found. Try a shorter or different word, or browse the menu.', on: 'on ', load: 'Loading…', hint: 'Type a word or two, for example “confession”, “Memorare” or “godparent”.' },
    es: { n1: ' resultado', n: ' resultados', none: 'No encontramos nada. Prueba con una palabra más corta o distinta, o usa el menú.', on: 'en ', load: 'Cargando…', hint: 'Escribe una o dos palabras, por ejemplo «confesión», «Acordaos» o «padrino».' },
    pt: { n1: ' resultado', n: ' resultados', none: 'Nada encontrado. Tente uma palavra mais curta ou diferente, ou use o menu.', on: 'em ', load: 'Carregando…', hint: 'Digite uma ou duas palavras, por exemplo “confissão”, “Lembrai-vos” ou “padrinho”.' },
    tl: { n1: ' resulta', n: ' resulta', none: 'Walang nakita. Subukan ang mas maikli o ibang salita, o gamitin ang menu.', on: 'sa ', load: 'Naglo-load…', hint: 'Mag-type ng isa o dalawang salita, halimbawa “kumpisal”, “rosaryo” o “ninong”.' }
  }[LG] || null;
  if (!W) return;
  var rows = null, STOP = {};
  ('the of and a an to in on for is are do does i my me how what why can at by or ' +
   'el la los las de del y en un una que es por para como mi se ' +
   'o os as do da dos das e um uma em no na que por para como meu ' +
   'ang ng sa mga at na ay si ni ko ako paano ano bakit').split(' ').forEach(function (w) { STOP[w] = 1; });
  function fold(s) { return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[‘’]/g, "'"); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(s, words) {
    var f = fold(s), hits = [];
    words.forEach(function (w) { var i = 0; while ((i = f.indexOf(w, i)) >= 0) { hits.push([i, i + w.length]); i += w.length; } });
    if (!hits.length) return esc(s);
    hits.sort(function (a, b) { return a[0] - b[0]; });
    var res = '', at = 0;
    hits.forEach(function (h) { if (h[0] < at) return; res += esc(s.slice(at, h[0])) + '<mark>' + esc(s.slice(h[0], h[1])) + '</mark>'; at = h[1]; });
    return res + esc(s.slice(at));
  }
  function score(r, words, phrase) {
    var t = r._t, b = r._b, total = 0, hit = 0;
    for (var i = 0; i < words.length; i++) {
      var w = words[i], s = 0, re = new RegExp('(^|[^a-z0-9])' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
      if (re.test(t)) s += 10; else if (t.indexOf(w) >= 0) s += 6;
      if (re.test(b)) s += 2; else if (b.indexOf(w) >= 0) s += 1;
      if (s) hit++;
      total += s;
    }
    // Every word must match, except in longer searches, where most of them will do.
    if (hit < (words.length <= 2 ? words.length : Math.ceil(words.length * 0.6))) return 0;
    total += hit * 4;
    if (words.length > 1 && t.indexOf(phrase) >= 0) total += 8;
    if (t === phrase) total += 12;
    if (r[1].indexOf('#') < 0) total += 3;
    if (/\/(dioceses|diocesis|mga-diyosesis)\//.test(r[1])) total -= 2;
    return total;
  }
  function run() {
    var q = input.value.trim();
    try { history.replaceState(null, '', q ? '?q=' + encodeURIComponent(q) : location.pathname); } catch (e) {}
    if (!q) { out.innerHTML = ''; count.textContent = W.hint; return; }
    if (!rows) { count.textContent = W.load; return; }
    var phrase = fold(q).replace(/\s+/g, ' ').trim();
    var words = phrase.split(' ').filter(function (w) { return (w.length > 1 || /\d/.test(w)) && !STOP[w]; });
    if (!words.length) words = [phrase];
    var res = [];
    rows.forEach(function (r) { var s = score(r, words, phrase); if (s) res.push([s, r]); });
    res.sort(function (a, b) { return b[0] - a[0]; });
    count.textContent = res.length + (res.length === 1 ? W.n1 : W.n);
    if (!res.length) { out.innerHTML = '<p class="muted">' + esc(W.none) + '</p>'; return; }
    out.innerHTML = res.slice(0, 40).map(function (x) {
      var r = x[1];
      return '<li><a href="' + esc(r[1]) + '">' + mark(r[0], words) + '</a>' + (r[3] ? '<span class="sr-page"> ' + esc(W.on) + esc(r[3]) + '</span>' : '') +
        (r[2] ? '<p>' + mark(r[2], words) + '</p>' : '') + '</li>';
    }).join('');
  }
  var timer;
  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 120); });
  document.getElementById('site-search').addEventListener('submit', function (e) { e.preventDefault(); run(); });
  var q0 = new URLSearchParams(location.search).get('q');
  if (q0) input.value = q0;
  run();
  fetch('/data/search-' + LG + '.json').then(function (r) { return r.json(); }).then(function (d) {
    rows = d.map(function (r) { r._t = fold(r[0]); r._b = fold(r[2] + ' ' + r[3]); return r; });
    run();
  }).catch(function () { count.textContent = ''; });
})();
