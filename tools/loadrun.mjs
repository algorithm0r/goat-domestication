// loadrun.mjs — read any run file (old plain .json, compact .json.gz) as the OLD plain object, exactly what
// JSON.parse of the plain file gives (same values, key order, absent keys). The codec is in runformat.mjs.
//   import { loadRun } from './loadrun.mjs';  const run = loadRun('results/x/R15_seed1.json.gz');  run.years[0].killoff ...
//   node tools/loadrun.mjs <file> [--json]   prints a summary, or (--json) the plain JSON text to stdout
import { loadRun } from './runformat.mjs';
import { fileURLToPath } from 'url';
export { loadRun };

// Years of the gene histograms (2026-11-13). Runs may record them every histPeriod years, and the census every
// reportingPeriod days, so index them by year, never by position. Census rows (samples[]) carry tick, year and day.
/** Year of each row of run.hist / run.histHerd: run.histYears when the run has it; older runs recorded one row at every
 *  year end, so the years of run.years (checked on 40 saved runs: rows = year records, year = index). */
export const histYears = run => Array.isArray(run.histYears) ? run.histYears : run.years.map(y => y.year);
/** Map year -> row of run.hist / run.histHerd, for the years that were recorded. */
export const histIndex = run => new Map(histYears(run).map((y, i) => [y, i]));
/** Last year of each run.histDepth record (each covers histDepth.every years ending there). */
export function depthYears(run) {
  const D = run.histDepth; if (!D) return [];
  if (D.years) return D.years;
  const first = D.herd && Object.values(D.herd)[0];
  return Array.from({ length: first ? first.length : 0 }, (_, k) => (k + 1) * D.every - 1);
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const [file, flag] = process.argv.slice(2);
  const run = loadRun(file);
  if (flag === '--json') process.stdout.write(JSON.stringify(run));
  else console.log(`${file}: ${run.years.length} years, ${run.samples.length} samples, year keys: ${Object.keys(run.years.at(-1) || {}).length}, extinct ${run.extinct}`);
}
