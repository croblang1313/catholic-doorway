// Renders one Catholic Doorway TikTok/Reels video (1080x1920 MP4, 30 fps, ~11 s, with original audio).
// Usage: node make_post_video.js spec.json out.mp4
// spec: the same image spec as make_post_image.js plus
//   "hook": "Big on-screen line for the first 3 seconds (under ~70 characters; *word* = gold)",
//   "path": "/saints"          (page shown on the end card; optional)
//   "art":  "window" | "none"   (background photo; default window. The window photo is public domain/CC0.
//            Don't add the nave photo here: it is CC BY-SA and would need a credit on every video.)
// Scenes: 0-3 s hook (word by word) · 3-8.5 s the post card (kicker, title, body, ref) · 8.5-11 s end card.
// Motion: slow Ken Burns zoom over the background, drifting light, staggered text.
// Sound: an original ambient chord with soft bell chimes on each scene change, made here with numpy
// (no third-party music, so nothing to license). Text stays clear of TikTok's bottom and right UI.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { spawn, execFileSync } = require('child_process');

const W = 1080, H = 1920, FPS = 30, DUR = 11;
const esc = (s) => String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NAVY = '#1d2b4f', GOLD = '#a8802f', CREAM = '#faf6ee', LGOLD = '#e9cf8e';
const mark = (line, gold, op) => `<svg viewBox="0 0 34 40" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block"><path d="M3 39V17C3 8.7 9.3 2 17 2s14 6.7 14 15v22" fill="none" stroke="${line}" stroke-width="2.4"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="${line}" opacity="${op}"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="none" stroke="${line}" stroke-width="1.6"/><path d="M17 12v9M13.6 15.2h6.8" stroke="${gold}" stroke-width="2" stroke-linecap="round"/><circle cx="22" cy="28" r="1.4" fill="${gold}"/><path d="M1 39h32" stroke="${line}" stroke-width="2.4" stroke-linecap="round"/></svg>`;

const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const out = process.argv[3];
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
const hook = spec.hook || spec.title;  // may use *word* for gold emphasis
const hookN = hook.split(/\s+/).length;
const hlen = hook.replace(/\*/g, '').length;
const hsize = hlen > 55 ? 86 : hlen > 34 ? 100 : 118;
const title = spec.title || '';
const tsize = title.length > 40 ? 92 : title.length > 24 ? 108 : 128;
const bodyN = (spec.body || '').split(/\s+/).length;
const bodyStep = Math.min(0.07, 2.0 / Math.max(bodyN, 1));

