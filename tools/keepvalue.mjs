// keepvalue.mjs — the opportunity cull's keep value, broken into its parts, for every herd goat at one moment.
//   node tools/keepvalue.mjs <years> <out.json> [key=value ...]
// Runs the sim <years> years, then for each camp's herd calls World.cullByOpportunity once with cullNoise 0 and keepTerms 1,
// which stores each goat's keep-value terms (growth, kids, milk, sire share, feed, meat at risk, flight, last breeder);
// checks their total against the key the sim ranks by. Writes every goat's row to <out.json> and prints a table by sex and age.
import fs from 'fs'; import path from 'path';
import { loadSim } from '../load.mjs';
const [years, out, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS, Y = P.yearDays;
if (P.cullRule !== 'opportunity') throw new Error('keepvalue needs cullRule=opportunity');
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
for (let t = 1; t <= years * Y && world.goats.length > 0; t++) engine.update();

const herds = new Map();
for (const g of world.goats) if (!g.dead && g.herd >= 0) { if (!herds.has(g.herd)) herds.set(g.herd, []); herds.get(g.herd).push(g); }
const rows = []; let maxErr = 0;
// 2026-11-18: the terms come from the sim itself (keepTerms), so this tool can no longer drift from the cull rule
P.keepTerms = 1;
for (const [cid, m] of herds) {
  const noise = P.cullNoise; P.cullNoise = 0; world.cullByOpportunity(m.slice()); P.cullNoise = noise;
  const sires = P.sireRule !== 'oldest' ? world.siresOf(cid)
    : m.filter(g => g.sex === G.SEX_M && g.age >= P.maleMinAge).sort((a, b) => b.age - a.age).slice(0, P.keepSires);
  const heirs = m.filter(g => g.sex === G.SEX_M && !sires.includes(g) && g.age >= P.weanAge).sort((a, b) => b.age - a.age).slice(0, P.keepHeirs);
  for (const g of m) {
    const t = g._kvTerms, r = { camp: cid, sex: g.sex ? 'M' : 'F', age: +(g.age / Y).toFixed(2), size: +g.size.toFixed(3), target: +g.target.toFixed(3) };
    for (const k of ['growth', 'kids', 'milk', 'sire', 'feed', 'risk', 'flight', 'last', 'total']) r[k] = t[k];
    r.role = sires.includes(g) ? 'sire' : heirs.includes(g) ? 'heir' : '';
    maxErr = Math.max(maxErr, Math.abs(-g._cullKey - t.total));       // the stored total against the key the sim ranks by
    rows.push(r);
  }
}
// rank within each herd: rank 1 = eaten first
for (const cid of herds.keys()) {
  const rs = rows.filter(r => r.camp === cid).sort((a, b) => a.total - b.total);
  rs.forEach((r, i) => { r.rank = i + 1; r.pct = +((i + 0.5) / rs.length).toFixed(3); });
}
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({ params: P, year: world.year, day: world.day, maxErr, rows }));

const f = x => (x >= 0 ? '+' : '') + x.toFixed(3);
console.log(`year ${world.year} day ${world.day}; ${herds.size} herds, ${rows.length} herd goats; check against the sim: max |diff| ${maxErr.toExponential(1)}`);
console.log('class            n  growth   kids   sire   feed   risk  total  eaten-first share (bottom 15% of its herd)');
const classes = [['F', 0, 1], ['F', 1, 2], ['F', 2, 3], ['F', 3, 5], ['F', 5, 9], ['F', 9, 99], ['M', 0, 1], ['M', 1, 2], ['M', 2, 3], ['M', 3, 5], ['M', 5, 99]];
for (const [s, a0, a1] of classes) {
  const rs = rows.filter(r => r.sex === s && r.age >= a0 && r.age < a1 && r.role !== 'sire'); if (!rs.length) continue;
  const mean = k => rs.reduce((t, r) => t + r[k], 0) / rs.length;
  console.log(`${s} ${a0}-${a1 === 99 ? '+' : a1}`.padEnd(12) + String(rs.length).padStart(5) + ['growth', 'kids', 'sire', 'feed', 'risk', 'total'].map(k => f(mean(k)).padStart(7)).join('')
    + `  ${(rs.filter(r => r.pct < 0.15).length / rs.length).toFixed(2)}`);
}
const sr = rows.filter(r => r.role === 'sire');
if (sr.length) { const mean = k => sr.reduce((t, r) => t + r[k], 0) / sr.length;
  console.log('M sires'.padEnd(12) + String(sr.length).padStart(5) + ['growth', 'kids', 'sire', 'feed', 'risk', 'total'].map(k => f(mean(k)).padStart(7)).join('')); }
