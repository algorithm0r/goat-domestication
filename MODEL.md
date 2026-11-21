# Animal Domestication — Model Description (v0.1.0, batch 1, plus record thinning and the sex-cull preference terms)

*2026-11-20. The model as it stands in the code: v0.1.0 (batch 1, frozen 2026-11-18), plus commits cda20ea (record
thinning, output only) and 1468afe (`buckPrefValue` / `doePrefValue`), written from the source. Structured after ODD
(Grimm et al. 2020). DESIGN.md is the intent; this file is what the code does. Every modelling choice has an ID (C1,
C2, …) for flagging, with its rule, default values and code location. Parameter names and values are those in
`src/params.js`, and every value given is the default unless marked otherwise; §7.11a lists what the batch-1
reference culture (REF) changes. The first version (choices C1–C66, bugs B1–B8) is in git at ae4f03d; §12 lists what
changed.*

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
vegetation (fraction of capacity K = `vegK` 1,440,000 kcal), camp id. Scratch fields: goat count, wild-goat count,
goats within radius 4 (`socialField`) and does in heat, rebuilt every sub-tick and after the herd
night; hungry-wolf scent, built at dawn from where wolves lie up; hunter presence, rebuilt each day
sub-tick and cleared at dusk.

**Goat**: position; genome (allele values + lineage ids); 10 expressed traits (R A S B H T M W L C, C16); genome
penalty p (mean of the eight core traits; computed but inert unless `reproCostGrowth` or `reproCostFertility` > 0, both
0 by default, C22); sex; age; target and current size; energy reserve E; mother; alarm flag (C35); learned fear of wolves and of humans; herd (camp id or −1); led-by (a hunter leading
it); kept-at-camp-today flag; generations since capture; father; gestation and fetus; nursing kid;
in-heat flag; oestrous phase; milk taken today; kid count; age at first kid.

**Wolf**: position, fullness, memory of finding goats, tonight's choice (goats or other game), attacks
left, kills. **Human**: camp, position, today's role (herd, hunt, forage, camp, return), target, cells
walked, attempts left, captive, forage load. **Camp** (3): position, milk pool, fodder store, record
of kids (and milk) per doe-year by age class.

**Scales.** **C1** One engine tick = one day; year = 360 days. **C2** Each day has sub-ticks: 4 dawn,
6 day, 4 dusk, 3 night (`dawnSteps`, `daySteps`, `duskSteps`, `nightSteps`). **C3** A cell is nominally ~1 km (with Chris, 2026-11-11; it was ~2 km. Nothing in the code uses the
scale: it only names what the cell-counted ranges and densities mean, e.g. herdRange 4-8 = 4-8 km). Runs: no
humans for 300 years, humans from year 300, herding from year 400; batch-1 experiments run 1600 years (exp001–exp004)
or 4000 years (exp005 on). **Units**: energy is in kcal of metabolisable energy, for goats' forage, reserves and
fodder and for human food alike (since 2026-10-28; before, forage units: in the goat world 1 fu = 3,600 kcal, so a
size-1 goat's maintenance of 0.6 fu is 2,160 kcal; human food 1 fu = 900 kcal). Meat (keep value) units are goat size
units, 36,000 kcal each (`meatYield`).

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
   culling (C57: the threshold cull every `cullEvery` days, or the nightly quota); index rebuilt.
7. **Night**, 3 sub-ticks (`nightSub` → `wolfTick`): wolves hunt; goats flee wolves they spot.
8. **Life history** (`lifeHistory`), once per goat: age, milk, fodder, upkeep, gestation, lactation,
   milking, growth, starvation, background death, weaning, forgetting, birth. Wolves get hungrier.
   Camp kidding records at year end.
9. Dead removed, newborns added.

**C4** Within each pass agents act in array order (asynchronous). Goats move on the index from the
previous sub-tick.

---

## 4. Design concepts (short)

Nothing is scored. Each trait's benefits and costs come from mechanisms. The genome's reproductive cost
(C22) is a switch, off by default since 2026-11-03. Humans and wolves see behaviour and visible traits, never genes.
Adaptation is genetic (eight core traits, plus twinning L where twins are on and the neutral marker C) and plastic
(learned threat-specific fear; size on nutrition; breeding on condition). Herd demography, gene flow and herd size are
emergent from movement and encounters. Under the batch-1 threshold cull (`cullRule` 'opportunity' with `econCull` 1,
C57) offtake is emergent too: the herder slaughters a goat once its keep value falls below a threshold. Only the
quota cull, used by the other cull rules and with `econCull` 0, sets an offtake rate as an experimental parameter.

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
  floored at 0.03, K = `vegK` 1,440,000 kcal.
- **C14 Lean forage quality**: forage eaten in the lean season yields 0.4 of its growing-season energy
  (`leanQuality`; dry, dormant forage). This is what makes the lean season lean.
- **C15 Camps**: 3, at x = 13, 40, 67, one row inland from the bank.

### 7.2 Genome
- **C16** Eight traits: R reactivity, A aggression, S gregariousness, B body size, H horns, T season
  breadth, M milk capacity, W pigmentation. A ninth, L twinning (2026-11-05), acts only when
  `twinMax` > 0 (C26). Its alleles draw from a second random stream, and it is left out of the genome
  cost (C22) and of IBD (C21), so runs with `twinMax` 0 reproduce runs from before it existed (checked:
  0 of 200 years differ in H4 and H5, and in H5 with genome costs on). A tenth, C coat marking (2026-11-10, with Chris),
  is neutral: no mechanism reads it, only sireRule `'marked'`. It draws from a third stream and is likewise left out
  of the cost and of IBD.
- **C17** Diploid, 2 loci per trait (haploid, L = 4, 6 available); allele values in [0,1]; trait = mean
  of its alleles. **C18** Free recombination. **C19** Each inherited allele moves U(−0.04, +0.04) once
  per meiosis, clamped to [0, 1]. **C20** No expression noise; switchable links W ← R (pleioW) and A ← R (pleioA), both 0.
- **C21** Lineage ids ride with alleles (identity by descent), relabelled at year 400.
- **C22 Reproductive cost of the genome** (off by default since 2026-11-03, with Chris; 0.5 before). p = mean of
  the eight core expressed traits. Growth rate × (1 − `reproCostGrowth` × p) (later maturity). Each mating's
  conception chance × (1 − `reproCostFertility` × p_doe) × (1 − `reproCostFertility` × p_buck). Both are 0 by
  default, so p is computed but inert; at 0.5 they give the earlier cost, which applied however well fed the goat
  was. The gene-load delays (`loadFirstBreed`, `loadRecovery`, `loadGrowth`, 2026-11-03) are also 0. (There are no
  trait running costs.)

### 7.3 Energetics and growth (`Goat.graze`, `Goat.daily`)
- **C23 Grazing**, each day sub-tick, where the goat stands: 1/6 of a day's appetite `goatIntake` 5,760 kcal ×
  size^0.75 × a/(a + 0.05) (a = cell biomass above floor, as a fraction of K), kids scaled by age/weaning age,
  alarmed goats × 0.75; capped by reserve room plus a sub-tick's upkeep; × lean quality (C14).
- **C24 Upkeep**: `maintBase` 2,160 kcal × size^0.75 a day (body only). Reserve capacity `reserveMax` 216,000 kcal ×
  size. Starvation at E < −leanBuffer × size.
  - **Lean-tissue buffer** (`leanBuffer`, 2026-11-10; 12,000 by default from 2026-11-11, 0 before): E may fall to −leanBuffer × size before
    the goat dies, standing for lean tissue burned once fat is gone; a fed goat refills it before rebuilding fat.
    About 12,000 kcal per unit size puts death at roughly 70% of lean body weight for a 50 kg goat (Turner et
    al. 1993, a rule from their ungulate model, not a measurement), about 5-7 days of total fasting after the
    fat reserve. Below zero a goat weighs food above safety more (foraging need > 1), does not breed, and a
    mother gives no milk. Chris, 2026-11-10: death at the first day of an empty reserve made the starvation count
    a knife-edge on the ration, not a deficit.
- **C25 Growth** (defaults from 2026-11-18, with Chris; EXPLOG 2026-11-14 to 11-18): target = 0.6 + 0.8B, × `sexSize`
  1.7 for males (bezoar weights). While E > 0.4 capacity a goat grows at its curve's rate × (1 − `reproCostGrowth` × p)
  (× 1 by default, C22) size/day, at `growthCost` 216,000 kcal per unit size. `growthCurve` 'curved' (Chris
  2026-11-16): every goat advances one daily chunk, (1 − 0.15)/(`growYearsF` 3.75 × 360), along the line from birth
  size b to target T, bent by `curveExp` 2: ds = chunk × k × ((T − size)/(T − b))^((k − 1)/k), so growth slows to 0 at
  the target and a bigger target takes longer (Goat.curveRate). Birth size 0.15 × the sex-neutral target (males ×
  `maleBirthSize` 1.1). Other rules: 'linear' (+0.0035 a day; the default before 2026-11-18), 'vb' (von Bertalanffy),
  'ogm' (ontogenetic growth model). Growth continues while size < target, at any age. `adultAge` (720 days) sets only:
  the starting size of initial goats and immigrants (at their target from 720 days; C6, C53), the herd's adult mean
  size toward which the keep value credits growth (C57, `creditAge` 0 = adultAge), and which goats can be exchanged
  (C59a). Bucks mate and are kept as sires from `maleMinAge` 365 days (C31, C57); the juvenile hazard covers the first
  year (C41).
- **C26 Gestation**: birth 148 days after conception (nominal 150; an off-by-two in the counter, kept
  because it is immaterial), `gestationCost` 540 kcal/day, one kid. **Twins** (`twinMax` > 0; off by default, on in
  REF at 1): at conception a doe
  carries twins with chance twinMax × L (two meioses, one sire). Each twin is born at 0.8 × the single
  birth size (`twinBirthSize`), with reserves to match; twin gestation costs 2 × 0.8 = 1.6 × a single's,
  by litter birth mass. A doe's kid record (the opportunity cull's keep value) counts both.
  **Triplets** (`tripletMax` > 0, with Chris 2026-11-05; off by default, on in REF at 0.2): a twin pregnancy becomes
  triplets with chance tripletMax × max(0, 2L − 1), so only does with L above 0.5 have them. Each triplet is born at
  0.7 × the single birth size (`tripletBirthSize`); gestation costs 3 × 0.7 = 2.1 × a single's. Off, runs
  match the code before triplets exactly. At tripletMax 0.2, one-seed smoke runs gave 0.6–2% triplet
  litters (pre-batch-1 model, 2026-11-05; wild bezoar in Turkey: about 4%).
