// campherds.mjs — each camp's herd size every `every` years from herdingAt (do single herds die out and
// get refounded?).  node tools/campherds.mjs <years> <every> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 520, every = 5, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed, herdingAt: 400 }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const line = [];
for (let d = 1; d <= years * P.yearDays; d++) {
  e.update();
  if (d % P.yearDays === 0 && w.year >= P.herdingAt && w.year % every === 0) {
    const n = w.camps.map(c => w.goats.filter(g => !g.dead && g.herd === c.id).length);
    line.push(`y${w.year} ${n.join('/')}`);
  }
}
console.log(line.join('  '));
