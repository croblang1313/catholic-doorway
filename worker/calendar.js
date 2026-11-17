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

export function eventsFor(y) {
  const E = easter(y), ev = [];
  const push = (dt, title, kind, note) => ev.push({ date: iso(dt), title, kind, note: note || "" });
  const HDO = "Holy Day of Obligation: Catholics attend Mass.";
  const satMon = (dt) => dow(dt) === 6 || dow(dt) === 1;

  // Jan 1
  const jan1 = utc(y, 1, 1);
  push(jan1, "Mary, the Holy Mother of God", satMon(jan1) ? "solemnity" : "obligation",
    satMon(jan1) ? "Solemnity. Not a day of obligation this year because it falls on a " + (dow(jan1) === 6 ? "Saturday." : "Monday.") : HDO);
  // Epiphany: Sunday Jan 2-8
  let ep = utc(y, 1, 2); while (dow(ep) !== 0) ep = add(ep, 1);
  push(ep, "The Epiphany of the Lord", "feast", "The Magi visit the child Jesus.");
  // Baptism of the Lord: Sunday after Epiphany, or Monday if Epiphany is Jan 7 or 8
  push(ep.getUTCDate() >= 7 ? add(ep, 1) : add(ep, 7), "The Baptism of the Lord", "feast", "Christmas season ends.");
  // Lent and Easter
  const ash = add(E, -46);
  push(ash, "Ash Wednesday", "fast", "Lent begins. Day of fasting and abstinence from meat.");
  for (let f = add(ash, 2); f < add(E, -2); f = add(f, 7)) push(f, "Friday of Lent", "abstinence", "Abstinence from meat (ages 14 and up).");
  // St. Joseph (Mar 19) and the Annunciation (Mar 25), with transfers
  const palm = add(E, -7);
  let jos = utc(y, 3, 19);
  if (jos >= palm && jos <= E) jos = add(palm, -1);
  else if (dow(jos) === 0) jos = add(jos, 1);
  push(jos, "St. Joseph, Spouse of the Blessed Virgin Mary", "solemnity", "");
  let ann = utc(y, 3, 25);
  if (ann >= palm && ann <= add(E, 7)) ann = add(E, 8);
  else if (dow(ann) === 0) ann = add(ann, 1);
  push(ann, "The Annunciation of the Lord", "solemnity", "The angel Gabriel announces to Mary that she will bear the Son of God.");
  push(palm, "Palm Sunday of the Passion of the Lord", "feast", "Holy Week begins.");
  push(add(E, -3), "Holy Thursday", "feast", "Evening Mass of the Lord's Supper.");
  push(add(E, -2), "Good Friday", "fast", "The Lord's Passion. Day of fasting and abstinence from meat.");
  push(add(E, -1), "Holy Saturday: Easter Vigil", "feast", "The Easter Vigil is celebrated after nightfall.");
  push(E, "Easter Sunday", "solemnity", "The Resurrection of the Lord.");
  push(add(E, 7), "Divine Mercy Sunday", "feast", "Second Sunday of Easter.");
  push(add(E, 42), "The Ascension of the Lord", "obligation",
    "Holy Day of Obligation, celebrated on this Sunday in most of the U.S. The ecclesiastical provinces of Boston, Hartford, New York, Newark, Omaha and Philadelphia keep it on Thursday, " + iso(add(E, 39)) + ".");
  push(add(E, 49), "Pentecost Sunday", "solemnity", "The Holy Spirit descends on the Apostles; the Easter season ends.");
  push(add(E, 56), "The Most Holy Trinity", "solemnity", "");
  push(add(E, 63), "The Most Holy Body and Blood of Christ (Corpus Christi)", "solemnity", "");
  push(add(E, 68), "The Most Sacred Heart of Jesus", "solemnity", "");
  // Fixed summer and autumn days
  push(utc(y, 6, 29), "Sts. Peter and Paul, Apostles", "solemnity", "");
  const aug15 = utc(y, 8, 15);
  push(aug15, "The Assumption of the Blessed Virgin Mary", satMon(aug15) ? "solemnity" : "obligation",
    satMon(aug15) ? "Solemnity. Not a day of obligation this year because it falls on a " + (dow(aug15) === 6 ? "Saturday." : "Monday.") : HDO);
  const nov1 = utc(y, 11, 1);
  push(nov1, "All Saints", satMon(nov1) ? "solemnity" : "obligation",
    satMon(nov1) ? "Solemnity. Not a day of obligation this year because it falls on a " + (dow(nov1) === 6 ? "Saturday." : "Monday.") : HDO);
  push(utc(y, 11, 2), "All Souls' Day", "feast", "Commemoration of all the faithful departed.");
  const adv = adventStart(y);
  push(add(adv, -7), "Our Lord Jesus Christ, King of the Universe", "solemnity", "The last Sunday of the Church year.");
  push(adv, "First Sunday of Advent", "feast", "A new Church year begins.");
  let dec8 = utc(y, 12, 8);
  if (dow(dec8) === 0) push(add(dec8, 1), "The Immaculate Conception of the Blessed Virgin Mary", "solemnity",
    "Moved from Sunday, December 8. Not a day of obligation this year.");
  else push(dec8, "The Immaculate Conception of the Blessed Virgin Mary", "obligation", HDO + " Patronal feast of the United States.");
  push(utc(y, 12, 12), "Our Lady of Guadalupe", "feast", "Patroness of the Americas.");
  push(utc(y, 12, 24), "Christmas Eve", "feast", "Vigil Masses are celebrated in the evening.");
  push(utc(y, 12, 25), "The Nativity of the Lord (Christmas)", "obligation", HDO);
  // Holy Family: Sunday in the Christmas octave, or Dec 30 if there is none
  const xd = dow(utc(y, 12, 25));
  push(xd === 0 ? utc(y, 12, 30) : add(utc(y, 12, 25), 7 - xd), "The Holy Family of Jesus, Mary and Joseph", "feast", "");
  return ev.sort((a, b) => a.date.localeCompare(b.date));
}

