// batch.mjs — run conditions × seeds in parallel via runyears.mjs.
//   node tools/batch.mjs <conditions.json> <outdir> <years> <seeds: N or a-b> [conc=10; cpuslot queues past its level] [only=H2,H3 or cond:seed pairs, e.g. H2:3,H4:1]
// Skips outputs that already exist, so an interrupted batch resumes. Log: <outdir>/batch.log
import { spawn } from 'child_process'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
const [condFile, out, years, seeds, conc = 10, only] = process.argv.slice(2);
const conds = JSON.parse(fs.readFileSync(condFile, 'utf8')); delete conds._doc;
const want = only ? only.split(',') : null;   // condition names, or cond:seed pairs for exact jobs
fs.mkdirSync(out, { recursive: true });
const log = s => fs.appendFileSync(path.join(out, 'batch.log'), `${new Date().toISOString()} ${s}\n`);
const jobs = [];
const [s0, s1] = String(seeds).includes('-') ? String(seeds).split('-').map(Number) : [1, +seeds];   // seeds: N (1..N) or a-b
for (let s = s0; s <= s1; s++) for (const c of Object.keys(conds)) if (!want || want.includes(c) || want.includes(`${c}:${s}`)) jobs.push({ c, s, file: path.join(out, `${c}_seed${s}.json`) });
let next = 0, running = 0, done = 0;
log(`batch ${jobs.length} jobs, conc ${conc}`);
const launch = () => {
  while (running < +conc && next < jobs.length) {
    const j = jobs[next++]; if (fs.existsSync(j.file)) { done++; continue; }
    running++;
    const args = [path.join(here, 'runyears.mjs'), years, j.file, `seed=${j.s}`, ...Object.entries(conds[j.c]).map(([k, v]) => `${k}=${v}`)];
    // each worker takes one slot of the shared desktop CPU pool (conventions §4a″); runs past its level queue there
    const p = spawn('cpuslot', ['run', '--tag', 'animal-domestication', '--desc', `${path.basename(out)} ${j.c} seed ${j.s}, ${years} y`, '--', process.execPath, ...args], { windowsHide: true }); let o = '';
    p.stdout.on('data', d => o += d); p.stderr.on('data', d => o += d);
    p.on('close', code => { running--; done++; log(`${code === 0 ? 'done' : 'FAIL'} ${j.c} seed ${j.s} (${done}/${jobs.length}) ${o.trim().split('\n').pop()}`); launch();
      if (running === 0 && next >= jobs.length) { log('ALL DONE'); console.log('ALL DONE', done); } });
  }
};
launch();
