# Animal Domestication — Design (v0.2, agreed for build)

*Design bible: amended in place, not a log. First pass 2026-10-18; workshopped and amended
2026-10-19 (decisions in §11). Literature grounding, with sources and how far each was checked:
[notes/research-brief.md](notes/research-brief.md). Grain side experiment on the gene architecture:
`../grain-diploid/` (§12).*

---

## 0. The question

The grain paper tested competing *unintentional* mechanisms of plant domestication as explicit
behavioural rules. Selective harvesting alone never produced domestication syndrome. Planting that
isolated the planted lineage did, even with no trait under selection. Its conclusion names
human–animal coevolution as the next application of the method.

Goats come with a puzzle that fits the method. At Ganj Dareh (about 8200–7600 cal BC), 60–70% of males
were killed before 2.5 years, and the herded goats were already genetically distinct and inbred, with
few sires. Yet they are **morphologically wild** and show **no selection sweeps**. Body-size reduction
and horn change arrive 500–1,500 years later (Daly et al. 2021; Zeder 2008). Throughout, gene flow
from wild goats was substantial (Marshall et al. 2014; about 30% wild ancestry in Neolithic Serbian goats).

**Question:** which human behaviours toward a wild herd animal are sufficient to reproduce that
sequence? The candidates are hunting, keeping, sex-biased culling, penning, protecting, milking and
culling by temperament. **Second question:** does the syndrome need a shared developmental cause
(pleiotropy), or can the selective regime produce the trait suite from independent genes?

Wolves enter in two roles. First (v1) they are the wild predator that gives goats' anti-predator
traits a function. Second (Stage 2) they are a commensal-pathway domesticate.

### Patterns the model should reproduce (ODD element 1)
1. **Coexistence.** Herded and wild goats persist as distinct populations despite gene flow (Ganj
   Dareh "Main" vs hunted "Outlier"), the analogue of grain's bimodal split.
2. **Order.** Demographic management first, then genetic differentiation by drift and inbreeding,
   then shifts in behaviour and pigmentation, and body size and horns last.
3. **Conditionality.** The transition takes hold only in part of the parameter space.

**Calibration, not tests.** A "cull young males" rule produces a Ganj Dareh kill-off profile by
construction, so matching it checks the demography and says nothing about domestication. Herd
viability is a real constraint: Triozzi & McClure 2026 found goat herds declined under all ten
idealised culling strategies. Their open stage matrix is the reference for our demographic layer.

---

## 1. What carries over, and what does not

**From the grain model (keep):**
- Hypothesis discrimination by fixed behavioural conditions, run as ensembles. Humans hold behaviour
  constant within a run. The paper reports that a dynamic human population on a small grid
  collapsed into predator–prey cycles, so v1 keeps the human population fixed.
- A **cost on every trait**, the grain model's gene-minimisation penalty, so a trait whose benefit humans
  remove decays. Relaxed selection is a first-class mechanism.
- River and water-table world, camps, metabolic excursions.
- Uniform initial genes plus a no-human burn-in, so the wild type is an emergent equilibrium and not
  an imposed one.
- **Reproductive isolation of the managed lineage**, which is what domestication tracked in grain.
  For a herd animal the isolation is literal: a penned herd versus wild bucks. That makes gene flow
  from the wild the main lever.
- Two of the grain paper's own stated limitations, taken on here: a **genotype→phenotype step**
  and **seasons**. The phenotype is what the genes do through the model's mechanisms
  (development, nutrition, habituation, encounters), not genotype plus noise (§4.1).
- **Not carried over:** the grain model's second mutation when a harvested grain is sown. A copied
  grain or animal does not mutate; mutation happens once, at meiosis.

**From AgriGin (what it got right, and why it stalled):**
- Right: goats with heritable behavioural genes (horns, herd, aggression, fear), cell-scoring movement
  that reads the genes, a carcass/meat economy, goats and humans in the grain world.
- **Hunting selected the wrong way.** `huntGoat()` kills when `random > aggression`, so it removes the
  least aggressive goats. No human action kept a goat alive, so no setting could domesticate.
- **Inheritance was single-parent.** `new Goat(this)` copies the initiating parent's genes and the
  mate contributes nothing. Averaging two parents fails differently: blending halves the variance
  each generation and selection runs out of material. The one published wolf→dog ABM (Elzinga et al.
  2025) draws each pup's value uniformly between its parents', and it needs assortative mating to get
  any divergence (0% of runs without it, 74% with it). Our diploid design keeps variance, so it can
  test whether physical isolation does what assortative mating did there.
