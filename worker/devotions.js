// Prayer reminders as a subscribable calendar.
//
//   GET /api/devotions.ics?set=angelus12,angelus6,mercy,stations,novenas&lang=en|es|pt|tl
//
// Daily reminders use "floating" local times (no time zone), so the Angelus
// shows up at noon wherever the person lives. Novena days and the Fridays of
// Lent are computed for last year, this year and next year.

import { easter, fold, icsEscape } from "./calendar.js";
import NOVENAS from "./novenas-data.js"; // written by src/build.py from src/data/novenas.json

const DAY = 86400000;
const utc = (y, m, d) => new Date(Date.UTC(y, m - 1, d));
const add = (dt, n) => new Date(dt.getTime() + n * DAY);
const ymd = (dt) => dt.toISOString().slice(0, 10).replace(/-/g, "");

const SITE = { en: "https://catholicdoorway.com", es: "https://catholicdoorway.com/es", pt: "https://catholicdoorway.com/pt", tl: "https://catholicdoorway.com/tl" };
const PAGE = {
  angelus: { en: "/angelus", es: "/angelus", pt: "/angelus", tl: "/orasyon" },
  mercy: { en: "/divine-mercy-chaplet", es: "/coronilla-de-la-divina-misericordia", pt: "/terco-da-misericordia", tl: "/koronilya-ng-banal-na-awa" },
  stations: { en: "/stations-of-the-cross", es: "/via-crucis", pt: "/via-sacra", tl: "/daan-ng-krus" },
  novenas: { en: "/novenas", es: "/novenas", pt: "/novenas", tl: "/mga-nobena" },
};
const T = {
  angelus: { en: "The Angelus", es: "El Ángelus", pt: "O Angelus", tl: "Ang Orasyon" },
  angelusNote: {
    en: "Pray the Angelus (the Regina Caeli during the Easter season).",
    es: "Reza el Ángelus (el Regina Caeli en el tiempo de Pascua).",
    pt: "Reze o Angelus (a Rainha do Céu no Tempo Pascal).",
    tl: "Dasalin ang Orasyon (ang Regina Caeli sa Panahon ng Pagkabuhay).",
  },
  mercy: { en: "Hour of Mercy: Divine Mercy Chaplet", es: "Hora de la Misericordia: Coronilla", pt: "Hora da Misericórdia: Terço da Misericórdia", tl: "Oras ng Awa: Koronilya ng Banal na Awa" },
  mercyNote: {
    en: "3 p.m., the hour Jesus died. Pray the Divine Mercy Chaplet, or simply: Jesus, I trust in you.",
    es: "Las 3 de la tarde, la hora en que murió Jesús. Reza la Coronilla de la Divina Misericordia, o simplemente: Jesús, en ti confío.",
    pt: "3 da tarde, a hora em que Jesus morreu. Reze o Terço da Misericórdia, ou simplesmente: Jesus, eu confio em vós.",
    tl: "Ikatlo ng hapon, ang oras ng pagkamatay ni Hesus. Dasalin ang Koronilya ng Banal na Awa, o simpleng: Hesus, ako ay nananalig sa iyo.",
  },
  stations: { en: "Stations of the Cross", es: "Vía Crucis", pt: "Via-Sacra", tl: "Daan ng Krus" },
  stationsNote: {
    en: "A Friday of Lent. Many parishes pray the Stations of the Cross this evening.",
    es: "Un viernes de Cuaresma. Muchas parroquias rezan el Vía Crucis esta tarde.",
    pt: "Uma sexta-feira da Quaresma. Muitas paróquias rezam a Via-Sacra hoje à tarde.",
    tl: "Biyernes ng Kuwaresma. Maraming parokya ang nagdarasal ng Daan ng Krus ngayong gabi.",
  },
  day: { en: "day", es: "día", pt: "dia", tl: "araw" },
  of: { en: "of", es: "de", pt: "de", tl: "sa" },
  name: { en: "Catholic prayer reminders", es: "Recordatorios de oración católica", pt: "Lembretes de oração católica", tl: "Mga paalala sa pagdarasal" },
};

export function novenaStart(start, y) {
  if (start.startsWith("E")) return add(easter(y), parseInt(start.slice(1), 10));
  const [m, d] = start.split("-").map(Number);
  return utc(y, m, d);
}

function strip(s) {
  return s.replace(/<[^>]+>/g, "");
}

