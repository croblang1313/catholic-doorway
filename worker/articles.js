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
//   GET  /this-week/<slug>/share.jpg the article's share picture (link previews; ?k= for a draft)
//   GET  /this-week/<slug>/article.pdf  the article as a PDF to download (?k= for a draft)
//   POST /api/articles/files         {slug, image?, image_alt?, pdf?}: add or replace an article's
//                                    share picture and/or PDF (also at /api/articles/image)
//
// Share pictures: a draft may carry "image" (a base64 JPEG or PNG, ideally 1200x630) and
// "image_alt". The bytes are kept under article-img:<slug>; the article keeps {v, w, h, type, alt}.
// Article pages point og:image / twitter:image at it, so Facebook, X, WhatsApp and the rest show it
// when the link is shared. Without one, the site's general picture (og.png) is used.
// PDFs: a draft may carry "pdf" (base64, made by tools/articles/make_article_pdf.js). It is kept
// under article-pdf:<slug>; the article keeps {v, size}. Without one, the article's Download PDF
// button opens the browser's print dialog, where "Save as PDF" makes one from the print styles.
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

// ---- Share pictures ---------------------------------------------------------------------

const IMG_MAX = 3000000;

function u16(b, i) { return (b[i] << 8) | b[i + 1]; }

function imageSize(b) {
  if (b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47) {
    return { type: "png", w: (b[16] << 24 | b[17] << 16 | b[18] << 8 | b[19]) >>> 0, h: (b[20] << 24 | b[21] << 16 | b[22] << 8 | b[23]) >>> 0 };
  }
  if (b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i + 9 < b.length) {
      if (b[i] !== 0xff) { i++; continue; }
      const m = b[i + 1];
      if (m === 0xd8 || m === 0x01 || (m >= 0xd0 && m <= 0xd7) || m === 0xff) { i += m === 0xff ? 1 : 2; continue; }
      if ((m >= 0xc0 && m <= 0xc3) || (m >= 0xc5 && m <= 0xc7) || (m >= 0xc9 && m <= 0xcb) || (m >= 0xcd && m <= 0xcf)) {
        return { type: "jpg", h: u16(b, i + 5), w: u16(b, i + 7) };
      }
      i += 2 + u16(b, i + 2);
    }
  }
  return null;
}

// Returns {bytes, meta} for a valid picture, null when none was sent, or "bad".
export async function readImage(v, alt) {
  if (!v) return null;
  let s = String(v).trim();
  const m = /^data:image\/(?:jpeg|jpg|png);base64,/i.exec(s);
  if (m) s = s.slice(m[0].length);
  let bytes;
  try {
    const bin = atob(s.replace(/\s+/g, ""));
    bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  } catch (e) {
    return "bad";
  }
  if (bytes.length < 200 || bytes.length > IMG_MAX) return "bad";
  const size = imageSize(bytes);
  if (!size || !size.w || !size.h || size.w > 4000 || size.h > 4000) return "bad";
  const d = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  const v10 = [...d.slice(0, 5)].map((x) => x.toString(16).padStart(2, "0")).join("");
  return { bytes, meta: { v: v10, w: size.w, h: size.h, type: size.type, alt: clean(alt, 200) } };
}

// Returns {bytes, meta} for a valid PDF, null when none was sent, or "bad".
export async function readPdf(v) {
  if (!v) return null;
  let s = String(v).trim();
  const m = /^data:application\/pdf;base64,/i.exec(s);
  if (m) s = s.slice(m[0].length);
  let bytes;
  try {
    const bin = atob(s.replace(/\s+/g, ""));
    bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  } catch (e) {
    return "bad";
  }
  if (bytes.length < 500 || bytes.length > 8000000) return "bad";
  if (String.fromCharCode(...bytes.slice(0, 5)) !== "%PDF-") return "bad";
  const d = new Uint8Array(await crypto.subtle.digest("SHA-256", bytes));
  return { bytes, meta: { v: [...d.slice(0, 5)].map((x) => x.toString(16).padStart(2, "0")).join(""), size: bytes.length } };
}

export function pdfUrl(a, withKey) {
  return a.pdf ? `/this-week/${a.slug}/article.pdf?v=${a.pdf.v}${withKey ? "&k=" + a.key : ""}` : "";
}

