// rangeprobe.mjs — penned herds at night: how far from camp the herd's goats are when herdNight runs (the stray
// check), how many are lost there, and how far from camp the herder took the herd that day; years from..years.
//   node tools/rangeprobe.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 440, from = 400, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const on = () => w.year >= +from;
const distN = {}, herderMax = {}; let nights = 0, goatNights = 0, lostNight = 0;
const night = w.herdNight.bind(w);
w.herdNight = () => {
  if (on()) {
    nights++;
    for (const g of w.goats) {
      if (g.dead || g.herd < 0 || g.ledBy || g.isKeptAtCamp() || g.isSheltered()) continue;
      const c = w.camps[g.herd], d = Math.max(Math.abs(g.x - c.x), Math.abs(g.y - c.y));
      goatNights++; distN[d] = (distN[d] || 0) + 1;
    }
    const before = w.ys.escaped; night(); lostNight += w.ys.escaped - before;
  } else night();
};
const pick = w.pickPasture.bind(w);
w.pickPasture = (c, h) => { pick(c, h); if (on()) { const d = Math.max(Math.abs(h.target.x - c.x), Math.abs(h.target.y - c.y)); herderMax[d] = (herderMax[d] || 0) + 1; } };
for (let d = 1; d <= years * P.yearDays; d++) e.update();
console.log(`seed ${seed} ${kv.join(' ')} | years ${from}-${years} | nights ${nights}, herd goat-nights out (not kept or sheltered) ${goatNights}, lost in the night check ${lostNight}`);
console.log('goat distance from camp at the night check:', JSON.stringify(distN));
console.log('pasture target distance from camp:', JSON.stringify(herderMax));
