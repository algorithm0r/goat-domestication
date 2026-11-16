// No-DB sanity run. Asserts the current stage's invariants and prints the numbers that belong in
// the DEVLOG entry (proof coupled to log). Exits non-zero on failure.   node smoketest.mjs
import { performance } from 'perf_hooks';
import { loadSim } from './load.mjs';

const G = loadSim({ seed: 1 });
const P = G.PARAMETERS;
let ok = true;
const check = (name, cond, detail) => { console.log(`  ${cond ? 'ok  ' : 'FAIL'} ${name}: ${detail}`); ok = ok && cond; };

// Stage 1 — vegetation alone settles into a stable seasonal cycle within [floor, 1].
{
  const saved = [P.goatsInit, P.wolvesN]; P.goatsInit = 0; P.wolvesN = 0;
  const w = new G.World(), e = new G.GameEngine(); e.add(w);
  const ym = []; let acc = 0, n = 0, lo = Infinity, hi = -Infinity;
  for (let t = 1; t <= 4 * P.yearDays; t++) {
    e.update(); acc += w.meanVeg(); n++;
    if (t % P.yearDays === 0) { ym.push(acc / n); acc = 0; n = 0; }
    for (const i of w.land) { const v = w.veg[i]; if (v < lo) lo = v; if (v > hi) hi = v; }
  }
  const drift = Math.abs(ym[3] - ym[2]) / ym[2];
  check('vegetation equilibrium', drift < 0.01 && lo >= P.vegFloor - 1e-6 && hi <= 1 + 1e-6,
    `drift ${(drift * 100).toFixed(3)}%, range [${lo.toFixed(3)}, ${hi.toFixed(3)}]`);
  [P.goatsInit, P.wolvesN] = saved;
}

// Stage 2 — goats and fixed wolves: 40 years persist; genomes and energies stay valid.
{
  const w = new G.World(), e = new G.GameEngine(), dm = new G.DataManager(w, null, null); e.add(w); e.add(dm);
  const t0 = performance.now();
  for (let t = 1; t <= 40 * P.yearDays; t++) e.update();
  const tps = Math.round(e.tick / ((performance.now() - t0) / 1000));
  let badAllele = 0, badE = 0;
  for (const g of w.goats) { for (const a of g.genome) if (!(a >= 0 && a <= 1)) badAllele++; if (!Number.isFinite(g.E) || g.E < 0) badE++; }
  const y = dm.years[dm.years.length - 1];
  check('goats persist 40 years', w.goats.length > 100, `${w.goats.length} goats, ${y.births} births in year 40`);
  check('alleles in [0,1], energies valid', badAllele === 0 && badE === 0, `${badAllele} bad alleles, ${badE} bad energies`);
  check('wolf count fixed', w.wolves.length === P.wolvesN, `${w.wolves.length} wolves`);
  console.log(`  ticks/s ${tps} at ~${w.goats.length} goats; trait means y40: ` + Object.entries(y.traitMeans).map(([k, v]) => k + v.toFixed(2)).join(' '));
}
console.log('smoke -> ' + (ok ? 'PASS' : 'FAIL'));
process.exit(ok ? 0 : 1);
