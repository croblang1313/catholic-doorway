// Holy days, fasting days and major feasts for the Catholic Church in the
// United States, computed for any year (no external data needed).
//
//   GET /api/calendar.ics   subscribable iCalendar feed (last year + next 2)
//   GET /api/calendar.json  the same events as JSON for the website
//
// U.S. rules followed:
// - Holy days of obligation: Jan 1, Ascension, Aug 15, Nov 1, Dec 8, Dec 25.
//   Jan 1, Aug 15 and Nov 1 are not obligatory when they fall on a Saturday
//   or Monday. Most U.S. provinces move Ascension to the following Sunday.
//   Dec 8 on a Sunday moves to Monday and is not obligatory that year.
// - Epiphany is the Sunday from Jan 2 to 8; Corpus Christi is on Sunday.
// - Fast and abstinence: Ash Wednesday, Good Friday. Abstinence: Lent Fridays.

const DAY = 86400000;
const utc = (y, m, d) => new Date(Date.UTC(y, m - 1, d));
const add = (dt, n) => new Date(dt.getTime() + n * DAY);
const iso = (dt) => dt.toISOString().slice(0, 10);
const dow = (dt) => dt.getUTCDay(); // 0 = Sunday

export function easter(y) {
  // Anonymous Gregorian algorithm (Meeus/Jones/Butcher)
  const a = y % 19, b = Math.floor(y / 100), c = y % 100, d = Math.floor(b / 4), e = b % 4;
  const f = Math.floor((b + 8) / 25), g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30, i = Math.floor(c / 4), k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7, m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31), day = ((h + l - 7 * m + 114) % 31) + 1;
  return utc(y, month, day);
}

function adventStart(y) {
  // Fourth Sunday before Christmas = the Sunday from Nov 27 to Dec 3
  const xmas = utc(y, 12, 25);
  return add(xmas, -(dow(xmas) || 7) - 21);
}

