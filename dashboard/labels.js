'use strict';
// Plain-language labels for the goat genes dashboard: genes, settings, experiments (result folders) and arms.
// Sources: paper/draft.tex Table 1 (what reads each gene), MODEL.md, and each experiment's EXPLOG entry.
// A new experiment folder or arm with no entry here falls back to its folder/arm name and an automatic
// description of how its settings differ from the reference culture.
var LABELS = (function () {
  var GENES = {
    R: { name: 'Reactivity', does: 'How readily a goat is alarmed by a wolf or a person. Low means calm and tame.' },
    A: { name: 'Aggression', does: 'Defence against wolves, and how long a buck keeps fighting a rival.' },
    S: { name: 'Gregariousness', does: 'Pull toward company, and how closely a herd goat follows the herder.' },
    B: { name: 'Body size', does: 'Adult size: fighting ability, and meat.' },
    H: { name: 'Horn size', does: 'Fighting ability, injury in fights, and defence.' },
    T: { name: 'Breeding season length', does: 'How many weeks of the year a doe can come into heat.' },
    M: { name: 'Milk yield', does: 'How much milk a doe can make.' },
    W: { name: 'Coat colour (camouflage)', does: 'Pigmentation: camouflage against wolves and hunters.' },
    L: { name: 'Twinning', does: 'Chance of twins, and above 0.5 of triplets.' },
    C: { name: 'Coat marking (neutral)', does: 'Nothing in the model reads it: a control for drift.' }
  };

  // the reference culture (Run length S0): settings an arm is described against
  var REFERENCE = { humansAt: 300, herdingAt: 400, cullRule: 'opportunity', offtakeRate: 0.1, penning: 1, guarding: 1,
    provision: 2160, kidShelter: 1, buckManagement: 1, tetherNew: 1, milkIntensity: 0.5, exchangeN: 0, sireRule: 'oldest',
    herdMemory: 3, buckCull: '', doeCull: '', captureUntil: 1e9, wildSireBlock: 0, cullFloor: 0, immigrationRate: 0, herdRange: 8,
    surplusCull: 0, fodderRation: 0, winterCull: 0, milkCondition: 0 };

  var never = function (v) { return v == null || v >= 1e8; };
  var noHumans = function (p) { return never(p.humansAt) || p.humansPerCamp === 0; };   // older runs set humansPerCamp 0
  var pct = function (v) { return Math.round(v * 100) + '%'; };
  var CULL = { opportunity: 'least valuable eaten first', random: 'goats eaten at random', flight: 'goats that run off most eaten first',
    return: 'goats that rarely come back on their own eaten first', attack: 'goats that butt the herder eaten first' };
  var SIRE = { oldest: 'the oldest bucks breed', random: 'bucks chosen at random breed', calm: 'the calmest bucks breed',
    gentle: 'bucks that never butt the herder breed', large: 'the largest bucks breed', milk: 'bucks from the best-milking mothers breed',
    deep: 'bucks with the most generations born in the herd breed', shallow: 'bucks with the fewest generations born in the herd breed',
    homebred: 'bucks with the most camp-born mothers breed', marked: 'bucks with the most coat marking breed' };
  var SEXCULL = { random: 'at random', calm: 'run-offs first', large: 'smallest first', homebred: 'captives first', youngMales: 'young males first' };

  // one setting → a short phrase (null = say nothing)
  function phrase(k, v, p) {
    switch (k) {
      case 'humansAt': return noHumans(p) ? 'no humans' : 'humans arrive in year ' + v;
      case 'herdingAt': return noHumans(p) ? null : never(v) ? 'humans hunt but never herd' : 'herding from year ' + v;
      case 'cullRule': return CULL[v] ? 'cull: ' + CULL[v] : 'cull rule ' + v;
      case 'offtakeRate': return pct(v) + ' of the herd eaten a year';
      case 'penning': return v ? 'penned at camp each night' : 'not penned';
      case 'guarding': return v ? 'guarded against wolves' : 'not guarded';
      case 'provision': return v ? 'fodder in the lean season' : 'no fodder';
      case 'kidShelter': return v ? 'young kids kept at camp' : 'no kid shelter';
      case 'buckManagement': return v ? 'herder picks the breeding bucks' : 'bucks fight for mates';
      case 'tetherNew': return v ? 'new captives tethered until tame' : 'new captives not tethered';
      case 'milkIntensity': return v ? 'milked (' + pct(v) + ' of capacity)' : 'not milked';
      case 'exchangeN': return v ? 'camps trade ' + v + ' goats a year' : null;
      case 'sireRule': return p.buckManagement ? SIRE[v] || 'sire rule ' + v : null;
      case 'herdMemory': return p.sireRule === 'homebred' ? 'herder remembers ' + v + ' generation' + (v > 1 ? 's' : '') + ' of mothers' : null;
      case 'buckCull': return v ? 'bucks eaten ' + (SEXCULL[v] || v) : null;
      case 'doeCull': return v ? 'does eaten ' + (SEXCULL[v] || v) : null;
      case 'captureUntil': return never(v) ? null : 'no new wild goats taken after year ' + v;
      case 'wildSireBlock': return v ? 'wild bucks kept away from herd does' + (p.wildSireBlockFrom ? ' from year ' + p.wildSireBlockFrom : '') : null;
      case 'cullFloor': return v ? 'goats eaten only while a camp has more than ' + v : null;
      case 'surplusCull': return v ? 'spare bucks eaten (only the breeding bucks and ' + (p.insuranceBucks != null ? p.insuranceBucks : 2) + ' spares kept)' : null;
      case 'fodderRation': return v ? 'fodder rationed to last the lean season, pregnant and nursing does and young first' : null;
      case 'winterCull': return v ? 'does and young the fodder cannot carry eaten before winter' : null;
      case 'milkCondition': return v ? 'thin does give less milk' : null;
      case 'immigrationRate': return v ? Math.round(v * 100) + '% of adult wild goats swapped for immigrants a year' : null;
      case 'twinMax': return v ? 'twins possible' : 'no twins';
      case 'leanBuffer': return v ? 'goats can live on lean tissue before starving' : 'goats starve when their fat runs out';
      case 'herdRange': return 'pasture up to ' + v + ' km from camp';
      case 'herdTravel': return v > 1 ? 'herd walks to pasture at ' + v + '× pace' : 'herd walks to pasture at normal pace';
      default: return null;
    }
  }
  var ORDER = ['humansAt', 'herdingAt', 'cullRule', 'offtakeRate', 'penning', 'guarding', 'provision', 'kidShelter', 'buckManagement',
    'sireRule', 'herdMemory', 'buckCull', 'doeCull', 'tetherNew', 'milkIntensity', 'exchangeN', 'captureUntil', 'wildSireBlock',
    'cullFloor', 'surplusCull', 'fodderRation', 'winterCull', 'milkCondition', 'immigrationRate', 'herdRange', 'herdTravel', 'leanBuffer', 'twinMax'];
  var HERDING = ['cullRule', 'offtakeRate', 'penning', 'guarding', 'provision', 'kidShelter', 'buckManagement', 'sireRule', 'herdMemory',
    'buckCull', 'doeCull', 'tetherNew', 'milkIntensity', 'exchangeN', 'captureUntil', 'wildSireBlock', 'cullFloor', 'surplusCull', 'fodderRation', 'winterCull', 'milkCondition', 'herdRange', 'herdTravel'];
  /** every setting of an arm, as phrases; herding settings only when there is herding */
  function settings(p) {
    var herding = !noHumans(p) && !never(p.herdingAt);
    return ORDER.filter(function (k) { return p[k] !== undefined && (herding || HERDING.indexOf(k) < 0); })
      .map(function (k) { return phrase(k, p[k], p); }).filter(Boolean);
  }
  /** how an arm's settings differ from the reference culture (settings the arm's code had only) */
  function differences(p) {
    var herding = !noHumans(p) && !never(p.herdingAt);
    if (noHumans(p)) return ['no humans'];
    if (!herding) return ['humans hunt but never herd'];
    return ORDER.filter(function (k) {
      return k in REFERENCE && p[k] !== undefined && JSON.stringify(p[k]) !== JSON.stringify(REFERENCE[k]);
    }).map(function (k) { return phrase(k, p[k], p); }).filter(Boolean);
  }

  var OLDER = 'Run before 2026-11-11 on the older settings unless it set them itself: goats starve when their fat runs out, ' +
    'pasture up to 4 km from camp, normal walking pace. Older code also differs in other ways; the experiment notes say how.';

  // result folder → title and the question it asked (EXPLOG)
  var EXPERIMENTS = {
    iso: { title: 'Isolated herds', about: 'From year 800 no wild goats are captured and no wild buck mates a herd doe, so no wild genes enter the herd; herders eat goats only while a camp has more than 30. On the reference culture (with and without that floor), random bucks, and minimal herding.' },
    imm: { title: 'Immigration into the wild', about: 'The map is a corner of a much larger wild range. Each year from the arrival of humans, a share of the adult wild goats is swapped for immigrants from a hunted wild population: 1, 4 or 10% a year on the reference culture, and 4% into the hunted-only wild as a control.' },
    ladder: { title: 'Anchor ladder', about: 'The two missing rungs of the ladder from wild to herded: humans who hunt but never herd, and minimal herding (every husbandry practice off). The other two rungs, no humans and the full reference culture, are in "Run length".' },
    settle: { title: 'Run length', about: 'How long must runs be before the genes settle? 19 herding cultures and a no-humans control, 4 runs each, 4,000 years. Includes the herd range sweep: the reference culture with pasture up to 4, 6 and 8 km.' },
    depthcheck: { title: 'Lineage check runs', about: 'Two 600-year runs from checking the lineage-depth code (1 run each). So far the only runs with the "Gene values by ancestry" section.' },
    travel: { title: 'Walking pace to pasture', about: 'Does a faster walk to and from pasture let penned herds use pasture 6 and 8 km out?' },
    herdrange: { title: 'Pasture range', about: 'Does reaching pasture further out relieve herd starvation? At normal walking pace, herds at 6 and 8 km were lost.' },
    lean: { title: 'Lean-tissue buffer', about: 'What changes when goats can live on lean tissue for a while before starving?' },
    pilot: { title: 'Run length, first pilot', about: 'Run length and burn-in to year 4,000, including a late start (humans in 1900, herding from 2000).' },
    corners: { title: 'Run length across cultures (stopped)', about: 'Which herding cultures settle latest? Only 10 of 52 runs were made before the settings changed; "Run length" replaced it.' },
    corners_r3: { title: 'Cutting gene flow from the wild', about: 'Stop taking wild goats after year 800, and also keep wild bucks away from herd does.' },
    lineage: { title: 'Lineage test', about: 'Breed from the bucks with the most or the fewest generations born in the herd, with no trait looked at, against bucks chosen at random.' },
    herders: { title: 'Choices a herder could see', about: 'Bucks chosen by camp-born ancestry or coat marking, trade between camps, and the cull at random.' },
    milksel: { title: 'Milk in herder choices', about: 'Counting a doe\'s milk in her value when choosing what to eat, and breeding from bucks of the best-milking mothers.' },
    milk3: { title: 'Milking (third form)', about: 'Milking at 0, 25 and 50% of capacity, with milk paid as made and kid deaths depending on size.' },
    milk2: { title: 'Milking (second form)', about: 'Milking at 0, 25 and 50% of capacity, with milk shared within a litter.' },
    milk: { title: 'Milking (first form)', about: 'Milking at a fixed share of capacity: 0, 25, 50%.' },
    twins: { title: 'Twinning', about: 'Twins and triplets in penned herds, with and without husbandry.' },
    sires2: { title: 'Which bucks breed (second form)', about: 'Oldest, random, calmest, gentlest or largest bucks breed; sires can be eaten like any goat.' },
    sires: { title: 'Which bucks breed (first form)', about: 'Oldest, random, calmest, gentlest or largest bucks breed; chosen sires never eaten.' },
    profiles: { title: 'Which goats are eaten', about: 'Goats eaten at random, least valuable first, or by behaviour the herder sees: running off, coming back, butting.' },
    ablate: { title: 'Husbandry one practice at a time', about: 'Full husbandry less one practice, and penned herds plus one practice: guarding, fodder, kid shelter, buck management, tethering.' },
    nocost: { title: 'No genome cost', about: 'The staged ladder with the genome\'s cost to growth and fertility switched off.' },
    longrun: { title: 'Long runs (2,400 years)', about: 'Does herd size stop predicting the reactivity gap in longer runs?' },
    loadcal: { title: 'Breeding delay from gene load (calibration)', about: 'Calibrating a delay to first breeding that grows with the genome\'s load, without herding.' },
    growcal: { title: 'Growth cost from gene load (calibration)', about: 'Calibrating a growth cost that grows with the genome\'s load, without herding.' },
    growherd: { title: 'Growth cost from gene load in herds', about: 'Does a growth cost from gene load make horns and aggression fall in herds?' },
    staged: { title: 'Husbandry added in stages', about: 'One run adds husbandry in steps: herding with goats eaten at random from 400, least valuable eaten first from 700, penning from 1000, full husbandry from 1300. With no-humans, hunting-only and full-husbandry controls.' }
  };

  // arm names: by arm, then folder/arm where the same name means something else
  var ARMS = {
    S0: 'Reference culture', WT: 'No humans (wild type 1)', WT2: 'Hunting only, no herds (wild type 2)', Hmin: 'Minimal herding (all husbandry off)',
    S0R4: 'Reference culture, pasture 4 km', S0R6: 'Reference culture, pasture 6 km', S0late: 'Reference culture, late start (herding from 2000)',
    Lrandom: 'Bucks chosen at random', Ldeep: 'Bucks from the deepest herd lineages', Lshallow: 'Bucks from the shallowest herd lineages',
    Hped: 'Bucks with the most camp-born mothers', Hbred: 'Camp-born bucks before captured ones', Cmarked: 'Bucks with the most coat marking',
    X: 'Camps trade 2 goats a year', Bold_rc: 'Eaten at random, oldest bucks', Brand_rc: 'Eaten at random, random bucks',
    noGuard: 'No guarding', noMilk: 'No milking', noPen: 'No penning', noBuck: 'Bucks fight for mates', noTether: 'New captives not tethered',
    noShelter: 'No kid shelter', randCull: 'Goats eaten at random', noGuardMilk: 'No guarding, no milking',
    noBuckRandCull: 'Bucks fight, goats eaten at random', bCullRand: 'Bucks eaten at random', dCullLarge: 'Smallest does eaten first',
    R3aRandom: 'Wild bucks kept from herd does', R3bRandom: 'No wild goats taken after year 800', R3cRandom: 'No wild goats after 800, wild bucks kept out',
    HmaxIso: 'Reference culture, isolated from year 800', HmaxIsoNF: 'Reference culture, isolated, no cull floor',
    LrIso: 'Random bucks, isolated from year 800', HminIso: 'Minimal herding, isolated from year 800',
    I01: 'Reference culture, 1% immigrants a year', I04: 'Reference culture, 4% immigrants a year', I10: 'Reference culture, 10% immigrants a year',
    WT2I04: 'Hunting only, 4% immigrants a year (control)',
    T2R4: 'Faster walk, pasture 4 km', T2R6: 'Faster walk, pasture 6 km', T2R8: 'Faster walk, pasture 8 km',
    R6off: 'Pasture 6 km, no lean buffer', R6on: 'Pasture 6 km, lean buffer', R8off: 'Pasture 8 km, no lean buffer', R8on: 'Pasture 8 km, lean buffer',
    S0on: 'Reference culture, lean buffer', Lrandomon: 'Random bucks, lean buffer', R3bon: 'No wild goats after 800, lean buffer', WTon: 'No humans, lean buffer',
    S025: 'Milk counts a quarter in a doe\'s value', S1: 'Milk counts fully in a doe\'s value', S1M: 'Milk in doe value, bucks from best-milking mothers',
    FH4: 'Penned, no husbandry, twins on', M0: 'Full husbandry, not milked', M25: 'Full husbandry, milked 25%', M50: 'Full husbandry, milked 50%',
    TH4: 'Penned, no husbandry, twins on', TH5: 'Full husbandry, twins on',
    Soldest: 'Oldest bucks breed', Srandom: 'Random bucks breed', Scalm: 'Calmest bucks breed', Sgentle: 'Gentlest bucks breed', Slarge: 'Largest bucks breed',
    S2oldest: 'Oldest bucks breed', S2random: 'Random bucks breed', S2calm: 'Calmest bucks breed', S2gentle: 'Gentlest bucks breed', S2large: 'Largest bucks breed',
    Prand: 'Goats eaten at random', Pmeat: 'Least valuable eaten first', Pflight: 'Run-offs eaten first', Preturn: 'Goats that rarely come back eaten first',
    Pattack: 'Goats that butt the herder eaten first',
    AH4: 'Penned, no husbandry (H4)', AH5: 'Full husbandry (H5)', Lguard: 'Full husbandry less guarding', Lprov: 'Full husbandry less fodder',
    Lshelter: 'Full husbandry less kid shelter', Lbuck: 'Full husbandry less buck management', Ltether: 'Full husbandry less tethering',
    Pguard: 'Penned plus guarding', Pprov: 'Penned plus fodder', Pshelter: 'Penned plus kid shelter', Pbuck: 'Penned plus buck management', Ptether: 'Penned plus tethering',
    H0: 'No humans', H1: 'Hunting only', H5: 'Full husbandry from year 400', STAGED: 'Husbandry added in stages',
    H0nc: 'No humans, no genome cost', H1nc: 'Hunting only, no genome cost', H5nc: 'Full husbandry, no genome cost', STAGEDnc: 'Stages, no genome cost',
    H0k0: 'No humans, no breeding delay', H0k15: 'No humans, breeding delay 15 days per unit of load', H0k30: 'No humans, breeding delay 30 days per unit of load', H0k60: 'No humans, breeding delay 60 days per unit of load',
    H1k0: 'Hunting only, no breeding delay', H1k15: 'Hunting only, breeding delay 15 days per unit of load', H1k30: 'Hunting only, breeding delay 30 days per unit of load', H1k60: 'Hunting only, breeding delay 60 days per unit of load',
    H0c01: 'No humans, growth cost 0.1', H0c033: 'No humans, growth cost 0.33', H0c1: 'No humans, growth cost 1',
    H1c01: 'Hunting only, growth cost 0.1', H1c033: 'Hunting only, growth cost 0.33', H1c1: 'Hunting only, growth cost 1',
    H5c033: 'Full husbandry, growth cost 0.33', H5c1: 'Full husbandry, growth cost 1', STAGEDc1: 'Stages, growth cost 1'
  };
  // where the stored settings mislead: runs whose settings changed during the run
  var NOTES = {
    'staged/STAGED': 'Settings change during the run; those shown are the last stage’s, from year 1300.',
    'nocost/STAGEDnc': 'Settings change during the run; those shown are the last stage’s, from year 1300.',
    'growherd/STAGEDc1': 'Settings change during the run; those shown are the last stage’s, from year 1300.'
  };
  var ARMS_IN = {
    'milksel/S0': 'Milk not counted in a doe\'s value', 'herders/WT': 'No humans', 'pilot/WT': 'No humans', 'lean/WTon': 'No humans, lean buffer',
    'longrun/Srandom': 'Eaten at random, random bucks breed', 'depthcheck/S0': 'Reference culture (1 run)', 'depthcheck/noPen': 'No penning (1 run)'
  };

  return {
    GENES: GENES, OLDER: OLDER, settings: settings, differences: differences,
    experiment: function (f) { return EXPERIMENTS[f] || { title: f, about: '' }; },
    arm: function (f, a) { return ARMS_IN[f + '/' + a] || ARMS[a] || a; },
    note: function (f, a) { return NOTES[f + '/' + a] || ''; }
  };
})();
