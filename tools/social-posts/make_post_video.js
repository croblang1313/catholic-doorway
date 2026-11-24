// Renders one Catholic Doorway TikTok/Reels video (1080x1920 MP4, 30 fps, 10-14 s, with original audio).
// Usage: node make_post_video.js spec.json out.mp4
// spec: the same image spec as make_post_image.js (kicker, title, body, ref, theme) plus
//   "format": "reveal" | "kinetic" | "list" | "split" | "scripture"   (default reveal; vary them!)
//   "hook":   big first line, under ~60 characters; *word* or *two words* = gold
//   "path":   "/saints"   page shown on the end card (optional)
//   "art":    "window" | "none"   background photo (the CC0 Holy Spirit window; don't add CC BY-SA photos)
//   "lines":  ["Short", "punchy", "beats"]     kinetic: 3-5 lines of up to ~6 words (default: hook, title, ref)
//   "items":  ["One", "Two", "Three"]           list: 3 items of up to ~8 words (required for list)
//   "list_title": "3 things to know"            list: heading (default: the hook)
//   "quote":  "Short Scripture or prayer line"   scripture: RSV-CE wording (default: body)
// Formats:
//   reveal    hook pops in word by word, the post card builds, end card. Slow zoom on the window. Pad + bells.
//   kinetic   one bold line per beat on alternating navy/gold screens with sliding stripes. Pulse + plucks.
//   list      numbered items slide in one at a time over a sideways pan. Rising chime per item.
//   split     photo on top with a slow push-in, text band below (like a lower third). Warm pad.
//   scripture candlelit dark scene, words of a verse appear one by one, rising light motes. Drone + choir hum.
// Every video ends on the same end card and closing bell, so the brand stays recognizable.
// Day-to-day looks (video_looks.js): each post date gets its own logo corner, picture/word placement,
// photo motion, word entrance, highlight style, scene change and hook lettering, so no two days look alike.
//   "post_on": "2026-11-30"   the post's date (send_drafts.py fills it in; default today)
//   "prev_on": "2026-11-27"   the previous post's date (send_drafts.py fills it in), so the logo corner changes
//   "look":    {"corner": "top-right", ...}   optional overrides of any part of the day's look
// All sound is synthesized here with numpy (nothing to license). Text stays clear of TikTok's bottom/right UI.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { spawn, execFileSync } = require('child_process');

const W = 1080, H = 1920, FPS = 30;
const esc = (s) => String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NAVY = '#1d2b4f', GOLD = '#a8802f', CREAM = '#faf6ee', LGOLD = '#e9cf8e';
const mark = (line, gold, op) => `<svg viewBox="0 0 34 40" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block"><path d="M3 39V17C3 8.7 9.3 2 17 2s14 6.7 14 15v22" fill="none" stroke="${line}" stroke-width="2.4"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="${line}" opacity="${op}"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="none" stroke="${line}" stroke-width="1.6"/><path d="M17 12v9M13.6 15.2h6.8" stroke="${gold}" stroke-width="2" stroke-linecap="round"/><circle cx="22" cy="28" r="1.4" fill="${gold}"/><path d="M1 39h32" stroke="${line}" stroke-width="2.4" stroke-linecap="round"/></svg>`;

const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = process.argv[3];
const { lookFor } = require('./video_looks.js');
const LOOK = Object.assign(lookFor(spec.post_on || new Date().toISOString().slice(0, 10), spec.prev_on), spec.look || {});
const navy = spec.theme !== 'cream';
const ink = navy ? CREAM : NAVY, accent = navy ? LGOLD : GOLD;

// Background art: the Holy Spirit window, St. Peter's Basilica (Wilfredor, Wikimedia Commons, CC0).
const ART = { window: 'bg-window.jpg' };
let artUrl = '';
if (spec.art !== 'none') {
  const name = ART[spec.art] || ART.window;
  const cands = [path.join(__dirname, 'art', name), path.join(__dirname, '../../site/assets/img', name)];
  const f = cands.find((c) => fs.existsSync(c));
  if (f) artUrl = 'data:image/jpeg;base64,' + fs.readFileSync(f).toString('base64');
}
const overlay = navy
  ? 'linear-gradient(180deg,rgba(19,29,56,.80) 0%,rgba(29,43,79,.72) 45%,rgba(19,29,56,.92) 100%)'
  : 'linear-gradient(180deg,rgba(236,223,196,.86) 0%,rgba(244,236,220,.82) 45%,rgba(250,246,238,.94) 100%)';