// Filipino (Tagalog) titles and notes, keyed by the English text.
const TLX = {
  "Holy Day of Obligation: Catholics attend Mass.": "Pistang pangilin: nagsisimba ang mga Katoliko.",
  "Mary, the Holy Mother of God": "Santa Maria, Ina ng Diyos",
  "The Epiphany of the Lord": "Ang Pagpapakita ng Panginoon (Tatlong Hari)",
  "The Magi visit the child Jesus.": "Dinalaw ng mga Pantas ang Sanggol na si Hesus.",
  "The Baptism of the Lord": "Ang Pagbibinyag sa Panginoon",
  "Christmas season ends.": "Nagtatapos ang Panahon ng Pasko.",
  "Ash Wednesday": "Miyerkoles ng Abo",
  "Lent begins. Day of fasting and abstinence from meat.": "Nagsisimula ang Kuwaresma. Araw ng pag-aayuno at pangingilin sa karne.",
  "Friday of Lent": "Biyernes ng Kuwaresma",
  "Abstinence from meat (ages 14 and up).": "Pangingilin sa karne (14 taong gulang pataas).",
  "St. Joseph, Spouse of the Blessed Virgin Mary": "San Jose, Esposo ng Mahal na Birheng Maria",
  "The Annunciation of the Lord": "Ang Pagbati ng Anghel sa Panginoon",
  "The angel Gabriel announces to Mary that she will bear the Son of God.": "Ibinalita ng anghel Gabriel kay Maria na siya ang magiging ina ng Anak ng Diyos.",
  "Palm Sunday of the Passion of the Lord": "Linggo ng Palaspas ng Pagpapakasakit ng Panginoon",
  "Holy Week begins.": "Nagsisimula ang Semana Santa.",
  "Holy Thursday": "Huwebes Santo",
  "Evening Mass of the Lord's Supper.": "Misa ng Huling Hapunan ng Panginoon sa gabi.",
  "Good Friday": "Biyernes Santo",
  "The Lord's Passion. Day of fasting and abstinence from meat.": "Ang Pagpapakasakit ng Panginoon. Araw ng pag-aayuno at pangingilin sa karne.",
  "Holy Saturday: Easter Vigil": "Sabado de Gloria: Bihilya ng Pasko ng Pagkabuhay",
  "The Easter Vigil is celebrated after nightfall.": "Ipinagdiriwang ang Bihilya ng Pasko ng Pagkabuhay pagsapit ng gabi.",
  "Easter Sunday": "Linggo ng Pagkabuhay",
  "The Resurrection of the Lord.": "Ang Muling Pagkabuhay ng Panginoon.",
  "Divine Mercy Sunday": "Linggo ng Banal na Awa",
  "Second Sunday of Easter.": "Ikalawang Linggo ng Pagkabuhay.",
  "The Ascension of the Lord": "Ang Pag-akyat sa Langit ng Panginoon",
  "Pentecost Sunday": "Linggo ng Pentekostes",
  "The Holy Spirit descends on the Apostles; the Easter season ends.": "Bumaba ang Espiritu Santo sa mga Apostol; nagtatapos ang Panahon ng Pagkabuhay.",
  "The Most Holy Trinity": "Ang Kabanal-banalang Santatlo",
  "The Most Holy Body and Blood of Christ (Corpus Christi)": "Ang Kabanal-banalang Katawan at Dugo ni Kristo (Corpus Christi)",
  "The Most Sacred Heart of Jesus": "Ang Kamahal-mahalang Puso ni Hesus",
  "Sts. Peter and Paul, Apostles": "San Pedro at San Pablo, mga Apostol",
  "The Assumption of the Blessed Virgin Mary": "Ang Pag-akyat sa Langit ng Mahal na Birheng Maria",
  "All Saints": "Todos los Santos (Araw ng mga Santo)",
  "All Souls' Day": "Araw ng mga Kaluluwa",
  "Commemoration of all the faithful departed.": "Paggunita sa lahat ng mga yumaong mananampalataya.",
  "Our Lord Jesus Christ, King of the Universe": "Ang Panginoong Hesukristo, Hari ng Sanlibutan",
  "The last Sunday of the Church year.": "Ang huling Linggo ng taon ng Simbahan.",
  "First Sunday of Advent": "Unang Linggo ng Adbiyento",
  "A new Church year begins.": "Nagsisimula ang bagong taon ng Simbahan.",
  "The Immaculate Conception of the Blessed Virgin Mary": "Ang Kalinis-linisang Paglilihi sa Mahal na Birheng Maria",
  "Moved from Sunday, December 8. Not a day of obligation this year.": "Inilipat mula sa Linggo, Disyembre 8. Hindi pistang pangilin ngayong taon.",
  " Patronal feast of the United States.": " Kapistahan ng patrona ng Estados Unidos.",
  "Our Lady of Guadalupe": "Mahal na Birhen ng Guadalupe",
  "Patroness of the Americas.": "Patrona ng Amerika.",
  "Christmas Eve": "Bisperas ng Pasko",
  "Vigil Masses are celebrated in the evening.": "Ipinagdiriwang sa gabi ang mga Misa ng bihilya.",
  "The Nativity of the Lord (Christmas)": "Ang Pagsilang ng Panginoon (Pasko)",
  "The Holy Family of Jesus, Mary and Joseph": "Ang Banal na Mag-anak nina Hesus, Maria at Jose"
};

