# Animal Domestication — DEVPLAN
*Living document, not frozen. The design is in DESIGN.md (bible, amended in place); this is the
build checklist. Status tokens: `[ DONE ] [ ACTIVE ] [ TESTING ] [ PLANNED ]`. A stage closes with a
**Closed** statement: the date, the evidence against its done-when, and where anything left over went.*

## Built
- Scaffold (engine v2): vanilla-JS canvas, model/view split, vendored DB client, main-realm runners.
- DESIGN.md v0.2, agreed in the 2026-10-19 workshop. Literature brief in `notes/`.
- Side experiment `../grain-diploid/`: the gene architecture tested on the grain model (DESIGN §12).
- World, vegetation and seasons (Stage 1). Wild goats with genome and a fixed wolf guild (Stage 2).
- Hunting humans and learned, threat-specific fear (Stage 3).
- Browser viewer: `index.html` via the Static Server (`/research/Animal%20Domestication/sim/`).

## Not yet built
- Herd management (Stage 4), experiments (Stage 5) and the later stages.

## Stages

### Stage 1 — World: grid, river, elevation, vegetation, seasons  [ DONE ]
- [x] `params.js`: world, clock (1 tick = 1 day, 360-day year), vegetation parameters
- [x] `world.js`: 80×50 grid in typed arrays: water table from the river edge, elevation rising away
      from it, escape-terrain flag, camp cells
- [x] Vegetation: one biomass value per cell, logistic regrowth at a water- and season-dependent
      rate, with a floor
- [x] Observer draws the field (biomass, elevation shading, river, camps); season readout
- [x] DataManager samples total biomass and season; runner and smoketest load the new files
**Done when:** headless, vegetation settles into a stable seasonal cycle (each year's mean biomass is
within 1% of the year before, by year 3), stays within [floor, K] in every cell, and the smoketest
asserts it. Ticks/s is recorded in the DEVLOG.
**Closed 2026-10-19.** Smoke PASS, seed 1: year-on-year drift 0.000% after a 20-year vegetation
pre-warm, range [0.241, 0.955], ~44k ticks/s (vegetation only). The mild seasonal swing was later
handled in Stage 2 through grazing and type II intake. Nothing carried.

### Stage 2 — Goats, genome, fixed wolves; no humans (H0)  [ DONE ]
- [x] Genome: haploid / diploid L (default 2), meiosis, one mutation per meiosis, the seven traits
      plus W's β link
- [x] Goat: energy budget, type II grazing, cell-scoring movement (DESIGN §5), flight, rut and
      gestation, birth, kid survival, ageing, death
- [x] Spatial index of agents by cell (no per-tick allocation)
- [x] Wolves: fixed guild, hunger-driven hunting, type III prey switching, detection by coat,
      escape-terrain discount. (Replacement of killed wolves needs guards → Stage 4.)
- [x] Observables: yearly trait histograms and means, population, life history, deaths by cause
- [x] Burn-in from uniform alleles to the wild-type equilibrium
**Done when:** goats persist with wolves for 500+ years across 10 seeds without collapse, gene
distributions settle, and life-history outputs (age at first kidding, kids per doe per year, adult
mortality) are in the ranges of brief §4.3.
**Closed 2026-10-19** @ bc8d90f, 10 seeds × 500 years, 60-wolf guild (`tools/runyears.mjs`,
`tools/plot_stage2.py`). Persistence ✓ (0/10 extinct; 373–630 goats). Natural herding ✓ (87–92% of
goats in herds of ≥5; largest 50–100). First kidding median 2.13 y ✓. Distributions settled within
±0.03 over the last 150 y, except T (0.047) and S, which drift because they are near-neutral once
everyone herds. Wild type: R 0.68±0.04, S 0.43±0.08, A 0.80, B 0.86, H 0.84, T 0.35±0.11, M 0.37,
W 0.87; every trait has room to move in the domestic direction. Adult mortality (0.31/y against
~0.10–0.15) → tidy-up T1. Mechanisms added in calibration are in the DEVLOG.