async function articlePdf(request, env, slug, url) {
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a || !a.pdf) return Response.redirect(`${DOMAIN}/this-week/${SLUG.test(slug) ? slug : ""}`, 302);
  const live = a.status === "published";
  if (!live && !same(url.searchParams.get("k") || "", a.key)) return new Response("Not found", { status: 404 });
  const bytes = await env.LISTINGS.get("article-pdf:" + slug, "arrayBuffer");
  if (!bytes) return new Response("Not found", { status: 404 });
  return new Response(bytes, { headers: {
    "Content-Type": "application/pdf",
    "Content-Disposition": `attachment; filename="catholicdoorway-${slug}.pdf"`,
    "Cache-Control": !live ? "no-store" : url.searchParams.get("v") === a.pdf.v ? "public, max-age=31536000, immutable" : "public, max-age=3600",
  } });
}

async function saveImage(env, slug, img) {
  await env.LISTINGS.put("article-img:" + slug, img.bytes, { metadata: { type: img.meta.type } });
}

export function imageUrl(a, withKey) {
  if (!a.image) return `${DOMAIN}/assets/img/og.png`;
  return `${DOMAIN}/this-week/${a.slug}/share.${a.image.type}?v=${a.image.v}${withKey ? "&k=" + a.key : ""}`;
}

async function shareImage(request, env, slug, url) {
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a || !a.image) return new Response("Not found", { status: 404 });
  const live = a.status === "published";
  if (!live && !same(url.searchParams.get("k") || "", a.key)) return new Response("Not found", { status: 404 });
  const bytes = await env.LISTINGS.get("article-img:" + slug, "arrayBuffer");
  if (!bytes) return new Response("Not found", { status: 404 });
  const fixed = url.searchParams.get("v") === a.image.v;
  return new Response(bytes, { headers: {
    "Content-Type": a.image.type === "png" ? "image/png" : "image/jpeg",
    "Cache-Control": !live ? "no-store" : fixed ? "public, max-age=31536000, immutable" : "public, max-age=3600",
  } });
}

async function setFiles(request, env) {
  if (!(await bearerOk(request, env))) return json({ ok: false, error: "unauthorized" }, 401);
  let b;
  try {
    b = await request.json();
  } catch (e) {
    return json({ ok: false, error: "bad_request" }, 400);
  }
  const slug = clean(b.slug, 90);
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a) return json({ ok: false, error: "not_found" }, 404);
  const img = await readImage(b.image, b.image_alt || a.title), pdf = await readPdf(b.pdf);
  const bad = [img === "bad" && "image", pdf === "bad" && "pdf"].filter(Boolean);
  if (bad.length || (!img && !pdf)) return json({ ok: false, error: "invalid", fields: bad.length ? bad : ["image", "pdf"] }, 400);
  if (img) {
    await saveImage(env, slug, img);
    a.image = img.meta;
  }
  if (pdf) {
    await env.LISTINGS.put("article-pdf:" + slug, pdf.bytes);
    a.pdf = pdf.meta;
  }
  await env.LISTINGS.put("article:" + slug, JSON.stringify(a));
  const draft = a.status !== "published";
  return json({ ok: true, slug, image_url: a.image ? imageUrl(a, draft) : "", pdf_url: a.pdf ? DOMAIN + pdfUrl(a, draft) : "" });
}