export function eventsFor(y, lang = "en") {
  const E = easter(y), ev = [];
  const t = (en, es, pt) => (lang === "tl" ? (TLX[en] ?? en) : lang === "pt" ? pt : lang === "es" ? es : en);
  const push = (dt, title, kind, note) => ev.push({ date: iso(dt), title, kind, note: note || "" });
  const HDO = t("Holy Day of Obligation: Catholics attend Mass.", "Día de precepto: los católicos van a Misa.", "Dia santo de guarda: os católicos vão à Missa.");
  const satMon = (dt) => dow(dt) === 6 || dow(dt) === 1;
  const notThisYear = (dt) => lang === "tl" ? "Dakilang Kapistahan. Hindi pistang pangilin ngayong taon dahil natapat sa " + (dow(dt) === 6 ? "Sabado." : "Lunes.") : t("Solemnity. Not a day of obligation this year because it falls on a " + (dow(dt) === 6 ? "Saturday." : "Monday."),
    "Solemnidad. Este año no es día de precepto porque cae en " + (dow(dt) === 6 ? "sábado." : "lunes."),
    "Solenidade. Este ano não é dia santo de guarda porque cai " + (dow(dt) === 6 ? "num sábado." : "numa segunda-feira."));

  // Jan 1
  const jan1 = utc(y, 1, 1);
  push(jan1, t("Mary, the Holy Mother of God", "Santa María, Madre de Dios", "Santa Maria, Mãe de Deus"), satMon(jan1) ? "solemnity" : "obligation", satMon(jan1) ? notThisYear(jan1) : HDO);
  // Epiphany: Sunday Jan 2-8
  let ep = utc(y, 1, 2); while (dow(ep) !== 0) ep = add(ep, 1);
  push(ep, t("The Epiphany of the Lord", "La Epifanía del Señor", "A Epifania do Senhor"), "feast", t("The Magi visit the child Jesus.", "Los Magos visitan al Niño Jesús.", "Os Magos visitam o Menino Jesus."));
  // Baptism of the Lord: Sunday after Epiphany, or Monday if Epiphany is Jan 7 or 8
  push(ep.getUTCDate() >= 7 ? add(ep, 1) : add(ep, 7), t("The Baptism of the Lord", "El Bautismo del Señor", "O Batismo do Senhor"), "feast", t("Christmas season ends.", "Termina el tiempo de Navidad.", "Termina o tempo do Natal."));
  // Lent and Easter
  const ash = add(E, -46);
  push(ash, t("Ash Wednesday", "Miércoles de Ceniza", "Quarta-feira de Cinzas"), "fast", t("Lent begins. Day of fasting and abstinence from meat.", "Comienza la Cuaresma. Día de ayuno y abstinencia de carne.", "Começa a Quaresma. Dia de jejum e abstinência de carne."));
  for (let f = add(ash, 2); f < add(E, -2); f = add(f, 7)) push(f, t("Friday of Lent", "Viernes de Cuaresma", "Sexta-feira da Quaresma"), "abstinence", t("Abstinence from meat (ages 14 and up).", "Abstinencia de carne (a partir de los 14 años).", "Abstinência de carne (a partir dos 14 anos)."));
  // St. Joseph (Mar 19) and the Annunciation (Mar 25), with transfers
  const palm = add(E, -7);
  let jos = utc(y, 3, 19);
  if (jos >= palm && jos <= E) jos = add(palm, -1);
  else if (dow(jos) === 0) jos = add(jos, 1);
  push(jos, t("St. Joseph, Spouse of the Blessed Virgin Mary", "San José, Esposo de la Virgen María", "São José, Esposo da Virgem Maria"), "solemnity", "");
  let ann = utc(y, 3, 25);
  if (ann >= palm && ann <= add(E, 7)) ann = add(E, 8);
  else if (dow(ann) === 0) ann = add(ann, 1);
  push(ann, t("The Annunciation of the Lord", "La Anunciación del Señor", "A Anunciação do Senhor"), "solemnity", t("The angel Gabriel announces to Mary that she will bear the Son of God.", "El ángel Gabriel anuncia a María que será la madre del Hijo de Dios.", "O anjo Gabriel anuncia a Maria que ela será a mãe do Filho de Deus."));
  push(palm, t("Palm Sunday of the Passion of the Lord", "Domingo de Ramos de la Pasión del Señor", "Domingo de Ramos e da Paixão do Senhor"), "feast", t("Holy Week begins.", "Comienza la Semana Santa.", "Começa a Semana Santa."));
  push(add(E, -3), t("Holy Thursday", "Jueves Santo", "Quinta-feira Santa"), "feast", t("Evening Mass of the Lord's Supper.", "Misa vespertina de la Cena del Señor.", "Missa vespertina da Ceia do Senhor."));
  push(add(E, -2), t("Good Friday", "Viernes Santo", "Sexta-feira Santa"), "fast", t("The Lord's Passion. Day of fasting and abstinence from meat.", "La Pasión del Señor. Día de ayuno y abstinencia de carne.", "A Paixão do Senhor. Dia de jejum e abstinência de carne."));
  push(add(E, -1), t("Holy Saturday: Easter Vigil", "Sábado Santo: Vigilia Pascual", "Sábado Santo: Vigília Pascal"), "feast", t("The Easter Vigil is celebrated after nightfall.", "La Vigilia Pascual se celebra después del anochecer.", "A Vigília Pascal é celebrada depois do anoitecer."));
  push(E, t("Easter Sunday", "Domingo de Pascua", "Domingo de Páscoa"), "solemnity", t("The Resurrection of the Lord.", "La Resurrección del Señor.", "A Ressurreição do Senhor."));
  push(add(E, 7), t("Divine Mercy Sunday", "Domingo de la Divina Misericordia", "Domingo da Divina Misericórdia"), "feast", t("Second Sunday of Easter.", "Segundo Domingo de Pascua.", "Segundo Domingo da Páscoa."));
  push(add(E, 42), t("The Ascension of the Lord", "La Ascensión del Señor", "A Ascensão do Senhor"), "obligation",
    lang === "tl" ? "Pistang pangilin, ipinagdiriwang sa Linggong ito sa karamihan ng Estados Unidos. Sa mga lalawigang eklesiyastiko ng Boston, Hartford, New York, Newark, Omaha at Philadelphia, ipinagdiriwang ito sa Huwebes, " + iso(add(E, 39)) + "." : t("Holy Day of Obligation, celebrated on this Sunday in most of the U.S. The ecclesiastical provinces of Boston, Hartford, New York, Newark, Omaha and Philadelphia keep it on Thursday, " + iso(add(E, 39)) + ".",
      "Día de precepto; en la mayor parte de Estados Unidos se celebra este domingo. Las provincias eclesiásticas de Boston, Hartford, Nueva York, Newark, Omaha y Filadelfia la celebran el jueves " + iso(add(E, 39)) + ".",
      "Dia santo de guarda; na maior parte dos Estados Unidos é celebrada neste domingo. As províncias eclesiásticas de Boston, Hartford, Nova York, Newark, Omaha e Filadélfia a celebram na quinta-feira, " + iso(add(E, 39)) + "."));
  push(add(E, 49), t("Pentecost Sunday", "Domingo de Pentecostés", "Domingo de Pentecostes"), "solemnity", t("The Holy Spirit descends on the Apostles; the Easter season ends.", "El Espíritu Santo desciende sobre los Apóstoles; termina el tiempo de Pascua.", "O Espírito Santo desce sobre os Apóstolos; termina o Tempo Pascal."));
  push(add(E, 56), t("The Most Holy Trinity", "La Santísima Trinidad", "A Santíssima Trindade"), "solemnity", "");
  push(add(E, 63), t("The Most Holy Body and Blood of Christ (Corpus Christi)", "El Santísimo Cuerpo y Sangre de Cristo (Corpus Christi)", "O Santíssimo Corpo e Sangue de Cristo (Corpus Christi)"), "solemnity", "");
  push(add(E, 68), t("The Most Sacred Heart of Jesus", "El Sagrado Corazón de Jesús", "O Sagrado Coração de Jesus"), "solemnity", "");
  // Fixed summer and autumn days
  push(utc(y, 6, 29), t("Sts. Peter and Paul, Apostles", "San Pedro y San Pablo, Apóstoles", "São Pedro e São Paulo, Apóstolos"), "solemnity", "");
  const aug15 = utc(y, 8, 15);
  push(aug15, t("The Assumption of the Blessed Virgin Mary", "La Asunción de la Virgen María", "A Assunção de Nossa Senhora"), satMon(aug15) ? "solemnity" : "obligation", satMon(aug15) ? notThisYear(aug15) : HDO);
  const nov1 = utc(y, 11, 1);
  push(nov1, t("All Saints", "Todos los Santos", "Todos os Santos"), satMon(nov1) ? "solemnity" : "obligation", satMon(nov1) ? notThisYear(nov1) : HDO);
  push(utc(y, 11, 2), t("All Souls' Day", "Día de los Fieles Difuntos", "Dia de Finados"), "feast", t("Commemoration of all the faithful departed.", "Conmemoración de todos los fieles difuntos.", "Comemoração de todos os fiéis defuntos."));
  const adv = adventStart(y);
  push(add(adv, -7), t("Our Lord Jesus Christ, King of the Universe", "Nuestro Señor Jesucristo, Rey del Universo", "Nosso Senhor Jesus Cristo, Rei do Universo"), "solemnity", t("The last Sunday of the Church year.", "El último domingo del año litúrgico.", "O último domingo do ano litúrgico."));
  push(adv, t("First Sunday of Advent", "Primer Domingo de Adviento", "Primeiro Domingo do Advento"), "feast", t("A new Church year begins.", "Comienza un nuevo año litúrgico.", "Começa um novo ano litúrgico."));
  const dec8 = utc(y, 12, 8);
  const ic = t("The Immaculate Conception of the Blessed Virgin Mary", "La Inmaculada Concepción de la Virgen María", "A Imaculada Conceição da Virgem Maria");
  if (dow(dec8) === 0) push(add(dec8, 1), ic, "solemnity", t("Moved from Sunday, December 8. Not a day of obligation this year.", "Trasladada del domingo 8 de diciembre. Este año no es día de precepto.", "Transferida do domingo, 8 de dezembro. Este ano não é dia santo de guarda."));
  else push(dec8, ic, "obligation", HDO + t(" Patronal feast of the United States.", " Fiesta patronal de Estados Unidos.", " Festa da padroeira dos Estados Unidos."));
  push(utc(y, 12, 12), t("Our Lady of Guadalupe", "Nuestra Señora de Guadalupe", "Nossa Senhora de Guadalupe"), "feast", t("Patroness of the Americas.", "Patrona de América.", "Padroeira da América."));
  push(utc(y, 12, 24), t("Christmas Eve", "Nochebuena", "Véspera de Natal"), "feast", t("Vigil Masses are celebrated in the evening.", "Las Misas de vigilia se celebran por la tarde y la noche.", "As Missas da vigília são celebradas à tarde e à noite."));
  push(utc(y, 12, 25), t("The Nativity of the Lord (Christmas)", "La Natividad del Señor (Navidad)", "O Natal do Senhor"), "obligation", HDO);
  // Holy Family: Sunday in the Christmas octave, or Dec 30 if there is none
  const xd = dow(utc(y, 12, 25));
  push(xd === 0 ? utc(y, 12, 30) : add(utc(y, 12, 25), 7 - xd), t("The Holy Family of Jesus, Mary and Joseph", "La Sagrada Familia de Jesús, María y José", "A Sagrada Família de Jesus, Maria e José"), "feast", "");
  return ev.sort((a, b) => a.date.localeCompare(b.date));
}

