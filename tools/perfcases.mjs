// perfcases.mjs — the identical-output check list for speed work on the sim core (DEVLOG 2026-11-10), as a
// cpuslot submit list: one line per run of <tree>/tools/runyears.mjs, outputs to <outdir>/<case>.json.
//   node tools/perfcases.mjs <tree> <outdir> > runs.jsonl
// Run it once against the base commit's tree and once against the changed tree, then compare each pair with
// tools/samerun.mjs (every field but `seconds` must match).
import fs from 'fs'; import path from 'path';
const [tree, out] = process.argv.slice(2);
const S0 = JSON.parse(fs.readFileSync(path.join(tree, 'tools', 'pilot.json'), 'utf8')).S0;
const cases = [];
for (const s of [1, 2, 3]) cases.push([`S0_s${s}`, 520, s, {}]);
for (const kv of ['sireRule=random', 'sireRule=deep', 'sireRule=homebred herdMemory=3', 'sireRule=marked', 'exchangeN=2',
  'humansAt=1000000000', 'buckManagement=0', 'guarding=0', 'penning=0', 'cullRule=random', 'milkIntensity=0'])
  cases.push([kv.replace(/[ =]/g, '_'), 520, 1, Object.fromEntries(kv.split(' ').map(e => e.split('=')))]);
for (const kv of ['buckCull=calm', 'buckCull=youngMales', 'doeCull=large', 'doeCull=homebred', 'wildSireBlock=1', 'captureUntil=150'])
  cases.push([`smoke_${kv.replace(/=/g, '_')}`, 300, 1, { humansAt: 5, herdingAt: 10, ...Object.fromEntries([kv.split('=')]) }]);
for (const [name, years, seed, over] of cases) {
  const p = { ...S0, ...over, seed };
  console.log(JSON.stringify({ name, cmd: ['node', path.join(tree, 'tools', 'runyears.mjs'), String(years), path.join(out, `${name}.json`),
    ...Object.entries(p).map(([k, v]) => `${k}=${v}`)] }));
}
