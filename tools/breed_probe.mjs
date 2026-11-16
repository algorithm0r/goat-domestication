// breed_probe.mjs — which gate keeps young does from breeding? No rand draws added; reads goats at chosen days.
//   node tools/breed_probe.mjs <years> <from-year> <out.json> [key=value ...]
// From <from-year> on, on each probe day (rut peak and ±45 days), for every doe that has never kidded, by age in
// whole years: counts that pass each gate of updateReceptive (age ≥ breedAge, size ≥ breedSizeFrac × target,
// reserve ≥ breedCondition × cap, inside her season) and all of them, and mean load of those that pass the size
// gate vs not. Also, per year, first-kid ages and loads of does that kidded for the first time.
import fs from 'fs'; import path from 'path';
import { loadSim } from '../load.mjs';
const [years, from, out, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const days = [P.rutPeakDay - 45, P.rutPeakDay, (P.rutPeakDay + 45) % P.yearDays];
const S = { over, days, byAge: {}, firstKid: [] };
const gate = (g) => {
  const half = P.rutHalfBase + g.tr[G.T_T] * P.rutHalfRange;
  let d = Math.abs(world.day - P.rutPeakDay); if (d > P.yearDays / 2) d = P.yearDays - d;
  return { age: g.age >= g.breedAge, size: g.size >= P.breedSizeFrac * g.target, cond: g.E >= P.breedCondition * g.reserveCap(), season: d <= half };
};
const seenKid = new Set();
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) {
  engine.update();
  if (world.year < +from) continue;
  if (days.includes(world.day)) for (const g of world.goats) {
    if (g.dead || g.sex !== G.SEX_F || g.kids > 0 || g.age < P.yearDays) continue;
    const a = Math.min(5, Math.floor(g.age / P.yearDays)), r = gate(g);
    const b = S.byAge[a] || (S.byAge[a] = { n: 0, age: 0, size: 0, cond: 0, season: 0, all: 0, sizeCond: 0, loadSize: 0, nSize: 0, loadNoSize: 0, nNoSize: 0 });
    b.n++; for (const k of ['age', 'size', 'cond', 'season']) if (r[k]) b[k]++;
    if (r.age && r.size && r.cond && r.season) b.all++;
    if (r.size && r.cond) b.sizeCond++;
    if (r.size) { b.loadSize += g.load; b.nSize++; } else { b.loadNoSize += g.load; b.nNoSize++; }
  }
  if (world.day === P.yearDays - 1) for (const g of world.goats) if (!g.dead && g.sex === G.SEX_F && g.firstKidAge > 0 && !seenKid.has(g.id)) {
    seenKid.add(g.id); S.firstKid.push([g.firstKidAge, +g.load.toFixed(3)]);
  }
}
fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, JSON.stringify(S));
console.log(out, 'done');