function range(fromYear, toYear, lang) {
  const out = [];
  for (let y = fromYear; y <= toYear; y++) out.push(...eventsFor(y, lang));
  return out;
}

const KIND_LABEL = { obligation: "Holy Day of Obligation", fast: "Fast and abstinence", abstinence: "Abstinence", solemnity: "Solemnity", feast: "Feast" };
const KIND_LABEL_ES = { obligation: "Día de precepto", fast: "Ayuno y abstinencia", abstinence: "Abstinencia", solemnity: "Solemnidad", feast: "Fiesta" };
const KIND_LABEL_TL = { obligation: "Pistang pangilin", fast: "Ayuno at pangingilin", abstinence: "Pangingilin", solemnity: "Dakilang Kapistahan", feast: "Kapistahan" };
const KIND_LABEL_PT = { obligation: "Dia santo de guarda", fast: "Jejum e abstinência", abstinence: "Abstinência", solemnity: "Solenidade", feast: "Festa" };

export function icsEscape(s) {
  return s.replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
}

export function fold(line) {
  // RFC 5545: lines over 75 octets are folded
  const out = [];
  let s = line;
  while (new TextEncoder().encode(s).length > 75) {
    let n = 74;
    while (new TextEncoder().encode(s.slice(0, n)).length > 74) n--;
    out.push(s.slice(0, n));
    s = " " + s.slice(n);
  }
  out.push(s);
  return out.join("\r\n");
}

