'use strict';
// Single source of truth for every tunable. Serialized verbatim into every saved data
// packet (see datamanager.js) so any run reconstructs from its stored parameters.
// Declared `var` so it's a global in the browser AND headless. Design: DESIGN.md.
var PARAMETERS = {
  seed: null,             // integer → reproducible run (util.js seedRandom); null → unseeded

  // --- world (DESIGN §3) ---
  width: 80,              // cells; a cell is nominally ~1 km (2 km before 2026-11-11; a label only)
  height: 50,
  riverRows: 2,           // river along the top edge (y < riverRows): water, no vegetation
  wetDepth: 15,           // rows over which the water table falls from river to dry upland
  uplandWetness: 0.35,    // wetness floor away from the river (uplands still get rain)
  ruggedScale: 6,         // value-noise lattice spacing (cells) for ruggedness
  escapeElevation: 0.55,  // escape terrain: elevation above this AND ruggedness above escapeRugged
  escapeRugged: 0.55,
  camps: 3,               // camp sites spaced along the river bank

  // --- clock (DESIGN §3: one tick = one day) ---
  yearDays: 360,
  dawnSteps: 4,           // sub-ticks at dawn: herds walk out to pasture; wolves end their hunting bout
  daySteps: 6,            // movement sub-ticks in a day (grazing, herding, hunting, foraging)
  duskSteps: 4,           // sub-ticks at dusk: herds and captives walk home; wild goats bed down
  nightSteps: 3,          // sub-ticks at night: wolves hunt (a bout runs dusk → night → dawn)

  // --- vegetation (one biomass value per cell, as a fraction of cell capacity K) ---
  vegK: 1440000,          // kcal of forage (ME) per cell at capacity (was 400 fu; calibrated against goat intake in Stage 2)
  vegRegrowth: 0.04,      // max logistic regrowth rate per day (wet cell, peak season)
  vegFloor: 0.03,         // floor: grazing can't take a cell below this
  vegRoot: 0.15,          // root-reserve term in regrowth: (v + vegRoot)(1 − v), so grazed cells recover
  vegDecay: 0.004,        // daily loss of standing biomass outside the growing season
  vegInit: 0.5,
  vegPrewarmYears: 20,    // vegetation-only years run at world build, so tick 1 starts at equilibrium
  growPeakDay: 100,       // day of year of peak growth (~mid April; Zagros spring)
  growFraction: 0.4,      // share of the year with any growth (rest is the lean season)
  leanQuality: 0.4,       // energy per unit of forage eaten in the lean season (dry, dormant forage), relative to growing season

  // --- goats (DESIGN §5; units: kcal (metabolisable energy) and days; until 2026-10-28 forage units, fu:
  //     goat-world 1 fu = 3,600 kcal (maintenance 0.6 fu → 2,160 kcal, NRC-style ~117 kcal/kg^0.75 for 50 kg)) ---
  goatsInit: 800,
  goatIntake: 5760,       // kcal/day max appetite of a size-1 adult (Kleiber-scaled by size^0.75)
  intakeHalf: 0.05,       // type II intake: appetite × a/(a + intakeHalf), a = cell biomass above floor (0 = type I)
  maintBase: 2160,        // kcal/day maintenance of a size-1 adult (size^0.75)
  reserveMax: 216000,     // energy reserve capacity, kcal per unit size (~3 months' fasting)
  reproCostGrowth: 0,     // reproductive cost: growth rate × (1 − this × p), p = mean trait value (later maturity);
                          // off by default since 2026-11-03 (Chris; EXPLOG no-genome-cost entry), 0.5 before
  reproCostFertility: 0,  // reproductive cost: each parent's fertility × (1 − this × p) (per mating); off since 2026-11-03, 0.5 before
  matingConception: 0.7,  // chance a mating on a heat day conceives, before the genome costs
  // gene load (2026-11-03, with Chris): load = SUM of the expressed trait values (0..8), the grain model's form
  // (Domestication/sim/seed.js: germination time = germThreshold + load × growthPenalty), charged as fixed delays
  loadFirstBreed: 0,      // days added to the minimum breeding age (does and bucks) per unit of load
  loadRecovery: 0,        // days after kidding before a doe can conceive again, per unit of load
  postpartumDays: 0,      // days after kidding before a doe can conceive again, whatever her genome (2026-11-05, with
                          // Chris; 0 = none: she can conceive the day she kids, inside her season)
  loadGrowth: 0,          // growth time × (1 + this × (load − loadRef)): each unit of load above loadRef lengthens growth to
                          // adult size by this share (the grain model's germination delay; 0 = the old mean-trait growth cost)
  loadRef: 4.4,           // the load at which growth is unchanged from the old cost (the H0 wild mean, results/loadcal k 0)
  sizeMin: 0.6, sizeMax: 1.4,   // adult size range spanned by B
  birthSize: 0.15,        // newborn size as a fraction of its target
  growthAbs: 0.0035,      // size units gained per day when in surplus (absolute: big targets mature later)
  growthCost: 216000,     // kcal per unit of size gained
  growCondition: 0.4,     // reserve fraction needed to grow
  // sex differences in size and growth (2026-11-14, with Chris; EXPLOG 'Sex differences in size and growth'):
  sexSize: 1.7,           // default 1.7 from 2026-11-18 (Chris); a male's target is sexSize × the target from B (1 = same-size sexes; 1.7 = bezoar weights)
  maleBirthSize: 1.1,     // default 1.1 from 2026-11-18 (Chris); a male newborn's size × this (birth size stays a share of the sex-neutral target; 1.1 = bezoar)
  growthCurve: 'curved',  // default 'curved' from 2026-11-18 (Chris; 'linear' before); 'linear' (growthAbs a day) | 'vb': von Bertalanffy in mass, dM/dt = 3k(T^(1/3) M^(2/3) - M)
                          // | 'ogm': ontogenetic growth model, dM/dt = a M^(3/4) (1 - (M/T)^(1/4)), time to grow ~ T^(1/4)
                          // | 'curved': one daily chunk for every goat, (1 - birthSize) / (growYearsF x yearDays), bent by
                          //   curveExp: ds = chunk k ((T - M) / (T - b))^((k - 1) / k), time to grow ~ T - b (Chris, 2026-11-16)
  growYearsF: 3.75, growYearsM: 4,   // growYearsF default 3.75 from 2026-11-18 (2 before; 'curved' uses it for both sexes); 'vb': years at the full rate from birth (birthSize of target) to 95% of target, per sex
                          // ('ogm': the same for a goat of target 1 x the sex's size multiplier)
  curveExp: 2,            // 'curved': 1 = the straight line; 2 = twice its speed at birth, slowing to 0 at the target
  growSD: 0,              // 'ogm': each goat's rate a x exp(growSD z), z ~ N(0,1) drawn at birth (rand4), not inherited
  adultAge: 720,          // days: counted as adult (growth continues while size < target)
  weanAge: 120,           // days
  kidExposure: 0,         // optional: daily death chance of a kid under 30 days, × (1 − seasonal growth); off (lean forage does this through energy)
  kidMilkNeed: 2160,      // kcal/day a newborn needs from milk (falls linearly to 0 at weaning)
  milkBase: 2160,         // lactation capacity = milkBase × (0.5 + M), kcal/day
  milkCost: 'made',       // what lactation costs the doe: 'made' (what her kids drink + the herders' take; 2026-11-05,
                          // Chris) | 'capacity' (the whole capacity, needed or not; every run before this)
  gestationDays: 150,
  gestationCost: 540,     // kcal/day (one fetus; twins cost 2 × twinBirthSize × this, by litter birth mass)
  twinMax: 0,             // twinning (2026-11-05, with Chris): a doe carries twins with chance twinMax × L (0 = off; L inert)
  twinBirthSize: 0.8,     // a twin's birth size as a share of a single kid's
  tripletMax: 0,          // triplets (2026-11-05, with Chris): a twin pregnancy becomes triplets with chance
                          // tripletMax × max(0, 2L − 1), so only high-L does have them (0 = off)
  tripletBirthSize: 0.7,  // a triplet's birth size as a share of a single kid's (three cost 3 × this in gestation)
  femaleMinAge: 480,      // days; breeding also needs size and condition (plastic)
  breedSizeFrac: 0.65,    // default 0.65 from 2026-11-18 (0.8 before); fraction of target size needed to conceive
  breedCondition: 0.35,   // reserve fraction needed to conceive
  rutPeakDay: 330,        // late November
  rutHalfBase: 15,        // rut half-width at T = 0 (days)
  rutHalfRange: 120,      // extra half-width at T = 1 (T = 1: ±135 days, a nine-month window)
  cycleDays: 21,          // oestrous cycle length (days); does cycle through their breeding season
  oestrusDays: 1,         // days in heat per cycle (the fertile window)
  maleMinAge: 365,
  hornW: 0.5,             // horns' weight in fighting ability: size × (1 + hornW × H)
  contestRounds: 8,       // max rounds in a contest (sequential assessment)
  displayRounds: 2,       // first rounds are display (no injury)
  displayCost: 180,       // kcal per display round, each buck
  contactCost: 540,       // kcal per contact round, each buck
  injuryPerContact: 0.01, // death chance per contact round × opponent's share of ability × (1 + opponent's H)
  assessNoise: 0.25,      // sd of each round's observation of own relative strength
  quitBase: 0.4, quitA: 0.4, quitR: 0.2, quitE: 0.3,   // quit threshold = base − quitA(A−½) + quitR(R−½) + quitE(1 − E/cap)
  adultMortality: 0.03,   // background hazard per year (disease, accident)
  juvMortality: 0.15,     // extra first-year hazard per year
  juvSizeExp: 1.5,        // that hazard × (ref size / size)^this, ref a single grown at full rate to its age (0 = flat,
                          // every run before 2026-11-05); 1.5 provisional, from one-seed smoke against kid-mortality studies
  senescenceAge: 9,       // years
  senescenceRate: 0.25,   // added hazard per year past senescenceAge
  goatMoves: 2,           // foraging moves a wild goat makes per day (spread over the day sub-ticks)
  kidSteps: 2,            // cells per sub-tick a kid can move to keep up with its mother
  fleeSteps: 3,           // cells moved in one sub-tick when alarmed
  alarmLoss: 0.25,        // share of the day's feeding lost when alarmed
  crowding: 0,            // movement penalty per conspecific in a cell (0: competition only through depletion)
  socialW: 1.0,           // attraction to conspecifics × S
  socialRange: 4,         // cells within which company is sensed (box radius)
  herdSat: 15,            // social pull = socialW × S × ln(1 + min(company, herdSat))/ln(1 + herdSat): flat beyond a herd
  fearW: 0.5,             // avoidance of wolf scent × R
  escapePrefW: 0.1,       // preference for escape terrain × R
  mateW: 0.5,             // pull of receptive does on adult males
  moveNoise: 0.05,
  groupVigilance: 0.6,    // chance per neighbour × its R of spotting an attacking wolf and warning the target
  warnShare: 0.5,         // a warned goat gets this share of the full flight benefit (the spotter bolts first)

  // --- wolves (DESIGN §6: fixed population) ---
  wolvesN: 60,            // a predator guild: with type III switching most meals are other game
  wolfHunger: 0.08,       // fullness lost per day (1 = just fed)
  wolfHungry: 0.5,        // hunts below this fullness
  wolfSense: 3,           // radius (cells) a goat-hunting wolf senses goats within
  wolfAttractExp: 0,      // hungry wolves move toward (goats within wolfSense)^exp; 0 = presence (selfish-herd premise)
  wolfAttempts: 2,        // unused since 2026-10-23: a hungry goat-hunting wolf attacks once every bout sub-tick until fed
  altPrey: 0.15,          // nightly chance a hungry wolf hunting other game fills up
  wolfSwitchHalf: 0.3,    // type III on the wolf's own memory s of finding goats: hunts goats with chance s²/(s² + this²)
  wolfMemory: 0.1,        // update rate of that memory per night spent hunting goats
  wolfFieldR: 1,          // radius of a hunting wolf's scent that alarms goats
  detectBase: 0.5,        // chance a wolf sees a goat in its 3×3
  camouflage: 0.5,        // pigmentation W reduces detection by camouflage × W
  confusion: 0.15,        // group confusion: detection ÷ (1 + confusion × (goats in cell − 1))
  killBase: 0.15,
  kidVulnerability: 3.0,
  defSize: 0.3, defAggr: 0.2, defHorn: 0.2,   // adult defence against a kill
  fleeEscape: 0.6,        // reactivity R cuts kill chance (fully if already alarmed)
  escapeRefuge: 0.85,     // kill chance and wolf-scent fear reduced on escape terrain

  // --- humans (DESIGN §7; fixed population; Stage 3: hunting only) ---
  humansAt: 300,          // year humans arrive (after the no-human burn-in to the wild type)
  humansPerCamp: 5,       // 0 = no humans (H0)
  // Immigration (2026-11-11, with Chris): the map is a corner of a much larger wild range. From humansAt, at each year's
  // start, this share of the adult wild goats (not pregnant, no kids at foot, not being led) is swapped in place for
  // immigrants drawn from immigrationPool (genomes and learned fears of hunted wild goats, tools/pool.mjs). 0 = off.
  // Headless only: load.mjs reads the pool.
  immigrationRate: 0,
  immigrationPool: 'tools/pools/wt2.json',
  economy: 0,             // 1: people choose roles by return (notes/human-economy.md); huntEffort, forageEffort, offtakeRate unused
  econHunt: 1,            // economy: hunting is an available role
  econHerd: 1,            // economy: herding is an available role (once herding is allowed and a herd exists)
  needPerPerson: 2250,    // economy: kcal a person eats per day (Hadza adults: women 1,877, men 2,649; Pontzer et al. 2012).
                          // Human-world energy was in fu until 2026-10-28: 1 fu = 900 kcal
  groupSink: 0,           // economy: kcal/day per camp eaten by the wider group beyond the labourers (off until herds are robust; then it drives offtake)
  meatYield: 36000,       // economy: edible kcal per unit of goat size (hunted or slaughtered); was 40 fu
  meatDecay: 0.05,        // economy: daily loss of the meat store's nutrition (gradual; no cliff)
  plantValue: 1,          // economy: kcal of human food per kcal of gathered plant matter (1, with Chris: raise the gathering rate, not this)
  returnTau: 30,          // economy: days over which a role's estimated return decays toward new returns
  roleFloor: 0.1,         // economy: share of choices made at random among available roles (keeps measuring)
  feedCapacity: 40,       // unused since 2026-10-25 (feeders now cut the fodder themselves)
  // human plant food (economy only; seeds, tubers, fruit: goats don't eat it)
  foodPatches: 120,       // patches of food sites on the map (centres drawn by wetness)
  foodPatchRadius: 2,     // cells
  foodPatchFill: 0.5,     // share of a patch's cells that are sites
  foodSiteK: 720000,      // kcal a site yields in an average year (lognormal across sites)
  foodSiteSd: 0.5,        // log-sd of site capacity
  foodMast: 0.6,          // log-sd of a patch's yearly yield factor (good and bad years)
  foodPeak: 150,          // day of year at the middle of the fruiting window
  foodSpan: 45,           // ± days of the fruiting window
  foodRot: 0.03,          // daily loss of unharvested food outside the window
  plantSpoil: 0.003,      // daily loss of the camp's plant-food store (dried, it keeps)
  slopValue: 4,           // kcal of goat fodder per kcal of spoiled plant food (store → slop); 4 keeps the old 1 fu → 1 fu (3,600/900)
  heapSeed: 0,            // chance per kcal of slop thrown on the dump heap that it seeds a new food site (off: backed out 2026-10-25)
  heapRadius: 2,          // cells from camp the dump heap seeds sites within
  siteGrass: 1,           // land competition: share of a food-site cell's vegetation capacity left to grass (1 = off)
  cropDamage: 0,          // 1: goats (herd and wild) on a food site eat the standing plant food first, and seek it out
  foodReplace: 1,         // food sites are redrawn each year from the same distribution (none persist)
  huntEffort: 0.3,        // share of days each human goes hunting (a fixed policy, not a demand)
  forageEffort: 0.3,      // share of days a non-herder forages (cuts fodder for the camp store)
  forageRange: 6,         // cells from camp a forager will consider (a day's walk; it trades distance against lushness)
  forageCut: 14400,       // kcal of fodder cut per sub-tick at the forage cell (removed from its vegetation); was 4 fu
  forageLoad: 36000,      // kcal of fodder a forager can carry home (~60 kg fresh browse, two headloads; 72,000 until 2026-10-31)
  foodCut: 3600,          // economy: kcal of plant food a gatherer harvests per sub-tick at a food site (was forageCut, 4 fu)
  foodLoad: 18000,        // economy: kcal of plant food a gatherer can carry home (was forageLoad, 20 fu)
  fodderSpoil: 0.005,     // daily loss of the camp fodder store
  // shelf-life stores (with Chris, 2026-10-28): every store keeps for a window instead of decaying at a rate
  storeWindows: 1,        // 1: dated batches, eaten soonest to expire first; the rates above (meatDecay, plantSpoil, fodderSpoil) unused
                          // (default 1 from 2026-10-31; with economy 0 it touches only the fodder store)
  freshDays: 3,           // windows: days fresh meat keeps; then it is dried
  dryValue: 0.7,          // windows: share of fresh meat's food that drying keeps
  dryDays: 270,           // windows: days dried meat keeps; then lost
  plantDays: 135,         // windows: days stored plant food keeps; then slop
  slopDays: 14,           // windows: days slop keeps; then the dump heap
  fodderDays: 270,        // windows: days cut fodder (hay) keeps; then lost
  storeCredit: 0.0011,    // windows: herding's storage credit, × stock per day (dried meat: 30% lost over 270 d); was meatDecay
  needScore: 0,           // windows: 1 = gathering and hunting returns count a delivery for the food it adds to what the camp will eat
  gatherSee: 0,           // economy: 1 = gathering's return is predicted each morning from the ripe food in range (shared among
                          // yesterday's gatherers, up to foodLoad each; valued by needScore if on), not remembered
  huntRange: 8,           // max cells a hunter walks out in a day
  huntAttempts: 2,        // tries per hunting day (at most one kill)
  humanDetect: 0.6,       // chance a hunter sees a goat in its 3×3 (camouflage counts half)
  huntBase: 0.5,          // success chance against an unwarned, non-reactive goat
  stalkDetect: 0.6,       // chance × R × fearOfHumans a goat spots the stalking hunter and bolts first
  huntFlee: 0.8,          // flight cuts success: fully if alarmed, warnShare if warned, 0.5 × R × fearOfHumans otherwise
  humanRefuge: 0.5,       // success reduced on cliffs
  humanFieldR: 1,         // radius around a hunter that alarms goats
  shotChance: 0,          // chance a ranged shot at a visible wild goat within shotRange hits (0 = no shots); taken
                          // before the goat can spot the stalk; less on cliffs (humanRefuge) and at alarmed goats (huntFlee); a miss alarms the goats in range.
                          // Fixed policy: an attempt that is not a capture try is a shot when a goat is in sight, else a stalk
  shotRange: 2,           // cells (box radius) a hunter can shoot across
  altGame: 0,             // economy hunters: chance a hunting day that took no goat brings home other game (gazelle, deer, boar;
                          // not modelled as animals, never depleted, as the wolves' altPrey); 0 = goats are the only game
  altYield: 36000,        // kcal of edible meat in an other-game carcass (36,000 = one adult goat's)

  // --- herd management (DESIGN §2 conditions, §7; Stage 4) ---
  herdingAt: 1e9,         // year camps start keeping herds (1e9 = never: H0/H1); e.g. 400 for H2+
  schedule: '',           // behaviour changes partway through a run: 'year:key=value,key=value;year:...', each set
                          // applied at the start of that year (2026-11-02: the staged ladder, H2 then H3, H4, H5 in turn)
  herdTarget: 1e9,        // optional hard cap per camp (none by default: herd size emerges from labour, forage, offtake)
  cullFloor: 0,           // offtake only above this many goats per camp (2026-11-11, with Chris: keeps an isolated herd alive;
                          // 0 = off). Losses other than offtake still take a herd below it
  surplusCull: 0,         // 1 (2026-11-12, with Chris): each night the herder slaughters every weaned herd male beyond the camp's
                          // sires (siresOf) and insuranceBucks spares (the oldest other weaned males); these culls count
                          // against the year's offtake draws (that year's offtake = the larger of the two), and cullFloor
                          // does not stop them
  insuranceBucks: 2,      // surplusCull: weaned males kept besides the sires, as insurance against losing a sire
  winterCull: 0,          // 1 (2026-11-12, with Chris): on the first lean day the herder slaughters breeding-age does and
                          // goats under a year, lowest keep value first, until the fodder store covers a full ration
                          // (provision) through the lean season for those of them kept (bucks and dry yearlings graze);
                          // never below cullFloor; counts against the year's offtake like surplusCull
  winterBudget: 1,        // winterCull (2026-11-13, with Chris): the share of a full ration the herder budgets per fed goat through
                          // the lean days; 1 = a full ration (the pilot), lower keeps more goats on the same fodder
  feedExtend: 0,          // spring feeding (2026-11-13, with Chris: feed until normal grazing starts): fodderRation goes on this many
                          // days past the lean season (0 = off), the store rationed to last the window; feedNeed sets each goat's want
  feedNeed: 'deficit',    // feedExtend: 'deficit' = today's upkeep (maintenance, gestation, lactation) not met by today's grazing and
                          // milk, so feeding tapers as pasture recovers; 'full' = as in the lean season (up to provision, to a full reserve)
  leanPulse: 0,           // offtake timing (2026-11-13, with Chris): the share of the year's offtake drawn in the first leanPulseDays
                          // of the lean season (the herder eats the goats he would otherwise have to carry through it); the
                          // rest spread over the other days, so the yearly rate is unchanged; 0 = off (offtake even all year)
  leanPulseDays: 30,      // leanPulse: length of the early-lean window, days
  winterCullAll: 0,       // winterCull (2026-11-14, with Chris: cull grown males and old does before they lose condition): 1 = budget
                          // every herd goat, bucks included, and cull among all of them by keep value; 0 = breeding does and young only
  herdPerHerder: 20,      // goats one herder watches before spooking rises: spook × max(minLoad, herd / herdPerHerder)
  minLoad: 0.25,
  offtakeRate: 0.1,       // share of the herd slaughtered for meat per year (chosen by cullRule); an experimental variable
  captureRate: 0.2,       // chance per hunting attempt that a hunter tries to take a goat alive instead (from herdingAt)
  captureFear: 0.35,      // tethering: a herd goat with R × fearOfHumans at or above this stays tethered
  captureSteps: 3,        // approach steps to seize a goat alive (each: bolt with stalkDetect × R × fearOfHumans)
  searchRange: 6,         // cells a herder will go back for a stray; beyond it the stray is lost
  captureOrphans: 1,      // a doe's nursing kid is taken alive when she is hunted
  captureUntil: 1e9,      // R3 (gene flow by sex): year from which camps take no more goats alive (captures and orphans)
  wildSireBlock: 0,       // R3: 1 = a herd doe never mates a wild buck (gene flow from the wild only through captives)
  wildSireBlockFrom: 0,   // the year wildSireBlock starts (2026-11-11: isolated herds block wild sires from captureUntil)
  herdRange: 8,           // cells from camp a herder goes to find pasture (4 before 2026-11-11; a key sweep variable: herd
                          // size follows it, about 102 / 145 / 224 at 4 / 6 / 8 with herdTravel 2, EXPLOG 2026-11-11)
  herdTravel: 2,          // cells per sub-tick a herd and its herder cover walking out at dawn and home at dusk (1: every
                          // run before 2026-11-11; 2 the default from then); a penned herd can use pasture up to about duskSteps × herdTravel away
  herdPull: 1.0,          // pull toward the herder, × (0.5 + S)
  herderAlarm: 0.05,      // daily chance × R × fearOfHumans × herder load that the herder spooks a herd goat (spread over the day sub-ticks)
  refetchRunOffs: 2,      // run-offs (a goat spooked beyond keepRadius): 0 drifts back on its own; 1 gone after at once (approach
                          // test); 2 loose: moves as a wild goat, rejoins if it comes back near, keepers chase one a sub-tick
  chaseDelay: 2,          // run-offs (mode 2): sub-ticks loose before a keeper goes after it
  spookAtDusk: 0,         // 1: the herder can also spook goats on the walk home at dusk (same daily chance, spread over day + dusk sub-ticks)
  keepRadius: 2,          // a herd goat further than this from its herder at day's end has strayed
  penning: 1,             // the herd walks home at dusk and is penned at camp overnight
  penProtection: 0.8,     // penned at camp: a wolf's kill chance on a herd goat is cut by this
  herderProtection: 0,    // a wolf's kill chance on a herd goat within 1 cell of its herder is cut by this: the herder's
                          // presence, the herder's dogs included (with Chris, 2026-10-31; Soofi et al. 2022, NE Iran: shepherd
                          // present ~-43% wolf predation in night corrals, ~-60% by day; each dog a further -25%)
  herderChase: 1,         // chance the herder drives off a wolf that strikes at a herd goat within 1 cell of them (kill or
                          // miss): its bout ends and it is pushed herderChaseDist cells away from the herder (with Chris,
                          // 2026-11-01: herd goats bunch to the herder instead of fleeing, so the herder's answer is the defence;
                          // default on from 2026-11-01, part of every herding condition)
  herderChaseDist: 5,     // cells
  guarding: 0,            // H5: a deliberate watch over the herd (the herder's own presence and dogs are herderChase)
  guardProtection: 0.7,   // guarded: kill chance on a herd goat cut by this (on top of the pen)
  guardKill: 0.2,         // chance a guard kills an attacking wolf (replaced by an immigrant)
  provision: 0,           // H5: fodder (kcal/day, × size^0.75; 0.6 fu = 2,160 kcal) given to herd goats in the lean season
  fodderRation: 0,        // 1 (2026-11-12, with Chris): in the lean season each camp feeds at most its fodder store / the lean days
                          // left a day, so the store lasts the season; pregnant and nursing does and goats under a year
                          // first, then the rest, each class shared in proportion to what its goats want (0: each goat
                          // takes its full want in turn until the store is empty)
  leanBuffer: 12000,      // kcal per unit size the reserve may fall below empty (lean tissue burned) before the goat dies;
                          // 0 = dies the day its reserve goes negative (every run before 2026-11-10; the default until
                          // 2026-11-11). 12000 (the default from 2026-11-11): death at about
                          // 70% of lean body weight for a 50 kg goat (Turner et al. 1993), refilled before fat when fed
  provisionShelter: 0.5,  // with provisioning, herd kids' exposure risk is cut by this
  kidShelter: 0,          // husbandry: herd kids under shelterAge stay in the camp pen (no exposure, pen protection)
  shelterAge: 30,         // days
  shelterExposure: 0.8,   // exposure risk cut by this while sheltered
  buckManagement: 0,      // husbandry: herd males don't fight; the keepSires herd males chosen by sireRule sire
  tetherNew: 0,           // husbandry: captives too fearful to approach stay tethered at camp on fodder until tame
  ibdFrom: 400,           // year allele lineages are relabelled: IBD (inbreeding) is measured from here in every condition
  cullRule: 'random',     // 'random' (H2) | 'opportunity' (keep value; H3+) | 'flight' | 'return' | 'attack' (phenotype
                          // profiles: what the herder has seen the goat do) | 'youngMales' | 'temperament' (legacy sorted rules)
  buttRate: 0.002,        // attack profile: daily chance × A that a herd goat butts the herder (seen only; drawn only under
                          // cullRule 'attack' or sireRule 'gentle')
  sireRule: 'oldest',     // which keepSires adult herd bucks the herder breeds from: 'oldest' | phenotype profiles 'random'
                          // (control) | 'calm' (fewest seen run-offs) | 'gentle' (fewest seen butts) | 'large' (biggest)
                          // | 'milk' (sons of the dams with the best milk record) | 'deep' / 'shallow' (most / fewest
                          // generations since the wild, no trait) | 'homebred' (camp-born dams on the maternal line, up to
                          // herdMemory) | 'marked' (most coat marking, neutral C); the opportunity cull keeps the bucks any rule but 'oldest' chose
  keepChosenSires: 0,     // random cull: the chosen sires are never culled (1); results/sires and results/longrun only
  herdMemory: 3,          // sireRule 'homebred': generations of camp-born dams a herder remembers (1: camp-born vs captured)
  buckCull: '',           // the bucks' own cull rule within the herd's cull order: '' (the overall cullRule decides) |
                          // 'random' | 'calm' | 'large' | 'homebred' | 'youngMales' (World.cullBySex); sires never taken
  doeCull: '',            // the does' own cull rule: '' | 'random' | 'calm' | 'large' | 'homebred'
  exchangeN: 0,           // adults each camp gives another camp a year (exchangeGoats; 0 = no exchange)
  keepLastSires: 0,       // random cull: adult herd bucks are not culled while the herd has keepSires or fewer (1);
                          // sires otherwise eaten as any goat (Chris, 2026-11-04)
  kidValue: 0.3,          // opportunity: a weaned kid's worth in meat (size) units
  milkValue: 0,           // opportunity: a doe's expected milk to the camp (her record, as for kids) at this × its food
                          // energy, in meat units (1 = a kcal of milk worth a kcal of meat; with Chris 2026-11-09)
  priorKidRate: 0.8,      // opportunity: kidding rate assumed before the camp has any record
  keepHorizon: 3,         // opportunity (≈ age at first kidding): years ahead a herder counts a doe's expected kidding (survival-discounted)
  recordWeight: 1,        // opportunity: years of a doe's own record at which it weighs equal to the camp's
  ageClasses: 10,         // opportunity: camp record of kids per doe-year by age class (years)
  feedCost: 0.085,        // opportunity: a year's keep, × size^0.75, in meat units. 0.085 from 2026-11-18 (batch 1; 0.15 before): exp003
                          // puts males dead before 2.5 y in the Ganj Dareh band at 0.075-0.10 (Chris: sweep that range, report it)
  cullSizeNeutral: 'age', // default 'age' from 2026-11-18 batch 1 ('sex' earlier that day, 1 before); opportunity: feed and meat-at-risk charged per head, so the cull rule cannot itself select on size (0 = by size;
                          // 'sex' = per head at the sex's size multiplier, sexSize for males: neutral within a sex, a buck eats more;
                          // 'age' = at the herd's mean size for the goat's sex and age in years, 0..5+: neutral within sex and age, 2026-11-18)
  growthCredit: 'herd',   // opportunity: next year's growth in the keep value, toward 'own' (the goat's own target), 'herd' (the
                          // herd's mean adult size for its sex: the herder's learned expectation; default from 2026-11-18, Chris)
                          // or 'cull' (running mean size of the goats of that sex the camp has slaughtered, over the last ~cullMemory;
                          // the herd's adult mean until the first cull) or 'max' (the herd's largest goat of that sex now; 2026-11-18),
                          // on the goat's growth rule; 'model' = linear 'herd',
                          // vb/ogm/curved 'own' (as before 2026-11-17); 'herd' and 'cull' need linear or curved (Chris, 2026-11-17/18)
  keepFrame: 'year',      // opportunity (2026-11-18, Chris): 'year' = growth, feed, meat at risk and the sire's share over the next year
                          // (kids over keepHorizon); 'horizon' = every term over keepHorizon years, each discounted by survival
  keepTerms: 0,           // diagnostic: 1 stores each herd goat's keep-value terms on it at every cull (g._kvTerms; tools/keepvalue.mjs)
  creditAge: 0,           // growthCredit 'herd': days from which the herder counts a goat in the adult mean (0 = adultAge; 2026-11-18)
  cullMemory: 20,         // growthCredit 'cull': culls of a sex in the herder's running mean (exponential, weight 1/cullMemory per cull)
  cullNoise: 0.05,       // opportunity: sd of the herder's judgement noise on keep value (0 = pure ranking)
  flightCost: 0,          // opportunity: cost of observed flightiness (R × fear of humans); H6 > 0
  rutGuard: 0,            // husbandry: chance a receptive herd doe is kept at camp each rut day; cuts wild-buck sirings by this
  keepSires: 2,           // bucks kept as sires per camp (oldest first)
  keepHeirs: 1,           // opportunity: young bucks held back as replacement sires (succession)
  lastBreederValue: 0,    // keep-value boost (meat units) for the herd's last breeding doe and last breeding buck (0 = off)
  lastBreeders: 1,        // how many does/bucks count as "the last" for the boost
  econCull: 1,            // default 1 from 2026-11-18 (batch 1, Chris; 0 before = the offtakeRate quota; only under cullRule
                          // 'opportunity': other rules and surplusCull/winterCull runs need econCull=0). 1 = opportunity cull, every cullEvery days, of goats whose keep value < cullThreshold; with economy 0 it
                          // replaces the offtakeRate quota (2026-11-18, Chris), with economy 1 it runs beside the camp's demand
  cullEvery: 30,          // days between opportunity culls
  cullThreshold: 0,       // keep value (meat units) below which keeping a goat no longer pays
  cullOldAge: 7,          // youngMales: females older than this (years) are culled before breeding females
  milkIntensity: 0,       // share of a herded doe's milk capacity taken daily (0 = no milking)
  milkCondition: 0,       // 2026-11-12, with Chris: a doe's milk capacity falls with her condition, full at a reserve of this
                          // share of its cap or more, in proportion below (yield tracks body condition: Flores-Najera et al.
                          // 2021, Biology 10:220); kids and herders both get less. 0 = capacity from M alone
  milkKeep: 0.5,          // share of the camp milk pool kept to the next day (feeds herd orphans)
  windowMax: 180,         // socialisation window = windowMax × (1 − R) days
  habKid: 0.1,            // daily habituation inside the window (toward fearMin)
  habAdult: 0.02,         // daily habituation after it (wild-caught adults settle over weeks)
  fearMin: 0.05,

  // --- learned fear (plastic, threat-specific; DESIGN §4.3) ---
  sensitize: 0.3,         // fear gained per survived attack, × R (reactive goats learn faster)
  witnessShare: 0.5,      // seeing a herdmate killed nearby counts as this share of an attack
  fearMax: 3,             // cap on learned fear (× R)
  fearLearnR: 1,          // 1: fear learned per event scales with R (reactive goats learn faster); 0: the same for all, at fearLearnRef
  fearLearnRef: 0.6,      // the R used for every goat's learning when fearLearnR is 0
  alarmLearn: 0,          // share of an attack's sensitisation that each alarm, spotted stalk or herder spook adds (0 = off)
  forgetRate: 0.002,      // daily relaxation of learned fear toward 1 (half-life ~1 year)
  motherLearn: 0.1,       // a following kid's fears move this far toward its alarmed mother's

  // --- genome (DESIGN §4; swept: haploid, diploid L = 2 (default), 4, 6) ---
  ploidy: 'diploid',      // 'diploid' | 'haploid'
  loci: 2,                // loci per trait (diploid)
  mutationStep: 0.04,     // uniform ±step on every allele at meiosis (grain model's value); copies never mutate
  pleioW: 0,              // β: weight of R's genotype in expressed pigmentation W (neural-crest switch)
  pleioA: 0,              // weight of R's genotype in expressed aggression A (shared HPA axis switch)

  // --- engine ---
  updatesPerDraw: 3,      // fast-forward: sim days per rendered frame

  // --- data collection ---
  reportingPeriod: 30,    // sample scalars (the census, samples[]) every N days; each row carries its tick, year and day
  histPeriod: 1,          // record the gene histograms (hist, histHerd) every N years, at the end of years N-1, 2N-1, ...;
                          // histYears lists the year of each row; histDepth pools max(10, N) years per record (2026-11-13)
  recordEvery: 1,         // keep the year row (years[]) every N years, at the end of years N-1, 2N-1, ...; each row carries
                          // its year and is that one year's record (totals are per year, not summed over N). Output only:
                          // the run is the same. Experiment runs scale it with run length (runyears, 2026-11-19)
  epoch: 360 * 200,       // a run ends (and ships a packet) at N ticks
  // diagnostics, each a named switch (conventions §4 "Keep packets small", 2026-11-13): 1 records it, 0 leaves it out
  // of the saved run. All on by default so runs stay comparable with saved ones; a sweep turns off what it no longer
  // uses, in its pre-registration. Share of the plain JSON of a 4000-y husbandry run (husb/HmaxH_seed1, 32 MB):
  logWolfAtk: 1,          // years[].wolfAtk: wolf attacks and kills by herd/wild, phase, escape, camp, spotted, ... (14%)
  logKidLife: 1,          // years[].kidLife: unweaned kids' kid-days, kcal by source, weaning, orphan deaths (13%)
  logKilloff: 1,          // years[].killoff: deaths by cause, sex and age (8%)
  logHerdKilloff: 1,      // years[].herdKilloff: herd deaths by sex and age (1%)
  logKidDeathCause: 1,    // years[].kidDeathCause: unweaned deaths by cause and litter size (2%)
  logHistDepth: 1,        // histDepth: gene histograms by lineage depth, every 10 years (7%)

  // --- database (the standard vendored client, src/db.js) ---
  db: {
    transport: 'socket',
    server: 'https://research.climbinggiants.com:8888',
    mongoUrl: 'mongodb://127.0.0.1:27017',
    db: 'animalDomestication',
    run: 'run',
  },
};

// Schema drives the auto-generated control panel (ui.js). One entry per live-tunable.
var PARAM_SCHEMA = [
  { key: 'updatesPerDraw', label: 'Speed (days/frame)', min: 1, max: 60, step: 1 },
  { key: 'vegRegrowth', label: 'Regrowth rate', min: 0.005, max: 0.15, step: 0.005 },
  { key: 'vegDecay', label: 'Lean-season decay', min: 0, max: 0.02, step: 0.001 },
  { key: 'growFraction', label: 'Growing-season share', min: 0.2, max: 1, step: 0.05 },
];
