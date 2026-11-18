// probe_offtake.mjs: at each offtake cull, the herd by class with keep values, and who goes. Draws no extra random numbers.
//   node probe_offtake.mjs <years> <from> key=value ...
import { pathToFileURL } from 'url';
const SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/";
const { loadSim } = await import(pathToFileURL(SIM + 'load.mjs').href);
const [years, from, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='); const v = a.slice(i + 1); over[a.slice(0, i)] = isNaN(+v) ? v : +v; }
process.chdir(SIM);
const G = loadSim(over), P = G.PARAMETERS, Y = P.yearDays, F = G.SEX_F;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const cls = g => g.age < Y ? (g.sex === F ? 'doeKid' : 'buckKid') : g.age >= g.breedAge ? (g.sex === F ? 'doe' : 'buck') : (g.sex === F ? 'yrlgF' : 'yrlgM');
const H = {}, C = {}; let calls = 0, on = false, last = null;
const h = k => H[k] || (H[k] = { n: 0, v: 0, age: 0 });
const origOrder = world.cullOrder.bind(world);
world.cullOrder = function (m) { origOrder(m); if (on) { calls++; last = m; for (const g of m) { const r = h(cls(g)); r.n++; r.v += -g._cullKey; r.age += g.age; } } };
const origTally = world.tallyCull.bind(world);
world.tallyCull = function (g, kind) { origTally(g, kind); if (on && kind === 'offtake') { const k = cls(g), r = C[k] || (C[k] = { n: 0, v: 0, age: 0 }); r.n++; r.v += -g._cullKey; r.age += g.age; } };
for (let d = 1; d <= years * Y && world.goats.length > 0; d++) { on = Math.floor((d - 1) / Y) >= +from; engine.update(); }
console.log(`cull events ${calls}`);
for (const k of ['buck', 'doe', 'yrlgM', 'yrlgF', 'buckKid', 'doeKid']) {
  const r = H[k] || { n: 0 }, c = C[k] || { n: 0 };
  console.log(`${k.padEnd(8)} in herd ${(r.n / calls).toFixed(1).padStart(5)} keep ${r.n ? (r.v / r.n).toFixed(2) : '-'}  age ${r.n ? (r.age / r.n / Y).toFixed(2) : '-'} y | culled ${c.n} keep ${c.n ? (c.v / c.n).toFixed(2) : '-'} age ${c.n ? (c.age / c.n).toFixed(0) : '-'} d`);
}
