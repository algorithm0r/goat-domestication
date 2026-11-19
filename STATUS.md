# Animal Domestication — STATUS
*One screen. The current pulse. Overwritten, never appended — for history read DEVLOG.*

**Updated:** 2026-11-18 (batch 1) — refreshed every session close; may carry unverified claims
**Verified:** 2026-10-18 (scaffold) — last cold audit (`/audit`); the State section is trusted only as of this date

## Stage
DEVPLAN Stage 4 — Herd management  `[ ACTIVE ]` (4f closed: realistic growth and body size; Done-when half met)

## State
Batch 1 frozen at v0.1.0. Smoke PASS @ 88ad485. Defaults: curve at the wild pace, bezoar sex sizes, breeding at 0.65,
growth credit toward the herd mean from 2 y, threshold cull (econCull 1, keep value below 0, opportunity rule only),
charges at the size for sex and age, feedCost 0.085. Experiments go through db.js v2 (exp001-exp004 so far).

## Metrics (exp004 A1: R15 husbandry + defaults, years 1501-1600, 4 seeds)
- Herd 286; R gap -0.63; B gap -0.25 (seeds -0.12 to -0.41); breadth 6
- Males dead before 2.5 y 0.69 (slaughter; calibrated via feedCost, exp003); aged 4+ 0.14; other Ganj Dareh measures miss
- Herd starvation 53 a year: accepted artefact (Chris 2026-11-18)

## Branches
- `main` (no remote); public mirror via tools/publish_public.sh (excludes paper/)
- harness/run-format merged 2026-11-18 (1866bd4)

## Open
- Ganj Dareh out-of-sample measures (aged 4+, does past 2.5, F:M) miss at the calibrated feedCost
- Kill age stays at 2-2.5 y across feedCost; guess (untested): the herd-mean reference sets it
- G9, G12, G13 (MODEL §10) not rechecked since 2026-10-21 — unverified
- Accepted gap: herd starvation at carrying capacity

## Next action
Draft the batch-1 experiment plan for Chris; brief the author session on the body-size reframe.

## Blockers
- none