- **C27 Kids**: milk need `kidMilkNeed` 2,160 kcal/day at birth, falling to 0 at weaning (120 d); a kid takes
  min(need, mother's capacity − herders' take, mother's E). Herd orphans draw on the camp milk pool.
  Twins and triplets share one capacity equally: each kid takes up to (capacity − herders' take) / the
  litter's live unweaned kids (2026-11-05; before, the kid processed first, always the same one, drank
  its fill and the next got what was left, so second twins starved). A hunter who kills a nursing doe
  takes home one orphan.
- **C28 Lactation**: capacity `milkBase` 2,160 kcal × (0.5 + M) a day. She lactates (and is milked) while any kid
  of her litter is unweaned; before 2026-11-05 only while the first was, so a surviving second twin drank free
  (twin runs before commit a7c2895 carry that; twins off is unaffected). Milking (`milkIntensity`; off by default, on
  in REF at 0.5) takes that share of capacity each day before the kids drink. `milkCondition` (2026-11-12, with
  Chris; off by default, 0; on in REF at 0.5):
  capacity falls with her condition, full at a reserve of `milkCondition` × cap or more, in proportion below,
  none at an empty reserve, so kids and herders both get less from a thin doe (yield tracks body condition:
  Flores-Najera et al. 2021). **Cost** (`milkCost`): `'made'` (default from
  2026-11-05, with Chris) charges the doe for the milk made, what her kids drink (as they drink it) and
  what the herders take, so capacity is a ceiling and costs nothing unused; `'capacity'` charges the
  whole capacity every day, needed or not, as every run before this did (it reproduces them exactly).
  Under `'capacity'` M fell from 0.50 to about 0.18 in 1,600 years, wild and herd alike
  (results/milk2; pre-batch-1 model, 2026-11-05).
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
- **C32 Conception**: `matingConception` 0.7 × the doe's and the buck's fertility factors (C22; both 1 by default).
- **C33 Contests** (sequential assessment, after Enquist & Leimar 1983): up to 8 rounds, the first 2
  display. Each round costs each buck `displayCost` 180 kcal (display) or `contactCost` 540 kcal (contact). In
  contact rounds each risks
  death 0.01 × opponent's share of fighting ability × (1 + opponent's H). Fighting ability = size ×
  (1 + 0.5H). After each round each buck updates a noisy estimate (sd 0.25) of his relative strength and
  quits below 0.4 − 0.4(A − ½) + 0.2(R − ½) + 0.3(1 − E/capacity). If both quit in the same round, the
  one with the higher estimate stays. If neither quits, the stronger wins with probability equal to his
  share. If a fight kills both, the next live buck holds.
- **C34 Rut pull**: adult males foraging on their own (wild males, and herd males on a day their camp
  has no herder) add +0.5 to cells holding a doe in heat now.

### 7.5 Movement and behaviour (`Goat.step` and helpers)
- **C35 Alarm**, every sub-tick, for free goats (wild goats, loose run-offs C56a, and herd goats of a camp with no
  herder that day), unweaned kids following a live mother, and sheltered or kept goats (C39): chance R × fearOfWolves
  if a wolf's scent is on the cell (by day, where hungry wolves rest; at dawn, dusk and night, where goat-hunting
  wolves are now), or R × fearOfHumans if a hunter is within 1 cell now. Only free goats flee: 3 cells away from scent
  and hunters toward cliffs. An alarmed kid with a live mother steps toward her as usual (C37) and learns from her
  (C46); a sheltered or kept goat steps toward camp (C39). Herd goats with a herder react only to wolf scent and to
  the herder (C38), never to hunters; led captives are never alarmed (C40). An alarmed goat grazes at 0.75 that
  sub-tick.
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
- **C39 Kept at camp**: sheltered kids (< 30 d; H5, REF), tethered goats (H5, REF) and rut-guarded does walk to
  the camp cell (1 cell per sub-tick) and stay there, grazing it. Tethered and rut-guarded goats get
  fodder all year (C61); sheltered kids only in the lean season. None are stray-tested.
- **C40 Captives** walk with the hunter leading them. While led they count in the herd (and its load),
  are safe from wolves, are not stray-tested, culled or habituated, and a led doe in heat can still
  mate (led bucks cannot). A captured doe's wild kid stays wild but follows her into camp.

