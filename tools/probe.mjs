// probe.mjs — quick headless look at population dynamics: one run, a line per N years.
//   node tools/probe.mjs [years=60] [every=5] [seed=1] [key=value ...param overrides]
import { performance } from 'perf_hooks';
import { loadSim } from '../load.mjs';
const [years = 60, every = 5, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed };
for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const t0 = performance.now();
for (let t = 1; t <= years * P.yearDays; t++) {
  engine.update();
  if (t % P.yearDays === 0) {
    const y = dm.years[dm.years.length - 1];
    if ((y.year + 1) % every === 0 || world.goats.length === 0) {
      const c = world.census(), d = y.deaths, tm = y.traitMeans;
      console.log(`y${String(y.year + 1).padStart(4)} goats ${String(c.goats).padStart(5)} kids ${String(c.kids).padStart(4)} F/M ${c.females}/${c.males}` +
        ` births ${y.births} deaths pred/hunt/starv/age/oth/fight/exp ${d.predation}/${d.hunted}/${d.starvation}/${d.age}/${d.other}/${d.fight}/${d.exposure}` +
        ` firstKid ${y.medianFirstKidAge} adultMort ${y.adultMortality} veg ${world.meanVeg().toFixed(3)}` +
        ` | ` + Object.entries(tm).map(([k, v]) => k + (v == null ? '-' : v.toFixed(2))).join(' ') +
        (y.herded ? ` || herded ${y.herded} cap ${y.captured} esc ${y.escaped} cull ${y.culledHerd} fearH ${y.herdFearOfHumans}` +
          ` herd R ${y.herdTraitMeans.R.toFixed(2)} S ${y.herdTraitMeans.S.toFixed(2)}` : ''));
    }
    if (world.goats.length === 0) { console.log('EXTINCT'); break; }
  }
}
console.log(`ticks/s ${Math.round(engine.tick / ((performance.now() - t0) / 1000))}`);
