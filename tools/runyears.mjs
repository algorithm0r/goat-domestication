// runyears.mjs — one headless run, saving the DataManager's year records and trait histograms.
//   node tools/runyears.mjs <years> <out.json> [key=value ...]
import fs from 'fs'; import path from 'path';
import { performance } from 'perf_hooks';
import { loadSim } from '../load.mjs';
const [years, out, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
process.title = 'Animal Domestication runyears';
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const t0 = performance.now();
// progress for the cpuslot dashboard (conventions §4a″): simulated years done, at most every few seconds; reads nothing back
const hb = process.env.CPUSLOT_HEARTBEAT; let hbAt = 0;
const beat = done => { try { fs.writeFileSync(hb, JSON.stringify({ done, total: +years })); } catch (e) {} };
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) {
  engine.update();
  if (hb && t % P.yearDays === 0 && performance.now() - hbAt > 3000) { hbAt = performance.now(); beat(t / P.yearDays); }
}
if (hb) beat(+years);
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({ project: 'Animal Domestication', params: P, years: dm.years, hist: dm.hist, histHerd: dm.histHerd, histDepth: dm.histDepth, samples: dm.samples,
  extinct: world.goats.length === 0, seconds: Math.round((performance.now() - t0) / 1000) }));
console.log(`${out}: ${dm.years.length} years, goats ${world.goats.length}, ${Math.round((performance.now() - t0) / 1000)} s`);
