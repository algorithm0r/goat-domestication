'use strict';
// The world: landscape, vegetation and the animal populations. The field is held in flat typed
// arrays (index = y*W + x) so the per-tick update allocates nothing. It is an engine entity (has
// update) but draws nothing — rendering is the Observer's job. MODEL.md describes every step.
//
// One engine tick is one DAY, run as sub-ticks (MODEL §3):
//   dawn   roles for the day; herders pick pasture; rut guarding; heats; then dawnSteps sub-ticks:
//          herders lead penned herds out; wolves end their hunting bout (wolfTick)
//   rest   wolves lie up for the day; their scent marks where they rest
//   day    daySteps sub-ticks: humans move (herders lead, hunters stalk, foragers cut fodder); goats
//          move and graze; hunters attempt; the index is rebuilt after each
//   mating once, on end-of-day positions: a doe in heat mates among the bucks actually around her
//   dusk   duskSteps sub-ticks: herds and captives walk home; wild goats bed down; wolves start a
//          hunting bout (wolfTick)
//   herd   strays, habituation, offtake and culling
//   night  nightSteps sub-ticks: wolves hunt (wolfTick); goats flee wolves they spot
//   A wolf's bout runs dusk → night → next dawn: in every one of those sub-ticks a hungry, goat-hunting
//   wolf moves, marks the cells around it, goats react (flee), and it attacks once; it stops when fed.
//   life   once per goat: milk, fodder, upkeep, growth, deaths, births, learning
// shelf-life stores (storeWindows): each batch queue, the camp total it adds to, and its shelf life
var STORE_FIELD = { fresh: 'meat', dried: 'meat', pfood: 'pfood', slop: 'slop', fodder: 'fodder' };
var STORE_DAYS = { fresh: 'freshDays', dried: 'dryDays', pfood: 'plantDays', slop: 'slopDays', fodder: 'fodderDays' };
var IMMIGRANT_POOL = null;   // [{g: alleles, fw, fh}], set by load.mjs when immigrationRate > 0

