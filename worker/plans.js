// Reading plan reminders as a subscribable calendar.
//
//   GET /api/plans.ics?plan=bible|catechism|gospels|ocia&start=YYYY-MM-DD&time=HHMM&lang=en|es|pt|tl
//
// One event per day of the plan, starting on the reader's own start date, at a "floating"
// local time (no time zone) so 7 a.m. means 7 a.m. wherever the person lives. Each event lists
// that day's readings and links straight to them. The schedule comes from the same
// /data/plans-<lang>.json file the Reading Plans page uses (built by src/plans.py).

import { fold, icsEscape } from "./calendar.js";

const LEN = { bible: 365, catechism: 365, gospels: 30, ocia: 90 };
const SITE = "https://catholicdoorway.com";
const PAGE = { en: "/reading-plans", es: "/es/planes-de-lectura", pt: "/pt/planos-de-leitura", tl: "/tl/mga-plano-sa-pagbasa" };
const NAMES = {
  bible: { en: "Bible in a Year", es: "La Biblia en un año", pt: "A Bíblia em um ano", tl: "Ang Bibliya sa isang taon" },
  catechism: { en: "Catechism in a Year", es: "El Catecismo en un año", pt: "O Catecismo em um ano", tl: "Ang Katesismo sa isang taon" },
  gospels: { en: "The Gospels in 30 Days", es: "Los Evangelios en 30 días", pt: "Os Evangelhos em 30 dias", tl: "Ang mga Ebanghelyo sa 30 araw" },
  ocia: { en: "OCIA in 90 Days", es: "OCIA en 90 días", pt: "OCIA em 90 dias", tl: "OCIA sa 90 araw" },
};
const DAY = { en: "Day", es: "Día", pt: "Dia", tl: "Araw" };
const OF = { en: "of", es: "de", pt: "de", tl: "sa" };

const pad = (n) => String(n).padStart(2, "0");
const ymd = (dt) => `${dt.getUTCFullYear()}${pad(dt.getUTCMonth() + 1)}${pad(dt.getUTCDate())}`;

export function plansIcs(data, id, start, hhmm, lang, now = new Date()) {
  const stamp = now.toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";
  const name = NAMES[id][lang];
  const lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//CatholicDoorway//Reading Plans//EN", "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH", fold(`X-WR-CALNAME:${icsEscape(name)}`), "REFRESH-INTERVAL;VALUE=DURATION:P7D", "X-PUBLISHED-TTL:P7D"];
  const days = data[id];
  const s0 = Date.UTC(start.y, start.m - 1, start.d);
  const L = lang === "en" ? "" : `&lang=${lang}`;
  const tag = `${id}-${start.y}${pad(start.m)}${pad(start.d)}${lang === "en" ? "" : "-" + lang}`;
  days.forEach((readings, i) => {
    const n = i + 1, dt = new Date(s0 + i * 86400000);
    const refs = readings.filter((r) => r.k === "b").map((r) => r.r);
    const url = refs.length
      ? `${SITE}/read-the-bible?ref=${refs.join(";")}&plan=${id}&day=${n}${L}`
      : `${SITE}${PAGE[lang]}?plan=${id}&day=${n}`;
    const list = readings.map((r) => (r.k === "c" ? `${r.l} (${r.t}): ${r.u}` : r.l)).join("\n");
    const title = `${name}, ${DAY[lang]} ${n}: ${readings.map((r) => r.l).join(" · ")}`;
    lines.push("BEGIN:VEVENT", `UID:plan-${tag}-${n}@catholicdoorway.com`, `DTSTAMP:${stamp}`,
      `DTSTART:${ymd(dt)}T${hhmm}00`, "DURATION:PT15M", fold(`SUMMARY:${icsEscape(title)}`),
      fold(`DESCRIPTION:${icsEscape(`${DAY[lang]} ${n} ${OF[lang]} ${LEN[id]}\n${list}\n\n${url}`)}`), fold(`URL:${url}`),
      "TRANSP:TRANSPARENT", "BEGIN:VALARM", "ACTION:DISPLAY", fold(`DESCRIPTION:${icsEscape(title)}`), "TRIGGER:PT0M", "END:VALARM",
      "END:VEVENT");
  });
  lines.push("END:VCALENDAR");
  return lines.join("\r\n") + "\r\n";
}

export function parseParams(url, now = new Date()) {
  const q = url.searchParams.get("lang"), lang = q === "es" || q === "pt" || q === "tl" ? q : "en";
  const p = url.searchParams.get("plan"), id = LEN[p] ? p : "bible";
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(url.searchParams.get("start") || "");
  let start = m ? { y: +m[1], m: +m[2], d: +m[3] } : null;
  if (!start || start.y < 2000 || start.y > 2100 || start.m < 1 || start.m > 12 || start.d < 1 || start.d > 31) {
    start = { y: now.getUTCFullYear(), m: now.getUTCMonth() + 1, d: now.getUTCDate() };
  }
  const t = /^([01]\d|2[0-3])([0-5]\d)$/.exec(url.searchParams.get("time") || "");
  const hhmm = t ? t[1] + t[2] : "0700";
  return { id, start, hhmm, lang };
}

export async function plans(request, url, env) {
  const { id, start, hhmm, lang } = parseParams(url);
  const res = await env.ASSETS.fetch(new Request(new URL(`/data/plans-${lang}.json`, url).toString()));
  if (!res.ok) return new Response("Reading plans are unavailable right now.", { status: 503 });
  const data = await res.json();
  return new Response(plansIcs(data, id, start, hhmm, lang), {
    headers: {
      "Content-Type": "text/calendar; charset=utf-8",
      "Content-Disposition": `inline; filename="reading-plan-${id}.ics"`,
      "Cache-Control": "public, max-age=86400",
    },
  });
}
