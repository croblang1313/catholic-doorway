/* CatholicDoorway Stations of the Cross: walk from station to station, one at a time.
   Without JavaScript every station shows as a list; this turns them into a walk-through. */
(function () {
  'use strict';
  var root = document.getElementById('stations-app');
  if (!root) return;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var cards = $$('.st-card', root), dots = $$('.st-dots button', root);
  var back = $('#st-back', root), next = $('#st-next', root), count = $('#st-count', root);
  var KEY = 'cd-stations-at', at = 0, lock = null, last = cards.length - 1;

  root.classList.add('is-walk');
  $$('[hidden]', root).forEach(function (el) { if (!el.classList.contains('st-card')) el.hidden = false; });

  // Start where the link points (#station-7), else where you left off in the last 6 hours
  var m = /^#station-(\d+)$/.exec(location.hash);
  if (m && +m[1] <= last) at = +m[1];
  else {
    try {
      var saved = JSON.parse(localStorage.getItem(KEY));
      if (saved && Date.now() - saved.t < 6 * 3600 * 1000 && saved.i <= last) at = saved.i;
    } catch (e) {}
  }
  // Keep the prayers open or closed the way you last left them
  var openPrayers = false;
  try { openPrayers = localStorage.getItem('cd-stations-prayers') === '1'; } catch (e) {}
  $$('.st-prayers', root).forEach(function (d) {
    d.open = openPrayers;
    d.addEventListener('toggle', function () {
      openPrayers = d.open;
      try { localStorage.setItem('cd-stations-prayers', d.open ? '1' : '0'); } catch (e) {}
      $$('.st-prayers', root).forEach(function (o) { if (o !== d) o.open = d.open; });
    });
  });

  function show(i, focus) {
    at = Math.max(0, Math.min(last, i));
    cards.forEach(function (c, k) { c.hidden = k !== at; });
    dots.forEach(function (d, k) {
      d.classList.toggle('now', k === at);
      d.classList.toggle('done', k < at);
      if (k === at) d.setAttribute('aria-current', 'step'); else d.removeAttribute('aria-current');
    });
    count.textContent = at === 0 || at === last ? dots[at].getAttribute('aria-label') : at + ' / ' + (last - 1);
    back.disabled = at === 0;
    next.innerHTML = at === last ? next.getAttribute('data-again') : next.getAttribute('data-next');
    try { localStorage.setItem(KEY, JSON.stringify({ i: at, t: Date.now() })); } catch (e) {}
    if (history.replaceState) history.replaceState(null, '', at ? '#station-' + at : location.pathname + location.search);
    if (focus) {
      var h = $('h2', cards[at]);
      h.setAttribute('tabindex', '-1');
      h.focus({ preventScroll: true });
      var top = root.getBoundingClientRect().top;
      if (top < 0 || top > window.innerHeight * 0.4) root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function keepAwake() {
    if (!lock && navigator.wakeLock && document.visibilityState === 'visible') {
      navigator.wakeLock.request('screen').then(function (l) { lock = l; l.addEventListener('release', function () { lock = null; }); }).catch(function () {});
    }
  }
  function go(i) { show(i, true); keepAwake(); }

  next.addEventListener('click', function () { go(at === last ? 0 : at + 1); });
  back.addEventListener('click', function () { go(at - 1); });
  dots.forEach(function (d) { d.addEventListener('click', function () { go(+d.getAttribute('data-go')); }); });
  document.addEventListener('keydown', function (ev) {
    if (ev.target.closest && ev.target.closest('input, select, textarea, summary')) return;
    if (ev.key === 'ArrowRight') { go(at + 1); }
    else if (ev.key === 'ArrowLeft') { go(at - 1); }
  });
  // Swipe left or right on the picture
  var sx = null, sy = null;
  root.addEventListener('touchstart', function (ev) { sx = ev.touches[0].clientX; sy = ev.touches[0].clientY; }, { passive: true });
  root.addEventListener('touchend', function (ev) {
    if (sx === null) return;
    var dx = ev.changedTouches[0].clientX - sx, dy = ev.changedTouches[0].clientY - sy;
    sx = null;
    if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) go(at + (dx < 0 ? 1 : -1));
  }, { passive: true });
  document.addEventListener('visibilitychange', function () { if (document.visibilityState === 'visible' && lock === null && at > 0) keepAwake(); });

  show(at, false);
})();