### 7.6 Mortality
- **C41 Background**: 0.03/y, + 0.15 in the first year, + 0.25 per year past 9. **C42** Other deaths:
  starvation (C24), fights (C33), wolves (C49), hunting (C52), culling (C57).
  **Small kids die more** (`juvSizeExp`, with Chris 2026-11-05): the first-year 0.15 is multiplied by
  (ref / size)^1.5, ref the size of a single with the same target born and grown at full rate to that age on the
  goat's growth rule (default 'curved': the curve of C25, Goat.curveSizeAt; 'linear': min(target, birth share ×
  target + 0.0035 age)). Twins (born 0.8) and triplets (0.7) start at 1.4× and 1.7×,
  and a kid short of milk falls further behind. At 0 the hazard is flat, as in every run before; that
  reproduces commit ec96ea3 exactly (H5 with twins, seed 1, 300 years: 0 of 300 years differ). Studies of
  managed goats give twins 1.0–1.3× (once 2.5×) and triplets about 2× singles' pre-weaning mortality
  (Angora 10/13/22%; Pakistani desert goats 7.3/9.6/16.7%; Borana 30/30/57%). One-seed smoke, years
  201–300 (twins, triplets on; pre-batch-1 model, 2026-11-05): wild twin deaths per kid 1.06× singles at 0, 1.29× at 1, 1.34× at 1.5,
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
  stops when fed or chased off (C50). Detection of each goat in its 3×3: 0.5 (1 − 0.5W)/(1 + 0.15 (goats in the 3×3
  around the goat − 1)). A detected goat spots the wolf with chance
  R × fearOfWolves (alarmed). The target is drawn weighted by kill chance: 0.15; × 3 for kids; older goats
  defend by 0.3 (size / s − 0.6)/0.8 + 0.2A + 0.2H (males), s the sex's size multiplier (1, or `sexSize` 1.7
  for males: size within the sex's own range), clamped to [0, 0.9]; × (1 − 0.6 × flight), flight = 1 alarmed, 0.5 warned (each other
  weaned goat in the 3×3 spots it with chance 0.6 R fearOfWolves), else 0.5 min(1, R fearOfWolves);
  × 0.15 on cliffs.
- **C50 Herd protection**: a herd goat on any camp's cell × (1 − `penProtection` 0.8) = 0.2 if its herd is penned
  (`penning` 1, the default) or it is sheltered or kept at camp; within 1 cell of its herder × (1 − `herderProtection`)
  (0 by default: off); with guarding (off by default; on in H5 and REF), any herd goat × 0.3 more, and first a 0.2
  chance the guard kills the wolf (replaced by an immigrant at the upland edge, with a fresh memory). **Herder chase**
  (`herderChase` 1, `herderChaseDist` 5; with Chris 2026-11-01, on by default from then): after a wolf strikes at a
  herd goat within 1 cell of its herder, kill or miss (and the wolf not killed by a guard), the herder drives it off
  with chance herderChase: its bout ends until the next dusk, it leaves no scent for the rest of the bout, and it is
  pushed 5 cells straight away from the herder. Its memory still updates at dawn.

### 7.9 Humans
- **C51 Roles**, each dawn: each camp has `humansPerCamp` 5 people (fixed; 0 = no humans, H0); a camp with a herd
  sends one herder; each other human hunts (0.3), forages (0.3) or stays in camp (0.4). Fixed shares (§10, G5).
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
    wild range. From `humansAt`, at each year's start, that share of the wild goats a year (360 days) or older (not
    pregnant, no kids at foot, not being led; stochastic rounding) is chosen at random and swapped in place for an
    immigrant drawn from `immigrationPool` (genomes and learned fears of adult hunted wild goats, sampled from
    hunted-only runs by tools/pool.mjs): same place, sex and age; a new id and fresh lineage ids; no herd ancestry; size
    = its own target (from its own genes) if 720 days or older (`adultAge`), else the replaced goat's size capped at its
    own target. Headless only (load.mjs reads the pool). No random draws when off.
- **C54 Foraging**: a forager claims, for the day, the unclaimed non-camp cell within `forageRange` 6 cells of camp
  that will yield most: min(room in the load, `forageCut` 14,400 kcal × sub-ticks left after walking there, what the
  cell holds), so gatherers spread out and trade distance against lushness; it cuts 14,400 kcal per sub-tick (removed
  from the cell) up to a load of `forageLoad` 36,000 kcal (about 60 kg of fresh browse, two headloads; 72,000 until
  2026-10-31) and re-chooses when a spot is spent; loads are stored at camp each night. The fodder store keeps by
  shelf life (`storeWindows` 1, the default from 2026-10-31): each night's cut is a dated batch, fed soonest to expire
  first and lost `fodderDays` 270 days after it was stored (`fodderSpoil`, 0.5%/day, applies only with storeWindows
  0). Without the economy, foragers cut vegetation from year 300; the cutting is a real grazing cost to wild goats near
  camps. (In the economy, C68.)

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
  (~0.2% of penned goat-nights; pre-batch-1 model, 2026-10-21).
- **C56a Run-offs** (`refetchRunOffs`; 2 by default, with Chris 2026-10-24): a goat spooked by the
  herder (C38) beyond 2 cells is *loose*: still the herd's, but moving as a wild goat (C35–C36, its
  gregariousness may bring it back). It rejoins if it comes within 2 cells of the herd's leader. Each
  keeper (the herder, or in the economy each keeper, C71) makes at most one attempt per day or dusk
  sub-tick on the nearest loose goat within 6 cells that has been loose ≥ 2 sub-ticks (`chaseDelay`):
  the approach test over the distance; lost if it bolts, else back with him. Still loose at the end of
  dusk: the night stray test (C56). Mode 0: run-offs drift back on their own; mode 1: chased at once.
  Observed fates (pre-batch-1 model, 2026-10-24): ~20% rejoin, 53–59% fetched back, 15–24% lost on the chase.
