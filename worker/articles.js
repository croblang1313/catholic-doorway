// "This Week in the Church": short articles on the week's feast, saint or season.
//
// Articles live in the LISTINGS KV namespace, so publishing one needs no rebuild:
//   article:<slug>   the article (draft or published)
//   articles:index   summaries of the published ones, newest first
//
//   POST /api/articles               create or replace a draft (Bearer drafts token or ADMIN_TOKEN)
//   POST /api/articles/publish       {slug, k}: publish with the article's review key
//   GET  /api/articles/latest.json   the newest published article (home-page card)
//   GET  /this-week                  index of published articles
//   GET  /this-week/<slug>           one article; a draft's address sends visitors to the index
//   GET  /this-week/review           list of drafts and articles (asks for the admin password)
//   GET  /this-week/review/<slug>?k= preview a draft exactly as it will look, with a Publish button
//   GET  /this-week/feed.xml         RSS
//   GET  /sitemap-articles.xml       sitemap of published articles
//
// Pages are made from the built /this-week page (src/pages/this-week.html), so they share the
// site's header, menu, footer and verse banner. The drafts token is the Social Posts DRAFTS_TOKEN;
// only its SHA-256 is kept here (ARTICLE_DRAFTS_SHA256 in wrangler.jsonc). Christopher reviews and
// publishes in the Articles tab of Social Posts, which calls GET /api/articles/all and
// POST /api/articles/action with that token from its server. The weekly job is told never to
// publish. The per-article review link and /this-week/review (ADMIN_TOKEN) also work.

const DOMAIN = "https://catholicdoorway.com";
const SLUG = /^[a-z0-9]+(?:-[a-z0-9]+){0,12}$/;
const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
}

function clean(v, n) {
  return String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);
}

function json(body, status = 200, cache = "no-store") {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": cache } });
}

async function sha(s) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

function same(x, y) {
  if (!x || !y || x.length !== y.length) return false;
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x.charCodeAt(i) ^ y.charCodeAt(i);
  return d === 0;
}

async function isAdmin(token, env) {
  return !!token && !!env.ADMIN_TOKEN && same(await sha(token), await sha(env.ADMIN_TOKEN));
}

async function canDraft(token, env) {
  if (!token) return false;
  if (await isAdmin(token, env)) return true;
  const h = await sha(token);
  return [env.ARTICLE_DRAFTS_SHA256, env.ARTICLES_TOKEN && (await sha(env.ARTICLES_TOKEN))].some((x) => x && same(h, String(x).toLowerCase()));
}

export function longDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || "");
  return m ? `${MONTHS[+m[2] - 1]} ${+m[3]}, ${m[1]}` : "";
}

// Article bodies come from Claude through the drafts token, but they are still cut down to a
// small set of tags and attributes before anyone sees them.
const TAGS = new Set(["p", "h2", "h3", "ul", "ol", "li", "blockquote", "strong", "em", "b", "i", "a", "cite", "br", "hr", "small", "sup", "figure", "figcaption"]);

export function sanitize(input) {
  let s = String(input || "").replace(/<!--[\s\S]*?-->/g, "");
  s = s.replace(/<(script|style|iframe|object|embed|template|noscript|svg|math|form)\b[\s\S]*?<\/\1\s*>/gi, "");
  return s.replace(/<\/?([a-zA-Z0-9]+)\b([^>]*)>/g, (all, tag, attrs) => {
    tag = tag.toLowerCase();
    if (!TAGS.has(tag)) return "";
    if (all.startsWith("</")) return tag === "br" || tag === "hr" ? "" : `</${tag}>`;
    let out = "";
    const id = /\bid\s*=\s*"([a-z0-9-]{1,40})"/i.exec(attrs);
    if (id && (tag === "h2" || tag === "h3")) out += ` id="${id[1]}"`;
    if (tag === "a") {
      const h = /\bhref\s*=\s*"([^"]*)"/i.exec(attrs);
      let href = h ? h[1].replace(/&amp;/g, "&").trim() : "";
      if (!/^(https:\/\/|\/(?!\/)|#|mailto:)/i.test(href)) href = "";
      if (href) {
        out += ` href="${esc(href)}"`;
        if (/^https:\/\//i.test(href) && !/^https:\/\/(www\.)?catholicdoorway\.com(\/|$)/i.test(href)) out += ' target="_blank" rel="noopener"';
      }
    }
    if (tag === "blockquote" || tag === "p") {
      const c = /\bclass\s*=\s*"(scripture|ccc|note)"/.exec(attrs);
      if (c) out += ` class="${c[1]}"`;
    }
    return `<${tag}${out}>`;
  });
}

function minutes(body) {
  const words = String(body).replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 220));
}

