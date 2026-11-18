// keepvalue.mjs — the opportunity cull's keep value, broken into its parts, for every herd goat at one moment.
//   node tools/keepvalue.mjs <years> <out.json> [key=value ...]
// Runs the sim <years> years, then for each camp's herd recomputes World.cullByOpportunity term by term (growth,
// kids, sire share, feed, meat at risk, last-breeder boost) and checks the sum against the sim's own keep value
// (cullNoise set to 0 for that one call). Writes every goat's row to <out.json> and prints a table by sex and age.
import fs from 'fs'; import path from 'path';
import { loadSim } from '../load.mjs';
const [years, out, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS, Y = P.yearDays;
if (P.cullRule !== 'opportunity') throw new Error('keepvalue needs cullRule=opportunity');
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
for (let t = 1; t <= years * Y && world.goats.length > 0; t++) engine.update();

const herds = new Map();
for (const g of world.goats) if (!g.dead && g.herd >= 0) { if (!herds.has(g.herd)) herds.set(g.herd, []); herds.get(g.herd).push(g); }
const rows = []; let maxErr = 0;
for (const [cid, m] of herds) {
  // the sim's inputs, as in cullByOpportunity
  const adult = [0, 0], an = [0, 0]; let does = 0, bucks = 0;
  for (const g of m) {
    if (g.age >= (P.creditAge || P.adultAge)) { adult[g.sex] += g.size; an[g.sex]++; }
    if (g.sex === G.SEX_F && g.age >= P.femaleMinAge) does++;
    if (g.sex === G.SEX_M && g.age >= P.maleMinAge) bucks++;
  }
  const adultSize = [an[0] ? adult[0] / an[0] : 1, an[1] ? adult[1] / an[1] : 1];
  const camp = world.camps[cid], record = camp && camp.record ? camp.record : null;
  const ref = P.growthCredit === 'max' ? [0, 1].map(s => m.reduce((x, g) => g.sex === s && g.size > x ? g.size : x, 0) || adultSize[s])
    : P.growthCredit !== 'cull' ? adultSize : [0, 1].map(s => camp && camp.cullRef && !isNaN(camp.cullRef[s]) ? camp.cullRef[s] : adultSize[s]);
  const herdRate = record && record.yrs > 0 ? record.kids / record.yrs : P.priorKidRate;
  const herdMilk = record && record.yrs > 0 ? record.milk / record.yrs : 0;
  const sires = P.sireRule !== 'oldest' ? world.siresOf(cid)
    : m.filter(g => g.sex === G.SEX_M && g.age >= P.maleMinAge).sort((a, b) => b.age - a.age).slice(0, P.keepSires);
  const heirs = m.filter(g => g.sex === G.SEX_M && !sires.includes(g) && g.age >= P.weanAge).sort((a, b) => b.age - a.age).slice(0, P.keepHeirs);
  for (const g of m) {
    const ay = g.age / Y, r = { camp: cid, sex: g.sex ? 'M' : 'F', age: +ay.toFixed(2), size: +g.size.toFixed(3), target: +g.target.toFixed(3) };
    const credit = P.growthCredit === 'model' ? (P.growthCurve === 'linear' ? 'herd' : 'own') : P.growthCredit;
    r.growth = P.growthCurve === 'vb' ? g.vbGain(Y) : P.growthCurve === 'ogm' ? g.ogmGain(Y)
      : P.growthCurve === 'curved' ? (credit === 'own' ? g.curveGain(Y) : g.curveGainTo(ref[g.sex], Y))
      : Math.max(0, Math.min((credit === 'own' ? g.target : ref[g.sex]) - g.size, P.growthAbs * Y));
    r.kids = 0; r.milk = 0;
    if (g.sex === G.SEX_F && ay < P.senescenceAge) {
      const yrs = Math.max(0, (g.age - P.femaleMinAge) / Y), own = yrs > 0 ? g.kids / yrs : 0, wOwn = yrs / (yrs + P.recordWeight);
      const ownMilk = yrs > 0 ? g.milkYield / yrs : 0;
      let kv = 0, mv = 0, surv = 1;
      for (let k = 0; k < P.keepHorizon && ay + k < P.senescenceAge; k++) {
        const ac = Math.min(P.ageClasses - 1, Math.floor(ay + k));
        const classRate = record && record.byAge[ac].yrs > 1 ? record.byAge[ac].kids / record.byAge[ac].yrs : herdRate;
        kv += surv * (wOwn * own + (1 - wOwn) * classRate) * (k === 0 && g.age < P.femaleMinAge ? 0.5 : 1);
        if (P.milkValue > 0) {
          const classMilk = record && record.byAge[ac].yrs > 1 ? record.byAge[ac].milk / record.byAge[ac].yrs : herdMilk;
          mv += surv * (wOwn * ownMilk + (1 - wOwn) * classMilk) * (k === 0 && g.age < P.femaleMinAge ? 0.5 : 1);
        }
        surv *= 1 - P.adultMortality;
      }
      r.kids = P.kidValue * kv;
      if (P.milkValue > 0) r.milk = P.milkValue * mv / P.meatYield;
    }
    r.role = sires.includes(g) ? 'sire' : heirs.includes(g) ? 'heir' : '';
    r.sire = r.role === 'sire' ? P.kidValue * herdRate * does / Math.max(1, sires.length)
      : r.role === 'heir' ? 0.5 * P.kidValue * herdRate * does / Math.max(1, sires.length) : 0;
    const sz = P.cullSizeNeutral === 'sex' ? g.sexMult() : P.cullSizeNeutral ? 1 : g.size;
    r.feed = -P.feedCost * Math.pow(sz, 0.75);
    const hz = P.adultMortality + (ay < 1 ? P.juvMortality : 0) + (ay > P.senescenceAge ? P.senescenceRate * (ay - P.senescenceAge) : 0);
    r.risk = -Math.min(1, hz) * sz;
    r.flight = P.flightCost > 0 ? -P.flightCost * g.tr[G.T_R] * g.fearOfHumans : 0;
    r.last = P.lastBreederValue > 0 && ((g.sex === G.SEX_F && g.age >= P.femaleMinAge && does <= P.lastBreeders) ||
      (g.sex === G.SEX_M && g.age >= P.maleMinAge && bucks <= P.lastBreeders)) ? P.lastBreederValue : 0;
    r.total = r.growth + r.kids + r.milk + r.sire + r.feed + r.risk + r.flight + r.last;
    r._g = g; rows.push(r);
  }
  // check against the sim's own keep value, noise off
  const noise = P.cullNoise; P.cullNoise = 0; world.cullByOpportunity(m.slice()); P.cullNoise = noise;
  for (const r of rows) if (r.camp === cid) maxErr = Math.max(maxErr, Math.abs(-r._g._cullKey - r.total));
}
// rank within each herd: rank 1 = eaten first
for (const cid of herds.keys()) {
  const rs = rows.filter(r => r.camp === cid).sort((a, b) => a.total - b.total);
  rs.forEach((r, i) => { r.rank = i + 1; r.pct = +((i + 0.5) / rs.length).toFixed(3); });
}
for (const r of rows) delete r._g;
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({ params: P, year: world.year, day: world.day, maxErr, rows }));