- **The RL could not see the payoff.** It used tabular Q-learning over 13 primitive actions (step N, NE, …,
  harvest, plant, hunt), discount γ = 0.5 (an effective horizon of about 2 steps), ε decaying ×0.99 per
  action (under 1% exploration after about 460 actions), and rewards in units that do not compare
  (seed counts, water units, −2 penalties). Planting or herding pays off seasons later, and partly to
  other people. The problem is the horizon, not the idea of adaptation, and §7 moves adaptation to the
  timescale where the payoff shows.

---

## 2. Conditions (the experiment the model is built for)

The conditions follow Zeder's *prey pathway* (hunting → game management → herd management → directed
breeding). They are ordered by how early each human action is documented (brief §6).

| ID | Condition | What humans do | Evidence | Prediction to test |
|---|---|---|---|---|
| H0 | Control | No humans | — | Wild-type equilibrium under wolves and seasons |
| H1 | Hunting only | Hunt wild goats | Asiab, before ~9300 BC | Tame goats are caught first, so selection runs *toward* wariness; no DS |
| H2 | Keeping, trait-blind | Capture approachable animals (orphaned kids), keep a herd, cull at random | Implied | **Retention filter.** Flighty animals escape back to the wild, so the herd is enriched for tameness with nobody choosing. This is the animal analogue of "bottom of the basket" |
| H3 | H2 + demographic culling | Cull subadult males, keep females | **Established early** (Ganj Dareh) | Few sires, so drift and inbreeding. Does it reproduce "distinct but morphologically wild"? |
| H4 | H3 + penning | Night pens, which cut wild mating and raise density | **Established early** (Aşıklı Höyük) | Isolation, plus stress selection on R |
| H5 | H4 + protection and provisioning | Guard from wolves, feed in the lean season | Inferred | Relaxed selection on anti-predator traits and on seasonality |
| H6 | H4 + temperament culling | Cull the most reactive and aggressive | Inferred (RRM1 sweep by ~6500 BP) | The Belyaev analogue: fast change. Which traits follow? |
| G | Gene-flow sweep, crossed with H2–H6 | Wild-buck mating rate per season, 0–0.3 | 30% wild ancestry reachable | The isolation axis. Gene flow both brakes divergence and rescues inbred herds. Where does it tip? |
| P | Pleiotropy switch, crossed with all | β (R → spotting) = 0 vs > 0 | NCC debate | §4.3: the β contrast within a condition isolates the link |
| W | Ownership marking, crossed with H3–H6 | Herders prefer to keep marked (spotted) animals | KIT/KITLG sweeps | Preference vs relaxation, told apart by timing and direction (§4.3) |
| A | Gene architecture, crossed with the main conditions | haploid, diploid L = 2 (default), 4, 6 | grain side experiment §12 | Robustness of every result to the architecture |

The headline result would be H3 or H4 producing a distinct domestic type with no trait ever chosen,
which is what unintentional planting did for grain.

---

## 3. World

- **Grid** 80×50, closed, no wrap. It is wider than grain's 50×50 because herd animals range. A
  cell is nominally about 1 km (2 km until 2026-11-11), so the world is roughly 80×50 km; that sets how far an animal
  moves in a day (below).
- **River valley to uplands.** The river runs along one long edge, and the water table falls with
  distance as in grain. **Elevation** rises away from the river. High cells are *escape terrain*
  where wolves succeed less often; cliffs are the bezoar's real anti-predator refuge.
- **Vegetation: one biomass value per cell**, in typed arrays, not plant agents (grain had up to 4
  plant agents per cell). It regrows logistically at a rate set by water and season, and goats graze
  it down. Sim speed matters more than plant detail. Regrowth keeps a small floor (root reserve), so
  grazing cannot drive a cell extinct, which damps a goat–vegetation boom and bust.
- **Clock: one tick = one day, year = 360 ticks.** Life history then comes straight from the
  literature in days: gestation 150, rut window, age at first breeding. A human trip out and back is
  one day, with herds penned at night. **Movement per tick** is a parameter per species, in cells per
  day (default goat 2, wolf 4, human 3), so calibration changes speed without changing the clock.
  Metabolism is in daily units. The calibration targets are goat daily intake vs regrowth, wild herd
  density, and hunting trip length.
