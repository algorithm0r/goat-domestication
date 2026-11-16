import { loadSim } from "../load.mjs";
const [q, seed] = process.argv.slice(2);
const G = loadSim({ seed: +seed, humansPerCamp: 0, leanQuality: +q }), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(), dm = new G.DataManager(w, null, null); e.add(w); e.add(dm);
for (let t = 1; t <= 280 * P.yearDays; t++) e.update();
let n = 0, lowE = 0, Ef = 0;
const kids = { lean: [0, 0], grow: [0, 0] };                 // [born, died before weaning]
const born = new Map();
for (let t = 1; t <= 20 * P.yearDays; t++) {
  e.update();
  for (const g of w.goats) if (g.age === 1 && !born.has(g.id)) born.set(g.id, { lean: w.growth === 0, g });
  let dd = Math.abs(w.day - P.rutPeakDay); if (dd > 180) dd = 360 - dd;
  if (dd <= 30) for (const g of w.goats) {
    if (g.dead || g.sex !== G.SEX_F || g.age < P.femaleMinAge || g.gestation > 0) continue;
    n++; Ef += g.E / g.reserveCap(); if (g.E < P.breedCondition * g.reserveCap()) lowE++;
  }
}
for (const { lean, g } of born.values()) { const k = lean ? kids.lean : kids.grow; k[0]++; if (g.dead && g.age < P.weanAge) k[1]++; }
const y = dm.years[dm.years.length - 1].traitMeans;
console.log(`leanQuality ${q} seed ${seed}: goats ${w.goats.length} | T ${y.T.toFixed(2)} R ${y.R.toFixed(2)} S ${y.S.toFixed(2)} B ${y.B.toFixed(2)} M ${y.M.toFixed(2)} | rut reserve ${(Ef / n).toFixed(2)}, condition-limited ${(lowE / n).toFixed(2)} | kid deaths before weaning: born in lean ${(kids.lean[1] / Math.max(1, kids.lean[0])).toFixed(2)} (n=${kids.lean[0]}), in growing ${(kids.grow[1] / Math.max(1, kids.grow[0])).toFixed(2)} (n=${kids.grow[0]})`);