// Words wrapped in *asterisks* are highlighted in gold (a span may cover several words).
const words = (s, cls, start, step) => { let on = false; return String(s || '').split(/\s+/).filter(Boolean).map((w, i) => {
  const opens = w.startsWith('*'), closes = /\*[.,!?:;]*$/.test(w) && (w.length > 1 || on);
  if (opens) on = true; const em = on; if (closes) on = false;
  return `<span class="${cls}${em ? ' em' : ''}" style="animation-delay:${(start + i * step).toFixed(2)}s">${esc(w.replace(/\*/g, ''))}</span>`;
}).join(' '); };
const plain = (s) => String(s || '').replace(/\*/g, '');
const nWords = (s) => String(s || '').split(/\s+/).filter(Boolean).length;
const hook = spec.hook || spec.title || '';
const title = spec.title || '';
const fit = (s, sizes) => { const n = plain(s).length; return n > 55 ? sizes[0] : n > 34 ? sizes[1] : sizes[2]; };
const scene = (a, b, extra) => `class="scene${extra ? ' ' + extra : ''}" style="animation:fin .45s ease-out ${a}s both${b ? `, fout .4s ease-in ${b}s forwards` : ''}"`;

let format = spec.format || 'reveal';
if (format === 'list' && !(Array.isArray(spec.items) && spec.items.length)) format = 'reveal';
if (format === 'scripture' && !(spec.quote || spec.body)) format = 'split';

// Where the words and the picture go. "frame" layouts (reveal only) start with the photo inside a shape
// (an arched window, a band, a side strip) and the words beside it; then the window opens to full screen.
const LAYOUTS = {
  'full-center': { v: 'center', h: 'center' },
  'full-low-left': { v: 'bottom', h: 'left' },
  'full-high-left': { v: 'top', h: 'left' },
  'arch-window': { v: 'bottom', h: 'center', frame: 'arch', pad: [1080, 110, 500, 110] },
  'photo-band': { v: 'top', h: 'center', frame: 'band', pad: [300, 110, 960, 110] },
  'photo-strip': { v: 'center', h: 'left', frame: 'strip', pad: [260, 430, 520, 96], scale: 0.8 },
};
const LAY = Object.assign({}, LAYOUTS[LOOK.layout] || LAYOUTS['full-center']);
if (format !== 'reveal') { delete LAY.frame; delete LAY.pad; delete LAY.scale; }
const TYPE_SCALE = { sans: 1, serif: 1.12, caps: 0.86 }[LOOK.type] || 1;
const hs = (px) => Math.round(px * TYPE_SCALE * (LAY.scale || 1)); // hook font size for the day's lettering and layout
const OPEN = 3.0; // reveal: when a framed photo opens to full screen

