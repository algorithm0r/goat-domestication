// herdcauses.mjs — herd deaths (≥ probeMinAge y, default 1) by cause, sex and age band, from year `from` on: what shapes the
// herd kill-off profile.  node tools/herdcauses.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 500, from = 420, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(), dm = new G.DataManager(w, null, null); e.add(w); e.add(dm);
const minAge = over.probeMinAge ?? 1, bands = ['<1', '1-2.5', '2.5-4', '4+'], t = {};
const kill = w.kill.bind(w);
w.kill = (g, cause) => {
  if (!g.dead && g.herd >= 0 && w.year >= +from && g.age >= minAge * P.yearDays) {
    const a = g.age / P.yearDays, b = a < 1 ? 0 : a < 2.5 ? 1 : a < 4 ? 2 : 3;
    const k = `${g.sex === G.SEX_F ? 'F' : 'M'} ${G.CAUSE_NAMES[cause]}`;
    (t[k] || (t[k] = [0, 0, 0, 0]))[b]++;
  }
  kill(g, cause);
};
for (let d = 1; d <= years * P.yearDays; d++) e.update();
console.log(`deaths ≥ ${minAge} y in herds, years ${from}–${years}, seed ${seed}`);
console.log('sex cause'.padEnd(18) + bands.map(b => b.padStart(8)).join(''));
for (const k of Object.keys(t).sort()) console.log(k.padEnd(18) + t[k].map(n => String(n).padStart(8)).join(''));