- **Seasons.** A growing season (regrowth on) and a lean season (regrowth near zero). The rut comes in
  autumn and kids are born in spring. The lean season is why a live herd is worth having: it is
  stored food that walks, the animal analogue of the granary (Alvard & Kuznar 2001, "deferred
  harvests").
- **Camps** (2–4) near the river, each with its own herd and stores, so camps can differ and, in
  adaptive mode, imitate one another.
- **Upland refugium** beyond the humans' excursion radius, where a wild population always persists.
  It is the gene-flow reservoir, the analogue of grain's persistent wild stand.
- **Run length.** Morphology lags by 500–1,500 years, so runs need roughly 1,500–2,000 simulated years
  (540k–720k daily ticks). The grain model ran 100k ticks at 100–400 ticks/s under `vm`. Ours runs in
  the main V8 realm (engine v2), and the per-tick budget is the main performance constraint: typed
  arrays for the field, no per-tick allocation, spatial index by cell.
- **Grain** is left out of v1. Humans gather an abstract plant food from vegetation. With two
  co-evolving domesticates in v1 we could not tell which caused what. A later stage plugs grain in as
  human food and as fodder, together with a CYP2C19-like fodder-tolerance locus (Daly 2018).

---

## 4. Genome

### 4.1 Architecture
- **Diploid and multi-locus, L = 2 by default.** Each trait has L loci. Each allele is a real number,
  and the genotypic value G is the mean of the 2L alleles, in [0,1]. Each parent passes one allele per
  locus at random (free recombination). Each allele mutates at meiosis by the grain model's ±0.04
  uniform step. A copy (an animal moved between herds) never mutates. This keeps additive variance
  across generations (see §1, blending).
- **Architecture is a swept condition**: haploid (one allele per trait, each trait inherited from a
  random parent; not blending), diploid L = 2, 4, 6. L = 2 is the default. In the grain side experiment
  it domesticated like haploid (0.48 vs 0.48), with the least pull toward the middle (§12). The mean
  of 2L alleles pulls traits toward 0.5 as L grows. The grain model's pre-human Abscission settled at
  0.05 haploid but 0.35 at L = 6. So the wild equilibrium partly depends on L, which is why L is swept.
- **No noise term.** The phenotype is what the genes do through the mechanisms: R through habituation
  and the socialisation window, B through nutrition during growth, T through nutrition and stress,
  contests and flight through whom the animal meets and on what terrain. Humans and wolves act on
  what they observe (it fled, it charged, it grew large), never on genes. **Heritability is an
  output**, measured by offspring–parent regression on realised behaviour and size, and compared with
  the published 0.1–0.35. It is never tuned in.
- **Pleiotropy is switchable, never hard-wired.** A and R are independent by default; a shared-locus
  switch lets them co-vary (brief: r_g weak, ≈ 0.2–0.3). W's expressed genotype is
  (1 − β)·G_W + β·G_R, with β = 0 by default (§4.3).
- **Costs.** Every trait value carries an energy maintenance cost. This is the grain penalty in
  energy units.
- **Optional large-effect locus** inside R (RRM1 I241V-like; Dou et al. 2023), so a behavioural
  sweep can be detected in the simulated genome against the polygenic background.

### 4.2 Traits (v1 core: seven)

| Sym | Trait | What it does in the model | Wild benefit | Cost | Published h² (check, not input) |
|---|---|---|---|---|---|
| **R** | **Reactivity** (fear / HPA axis), the hub | Flight distance from humans and wolves. **Closes the socialisation window** earlier (window ∝ 1 − R). Under crowding or penning, stress lowers fertility | Escape from wolves and hunters | Feeding lost to flight; fertility loss at density | 0.25 (0.1–0.35) |
| **A** | Reactive aggression | Contest strength; defence against wolves; charging handlers | Mating access, defence | Energy, injury | 0.15 (0–0.35) |
| **S** | Gregariousness | Cohesion with conspecifics; how herdable it is; strays less | Dilution of predation risk | Competition for forage | 0.2 (assumed) |
| **B** | Body size | Intake need, contest weight, resistance to wolf kills, lean-season reserve, meat yield. **Plastic**: realised size depends on nutrition during growth | Contests, reserves, defence | Maintenance ∝ B | 0.3 (0.15–0.45) |
| **H** | Horn size (expressed in males) | Contest weight; wolf defence | Sexual selection | Energy | 0.4 (assumed) |
| **T** | Breeding-season breadth | Width of the rut window, as a **reaction norm**: genetic baseline shifted by nutrition and stress | Narrow: kids born at the vegetation peak | Off-season kids die in the lean season unless provisioned | 0.15 (assumed) |
| **M** | Milk yield | Milk produced above kid need | Kid growth, up to need | Energy | 0.2 (0.04–0.39) |
| **W** | Coat pigmentation (camouflage) | Wolves detect low-W (conspicuous, spotted) goats more readily. Gets weight β from R when the pleiotropy switch is on. Herders may prefer marked animals (condition W) | Camouflage against wolves | Pigment maintenance cost, so relaxation can drive a sweep toward less pigment when protection removes the benefit | Mendelian-like |

Each trait is there to carry a mechanism. R carries retention, hunting and temperament selection. A,
H and B carry relaxed sexual selection when males are culled. T carries relaxed seasonality under
provisioning. M carries milking. S carries herdability. W carries camouflage, its relaxation, and the
pleiotropy test. Body size and
horns are the archaeological markers, so whether their lag appears is a real test.

**Optional, later:** litter size (h² ≈ 0.1); a recessive deleterious load, so that inbreeding
depression is explicit and gene flow can rescue small herds; a MUC6-like disease-resistance allele
present only in a related wild population (adaptive introgression); and a CYP2C19-like fodder locus
for the grain coupling.

### 4.3 Two distinctions the model must keep
- **Tame vs domesticated: genetic reactivity × learned, threat-specific fear** (decided 2026-10-19).
  R is heritable general reactivity (the stress axis) and sets how strongly and how fast a goat learns
  fear. Each goat also carries two learned fears, of wolves and of humans (1 = naive). Surviving an
  attack or seeing a herdmate killed nearby raises the fear for that threat (× R); without threat it
  relaxes back toward 1 (half-life about a year); a kid takes on its mother's values at weaning
  (maternal transmission). Effective fear of a threat = R × learned fear: it drives alarm, stalk
  detection, the last-moment bolt, avoidance and warning herdmates. Habituation (Stage 4) is the same
  variable pushed down by harmless exposure, fastest inside the socialisation window (length set by R;
  fear onset moved from ~45 days to > 4 months in the foxes, Trut et al. 2009). So a kid raised in camp
  is tame whatever its genes, and a herd can pass tameness down the maternal line without any genetic
  change. Domestication is the genetic shift; tameness can be learned and transmitted. Evidence:
  flight distances lengthen in hunted populations (Stankowich 2008); moose that lost calves became
  warier of wolf cues specifically (Berger et al. 2001).
  *First result (Stage 3):* under hunting, effective fear of humans rises 14% while genetic R is
  unchanged; with no humans, learned fear of wolves lets genetic R settle lower (0.58 vs 0.69 without
  learning). Plasticity shields the genes.
- **Syndrome by pleiotropy vs by regime.** The pleiotropy test is the contrast between β = 0 and β > 0
  *within* one condition. Whatever moves W in both runs (camouflage relaxing under protection, herder
  preference) cancels out, and what remains is the link to R. W's own two causes are told apart by
  timing and direction. A relaxation sweep needs protection first and runs toward the cheapest coat
  (convergent loss of pigment), and only if the cost is large against drift (s > 1/2Ne, so small herds
  may just drift). A preference sweep can happen with wolves still active, and runs toward whatever
  herders favour. Separately, the domestic-minus-wild difference across R, A, B, H and T can show a
  "suite" from independent genes, if one management regime relaxes all of their benefits at once.
  That would be the selective regime producing the syndrome, which bears on Lord et al. 2020
  against Wilkins et al. 2014. Burban et al. 2022 predict genetic correlations *emerge* under
  domestication, which our within-herd correlation matrix can check.

---

## 5. Goat behaviour: scripted, varied by genes

Goats do not learn, apart from habituation. Each tick a goat scores its 9 Moore cells and moves to
the best one, as in AgriGin, with terms read from its phenotype:

```
U(c) = forage(c)·hungerNeed + water(c)·thirstNeed
     + S·conspecifics(c)
     − R·(1 − familiarity)·threat(c, humans)
     − R·threat(c, wolves)·(1 − escape(c))
     + mateDrive·inSeason·mates(c)
     + ε·noise
```

- **Flight.** A human or wolf inside the flight distance (∝ effective R) triggers flight. This is why
  hunting, capture and herding depend on the genes.
- **Energy budget** per tick: intake − maintenance(all trait costs) − gestation − lactation. Death
  comes from starvation, wolves, culling, hunting or age.
- **Reproduction.** Females are receptive inside the rut window (T). Males contest access with A, B and H,
  as AgriGin's `matingCombat` did. Gestation lasts 150 days, with 1 kid by default (twinning optional).
  Kid survival depends on maternal milk up to need, then on season.

---

## 6. Wolves

- **v1: wild predator only, fixed population.** Wolves are simple agents. They roam and detect goats
  (conspicuous coats and goats that don't flee in time are taken first), chase (escape terrain cuts
  success), kill, eat and scavenge carcasses. Hunger drives hunting and a kill satiates, so total
  predation tracks the number of wolves while encounter rates fall when goats are scarce. **Wolf
  numbers are fixed**, like the humans: wolves do not breed or starve, and a wolf that dies (killed by
  a guard) is replaced by an immigrant from the upland edge. This holds predation pressure steady and
  rules out wolf–goat predator–prey cycles and co-extinction, the failure the grain paper hit with
  dynamic humans. Without a predator, reactivity, gregariousness, camouflage and escape-terrain use
  have no function in the wild, so protection has nothing to relax.
- They carry the same behavioural genome (R, A, S, B, W), inert in v1 because they do not breed, so
  Stage 2 needs no new genetics, only wolf reproduction.
- **Stage 2: commensal pathway**, with three competing mechanisms from the brief:
  - scavenging camp refuse (Coppinger);
  - the winter protein surplus (Lahtinen et al. 2021);
  - humans raising pups taken before the socialisation window closes (Serpell 2021), which runs
    straight through R's window.

  Humans kill wolves that take herd goats. Tolerated wolves near camp deter wild ones. This tests
  Zeder's commensal pathway against the goats' prey pathway in one world.

---

## 7. Human architecture: scripted routines, adaptive policy

Three layers, each working at the timescale where its signal appears.

**Layer 1: routines (scripted, legible).** Rest at camp · Gather · Hunt (stalk a wild goat; success
depends on its detection and flight) · Capture (take an approachable kid or animal into the herd) ·
Herd (to pasture and back) · Pen (at night) · Milk · Slaughter (apply the cull rule) · Guard. Each is
a short deterministic script, with movement as in grain.

**Layer 2: daily choice (needs-driven utility).** Which routine to run today, from hunger, camp
stores, season and herd state. Fixed weights, plus small noise between individuals.

**Layer 3: camp management policy.** A small vector per camp:
- `cullRule`: weights over sex, age, observed reactivity, aggression and size;
- `herdTarget` and `captureRate`;
- `penning`, `guarding`, `provisioning`;
- `sireControl`: any male mates / keep a few sires / exclude wild bucks;
- `milkingIntensity`.

Humans judge animals by behaviour they observe (it fled, it charged) and by visible traits (size,
coat, horns). They never see genes.

**Culling is opportunistic** (decided with Chris 2026-10-20). Herders keep an animal while keeping it
pays and slaughter it for meat once it does not. Each herd animal's one-year keep value, from what a
herder can see: + meat still to grow, + a doe's expected kids (her kidding record, else the herd's,
zero past breeding age), + sire value for the kept sires and half that for one replacement buck,
− a year's feed, − meat at risk of dying unused, − (H6 only) a cost for observed flightiness. Offtake
(`offtakeRate` per year) and the herd cap take the lowest keep value first, with a little judgement
noise. Feed and meat-at-risk are charged per head (`cullSizeNeutral`), so the rule cannot itself
select on body size. The kill-off profile is therefore an output of herd economics, not an input.