// Each format returns {dur, end (end-card start), css, html, audio}.
function reveal() {
  const bodyN = nWords(spec.body), step = Math.min(0.07, 2.0 / Math.max(bodyN, 1));
  return {
    dur: 11, end: 8.6, bg: 'kb', css: '',
    html: `<div ${scene(0, 3.0, 'hk')}><div class="hook" style="font-size:${hs(fit(hook, [86, 100, 118]))}px">${words(hook, 'hw', 0.25, Math.min(0.22, 1.6 / Math.max(nWords(hook), 1)))}</div></div>
<div ${scene(3.1, 8.2, 'cd')}>
 <div class="mk" style="animation-delay:3.2s">${mark(accent, accent, 0.14)}</div>
 <div class="k" style="animation-delay:3.4s">${esc(spec.kicker)}</div>
 <div class="rule" style="animation-delay:3.6s"></div>
 <div class="t" style="font-size:${title.length > 40 ? 92 : title.length > 24 ? 108 : 128}px">${words(title, 'tw', 3.8, 0.14)}</div>
 ${spec.body ? `<div class="b">${words(spec.body, 'bw', 4.7, step)}</div>` : ''}
 ${spec.ref ? `<div class="r" style="animation-delay:${(4.9 + bodyN * step).toFixed(2)}s">${esc(spec.ref)}</div>` : ''}
</div>`,
    audio: { key: 73.42, chord: [1, 1.5, 2, 2.52, 3, 4.49], pad: 0.55, bells: [[0.25, 587.33], [3.8, 880]] },
  };
}
function kinetic() {
  const lines = (Array.isArray(spec.lines) && spec.lines.length ? spec.lines : [hook, title, spec.ref].filter(Boolean)).slice(0, 5);
  const beat = 1.7, t0 = 0.2, end = t0 + lines.length * beat + 0.2;
  const html = lines.map((l, i) => {
    const a = t0 + i * beat, alt = i % 2 === 1;
    return `<div ${scene(a, a + beat - 0.15, 'kin hk' + (alt ? ' alt' : ''))}><div class="kline" style="animation-delay:${a.toFixed(2)}s;font-size:${fit(l, [96, 118, 150])}px">${words(l, 'kw', a + 0.05, 0.06)}</div></div>`;
  }).join('\n');
  const css = `.kin{padding:300px 110px 560px}
.kin::before{content:'';position:absolute;inset:-20%;background:repeating-linear-gradient(-35deg,rgba(255,255,255,.05) 0 40px,transparent 40px 120px);animation:slide 2s linear infinite}
.kin.alt{background:${accent}}.kin.alt .kline{color:${NAVY}}.kin.alt .em{color:#fff;text-shadow:0 3px 0 rgba(29,43,79,.35)}
.kin:not(.alt){background:${navy ? NAVY : CREAM}}
.kline{position:relative;font-family:'Source Sans 3';font-weight:800;line-height:1.05;color:${ink};text-transform:uppercase;letter-spacing:-.01em;animation:slam .5s cubic-bezier(.2,1.5,.4,1) both}
.kline .em{color:${accent}}
.kw{display:inline-block;opacity:0;animation:fade .2s ease-out both}
@keyframes slam{from{transform:scale(1.6) rotate(-4deg);opacity:0}to{transform:none;opacity:1}}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(146px)}}`;
  return {
    dur: end + 2.6, end, bg: 'none', css, html,
    audio: { key: 110, chord: [1, 1.5, 2, 2.38, 3], pad: 0.3, bpm: 105, pulseEnd: end,
      plucks: lines.map((_, i) => [t0 + i * beat, 440 * [1, 1.189, 1.335, 1.498, 1.782][i % 5]]) },
  };
}
function list() {
  const items = spec.items.slice(0, 4), head = spec.list_title || hook, t0 = 2.2, gap = 2.0;
  const end = t0 + items.length * gap + 1.0;
  const html = `<div ${scene(0, end - 0.4, 'lst')}>
 <div class="lh" style="font-size:${hs(fit(head, [76, 88, 104]))}px">${words(head, 'hw', 0.2, 0.12)}</div>
 <ol class="li">${items.map((it, i) => `<li style="animation-delay:${(t0 + i * gap).toFixed(2)}s"><span class="n" style="animation-delay:${(t0 + i * gap).toFixed(2)}s">${i + 1}</span><span>${words(it, 'em0', t0 + i * gap + 0.35, 0)}</span></li>`).join('')}</ol>
</div>`;
  const css = `.lst{justify-content:center;align-items:stretch;text-align:left;padding:240px 110px 540px}
.lh{font-family:'Source Sans 3';font-weight:800;line-height:1.08;color:${ink};margin-bottom:60px;text-align:center}.lh .em{color:${accent}}
.li{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:34px}
.li li{display:flex;gap:30px;align-items:center;font-family:'Source Serif 4';font-weight:600;font-size:56px;line-height:1.25;color:${ink};
 background:${navy ? 'rgba(255,255,255,.07)' : 'rgba(29,43,79,.06)'};border-left:6px solid ${accent};border-radius:14px;padding:26px 30px;opacity:0;animation:slidein .6s cubic-bezier(.2,1.2,.4,1) both}
.li .em{color:${accent}}
.n{flex:none;width:86px;height:86px;border-radius:50%;background:${accent};color:${navy ? NAVY : CREAM};font-family:'Source Sans 3';font-weight:800;font-size:50px;display:flex;align-items:center;justify-content:center;animation:pop .5s cubic-bezier(.2,1.6,.4,1) both}
@keyframes slidein{from{opacity:0;transform:translateX(-120px)}to{opacity:1;transform:none}}`;
  return {
    dur: end + 2.6, end, bg: 'kb', css, html,
    audio: { key: 98, chord: [1, 1.5, 2, 2.52, 3.36], pad: 0.45, bells: [[0.2, 783.99]],
      chimes: items.map((_, i) => [t0 + i * gap, 587.33 * [1, 1.122, 1.26, 1.335][i]]) },
  };
}
function split() {
  // The photo sits on the same side as the day's logo corner, so the small logo is always over the picture:
  // top corners = photo on top, text band below; bottom corners = text band on top, photo below.
  const end = 7.8, flip = /^bottom/.test(LOOK.corner);
  const html = `<div class="sp-photo"></div><div class="sp-shade"></div>
<div ${scene(0, 3.0, 'sp-top')}><div class="sp-hook" style="font-size:${hs(fit(hook, [70, 80, 92]))}px">${words(hook, 'hw', 0.3, Math.min(0.2, 1.5 / Math.max(nWords(hook), 1)))}</div></div>
<div class="sp-band" style="animation:bandup .7s cubic-bezier(.2,1,.3,1) 0.1s both">
 <div class="sp-row"><div class="sp-k">${esc(spec.kicker)}</div></div>
 <div class="sp-t" style="font-size:${title.length > 30 ? 84 : 104}px">${words(title, 'tw', 3.2, 0.16)}</div>
 <div class="sp-line" style="animation-delay:4.2s"></div>
 ${spec.body ? `<div class="sp-b" style="animation-delay:4.6s">${esc(plain(spec.body))}</div>` : ''}
</div>`;
  const css = `.sp-photo{position:absolute;left:0;right:0;top:0;height:62%;background:${artUrl ? `url(${artUrl}) center 30%/cover` : NAVY};animation:pm 10s linear both}
.sp-shade{position:absolute;left:0;right:0;top:0;height:62%;background:linear-gradient(180deg,rgba(0,0,0,.15),rgba(0,0,0,.05) 50%,rgba(13,20,40,.95) 100%)}
.sp-top{justify-content:flex-start;padding:330px 110px 0}
${flip ? `.sp-photo,.sp-shade{top:auto;bottom:0}.sp-shade{background:linear-gradient(0deg,rgba(0,0,0,.15),rgba(0,0,0,.05) 50%,rgba(13,20,40,.95) 100%)}
.sp-top{justify-content:flex-end;padding:0 110px 560px}
.sp-band{top:0!important;bottom:44%!important;padding:230px 90px 30px!important;display:flex;flex-direction:column;justify-content:center;animation-name:banddown!important}
@keyframes banddown{from{transform:translateY(-100%)}to{transform:none}}` : ''}
${LAY.h === 'left' ? '.sp-top{align-items:flex-start;text-align:left}' : ''}
.sp-hook{font-family:'Source Sans 3';font-weight:800;line-height:1.1;color:#fff;text-shadow:0 4px 30px rgba(0,0,0,.6)}.sp-hook .em{color:${LGOLD}}
.sp-band{position:absolute;left:0;right:0;top:56%;bottom:0;background:#0f1730;padding:70px 90px 0}
.sp-row{display:flex;align-items:center;gap:22px}
.sp-k{font-family:'Source Sans 3';font-weight:700;font-size:34px;letter-spacing:.14em;text-transform:uppercase;color:${LGOLD}}
.sp-t{font-family:'Source Sans 3';font-weight:800;line-height:1.02;color:#fff;margin-top:34px}
.sp-t .tw:last-child{color:${LGOLD}}
.sp-line{height:6px;width:260px;background:${LGOLD};margin:26px 0 0;transform-origin:left;animation:grow .6s ease-out both}
.sp-b{font-family:'Source Sans 3';font-weight:600;font-size:40px;line-height:1.35;color:#d9d3c4;margin-top:28px;max-width:860px;animation:up .6s ease-out both}
@keyframes bandup{from{transform:translateY(100%)}to{transform:none}}`;
  return {
    dur: end + 2.6, end, bg: 'none', css, html,
    audio: { key: 87.31, chord: [1, 1.5, 2, 2.52, 3, 3.78], pad: 0.6, bells: [[3.2, 698.46]] },
  };
}
function scripture() {
  const q = spec.quote || spec.body, qn = nWords(q), step = Math.min(0.32, 4.6 / Math.max(qn, 1));
  const refAt = 0.8 + qn * step + 0.4, end = Math.max(8.2, refAt + 2.4);
  const motes = Array.from({ length: 26 }, (_, i) => {
    const x = (i * 37) % 100, d = 6 + (i % 5) * 1.4, del = -((i * 0.73) % d), sz = 4 + (i % 4) * 3;
    return `<i class="mote" style="left:${x}%;width:${sz}px;height:${sz}px;animation-duration:${d}s;animation-delay:${del.toFixed(2)}s"></i>`;
  }).join('');
  const html = `<div class="candle"></div>${motes}
<div ${scene(0.2, end - 0.4, 'scr hk')}>
 <div class="qm">“</div>
 <div class="q" style="font-size:${plain(q).length > 120 ? 68 : plain(q).length > 70 ? 80 : 96}px">${words(q, 'qw', 0.8, step)}</div>
 ${spec.ref ? `<div class="qr" style="animation-delay:${refAt.toFixed(2)}s">${esc(spec.ref)}</div>` : ''}
</div>`;
  const css = `.candle{position:absolute;left:${LAY.h === 'left' ? 36 : 50}%;top:${{ top: 34, bottom: 58 }[LAY.v] || 44}%;width:1400px;height:1400px;margin:-700px 0 0 -700px;border-radius:50%;
 background:radial-gradient(circle,rgba(233,190,110,.30) 0%,rgba(233,190,110,.10) 30%,transparent 62%);animation:flick 1.3s steps(9) infinite}
@keyframes flick{0%{opacity:.85;transform:scale(1)}20%{opacity:1;transform:scale(1.02)}40%{opacity:.8}60%{opacity:.95;transform:scale(.99)}80%{opacity:.88}100%{opacity:.85;transform:scale(1)}}
.mote{position:absolute;bottom:-20px;border-radius:50%;background:${LGOLD};opacity:.0;animation:rise linear infinite}
@keyframes rise{0%{transform:translateY(0);opacity:0}15%{opacity:.6}100%{transform:translateY(-2000px) translateX(60px);opacity:0}}
.scr{padding:280px 110px 560px}
.qm{font-family:'Cormorant Garamond';font-size:260px;line-height:.6;color:${LGOLD};opacity:.8;animation:fade 1s ease-out .3s both}
.q{font-family:'Cormorant Garamond';font-style:italic;font-weight:600;line-height:1.18;color:#f6efe0}
.qw{opacity:0;display:inline-block;animation:glowin .8s ease-out both}.q .em{color:${LGOLD}}
@keyframes glowin{from{opacity:0;filter:blur(8px)}to{opacity:1;filter:none}}
.qr{font-family:'Source Sans 3';font-weight:700;font-size:38px;letter-spacing:.14em;text-transform:uppercase;color:${LGOLD};margin-top:50px;animation:up .8s ease-out both}`;
  return {
    dur: end + 2.6, end, bg: 'dark', css, html,
    audio: { key: 65.41, chord: [1, 1.5, 2, 3], pad: 0.5, drone: true, choir: [[0.8, 261.63], [refAt, 329.63]] },
  };
}