function alarm(text) {
  return ["BEGIN:VALARM", "ACTION:DISPLAY", fold(`DESCRIPTION:${icsEscape(text)}`), "TRIGGER:PT0M", "END:VALARM"];
}

function daily(lines, stamp, uid, hhmm, title, note, url) {
  lines.push("BEGIN:VEVENT", `UID:${uid}@catholicdoorway.com`, `DTSTAMP:${stamp}`, `DTSTART:20260101T${hhmm}00`,
    "DURATION:PT10M", "RRULE:FREQ=DAILY", fold(`SUMMARY:${icsEscape(title)}`),
    fold(`DESCRIPTION:${icsEscape(note + "\n" + url)}`), fold(`URL:${url}`), "TRANSP:TRANSPARENT", ...alarm(title), "END:VEVENT");
}

function timed(lines, stamp, uid, dt, hhmm, mins, title, note, url) {
  lines.push("BEGIN:VEVENT", `UID:${uid}@catholicdoorway.com`, `DTSTAMP:${stamp}`, `DTSTART:${ymd(dt)}T${hhmm}00`,
    `DURATION:PT${mins}M`, fold(`SUMMARY:${icsEscape(title)}`), fold(`DESCRIPTION:${icsEscape(note + "\n" + url)}`),
    fold(`URL:${url}`), "TRANSP:TRANSPARENT", ...alarm(title), "END:VEVENT");
}

export function devotionsIcs(set, lang, now = new Date()) {
  const stamp = now.toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
  const y = now.getUTCFullYear();
  const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CatholicDoorway//Prayer Reminders//EN", "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH", fold(`X-WR-CALNAME:${T.name[lang]}`), "REFRESH-INTERVAL;VALUE=DURATION:P7D", "X-PUBLISHED-TTL:P7D"];
  const url = (k, hash = "") => SITE[lang] + PAGE[k][lang] + hash;
  const L = lang === "en" ? "" : lang + "-";
  if (set.has("angelus12")) daily(lines, stamp, `${L}angelus-noon`, "1200", T.angelus[lang], T.angelusNote[lang], url("angelus"));
  if (set.has("angelus6")) {
    daily(lines, stamp, `${L}angelus-morning`, "0600", T.angelus[lang], T.angelusNote[lang], url("angelus"));
    daily(lines, stamp, `${L}angelus-evening`, "1800", T.angelus[lang], T.angelusNote[lang], url("angelus"));
  }
  if (set.has("mercy")) daily(lines, stamp, `${L}hour-of-mercy`, "1500", T.mercy[lang], T.mercyNote[lang], url("mercy"));
  for (let yr = y - 1; yr <= y + 1; yr++) {
    if (set.has("stations")) {
      const E = easter(yr);
      for (let f = add(E, -44); f <= add(E, -2); f = add(f, 7)) {
        timed(lines, stamp, `${L}stations-${ymd(f)}`, f, "1900", 45, T.stations[lang], T.stationsNote[lang], url("stations"));
      }
    }
    if (set.has("novenas")) {
      for (const nv of NOVENAS) {
        const s = novenaStart(nv.start, yr), [title] = nv[lang];
        for (let i = 0; i < 9; i++) {
          const dt = add(s, i);
          const intent = nv.days ? ": " + nv.days[lang][i] : "";
          timed(lines, stamp, `${L}novena-${nv.id}-${ymd(dt)}`, dt, "0800", 10,
            `${title}, ${T.day[lang]} ${i + 1} ${T.of[lang]} 9`, strip(nv[lang][1]) + intent, url("novenas", "#" + nv.id));
        }
      }
    }
  }
  lines.push("END:VCALENDAR");
  return lines.join("\r\n") + "\r\n";
}

export function devotions(url, now = new Date()) {
  const q = url.searchParams.get("lang"), lang = q === "es" || q === "pt" || q === "tl" ? q : "en";
  const allowed = ["angelus12", "angelus6", "mercy", "stations", "novenas"];
  const set = new Set((url.searchParams.get("set") || "angelus12,mercy,stations,novenas").split(",").filter((s) => allowed.includes(s)));
  return new Response(devotionsIcs(set, lang, now), {
    headers: {
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": `inline; filename="prayer-reminders.ics"`,
      "Cache-Control": "public, max-age=86400",
    },
  });
}
