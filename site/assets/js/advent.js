/* CatholicDoorway Advent calendar: a church whose numbered doors and windows open one day at a time.
   Without JavaScript each door is a link to that day's card in the list below the picture.
   Opened doors are remembered in localStorage (cd-advent-<year>); future days stay shut.
   Add ?peek to the address to open every door early (for previewing the calendar). */
(function () {
  'use strict';
  var root = document.getElementById('advent-cal');
  if (!root) return;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var M = JSON.parse(root.getAttribute('data-msgs'));
  var start = root.getAttribute('data-start'), end = root.getAttribute('data-end');
  var KEY = 'cd-advent-' + root.getAttribute('data-year');
  var doors = $$('.ac-door', root);
  var days = doors.map(function (d) { return d.getAttribute('data-day'); }).sort();
  var byDay = {};
  doors.forEach(function (d) { byDay[d.getAttribute('data-day')] = d; });
  var dialog = $('#ac-dialog', root), body = $('#ac-dbody', root);
  var status = $('#ac-status', root), progress = $('#ac-progress', root);
  var todayBtn = $('#ac-today', root), reset = $('#ac-reset', root);
  var prev = $('#ac-prev', root), next = $('#ac-next', root), closeBtn = $('#ac-close', root);
  var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var canDialog = dialog && typeof dialog.showModal === 'function';
  var current = null, lastDoor = null, toast = $('#ac-toast', root), toastTimer = null;
  // A short note at the bottom of the screen, so it is seen wherever the door is
  function note(text) {
    toast.textContent = text;
    toast.hidden = false;
    toast.classList.remove('is-out');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.classList.add('is-out');
      toastTimer = setTimeout(function () { toast.hidden = true; }, 400);
    }, 4500);
  }

  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function localISO(dt) { return dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate()); }
  var peek = /[?&]peek\b/.test(location.search);
  var today = peek ? end : localISO(new Date());
  function isOpenable(day) { return day <= today; }
  function fill(s, d) { return s.replace('{d}', d); }

  var opened = {};
  try { (JSON.parse(localStorage.getItem(KEY)) || []).forEach(function (d) { opened[d] = 1; }); } catch (e) {}
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(Object.keys(opened))); } catch (e) {}
  }

  root.classList.add('is-live');
  if (canDialog) root.classList.add('has-dialog');

  function label(door) {
    var day = door.getAttribute('data-day'), date = door.getAttribute('data-date');
    var s = opened[day] ? M.opened : (isOpenable(day) ? M.open : M.locked);
    door.setAttribute('aria-label', fill(s, date));
  }

  function refresh() {
    var k = days.filter(function (d) { return opened[d]; }).length;
    progress.textContent = M.progress.replace('{k}', k).replace('{N}', days.length);
    reset.hidden = k === 0;
    doors.forEach(function (d) {
      var day = d.getAttribute('data-day');
      d.classList.toggle('is-open', !!opened[day]);
      d.classList.toggle('is-today', day === today && !opened[day]);
      label(d);
    });
  }

  function say(text) { status.textContent = text; status.hidden = !text; }
  function baseline() {
    if (today < start) say(fill(M.before, root.getAttribute('data-first')));
    else if (today > end) say(M.after);
    else say('');
    todayBtn.hidden = !(today >= start && today <= end);
  }

  // Doors already opened appear open without swinging when the page loads
  root.classList.add('no-anim');
  refresh();
  baseline();
  requestAnimationFrame(function () { requestAnimationFrame(function () { root.classList.remove('no-anim'); }); });

  function show(day) {
    var card = document.getElementById('advent-' + day);
    if (!card) return;
    current = day;
    if (!canDialog) { card.scrollIntoView({ behavior: calm ? 'auto' : 'smooth', block: 'start' }); return; }
    body.innerHTML = card.innerHTML;
    var h = $('h3', body);
    h.id = 'ac-dtitle';
    h.setAttribute('tabindex', '-1');
    var i = days.indexOf(day);
    prev.disabled = i <= 0;
    next.disabled = i >= days.length - 1 || !isOpenable(days[i + 1]);
    if (!dialog.open) dialog.showModal();
    body.scrollTop = 0;
    h.focus({ preventScroll: true });
  }

  function open(door, fromNav) {
    var day = door.getAttribute('data-day');
    if (!isOpenable(day)) {
      note(fill(M.wait, door.getAttribute('data-date')));
      door.classList.remove('is-shake');
      void door.offsetWidth;
      door.classList.add('is-shake');
      return;
    }
    lastDoor = fromNav ? lastDoor : door;
    if (opened[day]) { show(day); return; }
    opened[day] = 1;
    save();
    refresh();
    baseline();
    if (fromNav || calm) show(day);
    else setTimeout(function () { show(day); }, 650);
  }

  doors.forEach(function (d) {
    d.addEventListener('click', function (ev) { ev.preventDefault(); open(d); });
    d.addEventListener('animationend', function () { d.classList.remove('is-shake'); });
  });
  todayBtn.addEventListener('click', function () { if (byDay[today]) open(byDay[today]); });
  reset.addEventListener('click', function () {
    opened = {};
    save();
    refresh();
    baseline();
  });

  if (canDialog) {
    prev.addEventListener('click', function () {
      var i = days.indexOf(current);
      if (i > 0) open(byDay[days[i - 1]], true);
    });
    next.addEventListener('click', function () {
      var i = days.indexOf(current);
      if (i < days.length - 1) open(byDay[days[i + 1]], true);
    });
    closeBtn.addEventListener('click', function () { dialog.close(); });
    // Tap outside the card to close it
    dialog.addEventListener('click', function (ev) { if (ev.target === dialog) dialog.close(); });
    dialog.addEventListener('close', function () {
      var door = (current && byDay[current]) || lastDoor;
      if (door) door.focus({ preventScroll: true });
      current = null;
    });
  }

  // A link straight to a day (#advent-2026-12-08) opens it, if its day has come
  var m = /^#advent-(\d{4}-\d{2}-\d{2})$/.exec(location.hash);
  if (m && byDay[m[1]] && isOpenable(m[1])) {
    root.scrollIntoView({ block: 'start' });
    open(byDay[m[1]], true);
  }
})();
