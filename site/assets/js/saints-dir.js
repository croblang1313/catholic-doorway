/* CatholicDoorway saints and causes directory. Data: Wikidata (CC0), refreshed weekly. */
(function () {
  'use strict';
  var list = document.getElementById('sd-list');
  if (!list) return;
  var $ = function (id) { return document.getElementById(id); };
  var feastOnly = '';
  var q = $('sd-q'), st = $('sd-status'), ct = $('sd-country'), cy = $('sd-century'), so = $('sd-sort'), more = $('sd-more'), count = $('sd-count');
  var LG = document.documentElement.lang, ES = LG === 'es', PT = LG === 'pt', TL = LG === 'tl';
  // Filipino (Tagalog) strings, keyed by the English text. Names and descriptions stay in English (Wikidata has few Tagalog labels).
  var TLX = { ' BC': ' BK', 'Died ': 'Namatay noong ', 'Born ': 'Isinilang noong ', 'The directory could not load. Please refresh the page.': 'Hindi ma-load ang direktoryo. Paki-refresh ang pahina.',
    'No one matches. Try fewer words or a different filter.': 'Walang tumugma. Subukan ang mas kaunting salita o ibang filter.', 'Feast: ': 'Kapistahan: ', 'Patron of ': 'Patron ng ',
    ' and more': ' at iba pa', 'Read more': 'Basahin pa (sa Ingles)', 'Correct this entry': 'Itama ang entry na ito', 'Show more (': 'Ipakita pa (', ' left)': ' natitira)' };
  function T(en, es, pt) { return TL ? (TLX[en] !== undefined ? TLX[en] : en) : PT ? pt : ES ? es : en; }
  var LABEL = TL ? { 4: 'Santo', 3: 'Beato', 2: 'Benerable', 1: 'Lingkod ng Diyos' } : PT ? { 4: 'Santo', 3: 'Beato', 2: 'Venerável', 1: 'Servo de Deus' } : ES ? { 4: 'Santo', 3: 'Beato', 2: 'Venerable', 1: 'Siervo de Dios' }
    : { 4: 'Saint', 3: 'Blessed', 2: 'Venerable', 1: 'Servant of God' };
  // Feminine forms for women (Wikidata sex or gender).
  var LABEL_F = TL ? { 4: 'Santa', 3: 'Beata', 2: 'Benerable', 1: 'Lingkod ng Diyos' } : PT ? { 4: 'Santa', 3: 'Beata', 2: 'Venerável', 1: 'Serva de Deus' } : ES ? { 4: 'Santa', 3: 'Beata', 2: 'Venerable', 1: 'Sierva de Dios' } : LABEL;
  var DECREE_F = TL ? null : PT ? { 4: 'Canonizada em', 3: 'Beatificada em', 2: 'Declarada Venerável em' } : ES ? { 4: 'Canonizada en', 3: 'Beatificada en', 2: 'Declarada Venerable en' } : null;
  var CLS = { 4: 's-saint', 3: 's-blessed', 2: 's-venerable', 1: 's-servant' };
  var DECREE = TL ? { 4: 'Kinanonisa noong', 3: 'Binatipika noong', 2: 'Idineklarang Benerable noong' } : PT ? { 4: 'Canonizado em', 3: 'Beatificado em', 2: 'Declarado Venerável em' } : ES ? { 4: 'Canonizado en', 3: 'Beatificado en', 2: 'Declarado Venerable en' }
    : { 4: 'Canonized in', 3: 'Beatified in', 2: 'Declared Venerable in' };
  var LOC = PT ? 'pt-BR' : ES ? 'es-US' : TL ? 'fil-PH' : 'en-US';
  function num(n) { return n.toLocaleString(LOC); }
  // Country names: [Spanish, Portuguese]. Filter values stay in English.
  var C = { 'Spain': ['España', 'Espanha'], 'France': ['Francia', 'França'], 'Italy': ['Italia', 'Itália'], 'Roman Empire': ['Imperio romano', 'Império Romano'],
    'Poland': ['Polonia', 'Polônia'], 'Germany': ['Alemania', 'Alemanha'], 'Byzantine Empire': ['Imperio bizantino', 'Império Bizantino'], 'Wales': ['Gales', 'País de Gales'],
    'Ireland': ['Irlanda', 'Irlanda'], 'England': ['Inglaterra', 'Inglaterra'], 'Mexico': ['México', 'México'], 'Portugal': ['Portugal', 'Portugal'],
    'Austria-Hungary': ['Austria-Hungría', 'Áustria-Hungria'], 'United Kingdom': ['Reino Unido', 'Reino Unido'], 'Yugoslavia': ['Yugoslavia', 'Iugoslávia'],
    'United States': ['Estados Unidos', 'Estados Unidos'], 'Hungary': ['Hungría', 'Hungria'], 'Brazil': ['Brasil', 'Brasil'], 'Russian Empire': ['Imperio ruso', 'Império Russo'],
    'Austria': ['Austria', 'Áustria'], 'Kingdom of Northumbria': ['Reino de Northumbria', 'Reino da Nortúmbria'], 'Belgium': ['Bélgica', 'Bélgica'], 'Canada': ['Canadá', 'Canadá'],
    'Cisleithania': ['Cisleitania', 'Cisleitânia'], 'German Reich': ['Reich alemán', 'Reich alemão'], 'India': ['India', 'Índia'], 'Kingdom of Toledo': ['Reino de Toledo', 'Reino de Toledo'],
    'Argentina': ['Argentina', 'Argentina'], 'Emirate of Córdoba': ['Emirato de Córdoba', 'Emirado de Córdova'], 'Soviet Union': ['Unión Soviética', 'União Soviética'],
    'Japan': ['Japón', 'Japão'], 'Switzerland': ['Suiza', 'Suíça'], 'Czech lands': ['Chequia', 'Tchéquia'], 'Ottoman Empire': ['Imperio otomano', 'Império Otomano'],
    'Joseon': ['Joseon (Corea)', 'Joseon (Coreia)'], 'Kingdom of Serbs, Croats and Slovenes': ['Reino de los Serbios, Croatas y Eslovenos', 'Reino dos Sérvios, Croatas e Eslovenos'],
    'Kingdom of Mercia': ['Reino de Mercia', 'Reino da Mércia'], 'Kingdom of Wessex': ['Reino de Wessex', 'Reino de Wessex'], 'Romania': ['Rumania', 'Romênia'],
    'Ostrogothic Kingdom': ['Reino ostrogodo', 'Reino Ostrogodo'], 'Egypt': ['Egipto', 'Egito'], 'Kingdom of Leon': ['Reino de León', 'Reino de Leão'],
    'Kingdom of the Lombards': ['Reino lombardo', 'Reino Lombardo'], 'Sweden': ['Suecia', 'Suécia'], 'Philippines': ['Filipinas', 'Filipinas'],
    'Socialist Federal Republic of Yugoslavia': ['Yugoslavia socialista', 'Iugoslávia socialista'], 'Albania': ['Albania', 'Albânia'], 'Kingdom of Denmark': ['Dinamarca', 'Dinamarca'],
    'Uganda': ['Uganda', 'Uganda'], 'Kingdom of East Anglia': ['Reino de Anglia Oriental', 'Reino da Ânglia Oriental'], 'Croatia': ['Croacia', 'Croácia'], 'Vietnam': ['Vietnam', 'Vietnã'],
    'Scotland': ['Escocia', 'Escócia'], 'Visigothic Kingdom': ['Reino visigodo', 'Reino Visigodo'], 'Colombia': ['Colombia', 'Colômbia'], 'Kingdom of Kent': ['Reino de Kent', 'Reino de Kent'],
    'Netherlands': ['Países Bajos', 'Países Baixos'], 'Chile': ['Chile', 'Chile'], "West Ukrainian People's Republic": ['República Popular de Ucrania Occidental', 'República Popular da Ucrânia Ocidental'],
    'Venezuela': ['Venezuela', 'Venezuela'], 'Peru': ['Perú', 'Peru'], 'Qing dynasty': ['China (dinastía Qing)', 'China (dinastia Qing)'], 'Kingdom of Gwynedd': ['Reino de Gwynedd', 'Reino de Gwynedd'],
    'Bulgaria': ['Bulgaria', 'Bulgária'], 'Visigothic Kingdom of Tolosa': ['Reino visigodo de Tolosa', 'Reino Visigodo de Tolosa'], 'Tokugawa shogunate': ['Japón (shogunato Tokugawa)', 'Japão (xogunato Tokugawa)'],
    'Syria': ['Siria', 'Síria'], 'Kingdom of Burgundy': ['Reino de Borgoña', 'Reino da Borgonha'], 'Kingdom of Lombardy–Venetia': ['Reino lombardo-véneto', 'Reino Lombardo-Vêneto'],
    'Malta': ['Malta', 'Malta'], 'Lithuania': ['Lituania', 'Lituânia'], 'Kingdom of Asturias': ['Reino de Asturias', 'Reino das Astúrias'], 'South Korea': ['Corea del Sur', 'Coreia do Sul'],
    'Lebanon': ['Líbano', 'Líbano'], 'Kingdom of Galicia': ['Reino de Galicia', 'Reino da Galiza'], 'Brittany': ['Bretaña', 'Bretanha'], 'Ecuador': ['Ecuador', 'Equador'],
    'Slovenia': ['Eslovenia', 'Eslovênia'], "Ukrainian People's Republic": ['República Popular de Ucrania', 'República Popular da Ucrânia'], 'Ethiopia': ['Etiopía', 'Etiópia'],
    'Kingdom of Majorca': ['Reino de Mallorca', 'Reino de Maiorca'], 'Norway': ['Noruega', 'Noruega'], 'Principality of Wallachia': ['Principado de Valaquia', 'Principado da Valáquia'],
    'Republic of Pisa': ['República de Pisa', 'República de Pisa'], 'Kingdom of Romania': ['Reino de Rumania', 'Reino da Romênia'], 'Grand Duchy of Lithuania': ['Gran Ducado de Lituania', 'Grão-Ducado da Lituânia'],
    'Roman Hispania': ['Hispania romana', 'Hispânia romana'], 'El Salvador': ['El Salvador', 'El Salvador'], 'Ukraine': ['Ucrania', 'Ucrânia'], 'China': ['China', 'China'],
    'Korea': ['Corea', 'Coreia'], 'Slovakia': ['Eslovaquia', 'Eslováquia'], 'Czech Republic': ['Chequia', 'Tchéquia'], 'Cuba': ['Cuba', 'Cuba'], 'Guatemala': ['Guatemala', 'Guatemala'],
    'Paraguay': ['Paraguay', 'Paraguai'], 'Uruguay': ['Uruguay', 'Uruguai'], 'Bolivia': ['Bolivia', 'Bolívia'], 'Australia': ['Australia', 'Austrália'], 'Israel': ['Israel', 'Israel'],
    'Greece': ['Grecia', 'Grécia'], 'Turkey': ['Turquía', 'Turquia'], 'Kingdom of Portugal': ['Portugal', 'Portugal'] };
  function country(c) { var t = C[c]; return t && (ES || PT) ? t[PT ? 1 : 0] : c; }
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  var MES = PT ? ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
    : ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  function feast(f) {
    if (!f || !(ES || PT || TL)) return f;
    var m = /^([A-Z][a-z]+) (\d{1,2})$/.exec(f), i = m ? MONTHS.indexOf(m[1]) : -1;
    if (TL) return i < 0 ? f : ['Enero', 'Pebrero', 'Marso', 'Abril', 'Mayo', 'Hunyo', 'Hulyo', 'Agosto', 'Setyembre', 'Oktubre', 'Nobyembre', 'Disyembre'][i] + ' ' + m[2];
    return i < 0 ? f : m[2] + ' de ' + MES[i];
  }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  var people = [], shown = 0, filtered = [], PAGE = 50;

  function fold(s) { return String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function century(y) {
    if (!y) return '';
    var c = y > 0 ? Math.floor((y - 1) / 100) + 1 : 0;
    return c;
  }
  function roman(n) {
    var r = '', v = [[10, 'X'], [9, 'IX'], [5, 'V'], [4, 'IV'], [1, 'I']];
    v.forEach(function (x) { while (n >= x[0]) { r += x[1]; n -= x[0]; } });
    return r;
  }
  function ord(n) { var s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
  function fmtYear(y) { return y < 0 ? (-y) + T(' BC', ' a. C.', ' a.C.') : String(y); }
  function life(p) {
    if (p.born && p.died) return fmtYear(p.born) + '–' + fmtYear(p.died);
    if (p.died) return T('Died ', 'Murió en ', 'Morreu em ') + fmtYear(p.died);
    if (p.born) return T('Born ', 'Nació en ', 'Nasceu em ') + fmtYear(p.born);
    return '';
  }

  function load() {
    fetch('/data/saints-directory.json').then(function (r) { return r.json(); }).then(function (d) {
      people = d.people.map(function (a) {
        var p = { id: a[0], name: a[1], alt: a[2], desc: a[3], rank: a[4], when: a[5], born: a[6], died: a[7],
          countries: a[8] ? a[8].split('|') : [], patron: a[9] ? a[9].split('|') : [], feast: a[10], wiki: a[11] };
        // Spanish and Portuguese: show the local name, description and patronages when Wikidata has them.
        var ln = PT ? a[12] : ES ? a[2] : '', ld = PT ? a[14] : ES ? a[13] : '', lp = PT ? a[16] : ES ? a[15] : '';
        p.f = a[17] === 'f';
        p.show = ln || p.name;
        p.other = ln ? p.name : '';
        p.ldesc = ld || p.desc;
        p.lpat = lp ? lp.split('|') : p.patron;
        p.cent = century(p.died || p.born);
        p.hay = fold(p.name + ' ' + p.alt + ' ' + (a[12] || '') + ' ' + p.desc + ' ' + (ld || '') + ' ' + p.countries.map(country).join(' ') + ' ' +
          p.countries.join(' ') + ' ' + p.patron.join(' ') + ' ' + (lp || '').replace(/\|/g, ' '));
        return p;
      });
      var cc = {}, cents = {};
      people.forEach(function (p) {
        p.countries.forEach(function (c) { cc[c] = (cc[c] || 0) + 1; });
        if (p.cent) cents[p.cent] = 1;
      });
      Object.keys(cc).filter(function (c) { return cc[c] >= 3; }).sort().forEach(function (c) {
        var o = document.createElement('option'); o.value = c; o.textContent = country(c) + ' (' + cc[c] + ')'; o.dataset.sort = fold(country(c)); ct.appendChild(o);
      });
      if (ES || PT) {
        var opts = Array.prototype.slice.call(ct.options, 1).sort(function (x, y) { return x.dataset.sort < y.dataset.sort ? -1 : 1; });
        opts.forEach(function (o) { ct.appendChild(o); });
      }
      Object.keys(cents).map(Number).sort(function (a, b) { return a - b; }).forEach(function (c) {
        var o = document.createElement('option'); o.value = c; o.textContent = TL ? 'Ika-' + c + ' siglo' : T(ord(c) + ' century', 'Siglo ' + roman(c), 'Século ' + roman(c)); cy.appendChild(o);
      });
      var n = d.counts || {};
      $('sd-updated').textContent = TL
        ? 'Na-update noong ' + d.updated + ': ' + num(n.saints || 0) + ' Santo, ' + num(n.blessed || 0) + ' Beato, ' + num(n.venerable || 0) + ' Benerable at ' + num(n.servants || 0) + ' Lingkod ng Diyos. Datos mula sa Wikidata (CC0).'
        : PT
        ? 'Atualizado em ' + d.updated + ': ' + num(n.saints || 0) + ' Santos, ' + num(n.blessed || 0) + ' Beatos, ' + num(n.venerable || 0) + ' Veneráveis e ' + num(n.servants || 0) + ' Servos de Deus. Dados do Wikidata (CC0).'
        : ES
        ? 'Actualizado el ' + d.updated + ': ' + num(n.saints || 0) + ' Santos, ' + num(n.blessed || 0) + ' Beatos, ' + num(n.venerable || 0) + ' Venerables y ' + num(n.servants || 0) + ' Siervos de Dios. Datos de Wikidata (CC0).'
        : 'Updated ' + d.updated + ': ' + num(n.saints || 0) + ' Saints, ' + num(n.blessed || 0) + ' Blesseds, ' + num(n.venerable || 0) + ' Venerables and ' + num(n.servants || 0) + ' Servants of God. ' + d.license;
      var params = new URLSearchParams(location.search);
      if (params.get('q')) q.value = params.get('q');
      if (params.get('status')) st.value = params.get('status');
      if (params.get('sort')) so.value = params.get('sort');
      feastOnly = params.get('feast') || '';
      var fb = document.getElementById('sd-feast-note');
      if (feastOnly && fb) { fb.hidden = false; fb.querySelector('b').textContent = feast(feastOnly); }
      run();
    }).catch(function () { list.classList.add('ready'); count.textContent = T('The directory could not load. Please refresh the page.', 'No se pudo cargar el directorio. Vuelve a cargar la página.', 'Não foi possível carregar o diretório. Recarregue a página.'); });
  }

  function run() {
    var terms = fold(q.value).trim().split(/\s+/).filter(Boolean), s = +st.value, c = ct.value, ce = +cy.value || 0;
    filtered = people.filter(function (p) {
      if (feastOnly && p.feast !== feastOnly) return false;
      if (s && p.rank !== s) return false;
      if (c && p.countries.indexOf(c) < 0) return false;
      if (ce && p.cent !== ce) return false;
      for (var i = 0; i < terms.length; i++) if (p.hay.indexOf(terms[i]) < 0) return false;
      return true;
    });
    if (so.value === 'name' && (ES || PT)) filtered.sort(function (a, b) { var x = fold(a.show), y = fold(b.show); return x < y ? -1 : x > y ? 1 : 0; });
    else if (so.value === 'recent') filtered = filtered.filter(function (p) { return p.when; }).sort(function (a, b) { return b.when - a.when || b.rank - a.rank; });
    else if (so.value === 'died') filtered.sort(function (a, b) { return (a.died || 9999) - (b.died || 9999); });
    list.innerHTML = ''; shown = 0; list.classList.add('ready');
    var one = filtered.length === 1, rec = so.value === 'recent';
    count.textContent = filtered.length
      ? num(filtered.length) + (TL ? (one ? ' tao' : ' na tao') + (rec ? ' na may nakatalang petsa ng dekreto, pinakabago muna.' : '.') : T((one ? ' person' : ' people') + (rec ? ' with a recorded decree date, newest first.' : '.'),
          (one ? ' persona' : ' personas') + (rec ? ' con fecha de decreto registrada, de la más reciente a la más antigua.' : '.'),
          (one ? ' pessoa' : ' pessoas') + (rec ? ' com data de decreto registrada, da mais recente para a mais antiga.' : '.')))
      : T('No one matches. Try fewer words or a different filter.', 'Nadie coincide. Prueba con menos palabras u otro filtro.', 'Ninguém corresponde. Tente menos palavras ou outro filtro.');
    page();
  }

  function page() {
    var html = '';
    filtered.slice(shown, shown + PAGE).forEach(function (p) {
      var meta = [life(p), p.countries.slice(0, 2).map(country).join(', '), p.feast ? T('Feast: ', 'Fiesta: ', 'Festa: ') + feast(p.feast) : ''].filter(Boolean).join(' · ');
      var desc = p.ldesc, enDesc = (ES || PT) && desc === p.desc && desc;
      var pat = p.lpat, enPat = (ES || PT) && pat === p.patron;
      var en = ' lang="en"';
      html += '<article class="card sd-item"><div class="sd-head"><h3>' + esc(p.show) + '</h3>' +
        '<span class="status ' + CLS[p.rank] + '">' + (p.f ? LABEL_F : LABEL)[p.rank] + '</span></div>' +
        (p.other ? '<p class="sd-meta"' + en + '>' + esc(p.other) + '</p>' : '') +
        (meta ? '<p class="sd-meta">' + esc(meta) + '</p>' : '') +
        (desc ? '<p class="sd-desc"' + (enDesc ? en : '') + '>' + esc(cap(desc)) + '</p>' : '') +
        (p.when && p.rank > 1 ? '<p class="sd-meta">' + (p.f && DECREE_F ? DECREE_F : DECREE)[p.rank] + ' ' + p.when + '</p>' : '') +
        (pat.length ? '<p class="sd-meta">' + T('Patron of ', 'Patrono de: ', 'Padroeiro de: ') + '<span' + (enPat ? en : '') + '>' + esc(pat.slice(0, 6).join(', ')) + '</span>' +
          (pat.length > 6 ? T(' and more', ' y más', ' e mais') : '') + '</p>' : '') +
        '<p class="sd-links">' + (p.wiki ? '<a href="https://en.wikipedia.org/wiki/' + encodeURIComponent(p.wiki).replace(/%2F/g, '/') + '" target="_blank" rel="noopener">' +
          T('Read more', 'Leer más (en inglés)', 'Leia mais (em inglês)') + '</a> · ' : '') +
        '<a href="https://www.wikidata.org/wiki/' + p.id + '" target="_blank" rel="noopener">' + T('Correct this entry', 'Corregir esta ficha', 'Corrigir esta ficha') + '</a></p></article>';
    });
    list.insertAdjacentHTML('beforeend', html);
    shown = Math.min(filtered.length, shown + PAGE);
    more.hidden = shown >= filtered.length;
    if (!more.hidden) more.textContent = T('Show more (', 'Ver más (', 'Ver mais (') + num(filtered.length - shown) + T(' left)', ' restantes)', ' restantes)');
  }

  var t;
  q.addEventListener('input', function () { clearTimeout(t); t = setTimeout(run, 150); });
  [st, ct, cy, so].forEach(function (el) { el.addEventListener('change', run); });
  more.addEventListener('click', page);
  load();
})();