**Husbandry** (H5): kid sheltering (kids under 30 days stay in the pen), buck management (no fights
in the herd; chosen sires, with a replacement held back), tethering of captives too fearful to approach
until they are tame, lean-season fodder, guarding. **Rut guarding** (`rutGuard`) keeps receptive herd
does at camp during the rut, cutting wild-buck sirings at the cost of grazing; `wildFallback = 0` leaves
a buckless herd's does unbred rather than letting wild bucks in. **The human population is fixed**: no births or deaths, as in the
grain model.

- **Fixed mode** (the experiments in §2). The policy is the condition, held constant for a run.
- **Adaptive mode** (later stage). Once a year each camp scores its policy by food security in the lean
  season, and copies the policy of better-scoring camps with some copy error. This is payoff-biased
  social learning (Boyd & Richerson). The alternative is a per-camp bandit over a policy menu. Either
  way the learner works at the yearly, camp-level horizon where a management payoff shows, which
  AgriGin's per-step learner could not reach. Alvard & Kuznar's deferred-harvest logic supplies the
  economics. Adaptive mode asks: as hunting returns fall, do camps move into herding without a script
  telling them to?

---

## 8. Schedule (one tick)

1. Clock, season, vegetation regrowth.
2. Goats: energy, move (§5), flight, graze, mate/gestate/birth, death.
3. Wolves: move, hunt, eat, breed, death.
4. Humans: one routine step (§7). Hunting, capture, milking and slaughter resolve here.
5. Year end (tick % 360 == 0): adaptive-policy update if on, census, observation.

