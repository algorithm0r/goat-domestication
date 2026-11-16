// Headless batch runner. Loads the SAME browser sim files into the main V8 realm (load.mjs), runs
// reps, and writes self-describing packets via the standard DB client (direct transport).
//   node runner.mjs [--reps N] [--ticks N] [--db NAME] [--collection NAME] [--seed N]
import { createRequire } from 'module';
import { loadSim } from './load.mjs';

const require = createRequire(import.meta.url);
const { createDB } = require('./src/db.js');
const argv = process.argv.slice(2);
const flag = (n, d) => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : d; };
const reps = parseInt(flag('reps', '1'), 10);
const seed0 = flag('seed', null);

const G = loadSim();
const P = G.PARAMETERS;
process.title = 'Animal Domestication runner';
const limit = parseInt(flag('ticks', '0'), 10) || P.epoch;
const db = createDB(Object.assign({}, P.db, { transport: 'direct', db: flag('db', P.db.db) }));
const collection = flag('collection', null);

for (let r = 0; r < reps; r++) {
  const run = 'run_' + String(r).padStart(3, '0');
  P.seed = seed0 == null ? null : parseInt(seed0, 10) + r;
  db.config.run = run;
  const world = new G.World(), engine = new G.GameEngine();
  const dm = new G.DataManager(world, null, null);
  engine.add(world); engine.add(dm);
  for (let t = 1; t <= limit; t++) engine.update();
  const pkt = db.packet(P, { project: 'Animal Domestication', run, samples: dm.samples });
  const res = await db.insert(collection || run, pkt);
  console.log(run + ': meanVeg=' + world.meanVeg().toFixed(3) + '  saved=' + JSON.stringify(res));
}
await db.close();
