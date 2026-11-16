// econprobe.mjs — what limits a herd in the economy? From year `from`, per camp-day: herd size, feeders,
// fodder in store, fodder the herd wanted vs got; and the circumstances of every herd starvation and every
// shortfall slaughter (season, feeders that day, stores).   node tools/econprobe.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 540, from = 500, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed, economy: 1, herdingAt: 400 }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const on = () => w.year >= +from;
const T = { campDays: 0, herdDays: 0, feederDays: 0, want: 0, got: 0, emptyStoreDays: 0 };
const starv = { n: 0, noFeeder: 0, lean: 0, storeEmpty: 0, kid: 0, ageSum: 0, Esum: 0 };
const cull = { n: 0, lean: 0, byQuarter: [0, 0, 0, 0], meat: 0, fodder: 0 };
const kill = w.kill.bind(w);
w.kill = (g, cause) => {
  if (on() && !g.dead && g.herd >= 0) {
    const c = w.camps[g.herd], lean = w.growth === 0;
    if (cause === G.CAUSE.starvation) {
      starv.n++; if (c.feedBudget <= 0 && (c._feeders || 0) === 0) starv.noFeeder++; if (lean) starv.lean++;
      if (c.fodder < 1) starv.storeEmpty++; if (g.isKid()) starv.kid++; starv.ageSum += g.age / P.yearDays;
    }
    if (cause === G.CAUSE.culled) { cull.n++; if (lean) cull.lean++; cull.byQuarter[Math.min(3, (w.day / 90) | 0)]++; cull.meat += c.meat; cull.fodder += c.fodder; }
  }
  kill(g, cause);
};
const assign = w.assignHerdTasks.bind(w);
w.assignHerdTasks = (c, crew) => { assign(c, crew); c._feeders = crew.filter(h => h.task === 'feed').length; };
// fodder wanted vs got: wrap each goat's daily via the camp's feed signal and fodder drawn
const life = w.lifeHistory.bind(w);
w.lifeHistory = () => {
  const before = w.camps.map(c => ({ f: c.fodder, s: c.sd.feed }));
  life();
  if (!on()) return;
  w.camps.forEach((c, k) => {
    T.campDays++;
    if (w.herdCount[c.id] > 0) { T.herdDays++; if (c._feeders > 0) T.feederDays++; }
    T.want += c.sd.feed - before[k].s; T.got += Math.max(0, before[k].f - c.fodder);
    if (c.fodder < 1) T.emptyStoreDays++;
  });
};
for (let d = 1; d <= years * P.yearDays; d++) e.update();
const f = (a, b) => (b ? a / b : 0).toFixed(2);
console.log(`seed ${seed} ${kv.join(' ')}`);
console.log(`  herd camp-days ${T.herdDays} of ${T.campDays} | with a feeder ${f(T.feederDays, T.herdDays)} | fodder got/wanted ${f(T.got, T.want)} | camp-days with store < 1 fu ${f(T.emptyStoreDays, T.campDays)}`);
console.log(`  herd starvation ${starv.n}: no feeder that day ${f(starv.noFeeder, starv.n)}, lean season ${f(starv.lean, starv.n)}, store empty ${f(starv.storeEmpty, starv.n)}, kids ${f(starv.kid, starv.n)}, mean age ${f(starv.ageSum, starv.n)} y`);
console.log(`  shortfall slaughters ${cull.n}: lean season ${f(cull.lean, cull.n)}, by quarter of year ${cull.byQuarter.join('/')}, mean meat store ${f(cull.meat, cull.n)} fodder store ${f(cull.fodder, cull.n)} at the time`);
