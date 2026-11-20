/* CatholicDoorway Kids and Families: tap-to-color pictures, printing one picture or sheet,
   prayers read aloud, the next saint story and this season's family ideas.
   Everything stays on this device; nothing is sent anywhere. */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var LG = document.documentElement.lang;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} return null; }

  /* ---------- Print just one picture or one sheet ---------- */
  function printNode(node, blank) {
    var old = $('#print-area'); if (old) old.remove();
    var area = document.createElement('div'); area.id = 'print-area';
    var copy = node.cloneNode(true);
    copy.removeAttribute('id');
    if (blank) $$('.r', copy).forEach(function (r) { r.style.fill = ''; });
    area.appendChild(copy);
    document.body.appendChild(area);
    document.documentElement.classList.add('printing');
    var done = function () {
      document.documentElement.classList.remove('printing');
      if (area.parentNode) area.remove();
      window.removeEventListener('afterprint', done);
    };
    window.addEventListener('afterprint', done);
    setTimeout(function () { window.print(); }, 50);
  }
  $$('[data-print]').forEach(function (b) {
    b.addEventListener('click', function () { var n = $(b.getAttribute('data-print')); if (n) printNode(n, !!b.getAttribute('data-blank')); });
  });

  /* ---------- Coloring pages ---------- */
  var app = $('#coloring-app');
  if (app) {
    var studio = $('#studio'), art = $('#studio-art'), title = $('#studio-title');
    var cur = null, curId = null, regions = [], hist = [], color = '#e53935';
    var swatches = $$('.swatch', studio);
    var saved = store('cd-color-swatch');
    swatches.forEach(function (s) {
      if (saved && s.getAttribute('data-c') === saved) color = saved;
      s.addEventListener('click', function () {
        color = s.getAttribute('data-c'); store('cd-color-swatch', color);
        swatches.forEach(function (o) { o.setAttribute('aria-pressed', o === s ? 'true' : 'false'); });
      });
    });
    swatches.forEach(function (o) { o.setAttribute('aria-pressed', o.getAttribute('data-c') === color ? 'true' : 'false'); });

    var load = function (id) { try { return JSON.parse(store('cd-color-' + id)) || {}; } catch (e) { return {}; } };
    var paint = function (svg, fills) { var rs = $$('.r', svg); Object.keys(fills).forEach(function (i) { if (rs[i]) rs[i].style.fill = fills[i]; }); };
    // Show saved work in the gallery too
    $$('.cpage-card').forEach(function (card) { var svg = $('svg', card); paint(svg, load(svg.getAttribute('data-page'))); });

    var save = function () {
      var fills = {};
      regions.forEach(function (r, i) { if (r.style.fill) fills[i] = r.style.fill; });
      if (Object.keys(fills).length) store('cd-color-' + curId, JSON.stringify(fills)); else store('cd-color-' + curId, null);
      var thumb = $('#color-' + curId + ' svg');
      if (thumb) { var trs = $$('.r', thumb); trs.forEach(function (r, i) { r.style.fill = fills[i] || ''; }); }
    };
    var open = function (id, scroll) {
      var src = $('#color-' + id + ' svg');
      if (!src) return;
      curId = id; hist = [];
      cur = src.cloneNode(true);
      art.innerHTML = ''; art.appendChild(cur);
      regions = $$('.r', cur);
      title.textContent = $('#color-' + id + ' h3').textContent;
      studio.hidden = false;
      if (scroll) studio.scrollIntoView({ behavior: 'smooth', block: 'start' });
      try { history.replaceState(null, '', '#color-' + id); } catch (e) {}
    };
    art.addEventListener('click', function (ev) {
      var r = ev.target.closest ? ev.target.closest('.r') : null;
      if (!r || !cur) return;
      var i = regions.indexOf(r);
      if (i < 0) return;
      hist.push([i, r.style.fill]);
      r.style.fill = color;
      save();
    });
    $('#studio-undo').addEventListener('click', function () {
      var h = hist.pop(); if (!h) return;
      if (h[0] === 'all') regions.forEach(function (r, i) { r.style.fill = h[1][i] || ''; });
      else regions[h[0]].style.fill = h[1];
      save();
    });
    $('#studio-clear').addEventListener('click', function () {
      hist.push(['all', regions.map(function (r) { return r.style.fill; })]);
      regions.forEach(function (r) { r.style.fill = ''; });
      save();
    });
    $('#studio-print').addEventListener('click', function () { if (cur) printNode(cur, false); });
    $('#studio-blank').addEventListener('click', function () { if (cur) printNode(cur, true); });
    $('#studio-close').addEventListener('click', function () {
      studio.hidden = true;
      var card = $('#color-' + curId);
      if (card) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    $$('[data-color]').forEach(function (b) { b.addEventListener('click', function () { open(b.getAttribute('data-color'), true); }); });
    $$('.cpage-card svg').forEach(function (svg) {
      svg.style.cursor = 'pointer';
      svg.addEventListener('click', function () { open(svg.getAttribute('data-page'), true); });
    });
    var m = /^#color-([a-z-]+)$/.exec(location.hash);
    if (m) setTimeout(function () { open(m[1], true); }, 60);
  }

  /* ---------- First prayers, read aloud ---------- */
  var fp = $('#first-prayers');
  if (fp && 'speechSynthesis' in window && window.SpeechSynthesisUtterance) {
    var synth = window.speechSynthesis, bar = $('#kp-bar'), voice = null, rate = parseFloat(store('cd-kp-rate')) || 0.7, playing = null;
    var WANT = { en: ['en-US', 'en'], es: ['es-US', 'es-MX', 'es'], pt: ['pt-BR', 'pt'], tl: ['fil', 'tl'] }[LG] || ['en'];
    var pick = function () {
      var vs = synth.getVoices() || [];
      for (var w = 0; w < WANT.length; w++) {
        for (var i = 0; i < vs.length; i++) {
          var l = (vs[i].lang || '').replace('_', '-');
          if (l === WANT[w] || l.toLowerCase().indexOf(WANT[w].toLowerCase()) === 0) return vs[i];
        }
      }
      return null;
    };
    var ready = function () {
      voice = pick();
      var ok = !!voice || (LG === 'en' && synth.getVoices().length === 0);
      bar.hidden = false;
      $('#kp-novoice').hidden = ok;
      $$('.kp-say', fp).forEach(function (b) { b.hidden = !ok; });
    };
    var READ = $('.kp-say', fp) ? $('.kp-say', fp).innerHTML : 'Read aloud';
    var STOP = { en: '&#9632; Stop', es: '&#9632; Parar', pt: '&#9632; Parar', tl: '&#9632; Itigil' }[LG] || '&#9632; Stop';
    var reset = function () {
      $$('.kp-line.on', fp).forEach(function (l) { l.classList.remove('on'); });
      $$('.kp-say', fp).forEach(function (b) { b.innerHTML = READ; });
      playing = null;
    };
    $$('.chip[data-rate]', bar).forEach(function (c) {
      c.setAttribute('aria-pressed', Math.abs(parseFloat(c.getAttribute('data-rate')) - rate) < 0.01 ? 'true' : 'false');
      c.addEventListener('click', function () {
        rate = parseFloat(c.getAttribute('data-rate')); store('cd-kp-rate', String(rate));
        $$('.chip[data-rate]', bar).forEach(function (o) { o.setAttribute('aria-pressed', o === c ? 'true' : 'false'); });
      });
    });
    $$('.kid-prayer', fp).forEach(function (card) {
      var btn = $('.kp-say', card), lines = $$('.kp-line', card);
      btn.addEventListener('click', function () {
        var was = playing;
        synth.cancel(); reset();
        if (was === card) return;
        playing = card; btn.innerHTML = STOP;
        lines.forEach(function (line, i) {
          var u = new SpeechSynthesisUtterance(line.textContent);
          if (voice) { u.voice = voice; u.lang = voice.lang; } else u.lang = WANT[0];
          u.rate = rate;
          u.onstart = function () { $$('.kp-line.on', fp).forEach(function (l) { l.classList.remove('on'); }); line.classList.add('on'); };
          if (i === lines.length - 1) u.onend = function () { if (playing === card) reset(); };
          synth.speak(u);
        });
      });
    });
    ready();
    if (synth.addEventListener) synth.addEventListener('voiceschanged', ready); else synth.onvoiceschanged = ready;
    window.addEventListener('pagehide', function () { synth.cancel(); });
  }

  /* ---------- Date helpers (U.S. calendar) ---------- */
  function day(y, m, d) { return new Date(y, m, d); }
  function addDays(dt, n) { var r = new Date(dt); r.setDate(r.getDate() + n); return r; }
  function easter(y) {
    var a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4,
      f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30,
      i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7,
      m = Math.floor((a + 11 * h + 22 * l) / 451), mo = Math.floor((h + l - 7 * m + 114) / 31),
      dd = ((h + l - 7 * m + 114) % 31) + 1;
    return day(y, mo - 1, dd);
  }
  function advent1(y) { var d = day(y, 10, 27); while (d.getDay() !== 0) d = addDays(d, 1); return d; }
  function baptismOfLord(y) { var ep = day(y, 0, 2); while (ep.getDay() !== 0) ep = addDays(ep, 1); return ep.getDate() >= 7 ? addDays(ep, 1) : addDays(ep, 7); }
  var now = new Date(), today = day(now.getFullYear(), now.getMonth(), now.getDate());

  /* ---------- Saint stories: today's or the next one ---------- */
  var ss = $('#saint-stories');
  if (ss) {
    var ui = JSON.parse($('#saint-ui').textContent);
    var key = ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
    var cards = $$('.kid-saint', ss), hit = null, isToday = false;
    cards.forEach(function (c) { if (!hit && c.getAttribute('data-feast') === key) { hit = c; isToday = true; } });
    if (!hit) cards.forEach(function (c) { if (!hit && c.getAttribute('data-feast') > key) hit = c; });
    if (!hit) hit = cards[0];
    if (hit) {
      var label = isToday ? ui.today : ui.next, f = hit.getAttribute('data-feast');
      $('#saint-feature-label').innerHTML = label;
      $('#saint-feature-name').textContent = $('h3', hit).textContent;
      $('#saint-feature-date').textContent = ui.fmt.replace('{m}', ui.months[+f.slice(0, 2) - 1]).replace('{d}', String(+f.slice(3)));
      $('#saint-feature-link').href = '#' + hit.id;
      hit.classList.add('is-next');
      var flag = $('.ks-flag', hit); flag.innerHTML = label; flag.hidden = false;
    }
  }

  /* ---------- Family corner: this season ---------- */
  var fc = $('#family-corner');
  if (fc) {
    var y = today.getFullYear(), e = easter(y), s;
    if (today >= day(y, 11, 25) || today <= baptismOfLord(y)) s = 'christmas';
    else if (today >= advent1(y)) s = 'advent';
    else if (today >= addDays(e, -46) && today < e) s = 'lent';
    else if (today >= e && today <= addDays(e, 49)) s = 'easter';
    else s = 'ordinary';
    var sec = $('#season-' + s), fui = JSON.parse($('#fam-ui').textContent);
    if (sec) {
      $('.fam-now', sec).hidden = false;
      var line = $('#fam-season-now');
      line.innerHTML = '<span class="season-dot" style="background:' + getComputedStyle($('.season-dot', sec)).backgroundColor + '"></span>' +
        fui.now.replace('{name}', '<a href="#season-' + s + '">' + fui.names[s] + '</a>');
      line.hidden = false;
    }
  }
})();
