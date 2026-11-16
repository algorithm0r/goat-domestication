// storeprobe.mjs — check the shelf-life store books (storeWindows, EXPLOG 2026-10-28): every day, each
// camp total equals the sum of its batch queues, no batch is negative or past its shelf life, and queues
// are in expiry order; every year, plant food and meat balance (in = eaten + moved on + Δ store).
//   node tools/storeprobe.mjs <years> [key=value ...]
import { loadSim } from '../load.mjs';
const [years, ...kv] = process.argv.slice(2);
const over = { storeWindows: 1 }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const sum = q => q.reduce((a, b) => a + b[1], 0);
let bad = 0, checks = 0, maxQ = 0;
const fail = s => { if (bad++ < 10) console.log('FAIL', s); };
// meat in: hunted + slaughtered; wrap kill to count slaughter meat and storeFodder to count hunted meat
let hunted = 0, slaughtered = 0;
const sf = world.storeFodder.bind(world);
world.storeFodder = function () { for (const h of this.humans) if (h.role === 'hunt') hunted += h.meat || 0; return sf(); };
const st = world.stash.bind(world);
world.stash = function (c, k, x) { if (k === 'fresh' && x > 0 && this._inEcon) slaughtered += x; return st(c, k, x); };
const ce = world.campEconomy.bind(world);
world.campEconomy = function (...a) { this._inEcon = true; const r = ce(...a); this._inEcon = false; return r; };
let prev = null;
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) {
  const yBefore = world.year, ys = world.ys;
  const snap = prev || { pfood: 0, meat: 0, gathered: 0, plantEaten: 0, slop: 0, meatEaten: 0, dried: 0, driedLost: 0, hunted: 0, slaughtered: 0 };
  engine.update();
  for (const c of world.camps) {
    for (const [k, f] of Object.entries(G.STORE_FIELD)) {
      const q = c.q[k];
      maxQ = Math.max(maxQ, q.length);
      for (let i = 0; i < q.length; i++) {
        if (q[i][1] < -1e-9) fail(`negative batch ${k} t${t}`);
        if (q[i][0] <= world.tick) fail(`stale batch ${k} t${t} exp ${q[i][0]}`);
        if (i && q[i][0] < q[i - 1][0]) fail(`unsorted ${k} t${t}`);
      }
    }
    for (const f of ['pfood', 'slop', 'fodder']) { checks++; if (Math.abs(c[f] - sum(c.q[f])) > 1e-6 * (1 + c[f])) fail(`${f} total ${c[f]} vs queue ${sum(c.q[f])} t${t}`); }
    checks++; if (Math.abs(c.meat - sum(c.q.fresh) - sum(c.q.dried)) > 1e-6 * (1 + c.meat)) fail(`meat total ${c.meat} vs queues t${t}`);
  }
  // books each day (ys resets at year end, so check within a year on running totals)
  const pf = world.camps.reduce((a, c) => a + c.pfood, 0), mt = world.camps.reduce((a, c) => a + c.meat, 0);
  const cur = { demand: ys.demand, pfood: pf, meat: mt, gathered: ys.foodGathered, plantEaten: ys.plantEaten, slop: ys.slop, meatEaten: ys.meatEaten, dried: ys.dried, driedLost: ys.driedLost, hunted, slaughtered };
  if (prev && ys.demand >= prev.demand) {   // skip the day the year's stats reset
    const dIn = cur.gathered - snap.gathered, dOut = (cur.plantEaten - snap.plantEaten) / P.plantValue + (cur.slop - snap.slop) / P.slopValue;
    checks++; if (Math.abs(dIn - dOut - (cur.pfood - snap.pfood)) > 1e-6 * (1 + pf)) fail(`plant books t${t}: in ${dIn} out ${dOut} d ${cur.pfood - snap.pfood}`);
    // meat: in (hunted + slaughtered) − eaten − drying loss (fresh dried × (1 − dryValue)/dryValue) − dried lost = Δ store
    const mIn = (cur.hunted - snap.hunted) + (cur.slaughtered - snap.slaughtered), dryLoss = (cur.dried - snap.dried) * (1 - P.dryValue) / P.dryValue;
    const mOut = (cur.meatEaten - snap.meatEaten) + dryLoss + (cur.driedLost - snap.driedLost);
    checks++; if (Math.abs(mIn - mOut - (cur.meat - snap.meat)) > 1e-6 * (1 + mt + mIn)) fail(`meat books t${t}: in ${mIn} out ${mOut} d ${cur.meat - snap.meat}`);
  }
  prev = { ...cur, demand: ys.demand };
}
const y = dm.years.slice(-5).map(r => r.econ && `y${r.year} unmetQ ${r.econ.unmetQ} plantStore ${r.econ.plantStore} meatStore ${r.econ.meatStore} dried ${r.econ.dried} driedLost ${r.econ.driedLost} slop ${r.econ.slopMade} heap ${r.econ.heap} fodderLost ${r.econ.fodderLost}`);
console.log(y.join('\n'));
console.log(`${checks} checks, ${bad} failures, longest queue ${maxQ}`);
