// starveprobe.mjs — why herd goats starve: each herd starvation death from year `from` on, by kid (born in the herd,
// unweaned) or weaned, lean or growing season, kept at camp or not, and whether the camp's store (slop + fodder) held
// less than the goat's ration that day; plus, per herding camp, the share of lean days its store was empty.
//   node tools/starveprobe.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 600, from = 450, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const on = () => w.year >= +from;
const kids = new Set(), dead = {}, inc = (k) => { dead[k] = (dead[k] || 0) + 1; };
let herdDeaths = 0;
const birth = w.birth.bind(w);
w.birth = m => { const n = w.newborn.length; birth(m); if (m.herd >= 0 && w.newborn[n]) kids.add(w.newborn[n].id); };
const kill = w.kill.bind(w);
w.kill = (g, cause) => {
  if (on() && !g.dead && g.herd >= 0) {
    herdDeaths++;
    if (cause === G.CAUSE.starvation) {
      const c = w.camps[g.herd], store = (c.slop || 0) + (c.fodder || 0), ration = P.provision * Math.pow(g.size, 0.75);
      const who = kids.has(g.id) && g.age < P.weanAge ? 'kid' : 'weaned', season = w.growth === 0 ? 'lean' : 'growing';
      const kept = g.isKeptAtCamp() ? 'kept' : 'out', empty = store < ration ? 'storeShort' : 'storeHeld';
      inc('all'); inc(who); inc(season); inc(`${who}|${season}`); inc(`${who}|${season}|${kept}|${empty}`);
    }
  }
  kill(g, cause);
};
let leanCampDays = 0, leanCampEmpty = 0, herdGoatDays = 0;
for (let d = 1; d <= years * P.yearDays; d++) {
  e.update();
  if (!on()) continue;
  for (const g of w.goats) if (!g.dead && g.herd >= 0) herdGoatDays++;
  if (w.growth !== 0) continue;
  const held = new Set(); for (const g of w.goats) if (!g.dead && g.herd >= 0) held.add(g.herd);
  for (const id of held) { const c = w.camps[id]; leanCampDays++; if ((c.slop || 0) + (c.fodder || 0) < 1) leanCampEmpty++; }
}
const gy = herdGoatDays / P.yearDays, yrs = years - from;
console.log(`seed ${seed} ${kv.join(' ')} | years ${from}-${years} | mean herd ${(herdGoatDays / (yrs * P.yearDays)).toFixed(1)}`);
console.log(`herd deaths/y ${(herdDeaths / yrs).toFixed(1)}, starvation/y ${((dead.all || 0) / yrs).toFixed(1)} (${((dead.all || 0) / gy).toFixed(3)} per goat-year)`);
for (const [k, v] of Object.entries(dead).sort((a, b) => b[1] - a[1])) console.log(`  ${k.padEnd(36)} ${String(v).padStart(5)}  ${(v / (dead.all || 1)).toFixed(3)}`);
console.log(`lean camp-days with a herd ${leanCampDays}; store empty (< 1 fu) on ${leanCampEmpty} (${(leanCampEmpty / (leanCampDays || 1)).toFixed(3)})`);