const f = x => (x >= 0 ? '+' : '') + x.toFixed(3);
console.log(`year ${world.year} day ${world.day}; ${herds.size} herds, ${rows.length} herd goats; check against the sim: max |diff| ${maxErr.toExponential(1)}`);
console.log('class            n  growth   kids   sire   feed   risk  total  eaten-first share (bottom 15% of its herd)');
const classes = [['F', 0, 1], ['F', 1, 2], ['F', 2, 3], ['F', 3, 5], ['F', 5, 9], ['F', 9, 99], ['M', 0, 1], ['M', 1, 2], ['M', 2, 3], ['M', 3, 5], ['M', 5, 99]];
for (const [s, a0, a1] of classes) {
  const rs = rows.filter(r => r.sex === s && r.age >= a0 && r.age < a1 && r.role !== 'sire'); if (!rs.length) continue;
  const mean = k => rs.reduce((t, r) => t + r[k], 0) / rs.length;
  console.log(`${s} ${a0}-${a1 === 99 ? '+' : a1}`.padEnd(12) + String(rs.length).padStart(5) + ['growth', 'kids', 'sire', 'feed', 'risk', 'total'].map(k => f(mean(k)).padStart(7)).join('')
    + `  ${(rs.filter(r => r.pct < 0.15).length / rs.length).toFixed(2)}`);
}
const sr = rows.filter(r => r.role === 'sire');
if (sr.length) { const mean = k => sr.reduce((t, r) => t + r[k], 0) / sr.length;
  console.log('M sires'.padEnd(12) + String(sr.length).padStart(5) + ['growth', 'kids', 'sire', 'feed', 'risk', 'total'].map(k => f(mean(k)).padStart(7)).join('')); }
