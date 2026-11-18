// diag_collapse.mjs: rerun one saved run and, from year `from`, log each camp's herd breeding state per year (reads
// world state only; draws no random numbers). Saves the DataManager's year records too, to check the rerun reproduces.
//   node diag_collapse.mjs <years> <from> <out.json> key=value ...
import fs from 'fs';
const SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/";
const { loadSim } = await import('file:///' + SIM + 'load.mjs');
const [years, from, out, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
process.chdir(SIM);
const G = loadSim(over), P = G.PARAMETERS, Y = P.yearDays, F = G.SEX_F, M = G.SEX_M;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const hb = process.env.CPUSLOT_HEARTBEAT;
const blank = () => ({ days: 0, n: 0, does: 0, bucks: 0, kids: 0, preg: 0, eligDays: 0, smallDays: 0, thinDays: 0,
  outOfSeason: 0, recvDays: 0, recvBuckNear: 0, conc: 0, doeE: 0, buckE: 0, nb: 0, nd: 0 });
const log = [];
let acc = null;
for (let t = 1; t <= years * Y && world.goats.length > 0; t++) {
  const pre = new Set(), herdPre = [];
  const y = Math.floor((t - 1) / Y);
  if (y >= +from) for (const g of world.goats) if (!g.dead && g.herd >= 0) {
    herdPre.push([g, g.herd, g.sex === M ? (g.age >= g.breedAge ? 'buck' : g.age >= Y ? 'youngM' : 'kidM') : g.age < Y ? 'kidF'
      : g.gestation > 0 || g.litterNursing() > 0 ? 'doePregNurse' : g.age >= g.breedAge ? 'doeOther' : 'youngF']);
    if (g.sex === F && g.gestation > 0) pre.add(g);
  }
  engine.update();
  if (y >= +from) for (const [g, h, cls] of herdPre) if (g.dead && g.cause === G.CAUSE.starvation) {
    if (!acc) acc = world.camps.map(blank);
    acc[h].starv = acc[h].starv || {}; acc[h].starv[cls] = (acc[h].starv[cls] || 0) + 1;
  }
  if (hb && t % (20 * Y) === 0) try { fs.writeFileSync(hb, JSON.stringify({ done: t / Y, total: +years })); } catch (e) {}
  if (y < +from) continue;
  if (!acc) acc = world.camps.map(blank);
  // bucks' cells, per camp
  const bc = world.camps.map(() => new Set());
  for (const g of world.goats) if (!g.dead && g.herd >= 0 && g.sex === M && g.age >= g.breedAge && !g.ledBy) bc[g.herd].add(g.y * world.W + g.x);
  const half0 = P.rutHalfBase;
  for (const g of world.goats) {
    if (g.dead || g.herd < 0) continue;
    const a = acc[g.herd]; a.n++;
    if (g.age < Y) a.kids++;
    if (g.sex === M && g.age >= g.breedAge) { a.bucks++; a.buckE += g.E / g.reserveCap(); a.nb++; }
    if (g.sex !== F || g.age < g.breedAge) continue;
    a.does++; a.doeE += g.E / g.reserveCap(); a.nd++;
    if (g.gestation > 0) { a.preg++; if (!pre.has(g) && g.gestation <= 1) a.conc++; continue; }
    if (g.age < g.recoverUntil) continue;
    const half = P.rutHalfBase + g.tr[G.T_T] * P.rutHalfRange;
    let d = Math.abs(world.day - P.rutPeakDay); if (d > Y / 2) d = Y - d;
    if (d > half) { a.outOfSeason++; continue; }
    a.eligDays++;
    if (g.size < P.breedSizeFrac * g.target) { a.smallDays++; continue; }
    if (g.E < P.breedCondition * g.reserveCap()) { a.thinDays++; continue; }
    if (g.receptive) {
      a.recvDays++;
      let near = false;
      for (let yy = g.y - 1; yy <= g.y + 1 && !near; yy++) for (let xx = g.x - 1; xx <= g.x + 1; xx++) if (bc[g.herd].has(yy * world.W + xx)) { near = true; break; }
      if (near) a.recvBuckNear++;
    }
  }
  for (let i = 0; i < acc.length; i++) { const a = acc[i]; a.days++;
    if (world.growth === 0) { a.leanDays = (a.leanDays || 0) + 1; if (world.camps[i].fodder < 1) a.emptyDays = (a.emptyDays || 0) + 1;
      if (world._rationF) { a.f0 = (a.f0 || 0) + world._rationF[i][0]; a.f1 = (a.f1 || 0) + world._rationF[i][1]; } } }
  if (t % Y === 0) {
    const bucks = world.camps.map(c => world.goats.filter(g => !g.dead && g.herd === c.id && g.sex === M && g.age >= g.breedAge)
      .map(g => ({ age: +(g.age / Y).toFixed(1), E: +(g.E / g.reserveCap()).toFixed(2), fert: +g.fertility().toFixed(2) })));
    const youngM = world.camps.map(c => world.goats.filter(g => !g.dead && g.herd === c.id && g.sex === M && g.age < g.breedAge).length);
    log.push({ year: y, camps: acc.map((a, i) => ({ n: a.n / a.days, does: a.does / a.days, bucks: a.bucks / a.days, kids: a.kids / a.days,
      doeE: a.nd ? a.doeE / a.nd : null, buckE: a.nb ? a.buckE / a.nb : null, eligDays: a.eligDays, smallDays: a.smallDays,
      thinDays: a.thinDays, recvDays: a.recvDays, recvBuckNear: a.recvBuckNear, conc: a.conc, bucksEnd: bucks[i], youngMEnd: youngM[i],
      starv: a.starv || {}, leanDays: a.leanDays || 0, emptyDays: a.emptyDays || 0, f0: a.leanDays ? (a.f0 || 0) / a.leanDays : null, f1: a.leanDays ? (a.f1 || 0) / a.leanDays : null })) });
    acc = null;
  }
}
fs.writeFileSync(out, JSON.stringify({ over, log, years: dm.years }));
console.log(`${out}: ${dm.years.length} years, ${log.length} logged`);
