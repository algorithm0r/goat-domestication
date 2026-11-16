// kidfate.mjs — a herd's books, from year `from`: per goat-year, births, captures, deaths (kids before
// weaning and weaned goats, by cause) and escapes (goats leaving the herd alive); kid survival; births
// per doe-year; doe share.   node tools/kidfate.mjs <years> <from> <seed> [k=v ...]
import { loadSim } from '../load.mjs';
const [years = 470, from = 430, seed = 1, ...kv] = process.argv.slice(2);
const over = { seed: +seed }; for (const a of kv) { const [k, v] = a.split('='); over[k] = isNaN(+v) ? v : +v; }
const G = loadSim(over), P = G.PARAMETERS;
const w = new G.World(), e = new G.GameEngine(); e.add(w);
const on = () => w.year >= +from;
let births = 0, captured = 0, escaped = 0, doeDays = 0, goatDays = 0;
const kidDied = {}, adultDied = {}, kids = new Set();
const birth = w.birth.bind(w);
w.birth = m => { const n = w.newborn.length; birth(m); if (on() && m.herd >= 0) { births++; kids.add(w.newborn[n].id); } };
const capture = w.capture.bind(w);
w.capture = (g, h) => { if (on()) captured++; capture(g, h); };
const kill = w.kill.bind(w);
w.kill = (g, cause) => {
  if (on() && !g.dead && g.herd >= 0) {
    const t = kids.has(g.id) && g.age < P.weanAge ? kidDied : adultDied, c = G.CAUSE_NAMES[cause];
    t[c] = (t[c] || 0) + 1;
  }
  kill(g, cause);
};
let inHerd = new Set();
for (let d = 1; d <= years * P.yearDays; d++) {
  e.update();
  if (!on()) continue;
  const now = new Set();
  for (const g of w.goats) {
    if (g.dead) continue;
    if (g.herd >= 0) { now.add(g.id); goatDays++; if (g.sex === G.SEX_F && g.age >= P.femaleMinAge) doeDays++; }
    else if (inHerd.has(g.id)) escaped++;
  }
  inHerd = now;
}
const sum = o => Object.values(o).reduce((a, b) => a + b, 0), gy = goatDays / P.yearDays, f = x => (x / gy).toFixed(3);
const kd = sum(kidDied), ad = sum(adultDied);
console.log(`seed ${seed} ${kv.join(' ')}`);
console.log(`  mean herd ${(goatDays / ((years - from) * P.yearDays)).toFixed(1)} | doe share ${(doeDays / goatDays).toFixed(2)} | births/doe-year ${(births / (doeDays / P.yearDays)).toFixed(2)} | kid survival to weaning ${(1 - kd / births).toFixed(2)}`);
console.log(`  per goat-year: + births ${f(births)} + captured ${f(captured)} − kid deaths ${f(kd)} − weaned deaths ${f(ad)} − escaped ${f(escaped)} = net ${f(births + captured - kd - ad - escaped)}`);
console.log(`  weaned deaths per goat-year: ` + Object.entries(adultDied).map(([k, v]) => `${k} ${f(v)}`).join(' '));
