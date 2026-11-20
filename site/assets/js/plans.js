/* CatholicDoorway reading plans: Bible in a Year, Catechism in a Year, the Gospels in 30 days, OCIA in 90 days.
   The schedule comes from /data/plans-<lang>.json (built by src/plans.py).
   Progress stays on this device only (localStorage "cd-plans"): no account, nothing sent anywhere. */
(function () {
  'use strict';
  var root = document.getElementById('reading-plans');
  if (!root) return;
  var LG = (document.documentElement.lang || 'en').slice(0, 2);
  if (['en', 'es', 'pt', 'tl'].indexOf(LG) < 0) LG = 'en';
  var LOCALE = { en: 'en-US', es: 'es-US', pt: 'pt-BR', tl: 'fil-PH' }[LG];
  var KEY = 'cd-plans', LEN = { bible: 365, catechism: 365, gospels: 30, ocia: 90 }, IDS = ['bible', 'catechism', 'gospels', 'ocia'];
  var S = {
    en: {
      names: { bible: 'Bible in a Year', catechism: 'Catechism in a Year', gospels: 'The Gospels in 30 Days', ocia: 'OCIA in 90 Days' },
      day: 'Day', of: 'of', startToday: 'Start today', startOn: 'Start on this date', otherDate: 'Choose another start date',
      jan1: 'Start on January 1 (read with others on the calendar year)', started: 'Started', change: 'Change start date',
      stop: 'Stop this plan', stopSure: 'Tap again to stop and clear progress', readAll: 'Read today’s passages',
      mark: 'Mark as read', marked: 'Read ✓', progress: '{n} of {t} days read', behind: 'You have {n} unread {d} before today.',
      dayWord: 'day', daysWord: 'days', next: 'Next unread: Day {n}', future: 'Your plan starts on {date}. Here is Day 1 to look ahead.',
      finished: 'You have reached the end of this plan. Well done, and thanks be to God!', finishedBehind: 'The plan’s last day has passed. Read the days you missed whenever you like.',
      today: 'Today', schedule: 'Show the schedule', hide: 'Hide the schedule', days: 'Days {a}–{b}', none: 'Pick a plan below to begin. Today’s reading will show up here every time you come back.',
      opens: 'opens vatican.va', cont: 'next page', loadErr: 'The reading plans could not load. Please check your connection and refresh the page.',
      calName: 'CatholicDoorway reading plan', planFor: 'Reminders for', time: 'Time',
      notStarted: 'Not started yet: the reminders will begin today.'
    },
    es: {
      names: { bible: 'La Biblia en un año', catechism: 'El Catecismo en un año', gospels: 'Los Evangelios en 30 días', ocia: 'OCIA en 90 días' },
      day: 'Día', of: 'de', startToday: 'Empezar hoy', startOn: 'Empezar en esta fecha', otherDate: 'Elegir otra fecha de inicio',
      jan1: 'Empezar el 1 de enero (para leer con otros según el año)', started: 'Empezaste el', change: 'Cambiar la fecha de inicio',
      stop: 'Dejar este plan', stopSure: 'Toca otra vez para dejarlo y borrar tu avance', readAll: 'Leer las lecturas de hoy',
      mark: 'Marcar como leído', marked: 'Leído ✓', progress: '{n} de {t} días leídos', behind: 'Tienes {n} {d} sin leer antes de hoy.',
      dayWord: 'día', daysWord: 'días', next: 'Siguiente sin leer: día {n}', future: 'Tu plan empieza el {date}. Aquí tienes el día 1 para adelantarte.',
      finished: 'Has llegado al final de este plan. ¡Muy bien, y gracias a Dios!', finishedBehind: 'Ya pasó el último día del plan. Lee los días que te faltan cuando quieras.',
      today: 'Hoy', schedule: 'Ver el calendario', hide: 'Ocultar el calendario', days: 'Días {a}–{b}', none: 'Elige un plan abajo para empezar. La lectura de hoy aparecerá aquí cada vez que vuelvas.',
      opens: 'abre vatican.va', cont: 'página siguiente', loadErr: 'No se pudieron cargar los planes de lectura. Revisa tu conexión y vuelve a cargar la página.',
      calName: 'Plan de lectura de CatholicDoorway', planFor: 'Recordatorios para', time: 'Hora',
      notStarted: 'Aún no empiezas: los recordatorios comenzarán hoy.'
    },
    pt: {
      names: { bible: 'A Bíblia em um ano', catechism: 'O Catecismo em um ano', gospels: 'Os Evangelhos em 30 dias', ocia: 'OCIA em 90 dias' },
      day: 'Dia', of: 'de', startToday: 'Começar hoje', startOn: 'Começar nesta data', otherDate: 'Escolher outra data de início',
      jan1: 'Começar em 1º de janeiro (para ler com outros pelo ano civil)', started: 'Começou em', change: 'Mudar a data de início',
      stop: 'Parar este plano', stopSure: 'Toque de novo para parar e apagar o progresso', readAll: 'Ler as leituras de hoje',
      mark: 'Marcar como lido', marked: 'Lido ✓', progress: '{n} de {t} dias lidos', behind: 'Você tem {n} {d} sem ler antes de hoje.',
      dayWord: 'dia', daysWord: 'dias', next: 'Próximo não lido: dia {n}', future: 'Seu plano começa em {date}. Aqui está o dia 1 para você se adiantar.',
      finished: 'Você chegou ao fim deste plano. Parabéns, e graças a Deus!', finishedBehind: 'O último dia do plano já passou. Leia os dias que faltam quando quiser.',
      today: 'Hoje', schedule: 'Ver o cronograma', hide: 'Esconder o cronograma', days: 'Dias {a}–{b}', none: 'Escolha um plano abaixo para começar. A leitura de hoje aparecerá aqui sempre que você voltar.',
      opens: 'abre vatican.va', cont: 'página seguinte', loadErr: 'Não foi possível carregar os planos de leitura. Verifique sua conexão e recarregue a página.',
      calName: 'Plano de leitura do CatholicDoorway', planFor: 'Lembretes para', time: 'Horário',
      notStarted: 'Ainda não começou: os lembretes começam hoje.'
    },
    tl: {
      names: { bible: 'Ang Bibliya sa isang taon', catechism: 'Ang Katesismo sa isang taon', gospels: 'Ang mga Ebanghelyo sa 30 araw', ocia: 'OCIA sa 90 araw' },
      day: 'Araw', of: 'sa', startToday: 'Magsimula ngayon', startOn: 'Magsimula sa petsang ito', otherDate: 'Pumili ng ibang petsa ng simula',
      jan1: 'Magsimula sa Enero 1 (para sumabay sa iba ayon sa taon)', started: 'Nagsimula noong', change: 'Palitan ang petsa ng simula',
      stop: 'Itigil ang planong ito', stopSure: 'Pindutin muli para itigil at burahin ang progreso', readAll: 'Basahin ang mga pagbasa ngayon',
      mark: 'Markahang nabasa', marked: 'Nabasa ✓', progress: '{n} sa {t} araw ang nabasa', behind: 'May {n} {d} kang hindi pa nababasa bago ngayon.',
      dayWord: 'araw', daysWord: 'araw', next: 'Susunod na hindi pa nababasa: Araw {n}', future: 'Magsisimula ang iyong plano sa {date}. Narito ang Araw 1 para makapaghanda.',
      finished: 'Natapos mo na ang planong ito. Magaling, at salamat sa Diyos!', finishedBehind: 'Lumipas na ang huling araw ng plano. Basahin ang mga araw na nalaktawan mo kahit kailan.',
      today: 'Ngayon', schedule: 'Ipakita ang iskedyul', hide: 'Itago ang iskedyul', days: 'Araw {a}–{b}', none: 'Pumili ng plano sa ibaba para magsimula. Lalabas dito ang pagbasa ngayong araw tuwing babalik ka.',
      opens: 'bubuksan ang vatican.va', cont: 'susunod na pahina', loadErr: 'Hindi ma-load ang mga plano sa pagbasa. Pakisuri ang iyong koneksiyon at i-refresh ang pahina.',
      calName: 'Plano sa pagbasa ng CatholicDoorway', planFor: 'Mga paalala para sa', time: 'Oras',
      notStarted: 'Hindi pa nagsisimula: magsisimula ngayon ang mga paalala.'
    }
  }[LG];
  var $ = function (id) { return document.getElementById(id); };
  var fmt = function (s, o) { return s.replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); };
  var el = function (tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };

  /* ---------- storage ---------- */
  function load() { try { var s = JSON.parse(localStorage.getItem(KEY)); return s && s.plans ? s : { plans: {} }; } catch (e) { return { plans: {} }; } }
  function save(st) { try { localStorage.setItem(KEY, JSON.stringify(st)); } catch (e) {} }
  var state = load();

  /* ---------- dates (local calendar days) ---------- */
  function iso(d) { return d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2); }
  function parseIso(s) { var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || ''); return m ? new Date(+m[1], +m[2] - 1, +m[3]) : null; }
  var now = new Date(), today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  function addDays(d, n) { return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n); }
  function dayNum(p) { var s = parseIso(p.start); return s ? Math.round((today - s) / 86400000) + 1 : 1; }
  function longDate(d) { try { return d.toLocaleDateString(LOCALE, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }); } catch (e) { return iso(d); } }
  function shortDate(d) { try { return d.toLocaleDateString(LOCALE, { month: 'short', day: 'numeric' }); } catch (e) { return iso(d); } }

  var DATA = null, openSchedule = null;
  var done = function (id) { var p = state.plans[id]; return p && p.done ? p.done : []; };
  var isDone = function (id, n) { return done(id).indexOf(n) >= 0; };
  function setDone(id, n, on) {
    var p = state.plans[id]; if (!p) p = state.plans[id] = { start: iso(today), done: [] };
    p.done = (p.done || []).filter(function (x) { return x !== n; });
    if (on) p.done.push(n);
    p.done.sort(function (a, b) { return a - b; });
    save(state);
    renderAll();
  }

  /* ---------- one day's readings ---------- */
  function readerUrl(refs, id, n) {
    return '/read-the-bible?ref=' + refs.join(';') + '&plan=' + id + '&day=' + n + (LG === 'en' ? '' : '&lang=' + LG);
  }
  function readingList(id, n) {
    var ul = el('ul', 'plan-readings');
    DATA[id][n - 1].forEach(function (r) {
      var li = el('li');
      if (r.k === 'b') {
        var a = el('a', null, r.l); a.href = readerUrl([r.r], id, n); li.appendChild(a);
      } else {
        var c = el('a', null, r.l); c.href = r.u; c.target = '_blank'; c.rel = 'noopener'; c.title = S.opens; li.appendChild(c);
        if (r.u2) { li.appendChild(document.createTextNode(' (')); var c2 = el('a', null, S.cont); c2.href = r.u2; c2.target = '_blank'; c2.rel = 'noopener'; li.appendChild(c2); li.appendChild(document.createTextNode(')')); }
        if (r.t) li.appendChild(el('span', 'plan-topic', r.t));
      }
      ul.appendChild(li);
    });
    return ul;
  }
  function bibleRefs(id, n) { return DATA[id][n - 1].filter(function (r) { return r.k === 'b'; }).map(function (r) { return r.r; }); }
  function markBtn(id, n) {
    var b = el('button', 'btn small' + (isDone(id, n) ? ' secondary' : ''), isDone(id, n) ? S.marked : S.mark);
    b.type = 'button'; b.setAttribute('aria-pressed', isDone(id, n) ? 'true' : 'false');
    b.addEventListener('click', function () { setDone(id, n, !isDone(id, n)); });
    return b;
  }
  function bar(id) {
    var t = LEN[id], n = done(id).length, wrap = el('div', 'plan-progress');
    var m = el('div', 'plan-meter'); m.setAttribute('role', 'progressbar'); m.setAttribute('aria-valuemin', '0'); m.setAttribute('aria-valuemax', String(t)); m.setAttribute('aria-valuenow', String(n));
    var f = el('span'); f.style.width = (100 * n / t).toFixed(1) + '%'; m.appendChild(f);
    wrap.appendChild(m); wrap.appendChild(el('p', 'small muted', fmt(S.progress, { n: n, t: t }) + ' (' + Math.round(100 * n / t) + '%)'));
    return wrap;
  }

  /* ---------- Today ---------- */
  function renderToday() {
    var box = $('plan-today'); box.innerHTML = '';
    var active = IDS.filter(function (id) { return state.plans[id]; });
    $('plan-none').hidden = active.length > 0;
    active.forEach(function (id) {
      var p = state.plans[id], n = dayNum(p), t = LEN[id], card = el('article', 'card plan-today');
      card.appendChild(el('p', 'label', S.names[id]));
      var shown = Math.min(Math.max(n, 1), t);
      var h = el('h3', null, S.day + ' ' + shown + ' ' + S.of + ' ' + t);
      card.appendChild(h);
      card.appendChild(el('p', 'small muted', longDate(addDays(parseIso(p.start), shown - 1))));
      if (n < 1) card.appendChild(el('p', 'plan-note', fmt(S.future, { date: longDate(parseIso(p.start)) })));
      if (n > t) card.appendChild(el('p', 'plan-note', done(id).length >= t ? S.finished : S.finishedBehind));
      card.appendChild(readingList(id, shown));
      var row = el('div', 'btn-row plan-actions');
      var refs = bibleRefs(id, shown);
      if (refs.length) { var a = el('a', 'btn small secondary', S.readAll); a.href = readerUrl(refs, id, shown); row.appendChild(a); }
      row.appendChild(markBtn(id, shown));
      card.appendChild(row);
      card.appendChild(bar(id));
      var missed = [];
      for (var i = 1; i < Math.min(n, t + 1); i++) if (!isDone(id, i)) missed.push(i);
      if (n > t && !isDone(id, t)) missed = missed.filter(function (x) { return x !== t; });
      if (missed.length) {
        var note = el('p', 'small plan-behind', fmt(S.behind, { n: missed.length, d: missed.length === 1 ? S.dayWord : S.daysWord }) + ' ');
        var go = el('a', null, fmt(S.next, { n: missed[0] })); go.href = '#day-' + id + '-' + missed[0];
        go.addEventListener('click', function (e) { e.preventDefault(); showSchedule(id, missed[0]); });
        note.appendChild(go); card.appendChild(note);
      }
      box.appendChild(card);
    });
  }

  /* ---------- plan cards: start, change, stop ---------- */
  function renderCard(id) {
    var slot = document.querySelector('#plan-' + id + ' .plan-start'); if (!slot) return;
    slot.innerHTML = '';
    var p = state.plans[id];
    if (p) {
      slot.appendChild(el('p', 'small', S.started + ' ' + longDate(parseIso(p.start)) + ' · ' + S.day + ' ' + Math.min(Math.max(dayNum(p), 1), LEN[id]) + ' ' + S.of + ' ' + LEN[id]));
      slot.appendChild(bar(id));
    } else {
      var b = el('button', 'btn small', S.startToday); b.type = 'button';
      b.addEventListener('click', function () { start(id, iso(today)); });
      slot.appendChild(b);
    }
    var det = el('details', 'plan-date'), sum = el('summary', null, p ? S.change : S.otherDate);
    det.appendChild(sum);
    var lab = el('label', 'sr-only', p ? S.change : S.otherDate), inp = el('input'), go = el('button', 'btn small secondary', S.startOn);
    inp.type = 'date'; inp.value = p ? p.start : iso(today); inp.id = 'start-' + id; lab.htmlFor = inp.id; go.type = 'button';
    go.addEventListener('click', function () { if (parseIso(inp.value)) start(id, inp.value); });
    var row = el('div', 'plan-date-row'); row.appendChild(lab); row.appendChild(inp); row.appendChild(go); det.appendChild(row);
    if (LEN[id] === 365) {
      var j = el('button', 'linkish small', S.jan1); j.type = 'button';
      j.addEventListener('click', function () { start(id, today.getFullYear() + '-01-01'); });
      det.appendChild(j);
    }
    if (p) {
      var stop = el('button', 'linkish small danger', S.stop), armed = false; stop.type = 'button';
      stop.addEventListener('click', function () {
        if (!armed) { armed = true; stop.textContent = S.stopSure; setTimeout(function () { armed = false; stop.textContent = S.stop; }, 5000); return; }
        delete state.plans[id]; save(state); renderAll();
      });
      det.appendChild(stop);
    }
    slot.appendChild(det);
    var sh = el('button', 'linkish small', openSchedule === id ? S.hide : S.schedule); sh.type = 'button';
    sh.setAttribute('aria-expanded', openSchedule === id ? 'true' : 'false');
    sh.addEventListener('click', function () { if (openSchedule === id) { openSchedule = null; renderSchedule(); renderCards(); } else showSchedule(id); });
    slot.appendChild(sh);
  }
  function renderCards() { IDS.forEach(renderCard); }
  function start(id, date) {
    var p = state.plans[id];
    state.plans[id] = { start: date, done: p ? p.done || [] : [] };
    save(state); renderAll();
    var t = $('today'); if (t && t.scrollIntoView) t.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ---------- full schedule with checkboxes ---------- */
  function showSchedule(id, n) {
    openSchedule = id; renderSchedule(n); renderCards();
    var target = n ? $('day-' + id + '-' + n) : $('plan-schedule');
    if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  function renderSchedule(focus) {
    var box = $('plan-schedule'); box.innerHTML = '';
    var id = openSchedule; box.hidden = !id; if (!id) return;
    var p = state.plans[id], cur = p ? dayNum(p) : 0, t = LEN[id], startD = p ? parseIso(p.start) : null;
    box.appendChild(el('h2', null, S.names[id]));
    box.appendChild(bar(id));
    for (var a = 1; a <= t; a += 30) {
      var b = Math.min(a + 29, t), det = el('details', 'plan-block');
      if ((focus && focus >= a && focus <= b) || (!focus && (cur >= a && cur <= b || (!p && a === 1)))) det.open = true;
      var cnt = 0; for (var k = a; k <= b; k++) if (isDone(id, k)) cnt++;
      det.appendChild(el('summary', null, fmt(S.days, { a: a, b: b }) + '  ·  ' + cnt + '/' + (b - a + 1)));
      var ol = el('ol', 'plan-days');
      for (var n = a; n <= b; n++) {
        var li = el('li'); li.id = 'day-' + id + '-' + n;
        if (n === cur) li.className = 'is-today';
        var lab = el('label', 'plan-check'), cb = el('input');
        cb.type = 'checkbox'; cb.checked = isDone(id, n); cb.dataset.n = n;
        cb.addEventListener('change', function () { setDone(id, +this.dataset.n, this.checked); });
        lab.appendChild(cb);
        lab.appendChild(el('span', 'plan-dn', S.day + ' ' + n + (startD ? ' · ' + shortDate(addDays(startD, n - 1)) : '')));
        li.appendChild(lab);
        li.appendChild(readingList(id, n));
        ol.appendChild(li);
      }
      det.appendChild(ol);
      box.appendChild(det);
    }
  }

  /* ---------- calendar reminders ---------- */
  function renderReminder() {
    var sel = $('rem-plan'), tm = $('rem-time'); if (!sel) return;
    var id = sel.value, p = state.plans[id], startD = p ? p.start : iso(today);
    $('rem-note').textContent = p ? S.started + ' ' + longDate(parseIso(p.start)) + '.' : S.notStarted;
    var q = 'plan=' + id + '&start=' + startD + '&time=' + tm.value + (LG === 'en' ? '' : '&lang=' + LG);
    var https = 'https://catholicdoorway.com/api/plans.ics?' + q, webcal = 'webcal://catholicdoorway.com/api/plans.ics?' + q;
    $('rem-apple').href = webcal;
    $('rem-google').href = 'https://calendar.google.com/calendar/r?cid=' + encodeURIComponent(webcal);
    $('rem-outlook').href = 'https://outlook.live.com/calendar/0/addfromweb?url=' + encodeURIComponent(https) + '&name=' + encodeURIComponent(S.names[id]);
    $('rem-ics').href = https;
  }

  function renderAll() {
    renderToday(); renderCards(); renderSchedule(); renderReminder();
  }

  var sel = $('rem-plan');
  if (sel) {
    var first = IDS.filter(function (id) { return state.plans[id]; })[0];
    if (first) sel.value = first;
    sel.addEventListener('change', renderReminder); $('rem-time').addEventListener('change', renderReminder);
    if (/Android/i.test(navigator.userAgent)) $('rem-apple').hidden = true;
  }

  fetch('/data/plans-' + LG + '.json').then(function (r) { if (!r.ok) throw 0; return r.json(); }).then(function (d) {
    DATA = d;
    root.classList.add('ready');
    var m = /^#plan-(\w+)$/.exec(location.hash);
    var qs = new URLSearchParams(location.search), qp = qs.get('plan');
    renderAll();
    if (qp && LEN[qp]) showSchedule(qp, parseInt(qs.get('day'), 10) || null);
    else if (m && LEN[m[1]]) { var c = $('plan-' + m[1]); if (c) c.scrollIntoView(); }
  }).catch(function () { $('plan-today').textContent = S.loadErr; $('plan-none').hidden = true; });
})();
