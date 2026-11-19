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
  // "John 3:16-18", "1 Cor 13", "Psalm 22", "jn 3 16"
  function parse(s) {
    var m = /^\s*(.+?)\s*(\d+)(?:\s*[:.\s]\s*(\d+)(?:\s*[-–]\s*(\d+))?)?\s*$/.exec(String(s || ''));
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
    show(p, true);
  }

  fetch(BASE + 'books.json').then(function (r) { return r.json(); }).then(function (bs) {
    books = bs;
    var og = '<optgroup label="Old Testament">', ng = '<optgroup label="New Testament">';
    bs.forEach(function (b) { var o = '<option value="' + b.n + '">' + label(b) + '</option>'; if (b.nt) ng += o; else og += o; });
    book.innerHTML = og + '</optgroup>' + ng + '</optgroup>';
    var q = new URLSearchParams(location.search).get('ref');
    var p = q ? parse(q.replace(/\+/g, ' ')) : null;
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
