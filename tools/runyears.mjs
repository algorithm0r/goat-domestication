// runyears.mjs — one headless run, saving the DataManager's year records and trait histograms.
//
// Experiment data protocol (conventions §4, db.js v2; from 2026-11-18):
//   node tools/runyears.mjs --register <slug> "<one-line question>"
//       claims the next experiment number (e.g. exp001) in Mongo's registry and prints an EXPLOG stub.
//   node tools/runyears.mjs <years> --exp expNNN --run <name> seed=S [key=value ...]
//       refuses to run until EXPLOG.md has a "## expNNN" heading. Saves the run to Mongo
//       (animalDomestication.expNNN_<slug>, the record) and results/expNNN_<slug>/<name>.json (the plain JSON copy),
//       with PARAMETERS.id = {project, exp, run, seed, commit, dirty, host, started}. Run names: see DEVPLAN "Run names".
//       Experiment runs are lean by default (LEAN below: the diagnostics no table reads are off, gene histograms every
//       5 years, the census yearly), so a 1600-year run is about 9 MB of BSON, under Mongo's 16 MB; any key=value
//       overrides them, and they are saved in the run's parameters like every other setting.
//   node tools/runyears.mjs <years> --scratch --run <name> [key=value ...]
//       a probe or smoke run: animalDomestication_scratch and results/_scratch.
// Legacy (before the protocol; kept so old EXPLOG entries reproduce):
//   node tools/runyears.mjs <years> <out.json | out.json.gz> [key=value ...]
//       out.json writes the plain JSON; out.json.gz the compact gzipped form (tools/runformat.mjs, lossless). Read either
//       with tools/loadrun.mjs or tools/loadrun.py. Every setting at its default, so nothing is thinned.
// Launch batches through cpuslot (conventions §4a″).
import fs from 'fs'; import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';
import { saveRun } from './runformat.mjs';
import { performance } from 'perf_hooks';
import { loadSim } from '../load.mjs';

const require = createRequire(import.meta.url);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const argv = process.argv.slice(2);
const has = n => argv.includes('--' + n);
const flag = n => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : null; };
const die = m => { console.error(m); process.exit(2); };
const LEAN = { logKilloff: 0, logWolfAtk: 0, logKidLife: 0, logKidDeathCause: 0, logHistDepth: 0, histPeriod: 5, reportingPeriod: 360 };

const openDB = (scratch, P) => {                                   // P: the loaded PARAMETERS (loadSim again would reset them)
  const { createDB } = require('../src/db.js');
  const base = createDB(Object.assign({}, P.db, { transport: 'direct', project: 'Animal Domestication', repo: ROOT,
    results: path.join(ROOT, 'results', scratch ? '_scratch' : '') }));
  return scratch ? base.scratch() : base;
};

if (has('register')) {
  const i = argv.indexOf('--register'), slug = argv[i + 1], question = argv[i + 2];
  if (!slug || !question) die('usage: node tools/runyears.mjs --register <slug> "<one-line question>"');
  const db = openDB(false, loadSim({}).PARAMETERS), ex = await db.experiment(slug, { question });
  console.log(`${ex.label} registered as animalDomestication.${ex.collection}\n\nAdd to EXPLOG.md before running:\n`);
  console.log(`## ${ex.label} — ${question}\n**Pre-registered:** ${new Date().toISOString().slice(0, 10)}\n**Settings:**\n**Seeds / years:**\n**Prediction:**\n`);
  await db.close(); process.exit(0);
}

// positional: <years> [out] ; then key=value overrides; --flags with values are skipped
const pos = [], kv = [];
for (let i = 0; i < argv.length; i++) {
  if (argv[i].startsWith('--')) { if (['exp', 'run'].includes(argv[i].slice(2))) i++; continue; }
  (argv[i].includes('=') ? kv : pos).push(argv[i]);
}
const years = +pos[0], out = pos[1], label = flag('exp'), scratch = has('scratch'), runName = flag('run');
const protocol = !!(label || scratch);
if (!years) die('usage: see the header of tools/runyears.mjs');
if (protocol && !runName) die('--exp and --scratch need --run <name>');
if (!protocol && !out) die('legacy mode needs an output path (or use --exp expNNN --run NAME)');
if (label) {
  if (!/^exp\d{3,}$/.test(label)) die(`--exp wants expNNN, got ${label}`);
  const text = fs.existsSync(path.join(ROOT, 'EXPLOG.md')) ? fs.readFileSync(path.join(ROOT, 'EXPLOG.md'), 'utf8') : '';
  if (!new RegExp('^##\\s+' + label + '\\b', 'm').test(text)) die(`EXPLOG.md has no "## ${label}" entry. Pre-register before running (conventions §4).`);
}
const over = protocol ? Object.assign({}, LEAN) : {};
for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
process.title = 'Animal Domestication runyears';

let db = null, run = null;
if (protocol) {
  db = openDB(scratch, P);
  const ex = label ? await db.experiment(label) : await db.experiment('probe', { question: 'scratch run' });
  run = ex.run(P, { name: runName, seed: P.seed });
  await run.start();
}
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const t0 = performance.now();
// progress for the cpuslot dashboard (conventions §4a″): simulated years done, at most every few seconds; reads nothing back
const hb = process.env.CPUSLOT_HEARTBEAT; let hbAt = 0;
const beat = done => { try { fs.writeFileSync(hb, JSON.stringify({ done, total: years })); } catch (e) {} };
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) {
  engine.update();
  if (hb && t % P.yearDays === 0 && performance.now() - hbAt > 3000) { hbAt = performance.now(); beat(t / P.yearDays); }
}
if (hb) beat(years);
const data = { years: dm.years, hist: dm.hist, histHerd: dm.histHerd, histYears: dm.histYears, histDepth: dm.histDepth, samples: dm.samples,
  extinct: world.goats.length === 0, seconds: Math.round((performance.now() - t0) / 1000) };
if (protocol) {
  const res = await run.save(data);
  console.log(`${label || 'scratch'}/${runName}: ${dm.years.length} years, goats ${world.goats.length}, ${data.seconds} s, ${(res.bytes / 1e6).toFixed(1)} MB`);
  await db.close();
} else {
  fs.mkdirSync(path.dirname(out), { recursive: true });
  saveRun(out, Object.assign({ project: 'Animal Domestication', params: P }, data));
  console.log(`${out}: ${dm.years.length} years, goats ${world.goats.length}, ${data.seconds} s`);
}