export function validate(b) {
  const a = {
    slug: clean(b.slug, 90).toLowerCase(),
    title: clean(b.title, 110),
    description: clean(b.description, 300),
    kicker: clean(b.kicker, 90),
    date: /^\d{4}-\d{2}-\d{2}$/.test(String(b.date || "")) ? String(b.date) : "",
    verse: b.verse && typeof b.verse === "object" ? { t: clean(b.verse.t, 260), r: clean(b.verse.r, 60) } : null,
    body: sanitize(b.body).slice(0, 60000),
    related: (Array.isArray(b.related) ? b.related : []).slice(0, 6).map((r) => ({ href: clean(r && r.href, 200), label: clean(r && r.label, 80), note: clean(r && r.note, 140) }))
      .filter((r) => r.label && /^\/(?!\/)[\w\-/#?=&.]*$/.test(r.href)),
    sources: (Array.isArray(b.sources) ? b.sources : []).slice(0, 12).map((r) => ({ label: clean(r && r.label, 200), href: clean(r && r.href, 300) }))
      .map((r) => (/^https:\/\//.test(r.href) ? r : { label: r.label, href: "" })).filter((r) => r.label),
    social: clean(b.social, 400),
  };
  const errors = [];
  if (!SLUG.test(a.slug) || a.slug === "review" || a.slug === "feed") errors.push("slug");
  for (const k of ["title", "description", "kicker", "date"]) if (!a[k]) errors.push(k);
  if (a.body.replace(/<[^>]+>/g, "").trim().length < 400) errors.push("body");
  if (a.verse && (!a.verse.t || !a.verse.r)) a.verse = null;
  return { a, errors };
}

async function getIndex(env) {
  return (await env.LISTINGS.get("articles:index", "json")) || [];
}

async function putIndex(env, list) {
  list.sort((x, y) => (y.published || "").localeCompare(x.published || "") || (y.date || "").localeCompare(x.date || ""));
  await env.LISTINGS.put("articles:index", JSON.stringify(list));
}

function summary(a) {
  return { slug: a.slug, title: a.title, description: a.description, kicker: a.kicker, date: a.date, published: a.published, updated: a.updated || a.published, minutes: minutes(a.body) };
}

async function publish(env, a) {
  const now = new Date().toISOString();
  a.status = "published";
  a.published = a.published || now;
  a.updated = now;
  await env.LISTINGS.put("article:" + a.slug, JSON.stringify(a));
  const list = (await getIndex(env)).filter((x) => x.slug !== a.slug);
  list.push(summary(a));
  await putIndex(env, list);
}

async function unpublish(env, a) {
  a.status = "draft";
  await env.LISTINGS.put("article:" + a.slug, JSON.stringify(a));
  await putIndex(env, (await getIndex(env)).filter((x) => x.slug !== a.slug));
}

function reviewUrl(a) {
  return `${DOMAIN}/this-week/review/${a.slug}?k=${a.key}`;
}

// ---- API ---------------------------------------------------------------------------------

async function createDraft(request, env) {
  const auth = (request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "").trim();
  if (!(await canDraft(auth, env))) return json({ ok: false, error: "unauthorized" }, 401);
  let body;
  try {
    body = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const { a, errors } = validate(body);
  if (errors.length) return json({ ok: false, error: "invalid", fields: errors }, 400);
  const old = await env.LISTINGS.get("article:" + a.slug, "json");
  if (old && old.status === "published") return json({ ok: false, error: "already_published", url: `${DOMAIN}/this-week/${a.slug}` }, 409);
  a.status = "draft";
  a.created = (old && old.created) || new Date().toISOString();
  a.key = (old && old.key) || crypto.randomUUID().replace(/-/g, "");
  await env.LISTINGS.put("article:" + a.slug, JSON.stringify(a));
  return json({ ok: true, slug: a.slug, url: `${DOMAIN}/this-week/${a.slug}`, review_url: reviewUrl(a) }, 201);
}

async function publishByKey(request, env) {
  let b;
  try {
    b = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const slug = clean(b.slug, 90);
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a || !same(String(b.k || ""), a.key)) return json({ ok: false, error: "not_found" }, 404);
  if (a.status !== "published") await publish(env, a);
  return json({ ok: true, url: `${DOMAIN}/this-week/${a.slug}`, published: a.published });
}

// For the Articles tab in Social Posts (social.catholicdoorway.com). That Worker signs Christopher
// in with its own password and calls these with its DRAFTS_TOKEN.
async function bearerOk(request, env) {
  return canDraft((request.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "").trim(), env);
}

async function allForTool(request, env) {
  if (!(await bearerOk(request, env))) return json({ ok: false, error: "unauthorized" }, 401);
  const rows = (await listAll(env)).map((a) => ({ slug: a.slug, title: a.title, description: a.description, kicker: a.kicker, date: a.date,
    status: a.status, published: a.published || "", minutes: minutes(a.body), url: `${DOMAIN}/this-week/${a.slug}`, review_url: reviewUrl(a) }));
  return json({ ok: true, articles: rows });
}

async function actionForTool(request, env) {
  if (!(await bearerOk(request, env))) return json({ ok: false, error: "unauthorized" }, 401);
  let b;
  try {
    b = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const slug = clean(b.slug, 90), action = String(b.action || "");
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a) return json({ ok: false, error: "not_found" }, 404);
  if (action === "publish" && a.status !== "published") await publish(env, a);
  else if (action === "unpublish" && a.status === "published") await unpublish(env, a);
  else if (action === "delete") {
    if (a.status === "published") return json({ ok: false, error: "Unpublish it first." }, 409);
    await env.LISTINGS.delete("article:" + slug);
    return json({ ok: true, deleted: true });
  }
  return json({ ok: true, status: a.status, url: `${DOMAIN}/this-week/${a.slug}` });
}

async function latest(env) {
  const list = await getIndex(env);
  return json({ article: list[0] || null }, 200, "public, max-age=300");
}

// ---- Pages -------------------------------------------------------------------------------

async function shell(request, env) {
  const res = await env.ASSETS.fetch(new Request(new URL("/this-week", request.url)));
  return res.text();
}

function setMeta(html, { title, desc, url, type, ld, verse, main, noindex }) {
  const t = esc(title), d = esc(desc), u = esc(DOMAIN + url);
  html = html.replace(/<title>[\s\S]*?<\/title>/, `<title>${t}</title>`)
    .replace(/(<meta name="description" content=")[^"]*"/, `$1${d}"`)
    .replace(/(<link rel="canonical" href=")[^"]*"/, `$1${u}"`)
    .replace(/(<meta property="og:title" content=")[^"]*"/, `$1${t}"`)
    .replace(/(<meta property="og:description" content=")[^"]*"/, `$1${d}"`)
    .replace(/(<meta property="og:url" content=")[^"]*"/, `$1${u}"`)
    .replace(/<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?/g, "");
  if (type) html = html.replace('<meta property="og:type" content="website">', `<meta property="og:type" content="${type}">`);
  if (noindex) html = html.replace("</head>", '<meta name="robots" content="noindex">\n</head>');
  if (ld) {
    html = html.replace(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/, (all, raw) => {
      let g;
      try {
        g = JSON.parse(raw);
      } catch (e) {
        return all;
      }
      g["@graph"] = ld(g["@graph"] || []);
      return `<script type="application/ld+json">${JSON.stringify(g).replace(/</g, "\\u003c")}</script>`;
    });
  }
  if (verse) {
    html = html.replace(/(<p class="vb-text">)[\s\S]*?(<\/p>)/, `$1&ldquo;${esc(verse.t)}&rdquo;$2`)
      .replace(/(<p class="vb-cite">)[\s\S]*?(<\/p>)/, `$1${esc(verse.r)} &middot; RSV-CE$2`);
  }
  if (main != null) html = html.replace(/<!--TW-->[\s\S]*?<!--\/TW-->/, main);
  return html;
}

function htmlResponse(html, cache = "public, max-age=300", status = 200) {
  return new Response(html, { status, headers: { "Content-Type": "text/html; charset=utf-8", "Cache-Control": cache } });
}

function articleMain(a, preview) {
  const related = a.related.length
    ? `<section class="section tw-related"><h2>Keep going</h2><div class="grid">${a.related.map((r) =>
      `<a class="card tile" href="${esc(r.href)}"><h3>${esc(r.label)}</h3>${r.note ? `<p>${esc(r.note)}</p>` : ""}<span class="go">Open &rarr;</span></a>`).join("")}</div></section>`
    : "";
  const sources = a.sources.length
    ? `<section class="section prose tw-sources"><h2>Sources</h2><ul>${a.sources.map((s) =>
      `<li>${s.href ? `<a href="${esc(s.href)}" target="_blank" rel="noopener">${esc(s.label)}</a>` : esc(s.label)}</li>`).join("")}</ul></section>`
    : "";
  const when = preview ? "Not published yet" : `Published ${longDate(a.published)}`;
  return `<div class="page-head">
  <div class="wrap">
    <p class="kicker"><a href="/this-week">This Week in the Church</a> &rsaquo; ${esc(a.kicker)}</p>
    <h1>${esc(a.title)}</h1>
    <p class="lede">${esc(a.description)}</p>
    <p class="small muted tw-meta">${when} &middot; ${minutes(a.body)} min read</p>
  </div>
</div>
<div class="wrap">
  <article class="section prose tw-article">
${a.body}
  </article>
  ${related}
  ${sources}
  <p class="small muted tw-foot">Written for CatholicDoorway and reviewed before publishing. Scripture quotations are from the Revised Standard Version, Catholic Edition. Spot a mistake? Write to <a href="mailto:hello@catholicdoorway.com">hello@catholicdoorway.com</a>. <a href="/this-week">More from This Week in the Church</a> &middot; <a href="/this-week/feed.xml">RSS</a></p>
</div>`;
}

function articleLd(a) {
  const url = `${DOMAIN}/this-week/${a.slug}`;
  return (graph) => {
    const out = graph.filter((x) => x["@type"] !== "WebPage");
    out.push({ "@type": "WebPage", "@id": url + "#webpage", url, name: a.title, description: a.description, inLanguage: "en",
      isPartOf: { "@id": `${DOMAIN}/#website` }, publisher: { "@id": `${DOMAIN}/#org` },
      breadcrumb: { "@type": "BreadcrumbList", itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: `${DOMAIN}/` },
        { "@type": "ListItem", position: 2, name: "This Week in the Church", item: `${DOMAIN}/this-week` },
        { "@type": "ListItem", position: 3, name: a.title, item: url }] } });
    out.push({ "@type": "Article", "@id": url + "#article", headline: a.title.slice(0, 110), description: a.description,
      datePublished: a.published, dateModified: a.updated || a.published, inLanguage: "en", isAccessibleForFree: true,
      image: `${DOMAIN}/assets/img/og.png`, mainEntityOfPage: { "@id": url + "#webpage" },
      author: { "@id": `${DOMAIN}/#org` }, publisher: { "@id": `${DOMAIN}/#org` },
      wordCount: String(a.body).replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length });
    return out;
  };
}

async function articlePage(request, env, slug) {
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a) return env.ASSETS.fetch(new Request(new URL("/this-week/" + slug + "-missing", request.url)));
  // A link shared before the article is published goes to the index instead of a dead end.
  if (a.status !== "published") return Response.redirect(`${DOMAIN}/this-week`, 302);
  const html = setMeta(await shell(request, env), {
    title: `${a.title} | CatholicDoorway`, desc: a.description, url: `/this-week/${a.slug}`, type: "article",
    ld: articleLd(a), verse: a.verse, main: articleMain(a, false),
  });
  return htmlResponse(html);
}

function indexMain(list) {
  const card = (x, big) => `<a class="card tile tw-card${big ? " tw-lead" : ""}" href="/this-week/${esc(x.slug)}">
      <p class="label">${esc(x.kicker)}</p><h3>${esc(x.title)}</h3><p>${esc(x.description)}</p>
      <p class="small muted">${esc(longDate(x.published))} &middot; ${x.minutes || 1} min read</p><span class="go">Read &rarr;</span></a>`;
  const body = list.length
    ? `<section class="section">${card(list[0], true)}</section>` +
      (list.length > 1 ? `<section class="section"><h2>Earlier articles</h2><div class="grid">${list.slice(1).map((x) => card(x, false)).join("")}</div></section>` : "")
    : `<section class="section"><p class="muted">The first article is on its way. In the meantime, see the <a href="/calendar">holy days calendar</a> and <a href="/advent">Advent and Christmas</a>.</p></section>`;
  return `<div class="page-head">
  <div class="wrap">
    <p class="kicker"><a href="/bible">Bible &amp; Readings</a> &rsaquo; This Week in the Church</p>
    <h1>This Week in the Church</h1>
    <p class="lede">Every week the Church remembers a mystery of Christ, a saint or a season. Here is a short, plain-language article on what this week&rsquo;s feast means, where it comes from and how to keep it.</p>
  </div>
</div>
<div class="wrap">
  ${body}
  <p class="small muted">New articles each week. Follow along with <a href="/this-week/feed.xml">RSS</a> or add the <a href="/calendar">holy days calendar</a> to your phone.</p>
</div>`;
}

async function indexPage(request, env) {
  const list = env.LISTINGS ? await getIndex(env) : [];
  const html = setMeta(await shell(request, env), {
    title: "This Week in the Church: Catholic Feasts and Seasons Explained | CatholicDoorway",
    desc: "Short, plain-language articles on this week's Catholic feasts, saints and seasons: what they mean, where they come from and how to keep them.",
    url: "/this-week", main: indexMain(list),
    ld: (graph) => graph.map((x) => (x["@type"] === "WebPage" ? { ...x, "@type": "CollectionPage",
      mainEntity: { "@type": "ItemList", itemListElement: list.slice(0, 20).map((y, i) => ({ "@type": "ListItem", position: i + 1, url: `${DOMAIN}/this-week/${y.slug}` })) } } : x)),
  });
  return htmlResponse(html);
}

function xmlEsc(s) {
  return String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]);
}

