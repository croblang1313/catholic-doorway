/* CatholicDoorway saints and causes directory. Data: Wikidata (CC0), refreshed weekly. */
(function () {
  'use strict';
  var list = document.getElementById('sd-list');
  if (!list) return;
  var $ = function (id) { return document.getElementById(id); };
  var q = $('sd-q'), st = $('sd-status'), ct = $('sd-country'), cy = $('sd-century'), so = $('sd-sort'), more = $('sd-more'), count = $('sd-count');
  var LABEL = { 4: 'Saint', 3: 'Blessed', 2: 'Venerable', 1: 'Servant of God' };
  var CLS = { 4: 's-saint', 3: 's-blessed', 2: 's-venerable', 1: 's-servant' };
  var DECREE = { 4: 'canonized', 3: 'beatified', 2: 'declared Venerable', 1: 'cause opened' };
  var people = [], shown = 0, filtered = [], PAGE = 50;

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function century(y) {
    if (!y) return '';
    var c = y > 0 ? Math.floor((y - 1) / 100) + 1 : 0;
    return c;
  }
  function ord(n) { var s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
  function fmtYear(y) { return y < 0 ? (-y) + ' BC' : String(y); }
  function life(p) {
    if (p.born && p.died) return fmtYear(p.born) + '–' + fmtYear(p.died);
    if (p.died) return 'Died ' + fmtYear(p.died);
    if (p.born) return 'Born ' + fmtYear(p.born);
    return '';
  }

  function load() {
    fetch('/data/saints-directory.json').then(function (r) { return r.json(); }).then(function (d) {
      people = d.people.map(function (a) {
        var p = { id: a[0], name: a[1], alt: a[2], desc: a[3], rank: a[4], when: a[5], born: a[6], died: a[7],
          countries: a[8] ? a[8].split('|') : [], patron: a[9] ? a[9].split('|') : [], feast: a[10], wiki: a[11] };
        p.cent = century(p.died || p.born);
        p.hay = (p.name + ' ' + p.alt + ' ' + p.desc + ' ' + p.countries.join(' ') + ' ' + p.patron.join(' ')).toLowerCase();
        return p;
      });
      var cc = {}, cents = {};
      people.forEach(function (p) {
        p.countries.forEach(function (c) { cc[c] = (cc[c] || 0) + 1; });
        if (p.cent) cents[p.cent] = 1;
      });
      Object.keys(cc).filter(function (c) { return cc[c] >= 3; }).sort().forEach(function (c) {
        var o = document.createElement('option'); o.value = c; o.textContent = c + ' (' + cc[c] + ')'; ct.appendChild(o);
      });
      Object.keys(cents).map(Number).sort(function (a, b) { return a - b; }).forEach(function (c) {
        var o = document.createElement('option'); o.value = c; o.textContent = ord(c) + ' century'; cy.appendChild(o);
      });
      var n = d.counts || {};
      $('sd-updated').textContent = 'Updated ' + d.updated + ': ' + (n.saints || 0).toLocaleString() + ' Saints, ' + (n.blessed || 0).toLocaleString() + ' Blesseds, ' +
        (n.venerable || 0).toLocaleString() + ' Venerables and ' + (n.servants || 0).toLocaleString() + ' Servants of God. ' + d.license;
      var params = new URLSearchParams(location.search);
      if (params.get('q')) q.value = params.get('q');
      if (params.get('status')) st.value = params.get('status');
      if (params.get('sort')) so.value = params.get('sort');
      run();
    }).catch(function () { count.textContent = 'The directory could not load. Please refresh the page.'; });
  }

  function run() {
    var terms = q.value.toLowerCase().trim().split(/\s+/).filter(Boolean), s = +st.value, c = ct.value, ce = +cy.value || 0;
    filtered = people.filter(function (p) {
      if (s && p.rank !== s) return false;
      if (c && p.countries.indexOf(c) < 0) return false;
      if (ce && p.cent !== ce) return false;
      for (var i = 0; i < terms.length; i++) if (p.hay.indexOf(terms[i]) < 0) return false;
      return true;
    });
    if (so.value === 'recent') filtered = filtered.filter(function (p) { return p.when; }).sort(function (a, b) { return b.when - a.when || b.rank - a.rank; });
    else if (so.value === 'died') filtered.sort(function (a, b) { return (a.died || 9999) - (b.died || 9999); });
    list.innerHTML = ''; shown = 0;
    count.textContent = filtered.length ? filtered.length.toLocaleString() + (filtered.length === 1 ? ' person' : ' people') + (so.value === 'recent' ? ' with a recorded decree date, newest first.' : '.') : 'No one matches. Try fewer words or a different filter.';
    page();
  }

  function page() {
    var html = '';
    filtered.slice(shown, shown + PAGE).forEach(function (p) {
      var meta = [life(p), p.countries.slice(0, 2).join(', '), p.feast ? 'Feast: ' + p.feast : ''].filter(Boolean).join(' · ');
      html += '<article class="card sd-item"><div class="sd-head"><h3>' + esc(p.name) + '</h3>' +
        '<span class="status ' + CLS[p.rank] + '">' + LABEL[p.rank] + '</span></div>' +
        (meta ? '<p class="sd-meta">' + esc(meta) + '</p>' : '') +
        (p.desc ? '<p class="sd-desc">' + esc(p.desc.charAt(0).toUpperCase() + p.desc.slice(1)) + '</p>' : '') +
        (p.when && p.rank > 1 ? '<p class="sd-meta">' + esc(DECREE[p.rank].charAt(0).toUpperCase() + DECREE[p.rank].slice(1)) + ' in ' + p.when + '</p>' : '') +
        (p.patron.length ? '<p class="sd-meta">Patron of ' + esc(p.patron.slice(0, 6).join(', ')) + (p.patron.length > 6 ? ' and more' : '') + '</p>' : '') +
        '<p class="sd-links">' + (p.wiki ? '<a href="https://en.wikipedia.org/wiki/' + encodeURIComponent(p.wiki).replace(/%2F/g, '/') + '" target="_blank" rel="noopener">Read more</a> · ' : '') +
        '<a href="https://www.wikidata.org/wiki/' + p.id + '" target="_blank" rel="noopener">Correct this entry</a></p></article>';
    });
    list.insertAdjacentHTML('beforeend', html);
    shown = Math.min(filtered.length, shown + PAGE);
    more.hidden = shown >= filtered.length;
    if (!more.hidden) more.textContent = 'Show more (' + (filtered.length - shown).toLocaleString() + ' left)';
  }

  var t;
  q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 150); });
  [st, ct, cy, so].forEach(function (el) { el.addEventListener('change', run); });
  more.addEventListener('click', page);
  load();
})();
