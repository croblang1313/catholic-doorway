/**
 * Social Posts — a Cloudflare Worker.
 *
 * Write a post once, preview it for every platform, approve it. Facebook and
 * Instagram post automatically through Meta's Graph API (free). X, YouTube,
 * TikTok and Pinterest finish from a phone's share button (free).
 *
 * Needs (Worker → Settings → Variables and Bindings):
 *   SOCIAL          KV namespace binding (required)
 *   ADMIN_PASSWORD  secret: the sign-in password (required)
 *   SESSION_SECRET  secret: any long random text (optional, recommended)
 *   DRAFTS_TOKEN    secret: lets Claude or a script leave drafts (optional)
 *   SITE_NAME       text: shown on the page (optional)
 *
 * Version 1.2.0-cd (Catholic Doorway: Facebook, Instagram, X, TikTok only; optional post_on date on drafts). License: GPL-2.0-or-later.
 */

const VERSION = '1.0.0';
const GRAPH = 'https://graph.facebook.com/';
const MAX_MEDIA = 25 * 1024 * 1024; // Workers KV value limit.
const PLATFORMS = {
	facebook: { label: 'Facebook', photo: true, video: true },
	instagram: { label: 'Instagram', photo: true, video: true },
	x: { label: 'X (Twitter)', photo: true, video: true },
	tiktok: { label: 'TikTok', photo: true, video: true },
};
const DEFAULT_SETTINGS = {
	test_mode: true,
	site_name: '',
	site_link: 'https://catholicdoorway.com',
	accent: '#a8802f',
	facebook_via: 'meta',
	instagram_via: 'meta',
	default_platforms: ['facebook', 'instagram'],
	graph_version: 'v24.0',
	meta_page_id: '',
	meta_page: '',
	meta_token: '',
	meta_ig_id: '',
	meta_ig_user: '',
	meta_at: 0,
};

