// attr_batch.mjs — run the same conditions × seeds on several code points (git commits), each with its own
// code, in parallel from one job queue (rebuild attribution, EXPLOG 2026-10-25).
//   node tools/attr_batch.mjs <conditions.json> <outdir> <years> <seeds> <conc> <commit> [commit ...]
// Each commit gets a git worktree under <outdir>/_wt/<commit>; runs use that worktree's tools/runyears.mjs.
// Outputs <outdir>/<commit>/<cond>_seed<N>.json; skips existing outputs (resumable). Log: <outdir>/batch.log
import { spawn, execFileSync } from 'child_process'; import fs from 'fs'; import path from 'path';
const [condFile, out, years, seeds, conc, ...commits] = process.argv.slice(2);
const conds = JSON.parse(fs.readFileSync(condFile, 'utf8')); delete conds._doc;
fs.mkdirSync(out, { recursive: true });
const log = s => fs.appendFileSync(path.join(out, 'batch.log'), `${new Date().toISOString()} ${s}\n`);
const jobs = [];
for (const c of commits) {
  const wt = path.resolve(out, '_wt', c);
  if (!fs.existsSync(wt)) execFileSync('git', ['worktree', 'add', '--detach', wt, c], { stdio: 'ignore' });
  fs.mkdirSync(path.join(out, c), { recursive: true });
  for (let s = 1; s <= +seeds; s++) for (const k of Object.keys(conds)) jobs.push({ c, wt, k, s, file: path.resolve(out, c, `${k}_seed${s}.json`) });
}
// interleave so every code point progresses together (a stopped batch still compares like with like)
jobs.sort((a, b) => a.s - b.s || Object.keys(conds).indexOf(a.k) - Object.keys(conds).indexOf(b.k) || commits.indexOf(a.c) - commits.indexOf(b.c));
let next = 0, running = 0, done = 0;
log(`attr batch ${jobs.length} jobs, conc ${conc}, commits ${commits.join(' ')}`);
const launch = () => {
  while (running < +conc && next < jobs.length) {
    const j = jobs[next++]; if (fs.existsSync(j.file)) { done++; continue; }
    running++;
    const args = [path.join(j.wt, 'tools', 'runyears.mjs'), years, j.file, `seed=${j.s}`, ...Object.entries(conds[j.k]).map(([k, v]) => `${k}=${v}`)];
    const p = spawn(process.execPath, args, { cwd: j.wt, windowsHide: true }); let o = '';
    p.stdout.on('data', d => o += d); p.stderr.on('data', d => o += d);
    p.on('close', code => { running--; done++; log(`${code === 0 ? 'done' : 'FAIL'} ${j.c} ${j.k} seed ${j.s} (${done}/${jobs.length}) ${o.trim().split('\n').pop()}`); launch();
      if (running === 0 && next >= jobs.length) { log('ALL DONE'); console.log('ALL DONE', done); } });
  }
};
launch();