- **C57 Culling.** Two paths, chosen by `econCull` and `cullRule`.
  - **The threshold cull** (the batch-1 default, 2026-11-18, v0.1.0, with Chris; `econCull` 1 with `cullRule`
    'opportunity', as in H3–H6 and REF): there is no quota, and offtake is an outcome. Every `cullEvery` (30) days the
    herder slaughters every herd goat whose keep value (below) plus judgement noise N(0, `cullNoise` 0.05) is below
    `cullThreshold` 0 (exp002). The keep value charges feed and meat at risk by the herd's size for the goat's sex and
    age (`cullSizeNeutral` 'age') at `feedCost` 0.085 (exp003: males dead before 2.5 y in the Ganj Dareh band for
    0.075–0.10; report the range, §9). `surplusCull` and `winterCull` are refused with it (an error: they belong to the
    quota), and `cullFloor` does not apply; the optional hard cap `herdTarget` (off) still does.
  - **The quota** (any `cullRule` other than 'opportunity', and 'opportunity' with `econCull` 0): each night a camp
    slaughters at `offtakeRate` of its herd per year (0.1 by default; stochastic rounding of the night's share), chosen
    in the cull rule's order; then anything above `herdTarget` (off). `cullFloor` (2026-11-11, with Chris; 0 = off): the
    offtake never takes a camp's herd below that many goats (the night's draw is still made, so off reproduces earlier
    runs); other losses can. `surplusCull` (2026-11-12, with Chris; 0 = off): before the offtake, each night the herder
    slaughters every weaned herd male beyond the camp's sires (C64's chosen) and `insuranceBucks` spares (2; the oldest
    other weaned males). These culls are credited against the offtake draws of the same year, so the year's offtake is
    the larger of the two; `cullFloor` does not stop them. Records `surplusBucks` a year. (Before it, the offtake count
    was a fixed share of the herd whatever its make-up, and adult bucks built up to 1.0-5.6 per doe in one isolated
    camp: EXPLOG 2026-11-12 diagnostic.) `winterCull` (2026-11-12, with Chris; 0 = off): on the first lean day, after
    the surplus cull, the herder budgets a full ration (`provision` × size^0.75 a day) through the lean days ahead for
    each breeding-age doe and each goat under a year (bucks and dry yearlings winter on grazing), and while the camp's
    fodder store falls short slaughters among those goats in the cull rule's order, never below `cullFloor`; credited
    against the year's offtake like the surplus cull. Records `winterCulled` a year. (The first form, b9ec5e5,
    budgeted every goat and held the open reference herd at about 60.) The batch-1 random-cull baseline rate is 0.13
    (§7.11a).
  - **Cull rules.** *random* (H2, and the batch-1 baseline RAND): no preference. *opportunity* (H3–H6, REF): the keep
    value, in meat (size) units, from what a herder can see (age, sex, size, kidding record, behaviour; never genes),
    lowest first. Over the next year (`keepFrame` 'year', the default, 2026-11-18; 'horizon' instead sums growth,
    feed, meat at risk and the sire's share over `keepHorizon` years, each year discounted by survival):
    + next year's growth on the goat's curve toward the size the herder expects (`growthCredit` 'herd', the default:
    the herd's mean size of its sex among goats of 720 days or older, `creditAge` 0 = `adultAge`; Chris 2026-11-18, a
    learned expectation, since a herder cannot see a target; this credit is what shrinks herd body size, EXPLOG
    crossover 2026-11-17. Options: 'own' the goat's own target, 'cull' the camp's running mean size at slaughter by
    sex, 'max' the herd's largest goat of the sex)
    + for does under 9: `kidValue` 0.3 × expected kidding over the next 3 years (`keepHorizon`, ≈ age at first
    kidding; each year × the chance she lives to it, 0.97 per year; the first year at half for does under 480 d).
    Each year's rate is her own record weighted by its length (years since 480 d / (years + `recordWeight` 1))
    blended with the camp's record for does of that age class (`ageClasses` 10, one per year of age, the last open):
    the camp's mean over all ages until that class holds more than one doe-year, and `priorKidRate` 0.8 before the
    camp has any record. Only kids born in the herd count
    + for the sires (the `keepSires` 2 oldest bucks of 365 days or more, or those `sireRule` chose): 0.3 × herd rate ×
    breeding does (480 days or older) per sire; the `keepHeirs` (1) oldest other weaned buck, held back as a
    replacement, at half that
    − `feedCost` 0.085 × size^0.75 (a year's feed)
    − annual death hazard × size (meat at risk; hazard 0.03, + 0.15 under a year, + 0.25 per year past 9: C41
    without the small-kid factor)
    − (H6) `flightCost` 1.0 × R × fearOfHumans
    + the sex preference terms (below)
    + (off) `lastBreederValue` 0 for the herd's last `lastBreeders` 1 breeding doe or buck
    + N(0, 0.05).
    A herd with no adult of a sex (age ≥ `creditAge`, default adultAge) takes adult size 1 for that sex in the growth
    credit and the size references.
    The size in feed and meat at risk is set by `cullSizeNeutral`: 'age' (the batch-1 default) = the herd's mean size
    for the goat's sex and age class in whole years, classes 0–4 and an open 5+ (`AGE_REF` 6, a constant in
    world.js); an empty class takes the class below it, or from age 2 the herd's adult mean for the sex if that is
    larger, and an empty class 0 takes class 1 or else the adult mean. 'sex' = the sex's size multiplier (1, or
    sexSize for bucks); 1 = 1 per head; 0 = the goat's own size.
  - **Milk in the keep value** (`milkValue`, off; with Chris 2026-11-09): a doe's expected milk to the camp
    over the same 3 years, built like her kidding (her own record of milk taken per year since breeding
    age, blended with the camp's milk per doe-year for her age class, survival-discounted), × milkValue /
    36,000 kcal per meat unit (1 = milk worth its food energy as meat). At 50% milking a doe gives about
    1,100 kcal a nursing day, so at 1 her milk outweighs her kids several times.
  - **Each sex's own cull rule** (`buckCull`, `doeCull`, both off; with Chris 2026-11-10). Under the quota: the cull
    rule above still sets how many of each sex are eaten; within the places it gave a sex, that sex's rule picks
    which go. *random*; *calm* (most run-offs seen per year watched first); *large* (smallest for its sex and age in
    years first); *homebred* (fewest generations of camp-born dams, up to `herdMemory`, first: captives first); bucks
    only, *youngMales* (0.5-2.5 y, then older, then kids). A buck rule never takes the herder's sires (as `sireRule`
    picks them).
    Under the threshold cull (`econCull` 1, rule *opportunity*; with Chris 2026-11-20, commit 1468afe) there is no
    count to work within, so a sex's rule is a term of the keep value instead: each goat of that sex in the herd is
    ranked by the rule (ties share their mean rank), the rank is centered to +0.5 for the most preferred and -0.5 for
    the least, and it is multiplied by `buckPrefValue` / `doePrefValue` (meat units, 0 by default; a weaned kid is
    worth 0.3). A preferred goat crosses the threshold later. *random* is a fixed per-goat liking that tracks no trait
    (the control); *youngMales* is not offered, since the keep value already culls grown non-sire bucks. A rule
    without a value above 0, or a value without a rule or under the quota cull, is an error.
  - **Herder-culture rules** (with Chris 2026-11-20; all off by default; tested in exp011 against spooking at a fixed
    load with no loss):
    - `runOffLoss` (1): 0 = a run-off or night stray is always brought back (no searchRange limit, no approach test), so
      spooking removes no goat; goats still bolt and the herder still sees it (`seen`).
    - Self-maintaining herd: a camp's herd holding at least `selfDoes` home-born breeding does (gsc ≥ 1, age ≥
      femaleMinAge), counted each night (`World.selfMaint`); `selfDoes` 0 = never.
    - `larder` (threshold cull): once the herd is self-maintaining, a captive that has not yet bred in the herd (gsc 0,
      `capBred` not set) is kept as meat: no kid, milk or sire credit in its keep value. Before that every goat counts
      as herd, which lets herds found from captives.
    - `captureTaper`: once a camp's herd is self-maintaining, its hunters take no goat alive (live capture and orphans).
    - `nuisanceCost` (threshold cull): the keep value is charged this × the goat's observed run-offs per year watched
      (seen[0] / (years watched + 1)) × its expected years ahead: the herder's chasing labour, judged from behaviour only.
- **C58 Habituation**: every kept herd goat each night, fearOfHumans → 0.05 at rate 0.1 inside the
  socialisation window (age < 180 (1 − R) d), 0.02 after.
- **C59a Exchange between camps** (`exchangeN`, 0; with Chris 2026-11-10): at each year's end every camp with a herd
  gives `exchangeN` adults, at random, to another camp with a herd, at random: never its sires, a tethered, guarded or
  led goat, or a doe with a kid at foot. The receiver starts watching it afresh; its lineage goes with it.
- **C59 Herd size** is not capped: it emerges from captures, births, losses, offtake, and the herder's
  load (C38), which raises spooking and so straying in proportion to herd size above 5.
- **C60 Milking** (`milkIntensity`; off by default and in every condition of §7.11; on in REF at 0.5): herders take a share of capacity into a camp pool that halves
  nightly and feeds herd orphans. Each doe's total taken is her milk record (C57, C31).
