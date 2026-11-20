/* CatholicDoorway: Watch Mass Online.
   Shows each broadcast's Mass times in the visitor's own time zone, filters by language,
   lists parish livestreams (reviewed listings) with "report broken link", and sends the
   "add your livestream" form. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var LG = document.documentElement.lang, ES = LG === 'es', PT = LG === 'pt', TL = LG === 'tl';
  var LOC = ES ? 'es-US' : PT ? 'pt-BR' : TL ? 'fil-PH' : 'en-US';
  var T = function (en, es, pt, tl) { return TL ? (tl || en) : PT ? (pt || en) : ES ? es : en; };
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  };
  var root = $('.watch');
  if (!root) return;
  var L = {}; try { L = JSON.parse(root.getAttribute('data-labels') || '{}'); } catch (e) {}
  var HERE = 'UTC';
  try { HERE = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'; } catch (e) {}

  /* ---------- Time zones ---------- */
  function parts(ts, tz) {
    var o = {};
    new Intl.DateTimeFormat('en-US', { timeZone: tz, hourCycle: 'h23', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric', weekday: 'short' })
      .formatToParts(new Date(ts)).forEach(function (p) { o[p.type] = p.value; });
    return { y: +o.year, m: +o.month, d: +o.day, h: +o.hour % 24, mi: +o.minute, wd: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(o.weekday) };
  }
  function offset(ts, tz) { var p = parts(ts, tz); return Date.UTC(p.y, p.m - 1, p.d, p.h, p.mi) - Math.floor(ts / 60000) * 60000; }
  // The moment when it is y-m-d h:mi on the wall clocks of tz.
  function at(y, m, d, h, mi, tz) {
    var guess = Date.UTC(y, m - 1, d, h, mi);
    var t = guess - offset(guess, tz);
    return guess - offset(t, tz);
  }
  var fmtTime = new Intl.DateTimeFormat(LOC, { hour: 'numeric', minute: '2-digit' });
  var fmtDay = new Intl.DateTimeFormat(LOC, { weekday: 'short' });
  var fmtLong = new Intl.DateTimeFormat(LOC, { weekday: 'long' });
  var tzLabel = HERE;
  try {
    var tn = new Intl.DateTimeFormat(LOC, { timeZoneName: 'long' }).formatToParts(new Date()).filter(function (p) { return p.type === 'timeZoneName'; })[0];
    if (tn) tzLabel = tn.value;
  } catch (e) {}
  $$('.tz-name').forEach(function (el) { el.textContent = ' (' + tzLabel + ')'; });

  // Every start in the next 8 days, as [utc ms, group index].
  function instances(sched, tz, now) {
    var out = [], p0 = parts(now - 86400000, tz);
    for (var i = 0; i < 9; i++) {
      var noon = at(p0.y, p0.m, p0.d, 12, 0, tz) + i * 86400000, p = parts(noon, tz);
      sched.forEach(function (g, gi) {
        if (g.d.indexOf(p.wd) < 0) return;
        g.t.forEach(function (hm) { var a = hm.split(':'); out.push([at(p.y, p.m, p.d, +a[0], +a[1], tz), gi]); });
      });
    }
    return out.sort(function (a, b) { return a[0] - b[0]; });
  }
  function dayWord(ts, now) {
    var a = parts(ts, HERE), b = parts(now, HERE);
    var da = Date.UTC(a.y, a.m - 1, a.d), db = Date.UTC(b.y, b.m - 1, b.d), n = Math.round((da - db) / 86400000);
    if (n === 0) return T('today', 'hoy', 'hoje', 'ngayon');
    if (n === 1) return T('tomorrow', 'mañana', 'amanhã', 'bukas');
    return fmtLong.format(new Date(ts));
  }

  function drawCard(card, now) {
    var sched; try { sched = JSON.parse(card.getAttribute('data-sched') || '[]'); } catch (e) { sched = []; }
    var box = $('.stream-times', card), tz = card.getAttribute('data-tz');
    if (!sched.length) { box.innerHTML = ''; return; }
    var SHIFT = { 1: T('next day', 'día siguiente', 'dia seguinte', 'kinabukasan'), '-1': T('day before', 'día anterior', 'dia anterior', 'isang araw bago') };
    var today = parts(now, tz);
    var rows = sched.map(function (g) {
      // A sample day for this group (the next one, counting today), with all its starts.
      var sample = null;
      for (var i = 0; i < 8 && !sample; i++) {
        var p = parts(at(today.y, today.m, today.d, 12, 0, tz) + i * 86400000, tz);
        if (g.d.indexOf(p.wd) >= 0) sample = p;
      }
      if (!sample) return '';
      var single = g.d.length === 1, times = [];
      g.t.forEach(function (hm) {
        var a = hm.split(':'), ts = at(sample.y, sample.m, sample.d, +a[0], +a[1], tz), loc = parts(ts, HERE);
        var shift = Math.round((Date.UTC(loc.y, loc.m - 1, loc.d) - Date.UTC(sample.y, sample.m - 1, sample.d)) / 86400000);
        var label = fmtTime.format(new Date(ts));
        if (shift && single) label = fmtDay.format(new Date(ts)) + ' ' + label;
        else if (shift && g.d.length < 7) label += ' (' + SHIFT[shift] + ')';
        times.push([(g.d.length < 7 ? shift * 1440 : 0) + loc.h * 60 + loc.mi, label]);
      });
      times.sort(function (a, b) { return a[0] - b[0]; });
      return '<li><strong>' + esc(g.k) + ':</strong> ' + times.map(function (x) { return esc(x[1]); }).join(', ') + '</li>';
    });
    var all = instances(sched, tz, now), live = null, next = null;
    all.forEach(function (x) {
      if (!live && x[0] <= now && now < x[0] + 60 * 60000) live = x;
      if (!next && x[0] > now) next = x;
    });
    var status = live
      ? '<p class="stream-next live"><span class="badge">' + esc(L.on_now || 'On now') + '</span> ' + esc(fmtTime.format(new Date(live[0]))) + '</p>'
      : next ? '<p class="stream-next"><strong>' + esc(L.next_ || 'Next') + ':</strong> ' + esc(dayWord(next[0], now)) + ', ' + esc(fmtTime.format(new Date(next[0]))) + '</p>' : '';
    box.innerHTML = '<p class="small stream-your">' + esc(L.your || 'your time') + ' (' + esc(tzLabel) + ')</p><ul class="stream-list">' + rows.join('') + '</ul>' + status;
  }
  function drawAll() { var now = Date.now(); $$('.card.stream').forEach(function (c) { drawCard(c, now); }); }
  try { drawAll(); setInterval(drawAll, 60000); } catch (e) {}

  /* ---------- Language filter ---------- */
  $$('[data-slang]').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.getAttribute('data-slang');
      $$('[data-slang]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      $$('.card.stream').forEach(function (c) { c.hidden = v !== 'all' && (' ' + c.getAttribute('data-langs') + ' ').indexOf(' ' + v + ' ') < 0; });
    });
  });

  /* ---------- Parish livestreams ---------- */
  var list = $('#ps-list'), sel = $('#ps-state'), rows = [];
  var MAP = TL ? '/tl/hanapin-ang-simbahan?stream=1' : PT ? '/pt/encontrar-igreja?stream=1' : ES ? '/es/buscar-iglesia?stream=1' : '/find-a-church?stream=1';
  var fmtDate = function (d) {
    if (!d) return '';
    try { return new Intl.DateTimeFormat(LOC, { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' }).format(new Date(d + 'T12:00:00Z')); } catch (e) { return d; }
  };
  var host = function (u) { try { return new URL(u).hostname.replace(/^www\.|^m\./, ''); } catch (e) { return ''; } };
  function draw() {
    if (!list) return;
    var st = sel.value, shown = rows.filter(function (r) { return !st || r.state === st; });
    if (!shown.length) {
      list.innerHTML = '<p class="muted">' + T('No parish livestreams are listed here yet. If your parish streams its Masses, ', 'Todavía no hay transmisiones de parroquias aquí. Si tu parroquia transmite sus Misas, ',
        'Ainda não há transmissões de paróquias aqui. Se a sua paróquia transmite as Missas, ', 'Wala pang nakalistang livestream ng parokya rito. Kung nagla-livestream ng Misa ang inyong parokya, ') +
        '<a href="#add-stream">' + T('add it below', 'añádela abajo', 'cadastre abaixo', 'idagdag sa ibaba') + '</a>.</p>';
      return;
    }
    list.innerHTML = shown.map(function (r) {
      var h = host(r.stream);
      return '<article class="card parish-stream" data-id="' + esc(r.id) + '"><h3>' + esc(r.parish) + '</h3>' +
        '<p class="small muted">' + esc(r.city) + ', ' + esc(r.state) + (r.diocese ? ' &middot; ' + esc(r.diocese) : '') + '</p>' +
        (r.stream_times ? '<p>' + esc(r.stream_times) + '</p>' : '') +
        '<div class="actions"><a class="btn small" href="' + esc(r.stream) + '" target="_blank" rel="noopener nofollow ugc">' + T('Watch', 'Ver', 'Assistir', 'Manood') + (h ? ' <span class="small">(' + esc(h) + ')</span>' : '') + '</a>' +
        '<button type="button" class="btn small secondary report-btn">' + T('Report broken link', 'Avisar de un enlace roto', 'Avisar link quebrado', 'Iulat ang sirang link') + '</button></div>' +
        '<p class="small muted stream-check">' + T('Link last checked', 'Enlace revisado el', 'Link conferido em', 'Huling sinuri ang link noong') + ' ' + esc(fmtDate(r.checked || r.approved)) + '</p></article>';
    }).join('');
  }
  if (list) {
    list.addEventListener('click', function (e) {
      var b = e.target.closest('.report-btn');
      if (!b) return;
      var card = b.closest('[data-id]');
      b.disabled = true;
      fetch('/api/stream-report', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: card.getAttribute('data-id') }) })
        .then(function (r) { return r.ok; }).catch(function () { return false; })
        .then(function (ok) {
          b.textContent = ok ? T('Thanks, we’ll check it', 'Gracias, lo revisaremos', 'Obrigado, vamos verificar', 'Salamat, titingnan namin')
            : T('Could not send. Please email hello@catholicdoorway.com', 'No se pudo enviar. Escribe a hello@catholicdoorway.com', 'Não foi possível enviar. Escreva para hello@catholicdoorway.com', 'Hindi naipadala. Mag-email sa hello@catholicdoorway.com');
        });
    });
    fetch('/api/ocia-listings.json').then(function (r) { return r.json(); }).then(function (d) {
      rows = (d.listings || []).filter(function (r) { return r.stream && /^https:\/\//.test(r.stream); });
      rows.forEach(function (r) { if (!r.id) r.id = ''; });
      var states = rows.map(function (r) { return r.state; }).filter(function (s, i, a) { return s && a.indexOf(s) === i; }).sort();
      states.forEach(function (s) { var o = document.createElement('option'); o.value = s; o.textContent = s; sel.appendChild(o); });
      sel.addEventListener('change', draw);
      draw();
    }).catch(function () { rows = []; draw(); });
  }

  /* ---------- Add your livestream ---------- */
  var f = $('#stream-form');
  if (f) {
    var started = Date.now(), msg = $('#stream-msg');
    var say = function (text, bad) { msg.textContent = text; msg.classList.toggle('error', !!bad); };
    var mailto = function (data) {
      var body = ['parish', 'city', 'state', 'stream', 'stream_times', 'contact', 'email'].filter(function (k) { return data[k]; }).map(function (k) { return k + ': ' + data[k]; }).join('\n');
      return 'mailto:hello@catholicdoorway.com?subject=' + encodeURIComponent('Parish livestream: ' + (data.parish || '')) + '&body=' + encodeURIComponent(body);
    };
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var data = {};
      new FormData(f).forEach(function (v, k) { data[k] = String(v).trim(); });
      data.consent = !!f.elements.consent.checked; data.t = started; data.lang = LG; data.kind = 'stream';
      if (data.stream && !/^https?:\/\//i.test(data.stream)) data.stream = 'https://' + data.stream;
      var miss = ['parish', 'city', 'state', 'stream', 'contact', 'email'].filter(function (k) { return !data[k]; });
      $$('#stream-form [aria-invalid]').forEach(function (x) { x.removeAttribute('aria-invalid'); });
      miss.forEach(function (k) { f.elements[k].setAttribute('aria-invalid', 'true'); });
      if (miss.length) { f.elements[miss[0]].focus(); return say(T('Please fill in the fields marked *.', 'Completa los campos marcados con *.', 'Preencha os campos marcados com *.', 'Pakipunan ang mga patlang na may markang *.'), true); }
      if (!data.consent) return say(T('Please tick the box to confirm the parish agrees.', 'Marca la casilla para confirmar que la parroquia está de acuerdo.', 'Marque a caixa para confirmar que a paróquia concorda.', 'Pakimarkahan ang kahon upang kumpirmahing pumapayag ang parokya.'), true);
      var btn = $('button[type=submit]', f); btn.disabled = true;
      say(T('Sending…', 'Enviando…', 'Enviando…', 'Ipinapadala…'));
      fetch('/api/ocia-listing', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { return [r.status, j]; }); })
        .then(function (res) {
          btn.disabled = false;
          var j = res[1];
          if (j.ok) { f.reset(); return say(T('Thank you! We received your link and will check it with your parish before it appears here.', '¡Gracias! Recibimos su enlace y lo confirmaremos con la parroquia antes de publicarlo.', 'Obrigado! Recebemos o link e vamos confirmá-lo com a paróquia antes de publicá-lo.', 'Salamat! Natanggap namin ang link at kukumpirmahin namin ito sa parokya bago ilathala.')); }
          if (res[0] === 503) { msg.innerHTML = esc(T('Online listings open soon. For now, please send it by email:', 'Los registros en línea abrirán pronto. Por ahora, envíelo por correo:', 'Os cadastros on-line abrem em breve. Por enquanto, envie por e-mail:', 'Malapit nang magbukas ang online na listahan. Sa ngayon, ipadala ito sa email:')) + ' <a href="' + esc(mailto(data)) + '">hello@catholicdoorway.com</a>'; return; }
          if (j.error === 'too_many') return say(T('Too many tries. Please wait an hour and try again.', 'Demasiados intentos. Espere una hora y vuelva a intentarlo.', 'Muitas tentativas. Espere uma hora e tente de novo.', 'Masyadong maraming subok. Maghintay ng isang oras at subukang muli.'), true);
          (j.fields || []).forEach(function (k) { if (f.elements[k]) f.elements[k].setAttribute('aria-invalid', 'true'); });
          say(T('Please check the highlighted fields.', 'Revise los campos marcados.', 'Confira os campos destacados.', 'Pakisuri ang mga naka-highlight na patlang.'), true);
        })
        .catch(function () { btn.disabled = false; msg.innerHTML = esc(T('Something went wrong. You can also email it to', 'Algo salió mal. También puede enviarlo a', 'Algo deu errado. Você também pode enviar para', 'May nangyaring mali. Maaari rin itong i-email sa')) + ' <a href="' + esc(mailto(data)) + '">hello@catholicdoorway.com</a>.'; });
    });
  }
})();