export function ics(events, stamp, lang = "en") {
  const es = lang === "es", pt = lang === "pt", tl = lang === "tl", K = tl ? KIND_LABEL_TL : pt ? KIND_LABEL_PT : es ? KIND_LABEL_ES : KIND_LABEL;
  const lines = [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CatholicDoorway//Holy Days//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
    tl ? "X-WR-CALNAME:Mga pistang pangilin (Estados Unidos)" : pt ? "X-WR-CALNAME:Dias santos católicos (EUA)" : es ? "X-WR-CALNAME:Días santos católicos (EE. UU.)" : "X-WR-CALNAME:Catholic Holy Days (U.S.)",
    fold(tl ? "X-WR-CALDESC:Mga pistang pangilin\\, araw ng pag-aayuno at pangunahing kapistahan. Mula sa CatholicDoorway.com"
      : pt ? "X-WR-CALDESC:Dias santos de guarda\\, dias de jejum e festas principais. Do CatholicDoorway.com"
      : es ? "X-WR-CALDESC:Días de precepto\\, días de ayuno y fiestas principales. De CatholicDoorway.com"
      : "X-WR-CALDESC:Holy days of obligation\\, fasting days and major feasts. From CatholicDoorway.com"),
    "REFRESH-INTERVAL;VALUE=DURATION:P7D", "X-PUBLISHED-TTL:P7D",
  ];
  for (const e of events) {
    const d = e.date.replace(/-/g, "");
    const next = iso(add(new Date(e.date + "T00:00:00Z"), 1)).replace(/-/g, "");
    const slug = (es ? "es-" : pt ? "pt-" : tl ? "tl-" : "") + e.title.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    const title = e.kind === "obligation" ? `${e.title} (${K.obligation})` : e.kind === "fast" ? `${e.title} (${K.fast})` : e.title;
    const desc = [e.note.startsWith(K[e.kind]) ? "" : K[e.kind], e.note, tl ? "https://catholicdoorway.com/tl/kalendaryo" : pt ? "https://catholicdoorway.com/pt/calendario" : es ? "https://catholicdoorway.com/es/calendario" : "https://catholicdoorway.com/calendar"].filter(Boolean).join("\n");
    lines.push("BEGIN:VEVENT", fold(`UID:${d}-${slug}@catholicdoorway.com`), `DTSTAMP:${stamp}`,
      `DTSTART;VALUE=DATE:${d}`, `DTEND;VALUE=DATE:${next}`, fold(`SUMMARY:${icsEscape(title)}`),
      fold(`DESCRIPTION:${icsEscape(desc)}`), "TRANSP:TRANSPARENT", "END:VEVENT");
  }
  lines.push("END:VCALENDAR");
  return lines.join("\r\n") + "\r\n";
}

export function calendar(url, now = new Date()) {
  const y = now.getUTCFullYear();
  const q = url.searchParams.get("lang"), lang = q === "es" || q === "pt" || q === "tl" ? q : "en";
  if (url.pathname.endsWith(".json")) {
    const from = parseInt(url.searchParams.get("year") || y, 10);
    const yr = Number.isFinite(from) && from > 1582 && from < 4000 ? from : y;
    return new Response(JSON.stringify({ year: yr, events: range(yr, yr + 1, lang) }), {
      headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "public, max-age=86400" },
    });
  }
  const stamp = now.toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
  return new Response(ics(range(y - 1, y + 2, lang), stamp, lang), {
    headers: {
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": `inline; filename="${lang === "es" ? "dias-santos-catolicos" : lang === "pt" ? "dias-santos-catolicos-pt" : lang === "tl" ? "mga-pistang-pangilin" : "catholic-holy-days"}.ics"`,
      "Cache-Control": "public, max-age=86400",
    },
  });
}
