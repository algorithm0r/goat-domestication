'use strict';
// Goats, wolves and humans. Agents hold state and take their steps; the World orchestrates the
// day (sub-ticks of movement and grazing), dusk, night, and the once-a-day life history, owns the
// spatial index, and runs the cross-agent passes (mating, hunting, wolves). MODEL.md describes it all.
//
// Units: energy and forage are in kcal (metabolisable energy; 1 fu = 3,600 kcal in older notes); a day is one engine tick, split into movement
// sub-ticks. Every trait's benefit and cost comes from a mechanism; nothing is a fitness score.
//   R  reactivity: alarm and flight; sensitivity of learned fear; quitting contests
//   A  aggression: persistence in contests, defence against wolves
//   S  gregariousness: attraction to company, following the herd
//   B  adult size target: intake, upkeep, reserve, fighting ability, defence (plastic: grows on food)
//   H  horns (males): fighting ability, defence
//   T  breeding-season breadth: more heats per year
//   M  lactation capacity: kid growth up to need; costs the mother energy (all of it, or what is made: milkCost)
//   W  pigmentation: wolves detect well-pigmented goats less often
// The genome's reproductive cost (penalty: slower growth, lower fertility) is off by default since 2026-11-03
// (reproCostGrowth, reproCostFertility 0); traits cost only through their mechanisms.

var SEX_F = 0, SEX_M = 1;
var CAUSE = { predation: 0, starvation: 1, age: 2, other: 3, fight: 4, exposure: 5, hunted: 6, culled: 7 };
var CAUSE_NAMES = ['predation', 'starvation', 'age', 'other', 'fight', 'exposure', 'hunted', 'culled'];
var _nextId = 1;

var WV_DEPTH = 24;      // generations-since-wild slots per herd goat (Goat.wv; last open-ended)
var LOG1P_INT = new Float64Array(256);   // Math.log1p(k) for k = 0..255 (score's company term: the same values, no call)
for (let k = 0; k < 256; k++) LOG1P_INT[k] = Math.log1p(k);

// growSD (2026-11-14): a goat's growth-rate multiplier under 'ogm', exp(growSD z), from its own stream (rand4) so that
// rand() is untouched; 1 with growSD 0 (no draw).
function growMultDraw() {
  const sd = PARAMETERS.growSD;
  if (!(sd > 0)) return 1;
  const u = 1 - rand4(), v = rand4();
  return Math.exp(sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v));
}