const F = { reveal, kinetic, list, split, scripture }[format]();
const DUR = Math.round(F.dur * 10) / 10, E = F.end;

const FRAMES = { // photo shape at the start (clip-path on the full screen) and its gold edge
  arch: { clip: 'inset(240px 150px 880px 150px round 390px 390px 0px 0px)', edge: 'left:150px;top:240px;width:780px;height:800px;border:5px solid;border-radius:390px 390px 0 0' },
  band: { clip: 'inset(1010px 0px 0px 0px round 0px 0px 0px 0px)', edge: 'left:0;right:0;top:1004px;height:6px;border-top:6px solid' },
  strip: { clip: 'inset(0px 0px 0px 690px round 0px 0px 0px 0px)', edge: 'top:0;bottom:0;left:684px;width:6px;border-left:6px solid' },
};
const FR = LAY.frame && FRAMES[LAY.frame];
const bgLayers = F.bg === 'none' ? '' : F.bg === 'dark'
  ? `<div class="art" style="opacity:.18;animation:pm ${DUR}s linear both"></div>`
  : `<div class="pic"${FR ? ` style="animation:open .9s cubic-bezier(.6,0,.2,1) ${OPEN}s both"` : ''}><div class="art" style="animation:pm ${DUR}s linear both"></div></div>
${FR ? `<div class="edge" style="${FR.edge};border-color:${accent};animation:gone .5s ease-in ${OPEN - 0.1}s forwards"></div>` : ''}
<div class="veil"${FR ? ` style="animation:fade .9s ease-out ${OPEN}s both"` : ''}><div class="ov"></div><div class="rays"></div><div class="glow"></div></div>`;

