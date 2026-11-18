# Animal Domestication — Model Description (as built, v2)

*The model as it stands in the code after the 2026-10-21 rebuild (commit 7b7e356 and the comment fix
after it), written from the source. Structured after ODD (Grimm et al. 2020). DESIGN.md is the intent;
this file is what the code does. Every modelling choice has an ID (C1, C2, …) for flagging, with its
rule, default values and code location. Parameter names are those in `src/params.js`. The first version
(choices C1–C66, bugs B1–B8) is in git at ae4f03d; §12 lists what changed.*

---

## 1. Purpose and patterns

**Purpose.** To test which human behaviours toward a wild herd animal (hunting, keeping, culling,
penning, husbandry, isolating the herd) are sufficient to produce the animal domestication syndrome,
and whether the syndrome needs a shared developmental cause (pleiotropy) or can come from the
selective regime acting on independent genes.

**Patterns** (DESIGN §0): (1) herded and wild goats coexist as distinct populations despite gene flow;
(2) order of change: demography, then inbreeding, then behaviour, with body size and horns last;
(3) conditionality. Calibration targets: Ganj Dareh kill-off (of males, 60–70% dead before 2.5 y; of
does, 60–70% surviving past 2.5 y; ~20% of goats past 4 y); wild first kidding at 2–3 y.

---

## 2. Entities, state variables and scales

**Cell** (80 × 50 grid, typed arrays): river flag, wetness, elevation, ruggedness, escape terrain,
vegetation (fraction of capacity K = 400 fu), camp id. Scratch fields: goat count, wild-goat count,
goats within radius 4 (`socialField`) and does in heat, rebuilt every sub-tick and after the herd
night; hungry-wolf scent, built at dawn from where wolves lie up; hunter presence, rebuilt each day
sub-tick and cleared at dusk.

**Goat**: position; genome (allele values + lineage ids); 8 expressed traits; genome penalty p (mean
trait value); sex; age; target and current size; energy reserve E; mother; alarm flag (C35); learned fear of wolves and of humans; herd (camp id or −1); led-by (a hunter leading
it); kept-at-camp-today flag; generations since capture; father; gestation and fetus; nursing kid;
in-heat flag; oestrous phase; milk taken today; kid count; age at first kid.

**Wolf**: position, fullness, memory of finding goats, tonight's choice (goats or other game), attacks
left, kills. **Human**: camp, position, today's role (herd, hunt, forage, camp, return), target, cells
walked, attempts left, captive, forage load. **Camp** (3): position, milk pool, fodder store, record
of kids per doe-year by age class.

**Scales.** **C1** One engine tick = one day; year = 360 days. **C2** Each day has sub-ticks: 4 dawn,
6 day, 4 dusk, 3 night (`dawnSteps`, `daySteps`, `duskSteps`, `nightSteps`). **C3** A cell is nominally ~1 km (with Chris, 2026-11-11; it was ~2 km. Nothing in the code uses the
scale: it only names what the cell-counted ranges and densities mean, e.g. herdRange 4-8 = 4-8 km). Runs: no
humans for 300 years, humans from year 300, herding from year 400; condition batch runs 800 years.

---

## 3. Schedule (one day, `World.update`)

1. Clock and season; vegetation regrows. Humans arrive at `humansAt`; allele lineages relabelled at
   min(herdingAt, ibdFrom).
2. **Dawn** (`dawn`): index rebuilt with today's heats and herd counts; every human except one still
   leading a captive is at camp; roles assigned; each herder picks a pasture; rut guarding. Then 4 dawn
   sub-ticks (`dawnSub`): herders lead their herds out toward pasture; captive-leaders walk home; wolves
   end their hunting bout (`wolfTick`, C49). Then hungry-wolf scent from where wolves lie up for the day.
3. **Day**, 6 sub-ticks (`daySub`): humans move (herders toward pasture, hunters up the goat gradient,
   foragers to their cutting cell, captive-leaders home); hunter presence marked; every goat steps and
   grazes; index rebuilt; hunters attempt.
4. **Mating**, once, on end-of-day positions (`mate`).
5. **Dusk**, 4 sub-ticks (`duskSub`): herders of penned herds walk home and the herd follows; hunters
   leading captives walk home; other humans are home; kids follow mothers; wild goats bed down; wolves
   begin a hunting bout (`wolfTick`).
6. **Herd night** (`herdNight`): foragers' loads stored; strays retrieved or lost; the kept habituate;
   offtake and culling; index rebuilt.
7. **Night**, 3 sub-ticks (`nightSub` → `wolfTick`): wolves hunt; goats flee wolves they spot.
8. **Life history** (`lifeHistory`), once per goat: age, milk, fodder, upkeep, gestation, lactation,
   milking, growth, starvation, background death, weaning, forgetting, birth. Wolves get hungrier.
   Camp kidding records at year end.
9. Dead removed, newborns added.

**C4** Within each pass agents act in array order (asynchronous). Goats move on the index from the
previous sub-tick.

---

## 4. Design concepts (short)

Nothing is scored. Each trait's benefits and costs come from mechanisms, and every trait also carries
the genome's reproductive cost. Humans and wolves see behaviour and visible traits, never genes.
Adaptation is genetic (eight traits) and plastic (learned threat-specific fear; size on nutrition;
breeding on condition). Herd demography, gene flow and herd size are emergent from movement and
encounters, except the offtake rate, which is an experimental parameter.

---

## 5. Initialisation

**C5** Vegetation pre-warmed 20 years. **C6** 800 goats on random land cells; random sex; age 0–6 y;
alleles ~U[0,1]; E = 0.6 capacity; fears 1. Goats ≥ 720 days start at target size, younger ones at
birth size with no mother. **C7** 60 wolves on random land cells. **C8** No humans until year 300.
**C9** `seed` makes a run reproducible.

## 6. Input data

None.

---

## 7. Submodels

### 7.1 Landscape and vegetation
- **C10 Wetness** = max(0.35, 1 − d/15) for d rows from the bank (floor reached ~row 10).
- **C11 Escape terrain**: elevation > 0.55 and ruggedness > 0.55 (~17–28% of land by seed).
- **C12 Seasons**: growth multiplier, a raised cosine peaking day 100 (mid-April), positive for 40% of
  the year; the rest is the lean season.
