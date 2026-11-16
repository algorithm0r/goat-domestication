// huntsel.mjs — selection on R by hunters and wolves, from year `from`: R of goats killed by each cause
// vs R of the living (weaned) population, sampled daily at the hunt; for hunted goats, the share on
// cliffs and alarmed, and the same shares among goats a hunter could have seen (in a hunter's 3×3).
//   node tools/huntsel.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 340, from = 300, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed, herdingAt: 1e9 }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS, TR = G.T_R;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const on = () => w.year >= +from;
const acc = {};
const add = (k, v) => { const a = acc[k] || (acc[k] = { n: 0, s: 0 }); a.n++; a.s += v; };
const kill = w.kill.bind(w);
w.kill = (g, cause) => {
  if (on() && !g.dead && g.age >= P.weanAge) {
    const c = G.CAUSE_NAMES[cause], i = g.y * w.W + g.x;
    add(`killed ${c}: R`, g.tr[TR]);
    if (cause === G.CAUSE.hunted) { add('hunted: on cliff', w.escape[i] ? 1 : 0); add('hunted: alarmed', g.alarmed ? 1 : 0); add('hunted: fearH', g.fearOfHumans); }
  }
  kill(g, cause);
};
const hunt = w.humansHunt.bind(w);
w.humansHunt = () => {
  if (on()) for (const h of w.humans) {
    if (!h.hunting || h.attemptsLeft <= 0) continue;
    for (let y = Math.max(0, h.y - 1); y <= Math.min(w.H - 1, h.y + 1); y++)
      for (let x = Math.max(0, h.x - 1); x <= Math.min(w.W - 1, h.x + 1); x++) {
        const i = y * w.W + x;
        for (let o = w.cellStart[i]; o < w.cellStart[i + 1]; o++) {
          const g = w.goats[w.order[o]];
          if (g.dead || g.herd >= 0 || g.age < P.weanAge) continue;
          add('in a hunter 3x3: R', g.tr[TR]); add('in a hunter 3x3: on cliff', w.escape[i] ? 1 : 0); add('in a hunter 3x3: alarmed', g.alarmed ? 1 : 0);
        }
      }
  }
  hunt();
};
for (let d = 1; d <= years * P.yearDays; d++) {
  e.update();
  if (on() && d % 30 === 0) for (const g of w.goats) if (!g.dead && g.age >= P.weanAge) {
    add('population: R', g.tr[TR]); add('population: on cliff', w.escape[g.y * w.W + g.x] ? 1 : 0); add('population: fearH', g.fearOfHumans);
  }
}
console.log(`seed ${seed} ${kv.join(' ')}`);
for (const k of Object.keys(acc).sort()) console.log(`  ${k.padEnd(30)} n ${String(acc[k].n).padStart(8)}  ${(acc[k].s / acc[k].n).toFixed(3)}`);