// The day's look as CSS: word placement, word entrance, highlight, scene change, photo motion, lettering.
const ACC = navy ? LGOLD : GOLD, ACCINK = navy ? NAVY : CREAM;
const pad = LAY.pad || { center: [260, 120, 520, 120], bottom: [260, 120, 560, 110], top: [330, 120, 520, 110] }[LAY.v];
const lookCss = `
:root{--hl:${ACC};--hlink:${ACCINK}}
.sp-top,.sp-band,.scr,.endc{--hl:${LGOLD};--hlink:${NAVY}}
.kin.alt{--hl:#fff;--hlink:${NAVY}}
${FR ? `.pic{clip-path:${FR.clip}}@keyframes open{to{clip-path:inset(0px 0px 0px 0px round 0px 0px 0px 0px)}}` : ''}
.pic{position:absolute;inset:0;overflow:hidden}.veil{position:absolute;inset:0}.edge{position:absolute;box-sizing:border-box;opacity:.9}
.scene.hk{padding:${pad.map((n) => n + 'px').join(' ')};justify-content:${{ top: 'flex-start', bottom: 'flex-end' }[LAY.v] || 'center'};
 align-items:${LAY.h === 'left' ? 'flex-start' : 'center'};text-align:${LAY.h}}
${LAY.h === 'left' ? `.scene.cd{align-items:flex-start;text-align:left}.cd .mk{margin-left:0}.cd .rule{margin-left:0;transform-origin:left}.lst .lh{text-align:left}` : ''}
.hook,.sp-hook,.lh{${{ serif: "font-family:'Cormorant Garamond';font-weight:700;line-height:1.02", caps: 'text-transform:uppercase;letter-spacing:.04em;line-height:1.08' }[LOOK.type] || ''}}
@keyframes wordin{from{opacity:0;${{ pop: 'transform:translateY(40px) scale(.85)', rise: 'transform:translateY(70px)', slide: 'transform:translateX(-90px)',
  drop: 'transform:translateY(-80px)', blur: 'filter:blur(14px);transform:scale(1.06)', zoom: 'transform:scale(2.2)' }[LOOK.words]}}to{opacity:1;transform:none;filter:none}}
.hw,.tw,.kw,.qw{animation-name:wordin!important;animation-timing-function:${{ pop: 'cubic-bezier(.2,1.4,.4,1)', zoom: 'cubic-bezier(.2,.9,.3,1)', drop: 'cubic-bezier(.3,1.5,.5,1)' }[LOOK.words] || 'ease-out'}!important}
.hw.em,.tw.em,.kw.em,.qw.em{animation-name:wordin,hl!important;animation-duration:.55s,1.1s!important;animation-fill-mode:both!important}
.em0.em{animation:hl 1.1s ease-out both}
.em{${{
  gold: 'color:var(--hl)!important',
  marker: 'color:var(--hlink)!important;text-shadow:none!important;background:linear-gradient(var(--hl),var(--hl)) no-repeat 0 50%/100% 100%;padding:0 .14em;margin:0 -.04em;border-radius:.12em;-webkit-box-decoration-break:clone',
  underline: 'color:var(--hl)!important;background:linear-gradient(var(--hl),var(--hl)) no-repeat 0 96%/100% .1em;padding-bottom:.04em',
  box: 'color:var(--hl)!important;box-shadow:inset 0 0 0 .055em var(--hl);border-radius:.18em;padding:0 .14em',
  glow: 'color:var(--hl)!important;text-shadow:0 0 .25em var(--hl),0 0 .6em var(--hl)!important',
  serif: "color:var(--hl)!important;font-family:'Cormorant Garamond'!important;font-style:italic;font-weight:700;font-size:1.1em;letter-spacing:0;text-transform:none",
}[LOOK.highlight]}}
@keyframes hl{${{
  marker: 'from{background-size:0% 100%}to{background-size:100% 100%}',
  underline: 'from{background-size:0% .1em}to{background-size:100% .1em}',
  box: 'from{box-shadow:inset 0 0 0 0 var(--hl)}to{box-shadow:inset 0 0 0 .055em var(--hl)}',
  glow: '0%{text-shadow:none}60%{text-shadow:0 0 .4em var(--hl),0 0 .9em var(--hl)}100%{text-shadow:0 0 .25em var(--hl),0 0 .6em var(--hl)}',
}[LOOK.highlight] || 'from{opacity:.999}to{opacity:1}'}}
@keyframes fin{${{
  'fade-up': 'from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}',
  slide: 'from{opacity:0;transform:translateX(55%)}to{opacity:1;transform:none}',
  zoom: 'from{opacity:0;transform:scale(.82)}to{opacity:1;transform:none}',
  wipe: 'from{opacity:1;clip-path:inset(0 100% 0 0)}to{opacity:1;clip-path:inset(0 0 0 0)}',
  blur: 'from{opacity:0;filter:blur(22px)}to{opacity:1;filter:none}',
}[LOOK.scene]}}
@keyframes fout{${{
  'fade-up': 'from{opacity:1;transform:none}to{opacity:0;transform:translateY(-40px)}',
  slide: 'from{opacity:1;transform:none}to{opacity:0;transform:translateX(-55%)}',
  zoom: 'from{opacity:1;transform:none}to{opacity:0;transform:scale(1.18)}',
  wipe: 'from{opacity:1;clip-path:inset(0 0 0 0)}to{opacity:1;clip-path:inset(0 0 0 100%)}',
  blur: 'from{opacity:1;filter:none}to{opacity:0;filter:blur(22px)}',
}[LOOK.scene]}}
@keyframes pm{${{
  'zoom-in': 'from{transform:scale(1.04)}to{transform:scale(1.24)}',
  'zoom-out': 'from{transform:scale(1.28)}to{transform:scale(1.04)}',
  'pan-left': 'from{transform:scale(1.28) translateX(7%)}to{transform:scale(1.28) translateX(-7%)}',
  'pan-right': 'from{transform:scale(1.28) translateX(-7%)}to{transform:scale(1.28) translateX(7%)}',
  'tilt-up': 'from{transform:scale(1.28) translateY(7%)}to{transform:scale(1.28) translateY(-7%)}',
  'tilt-down': 'from{transform:scale(1.28) translateY(-7%)}to{transform:scale(1.28) translateY(7%)}',
  drift: 'from{transform:scale(1.14) translate(-3%,3%)}to{transform:scale(1.26) translate(3%,-3%)}',
  turn: 'from{transform:scale(1.34) rotate(-5deg)}to{transform:scale(1.2) rotate(4deg)}',
}[LOOK.photo]}}
@keyframes gone{to{opacity:0}}
.clogo{position:absolute;z-index:5;display:flex;align-items:center;gap:14px;padding:12px 26px 12px 18px;border-radius:999px;
 background:${navy ? 'rgba(15,23,48,.62)' : 'rgba(250,246,238,.78)'};box-shadow:0 6px 24px rgba(0,0,0,.18);opacity:0;
 animation:fade .6s ease-out .4s both, gone .4s ease-in ${(E - 0.45).toFixed(2)}s forwards}
.clogo .lm{width:${48 / 1.18}px;height:48px}
.clogo .lw{font-family:'Cormorant Garamond';font-weight:700;font-size:40px;line-height:1;color:${navy ? CREAM : NAVY}}.clogo .lw span{color:${ACC}}
.c-top-left{top:160px;left:56px}.c-top-right{top:160px;right:56px}.c-bottom-left{bottom:430px;left:56px}.c-bottom-right{bottom:430px;right:170px}`;
const cornerLogo = `<div class="clogo c-${LOOK.corner}"><div class="lm">${mark(ACC, ACC, 0.14)}</div><div class="lw">Catholic<span>Doorway</span></div></div>`;

