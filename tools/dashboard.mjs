// Build the dashboard's data from saved runs: node tools/dashboard.mjs [folder ...]
// Every results/<folder>/<arm>_seed<s>.json that recorded herd histograms (histHerd, from 2026-11-02) becomes one arm:
// dashboard/data/<folder>/<arm>.json holds, per column of dx years and pooled over seeds, each gene's genotype
// histogram (20 buckets on 0-1) in the herd and in the wild (all goats minus herd), and lines for goats, gene means,
// lineage depth and IBD. dashboard/data/index.json lists the arms. A file is re-read only when its size or time changes
// (dashboard/data/cache.json), so a rebuild after a new batch reads only the new runs. View it at http://localhost:8000/goats/
// (the always-on Static Server, mount 'goats' in Claude's Space/Static Server/sites.json).
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const SIM = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const RES = path.join(SIM, 'results'), OUT = path.join(SIM, 'dashboard', 'data');
const GENES = ['R', 'A', 'S', 'B', 'H', 'T', 'M', 'W', 'L', 'C'];
const BINS = 20;
// the new base (EXPLOG [STANDARD SETTINGS 2026-11-11]); herdRange is a sweep variable, so it does not decide the base
const NEW_BASE = p => p.leanBuffer === 12000 && p.herdTravel === 2;
// keys that describe an arm: human behaviour and the base; the rest are model constants
const DESCRIBE = ['humansAt', 'humansPerCamp', 'herdingAt', 'cullRule', 'offtakeRate', 'penning', 'guarding', 'provision', 'kidShelter',
  'buckManagement', 'tetherNew', 'milkIntensity', 'exchangeN', 'sireRule', 'herdMemory', 'buckCull', 'doeCull',
  'captureUntil', 'wildSireBlock', 'wildSireBlockFrom', 'cullFloor', 'immigrationRate', 'keepSires', 'twinMax', 'tripletMax', 'leanBuffer', 'herdRange', 'herdTravel', 'genomeCosts'];

const BUILD = 3;   // bump when the digest or the index entry changes, so every arm is rebuilt
const want = process.argv.slice(2);
fs.mkdirSync(OUT, { recursive: true });
const cacheFile = path.join(OUT, 'cache.json');
const cache = fs.existsSync(cacheFile) ? JSON.parse(fs.readFileSync(cacheFile, 'utf8')) : {};
const oldIndex = fs.existsSync(path.join(OUT, 'index.json')) ? JSON.parse(fs.readFileSync(path.join(OUT, 'index.json'), 'utf8')) : { arms: [] };

const localDate = ms => { const d = new Date(ms); return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); };
const mean = v => { const f = v.filter(x => typeof x === 'number' && isFinite(x)); return f.length ? f.reduce((a, b) => a + b, 0) / f.length : null; };
const r4 = x => x == null ? null : Math.round(x * 1e4) / 1e4;

// one seed's run → per-column sums, so seeds pool by adding
function digest(d, dx) {
  const Y = d.years, n = Y.length, nc = Math.ceil(n / dx);
  const herd = {}, wild = {};
  for (const g of GENES) { herd[g] = Array.from({ length: nc }, () => new Array(BINS).fill(0)); wild[g] = Array.from({ length: nc }, () => new Array(BINS).fill(0)); }
  const lines = { herd: [], wild: [], depth: [], ibd: [], herdMean: {}, wildMean: {} };
  for (const g of GENES) { lines.herdMean[g] = []; lines.wildMean[g] = []; }
  for (let c = 0; c < nc; c++) {
    const ys = Y.slice(c * dx, (c + 1) * dx);
    for (let k = 0; k < ys.length; k++) {
      const yi = c * dx + k;
      for (const g of GENES) {
        const all = d.hist[g] && d.hist[g][yi], hh = d.histHerd[g] && d.histHerd[g][yi];
        if (!all) continue;
        for (let b = 0; b < BINS; b++) { const h = hh ? hh[b] : 0; herd[g][c][b] += h; wild[g][c][b] += all[b] - h; }
      }
    }
    lines.herd.push(mean(ys.map(y => y.herded)));
    lines.wild.push(mean(ys.map(y => y.goats - y.herded)));
    lines.depth.push(mean(ys.filter(y => y.herded).map(y => y.herdAncDepth)));
    lines.ibd.push(mean(ys.filter(y => y.herded).map(y => y.herdF)));
    for (const g of GENES) {
      lines.herdMean[g].push(mean(ys.filter(y => y.herded && y.herdTraitMeans).map(y => y.herdTraitMeans[g])));
      lines.wildMean[g].push(mean(ys.map(y => {
        const hm = y.herdTraitMeans && y.herdTraitMeans[g], am = y.traitMeans[g], nh = y.herded, na = y.goats;
        if (am == null) return null;
        if (!nh || hm == null) return am;
        return na > nh ? (am * na - hm * nh) / (na - nh) : null;
      })));
    }
  }
  return { n, nc, herd, wild, lines, depth: depthDigest(d) };
}