- **C61 Provisioning** (`provision`; 0 by default, 2,160 in H5 and REF): herd goats get up to `provision` kcal ×
  size^0.75 a day **from the camp fodder store** in the lean season (kept-at-camp goats all year), limited by what the
  store holds: each goat takes its want (up to that ration and its reserve's room) in population order until the
  store is empty. `fodderRation` (2026-11-12, with Chris; off by default, 0; on in REF, 1): in the lean season each camp's daily budget is its store
  over the lean days left (today included), so the store lasts the season; pregnant or nursing does and goats
  under a year are fed first, then the rest, each class in proportion to its goats' wants (no random draws).
- **C62 Kid shelter** (H5, REF): herd kids under 30 d stay at camp; **C63 Tethering** (H5, REF): a herd goat
  with R × fearOfHumans ≥ 0.35 stays at camp until it habituates below that; **C64 Buck management**
  (H5, REF): C31; **C65 Guarding** (H5, REF): C50; **C66 Rut guarding** (off): a doe in heat stays at camp with
  chance `rutGuard`, and with buck management so do her herd's sires.

### 7.11 Conditions (`tools/conditions.json`)

| | Humans | Herding | Cull | Pen | Husbandry |
|---|---|---|---|---|---|
| H0 | none | — | — | — | — |
| H1 | hunt, forage from 300 | never | — | — | — |
| H2 | hunt, forage | from 400 | random | no | — |
| H3 | hunt, forage | from 400 | opportunity | no | — |
| H4 | hunt, forage | from 400 | opportunity | yes | — |
| H5 | hunt, forage | from 400 | opportunity | yes | guard, fodder 2,160 kcal × size^0.75 (from store), kid shelter, buck management, tethering |
| H6 | hunt, forage | from 400 | opportunity + flightiness cost 1.0 | yes | — |

conditions.json sets `offtakeRate` 0.1 in H2–H6. At the batch-1 defaults (`econCull` 1) H3–H6 run the threshold
cull (C57) and that rate is unused; H2 (*random*) runs the quota at 0.1, the legacy condition value. (Pre-batch-1
model, 2026-10-21: 10%/y was the highest rate tested at which unpenned H3 herds persist: 57 → 114 goats with the
3-year horizon, ~10 at 20%; H5 held ~80 at 20% and collapsed at 30%.) No herd cap; herd size is otherwise limited by
C59.

### 7.11a The reference culture (REF)

The batch-1 experiments (the exp004 anchor on; the same husbandry was called R15 up to exp004, after the 0.15 arm of
an offtake-rate sweep) run the reference culture, REF: `herdingAt`=400
`cullRule`=opportunity `penning`=1 `guarding`=1 `provision`=2160 `kidShelter`=1 `buckManagement`=1 `tetherNew`=1
`milkIntensity`=0.5 `twinMax`=1 `tripletMax`=0.2 `leanBuffer`=12000 `herdRange`=8 `herdTravel`=2 `surplusCull`=0
`fodderRation`=1 `milkCondition`=0.5 `winterCull`=0 `exchangeN`=0, defaults otherwise (the job lists also pass
`offtakeRate`=0.15, unused under the threshold cull). Of these, twelve override a default: herdingAt (1e9, never),
cullRule ('random'), guarding (0), provision (0), kidShelter (0), buckManagement (0), tetherNew (0), milkIntensity
(0), twinMax (0), tripletMax (0), fodderRation (0) and milkCondition (0). The rest restate defaults: penning,
leanBuffer, herdRange, herdTravel, surplusCull, winterCull and exchangeN. REF is H5 plus milking, twins and triplets,
rationed fodder and milk by condition. With cullRule 'opportunity' and the default `econCull` 1, REF culls by the
threshold (C57).

The random-cull baseline (RAND, exp005 on) is REF with `cullRule`=random `offtakeRate`=0.13: the quota at the threshold
cull's realized offtake in the exp004 anchor (37.8 goats culled a year from a herd of 286). conditions.json's H2
`offtakeRate` 0.1 is the legacy condition value.

### 7.12 The camp economy (`economy` = 1; notes/human-economy.md; with Chris, 2026-10-23 to 10-25)

Off by default (`economy` 0), and parked since 2026-10-29: human behaviour is the controlled variable, set per
condition. Replaces fixed human policies (C51 shares, C53 capture by hunters, C57 offtakeRate, C61 provisioning
by switch, C65 global guarding). Human numbers stay fixed (`humansPerCamp`, 5 by default; the economy runs of
2026-10-24 on used 10); the camp optimises income, and consumption is a sink.
- **C67 Currency and stores** (kcal, for people and goats alike; human food was in fu of 900 kcal until 2026-10-28):
  meat, human plant food, slop (spoiled plant food, goat fodder), cut fodder, and the herd (stock value = `meatYield`
  36,000 kcal × size per goat). Stores keep by shelf life (`storeWindows` 1, the default; with Chris 2026-10-28):
  each is a queue of dated batches, eaten soonest to expire first. Fresh meat keeps `freshDays` 3, then is dried,
  keeping `dryValue` 0.7 of its food, and dried meat keeps `dryDays` 270, then is lost; plant food keeps `plantDays`
  135, then becomes slop; slop keeps `slopDays` 14, then goes on the dump heap (C75); cut fodder keeps `fodderDays`
  270, then is lost. With storeWindows 0 the stores decay at rates instead: meat `meatDecay` 5% of its nutrition a
  day, plant food `plantSpoil` 0.3%/day, fodder and slop `fodderSpoil` 0.5%/day.
- **C68 Human plant food** (seeds, tubers, fruit; goats eat it only as crop damage, C77):
  `foodPatches` 120 patches, centres drawn in proportion to wetness, radius 2, fill 0.5; site capacity
  `foodSiteK` 720,000 kcal × lognormal(0.5); each year each patch draws a yield factor, lognormal(0.6)
  (masting), and the sites themselves are redrawn each year from the same distribution (`foodReplace` 1, with Chris
  2026-10-25; none persist). Food ripens across the fruiting window (day 150 ± 45, linear to the year's capacity) and
  rots 3%/day outside it. Gatherers harvest it (C54 choice rule on the food field; `foodCut` 3,600 kcal a sub-tick, up
  to a load of `foodLoad` 18,000 kcal) into the plant store.
- **C69 The sink**, each night: demand = people × `needPerPerson` 2,250 kcal + `groupSink` (0; to be used to
  drive offtake once herds are robust). With storeWindows (the default) people eat fresh meat, dried meat and plant
  food (`plantValue` 1) soonest to expire first (storeWindows 0: meat, then plant food); then, while short, the camp
  slaughters herd goats in keep-value order (C57 opportunity rule); unmet demand has no consequence. Before eating,
  with `econCull` 1 (the default) the threshold cull (C57) also runs here every `cullEvery` days, whether or not the
  camp is short. Offtake is therefore an outcome.
- **C70 Role choice** (after Marriott & Gershenson 2011): at dawn each person picks gather, hunt or
  herd with probability proportional to the camp's decaying estimate (`returnTau` 30 d) of that role's
  return per labour-day, after a random choice with chance `roleFloor` 0.1; an untried role is valued
  at the best known. Returns per labour-day: gather = plant food delivered; hunt = meat delivered
  (`meatYield` × size; hunters only hunt); herd = (offtake + Δ herd stock value + storage credit) ÷ herders: what is
  taken, plus the change in what is saved, plus the spoilage that storing food alive avoids. The storage credit is
  `storeCredit` 0.0011 × stock with storeWindows (dried meat loses 30% over 270 days), `meatDecay` × stock without.
  Herding is available once herding is allowed, herd or not.
- **C71 Herding tasks** (camp-level priority): the first herder keeps (leads to pasture, C55; keeps
  the herd together; chases run-offs, C56a; night strays, C56; herder load counts keepers). Each
  further herder takes the task whose decaying signal ÷ (1 + those already on it) is largest, or a
  random task with chance `roleFloor`. Signals, kcal of goats at risk per day (`meatYield` × size): keep, herd goats
  run off or straying; guard, herd goats attacked by wolves; feed, herd goats hungry (reserve < 40%); capture, kcal
  captured per capturer-day. A camp with no herd sends its whole crew to capture.
- **C72 Guards** protect herd goats within 1 cell of themselves (C50 factors), walking with the herd.
- **C73 Feeders** cut vegetation as fodder (C54 rule on the grass), stored at camp; herd goats are fed
  up to `provision` kcal × size^0.75 a day all year (only when provision > 0) from slop first, then cut fodder.
- **C74 Capturers** walk out like hunters (C52) and only take goats alive (C53 approach test).
- **C75 Spoilage cascade** (with Chris, 2026-10-25): spoiled plant food becomes slop (`slopValue` 4 kcal of goat
  fodder per kcal of plant food, which keeps the old 1 fu → 1 fu); spoiling slop is thrown on the dump heap; each
  kcal on the heap seeds a new food site within `heapRadius` 2 of camp with chance `heapSeed` (its own patch and
  masting): near-camp gardens from waste ("dump-heap" origin of cultivation). `heapSeed` is 0 (off; backed out
  2026-10-25), so the heap seeds nothing.
- **C76 Land competition**: a food-site cell keeps only `siteGrass` of its vegetation capacity; 1 by default (off).
- **C77 Crop damage** (`cropDamage`, 0 = off by default): a goat (herd or wild) on a food site eats the standing plant food
  first, and counts it as forage when choosing where to move (it seeks crops out).

---

## 8. Observation

Every `reportingPeriod` days (30; the census, `samples`): population, kids, sexes, vegetation. Every `histPeriod`
years (1): genotype histograms per trait (all goats, `hist`, and the herded subset, `histHerd`). Every year (the year
row, `years`, kept every `recordEvery` years): trait means (all goats, and the herded subset); learned fear; births, deaths by cause; kill-off by cause, sex
and age, and the herd's own kill-off; first kidding; adult mortality; captures, escapes, culls, milk,
fodder fed and foraged, wolves killed; herd and wild IBD; sires per camp-year; wild-sired share of herd
births; R of the year's captives; generations since capture. Unweaned kids (`kidLife`, from 2026-11-05),
by wild or herd and litter size: kid-days; energy wanted from milk, drunk from the mother, from the camp
milk pool, grazed, and fed as fodder; at weaning, size, size over target, and condition (E/capacity),
and how many had lost their mother; kid deaths with the mother dead. Herd conceptions by origin (from 2026-11-10; does already
in the herd, so a doe captured pregnant is not counted): dam captured or camp-born, by sire wild, captured,
camp-born, or another camp's. From 2026-11-20 (output only; runs identical): wild does' conceptions by a wild or a
herd sire (`wildConc`, the herd-to-wild route through herd bucks mating wild does, which nothing in the mating rule
prevents); captures by sex (`capIn`) and captives that conceive or sire while still in the herd (`capBred`; capBred /
capIn over a window is a ratio of events, first breedings by captives per capture, close to but not the share of a
cohort of captives that ever breed: a capture late in a window may breed in the next, and a recapture counts as a
new entry; the cohort share would need per-captive tracking). Also output only (2026-11-20): herd goats dying while
loose (`looseDeaths`), camp-days a herd is self-maintaining (`selfMaintDays`, when `selfDoes` > 0), and parents' ages
at each litter (`parentAge`, wild / herd: summed dam age, summed sire age at birth, litters), for generation time; and
viability (`cohortBirth`, `cohortBreed`: summed genotype per trait and count, wild / herd × female / male, of each kid at
birth and of each goat at its first breeding, a doe's first kidding or a buck's first siring; birth minus first
breeding is the selection between).
Realized selection differentials
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

**Recording periods and thinning** (output only: the run is the same whatever they are set to). `reportingPeriod`
(30 days) sets the census; `histPeriod` (1 year) the gene histograms, recorded at the end of years N−1, 2N−1, …
(`histYears` lists each row's year; `histDepth` pools max(10, N) years per record); `recordEvery` (1; 2026-11-19,
commit cda20ea) keeps the year row every N years, at the end of years N−1, 2N−1, …, each row that one year's record
(totals are per year, not summed over N). Diagnostics are named switches, all on (1) by default so runs stay
comparable with saved ones (2026-11-13): `logWolfAtk` (wolf attacks and kills by herd or wild, phase, terrain, camp,
…), `logKidLife` (the unweaned-kid counters above), `logKilloff` (deaths by cause, sex and age), `logHerdKilloff`
(herd deaths by sex and age), `logKidDeathCause` (unweaned deaths by cause and litter size), `logHistDepth`
(`histDepth`). Experiment and scratch runs (tools/runyears.mjs `--exp` or `--scratch`) use the LEAN profile: logKilloff,
logWolfAtk, logKidLife, logKidDeathCause and logHistDepth 0 (logHerdKilloff stays 1), histPeriod 5, reportingPeriod
360. Every period is then multiplied by k = ceil(years / 1600): recordEvery k, histPeriod 5k, reportingPeriod 360k.
A 1600-year run has k = 1; a 4000-year run k = 3 (year rows every 3rd year, histograms every 15 years, census every
1,080 days), about the same size in Mongo. Any key=value on the command line overrides these, and they are saved in
the run's parameters like every other setting.

## 9. Calibration status (batch 1, 2026-11-18)

Most numbers in §7 are calibration choices, not data; literature-backed ones: gestation, weaning, rut timing, spring
kidding, oestrous cycle length, first kidding, that R is heritable (the model's heritability of 1, with no
expression noise, is a choice, not a datum), bezoar sex sizes, age at first kidding (about 3 y, Schaller & Laurie
1974), and the Ganj Dareh targets. Batch 1 (v0.1.0) was calibrated in three steps (EXPLOG 2026-11-17 to exp004):
- **Growth pace** (EXPLOG 2026-11-17, wild growth pace and breeding threshold; humansPerCamp 0, 2 seeds × 600 y,
  years 501–600): `growYearsF` set so wild does reach 95% of adult size at about 5 years (Alpine ibex females 4.5–5.5
  y as the stand-in; no bezoar growth curve found). With the curve and `breedSizeFrac` 0.8 that gave 4.0, and wild
  first kidding at about 1,460 days; at `breedSizeFrac` 0.65 (a calibration choice, near the recommended weight for a
  domestic doe's first breeding, about 60% of mature weight, MSD Veterinary Manual; measured puberty comes earlier,
  about 40% in goats, MLA, and no caprine study of the puberty weight fraction was found: paper/literature.md §10) it gave 3.75 (interpolated t95 5.0 y), with wild first kidding at about 1,096 days
  (interpolated). The field comparison (literature helper, 2026-11-20, paper/literature.md): bezoar yearlings join
  the rut but few conceive, and does usually first give birth at about 3 years (Schaller & Laurie 1974, p. 117, one
  arid population in Sind); maturity at 2–3 years (HMW 2011). The earlier rationale "most bezoar females first mate
  at 1–2 y" holds only in that weak sense and is withdrawn as a calibration target. `sexSize` 1.7 and `maleBirthSize` 1.1 are bezoar weights.
- **feedCost** (exp003, REF with the threshold cull and age-sized charges, 4 seeds × 1600 y, years 1501–1600): swept
  0.05–0.15 against the Ganj Dareh male kill-off (males dead before 2.5 y, slaughter, 0.60–0.70): 0.57, 0.61, 0.72,
  0.85, 0.85 at 0.05, 0.075, 0.10, 0.125, 0.15. The band is reached between 0.075 and 0.10; the default is 0.085 (Chris,
  2026-11-18: report the range 0.075–0.10, not a fit). Out-of-sample Ganj Dareh checks at 0.075, 0 of 3 in band: aged
  4 or older 0.13 of slaughter (about 0.20); does dead at 2.5 y or older 0.47 of all causes (0.60–0.70); does per buck
  0.92 of all causes (1.11–1.86). `cullThreshold` 0 is exp002's.
- **Anchor** (exp004, REF at the v0.1.0 defaults, 4 seeds × 1600 y, years 1501–1600): herd 286 (per seed 278–295),
  herd starvation 52.7 a year, births 147.7, culled 37.8. Herd − wild genotype gaps: R −0.63, A −0.10, S +0.08, B −0.25
  (per seed −0.12 to −0.41), H −0.14, T +0.37, M −0.12, W −0.04, L +0.21, C +0.00. Herd B 0.624, wild B 0.873. Median
  first kidding: herd 915 days, wild 1,250. Slaughter: males dead before 2.5 y 0.69, aged 4 or older 0.14; all causes:
  males dead before 2.5 y 0.80, aged 4 or older 0.11, does dead at 2.5 y or older 0.45; Ganj Dareh targets met 1 of 4
  (slaughter), 0 of 4 (all causes). Herd starvation at carrying capacity is accepted as an artefact of food-limited
  growth, with no data to calibrate it against (Chris, 2026-11-18).

*Pre-batch-1 model, 2026-10-21:* wild type (H0, 10 seeds × 500 y, `results/stage2v4`): 10/10 persist (252–469 goats);
88% of goats in herds of ≥ 5; first kidding 2.81 y; adult mortality 0.23/y; R 0.64, A 0.74, S 0.39, B 0.89, H 0.80,
T 0.44, M 0.18, W 0.81.

---

## 10. Open items

- **G5. Human time is fixed shares.** Balancing hunting against foraging by payout needs a common
  currency (meat vs fodder), i.e. a human metabolism; deferred.
- **G6. Herders see the best pasture within range** (C55; kept by choice) and **wolves are replaced at
  the edge** (C50; kept by choice); **hunters return home instantly** (C52; kept by choice).
- **G7. No stress cost of R at density** (unchanged).
- **G8. B sits near the top of its range** in the wild type (0.89, pre-batch-1 model, 2026-10-21; wild B 0.873 in
  the batch-1 anchor, exp004), so it can fall under domestication but has little room above.
- **G9. The share of herd goats living past 4 years.** Pre-batch-1 model (2026-10-21, quota cull): too many (0.33–0.37
  of herd deaths ≥ 1 y vs Ganj Dareh ~0.20) once the keep horizon fixed the female side. Batch 1 (exp004, threshold
  cull): too few, aged 4 or older 0.14 of the slaughtered and 0.11 of herd deaths of all causes (exp003/exp004
  tables, years 1501–1600).
  - *Pre-batch-1 (too many):* does kept their worth to age 9 because nothing in the model makes an older doe kid
    less (no reproductive senescence), so a herder had no observed reason to cull her early. The candidate fix then
    was age-declining fertility. Under batch 1 that fix would make the miss worse.
  - *Batch 1 (too few):* not yet diagnosed. To check: which goats die before 4 and of what (cull, wolves, starvation),
    by sex, against the keep value's age terms (hazard rising past 9, the age-class size references).
- **G10. A wolf that rarely hunts goats rarely relearns them** (C48 updates its memory only on
  goat-hunting nights; at s = 0.05 it hunts goats 2.7% of nights). Whether this matters depends on how
  often wolf memories fall that low; not measured.
- **G11. Dusk is as long as the herd range** (4 sub-ticks, 4 cells), so a goat at the edge of a penned
  herd's range may not reach camp by nightfall and is stray-tested (~0.2% of penned goat-nights; pre-batch-1 model,
  2026-10-21).
  From 2026-11-11 the default walk home (4 sub-ticks × herdTravel 2) again equals the range (8); with
  herdTravel 1, ranges 6 and 8 lost every herd (EXPLOG 2026-11-11, herder range).
- **G12. Penned herds without husbandry stay small** (pre-batch-1 model, 2026-10-22, quota cull at 10%, herdRange 4,
  herdTravel 1; H4, H6: ~22 goats over 3 camps vs ~90–115
  unpenned), at 2–13 per camp, single herds lost and refounded (generations since capture 3.9 vs 21–33).
  Doe condition, pregnancy share and heats match unpenned herds, and it is not offtake. *Found
  2026-10-22 (`tools/kidfate.mjs`, 2 seeds, years 520–560):* food. H4 + lean-season fodder only
  (provision 0.6) holds 87–88 goats (vs 22), doe share 0.37 → 0.50, births per doe-year 0.70 → 0.87.
  A penned herd can only graze what it can reach and walk back from in a day (6 day sub-ticks, range
  4); widening the range to 8 shrinks herds to 8–10 and raises starvation (0.07 → 0.11 per goat-year),
  because the herd spends the day walking. Unpenned herds escape this by moving on and sleeping out.
  Kid survival (0.90–0.93) is the same in all.
- **G13. The genetic R signal was weak** in the pre-batch-1 model (2026-10-21 to 10-24: herded − wild −0.02 to
  −0.06; captives ≈ herd; every figure below the next sentence is from that model). In the batch-1 anchor (exp004,
  REF) the R gap is −0.63; G15 for what it rests on. *Diagnosed 2026-10-21:* not habituation. Wild R itself rises under hunting (0.62 → ~0.86 by year 400), and herds
  start from that. Herd R fell to ~0.3 before the cold check (H5, no culling) because the herder also
  spooked goats at dusk. A goat bolting on the walk home is still out at the nightly stray test and is
  lost by the approach test (R × fear), so ~22 reactive goats a year were filtered out. Single-fix
  bisection on 7b7e356 (H5, 2 seeds × 600 y): only the dusk-spook fix moves herd R (0.50 → 0.77;
  escapes 22 → 6/y). With dusk spooking back at the same daily rate (`spookAtDusk 1`, 3 seeds): herd R
  0.67–0.72, escapes ~21/y, vs 0.78–0.85 and ~6/y without. So the filter's strength depends on the
  gap between a spook and the once-a-night stray test: spooks by day are undone by regrouping before
  dusk. A more local alternative: the herder deals with a stray when it strays (any sub-tick), not
  once at night. *Built as `refetchRunOffs` mode 1 (the default has been mode 2, loose run-offs, C56a, since
  2026-10-24):* a goat spooked beyond keepRadius is gone after at once by the approach test. At herderAlarm 0.05 herds collapse (H3 113 →
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
  (Pre-batch-1 model.) Chris (2026-11-06): move on for now; this could be investigated. To do: several seeds per strength,
  and a target for wild twinning (feral goats on Macauley Island: 39% of adult does' pregnancies twins).
- **G15. Batch 1's R gap and the herd-load rule** (the reviewer's design review, 2026-11-20, finding 1). A herded
  goat's spook chance is `herderAlarm` × R × fearOfHumans × herdLoad (animals.js:363), and herdLoad = max(`minLoad`
  0.25, herd goats / (`herdPerHerder` 20 × herders)) (world.js:181-183). The selection on R therefore grows with
  herd size by rule, and in every batch-1 herd that grew the R gap is −0.55 to −0.68 (exp005/exp006). Whether the R
  gap follows herd size or the spook load, and how much of it the rule writes in, is being tested in exp007 (LOADLO,
  LOADHI). Until then R is not evidence of isolation and establishment is defined by herd size.
- **G16. Batch 1's B gap and the herder's reference size** (design review finding 4). B depends on which reference
  size the keep value credits growth toward (`growthCredit`: own, herd, cull, max; +0.03 to −0.67 across the
  options, EXPLOG 2026-11-17/18), and 'herd' was adopted after those outcomes were seen. In REF the B gap still moves
  late and by large per-seed steps, and it has not settled by year 3200 (exp005/exp006 settling tables). Report B
  conditional on the reference, with the other options beside it (batch-1 plan block B5).

## 11. Non-local and stand-in steps remaining

Still non-local by choice: herder pasture scan, wolf replacement, hunters' return. Still stand-ins:
background hazards (kept by choice), kill-chance and protection multipliers, confusion and warning
formulas, learning rates, the threshold cull's constants (`cullThreshold` 0, `cullEvery` 30 days, `feedCost` 0.085: a
declared calibration, reported as the range 0.075–0.10, §9; `kidValue` 0.3; the kidding they weigh is blended with
camp records), the quota's `offtakeRate` where a cull rule other than opportunity is used (an experimental parameter
by choice), "other game" for wolves.