function range(fromYear, toYear) {
  const out = [];
  for (let y = fromYear; y <= toYear; y++) out.push(...eventsFor(y));
  return out;
}

const KIND_LABEL = { obligation: "Holy Day of Obligation", fast: "Fast and abstinence", abstinence: "Abstinence", solemnity: "Solemnity", feast: "Feast" };

function icsEscape(s) {
  return s.replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");
}

function fold(line) {
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

export function ics(events, stamp) {
  const lines = [
    "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CatholicDoorway//Holy Days//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
    "X-WR-CALNAME:Catholic Holy Days (U.S.)",
    fold("X-WR-CALDESC:Holy days of obligation\\, fasting days and major feasts. From CatholicDoorway.com"),
    "REFRESH-INTERVAL;VALUE=DURATION:P7D", "X-PUBLISHED-TTL:P7D",
  ];
  for (const e of events) {
    const d = e.date.replace(/-/g, "");
    const next = iso(add(new Date(e.date + "T00:00:00Z"), 1)).replace(/-/g, "");
    const slug = e.title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
    const title = e.kind === "obligation" ? `${e.title} (Holy Day of Obligation)` : e.kind === "fast" ? `${e.title} (Fast & Abstinence)` : e.title;
    const desc = [e.note.startsWith(KIND_LABEL[e.kind]) ? "" : KIND_LABEL[e.kind], e.note, "https://catholicdoorway.com/calendar"].filter(Boolean).join("\n");
    lines.push("BEGIN:VEVENT", fold(`UID:${d}-${slug}@catholicdoorway.com`), `DTSTAMP:${stamp}`,
      `DTSTART;VALUE=DATE:${d}`, `DTEND;VALUE=DATE:${next}`, fold(`SUMMARY:${icsEscape(title)}`),
      fold(`DESCRIPTION:${icsEscape(desc)}`), "TRANSP:TRANSPARENT", "END:VEVENT");
  }
  lines.push("END:VCALENDAR");
  return lines.join("\r\n") + "\r\n";
}

export function calendar(url, now = new Date()) {
  const y = now.getUTCFullYear();
  if (url.pathname.endsWith(".json")) {
    const from = parseInt(url.searchParams.get("year") || y, 10);
    const yr = Number.isFinite(from) && from > 1582 && from < 4000 ? from : y;
    return new Response(JSON.stringify({ year: yr, events: range(yr, yr + 1) }), {
      headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "public, max-age=86400" },
    });
  }
  const stamp = now.toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
  return new Response(ics(range(y - 1, y + 2), stamp), {
    headers: {
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": 'inline; filename="catholic-holy-days.ics"',
      "Cache-Control": "public, max-age=86400",
    },
  });
}