const APP_HTML = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<meta name=\"robots\" content=\"noindex, nofollow\">\n<title>Social Posts</title>\n<style>\n:root{--accent:#2563eb;--ink:#16181d;--muted:#5d6470;--line:#e2e5ea;--bg:#f6f7f9;--card:#fff;--ok:#157f3b;--bad:#b42318;--warn:#a15c07;--radius:12px}\n*{box-sizing:border-box}\nhtml,body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,\"Segoe UI\",Roboto,Helvetica,Arial,sans-serif}\na{color:var(--accent)}\nbutton,input,select,textarea{font:inherit;color:inherit}\n.bar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;background:var(--ink);color:#fff;border-bottom:3px solid var(--accent)}\n.bar strong{font-size:17px}\n.bar .who{font-size:14px;opacity:.9}\n.bar button{background:none;border:0;color:#fff;text-decoration:underline;cursor:pointer;padding:0 0 0 6px}\nmain{max-width:1080px;margin:0 auto;padding:20px 16px 60px}\nh1{font-size:24px;margin:4px 0 16px}\nh2{font-size:18px;margin:0 0 12px}\n.card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px;margin:0 0 16px}\n.banner{border-left:4px solid var(--accent);background:#fff;padding:10px 14px;border-radius:8px;margin:0 0 16px;font-size:15px}\n.banner.test{border-color:var(--warn);background:#fff8eb}\n.msg{padding:10px 14px;border-radius:8px;margin:0 0 16px;font-size:15px}\n.msg.ok{background:#e9f7ee;color:var(--ok)}\n.msg.err{background:#fdecea;color:var(--bad)}\n.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 16px}\n.tabs a{padding:8px 14px;border-radius:999px;background:#fff;border:1px solid var(--line);text-decoration:none;color:var(--ink);font-weight:600;font-size:15px}\n.tabs a.on{background:var(--accent);border-color:var(--accent);color:#fff}\n.btn{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:44px;padding:8px 18px;border-radius:10px;border:1px solid var(--accent);background:var(--accent);color:#fff;font-weight:600;cursor:pointer;text-decoration:none}\n.btn.ghost{background:#fff;color:var(--accent)}\n.btn.danger{background:#fff;color:var(--bad);border-color:#f0c6c2}\n.btn:disabled{opacity:.6;cursor:wait}\n.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}\nlabel.field{display:block;font-weight:600;margin:14px 0 6px}\ninput[type=text],input[type=password],input[type=url],textarea,select{width:100%;padding:10px 12px;border:1px solid #c9ced6;border-radius:8px;background:#fff}\ntextarea{min-height:140px;resize:vertical}\n.hint{color:var(--muted);font-size:14px;margin:6px 0 0}\n.counts{display:flex;gap:12px;flex-wrap:wrap;font-size:13px;color:var(--muted);margin-top:4px}\n.counts .over{color:var(--bad);font-weight:700}\n.seg{display:inline-flex;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff}\n.seg button{border:0;background:none;padding:10px 18px;font-weight:600;cursor:pointer;min-height:44px}\n.seg button.on{background:var(--accent);color:#fff}\n.plats{display:flex;flex-wrap:wrap;gap:8px}\n.plats label{display:flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:10px;padding:8px 12px;background:#fff;cursor:pointer;min-height:44px}\n.thumbs{display:flex;flex-wrap:wrap;gap:10px;margin:10px 0}\n.thumb{position:relative;width:104px;height:104px;border-radius:10px;overflow:hidden;background:#e9ecf0;border:1px solid var(--line)}\n.thumb img,.thumb video{width:100%;height:100%;object-fit:cover;display:block}\n.thumb .x{position:absolute;top:4px;right:4px;width:28px;height:28px;border-radius:50%;border:0;background:rgba(0,0,0,.65);color:#fff;cursor:pointer;font-size:16px;line-height:1}\n.thumb .mv{position:absolute;bottom:4px;left:4px;width:28px;height:28px;border-radius:50%;border:0;background:rgba(0,0,0,.65);color:#fff;cursor:pointer}\n.thumb .bar2{position:absolute;left:0;right:0;bottom:0;height:5px;background:rgba(0,0,0,.2)}\n.thumb .bar2 i{display:block;height:100%;background:var(--accent);width:0}\n.drop{border:2px dashed #c9ced6;border-radius:12px;padding:18px;text-align:center;background:#fff;cursor:pointer}\n.drop.hot{border-color:var(--accent);background:#eef3ff}\ntable.list{width:100%;border-collapse:collapse;font-size:15px}\ntable.list th,table.list td{text-align:left;padding:10px 8px;border-bottom:1px solid var(--line);vertical-align:top}\ntable.list a{font-weight:600}\n.pill{display:inline-block;padding:2px 10px;border-radius:999px;font-size:13px;font-weight:600;background:#eef0f3;color:var(--muted);white-space:nowrap}\n.pill.draft{background:#fff1d6;color:var(--warn)}\n.pill.sent{background:#e2f5e9;color:var(--ok)}\n.coach{border-color:#e6d3a3;background:#fffdf7}\n.coach .score{display:inline-flex;align-items:baseline;gap:2px;font-weight:700;font-size:28px;color:var(--accent)}\n.coach .score small{font-size:15px;color:var(--muted);font-weight:600}\n.coach .sc{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:4px 16px;margin:10px 0 0;padding:0;list-style:none;font-size:14px;color:var(--muted)}\n.coach .sc b{color:var(--ink)}\n.coach .alt{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:10px 0 0;background:#fff}\n.coach .alt p{margin:0 0 8px;white-space:pre-wrap}\n.coach details{margin-top:10px}\n.sc-hi,.sc-mid,.sc-lo{display:inline-block;font-weight:800;border-radius:999px;padding:1px 9px;line-height:1.5}\n.sc-hi{background:#16a34a;color:#fff}.sc-mid{background:#facc15;color:#1f1a00}.sc-lo{background:#dc2626;color:#fff}\n.coach .score.sc-hi,.coach .score.sc-mid,.coach .score.sc-lo{font-size:26px;padding:4px 16px}\n.coach .score.sc-hi small,.coach .score.sc-lo small{color:rgba(255,255,255,.85)}.coach .score.sc-mid small{color:#4a3f00}\ntr.day td{background:#f3ead6;color:#5b4413;font-weight:700;font-size:14px;letter-spacing:.04em;text-transform:uppercase;padding:8px 12px}\n.pill.failed{background:#fdecea;color:var(--bad)}\n.pill.todo,.pill.processing{background:#e8efff;color:var(--accent)}\n.pv-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px}\n.pv{background:#fff;border:1px solid var(--line);border-radius:12px;overflow:hidden;margin:0}\n.pv-head{display:flex;gap:10px;align-items:center;padding:12px}\n.av{width:38px;height:38px;border-radius:50%;background:var(--accent);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex:none}\n.pv-sub{color:var(--muted);font-size:13px}\n.pv-text{padding:0 12px 12px;white-space:pre-wrap;word-wrap:break-word;font-size:15px}\n.pv-media{position:relative;background:#111}\n.pv-media img,.pv-media video{display:block;width:100%;max-height:420px;object-fit:cover}\n.pv-media .more{position:absolute;right:10px;bottom:10px;background:rgba(0,0,0,.7);color:#fff;border-radius:999px;padding:2px 10px;font-size:13px}\n.pv.instagram .pv-media img{aspect-ratio:4/5}\n.pv.tiktok .pv-media video,.pv.youtube .pv-media video{aspect-ratio:9/16;max-height:480px;object-fit:cover}\n.pv-note{padding:8px 12px;font-size:13px;color:var(--muted);border-top:1px solid var(--line)}\n.pv-note.bad{color:var(--bad)}\n.results{list-style:none;margin:0;padding:0}\n.results li{padding:10px 0;border-bottom:1px solid var(--line)}\n.results li:last-child{border:0}\n.ok{color:var(--ok)}.bad{color:var(--bad)}\n.phone{border:1px solid var(--line);border-radius:12px;padding:14px;margin:10px 0;background:#fbfcfd}\n.phone h3{margin:0 0 6px;font-size:16px}\n.phone .row{margin-top:10px}\n.login{max-width:420px;margin:40px auto}\n.choose label{display:flex;gap:10px;align-items:center;padding:10px;border:1px solid var(--line);border-radius:10px;margin:6px 0;cursor:pointer;background:#fff}\ndetails.howto{margin-top:14px}\ndetails.howto summary{cursor:pointer;font-weight:600}\ndetails.howto li{margin:6px 0}\ncode{background:#eef0f3;border-radius:4px;padding:1px 5px;font-size:14px}\n.empty{color:var(--muted);padding:12px 0}\n@media (max-width:600px){h1{font-size:21px}.card{padding:14px}table.list .hide-s{display:none}.btn{width:100%}.row .btn{flex:1 1 auto}}\n</style>\n</head>\n<body>\n<header class=\"bar\"><strong id=\"brand\">Social Posts</strong><span class=\"who\" id=\"who\"></span></header>\n<main id=\"app\"><p class=\"empty\">Loading\u2026</p></main>\n<script>\n(function () {\n\t'use strict';\n\tvar S = { settings: null, platforms: {}, posts: [], who: '' };\n\tvar app = document.getElementById('app');\n\tvar draft = null; // Compose state.\n\n\tfunction esc(s) {\n\t\treturn String(s == null ? '' : s).replace(/[&<>\"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '\"': '&quot;', \"'\": '&#39;' }[c]; });\n\t}\n\tfunction api(method, path, body) {\n\t\tvar opt = { method: method, headers: { 'X-SP': '1' }, credentials: 'same-origin' };\n\t\tif (body !== undefined) { opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }\n\t\treturn fetch(path, opt).then(function (r) {\n\t\t\treturn r.json().catch(function () { return {}; }).then(function (d) {\n\t\t\t\tif (r.status === 401) { showLogin(); throw new Error(d.error || 'Please sign in.'); }\n\t\t\t\tif (!r.ok) { throw new Error(d.error || ('Error ' + r.status)); }\n\t\t\t\treturn d;\n\t\t\t});\n\t\t});\n\t}\n\tfunction flash(kind, text) {\n\t\tsessionStorageSet('sp_flash', JSON.stringify({ kind: kind, text: text }));\n\t}\n\tfunction sessionStorageSet(k, v) { try { sessionStorage.setItem(k, v); } catch (e) { /* ignore */ } }\n\tfunction takeFlash() {\n\t\tvar v = null;\n\t\ttry { v = sessionStorage.getItem('sp_flash'); sessionStorage.removeItem('sp_flash'); } catch (e) { /* ignore */ }\n\t\tif (!v) { return ''; }\n\t\ttry { var f = JSON.parse(v); return '<div class=\"msg ' + (f.kind === 'ok' ? 'ok' : 'err') + '\">' + esc(f.text) + '</div>'; } catch (e) { return ''; }\n\t}\n\tfunction siteName() { return (S.settings && S.settings.site_name) || 'Social Posts'; }\n\tfunction initials() {\n\t\tvar w = siteName().replace(/[^A-Za-z0-9 ]/g, ' ').trim().split(/\\s+/);\n\t\treturn ((w[0] || 'S').charAt(0) + (w[1] ? w[1].charAt(0) : '')).toUpperCase();\n\t}\n\tfunction when(t) {\n\t\tif (!t) { return ''; }\n\t\tvar d = new Date(t);\n\t\treturn d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) + ', ' + d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });\n\t}\n\tfunction postOn(d) { var t = new Date(d + 'T12:00:00'); return isNaN(t) ? d : t.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' }); }\n\tfunction label(p) { return (S.platforms[p] && S.platforms[p].label) || p; }\n\tfunction statusPill(st) {\n\t\tvar t = { draft: 'Waiting for approval', todo: 'Finish on phone', processing: 'Processing', failed: 'Needs attention', sent: 'Posted' }[st] || st;\n\t\treturn '<span class=\"pill ' + esc(st) + '\">' + esc(t) + '</span>';\n\t}\n\tfunction mediaSrc(m, ig) { return '/m/' + (ig && m.ig_key ? m.ig_key : m.key); }\n\n\t/* ---------------- Sign-in ---------------- */\n\tfunction showLogin(err) {\n\t\tdocument.getElementById('who').innerHTML = '';\n\t\tapp.innerHTML = '<div class=\"login card\"><h1>Social Posts</h1><p>Sign in to write and approve posts.</p>' +\n\t\t\t(err ? '<div class=\"msg err\">' + esc(err) + '</div>' : '') +\n\t\t\t'<form id=\"lf\"><label class=\"field\" for=\"ln\">Your name</label><input type=\"text\" id=\"ln\" autocomplete=\"name\" placeholder=\"So posts show who wrote them\">' +\n\t\t\t'<label class=\"field\" for=\"lp\">Password</label><input type=\"password\" id=\"lp\" autocomplete=\"current-password\" required>' +\n\t\t\t'<label style=\"display:flex;gap:8px;align-items:center;margin:14px 0\"><input type=\"checkbox\" id=\"lr\" checked> Keep me signed in on this device</label>' +\n\t\t\t'<button class=\"btn\" type=\"submit\" style=\"width:100%\">Sign in</button></form></div>';\n\t\ttry { document.getElementById('ln').value = localStorage.getItem('sp_name') || ''; } catch (e) { /* ignore */ }\n\t\tdocument.getElementById('lf').onsubmit = function (e) {\n\t\t\te.preventDefault();\n\t\t\tvar name = document.getElementById('ln').value;\n\t\t\ttry { localStorage.setItem('sp_name', name); } catch (er) { /* ignore */ }\n\t\t\tvar b = this.querySelector('button'); b.disabled = true;\n\t\t\tfetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin', body: JSON.stringify({ name: name, password: document.getElementById('lp').value, remember: document.getElementById('lr').checked }) })\n\t\t\t\t.then(function (r) { return r.json().then(function (d) { if (!r.ok) { throw new Error(d.error || 'Sign-in failed.'); } }); })\n\t\t\t\t.then(load).catch(function (er) { showLogin(er.message); });\n\t\t};\n\t}\n\n\t/* ---------------- Load + route ---------------- */\n\tfunction load() {\n\t\treturn fetch('/api/state', { credentials: 'same-origin' }).then(function (r) {\n\t\t\tif (r.status === 401) { showLogin(); return null; }\n\t\t\treturn r.json().then(function (d) {\n\t\t\t\tif (!r.ok) { throw new Error(d.error || 'Could not load.'); }\n\t\t\t\tS = d;\n\t\t\t\tdocument.documentElement.style.setProperty('--accent', S.settings.accent || '#2563eb');\n\t\t\t\tdocument.getElementById('brand').textContent = siteName();\n\t\t\t\tdocument.title = 'Social Posts \u00b7 ' + siteName();\n\t\t\t\tdocument.getElementById('who').innerHTML = esc(S.who) + ' \u00b7 <button type=\"button\" id=\"so\">Sign out</button>';\n\t\t\t\tdocument.getElementById('so').onclick = function () { api('POST', '/api/logout', {}).then(function () { showLogin(); }); };\n\t\t\t\trender();\n\t\t\t\treturn d;\n\t\t\t});\n\t\t}).catch(function (e) { app.innerHTML = '<div class=\"msg err\">' + esc(e.message) + '</div>'; });\n\t}\n\twindow.addEventListener('hashchange', function () { if (S.settings) { render(); } });\n\n\tfunction render() {\n\t\tvar h = location.hash.replace(/^#/, '') || 'new';\n\t\tvar todo = S.posts.filter(function (p) { return p.status !== 'sent'; }).length;\n\t\tvar tabs = [['new', 'New post'], ['todo', 'To do' + (todo ? ' (' + todo + ')' : '')], ['history', 'History'], ['settings', 'Settings']];\n\t\tvar top = '<h1>Social Posts</h1>' + takeFlash();\n\t\tif (S.settings.test_mode) {\n\t\t\ttop += '<div class=\"banner test\"><strong>Test mode is on.</strong> Nothing will be posted. Approving shows exactly what would have been sent. Turn it off under <a href=\"#settings\">Settings</a> when you are ready.</div>';\n\t\t}\n\t\ttop += '<nav class=\"tabs\">' + tabs.map(function (t) { return '<a href=\"#' + t[0] + '\" class=\"' + (h === t[0] || (h.indexOf(t[0]) === 0 && t[0] !== 'new') ? 'on' : '') + '\">' + esc(t[1]) + '</a>'; }).join('') + '</nav>';\n\t\tif (h.indexOf('post/') === 0) { return viewPost(top, h.slice(5)); }\n\t\tif (h.indexOf('edit/') === 0) { return viewCompose(top, h.slice(5)); }\n\t\tif (h === 'todo') { return viewList(top, 'todo'); }\n\t\tif (h === 'history') { return viewList(top, 'history'); }\n\t\tif (h === 'settings') { return viewSettings(top); }\n\t\treturn viewCompose(top, '');\n\t}\n\n\t/* ---------------- Lists ---------------- */\n\tfunction viewList(top, which) {\n\t\tvar rows = S.posts.filter(function (p) { return which === 'todo' ? p.status !== 'sent' : true; });\n\t\tif (which === 'todo') {\n\t\t\t// Next in line first: by post date (undated last), then the photo post before the TikTok video.\n\t\t\trows = rows.slice().sort(function (a, b) {\n\t\t\t\tvar da = a.post_on || '9999-99-99', db = b.post_on || '9999-99-99';\n\t\t\t\tif (da !== db) { return da < db ? -1 : 1; }\n\t\t\t\tvar ka = a.kind === 'video' ? 1 : 0, kb = b.kind === 'video' ? 1 : 0;\n\t\t\t\treturn ka !== kb ? ka - kb : a.created - b.created;\n\t\t\t});\n\t\t}\n\t\tvar html = top + '<div class=\"card\"><h2>' + (which === 'todo' ? 'Waiting on you' : 'All posts') + '</h2>';\n\t\tif (!rows.length) {\n\t\t\thtml += '<p class=\"empty\">' + (which === 'todo' ? 'Nothing waiting. Nice.' : 'No posts yet.') + '</p>';\n\t\t} else {\n\t\t\thtml += '<table class=\"list\"><thead><tr><th>Post</th><th class=\"hide-s\">Goes to</th><th>Status</th><th class=\"hide-s\">When</th></tr></thead><tbody>';\n\t\t\tvar lastDay = null;\n\t\t\trows.forEach(function (p) {\n\t\t\t\tif (which === 'todo' && (p.post_on || '') !== lastDay) {\n\t\t\t\t\tlastDay = p.post_on || '';\n\t\t\t\t\thtml += '<tr class=\"day\"><td colspan=\"4\">' + (lastDay ? esc(postOn(lastDay)) : 'No date set') + '</td></tr>';\n\t\t\t\t}\n\t\t\t\tvar t = p.caption.length > 70 ? p.caption.slice(0, 70) + '\u2026' : p.caption;\n\t\t\t\thtml += '<tr><td><a href=\"#post/' + esc(p.id) + '\">' + esc(t) + '</a><div class=\"hint\">' + (p.kind === 'video' ? '<strong>' + esc(p.platforms.map(label).join(', ')) + ' video</strong>' : '<strong>' + esc(p.platforms.map(label).join(', ')) + '</strong> \u00b7 ' + p.media.length + ' photo' + (p.media.length > 1 ? 's' : '')) + ' \u00b7 by ' + esc(p.author) + (p.post_on ? ' \u00b7 <strong>post on ' + esc(postOn(p.post_on)) + '</strong>' : '') + (p.coach && p.coach.score !== null && p.coach.score !== undefined ? ' \u00b7 ' + scoreTag(p.coach.score) : '') + '</div></td>' +\n\t\t\t\t\t'<td class=\"hide-s\">' + p.platforms.map(label).map(esc).join(', ') + '</td><td>' + statusPill(p.status) + '</td><td class=\"hide-s\">' + esc(when(p.sent_at || p.created)) + '</td></tr>';\n\t\t\t});\n\t\t\thtml += '</tbody></table>';\n\t\t}\n\t\tapp.innerHTML = html + '</div>';\n\t}\n\n\t/* ---------------- Compose ---------------- */\n\tfunction viewCompose(top, id) {\n\t\tvar existing = id ? S.posts.filter(function (p) { return p.id === id; })[0] : null;\n\t\tif (!draft || draft.id !== (existing ? existing.id : '')) {\n\t\t\tdraft = existing ? { id: existing.id, kind: existing.kind, caption: existing.caption, title: existing.title, platforms: existing.platforms.slice(), media: existing.media.map(function (m) { return { key: m.key, ig_key: m.ig_key, type: m.type, src: '/m/' + m.key, done: true }; }) }\n\t\t\t\t: { id: '', kind: 'photo', caption: '', title: '', platforms: (S.settings.default_platforms || ['facebook', 'instagram']).slice(), media: [] };\n\t\t}\n\t\tvar d = draft;\n\t\tvar plats = Object.keys(S.platforms).filter(function (p) { return S.platforms[p][d.kind]; });\n\t\tvar html = top + '<form class=\"card\" id=\"cf\"><h2>' + (d.id ? 'Edit draft' : 'New post') + '</h2>';\n\t\tif (!d.id) {\n\t\t\thtml += '<div class=\"seg\" role=\"group\" aria-label=\"Post type\"><button type=\"button\" data-k=\"photo\" class=\"' + (d.kind === 'photo' ? 'on' : '') + '\">Photo post</button><button type=\"button\" data-k=\"video\" class=\"' + (d.kind === 'video' ? 'on' : '') + '\">Video post</button></div>';\n\t\t}\n\t\thtml += '<label class=\"field\">' + (d.kind === 'video' ? 'Video' : 'Photos (up to 10)') + '</label>' +\n\t\t\t'<div class=\"drop\" id=\"drop\" tabindex=\"0\" role=\"button\">' + (d.kind === 'video' ? 'Tap to choose a video, or drop it here. MP4 or MOV, 25 MB or less. Vertical and under 90 seconds works everywhere.' : 'Tap to choose photos, or drop them here.') + '</div>' +\n\t\t\t'<input type=\"file\" id=\"file\" hidden ' + (d.kind === 'video' ? 'accept=\"video/mp4,video/quicktime\"' : 'accept=\"image/*\" multiple') + '>' +\n\t\t\t'<div class=\"thumbs\" id=\"thumbs\"></div>' +\n\t\t\t'<label class=\"field\" for=\"cap\">Post text</label><textarea id=\"cap\" maxlength=\"2200\" placeholder=\"Write it once. It goes to every place you tick.\">' + esc(d.caption) + '</textarea><div class=\"counts\" id=\"counts\"></div>' +\n\t\t\t'<div id=\"ytbox\"' + (d.kind === 'video' && d.platforms.indexOf('youtube') > -1 ? '' : ' hidden') + '><label class=\"field\" for=\"ttl\">YouTube title</label><input type=\"text\" id=\"ttl\" maxlength=\"100\" value=\"' + esc(d.title) + '\"><p class=\"hint\">100 characters or fewer.</p></div>' +\n\t\t\t'<label class=\"field\">Post to</label><div class=\"plats\">' + plats.map(function (p) {\n\t\t\t\treturn '<label><input type=\"checkbox\" name=\"pl\" value=\"' + p + '\"' + (d.platforms.indexOf(p) > -1 ? ' checked' : '') + '> ' + esc(label(p)) + '</label>';\n\t\t\t}).join('') + '</div><p class=\"hint\">' + esc(viaHint()) + '</p>' +\n\t\t\t'<div class=\"row\" style=\"margin-top:18px\"><button class=\"btn\" type=\"submit\" id=\"save\">Save and preview</button>' + (d.id ? '<a class=\"btn ghost\" href=\"#post/' + esc(d.id) + '\">Cancel</a>' : '') + '</div></form>';\n\t\tapp.innerHTML = html;\n\t\tvar form = document.getElementById('cf');\n\t\tArray.prototype.forEach.call(form.querySelectorAll('.seg button'), function (b) {\n\t\t\tb.onclick = function () {\n\t\t\t\tif (d.kind === b.dataset.k) { return; }\n\t\t\t\tif (d.media.length && !confirm('Switching clears the files you added. Continue?')) { return; }\n\t\t\t\td.kind = b.dataset.k; d.media = []; render();\n\t\t\t};\n\t\t});\n\t\tvar file = document.getElementById('file'), drop = document.getElementById('drop');\n\t\tdrop.onclick = function () { file.click(); };\n\t\tdrop.onkeydown = function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); file.click(); } };\n\t\tdrop.ondragover = function (e) { e.preventDefault(); drop.classList.add('hot'); };\n\t\tdrop.ondragleave = function () { drop.classList.remove('hot'); };\n\t\tdrop.ondrop = function (e) { e.preventDefault(); drop.classList.remove('hot'); addFiles(e.dataTransfer.files); };\n\t\tfile.onchange = function () { addFiles(file.files); file.value = ''; };\n\t\tvar cap = document.getElementById('cap');\n\t\tcap.oninput = function () { d.caption = cap.value; counts(); };\n\t\tvar ttl = document.getElementById('ttl');\n\t\tif (ttl) { ttl.oninput = function () { d.title = ttl.value; }; }\n\t\tArray.prototype.forEach.call(form.querySelectorAll('input[name=pl]'), function (c) {\n\t\t\tc.onchange = function () {\n\t\t\t\td.platforms = Array.prototype.map.call(form.querySelectorAll('input[name=pl]:checked'), function (x) { return x.value; });\n\t\t\t\tdocument.getElementById('ytbox').hidden = !(d.kind === 'video' && d.platforms.indexOf('youtube') > -1);\n\t\t\t\tcounts();\n\t\t\t};\n\t\t});\n\t\tform.onsubmit = function (e) { e.preventDefault(); saveDraft(); };\n\t\tdrawThumbs(); counts();\n\t}\n\tfunction viaHint() {\n\t\tvar s = S.settings, auto = [], phone = [];\n\t\t[['facebook', s.facebook_via], ['instagram', s.instagram_via]].forEach(function (x) { (x[1] === 'share' ? phone : auto).push(label(x[0])); });\n\t\t['x', 'tiktok'].forEach(function (p) { phone.push(label(p)); });\n\t\treturn (auto.length ? auto.join(' and ') + ' post automatically. ' : '') + phone.join(', ') + ' finish from your phone with one tap.';\n\t}\n\tfunction counts() {\n\t\tvar n = Array.from(draft.caption || '').length, out = [];\n\t\tvar lim = { x: 280, pinterest: 500, instagram: 2200, tiktok: 2200, facebook: 2200 };\n\t\tdraft.platforms.forEach(function (p) { if (lim[p]) { out.push('<span class=\"' + (n > lim[p] ? 'over' : '') + '\">' + esc(label(p)) + ': ' + n + ' / ' + lim[p] + '</span>'); } });\n\t\tvar el = document.getElementById('counts'); if (el) { el.innerHTML = out.join(''); }\n\t}\n\tfunction drawThumbs() {\n\t\tvar box = document.getElementById('thumbs'); if (!box) { return; }\n\t\tbox.innerHTML = draft.media.map(function (m, i) {\n\t\t\treturn '<div class=\"thumb\">' + (m.type.indexOf('video') === 0 ? '<video src=\"' + esc(m.src) + '\" muted playsinline preload=\"metadata\"></video>' : '<img src=\"' + esc(m.src) + '\" alt=\"\">') +\n\t\t\t\t'<button type=\"button\" class=\"x\" data-i=\"' + i + '\" aria-label=\"Remove\">\u00d7</button>' + (i > 0 ? '<button type=\"button\" class=\"mv\" data-i=\"' + i + '\" aria-label=\"Move earlier\">\u2039</button>' : '') +\n\t\t\t\t(m.done ? '' : '<div class=\"bar2\"><i style=\"width:' + Math.round((m.pct || 0) * 100) + '%\"></i></div>') + '</div>';\n\t\t}).join('');\n\t\tArray.prototype.forEach.call(box.querySelectorAll('.x'), function (b) { b.onclick = function () { draft.media.splice(+b.dataset.i, 1); drawThumbs(); }; });\n\t\tArray.prototype.forEach.call(box.querySelectorAll('.mv'), function (b) { b.onclick = function () { var i = +b.dataset.i; var t = draft.media[i]; draft.media[i] = draft.media[i - 1]; draft.media[i - 1] = t; drawThumbs(); }; });\n\t}\n\tfunction upload(blob, name, w, h, onPct) {\n\t\treturn new Promise(function (resolve, reject) {\n\t\t\tvar x = new XMLHttpRequest();\n\t\t\tx.open('POST', '/api/media');\n\t\t\tx.setRequestHeader('X-SP', '1');\n\t\t\tx.setRequestHeader('Content-Type', blob.type);\n\t\t\tx.setRequestHeader('X-Filename', (name || 'media').replace(/[^\\w.\\- ]/g, ''));\n\t\t\tif (w) { x.setRequestHeader('X-Width', String(w)); x.setRequestHeader('X-Height', String(h)); }\n\t\t\tx.upload.onprogress = function (e) { if (e.lengthComputable && onPct) { onPct(e.loaded / e.total); } };\n\t\t\tx.onload = function () { var d = {}; try { d = JSON.parse(x.responseText); } catch (e) { /* ignore */ } if (x.status === 200) { resolve(d); } else { reject(new Error(d.error || 'Upload failed (' + x.status + ').')); } };\n\t\t\tx.onerror = function () { reject(new Error('Upload failed. Check the connection and try again.')); };\n\t\t\tx.send(blob);\n\t\t});\n\t}\n\tfunction toJpeg(file, crop) {\n\t\t// Re-saves a photo as JPEG (max 2160px), optionally center-cropped to fit Instagram (4:5 to 1.91:1).\n\t\treturn new Promise(function (resolve, reject) {\n\t\t\tvar url = URL.createObjectURL(file), img = new Image();\n\t\t\timg.onload = function () {\n\t\t\t\tvar sw = img.naturalWidth, sh = img.naturalHeight, sx = 0, sy = 0, r = sw / sh;\n\t\t\t\tif (crop) {\n\t\t\t\t\tif (r < 0.8) { var nh = Math.floor(sw / 0.8); sy = Math.round((sh - nh) / 2); sh = nh; }\n\t\t\t\t\telse if (r > 1.91) { var nw = Math.floor(sh * 1.91); sx = Math.round((sw - nw) / 2); sw = nw; }\n\t\t\t\t}\n\t\t\t\tvar scale = Math.min(1, 2160 / Math.max(sw, sh)), cw = Math.round(sw * scale), ch = Math.round(sh * scale);\n\t\t\t\tvar c = document.createElement('canvas'); c.width = cw; c.height = ch;\n\t\t\t\tvar g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, cw, ch);\n\t\t\t\tg.drawImage(img, sx, sy, sw, sh, 0, 0, cw, ch);\n\t\t\t\tURL.revokeObjectURL(url);\n\t\t\t\tc.toBlob(function (b) { if (b) { resolve({ blob: b, w: cw, h: ch, ratio: img.naturalWidth / img.naturalHeight }); } else { reject(new Error('Could not read that photo.')); } }, 'image/jpeg', 0.88);\n\t\t\t};\n\t\t\timg.onerror = function () { URL.revokeObjectURL(url); reject(new Error('Could not read that photo. Try a JPEG or PNG.')); };\n\t\t\timg.src = url;\n\t\t});\n\t}\n\tfunction addFiles(list) {\n\t\tvar files = Array.prototype.slice.call(list || []);\n\t\tif (draft.kind === 'video') { files = files.slice(0, 1); draft.media = []; }\n\t\tfiles = files.slice(0, Math.max(0, 10 - draft.media.length));\n\t\tfiles.forEach(function (f) {\n\t\t\tvar m = { type: f.type || 'application/octet-stream', src: URL.createObjectURL(f), done: false, pct: 0 };\n\t\t\tdraft.media.push(m); drawThumbs();\n\t\t\tvar job;\n\t\t\tif (draft.kind === 'video') {\n\t\t\t\tif (!/^video\\/(mp4|quicktime)$/.test(f.type)) { job = Promise.reject(new Error('Use an MP4 or MOV video.')); }\n\t\t\t\telse if (f.size > 25 * 1024 * 1024) { job = Promise.reject(new Error('That video is over 25 MB. Export it smaller (1080p, under 90 seconds) and try again.')); }\n\t\t\t\telse { job = upload(f, f.name, 0, 0, function (p) { m.pct = p; drawThumbs(); }).then(function (r) { m.key = r.key; }); }\n\t\t\t} else {\n\t\t\t\tjob = toJpeg(f, false).then(function (j) {\n\t\t\t\t\treturn upload(j.blob, f.name.replace(/\\.\\w+$/, '') + '.jpg', j.w, j.h, function (p) { m.pct = p; drawThumbs(); }).then(function (r) {\n\t\t\t\t\t\tm.key = r.key; m.type = 'image/jpeg';\n\t\t\t\t\t\tif (j.ratio < 0.8 || j.ratio > 1.91) {\n\t\t\t\t\t\t\treturn toJpeg(f, true).then(function (c) { return upload(c.blob, 'ig-' + f.name.replace(/\\.\\w+$/, '') + '.jpg', c.w, c.h); }).then(function (r2) { m.ig_key = r2.key; });\n\t\t\t\t\t\t}\n\t\t\t\t\t});\n\t\t\t\t});\n\t\t\t}\n\t\t\tjob.then(function () { m.done = true; drawThumbs(); }).catch(function (e) {\n\t\t\t\tvar i = draft.media.indexOf(m); if (i > -1) { draft.media.splice(i, 1); }\n\t\t\t\tdrawThumbs(); alert(e.message);\n\t\t\t});\n\t\t});\n\t}\n\tfunction saveDraft() {\n\t\tvar d = draft, b = document.getElementById('save');\n\t\tif (d.media.some(function (m) { return !m.done; })) { alert('Wait for the files to finish uploading.'); return; }\n\t\tb.disabled = true; b.textContent = 'Saving\u2026';\n\t\tvar body = { kind: d.kind, caption: d.caption, title: d.title, platforms: d.platforms, media: d.media.map(function (m) { return m.key; }), ig_media: d.media.map(function (m) { return m.ig_key || ''; }) };\n\t\t(d.id ? api('PUT', '/api/posts/' + d.id, body) : api('POST', '/api/posts', body)).then(function (r) {\n\t\t\tvar id = r.id; draft = null;\n\t\t\tflash('ok', 'Saved. Check the preview, then approve it.');\n\t\t\treturn load().then(function () { location.hash = 'post/' + id; });\n\t\t}).catch(function (e) { b.disabled = false; b.textContent = 'Save and preview'; alert(e.message); });\n\t}\n\n\t/* ---------------- One post ---------------- */\n\tfunction viewPost(top, id) {\n\t\tvar p = S.posts.filter(function (x) { return x.id === id; })[0];\n\t\tif (!p) {\n\t\t\tapp.innerHTML = top + '<div class=\"card\"><p class=\"empty\">Loading\u2026</p></div>';\n\t\t\tapi('GET', '/api/posts/' + id).then(function (post) { S.posts.unshift(post); render(); }).catch(function (e) { app.innerHTML = top + '<div class=\"msg err\">' + esc(e.message) + '</div>'; });\n\t\t\treturn;\n\t\t}\n\t\tvar html = top + '<div class=\"row\" style=\"margin-bottom:12px\">' + statusPill(p.status) + '<span class=\"hint\" style=\"margin:0\">Written by ' + esc(p.author) + ', ' + esc(when(p.created)) + (p.approved_by ? ' \u00b7 approved by ' + esc(p.approved_by) : '') + (p.post_on ? ' \u00b7 <strong>planned for ' + esc(postOn(p.post_on)) + '</strong>' : '') + '</span></div>';\n\t\tif (p.status === 'draft') {\n\t\t\thtml += '<div class=\"card\" style=\"border-color:var(--accent)\"><div class=\"row\"><button class=\"btn\" id=\"ap\">' + (S.settings.test_mode ? 'Approve (test run)' : 'Approve and post') + '</button><a class=\"btn ghost\" href=\"#edit/' + esc(p.id) + '\">Edit</a><button class=\"btn danger\" id=\"del\">Delete draft</button></div></div>';\n\t\t} else {\n\t\t\thtml += resultsHtml(p);\n\t\t}\n\t\tif (p.coach) { html += coachHtml(p); }\n\t\thtml += '<h2>Preview</h2><div class=\"pv-grid\">' + p.platforms.map(function (pl) { return previewCard(p, pl); }).join('') + '</div>';\n\t\tif (p.status !== 'draft') { html += '<div class=\"row\" style=\"margin-top:16px\"><button class=\"btn danger\" id=\"del\">Remove from this list</button></div>'; }\n\t\tapp.innerHTML = html;\n\t\tvar ap = document.getElementById('ap');\n\t\tif (ap) {\n\t\t\tap.onclick = function () {\n\t\t\t\tif (!S.settings.test_mode && !confirm('Post this now to ' + p.platforms.map(label).join(', ') + '?')) { return; }\n\t\t\t\tap.disabled = true; ap.textContent = 'Posting\u2026 this can take up to a minute for videos';\n\t\t\t\tapi('POST', '/api/posts/' + p.id + '/approve', {}).then(function (np) { replacePost(np); flash(np.status === 'failed' ? 'err' : 'ok', np.status === 'failed' ? 'Some places failed. See below.' : (np.status === 'todo' ? 'Approved. Finish the phone steps below.' : 'Approved.')); render(); })\n\t\t\t\t\t.catch(function (e) { ap.disabled = false; ap.textContent = 'Approve'; alert(e.message); });\n\t\t\t};\n\t\t}\n\t\tvar rt = document.getElementById('retry');\n\t\tif (rt) { rt.onclick = function () { rt.disabled = true; api('POST', '/api/posts/' + p.id + '/approve', {}).then(function (np) { replacePost(np); render(); }).catch(function (e) { rt.disabled = false; alert(e.message); }); }; }\n\t\tvar ck = document.getElementById('check');\n\t\tif (ck) { ck.onclick = function () { ck.disabled = true; ck.textContent = 'Checking\u2026'; api('POST', '/api/posts/' + p.id + '/check', {}).then(function (np) { replacePost(np); render(); }).catch(function (e) { ck.disabled = false; alert(e.message); }); }; }\n\t\tvar del = document.getElementById('del');\n\t\tif (del) { del.onclick = function () { if (!confirm(p.status === 'draft' ? 'Delete this draft?' : 'Remove this post and its files from this list? It stays on the social sites.')) { return; } api('DELETE', '/api/posts/' + p.id).then(function () { S.posts = S.posts.filter(function (x) { return x.id !== p.id; }); flash('ok', 'Deleted.'); location.hash = 'todo'; }).catch(function (e) { alert(e.message); }); }; }\n\t\tArray.prototype.forEach.call(app.querySelectorAll('.phone'), wirePhone);\n\t\tArray.prototype.forEach.call(app.querySelectorAll('.use-alt'), function (b) {\n\t\t\tb.onclick = function () {\n\t\t\t\tvar i = Number(b.dataset.i), c = p.coach, alt = c.alternates[i];\n\t\t\t\tvar alts = c.alternates.slice(); alts[i] = { caption: p.caption, hook: c.edited ? 'Your edit' : c.hook, score: c.edited ? null : c.score, why: c.edited ? '' : c.why, scorecard: c.edited ? [] : c.scorecard, fixes: c.edited ? [] : c.fixes };\n\t\t\t\tvar coach = { hook: alt.hook, score: alt.score, why: alt.why || '', scorecard: alt.scorecard || [], fixes: alt.fixes || [], alternates: alts };\n\t\t\t\tvar body = { kind: p.kind, caption: alt.caption, title: p.title, platforms: p.platforms, media: p.media.map(function (m) { return m.key; }), ig_media: p.media.map(function (m) { return m.ig_key || ''; }), coach: coach };\n\t\t\t\tb.disabled = true;\n\t\t\t\tapi('PUT', '/api/posts/' + p.id, body).then(function (np) { replacePost(np); flash('ok', 'Switched to that version. The old one is kept under Other versions.'); render(); }).catch(function (e) { b.disabled = false; alert(e.message); });\n\t\t\t};\n\t\t});\n\t}\n\t// Rating colors: green 8+ (likely to do well), yellow 6.5-7.9 (could go either way), red under 6.5 (unlikely).\n\tfunction scoreClass(n) { return n >= 8 ? 'hi' : n >= 6.5 ? 'mid' : 'lo'; }\n\tfunction scoreTag(n) { return '<span class=\"sc-' + scoreClass(n) + '\" title=\"' + (n >= 8 ? 'Likely to do well' : n >= 6.5 ? 'Could go either way' : 'Unlikely to do well') + '\">' + esc(String(n)) + '/10</span>'; }\n\tfunction coachHtml(p) {\n\t\tvar c = p.coach, h = '<div class=\"card coach\"><div class=\"row\" style=\"justify-content:space-between\"><h2 style=\"margin:0\">Coach notes</h2>' +\n\t\t\t(c.score !== null && c.score !== undefined ? '<span class=\"score sc-' + scoreClass(c.score) + '\">' + esc(String(c.score)) + '<small>/10</small></span>' : '') + '</div>' +\n\t\t\t'<p class=\"hint\" style=\"margin-top:2px\"><span class=\"sc-hi\">Green 8+</span> likely to do well \u00b7 <span class=\"sc-mid\">Yellow 6.5 to 7.9</span> could go either way \u00b7 <span class=\"sc-lo\">Red under 6.5</span> unlikely</p>';\n\t\tif (c.hook) { h += '<p class=\"hint\" style=\"margin-top:4px\">Hook: <strong>' + esc(c.hook) + '</strong></p>'; }\n\t\tif (c.edited) { h += '<p class=\"hint\">You edited the text after it was scored, so the score is for the earlier wording.</p>'; }\n\t\tif (c.why) { h += '<p style=\"margin:10px 0 0\">' + esc(c.why) + '</p>'; }\n\t\tif (c.scorecard && c.scorecard.length) { h += '<ul class=\"sc\">' + c.scorecard.map(function (r) { return '<li>' + esc(r.name) + ': <b>' + esc(String(r.score)) + '</b></li>'; }).join('') + '</ul>'; }\n\t\tif (c.fixes && c.fixes.length) { h += '<details><summary>What would make it stronger</summary><ul>' + c.fixes.map(function (f) { return '<li>' + esc(f) + '</li>'; }).join('') + '</ul></details>'; }\n\t\tif (c.alternates && c.alternates.length) {\n\t\t\th += '<details' + (p.status === 'draft' ? ' open' : '') + '><summary>Other versions (' + c.alternates.length + ')</summary>' + c.alternates.map(function (a, i) {\n\t\t\t\treturn '<div class=\"alt\"><p>' + esc(a.caption) + '</p><div class=\"row\"><span class=\"hint\" style=\"margin:0\">' + esc(a.hook || '') + (a.score !== null && a.score !== undefined ? ' \u00b7 ' + scoreTag(a.score) : '') + ' \u00b7 ' + Array.from(a.caption).length + ' characters</span>' +\n\t\t\t\t\t(p.status === 'draft' ? '<button type=\"button\" class=\"btn ghost use-alt\" style=\"min-height:34px;padding:4px 12px\" data-i=\"' + i + '\">Use this version</button>' : '') + '</div></div>';\n\t\t\t}).join('') + '</details>';\n\t\t}\n\t\treturn h + '</div>';\n\t}\n\tfunction replacePost(np) { S.posts = S.posts.map(function (x) { return x.id === np.id ? np : x; }); }\n\tfunction resultsHtml(p) {\n\t\tvar r = p.results || {}, html = '<div class=\"card\"><h2>What happened</h2><ul class=\"results\">', failed = false, processing = false, phones = '';\n\t\tp.platforms.forEach(function (pl) {\n\t\t\tvar x = r[pl] || {}, line = '';\n\t\t\tif (x.state === 'sent') { line = '<span class=\"ok\">Posted.</span>' + (x.url ? ' <a href=\"' + esc(x.url) + '\" target=\"_blank\" rel=\"noopener\">View it</a>' : ''); }\n\t\t\telse if (x.state === 'test') { line = '<span class=\"ok\">' + esc(x.message) + '</span>'; }\n\t\t\telse if (x.state === 'failed') { failed = true; line = '<span class=\"bad\">Failed: ' + esc(x.message) + '</span>'; }\n\t\t\telse if (x.state === 'processing') { processing = true; line = esc(x.message); }\n\t\t\telse if (x.state === 'done') { line = '<span class=\"ok\">Done from phone.</span> <button type=\"button\" class=\"btn ghost undo\" style=\"min-height:32px;padding:2px 10px\" data-p=\"' + pl + '\">Undo</button>'; }\n\t\t\telse if (x.state === 'phone') { line = 'Finish on your phone (below).'; phones += phoneBox(p, pl); }\n\t\t\telse { line = 'Not sent yet.'; }\n\t\t\thtml += '<li><strong>' + esc(label(pl)) + ':</strong> ' + line + '</li>';\n\t\t});\n\t\thtml += '</ul>';\n\t\tif (failed) { html += '<div class=\"row\" style=\"margin-top:10px\"><button class=\"btn\" id=\"retry\">Try the failed ones again</button></div>'; }\n\t\tif (processing) { html += '<div class=\"row\" style=\"margin-top:10px\"><button class=\"btn\" id=\"check\">Check Instagram now</button></div>'; }\n\t\thtml += phones + '</div>';\n\t\tsetTimeout(function () {\n\t\t\tArray.prototype.forEach.call(app.querySelectorAll('.undo'), function (b) { b.onclick = function () { api('POST', '/api/posts/' + p.id + '/done', { platform: b.dataset.p, undo: true }).then(function (np) { replacePost(np); render(); }); }; });\n\t\t}, 0);\n\t\treturn html;\n\t}\n\tfunction shareText(p, pl) {\n\t\tvar t = p.caption;\n\t\tif (pl === 'youtube' && p.title) { t = p.title + '\\n\\n' + t; }\n\t\tif (pl === 'pinterest' && S.settings.site_link) { t += '\\n\\n' + S.settings.site_link; }\n\t\treturn t;\n\t}\n\tfunction phoneBox(p, pl) {\n\t\tvar app2 = { x: 'X', youtube: 'YouTube', tiktok: 'TikTok', pinterest: 'Pinterest', facebook: 'Facebook (or Meta Business Suite)', instagram: 'Instagram' }[pl] || label(pl);\n\t\treturn '<div class=\"phone\" data-p=\"' + pl + '\" data-id=\"' + esc(p.id) + '\"><h3>Finish on ' + esc(label(pl)) + '</h3>' +\n\t\t\t'<p class=\"hint\">Open this page on your phone. Tap Share, pick ' + esc(app2) + ', paste the text if it is not already there, and tap Post. Then come back and tap Done.' + (pl === 'x' ? ' X allows 280 characters.' : '') + '</p>' +\n\t\t\t'<textarea readonly style=\"min-height:90px\">' + esc(shareText(p, pl)) + '</textarea>' +\n\t\t\t'<div class=\"row\"><button type=\"button\" class=\"btn sh\">Share to ' + esc(label(pl).replace(/ \\(.*\\)$/, '')) + '</button><button type=\"button\" class=\"btn ghost cp\">Copy text</button><button type=\"button\" class=\"btn ghost dn\">Done</button></div>' +\n\t\t\t'<p class=\"hint fb\" hidden>This browser can\\'t share files. Save the ' + (p.kind === 'video' ? 'video' : 'photos') + ': ' + p.media.map(function (m, i) { return '<a href=\"' + esc(mediaSrc(m, pl === 'instagram')) + '\" download>file ' + (i + 1) + '</a>'; }).join(', ') + ', copy the text, then post them in the app.</p></div>';\n\t}\n\tfunction copy(text) {\n\t\tif (navigator.clipboard && window.isSecureContext) { return navigator.clipboard.writeText(text); }\n\t\tvar t = document.createElement('textarea'); t.value = text; t.style.position = 'fixed'; t.style.opacity = '0'; document.body.appendChild(t); t.select();\n\t\ttry { document.execCommand('copy'); } catch (e) { /* ignore */ }\n\t\tt.remove(); return Promise.resolve();\n\t}\n\tfunction wirePhone(box) {\n\t\tvar pl = box.dataset.p, p = S.posts.filter(function (x) { return x.id === box.dataset.id; })[0], text = shareText(p, pl);\n\t\tvar sh = box.querySelector('.sh'), fb = box.querySelector('.fb');\n\t\tif (!(navigator.canShare && window.File)) { fb.hidden = false; }\n\t\tbox.querySelector('.cp').onclick = function () { var b = this; copy(text).then(function () { b.textContent = 'Text copied'; }); };\n\t\tbox.querySelector('.dn').onclick = function () { api('POST', '/api/posts/' + p.id + '/done', { platform: pl }).then(function (np) { replacePost(np); render(); }).catch(function (e) { alert(e.message); }); };\n\t\tsh.onclick = function () {\n\t\t\tvar lbl = sh.textContent; sh.disabled = true; sh.textContent = 'Getting it ready\u2026';\n\t\t\tcopy(text).catch(function () {}).then(function () {\n\t\t\t\treturn Promise.all(p.media.map(function (m, i) {\n\t\t\t\t\treturn fetch(mediaSrc(m, pl === 'instagram')).then(function (r) { if (!r.ok) { throw new Error('download'); } return r.blob(); }).then(function (b) {\n\t\t\t\t\t\treturn new File([b], 'post-' + (i + 1) + '.' + (b.type.indexOf('video') === 0 ? 'mp4' : 'jpg'), { type: b.type });\n\t\t\t\t\t});\n\t\t\t\t}));\n\t\t\t}).then(function (files) {\n\t\t\t\tvar data = { files: files, text: text };\n\t\t\t\tif (!navigator.canShare || !navigator.canShare({ files: files })) { throw new Error('noshare'); }\n\t\t\t\tif (!navigator.canShare(data)) { delete data.text; }\n\t\t\t\treturn navigator.share(data);\n\t\t\t}).then(function () { sh.disabled = false; sh.textContent = 'Sent. Paste the text if needed, post, then tap Done.'; })\n\t\t\t\t.catch(function (err) { sh.disabled = false; sh.textContent = lbl; if (err && err.name === 'AbortError') { return; } fb.hidden = false; });\n\t\t};\n\t}\n\tfunction previewCard(p, pl) {\n\t\tvar s = S.settings, name = siteName(), sub = label(pl), note = '', bad = false;\n\t\tif (pl === 'facebook' && s.meta_page) { name = s.meta_page; }\n\t\tif (pl === 'instagram' && s.meta_ig_user) { name = s.meta_ig_user; sub = '@' + s.meta_ig_user + ' \u00b7 Instagram'; }\n\t\tvar auto = (pl === 'facebook' && s.facebook_via !== 'share') || (pl === 'instagram' && s.instagram_via !== 'share');\n\t\tif (auto && !s.connected) { note = 'Not connected yet. Connect it under Settings.'; bad = true; }\n\t\telse if (auto && pl === 'instagram' && !s.meta_ig_id) { note = 'No Instagram account is linked to the Facebook Page.'; bad = true; }\n\t\telse if (!auto) { note = 'You finish this one from your phone after approving.'; }\n\t\tif (pl === 'x' && Array.from(p.caption).length > 280) { note = 'Over 280 characters. X will cut it off; shorten it when you share.'; bad = true; }\n\t\tif (pl === 'instagram' && p.media.some(function (m) { return m.ig_key; })) { note = (note ? note + ' ' : '') + 'Instagram gets a cropped copy of tall or wide photos.'; }\n\t\tvar media = '';\n\t\tif (p.kind === 'video') { media = '<div class=\"pv-media\"><video src=\"' + esc(mediaSrc(p.media[0])) + '\" controls playsinline preload=\"metadata\"></video></div>'; }\n\t\telse { media = '<div class=\"pv-media\"><img src=\"' + esc(mediaSrc(p.media[0], pl === 'instagram')) + '\" alt=\"\">' + (p.media.length > 1 ? '<span class=\"more\">1 / ' + p.media.length + '</span>' : '') + '</div>'; }\n\t\tvar textTop = pl === 'facebook' || pl === 'x';\n\t\tvar cap = esc(pl === 'x' && Array.from(p.caption).length > 280 ? Array.from(p.caption).slice(0, 279).join('') + '\u2026' : p.caption);\n\t\tvar title = pl === 'youtube' && p.title ? '<div class=\"pv-text\"><strong>' + esc(p.title) + '</strong></div>' : '';\n\t\treturn '<figure class=\"pv ' + pl + '\"><figcaption class=\"pv-head\"><span class=\"av\">' + esc(initials()) + '</span><span><strong>' + esc(name) + '</strong><br><span class=\"pv-sub\">' + esc(sub) + '</span></span></figcaption>' +\n\t\t\t(textTop ? '<div class=\"pv-text\">' + cap + '</div>' : '') + media + title + (!textTop ? '<div class=\"pv-text\" style=\"padding-top:10px\">' + cap + '</div>' : '') +\n\t\t\t(note ? '<div class=\"pv-note' + (bad ? ' bad' : '') + '\">' + esc(note) + '</div>' : '') + '</figure>';\n\t}\n\n\t/* ---------------- Settings ---------------- */\n\tfunction viewSettings(top) {\n\t\tvar s = S.settings, origin = location.origin;\n\t\tvar html = top + '<form class=\"card\" id=\"sf\"><h2>General</h2>' +\n\t\t\t'<label style=\"display:flex;gap:8px;align-items:center\"><input type=\"checkbox\" id=\"tm\"' + (s.test_mode ? ' checked' : '') + '> Test mode: approving shows what would be sent, and nothing is posted</label>' +\n\t\t\t'<label class=\"field\" for=\"sn\">Name shown on this page</label><input type=\"text\" id=\"sn\" value=\"' + esc(s.site_name) + '\">' +\n\t\t\t'<label class=\"field\" for=\"sl\">Your website address</label><input type=\"text\" inputmode=\"url\" id=\"sl\" placeholder=\"https://example.com\" value=\"' + esc(s.site_link) + '\"><p class=\"hint\">Added to the end of Pinterest pins so people can click through.</p>' +\n\t\t\t'<label class=\"field\" for=\"ac\">Accent color</label><input type=\"color\" id=\"ac\" value=\"' + esc(s.accent) + '\" style=\"width:64px;height:44px;padding:2px;border:1px solid #c9ced6;border-radius:8px\">' +\n\t\t\t'<label class=\"field\">Ticked on new posts</label><div class=\"plats\">' + Object.keys(S.platforms).map(function (p) { return '<label><input type=\"checkbox\" name=\"dp\" value=\"' + p + '\"' + (s.default_platforms.indexOf(p) > -1 ? ' checked' : '') + '> ' + esc(label(p)) + '</label>'; }).join('') + '</div>' +\n\t\t\t'<h2 style=\"margin-top:22px\">Facebook and Instagram</h2>' +\n\t\t\t'<label class=\"field\">Facebook posts</label><label style=\"display:block\"><input type=\"radio\" name=\"fv\" value=\"meta\"' + (s.facebook_via !== 'share' ? ' checked' : '') + '> Post automatically (the Meta app must be in Live mode, or only you will see the posts)</label><label style=\"display:block\"><input type=\"radio\" name=\"fv\" value=\"share\"' + (s.facebook_via === 'share' ? ' checked' : '') + '> Always send from my phone</label>' +\n\t\t\t'<label class=\"field\">Instagram posts</label><label style=\"display:block\"><input type=\"radio\" name=\"iv\" value=\"meta\"' + (s.instagram_via !== 'share' ? ' checked' : '') + '> Post automatically</label><label style=\"display:block\"><input type=\"radio\" name=\"iv\" value=\"share\"' + (s.instagram_via === 'share' ? ' checked' : '') + '> Always send from my phone</label>' +\n\t\t\t'<div class=\"row\" style=\"margin-top:18px\"><button class=\"btn\" type=\"submit\">Save settings</button></div></form>';\n\t\thtml += '<div class=\"card\"><h2>Connect Facebook and Instagram</h2>';\n\t\tif (s.connected) {\n\t\t\thtml += '<ul class=\"results\"><li class=\"ok\"><strong>Facebook Page:</strong> ' + esc(s.meta_page) + '</li><li class=\"' + (s.meta_ig_id ? 'ok' : 'bad') + '\"><strong>Instagram:</strong> ' + (s.meta_ig_id ? '@' + esc(s.meta_ig_user) : 'not linked to this Page') + '</li></ul><p class=\"hint\">Connected ' + esc(when(s.meta_at)) + '. This connection does not expire unless the Page admin removes it or changes their Facebook password.</p>';\n\t\t} else {\n\t\t\thtml += '<p>Not connected yet. Follow the steps once. It takes about 10 minutes.</p>';\n\t\t}\n\t\thtml += '<form id=\"mf\"><label class=\"field\" for=\"ut\">Access token from Graph API Explorer</label><textarea id=\"ut\" style=\"min-height:80px\" autocomplete=\"off\" placeholder=\"Paste it here. It is swapped for a Page connection that does not expire; the pasted token is not kept.\"></textarea>' +\n\t\t\t'<details class=\"howto\"><summary>Optional: App ID and App Secret (swaps a short token for a long one)</summary><label class=\"field\" for=\"ai\">Meta App ID</label><input type=\"text\" id=\"ai\"><label class=\"field\" for=\"as\">Meta App Secret</label><input type=\"password\" id=\"as\" autocomplete=\"off\"><p class=\"hint\">Used once and not saved.</p></details>' +\n\t\t\t'<div id=\"choose\"></div><div class=\"row\" style=\"margin-top:14px\"><button class=\"btn\" type=\"submit\" id=\"cn\">' + (s.connected ? 'Connect again' : 'Connect') + '</button>' + (s.connected ? '<button class=\"btn danger\" type=\"button\" id=\"dc\">Disconnect</button>' : '') + '</div></form>' +\n\t\t\t'<details class=\"howto\"' + (s.connected ? '' : ' open') + '><summary>How to connect</summary><ol>' +\n\t\t\t'<li>Make sure your Instagram is a <strong>Business</strong> or <strong>Creator</strong> account linked to your Facebook Page (Page settings \u2192 Linked accounts).</li>' +\n\t\t\t'<li>At <a href=\"https://developers.facebook.com/apps/\" target=\"_blank\" rel=\"noopener\">developers.facebook.com/apps</a>, sign in as a Page admin and create a <strong>Business</strong> app (or reuse one you have). In <strong>App settings \u2192 Basic</strong> add your domain, a privacy policy URL and a category, then switch the app to <strong>Live</strong>.</li>' +\n\t\t\t'<li>Open the <a href=\"https://developers.facebook.com/tools/explorer/\" target=\"_blank\" rel=\"noopener\">Graph API Explorer</a>, pick the app, and add these permissions: <code>pages_show_list</code>, <code>pages_read_engagement</code>, <code>pages_manage_posts</code>, <code>business_management</code>, <code>instagram_basic</code>, <code>instagram_content_publish</code>.</li>' +\n\t\t\t'<li>Click <strong>Generate Access Token</strong>. When Facebook asks which Pages to allow, pick only the Page this site posts to, and its Instagram.</li>' +\n\t\t\t'<li>No App Secret? Open the token in the <a href=\"https://developers.facebook.com/tools/debug/accesstoken/\" target=\"_blank\" rel=\"noopener\">Access Token Debugger</a> and click <strong>Extend Access Token</strong>; use the longer token.</li>' +\n\t\t\t'<li>Paste it above and click Connect. Then make a test post with test mode on before turning test mode off.</li></ol></details></div>';\n\t\thtml += '<div class=\"card\"><h2>Drafts from Claude or a script</h2>' + (s.drafts_api ? '<p class=\"ok\">On. Drafts can be sent to <code>' + esc(origin) + '/api/drafts</code> with the drafts token. They wait here for approval.</p>' : '<p>Off. Add a secret named <code>DRAFTS_TOKEN</code> to the Worker to turn it on.</p>') + '<p class=\"hint\">Social Posts ' + esc(s.version) + '</p></div>';\n\t\tapp.innerHTML = html;\n\t\tdocument.getElementById('sf').onsubmit = function (e) {\n\t\t\te.preventDefault();\n\t\t\tvar b = { test_mode: document.getElementById('tm').checked, site_name: document.getElementById('sn').value, site_link: document.getElementById('sl').value, accent: document.getElementById('ac').value,\n\t\t\t\tfacebook_via: (document.querySelector('input[name=fv]:checked') || {}).value, instagram_via: (document.querySelector('input[name=iv]:checked') || {}).value,\n\t\t\t\tdefault_platforms: Array.prototype.map.call(document.querySelectorAll('input[name=dp]:checked'), function (x) { return x.value; }) };\n\t\t\tapi('POST', '/api/settings', b).then(function () { flash('ok', b.test_mode ? 'Saved. Test mode is on.' : 'Saved. Test mode is off, so approved posts will go live.'); return load(); }).catch(function (er) { alert(er.message); });\n\t\t};\n\t\tvar dc = document.getElementById('dc');\n\t\tif (dc) { dc.onclick = function () { if (confirm('Disconnect Facebook and Instagram?')) { api('POST', '/api/disconnect', {}).then(function () { flash('ok', 'Disconnected.'); load(); }); } }; }\n\t\tdocument.getElementById('mf').onsubmit = function (e) {\n\t\t\te.preventDefault();\n\t\t\tvar cn = document.getElementById('cn'); cn.disabled = true; cn.textContent = 'Connecting\u2026';\n\t\t\tapi('POST', '/api/connect', { user_token: document.getElementById('ut').value, app_id: document.getElementById('ai').value, app_secret: document.getElementById('as').value }).then(function (r) {\n\t\t\t\tif (r.choose) {\n\t\t\t\t\tcn.disabled = false; cn.textContent = 'Connect';\n\t\t\t\t\tvar c = document.getElementById('choose');\n\t\t\t\t\tc.innerHTML = '<p><strong>Which Page should posts go to?</strong></p><div class=\"choose\">' + r.choose.map(function (pg) { return '<label><input type=\"radio\" name=\"pg\" value=\"' + esc(pg.id) + '\"> ' + esc(pg.name) + (pg.ig_user ? ' <span class=\"hint\">(Instagram @' + esc(pg.ig_user) + ')</span>' : ' <span class=\"hint\">(no Instagram linked)</span>') + '</label>'; }).join('') + '</div><button class=\"btn\" type=\"button\" id=\"pk\">Use this Page</button>';\n\t\t\t\t\tdocument.getElementById('pk').onclick = function () {\n\t\t\t\t\t\tvar v = (document.querySelector('input[name=pg]:checked') || {}).value; if (!v) { alert('Pick a Page.'); return; }\n\t\t\t\t\t\tapi('POST', '/api/connect/pick', { page_id: v }).then(done).catch(function (er) { alert(er.message); });\n\t\t\t\t\t};\n\t\t\t\t\treturn;\n\t\t\t\t}\n\t\t\t\tdone(r);\n\t\t\t}).catch(function (er) { cn.disabled = false; cn.textContent = 'Connect'; alert(er.message); });\n\t\t\tfunction done(r) { flash(r.warning ? 'err' : 'ok', r.warning || 'Connected. Facebook and Instagram are ready.'); load(); }\n\t\t};\n\t}\n\n\tload();\n}());\n</script>\n</body>\n</html>\n";

