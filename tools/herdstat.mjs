// herdstat.mjs — are goats herding? After `years`, compare each adult's company (goats in its own
// cell, its 3×3, and within socialRange) with the expectation under random placement on land, and
// report herd sizes as connected clusters of occupied cells (8-neighbour).
//   node tools/herdstat.mjs [years=150] [seed=1] [key=value ...]
import { loadSim } from '../load.mjs';
const [years = 150, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
for (let t = 0; t < years * P.yearDays; t++) e.update();
w.buildIndex();
const n = w.goats.length, dens = n / w.land.length, Rw = (2 * P.socialRange + 1) ** 2;
let c0 = 0, c1 = 0, c4 = 0;
for (const g of w.goats) { const i = g.y * w.W + g.x; c0 += w.goatCount[i] - 1; c1 += w.goats3x3(i) - 1; c4 += w.socialField[i] - 1; }
// clusters of occupied cells
const seen = new Uint8Array(w.N), sizes = [];
for (let i = 0; i < w.N; i++) {
  if (!w.goatCount[i] || seen[i]) continue;
  let s = 0; const st = [i]; seen[i] = 1;
  while (st.length) { const c = st.pop(); s += w.goatCount[c]; const x = c % w.W, y = (c / w.W) | 0;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) { const xx = x + dx, yy = y + dy;
      if (xx < 0 || yy < 0 || xx >= w.W || yy >= w.H) continue; const j = yy * w.W + xx; if (w.goatCount[j] && !seen[j]) { seen[j] = 1; st.push(j); } } }
  sizes.push(s);
}
sizes.sort((a, b) => b - a);
const inHerds = sizes.reduce((a, s) => a + (s >= 5 ? s : 0), 0);
console.log(`${n} goats, year ${years}, day ${w.day} | company per goat: same cell ${(c0 / n).toFixed(2)} (random ${dens.toFixed(2)}), 3×3 ${(c1 / n).toFixed(2)} (random ${(dens * 9).toFixed(2)}), radius ${P.socialRange} ${(c4 / n).toFixed(1)} (random ${(dens * Rw).toFixed(1)})`);
console.log(`clusters: ${sizes.length}, largest ${sizes.slice(0, 8).join(', ')}, median ${sizes[sizes.length >> 1]}, share of goats in clusters ≥5: ${(inHerds / n).toFixed(2)}`);