## 12. Changes since v1 (ae4f03d)

**v2 (the rebuild, 2026-10-21, commit 7b7e356 and the comment fix after it).** Reproductive cost of the genome
replaces trait running costs; kid exposure off; lean forage quality
added; oestrous cycles replace the flat 0.3; sequential-assessment contests replace the contest score
and hawk–dove fights; the day split into day/dusk/night sub-ticks; mating spatial (wildBuckRate and the
buckless fallback removed); herds, kids and captives walk; capture and stray retrieval as approach
tests; wolves switch prey on their own experience; foragers and a fodder store; herder load replaces
the herd cap; keep value blends individual and camp records; kids learn fear from their mothers; the
alarm flag is recomputed every sub-tick (bugs B1, B2 fixed); hunters no longer stall next to herd
goats (B3 fixed: they look for wild goats only). Growth 0.0035 and breeding size 0.8 recalibrated (both
historical: growth is the curve from 2026-11-18, C25, and `breedSizeFrac` 0.65, C30).

**v2.2 (2026-10-23, with Chris).** Crepuscular wolves: dawn sub-ticks added (herds walk out), wolves hunt
in every dusk, night and dawn sub-tick until fed (wolfAttempts unused), and goats flee wolves in real
time, the same rule as for hunters. Not recalibrated at the time (the batch-1 calibration is §9).

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
camp. Not cold-checked at the time.