export default {
	async fetch(request, env, ctx) {
		try {
			return await route(request, env, ctx);
		} catch (err) {
			const msg = err && err.message ? err.message : String(err);
			return json({ error: msg }, err && err.status ? err.status : 500);
		}
	},
};

/* ------------------------------------------------------------------ */
/* Routing                                                            */
/* ------------------------------------------------------------------ */

async function route(request, env, ctx) {
	if (!env.SOCIAL) {
		return text('Setup is not finished: add a KV namespace binding named SOCIAL to this Worker.', 500);
	}
	if (!env.ADMIN_PASSWORD) {
		return text('Setup is not finished: add a secret named ADMIN_PASSWORD to this Worker.', 500);
	}
	globalThis.SP_GRAPH = env.GRAPH_URL || GRAPH; // GRAPH_URL is only for testing.
	const url = new URL(request.url);
	const path = url.pathname.replace(/\/+$/, '') || '/';
	const method = request.method;

	if (path === '/robots.txt') {
		return text('User-agent: *\nDisallow: /\n');
	}
	if (path.startsWith('/m/') && (method === 'GET' || method === 'HEAD')) {
		return serveMedia(request, env, path.slice(3));
	}
	if (path === '/' || path === '/index.html') {
		return new Response(APP_HTML, {
			headers: {
				'Content-Type': 'text/html; charset=utf-8',
				'Cache-Control': 'no-store',
				'X-Robots-Tag': 'noindex, nofollow',
				'X-Frame-Options': 'DENY',
				'Referrer-Policy': 'same-origin',
			},
		});
	}
	if (!path.startsWith('/api/')) {
		return text('Not found', 404);
	}

	// Sign-in does not need a session.
	if (path === '/api/login' && method === 'POST') {
		return login(request, env);
	}
	if (path === '/api/logout' && method === 'POST') {
		return json({ ok: true }, 200, { 'Set-Cookie': 'sp=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0' });
	}

	const who = await whoIs(request, env);
	if (!who) {
		return json({ error: 'Please sign in.' }, 401);
	}
	// Cookie sessions must send the X-SP header (blocks cross-site form posts).
	if (who.via === 'cookie' && method !== 'GET' && request.headers.get('X-SP') !== '1') {
		return json({ error: 'Bad request.' }, 400);
	}
	const bearerOk = ['/api/media', '/api/drafts', '/api/posts'];
	if (who.via === 'bearer' && !(bearerOk.includes(path) && method === 'POST') && !(path === '/api/state' && method === 'GET')) {
		return json({ error: 'The drafts token can only upload media and create drafts.' }, 403);
	}

	if (path === '/api/state' && method === 'GET') {
		return json(await state(env, who));
	}
	if (path === '/api/media' && method === 'POST') {
		return json(await uploadMedia(request, env, url));
	}
	if ((path === '/api/posts' || path === '/api/drafts') && method === 'POST') {
		const body = await readJson(request);
		const post = await savePost(env, null, body, who);
		return json({ id: post.id, status: 'draft', review_url: url.origin + '/#post/' + post.id });
	}
	let m = path.match(/^\/api\/posts\/([a-z0-9]+)(\/[a-z]+)?$/);
	if (m) {
		const id = m[1];
		const action = m[2] || '';
		if (!action && method === 'GET') {
			return json(await getPost(env, id, true));
		}
		if (!action && method === 'PUT') {
			return json(await savePost(env, id, await readJson(request), who));
		}
		if (!action && method === 'DELETE') {
			return json(await deletePost(env, id));
		}
		if (action === '/approve' && method === 'POST') {
			return json(await approve(env, id, who, url.origin));
		}
		if (action === '/check' && method === 'POST') {
			return json(await checkPending(env, id));
		}
		if (action === '/done' && method === 'POST') {
			const b = await readJson(request);
			return json(await phoneDone(env, id, String(b.platform || ''), b.undo === true));
		}
	}
	if (path === '/api/settings' && method === 'POST') {
		return json(await saveSettings(env, await readJson(request)));
	}
	if (path === '/api/connect' && method === 'POST') {
		return json(await metaConnect(env, await readJson(request)));
	}
	if (path === '/api/connect/pick' && method === 'POST') {
		return json(await metaPick(env, await readJson(request)));
	}
	if (path === '/api/disconnect' && method === 'POST') {
		const s = await getSettings(env);
		Object.assign(s, { meta_page_id: '', meta_page: '', meta_token: '', meta_ig_id: '', meta_ig_user: '', meta_at: 0 });
		await env.SOCIAL.put('settings', JSON.stringify(s));
		return json({ ok: true, settings: publicSettings(s, env) });
	}
	return json({ error: 'Not found.' }, 404);
}

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

