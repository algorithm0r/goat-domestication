// wolfmem.mjs — wolves' memory of finding goats (prey switching, MODEL C48): every `every` years from
// `from`, the mean memory s, the share of wolves with s < 0.1 and > 0.3, the share of bouts spent on
// goats, and recoveries (a wolf passing from s < 0.1 to s > 0.3) and collapses (the reverse) since the
// last line; plus goat kills by wolves.   node tools/wolfmem.mjs <years> <from> <every> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 400, from = 250, every = 10, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const state = new Map();                                       // wolf → 'low' | 'high' | 'mid'
let rec = 0, col = 0, bouts = 0, goatBouts = 0, kills = 0;
const kill = w.kill.bind(w);
w.kill = (g, c) => { if (!g.dead && c === G.CAUSE.predation && w.year >= +from) kills++; kill(g, c); };
for (let d = 1; d <= years * P.yearDays; d++) {
  e.update();
  if (w.year < +from) continue;
  for (const wf of w.wolves) {
    const s = wf.goatSuccess, prev = state.get(wf), now = s < 0.1 ? 'low' : s > 0.3 ? 'high' : (prev === 'low' || prev === 'high' ? prev : 'mid');
    if (prev === 'low' && now === 'high') rec++;
    if (prev === 'high' && now === 'low') col++;
    state.set(wf, now);
    if (wf.fullness < P.wolfHungry) { bouts++; if (wf.huntingGoats) goatBouts++; }
  }
  if (d % (every * P.yearDays) === 0) {
    const s = w.wolves.map(x => x.goatSuccess), m = s.reduce((a, b) => a + b, 0) / s.length;
    console.log(`y${w.year + 1} goats ${w.goats.length} | memory s mean ${m.toFixed(2)}, <0.1 ${(s.filter(x => x < 0.1).length / s.length).toFixed(2)}, >0.3 ${(s.filter(x => x > 0.3).length / s.length).toFixed(2)} | hungry days on goats ${(goatBouts / Math.max(1, bouts)).toFixed(2)} | recoveries ${rec} collapses ${col} | wolf kills ${kills}`);
    rec = col = bouts = goatBouts = kills = 0;
  }
}
