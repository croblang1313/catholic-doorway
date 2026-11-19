/* Catholic Terms filters and the visual guides (church plan, vestments). No dependencies. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var norm = function (s) { return (s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); };
  var wide = function () { return window.matchMedia('(min-width: 900px)').matches; };

  /* ---------- Catholic Terms: search + theme chips ---------- */
  var gl = $('#glossary');
  if (gl && $('.term-cats')) {
    var q = $('#gloss-search'), empty = $('#gloss-empty'), chips = $$('.term-cats .chip'), cat = '';
    var apply = function () {
      var term = norm(q.value), any = false;
      $$('dt', gl).forEach(function (dt) {
        var dd = dt.nextElementSibling;
        var okCat = !cat || (' ' + dt.getAttribute('data-cats') + ' ').indexOf(' ' + cat + ' ') > -1;
        var okText = !term || norm(dt.textContent + ' ' + dd.querySelector('p').textContent).indexOf(term) > -1;
        var ok = okCat && okText;
        dt.hidden = dd.hidden = !ok;
        if (ok) any = true;
      });
      $$('.letter-head', gl).forEach(function (h) {
        var el = h.nextElementSibling, vis = false;
        while (el && !el.classList.contains('letter-head')) { if (el.tagName === 'DT' && !el.hidden) vis = true; el = el.nextElementSibling; }
        h.hidden = !vis;
      });
      $$('.alpha a').forEach(function (a) {
        var h = document.getElementById(a.getAttribute('href').slice(1));
        a.classList.toggle('off', !!(h && h.hidden));
      });
      empty.hidden = any;
    };
    var setCat = function (c, scroll) {
      cat = c;
      chips.forEach(function (o) { o.setAttribute('aria-pressed', o.getAttribute('data-cat') === c ? 'true' : 'false'); });
      apply();
      try { history.replaceState(null, '', c ? '#theme-' + c : location.pathname); } catch (e) {}
      if (scroll) $('.term-cats').scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    chips.forEach(function (ch) { ch.addEventListener('click', function () { setCat(ch.getAttribute('data-cat')); }); });
    $$('.tag', gl).forEach(function (t) { t.addEventListener('click', function () { setCat(t.getAttribute('data-cat'), true); }); });
    q.addEventListener('input', apply);
    // A link to a term hidden by a filter clears the filters first
    var reveal = function () {
      var id = location.hash.slice(1);
      if (id.indexOf('theme-') === 0) { setCat(id.slice(6)); return; }
      var dt = id && document.getElementById(id);
      if (dt && dt.tagName === 'DT' && dt.hidden) {
        q.value = '';
        cat = '';
        chips.forEach(function (o) { o.setAttribute('aria-pressed', o.getAttribute('data-cat') === '' ? 'true' : 'false'); });
        apply();
        dt.scrollIntoView();
      }
    };
    gl.addEventListener('click', function (ev) {
      var a = ev.target.closest('a[href^="#"]');
      if (!a) return;
      var dt = document.getElementById(a.getAttribute('href').slice(1));
      if (dt && dt.hidden) { setTimeout(reveal, 0); }
    });
    window.addEventListener('hashchange', reveal);
    reveal();
  }

  /* ---------- Anatomy of a Catholic Church ---------- */
  var plan = $('.church-plan');
  if (plan) {
    var info = $('#plan-info'), hots = $$('.hot', plan), items = $$('.an-steps li');
    var pick = function (k, fromList) {
      hots.forEach(function (h) { h.classList.toggle('on', h.getAttribute('data-k') === k); });
      items.forEach(function (li) { li.classList.toggle('on', li.getAttribute('data-k') === k); });
      var li = document.getElementById(k);
      if (!li) return;
      var s = document.createElement('strong'), p = document.createElement('span');
      s.textContent = $('.an-no', li).textContent + '. ' + $('strong', li).textContent;
      p.textContent = $('.an-def', li).textContent;
      info.innerHTML = '';
      info.appendChild(s);
      info.appendChild(p);
      var pray = $('.an-pray', li);
      if (pray) { var pl = pray.cloneNode(true); pl.style.display = 'block'; pl.style.marginTop = '.4rem'; info.appendChild(pl); }
      if (!fromList && wide()) li.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    };
    hots.forEach(function (h) {
      h.addEventListener('click', function () { pick(h.getAttribute('data-k')); });
      h.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); pick(h.getAttribute('data-k')); }
      });
    });
    items.forEach(function (li) {
      $('.an-item', li).addEventListener('click', function () {
        pick(li.getAttribute('data-k'), true);
        if (!wide()) plan.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
    var start = location.hash.slice(1);
    if (start && $('.hot[data-k="' + start + '"]', plan)) pick(start, true);
  }

  /* ---------- What Priests & Deacons Wear ---------- */
  var dress = $('.dress-fig');
  if (dress) {
    var lb = $$('button[data-layer]'), texts = $$('.layer-text');
    lb.forEach(function (b) {
      b.addEventListener('click', function () {
        var n = b.getAttribute('data-layer');
        dress.setAttribute('data-layer', n);
        lb.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        texts.forEach(function (t) { t.hidden = t.getAttribute('data-layer') !== n; });
      });
    });
    var sw = $$('.swatch');
    var setColor = function (c) {
      $$('.vest-fig').forEach(function (f) { f.setAttribute('data-color', c); });
      sw.forEach(function (o) { o.setAttribute('aria-pressed', o.getAttribute('data-color') === c ? 'true' : 'false'); });
    };
    sw.forEach(function (b) { b.addEventListener('click', function () { setColor(b.getAttribute('data-color')); }); });
    $$('.year-wheel .seg').forEach(function (s) {
      s.addEventListener('click', function () { setColor(s.getAttribute('data-c')); dress.scrollIntoView({ behavior: 'smooth', block: 'center' }); });
    });
    setColor('green');
  }
})();
