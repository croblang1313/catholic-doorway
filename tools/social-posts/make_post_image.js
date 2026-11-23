// Renders one Catholic Doorway social image (1080x1350 JPEG, Instagram 4:5) with Playwright.
// Usage: node make_post_image.js spec.json out.jpg [--wide]
// --wide renders the same design at 1200x630, the size Facebook, X and WhatsApp use for link
// previews. send_drafts.py makes one for each "This Week in the Church" article (its share picture).
// spec: {"kicker":"Monday · Saint of the Day","title":"St. Cecilia","body":"Short text...",
//        "ref":"Nov 22 · Feast", "theme":"cream"|"navy"}
const { chromium } = require('playwright');
const fs = require('fs');
const esc = (s) => String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const NAVY = '#1d2b4f', GOLD = '#a8802f', CREAM = '#faf6ee', LGOLD = '#e9cf8e';
const mark = (line, gold, op) => `<svg viewBox="0 0 34 40" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%;display:block"><path d="M3 39V17C3 8.7 9.3 2 17 2s14 6.7 14 15v22" fill="none" stroke="${line}" stroke-width="2.4"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="${line}" opacity="${op}"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="none" stroke="${line}" stroke-width="1.6"/><path d="M17 12v9M13.6 15.2h6.8" stroke="${gold}" stroke-width="2" stroke-linecap="round"/><circle cx="22" cy="28" r="1.4" fill="${gold}"/><path d="M1 39h32" stroke="${line}" stroke-width="2.4" stroke-linecap="round"/></svg>`;
const spec = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const navy = spec.theme === 'navy';
const ink = navy ? CREAM : NAVY, accent = navy ? LGOLD : GOLD, soft = navy ? '#cfc8b8' : '#4a5060';
const bg = navy ? 'radial-gradient(circle at 50% 30%, #26386a 0%, #1d2b4f 55%, #131d38 100%)'
  : 'linear-gradient(180deg,#ecdfc4 0%,#f4ecdc 35%,#faf6ee 100%)';
const wide = process.argv.includes('--wide');
const W = wide ? 1200 : 1080, H = wide ? 630 : 1350;
const title = esc(spec.title);
const tsize = wide ? (title.length > 40 ? 64 : title.length > 24 ? 76 : 88) : (title.length > 40 ? 84 : title.length > 24 ? 100 : 118);
// The body line only fits the wide card when it is short.
const body = wide && String(spec.body || '').length > 130 ? '' : spec.body;
const Z = wide ? { pad: '44px 90px 40px', k: 22, rule: '18px auto', b: 28, bm: 20, r: 28, rm: 14, mark: 54, markm: 18, wm: 34, url: 17, urlm: 6, mainpb: 10 }
  : { pad: '90px 100px 100px', k: 30, rule: '34px auto', b: 40, bm: 44, r: 38, rm: 30, mark: 86, markm: 40, wm: 52, url: 26, urlm: 14, mainpb: 40 };
const html = `<!doctype html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Source+Sans+3:wght@600;700&family=Source+Serif+4:opsz,wght@8..60,400&display=swap" rel="stylesheet">
<style>html,body{margin:0;width:${W}px;height:${H}px;overflow:hidden;background:${bg}}*{box-sizing:border-box}
.wrap{position:absolute;inset:0;padding:${Z.pad};display:flex;flex-direction:column;align-items:center;text-align:center}
.k{font-family:'Source Sans 3';font-weight:700;font-size:${Z.k}px;letter-spacing:.16em;text-transform:uppercase;color:${accent}}
.rule{width:120px;height:2px;background:${accent};opacity:.6;margin:${Z.rule}}
.t{font-family:'Cormorant Garamond';font-weight:600;font-size:${tsize}px;line-height:1.05;color:${ink}}
.b{font-family:'Source Serif 4';font-size:${Z.b}px;line-height:1.45;color:${ink};margin-top:${Z.bm}px;opacity:.92}
.r{font-family:'Cormorant Garamond';font-style:italic;font-size:${Z.r}px;color:${accent};margin-top:${Z.rm}px}
.main{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:${Z.mainpb}px}
.foot{display:flex;align-items:center;gap:20px}
.wm{font-family:'Cormorant Garamond';font-weight:600;font-size:${Z.wm}px;color:${ink}}
.url{font-family:'Source Sans 3';font-weight:600;font-size:${Z.url}px;letter-spacing:.12em;color:${soft};margin-top:${Z.urlm}px}
</style></head><body><div class="wrap">
<div class="main"><div style="width:${Z.mark / 1.18}px;height:${Z.mark}px;margin:0 auto ${Z.markm}px">${mark(accent, accent, 0.14)}</div>
<div class="k">${esc(spec.kicker)}</div><div class="rule"></div>
<div class="t">${title}</div>
${body ? `<div class="b">${esc(body)}</div>` : ''}
${spec.ref ? `<div class="r">${esc(spec.ref)}</div>` : ''}</div>
<div class="foot" style="flex-direction:column;gap:0"><div class="wm">Catholic<span style="color:${accent}">Doorway</span></div>
<div class="url">CATHOLICDOORWAY.COM</div></div>
</div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: W, height: H } });
  await p.setContent(html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.screenshot({ path: process.argv[3], type: 'jpeg', quality: 90 });
  await b.close();
})();
