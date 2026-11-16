// diag_trait.mjs — selection on one trait, measured directly. Runs `burn` years, then for `obs` years
// tracks every goat-day by tercile of the trait's genotypic value: deaths by cause per goat-year,
// conceptions per doe-year, and mean group size (other goats in the cell).
//   node tools/diag_trait.mjs <trait=S> [burn=100] [obs=30] [seed=1] [key=value ...]
import { loadSim } from '../load.mjs';
const [trait = 'S', burn = 100, obs = 30, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = +v; }
const G = loadSim(over), P = G.PARAMETERS, ti = G.TRAITS.indexOf(trait);
const world = new G.World(), engine = new G.GameEngine(); engine.add(world);
for (let t = 0; t < burn * P.yearDays; t++) engine.update();
// tercile cutoffs from the current population
const gv = new Float32Array(G.NT), vals = world.goats.map(g => G.genotypicValues(g.genome, gv)[ti]).sort((a, b) => a - b);
const c1 = vals[(vals.length / 3) | 0], c2 = vals[(2 * vals.length / 3) | 0];
const bin = g => { const v = G.genotypicValues(g.genome, gv)[ti]; return v < c1 ? 0 : v < c2 ? 1 : 2; };
const S = [0, 1, 2].map(() => ({ days: 0, doeDays: 0, group: 0, deaths: new Array(G.CAUSE_NAMES.length).fill(0), conc: 0 }));
const origKill = world.kill.bind(world);
world.kill = (g, cause) => { if (!g.dead && !g.isKid()) S[bin(g)].deaths[cause]++; origKill(g, cause); };
const origMeiosis = G.meiosis;
for (let t = 0; t < obs * P.yearDays; t++) {
  const preg = new Set(world.goats.filter(g => g.gestation > 0).map(g => g.id));
  engine.update();
  for (const g of world.goats) {
    if (g.dead || g.isKid()) continue;
    const b = S[bin(g)]; b.days++; b.group += world.goatCount[g.y * world.W + g.x] - 1;
    if (g.sex === G.SEX_F && g.age >= P.femaleMinAge) { b.doeDays++; if (g.gestation === 1 && !preg.has(g.id)) b.conc++; }
  }
}
console.log(`${trait} terciles (cut ${c1.toFixed(2)} / ${c2.toFixed(2)}), ${obs} years after ${burn}-year burn-in, non-kids:`);
for (const [k, b] of S.entries()) {
  const yrs = b.days / P.yearDays, d = G.CAUSE_NAMES.map((c, i) => `${c} ${(b.deaths[i] / yrs).toFixed(3)}`).filter(x => !x.endsWith(' 0.000')).join(', ');
  console.log(`  ${['low ', 'mid ', 'high'][k]}: group ${(b.group / b.days).toFixed(2)} | deaths/goat-yr ${d} | conceptions/doe-yr ${(b.conc / (b.doeDays / P.yearDays)).toFixed(3)}`);
}
