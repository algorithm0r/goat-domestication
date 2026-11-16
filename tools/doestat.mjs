// doestat.mjs — why do herd does kid (or not)? From year `from`, each day tally herd vs wild adult does
// (≥ 480 d): reserve fraction, size vs breeding threshold, pregnant, in heat, in heat with a buck in her
// 3×3, and vegetation where she stands. Prints means.   node tools/doestat.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 460, from = 430, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(), dm = new G.DataManager(w, null, null); e.add(w); e.add(dm);
const T = { herd: {}, wild: {} };
const add = (t, k, v) => { t[k] = (t[k] || 0) + v; };
const mate = w.mate.bind(w);
w.mate = () => {                                                 // sample on end-of-day positions, before mating
  if (w.year >= +from) for (const g of w.goats) {
    if (g.dead || g.sex !== G.SEX_F || g.age < P.femaleMinAge) continue;
    const t = g.herd >= 0 ? T.herd : T.wild, i = g.y * w.W + g.x;
    add(t, 'n', 1); add(t, 'E', g.E / g.reserveCap()); add(t, 'bigEnough', g.size >= P.breedSizeFrac * g.targetSize ? 1 : 0);
    add(t, 'pregnant', g.gestation > 0 ? 1 : 0); add(t, 'veg', w.veg[i]);
    if (g.receptive) {
      add(t, 'heat', 1); let bucks = 0;
      for (let y = Math.max(0, g.y - 1); y <= Math.min(w.H - 1, g.y + 1); y++)
        for (let x = Math.max(0, g.x - 1); x <= Math.min(w.W - 1, g.x + 1); x++) {
          const j = y * w.W + x;
          for (let o = w.cellStart[j]; o < w.cellStart[j + 1]; o++) { const m = w.goats[w.order[o]]; if (!m.dead && m.sex === G.SEX_M && m.age >= P.maleMinAge) bucks++; }
        }
      add(t, 'heatWithBuck', bucks > 0 ? 1 : 0);
    }
  }
  mate();
};
for (let d = 1; d <= years * P.yearDays; d++) e.update();
for (const k of ['herd', 'wild']) {
  const t = T[k], n = t.n || 1;
  console.log(`${k}: doe-days ${t.n} | E/cap ${(t.E / n).toFixed(2)} | big enough ${(t.bigEnough / n).toFixed(2)} | pregnant ${(t.pregnant / n).toFixed(2)} | heat-days per doe-year ${(360 * (t.heat || 0) / n).toFixed(2)} | with buck ${((t.heatWithBuck || 0) / (t.heat || 1)).toFixed(2)} | veg ${(t.veg / n).toFixed(2)}`);
}
