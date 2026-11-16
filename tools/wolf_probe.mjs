// wolf_probe.mjs — instrument wolf bouts without changing the run (no rand draws added).
//   node tools/wolf_probe.mjs <years> <from-year> <out.json> <cond> [conditions.json] [key=value ...]
// From <from-year> on, per hunting wolf per bout sub-tick: goats of each kind in its 3×3 (encounters),
// whether it struck a herd or wild goat (from the wolfAtk tallies), and per bout: herd strikes, herd kills,
// whether a guard killed it. A bout runs from dusk sub-tick 0 to the last dawn sub-tick.
import fs from 'fs'; import path from 'path';
import { loadSim } from '../load.mjs';
const [years, from, out, cond, condFile = 'tools/conditions.json', ...kv] = process.argv.slice(2);
const conds = JSON.parse(fs.readFileSync(condFile, 'utf8'));
const over = { ...conds[cond] }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS, WP = G.World.prototype;
const S = { cond, over, enc: { herd: 0, wild: 0 }, strikes: { herd: 0, wild: 0 }, kills: { herd: 0, wild: 0 }, goatYears: { herd: 0, wild: 0 },
  wolfSubticks: 0, wolfSubticksNearHerd: 0, bouts: 0, boutsHuntingGoats: 0, herdBouts: 0, herdStrikeHist: {}, herdStrikesByRun: {},
  herdBoutKill: 0, herdBoutGuardKilled: 0,
  pre: { herd: 0, wild: 0 }, post: { herd: 0, wild: 0 }, near3: { herd: 0, wild: 0 }, goatSubticks: { herd: 0, wild: 0 },
  escapeShare: { herd: 0, wild: 0 }, campDist: { herd: 0, wild: 0 }, wolfCampDist: 0, wolfN: 0 };
// pre: hunting wolves whose 3×3 holds the goat, right after the wolves move and before goats step (where
// the wolves are); post: the same after the goats have stepped (what flight and avoidance leave);
// near3: hunting wolves within wolfSense (3 cells) before goats step.
let postPending = false;
const kind = g => g.herd >= 0 ? 'herd' : 'wild';
const origField = WP.buildWolfField;
WP.buildWolfField = function (hunting) {
  origField.call(this, hunting);
  if (!on || !hunting) return;
  const W = this.W, H = this.H, f = this.wolfField, cnt = this._wc || (this._wc = new Int16Array(W * H));
  cnt.fill(0);
  for (const w of this.wolves) if (w.huntingGoats && w.fullness < P.wolfHungry) { cnt[w.y * W + w.x]++; S.wolfN++; S.wolfCampDist += this.campDistOf(w.x, w.y); }
  for (const g of this.goats) {
    if (g.dead || g.ledBy) continue;
    const k = kind(g); S.pre[k] += f[g.y * W + g.x]; S.goatSubticks[k]++;
    if (this.escape[g.y * W + g.x]) S.escapeShare[k]++;
    S.campDist[k] += this.campDistOf(g.x, g.y);
    let n = 0;
    for (let y = Math.max(0, g.y - 3); y <= Math.min(H - 1, g.y + 3); y++) for (let x = Math.max(0, g.x - 3); x <= Math.min(W - 1, g.x + 3); x++) n += cnt[y * W + x];
    S.near3[k] += n;
  }
  postPending = true;
};
WP.campDistOf = function (x, y) { let d = 1e9; for (const c of this.camps) d = Math.min(d, Math.max(Math.abs(c.x - x), Math.abs(c.y - y))); return d; };
let on = false;
const tally = (ys, g) => { let a = 0, k = 0; for (const key in ys.wolfAtk) if (key.startsWith(g)) { a += ys.wolfAtk[key][0]; k += ys.wolfAtk[key][1]; } return [a, k]; };
const endBout = w => {
  if (!w._b) return;
  const b = w._b; w._b = null;
  if (b.hs > 0) {
    S.herdBouts++; S.herdStrikeHist[b.hs] = (S.herdStrikeHist[b.hs] || 0) + 1;
    const bin = b.hs >= 11 ? '11+' : b.hs >= 6 ? '6-10' : b.hs >= 3 ? '3-5' : String(b.hs);
    S.herdStrikesByRun[bin] = (S.herdStrikesByRun[bin] || 0) + b.hs;
    if (b.hk) S.herdBoutKill++; if (b.guarded) S.herdBoutGuardKilled++;
  }
};
const origTick = WP.wolfTick;
WP.wolfTick = function (phase, s) {
  if (on && phase === 'dusk' && s === 0) {
    for (const w of this.wolves) { endBout(w); w._b = { hs: 0, hk: 0, guarded: false }; }
    S.bouts += this.wolves.length;
  }
  origTick.call(this, phase, s);
  if (on && phase === 'dusk' && s === 0) for (const w of this.wolves) if (w.huntingGoats) S.boutsHuntingGoats++;
};
const origAtk = WP.wolfAttack;
WP.wolfAttack = function (w, phase) {
  if (!on) return origAtk.call(this, w, phase);
  const W = this.W, H = this.H; let nh = 0, nw = 0;
  if (postPending) { postPending = false; for (const g of this.goats) if (!g.dead && !g.ledBy) S.post[kind(g)] += this.wolfField[g.y * W + g.x]; }
  for (let y = Math.max(0, w.y - 1); y <= Math.min(H - 1, w.y + 1); y++)
    for (let x = Math.max(0, w.x - 1); x <= Math.min(W - 1, w.x + 1); x++) {
      const i = y * W + x;
      for (let o = this.cellStart[i]; o < this.cellStart[i + 1]; o++) { const g = this.goats[this.order[o]]; if (g.dead || g.ledBy) continue; if (g.herd >= 0) nh++; else nw++; }
    }
  S.enc.herd += nh; S.enc.wild += nw; S.wolfSubticks++; if (nh > 0) S.wolfSubticksNearHerd++;
  const [ha, hk] = tally(this.ys, 'herd'), [wa, wk] = tally(this.ys, 'wild'), killed0 = this.ys.wolvesKilled;
  origAtk.call(this, w, phase);
  const [ha2, hk2] = tally(this.ys, 'herd'), [wa2, wk2] = tally(this.ys, 'wild');
  S.strikes.herd += ha2 - ha; S.kills.herd += hk2 - hk; S.strikes.wild += wa2 - wa; S.kills.wild += wk2 - wk;
  if (w._b) {
    w._b.hs += ha2 - ha; w._b.hk += hk2 - hk;
    if (this.ys.wolvesKilled > killed0) { w._b.guarded = true; endBout(w); }
  }
};
const world = new G.World(), engine = new G.GameEngine(), dm = new G.DataManager(world, null, null);
engine.add(world); engine.add(dm);
for (let t = 1; t <= years * P.yearDays && world.goats.length > 0; t++) {
  if (!on && t > from * P.yearDays) on = true;
  engine.update();
  if (on && t % P.yearDays === 0) { const y = dm.years[dm.years.length - 1]; S.goatYears.herd += y.herded; S.goatYears.wild += y.goats - y.herded; }
}
for (const w of world.wolves) endBout(w);
S.years = years - from;
fs.mkdirSync(path.dirname(out), { recursive: true }); fs.writeFileSync(out, JSON.stringify(S, null, 1));
console.log(out, 'done');
