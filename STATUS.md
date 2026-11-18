# Animal Domestication — STATUS
*One screen. The current pulse. Overwritten, never appended — for history read DEVLOG.*

**Updated:** 2026-11-18 — refreshed every session close; may carry unverified claims
**Verified:** 2026-10-18 (scaffold) — last cold audit (`/audit`); the State section is trusted only as of this date

## Stage
DEVPLAN Stage 4 — Herd management  `[ ACTIVE ]` (4f closed: realistic growth and body size; Done-when half met)

## State
Smoke PASS @ c8e5eda-dirty (40 y, 536 goats). Defaults since 81615f1: bezoar sex sizes (1.7), Chris's curved growth
at the wild pace (growYearsF 3.75), breeding at 0.65 of target, keep value crediting growth toward the herd's mean
adult size (growthCredit 'herd'). New defaults reproduce the crossover's CH seed 1 exactly (0 of 1600 years differ).
Experiments run as JSON files under results/ via tools/runyears.mjs and cpuslot, ledgered in EXPLOG (not expNNN).

## Metrics (anchor = R15 husbandry + defaults, years 1501-1600, 4 seeds)
- Herd 272; R gap -0.65; B gap -0.21 (own-growth credit +0.03; adult mean from 4 y -0.57; largest goat -0.67)
- Ganj Dareh slaughter: males dead < 2.5 y 0.47 ✗ (0.60-0.70); aged 4+ 0.19 ✓ (about 0.20)
- Herd starvation 48 a year: accepted as an artefact of food-limited growth (Chris 2026-11-18)

## Branches
- `main` (no remote); public mirror via tools/publish_public.sh (excludes paper/)
- sim-runfmt: harness/run-format branch, unmerged (stale world.draw calls)

## Open
- Males killed before 2.5 y below the Ganj Dareh band (0.47)
- Keep-value recalibration (one horizon; reference-size charges) — DEVPLAN Backlog
- G9, G12, G13 (MODEL §10) not rechecked since 2026-10-21 — unverified
- Accepted gap: herd starvation at carrying capacity (no calibration data)

## Next action
Choose with Chris what follows the closed body-size question; candidates in DEVPLAN Backlog. Offer a full sweep
of Stage 4 (unchanged since October apart from 4f).

## Blockers
- none
