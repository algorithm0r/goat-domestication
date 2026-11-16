// pool.mjs — a pool of immigrant goats for immigrationRate (World.immigrate): run a population and sample its adult wild
// goats (genome alleles and learned fears) at the ends of chosen years.
//   node tools/pool.mjs <years> <out.json> <sampleFrom> <every> <perSample> [key=value ...]
// e.g. node tools/pool.mjs 1600 results/pools/wt2_seed101.json 1000 100 150 seed=101 herdingAt=1000000000 ...
// Sampling uses its own generator (seeded from the run's seed), so it does not touch the sim's random streams.
// tools/pools/merge.mjs joins the per-seed files into the pool the model reads.
import fs from 'fs'; import path from 'path';
import { loadSim } from '../load.mjs';
const [years, out, from, every, per, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
process.title = 'Animal Domestication pool';
const world = new G.World(), engine = new G.GameEngine();
engine.add(world);
let s = (P.seed * 2654435761) >>> 0;
const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
const goats = [], hb = process.env.CPUSLOT_HEARTBEAT;
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) {
  engine.update();
  if (t % P.yearDays !== 0) continue;
  const y = t / P.yearDays;   // years completed
  if (hb && y % 20 === 0) try { fs.writeFileSync(hb, JSON.stringify({ done: y, total: +years })); } catch (e) {}
  if (y < +from || (y - from) % +every !== 0) continue;
  const c = world.goats.filter(g => !g.dead && g.herd < 0 && g.age >= P.yearDays);
  for (let i = 0; i < Math.min(+per, c.length); i++) {
    const j = i + Math.floor(rnd() * (c.length - i)), g = c[j]; c[j] = c[i]; c[i] = g;
    goats.push({ g: Array.from(g.genome, v => +v.toFixed(5)), fw: +g.fearOfWolves.toFixed(4), fh: +g.fearOfHumans.toFixed(4), year: y });
  }
}
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({ info: { seed: P.seed, years: +years, from: +from, every: +every, per: +per, over }, goats }));
console.log(`${out}: ${goats.length} goats`);