**After v2.3, to v0.1.0 and since** (one line each; EXPLOG and DEVLOG hold the detail):
- 2026-10-25: food sites redrawn each year (`foodReplace` 1); dump-heap seeding backed out (`heapSeed` 0).
- 2026-10-27: alarms and spooks as fear learning (`alarmLearn`, off); the opportunity cull by keep-value threshold in
  the economy (`econCull`, `cullEvery`, `cullThreshold`) and the last breeders' value (off).
- 2026-10-28: kcal replace forage units (goats 1 fu = 3,600 kcal; human food 1 fu = 900 kcal); shelf-life store
  windows (`storeWindows`); need-relative returns (`needScore`, off) and seen gathering (`gatherSee`, off).
- 2026-10-29: the economy parked behind `economy` 0; human behaviour set per condition. H5 `provision` 0.6 → 2160.
- 2026-10-29 to 10-31: other game for economy hunters (`altGame`, off); ranged shots for fixed-policy hunters
  (`shotChance`, off); herder presence against wolves (`herderProtection`, off).
- 2026-10-31: `storeWindows` 1 (fodder keeps `fodderDays` 270) and `forageLoad` 36,000 kcal (was 72,000) the defaults.
- 2026-11-01: the herder chases wolves off the herd (`herderChase` 1, `herderChaseDist` 5, on by default).
- 2026-11-02: behaviour schedules within a run (`schedule`; the staged ladder); herd gene histograms (`histHerd`).
- 2026-11-03: the genome's reproductive cost off by default (`reproCostGrowth`, `reproCostFertility` 0.5 → 0); gene-load
  delays (`loadFirstBreed`, `loadRecovery`, `loadGrowth`, off); cull profiles (`cullRule` flight, return, attack) and
  sire profiles (`sireRule` random, calm, gentle, large).
