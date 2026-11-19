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

const APP_HTML = __APP_HTML__;

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
