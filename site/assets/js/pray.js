/* CatholicDoorway: examination of conscience, devotions and reminders, novenas, Angelus,
   Liturgy of the Hours, Catechism lookup and documents, and the parish OCIA listing form. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var LG = document.documentElement.lang, ES = LG === 'es', PT = LG === 'pt', LOC = ES ? 'es-US' : PT ? 'pt-BR' : 'en-US';
  var T = function (en, es, pt) { return PT ? pt : ES ? es : en; };
  var P = ES ? '/es' : PT ? '/pt' : '';
  var esc = function (x) { return String(x == null ? '' : x).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var DAY = 86400000;
  function day(y, m, d) { return new Date(y, m, d); }
  function add(dt, n) { var r = new Date(dt); r.setDate(r.getDate() + n); return r; }
  function easter(y) {
    var a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4,
      f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3), h = (19 * a + b - d - g + 15) % 30,
      i = Math.floor(c / 4), k = c % 4, l = (32 + 2 * e + 2 * i - h - k) % 7,
      m = Math.floor((a + 11 * h + 22 * l) / 451), month = Math.floor((h + l - 7 * m + 114) / 31),
      dd = ((h + l - 7 * m + 114) % 31) + 1;
    return day(y, month - 1, dd);
  }
  var now = new Date(), today = day(now.getFullYear(), now.getMonth(), now.getDate());
  var fmt = function (d, o) { return d.toLocaleDateString(LOC, o || { month: 'long', day: 'numeric' }); };
  function isEaster(t) { var e = easter(t.getFullYear()); return t >= e && t <= add(e, 49); }

  /* ---------- Examination of conscience ---------- */
  var tabs = $$('[data-exam]');
  if (tabs.length) {
    var panels = $$('.exam-panel'), list = $('#exam-list'), out = $('#exam-out'), empty = $('#exam-empty');
    var current = function () { return panels.filter(function (p) { return !p.hidden; })[0]; };
    tabs.forEach(function (b) {
      b.addEventListener('click', function () {
        tabs.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        panels.forEach(function (p) { p.hidden = p.getAttribute('data-panel') !== b.getAttribute('data-exam'); });
        list.hidden = true;
      });
    });
    var show = function () {
      var picked = $$('input:checked', current()).map(function (i) { return i.value; });
      out.innerHTML = picked.map(function (v) { return '<li>' + esc(v) + '</li>'; }).join('');
      empty.hidden = picked.length > 0;
      list.hidden = false;
      list.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    $('#exam-show').addEventListener('click', show);
    $('#exam-print').addEventListener('click', function () { show(); window.print(); });
    $('#exam-clear').addEventListener('click', function () {
      $$('.exam-panel input').forEach(function (i) { i.checked = false; });
      out.innerHTML = ''; list.hidden = true;
    });
  }

  /* ---------- Novena dates ---------- */
  function novenaStart(code, y) {
    if (code.charAt(0) === 'E') return add(easter(y), parseInt(code.slice(1), 10));
    var p = code.split('-'); return day(y, +p[0] - 1, +p[1]);
  }
  function nextNovena(code) {
    var s = novenaStart(code, today.getFullYear());
    if (add(s, 8) < today) s = novenaStart(code, today.getFullYear() + 1);
    return s;
  }
  var novenas = $$('.novena[data-start]');
  novenas.forEach(function (n) {
    var s = nextNovena(n.getAttribute('data-start')), end = add(s, 8), lab = $('.novena-when', n);
    var dn = Math.round((today - s) / DAY) + 1;
    if (dn >= 1 && dn <= 9) {
      lab.textContent = T('Today is day ' + dn + ' of 9', 'Hoy es el día ' + dn + ' de 9', 'Hoje é o dia ' + dn + ' de 9');
      n.classList.add('today-mystery');
      var li = $$('.novena-days li', n)[dn - 1]; if (li) li.classList.add('today-day');
    } else {
      lab.textContent = fmt(s) + ' – ' + fmt(end, { month: 'long', day: 'numeric', year: 'numeric' });
    }
    n.setAttribute('data-sort', String(s.getTime()));
  });
  var ng = $('.novena-grid');
  if (ng && novenas.length) novenas.sort(function (a, b) { return a.getAttribute('data-sort') - b.getAttribute('data-sort'); }).forEach(function (n) { ng.appendChild(n); });

  /* ---------- Devotions: coming up ---------- */
  var cl = $('#coming-list');
  if (cl) {
    fetch(P + '/novenas').then(function (r) { return r.text(); }).then(function (h) {
      var doc = new DOMParser().parseFromString(h, 'text/html'), items = [];
      $$('.novena[data-start]', doc).forEach(function (n) {
        var s = nextNovena(n.getAttribute('data-start')), dn = Math.round((today - s) / DAY) + 1, title = $('h3', n).textContent;
        var href = P + '/novenas#' + n.id;
        if (dn >= 1 && dn <= 9) items.push([0, '<a href="' + href + '">' + esc(title) + '</a>: ' + T('today is day ', 'hoy es el día ', 'hoje é o dia ') + dn + T(' of 9', ' de 9', ' de 9')]);
        else if (dn < 1 && dn > -15) items.push([1 - dn, '<a href="' + href + '">' + esc(title) + '</a> ' + T('begins ', 'empieza el ', 'começa em ') + fmt(s)]);
      });
      var e = easter(today.getFullYear()), ash = add(e, -46);
      if (today >= ash && today < e) {
        var fri = add(today, (5 - today.getDay() + 7) % 7);
        if (fri < e) items.push([Math.round((fri - today) / DAY), '<a href="' + P + T('/stations-of-the-cross', '/via-crucis', '/via-sacra') + '">' + T('Stations of the Cross', 'Vía Crucis', 'Via-Sacra') + '</a>, ' + (fri.getTime() === today.getTime() ? T('today (Friday of Lent)', 'hoy (viernes de Cuaresma)', 'hoje (sexta-feira da Quaresma)') : fmt(fri, { weekday: 'long', month: 'long', day: 'numeric' }))]);
      }
      if (isEaster(today)) items.push([0, '<a href="' + P + '/angelus">Regina Caeli</a>: ' + T('prayed instead of the Angelus until Pentecost', 'se reza en lugar del Ángelus hasta Pentecostés', 'rezada no lugar do Angelus até Pentecostes')]);
      if (!items.length) return;
      items.sort(function (a, b) { return a[0] - b[0]; });
      cl.innerHTML = items.slice(0, 4).map(function (x) { return '<li>' + x[1] + '</li>'; }).join('');
      $('#coming-up').hidden = false;
    }).catch(function () {});
  }

  /* ---------- Reminder calendar links ---------- */
  var opts = $$('.rem-opts input');
  if (opts.length) {
    var upd = function () {
      var set = opts.filter(function (i) { return i.checked; }).map(function (i) { return i.value; });
      if (!set.length) set = ['angelus12'];
      var q = 'set=' + set.join(',') + (LG === 'en' ? '' : '&lang=' + LG);
      var https = 'https://catholicdoorway.com/api/devotions.ics?' + q, webcal = 'webcal://catholicdoorway.com/api/devotions.ics?' + q;
      $('#rem-apple').href = webcal;
      $('#rem-google').href = 'https://calendar.google.com/calendar/r?cid=' + encodeURIComponent(webcal);
      $('#rem-outlook').href = 'https://outlook.live.com/calendar/0/addfromweb?url=' + encodeURIComponent(https) + '&name=' + encodeURIComponent(T('Catholic prayer reminders', 'Recordatorios de oración', 'Lembretes de oração'));
    };
    opts.forEach(function (i) { i.addEventListener('change', upd); });
    upd();
    if (/Android/i.test(navigator.userAgent)) $('#rem-apple').hidden = true;
  }

  /* ---------- Angelus: which prayer now, and when next ---------- */
  var an = $('#angelus-now');
  if (an) {
    var easterTime = isEaster(today);
    $('#an-title').textContent = easterTime ? T('Regina Caeli (Easter season)', 'Regina Caeli (tiempo de Pascua)', 'Rainha do Céu (Tempo Pascal)') : T('The Angelus', 'El Ángelus', 'O Angelus');
    var h = now.getHours() + now.getMinutes() / 60, times = [6, 12, 18], next = null;
    for (var i = 0; i < times.length; i++) if (h < times[i]) { next = times[i]; break; }
    var label = function (t) { return t === 12 ? T('noon', 'el mediodía', 'meio-dia') : t === 6 ? T('6 a.m.', 'las 6 de la mañana', '6 da manhã') : T('6 p.m.', 'las 6 de la tarde', '6 da tarde'); };
    $('#an-next').textContent = next === null
      ? T('Next: tomorrow at 6 a.m.', 'La próxima vez: mañana a las 6 de la mañana.', 'Próxima vez: amanhã às 6 da manhã.')
      : T('Next: today at ' + label(next) + '.', 'La próxima vez: hoy a ' + label(next) + '.', 'Próxima vez: hoje ' + (next === 12 ? 'ao ' : 'às ') + label(next) + '.');
    var rc = $('#regina-caeli'), ag = $('#angelus');
    if (easterTime && rc && ag) { rc.classList.add('today-mystery'); rc.parentNode.insertBefore(rc, ag); }
    else if (ag) ag.classList.add('today-mystery');
  }

  /* ---------- Liturgy of the Hours: today's links and the hour that fits now ---------- */
  var hn = $('#hours-now');
  if (hn) {
    $('#hn-date').textContent = today.toLocaleDateString(LOC, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
    var ymd = today.getFullYear() + ('0' + (today.getMonth() + 1)).slice(-2) + ('0' + today.getDate()).slice(-2);
    var hr = now.getHours();
    var want = hr < 11 ? 0 : hr < 20 ? 1 : 2, btns = $$('[data-hour]', hn);
    btns.forEach(function (b, i) {
      if (LG === 'en') b.href = 'https://universalis.com/' + ymd + '/' + b.getAttribute('data-hour') + '.htm';
      b.classList.toggle('secondary', i !== want);
    });
    $('#hn-label').textContent = [T('Good morning', 'Buenos días', 'Bom dia'), T('This evening', 'Esta tarde', 'Esta tarde'), T('Before you sleep', 'Antes de dormir', 'Antes de dormir')][want];
  }

  /* ---------- Catechism lookup ---------- */
  var cf = $('#ccc-form');
  if (cf) {
    var cmap = JSON.parse(cf.getAttribute('data-map'));
    var cccUrl = function (n) {
      var page = null;
      for (var i = 0; i < cmap.map.length; i++) if (cmap.map[i][0] <= n) page = cmap.map[i][1];
      return cmap.base + page + cmap.ext + '#:~:text=' + n;
    };
    var go = function (n) {
      if (!(n >= 1 && n <= 2865)) { $('#ccc-msg').textContent = T('Please enter a number from 1 to 2865.', 'Escribe un número del 1 al 2865.', 'Digite um número de 1 a 2865.'); return; }
      window.open(cccUrl(n), '_blank', 'noopener');
    };
    cf.addEventListener('submit', function (e) { e.preventDefault(); go(parseInt($('#ccc-num').value, 10)); });
  }

  /* ---------- Documents filter ---------- */
  var dl = $('#doc-list');
  if (dl) {
    var docs = $$('.doc', dl), ds = $('#doc-search'), dt = $('#doc-topic'), kind = 'all';
    var fold = function (x) { return (x || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); };
    var run = function () {
      var terms = fold(ds.value).split(/\s+/).filter(Boolean), tp = dt.value, n = 0;
      docs.forEach(function (d) {
        var hay = fold(d.textContent), ok = (kind === 'all' || d.getAttribute('data-kind') === kind) &&
          (!tp || (' ' + d.getAttribute('data-topics') + ' ').indexOf(' ' + tp + ' ') > -1) &&
          terms.every(function (t) { return hay.indexOf(t) > -1; });
        d.hidden = !ok; if (ok) n++;
      });
      $('#doc-empty').hidden = n > 0;
    };
    $$('[data-dkind]').forEach(function (b) {
      b.addEventListener('click', function () {
        kind = b.getAttribute('data-dkind');
        $$('[data-dkind]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        run();
      });
    });
    ds.addEventListener('input', run); dt.addEventListener('change', run);
  }

  /* ---------- Parish OCIA listing form ---------- */
  var of = $('#ocia-form');
  if (of) {
    var started = Date.now(), msg = $('#ocia-msg');
    var say = function (text, bad) { msg.textContent = text; msg.classList.toggle('error', !!bad); };
    var mailto = function (data) {
      var body = Object.keys(data).filter(function (k) { return data[k] && k !== 't' && k !== 'consent' && k !== 'lang'; })
        .map(function (k) { return k + ': ' + (Array.isArray(data[k]) ? data[k].join(', ') : data[k]); }).join('\n');
      return 'mailto:hello@catholicdoorway.com?subject=' + encodeURIComponent('OCIA listing: ' + (data.parish || '')) + '&body=' + encodeURIComponent(body);
    };
    of.addEventListener('submit', function (e) {
      e.preventDefault();
      var fd = new FormData(of), data = {};
      fd.forEach(function (v, k) { if (k === 'langs') (data.langs = data.langs || []).push(v); else data[k] = String(v).trim(); });
      data.consent = !!of.elements.consent.checked; data.t = started; data.lang = LG;
      var miss = ['parish', 'city', 'state', 'contact', 'email'].filter(function (k) { return !data[k]; });
      $$('.ocia-form [aria-invalid]').forEach(function (x) { x.removeAttribute('aria-invalid'); });
      miss.forEach(function (k) { of.elements[k].setAttribute('aria-invalid', 'true'); });
      if (miss.length) { of.elements[miss[0]].focus(); return say(T('Please fill in the fields marked *.', 'Completa los campos marcados con *.', 'Preencha os campos marcados com *.'), true); }
      if (!data.consent) return say(T('Please tick the box to confirm the parish agrees.', 'Marca la casilla para confirmar que la parroquia está de acuerdo.', 'Marque a caixa para confirmar que a paróquia concorda.'), true);
      var btn = $('button[type=submit]', of); btn.disabled = true;
      say(T('Sending…', 'Enviando…', 'Enviando…'));
      fetch('/api/ocia-listing', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { return [r.status, j]; }); })
        .then(function (res) {
          btn.disabled = false;
          var j = res[1];
          if (j.ok) {
            of.reset();
            return say(T('Thank you! We received your listing and will check it with your parish before it appears here.', '¡Gracias! Recibimos tu registro y lo confirmaremos con tu parroquia antes de publicarlo.', 'Obrigado! Recebemos o seu cadastro e vamos confirmá-lo com a sua paróquia antes de publicá-lo.'));
          }
          if (res[0] === 503) {
            msg.innerHTML = esc(T('Online listings open soon. For now, please send it by email:', 'Los registros en línea abrirán pronto. Por ahora, envíalo por correo:', 'Os cadastros on-line abrem em breve. Por enquanto, envie por e-mail:')) + ' <a href="' + esc(mailto(data)) + '">hello@catholicdoorway.com</a>';
            return;
          }
          if (j.error === 'too_many') return say(T('Too many tries. Please wait an hour and try again.', 'Demasiados intentos. Espera una hora y vuelve a intentarlo.', 'Muitas tentativas. Espere uma hora e tente de novo.'), true);
          (j.fields || []).forEach(function (k) { if (of.elements[k]) of.elements[k].setAttribute('aria-invalid', 'true'); });
          say(T('Please check the highlighted fields.', 'Revisa los campos marcados.', 'Confira os campos destacados.'), true);
        })
        .catch(function () { btn.disabled = false; msg.innerHTML = esc(T('Something went wrong. You can also email it to', 'Algo salió mal. También puedes enviarlo a', 'Algo deu errado. Você também pode enviar para')) + ' <a href="' + esc(mailto(data)) + '">hello@catholicdoorway.com</a>.'; });
    });

    var ol = $('#ol-list'), ost = $('#ol-state'), rows = [];
    var LN = { en: T('English', 'Inglés', 'Inglês'), es: T('Spanish', 'Español', 'Espanhol'), pt: T('Portuguese', 'Portugués', 'Português'), other: T('Other languages', 'Otros idiomas', 'Outros idiomas') };
    var draw = function () {
      var st = ost.value, list = rows.filter(function (r) { return !st || r.state === st; });
      if (!list.length) { ol.innerHTML = '<p class="muted">' + T('No parishes listed here yet. Find any parish on the ', 'Todavía no hay parroquias registradas aquí. Busca cualquier parroquia en el ', 'Ainda não há paróquias cadastradas aqui. Procure qualquer paróquia no ') + '<a href="' + P + T('/find-a-church?ocia=1', '/buscar-iglesia?ocia=1', '/encontrar-igreja?ocia=1') + '">' + T('map', 'mapa', 'mapa') + '</a>.</p>'; return; }
      ol.innerHTML = list.map(function (r) {
        var lines = [];
        if (r.contact) lines.push(esc(r.contact) + (r.role ? ', ' + esc(r.role) : ''));
        var c = [];
        if (r.email) c.push('<a href="mailto:' + esc(r.email) + '">' + esc(r.email) + '</a>');
        if (r.phone) c.push('<a href="tel:' + esc(r.phone.replace(/[^\d+]/g, '')) + '">' + esc(r.phone) + '</a>');
        if (r.website && /^https?:\/\//.test(r.website)) c.push('<a href="' + esc(r.website) + '" target="_blank" rel="noopener">' + T('Website', 'Sitio web', 'Site') + '</a>');
        if (c.length) lines.push(c.join(' &middot; '));
        if (r.schedule) lines.push(esc(r.schedule));
        if (r.start) lines.push(esc(r.start));
        if (r.langs && r.langs.length) lines.push(r.langs.map(function (l) { return LN[l] || l; }).join(', '));
        if (r.notes) lines.push('<span class="muted">' + esc(r.notes) + '</span>');
        return '<article class="card"><h3>' + esc(r.parish) + '</h3><p class="small muted">' + esc(r.city) + ', ' + esc(r.state) + (r.diocese ? ' &middot; ' + esc(r.diocese) : '') + '</p><p>' + lines.join('<br>') + '</p></article>';
      }).join('');
    };
    fetch('/api/ocia-listings.json').then(function (r) { return r.json(); }).then(function (d) {
      rows = d.listings || [];
      var states = rows.map(function (r) { return r.state; }).filter(function (s, i, a) { return s && a.indexOf(s) === i; }).sort();
      states.forEach(function (s) { var o = document.createElement('option'); o.value = s; o.textContent = s; ost.appendChild(o); });
      ost.addEventListener('change', draw);
      draw();
    }).catch(function () { rows = []; draw(); });
  }
})();