### Stage 3 — Humans: hunting only (H1)  [ DONE ]
- [x] Fixed human population at the camps, introduced after a no-human burn-in
- [x] Daily trips: walk out toward goats, hunt, back at camp by night; hunting effort is a fixed
      policy (share of days each human hunts), not a fixed demand, so there is no predator pit
- [x] Goats flee hunting humans (R × (1 − familiarity)): stalk detection, herd warnings, next-day disturbance
- [x] Hunt success depends on goat flight, warnings and terrain; hunters prefer meat (size)
- [x] Kill-off records: age at death by cause and sex, per year
- [x] Viewer draws humans
**Done when:** hunting runs, goats persist under it across 10 seeds, kill-off is recorded, and the
effect on wariness is measured and explained. (Reworded 2026-10-19 with Chris: the original "wild R
rises under hunting" was a prediction, not an acceptance criterion.)
**Closed 2026-10-19** @ 6113dcf, H0 vs H1, 10 seeds × 600 years, humans from year 300
(`tools/compare_conditions.py results/stage3 H0 H1`). Persistence 10/10 (goats ~270 vs ~530). Kill-off
recorded (hunted: 34% under 1 y, 40% male). Wariness: the first version had genetic R falling under
hunting (wolf displacement, disturbance cost, weak selection by hunters), which led to **learned,
threat-specific fear** (DESIGN §4.3). With it, effective fear of humans rises 14% (0.66 vs 0.58) and of
wolves falls 18%, while genetic R is neutral (0.60 vs 0.58). Hunted goats become warier of humans,
plastically. Nothing carried.

### Stage 4 — Herd management (H2–H6)  [ ACTIVE ]
- [x] 4a. Capture (approachable goats, orphans of hunted does), camp herds, daily herding to pasture,
      night penning (out of wolves' reach), strays lost or retrieved (retention filter), habituation
      inside the socialisation window. A wolf alarm sends herd goats to the herder; a herder spook
      sends them away. *Probe, seed 1, herding from year 400:* herds grow 8 → ~57 over 160 y; herded
      genetic R ~0.25 vs ~0.5 overall (capture bias + retention, to be separated in 4d).
      Open: orphaned unweaned kids starve without care → hand-rearing with milking (4b).
- [x] 4b. Cull rules (`random` H2, `youngMales` H3 with keepSires, `temperament` H6 by observed
      flightiness), milking (herders take a share of capacity; competes with the kid), camp milk pool
      hand-rears herd orphans. *Probe, seed 1, y560:* herded R — youngMales 0.29, youngMales+milking
      0.29, temperament 0.04 (escapes fall to ~1/y).
- [x] 4c. Pen protection (kill chance −80%), guarding (−70% more; guards may kill wolves, replaced
      by immigrants), lean-season provisioning with kid shelter. *Probe:* ~5 wolves killed/y under H5.
- [x] 4d. Herd does breed within the herd except wildBuckRate wild sires; allele lineage ids give
      identity by descent since herding began (ROH analogue); sires per camp-year; wild-sired share;
      R at capture vs in the herd; generations since capture. *Probe, H3 seed 1:* herd F 0.15–0.33 vs
      wild 0.03–0.10; 1–3 sires/camp; captured R ~0.5 vs herd R ~0.3 (retention beyond capture bias).
- [~] 4e. Condition batch H0–H6 × 10 seeds × 800 y (`tools/batch.mjs tools/conditions.json`,
      `tools/condition_table.py`). Batch runs ✓ (70/70). Fixes found by the first batch: stray retrieval by
      approachability, unpenned herders stay with the herd, common IBD baseline, herd-only kill-off.
      *Result @ 66b3b8c+:* herded − wild R: H2 −0.28, H3 −0.15, H4 −0.13, H5 −0.17, H6 −0.54; herd IBD
      0.30–0.88 vs wild 0.26–0.34; wild-sired share H2 0.14, H3–H5 0.49–0.62 (culling young males empties
      the herd of sires, so wild bucks fill in), H6 0.06. **Open: Ganj Dareh calibration.** Without
      offtake herds sit below target and keep old animals (H3: past 4 y 0.41 vs ~0.20). Meat offtake
      (`offtakeRate`, new) at 25–35%/y reproduces the profile (males dead < 2.5 y 0.66 ✓, past 4 y 0.28) but
      herds collapse to 3–4 goats, as in Triozzi & McClure 2026 (goat herds declined under all culling
      strategies). Needs a decision on herd productivity vs restocking.
      *Husbandry added (2026-10-20, with Chris):* kid sheltering (kids < 30 d in the pen), buck
      management (no herd fights; the keepSires oldest bucks sire), tethering of fearful captives at
      camp on fodder until tame. All in H5. Tethering was what let herds found under offtake: H5 herds
      hold ~72 goats at no offtake and persist at 15–25%/y (28–37 goats), falling at 35% (13).
      **Still open: the female side of the Ganj Dareh profile.** Offtake takes young males first and
      they alone supply 20–25%/y, so does are never reached and die old (past 4 y 0.41–0.60 of deaths
      ≥ 1 y, vs ~0.20; check also excludes first-year deaths, unlike archaeological survivorship).
      *Opportunity culling (2026-10-20, Chris's framing):* keep value from growth, kids, sire/replacement
      value, feed, meat at risk (DESIGN §7). H3–H6 now use it; H6 = H4 + flightiness cost. Rut guarding
      and wildFallback added. *Results (6 seeds, final 100 y):* H5 sustains 15% offtake (41–58 goats),
      shrinks at 20% (18), collapses at 25%. Ganj Dareh at 20%: males dead < 2.5 y 0.70 ✓, past 4 y 0.18 ✓,
      does past 2.5 y 0.45 (target 0.60–0.70) ✗. Rut guarding at 15%: wild-sired 22% → 0.5%, herd 41 → 57,
      R −0.26 → −0.35, B −0.19 → −0.28, IBD 0.57 → 0.75: isolation drives divergence (cf. the grain paper).
      Body size falls in persistent herds (B −0.18 at 15%) and survives a size-neutral cull rule, so it is
      not the rule's artefact; likely relaxed selection (no contests, fodder, protection) → confirm by
      ablation.
      *Rebuild (MODEL v2, 2026-10-21; v2.1 after a cold check @ b381d31).* The cold check found culling
      never ran in v2 (offtake 0, no cap: H3 = H2, H6 = H4) plus ~10 bugs; fixed. Offtake sweep (6 seeds):
      H3 holds at 10%/y, not 20%; H5 holds at 20%, collapses at 30%. Female side fixed by a 3-year keep
      horizon (a young doe's worth is mostly to come): does past 2.5 y 0.43 → 0.65–0.69; the B −0.15 seen
      in H5 at 20% vanished with it (a one-year-rule artefact). *Condition table @ b381d31 (10 seeds × 800 y,
      offtake 10%, `results/stage4v3`):* all persist; herded H2 92, H3 116, H4 22, H5 89, H6 24; herded −
      wild R −0.02 to −0.06 (was −0.13 to −0.54 before the rebuild); R of captives ≈ R of herds
      (0.81–0.89); herd IBD 0.28–0.44 vs wild 0.15–0.18; wild-sired 0.3–8%. Ganj Dareh: does past 2.5 y
      0.66–0.69 ✓ (H5 0.78); males dead < 2.5 y H3 0.58, H5 0.56, H2 0.46, H4/H6 0.30; past 4 y 0.33–0.47 ✗.
      **Open (MODEL §10):** G9 too many old goats (no reproductive senescence in does); G12 penned herds
      without husbandry stay at 2–13 per camp and are repeatedly lost and refounded (generations since
      capture 3.9 vs 21–33 unpenned; doe condition, pregnancy and heats the same; not offtake — 20 goats at
      0% too), mechanism not found; G13 the R signal is weak, so the behavioural filters (capture,
      retrieval, spook, cull) now seem to act on learned fear more than on R, as habituation resets fear;
      untested (ablate habituation).
- [x] 4f. Realistic growth and the source of herd body size (2026-11-14 to 11-18, EXPLOG; DEVLOG 2026-11-18).
      Defaults now: bezoar sex sizes, Chris's curved growth at the wild pace, breeding at 0.65 of target, and the
      keep value crediting growth toward the herd's mean size (a herder's learned expectation). Body size
      shrinks only through that credit (crossover). Anchor, years 1501-1600: males dead < 2.5 y 0.47 ✗ (0.60-0.70),
      past 4 y 0.19 ✓. Herd starvation at capacity (about 48 a year) is accepted, not a target (Chris 2026-11-18).
**Done when:** the H0–H6 condition table runs as a headless batch, and the H3 kill-off profile
matches Ganj Dareh (60–70% of males dead by 2.5 years; about 20% of all goats past 4 years) as a
calibration check.

### Stage 5 — Experiments  [ PLANNED ]
- [ ] Ensembles per condition; heatmaps in the grain paper's form; domesticated-share curves
- [ ] Sweeps: gene flow (G), pleiotropy β (P), ownership preference (W), architecture (A)
- [ ] Order-of-change analysis (DESIGN §9, pattern 2)
**Done when:** each DESIGN §2 prediction has a figure and a stated outcome.

### Stage 6 — Adaptive policy mode  [ PLANNED ]
### Stage 7 — Wolves as commensals (reproduction on; refuse, protein surplus, pup adoption)  [ PLANNED ]
### Stage 8 — Grain coupling: fodder and the CYP2C19-like locus (optional)  [ PLANNED ]

## Tidy-up (carried items, no stage of their own)
- **T1. Adult mortality** is 0.31/y (all goats ≥ 1 y) against ~0.10–0.15 for adult females. Report it
  by sex and age class first (yearlings and fighting males inflate it), then decide whether it
  needs fixing. It matters because it sets generation time (~3–4 y now), which scales evolutionary
  speed against archaeological time. Do before Stage 5.
- **T2. H and W sit near the top of their range** in the wild type (0.84, 0.87). Fine for now: both
  should fall under domestication. Revisit if a condition needs them to rise.
- **T3. Bake the burn-in.** Every run repeats a 300-year no-human burn-in. Save wild-type
  checkpoints per seed and start conditions from them. Do before the Stage 5 batches.

## Backlog
- [ ] fix: about 20 analysis tools that EXPLOG cites as "scratchpad ..." (ablate_tab.py, milk_tab.py, overlap.py, ...)
  are lost with earlier sessions' scratchpads; their result tables are in results/. Keep new tools in tools/.
- [ ] feat: migrate the runner to db.js v2 and expNNN experiment names (results are JSON under results/, README
  still describes the Mongo runner).
- [ ] idea: recalibrate the keep value: one horizon for every term (growth, kids, feed, risk), feed and risk at a
  reference size for sex and age, and keepHorizon 3 revisited (probe 2026-11-17: buck kids sit in the bottom 15%).
- [ ] idea: males killed before 2.5 y are 0.47 in the anchor against Ganj Dareh 0.60-0.70.
- [ ] idea: horns shrink more under the own-growth credit (-0.24) than under the herd average (-0.11); unexplained.
- [ ] idea: pigmentation -0.13 in the anchor only (3 of 4 seeds beyond the neutral gene's drift range): hitchhiking
  or drift, untested.
- [ ] fix: trace the condition gap between bucks and dry does.
- [ ] idea: are the winter cull's kids male or female?
- [ ] feat: merge the harness/run-format branch (sim-runfmt; it still has world.draw(c, ...) calls) on Chris's word.
- [ ] idea: should paper/ go public? (asked, unanswered)
