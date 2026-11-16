'use strict';
// Goat genes dashboard. Reads data/index.json and data/<folder>/<arm>.json (built by tools/dashboard.mjs) and draws,
// per gene, the wild and herd genotype distributions over time as histogram heatmaps, and their means as lines.
// The page state is the hash: #<folder>/<arm>.
(function () {
  var GENES = LABELS.GENES;
  var WILD = 'var(--cb-series-1)', HERD = 'var(--cb-series-2)';
  var $ = function (id) { return document.getElementById(id); };
  var esc = CB.esc, index = null;

  document.getElementById('picker').appendChild(CB.theme.picker());

  function shown() {
    return index.arms.filter(function (a) { return $('show').value !== 'new' || a.base === 'new'; });
  }
  function folders() {
    var seen = {}, out = [];
    shown().forEach(function (a) { if (!seen[a.folder]) { seen[a.folder] = a.date; out.push(a.folder); } });
    return out;
  }
  function fillFolders(sel) {
    $('folder').innerHTML = folders().map(function (f) {
      var n = shown().filter(function (a) { return a.folder === f; });
      return '<option value="' + esc(f) + '">' + esc(LABELS.experiment(f).title) + ' · ' + n[0].date + ' (' + n.length + ')</option>';
    }).join('');
    if (sel) $('folder').value = sel;
  }
  function fillArms(sel) {
    var f = $('folder').value;
    $('arm').innerHTML = shown().filter(function (a) { return a.folder === f; }).map(function (a) {
      return '<option value="' + esc(a.arm) + '">' + esc(LABELS.arm(a.folder, a.arm)) + '</option>';
    }).join('');
    if (sel) $('arm').value = sel;
  }
  function entry() {
    var f = $('folder').value, a = $('arm').value;
    return index.arms.filter(function (e) { return e.folder === f && e.arm === a; })[0];
  }

  // what the experiment asked, what this condition is, and its settings in words; the raw settings behind a disclosure
  function about(e) {
    var p = e.params, x = LABELS.experiment(e.folder), diff = LABELS.differences(p);
    var raw = Object.keys(p).filter(function (k) { return k !== 'seed'; }).map(function (k) { return esc(k) + ' ' + esc(String(p[k])); }).join(' · ');
    $('about').innerHTML =
      '<div class="exp"><b>' + esc(x.title) + '.</b> ' + esc(x.about) + '</div>' +
      '<div class="cond"><b>' + esc(LABELS.arm(e.folder, e.arm)) + '</b>' +
      (LABELS.note(e.folder, e.arm) ? '' : diff.length ? '<span class="diff">differs from the reference culture: ' + esc(diff.join('; ')) + '</span>'
        : e.herding ? '<span class="diff">the reference culture\'s herding practices</span>' : '') + '</div>' +
      '<div class="badges">' +
      '<span class="cb-badge ' + (e.base === 'new' ? 'ok' : 'neutral') + '" data-tip="' + esc(e.base === 'new'
        ? 'Lean-tissue buffer on, pasture range swept, walking pace 2 (the settings from 2026-11-11 on).' : LABELS.OLDER) + '">' +
      (e.base === 'new' ? 'current settings' : 'older settings') + '</span>' +
      '<span class="cb-badge neutral" data-tip="Independent runs with different random seeds, pooled in every chart.">' + e.seeds + ' run' + (e.seeds > 1 ? 's' : '') + '</span>' +
      '<span class="cb-badge neutral">' + e.years + ' years</span>' +
      '<span class="cb-badge neutral" data-tip="When the runs finished.">' + e.date + '</span>' +
      '<span class="cb-badge neutral" data-tip="Folder results/' + esc(e.folder) + ', condition ' + esc(e.arm) + '; see EXPLOG.md.">' + esc(e.folder) + ' / ' + esc(e.arm) + '</span>' +
      '</div>' +
      (LABELS.note(e.folder, e.arm) ? '<div class="diff">' + esc(LABELS.note(e.folder, e.arm)) + '</div>' : '') +
      '<details class="cb-disclosure"><summary>All settings in words</summary><div class="body">' + esc(LABELS.settings(p).join(' · ')) +
      '<div class="raw">' + raw + '</div></div></details>';
  }

  function series(label, sers, d, opts) {
    var el = document.createElement('cb-sim-series');
    el.setAttribute('label', label); el.setAttribute('x-label', 'year');
    for (var k in (opts || {})) el.setAttribute(k, opts[k]);
    el.data = { dx: d.dx, x0: 0, series: sers };
    return el;
  }
  function histmap(label, cols, d, color) {
    var el = document.createElement('cb-sim-histmap');
    el.setAttribute('label', label); el.setAttribute('x-label', 'year');
    el.setAttribute('lo', '0'); el.setAttribute('hi', '1'); el.setAttribute('bins', String(d.bins));
    el.setAttribute('color', color); el.setAttribute('height', '96');
    el.data = { columns: cols, dx: d.dx, x0: 0 };
    return el;
  }
  function group(title, name, kids) {
    var g = document.createElement('div');
    g.className = 'cb-sim-group'; g.style.setProperty('--cols', String(kids.length));
    g.innerHTML = '<div class="cb-label">' + esc(title) + (name ? '<span class="name">' + esc(name) + '</span>' : '') + '</div>';
    kids.forEach(function (k) { g.appendChild(k); });
    return g;
  }

  function draw(d) {
    var box = $('charts'); box.innerHTML = '';
    var herded = d.herding && d.humans;   // no humans: herdingAt is set but nothing is herded
    var wildName = herded ? 'wild goats' : 'all goats';
    box.appendChild(group('Population', '', [
      series('Number of goats', [{ label: wildName, values: d.lines.wild, color: WILD }].concat(herded ? [{ label: 'herd goats', values: d.lines.herd, color: HERD }] : []), d, { 'y-min': 0 })
    ].concat(herded ? [
      series('Generations born in the herd (herd average)', [{ label: 'generations', values: d.lines.depth, color: HERD }], d, { 'y-min': 0 }),
      series('Inbreeding in the herd (0 none, 1 complete)', [{ label: 'share of genome identical by descent', values: d.lines.ibd, color: HERD }], d, { 'y-min': 0, 'y-max': 1 })
    ] : [])));
    d.genes.forEach(function (g) {
      var kids = [histmap(herded ? 'Wild goats: gene value over time' : 'All goats: gene value over time', d.wild[g], d, WILD)];
      if (herded) kids.push(histmap('Herd goats: gene value over time', d.herd[g], d, HERD));
      kids.push(series('Average gene value', [{ label: wildName, values: d.lines.wildMean[g], color: WILD }]
        .concat(herded ? [{ label: 'herd goats', values: d.lines.herdMean[g], color: HERD }] : []), d, { 'y-min': 0, 'y-max': 1 }));
      box.appendChild(group(GENES[g].name, GENES[g].does + ' (gene ' + g + ')', kids));
    });
    if (d.depth) box.appendChild(depthSection(d));
  }

  // ── by lineage depth: per gene, one distribution per depth class, pooled over a window of years ──────────────
  // Columns: wild goats by the share of their genome from herd-born goats (none, up to 1/16, 1/8, 1/4, 1/2, more), then
  // herd goats by mean generations born in a herd, in the recorded bins (MODEL §8, lineage depth).
  function depthCols(d, side, gene, r0, r1) {
    var D = d.depth, nb = D.bins.length, cols = [];
    var sum = function (sd, j) {
      var c = new Array(d.bins).fill(0);
      for (var r = r0; r < r1; r++) D[sd][gene][r][j].forEach(function (v, q) { c[q] += v; });
      return c;
    };
    if (side === 'wild') {
      var out = [];
      for (var j = 0; j < D.wild[gene][0].length; j++) out.push(sum('wild', j));
      return out;
    }
    for (var k = 0; k < nb; k++) cols.push(sum('herd', k));
    return cols;
  }
  function depthSection(d) {
    var D = d.depth, nr = D.herd.R.length, wrap = document.createElement('div');
    wrap.className = 'wide depth';
    var span = nr * D.dx, wins = [[400, 500], [800, 900], [1200, 1300], [1500, 1600]].filter(function (w) { return w[1] <= span; });
    var last = [Math.max(0, span - (span > 2000 ? 800 : 200)), span];
    wins.push(last);
    var binName = function (b) { return b[0] === b[1] ? String(b[0]) : b[1] > 1e8 ? b[0] + '+' : b[0] + '–' + b[1]; };
    var shareName = ['none', '⅟16', '⅛', '¼', '½', '>½'];
    var names = (D.wildShareBins || [0]).map(function (_, i) { return 'wild ' + shareName[i]; })
      .concat(D.bins.map(function (b) { return 'herd ' + binName(b); }));
    wrap.innerHTML = '<div class="cb-label">Gene values by ancestry<span class="name">wild goats by how much of their genome comes from herd-born goats (escaped herd stock); herd goats by how many generations their ancestry was born in the herd · years ' +
      '<select class="cb-select" id="dwin">' + wins.map(function (w, i) {
        return '<option value="' + i + '"' + (i === wins.length - 1 ? ' selected' : '') + '>' + (w[0] + 1) + '–' + w[1] + '</option>';
      }).join('') + '</select></span></div><div class="cb-sim-charts depth-charts"></div>';
    var box = wrap.lastChild;
    function paint() {
      var w = wins[+wrap.querySelector('#dwin').value], r0 = w[0] / D.dx, r1 = w[1] / D.dx;
      box.innerHTML = '';
      d.genes.forEach(function (g) {
        var cols = depthCols(d, 'wild', g, r0, r1).concat(depthCols(d, 'herd', g, r0, r1));
        var el = document.createElement('cb-sim-histmap');
        el.setAttribute('label', GENES[g].name); el.setAttribute('x-label', 'ancestry group');
        el.setAttribute('lo', '0'); el.setAttribute('hi', '1'); el.setAttribute('bins', String(d.bins)); el.setAttribute('height', '96');
        el.data = { columns: cols, dx: 1, x0: 1 };
        var cell = document.createElement('div');
        cell.appendChild(el);
        var key = document.createElement('div'); key.className = 'depth-key'; key.style.gridTemplateColumns = 'repeat(' + cols.length + ', minmax(0, 1fr))';
        var nw = (D.wildShareBins || [0]).length;
        key.innerHTML = '<span class="grp" style="grid-column: 1 / ' + (nw + 1) + '" title="Share of the genome from herd-born goats">wild: share from herd</span>' +
          '<span class="grp herd" style="grid-column: ' + (nw + 1) + ' / -1" title="Generations born in the herd">herd: generations in herd</span>' +
          cols.map(function (c, i) {
            var n = c.reduce(function (a, b) { return a + b; }, 0);
            var short = names[i].replace(/^(wild|herd) /, '').replace('none', '0');
            return '<span title="' + names[i] + ': goats a year, mean over seeds"' + (i === nw ? ' class="first-herd"' : '') + '>' + short +
              '<br><b>' + CB.fmt.num(Math.round(n / (r1 - r0) / D.dx / d.seeds)) + '</b></span>';
          }).join('');
        cell.appendChild(key);
        box.appendChild(cell);
      });
    }
    wrap.querySelector('#dwin').addEventListener('change', paint);
    setTimeout(paint);
    return wrap;
  }

  function load() {
    var e = entry(); if (!e) return;
    about(e);
    location.replace('#' + encodeURIComponent(e.folder) + '/' + encodeURIComponent(e.arm));
    fetch('data/' + encodeURIComponent(e.folder) + '/' + encodeURIComponent(e.arm) + '.json')
      .then(function (r) { return r.json(); })
      .then(draw)
      .catch(function (err) { $('charts').innerHTML = '<div class="cb-empty">Could not load this arm: ' + esc(String(err)) + '</div>'; });
  }

  $('folder').addEventListener('change', function () { fillArms(); load(); });
  $('arm').addEventListener('change', load);
  $('show').addEventListener('change', function () { var f = $('folder').value; fillFolders(f); fillArms(); load(); });

  // the arm the hash names, or the reference culture
  function fromHash() {
    var h = location.hash.slice(1).split('/').map(decodeURIComponent);
    var e = index.arms.filter(function (a) { return a.folder === h[0] && a.arm === h[1]; })[0]
      || index.arms.filter(function (a) { return a.folder === 'settle' && a.arm === 'S0'; })[0] || index.arms[0];
    if (e.base !== 'new') $('show').value = 'all';
    if (e.folder === $('folder').value && e.arm === $('arm').value) return;
    fillFolders(e.folder); fillArms(e.arm); load();
  }
  window.addEventListener('hashchange', function () { if (index) fromHash(); });

  fetch('data/index.json').then(function (r) { return r.json(); }).then(function (ix) {
    index = ix;
    var b = new Date(ix.built);
    $('built').textContent = ix.arms.length + ' conditions, updated ' + b.toLocaleDateString() + ' ' + b.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    fromHash();
  });
})();