- **C13 Vegetation**: v += 0.04 × growth × wetness × (v + 0.15)(1 − v) − 0.004 × (1 − growth) × v,
  floored at 0.03, K = 400 fu.
- **C14 Lean forage quality**: forage eaten in the lean season yields 0.4 of its growing-season energy
  (`leanQuality`; dry, dormant forage). This is what makes the lean season lean.
- **C15 Camps**: 3, at x = 13, 40, 67, one row inland from the bank.

### 7.2 Genome
- **C16** Eight traits: R reactivity, A aggression, S gregariousness, B body size, H horns, T season
  breadth, M milk capacity, W pigmentation. A ninth, L twinning (2026-11-05), acts only when
  `twinMax` > 0 (C26). Its alleles draw from a second random stream, and it is left out of the genome
  cost (C22) and of IBD (C21), so runs with `twinMax` 0 reproduce runs from before it existed (checked:
  0 of 200 years differ in H4, H5 and H5 with genome costs on). A tenth, C coat marking (2026-11-10, with Chris),
  is neutral: no mechanism reads it, only sireRule `'marked'`. It draws from a third stream and is likewise left out
  of the cost and of IBD.
- **C17** Diploid, 2 loci per trait (haploid, L = 4, 6 available); allele values in [0,1]; trait = mean
  of its alleles. **C18** Free recombination. **C19** Each inherited allele moves U(−0.04, +0.04) once
  per meiosis, clamped to [0, 1]. **C20** No expression noise; switchable links W ← R (pleioW) and A ← R (pleioA), both 0.
- **C21** Lineage ids ride with alleles (identity by descent), relabelled at year 400.
- **C22 Reproductive cost of the genome.** p = mean of the eight expressed traits. Growth rate ×
  (1 − 0.5p) (later maturity). Each mating's conception chance × (1 − 0.5 p_doe) × (1 − 0.5 p_buck).
  Unconditional: it applies however well fed the goat is. (There are no trait running costs.)

### 7.3 Energetics and growth (`Goat.graze`, `Goat.daily`)
- **C23 Grazing**, each day sub-tick, where the goat stands: 1/6 of a day's appetite 1.6 × size^0.75 ×
  a/(a + 0.05) (a = cell biomass above floor, as a fraction of K), kids scaled by age/weaning age,
  alarmed goats × 0.75; capped by reserve room plus a sub-tick's upkeep; × lean quality (C14).
- **C24 Upkeep**: 0.6 × size^0.75 fu/day (body only). Reserve capacity 60 × size. Starvation at E < −leanBuffer × size.
  - **Lean-tissue buffer** (`leanBuffer`, 2026-11-10; 12,000 by default from 2026-11-11, 0 before): E may fall to −leanBuffer × size before
    the goat dies, standing for lean tissue burned once fat is gone; a fed goat refills it before rebuilding fat.
    About 12,000 kcal per unit size puts death at roughly 70% of lean body weight for a 50 kg goat (Turner et
    al. 1993, a rule from their ungulate model, not a measurement), about 5-7 days of total fasting after the
    fat reserve. Below zero a goat weighs food above safety more (foraging need > 1), does not breed, and a
    mother gives no milk. Chris, 2026-11-10: death at the first day of an empty reserve made the starvation count
    a knife-edge on the ration, not a deficit.
- **C25 Growth** (defaults from 2026-11-18, with Chris; EXPLOG 2026-11-14 to 11-18): target = 0.6 + 0.8B, × `sexSize`
  1.7 for males (bezoar weights). While E > 0.4 capacity a goat grows at its curve's rate × (1 − 0.5p) size/day, at
  60 fu per unit size. `growthCurve` 'curved' (Chris 2026-11-16): every goat advances one daily chunk,
  (1 − 0.15)/(`growYearsF` 3.75 × 360), along the line from birth size b to target T, bent by `curveExp` 2:
  ds = chunk × k × ((T − size)/(T − b))^((k − 1)/k), so growth slows to 0 at the target and a bigger target takes
  longer (Animal.curveRate). Birth size 0.15 × the sex-neutral target (males × `maleBirthSize` 1.1). Other rules:
  'linear' (+0.0035 a day; the default before 2026-11-18), 'vb' (von Bertalanffy), 'ogm' (ontogenetic growth model).
  Adult (for mortality, sires and culling) at 720 days; growth continues past that while size < target.
- **C26 Gestation**: birth 148 days after conception (nominal 150; an off-by-two in the counter, kept
  because it is immaterial), 0.15 fu/day, one kid. **Twins** (`twinMax` > 0): at conception a doe
  carries twins with chance twinMax × L (two meioses, one sire). Each twin is born at 0.8 × the single
  birth size (`twinBirthSize`), with reserves to match; twin gestation costs 2 × 0.8 = 1.6 × a single's,
  by litter birth mass. A doe's kid record (the opportunity cull's keep value) counts both.
  **Triplets** (`tripletMax` > 0, with Chris 2026-11-05): a twin pregnancy becomes triplets with chance
  tripletMax × max(0, 2L − 1), so only does with L above 0.5 have them. Each triplet is born at 0.7 ×
  the single birth size (`tripletBirthSize`); gestation costs 3 × 0.7 = 2.1 × a single's. Off, runs
  match the code before triplets exactly. At tripletMax 0.2, one-seed smoke runs gave 0.6–2% triplet
  litters (wild bezoar in Turkey: about 4%).