async function removeArticle(env, slug) {
  await env.LISTINGS.delete("article:" + slug);
  await env.LISTINGS.delete("article-img:" + slug);
  await env.LISTINGS.delete("article-pdf:" + slug);
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
  const img = await readImage(body.image, body.image_alt || a.title), pdf = await readPdf(body.pdf);
  if (img === "bad" || pdf === "bad") return json({ ok: false, error: "invalid", fields: [img === "bad" && "image", pdf === "bad" && "pdf"].filter(Boolean) }, 400);
  const old = await env.LISTINGS.get("article:" + a.slug, "json");
  if (old && old.status === "published") return json({ ok: false, error: "already_published", url: `${DOMAIN}/this-week/${a.slug}` }, 409);
  if (img) await saveImage(env, a.slug, img);
  a.image = img ? img.meta : (old && old.image) || null;
  if (pdf) await env.LISTINGS.put("article-pdf:" + a.slug, pdf.bytes);
  a.pdf = pdf ? pdf.meta : (old && old.pdf) || null;
  a.status = "draft";
  a.created = (old && old.created) || new Date().toISOString();
  a.key = (old && old.key) || crypto.randomUUID().replace(/-/g, "");
  await env.LISTINGS.put("article:" + a.slug, JSON.stringify(a));
  return json({ ok: true, slug: a.slug, url: `${DOMAIN}/this-week/${a.slug}`, review_url: reviewUrl(a), image_url: a.image ? imageUrl(a, true) : "", pdf_url: a.pdf ? DOMAIN + pdfUrl(a, true) : "" }, 201);
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
    status: a.status, published: a.published || "", minutes: minutes(a.body), url: `${DOMAIN}/this-week/${a.slug}`, review_url: reviewUrl(a),
    image_url: a.image ? imageUrl(a, a.status !== "published") : "", pdf_url: a.pdf ? DOMAIN + pdfUrl(a, a.status !== "published") : "" }));
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
    await removeArticle(env, slug);
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

function setMeta(html, { title, desc, url, type, ld, verse, main, noindex, image }) {
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
  if (image) {
    html = html.replace(/(<meta property="og:image" content=")[^"]*"/, `$1${esc(image.url)}"`)
      .replace(/(<meta property="og:image:width" content=")[^"]*"/, `$1${image.w}"`)
      .replace(/(<meta property="og:image:height" content=")[^"]*"/, `$1${image.h}"`)
      .replace(/(<meta property="og:image:alt" content=")[^"]*"/, `$1${esc(image.alt)}"`)
      .replace("</head>", `<meta name="twitter:image" content="${esc(image.url)}">\n<meta name="twitter:image:alt" content="${esc(image.alt)}">\n</head>`);
  }
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

function pdfButton(a, preview) {
  return a.pdf
    ? `<a class="share-btn pdf" href="${esc(pdfUrl(a, preview))}" download>Download PDF</a>`
    : `<button type="button" class="share-btn pdf" data-print>Download PDF</button>`;
}

function shareBox(a, preview) {
  const url = `${DOMAIN}/this-week/${a.slug}`, u = encodeURIComponent(url), t = encodeURIComponent(a.title);
  const links = [
    ["Facebook", `https://www.facebook.com/sharer/sharer.php?u=${u}`],
    ["X", `https://twitter.com/intent/tweet?url=${u}&text=${t}`],
    ["WhatsApp", `https://wa.me/?text=${encodeURIComponent(a.title + " " + url)}`],
    ["Pinterest", `https://www.pinterest.com/pin/create/button/?url=${u}&media=${encodeURIComponent(imageUrl(a))}&description=${t}`],
    ["Email", `mailto:?subject=${t}&body=${encodeURIComponent(a.description + "\n\n" + url)}`],
  ];
  return `<section class="share-box" id="share" aria-label="Download or share this article">
    <div class="share-part share-pdf">
      <h2>Keep a copy</h2>
      <p class="small muted">Download this article as a PDF to read later, print or hand to a friend.</p>
      <div class="share-row">${pdfButton(a, preview)}</div>
    </div>
    <div class="share-part share-social">
      <h2>Share this article</h2>
      <p class="small muted">Know someone who would like this? Send it their way.</p>
      <div class="share-row">${links.map(([n, h]) =>
      `<a class="share-btn" href="${esc(h)}"${n === "Email" ? "" : ' target="_blank" rel="noopener"'}>${n}</a>`).join("")}
      <button type="button" class="share-btn" data-copy-link="${esc(url)}">Copy link</button>
      <button type="button" class="share-btn" data-native-share data-title="${esc(a.title)}" data-url="${esc(url)}" hidden>More&hellip;</button>
      </div>
    </div>
  </section>`;
}

// "More from This Week in the Church": up to 3 other published articles and a link to them all.
function moreBox(a, list) {
  const others = (list || []).filter((x) => x.slug !== a.slug).slice(0, 3);
  const cards = others.map((x) => `<a class="card tile tw-card" href="/this-week/${esc(x.slug)}">
      <p class="label">${esc(x.kicker)}</p><h3>${esc(x.title)}</h3>
      <p class="small muted">${esc(longDate(x.published))} &middot; ${x.minutes || 1} min read</p><span class="go">Read &rarr;</span></a>`).join("");
  return `<section class="section tw-more" aria-labelledby="tw-more-h">
    <h2 id="tw-more-h">More from This Week in the Church</h2>
    <p class="muted">A short article every week on the Church&rsquo;s feasts, saints and seasons.</p>
    ${cards ? `<div class="grid">${cards}</div>` : ""}
    <p class="btn-row"><a class="btn" href="/this-week">See all articles</a> <a class="btn secondary" href="/this-week/feed.xml">Follow with RSS</a></p>
  </section>`;
}

function articleMain(a, preview, list) {
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
    <p class="small muted tw-meta">${when} &middot; ${minutes(a.body)} min read &middot; <a href="#share">Share</a> &middot; ${a.pdf ? `<a href="${esc(pdfUrl(a, preview))}" download>Download PDF</a>` : `<a href="#share" data-print>Download PDF</a>`}</p>
  </div>
</div>
<div class="wrap">
  <article class="section prose tw-article">
${a.body}
  </article>
  ${sources}
  <p class="small muted tw-foot">Written for CatholicDoorway and reviewed before publishing. Scripture quotations are from the Revised Standard Version, Second Catholic Edition. Spot a mistake? Write to <a href="mailto:hello@catholicdoorway.com">hello@catholicdoorway.com</a>.</p>
  ${shareBox(a, preview)}
  ${moreBox(a, list)}
  ${related}
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
      image: imageUrl(a), mainEntityOfPage: { "@id": url + "#webpage" },
      author: { "@id": `${DOMAIN}/#org` }, publisher: { "@id": `${DOMAIN}/#org` },
      wordCount: String(a.body).replace(/<[^>]+>/g, " ").split(/\s+/).filter(Boolean).length });
    return out;
  };
}

