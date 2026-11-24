'use strict';
// Samples the world and ships a self-describing packet (full PARAMETERS + samples) to the DB at
// epoch. packet() (db.js) embeds PARAMETERS verbatim so every run reconstructs from its own record.
//   every reportingPeriod days : census scalars (population, kids, sexes, vegetation)
//   at each year end           : per-trait genotype histograms (20 buckets, the grain paper's form; all goats
//                                and herd goats) and learned-fear histograms,
//                                trait means, and the year's life history (births, deaths by cause,
//                                age at first kidding, adult mortality)
// In the browser this auto-flushes at epoch; the headless runner flushes explicitly.
var HIST_BUCKETS = 20;
var GEN_BINS = [[0, 0], [1, 1], [2, 4], [5, 9], [10, 19], [20, 1e9]];   // generations-since-wild bins, as recorded
var DEPTH_EVERY = 10;                        // years pooled per record of the gene histograms by lineage depth
var SHARE_BINS = [0, 1 / 16, 1 / 8, 1 / 4, 1 / 2, 1];   // wild goats: upper edges of the herd-born genome share bins
var shareBin = s => { for (let b = 0; b < SHARE_BINS.length; b++) if (s <= SHARE_BINS[b] + 1e-9) return b; return SHARE_BINS.length - 1; };
var FEAR_KEYS = ['fearW', 'fearH'];          // learned fear of wolves, of humans: histograms over [0, fearMax]
var HIST_KEYS = TRAITS.concat(FEAR_KEYS);
var median = v => { if (!v.length) return null; const s = v.slice().sort((a, b) => a - b); return s[s.length >> 1]; };
// year-record diagnostics behind a named PARAMETERS switch (params.js, "diagnostics"); 0 leaves the field out
var DIAG_FIELDS = { logWolfAtk: 'wolfAtk', logKidLife: 'kidLife', logKilloff: 'killoff', logHerdKilloff: 'herdKilloff', logKidDeathCause: 'kidDeathCause' };
var diagOff = s => PARAMETERS[s] === 0 || PARAMETERS[s] === false;
var histPeriod = () => Math.max(1, Math.round(PARAMETERS.histPeriod || 1));   // years between recorded gene histograms
var genBin = d => { for (let b = 0; b < GEN_BINS.length; b++) if (d <= GEN_BINS[b][1]) return b; return GEN_BINS.length - 1; };