var Goat = class Goat {
  constructor(x, y, genome, sex, ageDays, mother) {
    const P = PARAMETERS;
    this.id = _nextId++;
    this.x = x; this.y = y;
    this.genome = genome;
    this.tr = expressTraits(genome, new Float32Array(NT));     // expressed trait values
    this.sex = sex;
    this.age = ageDays;
    const base = P.sizeMin + (P.sizeMax - P.sizeMin) * this.tr[T_B];   // the sex-neutral target from B
    this.target = base * (sex === SEX_M ? P.sexSize : 1);
    // reproductive cost of the genome (the grain model's gene-minimisation penalty, carried over):
    // p = mean expressed trait value. When reproCostGrowth/reproCostFertility > 0 (both 0 by default since 2026-11-03)
    // it slows growth and cuts fertility, whatever the goat's condition, so a trait whose benefit is removed decays
    // instead of drifting; at the defaults p is computed but inert. Core traits only:
    // twinning (L) carries its own costs (heavier gestation, lighter kids, shared milk).
    let ps = 0; for (let t = 0; t < NT_CORE; t++) ps += this.tr[t];
    this.penalty = ps / NT_CORE;
    this.load = ps;                                              // gene load, the grain model's sum
    this.breedAge = (sex === SEX_F ? P.femaleMinAge : P.maleMinAge) + P.loadFirstBreed * ps;   // days
    this.recoverUntil = 0;                                       // age (days) before which a doe that kidded can't conceive
    this.size = ageDays >= P.adultAge ? this.target : P.birthSize * base * (sex === SEX_M ? P.maleBirthSize : 1);
    this.growMult = growMultDraw();                              // 'ogm': this goat's growth-rate multiplier (not inherited)
    this.E = 0.6 * this.reserveCap();                           // energy reserve (kcal)
    this.mother = mother || null;
    this.dead = false; this.cause = -1;
    this.alarmed = false;                                       // recomputed every sub-tick
    // learned, threat-specific fear (plastic, not genetic): multiplies R for that threat. 1 = naive.
    // Sensitisation raises it, it relaxes back toward 1, habituation lowers fearOfHumans; a kid starts
    // from its mother's values and keeps learning from her alarms while it follows her.
    this.fearOfWolves = mother ? mother.fearOfWolves : 1;
    this.fearOfHumans = mother ? mother.fearOfHumans : 1;
    this.herd = -1;                                             // camp id if herded; -1 wild
    this.gsc = -1;                                              // generations since capture, maternal line (-1 = wild lineage)
    this.pgs = -1;                                              // the same on the sire line (a wild sire counts as captured)
    this.wv = null;                                             // herd-born: share of the genome by generations since it left
                                                                // the wild (WV_DEPTH slots, last open-ended); null = all wild
    this.fatherId = 0; this.fatherWild = false;
    this.ledBy = null;                                          // a hunter leading this captive back to camp
    this.guardedToday = false;                                  // rut guarding: kept at camp today
    // reproduction
    this.gestation = 0;                                         // days pregnant; 0 = not pregnant
    this.loose = false;                                         // a herd goat that ran off and has not yet rejoined
    this.grazed = 0;                                            // energy grazed today (reset each night in daily)
    this.seen = [0, 0, 0];                                      // what the herder has seen it do: [ran off, came back on its own, butted him]
    this.seenFrom = 0;                                          // day (from the run's start) the herder began watching it
    this.looseTicks = 0;                                        // sub-ticks it has been loose
    this.fetus = null;                                          // offspring genome fixed at conception
    this.fetus2 = null;                                         // the second twin's genome, if she carries twins
    this.fetus3 = null;                                         // the third, if she carries triplets
    this.nursing = null;                                        // the kid she is feeding
    this.nursing2 = null;                                       // its twin, sharing her milk
    this.nursing3 = null;                                       // a third, if triplets
    this.twin = false;                                          // born a twin or triplet (lighter at birth)
    this.litter = 1;                                            // the size of the litter it was born in
    this.milkGiven = 0; this.milkTick = -1;                     // milk her kids have drunk today (twins share it)
    this.receptive = false;
    this.cycleOffset = randomInt(P.cycleDays);                  // her own oestrous phase
    this.milkTaken = 0;                                         // today's milk taken by herders (kcal)
    this.milkYield = 0;                                         // all the milk herders have taken from her (her record)
    this.firstKidAge = -1;
    this.kids = 0;
    // Fields other code sets later, declared here (undefined, exactly as if never set) so every goat has the same
    // hidden class from birth. Added one by one in varying orders they gave goats many shapes, and every property
    // read in the hot loops went megamorphic once herding began (3x slower per year; DEVLOG 2026-11-10).
    this.fetusFather = undefined; this.fetusFatherWild = undefined; this.fetusFatherPgs = undefined; this.fetusFatherWv = undefined;
    this.capturedYear = undefined; this._kidsAtYearStart = undefined; this._milkAtYearStart = undefined;
    this._cullKey = undefined; this._seenRate = undefined; this._sireKey = undefined; this._sireRank = undefined;
    this._sexKey = undefined; this._sexTie = undefined;
    this._p75size = -1; this._p75 = 0;                          // cache of size^0.75 (p75())
  }

  // size^0.75 (Kleiber), recomputed only when size has changed: the same value Math.pow gives, without the call
  p75() {
    if (this._p75size !== this.size) { this._p75size = this.size; this._p75 = Math.pow(this.size, 0.75); }
    return this._p75;
  }

  reserveCap() { return PARAMETERS.reserveMax * this.size; }
  // Sex differences in size and growth (2026-11-14): the sex's size multiplier, and von Bertalanffy growth in mass
  // (growthCurve 'vb'). k is set so a goat born as a single at its sex's birth share of its target reaches 95% of it in
  // growYears at the full rate: M(t) = T (1 - A e^(-kt))^3, A = 1 - (birth share)^(1/3). Until 2026-11-16 k and the
  // ogm a were set from birthSize for both sexes, so with maleBirthSize / sexSize below 1 a buck took longer than
  // growYearsM (1507 days, not 1440, at sexSize 1.7 and maleBirthSize 1.1 under ogm).
  sexMult() { return this.sex === SEX_M ? PARAMETERS.sexSize : 1; }
  birthShare() {                                                // a single newborn's size as a share of its target
    const P = PARAMETERS;
    return P.birthSize * (this.sex === SEX_M ? P.maleBirthSize / P.sexSize : 1);
  }
  vbK() {
    const P = PARAMETERS, A = 1 - Math.cbrt(this.birthShare());
    return Math.log(A / (1 - Math.cbrt(0.95))) / (P.yearDays * (this.sex === SEX_M ? P.growYearsM : P.growYearsF));
  }
  vbSizeAt(age) {                                               // size at this age born as a single, grown at the full rate
    const b = this.birthShare();
    const x = 1 - (1 - Math.cbrt(b)) * Math.exp(-this.vbK() * age);
    return this.target * x * x * x;
  }
  vbGain(days) {                                                // size gained over the next days at the full rate
    const r = 1 - (1 - Math.cbrt(Math.min(1, this.size / this.target))) * Math.exp(-this.vbK() * days);
    return Math.max(0, this.target * r * r * r - this.size);
  }
  // Ontogenetic growth model (growthCurve 'ogm', 2026-11-14, with Chris: size, growth rate and maturity are coupled):
  // dM/dt = a M^(3/4) (1 - (M/T)^(1/4)), so (M/T)^(1/4) = 1 - (1 - u0) e^(-a t / (4 T^(1/4))) and time to grow ~ T^(1/4).
  // a per sex: a goat of target 1 x the sex's multiplier, born at its sex's birth share, reaches 95% in growYears.
  ogmA() {
    const P = PARAMETERS, m = this.sexMult();
    return 4 * Math.pow(m, 0.25) * Math.log((1 - Math.pow(this.birthShare(), 0.25)) / (1 - Math.pow(0.95, 0.25)))
      / (P.yearDays * (this.sex === SEX_M ? P.growYearsM : P.growYearsF));
  }
  ogmSizeAt(age) {                                              // a single of its target at the sex's a, full rate
    const b = this.birthShare();
    const u = 1 - (1 - Math.pow(b, 0.25)) * Math.exp(-this.ogmA() * age / (4 * Math.pow(this.target, 0.25)));
    return this.target * u * u * u * u;
  }
  ogmGain(days) {                                               // its own gain over the next days at the full rate
    const u0 = Math.pow(Math.min(1, this.size / this.target), 0.25);
    const u = 1 - (1 - u0) * Math.exp(-this.ogmA() * this.growMult * days / (4 * Math.pow(this.target, 0.25)));
    return Math.max(0, this.target * u * u * u * u - this.size);
  }
  // Curved linear growth (growthCurve 'curved', Chris 2026-11-16): every goat, either sex, advances one chunk a day along
  // the straight line from its birth size b to its target T, and the line is bent into a curve: a single follows
  // size = b + (T - b)(1 - (1 - x)^k), x = chunk t / (T - b), so it reaches T at (T - b) / chunk. The rate form below acts
  // on the current size, so stalls, twins born small (who start faster) and any size are handled.
  curveChunk() { const P = PARAMETERS; return (1 - P.birthSize) / (P.growYearsF * P.yearDays); }
  curveRate() {
    const P = PARAMETERS, k = P.curveExp, b = this.birthShare() * this.target;
    const left = Math.max(0, (this.target - this.size) / (this.target - b));
    return this.curveChunk() * k * (k === 1 ? 1 : Math.pow(left, (k - 1) / k));
  }
  curveSizeAt(age) {                                            // a single of its target on the curve, full rate
    const k = PARAMETERS.curveExp, b = this.birthShare() * this.target;
    const x = Math.min(1, this.curveChunk() * age / (this.target - b));
    return b + (this.target - b) * (1 - Math.pow(1 - x, k));
  }
  curveGain(days) { return this.curveGainTo(this.target, days); }   // gain over the next days on the curve, full rate
  curveGainTo(T, days) {                                        // the same toward target T (the keep value's growthCredit 'herd')
    const k = PARAMETERS.curveExp, b = this.birthShare() * T, span = T - b;
    const y = Math.min(1, Math.max(0, (this.size - b) / span));
    const x = Math.min(1, 1 - Math.pow(1 - y, 1 / k) + this.curveChunk() * days / span);
    return Math.max(0, b + span * (1 - Math.pow(1 - x, k)) - Math.max(this.size, b));
  }
  // An immigrant takes this goat's place, sex and age (World.immigrate): a new individual with the given genome and
  // learned fears, unrelated to every local goat (fresh lineage ids), with no herd ancestry, at its adult size.
  becomeImmigrant(genome, fearOfWolves, fearOfHumans) {
    const P = PARAMETERS;
    relabelGenome(genome);
    this.id = _nextId++; this.genome = genome; expressTraits(genome, this.tr);
    this.target = (P.sizeMin + (P.sizeMax - P.sizeMin) * this.tr[T_B]) * (this.sex === SEX_M ? P.sexSize : 1);
    let ps = 0; for (let t = 0; t < NT_CORE; t++) ps += this.tr[t];
    this.penalty = ps / NT_CORE; this.load = ps;
    this.breedAge = (this.sex === SEX_F ? P.femaleMinAge : P.maleMinAge) + P.loadFirstBreed * ps;
    this.size = this.age >= P.adultAge ? this.target : Math.min(this.size, this.target);
    this.growMult = growMultDraw();
    this.E = 0.6 * this.reserveCap();
    this.fearOfWolves = fearOfWolves; this.fearOfHumans = fearOfHumans;
    this.mother = null; this.gsc = -1; this.pgs = -1; this.wv = null; this.fatherId = 0; this.fatherWild = false;
    this.kids = 0; this.firstKidAge = -1;
  }
  isKid() { return this.age < PARAMETERS.weanAge; }
  // fodderRation's feeding class: 0 = pregnant or nursing does and goats under a year (fed first), 1 = the rest
  // feedExtend: a goat's want from the spring ration. 'deficit': today's upkeep (maintenance, gestation, and for a nursing
  // doe her milk capacity) less what it grazed and drank today, so the want falls to 0 as pasture recovers; 'full': as in the
  // lean season. Never more than provision × size^0.75 or the room in its reserve.
  springWant(milk) {
    const P = PARAMETERS, full = Math.min(P.provision * this.p75(), this.reserveCap() - this.E);
    if (P.feedNeed === 'full') return full;
    if (P.feedNeed !== 'deficit') throw new Error(`unknown feedNeed ${P.feedNeed}`);
    let up = this.maintenance();
    if (this.gestation > 0) up += this.fetus3 ? 3 * P.tripletBirthSize * P.gestationCost : this.fetus2 ? 2 * P.twinBirthSize * P.gestationCost : P.gestationCost;
    if (this.nursing || this.nursing2 || this.nursing3) up += this.milkCapacity();   // what she can make: her kids' and the herders' share (any milkCost)
    return Math.max(0, Math.min(full, up - this.grazed - milk));
  }
  rationClass() { return this.gestation > 0 || this.litterNursing() > 0 || this.age < PARAMETERS.yearDays ? 0 : 1; }
  // the first of her unweaned litter still alive, if any (an orphan when she dies)
  orphan() { return [this.nursing, this.nursing2, this.nursing3].find(k => k && !k.dead) || null; }
  // how many of her litter are alive and unweaned (they share her milk)
  litterNursing() {
    let n = 0;
    for (const k of [this.nursing, this.nursing2, this.nursing3]) if (k && !k.dead && k.isKid()) n++;
    return Math.max(1, n);
  }
  isAdult() { return this.age >= PARAMETERS.adultAge; }

  // Daily upkeep (kcal): Kleiber-scaled body maintenance only (traits cost through reproduction).
  maintenance() { return PARAMETERS.maintBase * this.p75(); }

  // Fighting ability a rival can see and feel: body size and horns.
  fightingAbility() { return this.size * (1 + PARAMETERS.hornW * this.tr[T_H]); }

  // Quit threshold in a contest: a buck withdraws when his estimate of his own relative strength
  // falls below it. Aggression (A) lowers it, reactivity (R) raises it, a low reserve raises it.
  quitThreshold() {
    const P = PARAMETERS, t = this.tr;
    return P.quitBase - P.quitA * (t[T_A] - 0.5) + P.quitR * (t[T_R] - 0.5) + P.quitE * (1 - this.E / this.reserveCap());
  }

  // Fertility factor from the genome's reproductive cost.
  fertility() { return 1 - PARAMETERS.reproCostFertility * this.penalty; }

  // In heat today? Needs her breeding season (breadth from T), her cycle phase, age, size, condition.
  updateReceptive(world) {
    const P = PARAMETERS;
    this.receptive = false;
    if (this.sex !== SEX_F || this.gestation > 0 || this.age < this.breedAge || this.age < this.recoverUntil) return;
    if (this.size < P.breedSizeFrac * this.target || this.E < P.breedCondition * this.reserveCap()) return;
    const half = P.rutHalfBase + this.tr[T_T] * P.rutHalfRange;
    let d = Math.abs(world.day - P.rutPeakDay); if (d > P.yearDays / 2) d = P.yearDays - d;
    if (d > half) return;
    this.receptive = (world.day + this.cycleOffset) % P.cycleDays < P.oestrusDays;
  }

  isSheltered() { return this.herd >= 0 && PARAMETERS.kidShelter && this.age < PARAMETERS.shelterAge; }
  // tethering: a herd goat still too fearful to approach (R × fearOfHumans ≥ captureFear) stays at
  // camp on fodder until it habituates, instead of going out with the herd (husbandry)
  isTethered() { return this.herd >= 0 && !this.ledBy && PARAMETERS.tetherNew && this.tr[T_R] * this.fearOfHumans >= PARAMETERS.captureFear; }
  isKeptAtCamp() { return this.isTethered() || this.guardedToday; }

  // Alarm for this sub-tick: a hunting wolf's scent or a hunter here now; R × learned fear of it.
  // An alarm is itself a fear response: with alarmLearn > 0 it sensitises the goat to that threat
  // (alarmLearn of an attack's lesson; with Chris, 2026-10-27).
  checkAlarm(world) {
    const i = this.y * world.W + this.x, R = this.tr[T_R];
    const byWolf = world.wolfField[i] > 0 && rand() < R * this.fearOfWolves;
    const byHuman = !byWolf && world.humanField[i] > 0 && rand() < R * this.fearOfHumans;
    this.alarmed = byWolf || byHuman;
    const L = PARAMETERS.alarmLearn;
    if (L > 0) { if (byWolf) this.learnFear('fearOfWolves', L); else if (byHuman) this.learnFear('fearOfHumans', L); }
  }

  // One movement sub-tick. phase: 'dawn' | 'day' | 'dusk' | 'night'.
  step(world, phase) {
    const P = PARAMETERS;
    if (this.ledBy) { this.alarmed = false; this.stepToward(world, this.ledBy.x, this.ledBy.y, 1); return; }
    if (this.isSheltered() || this.isKeptAtCamp()) {                                          // kept at camp
      this.checkAlarm(world); const c = world.camps[this.herd]; this.stepToward(world, c.x, c.y, 1); return;
    }
    if (this.mother && !this.mother.dead && this.isKid()) {
      this.checkAlarm(world);
      if (this.mother.alarmed) this.learnFromMother();
      this.stepToward(world, this.mother.x, this.mother.y, P.kidSteps);
      return;
    }
    if (this.herd >= 0 && world.herders[this.herd]) {
      const h = world.herders[this.herd];
      // a loose run-off rejoins once it is back within keepRadius of the herd's leader; until then it
      // moves as a wild goat (its gregariousness may bring it back to the flock)
      if (this.loose && Math.max(Math.abs(this.x - h.x), Math.abs(this.y - h.y)) <= P.keepRadius) { this.loose = false; this.seen[1]++; world.ys.rejoined++; }
      if (!this.loose) { this.stepWithHerd(world, h, phase); return; }
      this.looseTicks++;
    }
    if (phase !== 'day') {                                       // wild goats bed down, but flee a wolf they spot
      this.checkAlarm(world); if (this.alarmed) this.flee(world, P.fleeSteps); return;
    }
    this.checkAlarm(world);
    if (this.alarmed) this.flee(world, P.fleeSteps);
    else if (rand() < P.goatMoves / P.daySteps) this.forage(world);
  }

  // Move up to `steps` cells toward (tx, ty), not into the river.
  stepToward(world, tx, ty, steps) {
    const W = world.W, H = world.H;
    for (let s = 0; s < steps; s++) {
      if (this.x === tx && this.y === ty) return;
      const nx = this.x + Math.sign(tx - this.x), ny = this.y + Math.sign(ty - this.y);
      if (nx >= 0 && ny >= 0 && nx < W && ny < H && !world.river[ny * W + nx]) { this.x = nx; this.y = ny; }
      else return;
    }
  }

  // Score a candidate cell (MODEL C36). Forage competition is per cell; company is sensed over
  // socialRange (the goat itself is inside every candidate's window).
  // (x, y) is cell i; company is the socialRange box sum (world.socialField[i]), read from the summed-area table.
  score(world, i, need, here, x, y) {
    const P = PARAMETERS, t = this.tr, n = world.goatCount[i] - (i === here ? 1 : 0);
    const herd = world.goatsNear(x, y, P.socialRange) - 1;
    let u = need * world.forageAt(i) / (1 + P.crowding * n);
    const c = herd < P.herdSat ? herd : P.herdSat;
    u += P.socialW * t[T_S] * (c >= 0 && c < 256 && (c | 0) === c ? LOG1P_INT[c] : Math.log1p(c)) * world.logHerdNorm;
    u -= P.fearW * t[T_R] * this.fearOfWolves * world.wolfField[i] * (world.escape[i] ? 1 - P.escapeRefuge : 1);
    u -= P.fearW * t[T_R] * this.fearOfHumans * world.humanField[i];
    u += P.escapePrefW * t[T_R] * world.escape[i];
    if (this.sex === SEX_M && this.age >= this.breedAge && world.estrusCount[i] > 0) u += P.mateW;
    return u + P.moveNoise * rand();
  }

  // One foraging step to the best of the 9 Moore cells.
  forage(world) {
    const W = world.W, H = world.H, here = this.y * W + this.x, need = 1 - this.E / this.reserveCap();
    let bx = this.x, by = this.y, bu = -Infinity;
    for (let dy = -1; dy <= 1; dy++) {
      const y = this.y + dy; if (y < 0 || y >= H) continue;
      for (let dx = -1; dx <= 1; dx++) {
        const x = this.x + dx; if (x < 0 || x >= W) continue;
        const i = y * W + x; if (world.river[i]) continue;
        const u = this.score(world, i, need, here, x, y);
        if (u > bu) { bu = u; bx = x; by = y; }
      }
    }
    this.x = bx; this.y = by;
  }

  // Flight: `steps` cells away from wolf scent and hunters, toward cliffs.
  flee(world, steps) {
    const P = PARAMETERS, W = world.W, H = world.H;
    for (let s = 0; s < steps; s++) {
      let bx = this.x, by = this.y, bu = -Infinity;
      for (let dy = -1; dy <= 1; dy++) {
        const y = this.y + dy; if (y < 0 || y >= H) continue;
        for (let dx = -1; dx <= 1; dx++) {
          const x = this.x + dx; if (x < 0 || x >= W) continue;
          const i = y * W + x; if (world.river[i]) continue;
          const u = -world.wolfField[i] - world.humanField[i] + P.escapePrefW * world.escape[i] + 0.1 * rand();
          if (u > bu) { bu = u; bx = x; by = y; }
        }
      }
      this.x = bx; this.y = by;
    }
  }

  // A herd goat's sub-tick: by day it grazes near the herder (pulled by S); at dusk it follows the
  // herder home. Spooked by the herder (R × fear of humans, more often in a big herd) it bolts away;
  // alarmed by a hunting wolf it runs to the herder.
  stepWithHerd(world, h, phase) {
    const P = PARAMETERS, W = world.W, H = world.H, R = this.tr[T_R];
    const here = this.y * W + this.x, need = 1 - this.E / this.reserveCap();
    const wolfAlarm = world.wolfField[here] > 0 && rand() < R * this.fearOfWolves;
    const spookSteps = P.daySteps + (P.spookAtDusk ? P.duskSteps : 0);
    const spooked = (phase === 'day' || P.spookAtDusk) && rand() < (P.herderAlarm / spookSteps) * R * this.fearOfHumans * world.herdLoad(this.herd);
    this.alarmed = wolfAlarm || spooked;
    if (P.alarmLearn > 0) { if (wolfAlarm) this.learnFear('fearOfWolves', P.alarmLearn); if (spooked) this.learnFear('fearOfHumans', P.alarmLearn); }
    if (spooked && P.economy) world.camps[this.herd].sd.keep += P.meatYield * this.size;
    if (spooked) {                                               // bolt away from the herder
      for (let s = 0; s < P.fleeSteps; s++) {
        let bx = this.x, by = this.y, bu = -Infinity;
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          const x = this.x + dx, y = this.y + dy;
          if (x < 0 || y < 0 || x >= W || y >= H || world.river[y * W + x]) continue;
          const u = Math.max(Math.abs(x - h.x), Math.abs(y - h.y)) + 0.1 * rand();
          if (u > bu) { bu = u; bx = x; by = y; }
        }
        this.x = bx; this.y = by;
      }
      if (P.refetchRunOffs === 1) world.refetch(this, h);        // the herder goes after it now
      else if (P.refetchRunOffs === 2 && Math.max(Math.abs(this.x - h.x), Math.abs(this.y - h.y)) > P.keepRadius) { this.loose = true; this.looseTicks = 0; this.seen[0]++; world.ys.ranOff++; }
      return;
    }
    if (phase === 'dawn' || phase === 'dusk') { this.stepToward(world, h.x, h.y, P.herdTravel); return; }   // out or home with him
    if (phase !== 'day' || wolfAlarm) { this.stepToward(world, h.x, h.y, 1); return; }   // to him
    const pull = P.herdPull * (0.5 + this.tr[T_S]);
    let bx = this.x, by = this.y, bu = -Infinity;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const x = this.x + dx, y = this.y + dy;
      if (x < 0 || y < 0 || x >= W || y >= H || world.river[y * W + x]) continue;
      const d = Math.max(Math.abs(x - h.x), Math.abs(y - h.y));
      const u = need * world.forageAt(y * W + x) - pull * d + 0.05 * rand();
      if (u > bu) { bu = u; bx = x; by = y; }
    }
    this.x = bx; this.y = by;
  }

  // Graze one sub-tick's share of the day's appetite where the goat stands (type II intake).
  graze(world) {
    const P = PARAMETERS, cap = this.reserveCap();
    const here = this.y * world.W + this.x, avail = world.veg[here] - P.vegFloor;
    const functional = P.intakeHalf > 0 ? (avail > 0 ? avail / (avail + P.intakeHalf) : 0) : 1;
    const kid = this.isKid();
    const appetite = P.goatIntake * functional * this.p75() * (kid ? this.age / P.weanAge : 1) *
                     (this.alarmed ? 1 - P.alarmLoss : 1) / P.daySteps;
    let want = Math.max(0, Math.min(appetite, cap - this.E + this.maintenance() / P.daySteps));
    // crop damage (economy): a goat on a food site eats the standing plant food first, gladly
    if (P.economy && P.cropDamage && world.food[here] > 0) {
      const full = Math.max(0, Math.min(P.goatIntake * this.p75() * (kid ? this.age / P.weanAge : 1) *
                   (this.alarmed ? 1 - P.alarmLoss : 1) / P.daySteps, cap - this.E + this.maintenance() / P.daySteps));
      const c = Math.min(full, world.food[here]);
      world.food[here] -= c; this.E += c; world.ys.cropEaten += c; if (this.herd >= 0) world.ys.cropEatenHerd += c;
      if (kid) this.kidLife(world).graze += c;
      want = Math.max(0, want - c);
    }
    // forage quality: dry, dormant forage in the lean season yields less energy per unit eaten
    if (want > 0) {
      const got = world.graze(here, want) * (world.growth > 0 ? 1 : PARAMETERS.leanQuality);
      this.E += got; this.grazed += got; if (kid) this.kidLife(world).graze += got;
    }
  }

  // This year's counters for unweaned kids of its kind: [wild, herd] × litter size (single, twin, triplet).
  kidLife(world) { return world.ys.kidLife[this.herd >= 0 ? 1 : 0][this.litter - 1]; }

  // Once a day: milk, fodder, upkeep, gestation, lactation, milking, growth. False if starved.
  daily(world) {
    const P = PARAMETERS, cap = this.reserveCap();
    let milkToday = 0;                                           // milk drunk today (feedNeed 'deficit')
    if (this.isKid()) {                                          // milk, after the herders' share
      const want = P.kidMilkNeed * (1 - this.age / P.weanAge);
      let milk = 0, fromPool = false;
      const mo = this.mother;
      if (mo && !mo.dead && (mo.nursing === this || mo.nursing2 === this || mo.nursing3 === this)) {
        if (mo.milkTick !== world.tick) { mo.milkTick = world.tick; mo.milkGiven = 0; }
        // a litter shares the milk equally (2026-11-05: before, the first-processed twin drank its fill every day)
        const avail = mo.milkCapacity() - mo.milkTaken, n = mo.litterNursing();
        milk = Math.min(want, avail / n, avail - mo.milkGiven, Math.max(0, mo.E));
        mo.milkGiven += Math.max(0, milk);
        if (P.milkCost === 'made' && milk > 0) mo.E -= milk;     // she pays for the milk her kids drink
      } else if (this.herd >= 0) {                               // a herd orphan, hand-reared
        const c = world.camps[this.herd];
        milk = Math.min(want, c.milkPool); c.milkPool -= milk; fromPool = true;
      }
      if (milk > 0) { this.E += milk; milkToday = milk; }
      const kl = this.kidLife(world);                            // counters: the unweaned kid's day
      kl.days++; kl.want += want; if (milk > 0) kl[fromPool ? 'pool' : 'milk'] += milk;
    }
    // provisioning: the camp feeds its herd from its fodder store in the lean season (and kept-at-camp
    // goats all year), up to what the store holds
    const spring = world._springFeed && this.herd >= 0 && !this.isKeptAtCamp();   // feedExtend: rationed feeding past the lean season
    if (this.herd >= 0 && P.provision > 0 && (world.growth === 0 || this.isKeptAtCamp() || P.economy || spring)) {   // economy: surplus fed all year
      const c = world.camps[this.herd];
      let want = spring ? this.springWant(milkToday) : Math.min(P.provision * this.p75(), cap - this.E);
      if (P.fodderRation && (world.growth === 0 || spring) && world._rationF) want *= world._rationF[this.herd][this.rationClass()];   // the day's ration (World.rationFodder)
      if (P.economy && this.E < P.growCondition * cap) c.sd.feed += P.meatYield * this.size;   // a hungry goat: the feeders' signal (fu at risk)
      // slop (spoiling plant food) first, then cut fodder
      if (P.storeWindows) {                                    // shelf-life stores: soonest to expire first
        const fromSlop = want > 0 && c.slop > 0 ? world.takeStore(c, 'slop', want) : 0;
        const ration = fromSlop + (want - fromSlop > 0 && c.fodder > 0 ? world.takeStore(c, 'fodder', want - fromSlop) : 0);
        if (ration > 0) { this.E += ration; world.ys.fodder += ration; if (spring) world.ys.fodderSpring += ration; if (this.isKid()) this.kidLife(world).fodder += ration; }
      } else {
        const fromSlop = Math.min(want, c.slop), ration = fromSlop + Math.min(want - fromSlop, c.fodder);
        if (ration > 0) { this.E += ration; c.slop -= fromSlop; c.fodder -= ration - fromSlop; world.ys.fodder += ration; if (spring) world.ys.fodderSpring += ration; if (this.isKid()) this.kidLife(world).fodder += ration; }
      }
    }
    this.E -= this.maintenance();
    if (this.gestation > 0) this.E -= this.fetus3 ? 3 * P.tripletBirthSize * P.gestationCost
      : this.fetus2 ? 2 * P.twinBirthSize * P.gestationCost : P.gestationCost;   // twins, triplets: by litter birth mass
    const lactating = this.nursing || this.nursing2 || this.nursing3;   // while any of her litter is unweaned (fixed 2026-11-05: was the first kid only)
    // 'capacity': the whole capacity costs, needed or not; 'made' (2026-11-05, Chris): she pays only for the milk
    // made, what her kids drink (charged as they drink) and what the herders take
    if (lactating && P.milkCost !== 'made') this.E -= this.milkCapacity();
    this.milkTaken = 0;
    if (lactating && this.herd >= 0 && P.milkIntensity > 0) {
      const take = P.milkIntensity * this.milkCapacity();
      this.milkTaken = take; this.milkYield += take; world.camps[this.herd].milkPool += take; world.ys.milk += take;
      if (P.milkCost === 'made') this.E -= take;
    }
    // growth: by the growth curve (growthCurve, default 'curved'); × (1 − reproCostGrowth × p), 1 by default
    if (this.size < this.target && this.E > P.growCondition * cap) {
      const gm = P.loadGrowth > 0 ? (1 - P.reproCostGrowth * P.loadRef / NT_CORE) / Math.max(0.2, 1 + P.loadGrowth * (this.load - P.loadRef))
                                  : 1 - P.reproCostGrowth * this.penalty;
      const rate = P.growthCurve === 'vb'
        ? 3 * this.vbK() * (Math.cbrt(this.target) * Math.pow(this.size, 2 / 3) - this.size)
        : P.growthCurve === 'ogm' ? this.ogmA() * this.growMult * Math.pow(this.size, 0.75) * (1 - Math.pow(this.size / this.target, 0.25))
        : P.growthCurve === 'curved' ? this.curveRate()
        : P.growthAbs;
      const ds = Math.min(rate * gm, this.target - this.size);
      this.size += ds; this.E -= P.growthCost * ds;
    }
    if (this.E > cap) this.E = cap;
    this.grazed = 0;
    return this.E >= -P.leanBuffer * this.size;                 // starvation: past the lean-tissue buffer (0: an empty reserve)
  }

  // Habituation: a day of harmless contact with people lowers learned fear of humans, fast inside
  // the juvenile socialisation window (length falls with R), slowly after it.
  habituate() {
    const P = PARAMETERS, inWindow = this.age < P.windowMax * (1 - this.tr[T_R]);
    this.fearOfHumans += (P.fearMin - this.fearOfHumans) * (inWindow ? P.habKid : P.habAdult);
  }

  // lactation capacity (kcal/day) from M; with milkCondition > 0 (with Chris, 2026-11-12) it falls with her condition: full
  // at a reserve of milkCondition × cap or more, in proportion below, none at an empty reserve. Kids and herders share it.
  milkCapacity() {
    const P = PARAMETERS, c = P.milkBase * (0.5 + this.tr[T_M]);
    return P.milkCondition > 0 ? c * Math.max(0, Math.min(1, this.E / (P.milkCondition * this.reserveCap()))) : c;
  }
  // generations since the wild, genome-weighted (the goat's share of genome at each depth, wv); 0 for a captive or wild goat
  wildDepth() { if (!this.wv) return 0; let d = 0; for (let k = 1; k < WV_DEPTH; k++) d += k * this.wv[k]; return d; }

  // Sensitisation to a threat ('fearOfWolves' | 'fearOfHumans'): reactive goats learn fear faster.
  learnFear(threat, amount) {
    const P = PARAMETERS, r = P.fearLearnR ? this.tr[T_R] : P.fearLearnRef;   // reactive goats learn faster, or all alike
    const v = this[threat] + P.sensitize * r * amount;
    this[threat] = v > P.fearMax ? P.fearMax : v;
  }

  // A following kid sees its mother alarmed: its fears move toward hers (social learning).
  learnFromMother() {
    const r = PARAMETERS.motherLearn, m = this.mother;
    this.fearOfWolves += (m.fearOfWolves - this.fearOfWolves) * r;
    this.fearOfHumans += (m.fearOfHumans - this.fearOfHumans) * r;
  }

  // Daily: learned fear relaxes back toward the naive baseline of 1.
  forgetFear() {
    const r = PARAMETERS.forgetRate;
    this.fearOfWolves += (1 - this.fearOfWolves) * r;
    this.fearOfHumans += (1 - this.fearOfHumans) * r;
  }

  exposed(world) {
    const P = PARAMETERS;
    if (!(P.kidExposure > 0) || this.age >= 30) return false;
    let p = P.kidExposure * (1 - world.growth);
    if (this.herd >= 0 && P.provision > 0) p *= 1 - P.provisionShelter;
    if (this.isSheltered()) p *= 1 - P.shelterExposure;
    return rand() < p;
  }

  dies() {
    const P = PARAMETERS, a = this.age / P.yearDays;
    let h = P.adultMortality;
    if (a < 1) {
      // a small kid dies more (2026-11-05, with Chris): the first-year hazard × (ref / size)^juvSizeExp, ref the
      // size of a single of its target born and grown at full rate to this age (twins, triplets, and kids short of milk)
      let m = 1;
      if (P.juvSizeExp > 0) m = Math.pow((P.growthCurve === 'vb' ? this.vbSizeAt(this.age)
        : P.growthCurve === 'ogm' ? this.ogmSizeAt(this.age)
        : P.growthCurve === 'curved' ? this.curveSizeAt(this.age)
        : Math.min(this.target, this.birthShare() * this.target + P.growthAbs * this.age)) / this.size, P.juvSizeExp);
      // (linear: born at its sex's birth share since 2026-11-16; birthSize before, which with sexSize 1.7 made the
      // reference newborn buck 1.5x his real birth size; identical at sexSize 1 and maleBirthSize 1)
      h += P.juvMortality * m;
    }
    if (a > P.senescenceAge) h += P.senescenceRate * (a - P.senescenceAge);
    return rand() < h / P.yearDays;
  }
};