function json(data, status = 200, headers = {}) {
	return new Response(JSON.stringify(data), {
		status,
		headers: Object.assign({ 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' }, headers),
	});
}

function text(body, status = 200) {
	return new Response(body, { status, headers: { 'Content-Type': 'text/plain; charset=utf-8', 'X-Robots-Tag': 'noindex' } });
}

function fail(message, status = 400) {
	const e = new Error(message);
	e.status = status;
	return e;
}

async function readJson(request) {
	try {
		return await request.json();
	} catch (e) {
		throw fail('Expected JSON.');
	}
}

function randomId(bytes = 9) {
	const a = new Uint8Array(bytes);
	crypto.getRandomValues(a);
	return Array.from(a, (b) => b.toString(36).padStart(2, '0')).join('').slice(0, bytes * 2).replace(/[^a-z0-9]/g, 'x');
}

function b64url(buf) {
	let s = '';
	new Uint8Array(buf).forEach((b) => (s += String.fromCharCode(b)));
	return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

async function hmac(env, data) {
	const key = await crypto.subtle.importKey('raw', new TextEncoder().encode('sp:' + (env.SESSION_SECRET || env.ADMIN_PASSWORD)), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
	return b64url(await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(data)));
}

async function sameText(a, b) {
	// Compare digests so the time taken does not depend on where they differ.
	const da = new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(String(a))));
	const db = new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(String(b))));
	let diff = 0;
	for (let i = 0; i < da.length; i++) diff |= da[i] ^ db[i];
	return diff === 0;
}

