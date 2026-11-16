// tools/trace_flow.mjs (2026-11-12): rerun one run and, from year `from`, trace the goats crossing between herd and wild and
// the goats each cull takes. Wraps World.capture, World.kill, cullSurplusBucks and cullToFodder; reads state
// only and draws no random numbers, so the run is the same run (checked: year records saved for comparison).
//   node tools/trace_flow.mjs <years> <from> <out.json> key=value ...
import fs from 'fs';
import { fileURLToPath, pathToFileURL } from 'url'; import path from 'path';
const SIM = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..') + '/';
const { loadSim } = await import(pathToFileURL(SIM + 'load.mjs').href);
const [years, from, out, ...kv] = process.argv.slice(2);
const over = {}; for (const a of kv) { const i = a.indexOf('='), k = a.slice(0, i), v = a.slice(i + 1); over[k] = isNaN(+v) ? v : +v; }
process.chdir(SIM);
const G = loadSim(over), P = G.PARAMETERS, Y = P.yearDays, F = G.SEX_F, M = G.SEX_M, TR = G.T_R;
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
const hb = process.env.CPUSLOT_HEARTBEAT;

let on = false, ctx = 'offtake', orphanCand = null;
const escapedIds = new Set();                 // herd goats that went wild (to spot recaptures)
const blank = () => ({
  capt: { n: 0, orphan: 0, try: 0, recapt: 0, herdAnc: 0, R: 0, fear: 0, kid: 0, doe: 0, buck: 0 },
  esc: { n: 0, captSelf: 0, herdBorn: 0, R: 0, fear: 0, kid: 0, adult: 0, gscSum: 0 },
  cull: { offtake: blank2(), surplus: blank2(), winter: blank2() },
  starv: blank2(),
  herd: { days: 0, n: 0, captSelf: 0, gsc1: 0, R: 0, Rcapt: 0, nCapt: 0, Rborn: 0, nBorn: 0, kidsBorn: 0, kidsDamCapt: 0 },
});
function blank2() { return { n: 0, kid: 0, doe: 0, buck: 0, other: 0, captSelf: 0, R: 0 }; }
let acc = blank();
const cls = g => g.age < Y ? 'kid' : g.sex === F && g.age >= g.breedAge ? 'doe' : g.sex === M && g.age >= g.breedAge ? 'buck' : 'other';

const origCapture = world.capture.bind(world);
world.capture = function (g, h) {
  if (on) {
    const a = acc.capt; a.n++;
    if (g === orphanCand) a.orphan++; else a.try++;
    if (escapedIds.has(g.id)) a.recapt++;
    if (g.wv && g.wv[0] < 1 - 1e-9) a.herdAnc++;            // a wild goat with some herd-born ancestry
    a.R += g.tr[TR]; a.fear += g.fearOfHumans;
    const c = cls(g); if (c === 'kid') a.kid++; else if (c === 'doe') a.doe++; else if (c === 'buck') a.buck++;
  }
  return origCapture(g, h);
};
const origKill = world.kill.bind(world);
world.kill = function (g, cause) {
  if (on && !g.dead && g.herd >= 0) {
    const b = cause === G.CAUSE.culled ? acc.cull[ctx] : cause === G.CAUSE.starvation ? acc.starv : null;
    if (b) { b.n++; b[cls(g)]++; if (g.gsc === 0) b.captSelf++; b.R += g.tr[TR]; }
  }
  if (cause === G.CAUSE.hunted) orphanCand = g.orphan();
  return origKill(g, cause);
};
const origSurplus = world.cullSurplusBucks.bind(world);
world.cullSurplusBucks = function (m) { ctx = 'surplus'; try { return origSurplus(m); } finally { ctx = 'offtake'; } };
const origWinter = world.cullToFodder.bind(world);
world.cullToFodder = function (m, c) { ctx = 'winter'; try { return origWinter(m, c); } finally { ctx = 'offtake'; } };

const log = [];
const herdPre = new Map();
for (let t = 1; t <= years * Y && world.goats.length > 0; t++) {
  const y = Math.floor((t - 1) / Y);
  on = y >= +from;
  herdPre.clear();
  if (on) for (const g of world.goats) if (!g.dead && g.herd >= 0) herdPre.set(g, true);
  const nBefore = world.goats.length;
  engine.update();
  if (hb && t % (20 * Y) === 0) try { fs.writeFileSync(hb, JSON.stringify({ done: t / Y, total: +years })); } catch (e) {}
  if (!on) continue;
  for (const g of herdPre.keys()) if (!g.dead && g.herd < 0) {
    const e = acc.esc; e.n++; escapedIds.add(g.id);
    if (g.gsc === 0) e.captSelf++; else e.herdBorn++;
    e.gscSum += Math.max(0, g.gsc); e.R += g.tr[TR]; e.fear += g.fearOfHumans;
    if (g.age < Y) e.kid++; else e.adult++;
  }
  const H = acc.herd; H.days++;
  for (const g of world.goats) {
    if (g.dead || g.herd < 0) continue;
    H.n++; H.R += g.tr[TR];
    if (g.gsc === 0) { H.captSelf++; H.Rcapt += g.tr[TR]; H.nCapt++; } else { H.Rborn += g.tr[TR]; H.nBorn++; }
    if (g.gsc === 1) H.gsc1++;
    if (g.age === 0) { H.kidsBorn++; if (g.gsc === 1) H.kidsDamCapt++; }   // born today (age counted in days)
  }
  if (t % Y === 0) { log.push({ year: y, ...JSON.parse(JSON.stringify(acc)) }); acc = blank(); }
}
fs.writeFileSync(out, JSON.stringify({ over, log, years: dm.years }));
console.log(`${out}: ${dm.years.length} years, ${log.length} traced`);