- **C27 Kids**: milk need 0.6 fu/day at birth, falling to 0 at weaning (120 d); a kid takes
  min(need, mother's capacity − herders' take, mother's E). Herd orphans draw on the camp milk pool.
  Twins and triplets share one capacity equally: each kid takes up to (capacity − herders' take) / the
  litter's live unweaned kids (2026-11-05; before, the kid processed first, always the same one, drank
  its fill and the next got what was left, so second twins starved). A hunter who kills a nursing doe
  takes home one orphan.
- **C28 Lactation**: capacity 0.6 × (0.5 + M) fu/day. She lactates (and is milked) while any kid of her
  litter is unweaned; before 2026-11-05 only while the first was, so a surviving second twin drank free
  (twin runs before commit a7c2895 carry that; twins off is unaffected). Milking (`milkIntensity`) takes
  that share of capacity each day before the kids drink. `milkCondition` (2026-11-12, with Chris; 0 = off):
  capacity falls with her condition, full at a reserve of `milkCondition` × cap or more, in proportion below,
  none at an empty reserve, so kids and herders both get less from a thin doe (yield tracks body condition:
  Flores-Najera et al. 2021). **Cost** (`milkCost`): `'made'` (default from
  2026-11-05, with Chris) charges the doe for the milk made, what her kids drink (as they drink it) and
  what the herders take, so capacity is a ceiling and costs nothing unused; `'capacity'` charges the
  whole capacity every day, needed or not, as every run before this did (it reproduces them exactly).
  Under `'capacity'` M fell from 0.50 to about 0.18 in 1,600 years, wild and herd alike
  (results/milk2).
- **C29 Kid exposure**: available (`kidExposure`), off.

### 7.4 Reproduction (`updateReceptive`, `World.mate`, `World.fight`)
- **C30 Heat.** A doe is in heat on a day if: not pregnant; age ≥ 480 d; size ≥ `breedSizeFrac` 0.65 target (0.8 before
  2026-11-18); E ≥ 0.35
  capacity; within ±(15 + 120T) days of day 330; and on her own oestrous phase (1 day in 21). With
  `postpartumDays` > 0 (default 0), also not within that many days of her last kidding.
- **C31 Mating is spatial.** A doe in heat mates among the adult bucks (≥ 365 d) in her 3×3 at the end
  of the day, herd or wild. With buck management, if one of her herd's sires (the 2 oldest herd bucks,
  or by `sireRule`; `'milk'`, with Chris 2026-11-09: the bucks whose dams gave the camp most milk a year,
  her record blended with the camp's mean as in C57, a dam never milked counting as the mean; `'deep'` /
  `'shallow'`, with Chris 2026-11-10: the most / fewest generations since the wild, genome-weighted, no trait
  (the grain paper's lineage-isolation test); `'homebred'`, with Chris 2026-11-10: the most generations of camp-born
  dams on the maternal line (gsc), as far back as the herder remembers (`herdMemory`, 3; 1 = camp-born over
  captured); `'marked'`: the most coat marking (C16); `'random'`, `'calm'`, `'gentle'`, `'large'` as in the sire profiles.
  Under every rule but the oldest, the opportunity cull keeps the bucks the rule chose; 'milk' since 2026-11-09,
  the others since 2026-11-10) is there, he mates her without a contest. Otherwise the bucks present contest in random order and
  the last holder mates. Gene flow into a herd happens only when wild bucks are near its does.
- **C32 Conception**: 0.7 × the two genome costs (C22).
- **C33 Contests** (sequential assessment, after Enquist & Leimar 1983): up to 8 rounds, the first 2
  display. Each round costs each buck 0.05 (display) or 0.15 (contact) fu. In contact rounds each risks
  death 0.01 × opponent's share of fighting ability × (1 + opponent's H). Fighting ability = size ×
  (1 + 0.5H). After each round each buck updates a noisy estimate (sd 0.25) of his relative strength and
  quits below 0.4 − 0.4(A − ½) + 0.2(R − ½) + 0.3(1 − E/capacity). If both quit in the same round, the
  one with the higher estimate stays. If neither quits, the stronger wins with probability equal to his
  share. If a fight kills both, the next live buck holds.
- **C34 Rut pull**: adult males foraging on their own (wild males, and herd males on a day their camp
  has no herder) add +0.5 to cells holding a doe in heat now.

### 7.5 Movement and behaviour (`Goat.step` and helpers)
- **C35 Alarm**, every sub-tick for wild goats, kids and kept goats: chance R × fearOfWolves if a
  wolf's scent is on the cell (by day, where hungry wolves rest; at dawn, dusk and night, where
  goat-hunting wolves are now), or R × fearOfHumans if a hunter is within 1 cell now. Herd goats with a
  herder react only to wolf scent and to the herder (C38), never to hunters. An alarmed goat flees 3 cells away from scent and
  hunters toward cliffs, and grazes at 0.75 that sub-tick.
- **C36 Wild foraging**: on a day sub-tick, with chance 2/6, one step to the best Moore cell by
  need × vegetation + 1.0 S ln(1 + min(company, 15))/ln 16 − 0.5 R fearOfWolves scent (× 0.15 on cliffs)
  − 0.5 R fearOfHumans presence + 0.1 R cliff + rut pull + noise. Company = goats within 4 cells.
  At dawn, dusk and night wild goats stay put unless alarmed, and then flee (the same rule as by day).
- **C37 Kids** follow their mother by moving up to 2 cells per sub-tick toward her.
- **C38 Herd goats** by day take one step per sub-tick by need × vegetation − (0.5 + S) × distance to
  the herder; at dawn, dusk and night they step toward the herder (out to pasture at dawn, home at dusk
  if penned). Spooked by the herder (day
  sub-ticks only: chance 0.05/6 × R × fearOfHumans × load each, load = max(0.25, herd/20), so load
  rises above its floor once a herd passes 5) a goat bolts 3 cells away; alarmed by wolf scent it steps
  toward the herder. A camp whose herd was empty at dawn has no herder that day; its herd goats then
  behave as wild goats and are not stray-tested.
- **C39 Kept at camp**: sheltered kids (< 30 d, H5), tethered goats (H5) and rut-guarded does walk to
  the camp cell (1 cell per sub-tick) and stay there, grazing it. Tethered and rut-guarded goats get
  fodder all year (C61); sheltered kids only in the lean season. None are stray-tested.
- **C40 Captives** walk with the hunter leading them. While led they count in the herd (and its load),
  are safe from wolves, are not stray-tested, culled or habituated, and a led doe in heat can still
  mate (led bucks cannot). A captured doe's wild kid stays wild but follows her into camp.

### 7.6 Mortality
- **C41 Background**: 0.03/y, + 0.15 in the first year, + 0.25 per year past 9. **C42** Other deaths:
  starvation (C24), fights (C33), wolves (C49), hunting (C52), culling (C57).
  **Small kids die more** (`juvSizeExp`, with Chris 2026-11-05): the first-year 0.15 is multiplied by
  (ref / size)^1.5, ref the size of a single with the same target born and grown at full rate to that age
  (min(target, 0.15 target + 0.0035 age)). Twins (born 0.8) and triplets (0.7) start at 1.4× and 1.7×,
  and a kid short of milk falls further behind. At 0 the hazard is flat, as in every run before; that
  reproduces commit ec96ea3 exactly (H5 with twins, seed 1, 300 years: 0 of 300 years differ). Studies of
  managed goats give twins 1.0–1.3× (once 2.5×) and triplets about 2× singles' pre-weaning mortality
  (Angora 10/13/22%; Pakistani desert goats 7.3/9.6/16.7%; Borana 30/30/57%). One-seed smoke, years
  201–300 (twins, triplets on): wild twin deaths per kid 1.06× singles at 0, 1.29× at 1, 1.34× at 1.5,
  1.25× at 2, 1.45× at 3; wild twin litters 46% at 0, 31–37% at 1–3.

