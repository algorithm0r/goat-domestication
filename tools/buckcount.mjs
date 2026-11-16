// buckcount.mjs — adult herd bucks per camp, sampled at rut peak each year from year 60 on
//   node tools/buckcount.mjs <keepChosenSires 0|1> <seed>   (H5 husbandry, random cull, sireRule gentle, herding from year 10, 200 y)
import { loadSim } from '../load.mjs';
const [kcs, seed] = process.argv.slice(2);
const G = loadSim({ seed: +seed, humansAt: 5, herdingAt: 10, penning: 1, provision: 2160, kidShelter: 1, guarding: 1, tetherNew: 1, buckManagement: 1, cullRule: 'random', offtakeRate: 0.1, keepChosenSires: +kcs, sireRule: 'gentle' }), P = G.PARAMETERS;
const world = new G.World(), engine = new G.GameEngine(); engine.add(world);
const hist = {}; let n = 0, herd = 0, does = 0, kids = 0;
for (let t = 1; t <= 200 * P.yearDays; t++) {
  engine.update();
  if (world.year >= 60 && world.day === P.rutPeakDay) for (const c of world.camps) {
    const h = world.goats.filter(g => !g.dead && g.herd === c.id); if (!h.length) continue;
    const b = h.filter(g => g.sex === G.SEX_M && g.age >= g.breedAge).length;
    hist[Math.min(b, 6)] = (hist[Math.min(b, 6)] || 0) + 1; n++; herd += h.length;
    does += h.filter(g => g.sex === G.SEX_F && g.age >= P.femaleMinAge).length;
    kids += h.filter(g => g.sex === G.SEX_M && g.age < g.breedAge).length;
  }
}
console.log(`keepChosenSires ${kcs} seed ${seed}: camp-years ${n}, mean herd ${(herd / n).toFixed(1)}, adult does ${(does / n).toFixed(1)}, young males ${(kids / n).toFixed(1)}, adult bucks (share of camp-years):`,
  Object.keys(hist).sort().map(k => `${k == 6 ? '6+' : k}:${(hist[k] / n).toFixed(2)}`).join(' '));
