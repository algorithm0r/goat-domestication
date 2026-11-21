// camp_probe.mjs: per-camp diagnostics for the herder-culture rules (2026-11-20). A probe, not an experiment runner.
//   node tools/camp_probe.mjs <years> <fromYear> [key=value ...]
// Runs the sim headless to <years>; from <fromYear> on, counts captures per camp (wrapping World.capture) and samples each
// camp's herd size, home-born breeding does (the selfMaint count) and selfMaint() at the end of every year. Prints a
// per-camp summary: mean herd, mean home does, share of years self-maintaining, captures. Output only; runs unchanged.
import { loadSim } from '../load.mjs';
const [years, from] = [+process.argv[2], +process.argv[3]];
const over = {};
for (const a of process.argv.slice(4)) { const i = a.indexOf('='); const v = a.slice(i + 1); over[a.slice(0, i)] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const C = w.camps.length, caps = new Array(C).fill(0), herd = new Array(C).fill(0), home = new Array(C).fill(0), self = new Array(C).fill(0);
let n = 0;
const cap0 = w.capture.bind(w);
w.capture = (g, h) => { if (w.year >= from) caps[h.camp.id]++; return cap0(g, h); };
for (let t = 1; t <= years * P.yearDays; t++) {
  e.update();
  if (t % P.yearDays === 0 && w.year >= from) {
    n++;
    for (let c = 0; c < C; c++) { herd[c] += w.herdCount[c]; home[c] += (w._homeDoes ? w._homeDoes[c] : 0); self[c] += w.selfMaint(c) ? 1 : 0; }
  }
}
for (let c = 0; c < C; c++)
  console.log(`camp ${c}: herd ${(herd[c] / n).toFixed(1)}, home-born breeding does ${(home[c] / n).toFixed(1)}, self-maintaining ${(100 * self[c] / n).toFixed(0)}% of years, captures ${caps[c]}`);
