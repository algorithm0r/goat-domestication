// incomeprobe.mjs — what one labour-day brings home, by role and season (calibration against forager data,
// 2026-10-28): per gatherer-day, the load delivered (mean, and by 30-day block of the year); per hunter-
// day, kills and fu. Wraps storeFodder (where loads and carcasses reach the camp).
//   node tools/incomeprobe.mjs <years> <skipYears> [key=value ...]
import { loadSim } from '../load.mjs';
const [years, skip, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const B = 12, blk = () => Math.min(B - 1, (world.day * B / P.yearDays) | 0);
const g = { days: Array(B).fill(0), fu: Array(B).fill(0), full: 0 }, h = { days: 0, kills: 0, fu: 0 };
const sf = world.storeFodder.bind(world);
world.storeFodder = function () {
  if (this.year >= +skip) for (const p of this.humans) {
    if (p.foraging) { const b = blk(); g.days[b]++; g.fu[b] += p.load || 0; if ((p.load || 0) >= P.foodLoad - 1e-9) g.full++; }
    if (p.role === 'hunt') { h.days++; if (p.meat > 0) { h.kills++; h.fu += p.meat; } }
  }
  return sf();
};
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) engine.update();
const tot = g.days.reduce((a, b) => a + b, 0), fu = g.fu.reduce((a, b) => a + b, 0);
console.log(`gatherer-days ${tot}: mean load ${(fu / tot).toFixed(2)}; full loads (${P.foodLoad}) ${(g.full / tot).toFixed(2)} of days`);
console.log('by 30-day block (day of year from 0): ' + g.days.map((d, b) => `${b * 30}:${d ? (g.fu[b] / d).toFixed(1) : '—'} (${d})`).join('  '));
console.log('wild goats by year: ' + dm.years.filter(y => y.year >= +skip - 5).map(y => `${y.year}:${y.goats - (y.herded || 0)}${y.econ && y.econ.shots !== undefined ? '/' + y.econ.shots + 's' + y.econ.shotKills + 'k' : ''}`).join(' '));
console.log(`hunter-days ${h.days}: kills ${h.kills} (1 per ${(h.days / Math.max(1, h.kills)).toFixed(0)} days), fu per kill ${(h.fu / Math.max(1, h.kills)).toFixed(1)}, fu per hunter-day ${(h.fu / h.days).toFixed(2)}`);