// Coach notes from the posting skills (post-writer, post-grader, viral-hooks): a score, the hook
// pattern, why it works, the grader's scorecard and up to 3 alternate captions. Display only.
function cleanCoach(c) {
	if (!c || typeof c !== 'object') return null;
	const num = (n) => { const v = Number(n); return isFinite(v) ? Math.max(0, Math.min(10, Math.round(v * 10) / 10)) : null; };
	const card = (a) => (Array.isArray(a) ? a : []).slice(0, 8).map((r) => ({ name: cleanText(r && r.name, 40).trim(), score: num(r && r.score) })).filter((r) => r.name && r.score !== null);
	const fixes = (a) => (Array.isArray(a) ? a : []).slice(0, 3).map((f) => cleanText(f, 300).trim()).filter(Boolean);
	const out = {
		score: num(c.score),
		hook: cleanText(c.hook, 80).trim(),
		why: cleanText(c.why, 400).trim(),
		scorecard: card(c.scorecard),
		fixes: fixes(c.fixes),
		alternates: (Array.isArray(c.alternates) ? c.alternates : []).slice(0, 3).filter((a) => a && typeof a === 'object').map((a) => ({ caption: cleanText(a.caption, 2200).trim(), hook: cleanText(a.hook, 80).trim(), score: num(a.score), why: cleanText(a.why, 400).trim(), scorecard: card(a.scorecard), fixes: fixes(a.fixes) })).filter((a) => a.caption),
	};
	return out.score === null && !out.hook && !out.why && !out.alternates.length ? null : out;
}