async function feed(env) {
  const list = (env.LISTINGS ? await getIndex(env) : []).slice(0, 30);
  const items = list.map((x) => `<item><title>${xmlEsc(x.title)}</title><link>${DOMAIN}/this-week/${x.slug}</link><guid isPermaLink="true">${DOMAIN}/this-week/${x.slug}</guid><pubDate>${new Date(x.published).toUTCString()}</pubDate><description>${xmlEsc(x.description)}</description></item>`).join("\n");
  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>This Week in the Church | CatholicDoorway</title><link>${DOMAIN}/this-week</link>
<atom:link href="${DOMAIN}/this-week/feed.xml" rel="self" type="application/rss+xml"/>
<description>Short, plain-language articles on this week's Catholic feasts, saints and seasons.</description><language>en-us</language>
${items}
</channel></rss>`;
  return new Response(xml, { headers: { "Content-Type": "application/rss+xml; charset=utf-8", "Cache-Control": "public, max-age=900" } });
}

async function sitemap(env) {
  const list = env.LISTINGS ? await getIndex(env) : [];
  const rows = [`  <url><loc>${DOMAIN}/this-week</loc>${list[0] ? `<lastmod>${(list[0].updated || list[0].published).slice(0, 10)}</lastmod>` : ""}</url>`]
    .concat(list.map((x) => `  <url><loc>${DOMAIN}/this-week/${x.slug}</loc><lastmod>${(x.updated || x.published).slice(0, 10)}</lastmod></url>`));
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${rows.join("\n")}\n</urlset>\n`,
    { headers: { "Content-Type": "application/xml; charset=utf-8", "Cache-Control": "public, max-age=900" } });
}