// gene histograms by lineage depth (runs from 2026-11-11 on), re-pooled from DEPTH_EVERY-year records into DEPTH_DX-year
// records: depth[side][gene][record][bin][bucket], side herd | wild
const DEPTH_DX = 100;
function depthDigest(d) {
  const D = d.histDepth;
  if (!D || !D.herd || !D.herd.R) return null;
  const per = DEPTH_DX / D.every, nr = Math.floor(D.herd.R.length / per), out = { dx: DEPTH_DX, bins: D.bins, wildShareBins: D.wildShareBins, herd: {}, wild: {} };
  for (const side of ['herd', 'wild']) for (const g of GENES) {
    out[side][g] = Array.from({ length: nr }, (_, r) => {
      const acc = D[side][g][0].map(() => new Array(BINS).fill(0));
      for (let k = r * per; k < (r + 1) * per; k++) D[side][g][k].forEach((bin, j) => bin.forEach((v, q) => acc[j][q] += v));   // wild has SHARE_BINS.length bins
      return acc;
    });
  }
  return out;
}

const folders = fs.readdirSync(RES).filter(f => fs.statSync(path.join(RES, f)).isDirectory() && (!want.length || want.includes(f)));
const arms = new Map(oldIndex.arms.filter(a => want.length && !want.includes(a.folder)).map(a => [a.folder + '/' + a.arm, a]));
let read = 0, skipped = 0;
for (const folder of folders.sort()) {
  const files = fs.readdirSync(path.join(RES, folder)).filter(f => /_seed\d+\.json$/.test(f));
  const byArm = {};
  for (const f of files) (byArm[f.replace(/_seed\d+\.json$/, '')] ||= []).push(f);
  for (const [arm, fs_] of Object.entries(byArm)) {
    const key = folder + '/' + arm, stamp = 'b' + BUILD + '|' + fs_.sort().map(f => { const s = fs.statSync(path.join(RES, folder, f)); return f + ':' + s.size + ':' + s.mtimeMs; }).join('|');
    const outFile = path.join(OUT, folder, arm + '.json');
    if (cache[key] && cache[key].stamp === stamp && (cache[key].skip || fs.existsSync(outFile))) {
      if (!cache[key].skip) arms.set(key, cache[key].entry);
      continue;
    }
    const seeds = [];
    let P = null, dx = null, acc = null, mtime = 0;
    for (const f of fs_) {
      let d;
      try { d = JSON.parse(fs.readFileSync(path.join(RES, folder, f), 'utf8')); } catch (e) { continue; }
      read++;
      if (!d.histHerd || !d.hist || !Array.isArray(d.years) || !d.years.length || !d.histHerd.R || !d.histHerd.R.length) continue;
      P = P || d.params;
      dx = dx || (d.years.length > 2000 ? 20 : 10);
      const g = digest(d, dx);
      seeds.push({ seed: d.params.seed, years: g.n, lastHerd: g.lines.herd[g.nc - 1] });
      mtime = Math.max(mtime, fs.statSync(path.join(RES, folder, f)).mtimeMs);
      if (!acc) { acc = g; acc.lineList = [g.lines]; continue; }
      const nc = Math.min(acc.nc, g.nc);
      for (const gene of GENES) for (const side of ['herd', 'wild']) {
        acc[side][gene].length = nc;
        for (let c = 0; c < nc; c++) for (let b = 0; b < BINS; b++) acc[side][gene][c][b] += g[side][gene][c][b];
      }
      acc.nc = nc; acc.n = Math.min(acc.n, g.n); acc.lineList.push(g.lines);
      if (acc.depth && g.depth) {
        const nr = Math.min(acc.depth.herd.R.length, g.depth.herd.R.length);
        for (const side of ['herd', 'wild']) for (const gene of GENES) {
          acc.depth[side][gene].length = nr;
          for (let r = 0; r < nr; r++) g.depth[side][gene][r].forEach((bin, j) => bin.forEach((v, q) => acc.depth[side][gene][r][j][q] += v));
        }
      } else acc.depth = null;   // pool depth only when every seed has it
    }
    if (!acc) { cache[key] = { stamp, skip: true }; skipped++; continue; }
    const L = acc.lineList, nc = acc.nc;
    const avg = sel => Array.from({ length: nc }, (_, c) => r4(mean(L.map(l => sel(l)[c]))));
    const lines = { herd: avg(l => l.herd), wild: avg(l => l.wild), depth: avg(l => l.depth), ibd: avg(l => l.ibd), herdMean: {}, wildMean: {} };
    for (const g of GENES) { lines.herdMean[g] = avg(l => l.herdMean[g]); lines.wildMean[g] = avg(l => l.wildMean[g]); }
    const params = {};
    for (const k of DESCRIBE) if (P[k] !== undefined) params[k] = P[k];
    const entry = { folder, arm, seeds: seeds.length, years: acc.n, dx, base: NEW_BASE(P) ? 'new' : 'old', herding: P.herdingAt < 1e8 && P.humansAt < 1e8 && P.humansPerCamp !== 0,
      humans: P.humansAt < 1e8 && P.humansPerCamp !== 0, hasDepth: !!acc.depth, date: localDate(mtime), params };
    fs.mkdirSync(path.join(OUT, folder), { recursive: true });
    fs.writeFileSync(outFile, JSON.stringify({ ...entry, bins: BINS, genes: GENES, seedList: seeds, herd: acc.herd, wild: acc.wild, lines, depth: acc.depth }));
    arms.set(key, entry);
    cache[key] = { stamp, entry };
    console.log(`${key}: ${seeds.length} seeds, ${acc.n} years, ${entry.base} base`);
  }
}
const list = [...arms.values()].sort((a, b) => (b.date + b.folder).localeCompare(a.date + a.folder) || a.arm.localeCompare(b.arm));
fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify({ built: new Date().toISOString(), genes: GENES, arms: list }));
fs.writeFileSync(cacheFile, JSON.stringify(cache));
console.log(`${list.length} arms; read ${read} files; ${skipped} arms without herd histograms`);
