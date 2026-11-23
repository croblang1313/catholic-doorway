// Makes the downloadable PDF of a "This Week in the Church" article with Playwright.
// Usage: node make_article_pdf.js article.json out.pdf
// post_article.py runs this and sends the PDF with the draft, so the article page's
// "Download PDF" button hands readers a clean, printable copy (US Letter, page numbers).
const { chromium } = require('playwright');
const fs = require('fs');

const a = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const SITE = 'https://catholicdoorway.com';
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const url = `${SITE}/this-week/${a.slug}`;
// Site-relative links in the body become full addresses, so they still work on paper and offline.
const body = String(a.body || '')
  .replace(/<(script|style|iframe)[\s\S]*?<\/\1>/gi, '')
  .replace(/href="\/(?!\/)/g, `href="${SITE}/`);
const related = (a.related || []).filter((r) => r && r.href && r.label);
const sources = (a.sources || []).filter((s) => s && s.label);
const NAVY = '#1d2b4f', GOLD = '#a8802f';
const mark = `<svg viewBox="0 0 34 40" width="26" height="31" xmlns="http://www.w3.org/2000/svg"><path d="M3 39V17C3 8.7 9.3 2 17 2s14 6.7 14 15v22" fill="none" stroke="${GOLD}" stroke-width="2.4"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="${GOLD}" opacity=".14"/><path d="M8 39V18.5C8 13 12 8.5 17 8.5S26 13 26 18.5V39" fill="none" stroke="${GOLD}" stroke-width="1.6"/><path d="M17 12v9M13.6 15.2h6.8" stroke="${GOLD}" stroke-width="2" stroke-linecap="round"/><circle cx="22" cy="28" r="1.4" fill="${GOLD}"/><path d="M1 39h32" stroke="${GOLD}" stroke-width="2.4" stroke-linecap="round"/></svg>`;

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;1,500&family=Source+Sans+3:wght@600;700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap" rel="stylesheet">
<style>
@page { size: Letter; margin: 0.8in 0.85in 0.85in; }
body { margin: 0; font-family: 'Source Serif 4', Georgia, serif; font-size: 11.5pt; line-height: 1.55; color: #222; }
a { color: ${NAVY}; }
.top { display: flex; align-items: center; gap: 10px; border-bottom: 1.5px solid ${GOLD}; padding-bottom: 10px; margin-bottom: 22px; }
.wm { font-family: 'Cormorant Garamond'; font-weight: 600; font-size: 20pt; color: ${NAVY}; }
.wm span { color: ${GOLD}; }
.series { margin-left: auto; font-family: 'Source Sans 3'; font-weight: 700; font-size: 8.5pt; letter-spacing: .14em; text-transform: uppercase; color: ${GOLD}; }
.kicker { font-family: 'Source Sans 3'; font-weight: 700; font-size: 9pt; letter-spacing: .12em; text-transform: uppercase; color: ${GOLD}; margin: 0 0 6px; }
h1 { font-family: 'Cormorant Garamond'; font-weight: 600; font-size: 30pt; line-height: 1.05; color: ${NAVY}; margin: 0 0 10px; }
.lede { font-size: 13pt; color: #444; margin: 0 0 18px; }
.verse { font-style: italic; color: #444; border-left: 3px solid ${GOLD}; padding: 2px 0 2px 12px; margin: 0 0 20px; }
.verse b { font-style: normal; font-weight: 600; font-size: 10pt; color: ${GOLD}; }
h2 { font-family: 'Cormorant Garamond'; font-weight: 600; font-size: 18pt; color: ${NAVY}; margin: 22px 0 6px; break-after: avoid; }
h3 { font-size: 12.5pt; color: ${NAVY}; margin: 16px 0 4px; break-after: avoid; }
p, li { orphans: 3; widows: 3; }
blockquote { margin: 14px 0; padding: 6px 14px; border-left: 3px solid ${GOLD}; background: #f6f1e6; break-inside: avoid; }
blockquote p { margin: 4px 0; }
cite { display: block; font-style: normal; font-size: 9.5pt; color: #666; }
.box { margin-top: 24px; padding-top: 10px; border-top: 1px solid #ddd3bd; font-size: 10pt; break-inside: avoid; }
.box h2 { font-size: 14pt; margin: 0 0 4px; }
.box ul { margin: 4px 0; padding-left: 18px; }
.end { margin-top: 26px; font-size: 9pt; color: #666; border-top: 1px solid #ddd3bd; padding-top: 10px; }
</style></head><body>
<div class="top">${mark}<div class="wm">Catholic<span>Doorway</span></div><div class="series">This Week in the Church</div></div>
${a.kicker ? `<p class="kicker">${esc(a.kicker)}</p>` : ''}
<h1>${esc(a.title)}</h1>
<p class="lede">${esc(a.description)}</p>
${a.verse && a.verse.t ? `<p class="verse">&ldquo;${esc(a.verse.t)}&rdquo; <b>${esc(a.verse.r)} &middot; RSV-CE</b></p>` : ''}
<div class="body">${body}</div>
${related.length ? `<div class="box"><h2>Keep going</h2><ul>${related.map((r) => `<li><a href="${esc(SITE + r.href)}">${esc(r.label)}</a>${r.note ? `: ${esc(r.note)}` : ''} <span style="color:#777">(catholicdoorway.com${esc(r.href)})</span></li>`).join('')}</ul></div>` : ''}
${sources.length ? `<div class="box"><h2>Sources</h2><ul>${sources.map((s) => `<li>${s.href ? `<a href="${esc(s.href)}">${esc(s.label)}</a>` : esc(s.label)}</li>`).join('')}</ul></div>` : ''}
<p class="end">Read it online and find more at <a href="${url}">${url.replace('https://', '')}</a>. Free to print and share for personal, parish and classroom use. Scripture quotations are from the Revised Standard Version of the Bible, Second Catholic Edition &copy; 2006 National Council of the Churches of Christ in the USA. Used by permission. All rights reserved. Spot a mistake? Write to hello@catholicdoorway.com.</p>
</body></html>`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.setContent(html, { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({
    path: process.argv[3], format: 'Letter', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<div></div>',
    footerTemplate: `<div style="width:100%;font:8px sans-serif;color:#888;padding:0 0.85in;display:flex;justify-content:space-between"><span>catholicdoorway.com/this-week/${esc(a.slug)}</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>`,
  });
  await b.close();
})();