const html = `<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=Source+Sans+3:wght@600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<style>
html,body{margin:0;width:${W}px;height:${H}px;overflow:hidden;background:${F.bg === 'dark' ? '#0b0f1c' : navy ? NAVY : CREAM}}*{box-sizing:border-box}
.art{position:absolute;inset:-4%;background:${artUrl ? `url(${artUrl}) center/cover` : 'none'}}
@keyframes kb{from{transform:scale(1.04) translate(0,0)}to{transform:scale(1.2) translate(-2%,-3%)}}
@keyframes pan{from{transform:scale(1.25) translateX(6%)}to{transform:scale(1.25) translateX(-6%)}}
.ov{position:absolute;inset:0;background:${overlay}}
.glow{position:absolute;left:50%;top:38%;width:1500px;height:1500px;margin:-750px 0 0 -750px;border-radius:50%;
 background:radial-gradient(circle,${navy ? 'rgba(233,207,142,.22)' : 'rgba(168,128,47,.16)'} 0%,rgba(0,0,0,0) 60%);animation:gl ${DUR}s ease-in-out both}
@keyframes gl{0%{opacity:.3;transform:scale(.8)}50%{opacity:1;transform:scale(1.05)}100%{opacity:.6;transform:scale(1.15)}}
.rays{position:absolute;left:50%;top:-10%;width:1800px;height:1800px;margin-left:-900px;opacity:.12;
 background:repeating-conic-gradient(from 0deg,${navy ? LGOLD : GOLD} 0deg 2deg,transparent 2deg 15deg);
 -webkit-mask:radial-gradient(circle,#000 0%,transparent 65%);animation:rot ${DUR}s linear both}
@keyframes rot{from{transform:rotate(-6deg)}to{transform:rotate(8deg)}}
.scene{position:absolute;left:0;right:0;top:0;bottom:0;padding:260px 120px 520px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;opacity:0;overflow:hidden}
@keyframes fin{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:none}}
@keyframes fout{from{opacity:1;transform:none}to{opacity:0;transform:translateY(-40px)}}
.hw{display:inline-block;opacity:0;animation:pop .45s cubic-bezier(.2,1.4,.4,1) both}
@keyframes pop{from{opacity:0;transform:translateY(40px) scale(.85)}to{opacity:1;transform:none}}
.hook{font-family:'Source Sans 3';font-weight:800;line-height:1.12;color:${ink};text-shadow:0 4px 30px rgba(0,0,0,${navy ? '.45' : '.08'})}
.hook .em{color:${accent}}
.mk{width:${110 / 1.18}px;height:110px;margin:0 auto 46px;animation:fade .8s ease-out both}
.k{font-family:'Source Sans 3';font-weight:700;font-size:36px;letter-spacing:.16em;text-transform:uppercase;color:${accent};animation:up .6s ease-out both}
.rule{width:150px;height:3px;background:${accent};opacity:.7;margin:36px auto;transform-origin:center;animation:grow .7s ease-out both}
.t{font-family:'Cormorant Garamond';font-weight:700;line-height:1.04;color:${ink}}
.tw{display:inline-block;opacity:0;animation:up .6s ease-out both}
.b{font-family:'Source Serif 4';font-size:52px;line-height:1.42;color:${ink};margin-top:48px;opacity:.95}
.bw{opacity:0;animation:fade .35s ease-out both}
.r{font-family:'Cormorant Garamond';font-style:italic;font-size:46px;color:${accent};margin-top:36px;animation:up .7s ease-out both}
@keyframes up{from{opacity:0;transform:translateY(34px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.endc{background:${F.bg === 'dark' ? 'rgba(11,15,28,.0)' : 'transparent'}}
.endc.solid{background:${navy || F.bg === 'dark' ? NAVY : CREAM}}
.wm{font-family:'Cormorant Garamond';font-weight:700;font-size:104px;color:${F.bg === 'dark' ? CREAM : ink};line-height:1}
.url{font-family:'Source Sans 3';font-weight:700;font-size:48px;letter-spacing:.04em;color:${F.bg === 'dark' ? CREAM : ink};margin-top:40px;padding:18px 40px;border:3px solid ${F.bg === 'dark' ? LGOLD : accent};border-radius:999px}
.url b{color:${F.bg === 'dark' ? LGOLD : accent}}
.free{font-family:'Source Serif 4';font-size:40px;color:${F.bg === 'dark' ? CREAM : ink};opacity:.85;margin-top:36px}
${F.css}
${lookCss}
</style></head><body>
${bgLayers}
${F.html}
${cornerLogo}
<div ${scene(E, 0, 'endc' + (F.bg === 'none' ? ' solid' : ''))}>
 <div class="mk" style="animation-delay:${(E + 0.1).toFixed(2)}s;width:${150 / 1.18}px;height:150px">${mark(F.bg === 'dark' ? LGOLD : accent, F.bg === 'dark' ? LGOLD : accent, 0.14)}</div>
 <div class="wm">Catholic<span style="color:${F.bg === 'dark' ? LGOLD : accent}">Doorway</span></div>
 <div class="url">catholicdoorway.com<b>${esc(spec.path || '')}</b></div>
 <div class="free">Free. No sign-up. Come on in.</div>
</div>
</body></html>`;

