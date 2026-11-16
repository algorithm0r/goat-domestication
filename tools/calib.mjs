// calib.mjs — run named parameter variants in parallel (one process each, via probe.mjs) and print
// each one's final-year line side by side.   node tools/calib.mjs <years> '{"name":{...},...}'
import { spawn } from 'child_process';
import path from 'path'; import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url));
const [years, json] = process.argv.slice(2);
const variants = JSON.parse(json);
const jobs = Object.entries(variants).map(([name, over]) => new Promise(res => {
  const args = [path.join(here, 'probe.mjs'), years, years, over.seed ?? 1, ...Object.entries(over).filter(([k]) => k !== 'seed').map(([k, v]) => k + '=' + v)];
  const p = spawn(process.execPath, args, { windowsHide: true }); let out = '';
  p.stdout.on('data', d => out += d); p.stderr.on('data', d => out += d);
  p.on('close', () => res([name, out.trim().split('\n')]));
}));
for (const [name, lines] of await Promise.all(jobs)) console.log(`── ${name}\n   ${lines.join('\n   ')}`);