var Wolf = class Wolf {
  constructor(x, y, genome) {
    this.id = _nextId++;
    this.x = x; this.y = y;
    this.genome = genome;                                       // inert (wolves don't breed)
    this.fullness = rand();
    this.kills = 0;
    this.goatSuccess = 0.5;                                     // memory of finding goats (prey switching)
    this.huntingGoats = false;                                  // tonight's choice
    this.attemptsLeft = 0;
    this.sawGoats = false;
    this.chased = false;                                        // driven off by a herder this bout
  }
};

// A human: lives at a camp (fixed population, never dies). Each day a role: 'herd' (the camp's
// herder), 'hunt', 'forage' or 'camp'. x, y is where they are now.
var Human = class Human {
  constructor(camp) {
    this.id = _nextId++;
    this.camp = camp;
    this.x = camp.x; this.y = camp.y;
    this.role = 'camp';
    this.herding = false; this.hunting = false; this.foraging = false;
    this.target = null;                                         // herder: today's pasture
    this.steps = 0;                                             // cells walked today
    this.attemptsLeft = 0;
    this.captive = null;                                        // a goat being led home
    this.kills = 0;
    // set later by the World (dawn, foraging); declared here, undefined, so every human keeps one hidden class
    this.capturing = undefined; this.cutting = undefined; this.task = undefined; this.meat = undefined; this.load = undefined;
  }
};