---

## 9. Observables

- **Gene and phenotype heatmaps** over time for each trait, wild vs herded. This is the grain paper's
  figure form, so the two papers read together.
- **Divergence.** Wild/herded bimodality in R; the domestic-minus-wild difference per trait;
  the within-herd genetic correlation matrix (Burban's prediction).
- **Ganj Dareh diagnostics.** Pedigree inbreeding F, sires per year, number of paternal lineages (a
  Y-diversity proxy), and fraction of ancestry from wild immigrants.
- **Order of change.** For each trait, the year its herded–wild difference first exceeds a threshold.
  Pattern 2 is a prediction about this ordering.
- **Kill-off profiles.** Age and sex at death by cause (hunted, culled, predated, starved), plus the
  body-size distribution of the dead. The format is zooarchaeology's, for calibration (§0).
- **Generations since capture**, the analogue of grain's generations-since-planting.

---

## 10. Build stages (live checklist in DEVPLAN.md)

1. **World.** Grid, river, elevation, vegetation and seasons. *Done when* vegetation holds a stable
   seasonal cycle headless.
2. **Goats, genome and fixed wolves, no humans (H0).** *Done when* goats persist with wolves for 500+
   years without collapse across 10 seeds, and gene distributions settle.
3. **Hunting (H1).** *Done when* the population persists under hunting and R shifts upward.
4. **Herd management (H2–H6).** *Done when* the condition table runs as a headless batch, and the
   H3 kill-off profile matches Ganj Dareh as the calibration check.
5. **Experiments.** Ensembles, figures, then the gene-flow and pleiotropy sweeps.
6. **Adaptive mode.** 7. **Wolves as commensals.** 8. **Grain coupling** (optional).

---

## 11. Decisions (workshop, 2026-10-19)

1. **Fixed-policy humans in v1.** Adaptive mode is Stage 6.
2. **Wolves in v1 as predators**, with a **fixed population**. Humans are fixed too. Both choices
   avoid predator–prey collapse; goat–vegetation dynamics may still cycle, which is why regrowth
   keeps a floor.
3. **Seven core traits** as tabled (§4.2).
4. **Clock: one tick = one day, 360-day year**, chosen over 120 ticks/year, which felt too fast.
   Final speeds come from calibrating goat metabolism, vegetation growth and human trip length.
5. **Vegetation is one value per cell**, not plant agents. Sim speed takes priority over plant detail.
   Grain genetics are out of v1.
6. **Gene architecture is a swept condition**: haploid, diploid L = 2 (default), 4, 6.
7. **Phenotype from mechanism, no noise term**; heritability is measured, not tuned.
8. **W is camouflage with a cost**, so relaxation can sweep; ownership preference is its own condition.
9. **One mutation per meiosis.** The grain model's second mutation on sowing was a bug.

---

## 12. Grain side experiment: does the gene architecture change the known result?

`../grain-diploid/`: the grain model with its genes swapped for the diploid design (`loci`,
`outcrossRate`); `loci: 0` is byte-identical to the original on a seeded run. Anchor condition (plant
first-harvested, pop 80), 2 replicates each. Non-shattering share at 100k ticks:

| | selfing | 2% outcross | full outcross |
|---|---|---|---|
| haploid (paper ≈ 0.48) | 0.48 | — | — |
| L = 2 | 0.48 | 0.46 | 0.01 |
| L = 4 | 0.45 | 0.45 | 0.02 |
| L = 6 | 0.42 | 0.40 | 0.02 |

What it shows:
- More loci mean slower evolution, and a wild equilibrium pulled toward the middle.
- At realistic wheat and barley outcrossing (about 2%) the known result survives.
- Full outcrossing destroys it: pollen flow breaks the isolation of the planted lineage.

For goats, which cannot self, the lesson is that isolation of the herd has to come from penning, sire
control and distance from wild herds, so the wild-buck mating rate is the central lever.
