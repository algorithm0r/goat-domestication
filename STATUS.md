# Animal Domestication — STATUS
*One screen. The current pulse. Overwritten, never appended — for history read DEVLOG.*

**Updated:** 2026-10-21 — refreshed every session close; may carry unverified claims
**Verified:** 2026-10-18 (scaffold) — last cold audit (`/audit`); the State section is trusted only as of this date

## Stage
DEVPLAN Stage 4 — Herd management (H2–H6)  `[ ACTIVE ]` (4e open)

## State
Rebuilt model (MODEL.md v2.1, cold-checked against source by a subagent 2026-10-21, fixes @ b381d31).
Smoke PASS. Condition table H0–H6 × 10 seeds × 800 y runs (`results/stage4v3`), all persist.

## Metrics
- Wild type: first kidding 2.81 y, 88% of goats in groups ≥ 5, T 0.44 (seasonal breeding)
- Herded goats (final 100 y): H2 92, H3 116, H4 22, H5 89, H6 24
- Herded − wild genetic R: −0.02 to −0.06
- Ganj Dareh: does past 2.5 y 0.66–0.69 ✓; males dead < 2.5 y H3 0.58; past 4 y 0.33–0.47 ✗ (~0.20)

## Branches
- `main` (no remote)

## Open
- G12 penned herds without husbandry stay small (2–13 per camp, refounded); mechanism not found
- G13 weak R signal; filters may act on learned fear (habituation resets it); ablate to test
- G9 too many old goats; no reproductive senescence in does
- Tidy-up T1–T3 (DEVPLAN)

## Next action
G12: per-camp herd dynamics in H4 (`tools/campherds.mjs`), find what keeps penned herds small.

## Blockers
- none
