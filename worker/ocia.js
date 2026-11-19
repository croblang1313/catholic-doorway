// Parish OCIA self-listing.
//
//   POST /api/ocia-listing        a parish submits its OCIA contact (JSON body)
//   GET  /api/ocia-listings.json  approved listings, public fields only
//   GET  /api/ocia-admin          review page (asks for the admin password)
//   POST /api/ocia-admin          approve or remove a listing
//
// Needs a KV namespace bound as LISTINGS and a secret ADMIN_TOKEN (see README).
// Until they exist, the endpoints answer 503 and the form offers email instead.
// Nothing is published until an administrator approves it.

const MAX = { parish: 120, city: 80, state: 40, diocese: 120, contact: 80, role: 60, email: 120, phone: 40, website: 200, schedule: 300, start: 120, masses: 400, notes: 600 };
const LANGS = ["en", "es", "pt", "tl", "other"];
const PUBLIC = ["parish", "city", "state", "diocese", "contact", "role", "email", "phone", "website", "schedule", "start", "masses", "langs", "notes", "approved"];

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra },
  });
}

function clean(v, n) {
  return String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

async function sha(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

async function sameSecret(a, b) {
  if (!a || !b) return false;
  const [x, y] = await Promise.all([sha(a), sha(b)]);
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return d === 0;
}

export function validate(body) {
  const f = {};
  for (const k of Object.keys(MAX)) f[k] = clean(body[k], MAX[k]);
  f.langs = Array.isArray(body.langs) ? body.langs.filter((l) => LANGS.includes(l)) : [];
  const errors = [];
  for (const k of ["parish", "city", "state", "contact", "email"]) if (!f[k]) errors.push(k);
  if (f.email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f.email)) errors.push("email");
  if (f.website && !/^https?:\/\//i.test(f.website)) f.website = "https://" + f.website;
  if (f.website && !/^https?:\/\/[^\s/]+\.[^\s]+$/i.test(f.website)) errors.push("website");
  if (body.consent !== true) errors.push("consent");
  return { f, errors: [...new Set(errors)] };
}

async function submit(request, env) {
  if (!env.LISTINGS) return json({ ok: false, error: "not_ready" }, 503);
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  // Bots: a hidden field people never fill in, and a form filled in under three seconds.
  if (body.website2 || (body.t && Date.now() - Number(body.t) < 3000)) return json({ ok: true });
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const rk = "rate:" + (await sha(ip + new Date().toISOString().slice(0, 13))).slice(0, 24);
  const n = Number((await env.LISTINGS.get(rk)) || 0);
  if (n >= 5) return json({ ok: false, error: "too_many" }, 429);
  const { f, errors } = validate(body);
  if (errors.length) return json({ ok: false, error: "invalid", fields: errors }, 400);
  const id = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14) + "-" + crypto.randomUUID().slice(0, 8);
  f.submitted = new Date().toISOString();
  f.lang = ["en", "es", "pt", "tl"].includes(body.lang) ? body.lang : "en";
  await env.LISTINGS.put("pending:" + id, JSON.stringify(f));
  await env.LISTINGS.put(rk, String(n + 1), { expirationTtl: 3600 });
  return json({ ok: true, id });
}

async function listAll(env, prefix) {
  const out = [];
  let cursor;
  do {
    const page = await env.LISTINGS.list({ prefix, cursor });
    for (const k of page.keys) {
      const v = await env.LISTINGS.get(k.name, "json");
      if (v) out.push({ key: k.name, ...v });
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return out;
}

async function approved(env) {
  if (!env.LISTINGS) return json({ listings: [], ready: false }, 200, { "Cache-Control": "public, max-age=300" });
  const rows = (await listAll(env, "approved:")).map((r) => Object.fromEntries(PUBLIC.map((k) => [k, r[k] || (k === "langs" ? [] : "")])));
  rows.sort((a, b) => (a.state + a.city + a.parish).localeCompare(b.state + b.city + b.parish));
  return json({ listings: rows, ready: true }, 200, { "Cache-Control": "public, max-age=300" });
}

function page(inner) {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>OCIA listings review</title>
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 16px;color:#1d2b4f;background:#fbf8f1}
.item{background:#fff;border:1px solid #ddd3bd;border-radius:10px;padding:1rem;margin:1rem 0}dl{display:grid;grid-template-columns:9rem 1fr;gap:.2rem .8rem;margin:.5rem 0}dt{font-weight:600}dd{margin:0;overflow-wrap:anywhere}
button{font:inherit;padding:.45rem .9rem;border-radius:8px;border:1px solid #1d2b4f;background:#1d2b4f;color:#fff;cursor:pointer}button.no{background:#fff;color:#a8322d;border-color:#a8322d}
input{font:inherit;padding:.45rem;border:1px solid #bbb;border-radius:8px}form.inline{display:inline}h2{margin-top:2rem}</style></head><body>${inner}</body></html>`,
    { headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store", "X-Robots-Tag": "noindex", "Referrer-Policy": "no-referrer" } });
}

function card(r, token) {
  const rows = ["parish", "city", "state", "diocese", "contact", "role", "email", "phone", "website", "schedule", "start", "masses", "notes"]
    .filter((k) => r[k]).map((k) => `<dt>${k}</dt><dd>${esc(r[k])}</dd>`).join("");
  const langs = (r.langs || []).length ? `<dt>languages</dt><dd>${esc(r.langs.join(", "))}</dd>` : "";
  const btn = (action, label, cls = "") =>
    `<form class="inline" method="post"><input type="hidden" name="token" value="${esc(token)}"><input type="hidden" name="key" value="${esc(r.key)}"><input type="hidden" name="action" value="${action}"><button class="${cls}">${label}</button></form>`;
  const pending = r.key.startsWith("pending:");
  return `<div class="item"><dl>${rows}${langs}<dt>submitted</dt><dd>${esc(r.submitted || "")}</dd></dl>${pending ? btn("approve", "Approve and publish") + " " + btn("reject", "Delete", "no") : btn("remove", "Unpublish", "no")}</div>`;
}

async function admin(request, env) {
  if (!env.LISTINGS || !env.ADMIN_TOKEN) return page("<h1>OCIA listings</h1><p>Not set up yet: bind a KV namespace as LISTINGS and add an ADMIN_TOKEN secret.</p>");
  const login = (msg = "") => page(`<h1>OCIA listings review</h1>${msg}<form method="post"><label>Admin password <input type="password" name="token" autocomplete="current-password" required></label> <button>Sign in</button></form>`);
  if (request.method !== "POST") return login();
  const form = await request.formData();
  const token = String(form.get("token") || "");
  if (!(await sameSecret(token, env.ADMIN_TOKEN))) return login("<p><strong>That password is not right.</strong></p>");
  const key = String(form.get("key") || ""), action = String(form.get("action") || "");
  let note = "";
  if (key && /^(pending|approved):[\w-]+$/.test(key)) {
    const v = await env.LISTINGS.get(key, "json");
    if (v && action === "approve" && key.startsWith("pending:")) {
      v.approved = new Date().toISOString().slice(0, 10);
      await env.LISTINGS.put("approved:" + key.slice(8), JSON.stringify(v));
      await env.LISTINGS.delete(key);
      note = `<p>Published ${esc(v.parish)}.</p>`;
    } else if (v && (action === "reject" || action === "remove")) {
      await env.LISTINGS.delete(key);
      note = `<p>Removed ${esc(v.parish)}.</p>`;
    }
  }
  const [pend, appr] = await Promise.all([listAll(env, "pending:"), listAll(env, "approved:")]);
  return page(`<h1>OCIA listings review</h1>${note}<p>Check each parish before publishing, for example by calling the parish office or looking for the contact on the parish website.</p>
<h2>Waiting for review (${pend.length})</h2>${pend.map((r) => card(r, token)).join("") || "<p>Nothing waiting.</p>"}
<h2>Published (${appr.length})</h2>${appr.map((r) => card(r, token)).join("") || "<p>None yet.</p>"}`);
}

export function ocia(request, url, env) {
  if (url.pathname === "/api/ocia-listing") {
    if (request.method !== "POST") return json({ ok: false, error: "method" }, 405, { Allow: "POST" });
    return submit(request, env);
  }
  if (url.pathname === "/api/ocia-listings.json") return approved(env);
  if (url.pathname === "/api/ocia-admin") return admin(request, env);
  return json({ error: "not_found" }, 404);
}