var DataManager = class DataManager {
  constructor(world, db, graph) {
    this.world = world;
    this.db = db;
    this.graph = graph;
    this.samples = [];
    this.years = [];
    this.hist = {};                          // trait → [year][bucket] counts, all goats
    this.histHerd = {};                      // the same, herd goats only (wild = hist − histHerd), from 2026-11-02
    for (const t of HIST_KEYS) { this.hist[t] = []; this.histHerd[t] = []; }
    // 2026-11-13: hist and histHerd are recorded at the end of every histPeriod-th year (years histPeriod-1, 2*histPeriod-1,
    // ...; every year by default), and histYears names the year of each recorded row, so readers never infer it
    this.histYears = [];
    // 2026-11-11: genotype histograms by lineage, pooled over DEPTH_EVERY years, [trait][record][bin][bucket]; record k covers
    // years k*every .. k*every + every - 1. Herd goats by mean depth (Goat.wildDepth rounded, in GEN_BINS); wild goats by the
    // share of the genome from herd-born goats (1 - wv[0], in SHARE_BINS: none, to 1/16, 1/8, 1/4, 1/2, more), since a
    // wild goat's mean depth mixes how much herd ancestry it has with how deep it is
    // histDepth pools max(DEPTH_EVERY, histPeriod) years per record (a histPeriod up to 10 leaves it as it is); years: the
    // last year of each record, which covers the `every` years ending there
    this.histDepth = { every: Math.max(DEPTH_EVERY, histPeriod()), bins: GEN_BINS, wildShareBins: SHARE_BINS, herd: {}, wild: {}, years: [] };
    for (const t of TRAITS) { this.histDepth.herd[t] = []; this.histDepth.wild[t] = []; }
    this._depthAcc = null;
    this.run = (PARAMETERS.db && PARAMETERS.db.run) || 'run';
    this.flushed = false;
    this._G = new Float32Array(NT);
    this._adultsAtYearStart = this.countAdults();
  }

  update(engine) {
    const P = PARAMETERS, w = this.world;
    if (engine.tick % P.reportingPeriod === 0) this.sample(engine.tick);
    if (w.day === P.yearDays - 1) this.yearEnd();
    if (!this.flushed && engine.tick >= P.epoch) { this.flushed = true; this.flush(); }
  }

  sample(tick) {
    const w = this.world, c = w.census();
    this.samples.push({ tick, year: w.year, day: w.day, meanVeg: +w.meanVeg().toFixed(4), ...c });
    if (this.graph) this.graph.push(c.goats);
  }

  countAdults() {
    let n = 0; for (const g of this.world.goats) if (!g.dead && g.age >= PARAMETERS.yearDays) n++; return n;
  }

  yearEnd() {
    const w = this.world, ys = w.ys, G = this._G;
    const h = HIST_KEYS.map(() => new Array(HIST_BUCKETS).fill(0)), hh = HIST_KEYS.map(() => new Array(HIST_BUCKETS).fill(0)), mean = new Float64Array(NT);
    const fb = v => Math.min(HIST_BUCKETS - 1, Math.max(0, (v / PARAMETERS.fearMax * HIST_BUCKETS) | 0));
    let fWh = 0;
    let n = 0, fW = 0, fH = 0, nh = 0, fHh = 0, Fh = 0, Fw = 0, gscs = 0;
    const meanH = new Float64Array(NT);
    const nb = GEN_BINS.length, da = this._depthAcc || (this._depthAcc = [0, 1].map(() => TRAITS.map(() => Array.from({ length: nb }, () => new Array(HIST_BUCKETS).fill(0)))));
    // generations since wild (2026-11-01): maternal line (herd goats), sire line (herd males), genome share by depth
    const mat = new Array(GEN_BINS.length).fill(0), pat = new Array(GEN_BINS.length).fill(0), anc = new Float64Array(GEN_BINS.length);
    let ancDepth = 0, wildHS = 0, wildAny = 0;
    const szS = [0, 1].map(() => [0, 1].map(() => new Float64Array(13))), szN = [0, 1].map(() => [0, 1].map(() => new Float64Array(13)));
    const logDepth = !diagOff('logHistDepth');   // histDepth stays in the run as an empty record when switched off
    for (const g of w.goats) {
      if (g.dead) continue;
      { const hi = g.herd >= 0 ? 1 : 0, a = Math.min(12, Math.floor(g.age / PARAMETERS.yearDays)); szS[hi][g.sex][a] += g.size; szN[hi][g.sex][a]++; }
      genotypicValues(g.genome, G); n++; fW += g.fearOfWolves; fH += g.fearOfHumans;
      const F = ibd(g.genome);
      h[NT][fb(g.fearOfWolves)]++; h[NT + 1][fb(g.fearOfHumans)]++;
      if (g.herd >= 0) { nh++; fHh += g.fearOfHumans; fWh += g.fearOfWolves;
        hh[NT][fb(g.fearOfWolves)]++; hh[NT + 1][fb(g.fearOfHumans)]++;
        for (let t = 0; t < NT; t++) hh[t][Math.min(HIST_BUCKETS - 1, (G[t] * HIST_BUCKETS) | 0)]++; Fh += F || 0; gscs += Math.max(0, g.gsc);
        mat[genBin(Math.max(0, g.gsc))]++; if (g.sex === SEX_M) pat[genBin(Math.max(0, g.pgs))]++;
        if (!g.wv) anc[0]++; else for (let d = 0; d < WV_DEPTH; d++) { anc[genBin(d)] += g.wv[d]; ancDepth += d * g.wv[d]; }
        for (let t = 0; t < NT; t++) meanH[t] += G[t]; }
      else Fw += F || 0;
      for (let t = 0; t < NT; t++) { mean[t] += G[t]; h[t][Math.min(HIST_BUCKETS - 1, (G[t] * HIST_BUCKETS) | 0)]++; }
      const inHerd = g.herd >= 0, dd = da[inHerd ? 1 : 0], hs = !inHerd && g.wv ? 1 - g.wv[0] : 0;
      const db = inHerd ? (g.wv ? genBin(Math.round(g.wildDepth())) : 0) : shareBin(hs);
      if (!inHerd) { wildHS += hs; if (hs > 1e-9) wildAny++; }
      if (logDepth) for (let t = 0; t < NT; t++) dd[t][db][Math.min(HIST_BUCKETS - 1, (G[t] * HIST_BUCKETS) | 0)]++;
    }
    if (logDepth && (w.year + 1) % this.histDepth.every === 0) {
      TRAITS.forEach((t, k) => { this.histDepth.wild[t].push(da[0][k]); this.histDepth.herd[t].push(da[1][k]); });
      this.histDepth.years.push(w.year);
      this._depthAcc = null;
    }
    if ((w.year + 1) % histPeriod() === 0) { HIST_KEYS.forEach((t, k) => { this.hist[t].push(h[k]); this.histHerd[t].push(hh[k]); }); this.histYears.push(w.year); }
    const fk = ys.firstKidAges.slice().sort((a, b) => a - b);
    const deaths = {}; CAUSE_NAMES.forEach((c, k) => deaths[c] = ys.deaths[k]);
    const herdDeaths = {}; CAUSE_NAMES.forEach((c, k) => herdDeaths[c] = ys.herdDeaths[k]);   // herd goats only (2026-10-31)
    const killoff = {};                       // cause → { F: [age 0..15+], M: [...] }, causes with deaths only
    CAUSE_NAMES.forEach((c, k) => { if (ys.deaths[k] > 0) killoff[c] = { F: ys.killoff[k][SEX_F], M: ys.killoff[k][SEX_M] }; });
    // mean size by [wild, herd] × sex × age in years (0..12+), and herd deaths by [slaughtered, starved, other] × sex ×
    // half-year of age (0..29), for the Ganj Dareh comparison (2026-11-14)
    const sizeByAge = [0, 1].map(hi => [0, 1].map(s => Array.from(szS[hi][s], (v, a) => szN[hi][s][a] ? +(v / szN[hi][s][a]).toFixed(3) : null)));
    const rec = {
      year: w.year, goats: n, wolves: w.wolves.length, humans: w.humans.length, killoff,
      sizeByAge, herdDeathHalf: ys.herdDeathHalf.map(c => c.map(a => a.slice())),
      wolfAtk: ys.wolfAtk,                    // key → [attacks, kills]; key herd/wild|phase|escape|camp|spotted|loose|kid|nearHerder
      herdDeaths: nh || ys.herdKilloff[0].some(v => v) ? herdDeaths : undefined,
      herdKilloff: nh || ys.herdKilloff[0].some(v => v) ? { F: ys.herdKilloff[SEX_F], M: ys.herdKilloff[SEX_M] } : undefined,
      births: ys.births, conceptions: ys.conceptions, deaths,
      medianFirstKidAge: fk.length ? fk[fk.length >> 1] : null,
      // 2026-11-05: age at first kidding by where the doe kidded, litters [singles, twins, triplets] and
      // unweaned deaths by the litter the kid was born in, each { wild, herd }
      medianFirstKidAgeHerd: median(ys.firstKidAgesHerd), medianFirstKidAgeWild: median(ys.firstKidAgesWild),
      litters: { wild: ys.litters[0], herd: ys.litters[1] }, kidDeaths: { wild: ys.kidDeaths[0], herd: ys.kidDeaths[1] },
      // unweaned deaths by cause, [single, twin, triplet] (causes with none left out); size and E/cap at first kidding
      kidDeathCause: Object.fromEntries(['wild', 'herd'].map((p, h) => [p, Object.fromEntries(CAUSE_NAMES.map((c, k) => [c, ys.kidDeathCause[h][k]]).filter(e => e[1].some(v => v)))])),
      // first-kid age with the mother's B and growth multiplier (2026-11-14): count, age quartiles, and sums for pooled
      // correlations (a = age, b = B, g = growth multiplier)
      firstKidStats: Object.fromEntries(['wild', 'herd'].map((p, h) => {
        const v = ys.firstKidStats[h]; if (!v.length) return [p, null];
        const ag = v.map(x => x[0]).sort((x, y) => x - y), q = f => ag[Math.min(ag.length - 1, Math.floor(f * ag.length))];
        const o = { n: v.length, q25: q(0.25), q50: q(0.5), q75: q(0.75), a: 0, aa: 0, b: 0, bb: 0, ab: 0, g: 0, gg: 0, ag: 0 };
        for (const [a, b, g] of v) { o.a += a; o.aa += a * a; o.b += b; o.bb += b * b; o.ab += a * b; o.g += g; o.gg += g * g; o.ag += a * g; }
        for (const k of ['b', 'bb', 'ab', 'g', 'gg', 'ag']) o[k] = +o[k].toFixed(4);
        return [p, o];
      })),
      firstKidCond: Object.fromEntries(['wild', 'herd'].map((p, h) => { const v = ys.firstKidCond[h]; return [p, v.length ? { n: v.length, size: +(v.reduce((a, x) => a + x[0], 0) / v.length).toFixed(3), cond: +(v.reduce((a, x) => a + x[1], 0) / v.length).toFixed(3) } : null]; })),
      // unweaned kids, [single, twin, triplet]: kid-days; kcal wanted from milk, drunk from the mother, from the camp
      // pool, grazed, fed as fodder; weaned (sums of size, size/target, E/cap; mother dead); deaths with mother dead
      kidLife: Object.fromEntries(['wild', 'herd'].map((p, h) => [p, ys.kidLife[h].map(o => Object.fromEntries(Object.entries(o).map(([k, v]) => [k, +v.toFixed(2)])))])),
      adultMortality: this._adultsAtYearStart ? +(ys.adultDeaths / this._adultsAtYearStart).toFixed(4) : null,
      traitMeans: Object.fromEntries(TRAITS.map((t, k) => [t, n ? +(mean[k] / n).toFixed(4) : null])),
      learnedFear: { wolves: n ? +(fW / n).toFixed(4) : null, humans: n ? +(fH / n).toFixed(4) : null },
      herded: nh, captured: ys.captured, exchanged: ys.exchanged, concOrigin: ys.concOrigin,
      wildConc: ys.wildConc, capIn: ys.capIn, capBred: ys.capBred,   // [wild sire, herd sire]; [does, bucks] (2026-11-20)
      looseDeaths: ys.looseDeaths, selfMaintDays: ys.selfMaintDays,
      parentAge: ys.parentAge.map(a => [Math.round(a[0]), Math.round(a[1]), a[2]]),   // [wild, herd]: [sum dam age, sum sire age (days), litters]
      // viability (2026-11-20): [wild, herd][female, male] = [sum genotype per trait (TRAITS order)..., n] at birth / first breeding
      firstSireAge: ys.firstSireAge.map(a => [Math.round(a[0]), a[1]]),   // [wild, herd]: [summed age at first siring (days), bucks]
      cohortBirth: ys.cohortBirth.map(h => h.map(r => Array.from(r, v => +v.toFixed(3)))),
      cohortBreed: ys.cohortBreed.map(h => h.map(r => Array.from(r, v => +v.toFixed(3)))),  // herd goats dying while loose; camp-days self-maintaining (selfDoes > 0)
      selSire: ys.selN[1] ? Object.fromEntries(TRAITS.map((t, k) => [t, +(ys.selSire[k] / ys.selN[1]).toFixed(5)])) : null,
      selDam: ys.selN[0] ? Object.fromEntries(TRAITS.map((t, k) => [t, +(ys.selDam[k] / ys.selN[0]).toFixed(5)])) : null, selN: ys.selN, escaped: ys.escaped, runOffLost: ys.runOffLost, refetched: ys.refetched, ranOff: ys.ranOff, rejoined: ys.rejoined, spooked: ys.spooked, alarmCaught: ys.alarmCaught, culledHerd: ys.culledHerd, milk: +ys.milk.toFixed(1),
      wolvesKilled: ys.wolvesKilled, wolvesChased: ys.wolvesChased, fodder: +ys.fodder.toFixed(1), fodderSpring: +ys.fodderSpring.toFixed(1), foraged: +ys.foraged.toFixed(1),
      // Ganj Dareh diagnostics: inbreeding (IBD since herding began), sires per camp-year, wild sires,
      // R of the goats captured this year (capture bias vs retention), generations since capture
      herdF: nh ? +(Fh / nh).toFixed(4) : null, wildF: n - nh ? +(Fw / (n - nh)).toFixed(4) : null,
      siresPerCamp: (() => { const s = ys.herdSires.map(x => x.size).filter(v => v > 0); return s.length ? +(s.reduce((a, b) => a + b, 0) / s.length).toFixed(2) : null; })(),
      herdBirths: ys.herdBirths, wildSiredShare: ys.herdBirths ? +(ys.wildSired / ys.herdBirths).toFixed(3) : null,
      chosenSiredShare: ys.herdConceptions ? +(ys.chosenSired / ys.herdConceptions).toFixed(3) : null,   // herd conceptions by a chosen sire (buck management)
      capturedR: ys.captured ? +(ys.capturedR / ys.captured).toFixed(4) : null,
      herdGSC: nh ? +(gscs / nh).toFixed(2) : null,
      // generations since wild, bins 0 | 1 | 2-4 | 5-9 | 10-19 | 20+: herd goats by maternal line and herd males by
      // sire line (counts); herd genome by depth (mean share), and its mean depth (the 20+ slot counted at 23)
      herdMatGen: nh ? mat : null, herdPatGen: nh ? pat : null,
      herdWildAnc: nh ? Array.from(anc, v => +(v / nh).toFixed(4)) : null, herdAncDepth: nh ? +(ancDepth / nh).toFixed(2) : null,
      // wild goats' genome share from herd-born goats (feral ancestry), mean, and the share of wild goats with any (2026-11-11)
      wildHerdShare: n - nh ? +(wildHS / (n - nh)).toFixed(4) : null, wildAnyHerd: n - nh ? +(wildAny / (n - nh)).toFixed(4) : null,
      herdTraitMeans: nh ? Object.fromEntries(TRAITS.map((t, k) => [t, +(meanH[k] / nh).toFixed(4)])) : null,
      herdFearOfHumans: nh ? +(fHh / nh).toFixed(4) : null, herdFearOfWolves: nh ? +(fWh / nh).toFixed(4) : null,
      ...(PARAMETERS.shotChance > 0 && !PARAMETERS.economy ? { shots: ys.shots, shotKills: ys.shotKills } : {}),
      ...(PARAMETERS.immigrationRate > 0 ? { immigrants: ys.immigrants } : {}),   // wild goats swapped for immigrants this year
      ...(PARAMETERS.surplusCull ? { surplusBucks: ys.surplusBucks } : {}),        // weaned herd males slaughtered as surplus (surplusCull)
      ...(PARAMETERS.winterCull ? { winterCulled: ys.winterCulled } : {}),         // herd goats slaughtered on the first lean day (winterCull)
      // how the culls interact (2026-11-13): offtake draws due, those cancelled by surplus/winter credit, each cull's victims
      // [kids, does, bucks, other, captured themselves]; hunting attempts spent; mean wild goats within herdRange of a camp
      offtakeDue: ys.offtakeDue, offtakeCredited: ys.offtakeCredited, cullTally: JSON.parse(JSON.stringify(ys.cullTally)),
      huntTries: ys.huntTries, wildNearCamp: ys.campDays ? +(ys.wildNearCamp / ys.campDays).toFixed(2) : null, herdComp: ys.campDays ? ys.herdComp.map(v => +(v / ys.campDays).toFixed(2)) : null, herdStarve: JSON.parse(JSON.stringify(ys.herdStarve)), herdStarveMonth: ys.herdStarveMonth.slice(),   // herd starvation [unweaned, weaned <1y, does pregnant or nursing, dry does, bucks, other] by season; by 30-day month   // mean kids/does/bucks/other per managed camp-day
      ...(PARAMETERS.economy ? { econ: {
        roleDays: { ...ys.roleDays }, taskDays: { ...ys.taskDays },
        roleReturn: Object.fromEntries(Object.entries(ys.roleRet).map(([r, v]) => [r, ys.roleDays[r] ? +(v / ys.roleDays[r]).toFixed(3) : null])),
        demand: +ys.demand.toFixed(1), meatEaten: +ys.meatEaten.toFixed(1), plantEaten: +ys.plantEaten.toFixed(1),
        unmet: +ys.unmet.toFixed(1), offtakeFu: +ys.offtakeFu.toFixed(1), culledValue: ys.culledValue, meanStock: +(ys.stock / PARAMETERS.yearDays).toFixed(1),
        meatStore: +w.camps.reduce((a, c) => a + c.meat, 0).toFixed(1), fodderStore: +w.camps.reduce((a, c) => a + c.fodder, 0).toFixed(1),
        plantStore: +w.camps.reduce((a, c) => a + c.pfood, 0).toFixed(1), slopStore: +w.camps.reduce((a, c) => a + c.slop, 0).toFixed(1),
        slopMade: +ys.slop.toFixed(1), heap: +ys.heap.toFixed(1), sitesSeeded: ys.sitesSeeded, cropEaten: +ys.cropEaten.toFixed(1), cropEatenHerd: +ys.cropEatenHerd.toFixed(1),
        nearSites: w.camps.map(c => { let n = 0, cap = 0; const R = PARAMETERS.heapRadius;
          for (let y = c.y - R; y <= c.y + R; y++) for (let x = c.x - R; x <= c.x + R; x++) { if (x < 0 || y < 0 || x >= w.W || y >= w.H) continue; const i = y * w.W + x; if (w.foodCap[i] > 0) { n++; cap += w.foodCap[i]; } }
          return [n, Math.round(cap)]; }), foodGathered: +ys.foodGathered.toFixed(1), fodderCut: +ys.foraged.toFixed(1),
        dried: +ys.dried.toFixed(1), driedLost: +ys.driedLost.toFixed(1), fodderLost: +ys.fodderLost.toFixed(1),
        gatherScored: +ys.gatherScored.toFixed(1), meatHunted: +ys.meatHunted.toFixed(1), huntScored: +ys.huntScored.toFixed(1), shots: ys.shots, shotKills: ys.shotKills, altKills: ys.altKills, kills: ys.hunted,
        unmetQ: ys.unmetQ.map(v => +v.toFixed(1)), slaughterQ: [...ys.slaughterQ], herdQ: [...ys.herdQ], labourQ: [...ys.labourQ],
      } } : {}),
    };
    for (const sw in DIAG_FIELDS) if (diagOff(sw)) delete rec[DIAG_FIELDS[sw]];   // switched-off diagnostics left out
    if ((w.year + 1) % Math.max(1, Math.round(PARAMETERS.recordEvery || 1)) === 0) this.years.push(rec);   // recordEvery (2026-11-19)
    w.resetYearStats();
    this._adultsAtYearStart = this.countAdults();
  }

  async flush() {
    if (!this.db) return { ok: false };
    const pkt = this.db.packet(PARAMETERS, { project: 'Animal Domestication', run: this.run, samples: this.samples, years: this.years, hist: this.hist, histHerd: this.histHerd, histYears: this.histYears, histDepth: this.histDepth });
    try {
      const res = await this.db.insert(this.run, pkt);
      if (typeof console !== 'undefined') console.log('[data] saved', JSON.stringify(res));
      return res;
    } catch (e) {
      if (typeof console !== 'undefined') console.error('[data] save failed:', e.message);
      return { ok: false, error: e.message };
    }
  }

  draw() {}
};
