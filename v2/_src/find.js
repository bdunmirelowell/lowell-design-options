/* Lowell Herb Co · Golden Hour v2 · Find Lowell
   Functional spec: brya8385.github.io/find-lowell (app.v4.js). Data is fetched live from that app's doors.json
   on every visit; there is deliberately no embedded or cached fallback. Product rows are shown as line x lean only,
   never by blend name. Tier B (shipped, no feed) and tier C (partner-reported) never show a price. */
(function () {
  'use strict';
  var main = document.querySelector('.fl');
  if (!main) return;
  var $ = function (id) { return document.getElementById(id); };
  var params = new URLSearchParams(location.search);
  var DOORS = params.get('doors-test') === 'fail' ? 'https://brya8385.github.io/find-lowell/data/does-not-exist.json' : main.dataset.doors;

  var LEAN = { I: 'Indica', S: 'Sativa', H: 'Hybrid', V: 'Variety' };
  var LINE_ORDER = ['Quicks', 'Smokes', "35's", 'Outlaws', 'Singles', '2-Pack', 'Littles', 'Ground Flower', 'Flower'];
  var STATE_NAME = { CA: 'California', CO: 'Colorado', NM: 'New Mexico', MO: 'Missouri', IL: 'Illinois', OH: 'Ohio', NY: 'New York', NJ: 'New Jersey' };
  var STATE_ORDER = ['CA', 'CO', 'NM', 'MO', 'IL', 'OH', 'NY', 'NJ'];
  /* generous state boxes: a door whose coordinates fall outside its own state is not pinned (geocoding error) */
  var BOX = { CA: [32.4, 42.1, -124.6, -114.0], CO: [36.9, 41.1, -109.1, -102.0], NM: [31.3, 37.1, -109.1, -103.0], IL: [36.9, 42.6, -91.6, -87.0],
    NJ: [38.9, 41.4, -75.6, -73.8], NY: [40.4, 45.1, -79.8, -71.8], MO: [35.9, 40.7, -95.8, -89.1], OH: [38.4, 42.0, -84.9, -80.5] };
  var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  var doors = [], rows = [], map = null, layer = null, ring = null, youMark = null, markers = new Map();
  var S = { started: false, st: null, line: null, lean: null, radius: 50, stockOnly: true, showMore: false, origin: null, originLabel: '', sel: null };

  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  function fmtDate(iso, withYear) {
    var m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || ''); if (!m) return iso || '';
    return MONTHS[+m[2] - 1] + ' ' + (+m[3]) + (withYear === false ? '' : ', ' + m[1]);
  }
  function miles(a, b, c, d) {
    var R = 3958.8, p = Math.PI / 180, dLa = (c - a) * p, dLo = (d - b) * p;
    var x = Math.sin(dLa / 2) * Math.sin(dLa / 2) + Math.cos(a * p) * Math.cos(c * p) * Math.sin(dLo / 2) * Math.sin(dLo / 2);
    return 2 * R * Math.asin(Math.sqrt(x));
  }
  function tier(d) { return d.C ? 'partner' : d.B ? 'ship' : (d.k > 0 ? 'stock' : 'out'); }
  function confirmedTier(d) { return !d.B && !d.C; }

  /* ---------------- load ---------------- */
  function load() {
    $('fl-list').innerHTML = '<div class="fl-loading">Loading stores&hellip;</div>';
    $('fl-asof').textContent = 'Loading store list…';
    fetch(DOORS, { cache: 'no-cache' })
      .then(function (r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
      .then(function (data) {
        if (!data || !Array.isArray(data.doors) || !data.doors.length) throw new Error('empty store list');
        document.querySelector('.fl-resulthead').hidden = false;
        doors = data.doors.map(function (d) {
          var b = BOX[d.s];
          d.valid = typeof d.la === 'number' && typeof d.lo === 'number' && (!b || (d.la >= b[0] && d.la <= b[1] && d.lo >= b[2] && d.lo <= b[3]));
          return d;
        });
        $('fl-asof').textContent = 'Store list updated ' + fmtDate(data.asof);
        $('fl-asof').dataset.asof = data.asof;
        initMap(); buildFilters(); applyParams();
      })
      .catch(function (err) {
        doors = [];
        document.querySelector('.fl-resulthead').hidden = true;
        $('fl-asof').textContent = 'Store list unavailable';
        $('fl-count').textContent = '';
        $('fl-reveal').hidden = true;
        $('fl-list').innerHTML = '<div class="fl-error" role="alert"><p class="h3">We couldn’t load the store list.</p>' +
          '<p class="small">The live list didn’t respond (' + esc(err.message) + '). We show nothing rather than an out-of-date copy. ' +
          'Try again in a moment.</p><button class="btn sm" type="button" id="fl-retry">Try again</button></div>';
        $('fl-retry').addEventListener('click', load);
        initMap();
      });
  }

  /* ---------------- map ---------------- */
  function initMap() {
    if (map || !window.L) {
      if (!window.L) $('fl-map').innerHTML = '<p class="fl-maperr small">The map didn’t load. The list still works.</p>';
      return;
    }
    map = L.map('fl-map', { scrollWheelZoom: false, zoomControl: true, attributionControl: true }).setView([39.5, -96], 4);
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors', maxZoom: 19
    }).addTo(map);
    map.on('focus click', function () { map.scrollWheelZoom.enable(); });
    map.on('blur mouseout', function () { map.scrollWheelZoom.disable(); });
    layer = L.layerGroup().addTo(map);
    var legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
      var el = L.DomUtil.create('div', 'fl-legend');
      el.innerHTML = '<div><span class="kdot k-stock"></span>In stock</div><div><span class="kdot k-out"></span>Listed, out today</div>' +
        '<div><span class="kdot k-ship"></span>Shipped, no menu feed</div><div><span class="kdot k-partner"></span>Partner-reported</div>';
      return el;
    };
    legend.addTo(map);
  }
  function icon(d) {
    var big = S.sel === d, sz = big ? 22 : 14;
    return L.divIcon({ className: 'fl-pin-wrap', html: '<span class="fl-pin p-' + tier(d) + (big ? ' sel' : '') + '"></span>', iconSize: [sz, sz], iconAnchor: [sz / 2, sz / 2] });
  }
  function drawMarkers(list) {
    if (!map) return;
    layer.clearLayers(); markers.clear();
    list.forEach(function (d) {
      if (!d.valid) return;
      var m = L.marker([d.la, d.lo], { icon: icon(d), title: d.n, alt: d.n, riseOnHover: true, zIndexOffset: tier(d) === 'stock' ? 200 : 0 });
      m.bindPopup(function () { return popup(d); }, { maxWidth: 280 });
      m.on('click', function () { select(d, false); });
      markers.set(d, m); layer.addLayer(m);
    });
  }
  function frame() {
    if (!map) return;
    if (ring) { map.removeLayer(ring); ring = null; }
    if (youMark) { map.removeLayer(youMark); youMark = null; }
    var pts;
    if (S.origin) {
      youMark = L.circleMarker(S.origin, { radius: 7, color: '#35291A', weight: 2, fillColor: '#A5301F', fillOpacity: 1 }).addTo(map).bindTooltip('Your search');
      if (S.radius) {
        ring = L.circle(S.origin, { radius: S.radius * 1609.34, color: '#A5301F', weight: 1.5, dashArray: '5 5', fillColor: '#C89B4B', fillOpacity: .07, interactive: false }).addTo(map);
        map.fitBounds(ring.getBounds(), { padding: [20, 20] }); return;
      }
      pts = rows.filter(function (d) { return d.valid; }).slice(0, 40).map(function (d) { return [d.la, d.lo]; }).concat([S.origin]);
    } else if (S.st) {
      pts = doors.filter(function (d) { return d.s === S.st && d.valid; }).map(function (d) { return [d.la, d.lo]; });
    } else {
      pts = doors.filter(function (d) { return d.valid; }).map(function (d) { return [d.la, d.lo]; });
    }
    if (pts && pts.length) map.fitBounds(L.latLngBounds(pts), { padding: [28, 28], maxZoom: 13 });
  }

  /* ---------------- filters ---------------- */
  function chip(parent, label, pressed, onclick, attrs) {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'chip'; b.innerHTML = label; b.setAttribute('aria-pressed', String(!!pressed));
    Object.keys(attrs || {}).forEach(function (k) { b.dataset[k] = attrs[k]; });
    b.addEventListener('click', onclick); parent.appendChild(b); return b;
  }
  function press(group, key, val) {
    Array.prototype.forEach.call($(group).children, function (b) { b.setAttribute('aria-pressed', String(b.dataset[key] === String(val))); });
  }
  function buildFilters() {
    var rad = $('fl-rad'), line = $('fl-line'), lean = $('fl-lean'), st = $('fl-st');
    rad.innerHTML = line.innerHTML = lean.innerHTML = st.innerHTML = '';
    [25, 50, 100, 0].forEach(function (r) {
      chip(rad, r ? r + ' mi' : 'Any', r === S.radius, function () { S.radius = r; press('fl-rad', 'r', r); render(); frame(); syncUrl(); }, { r: String(r) });
    });
    var present = {};
    doors.forEach(function (d) { (d.L || []).forEach(function (l) { present[l] = 1; }); });
    LINE_ORDER.filter(function (l) { return present[l]; }).concat(Object.keys(present).filter(function (l) { return LINE_ORDER.indexOf(l) < 0; }).sort())
      .forEach(function (l) {
        chip(line, esc(l), false, function () { S.line = S.line === l ? null : l; press('fl-line', 'line', S.line); render(); drawAndFrame(false); }, { line: l });
      });
    ['I', 'S', 'H', 'V'].filter(function (c) { return doors.some(function (d) { return (d.E || []).indexOf(c) > -1; }); }).forEach(function (c) {
      chip(lean, LEAN[c], false, function () { S.lean = S.lean === c ? null : c; press('fl-lean', 'lean', S.lean); render(); drawAndFrame(false); }, { lean: c });
    });
    STATE_ORDER.filter(function (s) { return doors.some(function (d) { return d.s === s; }); }).forEach(function (s) {
      chip(st, s, false, function () { pickState(S.st === s ? null : s); }, { st: s });
    });
    $('fl-stock').addEventListener('change', function (e) { S.stockOnly = e.target.checked; render(); drawAndFrame(false); });
  }
  var det = $('fl-filters'), mq = window.matchMedia('(max-width: 860px)');
  function syncDet() { if (!mq.matches) det.open = true; }
  syncDet(); if (mq.addEventListener) mq.addEventListener('change', syncDet);
  function filterCount() {
    var n = (S.line ? 1 : 0) + (S.lean ? 1 : 0) + (S.st ? 1 : 0) + (S.origin && S.radius !== 50 ? 1 : 0);
    $('fl-fcount').textContent = n ? '\u00b7 ' + n : '';
  }
  function drawAndFrame(reframe) { drawMarkers(rows); if (reframe) frame(); }
  function pickState(s) {
    S.st = s; S.origin = null; S.originLabel = ''; S.started = true; S.sel = null; $('fl-q').value = ''; $('fl-note').textContent = '';
    press('fl-st', 'st', s); render(); drawAndFrame(true); syncUrl();
  }

  /* ---------------- search ---------------- */
  var zipCache = {};
  function zipLookup(z) {
    var k = z.charAt(0);
    var p = zipCache[k] || (zipCache[k] = fetch('assets/zip/zip-' + k + '.v1.json').then(function (r) { if (!r.ok) throw new Error(); return r.json(); }).catch(function () { delete zipCache[k]; return {}; }));
    return p.then(function (tbl) {
      if (tbl[z]) return tbl[z];
      var hit = doors.filter(function (d) { return d.z === z && d.valid; })[0];
      return hit ? [hit.la, hit.lo] : null;
    });
  }
  function cityLookup(q) {
    q = q.toLowerCase().split(',')[0].trim(); if (!q) return null;
    var byCity = {};
    doors.forEach(function (d) { if (d.valid && d.c) (byCity[d.c.toLowerCase()] = byCity[d.c.toLowerCase()] || []).push(d); });
    var key = byCity[q] ? q : Object.keys(byCity).filter(function (c) { return c.indexOf(q) === 0; })[0];
    if (!key) return null;
    var pts = byCity[key];
    return { at: [pts.reduce(function (s, d) { return s + d.la; }, 0) / pts.length, pts.reduce(function (s, d) { return s + d.lo; }, 0) / pts.length], label: pts[0].c + ', ' + pts[0].s };
  }
  function search(raw) {
    var q = (raw || '').trim(); var note = $('fl-note');
    if (!q) { note.textContent = 'Enter a ZIP code or a city.'; return; }
    if (!doors.length) return;
    if (/^\d{5}$/.test(q)) {
      note.textContent = 'Looking up ' + q + '…';
      zipLookup(q).then(function (at) {
        if (!at) { note.textContent = 'We couldn’t find ZIP ' + q + '. Check the number, or try a city.'; return; }
        setOrigin(at, 'ZIP ' + q);
      });
      return;
    }
    if (/^\d+$/.test(q)) { note.textContent = 'ZIP codes have five digits.'; return; }
    var c = cityLookup(q);
    if (!c) { note.textContent = 'We don’t have a shop in “' + q + '”. Try a five-digit ZIP code and we’ll find the nearest.'; return; }
    setOrigin(c.at, c.label);
  }
  function setOrigin(at, label) {
    S.origin = at; S.originLabel = label; S.st = null; S.started = true; S.sel = null; S.showMore = false;
    $('fl-note').textContent = '';
    press('fl-st', 'st', null); render(); drawAndFrame(true); syncUrl();
  }
  $('fl-form').addEventListener('submit', function (e) { e.preventDefault(); search($('fl-q').value); });

  function syncUrl() {
    var u = new URLSearchParams();
    if (S.origin && /^ZIP \d{5}$/.test(S.originLabel)) u.set('zip', S.originLabel.slice(4));
    else if (S.origin) u.set('q', $('fl-q').value.trim());
    if (S.st) u.set('st', S.st);
    if (S.origin && S.radius !== 50) u.set('r', String(S.radius));
    if (params.get('doors-test')) u.set('doors-test', params.get('doors-test'));
    var qs = u.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : ''));
  }
  function applyParams() {
    var r = +params.get('r'); if ([25, 50, 100, 0].indexOf(r) > -1 && params.has('r')) { S.radius = r; press('fl-rad', 'r', r); }
    var z = (params.get('zip') || '').replace(/\D/g, ''), q = params.get('q'), st = (params.get('st') || '').toUpperCase();
    if (z) { $('fl-q').value = z; render(); drawAndFrame(true); search(z); }
    else if (q) { $('fl-q').value = q; render(); drawAndFrame(true); search(q); }
    else if (STATE_NAME[st]) { pickState(st); }
    else { render(); drawAndFrame(true); }
  }

  /* ---------------- render ---------------- */
  function inScope(d) {
    if (S.st && d.s !== S.st) return false;
    if (S.origin && S.radius && (!d.valid || d._m > S.radius)) return false;
    if (S.line && (d.L || []).indexOf(S.line) < 0) return false;
    if (S.lean && (d.E || []).indexOf(S.lean) < 0) return false;
    return true;
  }
  function render() {
    var list = $('fl-list');
    $('fl-filters').hidden = !S.started; filterCount();
    $('fl-rad').parentNode.hidden = !S.origin;
    doors.forEach(function (d) { d._m = (S.origin && d.valid) ? miles(S.origin[0], S.origin[1], d.la, d.lo) : null; });

    if (!S.started) {
      rows = doors.slice();
      var counts = {}; doors.forEach(function (d) { counts[d.s] = (counts[d.s] || 0) + 1; });
      $('fl-count').textContent = doors.length + ' stores in ' + Object.keys(counts).length + ' states';
      $('fl-reveal').hidden = true;
      list.innerHTML = '<div class="fl-where"><p class="h3">Where are you?</p><p class="small">Search a ZIP code or city above, or pick a state.</p><div class="fl-states">' +
        STATE_ORDER.filter(function (s) { return counts[s]; }).map(function (s) {
          return '<button type="button" class="fl-state" data-gstate="' + s + '"><b>' + STATE_NAME[s] + '</b><span>' + counts[s] + ' stores</span></button>';
        }).join('') + '</div></div>';
      Array.prototype.forEach.call(list.querySelectorAll('.fl-state'), function (b) { b.addEventListener('click', function () { pickState(b.dataset.gstate); }); });
      return;
    }

    var scope = doors.filter(inScope);
    var confirmed = scope.filter(confirmedTier), unconfirmed = scope.filter(function (d) { return !confirmedTier(d); });
    var auto = !confirmed.length && unconfirmed.length > 0;   /* CO, NM, CA: partner data only */
    var includeMore = S.showMore || auto;
    rows = scope.filter(function (d) {
      if (!confirmedTier(d)) return includeMore;
      return !(S.stockOnly && d.k <= 0);
    });
    rows.sort(S.origin ? function (a, b) { return a._m - b._m; }
      : function (a, b) { return (b.k || 0) - (a.k || 0) || (confirmedTier(b) - confirmedTier(a)) || a.n.localeCompare(b.n); });

    var where = S.origin ? (S.radius ? 'within ' + S.radius + ' miles of ' + S.originLabel : 'nearest to ' + S.originLabel) : (S.st ? 'in ' + STATE_NAME[S.st] : '');
    $('fl-count').innerHTML = '<b>' + rows.length + (rows.length === 1 ? ' store' : ' stores') + '</b> ' + esc(where) + (S.origin ? ', nearest first' : '');

    var rev = $('fl-reveal');
    if (auto) {
      rev.hidden = false;
      rev.innerHTML = '<span>No shop here has a live menu feed yet, so these are stores we ship or that our partner reports. Call ahead for stock.</span>';
    } else if (unconfirmed.length && !S.showMore) {
      rev.hidden = false;
      rev.innerHTML = '<span><b>' + unconfirmed.length + '</b> more ' + (unconfirmed.length === 1 ? 'store carries' : 'stores carry') + ' Lowell without a live menu feed.</span> <button type="button" class="fl-linkbtn" id="fl-more">Show them</button>';
      $('fl-more').addEventListener('click', function () { S.showMore = true; render(); drawAndFrame(false); });
    } else if (S.showMore && unconfirmed.length) {
      rev.hidden = false;
      rev.innerHTML = '<span>Including <b>' + unconfirmed.length + '</b> without a live menu feed.</span> <button type="button" class="fl-linkbtn" id="fl-less">Hide them</button>';
      $('fl-less').addEventListener('click', function () { S.showMore = false; render(); drawAndFrame(false); });
    } else rev.hidden = true;

    list.innerHTML = '';
    if (!rows.length) { list.appendChild(emptyState()); return; }
    var frag = document.createDocumentFragment();
    rows.slice(0, 150).forEach(function (d) { frag.appendChild(card(d)); });
    if (rows.length > 150) { var more = document.createElement('p'); more.className = 'small fl-cap'; more.textContent = 'Showing the first 150. Narrow the search to see the rest.'; frag.appendChild(more); }
    list.appendChild(frag);
  }
  function emptyState() {
    var el = document.createElement('div'); el.className = 'fl-empty';
    var msg = 'No stores match those filters.';
    if (S.origin && S.radius) {
      var near = doors.filter(function (d) { return d.valid && d._m != null && (!S.line || (d.L || []).indexOf(S.line) > -1) && (!S.lean || (d.E || []).indexOf(S.lean) > -1); })
        .sort(function (a, b) { return a._m - b._m; })[0];
      msg = 'No stores within ' + S.radius + ' miles of ' + S.originLabel + '.';
      if (near) msg += ' The nearest is ' + esc(near.n) + ' in ' + esc(near.c || '') + ', ' + near.s + ', ' + Math.round(near._m) + ' miles away.';
      el.innerHTML = '<p>' + msg + '</p><button type="button" class="btn sm line" id="fl-widen">Show any distance</button>';
      el.querySelector('#fl-widen').addEventListener('click', function () { S.radius = 0; press('fl-rad', 'r', 0); render(); drawAndFrame(true); syncUrl(); });
      return el;
    }
    if (S.stockOnly) {
      el.innerHTML = '<p>' + msg + '</p><button type="button" class="btn sm line" id="fl-nostock">Include stores out of stock today</button>';
      el.querySelector('#fl-nostock').addEventListener('click', function () { $('fl-stock').checked = false; S.stockOnly = false; render(); drawAndFrame(false); });
      return el;
    }
    el.innerHTML = '<p>' + msg + '</p>'; return el;
  }

  /* product rows: grouped by line x lean. The blend name field is never read. */
  function groups(d) {
    var g = {}, order = [];
    (d.P || []).forEach(function (r) {
      var line = r[1] || 'Lowell', lean = r[2] || '', key = line + '|' + lean;
      if (!g[key]) { g[key] = { line: line, lean: lean, spec: r[4] || '', price: null, n: 0 }; order.push(key); }
      g[key].n++;
      var p = parseFloat(r[3]); if (!isNaN(p) && (g[key].price === null || p < g[key].price)) g[key].price = p;
      if (!g[key].spec && r[4]) g[key].spec = r[4];
    });
    return order.map(function (k) { return g[k]; }).sort(function (a, b) {
      var ia = LINE_ORDER.indexOf(a.line), ib = LINE_ORDER.indexOf(b.line);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib) || 'IHSV'.indexOf(a.lean) - 'IHSV'.indexOf(b.lean);
    });
  }
  function money(v) { return '$' + (Math.round(v) === v ? v : v.toFixed(2)); }
  function badge(d) {
    var t = tier(d);
    if (t === 'stock') return '<span class="fl-badge b-stock">In stock &middot; ' + d.k + ' product' + (d.k > 1 ? 's' : '') + '</span>';
    if (t === 'out') return '<span class="fl-badge b-out">Listed &middot; out of stock today</span>';
    if (t === 'ship') return '<span class="fl-badge b-ship">Carries Lowell &middot; shipped ' + esc(fmtDate(d.last)) + '</span>';
    var when = String(d.src || '').split('·').pop().trim();
    return '<span class="fl-badge b-partner">Partner-reported' + (when ? ' &middot; ' + esc(when) : '') + '</span>';
  }
  function tel(d) { return d.tel ? '<a class="fl-tel" href="tel:' + String(d.tel).replace(/[^0-9+]/g, '') + '">' + esc(d.tel) + '</a>' : ''; }
  function link(d) {
    if (!d.u) return '';
    var verified = d.uk === 'verified';
    return '<a class="fl-go' + (verified ? '' : ' ghost') + '" href="' + esc(d.u) + '" target="_blank" rel="noopener">' + (verified ? 'See Lowell at this store' : 'View their menu') +
      '<span class="sr-only"> (opens in a new tab)</span> &rarr;</a>';
  }
  function card(d) {
    var t = tier(d), el = document.createElement('article');
    el.className = 'fl-card t-' + t + (S.sel === d ? ' sel' : '');
    el.dataset.key = doors.indexOf(d);
    var priced = t === 'stock';   /* tier A with stock only; B and C never show a price */
    var price = priced && d.p ? '<span class="fl-price mono">' + (d.p === d.ph || !d.ph ? money(+d.p) : money(+d.p) + '–' + money(+d.ph)) + '</span>' : '';
    var dist = d._m != null && S.origin ? '<span class="fl-dist mono">' + (d._m < 10 ? d._m.toFixed(1) : Math.round(d._m)) + ' mi</span>' : '';
    var gs = groups(d), shown = S.sel === d ? gs : gs.slice(0, 4), hidden = gs.length - shown.length;
    var prods = gs.length ? '<ul class="fl-prods" aria-label="' + (t === 'ship' ? 'What we shipped' : 'Lowell on the menu') + '">' + shown.map(function (g) {
      return '<li><span class="fl-line">' + esc(g.line) + '</span>' + (g.lean ? '<span class="fl-lean l-' + g.lean + '">' + LEAN[g.lean] + '</span>' : '') +
        (g.spec ? '<span class="fl-spec">' + esc(g.spec) + '</span>' : '') + (priced && g.price != null ? '<span class="fl-pp mono">' + money(g.price) + '</span>' : '') + '</li>';
    }).join('') + '</ul>' + ((hidden > 0 || d.more > 0) ? '<p class="fl-more small">' + (hidden > 0 ? '+' + hidden + ' more' : '') + (d.more > 0 ? (hidden > 0 ? ', and more on their menu' : 'More on their menu') : '') + '</p>' : '') : '';
    var note = t === 'ship' && !d.u ? '<p class="fl-hint small">No live menu feed: call ahead.</p>'
      : t === 'partner' ? '<p class="fl-hint small">' + (d.approx ? 'Placed by city, not street address. ' : '') + 'Call ahead for stock.</p>' : '';
    var nomap = !d.valid ? '<p class="fl-hint small">Map location unavailable.</p>' : '';
    el.innerHTML = '<div class="fl-top"><h3 class="fl-name"><button type="button" aria-describedby="addr-' + el.dataset.key + '">' + esc(d.n) + '</button></h3>' + dist + '</div>' +
      '<p class="fl-addr small" id="addr-' + el.dataset.key + '">' + esc(d.a) + '</p>' +
      '<div class="fl-meta">' + badge(d) + price + '</div>' + prods + note + nomap +
      '<div class="fl-actions">' + link(d) + tel(d) + '</div>';
    el.querySelector('.fl-name button').addEventListener('click', function () { select(d, true); });
    return el;
  }
  function popup(d) {
    return '<div class="fl-pop"><b>' + esc(d.n) + '</b><p>' + esc(d.a) + '</p>' + badge(d) + '<div class="fl-actions">' + link(d) + tel(d) + '</div></div>';
  }
  function select(d, fromList) {
    var prev = S.sel; S.sel = (S.sel === d && fromList) ? null : d;
    [prev, S.sel].forEach(function (x) { if (x && markers.get(x)) markers.get(x).setIcon(icon(x)); });
    var redraw = function (x) { var c = x && document.querySelector('.fl-card[data-key="' + doors.indexOf(x) + '"]'); if (c) c.replaceWith(card(x)); };
    if (prev && prev !== S.sel) redraw(prev);
    redraw(d);
    var el = document.querySelector('.fl-card[data-key="' + doors.indexOf(d) + '"]');
    if (!S.sel || !map) return;
    if (fromList && d.valid) {
      map.setView([d.la, d.lo], Math.max(map.getZoom(), 13));
      var m = markers.get(d); if (m) m.openPopup();
      if (window.innerWidth < 900) document.querySelector('.fl-mapwrap').scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  load();
})();