function shareMeta(a, withKey) {
  return a.image ? { url: imageUrl(a, withKey), w: a.image.w, h: a.image.h, alt: a.image.alt || a.title } : null;
}

async function articlePage(request, env, slug) {
  const a = SLUG.test(slug) ? await env.LISTINGS.get("article:" + slug, "json") : null;
  if (!a) return env.ASSETS.fetch(new Request(new URL("/this-week/" + slug + "-missing", request.url)));
  // A link shared before the article is published goes to the index instead of a dead end.
  if (a.status !== "published") return Response.redirect(`${DOMAIN}/this-week`, 302);
  const html = setMeta(await shell(request, env), {
    title: `${a.title} | CatholicDoorway`, desc: a.description, url: `/this-week/${a.slug}`, type: "article",
    ld: articleLd(a), verse: a.verse, main: articleMain(a, false, await getIndex(env)), image: shareMeta(a),
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
  ${a.image
    ? `<div class="tw-share-preview"><img src="${esc(imageUrl(a, !live))}" alt="" width="300" height="${Math.round(300 * a.image.h / a.image.w)}"><p class="small">This picture shows when the link is shared on Facebook, X, WhatsApp and other apps.</p></div>`
    : `<p class="small">No share picture yet, so a shared link shows the site&rsquo;s general picture.</p>`}
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
    verse: a.verse, main: reviewBar(a, msg) + articleMain(a, a.status !== "published", await getIndex(env)), image: shareMeta(a, a.status !== "published"),
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
    if (a && action === "delete" && a.status !== "published") await removeArticle(env, slug);
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
  if ((p === "/api/articles/files" || p === "/api/articles/image") && request.method === "POST") return setFiles(request, env);
  if (p === "/this-week/review") return reviewList(request, env);
  let m = /^\/this-week\/review\/([^/]+)$/.exec(p);
  if (m) return reviewArticle(request, env, m[1], url);
  m = /^\/this-week\/([^/]+)\/share\.(?:jpg|png)$/.exec(p);
  if (m) return shareImage(request, env, m[1], url);
  m = /^\/this-week\/([^/]+)\/article\.pdf$/.exec(p);
  if (m) return articlePdf(request, env, m[1], url);
  m = /^\/this-week\/([^/]+)$/.exec(p);
  if (m) {
    if (url.pathname.endsWith("/")) return Response.redirect(`${DOMAIN}/this-week/${m[1]}`, 301);
    return articlePage(request, env, m[1]);
  }
  return json({ ok: false, error: "not_found" }, 404);
}