- 2026-11-04: random cull spares the last sires (`keepLastSires`, off).
- 2026-11-05: twinning gene L, twins and triplets (`twinMax`, `tripletMax`, off); milk shared within the litter;
  lactation charged for milk made (`milkCost` 'made'); small kids die more (`juvSizeExp` 1.5); `postpartumDays`
  (0); unweaned-kid records (`kidLife`).
- 2026-11-09: milk in the keep value (`milkValue`, off) and the milk sire rule.
- 2026-11-10: neutral coat-marking gene C; sire rules deep, shallow, homebred, marked; each sex's own cull rule
  (`buckCull`, `doeCull`); exchange between camps (`exchangeN`, 0); gene-flow switches (`captureUntil`,
  `wildSireBlock`); the lean-tissue buffer (`leanBuffer`, 0 at first); headless runs about 2.5× faster, outputs
  identical.
- 2026-11-11: new standard settings `leanBuffer` 12,000, `herdRange` 8, `herdTravel` 2 (new); the cell relabelled ~1 km;
  `wildSireBlockFrom`, `cullFloor` (off); immigration into the wild (`immigrationRate`, off); lineage depth through wild
  births and gene histograms by lineage (`histDepth`).
- 2026-11-12: `surplusCull`, `fodderRation`, `milkCondition`, `winterCull` (all off by default).
- 2026-11-13/14: `winterBudget`, `winterCullAll`, `leanPulse`, spring feeding (`feedExtend`, `feedNeed`), all off;
  diagnostic record switches (`logWolfAtk` and the rest) and `histPeriod`.
- 2026-11-14 to 11-18: sex differences in size and growth (`sexSize`, `maleBirthSize`, 11-14); growth rules 'vb',
  'ogm' (11-14) and 'curved' (11-16); the keep value's growth credit (`growthCredit`, 11-17; `creditAge` and the 'cull'
  and 'max' references, 11-18).
- 2026-11-18 (commit 81615f1): new defaults `growthCurve` 'curved', `growYearsF` 3.75, `breedSizeFrac` 0.65, `sexSize`
  1.7, `maleBirthSize` 1.1, `growthCredit` 'herd'.
- 2026-11-18, **v0.1.0 (batch 1 frozen)**: the threshold cull without the economy and the default (`econCull` 1, with
  `cullRule` 'opportunity'); `keepFrame` ('year' default, 'horizon'); `cullSizeNeutral` 'age'; `feedCost` 0.15 →
  0.085; the experiment data protocol (tools/runyears.mjs `--exp`, LEAN records).
- 2026-11-19 (commit cda20ea): record thinning, output only (`recordEvery`; experiment runs scale every record period
  by k = ceil(years / 1600)).
- 2026-11-20 (commit 1468afe): `buckCull` / `doeCull` as keep-value terms under the threshold cull (`buckPrefValue`,
  `doePrefValue`, 0).
- 2026-11-20: output-only counters `wildConc`, `capIn`, `capBred` (8dd84a2); `cInitLo` / `cInitHi` (92d8f21); the
  herder-culture rules `runOffLoss`, `selfDoes`, `larder`, `captureTaper`, `nuisanceCost` (all off; defaults unchanged).