// ---- Review ------------------------------------------------------------------------------

const PRIVATE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex", "Referrer-Policy": "no-referrer" };

function plain(inner, title = "Articles review") {
  return new Response(`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>${esc(title)}</title>
<style>body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 16px;color:#1d2b4f;background:#fbf8f1}
.item{background:#fff;border:1px solid #ddd3bd;border-radius:10px;padding:1rem;margin:1rem 0}.item h3{margin:.1rem 0 .3rem}
button{font:inherit;padding:.45rem .9rem;border-radius:8px;border:1px solid #1d2b4f;background:#1d2b4f;color:#fff;cursor:pointer}button.no{background:#fff;color:#a8322d;border-color:#a8322d}
input{font:inherit;padding:.45rem;border:1px solid #bbb;border-radius:8px}form.inline{display:inline}.muted{color:#5d6680}</style></head><body>${inner}</body></html>`,
    { headers: { "Content-Type": "text/html; charset=utf-8", ...PRIVATE } });
}

function reviewBar(a, msg) {
  const live = a.status === "published";
  const btn = (action, label, cls = "") => `<form method="post" style="display:inline"><input type="hidden" name="k" value="${esc(a.key)}"><input type="hidden" name="action" value="${action}"><button class="btn${cls}" type="submit">${label}</button></form>`;
  return `<div class="tw-review" role="region" aria-label="Review"><div class="wrap">
  <p><strong>${live ? "This article is live." : "Preview: not published yet."}</strong> ${msg || (live ? `It is at <a href="/this-week/${esc(a.slug)}">/this-week/${esc(a.slug)}</a>.` : "Read it through. When it looks right, publish it. You can unpublish it any time.")}</p>
  <div class="btn-row">${live ? `<a class="btn secondary" href="/this-week/${esc(a.slug)}">Open the live page</a> ${btn("unpublish", "Unpublish", " secondary")}` : btn("publish", "Publish now")}</div>
</div></div>`;
}

