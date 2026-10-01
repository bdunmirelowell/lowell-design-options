/* Lowell Herb Co · Golden Hour v2 · shared behaviour: age gate, menu, ZIP forms, map hover */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* private mode: ask again next page */ } }
  };
  var page = [$('.site-head'), $('#main'), $('.site-foot'), $('.ribbon')].filter(Boolean);
  function setInert(on) { page.forEach(function (el) { if (on) el.setAttribute('inert', ''); else el.removeAttribute('inert'); }); }

  /* keep Tab inside an open dialog */
  function trap(dialog, e) {
    if (e.key !== 'Tab') return;
    var f = $$('a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])', dialog).filter(function (el) { return el.offsetParent !== null; });
    if (!f.length) return;
    var first = f[0], last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  }

  /* ---------- 21+ gate ---------- */
  var gate = $('#gate');
  if (gate && store.get('lhc-21') !== 'yes') {
    gate.hidden = false; setInert(true); document.documentElement.style.overflow = 'hidden';
    var yes = $('#gate-yes'); yes.focus();
    gate.addEventListener('keydown', function (e) { trap(gate, e); });
    yes.addEventListener('click', function () {
      store.set('lhc-21', 'yes'); gate.hidden = true; setInert(false); document.documentElement.style.overflow = '';
      var m = $('#main'); if (m) { m.setAttribute('tabindex', '-1'); m.focus({ preventScroll: true }); }
    });
    $('#gate-no').addEventListener('click', function () {
      $('#gate-msg').textContent = 'Come back when you’re 21. The farm isn’t going anywhere.';
    });
  }

  /* ---------- menu sheet ---------- */
  var sheet = $('#sheet'), openBtn = $('#menu-open'), closeBtn = $('#menu-close');
  function closeSheet() { sheet.hidden = true; setInert(false); openBtn.setAttribute('aria-expanded', 'false'); document.documentElement.style.overflow = ''; openBtn.focus(); }
  if (sheet && openBtn) {
    openBtn.addEventListener('click', function () {
      sheet.hidden = false; setInert(true); openBtn.setAttribute('aria-expanded', 'true'); document.documentElement.style.overflow = 'hidden'; closeBtn.focus();
    });
    closeBtn.addEventListener('click', closeSheet);
    sheet.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSheet(); else trap(sheet, e); });
    $$('nav a', sheet).forEach(function (a) { a.addEventListener('click', function () { if (a.getAttribute('href').indexOf('#') > -1) closeSheet(); }); });
  }

  /* ---------- ZIP forms: validate here, the locator resolves ---------- */
  $$('.js-zip').forEach(function (form) {
    var input = $('input', form), note = form.nextElementSibling;
    form.addEventListener('submit', function (e) {
      var v = (input.value || '').replace(/\D/g, '');
      if (v.length !== 5) { e.preventDefault(); if (note) note.textContent = 'Enter a five-digit ZIP code.'; input.focus(); return; }
      input.value = v;
    });
    input.addEventListener('input', function () { if (note) note.textContent = ''; });
  });

  /* ---------- home map: chips and states light each other ---------- */
  $$('.state-links .chip').forEach(function (chip) {
    var path = $('.usmap a[data-st="' + chip.dataset.st + '"]');
    if (!path) return;
    ['mouseenter', 'focus'].forEach(function (ev) { chip.addEventListener(ev, function () { path.classList.add('lit'); }); });
    ['mouseleave', 'blur'].forEach(function (ev) { chip.addEventListener(ev, function () { path.classList.remove('lit'); }); });
    path.addEventListener('mouseenter', function () { chip.classList.add('on'); });
    path.addEventListener('mouseleave', function () { chip.classList.remove('on'); });
  });

})();