### 7.7 Learned fear
- **C43** Fears of wolves and humans, effective fear = R × learned fear. **C44 Sensitisation**:
  surviving an attack +0.3R; every goat in the 3×3 of a kill +0.15R; cap 3. **C45 Forgetting** toward 1
  at 0.002/day. **C46 From the mother**: a kid starts with its mother's fears, and while following her,
  each sub-tick she is alarmed its fears move 10% toward hers.

### 7.8 Wolves (`World.wolfTick`, `World.wolfAttack`, `World.killChance`)
- **C47** Fixed guild of 60; fullness −0.08/day; hungry below 0.5. Never breed or starve.
- **C48 Prey switching on own experience**: at the start of each bout (first dusk sub-tick) a hungry
  wolf hunts goats with chance s²/(s² + 0.3²), s = its memory of finding goats (updated 10% toward 1 or
  0 at the end of each goat-hunting bout, the last dawn sub-tick); otherwise it hunts other game and is
  filled with chance 0.15.
- **C49 Hunting bout**, dusk → night → next dawn (4 + 3 + 4 sub-ticks; wolves rest by day). Each
  sub-tick: every wolf moves (a goat-hunting wolf one cell at random among the neighbouring cells that
  have goats within 3 cells, others roam); goat-hunting wolves' scent marks the cells within 1; every
  goat takes its step (C35–C38: spotting the scent it flees, wild goats away toward cliffs, herd goats to
  the herder; penned goats stay in the pen); then each hungry goat-hunting wolf attacks once. A wolf
  stops when fed. Detection of each goat in its 3×3: 0.5 (1 − 0.5W)/(1 + 0.15 (goats in the 3×3
  around the goat − 1)). A detected goat spots the wolf with chance
  R × fearOfWolves (alarmed). The target is drawn weighted by kill chance: 0.15; × 3 for kids; older goats
  defend by 0.3 (size − 0.6)/0.8 + 0.2A + 0.2H (males), clamped to [0, 0.9]; × (1 − 0.6 × flight), flight = 1 alarmed, 0.5 warned (each other
  weaned goat in the 3×3 spots it with chance 0.6 R fearOfWolves), else 0.5 min(1, R fearOfWolves);
  × 0.15 on cliffs.
- **C50 Herd protection**: a herd goat on any camp's cell × 0.2 if penned or kept at camp; with
  guarding, any herd goat × 0.3 more, and first a 0.2 chance the guard kills the wolf (replaced by an
  immigrant at the upland edge, with a fresh memory).

### 7.9 Humans
- **C51 Roles**, each dawn: a camp with a herd sends one herder; each other human hunts (0.3), forages
  (0.3) or stays in camp (0.4). Fixed shares (§10, G5).
- **C52 Hunting**: a hunter walks 1 cell per sub-tick up the gradient of wild goats sensed within 4
  cells (herd goats are not quarry) until wild goats are in his 3×3, then makes up to 2 attempts (the
  8-cell range never binds in 6 sub-ticks). Detection 0.6 (1 − 0.25W); a detected goat may spot the
  stalk (0.6 R fearOfHumans) and is then alarmed (it does not move, but is harder to kill); the target is drawn by success × size; success =
  0.5 (1 − 0.8 × flight) (flight as C49, fear of humans), × 0.5 on cliffs; one kill per day. Hunters
  disturb goats within 1 cell (C35). A failed kill alarms the goat and adds 0.3R fear of humans. A hunter
  who has made his kill walks on, disturbing goats, until dusk. Hunters are home at dusk (teleported).
- **C53 Capture** (from year 400): on an attempt, with chance 0.2, the hunter tries to take a goat alive
  instead: a random visible, unalarmed wild goat; he closes in over 3 steps, and at each it may bolt
  (0.6 R fearOfHumans). If it never bolts it is caught, joins the herd, and walks home with him; if it
  bolts it is alarmed and gains 0.15R fear of humans. If no goat is visible he makes an ordinary hunting
  attempt instead. A hunted doe's nursing kid is captured too.
  - **Gene-flow switches** (2026-11-10, both off by default): `captureUntil` is the year from which camps take
    no more goats alive, neither captures nor orphans (C27); `wildSireBlock` 1 means a herd doe never mates a
    wild buck, so wild genes enter the herd only through captives, including does captured pregnant;
    `wildSireBlockFrom` (2026-11-11, default 0) is the year that block starts, so an isolated herd can stop both
    routes in the same year.
  - **Immigration into the wild** (2026-11-11, with Chris; `immigrationRate`, off): the map is a corner of a much larger
    wild range. From `humansAt`, at each year's start, that share of the adult wild goats (not pregnant, no kids at foot,
    not being led; stochastic rounding) is chosen at random and swapped in place for an immigrant drawn from
    `immigrationPool` (genomes and learned fears of adult hunted wild goats, sampled from hunted-only runs by
    tools/pool.mjs): same place, sex and age; a new id and fresh lineage ids; no herd ancestry; adult size from its own
    genes. Headless only (load.mjs reads the pool). No random draws when off.
- **C54 Foraging**: a forager claims, for the day, the unclaimed cell within 6 cells of camp that will
  yield most: min(room in the load, 4 fu × sub-ticks left after walking there, what the cell holds),
  so gatherers spread out and trade distance against lushness; it cuts 4 fu per sub-tick (removed from
  the cell) up to a load of 20 fu and re-chooses when a spot is spent; loads are stored at camp each
  night; the store spoils 0.5%/day. Without the economy, foragers cut vegetation from year 300; the
  cutting is a real grazing cost to wild goats near camps. (In the economy, C68.)