function cleanText(s, max) {
	return String(s == null ? '' : s).replace(/\r\n/g, '\n').slice(0, max);
}

/* ------------------------------------------------------------------ */
/* Sign-in                                                            */
/* ------------------------------------------------------------------ */

async function login(request, env) {
	const b = await readJson(request);
	const ip = request.headers.get('CF-Connecting-IP') || 'x';
	const lockKey = 'lock:' + ip;
	const tries = parseInt((await env.SOCIAL.get(lockKey)) || '0', 10);
	if (tries >= 8) {
		return json({ error: 'Too many tries. Wait 15 minutes and try again.' }, 429);
	}
	if (!(await sameText(b.password || '', env.ADMIN_PASSWORD))) {
		await env.SOCIAL.put(lockKey, String(tries + 1), { expirationTtl: 900 });
		await new Promise((r) => setTimeout(r, 800));
		return json({ error: "That password didn't work. Try again." }, 401);
	}
	const name = cleanText(b.name, 40).replace(/[|]/g, '').trim() || 'Staff';
	const days = b.remember ? 30 : 1;
	const exp = Math.floor(Date.now() / 1000) + days * 86400;
	const payload = b64url(new TextEncoder().encode(exp + '|' + name));
	const token = payload + '.' + (await hmac(env, payload));
	return json({ ok: true }, 200, {
		'Set-Cookie': 'sp=' + token + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=' + days * 86400,
	});
}

