/* Lowell Herb Co · Golden Hour v2 · shared behaviour: age gate, menu, ZIP forms, map hover, shop filter, product placeholder */
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
  $$('.js-signup').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var note = form.nextElementSibling; if (note) note.textContent = 'Preview only: sign-ups open with the new store.';
    });
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

  /* ---------- shop filter ---------- */
  var grid = $('#shop-grid');
  if (grid) {
    var chips = $$('.shop-bar .chip'), count = $('#shop-count');
    var apply = function (cat) {
      var n = 0;
      $$('.pcard', grid).forEach(function (c) { var show = cat === 'all' || c.dataset.cat === cat; c.hidden = !show; if (show) n++; });
      chips.forEach(function (ch) { ch.setAttribute('aria-pressed', String(ch.dataset.filter === cat)); });
      count.textContent = n + (n === 1 ? ' good' : ' goods');
    };
    chips.forEach(function (ch) { ch.addEventListener('click', function () {
      apply(ch.dataset.filter);
      var u = new URL(location.href); if (ch.dataset.filter === 'all') u.searchParams.delete('c'); else u.searchParams.set('c', ch.dataset.filter);
      history.replaceState(null, '', u.pathname + u.search + '#all');
    }); });
    var c0 = new URLSearchParams(location.search).get('c');
    if (c0 && $('.shop-bar [data-filter="' + c0 + '"]')) apply(c0);
  }

  /* ---------- product placeholder ---------- */
  var cat = $('#catalog');
  if (cat) {
    var data = JSON.parse(cat.textContent), slug = new URLSearchParams(location.search).get('p'), p = data[slug];
    if (p) {
      $('#pd-title').textContent = p.t; $('#pd-crumb').textContent = p.t; $('#pd-cat').textContent = p.c;
      $('#pd-price').textContent = p.a ? p.p : p.p + ' · sold out';
      var img = $('#pd-img'); img.src = 'img/p/' + slug + '-640.webp'; img.alt = p.t;
      document.title = p.t + ' · Farm Store · Lowell Herb Co. (v2 preview)';
    } else {
      $('#pd-title').textContent = 'Product not found';
    }
  }
})();
