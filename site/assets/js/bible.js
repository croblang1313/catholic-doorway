/* CatholicDoorway Bible reader: the Douay-Rheims Bible (Challoner revision, public domain).
   Data: /data/bible/drb/books.json and one JSON file per book (chapters -> verses). */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var BASE = '/data/bible/drb/';
  var book = $('bible-book'), chap = $('bible-chapter'), ref = $('bible-ref'), msg = $('bible-msg');
  var title = $('bible-title'), douay = $('bible-douay'), text = $('bible-text');
  if (!book) return;
  var books = [], cache = {}, cur = { b: 0, c: 1, v1: 0, v2: 0 };

  function norm(s) { return String(s || '').toLowerCase().replace(/\bfirst\b|\bi\b(?=\s*[a-z])/g, '1').replace(/\bsecond\b|\bii\b/g, '2').replace(/\bthird\b|\biii\b/g, '3').replace(/\biv\b/g, '4').replace(/[^a-z0-9]/g, ''); }
  var ALIAS = { jn: 'john', mt: 'matt', mk: 'mark', lk: 'luke', gn: 'gen', ex: 'exod', is: 'isa', psalm: 'ps', psalms: 'ps', psa: 'ps', canticles: 'song', canticleofcanticles: 'song', songofsolomon: 'song', ecclesiasticus: 'sir', apocalypse: 'rev', revelations: 'rev', apoc: 'rev' };
  function findBook(q) {
    q = norm(q); if (!q) return null;
    if (ALIAS[q]) q = ALIAS[q];
    var exact = books.filter(function (b) { return norm(b.name) === q || norm(b.douay) === q || b.code === q; });
    if (exact.length) return exact[0];
    var pre = books.filter(function (b) { return norm(b.name).indexOf(q) === 0 || b.code.indexOf(q) === 0; });
    if (pre.length) return pre[0];
    var dpre = books.filter(function (b) { return b.douay && norm(b.douay).indexOf(q) === 0; });
    return dpre[0] || null;
  }
  // "John 3:16-18", "1 Cor 13", "Psalm 22", "jn 3 16", "Gen 1-3", "Matt 5:27-6:4"
  function parse(s) {
    s = String(s || '');
    var m = /^\s*(.*?[A-Za-z])\s*(\d+)\s*[:.]\s*(\d+)\s*[-–]\s*(\d+)\s*[:.]\s*(\d+)\s*$/.exec(s);
    if (m) { var bk0 = findBook(m[1]); return bk0 ? { b: bk0.n, c: +m[2], v1: +m[3], c2: +m[4], v2: +m[5] } : null; }
    m = /^\s*(.*?[A-Za-z])\s*(\d+)\s*[-–]\s*(\d+)\s*$/.exec(s);
    if (m) { var bk1 = findBook(m[1]); return bk1 ? { b: bk1.n, c: +m[2], c2: Math.max(+m[2], +m[3]), v1: 0, v2: 0 } : null; }
    m = /^\s*(.+?)\s*(\d+)(?:\s*[:.\s]\s*(\d+)(?:\s*[-–]\s*(\d+))?)?\s*$/.exec(s);
    if (!m) { var only = findBook(s); return only ? { b: only.n, c: 1 } : null; }
    var bk = findBook(m[1]);
    if (!bk) return null;
    return { b: bk.n, c: +m[2], v1: m[3] ? +m[3] : 0, v2: m[4] ? +m[4] : (m[3] ? +m[3] : 0) };
  }
  function label(b) { return b.name + (b.douay ? ' (' + b.douay + ')' : ''); }
  function load(n) {
    if (!cache[n]) cache[n] = fetch(BASE + n + '.json').then(function (r) { if (!r.ok) throw 0; return r.json(); });
    return cache[n];
  }
  function fillChapters(b) {
    var n = books[b - 1].chapters, h = '';
    for (var i = 1; i <= n; i++) h += '<option value="' + i + '">' + i + '</option>';
    chap.innerHTML = h;
  }
  function show(p, push) {
    var b = books[p.b - 1]; if (!b) return;
    $('bible-prev').hidden = $('bible-next').hidden = false;
    var c = Math.min(Math.max(1, p.c || 1), b.chapters);
    cur = { b: p.b, c: c, v1: p.v1 || 0, v2: p.v2 || 0 };
    book.value = String(p.b); fillChapters(p.b); chap.value = String(c);
    title.textContent = (b.n === 21 ? 'Psalm ' : b.name + ' ') + c;
    douay.textContent = b.douay ? 'Called ' + b.douay + ' in the Douay-Rheims.' : (b.n === 21 ? 'Douay-Rheims numbering: usually one lower than modern Bibles from Psalm 10 to 147.' : '');
    text.innerHTML = '<p class="muted">Loading&hellip;</p>';
    load(b.n).then(function (chs) {
      var vs = chs[c - 1] || [];
      text.innerHTML = vs.map(function (t, i) {
        var n = i + 1, hl = cur.v1 && n >= cur.v1 && n <= cur.v2;
        return '<p id="v' + n + '"' + (hl ? ' class="hl"' : '') + '><a class="vn" href="?ref=' + b.code + '+' + c + ':' + n + '" aria-label="Verse ' + n + '">' + n + '</a> ' + t.replace(/&/g, '&amp;').replace(/</g, '&lt;') + '</p>';
      }).join('');
      var url = '?ref=' + b.code + '+' + c + (cur.v1 ? ':' + cur.v1 + (cur.v2 > cur.v1 ? '-' + cur.v2 : '') : '');
      try { history[push ? 'pushState' : 'replaceState'](cur, '', url); } catch (e) {}
      document.title = title.textContent + ' (Douay-Rheims) | CatholicDoorway';
      if (cur.v1) { var el = $('v' + cur.v1); if (el) el.scrollIntoView({ block: 'center' }); }
      $('bible-prev').disabled = b.n === 1 && c === 1;
      $('bible-next').disabled = b.n === books.length && c === b.chapters;
    }).catch(function () { text.innerHTML = '<p>This chapter could not load. Please check your connection and try again.</p>'; });
  }
  function step(d) {
    var b = cur.b, c = cur.c + d;
    if (c < 1) { b -= 1; if (b < 1) return; c = books[b - 1].chapters; }
    else if (c > books[b - 1].chapters) { b += 1; if (b > books.length) return; c = 1; }
    show({ b: b, c: c }, true);
    title.scrollIntoView({ behavior: 'smooth' });
  }
  function go() {
    var p = parse(ref.value);
    if (!p) { msg.textContent = 'We could not find that passage. Try a book name and chapter, such as “Mark 1” or “John 3:16”.'; msg.classList.add('error'); return; }
    msg.textContent = ''; msg.classList.remove('error');
    if (p.c > books[p.b - 1].chapters) { msg.textContent = books[p.b - 1].name + ' has ' + books[p.b - 1].chapters + ' chapters.'; p.c = books[p.b - 1].chapters; }
    if (p.c2 && p.c2 > p.c) { var b = books[p.b - 1]; try { history.pushState(null, '', '?ref=' + b.code + '+' + p.c + (p.v1 ? ':' + p.v1 : '') + '-' + p.c2 + (p.v2 ? ':' + p.v2 : '')); } catch (e) {} showPassages([p], b.code + ' ' + p.c + (p.v1 ? ':' + p.v1 : '') + '-' + p.c2 + (p.v2 ? ':' + p.v2 : '')); return; }
    show(p, true);
  }

  /* Passage mode: one or more ranges, e.g. ?ref=gen+1-3;matt+5:1-23;ps+1 (used by the reading plans) */
  function esc(t) { return t.replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function refName(b, c) { return (b.n === 21 ? 'Psalm ' : b.name + ' ') + c; }
  function showPassages(ps, raw) {
    $('bible-prev').hidden = $('bible-next').hidden = true;
    var first = books[ps[0].b - 1];
    book.value = String(first.n); fillChapters(first.n); chap.value = String(ps[0].c);
    title.textContent = raw.replace(/\+/g, ' ').split(';').map(function (r) {
      var p = parse(r), b = p && books[p.b - 1]; if (!b) return r;
      return r.replace(/^\s*\S+\s*/, (b.n === 21 ? (p.c2 > p.c ? 'Psalms ' : 'Psalm ') : b.name + ' ')).replace(/-/g, '–');
    }).join(' · ');
    douay.textContent = ps.some(function (p) { return p.b === 21; }) ? 'Douay-Rheims numbering: psalms are usually one lower than modern Bibles from Psalm 10 to 147.' : '';
    text.innerHTML = '<p class="muted">Loading&hellip;</p>';
    Promise.all(ps.map(function (p) { return load(p.b); })).then(function (all) {
      var h = '';
      ps.forEach(function (p, i) {
        var b = books[p.b - 1], chs = all[i], c2 = Math.min(p.c2 || p.c, b.chapters);
        for (var c = p.c; c <= c2; c++) {
          var vs = chs[c - 1] || [], from = (c === p.c && p.v1) ? p.v1 : 1, to = (c === c2 && p.v2) ? p.v2 : vs.length;
          h += '<h3 class="bible-ch"><a href="?ref=' + b.code + '+' + c + '">' + refName(b, c) + (from > 1 || to < vs.length ? ':' + from + '–' + to : '') + '</a></h3>';
          for (var n = from; n <= to && n <= vs.length; n++) h += '<p id="v' + b.code + c + '-' + n + '"><span class="vn">' + n + '</span> ' + esc(vs[n - 1]) + '</p>';
        }
      });
      text.innerHTML = h;
      document.title = title.textContent + ' (Douay-Rheims) | CatholicDoorway';
    }).catch(function () { text.innerHTML = '<p>This passage could not load. Please check your connection and try again.</p>'; });
  }

  /* Reading plan bar: ?plan=bible&day=12 (&lang=es) */
  var PLAN_T = {
    en: { bible: 'Bible in a Year', catechism: 'Catechism in a Year', gospels: 'The Gospels in 30 Days', ocia: 'OCIA in 90 Days', day: 'Day', of: 'of', mark: 'Mark as read', done: 'Read ✓', back: 'Back to my reading plan', url: '/reading-plans' },
    es: { bible: 'La Biblia en un año', catechism: 'El Catecismo en un año', gospels: 'Los Evangelios en 30 días', ocia: 'OCIA en 90 días', day: 'Día', of: 'de', mark: 'Marcar como leído', done: 'Leído ✓', back: 'Volver a mi plan de lectura', url: '/es/planes-de-lectura' },
    pt: { bible: 'A Bíblia em um ano', catechism: 'O Catecismo em um ano', gospels: 'Os Evangelhos em 30 dias', ocia: 'OCIA em 90 dias', day: 'Dia', of: 'de', mark: 'Marcar como lido', done: 'Lido ✓', back: 'Voltar ao meu plano de leitura', url: '/pt/planos-de-leitura' },
    tl: { bible: 'Ang Bibliya sa isang taon', catechism: 'Ang Katesismo sa isang taon', gospels: 'Ang mga Ebanghelyo sa 30 araw', ocia: 'OCIA sa 90 araw', day: 'Araw', of: 'sa', mark: 'Markahang nabasa', done: 'Nabasa ✓', back: 'Bumalik sa aking plano sa pagbasa', url: '/tl/mga-plano-sa-pagbasa' }
  };
  var PLAN_LEN = { bible: 365, catechism: 365, gospels: 30, ocia: 90 };
  function planBar() {
    var qs = new URLSearchParams(location.search), id = qs.get('plan'), day = parseInt(qs.get('day'), 10);
    if (!PLAN_LEN[id] || !(day >= 1 && day <= PLAN_LEN[id])) return;
    var L = PLAN_T[qs.get('lang')] || PLAN_T.en, KEY = 'cd-plans';
    var read = function () { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } };
    var bars = [];
    var paint = function () {
      var st = read(), p = st.plans && st.plans[id], on = !!(p && p.done && p.done.indexOf(day) >= 0);
      bars.forEach(function (btn) { btn.textContent = on ? L.done : L.mark; btn.setAttribute('aria-pressed', on ? 'true' : 'false'); });
    };
    var toggle = function () {
      var st = read(); st.plans = st.plans || {};
      var p = st.plans[id] = st.plans[id] || { start: new Date().toISOString().slice(0, 10), done: [] };
      p.done = p.done || [];
      var i = p.done.indexOf(day);
      if (i >= 0) p.done.splice(i, 1); else p.done.push(day);
      try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {}
      paint();
    };
    var wrap = text.parentNode;
    [wrap.firstChild, null].forEach(function (before) {
      var bar = document.createElement('div');
      bar.className = 'plan-bar';
      bar.innerHTML = '<p class="label"></p><div class="btn-row"><button class="btn small" type="button"></button><a class="btn small secondary"></a></div>';
      bar.querySelector('.label').textContent = L[id] + ' · ' + L.day + ' ' + day + ' ' + L.of + ' ' + PLAN_LEN[id];
      var a = bar.querySelector('a'), btn = bar.querySelector('button');
      a.textContent = L.back; a.href = L.url + '#today';
      btn.addEventListener('click', toggle);
      bars.push(btn);
      wrap.insertBefore(bar, before);
    });
    paint();
  }

  fetch(BASE + 'books.json').then(function (r) { return r.json(); }).then(function (bs) {
    books = bs;
    var og = '<optgroup label="Old Testament">', ng = '<optgroup label="New Testament">';
    bs.forEach(function (b) { var o = '<option value="' + b.n + '">' + label(b) + '</option>'; if (b.nt) ng += o; else og += o; });
    book.innerHTML = og + '</optgroup>' + ng + '</optgroup>';
    var q = new URLSearchParams(location.search).get('ref');
    planBar();
    var ps = q ? q.replace(/\+/g, ' ').split(';').map(parse).filter(Boolean) : [];
    var p = ps[0] || null;
    if (ps.length > 1 || p && (p.c2 > p.c || p.v1 && new URLSearchParams(location.search).get('plan'))) { showPassages(ps, q); return; }
    if (q && p) ref.value = q.replace(/\+/g, ' ');
    show(p || { b: 48, c: 1 }, false);
  }).catch(function () { title.textContent = 'The Bible could not load'; text.innerHTML = '<p>Please check your connection and refresh the page.</p>'; });

  book.addEventListener('change', function () { show({ b: +book.value, c: 1 }, true); });
  chap.addEventListener('change', function () { show({ b: +book.value, c: +chap.value }, true); });
  $('bible-nav').addEventListener('submit', function (e) { e.preventDefault(); if (document.activeElement === ref && ref.value) go(); else show({ b: +book.value, c: +chap.value }, true); });
  $('bible-go').addEventListener('click', go);
  $('bible-prev').addEventListener('click', function () { step(-1); });
  $('bible-next').addEventListener('click', function () { step(1); });
  window.addEventListener('popstate', function (e) { if (e.state && e.state.b) show(e.state, false); });
})();