const html = `<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Source+Sans+3:wght@600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
<style>
html,body{margin:0;width:${W}px;height:${H}px;overflow:hidden;background:${navy ? NAVY : CREAM}}*{box-sizing:border-box}
.art{position:absolute;inset:-4%;background:${artUrl ? `url(${artUrl}) center/cover` : 'none'};animation:kb ${DUR}s linear both}
@keyframes kb{from{transform:scale(1.04) translate(0,0)}to{transform:scale(1.2) translate(-2%,-3%)}}
.ov{position:absolute;inset:0;background:${overlay}}
.glow{position:absolute;left:50%;top:38%;width:1500px;height:1500px;margin:-750px 0 0 -750px;border-radius:50%;
 background:radial-gradient(circle,${navy ? 'rgba(233,207,142,.22)' : 'rgba(168,128,47,.16)'} 0%,rgba(0,0,0,0) 60%);animation:gl ${DUR}s ease-in-out both}
@keyframes gl{0%{opacity:.3;transform:scale(.8)}50%{opacity:1;transform:scale(1.05)}100%{opacity:.6;transform:scale(1.15)}}
.rays{position:absolute;left:50%;top:-10%;width:1800px;height:1800px;margin-left:-900px;opacity:.12;
 background:repeating-conic-gradient(from 0deg,${navy ? LGOLD : GOLD} 0deg 2deg,transparent 2deg 15deg);
 -webkit-mask:radial-gradient(circle,#000 0%,transparent 65%);animation:rot ${DUR}s linear both}
@keyframes rot{from{transform:rotate(-6deg)}to{transform:rotate(8deg)}}
.scene{position:absolute;left:0;right:0;top:0;bottom:0;padding:260px 120px 520px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;opacity:0}
.s1{animation:sc1 ${DUR}s linear both}
@keyframes sc1{0%{opacity:1}26%{opacity:1;transform:none}29%{opacity:0;transform:translateY(-60px)}100%{opacity:0}}
.s2{animation:sc2 ${DUR}s linear both}
@keyframes sc2{0%,26%{opacity:0;transform:translateY(40px)}30%{opacity:1;transform:none}75%{opacity:1;transform:none}78%{opacity:0;transform:scale(.96)}100%{opacity:0}}
.s3{animation:sc3 ${DUR}s linear both}
@keyframes sc3{0%,78%{opacity:0;transform:scale(1.04)}81%{opacity:1;transform:none}100%{opacity:1}}
.hw{display:inline-block;opacity:0;animation:pop .45s cubic-bezier(.2,1.4,.4,1) both}
@keyframes pop{from{opacity:0;transform:translateY(40px) scale(.85)}to{opacity:1;transform:none}}
.hook{font-family:'Source Sans 3';font-weight:800;font-size:${hsize}px;line-height:1.12;color:${ink};text-shadow:0 4px 30px rgba(0,0,0,${navy ? '.45' : '.08'})}
.hook .em{color:${accent}}
.mk{width:${110 / 1.18}px;height:110px;margin:0 auto 46px;animation:fade .8s ease-out both}
.k{font-family:'Source Sans 3';font-weight:700;font-size:36px;letter-spacing:.16em;text-transform:uppercase;color:${accent};animation:up .6s ease-out both}
.rule{width:150px;height:3px;background:${accent};opacity:.7;margin:36px auto;transform-origin:center;animation:grow .7s ease-out both}
.t{font-family:'Cormorant Garamond';font-weight:700;font-size:${tsize}px;line-height:1.04;color:${ink}}
.tw{display:inline-block;opacity:0;animation:up .6s ease-out both}
.b{font-family:'Source Serif 4';font-size:52px;line-height:1.42;color:${ink};margin-top:48px;opacity:.95}
.bw{opacity:0;animation:fade .35s ease-out both}
.r{font-family:'Cormorant Garamond';font-style:italic;font-size:46px;color:${accent};margin-top:36px;animation:up .7s ease-out both}
@keyframes up{from{opacity:0;transform:translateY(34px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}
.wm{font-family:'Cormorant Garamond';font-weight:700;font-size:104px;color:${ink};line-height:1}
.url{font-family:'Source Sans 3';font-weight:700;font-size:48px;letter-spacing:.04em;color:${ink};margin-top:40px;padding:18px 40px;border:3px solid ${accent};border-radius:999px}
.url b{color:${accent}}
.free{font-family:'Source Serif 4';font-size:40px;color:${ink};opacity:.85;margin-top:36px}
</style></head><body>
<div class="art"></div><div class="ov"></div><div class="rays"></div><div class="glow"></div>
<div class="scene s1"><div class="hook">${words(hook, 'hw', 0.25, Math.min(0.22, 1.6 / Math.max(hookN, 1)))}</div></div>
<div class="scene s2">
 <div class="mk" style="animation-delay:3.2s">${mark(accent, accent, 0.14)}</div>
 <div class="k" style="animation-delay:3.4s">${esc(spec.kicker)}</div>
 <div class="rule" style="animation-delay:3.6s"></div>
 <div class="t">${words(title, 'tw', 3.8, 0.14)}</div>
 ${spec.body ? `<div class="b">${words(spec.body, 'bw', 4.7, bodyStep)}</div>` : ''}
 ${spec.ref ? `<div class="r" style="animation-delay:${(4.9 + bodyN * bodyStep).toFixed(2)}s">${esc(spec.ref)}</div>` : ''}
</div>
<div class="scene s3">
 <div class="mk" style="animation-delay:8.6s;width:${150 / 1.18}px;height:150px">${mark(accent, accent, 0.14)}</div>
 <div class="wm">Catholic<span style="color:${accent}">Doorway</span></div>
 <div class="url">catholicdoorway.com<b>${esc(spec.path || '')}</b></div>
 <div class="free">Free. No sign-up. Come on in.</div>
</div>
</body></html>`;

// Original audio: a soft D-major pad plus bell chimes at 0.25 s, 3.8 s and 8.6 s.
function makeAudio(wav) {
  const py = `
import numpy as np, wave, sys
sr=44100; dur=${DUR}; t=np.arange(int(sr*dur))/sr
def env(a,r): e=np.minimum(1,t/a); return e*np.minimum(1,(dur-t)/r)
pad=np.zeros_like(t)
for f,g in [(73.42,.5),(110,.35),(146.83,.4),(185,.22),(220,.25),(329.63,.12)]:
    for d in (-.6,.6): pad+=g*np.sin(2*np.pi*(f+d)*t)
pad*= (0.8+0.2*np.sin(2*np.pi*0.18*t))*env(2.5,2.0)
bell=np.zeros_like(t)
for start,f0 in [(0.25,587.33),(3.8,880),(8.6,739.99),(8.9,1174.66)]:
    tt=t-start; m=tt>=0; x=tt[m]
    for k,g,dc in [(1,.6,1.6),(2.76,.25,2.6),(5.4,.12,4.0),(2,.18,2.0)]:
        bell[m]+=g*np.sin(2*np.pi*f0*k*x)*np.exp(-x*dc)*np.minimum(1,x/0.004)
sig=0.55*pad/np.max(np.abs(pad))+0.35*bell/np.max(np.abs(bell))
# soft room: a few quiet echoes
for dly,g in [(0.11,.25),(0.23,.15),(0.37,.09)]:
    n=int(sr*dly); sig[n:]+=g*sig[:-n]
sig=sig/np.max(np.abs(sig))*0.7
l=sig; r=np.roll(sig,int(sr*0.012))
st=(np.stack([l,r],1)*32767).astype(np.int16)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(st.tobytes()); w.close()
`;
  execFileSync('python3', ['-c', py, wav]);
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
  const frames = DUR * FPS;
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
})().catch((e) => { console.error(e); process.exit(1); });
