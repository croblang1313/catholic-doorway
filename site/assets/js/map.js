/* CatholicDoorway church finder.
   Church data: OpenStreetMap via the Overpass API (ODbL). Geocoding: Nominatim.
   No data is scraped from MassTimes.org or any other directory. */
(function () {
  'use strict';
  var LG = document.documentElement.lang, ES = LG === 'es', PT = LG === 'pt', TL = LG === 'tl';
  // Filipino (Tagalog) strings, keyed by the English text.
  var TLX = {
    "The map could not load. Please check your connection and refresh.": "Hindi ma-load ang mapa. Pakitingnan ang iyong koneksiyon at i-refresh.",
    "Address not listed": "Walang nakalistang tirahan",
    "Becoming Catholic? Ask about OCIA": "Magiging Katoliko? Magtanong tungkol sa OCIA",
    "Call ": "Tumawag sa ",
    "Call the parish": "Tumawag sa parokya",
    "Catholic church": "Simbahang Katoliko",
    "Directions": "Direksiyon",
    "Email an inquiry": "Mag-email ng tanong",
    "Every parish can connect you with its OCIA group. Call or write and say something like:": "Maikokonekta ka ng bawat parokya sa kanilang grupo ng OCIA. Tumawag o sumulat at sabihin ang tulad nito:",
    "Finding your location…": "Hinahanap ang iyong lokasyon…",
    "From OpenStreetMap. Please confirm with the parish.": "Mula sa OpenStreetMap. Pakikumpirma sa parokya.",
    "How OCIA works": "Paano gumagana ang OCIA",
    "Improve this listing": "Pagbutihin ang listing na ito",
    "Interested in becoming Catholic (OCIA)": "Interested in becoming Catholic (OCIA)",
    "Listed service times:": "Nakalistang oras ng Misa:",
    "Looking for churches in this area…": "Naghahanap ng mga simbahan sa lugar na ito…",
    "No Catholic churches found here on OpenStreetMap. Try zooming out or searching a nearby town.": "Walang nakitang simbahang Katoliko rito sa OpenStreetMap. Subukang i-zoom out o maghanap ng kalapit na bayan.",
    "No phone or website is listed for this church. Try a nearby parish, or ": "Walang nakalistang telepono o website para sa simbahang ito. Subukan ang kalapit na parokya, o ",
    "On the website, look for “OCIA,” “RCIA” or “Becoming Catholic.” ": "Sa website, hanapin ang “OCIA,” “RCIA” o “Becoming Catholic.” ",
    "Parish website": "Website ng parokya",
    "Search is unavailable right now. Please try again shortly.": "Hindi magamit ang paghahanap ngayon. Pakisubukang muli mamaya.",
    "The church database is busy right now. Please try again in a minute.": "Abala ang database ng mga simbahan ngayon. Pakisubukang muli pagkalipas ng isang minuto.",
    "We couldn’t find that place. Try a city and state, or a ZIP code.": "Hindi namin mahanap ang lugar na iyon. Subukan ang lungsod at estado, o isang ZIP code.",
    "We couldn’t get your location. Please type a city or ZIP code instead.": "Hindi namin makuha ang iyong lokasyon. Mag-type na lang ng lungsod o ZIP code.",
    "Website &amp; Mass times": "Website at oras ng Misa",
    "Website": "Website",
    "You are here": "Narito ka",
    "Your browser can’t share location. Please type a city or ZIP code.": "Hindi maibahagi ng iyong browser ang lokasyon. Mag-type ng lungsod o ZIP code.",
    "Zoom in a little closer to search this area.": "Mag-zoom in nang kaunti upang maghanap sa lugar na ito.",
    "contact your diocese": "makipag-ugnayan sa iyong diyosesis",
    "your location": "iyong lokasyon",
    "“Hi, my name is ____. I’m interested in becoming Catholic. Could I speak with whoever leads OCIA, and find out when the next group starts?”": "“Magandang araw po, ako si ____. Interesado po akong maging Katoliko. Maaari ko po bang makausap ang namumuno sa OCIA, at malaman kung kailan magsisimula ang susunod na grupo?” Sa Ingles: “Hi, my name is ____. I’m interested in becoming Catholic. Could I speak with whoever leads OCIA?”",
    "/dioceses": "/tl/mga-diyosesis"
  };
  // Portuguese strings, keyed by the Spanish text so each T(en, es) call picks them up.
  var PTX = {
    'No se pudo cargar el mapa. Revisa tu conexión y vuelve a cargar la página.': 'Não foi possível carregar o mapa. Verifique sua conexão e recarregue a página.',
    'Iglesia católica': 'Igreja católica',
    'Interés en hacerme católico (OCIA)': 'Interesse em me tornar católico (OCIA)',
    'Llamar a la parroquia': 'Ligar para a paróquia',
    'Enviar un correo': 'Enviar um e-mail',
    'Sitio web de la parroquia': 'Site da paróquia',
    '¿Quieres hacerte católico? Pregunta por OCIA': 'Quer se tornar católico? Pergunte sobre a OCIA',
    'Cada parroquia puede ponerte en contacto con su grupo de OCIA. Llama o escribe y di algo así:': 'Toda paróquia pode colocar você em contato com o seu grupo de OCIA. Ligue ou escreva e diga algo assim:',
    'Esta iglesia no tiene teléfono ni sitio web en la lista. Prueba otra parroquia cercana o ': 'Esta igreja não tem telefone nem site na lista. Tente uma paróquia próxima ou ',
    'comunícate con tu diócesis': 'entre em contato com a sua diocese',
    'En el sitio web, busca “OCIA”, “RICA” o “Hacerse católico”. ': 'No site, procure por “OCIA”, “RICA”, “Catecumenato” ou “Tornar-se católico”. ',
    'Cómo funciona OCIA': 'Como funciona a OCIA',
    'Cómo llegar': 'Como chegar',
    'Sitio web': 'Site',
    'Dirección no disponible': 'Endereço não informado',
    'Horarios publicados:': 'Horários informados:',
    'Según OpenStreetMap. Confírmalos con la parroquia.': 'Segundo o OpenStreetMap. Confirme com a paróquia.',
    'Llamar al ': 'Ligar para ',
    'Sitio web y horarios de Misa': 'Site e horários de Missa',
    'Mejorar este dato': 'Melhorar este cadastro',
    'No encontramos iglesias católicas aquí en OpenStreetMap. Aleja el mapa o busca un pueblo cercano.': 'Não encontramos igrejas católicas aqui no OpenStreetMap. Afaste o mapa ou pesquise uma cidade próxima.',
    'Estás aquí': 'Você está aqui',
    'La base de datos de iglesias está ocupada. Vuelve a intentarlo en un minuto.': 'A base de dados de igrejas está ocupada. Tente de novo em um minuto.',
    'Acerca un poco más el mapa para buscar en esta zona.': 'Aproxime um pouco mais o mapa para pesquisar nesta área.',
    'Buscando iglesias en esta zona\u2026': 'Procurando igrejas nesta área\u2026',
    'No encontramos ese lugar. Prueba con una ciudad y estado, o un código postal.': 'Não encontramos esse lugar. Tente uma cidade e estado, ou um CEP (ZIP code).',
    'La búsqueda no está disponible en este momento. Inténtalo de nuevo en un rato.': 'A pesquisa não está disponível agora. Tente de novo daqui a pouco.',
    'Tu navegador no puede compartir tu ubicación. Escribe una ciudad o un código postal.': 'Seu navegador não pode compartilhar sua localização. Digite uma cidade ou um ZIP code.',
    'Buscando tu ubicación…': 'Procurando sua localização…',
    'tu ubicación': 'sua localização',
    'No pudimos obtener tu ubicación. Escribe una ciudad o un código postal.': 'Não conseguimos obter sua localização. Digite uma cidade ou um ZIP code.'
  };
  var T = function (en, es, pt) { return TL ? (TLX[en] !== undefined ? TLX[en] : en) : PT ? (pt !== undefined ? pt : (PTX[es] || en)) : ES ? es : en; };
  var OCIA = /[?&]ocia=1/.test(location.search);
  if (OCIA) document.documentElement.classList.add('ocia-mode');
  if (typeof L === 'undefined') {
    document.getElementById('map-status').textContent = T('The map could not load. Please check your connection and refresh.', 'No se pudo cargar el mapa. Revisa tu conexión y vuelve a cargar la página.');
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
        name: t.name || t['name:en'] || T('Catholic church', 'Iglesia católica'),
        addr: address(t), phone: phone(t), web: website(t),
        times: t.service_times || '', wheelchair: t.wheelchair, email: (t.email || t['contact:email'] || '').split(';')[0]
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
    return { id: type + '/' + a[8], type: type, osmId: a[8], lat: a[0], lon: a[1], name: a[2] || T('Catholic church', 'Iglesia católica'),
      addr: a[3], phone: a[4], web: normWeb(a[5]), times: a[6], email: a[9] || '' };
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


  function ociaBox(c) {
    var subj = T('Interested in becoming Catholic (OCIA)', 'Interés en hacerme católico (OCIA)');
    var body = TL ? 'Hello,\n\nI found ' + c.name + ' on CatholicDoorway.com. I am interested in learning more about becoming Catholic. Could you please put me in touch with the person who leads OCIA, and let me know when the next group begins? Is there a Filipino ministry or a Tagalog-speaking contact at the parish?\n\nThank you,\n' : T('Hello,\n\nI found ' + c.name + ' on CatholicDoorway.com. I am interested in learning more about becoming Catholic. Could you please put me in touch with the person who leads OCIA, and let me know when the next group begins?\n\nThank you,\n',
                 'Hola:\n\nEncontré ' + c.name + ' en CatholicDoorway.com. Me interesa saber más sobre cómo hacerme católico. ¿Me podrían poner en contacto con la persona que dirige OCIA y decirme cuándo empieza el próximo grupo? ¿Hay un grupo en español?\n\nGracias,\n',
                 'Olá,\n\nEncontrei ' + c.name + ' no CatholicDoorway.com. Tenho interesse em saber mais sobre como me tornar católico. Vocês poderiam me colocar em contato com a pessoa que coordena a OCIA e me dizer quando começa o próximo grupo? Há algum grupo ou atendimento em português?\n\nObrigado,\n');
    var btns = '';
    if (c.phone) btns += '<a class="btn small" href="tel:' + esc(c.phone.replace(/[^\d+]/g, '')) + '">' + T('Call the parish', 'Llamar a la parroquia') + '</a>';
    if (c.email) btns += '<a class="btn small' + (c.phone ? ' secondary' : '') + '" href="mailto:' + esc(c.email) + '?subject=' + encodeURIComponent(subj) + '&amp;body=' + encodeURIComponent(body) + '">' + T('Email an inquiry', 'Enviar un correo') + '</a>';
    if (c.web) btns += '<a class="btn small secondary" href="' + esc(c.web) + '" target="_blank" rel="noopener">' + T('Parish website', 'Sitio web de la parroquia') + '</a>';
    var say = T('“Hi, my name is ____. I’m interested in becoming Catholic. Could I speak with whoever leads OCIA, and find out when the next group starts?”',
                '“Hola, me llamo ____. Me interesa hacerme católico. ¿Puedo hablar con la persona que dirige OCIA y saber cuándo empieza el próximo grupo?”',
                '“Olá, meu nome é ____. Tenho interesse em me tornar católico. Posso falar com a pessoa que coordena a OCIA e saber quando começa o próximo grupo?”');
    return '<details class="ocia"' + (OCIA ? ' open' : '') + '><summary>' + T('Becoming Catholic? Ask about OCIA', '¿Quieres hacerte católico? Pregunta por OCIA') + '</summary>' +
      '<p>' + T('Every parish can connect you with its OCIA group. Call or write and say something like:', 'Cada parroquia puede ponerte en contacto con su grupo de OCIA. Llama o escribe y di algo así:') + '</p>' +
      '<p class="ocia-say">' + say + '</p>' +
      (btns ? '<div class="actions">' + btns + '</div>' : '<p class="muted">' + T('No phone or website is listed for this church. Try a nearby parish, or ', 'Esta iglesia no tiene teléfono ni sitio web en la lista. Prueba otra parroquia cercana o ') + '<a href="' + T('/dioceses', '/es/diocesis', '/dioceses') + '">' + T('contact your diocese', 'comunícate con tu diócesis') + '</a>.</p>') +
      '<p class="small muted">' + T('On the website, look for “OCIA,” “RCIA” or “Becoming Catholic.” ', 'En el sitio web, busca “OCIA”, “RICA” o “Hacerse católico”. ') + '<a href="' + (ES ? '/es/comenzar' : PT ? '/pt/comecar' : TL ? '/tl/magsimula' : '/start-here') + '">' + T('How OCIA works', 'Cómo funciona OCIA') + '</a></p>' +
      '</details>';
  }

  function render(list) {
    layer.clearLayers(); markers = {}; resultsEl.innerHTML = '';
    if (origin) list.forEach(function (c) { c.d = distKm(origin, [c.lat, c.lon]); });
    list.sort(function (a, b) { return (a.d || 0) - (b.d || 0); });
    var shown = list.slice(0, 60);
    shown.forEach(function (c) {
      var dir = directions(c.lat, c.lon, c.name);
      var popup = '<strong>' + esc(c.name) + '</strong>' + (c.addr ? '<br>' + esc(c.addr) : '') +
        '<br><a href="' + esc(dir) + '" target="_blank" rel="noopener">' + T('Directions', 'Cómo llegar') + '</a>' +
        (c.web ? ' &middot; <a href="' + esc(c.web) + '" target="_blank" rel="noopener">' + T('Website', 'Sitio web') + '</a>' : '');
      var m = L.marker([c.lat, c.lon], { icon: icon, title: c.name }).bindPopup(popup).addTo(layer);
      m.on('click', function () { highlight(c.id, true); });
      markers[c.id] = m;

      var card = document.createElement('article');
      card.className = 'card church';
      card.id = 'c-' + c.id.replace('/', '-');
      card.innerHTML =
        (c.d != null ? '<span class="dist">' + (ES ? 'a ' + fmtDist(c.d) : PT ? 'a ' + fmtDist(c.d) : TL ? fmtDist(c.d) + ' ang layo' : fmtDist(c.d) + ' away') + '</span>' : '') +
        '<h3><button type="button" class="linklike" style="all:unset;cursor:pointer">' + esc(c.name) + '</button></h3>' +
        '<p class="addr">' + (c.addr ? esc(c.addr) : '<span class="muted">' + T('Address not listed', 'Dirección no disponible') + '</span>') + '</p>' +
        (c.times ? '<div class="times"><strong>' + T('Listed service times:', 'Horarios publicados:') + '</strong> ' + esc(c.times) + '<br><span class="muted">' + T('From OpenStreetMap. Please confirm with the parish.', 'Según OpenStreetMap. Confírmalos con la parroquia.') + '</span></div>' : '') +
        '<div class="actions">' +
          '<a class="btn small" href="' + esc(dir) + '" target="_blank" rel="noopener">' + T('Directions', 'Cómo llegar') + '</a>' +
          (c.phone ? '<a class="btn small secondary" href="tel:' + esc(c.phone.replace(/[^\d+]/g, '')) + '">' + T('Call ', 'Llamar al ') + esc(c.phone) + '</a>' : '') +
          (c.web ? '<a class="btn small secondary" href="' + esc(c.web) + '" target="_blank" rel="noopener">' + T('Website &amp; Mass times', 'Sitio web y horarios de Misa') + '</a>' : '') +
        '</div>' +
        ociaBox(c) +
        '<p class="small muted" style="margin:.6rem 0 0"><a href="https://www.openstreetmap.org/edit?' + c.type + '=' + c.osmId + '" target="_blank" rel="noopener">' + T('Improve this listing', 'Mejorar este dato') + '</a></p>';
      card.querySelector('h3 button').addEventListener('click', function () {
        map.setView([c.lat, c.lon], Math.max(map.getZoom(), 15));
        m.openPopup();
        highlight(c.id, false);
      });
      resultsEl.appendChild(card);
    });
    if (!list.length) {
      setStatus(T('No Catholic churches found here on OpenStreetMap. Try zooming out or searching a nearby town.', 'No encontramos iglesias católicas aquí en OpenStreetMap. Aleja el mapa o busca un pueblo cercano.'));
    } else {
      setStatus(TL
        ? 'Ipinapakita ang ' + shown.length + (list.length > shown.length ? ' sa ' + list.length : '') + ' simbahang Katoliko' + (origin ? ', pinakamalapit muna.' : '.')
        : PT
        ? 'Mostrando ' + shown.length + (list.length > shown.length ? ' de ' + list.length : '') + (shown.length === 1 ? ' igreja católica' : ' igrejas católicas') + (origin ? ', da mais próxima à mais distante.' : '.')
        : ES
        ? 'Mostrando ' + shown.length + (list.length > shown.length ? ' de ' + list.length : '') + (shown.length === 1 ? ' iglesia católica' : ' iglesias católicas') + (origin ? ', de la más cercana a la más lejana.' : '.')
        : 'Showing ' + shown.length + (list.length > shown.length ? ' of ' + list.length : '') + ' Catholic ' + (shown.length === 1 ? 'church' : 'churches') + (origin ? ', nearest first.' : '.'));
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
    originMarker = L.circleMarker(origin, { radius: 7, color: '#a8802f', weight: 3, fillColor: '#fff', fillOpacity: 1 }).addTo(map).bindTooltip(label || T('You are here', 'Estás aquí'));
    setStatus(TL ? 'Naghahanap ng mga simbahang malapit sa ' + (label || 'iyo') + '\u2026' : PT ? 'Procurando igrejas perto de ' + (label || 'você') + '\u2026' : ES ? 'Buscando iglesias cerca de ' + (label || 'ti') + '\u2026' : 'Looking for churches near ' + (label || 'you') + '\u2026');
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
      setStatus(T('The church database is busy right now. Please try again in a minute.', 'La base de datos de iglesias está ocupada. Vuelve a intentarlo en un minuto.'));
    });
  }

  function searchArea() {
    if (map.getZoom() < 9) { setStatus(T('Zoom in a little closer to search this area.', 'Acerca un poco más el mapa para buscar en esta zona.')); return; }
    var b = map.getBounds();
    setStatus(T('Looking for churches in this area\u2026', 'Buscando iglesias en esta zona\u2026'));
    loadBox(b.getSouth(), b.getWest(), b.getNorth(), b.getEast()).then(function (list) {
      if (!list) return searchAreaLive(b);
      origin = [map.getCenter().lat, map.getCenter().lng];
      render(list);
    });
  }

  function searchAreaLive(b) {
    overpass(buildQuery('(' + [b.getSouth(), b.getWest(), b.getNorth(), b.getEast()].map(function (n) { return n.toFixed(5); }).join(',') + ')'))
      .then(function (data) { origin = [map.getCenter().lat, map.getCenter().lng]; render(toChurches(data)); })
      .catch(function () { setStatus(T('The church database is busy right now. Please try again in a minute.', 'La base de datos de iglesias está ocupada. Vuelve a intentarlo en un minuto.')); });
  }

  function geocode(q) {
    setStatus('Finding “' + q + '”…');
    var url = NOMINATIM + '?format=jsonv2&limit=1&addressdetails=0&q=' + encodeURIComponent(q);
    return fetch(url, { headers: { 'Accept-Language': 'en' } })
      .then(function (r) { return r.json(); })
      .then(function (res) {
        if (!res.length) { setStatus(T('We couldn’t find that place. Try a city and state, or a ZIP code.', 'No encontramos ese lugar. Prueba con una ciudad y estado, o un código postal.')); return; }
        var name = res[0].display_name.split(',').slice(0, 2).join(',');
        searchAround(parseFloat(res[0].lat), parseFloat(res[0].lon), name);
      })
      .catch(function () { setStatus(T('Search is unavailable right now. Please try again shortly.', 'La búsqueda no está disponible en este momento. Inténtalo de nuevo en un rato.')); });
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) return;
    try { history.replaceState(null, '', '?q=' + encodeURIComponent(q)); } catch (err) {}
    geocode(q);
  });

  document.getElementById('near-me').addEventListener('click', function () {
    if (!navigator.geolocation) { setStatus(T('Your browser can’t share location. Please type a city or ZIP code.', 'Tu navegador no puede compartir tu ubicación. Escribe una ciudad o un código postal.')); return; }
    setStatus(T('Finding your location…', 'Buscando tu ubicación…'));
    navigator.geolocation.getCurrentPosition(function (pos) {
      searchAround(pos.coords.latitude, pos.coords.longitude, T('your location', 'tu ubicación'));
    }, function () {
      setStatus(T('We couldn’t get your location. Please type a city or ZIP code instead.', 'No pudimos obtener tu ubicación. Escribe una ciudad o un código postal.'));
    }, { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 });
  });

  document.getElementById('search-area').addEventListener('click', searchArea);

  loadIndex(); // warm up the local church list
  var params = new URLSearchParams(location.search);
  var initial = params.get('q');
  if (initial) { input.value = initial; geocode(initial); }
})();
