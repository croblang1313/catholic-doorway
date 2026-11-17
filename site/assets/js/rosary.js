/* CatholicDoorway interactive Rosary: tap through the beads one prayer at a time. */
(function () {
  'use strict';
  var root = document.getElementById('rosary-app');
  if (!root) return;
  var $ = function (s, c) { return (c || document).querySelector(s); };

  var P = {
    sign: { t: 'The Sign of the Cross', x: 'In the name of the Father, and of the Son, and of the Holy Spirit. Amen.' },
    creed: { t: 'The Apostles’ Creed', x: 'I believe in God, the Father almighty, Creator of heaven and earth; and in Jesus Christ, his only Son, our Lord; who was conceived by the Holy Spirit, born of the Virgin Mary, suffered under Pontius Pilate, was crucified, died, and was buried. He descended into hell; the third day he rose again from the dead; he ascended into heaven, and sits at the right hand of God, the Father almighty; from there he shall come to judge the living and the dead. I believe in the Holy Spirit, the holy Catholic Church, the communion of saints, the forgiveness of sins, the resurrection of the body, and life everlasting. Amen.' },
    our: { t: 'Our Father', x: 'Our Father, who art in heaven, hallowed be thy name; thy kingdom come, thy will be done on earth as it is in heaven. Give us this day our daily bread, and forgive us our trespasses, as we forgive those who trespass against us; and lead us not into temptation, but deliver us from evil. Amen.' },
    hail: { t: 'Hail Mary', x: 'Hail Mary, full of grace, the Lord is with thee. Blessed art thou among women, and blessed is the fruit of thy womb, Jesus. Holy Mary, Mother of God, pray for us sinners, now and at the hour of our death. Amen.' },
    glory: { t: 'Glory Be', x: 'Glory be to the Father, and to the Son, and to the Holy Spirit, as it was in the beginning, is now, and ever shall be, world without end. Amen.' },
    fatima: { t: 'The Fatima Prayer', x: 'O my Jesus, forgive us our sins, save us from the fires of hell, lead all souls to heaven, especially those in most need of thy mercy.' },
    queen: { t: 'Hail, Holy Queen', x: 'Hail, holy Queen, Mother of mercy, our life, our sweetness and our hope. To thee do we cry, poor banished children of Eve. To thee do we send up our sighs, mourning and weeping in this valley of tears. Turn then, most gracious advocate, thine eyes of mercy toward us, and after this our exile show unto us the blessed fruit of thy womb, Jesus. O clement, O loving, O sweet Virgin Mary.\n\nV. Pray for us, O holy Mother of God.\nR. That we may be made worthy of the promises of Christ.' },
    close: { t: 'Closing prayer', x: 'Let us pray. O God, whose only-begotten Son, by his life, death and resurrection, has purchased for us the rewards of eternal life, grant, we beseech thee, that meditating upon these mysteries of the most holy Rosary of the Blessed Virgin Mary, we may imitate what they contain and obtain what they promise, through the same Christ our Lord. Amen.' }
  };

  var SETS = {
    joyful: { name: 'Joyful Mysteries', days: 'Mondays and Saturdays', m: [
      ['The Annunciation', 'Luke 1:26–38', 'Humility', 'The angel Gabriel tells Mary she will be the mother of God’s Son, and she says yes.'],
      ['The Visitation', 'Luke 1:39–56', 'Love of neighbor', 'Mary hurries to help her cousin Elizabeth, whose child leaps for joy.'],
      ['The Nativity', 'Luke 2:1–20', 'Poverty of spirit', 'Jesus is born in a stable in Bethlehem and laid in a manger.'],
      ['The Presentation in the Temple', 'Luke 2:22–38', 'Obedience', 'Mary and Joseph present the baby Jesus to God, and Simeon recognizes the Savior.'],
      ['The Finding of Jesus in the Temple', 'Luke 2:41–52', 'Joy in finding Jesus', 'After three days of searching, Mary and Joseph find the young Jesus in his Father’s house.']] },
    luminous: { name: 'Luminous Mysteries', days: 'Thursdays', m: [
      ['The Baptism of Jesus', 'Matthew 3:13–17', 'Openness to the Holy Spirit', 'The Father’s voice declares, “This is my beloved Son,” as the Spirit descends.'],
      ['The Wedding at Cana', 'John 2:1–11', 'To Jesus through Mary', 'At Mary’s request, Jesus turns water into wine, his first sign.'],
      ['The Proclamation of the Kingdom', 'Mark 1:14–15', 'Repentance', 'Jesus calls everyone to repent and believe the Good News.'],
      ['The Transfiguration', 'Luke 9:28–36', 'Desire for holiness', 'On the mountain, Jesus shines with glory before Peter, James and John.'],
      ['The Institution of the Eucharist', 'Luke 22:14–20', 'Love of the Eucharist', 'At the Last Supper, Jesus gives his Body and Blood under the signs of bread and wine.']] },
    sorrowful: { name: 'Sorrowful Mysteries', days: 'Tuesdays and Fridays', m: [
      ['The Agony in the Garden', 'Matthew 26:36–46', 'Sorrow for sin', 'In Gethsemane, Jesus prays, “Not my will, but yours be done.”'],
      ['The Scourging at the Pillar', 'John 19:1', 'Purity', 'Jesus is bound and whipped by the soldiers.'],
      ['The Crowning with Thorns', 'Matthew 27:27–31', 'Courage', 'Soldiers mock Jesus as a king, pressing a crown of thorns on his head.'],
      ['The Carrying of the Cross', 'Luke 23:26–32', 'Patience', 'Jesus carries his cross to Calvary, helped by Simon of Cyrene.'],
      ['The Crucifixion', 'Luke 23:33–46', 'Perseverance', 'Jesus dies on the cross, forgiving those who crucified him.']] },
    glorious: { name: 'Glorious Mysteries', days: 'Wednesdays and Sundays', m: [
      ['The Resurrection', 'Luke 24:1–12', 'Faith', 'On the third day, the tomb is empty: Jesus is risen.'],
      ['The Ascension', 'Acts 1:6–11', 'Hope', 'Jesus returns to the Father, promising to send the Holy Spirit.'],
      ['The Descent of the Holy Spirit', 'Acts 2:1–4', 'Love of God', 'At Pentecost, the Spirit comes upon Mary and the Apostles as tongues of fire.'],
      ['The Assumption of Mary', 'Revelation 12:1', 'Grace of a holy death', 'At the end of her life, Mary is taken body and soul into heaven.'],
      ['The Coronation of Mary', 'Revelation 12:1', 'Trust in Mary’s prayers', 'Mary is crowned Queen of heaven and earth.']] }
  };
  var BY_DAY = ['glorious', 'joyful', 'sorrowful', 'glorious', 'luminous', 'sorrowful', 'joyful'];

  /* ---- Steps: each is one prayer on one bead ---- */
  function buildSteps() {
    var s = [];
    s.push({ bead: 'cross', p: 'sign', label: 'Begin at the crucifix' });
    s.push({ bead: 'cross', p: 'creed', label: 'On the crucifix' });
    s.push({ bead: 'p1', p: 'our', label: 'First large bead' });
    for (var i = 1; i <= 3; i++) s.push({ bead: 'ps' + i, p: 'hail', label: 'Hail Mary ' + i + ' of 3', note: ['For an increase of faith', 'For an increase of hope', 'For an increase of charity'][i - 1] });
    s.push({ bead: 'p2', p: 'glory', label: 'Before the next large bead' });
    for (var d = 1; d <= 5; d++) {
      var big = d === 1 ? 'p2' : 'L' + (d - 1);
      s.push({ bead: big, p: 'mystery', d: d, label: 'Decade ' + d + ': announce the mystery' });
      s.push({ bead: big, p: 'our', d: d, label: 'Decade ' + d });
      for (var h = 1; h <= 10; h++) s.push({ bead: 'd' + d + '_' + h, p: 'hail', d: d, label: 'Decade ' + d + ' · Hail Mary ' + h + ' of 10' });
      var after = d < 5 ? 'L' + d : 'center';
      s.push({ bead: after, p: 'glory', d: d, label: 'End of decade ' + d });
      s.push({ bead: after, p: 'fatima', d: d, label: 'End of decade ' + d + ' (optional)' });
    }
    s.push({ bead: 'center', p: 'queen', label: 'Closing prayers' });
    s.push({ bead: 'center', p: 'close', label: 'Closing prayers' });
    s.push({ bead: 'cross', p: 'sign', label: 'Finish at the crucifix' });
    return s;
  }
  var STEPS = buildSteps();

  /* ---- Draw the rosary ---- */
  var NS = 'http://www.w3.org/2000/svg';
  var svg = $('#rosary-svg'), beads = {};
  function circle(id, x, y, r, cls) {
    var c = document.createElementNS(NS, 'circle');
    c.setAttribute('cx', x.toFixed(1)); c.setAttribute('cy', y.toFixed(1)); c.setAttribute('r', r);
    c.setAttribute('class', 'bead ' + cls);
    svg.appendChild(c); beads[id] = c; return c;
  }
  (function draw() {
    var cx = 150, cy = 135, R = 118;
    var chain = document.createElementNS(NS, 'circle');
    chain.setAttribute('cx', cx); chain.setAttribute('cy', cy); chain.setAttribute('r', R); chain.setAttribute('class', 'chain');
    svg.appendChild(chain);
    var line = document.createElementNS(NS, 'path');
    line.setAttribute('d', 'M150 ' + (cy + R) + ' V 382'); line.setAttribute('class', 'chain');
    svg.appendChild(line);
    // Loop: decade 1 runs up the right side from the centerpiece
    var units = [];
    for (var d = 1; d <= 5; d++) {
      for (var h = 1; h <= 10; h++) units.push({ id: 'd' + d + '_' + h, w: 1, cls: 'small' });
      if (d < 5) units.push({ id: 'L' + d, w: 1.9, cls: 'large' });
    }
    var total = units.reduce(function (a, u) { return a + u.w; }, 0), gap = 3.2;
    var step = 2 * Math.PI / (total + gap), a = Math.PI / 2 - step * gap / 2;
    units.forEach(function (u) {
      a -= step * u.w / 2;
      circle(u.id, cx + R * Math.cos(a), cy + R * Math.sin(a), u.cls === 'large' ? 7.5 : 5, u.cls);
      a -= step * u.w / 2;
    });
    var c = circle('center', 150, cy + R, 9, 'center');
    c.setAttribute('rx', 3);
    circle('p2', 150, cy + R + 26, 7.5, 'large');
    circle('ps1', 150, cy + R + 46, 5, 'small');
    circle('ps2', 150, cy + R + 62, 5, 'small');
    circle('ps3', 150, cy + R + 78, 5, 'small');
    circle('p1', 150, cy + R + 99, 7.5, 'large');
    var cross = document.createElementNS(NS, 'path');
    var top = cy + R + 114;
    cross.setAttribute('d', 'M150 ' + top + ' v38 M138 ' + (top + 11) + ' h24');
    cross.setAttribute('class', 'bead cross');
    svg.appendChild(cross); beads.cross = cross;
  })();

  /* ---- State ---- */
  var KEY = 'cd-rosary', at = 0, set = BY_DAY[new Date().getDay()], lock = null;
  try {
    var saved = JSON.parse(localStorage.getItem(KEY));
    if (saved && Date.now() - saved.t < 6 * 3600 * 1000 && SETS[saved.set]) { at = saved.i; set = saved.set; }
  } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify({ i: at, set: set, t: Date.now() })); } catch (e) {} }

  var picker = $('#rosary-set');
  Object.keys(SETS).forEach(function (k) {
    var o = document.createElement('option');
    o.value = k; o.textContent = SETS[k].name + (k === BY_DAY[new Date().getDay()] ? ' (today)' : '');
    picker.appendChild(o);
  });
  picker.value = set;
  picker.addEventListener('change', function () { set = picker.value; show(at); });

  function esc(x) { return String(x).replace(/[&<>]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]; }); }

  function show(i) {
    at = Math.max(0, Math.min(STEPS.length - 1, i));
    var st = STEPS[at], S = SETS[set];
    Object.keys(beads).forEach(function (k) { beads[k].classList.remove('now'); beads[k].classList.remove('done'); });
    for (var j = 0; j < at; j++) if (beads[STEPS[j].bead]) beads[STEPS[j].bead].classList.add('done');
    beads[st.bead].classList.remove('done'); beads[st.bead].classList.add('now');

    var html = '<p class="rs-where">' + esc(st.label) + '</p>';
    if (st.d) {
      var m = S.m[st.d - 1];
      html += '<div class="rs-mystery"><span class="rs-num">' + ['First', 'Second', 'Third', 'Fourth', 'Fifth'][st.d - 1] + ' ' + S.name.replace(' Mysteries', '') + ' Mystery</span>' +
        '<strong>' + esc(m[0]) + '</strong>' +
        (st.p === 'mystery' ? '<p>' + esc(m[3]) + '</p><p class="rs-meta">Read: <a href="https://bible.usccb.org/bible/' + bibleSlug(m[1]) + '" target="_blank" rel="noopener">' + esc(m[1]) + '</a> &middot; Fruit of the mystery: ' + esc(m[2]) + '</p>' : '') +
        '</div>';
    }
    if (st.p === 'mystery') {
      html += '<p class="rs-text">Announce the mystery, and picture the scene as you pray this decade.</p>';
    } else {
      var p = P[st.p];
      if (st.p === 'hail') {
        var n = st.d ? 10 : 3, k = parseInt(/Hail Mary (\d+)/.exec(st.label)[1], 10), dots = '';
        for (var q = 1; q <= n; q++) dots += '<span class="' + (q < k ? 'done' : q === k ? 'now' : '') + '"></span>';
        html += '<div class="rs-dots" aria-label="Hail Mary ' + k + ' of ' + n + '">' + dots + '</div>';
      }
      html += '<h3>' + esc(p.t) + '</h3>' + (st.note ? '<p class="rs-note">' + esc(st.note) + '</p>' : '') + '<p class="rs-text">' + esc(p.x).replace(/\n/g, '<br>') + '</p>';
    }
    $('#rosary-step').innerHTML = html;
    $('#rs-count').textContent = (at + 1) + ' / ' + STEPS.length;
    $('#rs-bar').style.width = ((at + 1) / STEPS.length * 100) + '%';
    $('#rs-back').disabled = at === 0;
    $('#rs-next').innerHTML = at === STEPS.length - 1 ? 'Amen. Start over' : 'Next &rarr;';
    save();
  }

  function bibleSlug(ref) {
    // "Luke 1:26-38" -> "luke/1?26" style deep link on the USCCB site
    var m = /^(\d?\s?[A-Za-z]+)\s(\d+)(?::(\d+))?/.exec(ref);
    if (!m) return '';
    var book = m[1].toLowerCase().replace(/\s/g, '');
    if (book === 'revelation') book = 'revelation';
    return book + '/' + m[2] + (m[3] ? '?' + m[3] : '');
  }

  function next() { if (at === STEPS.length - 1) { show(0); } else show(at + 1); keepAwake(); }
  function back() { show(at - 1); }
  function keepAwake() {
    if (!lock && navigator.wakeLock && document.visibilityState === 'visible') {
      navigator.wakeLock.request('screen').then(function (l) { lock = l; l.addEventListener('release', function () { lock = null; }); }).catch(function () {});
    }
  }
  $('#rs-next').addEventListener('click', next);
  $('#rs-back').addEventListener('click', back);
  $('#rs-restart').addEventListener('click', function () { show(0); });
  svg.addEventListener('click', next);
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'SELECT') return;
    if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); next(); }
    else if (e.key === 'ArrowLeft') back();
  });
  var x0 = null;
  root.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  root.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 60) (dx < 0 ? next : back)();
  });
  root.hidden = false;
  var nojs = $('#rosary-nojs'); if (nojs) nojs.hidden = true;
  show(at);
})();
