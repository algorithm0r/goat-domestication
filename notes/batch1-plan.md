# Batch 1 experiment plan (model v0.1.0): draft for Chris's review

*Experiment session, 2026-11-19. Nothing here runs until Chris agrees. This revises the suite in `paper/outline.md`
("Runs the paper needs", draft 2, 2026-11-10/11) for the batch-1 model. Each block becomes one numbered experiment
(exp005 onward), pre-registered in EXPLOG before it runs.*

## What batch 1 changes in the outline's suite
1. **There's no offtake quota.** The default cull eats a goat once its keep value falls below zero (econCull, exp002).
   The outline's "offtake 0.1" is gone, and so is the sweep's cull factor as written (opportunity against random at a
   fixed rate). The random rule still needs a quota. The proposal below gives it the anchor's own rate (37.8 culled a
   year from a herd of 286, about 13%), so the factor tests *which* goats die, not *how many*.
2. **The buck and doe cull rules (rules block) can't run under the threshold cull.** They pick which goat of a sex dies
   within a count the overall cull sets, and the threshold cull has no count. The code refuses the combination.
3. **Body size is now the meat cull's signature** (the growth credit, exp001-exp003 and the crossover), not part of
   the syndrome. The outline's B results (3.2, 3.4, 3.5) were all on the old linear growth, where the credit was hidden.
4. **The reference culture changes** from milksel S0 (offtake 0.1, old growth) to the reference culture (REF; called R15 up to exp004, after its offtake rate, which no longer exists) on v0.1.0, which is the
   exp004 anchor: herd 286, R gap -0.63, B gap -0.25, breadth 6, males dead before 2.5 y 0.69.
5. **Run length and file size.** The outline set 4000 years (EXPLOG c16de77). A 1600-year run is 22 minutes and 9 MB
   of BSON; 4000 years would be about 55 minutes and about 23 MB, over Mongo's 16 MB. 4000 years needs a smaller
   record (year rows every 5 years after year 1600, say) before it can be stored.

## Blocks
Seeds are per cell or arm. Windows are 401-500, 801-900, 1201-1300 and 1501-1600, plus the last century if longer.

| block | arms | claim (section) | seeds | runs |
|---|---|---|---|---|
| B0 pilot (exp005, running) | REF leave-one-out: each behaviour off in turn (8 arms plus REF; exchange is already off), to 4000 years, on v0.1.0; also measures settling | does the threshold cull keep herds alive in poor cultures? A check before the sweep: with the wrong charges (exp002 TS), herds never grew | 4 | 36 |
| B1 controls | Wild Type I (no humans); hunting only | hunting raises wild R; wild means (3.1, Table 2) | 10 | 20 |
| B2 husbandry sweep | 2^9 factorial: cull (threshold / random at 13%), penning, guarding, provisioning, kid shelter, buck management, tethering, milking, exchange | which behaviour selects which gene; persistence; the emergent kill-off (3.2-3.3b) | 8 | 4,096 |
| B3 sire rules | sireRule oldest, random, calm, large, milk, homebred (memory 3), marked, in the reference culture | strong selection through bucks (3.2) | 8 | 56 |
| B4 lineage test | sireRule random, deep, shallow, homebred (memory 3) | the causal core (3.5, 3.6) | 20, then the CI rule | 80+ |
| B5 body size | growthCredit own, herd (2 y), herd from 3 y and 4 y, cull, max | body size from the meat cull: crossover and reference sensitivity (new section) | 8 | 48 |
| B6 feed cost | feedCost 0.075, 0.085, 0.10 | the calibrated range, and how the main results move across it (Methods, calibration) | 8 | 24 |
| B7 range | herdRange 4, 6, 8 | range sets herd size and the gaps (2.3) | 8 | 24 |
| B8 gene flow and pleiotropy | R3 arms (captures stop; wild sires blocked; both) and R2 (pleioW, pleioA on), arms as in the outline | gene flow by sex; what pleiotropy adds (3.7) | 8 | about 56 |

**Compute** at cpuslot level 12: about 4,440 runs × 22 minutes is about 1,630 CPU hours, which is 5.7 days at 1600
years, or about 14 days at 4000 years. The sweep is 92% of it. B0 runs first and alone (about 2 hours). B3-B8 (about
300 runs, about 9 hours) can run before the sweep, so the paper's sections other than 3.2-3.4 have numbers within a day.

## Decisions for Chris (one at a time, in chat)
1. Run length: 1600 years (what every batch-1 check used), or 4000 with a thinned record?
2. The sweep's cull factor: threshold against random at the anchor's rate (proposed), or drop the factor and fix the
   threshold cull (2^8 = 256 cells)?
3. The buck and doe cull rules: drop them from batch 1 (proposed), or run them on the quota cull as a supplement?
4. Seeds for the sweep: 8 as the outline accepted, or 4 for a first pass?

## What stays from the outline
The measures list (conceptions by origin, selSire/selDam, the three depths); the lineage block's CI stopping rule; the
neutral coat gene C as a drift yardstick (its gap varies by about ±0.1 per seed, exp-crossover gene figure, so single-
seed gaps under 0.1 are drift).
