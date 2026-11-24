// Day-by-day "looks" for the Catholic Doorway TikTok videos, so no two days look alike.
// A look picks, for one calendar date:
//   corner     where the small Catholic Doorway logo sits while the video plays
//   layout     where the picture and the words go (full photo, arched window, photo strip, photo band...)
//   photo      how the picture moves (zoom in/out, pan, tilt, drift, turn)
//   words      how the words come in (pop, rise, slide, drop, blur, zoom)
//   highlight  how the *gold* words are marked (gold text, marker, underline, outline box, glow, serif italic)
//   scene      how one screen hands over to the next (fade up, slide, zoom, wipe, blur)
//   type       the hook lettering (bold sans, serif, spaced capitals)
//
// It is deterministic: the same date always gives the same look, on any computer, with no saved state.
// Every calendar day from EPOCH is worked out in order, and each choice avoids what the last few days used:
//   corner     never the same as any of the 3 days before (so Mon/Wed/Fri and Fri->Mon always change)
//   layout     not used in the 4 days before        photo   not used in the 5 days before
//   words      not used in the 4 days before        highlight  not used in the 4 days before
//   scene      not used in the 3 days before        type    not the same as the day before
// and the whole combination (layout + photo + words + highlight) never repeats within 90 days; within any
// 2 weeks, days share as few of those 4 parts as possible (usually no more than 2).
// lookFor(date, prevPostDate) also makes sure the corner differs from the previous post even when
// the gap is 4 days or more.
//
// CLI: node video_looks.js 2026-11-30 [days]   prints the looks for that many days (default 7).

const OPTIONS = {
  corner: ['top-left', 'bottom-right', 'top-right', 'bottom-left'],
  layout: ['full-center', 'full-low-left', 'arch-window', 'photo-band', 'photo-strip', 'full-high-left'],
  photo: ['zoom-in', 'zoom-out', 'pan-left', 'pan-right', 'tilt-up', 'tilt-down', 'drift', 'turn'],
  words: ['pop', 'rise', 'slide', 'drop', 'blur', 'zoom'],
  highlight: ['gold', 'marker', 'underline', 'box', 'glow', 'serif'],
  scene: ['fade-up', 'slide', 'zoom', 'wipe', 'blur'],
  type: ['sans', 'serif', 'caps'],
};
const WINDOW = { corner: 3, layout: 4, photo: 5, words: 4, highlight: 4, scene: 3, type: 1 };
const COMBO = ['layout', 'photo', 'words', 'highlight'];
const COMBO_DAYS = 90, NEAR_DAYS = 14;
const EPOCH = Date.UTC(2026, 10, 1); // 2026-11-01

const dayIndex = (s) => {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || ''));
  if (!m) throw new Error('date must be YYYY-MM-DD: ' + s);
  return Math.round((Date.UTC(+m[1], +m[2] - 1, +m[3]) - EPOCH) / 86400000);
};
const dateOf = (i) => new Date(EPOCH + i * 86400000).toISOString().slice(0, 10);
const hash = (s) => { let h = 2166136261; for (const c of s) { h ^= c.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; } return h; };

const cache = [];
function dayLook(i) {
  if (i < 0) throw new Error('dates before ' + dateOf(0) + ' are not supported');
  for (let d = cache.length; d <= i; d++) {
    const look = { date: dateOf(d) };
    const cands = {};
    for (const k of Object.keys(OPTIONS)) {
      const recent = cache.slice(Math.max(0, d - WINDOW[k])).map((l) => l[k]);
      const c = OPTIONS[k].filter((o) => !recent.includes(o)), start = hash(k + look.date) % c.length;
      cands[k] = c.slice(start).concat(c.slice(0, start));
      if (!COMBO.includes(k)) look[k] = cands[k][0];
    }
    // Layout, photo, words and highlight are chosen together, so the combination is never one used in the last 90 days.
    const seen = new Set(cache.slice(Math.max(0, d - COMBO_DAYS)).map((l) => COMBO.map((c) => l[c]).join('|')));
    let tuples = [[]];
    for (const k of COMBO) tuples = tuples.flatMap((t) => cands[k].map((o) => t.concat(o)));
    let fresh = tuples.filter((t) => !seen.has(t.join('|')));
    if (!fresh.length) fresh = tuples;
    // Of those, prefer the ones that share the fewest parts with any day in the last 2 weeks.
    const near = cache.slice(Math.max(0, d - NEAR_DAYS));
    const overlap = (t) => Math.max(0, ...near.map((l) => COMBO.filter((c, n) => l[c] === t[n]).length));
    const best = Math.min(...fresh.map(overlap));
    fresh = fresh.filter((t) => overlap(t) === best);
    const pick = fresh[hash('combo' + look.date) % fresh.length];
    COMBO.forEach((k, n) => { look[k] = pick[n]; });
    cache.push(look);
  }
  return { ...cache[i] };
}

// The look for a post date. prevPostDate (optional) is the previous post's date: if it was 4+ days
// earlier and landed on the same corner, the corner moves to the one the day before used.
function lookFor(date, prevPostDate) {
  const i = dayIndex(date), look = dayLook(i);
  if (prevPostDate) {
    const j = dayIndex(prevPostDate);
    if (j < i && dayLook(j).corner === look.corner) look.corner = dayLook(i - 1).corner;
  }
  return look;
}

module.exports = { OPTIONS, lookFor, dayLook, dayIndex };

if (require.main === module) {
  const start = process.argv[2] || new Date().toISOString().slice(0, 10), n = +(process.argv[3] || 7);
  const s = dayIndex(start);
  for (let i = s; i < s + n; i++) {
    const l = dayLook(i);
    console.log([l.date, new Date(l.date + 'T12:00:00Z').toUTCString().slice(0, 3), ...Object.keys(OPTIONS).map((k) => l[k].padEnd(14))].join('  '));
  }
}
