// probe_spring.mjs: by day of year, camp fodder store, standing veg near camps, herd condition by class, herd starvation.
// No random draws.   node probe_spring.mjs <years> <from> key=value ...
import { pathToFileURL } from 'url';
const SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/";
const { loadSim } = await import(pathToFileURL(SIM + 'load.mjs').href);
const [years, from, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='); const v = a.slice(i + 1); over[a.slice(0, i)] = isNaN(+v) ? v : +v; }
process.chdir(SIM);
const G = loadSim(over), P = G.PARAMETERS, Y = P.yearDays, F = G.SEX_F;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const B = 10, NB = Y / B, acc = Array.from({ length: NB }, () => ({ d: 0, fed: 0, spring: 0, store: 0, veg: 0, vegWild: 0, cls: {}, starve: 0, growth: 0 }));
let lastStarve = 0, lastFed = 0, lastSpring = 0;
for (let t = 1; t <= years * Y; t++) {
  engine.update();
  if (world.year < +from) { continue; }
  const a = acc[Math.floor(world.day / B)]; a.d++; a.growth += world.growth;
  const st = world.ys.herdDeaths ? world.ys.herdDeaths[G.CAUSE.starvation] : 0;
  a.starve += world.day === 0 ? st : st - lastStarve; lastStarve = st;
  const fd = world.ys.fodder, sp = world.ys.fodderSpring || 0;
  a.fed += Math.max(0, world.day === 0 ? fd : fd - lastFed); a.spring += Math.max(0, world.day === 0 ? sp : sp - lastSpring); lastFed = fd; lastSpring = sp;
  let s = 0, v = 0, nv = 0;
  for (const c of world.camps) {
    s += c.fodder + c.slop;
    for (let dy = -P.herdRange; dy <= P.herdRange; dy++) for (let dx = -P.herdRange; dx <= P.herdRange; dx++) {
      const x = c.x + dx, y = c.y + dy; if (x < 0 || y < 0 || x >= world.W || y >= world.H) continue;
      v += world.veg[y * world.W + x] - P.vegFloor; nv++;
    }
  }
  a.store += s / world.camps.length; a.veg += nv ? v / nv : 0;
  let wv = 0; for (let i = 0; i < world.veg.length; i++) wv += world.veg[i] - P.vegFloor; a.vegWild += wv / world.veg.length;
  for (const g of world.goats) {
    if (g.dead || g.herd < 0) continue;
    const k = g.age < Y ? 'young' : g.age >= g.breedAge ? (g.sex === F ? (g.gestation > 0 ? 'doePreg' : g.orphan() ? 'doeNurs' : 'doeDry') : 'buck') : 'yrlg';
    const r = a.cls[k] || (a.cls[k] = { n: 0, e: 0, low: 0 }); r.n++; const ec = g.E / g.reserveCap(); r.e += ec; if (ec < 0) r.low++;
  }
}
console.log('days  growth  fed/camp-day  springFed/camp-day  store/camp  veg(camp)  veg(all)  starve/yr | E/cap (share below 0): doePreg doeNurs doeDry buck young');
const yrs = +years - +from;
for (let i = 0; i < NB; i++) {
  const a = acc[i]; if (!a.d) continue;
  const c = k => a.cls[k] ? `${(a.cls[k].e / a.cls[k].n).toFixed(2)}(${(a.cls[k].low / a.cls[k].n).toFixed(2)})` : '-';
  console.log(`${String(i * B).padStart(3)}-${String(i * B + B - 1).padStart(3)} ${(a.growth / a.d).toFixed(2)}  ${(a.fed / a.d / world.camps.length).toFixed(0).padStart(7)}  ${(a.spring / a.d / world.camps.length).toFixed(0).padStart(7)}  ${(a.store / a.d).toFixed(0).padStart(9)}  ${(a.veg / a.d).toFixed(1).padStart(8)}  ${(a.vegWild / a.d).toFixed(1).padStart(7)}  ${(a.starve / yrs).toFixed(1).padStart(6)} | ${c('doePreg')} ${c('doeNurs')} ${c('doeDry')} ${c('buck')} ${c('young')}`);
}