### 7.10 Herding and husbandry
- **C55 Herder**: picks the best pasture within `herdRange` cells of camp (penned; this can be the camp cell),
  or within 2 cells of where he slept and no more than 2 × `herdRange` from camp (unpenned), and walks there
  (`herdTravel` cells per sub-tick at dawn, 1 by day). `herdRange` is 8 by default from 2026-11-11 (4 before),
  and is a key sweep variable: herd size follows the pasture it reaches (EXPLOG 2026-11-11, herd travel).
  - **Herd travel** (`herdTravel`, 2026-11-11; 2 by default, 1 before and in every earlier run): at dawn and dusk a herder leading a herd, and
    its goats following him (C38), cover `herdTravel` cells per sub-tick. With 1, a penned herd at pasture more
    than duskSteps (4) cells out is not home by the night check (C56), so `herdRange` above 4 loses the herd
    (EXPLOG 2026-11-11, herder range); a faster walk out and home lets the herd use further pasture.
- **C56 Strays and retrieval**: after dusk, a herd goat that is not at camp (penned) or is more than 2
  cells from the herder (unpenned) has strayed. If it is more than 6 cells away it is lost; otherwise
  the herder closes in over that distance, and it is lost if it bolts at any step (the approach test,
  as C53), else brought back to the pen or the herder. The kept habituate (C58). Strays that cannot
  reach camp in the 4 dusk sub-ticks from the edge of the herder's range are a small source of tests
  (~0.2% of penned goat-nights).
- **C56a Run-offs** (`refetchRunOffs`; 2 by default, with Chris 2026-10-24): a goat spooked by the
  herder (C38) beyond 2 cells is *loose*: still the herd's, but moving as a wild goat (C35–C36, its
  gregariousness may bring it back). It rejoins if it comes within 2 cells of the herd's leader. Each
  keeper (the herder, or in the economy each keeper, C71) makes at most one attempt per day or dusk
  sub-tick on the nearest loose goat within 6 cells that has been loose ≥ 2 sub-ticks (`chaseDelay`):
  the approach test over the distance; lost if it bolts, else back with him. Still loose at the end of
  dusk: the night stray test (C56). Mode 0: run-offs drift back on their own; mode 1: chased at once.
  Observed fates: ~20% rejoin, 53–59% fetched back, 15–24% lost on the chase.