// Original audio, different per format; every video ends with the same two-note closing bell.
function makeAudio(wav) {
  const cfg = Object.assign({ dur: DUR, end: E }, F.audio);
  const py = `
import numpy as np, wave, sys, json
c=json.loads(sys.argv[2]); sr=44100; dur=c['dur']; t=np.arange(int(sr*dur))/sr
def env(a,r): return np.minimum(1,t/a)*np.clip((dur-t)/r,0,1)
def bellat(sig,start,f0,g=1.0,dk=1.0):
    tt=t-start; m=tt>=0; x=tt[m]
    for k,gg,dc in [(1,.6,1.6),(2.76,.25,2.6),(5.4,.12,4.0),(2,.18,2.0)]:
        sig[m]+=g*gg*np.sin(2*np.pi*f0*k*x)*np.exp(-x*dc*dk)*np.minimum(1,x/0.004)
pad=np.zeros_like(t)
for i,r in enumerate(c['chord']):
    f=c['key']*r; g=0.5/(1+i*0.35)
    for d in (-.6,.6): pad+=g*np.sin(2*np.pi*(f+d)*t)
pad*=(0.8+0.2*np.sin(2*np.pi*0.18*t))*env(1.8 if c.get('bpm') else 2.5,2.0)
mix=c.get('pad',.5)*pad/np.max(np.abs(pad))
fx=np.zeros_like(t)
for s,f in c.get('bells',[]): bellat(fx,s,f,.8)
for s,f in c.get('chimes',[]): bellat(fx,s,f,.7,1.6)
for s,f in c.get('plucks',[]):
    tt=t-s; m=tt>=0; x=tt[m]
    fx[m]+=.7*(np.sin(2*np.pi*f*x)+.3*np.sin(2*np.pi*2*f*x))*np.exp(-x*7)*np.minimum(1,x/0.003)
if c.get('bpm'):
    beat=60/c['bpm']; k=np.zeros_like(t)
    for s in np.arange(0.2,c['pulseEnd'],beat):
        tt=t-s; m=(tt>=0)&(tt<0.35); x=tt[m]
        k[m]+=np.sin(2*np.pi*(55+70*np.exp(-x*30))*x)*np.exp(-x*9)
    fx+=.9*k
if c.get('drone'):
    d=np.sin(2*np.pi*c['key']*t)+.5*np.sin(2*np.pi*c['key']*1.5*t)
    mix+=.25*d*env(3,2.5)
for s,f in c.get('choir',[]):
    tt=t-s; m=tt>=0; x=tt[m]; v=f*(1+0.006*np.sin(2*np.pi*5*x))
    ph=2*np.pi*np.cumsum(v)/sr
    fx[m]+=.35*(np.sin(ph)+.5*np.sin(2*ph)+.25*np.sin(3*ph))*np.minimum(1,x/1.2)*np.exp(-x*.25)
bellat(fx,c['end'],739.99,1.0); bellat(fx,c['end']+0.3,1174.66,.9)
sig=mix+.45*fx/max(1e-9,np.max(np.abs(fx)))
for dly,g in [(0.11,.25),(0.23,.15),(0.37,.09)]:
    n=int(sr*dly); sig[n:]+=g*sig[:-n]
sig=sig/np.max(np.abs(sig))*0.7
st=(np.stack([sig,np.roll(sig,int(sr*0.012))],1)*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes()); w.close()
`;
  execFileSync('python3', ['-c', py, wav, JSON.stringify(cfg)]);
}

(async () => {
  const wav = out.replace(/\.mp4$/, '') + '.wav';
  makeAudio(wav);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.setContent(html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', wav,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const frames = Math.round(DUR * FPS);
  for (let i = 0; i < frames; i++) {
    const ms = (i / FPS) * 1000;
    await p.evaluate((ms) => { document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }); }, ms);
    const buf = await p.screenshot({ type: 'jpeg', quality: 88 });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r, j) => ff.on('close', (c) => (c ? j(new Error('ffmpeg ' + c)) : r())));
  await b.close();
  fs.unlinkSync(wav);
  console.log(format, DUR + 's', 'look', JSON.stringify(LOOK));
})().catch((e) => { console.error(e); process.exit(1); });
