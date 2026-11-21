/* CatholicDoorway: Prayer Wall.
   Lists the published prayer requests (/api/prayers.json) with an "I prayed" button and count,
   filters them by language, and sends the "ask for prayer" form (/api/prayer-request).
   The ids you have prayed for are remembered on this device (localStorage cd-prayed) so the
   button stays marked; the server also counts one prayer per visitor per request per day. */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var root = $('.prayer-wall');
  if (!root) return;
  var LG = document.documentElement.lang;
  var L = {}; try { L = JSON.parse(root.getAttribute('data-labels') || '{}'); } catch (e) {}
  var esc = function (s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  };
  var fill = function (s, n) { return String(s || '').replace('{n}', n); };
  var KEY = 'cd-prayed';
  var prayed = {};
  try { prayed = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) {}
  var savePrayed = function () {
    var cut = Date.now() - 31 * 86400000;
    Object.keys(prayed).forEach(function (k) { if (prayed[k] < cut) delete prayed[k]; });
    try { localStorage.setItem(KEY, JSON.stringify(prayed)); } catch (e) {}
  };

  /* ---------- The wall ---------- */
  var list = $('#pw-list'), moreBtn = $('#pw-more'), rows = [], lang = 'all', shown = 20;
  var count = function (n) { return n === 0 ? L.n0 : n === 1 ? L.n1 : fill(L.nn, n); };
  var ago = function (d) {
    if (!d) return '';
    var n = Math.floor((Date.now() - Date.parse(d + 'T12:00:00Z')) / 86400000);
    return n <= 0 ? L.today : n === 1 ? L.yday : fill(L.days, n);
  };
  function card(r) {
    var done = !!prayed[r.id];
    return '<article class="card pw-card" data-id="' + esc(r.id) + '" lang="' + esc(r.lang) + '">' +
      '<p class="pw-text">' + esc(r.text) + '</p>' +
      '<p class="small muted pw-meta"><strong>' + esc(r.name || L.anon) + '</strong> &middot; ' + esc(ago(r.sent || r.date)) +
      (r.lang !== LG && L.lang && L.lang[r.lang] ? ' &middot; ' + esc(L.lang[r.lang]) : '') + '</p>' +
      '<div class="pw-actions"><button type="button" class="btn small pw-pray' + (done ? ' done' : '') + '" aria-pressed="' + done + '"' + (done ? ' disabled' : '') + '>' +
      '<span aria-hidden="true">&#128591;</span> ' + esc(done ? L.thanks : L.prayed) + '</button>' +
      '<span class="small pw-count" aria-live="polite">' + esc(count(r.count || 0)) + '</span></div></article>';
  }
  function draw() {
    var pick = rows.filter(function (r) { return lang === 'all' || r.lang === lang; });
    if (!pick.length) { list.innerHTML = '<p class="muted">' + esc(L.empty) + ' <a href="#ask">&darr;</a></p>'; moreBtn.hidden = true; return; }
    list.innerHTML = pick.slice(0, shown).map(card).join('');
    moreBtn.hidden = pick.length <= shown;
  }
  $$('[data-plang]').forEach(function (b) {
    b.addEventListener('click', function () {
      lang = b.getAttribute('data-plang'); shown = 20;
      $$('[data-plang]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      draw();
    });
  });
  moreBtn.addEventListener('click', function () { shown += 20; draw(); });
  list.addEventListener('click', function (e) {
    var b = e.target.closest('.pw-pray');
    if (!b || b.disabled) return;
    var c = b.closest('[data-id]'), id = c.getAttribute('data-id');
    var r = rows.filter(function (x) { return x.id === id; })[0];
    b.disabled = true; b.classList.add('done'); b.setAttribute('aria-pressed', 'true');
    b.innerHTML = '<span aria-hidden="true">&#128591;</span> ' + esc(L.thanks);
    prayed[id] = Date.now(); savePrayed();
    if (r) { r.count = (r.count || 0) + 1; $('.pw-count', c).textContent = count(r.count); }
    fetch('/api/prayer-pray', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: id }) })
      .then(function (res) { return res.json(); })
      .then(function (j) { if (j && j.ok && r && j.count > r.count) { r.count = j.count; $('.pw-count', c).textContent = count(r.count); } })
      .catch(function () {});
  });
  fetch('/api/prayers.json').then(function (r) { return r.json(); }).then(function (d) {
    rows = d.prayers || [];
    // Requests in the visitor's language first, newest first within each.
    rows.forEach(function (r, i) { r._i = i; });
    rows.sort(function (a, b) { return ((a.lang === LG ? 0 : 1) - (b.lang === LG ? 0 : 1)) || a._i - b._i; });
    draw();
  }).catch(function () { rows = []; draw(); });

  /* ---------- Ask for prayer ---------- */
  var f = $('#prayer-form');
  if (!f) return;
  var started = Date.now(), msg = $('#prayer-msg'), left = $('#pw-left'), cbox = $('#pw-crisis');
  var CRISIS = /\b(suicid\w*|kill (my ?self|me)|end(ing)? my (own )?life|want(ed)? to die|wanna die|self[- ]?harm|hurt(ing)? my ?self|cutting myself|overdos\w*|quitarme la vida|matarme|me quiero morir|quiero morir(me)?|no quiero vivir|tirar (a )?minha (própria )?vida|me matar|quero morrer|não quero mais viver|magpakamatay|nagpapakamatay|gusto ko nang mamatay|ayoko nang mabuhay|saktan ang sarili)\b/i;
  var say = function (text, bad, html) { if (html) msg.innerHTML = html; else msg.textContent = text; msg.classList.toggle('error', !!bad); };
  var showCrisis = function (on) {
    cbox.hidden = !on;
    if (on) $('p', cbox).innerHTML = esc(L.crisis_seen) + ' <a href="#crisis">&uarr;</a>';
  };
  var ta = f.elements.text;
  var onType = function () {
    var n = 500 - ta.value.length;
    left.textContent = n < 120 ? fill(L.left, n) : '';
    showCrisis(CRISIS.test(ta.value));
  };
  ta.addEventListener('input', onType);
  var mailto = function (data) {
    return 'mailto:hello@catholicdoorway.com?subject=' + encodeURIComponent('Prayer request' + (data.name ? ': ' + data.name : '')) + '&body=' + encodeURIComponent(data.text || '');
  };
  var ERR = { text: 'e_text', long: 'e_long', link: 'e_link', contact: 'e_contact', name: 'e_name' };
  f.addEventListener('submit', function (e) {
    e.preventDefault();
    var data = { name: f.elements.name.value.trim(), text: ta.value.trim(), website2: f.elements.website2.value, private: !!f.elements['private'].checked, t: started, lang: LG };
    $$('#prayer-form [aria-invalid]').forEach(function (x) { x.removeAttribute('aria-invalid'); });
    if (data.text.length < 8) { ta.setAttribute('aria-invalid', 'true'); ta.focus(); return say(L.e_text, true); }
    var btn = $('button[type=submit]', f); btn.disabled = true;
    say(L.sending);
    fetch('/api/prayer-request', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().then(function (j) { return [r.status, j]; }); })
      .then(function (res) {
        btn.disabled = false;
        var j = res[1] || {};
        if (j.ok) {
          var crisis = CRISIS.test(data.text);
          f.reset(); left.textContent = '';
          say(data['private'] ? L.ok_private : L.ok);
          showCrisis(crisis);
          return;
        }
        if (res[0] === 503) return say('', true, esc(L.e_ready) + ' <a href="' + esc(mailto(data)) + '">hello@catholicdoorway.com</a>.');
        if (j.error === 'too_many') return say(L.e_many, true);
        var fields = j.fields || [];
        if (fields.indexOf('name') >= 0) f.elements.name.setAttribute('aria-invalid', 'true');
        if (fields.some(function (k) { return k !== 'name'; })) ta.setAttribute('aria-invalid', 'true');
        say(fields.map(function (k) { return L[ERR[k]]; }).filter(Boolean).join(' ') || L.e_fail, true);
      })
      .catch(function () { btn.disabled = false; say('', true, esc(L.e_fail) + ' <a href="' + esc(mailto(data)) + '">hello@catholicdoorway.com</a>.'); });
  });
})();
