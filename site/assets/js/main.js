/* CatholicDoorway shared scripts: navigation, theme, today's date and season, filters. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- Mobile navigation ---------- */
  var toggle = $('.nav-toggle'), nav = $('#site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('open')) { nav.classList.remove('open'); toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); }
    });
  }

  /* ---------- Theme toggle ---------- */
  var themeBtn = $('[data-theme-toggle]');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var root = document.documentElement;
      var cur = root.getAttribute('data-theme') ||
        (window.matchMedia && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      var next = cur === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('cd-theme', next); } catch (e) {}
    });
  }

  /* ---------- Dates and the liturgical year ---------- */
  function day(y, m, d) { return new Date(y, m, d); }
  function addDays(dt, n) { var r = new Date(dt); r.setDate(r.getDate() + n); return r; }
  function sameOrAfter(a, b) { return a.getTime() >= b.getTime(); }
  function easter(y) { // Anonymous Gregorian algorithm
    var a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4,
      f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30,
      i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7,
      m = Math.floor((a + 11 * h + 22 * l) / 451), month = Math.floor((h + l - 7 * m + 114) / 31),
      dd = ((h + l - 7 * m + 114) % 31) + 1;
    return day(y, month - 1, dd);
  }
  function advent1(y) { var d = day(y, 10, 27); while (d.getDay() !== 0) d = addDays(d, 1); return d; }
  function baptismOfLord(y) { // U.S. calendar: Epiphany is the Sunday from Jan 2 to 8
    var ep = day(y, 0, 2); while (ep.getDay() !== 0) ep = addDays(ep, 1);
    return ep.getDate() >= 7 ? addDays(ep, 1) : addDays(ep, 7);
  }
  var COLORS = { green: '#3f7a4a', violet: '#6a3f8a', white: '#f2ead6', red: '#a8322d' };

  function season(t) {
    var y = t.getFullYear(), e = easter(y), adv = advent1(y), bap = baptismOfLord(y);
    var ash = addDays(e, -46), holyThu = addDays(e, -3), pent = addDays(e, 49);
    var s;
    if (sameOrAfter(t, day(y, 11, 25))) s = { name: 'Christmas', color: 'white', next: ['the Baptism of the Lord', baptismOfLord(y + 1)] };
    else if (sameOrAfter(t, adv)) s = { name: 'Advent', color: 'violet', next: ['Christmas', day(y, 11, 25)] };
    else if (sameOrAfter(t, addDays(pent, 1))) s = { name: 'Ordinary Time', color: 'green', next: ['Advent', adv] };
    else if (sameOrAfter(t, e)) s = { name: 'Easter', color: 'white', next: ['Pentecost', pent] };
    else if (sameOrAfter(t, holyThu)) s = { name: 'The Easter Triduum', color: 'red', next: ['Easter Sunday', e] };
    else if (sameOrAfter(t, ash)) s = { name: 'Lent', color: 'violet', next: ['Easter', e] };
    else if (sameOrAfter(t, addDays(bap, 1))) s = { name: 'Ordinary Time', color: 'green', next: ['Ash Wednesday', ash] };
    else s = { name: 'Christmas', color: 'white', next: ['the Baptism of the Lord', bap] };
    if (t.getTime() === pent.getTime()) { s.name = 'Pentecost Sunday'; s.color = 'red'; }
    if (t.getTime() === e.getTime()) { s.name = 'Easter Sunday'; s.color = 'white'; }
    if (t.getTime() === addDays(adv, -7).getTime()) { s.name = 'Christ the King'; s.color = 'white'; }
    // Lectionary cycles: the liturgical year is named for the calendar year in which it ends.
    var ly = sameOrAfter(t, adv) ? y + 1 : y;
    s.sunday = ['C', 'A', 'B'][ly % 3];
    s.weekday = ly % 2 ? 'I' : 'II';
    return s;
  }

  var now = new Date();
  var today = day(now.getFullYear(), now.getMonth(), now.getDate());
  var longDate = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' };
  function usccb(d) {
    var mm = ('0' + (d.getMonth() + 1)).slice(-2), dd = ('0' + d.getDate()).slice(-2), yy = String(d.getFullYear()).slice(-2);
    return 'https://bible.usccb.org/bible/readings/' + mm + dd + yy + '.cfm';
  }
  var s = season(today);

  var dateEl = $('#today-date');
  if (dateEl) dateEl.textContent = today.toLocaleDateString('en-US', longDate);
  var seasonEl = $('#season');
  if (seasonEl) seasonEl.innerHTML = '<span class="season-dot" style="background:' + COLORS[s.color] + '"></span>' + s.name;
  var nextEl = $('#season-next');
  if (nextEl && s.next) {
    var days = Math.round((s.next[1] - today) / 86400000);
    if (days > 0 && days <= 60) nextEl.textContent = (days === 1 ? 'Tomorrow is ' : days + ' days until ') + s.next[0] + (days === 1 ? '.' : ', ' + s.next[1].toLocaleDateString('en-US', { month: 'long', day: 'numeric' }) + '.');
  }

  var tom = $('#readings-tomorrow'); if (tom) tom.href = usccb(addDays(today, 1));

  /* ---------- Daily readings card: titles, citations and links (no copied text) ---------- */
  var MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function esc(x) { return String(x || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var rcards = $$('[data-readings]');
  if (rcards.length) {
    var audioUrl = 'https://bible.usccb.org/podcasts/audio/daily-mass-reading-podcast-' + MONTHS[today.getMonth()] + '-' + today.getDate() + '-' + today.getFullYear();
    rcards.forEach(function (c) {
      $('.rd-read', c).href = usccb(today);
      $('.rd-listen', c).href = audioUrl;
    });
    var fallback = function () {
      rcards.forEach(function (c) {
        $('.rd-title', c).textContent = today.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
        $('.rd-list', c).innerHTML = '<li class="muted">Tap Read to see today&rsquo;s Scripture, or Listen to hear it.</li>';
      });
    };
    fetch('/api/readings?date=' + iso(today))
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) {
        if (!d || !d.readings || !d.readings.length) return fallback();
        rcards.forEach(function (c) {
          $('.rd-title', c).textContent = d.title || 'Today’s readings';
          $('.rd-list', c).innerHTML = d.readings.map(function (r) {
            var cite = r.url ? '<a href="' + esc(r.url) + '" target="_blank" rel="noopener">' + esc(r.citation) + '</a>' : esc(r.citation);
            return '<li><span class="rd-name">' + esc(r.name.replace(/^Responsorial /, '')) + '</span>' + cite + '</li>';
          }).join('');
          if (d.audio) $('.rd-listen', c).href = d.audio;
          if (d.page && /^https:\/\/bible\.usccb\.org\//.test(d.page)) $('.rd-read', c).href = d.page;
          var v = $('.rd-video', c);
          if (v && d.video) { v.href = d.video; v.hidden = false; }
        });
      })
      .catch(fallback);
  }
  var cyc = $('#cycle-note'); if (cyc) cyc.textContent = 'This liturgical year: Sunday readings Year ' + s.sunday + ', weekday readings Year ' + s.weekday + '. Season: ' + s.name + '.';
  var rform = $('#readings-form');
  if (rform) {
    var di = $('#readings-date-input');
    di.value = today.getFullYear() + '-' + ('0' + (today.getMonth() + 1)).slice(-2) + '-' + ('0' + today.getDate()).slice(-2);
    rform.addEventListener('submit', function (e) {
      e.preventDefault();
      var p = di.value.split('-');
      if (p.length === 3) window.open(usccb(day(+p[0], +p[1] - 1, +p[2])), '_blank', 'noopener');
    });
  }

  /* ---------- Rosary mysteries of the day ---------- */
  var MYST = ['Glorious', 'Joyful', 'Sorrowful', 'Glorious', 'Luminous', 'Sorrowful', 'Joyful'];
  var dow = today.getDay();
  var mt = $('#mystery-title');
  if (mt) { mt.textContent = 'The ' + MYST[dow] + ' Mysteries'; $('#mystery-sub').textContent = 'Today’s mysteries of the Rosary, with a step-by-step guide.'; }
  $$('#mysteries [data-days]').forEach(function (c) {
    if (c.getAttribute('data-days').split(',').indexOf(String(dow)) > -1) {
      c.classList.add('today-mystery');
      var h = c.querySelector('h4'); if (h) h.insertAdjacentHTML('beforeend', '<span class="badge">Today</span>');
    }
  });

  /* ---------- Copy buttons on prayers ---------- */
  $$('.prayer').forEach(function (p) {
    var txt = p.querySelector('.text');
    if (!txt || !navigator.clipboard) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'copy-btn'; b.textContent = 'Copy prayer';
    b.addEventListener('click', function () {
      navigator.clipboard.writeText(p.querySelector('h3').textContent.trim() + '\n\n' + txt.innerText.trim()).then(function () {
        b.textContent = 'Copied'; setTimeout(function () { b.textContent = 'Copy prayer'; }, 1800);
      });
    });
    var tools = document.createElement('div'); tools.className = 'prayer-tools'; tools.appendChild(b);
    p.appendChild(tools);
  });

  /* ---------- Filters ---------- */
  function norm(x) { return (x || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }

  // Saints
  var grid = $('#saint-grid');
  if (grid) {
    var cards = $$('.saint', grid), q = $('#saint-search'), chips = $$('.chip[data-status]'), statusSel = 'all';
    var count = $('#saint-count');
    var apply = function () {
      var term = norm(q.value), n = 0;
      cards.forEach(function (c) {
        var ok = (statusSel === 'all' || c.getAttribute('data-status') === statusSel) && (!term || norm(c.textContent).indexOf(term) > -1);
        c.hidden = !ok; if (ok) n++;
      });
      count.textContent = n + (n === 1 ? ' person' : ' people') + ' shown';
    };
    q.addEventListener('input', apply);
    chips.forEach(function (ch) {
      ch.addEventListener('click', function () {
        statusSel = ch.getAttribute('data-status');
        chips.forEach(function (o) { o.setAttribute('aria-pressed', o === ch ? 'true' : 'false'); });
        apply();
      });
    });
    apply();
  }

  // Glossary
  var gl = $('#glossary');
  if (gl) {
    var gq = $('#gloss-search'), gEmpty = $('#gloss-empty');
    gq.addEventListener('input', function () {
      var term = norm(gq.value), any = false;
      $$('dt', gl).forEach(function (dt) {
        var dd = dt.nextElementSibling;
        var ok = !term || norm(dt.textContent + ' ' + dd.textContent).indexOf(term) > -1;
        dt.hidden = dd.hidden = !ok; if (ok) any = true;
      });
      $$('.letter-head', gl).forEach(function (h) {
        var el = h.nextElementSibling, vis = false;
        while (el && !el.classList.contains('letter-head')) { if (el.tagName === 'DT' && !el.hidden) vis = true; el = el.nextElementSibling; }
        h.hidden = !vis;
      });
      gEmpty.hidden = any;
    });
  }

  // Dioceses
  /* ---------- First Mass companion: one step at a time, screen kept on, place saved ---------- */
  var mStart = $('#mass-start'), comp = $('#companion');
  if (mStart && comp) {
    var steps = $$('.mass-step'), at = 0, lock = null, KEY = 'cd-mass-step';
    var save = function () { try { localStorage.setItem(KEY, JSON.stringify({ i: at, t: Date.now() })); } catch (e) {} };
    var load = function () {
      try { var v = JSON.parse(localStorage.getItem(KEY)); if (v && Date.now() - v.t < 3 * 3600 * 1000) return v.i; } catch (e) {}
      return 0;
    };
    var keepAwake = function () {
      if (navigator.wakeLock && document.visibilityState === 'visible') {
        navigator.wakeLock.request('screen').then(function (l) { lock = l; }).catch(function () {});
      }
    };
    var show = function (i) {
      at = Math.max(0, Math.min(steps.length - 1, i));
      var st = steps[at], clone = st.cloneNode(true);
      clone.removeAttribute('id');
      var no = clone.querySelector('.mass-no'); if (no) no.remove();
      $('#comp-body').innerHTML = '';
      $('#comp-body').appendChild(clone);
      $('#comp-body').scrollTop = 0;
      $('#comp-part').textContent = st.getAttribute('data-part');
      $('#comp-count').textContent = (at + 1) + ' of ' + steps.length;
      $('#comp-progress').style.width = ((at + 1) / steps.length * 100) + '%';
      $('#comp-back').disabled = at === 0;
      $('#comp-next').innerHTML = at === steps.length - 1 ? 'Done' : 'Next &rarr;';
      save();
    };
    var open = function () {
      comp.hidden = false;
      document.body.classList.add('companion-open');
      show(load());
      keepAwake();
      $('#comp-next').focus();
    };
    var close = function () {
      comp.hidden = true;
      document.body.classList.remove('companion-open');
      if (lock) { lock.release().catch(function () {}); lock = null; }
      var st = steps[at]; if (st) st.scrollIntoView({ block: 'start' });
      mStart.focus();
    };
    mStart.addEventListener('click', open);
    $('#comp-close').addEventListener('click', close);
    $('#comp-back').addEventListener('click', function () { show(at - 1); });
    $('#comp-next').addEventListener('click', function () {
      if (at === steps.length - 1) { try { localStorage.removeItem(KEY); } catch (e) {} at = 0; close(); } else show(at + 1);
    });
    document.addEventListener('keydown', function (e) {
      if (comp.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowRight') show(at + 1);
      else if (e.key === 'ArrowLeft') show(at - 1);
    });
    var x0 = null;
    comp.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    comp.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 60) show(at + (dx < 0 ? 1 : -1));
    });
    document.addEventListener('visibilitychange', function () { if (!comp.hidden && !lock) keepAwake(); });
    if (load() > 0) mStart.textContent = 'Continue where you left off';
  }

  /* ---------- Holy days calendar ---------- */
  var calList = $('#cal-list');
  if (calList) {
    var LABEL = { obligation: 'Holy Day of Obligation', fast: 'Fast and abstinence', abstinence: 'Abstinence', solemnity: 'Solemnity', feast: 'Feast' };
    var calKind = 'all', calEvents = [];
    var todayIso = (function (d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); })(new Date());
    var escH = function (x) { return String(x || '').replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
    var drawCal = function () {
      var list = calEvents.filter(function (e) {
        if (e.date < todayIso) return false;
        if (calKind === 'fast') return e.kind === 'fast' || e.kind === 'abstinence';
        return calKind === 'all' || e.kind === calKind;
      });
      if (!list.length) { calList.innerHTML = '<p class="muted">Nothing coming up in this view.</p>'; return; }
      var out = '', month = '';
      list.forEach(function (e) {
        var d = new Date(e.date + 'T12:00:00');
        var m = d.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
        if (m !== month) { if (month) out += '</ol>'; month = m; out += '<h3 class="cal-month">' + m + '</h3><ol class="cal-month-list">'; }
        out += '<li class="cal-ev' + (e.date === todayIso ? ' today' : '') + '"><span class="cal-date"><b>' + d.getDate() + '</b>' +
          d.toLocaleDateString('en-US', { weekday: 'short' }) + '</span><div><strong>' + escH(e.title) + '</strong> ' +
          '<span class="kind kind-' + e.kind + '">' + LABEL[e.kind] + '</span>' + (e.note && e.note.indexOf(LABEL[e.kind]) !== 0 ? '<p>' + escH(e.note) + '</p>' : (e.note ? '<p>' + escH(e.note.replace(LABEL[e.kind] + ': ', '')) + '</p>' : '')) + '</div></li>';
      });
      calList.innerHTML = out + '</ol>';
    };
    $$('.chip[data-kind]').forEach(function (b) {
      b.addEventListener('click', function () {
        calKind = b.getAttribute('data-kind');
        $$('.chip[data-kind]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        drawCal();
      });
    });
    fetch('/api/calendar.json?year=' + new Date().getFullYear())
      .then(function (r) { return r.json(); })
      .then(function (d) { calEvents = d.events; drawCal(); })
      .catch(function () { calList.innerHTML = '<p class="muted">The calendar could not load. Please try again in a moment.</p>'; });
    // Android has no webcal handler; send Android users straight to Google Calendar.
    if (/Android/i.test(navigator.userAgent)) { var ap = $('#sub-apple'); if (ap) ap.hidden = true; }
  }

  /* ---------- Honest questions: search, open all, open from link ---------- */
  var qs = $('#qa-search');
  if (qs) {
    var qas = $$('.qa'), qEmpty = $('#qa-empty'), qt = $('#qa-toggle');
    qs.addEventListener('input', function () {
      var t = qs.value.trim().toLowerCase(), any = false;
      qas.forEach(function (d) { var ok = !t || d.textContent.toLowerCase().indexOf(t) > -1; d.hidden = !ok; if (ok) any = true; if (t && ok) d.open = true; });
      qEmpty.hidden = any;
    });
    qt.addEventListener('click', function () {
      var open = qt.getAttribute('aria-pressed') !== 'true';
      qas.forEach(function (d) { d.open = open; });
      qt.setAttribute('aria-pressed', open ? 'true' : 'false');
      qt.textContent = open ? 'Close all' : 'Open all';
    });
    var openHash = function () { var d = location.hash && document.getElementById(location.hash.slice(1)); if (d && d.tagName === 'DETAILS') { d.open = true; d.scrollIntoView(); } };
    window.addEventListener('hashchange', openHash); openHash();
  }

  /* ---------- Popes: search ---------- */
  var pq = $('#pope-search');
  if (pq) {
    var popes = $$('.pope'), heads = $$('.pope-cent'), pEmpty = $('#pope-empty');
    popes.forEach(function (li) { li._t = (li.value + ' ' + li.textContent).toLowerCase(); });
    pq.addEventListener('input', function () {
      var t = pq.value.trim().toLowerCase(), any = false;
      popes.forEach(function (li) { var ok = !t || li._t.indexOf(t) > -1; li.hidden = !ok; if (ok) any = true; });
      heads.forEach(function (h) {
        var ol = h.nextElementSibling;
        h.hidden = ol.hidden = !$$('.pope', ol).some(function (li) { return !li.hidden; });
      });
      pEmpty.hidden = any;
    });
  }

  var dq = $('#dio-search');
  if (dq) {
    var rows = $$('#dio-table tbody tr'), dEmpty = $('#dio-empty');
    dq.addEventListener('input', function () {
      var term = norm(dq.value).trim(), n = 0;
      rows.forEach(function (r) {
        var text = norm(r.textContent);
        var ok = !term || text.indexOf(term) > -1 || (term.length === 2 && text.indexOf('(' + term + ')') > -1);
        r.hidden = !ok; if (ok) n++;
      });
      dEmpty.hidden = n > 0;
    });
  }
})();
