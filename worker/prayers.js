// Prayer Wall.
//
//   POST /api/prayer-request  a visitor asks for prayer ({ name, text, private, lang })
//   GET  /api/prayers.json    published requests that have not expired (public fields only)
//   POST /api/prayer-pray     "I prayed" for one request ({ id }); once per visitor per request per day
//   GET  /api/prayer-admin    review page (asks for the ADMIN_TOKEN password)
//   POST /api/prayer-admin    publish, edit, remove or mark a request as prayed for
//
// Stored in the LISTINGS KV namespace (shared with the OCIA listings) under these keys:
//   prayer-pending:<id>  waiting for review, never shown
//   prayer:<id>          published on the wall
//   prayer-private:<id>  "keep it private": only the team sees it, it is never published
// Every one of them expires 30 days after it was sent (KV deletes it on its own).
// Nothing appears on the wall until an administrator approves it.

const DAYS = 30;
const LANGS = ["en", "es", "pt", "tl"];
const NAME_MAX = 40, TEXT_MIN = 8, TEXT_MAX = 500;

// Words that suggest someone may be in danger. They do not block a request: they flag it
// at the top of the review page, and the page itself shows crisis numbers when they are typed.
const CRISIS = /\b(suicid\w*|kill (my ?self|me)|end(ing)? my (own )?life|want(ed)? to die|wanna die|self[- ]?harm|hurt(ing)? my ?self|cutting myself|overdos\w*|quitarme la vida|matarme|me quiero morir|quiero morir(me)?|no quiero vivir|tirar (a )?minha (própria )?vida|me matar|quero morrer|não quero mais viver|magpakamatay|nagpapakamatay|gusto ko nang mamatay|ayoko nang mabuhay|saktan ang sarili)\b/i;
const LINK = /(https?:\/\/|www\.|\b[a-z0-9-]+\.(com|net|org|info|xyz|ru|io|ly|me|biz|shop|top)\b)/i;
const EMAIL = /[^\s@]+@[^\s@]+\.[a-z]{2,}/i;
// A phone number: a run of digits, spaces and ( ) . - + holding 10 or more digits.
const hasPhone = (s) => (s.match(/\+?\d[\d\s().-]{6,}\d/g) || []).some((m) => m.replace(/\D/g, "").length >= 10);

function json(body, status = 200, extra = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...extra },
  });
}

function clean(v, n) {
  return String(v == null ? "" : v).replace(/[\u0000-\u0009\u000b-\u001f\u007f]/g, " ").replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n").trim().slice(0, n);
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

const now = () => Math.floor(Date.now() / 1000);

// Write a request back under its key, keeping its original 30-day end date.
async function keep(env, key, v) {
  if (!v.exp || v.exp - now() < 120) return false;
  await env.LISTINGS.put(key, JSON.stringify(v), { expiration: v.exp });
  return true;
}

export function validate(body) {
  const name = clean(body.name, NAME_MAX).replace(/\n/g, " ");
  const text = clean(body.text, TEXT_MAX + 1);
  const errors = [];
  if (text.length < TEXT_MIN) errors.push("text");
  if (text.length > TEXT_MAX) errors.push("long");
  if (LINK.test(text) || LINK.test(name)) errors.push("link");
  if (EMAIL.test(text) || hasPhone(text) || EMAIL.test(name)) errors.push("contact");
  // A first name only: at most two words, no digits.
  if (name && (name.split(/\s+/).length > 2 || /\d/.test(name))) errors.push("name");
  return {
    f: {
      name, text,
      private: body.private === true,
      lang: LANGS.includes(body.lang) ? body.lang : "en",
      crisis: CRISIS.test(text),
    },
    errors,
  };
}

async function submit(request, env) {
  if (!env.LISTINGS) return json({ ok: false, error: "not_ready" }, 503);
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  // Bots: a hidden field people never fill in, and a form sent under three seconds after loading.
  if (body.website2 || (body.t && Date.now() - Number(body.t) < 3000)) return json({ ok: true });
  const { f, errors } = validate(body);
  if (errors.length) return json({ ok: false, error: "invalid", fields: errors }, 400);
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const rk = "prate:" + (await sha("prayer" + ip + new Date().toISOString().slice(0, 13))).slice(0, 24);
  const n = Number((await env.LISTINGS.get(rk)) || 0);
  if (n >= 3) return json({ ok: false, error: "too_many" }, 429);
  const id = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14) + "-" + crypto.randomUUID().slice(0, 8);
  const v = { ...f, submitted: new Date().toISOString(), exp: now() + DAYS * 86400, count: 0 };
  await env.LISTINGS.put((f.private ? "prayer-private:" : "prayer-pending:") + id, JSON.stringify(v), { expiration: v.exp });
  await env.LISTINGS.put(rk, String(n + 1), { expirationTtl: 3600 });
  return json({ ok: true, private: f.private, crisis: f.crisis });
}