async function reviewArticle(request, env, slug, url) {
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  let k = url.searchParams.get("k") || "";
  let msg = "";
  if (request.method === "POST") {
    const form = await request.formData();
    k = String(form.get("k") || "");
    if (a && same(k, a.key)) {
      const action = String(form.get("action") || "");
      if (action === "publish" && a.status !== "published") {
        await publish(env, a);
        msg = `Published. It is live at <a href="/this-week/${esc(a.slug)}">/this-week/${esc(a.slug)}</a>.`;
      } else if (action === "unpublish" && a.status === "published") {
        await unpublish(env, a);
        msg = "Unpublished. It is a draft again and no longer on the site.";
      }
    }
  }
  if (!a || !same(k, a.key)) return plain("<h1>Article not found</h1><p>This review link is not right or the article was removed. Sign in at <a href=\"/this-week/review\">/this-week/review</a> to see every article.</p>");
  let html = setMeta(await shell(request, env), {
    title: `Review: ${a.title}`, desc: a.description, url: `/this-week/${a.slug}`, noindex: true,
    verse: a.verse, main: reviewBar(a, msg) + articleMain(a, a.status !== "published"),
  });
  return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8", ...PRIVATE } });
}

async function listAll(env) {
  const out = [];
  let cursor;
  do {
    const page = await env.LISTINGS.list({ prefix: "article:", cursor });
    for (const k of page.keys) {
      const v = await env.LISTINGS.get(k.name, "json");
      if (v) out.push(v);
    }
    cursor = page.list_complete ? null : page.cursor;
  } while (cursor);
  return out.sort((x, y) => (y.date || "").localeCompare(x.date || ""));
}

