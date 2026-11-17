/* CatholicDoorway church finder.
   Church data: OpenStreetMap via the Overpass API (ODbL). Geocoding: Nominatim.
   No data is scraped from MassTimes.org or any other directory. */
(function () {
  'use strict';
  if (typeof L === 'undefined') {
    document.getElementById('map-status').textContent = 'The map could not load. Please check your connection and refresh.';
    return;
  }

  var OVERPASS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter'];
  var NOMINATIM = 'https://nominatim.openstreetmap.org/search';
  // Denominations in full communion with Rome, as tagged on OpenStreetMap.
  var DENOMS = '^(catholic|roman_catholic|greek_catholic|ukrainian_greek_catholic|byzantine_catholic|ruthenian_catholic|maronite|melkite|chaldean_catholic|armenian_catholic|syro-malabar|syro_malabar|syro-malankara|syriac_catholic|coptic_catholic|ethiopian_catholic)$';

  var statusEl = document.getElementById('map-status');
  var resultsEl = document.getElementById('results');
  var form = document.getElementById('map-form');
  var input = document.getElementById('map-q');
  var isApple = /iPhone|iPad|Macintosh/.test(navigator.userAgent) && 'ontouchend' in document;

  var map = L.map('map', { scrollWheelZoom: false }).setView([39.5, -98.35], 4);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);
  map.on('focus', function () { map.scrollWheelZoom.enable(); });
  map.on('blur', function () { map.scrollWheelZoom.disable(); });

  var layer = L.layerGroup().addTo(map);
  var origin = null;
  var originMarker = null;
  var markers = {};

  var icon = L.divIcon({
    className: 'cd-pin',
    html: '<svg viewBox="0 0 28 36" width="28" height="36" aria-hidden="true"><path d="M14 35s12-12.4 12-21A12 12 0 0 0 2 14c0 8.6 12 21 12 21z" fill="#1d2b4f" stroke="#fff" stroke-width="1.5"/><path d="M14 7v12M9.5 11.5h9" stroke="#e9cf8e" stroke-width="2.4" stroke-linecap="round"/></svg>',
    iconSize: [28, 36], iconAnchor: [14, 35], popupAnchor: [0, -30]
  });

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function setStatus(msg) { statusEl.textContent = msg; }

  function distKm(a, b) {
    var R = 6371, toRad = Math.PI / 180;
    var dLat = (b[0] - a[0]) * toRad, dLon = (b[1] - a[1]) * toRad;
    var x = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(a[0] * toRad) * Math.cos(b[0] * toRad) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * R * Math.asin(Math.sqrt(x));
  }
  function fmtDist(km) {
    var mi = km * 0.621371;
    return mi < 10 ? mi.toFixed(1) + ' mi' : Math.round(mi) + ' mi';
  }

  function address(t) {
    var line1 = [t['addr:housenumber'], t['addr:street']].filter(Boolean).join(' ');
    var line2 = [t['addr:city'], [t['addr:state'], t['addr:postcode']].filter(Boolean).join(' ')].filter(Boolean).join(', ');
    return [line1, line2].filter(Boolean).join(', ');
  }
  function normWeb(w) {
    w = (w || '').split(';')[0].trim();
    if (w && !/^https?:\/\//i.test(w)) w = 'https://' + w;
    return /^https?:\/\/[^\s]+$/i.test(w) ? w : '';
  }
  function website(t) { return normWeb(t.website || t['contact:website'] || t.url); }
  function phone(t) { return (t.phone || t['contact:phone'] || '').split(';')[0].trim(); }
  function directions(lat, lon, name) {
    return isApple
      ? 'https://maps.apple.com/?daddr=' + lat + ',' + lon + '&q=' + encodeURIComponent(name)
      : 'https://www.google.com/maps/dir/?api=1&destination=' + lat + ',' + lon;
  }

  function buildQuery(area) {
    return '[out:json][timeout:25];nwr["amenity"="place_of_worship"]["religion"="christian"]["denomination"~"' + DENOMS + '"]' + area + ';out center tags 300;';
  }

  function overpass(q, i) {
    i = i || 0;
    return fetch(OVERPASS[i], { method: 'POST', body: 'data=' + encodeURIComponent(q), headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .catch(function (e) { if (i + 1 < OVERPASS.length) return overpass(q, i + 1); throw e; });
  }

  function toChurches(data) {
    return (data.elements || []).map(function (el) {
      var lat = el.lat != null ? el.lat : el.center && el.center.lat;
      var lon = el.lon != null ? el.lon : el.center && el.center.lon;
      if (lat == null) return null;
      var t = el.tags || {};
      return {
        id: el.type + '/' + el.id, type: el.type, osmId: el.id, lat: lat, lon: lon,
        name: t.name || t['name:en'] || 'Catholic church',
        addr: address(t), phone: phone(t), web: website(t),
        times: t.service_times || '', wheelchair: t.wheelchair
      };
    }).filter(Boolean);
  }

  /* ---------- Local church list (site/data/churches), refreshed weekly ---------- */
  var DATA = '/data/churches/';
  var indexP = null, cellCache = {};
  var OSM_TYPES = { n: 'node', w: 'way', r: 'relation' };
  function loadIndex() {
    if (!indexP) indexP = fetch(DATA + 'index.json').then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
    return indexP;
  }
  function fromCompact(a) {
    var type = OSM_TYPES[a[7]] || 'node';
    return { id: type + '/' + a[8], type: type, osmId: a[8], lat: a[0], lon: a[1], name: a[2] || 'Catholic church',
      addr: a[3], phone: a[4], web: normWeb(a[5]), times: a[6] };
  }
  // Resolves to a list of churches inside the box, or null if the local list is unavailable.
  function loadBox(s, w, n, e) {
    return loadIndex().then(function (ix) {
      if (!ix || !ix.cells) return null;
      var have = {}, keys = [];
      ix.cells.forEach(function (c) { have[c] = true; });
      for (var la = Math.floor(s); la <= Math.floor(n); la++) {
        for (var lo = Math.floor(w); lo <= Math.floor(e); lo++) {
          var k = la + '_' + lo;
          if (have[k]) keys.push(k);
        }
      }
      return Promise.all(keys.map(function (k) {
        if (!cellCache[k]) cellCache[k] = fetch(DATA + k + '.json').then(function (r) { return r.json(); }).catch(function () { return []; });
        return cellCache[k];
      })).then(function (arrs) {
        var out = [];
        arrs.forEach(function (arr) { arr.forEach(function (a) { if (a[0] >= s && a[0] <= n && a[1] >= w && a[1] <= e) out.push(fromCompact(a)); }); });
        return out;
      });
    });
  }
  function boxAround(lat, lon, km) {
    var dLat = km / 111, dLon = km / (111 * Math.max(0.2, Math.cos(lat * Math.PI / 180)));
    return [lat - dLat, lon - dLon, lat + dLat, lon + dLon];
  }

  function render(list) {
    layer.clearLayers(); markers = {}; resultsEl.innerHTML = '';
    if (origin) list.forEach(function (c) { c.d = distKm(origin, [c.lat, c.lon]); });
    list.sort(function (a, b) { return (a.d || 0) - (b.d || 0); });
    var shown = list.slice(0, 60);
    shown.forEach(function (c) {
      var dir = directions(c.lat, c.lon, c.name);
      var popup = '<strong>' + esc(c.name) + '</strong>' + (c.addr ? '<br>' + esc(c.addr) : '') +
        '<br><a href="' + esc(dir) + '" target="_blank" rel="noopener">Directions</a>' +
        (c.web ? ' &middot; <a href="' + esc(c.web) + '" target="_blank" rel="noopener">Website</a>' : '');
      var m = L.marker([c.lat, c.lon], { icon: icon, title: c.name }).bindPopup(popup).addTo(layer);
      m.on('click', function () { highlight(c.id, true); });
      markers[c.id] = m;

      var card = document.createElement('article');
      card.className = 'card church';
      card.id = 'c-' + c.id.replace('/', '-');
      card.innerHTML =
        (c.d != null ? '<span class="dist">' + fmtDist(c.d) + ' away</span>' : '') +
        '<h3><button type="button" class="linklike" style="all:unset;cursor:pointer">' + esc(c.name) + '</button></h3>' +
        '<p class="addr">' + (c.addr ? esc(c.addr) : '<span class="muted">Address not listed</span>') + '</p>' +
        (c.times ? '<div class="times"><strong>Listed service times:</strong> ' + esc(c.times) + '<br><span class="muted">From OpenStreetMap. Please confirm with the parish.</span></div>' : '') +
        '<div class="actions">' +
          '<a class="btn small" href="' + esc(dir) + '" target="_blank" rel="noopener">Directions</a>' +
          (c.phone ? '<a class="btn small secondary" href="tel:' + esc(c.phone.replace(/[^\d+]/g, '')) + '">Call ' + esc(c.phone) + '</a>' : '') +
          (c.web ? '<a class="btn small secondary" href="' + esc(c.web) + '" target="_blank" rel="noopener">Website &amp; Mass times</a>' : '') +
        '</div>' +
        '<p class="small muted" style="margin:.6rem 0 0"><a href="https://www.openstreetmap.org/edit?' + c.type + '=' + c.osmId + '" target="_blank" rel="noopener">Improve this listing</a></p>';
      card.querySelector('h3 button').addEventListener('click', function () {
        map.setView([c.lat, c.lon], Math.max(map.getZoom(), 15));
        m.openPopup();
        highlight(c.id, false);
      });
      resultsEl.appendChild(card);
    });
    if (!list.length) {
      setStatus('No Catholic churches found here on OpenStreetMap. Try zooming out or searching a nearby town.');
    } else {
      setStatus('Showing ' + shown.length + (list.length > shown.length ? ' of ' + list.length : '') + ' Catholic ' + (shown.length === 1 ? 'church' : 'churches') + (origin ? ', nearest first.' : '.'));
    }
  }

  function highlight(id, scroll) {
    var els = resultsEl.querySelectorAll('.church.active');
    for (var i = 0; i < els.length; i++) els[i].classList.remove('active');
    var el = document.getElementById('c-' + id.replace('/', '-'));
    if (el) { el.classList.add('active'); if (scroll) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
  }

  function showResults(list) {
    render(list);
    var pts = list.slice(0, 12).map(function (c) { return [c.lat, c.lon]; }).concat([origin]);
    if (pts.length > 1) map.fitBounds(pts, { padding: [30, 30], maxZoom: 15 }); else map.setView(origin, 13);
  }

  function searchAround(lat, lon, label) {
    origin = [lat, lon];
    if (originMarker) map.removeLayer(originMarker);
    originMarker = L.circleMarker(origin, { radius: 7, color: '#a8802f', weight: 3, fillColor: '#fff', fillOpacity: 1 }).addTo(map).bindTooltip(label || 'You are here');
    setStatus('Looking for churches near ' + (label || 'you') + '\u2026');
    var bx = boxAround(lat, lon, 80);
    loadBox(bx[0], bx[1], bx[2], bx[3]).then(function (all) {
      if (!all) return searchAroundLive(lat, lon, label);
      all.forEach(function (c) { c.d = distKm(origin, [c.lat, c.lon]); });
      // Widen the circle until there are a few churches to show.
      var list = [];
      [15, 30, 50, 80].some(function (km) { list = all.filter(function (c) { return c.d <= km; }); return list.length >= 5; });
      if (!list.length) list = all;
      showResults(list);
    });
  }

  // Fallback: ask the public Overpass server directly (slow, used only if the local list is missing).
  function searchAroundLive(lat, lon, label, radius) {
    radius = radius || 15000;
    overpass(buildQuery('(around:' + radius + ',' + lat + ',' + lon + ')')).then(function (data) {
      var list = toChurches(data);
      if (list.length < 3 && radius < 60000) return searchAroundLive(lat, lon, label, radius * 2.5);
      showResults(list);
    }).catch(function () {
      setStatus('The church database is busy right now. Please try again in a minute.');
    });
  }

  function searchArea() {
    if (map.getZoom() < 9) { setStatus('Zoom in a little closer to search this area.'); return; }
    var b = map.getBounds();
    setStatus('Looking for churches in this area\u2026');
    loadBox(b.getSouth(), b.getWest(), b.getNorth(), b.getEast()).then(function (list) {
      if (!list) return searchAreaLive(b);
      origin = [map.getCenter().lat, map.getCenter().lng];
      render(list);
    });
  }

  function searchAreaLive(b) {
    overpass(buildQuery('(' + [b.getSouth(), b.getWest(), b.getNorth(), b.getEast()].map(function (n) { return n.toFixed(5); }).join(',') + ')'))
      .then(function (data) { origin = [map.getCenter().lat, map.getCenter().lng]; render(toChurches(data)); })
      .catch(function () { setStatus('The church database is busy right now. Please try again in a minute.'); });
  }

  function geocode(q) {
    setStatus('Finding “' + q + '”…');
    var url = NOMINATIM + '?format=jsonv2&limit=1&addressdetails=0&q=' + encodeURIComponent(q);
    return fetch(url, { headers: { 'Accept-Language': 'en' } })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.length) { setStatus('We couldn’t find that place. Try a city and state, or a ZIP code.'); return; }
        var name = res[0].display_name.split(',').slice(0, 2).join(',');
        searchAround(parseFloat(res[0].lat), parseFloat(res[0].lon), name);
      })
      .catch(function () { setStatus('Search is unavailable right now. Please try again shortly.'); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) return;
    try { history.replaceState(null, '', '?q=' + encodeURIComponent(q)); } catch (err) {}
    geocode(q);
  });

  document.getElementById('near-me').addEventListener('click', function () {
    if (!navigator.geolocation) { setStatus('Your browser can’t share location. Please type a city or ZIP code.'); return; }
    setStatus('Finding your location…');
    navigator.geolocation.getCurrentPosition(function (pos) {
      searchAround(pos.coords.latitude, pos.coords.longitude, 'your location');
    }, function () {
      setStatus('We couldn’t get your location. Please type a city or ZIP code instead.');
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 });
  });

  document.getElementById('search-area').addEventListener('click', searchArea);

  loadIndex(); // warm up the local church list
  var initial = new URLSearchParams(location.search).get('q');
  if (initial) { input.value = initial; geocode(initial); }
})();