var World = class World {
  constructor() {
    const P = PARAMETERS;
    seedRandom(P.seed);
    const W = this.W = P.width, H = this.H = P.height, N = this.N = W * H;

    this.river = new Uint8Array(N);       // 1 = river cell (water, no vegetation, impassable)
    this.wet = new Float32Array(N);       // 0..1 wetness → vegetation growth rate
    this.elev = new Float32Array(N);      // 0..1, rising away from the river
    this.rugged = new Float32Array(N);    // 0..1 value noise
    this.escape = new Uint8Array(N);      // 1 = escape terrain
    this.veg = new Float32Array(N);       // standing biomass as a fraction of K
    this.campOf = new Int8Array(N).fill(-1);
    this.camps = [];
    this.land = [];                       // indices of non-river cells (for placement)

    const rough = valueNoise(W, H, P.ruggedScale);
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      const i = y * W + x;
      if (y < P.riverRows) { this.river[i] = 1; this.wet[i] = 1; continue; }
      this.land.push(i);
      const d = y - P.riverRows;                                   // rows from the bank
      this.wet[i] = Math.max(P.uplandWetness, 1 - d / P.wetDepth);
      const base = Math.pow(d / (H - 1 - P.riverRows), 0.8);       // gentle valley, steeper uplands
      this.rugged[i] = rough[i];
      this.elev[i] = clamp(0.85 * base + 0.15 * rough[i] * base, 0, 1);
      this.escape[i] = (this.elev[i] > P.escapeElevation && rough[i] > P.escapeRugged) ? 1 : 0;
      this.veg[i] = P.vegInit;
    }
    for (let c = 0; c < P.camps; c++) {
      const x = Math.round((c + 0.5) * W / P.camps), y = P.riverRows + 1;
      this.camps.push({ id: c, x, y, milkPool: 0, fodder: 0, meat: 0, pfood: 0, slop: 0, ret: { gather: null, hunt: null, herd: null },
                        stim: { keep: null, guard: null, feed: null, capture: null }, sd: { keep: 0, guard: 0, feed: 0, capture: [0, 0] },
                        q: { fresh: [], dried: [], pfood: [], slop: [], fodder: [] },   // storeWindows: dated batches
                        feedBudget: 0, guards: [], keepers: [], keepN: 0,
                        stockPrev: null, herdedYesterday: false, lastX: x, lastY: y });
      this.campOf[y * W + x] = c;
    }

    // Pre-warm: vegetation alone for vegPrewarmYears, so day 1 starts on the field's own seasonal
    // equilibrium rather than the arbitrary vegInit (convergence is slow in dry cells).
    for (let t = 0; t < P.vegPrewarmYears * P.yearDays; t++) { this.growth = this.seasonGrowth(t % P.yearDays); this.regrow(); }

    // per-cell scratch fields
    this.goatCount = new Uint16Array(N);
    this.wildCount = new Uint16Array(N);   // wild goats only (hunters can't hunt herd goats)
    this._social = new Uint16Array(N);     // socialField's storage (see the getter): built on first read after an index rebuild
    this._socialStale = true;
    this.logHerdNorm = 1 / Math.log1p(P.herdSat);
    this._rowSum = new Uint32Array(N);
    this._sat = new Int32Array((W + 1) * (H + 1));   // summed-area table of goatCount (goatsNear), built on first use after a rebuild
    this._satStale = true;
    this._pullExp = undefined; this._pull = null;   // wolfPull table
    this.estrusCount = new Uint16Array(N);
    this.wolfField = new Uint8Array(N);
    this.humanField = new Uint8Array(N);   // hunters present this sub-tick (goats flee them)
    this.food = new Float32Array(N);       // human plant food standing on a site (fu); goats don't eat it
    this.foodCap = new Float32Array(N);    // a site's capacity in an average year (0 = not a site)
    this.foodPatch = new Int16Array(N).fill(-1);
    this.patchYear = [];                   // this year's yield factor of each patch (masting)
    if (P.economy) this.makeFoodSites();
    this.cellStart = new Int32Array(N + 1);
    this.order = new Int32Array(1024);

    // populations
    this.goats = []; this.newborn = []; this.wolves = []; this.humans = [];
    this.herders = new Array(P.camps).fill(null);   // today's herder per camp (null: no herd routine)
    this.herdCount = new Int32Array(P.camps);       // herded goats per camp (rebuilt with the index)
    for (let k = 0; k < P.goatsInit; k++) {
      const i = this.land[randomInt(this.land.length)];
      this.goats.push(new Goat(i % W, (i / W) | 0, randomGenome(), rand() < 0.5 ? SEX_F : SEX_M, randomInt(P.yearDays * 6)));
    }
    for (let k = 0; k < P.wolvesN; k++) this.wolves.push(this.newWolf(true));
    this.buildIndex(true);

    this.tick = 0; this.day = 0; this.year = 0; this.growth = 0;
    this.resetYearStats();
  }

  newWolf(anywhere) {
    const W = this.W;
    // immigrants arrive at the upland edge; at initialisation wolves start anywhere on land
    const i = anywhere ? this.land[randomInt(this.land.length)] : (this.H - 1) * W + randomInt(W);
    return new Wolf(i % W, (i / W) | 0, randomGenome());
  }

  idx(x, y) { return y * this.W + x; }

  // Seasonal growth multiplier: a raised-cosine bump centred on growPeakDay, nonzero for
  // growFraction of the year and 0 in the lean season.
  seasonGrowth(day) {
    const P = PARAMETERS;
    const c = Math.cos(Math.PI * P.growFraction);
    const v = (Math.cos(TAU * (day - P.growPeakDay) / P.yearDays) - c) / (1 - c);
    return v > 0 ? v : 0;
  }

  // ── the day ───────────────────────────────────────────────────────────────
  update(engine) {
    const P = PARAMETERS;
    this.tick = engine.tick;
    this.day = (this.tick - 1) % P.yearDays;
    this.year = Math.floor((this.tick - 1) / P.yearDays);
    if (this.day === 0 && P.schedule) this.applySchedule();
    if (this.day === 0) this.selectionPools();
    if (this.day === 0 && P.immigrationRate > 0 && this.year >= P.humansAt) this.immigrate();
    this.growth = this.seasonGrowth(this.day);
    this.regrow();
    if (P.economy) this.growFood();
    if (this.humans.length === 0 && this.year >= P.humansAt && P.humansPerCamp > 0) this.addHumans();
    if (!this._relabelled && this.year >= Math.min(P.herdingAt, P.ibdFrom)) {   // IBD from a common baseline
      this._relabelled = true;
      for (const g of this.goats) { relabelGenome(g.genome); if (g.fetus) relabelGenome(g.fetus); if (g.fetus2) relabelGenome(g.fetus2); if (g.fetus3) relabelGenome(g.fetus3); }
    }
    this.dawn();
    for (let s = 0; s < P.dawnSteps; s++) this.dawnSub(s);
    this.buildWolfField(false);                                  // wolves lie up for the day
    for (let s = 0; s < P.daySteps; s++) this.daySub(s);
    this.mate();
    for (let s = 0; s < P.duskSteps; s++) this.duskSub(s);
    this.herdNight();
    for (let s = 0; s < P.nightSteps; s++) this.nightSub(s);
    this.lifeHistory();
    this.compact();
  }

  // Staged behaviour (P.schedule): this year's parameter changes, if any, take effect from today.
  applySchedule() {
    const P = PARAMETERS;
    if (!this._schedule) this._schedule = P.schedule.split(';').filter(e => e.trim()).map(e => {
      const i = e.indexOf(':'), set = {};
      for (const kv of e.slice(i + 1).split(',')) { const j = kv.indexOf('='), v = kv.slice(j + 1).trim(); set[kv.slice(0, j).trim()] = isNaN(+v) ? v : +v; }
      return { year: +e.slice(0, i), set };
    });
    for (const e of this._schedule) if (e.year === this.year) Object.assign(P, e.set);
  }

  managing() { return this.humans.length > 0 && this.year >= PARAMETERS.herdingAt; }

  // Immigration (P.immigrationRate): swap that share of the adult wild goats (stochastic rounding), chosen at random, for
  // immigrants from IMMIGRANT_POOL. Draws random numbers only when the rate is above 0, so rate 0 reproduces earlier runs.
  immigrate() {
    const P = PARAMETERS, pool = IMMIGRANT_POOL;
    if (!pool || !pool.length) throw new Error('immigrationRate > 0 but no immigrant pool loaded (load.mjs reads P.immigrationPool)');
    const c = this.goats.filter(g => !g.dead && g.herd < 0 && !g.ledBy && g.age >= P.yearDays && g.gestation === 0 && !g.orphan());
    const want = P.immigrationRate * c.length;
    const k = Math.min(c.length, Math.floor(want) + (rand() < want - Math.floor(want) ? 1 : 0));
    for (let i = 0; i < k; i++) {
      const j = i + randomInt(c.length - i), g = c[j]; c[j] = c[i]; c[i] = g;
      const im = pool[randomInt(pool.length)];
      g.becomeImmigrant(Float32Array.from(im.g), im.fw, im.fh);
      this.ys.immigrants++;
    }
  }

  // Spooking and straying rise with the number of goats a herder must watch (labour limits herd size).
  herdLoad(camp) {
    const n = PARAMETERS.economy ? this.camps[camp].keepN : this.herdN[camp];
    return Math.max(PARAMETERS.minLoad, this.herdCount[camp] / (PARAMETERS.herdPerHerder * Math.max(1, n)));
  }

  dawn() {
    const P = PARAMETERS, W = this.W, H = this.H, managing = this.managing();
    this.buildIndex(true);                                       // heats today, herd counts
    // roles: each camp's first human herds if the camp has a herd; others hunt or forage by fixed shares
    this.herders.fill(null);
    if (!this.herdN) this.herdN = new Int32Array(P.camps);
    this.herdN.fill(0);
    for (const h of this.humans) {
      h.herding = h.hunting = h.foraging = h.capturing = h.cutting = false; h.task = null; h.steps = 0; h.attemptsLeft = 0; h.meat = 0;
      if (h.captive) { h.role = 'return'; continue; }           // still leading a captive home
      h.role = 'camp'; h.x = h.camp.x; h.y = h.camp.y; h.target = null;
    }
    for (const c of this.camps) {
      const people = this.humans.filter(u => u.camp === c && u.role !== 'return');
      if (P.economy) { this.chooseRoles(c, people, managing); c.herdedYesterday = !!this.herders[c.id]; continue; }
      let k = 0; c.keepers.length = 0;
      if (managing && this.herdCount[c.id] > 0 && people.length) {
        const h = people[k++];
        h.role = 'herd'; h.herding = true;
        this.pickPasture(c, h);
        this.herders[c.id] = h; this.herdN[c.id] = 1; c.keepers.length = 0; c.keepers.push(h);
      }
      c.herdedYesterday = !!this.herders[c.id];
      for (; k < people.length; k++) {
        const h = people[k], r = rand();
        if (r < P.huntEffort) { h.role = 'hunt'; h.hunting = true; h.attemptsLeft = P.huntAttempts; }
        else if (r < P.huntEffort + P.forageEffort) { h.role = 'forage'; h.foraging = true; }
      }
    }
    // rut guarding: a herd doe in heat is kept at camp with chance rutGuard; with buck management the
    // herd's sires stay at camp on days a doe of theirs is kept
    const guardHerd = new Uint8Array(P.camps);
    for (const g of this.goats) {
      g.guardedToday = false;
      if (!g.dead && g.herd >= 0 && g.receptive && P.rutGuard > 0 && rand() < P.rutGuard) { g.guardedToday = true; guardHerd[g.herd] = 1; }
    }
    if (P.buckManagement && P.rutGuard > 0)
      for (const c of this.camps) if (guardHerd[c.id]) for (const s of this.siresOf(c.id)) s.guardedToday = true;
    this.humanField.fill(0);
    if (!this.forageClaim) { this.forageClaim = new Uint8Array(this.N); this.foodClaim = new Uint8Array(this.N); }
    this.forageClaim.fill(0); this.foodClaim.fill(0);
  }

  // The herd's leader picks today's pasture: penned herds start at camp, so he searches around camp;
  // an unpenned herd slept out with its herder, who moves it on to fresh grazing nearby (within 2
  // cells, ≤ 2 × herdRange of camp).
  pickPasture(c, h) {
    const P = PARAMETERS, W = this.W, H = this.H;
    const out = !P.penning && c.herdedYesterday;
    if (out) { h.x = c.lastX; h.y = c.lastY; }
    const cx = out ? h.x : c.x, cy = out ? h.y : c.y, r = out ? 2 : P.herdRange, far = 2 * P.herdRange;
    let bx = cx, by = cy, bu = -Infinity;
    for (let y = Math.max(0, cy - r); y <= Math.min(H - 1, cy + r); y++)
      for (let x = Math.max(0, cx - r); x <= Math.min(W - 1, cx + r); x++) {
        const i = y * W + x; if (this.river[i]) continue;
        if (Math.max(Math.abs(x - c.x), Math.abs(y - c.y)) > far) continue;
        const u = this.veg[i] + 0.01 * rand();
        if (u > bu) { bu = u; bx = x; by = y; }
      }
    h.target = { x: bx, y: by };
  }

  // ── the camp economy (notes/human-economy.md; after Marriott & Gershenson 2011) ─────────────────
  // Each person picks a role on leaving camp at dawn, in proportion to the camp's decaying estimate of
  // each role's return per labour-day (fu), with a floor share chosen at random so every available
  // role keeps being measured. A role never yet tried is valued at the best known return.
  chooseRoles(c, people, managing) {
    const P = PARAMETERS, roles = ['gather'];
    if (P.econHunt) roles.push('hunt');
    if (P.econHerd && managing) roles.push('herd');
    const crew = [];
    if (P.gatherSee) c.predGather = this.predictGather(c);
    for (const h of people) {
      const r = this.pickRole(c, roles);
      if (r === 'hunt') { h.role = 'hunt'; h.hunting = true; h.attemptsLeft = P.huntAttempts; }
      else if (r === 'gather') { h.role = 'forage'; h.foraging = true; }
      else { h.role = 'herd'; crew.push(h); }
    }
    this.herdN[c.id] = crew.length;
    this.assignHerdTasks(c, crew);
  }

  // The herding crew's tasks, by camp-level priority (with Chris, 2026-10-24): the first herder keeps
  // (leads to pasture, keeps the herd together, goes after strays); each further herder takes the task
  // whose decaying need signal, divided by (1 + those already on it), is largest — or, with chance
  // roleFloor, a random task. Signals (fu/day of goats at risk): keep, herd goats run off or straying;
  // guard, herd goats attacked by wolves; feed, herd goats hungry (reserve below growCondition);
  // capture, fu captured per capturer-day. A camp
  // with no herd sends its whole crew to capture.
  assignHerdTasks(c, crew) {
    const P = PARAMETERS, tasks = ['keep', 'guard', 'feed', 'capture'], n = { keep: 0, guard: 0, feed: 0, capture: 0 };
    c.guards.length = 0; c.keepers.length = 0; c.keepN = 0; c.feedBudget = 0;
    let leader = null;
    let best = -Infinity;
    for (const t of tasks) if (c.stim[t] !== null && c.stim[t] > best) best = c.stim[t];
    if (best === -Infinity) best = 1;
    for (const h of crew) {
      let t;
      if (this.herdCount[c.id] === 0) t = 'capture';
      else if (!leader) t = 'keep';
      else if (rand() < P.roleFloor) t = tasks[randomInt(tasks.length)];
      else {
        let bs = -Infinity;
        for (const u of tasks) { const v = (c.stim[u] === null ? best : c.stim[u]) / (1 + n[u]); if (v > bs) { bs = v; t = u; } }
      }
      n[t]++; h.task = t;
      if (t === 'keep' || t === 'guard') { h.herding = true; if (t === 'keep') { c.keepN++; c.keepers.push(h); if (!leader) leader = h; } else c.guards.push(h); }
      else if (t === 'feed') { h.cutting = true; }                // a feeder cuts fodder near camp for the herd
      else { h.hunting = true; h.capturing = true; h.attemptsLeft = P.huntAttempts; }
    }
    if (leader) {
      this.pickPasture(c, leader); this.herders[c.id] = leader;
      for (const h of crew) if (h.herding && h !== leader) { h.x = leader.x; h.y = leader.y; h.target = leader.target; }
    }
    this.ys.taskDays.keep += n.keep; this.ys.taskDays.guard += n.guard; this.ys.taskDays.feed += n.feed; this.ys.taskDays.capture += n.capture;
  }

  // gatherSee (with Chris, 2026-10-28): gatherers judge their return from what they can see and predict.
  // Each morning the camp sees the ripe food standing on sites within forageRange and what a day there
  // would bring home, as a gatherer choosing cells does (claimForage): min(foodLoad, foodCut × the
  // sub-ticks left after walking out, the food there). Yesterday's gatherers (at least one) take the best
  // cells, one each; the mean of those loads is worth the food it adds to what the camp will eat
  // (needScore) or its plain value. Hunting and herding are still judged by their remembered returns.
  predictGather(c) {
    const P = PARAMETERS, W = this.W, R = P.forageRange, a = this._pg || (this._pg = []);
    let m = 0;
    for (let y = Math.max(0, c.y - R); y <= Math.min(this.H - 1, c.y + R); y++)
      for (let x = Math.max(0, c.x - R); x <= Math.min(W - 1, c.x + R); x++) {
        const i = y * W + x, f = this.food[i]; if (f <= 0 || this.river[i] || this.campOf[i] >= 0) continue;
        const cut = P.daySteps - Math.max(Math.abs(x - c.x), Math.abs(y - c.y)); if (cut <= 0) continue;
        a[m++] = Math.min(P.foodLoad, P.foodCut * cut, f);
      }
    const n = Math.max(1, c.nGather || 0);
    let load = 0;
    if (m > 0) { const t = a.slice(0, m).sort((u, v) => v - u); for (let k = 0; k < Math.min(n, m); k++) load += t[k]; load /= n; }
    return P.needScore && P.storeWindows ? this.marginalFood(c, 'pfood', load) : P.plantValue * load;
  }
  retOf(c, r) { return r === 'gather' && PARAMETERS.gatherSee ? c.predGather : c.ret[r]; }

  pickRole(c, roles) {
    const P = PARAMETERS;
    if (roles.length === 1 || rand() < P.roleFloor) return roles[randomInt(roles.length)];
    let best = -Infinity;
    for (const r of roles) { const v = this.retOf(c, r); if (v !== null && v > best) best = v; }
    if (best === -Infinity) best = 1;
    let sum = 0; const w = this._rw || (this._rw = []);
    for (let k = 0; k < roles.length; k++) { const v = this.retOf(c, roles[k]); w[k] = Math.max(0, v === null ? best : v); sum += w[k]; }
    if (sum <= 0) return roles[randomInt(roles.length)];
    let x = rand() * sum, k = 0;
    while (k < roles.length - 1 && (x -= w[k]) > 0) k++;
    return roles[k];
  }

  // Each night: meat loses nutrition; the camp eats its demand (people × need + groupSink), meat first,
  // then plant food (worth plantValue to people), then slaughters herd goats by keep value while short;
  // the day's returns per labour-day update each role's decaying estimate. Herding's return is
  // offtake + Δ stock value + meatDecay × stock value (the spoilage that storing food alive avoids).
  // With storeWindows the stores keep for a shelf life instead (ageStores), people eat meat and plant
  // food together, soonest to expire first, and the storage credit is storeCredit × stock.
  campEconomy(members, day) {
    const P = PARAMETERS, ys = this.ys, Q = Math.min(3, (this.day * 4 / P.yearDays) | 0);
    for (const c of this.camps) {
      if (P.storeWindows) this.ageStores(c); else c.meat *= 1 - P.meatDecay;
      const m = members ? members[c.id] : null;
      let off = 0;
      // the opportunity cull (with Chris, 2026-10-27): every cullEvery days a goat whose keep value has
      // fallen below cullThreshold (keeping it no longer pays: grown non-sire males, does past breeding)
      // is slaughtered for meat, whether or not the camp is short
      if (P.econCull && m && m.length && this.day % P.cullEvery === 0) {
        this.cullOrder(m);
        while (m.length && -m[m.length - 1]._cullKey < P.cullThreshold) {
          const g = m.pop(), fu = P.meatYield * g.size;
          this.kill(g, CAUSE.culled); ys.culledHerd++; ys.culledValue++; off += fu; this.stash(c, 'fresh', fu);
        }
      }
      let need = P.humansPerCamp * P.needPerPerson + P.groupSink;
      ys.demand += need;
      if (P.storeWindows) need = this.eatStores(c, need);
      else {
        const em = Math.min(need, c.meat); c.meat -= em; need -= em; ys.meatEaten += em;
        const spoiled = c.pfood * P.plantSpoil;                  // the spoilage cascade (with Chris, 2026-10-25):
        c.pfood -= spoiled; c.slop += spoiled * P.slopValue; ys.slop += spoiled * P.slopValue;   // store → slop for the goats
        if (P.plantValue > 0) { const ep = Math.min(need, c.pfood * P.plantValue); c.pfood -= ep / P.plantValue; need -= ep; ys.plantEaten += ep; }
      }
      if (need > 0 && m && m.length) {
        this.cullOrder(m);
        while (need > 0 && m.length) {
          const g = m.pop(), fu = P.meatYield * g.size;
          this.kill(g, CAUSE.culled); ys.culledHerd++; ys.slaughterQ[Q]++; off += fu;
          if (P.storeWindows) { this.stash(c, 'fresh', fu); need = this.eatStores(c, need); }
          else { c.meat += fu; const e = Math.min(need, c.meat); c.meat -= e; need -= e; ys.meatEaten += e; }
        }
      }
      ys.unmet += need; ys.unmetQ[Q] += need; ys.offtakeFu += off;
      const d = day[c.id];
      if (m) {
        let stock = 0; for (const g of m) stock += P.meatYield * g.size;
        if (c.stockPrev !== null && this.herdN[c.id] > 0) { d.herd[0] += (off + stock - c.stockPrev + (P.storeWindows ? P.storeCredit : P.meatDecay) * stock); d.herd[1] += this.herdN[c.id]; }
        c.stockPrev = stock; ys.stock += stock;
      } else c.stockPrev = null;
      const sd = c.sd, ema = (t, x) => { c.stim[t] = c.stim[t] === null ? x : c.stim[t] + (x - c.stim[t]) / P.returnTau; };
      if (m && m.length) { ema('keep', sd.keep); ema('guard', sd.guard); ema('feed', sd.feed); }
      if (sd.capture[1] > 0) ema('capture', sd.capture[0] / sd.capture[1]);
      sd.keep = sd.guard = sd.feed = 0; sd.capture[0] = sd.capture[1] = 0;
      c.nGather = d.gather[1];
      for (const r of ['gather', 'hunt', 'herd']) {
        const [sum, n] = d[r]; if (n === 0) continue;
        const x = sum / n;                                       // per labour-day (herding: the camp's herd income ÷ herders)
        c.ret[r] = c.ret[r] === null ? x : c.ret[r] + (x - c.ret[r]) / P.returnTau;
        ys.roleDays[r] += n; ys.roleRet[r] += x * n; ys.labourQ[Q] += n; if (r === 'herd') ys.herdQ[Q] += n;
      }
    }
  }

  // Dawn sub-tick: herders lead their herds out toward pasture (herdTravel cells; penned herds leave the pen), hunters
  // leading a captive keep walking home; the wolves' bout ends (they hunt in every dawn sub-tick).
  dawnSub(s) {
    const P = PARAMETERS;
    for (const h of this.humans) {
      if (h.herding) for (let k = 0; k < P.herdTravel; k++) this.stepHuman(h, h.target.x, h.target.y);
      else if (h.captive) { this.stepHuman(h, h.camp.x, h.camp.y); this.deliverCaptive(h); }
    }
    this.wolfTick('dawn', s);
  }

  daySub(s) {
    const P = PARAMETERS, W = this.W;
    for (const h of this.humans) {
      if (h.herding) this.stepHuman(h, h.target.x, h.target.y);
      else if (h.captive) { this.stepHuman(h, h.camp.x, h.camp.y); this.deliverCaptive(h); }
      else if (h.hunting && h.steps < P.huntRange && this.wild3x3(h.x, h.y) === 0) this.walkUpGradient(h);
      else if (h.foraging || h.cutting) this.forage(h, s);
    }
    // hunters present now disturb the goats around them
    this.humanField.fill(0);
    const R = P.humanFieldR;
    for (const h of this.humans) {
      if (!h.hunting) continue;
      for (let y = Math.max(0, h.y - R); y <= Math.min(this.H - 1, h.y + R); y++)
        for (let x = Math.max(0, h.x - R); x <= Math.min(W - 1, h.x + R); x++) { const i = y * W + x; if (this.humanField[i] < 255) this.humanField[i]++; }
    }
    for (const g of this.goats) { if (g.dead) continue; g.step(this, 'day'); g.graze(this); }
    this.keepersRefetch();
    this.buildIndex(false);
    this.humansHunt();
  }

  duskSub(s) {
    const P = PARAMETERS;
    if (s === 0) this.humanField.fill(0);                       // hunters have gone home
    for (const h of this.humans) {
      if (h.herding && P.penning) for (let k = 0; k < P.herdTravel; k++) this.stepHuman(h, h.camp.x, h.camp.y);
      else if (h.captive) { this.stepHuman(h, h.camp.x, h.camp.y); this.deliverCaptive(h); }
      else if (!h.herding && s === 0) { h.x = h.camp.x; h.y = h.camp.y; }              // others are home (C52)
    }
    this.wolfTick('dusk', s);
    this.keepersRefetch();
  }

  stepHuman(h, tx, ty) {
    if (h.x === tx && h.y === ty) return;
    const nx = h.x + Math.sign(tx - h.x), ny = h.y + Math.sign(ty - h.y);
    if (!this.river[ny * this.W + nx]) { h.x = nx; h.y = ny; h.steps++; }
  }

  // A hunter walks one cell up the gradient of sensed WILD goats (herd goats are not quarry).
  walkUpGradient(h) {
    const W = this.W, H = this.H;
    let bx = h.x, by = h.y, bu = -Infinity;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const x = h.x + dx, y = h.y + dy;
      if (x < 0 || y < 0 || x >= W || y >= H || this.river[y * W + x]) continue;
      const u = this.wildSensed(x, y) + rand();
      if (u > bu) { bu = u; bx = x; by = y; }
    }
    if (bx !== h.x || by !== h.y) { h.x = bx; h.y = by; h.steps++; }
  }

  // Wild goats within socialRange of (x, y) (what a hunter senses from there).
  wildSensed(x, y) {
    const R = PARAMETERS.socialRange, W = this.W, H = this.H, wc = this.wildCount;
    let s = 0;
    for (let yy = Math.max(0, y - R); yy <= Math.min(H - 1, y + R); yy++)
      for (let xx = Math.max(0, x - R); xx <= Math.min(W - 1, x + R); xx++) s += wc[yy * W + xx];
    return s;
  }

  // A forager walks toward the best grazing within forageRange of camp and cuts fodder there, carrying
  // up to forageLoad kcal back to the camp store at dusk (depleting the vegetation it cuts).
  // In the economy a gatherer harvests plant food (the food field; foodCut, foodLoad) and a feeder cuts
  // vegetation (fodder; forageCut, forageLoad); otherwise a forager cuts vegetation.
  cutOf(h) { const P = PARAMETERS; return this.eatsFood(h) ? P.foodCut : P.forageCut; }
  loadOf(h) { const P = PARAMETERS; return this.eatsFood(h) ? P.foodLoad : P.forageLoad; }
  forage(h, s) {
    const P = PARAMETERS, W = this.W;
    if (!h.target) { h.load = 0; this.claimForage(h, s); }
    if (h.x !== h.target.x || h.y !== h.target.y) { this.stepHuman(h, h.target.x, h.target.y); return; }
    const want = Math.min(this.cutOf(h), this.loadOf(h) - h.load), i = h.y * W + h.x;
    let take;
    if (this.eatsFood(h)) { take = Math.min(want, this.food[i]); this.food[i] -= take; }
    else take = this.graze(i, want);
    h.load += take;
    if (want > 0 && take < 0.5 * want) this.claimForage(h, s + 1);  // this spot is spent: move on to another
  }

  // A forager claims, for the rest of the day, the unclaimed cell within forageRange of camp that will
  // yield most: min(room in the load, forageCut × sub-ticks left after walking there, what the cell
  // holds). Near cells leave more time to cut, far ones may be lusher (with Chris, 2026-10-24);
  // claiming spreads gatherers out instead of crowding one spot.
  eatsFood(h) { return PARAMETERS.economy && h.foraging; }

  claimForage(h, s) {
    const P = PARAMETERS, W = this.W, H = this.H, c = h.camp, food = this.eatsFood(h);
    const claimed = food ? this.foodClaim : this.forageClaim;
    const cutR = this.cutOf(h), room = this.loadOf(h) - (h.load || 0), left = P.daySteps - s;
    let bx = h.x, by = h.y, bu = -Infinity;
    for (let y = Math.max(0, c.y - P.forageRange); y <= Math.min(H - 1, c.y + P.forageRange); y++)
      for (let x = Math.max(0, c.x - P.forageRange); x <= Math.min(W - 1, c.x + P.forageRange); x++) {
        const i = y * W + x; if (this.river[i] || this.campOf[i] >= 0 || claimed[i]) continue;
        const d = Math.max(Math.abs(x - h.x), Math.abs(y - h.y)), cut = left - d;
        if (cut <= 0) continue;
        const there = food ? this.food[i] : (this.veg[i] - P.vegFloor) * P.vegK;
        if (food && there <= 0) continue;
        const u = Math.min(room, cutR * cut, there) - cutR / 400 * d + cutR / 4000 * rand();   // distance and noise in units of a cut
        if (u > bu) { bu = u; bx = x; by = y; }
      }
    h.target = { x: bx, y: by }; claimed[by * W + bx] = 1;
  }

  // Shelf-life stores (storeWindows, with Chris 2026-10-28). Each camp store is a queue of dated batches
  // [expiry tick, fu]; batches join in day order, so the head is always the soonest to expire. A batch
  // is good while tick < expiry. The camp's scalar (c.meat = fresh + dried, c.pfood, c.slop, c.fodder)
  // holds the store's total, so readers need not know about batches. Windows off: plain totals.
  stash(c, k, x) {
    if (!(x > 0)) return;
    const P = PARAMETERS;
    c[STORE_FIELD[k]] += x; if (!P.storeWindows) return;
    const q = c.q[k], exp = this.tick + P[STORE_DAYS[k]], last = q[q.length - 1];
    if (last && last[0] === exp) last[1] += x; else q.push([exp, x]);
  }
  storeSum(c, k) {
    const f = STORE_FIELD[k]; let s = 0;
    for (const b of c.q[k]) s += b[1];
    if (f === 'meat') for (const b of c.q[k === 'fresh' ? 'dried' : 'fresh']) s += b[1];
    c[f] = s;
  }
  // take up to x fu from store k, soonest to expire first; returns what was taken
  draw(c, k, x) {
    const q = c.q[k]; let got = 0;
    while (x - got > 1e-12 && q.length) { const b = q[0], t = Math.min(b[1], x - got); b[1] -= t; got += t; if (b[1] <= 1e-12) q.shift(); }
    this.storeSum(c, k); return got;
  }
  // remove the batches past their shelf life; returns their fu
  expire(c, k) {
    const q = c.q[k]; let x = 0;
    while (q.length && q[0][0] <= this.tick) x += q.shift()[1];
    if (x > 0) this.storeSum(c, k);
    return x;
  }
  // nightly, before eating: fresh meat past freshDays is dried (keeping dryValue of its food); dried meat
  // past dryDays is lost; plant food past plantDays becomes slop for the goats
  ageStores(c) {
    const P = PARAMETERS, ys = this.ys;
    const fr = this.expire(c, 'fresh'); if (fr > 0) { this.stash(c, 'dried', fr * P.dryValue); ys.dried += fr * P.dryValue; }
    ys.driedLost += this.expire(c, 'dried');
    const pf = this.expire(c, 'pfood'); if (pf > 0) { this.stash(c, 'slop', pf * P.slopValue); ys.slop += pf * P.slopValue; }
  }
  // people eat fresh meat, dried meat and plant food, soonest to expire first; returns the unmet need
  eatStores(c, need) {
    const P = PARAMETERS, ys = this.ys, kinds = P.plantValue > 0 ? ['fresh', 'dried', 'pfood'] : ['fresh', 'dried'];
    while (need > 1e-12) {
      let k = null, e = Infinity;
      for (const j of kinds) { const q = c.q[j]; if (q.length && q[0][0] < e) { e = q[0][0]; k = j; } }
      if (k === null) break;
      const v = k === 'pfood' ? P.plantValue : 1, b = c.q[k][0], t = Math.min(b[1], need / v);
      b[1] -= t; need -= t * v; if (b[1] <= 1e-12) c.q[k].shift();
      if (k === 'pfood') ys.plantEaten += t * v; else ys.meatEaten += t;
    }
    this.storeSum(c, 'fresh'); this.storeSum(c, 'pfood');
    return need > 1e-12 ? need : 0;
  }
  // needScore (with Chris, 2026-10-28): the human food the camp will eat from its stores, eating
  // soonest to expire first at its daily demand with nothing more coming in, optionally with one more
  // batch (kind xk, xa fu) as if stashed today. Whatever expires by day e can feed at most demand × (e −
  // today) (deliveries come before tonight's meal); fresh meat left uneaten is dried and eaten later.
  eatenForward(c, xk, xa) {
    const P = PARAMETERS, D = P.humansPerCamp * P.needPerPerson + P.groupSink, t = this.tick, pv = P.plantValue, der = [];
    const S = [{ q: c.q.fresh, f: true, v: 1 }];
    const X = xk ? { q: [[t + P[STORE_DAYS[xk]], xa]], f: xk === 'fresh', v: xk === 'pfood' ? pv : 1 } : null;
    if (X && X.f) S.push(X);
    S.push({ q: c.q.dried, v: 1 }, { q: der, v: 1 }, { q: c.q.pfood, v: pv });
    if (X && !X.f) S.push(X);
    for (const s of S) s.i = 0;
    let E = 0;
    for (;;) {
      let s = null, e = Infinity;
      for (const u of S) if (u.i < u.q.length && u.q[u.i][0] < e) { e = u.q[u.i][0]; s = u; }
      if (s === null) return E;
      const a = s.q[s.i++][1] * s.v, take = Math.min(a, Math.max(0, D * (e - t) - E));
      E += take;
      if (s.f && a - take > 1e-12) der.push([e + P.dryDays, (a - take) * P.dryValue]);
    }
  }
  // a delivery's worth to the camp: the food it adds to what will be eaten
  marginalFood(c, k, x) { return x > 0 ? this.eatenForward(c, k, x) - this.eatenForward(c, null, 0) : 0; }

  // At day's end each forager's load joins the camp store (which spoils slowly, or keeps fodderDays).
  storeFodder() {
    const P = PARAMETERS;
    for (const c of this.camps) {
      if (P.storeWindows) {
        this.ys.fodderLost += this.expire(c, 'fodder');
        const off = this.expire(c, 'slop'); if (off > 0) this.dumpHeap(c, off);   // rotten slop → dump heap
        continue;
      }
      c.fodder *= 1 - P.fodderSpoil;
      if (P.economy && c.slop > 0) { const off = c.slop * P.fodderSpoil; c.slop -= off; this.dumpHeap(c, off); }   // slop → dump heap
    }
    const day = this._day || (this._day = this.camps.map(() => ({ gather: [0, 0], hunt: [0, 0], herd: [0, 0] })));
    for (const d of day) { d.gather[0] = d.gather[1] = d.hunt[0] = d.hunt[1] = d.herd[0] = d.herd[1] = 0; }
    for (const h of this.humans) {
      const d = day[h.camp.id];
      if (h.foraging) {
        if (P.economy) { const x = h.load || 0, v = P.needScore && P.storeWindows ? this.marginalFood(h.camp, 'pfood', x) : P.plantValue * x;
          if (P.storeWindows) this.stash(h.camp, 'pfood', x); else h.camp.pfood += x;
          this.ys.foodGathered += x; this.ys.gatherScored += v; d.gather[0] += v; d.gather[1]++; }
        else if (h.load) { this.stash(h.camp, 'fodder', h.load); this.ys.foraged += h.load; }
      }
      if (h.cutting && h.load) { this.stash(h.camp, 'fodder', h.load); this.ys.foraged += h.load; }
      if (h.role === 'hunt' && P.altGame > 0 && P.economy && !h.capturing && !(h.meat > 0) && rand() < P.altGame) { h.meat = P.altYield; this.ys.altKills++; }   // other game (with Chris, 2026-10-29)
      if (h.role === 'hunt') { const x = h.meat || 0, v = P.needScore && P.storeWindows ? this.marginalFood(h.camp, 'fresh', x) : x;
        if (P.storeWindows) this.stash(h.camp, 'fresh', x); else h.camp.meat += x;
        this.ys.meatHunted += x; this.ys.huntScored += v; d.hunt[0] += v; d.hunt[1]++; h.meat = 0; }
      if (h.task === 'capture') h.camp.sd.capture[1]++;
      h.load = 0; h.target = h.herding ? h.target : null;
    }
    return day;
  }

  // Wild goats in the 3×3 around (x, y) (what a hunter can see).
  wild3x3(x, y) {
    let s = 0;
    for (let yy = Math.max(0, y - 1); yy <= Math.min(this.H - 1, y + 1); yy++)
      for (let xx = Math.max(0, x - 1); xx <= Math.min(this.W - 1, x + 1); xx++) s += this.wildCount[yy * this.W + xx];
    return s;
  }
  // All goats in the 3×3 around cell i (the confusion effect).
  goats3x3(i) { return this.goatsNear(i % this.W, (i / this.W) | 0, 1); }

  // ── humans: hunting and capture (MODEL C52, C53) ─────────────────────────
  addHumans() {
    for (const c of this.camps) for (let k = 0; k < PARAMETERS.humansPerCamp; k++) this.humans.push(new Human(c));
  }

  // One sub-tick of hunting: a hunter with wild goats in its 3×3 and attempts left tries once. While its
  // herd is below target it first tries to take an approachable goat alive (led home).
  humansHunt() {
    const P = PARAMETERS, W = this.W, H = this.H, goats = this.goats, order = this.order, start = this.cellStart;
    const cand = this._hc || (this._hc = []), wts = this._hw || (this._hw = []), ps = this._hp || (this._hp = []), cells = this._hcell || (this._hcell = []);
    const managing = this.managing(), capOpen = managing && this.year < P.captureUntil;   // R3: no captures from captureUntil
    for (const h of this.humans) {
      if (!h.hunting || h.captive || h.attemptsLeft <= 0) continue;
      if (P.shotChance > 0 && P.economy && !h.capturing && this.shoot(h)) continue;   // a ranged shot used the attempt (economy hunters)
      // Fixed-policy hunters with shots (with Chris, 2026-10-30): the capture draw comes first; an attempt
      // that is not a capture try is a shot if a wild goat is in sight within shotRange, else a stalk.
      let cap = null;
      if (P.shotChance > 0 && !P.economy) {
        cap = capOpen && this.herdCount[h.camp.id] < P.herdTarget && rand() < P.captureRate;
        if (!cap && this.shoot(h)) continue;
      }
      if (this.wild3x3(h.x, h.y) === 0) continue;
      h.attemptsLeft--; this.ys.huntTries++;
      if (h.capturing) {                                          // economy: a capturer only takes goats alive
        const g = this.visibleWild(h);
        if (g) { if (this.approach(g, P.captureSteps)) { h.camp.sd.capture[0] += P.meatYield * g.size; this.capture(g, h); } else g.learnFear('fearOfHumans', 0.5); }
        continue;
      }
      if (!P.economy && (cap === null ? capOpen && this.herdCount[h.camp.id] < P.herdTarget && rand() < P.captureRate : cap)) {
        // try to take a goat alive: pick one he can see, then close in; it is caught only if it
        // never bolts on the way (the approach test, MODEL C53)
        const g = this.visibleWild(h);
        if (g) { if (this.approach(g, P.captureSteps)) this.capture(g, h); else g.learnFear('fearOfHumans', 0.5); continue; }
      }
      let nc = 0, sum = 0;
      for (let y = Math.max(0, h.y - 1); y <= Math.min(H - 1, h.y + 1); y++)
        for (let x = Math.max(0, h.x - 1); x <= Math.min(W - 1, h.x + 1); x++) {
          const i = y * W + x;
          for (let o = start[i]; o < start[i + 1]; o++) {
            const g = goats[order[o]]; if (g.dead || g.herd >= 0) continue;
            if (rand() >= P.humanDetect * (1 - 0.5 * P.camouflage * g.tr[T_W])) continue;
            // the stalk: a wary goat may spot the approaching hunter and bolt first
            if (!g.alarmed && rand() < P.stalkDetect * g.tr[T_R] * g.fearOfHumans) { g.alarmed = true; if (P.alarmLearn > 0) g.learnFear('fearOfHumans', P.alarmLearn); }
            const p = this.huntChance(g, i, false);
            cand[nc] = g; ps[nc] = p; cells[nc] = i; wts[nc] = p * g.size; sum += wts[nc]; nc++;
          }
        }
      if (nc === 0 || sum <= 0) continue;
      let r = rand() * sum, k = 0;
      while (k < nc - 1 && (r -= wts[k]) > 0) k++;
      const prey = cand[k];
      let p = ps[k];
      if (!prey.alarmed && this.warned(prey, cells[k], 'fearOfHumans')) p = this.huntChance(prey, cells[k], true);
      if (rand() < p) {
        this.kill(prey, CAUSE.hunted); h.kills++; this.ys.hunted++; this.witness(cells[k], 'fearOfHumans');
        h.meat += P.meatYield * prey.size;
        h.attemptsLeft = 0;                                        // one carcass a day
        const kid = prey.orphan();                                  // her orphaned kid is taken home alive (one of a litter)
        if (managing && P.captureOrphans && this.year < P.captureUntil && kid && !kid.dead && kid.herd < 0 && this.herdCount[h.camp.id] < P.herdTarget) this.capture(kid, h);
      } else { prey.alarmed = true; prey.learnFear('fearOfHumans', 1); }
    }
  }

  // The ranged shot (with Chris, 2026-10-28): before closing in, a hunter who can see a wild goat within
  // shotRange cells shoots, before the goat can spot the stalk (so its reactivity plays no part). It hits
  // with shotChance (less on cliffs; less if the goat is already alarmed and moving). A hit is a kill; a
  // miss alarms every wild goat within range, and the target learns fear as from a survived attack. True
  // if a shot was taken (it uses the attempt).
  shoot(h) {
    const P = PARAMETERS, W = this.W, H = this.H, goats = this.goats, order = this.order, start = this.cellStart, R = P.shotRange;
    const seen = this._shot || (this._shot = []), at = this._shotAt || (this._shotAt = []); let n = 0;
    for (let y = Math.max(0, h.y - R); y <= Math.min(H - 1, h.y + R); y++)
      for (let x = Math.max(0, h.x - R); x <= Math.min(W - 1, h.x + R); x++) {
        const i = y * W + x;
        for (let o = start[i]; o < start[i + 1]; o++) {
          const g = goats[order[o]]; if (g.dead || g.herd >= 0) continue;
          if (rand() < P.humanDetect * (1 - 0.5 * P.camouflage * g.tr[T_W])) { seen[n] = g; at[n] = i; n++; }
        }
      }
    if (n === 0) return false;
    h.attemptsLeft--; this.ys.shots++;
    const k = randomInt(n), prey = seen[k], i = at[k];
    let p = P.shotChance * (prey.alarmed ? 1 - P.huntFlee : 1);
    if (this.escape[i]) p *= 1 - P.humanRefuge;
    if (rand() < p) {
      this.kill(prey, CAUSE.hunted); h.kills++; this.ys.hunted++; this.ys.shotKills++; this.witness(i, 'fearOfHumans');
      h.meat += P.meatYield * prey.size;
      h.attemptsLeft = 0;                                        // one carcass a day
      const kid = prey.orphan();
      if (this.managing() && P.captureOrphans && this.year < P.captureUntil && kid && !kid.dead && kid.herd < 0 && this.herdCount[h.camp.id] < P.herdTarget) this.capture(kid, h);
      return true;
    }
    prey.learnFear('fearOfHumans', 1);
    for (let y = Math.max(0, h.y - R); y <= Math.min(H - 1, h.y + R); y++)
      for (let x = Math.max(0, h.x - R); x <= Math.min(W - 1, h.x + R); x++) {
        const j = y * W + x;
        for (let o = start[j]; o < start[j + 1]; o++) {
          const g = goats[order[o]]; if (g.dead || g.herd >= 0 || g.alarmed) continue;
          g.alarmed = true; if (P.alarmLearn > 0 && g !== prey) g.learnFear('fearOfHumans', P.alarmLearn);
        }
      }
    prey.alarmed = true;
    return true;
  }

  // A wild goat the hunter can see in his 3×3 (detection as in hunting), chosen at random.
  visibleWild(h) {
    const P = PARAMETERS, W = this.W, H = this.H, goats = this.goats, order = this.order, start = this.cellStart;
    const seen = this._seen || (this._seen = []); let n = 0;
    for (let y = Math.max(0, h.y - 1); y <= Math.min(H - 1, h.y + 1); y++)
      for (let x = Math.max(0, h.x - 1); x <= Math.min(W - 1, h.x + 1); x++) {
        const i = y * W + x;
        for (let o = start[i]; o < start[i + 1]; o++) {
          const g = goats[order[o]]; if (g.dead || g.herd >= 0 || g.alarmed) continue;
          if (rand() < P.humanDetect * (1 - 0.5 * P.camouflage * g.tr[T_W])) seen[n++] = g;
        }
      }
    return n ? seen[randomInt(n)] : null;
  }

  // The approach test (capture and retrieval): a person closes in over `steps` steps; at each the goat
  // may notice and bolt, with chance stalkDetect × R × fear of humans. True if it never bolts.
  approach(g, steps) {
    const p = Math.min(1, PARAMETERS.stalkDetect * g.tr[T_R] * g.fearOfHumans);
    for (let k = 0; k < steps; k++) if (rand() < p) { g.alarmed = true; return false; }
    return true;
  }

  // A herd goat that ran off: if it is beyond keepRadius of its herder he goes after it at once. Beyond
  // searchRange it is lost; otherwise he closes in over the distance (the approach test), and it is
  // lost if it bolts, else back with him.
  refetch(g, h) {
    const P = PARAMETERS, d = Math.max(Math.abs(g.x - h.x), Math.abs(g.y - h.y));
    if (d <= P.keepRadius) return;
    if (d > P.searchRange || !this.approach(g, d)) { g.herd = -1; this.ys.escaped++; this.ys.runOffLost++; return; }
    g.x = h.x; g.y = h.y; this.ys.refetched++;
  }

  // Each keeper makes at most one attempt per sub-tick on the nearest loose run-off of his herd within
  // searchRange that has been loose for chaseDelay sub-ticks (time to come back on its own first): he closes in over the distance (the approach test); it is lost if it bolts, else back
  // with him (with Chris, 2026-10-24: between "always comes back" and "always needs fetching").
  keepersRefetch() {
    const P = PARAMETERS;
    if (P.refetchRunOffs !== 2) return;
    let keepers = false; for (const c of this.camps) if (c.keepers.length) keepers = true;
    if (!keepers) return;                                        // nobody to go after them (the scan below only feeds keepers)
    const loose = this._loose || (this._loose = this.camps.map(() => []));
    for (const l of loose) l.length = 0;
    let any = false;
    for (const g of this.goats) if (!g.dead && g.loose && g.herd >= 0 && g.looseTicks >= P.chaseDelay) { loose[g.herd].push(g); any = true; }
    if (!any) return;
    for (const c of this.camps) {
      const l = loose[c.id];
      for (const k of c.keepers) {
        let best = null, bd = Infinity;
        for (const g of l) { if (!g.loose || g.herd < 0) continue; const d = Math.max(Math.abs(g.x - k.x), Math.abs(g.y - k.y)); if (d < bd) { bd = d; best = g; } }
        if (!best || bd > P.searchRange) continue;
        best.loose = false;
        if (bd <= P.keepRadius) continue;
        if (this.approach(best, bd)) { best.x = k.x; best.y = k.y; this.ys.refetched++; }
        else { best.herd = -1; this.ys.escaped++; this.ys.runOffLost++; }
      }
    }
  }

  // A captive joins the camp's herd and is led home by the hunter (walking with him).
  capture(g, h) {
    const c = h.camp;
    g.herd = c.id; g.capturedYear = this.year; g.gsc = 0; g.pgs = 0; g.wv = null; g.ledBy = h; this.ys.captured++;
    g._kidsAtYearStart = g.kids;                                 // the camp record counts only kids born in the herd
    g.seen = [0, 0, 0]; g.seenFrom = this.year * PARAMETERS.yearDays + this.day;   // the herder starts watching it
    this.ys.capturedR += g.tr[T_R];
    h.captive = g; h.hunting = false; h.attemptsLeft = 0; this.herdCount[c.id]++;
  }

  // A hunter who has walked his captive home hands it over.
  deliverCaptive(h) {
    const g = h.captive;
    if (!g) return;
    if (g.dead) { h.captive = null; return; }
    if (h.x === h.camp.x && h.y === h.camp.y && g.x === h.x && g.y === h.y) { g.ledBy = null; h.captive = null; if (h.role === 'return') h.role = 'camp'; }
  }

  huntChance(g, i, warned) {
    const P = PARAMETERS, Reff = Math.min(1, g.tr[T_R] * g.fearOfHumans);
    let p = P.huntBase * (1 - P.huntFlee * (g.alarmed ? 1 : warned ? P.warnShare : 0.5 * Reff));
    if (this.escape[i]) p *= 1 - P.humanRefuge;
    return p;
  }

  // ── herd at night (MODEL C56–C59) ────────────────────────────────────────
  // After dusk: a herd goat that did not come home (penned herds) or is more than keepRadius from its
  // herder (unpenned) has strayed; the herder goes back for it (the approach test); the kept habituate;
  // then offtake and culling.
  herdNight() {
    const P = PARAMETERS, ys = this.ys;
    const day = this.storeFodder();
    if (!this.managing()) { if (P.economy) this.campEconomy(null, day); return; }
    for (const g of this.goats) if (!g.dead && g.herd < 0)            // wild goats within herdRange of a camp (counter only)
      for (const c of this.camps) if (Math.max(Math.abs(g.x - c.x), Math.abs(g.y - c.y)) <= P.herdRange) ys.wildNearCamp++;
    ys.campDays += this.camps.length;
    const members = this._members || (this._members = this.camps.map(() => []));
    for (const m of members) m.length = 0;
    for (const g of this.goats) {
      if (g.dead || g.herd < 0 || g.ledBy) continue;
      const h = this.herders[g.herd], c = this.camps[g.herd];
      if (h && !g.isKeptAtCamp() && !g.isSheltered()) {
        const strayed = P.penning ? (g.x !== c.x || g.y !== c.y)
                                  : Math.max(Math.abs(g.x - h.x), Math.abs(g.y - h.y)) > P.keepRadius;
        if (strayed) {
          c.sd.keep += P.meatYield * g.size;
          // the herder goes back for it: beyond searchRange it is lost; otherwise he closes in over the
          // distance, and it is lost if it bolts (the approach test), else brought in
          const from = P.penning ? c : h, d = Math.max(Math.abs(g.x - from.x), Math.abs(g.y - from.y));
          if (d > P.searchRange || !this.approach(g, d)) { g.herd = -1; g.loose = false; ys.escaped++; continue; }
          g.x = from.x; g.y = from.y;                              // brought back to the pen / the herder
        }
      }
      g.loose = false;
      g.habituate();
      if ((P.cullRule === 'attack' || P.sireRule === 'gentle') && rand() < P.buttRate * g.tr[T_A]) g.seen[2]++;   // butts the herder (seen only; no draw otherwise)
      members[g.herd].push(g);
    }
    for (const m of members) for (const g of m)                     // herd composition per camp-day (counter only): kids, does, bucks, other
      ys.herdComp[g.age < P.yearDays ? 0 : g.age >= g.breedAge ? (g.sex === SEX_F ? 1 : 2) : 3]++;
    for (const c of this.camps) { const h = this.herders[c.id]; if (h) { c.lastX = h.x; c.lastY = h.y; } }
    for (const c of this.camps) c.milkPool *= P.milkKeep;  // milk keeps poorly
    if (P.economy && (P.surplusCull || P.winterCull)) throw new Error('surplusCull and winterCull are for the offtake-rate cull (economy 0)');
    if (P.economy) this.campEconomy(members, day);
    else for (const m of members) {
      // offtake: slaughter for meat at offtakeRate of the herd per year (stochastic, one animal at a
      // time, chosen by the cull rule), then cull anything above herdTarget
      let n = 0; const rate = P.leanPulse > 0 ? P.offtakeRate * this.leanPulseFactor() : P.offtakeRate;
      const daily = rate * m.length / P.yearDays;
      if (rand() < daily - Math.floor(daily)) n++; n += Math.floor(daily);
      if (P.cullFloor > 0) n = Math.max(0, Math.min(n, m.length - P.cullFloor));   // never eat the herd below the floor (the draw above is kept)
      ys.offtakeDue += n;                                          // counter: offtake draws due today
      if ((P.surplusCull || P.winterCull) && m.length) {            // surplus males, then the winter cull; their meat counts against the offtake
        const c = this.camps[m[0].herd];
        if (c.cullCreditYear !== this.year) { c.cullCreditYear = this.year; c.cullCredit = 0; }   // credit lasts the year only
        if (P.surplusCull) c.cullCredit += this.cullSurplusBucks(m);
        if (P.winterCull && this.growth === 0 && this.seasonGrowth((this.day + P.yearDays - 1) % P.yearDays) > 0) c.cullCredit += this.cullToFodder(m, c);
        const k = Math.min(n, c.cullCredit); ys.offtakeCredited += k; n -= k; c.cullCredit -= k;
      }
      if (n === 0 && m.length <= P.herdTarget) continue;
      this.cullOrder(m);
      for (; n > 0 && m.length > 0; n--) { const g = m.pop(); this.tallyCull(g, 'offtake'); this.kill(g, CAUSE.culled); ys.culledHerd++; }
      while (m.length > P.herdTarget) { this.kill(m.pop(), CAUSE.culled); ys.culledHerd++; }
    }
    this.buildIndex(false);                                      // retrieved strays moved; wolves see where goats are
  }

  // The herder's sires: keepSires adult herd males of a camp, by sireRule: the oldest, or (with Chris, 2026-11-03)
  // by what the herder can see: 'random' (a fixed preference per buck, the control), 'calm' (fewest seen run-offs
  // per year watched), 'gentle' (fewest seen butts per year watched), 'large' (biggest now), 'milk' (with Chris
  // 2026-11-09: whose dam gave the camp most milk a year, damMilk), 'deep' / 'shallow' (with Chris 2026-11-10: most / fewest
  // generations since the wild, Goat.wildDepth; lineage alone, no trait, the grain paper's isolation test), 'homebred' (with
  // Chris 2026-11-10: the lineage a herder can know, generations of camp-born dams on the maternal line, gsc, remembered
  // up to herdMemory; 1 = camp-born over captured), 'marked' (most coat marking, the neutral appearance gene C); ties at the preference.
  siresOf(camp) {
    const P = PARAMETERS, Y = P.yearDays;
    const m = this.goats.filter(g => !g.dead && g.herd === camp && g.sex === SEX_M && g.age >= g.breedAge);
    if (P.sireRule === 'oldest') m.sort((a, b) => b.age - a.age);
    else {
      const now = this.year * Y + this.day;
      for (const g of m) {
        if (g._sireKey === undefined) g._sireKey = rand();
        const watched = (now - g.seenFrom) / Y + 1;
        g._sireRank = P.sireRule === 'random' ? 0 : P.sireRule === 'calm' ? g.seen[0] / watched
          : P.sireRule === 'gentle' ? g.seen[2] / watched : P.sireRule === 'large' ? -g.size
          : P.sireRule === 'milk' ? -this.damMilk(g) : P.sireRule === 'deep' ? -g.wildDepth()
          : P.sireRule === 'shallow' ? g.wildDepth() : P.sireRule === 'homebred' ? -Math.min(g.gsc, P.herdMemory)
          : P.sireRule === 'marked' ? -g.tr[T_C] : NaN;
        if (Number.isNaN(g._sireRank)) throw new Error(`unknown sireRule ${P.sireRule}`);
      }
      m.sort((a, b) => a._sireRank - b._sireRank || a._sireKey - b._sireKey);
    }
    return m.slice(0, Math.max(1, P.keepSires));
  }

  // surplusCull (with Chris, 2026-11-12): slaughter a camp's weaned males beyond its sires (siresOf) and insuranceBucks spares
  // (the oldest other weaned males), whatever the floor; removes them from the camp's members m and returns how many.
  cullSurplusBucks(m) {
    const P = PARAMETERS, sires = this.siresOf(m[0].herd);
    const spare = m.filter(g => g.sex === SEX_M && g.age >= P.weanAge && !sires.includes(g)).sort((a, b) => b.age - a.age);
    if (spare.length <= P.insuranceBucks) return 0;
    const cut = new Set(spare.slice(P.insuranceBucks));
    for (const g of cut) { this.tallyCull(g, 'surplus'); this.kill(g, CAUSE.culled); this.ys.culledHerd++; this.ys.surplusBucks++; }
    let j = 0; for (const g of m) if (!cut.has(g)) m[j++] = g;
    m.length = j;
    return cut.size;
  }

  // Count a herd cull by kind (2026-11-13, with Chris: how the culls interact): kids under a year, breeding does, breeding
  // bucks, other; and goats captured themselves (gsc 0). Counter only.
  // leanPulse: today's offtake multiplier; leanPulse of the year's offtake falls in the first leanPulseDays of the lean
  // season and the rest evenly over the other days (mean multiplier over the year = 1)
  springDay() {                                                  // days since the lean season ended (growth began)
    const P = PARAMETERS, Y = P.yearDays;
    if (this._growStart === undefined) { let d = 0; while (!(this.seasonGrowth(d) > 0 && this.seasonGrowth((d + Y - 1) % Y) === 0)) d++; this._growStart = d; }
    return (this.day - this._growStart + Y) % Y;
  }
  leanPulseFactor() {
    const P = PARAMETERS, Y = P.yearDays;
    if (this._leanStart === undefined) { let d = 0; while (!(this.seasonGrowth(d) === 0 && this.seasonGrowth((d + Y - 1) % Y) > 0)) d++; this._leanStart = d; }
    return (this.day - this._leanStart + Y) % Y < P.leanPulseDays ? P.leanPulse * Y / P.leanPulseDays : (1 - P.leanPulse) * Y / (Y - P.leanPulseDays);
  }

  tallyCull(g, kind) {
    const Y = PARAMETERS.yearDays, t = this.ys.cullTally[kind];
    t[g.age < Y ? 0 : g.age >= g.breedAge ? (g.sex === SEX_F ? 1 : 2) : 3]++;
    if (g.gsc === 0) t[4]++;
  }

  // winterCull (with Chris, 2026-11-12: "cull does before feeding them over winter"; budget "only for breeding does and
  // young"): on the first lean day the herder budgets winterBudget of a full ration (provision × size^0.75 a day) through the lean days
  // ahead for each doe of breeding age and each goat under a year; bucks and dry yearlings winter on grazing. While the
  // camp's fodder store falls short he slaughters among those budgeted goats in the cull rule's order (lowest keep value
  // first), never below cullFloor. With winterCullAll every herd goat is budgeted and may be culled, so grown males and old
  // does (the lowest keep values) go first. Removes them from the camp's members m; returns how many.
  cullToFodder(m, c) {
    const P = PARAMETERS, Y = P.yearDays;
    let lean = 1; while (lean < Y && this.seasonGrowth((this.day + lean) % Y) === 0) lean++;   // lean days ahead, today included
    const fed = P.winterCullAll ? () => true : g => (g.sex === SEX_F && g.age >= g.breedAge) || g.age < Y;   // winterCullAll: every goat, bucks included
    const ration = g => P.provision * P.winterBudget * g.p75() * lean;   // the herder's budget for a fed goat (winterBudget 1: as before, bit for bit)
    let need = 0; for (const g of m) if (fed(g)) need += ration(g);
    const have = c.fodder + c.slop;
    if (need <= have) return 0;
    this.cullOrder(m);
    const cut = new Set();
    for (let k = m.length - 1; k >= 0 && need > have && m.length - cut.size > Math.max(0, P.cullFloor); k--) {
      const g = m[k]; if (!fed(g)) continue;
      need -= ration(g); cut.add(g); this.tallyCull(g, 'winter');
      this.kill(g, CAUSE.culled); this.ys.culledHerd++; this.ys.winterCulled++;
    }
    let j = 0; for (const g of m) if (!cut.has(g)) m[j++] = g;
    m.length = j;
    return cut.size;
  }

  // fodderRation (with Chris, 2026-11-12): each lean-season day, the share of what its goats want that each camp can give
  // each feeding class (world._rationF[camp][class]) so its fodder store lasts the lean days left: class 0 (pregnant or
  // nursing does, goats under a year) is fed first, then class 1 (the rest). Goat.daily takes want × its class's share.
  // No random draws.
  rationFodder() {
    const P = PARAMETERS, Y = P.yearDays;
    let left = 1;
    if (this.growth === 0) while (left < Y && this.seasonGrowth((this.day + left) % Y) === 0) left++;   // lean days left, today included
    else left = P.feedExtend - this.springDay();                                                     // feedExtend: days left in the window
    const want = this.camps.map(() => [0, 0]);
    for (const g of this.goats) {
      if (g.dead || g.herd < 0) continue;
      want[g.herd][g.rationClass()] += this.growth === 0 ? Math.max(0, Math.min(P.provision * g.p75(), g.reserveCap() - g.E))
        : g.isKeptAtCamp() ? 0 : g.springWant(0);                 // spring: kept-at-camp goats are fed as before; kids' milk not yet known
    }
    this._rationF = this.camps.map((c, i) => {
      let b = (c.fodder + c.slop) / left; const f = [0, 0];
      for (let k = 0; k < 2; k++) { const w = want[i][k]; if (w > 0) { const a = Math.min(w, b); f[k] = a / w; b -= a; } }
      return f;
    });
  }

  // A buck's dam's milk record, kcal a year: her milk given to the camp per year since breeding age, blended with
  // the camp's mean by the length of her record (as the keep value does); a dam the herder never milked (a captive's
  // wild mother, or none) counts as the camp's mean.
  damMilk(g) {
    const P = PARAMETERS, c = this.camps[g.herd], r = c && c.record, herdMilk = r && r.yrs > 0 ? r.milk / r.yrs : 0;
    const d = g.mother;
    if (!d || d.herd !== g.herd) return herdMilk;
    const yrs = Math.max(0, (d.age - P.femaleMinAge) / P.yearDays), w = yrs / (yrs + P.recordWeight);
    return w * (yrs > 0 ? d.milkYield / yrs : 0) + (1 - w) * herdMilk;
  }

  // Order a herd so the animals to cull first are at the END (cullRule):
  //   random      H2: no preference
  //   opportunity H3+: lowest keep value first (cullByOpportunity)
  //   flight, return, attack: phenotype profiles, the random rule plus what the herder has seen
  //   youngMales, temperament: older strict-priority rules, kept for comparison
  // Then, with buckCull / doeCull set (with Chris, 2026-11-10), each sex's own rule picks which of that sex go, in the
  // places the overall rule gave that sex (so the overall rule still sets how many of each sex are eaten).
  cullOrder(m) {
    if (PARAMETERS.econCull && (PARAMETERS.buckCull || PARAMETERS.doeCull)) throw new Error('buckCull/doeCull need the count cull (econCull 0)');
    this.cullOrderAll(m);
    if (PARAMETERS.buckCull) this.cullBySex(m, SEX_M, PARAMETERS.buckCull);
    if (PARAMETERS.doeCull) this.cullBySex(m, SEX_F, PARAMETERS.doeCull);
  }

  // One sex's cull rule, within its places in the herd's cull order (culled first at the END):
  //   random    no preference          calm      the most run-offs seen per year watched go first
  //   large     the smallest for their sex and age (years) in the herd go first
  //   homebred  the fewest generations of camp-born dams (gsc, up to herdMemory) go first: captives first
  //   youngMales (bucks) males of 0.5-2.5 years first, then older non-sires, then kids
  // The herder's sires (as the cull keeps them) are never taken by a buck rule.
  cullBySex(m, sex, rule) {
    const P = PARAMETERS, Y = P.yearDays, at = [], xs = [];
    for (let i = 0; i < m.length; i++) if (m[i].sex === sex) { at.push(i); xs.push(m[i]); }
    if (!xs.length) return;
    const sires = sex === SEX_M ? this.siresOf(xs[0].herd) : [];
    const now = this.year * Y + this.day, mean = {};
    if (rule === 'large') for (const g of xs) { const a = Math.floor(g.age / Y), e = mean[a] || (mean[a] = [0, 0]); e[0] += g.size; e[1]++; }
    for (const g of xs) {
      const a = Math.floor(g.age / Y);
      g._sexKey = rule === 'random' ? 0 : rule === 'calm' ? g.seen[0] / ((now - g.seenFrom) / Y + 1)
        : rule === 'large' ? -g.size / (mean[a][0] / mean[a][1]) : rule === 'homebred' ? -Math.min(g.gsc, P.herdMemory)
        : rule === 'youngMales' && sex === SEX_M ? (g.age >= 0.5 * Y && g.age < 2.5 * Y ? 3 : g.age >= 2.5 * Y ? 2 : 1) : NaN;
      if (Number.isNaN(g._sexKey)) throw new Error(`unknown ${sex === SEX_M ? 'buckCull' : 'doeCull'} ${rule}`);
      if (sires.includes(g)) g._sexKey = -Infinity;
      g._sexTie = rand();
    }
    xs.sort((a, b) => a._sexKey - b._sexKey || a._sexTie - b._sexTie);
    for (let k = 0; k < at.length; k++) m[at[k]] = xs[k];
  }

  cullOrderAll(m) {
    const P = PARAMETERS, Y = P.yearDays;
    if (P.cullRule === 'opportunity') return this.cullByOpportunity(m);
    for (const g of m) g._cullKey = rand();                     // random tie-break
    if (P.cullRule === 'youngMales') {
      const sires = m.filter(g => g.sex === SEX_M && g.age >= 2.5 * Y).sort((a, b) => b.age - a.age).slice(0, P.keepSires);
      for (const g of m) {
        if (g.sex === SEX_M) g._cullKey += sires.includes(g) ? 0 : (g.age >= 0.5 * Y && g.age < 2.5 * Y ? 30 : g.age >= 2.5 * Y ? 20 : 10);
        else if (g.age > P.cullOldAge * Y) g._cullKey += 5;
      }
    } else if (P.cullRule === 'temperament') {
      for (const g of m) g._cullKey += 10 * g.tr[T_R] * g.fearOfHumans;
    } else if (P.cullRule === 'random' && P.keepChosenSires && m.length) {
      for (const s of this.siresOf(m[0].herd)) s._cullKey = -1;   // random rule, but the chosen sires are not eaten
    } else if (P.cullRule === 'random' && P.keepLastSires) {
      const bucks = m.filter(g => g.sex === SEX_M && g.age >= g.breedAge);   // random rule, but not the last sires
      if (bucks.length <= P.keepSires) for (const g of bucks) g._cullKey = -1;
    } else if (P.cullRule === 'flight' || P.cullRule === 'return' || P.cullRule === 'attack') {
      // phenotype profiles (with Chris, 2026-11-03): ranked by how often the herder has seen the goat run off,
      // come back on its own, or butt him, per year watched (+1 year, so a newcomer's single act counts less);
      // ties (most goats, most of the time) at random as in the random rule. flight and attack cull the highest
      // rate first, return the lowest.
      const k = P.cullRule === 'flight' ? 0 : P.cullRule === 'return' ? 1 : 2, sign = k === 1 ? -1 : 1, now = this.year * Y + this.day;
      for (const g of m) g._seenRate = sign * g.seen[k] / ((now - g.seenFrom) / Y + 1);
      m.sort((a, b) => a._seenRate - b._seenRate || a._cullKey - b._cullKey);
      return;
    }
    m.sort((a, b) => a._cullKey - b._cullKey);
  }

  // Opportunistic culling (with Chris, 2026-10-20): a herder keeps an animal while keeping it pays and
  // slaughters it once it does not. One-year KEEP VALUE in meat (size) units, from what a herder can see
  // (age, sex, size, kidding record, behaviour; never genes):
  //   + growth  meat still to come this year (toward the herd's mean adult size for its sex)
  //   + kids    a doe in her breeding years: kidValue × her expected kidding over keepHorizon years —
  //             her own record blended with the camp's experience of past does of each age (MODEL C57)
  //   + sire    one of the keepSires oldest bucks: kidValue × his share of the herd's kidding; the
  //             oldest young buck is held back as a replacement at half a sire's value
  //   − feed, − meat at risk of dying unused (per head), − (H6) observed flightiness
  // Ranked by keep value + N(0, cullNoise); the lowest go first.
  cullByOpportunity(m) {
    const P = PARAMETERS, Y = P.yearDays;
    const adult = [0, 0], an = [0, 0];
    let does = 0, bucks = 0;
    for (const g of m) {
      if (g.age >= P.adultAge) { adult[g.sex] += g.size; an[g.sex]++; }
      if (g.sex === SEX_F && g.age >= P.femaleMinAge) does++;
      if (g.sex === SEX_M && g.age >= P.maleMinAge) bucks++;
    }
    const adultSize = [an[0] ? adult[0] / an[0] : 1, an[1] ? adult[1] / an[1] : 1];
    const camp = m.length ? this.camps[m[0].herd] : null;
    const record = camp && camp.record ? camp.record : null;     // camp's experience: kids per doe-year by age
    const herdRate = record && record.yrs > 0 ? record.kids / record.yrs : P.priorKidRate;
    const herdMilk = record && record.yrs > 0 ? record.milk / record.yrs : 0;   // milk per doe-year (kcal)
    // the sires the herder keeps: the oldest; under any other sireRule the ones that rule chose (so they are not eaten;
    // 'milk' from 2026-11-09, the others from 2026-11-10)
    const sires = P.sireRule !== 'oldest' && camp ? this.siresOf(camp.id)
      : m.filter(g => g.sex === SEX_M && g.age >= P.maleMinAge).sort((a, b) => b.age - a.age).slice(0, P.keepSires);
    const heirs = m.filter(g => g.sex === SEX_M && !sires.includes(g) && g.age >= P.weanAge).sort((a, b) => b.age - a.age).slice(0, P.keepHeirs);
    const yearGrowth = P.growthAbs * Y;
    for (const g of m) {
      const ay = g.age / Y;
      let v = P.growthCurve === 'vb' ? g.vbGain(Y) : P.growthCurve === 'ogm' ? g.ogmGain(Y)    // growth: next year's gain
        : Math.max(0, Math.min(adultSize[g.sex] - g.size, yearGrowth));
      if (g.sex === SEX_F && ay < P.senescenceAge) {
        // expected kidding: her own record weighted by its length, blended with the camp's rate for
        // does of her age class (or the herd mean while the camp has little experience)
        const yrs = Math.max(0, (g.age - P.femaleMinAge) / Y);
        const own = yrs > 0 ? g.kids / yrs : 0, wOwn = yrs / (yrs + P.recordWeight);
        const ownMilk = yrs > 0 ? g.milkYield / yrs : 0;
        // summed over keepHorizon years from now (a young doe's worth is mostly to come), each year
        // discounted by the chance she lives to it
        let kv = 0, mv = 0, surv = 1;
        for (let k = 0; k < P.keepHorizon && ay + k < P.senescenceAge; k++) {
          const ac = Math.min(P.ageClasses - 1, Math.floor(ay + k));
          const classRate = record && record.byAge[ac].yrs > 1 ? record.byAge[ac].kids / record.byAge[ac].yrs : herdRate;
          kv += surv * (wOwn * own + (1 - wOwn) * classRate) * (k === 0 && g.age < P.femaleMinAge ? 0.5 : 1);
          if (P.milkValue > 0) {                                  // her milk, the same way (with Chris, 2026-11-09)
            const classMilk = record && record.byAge[ac].yrs > 1 ? record.byAge[ac].milk / record.byAge[ac].yrs : herdMilk;
            mv += surv * (wOwn * ownMilk + (1 - wOwn) * classMilk) * (k === 0 && g.age < P.femaleMinAge ? 0.5 : 1);
          }
          surv *= 1 - P.adultMortality;
        }
        v += P.kidValue * kv;
        if (P.milkValue > 0) v += P.milkValue * mv / P.meatYield;   // milk at its food energy, in meat units
      }
      if (sires.includes(g)) v += P.kidValue * herdRate * does / Math.max(1, sires.length);
      else if (heirs.includes(g)) v += 0.5 * P.kidValue * herdRate * does / Math.max(1, sires.length);
      const sz = P.cullSizeNeutral === 'sex' ? g.sexMult() : P.cullSizeNeutral ? 1 : g.size;
      v -= P.feedCost * Math.pow(sz, 0.75);
      const hz = P.adultMortality + (ay < 1 ? P.juvMortality : 0) + (ay > P.senescenceAge ? P.senescenceRate * (ay - P.senescenceAge) : 0);
      v -= Math.min(1, hz) * sz;
      if (P.flightCost > 0) v -= P.flightCost * g.tr[T_R] * g.fearOfHumans;
      // the last breeding doe and the last breeding buck are worth more to keep (with Chris, 2026-10-27):
      // they can still be eaten in a shortfall, but last
      if (P.lastBreederValue > 0 && ((g.sex === SEX_F && g.age >= P.femaleMinAge && does <= P.lastBreeders) ||
                                     (g.sex === SEX_M && g.age >= P.maleMinAge && bucks <= P.lastBreeders))) v += P.lastBreederValue;
      g._cullKey = -(v + P.cullNoise * normalSample(0, 1));
    }
    m.sort((a, b) => a._cullKey - b._cullKey);
  }

  // Camp experience for the keep value: every herd doe-year by age class, and the kids and milk it produced.
  recordDoeYears() {
    const P = PARAMETERS, Y = P.yearDays;
    for (const c of this.camps) if (!c.record) c.record = { kids: 0, yrs: 0, milk: 0, byAge: Array.from({ length: P.ageClasses }, () => ({ kids: 0, yrs: 0, milk: 0 })) };
    for (const g of this.goats) {
      if (g.dead || g.herd < 0 || g.sex !== SEX_F || g.age < P.femaleMinAge) continue;
      const r = this.camps[g.herd].record, ac = Math.min(P.ageClasses - 1, Math.floor(g.age / Y));
      const kidsThisYear = g.kids - (g._kidsAtYearStart || 0);
      r.kids += kidsThisYear; r.yrs++; r.byAge[ac].kids += kidsThisYear; r.byAge[ac].yrs++;
      g._kidsAtYearStart = g.kids;
      const milkThisYear = g.milkYield - (g._milkAtYearStart || 0);   // and the milk it gave the camp
      r.milk += milkThisYear; r.byAge[ac].milk += milkThisYear; g._milkAtYearStart = g.milkYield;
    }
  }

  // ── vegetation ────────────────────────────────────────────────────────────
  // Human plant food (seeds, tubers, fruit; with Chris 2026-10-25): foodPatches patches of sites, centres
  // drawn in proportion to wetness, clustered (radius foodPatchRadius, fill foodPatchFill), each site's capacity foodSiteK × lognormal
  // (foodSiteSd). Each year every patch draws a yield factor (lognormal, foodMast: good and bad years).
  // Food ripens across the fruiting window (foodPeak ± foodSpan days) and rots outside it.
  makeFoodSites() {
    const P = PARAMETERS, W = this.W, H = this.H, R = P.foodPatchRadius;
    this.foodCap.fill(0); this.food.fill(0); this.foodPatch.fill(-1); this.patchYear.length = 0;
    for (let p = 0; p < P.foodPatches; p++) {
      let c;                                                     // patch centres are denser where it is wet (the valley)
      do c = this.land[randomInt(this.land.length)]; while (rand() >= this.wet[c]);
      const cx = c % W, cy = (c / W) | 0;
      for (let y = Math.max(0, cy - R); y <= Math.min(H - 1, cy + R); y++)
        for (let x = Math.max(0, cx - R); x <= Math.min(W - 1, cx + R); x++) {
          const i = y * W + x;
          if (this.river[i] || this.foodCap[i] > 0 || rand() >= P.foodPatchFill) continue;
          this.foodCap[i] = P.foodSiteK * Math.exp(P.foodSiteSd * normalSample(0, 1) - 0.5 * P.foodSiteSd * P.foodSiteSd);
          this.foodPatch[i] = p;
        }
      this.patchYear.push(1);
    }
  }

  // The dump heap: spoiled slop thrown out at camp carries the seeds of the plant food it came from. Each
  // fu that lands there seeds a new food site with chance heapSeed, on a land cell within heapRadius of
  // camp that is not yet a site (its own patch, so it masts on its own). Near-camp plant patches build up
  // from waste, without anyone choosing to plant ("dump-heap" origin of cultivation).
  dumpHeap(c, fu) {
    const P = PARAMETERS, W = this.W, H = this.H, R = P.heapRadius;
    this.ys.heap += fu;
    let n = Math.floor(fu * P.heapSeed); if (rand() < fu * P.heapSeed - n) n++;
    for (; n > 0; n--) {
      const x = c.x + randomInt(2 * R + 1) - R, y = c.y + randomInt(2 * R + 1) - R;
      if (x < 0 || y < 0 || x >= W || y >= H) continue;
      const i = y * W + x;
      if (this.river[i] || this.campOf[i] >= 0 || this.foodCap[i] > 0) continue;
      if (c.heapPatch === undefined) { c.heapPatch = this.patchYear.length; this.patchYear.push(1); }
      this.foodCap[i] = P.foodSiteK * Math.exp(P.foodSiteSd * normalSample(0, 1) - 0.5 * P.foodSiteSd * P.foodSiteSd);
      this.foodPatch[i] = c.heapPatch; this.ys.sitesSeeded++;
    }
  }

  growFood() {
    const P = PARAMETERS, s = P.foodMast;
    if (this.day === 0) {
      if (P.foodReplace) this.makeFoodSites();                   // this year's sites, from the same distribution (with Chris, 2026-10-25)
      for (let p = 0; p < this.patchYear.length; p++) this.patchYear[p] = Math.exp(s * normalSample(0, 1) - 0.5 * s * s);
    }
    let d = Math.abs(this.day - P.foodPeak); if (d > P.yearDays / 2) d = P.yearDays - d;
    const ripening = d <= P.foodSpan, rate = 1 / (2 * P.foodSpan);
    for (let i = 0; i < this.N; i++) {
      const cap = this.foodCap[i]; if (cap <= 0) continue;
      if (ripening) { const k = cap * this.patchYear[this.foodPatch[i]]; this.food[i] = Math.min(k, this.food[i] + k * rate); }
      else this.food[i] *= 1 - P.foodRot;
    }
  }

  regrow() {
    const P = PARAMETERS, g = this.growth, veg = this.veg, wet = this.wet, river = this.river;
    const r = P.vegRegrowth * g, decay = P.vegDecay * (1 - g), floor = P.vegFloor, root = P.vegRoot;
    const sites = P.economy && this.foodCap ? this.foodCap : null, sg = P.siteGrass;   // land competition
    for (let i = 0; i < this.N; i++) {
      if (river[i]) continue;
      let v = veg[i];
      v += r * wet[i] * (v + root) * (1 - v) - decay * v;     // root reserve: regrowth even when grazed down
      const top = sites && sites[i] > 0 ? sg : 1;             // a food site leaves only siteGrass of the cell to grass
      veg[i] = v < floor ? floor : (v > top ? top : v);
    }
  }

  // What a goat sees as forage on a cell: grass, plus standing plant food when goats eat crops.
  forageAt(i) {
    const P = PARAMETERS;
    return P.economy && P.cropDamage ? this.veg[i] + this.food[i] / P.vegK : this.veg[i];
  }

  // Remove up to `amount` forage units from cell i; returns what was actually eaten.
  graze(i, amount) {
    const P = PARAMETERS;
    const avail = (this.veg[i] - P.vegFloor) * P.vegK;
    const take = amount < avail ? amount : (avail > 0 ? avail : 0);
    this.veg[i] -= take / P.vegK;
    return take;
  }

  meanVeg() {
    let s = 0, n = 0;
    for (let i = 0; i < this.N; i++) if (!this.river[i]) { s += this.veg[i]; n++; }
    return s / n;
  }

  // ── spatial index: goats sorted by cell (counting sort, no allocation) ────
  // full = true at dawn: also today's heats (receptive does) and herd counts.
  buildIndex(full) {
    const N = this.N, W = this.W, H = this.H, goats = this.goats, cnt = this.goatCount, wc = this.wildCount, start = this.cellStart;
    cnt.fill(0); wc.fill(0); this.estrusCount.fill(0);
    if (full) this.herdCount.fill(0);
    for (let k = 0; k < goats.length; k++) {
      const g = goats[k]; if (g.dead) continue;
      const i = g.y * W + g.x; cnt[i]++;
      if (g.herd < 0) wc[i]++;
      if (full) { if (g.herd >= 0) this.herdCount[g.herd]++; g.updateReceptive(this); }
      if (g.receptive) this.estrusCount[i]++;                    // where does in heat are now (rut pull)
    }
    let run = 0;                                                 // running total in a local: no store-then-reload chain
    for (let i = 0; i < N; i++) { start[i] = run; run += cnt[i]; }
    start[N] = run;
    if (this.order.length < goats.length) this.order = new Int32Array(goats.length * 2);
    this._socialStale = true; this._satStale = true;            // both derive from goatCount; rebuilt when next read
    const fill = this._fill || (this._fill = new Int32Array(N)); fill.set(start.subarray(0, N));
    const order = this.order;
    for (let k = 0; k < goats.length; k++) {
      const g = goats[k]; if (g.dead) continue;
      order[fill[g.y * W + g.x]++] = k;
    }
  }

  // Goats within socialRange of each cell (box sum of goatCount): how far company is sensed. The sim itself reads the
  // same box sums cell by cell from the summed-area table (Goat.score); this whole field is for tools and the view,
  // built on the first read after an index rebuild (goatCount changes only there).
  get socialField() { if (this._socialStale) this.buildSocialField(); return this._social; }

  // separable box sum of goatCount over radius socialRange (O(N) via running sums)
  buildSocialField() {
    const W = this.W, H = this.H, cnt = this.goatCount;
    const Rs = PARAMETERS.socialRange, rs = this._rowSum, sf = this._social;
    this._socialStale = false;
    for (let y = 0; y < H; y++) {
      let run = 0; const row = y * W;
      for (let x = 0; x < Math.min(W, Rs); x++) run += cnt[row + x];
      for (let x = 0; x < W; x++) {
        if (x + Rs < W) run += cnt[row + x + Rs];
        if (x - Rs - 1 >= 0) run -= cnt[row + x - Rs - 1];
        rs[row + x] = run;
      }
    }
    for (let x = 0; x < W; x++) {
      let run = 0;
      for (let y = 0; y < Math.min(H, Rs); y++) run += rs[y * W + x];
      for (let y = 0; y < H; y++) {
        if (y + Rs < H) run += rs[(y + Rs) * W + x];
        if (y - Rs - 1 >= 0) run -= rs[(y - Rs - 1) * W + x];
        sf[y * W + x] = run;
      }
    }
  }

  // Summed-area table of goatCount: S[(y)(W+1) + x] = goats in cells [0, x) × [0, y). Integer sums, so a box read
  // from it is exactly the cell-by-cell count.
  buildSat() {
    const W = this.W, H = this.H, W1 = W + 1, cnt = this.goatCount, S = this._sat;
    this._satStale = false;
    for (let y = 0; y < H; y++) {
      const c = y * W, up = y * W1 + 1, here = up + W1;          // row y of goatCount; rows y and y+1 of S, from column 1
      let row = 0;
      for (let x = 0; x < W; x++) { row += cnt[c + x]; S[here + x] = S[up + x] + row; }
    }
  }

  // Wolf scent: marks the cells within wolfFieldR of each HUNGRY wolf (by day, where it rests) or,
  // during a bout (hunting = true), of each wolf hunting goats now; goats read it to avoid and flee.
  buildWolfField(hunting) {
    const P = PARAMETERS, f = this.wolfField, R = P.wolfFieldR, W = this.W, H = this.H;
    f.fill(0);
    for (const w of this.wolves) {
      if (w.fullness >= P.wolfHungry || (hunting && (!w.huntingGoats || w.chased))) continue;
      for (let y = Math.max(0, w.y - R); y <= Math.min(H - 1, w.y + R); y++)
        for (let x = Math.max(0, w.x - R); x <= Math.min(W - 1, w.x + R); x++) { const i = y * W + x; if (f[i] < 255) f[i]++; }
    }
  }

  // ── goats: once-a-day life history ────────────────────────────────────────
  lifeHistory() {
    const P = PARAMETERS, goats = this.goats;
    this._springFeed = P.feedExtend > 0 && this.growth > 0 && this.springDay() < P.feedExtend;   // feedExtend: rationed feeding past the lean season
    if (this._springFeed && !(P.fodderRation && P.provision > 0)) throw new Error('feedExtend needs fodderRation and provision');
    if (P.fodderRation && P.provision > 0 && (this.growth === 0 || this._springFeed) && this.managing()) this.rationFodder();
    for (let k = 0; k < goats.length; k++) {
      const g = goats[k]; if (g.dead) continue;
      g.age++;
      if (!g.daily(this)) { this.kill(g, CAUSE.starvation); continue; }
      if (g.exposed(this)) { this.kill(g, CAUSE.exposure); continue; }
      if (g.dies()) { this.kill(g, g.age > P.senescenceAge * P.yearDays ? CAUSE.age : CAUSE.other); continue; }
      if (g.age === P.weanAge) {                                  // weaned today (counters only)
        const kl = g.kidLife(this); kl.weaned++; kl.wSize += g.size; kl.wFrac += g.size / g.target; kl.wCond += g.E / g.reserveCap();
        if (!g.mother || g.mother.dead) kl.wOrphan++;
      }
      if (g.nursing && (g.nursing.dead || !g.nursing.isKid())) g.nursing = null;    // weaned or lost
      if (g.nursing2 && (g.nursing2.dead || !g.nursing2.isKid())) g.nursing2 = null;
      if (g.nursing3 && (g.nursing3.dead || !g.nursing3.isKid())) g.nursing3 = null;
      g.forgetFear();
      if (g.gestation > 0 && ++g.gestation >= P.gestationDays) this.birth(g);
    }
    for (const w of this.wolves) w.fullness -= P.wolfHunger;
    if (this.day === P.yearDays - 1 && this.managing()) { this.recordDoeYears(); if (P.exchangeN > 0) this.exchangeGoats(); }
  }

  // Realized selection differentials (with Chris, 2026-11-10; no random draws): at the start of each year, the
  // genotype means of each camp's adult herd males and females (age >= breedAge); then for each herd kid born, its
  // maternal allele half minus the camp's female mean (dam) and, unless its sire was wild, its paternal half minus
  // the camp's male mean (sire). Summed per trait in ys.selDam / ys.selSire, kids counted in ys.selN. Diploid only.
  selectionPools() {
    const P = PARAMETERS; this._pools = null;
    if (!this.managing() || P.ploidy === 'haploid') return;
    const sum = this.camps.map(() => [new Float64Array(NT), new Float64Array(NT)]), n = this.camps.map(() => [0, 0]), gv = new Float32Array(NT);
    for (const g of this.goats) {
      if (g.dead || g.herd < 0 || g.age < g.breedAge) continue;
      genotypicValues(g.genome, gv); const s = sum[g.herd][g.sex]; for (let t = 0; t < NT; t++) s[t] += gv[t]; n[g.herd][g.sex]++;
    }
    this._pools = sum.map((sx, c) => sx.map((s, x) => n[c][x] ? s.map(v => v / n[c][x]) : null));
  }

  selectionDiff(kid, genome, camp) {
    const pools = this._pools && this._pools[camp]; if (!pools) return;
    const L = PARAMETERS.loci, K = 2 * L, ys = this.ys;
    for (const [sx, off, acc] of [[SEX_F, 0, ys.selDam], [SEX_M, 1, ys.selSire]]) {
      const pool = pools[sx]; if (!pool || (off === 1 && kid.fatherWild)) continue;
      for (let t = 0; t < NT; t++) { let h = 0; for (let l = 0; l < L; l++) h += genome[t * K + 2 * l + off]; acc[t] += h / L - pool[t]; }
      ys.selN[off]++;
    }
  }

  // Gifts between camps (with Chris, 2026-11-10): at the year's end each camp with a herd gives exchangeN adults, at
  // random, to another camp with a herd, at random. Not its sires (as the cull would keep them), not a goat tethered,
  // guarded or being led, not a doe with a kid at foot. The receiving herder starts watching it afresh (as a captive);
  // its lineage (gsc, wv) goes with it.
  exchangeGoats() {
    const P = PARAMETERS, now = this.year * P.yearDays + this.day;
    const herds = this.camps.map(c => this.goats.filter(g => !g.dead && g.herd === c.id));
    const open = this.camps.filter(c => herds[c.id].length > 0);
    if (open.length < 2) return;
    const moves = [];
    for (const c of open) {
      const m = herds[c.id], sires = P.sireRule !== 'oldest' ? this.siresOf(c.id)
        : m.filter(g => g.sex === SEX_M && g.age >= P.maleMinAge).sort((a, b) => b.age - a.age).slice(0, P.keepSires);
      const can = m.filter(g => g.age >= P.adultAge && !sires.includes(g) && !g.ledBy && !g.isKeptAtCamp() && !g.nursing);
      for (let k = 0; k < P.exchangeN && can.length; k++) {
        const g = can.splice(randomInt(can.length), 1)[0], to = open.filter(o => o !== c);
        moves.push([g, to[randomInt(to.length)]]);
      }
    }
    for (const [g, d] of moves) {
      g.herd = d.id; g.x = d.x; g.y = d.y; g.seen = [0, 0, 0]; g.seenFrom = now; this.ys.exchanged++;
    }
  }

  // A litter: one kid, two when she carried twins, three for triplets (each lighter at birth, twinBirthSize
  // or tripletBirthSize; they share her milk).
  birth(mother) {
    const n = mother.fetus3 ? 3 : mother.fetus2 ? 2 : 1, kid = this.bornKid(mother, mother.fetus, n);
    const kid2 = n > 1 ? this.bornKid(mother, mother.fetus2, n) : null, kid3 = n > 2 ? this.bornKid(mother, mother.fetus3, n) : null;
    mother.gestation = 0; mother.fetus = null; mother.fetus2 = null; mother.fetus3 = null;
    mother.nursing = kid; mother.nursing2 = kid2; mother.nursing3 = kid3;
    mother.kids += n;
    mother.recoverUntil = mother.age + PARAMETERS.loadRecovery * mother.load + PARAMETERS.postpartumDays;
    const ys = this.ys, herd = mother.herd >= 0;
    if (mother.firstKidAge < 0) {
      mother.firstKidAge = mother.age; ys.firstKidAges.push(mother.age);
      (herd ? ys.firstKidAgesHerd : ys.firstKidAgesWild).push(mother.age);
      ys.firstKidCond[herd ? 1 : 0].push([mother.size, mother.E / mother.reserveCap()]);   // her size and condition then
      ys.firstKidStats[herd ? 1 : 0].push([mother.age, mother.tr[T_B], mother.growMult]); // her age, B, growth multiplier
    }
    ys.litters[herd ? 1 : 0][n - 1]++;
  }

  bornKid(mother, genome, n) {
    const kid = new Goat(mother.x, mother.y, genome, rand() < 0.5 ? SEX_F : SEX_M, 0, mother);
    if (n > 1) {
      kid.twin = true; kid.litter = n;
      kid.size *= n > 2 ? PARAMETERS.tripletBirthSize : PARAMETERS.twinBirthSize; kid.E = 0.6 * kid.reserveCap();
    }
    kid.herd = mother.herd;
    kid.fatherId = mother.fetusFather; kid.fatherWild = !!mother.fetusFatherWild;
    if (mother.herd >= 0) {
      this.selectionDiff(kid, genome, mother.herd);
      kid.gsc = mother.gsc + 1;
      kid.pgs = Math.max(0, mother.fetusFatherPgs) + 1;
      // each parent passes half its genome, one generation further from the wild (null = wild, all at depth 0)
      // a wild sire counts as fully wild here even when he descends from escaped herd goats (as before 2026-11-11)
      const wv = kid.wv = new Float32Array(WV_DEPTH), mw = mother.wv, fw = mother.fetusFatherWild ? null : mother.fetusFatherWv;
      for (const pw of [mw, fw]) {
        if (!pw) { wv[1] += 0.5; continue; }
        for (let d = 0; d < WV_DEPTH; d++) wv[Math.min(WV_DEPTH - 1, d + 1)] += 0.5 * pw[d];
      }
      kid.seenFrom = this.year * PARAMETERS.yearDays + this.day;
      this.ys.herdSires[mother.herd].add(kid.fatherId);
      if (kid.fatherWild) this.ys.wildSired++;
      this.ys.herdBirths++;
    } else if (mother.wv || mother.fetusFatherWv) {
      // 2026-11-11, bookkeeping only (nothing in the model reads a wild goat's wv, and capture resets it): a wild-born kid
      // of escaped herd stock keeps its parents' herd generations, one generation no further, since it was born wild; a
      // fully wild parent passes its half at depth 0. So depth counts herd-born generations, and feral lines keep theirs.
      const wv = kid.wv = new Float32Array(WV_DEPTH);
      for (const pw of [mother.wv, mother.fetusFatherWv]) {
        if (!pw) { wv[0] += 0.5; continue; }
        for (let d = 0; d < WV_DEPTH; d++) wv[d] += 0.5 * pw[d];
      }
    }
    this.newborn.push(kid);
    this.ys.births++;
    return kid;
  }

  kill(g, cause) {
    if (g.dead) return;
    g.dead = true; g.cause = cause;
    if (g.ledBy) { g.ledBy.captive = null; g.ledBy = null; }
    const ys = this.ys;
    ys.deaths[cause]++;
    if (g.age >= PARAMETERS.yearDays) ys.adultDeaths++;
    const ay = Math.min(15, Math.floor(g.age / PARAMETERS.yearDays));
    ys.killoff[cause][g.sex][ay]++;
    if (g.herd >= 0) { ys.herdKilloff[g.sex][ay]++; ys.herdDeaths[cause]++; }   // the herd's own mortality: age profile, and by cause
    if (g.herd >= 0)                                                              // herd deaths by [slaughtered, starved, other][sex][half-year of age]
      ys.herdDeathHalf[cause === CAUSE.culled ? 0 : cause === CAUSE.starvation ? 1 : 2][g.sex][Math.min(29, Math.floor(2 * g.age / PARAMETERS.yearDays))]++;
    if (g.herd >= 0 && cause === CAUSE.starvation) {                              // herd starvation by class, season and month (counter only)
      const Y = PARAMETERS.yearDays, t = ys.herdStarve[this.growth === 0 ? 'lean' : 'grow'];
      t[g.isKid() ? 0 : g.age < Y ? 1 : g.age >= g.breedAge ? (g.sex === SEX_F ? (g.gestation > 0 || g.orphan() ? 2 : 3) : 4) : 5]++;
      ys.herdStarveMonth[Math.floor(this.day / 30)]++;
    }
    if (g.isKid()) {                                                              // unweaned deaths, by litter size (and cause)
      ys.kidDeaths[g.herd >= 0 ? 1 : 0][g.litter - 1]++; ys.kidDeathCause[g.herd >= 0 ? 1 : 0][cause][g.litter - 1]++;
      if (!g.mother || g.mother.dead) g.kidLife(this).orphanDeaths++;
    }
  }

  // ── mating (MODEL C30–C34): spatial, on end-of-day positions ─────────────
  // A doe in heat mates among the adult bucks in her 3×3, herd or wild — so gene flow into a herd
  // happens only when wild bucks are near its does. With buck management, if one of her herd's chosen
  // sires is there he mates her without a contest; otherwise the bucks present contest in turn.
  mate() {
    const P = PARAMETERS, W = this.W, H = this.H, goats = this.goats, order = this.order, start = this.cellStart;
    const sires = P.buckManagement ? this.camps.map(c => this.siresOf(c.id)) : null;
    const rivals = this._rivals || (this._rivals = []);
    for (let k = 0; k < goats.length; k++) {
      const f = goats[k];
      if (f.dead || !f.receptive) continue;
      let best = null, nr = 0;
      for (let y = Math.max(0, f.y - 1); y <= Math.min(H - 1, f.y + 1); y++)
        for (let x = Math.max(0, f.x - 1); x <= Math.min(W - 1, f.x + 1); x++) {
          const i = y * W + x;
          for (let o = start[i]; o < start[i + 1]; o++) {
            const m = goats[order[o]];
            if (m.dead || m.sex !== SEX_M || m.age < m.breedAge || m.ledBy) continue;
            if (P.wildSireBlock && f.herd >= 0 && m.herd < 0 && this.year >= P.wildSireBlockFrom) continue;   // R3: no wild buck reaches a herd doe
            if (sires && f.herd >= 0 && sires[f.herd].includes(m)) best = m;
            rivals[nr++] = m;
          }
        }
      if (!best && nr > 0) {
        for (let r = nr - 1; r > 0; r--) { const j = randomInt(r + 1), tmp = rivals[r]; rivals[r] = rivals[j]; rivals[j] = tmp; }
        let holder = null;                                       // if a fight kills both, the next live buck holds
        for (let r = 0; r < nr; r++) if (!rivals[r].dead) holder = holder ? this.fight(holder, rivals[r]) : rivals[r];
        best = holder && !holder.dead ? holder : null;
      }
      if (!best) continue;
      if (rand() >= P.matingConception * f.fertility() * best.fertility()) continue;
      f.fetus = meiosis(f.genome, best.genome);
      f.fetus2 = P.twinMax > 0 && rand() < P.twinMax * f.tr[T_L] ? meiosis(f.genome, best.genome) : null;   // twins (fraternal, one sire)
      // triplets: only twins can become triplets, and only for L above 0.5 (chance rising to tripletMax at L = 1)
      f.fetus3 = f.fetus2 && P.tripletMax > 0 && rand() < P.tripletMax * Math.max(0, 2 * f.tr[T_L] - 1) ? meiosis(f.genome, best.genome) : null;
      f.fetusFather = best.id; f.fetusFatherWild = best.herd < 0;
      f.fetusFatherPgs = best.herd < 0 ? -1 : best.pgs; f.fetusFatherWv = best.wv;   // a wild buck's too (2026-11-11: feral lines)
      f.gestation = 1; f.receptive = false;
      this.ys.conceptions++;
      if (sires && f.herd >= 0) { this.ys.herdConceptions++; if (sires[f.herd].includes(best)) this.ys.chosenSired++; }
      // herd conceptions by origin (with Chris, 2026-11-10): dam captured / camp-born; sire wild / captured / camp-born /
      // another camp's herd (born or captured there)
      if (f.herd >= 0) this.ys.concOrigin[f.gsc >= 1 ? 1 : 0][best.herd < 0 ? 0 : best.herd !== f.herd ? 3 : best.gsc >= 1 ? 2 : 1]++;
    }
  }

  // Sequential-assessment contest (after Enquist & Leimar 1983) between bucks a and b over a doe.
  // Rounds of display, then contact. Each round both pay energy; in contact rounds each risks death in
  // proportion to the opponent's share of fighting ability (× his horns). After every round each buck
  // updates a noisy estimate of his own relative strength and quits when it falls below his threshold
  // (A, R, condition). Returns the winner (the one who stayed), or null if both died.
  fight(a, b) {
    const P = PARAMETERS, fa = a.fightingAbility(), fb = b.fightingAbility(), share = fa / (fa + fb);
    let ea = 0, eb = 0;
    for (let round = 1; round <= P.contestRounds; round++) {
      const contact = round > P.displayRounds;
      const cost = contact ? P.contactCost : P.displayCost;
      a.E -= cost; b.E -= cost;
      if (contact) {
        if (rand() < P.injuryPerContact * (1 - share) * (1 + b.tr[T_H])) this.kill(a, CAUSE.fight);
        if (rand() < P.injuryPerContact * share * (1 + a.tr[T_H])) this.kill(b, CAUSE.fight);
        if (a.dead || b.dead) return a.dead ? (b.dead ? null : b) : a;
      }
      ea += (share + P.assessNoise * normalSample(0, 1) - ea) / round;
      eb += ((1 - share) + P.assessNoise * normalSample(0, 1) - eb) / round;
      const qa = ea < a.quitThreshold(), qb = eb < b.quitThreshold();
      if (qa && qb) return ea < eb ? b : a;
      if (qa) return b;
      if (qb) return a;
    }
    return rand() < share ? a : b;
  }

  // ── wolves (MODEL C47–C50): a bout from dusk through night to the next dawn ──────────────────
  // At the start of a bout (first dusk sub-tick) each hungry wolf decides from its OWN recent success
  // whether to hunt goats (type III: chance s²/(s² + wolfSwitchHalf²) of its memory s of finding goats)
  // or other game (filled with chance altPrey). In every bout sub-tick (dusk, night, dawn) a hungry
  // goat-hunting wolf moves one cell among cells with goats within wolfSense, its scent marks the cells
  // around it, every goat takes its step for the phase (spotting the scent, R × fear of wolves, a goat
  // flees: wild goats away toward cliffs, herd goats to the herder), and then it attacks once among
  // the goats in its 3×3. It stops when fed. Memory is updated at the end of the bout (last dawn sub-tick).
  wolfTick(phase, s) {
    const P = PARAMETERS, W = this.W, H = this.H, goats = this.goats;
    if (phase === 'dusk' && s === 0) {
      for (const w of this.wolves) {
        w.sawGoats = false; w.chased = false;
        const hungry = w.fullness < P.wolfHungry, s2 = w.goatSuccess * w.goatSuccess, h2 = P.wolfSwitchHalf * P.wolfSwitchHalf;
        w.huntingGoats = hungry && rand() < s2 / (s2 + h2);
        if (hungry && !w.huntingGoats && rand() < P.altPrey) w.fullness = 1;
      }
    }
    const hunting = w => w.huntingGoats && !w.chased && w.fullness < P.wolfHungry;
    for (const w of this.wolves) {
      // move: a goat-hunting wolf heads for goats it senses (presence within wolfSense); others roam
      let bx = w.x, by = w.y, bu = -Infinity;
      const hg = hunting(w);
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        const x = w.x + dx, y = w.y + dy;
        if (x < 0 || y < 0 || x >= W || y >= H || this.river[y * W + x]) continue;
        const near = hg ? this.goatsNear(x, y, P.wolfSense) : 0;
        const u = (near > 0 ? this.wolfPull(near) : 0) + rand();
        if (u > bu) { bu = u; bx = x; by = y; }
      }
      w.x = bx; w.y = by;
    }
    this.buildWolfField(true);                                   // hunting wolves, where they are now
    for (const g of goats) { if (!g.dead) g.step(this, phase); }
    this.buildIndex(false);
    for (const w of this.wolves) if (hunting(w)) this.wolfAttack(w, phase);
    if (phase === 'dawn' && s === P.dawnSteps - 1)
      for (const w of this.wolves) if (w.huntingGoats) w.goatSuccess += ((w.sawGoats ? 1 : 0) - w.goatSuccess) * P.wolfMemory;
  }

  nightSub(n) { this.wolfTick('night', n); }

  // Math.pow(near, wolfAttractExp) for a goat count, from a table of the same values (rebuilt if the exponent changes)
  wolfPull(near) {
    const e = PARAMETERS.wolfAttractExp;
    if (this._pullExp !== e) { this._pullExp = e; this._pull = new Float64Array(1024); for (let k = 0; k < 1024; k++) this._pull[k] = Math.pow(k, e); }
    return near < 1024 ? this._pull[near] : Math.pow(near, e);
  }

  // One attack: among the goats in the wolf's 3×3 it detects (camouflage, confusion), each may spot it
  // (R × fear of wolves); the target is drawn by kill chance.
  wolfAttack(w, phase) {
    const P = PARAMETERS, W = this.W, H = this.H, goats = this.goats, order = this.order, start = this.cellStart;
    const cand = this._cand || (this._cand = []), pks = this._pks || (this._pks = []), cells = this._ccell || (this._ccell = []);
    let nc = 0, sum = 0;
    for (let y = Math.max(0, w.y - 1); y <= Math.min(H - 1, w.y + 1); y++)
      for (let x = Math.max(0, w.x - 1); x <= Math.min(W - 1, w.x + 1); x++) {
        const i = y * W + x;
        for (let o = start[i]; o < start[i + 1]; o++) {
          const g = goats[order[o]]; if (g.dead || g.ledBy) continue;
          w.sawGoats = true;
          const pd = P.detectBase * (1 - P.camouflage * g.tr[T_W]) / (1 + P.confusion * (this.goats3x3(i) - 1));
          if (rand() >= pd) continue;
          if (!g.alarmed && rand() < g.tr[T_R] * g.fearOfWolves) g.alarmed = true;     // it spots the wolf
          const pk = this.killChance(g, i);
          cand[nc] = g; pks[nc] = pk; cells[nc] = i; nc++; sum += pk;
        }
      }
    if (nc === 0 || sum <= 0) return;
    let r = rand() * sum, k = 0;
    while (k < nc - 1 && (r -= pks[k]) > 0) k++;
    const prey = cand[k];
    let pk = pks[k], nearHerder = false;
    if (!prey.alarmed && this.warned(prey, cells[k], 'fearOfWolves')) pk = this.killChance(prey, cells[k], true);
    if (prey.herd >= 0) {
      // a herd goat: penned at camp (penProtection) and/or guarded (guardProtection); a guard who
      // drives a wolf off may kill it (it is replaced by an immigrant, fixed guild)
      if ((P.penning || prey.isSheltered() || prey.isKeptAtCamp()) && this.campOf[cells[k]] >= 0) pk *= 1 - P.penProtection;
      const hd = this.herders[prey.herd];
      nearHerder = !!hd && Math.max(Math.abs(hd.x - cells[k] % W), Math.abs(hd.y - ((cells[k] / W) | 0))) <= 1;
      if (nearHerder && P.herderProtection > 0) pk *= 1 - P.herderProtection;
      let guarded = P.guarding && !P.economy;
      if (P.economy) {                                           // a guard within 1 cell of the goat
        const c = this.camps[prey.herd], gx = cells[k] % W, gy = (cells[k] / W) | 0;
        c.sd.guard += P.meatYield * prey.size;
        for (const h of c.guards) if (Math.max(Math.abs(h.x - gx), Math.abs(h.y - gy)) <= 1) { guarded = true; break; }
      }
      if (guarded) {
        pk *= 1 - P.guardProtection;
        if (rand() < P.guardKill) { this.replaceWolf(w); this.ys.wolvesKilled++; return; }
      }
    }
    // attack log (2026-10-31): herd/wild | phase | escape terrain | camp cell | spotted the wolf | loose run-off | kid | herder within 1 cell
    const key = `${prey.herd >= 0 ? 'herd' : 'wild'}|${phase}|${this.escape[cells[k]] ? 1 : 0}|${this.campOf[cells[k]] >= 0 ? 1 : 0}|${prey.alarmed ? 1 : 0}|${prey.loose ? 1 : 0}|${prey.isKid() ? 1 : 0}|${nearHerder ? 1 : 0}`;
    const rec = this.ys.wolfAtk[key] || (this.ys.wolfAtk[key] = [0, 0]); rec[0]++;
    if (rand() < pk) { this.kill(prey, CAUSE.predation); w.fullness = 1; w.kills++; this.witness(cells[k], 'fearOfWolves'); rec[1]++; }
    else { prey.alarmed = true; prey.learnFear('fearOfWolves', 1); }
    if (nearHerder && P.herderChase > 0 && rand() < P.herderChase) this.chaseOff(w, this.herders[prey.herd]);
  }

  // A herder drives a wolf off: its bout ends (chased, until next dusk) and it is pushed herderChaseDist cells straight away from the herder.
  chaseOff(w, h) {
    const P = PARAMETERS, W = this.W, H = this.H;
    let dx = Math.sign(w.x - h.x), dy = Math.sign(w.y - h.y);
    if (dx === 0 && dy === 0) { const a = (rand() * 8) | 0; dx = [1, 1, 0, -1, -1, -1, 0, 1][a]; dy = [0, 1, 1, 1, 0, -1, -1, -1][a]; }
    for (let s = 0; s < P.herderChaseDist; s++) {
      const x = w.x + dx, y = w.y + dy;
      if (x < 0 || y < 0 || x >= W || y >= H || this.river[y * W + x]) break;
      w.x = x; w.y = y;
    }
    w.chased = true; this.ys.wolvesChased++;                     // bout over; memory still updates at dawn
  }

  // Goats in the 3×3 around cell i see a herdmate killed and learn fear of that threat (half an escape).
  witness(i, threat) {
    const goats = this.goats, order = this.order, start = this.cellStart, W = this.W, H = this.H;
    const x0 = i % W, y0 = (i / W) | 0;
    for (let y = Math.max(0, y0 - 1); y <= Math.min(H - 1, y0 + 1); y++)
      for (let x = Math.max(0, x0 - 1); x <= Math.min(W - 1, x0 + 1); x++) {
        const c = y * W + x;
        for (let o = start[c]; o < start[c + 1]; o++) { const n = goats[order[o]]; if (!n.dead) n.learnFear(threat, PARAMETERS.witnessShare); }
      }
  }

  // Does any other goat in the 3×3 around cell i spot the threat and warn g?
  warned(g, i, threat) {
    const P = PARAMETERS, goats = this.goats, order = this.order, start = this.cellStart, W = this.W, H = this.H;
    const x0 = i % W, y0 = (i / W) | 0;
    for (let y = Math.max(0, y0 - 1); y <= Math.min(H - 1, y0 + 1); y++)
      for (let x = Math.max(0, x0 - 1); x <= Math.min(W - 1, x0 + 1); x++) {
        const c = y * W + x;
        for (let o = start[c]; o < start[c + 1]; o++) {
          const n = goats[order[o]];
          if (n !== g && !n.dead && !n.isKid() && rand() < P.groupVigilance * n.tr[T_R] * n[threat]) return true;
        }
      }
    return false;
  }

  replaceWolf(w) {
    const n = this.newWolf(false);
    w.x = n.x; w.y = n.y; w.genome = n.genome; w.fullness = n.fullness; w.kills = 0; w.attemptsLeft = 0;
    w.goatSuccess = n.goatSuccess; w.huntingGoats = false; w.sawGoats = false; w.chased = false;    // an immigrant, with its own memory
  }

  // Chance a wolf attack on goat g in cell i succeeds (warned: a neighbour raised the alarm).
  killChance(g, i, warned) {
    const P = PARAMETERS, t = g.tr;
    let p = P.killBase;
    if (g.isKid()) p *= P.kidVulnerability;
    else {
      const sizeDef = (g.size / g.sexMult() - P.sizeMin) / (P.sizeMax - P.sizeMin);   // within the sex's own range
      let def = P.defSize * sizeDef + P.defAggr * t[T_A];
      if (g.sex === SEX_M) def += P.defHorn * t[T_H];
      p *= 1 - clamp(def, 0, 0.9);
    }
    p *= 1 - P.fleeEscape * (g.alarmed ? 1 : warned ? P.warnShare : 0.5 * Math.min(1, t[T_R] * g.fearOfWolves));
    if (this.escape[i]) p *= 1 - P.escapeRefuge;
    return p;
  }

  // Goats in the box of radius r around (x, y), clipped to the map (from the summed-area table: four reads)
  goatsNear(x, y, r) {
    if (this._satStale) this.buildSat();
    const W1 = this.W + 1, S = this._sat;
    const x0 = Math.max(0, x - r), x1 = Math.min(this.W - 1, x + r) + 1, y0 = Math.max(0, y - r), y1 = Math.min(this.H - 1, y + r) + 1;
    return S[y1 * W1 + x1] - S[y0 * W1 + x1] - S[y1 * W1 + x0] + S[y0 * W1 + x0];
  }

  compact() {
    const goats = this.goats;
    let j = 0;
    for (let k = 0; k < goats.length; k++) if (!goats[k].dead) goats[j++] = goats[k];
    goats.length = j;
    for (const n of this.newborn) goats.push(n);
    this.newborn.length = 0;
  }

  // ── statistics ────────────────────────────────────────────────────────────
  resetYearStats() {
    this.ys = { births: 0, conceptions: 0, deaths: new Array(CAUSE_NAMES.length).fill(0), adultDeaths: 0, firstKidAges: [], hunted: 0,
      firstKidAgesHerd: [], firstKidAgesWild: [], litters: [[0, 0, 0], [0, 0, 0]], kidDeaths: [[0, 0, 0], [0, 0, 0]],   // [wild, herd][single, twin, triplet]
      kidDeathCause: [0, 1].map(() => CAUSE_NAMES.map(() => [0, 0, 0])), firstKidCond: [[], []], firstKidStats: [[], []],
      kidLife: [0, 1].map(() => [0, 1, 2].map(() => ({ days: 0, want: 0, milk: 0, pool: 0, graze: 0, fodder: 0,   // [wild, herd][litter]: kid-days, kcal
        weaned: 0, wSize: 0, wFrac: 0, wCond: 0, wOrphan: 0, orphanDeaths: 0 }))),   // [wild, herd][cause][litter]; [wild, herd] of [size, E/cap]
      captured: 0, exchanged: 0, immigrants: 0, surplusBucks: 0, winterCulled: 0, offtakeDue: 0, offtakeCredited: 0, huntTries: 0, wildNearCamp: 0, campDays: 0,
      cullTally: { offtake: [0, 0, 0, 0, 0], surplus: [0, 0, 0, 0, 0], winter: [0, 0, 0, 0, 0] }, herdComp: [0, 0, 0, 0], herdStarve: { lean: [0, 0, 0, 0, 0, 0], grow: [0, 0, 0, 0, 0, 0] }, herdStarveMonth: new Array(12).fill(0), fodderSpring: 0,
      herdDeathHalf: [0, 1, 2].map(() => [new Array(30).fill(0), new Array(30).fill(0)]),   // [kids, does, bucks, other, captured themselves]
      concOrigin: [[0, 0, 0, 0], [0, 0, 0, 0]],
      selSire: new Float64Array(NT), selDam: new Float64Array(NT), selN: [0, 0], escaped: 0, runOffLost: 0, refetched: 0, ranOff: 0, rejoined: 0, culledValue: 0, foodGathered: 0, slop: 0, heap: 0, sitesSeeded: 0, cropEaten: 0, cropEatenHerd: 0, culledHerd: 0, demand: 0, meatEaten: 0, plantEaten: 0, unmet: 0, offtakeFu: 0, stock: 0,
      dried: 0, driedLost: 0, fodderLost: 0, gatherScored: 0, meatHunted: 0, huntScored: 0, shots: 0, shotKills: 0, altKills: 0, unmetQ: [0, 0, 0, 0], slaughterQ: [0, 0, 0, 0], herdQ: [0, 0, 0, 0], labourQ: [0, 0, 0, 0],
      roleDays: { gather: 0, hunt: 0, herd: 0 }, roleRet: { gather: 0, hunt: 0, herd: 0 }, taskDays: { keep: 0, guard: 0, feed: 0, capture: 0 }, milk: 0, wolvesKilled: 0, wolvesChased: 0, fodder: 0, foraged: 0, capturedR: 0,
      herdBirths: 0, wildSired: 0, herdSires: this.camps.map(() => new Set()), herdConceptions: 0, chosenSired: 0,
      killoff: CAUSE_NAMES.map(() => [new Array(16).fill(0), new Array(16).fill(0)]),
      herdKilloff: [new Array(16).fill(0), new Array(16).fill(0)], herdDeaths: new Array(CAUSE_NAMES.length).fill(0), wolfAtk: {} };
  }

  census() {
    const P = PARAMETERS;
    let kids = 0, f = 0, m = 0, adultsF = 0;
    for (const g of this.goats) {
      if (g.dead) continue;
      if (g.isKid()) kids++;
      if (g.sex === SEX_F) { f++; if (g.age >= P.femaleMinAge) adultsF++; } else m++;
    }
    return { goats: this.goats.length, kids, females: f, males: m, breedingFemales: adultsF };
  }
};