async function reviewList(request, env) {
  if (!env.ADMIN_TOKEN) return plain("<h1>Articles review</h1><p>Add an ADMIN_TOKEN secret first.</p>");
  const login = (m = "") => plain(`<h1>This Week in the Church: review</h1>${m}<p class="muted">Use the same admin password as the OCIA listings review.</p><form method="post"><label>Admin password <input type="password" name="token" autocomplete="current-password" required></label> <button>Sign in</button></form>`);
  if (request.method !== "POST") return login();
  const form = await request.formData();
  const token = String(form.get("token") || "");
  if (!(await isAdmin(token, env))) return login("<p><strong>That password is not right.</strong></p>");
  const slug = String(form.get("slug") || ""), action = String(form.get("action") || "");
  if (SLUG.test(slug) && action) {
    const a = await env.LISTINGS.get("article:" + slug, "json");
    if (a && action === "publish" && a.status !== "published") await publish(env, a);
    if (a && action === "unpublish" && a.status === "published") await unpublish(env, a);
    if (a && action === "delete" && a.status !== "published") await env.LISTINGS.delete("article:" + slug);
  }
  const all = await listAll(env);
  const btn = (a, action, label, cls = "") => `<form class="inline" method="post"><input type="hidden" name="token" value="${esc(token)}"><input type="hidden" name="slug" value="${esc(a.slug)}"><input type="hidden" name="action" value="${action}"><button class="${cls}">${label}</button></form>`;
  const item = (a) => `<div class="item"><p class="muted" style="margin:0">${esc(a.kicker)} &middot; ${esc(a.date)}</p><h3>${esc(a.title)}</h3><p style="margin:.2rem 0 .6rem">${esc(a.description)}</p>
    <a href="/this-week/review/${esc(a.slug)}?k=${esc(a.key)}" target="_blank" rel="noopener">Read the preview</a> &nbsp;
    ${a.status === "published" ? `<a href="/this-week/${esc(a.slug)}" target="_blank" rel="noopener">Live page</a> ${btn(a, "unpublish", "Unpublish", "no")}` : `${btn(a, "publish", "Publish")} ${btn(a, "delete", "Delete draft", "no")}`}</div>`;
  const drafts = all.filter((a) => a.status !== "published"), live = all.filter((a) => a.status === "published");
  return plain(`<h1>This Week in the Church: review</h1>
<h2>Drafts (${drafts.length})</h2>${drafts.map(item).join("") || "<p>Nothing waiting.</p>"}
<h2>Published (${live.length})</h2>${live.map(item).join("") || "<p>None yet.</p>"}`);
}