async function whoIs(request, env) {
	const auth = request.headers.get('Authorization') || '';
	if (auth.startsWith('Bearer ') && env.DRAFTS_TOKEN) {
		if (await sameText(auth.slice(7).trim(), env.DRAFTS_TOKEN)) {
			return { name: 'Drafts API', via: 'bearer' };
		}
		return null;
	}
	const cookie = request.headers.get('Cookie') || '';
	const m = cookie.match(/(?:^|;\s*)sp=([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)/);
	if (!m) return null;
	if (!(await sameText(await hmac(env, m[1]), m[2]))) return null;
	let raw;
	try {
		raw = atob(m[1].replace(/-/g, '+').replace(/_/g, '/'));
		raw = new TextDecoder().decode(Uint8Array.from(raw, (c) => c.charCodeAt(0)));
	} catch (e) {
		return null;
	}
	const [exp, name] = raw.split('|');
	if (parseInt(exp, 10) < Date.now() / 1000) return null;
	return { name: name || 'Staff', via: 'cookie' };
}

/* ------------------------------------------------------------------ */
/* Settings                                                           */
/* ------------------------------------------------------------------ */

async function getSettings(env) {
	const raw = await env.SOCIAL.get('settings', 'json');
	return Object.assign({}, DEFAULT_SETTINGS, raw || {});
}

function publicSettings(s, env) {
	const out = Object.assign({}, s);
	delete out.meta_token;
	out.connected = !!s.meta_token;
	out.site_name = s.site_name || env.SITE_NAME || 'Social Posts';
	out.drafts_api = !!env.DRAFTS_TOKEN;
	out.version = VERSION;
	return out;
}

async function saveSettings(env, b) {
	const s = await getSettings(env);
	if ('test_mode' in b) s.test_mode = !!b.test_mode;
	if ('site_name' in b) s.site_name = cleanText(b.site_name, 80).trim();
	if ('site_link' in b) {
		const l = cleanText(b.site_link, 300).trim();
		s.site_link = /^https?:\/\//i.test(l) || l === '' ? l : 'https://' + l;
	}
	if ('accent' in b && /^#[0-9a-f]{6}$/i.test(String(b.accent))) s.accent = b.accent;
	if ('facebook_via' in b) s.facebook_via = b.facebook_via === 'share' ? 'share' : 'meta';
	if ('instagram_via' in b) s.instagram_via = b.instagram_via === 'share' ? 'share' : 'meta';
	if (Array.isArray(b.default_platforms)) s.default_platforms = b.default_platforms.filter((p) => PLATFORMS[p]);
	if ('graph_version' in b && /^v\d+\.\d+$/.test(String(b.graph_version))) s.graph_version = b.graph_version;
	await env.SOCIAL.put('settings', JSON.stringify(s));
	return { ok: true, settings: publicSettings(s, env) };
}

/* ------------------------------------------------------------------ */
/* Media                                                              */
/* ------------------------------------------------------------------ */

async function uploadMedia(request, env, url) {
	const type = (request.headers.get('Content-Type') || '').split(';')[0].trim().toLowerCase();
	if (!/^(image\/(jpeg|png|webp|gif)|video\/(mp4|quicktime))$/.test(type)) {
		throw fail('Use a JPEG, PNG or WebP photo, or an MP4 or MOV video.');
	}
	const len = parseInt(request.headers.get('Content-Length') || '0', 10);
	if (len > MAX_MEDIA) throw fail('That file is over 25 MB. Make it smaller and try again.');
	const buf = await request.arrayBuffer();
	if (buf.byteLength > MAX_MEDIA) throw fail('That file is over 25 MB. Make it smaller and try again.');
	if (!buf.byteLength) throw fail('The file was empty.');
	const name = cleanText(request.headers.get('X-Filename') || 'media', 120).replace(/[^\w.\- ]/g, '');
	const w = parseInt(request.headers.get('X-Width') || '0', 10) || 0;
	const h = parseInt(request.headers.get('X-Height') || '0', 10) || 0;
	const ext = { 'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp', 'image/gif': 'gif', 'video/mp4': 'mp4', 'video/quicktime': 'mov' }[type];
	const key = randomId(12) + '.' + ext;
	await env.SOCIAL.put('media:' + key, buf, { metadata: { type, name, w, h, size: buf.byteLength } });
	return { key, type, name, w, h, url: url.origin + '/m/' + key };
}

async function serveMedia(request, env, key) {
	if (!/^[a-z0-9]+\.(jpg|png|webp|gif|mp4|mov)$/.test(key)) return text('Not found', 404);
	const { value, metadata } = await env.SOCIAL.getWithMetadata('media:' + key, 'arrayBuffer');
	if (!value) return text('Not found', 404);
	const type = (metadata && metadata.type) || 'application/octet-stream';
	const total = value.byteLength;
	const base = {
		'Content-Type': type,
		'Accept-Ranges': 'bytes',
		'Cache-Control': 'public, max-age=86400',
		'X-Robots-Tag': 'noindex',
	};
	const range = request.headers.get('Range');
	const m = range && range.match(/bytes=(\d*)-(\d*)/);
	if (m && (m[1] || m[2])) {
		let start = m[1] ? parseInt(m[1], 10) : total - parseInt(m[2], 10);
		let end = m[1] && m[2] ? parseInt(m[2], 10) : total - 1;
		start = Math.max(0, start);
		end = Math.min(end, total - 1);
		if (start > end) return new Response(null, { status: 416, headers: { 'Content-Range': 'bytes */' + total } });
		return new Response(request.method === 'HEAD' ? null : value.slice(start, end + 1), {
			status: 206,
			headers: Object.assign({}, base, { 'Content-Range': 'bytes ' + start + '-' + end + '/' + total, 'Content-Length': String(end - start + 1) }),
		});
	}
	return new Response(request.method === 'HEAD' ? null : value, { headers: Object.assign({}, base, { 'Content-Length': String(total) }) });
}

async function mediaInfo(env, key) {
	const { metadata } = await env.SOCIAL.getWithMetadata('media:' + key, 'stream');
	return metadata || null;
}

/* ------------------------------------------------------------------ */
/* Posts                                                              */
/* ------------------------------------------------------------------ */

async function getIndex(env) {
	return (await env.SOCIAL.get('index', 'json')) || [];
}

async function putIndexEntry(env, post) {
	const idx = (await getIndex(env)).filter((e) => e.id !== post.id);
	idx.unshift({ id: post.id, status: post.status, kind: post.kind, created: post.created, sent_at: post.sent_at || 0 });
	idx.sort((a, b) => (b.sent_at || b.created) - (a.sent_at || a.created));
	await env.SOCIAL.put('index', JSON.stringify(idx.slice(0, 500)));
}

async function getPost(env, id, must) {
	const p = await env.SOCIAL.get('post:' + id, 'json');
	if (!p && must) throw fail('That post was not found. It may have been deleted.', 404);
	return p;
}

async function state(env, who) {
	const s = await getSettings(env);
	const idx = await getIndex(env);
	const recent = idx.slice(0, 60);
	const posts = (await Promise.all(recent.map((e) => getPost(env, e.id, false)))).filter(Boolean);
	return { who: who.name, settings: publicSettings(s, env), platforms: PLATFORMS, posts };
}

async function savePost(env, id, b, who) {
	let post = id ? await getPost(env, id, true) : null;
	if (post && post.status !== 'draft') throw fail('That post was already approved, so it can no longer be edited.');
	const kind = b.kind === 'video' ? 'video' : 'photo';
	const platforms = (Array.isArray(b.platforms) ? b.platforms : []).filter((p) => PLATFORMS[p] && PLATFORMS[p][kind]);
	if (!platforms.length) throw fail('Tick at least one place to post.');
	const keys = (Array.isArray(b.media) ? b.media : []).map(String).filter((k) => /^[a-z0-9]+\.(jpg|png|webp|gif|mp4|mov)$/.test(k));
	if (!keys.length) throw fail(kind === 'video' ? 'Add a video.' : 'Add at least one photo.');
	if (kind === 'video' && keys.length > 1) throw fail('A video post takes one video.');
	if (kind === 'photo' && keys.length > 10) throw fail('Use up to 10 photos.');
	const media = [];
	for (const k of keys) {
		const info = await mediaInfo(env, k);
		if (!info) throw fail('A file is missing. Upload it again.');
		if (kind === 'photo' && !info.type.startsWith('image/')) throw fail('A photo post takes photos only.');
		if (kind === 'video' && !info.type.startsWith('video/')) throw fail('A video post takes a video file.');
		const igKey = Array.isArray(b.ig_media) ? b.ig_media[keys.indexOf(k)] : '';
		media.push({ key: k, type: info.type, w: info.w, h: info.h, ig_key: igKey && /^[a-z0-9]+\.jpg$/.test(igKey) ? igKey : '' });
	}
	const caption = cleanText(b.caption, 2200).trim();
	if (!caption) throw fail('Write the post text.');
	const title = cleanText(b.title, 100).trim();
	if (kind === 'video' && platforms.includes('youtube') && !title) throw fail('YouTube needs a title.');
	const now = Date.now();
	post = Object.assign(post || { id: randomId(8), created: now, author: who.name, results: {}, status: 'draft' }, {
		kind,
		platforms,
		media,
		caption,
		title,
		post_on: /^\d{4}-\d{2}-\d{2}$/.test(String(b.post_on || '')) ? String(b.post_on) : (post && post.post_on) || '',
		coach: b.coach !== undefined ? cleanCoach(b.coach) : post && post.coach ? Object.assign({}, post.coach, { edited: post.coach.edited || post.caption !== caption }) : null,
		updated: now,
	});
	await env.SOCIAL.put('post:' + post.id, JSON.stringify(post));
	await putIndexEntry(env, post);
	return post;
}

async function deletePost(env, id) {
	const post = await getPost(env, id, true);
	await env.SOCIAL.delete('post:' + id);
	const idx = (await getIndex(env)).filter((e) => e.id !== id);
	await env.SOCIAL.put('index', JSON.stringify(idx));
	// Facebook and Instagram keep their own copies, so the files can go.
	for (const m of post.media) {
		await env.SOCIAL.delete('media:' + m.key);
		if (m.ig_key) await env.SOCIAL.delete('media:' + m.ig_key);
	}
	return { ok: true };
}

function viaOf(s, p) {
	if (p === 'facebook') return s.facebook_via === 'share' ? 'phone' : 'meta';
	if (p === 'instagram') return s.instagram_via === 'share' ? 'phone' : 'meta';
	return 'phone';
}

function overallStatus(post) {
	const r = post.results || {};
	let todo = false;
	let failed = false;
	let processing = false;
	for (const p of post.platforms) {
		const x = r[p];
		if (!x) {
			todo = true;
			continue;
		}
		if (x.state === 'failed') failed = true;
		if (x.state === 'processing') processing = true;
		if (x.state === 'phone') todo = true;
	}
	if (failed) return 'failed';
	if (processing) return 'processing';
	if (todo) return 'todo';
	return 'sent';
}

async function approve(env, id, who, origin) {
	const post = await getPost(env, id, true);
	const s = await getSettings(env);
	post.results = post.results || {};
	const test = !!s.test_mode;
	for (const p of post.platforms) {
		const prev = post.results[p];
		if (prev && prev.state !== 'failed') continue; // Only retry what failed.
		const via = viaOf(s, p);
		if (via === 'phone') {
			post.results[p] = { state: 'phone', via, test };
			continue;
		}
		if (test) {
			post.results[p] = { state: 'test', via, test, message: testMessage(p, post, s) };
			continue;
		}
		try {
			post.results[p] = p === 'facebook' ? await sendFacebook(post, s, origin) : await sendInstagram(post, s, origin);
		} catch (err) {
			post.results[p] = { state: 'failed', via, message: err.message || String(err) };
		}
	}
	post.approved_by = who.name;
	post.sent_at = post.sent_at || Date.now();
	post.status = overallStatus(post);
	await env.SOCIAL.put('post:' + post.id, JSON.stringify(post));
	await putIndexEntry(env, post);
	return post;
}

function testMessage(p, post, s) {
	const what = post.kind === 'video' ? 'the video' : post.media.length > 1 ? post.media.length + ' photos' : 'the photo';
	if (p === 'facebook') return 'Test mode: would post ' + what + ' with the text to the Facebook Page' + (s.meta_page ? ' "' + s.meta_page + '"' : '') + '.';
	return 'Test mode: would post ' + what + ' with the text to Instagram' + (s.meta_ig_user ? ' @' + s.meta_ig_user : '') + (post.kind === 'video' ? ' as a Reel.' : '.');
}

async function phoneDone(env, id, platform, undo) {
	const post = await getPost(env, id, true);
	const r = post.results && post.results[platform];
	if (!r || (r.state !== 'phone' && r.state !== 'done')) throw fail('Nothing to mark for that platform.');
	r.state = undo ? 'phone' : 'done';
	r.done_at = undo ? 0 : Date.now();
	post.status = overallStatus(post);
	await env.SOCIAL.put('post:' + post.id, JSON.stringify(post));
	await putIndexEntry(env, post);
	return post;
}

/* ------------------------------------------------------------------ */
/* Meta Graph API                                                     */
/* ------------------------------------------------------------------ */

async function graph(s, method, path, params, token) {
	const u = new URL((globalThis.SP_GRAPH || GRAPH) + (s.graph_version || 'v24.0') + '/' + path);
	const body = new URLSearchParams();
	const all = Object.assign({}, params || {}, { access_token: token || s.meta_token });
	for (const [k, v] of Object.entries(all)) {
		if (v === undefined || v === null || v === '') continue;
		(method === 'GET' ? u.searchParams : body).append(k, typeof v === 'object' ? JSON.stringify(v) : String(v));
	}
	const res = await fetch(u.toString(), method === 'GET' ? { method } : { method, body });
	let data = {};
	try {
		data = await res.json();
	} catch (e) {
		/* not JSON */
	}
	if (!res.ok || data.error) {
		const e = data.error || {};
		let msg = e.error_user_msg || e.message || 'Facebook answered with HTTP ' + res.status + '.';
		if (e.code === 190) msg = 'The Facebook connection has expired or was removed. Connect again under Settings. (' + msg + ')';
		if (e.code === 10 || e.code === 200) msg = 'Facebook refused permission: ' + msg + ' Check the permissions on the access token and connect again.';
		throw new Error(msg);
	}
	return data;
}

function mediaUrl(origin, m, forIg) {
	return origin + '/m/' + (forIg && m.ig_key ? m.ig_key : m.key);
}

async function sendFacebook(post, s, origin) {
	if (!s.meta_token || !s.meta_page_id) throw new Error('Facebook is not connected yet. Connect it under Settings.');
	const page = s.meta_page_id;
	if (post.kind === 'video') {
		const params = { file_url: mediaUrl(origin, post.media[0]), description: post.caption };
		if (post.title) params.title = post.title;
		const r = await graph(s, 'POST', page + '/videos', params);
		return { state: 'sent', via: 'meta', id: r.id, url: 'https://www.facebook.com/' + page + '/videos/' + r.id };
	}
	if (post.media.length === 1) {
		const r = await graph(s, 'POST', page + '/photos', { url: mediaUrl(origin, post.media[0]), message: post.caption });
		const pid = r.post_id || r.id;
		return { state: 'sent', via: 'meta', id: pid, url: 'https://www.facebook.com/' + pid };
	}
	const ids = [];
	for (const m of post.media) {
		const r = await graph(s, 'POST', page + '/photos', { url: mediaUrl(origin, m), published: 'false' });
		ids.push(r.id);
	}
	const params = { message: post.caption };
	ids.forEach((fid, i) => (params['attached_media[' + i + ']'] = JSON.stringify({ media_fbid: fid })));
	const r = await graph(s, 'POST', page + '/feed', params);
	return { state: 'sent', via: 'meta', id: r.id, url: 'https://www.facebook.com/' + r.id };
}

async function igWait(s, cid, tries) {
	for (let i = 0; i < tries; i++) {
		const st = await graph(s, 'GET', cid, { fields: 'status_code,status' });
		if (st.status_code === 'FINISHED') return 'ready';
		if (st.status_code === 'ERROR' || st.status_code === 'EXPIRED') {
			throw new Error('Instagram could not process this file (' + (st.status || st.status_code) + '). Photos should be JPEG between 4:5 and 1.91:1; videos MP4 (H.264), 3 to 90 seconds.');
		}
		await new Promise((r) => setTimeout(r, i < 3 ? 2000 : 3000));
	}
	return 'waiting';
}

async function igPublish(s, cid) {
	const pub = await graph(s, 'POST', s.meta_ig_id + '/media_publish', { creation_id: cid });
	let link = '';
	try {
		link = (await graph(s, 'GET', pub.id, { fields: 'permalink' })).permalink || '';
	} catch (e) {
		/* link is optional */
	}
	return { state: 'sent', via: 'meta', id: pub.id, url: link };
}

async function sendInstagram(post, s, origin) {
	if (!s.meta_token || !s.meta_ig_id) throw new Error('Instagram is not connected yet. Connect it under Settings (the Instagram account must be linked to the Facebook Page).');
	const ig = s.meta_ig_id;
	let cid;
	if (post.kind === 'video') {
		cid = (await graph(s, 'POST', ig + '/media', { media_type: 'REELS', video_url: mediaUrl(origin, post.media[0]), caption: post.caption, share_to_feed: 'true' })).id;
		const st = await igWait(s, cid, 12);
		if (st !== 'ready') {
			return { state: 'processing', via: 'meta', container: cid, message: 'Instagram is still processing the video. Open this post again in a few minutes to finish it.' };
		}
		return igPublish(s, cid);
	}
	if (post.media.length === 1) {
		cid = (await graph(s, 'POST', ig + '/media', { image_url: mediaUrl(origin, post.media[0], true), caption: post.caption })).id;
	} else {
		const children = [];
		for (const m of post.media) {
			children.push((await graph(s, 'POST', ig + '/media', { image_url: mediaUrl(origin, m, true), is_carousel_item: 'true' })).id);
		}
		cid = (await graph(s, 'POST', ig + '/media', { media_type: 'CAROUSEL', children: children.join(','), caption: post.caption })).id;
	}
	const st = await igWait(s, cid, 10);
	if (st !== 'ready') {
		return { state: 'processing', via: 'meta', container: cid, message: 'Instagram is still processing. Open this post again in a minute to finish it.' };
	}
	return igPublish(s, cid);
}

async function checkPending(env, id) {
	const post = await getPost(env, id, true);
	const s = await getSettings(env);
	const r = post.results && post.results.instagram;
	if (r && r.state === 'processing' && r.container) {
		try {
			const st = await igWait(s, r.container, 4);
			if (st === 'ready') post.results.instagram = await igPublish(s, r.container);
		} catch (err) {
			post.results.instagram = { state: 'failed', via: 'meta', message: err.message || String(err) };
		}
		post.status = overallStatus(post);
		await env.SOCIAL.put('post:' + post.id, JSON.stringify(post));
		await putIndexEntry(env, post);
	}
	return post;
}

async function metaConnect(env, b) {
	const s = await getSettings(env);
	let token = String(b.user_token || '').trim();
	if (!token) throw fail('Paste the access token from the Graph API Explorer.');
	const appId = String(b.app_id || '').trim();
	const secret = String(b.app_secret || '').trim();
	if (appId && secret) {
		// Swap the short token for a long one. The secret is used once and not kept.
		const ex = await graph(s, 'GET', 'oauth/access_token', { grant_type: 'fb_exchange_token', client_id: appId, client_secret: secret, fb_exchange_token: token }, token);
		token = ex.access_token;
	}
	const pages = await graph(s, 'GET', 'me/accounts', { fields: 'id,name,access_token,instagram_business_account{id,username}', limit: 100 }, token);
	const list = (pages.data || []).map((p) => ({
		id: String(p.id),
		name: p.name,
		token: p.access_token,
		ig_id: p.instagram_business_account ? String(p.instagram_business_account.id) : '',
		ig_user: p.instagram_business_account ? p.instagram_business_account.username || '' : '',
	}));
	if (!list.length) throw fail('No Facebook Pages came back. In the Graph API Explorer, pick your Page when Facebook asks which Pages to allow, then try again.');
	await env.SOCIAL.put('pending_pages', JSON.stringify(list), { expirationTtl: 900 });
	if (list.length === 1) return metaPick(env, { page_id: list[0].id });
	return { ok: true, choose: list.map((p) => ({ id: p.id, name: p.name, ig_user: p.ig_user })) };
}

async function metaPick(env, b) {
	const list = (await env.SOCIAL.get('pending_pages', 'json')) || [];
	const pick = list.find((p) => p.id === String(b.page_id || ''));
	if (!pick) throw fail('That choice expired. Paste the token and connect again.');
	const s = await getSettings(env);
	Object.assign(s, {
		meta_page_id: pick.id,
		meta_page: pick.name,
		meta_token: pick.token,
		meta_ig_id: pick.ig_id,
		meta_ig_user: pick.ig_user,
		meta_at: Date.now(),
	});
	await graph(s, 'GET', 'me', { fields: 'id' });
	await env.SOCIAL.put('settings', JSON.stringify(s));
	await env.SOCIAL.delete('pending_pages');
	return {
		ok: true,
		settings: publicSettings(s, env),
		warning: pick.ig_id ? '' : 'Facebook is connected, but no Instagram Business account is linked to this Page. Link it in the Page settings, then connect again.',
	};
}
