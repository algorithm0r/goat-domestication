// herdprobe.mjs — one run with herding; a line every N years from herdingAt: herd size, flows, and
// herded vs wild genetic R and S, and learned fear of humans.  node tools/herdprobe.mjs <years> <every> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 600, every = 10, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed, herdingAt: 400 }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(), dm = new G.DataManager(w, null, null); e.add(w); e.add(dm);
for (let t = 1; t <= years * P.yearDays; t++) {
  e.update();
  if (t % P.yearDays === 0) {
    const y = dm.years[dm.years.length - 1];
    if (y.year >= P.herdingAt && (y.year + 1) % every === 0) {
      const h = y.herdTraitMeans, wild = y.goats - y.herded;
      console.log(`y${y.year + 1} goats ${y.goats} herded ${y.herded} | cap ${y.captured} esc ${y.escaped} cull ${y.culledHerd} hunted ${y.deaths.hunted}` +
        (h ? ` | R herd ${h.R.toFixed(2)} all ${y.traitMeans.R.toFixed(2)} | S herd ${h.S.toFixed(2)} all ${y.traitMeans.S.toFixed(2)} | fearH herd ${y.herdFearOfHumans}` : ''));
    }
  }
}
