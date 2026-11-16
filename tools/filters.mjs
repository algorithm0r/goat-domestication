// filters.mjs — where does the herd's R come from? From year `from`, records the genetic R (expressed
// trait) of goats at each gate in and out of the herd:
//   in:   captured (at capture) and born in the herd (at birth; with mother's and father's R)
//   out:  lost on refetch, lost at the night stray test, and killed in the herd by cause
//   stay: refetched successfully
// plus yearly snapshots of wild adults and of the herd split by origin (captured, gsc 0; herd-born, gsc ≥ 1).
//   node tools/filters.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 800, from = 600, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS, TR = G.T_R;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const acc = {}, everHerd = new Set();
const add = (k, v) => { const a = acc[k] || (acc[k] = { n: 0, s: 0 }); a.n++; a.s += v; };
const on = () => w.year >= +from;

const capture = w.capture.bind(w);
w.capture = (g, h) => {
  if (on()) { add('in: captured', g.tr[TR]); const ex = everHerd.has(g.id); add(ex ? 'in: captured, ex-herd' : 'in: captured, never herded', g.tr[TR]); add('share: captures ex-herd', ex ? 1 : 0); add(ex ? 'fearH at capture, ex-herd' : 'fearH at capture, never herded', g.fearOfHumans); }
  capture(g, h);
};
const birth = w.birth.bind(w);
w.birth = m => {
  const before = w.newborn.length; birth(m);
  if (on() && m.herd >= 0) {
    const kid = w.newborn[before];
    add('in: herd-born kid', kid.tr[TR]); add('   its mother', m.tr[TR]);
    const f = w.goats.find(x => x.id === kid.fatherId) || null;
    if (f) add('   its father' + (kid.fatherWild ? ' (wild)' : ' (herd)'), f.tr[TR]);
  }
};
const refetch = w.refetch.bind(w);
w.refetch = (g, h) => {
  const was = g.herd; refetch(g, h);
  if (on() && was >= 0) {
    const d = Math.max(Math.abs(g.x - h.x), Math.abs(g.y - h.y));
    if (g.herd < 0) add('out: lost on refetch', g.tr[TR]); else add('stay: refetched', g.tr[TR]);
  }
};
const herdNight = w.herdNight.bind(w);
w.herdNight = () => {
  const inHerd = on() ? w.goats.filter(g => !g.dead && g.herd >= 0) : [];
  herdNight();
  for (const g of inHerd) if (g.herd < 0 && !g.dead) add('out: lost at night test', g.tr[TR]);
};
const kill = w.kill.bind(w);
w.kill = (g, cause) => { if (on() && !g.dead && g.herd >= 0 && g.age >= P.weanAge) add('out: killed, ' + G.CAUSE_NAMES[cause], g.tr[TR]); kill(g, cause); };

for (let d = 1; d <= years * P.yearDays; d++) {
  e.update();
  if (d % 30 === 0) for (const g of w.goats) if (!g.dead && g.herd >= 0) everHerd.add(g.id);
  if (d % P.yearDays === 0 && on()) for (const g of w.goats) {
    if (g.dead || g.age < P.weanAge) continue;
    if (g.herd < 0) {
      add('snap: wild (weaned)', g.tr[TR]);
      const near = w.camps.some(c => Math.max(Math.abs(g.x - c.x), Math.abs(g.y - c.y)) <= 6);
      add(near ? 'snap: wild ≤ 6 cells of a camp' : 'snap: wild > 6 cells from camps', g.tr[TR]);
      add(near ? 'share: near-camp wild ex-herd' : 'share: far wild ex-herd', everHerd.has(g.id) ? 1 : 0);
    }
    else add(g.gsc === 0 ? 'snap: herd, captured' : 'snap: herd, herd-born', g.tr[TR]);
  }
}
console.log(`seed ${seed}, years ${from}–${years}, ${kv.join(' ')}`);
for (const k of Object.keys(acc).sort()) console.log(`  ${k.padEnd(32)} n ${String(acc[k].n).padStart(7)}  ${k.startsWith('share') ? 'share' : k.startsWith('fearH') ? 'mean' : 'R'} ${(acc[k].s / acc[k].n).toFixed(3)}`);