// ---- Router ------------------------------------------------------------------------------

export async function articles(request, url, env) {
  const p = url.pathname.replace(/\/+$/, "") || "/";
  if (p === "/sitemap-articles.xml") return sitemap(env);
  if (p === "/this-week/feed.xml") return feed(env);
  if (p === "/this-week") return indexPage(request, env);
  if (!env.LISTINGS) {
    if (p.startsWith("/api/")) return json({ ok: false, error: "not_ready" }, 503);
    return Response.redirect(`${DOMAIN}/this-week`, 302);
  }
  if (p === "/api/articles" && request.method === "POST") return createDraft(request, env);
  if (p === "/api/articles/publish" && request.method === "POST") return publishByKey(request, env);
  if (p === "/api/articles/latest.json") return latest(env);
  if (p === "/api/articles/all" && request.method === "GET") return allForTool(request, env);
  if (p === "/api/articles/action" && request.method === "POST") return actionForTool(request, env);
  if (p === "/this-week/review") return reviewList(request, env);
  let m = /^\/this-week\/review\/([^/]+)$/.exec(p);
  if (m) return reviewArticle(request, env, m[1], url);
  m = /^\/this-week\/([^/]+)$/.exec(p);
  if (m) {
    if (url.pathname.endsWith("/")) return Response.redirect(`${DOMAIN}/this-week/${m[1]}`, 301);
    return articlePage(request, env, m[1]);
  }
  return json({ ok: false, error: "not_found" }, 404);
}