- **C57 Offtake and culling**: each night a camp slaughters at `offtakeRate` of its herd per year (0.1 in
  the condition table; an experimental variable), chosen by cull rule; an optional hard cap
  (`herdTarget`) is off. `cullFloor` (2026-11-11, with Chris; 0 = off): the offtake never takes a camp's herd
  below that many goats (the night's draw is still made, so off reproduces earlier runs); other losses can.
  `surplusCull` (2026-11-12, with Chris; 0 = off): before the offtake, each night the herder slaughters every
  weaned herd male beyond the camp's sires (C64's chosen) and `insuranceBucks` spares (2; the oldest other
  weaned males). These culls are credited against the offtake draws of the same year, so the year's offtake
  is the larger of the two; `cullFloor` does not stop them. Records `surplusBucks` a year. (Before it, the offtake count was
  a fixed share of the herd whatever its make-up, and adult bucks built up to 1.0-5.6 per doe in one isolated camp: EXPLOG
  2026-11-12 diagnostic.) `winterCull` (2026-11-12, with Chris; 0 = off): on the first lean day, after the
  surplus cull, the herder budgets a full ration (`provision` × size^0.75 a day) through the lean days ahead for
  each breeding-age doe and each goat under a year (bucks and dry yearlings winter on grazing), and while the
  camp's fodder store falls short slaughters among those goats in the cull rule's order, never below
  `cullFloor`; credited against the year's offtake like the surplus cull. Records `winterCulled` a year. (The
  first form, b9ec5e5, budgeted every goat and held the open reference herd at about 60.)
  - *random* (H2); *opportunity* (H3–H6): lowest keep value first: + next year's growth on the goat's curve toward
    the size the herder expects (`growthCredit` 'herd', the default: the herd's mean size of its sex among goats of
    720 days or older, `creditAge`; Chris 2026-11-18, a learned expectation, since a herder cannot see a target; this
    credit is what shrinks herd body size, EXPLOG crossover 2026-11-17. Options: 'own' the goat's own target, 'cull'
    the camp's running mean size at slaughter by sex, 'max' the herd's largest goat of the sex) + for does under 9: 0.3 × expected kidding
    over the next 3 years (`keepHorizon`, ≈ age at first kidding; each year × the chance she lives to
    it, 0.97 per year; the first year at half for does under 480 d). Each year's rate is her own
    record weighted by its length (years/(years + 1)) blended with the camp's record for does of that
    age (the herd's mean until that age class holds more than one doe-year; only kids born in the herd
    count)
    + for the 2 oldest bucks: 0.3 × herd rate × does per sire; the oldest young buck as a replacement at
    half that − 0.15 feed − annual death hazard (per head; `cullSizeNeutral` 'sex', the default from 2026-11-18:
    both charged at the sex's size multiplier, 1.7 for a buck) − (H6) 1.0 × R × fearOfHumans, + N(0, 0.05).
  - **Milk in the keep value** (`milkValue`, off; with Chris 2026-11-09): a doe's expected milk to the camp
    over the same 3 years, built like her kidding (her own record of milk taken per year since breeding
    age, blended with the camp's milk per doe-year for her age class, survival-discounted), × milkValue /
    36,000 kcal per meat unit (1 = milk worth its food energy as meat). At 50% milking a doe gives about
    1,100 kcal a nursing day, so at 1 her milk outweighs her kids several times.
  - **Each sex's own cull rule** (`buckCull`, `doeCull`, both off; with Chris 2026-11-10; count cull only, not
    `econCull`): the cull rule above still sets how many of each sex are eaten; within the places it gave a
    sex, that sex's rule picks which go. *random*; *calm* (most run-offs seen per year watched first);
    *large* (smallest for its sex and age in years first); *homebred* (fewest generations of camp-born dams,
    up to `herdMemory`, first: captives first); bucks only, *youngMales* (0.5-2.5 y, then older, then kids).
    A buck rule never takes the herder's sires (as `sireRule` picks them).
- **C58 Habituation**: every kept herd goat each night, fearOfHumans → 0.05 at rate 0.1 inside the
  socialisation window (age < 180 (1 − R) d), 0.02 after.
- **C59a Exchange between camps** (`exchangeN`, 0; with Chris 2026-11-10): at each year's end every camp with a herd
  gives `exchangeN` adults, at random, to another camp with a herd, at random: never its sires, a tethered, guarded or
  led goat, or a doe with a kid at foot. The receiver starts watching it afresh; its lineage goes with it.
- **C59 Herd size** is not capped: it emerges from captures, births, losses, offtake, and the herder's
  load (C38), which raises spooking and so straying in proportion to herd size above 5.
- **C60 Milking** (off in all conditions): herders take a share of capacity into a camp pool that halves
  nightly and feeds herd orphans. Each doe's total taken is her milk record (C57, C31).
- **C61 Provisioning** (H5): herd goats get up to 0.6 size^0.75 fu/day **from the camp fodder store**
  in the lean season (kept-at-camp goats all year), limited by what the store holds: each goat takes its
  want (up to that ration and its reserve's room) in population order until the store is empty.
  `fodderRation` (2026-11-12, with Chris; 0 = off): in the lean season each camp's daily budget is its store
  over the lean days left (today included), so the store lasts the season; pregnant or nursing does and goats
  under a year are fed first, then the rest, each class in proportion to its goats' wants (no random draws).
- **C62 Kid shelter** (H5): herd kids under 30 d stay at camp; **C63 Tethering** (H5): a herd goat
  with R × fearOfHumans ≥ 0.35 stays at camp until it habituates below that; **C64 Buck management**
  (H5): C31; **C65 Guarding** (H5): C50; **C66 Rut guarding** (off): a doe in heat stays at camp with
  chance `rutGuard`, and with buck management so do her herd's sires.

### 7.11 Conditions (`tools/conditions.json`)

| | Humans | Herding | Cull | Pen | Husbandry |
|---|---|---|---|---|---|
| H0 | none | — | — | — | — |
| H1 | hunt, forage from 300 | never | — | — | — |
| H2 | hunt, forage | from 400 | random | no | — |
| H3 | hunt, forage | from 400 | opportunity | no | — |
| H4 | hunt, forage | from 400 | opportunity | yes | — |
| H5 | hunt, forage | from 400 | opportunity | yes | guard, fodder 0.6 (from store), kid shelter, buck management, tethering |
| H6 | hunt, forage | from 400 | opportunity + flightiness cost 1.0 | yes | — |

Offtake 10%/y in H2–H6 (the highest rate tested at which unpenned H3 herds persist: 57 → 114 goats
with the 3-year horizon, ~10 at 20%; H5 holds ~80 at 20% and collapses at 30%). No herd cap; herd
size is otherwise limited by C59.

### 7.12 The camp economy (`economy` = 1; notes/human-economy.md; with Chris, 2026-10-23 to 10-25)

Replaces fixed human policies (C51 shares, C53 capture by hunters, C57 offtakeRate, C61 provisioning
by switch, C65 global guarding). Human numbers stay fixed (`humansPerCamp`, 10 in economy runs); the
camp optimises income, and consumption is a sink.
- **C67 Currency and stores** (fu, as goats): meat (loses `meatDecay` 5% of its nutrition a day),
  human plant food (spoils `plantSpoil` 0.3%/day), slop (spoiled plant food, goat fodder), cut fodder
  (spoils 0.5%/day), and the herd (stock value = `meatYield` 40 × size per goat).
- **C68 Human plant food** (seeds, tubers, fruit; goats eat it only as crop damage, C77):
  `foodPatches` 120 patches, centres drawn in proportion to wetness, radius 2, fill 0.5; site capacity
  `foodSiteK` 800 fu × lognormal(0.5); each year each patch draws a yield factor, lognormal(0.6)
  (masting). Food ripens across the fruiting window (day 150 ± 45, linear to the year's capacity) and
  rots 3%/day outside it. Gatherers harvest it (C54 choice rule on the food field) into the plant store.
- **C69 The sink**, each night: demand = people × `needPerPerson` 2.5 + `groupSink` (0; to be used to
  drive offtake once herds are robust). Eaten from meat, then plant food (`plantValue` 1), then by
  slaughtering herd goats in keep-value order (C57 opportunity rule) while short; unmet demand has no
  consequence. Offtake is therefore an outcome.
- **C70 Role choice** (after Marriott & Gershenson 2011): at dawn each person picks gather, hunt or
  herd with probability proportional to the camp's decaying estimate (`returnTau` 30 d) of that role's
  return per labour-day, after a random choice with chance `roleFloor` 0.1; an untried role is valued
  at the best known. Returns per labour-day: gather = plant food delivered; hunt = meat delivered
  (`meatYield` × size; hunters only hunt); herd = (offtake + Δ herd stock value + `meatDecay` × stock)
  ÷ herders: what is taken, plus the change in what is saved, plus the spoilage that storing food alive
  avoids. Herding is available once herding is allowed, herd or not.
- **C71 Herding tasks** (camp-level priority): the first herder keeps (leads to pasture, C55; keeps
  the herd together; chases run-offs, C56a; night strays, C56; herder load counts keepers). Each
  further herder takes the task whose decaying signal ÷ (1 + those already on it) is largest, or a
  random task with chance `roleFloor`. Signals, fu of goats at risk per day: keep, herd goats run off or
  straying; guard, herd goats attacked by wolves; feed, herd goats hungry (reserve < 40%); capture, fu
  captured per capturer-day. A camp with no herd sends its whole crew to capture.
- **C72 Guards** protect herd goats within 1 cell of themselves (C50 factors), walking with the herd.
- **C73 Feeders** cut vegetation as fodder (C54 rule on the grass), stored at camp; herd goats are fed
  up to 0.6 size^0.75 fu/day all year from slop first, then cut fodder.
- **C74 Capturers** walk out like hunters (C52) and only take goats alive (C53 approach test).
- **C75 Spoilage cascade** (with Chris, 2026-10-25): spoiled plant food becomes slop (`slopValue` 1);
  spoiling slop is thrown on the dump heap; each fu on the heap seeds a new food site within
  `heapRadius` 2 of camp with chance `heapSeed` (its own patch and masting): near-camp gardens from
  waste ("dump-heap" origin of cultivation).
- **C76 Land competition**: a food-site cell keeps only `siteGrass` 0.5 of its vegetation capacity.
- **C77 Crop damage** (`cropDamage`): a goat (herd or wild) on a food site eats the standing plant food
  first, and counts it as forage when choosing where to move (it seeks crops out).

---

## 8. Observation

Every 30 days: population, kids, sexes, vegetation. Every year: genotype histograms and means per
trait (all goats, and the herded subset); learned fear; births, deaths by cause; kill-off by cause, sex
and age, and the herd's own kill-off; first kidding; adult mortality; captures, escapes, culls, milk,
fodder fed and foraged, wolves killed; herd and wild IBD; sires per camp-year; wild-sired share of herd
births; R of the year's captives; generations since capture. Unweaned kids (`kidLife`, from 2026-11-05),
by wild or herd and litter size: kid-days; energy wanted from milk, drunk from the mother, from the camp
milk pool, grazed, and fed as fodder; at weaning, size, size over target, and condition (E/capacity),
and how many had lost their mother; kid deaths with the mother dead. Herd conceptions by origin (from 2026-11-10; does already
in the herd, so a doe captured pregnant is not counted): dam captured or camp-born, by sire wild, captured,
camp-born, or another camp's. Realized selection differentials
per trait (diploid): each herd kid's maternal allele mean minus the genotype mean of its camp's adult herd does
at the year's start (`selDam`), and its paternal allele mean minus the bucks' (`selSire`; not for wild sires),
averaged over the year's herd kids (`selN`).
Lineage depth (from 2026-11-11, with Chris): a goat's genome share by generations born in a herd (`Goat.wv`, 24
slots; null = no herd-born ancestry). A herd-born kid takes each parent's half one generation deeper, a fully wild
parent's half at 1. A wild-born kid of escaped herd stock (feral) takes its parents' shares at the same depths, a fully
wild parent's half at 0, so feral lines keep their herd generations and add none. Capture resets a goat to null, and a
herd kid's wild sire counts as fully wild (both as before, so the deep and shallow sire rules see what they saw).
Nothing in the model reads a wild goat's depth. Every 10 years: genotype histograms per trait by lineage class
(`histDepth`): herd goats by mean depth rounded (0 | 1 | 2-4 | 5-9 | 10-19 | 20+), wild goats by the share of the
genome from herd-born goats (none | to 1/16 | 1/8 | 1/4 | 1/2 | more; a wild goat's mean depth would mix how much
herd ancestry it has with how deep it is). Every year: wild goats' mean herd-born share (`wildHerdShare`) and the
share of wild goats with any (`wildAnyHerd`).

## 9. Calibration status (2026-10-21)

Wild type (H0, 10 seeds × 500 y, `results/stage2v4`): 10/10 persist (252–469 goats); 88% of goats in
herds of ≥ 5; first kidding 2.81 y; adult mortality 0.23/y; R 0.64, A 0.74, S 0.39, B 0.89, H 0.80,
T 0.44, M 0.18, W 0.81. Most numbers in §7 are calibration choices, not data; literature-backed ones:
gestation, weaning, rut timing, spring kidding, oestrous cycle length, first kidding, heritable R, and
the Ganj Dareh targets.

---

## 10. Open items

- **G5. Human time is fixed shares.** Balancing hunting against foraging by payout needs a common
  currency (meat vs fodder), i.e. a human metabolism; deferred.
- **G6. Herders see the best pasture within range** (C55; kept by choice) and **wolves are replaced at
  the edge** (C50; kept by choice); **hunters return home instantly** (C52; kept by choice).
- **G7. No stress cost of R at density** and **litter size is always 1** (unchanged).
- **G8. B sits near the top of its range** (0.89) in the wild type, so it can fall under domestication
  but has little room above.
- **G9. Too many herd goats live past 4 years** (0.33–0.37 of herd deaths ≥ 1 y vs Ganj Dareh ~0.20)
  once the keep horizon fixed the female side. Does keep their worth to age 9 because nothing in the
  model makes an older doe kid less (no reproductive senescence, litter size 1); a herder has no
  observed reason to cull her early. Candidate: age-declining fertility, which the camp record would
  then pick up on its own.
- **G10. A wolf that rarely hunts goats rarely relearns them** (C48 updates its memory only on
  goat-hunting nights; at s = 0.05 it hunts goats 2.7% of nights). Whether this matters depends on how
  often wolf memories fall that low; not measured.
- **G11. Dusk is as long as the herd range** (4 sub-ticks, 4 cells), so a goat at the edge of a penned
  herd's range may not reach camp by nightfall and is stray-tested (~0.2% of penned goat-nights).
  From 2026-11-11 the default walk home (4 sub-ticks × herdTravel 2) again equals the range (8); with
  herdTravel 1, ranges 6 and 8 lost every herd (EXPLOG 2026-11-11, herder range).
- **G12. Penned herds without husbandry stay small** (H4, H6: ~22 goats over 3 camps vs ~90–115
  unpenned), at 2–13 per camp, single herds lost and refounded (generations since capture 3.9 vs 21–33).
  Doe condition, pregnancy share and heats match unpenned herds, and it is not offtake. *Found
  2026-10-22 (`tools/kidfate.mjs`, 2 seeds, years 520–560):* food. H4 + lean-season fodder only
  (provision 0.6) holds 87–88 goats (vs 22), doe share 0.37 → 0.50, births per doe-year 0.70 → 0.87.
  A penned herd can only graze what it can reach and walk back from in a day (6 day sub-ticks, range
  4); widening the range to 8 shrinks herds to 8–10 and raises starvation (0.07 → 0.11 per goat-year),
  because the herd spends the day walking. Unpenned herds escape this by moving on and sleeping out.
  Kid survival (0.90–0.93) is the same in all.
- **G13. The genetic R signal is weak** (herded − wild −0.02 to −0.06; captives ≈ herd). *Diagnosed
  2026-10-21:* not habituation. Wild R itself rises under hunting (0.62 → ~0.86 by year 400), and herds
  start from that. Herd R fell to ~0.3 before the cold check (H5, no culling) because the herder also
  spooked goats at dusk. A goat bolting on the walk home is still out at the nightly stray test and is
  lost by the approach test (R × fear), so ~22 reactive goats a year were filtered out. Single-fix
  bisection on 7b7e356 (H5, 2 seeds × 600 y): only the dusk-spook fix moves herd R (0.50 → 0.77;
  escapes 22 → 6/y). With dusk spooking back at the same daily rate (`spookAtDusk 1`, 3 seeds): herd R
  0.67–0.72, escapes ~21/y, vs 0.78–0.85 and ~6/y without. So the filter's strength depends on the
  gap between a spook and the once-a-night stray test: spooks by day are undone by regrouping before
  dusk. A more local alternative: the herder deals with a stray when it strays (any sub-tick), not
  once at night. *Built as `refetchRunOffs` (off by default pending a decision):* a goat spooked beyond
  keepRadius is gone after at once by the approach test. At herderAlarm 0.05 herds collapse (H3 113 →
  3, H5 92 → 24) and track wild R. Sweep (3 seeds × 600 y, final 100 y), herd / wild R, herd size,
  run-offs lost per year: H5 0.005 0.82/0.87, 90, 6; 0.01 0.82/0.87, 87, 12; 0.02 0.74/0.84, 79, 19.
  H3 0.005 0.84/0.87, 57, 3.5; 0.02 0.89/0.90, 9, 1. An R signal needs herds that can absorb losses of
  ~20% a year (H5's husbandry can; unpenned H3 cannot). The refetch uses the hunter's stalk-detection
  rate (0.6 R × fear per step); herd goats' habituated fear (~0.14) already makes it ~7× easier per
  step than stalking a wild goat. *Sweep, 4 seeds × 800 y (`results/sweep_spook`), herd − wild R:*
  H5 off −0.09, 0.002 −0.04, 0.005 −0.04, 0.01 −0.10, 0.02 −0.19, 0.03 −0.24 (seeds −0.04 to −0.44),
  0.05 −0.16 (herd falls to 44); H5 herds hold 77–91 up to 0.03, while generations since capture fall
  10 → 3.5 and captures rise 2.9 → 7.1/y, so at high rates the gap is largely sorting (who stays)
  rather than breeding. H3 holds 85–102 up to 0.005 (gap −0.03 to −0.05) and collapses from 0.01 (≤18).
  H4 stays at 6–24 with a −0.02 gap at every rate.
  *Decomposition (`tools/filters.mjs`, H5 at 0.02, 3 seeds, years 600–800):* wild R 0.837 (near camps
  0.833); never-herded captives 0.79 (the capture filter, −0.04); ~61% of captures are recaptured
  escapees (fear of humans 0.35 vs 1.1, so they pass the approach easily; 38% with refetch off) at R
  0.72; herd goats that were captured 0.73, herd-born 0.69; kids equal their parents (0.70); run-offs
  lost 0.726 vs refetched 0.710, a small differential applied many times. So the gap is heritable
  selection by retention inside a herd whose lineage pool is partly closed by recapture, not just
  sorting. *Ablation (4 seeds × 800 y):* H4 + fodder only gives gap −0.17 at 0.02 (seeds −0.13 to
  −0.23; herd 75) vs −0.04 without refetch: the other husbandry is not needed. The two conditions
  together: a herd that can absorb run-off losses (food, G12) and a refetch that tests every run-off.
- **G14. The strength of small-kid mortality is not calibrated** (`juvSizeExp` 1.5, C41). Set
  2026-11-05 from one seed × 300 years at 0, 1, 1.5, 2, 3, against managed-goat studies (twins 1.0–1.3×,
  triplets ~2× singles' pre-weaning mortality). Across strengths the one-seed ratios do not order
  cleanly (wild twins 1.29×, 1.34×, 1.25×, 1.45×), and wild twinning fell from 46% of litters to 23–37%.
  Chris (2026-11-06): move on for now; this could be investigated. To do: several seeds per strength,
  and a target for wild twinning (feral goats on Macauley Island: 39% of adult does' pregnancies twins).

## 11. Non-local and stand-in steps remaining

Still non-local by choice: herder pasture scan, wolf replacement, hunters' return. Still stand-ins:
background hazards (kept by choice), kill-chance and protection multipliers, confusion and warning
formulas, learning rates, offtake rate (an experimental parameter by choice), keep-value constants
kidValue and feedCost (blended with camp records), "other game" for wolves.

## 12. Changes since v1 (ae4f03d)

Reproductive cost of the genome replaces trait running costs; kid exposure off; lean forage quality
added; oestrous cycles replace the flat 0.3; sequential-assessment contests replace the contest score
and hawk–dove fights; the day split into day/dusk/night sub-ticks; mating spatial (wildBuckRate and the
buckless fallback removed); herds, kids and captives walk; capture and stray retrieval as approach
tests; wolves switch prey on their own experience; foragers and a fodder store; herder load replaces
the herd cap; keep value blends individual and camp records; kids learn fear from their mothers; the
alarm flag is recomputed every sub-tick (bugs B1, B2 fixed); hunters no longer stall next to herd
goats (B3 fixed: they look for wild goats only). Growth 0.0035 and breeding size 0.8 recalibrated.

**v2.2 (2026-10-23, with Chris).** Crepuscular wolves: dawn sub-ticks added (herds walk out), wolves hunt
in every dusk, night and dawn sub-tick until fed (wolfAttempts unused), and goats flee wolves in real
time, the same rule as for hunters. Not yet recalibrated.

**v2.1 (cold check, 2026-10-21).** Culling never ran in v2 (offtake 0, no cap), so H3 = H2 and H6 = H4
in effect; the condition table now carries an offtake rate (§7.11). Fixed: hunters climbed a gradient
that included herd goats; the index was stale after the herd night (wolves found retrieved strays at
their old cells); unpenned retrieved strays were not brought in; the herder spooked goats at dusk too;
kept goats froze where they stood instead of walking to camp; rut pull used dawn positions; a fight
that killed both bucks ended the doe's chain; immigrant wolves inherited the dead wolf's memory; a
former herder could forage at yesterday's pasture; the camp record counted a captured doe's earlier
kids; the wild-sired share missed does captured pregnant. Several descriptions corrected.

**v2.3 (2026-10-23 to 10-25, with Chris).** The camp economy (§7.12, C67–C77): role choice by
decaying returns, herding tasks by camp-level priority, a second resource (human plant food:
patchy, masting, seasonal, placed by wetness), the spoilage cascade and dump-heap gardens, land
competition and crop damage. Loose run-offs (C56a, the default in all modes). Gatherers claim distinct
cells and weigh distance against yield (C54). An unpenned herd's sleeping place is remembered by the
camp. Not yet cold-checked.