async function listAll(env, prefix) {
  const out = [];
  let cursor;
  do {
    const page = await env.LISTINGS.list({ prefix, cursor });
    const vals = await Promise.all(page.keys.map((k) => env.LISTINGS.get(k.name, "json")));
    page.keys.forEach((k, i) => { if (vals[i]) out.push({ key: k.name, ...vals[i] }); });
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return out;
}

const PUBLIC_URL = "https://catholicdoorway.com/api/prayers.json";

async function published(env, ctx) {
  const headers = { "Cache-Control": "public, max-age=60" };
  if (!env.LISTINGS) return json({ prayers: [], ready: false }, 200, headers);
  const cache = typeof caches !== "undefined" ? caches.default : null;
  const hit = cache && (await cache.match(PUBLIC_URL));
  if (hit) return hit;
  const t = now();
  const rows = (await listAll(env, "prayer:"))
    .filter((r) => !r.exp || r.exp > t)
    .map((r) => ({ id: r.key.slice(7), name: r.name || "", text: r.text, lang: r.lang, date: (r.approved || r.submitted || "").slice(0, 10), sent: (r.submitted || "").slice(0, 10), count: r.count || 0 }))
    .sort((a, b) => (b.sent + b.id).localeCompare(a.sent + a.id));
  const res = json({ prayers: rows, ready: true }, 200, headers);
  if (cache && ctx) ctx.waitUntil(cache.put(PUBLIC_URL, res.clone()));
  return res;
}

async function forget(ctx) {
  if (typeof caches === "undefined") return;
  const p = caches.default.delete(PUBLIC_URL);
  if (ctx) ctx.waitUntil(p);
  else await p;
}

async function pray(request, env, ctx) {
  if (!env.LISTINGS) return json({ ok: false, error: "not_ready" }, 503);
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const id = String(body.id || "");
  if (!/^[\w-]{6,40}$/.test(id)) return json({ ok: false, error: "bad_request" }, 400);
  const key = "prayer:" + id;
  const v = await env.LISTINGS.get(key, "json");
  if (!v) return json({ ok: false, error: "not_found" }, 404);
  // One "I prayed" per visitor per request per day (the button also remembers it on the device).
  const ip = request.headers.get("CF-Connecting-IP") || "unknown";
  const rk = "pprayed:" + (await sha(ip + id + new Date().toISOString().slice(0, 10))).slice(0, 24);
  if (await env.LISTINGS.get(rk)) return json({ ok: true, count: v.count || 0 });
  await env.LISTINGS.put(rk, "1", { expirationTtl: 86400 });
  v.count = (v.count || 0) + 1;
  await keep(env, key, v);
  return json({ ok: true, count: v.count });
}

function page(inner) {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>Prayer Wall review</title>
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 16px;color:#1d2b4f;background:#fbf8f1}
.item{background:#fff;border:1px solid #ddd3bd;border-radius:10px;padding:1rem;margin:1rem 0}.item.crisis{border:2px solid #a8322d}
.flag{display:inline-block;background:#a8322d;color:#fff;border-radius:6px;padding:.1rem .5rem;font-size:.85rem;font-weight:600;margin-bottom:.4rem}
.meta{color:#5b6478;font-size:.9rem}.text{white-space:pre-wrap;margin:.4rem 0 .8rem}
button{font:inherit;padding:.45rem .9rem;border-radius:8px;border:1px solid #1d2b4f;background:#1d2b4f;color:#fff;cursor:pointer}button.no{background:#fff;color:#a8322d;border-color:#a8322d}
input,textarea{font:inherit;padding:.45rem;border:1px solid #bbb;border-radius:8px;box-sizing:border-box}textarea{width:100%;min-height:6rem}
form.inline{display:inline}h2{margin-top:2rem}.edit label{display:block;font-weight:600;margin:.4rem 0}.edit input{width:100%;max-width:20rem}
.help{background:#fff4e5;border-left:4px solid #c8962e;padding:.6rem 1rem;border-radius:0 8px 8px 0}</style></head><body>${inner}</body></html>`,
    { headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": "no-store", "X-Robots-Tag": "noindex", "Referrer-Policy": "no-referrer" } });
}

const LANG_NAME = { en: "English", es: "Spanish", pt: "Portuguese", tl: "Filipino" };

function card(r, token) {
  const hidden = (k, v) => `<input type="hidden" name="${k}" value="${esc(v)}">`;
  const btn = (action, label, cls = "") =>
    `<form class="inline" method="post">${hidden("token", token)}${hidden("key", r.key)}${hidden("action", action)}<button class="${cls}">${label}</button></form>`;
  const left = r.exp ? Math.max(0, Math.ceil((r.exp - now()) / 86400)) : "?";
  const meta = `<p class="meta">${esc(r.name || "Anonymous")} &middot; ${esc(LANG_NAME[r.lang] || r.lang)} &middot; sent ${esc((r.submitted || "").slice(0, 16).replace("T", " "))} UTC &middot; removed in ${left} days${r.count ? ` &middot; prayed for ${r.count} times` : ""}</p>`;
  const flag = r.crisis ? `<span class="flag">May mention self-harm or suicide</span>` : "";
  if (r.key.startsWith("prayer-pending:")) {
    return `<div class="item${r.crisis ? " crisis" : ""}">${flag}${meta}
<form method="post" class="edit">${hidden("token", token)}${hidden("key", r.key)}${hidden("action", "approve")}
<label>Name shown (blank = Anonymous) <input name="name" maxlength="${NAME_MAX}" value="${esc(r.name)}"></label>
<label>Request (edit to remove last names or private details) <textarea name="text" maxlength="${TEXT_MAX}">${esc(r.text)}</textarea></label>
<button>Publish on the wall</button></form> ${btn("reject", "Delete", "no")}</div>`;
  }
  const text = `<p class="text">${esc(r.text)}</p>`;
  if (r.key.startsWith("prayer-private:")) return `<div class="item${r.crisis ? " crisis" : ""}">${flag}${meta}${text}${btn("reject", "Prayed for: remove", "no")}</div>`;
  return `<div class="item">${meta}${text}${btn("reject", "Take down", "no")}</div>`;
}

async function admin(request, env, ctx) {
  if (!env.LISTINGS || !env.ADMIN_TOKEN) return page("<h1>Prayer Wall</h1><p>Not set up yet: bind a KV namespace as LISTINGS and add an ADMIN_TOKEN secret.</p>");
  const login = (msg = "") => page(`<h1>Prayer Wall review</h1>${msg}<form method="post"><label>Admin password <input type="password" name="token" autocomplete="current-password" required></label> <button>Sign in</button></form>`);
  if (request.method !== "POST") return login();
  const form = await request.formData();
  const token = String(form.get("token") || "");
  if (!(await sameSecret(token, env.ADMIN_TOKEN))) return login("<p><strong>That password is not right.</strong></p>");
  const key = String(form.get("key") || ""), action = String(form.get("action") || "");
  let note = "";
  if (key && /^prayer(-pending|-private)?:[\w-]+$/.test(key)) {
    const v = await env.LISTINGS.get(key, "json");
    if (v && action === "approve" && key.startsWith("prayer-pending:")) {
      const name = clean(form.get("name"), NAME_MAX).replace(/\n/g, " ");
      const text = clean(form.get("text"), TEXT_MAX);
      if (text.length >= TEXT_MIN) {
        v.name = name; v.text = text; v.approved = new Date().toISOString();
        if (await keep(env, "prayer:" + key.slice(15), v)) {
          await env.LISTINGS.delete(key);
          await forget(ctx);
          note = "<p>Published.</p>";
        } else note = "<p>That request has nearly reached 30 days, so it was not published.</p>";
      } else note = "<p>The request text is too short to publish.</p>";
    } else if (v && action === "reject") {
      await env.LISTINGS.delete(key);
      if (key.startsWith("prayer:")) await forget(ctx);
      note = "<p>Removed.</p>";
    }
  }
  const [pend, priv, pub] = await Promise.all([listAll(env, "prayer-pending:"), listAll(env, "prayer-private:"), listAll(env, "prayer:")]);
  const order = (a, b) => (b.crisis ? 1 : 0) - (a.crisis ? 1 : 0) || (a.submitted || "").localeCompare(b.submitted || "");
  pend.sort(order); priv.sort(order);
  pub.sort((a, b) => (b.submitted || "").localeCompare(a.submitted || ""));
  const crisis = [...pend, ...priv].some((r) => r.crisis)
    ? `<p class="help"><strong>A request below may mention self-harm or suicide.</strong> The person sees the 988 Suicide &amp; Crisis Lifeline (call or text 988 in the U.S.) on the page and again after sending. We have no way to contact them, so please pray for them, and publish it only if it is safe and kind to show.</p>` : "";
  return page(`<h1>Prayer Wall review</h1>${note}${crisis}
<p>Publish requests that are sincere and safe to show. Take out last names, contact details and private details about other people (you can edit the text before publishing). Every request is deleted automatically 30 days after it was sent. <a href="/prayer-wall">Open the Prayer Wall</a></p>
<h2>Waiting for review (${pend.length})</h2>${pend.map((r) => card(r, token)).join("") || "<p>Nothing waiting.</p>"}
<h2>Private requests, for the team to pray for (${priv.length})</h2><p class="meta">These are never shown on the site.</p>${priv.map((r) => card(r, token)).join("") || "<p>None right now.</p>"}
<h2>On the wall (${pub.length})</h2>${pub.map((r) => card(r, token)).join("") || "<p>None yet.</p>"}`);
}

export function prayers(request, url, env, ctx) {
  const post = (fn) => request.method === "POST" ? fn(request, env, ctx) : json({ ok: false, error: "method" }, 405, { Allow: "POST" });
  if (url.pathname === "/api/prayer-request") return post(submit);
  if (url.pathname === "/api/prayer-pray") return post(pray);
  if (url.pathname === "/api/prayers.json") return published(env, ctx);
  if (url.pathname === "/api/prayer-admin") return admin(request, env, ctx);
  return json({ error: "not_found" }, 404);
}
