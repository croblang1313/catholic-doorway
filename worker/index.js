// CatholicDoorway Worker.
// Serves the static site from ./site, plus one small API:
//   GET /api/readings?date=YYYY-MM-DD
//   GET /api/calendar.ics and /api/calendar.json (see calendar.js)
// It returns the day's liturgical title and the list of reading citations
// (e.g. "Luke 19:1-10") with links to the USCCB pages. It never copies the
// Scripture text or audio itself, which belong to the USCCB.

import { calendar } from "./calendar.js";

const MONTHS = ["january", "february", "march", "april", "may", "june", "july",
  "august", "september", "october", "november", "december"];

function json(body, status = 200, maxAge = 3600) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": `public, max-age=${maxAge}`,
    },
  });
}

function clean(s) {
  return s.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/\s+/g, " ").trim();
}

async function readings(url, env, ctx) {
  const base = env.USCCB_BASE || "https://bible.usccb.org"; // overridable for local tests
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(url.searchParams.get("date") || "");
  if (!m) return json({ error: "Use ?date=YYYY-MM-DD" }, 400, 60);
  const [, y, mo, d] = m;
  const page = `${base}/bible/readings/${mo}${d}${y.slice(2)}.cfm`;
  const audio = `https://bible.usccb.org/podcasts/audio/daily-mass-reading-podcast-${MONTHS[+mo - 1]}-${+d}-${y}`;

  const cache = caches.default;
  const cacheKey = new Request(`https://catholicdoorway.com/api/readings?date=${y}-${mo}-${d}`);
  const hit = await cache.match(cacheKey);
  if (hit) return hit;

  let res;
  try {
    res = await fetch(page, { headers: { "User-Agent": "CatholicDoorway.com (readings links)" }, cf: { cacheTtl: 3600 } });
  } catch (e) {
    return json({ page, audio, error: "unavailable" }, 200, 120);
  }
  if (!res.ok) return json({ page, audio, error: "unavailable" }, 200, 120);

  const out = { date: `${y}-${mo}-${d}`, page, audio, video: null, title: "", lectionary: "", readings: [] };
  let cur = null, inTitle = false, inName = false, inAddr = false;

  const rewritten = new HTMLRewriter()
    .on("h2:not(.visually-hidden)", {
      element() { inTitle = !out.title_done; },
      text(t) { if (inTitle) { out.title += t.text; if (t.lastInTextNode) { inTitle = false; out.title_done = true; } } },
    })
    .on("header.content-header h3.name", {
      element() { cur = { name: "", citation: "", url: "" }; out.readings.push(cur); inName = true; },
      text(t) { if (inName && cur) { cur.name += t.text; if (t.lastInTextNode) inName = false; } },
    })
    .on("header.content-header p.address a", {
      element(el) { if (cur && !cur.url) { cur.url = (el.getAttribute("href") || "").trim(); inAddr = true; } },
      text(t) { if (inAddr && cur) { cur.citation += t.text; if (t.lastInTextNode) inAddr = false; } },
    })
    .on('a[href*="/podcasts/video/"]', {
      element(el) { const h = el.getAttribute("href"); if (!out.video && h && /\/podcasts\/video\/\d{4}-/.test(h)) out.video = h.startsWith("http") ? h : "https://bible.usccb.org" + h; },
    })
    .on("div.innerblock, p", {
      text(t) { if (!out.lectionary) { const m2 = /Lectionary:\s*(\d+)/.exec(t.text); if (m2) out.lectionary = m2[1]; } },
    })
    .transform(res);
  await rewritten.text();

  delete out.title_done;
  out.title = clean(out.title);
  out.readings = out.readings
    .map((r) => ({ name: clean(r.name), citation: clean(r.citation), url: r.url.startsWith("http") ? r.url : "" }))
    .filter((r) => r.name && r.citation)
    .slice(0, 12);

  const response = json(out, 200, out.readings.length ? 21600 : 300);
  if (out.readings.length) ctx.waitUntil(cache.put(cacheKey, response.clone()));
  return response;
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname === "/api/readings") return readings(url, env, ctx);
    if (url.pathname === "/api/calendar.ics" || url.pathname === "/api/calendar.json") return calendar(url);
    return env.ASSETS.fetch(request);
  },
};
