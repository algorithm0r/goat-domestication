# Animal Domestication — EXPLOG (experiment ledger)
Newest entry on top. **Append only — never edit past entries.**

**What this is:** the record of *experiments and what they taught us*: the question asked, the
**exact settings** that produced the result, the numbers, and the conclusion. DEVLOG says what changed
in the *code*; EXPLOG says what we *learned from runs* and how to reproduce it. When an experiment sets
or changes a standard setting, note it here **and** carry the change into `src/params.js` + DEVLOG.
Keep settings blocks complete enough to re-run from scratch. (Format from RLLayers' EXPLOG.)

**Protocol** (Chris's, adopted in RLLayers 2026-07-28; here from 2026-10-25): **pre-register** the
exact settings *before* running, as a checkpoint to second-guess any undiscussed change. After the data
is in, append **raw results only** (numbers, no narration, no conclusions). Conclusions are drawn
separately, later, in their own dated entry.

**Where things are:** settings files `tools/*.json` (conditions = overrides on `src/params.js` at the
named commit); raw outputs `results/<folder>/` (git-ignored, on this machine only; each run's JSON
carries its full `params`); batches run with `node tools/batch.mjs <settings> <folder> <years> <seeds>`;
raw tables with `python tools/trial_summary.py results/<folder> [window]`.

**Run-name grammar** (from 2026-10-25): folder `<topic>[_v<N>]`; condition `<stage>[<variant>]`, where
stage is H0–H6 (fixed policy) or E0–E3 (economy), and variant lists overrides as short tokens
(`pv100` plantValue 1.0, `a0.02` herderAlarm, `p120` foodPatches, `loose` refetchRunOffs 2, `h1e-4`
heapSeed …), defined in the entry's settings line.

Entry template:
```
## [PRE-REGISTERED YYYY-MM-DD] <question in one line>
**Question:** what we are trying to find out.
**Settings:** settings file, code commit, overrides that matter, years, seeds, window.
**Method:** how measured (batch / probe), what metric.
**RAW RESULTS:** _[pending]_ → numbers only, added when the data is in.
```
```
## YYYY-MM-DD — CONCLUSIONS: <entry it concludes>
**Conclusion:** what it means / what standard it sets / what to do next.
```

## [PRE-REGISTERED 2026-10-25] Rebuild attribution, stage A: commit walk from v1 to today
**Question:** which of the changes made since model v1 produced which changes in results? (With Chris:
we made many changes at once in the rebuild, then patched the problems one by one, without asking
what each change did.) Branch `diag/rebuild-attribution`.
**Settings:**
- Code points (each run on its own code and its own defaults, in a git worktree):
  `11f9f07` v1 final (opportunity culling, rut guarding) · `ed2d739` rebuild 1–2 (reproductive cost of
  the genome, oestrous cycles, sequential-assessment contests) · `4acd39c` rebuild 3 (sub-day ticks,
  spatial mating replacing wildBuckRate, walking herds/kids/captives, wolf prey switching on own
  success, foragers + fodder store, herder load replacing the herd cap, record-based keep value,
  maternal fear) · `7d0c4f4` rebuild 4 (capture and retrieval as approach tests) · `4e854d9` lean
  forage quality · `7b7e356` calibration (growthAbs 0.0035, breedSizeFrac 0.8) · `b381d31` cold-check
  fixes + offtake 10%/y + keep horizon 3 · `4360353` crepuscular wolves, goats flee wolves · `7aac26c`
  today (main: + loose run-offs, gatherers claim cells and weigh distance, refetch etc.; economy off).
- Conditions: v1's condition overrides (from `11f9f07:tools/conditions.json`), the same at every point:
  H0 `humansPerCamp 0`; H1 `herdingAt 1e9`; H3 `herdingAt 400, cullRule opportunity, penning 0`;
  H5 `herdingAt 400, cullRule opportunity, penning 1, guarding 1, provision 0.6, kidShelter 1,
  buckManagement 1, tetherNew 1`. Settings file `tools/attr_conditions.json`.
- 800 years, seeds 1–4, window: last 100 years.
**Method:** `tools/attr_batch.mjs` runs every (code point, condition, seed) with that code point's own
`tools/runyears.mjs`; outputs `results/attr/<commit>/<cond>_seed<N>.json`. Metrics per condition,
means over seeds (per-seed where it matters): goats; herded; wild R and herd − wild R; wild and herd
mean of S, B, A; herd − wild B; herd and wild IBD (herdF, wildF); wild-sired share of herd births;
H5 herd kill-off (males dead < 2.5 y; does past 2.5 y; share past 4 y).
**Stage B (if one code point carries a change):** split that commit into its parts with switches,
pre-registered as its own entry.
**RAW RESULTS** (2026-10-25, 144/144 runs, 0 failed; `python tools/attr_table.py results/attr 100 <commits>`):

results: results/attr | window: last 100 y | means over seeds (per seed in brackets)

#### H0
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11f9f07 | 4 | 547 | 0 (0 0 0 0) | 0.58 | — (— — — —) | 0.39 | 0.85 | 0.84 | — | — / 0.13 | — | — | — | — |
| ed2d739 | 4 | 723 | 0 (0 0 0 0) | 0.45 | — (— — — —) | 0.27 | 0.85 | 0.59 | — | — / 0.09 | — | — | — | — |
| 4acd39c | 4 | 669 | 0 (0 0 0 0) | 0.56 | — (— — — —) | 0.20 | 0.86 | 0.49 | — | — / 0.09 | — | — | — | — |
| 7d0c4f4 | 4 | 669 | 0 (0 0 0 0) | 0.56 | — (— — — —) | 0.20 | 0.86 | 0.49 | — | — / 0.09 | — | — | — | — |
| 4e854d9 | 4 | 357 | 0 (0 0 0 0) | 0.73 | — (— — — —) | 0.37 | 0.88 | 0.76 | — | — / 0.13 | — | — | — | — |
| 7b7e356 | 4 | 376 | 0 (0 0 0 0) | 0.64 | — (— — — —) | 0.34 | 0.89 | 0.77 | — | — / 0.15 | — | — | — | — |
| b381d31 | 4 | 385 | 0 (0 0 0 0) | 0.60 | — (— — — —) | 0.33 | 0.91 | 0.77 | — | — / 0.15 | — | — | — | — |
| 4360353 | 4 | 506 | 0 (0 0 0 0) | 0.65 | — (— — — —) | 0.22 | 0.91 | 0.76 | — | — / 0.12 | — | — | — | — |
| 7aac26c | 4 | 506 | 0 (0 0 0 0) | 0.65 | — (— — — —) | 0.22 | 0.91 | 0.76 | — | — / 0.12 | — | — | — | — |

#### H1
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11f9f07 | 4 | 275 | 0 (0 0 0 0) | 0.57 | — (— — — —) | 0.36 | 0.82 | 0.74 | — | — / 0.27 | — | — | — | — |
| ed2d739 | 4 | 525 | 0 (0 0 0 0) | 0.39 | — (— — — —) | 0.32 | 0.85 | 0.53 | — | — / 0.12 | — | — | — | — |
| 4acd39c | 4 | 561 | 0 (0 0 0 0) | 0.78 | — (— — — —) | 0.25 | 0.84 | 0.56 | — | — / 0.11 | — | — | — | — |
| 7d0c4f4 | 4 | 561 | 0 (0 0 0 0) | 0.78 | — (— — — —) | 0.25 | 0.84 | 0.56 | — | — / 0.11 | — | — | — | — |
| 4e854d9 | 4 | 290 | 0 (0 0 0 0) | 0.91 | — (— — — —) | 0.36 | 0.88 | 0.76 | — | — / 0.15 | — | — | — | — |
| 7b7e356 | 4 | 310 | 0 (0 0 0 0) | 0.90 | — (— — — —) | 0.34 | 0.90 | 0.75 | — | — / 0.17 | — | — | — | — |
| b381d31 | 4 | 316 | 0 (0 0 0 0) | 0.91 | — (— — — —) | 0.35 | 0.90 | 0.77 | — | — / 0.17 | — | — | — | — |
| 4360353 | 4 | 422 | 0 (0 0 0 0) | 0.86 | — (— — — —) | 0.22 | 0.90 | 0.76 | — | — / 0.14 | — | — | — | — |
| 7aac26c | 4 | 421 | 0 (0 0 0 0) | 0.86 | — (— — — —) | 0.20 | 0.90 | 0.76 | — | — / 0.14 | — | — | — | — |

#### H3
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11f9f07 | 4 | 322 | 61 (58 63 70 52) | 0.59 | -0.30 (-0.38 -0.27 -0.25 -0.31) | 0.22 | 0.80 | 0.69 | -0.07 | 0.49 / 0.28 | 0.05 | 0.76 | 0.77 | 0.27 |
| ed2d739 | 4 | 564 | 77 (77 78 74 80) | 0.45 | -0.19 (-0.16 -0.24 -0.18 -0.19) | 0.27 | 0.84 | 0.56 | -0.20 | 0.31 / 0.12 | 0.05 | 0.72 | 0.67 | 0.19 |
| 4acd39c | 4 | 831 | 327 (323 334 319 332) | 0.59 | -0.32 (-0.27 -0.35 -0.34 -0.31) | 0.24 | 0.87 | 0.35 | +0.03 | 0.38 / 0.19 | 0.02 | 0.75 | 0.65 | 0.27 |
| 7d0c4f4 | 4 | 856 | 326 (324 325 330 324) | 0.59 | -0.26 (-0.24 -0.27 -0.28 -0.26) | 0.29 | 0.88 | 0.27 | +0.02 | 0.26 / 0.14 | 0.02 | 0.72 | 0.66 | 0.28 |
| 4e854d9 | 4 | 414 | 130 (112 124 133 148) | 0.75 | -0.10 (-0.03 -0.06 -0.17 -0.13) | 0.41 | 0.88 | 0.60 | +0.00 | 0.39 / 0.25 | 0.01 | 0.29 | 0.89 | 0.59 |
| 7b7e356 | 4 | 400 | 110 (117 100 102 120) | 0.75 | -0.13 (-0.19 -0.07 -0.05 -0.21) | 0.41 | 0.92 | 0.58 | +0.01 | 0.41 / 0.25 | 0.02 | 0.35 | 0.60 | 0.42 |
| b381d31 | 4 | 407 | 117 (110 121 117 121) | 0.84 | -0.03 (-0.02 +0.01 -0.08 -0.03) | 0.30 | 0.89 | 0.78 | -0.01 | 0.31 / 0.16 | 0.04 | 0.59 | 0.66 | 0.34 |
| 4360353 | 4 | 430 | 8 (15 4 7 6) | 0.86 | -0.03 (-0.03 -0.02 -0.03 -0.03) | 0.17 | 0.90 | 0.75 | -0.00 | 0.16 / 0.14 | 0.40 | 0.36 | 0.69 | 0.47 |
| 7aac26c | 4 | 425 | 3 (3 3 3 2) | 0.86 | -0.03 (-0.03 -0.05 -0.03 -0.03) | 0.19 | 0.89 | 0.71 | -0.00 | 0.14 / 0.14 | 0.60 | 0.37 | 0.65 | 0.44 |

#### H5
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11f9f07 | 4 | 330 | 85 (86 84 89 83) | 0.66 | -0.44 (-0.37 -0.45 -0.49 -0.47) | 0.23 | 0.82 | 0.72 | -0.21 | 0.75 / 0.31 | 0.06 | 0.63 | 0.56 | 0.19 |
| ed2d739 | 4 | 526 | 87 (87 87 87 87) | 0.54 | -0.34 (-0.35 -0.29 -0.30 -0.43) | 0.26 | 0.85 | 0.57 | -0.41 | 0.69 / 0.17 | 0.05 | 0.76 | 0.60 | 0.16 |
| 4acd39c | 4 | 758 | 140 (132 144 142 142) | 0.84 | -0.69 (-0.74 -0.64 -0.66 -0.72) | 0.25 | 0.84 | 0.56 | +0.01 | 0.69 / 0.10 | 0.00 | 0.29 | 0.73 | 0.57 |
| 7d0c4f4 | 4 | 747 | 134 (133 130 140 133) | 0.84 | -0.66 (-0.66 -0.68 -0.60 -0.67) | 0.23 | 0.85 | 0.56 | +0.02 | 0.53 / 0.10 | 0.00 | 0.29 | 0.72 | 0.58 |
| 4e854d9 | 4 | 385 | 87 (44 107 106 92) | 0.86 | -0.40 (-0.10 -0.54 -0.53 -0.41) | 0.40 | 0.86 | 0.71 | -0.05 | 0.50 / 0.21 | 0.00 | 0.23 | 0.76 | 0.64 |
| 7b7e356 | 4 | 403 | 91 (88 93 89 93) | 0.85 | -0.49 (-0.49 -0.60 -0.52 -0.37) | 0.41 | 0.88 | 0.73 | -0.03 | 0.57 / 0.20 | 0.00 | 0.17 | 0.75 | 0.67 |
| b381d31 | 4 | 404 | 90 (90 89 92 90) | 0.89 | -0.09 (-0.04 -0.15 -0.08 -0.08) | 0.34 | 0.86 | 0.77 | -0.07 | 0.46 / 0.18 | 0.00 | 0.53 | 0.79 | 0.45 |
| 4360353 | 4 | 517 | 91 (92 86 90 95) | 0.85 | -0.03 (-0.05 -0.02 -0.01 -0.05) | 0.18 | 0.89 | 0.73 | -0.04 | 0.30 / 0.13 | 0.00 | 0.52 | 0.80 | 0.46 |
| 7aac26c | 4 | 505 | 89 (96 91 86 83) | 0.79 | -0.29 (-0.36 -0.32 -0.27 -0.22) | 0.21 | 0.86 | 0.77 | -0.09 | 0.44 / 0.19 | 0.01 | 0.68 | 0.74 | 0.33 |


## [PRE-REGISTERED 2026-10-25] Rebuild attribution, stage B: the herd cap and body size
**Question:** stage A shows herd − wild B (body size) in H5 at −0.21 (v1, 11f9f07) and −0.41 (ed2d739),
then about 0 from 4acd39c on. 4acd39c removed v1's herd cap (herdTarget 30 → 1e9, so no culling at
offtake 0) among other changes. Is the body-size result produced by cap-driven culling (keep value
counts "growth still to come", which favours smaller goats), or by something else in 4acd39c? The same
runs show whether the cap changes the herd R gap (−0.44 v1 vs −0.69 at 4acd39c).
**Settings:** `tools/attrB_conditions.json`: H5 (v1 overrides, as stage A) with `herdTarget 30` (cap,
v1's value) and `herdTarget 1e9` (no cap). Code points 11f9f07, ed2d739, 4acd39c, 7aac26c, each with
both conditions (at 11f9f07/ed2d739 `H5cap30` = their default, at 4acd39c/7aac26c `H5nocap` = theirs:
these four re-run stage A's cells as a seed check). 800 y, seeds 1–4, window last 100 y.
**Method:** `tools/attr_batch.mjs` → `results/attrB/<commit>/`; `tools/attr_table.py`; metrics as stage A,
with herd − wild B and herd − wild R the primary ones.
**RAW RESULTS** (2026-10-25, 32/32 runs, 0 failed; the four repeated stage-A cells reproduce it exactly):

results: results/attrB | window: last 100 y | means over seeds (per seed in brackets)

#### H5cap30
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11f9f07 | 4 | 330 | 85 (86 84 89 83) | 0.66 | -0.44 (-0.37 -0.45 -0.49 -0.47) | 0.23 | 0.82 | 0.72 | -0.21 | 0.75 / 0.31 | 0.06 | 0.63 | 0.56 | 0.19 |
| ed2d739 | 4 | 526 | 87 (87 87 87 87) | 0.54 | -0.34 (-0.35 -0.29 -0.30 -0.43) | 0.26 | 0.85 | 0.57 | -0.41 | 0.69 / 0.17 | 0.05 | 0.76 | 0.60 | 0.16 |
| 4acd39c | 4 | 713 | 85 (84 86 85 85) | 0.83 | -0.58 (-0.54 -0.58 -0.58 -0.62) | 0.29 | 0.83 | 0.57 | -0.32 | 0.92 / 0.10 | 0.00 | 0.60 | 0.42 | 0.16 |
| 7aac26c | 4 | 482 | 60 (51 54 61 74) | 0.81 | -0.17 (-0.10 -0.09 -0.13 -0.34) | 0.22 | 0.87 | 0.75 | -0.05 | 0.36 / 0.17 | 0.02 | 0.73 | 0.60 | 0.31 |

#### H5nocap
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 11f9f07 | 4 | 386 | 164 (177 161 170 149) | 0.67 | -0.49 (-0.52 -0.52 -0.50 -0.44) | 0.34 | 0.79 | 0.73 | +0.01 | 0.58 / 0.33 | 0.05 | 0.56 | 0.43 | 0.37 |
| ed2d739 | 4 | 671 | 277 (280 276 277 277) | 0.54 | -0.39 (-0.38 -0.40 -0.36 -0.42) | 0.29 | 0.85 | 0.56 | +0.06 | 0.29 / 0.16 | 0.05 | 0.49 | 0.51 | 0.46 |
| 4acd39c | 4 | 758 | 140 (132 144 142 142) | 0.84 | -0.69 (-0.74 -0.64 -0.66 -0.72) | 0.25 | 0.84 | 0.56 | +0.01 | 0.69 / 0.10 | 0.00 | 0.29 | 0.73 | 0.57 |
| 7aac26c | 4 | 505 | 89 (96 91 86 83) | 0.79 | -0.29 (-0.36 -0.32 -0.27 -0.22) | 0.21 | 0.86 | 0.77 | -0.09 | 0.44 / 0.19 | 0.01 | 0.68 | 0.74 | 0.33 |


## 2026-10-25 — CONCLUSIONS: rebuild attribution, stages A and B
**Conclusion:** (1) **Hunting raising wild R** is introduced by `4acd39c` (sub-day ticks; goats react to
hunters in real time): H1 − H0 wild R is −0.01 in v1 and −0.06 at ed2d739, then +0.22 at 4acd39c and
+0.18 to +0.26 after. v1's "neutral R, plastic fear" result rested on the once-a-day schedule.
(2) **The herd R gap was not lost in the rebuild**: H5 −0.44 (v1), −0.34, −0.69, −0.66, −0.40, −0.49
through 7b7e356. It collapses at `b381d31` (−0.09; the dusk-spook fix, bisected 2026-10-21), falls to
−0.03 with crepuscular wolves (`4360353`), and returns to −0.29 today (loose run-offs, b1e6adb, are the
change since). In every version the R gap is a retention filter: goats that run off or stray are
lost by the approach test. (3) **The body-size result is produced by the herd cap**: H5 herd − wild B
with herdTarget 30 is −0.21 / −0.41 / −0.32 / −0.05 (v1 / ed2d739 / 4acd39c / today) and without a cap
+0.01 / +0.06 / +0.01 / −0.09. With a binding cap the camp culls every surplus goat by keep value, which
counts growth still to come, so grown, large goats go first: harvest selection on size under heavy
culling. 4acd39c made the cap optional (off), which is why B's signal disappears there. (4) **Herd
size**: the cap's removal (4acd39c) lets herds grow (H3 61 → 327, H5 85 → 140); lean forage quality
(`4e854d9`) roughly halves goat numbers and herds; crepuscular wolves (`4360353`) all but end unpenned
H3 herds (117 → 8; 3 today). (5) **Wild-sired share** drops from v1's fixed 5% (wildBuckRate) to ~0
with spatial mating (4acd39c), by construction. (6) **Wild type**: the reproductive cost (`ed2d739`)
lowers wild R, S and A (0.58 / 0.39 / 0.84 → 0.45 / 0.27 / 0.59); lean forage quality raises them
again; crepuscular wolves lower S (0.33 → 0.22). (7) **Ganj Dareh**: v1's fit came with the cap's
culling; uncapped with no offtake (4acd39c–7b7e356) herds grow old (past 4 y 0.57–0.67); offtake
(b381d31) partly restores it; today males 0.68, does 0.74, past 4 y 0.33.
**For decisions (Chris):** whether intense culling belongs in the model (it is what selects on size);
whether real-time avoidance of hunters is wanted (it is what removed v1's plastic-fear result); and
the run-off mechanism and spook rate (they set the R gap).

## [PRE-REGISTERED 2026-10-27] Alarms and spooks as fear learning (restoring the plastic response?)
**Question:** (Chris) the rebuild added many hunter encounters per day (sub-tick alarms and flights),
but learned fear still rises only from attacks and witnessed kills. Being alarmed or spooked *is* a
fear response. If every alarm and spook sensitises the goat, does the response to hunting become
plastic again (fear rises, R stays near the no-hunting level), as in v1? Branch `exp/alarm-fear`
(from `diag/rebuild-attribution`, whose model code equals main 7aac26c).
**Settings:** new `alarmLearn` (share of an attack's sensitisation, 0.3 × R, applied per event): an
alarm from a hunter's presence, a stalk spotted, and a herder's spook each add `alarmLearn` to fear of
humans; an alarm from wolf scent adds it to fear of wolves. Levels 0.05 and 0.2 (0.015R / 0.06R per
event). Control: alarmLearn 0, checked bit-identical to stage A's 7aac26c cells, which serve as the
control. Conditions `tools/attr_conditions.json` H0, H1, H5 (v1 overrides); 800 y, seeds 1–4; window
last 100 y. Everything else at main's defaults.
**Method:** `tools/batch.mjs` per level → `results/alarmfear/a<level>/`; `tools/attr_table.py` with
learned fear columns. Primary: wild R in H1 vs H0; mean learned fear of humans and of wolves; H5 herd −
wild R.
**RAW RESULTS** (2026-10-27, 24/24 new runs, 0 failed; a0 = stage A 7aac26c cells, bit-identity checked over
450 y for H1 and H5 seed 1; `python tools/attr_table.py results/alarmfear 100 a0 a0.05 a0.2`):

results: results/alarmfear | window: last 100 y | means over seeds (per seed in brackets)

#### H0
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a0 | 4 | 506 | 0 (0 0 0 0) | 0.65 | — (— — — —) | 0.22 | 0.91 | 0.76 | — | — / 0.12 | — | 1.00 / — | 1.40 | — | — | — |
| a0.05 | 4 | 563 | 0 (0 0 0 0) | 0.55 | — (— — — —) | 0.19 | 0.91 | 0.70 | — | — / 0.10 | — | 1.00 / — | 1.73 | — | — | — |
| a0.2 | 4 | 617 | 0 (0 0 0 0) | 0.42 | — (— — — —) | 0.17 | 0.91 | 0.70 | — | — / 0.10 | — | 1.00 / — | 2.47 | — | — | — |

#### H1
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a0 | 4 | 421 | 0 (0 0 0 0) | 0.86 | — (— — — —) | 0.20 | 0.90 | 0.76 | — | — / 0.14 | — | 1.10 / — | 1.09 | — | — | — |
| a0.05 | 4 | 469 | 0 (0 0 0 0) | 0.75 | — (— — — —) | 0.19 | 0.90 | 0.71 | — | — / 0.13 | — | 1.26 / — | 1.37 | — | — | — |
| a0.2 | 4 | 510 | 0 (0 0 0 0) | 0.65 | — (— — — —) | 0.21 | 0.91 | 0.73 | — | — / 0.12 | — | 1.64 / — | 2.23 | — | — | — |

#### H5
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a0 | 4 | 505 | 89 (96 91 86 83) | 0.79 | -0.29 (-0.36 -0.32 -0.27 -0.22) | 0.21 | 0.86 | 0.77 | -0.09 | 0.44 / 0.19 | 0.01 | 0.93 / 0.14 | 1.18 | 0.68 | 0.74 | 0.33 |
| a0.05 | 4 | 562 | 103 (100 100 103 107) | 0.73 | -0.36 (-0.32 -0.41 -0.34 -0.38) | 0.20 | 0.85 | 0.69 | -0.24 | 0.47 / 0.15 | 0.01 | 1.01 / 0.15 | 1.48 | 0.53 | 0.74 | 0.40 |
| a0.2 | 4 | 584 | 94 (87 94 98 96) | 0.63 | -0.24 (-0.18 -0.26 -0.27 -0.26) | 0.23 | 0.89 | 0.68 | -0.06 | 0.37 / 0.13 | 0.03 | 1.30 / 0.33 | 2.30 | 0.58 | 0.77 | 0.40 |


## [PRE-REGISTERED 2026-10-27] Alarm-driven fear with learning not scaled by R
**Question:** with alarms sensitising fear (alarmLearn 0.2), hunting still raised wild R by +0.23
(entry below). Fear learned per event scales with R (0.3 × R × weight), so high-R goats in hunted areas
also learn faster, which may compound R's advantage. If every goat learns the same from the same event,
does hunting's effect on wild R fall toward zero? (Chris: "sometimes compounding like this is wrong.")
**Settings:** new `fearLearnR` 0 (learning uses `fearLearnRef` 0.6 for every goat instead of its R; 1 =
today), applied to all fear learning (attacks, witnessed kills, alarms, spotted stalks, spooks).
alarmLearn 0.2. `tools/alarmfear_0.2_const.json`: H0, H1, H5 (v1 overrides); 800 y, seeds 1–4; window
last 100 y. Code: `exp/alarm-fear`.
**Method:** `tools/batch.mjs` → `results/alarmfear/a0.2c/`; `tools/attr_table.py`, compared with a0 and a0.2.
Primary: H1 − H0 wild R; learned fears; H5 herd − wild R.
**RAW RESULTS** (2026-10-27, 12/12 runs, 0 failed; `python tools/attr_table.py results/alarmfear 100 a0 a0.2 a0.2c`):

results: results/alarmfear | window: last 100 y | means over seeds (per seed in brackets)

#### H0
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a0 | 4 | 506 | 0 (0 0 0 0) | 0.65 | — (— — — —) | 0.22 | 0.91 | 0.76 | — | — / 0.12 | — | 1.00 / — | 1.40 | — | — | — |
| a0.2 | 4 | 617 | 0 (0 0 0 0) | 0.42 | — (— — — —) | 0.17 | 0.91 | 0.70 | — | — / 0.10 | — | 1.00 / — | 2.47 | — | — | — |
| a0.2c | 4 | 630 | 0 (0 0 0 0) | 0.36 | — (— — — —) | 0.16 | 0.90 | 0.71 | — | — / 0.09 | — | 1.00 / — | 2.78 | — | — | — |

#### H1
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a0 | 4 | 421 | 0 (0 0 0 0) | 0.86 | — (— — — —) | 0.20 | 0.90 | 0.76 | — | — / 0.14 | — | 1.10 / — | 1.09 | — | — | — |
| a0.2 | 4 | 510 | 0 (0 0 0 0) | 0.65 | — (— — — —) | 0.21 | 0.91 | 0.73 | — | — / 0.12 | — | 1.64 / — | 2.23 | — | — | — |
| a0.2c | 4 | 510 | 0 (0 0 0 0) | 0.62 | — (— — — —) | 0.16 | 0.90 | 0.71 | — | — / 0.12 | — | 1.60 / — | 2.14 | — | — | — |

#### H5
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| a0 | 4 | 505 | 89 (96 91 86 83) | 0.79 | -0.29 (-0.36 -0.32 -0.27 -0.22) | 0.21 | 0.86 | 0.77 | -0.09 | 0.44 / 0.19 | 0.01 | 0.93 / 0.14 | 1.18 | 0.68 | 0.74 | 0.33 |
| a0.2 | 4 | 584 | 94 (87 94 98 96) | 0.63 | -0.24 (-0.18 -0.26 -0.27 -0.26) | 0.23 | 0.89 | 0.68 | -0.06 | 0.37 / 0.13 | 0.03 | 1.30 / 0.33 | 2.30 | 0.58 | 0.77 | 0.40 |
| a0.2c | 4 | 590 | 95 (93 88 97 103) | 0.62 | -0.25 (-0.23 -0.21 -0.22 -0.35) | 0.16 | 0.89 | 0.69 | -0.09 | 0.34 / 0.13 | 0.04 | 1.27 / 0.32 | 2.27 | 0.57 | 0.75 | 0.41 |


## [PRE-REGISTERED 2026-10-27] Do herd escapees lower wild R?
**Question:** in H5 on today's code wild R is 0.79 against 0.86 in H1 (stage A); at 4360353 it was 0.85
against 0.86. The change since that touches herds is loose run-offs (b1e6adb), which raised escapes
(~18–19/y vs ~7/y). Do escapees carry the herd's lower R into the wild? If so, with loose run-offs off,
wild R in H5 should return to about H1's level.
**Settings:** `tools/escape_test.json`: H5 (v1 overrides) + `refetchRunOffs 0`; today's model code
(`exp/alarm-fear` with alarmLearn 0, fearLearnR 1 = main 7aac26c behaviour); 800 y, seeds 1–4; window
last 100 y. Control: stage A `results/attr/7aac26c/H5` (loose run-offs on).
**Method:** `tools/batch.mjs` → `results/escape/`; wild R, herd − wild R, herded, escapes/y.
**RAW RESULTS** (2026-10-27, 4/4 runs, 0 failed; loose_on = stage A 7aac26c H5, loose_off = results/escape):

results: C:\Users\Chris\AppData\Local\Temp/esc | window: last 100 y | means over seeds (per seed in brackets)

#### H5
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| loose_on | 4 | 505 | 89 (96 91 86 83) | 0.79 | -0.29 (-0.36 -0.32 -0.27 -0.22) | 0.21 | 0.86 | 0.77 | -0.09 | 0.44 / 0.19 | 0.01 | 0.93 / 0.14 | 1.18 | 0.68 | 0.74 | 0.33 |
| loose_off | 4 | 525 | 103 (103 102 104 104) | 0.84 | -0.06 (-0.04 -0.09 -0.05 -0.07) | 0.17 | 0.87 | 0.74 | -0.07 | 0.34 / 0.15 | 0.01 | 0.90 / 0.14 | 1.13 | 0.53 | 0.79 | 0.46 |

Escaped per year, last 100 y, per seed: loose on 20.8 21.5 23.6 25.6; loose off 7.7 6.6 8.2 7.6.


## [PRE-REGISTERED 2026-10-27] The opportunity cull and the last breeders' value (economy, E2)
**Question:** E2 herds stay at 7–8 goats because bad masting years leave ~20% of demand unmet and the
shortfall slaughter eats the herd to the last goats (`replace`). (a) If the last breeding doe and
last breeding buck are worth more to keep (still eaten in a shortfall, but last), does the herd
survive bad years and grow? (b) Does an opportunity cull (slaughter when keeping no longer pays)
change herd size, offtake, the R gap, and body size (herd − wild B)? Branch `exp/cull-core`.
**Settings:** `tools/cal_cullcore.json` on `replace`'s E2r (economy, 10 people/camp, plantValue 1,
sites redrawn yearly, no heap, no crop damage, spook 0.02, loose run-offs, penning, provision 0.6,
opportunity keep value): E2boost `lastBreederValue 2` (meat units; lastBreeders 1); E2cull `econCull 1`
(every `cullEvery` 30 d, slaughter goats with keep value + judgement noise < `cullThreshold` 0); E2both.
Control: `replace`'s E2r cells (switches off checked bit-identical over 450 y, seed 1). 800 y, seeds
1–3; window last 100 y.
**Method:** `tools/batch.mjs` → `results/cullcore/`; `tools/trial_summary.py`, `tools/attr_table.py`
(herded, herd − wild R and B, kill-off profile), plus slaughter by cause (opportunity vs shortfall).
**RAW RESULTS** (2026-10-27, 9/9 runs, 0 failed; E2 = replace E2r cells):

results: C:\Users\Chris\AppData\Local\Temp/cc | window: last 100 y | means over seeds (per seed in brackets)

#### E2
| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2 | 3 | 432 | 8 (8 7 8) | 0.87 | -0.02 (-0.02 -0.02 -0.03) | 0.31 | 0.89 | 0.76 | +0.00 | 0.14 / 0.14 | 0.35 | 1.10 / 0.20 | 1.10 | 0.38 | 0.67 | 0.45 |
| E2boost | 3 | 437 | 7 (7 7 7) | 0.87 | -0.02 (-0.02 -0.02 -0.03) | 0.28 | 0.88 | 0.79 | +0.00 | 0.13 / 0.13 | 0.33 | 1.11 / 0.20 | 1.10 | 0.35 | 0.69 | 0.44 |
| E2cull | 3 | 430 | 1 (2 1 1) | 0.89 | -0.03 (-0.02 -0.02 -0.04) | 0.31 | 0.89 | 0.77 | +0.00 | 0.14 / 0.14 | 0.93 | 1.12 / 0.32 | 1.07 | 0.39 | 0.64 | 0.49 |
| E2both | 3 | 436 | 3 (3 3 3) | 0.88 | -0.03 (-0.02 -0.03 -0.03) | 0.29 | 0.89 | 0.75 | -0.00 | 0.13 / 0.13 | 0.57 | 1.12 / 0.22 | 1.08 | 0.26 | 0.60 | 0.51 |

Last 100 y, means over seeds: slaughter/y (opportunity / shortfall), unmet %, herding share of labour, herd births/y:
E2 3.3 (0.0 / 3.3), 3.8%, 0.33, 1.7 · E2boost 3.0 (0.0 / 3.0), 3.6%, 0.31, 1.6 · E2cull 3.1 (2.6 / 0.5), 2.6%,
0.17, 0.3 · E2both 2.9 (1.9 / 1.0), 3.6%, 0.25, 0.7.


## [PRE-REGISTERED 2026-10-28] Shelf-life windows for every store, and herding's storage credit
**Question:** (With Chris.) Rate decay spoils some food at once and lets some keep forever; at
`plantSpoil` 0.3%/day the plant store lost ~56% of a harvest before the next. Replace every rate with a
shelf life (dated batches, eaten soonest-to-expire first, expired batches move on or are lost). With
plant food keeping 135 days the store no longer bridges harvest to harvest (fruiting window days
105–195; the last batch expires by ~day 330, the next ripens at 105): a lean-season gap of about four
months. (a) Does the gap appear (unmet demand by quarter, E1)? (b) In E2, is the herd's offtake in the
gap enough to keep herding without the old storage credit? The credit was `meatDecay` × stock (what
holding food alive saved against meat losing 5%/day); with drying, the honest counterfactual is dried
meat (30% lost once over 270 days ≈ 0.11%/day). Run both: the dried-meat credit and the old 5%.
Risk named in advance: return estimates decay over `returnTau` 30 d, so herding's return may peak in
the gap and fade through the harvest, and herders leave the herd before the next gap. Branch
`exp/store-windows` from `exp/cull-core` (37b29b4).
**Settings:** new switch `storeWindows` 1 (0 = the old rates, bit-identical), shelf lives (guesses, with
Chris): fresh meat `freshDays` 3, then dried at `dryValue` 0.7 keeping `dryDays` 270, then lost; plant
food `plantDays` 135, then slop; slop `slopDays` 14, then the dump heap (heapSeed 0: lost); cut fodder
`fodderDays` 270, then lost. People eat meat and plant food together, soonest-to-expire first (old
order: meat, then plant food). Herding's storage credit `storeCredit` × stock per day replaces
`meatDecay` × stock when windows are on. Settings file `tools/cal_windows.json`, on `replace`'s
conditions (economy, 10 people/camp, plantValue 1, sites redrawn yearly, no heap, no crop damage):
E1w = E1r + windows; E2w = E2r + windows, `storeCredit` 0.0011; E2w5 = E2r + windows, `storeCredit`
0.05. lastBreederValue 0, econCull 0. Controls: `replace`'s E1r and E2r cells. 800 y, seeds 1–3;
window last 100 y.
**Method:** `tools/batch.mjs` → `results/windows/`; `tools/attr_table.py` (herded, R and B gaps,
kill-off); a summary of the econ record: unmet % (whole year and by quarter), slaughter/y, herding
share of labour (whole year and by quarter), herd births/y, fu dried, dried meat lost, plant food to
slop, slop and fodder lost.
**RAW RESULTS** (2026-10-28, 15/15 runs, 0 failed; code b9f1a1e). Added to the plan: E1r and E2r re-run
on b9f1a1e into the same folder, for the quarter columns; their year records equal `replace`'s files
in every field the older code wrote (checked, seed 1, years 0/400/799). Before the batch:
`tools/storeprobe.mjs` (60 y, windows on) 302,280 checks, 0 failures (it fails 24,940 checks with
planted store bugs); windows off vs 37b29b4, E2r seed 1, 450 y: 0 differing years, histograms equal.

`python tools/store_table.py results/windows 100` (quarters: days 0–91 / 91–182 / 182–274 / 274–365;
dried … fodder lost: fu per camp-year):

| condition | n | herded | unmet % (Q1/Q2/Q3/Q4) | slaughter/y (Q1/Q2/Q3/Q4) | herding share (Q1/Q2/Q3/Q4) | herd births/y | dried | dried lost | plant → slop | slop → heap | fodder lost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1r | 3 | 0.0 | 2.4 (5.7/2.4/0.2/1.3) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 0 | 0 | 6863 | 6864 | 0 |
| E1w | 3 | 0.0 | 14.5 (39.2/16.1/0.5/2.2) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 50 | 0 | 7747 | 7747 | 0 |
| E2r | 3 | 7.6 | 3.8 (9.1/4.0/0.4/1.5) | 3.3 (2.2/0.7/0.0/0.4) | 0.33 (0.54/0.24/0.18/0.34) | 1.7 | 0 | 0 | 5602 | 5476 | 0 |
| E2w5 | 3 | 1.6 | 13.6 (36.6/16.3/0.3/1.3) | 3.0 (2.5/0.4/0.0/0.1) | 0.15 (0.31/0.10/0.06/0.15) | 0.1 | 41 | 0 | 7798 | 7778 | 592 |
| E2w | 3 | 1.3 | 14.3 (38.3/16.5/0.6/1.8) | 2.5 (2.1/0.3/0.0/0.1) | 0.08 (0.15/0.06/0.04/0.07) | 0.1 | 40 | 0 | 7589 | 7573 | 294 |

`python tools/trial_summary.py results/windows 100`:

| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1r | 3 | 800 | 426 | 0 (0 0 0) | 0.89 | — (— — —) | 2.4 | 0.73/0.27/0.00 |
| E1w | 3 | 800 | 426 | 0 (0 0 0) | 0.88 | — (— — —) | 14.5 | 0.73/0.27/0.00 |
| E2r | 3 | 800 | 432 | 8 (8 7 8) | 0.87 | -0.02 (-0.02 -0.02 -0.03) | 3.8 | 0.53/0.15/0.33 |
| E2w5 | 3 | 800 | 428 | 2 (1 2 2) | 0.87 | -0.02 (-0.02 -0.03 -0.03) | 13.6 | 0.66/0.19/0.15 |
| E2w | 3 | 800 | 426 | 1 (1 2 1) | 0.88 | -0.02 (-0.02 -0.02 -0.03) | 14.3 | 0.70/0.22/0.08 |

`tools/attr_table.py` (last 100 y): wild S / B / A — E1r 0.30/0.89/0.79, E1w 0.26/0.90/0.73, E2r
0.31/0.89/0.76, E2w 0.31/0.89/0.75, E2w5 0.29/0.89/0.72; herd − wild B E2r +0.00, E2w −0.00, E2w5
−0.00; wild-sired share E2r 0.35, E2w 1.00, E2w5 1.00; fear of humans (all / herd) E2r 1.10/0.20, E2w
1.13/0.31, E2w5 1.13/0.32; fear of wolves 1.07–1.10 in all; kill-off (males dead < 2.5 y / does past
2.5 y / past 4 y) E2r 0.38/0.67/0.45, E2w 0.38/0.73/0.51, E2w5 0.31/0.69/0.52.

## [PRE-REGISTERED 2026-10-28] Need-relative returns: a delivery counts for what the camp will eat
**Question:** (With Chris.) Under windows ~7,600 fu of plant food per camp-year expires uneaten, yet
gathering keeps ~70% of labour, because a gatherer's return counts every fu delivered. If a delivery
counts only for the food it adds to what the camp will actually eat, does labour leave gathering when
the store is full, and where does it go (hunting, herding)? Does the lean-season gap or the herd
change? Calibration of income against need (Chris: production per day vs 2.5 fu eaten per day; the
constants behind the trade-offs) is deliberately held back, so as not to muddy this.
**Settings:** new switch `needScore` 1 (needs `storeWindows` 1; 0 = off, bit-identical). Rule: at
delivery, the camp's human food (fresh meat, dried meat, plant food, as batches) is eaten forward
soonest-to-expire first at the daily demand D = people × need + groupSink, with nothing more coming in;
a batch expiring at e can feed the nights up to e (cap D × (e − today) on everything expiring by e);
fresh meat left uneaten is dried (× dryValue) and eaten later. A delivery's return = food eaten with it
− food eaten without it (so a hunted carcass that only displaces plant food that would then rot counts
for little). Applies to gathering and hunting returns; herding's return is unchanged (offtake + Δ stock
+ storeCredit × stock, storeCredit 0.0011). Settings file `tools/cal_needscore.json`: E1n = E1w +
needScore 1; E2n = E2w + needScore 1. Controls: `results/windows` E1w and E2w (same code with the
switch off; checked bit-identical before the batch). 800 y, seeds 1–3; window last 100 y.
**Method:** `tools/batch.mjs` → `results/needscore/`; `tools/store_table.py`, `tools/trial_summary.py`,
`tools/attr_table.py`; plus per camp-year: food gathered, eaten, returns per labour-day by role, and
labour-days by role.
**RAW RESULTS** (2026-10-28, 6/6 runs, 0 failed; code d832ce4). Before the batch: hand cases for
`eatenForward`/`marginalFood` 6/6 (store cap, marginal into empty and full stores, fresh meat drying, a
carcass into a full plant store); needScore 0 vs `results/windows` E2w and E2r, seed 1, 450 y: 0
differing years. One-seed 450-y preview run before launching (not part of the table).

`python tools/role_books.py` (per camp-year, last 100 y, 3 seeds; controls from `results/windows`,
whose code did not record scored values or meat hunted: —):

| condition | n | demand | gathered (scored) | hunted (scored) | plant eaten | meat eaten | unmet | labour-days gather/hunt/herd | return per labour-day gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|---|
| E1n | 3 | 9000 | 15446 (7525) | 330 (174) | 7396 | 303 | 1301 | 2801/799/0 | 2.69/0.22/— |
| E1w | 3 | 9000 | 15113 (—) | — (—) | 7367 | 326 | 1307 | 2623/977/0 | 5.76/0.36/— |
| E2n | 3 | 9000 | 15133 (7517) | 258 (140) | 7418 | 281 | 1301 | 2604/569/427 | 2.89/0.25/0.09 |
| E2w | 3 | 9000 | 15005 (—) | — (—) | 7423 | 289 | 1288 | 2533/775/292 | 5.92/0.36/0.09 |

`python tools/store_table.py`:

| condition | n | herded | unmet % (Q1/Q2/Q3/Q4) | slaughter/y (Q1/Q2/Q3/Q4) | herding share (Q1/Q2/Q3/Q4) | herd births/y | dried | dried lost | plant → slop | slop → heap | fodder lost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1n | 3 | 0.0 | 14.5 (39.2/16.5/0.4/1.6) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 44 | 0 | 8047 | 8045 | 0 |
| E1w | 3 | 0.0 | 14.5 (39.2/16.1/0.5/2.2) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 50 | 0 | 7747 | 7747 | 0 |
| E2n | 3 | 1.8 | 14.5 (38.6/16.7/0.7/1.8) | 3.4 (2.8/0.4/0.0/0.1) | 0.12 (0.23/0.08/0.05/0.11) | 0.1 | 34 | 0 | 7714 | 7689 | 526 |
| E2w | 3 | 1.3 | 14.3 (38.3/16.5/0.6/1.8) | 2.5 (2.1/0.3/0.0/0.1) | 0.08 (0.15/0.06/0.04/0.07) | 0.1 | 40 | 0 | 7589 | 7573 | 294 |

`tools/trial_summary.py`: goats E1n 423, E1w 426, E2n 437, E2w 426; herded E2n 2 (2 2 2), E2w 1 (1 2 1);
wild R 0.88 in all; herd − wild R E2n −0.02 (−0.03 −0.02 −0.02), E2w −0.02. `tools/attr_table.py`: wild
S/B/A E1n 0.28/0.90/0.72, E1w 0.26/0.90/0.73, E2n 0.30/0.89/0.73, E2w 0.31/0.89/0.75; wild-sired share
E2n 0.92, E2w 1.00; fear of humans (all / herd) E2n 1.12/0.34, E2w 1.13/0.31.

## [PRE-REGISTERED 2026-10-28] kcal units, then data values where goats and people meet
**Question:** (With Chris: "recalibrate to 1 fu = 1 kcal; adjust the rest to fit.") Energy was in forage
units (fu) with no real anchor. Goat metabolism and human need were set separately, so the model held two
implicit scales: goat-world 1 fu ≈ 3,600 kcal (maintenance 0.6 fu vs ~2,200 kcal ME/day for a 50 kg goat,
NRC-style 117 kcal/kg^0.75) and human-world 1 fu ≈ 900 kcal (need 2.5 fu vs Hadza adults' mean TEE ~2,260;
Pontzer et al. 2012). Step 1 rescales each world by its own factor, which keeps the dynamics. Step 2 sets
data values at the three places the worlds meet, where the old units implied a ratio nobody chose:
(a) a goat carcass, `meatYield` 36,000 → 30,000 kcal per unit size (size 1 ≈ 50 kg; ~50–55% edible
including offal; raw goat 1,090 kcal/kg, USDA SR 175303); (b) slop, `slopValue` 4 → 1 (the old 1 fu → 1 fu
turned 900 kcal of spoiled food into 3,600 kcal of goat feed; energy is at most conserved); (c) a fodder
cutter's load, `forageLoad` 72,000 → 36,000 kcal (≈ 60 kg of fresh browse at ~600 kcal ME/kg, two
headloads; goats eat up to ~6 kg fresh a day; the least-sourced of the three). Which, if any, moves the
herd, the lean-season gap, labour, or the R gap?
**Settings:** Step 1 (rescale, branch `exp/kcal` from `exp/store-windows` 05e99e2): goat world × 3,600
(`vegK` 1,440,000; `goatIntake` 5,760; `maintBase` 2,160; `reserveMax` 216,000; `growthCost` 216,000;
`kidMilkNeed` 2,160; `milkBase` 2,160; `gestationCost` 540; `displayCost` 180; `contactCost` 540;
`forageCut` 14,400; `forageLoad` 72,000; `provision` in conditions 0.6 → 2,160); human world × 900
(`needPerPerson` 2,250; `meatYield` 36,000; `foodSiteK` 720,000; new `foodCut` 3,600 and `foodLoad`
18,000, split from forageCut/forageLoad, which gatherers and fodder cutters had shared); `slopValue` 4;
the forager's cell-choice constants (0.01 × distance, 0.001 × noise) now in units of the cut. Old
settings files (`provision` 0.6 etc.) are in fu and valid only at earlier commits. Check before step 2:
powers-of-two rescale (× 4,096 goat, × 1,024 human) must reproduce the old code bit for bit (E2w, E2r,
H5, seed 1, 430 y), and the new code in old units likewise. Step 2: `tools/cal_kcal.json`: E1k, E2k
(step 1 only; should match `results/windows` E1w, E2w within seed noise); E1kM, E2kM (meatYield 30,000);
E2kS (slopValue 1); E2kF (forageLoad 36,000); E2kd (all three). needScore off, storeCredit 0.0011. 800
y, seeds 1–3; window last 100 y.
**Method:** `tools/batch.mjs` → `results/kcal/`; `tools/store_table.py`, `tools/role_books.py`,
`tools/trial_summary.py`, `tools/attr_table.py`.
**Check before step 2** (2026-10-28, seed 1, 430 y): new code in old units vs 05e99e2: 0 differing years
in E2w, E2r, H5. Powers-of-two rescale vs new code in old units: every non-energy field identical in all
430 years (goats, traits, deaths, herds, kill-off, IBD …), every energy field equal × 4,096 or × 1,024 up
to the record's 0.1 rounding, except `econ.hunted`, which exposed a bug: from d832ce4 the meat-delivered
counter `ys.hunted` shared its name with the count of hunting kills, so the field was kcal + kills (the
dynamics never read it). Renamed `meatHunted`. Correction to the need-relative entry above: its "hunted"
column includes ~8 kills per camp-year on top of the meat (about 2–3% high); the scored column is right.
**RAW RESULTS** (2026-10-28, 21/21 runs, 0 failed; code 682aa9b; energy in kcal; attr rows in condition
order E1k, E1kM, E2k, E2kF, E2kM, E2kS, E2kd).

`python tools/store_table.py results/kcal 100` (dried … fodder lost: kcal per camp-year):

| condition | n | herded | unmet % (Q1/Q2/Q3/Q4) | slaughter/y (Q1/Q2/Q3/Q4) | herding share (Q1/Q2/Q3/Q4) | herd births/y | dried | dried lost | plant → slop | slop → heap | fodder lost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1k | 3 | 0.0 | 14.7 (39.6/16.2/0.5/2.3) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 43049 | 0 | 28045657 | 28044576 | 0 |
| E1kM | 3 | 0.0 | 14.7 (40.0/16.6/0.4/1.6) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 29002 | 5 | 28560817 | 28554027 | 0 |
| E2k | 3 | 1.4 | 14.1 (37.8/16.4/0.3/1.7) | 2.6 (2.1/0.4/0.0/0.1) | 0.08 (0.15/0.07/0.04/0.07) | 0.0 | 35702 | 19 | 27986454 | 27916253 | 1081655 |
| E2kM | 3 | 1.3 | 14.4 (39.0/16.7/0.4/1.4) | 2.3 (2.0/0.3/0.0/0.0) | 0.08 (0.14/0.06/0.04/0.07) | 0.0 | 22211 | 0 | 27811974 | 27746543 | 794918 |
| E2kS | 3 | 1.3 | 14.2 (37.3/16.4/0.4/2.7) | 2.3 (1.9/0.4/0.0/0.0) | 0.08 (0.14/0.06/0.04/0.07) | 0.1 | 38306 | 18 | 7003670 | 6936628 | 942697 |
| E2kF | 3 | 1.3 | 14.3 (38.6/16.4/0.3/1.9) | 2.4 (2.0/0.3/0.0/0.0) | 0.08 (0.15/0.06/0.04/0.07) | 0.0 | 34166 | 0 | 27487490 | 27429896 | 625411 |
| E2kd | 3 | 1.4 | 14.5 (38.8/16.6/0.5/1.9) | 2.6 (2.3/0.3/0.0/0.0) | 0.08 (0.15/0.07/0.04/0.07) | 0.0 | 24356 | 0 | 6954447 | 6879813 | 530989 |

`python tools/role_books.py results/kcal 100` (kcal per camp-year; "hunted" = meatHunted):

| condition | n | demand | gathered (scored) | hunted (scored) | plant eaten | meat eaten | unmet | labour-days gather/hunt/herd | return per labour-day gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|---|
| E1k | 3 | 8100000 | 13646205 (13646205) | 299398 (299398) | 6632346 | 280929 | 1186725 | 2658/942/0 | 5134.59/317.73/— |
| E1kM | 3 | 8100000 | 13823626 (13823626) | 250195 (250195) | 6673062 | 237752 | 1189186 | 2661/939/0 | 5194.71/266.48/— |
| E2k | 3 | 8100000 | 13694798 (13694798) | 251354 (251354) | 6696830 | 263817 | 1139353 | 2539/763/298 | 5394.30/329.32/78.57 |
| E2kM | 3 | 8100000 | 13668846 (13668846) | 207779 (207779) | 6717348 | 219161 | 1163490 | 2572/755/273 | 5315.10/275.16/61.67 |
| E2kS | 3 | 8100000 | 13692711 (13692711) | 261159 (261159) | 6678437 | 269972 | 1151591 | 2550/769/281 | 5370.14/339.66/71.98 |
| E2kF | 3 | 8100000 | 13557162 (13557162) | 242863 (242863) | 6688922 | 253104 | 1157974 | 2561/752/286 | 5293.41/322.74/71.03 |
| E2kd | 3 | 8100000 | 13656809 (13656809) | 212737 (212737) | 6700974 | 226760 | 1172266 | 2560/751/289 | 5335.47/283.18/70.97 |

`tools/trial_summary.py`: goats E1k 425, E1kM 421, E2k 432, E2kM 424, E2kS 433, E2kF 427, E2kd 430;
herded (per seed) E2k 1 (1 1 2), E2kM 1 (1 1 1), E2kS 1 (1 1 2), E2kF 1 (1 1 1), E2kd 1 (1 1 2); wild R
0.88–0.89; herd − wild R −0.02 to −0.03; gather/hunt/herd E1 0.74/0.26/0.00, E2 0.71/0.21/0.08 in every
E2 condition. `tools/attr_table.py`: wild S/B/A E1k 0.33/0.90/0.75, E1kM 0.29/0.89/0.76, E2k
0.27/0.90/0.75, E2kF 0.27/0.90/0.79, E2kM 0.29/0.89/0.76, E2kS 0.26/0.90/0.75, E2kd 0.30/0.89/0.77;
wild-sired share 0.96–1.00; kill-off (males dead < 2.5 y / does past 2.5 y / past 4 y) E2k
0.31/0.68/0.51, E2kF 0.29/0.70/0.51, E2kM 0.33/0.68/0.50, E2kS 0.33/0.71/0.50, E2kd 0.30/0.64/0.45.
Reference (old units, same dynamics): `results/windows` E1w unmet 14.5%, E2w herded 1.3, unmet 14.3%.

## [PRE-REGISTERED 2026-10-28] Seen gathering: the return gatherers predict from the food they can see
**Question:** (With Chris: "gather return reflecting what they can see and predict is good.") About a
third of gatherer-days fall in months with nothing ripe (days 0–90 average 0 kcal, ~70k gatherer-days per
60 y in the probe), because gathering's return is remembered with a 30-day decay and roles are chosen in
proportion to returns. If gathering is judged from the ripe food a camp can see and from what it would add
to what the camp will eat, does labour leave gathering in the empty months, where does it go, and does the
lean-season gap or the herd change?
**Settings:** branch `exp/gather-hunt` (from `exp/kcal`): new switch `gatherSee` 1 (0 = off; checked
bit-identical to `results/kcal` E2k, seed 1, 430 y, before the batch). Each morning a camp sums the ripe
food standing on sites within `forageRange`; shared among yesterday's gatherers (at least one), each can
bring home up to `foodLoad`; that load is valued with `needScore` (what it adds to the food the camp will
eat). This replaces gathering's remembered return in the role choice; hunting and herding keep theirs.
Settings file `tools/cal_gathersee.json`: E1g = E1k + gatherSee 1 + needScore 1; E2g = E2k + gatherSee 1 +
needScore 1. Controls: `results/kcal` E1k, E2k (neither switch); needScore alone is `results/needscore`
E1n, E2n (old units, same dynamics). Ranged shots off. 800 y, seeds 1–3; window last 100 y.
**Method:** `tools/batch.mjs` → `results/gathersee/`; `tools/store_table.py`, `tools/role_books.py`,
`tools/trial_summary.py`, `tools/attr_table.py`; `tools/incomeprobe.mjs` (seed 1) for gatherer-days by
month.
**RAW RESULTS** (2026-10-28, 6/6 runs, 0 failed; code b0a7a01) — **INVALID** (see below): switch-off check
0 differing years. store_table: E1g herded 0.0, unmet 14.5% (39.7/15.8/0.6/1.9), hunting share of labour
0.32; E2g herded 1.7, unmet 14.1% (38.0/16.0/0.6/1.9), slaughter 3.3/y, herding share 0.14
(0.40/0.09/0.04/0.04), herd births 0.1/y. role_books: E1g gather/hunt/herd labour-days 2453/1147/0, E2g
2381/707/512. incomeprobe (E1g, seed 1, years 340–400): gatherer-days by 30-day block 2662 / 2739 / 2690
/ 26792 / 50724 / 50770 / 50966 / 51033 / 51079 / 51048 / 50774 / 50258, mean load in the last three
blocks 1,084 / 40 / 0 kcal. **Invalid:** the predictor summed all ripe food in the 13 × 13 cells around
camp, including food beyond a day's reach (a gatherer cuts only for the sub-ticks left after walking out),
so it kept predicting full loads in autumn from far, unreachable sites. Fixed in the entry below.

## [PRE-REGISTERED 2026-10-28] Seen gathering v2: predicted from the cells a gatherer can work in a day
**Question:** as above. **Settings:** as above, except the predictor (code after b0a7a01): for each food
site within forageRange, a day's load there = min(foodLoad, foodCut × (daySteps − distance from camp), the
food there), as gatherers choose cells (claimForage); yesterday's gatherers (at least one) take the best
cells, one each; the mean of their loads, valued with needScore. Folder `results/gathersee_v2/`.
**Method:** as above.
**RAW RESULTS** (2026-10-28, 6/6 runs, 0 failed; code 77f846d; controls `results/kcal` E1k, E2k).

`python tools/store_table.py results/gathersee_v2 100`:

| condition | n | herded | unmet % (Q1/Q2/Q3/Q4) | slaughter/y (Q1/Q2/Q3/Q4) | herding share (Q1/Q2/Q3/Q4) | herd births/y | dried | dried lost | plant → slop | slop → heap | fodder lost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1g | 3 | 0.0 | 14.8 (40.7/16.1/0.6/1.9) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 51942 | 0 | 29031124 | 29031222 | 0 |
| E2g | 3 | 1.6 | 14.2 (38.4/16.0/0.6/1.9) | 2.6 (2.3/0.3/0.0/0.0) | 0.21 (0.35/0.09/0.05/0.34) | 0.0 | 42662 | 0 | 28270251 | 28197072 | 3819126 |

`python tools/role_books.py results/gathersee_v2 100` (kcal per camp-year):

| condition | n | demand | gathered (scored) | hunted (scored) | plant eaten | meat eaten | unmet | labour-days gather/hunt/herd | return per labour-day gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|---|
| E1g | 3 | 8100000 | 13876286 (6748387) | 303167 (152712) | 6618870 | 280844 | 1200286 | 1813/1787/0 | 3723.16/85.44/— |
| E2g | 3 | 8100000 | 13757909 (6785939) | 253008 (134568) | 6682866 | 264699 | 1152435 | 1743/1116/741 | 3894.36/120.57/37.46 |

`tools/trial_summary.py`: goats E1g 410, E2g 423; herded E2g 2 (1 2 2); wild R E1g 0.90, E2g 0.89; herd −
wild R E2g −0.02 (−0.02 −0.02 −0.02); gather/hunt/herd E1g 0.50/0.50/0.00, E2g 0.48/0.31/0.21.
`tools/attr_table.py`: wild S/B/A E1g 0.37/0.90/0.74, E2g 0.31/0.89/0.74; wild-sired 1.00; fear of
humans (all / herd) E1g 1.17, E2g 1.14/0.34; kill-off E2g 0.36/0.67/0.47. `tools/incomeprobe.mjs` (E1g,
seed 1, years 340–400): gatherer-days by 30-day block 2670 / 2662 / 2725 / 26669 / 50522 / 50631 / 50749 /
50367 / 48176 / 30945 / 6510 / 2757; mean load by block 0 / 0 / 0 / 10,416 / 11,161 / 11,137 / 9,779 /
6,764 / 4,058 / 1,677 / 407 / 12 kcal; hunter-days 322,617, 1 kill per 185 days, 208 kcal per hunter-day
(E1k, same probe on the kcal code without the switches: 1 kill per 105 days, 356 kcal per hunter-day).

## [PROBE 2026-10-28, not pre-registered] Ranged shots: wild goats after humans arrive
Code 9a3a5c6 (`shotChance`, `shotRange` 2), E1k settings, seed 1, `tools/incomeprobe.mjs 345 305`, wild
goats by year from 300 (humans arrive) and shots/kills per year:
shotChance 0: 500, 297, 297, 272, 252, 240 … 224 (310) … 312–374 (340–344); 1 kill per 105 hunter-days.
shotChance 0.1: 484 (1,884 shots, 79 kills), 142 (7,620 shots, 307 kills), 115, 71, 68, 76, 87, 50, 31 …
31 (310) … 1 (332–338).
shotChance 0.3: 325 (1,183 shots, 230 kills), 11 (1,019 shots, 198 kills), 10, 9 … 5–13 (308–318) … 30–50
(340–344).
Also, humansAt 5 (founding population), shotChance 0.3, gatherSee 1, needScore 1: goats 800 → 17–24 by
years 21–24.

## [PRE-REGISTERED 2026-10-29] Other game for hunters, and ranged shots at 1%
**Question:** (With Chris: "i think testing your other game idea is worth it. but also a smaller shot
chance. 10% sounds high to me. try 1%.") Hunters' only prey is ~420 wild goats shared by 30 people (about
0.03 goats per km² against 1.4–16 in bezoar surveys), so hunting returns ~85–120 kcal per hunter-day as
scored, and ranged shots at 10% drove the wild goats extinct (probe above). (1) If a hunting day that took
no goat can bring home other game, as the wolves' altPrey, does labour move to hunting in the lean
quarter, does the winter gap (Q1 unmet ~40%) close, and do herding and the herd change? (2) Do ranged shots
at 1% leave a wild population, with and without other game?
**Settings:** branch `exp/gather-hunt`, code after 687e373: new switches `altGame` (daily chance; 0 =
off) and `altYield` (kcal per carcass, default 36,000 = one adult goat). An economy hunter (not a
capturer) whose day ended without a goat kill brings home one other-game carcass with chance altGame; the
other game is not modelled as animals and is never depleted. Switch-off check: altGame 0 bit-identical to
687e373 (E2g settings, seed 1, 430 y; 0 differing years apart from the new altKills field). Value
altGame 0.03: Hadza men took a large carcass on about 1 hunter-day in 30 (Hawkes, O'Connell & Coxworth,
from Hawkes et al. 1991), and the model's goat kills run 1 per ~185 hunter-days, so goats plus other game
come to about 1 per 28. altYield 36,000 stands for a Zagros mix (gazelle smaller, red deer and boar
larger), set at a goat's carcass for want of a weighted mean. Settings file `tools/cal_altgame.json`:
E1a, E2a = E1g, E2g + altGame 0.03; E1s, E2s = + shotChance 0.01; E1as, E2as = both. Controls:
`results/gathersee_v2` E1g, E2g. 800 y, seeds 1–3; window last 100 y.
**Method:** `tools/batch.mjs` → `results/altgame/`; `tools/store_table.py`, `tools/role_books.py`,
`tools/trial_summary.py`; wild goats by year after humans arrive (300) from the year records, with shots,
shot kills and other-game kills per year.

**RAW RESULTS** (2026-10-29, 18/18 runs, 0 failed; code 90829f9 + EXPLOG fix; controls `results/gathersee_v2`
E1g, E2g).

`python tools/store_table.py results/altgame 100`, `python tools/role_books.py results/altgame 100` (kcal
per camp-year), `python tools/trial_summary.py results/altgame`:

results: results/altgame | window: last 100 y | means over seeds
| condition | n | herded | unmet % (Q1/Q2/Q3/Q4) | slaughter/y (Q1/Q2/Q3/Q4) | herding share (Q1/Q2/Q3/Q4) | herd births/y | dried | dried lost | plant → slop | slop → heap | fodder lost |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1a | 3 | 0.0 | 2.3 (4.1/4.6/0.1/0.3) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 474438 | 23235 | 31426340 | 31438389 | 0 |
| E1as | 3 | 0.0 | 2.6 (4.4/4.9/0.4/0.6) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 464400 | 15842 | 31738820 | 31728237 | 0 |
| E1s | 3 | 0.0 | 14.7 (41.1/16.0/0.4/1.4) | 0.0 (0.0/0.0/0.0/0.0) | 0.00 (0.00/0.00/0.00/0.00) | 0.0 | 47597 | 0 | 28221228 | 28216677 | 0 |
| E2a | 3 | 1.1 | 3.1 (6.0/5.4/0.3/0.6) | 1.3 (0.8/0.5/0.0/0.0) | 0.06 (0.07/0.04/0.04/0.10) | 0.1 | 421139 | 13913 | 30577569 | 30521861 | 986721 |
| E2as | 3 | 0.8 | 3.1 (6.1/5.7/0.2/0.4) | 1.0 (0.6/0.4/0.0/0.0) | 0.06 (0.07/0.04/0.04/0.08) | 0.0 | 418623 | 11133 | 29652621 | 29610065 | 569887 |
| E2s | 3 | 1.1 | 14.4 (39.1/16.2/0.7/1.6) | 2.1 (1.8/0.3/0.0/0.0) | 0.14 (0.22/0.06/0.04/0.22) | 0.0 | 39500 | 6 | 28211110 | 28144882 | 1690898 |

results: results/altgame | window: last 100 y | per camp-year, sums over seeds
| condition | n | demand | gathered (scored) | hunted (scored) | plant eaten | meat eaten | unmet | labour-days gather/hunt/herd | return per labour-day gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|---|
| E1a | 3 | 8100000 | 13637898 (6685294) | 2352653 (1228569) | 5789409 | 2125750 | 184842 | 1730/1870/0 | 3864.61/656.95/— |
| E1as | 3 | 8100000 | 13738196 (6687752) | 2308208 (1204420) | 5797804 | 2093035 | 209161 | 1726/1874/0 | 3875.65/642.56/— |
| E1s | 3 | 8100000 | 13703915 (6765985) | 282173 (142308) | 6644815 | 261850 | 1193335 | 1818/1782/0 | 3721.09/79.87/— |
| E2a | 3 | 8100000 | 13560772 (6703998) | 2124279 (1136810) | 5908938 | 1943101 | 247961 | 1662/1712/225 | 4032.87/663.95/48.20 |
| E2as | 3 | 8100000 | 13291383 (6690759) | 2149336 (1147367) | 5880557 | 1968886 | 250558 | 1650/1750/200 | 4054.39/655.68/35.30 |
| E2s | 3 | 8100000 | 13752489 (6792080) | 235518 (120821) | 6691546 | 241975 | 1166479 | 1748/1359/493 | 3886.30/88.93/43.57 |

results: results/altgame | window: last 100 y | seeds per condition in n
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1a | 3 | 800 | 416 | 0 (0 0 0) | 0.89 | — (— — —) | 2.3 | 0.48/0.52/0.00 |
| E1as | 3 | 800 | 401 | 0 (0 0 0) | 0.71 | — (— — —) | 2.6 | 0.48/0.52/0.00 |
| E1s | 3 | 800 | 417 | 0 (0 0 0) | 0.70 | — (— — —) | 14.7 | 0.51/0.49/0.00 |
| E2a | 3 | 800 | 415 | 1 (1 1 1) | 0.90 | -0.01 (-0.01 -0.01 -0.01) | 3.1 | 0.46/0.48/0.06 |
| E2as | 3 | 800 | 409 | 1 (1 1 1) | 0.71 | -0.01 (-0.01 -0.01 -0.02) | 3.1 | 0.46/0.49/0.06 |
| E2s | 3 | 800 | 434 | 1 (1 1 2) | 0.69 | -0.05 (-0.05 -0.07 -0.03) | 14.4 | 0.49/0.38/0.14 |

Wild goats (total − herded) by year from the year records, seeds 1/2/3, years 299, 300, 301, 302, 305,
310, 350, 400, 500, 600, 700, 799; then per year over the last 100 y (whole world): goat kills, shots, shot
kills, other-game kills.
E1a: 525 492 264 279 232 220 333 449 443 406 451 511 / 438 432 266 292 221 213 419 381 404 483 478 368 /
538 243 243 211 198 202 374 415 409 406 450 482; goat kills 28.8/26.2/25.4, other game 167/169/170.
E1s: 525 542 447 483 386 371 425 441 373 346 409 428 / 438 457 375 399 370 333 423 416 431 425 328 507 /
538 423 449 294 298 309 443 386 465 435 446 331; goat kills 21.7/22.0/24.7, shots 5558/5700/6137, shot
kills 21.6/21.9/24.5.
E1as: 525 552 393 436 360 459 382 310 420 441 421 394 / 438 457 394 424 415 501 405 474 391 460 392 362 /
538 400 418 341 310 318 417 372 402 423 392 444; goat kills 22.6/23.6/25.2, shots 5768/6060/6223, shot
kills 22.4/23.5/25.0, other game 169/167/167.
E2a: years ≤ 310 as E1a; 350 on 333 469 411 451 339 326 / 419 356 455 404 426 425 / 374 416 449 381 395
466; goat kills 19.4/24.8/25.6, other game 154/155/150.
E2s: years ≤ 310 as E1s; 350 on 425 439 409 425 559 403 / 423 428 371 489 443 467 / 443 368 398 372 383
456; goat kills 17.2/20.1/20.2, shots 4323/4827/4607, shot kills 17.1/20.0/19.9.
E2as: years ≤ 310 as E1as; 350 on 382 280 318 353 382 425 / 405 467 465 381 466 377 / 417 380 405 413 450
414; goat kills 22.0/21.6/24.0, shots 5458/5622/5829, shot kills 21.9/21.5/23.8, other game 155/157/156.

<!-- append new entries above this line -->

## [PRE-REGISTERED 2026-10-30] Stalk vs shot: does the hunting method change wild and herd R? (fixed policy)
**Question:** (With Chris, 2026-10-29/30: human behaviour is the controlled variable; "this will
probably impact the R right?") Under stalking a goat escapes only if it spots the hunter, which turns
on R, and wild R rises from ~0.67 before humans to ~0.87 under hunting. A ranged shot is taken before
the goat can spot the stalk, so R plays no part in who is hit. With hunting effort held equal (policy
fixed; kills are an outcome), how do wild R, learned fear, the herd and herd − wild R differ between
stalking and shooting?
**Settings:** main, code after 6bba7e9: the shot is ungated for fixed-policy hunters. Per attempt (at
most one per day sub-tick, huntAttempts 2): the capture draw first (captureRate 0.2, managing, herd
below target); an attempt that is not a capture try is a shot if a wild goat is seen within shotRange
2, else a stalk as before. `shots` and `shotKills` are written to the year record when shotChance > 0
and economy 0. Switch-off check: shotChance 0, H5 seed 1, 600 y, against 71752e3: 0 of 600 years differ
(params identical too). Settings file `tools/cal_shots.json`: H1, H5 as `tools/conditions.json`;
H1S, H5S = + shotChance 0.01 (the value tested in the economy, 2026-10-29). 800 y, seeds 1–10;
window last 100 y.
**Prior look (probe, not pre-registered, 2026-10-30):** H1S and H5S seed 1, 450 y, years 400–449:
wild goats 439/442, wild R 0.672/0.665, hunted 15.3/14.6 per year (shot kills 15.1/13.8), shots
2,089/1,771 per year, H5S herded 14.0, herd R 0.583, captured 1.4/y. Stalk-only seed 1 (results/
smoke_noecon, same years): wild R 0.868/0.855, hunted 18.7/19.4, H5 herded 30.3.
**Prediction:** wild R under shots stays near the pre-human value (~0.67) instead of rising to ~0.87;
kills somewhat fewer than under stalking. Herd − wild R: no prediction (the capture approach test still
favours calm goats, but from a calmer population).
**Method:** `node tools/batch.mjs tools/cal_shots.json results/shots 800 10` → `results/shots/`;
`python tools/trial_summary.py results/shots`; `python tools/shot_rows.py results/shots 100` (per-run window means of wild goats, wild R, herded,
herd R, hunted, shots, shot kills, captured); wild R by year after humans arrive.
**RAW RESULTS** (2026-10-31, 40/40 runs, 0 failed; code 89d7ab6). Correction to the settings above:
`tools/shot_rows.py` as committed in 89d7ab6 printed the all-goat mean R (herd included) as wild R, and the
probe's H5S "wild R 0.665" is that all-goat mean; fixed before these tables (herd taken out).

`PYTHONIOENCODING=utf-8 python tools/trial_summary.py results/shots`:

| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) |
|---|---|---|---|---|---|---|
| H1S | 10 | 800 | 435 | 0 | 0.68 | — |
| H1 | 10 | 800 | 425 | 0 | 0.86 | — |
| H5S | 10 | 800 | 528 | 102 (103 112 97 98 105 90 106 101 98 108) | 0.63 | -0.32 (-0.37 -0.30 -0.25 -0.28 -0.45 -0.12 -0.36 -0.39 -0.31 -0.41) |
| H5 | 10 | 800 | 506 | 89 (96 89 91 86 83 59 88 95 102 100) | 0.80 | -0.31 (-0.36 -0.24 -0.32 -0.27 -0.22 -0.14 -0.33 -0.38 -0.42 -0.44) |

Means of 10 seeds, years 700–799 (per year; R and fear are means over goats; per-run rows in
`results/shots/shot_rows.txt`):

| condition | wild goats | wild R | herded | herd R | hunted (deaths) | shots | shot kills | captured | captured R | fear of humans (all goats) | herd fear of humans | escaped + run-offs lost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | 425.2 | 0.861 | 0 | — | 18.2 | 0 | 0 | 0 | — | 1.104 | — | 0 |
| H1S | 435.0 | 0.678 | 0 | — | 15.0 | 2116.1 | 14.8 | 0 | — | 1.887 | — | 0 |
| H5 | 416.8 | 0.804 | 89.0 | 0.494 | 31.5 | 0 | 0 | 10.0 | 0.617 | 0.928 | 0.144 | 40.0 |
| H5S | 425.8 | 0.633 | 101.9 | 0.310 | 16.7 | 1814.4 | 14.3 | 4.2 | 0.437 | 1.447 | 0.139 | 20.7 |

Wild R by 50-year block (block start year; mean of 10 seeds):

| condition | 250 | 350 | 400 | 450 | 500 | 600 | 700 | 750 |
|---|---|---|---|---|---|---|---|---|
| H1 | 0.667 | 0.827 | 0.848 | 0.857 | 0.860 | 0.859 | 0.860 | 0.861 |
| H1S | 0.667 | 0.686 | 0.688 | 0.685 | 0.679 | 0.677 | 0.677 | 0.679 |
| H5 | 0.667 | 0.827 | 0.844 | 0.828 | 0.808 | 0.797 | 0.800 | 0.808 |
| H5S | 0.667 | 0.686 | 0.682 | 0.648 | 0.611 | 0.603 | 0.629 | 0.638 |

## [PRE-REGISTERED 2026-10-31] Fodder from the economy work in the fixed-policy table
**Question:** (With Chris, 2026-10-31: "let's do the two fodder and go with your shot off as default.")
Two fodder settings from the economy work go into the H conditions: cut fodder keeps for a shelf life
(storeWindows 1: fodderDays 270, then lost) instead of losing 0.5% a day (fodderSpoil 0.005), and a
cutter carries 36,000 kcal home instead of 72,000 (forageLoad; ~60 kg fresh browse at ~600 kcal ME/kg,
two headloads; see the kcal entry, 2026-10-28). What do they change in each condition? Fodder is fed
only where provision > 0 (H5), so the window acts there alone; cutting happens wherever humans are
(huntEffort 0.3, forageEffort 0.3 of non-herder days, H1 included) and removes the vegetation it cuts,
so the load acts in H1–H6. Shots stay off (shotChance 0, stalking) as the default.
**Settings:** main, code 7ec4c78 (no code change; overrides only). Settings file `tools/cal_fodder.json`:
H1–H6 as `tools/conditions.json`; H1f–H6f = + storeWindows 1, forageLoad 36000; H5L36 = H5 + forageLoad
36000 only (so H5f − H5L36 is the window's part). With economy 0, storeWindows touches only the fodder
store (stash, expire, provisioning draw); campEconomy, where the other stores age and are eaten, does
not run. 800 y, seeds 1–10; window last 100 y.
**Prediction:** H5: with the window, fodder cut in the growing season reaches the lean season whole
(at 0.5%/day about 41% survives 180 days), which roughly offsets the halved load, so fodder fed and
the herd change little. H1–H4, H6: small effects (less browse removed near camp). No prediction for R.
**Method:** `node tools/batch.mjs tools/cal_fodder.json results/fodder 800 10` → `results/fodder/`;
`python tools/trial_summary.py results/fodder`; per-condition window means of wild goats, wild R,
herded, herd R, fodder fed and fodder cut per year (year records `fodder`, `foraged`).
**RAW RESULTS** (2026-10-31, 130/130 runs, 0 failed; code 7ec4c78; fodder in kcal per year, all camps).

`PYTHONIOENCODING=utf-8 python tools/trial_summary.py results/fodder`:

results: results/fodder | window: last 100 y | seeds per condition in n
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H1 | 10 | 800 | 425 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.86 | — (— — — — — — — — — —) | — | — |
| H1f | 10 | 800 | 430 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.87 | — (— — — — — — — — — —) | — | — |
| H2 | 10 | 800 | 428 | 2 (3 2 3 2 3 2 3 3 2 2) | 0.86 | -0.02 (-0.02 -0.02 -0.04 -0.03 -0.03 -0.01 -0.02 -0.01 -0.01 -0.02) | — | — |
| H2f | 10 | 800 | 436 | 3 (3 3 3 3 2 3 3 4 3 3) | 0.86 | -0.02 (-0.03 -0.02 -0.03 -0.02 -0.02 -0.03 -0.02 -0.03 -0.02 -0.02) | — | — |
| H3 | 10 | 800 | 428 | 3 (3 3 3 3 2 3 3 3 3 3) | 0.86 | -0.03 (-0.03 -0.01 -0.05 -0.03 -0.03 -0.03 -0.04 -0.03 -0.03 -0.03) | — | — |
| H3f | 10 | 800 | 432 | 3 (2 3 3 3 2 4 3 3 3 3) | 0.86 | -0.03 (-0.04 -0.02 -0.04 -0.03 -0.03 -0.02 -0.04 -0.02 -0.03 -0.02) | — | — |
| H4 | 10 | 800 | 428 | 3 (3 3 3 4 3 4 3 3 3 3) | 0.86 | -0.03 (-0.02 -0.03 -0.02 -0.04 -0.03 -0.03 -0.02 -0.02 -0.02 -0.03) | — | — |
| H4f | 10 | 800 | 436 | 4 (5 4 5 4 4 4 5 4 3 4) | 0.87 | -0.03 (-0.04 -0.02 -0.02 -0.04 -0.01 -0.02 -0.03 -0.02 -0.03 -0.02) | — | — |
| H5L36 | 10 | 800 | 503 | 81 (72 55 99 68 91 80 86 88 87 81) | 0.80 | -0.27 (-0.17 -0.06 -0.48 -0.15 -0.48 -0.24 -0.29 -0.30 -0.35 -0.22) | — | — |
| H5 | 10 | 800 | 506 | 89 (96 89 91 86 83 59 88 95 102 100) | 0.80 | -0.31 (-0.36 -0.24 -0.32 -0.27 -0.22 -0.14 -0.33 -0.38 -0.42 -0.44) | — | — |
| H5f | 10 | 800 | 503 | 82 (55 94 69 78 107 102 48 115 56 99) | 0.80 | -0.22 (-0.09 -0.19 -0.20 -0.15 -0.41 -0.31 -0.10 -0.44 -0.13 -0.23) | — | — |
| H6 | 10 | 800 | 430 | 4 (4 5 4 4 4 3 4 4 3 4) | 0.86 | -0.03 (-0.04 -0.03 -0.02 -0.02 -0.03 -0.03 -0.03 -0.02 -0.03 -0.03) | — | — |
| H6f | 10 | 800 | 434 | 4 (6 3 4 5 6 4 5 4 4 4) | 0.86 | -0.03 (-0.02 -0.03 -0.02 -0.03 -0.03 -0.03 -0.03 -0.05 -0.04 -0.02) | — | — |

`python tools/cond_rows.py results/fodder` (new tool, 59993f0 + this commit):

results: results/fodder | window: last 100 y | means over seeds (n)
| condition | n | wild goats | wild R | herded | herd R | fodder fed | fodder cut | hunted | captured |
|---|---|---|---|---|---|---|---|---|---|
| H1 | 10 | 425.2 | 0.861 | 0.000 | — | 0.000 | 82,996,793 | 18.2 | 0.000 |
| H1f | 10 | 430.1 | 0.866 | 0.000 | — | 0.000 | 58,290,210 | 18.3 | 0.000 |
| H2 | 10 | 425.9 | 0.864 | 2.435 | 0.840 | 0.000 | 76,685,179 | 15.8 | 2.848 |
| H2f | 10 | 433.1 | 0.862 | 3.010 | 0.838 | 0.000 | 51,488,274 | 16.6 | 3.010 |
| H3 | 10 | 425.4 | 0.862 | 2.844 | 0.832 | 0.000 | 76,368,351 | 15.7 | 2.897 |
| H3f | 10 | 428.8 | 0.859 | 3.052 | 0.830 | 0.000 | 51,676,404 | 17.0 | 3.043 |
| H4 | 10 | 424.3 | 0.863 | 3.202 | 0.836 | 0.000 | 75,717,266 | 16.0 | 2.780 |
| H4f | 10 | 432.2 | 0.867 | 4.173 | 0.841 | 0.000 | 50,721,920 | 16.3 | 2.870 |
| H5 | 10 | 416.8 | 0.804 | 89.0 | 0.494 | 29,246,916 | 59,425,486 | 31.5 | 10.0 |
| H5L36 | 10 | 422.0 | 0.801 | 80.8 | 0.528 | 21,966,862 | 41,810,893 | 31.7 | 9.3 |
| H5f | 10 | 420.8 | 0.801 | 82.3 | 0.578 | 24,908,142 | 41,755,077 | 34.0 | 10.6 |
| H6 | 10 | 426.3 | 0.864 | 3.860 | 0.837 | 0.000 | 75,176,312 | 15.7 | 2.928 |
| H6f | 10 | 429.9 | 0.864 | 4.435 | 0.833 | 0.000 | 50,532,234 | 16.4 | 2.942 |

## [PRE-REGISTERED 2026-10-31] What kills herd goats in H2? (herd deaths by cause)
**Question:** in the fodder batch, H2-H4 and H6 herds hold 2-4 goats (stage4v3 on 10-21 had 22-116).
Over years 700-799 of results/fodder H2f, per year: inflow 3.0 captures + 0.6 herd births; out 0.9
run-offs lost, 0.2 strays lost at dusk, 0.3 culled, and about 2.2 deaths in the herd (by balance;
herdKilloff, all causes incl. culls, gives 2.46). What causes those deaths, and how does H2 compare
with H4 and H5?
**Settings:** main, code 17958ef (adds year record `herdDeaths`, herd goats' deaths by cause; logging
only, no rand draws). `tools/conditions.json` H2, H4, H5 on current defaults (storeWindows 1,
forageLoad 36000, shotChance 0), 800 y, seeds 1-6; window last 100 y.
**Check:** H2 seed 1 must match results/fodder/H2f_seed1.json year for year (fields other than
herdDeaths).
**Prediction:** none on the split. If deaths were spread over causes as in wild goats, starvation
would lead.
**Method:** `node tools/batch.mjs tools/conditions.json results/herddeaths 800 6 18 H2,H4,H5` ->
`results/herddeaths/`; per condition, window means of herded and herdDeaths by cause per year, also as
a rate per herd goat-year, next to wild deaths by cause per wild goat-year.
**RAW RESULTS** (2026-10-31, 18/18 runs, 0 failed; code 17958ef). Check: H2 seed 1 vs
results/fodder/H2f_seed1.json, 0 of 800 years differ (herdDeaths removed).

`PYTHONIOENCODING=utf-8 python tools/herd_deaths.py results/herddeaths` (new tool):

results: results/herddeaths | window: last 100 y | herd deaths per year (per herd goat-year); wild deaths per wild goat-year
| condition | n | herded | predation | starvation | age | other | fight | exposure | hunted | culled | all |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H2 herd | 6 | 2.8 | 1.65 (0.579) | 0.12 (0.040) | 0.07 (0.023) | 0.18 (0.062) | 0.02 (0.006) | 0.00 (0.000) | 0.00 (0.000) | 0.28 (0.097) | 2.30 (0.808) |
| H2 wild | 6 | — | (0.009) | (0.084) | (0.029) | (0.060) | (0.023) | (0.000) | (0.037) | (0.000) | (0.242) |
| H4 herd | 6 | 4.6 | 1.80 (0.388) | 0.20 (0.043) | 0.10 (0.021) | 0.31 (0.067) | 0.05 (0.010) | 0.00 (0.000) | 0.00 (0.000) | 0.46 (0.099) | 2.92 (0.628) |
| H4 wild | 6 | — | (0.010) | (0.082) | (0.030) | (0.060) | (0.021) | (0.000) | (0.039) | (0.000) | (0.241) |
| H5 herd | 6 | 76.6 | 0.75 (0.010) | 3.66 (0.048) | 0.47 (0.006) | 6.72 (0.088) | 0.30 (0.004) | 0.00 (0.000) | 0.00 (0.000) | 8.37 (0.109) | 20.27 (0.265) |
| H5 wild | 6 | — | (0.017) | (0.068) | (0.032) | (0.060) | (0.022) | (0.000) | (0.078) | (0.000) | (0.276) |


## [PRE-REGISTERED 2026-10-31] Where and when do wolves kill herd goats in H2?
**Question:** herd goats in H2 die of predation at 0.58 per goat-year against 0.009 for wild goats
(results/herddeaths): about 1.7 a year per camp in H2 and 1.8 in H4, whatever the herd's size. Is it
that herd goats are attacked more often (exposure), or that an attack on one kills more often
(lethality), and in what circumstances?
**Settings:** main, code a6f486e (adds year record `wolfAtk`: key herd/wild | phase (dawn, dusk, night;
wolves do not hunt by day) | escape terrain | camp cell | prey alarmed at the strike | loose run-off |
kid -> [attacks, kills]; logging only, no rand draws). `tools/conditions.json` H2, H4, H5 on current
defaults, 800 y, seeds 1-6; window last 100 y.
**Check:** H2 seed 1 must match results/herddeaths/H2_seed1.json year for year (wolfAtk removed).
**Prediction:** none.
**Method:** `node tools/batch.mjs tools/conditions.json results/wolfatk 800 6 18 H2,H4,H5`; per
condition, attacks per year per goat (herd, wild) and kills per attack, split by each key field.
**RAW RESULTS** (2026-10-31, 18/18 runs, 0 failed; code a6f486e). Check: H2 seed 1 vs
results/herddeaths/H2_seed1.json, 0 of 800 years differ (wolfAtk removed).

`PYTHONIOENCODING=utf-8 python tools/wolf_atk.py results/wolfatk` (new tool):

results: results/wolfatk | window: last 100 y | sums over seeds

### H2 (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 1709 | 13.884 | 0.5869 | 0.042 |
| wild | 258090 | 0.268 | 0.0092 | 0.034 |
| group | field | value | share of attacks | kills/attack | kills/goat-y |
|---|---|---|---|---|---|
| herd | phase | dawn | 0.367 | 0.042 | 0.2147 |
| herd | phase | dusk | 0.356 | 0.040 | 0.1966 |
| herd | phase | night | 0.277 | 0.046 | 0.1755 |
| herd | escape | 0 | 1.000 | 0.042 | 0.5869 |
| herd | camp | 0 | 0.823 | 0.040 | 0.4587 |
| herd | camp | 1 | 0.177 | 0.052 | 0.1281 |
| herd | alarmed | 0 | 0.001 | 0.000 | 0.0000 |
| herd | alarmed | 1 | 0.999 | 0.042 | 0.5869 |
| herd | loose | 0 | 1.000 | 0.042 | 0.5869 |
| herd | loose | 1 | 0.000 | 0.000 | 0.0000 |
| herd | kid | 0 | 0.935 | 0.034 | 0.4465 |
| herd | kid | 1 | 0.065 | 0.155 | 0.1404 |
| wild | phase | dawn | 0.348 | 0.035 | 0.0032 |
| wild | phase | dusk | 0.383 | 0.034 | 0.0035 |
| wild | phase | night | 0.269 | 0.034 | 0.0025 |
| wild | escape | 0 | 0.626 | 0.050 | 0.0084 |
| wild | escape | 1 | 0.374 | 0.008 | 0.0008 |
| wild | camp | 0 | 0.999 | 0.034 | 0.0092 |
| wild | camp | 1 | 0.001 | 0.093 | 0.0000 |
| wild | alarmed | 0 | 0.103 | 0.049 | 0.0014 |
| wild | alarmed | 1 | 0.897 | 0.033 | 0.0078 |
| wild | kid | 0 | 0.921 | 0.027 | 0.0067 |
| wild | kid | 1 | 0.079 | 0.119 | 0.0025 |

### H4 (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 2787 | 16.195 | 0.3915 | 0.024 |
| wild | 262008 | 0.287 | 0.0096 | 0.033 |
| group | field | value | share of attacks | kills/attack | kills/goat-y |
|---|---|---|---|---|---|
| herd | phase | dawn | 0.315 | 0.035 | 0.1798 |
| herd | phase | dusk | 0.411 | 0.026 | 0.1701 |
| herd | phase | night | 0.274 | 0.009 | 0.0416 |
| herd | escape | 0 | 1.000 | 0.024 | 0.3915 |
| herd | camp | 0 | 0.481 | 0.040 | 0.3107 |
| herd | camp | 1 | 0.519 | 0.010 | 0.0807 |
| herd | alarmed | 0 | 0.001 | 0.064 | 0.0011 |
| herd | alarmed | 1 | 0.999 | 0.024 | 0.3904 |
| herd | loose | 0 | 1.000 | 0.024 | 0.3915 |
| herd | kid | 0 | 0.935 | 0.020 | 0.3010 |
| herd | kid | 1 | 0.065 | 0.086 | 0.0904 |
| wild | phase | dawn | 0.354 | 0.034 | 0.0034 |
| wild | phase | dusk | 0.379 | 0.034 | 0.0037 |
| wild | phase | night | 0.267 | 0.033 | 0.0025 |
| wild | escape | 0 | 0.635 | 0.048 | 0.0088 |
| wild | escape | 1 | 0.365 | 0.007 | 0.0008 |
| wild | camp | 0 | 0.999 | 0.033 | 0.0096 |
| wild | camp | 1 | 0.001 | 0.119 | 0.0000 |
| wild | alarmed | 0 | 0.104 | 0.046 | 0.0014 |
| wild | alarmed | 1 | 0.896 | 0.032 | 0.0082 |
| wild | kid | 0 | 0.919 | 0.026 | 0.0069 |
| wild | kid | 1 | 0.081 | 0.118 | 0.0027 |

### H5 (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 45966 | 0.785 | 0.0097 | 0.012 |
| wild | 255063 | 0.564 | 0.0169 | 0.030 |
| group | field | value | share of attacks | kills/attack | kills/goat-y |
|---|---|---|---|---|---|
| herd | phase | dawn | 0.399 | 0.018 | 0.0056 |
| herd | phase | dusk | 0.384 | 0.011 | 0.0034 |
| herd | phase | night | 0.218 | 0.004 | 0.0007 |
| herd | escape | 0 | 1.000 | 0.012 | 0.0097 |
| herd | camp | 0 | 0.537 | 0.019 | 0.0080 |
| herd | camp | 1 | 0.463 | 0.005 | 0.0018 |
| herd | alarmed | 0 | 0.179 | 0.020 | 0.0028 |
| herd | alarmed | 1 | 0.821 | 0.011 | 0.0069 |
| herd | loose | 0 | 1.000 | 0.012 | 0.0097 |
| herd | loose | 1 | 0.000 | 0.000 | 0.0000 |
| herd | kid | 0 | 0.793 | 0.008 | 0.0051 |
| herd | kid | 1 | 0.207 | 0.029 | 0.0047 |
| wild | phase | dawn | 0.352 | 0.029 | 0.0058 |
| wild | phase | dusk | 0.381 | 0.031 | 0.0066 |
| wild | phase | night | 0.268 | 0.031 | 0.0046 |
| wild | escape | 0 | 0.533 | 0.049 | 0.0149 |
| wild | escape | 1 | 0.467 | 0.008 | 0.0021 |
| wild | camp | 0 | 1.000 | 0.030 | 0.0169 |
| wild | camp | 1 | 0.000 | 0.136 | 0.0000 |
| wild | alarmed | 0 | 0.139 | 0.043 | 0.0034 |
| wild | alarmed | 1 | 0.861 | 0.028 | 0.0136 |
| wild | kid | 0 | 0.918 | 0.024 | 0.0124 |
| wild | kid | 1 | 0.082 | 0.097 | 0.0045 |


## [PRE-REGISTERED 2026-10-31] Herder presence against wolves (herderProtection) in H2-H6
**Question:** in H2-H4 and H6 herds hold 2-5 goats because wolves strike herd goats about 50 times as
often per goat as wild goats (results/wolfatk) and the herder beside them has no effect. With Chris,
2026-10-31: the herder's presence protects the herd in every herding condition, the effect of dogs
folded in (no dog agents). Soofi et al. 2022 (NE Iran): shepherd present, wolf predation about -43% in
night corrals and -60% by day; each dog a further -25%. Set herderProtection 0.6 (a herder with a dog
at night, 1 - 0.57 x 0.75 = 0.57; a herder by day, 0.60). Does it let herds grow in H2-H4/H6, and what
does it do to herd R and the herd-wild gap? What does it add in H5, which also has guarding (x 0.3)?
**Settings:** main, code 3a25ea7 (adds herderProtection, default 0: a wolf's kill chance on a herd goat
within 1 cell (Chebyshev) of its camp's herder x (1 - herderProtection), after the pen, before
guarding; wolfAtk key gains nearHerder). `tools/cal_herder.json`: H2p-H6p = conditions.json H2-H6 +
herderProtection 0.6. Current defaults (storeWindows 1, forageLoad 36000, shotChance 0). 800 y, seeds
1-6; window last 100 y. Baselines: results/wolfatk (H2, H4, H5, same seeds), results/fodder (H2f-H6f,
seeds 1-10).
**Check:** H2 at default (herderProtection 0), seed 1, must match results/wolfatk/H2_seed1.json year
for year (wolfAtk removed; its key format changed).
**Prediction:** herd kills per attack in H2 fall by about 0.6; herds in H2-H4/H6 larger than 5. No
prediction for size or R.
**Method:** `node tools/batch.mjs tools/cal_herder.json results/herder 800 6 18`;
`node tools/batch.mjs tools/conditions.json results/herder_check 800 1 1 H2`; trial_summary.py,
cond_rows.py, herd_deaths.py, wolf_atk.py on results/herder.
**RAW RESULTS** (2026-10-31, 30/30 runs + 1 check, 0 failed; code 3a25ea7). Check: results/herder_check
H2 seed 1 (herderProtection 0) vs results/wolfatk/H2_seed1.json, 0 of 800 years differ (wolfAtk removed).
Full wolf_atk.py output in results/herder/wolf_atk.txt; its summary rows below.

`trial_summary.py results/herder`:

results: results/herder | window: last 100 y | seeds per condition in n
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H2p | 6 | 800 | 436 | 6 (8 7 6 6 5 5) | 0.86 | -0.02 (-0.02 -0.02 -0.02 -0.03 -0.02 -0.02) | — | — |
| H3p | 6 | 800 | 443 | 6 (7 6 5 6 7 9) | 0.87 | -0.03 (-0.01 -0.04 -0.03 -0.03 -0.02 -0.02) | — | — |
| H4p | 6 | 800 | 441 | 8 (9 8 7 9 10 8) | 0.86 | -0.03 (-0.03 -0.02 -0.03 -0.03 -0.02 -0.02) | — | — |
| H5p | 6 | 800 | 513 | 93 (75 103 62 108 111 98) | 0.80 | -0.32 (-0.16 -0.47 -0.07 -0.50 -0.48 -0.24) | — | — |
| H6p | 6 | 800 | 445 | 10 (10 9 9 13 8 10) | 0.86 | -0.03 (-0.03 -0.02 -0.03 -0.03 -0.03 -0.02) | — | — |

`cond_rows.py results/herder`:

results: results/herder | window: last 100 y | means over seeds (n)
| condition | n | wild goats | wild R | herded | herd R | fodder fed | fodder cut | hunted | captured |
|---|---|---|---|---|---|---|---|---|---|
| H2p | 6 | 429.5 | 0.859 | 6.2 | 0.836 | 0.000 | 49,325,012 | 17.2 | 3.085 |
| H3p | 6 | 436.6 | 0.868 | 6.5 | 0.843 | 0.000 | 49,280,388 | 16.5 | 3.055 |
| H4p | 6 | 432.4 | 0.864 | 8.4 | 0.838 | 0.000 | 48,479,244 | 16.9 | 3.055 |
| H5p | 6 | 420.1 | 0.802 | 92.9 | 0.482 | 28,628,466 | 40,906,350 | 33.0 | 10.2 |
| H6p | 6 | 434.9 | 0.856 | 9.6 | 0.828 | 0.000 | 48,034,816 | 17.8 | 3.402 |

`herd_deaths.py results/herder`:

results: results/herder | window: last 100 y | herd deaths per year (per herd goat-year); wild deaths per wild goat-year
| condition | n | herded | predation | starvation | age | other | fight | exposure | hunted | culled | all |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H2p herd | 6 | 6.2 | 1.45 (0.233) | 0.14 (0.023) | 0.14 (0.022) | 0.41 (0.067) | 0.13 (0.020) | 0.00 (0.000) | 0.00 (0.000) | 0.70 (0.113) | 2.98 (0.478) |
| H2p wild | 6 | — | (0.010) | (0.080) | (0.030) | (0.061) | (0.022) | (0.000) | (0.040) | (0.000) | (0.243) |
| H3p herd | 6 | 6.5 | 1.46 (0.225) | 0.23 (0.036) | 0.10 (0.016) | 0.44 (0.068) | 0.11 (0.016) | 0.00 (0.000) | 0.00 (0.000) | 0.71 (0.110) | 3.06 (0.471) |
| H3p wild | 6 | — | (0.009) | (0.085) | (0.030) | (0.060) | (0.020) | (0.000) | (0.038) | (0.000) | (0.243) |
| H4p herd | 6 | 8.4 | 1.42 (0.169) | 0.34 (0.040) | 0.12 (0.015) | 0.57 (0.068) | 0.14 (0.016) | 0.00 (0.000) | 0.00 (0.000) | 0.89 (0.107) | 3.47 (0.414) |
| H4p wild | 6 | — | (0.010) | (0.084) | (0.030) | (0.060) | (0.021) | (0.000) | (0.039) | (0.000) | (0.244) |
| H5p herd | 6 | 92.9 | 0.36 (0.004) | 8.23 (0.089) | 0.71 (0.008) | 8.06 (0.087) | 0.43 (0.005) | 0.00 (0.000) | 0.00 (0.000) | 9.93 (0.107) | 27.72 (0.298) |
| H5p wild | 6 | — | (0.019) | (0.070) | (0.031) | (0.060) | (0.021) | (0.000) | (0.079) | (0.000) | (0.279) |
| H6p herd | 6 | 9.6 | 1.70 (0.176) | 0.37 (0.038) | 0.14 (0.015) | 0.69 (0.071) | 0.17 (0.018) | 0.00 (0.000) | 0.00 (0.000) | 1.03 (0.107) | 4.11 (0.426) |
| H6p wild | 6 | — | (0.011) | (0.076) | (0.031) | (0.060) | (0.020) | (0.000) | (0.041) | (0.000) | (0.239) |

`wolf_atk.py results/herder` (summary rows):

### H2p (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 3742 | 12.999 | 0.2338 | 0.018 |
| wild | 257682 | 0.301 | 0.0104 | 0.035 |

### H3p (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 3899 | 11.869 | 0.2252 | 0.019 |
| wild | 261980 | 0.275 | 0.0093 | 0.034 |

### H4p (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 5025 | 15.696 | 0.1692 | 0.011 |
| wild | 259445 | 0.295 | 0.0102 | 0.035 |

### H5p (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 55731 | 0.634 | 0.0039 | 0.006 |
| wild | 252061 | 0.597 | 0.0187 | 0.031 |

### H6p (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 5781 | 16.284 | 0.1763 | 0.011 |
| wild | 260952 | 0.330 | 0.0112 | 0.034 |


## [PRE-REGISTERED 2026-10-31] Why are herd goats struck so often? (wolf encounter and flight probe)
**Question:** herd goats in H2-H4/H6 are struck about 13-16 times per goat-year against 0.3 for wild
goats, with or without herderProtection (results/wolfatk, results/herder); H5 herd goats 0.6-0.8.
Herd goats (0.7% of goats in H2) draw about a quarter of all strikes. Candidates: (a) location: hunting
wolves are near herds more often (attraction, where herds sit); (b) flight: wild goats leave a wolf's
reach when they sense it, herd goats step toward the herder and stay; (c) repeated strikes by one wolf
in a bout; (d) in H5, guards kill about 15 wolves a year (of 60), each replaced by an immigrant at the
map's upland edge, ending its bout. Before any fix, with Chris.
**Settings:** main, code 9f0f7dc (probe only; model code 3a25ea7, defaults incl. herderProtection 0).
`node tools/wolf_probe.mjs 500 450 results/wolfprobe/<cond>_seed<s>.json <cond>`, conditions H2, H4, H5
from tools/conditions.json, seeds 1-3; measured over years 451-500.
**Method:** per sub-tick, after the wolves move and before goats step (pre), and after goats step
(post): for each goat, the number of hunting wolves whose 3x3 holds it; hunting wolves within 3 cells
(pre); share on escape terrain; distance to nearest camp. Per bout: herd strikes per wolf-bout,
whether a guard killed the wolf. Strikes and kills from the wolfAtk tallies. Rates per goat-sub-tick
and per goat-year. Smoke (4 y, herdingAt 1): pre herd 0.035, wild 0.019; post herd 0.035, wild 0.0024.
**Prediction:** (b) dominates: post/pre near 1 for herd goats, well below 1 for wild goats.
**RAW RESULTS** (2026-10-31, 9/9 runs; code 9f0f7dc). `python tools/wolf_probe_rows.py results/wolfprobe`
(new tool):

results: results/wolfprobe | per goat-sub-tick during bouts (pre: after wolves move; post: after goats step) | sums over seeds
| condition | n | group | goat-years | pre | post | post/pre | wolves within 3 | on escape terrain | cells to camp | strikes/goat-y | kills/strike |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H2 | 3 | herd | 461 | 0.0138 | 0.0138 | 1.00 | 0.068 | 0.00 | 4.1 | 13.92 | 0.043 |
| H2 | 3 | wild | 64370 | 0.0046 | 0.0003 | 0.07 | 0.058 | 0.38 | 22.8 | 0.32 | 0.034 |
| H4 | 3 | herd | 631 | 0.0179 | 0.0180 | 1.01 | 0.079 | 0.00 | 1.1 | 16.86 | 0.026 |
| H4 | 3 | wild | 63787 | 0.0047 | 0.0003 | 0.07 | 0.060 | 0.38 | 22.8 | 0.32 | 0.034 |
| H5 | 3 | herd | 7295 | 0.0056 | 0.0059 | 1.05 | 0.033 | 0.00 | 1.1 | 1.03 | 0.012 |
| H5 | 3 | wild | 63110 | 0.0063 | 0.0005 | 0.08 | 0.080 | 0.38 | 23.1 | 0.46 | 0.031 |

| condition | hunting wolves: cells to camp | wolf-bouts hunting goats | wolf-bouts striking a herd | herd strikes in bouts of 1 / 2 / 3-5 / 6-10 / 11+ | share of herd bouts with a herd kill | share ended by a guard kill |
|---|---|---|---|---|---|---|
| H2 | 22.6 | 181486 | 3243 | 0.24 / 0.26 / 0.43 / 0.07 / 0.00 | 0.09 | 0.00 |
| H4 | 22.0 | 191220 | 5351 | 0.24 / 0.26 / 0.42 / 0.08 / 0.00 | 0.05 | 0.00 |
| H5 | 27.2 | 256975 | 3850 | 0.26 / 0.27 / 0.38 / 0.09 / 0.00 | 0.02 | 0.24 |


## [PRE-REGISTERED 2026-11-01] Herder chases wolves off the herd (H2-H6)
**Question:** the probe (entry above) found herd goats stay inside a striking wolf's reach (post/pre
1.00 against 0.07 for wild goats) because they step toward the herder instead of fleeing; nothing in
H2-H4/H6 answers the wolf. Chris (2026-11-01): "chase of wolves from the herd". With herderChase, a
wolf that strikes at a herd goat within 1 cell of its herder (kill or miss) is driven off with that
chance: its bout ends (memory still updates at dawn) and it is pushed herderChaseDist 5 cells straight
away from the herder. How much does this cut herd predation, and what does it do to herd size and the
herd-wild gap?
**Settings:** main, code 686c2e2. tools/cal_chase.json: H2c-H6c = tools/conditions.json H2-H6 +
herderChase 1; H2h = H2 + herderChase 0.5. herderProtection 0 throughout.
**Method:** `node tools/batch.mjs tools/cal_chase.json results/chase 800 6 18`;
`node tools/batch.mjs tools/conditions.json results/chase_check 800 1 1 H2` (herderChase 0) against
results/herder_check/H2_seed1.json, wolvesChased removed. trial_summary.py, cond_rows.py,
herd_deaths.py, wolf_atk.py on results/chase; wolvesChased per year. Comparison rows: results/wolfatk
(H2, H4, H5) and results/herder (herderProtection 0.6). Smoke (H2 seed 1, herderChase 1, 450 y): runs,
12-27 chases a year at years 401-450; 100-year default run 0 of 100 years differ from
results/herder_check.
**Prediction:** herd strikes per wolf-bout fall to 1, so herd strikes per goat-year roughly halve (the
probe had about 0.5 herd bouts per herd strike) and herd predation in H2 falls from about 0.58 to about
0.3 per goat-year: herd goats still struck about 20x as often as wild ones; herds larger than with
herderProtection 0.6 is not expected. H5c changes little.

**RAW RESULTS** (2026-11-01, 36/36 runs + 1 check, 0 failed; code 686c2e2). Check: results/chase_check
H2 seed 1 (herderChase 0) vs results/herder_check/H2_seed1.json, 0 of 800 years differ (wolvesChased
removed). Full wolf_atk.py output in results/chase/wolf_atk.txt; its summary rows below.
New tool tools/herd_strikes.py (per year, all camps). trial_summary.py needs PYTHONIOENCODING=utf-8 on
this Windows console (it prints U+2212).

`trial_summary.py results/chase`:

results: results/chase | window: last 100 y | seeds per condition in n
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H2c | 6 | 800 | 444 | 9 (10 7 12 7 7 9) | 0.86 | -0.02 (-0.04 -0.03 -0.01 -0.02 -0.03 -0.03) | — | — |
| H2h | 6 | 800 | 438 | 8 (8 6 8 9 10 6) | 0.85 | -0.02 (-0.02 -0.03 -0.03 -0.04 -0.01 -0.01) | — | — |
| H3c | 6 | 800 | 441 | 11 (11 10 13 11 10 10) | 0.86 | -0.02 (-0.03 -0.02 -0.03 -0.01 -0.02 -0.02) | — | — |
| H4c | 6 | 800 | 450 | 14 (14 14 14 13 14 16) | 0.85 | -0.03 (-0.03 -0.05 -0.04 -0.03 -0.04 -0.02) | — | — |
| H5c | 6 | 800 | 504 | 95 (108 98 60 105 100 99) | 0.82 | -0.34 (-0.53 -0.34 -0.12 -0.41 -0.29 -0.32) | — | — |
| H6c | 6 | 800 | 443 | 14 (13 14 15 13 14 13) | 0.86 | -0.03 (-0.03 -0.05 -0.05 -0.02 -0.03 -0.02) | — | — |

`cond_rows.py results/chase`:

results: results/chase | window: last 100 y | means over seeds (n)
| condition | n | wild goats | wild R | herded | herd R | fodder fed | fodder cut | hunted | captured |
|---|---|---|---|---|---|---|---|---|---|
| H2c | 6 | 435.5 | 0.855 | 8.6 | 0.830 | 0.000 | 48,208,215 | 18.0 | 3.275 |
| H2h | 6 | 430.4 | 0.854 | 7.7 | 0.830 | 0.000 | 48,610,440 | 17.7 | 3.215 |
| H3c | 6 | 429.8 | 0.855 | 10.8 | 0.834 | 0.000 | 47,861,054 | 17.7 | 3.315 |
| H4c | 6 | 436.1 | 0.854 | 14.2 | 0.819 | 0.000 | 47,162,242 | 18.1 | 3.583 |
| H5c | 6 | 409.1 | 0.816 | 94.9 | 0.479 | 29,387,299 | 40,815,408 | 31.2 | 9.9 |
| H6c | 6 | 429.2 | 0.860 | 13.9 | 0.826 | 0.000 | 47,203,477 | 17.5 | 3.417 |

`herd_deaths.py results/chase`:

results: results/chase | window: last 100 y | herd deaths per year (per herd goat-year); wild deaths per wild goat-year
| condition | n | herded | predation | starvation | age | other | fight | exposure | hunted | culled | all |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H2c herd | 6 | 8.6 | 1.14 (0.133) | 0.22 (0.026) | 0.22 (0.026) | 0.67 (0.077) | 0.18 (0.022) | 0.00 (0.000) | 0.00 (0.000) | 0.92 (0.107) | 3.35 (0.390) |
| H2c wild | 6 | — | (0.010) | (0.080) | (0.030) | (0.061) | (0.021) | (0.000) | (0.041) | (0.000) | (0.243) |
| H2h herd | 6 | 7.7 | 1.52 (0.196) | 0.16 (0.021) | 0.15 (0.020) | 0.48 (0.062) | 0.15 (0.020) | 0.00 (0.000) | 0.00 (0.000) | 0.83 (0.107) | 3.29 (0.426) |
| H2h wild | 6 | — | (0.010) | (0.079) | (0.031) | (0.060) | (0.020) | (0.000) | (0.041) | (0.000) | (0.241) |
| H3c herd | 6 | 10.8 | 1.27 (0.117) | 0.23 (0.021) | 0.12 (0.011) | 0.82 (0.076) | 0.22 (0.020) | 0.00 (0.000) | 0.00 (0.000) | 1.24 (0.114) | 3.90 (0.360) |
| H3c wild | 6 | — | (0.011) | (0.078) | (0.030) | (0.060) | (0.021) | (0.000) | (0.041) | (0.000) | (0.241) |
| H4c herd | 6 | 14.2 | 1.23 (0.087) | 0.66 (0.047) | 0.13 (0.009) | 1.04 (0.073) | 0.32 (0.022) | 0.00 (0.000) | 0.00 (0.000) | 1.56 (0.110) | 4.94 (0.348) |
| H4c wild | 6 | — | (0.011) | (0.080) | (0.030) | (0.060) | (0.021) | (0.000) | (0.042) | (0.000) | (0.244) |
| H5c herd | 6 | 94.9 | 0.54 (0.006) | 8.32 (0.088) | 0.65 (0.007) | 8.15 (0.086) | 0.45 (0.005) | 0.00 (0.000) | 0.00 (0.000) | 10.27 (0.108) | 28.38 (0.299) |
| H5c wild | 6 | — | (0.018) | (0.071) | (0.030) | (0.061) | (0.023) | (0.000) | (0.076) | (0.000) | (0.280) |
| H6c herd | 6 | 13.9 | 1.09 (0.079) | 0.58 (0.042) | 0.15 (0.011) | 0.97 (0.070) | 0.33 (0.024) | 0.00 (0.000) | 0.00 (0.000) | 1.49 (0.107) | 4.63 (0.334) |
| H6c wild | 6 | — | (0.010) | (0.079) | (0.030) | (0.061) | (0.021) | (0.000) | (0.041) | (0.000) | (0.242) |

`wolf_atk.py results/chase` (summary rows):

### H2c (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 5151 | 2.779 | 0.1328 | 0.048 |
| wild | 261273 | 0.320 | 0.0102 | 0.032 |
### H2h (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 4633 | 4.278 | 0.1966 | 0.046 |
| wild | 258239 | 0.319 | 0.0102 | 0.032 |
### H3c (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 6504 | 2.380 | 0.1173 | 0.049 |
| wild | 257864 | 0.320 | 0.0107 | 0.034 |
### H4c (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 8508 | 2.353 | 0.0869 | 0.037 |
| wild | 261685 | 0.331 | 0.0112 | 0.034 |
### H5c (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 56948 | 0.359 | 0.0056 | 0.016 |
| wild | 245450 | 0.557 | 0.0182 | 0.033 |
### H6c (n 6)
| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |
|---|---|---|---|---|
| herd | 8330 | 2.287 | 0.0789 | 0.034 |
| wild | 257509 | 0.314 | 0.0103 | 0.033 |

`herd_strikes.py` on results/wolfatk, results/herder, results/chase:

results: results/wolfatk | window: last 100 y | per year, all camps, means over seeds
| condition | herded | herd strikes | wolves chased | herd predation | strikes per herd goat-year |
|---|---|---|---|---|---|
| H2 | 2.8 | 39.5 | 0.0 | 1.65 | 13.88 |
| H4 | 4.6 | 75.2 | 0.0 | 1.80 | 16.20 |
| H5 | 76.6 | 60.2 | 0.0 | 0.75 | 0.79 |
results: results/herder | window: last 100 y | per year, all camps, means over seeds
| condition | herded | herd strikes | wolves chased | herd predation | strikes per herd goat-year |
|---|---|---|---|---|---|
| H2p | 6.2 | 81.1 | 0.0 | 1.45 | 13.00 |
| H3p | 6.5 | 77.1 | 0.0 | 1.46 | 11.87 |
| H4p | 8.4 | 131.5 | 0.0 | 1.42 | 15.70 |
| H5p | 92.9 | 58.9 | 0.0 | 0.36 | 0.63 |
| H6p | 9.6 | 156.9 | 0.0 | 1.70 | 16.28 |
results: results/chase | window: last 100 y | per year, all camps, means over seeds
| condition | herded | herd strikes | wolves chased | herd predation | strikes per herd goat-year |
|---|---|---|---|---|---|
| H2c | 8.6 | 23.9 | 23.9 | 1.14 | 2.78 |
| H2h | 7.7 | 33.0 | 16.5 | 1.52 | 4.28 |
| H3c | 10.8 | 25.8 | 25.8 | 1.27 | 2.38 |
| H4c | 14.2 | 33.4 | 33.4 | 1.23 | 2.35 |
| H5c | 94.9 | 34.1 | 30.9 | 0.54 | 0.36 |
| H6c | 13.9 | 31.7 | 31.7 | 1.09 | 2.29 |

## [PRE-REGISTERED 2026-11-01] H5 to 1,500 years (does the herd settle?)
**Question:** under herderChase (now default 1, code 99953c1) H5 herds were still growing at year 800
(50-year means 33 at 401-450, 61 at 551-600, 99 at 751-800; results/chase H5c) and the herd-wild R
gap (-0.34, seeds -0.12 to -0.53) is a reading taken mid-climb. Where do herd size and the R gap
settle, and does the spread between seeds narrow? Chris (2026-11-01): "ok run a long run for H5".
**Settings:** main, code 99953c1. tools/conditions.json H5 (herderChase from the default, 1).
**Method:** `node tools/batch.mjs tools/conditions.json results/h5long 1500 12 18 H5`, seeds 1-12.
Check: seeds 1-6, years 1-800, against results/chase/H5c_seed1-6.json (same parameters: H5c set
herderChase 1 by override, now by default); expected 0 differing years. Per 100-year window: herded,
herd births, captures, herd R, wild R, herd-wild R gap, by seed; trial_summary.py, herd_deaths.py and
herd_strikes.py on the last 100 years.
**Prediction:** the herd levels off between 120 and 200 by year 1,200; the R gap keeps widening past
-0.34 while births outnumber captures.

**RAW RESULTS** (2026-11-01, 12/12 runs, 0 failed; code 99953c1). Check: seeds 1-6, years 1-800, vs
results/chase/H5c_seed1-6.json: 0 of 800 years differ in each. New tool tools/h5_trend.py.

`h5_trend.py results/h5long`:

results: results/h5long | windows of 100 y from year 401 | means over 12 seeds (herd R: years with a herd)
| years | herded | herd births/y | captures/y | herd R | wild R | herd − wild R | gap range over seeds |
|---|---|---|---|---|---|---|---|
| 401-500 | 39.7 | 15.2 | 5.8 | 0.790 | 0.840 | -0.050 | -0.10 to -0.02 |
| 501-600 | 61.1 | 25.8 | 9.1 | 0.702 | 0.811 | -0.109 | -0.23 to -0.05 |
| 601-700 | 80.0 | 34.7 | 10.9 | 0.596 | 0.797 | -0.201 | -0.38 to -0.05 |
| 701-800 | 96.2 | 41.3 | 10.3 | 0.481 | 0.810 | -0.330 | -0.53 to -0.12 |
| 801-900 | 104.1 | 44.3 | 8.8 | 0.395 | 0.827 | -0.432 | -0.55 to -0.10 |
| 901-1000 | 108.0 | 44.6 | 8.0 | 0.347 | 0.832 | -0.485 | -0.63 to -0.15 |
| 1001-1100 | 111.2 | 44.1 | 7.2 | 0.290 | 0.833 | -0.543 | -0.68 to -0.31 |
| 1101-1200 | 116.5 | 44.9 | 6.9 | 0.260 | 0.839 | -0.579 | -0.71 to -0.40 |
| 1201-1300 | 118.2 | 43.9 | 6.5 | 0.247 | 0.843 | -0.596 | -0.69 to -0.44 |
| 1301-1400 | 121.6 | 44.5 | 6.4 | 0.232 | 0.842 | -0.610 | -0.72 to -0.48 |
| 1401-1500 | 116.9 | 42.6 | 5.9 | 0.229 | 0.843 | -0.614 | -0.68 to -0.52 |

last 100 y by seed:
| seed | herded | herd births/y | captures/y | herd R | wild R | herd − wild R |
|---|---|---|---|---|---|---|
| 1 | 116 | 42.1 | 7.0 | 0.259 | 0.836 | -0.577 |
| 2 | 117 | 41.4 | 5.5 | 0.200 | 0.842 | -0.642 |
| 3 | 130 | 53.2 | 8.7 | 0.309 | 0.828 | -0.519 |
| 4 | 114 | 42.0 | 4.5 | 0.188 | 0.867 | -0.679 |
| 5 | 82 | 28.8 | 4.8 | 0.318 | 0.853 | -0.536 |
| 6 | 114 | 40.4 | 4.6 | 0.187 | 0.856 | -0.668 |
| 7 | 121 | 43.1 | 4.7 | 0.176 | 0.840 | -0.664 |
| 8 | 118 | 41.6 | 5.6 | 0.225 | 0.853 | -0.628 |
| 9 | 132 | 48.2 | 7.5 | 0.249 | 0.833 | -0.584 |
| 10 | 130 | 45.2 | 6.2 | 0.188 | 0.818 | -0.630 |
| 11 | 114 | 43.1 | 4.9 | 0.213 | 0.861 | -0.648 |
| 12 | 115 | 42.5 | 6.7 | 0.235 | 0.828 | -0.592 |

`trial_summary.py results/h5long` (per-seed lists in file order 1, 10, 11, 12, 2, ...):

results: results/h5long | window: last 100 y | seeds per condition in n
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H5 | 12 | 1500 | 545 | 117 (116 130 114 115 117 130 114 82 114 121 118 132) | 0.84 | -0.61 (-0.58 -0.63 -0.65 -0.59 -0.64 -0.52 -0.68 -0.54 -0.67 -0.66 -0.63 -0.58) | — | — |

`cond_rows.py results/h5long`:

results: results/h5long | window: last 100 y | means over seeds (n)
| condition | n | wild goats | wild R | herded | herd R | fodder fed | fodder cut | hunted | captured |
|---|---|---|---|---|---|---|---|---|---|
| H5 | 12 | 427.9 | 0.843 | 116.9 | 0.229 | 26,488,596 | 41,571,930 | 21.9 | 5.9 |

`herd_deaths.py results/h5long`:

results: results/h5long | window: last 100 y | herd deaths per year (per herd goat-year); wild deaths per wild goat-year
| condition | n | herded | predation | starvation | age | other | fight | exposure | hunted | culled | all |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H5 herd | 12 | 116.9 | 0.55 (0.005) | 13.78 (0.118) | 1.82 (0.016) | 8.96 (0.077) | 0.80 (0.007) | 0.00 (0.000) | 0.00 (0.000) | 12.42 (0.106) | 38.33 (0.328) |
| H5 wild | 12 | — | (0.014) | (0.076) | (0.032) | (0.060) | (0.019) | (0.000) | (0.051) | (0.000) | (0.252) |

`herd_strikes.py results/h5long`:

results: results/h5long | window: last 100 y | per year, all camps, means over seeds
| condition | herded | herd strikes | wolves chased | herd predation | strikes per herd goat-year |
|---|---|---|---|---|---|
| H5 | 116.9 | 27.9 | 25.5 | 0.55 | 0.24 |

Addendum (2026-11-01, not pre-registered; same runs, new tool tools/trait_gaps.py), `trait_gaps.py results/h5long`:

results: results/h5long | windows of 100 y from year 401 | herd − wild genetic mean per trait | means over 12 seeds
| years | R | A | S | B | H | T | M | W | herd IBD | wild IBD | wild-sired | sires/camp | gens since capture |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 401-500 | -0.05 | +0.00 | +0.01 | -0.02 | -0.00 | +0.02 | -0.00 | -0.01 | 0.13 | 0.03 | 0.048 | 1.3 | 1.9 |
| 501-600 | -0.11 | -0.01 | +0.02 | -0.02 | -0.02 | +0.05 | +0.01 | -0.01 | 0.27 | 0.09 | 0.017 | 1.4 | 2.7 |
| 601-700 | -0.20 | -0.00 | +0.03 | -0.05 | -0.02 | +0.07 | +0.03 | -0.01 | 0.36 | 0.15 | 0.012 | 1.5 | 2.9 |
| 701-800 | -0.33 | +0.00 | +0.07 | -0.13 | -0.03 | +0.09 | +0.04 | +0.01 | 0.49 | 0.19 | 0.009 | 1.5 | 4.0 |
| 801-900 | -0.43 | -0.01 | +0.08 | -0.21 | -0.02 | +0.10 | +0.03 | -0.01 | 0.60 | 0.23 | 0.008 | 1.4 | 5.3 |
| 901-1000 | -0.49 | -0.02 | +0.09 | -0.30 | -0.03 | +0.09 | +0.03 | -0.04 | 0.66 | 0.27 | 0.007 | 1.4 | 6.1 |
| 1001-1100 | -0.54 | -0.03 | +0.10 | -0.41 | -0.03 | +0.08 | +0.02 | -0.00 | 0.72 | 0.31 | 0.006 | 1.4 | 6.6 |
| 1101-1200 | -0.58 | -0.02 | +0.12 | -0.53 | -0.05 | +0.05 | +0.01 | +0.02 | 0.75 | 0.33 | 0.006 | 1.3 | 8.6 |
| 1201-1300 | -0.60 | -0.03 | +0.11 | -0.61 | -0.05 | +0.03 | +0.01 | +0.03 | 0.75 | 0.36 | 0.005 | 1.3 | 11.2 |
| 1301-1400 | -0.61 | -0.03 | +0.13 | -0.67 | -0.06 | +0.00 | +0.02 | +0.02 | 0.76 | 0.38 | 0.006 | 1.3 | 9.8 |
| 1401-1500 | -0.61 | -0.03 | +0.13 | -0.68 | -0.06 | +0.01 | +0.02 | +0.02 | 0.77 | 0.40 | 0.006 | 1.3 | 9.9 |

## [PRE-REGISTERED 2026-11-01] Generations since wild in H3, H4 and H5 herds
**Question:** Daly et al. 2021 (Ganj Dareh, Tepe Abdul Hosein): the managed goats carry the whole range of
modern domestic mtDNA haplogroups, clading with wild sequences, while all their Y sequences fall in one
lineage (Y1AA) absent from sampled wild males; F_ROH5Mb 2.7% and 8.2%. Read as wild genes entering mainly
through captured females, with a narrow sire line. Do the model's herds show this? Chris (2026-11-01):
"this might be our 'generations since planted' trace we used for grains. we need generations since wild?"
**Settings:** main, code 68e1763. tools/conditions.json H3, H4, H5 (herderChase default 1).
New fields, no rand draws: herdMatGen (herd goats by generations since a captured doe on the maternal
line), herdPatGen (herd males by the same on the sire line; a wild sire counts as captured), herdWildAnc
(mean herd genome share by generations since it left the wild; each parent passes half, one generation
deeper; captured goats and wild sires at 0), herdAncDepth. Bins 0 / 1 / 2-4 / 5-9 / 10-19 / 20+. A goat
recaptured after escaping restarts at 0 (as gsc always has); wild-born kids are wild.
**Method:** `node tools/batch.mjs tools/conditions.json results/gentrace 1500 12 12 H5` and
`node tools/batch.mjs tools/conditions.json results/gentrace 1500 6 6 H3,H4`, in parallel.
Check: H5 seeds 1-12 vs results/h5long, new fields removed, expected 0 differing years in all 1,500.
gen_trace.py (new), trait_gaps.py, trial_summary.py on results/gentrace. Smoke (H5 seed 1, 520 y): 0 of
520 years differ from results/h5long; year 519: herded 66, maternal 17/16/18/4/11/0, sire line (males)
5/2/10/5/0/0, genome by depth 0.26/0.17/0.35/0.18/0.04/0.00, mean depth 2.85.
**Prediction:** in H5 the sire line runs deeper than the maternal line (buck management keeps the oldest
herd bucks as sires, wild-sired share about 0.6%, while about 6 wild captures a year enter at 0): by year
1,500 most herd males sit at 5+ generations on the sire line, and at least 10% of herd goats at 0-1 on the
maternal line. Mean genome depth in H5 levels off under 15 generations. H3 and H4 herds stay shallow (mean
depth under 4), since their herds are short-lived and refounded from captures.

**Raw results (2026-11-01):** batch done 19:51 UTC, 24 runs, 1,500 years each, about 1,980 s per run.
Check: H5 seeds 1-12 vs results/h5long with the four new fields removed: 0 differing years in 1,500, every
seed; all four fields present in year 1,500. Instrument check: gentrace seed 1 vs h5long seed 2 differs in
1,500 of 1,500 years.

`gen_trace.py results/gentrace` (shares in bins 0 / 1 / 2-4 / 5-9 / 10-19 / 20+):

| cond | years | herded | maternal line (herd goats) | sire line (herd males) | genome by depth | mean genome depth |
|---|---|---|---|---|---|---|
| H3 | 401-500 | 10.3 | 0.46 / 0.28 / 0.24 / 0.03 / 0.00 / 0.00 | 0.46 / 0.31 / 0.20 / 0.02 / 0.00 / 0.00 | 0.46 / 0.30 / 0.22 / 0.02 / 0.00 / 0.00 | 1.0 |
| H3 | 901-1000 | 14.0 | 0.35 / 0.27 / 0.30 / 0.09 / 0.00 / 0.00 | 0.33 / 0.32 / 0.30 / 0.05 / 0.00 / 0.00 | 0.35 / 0.30 / 0.28 / 0.06 / 0.01 / 0.00 | 1.5 |
| H3 | 1401-1500 | 13.8 | 0.38 / 0.27 / 0.28 / 0.06 / 0.01 / 0.00 | 0.37 / 0.39 / 0.23 / 0.01 / 0.00 / 0.00 | 0.38 / 0.32 / 0.26 / 0.04 / 0.00 / 0.00 | 1.2 |
| H4 | 401-500 | 11.9 | 0.44 / 0.27 / 0.26 / 0.03 / 0.00 / 0.00 | 0.44 / 0.31 / 0.24 / 0.01 / 0.00 / 0.00 | 0.44 / 0.30 / 0.23 / 0.03 / 0.00 / 0.00 | 1.1 |
| H4 | 901-1000 | 14.3 | 0.38 / 0.29 / 0.28 / 0.05 / 0.00 / 0.00 | 0.37 / 0.35 / 0.27 / 0.01 / 0.00 / 0.00 | 0.38 / 0.32 / 0.27 / 0.04 / 0.00 / 0.00 | 1.2 |
| H4 | 1401-1500 | 15.8 | 0.38 / 0.30 / 0.28 / 0.04 / 0.00 / 0.00 | 0.35 / 0.32 / 0.28 / 0.04 / 0.00 / 0.00 | 0.38 / 0.30 / 0.28 / 0.04 / 0.00 / 0.00 | 1.3 |

H3 mean genome depth over all eleven windows 401-1500: 1.0-1.5; H4: 1.1-1.3.

| H5 years | herded | maternal line (herd goats) | sire line (herd males) | genome by depth | mean genome depth |
|---|---|---|---|---|---|
| 401-500 | 39.9 | 0.28 / 0.25 / 0.34 / 0.12 / 0.02 / 0.00 | 0.28 / 0.27 / 0.32 / 0.12 / 0.01 / 0.00 | 0.28 / 0.26 / 0.34 / 0.11 / 0.01 / 0.00 | 2.0 |
| 501-600 | 61.1 | 0.25 / 0.22 / 0.33 / 0.16 / 0.04 / 0.00 | 0.25 / 0.28 / 0.35 / 0.10 / 0.02 / 0.00 | 0.25 / 0.25 / 0.35 / 0.12 / 0.02 / 0.00 | 2.3 |
| 601-700 | 80.0 | 0.22 / 0.20 / 0.34 / 0.19 / 0.05 / 0.01 | 0.22 / 0.28 / 0.38 / 0.12 / 0.01 / 0.00 | 0.22 / 0.24 / 0.36 / 0.15 / 0.03 / 0.00 | 2.5 |
| 701-800 | 96.2 | 0.17 / 0.17 / 0.31 / 0.24 / 0.10 / 0.01 | 0.16 / 0.25 / 0.36 / 0.19 / 0.04 / 0.00 | 0.17 / 0.21 / 0.34 / 0.21 / 0.07 / 0.00 | 3.5 |
| 801-900 | 104.1 | 0.13 / 0.14 / 0.29 / 0.24 / 0.17 / 0.03 | 0.12 / 0.21 / 0.34 / 0.23 / 0.09 / 0.00 | 0.13 / 0.17 / 0.32 / 0.25 / 0.11 / 0.01 | 4.5 |
| 901-1000 | 108.0 | 0.12 / 0.12 / 0.28 / 0.26 / 0.17 / 0.05 | 0.11 / 0.18 / 0.31 / 0.25 / 0.13 / 0.02 | 0.12 / 0.15 / 0.29 / 0.25 / 0.17 / 0.03 | 5.5 |
| 1001-1100 | 111.2 | 0.10 / 0.11 / 0.26 / 0.27 / 0.21 / 0.05 | 0.10 / 0.15 / 0.30 / 0.21 / 0.18 / 0.05 | 0.10 / 0.14 / 0.28 / 0.24 / 0.17 / 0.07 | 6.5 |
| 1101-1200 | 116.5 | 0.09 / 0.09 / 0.23 / 0.24 / 0.23 / 0.12 | 0.09 / 0.13 / 0.24 / 0.27 / 0.20 / 0.07 | 0.09 / 0.11 / 0.24 / 0.25 / 0.20 / 0.10 | 7.5 |
| 1201-1300 | 118.2 | 0.08 / 0.08 / 0.20 / 0.22 / 0.22 / 0.20 | 0.08 / 0.12 / 0.26 / 0.20 / 0.20 / 0.13 | 0.08 / 0.10 / 0.23 / 0.23 / 0.22 / 0.14 | 8.4 |
| 1301-1400 | 121.6 | 0.08 / 0.08 / 0.22 / 0.25 / 0.22 / 0.14 | 0.08 / 0.13 / 0.29 / 0.22 / 0.17 / 0.11 | 0.08 / 0.11 / 0.23 / 0.24 / 0.21 / 0.13 | 8.2 |
| 1401-1500 | 116.9 | 0.08 / 0.08 / 0.19 / 0.23 / 0.28 / 0.15 | 0.07 / 0.10 / 0.19 / 0.25 / 0.25 / 0.14 | 0.08 / 0.09 / 0.19 / 0.23 / 0.25 / 0.17 | 9.4 |

H5 by seed (ad hoc script, same files): mean genome depth per century 901-1500, and sire-line shares
(herd males) in 1401-1500:

| seed | 901 | 1001 | 1101 | 1201 | 1301 | 1401 | sire 0-1 | sire 5+ |
|---|---|---|---|---|---|---|---|---|
| 1 | 5.4 | 5.2 | 7.3 | 6.6 | 6.9 | 6.3 | 0.27 | 0.46 |
| 2 | 6.2 | 6.1 | 7.4 | 7.5 | 9.0 | 10.8 | 0.11 | 0.73 |
| 3 | 2.4 | 2.9 | 3.7 | 4.0 | 3.8 | 5.5 | 0.24 | 0.43 |
| 4 | 6.6 | 9.4 | 7.0 | 9.4 | 8.9 | 10.2 | 0.15 | 0.62 |
| 5 | 4.9 | 8.8 | 11.6 | 14.2 | 13.3 | 11.8 | 0.14 | 0.78 |
| 6 | 5.8 | 5.6 | 7.5 | 7.0 | 6.6 | 10.5 | 0.11 | 0.72 |
| 7 | 8.1 | 11.5 | 14.0 | 13.4 | 10.4 | 12.2 | 0.15 | 0.74 |
| 8 | 5.9 | 8.8 | 9.3 | 8.9 | 7.8 | 9.6 | 0.13 | 0.70 |
| 9 | 4.6 | 4.4 | 5.9 | 7.5 | 6.3 | 6.6 | 0.25 | 0.46 |
| 10 | 3.9 | 3.6 | 4.8 | 8.3 | 8.0 | 11.4 | 0.13 | 0.72 |
| 11 | 3.5 | 4.5 | 5.1 | 5.7 | 7.4 | 9.1 | 0.13 | 0.73 |
| 12 | 7.5 | 7.1 | 6.8 | 7.6 | 9.9 | 8.8 | 0.22 | 0.61 |

`trial_summary.py results/gentrace` (last 100 y):

| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) |
|---|---|---|---|---|---|---|
| H3 | 6 | 1500 | 456 | 14 (17 12 15 13 11 14) | 0.84 | -0.04 (-0.04 -0.04 -0.04 -0.03 -0.04 -0.02) |
| H4 | 6 | 1500 | 462 | 16 (14 15 17 19 14 15) | 0.85 | -0.04 (-0.03 -0.03 -0.04 -0.04 -0.04 -0.03) |
| H5 | 12 | 1500 | 545 | 117 (116 130 114 115 117 130 114 82 114 121 118 132) | 0.84 | -0.61 (-0.58 -0.63 -0.65 -0.59 -0.64 -0.52 -0.68 -0.54 -0.67 -0.66 -0.63 -0.58) |

`trait_gaps.py results/gentrace` pools every run in the folder (24 seeds, H3+H4+H5), so its table mixes
conditions and is not recorded here; the H5 trait gaps are those of results/h5long above (identical runs).

## [PRE-REGISTERED 2026-11-02] The staged ladder: H2, H3, H4, H5 switched on in turn
**Question:** Chris (2026-11-02): "can you carry out runs that introduce the H at different times over the
epoch and track how genes respond to each behavioral change? also track the learning parameters in goats
too." How do the herd's genes and learned fears respond to each behaviour change, shown in the grain paper's
figure form (per-trait share of goats per value bucket per year, dashed lines at each change)?
**Settings:** main, code of this entry's commit. New: `schedule` parameter (each 'year:key=value,...' set
applied at the start of that year; no rand draws); year records gain herdFearOfWolves; histograms gain a herd
copy (histHerd; wild = all − herd) and learned fear of wolves and of humans (fearW, fearH; 20 buckets over
0..fearMax 3). tools/staged.json:
- STAGED: H2 from herdingAt 400 (cullRule random, penning 0, offtakeRate 0.1); 700: cullRule opportunity
  (H3); 1000: penning 1 (H4); 1300: guarding 1, provision 2160, kidShelter 1, buckManagement 1, tetherNew 1
  (H5).
- Controls on the same settings: H0 (no humans), H1 (hunting only), H5 (all of H5 from 400).
"Learning parameters": the goats' learned states are fearOfWolves and fearOfHumans. The learning rates
(sensitize, habKid, habAdult, forgetRate, motherLearn) are model-wide constants; a goat's R sets how fast it
sensitises and how long its socialisation window lasts. So the learned fears are what is tracked.
**Method:** `node tools/batch.mjs tools/staged.json results/staged 2200 12 20 STAGED`, then
`... 2200 6 20 H5`, `... 2200 4 20 H0,H1`. Figures: tools/gene_heatmap.py (new), columns herd and wild.
Tables: per 100 y, herded and herd − wild mean per trait and learned fear (ad hoc script, recorded with the
results). Checks before launch (seed 1, 520 y): (a) H5 under the new code vs results/gentrace H5 seed 1,
herdFearOfWolves removed: 0 differing years, histograms identical; (b) H2 + schedule '0:<H5 settings>' vs (a):
identical; (c) H2 + schedule '400:<H5 settings>' vs (a): identical unless some H5 setting acts before
herding starts.
Check results (2026-11-02, results/schedcheck): (a) 0 of 520 years differ, all trait histograms identical,
herd histogram total = herded (66 in year 519); (b) 0 years, 0 histogram rows differ, final cullRule
opportunity, guarding 1; (c) the same, 0 and 0. Instrument check: a first attempt of (b) and (c) passed an
empty schedule and no H2 settings (a shell error) and differed from (a) in 120 of 520 years.
**Prediction:**
- H2-H4 stages (400-1300): herds 10-16 goats per camp-year as in results/gentrace; herd − wild R gap no wider
  than −0.06 in any century; no other trait gap beyond ±0.05.
- After 1300 (H5): herds pass 80 within 300 years; the R gap reaches −0.45 or wider by 1900-2000 and −0.55
  or wider by 2100-2200, within 0.1 of H5-from-400 at the same time since H5 began (results/gentrace
  901-1000 and 1101-1200): the earlier stages neither speed nor slow it much. Body size gap lags R by 100-300
  years, as in results/h5long.
- Learned fear of humans: herd far below wild from H2 on (H5 seed 1 in results/gentrace: herd about 0.14,
  all goats about 0.9). Learned fear of wolves: no prediction.

**Raw results (2026-11-02):** batch done, 26 runs of 2,200 years, 0 failures. Figure:
`python tools/gene_heatmap.py results/staged results/staged/fig/staged_genes.png H0:all H1:all STAGED:herd
STAGED:wild H5:herd` (all ten rows; not in git, results/ is ignored). "herded" below is the total over the
three camps, the same unit as results/gentrace, not per camp.

`stage_table.py results/staged` (new tool; H0 and H1 shown at 301-400, 1201-1300, 2101-2200 only, the other windows within 0.03 of these):

results: results/staged | windows of 100 y from year 301 | herd − wild genetic mean per trait | learned fear herd / wild | means over seeds

### H0 (n 4)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.38 | — / 1.00 |
| 1201-1300 | 0.0 | — | — | — | — | — | — | — | — | — / 1.41 | — / 1.00 |
| 2101-2200 | 0.0 | — | — | — | — | — | — | — | — | — / 1.40 | — / 1.00 |

### H1 (n 4)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.18 | — / 1.14 |
| 1201-1300 | 0.0 | — | — | — | — | — | — | — | — | — / 1.10 | — / 1.11 |
| 2101-2200 | 0.0 | — | — | — | — | — | — | — | — | — / 1.10 | — / 1.11 |

### H5 (n 6)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.17 | — / 1.14 |
| 401-500 | 41.2 | -0.05 | +0.00 | +0.01 | -0.02 | +0.00 | +0.01 | -0.00 | +0.00 | 1.22 / 1.13 | 0.15 / 1.09 |
| 501-600 | 57.5 | -0.10 | -0.01 | +0.02 | -0.03 | -0.01 | +0.04 | +0.00 | -0.01 | 1.17 / 1.16 | 0.15 / 1.10 |
| 601-700 | 74.9 | -0.18 | -0.00 | +0.04 | -0.05 | -0.03 | +0.07 | +0.02 | -0.00 | 1.14 / 1.17 | 0.15 / 1.10 |
| 701-800 | 94.9 | -0.34 | -0.00 | +0.05 | -0.12 | -0.02 | +0.09 | +0.02 | +0.03 | 1.09 / 1.16 | 0.14 / 1.10 |
| 801-900 | 101.3 | -0.43 | -0.01 | +0.03 | -0.20 | +0.00 | +0.12 | +0.02 | +0.01 | 1.07 / 1.14 | 0.14 / 1.09 |
| 901-1000 | 105.6 | -0.47 | -0.03 | +0.06 | -0.30 | -0.03 | +0.10 | +0.05 | -0.02 | 1.06 / 1.14 | 0.14 / 1.09 |
| 1001-1100 | 109.6 | -0.54 | -0.04 | +0.09 | -0.41 | -0.02 | +0.08 | +0.04 | -0.01 | 1.05 / 1.14 | 0.14 / 1.09 |
| 1101-1200 | 117.1 | -0.58 | -0.01 | +0.15 | -0.53 | -0.03 | +0.06 | +0.03 | +0.01 | 1.04 / 1.13 | 0.14 / 1.09 |
| 1201-1300 | 121.0 | -0.60 | -0.02 | +0.13 | -0.59 | -0.04 | +0.03 | +0.04 | +0.05 | 1.03 / 1.12 | 0.14 / 1.09 |
| 1301-1400 | 123.6 | -0.60 | -0.03 | +0.14 | -0.65 | -0.08 | -0.01 | +0.05 | +0.04 | 1.03 / 1.12 | 0.14 / 1.09 |
| 1401-1500 | 112.1 | -0.60 | +0.00 | +0.15 | -0.65 | -0.08 | +0.01 | +0.03 | +0.03 | 1.04 / 1.12 | 0.14 / 1.09 |
| 1501-1600 | 123.1 | -0.62 | -0.00 | +0.13 | -0.68 | -0.08 | +0.03 | +0.03 | +0.03 | 1.03 / 1.12 | 0.14 / 1.09 |
| 1601-1700 | 121.1 | -0.63 | -0.00 | +0.14 | -0.72 | -0.08 | +0.00 | +0.04 | -0.01 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1701-1800 | 122.3 | -0.63 | -0.02 | +0.12 | -0.71 | -0.07 | -0.02 | +0.04 | -0.01 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1801-1900 | 123.5 | -0.65 | -0.04 | +0.13 | -0.76 | -0.05 | -0.01 | +0.03 | -0.02 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1901-2000 | 120.8 | -0.65 | -0.03 | +0.13 | -0.73 | -0.04 | -0.02 | +0.02 | -0.02 | 1.03 / 1.13 | 0.14 / 1.09 |
| 2001-2100 | 119.9 | -0.65 | -0.04 | +0.13 | -0.71 | -0.03 | -0.01 | +0.04 | -0.02 | 1.03 / 1.13 | 0.14 / 1.09 |
| 2101-2200 | 124.4 | -0.66 | -0.04 | +0.12 | -0.72 | -0.04 | +0.01 | +0.03 | -0.03 | 1.03 / 1.12 | 0.14 / 1.09 |

### STAGED (n 12)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.17 | — / 1.14 |
| 401-500 | 9.3 | -0.03 | +0.01 | +0.01 | -0.00 | +0.01 | +0.00 | +0.00 | +0.01 | 1.71 / 1.11 | 0.17 / 1.10 |
| 501-600 | 9.1 | -0.03 | -0.00 | +0.00 | -0.00 | +0.01 | +0.01 | +0.01 | -0.01 | 1.73 / 1.11 | 0.17 / 1.10 |
| 601-700 | 10.0 | -0.03 | +0.00 | +0.00 | -0.00 | +0.00 | +0.00 | -0.00 | -0.01 | 1.65 / 1.10 | 0.16 / 1.09 |
| 701-800 | 11.8 | -0.03 | +0.00 | +0.01 | -0.00 | +0.00 | +0.01 | +0.00 | +0.01 | 1.63 / 1.10 | 0.16 / 1.09 |
| 801-900 | 11.6 | -0.02 | -0.00 | +0.01 | -0.00 | -0.00 | +0.01 | +0.00 | -0.00 | 1.67 / 1.11 | 0.16 / 1.09 |
| 901-1000 | 11.3 | -0.03 | -0.00 | -0.00 | -0.00 | -0.00 | +0.00 | +0.00 | +0.00 | 1.67 / 1.11 | 0.16 / 1.09 |
| 1001-1100 | 15.4 | -0.03 | +0.00 | +0.01 | -0.00 | -0.00 | +0.01 | +0.01 | +0.00 | 1.64 / 1.11 | 0.16 / 1.09 |
| 1101-1200 | 15.0 | -0.03 | +0.01 | +0.00 | -0.01 | -0.00 | +0.01 | +0.00 | +0.00 | 1.67 / 1.11 | 0.16 / 1.09 |
| 1201-1300 | 14.9 | -0.03 | +0.00 | +0.00 | -0.00 | -0.00 | -0.01 | -0.00 | +0.00 | 1.68 / 1.11 | 0.16 / 1.09 |
| 1301-1400 | 42.8 | -0.06 | -0.00 | +0.00 | -0.01 | -0.01 | +0.02 | +0.00 | -0.00 | 1.20 / 1.13 | 0.15 / 1.09 |
| 1401-1500 | 60.2 | -0.10 | +0.00 | +0.01 | -0.03 | -0.00 | +0.05 | +0.01 | +0.01 | 1.16 / 1.17 | 0.15 / 1.10 |
| 1501-1600 | 83.4 | -0.20 | -0.00 | +0.01 | -0.08 | +0.01 | +0.07 | +0.01 | +0.02 | 1.13 / 1.19 | 0.15 / 1.10 |
| 1601-1700 | 97.5 | -0.31 | -0.02 | +0.01 | -0.17 | +0.00 | +0.08 | +0.02 | +0.00 | 1.10 / 1.18 | 0.14 / 1.10 |
| 1701-1800 | 107.1 | -0.40 | -0.04 | +0.03 | -0.27 | -0.01 | +0.08 | +0.01 | -0.02 | 1.07 / 1.16 | 0.14 / 1.09 |
| 1801-1900 | 116.3 | -0.48 | -0.04 | +0.05 | -0.37 | -0.01 | +0.10 | +0.02 | -0.02 | 1.05 / 1.15 | 0.14 / 1.09 |
| 1901-2000 | 118.7 | -0.55 | -0.05 | +0.04 | -0.49 | -0.03 | +0.09 | +0.02 | -0.01 | 1.04 / 1.14 | 0.14 / 1.09 |
| 2001-2100 | 118.1 | -0.58 | -0.07 | +0.05 | -0.57 | -0.03 | +0.08 | +0.02 | -0.02 | 1.04 / 1.13 | 0.14 / 1.09 |
| 2101-2200 | 123.6 | -0.61 | -0.08 | +0.06 | -0.63 | -0.03 | +0.04 | +0.03 | -0.02 | 1.03 / 1.12 | 0.14 / 1.09 |

## [NOT PRE-REGISTERED 2026-11-03] Gene-load delays: calibration of k on H0 and H1
Launched without a pre-registration entry, my omission; recorded here as it ran, raw results only.
**Question:** Chris (2026-11-03): the genome cost is too weak to make horns and aggression fall in H5 herds;
the grain model summed its genes and charged the load as a fixed delay. "let's do 1 and 2 and see the impact."
**Settings:** main, code of this entry's commit. New: Goat.load = sum of expressed trait values (0..8);
loadFirstBreed (days added to femaleMinAge / maleMinAge per unit of load, used for does' heat, bucks' mate
seeking, mating and the herder's sire choice; the herder's cull valuation still uses the fixed ages);
loadRecovery (days after kidding before a doe can conceive again, per unit of load). Both default 0. The old
per-mating fertility and growth costs (mean trait value, weight 0.5) unchanged.
**Method:** tools/loadcal.json: H0 and H1 with loadFirstBreed = loadRecovery = k, k 0/15/30/60;
`node tools/batch.mjs tools/loadcal.json results/loadcal 800 2 16`; summary tools/loadcal_sum.py.
Checks (seed 1, 520 y, H5): defaults vs results/schedcheck/H5.json: 0 of 520 years and 0 histogram rows
differ; k 30: 520 of 520 years differ.
**Raw results:** `loadcal_sum.py results/loadcal 500 800`:

years 501-800, means over seeds (n)
| cond | n | goats | births/y | births per goat | median 1st kid age (d) | load | R | A | S | B | H | T | M | W |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0k0 | 2 | 516 | 135 | 0.261 | 1049 | 4.40 | 0.65 | 0.73 | 0.30 | 0.91 | 0.82 | 0.38 | 0.16 | 0.45 |
| H0k15 | 2 | 515 | 134 | 0.260 | 1042 | 4.48 | 0.65 | 0.70 | 0.29 | 0.89 | 0.83 | 0.42 | 0.17 | 0.54 |
| H0k30 | 2 | 538 | 143 | 0.265 | 1070 | 4.58 | 0.66 | 0.73 | 0.31 | 0.89 | 0.83 | 0.48 | 0.16 | 0.53 |
| H0k60 | 2 | 496 | 108 | 0.217 | 1061 | 4.24 | 0.67 | 0.67 | 0.20 | 0.89 | 0.74 | 0.57 | 0.14 | 0.36 |
| H1k0 | 2 | 441 | 105 | 0.238 | 1057 | 4.66 | 0.86 | 0.74 | 0.23 | 0.90 | 0.80 | 0.37 | 0.17 | 0.58 |
| H1k15 | 2 | 448 | 109 | 0.243 | 1046 | 4.61 | 0.87 | 0.70 | 0.24 | 0.90 | 0.80 | 0.45 | 0.15 | 0.50 |
| H1k30 | 2 | 451 | 113 | 0.250 | 1069 | 4.58 | 0.86 | 0.79 | 0.23 | 0.88 | 0.76 | 0.49 | 0.16 | 0.41 |
| H1k60 | 2 | 409 | 82 | 0.200 | 1072 | 4.40 | 0.89 | 0.66 | 0.17 | 0.88 | 0.72 | 0.55 | 0.14 | 0.40 |

Load spread between goats (seed 1, year 800, sum of per-trait variances from the histograms, traits taken as
independent): sd 0.23 (H0k0), 0.28 (H0k60), 0.25 (H1k30). Rut half-width from mean T, 15 + 120 T days: 62
(H0k0), 85 (H0k60), 73 (H1k30).

## [PRE-REGISTERED 2026-11-03] Gene load on growth: calibration of c on H0 and H1
**Question:** Chris (2026-11-03): "try the growth version". The delays to first breeding and recovery
(entry above) barely select on load, since breeding is seasonal and does first conceive at about 2.5 years,
held back by size and condition, not age. Charge the load on growth to breeding size instead, the grain
model's germination delay. How strongly does it select on load in the wild, and which traits give way?
**Settings:** main, code of this entry's commit. New: loadGrowth c: growth rate = growthAbs × (1 − 0.5 ×
loadRef / 8) / max(0.2, 1 + c × (load − loadRef)), loadRef 4.4; this replaces the old growth cost (mean trait
value, weight 0.5) when c > 0; at load = loadRef the rate equals the old cost's at the same load. The old cost's
slope is about 8.6% of growth rate per unit of load at 4.4; c is the slope of growth time per unit. The
per-mating fertility cost is unchanged. tools/growcal.json: H0 and H1, c 0.1 / 0.33 / 1; baseline c 0 =
results/loadcal H0k0, H1k0 (same seeds 1-2, same code path when the new parameters are 0).
**Method:** `node tools/batch.mjs tools/growcal.json results/growcal 800 2 12`; tools/loadcal_sum.py,
years 501-800. Check: H5 seed 1, 520 y, defaults vs results/schedcheck/H5.json: 0 differing years.
**Prediction:**
- c 0.1 behaves like c 0: load within 0.15 of the baseline (4.40 H0, 4.66 H1).
- c 0.33: load falls by at least 0.3 against the baseline in both H0 and H1; median first-kid age within
  100 days of the baseline (about 1,050); goats within 25% of the baseline.
- c 1: load falls by at least 0.6; goats may fall by more than 25%.
- Which traits give way: those with little wild benefit first (T, W, S, M); horns and aggression, held by
  contests, fall least; R held up in H1 by hunting. Body size B may fall at c 1, since a larger target also
  takes longer to grow on its own.

**Raw results (2026-11-03):** batch done, 12 runs, 0 failures. Check: defaults vs results/schedcheck/H5.json:
0 of 520 years differ. `loadcal_sum.py` on results/growcal with results/loadcal H0k0, H1k0 (c 0) alongside,
years 501-800:

years 501-800, means over seeds (n)
| cond | n | goats | births/y | births per goat | median 1st kid age (d) | load | R | A | S | B | H | T | M | W |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0c01 | 2 | 517 | 133 | 0.257 | 1056 | 4.52 | 0.66 | 0.71 | 0.35 | 0.90 | 0.82 | 0.38 | 0.16 | 0.55 |
| H0c033 | 2 | 521 | 134 | 0.256 | 1065 | 4.57 | 0.67 | 0.77 | 0.32 | 0.91 | 0.81 | 0.36 | 0.18 | 0.56 |
| H0c1 | 2 | 526 | 138 | 0.262 | 1014 | 4.04 | 0.64 | 0.68 | 0.15 | 0.89 | 0.81 | 0.35 | 0.16 | 0.37 |
| H0k0 | 2 | 516 | 135 | 0.261 | 1049 | 4.40 | 0.65 | 0.73 | 0.30 | 0.91 | 0.82 | 0.38 | 0.16 | 0.45 |
| H1c01 | 2 | 439 | 106 | 0.240 | 1055 | 4.54 | 0.86 | 0.72 | 0.29 | 0.90 | 0.79 | 0.38 | 0.15 | 0.46 |
| H1c033 | 2 | 447 | 109 | 0.243 | 1056 | 4.56 | 0.86 | 0.77 | 0.20 | 0.90 | 0.81 | 0.41 | 0.17 | 0.44 |
| H1c1 | 2 | 445 | 109 | 0.244 | 1047 | 4.36 | 0.86 | 0.68 | 0.17 | 0.90 | 0.81 | 0.43 | 0.14 | 0.37 |
| H1k0 | 2 | 441 | 105 | 0.238 | 1057 | 4.66 | 0.86 | 0.74 | 0.23 | 0.90 | 0.80 | 0.37 | 0.17 | 0.58 |

Addendum (not pre-registered; new tool tools/breed_probe.mjs, no rand draws): which gate holds young does
back, counted on three days around the rut peak for every doe that has never kidded; and first-kid age by
load (does below vs at or above the median load of first kidders).

H0c0 (seed 1, humansPerCamp 0; years 200-400; probe days [285, 330, 15]):
| age y | n | age ok | size ok | condition ok | in season | size+cond | all | load size ok / not |
|---|---|---|---|---|---|---|---|---|
| 1 | 22700 | 0.99 | 0.67 | 0.35 | 0.89 | 0.26 | 0.22 | 4.18 / 4.24 |
| 2 | 12141 | 1.00 | 1.00 | 0.86 | 0.86 | 0.86 | 0.75 | 4.20 / 0.00 |
| 3 | 1666 | 1.00 | 1.00 | 0.88 | 0.79 | 0.88 | 0.71 | 4.17 / 0.00 |
| 4 | 272 | 1.00 | 1.00 | 0.88 | 0.63 | 0.88 | 0.56 | 4.07 / 0.00 |
| 5 | 84 | 1.00 | 1.00 | 0.89 | 0.49 | 0.89 | 0.48 | 4.05 / 0.00 |
first kids 5536, age median 1041, quartiles 737 / 1094; median first-kid age, low-load half 1046, high-load half 1037

H0c1 (seed 1, humansPerCamp 0, loadGrowth 1; years 200-400; probe days [285, 330, 15]):
| age y | n | age ok | size ok | condition ok | in season | size+cond | all | load size ok / not |
|---|---|---|---|---|---|---|---|---|
| 1 | 22684 | 0.99 | 0.75 | 0.41 | 0.86 | 0.33 | 0.27 | 4.06 / 4.47 |
| 2 | 11487 | 1.00 | 1.00 | 0.85 | 0.85 | 0.85 | 0.72 | 4.24 / 5.25 |
| 3 | 1524 | 1.00 | 1.00 | 0.87 | 0.73 | 0.87 | 0.63 | 4.21 / 0.00 |
| 4 | 249 | 1.00 | 1.00 | 0.88 | 0.58 | 0.88 | 0.53 | 4.13 / 0.00 |
| 5 | 63 | 1.00 | 1.00 | 0.84 | 0.48 | 0.84 | 0.40 | 4.04 / 0.00 |
first kids 5677, age median 1029, quartiles 736 / 1089; median first-kid age, low-load half 773, high-load half 1055


## [PRE-REGISTERED 2026-11-03] Gene load on growth in H5 and staged herds: do horns and aggression fall?
**Question:** Chris (2026-11-03): why do horns and aggression not fall in H5 herds, where contests are gone
and wolves rarely kill? With the load charged on growth (entry above), the low-load half of does first kids a
year earlier at c 1, so the channel exists; in the wild each trait's benefit holds the load up. Does the
herd, without those benefits for horns and aggression, shed them?
**Settings:** main, code 75b1f8a (no code change). tools/growherd.json: H5c033 (H5 + loadGrowth 0.33),
H5c1 (H5 + loadGrowth 1), STAGEDc1 (STAGED + loadGrowth 1). Baselines with loadGrowth 0: results/staged H5
seeds 1-6 and STAGED seeds 1-8. Note: under buck management the sires are the oldest herd bucks, so the
growth cost selects through does only.
**Method:** `node tools/batch.mjs tools/growherd.json results/growherd 2200 6 12 H5c033,H5c1` and
`node tools/batch.mjs tools/growherd.json results/growherd 2200 8 8 STAGEDc1`; tools/stage_table.py, and
tools/gene_heatmap.py columns H5c1:herd, H5c1:wild, STAGEDc1:herd, STAGEDc1:wild.
**Prediction:**
- H5c1, years 1901-2200: herd − wild gap in H at -0.15 or wider and in A at -0.15 or wider (baseline H5:
  about -0.04 each). H5c033: both between the baseline and H5c1, at -0.07 or wider.
- R and B gaps at least as wide as the baseline (-0.66, -0.72); herd size within 15% of the baseline (about
  122).
- STAGEDc1: no H or A gap beyond ±0.05 before 1300 (contests and wolf defence still matter in H2-H4 herds);
  after 1300 the same as H5c1 at the same time since H5 began.
- Wild goats: load within 0.4 of the calibration's c 1 value (4.04 H0, 4.36 H1).

**Raw results (2026-11-03):** batch done, 20 runs, 0 failures. `tools/stage_table.py results/growherd`:


### H5c033 (n 6)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.17 | — / 1.14 |
| 401-500 | 42.2 | -0.07 | +0.00 | +0.01 | -0.01 | -0.01 | +0.04 | -0.01 | -0.02 | 1.23 / 1.13 | 0.15 / 1.10 |
| 501-600 | 68.6 | -0.15 | +0.01 | +0.02 | -0.03 | -0.00 | +0.08 | +0.00 | +0.02 | 1.14 / 1.17 | 0.15 / 1.10 |
| 601-700 | 90.9 | -0.26 | -0.01 | +0.02 | -0.07 | +0.01 | +0.10 | +0.00 | -0.01 | 1.12 / 1.19 | 0.15 / 1.10 |
| 701-800 | 104.7 | -0.36 | -0.02 | +0.05 | -0.17 | -0.00 | +0.11 | +0.01 | +0.04 | 1.08 / 1.18 | 0.14 / 1.10 |
| 801-900 | 111.5 | -0.46 | -0.02 | +0.11 | -0.32 | -0.03 | +0.09 | +0.00 | +0.04 | 1.06 / 1.15 | 0.14 / 1.09 |
| 901-1000 | 114.2 | -0.54 | -0.02 | +0.12 | -0.44 | -0.02 | +0.08 | +0.02 | +0.04 | 1.05 / 1.13 | 0.14 / 1.09 |
| 1001-1100 | 118.0 | -0.59 | -0.04 | +0.10 | -0.53 | -0.01 | +0.08 | +0.02 | +0.03 | 1.04 / 1.13 | 0.14 / 1.09 |
| 1101-1200 | 113.6 | -0.61 | -0.02 | +0.11 | -0.59 | -0.03 | +0.06 | +0.02 | +0.03 | 1.03 / 1.12 | 0.14 / 1.08 |
| 1201-1300 | 117.1 | -0.62 | -0.02 | +0.11 | -0.61 | -0.05 | +0.03 | +0.04 | +0.02 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1301-1400 | 117.2 | -0.63 | -0.01 | +0.10 | -0.68 | -0.04 | +0.01 | +0.04 | +0.01 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1401-1500 | 119.6 | -0.64 | -0.01 | +0.10 | -0.69 | -0.04 | +0.02 | +0.06 | -0.03 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1501-1600 | 117.9 | -0.63 | -0.02 | +0.12 | -0.69 | -0.04 | +0.02 | +0.04 | -0.03 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1601-1700 | 118.9 | -0.64 | -0.06 | +0.14 | -0.69 | -0.05 | +0.01 | +0.04 | -0.03 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1701-1800 | 116.5 | -0.63 | -0.03 | +0.15 | -0.62 | -0.03 | -0.01 | +0.04 | +0.01 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1801-1900 | 122.5 | -0.67 | +0.01 | +0.16 | -0.68 | -0.01 | +0.00 | +0.06 | -0.00 | 1.02 / 1.12 | 0.14 / 1.09 |
| 1901-2000 | 118.5 | -0.66 | +0.01 | +0.12 | -0.70 | +0.01 | +0.01 | +0.06 | +0.01 | 1.03 / 1.13 | 0.14 / 1.09 |
| 2001-2100 | 117.8 | -0.66 | +0.02 | +0.11 | -0.71 | +0.03 | +0.01 | +0.06 | +0.04 | 1.03 / 1.13 | 0.14 / 1.09 |
| 2101-2200 | 121.5 | -0.66 | +0.02 | +0.13 | -0.71 | -0.00 | +0.03 | +0.04 | +0.04 | 1.03 / 1.12 | 0.14 / 1.09 |

### H5c1 (n 6)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.18 | — / 1.15 |
| 401-500 | 40.1 | -0.05 | +0.01 | +0.02 | -0.00 | -0.00 | +0.03 | +0.01 | +0.00 | 1.23 / 1.14 | 0.15 / 1.10 |
| 501-600 | 63.8 | -0.11 | +0.01 | +0.03 | -0.01 | +0.01 | +0.06 | +0.00 | +0.03 | 1.15 / 1.17 | 0.15 / 1.10 |
| 601-700 | 84.0 | -0.19 | -0.01 | +0.03 | -0.04 | +0.01 | +0.11 | +0.03 | +0.03 | 1.13 / 1.20 | 0.15 / 1.10 |
| 701-800 | 101.2 | -0.29 | -0.02 | +0.05 | -0.09 | +0.01 | +0.17 | +0.03 | +0.06 | 1.10 / 1.19 | 0.15 / 1.10 |
| 801-900 | 107.4 | -0.38 | -0.02 | +0.10 | -0.16 | -0.01 | +0.19 | +0.07 | +0.11 | 1.08 / 1.17 | 0.14 / 1.10 |
| 901-1000 | 106.8 | -0.42 | -0.00 | +0.12 | -0.21 | -0.02 | +0.18 | +0.06 | +0.09 | 1.07 / 1.16 | 0.14 / 1.09 |
| 1001-1100 | 108.5 | -0.46 | +0.02 | +0.11 | -0.27 | -0.02 | +0.15 | +0.04 | +0.08 | 1.06 / 1.15 | 0.14 / 1.09 |
| 1101-1200 | 113.4 | -0.52 | +0.02 | +0.10 | -0.39 | -0.01 | +0.16 | +0.04 | +0.09 | 1.05 / 1.14 | 0.14 / 1.09 |
| 1201-1300 | 118.7 | -0.55 | +0.01 | +0.14 | -0.47 | -0.00 | +0.21 | +0.00 | +0.08 | 1.04 / 1.14 | 0.14 / 1.09 |
| 1301-1400 | 118.6 | -0.59 | -0.02 | +0.16 | -0.58 | -0.00 | +0.19 | -0.02 | +0.05 | 1.04 / 1.14 | 0.14 / 1.09 |
| 1401-1500 | 120.4 | -0.63 | -0.04 | +0.17 | -0.63 | +0.00 | +0.15 | -0.01 | +0.03 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1501-1600 | 113.7 | -0.59 | -0.03 | +0.18 | -0.59 | -0.01 | +0.11 | +0.01 | +0.03 | 1.04 / 1.13 | 0.14 / 1.09 |
| 1601-1700 | 122.0 | -0.61 | -0.01 | +0.17 | -0.65 | -0.02 | +0.09 | +0.02 | +0.00 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1701-1800 | 117.4 | -0.63 | -0.01 | +0.16 | -0.68 | -0.00 | +0.04 | +0.04 | -0.01 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1801-1900 | 119.8 | -0.64 | -0.01 | +0.13 | -0.71 | -0.04 | +0.06 | +0.05 | -0.07 | 1.03 / 1.13 | 0.14 / 1.09 |
| 1901-2000 | 116.3 | -0.62 | -0.01 | +0.09 | -0.70 | -0.04 | +0.01 | +0.03 | -0.04 | 1.03 / 1.13 | 0.14 / 1.09 |
| 2001-2100 | 117.3 | -0.65 | +0.00 | +0.09 | -0.70 | -0.04 | +0.03 | +0.02 | -0.02 | 1.03 / 1.13 | 0.14 / 1.09 |
| 2101-2200 | 116.7 | -0.64 | +0.01 | +0.06 | -0.71 | -0.02 | +0.03 | +0.02 | +0.04 | 1.03 / 1.13 | 0.14 / 1.09 |

### STAGEDc1 (n 8)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.18 | — / 1.15 |
| 401-500 | 10.8 | -0.03 | +0.00 | +0.01 | +0.00 | -0.00 | -0.00 | -0.00 | +0.00 | 1.71 / 1.12 | 0.17 / 1.10 |
| 501-600 | 11.8 | -0.04 | +0.01 | +0.00 | +0.00 | -0.00 | -0.00 | +0.00 | +0.00 | 1.67 / 1.12 | 0.16 / 1.10 |
| 601-700 | 11.8 | -0.03 | +0.01 | +0.00 | -0.00 | +0.00 | +0.00 | -0.00 | +0.01 | 1.67 / 1.12 | 0.16 / 1.10 |
| 701-800 | 12.1 | -0.03 | -0.00 | +0.01 | -0.00 | +0.00 | +0.01 | -0.00 | +0.00 | 1.66 / 1.12 | 0.16 / 1.10 |
| 801-900 | 12.3 | -0.03 | -0.00 | +0.00 | -0.00 | -0.00 | +0.01 | +0.00 | -0.00 | 1.68 / 1.12 | 0.16 / 1.10 |
| 901-1000 | 13.0 | -0.03 | +0.01 | +0.01 | -0.00 | -0.00 | +0.01 | -0.01 | +0.00 | 1.65 / 1.12 | 0.16 / 1.10 |
| 1001-1100 | 15.5 | -0.03 | +0.01 | +0.00 | -0.00 | -0.00 | +0.00 | +0.00 | +0.01 | 1.66 / 1.12 | 0.16 / 1.10 |
| 1101-1200 | 14.9 | -0.03 | -0.01 | +0.00 | -0.01 | -0.00 | +0.01 | +0.01 | -0.01 | 1.67 / 1.11 | 0.16 / 1.10 |
| 1201-1300 | 13.8 | -0.03 | +0.00 | -0.00 | -0.00 | +0.00 | +0.00 | +0.00 | -0.00 | 1.66 / 1.11 | 0.16 / 1.10 |
| 1301-1400 | 46.6 | -0.07 | +0.00 | +0.01 | -0.01 | -0.00 | +0.03 | +0.01 | +0.01 | 1.19 / 1.14 | 0.15 / 1.09 |
| 1401-1500 | 68.1 | -0.14 | +0.02 | +0.01 | -0.02 | +0.00 | +0.06 | +0.03 | +0.02 | 1.14 / 1.18 | 0.15 / 1.10 |
| 1501-1600 | 82.4 | -0.20 | +0.02 | +0.01 | -0.05 | -0.01 | +0.08 | +0.02 | +0.04 | 1.13 / 1.19 | 0.15 / 1.10 |
| 1601-1700 | 87.8 | -0.27 | +0.03 | +0.02 | -0.09 | -0.01 | +0.10 | +0.03 | +0.04 | 1.11 / 1.18 | 0.15 / 1.10 |
| 1701-1800 | 96.4 | -0.35 | +0.02 | +0.03 | -0.14 | -0.01 | +0.11 | +0.03 | +0.05 | 1.09 / 1.17 | 0.14 / 1.09 |
| 1801-1900 | 100.4 | -0.40 | +0.02 | +0.04 | -0.21 | -0.01 | +0.12 | +0.03 | +0.07 | 1.08 / 1.16 | 0.14 / 1.09 |
| 1901-2000 | 103.4 | -0.46 | +0.03 | +0.06 | -0.29 | -0.00 | +0.13 | +0.03 | +0.11 | 1.07 / 1.15 | 0.14 / 1.09 |
| 2001-2100 | 111.5 | -0.50 | +0.00 | +0.08 | -0.34 | -0.01 | +0.13 | +0.04 | +0.12 | 1.05 / 1.15 | 0.14 / 1.09 |
| 2101-2200 | 112.0 | -0.57 | -0.01 | +0.09 | -0.43 | -0.01 | +0.12 | +0.06 | +0.15 | 1.04 / 1.14 | 0.14 / 1.09 |

Absolute means, years 1901-2200, herd and wild (wild = all − herd), with the sum over traits (the gene
load), baselines alongside; new tool tools/herd_wild_means.py:
```
H5 goats 559 herd 122 | herd R0.19 A0.72 S0.25 B0.16 H0.80 T0.39 M0.18 W0.51 sum 3.19 | wild R0.84 A0.75 S0.12 B0.89 H0.83 T0.39 M0.15 W0.53 sum 4.51
H5c033 goats 558 herd 119 | herd R0.18 A0.80 S0.25 B0.19 H0.85 T0.44 M0.21 W0.69 sum 3.61 | wild R0.84 A0.78 S0.13 B0.89 H0.84 T0.42 M0.16 W0.66 sum 4.72
H5c1 goats 560 herd 117 | herd R0.20 A0.74 S0.22 B0.17 H0.78 T0.43 M0.17 W0.63 sum 3.34 | wild R0.84 A0.74 S0.14 B0.88 H0.81 T0.40 M0.15 W0.64 sum 4.59
STAGED goats 547 herd 120 | herd R0.26 A0.69 S0.19 B0.31 H0.80 T0.48 M0.18 W0.55 sum 3.47 | wild R0.84 A0.76 S0.14 B0.87 H0.83 T0.41 M0.16 W0.57 sum 4.57
STAGEDc1 goats 544 herd 109 | herd R0.32 A0.78 S0.22 B0.50 H0.83 T0.59 M0.20 W0.67 sum 4.11 | wild R0.83 A0.78 S0.15 B0.86 H0.83 T0.46 M0.16 W0.54 sum 4.61
```
Figure: results/growherd/fig/growherd_genes.png (`tools/gene_heatmap.py results/growherd ... H5c1:herd
H5c1:wild STAGEDc1:herd STAGEDc1:wild H5c033:herd`).


## [PRE-REGISTERED 2026-11-03] No genome cost: H0, H1, H5 and the staged ladder with the costs off
**Question:** Chris (2026-11-03): "turn off all genetic costs and see what that does to our results." Which of
our results (herd sizes, the herd − wild gaps in R and B, wild trait means) depend on the genome cost?
**Settings:** main, code aa6dd92 (no code change). tools/nocost.json: tools/staged.json's H0, H1, H5, STAGED
with reproCostGrowth 0 and reproCostFertility 0 (fertility() = 1, growth × 1); loadFirstBreed, loadRecovery,
loadGrowth are 0 by default. Trait-specific costs stay (milk kcal, growth kcal per size, display and contact
kcal, contest injury). Not compensated: the mean conception chance per mating rises from about
0.7 × (1 − 0.5 × 0.56)² ≈ 0.36 to 0.7, and growth runs about 1.4 × faster, so demography changes along with
selection. Baselines: results/staged H0 (4 seeds), H1 (4), H5 (6), STAGED (12), code a6933ba, the same
model (load parameters default 0, checked 0 of 520 years differ).
**Method:** `node tools/batch.mjs tools/nocost.json results/nocost 2200 <seeds> <conc> <cond>`: H0nc 4 seeds,
H1nc 4, H5nc 6, STAGEDnc 8; tools/stage_table.py, tools/herd_wild_means.py (extended to these conditions),
tools/gene_heatmap.py.
**Prediction** (years 1901-2200 unless stated):
- Wild load rises: H0nc and H1nc load at least 0.3 above baseline (4.45 H0, 4.53 H1), mostly in S, T, W
  (low wild benefit); M stays below 0.3 (its own kcal cost). Wild goats within 10% of baseline (509 H0,
  436 H1): food limits them, not births.
- H5nc herd − wild gaps: R within 0.15 of baseline (-0.66), B within 0.15 of baseline (-0.72), i.e. both
  are driven by herding, not the cost; H and A gaps within ±0.05.
- Herd sizes larger: H5nc herd at least 10% above baseline (about 122); STAGEDnc H2-H4 stages (years
  401-1300) at least 10% above baseline (9-15).
- STAGEDnc after 1300: R and B gaps track H5nc at the same time since H5 began, within 0.15.


**Raw results (2026-11-03):** batch done, 22 runs, 0 failures. `tools/stage_table.py results/nocost`:


### H0nc (n 4)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.43 | — / 1.00 |
| 401-500 | 0.0 | — | — | — | — | — | — | — | — | — / 1.44 | — / 1.00 |
| 501-600 | 0.0 | — | — | — | — | — | — | — | — | — / 1.44 | — / 1.00 |
| 601-700 | 0.0 | — | — | — | — | — | — | — | — | — / 1.44 | — / 1.00 |
| 701-800 | 0.0 | — | — | — | — | — | — | — | — | — / 1.44 | — / 1.00 |
| 801-900 | 0.0 | — | — | — | — | — | — | — | — | — / 1.44 | — / 1.00 |
| 901-1000 | 0.0 | — | — | — | — | — | — | — | — | — / 1.45 | — / 1.00 |
| 1001-1100 | 0.0 | — | — | — | — | — | — | — | — | — / 1.45 | — / 1.00 |
| 1101-1200 | 0.0 | — | — | — | — | — | — | — | — | — / 1.47 | — / 1.00 |
| 1201-1300 | 0.0 | — | — | — | — | — | — | — | — | — / 1.46 | — / 1.00 |
| 1301-1400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.47 | — / 1.00 |
| 1401-1500 | 0.0 | — | — | — | — | — | — | — | — | — / 1.47 | — / 1.00 |
| 1501-1600 | 0.0 | — | — | — | — | — | — | — | — | — / 1.46 | — / 1.00 |
| 1601-1700 | 0.0 | — | — | — | — | — | — | — | — | — / 1.46 | — / 1.00 |
| 1701-1800 | 0.0 | — | — | — | — | — | — | — | — | — / 1.46 | — / 1.00 |
| 1801-1900 | 0.0 | — | — | — | — | — | — | — | — | — / 1.47 | — / 1.00 |
| 1901-2000 | 0.0 | — | — | — | — | — | — | — | — | — / 1.46 | — / 1.00 |
| 2001-2100 | 0.0 | — | — | — | — | — | — | — | — | — / 1.45 | — / 1.00 |
| 2101-2200 | 0.0 | — | — | — | — | — | — | — | — | — / 1.47 | — / 1.00 |

### H1nc (n 4)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.20 | — / 1.16 |
| 401-500 | 0.0 | — | — | — | — | — | — | — | — | — / 1.13 | — / 1.13 |
| 501-600 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 601-700 | 0.0 | — | — | — | — | — | — | — | — | — / 1.11 | — / 1.12 |
| 701-800 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 801-900 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 901-1000 | 0.0 | — | — | — | — | — | — | — | — | — / 1.11 | — / 1.12 |
| 1001-1100 | 0.0 | — | — | — | — | — | — | — | — | — / 1.11 | — / 1.12 |
| 1101-1200 | 0.0 | — | — | — | — | — | — | — | — | — / 1.11 | — / 1.12 |
| 1201-1300 | 0.0 | — | — | — | — | — | — | — | — | — / 1.11 | — / 1.12 |
| 1301-1400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 1401-1500 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 1501-1600 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 1601-1700 | 0.0 | — | — | — | — | — | — | — | — | — / 1.13 | — / 1.12 |
| 1701-1800 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |
| 1801-1900 | 0.0 | — | — | — | — | — | — | — | — | — / 1.13 | — / 1.12 |
| 1901-2000 | 0.0 | — | — | — | — | — | — | — | — | — / 1.13 | — / 1.12 |
| 2001-2100 | 0.0 | — | — | — | — | — | — | — | — | — / 1.13 | — / 1.12 |
| 2101-2200 | 0.0 | — | — | — | — | — | — | — | — | — / 1.12 | — / 1.12 |

### H5nc (n 6)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.20 | — / 1.16 |
| 401-500 | 54.3 | -0.08 | -0.00 | +0.00 | -0.02 | -0.00 | +0.01 | -0.00 | -0.01 | 1.20 / 1.16 | 0.15 / 1.10 |
| 501-600 | 83.4 | -0.19 | -0.00 | +0.02 | -0.06 | -0.01 | +0.04 | +0.00 | +0.02 | 1.14 / 1.21 | 0.15 / 1.11 |
| 601-700 | 96.9 | -0.30 | +0.00 | +0.05 | -0.14 | +0.01 | +0.04 | -0.00 | +0.01 | 1.11 / 1.21 | 0.15 / 1.11 |
| 701-800 | 99.3 | -0.40 | -0.01 | +0.06 | -0.24 | +0.00 | +0.07 | -0.01 | -0.01 | 1.08 / 1.19 | 0.14 / 1.11 |
| 801-900 | 103.7 | -0.46 | -0.02 | +0.07 | -0.32 | -0.03 | +0.07 | +0.01 | -0.00 | 1.07 / 1.17 | 0.14 / 1.10 |
| 901-1000 | 105.5 | -0.51 | -0.04 | +0.10 | -0.44 | -0.03 | +0.07 | +0.00 | +0.00 | 1.06 / 1.16 | 0.14 / 1.10 |
| 1001-1100 | 109.9 | -0.51 | -0.06 | +0.13 | -0.50 | -0.03 | +0.08 | -0.01 | -0.04 | 1.06 / 1.16 | 0.14 / 1.10 |
| 1101-1200 | 109.5 | -0.52 | -0.07 | +0.11 | -0.55 | -0.03 | +0.09 | -0.02 | -0.07 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1201-1300 | 112.4 | -0.55 | -0.09 | +0.08 | -0.62 | -0.02 | +0.05 | +0.02 | -0.08 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1301-1400 | 112.8 | -0.54 | -0.11 | +0.11 | -0.65 | -0.03 | +0.02 | +0.04 | -0.06 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1401-1500 | 117.0 | -0.57 | -0.12 | +0.09 | -0.69 | -0.04 | +0.02 | +0.03 | -0.04 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1501-1600 | 112.2 | -0.57 | -0.13 | +0.10 | -0.66 | -0.04 | +0.02 | +0.01 | -0.05 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1601-1700 | 109.0 | -0.57 | -0.13 | +0.07 | -0.62 | -0.04 | +0.01 | +0.00 | -0.01 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1701-1800 | 112.3 | -0.59 | -0.11 | +0.04 | -0.66 | -0.05 | +0.02 | +0.00 | -0.04 | 1.04 / 1.16 | 0.14 / 1.10 |
| 1801-1900 | 112.4 | -0.58 | -0.11 | +0.05 | -0.66 | -0.04 | +0.05 | -0.00 | -0.04 | 1.05 / 1.16 | 0.14 / 1.10 |
| 1901-2000 | 113.4 | -0.58 | -0.10 | +0.06 | -0.67 | -0.02 | +0.04 | -0.01 | -0.01 | 1.04 / 1.16 | 0.14 / 1.10 |
| 2001-2100 | 113.5 | -0.59 | -0.12 | +0.07 | -0.67 | -0.03 | +0.04 | -0.01 | -0.01 | 1.05 / 1.16 | 0.14 / 1.10 |
| 2101-2200 | 114.0 | -0.59 | -0.10 | +0.07 | -0.66 | -0.02 | +0.03 | -0.03 | -0.01 | 1.04 / 1.17 | 0.14 / 1.10 |

### STAGEDnc (n 8)
| years | herded | R | A | S | B | H | T | M | W | fear of wolves h / w | fear of humans h / w |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 301-400 | 0.0 | — | — | — | — | — | — | — | — | — / 1.19 | — / 1.16 |
| 401-500 | 13.6 | -0.03 | +0.00 | -0.00 | +0.00 | +0.00 | +0.00 | -0.00 | +0.01 | 1.73 / 1.14 | 0.16 / 1.11 |
| 501-600 | 13.7 | -0.03 | +0.01 | -0.00 | -0.00 | +0.01 | -0.00 | +0.00 | +0.01 | 1.73 / 1.13 | 0.16 / 1.11 |
| 601-700 | 15.0 | -0.03 | +0.01 | -0.01 | +0.00 | -0.00 | +0.01 | +0.01 | -0.01 | 1.72 / 1.13 | 0.16 / 1.11 |
| 701-800 | 18.6 | -0.04 | +0.00 | +0.01 | -0.01 | +0.00 | +0.00 | -0.00 | +0.01 | 1.64 / 1.14 | 0.16 / 1.10 |
| 801-900 | 17.4 | -0.04 | +0.01 | +0.00 | -0.00 | +0.00 | +0.00 | +0.01 | +0.00 | 1.68 / 1.14 | 0.16 / 1.11 |
| 901-1000 | 16.5 | -0.04 | +0.00 | +0.00 | -0.01 | +0.01 | +0.01 | +0.00 | +0.01 | 1.69 / 1.14 | 0.16 / 1.10 |
| 1001-1100 | 16.7 | -0.03 | +0.01 | -0.00 | -0.00 | -0.00 | +0.01 | +0.00 | +0.00 | 1.77 / 1.14 | 0.16 / 1.11 |
| 1101-1200 | 17.8 | -0.04 | +0.00 | +0.00 | -0.01 | -0.00 | -0.00 | +0.00 | +0.00 | 1.71 / 1.13 | 0.16 / 1.10 |
| 1201-1300 | 17.2 | -0.04 | -0.00 | +0.01 | -0.01 | -0.00 | +0.01 | -0.00 | +0.01 | 1.69 / 1.13 | 0.16 / 1.10 |
| 1301-1400 | 51.7 | -0.06 | +0.00 | +0.01 | -0.02 | -0.01 | +0.02 | +0.00 | -0.01 | 1.20 / 1.16 | 0.15 / 1.10 |
| 1401-1500 | 69.3 | -0.10 | -0.00 | +0.00 | -0.03 | -0.00 | +0.03 | +0.00 | -0.01 | 1.18 / 1.21 | 0.15 / 1.11 |
| 1501-1600 | 82.6 | -0.18 | -0.00 | +0.02 | -0.07 | -0.01 | +0.03 | -0.00 | -0.01 | 1.14 / 1.22 | 0.15 / 1.11 |
| 1601-1700 | 99.2 | -0.31 | +0.00 | +0.04 | -0.17 | -0.02 | +0.06 | -0.02 | -0.01 | 1.11 / 1.21 | 0.15 / 1.11 |
| 1701-1800 | 108.0 | -0.44 | -0.00 | +0.06 | -0.34 | -0.06 | +0.08 | -0.04 | -0.02 | 1.07 / 1.18 | 0.14 / 1.10 |
| 1801-1900 | 109.8 | -0.49 | +0.00 | +0.07 | -0.46 | -0.07 | +0.08 | -0.03 | -0.05 | 1.06 / 1.17 | 0.14 / 1.10 |
| 1901-2000 | 112.0 | -0.52 | +0.01 | +0.07 | -0.53 | -0.06 | +0.05 | -0.01 | -0.05 | 1.05 / 1.16 | 0.14 / 1.10 |
| 2001-2100 | 111.7 | -0.56 | -0.02 | +0.08 | -0.58 | -0.04 | +0.07 | -0.00 | -0.03 | 1.05 / 1.16 | 0.14 / 1.10 |
| 2101-2200 | 112.8 | -0.57 | -0.02 | +0.08 | -0.61 | -0.03 | +0.06 | +0.00 | -0.03 | 1.05 / 1.16 | 0.14 / 1.10 |

Absolute means, years 1901-2200, herd and wild, with the sum over traits, baselines alongside
(`tools/herd_wild_means.py`, now taking folder:COND arguments; its default output is unchanged):
```
H0 goats 509 herd 0 | herd R0.00 A0.00 S0.00 B0.00 H0.00 T0.00 M0.00 W0.00 sum 0.00 | wild R0.65 A0.77 S0.16 B0.91 H0.85 T0.37 M0.17 W0.58 sum 4.45
H0nc goats 535 herd 0 | herd R0.00 A0.00 S0.00 B0.00 H0.00 T0.00 M0.00 W0.00 sum 0.00 | wild R0.62 A0.85 S0.11 B0.89 H0.84 T0.25 M0.23 W0.72 sum 4.51
H1 goats 436 herd 0 | herd R0.00 A0.00 S0.00 B0.00 H0.00 T0.00 M0.00 W0.00 sum 0.00 | wild R0.85 A0.75 S0.11 B0.90 H0.83 T0.42 M0.18 W0.49 sum 4.53
H1nc goats 453 herd 0 | herd R0.00 A0.00 S0.00 B0.00 H0.00 T0.00 M0.00 W0.00 sum 0.00 | wild R0.83 A0.84 S0.11 B0.89 H0.83 T0.28 M0.24 W0.73 sum 4.74
H5 goats 559 herd 122 | herd R0.19 A0.72 S0.25 B0.16 H0.80 T0.39 M0.18 W0.51 sum 3.19 | wild R0.84 A0.75 S0.12 B0.89 H0.83 T0.39 M0.15 W0.53 sum 4.51
H5nc goats 570 herd 114 | herd R0.22 A0.73 S0.18 B0.20 H0.82 T0.32 M0.21 W0.71 sum 3.38 | wild R0.81 A0.84 S0.11 B0.87 H0.84 T0.28 M0.22 W0.72 sum 4.69
STAGED goats 547 herd 120 | herd R0.26 A0.69 S0.19 B0.31 H0.80 T0.48 M0.18 W0.55 sum 3.47 | wild R0.84 A0.76 S0.14 B0.87 H0.83 T0.41 M0.16 W0.57 sum 4.57
STAGEDnc goats 567 herd 112 | herd R0.27 A0.82 S0.20 B0.28 H0.79 T0.35 M0.19 W0.63 sum 3.53 | wild R0.82 A0.83 S0.12 B0.85 H0.84 T0.29 M0.20 W0.66 sum 4.61
```
`tools/loadcal_sum.py results/nocost 1901 2200` and the same on results/staged (all goats):

| cond | n | goats | births/y | births per goat | median 1st kid age (d) | load | R | A | S | B | H | T | M | W |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H0nc | 4 | 535 | 151 | 0.283 | 766 | 4.51 | 0.62 | 0.85 | 0.11 | 0.89 | 0.84 | 0.25 | 0.23 | 0.72 |
| H1nc | 4 | 453 | 121 | 0.266 | 775 | 4.74 | 0.83 | 0.84 | 0.11 | 0.89 | 0.83 | 0.28 | 0.24 | 0.73 |
| H5nc | 6 | 570 | 163 | 0.284 | 740 | 4.43 | 0.69 | 0.81 | 0.13 | 0.73 | 0.84 | 0.29 | 0.22 | 0.71 |
| STAGEDnc | 8 | 567 | 164 | 0.288 | 740 | 4.39 | 0.71 | 0.82 | 0.14 | 0.74 | 0.83 | 0.30 | 0.20 | 0.65 |
| H0 | 4 | 509 | 133 | 0.260 | 1053 | 4.45 | 0.65 | 0.77 | 0.16 | 0.91 | 0.85 | 0.37 | 0.17 | 0.58 |
| H1 | 4 | 436 | 106 | 0.242 | 1042 | 4.53 | 0.85 | 0.75 | 0.11 | 0.90 | 0.83 | 0.42 | 0.18 | 0.49 |
| H5 | 6 | 559 | 148 | 0.264 | 997 | 4.23 | 0.70 | 0.75 | 0.15 | 0.73 | 0.83 | 0.39 | 0.15 | 0.53 |
| STAGED | 12 | 547 | 149 | 0.272 | 810 | 4.33 | 0.71 | 0.75 | 0.15 | 0.75 | 0.83 | 0.42 | 0.16 | 0.56 |

Figure: results/nocost/fig/nocost_genes.png (`tools/gene_heatmap.py results/nocost ... H0nc:all H1nc:all
H5nc:herd H5nc:wild STAGEDnc:herd STAGEDnc:wild`).


## [PRE-REGISTERED 2026-11-03] Cull selection profiles: random, meat, flight, return, attack
**Question:** Chris (2026-11-03): the herders' selection is the experimental knob, as planting was in the grain
work. Build phenotype-based cull profiles, one at a time, with random as the control: a goat's standing changes
if it runs away, if it comes back on its own, if it attacks a person. Also his reading of the meat profile: the
herder keeps a grown goat smaller than the herd's adults for meat still to come that never comes, which may
push body size down ("we expect them to grow larger, so we keep, they don't, oops, evolution").
**Settings:** main, code after 0c78b72 plus this change: each goat carries `seen` = [ran off, came back on its
own, butted the herder] since the herder began watching it (capture or birth in the herd). New cull rules
'flight', 'return', 'attack': the random rule's order, re-sorted by seen count per (years watched + 1); flight
and attack cull the highest rate first, return the lowest; ties at random. A butt is new and seen only (no
injury, no other effect): once a day each herd goat butts the herder with chance buttRate (0.002) × A, drawn
only under 'attack'. Check: H5 and H5 with cullRule random, seed 1, 520 years, before vs after the change
(results/profcheck), must be identical: done, 0 of 520 years differ in either (934 and 507 herd goats culled
in them, so the cull path ran). tools/profiles.json: H5 husbandry with genome costs off (the default
since 0c78b72), cull rule the only difference: Prand (random), Pmeat (opportunity), Pflight, Preturn, Pattack.
Smoke test (40 y, herding from year 10, seed 1): most herd goats are seen to run off within 2-3 years; about a
quarter of run-offs come back on their own; about 0.2 butts per goat-year.
**Method:** `node tools/batch.mjs tools/profiles.json results/profiles 1200 4 20`; tools/stage_table.py,
tools/herd_wild_means.py (years 901-1200 window via a from= option if added, else the table), gene_heatmap.py.
**Prediction** (herd − wild gaps, years 1101-1200, against Prand):
- Pflight: R gap at least 0.10 wider (more negative) than Prand; herd at least as large as Prand's.
- Preturn: S gap at least 0.05 above Prand's; R gap narrower than Prand's (a goat must run off to come back).
- Pattack: A gap -0.10 or wider; Prand's A gap within ±0.05.
- Pmeat vs Prand (Chris's body-size question): B gap under Prand within 0.15 of Pmeat's, i.e. the meat
  profile's growth credit is not the main cause of the herd's smaller bodies. (The staged ladder showed no B gap
  in its H3 and H4 stages, which used the meat profile.)


## [RESULTS 2026-11-03] Cull selection profiles (raw)
Ran as pre-registered: 20 runs of 1200 years, conc 20, 0 FAIL, about 5,700-6,100 s each. results/profiles.
`tools/stage_table.py results/profiles`, herd − wild gaps, years 1101-1200, means over 4 seeds:

| cond | herded | R | A | S | B | H | T | M | W |
|---|---|---|---|---|---|---|---|---|---|
| Prand | 80.4 | -0.36 | -0.02 | +0.07 | -0.02 | -0.02 | +0.06 | -0.01 | -0.05 |
| Pmeat | 108.6 | -0.52 | -0.07 | +0.11 | -0.53 | -0.03 | +0.10 | -0.06 | -0.04 |
| Pflight | 93.4 | -0.68 | -0.02 | +0.12 | -0.05 | -0.02 | +0.10 | +0.03 | +0.10 |
| Preturn | 72.1 | -0.28 | -0.02 | +0.04 | -0.01 | -0.03 | +0.03 | +0.03 | -0.03 |
| Pattack | 81.0 | -0.39 | -0.20 | +0.09 | -0.02 | -0.00 | +0.10 | +0.02 | -0.02 |

Herd fear of humans 0.14-0.15 and wild 1.10 in every condition; herd fear of wolves 1.03 (Pflight) to 1.14
(Preturn), wild 1.15-1.18.

Per seed, years 1101-1200 (`tools/perseed_gaps.py results/profiles`; gaps herd − wild; B absolute herd / wild):
```
Prand   s1 herd  46 R-0.10 A-0.01 S+0.00 B-0.01 (0.89/0.90) | s2  97 R-0.54 A-0.00 S+0.11 B+0.01 (0.89/0.88)
        s3 herd  75 R-0.23 A+0.02 S+0.01 B-0.04 (0.82/0.86) | s4 103 R-0.58 A-0.06 S+0.14 B-0.03 (0.86/0.89)
Pmeat   s1 herd 108 R-0.61 A-0.13 S+0.13 B-0.65 (0.23/0.89) | s2 102 R-0.50 A-0.01 S+0.14 B-0.43 (0.43/0.86)
        s3 herd 114 R-0.41 A-0.08 S+0.03 B-0.51 (0.31/0.82) | s4 111 R-0.57 A-0.07 S+0.16 B-0.56 (0.32/0.87)
Pflight s1 herd  80 R-0.66 A+0.01 S+0.15 B-0.14 (0.72/0.86) | s2  98 R-0.77 A-0.07 S+0.07 B-0.00 (0.89/0.90)
        s3 herd  97 R-0.70 A-0.03 S+0.19 B-0.04 (0.85/0.89) | s4  99 R-0.59 A+0.03 S+0.08 B+0.00 (0.89/0.89)
Preturn s1 herd  40 R-0.07 A-0.03 S+0.01 B-0.00 (0.86/0.86) | s2  79 R-0.28 A-0.05 S+0.04 B-0.00 (0.86/0.86)
        s3 herd  75 R-0.38 A+0.00 S+0.02 B-0.02 (0.86/0.88) | s4  94 R-0.40 A-0.01 S+0.07 B-0.02 (0.86/0.89)
Pattack s1 herd  94 R-0.62 A-0.18 S+0.15 B-0.02 (0.85/0.87) | s2  48 R-0.09 A-0.02 S+0.01 B-0.00 (0.88/0.89)
        s3 herd  86 R-0.37 A-0.17 S+0.08 B-0.02 (0.86/0.87) | s4  96 R-0.50 A-0.43 S+0.14 B-0.03 (0.86/0.89)
```
Herd sizes by window (stage_table): Prand 38 (401-500) to 80; Pmeat 55 to 109; Pflight 35 to 93; Preturn 37 to
72; Pattack 35 to 81. Pmeat's B gap opens from 501-600 (-0.06) and reaches -0.44 by 901-1000.

Against the predictions:
- Pflight R gap 0.32 wider than Prand's: met. Herd 93 vs 80: met.
- Preturn S gap +0.04 vs Prand +0.07: not met. R gap -0.28 vs -0.36, narrower: met.
- Pattack A gap -0.20: met (seeds -0.18, -0.02, -0.17, -0.43). Prand A gap -0.02: met.
- Pmeat vs Prand B: -0.53 vs -0.02, 0.51 apart: not met.

Figure: results/profiles/fig/profiles_genes.png (`tools/gene_heatmap.py results/profiles ... Prand:herd
Pmeat:herd Pflight:herd Preturn:herd Pattack:herd from=300`).


## [PRE-REGISTERED 2026-11-03] Sire selection profiles: oldest, random, calm, gentle, large
**Question:** Chris (2026-11-03): the cull profiles showed a route from culling to selection; does deliberate
intervention in reproduction matter? Until now the herder's sires (buck management) were the two oldest adult
herd bucks, a rule blind to traits; does were not chosen at all. Add phenotype-based sire choice, random as the
control. Does are left for a separate step (the chosen sires already father nearly all herd kids, so the next
lever is which does are bred, a different change).
**Settings:** main, code after 7323f7d plus this change: sireRule picks keepSires (2) adult herd bucks: 'oldest'
(the old rule, default), 'random' (a fixed random preference per buck, drawn when first ranked), 'calm' (fewest
seen run-offs per year watched, the flight profile's rate), 'gentle' (fewest seen butts, butts drawn as in the
attack profile), 'large' (biggest size now); ties at the random preference. keepChosenSires 1: the random cull
never takes a chosen sire. New output chosenSiredShare: herd conceptions by a chosen sire. Check: H5 and H5 with
cullRule random, seed 1, 520 years, against results/profcheck (results/sirecheck): 0 of 520 years differ in
either, chosenSiredShare aside (934 and 507 herd goats culled, as before). Probe (40 y, herding from year 10):
each rule picks the expected bucks (in a 7-buck herd: calm picks run-off rates 0.17 and 0.35 a year against a
mean 1.25; gentle picks two with no butts; large the two biggest); in a 2-buck herd there is nothing to choose.
Smoke (100 y, herding from year 10, seed 1, years 51-100): chosen sires sire 99.7-100% of herd conceptions in all
five rules; wild-sired herd births 1-3%. tools/sires.json: H5 husbandry, costs off, cullRule random,
keepChosenSires 1; Soldest, Srandom, Scalm, Sgentle, Slarge.
**Method:** `node tools/batch.mjs tools/sires.json results/sires 1200 4 20`; tools/stage_table.py,
tools/perseed_gaps.py (condition list extended), gene_heatmap.py; chosenSiredShare and siresPerCamp by window.
**Prediction** (herd − wild gaps, years 1101-1200, against Srandom):
- Scalm: R gap at least 0.10 wider (more negative) than Srandom's.
- Sgentle: A gap -0.10 or wider; Srandom's A gap within ±0.05.
- Slarge: B gap at least 0.03 above Srandom's (headroom is small: wild B is about 0.87 of the range).
- No syndrome: in each of Scalm, Sgentle, Slarge, every trait other than the targeted one within 0.10 of
  Srandom's gap, except R (which moves with herd size across seeds in the cull profiles).
- Sire choice against cull choice on the same signal: Scalm's R gap wider than Pflight's (-0.68), Sgentle's A
  gap wider than Pattack's (-0.20).
- Soldest against Prand (same sire rule; sires now spared from the cull): every gap within 0.10.


## [RESULTS 2026-11-04] Sire selection profiles (raw)
Ran as pre-registered: 20 runs of 1200 years, conc 20, 0 FAIL, about 2,400 s each. results/sires.
`tools/stage_table.py results/sires`, herd − wild gaps, years 1101-1200, means over 4 seeds:

| cond | herded | R | A | S | B | H | T | M | W |
|---|---|---|---|---|---|---|---|---|---|
| Srandom | 52.3 | -0.15 | -0.02 | +0.03 | -0.02 | -0.00 | +0.03 | +0.01 | -0.00 |
| Soldest | 48.7 | -0.11 | -0.00 | +0.01 | +0.00 | +0.00 | +0.03 | -0.01 | +0.00 |
| Scalm | 73.2 | -0.38 | -0.02 | +0.04 | -0.03 | -0.03 | +0.07 | +0.02 | -0.01 |
| Sgentle | 46.4 | -0.08 | -0.01 | +0.01 | -0.00 | +0.00 | +0.02 | +0.01 | +0.00 |
| Slarge | 73.0 | -0.29 | -0.03 | +0.04 | +0.05 | -0.04 | +0.03 | +0.01 | -0.02 |

Herd fear of humans 0.14-0.15, wild 1.10-1.11, in every condition.

Per seed (`tools/perseed_gaps.py results/sires Soldest Srandom Scalm Sgentle Slarge`; B absolute herd / wild):
```
Soldest s1 herd 42 R-0.06 A-0.01 B+0.00 (0.89/0.89) | s2 44 R-0.08 A-0.01 B+0.01 (0.86/0.85) | s3 46 R-0.07 A+0.01 B-0.00 (0.88/0.88) | s4 63 R-0.21 A-0.01 B-0.00 (0.88/0.89)
Srandom s1 herd 49 R-0.12 A-0.01 B-0.02 (0.81/0.84) | s2 44 R-0.07 A-0.01 B-0.00 (0.89/0.89) | s3 47 R-0.05 A-0.01 B-0.01 (0.89/0.89) | s4 70 R-0.35 A-0.06 B-0.05 (0.81/0.86)
Scalm   s1 herd 59 R-0.19 A-0.01 B+0.01 (0.90/0.90) | s2 49 R-0.08 A-0.01 B-0.00 (0.89/0.89) | s3 92 R-0.60 A-0.05 B-0.02 (0.88/0.90) | s4 93 R-0.64 A-0.02 B-0.11 (0.77/0.88)
Sgentle s1 herd 39 R-0.05 A+0.01 B-0.00 (0.90/0.90) | s2 55 R-0.11 A-0.03 B-0.01 (0.89/0.89) | s3 46 R-0.07 A-0.00 B+0.01 (0.87/0.87) | s4 46 R-0.09 A-0.01 B-0.01 (0.88/0.89)
Slarge  s1 herd 94 R-0.49 A-0.01 B+0.06 (0.98/0.92) | s2 47 R-0.12 A+0.01 B+0.03 (0.95/0.92) | s3 64 R-0.12 A-0.04 B+0.03 (0.97/0.94) | s4 87 R-0.44 A-0.07 B+0.06 (0.97/0.91)
```
Herd demography, means over seeds (years 401-500 / 1001-1200): herded Prand (results/profiles) 38 / 79, Soldest 32 /
46, Srandom 33 / 53, Scalm 32 / 72, Sgentle 35 / 47, Slarge 33 / 70. chosenSiredShare 0.98-0.99 (401-500) and
0.998-0.999 (1001-1200) in all five; siresPerCamp (distinct fathers of herd births per camp-year) 1.15-1.37;
wild-sired herd births 1.7-4.8%.
Probe (`tools/buckcount.mjs`; H5 husbandry, random cull, sireRule gentle, herding from year 10, years 60-200,
seeds 1 and 2): adult herd bucks per camp at rut peak, keepChosenSires 1: 6+ in 44% and 93% of camp-years (mean
herd 14 and 30); keepChosenSires 0: 66% and 96% (mean herd 19 and 30).
Herd size against R gap, years 1101-1200, all 40 runs of results/profiles and results/sires: r = -0.91; the 28 runs
whose rule does not use R or its signals (Prand, Preturn, Pattack, Soldest, Srandom, Sgentle, Slarge): r = -0.96.
In those 28, herds of 39-55 have R gaps -0.05 to -0.12, herds of 62-103 have -0.12 to -0.62.
Slarge herd B reaches the top of the trait range by about year 600 (figure); wild B 0.91-0.94 against 0.84-0.90
in the other conditions.

Against the predictions:
- Scalm R gap -0.38 vs Srandom -0.15, 0.23 wider: met as stated (but see herd size above).
- Sgentle A gap -0.01: not met. Srandom A gap -0.02: met.
- Slarge B gap +0.05 vs Srandom -0.02, 0.07 above: met.
- No syndrome: every non-target trait other than R within 0.10 of Srandom in Scalm, Sgentle, Slarge: met.
- Scalm R gap wider than Pflight's -0.68: not met. Sgentle A gap wider than Pattack's -0.20: not met.
- Soldest vs Prand every gap within 0.10: not met (R -0.11 vs -0.36; others within 0.06).

Figure: results/sires/fig/sires_genes.png (`tools/gene_heatmap.py results/sires ... Srandom:herd Soldest:herd
Scalm:herd Sgentle:herd Slarge:herd from=300`).


## [PRE-REGISTERED 2026-11-04] Long runs: does herd size stop predicting the R gap?
**Question:** Chris (2026-11-04): across the profile and sire batches herd size and the herd − wild R gap
correlate (r -0.96 over the 28 runs whose rule does not use R). Is that speed to convergence: do small herds
diverge on the same path, only later, so that with longer runs the correlation falls off? Seen already in those
runs (per seed, windows 501-600 ... 1101-1200): most herds sit at 40-50 goats with R gap about -0.07 for
centuries, then at different times herd size and R gap grow together over a century or two (e.g. Pattack s3
near 900, Preturn s2 near 1100, Slarge s4 near 900); a few fall back somewhat (Srandom s4 93 to 70).
**Settings:** main at 478102e. tools/longrun.json: Prand (as in tools/profiles.json) and Srandom (as in
tools/sires.json), seeds 1-8 (1-4 repeat the existing runs exactly through year 1200), 2400 years.
**Method:** `node tools/batch.mjs tools/longrun.json results/longrun 2400 8 16`; per run and window (1101-1200,
1701-1800, 2301-2400): herd size and R gap; r(herd, R gap) over the 16 runs per window; share of runs "taken
off" (herd over 60 and R gap wider than -0.15).
**Prediction** (two readings, stated before the runs):
- Chris's (later, not different): by 2301-2400 at least 12 of 16 runs have taken off, and |r| at 2301-2400 is at
  least 0.2 below |r| at 1101-1200.
- Mine (two regimes, a waiting time to take off): some herds stay small with small gaps; r at 2301-2400 is -0.8
  or stronger.
Either can hold partly; the counts decide.


## [RESULTS 2026-11-04] Long runs (raw)
Ran as pre-registered: 16 runs of 2400 years, conc 16, 0 FAIL, up to about 5,250 s. results/longrun. Seeds 1-4
match the earlier 1200-year runs (herd and R gap at 1101-1200 identical to results/profiles and results/sires).
Herd size / R gap (herd − wild), per run and window:
```
run            501-600     801-900     1101-1200   1401-1500   1701-1800   2001-2100   2301-2400
Prand_seed1    48.8/-0.12  43.0/-0.06  46.1/-0.10  64.8/-0.16  81.7/-0.42  94.5/-0.47  90.0/-0.39
Prand_seed2    40.7/-0.09  86.2/-0.36  97.0/-0.54  99.1/-0.56  92.3/-0.55  94.9/-0.58  95.5/-0.59
Prand_seed3    47.6/-0.08  52.8/-0.10  75.3/-0.23  96.0/-0.61  83.4/-0.53  85.8/-0.46  97.4/-0.54
Prand_seed4    64.3/-0.14  91.7/-0.46 103.2/-0.58  97.3/-0.52 104.6/-0.64 101.1/-0.61  96.0/-0.52
Prand_seed5    46.8/-0.07  68.5/-0.27  90.5/-0.43  83.0/-0.49  92.8/-0.50  88.6/-0.55  91.2/-0.61
Prand_seed6    60.3/-0.29  98.6/-0.57  95.2/-0.46  98.5/-0.61  95.1/-0.49 101.7/-0.60 101.1/-0.64
Prand_seed7    41.1/-0.07  39.9/-0.03  49.6/-0.12  97.8/-0.43  83.6/-0.42  94.2/-0.54  98.9/-0.61
Prand_seed8    49.9/-0.11  74.1/-0.40  98.9/-0.59  96.5/-0.63 103.0/-0.62  97.9/-0.59 103.2/-0.66
Srandom_seed1  38.5/-0.08  41.2/-0.08  48.9/-0.12  59.1/-0.20  39.5/-0.04  39.0/-0.04  36.0/-0.04
Srandom_seed2  39.9/-0.05  43.9/-0.06  44.1/-0.07  37.3/-0.03  46.6/-0.15  44.2/-0.04  48.1/-0.09
Srandom_seed3  46.1/-0.09  43.2/-0.06  46.5/-0.05  46.5/-0.08  66.9/-0.24  55.8/-0.14  95.1/-0.45
Srandom_seed4  31.9/-0.05  75.4/-0.32  69.7/-0.35  66.5/-0.45  84.0/-0.44  82.4/-0.39  73.7/-0.29
Srandom_seed5  37.5/-0.06  41.9/-0.11  35.9/-0.06  35.6/-0.03  42.3/-0.06  39.6/-0.05  32.0/-0.05
Srandom_seed6  36.8/-0.05  41.2/-0.06  36.7/-0.04  44.7/-0.08  45.6/-0.09  34.7/-0.05  35.6/-0.04
Srandom_seed7  42.9/-0.08  44.4/-0.08  89.2/-0.39  69.7/-0.29  78.6/-0.28  45.9/-0.10  41.0/-0.05
Srandom_seed8  41.1/-0.06  38.2/-0.06  38.0/-0.04  41.9/-0.04  34.0/-0.05  42.7/-0.04  39.0/-0.07
```
Over the 16 runs per window: r(herd, R gap) -0.78, -0.98, -0.98, -0.95, -0.98, -0.99, -0.97; taken off (herd
over 60, R gap wider than -0.15) 1, 6, 8, 10, 11, 9, 10. Prand: 8 of 8 taken off by 1701-1800 and still so at
2301-2400. Srandom: 2 of 8 taken off at 2301-2400; 5 never over 60 in any of these windows; seed 7 took off
(89/-0.39 at 1101-1200) and came back (41/-0.05 at 2301-2400), seed 4 partly back (84/-0.44 to 74/-0.29).
Flows by herd size, 100-year windows 501-2400 of all 16 runs (run-centuries; per year; share of herd):
herd under 50 (129): herd 41, captured 6.8 (16.6%), run-offs lost 10.1 (24.6%), herd births 13.4 (32%),
wild-sired 2.7%; 50-70 (35): 60, 8.2 (13.7%), 13.4 (22.5%), 20.5 (34%), 2.0%; over 70 (140): 93, 7.3 (7.9%),
10.6 (11.4%), 31.6 (34%), 1.0%.
Against the predictions: Chris's reading (12 of 16 taken off, |r| down 0.2): not met (10; r -0.98 to -0.97).
Mine (some stay small, r -0.8 or stronger): met.
Figure: results/longrun/fig/herd_rgap.png (`tools/herd_rgap_traj.py results/longrun ...`, 50-year means).


## [PRE-REGISTERED 2026-11-04] Sire selection profiles, second form: sires culled as normal
**Question:** Chris (2026-11-04): sparing the chosen sires (keepChosenSires, results/sires) was a mistaken
setting. An opportunistic herder eats a sire too; protect only the last sires. Random sires: cull as normal and
breed from whichever bucks are available. Selective sires: any sire can be replaced by a younger buck, all the
more if it is better on the trait. Rerun the sire profiles that way, and long enough to see the herd states
(results/longrun: herds sit small with no R gap or large with a gap near -0.6, and can switch).
**Settings:** main at 2fc3055 plus keepLastSires: under the random cull, adult herd bucks are not culled while the
herd has keepSires (2) or fewer; otherwise sires are culled at random like any goat. keepChosenSires stays in the
code (default 0) for the earlier batches. The sire rules are unchanged: they re-rank every day among the adult
herd bucks, so a culled sire is replaced at once and a younger buck that ranks higher displaces an older one;
'random' keeps a fixed random preference per buck (trait-blind). tools/sires2.json: H5 husbandry, costs off,
cullRule random, keepLastSires 1; S2oldest, S2random, S2calm, S2gentle, S2large. Checks: H5 and H5 with cullRule random, seed 1, 520 years,
against results/profcheck (results/lastcheck): 0 of 520 years differ in either (934 and 507 culled). Probe
(scratchpad lastprobe.mjs, S2random settings, herding from year 10, 100 y): of 546 cull orderings, 18 found the
herd down to keepSires or fewer adult bucks; in 17 of those no such buck was at the cull end; 2 had no adult
buck. Smoke (100 y, herding from year 10, seed 1, years 51-100): chosen sires sire 99.8-100% of herd
conceptions; herded 55 (oldest), 54 (random), 86 (calm), 85 (gentle), 64 (large).
**Method:** `node tools/batch.mjs tools/sires2.json results/sires2 2400 8 20`; per run and window herd size,
herd − wild gaps (R, A, B), taken off (herd over 60, R gap wider than -0.15); stage_table, gene_heatmap,
herd_rgap_traj.
**Prediction** (years 2301-2400 unless stated; 8 seeds):
- With sires culled as normal, herds take off as under Prand: S2random and S2oldest each at least 6 of 8 taken
  off (Prand 8 of 8 in results/longrun; Srandom 2 of 8).
- S2large B gap at least 0.03 above S2random's.
- S2gentle A gap within ±0.05 of S2random's (sire choice on butts did nothing in results/sires).
- S2calm: among runs taken off, mean R gap at least 0.05 wider than S2random's taken-off runs.
- S2calm takes off sooner: more runs taken off than S2random at 1101-1200.


## [RESULTS 2026-11-04] Sire selection profiles, second form: sires culled as normal (raw)
**Run:** started at conc 20 at 05:10Z; stopped by PID at 06:24Z on Chris's instruction (exploratory batches stay at 10
workers; more only for a paper batch). No run had finished; the 7 FAIL lines in results/sires2/batch.log are the
killed jobs. Restarted `node tools/batch.mjs tools/sires2.json results/sires2 2400 8 10` at 06:24Z; 40 of 40 done
at 10:08Z, no FAIL. Tables: scratchpad sires2_tab.py; results/sires2/fig/stage_table.txt (400-y windows);
fig/herd_rgap.png (herd_rgap_traj.py); fig/heatmap_herd.png (gene_heatmap.py, herd, rows R A S B).

Means over 8 seeds (herd − wild genetic gaps); taken off = herd over 60 and R gap wider than -0.15; offR = mean R gap
of taken-off runs.

| cond | years | herd | R | A | S | B | off | offR |
|---|---|---|---|---|---|---|---|---|
| S2oldest | 1101-1200 | 67.6 | -0.252 | -0.020 | +0.013 | -0.010 | 5/8 | -0.353 |
| S2oldest | 2301-2400 | 90.4 | -0.489 | -0.045 | +0.045 | -0.034 | 7/8 | -0.551 |
| S2random | 1101-1200 | 57.9 | -0.187 | -0.000 | +0.023 | -0.006 | 2/8 | -0.449 |
| S2random | 2301-2400 | 66.7 | -0.217 | -0.011 | +0.014 | -0.012 | 5/8 | -0.298 |
| S2calm | 1101-1200 | 96.2 | -0.576 | -0.026 | +0.032 | -0.026 | 8/8 | -0.576 |
| S2calm | 2301-2400 | 96.7 | -0.660 | -0.033 | +0.050 | -0.044 | 8/8 | -0.660 |
| S2gentle | 1101-1200 | 60.4 | -0.200 | -0.022 | +0.008 | -0.011 | 3/8 | -0.387 |
| S2gentle | 2301-2400 | 59.0 | -0.194 | -0.013 | +0.006 | -0.005 | 3/8 | -0.288 |
| S2large | 1101-1200 | 85.8 | -0.412 | -0.047 | +0.049 | +0.060 | 7/8 | -0.447 |
| S2large | 2301-2400 | 91.8 | -0.500 | -0.102 | +0.083 | +0.072 | 8/8 | -0.500 |

Taken off by window (401-500, 701-800, 1101-1200, 1501-1600, 1901-2000, 2301-2400): S2oldest 0 1 5 6 8 7;
S2random 0 2 2 3 3 5; S2calm 0 4 8 8 8 8; S2gentle 0 1 3 3 2 3; S2large 0 1 7 8 8 8.

Per seed, 2301-2400, herd / R gap:
- S2oldest: 44/-0.06, 87/-0.50, 95/-0.51, 106/-0.61, 99/-0.46, 97/-0.59, 93/-0.60, 102/-0.59
- S2random: 48/-0.07, 64/-0.22, 54/-0.08, 103/-0.46, 43/-0.10, 65/-0.22, 92/-0.36, 64/-0.23
- S2calm: 97/-0.66, 95/-0.68, 104/-0.62, 79/-0.52, 98/-0.71, 102/-0.68, 101/-0.70, 97/-0.71
- S2gentle: 45/-0.07, 55/-0.19, 75/-0.25, 48/-0.10, 48/-0.07, 77/-0.38, 58/-0.25, 67/-0.24
- S2large: 97/-0.57, 88/-0.36, 96/-0.50, 98/-0.57, 75/-0.50, 92/-0.57, 97/-0.42, 92/-0.50

r(herd, R gap) across all 40 runs by window: -0.50, -0.94, -0.97, -0.95, -0.92 for 401-500, 701-800, 1101-1200,
1901-2000, 2301-2400; -0.97 for 1501-1600. S2large herd B sits in the top bucket from about year 1000 (heatmap).

**Against the predictions:**
- S2random and S2oldest each at least 6 of 8 taken off at 2301-2400: not met. S2oldest 7 of 8; S2random 5 of 8.
- S2large B gap at least 0.03 above S2random's: met (+0.072 vs -0.012).
- S2gentle A gap within ±0.05 of S2random's: met (-0.013 vs -0.011).
- S2calm taken-off R gap at least 0.05 wider than S2random's taken-off: met (-0.660, 8 runs, vs -0.298, 5 runs).
- S2calm more taken off than S2random at 1101-1200: met (8 vs 2).


## [PRE-REGISTERED 2026-11-04] H5 ablation: what each husbandry component contributes
**Question:** Chris (2026-11-04): break H5 into its parts and see how each contributes to the result. H5 = H4
(opportunity cull, penning, offtake 10%/y, herderChase default) + guarding, provision (2160), kidShelter,
buckManagement, tetherNew. H2-H4 herds stay at 10-16 goats, refounded from captures, with no genetic gap (G12, mechanism
not found); H5 herds reach about 117 with R gap about -0.6 and B gap about -0.7 (results/h5long, results/staged; genome
costs on there). Which components are needed for the herd to persist and grow, and which for the gaps? Herd goats
die at about the same rate per goat-year in H4 and H5 (results/gentrace, last 100 y: 0.35 vs 0.33), so the difference
is expected in births and kid survival, not adult deaths.
**Settings:** main at a4b7922 (no model change). tools/ablate.json: AH4, AH5 (as tools/conditions.json H4 and H5,
genome costs off by default); Lguard, Lprov, Lshelter, Lbuck, Ltether = AH5 less one component; Pguard, Pprov, Pshelter,
Pbuck, Ptether = AH4 plus one component. Check: AH5 from tools/ablate.json, seed 1, 520 years, against
results/profcheck/new_H5.json: 0 of 520 years differ (chosenSiredShare aside). Smoke (seed 1, humans from year 5, herding from year 10, 150 y; a first attempt without humansAt never herded and showed 0 differences, so the check could fail): each L condition differs from AH5, and each P from AH4, in 137-140 of 150 years. Herded, years 101-150: AH4 11, AH5 121; Lguard 86, Lprov 24, Lshelter 119, Lbuck 97, Ltether 106; Pguard 25, Pprov 87, Pshelter 25, Pbuck 22, Ptether 21. The predictions below were written before this smoke and are left as written; the smoke (one seed) already points to provision, not kidShelter or buckManagement, as the largest component.
**Method:** `node tools/batch.mjs tools/ablate.json results/ablate 1600 8 10` (96 runs, 10 workers); per condition and
100-y window: herded, herd − wild gaps (stage_table.py), taken off (herd over 80 and R gap wider than -0.15; the over-60
cut reported alongside), herd births, captures, herd deaths by cause (herd_deaths.py), per-seed table at 1501-1600;
gene_heatmap.py, herd_rgap_traj.py.
**Prediction** (years 1501-1600, 8 seeds):
- AH4: herd under 25 (three camps), R gap no wider than -0.06. AH5: herd over 90, R gap -0.5 or wider, B gap -0.4 or
  wider.
- Leave one out: removing kidShelter or buckManagement costs the most herd (each at least 30% below AH5); removing
  guarding the least (within 15% of AH5; herderChase already answers wolves).
- Add one: no single component takes H4's herd over 60.
- Wherever herds pass 80 the R gap is -0.4 or wider and the B gap -0.3 or wider (the meat cull runs in every condition);
  wherever herds stay under 40, both gaps stay within -0.1.


## [RESULTS 2026-11-04] H5 ablation (raw)
**Run:** `node tools/batch.mjs tools/ablate.json results/ablate 1600 8 10`, 16:35Z to 22:46Z; 96 of 96 done, no FAIL.
Tables: scratchpad ablate_tab.py, saved as results/ablate/tab.txt; results/ablate/fig/stage_table.txt;
fig/herd_deaths.txt (last 100 y). Figures: fig/loo_R.png, fig/loo_B.png (AH5, Lguard, Lprov, Lbuck, AH4),
fig/add_R.png, fig/add_B.png (AH5, Pprov, Pguard, Pbuck, AH4), from tools/herd_rgap_traj.py with new options conds= and
trait=; fig/heatmap_herd.png (gene_heatmap.py; AH4, AH5, Lprov, Lbuck, Pprov herds; rows R A S B H).

Means over 8 seeds, years 1501-1600 (herd − wild genetic gaps); off80 = herd over 80 and R gap wider than -0.15, off60
the same at 60; per year: herd births, captures, herd deaths (all causes), herd goats culled.

| cond | herd | R | A | S | B | off80 | off60 | births | capt | deaths | culled |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AH4 | 16.6 | -0.037 | +0.001 | +0.004 | -0.006 | 0/8 | 0/8 | 5.8 | 4.3 | 6.4 | 1.7 |
| AH5 | 112.4 | -0.572 | -0.116 | +0.096 | -0.660 | 8/8 | 8/8 | 40.4 | 7.1 | 36.2 | 11.8 |
| Lguard | 100.9 | -0.510 | -0.032 | +0.029 | -0.546 | 7/8 | 8/8 | 39.4 | 7.7 | 33.7 | 11.0 |
| Lprov | 24.2 | -0.050 | -0.002 | +0.002 | -0.009 | 0/8 | 0/8 | 7.6 | 4.7 | 8.0 | 2.6 |
| Lshelter | 114.7 | -0.590 | -0.069 | +0.085 | -0.661 | 8/8 | 8/8 | 40.8 | 6.9 | 36.3 | 12.2 |
| Lbuck | 90.8 | -0.416 | -0.007 | +0.023 | -0.007 | 8/8 | 8/8 | 47.8 | 9.4 | 39.3 | 10.1 |
| Ltether | 110.7 | -0.597 | -0.061 | +0.073 | -0.624 | 8/8 | 8/8 | 40.9 | 6.6 | 36.6 | 11.8 |
| Pguard | 22.4 | -0.044 | -0.003 | +0.003 | -0.009 | 0/8 | 0/8 | 7.7 | 4.8 | 7.5 | 2.3 |
| Pprov | 85.9 | -0.428 | -0.014 | +0.030 | -0.028 | 8/8 | 8/8 | 47.8 | 9.1 | 39.2 | 9.7 |
| Pshelter | 16.4 | -0.036 | -0.001 | +0.007 | -0.002 | 0/8 | 0/8 | 5.5 | 4.4 | 6.3 | 1.8 |
| Pbuck | 17.2 | -0.035 | -0.002 | +0.003 | -0.003 | 0/8 | 0/8 | 5.6 | 4.5 | 6.3 | 1.9 |
| Ptether | 19.0 | -0.035 | +0.001 | +0.008 | -0.003 | 0/8 | 0/8 | 6.3 | 4.5 | 7.5 | 2.0 |

Herd size by window (401-500, 701-800, 1101-1200, 1501-1600): AH5 53.5 100.1 108.9 112.4; Lguard 41.4 78.9 95.8 100.9;
Lbuck 46.0 79.3 92.4 90.8; Pprov 29.5 52.7 75.2 85.9; Ltether 45.7 105.6 111.7 110.7; Lshelter 53.2 103.3 114.8 114.7.
off80 by the same windows: AH5 0 8 8 8; Lguard 0 5 7 7; Lbuck 0 5 8 8; Pprov 0 2 5 8; Lshelter 0 8 8 8; Ltether 0 8 8 8;
all others 0 in every window. B gap at 1101-1200: AH5 -0.564, Lguard -0.366, Lshelter -0.586, Ltether -0.614,
Lbuck -0.027, Pprov -0.008.

Per seed, 1501-1600, herd / R gap / B gap:
- AH5: 112/-0.55/-0.74, 109/-0.61/-0.55, 116/-0.55/-0.67, 108/-0.62/-0.61, 115/-0.55/-0.72, 113/-0.51/-0.67, 113/-0.62/-0.68, 113/-0.56/-0.64
- Lguard: 113/-0.53/-0.56, 93/-0.52/-0.65, 98/-0.43/-0.43, 111/-0.59/-0.58, 77/-0.45/-0.41, 96/-0.51/-0.41, 117/-0.52/-0.66, 104/-0.54/-0.67
- Lbuck: 91/-0.42/-0.00, 93/-0.40/-0.01, 89/-0.40/-0.03, 88/-0.40/-0.01, 89/-0.36/-0.01, 94/-0.44/+0.01, 89/-0.45/+0.00, 92/-0.46/-0.01
- Pprov: 82/-0.43/+0.00, 89/-0.45/-0.01, 84/-0.45/-0.03, 91/-0.42/-0.04, 90/-0.43/-0.03, 82/-0.42/-0.06, 89/-0.44/-0.05, 80/-0.38/-0.03
- Lprov: 22/-0.07/+0.00, 22/-0.03/-0.01, 29/-0.04/-0.01, 27/-0.06/-0.02, 20/-0.06/-0.01, 22/-0.04/-0.01, 29/-0.04/-0.00, 22/-0.07/+0.00
- Other conditions: results/ablate/tab.txt.

Herd deaths by cause, last 100 y, per year (per herd goat-year), from fig/herd_deaths.txt: predation AH4 1.46 (0.088),
AH5 0.77 (0.007), Lbuck 0.67 (0.007), Pprov 3.76 (0.044), Lprov 0.27 (0.011); fight AH4 0.37 (0.022), AH5 0.52 (0.005),
Lbuck 6.49 (0.071), Pprov 6.52 (0.076), Lprov 0.08 (0.003); all causes AH4 6.42 (0.386), AH5 36.24 (0.322),
Lbuck 39.31 (0.433), Pprov 39.24 (0.457), Lprov 7.99 (0.330).

Code read for this entry (src/world.js mate(), src/animals.js fightingAbility()): with buckManagement on, a herd doe
next to one of her camp's keepSires (2, oldest) bucks mates with him without a contest; otherwise the bucks present
contest, and fighting ability is size × (1 + hornW × H).

**Against the predictions:**
- AH4 herd under 25 and R gap no wider than -0.06: met (16.6, -0.037).
- AH5 herd over 90, R gap -0.5 or wider, B gap -0.4 or wider: met (112.4, -0.572, -0.660).
- Removing kidShelter or buckManagement costs the most herd, each at least 30% below AH5: not met. Lshelter 114.7 (+2%),
  Lbuck 90.8 (-19%). The largest cost is Lprov, 24.2 (-78%).
- Removing guarding costs the least, within 15% of AH5: within 15% met (100.9, -10%); the least not met (Lshelter +2%,
  Ltether -1.5%).
- No single added component takes H4's herd over 60: not met. Pprov 85.9, 8 of 8 over 80.
- Herds over 80 have R gap -0.4 or wider and B gap -0.3 or wider: not met. R met everywhere (Lbuck -0.416, Pprov
  -0.428); B not met in Lbuck (-0.007) or Pprov (-0.028), every seed within -0.06.
- Herds under 40 keep both gaps within -0.1: met (AH4, Lprov, Pguard, Pshelter, Pbuck, Ptether; every seed).

## [PRE-REGISTERED 2026-11-05] Twinning and triplets under H4 and H5
**Question:** Chris (2026-11-05) asked how demand for meat and milk could become a demand for earlier maturity and
higher fertility; we added the twinning gene L (twins cost 2 × 0.8 in gestation, are born at 0.8 size and share milk)
and, at his request, a small chance of triplets for high L. The literature found (search summaries only; primary
sources not opened) puts wild bezoar twinning at about 52% (Daghestan, n 19) to 66% plus 4% triplets (Turkey), and
domestic breeds anywhere from 10-34% (Kilis) to 83% (Pote): wild goats twin about as often as many breeds, so a
general rise in litter size is not a known domestication change in goats. Does the herders' selection move L, the
twin share or the age at first kid, and does twinning change H5's herd and gaps?
**Settings:** main at 3d73bc4. tools/twins.json: TH4, TH5 = tools/ablate.json AH4, AH5 plus twinMax 1, tripletMax 0.2
(tripletBirthSize 0.7, postpartumDays 0). Controls: results/ablate AH4, AH5 (seeds 1-8, code a4b7922), not re-run.
Check that the controls stand for the current code (src unchanged from a4b7922 to b7649b2): twins off, 2701028 against b7649b2, H5 seed 1, H4 seed 2 and H5 with costs seed 3, 200 years each (humans from year 5, herding from year 10), 0 of 200 differ (negative control, costs on against off, 200 of 200); postpartumDays 0 at 3d480e8 against 2701028, 0 of 200; twins and triplets off at 3d73bc4 against 3d480e8, H5 seed 1, 0 of 200. With twins on and
triplets off, H5 seed 1 and H4 seed 2 for 300 years against the code before triplets: 0 of 300 differ. Negative
control: tripletMax 0.2 against 0 differs in 300 of 300 years, both conditions. Smoke (same early-humans runs, one
seed each, 300 y, tripletMax 0.2), years 201-300: TH5 wild litters 56/44/0.6% single/twin/triplet, herd 41/57/1.9%,
mean L 0.54, herd 136; TH4 wild 47/51/2.0%, herd 51/48/1.0%, herd 11. Unweaned deaths per kid, wild: singles 0.08,
twins 0.10, triplets 0.23 (TH5).
**Method:** `node tools/batch.mjs tools/twins.json results/twins 1600 8 10` (16 runs, 10 workers). Per condition at
1501-1600, means over seeds, beside AH4 and AH5: herded; herd − wild gaps in R, A, S, B and L (herdTraitMeans against
the wild mean); litters by size, herd and wild; unweaned deaths per kid by litter size; median first-kid age, herd and
wild; herd births per herd goat-year; per-seed herd and L gap; L by 100-y window.
**Prediction** (years 1501-1600, 8 seeds):
- TH5 herd L gap +0.05 or wider: the opportunity cull keeps does by their own kidding record, which counts each twin,
  and provision pays the twins' extra cost. This would be a mismatch with the historical record above. TH4 herd L gap
  within ±0.05 (herds small and refounded from captures, as in AH4).
- TH5 herd twin share at least 5 points above wild.
- Wild twin share 35-60%; triplets under 3% of litters, wild and herd.
- TH5 herd within 15% of AH5 (112.4); R and B gaps within 0.1 of AH5's (-0.572, -0.660). TH4 herd under 25.
- Herd median first-kid age younger than wild in TH5, by at least 100 days.

## [RESULTS 2026-11-05] Twinning and triplets under H4 and H5 (raw)
**Run:** `node tools/batch.mjs tools/twins.json results/twins 1600 8 10`, 17:20Z to 18:29Z, 16 of 16 done, no FAIL.
Table: scratchpad twins_tab.py (checked first against the H5 ablation entry: AH4 16.6 / R -0.037, AH5 112.4 / R -0.572 /
B -0.660 reproduced). Gaps are herd − wild (wild mean = (all × n − herd × nh)/(n − nh)). Controls AH4, AH5 from
results/ablate predate the litter and first-kid fields.

Means over 8 seeds, 1501-1600:

| cond | herd | R | A | S | B | L | herd births/goat-y | wild L |
|---|---|---|---|---|---|---|---|---|
| AH4 | 16.6 | -0.037 | +0.001 | +0.004 | -0.006 | | 0.343 | |
| TH4 | 17.6 | -0.043 | -0.002 | -0.002 | -0.004 | -0.008 | 0.396 | 0.564 |
| AH5 | 112.4 | -0.572 | -0.116 | +0.096 | -0.660 | | 0.359 | |
| TH5 | 120.0 | -0.570 | -0.036 | +0.048 | -0.590 | -0.060 | 0.445 | 0.590 |

Litters, single/twin/triplet, and unweaned deaths per kid by litter size, 1501-1600 (pooled over seeds):
- TH4 wild 46.6/51.2/2.2%, deaths 0.083/0.118/0.289; herd 48.2/49.5/2.3%, deaths 0.198/0.173/0.238.
- TH5 wild 44.3/53.2/2.5%, deaths 0.090/0.121/0.292; herd 50.8/47.3/1.9%, deaths 0.069/0.161/0.323.

Median first-kid age (days), 1501-1600: TH4 herd 1022, wild 1077; TH5 herd 725, wild 1076.

By window, herd / L gap / wild L: TH4 401-500 15.8 / -0.007 / 0.460, 801-900 17.5 / -0.006 / 0.435, 1201-1300
16.7 / -0.005 / 0.500; TH5 401-500 77.0 / +0.036 / 0.498, 801-900 107.4 / -0.011 / 0.532, 1201-1300 111.8 / +0.017 /
0.549. TH5 herd births per herd goat-year 0.563, 0.495, 0.476 in those windows.

Per seed, 1501-1600, herd / L gap / R gap: TH4 12/+0.00/-0.03, 19/-0.02/-0.06, 25/+0.00/-0.04, 24/-0.03/-0.06,
12/-0.01/-0.03, 16/-0.00/-0.04, 20/+0.00/-0.04, 13/-0.01/-0.05; TH5 129/-0.25/-0.57, 126/-0.03/-0.57, 113/+0.00/-0.57,
125/-0.03/-0.61, 111/+0.07/-0.58, 114/-0.06/-0.54, 128/-0.11/-0.57, 114/-0.08/-0.55.

TH5 L gap per seed, 100-y windows starting 401, 601, 801, 1001, 1201, 1401: s1 +0.01 +0.02 -0.04 -0.11 -0.06 -0.18; s2 +0.01 -0.04 -0.08 -0.07 +0.01
-0.08; s3 -0.00 -0.01 +0.03 +0.01 +0.11 +0.08; s4 +0.02 -0.06 -0.05 +0.01 -0.10 -0.08; s5 +0.09 +0.03 +0.09 -0.04 +0.11
+0.04; s6 +0.08 -0.03 -0.02 -0.03 +0.06 -0.09; s7 +0.05 +0.00 -0.12 -0.16 +0.02 -0.08; s8 +0.03 +0.05 +0.11 +0.11 -0.01
-0.16. Herd twin share / wild, 1501-1600, s1-s8: 36/59, 48/49, 48/49, 54/57, 66/60, 42/48, 45/55, 40/49.
Milk taken (year record `milk`): 0 in every TH5 and AH5 run, 1501-1600 (H5 does not milk).

**Against the predictions:**
- TH5 herd L gap +0.05 or wider: not met (-0.060; 1 of 8 seeds at +0.05 or wider). TH4 within ±0.05: met (-0.008).
- TH5 herd twin share at least 5 points above wild: not met (47.3 vs 53.2, 5.9 below).
- Wild twin share 35-60%: met (TH4 51.2, TH5 53.2). Triplets under 3% of litters: met (1.9-2.5%).
- TH5 herd within 15% of AH5: met (120.0, +7%). R gap within 0.1: met (-0.570 vs -0.572). B gap within 0.1: met
  (-0.590 vs -0.660). TH4 herd under 25: met (17.6).
- TH5 herd median first-kid age at least 100 days younger than wild: met (725 vs 1076).

## [PRE-REGISTERED 2026-11-05] Milking at a fixed share, H5 with twins
**Question:** Chris (2026-11-05): milking as opportunistic herders would do it, a fixed share taken first and the kids
second. Does milking move milk yield (M), twinning (L), herd size or the R and B gaps, and why do herd twins die more
than herd singles (twinning batch: unweaned deaths per kid 0.161 vs 0.069 in TH5 herds; wild 0.121 vs 0.090)? With the
economy off the milk taken feeds only herd orphans (camp milk pool), as culled meat feeds nothing: the take is a fixed
policy that costs the goats.
**Settings:** main at 7089922. Lactation fix (a7c2895): a doe lactates, pays and is milked while any kid of her litter is
unweaned; before, only while the first was, so a surviving second twin drank free. The twinning batch (results/twins)
carries that bug. New records (same commit): unweaned deaths by cause and litter size; mean size and E/cap at first
kidding, herd and wild. tools/milk.json: FH4 = TH4 re-run; M0 = TH5 re-run; M25, M50 = M0 with milkIntensity 0.25, 0.5.
Checks (H5, humans from year 5, herding from year 10): twins off, a7c2895 against 3d73bc4, 0 of 200 years differ, and
with milkIntensity 0.3, 0 of 200; twins on, fix against before, 300 of 300 differ (the fix bites); twins on, fix with
against without the new records, 0 of 300. Smoke (one seed each, years 201-300): herd 121 (M0), 114 (M25), 112 (M50);
herd gaps L +0.03, +0.19, +0.09; M +0.01, +0.25, +0.07; B -0.67, -0.59, -0.37; herd twin share 44, 66, 55% (wild
39-51%). Herd unweaned deaths in M0, singles/twins/triplets: starvation 4/284/25, other 104/169/5, predation 15/16/0;
wild starvation 7/140/32. Mean size at first kidding, herd 0.77-0.97, wild 1.26-1.30; condition herd 0.50-0.57, wild
0.64-0.66. Milk capacity and kid need do not depend on the doe's or the kid's size (milkBase × (0.5 + M); kidMilkNeed).
Some predictions below lean on this one-seed smoke, as marked.
**Method:** `node tools/batch.mjs tools/milk.json results/milk 1600 8 10` (32 runs, 10 workers). Per condition at
1501-1600, means over seeds: herded; herd − wild gaps in R, A, S, B, L, M; litters by size, herd and wild; unweaned
deaths per kid by litter size and by cause; milk taken per year; median first-kid age, and size and condition at first
kidding, herd and wild; per-seed herd, L and M gaps; L and M gaps by 100-y window.
**Prediction** (years 1501-1600, 8 seeds):
- M gap: M0 within ±0.05; M25 and M50 +0.10 or wider (with a share taken first, only a doe with more capacity leaves her
  kids enough), M50 at least as wide as M25.
- L gap: M0 and FH4 within ±0.05 (the twinning batch read as drift). M25 and M50 within ±0.05 of M0 (milking does not
  move L on balance).
- Herd twin deaths: starvation is at least half of herd twin and triplet unweaned deaths in M0, M25 and M50, and under
  10% of herd single deaths (from the smoke).
- Herd: M0, M25, M50 all over 90; M50 at least 5% below M0. R gap within 0.1 of M0 in M25 and M50. B gap in M50 at
  least 0.1 narrower than in M0 (from the smoke). FH4 herd under 25.
- Herd does are smaller at first kidding than wild does in every H5 arm (B gap), by at least 0.2 in size.

## [RESULTS 2026-11-05] Milking at a fixed share, H5 with twins (raw)
**Run:** `node tools/batch.mjs tools/milk.json results/milk 1600 8 10`, to 23:46Z, 32 of 32 done, no FAIL. Table:
scratchpad milk_tab.py. Gaps are herd − wild. Milk is the year record `milk` (kcal taken per year, all camps).

Means over 8 seeds, 1501-1600:

| cond | herd | milk/y | herd births/goat-y | R | A | S | B | L | M |
|---|---|---|---|---|---|---|---|---|---|
| FH4 | 16.7 | 0 | 0.397 | -0.038 | -0.001 | +0.007 | -0.007 | +0.010 | -0.003 |
| M0 | 117.6 | 0 | 0.447 | -0.581 | -0.045 | +0.054 | -0.578 | -0.037 | +0.001 |
| M25 | 112.6 | 1,712,158 | 0.481 | -0.538 | -0.038 | +0.076 | -0.519 | -0.041 | +0.030 |
| M50 | 117.4 | 3,320,774 | 0.490 | -0.577 | -0.017 | +0.043 | -0.514 | -0.047 | -0.026 |

Herd, 1501-1600: litters single/twin/triplet; unweaned deaths per kid by litter size; first-kid median age, mean size,
mean condition (E/cap):
- FH4: 41.2/55.1/3.7%; 0.190/0.191/0.288; 1020 d, 1.294, 0.808.
- M0: 52.1/46.3/1.6%; 0.065/0.132/0.291; 724 d, 0.856, 0.590.
- M25: 48.9/49.2/2.0%; 0.072/0.214/0.346; 726 d, 0.910, 0.624.
- M50: 47.0/50.4/2.5%; 0.066/0.199/0.385; 733 d, 0.920, 0.643.

Wild, same: FH4 43.4/53.8/2.9%, 0.082/0.119/0.304, 1078 d, 1.306, 0.697; M0 48.2/49.6/2.2%, 0.090/0.118/0.284, 1072 d,
1.295, 0.670; M25 45.1/52.1/2.8%, 0.095/0.123/0.299, 1074 d, 1.296, 0.684; M50 42.8/54.3/2.9%, 0.092/0.119/0.297,
1077 d, 1.304, 0.687.

Unweaned deaths by cause, [single, twin, triplet], summed over 8 seeds, 1501-1600:
- FH4 herd: starvation 21/125/40, other 68/224/19, predation 165/318/36, culled 12/14/1.
- M0 herd: starvation 3/1780/310, other 845/1427/64, predation 81/154/6, culled 45/26/0.
- M25 herd: starvation 0/4287/491, other 859/1464/71, predation 110/181/7, culled 29/15/0.
- M50 herd: starvation 0/4226/733, other 834/1540/95, predation 88/147/16, culled 16/17/1.
- Wild (M0): starvation 59/2544/1058, other 2045/4131/237, predation 692/1258/80, hunted 433/841/36. Wild in the other
  arms is similar (starvation 66-74 singles, 2898-3426 twins, 1358-1573 triplets).
Starvation's share of herd twin and triplet deaths: M0 0.55, M25 0.73, M50 0.73; of herd single deaths 0.003, 0, 0.

By window, herd / L gap / M gap: 401-500 FH4 15.2/-0.006/+0.007, M0 73.8/+0.012/+0.002, M25 77.4/+0.042/-0.006, M50
75.9/+0.017/-0.000; 801-900 FH4 16.3/-0.000/-0.001, M0 105.1/+0.031/-0.003, M25 108.0/+0.042/-0.018, M50
110.3/+0.027/-0.005; 1201-1300 FH4 16.0/+0.002/+0.001, M0 112.8/-0.003/+0.011, M25 110.4/-0.084/+0.052, M50
116.4/-0.048/-0.011.

Per seed, 1501-1600, herd / L gap / M gap / B gap:
- M0: 117/-0.06/+0.01/-0.52, 121/-0.21/-0.02/-0.70, 115/-0.03/+0.01/-0.56, 106/+0.12/-0.04/-0.39, 124/-0.13/-0.01/-0.66,
  115/+0.04/+0.03/-0.59, 122/+0.08/+0.05/-0.63, 120/-0.10/-0.04/-0.58
- M25: 112/-0.02/-0.02/-0.50, 112/-0.17/-0.02/-0.57, 116/-0.02/-0.02/-0.50, 118/+0.09/+0.04/-0.51, 113/-0.16/+0.09/-0.60,
  113/+0.03/+0.04/-0.57, 105/-0.10/+0.11/-0.44, 111/+0.02/+0.01/-0.45
- M50: 122/-0.09/+0.06/-0.53, 118/+0.03/-0.05/-0.49, 114/+0.15/+0.00/-0.42, 118/-0.06/-0.00/-0.48, 111/-0.02/-0.05/-0.44,
  117/-0.26/-0.04/-0.63, 120/-0.12/-0.09/-0.58, 119/-0.01/-0.05/-0.54
- FH4: 12/+0.00/-0.00/-0.01, 15/+0.03/-0.01/-0.00, 22/+0.01/+0.01/+0.00, 17/+0.00/-0.01/-0.03, 14/-0.01/+0.00/-0.01,
  14/-0.01/-0.01/-0.01, 21/+0.02/-0.00/+0.00, 18/+0.02/-0.01/-0.01

**Against the predictions:**
- M gap M0 within ±0.05: met (+0.001). M25 and M50 +0.10 or wider: not met (+0.030, -0.026). M50 at least as wide as
  M25: not met.
- L gap M0 and FH4 within ±0.05: met (-0.037, +0.010). M25 and M50 within ±0.05 of M0: met (-0.041, -0.047).
- Starvation at least half of herd twin and triplet deaths in M0, M25, M50: met (0.55, 0.73, 0.73); under 10% of herd
  single deaths: met (0.003, 0, 0).
- Herd over 90 in M0, M25, M50: met. M50 at least 5% below M0: not met (117.4 vs 117.6). R gap within 0.1 of M0: met
  (-0.538, -0.577 vs -0.581). B gap in M50 at least 0.1 narrower than M0: not met (-0.514 vs -0.578, 0.064). FH4 herd
  under 25: met (16.7).
- Herd does at least 0.2 smaller than wild at first kidding in every H5 arm: met (0.44, 0.39, 0.38).

## [PRE-REGISTERED 2026-11-05] Milk batch re-run with milk shared within the litter
**Question:** The milk batch (results/milk) found herd twin deaths mostly starvation (M0 0.55, M25 and M50 0.73 of twin
and triplet deaths; singles 0.003 or less) and no M response to milking. Reading the code afterwards: goats are processed
each day in a fixed order, so the first twin drank its fill every day and the second got what was left; at M 0.5 the
doe's capacity equals one newborn's need. Chris (2026-11-05) agreed to share the milk. Same question as the milk batch:
does a fixed-share milking (taken first) move M, L, herd size or the R and B gaps, now that the litter shares?
**Settings:** main at c766308: each kid of a litter takes up to (capacity − herders' take) / the litter's live unweaned
kids. tools/milk.json unchanged (FH4, M0, M25, M50). Checks (H5, humans from year 5, herding from year 10): twins off,
c766308 against 7089922, 0 of 200 years differ, and with milkIntensity 0.3, 0 of 200; twins on, 300 of 300 differ.
Smoke (one seed each, years 201-300; before → after sharing): herd 121 → 110 (M0), 114 → 103 (M25), 112 → 109 (M50);
herd M gap +0.01 → +0.10, +0.25 → +0.21, +0.07 → +0.16; herd L gap +0.03 → -0.17, +0.19 → -0.03, +0.09 → +0.07; herd
unweaned deaths per kid, single/twin/triplet, M0 0.06/0.14/0.34 → 0.07/0.09/0.05, M25 0.06/0.15/0.38 → 0.06/0.06/0.10,
M50 0.07/0.18/0.38 → 0.06/0.08/0.15; herd twin starvation deaths 284 → 51, 372 → 0, 484 → 41; wild twin deaths per
kid 0.08-0.09 (was 0.10-0.12); FH4 herd 17. Predictions below lean on this smoke where marked.
**Method:** `node tools/batch.mjs tools/milk.json results/milk2 1600 8 10` (32 runs, 10 workers). The same table as the
milk batch (scratchpad milk_tab.py), with results/milk beside it.
**Prediction** (years 1501-1600, 8 seeds):
- Herd twin unweaned deaths per kid within 0.03 of singles' in M0, M25, M50 (smoke); starvation under 25% of herd twin
  and triplet deaths in each.
- M gap: M25 and M50 each at least 0.05 wider than M0's (smoke), and M25 and M50 at least +0.05.
- Wild twin share over 55% in every arm (twins now die about as often as singles, so L should rise in the wild).
- Herd L gap within ±0.05 in M0 and FH4; M25 and M50 within ±0.05 of M0's.
- Herd over 90 in M0, M25 and M50; FH4 under 25. R gap within 0.1 of M0's in M25 and M50.
- Herd does at least 0.2 smaller than wild at first kidding in every H5 arm.

## [RESULTS 2026-11-05] Milk batch re-run with milk shared within the litter (raw)
**Run:** `node tools/batch.mjs tools/milk.json results/milk2 1600 8 10` at c766308; 32 of 32 done, no FAIL
(batch.log, ALL DONE 2026-11-06T03:35Z). Table from scratchpad milk_tab.py; means over 8 seeds; previous batch
(results/milk, before sharing) in brackets.
**Years 1501-1600:**

| | herd | births/herd goat-y | R gap | B gap | S gap | L gap | M gap | milk/y (kcal) |
|---|---|---|---|---|---|---|---|---|
| FH4 | 18.8 [16.7] | 0.422 [0.397] | -0.041 | -0.003 | +0.003 | +0.000 [+0.010] | -0.002 | 0 |
| M0 | 117.2 [117.6] | 0.484 [0.447] | -0.514 [-0.581] | -0.532 [-0.578] | +0.071 | -0.049 [-0.037] | +0.004 [+0.001] | 0 |
| M25 | 121.1 [112.6] | 0.486 [0.481] | -0.519 [-0.538] | -0.565 [-0.519] | +0.040 | -0.046 [-0.041] | -0.012 [+0.030] | 1,415,122 [1,712,158] |
| M50 | 120.6 [117.4] | 0.499 [0.490] | -0.515 [-0.577] | -0.523 [-0.514] | +0.051 | -0.032 [-0.047] | -0.009 [-0.026] | 2,809,678 [3,320,774] |

Litter shares, single/twin/triplet (%), and unweaned deaths per kid, single/twin/triplet:

| | wild litters | wild deaths/kid | herd litters | herd deaths/kid |
|---|---|---|---|---|
| FH4 | 25.3/67.1/7.5 [43.4/53.8/2.9] | 0.089/0.088/0.086 [0.082/0.119/0.304] | 24.5/68.0/7.5 | 0.183/0.189/0.157 [0.190/0.191/0.288] |
| M0 | 28.3/65.3/6.4 [48.2/49.6/2.2] | 0.096/0.095/0.090 [0.090/0.118/0.284] | 33.4/61.6/5.0 [52.1/46.3/1.6] | 0.076/0.069/0.068 [0.065/0.132/0.291] |
| M25 | 27.5/65.6/6.9 [45.1/52.1/2.8] | 0.097/0.095/0.089 | 33.0/62.0/5.0 [48.9/49.2/2.0] | 0.074/0.066/0.066 [0.072/0.214/0.346] |
| M50 | 25.0/67.5/7.6 [42.8/54.3/2.9] | 0.098/0.095/0.094 | 28.6/65.3/6.1 [47.0/50.4/2.5] | 0.075/0.067/0.065 [0.066/0.199/0.385] |

Herd kid deaths by cause, single/twin/triplet:
- M0: other 543/1956/231, predation 87/218/32, culled 44/21/0, starvation 2/46/3 (starvation 2.0% of twin and triplet
  deaths [0.55]).
- M25: other 556/2015/239, predation 74/210/27, culled 47/11/1, starvation 0/6/1 (0.3% [0.73]).
- M50: other 478/2083/282, predation 64/246/38, culled 41/19/0, starvation 0/0/0 (0% [0.73]).
- FH4: other 44/275/47, predation 86/502/66, starvation 19/110/11, culled 3/15/2.
- Wild starvation, single/twin/triplet: M0 47/377/66, M25 47/376/75, M50 45/396/93, FH4 49/404/102 (previous batch
  59-74 / 2544-3426 / 1058-1573).

First kidding: herd age 730-733 days, size 0.887-0.915, condition 0.595-0.604 in the H5 arms; wild 1080-1081 days,
size 1.303-1.307, condition 0.682-0.684. FH4 herd 1100 days, size 1.317, condition 0.860.

Per seed, herd / L gap / M gap / B gap:
- M0: 122/-0.08/+0.04/-0.64, 102/+0.03/-0.02/-0.21, 119/-0.02/-0.05/-0.65, 119/-0.08/-0.02/-0.53,
  117/-0.08/+0.01/-0.38, 119/-0.16/+0.06/-0.60, 117/+0.01/+0.00/-0.61, 123/-0.01/+0.01/-0.63
- M25: 124/-0.08/-0.05/-0.62, 134/-0.10/-0.05/-0.63, 122/-0.03/+0.03/-0.60, 121/-0.04/+0.03/-0.69,
  118/+0.00/-0.00/-0.56, 112/-0.03/+0.03/-0.34, 121/-0.07/-0.02/-0.60, 117/-0.02/-0.07/-0.49
- M50: 125/-0.09/-0.03/-0.53, 134/+0.05/-0.02/-0.69, 119/-0.06/-0.01/-0.60, 121/-0.02/-0.03/-0.52,
  111/-0.01/-0.02/-0.13, 113/-0.01/-0.01/-0.50, 125/-0.04/+0.05/-0.68, 117/-0.08/+0.00/-0.53

**Earlier windows** (herd; R, B, L, M gaps):
- 401-500: FH4 16.0; M0 75.2 (-0.082, -0.018, +0.024, +0.008); M25 73.6 (-0.080, -0.019, +0.015, +0.004);
  M50 74.8 (-0.078, -0.019, +0.024, +0.004).
- 801-900: FH4 17.4; M0 106.7 (-0.435, -0.293, +0.025, +0.010); M25 106.9 (-0.433, -0.219, +0.020, +0.015);
  M50 105.5 (-0.335, -0.146, +0.023, +0.006).
- 1201-1300: FH4 17.8; M0 114.8 (-0.508, -0.505, -0.044, +0.025); M25 111.3 (-0.516, -0.504, -0.013, +0.042);
  M50 114.3 (-0.474, -0.412, -0.013, +0.028).

**Prediction scoring:**
- Herd twin deaths per kid within 0.03 of singles': met (M0 0.069 vs 0.076, M25 0.066 vs 0.074, M50 0.067 vs 0.075).
  Starvation under 25% of herd twin and triplet deaths: met (2.0%, 0.3%, 0%).
- M25 and M50 M gaps at least 0.05 wider than M0's and at least +0.05: not met (M0 +0.004, M25 -0.012, M50 -0.009).
  The one-seed smoke (+0.10, +0.21, +0.16 at years 201-300) did not hold.
- Wild twin share over 55%: met (65.3-67.5% twin litters, 6.4-7.6% triplets).
- Herd L gap within ±0.05 in M0 and FH4: met (-0.049, +0.000). M25 and M50 within ±0.05 of M0's: met (-0.046, -0.032).
- Herd over 90 in the H5 arms: met (117.2, 121.1, 120.6). FH4 under 25: met (18.8). R gap within 0.1 of M0's: met
  (-0.519, -0.515 vs -0.514).
- Herd does at least 0.2 smaller than wild at first kidding: met (0.39-0.42 smaller).

## [PRE-REGISTERED 2026-11-06] Milk batch under milk paid as made and size-dependent kid deaths
**Question:** In the shared-milk re-run (results/milk2) milking did not move M (M gaps +0.004, -0.012, -0.009), and M
fell from 0.50 to about 0.18 everywhere, wild and herd alike. The doe paid for her whole capacity every day, and twins
died no more than singles, because most kid deaths were a flat first-year hazard that ignored size. Chris (2026-11-05):
the doe should pay for the milk she makes (what is drunk and taken), and kid death should track size. With both, does
milking at a fixed share move M, L, herd size, births, or the R and B gaps?
**Settings:** main at c80f0ca (model code f4ddeff). New defaults: `milkCost 'made'` (the doe pays for what her kids
drink, as they drink it, and for the herders' take); `juvSizeExp 1.5` (the first-year hazard × (ref / size)^1.5, ref a
single with the same target grown at full rate; provisional, MODEL G14). tools/milk.json unchanged (FH4, M0, M25,
M50). Checks: `milkCost=capacity` reproduces c766308 (H5, twins on and off, milkIntensity 0.25, seed 1, 300 years:
0 of 300 years differ); `juvSizeExp=0` reproduces ec96ea3 (H5 twins on: 0 of 300); a default run equals an explicit
juvSizeExp=1.5 run (0 of 300). New year counters (`kidLife`) were checked inert (0 of 300, twins on and off;
negative control 300 of 300).
Smoke (one seed each, humans from year 5, herding from year 10, years 201-300):
- **Population:** herd FH4 13, M0 112, M25 124, M50 126.
- **M (all goats):** 0.53, 0.51, 0.48, 0.60 (M was 0.30-0.34 by year 200-300 under the old cost).
- **Herd gaps:**
  - M: -0.02, -0.03, -0.22, +0.08;
  - L: +0.02, +0.02, +0.16, +0.07;
  - R: -0.03, -0.57, -0.56, -0.63.
- **Wild twin litters:** 37%, 37%, 27%, 27% (46% with the flat hazard).
- **Herd twin deaths per kid over singles':** M0 1.27×, M25 1.44×, M50 1.78×.
- **Herd births per herd goat-year:** M0 0.429, M25 0.440, M50 0.388.
- **Herd twins drank:** 782 kcal a day at M0, 470 at M50 (wild twins about 820).
**Method:** `node tools/batch.mjs tools/milk.json results/milk3 1600 8 10` (32 runs, 10 workers). Scratchpad
milk_tab.py and kl_tab.py, with results/milk2 beside it.
**Prediction** (years 1501-1600, 8 seeds):
- M (all goats) at least 0.40 in every arm (0.18 in milk2).
- M gap: M50 at least +0.05 and at least 0.05 wider than M0's; M25 between M0's and M50's.
- Herd twin deaths per kid at least 1.15× singles' in every H5 arm, and higher at M50 than at M0.
- Wild twin share between 20% and 45% of litters in every arm (65-68% in milk2).
- Herd L gap at least 0 in M0 (the opportunity cull keeps does by kids born, twins counted), and lower at M50
  than at M0.
- Herd births per herd goat-year at least 0.02 lower at M50 than at M0.
- Herd over 90 in M0, M25 and M50; FH4 under 25. R gap within 0.1 of M0's in M25 and M50.
- Herd does at least 0.2 smaller than wild at first kidding in every H5 arm.

## [RESULTS 2026-11-06] Milk batch under milk paid as made and size-dependent kid deaths (raw)
**Run:** `node tools/batch.mjs tools/milk.json results/milk3 1600 8 10` at c80f0ca; 32 of 32 done, no FAIL (batch.log,
ALL DONE 2026-11-06T22:55Z). Tables from scratchpad milk_tab.py and an inline pooled kidLife sum; means over 8 seeds;
results/milk2 (old cost, flat kid hazard) in brackets.
**Years 1501-1600:**

| | herd | births/herd goat-y | R gap | B gap | L gap | M gap | M all / herd / wild | milk/y (kcal) |
|---|---|---|---|---|---|---|---|---|
| FH4 | 16.0 [18.8] | 0.406 [0.422] | -0.038 | -0.002 | -0.009 | -0.008 | 0.694 / 0.686 / 0.694 | 0 |
| M0 | 122.2 [117.2] | 0.407 [0.484] | -0.590 [-0.514] | -0.647 [-0.532] | -0.024 [-0.049] | -0.052 [+0.004] | 0.640 / 0.601 / 0.653 | 0 |
| M25 | 117.1 [121.1] | 0.421 [0.486] | -0.605 [-0.519] | -0.596 [-0.565] | -0.028 [-0.046] | -0.056 [-0.012] | 0.617 / 0.574 / 0.629 | 2,270,844 |
| M50 | 116.3 [120.6] | 0.434 [0.499] | -0.581 [-0.515] | -0.601 [-0.523] | +0.007 [-0.032] | -0.130 [-0.009] | 0.618 / 0.514 / 0.644 | 4,369,589 |

(M all goats in milk2: about 0.18 in every arm. Absolute M in milk3 at 401-500 / 801-900: FH4 0.627 / 0.692, M0 0.611 /
0.644, M25 0.600 / 0.611, M50 0.617 / 0.606; herd M at M50 0.606 / 0.583.)

Litters single/twin/triplet (%) and unweaned deaths per kid:
- Wild: FH4 55.3/43.4/1.3, 0.082/0.098/0.123; M0 56.5/42.5/1.0, 0.090/0.105/0.142; M25 54.1/44.7/1.2,
  0.085/0.105/0.119; M50 57.2/42.0/0.7, 0.087/0.103/0.124 (milk2 wild twins 65.3-67.5%).
- Herd: FH4 54.7/44.1/1.2, 0.179/0.192/0.231; M0 60.7/38.6/0.7, 0.0726/0.0838/0.1004 (twins 1.153×, triplets 1.382×
  singles'); M25 57.2/42.0/0.7, 0.0681/0.0873/0.1084 (1.283×, 1.591×); M50 57.5/41.7/0.8, 0.0760/0.1112/0.1449
  (1.464×, 1.908×).
- Herd kid deaths by cause, single/twin/triplet: M0 other 1079/1504/52, predation 95/124/4, culled 72/27/0, starvation
  27/151/0; M25 other 925/1823/62, predation 79/146/4, culled 63/10/0, starvation 1/23/0; M50 other 1073/2445/85,
  predation 110/127/4, culled 51/14/0, starvation 2/20/1.

Unweaned kid energy, kcal per kid-day (milk from the mother, camp pool, grazed, fodder), and at weaning size / size over
target / condition, pooled over seeds:
- M0 herd single 1045, 0, 806, 379; 0.530 / 0.709 / 0.731. Twin 831, 0, 711, 371; 0.490 / 0.635 / 0.547.
- M25 herd single 995, 33, 769, 436; 0.540 / 0.691 / 0.700. Twin 676, 28, 634, 378; 0.460 / 0.567 / 0.489.
- M50 herd single 787, 37, 762, 387; 0.517 / 0.653 / 0.553. Twin 465, 46, 559, 301; 0.389 / 0.485 / 0.427.
- Wild (all three arms): single 1085-1087, 0, 766-785, 0; 0.534-0.538 / 0.417-0.418 / 0.378-0.387. Twin 875-886, 0,
  688-700, 0; 0.431-0.436 / 0.336-0.339 / 0.383-0.384.

First kidding: herd 723-725 days, size 0.796-0.830, condition 0.556-0.604 (H5 arms); wild 1025-1044 days, size
1.277-1.283. FH4 herd 911 days, size 1.289.

Per seed, herd / L gap / M gap / B gap:
- M0: 113/+0.10/+0.08/-0.56, 115/+0.02/+0.12/-0.62, 130/+0.10/-0.24/-0.69, 128/+0.02/-0.10/-0.72,
  112/-0.21/-0.10/-0.50, 121/-0.06/+0.07/-0.68, 140/-0.14/-0.17/-0.75, 119/-0.02/-0.08/-0.66
- M25: 128/+0.04/-0.13/-0.71, 106/+0.03/+0.01/-0.49, 122/-0.10/+0.09/-0.70, 133/+0.05/-0.22/-0.63,
  116/-0.10/-0.05/-0.61, 119/-0.11/-0.00/-0.56, 101/-0.02/-0.17/-0.45, 111/-0.01/+0.02/-0.61
- M50: 105/+0.01/-0.01/-0.53, 107/-0.01/-0.10/-0.45, 128/+0.12/-0.08/-0.63, 120/-0.07/-0.10/-0.69,
  122/-0.12/-0.26/-0.67, 111/+0.09/-0.17/-0.59, 116/+0.05/-0.25/-0.58, 122/-0.01/-0.08/-0.67

**Earlier windows** (herd; R, B, L, M gaps):
- 401-500: FH4 15.3; M0 65.3 (-0.077, -0.018, +0.023, -0.005); M25 68.3 (-0.082, -0.016, +0.025, -0.011);
  M50 65.4 (-0.086, -0.020, +0.024, -0.014).
- 801-900: FH4 15.7; M0 104.2 (-0.498, -0.276, +0.012, -0.044); M25 103.7 (-0.472, -0.288, +0.040, -0.000);
  M50 102.7 (-0.469, -0.288, +0.035, -0.028).
- 1201-1300: FH4 15.4; M0 120.9 (-0.569, -0.591, -0.024, -0.085); M25 109.4 (-0.528, -0.481, -0.013, -0.054);
  M50 116.8 (-0.551, -0.594, -0.015, -0.113).

**Prediction scoring:**
- M (all goats) at least 0.40 in every arm: met (0.617-0.694).
- M50 M gap at least +0.05 and at least 0.05 wider than M0's: not met (M50 -0.130, M0 -0.052; the gap widened in the
  negative direction). M25 between M0's and M50's: met as worded (-0.056), but next to M0, not partway to M50.
- Herd twin deaths per kid at least 1.15× singles' in every H5 arm: met (1.153×, 1.283×, 1.464×); higher at M50 than
  M0: met.
- Wild twin share 20-45% in every arm: met (42.0-44.7%).
- Herd L gap at least 0 in M0: not met (-0.024). Lower at M50 than M0: not met (+0.007 vs -0.024).
- Herd births per herd goat-year at least 0.02 lower at M50 than M0: not met (0.434 vs 0.407, higher).
- Herd over 90 in the H5 arms: met (122.2, 117.1, 116.3). FH4 under 25: met (16.0). R gap within 0.1 of M0's: met
  (-0.605, -0.581 vs -0.590).
- Herd does at least 0.2 smaller than wild at first kidding: met (0.45-0.49 smaller).

## [PRE-REGISTERED 2026-11-09] Doe-side milk selection: milk in the keep value, and a milk sire rule
**Question:** Under milk paid as made (results/milk3), milking at 0.5 left herd M below wild (gap -0.130), because a
fixed-share take costs a high-M doe more and nothing in the herders' policy rewarded yield. Chris (2026-11-09): build
herders that keep does by their milk, and breed from the sons of good milkers. Does milk selection by the herder move
herd M, and through which channel, culling does or choosing sires?
**Settings:** main at 0852621. `milkValue`: the opportunity keep value adds a doe's expected milk to the camp (her
record of milk taken per year since breeding age, blended with the camp's per-age record, survival-discounted over
keepHorizon 3) × milkValue / 36,000 kcal per meat unit. `sireRule 'milk'`: sires are the bucks whose dams gave the camp
most milk a year (dam record blended with the camp mean; a dam never milked counts as the mean); the opportunity cull
keeps the bucks that rule chose. tools/milksel.json: H5 with twins (twinMax 1, tripletMax 0.2), milkIntensity 0.5,
and S0 (milkValue 0), S025 (0.25), S1 (1), S1M (1 + sireRule milk). S0 is milk3's M50 on new code. Check: defaults
reproduce c80f0ca (H5 twins, milkIntensity 0.5, seed 1, 300 years: 0 of 300 years differ); milkValue 1 differs in 245
of 300, from year 55.
Smoke (one seed, humans from year 5, herding from year 10; years 201-300, S0 / S025 / S1 / S1M):
- **Herd:** 126.3 / 121.4 / 119.2 / 97.6.
- **Herd gaps:**
  - M: +0.076 / -0.060 / -0.054 / +0.206 (herd M at year 300: 0.685 / 0.481 / 0.486 / 0.812);
  - B: -0.680 / -0.661 / -0.650 / -0.119;
  - R: -0.633 / -0.554 / -0.578 / -0.537;
  - L: +0.065 / +0.015 / -0.037 / -0.055.
- **Herd does at first kidding:** size 0.745 / 0.788 / 0.778 / 1.185.
- **Herd births per goat-year:** 0.388 / 0.440 / 0.401 / 0.453.
**Method:** `node tools/batch.mjs tools/milksel.json results/milksel 1600 8 10` (32 runs, 10 workers). Scratchpad
milk_tab.py and the pooled kidLife sum, with results/milk3 M50 beside S0.
**Prediction** (years 1501-1600, 8 seeds):
- S0 equals results/milk3 M50 in every year of every seed (same code path, same seeds).
- S1M herd M gap at least +0.10; S025 and S1 herd M gaps within 0.05 of S0's (culling does alone is weak at 10%
  offtake).
- S1M B gap at least 0.2 narrower than S0's, and S1M herd does at first kidding within 0.2 of wild does' size.
- S1M herd at least 10 below S0's; herd over 70 in every arm.
- R gap within 0.1 of S0's in every arm.
- M (all goats) at least 0.40 in every arm.

## [RESULTS 2026-11-09] Doe-side milk selection: milk in the keep value, and a milk sire rule (raw)
**Run:** `node tools/batch.mjs tools/milksel.json results/milksel 1600 8 10` at 888ef05; 32 of 32 done, no FAIL
(batch.log, ALL DONE 2026-11-10T01:51Z). Tables from scratchpad milk_tab.py and inline sums over the year records;
means over 8 seeds. S0 against results/milk3 M50, year records compared whole: 0 of 1600 years differ in each of the 8
seeds (negative control, S025 seed 1 against M50 seed 1: 1195 years differ).
**Years 1501-1600:**

| | herd | births/herd goat-y | R gap | B gap | L gap | M gap | M all / herd | herd B | herd S | herd F | milk/herd goat-y (kcal) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 116.3 | 0.434 | -0.581 | -0.601 | +0.007 | -0.130 | 0.618 / 0.514 | 0.261 | 0.182 | 0.735 | 37,518 |
| S025 | 115.9 | 0.427 | -0.591 | -0.628 | -0.045 | -0.133 | 0.659 / 0.554 | 0.244 | 0.226 | 0.717 | 38,668 |
| S1 | 115.7 | 0.437 | -0.548 | -0.579 | -0.024 | -0.087 | 0.632 / 0.563 | 0.288 | 0.215 | 0.709 | 40,306 |
| S1M | 91.5 | 0.522 | -0.513 | -0.122 | +0.040 | +0.128 | 0.796 / 0.903 | 0.760 | 0.262 | 0.841 | 58,812 |

Other gaps (A, S): S0 -0.033, +0.053; S025 -0.036, +0.053; S1 -0.056, +0.086; S1M -0.057, +0.126. Total milk taken per
year: 4,369,589 / 4,514,282 / 4,657,950 / 5,370,395. Herd culls per year 12.3 / 12.5 / 12.3 / 10.2. Sires per camp
1.23-1.26, chosen-sired share of herd births 0.997-1.000, wild-sired 0.008-0.014 in every arm. M (all goats) per seed,
lowest: 0.545 / 0.528 / 0.477 / 0.717.

Litters single/twin/triplet (%) and unweaned deaths per kid:
- Wild: S0 57.2/42.0/0.7, 0.087/0.103/0.124; S025 55.7/42.9/1.4, 0.087/0.104/0.128; S1 57.4/41.6/1.0,
  0.090/0.106/0.141; S1M 54.5/44.4/1.0, 0.087/0.104/0.122.
- Herd: S0 57.5/41.7/0.8, 0.076/0.111/0.145; S025 60.9/37.6/1.5, 0.071/0.109/0.147; S1 60.5/38.6/0.8,
  0.070/0.109/0.160; S1M 48.7/49.3/2.0, 0.071/0.092/0.119.
- Herd kid deaths by cause, single/twin/triplet: S1M other 678/2037/164, predation 114/168/10, culled 80/46/1, no
  starvation (S0 other 1073/2445/85, predation 110/127/4, culled 51/14/0, starvation 2/20/1).

Unweaned kid energy, kcal per kid-day (milk from the mother, grazed, fodder), and at weaning size / size over target,
pooled over seeds:
- Herd single: S0 787, 762, 387; 0.517 / 0.653. S025 792, 812, 331; 0.513 / 0.684. S1 814, 730, 439; 0.525 / 0.653.
  S1M 949, 914, 423; 0.598 / 0.505.
- Herd twin: S0 465, 559, 301; 0.389 / 0.485. S025 472, 581, 297; 0.397 / 0.490. S1 477, 528, 343; 0.394 / 0.483.
  S1M 617, 712, 360; 0.486 / 0.401.
- Wild single 1086-1089 milk, 0.535-0.539 / 0.411-0.417 in every arm; wild twin 881-939 milk, 0.431-0.453 /
  0.334-0.348 (S1M highest).

First kidding: herd 723-727 days in every arm, size S0 0.830, S025 0.815, S1 0.844, S1M 1.212, condition 0.558-0.663;
wild 1030-1054 days, size 1.282-1.300.

Per seed, herd / L gap / M gap / B gap:
- S0: as results/milk3 M50.
- S025: 115/-0.08/-0.09/-0.65, 127/-0.09/-0.15/-0.72, 119/-0.06/-0.20/-0.67, 122/-0.11/-0.22/-0.74,
  101/+0.01/-0.11/-0.38, 112/-0.13/-0.08/-0.63, 120/-0.03/-0.01/-0.61, 110/+0.13/-0.20/-0.63
- S1: 114/+0.02/-0.17/-0.60, 114/-0.05/-0.08/-0.43, 124/+0.02/+0.03/-0.58, 97/+0.07/+0.02/-0.37,
  120/+0.04/-0.25/-0.71, 114/-0.07/-0.02/-0.68, 128/-0.14/-0.08/-0.72, 114/-0.08/-0.15/-0.54
- S1M: 94/-0.04/+0.15/-0.21, 91/-0.03/+0.07/-0.23, 85/+0.11/+0.23/-0.00, 92/+0.19/+0.11/-0.20,
  92/+0.04/+0.10/-0.04, 94/+0.00/+0.17/-0.14, 89/+0.05/+0.06/-0.07, 95/+0.01/+0.13/-0.08

**Earlier windows** (herd; R, B, L, M gaps; M all / herd):
- 201-300: no herds yet in any arm (identical wild runs).
- 401-500: S0 65.4 (-0.086, -0.020, +0.024, -0.014; 0.617 / 0.606); S025 62.3 (-0.073, -0.014, +0.011, +0.002; 0.620 /
  0.622); S1 63.6 (-0.079, -0.012, +0.025, -0.013; 0.601 / 0.590); S1M 68.1 (-0.106, -0.018, +0.007, +0.031; 0.641 /
  0.667).
- 801-900: S0 102.7 (-0.469, -0.288, +0.035, -0.028; 0.606 / 0.583); S025 103.2 (-0.461, -0.289, +0.030, -0.051; 0.638
  / 0.597); S1 100.2 (-0.438, -0.283, +0.024, -0.032; 0.590 / 0.564); S1M 95.4 (-0.495, -0.098, +0.009, +0.137; 0.775 /
  0.888).
- 1201-1300: S0 116.8 (-0.551, -0.594, -0.015, -0.113; 0.633 / 0.543); S025 110.5 (-0.570, -0.540, +0.011, -0.083;
  0.652 / 0.587); S1 113.6 (-0.544, -0.563, -0.014, -0.094; 0.628 / 0.553); S1M 94.2 (-0.525, -0.120, +0.012, +0.135;
  0.785 / 0.897).

**Prediction scoring:**
- S0 equals results/milk3 M50 in every year of every seed: met (0 of 1600 differ, 8 of 8 seeds).
- S1M herd M gap at least +0.10: met (+0.128; positive in 8 of 8 seeds). S025 and S1 within 0.05 of S0's -0.130: met
  (-0.133, -0.087).
- S1M B gap at least 0.2 narrower than S0's: met (-0.122 vs -0.601). S1M herd does at first kidding within 0.2 of wild
  size: met (1.212 vs 1.300).
- S1M herd at least 10 below S0's: met (91.5 vs 116.3). Herd over 70 in every arm: met (lowest seed 85).
- R gap within 0.1 of S0's in every arm: met (-0.591, -0.548, -0.513 vs -0.581).
- M (all goats) at least 0.40 in every arm: met (0.618-0.796; lowest seed 0.477).

## [PRE-REGISTERED 2026-11-10] Lineage isolation alone: sires by generations since the wild, no trait
**Question:** The grain paper (Marriott & Chebib, Artificial Life, accepted) found that domestication tracked the
reproductive isolation of the planted lineage, and that planting the seeds with the fewest generations since
planting, with no trait selected, produced the syndrome while planting the most produced none. Chris (2026-11-10):
run the goat version of that causal test. Does breeding the herd from its deepest lineage, with no trait looked at,
produce the herd - wild divergence across traits, and does breeding from fresh captures prevent it?
**Settings:** code of this entry's commit (after 8a219b6). New: sireRule 'deep' / 'shallow': the keepSires (2) adult
herd bucks with the most / fewest generations since the wild, genome-weighted (Goat.wildDepth, the per-goat form of
herdAncDepth; a captive scores 0); ties at the random preference. The opportunity cull now keeps the bucks any rule
but 'oldest' chose ('milk' already did), so the control and both lineage arms have their sires spared alike.
tools/lineage.json: tools/milksel.json S0 (H5 + twins, milkIntensity 0.5, milkValue 0) with sireRule random
(Lrandom, the control), deep (Ldeep), shallow (Lshallow). Reference: results/milksel S0 (oldest).
Checks (seed 1, 520 years, herding from year 400): S0 settings against results/milksel S0 seed 1, 0 of 520 years
differ; S1M settings (milk rule) against results/milksel S1M seed 1, 0 of 520 differ; Lrandom against S0 seed 1, 119
of 520 differ, from year 401.
Smoke (one seed, humans from year 5, herding from year 10, years 201-300; oldest / random / deep / shallow):
- **Herd:** 126.3 / 97.0 / 98.3 / 102.5.
- **Herd lineage depth (generations):** 8.15 / 8.73 / 16.11 / 1.51.
- **Herd IBD:** 0.585 / 0.551 / 0.790 / 0.284.
- **Captures per year:** 6.3 / 7.6 / 8.5 / 14.1.
- **Herd - wild gaps:**
  - R: -0.63 / -0.49 / -0.48 / -0.28;
  - B: -0.68 / -0.11 / -0.36 / -0.13;
  - A: -0.23 / -0.09 / -0.14 / -0.07;
  - S: +0.13 / -0.06 / +0.17 / +0.05;
  - H: -0.05 / -0.27 / -0.35 / -0.06;
  - L: +0.06 / +0.12 / +0.21 / +0.04.
**Method:** `node tools/batch.mjs tools/lineage.json results/lineage 1600 8 10` (24 runs, 10 workers). Per arm,
windows 401-500, 801-900, 1201-1300, 1501-1600: herd, lineage depth (herdAncDepth), herd genome share at depth 0
(herdWildAnc[0]), IBD, captures, wild-sired share, herd - wild gap for every trait (R A S B H T M W L), and the count
of traits with |gap| >= 0.10; scratchpad milk_tab.py where it applies; per seed herd / depth / R gap / B gap.
**Prediction** (years 1501-1600, 8 seeds; written before the smoke above, kept as written):
- **Isolation moves as intended:** herd lineage depth in Ldeep at least 2 generations above Lrandom's; Lshallow at
  least 2 below.
- **R:** Ldeep R gap at least 0.10 wider (more negative) than Lrandom's; Lshallow R gap at least 0.15 narrower.
- **Syndrome breadth:** Ldeep has at least as many traits with |gap| >= 0.10 as Lrandom; Lshallow fewer.
- **Body size:** Lshallow B gap at least 0.20 narrower than Lrandom's.
- **Inbreeding:** Ldeep herd IBD at least 0.05 above Lrandom's.
- **Herd size:** over 70 in every arm.
- **Depth against divergence:** across the 24 runs, r(herd lineage depth, R gap) -0.6 or stronger (the grain paper's
  Fig 7 analogue).

## [RESULTS 2026-11-10] Lineage isolation alone: sires by generations since the wild, no trait (raw)
**Run:** `node tools/batch.mjs tools/lineage.json results/lineage 1600 8 10` at 0da62de; 24 of 24 done, no FAIL
(batch.log, ALL DONE 2026-11-10T09:03Z). Tables from scratchpad lin_tab.py; means over 8 seeds. Reference S0 is
results/milksel S0 (oldest sires).
**Years 1501-1600:**

| | herd | lineage depth | depth-0 share | IBD | captures/y | wild-sired | traits with abs(gap) >= 0.10 |
|---|---|---|---|---|---|---|---|
| S0 (oldest) | 116.3 | 8.11 | 0.084 | 0.735 | 7.19 | 0.008 | 3 |
| Lrandom | 98.2 | 7.61 | 0.116 | 0.740 | 8.41 | 0.011 | 1 |
| Ldeep | 99.9 | 18.11 | 0.087 | 0.912 | 6.75 | 0.009 | 6 |
| Lshallow | 95.4 | 1.46 | 0.218 | 0.616 | 14.86 | 0.017 | 1 |

Herd - wild gaps:

| | R | A | S | B | H | T | M | W | L |
|---|---|---|---|---|---|---|---|---|---|
| S0 (oldest) | -0.581 | -0.033 | +0.053 | -0.601 | -0.042 | +0.054 | -0.130 | -0.010 | +0.007 |
| Lrandom | -0.477 | -0.000 | +0.016 | -0.044 | -0.018 | -0.014 | +0.019 | -0.007 | +0.009 |
| Ldeep | -0.569 | -0.105 | +0.183 | -0.121 | -0.212 | +0.045 | -0.078 | -0.103 | +0.025 |
| Lshallow | -0.208 | -0.003 | +0.004 | -0.022 | -0.005 | +0.000 | -0.006 | -0.002 | +0.016 |

Per seed, herd / depth / R gap / B gap:
- S0: 105/7.3/-0.55/-0.53, 107/5.6/-0.52/-0.45, 128/6.3/-0.56/-0.63, 120/11.9/-0.64/-0.69, 122/6.3/-0.55/-0.67,
  111/8.8/-0.62/-0.59, 116/11.1/-0.61/-0.58, 122/7.6/-0.58/-0.67
- Lrandom: 99/6.1/-0.39/-0.02, 101/7.0/-0.44/-0.05, 99/5.9/-0.41/-0.06, 102/9.5/-0.48/-0.02, 92/9.9/-0.57/-0.09,
  100/5.6/-0.43/-0.01, 96/7.0/-0.49/-0.03, 97/9.9/-0.59/-0.07
- Ldeep: 103/18.7/-0.59/-0.16, 99/16.0/-0.48/-0.14, 94/15.9/-0.50/-0.10, 98/20.2/-0.64/+0.00, 97/16.5/-0.55/-0.20,
  106/20.0/-0.67/-0.12, 105/17.5/-0.49/-0.18, 97/20.1/-0.63/-0.07
- Lshallow: 95/1.5/-0.17/-0.02, 93/1.4/-0.21/-0.00, 93/1.3/-0.15/-0.01, 102/1.5/-0.26/-0.03, 95/1.5/-0.18/-0.04,
  96/1.3/-0.22/-0.02, 97/1.6/-0.26/-0.04, 91/1.6/-0.21/-0.02

r(lineage depth, R gap) at 1501-1600 over the 24 lineage runs: -0.893. Within arm (8 runs each): Lrandom -0.885,
Ldeep -0.916, Lshallow -0.473.

**Earlier windows** (herd; depth; IBD; captures/y; R, B, H, S gaps; traits with abs(gap) >= 0.10), S0 / Lrandom /
Ldeep / Lshallow:
- 401-500: herd 65.4 / 69.0 / 68.6 / 61.7; depth 1.98 / 2.68 / 5.78 / 1.27; IBD 0.211 / 0.243 / 0.353 / 0.114;
  captures 10.94 / 11.20 / 11.23 / 10.21; R -0.086 / -0.106 / -0.102 / -0.072; no other gap past 0.04; traits 0 / 1 /
  1 / 0.
- 801-900: herd 102.7 / 100.0 / 100.5 / 94.6; depth 5.07 / 5.12 / 16.20 / 1.42; IBD 0.617 / 0.595 / 0.876 / 0.379;
  captures 8.64 / 10.86 / 8.31 / 15.11; R -0.469 / -0.374 / -0.484 / -0.192; B -0.288 / -0.055 / -0.094 / -0.013;
  H -0.022 / +0.002 / -0.069 / -0.006; S +0.066 / +0.003 / +0.109 / +0.008; traits 2 / 1 / 2 / 1.
- 1201-1300: herd 116.8 / 98.5 / 98.6 / 95.2; depth 7.60 / 5.76 / 18.33 / 1.49; IBD 0.720 / 0.682 / 0.897 / 0.533;
  captures 7.87 / 9.44 / 6.65 / 14.83; R -0.551 / -0.436 / -0.556 / -0.204; B -0.594 / -0.048 / -0.139 / -0.015;
  H -0.045 / -0.045 / -0.180 / -0.003; S +0.049 / +0.035 / +0.163 / +0.007; traits 3 / 1 / 4 / 1.

**Prediction scoring:**
- Ldeep depth at least 2 above Lrandom's: met (18.11 vs 7.61). Lshallow at least 2 below: met (1.46).
- Ldeep R gap at least 0.10 wider than Lrandom's: not met (-0.569 vs -0.477, 0.092 wider). Lshallow at least 0.15
  narrower: met (-0.208, 0.269 narrower).
- Ldeep traits with abs(gap) >= 0.10 at least Lrandom's: met (6 vs 1). Lshallow fewer than Lrandom: not met (1 and 1;
  R in both).
- Lshallow B gap at least 0.20 narrower than Lrandom's: not met (-0.022 vs -0.044; Lrandom's B gap is -0.044, not the
  S0-sized gap the prediction assumed).
- Ldeep IBD at least 0.05 above Lrandom's: met (0.912 vs 0.740).
- Herd over 70 in every arm: met (lowest seed 91).
- r(lineage depth, R gap) across the 24 runs -0.6 or stronger: met (-0.893).

## [PRE-REGISTERED 2026-11-10] Herder-visible selection: homebred and marked sires, exchange, body-size checks, Wild Type I
**Question:** Chris (2026-11-10), after the lineage test: which selection profiles were open to opportunistic herders,
and what else to settle before calling the model done. The deep rule ranks bucks by genome share at each depth since
the wild, which no herder sees. (1) Does a pedigree a herder could know (camp-born, and the dam's line) carry the
isolation and the syndrome? (2) Chris's prediction: selecting on a neutral appearance trait drives the syndrome for the
same reason (it passes over wild-born animals). (3) Chris's prediction: goat exchange between camps has no effect. (4)
Is the -0.60 B gap under oldest sires the oldest rule itself, or the oldest rule under the opportunity cull? (5)
Wild Type I: the wild with wolves only, to year 1600 (the burn-in to 300 is this, shorter).
**Settings:** code of this entry's commit (after 8ccf027). New:
- Neutral gene C (coat marking; genome.js): no mechanism reads it. Its alleles draw from a third random stream
  (rand3), and it is left out of the genome cost and of IBD.
- sireRule 'homebred': the keepSires bucks with the most generations of camp-born dams on the maternal line (gsc),
  capped at herdMemory (default 3; 1 = camp-born over captured). Ties at the random preference.
- sireRule 'marked': the keepSires bucks with the most C.
- exchangeN (exchangeGoats): at each year's end every camp with a herd gives exchangeN adults, at random, to another
  camp with a herd, at random. It never gives its sires, a tethered, guarded or led goat, or a doe with a kid at foot.
tools/herders.json is tools/milksel.json S0 with:
- Hbred: homebred, herdMemory 1.
- Hped: homebred, herdMemory 3.
- Cmarked: marked.
- X: exchangeN 2, oldest sires.
- Bold_rc: cullRule random, keepChosenSires 1, oldest.
- Brand_rc: cullRule random, keepChosenSires 1, random.
- WT: humansAt 1e9.
References: results/milksel S0, results/lineage Lrandom and Ldeep.
Checks (seed 1, 520 years, herding from year 400; year records compared with C and the exchanged count set aside):
S0 settings against results/milksel S0 seed 1, Ldeep against results/lineage Ldeep seed 1, Lrandom against
results/lineage Lrandom seed 1: 0 of 520 years differ in each. New arms against the earlier smoke runs: Hbred and X
against oldest differ from years 12 and 13; Brand_rc against random differs from year 14.
Smoke (one seed, humans from year 5, herding from year 10, years 201-300; oldest, random and deep from the lineage
smoke). Columns: herd, depth, IBD, captures/y, exchanged/y, then gaps R / B / H / S / C, then the count of traits
other than C with abs(gap) >= 0.10:

| Arm | herd | depth | IBD | captures/y | exchanged/y | R | B | H | S | C | traits |
|---|---|---|---|---|---|---|---|---|---|---|---|
| oldest | 126.3 | 8.15 | 0.585 | 6.3 | 0 | -0.63 | -0.68 | -0.05 | +0.13 | — | 4 |
| random | 97.0 | 8.73 | 0.551 | 7.6 | 0 | -0.49 | -0.11 | -0.27 | -0.06 | — | 5 |
| deep | 98.3 | 16.11 | 0.790 | 8.5 | 0 | -0.48 | -0.36 | -0.35 | +0.17 | — | 6 |
| Hbred | 106.2 | 11.74 | 0.817 | 6.3 | 0 | -0.60 | -0.40 | -0.25 | +0.17 | +0.07 | 8 |
| Hped | 104.1 | 15.30 | 0.860 | 8.6 | 0 | -0.46 | -0.27 | -0.38 | +0.14 | -0.16 | 7 |
| Cmarked | 97.7 | 4.66 | 0.714 | 9.6 | 0 | -0.38 | -0.03 | -0.02 | -0.01 | +0.22 | 3 |
| X | 132.0 | 11.63 | 0.466 | 5.9 | 6.0 | -0.67 | -0.73 | -0.14 | +0.09 | -0.17 | 6 |
| Bold_rc | 98.8 | 6.23 | 0.467 | 6.0 | 0 | -0.57 | -0.15 | -0.12 | -0.07 | -0.02 | 5 |
| Brand_rc | 93.2 | 7.07 | 0.553 | 7.5 | 0 | -0.48 | -0.09 | -0.03 | -0.02 | +0.12 | 3 |

C, unselected, sits -0.17 to +0.12 from the wild in one seed in the other arms.
**Method:** `node tools/batch.mjs tools/herders.json results/herders 1600 8 10` (56 runs, 10 workers). Per arm,
windows 401-500, 801-900, 1201-1300, 1501-1600:
- herd, lineage depth, depth-0 share, IBD, captures, exchanged, wild-sired share;
- every trait gap (R A S B H T M W L C), and the count of traits other than C with abs(gap) >= 0.10;
- per seed: herd / depth / R gap / B gap;
- WT: whole-population trait means at 201-300 and 1501-1600.
Scratchpad lin_tab.py, extended to C.
**Prediction** (years 1501-1600, 8 seeds; written before the checks and the smoke above, kept as written):
- **Homebred:**
  - Hped herd lineage depth at least 1.5 above Lrandom's (7.61) and at least 3 below Ldeep's (18.11): a herder's
    visible pedigree carries part of the deep oracle's isolation, not all.
  - Hbred (herdMemory 1) depth between Lrandom's and Hped's.
  - Hped R gap at least 0.05 wider than Lrandom's (-0.477).
- **Marked (neutral appearance):** herd C gap at least +0.20. Against Lrandom:
  - depth at least 1 above;
  - R gap at least 0.05 wider;
  - at least 2 traits other than C with abs(gap) >= 0.10.
- **Exchange (X, oldest sires, 2 adults per camp-year), against S0:**
  - R gap within 0.10 of S0's (-0.581);
  - depth within 2 of S0's (8.11);
  - herd IBD at least 0.05 below S0's (0.735).
- **Body size:**
  - Bold_rc (oldest, random cull, chosen sires spared) B gap at least 0.30 narrower than S0's (-0.601).
  - Brand_rc (random, random cull, chosen sires spared) B gap within 0.10 of Lrandom's (-0.044).
- **Wild Type I (WT, no humans):** every core trait's mean at 1501-1600 within 0.05 of its mean at 201-300.
- **Herd size:** over 70 in every herding arm.

## [RESULTS 2026-11-10] Herder-visible selection: homebred and marked sires, exchange, body-size checks, Wild Type I (raw)
**Run:** `node tools/batch.mjs tools/herders.json results/herders 1600 8 10` at a17303d; 56 of 56 done, no FAIL
(batch.log, ALL DONE 2026-11-10T20:51Z). Tables from scratchpad herd_tab.py (lin_tab.py extended to C and these
arms); means over 8 seeds. S0 is results/milksel S0; Lrandom and Ldeep are results/lineage. Trait counts leave out C.
**Years 1501-1600:**

| | herd | lineage depth | depth-0 share | IBD | captures/y | wild-sired | traits with abs(gap) >= 0.10 |
|---|---|---|---|---|---|---|---|
| S0 (oldest) | 116.3 | 8.11 | 0.084 | 0.735 | 7.19 | 0.008 | 3 |
| Lrandom | 98.2 | 7.61 | 0.116 | 0.740 | 8.41 | 0.011 | 1 |
| Ldeep | 99.9 | 18.11 | 0.087 | 0.912 | 6.75 | 0.009 | 6 |
| Hbred | 97.1 | 11.55 | 0.099 | 0.822 | 7.60 | 0.010 | 1 |
| Hped | 98.7 | 16.45 | 0.083 | 0.880 | 6.59 | 0.009 | 4 |
| Cmarked | 97.6 | 8.98 | 0.103 | 0.859 | 7.66 | 0.010 | 2 |
| X | 127.7 | 13.06 | 0.057 | 0.697 | 6.15 | 0.007 | 4 |
| Bold_rc | 94.1 | 6.30 | 0.117 | 0.610 | 7.28 | 0.011 | 1 |
| Brand_rc | 91.9 | 4.73 | 0.161 | 0.689 | 9.47 | 0.013 | 1 |

X exchanged 6 goats a year. Herd - wild gaps:

| | R | A | S | B | H | T | M | W | L | C |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 (oldest) | -0.581 | -0.033 | +0.053 | -0.601 | -0.042 | +0.054 | -0.130 | -0.010 | +0.007 | — |
| Lrandom | -0.477 | -0.000 | +0.016 | -0.044 | -0.018 | -0.014 | +0.019 | -0.007 | +0.009 | — |
| Ldeep | -0.569 | -0.105 | +0.183 | -0.121 | -0.212 | +0.045 | -0.078 | -0.103 | +0.025 | — |
| Hbred | -0.514 | -0.025 | +0.047 | -0.061 | -0.041 | +0.020 | -0.012 | +0.009 | +0.028 | +0.032 |
| Hped | -0.570 | -0.061 | +0.117 | -0.105 | -0.119 | +0.002 | -0.096 | -0.043 | +0.013 | +0.071 |
| Cmarked | -0.507 | -0.095 | +0.110 | -0.098 | -0.054 | +0.028 | -0.043 | -0.073 | -0.022 | +0.157 |
| X | -0.662 | -0.060 | +0.106 | -0.715 | -0.059 | +0.088 | -0.232 | -0.042 | -0.049 | -0.037 |
| Bold_rc | -0.499 | -0.009 | +0.047 | -0.023 | -0.024 | +0.025 | -0.005 | +0.018 | +0.022 | -0.026 |
| Brand_rc | -0.385 | -0.020 | +0.032 | -0.018 | -0.016 | +0.021 | -0.025 | +0.015 | +0.051 | -0.027 |

Per seed, herd / depth / R gap / B gap / C gap:
- Hbred: 98/13.0/-0.61/-0.00/+0.16, 97/11.4/-0.52/-0.04/+0.02, 101/8.9/-0.45/-0.08/-0.07, 90/12.2/-0.49/-0.06/+0.02,
  100/11.4/-0.52/-0.08/+0.02, 95/9.9/-0.52/+0.00/+0.13, 98/13.9/-0.48/-0.13/+0.00, 98/11.6/-0.53/-0.10/-0.02
- Hped: 99/16.7/-0.57/-0.16/+0.15, 98/17.1/-0.58/-0.19/-0.05, 94/17.4/-0.58/-0.07/+0.20, 100/18.5/-0.63/-0.12/+0.12,
  98/15.9/-0.62/-0.11/+0.13, 98/14.5/-0.53/+0.00/-0.01, 103/16.3/-0.53/-0.17/+0.02, 100/15.3/-0.51/-0.02/+0.02
- Cmarked: 104/12.4/-0.58/-0.23/+0.24, 97/10.9/-0.61/-0.05/+0.19, 98/6.7/-0.45/-0.05/+0.11, 92/7.7/-0.44/-0.02/+0.26,
  98/6.7/-0.47/-0.09/+0.07, 99/9.9/-0.49/-0.01/+0.12, 99/8.8/-0.53/-0.38/+0.18, 93/8.8/-0.50/+0.02/+0.09
- X: 117/11.3/-0.62/-0.68/+0.17, 123/14.1/-0.65/-0.71/-0.13, 133/15.6/-0.67/-0.75/-0.20, 128/14.8/-0.71/-0.73/+0.09,
  122/12.7/-0.65/-0.65/-0.12, 130/12.4/-0.67/-0.74/-0.06, 143/13.9/-0.69/-0.76/-0.12, 125/9.8/-0.64/-0.69/+0.07
- Bold_rc: 98/10.1/-0.59/-0.07/+0.01, 89/5.7/-0.48/+0.01/-0.14, 99/4.8/-0.46/-0.02/-0.03, 97/5.5/-0.45/-0.02/-0.07,
  96/5.5/-0.49/-0.01/-0.06, 97/7.1/-0.56/-0.05/+0.08, 91/6.2/-0.53/-0.01/-0.05, 85/5.5/-0.42/-0.01/+0.04
- Brand_rc: 92/3.2/-0.28/+0.00/+0.01, 86/4.8/-0.33/-0.01/-0.09, 95/4.8/-0.37/-0.03/+0.03, 90/4.2/-0.35/-0.04/-0.03,
  93/5.7/-0.47/-0.04/-0.03, 88/5.1/-0.44/-0.04/-0.04, 93/5.2/-0.39/-0.01/-0.03, 97/4.7/-0.45/+0.02/-0.01

**Earlier windows** (herd; depth; IBD; R, B, C gaps; traits with abs(gap) >= 0.10), Hbred / Hped / Cmarked / X /
Bold_rc / Brand_rc:
- 401-500: herd 68.7 / 67.6 / 66.1 / 65.2 / 44.7 / 43.5; depth 3.62 / 5.27 / 2.56 / 1.91 / 1.62 / 2.16; IBD 0.288 /
  0.346 / 0.292 / 0.132 / 0.123 / 0.164; R -0.101 / -0.105 / -0.094 / -0.079 / -0.065 / -0.060; B -0.015 / -0.014 /
  -0.021 / -0.021 / +0.000 / -0.014; C -0.005 / -0.010 / +0.149 / -0.004 / -0.000 / +0.015; traits 1 / 1 / 0 / 0 /
  0 / 0.
- 801-900: herd 99.0 / 98.2 / 99.2 / 110.7 / 90.4 / 85.0; depth 9.31 / 16.06 / 6.96 / 6.72 / 3.97 / 3.68; IBD 0.735 /
  0.842 / 0.827 / 0.598 / 0.445 / 0.492; R -0.436 / -0.545 / -0.466 / -0.543 / -0.357 / -0.282; B -0.054 / -0.070 /
  -0.100 / -0.490 / -0.019 / -0.023; C +0.012 / -0.017 / +0.099 / -0.052 / -0.023 / -0.003; traits 1 / 1 / 2 / 3 /
  1 / 1.
- 1201-1300: herd 97.9 / 101.2 / 96.5 / 125.4 / 94.5 / 88.0; depth 10.54 / 16.86 / 10.18 / 12.28 / 5.82 / 4.98; IBD
  0.792 / 0.890 / 0.855 / 0.667 / 0.577 / 0.628; R -0.493 / -0.577 / -0.546 / -0.662 / -0.498 / -0.354; B -0.074 /
  -0.110 / -0.115 / -0.716 / -0.017 / -0.038; C -0.036 / +0.007 / +0.155 / +0.011 / -0.021 / +0.016; traits 1 / 4 /
  3 / 4 / 1 / 1.

**Wild Type I** (WT, no humans; 8 seeds; never herded). Whole-population trait means:

| years | goats | R | A | S | B | H | T | M | W | L | C |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 201-300 | 522.5 | 0.639 | 0.771 | 0.403 | 0.856 | 0.742 | 0.229 | 0.568 | 0.574 | 0.393 | 0.511 |
| 401-500 | 533.4 | 0.632 | 0.830 | 0.329 | 0.886 | 0.809 | 0.178 | 0.639 | 0.625 | 0.424 | 0.531 |
| 801-900 | 549.3 | 0.621 | 0.849 | 0.209 | 0.894 | 0.844 | 0.160 | 0.650 | 0.679 | 0.504 | 0.544 |
| 1201-1300 | 559.3 | 0.610 | 0.850 | 0.152 | 0.896 | 0.848 | 0.165 | 0.651 | 0.736 | 0.534 | 0.531 |
| 1501-1600 | 559.2 | 0.612 | 0.849 | 0.132 | 0.897 | 0.859 | 0.163 | 0.677 | 0.743 | 0.548 | 0.534 |

Change 201-300 to 1501-1600: R -0.027, A +0.078, S -0.271, B +0.041, H +0.116, T -0.065, M +0.109, W +0.170,
L +0.155, C +0.023. Largest core change per seed: 0.224, 0.240, 0.306, 0.341, 0.178, 0.256, 0.353, 0.269.

**Prediction scoring:**
- Hped depth at least 1.5 above Lrandom's: met (16.45 vs 7.61). At least 3 below Ldeep's: not met (1.66 below 18.11).
- Hbred depth between Lrandom's and Hped's: met (11.55).
- Hped R gap at least 0.05 wider than Lrandom's: met (-0.570, 0.093 wider).
- Cmarked C gap at least +0.20: not met (+0.157; per seed +0.07 to +0.26, all positive). Depth at least 1 above
  Lrandom's: met (8.98, 1.37 above). R gap at least 0.05 wider: not met (-0.507, 0.030 wider). At least 2 traits other
  than C with abs(gap) >= 0.10: met (2: R, and S at +0.110).
- X R gap within 0.10 of S0's: met (-0.662, 0.081 wider). Depth within 2 of S0's: not met (13.06, 4.95 above). IBD at
  least 0.05 below S0's: not met (0.697, 0.038 below).
- Bold_rc B gap at least 0.30 narrower than S0's: met (-0.023, 0.578 narrower).
- Brand_rc B gap within 0.10 of Lrandom's: met (-0.018).
- WT every core trait within 0.05 between 201-300 and 1501-1600: not met (only R and B; S -0.271, W +0.170).
- Herd over 70 in every herding arm: met (lowest seed 85, Bold_rc).

## [PRE-REGISTERED 2026-11-10] Epoch pilot: run length and burn-in, to year 4000
**Question:** Chris (2026-11-10), on the paper suite: "i'm also not sure on the epoch you've selected. we might need
longer." Every batch so far stops at year 1600, 1200 years of herding. (1) Have the herd - wild gaps and their breadth
settled by then, or are they still moving? (2) Wild Type I (results/herders WT) showed the wild still changing under
wolves to 1600 (S -0.27, W +0.17 from 201-300). Does herding that starts on a later, more settled wild give the same
herd at the same time since herding began?
**Settings:** code of a1c6be8 (suite-measures merged: buckCull and doeCull, both off here; conception origins and
selection differentials recorded). tools/pilot.json: tools/milksel.json S0 (H5 + twins, milked at 0.5) as
- S0 (oldest sires);
- Lrandom (sireRule random);
- Hped (sireRule homebred, herdMemory 3);
- WT (humansAt 1e9);
- S0late (S0 with humansAt 1900, herdingAt 2000, ibdFrom 2000: the same 100 years of hunting before herding).
Checks for the suite-measures merge (seed 1, 520 years, herding from 400): S0, Ldeep and Lrandom settings equal the
a17303d check runs in every year once concOrigin, selSire, selDam and selN are set aside. Smoke (one seed, humans from
5, herding from 10, years 201-300): the reference equals the earlier oldest smoke (herd 126.3, depth 8.15, IBD 0.585,
R -0.63, B -0.68); every buckCull (random, calm, large, homebred, youngMales) and doeCull (random, calm, large,
homebred) rule runs clean. Herd conceptions by sire origin count only does already in the herd, so a doe captured
pregnant is not counted; the wild-sired share of herd births (0.005-0.03 in the smoke) counts her.
**Method:** `node tools/batch.mjs tools/pilot.json results/pilot 4000 4 10` (20 runs, 10 workers). Years 1-1600 of S0,
Lrandom and Hped seeds 1-4 should equal results/milksel S0, results/lineage Lrandom and results/herders Hped seeds 1-4
(checked, the new keys set aside). Per arm, means over 4 seeds, in the windows 1501-1600, 2001-2100, 2501-2600,
3001-3100, 3501-3600, 3901-4000; for S0late also by time since herding (its 2401-2500, 2801-2900, 3101-3200, 3901-4000
against S0's 801-900, 1201-1300, 1501-1600, 2301-2400):
- herd, lineage depth, IBD, captures, wild-sired share;
- every trait gap (R A S B H T M W L C), and the count of core traits with abs(gap) >= 0.10;
- sire and dam selection differentials per trait;
- WT and every arm: whole-population (wild) trait means.
**Prediction** (written before any pilot run):
- **WT:** at least one core trait mean moves by 0.05 or more between 1501-1600 and 3901-4000; every core trait is within
  0.05 between 2901-3000 and 3901-4000.
- **S0:** R and B gaps at 3901-4000 each within 0.05 of 1501-1600; lineage depth at least 2 higher.
- **Lrandom:** R gap at 3901-4000 at least 0.03 wider than at 1501-1600.
- **Hped:** traits with abs(gap) >= 0.10 at 3901-4000 at least as many as at 1501-1600.
- **S0late against S0 at equal time since herding** (S0late 3101-3200 against S0 1501-1600): R gap within 0.10, B gap
  within 0.15, herd within 15.
- **Herd size:** over 70 in every herding arm from the window 400-500 years after herding began.
**Decision rules** (for the paper suite, set now):
- **Run length:** for each herding arm, the first window end among 1600, 2100, 2600, 3100, 3600 after which every
  later window's R gap and B gap stay within 0.05 of the 3901-4000 value and the trait count within 1. The suite runs to
  the latest of these over the arms (1600 if all are met there).
- **Burn-in:** if S0late meets the three bounds above, herding stays at year 400. If not, the suite moves herding later,
  to a year after which WT's core traits stay within 0.05.

## [RESULTS 2026-11-10] Epoch pilot: run length and burn-in, to year 4000 (raw)
**Run:** `node tools/batch.mjs tools/pilot.json results/pilot 4000 4 10` at a1c6be8; 20 of 20 done, no FAIL
(batch.log, ALL DONE 2026-11-11T00:33Z). Tables from scratchpad pilot_tab.py; means over 4 seeds. Trait counts are
core traits (R A S B H T M W L, not C) with abs(gap) >= 0.10. herd_tab.py (the herders entry above) counted R to W
only, leaving L out; rerun with L included, every count it printed is unchanged.
**Check:** years 1-1600 of S0, Lrandom and Hped seeds 1-4 equal results/milksel S0, results/lineage Lrandom and
results/herders Hped seeds 1-4 in every year (12 of 12 runs, 0 differing years) once the keys added since are set
aside (concOrigin, selSire, selDam, selN, exchanged, and C in the trait means). The same comparison on a mismatched
pair (milksel S0 seed 1 against pilot Lrandom seed 1) differs in 1199 years, from year 402.
**Windows:**

| arm | years | herd | depth | IBD | capt/y | wild-sired | R | A | S | B | H | T | M | W | L | C | traits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 1501-1600 | 114.9 | 7.77 | 0.721 | 7.21 | 0.007 | -0.570 | +0.001 | +0.028 | -0.575 | -0.023 | +0.050 | -0.070 | -0.019 | +0.012 | +0.013 | 2 |
| S0 | 2001-2100 | 121.8 | 8.72 | 0.788 | 7.83 | 0.010 | -0.575 | -0.008 | +0.040 | -0.634 | -0.037 | +0.043 | -0.066 | -0.005 | -0.006 | +0.001 | 2 |
| S0 | 2501-2600 | 120.9 | 10.68 | 0.838 | 7.06 | 0.008 | -0.600 | -0.027 | +0.035 | -0.672 | -0.033 | +0.047 | -0.114 | -0.032 | +0.048 | -0.038 | 3 |
| S0 | 3001-3100 | 115.7 | 10.09 | 0.821 | 7.18 | 0.009 | -0.580 | -0.059 | +0.030 | -0.587 | -0.072 | +0.056 | -0.031 | -0.068 | -0.002 | -0.026 | 2 |
| S0 | 3501-3600 | 118.4 | 10.24 | 0.858 | 6.53 | 0.008 | -0.615 | -0.029 | +0.018 | -0.609 | -0.033 | +0.063 | -0.080 | -0.021 | -0.065 | -0.038 | 2 |
| S0 | 3901-4000 | 117.1 | 8.67 | 0.855 | 8.16 | 0.009 | -0.557 | -0.044 | +0.032 | -0.588 | -0.068 | -0.009 | -0.147 | -0.088 | +0.002 | -0.037 | 3 |
| Lrandom | 1501-1600 | 100.1 | 7.11 | 0.740 | 9.30 | 0.011 | -0.433 | +0.004 | -0.002 | -0.039 | -0.011 | -0.035 | +0.000 | -0.015 | -0.008 | +0.047 | 1 |
| Lrandom | 2001-2100 | 97.2 | 4.85 | 0.764 | 10.81 | 0.013 | -0.365 | -0.023 | +0.016 | -0.042 | -0.028 | +0.004 | -0.021 | +0.010 | +0.054 | -0.001 | 1 |
| Lrandom | 2501-2600 | 98.1 | 7.15 | 0.818 | 8.19 | 0.010 | -0.492 | -0.041 | +0.032 | -0.039 | -0.012 | +0.031 | -0.031 | +0.054 | +0.094 | +0.029 | 1 |
| Lrandom | 3001-3100 | 99.1 | 6.78 | 0.850 | 9.11 | 0.012 | -0.461 | -0.052 | +0.039 | -0.020 | -0.021 | -0.028 | -0.055 | +0.007 | +0.039 | -0.015 | 1 |
| Lrandom | 3501-3600 | 98.7 | 6.41 | 0.885 | 8.85 | 0.010 | -0.462 | -0.021 | +0.060 | -0.043 | -0.002 | -0.011 | -0.034 | -0.008 | +0.038 | -0.002 | 1 |
| Lrandom | 3901-4000 | 97.3 | 5.83 | 0.891 | 8.99 | 0.011 | -0.446 | -0.036 | +0.038 | -0.038 | +0.029 | +0.024 | -0.026 | -0.052 | +0.011 | -0.024 | 1 |
| Hped | 1501-1600 | 97.9 | 17.41 | 0.877 | 6.51 | 0.009 | -0.590 | -0.088 | +0.093 | -0.134 | -0.097 | -0.010 | -0.123 | +0.011 | +0.025 | +0.104 | 3 |
| Hped | 2001-2100 | 101.7 | 17.83 | 0.918 | 6.25 | 0.009 | -0.593 | -0.017 | +0.135 | -0.120 | -0.073 | -0.021 | -0.177 | -0.046 | +0.046 | +0.052 | 4 |
| Hped | 2501-2600 | 97.4 | 18.24 | 0.923 | 6.14 | 0.010 | -0.618 | -0.022 | +0.097 | -0.117 | -0.033 | +0.038 | -0.091 | -0.021 | +0.053 | -0.006 | 2 |
| Hped | 3001-3100 | 96.8 | 16.01 | 0.915 | 6.92 | 0.009 | -0.557 | -0.084 | +0.076 | -0.107 | -0.081 | +0.059 | -0.108 | +0.010 | +0.049 | +0.102 | 3 |
| Hped | 3501-3600 | 98.4 | 15.98 | 0.935 | 6.60 | 0.008 | -0.562 | -0.158 | +0.118 | -0.119 | +0.030 | +0.039 | -0.125 | +0.044 | -0.043 | -0.009 | 5 |
| Hped | 3901-4000 | 96.6 | 17.32 | 0.950 | 6.81 | 0.009 | -0.568 | -0.091 | +0.113 | -0.150 | -0.040 | +0.034 | -0.106 | -0.016 | +0.013 | -0.022 | 4 |
| S0late | 2001-2100 | 69.3 | 2.07 | 0.169 | 11.94 | 0.026 | -0.079 | -0.002 | +0.014 | -0.018 | -0.007 | +0.015 | +0.004 | -0.018 | +0.009 | -0.007 | 0 |
| S0late | 2501-2600 | 109.5 | 4.44 | 0.556 | 10.89 | 0.012 | -0.420 | +0.013 | +0.004 | -0.394 | -0.039 | +0.050 | -0.066 | -0.003 | +0.048 | +0.013 | 2 |
| S0late | 3001-3100 | 112.6 | 10.66 | 0.704 | 6.67 | 0.010 | -0.598 | -0.038 | +0.020 | -0.595 | -0.053 | +0.107 | -0.043 | +0.022 | -0.023 | -0.025 | 3 |
| S0late | 3501-3600 | 116.3 | 9.26 | 0.753 | 7.41 | 0.009 | -0.569 | -0.047 | +0.054 | -0.589 | +0.005 | +0.075 | -0.081 | +0.036 | -0.021 | +0.071 | 2 |
| S0late | 3901-4000 | 115.3 | 10.25 | 0.788 | 6.81 | 0.009 | -0.597 | -0.057 | +0.054 | -0.611 | -0.066 | +0.057 | -0.126 | +0.023 | -0.119 | +0.080 | 4 |

Standard error over the 4 seeds of each window's R gap: 0.010-0.060 (S0 0.018-0.030, Lrandom 0.019-0.055, Hped
0.010-0.060, S0late 0.015-0.027); of the B gap: 0.004-0.070 (S0 0.025-0.053, Lrandom 0.011-0.017, Hped 0.015-0.050,
S0late 0.004-0.070).
Per seed at 3901-4000, herd / depth / R gap / B gap:
- S0: 119/10.2/-0.62/-0.57, 124/8.4/-0.55/-0.66, 109/5.5/-0.48/-0.56, 116/10.6/-0.59/-0.56
- Lrandom: 96/7.2/-0.52/-0.05, 100/5.9/-0.42/-0.06, 96/4.5/-0.35/-0.04, 97/5.7/-0.51/-0.01
- Hped: 98/19.0/-0.63/-0.20, 103/17.3/-0.56/-0.23, 95/13.9/-0.40/-0.13, 91/19.1/-0.67/-0.04
- S0late: 109/10.3/-0.64/-0.60, 117/10.2/-0.59/-0.65, 124/12.4/-0.60/-0.67, 112/8.1/-0.56/-0.53

**Selection differentials** (window means of the yearly sire and dam differentials), R and B; every other trait is
within +-0.012 in every arm and window:
- S0 sire R -0.011/-0.003/-0.008/-0.006/-0.015/-0.007, B -0.006/-0.011/-0.021/-0.012/-0.019/-0.015; dam R +0.002 to
  +0.006, B +0.011/+0.014/+0.015/+0.015/+0.015/+0.016.
- Lrandom sire R +0.003 to -0.012, B -0.000 to +0.013; dam R and B within +-0.004.
- Hped sire R -0.038/-0.026/-0.041/-0.033/-0.032/-0.035, B within +-0.005; dam R and B within +-0.002.
- S0late (2001-2100 to 3901-4000) sire R +0.002/-0.001/-0.014/-0.006/-0.008, B -0.001/-0.011/-0.022/-0.015/-0.006;
  dam B -0.002/+0.006/+0.011/+0.013/+0.017.

**S0late against S0 at equal time since herding** (S0late window | S0 window):

| years since herding | S0late herd / depth / IBD | S0 herd / depth / IBD | S0late R / B | S0 R / B | traits |
|---|---|---|---|---|---|
| 401-500 | 99.6 / 3.95 / 0.515 | 101.5 / 4.95 / 0.599 | -0.399 / -0.305 | -0.466 / -0.337 | 2 / 2 |
| 801-900 | 109.6 / 8.70 / 0.650 | 119.1 / 8.05 / 0.723 | -0.567 / -0.555 | -0.551 / -0.609 | 2 / 3 |
| 1101-1200 | 116.6 / 10.14 / 0.706 | 114.9 / 7.77 / 0.721 | -0.598 / -0.584 | -0.570 / -0.575 | 2 / 2 |
| 1901-2000 | 115.3 / 10.25 / 0.788 | 121.0 / 9.11 / 0.796 | -0.597 / -0.611 | -0.597 / -0.635 | 4 / 2 |

**Whole-population trait means** (WT never herded; 4 seeds):

| WT years | goats | R | A | S | B | H | T | M | W | L | C |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 201-300 | 513.2 | 0.634 | 0.775 | 0.408 | 0.861 | 0.731 | 0.237 | 0.584 | 0.566 | 0.397 | 0.524 |
| 1501-1600 | 544.7 | 0.613 | 0.853 | 0.131 | 0.904 | 0.860 | 0.168 | 0.641 | 0.732 | 0.505 | 0.579 |
| 1901-2000 | 549.2 | 0.612 | 0.861 | 0.116 | 0.894 | 0.858 | 0.177 | 0.691 | 0.773 | 0.447 | 0.572 |
| 2501-2600 | 554.5 | 0.612 | 0.861 | 0.110 | 0.890 | 0.833 | 0.167 | 0.705 | 0.801 | 0.512 | 0.567 |
| 2901-3000 | 560.3 | 0.609 | 0.856 | 0.104 | 0.890 | 0.851 | 0.178 | 0.682 | 0.786 | 0.521 | 0.600 |
| 3501-3600 | 559.0 | 0.607 | 0.853 | 0.106 | 0.888 | 0.851 | 0.187 | 0.703 | 0.790 | 0.541 | 0.641 |
| 3901-4000 | 549.6 | 0.599 | 0.860 | 0.134 | 0.893 | 0.849 | 0.181 | 0.687 | 0.774 | 0.554 | 0.629 |

WT change 1501-1600 to 3901-4000: R -0.014, A +0.006, S +0.003, B -0.011, H -0.011, T +0.013, M +0.045, W +0.042,
L +0.049, C +0.051. 2901-3000 to 3901-4000: R -0.010, A +0.003, S +0.030, B +0.003, H -0.002, T +0.003, M +0.005,
W -0.012, L +0.034, C +0.029. WT and S0late year records are equal in every year to 1900 except wildF (the wild inbreeding
measure), in all 4 seeds; S0late's humans arrive at 1900. WT never herded a goat. Whole population at 3901-4000 in the herding arms: S0 R 0.680, B 0.736; Lrandom R 0.715, B 0.861; Hped R 0.709,
B 0.853; S0late R 0.679, B 0.741.
**Herd size**, from the window 400-500 years after herding began (801-900; S0late 2401-2500) to 4000: lowest
seed-window mean S0 97.8, Lrandom 91.7, Hped 89.5, S0late 96.6; lowest single year 35, 44, 32, 31.

**Prediction scoring:**
- WT, at least one core trait moves by 0.05 or more between 1501-1600 and 3901-4000: not met (largest L +0.049, M
  +0.045; C +0.051 is not core). Every core trait within 0.05 between 2901-3000 and 3901-4000: met (largest L +0.034).
- S0, R and B gaps at 3901-4000 within 0.05 of 1501-1600: met (R 0.013, B 0.013). Depth at least 2 higher: not met
  (+0.90).
- Lrandom, R gap at least 0.03 wider at 3901-4000: not met (0.013 wider).
- Hped, trait count at 3901-4000 not lower than at 1501-1600: met (4 against 3).
- S0late 3101-3200 against S0 1501-1600: R within 0.10, met (0.028); B within 0.15, met (0.009); herd within 15, met
  (1.7).
- Herd over 70 in every herding arm from 400-500 years after herding: met on window means (lowest seed 89.5); single
  years fall to 31-44.

**Decision rules, applied as written:**
- **Run length.** Windows meeting the rule (R and B gaps within 0.05 of 3901-4000, trait count within 1), at window
  ends 1600 / 2100 / 2600 / 3100 / 3600:
  - S0: yes / yes / no (B 0.084) / yes / no (R 0.058). No window end qualifies.
  - Lrandom: yes / no (R 0.081) / yes / yes / yes. First qualifying end 2600.
  - Hped: yes / yes / no (trait count 2 against 4) / yes / yes. First qualifying end 3100.
  The rule's suite length is the latest over the arms. S0 has no qualifying window end at or before 3600, so the rule
  as written sets no length within the pilot.
- **Burn-in.** S0late meets all three bounds, so herding stays at year 400.

## [PRE-REGISTERED 2026-11-10] Corner pilot: run length across the suite, to year 4000
**Question:** Chris (2026-11-10), on the epoch pilot: "did we run 1600 on just the anchor? what if other run types need
longer to settle?" The epoch pilot (entry above) varied only the sire rule, and every arm had the reference culture's
husbandry. A scan of every existing arm with at least 1100 years of herding (scratchpad settle_scan.py: the last 100
years against 301-400 years before the end, means over seeds) found the B gap still widening at 1600 in results/ablate
Lguard (guarding off, -0.148), results/milk3 M25 (milking at 0.25, -0.114; R -0.077) and milk3 M0 (unmilked, -0.056).
Brand_rc's R gap moved -0.032. milksel S0 moved B -0.007 and R -0.029. ablate ran older code; milk3 M50 equals milksel
S0, so milk3 ran the current model up to the keys added since. Which corners of the suite settle latest, and how long
must the suite run?
**Settings:** code of the commit registering this entry (277f411, R3 switches merged, plus tools/batch.mjs, which now runs each worker under `cpuslot run --tag
animal-domestication`, checked: a 3-year run through the wrapper equals the same run made directly). tools/corners.json:
the reference culture (tools/pilot.json S0: milksel S0, oldest sires, opportunity cull, milked at 0.5, herding from 400)
with these changes:
- husbandry corners: noGuard (guarding 0), noMilk (milkIntensity 0), noPen (penning 0), noBuck (buckManagement 0),
  noTether (tetherNew 0), noShelter (kidShelter 0), randCull (cullRule random);
- combinations: noGuardMilk (guarding 0, milkIntensity 0), noBuckRandCull (buckManagement 0, cullRule random);
- rules block: bCullRand (buckCull random), dCullLarge (doeCull large);
- lineage test: Ldeep (sireRule deep);
- R3: R3aRandom (sireRule random, wildSireBlock 1).
Provisioning off and exchange on are left out: provisioning off lost the herd in results/ablate Lprov (herd 24), and
exchange (results/herders X) moved R and B less than 0.003 over its last 300 years.
**Method:** `node tools/batch.mjs tools/corners.json results/corners 4000 4 10` (52 runs, 10 slots). The epoch pilot's
S0, Lrandom and Hped (results/pilot) are scored by the same rule. Per arm, per seed: 200-year window means of every
core gap (R A S B H T M W L) ending at E = 1600, 2000, 2400, 2800, 3200, and the long-run mean over 3201-4000. Bias at E
for a trait is the mean over seeds of (window ending at E minus long-run mean); its SE is over the 4 seeds. Also per
window: herd, lineage depth, IBD, captures, wild-sired share, breadth (core traits with abs(gap) >= 0.10), conceptions
by sire origin, selection differentials.
**Prediction** (written before any corner run):
- noGuard and noMilk are not settled at 1600: the B bias at 1600 is beyond 0.05.
- noGuardMilk settles no earlier than either of noGuard and noMilk.
- noBuckRandCull is not settled at 1600 on R.
- Ldeep breadth at 3801-4000 is at least its breadth at 1401-1600.
- dCullLarge B gap at 1401-1600 is between -0.05 and -0.30.
- R3aRandom R gap at 1401-1600 is within 0.05 of the pilot Lrandom's over the same years.
- The suite length the rule gives is 2400.
**Decision rule** (for the paper suite, set now; replaces the epoch pilot's run-length rule, which set no length because
its 0.05 tolerance on single 100-year windows was within 4-seed noise):
- An arm is settled at E if abs(bias) <= 0.05 for every core trait at E and at every later candidate end.
- An arm whose herd averages under 30 goats over 3201-4000 is reported and does not set the length.
- The suite runs to the latest settled E over the corner arms and the epoch pilot's S0, Lrandom and Hped. If an arm is
  not settled at 3200, the suite runs to 4000 and the arm is reported as unsettled.

## [PRE-REGISTERED 2026-11-10] Corner pilot addendum: R3 (b) and (c) under random sires, to year 4000
**Question:** completes R3 in the corner pilot (entry above), and is the first batch queued past the cpuslot level
(Chris, 2026-11-10: "can you queue all the runs you want to do on the new CPU coordinator to see if the queue is
working? (maybe just do the next 6)"). With the corner pilot holding 10 of 12 slots, 2 of these 6 start and 4 queue.
Does the herd persist and stay divergent when captures stop after founding, with and without wild sires?
**Settings:** code of 6ae7bb4. tools/corners_r3.json: the reference culture with sireRule random and captureUntil 800
(R3bRandom), and the same plus wildSireBlock 1 (R3cRandom). Year 800 is 400 years after herding began, when the
reference herds have reached about 100 goats (results/milksel S0 801-900).
**Method:** `node tools/batch.mjs tools/corners_r3.json results/corners_r3 4000 3 6` (6 runs, up to 6 slots, queued by
cpuslot). Measures and settle rule as in the corner pilot. Queue check: `cpuslot status` right after launch shows these
runs waiting, and each starts as a slot frees.
**Prediction:**
- Both arms keep a herd: over 70 goats in 1401-1600.
- R gap in 1401-1600 at least as wide as the pilot Lrandom's (-0.433 in 1501-1600) minus 0.05 tolerance, in both arms.
- Captures over 801-4000 are 0 in both arms.
- Settle rule: both arms settled by 2400.

## [RESULTS 2026-11-10] Corner pilot addendum: R3 (b) and (c) under random sires, to year 4000 (raw)
**Run:** `node tools/batch.mjs tools/corners_r3.json results/corners_r3 4000 3 6` at 4a9887a (code of 6ae7bb4); 6 of
6 done, no FAIL (batch.log, ALL DONE 2026-11-11T03:45Z), 7978-8695 s each with 16 runs sharing the machine. Compared
with the epoch pilot's Lrandom seeds 1-3 (results/pilot), which is the same culture with captures open. Means over 3
seeds; core traits R A S B H T M W L.

| arm | years | herd | R | A | S | B | H | W | L | traits |
|---|---|---|---|---|---|---|---|---|---|---|
| R3bRandom | 701-800 | 97.3 | -0.307 | -0.018 | +0.020 | -0.027 | +0.012 | -0.028 | +0.021 | 1 |
| R3bRandom | 801-900 | 97.0 | -0.457 | -0.077 | +0.014 | -0.076 | -0.019 | +0.064 | +0.017 | 1 |
| R3bRandom | 1401-1600 | 61.4 | -0.587 | -0.091 | +0.085 | -0.163 | -0.167 | +0.014 | -0.009 | 3 |
| R3bRandom | 2201-2400 | 46.6 | -0.608 | -0.101 | +0.058 | -0.355 | -0.336 | +0.062 | -0.099 | 4 |
| R3bRandom | 3201-4000 | 9.5 | | | | | | | | |
| R3cRandom | 701-800 | 100.3 | -0.326 | +0.008 | +0.021 | -0.021 | -0.021 | +0.047 | +0.023 | 1 |
| R3cRandom | 801-900 | 91.4 | -0.429 | -0.031 | +0.072 | -0.038 | -0.003 | -0.029 | +0.067 | 1 |
| R3cRandom | 1401-1600 | 43.1 | -0.588 | -0.151 | +0.195 | -0.133 | -0.197 | -0.143 | +0.174 | 7 |
| R3cRandom | 2201-2400 | 8.8 | | | | | | | | |
| Lrandom | 801-900 | 101.6 | -0.356 | -0.050 | -0.010 | -0.069 | +0.004 | -0.007 | +0.031 | 1 |
| Lrandom | 1401-1600 | 99.7 | -0.421 | +0.005 | +0.005 | -0.045 | -0.025 | -0.046 | -0.021 | 1 |
| Lrandom | 2201-2400 | 97.6 | -0.428 | -0.030 | +0.036 | -0.031 | -0.014 | +0.006 | -0.000 | 1 |
| Lrandom | 3201-4000 | 97.5 | -0.421 | -0.020 | +0.029 | -0.036 | -0.010 | -0.006 | +0.022 | 1 |

T and M gaps within +-0.10 throughout (R3cRandom 1401-1600 M +0.049). Gaps after the herd falls below about 10 are
left blank (no herd in some seeds). Years 1-800 of R3bRandom equal Lrandom's (701-800 identical).
- Herd lost in every seed: last year with a herd R3bRandom 2719, 2553, 3911; R3cRandom 2383, 2173, 1947. Herd at years
  1000 / 1200 / 1600: R3b 75/118/93, 124/60/32, 105/106/52; R3c 26/36/37, 127/86/35, 119/22/41. Lrandom's lowest
  yearly herd over 801-4000: 53, 47, 44.
- Captures over 801-4000: 0 in every R3 seed. Over 701-800: R3b 1190, 935, 1621 (equal to Lrandom's); R3c 1218, 1335,
  1242. Lrandom over 801-4000: 32265, 29936, 32455 (seed 1 at 1401-1600: 9.6 a year, herd 99.3).
- Wild-sired herd conceptions over 801-4000: R3b 33, 6, 56; R3c 0, 0, 0; Lrandom 98, 113, 135. Wild-sired share of
  herd births 1401-1600: R3b 0.0025, R3c 0, Lrandom 0.0106.
**Prediction scoring:**
- Both arms keep a herd over 70 in 1401-1600: not met (R3b 61.4, R3c 43.1; every herd is later lost).
- R gap in 1401-1600 at -0.383 or wider in both arms: met (R3b -0.587, R3c -0.588).
- Captures over 801-4000 are 0: met.
- Both arms settled by 2400: not met (no herd persists to 3201-4000).

## [PRE-REGISTERED 2026-11-10] Starvation probe: why herd goats starve
**Question:** Chris (2026-11-10): "starvation means that goats are not being fed during the lean season because the
herders don't have enough fodder?" In the epoch pilot (1401-1600) herd goats die of starvation at about 17 a year in a
herd of about 100-113, the largest cause after none of culling (10.9-12.4) and ahead of background mortality (11-12).
Provisioning (C61) gives herd goats up to provision × size^0.75 kcal a day from the camp store in the lean season (all
year if kept at camp); provision 2160 equals maintBase, so the ration covers maintenance only.
**Settings:** code of the commit registering this entry; tools/starveprobe.mjs (new). Reference culture
(tools/pilot.json S0), seed 1, years 450-600.
**Method:** `cpuslot run --tag animal-domestication -- node tools/starveprobe.mjs 600 450 1 <S0 settings>`. Each herd
starvation death classified: kid (born in the herd, unweaned) or weaned; lean (growth 0) or growing season; kept at camp
or out; camp store (slop + fodder) below the goat's ration that day or not. Per herding camp, share of lean days with the
store under 1 kcal.
**Prediction:** at least 70% of herd starvation deaths are weaned goats; at least 70% fall in the lean season; at least
half of the lean-season ones die on a day the camp store is short of their ration.

## [PRE-REGISTERED 2026-11-10] Lean-tissue buffer: what changes when a goat can run short before it starves
**Question:** Chris (2026-11-10): goats should not starve from missing a few days' feed ("goats don't starve after
missing 1.7% of their meals right?"), and herds may simply grow to whatever the fodder supports and starve at the
margin ("harvesting more fodder will increase capacity, but then goats will simply grow to that new one and starve").
Until now a goat died the first day its reserve went below zero. The starvation probe (entry above, years 450-600)
found every herd starvation death was a weaned goat, half in the lean season on a day the camp store ran short of its
ration and half in the growing season while foraging. With a lean-tissue buffer (leanBuffer, MODEL.md C24), how do herd
size, the herd's yearly budget, the gaps, the wild population and the closed herd of R3 (b) change?
**Settings:** code of the commit registering this entry (leanBuffer added, default 0, checked identical to the
previous code over 520 years). leanBuffer 12000 (death at about 70% of lean body weight for a 50 kg goat; Turner et al.
1993). Arms, the reference culture (tools/pilot.json S0) with leanBuffer 12000:
- S0on: oldest sires, 1600 years, seeds 1-4;
- Lrandomon: sireRule random, 1600 years, seeds 1-4;
- WTon: humansAt 1e9 (no humans), 1600 years, seeds 1-4;
- R3bon: sireRule random, captureUntil 800, 4000 years, seeds 1-4.
Each is compared with the same arm without the buffer and the same seeds: results/pilot S0, Lrandom and WT (years
1-1600 of the 4000-year runs) and results/corners_r3 R3bRandom (seeds 1-3).
**Method:** `cpuslot submit --tag animal-domestication --list tools/lean.jsonl` (16 runs). Per arm, means over seeds, in
windows 801-900, 1201-1300 and 1401-1600 (R3bon also 2201-2400 and 3201-4000): herd; the herd's yearly budget (births,
captures, culled, deaths by cause, ran off); herd starvation deaths per herd goat-year; every core gap (R A S B H T M W
L) and the count with abs(gap) >= 0.10; lineage depth; IBD; wild goats and wild starvation deaths per goat-year;
whole-population trait means (WTon). R3bon: the last year with a herd, per seed.
Seen before registering: one 300-year smoke (seed 1, humans from 5, herding from 10, leanBuffer 12000) against
the reference smoke, years 201-300: herd 101.9 against 126.3, herd starvation 14.7 against 17.5 a year. The predictions
below were written before that smoke and are left as written.
**Prediction:**
- S0on and Lrandomon: herd at 1401-1600 at least 10 above the same arm without the buffer.
- S0on and Lrandomon: herd starvation deaths per herd goat-year at 1401-1600 fall, but by less than half (the herd grows
  into the slack).
- S0on: R and B gaps at 1401-1600 within 0.10 of S0 without the buffer.
- WTon: wild goats at 1401-1600 at least 5% more than WT without the buffer.
- R3bon: the herd persists to year 4000 in at least 2 of 4 seeds.

## [RESULTS 2026-11-10] Starvation probe: why herd goats starve (raw)
**Run:** `cpuslot run --tag animal-domestication -- node tools/starveprobe.mjs 600 450 1 <S0 settings>` at 8736c06, as
registered. A second window, years 1200-1300 (`starveprobe.mjs 1300 1200 1`, same settings, code 27fd050, src unchanged),
was added after the first result, because starvation in the epoch pilot's S0 seed 1 rises from 5.0 a year at 451-600 to
17.2-18.0 from 801-900 on. Both windows agree with the pilot's own records for the same seed and years: 451-600 herd
deaths 30.4 and starvation 5.0 a year; 1201-1300 starvation 17.3 a year.

| | years 450-600 | years 1200-1300 |
|---|---|---|
| mean herd | 107.5 | 138.8 |
| herd deaths a year | 30.4 | 46.9 |
| herd starvation a year (per goat-year) | 5.0 (0.047) | 17.3 (0.125) |
| starvation deaths | 752 | 1734 |
| weaned | 752 (1.000) | 1727 (0.996) |
| kid (born in the herd, unweaned) | 0 | 7 (0.004) |
| growing season | 379 (0.504) | 1191 (0.687) |
| of which out, store held | 375 | 1176 |
| lean season | 373 (0.496) | 543 (0.313) |
| of which out, store short of the ration | 371 | 527 |
| of which out, store held | 0 | 14 |
| kept at camp | 3 | 2 |
| lean camp-days with a herd; store empty | 97650; 1681 (0.017) | 65100; 2391 (0.037) |

The store is read after the dying goat's own draw that day.
**Prediction scoring:**
- At least 70% of herd starvation deaths are weaned goats: met (1.000; 0.996).
- At least 70% fall in the lean season: not met (0.496; 0.313).
- At least half of the lean-season ones die on a day the camp store is short of their ration: met (371 of 373; 527 of
  543).

## [PRE-REGISTERED 2026-11-10] Herder range: does reaching further pasture relieve herd starvation?
**Question:** Chris (2026-11-10): "what if we extend herder range?" The starvation probe (entry above) found that by
years 1200-1300, 69% of herd starvation deaths fall in the growing season, among goats out grazing with the camp store
full, in a herd of about 139 kept within herdRange 4 cells of camp. MODEL.md G12 (2026-10-22, H4, older code, 2 seeds):
widening the range to 8 shrank penned herds to 8-10 and raised starvation 0.07 -> 0.11 per goat-year, because a penned
herd must walk home by dusk (daySteps 6, duskSteps 4) and spends the day walking. Does a wider range help the reference
culture, with or without the lean-tissue buffer?
**Settings:** code of the commit registering this entry (c6261e9 + this entry; src unchanged since 8e729ff).
tools/herdrange.jsonl: the reference culture (tools/pilot.json S0) with herdRange 6 or 8, leanBuffer 0 or 12000, seeds
1-4, 1000 years (16 runs). Range 4 comparisons: results/pilot S0 seeds 1-4 (leanBuffer 0, years 1-1000) and
results/lean S0on seeds 1-4 (leanBuffer 12000, years 1-1000).
**Method:** `cpuslot submit --tag animal-domestication --out results/herdrange/logs --list tools/herdrange.jsonl`. Per
arm, means over seeds in 801-1000: herd; herd starvation deaths per herd goat-year; the herd's yearly budget (births,
captures, culled, deaths by cause, ran off); R and B gaps; lineage depth.
**Prediction:**
- herdRange 8: herd at 801-1000 at least 10 below range 4, with and without the buffer.
- herdRange 8: herd starvation per goat-year higher than at range 4, with and without the buffer.
- herdRange 6: herd at 801-1000 no more than 10 below range 4, with and without the buffer.

## [RESULTS 2026-11-11] Lean-tissue buffer: what changes when a goat can run short before it starves (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/lean/logs --list tools/lean.jsonl` at c6261e9 (src of
ee1dd8f); 16 of 16 exit 0, last finished 2026-11-11T00:08 local. 1600-year runs 1203-3969 s, R3bon 8751-11138 s, sharing
the machine. Off arms: results/pilot S0, Lrandom, WT seeds 1-4 and results/corners_r3 R3bRandom seeds 1-3. Means over
seeds. Herd budget per year: herd births, captures, culled, non-cull herd deaths (starvation, other), herd goats lost
after running off (runOffLost). "Wild" is all goats minus herded. Tabulated by scratchpad lean_tab.py; its off-arm S0
1401-1600 budget reproduces the epoch pilot's (113.5, 48.7, 7.6, 12.4, 30.6, 16.3, 11.4, 11.4).

| arm | years | herd | births | capt | culled | non-cull (starv, other) | lost | starv / herd goat-yr | wild | R | B | traits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0on | 801-900 | 105.2 | 52.0 | 11.7 | 11.6 | 29.2 (14.6, 12.3) | 19.7 | 0.139 | 500.7 | -0.401 | -0.346 | 2 |
| S0 | 801-900 | 101.5 | 50.3 | 8.8 | 11.2 | 30.5 (16.2, 12.1) | 14.7 | 0.159 | 442.9 | -0.466 | -0.337 | 2 |
| S0on | 1201-1300 | 112.2 | 49.0 | 8.8 | 12.2 | 30.8 (16.2, 11.6) | 13.1 | 0.148 | 500.5 | -0.529 | -0.582 | 3 |
| S0 | 1201-1300 | 119.1 | 49.8 | 8.0 | 12.9 | 30.7 (16.4, 11.4) | 12.5 | 0.139 | 454.9 | -0.551 | -0.609 | 3 |
| S0on | 1401-1600 | 112.9 | 49.7 | 8.6 | 12.3 | 32.0 (17.0, 12.0) | 12.1 | 0.151 | 501.7 | -0.541 | -0.573 | 2 |
| S0 | 1401-1600 | 113.5 | 48.7 | 7.6 | 12.4 | 30.6 (16.3, 11.4) | 11.4 | 0.143 | 453.8 | -0.555 | -0.561 | 2 |
| Lrandomon | 801-900 | 97.2 | 53.8 | 10.7 | 10.8 | 33.4 (19.0, 12.9) | 16.9 | 0.195 | 490.5 | -0.404 | -0.024 | 1 |
| Lrandom | 801-900 | 101.3 | 52.6 | 10.8 | 11.1 | 30.7 (16.8, 12.4) | 18.4 | 0.166 | 433.1 | -0.373 | -0.065 | 1 |
| Lrandomon | 1201-1300 | 99.9 | 54.8 | 11.7 | 11.1 | 32.5 (17.6, 13.2) | 19.2 | 0.176 | 506.4 | -0.380 | -0.042 | 1 |
| Lrandom | 1201-1300 | 98.7 | 51.3 | 9.8 | 10.9 | 30.8 (17.4, 11.9) | 16.6 | 0.177 | 446.4 | -0.412 | -0.043 | 1 |
| Lrandomon | 1401-1600 | 101.2 | 56.3 | 10.3 | 11.3 | 36.8 (21.2, 13.8) | 15.6 | 0.209 | 503.8 | -0.437 | -0.013 | 1 |
| Lrandom | 1401-1600 | 99.6 | 50.7 | 9.5 | 10.9 | 31.1 (17.6, 11.9) | 15.6 | 0.177 | 446.3 | -0.422 | -0.034 | 1 |
| R3bon | 801-900 | 95.3 | 55.1 | 0 | 10.7 | 35.1 (19.9, 13.6) | 7.8 | 0.211 | 495.2 | -0.533 | -0.031 | 1 |
| R3b (n3) | 801-900 | 97.0 | 51.0 | 0 | 10.6 | 28.8 (15.7, 11.6) | 9.8 | 0.161 | 446.6 | -0.457 | -0.076 | 1 |
| R3bon | 1201-1300 | 82.4 | 44.9 | 0 | 9.1 | 30.5 (17.9, 11.0) | 4.5 | 0.221 | 497.1 | -0.603 | -0.056 | 4 |
| R3b (n3) | 1201-1300 | 77.5 | 37.0 | 0 | 8.5 | 25.2 (15.4, 8.4) | 3.0 | 0.195 | 458.6 | -0.602 | -0.159 | 4 |
| R3bon | 1401-1600 | 81.9 | 42.4 | 0 | 9.1 | 30.0 (18.4, 10.0) | 2.8 | 0.228 | 502.0 | -0.621 | -0.114 | 5 |
| R3b (n3) | 1401-1600 | 61.4 | 31.0 | 0 | 6.6 | 21.3 (13.2, 7.0) | 2.7 | 0.213 | 456.4 | -0.587 | -0.163 | 3 |
| R3bon | 2201-2400 | 76.4 | 39.4 | 0 | 8.4 | 26.5 (15.6, 9.3) | 3.8 | 0.207 | 506.5 | -0.585 | -0.183 | 8 |
| R3b (n3) | 2201-2400 | 46.6 | 21.9 | 0 | 5.0 | 13.7 (8.0, 4.8) | 2.8 | 0.171 | 457.3 | -0.608 | -0.355 | 4 |
| R3bon | 3201-4000 | 49.1 | 23.9 | 0 | 5.3 | 16.9 (10.2, 5.7) | 1.5 | 0.214 | 508.7 | -0.642 | -0.290 | 7 |
| R3b (n3) | 3201-4000 | 9.5 | 4.6 | 0 | 1.0 | 3.5 (2.1, 1.1) | 0.1 | | 471.4 | | | |

"Traits" counts core gaps (R A S B H T M W L) at abs >= 0.10. Other gaps at 1401-1600, on / off: S0 A -0.044 / -0.007,
M -0.092 / -0.076, W +0.017 / -0.008; Lrandom all within +-0.05 but R in both; R3bon S +0.292, H -0.137, W -0.160 (R3b
S +0.085, H -0.167). R3bon 3201-4000: A -0.160, S +0.326, M -0.257, W -0.328, L -0.133. Herd lineage depth 1401-1600
on / off: S0 7.13 / 7.42, Lrandom 6.30 / 6.35, R3b 22.80 / 22.81; IBD S0 0.650 / 0.711, Lrandom 0.690 / 0.725.
- Per seed 1401-1600, herd / starvation per herd goat-year: S0on 118/0.130, 110/0.170, 103/0.169, 121/0.136; S0
  109/0.137, 109/0.150, 121/0.143, 115/0.143. Lrandomon 102/0.209, 96/0.183, 104/0.219, 103/0.226; Lrandom 99/0.177,
  101/0.177, 99/0.181, 99/0.173.
- Wild starvation deaths per wild goat-year, 1401-1600, on / off: S0 0.103 / 0.097; Lrandom 0.095 / 0.096.
- R3bon: herd in every seed through year 3999; herd at year 4000: 42, 36, 11, 37. R3b without the buffer: last year
  with a herd 2718, 2552, 3910 (seeds 1-3).
- WT (no humans), all goats, on / off: 801-900 604.1 / 530.6; 1201-1300 604.0 / 543.7; 1401-1600 603.5 / 544.2 (per
  seed on 616.4, 637.9, 594.7, 564.9; off 567.5, 563.4, 536.4, 509.6). Starvation per goat-year 1401-1600 0.101 / 0.108.
  Population trait means 1401-1600, on / off: R 0.595 / 0.610, A 0.840 / 0.853, S 0.102 / 0.133, B 0.887 / 0.903, H
  0.852 / 0.857, T 0.238 / 0.168, M 0.624 / 0.626, W 0.787 / 0.725, L 0.441 / 0.501.
**Prediction scoring:**
- S0on and Lrandomon herd at 1401-1600 at least 10 above the same arm without the buffer: not met (S0 112.9 vs 113.5;
  Lrandom 101.2 vs 99.6).
- Herd starvation per herd goat-year at 1401-1600 falls, by less than half: not met; it does not fall (S0 0.151 vs
  0.143; Lrandom 0.209 vs 0.177).
- S0on R and B gaps at 1401-1600 within 0.10 of S0: met (R -0.541 vs -0.555; B -0.573 vs -0.561).
- WTon goats at 1401-1600 at least 5% above WT: met (603.5 vs 544.2, +10.9%).
- R3bon herd persists to year 4000 in at least 2 of 4 seeds: met (4 of 4; herds 42, 36, 11, 37).

## [RESULTS 2026-11-11] Herder range: does reaching further pasture relieve herd starvation? (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/herdrange/logs --list tools/herdrange.jsonl` at f8a3c69
(src of ee1dd8f); 16 of 16 exit 0, last finished 2026-11-10T23:46 local, 1115-1705 s each. Range 4: results/pilot S0
and results/lean S0on, seeds 1-4. Years 1-399 of R6off seed 1 equal pilot S0 seed 1, and of R6on seed 1 equal S0on
seed 1 (no herding before 400). Means over seeds, years 801-1000; budget as in the lean-buffer entry above.

| herdRange | leanBuffer | herd | births | capt | culled | non-cull (starv) | escaped (run-off lost) | starv / herd goat-yr | R | B |
|---|---|---|---|---|---|---|---|---|---|---|
| 4 | 0 | 104.5 | 49.8 | 8.5 | 11.4 | 30.4 (16.4) | 16.3 (14.1) | 0.156 | -0.485 | -0.392 |
| 6 | 0 | 0.8 | 0.2 | 4.4 | 0.1 | 0.2 (0.0) | 4.3 (0.1) | 0.000 | -0.033 | -0.004 |
| 8 | 0 | 0.7 | 0.2 | 4.5 | 0.1 | 0.2 (0.0) | 4.4 (0.1) | 0.000 | -0.035 | -0.000 |
| 4 | 12000 | 108.4 | 52.4 | 11.3 | 11.8 | 30.2 (15.4) | 21.6 (18.6) | 0.142 | -0.424 | -0.373 |
| 6 | 12000 | 0.9 | 0.2 | 5.1 | 0.1 | 0.3 (0.0) | 4.9 (0.2) | 0.000 | -0.029 | -0.000 |
| 8 | 12000 | 0.7 | 0.2 | 5.1 | 0.1 | 0.2 (0.0) | 5.0 (0.2) | 0.000 | -0.032 | -0.005 |

Gaps at range 6 and 8 average the few years with a herd (a goat or two). Range 4 lineage depth 5.47 (off), 4.41 (on).
- Ranges 6 and 8, years 400-1000, per seed, largest yearly herd / years with any herd (of 601) / captures / escaped (of
  which run-off lost): R6off 5/325/2436/2367(97), 5/337/2691/2602(95), 5/337/2847/2768(87), 5/258/2061/2021(53); R8off
  4/242/2467/2426(69), 4/301/2852/2757(58), 4/313/2788/2716(68), 5/205/2232/2179(47); R6on 5/357/2771/2668(101),
  4/358/2864/2752(117), 5/403/3855/3711(124), 4/305/2414/2297(93); R8on 4/297/2907/2792(76), 5/298/2784/2680(85),
  5/334/3765/3664(87), 3/211/2473/2424(71). Escapes not lost on running off are herd goats not home at the night check
  that bolt or are out of searchRange (6) when the herder goes back (src/world.js herdNight).
- Range 4 per seed herd / starvation per herd goat-year: off 108/0.167, 103/0.156, 99/0.150, 108/0.153; on 112/0.117,
  106/0.160, 106/0.156, 110/0.135.
- Diagnostic added after the result (not registered): `tools/rangeprobe.mjs 440 400 1 <S0 settings> herdRange=4|6`
  under cpuslot, code of f8a3c69. At the night check, years 400-440, seed 1, herd goats not kept or sheltered, by
  distance from camp in cells: range 4, 707638 goat-nights, 707175 at 0, 463 at 1-14, 102 lost; range 6, 7371
  goat-nights, 6580 at 0, 462 at 1, 311 at 2, 18 at 3-11, 143 lost. Pasture target distance from camp, herd-days:
  range 4, 0: 1861, 1: 501, 2: 7693, 3: 13972, 4: 17999; range 6, 0: 3110, 2: 895, 3: 3185, 4: 1937, 5: 982, 6: 806.
  (duskSteps is 4.)
**Prediction scoring:**
- herdRange 8 herd at 801-1000 at least 10 below range 4, with and without the buffer: met (0.7 vs 104.5; 0.7 vs 108.4).
- herdRange 8 herd starvation per herd goat-year higher than range 4: not met (0.000; there is no herd to starve).
- herdRange 6 herd no more than 10 below range 4: not met (0.8 vs 104.5; 0.9 vs 108.4).

## [PRE-REGISTERED 2026-11-11] Herd travel: a faster walk out and home, at herder range 4, 6 and 8
**Question:** The herder-range test (results entry above) lost every herd at herdRange 6 and 8: a penned herd walks 1
cell per sub-tick, so pasture more than duskSteps (4) cells out leaves goats short of camp at the night check, where
fresh captures bolt. Chris (2026-11-11): "the fix on range should be to allow faster movement to and from the grazing
zone." With herdTravel (MODEL.md C55, cells per sub-tick for a herd and its herder at dawn and dusk) at 2, does further
pasture give a larger herd, and does herd starvation per goat-year fall, or does the herd grow into the new pasture
(Chris, 2026-11-10: "goats will simply grow to that new one and starve")?
**Settings:** code of the commit registering this entry (perf-speedup merged at 4f1d7b6, herdTravel added; outputs at
herdTravel 1 checked identical to saved runs, see the commit message). tools/travel.jsonl: the reference culture
(tools/pilot.json S0) with herdTravel 2 and herdRange 4, 6 or 8, leanBuffer 0, seeds 1-4, 1000 years (12 runs).
Comparison at herdTravel 1: results/pilot S0 seeds 1-4, years 1-1000 (herdRange 4). A 600-year smoke at herdTravel 2,
herdRange 6, seed 1 was queued with the identity checks; this entry and its predictions were written before the smoke was read. Read before the commit:
mean herd 36.5, 51.0, 60.1, 65.9 in years 401-450, 451-500, 501-550, 551-600; no herd starvation deaths in 501-600.
**Method:** `cpuslot submit --tag animal-domestication --out results/travel/logs --list tools/travel.jsonl`. Per arm,
means over seeds in 801-1000: herd; herd starvation deaths per herd goat-year; the herd's yearly budget (births,
captures, culled, deaths by cause, escaped, run-off lost); R and B gaps; lineage depth; wild goats.
**Prediction:**
- herdTravel 2, herdRange 4: herd within 10 of herdTravel 1, herdRange 4.
- herdTravel 2, herdRange 6 and 8: herd at least 10 above herdTravel 2, herdRange 4.
- herdTravel 2, herdRange 6 and 8: herd starvation per herd goat-year within 0.03 of herdTravel 2, herdRange 4 (the
  herd grows into the pasture rather than starving less).

## [RESULTS 2026-11-11] Herd travel: a faster walk out and home, at herder range 4, 6 and 8 (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/travel/logs --list tools/travel.jsonl` at 82085e2; 12 of
12 exit 0, last finished 2026-11-11T08:13 local, 629-704 s each, sharing the machine. Comparison at herdTravel 1:
results/pilot S0 seeds 1-4 (herdRange 4). Means over seeds, years 801-1000; budget as in the lean-buffer entry above
(escaped counts every herd goat lost; run-off lost is the part lost on running off, the rest at the night check).

| herdTravel | herdRange | herd | births | capt | culled | non-cull (starv, other) | escaped (run-off lost) | starv / herd goat-yr | wild | depth | R | B | traits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 104.5 | 49.8 | 8.5 | 11.4 | 30.4 (16.4, 11.7) | 16.3 (14.1) | 0.156 | 444.3 | 5.47 | -0.485 | -0.392 | 2 |
| 2 | 4 | 101.7 | 51.6 | 8.3 | 11.0 | 33.5 (18.6, 12.7) | 15.4 (10.7) | 0.184 | 435.4 | 5.73 | -0.538 | -0.347 | 2 |
| 2 | 6 | 145.3 | 69.3 | 9.9 | 16.0 | 40.5 (21.4, 15.9) | 22.7 (12.0) | 0.148 | 430.7 | 6.04 | -0.547 | -0.488 | 3 |
| 2 | 8 | 223.9 | 106.3 | 7.1 | 24.5 | 69.5 (40.1, 24.4) | 19.4 (7.5) | 0.179 | 374.3 | 10.69 | -0.622 | -0.607 | 4 |

Other core gaps, 801-1000: travel 2 range 4 A -0.032, S +0.073, H -0.019, T +0.070, M -0.078, W -0.006, L +0.058;
range 6 S +0.156, T +0.079, M -0.073, others within +-0.05; range 8 T +0.129, L +0.148, W -0.062, H -0.067, others
within +-0.05. Wild starvation per wild goat-year: 0.102, 0.099, 0.089, 0.088 (rows in order). IBD 0.616, 0.641, 0.708,
0.798.
- Per seed herd / starvation per herd goat-year: travel 2 range 4 102/0.163, 97/0.228, 102/0.197, 106/0.148; range 6
  144/0.175, 145/0.148, 143/0.148, 149/0.119; range 8 216/0.175, 220/0.175, 233/0.161, 226/0.206.
- Herd and starvation per herd goat-year by window, travel 2: range 4 401-500 58.2/0.008, 601-700 96.6/0.108; range 6
  50.7/0.000, 130.1/0.083; range 8 54.7/0.000, 180.3/0.125.
**Prediction scoring:**
- herdTravel 2, herdRange 4: herd within 10 of herdTravel 1: met (101.7 vs 104.5).
- herdTravel 2, herdRange 6 and 8: herd at least 10 above herdTravel 2, herdRange 4: met (145.3; 223.9; vs 101.7).
- Starvation per herd goat-year within 0.03 of herdTravel 2, herdRange 4 (0.184): range 8 met (0.179); range 6 not met
  (0.148, 0.036 lower).

## [STANDARD SETTINGS 2026-11-11] leanBuffer 12000, herdRange 8, herdTravel 2 become the defaults
With Chris (2026-11-11): "i think lean buffer should be default too. and yes to range 8, but note range as an important
sweep variable." src/params.js now defaults leanBuffer 12000 (was 0), herdRange 8 (was 4), herdTravel 2 (was 1), from
the commit carrying this entry. Every earlier entry ran the old defaults unless its settings say otherwise. Grounds:
the lean-buffer, herder-range and herd-travel results entries above. herdRange is to be swept in the paper suite and
its effect on herd size and on the gaps reported.

## [PRE-REGISTERED 2026-11-11] Run-length pilot on the new base: how long must the suite run at range 8?
**Question:** The new standard settings (entry above: leanBuffer 12000, herdRange 8, herdTravel 2) give herds about
twice the reference herd, so the epoch and corner pilots, run on the old defaults, do not set the suite's length; 42 of
the corner pilot's 52 runs were never made. Chris (2026-11-11): "keeping range 8 makes sense if we see more movement in
the genes. it might mean shorter epoch." How long does each arm take to settle on the new base, does range 8 settle no
later than range 4, and does it separate herd from wild more?
**Settings:** code of the commit registering this entry (a0e3e4d + this entry). tools/settle.json (jobs
tools/settle.jsonl): every arm states leanBuffer 12000, herdRange 8, herdTravel 2 explicitly, on top of:
- anchors from tools/pilot.json: S0 (reference culture, oldest sires), Lrandom (random sires), Hped (homebred,
  herdMemory 3), WT (no humans);
- the 13 corner arms of tools/corners.json (noGuard, noMilk, noPen, noBuck, noTether, noShelter, randCull,
  noGuardMilk, noBuckRandCull, Ldeep, bCullRand, dCullLarge, R3aRandom), unchanged otherwise;
- R3bRandom from tools/corners_r3.json (random sires, captureUntil 800);
- range sweep: S0R4 and S0R6, S0 with herdRange 4 and 6.
20 arms, seeds 1-4, 4000 years (80 runs).
**Method:** `cpuslot submit --tag animal-domestication --out results/settle/logs --list tools/settle.jsonl`. Scored as
the corner pilot was registered (entry 2026-11-10): per arm and seed, 200-year window means of every core gap (R A S B
H T M W L) ending at E = 1600, 2000, 2400, 2800, 3200, against the 3201-4000 mean; bias and its SE over seeds; also
herd, lineage depth, IBD, captures, wild-sired share, breadth (core traits with abs(gap) >= 0.10), wild goats, the
herd's yearly budget. WT: whole-population trait means. R3bRandom: last year with a herd, per seed.
**Prediction** (written before any run on the new base):
- S0 settles at the same E as S0R4 or earlier.
- S0 breadth at 3201-4000 is at least S0R4's plus 1.
- S0 R gap at 3201-4000 is at least 0.05 more negative than S0R4's.
- Herd at 3201-4000 rises S0R4 < S0R6 < S0, each step at least 20.
- R3bRandom keeps a herd to year 4000 in at least 3 of 4 seeds.
- noGuard and noMilk are not settled at 1600 (B bias beyond 0.05).
- The suite length the rule gives is 2400 or less.
**Decision rule:** the corner pilot's (an arm is settled at E if abs(bias) <= 0.05 for every core trait at E and every
later candidate end; arms with a 3201-4000 herd under 30 report but do not set the length; the suite runs to the latest
settled E over the arms, or to 4000 if any arm is unsettled at 3200). WT is reported and does not set the length. The
range arms S0R4 and S0R6 count like any other arm.

## [RESULTS 2026-11-11] Run-length pilot on the new base: how long must the suite run at range 8? (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/settle/logs --list tools/settle.jsonl` at 0098c89; 80 of
80 exit 0, last finished 2026-11-11T15:48 local, 2386-4733 s each (part of the batch ran during the cpuslot level
experiment, which suspends and resumes runs; outputs are seeded and do not depend on it). Scored by the pre-registered
rule (scratchpad settle_tab.py): per arm and seed, 200-year window means ending at E against the 3201-4000 mean, bias and
SE over 4 seeds. Breadth n = core traits (R A S B H T M W L) with abs(gap) >= 0.10 on the seed-mean gaps.

Long run, 3201-4000, means over seeds (wss = wild-sired share of herd births):

| arm | herd | wild | depth | IBD | capt/yr | wss | R | A | S | B | H | T | M | W | L | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 242.3 | 456.9 | 15.34 | 0.948 | 7.71 | 0.002 | -0.636 | -0.135 | +0.273 | -0.801 | -0.148 | +0.194 | -0.242 | -0.191 | -0.039 | 8 |
| S0R6 | 155.8 | 496.0 | 8.56 | 0.857 | 9.83 | 0.007 | -0.573 | -0.028 | +0.021 | -0.664 | -0.044 | +0.113 | -0.002 | -0.015 | -0.000 | 3 |
| S0R4 | 114.4 | 506.6 | 8.17 | 0.862 | 8.77 | 0.010 | -0.581 | -0.010 | +0.067 | -0.579 | -0.022 | +0.022 | -0.127 | -0.021 | -0.040 | 3 |
| Lrandom | 203.5 | 452.4 | 15.14 | 0.974 | 7.96 | 0.002 | -0.585 | -0.055 | +0.104 | -0.230 | -0.141 | +0.104 | -0.015 | -0.117 | +0.104 | 7 |
| Hped | 210.6 | 452.8 | 20.79 | 0.989 | 7.63 | 0.002 | -0.598 | -0.216 | +0.378 | -0.346 | -0.286 | +0.239 | -0.195 | -0.162 | +0.080 | 8 |
| noGuard | 234.6 | 457.7 | 14.79 | 0.911 | 7.79 | 0.003 | -0.634 | -0.062 | +0.193 | -0.792 | -0.131 | +0.191 | -0.204 | -0.018 | +0.081 | 6 |
| noMilk | 235.3 | 454.8 | 13.54 | 0.907 | 8.11 | 0.003 | -0.629 | -0.202 | +0.175 | -0.757 | -0.091 | +0.243 | -0.028 | -0.064 | +0.060 | 5 |
| noPen | 390.4 | 378.8 | 17.17 | 0.967 | 6.57 | 0.001 | -0.636 | -0.435 | +0.247 | -0.816 | -0.292 | +0.333 | -0.421 | -0.101 | -0.082 | 8 |
| noBuck | 194.8 | 422.4 | 8.86 | 0.887 | 11.21 | 0.086 | -0.498 | -0.086 | +0.030 | -0.010 | +0.000 | +0.146 | -0.030 | +0.003 | +0.044 | 2 |
| noTether | 242.7 | 457.8 | 15.29 | 0.932 | 7.44 | 0.001 | -0.637 | -0.307 | +0.180 | -0.820 | -0.179 | +0.168 | -0.165 | -0.072 | +0.002 | 7 |
| noShelter | 247.0 | 454.4 | 15.14 | 0.928 | 7.55 | 0.002 | -0.633 | -0.253 | +0.228 | -0.807 | -0.159 | +0.186 | -0.251 | -0.093 | +0.013 | 7 |
| randCull | 189.2 | 450.5 | 16.05 | 0.923 | 6.89 | 0.002 | -0.614 | -0.150 | +0.173 | -0.031 | -0.097 | +0.247 | -0.223 | -0.144 | +0.071 | 6 |
| noGuardMilk | 228.5 | 454.6 | 12.36 | 0.888 | 8.55 | 0.003 | -0.618 | -0.071 | +0.147 | -0.740 | -0.110 | +0.179 | -0.118 | +0.023 | +0.009 | 6 |
| noBuckRandCull | 181.6 | 437.8 | 12.95 | 0.850 | 9.09 | 0.044 | -0.550 | -0.259 | +0.072 | +0.001 | +0.000 | +0.275 | -0.087 | -0.045 | +0.050 | 3 |
| Ldeep | 214.5 | 452.1 | 21.48 | 0.982 | 7.67 | 0.002 | -0.601 | -0.253 | +0.372 | -0.410 | -0.297 | +0.192 | -0.158 | -0.198 | +0.128 | 9 |
| bCullRand | 191.6 | 446.0 | 14.81 | 0.949 | 7.22 | 0.002 | -0.607 | -0.198 | +0.136 | -0.033 | -0.171 | +0.275 | -0.131 | +0.005 | +0.032 | 6 |
| dCullLarge | 171.9 | 447.6 | 11.64 | 0.895 | 7.72 | 0.004 | -0.595 | -0.055 | +0.049 | -0.067 | -0.006 | +0.206 | -0.068 | -0.015 | +0.051 | 2 |
| R3aRandom | 207.2 | 448.9 | 13.98 | 0.965 | 8.69 | 0.002 | -0.570 | -0.116 | +0.167 | -0.262 | -0.017 | +0.067 | -0.075 | -0.083 | +0.035 | 4 |
| R3bRandom | 161.0 | 474.6 | 23.00 | 1.000 | 0.00 | 0.000 | -0.656 | -0.259 | +0.279 | -0.604 | -0.366 | +0.171 | -0.229 | -0.312 | +0.139 | 9 |

Herd budget, 3201-4000, per year (births / captures / culled / other deaths (of which starvation) / escaped (of which
run-off lost) / starvation per herd goat-year): S0 100.3/7.7/26.3/65.0(34.2)/16.7(6.8)/0.141; S0R6
66.8/9.8/17.0/40.9(21.1)/18.6(10.1)/0.135; S0R4 49.2/8.8/12.3/31.6(17.0)/14.0(9.8)/0.149; Lrandom 0.240; Hped 0.260;
noPen 0.171; noBuck 0.375; Ldeep 0.237; R3bRandom 0.194; other arms 0.116-0.301 (scratchpad settle_tab.out).

Bias (window ending E minus 3201-4000): largest abs over the 9 core traits [trait]; ok = every trait within 0.05:

| arm | 1600 | 2000 | 2400 | 2800 | 3200 | settled at |
|---|---|---|---|---|---|---|
| S0 | 0.190 [M] | 0.139 [W] | 0.102 [M] | 0.045 ok | 0.049 ok | 2800 |
| S0R6 | 0.104 [A] | 0.035 ok | 0.049 ok | 0.037 ok | 0.048 ok | 2000 |
| S0R4 | 0.113 [M] | 0.111 [M] | 0.064 [M] | 0.092 [M] | 0.043 ok | 3200 |
| Lrandom | 0.077 [M] | 0.075 [W] | 0.104 [H] | 0.099 [H] | 0.078 [B] | not settled |
| Hped | 0.164 [H] | 0.175 [S] | 0.135 [S] | 0.096 [M] | 0.049 ok | 3200 |
| noGuard | 0.078 [H] | 0.074 [A] | 0.084 [A] | 0.075 [L] | 0.077 [W] | not settled |
| noMilk | 0.092 [A] | 0.075 [A] | 0.063 [A] | 0.061 [M] | 0.049 ok | 3200 |
| noPen | 0.240 [H] | 0.174 [H] | 0.174 [H] | 0.169 [H] | 0.095 [H] | not settled |
| noBuck | 0.051 [A] | 0.037 ok | 0.030 ok | 0.057 [A] | 0.027 ok | 3200 |
| noTether | 0.154 [M] | 0.149 [L] | 0.093 [L] | 0.128 [L] | 0.087 [A] | not settled |
| noShelter | 0.156 [A] | 0.161 [A] | 0.128 [A] | 0.058 [L] | 0.039 ok | 3200 |
| randCull | 0.200 [M] | 0.139 [M] | 0.109 [L] | 0.081 [L] | 0.048 ok | 3200 |
| noGuardMilk | 0.101 [S] | 0.077 [T] | 0.078 [W] | 0.080 [T] | 0.046 ok | 3200 |
| noBuckRandCull | 0.162 [A] | 0.095 [A] | 0.068 [A] | 0.066 [W] | 0.033 ok | 3200 |
| Ldeep | 0.176 [B] | 0.152 [B] | 0.126 [L] | 0.121 [W] | 0.084 [W] | not settled |
| bCullRand | 0.123 [H] | 0.104 [H] | 0.089 [H] | 0.049 ok | 0.035 ok | 2800 |
| dCullLarge | 0.093 [A] | 0.064 [L] | 0.071 [B] | 0.062 [T] | 0.042 ok | 3200 |
| R3aRandom | 0.178 [B] | 0.087 [B] | 0.090 [L] | 0.060 [T] | 0.089 [T] | not settled |
| R3bRandom | 0.318 [B] | 0.333 [B] | 0.259 [B] | 0.142 [B] | 0.052 [H] | not settled |

Every arm's 3201-4000 herd is at least 161, so every arm counts. R bias is within 0.046 in every arm at every E. B bias
beyond 0.05 at some E >= 1600: Lrandom (+0.078 ± 0.054 at 3200), Ldeep (+0.176 ± 0.030 at 1600 falling to +0.048 at
3200), dCullLarge (+0.071 at 2400), R3aRandom (+0.178 ± 0.083 at 1600, +0.087 at 2000), R3bRandom (+0.318, +0.333, +0.259,
+0.142, +0.028). Other failures are on A H L M S T W; SEs on those traits are 0.01-0.15 (full table in
scratchpad settle_tab.out).
- Per seed 3201-4000, herd / R / B / n: S0 243/-0.64/-0.80/9, 241/-0.64/-0.81/8, 249/-0.63/-0.81/7, 236/-0.64/-0.79/6;
  S0R6 156/-0.58/-0.66/4, 145/-0.57/-0.63/2, 167/-0.56/-0.69/3, 156/-0.59/-0.67/2; S0R4 119/-0.63/-0.70/4,
  116/-0.60/-0.63/3, 120/-0.56/-0.64/3, 102/-0.53/-0.35/2.
- R3bRandom last year with a herd, seeds 1-4: 3575, 3999, 3999, 3999; herd in year 4000: 0, 71, 256, 254.
- WT (no humans) whole-population means, 1401-1600 / 3201-4000: goats 603.5 / 608.0; R 0.595 / 0.596, B 0.887 / 0.896,
  L 0.441 / 0.495, others within 0.02.
- Not pre-registered (scratchpad settle_early.py), 200-year windows ending 600-1600 (herding starts at 400), herd / R / B /
  n: S0 at 1000 221/-0.62/-0.58/3, at 1200 238/-0.64/-0.75/5, at 1600 237/-0.64/-0.79/5; S0R6 at 1200 149/-0.57/-0.65/4;
  S0R4 at 1200 103/-0.51/-0.38/2, at 1600 111/-0.55/-0.55/2. Lrandom at 1200 204/-0.56/-0.19/3; noPen at 1200
  373/-0.64/-0.81/5.
**Prediction scoring:**
- S0 settles at the same E as S0R4 or earlier: met (2800 vs 3200).
- S0 breadth at 3201-4000 at least S0R4's plus 1: met (8 vs 3).
- S0 R gap at least 0.05 more negative than S0R4's: met (-0.636 vs -0.581, 0.055).
- Herd rises S0R4 < S0R6 < S0, each step at least 20: met (114.4, 155.8, 242.3).
- R3bRandom keeps a herd to year 4000 in at least 3 of 4 seeds: met (3 of 4; seed 1 lost its herd in 3575).
- noGuard and noMilk not settled at 1600 with B bias beyond 0.05: not met. Neither is settled at 1600, but on other
  traits; B bias at 1600 is -0.011 (noGuard) and -0.022 (noMilk).
- The suite length the rule gives is 2400 or less: not met. The rule gives 4000: Lrandom, noGuard, noPen, noTether, Ldeep,
  R3aRandom and R3bRandom are not settled at 3200.

## [CONCLUSION 2026-11-11] Run length on the new base
The pre-registered rule sets the suite at 4000 years, and the suite runs to 4000. On the new base, the headline gaps arrive
early: R bias is within 0.05 by 1600 in every arm, and S0 reaches R -0.64, B -0.75 by 1001-1200. The minor traits (A H L M
S T W), and B in the lineage and R3 arms (Ldeep, R3aRandom, R3bRandom), keep moving past 2400. Some of those failures sit
within two seed SEs of 0.05 and some are steady trends (Ldeep B, R3bRandom B, noPen H); the rule does not separate the two,
and 4 seeds cannot. Range 8 separates more and sooner than range 4 on every pre-registered count: herd 242 vs 114, breadth
8 vs 3, B -0.80 vs -0.58, settled 2800 vs 3200. Range 6 settles earliest (2000) with breadth 3.

## [PRE-REGISTERED 2026-11-11] Anchor ladder pilot: wild type 1, wild type 2, minimal herding, maximal herding
**Question:** Chris (2026-11-11): "i think we need a few anchors in a ladder. like wild type 1 (no humans), wild type 2
(human predation), herding minimal, herding maximal." Every block of the suite will depart from one of these rungs.
Two rungs have not run on the new base (entry [STANDARD SETTINGS 2026-11-11]): wild type 2, and minimal herding. Does a
minimal herding culture keep a herd at range 8, how far does it separate from the wild, and what does human hunting alone
do to the wild goats?
**Settings:** code of the commit registering this entry (c16de77 + this entry). tools/ladder.json (jobs
tools/ladder.jsonl), every arm with twinMax 1, tripletMax 0.2, leanBuffer 12000, herdRange 8, herdTravel 2:
- WT2, wild type 2: humans hunt and forage from year 300 and never herd (herdingAt 1e9; the old H1).
- Hmin, minimal herding: herding from 400 with every behaviour of the husbandry factorial at its off level: random
  cull, penning 0, guarding 0, provision 0, kidShelter 0, buckManagement 0, tetherNew 0, milkIntensity 0, exchangeN 0;
  offtake 10% a year (the old H2 plus the new base).
- Rungs already run (results/settle, same base and seeds): WT1 = WT (no humans), Hmax = S0 (the reference culture).
4 seeds, 4000 years (8 new runs).
**Method:** `cpuslot submit --tag animal-domestication --out results/ladder/logs --list tools/ladder.jsonl`. Means over
seeds in 3201-4000 and in the outline's report windows 401-500, 801-900, 1201-1300, 1501-1600: wild and herd goats;
whole-population trait means (WT1, WT2); herd-wild gaps, breadth (core traits R A S B H T M W L with abs(gap) >= 0.10),
lineage depth, IBD, captures, the herd's yearly budget (Hmin, Hmax). Settling by the run-length rule (entry
2026-11-10, corner pilot), reported for Hmin.
**Prediction** (written before any ladder run):
- WT2 holds fewer goats than WT1 in 3201-4000, by at least 50.
- Every WT2 whole-population trait mean in 3201-4000 is within 0.05 of WT1's.
- Hmin keeps a herd to year 4000 in at least 3 of 4 seeds, with a 3201-4000 herd between 30 and 150.
- Hmin R gap in 3201-4000 is -0.10 or below; its B gap is within 0.10 of 0.
- Hmin breadth in 3201-4000 is 3 or less (Hmax 8); its lineage depth is below Hmax's (15.3).

## [RESULTS 2026-11-11] Anchor ladder pilot: wild type 1, wild type 2, minimal herding, maximal herding (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/ladder/logs --list tools/ladder.jsonl` at 3cf8105; 8 of
8 exit 0, started 2026-11-11T18:22 local, 1980-2938 s each. The runs loaded src before 2def6a7 (lineage depth through
wild births), so they carry no histDepth. WT1 = results/settle WT, Hmax = results/settle S0 (same base and seeds). Means
over seeds (scratchpad ladder_tab.py, ladder_tab.out).

Wild types, goats and whole-population gene means:

| rung | years | goats | R | A | S | B | H | T | M | W | L | C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| WT1 | 401-500 | 579.1 | 0.619 | 0.812 | 0.257 | 0.888 | 0.818 | 0.249 | 0.622 | 0.604 | 0.426 | 0.486 |
| WT2 | 401-500 | 485.6 | 0.824 | 0.822 | 0.288 | 0.884 | 0.813 | 0.268 | 0.611 | 0.604 | 0.425 | 0.501 |
| WT1 | 1501-1600 | 603.8 | 0.595 | 0.842 | 0.103 | 0.887 | 0.855 | 0.230 | 0.627 | 0.788 | 0.450 | 0.519 |
| WT2 | 1501-1600 | 509.9 | 0.829 | 0.842 | 0.112 | 0.872 | 0.825 | 0.279 | 0.699 | 0.703 | 0.519 | 0.383 |
| WT1 | 3201-4000 | 608.0 | 0.596 | 0.843 | 0.098 | 0.896 | 0.848 | 0.231 | 0.628 | 0.792 | 0.495 | 0.449 |
| WT2 | 3201-4000 | 515.8 | 0.832 | 0.847 | 0.110 | 0.880 | 0.824 | 0.268 | 0.698 | 0.719 | 0.543 | 0.545 |

WT2 minus WT1 in 3201-4000: goats -92.1; R +0.236, A +0.004, S +0.012, B -0.016, H -0.025, T +0.037, M +0.070, W -0.073,
L +0.049, C +0.096. Goats per seed 3201-4000: WT1 621, 649, 590, 572; WT2 547, 546, 500, 470.

Herding rungs:

| rung | years | herd | wild | depth | IBD | capt/yr | R | A | S | B | H | T | M | W | L | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hmin | 401-500 | 17.5 | 480.7 | 1.44 | 0.066 | 5.15 | -0.050 | -0.000 | -0.013 | -0.003 | +0.001 | +0.021 | +0.011 | +0.007 | +0.016 | 0 |
| Hmin | 1501-1600 | 18.5 | 502.0 | 1.44 | 0.409 | 5.57 | -0.050 | -0.001 | +0.002 | +0.003 | +0.006 | +0.014 | -0.016 | -0.010 | +0.017 | 0 |
| Hmin | 3201-4000 | 18.5 | 509.4 | 1.52 | 0.794 | 5.38 | -0.048 | +0.000 | +0.005 | -0.002 | +0.000 | +0.002 | +0.002 | +0.002 | -0.005 | 0 |
| Hmax | 401-500 | 65.2 | 476.9 | 1.72 | 0.170 | 12.98 | -0.081 | -0.008 | +0.032 | -0.020 | -0.008 | +0.041 | -0.003 | -0.018 | +0.015 | 0 |
| Hmax | 801-900 | 220.1 | 429.0 | 9.46 | 0.816 | 7.84 | -0.614 | -0.019 | +0.045 | -0.527 | -0.086 | +0.209 | -0.031 | -0.033 | +0.062 | 3 |
| Hmax | 1501-1600 | 236.2 | 454.1 | 15.19 | 0.898 | 7.65 | -0.642 | -0.078 | +0.271 | -0.791 | -0.117 | +0.217 | -0.053 | -0.016 | +0.075 | 5 |
| Hmax | 3201-4000 | 242.3 | 456.9 | 15.34 | 0.948 | 7.71 | -0.636 | -0.135 | +0.273 | -0.801 | -0.148 | +0.194 | -0.242 | -0.191 | -0.039 | 8 |

- Hmin per seed 3201-4000, herd / R / B / n: 17/-0.04/-0.00/0, 17/-0.05/-0.00/0, 19/-0.04/-0.00/0, 21/-0.07/-0.00/0; a
  herd in all 800 years and in year 4000 in every seed (10, 10, 21, 17 goats).
- Hmin herd budget 3201-4000 per year: births 8.8, captures 5.4, culled 2.1, other deaths 6.6 (starvation 0.5), escaped
  5.5 (run-off lost 4.2); starvation per herd goat-year 0.025 (Hmax 0.141).
- Hmin settling by the run-length rule: max bias 0.020 [L] at 1600, 0.017 at 2000, 0.020 at 2400, 0.010 at 2800, 0.004 [R]
  at 3200; settled at 1600.
- Wild gene means in 3201-4000 (dashboard data, settle S0 against WT2 here): R 0.706 vs 0.832, B 0.877 vs 0.880.
**Prediction scoring:**
- WT2 holds at least 50 fewer goats than WT1 in 3201-4000: met (-92.1).
- Every WT2 whole-population gene mean within 0.05 of WT1's: not met (R +0.236, M +0.070, W -0.073; the neutral C
  +0.096).
- Hmin keeps a herd to 4000 in at least 3 of 4 seeds, herd 30-150 in 3201-4000: half met. A herd in 4 of 4 seeds, but it
  averages 18.5.
- Hmin R gap -0.10 or below: not met (-0.048). Hmin B gap within 0.10 of 0: met (-0.002).
- Hmin breadth 3 or less and depth below Hmax's: met (breadth 0; depth 1.52 vs 15.34).

## [PRE-REGISTERED 2026-11-11] Isolated herds: no wild goats in after year 800, offtake only above a floor
**Question:** Chris (2026-11-11): "i want the isolated herd to only cull over some level so the population can be
maintained and run out for some time to see what happens. also on anchor settings ... my hypothesis is pure isolation
would complete the picture." The herd distributions keep a thin wild-like tail (captures and their first generations),
and gene flow from the wild may hold some genes near their wild state. With no wild genes entering after year 800 and a
herd kept from being eaten out, do herd and wild separate on more genes and further, and does the wild-like tail go?
**Settings:** code of the commit registering this entry: `cullFloor` (params.js, world.js: the night's offtake never takes
a camp's herd below cullFloor goats; the offtake draw is kept, so cullFloor 0 reproduces earlier runs, checked: S0 seed
1, 600 years, 0 of 600 year records differ from results/settle) and `wildSireBlockFrom` (the year wildSireBlock starts;
default 0, as every earlier R3 run had it). tools/iso.json, new base (leanBuffer 12000, herdRange 8,
herdTravel 2, twinMax 1, tripletMax 0.2); isolation = captureUntil 800 (no captures or orphans taken from year 800) and
wildSireBlock 1 with wildSireBlockFrom 800 (no wild buck mates a herd doe from year 800); camps do not exchange goats
(exchangeN 0):
- HmaxIso: the reference culture (results/settle S0) isolated, cullFloor 30.
- HmaxIsoNF: the same with no floor (cullFloor 0).
- LrIso: random sires (results/settle Lrandom) isolated, cullFloor 30.
- HminIso: minimal herding (results/ladder Hmin) isolated, cullFloor 30.
Open-herd controls, already run on the same base and seeds: results/settle S0 and Lrandom, results/ladder Hmin. 4 seeds,
4000 years (16 runs). The runs record gene histograms by lineage (histDepth).
**Method:** `cpuslot submit --tag animal-domestication --out results/iso/logs --list tools/iso.jsonl`. Windows 701-800
(before isolation), 1201-1300, 1501-1600, 3201-4000, pooled over seeds. The main measure is a distribution, not a mean:
per gene, the herd-wild overlap OVL = sum over the 20 genotype buckets of min(herd share, wild share), from the year
histograms (1 = the same distribution, 0 = none shared; scratchpad overlap.py); the neutral gene C is the drift
yardstick. Also: the share of herd goats with R genotype 0.40 or more (the wild range); herd size and the last year
with a herd, per seed; lineage depth; IBD; the herd's yearly budget; mean gaps and breadth as before. Open-herd values
already computed with overlap.py, 3201-4000: S0 overlap R 0.02 A 0.59 S 0.34 B 0.03 H 0.45 T 0.35 M 0.43 W 0.48 L 0.78
C 0.84, herd R >= 0.40 0.01; Lrandom R 0.04 A 0.78 S 0.59 B 0.38 H 0.57 T 0.60 M 0.80 W 0.70 L 0.65 C 0.84, 0.02; Hmin R
0.74, all others 0.97-0.99, 1.00. (results/settle R3bRandom, random sires with captures stopped at 800 and wild bucks
not blocked: A 0.33 S 0.32 B 0.02 H 0.22 T 0.41 M 0.38 W 0.28 L 0.76 C 0.73, 0.00.)
Smoke, read before these predictions: HmaxIso settings with wild sires blocked from year 0 (before wildSireBlockFrom
existed), seed 1, 1200 years: herd 222.7 / 233.3 / 218.0 / 218.1 / 239.0 in 701-800 / 801-900 / 901-1000 / 1001-1100 /
1101-1200 (lowest year 100), no captures from 800, culled 22-26 a year.
**Prediction** (written before any isolated run but that smoke):
- HmaxIso keeps a herd to year 4000 in at least 3 of 4 seeds; HmaxIsoNF in fewer seeds than HmaxIso, or with a smaller
  3201-4000 herd.
- HmaxIso herd R >= 0.40 share in 3201-4000 is 0.005 or less.
- HmaxIso overlap in 3201-4000 is below S0's on at least 6 of the 8 genes A S B H T M W L.
- LrIso overlap in 3201-4000 is at least 0.15 below Lrandom's on each of A S B H W.
- HminIso has lost its herd by year 4000 in at least 3 of 4 seeds.
- In every isolated arm with a herd in 3201-4000, C overlap is above the lowest overlap among A S B H T M W.

## [PRE-REGISTERED 2026-11-11] Immigration: hunted wild goats swapped into the local wild at 1, 4 and 10% a year
**Question:** Chris (2026-11-11): "let's have immigrants that are hunted wild goats swap out for random not herd goats at
different rates", on the assumption that the wild population at large was much larger than the herds. Escaped herd
goats and their descendants make up much of the local wild (S0 seed 1, years 500-599: mean herd-born genome share 0.59;
2def6a7), and the wild's R sits between the hunted-only wild's and the herd's. Does immigration from a hunted wild
population push the feral share down and the wild back toward the hunted-only wild type, and what does that do to the
herd and to herd-wild separation?
**Settings:** code of the commit registering this entry. `immigrationRate` (params.js; World.immigrate, Goat.becomeImmigrant):
from humansAt, at each year's start, that share of the adult wild goats (not pregnant, no kids at foot, not being led;
stochastic rounding) is chosen at random and swapped in place for an immigrant: same place, sex and age; a new id;
a genome and learned fears drawn at random from the pool; fresh lineage ids; no herd ancestry; adult size from its own
genes. Draws random numbers only when the rate is above 0 (checked: rate 0, S0 seed 1, 600 years, against
results/settle; see the commit). Pool `tools/pools/wt2.json`: hunted-only wild goats (WT2 settings, seeds 101-104,
not the runs' seeds), 150 adults sampled at the ends of years 1000, 1100, ..., 1600 per seed (tools/pool.mjs).
tools/imm.json, new base: I01, I04, I10 = the reference culture (results/settle S0) with immigrationRate 0.01, 0.04, 0.10;
WT2I04 = the hunted-only wild (results/ladder WT2) with 0.04, a control in which immigrants match the residents. Rate 0:
results/settle S0, results/ladder WT2. 4 seeds, 4000 years (16 runs).
**Method:** `cpuslot submit --tag animal-domestication --out results/imm/logs --list tools/imm.jsonl`. Windows 401-500,
801-900, 1501-1600, 3201-4000, pooled over seeds: wild goats' mean herd-born share (wildHerdShare) and share with any
(wildAnyHerd); wild and whole-population gene means; herd-wild overlap per gene (scratchpad overlap.py), herd R >= 0.40
share; herd size, depth, IBD, captures, the herd's budget; immigrants a year. Rate-0 values: S0 3201-4000 wild R 0.706
(dashboard data), herd 242.3, overlap R 0.02 A 0.59 S 0.34 B 0.03 H 0.45 T 0.35 M 0.43 W 0.48 L 0.78 C 0.84; WT2
3201-4000 R 0.832. S0 at rate 0 has no wildHerdShare record (run before 2def6a7).
Smoke, read before these predictions: I10 settings, seed 1, 500 years: 0 immigrants a year before humansAt (300),
then 23-27 a year (24.9 a year in 301-400, 26.5 in 401-500) against 454-608 goats in all; whole-population R 0.643 /
0.816 / 0.797 in 201-300 / 301-400 / 401-500; herd 54.8 and wildHerdShare 0.202 in 401-500 (herding from 400). The
smoke records no count of eligible wild adults, so it shows swaps happen at a steady rate, not that the rate is exactly
10% of them.
**Prediction** (written before any immigration run):
- wildHerdShare in 3201-4000 falls with the rate: I01 > I04 > I10, and I10 is below half of I01.
- Wild R mean in 3201-4000 rises with the rate (I01 < I04 < I10), and I10's is within 0.05 of WT2's (0.832).
- I10 herd-wild overlap in 3201-4000 is below S0's on at least 5 of A S B H T M W L.
- Herd in 3201-4000 within 10% of S0's (242.3) at every rate.
- WT2I04 whole-population gene means in 3201-4000 within 0.03 of WT2's on every gene.

## [RESULTS 2026-11-11] Isolated herds: no wild goats in after year 800, offtake only above a floor (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/iso/logs --list tools/iso.jsonl` at ce87c7b; 16 of 16
exit 0, 3529-7319 s each. Controls: results/settle S0 (open HmaxIso), results/settle Lrandom (open LrIso),
results/ladder Hmin (open HminIso). Means over seeds; window means of gene gaps, depth and IBD over the seeds with a
herd in the window; overlap pooled over seeds (scratchpad iso_tab.py, iso_out.txt; traj.py for per-century herds).

Herd, and herd size per seed, 3201-4000 (herd 0 = lost):

| arm | 701-800 | 1201-1300 | 1501-1600 | 3201-4000 | per seed 3201-4000 | last year with a herd, per seed |
|---|---|---|---|---|---|---|
| HmaxIso | 211.2 | 209.6 | 184.6 | 40.1 | 0, 81, 0, 79 | 2868, 3999, 2732, 3999 |
| HmaxIsoNF | 211.3 | 218.2 | 210.3 | 101.2 | 108, 54, 84, 159 | 3999, 3719, 3999, 3999 |
| LrIso | 197.6 | 203.6 | 205.2 | 188.8 | 207, 193, 158, 197 | 3999 in all |
| HminIso | 66.7 | 94.2 | 107.3 | 91.3 | 0, 125, 141, 99 | 890, 3999, 3999, 3999 |
| S0 (open) | 211.3 | 236.4 | 236.2 | 242.3 | 243, 241, 249, 236 | 3999 in all |
| Lrandom (open) | 198.7 | 200.9 | 207.0 | 203.5 | 198, 202, 204, 210 | 3999 in all |
| Hmin (open) | 19.1 | 18.8 | 18.5 | 18.5 | 17, 17, 19, 21 | 3999 in all |

Herd-wild overlap per gene (1 = same distribution) and herd share with R genotype >= 0.40, 3201-4000:

| arm | R | A | S | B | H | T | M | W | L | C | R>=0.40 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HmaxIso (seeds 2, 4) | 0.00 | 0.09 | 0.03 | 0.00 | 0.01 | 0.22 | 0.26 | 0.46 | 0.83 | 0.46 | 0.000 |
| HmaxIsoNF | 0.00 | 0.57 | 0.26 | 0.00 | 0.48 | 0.06 | 0.42 | 0.63 | 0.67 | 0.71 | 0.000 |
| S0 | 0.02 | 0.59 | 0.34 | 0.03 | 0.45 | 0.35 | 0.43 | 0.48 | 0.78 | 0.84 | 0.011 |
| LrIso | 0.01 | 0.31 | 0.11 | 0.09 | 0.19 | 0.29 | 0.65 | 0.36 | 0.47 | 0.75 | 0.000 |
| Lrandom | 0.04 | 0.78 | 0.59 | 0.38 | 0.57 | 0.60 | 0.80 | 0.70 | 0.65 | 0.84 | 0.016 |
| HminIso (seeds 2-4) | 0.00 | 0.04 | 0.14 | 0.76 | 0.87 | 0.55 | 0.82 | 0.82 | 0.75 | 0.64 | 0.000 |
| Hmin | 0.74 | 0.99 | 0.98 | 0.99 | 0.99 | 0.98 | 0.97 | 0.97 | 0.98 | 0.98 | 1.000 |

Gene gaps (herd mean minus wild mean), 3201-4000, and the count n of R A S B H T M W L at 0.10 or more:

| arm | R | A | S | B | H | T | M | W | L | C | n |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HmaxIsoNF | -0.73 | -0.22 | +0.20 | -0.82 | -0.15 | +0.31 | -0.29 | -0.15 | -0.15 | -0.04 | 9 |
| LrIso | -0.64 | -0.24 | +0.28 | -0.56 | -0.35 | +0.22 | -0.14 | -0.26 | +0.19 | +0.10 | 9 |
| HminIso | -0.66 | -0.52 | +0.41 | -0.04 | -0.00 | +0.07 | -0.03 | -0.07 | +0.07 | -0.06 | 3 |
| S0 | -0.64 | -0.14 | +0.27 | -0.80 | -0.15 | +0.19 | -0.24 | -0.19 | -0.04 | -0.07 | 8 |
| Lrandom | -0.59 | -0.06 | +0.10 | -0.23 | -0.14 | +0.10 | -0.02 | -0.12 | +0.10 | +0.04 | 7 |

- From 1201-1300 every isolated herd has depth 23 (the cap) and IBD 0.95-1.00; captures 0, wild-sired share 0.
- The isolated herds shrink in steps of about one camp's herd: HmaxIso seed 1 about 240 (1101-1600), 150-160
  (1901-2800), 0 from 2868; seed 2 about 230, 150, 80; seed 3 about 175 (1301-2400), 94, 21, 0 from 2732; seed 4 about
  150, 77 from 1501.
- HmaxIso seed 3, last camp: herd 114 in 2720; starvation 53 in 2721 and 53 in 2722 (herd 31, fodder store 1.2 million
  against 12-20 million in 2716-2720); no herd birth from 2723 with 28 goats left; 0 in 2733. The year records do not
  say whether the camp lacked a breeding buck or its does did not conceive.
- HminIso herds are larger than Hmin's before isolation (66.7 against 19.1 in 701-800): open Hmin keeps about 6 goats a
  camp, below the floor of 30, so the floor stopped Hmin's offtake. HminIso is not the minimal rung isolated.
- Herd budget 3201-4000 per year: HmaxIso births 16.5, culled 4.4, other deaths 10.7 (starvation 5.9); HmaxIsoNF 43.6,
  10.9, 28.8 (15.8); LrIso 96.8, 20.8, 66.3 (39.8); HminIso 45.9, 10.1, 34.3 (8.1).
**Prediction scoring:**
- HmaxIso keeps a herd to 4000 in at least 3 of 4 seeds; HmaxIsoNF in fewer, or smaller: **not met** (HmaxIso 2 of 4;
  HmaxIsoNF 3 of 4 with herd 101.2 against 40.1).
- HmaxIso herd R >= 0.40 share 3201-4000 at most 0.005: **met** (0.000; two seeds).
- HmaxIso overlap below S0's on at least 6 of A S B H T M W L: **met** (7 of 8, not L; two seeds; C overlap also fell, 0.84
  to 0.46).
- LrIso overlap at least 0.15 below Lrandom's on each of A S B H W: **met** (0.47, 0.49, 0.28, 0.38, 0.33 below).
- HminIso has lost its herd by 4000 in at least 3 of 4 seeds: **not met** (1 of 4; the floor changed the arm, above).
- In every isolated arm with a herd, C overlap above the lowest of A S B H T M W: **met** (4 of 4).
4 of 6 met.

## [RESULTS 2026-11-12] Immigration: hunted wild goats swapped into the local wild at 1, 4 and 10% a year (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/imm/logs --list tools/imm.jsonl` at 3c2002d; 16 of 16
exit 0. Rate 0: results/settle S0 (run before 2def6a7, so no wildHerdShare), results/ladder WT2. Means over seeds;
overlap pooled over seeds (scratchpad imm_tab.py, imm_out.txt). Wild gene means from the year records' whole-population
and herd means.

| arm | years | herd | wild | immigrants/yr | wildHerdShare | wildAnyHerd | captures/yr | depth | IBD |
|---|---|---|---|---|---|---|---|---|---|
| S0 | 3201-4000 | 242.3 | 456.9 | 0 | - | - | 7.71 | 15.34 | 0.948 |
| I01 | 401-500 | 64.5 | 494.8 | 2.4 | 0.39 | 0.74 | 11.96 | 1.98 | 0.182 |
| I01 | 801-900 | 216.1 | 463.4 | 2.4 | 0.15 | 0.95 | 8.15 | 10.00 | 0.806 |
| I01 | 1501-1600 | 244.0 | 463.2 | 2.4 | 0.06 | 0.95 | 7.23 | 14.65 | 0.864 |
| I01 | 3201-4000 | 246.6 | 460.1 | 2.4 | 0.05 | 0.95 | 6.86 | 15.17 | 0.869 |
| I04 | 401-500 | 64.9 | 506.2 | 10.1 | 0.33 | 0.69 | 11.81 | 2.02 | 0.156 |
| I04 | 801-900 | 225.8 | 456.9 | 9.5 | 0.06 | 0.90 | 7.01 | 9.76 | 0.794 |
| I04 | 1501-1600 | 242.3 | 459.8 | 9.5 | 0.03 | 0.90 | 5.56 | 14.67 | 0.858 |
| I04 | 3201-4000 | 248.1 | 459.4 | 9.5 | 0.03 | 0.90 | 5.73 | 14.88 | 0.912 |
| I10 | 401-500 | 62.8 | 506.3 | 25.2 | 0.25 | 0.61 | 11.78 | 1.96 | 0.198 |
| I10 | 801-900 | 221.2 | 460.4 | 24.2 | 0.04 | 0.78 | 5.41 | 11.42 | 0.784 |
| I10 | 1501-1600 | 243.3 | 459.9 | 24.0 | 0.02 | 0.78 | 4.89 | 14.48 | 0.848 |
| I10 | 3201-4000 | 242.3 | 462.5 | 24.1 | 0.02 | 0.78 | 5.09 | 14.69 | 0.892 |

Wild gene means, 3201-4000 (WT2, WT2I04: whole population, no herds):

| arm | R | A | S | B | H | T | M | W | L | C |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 0.706 | 0.835 | 0.117 | 0.877 | 0.845 | 0.281 | 0.576 | 0.782 | 0.363 | 0.527 |
| I01 | 0.725 | 0.836 | 0.114 | 0.872 | 0.837 | 0.261 | 0.678 | 0.785 | 0.451 | 0.485 |
| I04 | 0.764 | 0.838 | 0.130 | 0.869 | 0.854 | 0.266 | 0.691 | 0.767 | 0.460 | 0.481 |
| I10 | 0.793 | 0.843 | 0.136 | 0.870 | 0.855 | 0.271 | 0.699 | 0.762 | 0.469 | 0.482 |
| WT2 | 0.832 | 0.847 | 0.110 | 0.880 | 0.824 | 0.268 | 0.698 | 0.719 | 0.543 | 0.545 |
| WT2I04 | 0.833 | 0.847 | 0.130 | 0.885 | 0.853 | 0.270 | 0.711 | 0.759 | 0.477 | 0.479 |

Pool gene means (39faab7): R 0.837 A 0.845 S 0.149 B 0.883 H 0.858 T 0.265 M 0.705 W 0.766 L 0.479 C 0.480.

Herd-wild overlap and gene gaps (herd minus wild), 3201-4000:

| arm | | R | A | S | B | H | T | M | W | L | C | herd R>=0.40 / n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | overlap | 0.02 | 0.59 | 0.34 | 0.03 | 0.45 | 0.35 | 0.43 | 0.48 | 0.78 | 0.84 | 0.011 |
| I01 | overlap | 0.02 | 0.51 | 0.46 | 0.03 | 0.62 | 0.29 | 0.38 | 0.80 | 0.80 | 0.83 | 0.010 |
| I04 | overlap | 0.02 | 0.37 | 0.31 | 0.02 | 0.65 | 0.16 | 0.24 | 0.89 | 0.53 | 0.74 | 0.007 |
| I10 | overlap | 0.02 | 0.49 | 0.49 | 0.02 | 0.50 | 0.24 | 0.21 | 0.60 | 0.91 | 0.88 | 0.007 |
| S0 | gap | -0.64 | -0.14 | +0.27 | -0.80 | -0.15 | +0.19 | -0.24 | -0.19 | -0.04 | -0.07 | 8 |
| I01 | gap | -0.66 | -0.15 | +0.12 | -0.80 | -0.15 | +0.21 | -0.25 | -0.05 | -0.07 | -0.00 | 7 |
| I04 | gap | -0.70 | -0.21 | +0.25 | -0.80 | -0.10 | +0.24 | -0.33 | -0.03 | -0.17 | -0.07 | 7 |
| I10 | gap | -0.73 | -0.17 | +0.15 | -0.80 | -0.16 | +0.23 | -0.38 | -0.20 | +0.02 | -0.03 | 8 |

- Per seed 3201-4000, herd / wildHerdShare / wild R: I01 243/0.05/0.729, 245/0.04/0.724, 256/0.05/0.711, 242/0.05/0.737;
  I04 246/0.03/0.766, 248/0.04/0.763, 252/0.03/0.757, 246/0.03/0.772; I10 238/0.02/0.795, 230/0.02/0.794,
  252/0.02/0.789, 249/0.02/0.794.
- Herd budget 3201-4000 per year: S0 births 100.3, captures 7.7, culled 26.3, other deaths 65.0, escaped 16.7; I01 100.7,
  6.9, 26.8, 65.4, 15.4; I04 99.4, 5.7, 26.8, 64.1, 14.3; I10 106.8, 5.1, 26.4, 71.7, 13.8.
- No rate-0 run records wildHerdShare after year 600 (S0 seed 1, 500-599: 0.59, depth check of 2def6a7), so the
  wildHerdShare fall cannot be separated from what rate 0 would do over the same years.
**Prediction scoring:**
- wildHerdShare 3201-4000 I01 > I04 > I10 and I10 below half of I01: **met** (0.049, 0.033, 0.021).
- Wild R rises with the rate and I10 within 0.05 of 0.832: **met** (0.725, 0.764, 0.793; I10 0.039 below).
- I10 overlap below S0's on at least 5 of A S B H T M W L: **not met** (4: A B T M).
- Herd within 10% of 242.3 at every rate: **met** (246.6, 248.1, 242.3).
- WT2I04 whole-population means within 0.03 of WT2's on every gene: **not met** (W +0.040, L -0.066, C -0.066; WT2's
  own C mean moves 0.383-0.545 between windows).
3 of 5 met.

## [RESULTS 2026-11-12] Diagnostic: why the last isolated camp of HmaxIso seed 3 stopped breeding (raw)
**Question:** Chris (2026-11-12) asked for this check after the isolated-herd results: HmaxIso seed 3's last camp had no
herd birth from 2723 with 28 goats left. Was that from no breeding buck, or from does that would not conceive? A single
rerun of a saved run, not a new condition, so not pre-registered.
**Run:** `cpuslot submit --tag animal-domestication --out <scratchpad>/diag/logs --list <scratchpad>/diag/run.jsonl`
(scratchpad diag_collapse.mjs: HmaxIso settings, seed 3, 2735 years, code at 92efedf, src unchanged since ce87c7b).
From year 2690 the script reads each camp's herd once a day without drawing random numbers: adult does and bucks
(age >= breedAge), kids, condition (reserve E over its cap), the doe-days in season blocked by size or condition, the
doe-days in heat, and those with an adult herd buck within one cell. The rerun's year records match
results/iso/HmaxIso_seed3.json in 2735 of 2735 years. Its conception counter is broken (0 every year while herd births
continue) and is not used.
**Results** (camp 1, the only camp with a herd from before 2690; daily means over the year):
- 2690-2720: adult does 21.0, adult bucks 39.6 (bucks 0.99 to 5.6 times the does, year by year). Every doe-day in
  heat had an adult herd buck within one cell (for example 2716: 40 of 40; 2720: 20 of 20). No in-season doe-day was
  blocked by size; doe-days blocked by condition ranged 0-628 a year.
- Through the crash:

| year | adult does | adult bucks | kids | doe condition | buck condition |
|---|---|---|---|---|---|
| 2716 | 28.4 | 56.3 | 46.2 | 0.65 | 0.97 |
| 2720 | 26.4 | 40.2 | 42.8 | 0.76 | 0.99 |
| 2721 | 31.5 | 43.7 | 54.1 | 0.56 | 0.95 |
| 2722 | 1.1 | 34.7 | 2.5 | 0.12 | 0.83 |
| 2723 | 0.0 | 30.1 | 0.0 | - | 0.99 |
| 2724 | 0.0 | 27.1 | 0.0 | - | 0.99 |

- From 2723 the herd was all adult bucks (ages 3.7-9.6 at the end of 2723), and none younger. The last one died in 2733.

## [PRE-REGISTERED 2026-11-12] New husbandry: spare bucks eaten, fodder rationed and budgeted, milk by condition
**Question:** Chris (2026-11-12), after the collapse diagnostic (does starved while bucks survived): "does shouldn't be
dying of starvation while bucks are healthy ... bucks should be the only offtake if they are outnumbering does";
"fodder should just be rationed and prioritized"; "milk by condition, and cull does before feeding them over winter";
"budget fodder only for breeding does and young". With the four rules on, does the reference culture still keep a
herd, open and isolated, how large, does herd starvation go, and do herd and wild separate as far as before?
**Settings:** code of 077e653 + this entry. The four switches (params.js, MODEL.md C28, C57, C61; all 0 by default;
with all four off, S0 seed 1 reproduces results/settle for 600 years, 0 of 600 year records and 0 histogram rows
differ): surplusCull 1 with insuranceBucks 2, fodderRation 1, winterCull 1, milkCondition 0.5 (my placeholder, not yet
set with Chris). tools/husb.json (jobs tools/husb.jsonl):
- HmaxH: the reference culture (results/settle S0) with the four rules.
- HmaxIsoH: the isolated reference culture (results/iso HmaxIso: captures and wild sires stopped from 800, exchangeN 0,
  cullFloor 30) with the four rules.
Controls already run on the same base and seeds: results/settle S0, results/iso HmaxIso. 4 seeds, 4000 years (8 runs).
**Method:** `cpuslot submit --tag animal-domestication --out results/husb/logs --list tools/husb.jsonl`. Means over
seeds in 401-500, 801-900, 1201-1300, 1501-1600, 3201-4000: herd size, and the last year with a herd per seed; the herd's
yearly budget (births, culled with its surplus-buck and winter-cull parts, starvation, other deaths, captures); milk;
gene gaps, breadth (R A S B H T M W L with abs(gap) >= 0.10), herd-wild overlap per gene (as in the isolation entry,
gene C the drift yardstick), herd share with R >= 0.40, lineage depth, IBD.
Smoke, read before these predictions (scratchpad, all four rules on, one seed, 1200 years): open S0 seed 1 herd 86.6 /
94.0 / 100.4 / 103.2 in 701-800 / 901-1000 / 1001-1100 / 1101-1200 (S0 199.1 / 213.4 / 237.8 / 237.2), herd starvation
0 in every century from 401, culled 84.3 a year in 1101-1200 (surplus bucks 21.7, winter cull 55.9); isolated seed 3 herd
95.1 / 71.7 / 73.2 / 78.7 (HmaxIso 209.7 / 230.1 / 233.4 / 250.5), starvation 0, one of its three camps without a herd by
1100.
**Prediction** (written before any 4000-year run with the rules):
- HmaxH keeps a herd to year 4000 in 4 of 4 seeds, with a 3201-4000 herd between 60 and 200 (S0 242.3).
- HmaxH herd starvation in 3201-4000 is below 5 a year (S0 seed 1: 45).
- HmaxIsoH keeps a herd to year 4000 in at least 3 of 4 seeds (HmaxIso 2 of 4).
- HmaxH overlap in 3201-4000 is below S0's on at least 5 of the 8 genes A S B H T M W L.
- HmaxH breadth in 3201-4000 is 8 or more (S0 8).
- In each arm with a herd in 3201-4000, C overlap is above the lowest overlap among A S B H T M W.

## [RESULTS 2026-11-12] Diagnostic: how many bucks the old-husbandry herds carried (raw)
**Question:** Chris (2026-11-12): "old herd numbers might have been inflated by old bucks right?" Not pre-registered: a
rerun of two saved controls with the per-camp logger, read-only.
**Run:** scratchpad diag_collapse.mjs (logs each camp's herd daily from year 1100; draws no random numbers) at 014d575,
1200 years, through cpuslot: S0 seed 1 (results/settle) and HmaxIso seed 3 (results/iso), the four new husbandry
switches off; against the smoke runs with all four on (pre-registration entry above). Per camp-year, 1101-1200, daily
means:

| run | herd goats | adult does | adult bucks | under 1 year | doe condition | buck condition | herd births a year | herd starvation a year |
|---|---|---|---|---|---|---|---|---|
| S0 seed 1, old | 86.0 | 26.1 | 31.1 | 25.4 | 0.79 | 0.96 | 94.6 | 33.3 |
| S0 seed 1, new | 44.0 | 18.4 | 2.3 | 20.8 | 0.97 | 0.98 | 121.0 | 0 |
| HmaxIso seed 3, old | 89.1 | 21.0 | 33.4 | 30.8 | 0.71 | 0.96 | 125.8 | 52.0 |
| HmaxIso seed 3, new | 50.9 | 19.9 | 2.6 | 26.1 | 0.87 | 0.99 | 107.5 | 0 |

- Adult bucks (males at breeding age) median age at year end 4.8 in both old runs, 3.9 and 4.5 in the new.
- Old-husbandry herd starvation 1101-1200 by class, a year: S0 pregnant or nursing does 19.1, kids 13.8, bucks 0.4;
  HmaxIso pregnant or nursing does 29.0, kids 22.7, bucks 0.2.
- Condition is reserve over reserve cap, averaged over goats and days.

## [RESULTS 2026-11-12] New husbandry: spare bucks eaten, fodder rationed and budgeted, milk by condition (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/husb/logs --list tools/husb.jsonl` at 014d575; 8 of 8
exit 0, 2548-2891 s each. Controls results/settle S0 and results/iso HmaxIso. Scratchpad husb_tab.py, husb_out.txt.
Window means over seeds; gaps, depth and IBD over the seeds with a herd in the window; overlap pooled over seeds, from
the years in which that seed has a herd (wild goats of a seed with no herd that year left out: for HmaxIso 3201-4000 this
gives S 0.02 T 0.14 M 0.31 W 0.42 L 0.84 C 0.40, against 0.03 0.22 0.26 0.46 0.83 0.46 in the isolation entry, which
pooled the wild of all four seeds; S0's row is the same either way).

Herd, and the herd's yearly budget, 3201-4000:

| arm | 401-500 | 801-900 | 1201-1300 | 1501-1600 | 3201-4000 | per seed 3201-4000 | last year with a herd |
|---|---|---|---|---|---|---|---|
| HmaxH | 48.9 | 93.8 | 103.6 | 104.4 | 104.3 | 103, 102, 103, 110 | 3999 in all |
| S0 | 65.2 | 220.1 | 236.4 | 236.2 | 242.3 | 243, 241, 249, 236 | 3999 in all |
| HmaxIsoH | 53.8 | 83.3 | 80.4 | 86.1 | 95.4 | 137, 0, 94, 151 | 3999, 1009, 3999, 3999 |
| HmaxIso | 73.5 | 219.1 | 209.6 | 184.6 | 40.1 | 0, 81, 0, 80 | 2868, 3999, 2732, 3999 |

| arm, 3201-4000 | births | culled (surplus bucks, winter cull) | starvation | other deaths | captures | milk |
|---|---|---|---|---|---|---|
| HmaxH | 122.4 | 86.0 (23.7, 56.2) | 0.0 | 19.6 | 14.8 | 9.20M |
| S0 | 100.3 | 26.3 | 34.2 | 30.8 | 7.7 | 7.63M |
| HmaxIsoH | 152.7 | 127.2 (38.9, 83.5) | 0.0 | 20.3 | 0 | 9.37M |
| HmaxIso | 16.5 | 4.4 | 5.9 | 4.8 | 0 | 1.36M |

Herd starvation is 0.0 in every window of both new arms.

Gene gaps (herd minus wild) and breadth n, overlap, herd R >= 0.40 share, lineage depth, IBD, 3201-4000:

| arm | R | A | S | B | H | T | M | W | L | C | n | depth | IBD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HmaxH gap | -0.36 | -0.01 | +0.02 | -0.04 | -0.04 | +0.23 | -0.01 | -0.00 | +0.06 | +0.00 | 2 | 3.8 | 0.88 |
| S0 gap | -0.64 | -0.14 | +0.27 | -0.80 | -0.15 | +0.19 | -0.24 | -0.19 | -0.04 | -0.07 | 8 | 15.3 | 0.95 |
| HmaxIsoH gap | -0.65 | -0.19 | +0.37 | -0.46 | -0.27 | +0.61 | -0.10 | -0.25 | +0.27 | +0.07 | 8 | 23.0 | 1.00 |
| HmaxIso gap | -0.76 | -0.37 | +0.37 | -0.81 | -0.49 | +0.23 | -0.21 | -0.36 | -0.01 | +0.02 | 8 | 23.0 | 1.00 |

| arm, overlap | R | A | S | B | H | T | M | W | L | C | R>=0.40 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HmaxH | 0.22 | 0.93 | 0.91 | 0.78 | 0.86 | 0.54 | 0.92 | 0.96 | 0.86 | 0.95 | 0.351 |
| S0 | 0.02 | 0.59 | 0.34 | 0.03 | 0.45 | 0.35 | 0.43 | 0.48 | 0.78 | 0.84 | 0.011 |
| HmaxIsoH (seeds 1, 3, 4) | 0.00 | 0.33 | 0.13 | 0.05 | 0.29 | 0.01 | 0.72 | 0.38 | 0.38 | 0.73 | 0.000 |
| HmaxIso (seeds 2, 4) | 0.00 | 0.09 | 0.02 | 0.00 | 0.01 | 0.14 | 0.31 | 0.42 | 0.84 | 0.40 | 0.000 |

- HmaxH's herd stays wild-like at every window: herd R >= 0.40 share 0.54 in 801-900, 0.33, 0.23, 0.35 (S0 0.010-0.013
  from 801); breadth 2 in every window from 801 (S0 3, 5, 5, 8).
- Year-record means over the years with a herd, 3201-4000, HmaxH against S0: captures 14.8 against 7.7 a year;
  generations since capture on the maternal line (herdGSC) 6.1 against 31.9; wild-sired share 0.017 against 0.002;
  herd goats that escaped 31.6 against 16.7, lost to the wild (runOffLost) 16.4 against 6.8, rejoined 34.7 against 33.7;
  sires per camp 1.84 against 1.41. herdTarget is 1e9 in both (captures are not gated by herd size).
- HmaxIsoH seed 2 lost its herd in 1009 (herd 42.9 in 801-900, the lowest of the four seeds); the year records do not
  show why.
**Prediction scoring:**
- HmaxH keeps a herd to 4000 in 4 of 4 seeds, 3201-4000 herd between 60 and 200: **met** (4 of 4; 104.3).
- HmaxH herd starvation 3201-4000 below 5 a year: **met** (0.0).
- HmaxIsoH keeps a herd to 4000 in at least 3 of 4 seeds: **met** (3 of 4).
- HmaxH overlap below S0's on at least 5 of A S B H T M W L: **not met** (0 of 8; above S0's on all 8).
- HmaxH breadth 3201-4000 is 8 or more: **not met** (2).
- In each arm with a herd, C overlap above the lowest of A S B H T M W: **met** (HmaxH 0.95 against T 0.54; HmaxIsoH 0.73
  against T 0.01).
4 of 6 met.

## [PRE-REGISTERED 2026-11-12] Which new husbandry rule stops the open herd separating, and where its gene flow comes from
**Question:** Chris (2026-11-12), on the new husbandry results (entry above: the open herd HmaxH keeps a herd of 104
with no starvation but separates from the wild on 2 genes, not 8): "want to ablate the recent changes and find what
ruined our open results? what is driving the gene flow? where are the new captures and escapes coming from ... i'm
suspicious of the winter cull." Which of the four rules does it, and what carries wild genes into the herd: captures
of wild goats, recaptures of the herd's own escapees, or who the culls take?
**Settings:** code of the commit registering this entry (18ad5ab + this entry; tools/trace_flow.mjs new, reads the
run only). tools/husbablate.json (jobs tools/husbablate.jsonl), the open reference culture HmaxH (tools/husb.json) with:
- noWC: winter cull off (surplus cull, rationing and milk by condition on).
- noSC: surplus-buck cull off.
- noFR: fodder rationing off.
- noMC: milk by condition off.
- WConly: the reference culture S0 with the winter cull alone.
4 seeds, 1600 years (20 runs). Controls: years 1-1600 of results/husb HmaxH (all four on) and results/settle S0 (all
off), same seeds (the runs are deterministic, so their first 1600 years are what a 1600-year run gives).
Trace (tools/trace_flow.mjs, logs from year 400; smoke: HmaxH seed 1 for 430 years reproduces results/husb, 0 of 430
year records differ; its captures, culls and herd births equal the year records; it counts 497 of the 504 escapes,
missing goats taken and lost the same day): HmaxH seed 1 and S0 seed 1, 1600 years. Per year: captures split into
orphans (the nursing kid of a doe just hunted) and other captures, recaptures of goats that had escaped the herd, wild
goats with herd-born ancestry, and their age class, R and fear of humans; escapes by origin (captured themselves or
herd-born), age and R; each cull's goats (offtake, surplus bucks, winter cull) by class (under a year, doe, buck) and
origin; herd starvation by class; the herd's daily share of goats captured themselves, and R of captured and herd-born.
**Method:** `cpuslot submit --tag animal-domestication --out results/husbablate/logs --list tools/husbablate.jsonl`; the
two traces in the same way (results/husbablate/trace_*.json). Scratchpad husb_tab.py, windows 801-900 and 1501-1600:
herd, budget (births, culls, starvation, captures, escapes, lost run-offs), gene gaps and breadth, overlap per gene, herd
share with R >= 0.40, lineage depth. Controls in 1501-1600: S0 R >= 0.40 share 0.013, breadth 5, captures 7.6, escapes
16.7; HmaxH 0.231, 2, 12.9, 25.4.
**Prediction** (written before any ablation or trace run):
- noWC separates like S0: in 1501-1600 its herd R >= 0.40 share is 0.05 or less and its breadth 4 or more.
- WConly separates like HmaxH: R >= 0.40 share 0.15 or more, breadth 3 or less.
- noSC, noFR and noMC each keep R >= 0.40 share at 0.15 or more (switching any one of them off does not restore
  separation).
- Captures a year in 1501-1600: noWC within 2 of S0's 7.6; WConly 11 or more.
- In the HmaxH trace, 1501-1600, goats under a year are at least 70% of the winter cull.

## [RESULTS 2026-11-12] Which new husbandry rule stops the open herd separating, and where its gene flow comes from (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/husbablate/logs --list tools/husbablate.jsonl` and
tools/husbablate_trace.jsonl at bcfc3c9; 22 of 22 exit 0. Both traces reproduce their saved runs (0 of 1600 year
records differ on shared fields). Scratchpad husb_tab.py (ablate_out.txt), trace_tab.mjs (trace_out.txt).

Means over 4 seeds, 1501-1600 (801-900 in ablate_out.txt):

| arm | herd | births | culled (surplus, winter) | starvation | captures | escapes | lost run-offs | R gap | B gap | breadth | herd R >= 0.40 | depth |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 (all off) | 236.2 | 100.2 | 25.2 | 35.8 | 7.6 | 16.7 | 6.9 | -0.64 | -0.79 | 5 | 0.013 | 15.2 |
| HmaxH (all on) | 104.4 | 122.4 | 90.2 (26.4, 57.6) | 0.0 | 12.9 | 25.4 | 12.7 | -0.43 | -0.06 | 2 | 0.231 | 4.2 |
| noWC | 231.8 | 216.2 | 88.4 (79.8, 0) | 52.4 | 10.0 | 30.4 | 12.4 | -0.54 | -0.04 | 4 | 0.027 | 11.4 |
| noSC | 129.6 | 152.1 | 108.6 (0, 99.8) | 0.0 | 13.8 | 32.2 | 16.0 | -0.43 | -0.25 | 4 | 0.209 | 4.2 |
| noFR | 102.9 | 115.1 | 79.2 (21.6, 51.5) | 0.0 | 15.6 | 32.7 | 17.3 | -0.34 | -0.05 | 2 | 0.398 | 3.3 |
| noMC | 106.3 | 126.6 | 95.0 (31.2, 58.0) | 0.0 | 12.4 | 24.6 | 12.5 | -0.43 | -0.02 | 2 | 0.241 | 4.8 |
| WConly | 132.3 | 157.5 | 117.7 (0, 108.4) | 0.2 | 11.6 | 24.6 | 11.9 | -0.50 | -0.26 | 4 | 0.155 | 6.0 |

Genes over 0.10 in 1501-1600: S0 R S B H T; noWC R S T M (S +0.10); noSC R B T L; WConly R B T L; HmaxH, noFR, noMC R T.

Traces, seed 1 (a year; R is the trait value; herd R the daily mean):

| window | run | herd | herd R | captures (R) | of them recaptured escapees / wild with herd ancestry / orphans | escapes (R) | culled (R) | starved (R) | herd share captured themselves | kids born to captured dams |
|---|---|---|---|---|---|---|---|---|---|---|
| 501-600 | S0 | – | 0.33 | 19.4 (0.46) | – | 56.1 (0.40) | 17.7 (0.32) | 21.8 (0.27) | – | – |
| 501-600 | HmaxH | – | 0.64 | 14.9 (0.67) | – | 34.8 (0.66) | 27.0 (0.64) | 0 | – | – |
| 801-900 | S0 | 235.3 | 0.11 | 7.6 (0.46) | 3.0 / 7.0 / 2.1 | 20.1 (0.24) | 23.3 (0.11) | 37.2 (0.11) | 0.036 | 4.7 |
| 801-900 | HmaxH | 106.2 | 0.52 | 18.0 (0.59) | 8.6 / 15.6 / 4.8 | 40.9 (0.56) | 45.6 (0.52) | 0 | 0.182 | 22.3 |
| 1501-1600 | S0 | 258.6 | 0.06 | 6.9 (0.56) | 2.0 / 6.3 / 2.1 | 14.3 (0.29) | 25.1 (0.07) | 36.1 (0.05) | 0.027 | 3.6 |
| 1501-1600 | HmaxH | 137.7 | 0.27 | 12.6 (0.54) | 4.4 / 11.5 / 3.6 | 23.8 (0.42) | 98.2 (0.26) | 0 | 0.083 | 13.9 |

- HmaxH 1501-1600 culls by kind: offtake 6.3 (kids 5.4), surplus 28.4 (kids 28.3), winter 63.4 (kids 49.4, does 14.1);
  goats captured themselves 3.4 of the winter cull. S0: offtake 25.1 (kids 14.3, does 3.3, bucks 7.5); starvation 36.1
  (kids 14.0, does 21.6, bucks 0.5).
- Escapes: S0 1501-1600 4.9 captured themselves, 9.5 herd-born (kids 4.7); HmaxH 6.5 and 17.3 (kids 10.6).
- Herd R >= 0.40 share in 1501-1600 against herd size, the seven arms: S0 236 / 0.013, noWC 232 / 0.027, WConly 132 /
  0.155, noSC 130 / 0.209, HmaxH 104 / 0.231, noMC 106 / 0.241, noFR 103 / 0.398.
- noWC: herd starvation 52.4 a year (S0 35.8); births 216.2 (S0 100.2), surplus bucks 79.8.
**Prediction scoring:**
- noWC separates like S0, R >= 0.40 share at most 0.05 and breadth 4 or more: **met** (0.027; 4).
- WConly separates like HmaxH, R >= 0.40 share 0.15 or more and breadth 3 or less: **not met** (0.155, but breadth 4).
- noSC, noFR and noMC each keep R >= 0.40 share at 0.15 or more: **met** (0.209, 0.398, 0.241).
- Captures 1501-1600: noWC within 2 of S0's 7.6, WConly 11 or more: **not met** (noWC 10.0; WConly 11.6).
- HmaxH trace 1501-1600, goats under a year at least 70% of the winter cull: **met** (49.4 of 63.4, 78%).
3 of 5 met.

## [PRE-REGISTERED 2026-11-13] Winter-cull budget: does a less conservative winter cull keep a bigger, more separated herd?
**Question:** Chris (2026-11-13), on the ablation above: "in the winter cull we cull to some level we have decided is
survivable. my guess is this is too conservative. this creates a herd that is smaller than the herders can handle ...
we should also track how the different culls are interacting. are we taking 10% still after the winter cull?" And on
captures: "less herd goats means more capacity for wild goats which might mean more opportunity for hunters which means
more captures." The winter cull budgets a full ration (provision × size^0.75) for every lean day for each breeding doe
and each goat under a year, and kills until the fodder store covers it; its kills, and the surplus cull's, count
against the year's 10% offtake. In 1501-1600 HmaxH culls 90.2 goats a year from a herd of 104 (offtake 6.2, surplus
26.4, winter 57.6); noWC, on the same fodder, keeps 232 and loses 52.4 to starvation. Hunting kills rise as the herd
shrinks (S0 25.0 a year, noWC 27.6, WConly 33.9, HmaxH 36.5, noFR 43.1) and captures stay near 0.31-0.36 of hunting
kills in every arm (year records, 4 seeds), so captures follow hunting encounters; whether the wild come closer to
camp has not been measured.
**Settings:** code of the commit registering this entry. New parameter winterBudget (default 1): the share of a full
ration the winter cull budgets per fed goat; at 1 the arithmetic is unchanged bit for bit. New year-record counters,
no random draws: offtakeDue (offtake draws due), offtakeCredited (of them cancelled by surplus and winter culls),
cullTally (each cull's goats: kids under a year, breeding does, breeding bucks, other, and goats captured themselves),
huntTries (hunting attempts spent, i.e. with a wild goat in the hunter's 3×3), wildNearCamp (mean wild goats within
herdRange of a camp, per camp-day). Check: HmaxH seed 1 and WConly seed 1, 600 years, against results/husb and
results/husbablate: 0 of 600 year records differ on any saved field, and R histograms are identical; counters add up
(offtake + surplus + winter tallies = culledHerd). Smoke: Wb25 seed 1, 600 years, differs from Wb100 in 132 of
600 year records, from year 468 (the first winter cull; a 450-year smoke showed 0 differences because no winter cull
had fired yet, so it could not fail); 501-600 herd 62.2 against 66.2, winter cull 0.0 against 4.0 a year.
tools/winterbudget.json (jobs tools/winterbudget.jsonl): HmaxH (tools/husb.json) at winterBudget 1 (Wb100, a rerun for
the counters), 0.75 (Wb75), 0.5 (Wb50), 0.25 (Wb25); noWC (winter cull off) and S0 (all four rules off) rerun for the
counters. 4 seeds, 1600 years, 24 runs. Wb100 and noWC must reproduce results/husb and results/husbablate.
**Method:** `cpuslot submit --tag animal-domestication --out results/winterbudget/logs --list tools/winterbudget.jsonl`.
Scratchpad husb_tab.py (windows 801-900, 1501-1600: herd, culls, starvation, captures, escapes, gaps, breadth, overlap,
herd R >= 0.40 share) and a counter table per arm (offtake due and credited, each cull by class, hunting attempts, wild
near camp, captures per attempt).
**Prediction** (years 1501-1600, 4 seeds; written before any sweep run, before the smoke finished, and left as written):
- Herd rises as the budget falls: Wb100 < Wb75 < Wb50 < Wb25, and Wb25 over 170.
- Herd starvation rises as the budget falls: Wb75 under 5 a year, Wb25 over 10.
- The herd R >= 0.40 share falls as the herd grows: Wb25 at 0.08 or less, and breadth 4 or more.
- Chris's capture path: wild goats near camp and hunting attempts are each at least 10% higher in Wb100 than in S0;
  across the six arms captures a year rise as the herd shrinks (rank correlation with herd -0.6 or stronger); captures
  per hunting attempt differ by no more than 20% between Wb100 and S0.
- Culls: in Wb100 at least 80% of the offtake draws due are cancelled by surplus and winter credit, and goats under a
  year are at least 60% of all goats culled.

## [RESULTS 2026-11-13] Winter-cull budget: does a less conservative winter cull keep a bigger, more separated herd? (raw)
**Run:** `cpuslot submit --tag animal-domestication --out results/winterbudget/logs --list tools/winterbudget.jsonl` at
c42c44f; 24 of 24 exit 0. Wb100, noWC and S0 reproduce results/husb HmaxH, results/husbablate noWC and results/settle
S0: 0 of 1600 year records differ, every seed. Tables: tools/wb_tab.py (results/winterbudget/counters.txt) and scratchpad
husb_tab.py (results/winterbudget/tab.txt; 801-900 there too).

Means over 4 seeds, 1501-1600:

| arm | herd | births | culled (offtake, surplus, winter) | starvation | captures | escapes | R gap | B gap | breadth | herd R >= 0.40 | depth |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 236.2 | 100.2 | 25.2 (25.2, 0, 0) | 35.8 | 7.6 | 16.7 | -0.64 | -0.79 | 5 | 0.013 | 15.2 |
| noWC | 231.8 | 216.2 | 88.4 (8.6, 79.8, 0) | 52.4 | 10.0 | 30.4 | -0.54 | -0.04 | 4 | 0.027 | 11.4 |
| Wb100 | 104.4 | 122.4 | 90.2 (6.3, 26.4, 57.6) | 0.0 | 12.9 | 25.4 | -0.43 | -0.06 | 2 | 0.231 | 4.2 |
| Wb75 | 137.9 | 180.6 | 138.9 (7.3, 41.6, 90.0) | 0.0 | 12.2 | 27.2 | -0.48 | -0.05 | 2 | 0.092 | 6.7 |
| Wb50 | 163.0 | 232.1 | 181.8 (8.2, 58.1, 115.5) | 0.4 | 10.2 | 24.0 | -0.54 | -0.07 | 3 | 0.059 | 8.2 |
| Wb25 | 204.4 | 222.9 | 140.2 (10.4, 50.0, 79.8) | 15.2 | 9.5 | 26.9 | -0.54 | -0.08 | 2 | 0.027 | 11.1 |

Counters, 1501-1600 (a year; cull classes kids under a year / breeding does / breeding bucks / other, and of them goats
captured themselves; hunting attempts are attempts spent with a wild goat in the hunter's 3x3; wild near camp is the
mean wild goats within herdRange of a camp):

| arm | offtake due | of it cancelled by credit | offtake cull | surplus cull | winter cull | hunting attempts | hunting kills | captures per 1000 attempts | wild near camp |
|---|---|---|---|---|---|---|---|---|---|
| S0 | 25.2 | 0.0 | 14.8/3.3/7.1/0; 1.2 | - | - | 236 | 25.0 | 32.3 | 10.94 |
| noWC | 25.3 | 16.7 | 3.5/4.2/0.9/0; 0.6 | 79.5/0/0.3/0; 1.6 | - | 231 | 27.6 | 43.3 | 7.83 |
| Wb100 | 13.3 | 7.0 | 5.3/0.6/0.3/0; 0.7 | 26.2/0/0.2/0; 1.0 | 45.0/12.6/0/0; 3.3 | 326 | 36.5 | 39.4 | 14.68 |
| Wb75 | 17.2 | 9.8 | 6.6/0.4/0.3/0; 0.5 | 41.4/0/0.2/0; 1.0 | 73.8/16.2/0/0; 3.3 | 291 | 34.0 | 42.0 | 11.28 |
| Wb50 | 20.4 | 12.2 | 7.7/0.2/0.3/0; 0.4 | 57.9/0/0.2/0; 0.8 | 94.1/21.3/0/0; 2.8 | 245 | 28.4 | 41.6 | 9.30 |
| Wb25 | 25.1 | 14.7 | 7.5/2.6/0.3/0; 0.5 | 49.8/0/0.2/0; 0.6 | 56.5/23.2/0/0; 2.1 | 219 | 26.2 | 43.5 | 7.41 |

- Genes over 0.10 in 1501-1600: S0 R S B H T; noWC R S T M; Wb100 R T; Wb75 R T; Wb50 R T L; Wb25 R T.
- 801-900: herd Wb100 93.8, Wb75 131.8, Wb50 154.3, Wb25 207.5; herd R >= 0.40 0.536, 0.207, 0.113, 0.029.
**Prediction scoring:**
- Herd rises as the budget falls, Wb25 over 170: **met** (104.4 < 137.9 < 163.0 < 204.4).
- Starvation Wb75 under 5, Wb25 over 10: **met** (0.0; 15.2).
- Wb25 R >= 0.40 share 0.08 or less and breadth 4 or more: **not met** (0.027, but breadth 2).
- Capture path: wild near camp and hunting attempts each at least 10% higher in Wb100 than S0, captures' rank
  correlation with herd -0.6 or stronger, captures per attempt within 20%: **not met** (wild near camp +34%, attempts
  +38%, rank correlation -0.94, but captures per attempt +22%: 39.4 against 32.3 per 1000).
- Wb100: at least 80% of offtake due cancelled, kids at least 60% of all culled: **not met** (53% cancelled; kids 85%).
2 of 5 met.

## [PRE-REGISTERED 2026-11-13] Offtake rate and timing without the surplus and winter culls
**Question:** Chris (2026-11-13): "the surplus cull is far too aggressive. like our winter cull was too conservative.
herder culling was likely opportunisitic ... who do we cull? large male goats that have completed their growth ... we
cull other males, or old does, before they lose size due to starving"; and "our humans are not metabolic. so they don't
have hunger. that is what the fixed rate was meant to simulate." The tooth-seasonality literature found in a search
(abstracts only) points to slaughter through the year with site-specific peaks, not a general pre-winter kill. So: drop
the surplus and winter culls, keep the fixed offtake as the stand-in for hunger, chosen by keep value; vary the rate;
and test a milder lean-season rule, a share of the year's offtake moved to the start of the lean season.
Who the keep value takes (scratchpad probe_offtake.mjs, S0 seed 1, years 501-560, 1004 cull events): adult bucks 553
(keep value -0.24), buck kids 341 (age 302 d, keep -0.29: at the herd's mean adult male size, so no growth to come), old
does 107 (age 9.2 y), yearling males 3, doe kids and yearling does 0. The ranking is Chris's: grown males first, then
old does; the "kids" in the cullTally are mostly males near a year old.
**Settings:** code of the commit registering this entry. New parameters leanPulse (default 0, off) and leanPulseDays
(30): leanPulse of the year's offtake falls in the first leanPulseDays of the lean season and the rest evenly over the
other days (the yearly rate unchanged). New year-record counter herdComp: mean kids, breeding does, breeding bucks,
other per managed camp-day (no random draws). Check: HmaxH seed 1, 600 years, new code against results/winterbudget
Wb100: 0 of 600 year records differ on any saved field; R10 vs P10 seed 1, 600 years: first differ in year 401
(herding from 400). Smoke seen (seed 1, years 501-600): R10 herd 138, herd starvation 0.2 a year, per camp 22.9 kids,
18.7 does, 9.7 bucks, offtake 3.1 kids, 1.4 does, 11.9 bucks a year; P10 herd 188, starvation 2.5, bucks 18.9 of the
offtake.
tools/offtake.json (jobs tools/offtake.jsonl): HmaxH with surplusCull 0 and winterCull 0 (keep-value ranking, fodder
rationed, milk by condition) at offtakeRate 0.1, 0.15, 0.2, 0.3 (R10, R15, R20, R30), and 0.1 and 0.2 with leanPulse
0.3 over 30 days (P10, P20: 3.6x the even rate in that window, 0.76x elsewhere); S0 rerun for herdComp, which must
reproduce results/winterbudget S0. 4 seeds, 1600 years, 28 runs. References: results/winterbudget S0, noWC, Wb100.
**Method:** `cpuslot submit --tag animal-domestication --out results/offtake/logs --list tools/offtake.jsonl`.
Scratchpad husb_tab.py (herd, culls, starvation, captures, escapes, gaps, breadth, herd R >= 0.40 share) and wb_tab.py
counters extended with herdComp, windows 801-900 and 1501-1600.
**Prediction** (years 1501-1600, 4 seeds; written after the smoke, before any sweep run):
- Herd falls as the rate rises: R10 > R15 > R20 > R30.
- Breeding bucks per camp fewer than breeding does in every R and P arm, and the buck:doe ratio falls as the rate rises.
- Grown males first: in R10 buck kids plus breeding bucks are at least 70% of offtake kills, does at most 20%.
- Herd starvation under 10 a year in R10 (noWC 52.4, S0 35.8).
- Separation without the surplus cull: B gap at -0.3 or below in R10 (S0 -0.79, Wb100 -0.06) and breadth 3 or more.
- Chris's capture path: across S0, R10-R30, P10, P20 captures a year fall as the herd grows (rank correlation with herd
  -0.6 or stronger).
- Timing: P10's herd at least 10% larger than R10's, and P20's than R20's (the smoke shows +36% in seed 1), with herd
  starvation in P10 under 10 a year.

## [RESULTS 2026-11-13] Offtake rate and timing without the surplus and winter culls (raw)
28 runs, all exit 0. S0 rerun reproduces results/winterbudget S0: 0 of 1600 year records differ, all 4 seeds. Tables:
results/offtake/counters.txt (tools/offtake_tab.py), results/offtake/tab.txt (scratchpad husb_tab.py).
Years 1501-1600, 4 seeds, per year (comp: mean per camp-day, kids/does/bucks/other; offtake kills: kids/does/bucks/other):
| arm | herd | starv | culled | offtake kills | comp | buck:doe | capt | R>=0.40 share | breadth | B gap | R gap |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 236.2 | 35.8 | 25.2 | 14.8/3.3/7.1/0 | 26.4/24.9/31.0/3.4 | 1.24 | 7.6 | 0.013 | 5 | -0.79 | -0.64 |
| R10 | 302.9 | 43.4 | 32.4 | 15.8/2.0/14.6/0 | 34.2/33.9/35.9/4.5 | 1.06 | 7.3 | 0.005 | 7 | -0.82 | -0.64 |
| R15 | 303.3 | 49.2 | 50.7 | 25.1/2.9/22.6/0 | 43.7/43.4/19.2/5.8 | 0.44 | 8.5 | 0.005 | 6 | -0.82 | -0.61 |
| R20 | 287.2 | 57.2 | 67.0 | 43.8/4.2/18.9/0 | 50.4/47.2/6.7/6.4 | 0.14 | 9.0 | 0.007 | 6 | -0.67 | -0.59 |
| R30 | 243.5 | 45.7 | 87.9 | 75.4/9.3/3.2/0 | 45.5/43.0/2.8/6.2 | 0.07 | 9.4 | 0.013 | 5 | -0.37 | -0.57 |
| P10 | 294.5 | 39.4 | 32.2 | 14.2/2.9/15.2/0 | 33.3/35.1/33.6/4.3 | 0.96 | 7.8 | 0.007 | 7 | -0.81 | -0.63 |
| P20 | 282.0 | 62.1 | 66.6 | 44.6/3.2/18.8/0 | 50.1/45.0/6.4/6.4 | 0.14 | 9.2 | 0.011 | 4 | -0.61 | -0.59 |
| noWC | 231.8 | 52.4 | 88.4 | (surplus 79.8) | - | - | 10.0 | 0.027 | 4 | -0.04 | -0.54 |
| Wb100 | 104.4 | 0 | 90.2 | (winter 57.6) | - | - | 12.9 | 0.231 | 2 | -0.06 | -0.43 |
Years 801-900: R30 herd 150.0 (seeds 75, 243, 214, 69), R>=0.40 share 0.256, breadth 3; R10 279.3, R15 263.8, R20
250.6, P10 274.6, P20 239.0; herd starvation 29-42 a year in every arm but R30 (11.4). Births a year 1501-1600: R10
138, R15 184, R20 231, R30 229, P10 131, P20 232. Captures vs herd, rank correlation over S0, R and P arms: -0.32
(1501-1600), -0.61 (801-900). The smoke's R10 seed 1, years 501-600, had herd starvation 0.2 a year and 9.7 bucks per
camp; by 801-900 the 4-seed means are 39.4 and 31.3. Herd starvation is not split by sex or age in the year record
(herdKilloff is all causes).
**Predictions:** 2 of 7 met.
- Herd falls as the rate rises, R10 > R15 > R20 > R30: missed (R10 302.9, R15 303.3; then 287.2, 243.5).
- Bucks fewer than does in every R and P arm, ratio falling with rate: missed (R10 1.06; ratio does fall, 1.06, 0.44,
  0.14, 0.07; P10 0.96).
- Grown males first, R10 kids plus bucks >= 70% of offtake, does <= 20%: met (94%, does 6%); the kids slot is not split
  by sex in the record (the probe found doe kids never culled in S0 years 501-560; not checked here).
- R10 herd starvation under 10: missed (43.4).
- R10 B gap -0.3 or below and breadth 3 or more: met (-0.82, breadth 7).
- Captures vs herd rank correlation -0.6 or stronger: missed in 1501-1600 (-0.32; -0.61 in 801-900).
- P10 herd 10% above R10 and P20 above R20, P10 starvation under 10: missed (294.5 vs 302.9; 282.0 vs 287.2; 39.4).

## [PRE-REGISTERED 2026-11-13] Who starves in the herd without the winter cull
**Question:** Chris, on the offtake sweep above (herd starvation 40-60 a year in every arm without the winter cull):
yes to splitting herd starvation by sex and age and tracing who starves in R15. His standing objection (2026-11-12):
"does shouldn't be dying of starvation while bucks are healthy." Known from saved records: unweaned herd kids are 5-9
of the 43-49 starving a year (kidDeathCause), so most are weaned; in R15 herd starvation is 0 in every seed to year
500-600, then rises to 36-71 a year by 1000-1100 (4 seeds). fodderRation feeds pregnant or nursing does and goats under
a year first, the rest after. The lean season runs from day 172 to day 28 (months 5-11 and 0 of 30 days).
**Settings:** code of the commit registering this entry. New year-record counters, no random draws: herdStarve (herd
starvation deaths by season, lean or grow, and class: unweaned, weaned under a year, breeding does pregnant or nursing,
dry breeding does, breeding bucks, other) and herdStarveMonth (by 30-day month). Check: R15 seed 1, 600 years, against
results/offtake R15: 0 of 600 year records differ; class and month totals equal herdDeaths.starvation in 600 of 600
years, but that run has no herd starvation, so the add-up check could not fail there; it is repeated on every year of
the runs below.
tools/starve.jsonl: R15, R10 and S0 (tools/offtake.json) rerun with the counters, 4 seeds, 1600 years, 12 runs; each
must reproduce results/offtake on every saved field.
**Method:** `cpuslot submit --tag animal-domestication --out results/starve/logs --list tools/starve.jsonl`. Table of
herdStarve and herdStarveMonth per arm, years 801-900 and 1501-1600.
**Prediction** (years 1501-1600, 4 seeds, written before any run):
- At least 80% of herd starvation falls in the lean season in all three arms, and most of it in the last three lean
  months (months 10, 11, 0).
- R15: weaned goats under a year are the largest class; pregnant or nursing does are under 20% of herd starvation.
- R15 and R10: breeding bucks starve at a higher rate per head than breeding does (fodder goes to does first); S0, with
  no rationing, not.

## [RESULTS 2026-11-13] Who starves in the herd without the winter cull (raw)
12 runs, all exit 0. Every run reproduces results/offtake: 0 of 1600 year records differ, all arms and seeds. Class and
month totals equal herdDeaths.starvation in 1600 of 1600 years in every run (869-1068 years with herd starvation per
run). Table: results/starve/tab.txt (tools/starve_tab.py). Rates per head use herdComp × an estimated camp count
(year-end herd / mean head per camp), so they are approximate.
Years 1501-1600, 4 seeds, herd starvation a year by class (lean / growing season) and share:
| class | R15 | R10 | S0 |
|---|---|---|---|
| total (% lean) | 49.2 (15%) | 43.4 (15%) | 35.8 (52%) |
| unweaned | 0.4 / 8.5, 18% | 0.1 / 5.6, 13% | 0.0 / 0.4, 1% |
| weaned under a year | 0.5 / 5.2, 12% | 0.3 / 6.7, 16% | 11.2 / 3.6, 41% |
| does pregnant or nursing | 5.3 / 19.0, 49% | 4.2 / 16.6, 48% | 7.0 / 12.6, 55% |
| dry does | 1.2 / 8.4, 19% | 1.7 / 6.9, 20% | 0.4 / 0.2, 2% |
| bucks | 0.0 / 0.2, 0% | 0.0 / 0.5, 1% | 0.0 / 0.2, 1% |
| other | 0.0 / 0.4, 1% | 0.0 / 0.8, 2% | 0.0 / 0.2, 1% |
| per head a year, does / bucks | 0.288 / 0.004 | 0.311 / 0.005 | 0.294 / 0.003 |
By 30-day month (lean from day 172 to day 28; growth from day 29): R15 months 0, 1, 2: 5.0, 31.8, 9.3, months 3-9 under
0.3 each, months 10, 11: 0.6, 2.1; R10 4.6, 29.4, 6.9; S0 12.1, 14.0, 2.5, and 5.6 in month 11. Years 801-900 show the
same pattern (R15 40.2, 16% lean, month 1 26.6; does 0.234 per head, bucks 0.015). Rut peaks on day 330 and gestation is
150 days, so does in months 0-2 are mid-gestation; fodderRation feeds only on days with growth 0.
**Predictions:** 0 of 3 met.
- At least 80% in the lean season, most in months 10, 11, 0: missed (15%, 15%, 52%; the peak is month 1, the first
  growing month).
- R15: weaned under a year the largest class, pregnant or nursing does under 20%: missed (does 49%, the largest).
- R15 and R10: bucks starve at a higher rate per head than does: missed (does 0.29-0.31, bucks 0.004-0.005).

## [PRE-REGISTERED 2026-11-13] Spring feeding: the lean-season ration carried into spring
**Question:** The starvation trace above: in R15 herd starvation falls mostly in days 30-59, just after feeding stops
on day 29, on breeding does (half pregnant or nursing), almost never on bucks. A probe (scratchpad probe_spring.mjs,
R15 seed 1, years 1501-1505) found the camp store at 1.4-1.6 million kcal at day 29 and refilling from day 30, standing
veg near camp at 0.0-0.1 of K until about day 80, and herd starvation ending by day 90. Chris: "feeding should continue
until normal grazing starts. i feel maybe we just fix a time"; on the deficit version's small effect, "the herder should
do what they were doing in the lean season still in the spring."
**Settings:** code of 37d7d95 (feedExtend, feedNeed, fodderSpring counter; off by default). feedExtend N: fodderRation
goes on N days past the lean season (days 29 to 28+N), the store rationed to last the window, pregnant or nursing does
and goats under a year first. feedNeed full: each goat wants what it would in the lean season (up to provision ×
size^0.75, to a full reserve); deficit: its upkeep (maintenance, gestation, milk capacity if nursing) less what it grazed
and drank today. Checks: feedExtend 0, R15 seed 1, 600 years, 0 of 600 year records differ from results/offtake. Smoke
(seed 1, 1000 years, deficit before its lactation term counted milk capacity under milkCost made): feedExtend 60 herd
starvation 38.2 vs 45.5 a year in 901-1000, herd 248 vs 289; a 120-day deficit window's spring fodder per camp-day 1,800
(days 30-39), 5,100 (50-69), 290 (80-89), about 0 from day 90. No smoke of feedNeed full.
tools/spring.json (jobs tools/spring.jsonl): R15 rerun (must reproduce results/starve R15 on every saved field), F30,
F60 (full, 30 and 60 days), D60 (deficit, 60 days). 4 seeds, 1600 years, 16 runs.
**Method:** `cpuslot submit --tag animal-domestication --out results/spring/logs --list tools/spring.jsonl`. Tables:
tools/starve_tab.py pattern (herdStarve by class and month), tools/offtake_tab.py counters and herdComp, scratchpad
husb_tab.py separation measures; years 801-900 and 1501-1600.
**Prediction** (years 1501-1600, 4 seeds, written before any sweep run):
- F60 herd starvation at least 25% below R15 (R15 49.2), and F30 between them.
- Starvation in days 30-89 (months 1 and 2) at least 40% lower in F60 than R15.
- Spring fodder a year at least 3 times larger in F60 than in D60.
- Late-lean starvation (months 10, 11, 0) in F60 no more than 2 a year above R15.
- Separation holds: breadth in F60 within 2 of R15 (6) and herd R >= 0.40 share under 0.03.

## [PRE-REGISTERED 2026-11-13] Spring feeding addendum: deficit feeding through the whole growing season (DY)
**Question:** Chris, after the deficit smoke (feeding fell to about 0 by day 90 on its own): "if feeding drops to 0
after 90 just let it drop and pick back up when needed?" DY: R15 with feedNeed deficit and feedExtend 143, the whole
growing season (days 29-171), so feeding stops and restarts with need until the lean ration takes over. The window's
store is rationed to last until the lean season starts, so there is no guard keeping fodder back for winter; this arm
measures whether one is needed.
**Settings:** code of 37d7d95, as in the entry above; tools/spring.json arm DY; jobs tools/spring_dy.jsonl, 4 seeds,
1600 years, plus scratchpad probe_spring.mjs on DY seed 1, years 1601-1605 (store, fodder fed and spring fodder per
camp-day, veg, condition by class, by 10-day block). Submitted after the 16 runs above, in the same queue.
**Prediction** (years 1501-1600, 4 seeds):
- DY within 10% of D60 on herd starvation, spring fodder and herd size (feeding after day 89 near 0).
- In the probe, spring fodder per camp-day under 1,000 in every 10-day block from day 90 to day 171, and the store at
  day 170-179 within 10% of R15's (7.0 million kcal per camp in the R15 seed 1 probe, years 1501-1505).

## [RESULTS 2026-11-13] Spring feeding, with the DY addendum (raw)
20 runs and the DY probe, all exit 0. R15 rerun reproduces results/starve R15: 0 of 1600 year records differ, all
seeds. Tables: results/spring/counters.txt (tools/spring_tab.py), results/spring/tab.txt (scratchpad husb_tab.py);
probe log results/spring/logs/probe_DY.log.
Years 1501-1600, 4 seeds, per year (starvation by month: days 30-89 = months 1-2; late lean = months 10, 11, 0):
| arm | herd | herd starv | days 30-89 | late lean | fodder fed (M kcal) | spring fodder (M) | births | breadth | B gap |
|---|---|---|---|---|---|---|---|---|---|
| R15 | 303.3 | 49.2 | 41.1 | 7.7 | 43.22 | 0 | 333.3 | 6 | -0.82 |
| F30 | 314.9 | 57.4 | 38.4 | 14.9 | 43.66 | 3.80 | 372.3 | 7 | -0.82 |
| F60 | 288.1 | 57.9 | 38.8 | 15.4 | 43.48 | 7.30 | 341.2 | 5 | -0.81 |
| D60 | 307.5 | 47.0 | 33.2 | 12.1 | 43.22 | 2.49 | 356.8 | 9 | -0.82 |
| DY | 304.5 | 47.8 | 36.1 | 11.3 | 43.18 | 2.07 | 337.0 | 7 | -0.82 |
R gap -0.61 to -0.62 in every arm. Years 801-900: herd starvation R15 40.2, F30 40.0, F60 46.3, D60 29.4, DY 39.0.
DY probe (seed 1, years 1601-1605, per camp): spring fodder per camp-day 4,900 (days 30-39), 10,800 (50-69), 4,000
(80-89), 2,400 (90-99), 1,300-1,900 (100-139), 650-820 (140-159), 370 (160-169); store 7.06 million kcal at days
170-179; lean fodder per camp-day rises from 35,000 (days 180-189) to 90,000 (days 340-349). E/cap by class: dry does
0.95 at days 180-249, falling to 0.12 by days 350-9, with 22-42% of them below 0 from day 0 to day 69; breeding bucks
0.72-0.96 all year, never more than 4% below 0.
**Predictions:** 1 of 7 met in full (the DY items each met in part).
- F60 at least 25% below R15, F30 between: missed (F60 57.9, F30 57.4, R15 49.2).
- Days 30-89 at least 40% lower in F60: missed (38.8 vs 41.1).
- Spring fodder F60 at least 3 times D60: missed (2.9 times).
- Late lean in F60 within 2 of R15: missed (15.4 vs 7.7).
- Separation holds, breadth in F60 within 2 of R15 and herd R >= 0.40 share under 0.03: met (F60 breadth 5; herd R >= 0.40 share 0.004-0.005 in every arm).
- DY within 10% of D60 on herd starvation, spring fodder and herd: missed on spring fodder (2.07 vs 2.49, -17%); met
  on starvation (47.8 vs 47.0) and herd (304.5 vs 307.5).
- DY probe: spring fodder under 1,000 per camp-day from day 90 to 171: missed (1,300-2,400 until day 139); store at
  days 170-179 within 10% of R15's 7.0 million: met (7.06).

## [PRE-REGISTERED 2026-11-14] Winter cull at a partial budget, without the surplus cull, bucks included
**Question:** Chris (2026-11-14): "the population grows to capacity and faces food shortages. what would traditional
herders do?" Spring feeding (above) did not cut herd starvation: every arm fed the same 43 million kcal a year, and the
herd stays near 300 with about 16% starving each spring. Raising offtake raised births instead (R20 231 a year, R10
138). The pastoral literature found (search summaries) names moving herds, extra fodder, boom-and-bust losses, and
tracking feed by destocking; pasture across the whole map is near 0.1 of K in late lean, so moving cannot help here.
The winter cull destocks to the fodder store; it ran before only with the surplus cull (Wb50: herd 163, starvation 0.4,
breadth 3, R >= 0.40 share 0.059; Wb100: R share 0.231). Chris asked to cull grown males and old does first, so a new
switch lets the winter cull budget and cut bucks too.
**Settings:** code of the commit registering this entry. New parameter winterCullAll (default 0): 1 = the winter cull
budgets every herd goat and may cut any of them, lowest keep value first; 0 = breeding does and goats under a year only,
as before. Check: Wb100 seed 1, 600 years, against results/winterbudget Wb100: 0 of 600 year records differ, with 424
winter culls in those years. Smoke seen (seed 1, 700 years, years 601-700): W50 herd 156.3, starvation 0.0, winter cull
33.9 kids, 6.0 does, 0 bucks, 0 other a year; W50A herd 146.2, starvation 0.0, winter cull 35.4 kids, 4.6 does, 2.6
bucks, 7.9 other; W50A first differs from W50 in year 577. Herd starvation in R15 starts only after year 600.
tools/wintercull2.json (jobs tools/wintercull2.jsonl): R15 plus winterCull 1 at winterBudget 0.5 with winterCullAll 1
(W50A), 0.25 with winterCullAll 1 (W25A), and 0.5 without (W50). 4 seeds, 1600 years, 12 runs. Reference: results/spring
R15.
**Method:** `cpuslot submit --tag animal-domestication --out results/wintercull2/logs --list tools/wintercull2.jsonl`.
Tables as for the spring sweep (herd, starvation by class and month, culls by class, herdComp) and scratchpad husb_tab.py
separation measures, years 801-900 and 1501-1600.
**Prediction** (years 1501-1600, 4 seeds, written before any sweep run):
- Herd starvation under 5 a year in W50A and W50, under 15 in W25A (R15 49.2).
- Herd between 120 and 200 in W50A, and larger in W25A than in W50A.
- Separation without the surplus cull: B gap at -0.5 or below, herd R >= 0.40 share at 0.05 or less, and breadth 4 or
  more in W50A.
- The winter cull takes bucks: in W50A breeding bucks plus other (yearlings past a year) cut by the winter cull at least
  2 a year, against 0 in W50; goats under a year are still the largest class cut in W50A.

## [RESULTS 2026-11-14] Winter cull at a partial budget, without the surplus cull, bucks included (raw)
12 runs, all exit 0. Tables: results/wintercull2/counters.txt (tools/wintercull2_tab.py), results/wintercull2/tab.txt
(scratchpad husb_tab.py). R15 is results/spring R15.
Years 1501-1600, 4 seeds, per year (herd births and culls from husb_tab; winter cull by class kids/does/bucks/other):
| arm | herd | herd starv | herd births | culled | winter cull | herd comp k/d/b/o | capt | breadth | B gap | R gap | R>=0.40 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R15 | 303.3 | 49.2 | 184.4 | 50.7 | 0 | 43.7/43.4/19.2/5.8 | 8.5 | 6 | -0.82 | -0.61 | 0.005 |
| W50A | 199.2 | 2.4 | 230.8 | 166.6 | 120.6/16.4/2.0/6.6 | 39.8/34.2/2.8/4.0 | 12.1 | 6 | -0.61 | -0.55 | 0.054 |
| W25A | 250.2 | 16.3 | 296.2 | 176.3 | 126.1/21.6/0.7/3.4 | 50.0/43.0/2.7/5.5 | 9.9 | 4 | -0.40 | -0.56 | 0.019 |
| W50 | 212.1 | 1.5 | 283.1 | 210.8 | 170.6/18.8/0/0 | 44.6/33.2/2.8/3.5 | 10.6 | 5 | -0.40 | -0.57 | 0.029 |
W25A herd starvation by class: unweaned 7.0, does pregnant or nursing 7.7, dry does 1.2; months 1 and 2 hold 13.7 of
16.3. Years 801-900: herd W50A 162.5, W25A 216.5, W50 185.6; starvation 0.1, 7.7, 0.8; herd R >= 0.40 share 0.113,
0.037, 0.053 (R15 0.011); B gap -0.21, -0.22, -0.23 (R15 -0.47).
**Predictions:** 2 of 4 met.
- Herd starvation under 5 in W50A and W50, under 15 in W25A: missed (2.4 and 1.5 met; W25A 16.3).
- Herd 120-200 in W50A and larger in W25A: met (199.2; 250.2).
- Separation in W50A, B gap -0.5 or below, R >= 0.40 share 0.05 or less, breadth 4 or more: missed (-0.61 and 6 met;
  share 0.054).
- The winter cull takes bucks and yearlings, at least 2 a year in W50A against 0 in W50, kids still the largest class:
  met (8.6 against 0; kids 120.6).

## [PRE-REGISTERED 2026-11-14] Sex differences in size and growth, scored against the Ganj Dareh harvest profile
**Status:** design only. Chris checks the parameter choices before any code is built or run (Chris 2026-11-14: "adding
size and growth differences seems more accurate"; "yes please go" to a design first).
**Question:** Our goats reach their target size in 5-11 months at the full growth rate, and both sexes share one target
(animals.js:36). Wild goats differ on both counts. Bezoar adults weigh about 45-90 kg (males) against 25-55 kg
(females), from general-interest sources. Alpine ibex males reach asymptotic size at about 8 years (Bern ibex papers;
Toïgo et al. 1999 not read). I found no female figure and no bezoar growth curve. At Ganj Dareh (Daly et al. 2021,
PNAS, read in full) 60-70% of males were killed before 2.5 years and 60-70% of females lived past 2.5. About 20% of all
goats lived past 4. Females outnumber males 1.11 to 1.86 to 1 in all five building levels. Our keep-value rule kills
males at about 10 months (S0 probe), when they stop growing. Does the model, with wild-like growth, produce the Ganj
Dareh profile under the husbandry rules we already have, and does separation survive?
Note: the B gap compares B genotypes (datamanager.js:83, G[t]), not body sizes, so size differences that come from
who is killed cannot bias it. My message of 2026-11-14 said otherwise; that was wrong.
**Proposed switches** (all off by default; names checked against params.js):
- sexSize (default 1): a male's target is sexSize × the target from B. Proposed 1.7 (bezoar midpoints 67.5 / 40 kg).
- growthCurve ('linear' | 'vb'): 'vb' replaces the straight-line rate with von Bertalanffy growth in mass,
  dM/dt = 3k (T^(1/3) M^(2/3) − M), applied only on days the goat is above growCondition, as now. Because it acts on the
  current size, it handles stalls in the lean season and any birth size.
- growYearsF, growYearsM: years at the full rate from birth to 95% of target, which set k. Proposed 2 and 4. At full
  rate a doe is then at 0.76 / 0.95 / 0.98 of her target at 1 / 2 / 2.5 years, and a buck at 0.50 / 0.76 / 0.83. Lean
  seasons stretch both in calendar time. A buck's starting absolute growth rate is 0.0016 size units a day against a
  doe's 0.0018, so male kids grow slightly slower at first. Real male kids grow faster. One rate constant cannot give
  both faster early growth and a longer tail; I chose the long tail.
- birthSize stays a share of the sex-neutral target, × 1.1 for males (bezoar newborns 2.5-3 kg males, 2-3 kg females).
**Knock-ons that follow size automatically:** intake, maintenance and fodder (size^0.75); reserve and lean buffer
(× size); meat (× size); fighting ability (× size); hunter choice (weighted by size).
**Knock-ons that need a decision:**
- Wolf defence (world.js:1711) scales size over the 0.6-1.4 range. A 1.7× buck would sit at the 0.9 cap, almost safe
  from wolves. Proposed: scale by size / the sex's multiplier, so defence keeps its current spread within each sex.
- Keep value (world.js:1110, 1135): the growth term uses growthAbs × a year. Under 'vb' it becomes the expected gain
  over the next year from the goat's current size. cullSizeNeutral 1 charges feed per head, so a buck costs the
  same as a doe. Proposed: a new value cullSizeNeutral 'sex' that charges by size relative to the sex's mean, so the
  rule stays neutral on size within a sex but sees that a buck eats more.
- Juvenile hazard reference (animals.js:468) uses the straight-line curve; under 'vb' it uses the vb curve.
**New output:** herd deaths by sex × age in years (0-12) and cause group (slaughter: offtake and culls / starvation /
other); mean size by sex × age in years, herd and wild.
**Scoring against Ganj Dareh** (herd deaths older than 6 months, since fusion-based sex profiles cannot see younger
goats; slaughter only, and all causes):
- Share of male deaths before 2.5 years: 0.60-0.70.
- Share of female deaths at or after 2.5 years: 0.60-0.70.
- Share of all deaths at 4 years or older: about 0.20.
- Female-to-male ratio among deaths: 1.11-1.86.
**Runs, in order:**
1. Switch-off check: R15 seed 1, 600 years, new code with all switches off, against results/spring R15: 0 year records
   differ.
2. Wild (H0, no humans), 4 seeds × 600 years: base and SD (all four switches on, plus the defence and keep-value
   choices). Gate: SD wild goats in 0.75-1.0 of base, and adult males at 1.5-1.8× female size from age 5. If the gate
   fails, I stop and report.
3. Husbandry, 4 seeds × 1600 years: R15 and W50, each base and SD (8 runs; the base arms re-run for the new output).
Total 1 + 8 + 8 = 17 runs, through cpuslot.
**Prediction** (years 1501-1600 unless noted, written before any code):
- Wild SD: fewer goats than base (bucks eat more), within 0.75-1.0 of base.
- Male death age: share of male slaughter deaths before 2.5 years above 0.85 in base R15, and 0.50-0.80 in SD R15.
- At least one SD arm meets 3 of the 4 Ganj Dareh measures; neither base arm does.
- Separation holds in SD R15: B gap −0.5 or below, herd R >= 0.40 share 0.02 or less, breadth 4 or more.
- SD R15 herd smaller than base (303), between 220 and 290.

## [RESULTS 2026-11-14] Sex differences in size and growth, scored against the Ganj Dareh harvest profile (raw)
Built at 5144af6 with the parameters as proposed (Chris 2026-11-14: "yes go"). The wild gate runs were launched on the
same code just before that commit. SD = sexSize 1.7, maleBirthSize 1.1, growthCurve vb, growYearsF 2, growYearsM 4,
cullSizeNeutral 'sex'. All 3 check runs, 8 wild runs and 16 husbandry runs exit 0.
Tables: results/sexsize/tab_1501.txt, tab_801.txt (tools/sexsize_tab.py), husb.txt (scratchpad husb_tab.py).
**Switch-off check:** R15 seed 1, 600 years: 0 of 600 year records differ from results/spring R15 (new fields left
out). herdDeathHalf sums to herdDeaths (4263 = 4263).
**Wild gate** (H0, 4 seeds, years 501-600): goats 537.7 SD against 560.1 base (0.96); wild male size at 5+ years 1.69 ×
female. Wild size by age F/M, SD: 1 y 1.05/1.06, 2 y 1.23/1.53, 3 y 1.29/1.86, 5 y 1.32/2.15. Wild trait means base / SD:
R 0.625/0.624, A 0.828/0.796, B 0.888/0.897, H 0.853/0.802, S 0.340/0.260. Gate passed.
**Husbandry**, years 1501-1600, 4 seeds:
| arm | herd | herd starv | B gap | R gap | R>=0.40 | breadth | slaughter m<2.5 / f>=2.5 / >=4 / F:M | GD | all causes m<2.5 / f>=2.5 / >=4 / F:M | GD |
|---|---|---|---|---|---|---|---|---|---|---|
| R15 | 303.3 | 49.2 | -0.82 | -0.61 | 0.005 | 6 | 0.80 / 1.00 / 0.13 / 0.07 | 0 | 0.82 / 0.56 / 0.17 / 0.94 | 1 |
| R15SD | 224.6 | 48.5 | +0.03 | -0.56 | 0.017 | 4 | 0.66 / 1.00 / 0.18 / 0.20 | 2 | 0.81 / 0.36 / 0.11 / 1.06 | 0 |
| W50 | 212.1 | 1.5 | -0.40 | -0.57 | 0.029 | 5 | 0.99 / 0.27 / 0.16 / 1.84 | 2 | 0.97 / 0.27 / 0.17 / 2.12 | 1 |
| W50SD | 168.3 | 0.1 | +0.01 | -0.50 | 0.072 | 3 | 0.98 / 0.24 / 0.14 / 1.56 | 1 | 0.96 / 0.24 / 0.14 / 1.73 | 1 |
GD = Ganj Dareh measures met of 4 (bands 0.60-0.70, 0.60-0.70, 0.15-0.25, 1.11-1.86; the >=4 band was fixed at
0.15-0.25 when the scoring script was written, before any husbandry run). Herd deaths older than 6 months.
Herd mean size at 5+ years F/M: R15 0.65/0.63, R15SD 1.35/2.24, W50 0.98/0.97, W50SD 1.34/2.23; wild 1.30-1.33 (F).
Years 801-900: B gap R15 -0.47, R15SD +0.02, W50 -0.23, W50SD +0.01; herd R>=0.40 share 0.011, 0.023, 0.053, 0.096;
Ganj Dareh, slaughter only: 0, 1, 1, 1 of 4.
Smoke note: herd goats that run off and are lost (about 9-14 a year here) leave the herd alive and are not herd deaths.
**Predictions:** 2 of 5 met.
- Wild SD within 0.75-1.0 of base: met (0.96).
- Male slaughter deaths before 2.5 years above 0.85 in base R15, 0.50-0.80 in SD R15: missed (0.80; SD 0.66 met).
- At least one SD arm meets 3 of 4 Ganj Dareh measures, neither base arm does: missed (best SD 2, R15SD slaughter;
  W50 base also 2).
- Separation holds in SD R15, B gap -0.5 or below, R>=0.40 share 0.02 or less, breadth 4 or more: missed (B gap
  +0.03; share 0.017 and breadth 4 met).
- SD R15 herd 220-290: met (224.6).
Untested: which of the switches removes the B gap. 'vb' sets growth time by sex only, so a big-B goat no longer takes
longer to reach its target than a small one, as it did under growthAbs ("absolute: big targets mature later").
Separating that from sexSize needs an ablation.

## [PRE-REGISTERED 2026-11-14] Coupled size, growth rate and maturity, with growth rate varying between goats
**Question:** Chris (2026-11-14): "no mammal is such that every member matures to the day"; "body size, growth rate,
and age of maturity are not independent from each other"; "vary it between goats, pre-register and build it". The vb
curve in the sex-differences batch (above) fixed the time to grow for each sex: every doe at the full rate reaches 95%
of her target in 2 years whatever her B, so size and time to maturity were decoupled, and the B gap went from -0.82
(linear) to +0.03. The linear curve is the other extreme: a fixed daily gain, so time to grow is proportional to size.
Search summaries (primary papers not read): goats reach puberty at about 60-75% of their own mature weight (MSD Vet
Manual; Shiba does at 27 weeks and 12 kg); across cattle breeds larger mature size goes with later puberty, while
within breeds the genetic correlation of growth rate with puberty is near zero or favourable; bighorn ewes first lamb
at 2-4 years, set by mass with density, with wide overlap in mass between early and late breeders. The ontogenetic
growth model (West et al. 2001, Nature; form recalled, not re-read) couples the three: growth is paid from an
intake surplus that scales as m^(3/4), and time to maturity scales as (adult mass)^(1/4). Does that coupling, with
growth rate varying between goats, bring back part of the B gap, and does it spread the age at first kid?
Correction: my message of 2026-11-14 said a small doe could breed in her first autumn under linear growth. Does cannot
conceive before femaleMinAge (480 days) at any size, so that was wrong; the size threshold can only delay a doe past
her second rut, and only where food stalls growth.
**Settings:** code of the commit building this entry (after the commit registering it). New options, default off:
- growthCurve 'ogm': dm/dt = a m^(3/4) (1 - (m/T)^(1/4)), applied on growing days and scaled by the genome's growth
  multiplier exactly as vb is. a per sex is set as vb's k was, from birthSize: a goat of target 1 x the sex's size
  multiplier, born at birthSize of its target, reaches 95% of it in growYears at the full rate, so
  a = 4 (sexMult)^(1/4) ln[(1 - birthSize^(1/4)) / (1 - 0.95^(1/4))] / (growYears x yearDays): 0.01883 (does), 0.01075
  (bucks, sexSize 1.7). Time to grow then scales with (T / T_ref)^(1/4). Does of target 0.6 / 1.0 / 1.4 reach 95% at
  634 / 720 / 783 days and 80% (breedSizeFrac) at 363 / 412 / 448 days at the full rate; bucks of target 1.02 / 1.7 /
  2.38 reach 95% at 1267 / 1440 / 1566 days. All does are at breeding size before femaleMinAge at the full rate, so B
  delays first conception only through stalled growth.
- growSD (default 0): each goat's a is multiplied by exp(growSD z), z ~ N(0, 1), drawn at birth (and for an immigrant)
  from a new random stream rand4, so rand() is untouched. Not inherited, by design: a heritable rate whose only cost is
  energy would run to its upper bound in wild and herd alike, since growth stops when reserves reach growCondition
  (Chris, 2026-11-14: "fast growing goats monoculture"). Proposed 0.2.
- Juvenile hazard reference under ogm: the size of a single of its target grown at the sex's a (multiplier 1), so a
  slow grower counts as small for its age. Keep value under ogm: its own next-year gain at its own a.
- New output firstKidStats (wild, herd): per year the count, quartiles of age at first kid, and sums for correlations of
  that age with the mother's B and with her growth multiplier.
Base settings for every arm: the SD settings of the sex-differences batch (sexSize 1.7, maleBirthSize 1.1, growYearsF 2,
growYearsM 4, cullSizeNeutral sex), with growthCurve ogm. Arms: H0O0 and H0O (humansPerCamp 0, growSD 0 and 0.2, 600
years); R15O0, R15O, W50O0, W50O (R15 and W50 as in the sex-differences batch, growSD 0 and 0.2, 1600 years); 4 seeds
each. Baselines with the new output: H0SD, R15SD, W50SD (vb) seeds 1-2, which must reproduce results/sexsize year
records exactly apart from the new field. 30 runs. Check before the batch: R15 seed 1, 600 years, defaults, against
results/spring R15: 0 year records differ.
**Method:** `cpuslot submit --tag animal-domestication --out results/ogm/logs --list tools/ogm.jsonl`. Tables:
tools/sexsize_tab.py (size by age, Ganj Dareh measures), scratchpad husb_tab.py (separation, years 801-900 and
1501-1600), tools/ogm_tab.py (first-kid ages: mean yearly quartiles, pooled correlations with B and growth multiplier).
Wild arms read at years 501-600.
**Prediction** (written before any ogm run):
- Wild gate: H0O goats within 0.9-1.1 of H0SD (537.7); wild adult male size 1.6-1.8 x female at 5+ years.
- Coupling: in H0O the pooled correlation of a wild doe's B with her age at first kid is above +0.05, and larger than in
  the vb baseline H0SD.
- Variation: the mean yearly interquartile range of wild age at first kid is at least 20% wider in H0O than in H0O0.
- B gap (years 1501-1600) comes back partway: R15O between -0.10 and -0.60, and |B gap| in R15O at least that in W50O.
- Variation does not set the direction: B gaps of R15O and R15O0 within 0.15 of each other.
- R gap holds: R15O within 0.1 of R15SD (-0.56).

## [RESULTS 2026-11-14] Coupled size, growth rate and maturity, with growth rate varying between goats (raw)
30 runs, all exit 0 (results/ogm). Check before the batch (results/ogm_verify): R15 seed 1, 600 years, defaults, 0 of
600 year records differ from results/spring R15 (66 shared keys; against seed 2, 600 of 600 differ). The vb baselines
H0SD, R15SD, W50SD seeds 1-2 reproduce results/sexsize: 0 year records differ in every run (66-69 shared keys).
Discrepancy with the registered settings: the buck times there (1267 / 1440 / 1566 days to 95%) assumed a buck born at
birthSize of his target; a buck is born at birthSize x maleBirthSize / sexSize = 0.097 of it, so at the full rate the
built code gives 1327 / 1507 / 1639 days (Euler on the same equation agrees to a day). Does: 634 / 720 / 784, as
registered. vb was calibrated the same way, so the baselines share this.
Tables: results/ogm/fk_wild.txt and fk_herd.txt (tools/ogm_tab.py), tab_wild.txt and tab_1501.txt
(tools/sexsize_tab.py; SD rows are results/sexsize, 4 seeds), husb.txt (scratchpad husb_tab.py).
Wild, years 501-600 (H0SD first-kid rows 2 seeds, the rest 4):
| arm | goats | M:F size 5+ | first kids/yr | age q25/q50/q75 | IQR | r(age, B) | r(age, growth mult) |
|---|---|---|---|---|---|---|---|
| H0SD (vb) | 537.7 | 1.69 | 35.5 | 764/949/1071 | 307 | +0.017 | - |
| H0O0 | 538.7 | 1.67 | 34.1 | 839/985/1068 | 229 | +0.045 | - |
| H0O | 534.8 | 1.67 | 33.2 | 797/988/1080 | 283 | +0.017 | -0.595 |
Husbandry, years 1501-1600 (separation from husb.txt; first-kid ages herd does, vb rows 2 seeds):
| arm | herd | herd starv | B gap | R gap | R>=0.40 | breadth | herd first kid q50, IQR | r(age, B) herd | r(age, g) herd |
|---|---|---|---|---|---|---|---|---|---|
| R15SD (vb) | 224.6 | 48.5 | +0.03 | -0.56 | 0.017 | 4 | 874, 191 | -0.040 | - |
| R15O0 | 232.5 | 53.5 | +0.02 | -0.59 | 0.010 | 5 | 904, 196 | -0.011 | - |
| R15O | 222.9 | 47.3 | +0.02 | -0.59 | 0.019 | 6 | 911, 201 | +0.059 | -0.384 |
| W50SD (vb) | 168.3 | 0.1 | +0.01 | -0.50 | 0.072 | 3 | 688, 55 | -0.031 | - |
| W50O0 | 168.8 | 0.1 | +0.00 | -0.49 | 0.070 | 3 | 699, 54 | +0.004 | - |
| W50O | 171.8 | 0.2 | -0.01 | -0.55 | 0.038 | 3 | 703, 62 | +0.074 | -0.353 |
Years 801-900 B gaps: R15O0 +0.03, R15O +0.02, W50O0 +0.01, W50O -0.01. B spread, years 501-600 / 1501-1600, all
goats (hist): H0O mean 0.893 sd 0.050; R15O all goats 0.909 sd 0.048, herd 0.925 sd 0.040 (base linear R15: all
goats 0.545 sd 0.417, herd 0.055 sd 0.077). Ganj Dareh, slaughter only: R15O 1/4 (m<2.5 0.39, f>=2.5 1.00, >=4 0.20,
F:M 0.18), R15O0 0/4, W50O 2/4 (F:M 1.74, >=4 0.15), W50O0 1/4.
**Predictions:** 4 of 6 met.
- Wild gate, H0O goats 0.9-1.1 of H0SD and M:F 1.6-1.8: met (0.99; 1.67).
- Coupling, r(age, B) in H0O above +0.05 and above H0SD: missed (+0.017, equal to H0SD).
- Variation, wild IQR at least 20% wider in H0O than H0O0: met (283 against 229, +24%; the vb baseline H0SD is 307).
- B gap in R15O between -0.10 and -0.60, |R15O| at least |W50O|: missed (+0.02).
- B gaps of R15O and R15O0 within 0.15: met (+0.02 and +0.02).
- R gap of R15O within 0.1 of -0.56: met (-0.59).

## [PRE-REGISTERED 2026-11-16] Curved linear growth: one daily growth chunk for every goat, bent into a curve
**Question:** Chris (2026-11-16), on the ogm curve of the coupled-growth batch (above): bucks were 1.7x and also had a
sex-specific a that made them take longer, "this is just building the linear model into this model". His
specification: every day a goat is above growCondition it grows a fixed chunk, as in the linear model, the same for
every goat; the chunk is set so a doe takes 2 years from birth size to target; a function turns that line into a
curve that gives the actual daily growth; a buck, with about twice the target, takes about twice as long; no a and no
g. So time to grow is proportional to (target - birth size) within and between sexes. He holds the within-sex link
plausible without direct evidence, given the cross-species and cross-sex evidence; the cattle result I reported
(within breeds, growth rate does not clearly predict puberty) is about growth rate, not mature size. Does the size-time
link of linear growth, with growth slower and curved, bring back the B gap of linear growth (R15 -0.82)?
Fixes since the coupled-growth batch (7bba221): vb k and ogm a now use each sex's birth share (bucks had taken 1507
days, not 1440, to 95% under ogm); the linear juvenile-hazard reference newborn uses it too. Defaults unchanged
(0 of 600 year records differ). The browser view's World.draw crash is fixed (9d405a8, rename only, 0 differ).
**Settings:** code of the commit building this entry (after the commit registering it). New options, default off:
- growthCurve 'curved': on a growing day, ds = chunk x gm x k x ((T - size) / (T - b))^((k - 1) / k), capped at T -
  size, where chunk = (1 - birthSize) / (growYearsF x yearDays) (a doe of target 1 crosses from birth to target in
  growYearsF on the straight line), b = the sex's birth share x T (a single newborn), and k = curveExp. A single then
  follows size = b + (T - b) (1 - (1 - x)^k), x = chunk t / (T - b), reaching T at (T - b) / chunk. k = 1 is the
  straight line at the slower chunk; k = 2 starts at twice the line's speed and slows to 0 at the target. A twin
  born smaller starts faster (catch-up). growYearsM, growSD and the per-goat multiplier are not used.
- curveExp (default 2).
- Juvenile hazard reference: a single of its target on this curve at its age. Keep value: its gain over the next year
  on this curve from its current size.
With chunk 0.00118 a day (growthAbs is 0.0035), at the full rate (k = 2; k = 1 in brackets):
| goat | target | to target | to 80% |
|---|---|---|---|
| doe | 0.6 | 432 d | 239 d (346) |
| doe | 1.0 | 720 d | 398 d (576) |
| doe | 1.31 (wild mean B) | 943 d | 521 d (755) |
| doe | 1.4 | 1008 d | 557 d (806) |
| buck | 1.7 | 1300 d | 719 d (1040) |
| buck | 2.23 | 1706 d | 943 d (1364) |
| buck | 2.38 | 1820 d | 1006 d (1456) |
A doe cannot conceive before femaleMinAge (480 d), so at the full rate a doe of target above about 1.1 (k = 2) is still
short of breeding size then, and size delays first conception even without food stalls.
Base settings for every arm: sexSize 1.7, maleBirthSize 1.1, cullSizeNeutral sex, growYearsF 2, growthCurve curved.
Arms: H0C, H0C1 (humansPerCamp 0, 600 years); R15C, R15C1, W50C, W50C1 (R15 and W50 as in the sex-differences batch,
1600 years); C = curveExp 2, C1 = curveExp 1. 4 seeds, 24 runs. References: results/sexsize H0, R15, W50 (linear,
same-size sexes) and H0SD, R15SD, W50SD (vb, run before the birth-share fix). Check before the batch: R15 seed 1, 600
years, defaults, against results/ogm_verify/off_R15_s1: 0 year records differ.
**Method:** `cpuslot submit --tag animal-domestication --out results/curved/logs --list tools/curved.jsonl`. Tables:
tools/sexsize_tab.py, tools/ogm_tab.py, scratchpad husb_tab.py (years 801-900 and 1501-1600); B spread from hist and
histHerd. Wild arms read at years 501-600.
**Prediction** (written before any curved run):
- Wild: H0C goats 0.80-1.05 of H0SD (537.7); wild adult male size 1.6-1.8 x female; wild mean B 0.75 or above.
- Coupling: in H0C the pooled correlation of a wild doe's B with her age at first kid is above +0.10.
- B gap (years 1501-1600) returns: R15C at -0.30 or below; |B gap| in R15C at least that in W50C.
- Curve against line: |B gap| in R15C1 at least that in R15C (the line spreads breeding ages over more days).
- R gap holds: R15C within 0.1 of -0.56.

## [RESULTS 2026-11-16] Curved linear growth: one daily growth chunk for every goat, bent into a curve (raw)
24 runs, all exit 0 (results/curved). Check before the batch (results/curved_verify): R15 seed 1, 600 years, defaults,
0 of 600 year records differ from results/ogm_verify/off_R15_s1 (69 shared keys). Smoke R15C seed 1, 600 years, ran.
Discrepancy with the registered table: its "to 80%" column is 80% of the way from birth size to target; breeding needs
80% of the target (breedSizeFrac x T), which the code uses. Correct full-rate days to 80% of target, k = 2 (k = 1):
does 0.6 / 1.0 / 1.31 / 1.4: 223 / 371 / 486 / 520 (331 / 551 / 722 / 771); bucks 1.7 / 2.23 / 2.38: 689 / 903 / 964
(1013 / 1328 / 1418). Days to target match the table within 4. So at the full rate (k = 2) does of target above about
1.30, not 1.1, are short of breeding size at femaleMinAge.
Tables: results/curved/tab_wild.txt, tab_1501.txt (tools/sexsize_tab.py; H0, R15, W50 rows are results/sexsize
linear, same-size sexes), fk_wild.txt, fk_herd.txt (tools/ogm_tab.py), husb.txt (scratchpad husb_tab.py).
Wild, years 501-600, 4 seeds:
| arm | goats | M:F size 5+ | B mean (sd) | first kids/yr | age q25/q50/q75 | r(age, B) |
|---|---|---|---|---|---|---|
| H0 (linear) | 560.1 | 1.00 | - | - | - | - |
| H0SD (vb) | 537.7 | 1.69 | - | - | - | - |
| H0C | 524.3 | 1.70 | 0.878 (0.054) | 31.9 | 970/1062/1090 | +0.178 |
| H0C1 | 539.8 | 1.69 | 0.858 (0.067) | 28.7 | 1117/1248/1385 | +0.280 |
Husbandry, years 1501-1600, 4 seeds (first-kid ages and r for herd does; B for herd goats):
| arm | herd | herd starv | B gap | R gap | R>=0.40 | breadth | herd B mean (sd) | herd first kid q50 | r(age, B) herd |
|---|---|---|---|---|---|---|---|---|---|
| R15 (linear) | 303.3 | 49.2 | -0.82 | -0.61 | 0.005 | 6 | - | - | - |
| R15C | 228.0 | 49.3 | +0.03 | -0.57 | 0.017 | 5 | 0.931 (0.037) | 931 | +0.074 |
| R15C1 | 230.9 | 42.2 | +0.02 | -0.61 | 0.011 | 5 | 0.906 (0.049) | 1145 | +0.118 |
| W50 (linear) | 212.1 | 1.5 | -0.40 | -0.57 | 0.029 | 5 | - | - | - |
| W50C | 170.1 | 0.3 | -0.01 | -0.53 | 0.050 | 3 | 0.882 (0.058) | 712 | +0.208 |
| W50C1 | 190.7 | 0.3 | -0.02 | -0.58 | 0.023 | 4 | 0.865 (0.061) | 993 | +0.448 |
Years 801-900 B gaps: R15 -0.47, R15C -0.00, R15C1 -0.00, W50 -0.23, W50C +0.01, W50C1 -0.01. Herd size at 5+ years
F/M: R15C 1.35/2.28, R15C1 1.33/2.22, W50C 1.31/2.22, W50C1 1.30/2.20 (R15 linear 0.65/0.63). Ganj Dareh, slaughter
only: R15C 1/4, R15C1 0/4, W50C 2/4, W50C1 2/4; all causes: R15C1 2/4, W50C 2/4, W50C1 2/4.
**Predictions:** 3 of 5 met.
- Wild, H0C goats 0.80-1.05 of H0SD, M:F 1.6-1.8, wild mean B 0.75 or above: met (0.98; 1.70; 0.878).
- Coupling, r(age, B) in H0C above +0.10: met (+0.178; H0C1 +0.280).
- B gap in R15C at -0.30 or below, |R15C| at least |W50C|: missed (+0.03).
- |B gap| in R15C1 at least that in R15C: missed (0.02 against 0.03; both near 0).
- R gap of R15C within 0.1 of -0.56: met (-0.57).

## [PRE-REGISTERED 2026-11-16] What removed the B gap: growth pace or sex differences
**Question:** The B gap of linear growth (R15 -0.82, W50 -0.40) is gone in every batch with sex differences on (vb,
ogm, curved; +0.03 to -0.02), and the curved batch (above) showed it is not the size-maturity link: on the straight
line at the slower pace, bigger does breed later (herd W50C1 r +0.45) and B still does not move. Two differences
remain between the runs that shrank and the ones that did not: growth pace (linear growthAbs 0.0035 a day, a target-1
doe grown in 243 days, against 720 at the curved chunk) and the sex differences (sexSize 1.7, maleBirthSize 1.1,
cullSizeNeutral sex). Chris (2026-11-16): "Sure" to separating them.
**Settings:** code of 0a6a0a2 (no code change). R15 as in the sex-differences batch, 1600 years, 4 seeds, 8 runs:
- LSD: linear growth (growthCurve linear, growthAbs 0.0035) with sexSize 1.7, maleBirthSize 1.1, cullSizeNeutral sex.
  Bucks of target 2.23 take (2.23 - 0.216) / 0.0035 = 575 days at the full rate. The linear juvenile reference has used
  each sex's birth share since 7bba221, so this arm has not run before in any form.
- CNS: curved growth (curveExp 2, growYearsF 2) with sexSize 1, maleBirthSize 1, cullSizeNeutral 1 (default).
References: results/sexsize R15 (linear, no sex differences) and results/curved R15C (curved, sex differences).
**Method:** `cpuslot submit --tag animal-domestication --out results/ablate/logs --list tools/ablate.jsonl`. Tables as
for the curved batch: tools/sexsize_tab.py, tools/ogm_tab.py, scratchpad husb_tab.py (years 801-900, 1501-1600), B
mean and sd from hist and histHerd.
**Prediction** (written before any run; a guess, since no mechanism is in hand):
- Pace, not sex differences, removed the gap: LSD B gap at -0.30 or below; CNS B gap within +-0.15 of 0.
- R gap holds in both: within 0.1 of -0.6.
- Wild mean B in both arms 0.75 or above.

## [RESULTS 2026-11-16] What removed the B gap: growth pace or sex differences (raw)
8 runs, all exit 0 (results/ablate). Tables: results/ablate/tab_1501.txt (tools/sexsize_tab.py), fk.txt
(tools/ogm_tab.py), husb.txt (scratchpad husb_tab.py). Wild B is hist minus histHerd. Years 1501-1600, 4 seeds:
| arm | growth | sex differences | herd | herd starv | B gap | R gap | R>=0.40 | breadth | herd B mean (sd) | wild B mean (sd) | herd doe size 5+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R15 | linear | off | 303.3 | 49.2 | -0.82 | -0.61 | 0.005 | 6 | - | 0.875 (0.126) | 0.65 |
| LSD | linear | on | 277.1 | 45.8 | -0.66 | -0.60 | 0.007 | 6 | 0.180 (0.153) | 0.846 (0.133) | 0.75 |
| CNS | curved | off | 241.0 | 47.9 | +0.02 | -0.55 | 0.020 | 3 | 0.916 (0.043) | 0.897 (0.047) | 1.33 |
| R15C | curved | on | 228.0 | 49.3 | +0.03 | -0.57 | 0.017 | 5 | 0.931 (0.037) | 0.901 (0.047) | 1.35 |
Years 801-900 B gaps: R15 -0.47, LSD -0.36, CNS +0.01, R15C -0.00. First kid, herd does: LSD median 712 days, r(age,
B) +0.207; CNS 954, +0.072. Wild does: LSD 1051, r +0.369; CNS 1084, +0.037. Herd buck size 5+ LSD 1.26 (wild 2.19).
Ganj Dareh, slaughter only: LSD 0/4 (m<2.5 0.94, f>=2.5 0.91, >=4 0.09, F:M 0.10), CNS 1/4.
**Predictions:** 3 of 3 met.
- Pace, not sex differences: LSD B gap at -0.30 or below, CNS within +-0.15 of 0: met (-0.66; +0.02).
- R gap within 0.1 of -0.6 in both: met (-0.60; -0.55).
- Wild mean B 0.75 or above in both: met (0.846; 0.897).

## [PRE-REGISTERED 2026-11-17] Chris's curve at the fast pace
**Question:** The ablation above compared the fast straight line (LSD, -0.66) with the slow curve (CNS, R15C, about 0),
and the straight line at the slow pace (R15C1, +0.02) is the only run that holds shape fixed. Chris's curve
(curveExp 2) has not run at the fast pace, so whether pace alone decides the gap is shown for the straight line only.
Chris (2026-11-17): "run my arm please".
**Settings:** code of b890989 (no code change). R15C exactly (curved, curveExp 2, sexSize 1.7, maleBirthSize 1.1,
cullSizeNeutral sex) with growYearsF 0.6746, so the daily chunk is (1 - 0.15) / (0.6746 x 360) = 0.0035, the linear
growthAbs. A target-1 doe grows in 243 days (as on the line, but starting at twice its speed and slowing); a
target-1.7 buck in 439. 1600 years, 4 seeds, 4 runs (CF). References: LSD (fast line), R15C (slow curve).
**Method:** `cpuslot submit --tag animal-domestication --out results/curvefast/logs --list tools/curvefast.jsonl`.
Tables as for the ablation (tools/sexsize_tab.py, tools/ogm_tab.py, scratchpad husb_tab.py), years 1501-1600.
**Prediction** (written before any run; a guess):
- Pace decides it on the curve too: CF B gap at -0.30 or below.
- R gap within 0.1 of -0.6.
- Wild mean B 0.75 or above.

## [RESULTS 2026-11-17] Chris's curve at the fast pace (raw)
4 runs, all exit 0 (results/curvefast). Tables: results/curvefast/tab_1501.txt (tools/sexsize_tab.py), fk.txt
(tools/ogm_tab.py), husb.txt (scratchpad husb_tab.py), each with LSD and R15C beside CF. B mean (sd) from the hist and
histHerd B histograms (bin midpoints, wild = hist - histHerd), years 1501-1600, 4 seeds:
| arm | shape | pace | herd | herd starv | B gap | R gap | breadth | herd B mean (sd) | wild B mean (sd) | herd doe size 5+ |
|---|---|---|---|---|---|---|---|---|---|---|
| LSD | line | fast | 277.1 | 45.8 | -0.66 | -0.60 | 6 | 0.183 (0.125) | 0.846 (0.130) | 0.75 |
| CF | curve | fast | 200.7 | 26.8 | +0.00 | -0.58 | 5 | 0.901 (0.047) | 0.898 (0.045) | 1.32 |
| R15C | curve | slow | 228.0 | 49.3 | +0.03 | -0.57 | 5 | 0.931 (0.033) | 0.901 (0.046) | 1.35 |
R15C1 (line, slow; results/curved) B gap +0.02. Years 801-900 B gap: CF +0.01, LSD -0.36, R15C -0.00. CF size at age 1,
herd F/M 1.21/1.41 (LSD 0.73/1.02, R15C 0.99/1.07). First kid, herd does: CF median 730 days, r(age, B) +0.044; LSD 712,
+0.207; R15C 931, +0.074. Ganj Dareh, slaughter only: CF 0/4.
**Predictions:** 2 of 3 met.
- Pace decides it on the curve too, CF B gap at -0.30 or below: not met (+0.00). Of the four shape-by-pace cells only
  the fast line moves B.
- R gap within 0.1 of -0.6: met (-0.58).
- Wild mean B 0.75 or above: met (0.898).

## [PRE-REGISTERED 2026-11-17] Growth pace calibrated to wild goats, then R15 at that pace
**Question:** Every growth pace so far was set by hand: linear growthAbs 0.0035 (a doe grown in 243 days at the full
rate) and growYearsF 2 (my guess, with no female growth data). Chris (2026-11-17): balance it "around wild
populations"; "go with your best guess". Wild data (search summaries and secondary sources, primary papers not read):
Alpine ibex females reach full body mass at 4.5-5.5 years and males at 8.5-10.5 (Mammalian Species account); ibex
females conceive at 2 years at rate 0.13, at 3 at 0.56, at 4 at 1.00 (Giacometti and Ratti, Albris). No bezoar growth
curve was found; bezoar females weigh 25-55 kg against ibex 40-50, so the ibex female figure is the stand-in. Most
bezoar females first mate at 2 in Turkmenistan; most yearlings mate in Daghestan (IUCN). Our wild does now reach about
95% of adult size by about 2.7 years at growYearsF 2 on the curve (H0C) and about 3.3 on the line (H0C1), and about
1 year on the old fast line (H0).
**Target:** wild does at 95% of adult size at 5.0 years. Bucks are not targeted: one chunk for every goat gives them
about 1.8x the doe's distance, so about 9 years if does take 5 (ibex 8.5-10.5).
**Stage 1 settings:** code of 21c1672 (no code change). humansPerCamp 0, sexSize 1.7, maleBirthSize 1.1,
cullSizeNeutral sex, growthCurve curved, curveExp 1 (the line) and 2 (Chris's curve), growYearsF 3, 3.5, 4, 4.5, 5;
2 seeds, 600 years, 20 runs (tools/wildcal.jsonl, results/wildcal).
**Stage 1 measure and rule** (fixed now): wild does, sizeByAge, years 501-600, pooled over seeds. Adult size A = mean of
age bins 8-12. Bin a covers ages a to a+1 and sits at a+0.5. t95 = the age where the bin means first reach 0.95 A,
interpolated linearly between bin midpoints. For each shape, the stage 2 growYearsF is the one interpolated linearly
between the two swept values whose t95 bracket 5.0, rounded to 0.25. If none bracket it, the nearest swept value.
Wild first-kid age (firstKidStats) is reported as a check, not a target.
**Stage 2 settings:** R15 as for R15C and R15C1 (sexSize 1.7, maleBirthSize 1.1, cullSizeNeutral sex, growthCurve
curved), curveExp 1 and 2, each at its stage 1 growYearsF; 4 seeds, 1600 years, 8 runs (RW1, RW2; results/wildpace).
Tables as for the ablation, years 1501-1600.
**Prediction** (written before any run; guesses):
- Stage 1: growYearsF near 3.75 for the curve and 3.0 for the line (scaling t95 from H0C and H0C1).
- Stage 1: wild median first kid rises above 1100 days on both shapes (breedSizeFrac 0.8 of target binds later). If
  it passes 1460 days (4 years) the breeding threshold, not pace, becomes the next thing to check against the
  literature (puberty at 60-75% of mature weight).
- Stage 2: B gap within +-0.15 of 0 on both shapes; R gap within 0.1 of -0.6; wild mean B 0.75 or above.
- Stage 2: share of slaughtered males killed before 2.5 years below 0.55 (R15C1 at the 2-year pace gave 0.55; slower
  growth keeps males growing, so the keep-value rule holds them longer). Ganj Dareh band 0.60-0.70.

## [RESULTS 2026-11-17] Growth pace calibrated to wild goats, stage 1 (raw)
20 runs, all exit 0 (results/wildcal). Table: results/wildcal/tab.txt (tools/wildcal_tab.py 501 600). Wild goats,
years 501-600, 2 seeds; A = adult size (bins 8-12), t95 in years, first kid = mean of yearly wild medians:
| shape | growYearsF | doe A | doe t95 | buck A | buck t95 | wild first kid (days) |
|---|---|---|---|---|---|---|
| line | 3 | 1.248 | 4.41 | 2.113 | 7.46 | 1594 |
| line | 3.5 | 1.225 | 5.04 | 2.061 | 8.34 | 1799 |
| line | 4 | 1.215 | 5.45 | 1.996 | 8.99 | 1833 |
| line | 4.5 | 1.178 | 6.00 | 1.874 | 9.36 | 2081 |
| line | 5 | 1.173 | 6.48 | 1.767 | 9.68 | 2168 |
| curve | 3 | 1.287 | 3.91 | 2.181 | 6.45 | 1254 |
| curve | 3.5 | 1.291 | 4.35 | 2.187 | 7.34 | 1440 |
| curve | 4 | 1.291 | 4.95 | 2.170 | 8.08 | 1458 |
| curve | 4.5 | 1.250 | 5.25 | 2.076 | 8.40 | 1576 |
| curve | 5 | 1.248 | 5.74 | 2.035 | 8.85 | 1792 |
References at growYearsF 2 (results/curved, 4 seeds): curve t95 2.71, first kid 1062; line 3.30, 1248.
**Rule applied:** line 3 + 0.5 (5.0 - 4.41) / (5.04 - 4.41) = 3.47, rounded 3.5; curve 4 + 0.5 (5.0 - 4.95) / (5.25 -
4.95) = 4.08, rounded 4.0. Stage 2: RW1 line at 3.5, RW2 curve at 4.0 (tools/wildpace.jsonl, results/wildpace).
**Stage 1 predictions:** 1 of 2 met.
- growYearsF near 3.75 (curve) and 3.0 (line): not met (4.0, 3.5).
- Wild median first kid above 1100 days on both: met (curve 1458, line 1799). The line passes 1460 days and the curve
  sits at it, so by the pre-registered note the breeding threshold (breedSizeFrac 0.8) is the next thing to check:
  ibex conceive at 4 years at rate 1.00 and most bezoar first mate at 1-2.

## [RESULTS 2026-11-17] Growth pace calibrated to wild goats, stage 2: R15 at the wild pace (raw)
8 runs, all exit 0 (results/wildpace). Tables: tab_1501.txt (tools/sexsize_tab.py), fk.txt (tools/ogm_tab.py), husb.txt
(scratchpad husb_tab.py), wildsize.txt (tools/wildcal_tab.py), each against R15C1 and R15C (same shapes at growYearsF
2). B means from the hist and histHerd histograms as for the fast-curve batch. Years 1501-1600, 4 seeds:
| arm | shape | growYearsF | herd | herd per seed | herd starv | B gap | R gap | herd R>=0.40 | herd B | wild B | herd doe size 5+ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RW1 | line | 3.5 | 153.9 | 59, 38, 268, 250 | 11.5 | -0.03 | -0.36 | 0.149 | 0.803 | 0.831 | 1.24 |
| RW2 | curve | 4.0 | 245.1 | 241, 238, 252, 251 | 42.7 | +0.02 | -0.63 | 0.007 | 0.916 | 0.893 | 1.32 |
| R15C1 | line | 2 | 230.9 | - | 42.2 | +0.02 | -0.57 | - | - | - | 1.33 |
| R15C | curve | 2 | 228.0 | - | 49.3 | +0.03 | -0.57 | 0.017 | 0.931 | 0.901 | 1.35 |
Herd takeoff (herded goats, every 100 years from year 450): RW1 herds stay at about 20-60 for about 1000 years in every
seed; seeds 3 and 4 rise past 200 by year 1450, seeds 1 and 2 have not risen by 1600 (59 and 26 at 1550). RW2 herds
pass 150 at years 750-1150. Years 801-900: RW1 herd 34.7, R gap -0.07, breadth 0; RW2 R gap -0.35. So the RW1 1501-1600
row mixes two taken-off and two small herds. First kid, median: RW1 herd 1574, wild 1923 days; RW2 herd 1419, wild 1751
(R15C1 1145 / 1441; R15C 931 / 1084). Wild t95 under R15: does RW1 5.71, RW2 5.49; bucks 8.98, 8.51. Slaughter,
males killed before 2.5 years: RW1 0.82, RW2 0.73 (R15C1 0.55, R15C 0.61). Ganj Dareh, slaughter only: 0/4 both.
**Stage 2 predictions:** 2 of 4 met.
- B gap within +-0.15 of 0 on both: met (-0.03, +0.02).
- R gap within 0.1 of -0.6 on both: not met (RW1 -0.36, with two herds not yet taken off; RW2 -0.63).
- Wild mean B 0.75 or above: met (0.831, 0.893).
- Males slaughtered before 2.5 years below 0.55: not met (0.82, 0.73); slower growth raised the share.

## [PRE-REGISTERED 2026-11-17] Breeding threshold 0.65 at the wild pace
**Question:** At the wild-calibrated pace, does first kid at 4-5 years (wild) and herds take off centuries later (RW1:
2 of 4 seeds not by 1600). A doe conceives only at breedSizeFrac 0.8 of her own target (animals.js:239; does only).
Goats reach puberty at about 60-75% of mature weight (search summaries, EXPLOG 2026-11-15 discussion); ibex conceive at
rate 1.00 by 4 years, and most bezoar first mate at 1-2. Chris (2026-11-17): "lower the breeding threshold to 0.65 as
you suggest and see what we get".
**Stage 1 settings:** code of 6aebfc2 (no code change). As the wild calibration (humansPerCamp 0, sexSize 1.7,
maleBirthSize 1.1, cullSizeNeutral sex, growthCurve curved) with breedSizeFrac 0.65: line (curveExp 1) at growYearsF 3,
3.5, 4; curve (curveExp 2) at 3.5, 4, 4.5; 2 seeds, 600 years, 12 runs (tools/breed65.jsonl, results/breed65). Measure
and rule exactly as in the wild calibration (tools/wildcal_tab.py, years 501-600; t95 of wild does to 5.0 years,
interpolated between bracketing values, rounded to 0.25; nearest swept value if none bracket).
**Stage 2 settings:** R15 with breedSizeFrac 0.65, each shape at its stage 1 growYearsF, as RW1 and RW2 otherwise;
4 seeds, 1600 years, 8 runs (BW1, BW2; results/breed65r). Tables as for stage 2 of the wild calibration.
**Prediction** (written before any run; guesses):
- Stage 1: growYearsF within 0.5 of the 0.8 values (line 3.5, curve 4.0).
- Stage 1: wild median first kid at least 250 days earlier than at 0.8 at the chosen pace (line 1799, curve 1458), and
  below 1460 on both.
- Stage 2: every seed's herd passes 150 goats by year 1200 on both shapes.
- Stage 2: B gap within +-0.15 of 0; R gap within 0.1 of -0.6; wild mean B 0.75 or above, on both shapes.

## [RESULTS 2026-11-17] Breeding threshold 0.65 at the wild pace, stage 1 (raw)
12 runs, all exit 0 (results/breed65). Table: results/breed65/tab.txt (tools/wildcal_tab.py 501 600). Wild, 2 seeds:
| shape | growYearsF | doe A | doe t95 | buck A | buck t95 | wild first kid (days) |
|---|---|---|---|---|---|---|
| line | 3 | 1.274 | 4.72 | 2.157 | 7.67 | 1436 |
| line | 3.5 | 1.285 | 5.38 | 2.147 | 8.66 | 1449 |
| line | 4 | 1.262 | 6.02 | 2.037 | 9.19 | 1604 |
| curve | 3.5 | 1.308 | 4.65 | 2.219 | 7.49 | 1084 |
| curve | 4 | 1.308 | 5.29 | 2.189 | 8.18 | 1107 |
| curve | 4.5 | 1.264 | 5.54 | 2.092 | 8.50 | 1310 |
**Rule applied:** line 3 + 0.5 (5.0 - 4.72) / (5.38 - 4.72) = 3.21, rounded 3.25; curve 3.5 + 0.5 (5.0 - 4.65) /
(5.29 - 4.65) = 3.77, rounded 3.75. Stage 2: BW1 line at 3.25, BW2 curve at 3.75 (tools/breed65r.jsonl).
**Stage 1 predictions:** 2 of 2 met. The chosen paces were not run in stage 1; first-kid ages there are interpolated
between the bracketing runs (line about 1442, curve about 1096).
- growYearsF within 0.5 of the 0.8 values: met (3.25 against 3.5; 3.75 against 4.0).
- Wild first kid at least 250 days earlier and below 1460 on both: met (line 1442 against 1799; curve 1096 against
  1458).

## [RESULTS 2026-11-17] Breeding threshold 0.65 at the wild pace, stage 2: R15 (raw)
8 runs, all exit 0 (results/breed65r). Tables: tab_1501.txt, fk.txt, husb.txt, wildsize.txt (tools as for the
wild-pace stage 2), each against RW1 and RW2 (threshold 0.8). Years 1501-1600, 4 seeds:
| arm | shape | growYearsF | threshold | herd | herd starv | B gap | R gap | herd R>=0.40 | herd B | wild B | first kid herd / wild (days) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BW1 | line | 3.25 | 0.65 | 247.9 | 33.6 | +0.02 | -0.66 | 0.006 | 0.902 | 0.883 | 1333 / 1508 |
| BW2 | curve | 3.75 | 0.65 | 234.1 | 38.0 | +0.03 | -0.63 | 0.010 | 0.935 | 0.903 | 1082 / 1252 |
| RW1 | line | 3.5 | 0.8 | 153.9 | 11.5 | -0.03 | -0.36 | 0.149 | 0.803 | 0.831 | 1574 / 1923 |
| RW2 | curve | 4.0 | 0.8 | 245.1 | 42.7 | +0.02 | -0.63 | 0.007 | 0.916 | 0.893 | 1419 / 1751 |
First year with 150 or more herded goats, by seed: BW1 929, 811, 998, 676; BW2 716, 609, 695, 874. Years 801-900: BW1
herd 145.5 (61, 224, 47, 251), R gap -0.32; BW2 214.2, R gap -0.51. Wild t95 under R15: does BW1 5.60, BW2 5.34;
bucks 8.80, 8.27. Slaughter: males before 2.5 years BW1 0.74, BW2 0.68 (Ganj Dareh 0.60-0.70); 4 years or older 0.46,
0.49 (about 0.20); Ganj Dareh slaughter only BW1 0/4, BW2 1/4; all causes 1/4, 2/4.
**Stage 2 predictions:** 2 of 2 met.
- Every seed's herd passes 150 by year 1200 on both shapes: met (latest 998).
- B gap within +-0.15 of 0, R gap within 0.1 of -0.6, wild B 0.75 or above, on both: met (+0.02, +0.03; -0.66, -0.63;
  0.883, 0.903).

## [PRE-REGISTERED 2026-11-17] Crossover: growth model against the keep value's growth credit
**Question:** Only runs on the linear growth rule shrank the herd (R15 -0.82, LSD -0.66); every curved run did not,
including the straight line at the slow pace (curveExp 1, +0.02) and the curve at the fast pace (CF, +0.00). The
keep value (World.cullByOpportunity) credits next year's growth differently by rule: linear credits growth up to the
herd's mean adult size for the goat's sex (adultSize, goats of adultAge 720 days or older), so a grown goat smaller
than that mean is credited growth it will not make; vb, ogm and curved credit growth toward the goat's own target.
Keep-value probe (tools/keepvalue.mjs, R15 seed 2, year 800): adult does' credited growth r(target, growth) -0.69,
with none left to grow. A herder cannot see a target, so 'herd' is a belief a herder could hold, not an error.
Chris (2026-11-17): run the old linear rule with the new credit and the new curve with the average credit; "the
linear branch should lose body size diff and our new one should gain it."
**Code change** (this commit): growthCredit 'model' (default; unchanged behaviour) | 'own' | 'herd'; Animal.curveGainTo(T,
days) is curveGain toward target T. Under 'herd' on the curve the credit is a year of curve growth toward the herd mean,
not the whole shortfall as on the line (a full-grown 1.3 doe under a 1.6 mean: 0.175 a year).
**Settings:** 4 seeds, 1600 years, tables as for the wild-pace stage 2, years 1501-1600.
- LH: R15 exactly (linear, growthAbs 0.0035, no sex differences, cullSizeNeutral 1), growthCredit model (= herd). The
  original body-size result, rerun on this code.
- LO: LH with growthCredit own.
- CH: BW2 (curved, curveExp 2, growYearsF 3.75, breedSizeFrac 0.65, sexSize 1.7, maleBirthSize 1.1, cullSizeNeutral
  sex) with growthCredit herd.
- CO: BW2 itself (results/breed65r), reused if the identity check on this code passes (below).
Identity check: LSD seed 1 and BW2 seed 1, 600 years on this code, against results/ablate and results/breed65r
(scratchpad cmp_years.py); 0 records may differ.
**Prediction** (Chris's hypothesis):
- LO: B gap within +-0.15 of 0 (LH about -0.8).
- CH: B gap -0.30 or below (CO +0.03).
My own guess, recorded separately: CH moves less than the line did, to between -0.10 and -0.30, because the curve's
credit is a year of slow growth rather than the whole shortfall, and the herd mean includes goats still growing.
Both: R gap within 0.1 of -0.6 in all arms; wild mean B 0.75 or above.
**Identity check** (done before any arm ran to the cull): LSD seed 1 and BW2 seed 1, 600 years on f4c9ca2, against
results/ablate and results/breed65r: 0 of 600 records differ in each (69 shared keys); the same check on LSD seed 1
against LSD seed 2 finds 600 of 600 differ. CO reuses results/breed65r BW2.

## [RESULTS 2026-11-17] Crossover: growth model against the keep value's growth credit (raw)
12 runs, all exit 0 (results/credit). Tables: tab_1501.txt, fk.txt, husb.txt (tools as for the wild-pace stage 2), with
CO = results/breed65r BW2. B means from the hist and histHerd histograms. Years 1501-1600, 4 seeds:
| arm | growth | credit | herd | herd starv | B gap | R gap | breadth | herd B | wild B | herd doe size 5+ | herd first kid (days) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LH | linear fast | herd | 303.3 | 49.2 | -0.82 | -0.61 | 6 | 0.055 | 0.875 | 0.65 | 712 |
| LO | linear fast | own | 223.0 | 37.7 | +0.02 | -0.57 | 4 | 0.921 | 0.906 | 1.34 | 781 |
| CH | curve, wild pace | herd | 272.1 | 48.3 | -0.21 | -0.65 | 7 | 0.670 | 0.882 | 1.14 | 926 |
| CO | curve, wild pace | own | 234.1 | 38.0 | +0.03 | -0.63 | 5 | 0.935 | 0.903 | 1.34 | 1082 |
LH reproduces the sexsize R15 row (herd 303.3, starvation 49.2, B gap -0.82). B gap by century from year 501: LH -0.03,
-0.17, -0.32, -0.47, -0.62, -0.73, -0.77, -0.80, -0.81, -0.82, -0.82; CH -0.01, -0.01, -0.03, -0.07, -0.11, -0.12, -0.17,
-0.18, -0.22, -0.22, -0.21 (level from about 1300). r(first-kid age, B), herd: LH +0.145, LO +0.050, CH +0.385, CO
+0.099. Slaughter: males before 2.5 years LH 0.80, LO 0.92, CH 0.47, CO 0.68; share 4 years or older 0.13, 0.14, 0.19,
0.49 (Ganj Dareh about 0.20); Ganj Dareh slaughter only LH 0/4, LO 0/4, CH 1/4, CO 1/4.
**Predictions:** Chris's hypothesis 1 of 2 met; my guess met; both shared predictions met.
- LO B gap within +-0.15 of 0: met (+0.02; LH -0.82).
- CH B gap -0.30 or below: not met (-0.21; CO +0.03). The sign is as predicted.
- My guess, CH between -0.10 and -0.30: met (-0.21).
- R gap within 0.1 of -0.6 in all arms: met (-0.61, -0.57, -0.65, -0.63). Wild mean B 0.75 or above: met (0.875 to 0.906).

## [PRE-REGISTERED 2026-11-18] The herder's reference size: adult age, and size at slaughter
**Decision first** (Chris, 2026-11-18): the herd-average credit is husbandry, herders judging future meat against "an
associatively learned expectation" of size; "change the defaults to curve with average size used for cull". New defaults
(this commit): growthCurve curved, growYearsF 3.75, breedSizeFrac 0.65, sexSize 1.7, maleBirthSize 1.1, cullSizeNeutral
sex, growthCredit herd (curveExp 2 unchanged). Job lists before this commit that leave these out now run the new model.
**Question:** CH (-0.21) depends on what the herder counts as typical. (1) The herd mean counts goats from adultAge (720
days), and on the curve does grow to about 3.75 years, so the mean includes goats still growing. (2) Chris: herders
"would estimate size based on the size of the goats when they cull them", so the mean size at slaughter replaces the
adult mean; is that too strong a feedback?
**Code change** (this commit): creditAge (days from which a goat counts in the herder's adult mean; 0 = adultAge, which
also sets newborn-cohort and other uses, so it is not varied); growthCredit 'cull': each camp keeps a running mean size of
the goats of each sex it slaughters (offtake, surplus and winter culls; exponential, weight 1/cullMemory, cullMemory 20),
the adult mean until its first cull of that sex; it replaces the adult mean in the growth credit.
**Settings:** R15 arguments only (the growth settings are now defaults), 4 seeds, 1600 years, tables as for the
crossover, years 1501-1600.
- D: new defaults, seed 1 only: identity check against results/credit CH seed 1 (cmp_years.py, all years); 0 records may
  differ.
- A3: creditAge 1080 (3 years). A4: creditAge 1440 (4 years). CH (creditAge = adultAge 720) is the 2-year arm.
- CU: growthCredit cull.
**Prediction** (mine; Chris made none):
- A3 and A4: the B gap grows with creditAge, A4 more negative than CH (-0.21), between -0.25 and -0.45. Low confidence:
  the curve's gain depends on the distance to the reference in a way I have not worked through.
- CU: the reference falls well below adult size, since about half the males slaughtered are under 2.5 years, so goats
  past about a year are credited no growth. Weaker than CH: B gap between -0.15 and +0.05. I expect the feedback (smaller
  herd goats, smaller culls, a lower reference) to limit itself rather than run away, because a lower reference credits
  fewer goats. The share of males slaughtered before 2.5 years rises above CH's 0.47.
- All arms: R gap within 0.1 of -0.6; wild mean B 0.75 or above.

## [RESULTS 2026-11-18] The herder's reference size: adult age, and size at slaughter (raw)
13 runs, all exit 0 (results/refsize). Tables: tab_1501.txt (tools/sexsize_tab.py), fk.txt (tools/ogm_tab.py), husb.txt
and bcentury.txt (scratchpad husb_tab.py), perseed_1501.txt; CH from results/credit, CO = results/breed65r BW2.
**Identity:** D seed 1 (new defaults) against CH seed 1: 0 of 1600 records differ (69 shared keys).
Years 1501-1600, 4 seeds:
| arm | reference | herd | herd starv | B gap | per seed | R gap | herd B | wild B | herd doe size 5+ (wild 1.26) | herd first kid (days) | m<2.5 | >=4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CH | adult mean from 2 y | 272.1 | 48.3 | -0.21 | -0.15 -0.23 -0.31 -0.16 | -0.65 | 0.670 | 0.880 | 1.14 | 928 | 0.47 | 0.19 |
| A3 | adult mean from 3 y | 268.6 | 43.2 | -0.26 | -0.58 -0.19 -0.10 -0.15 | -0.62 | 0.615 | 0.877 | 1.10 | 911 | 0.48 | 0.30 |
| A4 | adult mean from 4 y | 285.5 | 48.6 | -0.57 | -0.83 -0.46 -0.65 -0.37 | -0.65 | 0.296 | 0.878 | 0.86 | 783 | 0.45 | 0.36 |
| CU | mean size at slaughter | 254.5 | 51.4 | -0.16 | -0.11 -0.16 -0.11 -0.23 | -0.65 | 0.735 | 0.886 | 1.19 | 950 | 0.78 | 0.20 |
| CO | own target | 234.1 | 38.0 | +0.03 | | -0.63 | 0.935 | 0.903 | 1.34 | 1082 | 0.68 | 0.49 |
B gap by century from year 501: A3 -0.02, -0.02, -0.02, -0.02, -0.06, -0.11, -0.16, -0.20, -0.20, -0.22, -0.26; A4 -0.01,
-0.03, -0.05, -0.07, -0.12, -0.18, -0.25, -0.32, -0.40, -0.51, -0.57 (still falling at 1600); CU -0.01, -0.01, -0.02,
-0.04, -0.05, -0.07, -0.10, -0.13, -0.15, -0.16, -0.16 (level from about 1400). Slaughter is males before 2.5 years and
share 4 years or older (Ganj Dareh 0.60-0.70 and about 0.20); Ganj Dareh slaughter count 1/4, 0/4, 0/4, 1/4, 1/4.
**Predictions:** 4 of 6 of mine met; both shared predictions met.
- B gap grows with creditAge: met (-0.21, -0.26, -0.57). A4 between -0.25 and -0.45: not met (-0.57, and not level).
- CU between -0.15 and +0.05: not met, narrowly (-0.16). Weaker than CH: met (-0.16 vs -0.21). Males before 2.5 years
  above 0.47: met (0.78). No runaway: CU levels from about year 1400.
- R gap within 0.1 of -0.6: met (-0.62 to -0.65). Wild mean B 0.75 or above: met (0.877 to 0.886).

## [PRE-REGISTERED 2026-11-18] The herder's reference size: the largest goat
**Question:** Chris (2026-11-18), "an obvious other opportunistic choice": the herder measures each goat against the
largest goat in the herd. Each goat is credited next year's growth on its curve toward the size of the herd's largest
goat of its sex, now.
**Code change** (this commit): growthCredit 'max' (per sex; the adult mean if the herd has none of that sex).
**Settings:** R15 arguments with growthCredit max, 4 seeds, 1600 years, tables as for the reference-size arms, years
1501-1600. Compared with CH (herd adult mean from 2 years, the default), A4 and CU (results/refsize).
**Prediction** (mine; Chris made none):
- The largest goat sits above most targets, so grown does and bucks below it are credited growth they will not make, as on
  the old linear rule (LH -0.82), and the largest goats are credited none. B gap -0.40 or below, between A4 (-0.57) and
  LH; low confidence.
- More old goats are kept: the share of the slaughtered aged 4 or older falls below CH's 0.19.
- R gap within 0.1 of -0.6; wild mean B 0.75 or above.

## [RESULTS 2026-11-18] The herder's reference size: the largest goat (raw)
4 runs, all exit 0 (results/refsize MX). Tables: tab_mx.txt, fk_mx.txt, husb_mx.txt (tools as for the reference-size
arms). Years 1501-1600, 4 seeds:
| arm | reference | herd | herd starv | B gap | per seed | R gap | herd B | wild B | herd doe size 5+ (wild 1.26) | herd first kid (days) | m<2.5 | >=4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| MX | largest goat of the sex | 289.0 | 46.0 | -0.67 | -0.81 -0.83 -0.34 -0.71 | -0.65 | 0.188 | 0.871 | 0.77 | 759 | 0.43 | 0.35 |
B gap by century from year 501: -0.02, -0.04, -0.06, -0.12, -0.16, -0.22, -0.31, -0.41, -0.51, -0.60, -0.67 (still
falling at 1600). Other gaps: A -0.21, S +0.12, H -0.19, T +0.38, M -0.16, W -0.29, L +0.13; breadth 9 (CH 7). Herd
M:F size at 5+ 1.76 (wild 1.58). Ganj Dareh slaughter 0/4.
**Predictions:** 1 of 2 of mine met; both shared predictions met.
- B gap -0.40 or below: met (-0.67).
- Share of the slaughtered aged 4 or older below CH's 0.19: not met (0.35, the other way).
- R gap within 0.1 of -0.6: met (-0.65). Wild mean B 0.75 or above: met (0.871).

## exp001 — Keep value recalibrated: every term over the same horizon, feed and risk at the size for sex and age: what happens to body size and the kill-off?
**Pre-registered:** 2026-11-18. The first experiment under the data protocol (conventions §4): Mongo
animalDomestication.exp001_keep-recal is the record, results/exp001_keep-recal/<run>.json the copy.
**Question:** Chris (2026-11-18): "let's do the keep value recalibration and see what that does". The keep value mixes
time frames: growth, feed, meat at risk and the sire's share count one year, a doe's kids keepHorizon (3) years. Feed
and risk are charged at the sex's size multiplier (cullSizeNeutral 'sex'), so a buck kid of size 0.4 pays a grown
buck's 1.7. Probe 2026-11-17 (tools/keepvalue.mjs, BW2 seed 2, year 800): buck kids total -0.13 (feed -0.223, risk
-0.306), 95% of them in the bottom 15% of their herd.
**Code change** (this commit): keepFrame 'year' (default, unchanged) | 'horizon': growth credited over keepHorizon years
(on the curve, toward the same reference), feed, meat at risk and the sire's share summed over keepHorizon years, each
year discounted by the chance the goat lives to it (1 - that year's hazard) at the size charged for its age that year.
cullSizeNeutral 'age': feed and risk at the herd's mean size for the goat's sex and age in years (0..5+), neutral
within sex and age. keepTerms (diagnostic) stores each goat's terms; tools/keepvalue.mjs now reads them from the sim.
**Settings:** R15 husbandry arguments (as for the crossover), defaults otherwise (curve, herd-average credit from 2 y),
experiment runs lean (runyears LEAN: unused diagnostics off, histPeriod 5, reportingPeriod 360). 4 seeds, 1600 years.
Run names <ARM>_seed<S>.
- K0: defaults. Identity check: every seed against results/credit CH_seed1-4 (tools/cmp_years.py, shared year
  fields); 0 records may differ.
- KA: cullSizeNeutral age.
- KH: keepFrame horizon.
- KAH: both.
Tables, years 1501-1600: tools/sexsize_tab.py, ogm_tab.py, husb_tab.py; gene_dists.py; tools/keepvalue.mjs probe at
year 800, seed 2, for each arm (results/_scratch).
**Prediction** (mine; Chris made none):
- K0 reproduces CH: 0 of 1600 year records differ in all 4 seeds.
- KA: buck kids leave the bottom of the ranking, so males are eaten older: males dead before 2.5 y below CH's 0.47
  (0.25-0.45), share aged 4 or older above 0.19. B gap within 0.08 of CH's -0.21 (the growth credit is unchanged).
- KH: three years of growth credited toward the herd mean widens the gap between small and large goats' credit: B gap
  stronger than CH, -0.25 to -0.45. Young males are credited more growth, so males dead before 2.5 y fall below 0.47.
- KAH: B gap as KH (within 0.10); males dead before 2.5 y the lowest of the four arms.
- All arms: R gap within 0.1 of -0.6; wild mean B 0.75 or above.
I expect neither change to bring young males into the Ganj Dareh band (0.60-0.70); both should move them away from it.

## exp001 results (raw)
16 runs and 4 probes, all exit 0. Mongo animalDomestication.exp001_keep-recal (8.6-8.7 MB of BSON a run);
results/exp001_keep-recal: tab_1501.txt (tools/sexsize_tab.py), fk.txt (ogm_tab.py), husb.txt and bcentury.txt
(husb_tab.py); probes results/_scratch/exp001_kv (keepvalue.mjs, seed 2, year 800; terms read from the sim, max |diff| 0).
**Identity:** K0 against results/credit CH, all 4 seeds: 0 of 1600 records differ (65 shared fields).
Years 1501-1600, 4 seeds:
| arm | herd | herd starv | B gap | per seed | R gap | herd B | wild B | breadth | herd doe size 5+ | herd first kid (days) | m<2.5 | >=4 | GD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 | 272.1 | 48.3 | -0.21 | -0.15 -0.23 -0.31 -0.16 | -0.65 | 0.670 | 0.880 | 7 | 1.14 | 928 | 0.47 | 0.19 | 1/4 |
| KA | 286.7 | 59.6 | -0.16 | -0.20 -0.09 -0.02 -0.33 | -0.63 | 0.720 | 0.883 | 4 | 1.17 | 956 | 0.87 | 0.09 | 0/4 |
| KH | 293.3 | 50.6 | -0.37 | -0.59 -0.27 -0.44 -0.17 | -0.63 | 0.502 | 0.875 | 6 | 1.01 | 854 | 0.80 | 0.10 | 0/4 |
| KAH | 149.4 | 8.4 | -0.11 | -0.02 -0.01 -0.33 -0.09 | -0.24 | 0.574 | 0.832 | 3 | 1.14 | 840 | 0.81 | 0.14 | 0/4 |
KAH herds by seed, 1501-1600: 29.4, 35.0, 291.8, 241.3. By century from 401, seeds 1 and 2 stay at 22-41 throughout;
seed 3 passes 100 in 901-1000, seed 4 in 1401-1500. B gap by century from 501: K0 -0.01 ... -0.21 (level); KA -0.03, -0.03,
-0.05, -0.10, -0.16, -0.19, -0.19, -0.16, -0.13, -0.15, -0.16; KH -0.01, -0.03, -0.03, -0.09, -0.12, -0.17, -0.26, -0.30,
-0.31, -0.34, -0.37 (still falling); KAH -0.02 ... -0.11.
Probe, seed 2, year 800, bottom-15% share (total keep value) by class: K0 F kids 0.11 (+0.20), M kids 0.38 (+0.05), M 2-3
0.80, M 3-5 0.67; KA F kids 0.04 (+0.37), M kids 0.63 (+0.31), M 1-2 1.00 (+0.11), no non-sire males past 3; KH M kids 0.81
(+0.01), M 1-2 0.43, F 2-3 0.25; KAH (36 herd goats) F 5-9 0.67, M 1-2 0.50. Under 'age' a female kid's risk falls from
-0.180 to -0.085 and her feed from -0.150 to -0.086, more than a buck kid's gains relative to bucks a year older.
**Predictions:** 4 of 11 met.
- K0 reproduces CH: met.
- KA males dead before 2.5 y 0.25-0.45: not met (0.87, the other way). KA aged 4+ above 0.19: not met (0.09). KA B gap
  within 0.08 of -0.21: met (-0.16).
- KH B gap -0.25 to -0.45: met (-0.37, not level). KH males dead before 2.5 y below 0.47: not met (0.80).
- KAH B gap within 0.10 of KH: not met (-0.11). KAH young males the lowest: not met (0.81; K0 0.47 lowest).
- R gap within 0.1 of -0.6 in all arms: not met (KAH -0.24; others -0.63 to -0.65). Wild B 0.75 or above: met (0.832-0.883).
- "Neither change brings young males into the band; both move them away": not met as worded. Both move them out of the
  band, but past it (0.80-0.87), not away from it on the low side.

## exp002 — No quota: the herder eats only goats whose keep value falls below zero. When are males eaten, and what happens to body size and the herd?
**Pre-registered:** 2026-11-18. Mongo animalDomestication.exp002_keep-threshold; results/exp002_keep-threshold.
**Question:** exp001 showed the flat quota (15% of the herd's head count a year) forces the herder to eat goats that
still pay to keep (a buck kid at +0.31 in the KA probe) and counts a kid as a full head. Chris (2026-11-18): "the
herders kept the goats during the fast growth and once growth was less than feed or opportunity cost they became
dinner. ... i like the econCull idea where we cull those below a keep threshold."
**Code change** (this commit): econCull with economy 0 replaces the offtakeRate quota: every cullEvery (30) days the
herder slaughters every herd goat whose keep value plus judgement noise (cullNoise 0.05) is below cullThreshold (0).
The keep value is the one-year frame (keepFrame 'year'): next year's growth toward the herd mean, a doe's kids over 3
years, the sire's share, against next year's feed and meat at risk. surplusCull and winterCull are refused with it.
econCull 0 (the default) leaves the quota path untouched.
**Settings:** exp001's R15 husbandry arguments (offtakeRate 0.15 is then unused) plus econCull 1. Lean experiment runs.
4 seeds, 1600 years. Reference: exp001 K0 (the quota, same defaults).
- TS: econCull 1 (feed and risk at the sex's multiplier, the default).
- TA: econCull 1, cullSizeNeutral age (feed and risk at the herd's size for the goat's sex and age).
- Check: one scratch run, econCull 0, seed 1, 600 years, against exp001 K0_seed1 (tools/cmp_years.py): 0 records may
  differ.
**Prediction** (mine; Chris made none):
- Herds grow past the quota's 272 in both arms, and herd starvation rises above K0's 48 a year, since nothing caps the
  herd but forage.
- TS: in the exp001 K0 probe a yearling buck's keep value is +0.000 (growth 0.275 against feed 0.223 and risk 0.051 at
  the buck multiplier), so with noise about half are eaten as yearlings: males dead before 2.5 y 0.60 or more.
- TA: a yearling buck is +0.11 (feed and risk at a yearling's size) and a buck aged 2-3 about -0.07, so males are eaten
  mostly at 2-3: males dead before 2.5 y lower than TS, between 0.35 and 0.70.
- Both: does are eaten only when their kidding value runs out (old or barren), so the share of the slaughtered aged 4
  or older is above 0.30.
- Both: only grown non-sire bucks and spent does are eaten, so the growth credit selects on size less: B gap weaker than
  K0's -0.21, between -0.15 and +0.05.
- R gap within 0.1 of -0.6; wild mean B 0.75 or above.

## exp002 results (raw)
8 runs and the check, all exit 0. Mongo animalDomestication.exp002_keep-threshold (8.4-8.6 MB of BSON a run);
results/exp002_keep-threshold: tab_1501.txt, fk.txt, husb.txt, bcentury.txt (tools as for exp001), K0 = exp001 K0.
**Check:** econCull 0, seed 1, 600 years (results/_scratch) against exp001 K0_seed1: 0 of 600 records differ.
Years 1501-1600, 4 seeds:
| arm | herd | herd starv | herd births | culled | B gap | R gap | herd B | wild B | breadth | herd doe size 5+ | herd first kid (days) | m<2.5 | >=4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K0 (exp001) | 272.1 | 48.3 | 142.0 | 44.3 | -0.21 | -0.65 | 0.670 | 0.880 | 7 | 1.14 | 928 | 0.47 | 0.19 |
| TS | 20.2 | 0.0 | 12.3 | 9.7 | +0.00 | -0.03 | 0.881 | 0.887 | 0 | 1.30 | 1113 | 0.33 | 0.49 |
| TA | 286.0 | 55.0 | 153.6 | 38.4 | -0.15 | -0.62 | 0.718 | 0.870 | 3 | 1.17 | 974 | 0.85 | 0.11 |
TS herds by seed 11.7, 26.9, 29.6, 12.6; seeds 1 and 2 by century from 401: 6-27 throughout. TS seeds 1 and 2, 1501-1600,
culled by class a year (kids under 1 y, breeding does, breeding bucks, other, no herd-born dam): seed 1 4.6, 1.3, 0.8, 0.0,
2.8 of 6.7 culled, 6.4 births; seed 2 8.6, 1.4, 0.6, 0.0, 2.2 of 10.6, 15.3 births. TA seeds 1 and 2: kids 0.1 and 0.0,
breeding bucks 38.5 and 33.9, breeding does 2.7 and 6.0 a year. TA herds pass 100 at 801-900 (seed 1) and 1201-1300
(seed 2).
Slaughter by age (herdDeathHalf, 4 seeds, 1501-1600), share of males by half-year from 0: K0 0.18, 0.36, 0.00, 0.00, 0.03,
0.11, 0.19, 0.08, 0.05, 0.01; TA 0.00, 0.00, 0.01, 0.11, 0.74, 0.11, 0.02, 0.00, 0.00, 0.00. Females slaughtered: all aged
5 or older in both.
B gap by century from 501: TS -0.01 to +0.00 throughout; TA -0.00, -0.01, -0.03, -0.01, -0.05, -0.15, -0.17, -0.19, -0.19,
-0.16, -0.15.
**Predictions:** 3 of 8 met.
- Check: met.
- Herds past 272 and herd starvation above 48 in both arms: not met (TA 286 and 55 met; TS 20 and 0).
- TS males dead before 2.5 y 0.60 or more: not met (0.33).
- TA males dead before 2.5 y 0.35-0.70 and below TS: not met (0.85; 74% of male slaughter at 2.0-2.5 y).
- Share of the slaughtered aged 4+ above 0.30 in both: not met (TS 0.49, TA 0.11).
- B gap between -0.15 and +0.05 in both: met (TS +0.00, TA -0.15).
- R gap within 0.1 of -0.6: not met (TS -0.03; TA -0.62). Wild B 0.75 or above: met (0.887, 0.870).

## exp003 — Threshold cull with age-sized charges: which feedCost puts the male kill age in the Ganj Dareh band, and what else moves with it?
**Pre-registered:** 2026-11-18. Mongo animalDomestication.exp003_feedcost-sweep; results/exp003_feedcost-sweep.
**Question:** In exp002 TA (econCull 1, cullSizeNeutral age, feedCost 0.15) the herder eats a buck once a year's growth
falls below a year's feed plus meat at risk, at 2.0-2.5 y (74% of male slaughter): males dead before 2.5 y 0.85 against
Ganj Dareh 0.60-0.70. feedCost is a placeholder constant (MODEL.md §11): what the herder prices in for a year's keep, in
meat units, x size^0.75. Chris (2026-11-18): "we are basically using this constant to estimate the cost that the
herder is pricing in ... that's why we sweep and report ... register the default as the range that places us in the
band." This is a declared calibration: once chosen, the male kill age is a calibration target, not a test.
**Settings:** exp002 TA arguments (R15 husbandry, econCull 1, cullSizeNeutral age), lean experiment runs, 4 seeds, 1600
years, years 1501-1600 scored. Arms F050, F075, F100, F125: feedCost 0.05, 0.075, 0.10, 0.125. feedCost 0.15 is exp002
TA (same code path and arguments), reused as the fifth point.
**Selection rule** (fixed now): the calibrated default is the swept value whose 4-seed males-dead-before-2.5-y share
(slaughter, tools/sexsize_tab.py) lies in 0.60-0.70; if two do, the one closest to 0.65; if none, the value
interpolated linearly between the two that bracket 0.65, rounded to 0.005, which then gets its own pre-registered
4-seed confirmation before it becomes the default.
**Out-of-sample checks at the chosen value** (Ganj Dareh, not used to choose): share of the slaughtered aged 4 or
older (about 0.20), females' deaths at 2.5 y or older (0.60-0.70), females per male (1.11-1.86), reported for slaughter
and all causes. Sensitivity across all five points: B gap, R gap, breadth, herd size, herd starvation.
**Prediction** (mine; Chris made none):
- Males dead before 2.5 y falls as feedCost falls: about 0.80 at 0.125, 0.70-0.80 at 0.10, 0.55-0.70 at 0.075, 0.30-0.55
  at 0.05; the band is reached between 0.075 and 0.10.
- The share of the slaughtered aged 4 or older rises as feedCost falls (0.11 at 0.15).
- Fewer goats fall below zero, so herds are larger and herd starvation higher at lower feedCost.
- B gap between -0.10 and -0.25 at every point; R gap within 0.1 of -0.6 at every point; wild B 0.75 or above.

## exp003 results (raw)
16 runs, all exit 0. Mongo animalDomestication.exp003_feedcost-sweep; results/exp003_feedcost-sweep: tab_1501.txt,
fk.txt, husb.txt (tools as for exp001); F150 = exp002 TA. Years 1501-1600, 4 seeds:
| arm | feedCost | herd | herd starv | B gap | per seed | R gap | breadth | herd B | wild B | m<2.5 slaughter | all causes | >=4 slaughter | f>=2.5 all causes | F:M all causes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| F050 | 0.05 | 277.8 | 53.8 | -0.27 | -0.38 -0.43 -0.18 -0.08 | -0.63 | 5 | 0.613 | 0.889 | 0.57 | 0.72 | 0.10 | 0.47 | 0.95 |
| F075 | 0.075 | 273.4 | 55.1 | -0.12 | -0.01 -0.12 -0.25 -0.09 | -0.61 | 6 | 0.769 | 0.889 | 0.61 | 0.77 | 0.13 | 0.47 | 0.92 |
| F100 | 0.10 | 281.2 | 55.3 | -0.16 | -0.34 -0.08 -0.15 -0.06 | -0.63 | 7 | 0.718 | 0.889 | 0.72 | 0.82 | 0.13 | 0.49 | 0.92 |
| F125 | 0.125 | 288.1 | 49.0 | -0.28 | +0.01 -0.44 -0.46 -0.22 | -0.61 | 5 | 0.580 | 0.877 | 0.85 | 0.89 | 0.11 | 0.48 | 0.90 |
| F150 | 0.15 | 286.0 | 55.0 | -0.15 | -0.26 -0.19 -0.07 -0.10 | -0.62 | 3 | 0.718 | 0.870 | 0.85 | 0.90 | 0.11 | 0.49 | 0.90 |
Male slaughter by half-year of age (herdDeathHalf), shares at 1.5-2, 2-2.5, 2.5-3, 3-3.5, 3.5-4 y: F050 0.02, 0.55, 0.30,
0.10, 0.02; F075 0.02, 0.59, 0.27, 0.08, 0.02; F100 0.05, 0.67, 0.20, 0.05, 0.01; F125 0.13, 0.71, 0.12, 0.02, 0.00; F150
0.11, 0.74, 0.11, 0.02, 0.00. Unrounded males dead before 2.5 y (slaughter): 0.569, 0.613, 0.723, 0.847, 0.853.
**Selection (rule as registered):** F075 is the only value in 0.60-0.70 (0.613): calibrated feedCost 0.075.
**Out-of-sample checks at 0.075:** 0 of 3 in band. Aged 4 or older 0.13 slaughter, 0.12 all causes (about 0.20); females
dead at 2.5 y or older 0.47 all causes (0.60-0.70; slaughter 1.00); females per male 0.92 all causes (1.11-1.86;
slaughter 0.14). Males dead before 2.5 y on all causes: 0.77 (the calibration used slaughter, as registered).
**Predictions:** 5 of 10 met.
- Males dead before 2.5 y by feedCost: 0.125 about 0.80 not met (0.85); 0.10 in 0.70-0.80 met (0.72); 0.075 in 0.55-0.70
  met (0.61); 0.05 in 0.30-0.55 not met (0.57); the band reached between 0.075 and 0.10 met.
- Share aged 4 or older rises as feedCost falls: not met (0.10-0.13, no trend).
- Larger herds and more starvation at lower feedCost: not met (herd 273-288, starvation 49-55, no trend).
- B gap within -0.10 to -0.25 at every point: not met (F050 -0.27, F125 -0.28; no trend, wide seed spread).
- R gap within 0.1 of -0.6: met (-0.61 to -0.63). Wild B 0.75 or above: met (0.870-0.889).

## exp004 — Batch 1 anchor (v0.1.0): the frozen defaults under R15 husbandry, the reference for the paper's first experiments
**Pre-registered:** 2026-11-18. Mongo animalDomestication.exp004_batch1-anchor; results/exp004_batch1-anchor.
**Decision** (Chris, 2026-11-18): freeze the model for a first batch of paper experiments ("tag this as our first
batch"); feedCost "perhaps 0.08 or 0.09 ... sweep this range when we do final tests ... find these ranges and report
them". New defaults (this commit): econCull 1 (threshold cull, opportunity rule only; other cull rules keep the
quota), cullSizeNeutral 'age', feedCost 0.085. With the curve, the herd-average credit from 2 y, bezoar sex sizes and
breeding at 0.65 already default, R15 husbandry arguments alone now run the batch-1 model. Pre-batch-1 job lists that
use surplusCull or winterCull with the opportunity rule now stop with an error (set econCull=0); the others run the
batch-1 cull unless they set econCull, cullSizeNeutral and feedCost.
**Settings:** R15 husbandry arguments (as for exp001-003; offtakeRate 0.15 unused), defaults otherwise. A1: 4 seeds,
1600 years, lean experiment runs, years 1501-1600 scored with the exp003 tables.
**Checks:** (1) one scratch run, defaults with feedCost=0.075, seed 1, 600 years, against exp003 F075_seed1
(tools/cmp_years.py): 0 records may differ (the defaults equal exp003's explicit arguments). (2) smoketest.mjs PASS.
**Prediction** (mine): males dead before 2.5 y (slaughter) between 0.61 and 0.72 (exp003 at 0.075 and 0.10); R gap within
0.1 of -0.6; B gap between -0.10 and -0.30; herd 260-300; wild B 0.75 or above.

## exp004 results (raw)
4 runs, the check and the smoke, all exit 0. Mongo animalDomestication.exp004_batch1-anchor; results/exp004_batch1-anchor:
tab_1501.txt, fk.txt, husb.txt (tools as for exp003).
**Checks:** (1) defaults with feedCost 0.075, seed 1, 600 years, against exp003 F075_seed1: 0 of 600 records differ.
(2) smoketest PASS (40 y, 536 goats, 0 bad alleles or energies).
Years 1501-1600, 4 seeds, A1: herd 286.0 (per seed 286.4, 284.5, 294.8, 278.2), herd starvation 52.7, births 147.7,
culled 37.8 a year. Gaps R -0.63, A -0.10, S +0.08, B -0.25 (per seed -0.25, -0.23, -0.41, -0.12), H -0.14, T +0.37,
M -0.12, W -0.04, L +0.21, C +0.00; breadth 6, depth 13.9, IBD 0.90. Herd B 0.624, wild B 0.873. Herd first kid median
915 days (wild 1250). Herd size by age (F/M): 1 y 0.68/0.74, 2 y 0.88/0.98, 5 y 1.10/1.70. Slaughter: males dead before
2.5 y 0.69 (unrounded 0.689; by half-year 1.5-3.5 y 0.04, 0.65, 0.23, 0.06, 0.01), aged 4+ 0.14, F:M 0.15, Ganj Dareh
1/4; all causes: 0.80, 0.11, F:M 0.93, does dead at 2.5+ 0.45, Ganj Dareh 0/4.
**Predictions:** 5 of 5 met; both checks met. Males dead before 2.5 y 0.61-0.72 (0.69); R gap within 0.1 of -0.6
(-0.63); B gap -0.10 to -0.30 (-0.25); herd 260-300 (286); wild B 0.75 or above (0.873).

## exp005 — B0 pilot: the reference culture with each behaviour off in turn, to 4000 years: do herds persist under the threshold cull, and when do the gaps settle?
**Pre-registered:** 2026-11-19. Mongo animalDomestication.exp005_b0-pilot; results/exp005_b0-pilot; job list
tools/exp005.jsonl; code cda20ea (v0.1.0 plus record thinning, output only).
**Why** (notes/batch1-plan.md, decision 1): the 2026-11-11 run-length pilot (c16de77, old model: quota cull, linear
growth) set the suite at 4000 years: R settled by 1600 in every arm, but the minor traits and the lineage and gene-flow
arms did not, and 6 arms never settled. Batch 1 changes the cull, so settling may differ. Chris, 2026-11-19: thin the
record relative to the length, then run a test on B0. B0 is also the plan's check that the threshold cull keeps herds
alive in poorer cultures (exp002 TS: with sex-sized charges, herds never grew).
**Naming:** the reference culture (REF) is the husbandry called R15 up to exp004 (that name was the 0.15 arm of the
offtake-rate sweep; there is no rate under the threshold cull).
**Settings:** REF = exp004's arguments (herdingAt=400 cullRule=opportunity penning=1 offtakeRate=0.15 (unused)
guarding=1 provision=2160 kidShelter=1 buckManagement=1 tetherNew=1 milkIntensity=0.5 twinMax=1 tripletMax=0.2
leanBuffer=12000 herdRange=8 herdTravel=2 surplusCull=0 fodderRation=1 milkCondition=0.5 winterCull=0), v0.1.0
defaults otherwise. Arms, one change each: REF; RAND cullRule=random offtakeRate=0.13 (exp004's 37.8 culled a year from
286, so the quota cull at the threshold cull's rate); noPen penning=0; noGuard guarding=0; noProv provision=0;
noShelter kidShelter=0; noBuck buckManagement=0; noTether tetherNew=0; noMilk milkIntensity=0. Exchange is off in REF
(exchangeN 0), so it has no leave-one-out arm. 9 arms x seeds 1-4, 4000 years, lean protocol runs thinned by length
(k = 3: year rows every 3rd year, gene histograms every 15 years, census every 1080 days).
**Measure:** tools/settle_tab.py results/exp005_b0-pilot, the 11-11 rule as rebuilt (it reproduces that pilot's
settled-at in all 19 arms): gap = herd - wild genotype mean per histogram row, averaged over a window's rows; bias =
seed mean of (200-year window ending at E - the 3201-4000 window), E = 1600, 2000, 2400, 2800, 3200; ok = every core
trait (R A S B H T M W L) within 0.05; settled at = the first E from which every later E is ok. Herd = mean of the
year rows' herded over 3201-4000; an arm whose herd is under 30 is reported and does not set the length.
**Decision rule (a recommendation to Chris, who decides):** the suite's run length = the latest settled-at over the
counted arms; if any counted arm is not settled at 3200, 4000. Also reported, not part of the rule: the first E at
which R and B alone are within 0.05 in every counted arm.
**Checks:** every run exits 0 and saves (a 4000-year thinned run fits Mongo's 16 MB); the run's saved parameters show
recordEvery 3, histPeriod 15, reportingPeriod 1080.
**Prediction** (mine):
1. Herds persist (herd 30 or more over 3201-4000) in every arm and every seed.
2. R bias within 0.05 at E = 1600 in every counted arm.
3. At least 5 of the 9 arms are not ok at E = 1600.
4. RAND's long-run B gap is within 0.10 of 0; REF's is -0.15 or below.
5. REF settles at 3200 or earlier.
6. The rule gives 4000 (at least one counted arm not settled at 3200).
7. A thinned 4000-year run is under 9 MB.

## exp005 results (raw)
36 of 36 runs exit 0 (cpuslot, shared with another project at 6 slots), 2983-5033 s each; every run saved, 7.8-7.9 MB
of BSON. Saved parameters (REF_seed1): recordEvery 3, histPeriod 15, reportingPeriod 1080, commit v0.1.0-5-gdbbfa1e,
clean. Tables: results/exp005_b0-pilot/settle.txt (tools/settle_tab.py), perseed.txt.
Long run 3201-4000, seed means (n = core traits with abs(gap) >= 0.10):

| arm | herd | R | A | S | B | H | T | M | W | L | C | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REF | 291.1 | -0.629 | -0.146 | +0.125 | -0.291 | -0.093 | +0.468 | -0.092 | -0.067 | +0.108 | -0.008 | 6 |
| RAND | 127.5 | -0.364 | -0.083 | +0.049 | -0.029 | -0.032 | +0.091 | -0.043 | +0.017 | +0.128 | +0.028 | 2 |
| noPen | 498.0 | -0.617 | -0.231 | +0.278 | -0.399 | -0.242 | +0.654 | +0.126 | -0.043 | +0.392 | -0.082 | 8 |
| noGuard | 301.9 | -0.629 | -0.085 | +0.164 | -0.482 | -0.057 | +0.487 | -0.072 | +0.013 | +0.088 | -0.028 | 4 |
| noProv | 103.8 | -0.402 | -0.018 | +0.036 | -0.060 | -0.046 | +0.117 | -0.034 | -0.054 | +0.015 | -0.012 | 2 |
| noShelter | 291.4 | -0.634 | -0.137 | +0.170 | -0.388 | -0.145 | +0.401 | -0.065 | -0.183 | +0.169 | -0.021 | 8 |
| noBuck | 264.0 | -0.622 | -0.510 | +0.094 | -0.018 | -0.002 | +0.309 | -0.054 | -0.063 | +0.077 | +0.042 | 3 |
| noTether | 301.3 | -0.642 | -0.113 | +0.326 | -0.475 | -0.117 | +0.569 | +0.121 | -0.099 | +0.267 | -0.127 | 8 |
| noMilk | 290.9 | -0.627 | -0.117 | +0.065 | -0.448 | -0.107 | +0.480 | -0.006 | -0.105 | +0.055 | -0.001 | 6 |

Bias (window ending E minus 3201-4000), largest abs over core traits [trait]; R and B bias:

| arm | 1600 | 2000 | 2400 | 2800 | 3200 | settled at |
|---|---|---|---|---|---|---|
| REF | 0.106 [T] (R +0.002, B +0.033) | 0.092 [B] (R -0.001, B +0.092) | 0.141 [B] (R +0.019, B +0.141) | 0.155 [B] (R +0.016, B +0.155) | 0.079 [M] (R -0.001, B +0.064) | not settled |
| RAND | 0.289 [R] (R +0.289, B +0.025) | 0.281 [R] (R +0.281, B +0.017) | 0.250 [R] (R +0.250, B +0.019) | 0.128 [R] (R +0.128, B +0.015) | 0.057 [A] (R -0.014, B +0.011) | not settled |
| noPen | 0.233 [S] (R +0.017, B +0.170) | 0.154 [B] (R +0.016, B +0.154) | 0.106 [B] (R +0.004, B +0.106) | 0.086 [B] (R +0.014, B +0.086) | 0.049 ok (R +0.005, B +0.049) | 3200 |
| noGuard | 0.219 [B] (R +0.001, B +0.219) | 0.194 [B] (R -0.004, B +0.194) | 0.149 [B] (R -0.013, B +0.149) | 0.111 [B] (R -0.025, B +0.111) | 0.092 [L] (R -0.018, B +0.055) | not settled |
| noProv | 0.051 [B] (R +0.047, B +0.051) | 0.045 ok (R +0.045, B +0.027) | 0.053 [R] (R +0.053, B +0.046) | 0.048 ok (R +0.048, B +0.026) | 0.034 ok (R +0.029, B +0.010) | 2800 |
| noShelter | 0.145 [B] (R +0.000, B +0.145) | 0.079 [W] (R +0.005, B +0.068) | 0.213 [W] (R +0.010, B +0.050) | 0.142 [W] (R +0.020, B -0.010) | 0.080 [L] (R +0.010, B -0.017) | not settled |
| noBuck | 0.152 [A] (R +0.018, B +0.004) | 0.094 [S] (R +0.014, B -0.006) | 0.056 [L] (R +0.012, B +0.014) | 0.034 ok (R +0.010, B -0.013) | 0.042 ok (R +0.007, B -0.011) | 2800 |
| noTether | 0.199 [B] (R +0.004, B +0.199) | 0.190 [B] (R +0.008, B +0.190) | 0.197 [B] (R +0.008, B +0.197) | 0.088 [B] (R +0.012, B +0.088) | 0.088 [B] (R +0.001, B +0.088) | not settled |
| noMilk | 0.335 [B] (R +0.008, B +0.335) | 0.255 [B] (R -0.009, B +0.255) | 0.253 [B] (R -0.009, B +0.253) | 0.128 [B] (R +0.011, B +0.128) | 0.114 [M] (R +0.015, B +0.058) | not settled |

B bias SEs over seeds 0.04-0.21 in REF, noGuard, noMilk, noTether, noShelter (settle.txt).
Per seed, herd over 3201-4000 (lowest year row) and R / B gap in windows 1401-1600, 2001-2200, 2601-2800, 3201-3400,
3801-4000:
- RAND: s1 36.8 (18) R -0.08 -0.08 -0.09 -0.08 -0.11, B about 0; s2 216.0 (155) R -0.10 -0.06 -0.62 -0.67 -0.63;
  s3 41.3 (16) R -0.07 -0.13 -0.05 -0.09 -0.10; s4 215.7 (155) R -0.06 -0.11 -0.18 -0.64 -0.62. B -0.05 to +0.00 in all.
- noProv: s1 65.6 (20) R -0.09 -0.09 -0.08 -0.08 -0.46; s2 47.0 (18) R -0.08 -0.10 -0.07 -0.09 -0.24; s3 153.3 (107)
  R -0.62 -0.61 -0.59 -0.61 -0.59, B +0.03 -0.06 -0.10 -0.21 -0.08; s4 149.4 (106) R -0.63 -0.64 -0.67 -0.64 -0.60,
  B -0.05 -0.05 -0.04 -0.10 -0.05.
- REF B: s1 -0.23 +0.00 -0.03 -0.16 -0.11; s2 -0.25 -0.37 -0.36 -0.42 -0.74; s3 -0.39 -0.25 -0.13 -0.33 -0.27;
  s4 -0.16 -0.10 -0.03 -0.14 -0.12. R -0.59 to -0.66 in every window and seed.
- noTether B: s1 -0.29 -0.26 -0.27 -0.11 -0.29; s2 -0.74 -0.74 -0.76 -0.73 -0.78; s3 -0.08 -0.10 -0.19 -0.24 -0.17;
  s4 +0.01 -0.09 -0.33 -0.73 -0.76.
- noMilk B: s1 -0.11 -0.05 -0.25 -0.70 -0.68; s2 -0.25 -0.37 -0.60 -0.75 -0.74; s3 -0.02 -0.09 -0.26 -0.09 -0.19;
  s4 -0.07 -0.18 -0.17 -0.19 -0.17.
- noGuard B: s1 -0.39 -0.56 -0.67 -0.75 -0.69; s2 -0.16 -0.22 -0.09 -0.33 -0.07; s3 +0.01 -0.05 -0.21 -0.22 -0.30;
  s4 -0.50 -0.38 -0.51 -0.70 -0.78.
- noShelter B: s1 -0.16 -0.20 -0.19 -0.13 -0.10; s2 -0.33 -0.21 -0.35 -0.41 -0.24; s3 -0.11 -0.37 -0.39 -0.42 -0.42;
  s4 -0.38 -0.61 -0.66 -0.71 -0.65 (lowest year row 43).
- noPen B: s1 -0.25 -0.45 -0.52 -0.51 -0.45; s2 -0.14 -0.09 -0.10 -0.20 -0.40; s3 -0.24 -0.23 -0.28 -0.42 -0.52;
  s4 -0.29 -0.35 -0.36 -0.27 -0.38. noBuck B -0.07 to +0.01 in every window and seed.
- In every seed of every arm other than RAND s1-s4 and noProv s1-s2, R is -0.55 to -0.68 in every window.
**Decision rule:** counted arms (herd 30 or more): all 9. Not settled at 3200: REF, RAND, noGuard, noMilk, noShelter,
noTether. The rule gives 4000. R and B alone within 0.05 in every arm: at no E (at 3200, B: REF 0.064, noGuard 0.055,
noMilk 0.058, noTether 0.088).
**Predictions:** 5 of 7 met; checks met.
1. Herds persist (30 or more over 3201-4000) in every arm and seed: met (lowest RAND s1 36.8; single years to 16).
2. R bias within 0.05 at 1600 in every arm: not met (RAND +0.289).
3. At least 5 of 9 arms not ok at 1600: met (9 of 9).
4. RAND B within 0.10 of 0, REF -0.15 or below: met (-0.029, -0.291).
5. REF settles by 3200: not met (not settled).
6. The rule gives 4000: met.
7. A thinned 4000-year run under 9 MB: met (7.8-7.9).

## exp006 — Sweep, first pass: each behaviour added alone to a bare culture and removed alone from the reference culture, to 4000 years: which behaviour selects which gene, and where do they interact?
**Pre-registered:** 2026-11-19. Mongo animalDomestication.exp006_two-corner; results/exp006_two-corner; job list
tools/exp006.jsonl (124 runs); code as exp005 (v0.1.0 plus record thinning).
**Decision** (Chris, 2026-11-19, after exp005 and a speed review): "for the sweep let's start with just 0 factors + 1
and all factors - 1". In place of the 2^9 factorial for now: one behaviour at a time from both corners. Run length
4000 (exp005's rule). No gain from more cpuslot workers (Chris: throughput was timed).
**Factors** (on / off): cull = threshold cull (cullRule opportunity, econCull default) / random cull at quota 0.13;
penning 1/0; guarding 1/0; provision 2160/0; kidShelter 1/0; buckManagement 1/0; tetherNew 1/0; milkIntensity 0.5/0;
exchangeN 2/0 (the outline's "exchange on").
**Arms:** base arguments as exp005 REF plus exchangeN=0, with the factors set as named.
- Bottom corner: NONE (all nine off); addCull, addPen, addGuard, addProv, addShelter, addBuck, addTether, addMilk,
  addExch (NONE with that one on). 10 arms x seeds 1-8.
- Top corner: REF (the reference culture, every factor on but exchange) and its leave-one-out arms RAND, noPen,
  noGuard, noProv, noShelter, noBuck, noTether, noMilk: exp005 seeds 1-4 plus seeds 5-8 here (36 runs); addExchREF
  (REF with exchange) seeds 1-8. The top corner is REF, not REF + exchange: exchange's top-corner effect is
  addExchREF - REF, the others are measured with exchange off.
**Measure:** tools/corner_tab.py 3201-4000 results/exp005_b0-pilot results/exp006_two-corner (also 1401-1600): per arm,
herd, gaps (settle_tab's), breadth n, est = seeds with R gap -0.30 or below; per behaviour, add effect = (NONE + it) -
NONE and drop effect = REF - (REF without it), seed means with SE; "interacts" = core traits where add and drop differ
by more than 0.10. Settling: tools/settle_tab.py on the pooled arms.
**Prediction** (mine):
1. NONE: est in at most 4 of 8 seeds, and its herd under 100.
2. The add-one arm with the largest herd is addProv.
3. No add-one arm has a B gap of -0.10 or below (in REF, B needs both the threshold cull and buck management: RAND
   -0.03, noBuck -0.02 in exp005).
4. Buck management's add and drop effects on B differ by more than 0.10 (it interacts).
5. addExchREF's R and B gaps are within 0.10 of REF's.
6. R's drop effect for the cull and for provisioning is -0.15 or below with 8 seeds (exp005: -0.27, -0.23 at 4 seeds).

## exp006 note, 2026-11-19 (before any result): runs split between the desktop and mint
Chris, 2026-11-19: "so why not run some of these runs on mint?". The 6 runs already started (NONE, addCull, addPen,
addGuard, addProv, addShelter, seed 1) stay on the desktop. The other 118 were cancelled from the queue and resubmitted
with cpuslot --anywhere (tools/exp006_anywhere.jsonl, same commands), so each runs on whichever machine frees first; a
run's host is in its _parameters.id.host. Cross-host check: cpuslot crosscheck, a 600-year REF run in file mode, seed 1:
the saved JSON identical on both (seconds, host, started ignored); 432 s desktop, 725 s mint. Mongo: the runs had been
writing to the desktop's own MongoDB, not mint's (conventions say mint); mint's mongod had no animalDomestication.
Copied to mint before resubmitting: the registry and exp001-exp005 (86 documents, counts equal on both). Runs on mint
write exp006 to mint's database; after the last run, the desktop's exp006 documents are merged into mint's and counted
(Chris: move animalDomestication to mint after exp006). The JSON copies come back to results/exp006_two-corner either way.

## exp006 results (raw)
124 of 124 runs complete (complete: true, last year row 3998 of 0-3999 at recordEvery 3). 101 ran on the desktop
(2629-5676 s), 23 on mint (3989-6514 s). Exit files: 121 read 0; addBuck_seed1, addMilk_seed1 and addTether_seed1
(mint) read "unknown (agent restarted)", but their logs end with the run line and the cpuslot copy-back, and their JSON
is complete (finished 2026-11-20 06:16-06:17Z). Commits v0.1.0-8-gd5b3091 (9 runs) and v0.1.0-9-gd370f3b (115), both
clean; the two differ only in README and EXPLOG. Saved parameters: recordEvery 3, histPeriod 15, reportingPeriod 1080.
Mongo: runs wrote to the database of the host they ran on (desktop or mint); the cpuslot session merges the desktop's
into mint's after this. Top-corner arms pool exp005 seeds 1-4 with seeds 5-8 here. Tables:
results/exp006_two-corner/corner_3201-4000.txt, corner_1401-1600.txt (tools/corner_tab.py), settle.txt
(tools/settle_tab.py, given both folders), perseed.txt.

Long run 3201-4000, seed means:

| arm | seeds | est | herd | R | A | S | B | H | T | M | W | L | C | n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NONE | 8 | 0 | 11.4 | -0.033 | +0.003 | -0.000 | -0.001 | +0.000 | +0.001 | -0.001 | +0.002 | +0.005 | +0.001 | 0 |
| addCull | 8 | 4 | 130.4 | -0.338 | -0.181 | +0.028 | -0.018 | +0.003 | +0.127 | +0.012 | -0.012 | -0.017 | +0.011 | 3 |
| addPen | 8 | 0 | 13.3 | -0.035 | -0.001 | +0.002 | +0.002 | -0.001 | -0.000 | +0.008 | +0.003 | +0.007 | +0.001 | 0 |
| addGuard | 8 | 1 | 44.6 | -0.125 | -0.048 | +0.013 | -0.000 | +0.001 | +0.013 | +0.016 | -0.007 | -0.006 | -0.000 | 1 |
| addProv | 8 | 0 | 14.2 | -0.035 | +0.004 | +0.004 | -0.001 | -0.001 | +0.004 | +0.001 | -0.002 | +0.003 | -0.006 | 0 |
| addShelter | 8 | 0 | 11.2 | -0.031 | +0.001 | +0.002 | -0.001 | -0.001 | +0.003 | +0.003 | +0.002 | +0.005 | -0.003 | 0 |
| addBuck | 8 | 0 | 11.8 | -0.038 | +0.002 | +0.001 | +0.000 | -0.001 | +0.001 | -0.000 | +0.004 | -0.003 | -0.005 | 0 |
| addTether | 8 | 0 | 17.0 | -0.032 | -0.000 | +0.001 | +0.000 | +0.002 | +0.004 | -0.001 | +0.001 | +0.000 | +0.003 | 0 |
| addMilk | 8 | 0 | 9.3 | -0.029 | +0.001 | +0.001 | -0.002 | +0.001 | +0.001 | -0.003 | +0.001 | +0.011 | +0.002 | 0 |
| addExch | 8 | 0 | 12.2 | -0.030 | +0.000 | +0.001 | -0.002 | -0.000 | +0.005 | +0.006 | +0.006 | +0.005 | -0.002 | 0 |
| REF | 8 | 8 | 287.8 | -0.636 | -0.148 | +0.174 | -0.295 | -0.083 | +0.447 | -0.062 | -0.090 | +0.140 | -0.001 | 6 |
| addExchREF | 8 | 8 | 304.8 | -0.638 | -0.179 | +0.107 | -0.454 | -0.206 | +0.520 | -0.036 | -0.143 | +0.183 | +0.006 | 8 |
| RAND | 8 | 4 | 123.0 | -0.351 | -0.050 | +0.025 | -0.025 | -0.033 | +0.106 | -0.024 | -0.007 | +0.088 | -0.000 | 2 |
| noPen | 8 | 8 | 497.3 | -0.622 | -0.164 | +0.239 | -0.423 | -0.224 | +0.628 | +0.096 | -0.095 | +0.374 | -0.028 | 7 |
| noGuard | 8 | 8 | 299.0 | -0.635 | -0.066 | +0.144 | -0.482 | -0.073 | +0.484 | -0.058 | -0.023 | +0.065 | -0.004 | 4 |
| noProv | 8 | 5 | 109.6 | -0.444 | -0.032 | +0.034 | -0.042 | -0.063 | +0.133 | -0.045 | -0.039 | +0.018 | -0.014 | 2 |
| noShelter | 8 | 8 | 296.1 | -0.637 | -0.119 | +0.178 | -0.434 | -0.145 | +0.424 | -0.054 | -0.162 | +0.134 | -0.016 | 8 |
| noBuck | 8 | 8 | 265.9 | -0.624 | -0.491 | +0.065 | -0.020 | +0.003 | +0.304 | -0.080 | -0.069 | +0.069 | +0.020 | 3 |
| noTether | 8 | 8 | 303.4 | -0.649 | -0.258 | +0.272 | -0.499 | -0.178 | +0.545 | +0.083 | -0.105 | +0.267 | -0.032 | 8 |
| noMilk | 8 | 8 | 278.4 | -0.636 | -0.098 | +0.082 | -0.304 | -0.150 | +0.443 | -0.005 | -0.104 | +0.091 | -0.009 | 5 |

Effects (add = from NONE, drop = from REF), seed-mean difference (SE):

| behaviour | from | herd | R | A | S | B | H | T | M | W | L | interacts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cull | add | +119.0 | -0.31 (0.11) | -0.18 (0.07) | +0.03 (0.01) | -0.02 (0.01) | +0.00 (0.01) | +0.13 (0.05) | +0.01 (0.01) | -0.01 (0.01) | -0.02 (0.01) |  |
| cull | drop | +164.7 | -0.28 (0.10) | -0.10 (0.04) | +0.15 (0.04) | -0.27 (0.07) | -0.05 (0.04) | +0.34 (0.05) | -0.04 (0.04) | -0.08 (0.05) | +0.05 (0.06) | S B T |
| pen | add | +1.9 | -0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) | +0.01 (0.00) | +0.00 (0.00) | +0.00 (0.00) |  |
| pen | drop | -209.6 | -0.01 (0.01) | +0.02 (0.07) | -0.06 (0.06) | +0.13 (0.07) | +0.14 (0.05) | -0.18 (0.04) | -0.16 (0.06) | +0.00 (0.05) | -0.23 (0.05) | B H T M L |
| guard | add | +33.2 | -0.09 (0.08) | -0.05 (0.05) | +0.01 (0.01) | +0.00 (0.00) | +0.00 (0.00) | +0.01 (0.01) | +0.02 (0.01) | -0.01 (0.01) | -0.01 (0.01) |  |
| guard | drop | -11.2 | -0.00 (0.01) | -0.08 (0.04) | +0.03 (0.05) | +0.19 (0.11) | -0.01 (0.04) | -0.04 (0.04) | -0.00 (0.04) | -0.07 (0.05) | +0.07 (0.04) | B |
| prov | add | +2.8 | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) |  |
| prov | drop | +178.2 | -0.19 (0.08) | -0.12 (0.03) | +0.14 (0.04) | -0.25 (0.07) | -0.02 (0.05) | +0.31 (0.05) | -0.02 (0.04) | -0.05 (0.05) | +0.12 (0.04) | R A S B T L |
| shelter | add | -0.2 | +0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) |  |
| shelter | drop | -8.3 | +0.00 (0.01) | -0.03 (0.04) | -0.00 (0.05) | +0.14 (0.11) | +0.06 (0.05) | +0.02 (0.03) | -0.01 (0.05) | +0.07 (0.05) | +0.01 (0.05) | B |
| buck | add | +0.4 | -0.01 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.01) | +0.00 (0.00) | -0.01 (0.01) |  |
| buck | drop | +21.8 | -0.01 (0.01) | +0.34 (0.03) | +0.11 (0.04) | -0.27 (0.07) | -0.09 (0.04) | +0.14 (0.03) | +0.02 (0.04) | -0.02 (0.05) | +0.07 (0.04) | A S B T |
| tether | add | +5.6 | +0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) |  |
| tether | drop | -15.7 | +0.01 (0.01) | +0.11 (0.08) | -0.10 (0.09) | +0.20 (0.12) | +0.10 (0.06) | -0.10 (0.05) | -0.14 (0.06) | +0.01 (0.06) | -0.13 (0.05) | A B T M L |
| milk | add | -2.1 | +0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) | +0.01 (0.00) |  |
| milk | drop | +9.4 | +0.00 (0.01) | -0.05 (0.05) | +0.09 (0.04) | +0.01 (0.12) | +0.07 (0.06) | +0.00 (0.04) | -0.06 (0.04) | +0.01 (0.05) | +0.05 (0.05) |  |
| exch | add | +0.8 | +0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | -0.00 (0.00) | -0.00 (0.00) | +0.00 (0.00) | +0.01 (0.00) | +0.00 (0.00) | +0.00 (0.00) |  |
| exch | drop | +17.1 | -0.00 (0.01) | -0.03 (0.06) | -0.07 (0.06) | -0.16 (0.10) | -0.12 (0.05) | +0.07 (0.04) | +0.03 (0.06) | -0.05 (0.07) | +0.04 (0.06) | B H |

1401-1600 (corner_1401-1600.txt): the add-one arms other than addCull have herd 9.1-21.6 and every gap within 0.02
of zero; addCull herd 126.3, R -0.286, est 4. est at 1600: RAND 1, noProv 4, the other top-corner arms 8.
Settled at (bias rule, pooled seeds 1-8): 1600 for NONE and every add-one arm except addCull 2400, addGuard 2800;
noBuck, noPen, noShelter 3200; not settled: REF, RAND, noGuard, noMilk, noProv, noTether, addExchREF. At 3200 REF's worst trait is B, +0.074 +- 0.040.
Per seed, R gap / herd in 400-year blocks (1-400, 401-800, ..., 3601-4000; herding starts in year 400):

```
addCull
  s1: +0.00/0 -0.05/13 -0.12/37 -0.40/134 -0.57/216 -0.56/210 -0.60/219 -0.62/228 -0.60/216 -0.62/213
  s2: +0.00/0 -0.04/2 -0.03/9 -0.06/26 -0.05/26 -0.05/26 -0.08/29 -0.05/21 -0.09/32 -0.05/24
  s3: +0.00/0 -0.10/36 -0.41/182 -0.59/253 -0.59/242 -0.58/237 -0.59/235 -0.58/229 -0.60/229 -0.59/229
  s4: +0.00/0 -0.02/10 -0.15/51 -0.46/205 -0.57/247 -0.60/247 -0.60/242 -0.62/255 -0.63/250 -0.64/249
  s5: +0.00/0 -0.04/18 -0.04/19 -0.03/19 -0.05/20 -0.03/16 -0.03/18 -0.04/19 -0.03/19 -0.13/43
  s6: +0.00/0 -0.05/15 -0.04/24 -0.04/19 -0.08/28 -0.03/20 -0.03/23 -0.07/29 -0.05/24 -0.04/19
  s7: +0.00/0 -0.05/23 -0.11/41 -0.47/212 -0.64/259 -0.62/240 -0.64/242 -0.63/241 -0.64/253 -0.62/245
  s8: +0.00/0 -0.04/11 -0.04/15 -0.05/24 -0.05/20 -0.08/31 -0.03/21 -0.04/27 -0.04/22 -0.04/19
addGuard
  s1: +0.00/0 -0.05/22 -0.06/26 -0.04/21 -0.04/22 -0.04/25 -0.07/25 -0.06/23 -0.05/23 -0.03/23
  s2: +0.00/0 -0.04/18 -0.03/19 -0.04/21 -0.06/18 -0.04/19 -0.06/22 -0.06/26 -0.05/22 -0.05/19
  s3: +0.00/0 -0.04/21 -0.04/24 -0.05/32 -0.06/30 -0.04/32 -0.12/33 -0.07/31 -0.04/26 -0.05/27
  s4: +0.00/0 -0.04/20 -0.13/26 -0.05/22 -0.05/25 -0.06/24 -0.06/22 -0.04/21 -0.06/25 -0.07/28
  s5: +0.00/0 -0.03/18 -0.04/22 -0.05/21 -0.04/20 -0.03/20 -0.04/21 -0.04/21 -0.06/21 -0.04/20
  s6: +0.00/0 -0.04/21 -0.04/20 -0.03/20 -0.04/20 -0.05/21 -0.03/20 -0.04/22 -0.05/23 -0.05/24
  s7: +0.00/0 -0.04/21 -0.04/23 -0.05/24 -0.04/28 -0.05/25 -0.27/69 -0.59/200 -0.67/198 -0.66/187
  s8: +0.00/0 -0.04/20 -0.05/22 -0.03/20 -0.05/25 -0.04/21 -0.05/20 -0.04/22 -0.03/24 -0.04/23
RAND
  s1: +0.00/0 -0.05/30 -0.05/34 -0.07/36 -0.09/35 -0.09/38 -0.10/40 -0.09/36 -0.07/34 -0.10/40
  s2: +0.00/0 -0.05/27 -0.04/30 -0.07/33 -0.10/37 -0.15/42 -0.53/186 -0.65/217 -0.65/217 -0.63/215
  s3: +0.00/0 -0.04/34 -0.06/34 -0.07/36 -0.07/35 -0.09/41 -0.04/35 -0.12/42 -0.08/41 -0.10/41
  s4: +0.00/0 -0.05/27 -0.06/33 -0.06/35 -0.06/35 -0.09/43 -0.13/48 -0.58/210 -0.64/216 -0.63/216
  s5: +0.00/0 -0.06/31 -0.13/40 -0.60/196 -0.65/205 -0.64/209 -0.65/207 -0.65/205 -0.66/208 -0.66/208
  s6: +0.00/0 -0.04/27 -0.04/30 -0.08/33 -0.06/32 -0.06/31 -0.08/34 -0.05/32 -0.04/29 -0.04/30
  s7: +0.00/0 -0.05/28 -0.04/29 -0.06/33 -0.16/44 -0.09/38 -0.10/41 -0.08/40 -0.24/84 -0.66/226
  s8: +0.00/0 -0.07/30 -0.05/33 -0.06/32 -0.05/26 -0.05/28 -0.03/30 -0.05/33 -0.06/35 -0.37/130
noProv
  s1: +0.00/0 -0.06/30 -0.06/38 -0.08/39 -0.07/41 -0.08/42 -0.08/42 -0.12/49 -0.11/42 -0.36/89
  s2: +0.00/0 -0.05/26 -0.05/35 -0.08/39 -0.08/41 -0.09/44 -0.07/42 -0.09/42 -0.11/43 -0.18/51
  s3: +0.00/0 -0.14/55 -0.54/144 -0.64/152 -0.63/157 -0.60/153 -0.61/149 -0.62/152 -0.59/155 -0.60/151
  s4: +0.00/0 -0.07/24 -0.29/80 -0.63/147 -0.64/149 -0.64/150 -0.65/149 -0.62/151 -0.65/156 -0.62/143
  s5: +0.00/0 -0.06/27 -0.07/33 -0.08/40 -0.06/36 -0.07/42 -0.08/38 -0.13/47 -0.53/122 -0.62/130
  s6: +0.00/0 -0.09/36 -0.25/63 -0.54/119 -0.65/146 -0.63/136 -0.65/140 -0.67/139 -0.67/134 -0.63/140
  s7: +0.00/0 -0.17/53 -0.61/158 -0.66/158 -0.63/160 -0.61/156 -0.65/157 -0.60/148 -0.62/153 -0.62/155
  s8: +0.00/0 -0.04/26 -0.06/39 -0.05/37 -0.08/42 -0.07/40 -0.05/36 -0.05/37 -0.09/43 -0.12/45
```
**Predictions:** 4 of 6 met.
1. NONE est in at most 4 of 8 and herd under 100: met (est 0, herd 11.4).
2. The add-one arm with the largest herd is addProv: not met (addCull 130.4; addProv 14.2).
3. No add-one arm has B gap -0.10 or below: met (lowest addCull -0.018).
4. Buck management's add and drop effects on B differ by more than 0.10: met (add +0.00, drop -0.27).
5. addExchREF's R and B within 0.10 of REF's: not met (R -0.638 vs -0.636; B -0.454 vs -0.295, 0.159 apart).
6. R drop effect of cull and of provisioning -0.15 or below: met (cull -0.28 +- 0.10, provisioning -0.19 +- 0.08).

## exp006 correction, 2026-11-20 (the analysis session's audit, d5254b3)
In "exp006 results (raw)", the 1401-1600 sentence "the add-one arms other than addCull have herd 9.1-21.6 and every gap
within 0.02 of zero" is wrong for R: R is -0.031 to -0.040 in all of them (addGuard -0.040, addShelter -0.039, NONE
-0.032); the other traits are within 0.014. Every exp006 table reproduces from its command (tools/audit_scoring.py,
each check failing on a planted bad input first). corner_tab's "exch / drop" row is addExchREF - REF, a top-corner
add, as the tool's header says; only its label reads "drop".

## exp007 — Reviewer's design checks: is the R gap the herd-load spook rule, and do lineage sire rules move gaps when the herd selects on no trait?
**Pre-registered:** 2026-11-20, before batch 1's remaining blocks launch (they wait on this). Mongo animalDomestication.exp007_design-checks;
results/exp007_design-checks; job list tools/exp007.jsonl (48 runs, cpuslot --anywhere); code 0bc2e21 (v0.1.0 plus the
sex-cull preference terms, default off). Registry note: a second --register by mistake claimed exp008 (question "x");
deleted from the registry at once, nothing ran under it.
**Why:** the reviewer's design review (notes/review/2026-11-20-design.md, 0bc2e21), findings 1, 2 and 6. Checked in the
code before registering: a herded goat's spook chance is herderAlarm × R × fearOfHumans × herdLoad (src/animals.js:363),
herdLoad = max(minLoad 0.25, herd goats / (herdPerHerder 20 × herders)) (src/world.js:181-183), and herdLoad is used
nowhere else. REF's ~288 goats over 3 camps give a load of about 4.8; a herd of 30 gives 0.5.
**Arms** (4000 years, seeds 1-8, the exp006 base arguments):
- LOADLO: REF with herdPerHerder=1e9 (load fixed at minLoad 0.25 whatever the herd size).
- LOADHI: REF with herdPerHerder=1e9 minLoad=4.8 (load fixed at about REF's established level, also in small herds).
- CTLDEEP, CTLRAND, CTLSHAL: REF with herderAlarm=0 (no spooking), the random cull at 0.13 (no keep value), and
  sireRule deep / random / shallow: a herd regime that selects on no trait by rule (the S pull of herd goats toward the
  herder remains).
- NOCULL: NONE (exp006's bare culture) with offtakeRate=0: no cull at all, so the bottom corner is not a 13% quota.
**Measure** (the analysis session scores; years 3201-4000 unless named): per arm, herd (mean of year rows' herded),
gaps by tools/settle_tab.py's gaps(), breadth n (core traits with abs(seed-mean gap) >= 0.10). Established = mean herd
>= 100 over 3201-4000 (by herd size, not by a trait gap, as the review asks). Within each arm, the across-seed
correlation of herd and R gap. LOADLO and LOADHI are compared with REF (exp005 seeds 1-4 + exp006 seeds 5-8); the CTL
arms with each other. Exploratory, beside these: each gap split into herd change and wild change against the
founders' mean at year 400 (an analysis tool, to be written).
**Prediction** (mine):
1. LOADLO: established in at least 6 of 8 seeds; the seed-mean R gap of established seeds between -0.30 and 0 (REF -0.64).
2. LOADHI: seed-mean R gap -0.50 or below, and every seed with a herd of 30 or more has an R gap of -0.30 or below.
3. CTLDEEP minus CTLRAND: within 0.10 on every core trait (seed means).
4. Breadth n of 2 or less in each CTL arm.
5. NOCULL: established in at least 6 of 8 seeds.
**Decision rule:** if 1 holds (the R gap mostly goes when the load no longer scales with herd size), the paper reports R
as a consequence of the load rule (Methods), establishment is defined by herd size, and R leaves every isolation
measure. If 3 fails (deep differs from random with no trait selected), the lineage block runs as planned with this
control added; if 3 holds, the lineage claim is restated as within-herd selection carried by isolation (review 2) and
B4 is redesigned before it runs. Either way the batch is re-planned with Chris before launch.

## exp007 amendment, 2026-11-20 (before any result: 0 of 48 runs finished; the reviewer's pre-registration review, notes/review/2026-11-20-exp007-prereg.md, 4e8bd8b)
**Wording corrected.** The CTL arms do not "select on no trait by rule". They have no spooking and no keep value, but
these rules still read R: tethering (src/animals.js:250, R × fearOfHumans ≥ captureFear keeps a goat at camp), the
retrieval of night strays (world.js:849, the approach test) and capture (world.js:660/667). Natural selection in the
herd's own environment (pens, guards, provisioning, milking) also continues.
**Measures added** (scored by the analysis session, alongside the registered ones):
- For every arm: the herd-change / wild-change split of each gap, against the founders' mean at year 400; realized
  offtake (culled per year per herd goat, from the year rows); jump years by a herd-size criterion and by R (tools/jump_tab.py).
- The CTL arms are compared over established seeds only (herd >= 100 over 3201-4000), with each seed's herd beside its gaps.
**Prediction 3 restated:** a CTLDEEP - CTLRAND difference counts only if abs(diff) > 0.10 AND > 2 SE (unpaired), with
the neutral marker C's deep - random difference reported as the noise reference. "Prediction 3 fails" means at least
one core trait passes both bars.
**Prediction 2 restated:** scored only if at least 4 LOADHI seeds keep a herd of 30 or more over 3201-4000. If fewer do,
that is the result: a fixed high load stops herds growing.
**Decision rule, revised:**
- R and herd size. LOADLO alone tests how strong the spook filter is, not whether the gap follows herd size. If
  LOADHI gives an R gap of -0.30 or below in herds of 30-100 goats, the R gap tracks spook load, not herd size, and R
  is reported as a consequence of the load rule. If LOADLO's R gap moves to -0.30 or above, R leaves every isolation
  measure either way.
- Lineage. If prediction 3 holds: lineage alone does not move the gaps here, and B4's lineage claim is redesigned
  before it runs. If it fails, the split decides how to read it, and isolation acting alone is not among the readings:
  - a difference carried by wild change: the deep herd stopped tracking a moving wild;
  - a difference carried by herd change in a trait no remaining rule reads (any but R): selection in the herd's own
    environment, carried by isolation.
- NOCULL. If NOCULL establishes in at least 6 of 8 seeds while NONE established in none, the bottom corner's lack of
  herds was the 13% quota's doing. The factorial's cull factor then compares the threshold cull against no cull, not
  against the quota.
**Identity check added:** REF seed 1, 4000 years, current code, --scratch, compared year row by year row with
exp005's REF_seed1 (the code since exp005 adds output thinning and default-off preference terms; a 500-year check
on 2026-11-20 found every record equal).

## exp007 amendment 2, 2026-11-20 (before any result; the reviewer's four gaps, 5508103)
- Lineage branch, R: a CTLDEEP - CTLRAND difference in R carried by herd change reads as selection by the remaining
  R-reading rules (tether, stray retrieval, capture), carried by isolation.
- "Carried by": the component (herd change or wild change) that accounts for more than half of the difference; if
  neither does, the reading is "mixed" and the branch takes no reading for that trait.
- Established-only CTL comparison: at least 4 established seeds per CTL arm. With fewer, prediction 3 is scored on all 8
  seeds, with herd size beside each gap, and the comparison is reported as not resolved on established herds.
- NOCULL established in 1-5 of 8: the quota explains part of the bottom corner's failure. The factorial's cull factor
  then keeps three levels (threshold, 13% random quota, no cull), not two.

## exp007 results (raw)
48 of 48 runs complete (complete: true, last year row 3998), every exit file 0. 40 on the desktop (2175-3962 s),
8 on mint (4440-5547 s). Commits recorded: e20d071 through a0a2e12 (other sessions committed docs and analysis
tools while the batch ran); `git diff e20d071 a0a2e12 -- src load.mjs tools/runyears.mjs` is empty, so every run used
the same sim code. Two runs started with a dirty tree (a5115fa, 958274f); the uncommitted files then were analysis
tools and docs, none in src. Mongo: animalDomestication.exp007_design-checks on mint (both hosts write there since
2026-11-20). JSON copies in results/exp007_design-checks/. The identity check named in amendment 1 did not run (its job
list was written to /tmp, which cpuslot did not run from); resubmitted 2026-11-20 after the batch, result to follow as a
note. Scoring: the analysis session's "exp007 results (scored)" (tools/exp007_tab.py).

## exp007 results (scored)
Analysis session, 2026-11-20.
**Command:** `python tools/exp007_tab.py results/exp007_design-checks "results/exp005_b0-pilot;results/exp006_two-corner"`
(run through cpuslot), saved as results/exp007_design-checks/scored.txt.
- REF pools exp005 seeds 1-4 with exp006 seeds 5-8; NONE is exp006.
- Window 3201-4000.
- Every exp007 run passes `tools/audit_scoring.py rows`: each histogram row's counts equal its year row's goats and
  herded.
- The split's identity check (herd change − wild change = settle_tab gap, 1e-9) holds on every run.

Registered measures, seed means. est = seeds with herd ≥ 100. n = core traits with abs(gap) ≥ 0.10. offtake = culled
per year per herd goat (amendment). r(herd,R) = the across-seed correlation of herd and R gap within the arm.

| arm | seeds | est | herd | R | A | S | B | H | T | M | W | L | C | n | offtake | r(herd,R) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REF | 8 | 8 | 287.8 | -0.636 | -0.148 | +0.174 | -0.295 | -0.083 | +0.447 | -0.062 | -0.090 | +0.140 | -0.001 | 6 | 0.133 | +0.00 |
| LOADLO | 8 | 8 | 261.6 | -0.055 | -0.009 | +0.003 | -0.009 | -0.005 | +0.039 | -0.004 | -0.006 | +0.009 | +0.002 | 0 | 0.124 | -0.70 |
| LOADHI | 8 | 0 | 0.9 | -0.030 | +0.002 | -0.007 | +0.000 | -0.005 | -0.001 | -0.010 | +0.001 | -0.002 | +0.013 | 0 | 1.381 | -0.64 |
| NONE | 8 | 0 | 11.4 | -0.033 | +0.003 | -0.000 | -0.001 | +0.000 | +0.001 | -0.001 | +0.002 | +0.005 | +0.001 | 0 | 0.144 | +0.09 |
| NOCULL | 8 | 8 | 207.4 | -0.645 | -0.585 | +0.182 | +0.029 | +0.017 | -0.010 | +0.043 | +0.028 | -0.073 | +0.032 | 3 | 0.000 | +0.49 |
| CTLDEEP | 8 | 8 | 209.2 | -0.165 | -0.198 | +0.236 | -0.098 | -0.195 | +0.155 | +0.014 | -0.137 | +0.064 | -0.021 | 6 | 0.136 | -0.18 |
| CTLRAND | 8 | 8 | 204.7 | -0.025 | -0.006 | +0.016 | -0.010 | -0.010 | +0.014 | -0.018 | -0.011 | -0.009 | +0.009 | 0 | 0.135 | +0.62 |
| CTLSHAL | 8 | 8 | 202.7 | -0.025 | -0.003 | +0.003 | -0.003 | -0.002 | +0.002 | -0.004 | +0.001 | -0.002 | +0.004 | 0 | 0.135 | -0.23 |

Notes on the table:
- LOADHI's herd is 0.9 (0-1 goats per seed over 3201-4000), so its offtake (culls within a year over year-end herd
  goats) cannot be read.
- Within an arm the herd varies little (LOADLO 256-269, the CTL arms 201-214), so r(herd,R) is computed over a
  narrow range.
- Per-seed herd, R and B gaps are in scored.txt.

**Herd/wild split** (amendment), seed means, herd change / wild change against the founders (301-400). The SEs and
the other arms are in scored.txt.

| arm | R | A | S | B | H | T | M | W | L | C |
|---|---|---|---|---|---|---|---|---|---|---|
| REF | -0.714/-0.078 | -0.060/+0.088 | -0.073/-0.247 | -0.291/+0.004 | -0.023/+0.060 | +0.459/+0.012 | -0.196/-0.135 | +0.067/+0.158 | +0.102/-0.038 | -0.054/-0.053 |
| LOADLO | -0.151/-0.096 | +0.011/+0.019 | -0.085/-0.088 | -0.004/+0.005 | +0.052/+0.057 | +0.264/+0.225 | -0.229/-0.225 | +0.146/+0.152 | -0.091/-0.100 | +0.050/+0.047 |
| NOCULL | -0.693/-0.048 | -0.576/+0.009 | -0.004/-0.187 | +0.048/+0.019 | +0.118/+0.101 | -0.028/-0.018 | -0.048/-0.092 | +0.228/+0.200 | -0.255/-0.182 | -0.017/-0.049 |
| CTLDEEP | -0.224/-0.059 | -0.092/+0.106 | -0.027/-0.263 | -0.079/+0.018 | -0.115/+0.081 | +0.134/-0.021 | -0.061/-0.074 | +0.085/+0.222 | -0.032/-0.096 | -0.066/-0.045 |
| CTLRAND | -0.085/-0.060 | +0.098/+0.104 | -0.248/-0.264 | +0.008/+0.018 | +0.089/+0.100 | -0.000/-0.015 | -0.082/-0.064 | +0.228/+0.239 | -0.102/-0.093 | -0.010/-0.019 |

**Establishment year** (amendment; tools/jump_tab.py criteria; per seed in scored.txt).
- By herd size:
  - LOADLO and all three CTL arms: 8 of 8 each, all at 501, the criterion's first testable year (the 100-year mean
    ending there was already ≥ 100). That is left-censored: these herds were established at once.
  - NOCULL: 8 of 8, at 657-996.
  - LOADHI and NONE: 0 of 8.
- By R: none of LOADLO, LOADHI, CTLRAND, CTLSHAL or CTLDEEP establishes. NOCULL establishes at 615-975, 0-60 years
  before its herd years.
- So in LOADLO and the CTL arms the two markers part.

**Prediction 3, CTLDEEP − CTLRAND.** Every CTL seed is established, so all 8 seeds of each arm are scored. A
difference counts at abs(diff) > 0.10 and > 2 SE (unpaired). "Carried by" uses the more-than-half rule of amendment 2.

| trait | diff (SE) | counts | herd change diff | wild change diff | carried by | paired over 8 shared seeds, herd / wild (SE) (added after registration, descriptive) |
|---|---|---|---|---|---|---|
| R | -0.139 (0.019) | yes | -0.139 | +0.001 | herd | -0.139 (0.022) / +0.001 (0.003) |
| A | -0.193 (0.032) | yes | -0.190 | +0.003 | herd | -0.190 (0.033) / +0.003 (0.005) |
| S | +0.220 (0.031) | yes | +0.221 | +0.000 | herd | +0.221 (0.028) / +0.000 (0.009) |
| B | -0.088 (0.013) | no | -0.088 | -0.000 | herd | -0.088 (0.013) / -0.000 (0.003) |
| H | -0.185 (0.035) | yes | -0.204 | -0.019 | herd | -0.204 (0.038) / -0.019 (0.013) |
| T | +0.141 (0.019) | yes | +0.135 | -0.006 | herd | +0.135 (0.024) / -0.006 (0.010) |
| M | +0.031 (0.027) | no | +0.021 | -0.010 | herd | +0.021 (0.030) / -0.010 (0.020) |
| W | -0.126 (0.027) | yes | -0.143 | -0.017 | herd | -0.143 (0.043) / -0.017 (0.025) |
| L | +0.073 (0.035) | no | +0.070 | -0.003 | herd | +0.070 (0.044) / -0.003 (0.030) |
| C (noise reference) | -0.030 (0.029) | - | -0.056 | -0.026 | - | -0.056 (0.046) / -0.026 (0.052) |

Exploratory, beside the registered reading:
- The two arms share a wild: wild change differs by at most 0.026 on any trait, because the wild's course is set by
  the seed (tools/pair_tab.py on exp005/006). So every deep − random difference is herd change by construction.
- Within CTLDEEP's own gaps, the same more-than-half rule gives:
  - wild change for S (herd −0.027, wild −0.263), W (+0.085 / +0.222) and A (−0.092 / +0.106): the deep herd
    stayed near the founders while the wild moved;
  - herd change for R, H and T.
- In CTLRAND and CTLSHAL the herd change is within 0.025 of the wild change on every trait: those herds track the wild.

**Predictions:** 2 of 5 met, 1 not scored, 2 not met.
1. LOADLO established in ≥ 6 of 8, with seed-mean R gap of established seeds in [−0.30, 0]: met (8 of 8; R −0.055).
2. LOADHI: not scored. 0 of 8 seeds keep a herd of 30 or more (herd 0.9). By amendment 1 that is the result: a fixed
   high load stops herds growing.
3. No core trait with abs(CTLDEEP − CTLRAND) > 0.10 and > 2 SE: not met. R, A, S, H, T and W pass both bars; C's
   difference is −0.030 (0.029).
4. Breadth ≤ 2 in each CTL arm: not met. CTLDEEP n = 6 (R A S H T W); CTLRAND n = 0 and CTLSHAL n = 0 are within it.
5. NOCULL established in ≥ 6 of 8: met (8 of 8; NONE 0 of 8).

**Decision rule, as amended, applied:**
- *R and herd size.* LOADLO's R gap is −0.055, above −0.30, so R leaves every isolation measure. LOADHI has no herd of
  30-100 goats, so the branch "R tracks spook load, not herd size" cannot be tested on these runs. LOADLO's whole gap
  vector is within 0.04 of zero (n = 0; REF n = 6) at a herd of 262.
- *Lineage.* Prediction 3 fails. Every passing trait is carried by herd change by the registered rule. So the readings
  are: R is selection by the remaining R-reading rules (tether, stray retrieval, capture), carried by isolation
  (amendment 2); A, S, H, T and W are selection in the herd's own environment, carried by isolation (amendment 1).
  The exploratory note above qualifies S, W and A.
- *NOCULL.* 8 of 8 established against NONE's 0 of 8: the bottom corner's lack of herds was the 13% quota's doing. The
  factorial's cull factor compares the threshold cull with no cull.

## exp007 note, 2026-11-20 (after scoring; the reviewer's results review, 3af3969 and a353b1b)
The between-arm "carried by" rule (amendment 2) cannot detect a herd that stopped tracking the wild: arms run on the
same seeds share a wild whose trajectory is mostly the seed's own (tools/pair_tab.py), so a deep herd that stands
still while the wild moves shows as herd change against a random herd that follows it. The within-arm split (each
arm's herd change and wild change against its own founders, tools/split_tab.py) is the instrument for that from
exp008 on. The reviewer withdraws the claim that herd-born escapees add little to the wild: in the CTL arms escapes
are 0 and the wild is 28-41% herd-descended, through herd bucks siring wild kids (world.js mating; counted from
8dd84a2 as wildConc). Open hypothesis (reviewer, 9f67403): CTLDEEP's own herd change on R, A, B, H, T, all toward 0.5
from founders far from it, may be the mutation model's pull (uniform ±0.04 clamped to [0,1], stationary mean 0.5)
acting once wild selection is relaxed; to be tested with a shifted neutral marker (cInitLo).

## exp007 correction, 2026-11-20 (the identity check)
"exp007 results (raw)" says the identity check "did not run (its job list was written to /tmp ...)". Wrong: it ran,
on mint, and its result came back late, to results/_scratch/exp008_probe/REFid_seed1.json (commit a0a2e12; the sim
code is the same as exp007's runs). tools/cmp_years.py against exp005's REF_seed1.json: 1333 records compared, 0
differ; hist and histHerd identical. So the code exp007 ran reproduces exp005 exactly. A duplicate submission from
the desktop was also made; it adds a second host and changes nothing here. Later code (8dd84a2 counters, 92d8f21
cInitLo) was identity-checked separately at 500 years.

## exp008 — not used
A stray `--register` on 2026-11-20 (see the exp007 entry) claimed exp008 and made an empty results/exp008_design-checks
folder; the registry entry was deleted, but the folder kept the number taken. Nothing ran under it; folder removed
2026-11-20. The next experiment is exp009.

## exp009 — Does the deep-sire herd's own change come from the mutation model's pull toward 0.5? A neutral marker started at U[0.6,1] against A, H, T, R, B.
**Pre-registered:** 2026-11-20. Mongo animalDomestication.exp009_mutation-pull (mint); results/exp009_mutation-pull; job
list tools/exp009.jsonl (40 runs, cpuslot --anywhere); code 92d8f21.
**Why:** the reviewer's exp007 results review (notes/review/2026-11-20-exp007-results.md, 9f67403, prediction 405e315).
Mutation is a uniform ±mutationStep 0.04 step clamped to [0,1] (src/genome.js mutateAllele), whose stationary mean is
0.5 for any trait no selection holds. In exp007 CTLDEEP's herd moved toward 0.5 on all five traits whose founders sit
far from it (R, A, B, H, T) and not on the four near it, which a relaxation of wild selection plus that pull would
also produce. The neutral marker C is read by nothing and has its own random stream; started far from 0.5, its herd
change measures the pull alone at the deep herd's depth and size. The switch cInitLo/cInitHi (92d8f21) draws C's
initial alleles from U[0.6,1] with one draw per allele as before (identity: defaults 0 of 500 year rows differ from
8dd84a2; shifted C differs only in C's fields). The mutationStep 0.02 arm first proposed is dropped: a deep, inbred
herd's selection responses also wait on new mutation, so a slower change at 0.02 would not separate the two.
**Arms** (4000 years; exp007's arguments plus cInitLo=0.6 cInitHi=1 logHistDepth=1):
- CTLDEEP: no spooking, random cull 0.13, sireRule deep. Seeds 1-16.
- CTLRAND: the same with sireRule random. Seeds 1-16.
- REF: the reference culture. Seeds 1-8 (context: REF's own herd change on A/H/T bears on the same question).
logHistDepth is on (histDepth every 15 years at k = 3; measured 19.2 kB a record, about 5.1 MB a run, so about 13 MB of
BSON a run, under Mongo's 16 MB). Code from 8dd84a2 on also records wildConc, capIn, capBred.
**Measure** (the analysis session; years 3201-4000; founders = the run's own 301-400 means):
- Primary: tools/shiftc_tab.py 3201-4000 results/exp009_mutation-pull CTLDEEP,CTLRAND,REF: per run, herd change as a
  fraction of (0.5 - F) for C and for A, H, T, R, B; per arm the seed mean with a 95% t interval; within-run paired
  differences fraction(C) - fraction(trait).
- Width bar: if C's 95% half-width in CTLDEEP exceeds 0.20, the reading is "unresolved" whatever the point estimate.
- Standing measures (notes/batch1-plan.md): establishment by herd size, the within-arm split, gene flow by
  tools/flow_tab.py (now with wildConc and capBred / capIn, first breedings by captives per capture, a ratio of events).
**Prediction** (the reviewer's, 405e315, quoted): "if the deep herd's own change is mutational: a shifted C (initial
alleles U[0.6, 1.0], scored from its own 301-400 F) reaches a fraction of 0.3-0.6 in CTLDEEP over 3201-4000, with A, H
and T inside its 95% interval, and near 0 in CTLRAND. If C's fraction is below 0.15 while A, H and T stay near 0.4-0.5,
the deep herd's own change is selection, not mutational pull. Between 0.15 and 0.3 I'd call it unresolved at 8 seeds."
(Here 16 seeds, and the width bar above.) Mine: C's fraction in CTLDEEP between 0.15 and 0.45, and in CTLRAND within
0.10 of 0.
**Decision rule:** mutational: CTLDEEP's own change on A, H and T (its direction toward 0.5) is reported as the
mutation model's pull acting where wild selection no longer reaches the herd, a property of the clamped uniform
mutation; the re-plan then puts the mutation model on the list of assumptions to vary. Selection: the deep herd's own
change is selection in the herd's environment, carried by isolation. Unresolved: neither is claimed; the paper reports
the deep herd's change against the wild only.

## exp009 amendment, 2026-11-20 (before any result: 0 of 40 runs finished, no JSON; the reviewer's prereg review, fdbb68f)
**Predictions about CTLRAND withdrawn.** C is neutral in every population and unlinked, so it relaxes toward 0.5 in
CTLRAND's herd and in the wild exactly as in CTLDEEP's herd (drift does not move its expected mean). The reviewer's
"near 0 in CTLRAND" and my "CTLRAND within 0.10 of 0" would fail under the very hypothesis tested. Replaced by a validity
check: C's fraction in CTLRAND's herd equals CTLDEEP's within noise (difference within 2 SE); if it does not, C is not a
valid reference and the experiment is reported as not resolving the question.
**Primary measure changed to a pooled pull estimate.** The pull on C is the same everywhere, so: the pooled C fraction
over herd C in CTLDEEP and CTLRAND and wild C in the same runs (each run's change against its own 301-400 founders' C,
as a fraction of 0.5 - F), with its 95% interval over runs, after the validity check above. The width bar (95%
half-width <= 0.20, else "unresolved") applies to the pooled estimate. CTLDEEP's herd C alone is secondary.
**Readings, per trait (A, H, T, R, B), CTLDEEP's herd fraction against the pooled C:**
- inside the pooled C's 95% interval: the trait's own change in the deep herd is accounted for by the mutation pull;
- clearly below it (below the interval): pull, partly opposed by selection in the herd;
- clearly above it (above the interval): selection beyond the pull.
The reviewer's thresholds stand for the pooled C: pooled C below 0.15 while A, H and T sit near 0.4-0.5 means the deep
herd's own change is selection; pooled C 0.3-0.6 with A, H and T inside its interval means it is mutational; 0.15-0.3
is unresolved. Expected, and read accordingly: C's founders' spread is wider than A, H and T's, so its pull per unit
distance may be faster.
**REF, stated comparison:** REF's herd fractions for A, H, T, R, B against the pooled C, read the same way.
**Decision rule** unchanged in its three outcomes (mutational / selection / unresolved), now read from the pooled C.

## exp009 amendment 2, 2026-11-20 (before any result: 0 of 40 finished, no JSON; the reviewer's three refinements)
- Pooling: each run's herd C fraction and wild C fraction are averaged within the run first; the pooled estimate and
  its 95% interval are then taken over the 32 CTLDEEP and CTLRAND runs.
- Validity check: the CTLRAND - CTLDEEP difference in herd C fraction is reported with its 95% interval beside the
  pass/fail (within 2 SE), so a pass that comes only from a noisy C shows as a wide interval.
- Per-trait readings come from the paired within-run difference fraction(C) - fraction(trait) and its 95% interval
  over CTLDEEP runs (REF runs for REF): spanning 0 = inside (the pull accounts for it); entirely above 0 = the trait
  moved less than C (pull partly opposed by selection in the herd); entirely below 0 = the trait moved more than C
  (selection beyond the pull). This replaces reading a trait's point estimate against C's interval.

## exp010 — Herder spooking at a fixed load, not tied to herd size: at which spook loads do herds persist, and do they diverge from the wild?
**Pre-registered:** 2026-11-20. Chris: "can we run a test run where herder spooks is not tied to herd size?". Mongo
animalDomestication.exp010_fixed-load (mint); results/exp010_fixed-load; job list tools/exp010.jsonl (32 runs, cpuslot
--anywhere, queued behind exp009); code 6367599 (counters wildConc/capIn/capBred recorded).
**Why:** exp007 fixed the spook load at its two ends: LOADLO (0.25) gave herds of about 262 in 8 of 8 seeds with every
gap within 0.04 of zero; LOADHI (4.8, REF's established level) let no herd survive. REF's load rises with the herd
(herd goats / 20 per herder, src/world.js:181-183). This fills in the dose-response between the ends with the load
fixed, so the herd's size no longer sets the strength of the spook filter.
**Arms:** REF with herdPerHerder=1e9 and minLoad = 0.5, 1, 2, 3 (LOAD05, LOAD1, LOAD2, LOAD3): spooking as if each
herder always watched 10, 20, 40 or 60 goats. Seeds 1-8, 4000 years. Compared with exp007's LOADLO (0.25) and LOADHI
(4.8), and REF (exp005 seeds 1-4 + exp006 seeds 5-8).
**Measure** (the analysis session; 3201-4000; the standing measures of notes/batch1-plan.md): establishment by herd
size (and time to it), herd, gaps, breadth, the within-arm split, gene flow (flow_tab: captive sires and dams, depth,
wildHerdShare, wildConc, capBred / capIn as first breedings by captives per capture), realized offtake; across the six
load levels (with LOADLO and LOADHI), herd, R gap, breadth and captive-sire share against load.
**Prediction** (mine): herds establish in at least 6 of 8 seeds at 0.5, 1 and 2, and in at most 4 of 8 at 3. Among
established seeds, the R gap falls with load (more negative at each higher level), with LOAD1 between -0.20 and -0.50;
breadth rises with load; the captive-sire share falls with load.
**Decision rule:** if established herds diverge at a fixed load (R gap -0.30 or below and breadth 3 or more at some
level), the divergence needs a spook filter of that strength, not its scaling with herd size, and the paper's question
becomes how strong a filter herders would plausibly impose. If no fixed load gives both a persisting herd and
divergence, the divergence in REF needs the load to grow with the herd: a herd that starts small under a weak filter
and tightens it as it grows. Either way the result goes to Chris for the re-plan.

## exp010 amendment, 2026-11-20 (before any result: 0 of 32 runs finished; the reviewer's prereg review)
- Observable rates per level, registered: run-offs, run-offs fetched back and goats lost (escaped) per herd goat per
  year, from the year rows (ranOff, refetched, escaped over herded), so a level reads as "losses of x% a year" and can
  be set against herd-loss figures.
- Bistability (Q1): if herds at fixed loads 1-3 wait in the small state and then jump (establishment by herd size
  after year 500 with a small-state plateau before it), the waiting does not need the load to scale with herd size;
  if they establish at once or never, the waiting in REF is the scaling rule's doing.
- At a fixed load, herderAlarm and the load enter the spook chance only as their product (src/animals.js:363), so
  this is also a herderAlarm sweep (herderAlarm × load = 0.025, 0.05, 0.1, 0.15 a day for a goat with R × fear 1).
- Follow-up stated now: if LOAD3 establishes in 6 or more of 8 seeds, the edge lies in 3-4.8, and the next run is a
  fixed load of 4, 8 seeds, the same arguments.
- Comparability with exp007 and REF rests on the identity checks: exp007's code reproduces exp005's REF seed 1 (0 of
  1333 year rows differ, 710f1eb); the counters (8dd84a2) and cInitLo (92d8f21) change no run (500-year checks).

## exp010 clarification, 2026-11-20 (before any result; the analysis session's question)
"Breadth rises with load": breadth is an integer count, so it is read as non-decreasing across the levels read (those
with at least 2 established seeds, in load order) AND higher at the highest level read than at the lowest. A tie
between neighbouring levels does not fail it. The continuous measures (R gap falling, captive-sire share falling)
stay strict at each step.

## exp011 — Herder-culture rules in place of the spook filter: do a larder, capture tapering or a nuisance cull close the herd, and does it then diverge from the wild?
**Pre-registered:** 2026-11-20. Mongo animalDomestication.exp011_herder-culture (mint); results/exp011_herder-culture; job
list tools/exp011.jsonl (48 runs, cpuslot --anywhere, queued behind exp009 and exp010); code aab0e86.
**Why** (Chris, 2026-11-20): the paper read "we built a rule where herding selects against reactivity, and our claim is
that herding selects against reactivity". The spook rule is about goats, not culture. "Can we write a rule about human
culture that has the same effect? An opportunistic one?" exp007 showed divergence needs the herd to stop breeding
from captives (closure). Three opportunistic herder rules, each a reason to keep captives out of breeding (aab0e86,
MODEL C57 "Herder-culture rules"):
- larder: once the herd is self-maintaining, a captive that has not yet bred in the herd is kept as meat (no kid,
  milk or sire credit in its keep value); before that every animal counts as herd (Chris: "the larder only is a rule
  once a herd and captives can be distinguished ... it also solves the founding problem mechanically").
- capture tapering: once the herd is self-maintaining, hunters take no goat alive (live capture and orphans).
- nuisance cull: the keep value is charged the herder's chasing labour, nuisanceCost × the goat's observed run-offs
  per year watched × its expected years ahead; judged from behaviour only.
Self-maintaining = at least selfDoes 10 home-born breeding does in the camp's herd (a first choice; herds of ~90 a camp
held about 40 in the probes).
**Baseline for every arm (FLAT):** REF with the spook load fixed at 1 (herdPerHerder 1e9, minLoad 1: spooking as if each
herder watched 20 goats) and runOffLoss 0 (a run-off is always brought back), so spooking removes no goat and selects
nothing by loss; goats still bolt and the herder sees it. logHistDepth 1.
**Probes before registering** (1000 y, seed 3; not results): runOffLoss 0 gives 0 escapes; larder cuts captives' first
breedings per capture from about 0.41 (FLAT) to about 0.1; captureTaper stops all captures once every camp is
self-maintaining (tools/camp_probe.mjs; orphan capture first bypassed it and was then covered); nuisanceCost 0.03 showed
no effect at that seed, so the nuisance cull runs as a dose-response, levels fixed here: 0.03, 0.1, 0.3 meat units
per run-off (0.3 = a weaned kid's worth; herd goats ran off about 1.5 times a year each in the probes).
**Arms** (seeds 1-8, 4000 years): FLAT; NUIS03, NUIS10, NUIS30; LARD (larder 1, selfDoes 10); TAPER (captureTaper 1,
selfDoes 10). REF (exp005 + exp006) and exp007's LOADLO as context.
**Measure** (the analysis session; 3201-4000; the standing measures of notes/batch1-plan.md): establishment by herd size
and time to it; herd; gaps, breadth; the within-arm split; gene flow (captive-sire and captive-dam shares, depth,
wildHerdShare, wildConc, capBred / capIn as first breedings by captives per capture); realized offtake; run-offs,
fetched back and lost per herd goat per year. "Closed" = depth 10 generations or more AND captive-sire share 0.10 or
below; "diverged" = breadth 3 or more on established seeds.
**Prediction** (mine):
1. FLAT: established in 6 or more of 8; breadth 2 or less; R gap above -0.20 (the herd tracks the wild, as LOADLO).
2. LARD and TAPER: both closed; R gap above -0.30 (no rule reads R); breadth 3 or more.
3. NUIS: the R gap falls (more negative) and the captive-sire share falls with nuisanceCost; NUIS30 closed with an R
   gap of -0.30 or below.
**Decision rule:**
- LARD or TAPER closed and diverged with R near the wild: closure by herder culture gives divergence without any rule
  reading reactivity; tameness is then a separate question, answered by NUIS.
- LARD or TAPER closed but not diverged: closure is necessary (exp007) but not sufficient; the paper says what else
  divergence needs.
- NUIS closed with R diverged: a herder judging behaviour recreates REF's pattern through culture, and the spook
  filter can be retired from the reference culture in favour of it.
- No arm closes: these rules, at these settings, do not close a herd; selfDoes and the nuisance levels go to Chris.

## exp011 amendment, 2026-11-20 (before any run started: 0 of 48 begun; the reviewer's prereg review, d265982, and the analysis session's reading questions)
**Code:** the runs will carry 1dd4fa7, which adds two output-only counters to aab0e86 (looseDeaths, herd goats dying
while loose; selfMaintDays, camp-days self-maintaining); identity: 500 y REF seed 3, 0 of 500 year rows differ outside
the new keys. Not done: cInitLo=0.6 on every job (the queued jobs could not be replaced without clearing the shared
queue); the mutation-pull reference comes from exp009 instead.
**"Diverged", restated:** a trait counts toward breadth only if, on established seeds, its herd change against the
founders exceeds both the mutational expectation (exp009's pooled C fraction × (0.5 - F) for that trait, F the arm's
301-400 founders' mean) and the size of its wild change. Branch 1 is read only once exp009 is scored, and through
this restated count.
**Nuisance arms:** NUIS reads observed run-offs, which spooking produces in proportion to R × fear, so it is culture
acting on what spooking shows. Registered for every arm: realized selection on R (selSire, selDam, from the year
rows), so selection on R is told apart from captives being eaten first through their fear. Branch 3 restated: NUIS
closed with R diverged means herder culture can replace the spook filter's loss and its herd-size scaling, not the
spooking itself. New branch: if NUIS30 establishes in 2 or fewer seeds, the cost exceeds what a herd can bear; the
dose-response is then read over FLAT, NUIS03 and NUIS10.
**R gaps** are read paired against FLAT by seed, not against 0. Registered: FLAT - exp010 LOAD1 by seed (they differ
only in runOffLoss: the cleanest test of "loss is the filter"); exp010's LOAD1 is the same-load context arm.
**"Closed"** is classified per established seed, with counts per arm, beside the arm-mean reading. Branch 2 ("closure
necessary but not sufficient") is read with breadth against depth across exp007, exp010 and exp011 together.
**selfDoes 10** encodes demographic self-replacement (enough home-born breeding does), not "captives can be told apart".
If established herds are self-maintaining on 95% or more of camp-days over 3201-4000 (selfMaintDays), no selfDoes
sweep; otherwise a follow-up at 5 and 20, stated now.
**Reading choices (the analysis session's, accepted):** established by the jump_tab herd-size criterion with a
Kaplan-Meier interval, the herd >= 100 count beside it; an arm is read with 2 or more established seeds; "closed" and
"diverged" judged on arm means over established seeds, with per-seed counts; nuisance "falls" = strictly lower at each
step over FLAT, NUIS03, NUIS10, NUIS30 among the levels read; "R near the wild" = R gap above -0.30, "R diverged" = -0.30
or below. Added branch: LARD or TAPER closed and diverged with R at -0.30 or below means closure without any rule built
for it still made herds tamer; read through selection on R (selSire, selDam) and the remaining R-reading rules (tether,
capture's approach test, retrieval).

## exp009 results (raw)
40 of 40 runs complete (complete: true, last year row 3998), every exit 0; every run has cInitLo 0.6 and logHistDepth 1.
34 on the desktop (3535-4679 s), 6 on mint (4901-5371 s). Commits recorded 6367599 to 4afb749 (other sessions'
commits while the batch ran); `git diff 6367599 4afb749 -- src load.mjs tools/runyears.mjs` is empty. Five runs
started with a dirty tree (at d9c3fbe, 75478a4, f2555ff); the uncommitted files then were analysis tools, none in src
(the herder-culture edits to src began after 4afb749, and every 4afb749 run recorded a clean tree). Mongo
animalDomestication.exp009_mutation-pull on mint; JSON in results/exp009_mutation-pull/. Scoring: the analysis
session's "exp009 results (scored)" (tools/shiftc_tab.py, as amended twice).

## exp011 amendment 2, 2026-11-20 (before any result; the reviewer's f3b8433)
- When an arm's mean reading and its per-seed counts disagree on "closed" or "diverged", the per-seed count governs:
  an arm is closed (or diverged) if 6 or more of its established seeds are, not (or not diverged) if 6 or more are
  not, and "mixed" otherwise.
- The mutational expectation scales with generations, not Ne: each arm's generation time (mean age of parents at birth,
  from the records) is reported, and where an arm's generations from year 400 to the window differ from exp009's, the
  expectation from exp009's pooled C is scaled by the ratio of generations.

## exp009 results (scored)
**Scored** 2026-11-20 by the analysis session, as pre-registered and amended twice (a2f5c04, d9c3fbe):
`python tools/shiftc_tab.py 3201-4000 results/exp009_mutation-pull CTLDEEP,CTLRAND,REF` (the tool at 75478a4; its
selftest passes). Standing measures: tools/jump_tab.py; split_tab.py (--perseed, --show-founders); flow_tab.py (--pairs
CTLDEEP-CTLRAND); admix_tab.py (exploratory). Tables in results/exp009_mutation-pull/: scored.txt, jump_herd.txt,
split_3201-4000.txt, split_founders.txt, flow_3201-4000.txt, admix_3201-4000.txt. Window 3201-4000; founders = each
run's own 301-400; fraction = herd change / (0.5 - F).

**As amended:**
1. Validity: herd C fraction CTLRAND - CTLDEEP = -0.074 [-0.349, +0.200] (paired SE 0.129, 16 seeds), within 2 SE: C
   is a valid reference.
2. Pooled C fraction (herd and wild averaged within each run; interval over the 32 CTLDEEP and CTLRAND runs): +0.843
   [+0.719, +0.968]. Width bar: half-width 0.125 <= 0.20, passes.
3. Per trait, paired within-run fraction(C) - fraction(trait), 95% interval:

| arm | runs | A | H | T | R | B |
|---|---|---|---|---|---|---|
| CTLDEEP | 16 | +0.419 [+0.152, +0.686] | +0.521 [+0.194, +0.847] | +0.496 [+0.285, +0.708] | +0.260 [+0.053, +0.467] | +0.706 [+0.514, +0.897] |
| REF | 8 | +0.542 [+0.154, +0.930] | +0.695 [+0.239, +1.150] | -0.663 [-1.081, -0.244] | -1.669 [-2.009, -1.329] | +0.016 [-0.561, +0.593] |

   CTLDEEP: all five traits moved less than C (pull partly opposed by selection in the herd). REF: A and H moved less
   than C; T and R moved more (selection beyond the pull); B inside.
4. Thresholds: the pooled C, 0.843, lies above every range the rule names (selection: below 0.15; unresolved: 0.15-0.3;
   mutational: 0.3-0.6 with A, H and T inside). None of A, H, T is inside. The tool's reading: neither stated case.
   Seed-level sensitivity (each seed's two runs averaged, interval over 16 seeds): +0.843 [+0.713, +0.973], half-width
   0.130, the same reading. It is wider than the run-level interval (0.130 against 0.125), so it is the conservative line.
5. Secondary: CTLDEEP's herd C alone +0.915 [+0.735, +1.094], half-width 0.180.

The fractions (seed mean, 95% t interval in scored.txt): CTLDEEP C +0.91, A +0.50, H +0.39, T +0.42, R +0.65, B +0.21;
CTLRAND C +0.84, A -0.41, H -0.54, T -0.01, R +0.29, B -0.02; REF C +0.79, A +0.25, H +0.09, T +1.45, R +2.46, B +0.77.

**Predictions:**
- The reviewer's mutational case (pooled C 0.3-0.6 with A, H, T inside): not met (0.843; none inside).
- The reviewer's selection case (pooled C below 0.15 with A, H, T near 0.4-0.5): not met. A, H and T sit at 0.39-0.50,
  but the pooled C is 0.843, not below 0.15.
- The steward's (C's fraction in CTLDEEP between 0.15 and 0.45): not met (+0.915 herd C alone).
- CTLRAND's predictions were withdrawn by the amendment; the validity check that replaced them passes.

**Decision rule:** none of its three outcomes (mutational / selection / unresolved) applies, because the pooled C lies
above the ranges it names. What the registered measures show: under the same pull, the neutral marker moved 0.84 of the
way to 0.5 over 3201-4000. In the same runs each of A, H, T, R and B in the deep herd moved significantly less than C
(paired intervals entirely above 0). So the pull alone would have carried these traits further toward 0.5 than they
went. The amended per-trait reading for all five is "pull partly opposed by selection in the herd". How the paper words
this is for the steward and the author.

**Standing measures:**
- Establishment (herd size): CTLDEEP 16 of 16 and CTLRAND 16 of 16 at once (501); REF 8 of 8, median 705, KM 0.75
  [0.44-0.96] by 800. No fall-backs; no late crossings.
- Split (seed means): CTLDEEP herd / wild change R -0.191 / -0.058, A -0.114 / +0.090, H -0.108 / +0.098, T +0.131 /
  -0.018, B -0.078 / +0.019, C -0.258 / -0.213. CTLRAND's herd tracks its wild on every trait (largest gap R -0.026).
- Gene flow, CTLDEEP - CTLRAND paired over 16 seeds: captive-sire share -0.060 (0.003) (CTLDEEP 0.000, CTLRAND 0.060);
  depth +9.46 (0.20) generations (19.61 against 10.15); wildHerdShare -0.119 (0.009); first breedings per captured buck
  -0.039 (0.003). Captures, captive-dam share and wildConc's herd-sire share are equal. No escapes in either CTL arm.

**Exploratory** (not registered):
- The neutral C has a gap in the deep herd: -0.045 (SE 0.018; herd change -0.258 against wild -0.213), against
  CTLRAND's +0.007 (0.008). So a trait that nothing reads differs between herd and wild by about 0.05 in a closed herd
  of about 209. Not tested: more generations per year in the herd (so more mutations per year), or drift in the small
  herd. It bears on the 0.10 breadth threshold, and on exp011's scaling of the expectation by generations.
- Founders' genotype SD (split_tab --show-founders, seed means): C 0.080; A 0.108, H 0.109, T 0.079, R 0.068, B 0.059.
  The first amendment expected C's founders' spread to be wider than A, H and T's. At the genotype level it is narrower
  than A's and H's and equal to T's. The SD is of goats' allele means, not of alleles; no record holds alleles.
- admix_tab: no wild goat in the CTL arms is free of herd-born ancestry (CTLDEEP has 83% of wild goat-years in the 1/4-1/2
  herd-born bin), so the low-admixture comparison cannot be made there. REF: herd against wild goats with no herd-born
  ancestry, R -0.598 (0.008), against -0.636 for all wild.

## exp011 clarification, 2026-11-20 (before any result; the analysis session's questions on amendment 2)
- Generation scaling: exp009's runs lack a parent-age record, so the ratio uses the same proxy on both sides: median
  age at first kidding (herd and wild pooled as the pooled C is). exp011's runs carry parentAge (0850eb3, output only;
  identity: 500 y, 0 of 500 rows differ outside the new keys), and the mean parent age at birth is reported beside it.
- The mutational expectation uses exp009's pooled C fraction (+0.843, as registered); herd C alone (+0.915) is
  reported beside it as a sensitivity line.
- "Herd change exceeds the mutational expectation", signed: a trait counts if its herd change goes further than the
  expected pull in the pull's direction, or goes against the pull (away from 0.5); and, as before, its herd change
  exceeds its wild change in size and abs(gap) >= 0.10.
- R thresholds are read paired against FLAT; FLAT itself against 0. Branch 2 reads exp007 and exp010 when their
  folders are given.

## exp011 amendment 3, 2026-11-20 (before any run started: 0 of 48 begun; the reviewer's exp009 results review, 65cc886)
**The divergence null, revised.** The C-fraction null (exp009's pooled C × (0.5 - F)) holds only for a herd closed to
inflow: C relaxes in herd and wild alike, while a trait the wild holds by selection keeps flowing into the herd. With
inflow m (wild genome share entering the herd per generation) and the pull r per generation (from exp009's C over its
generations), a herd without selection on a trait sits at about its wild mean + r / (m + r) × (0.5 - wild mean), plus
the arm's own C herd-wild gap. A trait counts toward breadth if its herd-wild gap departs from that null (signed, as in
the clarification) and abs(gap) >= 0.10. The C-fraction null is kept only for herds closed to inflow (m near 0, e.g.
TAPER once it stops capturing).
**Validation of the null, before it is used:** it must predict the neutral marker C's own herd-wild gap in REF,
CTLDEEP and CTLRAND (exp009, and exp005/006/007 where C is unshifted) within its interval. It is not calibrated
against any selected trait; in particular no target is set for REF's B.
**m** is estimated per arm from the conception records (half the share of herd conceptions by captive sires plus
half that by captive dams, per generation) and reported beside depth; depth is capped at 23 (WV_DEPTH 24), so TAPER
may saturate it.
**"Closed" set aside as a binary.** exp007 and exp009 show its line (depth >= 10, captive-sire share <= 0.10) does not
separate herds that diverge from herds that track the wild: CTLRAND passes it (depth 10.15, captive-sire 0.063) and
tracks the wild, while REF (14.7, 0.064) diverges. Changed after seeing exp009, before any exp011 result: branch
readings use m as a continuous measure, with breadth against m across exp007, exp009, exp010 and exp011, read as
migration-selection balance (divergence where selection in the herd outweighs inflow). The closed/not counts still
print, for reference only.

## exp011 amendment 4, 2026-11-20 (before any run started; the reviewer's e72dff2)
- **Validation restated so it can fail:** the C-gap part of the null is checked on C without C's own gap inside it:
  the null must predict C's herd-wild gap as about 0 within its interval in REF, CTLDEEP and CTLRAND. The inflow term
  r / (m + r) × (0.5 - wild mean) has no neutral test in the record (C's wild relaxes too, so the term is about 0 for C
  whatever m is); it is model-derived and untested, and is reported as such. Breadth is reported twice: with that
  term at 0, and at the m used. A test of the term needs a neutral marker held away from 0.5 in the wild (new code;
  for the re-plan).
- **Which m:** divergence is read on the realized inflow, from the herd's wild ancestry (herdWildAnc / herdAncDepth,
  with the depth cap at 23 undone), by a committed conversion in tools/; the conception-based m (half the captive-sire
  share plus half the captive-dam share) is reported beside it. The conception figure is larger where captives'
  lineages do not persist (CTLDEEP about 0.043 against about 0.015 realized) and would shrink the null, so it is the
  anti-conservative choice and is not used for the reading.

## exp011 amendment 5, 2026-11-20 (before any run started; the reviewer's ac4160d)
The restated C check already fails in exp009's CTLDEEP: C's herd-wild gap is -0.045 (SE 0.018), excluding 0; REF and
CTLRAND pass. What that means for exp011, decided now:
- The C part of the null is validated only for arms where C's gap is about 0 (checked per exp011 arm by the same
  test). In an arm where C's gap departs from 0, the arm's own C gap is used as an empirical neutral offset, labelled
  unvalidated, and that arm's breadth is reported with and without it.
- Two candidate causes of a neutral offset, neither yet tested: (a) selection on ancestry (CTLDEEP's sire rule,
  world.js sireRule 'deep'; LARD's unbred-captive rule), which is correlated with every allele that differs between
  herd and wild, C included (the reviewer's); (b) herd generations shorter than the wild's (herd parents about 4.5 y
  at a litter against about 6 y in the wild, parentAge, 0850eb3), so a closed herd takes more mutation steps per year
  and relaxes faster toward 0.5 than its wild. (b) predicts the offset in any arm with low inflow, scaled by the
  generation ratio; (a) predicts it only where ancestry is selected. exp011's TAPER (low inflow, no ancestry
  selection) against LARD separates them; parentAge gives the generation ratio per arm.
- The analysis session reports, for exp009's CTLDEEP, C's gap by seed (sign count) and herd against wild first-kid
  age, before exp011 is scored.

## exp011 amendment 6, 2026-11-20 (before any run started; the steward's decision after the analysis session's inflow table, a96d554)
The inflow-aware null of amendments 3-5 needs a single inflow m, and exp009's CTLDEEP shows a herd that one number
misdescribes: wild genes arrive (herdWildAnc depths 0-4 hold about 15% of the genome) but are lost within about four
generations, while the persistent core (84% at depth 20+) takes in about 0.0006 a generation, below the pull. Rather
than choose among m definitions or build a two-pool null now, divergence is read as follows:
- **Primary (conservative):** against the closed-herd null, exp009's pooled C fraction × (0.5 - F), scaled by the
  arm's generation ratio (amendment 2, clarification). Inflow from a selection-held wild can only reduce the drift a
  herd shows, so a trait whose herd change goes beyond this null toward 0.5, or moves away from 0.5, has diverged
  whatever the inflow; together with abs(herd change) > abs(wild change) and abs(gap) >= 0.10. This bound can miss
  divergence; it cannot invent it.
- **Secondary (model-dependent):** the inflow-aware null at two m: the arrival rate (from the depth profile's shallow
  bins) and the flow reaching the core (depths 10-19), with the shape check reported; labelled model-dependent.
- The per-arm C check and offset (amendment 5) stand. A two-pool null is for the re-plan if the secondary reading
  matters to a claim.
This supersedes the reading of amendments 3 and 4 where they differ; their measures are still reported.

## exp011 amendment 7, 2026-11-20 (before any run started; the reviewer's ed0c0a5)
- The primary (closed-herd) null's pull fraction is 0.95, CTLDEEP's core C fraction in exp009, not the pooled 0.843
  scaled: a nearly closed core relaxed further than the pooled estimate, and exp011's runs (C unshifted) cannot
  measure their own pull. At 0.95 the primary reading cannot invent divergence; it is the bound.
- For arms whose ancestry profile passes the geometric shape check (REF-like), the inflow-aware null rests on measured
  ancestry, and both readings are reported side by side as findings; for arms that fail the shape check it stays
  secondary and model-dependent.

## Code note, 2026-11-20: output-only counters added while exp010 and exp011 were queued (identity checks)
Each was committed before it could reach a run, then checked: tools/runyears.mjs 500 years, REF arguments, seed 3, file
mode, compared by tools/cmp_years.py with the previous code's output, the new keys excluded.
- 8dd84a2 (wildConc, capIn, capBred): 0 of 500 year rows differ.
- 92d8f21 (cInitLo/cInitHi, default [0,1]): 0 of 500 differ; cInitLo=0.6 differs only in C's fields.
- aab0e86 (herder-culture switches, all off): 0 of 500 differ; smoke PASS.
- 1dd4fa7 (looseDeaths, selfMaintDays): 0 of 500 differ.
- 0850eb3 (parentAge): 0 of 500 differ.
- 434ee46 (cohortBirth, cohortBreed: viability): 0 of 500 differ.
- a659a59 (firstSireAge, a buck's age at first siring): 0 of 500 differ. exp011's runs will carry a659a59.
exp011's runs (none begun when these landed) will carry a659a59 rather than the registered 1dd4fa7; the sim's
behaviour is the same. exp010 spans code versions (its earlier runs predate some counters): each run's commit is in
its saved parameters and goes in exp010's raw provenance, and the counters are not read for exp010 (the runs that
carry them are a non-random subset).

## exp011 amendment 8, 2026-11-20 (before any run started; Chris's decision)
Chris: relaxed selection is the change the theory predicts (the grain paper's result needed it), and the
mutation-pull and inflow analysis "doesn't belong in our paper ... it's too far down a branch". So:
- "Diverged" goes back to the registered measure: breadth 3 or more (core traits with abs(gap) >= 0.10) on established
  seeds, by per-seed votes (amendment 2). Relaxation-driven change counts as divergence.
- The pull and inflow nulls of amendments 1 and 3-7 (C-fraction, closed-herd bound, inflow-aware, offsets) are
  demoted to exploratory: computed and kept, not used for the predictions or the decision rule, not for the paper.
- Everything else stands: the standing measures (establishment by herd size, the within-arm split, gene flow, R
  paired against FLAT, FLAT - LOAD1, selection on R, loss rates, selfMaintDays, the per-seed closure counts).

## exp012 — The genome's cost reinstated on conception chance (smooth gradient): does relaxed selection then give directional change in closed herds, as in the grain model?
**Pre-registered:** 2026-11-20. Chris: the mutation-pull analysis is "too far down a branch" for the paper; "try an
experiment that reinstates the gene cost ... maybe on conception chance or something that will have a smooth
selection gradient". Mongo animalDomestication.exp012_gene-cost (mint); results/exp012_gene-cost; job list
tools/exp012.jsonl (40 runs, cpuslot --anywhere, queued behind exp010 and exp011); code a659a59 (no new sim code).
**Why:** the grain paper's syndrome came from relaxed selection with a cost that makes a trait whose benefit is removed
decay toward 0. Here that cost has been off since 2026-11-03 (reproCostGrowth, reproCostFertility 0), so relaxed traits
drift toward 0.5 under mutation instead (exp009). The cost on conception (src/animals.js fertility(): 1 -
reproCostFertility × p, p = the goat's mean of the eight core expressed traits; each mating's conception chance ×
both parents' fertility) is linear in p, a smooth gradient, and acts on wild and herd alike. The growth cost stays off.
**Arms** (seeds 1-8, 4000 years; exp007's arguments):
- REF25, REF50: the reference culture with reproCostFertility 0.25, 0.5.
- DEEP25, DEEP50: CTLDEEP (no spooking, random cull 0.13, sireRule deep: a nearly closed herd) at 0.25, 0.5.
- RAND50: CTLRAND (the same, sireRule random: a herd that tracks the wild) at 0.5, the open-herd contrast.
Compared with the same cultures at cost 0: REF (exp005 seeds 1-4 + exp006 seeds 5-8), CTLDEEP and CTLRAND (exp007).
**Measure** (the analysis session; 3201-4000; the standing measures): establishment by herd size; herd; gaps and
breadth (abs(gap) >= 0.10, established seeds); the within-arm split; gene flow; wild means against cost 0 (the cost
moves the wild too); per arm, the number of core traits whose herd sits below its wild by 0.10 or more (decay) and
above by 0.10 or more.
**Prediction** (mine):
1. Wild means of the core traits fall with the cost: at 0.5, at least 5 of 8 core traits lower than at cost 0 by 0.05
   or more.
2. DEEP50: breadth at least CTLDEEP's at cost 0 (6), and at least 4 core traits with the herd below the wild by 0.10
   or more (directional decay).
3. RAND50: breadth 2 or less (the open herd still tracks the wild).
4. Herds establish in at least 6 of 8 seeds at 0.25 in every arm.
**Decision rule:** if 2 and 3 hold, the cost gives the grain model's mechanism in goats: closure plus relaxed selection
gives directional change toward lower trait values, and an open herd does not; this goes to Chris for the re-plan
(whether the cost returns to the reference culture). If DEEP50 is no more directional than at cost 0, the cost does
little here, as was judged on 2026-11-03. If herds fail to establish at 0.5, the reading uses 0.25. Note: the cost
moves the wild's calibrated means (wild B 0.873 at cost 0, exp004), so these arms are a mechanism test, not a
recalibrated culture.

## exp012 amendment, 2026-11-20 (before any run started: 0 of 40 begun; the reviewer's prereg review, 12e1e47)
**Predictions 2 and 3 replaced** (as written they could not fail: exp007's CTLDEEP at cost 0 already has breadth 6 with
four traits 0.10 below the wild, and CTLRAND breadth 0; breadth is also unsigned). The measured quantity is now the
one the cost reads: the mean core gap, herd p - wild p (p = mean of the eight core genotypes), and its change from
cost 0, same seeds 1-8 (cost-0 values: CTLDEEP -0.049, CTLRAND -0.006, REF -0.087).
**Control arm added:** DEEPFLAT50: CTLDEEP at cost 0 with matingConception 0.356, the mean conception chance the cost
gives at 0.5 (0.7 × (1 - 0.5 × 0.574)², 0.574 = CTLDEEP's all-goat mean core p at cost 0, exp007, 3201-4000): the same
demography with no gradient (approximate, since p moves under the cost). Seeds 1-8. The cost's selective effect is
read as DEEP50 - DEEPFLAT50.
**Registered measures added:** the selection differential on p (the mean over the eight core traits of selDam and of
selSire, from the year rows) per arm, against exp007's CTLDEEP / CTLRAND and REF at cost 0; per-trait signed gap
change from cost 0; decay read through the within-arm split (herd change and wild change against the founders).
There is no counter of conceptions per heat or of does ending a season unmated; the selection differential stands
in for whether the cost selects.
**Predictions** (replacing 1-3; 4 stands):
1. Wild: the wild mean core p is lower at cost 0.5 than at cost 0 (interval excluding 0), with T predicted separately
   to rise (a per-heat cost favours a longer season, as on 2026-11-03).
2. DEEP50 - CTLDEEP (cost 0), mean core gap: below 0, 95% interval excluding 0.
3. RAND50 - CTLRAND (cost 0), mean core gap: 95% interval including 0.
4. (stands) herds establish in at least 6 of 8 seeds at 0.25 in every arm.
5. DEEP50 - DEEPFLAT50, mean core gap: below 0, interval excluding 0.
6. REF50 - REF (cost 0), mean core gap: below 0, interval excluding 0; REF25 between REF and REF50.
7. The selection differential on p is more negative in DEEP50 than in CTLDEEP at cost 0.
**Decision rule (replacing the first):**
- 2, 3 and 5 hold: the cost gives directional change toward lower trait values through selection in a closed herd and
  not in an open one: the grain model's mechanism in goats. To Chris for the re-plan.
- 2 holds and 5 fails: the change is the cost's demographic effect, not its gradient.
- 2 fails and 7 fails: the cost does not select here (a doe retries each cycle, so the per-heat cost is diluted); the
  null says nothing about the mechanism.
- 2 fails and 7 holds: selection on p is present but swamped in the herd.
- 2 holds and 3 fails (RAND50 also below 0): the change is not specific to closed herds.
- Herds fail to establish at 0.5 in an arm: that arm is read at 0.25.
**Wording for the paper (the reviewer's):** at cost 0, the direction of relaxed change toward 0.5 is set by the clamped
uniform mutation kernel (src/genome.js mutateAllele): it is relaxed selection with the mutation model's direction, not
decay and not herder selection.
**Identity check added (the reviewer's point 5):** CTLDEEP seed 1, 4000 years, cost 0, on the current code (a659a59),
--scratch, against exp007's CTLDEEP_seed1 by tools/cmp_years.py (the earlier checks covered 500 years, 100 of herding).

## exp012 amendment 2, 2026-11-20 (before any run started; the reviewer's 2caaf62)
- DEEP50 and DEEPFLAT50 are reported side by side on herd births per doe-year, mean age at first kidding, herd size and
  wild size. If they differ beyond noise, the demographic match is incomplete, and prediction 5's difference is said
  to carry part of the demographic effect, next to it.
- There is no flat arm at 0.25: where an arm is read at 0.25 (herds failing at 0.5), prediction 5 cannot be read.

## exp012 clarification, 2026-11-20 (before any result; the analysis session's reading choices, a7b98b0, accepted)
Prediction 1 holds only if wild p is lower (interval excluding 0) in every 0.5 arm, and T rises in every 0.5 arm;
gap and selection changes over seeds established in both arms, wild changes over all seeds; prediction 7 on the
mid-parent differential, paired interval below 0; "fails to establish" = fewer than 2 established seeds (DEEP50 falls
back to DEEP25, REF50 to REF25, RAND50 has none); prediction 6's "between" on paired means; "beyond noise" = paired 95%
interval excluding 0; breadth and the below/above counts over the 9 core traits, p over the 8 that fertility() reads.
The cost-0 mean core gaps quoted in the amendment are -0.0485, -0.0063, -0.0865 unrounded.

## exp010 provenance check, 2026-11-21 (after the 32 runs finished, before any scoring)
All 32 runs finished, but 14 started with a dirty tree. Eleven are at 4afb749-dirty: LOAD05, LOAD1 and LOAD2 seeds
1-3, and LOAD3 seeds 1-2, started 16:54-17:51 PST on 11-20. The herder-culture edits to src/world.js and src/params.js
were then uncommitted and in progress; they were committed at 17:55 as aab0e86. Three more are at a659a59-dirty or
ded6069-dirty: LOAD05, LOAD1 and LOAD2 seed 8, started about 19:00. What was uncommitted then is not recorded. So these
14 runs may have carried a half-edited sim.
**Check:** each of the 14 runs again for 800 years on clean committed code, with the same arguments and the same
recording periods as a 4000-year run (recordEvery 3, histPeriod 15, reportingPeriod 1080), in --scratch, under the
dev tag. Job list: tools/exp010_prov.jsonl. Each is compared with the first 800 years of its exp010 run by
tools/cmp_years.py, excluding the counter keys that some runs lack. The committed code is behaviour-identical from
4afb749 to 78ca109; see the code note's identity checks.
**Rule:** a run whose rows all match (0 differ) stands. A run with any differing row is replaced by a full 4000-year
re-run on clean code before exp010 is scored, and the replacement is noted here.
**Amendment (before any re-run finished; the reviewer's b5cc0b7):**
- LOAD1 seeds 1, 2, 3 and 8 first reach 100 herd goats after year 800 (in years 2288, 935, 1472 and 2993). An
  800-year check never runs their code on the large herds they will be scored on. Each is re-run for the full 4000
  years on clean code (LOAD1full_seedS) and compared over all rows. Their 800-year checks still run.
- Positive control: LOAD1 seed 4, a clean run (65e8cc0), re-run for 800 years on the desktop host where it first ran
  (LOAD1ctl_seed4). If it differs from its original, no "differ" among the dirty runs can be read, and the pipeline is
  fixed first.
- Each comparison records cmp_years' shared-key count.
- Recorded: to answer, the reviewer read the saved parameters, the year-row key sets and the first year with 100 or
  more herd goats in all 32 exp010 files. That last figure is close to the establishment result. Parameters are
  identical across the 32 runs except id, seed and minLoad.
- Job list: tools/exp010_prov2.jsonl.
**Result, 800-year checks (2026-11-21):** all 14 are complete, at clean ca6d3ae or 0831d1f on the desktop, with rows for
years 2-797. Each was compared by `python tools/cmp_years.py results/exp010_fixed-load/<RUN>.json
results/_scratch/<probe>/<ARM>prov_<seed>.json`. In all 14, 0 of 266 records differ. The 4afb749-dirty runs share 68
keys with their checks (the checks add the six later counters); the seed-8 runs share 74. The full-length checks of
LOAD1 seeds 1, 2, 3 and 8, and the positive control, are still running.
**Result, full-length checks and control:** LOAD1full seeds 1, 2, 3 and 8 (clean 0831d1f or 736c15d, desktop, 4000 years)
against their exp010 runs: 0 of 1333 records differ. Seeds 1-3 share 68 keys; seed 8 shares 74. The control, LOAD1ctl
seed 4 (clean 0831d1f, desktop, 800 years), against LOAD1_seed4 (clean 65e8cc0): 0 of 266 records differ, 68 shared keys.
The re-run pipeline reproduces a clean original, and none of the 14 dirty-tree runs differs from clean code over its
checked span. **All 32 exp010 runs stand.**

## exp010 results (raw)
32 of 32 runs complete (complete: true, last year row 3998), every exit 0; parameters identical across runs except id,
seed and minLoad (0.5, 1, 2, 3; herdPerHerder 1e9). Hosts: 25 on the desktop and 7 on mint (algorithm0r-Media-2016).
Run times were 2767-11907 s; they ran long while other projects shared the machine. Commits recorded: 4afb749-dirty
(11 runs), 65e8cc0, d265982, ecaf9d3, bbd6259, 06c97bc, 16dfdd2, 6c1cc76, b64a201, a659a59-dirty, ded6069-dirty and
78ca109. Every run's commit is in its saved parameters. The committed sim is behaviour-identical across these commits
(the code note's identity checks), and the 14 dirty runs were checked against clean code above. The output-only
counters added after 4afb749 are in some runs only, and are not read for exp010 (the code note). Mongo
animalDomestication.exp010_fixed-load on mint; JSON in results/exp010_fixed-load/. Scoring: the analysis session, with
tools/load_tab.py and the standing measures.

## exp010 results (scored)
**Scored** 2026-11-21 by the analysis session, as pre-registered (4aaf978), amended (071fd3e) and clarified (f2555ff):
`python tools/load_tab.py "results/exp010_fixed-load;results/exp007_design-checks;results/exp005_b0-pilot;results/exp006_two-corner"`
(the tool at f2555ff; its parameter guard checked every exp010 run's herdPerHerder and minLoad, and none stopped it).
Standing measures over the same folders, arms LOADLO,LOAD05,LOAD1,LOAD2,LOAD3,LOADHI,REF: tools/jump_tab.py;
split_tab.py 3201-4000 (--perseed, and --min-herd 100); flow_tab.py 3201-4000 (--perseed, --pairs between neighbouring
levels). Tables in results/exp010_fixed-load/: scored.txt, jump_herd.txt, split_3201-4000.txt,
split_est_3201-4000.txt, flow_3201-4000.txt. Window 3201-4000. The output-only counters added after 4afb749 are not read.

**Dose-response** (est = herd >= 100 over the window, exp007's definition, which the predictions read; by-herd = the
jump_tab criterion; R, breadth n and captive-sire share over established seeds):

| arm | load | est | by-herd (KM median) | herd | R gap | n | csire | offtake |
|---|---|---|---|---|---|---|---|---|
| LOADLO | 0.25 | 8 | 8 (501) | 261.6 | -0.055 | 0 | 0.288 | 0.124 |
| LOAD05 | 0.5 | 8 | 8 (525) | 261.9 | -0.104 | 1 | 0.333 | 0.121 |
| LOAD1 | 1 | 8 | 7 (1614), 1 late | 245.8 | -0.247 | 1 | 0.311 | 0.121 |
| LOAD2 | 2 | 0 | 0 | 2.1 | - | - | - | - |
| LOAD3 | 3 | 0 | 0 | 1.4 | - | - | - | - |
| LOADHI | 4.8 | 0 | 0 | 0.9 | - | - | - | - |
| REF | grows | 8 | 8 (705) | 287.8 | -0.636 | 6 | 0.064 | 0.133 |

(scored.txt's "median" column takes the upper of the two middle years, so it gives 528 and 717 where jump_tab's KM
median gives 525 and 705.) No herd persists at load 2 or above: herds of 1-3 goats over the window in all 24 runs.
These no-herd runs are counted and not scored as gaps.

**Predictions:**
1. Established in >= 6 of 8 at 0.5, 1 and 2, and in <= 4 of 8 at 3: **not met** (8, 8, 0; 0). The edge lies between
   loads 1 and 2, not between 2 and 3.
2. R gap of established seeds more negative at each higher level read (LOADLO, LOAD05, LOAD1; the only levels with 2
   or more established seeds): **met** (-0.055, -0.104, -0.247).
3. LOAD1 R gap between -0.50 and -0.20: **met** (-0.247).
4. Breadth rises with load (non-decreasing, highest level read above lowest; clarification f2555ff): **met** (0, 1, 1).
   It rests on LOADLO's 0: exp010's own two levels read tie at 1. The 1 at LOAD05 and LOAD1 is R alone.
5. Captive-sire share falls with load: **not met** (0.288, 0.333, 0.311). It rises from LOADLO to LOAD05 (paired
   +0.044, SE 0.012), then LOAD1 - LOAD05 is -0.022 (0.028).

**Decision rule:** no level has established herds with R gap <= -0.30 and breadth >= 3. Registered outcome: no fixed
load gives both a persisting herd and divergence, so REF's divergence (R -0.636, breadth 6) needs the load to grow
with the herd. The result goes to Chris for the re-plan. The amendment's follow-up (a fixed load of 4) was conditional
on LOAD3 establishing and does not apply.

**Flag, est against the jump criterion (LOAD1):** est counts 8 of 8, the jump criterion 7 by its follow-up end (3599).
Seed 5 crosses late (3708, inside the window; window herd 111), so part of its window is small-state. Seeds 6 and 8
establish at 3171 and 3039, just before the window. Per-seed LOAD1 R gaps (split_tab): -0.399, -0.314, -0.292, -0.290,
-0.056 (s5), -0.127 (s6), -0.372, -0.127 (s8). The late seeds have the smallest gaps. Dropping seed 5 cannot change a
reading: it has the least negative R gap, so predictions 2 and 3 hold either way (no seed is below -0.50). Prediction 5
fails at its first step, LOADLO to LOAD05, which LOAD1 does not enter. And every LOAD1 per-seed |gap| outside R and T
is below 0.10, so breadth stays at most 2 for any subset and the decision rule cannot fire. A subset mean was not
computed.

**Observable rates** (amendment; per herd goat per recorded year, seed mean (SE)):

| arm | run-offs | fetched back | lost (escaped) |
|---|---|---|---|
| LOADLO | 0.359 (0.004) | 0.205 (0.002) | 0.074 (0.001) |
| LOAD05 | 0.631 (0.011) | 0.369 (0.006) | 0.122 (0.003) |
| LOAD1 | 0.911 (0.085) | 0.550 (0.046) | 0.154 (0.020) |
| LOAD2 | 3.764 (0.068) | 1.886 (0.036) | 1.013 (0.018) |
| LOAD3 | 5.753 (0.092) | 2.845 (0.045) | 1.648 (0.049) |
| LOADHI | 8.629 (0.210) | 4.115 (0.102) | 2.688 (0.052) |
| REF | 0.859 (0.042) | 0.577 (0.029) | 0.082 (0.004) |

Herds that persist lose 7-15% of their goats a year. REF loses 8%, about the rate of LOADLO, with run-offs near
LOAD1's. Rates at loads 2 and above are over herds of 1-3 goats and are rates of the capture-and-loss cycle, not of a
herd.

**Bistability (Q1):** LOAD1 waited in the small state and then jumped in 7 of 8 seeds (plateaus of 5-12 goats before
the jump; jump years 978-3171), with seed 5 a late crossing. LOAD05 established at once or grew (2 and 6), and
LOADLO at once in 7. LOAD2 and LOAD3 never established. The amendment's reading: the waiting does not need the load to
scale with herd size. Context: REF's 8 seeds are classed "grew", not "waited", by the same plateau criterion (100-year
herd mean under 60 for 300+ years).

**Standing measures:**
- Establishment (herd size, KM): LOADLO 1.00 by 800; LOAD05 1.00 by 800; LOAD1 0.00 by 800, 0.25 [0.07-0.69] by 1200,
  0.50 [0.23-0.85] by 2000, 0.88 [0.58-0.99] by 3200; REF 0.75 [0.44-0.96] by 800, 1.00 by 1200; LOAD2, LOAD3 and
  LOADHI 0. No fall-backs.
- Split (established seeds; herd change / wild change against each run's founders): R LOADLO -0.151 / -0.096, LOAD05
  -0.234 / -0.129, LOAD1 -0.374 / -0.127, REF -0.714 / -0.078. T LOADLO +0.264 / +0.225, LOAD05 +0.320 / +0.285, LOAD1
  +0.219 / +0.159, REF +0.459 / +0.012. At fixed loads the wild moves with the herd on T, and on R by part of the herd's
  change; in REF it barely moves on either.
- Gene flow (flow_tab): captive-sire share LOADLO 0.288, LOAD05 0.333, LOAD1 0.311, REF 0.064. Herd lineage depth 4.66,
  3.95, 4.56, against REF 14.69. The wild genome's herd-born share (wildHerdShare) is 0.886, 0.844 and 0.721, against REF
  0.128. Wild conceptions by a herd sire (wildConc share) 0.003 at LOAD05 and 0.002 at LOAD1. First breedings per capture
  (capBred / capIn) are 0.635 for does and 0.121 for bucks at LOAD05, and 0.574 and 0.107 at LOAD1; LOAD1 - LOAD05 is
  -0.062 (0.008) and -0.014 (0.003), paired. Persisting fixed-load herds are open (about a third of conceptions by
  captured sires) and shallow, and their losses have made the wild mostly herd-descended. REF's herd is closed and deep.

## exp011 results (raw)
48 of 48 runs complete (complete: true, last year row 3998), every exit 0, every run on a clean tree. Arms as registered,
8 seeds each: FLAT; NUIS03, NUIS10 and NUIS30 (nuisanceCost 0.03, 0.1, 0.3); LARD (larder 1, selfDoes 10); TAPER
(captureTaper 1, selfDoes 10). Every run has herdPerHerder 1e9, minLoad 1, runOffLoss 0 and logHistDepth 1. Parameters
are identical across runs except id, seed, larder, captureTaper, nuisanceCost and selfDoes. Hosts: 37 on the desktop and
11 on mint. Run times 5045-12654 s. Commits: 78ca109 (10), 0831d1f (3), 736c15d (8) and 4c92797 (27).
`git diff 78ca109 4c92797 -- src load.mjs tools/runyears.mjs` is empty, and src is unchanged from a659a59 to 78ca109, so
every run carries a659a59's sim: the code note's identity chain, which says amendment 1's registered 1dd4fa7 behaves the
same. FLAT is exp010's LOAD1 with runOffLoss 0 (a run-off is always brought back); compared row by row with
tools/cmp_years.py, 1200 of 1333 records differ from year 401 on, as they should: herding starts at 400. So FLAT is not
an identity check; it is the registered loss-off contrast. Mongo animalDomestication.exp011_herder-culture on mint; JSON in
results/exp011_herder-culture/. Scoring: the analysis session, with tools/culture_tab.py as amended (8) and
tools/cohort_tab.py.

## exp011 results (scored)
**Scored** 2026-11-21 by the analysis session, as registered (65e8cc0) and amended through amendment 8 (d68a794):
`python tools/culture_tab.py "results/exp011_herder-culture;results/exp010_fixed-load;results/exp005_b0-pilot;results/exp006_two-corner;results/exp007_design-checks" --perseed`
(the tool at 903b4b1; selftest passes, `selftest bad` fails as it should; its parameter guard passed on every run).
Standing measures: tools/jump_tab.py; split_tab.py 3201-4000 (--perseed, --min-herd 100); flow_tab.py 3201-4000
(--perseed, --pairs each arm against FLAT, and FLAT-LOAD1). Tables in results/exp011_herder-culture/: scored.txt,
selftest.txt, selftest_bad.txt, jump_herd.txt, split_3201-4000.txt, split_est_3201-4000.txt, flow_3201-4000.txt. Window
3201-4000. Divergence is plain breadth (abs(gap) >= 0.10, per-seed votes) and nothing else. The tool prints the
exploratory null readings and checks that the registered reading is the same under each one (it is). They are not
reported here; nor is cohort_tab, which was not run (the steward: Chris put both out of the paper).

**Arms** (established by the jump_tab criterion; everything after herd over established seeds; R vs FLAT paired by seed):

| arm | est (KM median) | herd | R gap | R vs FLAT | breadth | traits | depth | csire | closed | diverged |
|---|---|---|---|---|---|---|---|---|---|---|
| FLAT | 8 (501) | 260.1 | -0.030 | - | 0 | - | 6.87 | 0.218 | 0 of 8 | 0 of 8 |
| NUIS03 | 8 (501) | 253.9 | -0.041 | -0.010 (0.003) | 0 | - | 6.44 | 0.239 | 0 of 8 | 0 of 8 |
| NUIS10 | 8 (708) | 255.1 | -0.055 | -0.025 (0.007) | 0 | - | 5.94 | 0.259 | 0 of 8 | 0 of 8 |
| NUIS30 | 0 | 2.0 | - | - | - | - | - | - | not read | not read |
| LARD | 8 (501) | 271.2 | -0.069 | -0.039 (0.029) | 6 | A S B H T W | 20.80 | 0.005 | 8 of 8 | 8 of 8 |
| TAPER | 8 (501) | 267.8 | -0.117 | -0.087 (0.034) | 6 | R A S H T W | 22.23 | 0.003 | 8 of 8 | 8 of 8 |
| REF | 8 (705) | 287.8 | -0.636 | -0.605 (0.003) | 6 | R A S B T L | 14.69 | 0.064 | 8 of 8 | 8 of 8 |
| LOADLO | 8 (501) | 261.6 | -0.055 | -0.025 (0.005) | 0 | - | 4.66 | 0.288 | 0 of 8 | 0 of 8 |
| LOAD1 | 7 (1614), 1 late | 245.8 | -0.274 | -0.246 (0.044, 7) | 1 | R | 4.94 | 0.302 | 0 of 7 | 0 of 7 |

(scored.txt's "median year" is the upper median of the established runs' years, 771 for NUIS10; the KM median from
jump_tab is given here.) Per-seed breadth, LARD: 8, 3, 5, 3, 3, 3, 9, 6; TAPER: 6, 8, 5, 5, 6, 4, 4, 3. Every
per-seed and arm-mean reading agrees, so no arm is mixed. "Closed" is far from its line in every arm (depth 20.8-22.2
and csire <= 0.005 for LARD and TAPER; 5.9-6.9 and 0.22-0.26 for FLAT and NUIS).

**Predictions:**
1. FLAT established in >= 6 of 8, breadth <= 2, R gap above -0.20: **met** (8, 0, -0.030).
2. LARD and TAPER closed, R gap above -0.30 (vs FLAT), breadth >= 3: **met** for both (LARD -0.039, breadth 6; TAPER
   -0.087, breadth 6).
3. Nuisance dose-response: NUIS30 established in no seed, so it is read over FLAT, NUIS03 and NUIS10 (amendment 1). R gap
   falls with nuisanceCost: met (+0.000, -0.010, -0.025 vs FLAT). Captive-sire share falls: **not met** (0.218, 0.239,
   0.259; NUIS10 - FLAT +0.042, SE 0.012, paired). NUIS30 closed with R <= -0.30: not applicable. Prediction 3: **not
   met**.

**Decision rule:**
- LARD and TAPER closed and diverged with R near the wild: closure by herder culture gives divergence without any rule
  reading reactivity; tameness is then a separate question, answered by NUIS.
  "Near the wild" is the registered line, R gap above -0.30 against FLAT. TAPER's R gap is -0.117 against 0, so R also
  counts in its breadth at 0.10 (REF -0.636).
- NUIS30 established in 2 or fewer seeds (0 of 8): the cost exceeds what a herd can bear.
- The NUIS branch (closed with R diverged) does not fire: no NUIS arm closes, and its R moves by -0.010 and -0.025.
- The selfDoes follow-up does not apply: LARD and TAPER are self-maintaining on 0.991 and 0.994 of camp-days (every seed
  0.988 or more; the bar is 0.95).
- The reading is the same with R read against 0 instead of paired against FLAT.

**Registered measures beside the rule:**
- FLAT - LOAD1 by seed (runOffLoss 0 against 1, the same load; 8 seeds): R gap +0.217 (0.048); captive-sire share -0.093
  (0.023); depth +2.31 (0.56); run-offs +0.582 (0.084) and escapes -0.154 (0.020) per herd goat-year. With loss
  switched off, the R gap that LOAD1 builds (-0.247 over the same 8 seeds, load_tab) is gone (FLAT -0.030).
- Selection on R (selSire / selDam R, kids-weighted, established seeds): FLAT +0.000 / -0.001; NUIS03 +0.001 / -0.001;
  NUIS10 +0.002 / -0.001; LARD +0.000 / -0.001; TAPER +0.000 / -0.000; REF +0.005 / -0.001; LOAD1 +0.014 / -0.004.
- Gene flow, paired against FLAT (8 seeds): LARD csire -0.213 (0.004), depth +13.93 (0.24), first breedings per
  captured doe -0.563 (0.024) and buck -0.152 (0.005); captures unchanged (-0.001). TAPER csire -0.215 (0.004), depth
  +15.36 (0.18), captures -0.015 (0.000) per herd goat-year (8-20 captures per seed over the window against about 1000).
  The wild's herd-born share (wildHerdShare) is 0.33-0.36 in every established exp011 arm, against 0.73 in LOAD1 and
  0.13 in REF.
- Loss rates (per herd goat per recorded year): run-offs 1.31-1.49 and fetched back 0.92-1.05 in the established
  exp011 arms; lost 0 and died loose 0 in every exp011 run (escapes counted: 0, checked).
- Split (established seeds, herd change / wild change against founders): LARD T +0.353 / +0.001, B -0.143 / +0.014,
  A -0.011 / +0.093, H -0.025 / +0.083, S -0.139 / -0.250, W +0.109 / +0.209, R -0.120 / -0.051. TAPER T +0.390 /
  +0.003, A -0.039 / +0.083, H -0.064 / +0.082, S -0.125 / -0.256, W +0.101 / +0.239, R -0.177 / -0.060. FLAT and NUIS
  herds track their wild: every gap is under 0.07 in size (largest T, +0.051 to +0.066).
- Branch 2, breadth against depth (exp007, exp010, exp011 arms; established seeds; arm means): breadth 0-1 at depth
  under 7 (LOADLO, CTLSHAL, LOAD05, LOAD1, FLAT, NUIS03, NUIS10), and 0 at CTLRAND (10.06); 3 at NOCULL (17.05); 6 at
  REF (14.69), CTLDEEP (19.61), LARD (20.80) and TAPER (22.23).

**Exploratory** (not registered): the signs of LARD's and TAPER's nine core gaps all match REF's (R, A, B, H, M and W
negative; S, T and L positive). In LARD and TAPER the R gap is small (-0.069, -0.117), against REF's -0.636.

**Exploratory, added after the reviewer's 8fee17d** (culture_tab 48a8de9; the rerun adds only this table, and every
other line of scored.txt is unchanged). Not read by the predictions or the decision rule. The carrier of each breadth
trait uses exp007's more-than-half rule within the arm (gap = herd change - wild change). Breadth over the 8 NT_CORE
traits (genome.js:34) leaves out L.

| arm | breadth | traits (carrier) | herd-carried (arm mean) | seeds herd-carried >= 3 | 8-trait | seeds 8-trait >= 3 |
|---|---|---|---|---|---|---|
| LARD | 6 | A wild, S wild, B herd, H wild, T herd, W wild | 2 | 4 of 8 | 6 | 6 of 8 |
| TAPER | 6 | R herd, A wild, S wild, H wild, T herd, W wild | 2 | 5 of 8 | 6 | 7 of 8 |
| REF | 6 | R herd, A wild, S wild, B herd, T herd, L herd | 4 | 8 of 8 | 5 | 8 of 8 |
| LOAD1 | 1 | R herd | 1 | 0 of 7 | 1 | 0 of 7 |

FLAT, NUIS03, NUIS10 and LOADLO are 0 on all four counts. Per seed, herd-carried / 8-trait: LARD 6/7, 1/2, 4/5, 2/3,
2/2, 2/3, 5/8, 4/5; TAPER 5/6, 5/8, 3/5, 4/4, 2/6, 2/4, 3/4, 1/2. In LARD and TAPER the wild carries the A, S, H and W
gaps; the herd carries T, plus B (LARD) or R (TAPER). Read by amendment 2's vote, herd-carried breadth is mixed in both
arms (4 and 5 of 8 seeds at 3 or more) and 2 at the arm mean. The 8-trait breadth leaves LARD diverged at 6 of 8 (on the
line) and TAPER at 7 of 8.

## exp013 — Herding after the wild has settled: are the closed herds' gaps carried by the herd, or by the wild still settling after the burn-in?
**Pre-registered:** 2026-11-21. Mongo animalDomestication.exp013_late-herding (mint); results/exp013_late-herding; job list
tools/exp013.jsonl (24 runs, cpuslot --anywhere, queued behind exp012); code 577ec9b's sim (a659a59, unchanged).
**Why** (the reviewer's exp011 review, 8fee17d): four of LARD's and TAPER's six breadth traits (A, S, H, W) are carried
by the wild, not the herd. The herd stays near its 301-400 founders while the wild moves the same way in every arm (S
about -0.25, A +0.09, H +0.08, W +0.16 to +0.25). That matches the wild still settling under the wolves after the
300-year burn-in: an old-model no-human run settled only by about year 2900. REF's A and S gaps are wild-carried too.
If so, much of the closed-herd breadth across exp007, exp009 and exp011 measures an unsettled wild, not the herd.
The old S0late check (herding at 2000) ran on the pre-v0.1.0 model and read only R, B and herd size, so it does not
answer this.
**Arms** (seeds 1-8, 6600 years): REFlate, LARDlate, TAPERlate. Each is its year-400 arm exactly (REF: exp005 and
exp006; LARD, TAPER: exp011) with humansAt 2900, herdingAt 3000 and ibdFrom 3000: the same 100 years of hunting
before herding, after 2900 years with no humans. Thinning k = 5.
**Measure** (the analysis session; standing measures of notes/batch1-plan.md): read at equal time since herding.
Window 5801-6600 against the year-400 arms' 3201-4000; founders 2901-3000 against 301-400. Per arm and trait: gap, herd
change hc, wild change wc; breadth (core traits with abs(gap) >= 0.10, per-seed votes as in exp011 amendment 2);
closure (depth, captive-sire share). The wild's settling, from the late arms' own years before 2900 (no humans): per
trait, the century from which the wild mean stays within 0.02 of its 2801-2900 mean.
**Predictions** (mine):
1. The wild has settled before humans arrive: for every core trait, the wild mean stays within 0.02 from century 2701
   at the latest.
2. In the late arms, wild change from founders to window on A, S, H and W is within 0.05, against the year-400 arms'
   0.08-0.25.
3. LARDlate and TAPERlate stay closed (captive-sire share below 0.05 in at least 6 of 8 seeds) and herd change carries
   their gaps: for each trait with abs(gap) >= 0.10, abs(hc) > abs(wc). Whether their breadth reaches 3 I do not
   predict. exp009's mutation pull (pooled C fraction 0.84) says relaxed traits drift toward 0.5 in a closed herd, but
   how far by 3600 years after herding from a settled wild is the question.
4. REFlate keeps an R gap of -0.30 or below, herd-carried.
**Decision rule:**
- If prediction 2 holds and closed late breadth is below 3: the closed-herd breadth of exp007, exp009 and exp011 was
  mostly the wild settling. The re-plan with Chris moves herding to after the wild settles for every arm, and the
  paper reports closure as herd change until then.
- If prediction 2 holds and closed late breadth is 3 or more with herd-carried gaps: the herd diverges from a settled
  wild by itself (relaxation and selection in a closed herd), and the reading "closure gives divergence" stands on
  the late design. The re-plan still moves herding later.
- If prediction 2 fails (the wild still moves 0.05 or more from 2901-3000): the wild is not settled by 2900 either,
  and the settling time goes to Chris before any later design.

## exp013 amendment, 2026-11-21 (before any run started: 0 of 24 begun; the reviewer's prereg review, 92a6acd)
- **Correction to Why:** the old WT run was within 0.05 on every core trait from 1501-1600 on; "settled only by about
  year 2900" overstated it. Herding at 3000 stays, as the safe choice.
- **Control arm WTlate** (seeds 1-8, 6600 years): REFlate's arguments with humansAt 1e9 (no humans, so no herds). It
  shares each seed's history to 2900 with the late arms. Job list tools/exp013_wt.jsonl.
- **P1 restated:** the wild has settled before humans arrive if, for every core trait, the seed-mean wild in 2701-2900 is
  within 0.02 of 2401-2600, and WTlate's wild moves less than 0.05 from 2901-3000 to 5801-6600.
- **P2 restated as human-caused wild change:** per trait (A, S, H, W) and late arm, the wild change from 2901-3000 to
  5801-6600 minus WTlate's over the same span, paired by seed, with a 95% interval. Prediction: under 0.05 in size.
  Also reported: the year-400 arms' wild change minus the late arms' (the burn-in's share).
- **Primary reading** (new): per arm (LARD, TAPER, REF) and per trait (A, S, H, W), the late gap against the year-400
  gap, unpaired 8 v 8, 95% interval of the difference. Prediction: abs(late gap) < 0.10 for A, S, H and W in LARDlate
  and TAPERlate, and for A and S in REFlate, with the difference's interval excluding 0.
- **Which breadth governs:** plain breadth (abs gap >= 0.10, per-seed votes, the 9 traits as in exp011), as amendment 8
  of exp011 set. Herd-carried breadth (culture_tab 48a8de9) and breadth over the 8 NT_CORE traits are reported beside
  it, exploratory. A "mixed" vote fires no divergence branch and is reported as mixed. If LARDlate and TAPERlate
  disagree, each is reported alone, and a claim about closure rests only on what both show.
- **Decision rule, replaced:**
  - P1 fails: the wild's settling time on this code goes to Chris before any later design.
  - P1 holds, human-caused wild change under 0.05 on A, S, H and W: the year-400 closed-herd gaps on those traits were
    the burn-in's settling. The re-plan moves herding to after the wild settles, for every arm, and the paper reads
    closure from the late design.
  - P1 holds, human-caused wild change 0.05 or more on any of A, S, H, W: humans move the wild (hunting, herding), and
    a closed herd's gap on that trait is the herd sheltered from human-driven selection on the wild, a model result.
    Said per trait.
  - In every branch, whether LARDlate and TAPERlate still diverge (plain breadth 3 or more) is read on the late design.
- **Tools:** jump_tab, culture_tab and split_tab hard-code years 300-500 (the reviewer's 92a6acd point 3). The scorer
  offsets founders, the herd series and the generation records by each run's saved herdingAt, and its selftest passes
  on a planted late run before any exp013 result is read.

## exp013 amendment 2, 2026-11-21 (before any run started; the reviewer's 5b1722f)
- **P1's WTlate clause** is restricted to A, S, H and W: WTlate's wild moves less than 0.05 on each from 2901-3000 to
  5801-6600. WTlate's drift on the other core traits is reported beside P1 and decides nothing; the paired P2 already
  removes drift.
- **Branch 2 reads per trait and requires the primary reading.** Where P1 holds and human-caused wild change on a trait
  is under 0.05:
  - late gap under 0.10, with the late-vs-400 interval excluding 0: that trait's year-400 gap was the burn-in's settling;
  - late gap 0.10 or more: the trait is herd divergence from a settled wild;
  - anything else (late gap under 0.10 but the interval includes 0): unresolved, said so.
  The re-plan's move of herding to after the wild settles follows if the burn-in reading holds on any of A, S, H, W in
  either closed arm.
- **Two named checks:**
  - The scorer's selftest must fail when the herdingAt offset is removed.
  - The shared history to 2900 is checked, not assumed: years 1-2900 of WTlate_seed1 against REFlate_seed1,
    LARDlate_seed1 and TAPERlate_seed1 with tools/cmp_years.py (the same thinning, k = 5), 0 rows may differ.

## exp013 clarification, 2026-11-21 (before any run started; the analysis session's reading choices for late_tab)
Adopted, under amendments 1 and 2:
- P1's seed-mean clause is read on each late arm's seed-mean wild, per core trait: 2701-2900 against 2401-2600, within
  0.02. Per-seed settling years, and the count of seeds settled by 2701, print beside it. If the three late arms share
  their history to 2900 seed by seed (checked), the settling rests on 8 histories, not 24, and is reported as such.
- Prediction 3's closure: captive-sire share under 0.05 in 6 or more of 8 seeds; a seed that is not established counts
  as not closed.
- "Diverge" in every branch is plain breadth by per-seed vote (exp011 amendment 2), read for LARDlate and TAPERlate
  separately; a mixed vote reads no divergence.
- An arm is read only if 2 or more of its seeds are established.
The analysis session's other choices, (b) arm-mean wild change as P2, (d) the carrying test on arm-mean breadth traits
and (f) the "neither branch" label, were written to 9522ce9's rule and are superseded by amendments 1 and 2.
Two more (the reviewer's da67400):
- P2's paired human-caused wild change uses all 8 seeds (the wild needs no herd). Both sides are computed the same way:
  the wild mean over every histogram row in the window (WTlate: all goats; late arms: hist minus histHerd), not only
  rows with a herd.
- The per-seed vote answers only the arm-level question, whether LARDlate or TAPERlate still diverges. Amendment 2's
  per-trait burn-in reading uses each trait's arm-mean late gap and the late-vs-400 interval, not a vote.

## exp013 clarification 2, 2026-11-21 (before any run started; late_tab 3f43114's reading choices, accepted)
- P1's seed-mean clause is read on WTlate's 8 seeds (2401-2600 against 2701-2900, abs <= 0.02), with the late arms
  printed beside it. That rests on the shared history to 2900 (amendment 2's check); if any late arm does not share it,
  P1 is read on each late arm separately.
- "Under 0.05" (P1's WTlate clause and P2) means abs(mean) < 0.05. P2's interval is reported and need not exclude
  anything.
- P2's wild change is the window mean of hist minus histHerd minus the founders' all-goat mean. It is defined for
  WTlate, and is paired over all 8 seeds, established or not.
- The primary reading uses gaps over established seeds, unpaired: SE = hypot(SE_late, SE_400), t at min(n) - 1 df.
  "Late gap under 0.10" means abs(arm-mean gap).
- Per-trait branch readings print for REFlate too, marked not governing. The re-plan trigger reads LARDlate and
  TAPERlate only. A closed arm with fewer than 6 closed seeds is still read, flagged "not closed".
- P3 and P4 stand as registered: the amendments replaced the rule, not those predictions. P3's carrying test is read on
  the arm-mean breadth traits, and is vacuous if none reaches 0.10. Correction to the first clarification: its
  superseding of choice (d) applied to the rule, not to P3.
- Gap-based readings need 2 or more established seeds.
- The re-plan trigger reads only a closed late arm (closed as in the first clarification). A late gap that shrinks in an
  open herd can be herd and wild merging, not the burn-in. A "burn-in" reading also needs the gap to have shrunk, not
  flipped sign (the reviewer's 74b70f3).
- "Shrunk" means abs(late gap) < abs(year-400 gap). A late gap of the opposite sign that is 0.05 or more in size (an
  overshoot through zero, e.g. -0.105 to +0.09) reads unresolved, not burn-in.

## exp012 results (raw)
48 of 48 runs complete (complete: true, last year row 3998). Arms as registered, 8 seeds each: REF25, REF50 (threshold
cull, reproCostFertility 0.25 and 0.5); DEEP25, DEEP50 (random cull, sireRule deep, herderAlarm 0); RAND50 (random cull,
random sires); DEEPFLAT50 (cost 0, matingConception 0.356). Every run's parameters match its arm. Hosts: 38 on the
desktop and 10 on mint. Run times 7378-16693 s. Commits: 4c92797 (14), a7e3d14 (33) and 4d3ba9c-dirty (1, RAND50 seed
3, started 20:18:58Z on 11-21). `git diff 78ca109 HEAD -- src load.mjs tools/runyears.mjs` is empty, and no file the sim
loads (src/*.js, load.mjs, tools/runyears.mjs) was modified after 02:56Z on 11-21, so the dirty run loaded committed
sim code; the uncommitted files then were tools or notes. Every run carries a659a59's sim.
**Exit codes:** 45 are 0. Three ran on mint across the cpuslot agent restart at 19:56:58 PST on 11-21 (the CPU-slots
session's notice) and record "unknown (agent restarted)": REF50 seed 7, DEEP25 seed 7, RAND50 seed 8. They were
re-adopted and ran to the end; each result file is complete with last row 3998, and each log ends with the copy-back
from mint.
**Identity run** (amendment, the reviewer's point 5): CTLDEEPid seed 1, 4000 years, cost 0, current code (e53d80f-dirty,
desktop; sim files unchanged since 02:56Z, as above) against results/exp007_design-checks/CTLDEEP_seed1.json with
tools/cmp_years.py: 0 of 1333 records differ, 65 shared keys. Log in results/exp012_gene-cost/idlogs/. exp007's cost-0
runs are the valid baseline for exp012. Mongo animalDomestication.exp012_gene-cost on mint; JSON in
results/exp012_gene-cost/. Scoring: the analysis session, with tools/genecost_tab.py.

## exp012 results (scored)
**Scored** 2026-11-22 by the analysis session, as registered (5a2948f), amended (e53d80f, amendment 2) and clarified:
`python tools/genecost_tab.py results/exp012_gene-cost "results/exp005_b0-pilot;results/exp006_two-corner;results/exp007_design-checks" --perseed`
(the tool at db9a2a6: 2d35e92's scorer plus a reading aid that changes no reading; selftest passes, `selftest bad`
fails). The parameter guard passed on all 48 runs: dose, DEEPFLAT50's matingConception 0.356, and every other parameter
equal to the cost-0 run of the same seed. Keys added since the cost-0 runs are listed and allowed. Checks: the
amendment's quoted cost-0 values recompute (mean core gap CTLDEEP -0.04848, CTLRAND -0.00631, REF -0.08646; CTLDEEP
all-goat p 0.57428), and the split identity passes on every run. Standing measures: tools/jump_tab.py, split_tab.py
(--perseed) and flow_tab.py (--pairs as the scorer's PAIRS), arms REF25, REF50, DEEP25, DEEP50, RAND50, DEEPFLAT50, REF,
CTLDEEP, CTLRAND. Tables in results/exp012_gene-cost/: scored.txt, selftest.txt, selftest_bad.txt, jump_herd.txt,
split_3201-4000.txt, flow_3201-4000.txt. Window 3201-4000. p = the mean of the eight core genotypes.

**Arms** (established by the jump_tab criterion; gap columns over established seeds, wild over all seeds):

| arm | est (KM median) | herd | wild size | mean core gap (SE) | wild p | wild T | sel p mid | breadth | below / above | depth | csire |
|---|---|---|---|---|---|---|---|---|---|---|---|
| REF25 | 8 (735) | 308.2 | 447.2 | -0.126 (0.009) | 0.582 | 0.244 | +0.000 | 7 | 4 / 3 | 14.29 | 0.072 |
| REF50 | 8 (813) | 296.4 | 432.5 | -0.110 (0.016) | 0.557 | 0.308 | +0.000 | 7 | 4 / 3 | 13.86 | 0.070 |
| DEEP25 | 8 (501) | 211.0 | 445.7 | -0.041 (0.013) | 0.588 | 0.222 | -0.003 | 6 | 4 / 2 | 19.98 | 0.000 |
| DEEP50 | 8 (501) | 216.4 | 433.3 | -0.027 (0.015) | 0.560 | 0.263 | -0.002 | 6 | 4 / 2 | 20.49 | 0.000 |
| RAND50 | 8 (501) | 212.1 | 431.8 | -0.009 (0.001) | 0.571 | 0.284 | -0.000 | 0 | 0 / 0 | 12.10 | 0.046 |
| DEEPFLAT50 | 8 (501) | 213.3 | 424.2 | -0.050 (0.014) | 0.612 | 0.331 | -0.003 | 7 | 5 / 2 | 20.50 | 0.000 |
| REF (cost 0) | 8 (705) | 287.8 | 456.6 | -0.086 (0.017) | 0.571 | 0.196 | +0.000 | 6 | 3 / 3 | 14.69 | 0.064 |
| CTLDEEP (cost 0) | 8 (501) | 209.2 | 452.5 | -0.048 (0.010) | 0.590 | 0.163 | -0.004 | 6 | 4 / 2 | 19.61 | 0.000 |
| CTLRAND (cost 0) | 8 (501) | 204.7 | 454.3 | -0.006 (0.001) | 0.596 | 0.169 | -0.000 | 0 | 0 / 0 | 10.06 | 0.063 |

(KM medians from jump_tab; scored.txt's "median year" column is the upper median of the established years, 747 and 852
for REF25 and REF50.) Every arm has 8 of 8 seeds established, so nothing falls back to 0.25. REF50 establishes later:
KM 0.25 [0.07-0.69] by 800, against REF's 0.75 [0.44-0.96].

**Predictions** (paired by seed, 95% intervals; the clarification's reading choices):
1. Wild mean core p lower at 0.5 than at cost 0 in every 0.5 arm: **not met**. DEEP50 - CTLDEEP -0.030 [-0.046,
   -0.014] and RAND50 - CTLRAND -0.025 [-0.040, -0.010] are lower; REF50 - REF -0.014 [-0.035, +0.007] is not. T
   rises in every 0.5 arm, as predicted separately: +0.100 [+0.075, +0.126], +0.115 [+0.078, +0.151] and +0.112
   [+0.090, +0.135].
2. DEEP50 - CTLDEEP, mean core gap, below 0: **not met** (+0.021 [-0.024, +0.066]).
3. RAND50 - CTLRAND, interval including 0: **met** (-0.002 [-0.005, +0.001]).
4. Herds established in >= 6 of 8 at 0.25 in every arm: **met** (REF25 8, DEEP25 8).
5. DEEP50 - DEEPFLAT50 below 0: **not met** (+0.023 [-0.029, +0.075]). Amendment 2's side-by-side: herd births per
   doe-year +0.051 [-0.092, +0.193] and herd first-kid age +0.037 y [-0.094, +0.168] are within noise. Wild first-kid
   age +0.136 y [+0.042, +0.230], herd size +3.1 [+0.0, +6.3] and wild size +9.1 [+0.7, +17.5] differ beyond noise. So
   the demographic match is incomplete, and prediction 5's difference carries part of the demographic effect.
6. REF50 - REF below 0 with REF25 between: **not met** (REF50 - REF -0.023 [-0.072, +0.025]; REF25 - REF -0.040
   [-0.087, +0.008], not between).
7. Selection differential on p (mid-parent) more negative in DEEP50 than CTLDEEP: **not met** (+0.003 [-0.001,
   +0.006]).

**Decision rule:** branch C fires: 2 fails and 7 fails. In the reviewer's wording (ba50e23, adopted by the steward in
place of the registered "the cost does not select here"): the cost lowers wild p (-0.052 against its demographic
control), mostly before herding begins. Within closed herds it adds no detectable selection on p (prediction 7), and
the herd does not move away from its wild under it (predictions 2 and 5). The null, narrowed: the per-heat cost, as
built, acts in the wild and not within managed herds. Whether retries in the herd dilute it (a doe retries each cycle,
the registered candidate) is untested; there is no counter for it. No other branch fires. For context, the demographic control alone,
DEEPFLAT50 - CTLDEEP, moves the mean core gap by -0.002 [-0.034, +0.030].

**Reading aid** (the steward's, not a rule; db9a2a6): per trait, the paired change from cost 0 in gap / absolute herd
mean / absolute wild mean (gap = herd - wild, checked), with the founders' (301-400) shift in brackets. The cost acts
on every goat from year 0, so it moves the founders too: at 0.5, T +0.113, M -0.092, S -0.052, A -0.047 and C -0.050,
the same in DEEP50, RAND50 and REF50. The per-trait gap changes whose intervals exclude 0:
- DEEP50 - DEEPFLAT50: H -0.083 [-0.154, -0.013] = herd -0.118 / wild -0.035 (herd moved); W +0.160 [+0.054, +0.267]
  = herd +0.010 / wild -0.150 (the wild moved).
- REF50 - REF: R -0.030 [-0.046, -0.014] = herd -0.000 / wild +0.029 (the wild moved); T -0.107 [-0.147, -0.068] =
  herd +0.005 / wild +0.112 (the wild moved).
- REF25 - REF: B -0.266 [-0.431, -0.100] = herd -0.274 / wild -0.009 (herd moved).
- RAND50 - CTLRAND: T +0.020 [+0.003, +0.037] = herd +0.135 / wild +0.115 (both moved, the herd slightly more).
- DEEPFLAT50 - CTLDEEP: W -0.085 [-0.138, -0.032] = herd -0.096 / wild -0.011 (herd moved).
In DEEP50 - CTLDEEP no per-trait interval excludes 0. The largest moves are H -0.079 (herd -0.099 / wild -0.020), W
+0.076 (herd -0.086 / wild -0.161) and M +0.076 (herd -0.015 / wild -0.090).
Not to be quoted as cost effects until exp013 reads (the steward, 2026-11-22). The reviewer (ba50e23) reads the wild at
cost 0.5 as still changing at year 400, the burn-in issue exp013 tests; exp013 has no cost arms.

**Standing measures:**
- Establishment (herd size, KM): all six exp012 arms 8 of 8; REF25 and REF50 later than the cost-0 REF (medians 735
  and 813 against 705); the DEEP and RAND arms at once (501). No fall-backs, no late crossings.
- Split (established seeds, herd change / wild change of p after founding, each against its own run's founders, which
  differ across cost levels): DEEP50 -0.044 / -0.016,
  CTLDEEP -0.047 / +0.001, DEEPFLAT50 -0.049 / +0.001, RAND50 -0.014 / -0.005, REF50 -0.129 / -0.019, REF -0.104 /
  -0.017.
- Gene flow (flow_tab, paired): the DEEP arms stay closed (captive-sire share 0.000; depth 20.0-20.5 against CTLDEEP's
  19.6). DEEP50 - CTLDEEP: captive-dam share -0.026 (SE 0.004), depth +0.88 (0.13), herd +7.2 (1.7). RAND50 - CTLRAND:
  captive-sire share -0.016 (0.008), depth +2.04 (0.39). REF50 - REF: captive-sire share +0.005 (0.004), depth -0.83
  (0.46).

**Added after the reviewer's ba50e23** (genecost_tab bfc19d6; the rerun adds a founders' p column and an interval
count, and changes no other number). The registered reading stands. These narrow what branch C says:
- **Selection in the wild.** The registered selection differential (prediction 7) is over the camp's herd adults only
  (world.js:1492). In the wild, the gradient's effect on p is clear: DEEP50 - DEEPFLAT50 wild p -0.052 [-0.070,
  -0.035]. Most of it is in place before herding: founders' p (301-400) -0.035 [-0.051, -0.019], with wild change
  after founding -0.017 [-0.039, +0.004]. So the registered "the cost does not select here" was true of the closed
  herd, not of the wild; the decision rule above now carries the reviewer's wording. DEEP50 - CTLDEEP founders' p is -0.012 [-0.032, +0.007]; DEEPFLAT50 - CTLDEEP +0.022 [+0.004, +0.041].
- **T.** The lower conception chance alone raises wild T (DEEPFLAT50 - CTLDEEP +0.167 [+0.146, +0.189]). The gradient
  lowers it against that (DEEP50 - DEEPFLAT50 -0.067 [-0.090, -0.044]). Prediction 1's rise in T is the conception
  chance's, not the gradient's.
- **Per-trait intervals.** 7 of the per-trait gap table's 70 intervals exclude 0, where about 3.5 would by chance at
  95%. None of the reading aid's per-trait lines is to be cited alone.

## exp013 results (raw)
32 of 32 runs complete (complete: true, 6600 years), every exit 0 (cpuslot-logs/), every run on a clean tree. Arms, 8
seeds each: REFlate, LARDlate, TAPERlate, WTlate. Hosts: 26 on the desktop and 6 on mint. Commits: a7e3d14 (1), 72c8473 (11)
and d63d785 (20); src unchanged since a659a59, so one sim. **Shared history (amendment 2's check):** WTlate_seed1
against REFlate_seed1, LARDlate_seed1 and TAPERlate_seed1 with tools/cmp_years.py: in each, the first differing record
is year 2904, the first recorded after humans arrive at 2900 (k = 5). Every record to 2899 is identical, 72 shared
keys. P1 can rest on WTlate's 8 histories. Mongo animalDomestication.exp013_late-herding on mint; JSON in
results/exp013_late-herding/. Scoring: the analysis session, with tools/late_tab.py as frozen (ae0f6f5).

## exp013 results (scored)
**Scored** 2026-11-22 by the analysis session, as registered (9522ce9), amended (f752422, 37df366) and clarified
(clarifications 1 and 2):
`python tools/late_tab.py results/exp013_late-herding "results/exp005_b0-pilot;results/exp006_two-corner;results/exp011_herder-culture" --perseed`
(the tool as frozen, ae0f6f5; selftest passes all 17 checks, `selftest bad` fails 3). Every time is taken from each run's
herdingAt: founders 2901-3000 against 301-400, window 5801-6600 against 3201-4000. The parameter guard passed on all 32
runs. Each late arm differs from its year-400 run of the same seed only in humansAt, herdingAt and ibdFrom, thinning
(k 5 against 3), and REFlate's keys added since exp005/006. WTlate differs from REFlate only in humansAt. The tool's
shared-history test agrees with the steward's cmp_years check: every late run's P1 span change equals WTlate's, seed by
seed, so P1 rests on 8 histories, not 32. Tables in results/exp013_late-herding/: scored.txt, selftest.txt,
selftest_bad.txt. The standing measures (establishment by herd size with KM, the split, closure) are in late_tab's output.

**Arms** (established seeds; herd and wild change against each run's own founders):

| arm | est (y after herding) | herd | breadth (vote) | traits | depth | csire | herd-carried breadth (exploratory) | 8-trait breadth (exploratory) |
|---|---|---|---|---|---|---|---|---|
| REFlate | 8 (median 300) | 296.5 | 8 (8 of 8 diverged) | R A S B H T W L | 14.28 | 0.073 | 7 | 7 |
| REF | 8 (305) | 287.8 | 6 (8 of 8) | R A S B T L | 14.69 | 0.064 | 4 | 5 |
| LARDlate | 8 (105) | 268.0 | 4 (7 of 8 diverged) | A B H T | 20.81 | 0.007 | 4 | 4 |
| LARD | 8 (101) | 271.2 | 6 (8 of 8) | A S B H T W | 20.80 | 0.005 | 2 | 6 |
| TAPERlate | 8 (105) | 269.8 | 6 (8 of 8 diverged) | A S B H T L | 22.00 | 0.003 | 5 | 5 |
| TAPER | 8 (101) | 267.8 | 6 (8 of 8) | R A S H T W | 22.23 | 0.003 | 2 | 6 |
| WTlate | 0 (no humans, no herd) | 0.0 | - | - | - | - | - | - |

A, S, H and W, gap / herd change / wild change (arm means; the full table is in scored.txt):

| arm | A | S | H | W |
|---|---|---|---|---|
| LARDlate | -0.111 / -0.105 / +0.006 | +0.063 / +0.091 / +0.028 | -0.110 / -0.105 / +0.005 | -0.053 / -0.075 / -0.022 |
| LARD | -0.105 / -0.011 / +0.093 | +0.111 / -0.139 / -0.250 | -0.107 / -0.025 / +0.083 | -0.100 / +0.109 / +0.209 |
| TAPERlate | -0.132 / -0.143 / -0.010 | +0.165 / +0.181 / +0.016 | -0.119 / -0.129 / -0.009 | -0.084 / -0.090 / -0.007 |
| TAPER | -0.121 / -0.039 / +0.083 | +0.131 / -0.125 / -0.256 | -0.147 / -0.064 / +0.082 | -0.138 / +0.101 / +0.239 |
| REFlate | -0.121 / -0.142 / -0.021 | +0.111 / +0.160 / +0.049 | -0.131 / -0.151 / -0.020 | -0.130 / -0.196 / -0.066 |
| REF | -0.148 / -0.060 / +0.088 | +0.174 / -0.073 / -0.247 | -0.083 / -0.023 / +0.060 | -0.090 / +0.067 / +0.158 |

**Predictions:**
1. The wild settled before humans: **met**. (i) WTlate's seed-mean wild, 2701-2900 minus 2401-2600, is within 0.02 on
   every core trait (largest M -0.011, W +0.012). (ii) WTlate's wild moves under 0.05 from 2901-3000 to 5801-6600 on
   A +0.003, S -0.011, H +0.003 and W +0.007. On the other core traits, deciding nothing: R -0.008, B +0.003, T +0.001,
   M +0.001, L +0.044. The registration's settling year per trait (each seed's first century from which every century
   stays within 0.02 of 2801-2900) is late in many seeds: M 2601-2801, H 2501-2801, and A 1601-2801 (scored.txt).
2. Human-caused wild change (late arm - WTlate, paired by seed) under 0.05 on A, S, H, W in every late arm: **not met**,
   on REFlate alone: S +0.060 [+0.016, +0.104] and W -0.073 [-0.135, -0.012]. In the closed arms every mean is under
   0.05. LARDlate: A +0.002, S +0.039 [-0.002, +0.079], H +0.002, W -0.029 [-0.059, -0.000]. TAPERlate: A -0.014, S
   +0.027 [+0.009, +0.044], H -0.012, W -0.014.
   The burn-in's share (year-400 arm wild change - late arm wild change, unpaired): REF A +0.109, S -0.296, H +0.080,
   W +0.224; LARD A +0.087, S -0.277, H +0.078, W +0.231; TAPER A +0.093, S -0.272, H +0.092, W +0.246. Every
   interval excludes 0. The year-400 wild moved this far after founding; the late wild does not.
3. Primary, late gap - year-400 gap (unpaired), predicted abs(late gap) < 0.10 with the interval excluding 0: **not met
   on any trait of any arm**. No difference's interval excludes 0. LARDlate A -0.006 [-0.088, +0.075], S -0.048, H
   -0.003, W +0.047. TAPERlate A -0.011, S +0.035, H +0.027, W +0.054. REFlate A +0.028, S -0.063. The late gaps
   stand at 0.10 or more on A and H in both closed arms and on S in TAPERlate.
4. (Registration's P3) LARDlate closed and every trait at 0.10 herd-carried: **met** (csire < 0.05 in 8 of 8; A, B,
   H, T with abs(hc) > abs(wc)). TAPERlate: **not met**. It is closed in 8 of 8, but L (gap +0.111) is wild-carried
   (herd -0.088, wild -0.199). Its other five traits are herd-carried.
5. (Registration's P4) REFlate R gap <= -0.30, herd-carried: **met** (-0.634; herd -0.687, wild -0.053).

**Decision rule** (amendments 1-2, clarification 2): P1 holds. Per closed arm and trait:
- LARDlate: A and H herd divergence from a settled wild; S and W unresolved (late gap under 0.10, interval includes 0).
- TAPERlate: A, S and H herd divergence from a settled wild; W unresolved.
- REFlate (not governing): A and H herd divergence; S and W, humans move the wild (human-caused change 0.05 or more),
  and the gap is the herd sheltered from human-driven selection on the wild, a model result.
  Annotation: REFlate (not governing): the wild moves toward the open herd (S herd +0.160 / wild +0.049; W -0.196 /
  -0.066), which reads as herd-born goats entering the wild, not shelter (reviewer 5df38b3).
- The burn-in reading holds on no trait of either closed arm, so the registered re-plan trigger (move herding after
  the wild settles) does not fire.
- Plain breadth, per-seed vote: LARDlate diverged (7 of 8 seeds at 3 or more; breadth 4), TAPERlate diverged (8 of 8;
  breadth 6). The two agree.

**What the registered measures show together.** On the late design, from a wild that had settled, the closed herds'
A and H gaps (and TAPER's S) do not differ detectably from year 400's (late-vs-400 intervals +-0.07 to +-0.15), but now the
herd carries them. LARDlate A: herd -0.105 / wild +0.006, against LARD's herd -0.011 / wild +0.093. At year 400 the
same gaps were carried by the wild's post-founding move, the burn-in's share above. So on these traits the year-400
and late gaps do not differ detectably but are carried by opposite pools: at year 400 the herd held its founders while the wild settled; from a settled wild, the closed herd
moves away by itself (the rule's "herd divergence from a settled wild").

**Exploratory** (not registered):
- Herd-carried breadth (exp007's carrier) rises on the late design: LARDlate 4 (7 of 8 seeds at 3+), TAPERlate 5 (8 of
  8), REFlate 7 (8 of 8), against LARD 2, TAPER 2, REF 4. 8-trait breadth: LARDlate 4, TAPERlate 5, REFlate 7.
- L's wild moves in every late arm after humans arrive (wild change REFlate -0.131, LARDlate -0.154, TAPERlate
  -0.199), against WTlate's +0.044. L is outside A, S, H, W, so no registered test reads it.
- REFlate's breadth is 8 against REF's 6. R is unchanged (-0.634 against -0.636).
- **Added after the reviewer's 5df38b3** (late_tab 22f54f7; no registered line of scored.txt changes). These are
  absolute window means on A, S, H and W over established seeds, late arm against year-400 arm, unpaired. The
  founders differ by design: A +0.103 [+0.078, +0.127], S -0.281 [-0.354, -0.207], H +0.086 [+0.049, +0.123] and W
  +0.259 [+0.159, +0.359], the same in every pair. Neither the herds' absolute means nor the wilds' differ detectably
  between the designs; every interval includes 0.
  - Herd: LARDlate - LARD A +0.009 [-0.071, +0.089], H +0.005 [-0.082, +0.092]; TAPERlate - TAPER A -0.001 [-0.082,
    +0.079], S +0.025 [-0.036, +0.087], H +0.021 [-0.121, +0.164].
  - Wild: LARDlate - LARD A +0.015 [-0.004, +0.034], H +0.008 [-0.012, +0.028]; TAPERlate - TAPER A +0.010, S
    -0.009, H -0.006.
  So the closed herds, and their wilds, reach the same window means from founders as far apart as these. That fits the
  reviewer's reading: each gap is a herd equilibrium minus a wild equilibrium, and the carrier is set by where the
  founders started. Herd intervals are wide (+-0.08 to +-0.19), so equal equilibria are not shown, only not ruled out.

## Take-off analysis, 2026-11-22 (reading stated before any tool reads the pre-jump years; existing runs, no new simulation)
**Question** (Chris, 2026-11-22: "what triggers the phase transition?"): herds that wait small and then jump: does
the herd's reactivity fall before the jump (a feedback loop: a less reactive herd loses fewer goats, grows, and its
home-born goats outnumber captives), or does its breeding stock rise first, with R following (a demographic tipping
point)?
**Data:** exp010 LOAD1, the 7 seeds classed "waited" (5-12 goats, then a jump at 978-3171); the exp005 arms whose
herds plateaued (20-65 goats) if their records allow it. Only year-row keys present in every run used.
**Measure** (the analysis session; a committed tool): each seed aligned on its own jump year (jump_tab's criterion,
first year of the established run). In the centuries before and after it: herd size, herd mean R, home-born breeding
does if recorded (otherwise herd does of breeding age), the captured share of herd sires, and the loss rate (escaped
per herd goat). Per variable and seed, its departure year: the first year, going forward from 300 years before the jump,
from which it stays beyond 2 SD of its own plateau (the 300 years before that).
**Reading:** R departs first (earlier than both size and does) in 5 or more of 7 seeds: feedback. Does or size depart
first in 5 or more: demographic. Otherwise mixed, said so. Exploratory: it describes the transition in existing runs
and decides nothing in the design.

## Take-off analysis clarification, 2026-11-22 (before any real data is read; the analysis session's definitions, accepted)
- Variables per year row: herd size = herded; herd R = herdTraitMeans.R; breeding does = herded x herdComp[1] /
  sum(herdComp) (home-born does are not recorded by sex); captured-sire share = herd conceptions by a captured sire
  (concOrigin column 1) / herd conceptions; loss = escaped / herded.
- Each is read as a trailing 30-year window (ratios as summed numerator / summed denominator; R weighted by herded).
- Plateau J-600..J-301 (J = jump_tab's jump year), shortened to start at 500 where needed. A seed with a plateau under
  200 years (LOAD1 seed 2, 178) stays in, flagged.
- Departure: beyond 2 SD of the plateau, in the direction the variable moves across the jump (J..J+300 mean minus
  plateau mean), at every smoothed point from the departure year to J+300; the search starts at J-300. No year: no
  departure. Plateau SD 0: the first point that differs and stays different, flagged.
- "First": strictly earlier than both size and does; a tie counts for neither.
- exp005: runs that jump and whose 100-year herd stayed in 20-99 for 300 or more years before J, reported apart. The
  5-of-7 reading is on LOAD1's 7 only.
- Stated beside the result: J is defined on herd size, so size must rise before J; a "size first" partly reflects the
  alignment. Each seed's signed lead (R departure minus the earlier of size and does, in years) is printed, so the
  margin shows, not only the vote. An R departure at the search start (J-300) is flagged as possibly earlier.

## Take-off analysis results (exploratory; decides nothing in the design)
**Run** 2026-11-22 by the analysis session with tools/takeoff_tab.py (7e44e2a; selftest passes; `selftest bad`
fails on the planted dip):
`python tools/takeoff_tab.py results/exp010_fixed-load LOAD1 --waited --out results/exp010_fixed-load/takeoff_LOAD1.json`
`python tools/takeoff_tab.py results/exp005_b0-pilot RAND,REF,noBuck,noGuard,noMilk,noPen,noProv,noShelter,noTether --plateau20 --out results/exp005_b0-pilot/takeoff_plateau20.json`
Plots: tools/takeoff_plot.py, results/exp010_fixed-load/takeoff_LOAD1.png and results/exp005_b0-pilot/takeoff_plateau20.png.
Tables: takeoff_LOAD1.txt and takeoff_plateau20.txt beside them.

**LOAD1, the 7 waiting seeds** (s5, a late crossing, is left out). Departure years relative to J; R's lead is R minus
the earlier of size and does (negative = R first):

| seed | J | size | R | does | csire | loss | first | R lead |
|---|---|---|---|---|---|---|---|---|
| s1 | 2325 | -132 | -90 | -132 | none | +171 | none (size = does) | +42 |
| s2 | 978 | -159 | -147 | -156 | none | +264 | size | +12 |
| s3 | 1515 | -114 | -108 | -111 | none | none | size | +6 |
| s4 | 1176 | -177 | -123 | -177 | none | -75 | none (size = does) | +54 |
| s6 | 3171 | -102 | -105 | -99 | none | none | R | -3 |
| s7 | 1614 | -132 | -135 | -132 | none | none | R | -3 |
| s8 | 3039 | -60 | -75 | -60 | none | +300 | R | -15 |

s2's plateau is 178 years (flagged, kept). **Reading (stated before the data): mixed.** R departs first in 3, size in
2, does in 0; 2 have no first because size and does tie.
- The margins are small. In 5 of 7 seeds, R, size and does depart within 15 years of each other, inside the 30-year
  smoothing window, so their order is not resolved. In s1 and s4, R departs 42 and 54 years after size and does.
- In no seed does R lead by more than 15 years.
- Size and does depart together (within 3 years in every seed). Does are herd size times the breeding-doe share, so
  they follow size closely by construction.
- The captured-sire share has no departure in any seed. Loss departs after J in 3 seeds, before J in 1 (s4, -75), and
  not at all in 3.
- Alignment caveat: J is set by the 100-year trailing mean of herd size, so raw size must rise before J.

**exp005** (reported apart; counts only, no 7-seed verdict). The four runs the reviewer named as plateaued at 20-65
goats (RAND s1 and s3, noProv s1 and s2) never establish, so none can be aligned on a jump. 12 runs pass the 20-99 rule:
R first in 7, does in 1, no first in 4. R's lead is -201 (noGuard s2), -96 (noProv s4), -63 (noProv s3) and -27 to
+57 in the rest. 9 of the 12 jump before year 1100, so their plateaus are 43-253 years and fall partly in the founding
years (flagged in the table). These herds grow through 20-99 rather than wait at it; the plot shows them rising across
the plateau window. The R-first count is not comparable to LOAD1's.

## Take-off analysis clarification 2, 2026-11-22 (before the matched-scale reading reads real data; the reviewer's a5a0b06)
Exploratory, printed beside the stated 2-SD reading, which it does not replace:
- Noise ratio per variable and seed: plateau SD / abs(post - plateau mean), post = the J..J+300 mean.
- Matched-scale departure: the first smoothed point from J-300 from which the variable has covered at least 1/4 of its
  own change ((v - plateau mean) x sign >= 1/4 x abs(post - plateau mean)) and stays there through J+300. "First" and
  R's lead read on it as before.
- Caveat in the entry: as home-born goats replace captives, R falls with growth by composition alone, so a tie or an R
  lag is what the demographic reading predicts; only R well ahead points to feedback.
This is the last addition to this test. The records do not separate the two triggers; any further answer comes from
an intervention experiment, which goes to Chris.

## Take-off analysis, matched-scale results (exploratory; clarification 2; beside the stated reading, which stays mixed)
**Run** 2026-11-22 with tools/takeoff_tab.py (8ae956e; selftest passes; `selftest bad` fails, including the planted
matched-scale case): the same command as the results entry. The stated 2-SD lines of takeoff_LOAD1.txt are unchanged.
LOAD1, the 7 waiting seeds:

| seed | noise ratio size / R / does / csire / loss | departure at 1/4: size / R / does / csire / loss | first | R lead |
|---|---|---|---|---|
| s1 | 0.01 / 0.07 / 0.01 / 0.83 / 0.47 | -39 / -60 / -39 / +276 / -63 | R | -21 |
| s2 | 0.00 / 0.04 / 0.00 / 7.54 / 0.52 | -39 / -108 / -39 / +273 / -189 | R | -69 |
| s3 | 0.00 / 0.07 / 0.00 / 4.13 / 0.78 | -33 / -78 / -33 / +192 / -48 | R | -45 |
| s4 | 0.01 / 0.04 / 0.01 / 1.14 / 0.32 | -39 / -99 / -39 / +186 / -183 | R | -60 |
| s6 | 0.01 / 0.05 / 0.01 / 0.99 / 0.58 | -45 / -84 / -42 / +252 / -78 | R | -39 |
| s7 | 0.01 / 0.03 / 0.01 / 2.38 / 0.66 | -33 / -108 / -33 / none / -51 | R | -75 |
| s8 | 0.02 / 0.07 / 0.01 / 0.72 / 0.54 | -33 / -69 / -33 / +261 / -66 | R | -36 |

**Matched scale: R first in 7 of 7, leading by 21 to 75 years.** Read with these limits:
- **Scale (the analysis session's, noted after reading; the measure is not changed).** Herd size rises roughly
  exponentially, from 5-12 goats on the plateau to a window herd of 245.8 (load_tab), so a quarter of its change on a
  linear scale is reached late in the rise (J-45 to J-33). Does follow size. R falls without that curvature (plot). On this scale R's quarter point comes before size's
  even if growth were the trigger, so R first here does not by itself point to feedback. The fraction was fixed before
  reading; the scale of size (linear or log) was not discussed.
- **Composition (clarification 2):** a tie or an R lag is what the demographic reading predicts. R ahead by 21-75 years
  on a linear size scale does not clear that, given the point above.
- **Noise:** R's noise ratio (0.03-0.07) is larger than size's and does' (0.00-0.02), so the 2-SD rule dated R later
  than its own change does. That is the reviewer's a5a0b06 point 1, now in the tool's numbers.
- **Loss** reaches 1/4 of its fall before R in s1, s2 and s4 (-63, -189, -183) and after R in the other four; its
  noise ratio is 0.32-0.78, so its timing is weak. The captured-sire share's noise ratio is 0.72-7.54; its quarter points are after J.
The stated reading (2-SD rule) remains mixed. The records do not separate the two triggers (clarification 2).

## exp014 — Run-off by a time schedule matched to REF's curve, with no R, fear or herd size: does recapture alone, where R still acts, tame the herd?
**Pre-registered:** 2026-11-22. Chris: make the run-off rate fixed "and recapture is as it is now ... no R on the run-off
side, only R on the recapture side"; matched to REF "by time". Mongo animalDomestication.exp014_runoff-schedule (mint);
results/exp014_runoff-schedule; job list tools/exp014.jsonl; code c72d86f (spookFixed f8848f0, spookSchedule c72d86f).
Identity: with both off, 800 years of REF seed 1 reproduce exp005 REF_seed1, 0 of 266 records differ, 65 shared keys,
at f8848f0 and again at 8c10761.
**Why:** in REF, R acts twice: in the spook chance (herderAlarm × R × fear × load, animals.js:365) and in recapture
(the approach test, stalkDetect × R × fear per step, world.js approach()). The load, which rises with herd size, acts
only on the spook. This takes R, fear and load out of the spook and keeps recapture as it is.
**The schedule:** a daily spook chance, the same for every herd goat, by years since herding, piecewise constant per
century: spookSchedule = "0:0.00600,100:0.00758,200:0.00939,300:0.00975,400:0.00855,500:0.00718,600:0.00529,700:0.00406,800:0.00363". The values are REF's run-off rate per herd goat-year (tools/runoff_rate.py, exp005
and exp006 REF, 8 seeds) per century of herding (1.440, 1.820, 2.254, 2.341, 2.052, 1.722, 1.269, 0.975, then 0.871 over
1201-4000), divided by 240, the run-offs per goat-year per unit of daily chance from the calibration probes
(tools/exp014_cal.jsonl: 4.5-4.8 at 0.02, 7.9-8.7 at 0.04, 10.9-13.1 at 0.08; near-linear at the low end). The probes'
herds collapsed to 1-2 goats, which was seen.
**Calibration check before the main runs:** SCHED seeds 1-2 for 1600 years in --scratch; only their run-off rates
(runoff_rate.py's ranOff) are read, per century 401-1200 and over 1201-1600. Pass: within 15% of REF's rate in every
one of those periods. On a failure, the divisor is rescaled and the check repeated, recorded here as an amendment
before any main run starts.
**Arms** (seeds 1-8, 4000 years, herding at 400, REF's arguments otherwise):
- SCHED: spookSchedule as above.
- SCHEDT: SCHED with captureTaper 1, selfDoes 10 (closed).
- REFT: REF with captureTaper 1, selfDoes 10 (closed, R in both stages): SCHEDT's contrast, paired by seed.
REF (exp005 + exp006) is SCHED's contrast, paired by seed.
**Measure** (the analysis session; window 3201-4000; standing measures): establishment (jump_tab), herd, R gap, herd
and wild change of R against the 301-400 founders, breadth, closure (captive-sire share, depth), loss rates (ranOff,
refetched, escaped per herd goat-year), and the achieved run-off curve per century against REF's.
**Predictions** (mine):
1. SCHED and SCHEDT establish in 6 or more of 8 seeds.
2. SCHEDT's R gap is -0.30 or below, but smaller in size than REFT's (paired by seed, interval excluding 0): recapture
   alone filters, and R on the run-off side adds to it.
3. SCHED's herd R falls from its founders by 0.20 or more.
**Decision rule:**
- SCHEDT R gap -0.30 or below: recapture alone carries a filter strong enough for divergence on R; neither R on the
  run-off side nor herd-size scaling is needed for it.
- SCHEDT R gap above -0.30 while REFT's is -0.30 or below: the filter needs R on the run-off side (run-offs concentrated
  on reactive goats).
- Fewer than 2 established seeds in SCHEDT: the schedule's rates, spread over all goats, do not let a closed herd form;
  goes to Chris.
- In each branch, SCHEDT's R gap as a share of REFT's (paired) is reported as the recapture stage's share of the
  filter, descriptively.

## exp014 amendment, 2026-11-22 (before any main run; the calibration check running, nothing of it read; the reviewer's 3c9ab09)
- **The check reads only run-off rates:** `python tools/runoff_rate.py --check "401-500:1.440,501-600:1.820,601-700:2.254,
  701-800:2.341,801-900:2.052,901-1000:1.722,1001-1100:1.269,1101-1200:0.975,1201-1600:0.871" <the two SCHEDcal files>`
  prints only mean ranOff per period, its target and pass or fail. The SCHEDcal runs are the first 1600 years of the
  main SCHED seeds 1 and 2, so nothing else of them is read. Each rescaling attempt is recorded here. The earlier
  constant-rate probes (tools/exp014_cal.jsonl) printed herd size and losses, but at different settings (spookFixed
  0.02-0.08, herds collapsed to 1-2 goats), not the main runs' arguments.
- **Guard:** World.spookAt throws on a schedule value of 0 or below, which would otherwise silently restore REF's
  R-based spook.
- **Branch 1, reworded:** SCHEDT R gap -0.30 or below, with SCHEDT closed (captive-sire share under 0.05 in 6 or more of 8
  seeds): recapture alone carries a filter strong enough for divergence on R; no per-herd load is needed for it, and
  the run-off time course is REF's.
- **Branch 2, reworded:** SCHEDT closed with R gap above -0.30, while REFT's is -0.30 or below: the filter needs the
  run-off side to read the goat (R x fear) and its herd's load. Four things differ between SCHEDT and REFT: R in the
  spook, fear in the spook, the per-herd load, and the run-off level (the schedule follows REF's curve, not REFT's).
  REFT's and SCHEDT's achieved run-off rates per century are reported side by side; where they differ by more than 15%
  in the window, the reading is said to carry a rate difference too.
- **Outcomes with no branch before:**
  - REFT R gap above -0.30: closing REF removes the reactive captives the filter acts on; no contrast is read, and
    SCHEDT is reported alone.
  - SCHEDT established but not closed: no branch fires; reported with herd change against founders.
  - SCHED (open) is read beside the rule, by herd change against founders, since in an open herd the wild follows.

## Take-off analysis on REF, 2026-11-22 (Chris: "let's run that same analysis on REF"; before REF's trajectories are read)
REF's 8 seeds (exp005 1-4, exp006 5-8) aligned on their jump years with tools/takeoff_tab.py and takeoff_plot.py, as
for LOAD1. REF herds grew without a waiting plateau (exp010's Q1: "grew" in 8 of 8; jumps near year 700), so the
stated 2-SD departure test needs a plateau of 200 years or more before J-300 that most REF seeds lack. The test is run
only on seeds that have one; the others are listed. The aligned plot is descriptive and claims no order. Same
definitions and caveats as for LOAD1 (812c5e1, 871974d); nothing new is added to the test.

## Take-off analysis on REF, results (descriptive)
**Run** 2026-11-22 with tools/takeoff_tab.py (cd68c7c; --minplateau 200 only lists and skips; LOAD1's output is
unchanged by it; selftest passes, `selftest bad` fails):
`python tools/takeoff_tab.py "results/exp005_b0-pilot;results/exp006_two-corner" REF --minplateau 200 --out results/exp006_two-corner/takeoff_REF.json`
Plot: `python tools/takeoff_plot.py results/exp006_two-corner/takeoff_REF.json results/exp006_two-corner/takeoff_REF.png`.
Table: results/exp006_two-corner/takeoff_REF.txt.
**Departure test: run on no seed.** None has 200 years of plateau before J-300, counting from year 500: s1 (J 957) 157
years, s2 (J 849) 49, and s3-s8 (J 588-783) none. All 8 are plotted.
**What the plot shows** (shapes read by eye; no order is claimed). Figures are the plotted smoothed values at J-300 / J
/ J+300, mean over runs (n), printed by tools/takeoff_plot.py (the reviewer's 9a18d2e; results/exp006_two-corner/
takeoff_REF_plot.txt). Two seeds have no herd yet at J-300.
- Each herd starts from nothing when herding begins and grows steadily to the jump, with no flat waiting stretch: size
  14.4 (8) / 134.0 (8) / 279.1 (8). s1 is the exception; the plot shows it holding at a few tens of goats for about 200
  years first.
- Herd R falls the whole way: 0.802 (6) / 0.437 (8) / 0.104 (8). It falls together with growth from the start, not at a
  separate moment. Composition caveat (as for LOAD1): as home-born goats replace captives, R falls with growth on
  composition alone, so falling together with growth does not separate feedback from demography.
- Breeding does climb with herd size throughout: 5.3 (8) / 48.0 (8) / 103.3 (8).
- Captured-sire share of conceptions: 0.234 (6) / 0.368 (8) / 0.065 (8).
- Loss rate: 0.243 (6) / 0.459 (8) / 0.114 (8). It rises as the herd grows (REF's spook load grows with herd size) and
  falls after the jump. In LOAD1, at a fixed load, the plot shows loss lower after J than before.

## exp014 amendment 2, 2026-11-22 (before any main run; the calibration check, attempt 1)
Attempt 1 (schedule of the pre-registration, divisor 240), SCHEDcal seeds 1-2, `runoff_rate.py --check`, ranOff only:
every period high, ratios 1.22, 1.18, 1.19, 1.18, 1.24, 1.21, 1.24, 1.29 (401-500 .. 1101-1200) and 1.35 (1201-1600):
FAIL. Rescaled per period, each value divided by its own period's ratio:
spookSchedule = "0:0.00492,100:0.00642,200:0.00789,300:0.00826,400:0.00690,500:0.00593,600:0.00427,700:0.00315,800:0.00269". tools/exp014.jsonl rewritten with it. Attempt 2: SCHEDcal2 seeds 1-2, 1600 years, the same check.
The main runs carry this schedule and commit 3dfc9bb or later (the spookAt guard, which cannot fire on it).

## exp014 calibration check passed, 2026-11-22 (before any main run)
Attempt 2 (amendment 2's per-period schedule), SCHEDcal2 seeds 1-2, 1600 years, commit 1a67ab6, `runoff_rate.py --check`,
ranOff only: ratios to REF's rate 1.00, 1.07, 1.07, 1.01, 1.05, 1.08, 1.07, 1.04 (401-500 .. 1101-1200) and 0.99
(1201-1600): PASS. Nothing else of these runs was read. The 24 main runs (tools/exp014.jsonl) queued now.

## exp014 clarification, 2026-11-22 (before any main result; sched_tab 52ef90a's reading choices, accepted)
- "Differ by more than 15% in the window": abs(SCHEDT/REFT - 1) > 0.15 on the 3201-4000 run-off rate (each arm's mean
  over seeds). The eight centuries are listed with a count of those beyond 15%, not part of the flag.
- Branch 1 does not involve REFT, so it can fire beside the "REFT above -0.30: no contrast read" note.
- Prediction 2's "smaller in size": the paired signed SCHEDT - REFT R gap with its interval above 0, read only when
  REFT's arm gap is negative.
- Closed: captive-sire share under 0.05 in 6 or more of all 8 seeds; a seed with no herd conceptions in the window
  counts as not closed.
- Recapture share: mean SCHEDT R gap / mean REFT R gap over seeds established in both, per-seed ratios listed.
- Breadth is descriptive; the rule does not read it.

## exp014 results (raw)
24 of 24 runs complete (complete: true, last row year 3998), every exit 0 (cpuslot-logs/, batch 1795377055079603700),
every run on a clean tree, no error in any log. Arms, 8 seeds each: SCHED, SCHEDT, REFT; SCHED and SCHEDT carry amendment
2's schedule, SCHEDT and REFT captureTaper 1 and selfDoes 10. Hosts: 18 on the desktop and 6 on mint. **Commits:** the
runs carry 1a81bb5 (8), 60a121d (1) and 599fca2 (15), not the registered c72d86f: amendment 2 moved the main runs to
3dfc9bb or later, and src is unchanged from 3dfc9bb to 599fca2 (git diff --stat empty), so one sim. The spookAt guard
added at 3dfc9bb cannot fire on this schedule (every value > 0). JSON in results/exp014_runoff-schedule/; the registered
Mongo collection is animalDomestication.exp014_runoff-schedule on mint. Nothing of the runs has been read beyond these
checks. Scoring: the analysis session, with tools/sched_tab.py as accepted (f237316, the reviewer's 599fca2).

## exp014 results (scored)
**Scored** 2026-11-22 by the analysis session, as registered (536bc53), amended (3dfc9bb, 1a67ab6), calibrated (1a81bb5)
and clarified (60a121d):
`python tools/sched_tab.py results/exp014_runoff-schedule "results/exp005_b0-pilot;results/exp006_two-corner" --perseed`
(the tool as accepted, f237316; selftest passes all 46 checks, `selftest bad` fails 4). Window 3201-4000, founders
301-400. The parameter guard passed on all 24 runs (the tool stops otherwise): SCHEDT = SCHED but captureTaper 1 and
selfDoes 10; REFT = SCHEDT but no schedule; SCHED = REF but the schedule, with the keys added since exp005/006 each at
its identity value (runOffLoss 1, spookFixed 0, captureTaper 0, selfDoes 0, and the rest listed in scored.txt). Every
window run-off rate equals runoff_rate.rates. REF's nine registered run-off rates are reproduced from the base runs.
Tables in results/exp014_runoff-schedule/: scored.txt, selftest.txt, selftest_bad.txt.

**Arms** (established seeds for R and changes; closure over all 8 seeds):

| arm | est | herd | R gap (SE) | herd change R | wild change R | closed seeds | csire | depth | lost per goat-yr | run-offs per goat-yr |
|---|---|---|---|---|---|---|---|---|---|---|
| SCHED | 8 (median 1140) | 266.0 | -0.060 (0.006) | -0.212 | -0.151 | 0 of 8 | 0.382 | 3.27 | 0.166 | 0.867 |
| REF | 8 (717) | 287.8 | -0.636 (0.006) | -0.714 | -0.078 | 1 of 8 | 0.064 | 14.69 | 0.082 | 0.859 |
| SCHEDT | 8 (1152) | 309.6 | -0.270 (0.060) | -0.412 | -0.142 | 8 of 8 | 0.002 | 22.40 | 0.122 | 0.846 |
| REFT | 8 (699) | 289.6 | -0.657 (0.006) | -0.724 | -0.067 | 8 of 8 | 0.002 | 22.57 | 0.057 | 0.737 |

**Predictions:**
1. SCHED and SCHEDT establish in 6 or more of 8: **holds** (8 and 8).
2. SCHEDT R gap -0.30 or below and smaller in size than REFT's: **fails**. SCHEDT's gap is -0.270, above -0.30; the paired
   SCHEDT - REFT difference is +0.387 [+0.253, +0.520], n 8, above 0.
3. SCHED's herd R falls from its founders by 0.20 or more: **holds** (-0.212, near the boundary).

**Decision rule: branch 2 fires.** SCHEDT is closed (csire under 0.05 in 8 of 8 seeds) with R gap -0.270, above -0.30,
while REFT, also closed in 8 of 8, has -0.657. As registered: the filter needs the run-off side to read the goat (R x
fear) and its herd's load. Four things differ between SCHEDT and REFT: R in the spook, fear in the spook, the per-herd
load, and the run-off level. **Run-off rates in the window are within 15%:** SCHEDT / REFT = 1.15 (window rates 0.846
and 0.737), so the reading is not said to carry a rate difference. It sits at the boundary. As context, not part of the
flag: 4 of the window's 8 centuries and 19 of all 36 differ by more than 15%. The paired run-off difference is +0.108
[+0.008, +0.209]. SCHEDT's achieved curve follows REF's (window 0.846 against REF's 0.859; the schedule was matched to
REF). REFT's rate runs below REF's from 401-500 on (0.737 against 0.859 in the window).

**Recapture stage's share of the filter** (descriptive): SCHEDT's R gap / REFT's = 0.41 (n 8). Per seed: s1 0.74, s2
0.68, s3 0.11, s4 0.14, s5 0.55, s6 0.13, s7 0.41, s8 0.51. SCHEDT's spread across seeds is wide (SE 0.060 against
REFT's 0.006). Seeds 3, 4 and 6 have gaps of -0.071 to -0.089; seeds 1, 2, 5 and 8 have -0.332 to -0.494. In s3 and s6 the
wild's R moves with the herd's (wild change -0.240 and -0.383, against -0.041 to -0.148 in the other seeds). In s4 the
herd moves little (herd change -0.187). The cause of the spread is untested.

**Closure is not what differs:** SCHEDT and REFT have the same captive-sire share (0.002 each, paired -0.000 [-0.002,
+0.002]) and depth (22.40 and 22.57, paired -0.175 [-0.692, +0.342]). SCHEDT loses more goats for good (lost 0.122
against 0.057 per herd goat-year, paired +0.065 [+0.046, +0.084]).

**SCHED (open), read beside the rule:** herd change of R against founders -0.212 and wild change -0.151, so the R gap
is -0.060. Paired SCHED - REF: R gap +0.575 [+0.558, +0.593], herd change +0.502 [+0.472, +0.533], wild change -0.073
[-0.097, -0.048], n 8. SCHED is open (csire 0.382, depth 3.27), and the wild follows the herd. Breadth 0.

Breadth is descriptive only: SCHED 0, REF 6, SCHEDT 3 (R B T; 5 of 8 seeds with 3 or more), REFT 8. The gaps by
trait, the per-century run-off curve and the per-seed rows are in scored.txt.

## exp014 results (scored), correction 2026-11-22 (the reviewer's 5b57cf5, wording; the steward's decision)
Corrects the wording of the entry above; no number in it changes. Branch 2 stays the registered outcome. The tool was
run again with sched_tab dfc030c, a display-only change: the window ratio to 3 decimals and a count of centuries with
SCHEDT above REFT; the table is otherwise identical to f237316's; selftest passes all 48 checks, `selftest bad` fails 5.
Per the steward: no tool line against exp011 TAPER, and no sentence splits the filter between the run-off and
recapture stages; the claim is the contrast. The entry's "needs the run-off side" holds only with its threshold, and its
"Recapture stage's share of the filter" is withdrawn as a label; read the three paragraphs below in their place.

**Decision rule: branch 2 fires.** SCHEDT is closed (csire under 0.05 in 8 of 8 seeds) with R gap -0.270, above -0.30,
while REFT, also closed in 8 of 8, has -0.657. The registered sentence is "the filter needs the run-off side to read the
goat (R x fear) and its herd's load". That is a threshold call on an arm mean 0.03 above the line (SE 0.060), with 4
of 8 SCHEDT seeds past -0.30 (s1 -0.494, s2 -0.451, s5 -0.363, s8 -0.332), so "needs" holds only with the threshold
attached. What the data carry cleanly is the contrast, paired SCHEDT - REFT, n 8: R gap +0.387 [+0.253, +0.520], herd
change of R +0.312 [+0.214, +0.410], wild change -0.075 [-0.172, +0.022]. The shortfall is mostly in the herd's own
change, not in the wild following it. Read so: without R, fear and load in the spook, a closed herd's R gap is less
than half of REFT's, and the schedule-only arm still moves its herd and reaches -0.30 in 4 of 8 seeds. Four things
differ between SCHEDT and REFT: R in the spook, fear in the spook, the per-herd load, and the run-off level. Closure is
not a fifth (the entry above: csire paired -0.000 [-0.002, +0.002]).

**Run-off rates in the window are within 15%:** SCHEDT / REFT = 1.147 (window rates 0.846 and 0.737), so the reading is
not said to carry a rate difference. As context, not part of the flag: 4 of the window's 8 centuries and 19 of all 36
differ by more than 15%. **SCHEDT ran off more than REFT throughout** (36 of 36 centuries; paired in the window +0.108
[+0.008, +0.209]), which gives its recapture stage more tests: each run-off is a recapture attempt, and the approach
test reads R and fear. The difference in R gap is in spite of this; the rate difference would narrow it, not produce
it. The direction comes from the code path, not from a measurement. SCHEDT's achieved
curve follows REF's (window 0.846 against REF's 0.859; the schedule was matched to REF), while REFT's runs below REF's
in every century (0.737 against 0.859 in the window).

**SCHEDT's R gap as a share of REFT's** (descriptive): 0.41 (n 8). Per seed: s1 0.74, s2 0.68, s3 0.11, s4 0.14, s5 0.55,
s6 0.13, s7 0.41, s8 0.51. This is not the recapture stage's share of the filter. A closed herd with no loss on run-off
also opens an R gap: exp011 TAPER (captureTaper 1, selfDoes 10, runOffLoss 0, the same seeds) has -0.117 (SE 0.031;
results/exp011_herder-culture/scored.txt). So part of each arm's gap is not run-off selection, and no apportioning
between the stages is made here. SCHEDT's spread across seeds is wide (SE 0.060 against REFT's 0.006). Per seed, R gap
/ herd change / wild change: s1 -0.494 / -0.571 / -0.077, s2 -0.451 / -0.531 / -0.080, s3 -0.071 / -0.310 / -0.240,
s4 -0.089 / -0.187 / -0.098, s5 -0.363 / -0.432 / -0.069, s6 -0.084 / -0.467 / -0.383, s7 -0.276 / -0.424 / -0.148,
s8 -0.332 / -0.373 / -0.041. Seven of 8 herds move by 0.30 or more against their founders; s4 is the exception. In s3
and s6 the gap is small because the wild moved with the herd, and in s4 because the herd moved little. Escaped herd
goats join the wild, and SCHEDT loses more of them for good (the entry above), but s4 has the highest loss rate (0.171) and a
small wild change, so the cause of the spread is untested.

## exp015 — Fixed spook load between 0.5 and 1 (0.6, 0.7, 0.8, 0.9): where does the wait before take-off begin, and how does the R gap grow?
**Pre-registered:** 2026-11-22. Chris: "please sweep 0.6 0.7 0.8 0.9", after LOAD05 and LOAD1 side by side over time.
Mongo animalDomestication.exp015_load-sweep-mid (mint); results/exp015_load-sweep-mid; job list tools/exp015.jsonl (32
runs, cpuslot --anywhere); code HEAD at queueing (named in the raw entry). exp016 was claimed in the registry by a
mistaken second --register call (question "x") and marked abandoned; no run uses it.
**Why:** exp010 fixed the spook load, the herd-size factor in the spook chance (src/animals.js, herderAlarm × R × fear ×
load), so it no longer grows with the herd. At 0.5 every herd was established by year 800 (KM 1.00; Q1 "grew" 6, "at
once" 2), and the R gap was -0.104. At 1, 7 of 8 waited in the small state (plateaus of 5-12 goats) and jumped in years
978-3171, the eighth crossing late, and the gap was -0.247 (exp010 results, scored). Between them the waiting appears and the gap more than doubles.
This sweep places both. At a fixed load, herderAlarm and the load enter only as their product, so it is also a
herderAlarm sweep (daily spook chance 0.030-0.045 for a goat with R × fear 1).
**Identity:** 800 years of exp010's LOAD1 seed 1 at f5f92f3 (tools/exp015_id.jsonl, --scratch, thinned as a 4000-year run) reproduce exp010's run: 0 of 266 year records differ, 68 shared keys (tools/cmp_years.py). The keys added since exp010 (spookFixed, spookSchedule and others) sit at their identity values.
**Arms** (seeds 1-8, 4000 years, herding at 400; exp010's arguments, herdPerHerder 1e9, minLoad the load):
LOAD06 0.6, LOAD07 0.7, LOAD08 0.8, LOAD09 0.9. Read beside exp010's LOAD05 and LOAD1 (and exp007's LOADLO), same seeds.
Herds are open, as in exp010 (captures continue).
**Measure** (the analysis session; window 3201-4000; tools/load_tab.py with the four levels added, built and checked
before any result): per level, established (herd >= 100 over the window) and by jump_tab's criterion with the KM median
time; Q1 per seed (at once / grew / waited / never, load_tab's definition: waited = the 100-year herd mean under 60 for
300+ consecutive years after year 500, then established); herd; R gap; breadth; captive-sire share; observable rates
(ranOff, refetched, escaped per herd goat-year).
**Predictions** (mine):
1. Every new level establishes (herd >= 100 over the window) in 6 or more of 8 seeds.
2. Waiting is graded, not a switch: across 0.5, 0.6, 0.7, 0.8, 0.9, 1 the count of "waited" seeds is non-decreasing,
   and at least two of the four new levels have "waited" in 2 to 6 of 8 seeds.
3. The KM median time to establishment is non-decreasing with load across the six levels.
4. Among established seeds, every new level's R gap lies between -0.05 and -0.30, and LOAD09's is more negative than
   LOAD06's.
**Decision rule:**
- Waiting: if each new level has "waited" in 0-1 or in 7-8 seeds, the wait switches on between two neighbouring
  levels: a threshold in filter strength, stated as the interval between them. Otherwise the wait is graded: its
  chance rises with the load. Either way reported to Chris with the per-seed Q1 table.
- Divergence: if any level has established herds with R gap -0.30 or below and breadth 3 or more, exp010's registered
  conclusion (no fixed load gives both a persisting herd and divergence) is revised and goes to Chris. Otherwise it
  stands over 0.25-1.
- Descriptive, not a test: within each level, the R gap of seeds that waited beside those that did not.

## exp015 amendment, 2026-11-22 (before any result: 0 of 32 runs finished; the reviewer's f0c4284)
- **Waited, censoring removed:** a seed counts as waited if its 100-year herd mean stays under 60 for 300+ consecutive
  years after year 500, whether or not it establishes by the follow-up end. Printed in two parts: waited then
  established, and waited and still waiting (or crossing late). LOAD05 and LOAD1 are recounted with the same line
  (exp010's LOAD1 s5 waited and crossed at 3708, so LOAD1 reads 8, not 7).
- **The span cut:** per seed, J, the longest span under 60 after year 500, and the median herd over that span. The
  waited count is also printed at 200 and 400 years. If the waiting reading differs between the 200, 300 and 400 cuts,
  it is labelled cut-dependent.
- **Waiting decision rule, restated by resolution** (the waited fraction per level, across 0.5, 0.6, 0.7, 0.8, 0.9, 1):
  - no level intermediate (each 0-1 or 7-8 of 8): a switch narrower than 0.1, between the two neighbouring levels;
  - one intermediate level: the switch is located there, its width unresolved at this spacing;
  - two or more intermediate levels: graded over at least 0.1-0.2;
  - not monotone in load: no single threshold.
  Prediction 2 ("graded") holds only in the third reading.
- **Prediction 3:** "non-decreasing" admits ties, so it needs no tie rule. The median is jump_tab's KM median (the first
  event year where the established fraction reaches 0.5), not load_tab's upper median. Ties at the 501 floor carry no
  information and are listed as such. A level with fewer than half its seeds established has no median and reads as
  above every defined median; two such levels tie.
- **Prediction 4:** compares arm means over established seeds. Per seed, J is printed beside the R gap, with herd change
  and wild change of R against the 301-400 founders, since these herds are open.
- **exp016:** no heading is added for it. runyears.mjs refuses a label with no "## expNNN" heading in this file, so the
  abandoned registration can run nothing; a heading would open it.

## exp015 clarification, 2026-11-22 (before any result: 0 of 32 runs finished; the reviewer's a7c0fe5)
- **Not monotone,** read first: the waited count falls by 2 or more seeds between neighbouring levels in load order. A fall
  of 1 is within binomial noise and does not trigger it. If it fires, "no single threshold" is the reading even where two
  or more levels are intermediate.
- Each level's waited fraction is printed with its exact (Clopper-Pearson) 95% interval.
- The amendment's "LOAD1 reads 8, not 7" is an expectation from exp010's s5 (waited, crossed at 3708). The recount is
  the tool's, and the results entry quotes the tool's count.

## exp015 clarification 2, 2026-11-22 (before any result; load_tab f044e6e's reading choices, accepted)
The scorer is tools/load_tab.py --exp015 (f044e6e). Its reading choices, accepted as the registration's reading:
1. The span under 60 is measured before J for an established seed (as exp010's Q1), and to the run's end for a seed
   that never establishes.
2. Span length = last minus first year of the run of points under 60; the median herd over the span = the median raw
   herd over that run's year records.
3. Intermediate = 2-6 of 8 waited, counted across all six levels 0.5-1, LOAD05 and LOAD1 included.
4. Not monotone = a fall of 2 or more between neighbouring levels, read first, at each cut.
5. No intermediate level and no change from low to high within 0.5-1 reads "no switch in 0.5-1".
6. Prediction 2 holds only if the 300-year cut reads "graded", the waited count is non-decreasing, and at least two new
   levels have 2-6 waited.
7. Cut-dependent = the full reading (category and location) differs between the 200, 300 and 400 cuts.
8. The 501-floor note is printed when two or more levels have a KM median of 501.
9. Prediction 4's bounds, -0.30 and -0.05, are inclusive.
10. The divergence rule reads only levels with 2 or more established seeds, as exp010's did.
11. The guard checks each LOAD06-09 run against exp010's LOAD1 run of the same seed: only minLoad may differ, with
    spookFixed 0 and spookSchedule '' at identity, and logHistDepth (output only).

## exp015 results (raw)
32 of 32 runs complete (complete: true, last row year 3998), every exit 0 (cpuslot-logs/, batch 1795412363107110800), no
error in any log. Arms as registered, 8 seeds each: LOAD06, LOAD07, LOAD08, LOAD09 (herdPerHerder 1e9, minLoad 0.6-0.9);
parameters identical across runs except id, seed and minLoad. Hosts: 26 on the desktop and 6 on mint. Run times
5010-11238 s. **Commits:** 68edd40 (9 runs, started 05:39-05:43Z on 11-23) and 11763f2 (23, from 06:42Z). `git diff
68edd40 11763f2 -- src load.mjs tools/runyears.mjs` is empty, so one sim. Two 68edd40 runs started on a dirty tree
(LOAD06 seed 8 and LOAD07 seed 1, at 05:42-05:43Z); `git describe --dirty` records that a tracked file was modified,
not which one. **Dirty-run check:** both re-run for 800 years at clean 8f8c514
(job list tools/exp015_dirtyid.jsonl; results/_scratch/exp043_probe/LOAD06id_seed8.json and exp044_probe/LOAD07id_seed1.json)
and compared with tools/cmp_years.py: 0 of 266 records differ in each, 74 shared keys. The registered
Mongo collection is animalDomestication.exp015_load-sweep-mid on mint (all 32 logs print the run line that follows the save, tools/runyears.mjs:100-101); JSON in results/exp015_load-sweep-mid/. Nothing of the runs has been
read beyond these checks. Scoring: the analysis session, with tools/load_tab.py --exp015 as accepted (f044e6e, label
89eebfa; the reviewer's 11763f2).

## exp015 results (raw), note 2026-11-23 (the reviewer's c8d6331)
The dirty-run check covers years 1-800 only: it includes 400 years of herding and each run's J (LOAD06 s8 J 531, LOAD07
s1 J 540; scored.txt). Years 801-4000 of those two runs rest on the code identity (no change to src, load.mjs or
tools/runyears.mjs between 68edd40 and 11763f2, and a clean tree now). They were not re-run at full length; the
steward's decision: the herding and spook code runs, and matches, through 400 years of herding in the checked span.
Correction 2026-11-23 (the reviewer's 19641de): "rest on the code identity" overstates. The commit identity says nothing
about the unknown modified file. Years 801-4000 rest on the unchecked argument that a change to the sim would have shown
within the 800 checked years.

## exp015 results (scored)
**Scored** 2026-11-23 by the analysis session, as registered (68edd40), amended (d377a7d) and clarified (5dce596,
449ee72):
`python tools/load_tab.py "results/exp015_load-sweep-mid;results/exp010_fixed-load;results/exp007_design-checks" --exp015`
(the tool as accepted, 89eebfa; selftest passes all 44 checks, `selftest bad` fails 5). Window 3201-4000, founders
301-400. The guard passed on all 32 runs (the tool stops otherwise): each LOAD06-09 run equals exp010's LOAD1 run of the
same seed except minLoad, with spookFixed 0 and spookSchedule '' at identity. LOADLO, LOAD05 and LOAD1 reproduce
exp010's scored values (herd, R gap, breadth, KM median). Tables in results/exp015_load-sweep-mid/: scored.txt,
selftest.txt, selftest_bad.txt.

**Dose-response** (est = herd >= 100 over the window; by-herd = jump_tab's criterion with the KM median year; R gap,
breadth n and captive-sire share over established seeds; run-offs per herd goat-year):

| arm | load | est | by-herd (KM median) | herd | R gap | n | csire | run-offs | lost |
|---|---|---|---|---|---|---|---|---|---|
| LOADLO | 0.25 | 8 | 8 (501) | 261.6 | -0.055 | 0 | 0.288 | 0.359 | 0.074 |
| LOAD05 | 0.5 | 8 | 8 (525) | 261.9 | -0.104 | 1 | 0.333 | 0.631 | 0.122 |
| LOAD06 | 0.6 | 8 | 8 (510) | 260.6 | -0.112 | 1 | 0.349 | 0.730 | 0.137 |
| LOAD07 | 0.7 | 8 | 8 (561) | 261.3 | -0.167 | 1 | 0.324 | 0.776 | 0.140 |
| LOAD08 | 0.8 | 8 | 8 (609) | 262.5 | -0.214 | 1 | 0.312 | 0.800 | 0.138 |
| LOAD09 | 0.9 | 8 | 7 (792), 1 late | 249.8 | -0.244 | 1 | 0.304 | 0.825 | 0.137 |
| LOAD1 | 1 | 8 | 7 (1614), 1 late | 245.8 | -0.247 | 1 | 0.311 | 0.911 | 0.154 |

**Waited** (the 100-year herd mean under 60 for the cut's span or more after year 500, before J if established, else to
the run's end), by cut, with the 300 cut in two parts:

| arm | @200 | @300 | @400 | @300 [95% CP] | @300 then established | @300 still waiting / late |
|---|---|---|---|---|---|---|
| LOAD05 | 0 | 0 | 0 | 0.000 [0.000, 0.369] | 0 | 0 |
| LOAD06 | 0 | 0 | 0 | 0.000 [0.000, 0.369] | 0 | 0 |
| LOAD07 | 0 | 0 | 0 | 0.000 [0.000, 0.369] | 0 | 0 |
| LOAD08 | 3 | 2 | 1 | 0.250 [0.032, 0.651] | 2 (s7 846, s8 1578) | 0 |
| LOAD09 | 6 | 3 | 3 | 0.375 [0.085, 0.755] | 2 (s1 1158, s6 2019) | 1 (s8, late 3630) |
| LOAD1 | 8 | 8 | 8 | 1.000 [0.631, 1.000] | 7 | 1 (s5, late 3708) |

The LOAD1 recount, from the tool: 8 waited at the 300 cut, 7 then established and s5 crossing late at 3708 (exp010's Q1,
which required establishment, gave 7). LOADLO waits in no seed at any cut.

**Predictions:**
1. Every new level establishes in 6 or more of 8: **holds** (8, 8, 8, 8).
2. Waiting graded at the 300 cut: **holds**. Waited is non-decreasing over 0.5-1 (0, 0, 0, 2, 3, 8), two new levels have
   2-6 waited (LOAD08, LOAD09), and the reading is "graded". The strict non-decreasing test did not bite: no count falls
   between neighbours at any cut.
3. KM median non-decreasing over 0.5-1: **fails**, at the first step only: LOAD05 525, LOAD06 510. From 0.6 up it rises
   (510, 561, 609, 792, 1614). The fall is 15 years, within the first century after herding, where LOAD05 and LOAD06 each
   have 2 seeds "at once" (501); the registration admits no tolerance, so it fails as registered. No floor note (only
   LOADLO has a median of 501, and it is outside 0.5-1).
4. New levels' R gap within [-0.30, -0.05], and LOAD09 more negative than LOAD06: **holds** (-0.112, -0.167, -0.214,
   -0.244; LOAD09 -0.244 against LOAD06 -0.112).

**Decision rule, waiting: graded at the registered 300 cut; cut-dependent.** At 300, two levels are intermediate (LOAD08
2, LOAD09 3): graded over at least 0.1-0.2. At 200 the reading is the same (LOAD08 3, LOAD09 6). At 400 only LOAD09 is
intermediate (3; LOAD08 1): the switch is located at 0.9, its width unresolved at this spacing. Not monotone fires at no
cut. The cut dependence comes from the spans themselves, which are continuous at the upper levels rather than split into
short and long. Longest span under 60 after 500, per seed: LOAD08 0, 30, 81, 84, 87, 243, 324, 1053; LOAD09 45, 192, 243,
252, 267, 633, 1500, 3102. At 0.9, three seeds that "grew" at the 300 cut spent 243-267 years under 60 first. The
No seed below 0.8 waits at any cut (LOAD07's longest span is 177 years); from 0.8 the spans lengthen with the load.
At no cut is it a switch narrower than 0.1. To Chris with the per-seed table in scored.txt.

**Median raw herd** (read only for spans of 200 years or more): 3.0-8.0 in every waited seed at 0.8-1, and 4.5-20.5 in
the four 0.8-0.9 seeds with spans of 243-267 years. No still-waiting seed has a median under 3: LOAD09 s8 holds 4.0 over
3102 years and LOAD1 s5 holds 6.0 over 3183. Both kept a herd of a few goats; neither is a herd that never formed.

**Decision rule, divergence:** no level has established herds with R gap <= -0.30 and breadth >= 3 (levels read:
LOADLO to LOAD1, all with 8 established; arm means -0.055 to -0.247, breadth 0-1). exp010's
conclusion stands over 0.25-1: no fixed load gives both a persisting herd and divergence. In the new levels, five single seeds reach R
-0.30 or below (LOAD07 s6 -0.304, LOAD08 s5 -0.334 and s7 -0.321, LOAD09 s6 -0.310 and s7 -0.432); the rule reads
levels, not seeds.

**R gap with load** (descriptive): the arm-mean gap grows from -0.104 at 0.5 to -0.244 at 0.9, then -0.247 at 1. Per seed,
herd change of R against the founders runs -0.215 to -0.281 at 0.5 and -0.100 to -0.504 at 1, while wild change stays
within -0.044 to -0.194 at every level 0.5-1. Run-offs per herd goat-year rise with the load (0.631 to 0.911); goats lost for good
are flat over 0.6-0.9 (0.137-0.140).

**Waited beside not waited** (300 cut; descriptive, not a test): LOAD08 -0.250 (n 2) against -0.202 (n 6); LOAD09 -0.191
(n 3) against -0.276 (n 5). No direction. The late-crossing seeds have the smallest gaps (LOAD09 s8 -0.088, LOAD1 s5
-0.056), as exp010 found for LOAD1.

## exp015 results (scored), correction 2026-11-23 (the reviewer's c8d6331, wording; no number changes)
Three wording fixes. They replace the passages named below. The tables and verdicts are unchanged.
1. **Waiting** (replaces the "Decision rule, waiting" paragraph's lead, its sentence "At no cut is it a switch narrower
   than 0.1", and the stray "The" before "No seed below 0.8"):
   - The spans come first. Per level, the longest span under 60 after 500 is 177 years at 0.7, 1053 at 0.8 and 3102 at
     0.9. No seed below 0.8 waits at any cut. From 0.8 up the spans are continuous rather than split into short and
     long.
   - Read by category, the result is graded at the registered 300 cut and at 200, and located at 0.9 at 400:
     cut-dependent.
   - "Graded at 300" rests on one seed: LOAD08 s7's span is 324 years. Were it 25 or more years shorter (under 300),
     LOAD08 would have 1 waited and the 300 cut would read "located at 0.9".
2. **Single seeds at -0.30** (moved out of the divergence paragraph into "R gap with load"): in the new levels, five
   single seeds reach R -0.30 or below (LOAD07 s6 -0.304, LOAD08 s5 -0.334 and s7 -0.321, LOAD09 s6 -0.310 and s7
   -0.432). This is R gap alone. Breadth is not read per seed, and no level meets the rule.
3. **Prediction 3** (replaces "within the first century after herding"): both medians are the 4th of 8 J within 24 years
   of the floor (LOAD05 525, LOAD06 510). The J at 0.5 and 0.6 overlap throughout (501-669 and 501-639).

## exp017 — Alarm spreading as the spook's herd-size factor: with the herder load fixed at 0.5, a herder spook cascades through the herd (alarmSpread 0.1-1). Does it give a persisting herd with R gap <= -0.30 and breadth >= 3, as the herder-load rule does?
**Pre-registered:** 2026-11-23. Chris: "the idea is that alarm spreading is a different mechanism for the spook rule.
let's register this and test it. the alarm should spread faster in denser herds."
Mongo animalDomestication.exp017_alarm-spread (mint); results/exp017_alarm-spread; job list tools/exp017.jsonl (40 runs,
cpuslot --anywhere); code HEAD at queueing (named in the raw entry).
**Why:** in every arm so far, a strong R gap (-0.30 or below) together with divergence on other traits (breadth 3 or
more) has come only with the herder-load spook rule, where the spook chance grows with herd size (herderAlarm × R ×
fear × herd / (herdPerHerder × herders)): REF -0.636, breadth 6 (exp007). A fixed load gives at most -0.25 with breadth
0-1 over 0.25-1 (exp010, exp015). The herd-size factor there is a herder's labour limit. Alarm spreading puts a herd-size
factor in the goats instead: a goat that bolts sets off its neighbours, so in a denser herd one spook moves more goats.
Here the herder's own spook keeps a fixed load (0.5, exp010's LOAD05: established at once in 8 of 8, R gap -0.104,
breadth 1), so any herd-size effect comes from the spreading.
**The mechanism** (src, c364a5f; default alarmSpread 0 = off): when the herder spooks a goat, it bolts as before. Each
goat of the same herd walking with the herder (not loose, not tethered or kept at camp, not a kid following its
mother) in the 3×3 cells around a bolter catches the alarm with chance alarmSpread × its R × its fearOfHumans, bolts
the same way (away from the herder; a run-off beyond keepRadius, fetched back or lost as before), and passes the alarm
on from where it stood: a cascade within the sub-tick, each goat bolting at most once a sub-tick. Positions come from
the spatial index (where goats stood at the sub-tick's start). The herd ranges within herdRange 8 of the herder, so a
bigger herd is a denser one. New output counters per year: spooked (the herder's spooks) and alarmCaught (goats that
caught a spread alarm).
**Identity:** alarmSpread 0 at 4df0e92 against exp010's LOAD05_seed1 (tools/spread_id.jsonl;
results/_scratch/exp045_probe/LOAD05id_seed1.json), tools/cmp_years.py: 0 of 266 records differ (68 shared keys; the new
counters only in the new run); hist and histHerd identical over the 800 years.
**Calibration probe, seen before registering** (tools/spread_probe.jsonl, seed 1, 1200 years, load 0.5; read with
tools/spread_probe.py, 401-1200; results/_scratch/exp046-048_probe). Bolts per spook (1 = no spread) by herd size:
- 0.1: 1.03 (herd 1-9), 1.25 (10-29), 1.46 (30-99), 2.03 (100-199), 2.09 (200+).
- 0.3: 1.12, 1.50, 2.22, 3.30, 3.11.
- 1: 1.60 (1-9), 2.07 (10-29); the herd stayed under 30 through year 1200.
The tool also printed bolts and run-offs per herd goat-year by herd size, which I saw: at 0.3 with herd 200+, 0.663 bolts
per goat-year against 0.831 for alarmSpread 0. These are seed 1's first 800 years of herding; seed 1's main runs at 0.1,
0.3 and 1 repeat those years exactly. The levels below were chosen from the probe to run from a cascade of about 2 at
full herd to one that holds the herd small.
**Arms** (seeds 1-8, 4000 years, herding at 400; exp010's arguments, herdPerHerder 1e9, minLoad 0.5): SPR01, SPR02,
SPR03, SPR05, SPR10 (alarmSpread 0.1, 0.2, 0.3, 0.5, 1). Read beside exp010's LOAD05 (alarmSpread 0, same seeds and
arguments) and REF (exp007, the herder-load rule). Herds open, as in exp010.
**Measure** (the analysis session; window 3201-4000, founders 301-400; tools/load_tab.py extended for the five levels,
built and checked before any result): per level, established (herd >= 100 over the window) and by jump_tab's criterion
with the KM median; Q1 per seed (at once / grew / waited / never, with waited = the 100-year herd mean under 60 for 300+
consecutive years after year 500, as exp015); herd; R gap; breadth (core traits with abs(gap) >= 0.10); captive-sire
share; ranOff, refetched, escaped per herd goat-year. The mechanism check: tools/spread_probe.py over 401-4000, per
level, bolts per spook by herd-size bin.
**Predictions** (mine):
1. Mechanism: in every level, bolts per spook in the highest herd-size bin reached with 10 or more rows exceeds the
   1-9 bin.
2. SPR01, SPR02 and SPR03 establish (herd >= 100 over the window) in 6 or more of 8; SPR10 in 2 or fewer.
3. Every level with 2 or more established seeds has an R gap more negative than LOAD05's (-0.104), and among levels
   with 6 or more established, the R gap does not rise with alarmSpread.
4. At least one level established in 6 or more of 8 has R gap -0.30 or below and breadth 3 or more.
**Decision rule:**
- If a level established in 6 or more of 8 has R gap -0.30 or below and breadth 3 or more: alarm spreading is a second
  mechanism that gives what the herder-load rule gives, a persisting herd with strong R and divergence, with the
  herd-size factor in the goats' behaviour rather than the herder's labour. To Chris and the author.
- Otherwise, if some level has R gap -0.30 or below and breadth 3 or more but in fewer than 6 established seeds: the
  spreading that gives the filter also holds the herd small; read with Q1 (waiting), as exp015.
- Otherwise: alarm spreading at 0.1-1 on a load of 0.5 does not give strong R with divergence.
- If prediction 1 fails at a level, that level's reading is not about density: say so beside it.
- Descriptive, not a test: R gap and breadth against REF's; the wait by level.

## exp017 amendment, 2026-11-23 (before any result: 0 of 40 runs finished; the reviewer's 60de449)
1. **Prediction 1 window.** The catch chance is the receiver's alarmSpread × R × fear, so cascades shrink as the filter
   lowers R; over 401-4000 the 200+ bin would be mostly late, low-R years, and a level whose filter works could fail
   prediction 1 for that reason. Prediction 1 is read over 401-1200 (as the probe), with each level's 8 seeds pooled by
   summing their year rows in each herd-size bin; 401-4000 is printed as descriptive. Prediction 1 was seen for seed 1
   at 0.1, 0.3 and 1 in the probe.
2. **What the probe showed.** The bolt-rate line disclosed above (seed 1 at 0.3, herd 200+: 0.663 herder-plus-spread
   bolts per goat-year against 0.831 at alarmSpread 0, with about 3 bolts per spook) means the herder's own spooks per
   goat fell well below alarmSpread 0's. At a fixed load that can come only from R × fear, so it was a look at the
   direction of predictions 3 and 4 in seed 1. The scorer prints, descriptively, each level's R gap with and without
   seed 1.
3. **Readings for the scorer:**
   - Prediction 3: arm means of the established seeds (herd >= 100 over the window) against LOAD05 as the scorer
     recomputes it. "Does not rise" = non-increasing (more negative or equal) between neighbouring levels within the
     subset with 6 or more established; ties pass; no tolerance.
   - Prediction 4 and branch 1: arm means over established seeds; R gap -0.30 inclusive, breadth >= 3.
   - Branch 2 needs 2 or more established seeds at the level. Reworded: "strong R with divergence appears only at
     levels where the herd does not reliably persist; read with Q1". It is not read as the spreading holding the herd
     small.
   - Waited is exp015's uncensored count (amendment d377a7d's definition: span under 60 for 300 years or more, before J
     if established, else to the run's end), with the 200 and 400 cuts printed.
   - Guard: each run equals exp010's LOAD05 run of the same seed except alarmSpread (and logHistDepth, output only),
     as exp015's.
4. **Scope.** The spread radius is the 3×3 around a bolter, so the density effect saturates once neighbouring cells are
   full; in the probe, bolts per spook is about flat from herd 100-199 to 200+. It acts as a step with herd size, not a
   proportional rise like the herder load. Any reading is for radius 1. Branch 1 reads "on a load of 0.5", with the
   captive-sire share printed beside REF's.

## exp017 results (raw)
40 of 40 runs complete (complete: true, last row year 3998), every exit 0 (cpuslot-logs/, batch 1795452922106149000), no
error, exception or warning in any log. Each log carries the db client's packet-size advisory (9-10 MB of BSON, over its
4 MB suggestion), which does not stop the save. Arms as registered, 8 seeds each: SPR01, SPR02, SPR03, SPR05, SPR10
(alarmSpread 0.1, 0.2, 0.3, 0.5, 1; herdPerHerder 1e9, minLoad 0.5). Parameters are identical across runs except id, seed
and alarmSpread. Hosts: 28 on the desktop and 12 on mint. Run times 6187-11193 s.
**Commits:**
- ae6ddc4: 7 runs, started 16:55-16:59Z on 11-23.
- 35e7620: 33 runs, from 19:02Z.
`git diff ae6ddc4 35e7620 -- src load.mjs tools/runyears.mjs` is empty, so one sim.
**Dirty runs:** two ae6ddc4 runs started on a dirty tree: SPR01 seed 6 and seed 7, at 16:59:26Z and 16:59:31Z. `git
describe --dirty` records that a tracked file was modified, not which one. Two commits landed within a minute after:
60de449 (notes/review, 16:59:47Z) and ed844b5 (this ledger, 17:00:25Z). Which file was modified is not checked.
**Dirty-run check:** both are being re-run at full length (4000 years) on a clean tree, d4ee84b (job list
tools/exp017_dirtyid.jsonl, the empty 3dd4cc9 corrected). They will be compared with tools/cmp_years.py, and the result
added here as a dated note. Until then those two runs are provisional.
The registered Mongo collection is animalDomestication.exp017_alarm-spread on mint. All 40 logs print the run line that
follows the save (tools/runyears.mjs:100-101). JSON is in results/exp017_alarm-spread/. Nothing of the runs has been read
beyond these checks.
**Corrections to the registration** (the reviewer's 23f0958):
- REF is exp005's (results/exp005_b0-pilot), not exp007's: exp007 has no REF runs.
- Amendment point 4's account of the saturation is a guess whose cause is not checked: "the density effect saturates
  once neighbouring cells are full". The probe shows only that bolts per spook is about flat from herd 100-199 to 200+.
Scoring: the analysis session, with tools/load_tab.py --exp017 as accepted (9b54daf; the reviewer's 23f0958 and 456f9ff).

## exp017 results (scored)
`python tools/load_tab.py "results/exp017_alarm-spread;results/exp010_fixed-load;results/exp005_b0-pilot;results/exp006_two-corner" --exp017`
through cpuslot, tool 9b54daf. Selftest 86 ok; selftest bad fails 13. Guard passed on all 40: each SPR run equals
exp010's LOAD05 run of the same seed except alarmSpread, with spookFixed 0 and spookSchedule '' at identity. Tables in
results/exp017_alarm-spread/ (scored.txt, selftest.txt, selftest_bad.txt). REF is exp005's eight runs; its row
reproduces exp010's (herd 287.8, R gap -0.636, breadth 6, csire 0.064). LOAD05 recomputes at R gap -0.104, as
registered. All 40 runs are scored as registered; SPR01 seeds 6 and 7 are provisional (raw entry; see the end).

Window 3201-4000; established = herd >= 100 over the window; herd over all 8 seeds; R gap, breadth and csire over the
established seeds; waited at the registered 300 cut; KM median year established.
| level | alarmSpread | est | herd | R gap | breadth | csire | waited @300 | KM median |
|---|---|---|---|---|---|---|---|---|
| LOAD05 | 0 | 8 | 261.9 | -0.104 | 1 | 0.333 | 0 | 525 |
| SPR01 | 0.1 | 8 | 266.8 | -0.314 | 1 | 0.277 | 1 | 606 |
| SPR02 | 0.2 | 8 | 263.9 | -0.462 | 2 | 0.214 | 0 | 696 |
| SPR03 | 0.3 | 8 | 261.4 | -0.524 | 2 | 0.171 | 5 | 957 |
| SPR05 | 0.5 | 7 | 236.9 | -0.591 | 3 | 0.123 | 8 | 1551 |
| SPR10 | 1 | 0 | 11.8 | - | - | - | 8 | - |
| REF | load grows | 8 | 287.8 | -0.636 | 6 | 0.064 | 0 | 705 |

**Predictions:**
1. **Holds at every level.** Years 401-1200, each level's 8 seeds pooled. Rows are recorded year rows (every 3rd year),
   summed over seeds. Bolts per spook in the highest bin with 10+ rows, against the 1-9 bin (its rows and spooks):
   - SPR01: 200- 2.058 (1294 rows) against 1.031 (181 rows, 781 spooks).
   - SPR02: 200- 2.787 (982 rows) against 1.083 (77 rows, 396 spooks).
   - SPR03: 200- 3.132 (569 rows) against 1.122 (301 rows, 1522 spooks).
   - SPR05: 200- 5.636 (25 rows) against 1.252 (581 rows, 3187 spooks). The 25 rows are from seeds 1 (7) and 7 (18).
   - SPR10: 10-29 1.944 (610 rows) against 1.512 (1502 rows, 9300 spooks). No bin above 10-29 reached 10 rows.
   Every level was testable, and all 40 SPR runs carry the alarmCaught counter. A level printed "no alarmCaught counter"
   would mean missing output, not a herd that never grew; that line appears only for LOAD05 (exp010 predates the
   counter, c364a5f), which prediction 1 does not read.
   Descriptive: from 100-199 to 200- over 401-1200, bolts per spook rises at SPR01 (1.966 to 2.058) and SPR05 (4.902 to
   5.636) and falls at SPR02 (2.898 to 2.787) and SPR03 (3.430 to 3.132); the cause is not checked. Over 401-4000
   (descriptive) the top bin also exceeds 1-9 at every level.
2. **Holds.** SPR01, SPR02 and SPR03 established in 8 of 8; SPR10 in 0. (SPR05: 7, not in the prediction.)
3. **Holds.** Four levels have 2 or more established (SPR01, SPR02, SPR03, SPR05), all more negative than LOAD05's
   -0.104. All four have 6 or more established, and the R gap falls at each step: -0.314, -0.462, -0.524, -0.591.
   SPR10 (0 established) is not read.
4. **Holds, at SPR05 only:** 7 of 8 established, R gap -0.591, breadth 3. SPR03 has R gap -0.524 with breadth 2.
   SPR05's breadth 3 is R, B and T, and B's gap is -0.105. Had it been 0.005 or more smaller in magnitude, breadth
   would be 2 and no level would meet the prediction (branch 3: no strong R with divergence).

**Decision rule: branch 1, at SPR05.** As registered and amended: on a load of 0.5, alarm spreading (radius 1) is a
second mechanism that gives what the herder-load rule gives, a persisting herd with strong R and divergence, with the
herd-size factor in the goats' behaviour rather than the herder's labour. To Chris and the author. Read with:
- It rests on one level, and at that level on B's -0.105 (prediction 4).
- How SPR05's herds got there: all 8 seeds waited at every cut (200, 300 and 400). Seven then established, at J
  1080-2724 (KM median 1551, against LOAD05's 525 and REF's 705), after spans under 60 of 510-2178 years. Seed 6 was
  still waiting at year 4000 (span 3498). "Persisting" holds over the 3201-4000 window, after waits of five centuries
  or more.
- Prediction 1 holds at SPR05; its 200- bin over 401-1200 is 25 rows from two seeds.
- Beside REF (descriptive): breadth 3 against 6, and every core trait's gap smaller in magnitude than REF's (R -0.591
  against -0.636, B -0.105 against -0.295, T +0.245 against +0.447, A -0.060 against -0.148, S +0.040 against +0.174).
  Captive-sire share 0.123 against REF's 0.064.

**Waiting by level** (descriptive; exp015's uncensored definition, amendment d377a7d). Waited at 200 / 300 / 400:
LOAD05 0/0/0, SPR01 1/1/0, SPR02 2/0/0, SPR03 6/5/2, SPR05 8/8/8, SPR10 8/8/8, REF 2/0/0. Waiting rises with
alarmSpread at every cut except SPR01 to SPR02 at 300 (1 to 0). SPR01's one is seed 1, whose span of 309 years is 9 over
the cut. The KM median rises with alarmSpread: 525, 606, 696, 957, 1551, and under half established at SPR10.

**SPR10:** no seed established; herd 11.8 over the window; all 8 still waiting at year 4000; R gap over all seeds
-0.039. Run-offs per herd goat-year 1.923, against LOAD05's 0.631.

**Seed 1** (descriptive): the R gap of established seeds with and without seed 1 differs by 0.003 or less at every
level (for example SPR05 -0.591 with, -0.593 without). Seed 1, seen in the probe, does not carry the R gaps.

**Waited beside not waited** (descriptive, 300 cut): SPR03 waited -0.518 (n 5), did not -0.532 (n 3); SPR01 -0.295 (n 1)
against -0.317 (n 7). At SPR05 every seed waited; the seven established run from -0.616 to -0.577.

**SPR01 seeds 6 and 7** (provisional, dirty tree): their R gaps (-0.319, -0.314) and J (702, 528) lie within the
ranges of SPR01's other six seeds (R -0.364 to -0.278, J 507-846). SPR01 is not the branch-1 level. If the clean
re-runs differ, the steward asks for a rescore without them.

## exp017 results (scored), correction 2026-11-23 (the reviewer's 33c86fd; wording and additions, no number or verdict changes)
The readings stand: P1-P4 hold, P4 at SPR05 only, and the rule gives branch 1 at SPR05. Four changes to the entry above.
1. **Prediction 4's margin, and the graded gaps.** This replaces "Had it been 0.005 or more smaller in magnitude".
   - B's gap prints -0.105, to three places. It clears the 0.10 line by about 0.005 (between 0.0045 and 0.0055).
   - B's spread over SPR05's 7 established seeds is not printed.
   - The breadth count is a threshold crossing on a graded trend. Across alarmSpread 0, 0.1, 0.2, 0.3 and 0.5, the gaps
     in five traits grow at every step (trait table):
     - R -0.104, -0.314, -0.462, -0.524, -0.591.
     - T +0.035, +0.090, +0.146, +0.193, +0.245.
     - B -0.011, -0.017, -0.047, -0.048, -0.105.
     - L +0.015, +0.028, +0.039, +0.051, +0.080.
     - A -0.007, -0.011, -0.022, -0.034, -0.060.
   - Breadth goes 1, 1, 2, 2, 3 because B crosses 0.10 between 0.3 and 0.5.
   - For Chris and the paper, lead with this: the gaps in R, T, B, L and A grow at every step of alarmSpread; breadth
     reaches 3 at 0.5, with B at -0.105 against the 0.10 line.
   - Before the paper calls SPR05 "divergence", it needs B's per-seed gaps at SPR05 from a committed tool, as a
     descriptive line. Without them the sentence stays at "meets the criterion by about 0.005 on one trait".
2. **Branch 1 beside REF.** The registered sentence stands as registered. It is met on the criterion (6 or more
   established, R gap -0.30 or below, breadth 3 or more), not on the herd.
   - For Chris and the author: on a load of 0.5, spreading reaches the divergence line only at 0.5, after waits of
     510-2178 years, with half REF's breadth.
   - Across levels, the filter strengthens as the wait lengthens:
     - KM median 525, 606, 696, 957, 1551;
     - waited at 300: 0, 1, 0, 5, 8.
   - No level gives REF's growth without a wait (REF waited 0 at 300, KM median 705, breadth 6).
3. **Mechanism bins.** This goes beside "Over 401-4000 the top bin also exceeds 1-9 at every level".
   - Over 401-4000, the 200- bin falls below 100-199 at SPR02 (2.730 to 2.411), SPR03 (3.191 to 2.815) and SPR05 (4.387
     to 3.598). It is flat at SPR01 (1.892, 1.893).
   - Over 401-1200, SPR05 rises through every bin: 1.252, 1.812, 2.590, 4.902, 5.636.
   - Bolts per spook is not a proportional rise with herd size, and not a step either. The amendment's "step" is not
     carried into anything for Chris or the paper, which give the bins per level. The cause is not checked.
4. **Wording.**
   - Prediction 1 at SPR05 (beside its 25 rows): the direction does not rest on those rows.
     - The pooled 30-99 bin (285 rows, 2.590) and 100-199 bin (61 rows, 4.902) exceed 1-9's 1.252.
     - In every SPR05 seed, the 10-29 bin exceeds the 1-9 bin (1.71-1.95 against 1.19-1.45).
   - Waiting. This replaces "Waiting rises with alarmSpread at every cut except": waiting is non-decreasing in
     alarmSpread at every cut except SPR01 to SPR02 at 300 (1 to 0).
   - SPR01 seeds 6 and 7: no conclusion depends on them.
     - P2 would be 6 of 6.
     - Their R gaps are less negative than every SPR02 seed's (the least negative is -0.415).
     - SPR01 is not the branch level.
     - They stay provisional until the clean re-runs are compared.
   - Captive-sire share falls with alarmSpread: 0.333, 0.277, 0.214, 0.171, 0.123 (REF 0.064). It is reported, not
     interpreted.

## exp017 results (scored), correction 2 2026-11-24 (REF's source; the reviewer's bc24350; no number changes)
REF is exp005's seeds 1-4 plus exp006's seeds 5-8 (results/exp005_b0-pilot holds REF_seed1-4 and
results/exp006_two-corner holds REF_seed5-8), not "exp005's eight runs" as the scored entry says. load_tab read both
folders, so REF's row is these 8 seeds, the same as exp010's REF row. No number changes. The raw entry's "REF is
exp005's" under "Corrections to the registration" means the same eight runs.

## exp017 results (raw), note 2026-11-24: the dirty-run check
SPR01 seeds 6 and 7 were re-run at full length (4000 years) on a clean tree. The runs are d4ee84b with dirty false,
started 05:52Z on 11-24, one on the desktop and one on mint. Job list tools/exp017_dirtyid.jsonl; output in
results/_scratch/exp049_probe/SPR01id_seed6.json and results/_scratch/exp050_probe/SPR01id_seed7.json. Both exited 0
(cpuslot-logs/, batch 1795499519139204100). Each was compared with its exp017 run using tools/cmp_years.py:
- 0 of 1333 year records differ in each, over 76 shared keys, with no key in only one run.
- hist, histHerd and samples are identical in both.
The two runs match their clean re-runs over the whole run, so they are no longer provisional. All 40 exp017 runs stand
as scored, and nothing is rescored.

## exp017 gene flow, plan 2026-11-24 (descriptive; written before any flow output was read)
The analysis session's plan, for Chris's question via the steward: does alarm spreading give the selection in the herd
with less closure (herd-wild gene flow) than REF's herder-load rule? Descriptive, no predictions. Fixed before looking:
- **Tool:** tools/flow_tab.py as it stands (its measures, row filter and per-goat-year ratios). Any new argument goes in
  the committed tool. The only one planned is a folder tag, so exp009's REF can sit beside exp005/006's REF under its
  own name.
- **Windows:** 401-900 (herding years 1-500, when the wild falls with the herd in the R plots), 901-1600 (the
  spring-back), and 3201-4000 (the scored window). Each is one flow_tab call.
- **Arms:** LOAD05 (exp010), SPR01, SPR02, SPR03, SPR05, SPR10 (exp017), and REF. REF is the scored REF: exp005's
  seeds 1-4 and exp006's seeds 5-8, the folders exp017 was scored with.
- **Pairs:** --pairs SPR01-LOAD05, SPR02-LOAD05, SPR03-LOAD05, SPR05-LOAD05, SPR10-LOAD05 (same seed, same history
  to year 400), plus --perseed.
- **REF's missing columns.** The exp005/006 REF runs predate wildConc, capIn and capBred, so hsw, hout, bredF and bredM
  print "-" for them. exp009's REF runs (seeds 1-8) carry those keys.
  - They are used only if they are the same REF. Parameters must be equal apart from id, cInitLo, cInitHi (exp009's
    shifted neutral marker C, which has its own random stream) and logHistDepth (output only).
  - Year records must be equal over the shared keys, with C's fields left out, from the first record to the point
    where they first differ.
  - The check goes in a committed tool and must fail on a deliberately wrong input first.
  - If it passes, exp009's REF is printed as its own row (REF9), and its other columns should equal REF's. If it does
    not, those columns stay "-" for REF and the reason is given.
- **Waiting herds:** where a level's herd is under 60 goats in a window (SPR05 and SPR10 early, SPR10 throughout), its
  rates are per herd goat over a small herd. The herd column is printed beside them, and they are read that way.
- **Output:** results/exp017_alarm-spread/flow_<window>.txt, plus a descriptive entry. It goes to the reviewer
  first, and to Chris only after the reviewer settles it.

## exp017 gene flow (descriptive), 2026-11-24
Plan f240595; tools b328a1f and b0b300a. Descriptive, no predictions. Commands, through cpuslot, with W = 401-900,
901-1600 and 3201-4000 (results/exp017_alarm-spread/flow_W.txt):
`python tools/flow_tab.py W "results/exp017_alarm-spread;results/exp010_fixed-load;results/exp005_b0-pilot;results/exp006_two-corner;results/exp009_mutation-pull=9" LOAD05,SPR01,SPR02,SPR03,SPR05,SPR10,REF,REF9 --pairs SPR01-LOAD05,SPR02-LOAD05,SPR03-LOAD05,SPR05-LOAD05,SPR10-LOAD05,REF9-REF --perseed`
The table below is `python tools/flow_digest.py "<the three files>" LOAD05,SPR01,SPR02,SPR03,SPR05,SPR10,REF,REF9
herd,capt,csire,cdam,depth,esc,feral,hsw,bredM` (flow_digest.txt). It reprints flow_tab's seed means without their SEs,
and checks each cell against its source.

**REF9 is REF.** `python tools/ref_match.py "results/exp005_b0-pilot;results/exp006_two-corner" results/exp009_mutation-pull REF`
(ref_match_REF.txt):
- Parameters are equal apart from id, logHistDepth and cInitLo/cInitHi; buckPrefValue and doePrefValue are only in
  exp009's runs, at 0.
- In each of the 8 seeds, 0 of 1333 year records differ over the shared keys, with the marker C left out.
- Its wrong inputs fail (ref_match_REF_bad.txt): a changed minLoad stops; one changed herded shows 1 differing record;
  keeping C shows 1333.
- The REF9 - REF pair is 0 on every column both have. (That pair was added to the plan's list as this check.)
So REF's hsw and bredM are read from REF9.

**Measures** (flow_tab; per herd goat per recorded year unless a share; seed means over all 8 seeds, established or
not):
- **Into the herd:** capt = goats captured; csire = herd conceptions by a sire captured himself; cdam = by a dam
  captured herself; depth = generations since the wild of the herd genome.
- **Out of the herd:** esc = herd goats lost to the wild; feral = the wild genome's share from herd-born goats (a stock,
  not a flow); hsw = wild does' conceptions by a herd sire.
- **Captive fate:** bredM = first breedings by captured bucks per captured buck.

| measure | years | LOAD05 | SPR01 | SPR02 | SPR03 | SPR05 | SPR10 | REF | REF9 |
|---|---|---|---|---|---|---|---|---|---|
| herd | 401-900 | 207.7 | 145.6 | 113.2 | 51.8 | 13.7 | 7.0 | 119.2 | 119.2 |
| herd | 901-1600 | 264.0 | 264.4 | 258.6 | 223.9 | 80.4 | 8.8 | 275.9 | 275.9 |
| herd | 3201-4000 | 261.9 | 266.8 | 263.9 | 261.4 | 236.9 | 11.8 | 287.8 | 287.8 |
| capt | 401-900 | 0.049 | 0.103 | 0.126 | 0.211 | 0.394 | 0.575 | 0.118 | 0.118 |
| capt | 901-1600 | 0.044 | 0.056 | 0.046 | 0.055 | 0.179 | 0.488 | 0.029 | 0.029 |
| capt | 3201-4000 | 0.042 | 0.045 | 0.038 | 0.036 | 0.062 | 0.432 | 0.026 | 0.026 |
| csire | 401-900 | 0.306 | 0.405 | 0.368 | 0.344 | 0.314 | 0.305 | 0.294 | 0.294 |
| csire | 901-1600 | 0.350 | 0.324 | 0.220 | 0.215 | 0.292 | 0.325 | 0.091 | 0.091 |
| csire | 3201-4000 | 0.333 | 0.277 | 0.214 | 0.171 | 0.159 | 0.348 | 0.064 | 0.064 |
| cdam | 401-900 | 0.138 | 0.216 | 0.249 | 0.352 | 0.564 | 0.725 | 0.217 | 0.217 |
| cdam | 901-1600 | 0.128 | 0.136 | 0.096 | 0.109 | 0.322 | 0.678 | 0.046 | 0.046 |
| cdam | 3201-4000 | 0.122 | 0.113 | 0.083 | 0.071 | 0.114 | 0.660 | 0.032 | 0.032 |
| depth | 401-900 | 3.30 | 2.39 | 2.49 | 1.75 | 0.88 | 0.49 | 3.30 | 3.30 |
| depth | 901-1600 | 3.66 | 4.30 | 6.71 | 7.06 | 2.91 | 0.61 | 12.86 | 12.86 |
| depth | 3201-4000 | 3.95 | 5.23 | 7.37 | 8.98 | 10.47 | 0.72 | 14.69 | 14.69 |
| esc | 401-900 | 0.152 | 0.318 | 0.355 | 0.366 | 0.407 | 0.417 | 0.340 | 0.340 |
| esc | 901-1600 | 0.127 | 0.197 | 0.158 | 0.181 | 0.354 | 0.459 | 0.101 | 0.101 |
| esc | 3201-4000 | 0.122 | 0.145 | 0.126 | 0.121 | 0.155 | 0.499 | 0.082 | 0.082 |
| feral | 401-900 | 0.684 | 0.557 | 0.509 | 0.355 | 0.257 | 0.181 | 0.451 | 0.451 |
| feral | 901-1600 | 0.845 | 0.764 | 0.628 | 0.541 | 0.516 | 0.392 | 0.240 | 0.240 |
| feral | 3201-4000 | 0.844 | 0.737 | 0.612 | 0.512 | 0.420 | 0.485 | 0.128 | 0.128 |
| hsw | 401-900 | 0.002 | 0.003 | 0.003 | 0.003 | 0.002 | 0.001 | - | 0.004 |
| hsw | 901-1600 | 0.003 | 0.003 | 0.003 | 0.003 | 0.004 | 0.001 | - | 0.002 |
| hsw | 3201-4000 | 0.003 | 0.002 | 0.003 | 0.002 | 0.003 | 0.002 | - | 0.003 |
| bredM | 401-900 | 0.108 | 0.118 | 0.147 | 0.168 | 0.193 | 0.162 | - | 0.131 |
| bredM | 901-1600 | 0.116 | 0.103 | 0.096 | 0.106 | 0.212 | 0.192 | - | 0.063 |
| bredM | 3201-4000 | 0.121 | 0.101 | 0.100 | 0.089 | 0.116 | 0.222 | - | 0.060 |

**Readings** (descriptive):
1. **Beside REF, alarm spreading leaves the herd more open both ways after the first window.** In 3201-4000, with
   herds near REF's size (236.9-266.8 against 287.8), SPR01-SPR05 against REF:
   - captures 0.036-0.062 against 0.026;
   - captive-sire share 0.159-0.277 against 0.064;
   - herd lineage depth 5.23-10.47 generations against 14.69;
   - herd goats lost to the wild 0.121-0.155 against 0.082.
   901-1600 shows the same. In 401-900, SPR01 and SPR02 sit near REF on captures and losses (herds 145.6 and
   113.2 against 119.2), with a higher captive-sire share (0.405 and 0.368 against 0.294).
2. **The wild's herd-derived share falls back in REF only.**
   - In REF, feral falls over the three windows: 0.451, 0.240, 0.128.
   - At every spreading level it rises from the first window to the second and stays high: SPR01 0.557, 0.764, 0.737;
     SPR03 0.355, 0.541, 0.512; SPR05 0.257, 0.516, 0.420. LOAD05 does the same (0.684, 0.845, 0.844).
   - This matches the shape Chris described (the wild moves with the herd, then springs back, in REF), here on
     ancestry. Whether it drives the wild's R spring-back is not checked.
3. **The herd-to-wild route is lost herd goats, not herd bucks.** Herd sires father 0.001-0.004 of wild does'
   conceptions in every arm and window, REF9 included. So the measured outflow is herd goats lost to the wild (esc).
4. **Beside LOAD05, spreading closes the herd partly.** Paired over the same seeds in 3201-4000 (flow_3201-4000.txt,
   SPRxx - LOAD05):
   - captive-sire share falls by 0.055 to 0.174 as alarmSpread rises (SPR01 to SPR05);
   - feral by 0.108 to 0.424;
   - depth rises by 1.28 to 6.52;
   - losses to the wild change by +0.024 (SE 0.007) at SPR01, by -0.001 and +0.004 at SPR03 and SPR02, and by +0.033
     (SE 0.048) at SPR05.
   The high flow beside REF goes with the fixed load: among the arms with established herds, LOAD05 is the most open
   on csire and feral. Spreading moves
   each measure toward REF, but stops well short of it.
5. **Timing.**
   - REF closes between the first and second windows: csire 0.294 to 0.091, depth 3.30 to 12.86, feral 0.451 to 0.240.
   - At SPR02 and SPR03, csire falls less (0.368, 0.220, 0.214 and 0.344, 0.215, 0.171), and feral rises over the same
     step.
6. **Small herds.** Where a herd is under 60 goats, its rates are per goat of a small herd that captures keep turning
   over, and are not comparable with an established herd's:
   - 401-900: SPR03 51.8, SPR05 13.7, SPR10 7.0;
   - SPR10 throughout (8.8 and 11.8 later), with captures 0.432-0.575 per herd goat-year.
   SPR05's means include the never-established seed 6, so its 3201-4000 csire here (0.159, all seeds) differs from the
   scored 0.123 (established seeds).
7. **Captured bucks breed more often with spreading.** First breedings per captured buck in 3201-4000 are 0.089-0.116
   at SPR01-SPR05, against REF9's 0.060.
Not read here: the wild's trait trajectories, and what makes REF's wild spring back.

## exp017 gene flow (descriptive), correction 2026-11-24 (the reviewer's bc24350)
The tables above stand. This replaces readings 1-7. The flow files are unchanged.

**Established seeds.** flow_tab's arm means are over all 8 seeds. SPR05's seed 6 never established (herd 23.0 in
3201-4000), and it carries SPR05's all-seed means. New tool, tools/flow_est.py (1a3877f): per arm, the mean and
min-max of flow_tab's per-seed values over the seeds established by the window's start. Established means jump_tab's
J at or before the start, taken from scored.txt. Commands:
`python tools/flow_est.py results/exp017_alarm-spread/flow_W.txt results/exp017_alarm-spread/scored.txt LOAD05,SPR01,SPR02,SPR03,SPR05,REF9 herd,capt,csire,cdam,depth,esc,feral,hout,bredF,bredM --alias REF9=REF`
for W = 3201-4000 and 901-1600 (flow_est_W.txt). Checks:
- each arm's all-seed mean equals flow_tab's printed mean, to its precision;
- at 3201-4000, the seeds with a J equal the scored est column;
- --bad jcol (the span column read as J) stops.
Its means are of the per-seed values flow_tab prints to three places, so they can differ from flow_tab's arm means in
the last place (REF cdam 0.033 here, 0.032 in flow_tab).
- In 3201-4000, every seed of LOAD05, SPR01-SPR03 and REF is established, as are 7 of SPR05's 8 (all but seed 6).
- In 901-1600, all seeds of LOAD05, SPR01 and SPR02 are established at 901, but only 3 of SPR03's (seeds 3, 5, 6), none
  of SPR05's (J 1080-2724), and 7 of REF's (seed 1's J is 957).
- No seed of any arm is established at 401 (every J is 501 or later), so 401-900 is the forming phase everywhere.

**Readings** (descriptive; 3201-4000 unless named; ranges are per-seed min-max over established seeds):
1. **SPR05, the only level with REF-like selection (R gap -0.591 against REF's -0.636), against REF:**
   - The herd takes in and loses goats at about REF's rates. The ranges overlap:
     - captures 0.023-0.034 against 0.024-0.028;
     - losses to the wild 0.085-0.138 against 0.070-0.101;
     - lineage depth 10.36-14.34 against 12.52-15.84 generations.
   - It stays more open on how often captured goats breed. Every established seed is above REF's highest:
     - captive-sire share 0.092-0.138 against 0.048-0.078;
     - captive-dam share 0.045-0.060 against 0.025-0.042;
     - first breedings per captured doe 0.462-0.511 against 0.316-0.420.
     Per captured buck, 0.077-0.106 against 0.044-0.078 overlaps at one end.
   - The wild's herd-born share is 0.341-0.435 against 0.102-0.175.
   So at SPR05, the extra gene flow beside REF is in how often captives breed, not in how many goats move.
2. **SPR01-SPR03 against REF.** These are more open than REF on every flow measure except hout:
   - captures 0.045, 0.038, 0.036 against 0.026;
   - losses 0.145, 0.126, 0.121 against 0.082;
   - captive-sire share 0.277, 0.214, 0.171 against 0.064;
   - captive-dam share 0.113, 0.083, 0.071 against 0.032;
   - depth 5.23, 7.37, 8.98 against 14.69.
   hout is 0.001 in every established arm.
3. **Against LOAD05** (paired over the same seeds, SPRxx - LOAD05, at SPR01-SPR03; flow_3201-4000.txt).
   - These move toward REF as alarmSpread rises: the captive-sire share (-0.055, -0.119, -0.162), the captive-dam share
     (-0.009, -0.039, -0.051), feral (-0.108, -0.232, -0.332), depth (+1.28, +3.42, +5.03), first breedings per
     captured doe (-0.064, -0.086, -0.117) and per captured buck (-0.020, -0.021, -0.033).
   - Losses do not move toward REF: SPR01 +0.024 (SE 0.007) is away from REF, and SPR02 +0.004 and SPR03 -0.001 are no
     change. Captures at SPR01 are +0.003 (SE 0.002).
   - SPR05's pairs include seed 6 and are not read. On every one of these measures, its established seeds' range lies
     beyond LOAD05's range, on REF's side.
   So the high sire and dam shares, the high captive breeding rates (LOAD05 bredM 0.121, bredF 0.635, the highest of
   the established arms), the shallow depth and the high feral go with the fixed load, and spreading lowers each
   toward REF. The losses to the wild do not go with the fixed load: LOAD05 loses 0.122 a herd goat-year, and
   spreading at SPR01-SPR03 leaves that unchanged or raises it.
4. **feral is a stock, not closure.**
   - The herd's losses differ much less between arms than feral does (LOAD05 0.122 against REF 0.082; feral 0.844
     against 0.128), so feral does not measure the herd's outflow.
   - What lowers it in REF is not checked.
   - Every arm's wild carries herd ancestry: anyh is 0.972-0.988 in every arm in 3201-4000.
   - REF's feral falls over the three windows (0.451, 0.240, 0.128), and the spreading levels' does not. That is a
     series in ancestry, not set beside the wild's R here.
5. **The herd-to-wild route.** Wild conceptions by herd sires per herd goat-year (hout) are 0.001 in every established
   arm, against losses to the wild of 0.082-0.145 (SPR05's established seeds 0.109). In the small herds of 401-900,
   hout is at most 0.017, against losses of about 0.4. The measured outflow is herd goats lost to the wild, not herd
   bucks mating wild does.
6. **Timing,** read at SPR02, whose herd in 401-900 (113.2) is near REF's (119.2):
   - SPR02's captive-sire share falls 0.368, 0.220, 0.214 over the three windows;
   - REF's falls 0.294, 0.091, 0.064 (0.088 over REF's 7 seeds established at 901).
   So REF's captive sires drop out of the herd's breeding by the second window, and SPR02's mostly do not. SPR03's
   401-900 herd (51.8) is small, and SPR05 is not established in 901-1600, so neither is read for timing.
7. **Small herds.** Where a herd is under 60 goats, its rates are per goat of a small herd that captures keep turning
   over:
   - 401-900: SPR03 51.8, SPR05 13.7, SPR10 7.0;
   - SPR10 throughout;
   - SPR05's seed 6 in 3201-4000.
   They are not compared with an established herd's.
Not read here: the wild's trait trajectories, and what makes REF's wild herd-born share fall.

## exp017 results (raw), note 2026-11-24: REF's source (the reviewer's bc24350)
The raw entry's "REF is exp005's (results/exp005_b0-pilot)" is wrong. REF's eight runs are exp005's seeds 1-4
(results/exp005_b0-pilot/REF_seed1-4) plus exp006's seeds 5-8 (results/exp006_two-corner/REF_seed5-8), as the scoring
command reads them. These are the same eight runs the scoring used, so no number changes. "Not exp007's" stands.

## exp017 gene flow: the wild's R by window (exploratory, 2026-11-24)
**Exploratory.** This was added after the gene-flow entry was read, at the steward's request, to test Chris's "in REF
wild moves with the herd at first but then springs back". Tool tools/wildr_tab.py (6ccb419), through cpuslot:
`python tools/wildr_tab.py "results/exp017_alarm-spread;results/exp010_fixed-load;results/exp005_b0-pilot;results/exp006_two-corner" results/exp017_alarm-spread/scored.txt LOAD05,SPR01,SPR02,SPR03,SPR05,SPR10,REF 401-900,901-1600,3201-4000 --perseed`
(results/exp017_alarm-spread/wildr.txt).
- **What it computes.** Per run and window, wild R and herd R are genotype means of R from tools/split_tab.py's split
  (histogram rows with herd and wild goats; the founders' value F plus the wild or herd change). feral is as
  flow_tab's. Established = J at or before the window's start, from scored.txt, as flow_est.
- **Checks:**
  - split's identity on every run;
  - at 3201-4000, each run's herd and wild change of R equals scored.txt's per-seed values to three places;
  - at 3201-4000, the seeds with a J equal the scored est column;
  - --bad allgoats and --bad jcol each stop (wildr_bad.txt).
- **Founders.** The founders' R (301-400) is 0.791 in every arm: the same seeds share their history to year 400.

| arm | window | established | wild R est | herd R est | feral est | wild R all | herd R all | feral all |
|---|---|---|---|---|---|---|---|---|
| LOAD05 | 401-900 | 0 of 8 | - | - | - | 0.710 | 0.668 | 0.684 |
| LOAD05 | 901-1600 | 8 of 8 | 0.651 (0.636-0.665) | 0.569 (0.525-0.613) | 0.845 (0.829-0.868) | 0.651 | 0.569 | 0.845 |
| LOAD05 | 3201-4000 | 8 of 8 | 0.661 (0.644-0.677) | 0.557 (0.509-0.587) | 0.844 (0.826-0.863) | 0.661 | 0.557 | 0.844 |
| SPR01 | 401-900 | 0 of 8 | - | - | - | 0.692 | 0.616 | 0.557 |
| SPR01 | 901-1600 | 8 of 8 | 0.610 (0.552-0.663) | 0.385 (0.358-0.422) | 0.764 (0.756-0.784) | 0.610 | 0.385 | 0.764 |
| SPR01 | 3201-4000 | 8 of 8 | 0.658 (0.637-0.679) | 0.344 (0.311-0.373) | 0.737 (0.718-0.754) | 0.658 | 0.344 | 0.737 |
| SPR02 | 401-900 | 0 of 8 | - | - | - | 0.724 | 0.570 | 0.509 |
| SPR02 | 901-1600 | 8 of 8 | 0.675 (0.650-0.703) | 0.240 (0.213-0.275) | 0.628 (0.595-0.684) | 0.675 | 0.240 | 0.628 |
| SPR02 | 3201-4000 | 8 of 8 | 0.681 (0.645-0.697) | 0.220 (0.202-0.230) | 0.612 (0.595-0.664) | 0.681 | 0.220 | 0.612 |
| SPR03 | 401-900 | 0 of 8 | - | - | - | 0.801 | 0.687 | 0.355 |
| SPR03 | 901-1600 | 3 of 8 | 0.699 (0.679-0.712) | 0.163 (0.158-0.167) | 0.522 (0.500-0.546) | 0.700 | 0.252 | 0.541 |
| SPR03 | 3201-4000 | 8 of 8 | 0.691 (0.681-0.700) | 0.167 (0.159-0.177) | 0.512 (0.469-0.541) | 0.691 | 0.167 | 0.512 |
| SPR05 | 401-900 | 0 of 8 | - | - | - | 0.843 | 0.800 | 0.257 |
| SPR05 | 901-1600 | 0 of 8 | - | - | - | 0.784 | 0.578 | 0.516 |
| SPR05 | 3201-4000 | 7 of 8 | 0.703 (0.690-0.719) | 0.112 (0.103-0.116) | 0.400 (0.341-0.435) | 0.717 | 0.193 | 0.420 |
| SPR10 | 401-900 | 0 of 8 | - | - | - | 0.855 | 0.827 | 0.181 |
| SPR10 | 901-1600 | 0 of 8 | - | - | - | 0.848 | 0.819 | 0.392 |
| SPR10 | 3201-4000 | 0 of 8 | - | - | - | 0.833 | 0.794 | 0.485 |
| REF | 401-900 | 0 of 8 | - | - | - | 0.743 | 0.529 | 0.451 |
| REF | 901-1600 | 7 of 8 | 0.722 (0.705-0.738) | 0.090 (0.068-0.111) | 0.221 (0.144-0.298) | 0.720 | 0.097 | 0.240 |
| REF | 3201-4000 | 8 of 8 | 0.712 (0.696-0.725) | 0.077 (0.067-0.101) | 0.128 (0.102-0.175) | 0.712 | 0.077 | 0.128 |

**Readings** (exploratory):
1. **At these windows, REF's wild does not spring back in R.**
   - REF's wild R is 0.743, 0.720 and 0.712 over the three windows (all seeds), each below the founders' 0.791.
   - Its fall slows, but it does not reverse.
   - A move and return inside 401-900 would not show in a 500-year mean, so this does not rule one out there.
2. **The return between the second and third windows is at SPR01.** Its wild R is 0.692, 0.610, 0.658 (all seeds
   established after 900). LOAD05 rises a little (0.651 to 0.661), and SPR02 less (0.675 to 0.681). SPR03 and REF do
   not rise.
3. **The wild ends near REF's at the levels with the strongest herd selection.** In 3201-4000, on established seeds,
   the wild's R is 0.703 at SPR05 and 0.691 at SPR03, against REF's 0.712. LOAD05 and SPR01 have the lowest wild R
   (0.661, 0.658).
4. **Wild R does not follow feral.** SPR05's wild R (0.703) is near REF's (0.712) with feral 0.400 against 0.128. So
   the wild's herd-born share is not what sets how far the wild's R falls.
5. **Small herds.** In 401-900, SPR03, SPR05 and SPR10 have small herds (51.8, 13.7, 7.0 in flow_401-900.txt), and
   their wild R is above the founders' (0.801, 0.843, 0.855). In those three arms the wild has not followed the herd
   down in that window.
Not read: R within 401-900 at a finer grain (a timeline, not window means), and any cause of the wild's fall or return.

## exp017 gene flow (descriptive), correction 2 2026-11-24 (the reviewer's 5ff5134)
This replaces reading 1 of the correction above (343280c) and the last sentences of its reading 6. It compared ranges,
so "about REF's rates" rested on one seed.

Seed counts come from `python tools/flow_est.py results/exp017_alarm-spread/flow_3201-4000.txt results/exp017_alarm-spread/scored.txt LOAD05,SPR01,SPR02,SPR03,SPR05,REF9 herd,capt,csire,cdam,depth,esc,feral,hout,bredF,bredM --alias REF9=REF --against REF9`
(f26a7af; flow_est_3201-4000.txt regenerated, with its means and ranges unchanged). They agree with the reviewer's
hand count from flow_tab's per-seed rows.

1. **SPR05 against REF, on its 7 established seeds (3201-4000).** The herd is more open than REF on the mean of every
   measure except hout (0.001 in both).
   - **Captures, losses and depth** lie between REF and the fixed load (SPR05's established mean; REF's range; LOAD05's
     mean):
     - captures 0.031, against 0.024-0.028 and 0.042;
     - losses to the wild 0.109, against 0.070-0.101 and 0.122;
     - depth 11.80, against 12.52-15.84 and 3.95.

     Seed by seed against REF's range: captures, 6 above and 1 below (s7); losses, 5 above and 2 inside (s4, s7);
     depth, 6 below and 1 inside (s7). Seed 7 (J 1080) is the one REF-like seed on these.
   - **Captive breeding and the wild's herd-born share.** Every established seed is beyond REF's range:
     - captive-sire share 0.092-0.138 against 0.048-0.078;
     - captive-dam share 0.045-0.060 against 0.025-0.042;
     - first breedings per captured doe 0.462-0.511 against 0.316-0.420;
     - feral 0.341-0.435 against 0.102-0.175.

     Per captured buck, 6 seeds are above and 1 inside (s8).

   For Chris: "At SPR05 the herd is more open than REF on every measure. On captures, losses and depth it lies between
   REF and the fixed load; on how often captives breed, and on the wild's herd-born share, every established seed is
   beyond REF's range (for breedings per captured buck, all but seed 8)."
6. **Timing** (replaces "So REF's captive sires drop out ... mostly do not"). SPR02's captive-sire share falls from
   0.368 to 0.220 and then holds at 0.214, while REF's keeps falling (0.294, 0.091, 0.064).

## exp017 gene flow: the wild's R in 100-year bins (exploratory, 2026-11-24)
**Exploratory.** This was added at the steward's request, because Chris's "springs back" came from the over-time plots,
which 500-year means cannot test. Its question: does REF's wild R fall and return within the first centuries of
herding?
Command, through cpuslot (tools/wildr_tab.py at 8dcebc8; results/exp017_alarm-spread/wildr_timeline.txt):
`python tools/wildr_tab.py "results/exp017_alarm-spread;results/exp010_fixed-load;results/exp005_b0-pilot;results/exp006_two-corner" results/exp017_alarm-spread/scored.txt LOAD05,SPR01,SPR02,SPR03,SPR05,REF --timeline --perseed`
- **Bins:** 401-500 ... 1501-1600, then 3201-4000. Histogram rows fall every 15 years, so a bin holds 6 or 7.
- **Checks:** split's identity on every run, and the 3201-4000 checks against scored.txt, as before. --bad allgoats and
  --bad jcol stop (wildr_timeline_bad.txt). The window mode's output is byte-identical to wildr.txt.
- **Founders' R** (301-400): 0.791 (0.770-0.802 over seeds) in every arm.
- **wildr_timeline.txt** has each arm's per-bin min-max over seeds, and each seed's wild R by bin with its lowest bin
  over 401-1600.

All-seed means, wild R / herd R (established at the bin's start)
| years | LOAD05 | SPR01 | SPR02 | SPR03 | SPR05 | REF |
|---|---|---|---|---|---|---|
| 401-500 | 0.827 / 0.801 (0) | 0.829 / 0.788 (0) | 0.840 / 0.788 (0) | 0.846 / 0.812 (0) | 0.846 / 0.815 (0) | 0.836 / 0.784 (0) |
| 501-600 | 0.736 / 0.700 (2) | 0.765 / 0.714 (0) | 0.779 / 0.666 (0) | 0.838 / 0.786 (0) | 0.851 / 0.812 (0) | 0.796 / 0.698 (0) |
| 601-700 | 0.681 / 0.641 (7) | 0.676 / 0.621 (3) | 0.709 / 0.564 (1) | 0.809 / 0.709 (0) | 0.851 / 0.820 (0) | 0.731 / 0.544 (1) |
| 701-800 | 0.655 / 0.608 (8) | 0.606 / 0.509 (6) | 0.655 / 0.466 (4) | 0.770 / 0.618 (1) | 0.842 / 0.790 (0) | 0.670 / 0.372 (2) |
| 801-900 | 0.647 / 0.586 (8) | 0.585 / 0.447 (7) | 0.635 / 0.370 (5) | 0.745 / 0.521 (2) | 0.829 / 0.767 (0) | 0.682 / 0.254 (6) |
| 901-1000 | 0.645 / 0.569 (8) | 0.586 / 0.419 (8) | 0.636 / 0.320 (8) | 0.730 / 0.405 (3) | 0.818 / 0.724 (0) | 0.703 / 0.173 (7) |
| 1001-1100 | 0.650 / 0.571 (8) | 0.590 / 0.394 (8) | 0.647 / 0.264 (8) | 0.699 / 0.307 (5) | 0.807 / 0.687 (0) | 0.721 / 0.120 (8) |
| 1101-1200 | 0.652 / 0.565 (8) | 0.608 / 0.382 (8) | 0.667 / 0.238 (8) | 0.704 / 0.248 (7) | 0.785 / 0.608 (1) | 0.731 / 0.087 (8) |
| 1201-1300 | 0.654 / 0.561 (8) | 0.615 / 0.380 (8) | 0.690 / 0.222 (8) | 0.710 / 0.220 (7) | 0.777 / 0.550 (2) | 0.732 / 0.074 (8) |
| 1301-1400 | 0.652 / 0.579 (8) | 0.622 / 0.374 (8) | 0.694 / 0.207 (8) | 0.694 / 0.221 (7) | 0.774 / 0.535 (2) | 0.720 / 0.074 (8) |
| 1401-1500 | 0.649 / 0.568 (8) | 0.621 / 0.383 (8) | 0.695 / 0.217 (8) | 0.683 / 0.190 (7) | 0.771 / 0.500 (3) | 0.712 / 0.075 (8) |
| 1501-1600 | 0.654 / 0.569 (8) | 0.630 / 0.365 (8) | 0.692 / 0.215 (8) | 0.682 / 0.176 (8) | 0.757 / 0.437 (3) | 0.716 / 0.079 (8) |
| 3201-4000 | 0.661 / 0.557 (8) | 0.658 / 0.344 (8) | 0.681 / 0.220 (8) | 0.691 / 0.167 (8) | 0.717 / 0.193 (7) | 0.712 / 0.077 (8) |

**Readings** (exploratory):
1. **REF's wild R falls and springs back within the first centuries of herding.** This revises reading 1 of the window
   section above (a2eb2d6): the 500-year means averaged the dip away.
   - **All-seed mean:** 0.836 in 401-500, down to 0.670 in 701-800, back to 0.732 in 1201-1300, then 0.712-0.720 to
     1600 and 0.712 in 3201-4000.
   - **Seed by seed** (per-seed lines in wildr_timeline.txt), every REF seed's lowest bin is the one holding its J or
     the next:
     - s1: J 957, low 0.647 in 901-1000;
     - s2: J 849, low 0.650 in 901-1000;
     - s3: J 705, low 0.581 in 701-800;
     - s4: J 717, low 0.646 in 701-800;
     - s5: J 783, low 0.621 in 801-900;
     - s6: J 588, low 0.640 in 601-700;
     - s7: J 705, low 0.569 in 701-800;
     - s8: J 663, low 0.691 in 701-800.

     In each seed the later bins are higher than the low.
   - Over the same years REF's herd R falls without returning: 0.784, then 0.074 by 1201-1300.
2. **The fixed load (LOAD05): no spring-back.** Its wild R falls to 0.655 by 701-800, then stays at 0.645-0.654 through
   1600 (0.661 in 3201-4000).
3. **SPR01: deeper, and a slow, partial return.**
   - The mean falls to 0.585 (801-900) and returns to 0.630 by 1501-1600 and 0.658 in 3201-4000.
   - Per-seed lows are 0.511-0.588, against REF's 0.569-0.691.
   - SPR01's s7 stays at 0.521-0.572 from 601-700 through 1501-1600.
4. **SPR02: a dip and return like REF's, from a lower floor.** The mean falls to 0.635 (801-900) and returns to 0.695
   (1401-1500). Per-seed lows are 0.515-0.614.
5. **SPR03 and SPR05:** the herds form late, and the wild's R falls slowly through 1600 (SPR03 0.846 to 0.682, SPR05
   0.846 to 0.757). Their bin means mix seeds before and after establishment (the counts in brackets), so they are not
   read for a return.
6. **First century.** In 401-500, every arm's wild R (0.827-0.846) is above the founders' 0.791. Why is not checked.

For Chris: in REF, the wild's R moves down with the herd's as each herd establishes, and returns within the next few
centuries while the herd's keeps falling. At the fixed load without spreading it does not return. With spreading at 0.1
it falls further and returns slowly and only partly by 1600; at 0.2 it dips and returns, as in REF, from a lower
floor. What drives the return is not checked.

## exp017 gene flow: the wild's R by window, correction 2026-11-24 (the reviewer's 54f3c87)
This replaces readings 1-5 of "the wild's R by window" (a2eb2d6); its table stands. The tools changed in 670a57e: the
check of scored.txt's J column against its est column now runs whenever scored.txt is read, before any output. All
outputs are byte-identical, and wildr_bad.txt and wildr_timeline_bad.txt were regenerated: --bad jcol now stops before
printing.
1. **REF at window means, and what that does not test.**
   - REF's all-seed wild R is 0.743, 0.720 and 0.712 over the three windows, each below the founders' 0.791.
   - Per seed (wildr.txt, per run), part of REF does rise:
     - seeds 3, 6 and 7 rise from 401-900 to 901-1600 (0.692 to 0.705, 0.727 to 0.736, 0.708 to 0.724), three of the
       four lowest in 401-900;
     - seeds 2 and 5 rise from 901-1600 to 3201-4000 (0.709 to 0.713, 0.710 to 0.725).
   - 1601-3200 is not sampled.
   - This R is the wild-only genotype mean, the R gap's own measure. The year records' traitMeans is a mean over all
     goats, herd and wild (src/datamanager.js:144). Which series and plot Chris described is not identified; the
     reviewer has asked the steward to ask him.
   - At 100-year bins over 401-1600, the same wild R falls and returns in REF, in every seed: see "the wild's R in
     100-year bins" (003bf80), which is still with the reviewer.
2. **SPR01** (all seeds established by 901): wild R is 0.692, 0.610, 0.658. The rise from the second window to the
   third is a difference of two window means with 1601-3200 unread, not a trajectory. Over 901-1600 the 100-year bins
   rise from 0.586 to 0.630 (003bf80).
3. **Across arms, wild R against the wild's herd-born share** (replaces readings 3 and 4). In 3201-4000, on established
   seeds:

   | | LOAD05 | SPR01 | SPR02 | SPR03 | SPR05 | REF |
   |---|---|---|---|---|---|---|
   | feral | 0.844 | 0.737 | 0.612 | 0.512 | 0.400 | 0.128 |
   | wild R | 0.661 | 0.658 | 0.681 | 0.691 | 0.703 | 0.712 |
   | herd R | 0.557 | 0.344 | 0.220 | 0.167 | 0.112 | 0.077 |

   - Across arms, the wild's R is higher where its herd-born share is lower at every step except LOAD05 to SPR01.
   - Between SPR05 and REF, the share is 0.400 against 0.128, while wild R differs by 0.009. So the relation is not
     proportional.
   - The R that herd-born goats carry into the wild is that of the herd they left. The herd's R differs between arms
     (0.557 to 0.077), and that is not read.
4. **The first window** (replaces reading 5). In 401-900, against the founders' R (0.791):
   - at SPR05 and SPR10, neither the herd (0.800, 0.827) nor the wild (0.843, 0.855) is below it;
   - at SPR03 the wild is above it (0.801) and the herd below it (0.687).
   SPR10's wild stays above the founders' throughout (0.855, 0.848, 0.833). Why the wild rises above the founders is
   not checked.

For Chris (replacing the window section's message): the wild R that the R gap is measured on does not return at window
means, and three of eight REF seeds rise from the first window to the second. At 100-year bins it falls and returns in
every REF seed (003bf80, pending review). Which plot he meant is being asked.

## exp017 gene flow: the wild's R in 100-year bins, correction 2026-11-24 (the reviewer's 497d6ea)
This replaces readings 1-6 and the line for Chris in "the wild's R in 100-year bins" (003bf80); its table stands.
The tool now prints, per arm, the pre-herding all-goat R by bin, and per seed, the bin holding J, how many bins after
it the low comes, and the highest of the next three bins after the low (7a34b65). The tool stops if a herd goat falls
in a pre-herding bin; --bad prebin stops (wildr_timeline_bad.txt). The window mode's output is byte-identical.
Command as before; wildr_timeline.txt is regenerated, with its earlier table rows unchanged.
1. **REF against LOAD05, per seed** (wildr_timeline.txt, per-seed lines; replaces "in each seed the later bins are
   higher than the low", which is true of any minimum):
   - **REF:** each seed's low comes in J's bin or the next (0 or 1 bins after it, 8 of 8). The highest of the next
     three bins is 0.054-0.159 above the low.
   - **LOAD05:** the low comes 3-9 bins after J's bin. The next three bins rise 0.018-0.041 above it.
   - Within a seed, changes under about 0.04 are plateau noise (LOAD05 s1 runs 0.634-0.675 over 901-1600), so REF's
     drift from 0.732 to 0.712 after 1300 is not read.
2. **The return is partial.**
   - REF's mean returns to 0.732 (1201-1300), against 0.836 in 401-500.
   - In every REF seed, 3201-4000 is below 401-500 (for example s3 0.789 to 0.696, s7 0.844 to 0.711).
   - What differs between arms is how soon after J the recovery comes, and how large it is.
3. **The fixed load:** LOAD05 falls to a plateau and stays (lows 0.614-0.650, scattered over 801-1500).
4. **Spreading, per seed** (the bin means mix seeds before and after J until 901, so they are not read):
   - **SPR01:** the low comes 1-3 bins after J's bin, at 0.511-0.588, against REF's 0.569-0.691. The next three bins
     rise 0.018-0.104. In 4 of 8 seeds (s1, s4, s5, s7) the rise is 0.035 or less.
   - **SPR02:** the low comes 0-3 bins after J's bin, at 0.515-0.614. The next three bins rise 0.089-0.159, as in REF.
   - SPR03 and SPR05 are not read for a return: several seeds' J is late or outside 401-1600, or no bin follows the low.
5. **Hunting sets the baseline, and is the unchecked candidate.** Humans hunt from year 300 (humansAt 300, herdingAt
   400 in every arm). Before herding, every goat's R is:
   - 0.696 in 101-200 and 0.678 in 201-300, with no humans;
   - 0.762 in 301-350 and 0.819 in 351-400, under hunting.

   So the founders' window (0.791) is the wild's first hunted century, with R still rising. Every arm's 401-500 wild R
   (0.827-0.846) comes before any seed's J. The level the wild recovers toward may be set by hunting, and that is not
   checked.

   No run on this code has humans and no herding: exp013's WTlate has no humans, and REFlate hunts for 100 years
   before herding at 3000. The old ladder's WT2 (humans hunting from 300, never herding; pre-protocol code, EXPLOG
   "WT2" rows) held whole-population R near 0.82-0.83. That is a pointer from older code, not a reading here.

For Chris (replacing 003bf80's): in REF the wild's R falls with each herd's establishment and recovers part of the way
within two or three centuries, while the herd's keeps falling. At the fixed load without spreading it falls to a
plateau and stays. With spreading at 0.1 the dip is deeper, and in half the seeds it recovers little within three
centuries. At 0.2 the dip and recovery are like REF's, a little later. Hunting from year 300 was still raising the
wild's R when herding began, so the level it recovers toward may be hunting's. What drives the recovery is not checked.
Which plot Chris meant is still being asked.

## exp017 gene flow: the wild's R, note 2026-11-24 (the plot; the reviewer's 99dfa13)
- **The plot is identified.** Every REF plot with a wild line that Chris has seen (rtime_LOAD1_REF.png,
  takeoff_rdist_REF.png) comes from tools/takeoff_rdist.py. Its wild line is the wild-only mean, hist - histHerd at
  bucket midpoints (lines 9, 27-31): split's wild measure, the series wildr_tab reads. The steward found this and the
  reviewer checked it in the code. This replaces "which plot Chris meant is still being asked" in both corrections
  above.
- **The window correction (d9ab94b).** "Falls and returns in every REF seed", in reading 1 and in the line for Chris,
  should read "falls and recovers part of the way in every REF seed" (as reading 2 of the timeline correction, f15e544).
- **Hunting.** Stalk hunting from year 300 is the unchecked candidate for two things: the wild's rise above the
  founders' R in 401-500 (every arm 0.827-0.846, against 0.791, before any J), and the level it recovers toward
  (f15e544, reading 5).

## exp017 gene flow: the wild's R, note 2 2026-11-24 (the reviewer's 947dec7; wording, no number changes)
All three pieces are settled: gene flow (598a467), the window entry (99dfa13) and the timeline (947dec7).
- **SPR01's four small rises** (0.018-0.035; s1, s4, s5, s7) lie inside LOAD05's plateau range (0.018-0.041), so
  "recovers little" means no more than the fixed load's noise. LOAD05 s4's +0.018 is over one bin only (its low is in
  1401-1500).
- **By 3201-4000, SPR01's wild sits at the fixed load's level:** 0.637-0.679 against LOAD05's 0.644-0.677 (established
  seeds, wildr.txt).
- **f15e544 reading 5's heading** becomes "Hunting raises the wild's R before herding; whether it sets the level of
  recovery is not checked".
- "Which plot Chris meant is still being asked" is out of date in both corrections (note above, eb14d37).

**For Chris, the settled line** (replaces the earlier ones):
- In REF, the wild's R falls with each herd's establishment and recovers part of the way within two or three
  centuries, while the herd's keeps falling.
- At the fixed load without spreading, it falls to a plateau and stays.
- With spreading at 0.1, the dip is deeper. In half the seeds the recovery is no more than the fixed load's noise, and
  by 3201-4000 it sits at the fixed load's level.
- At 0.2, the dip and recovery are like REF's, a little later.
- Hunting from year 300 was still raising the wild's R when herding began. Whether it sets the level of recovery is
  not checked, and neither is what drives the recovery.
- These are the series Chris saw: the wild-only line in the takeoff_rdist plots.

## exp017 gene flow: the wild's R, note 3 2026-11-24 (the reviewer; wording, no number changes)
In note 2's line for Chris, "In half the seeds the recovery is no more than the fixed load's noise" reads "In half the
seeds the recovery within three centuries is no more than the fixed load's noise". Some of those seeds rise later: s1
goes from 0.567 in 1501-1600 to 0.654 in 3201-4000 (wildr_timeline.txt, per-seed line).

## exp018 — Goats per cell, wild and herd, in established and non-established herds; and hunting without herding (HUNT) as the standing control
**Pre-registered:** 2026-11-24. Chris: "hunting without herding should be a default control run. how many goats are there
per grid cell in wild vs herds in both established and non-established herds?" and, on why: "i'm wondering if we make
spook chance increase with other goats nearby so this is not a herd only rule".
Mongo animalDomestication.exp018_density-hunt (mint); results/exp018_density-hunt; job list tools/exp018.jsonl (32 runs,
cpuslot --anywhere); code HEAD at queueing (named in the raw entry). exp019 was claimed in the registry by a mistaken
second --register call (question "x"); no heading is added for it, so runyears.mjs refuses it and no run uses it.
**Why:** every spook rule so far acts on herd goats only (the herder's spook, its load, alarmSpread's cascade within a
herd). Chris is weighing a rule in which the spook chance rises with the goats nearby, for wild and herd goats alike.
Sizing it needs how crowded each kind of goat lives, which no record holds: the sim keeps per-cell counts (goatCount,
wildCount) but never saves them. Herd goats graze within keepRadius 2 of the herder and are pulled toward him
(grazeMove), so a herd sits in at most 25 cells; wild goats spread over the 80 × 50 map. HUNT is the control Chris asked
to make standard: the reference culture with hunting from humansAt 300 and no herding, so no captures and no herd. It also
answers the open question from exp017's wild-R timeline: whether hunting, not the herd, sets the level the wild's R
recovers to.
**The counter** (src, this commit; output only, no random draws): at the middle day sub-tick (s = daySteps >> 1, after
that sub-tick's index rebuild) every living goat is sampled once a day, as wild (herd < 0) or herd (herd >= 0, loose
run-offs included). Per year and class, the record's density field gives: n (goat-samples), own (mean goats of its own
kind in its cell, itself included, so a lone goat scores 1), all (mean goats of either kind in its cell), perCell (goats
per cell holding its kind), own9 and all9 (the same two over its 3×3 neighbourhood, the alarmSpread window).
**Identity:** a 700-year probe at this code (SPR05's arguments, seed 1, recordEvery 3) against exp017's SPR05_seed1,
tools/cmp_years.py: result in the raw entry, before queueing. Each rerun arm is also checked against its original record
(REF: exp005 s1-4, exp006 s5-8; SPR05, SPR10: exp017): 0 records differing on shared keys, hist and histHerd identical.
If REF does not reproduce, the code drift since exp005 is reported and this batch's REF is the one read.
**Arms** (seeds 1-8, 4000 years): HUNT (REF's arguments with herdingAt 1e9); REF (exp006's REF arguments, herding at
400); SPR05 and SPR10 (exp017's arguments: herdPerHerder 1e9, minLoad 0.5, alarmSpread 0.5 and 1). REF and SPR05 give
established herds (8 and 7 of 8 in exp017's scoring); SPR05's seeds all waited first, so they give the small state and
the established state within the same runs; SPR10 never established (herd 11.8).
**Measure** (the analysis session, with a committed tool built and checked on the identity probe before any result):
per arm and seed, wild and herd own, all, perCell, own9, all9, averaged over the year rows (weighted by n) in each state:
- established: 3201-4000 in seeds with herd >= 100 over that window;
- small: years after 500 in which the 100-year herd mean is under 60 (load_tab's waited state), each seed's years pooled;
- HUNT: 3201-4000, and 301-400 (humans' first century) for all arms as the pre-herding baseline.
Arm means with the seed range. Also HUNT's wild R by 100-year bins (tools/wildr_tab.py --timeline) beside REF's wild-only R.
**Predictions** (mine):
1. Herd goats live more crowded than wild goats: herd own > wild own, and herd own9 > wild own9, in every arm-state
   with a herd, in every seed.
2. Established herds are more crowded than small ones: in SPR05, herd own over the established state exceeds herd own over
   the small state in every established seed.
3. The herd does not change how crowded wild goats live: in REF, SPR05 and SPR10 over 3201-4000, wild own is within 25% of
   HUNT's.
4. HUNT's wild R over 3201-4000 is above REF's wild-only R in 6 or more of 8 seeds.
**Decision rule:** descriptive. The density table goes to Chris to size a nearby-goats spook rule; no rule is chosen from
this batch alone. Prediction 4 settles exp017's open question only as a reading: if it holds, the wild's lower R in REF is
the herd's doing, not hunting's.
**Standing control (from this batch):** HUNT seeds 1-8 is the default control. A batch on code that can change goats,
wolves or hunting includes it, unless a 700-year HUNT seed 1 probe at that code reproduces the last HUNT record (0 records
differing), in which case that HUNT is cited.

## exp018 amendment, 2026-11-24 (before any run started: 0 of 32 queued; the reviewer's prereg review, d11cab6)
notes/review/2026-11-24-exp018-prereg.md, points 1-5 taken in full, 6 and 7 as below. Where this differs from the entry,
this governs.
- **The counter is split (point 1; output only, this commit).** The herd class mixed goats out with the herder with
  goats kept at camp (sheltered kids under shelterAge, tethered goats with R × fearOfHumans >= captureFear 0.35), which
  sit on the camp cell. density is now {c, cells}: c holds four classes, [wild, with herder (walksWithHerder: the goats a
  herder can spook), kept at camp (sheltered, tethered or guarded), other herd (kids following a mother, loose run-offs,
  captives being led)], each {n, own, all, own9, all9}. own counts wild goats for the wild class and herd goats of any
  class otherwise. cells = occupied cell-samples [wild, herd], so perCell is read for wild and for the herd as a whole
  only. The entry's "a herd sits in at most 25 cells" is wrong: the 25 cells are the keepRadius 2 box around the herder,
  and they hold only the with-herder class.
- **Seen before queueing:** a 30-year smoke run at default arguments (herdingAt 5, humansAt 2, seed 1;
  results/_scratch, DENsmoke), read only to check that the field is written. In it, the with-herder class's own equalled
  its own9 in every printed row. Nothing is read from this run.
- **Identity:** the 700-year probe is rerun on this code. The result goes in the raw entry, before queueing.
- **States (point 3).**
  - Established: load_tab's rule as exp017 scored it, the mean of the year rows' herded over 3201-4000 >= 100. The state
    is read over 3201-4000.
  - Small: rows after year 500 and before the seed's J (load_tab's J, jump_tab.jump at >= 100 from 400; to 4000 if no
    J), whose own herded is under 60. Not the trailing mean, and not load_tab's waited state.
  - Floor: a seed-state is read only with 10 or more such rows, each with a with-herder goat-sample. Otherwise it is
    "not read".
  - Baseline: year indices 300-399 (labels 301-400; herding begins at index 400, label 401). It is one run per seed,
    printed once, not four arms.
- **Predictions 1-2** are read on the with-herder class, with the kept class's share of herd goat-samples printed
  beside. Prediction 1 is a mechanism check, true nearly by construction (keepRadius 2 around one person), as exp017's
  P1 was.
- **Prediction 3 (point 4)**, replaced: in each of REF, SPR05 and SPR10, the arm mean of wild own over 3201-4000 lies
  inside HUNT's per-seed range over the same window. Beside it, printed and not part of the prediction: wild all, own9
  and all9, the wild population (wild n / 360 sample days), and wildNearCamp.
- **Prediction 4 (point 2)**, replaced. HUNT's wild R is the all-goat R from hist over 3201-4000. The tool stops if
  any HUNT row has a non-empty histHerd. REF's is the wild-only R (hist − histHerd) from this batch's REF reruns.
  Prediction: at least 6 of HUNT's 8 per-seed values lie above REF's median per-seed value, and the arm means differ by
  more than 0.04 (exp017's within-seed plateau drift). A difference of 0.04 or less is "not read". Printed beside it:
  huntTries over 301-400 and 3201-4000, and the wild population.
- **Reading, replacing the entry's last sentence:** if prediction 4 holds, the wild's R under REF sits below its level
  under hunting alone. The difference is herding's doing, which includes its gene flow, captures, and one person per camp
  moved from hunting to herding. This batch does not separate them.
- **Standing control (point 5)**, replacing the entry's paragraph. Every batch includes HUNT seeds 1-8, unless the
  check passes. The check: one 4000-year HUNT seed 1 run at the batch's code reproduces the last HUNT seed 1 record on
  every year row (0 differing on shared keys, hist identical). If any base argument HUNT carries changes, HUNT reruns at
  the new base. Each registration that includes HUNT names what it reads against it: by default the wild R (3201-4000
  and its timeline), the wild population, and huntTries. Otherwise it says "available, not read". When HUNT is cited
  instead of rerun, the raw entry names its experiment, run and code commit, and the check's result.
- **Checks (points 6, 7).**
  - The four arms of each seed agree on every shared key in the year rows before index 400 (tools/cmp_years.py on those
    rows). A failure stops the reading.
  - SPR05 and SPR10 must reproduce exp017's records (they differ from it only by the counter). If either does not, the
    counter is not output only: stop.
  - If REF does not reproduce exp005/006, the drift is reported, and exp010's and exp017's comparisons against
    exp005/006's REF are flagged.
- **The tables** state their scope:
  - own − 1 is "other goats nearby".
  - Midday only, so dawn and night crowding is not measured.
  - The 1×1 and 3×3 windows are what the counter gives. The rule's radius is not chosen (the sim senses company over
    socialRange 4).
  - The 3×3 is clipped at the map edge.

## exp018 clarification, 2026-11-24 (before any run queued; the reviewer's 940b5fe, which settles the amendment)
- **Prediction 2** is printed with the with-herder goats per sample day (n / 360) beside own. If with-herder own is
  about that head count (the herd standing on the herder's cell), P2 is read as a mechanism check, like P1.
- **The other-herd class** also holds herd goats whose camp has no herder that day.
- **J for the small state** is load_tab's, as it computes it: the series after 500, with a 400-year hold.

## exp018 note, 2026-11-24: the identity probe (before queueing)
At the split counter (src as committed in 20db6e8; the probe ran from the working tree at d11cab6 with that change, id
commit v0.1.0-328-gd11cab6-dirty), with SPR05's arguments, seed 1, 700 years, and recordEvery 3, histPeriod 15,
reportingPeriod 1080 (results/_scratch/exp054_probe/DENid_seed1.json). Against exp017's SPR05_seed1, tools/cmp_years.py:
233 records compared, 76 shared keys, 0 differ; density only in the probe. hist and histHerd are identical over the 46
shared histogram rows, all 12 traits. The saved parameters are identical apart from id. The counter is output only over
these years. Queued next.

## exp018 note, 2026-11-24: prediction 1 on the probe (seen before results; no amendment)
The analysis session ran tools/density_tab.py (9c9e008) on the identity probe (exp054_probe/DENid_seed1, which is
exp017's SPR05_seed1 over its first 700 years; --late 601-700). Seed 1 has no J there, so every state row is small (67
rows). With-herder own 5.517 against wild own 1.952 holds. With-herder own9 5.519 against wild own9 6.699 fails: the herd
stands on one cell, and wild goats in a 3×3 outnumber a herd of about 6. Prediction 1 stands as registered and is scored
so. These numbers are data seen before results, not a batch reading.

## exp018 results (raw)
32 of 32 runs are complete (complete: true, last row year 3998). Every run exited 0 (cpuslot-logs/, batch
1795543753431140600), with no error, exception or warning in any log. Each log carries the db client's packet-size
advisory (over its 4 MB suggestion), which does not stop the save.
- Arms as registered, 8 seeds each: HUNT, REF, SPR05, SPR10.
- Parameters are identical across runs except id, seed, herdingAt (HUNT 1e9), and herdPerHerder, minLoad and
  alarmSpread (SPR arms).
- Hosts: 23 on the desktop, 9 on mint. Run times 2065-11923 s.
**Commits:**
- 477caad: 6 runs. a6f13b4: 1 run. 70758bf: 25 runs.
- All three are clean. `git diff 477caad 70758bf` over src, tools/runyears.mjs and load.mjs is empty: the commits
  between them touched EXPLOG and notes/review only.
**Identity checks (registered; tools/cmp_years.py and a direct comparison of hist, histHerd and histYears):**
- SPR05 and SPR10, s1-8, against exp017: 1333 of 1333 records compared, 76 shared keys, 0 differ; density only in
  exp018. hist, histHerd and histYears are identical (266 rows).
- REF s1-4 against exp005 and s5-8 against exp006: 1333 of 1333 records compared, 65 shared keys, 0 differ. hist,
  histHerd and histYears are identical (266 rows).
- REF reproduces at this code, so no drift is flagged. The counter is output only over the full 4000 years.
- The four-arms-agree check before index 400 is the analysis tool's, and its result goes in the scored entry.
**For the scored entry (the reviewer's 383e23d):** SPR05_seed1's small-state rows over its first 700 years were seen
before results, in the identity probe (note a6f13b4). P1's own9 half in SPR05's small state is therefore close to
decided by data seen beforehand. Only s1's small rows after year 700, up to its J, could change it. Say so beside P1.

## exp018 results (scored)
Through cpuslot, tools at 361944d (density_tab.py) and 9c9e008 (wildr_tab.py), scored to the entry as amended (20db6e8)
and clarified (513c1bc):
- `python tools/density_tab.py results/exp018_density-hunt HUNT,REF,SPR05,SPR10 --perseed` (density.txt);
- `python tools/wildr_tab.py results/exp018_density-hunt - HUNT,REF --timeline --perseed` (wildr_timeline.txt);
- `python tools/wildr_tab.py results/exp018_density-hunt - HUNT,REF 3201-4000 --pair HUNT,REF --perseed` (wildr_pair.txt).
Tables in results/exp018_density-hunt/. '-' means no SCORED.txt: J is computed as load_tab computes it.
**Checks:**
- The four arms agree on every shared key of every year row before index 400, per seed (24 arm pairs). On the probe this
  check stopped on a planted births+1 at year 201.
- Every row's density field passed the tool's checks (bounds, cells against samples, own >= perCell, no herd sample
  before herdingAt or in HUNT). --bad swap, nopool and nohold each stop (bad_*.txt).
- P4's per-seed values in density_tab equal wildr_tab --pair's, seed for seed, to three places.
- One fix before this reading: the first output (density_v1.txt) dropped REF s6's small state without a word, because it
  has no row after 500 before J (588) with herded < 60. 361944d names it as not read. No other line changed.
- J and established match exp017's scoring: SPR05 established 7 of 8 (s6 not, herded 23.0 over 3201-4000), J
  1080-2724; REF 8 of 8; SPR10 0. HUNT has no herd goat in any row or histogram.

**Baseline** (301-400, every goat wild, one run per seed): wild own 1.950 (1.898-1.987), own9 6.608 (6.285-6.874),
perCell 1.468, 515.2 wild goats per sample day.

**Over 3201-4000** (mean over seeds, min-max), with herder / wild:
| arm | est | wild own | wild own9 | wild per day | with-herder own | with-herder per day | kept share (est) |
|---|---|---|---|---|---|---|---|
| HUNT | - | 1.871 (1.761-1.927) | 6.054 (5.325-6.449) | 580.4 | - | - | - |
| REF | 8 | 1.789 (1.689-1.874) | 5.580 (4.984-6.035) | 471.9 | 103.575 (99.227-111.220) | 260.2 | 0.041 |
| SPR05 | 7 | 1.840 (1.766-1.888) | 5.860 (5.417-6.194) | 474.8 | 85.623 (10.358-101.003) | 216.4 | 0.040 |
| SPR10 | 0 | 1.861 (1.781-1.928) | 5.999 (5.343-6.473) | 583.6 | 5.885 (4.581-7.245) | 10.9 | - |
SPR05's with-herder row is over all 8 seeds; over its 7 established seeds, own 96.375 (90.756-101.003), per day 244.2.
Small state, with-herder own: REF 18.049 (7 seeds), SPR05 12.134 (8), SPR10 5.478 (8); wild own 1.868-1.881 in all
three.

**Predictions:**
1. **Fails** (a mechanism check): 33 of 38 seed-states at the floor. REF s6's small state is not read (no row).
   - The own half holds in all 38 seed-states read. Every failure is on the own9 half, all in SPR10's small state, in
     seeds 1, 2, 5, 6 and 8. With-herder own9 there is 4.099-5.613, against wild own9 6.355-6.475.
   - SPR10's seeds 3, 4 and 7 pass narrowly (with-herder own9 6.642, 5.830, 5.955 against wild 5.620, 5.567, 5.515).
     Their wild own9 values are the arm's lowest.
   - **Seen before results (the reviewer's 383e23d):** SPR05_seed1's small-state rows over its first 700 years were
     seen in the identity probe (note a6f13b4). There the own9 half failed, 5.519 against 6.699 over 67 rows, so that
     half was close to decided beforehand. Only s1's small rows after 700, up to its J, could change it, and they did.
     Over its full small state (187 rows, to J 1164) s1 passes: with-herder own9 14.077 against wild 6.432. P1's
     failure is in SPR10, a run from which no row was seen before results.
   - Read: with-herder own9 exceeds own by 0.001-0.015 in every per-seed line for SPR05 and SPR10 (derived
     from printed values). The herd stands on one cell. A wild goat's 3×3 holds about six goats, so a herd of five
     standing on one cell has fewer goats around it in the 3×3 than a wild goat does. In SPR10 the herd stays that small.
   - Kept share of herd goat-samples: est 0.041 (REF), 0.040 (SPR05); small 0.043 (REF), 0.055 (SPR05), 0.077 (SPR10).
2. **Holds**, 7 of 7 established SPR05 seeds. With-herder own over est is 90.756-101.003 against 9.934-14.071 over small;
   with-herder goats per sample day are 232.3-254.0 against 13.3-28.7. By the clarification's test, est's own is not
   about the per-day head count: it is under half of it. The per-day figure counts every with-herder goat in the run,
   whatever its camp, and the number of herds is not printed. So whether own equals one herd's head count is not
   checked, and P2 is not read as a mechanism check on this evidence.
3. **Holds.** The arm mean of late wild own lies inside HUNT's per-seed range 1.761-1.927 in each of REF (1.789), SPR05
   (1.840) and SPR10 (1.861). Beside it, not part of the prediction:
   - wild own9: REF 5.580, SPR05 5.860, SPR10 5.999, HUNT 6.054;
   - wild goats per sample day: REF 471.9 and SPR05 474.8, against HUNT 580.4 and SPR10 583.6;
   - wildNearCamp: REF 8.6, SPR05 11.9, SPR10 38.9.
   The herd arms that establish carry about 105-110 fewer wild goats a day than HUNT (derived), and their wild goats are a
   little less crowded. That is within HUNT's seed range on own, the registered measure.
4. **Holds.** Wild R over 3201-4000: HUNT (all-goat R) 0.826-0.870, REF (wild-only R) 0.696-0.725. HUNT lies above REF's
   median 0.712 in 8 of 8 seeds, and above REF's same-numbered seed in 8 of 8 (wildr_tab --pair, descriptive). Arm means
   are 0.854 against 0.712 (+0.142, over the 0.04 band). Beside it:
   - huntTries over 301-400 are 357.6 in both arms; over 3201-4000, HUNT 279.4 (247.6-311.7), REF 206.6 (184.5-224.4);
   - wild population late: HUNT 580.4, REF 471.9.
   **Reading, as amended:** the wild's R under REF sits below its level under hunting alone. The difference is
   herding's doing, which includes its gene flow, its captures, and one person per camp moved from hunting to herding.
   This batch does not separate them. The last is visible beside the prediction: REF hunts about a quarter less than
   HUNT over the late window.

**HUNT's wild R by 100-year bins beside REF's** (registered, descriptive; wildr_timeline.txt). Founders (301-400) are
0.791 in both. HUNT's wild R rises to 0.849 in 401-500 and holds at 0.856-0.869 through 1600, ending at 0.854 over
3201-4000. REF's wild R falls to 0.670 at 701-800 and comes back to 0.712-0.732 from 1001 onwards. This answers exp017's
open question: REF's wild "springs back" to about 0.72, not to the 0.85-0.87 that hunting alone holds. The level it
recovers to is set below hunting's by about 0.14, by herding (as the reading under P4 says). The founders' 0.791 is not
the right reference for the recovery either: hunting alone moves the wild above it within a century.

**Standing control:** this batch's HUNT (seeds 1-8; runs at 477caad, a6f13b4 and 70758bf, per the raw entry) is the HUNT
record a later batch reruns or cites under the amendment's check.

**For Chris (descriptive; the density table is what was asked).** At midday a wild goat shares its cell with about
0.7-1.0 others (own 1.689-1.987 over arms, states and seeds) and has about 4-6 others in its 3×3. In every arm and state, the with-herder goats stand on
one cell: about 100 in an established REF or SPR05 herd, 10-20 in a small one, and 4-7 in SPR10's. Kept-at-camp goats sit
at about 2-19 per cell. A spook chance that rises with goats nearby would rest, for wild goats, on a range of about 1-2 per
cell. For a herd goat it would be the herd's head count. The 3×3 window adds about four goats for a wild goat and almost
nothing for a herd goat.

## exp018 results (scored), correction 2026-11-24 (the reviewer's b2dabf0; no verdict changes)
The reviewer reproduced f1c5f0a byte for byte (density, pair, timeline, the three --bad outputs). Verdicts stand: P1
fails (33 of 38), P2, P3 and P4 hold. This section replaces the sentences of f1c5f0a named below. Every number here is
printed by tools/density_tab.py at 8ca8db8. That version appends a "Derived" block; every earlier line of density.txt is
byte-identical to 361944d's (density_v2.txt is the earlier output).

**1. The herd stands on the herder's cell; that is the model's grazing, not a measured spacing (point 1).**
- With-herder own9 − own is 0.001-0.033 over every arm, state and seed. The widest is REF s1 est, 0.033. f1c5f0a's
  "0.001-0.015" left REF out and is withdrawn. Kept: up to 0.161; other herd: up to 0.087. No herd goat stands in the
  eight cells around a with-herder goat, beyond a few hundredths of a goat on average.
- Why (src/animals.js:410-421, grazeMove): by day a herd goat that is not alarmed moves to the cell of its 3×3 with the
  highest need × forage − herdPull × (0.5 + S) × distance to the herder (herdPull 1.0), plus 0.05 noise. When the pull
  outweighs the forage difference between neighbouring cells, the whole herd stands on the herder's cell. About 100 goats
  grazing one cell at midday is a property of that rule. Whether it is intended is Chris's call. It also bears on what a
  herd eats and on how exp017's spread alarm travels within a herd. Asked of Chris, 2026-11-24; the density table does
  not size a rule until he answers.
- Reading (the reviewer's, unchecked): with the herd on one cell, a spook chance rising with goats in the cell rises with
  the herd's head count. REF's herder spook already does that through herdLoad = herdCount / (herdPerHerder × herders),
  floored at minLoad (src/world.js:224-227). On the herd side, a nearby-goats rule would repeat REF's scaling; only the
  wild side would be new.

**2. P2 is read as a mechanism check (point 2).** The per-day test in the clarification was the reviewer's (940b5fe), and
the reviewer withdraws it (b2dabf0). With-herder goats per sample day sum up to three camps (params.js camps 3), so it is
not one herd's head count. f1c5f0a's "P2 is not read as a mechanism check on this evidence" is withdrawn.
- One cell: SPR05 with-herder own9 − own is 0.012-0.015 over est and 0.004-0.006 over small.
- One herd's head count, from herdComp (each camp's herd goats per managed camp-day, summed over its four classes): over
  est, per seed, 89.7-99.2, against with-herder own 90.756-101.003. Over est, with-herder own is about one herd's head
  count. Over small, the head count is 5.2-11.1, against own 9.934-14.071. Own is goat-weighted and head count is a
  camp-day mean; the gap is not examined further.
- So est own > small own follows from the state definitions (mean herded ≥ 100 against each row's herded < 60) once
  herds stand on one cell, as the clarification foresaw. P2 holds as a mechanism check.

**3. The recovery level (point 3).** Withdrawn from f1c5f0a: "This answers exp017's open question: ... The level it
recovers to is set below hunting's by about 0.14, by herding (as the reading under P4 says)." Replaced by: REF's wild
recovers to 0.712-0.732, below the 0.856-0.869 that hunting alone holds (501-1600). The level it recovers to is not
hunting alone's. What sets it is not separated: herding's gene flow, its captures, and fewer hunting tries (206.6
against 279.4 over 3201-4000) are all in the difference. The point on the founders' 0.791 stands.
Descriptive, no cause: REF's wild is already below HUNT's before any herd is established (0 of 8): 0.836 against 0.849
over 401-500, and 0.796 against 0.860 over 501-600.

**4. Derived numbers, now printed (point 4).** These replace f1c5f0a's inline figures.
- Wild goats per sample day, late, against HUNT's 580.4: REF 471.9 (−108.5), SPR05 474.8 (−105.6), SPR10 583.6 (+3.2).
  This replaces "about 105-110 fewer".
- Late huntTries against HUNT's 279.4: REF 206.6 (ratio 0.740), SPR05 227.0 (0.813), SPR10 308.8 (1.105). This replaces
  "about a quarter less".
- Wild own − 1 (others of its kind in its cell), seed range over every arm and state: 0.689-0.987. Wild own9 − own
  (others in the eight cells around): 3.295-4.891. These replace "0.7-1.0 others", "4-6 others in its 3×3" and "adds
  about four goats".
- P3's "a little less crowded": late wild own, own9 and all9 are REF 1.789, 5.580, 5.874 and SPR05 1.840, 5.860, 6.106,
  against HUNT's 1.871, 6.054, 6.054.

**5. Wording (point 5).**
- SPR10 seeds 3, 4 and 7 pass P1; "narrowly" is withdrawn. Their with-herder own9 is 5.830-6.642, against 4.099-5.613
  in the failing seeds. Their wild own9 is 5.515-5.620, against 6.355-6.475.
- The counter gives means of goat-weighted counts only. It cannot say how often a wild goat has, say, five or more
  others in its cell. A rule's effect depends on that spread, not only on the mean.

**For Chris, replacing f1c5f0a's paragraph (descriptive).** At midday a wild goat has 0.689-0.987 others of its kind in
its cell and 3.295-4.891 more in the eight cells around (seed ranges over every arm and state; means only, not the
spread). A goat walking with its herder stands on the herder's cell with the rest of the herd. That comes from grazeMove's
pull against forage, not from a measured herd spacing. So its cell holds about one herd's head count: in REF's
established herds, with-herder own 99.227-111.220 against a head count per managed camp-day of 96.6-108.7. In SPR10's
small state, with-herder own is 4.098-6.639. Whether the one-cell herd is intended comes before sizing any nearby-goats rule. If it stays,
such a rule on herd goats rises with the herd's head count, as herdLoad already does (the reviewer's reading,
unchecked), and only the wild side is new.

## exp020 — The herd ledger over the early years: which channels move the herd's R while REF's herd grows, and how they differ under a fixed load of 0.5?
**Pre-registered:** 2026-11-24. Chris, on the steward's "we know which ingredients the effect needs, not how they produce
it": "yes i want to look at the period when the R moves and the herd grows specifically. let's get detailed looks at
those periods. luckly they are early in REF. sample more often and gather data that you think might help us solve this
mystery." Mongo animalDomestication.exp020_ledger-early (mint); results/exp020_ledger-early; job list tools/exp020.jsonl
(16 runs, cpuslot --anywhere); code HEAD at queueing (named in the raw entry).
**Why:** a fixed load of the same strength gives an open, shallow herd with a small R gap. REF's load grows with the herd
(herdLoad = max(minLoad 0.25, herd / (herdPerHerder 20 × herders))), and it gives a closed, deep herd with a large gap.
exp010 LOAD05 has captive-sire share 0.333, lineage depth 3.95 and R gap -0.104; REF has 0.064, 14.69 and -0.636.
REF also loses fewer goats (0.082 per herd goat-year against LOAD1's 0.154) at about LOAD1's run-off rate.
exp014 showed that the spook must read the goat, but changed four things at once. Nothing recorded says which goats
leave the herd, by which route, with what R, or what load the herders actually run at. So nothing says how the
herd-size factor becomes closure and the R gap. REF's herds grow and its R moves early (KM median establishment 705; all
8 established by 1200, exp010), so a 1600-year run covers the whole period with every year recorded.
**The ledger** (src, this commit; logLedger=1, default 0; output only, no random draws; World.newLedger names every
field). Per camp and year, split by origin (captured itself, gsc 0; herd-born, gsc >= 1):
- **Flows** (goats and their summed R): in by capture, by birth to a herd sire or to a wild sire, by gift; out by loss on a
  run-off's refetch, loss as a night stray, slaughter, any other death, gift. With the year-end stock the ledger closes
  exactly: last year's stock + ins - outs = this year's, in goats and in summed R.
- **Spook events** (count, summed R, summed R × fearOfHumans at the event): spooked by the herder, caught a spread alarm,
  ran off, came back on its own, fetched back.
- **A midday sample each managed day:** herd count, herdLoad as the rule computes it, herders, and three groups by
  origin: goats walking with the herder (with their R, R × fear and the rule's daily spook chance herderAlarm × R × fear
  × load), goats kept at camp (sheltered, tethered, guarded), and the rest.
tools/ledger_check.py checks the closure and checks the ledger against the year row's own counters (captured,
herdBirths, escaped, runOffLost, spooked, alarmCaught, ranOff, rejoined, refetched, herded, exchanged). With --bad
(the 'died' channel dropped) it must fail. On a 470-year REF seed 1 run at this code: PASS, 0 of 2814
camp-origin-year pairs off, largest summed-R gap 0.0002 (rounding); --bad FAILs.
**Identity:** the same 470-year run against exp018's REF_seed1 (tools/cmp_years.py --by-year, a mode added in this
commit to pair records by year): 156 records compared (years 2-467), 77 shared keys, 0 differ. The same run against
exp005's REF_seed2 differs in all 156, so the comparison can fail. In the batch, each run is compared with the same
seed's record over years 2-1598: exp018 REF for REF, exp010 LOAD05 for LOAD05. ledger_check must PASS on all 16. A run that
differs is reported, and this batch's run is the one read. Standing control: the 700-year HUNT seed 1 probe at this
code against exp018's HUNT_seed1 is in the raw entry. If it reproduces (0 differ), exp018's HUNT is cited and no HUNT
arm is run.
**Arms** (seeds 1-8, 1600 years, so k = 1 and every year row is kept; logLedger=1; histPeriod=1, so the gene
histograms come every year against every 15th in the 4000-year runs):
- REF: exp018's REF arguments.
- LOAD05: exp010's LOAD05 arguments (REF's with herdPerHerder 1e9 and minLoad 0.5).
**Phases** (per seed, from J = jump_tab's establishment year, herd >= 100, from 400): A = 401 to J; B = J+1 to J+100
(the take-off century); C = J+101 to 1600. If a seed has no J by 1500, A runs to 1600 and the seed is named.
**Measures** (the analysis session; a committed tool, checked on the 470-year probe file, which a 1600-year run's first 470
rows reproduce, before any result; the herd pooled over the three camps unless named):
1. **Timeline**, annual, per seed:
   - herd N, mean R of the stock by origin, and the captured share of the stock;
   - realized load (summed load / days) and herders per day;
   - per walking goat-day by origin: the rule's daily spook chance and R × fear;
   - the shares of goat-days walking, kept at camp and other, by origin;
   - the wild's mean R.
2. **R accounting.** Each year's change in herd mean R splits exactly by channel. With last year's mean R̄ and this
   year's stock N, a channel k of n_k goats with summed R S_k contributes ±(S_k − n_k R̄)/N, + for ins and − for outs.
   The contributions sum to the year's change. Summed over each phase, per channel: capture, birth (herd sire), birth
   (wild sire), lost (run-off and night stray, also shown apart), slaughtered, other deaths. Years whose previous stock is
   under 5 goats are not split; the change across them is shown as "restart". The channels plus restart must sum to the
   phase's change in herd R̄, and the tool checks this.
3. **The spook filter**, per phase and origin:
   - spooks per walking goat-day;
   - mean R of spooked goats minus mean R of walking goats;
   - the share of run-offs lost (lost on refetch / ran off);
   - mean R of goats lost, fetched back and come back on their own.
4. **Captives**, per phase:
   - loss rate per goat-year by origin (lost / mean stock);
   - the captured share of goat-days kept at camp (tethered);
   - captures per year;
   - captive-sire share (flow_tab's definition).
**Predictions** (mine, written before any ledger output of the batch is read):
1. REF's realized load over phase B is above 2 in 6 or more of 8 seeds. Every fixed load of 2 or more lost every herd
   in exp010.
2. In REF over phases A and B together, losses (run-off plus night stray) are the channel with the most negative
   contribution to herd R̄, in 6 or more of 8 seeds.
3. In REF over phase B, captured goats are lost at a higher rate per goat-year than herd-born goats in every seed. The
   ratio of the two rates is higher than LOAD05's (over LOAD05's own phase B) in 6 or more of 8 seed pairs.
**Decision rule:** descriptive; no model change follows from this batch alone. To Chris:
- which channel carries REF's herd R change in each phase, and how LOAD05's differ;
- whether the load and the captives' attrition behave as predicted.
If prediction 2 fails, the channel that does carry the change is named.

## exp020 amendment, 2026-11-24 (before any run queued; the reviewer's prereg review, ac321c5)
All seven points are taken. Where a passage below says "replaces", the entry's passage is replaced; the rest stands.
1. **Origin split (point 1).** Measure 2 prints every channel's contribution three ways: by captured goats, by herd-born
   goats, and by both together. A captive enters above R̄ and is often lost soon after, so a loss channel can be the most
   negative through captive turnover alone. That is not a filter acting on the herd's own lineage. Prediction 2 is
   therefore registered twice (below). Two competing explanations are named in advance; both are unchecked:
   - **Herd-sire births.** buckManagement 1, sireRule 'oldest', keepSires 2: the two oldest bucks sire. They are the
     bucks that survived the filter longest, so their kids may enter below R̄. That is selection through which bucks
     breed, not a spook channel.
   - **Slaughter.** REF's cull has no flightiness term (flightCost 0, nuisanceCost 0), so any R effect of slaughter
     comes through age, sex, size or kidding record.
2. **Phases (point 2; replaces the Phases paragraph).** J is jump_tab's year: the first at which the trailing 100-year
   herd mean is 100 or more and holds for 400 years. So the climb lies before J. Four phases per seed:
   - A = 401..J-100, the small herd;
   - T = J-99..J, the climb;
   - B = J+1..J+100;
   - C = J+101..1600.

   J comes from this batch's annual rows, so it may differ by a year or two from the earlier 3-year-row Js. jump_tab
   follows a run to its last row minus the 400-year hold, so a seed with no J by 1200 is named, and its A runs to 1600.
   LOAD05's J is left-censored: it sits at the tool's floor of 501 in s4 and s6, and at 531 or earlier in six seeds
   (exp010). Its T therefore marks the latest its herd can have climbed, not when it did. Where J − 99 < 401, T starts
   at 401 and A is empty.
3. **Prediction 1 (point 3; replaces it).** With economy 0 a camp has one herder whenever it has a herd (herdN = 1). So
   REF's load is max(0.25, camp herd / 20), and "load above 2" only means a camp herd above 40. It is kept as a
   descriptive check, labelled as following from herdN = 1, not as a prediction. The new prediction 1 is on what lets
   REF's herd stand that load: the walking goats themselves. "Every fixed load of 2 or more lost every herd" is
   withdrawn. exp010's LOAD2 and LOAD3 established in 0 of 8 seeds each.
4. **Prediction 3 (point 4; replaces its denominator and pairing).**
   - **Exposure:** midday goat-days by origin (walk + kept + other) / yearDays. The year-end-stock rate is printed beside it.
   - **Criterion:** fixed, not paired by seed number.
   - **Floor:** a seed is read in phase B only if it holds 20 or more captured goat-years there and a herd-born loss rate
     above 0. Otherwise it is named and counted as not read. "Every seed" means every seed that is read.
   - **Scoring:** prediction 3 is scored only if 6 or more seeds of each arm are read; otherwise "not read".
   - **Timing:** LOAD05's phase B falls earlier than REF's (exp010 J 501-669 against 588-957), against a wild that is itself
     still changing.
   - **Tethered captives:** they cannot run off (tetherNew; R × fear ≥ captureFear). Captive attrition is read beside
     measure 4's kept share, so a low captive loss rate is not read as captives being tame.
5. **The midday block's checks (point 5).** tools/ledger_check.py (this commit) adds:
   - walking goat-days = density.c[1].n, exactly, as a fail condition;
   - bornW = wildSiredShare × herdBirths, within the row's rounding, as a fail condition;
   - kept and other against density.c[2] and c[3], printed only: the ledger skips camps with no herder.

   On the 470-year probe all pass. Kept differs in 4 rows (total -4) and other in 11 (total -13). The analysis tool
   prints two further comparisons each year:
   - the stock's mean R beside histHerd's binned mean R;
   - spooks per walking goat-day beside walk[3] / walk[0], which can differ because one is a midday snapshot and the other
     counts the whole day.

   A probe that reaches a J: REF seed 6, 1000 annual years at this code (logLedger=1, histPeriod=1; exp010 J 588). The
   analysis tool is checked on it and on its own planted-J selftest before any result. It is queued now; its result and
   ledger_check go in the raw entry.
6. **Standing control (point 6; replaces the Identity entry's HUNT sentences).** The rule as amended (EXPLOG, exp018
   amendment point 5) asks for one 4000-year HUNT seed 1 run at the batch's code, reproducing exp018's HUNT_seed1 on
   every year row with hist identical. It is running now (--scratch, HUNT4000check_seed1), checked with
   tools/cmp_years.py --by-year. That tool now also compares hist and histHerd rows paired by histYears; on the 700-year
   probe it gives 0 of 46 differing against HUNT_seed1 and 46 of 46 on hist against HUNT_seed2. The batch is queued only
   once the check passes. Otherwise HUNT seeds 1-8 join the batch. Against HUNT: available, not read.
7. **Minor (point 7).**
   - **Identity:** each batch run is checked on hist and histHerd as well as on year rows, over the shared years.
   - **Wording:** the rule's "daily spook chance" is its daily rate (expected spooks per walking goat-day); it can exceed 1
     at REF's loads.
   - **Disclosure:** before these predictions were written I saw ledger_check's output on the probe (REF s1 to year 469:
     totals of 312 captures, 381 escapes, 1695 spooks, 1321 herd goat-rows) and the kept and other differences above.
     No per-channel R contribution and no R × fear by origin were computed or seen.
   - **Pooled restart:** the restart rule (previous pooled stock under 5) is pooled, so one camp's herd dying out and being
     refounded is split as ordinary flows, which is still exact.

**Predictions** (replacing the entry's three):
1. Over phase B, REF's walking goats have mean R × fear (walk[2] / walk[0], both origins) below one third of the median
   of LOAD05's eight phase-B values, in 6 or more of 8 REF seeds. That is, the herd has become calm faster than its load
   rose.
2. (a) In REF over A, T and B pooled, losses (run-off plus night stray, both origins) are the most negative channel in
   herd R̄'s change, in 6 or more of 8 seeds. (b) The same on herd-born goats alone: herd-born losses are the most
   negative of the herd-born channels, in 6 or more of 8 seeds. Each is also printed per phase (A, T, B), descriptive.
   If (a) holds and (b) fails, the reading for Chris says the losses' effect is captive turnover.
3. In REF over phase B, captured goats are lost at a higher rate per goat-year of exposure than herd-born goats in every
   seed that is read. The ratio of the two rates is above the median of LOAD05's read seeds in 6 or more of 8 REF seeds.

## exp020 amendment 2, 2026-11-24 (before any run queued; the reviewer's 26e87a4, 8d68c97)
Points C and D are taken, and the minor points too. The rest of the amendment stands.
- **C: P2(b) on the herd-born stock's own mean** (replaces how (b) is computed). (b) as written measured herd-born
  channels against the pooled R̄, captives included. Where captives sit above the herd-born goats in R, losing one of the
  highest-R herd-born goats could then count as positive, so (b) could fail on exactly what it is meant to detect.
  - The herd-born stock closes on its own, so (b) splits the change in the herd-born mean R over its own channels, using
    its own N and its own last-year mean.
  - Its channels are births to a herd sire, births to a wild sire, and herd-born goats lost, slaughtered and dead of
    other causes.
  - The split must close per year and per phase, and the tool checks this. The restart rule applies to the herd-born
    stock's own previous count (under 5).
  - (b) reads: herd-born losses are the most negative of these channels over A, T and B pooled, in 6 or more of 8 REF
    seeds, also printed per phase. (a) is unchanged, on the pooled mean.
- **D: prediction 1 anchored on the other arm's median** (replaces the amendment's prediction 1). Since the rule's rate
  is herderAlarm × R × fear × load, "calmer than the load rose" is exactly the per-goat rate being lower, so the
  arbitrary third is dropped. Over phase B, against the median of LOAD05's eight phase-B values:
  - (a) REF's walking goats' mean R × fear (walk[2] / walk[0], both origins) is below it, in 6 or more of 8 REF seeds.
    This is the claim that the herd calmed.
  - (b) REF's rule rate per walking goat-day (walk[3] / walk[0], both origins) is above it, in 6 or more of 8 REF seeds.
    This is the claim that the calming did not fully offset the load.
  - Both are my expectation. The ground for (b) is that REF ran off more per herd goat-year than LOAD05 in exp010's
    window (0.859 against 0.631), a late window and per herd goat rather than per walking goat, so (b) can fail.
  - Walking R × fear is truncated: a herd goat with R × fear ≥ captureFear 0.35 is tethered and not walking, and fear
    habituates each night toward fearMin. So walking goats' R (walk[1] / walk[0]) and the kept share are printed beside
    it, by origin, and (a) is read with them.
- **Minor:** tools/ledger_check.py --bad now takes died, walk or bornW. On the 470-year probe each FAILs, and the clean
  run PASSes:
  - walk: one goat-day added gives 1 row differing;
  - bornW: one birth moved from born to bornW gives 1 row differing.
  For HUNT, the histHerd comparison cannot fail (no herd), so only hist counts in the 4000-year check.
  **Disclosure, added:** ledger_tab's probe output exists (results/_scratch/exp020_ledger_probe/ledger_tab_probe.txt and
  ledger_tab_testJ430.txt). It holds per-channel contributions for REF s1 over 401-470. The analysis session and the
  reviewer have seen it, and so have I, in the analysis session's message: phase A capture +0.0952, born -0.0221, lost
  -0.1429, died -0.0317, restart +0.0683. Predictions 1 and 3 were not computed on it, apart from --testJ's labelled
  non-reading.

## exp020 amendment 3, 2026-11-24 (before any run queued): packet size; and the J probe
**The problem.** The J probe (REF seed 6, 1000 annual years, logLedger=1, histPeriod=1, --scratch, saved as
scratch exp056/REFledger1000_seed6, results/_scratch/exp056_probe/) is 13.4 MB of BSON. A 1600-year run would be about
21 MB, over Mongo's 16 MB limit, and db.js refuses a packet that size: the JSON copy is kept, but the run is not stored
in Mongo. Of the probe's 8.7 MB of JSON:
- the ledger is 2.29 MB;
- the annual gene histograms are 1.65 MB;
- five inline diagnostics the batch does not read are 1.76 MB: herdDeathHalf 0.56, sizeByAge 0.35, cohortBirth 0.30,
  cohortBreed 0.28, firstKidStats 0.27.

**The change** (replaces the Arms paragraph's settings; the arms are unchanged):
- **Switches.** Those five fields get diagnostic switches (src/params.js logHerdDeathHalf, logSizeByAge,
  logCohortBirth, logCohortBreed, logFirstKidStats; default 1; DIAG_FIELDS in datamanager.js, as the other switches).
  This batch sets all five to 0. Output only: a field is deleted from the saved row and nothing else changes. A 3-year
  run with the five at 0 lacks all five fields and keeps the rest.
- **Histograms.** histPeriod=1 is dropped, so the histograms come every 5 years, runyears' default at k = 1. The
  analysis tool's comparison of stock mean R with histHerd's binned mean is then made every 5 years.
- **Size.** The probe trimmed this way (src/db.js bsonSize) is 7.39 MB. Adding the extra 600 years at the rate of the
  probe's years 600-999 gives an estimated 11.7 MB for a 1600-year run.
- **No measure depends on what is removed.** The tools that read those fields (cohort_tab, genecost_tab, ogm_tab,
  sexsize_tab, wildcal_tab) are not exp020's.

**The J probe's checks** (amendment 1 point 5; before the batch):
- ledger_check PASS: 1000 annual rows, 5994 camp-origin-year pairs, 0 off, largest summed-R gap 0.0002; walk = density
  0 rows differing; bornW 0 rows differing.
- cmp_years --by-year against exp018's REF_seed6: 333 records over years 2-998, 77 shared keys, 0 differ. hist and
  histHerd each 0 of 66 rows differing (years 14-989).
- The analysis tool is checked on this file before any result, with --refJ against exp018's REF runs. Its output goes
  in the raw entry.

## exp020 results (raw)
16 of 16 runs are complete (complete: true, 1600 annual rows each, labels 0-1599). Every run exited 0 (cpuslot-logs/,
batch 1795591917811932600). No log has an error, exception or warning; each carries the db client's packet-size
advisory (over its 4 MB suggestion), which does not stop the save.
- Arms as registered, 8 seeds each: REF and LOAD05. Parameters are identical across the 16 except id, seed, and
  herdPerHerder and minLoad (LOAD05: 1e9 and 0.5; REF: 20 and 0.25). All 16 have logLedger 1 and the five switches of
  amendment 3 at 0.
- Hosts: 13 on the desktop, 3 on mint (LOAD05 s4-6). Run times 2878-4247 s.
- The mint logs of LOAD05 s5 and s6 also say "NOT copied" for the sibling files (LOAD05_seed4, and seed4 and seed5),
  which earlier mint runs had already copied back to the desktop. Each run's own file was copied back, and each passes
  the identity check below.

**Commit.** All 16 are stamped v0.1.0-367-g7cf6888, dirty false. `git diff --stat 700f5d4 7cf6888` over src,
tools/runyears.mjs and tools/load.mjs is empty: the commits between them touched notes/review and
tools/ledger_tab.py only.

**Packet size** (amendment 3; the reviewer asked for real sizes):
- Each packet is 12.1-12.2 MB of BSON (the db client's own measure in each log): LOAD05 s1 12.1, the other 15 12.2.
  This is against amendment 3's estimate of 11.7 MB.
- db.js refused none: no packet carries storeError. The JSON copies are 7,705,743-7,860,714 bytes on disk.

**Identity** (registered; tools/cmp_years.py --by-year, which also pairs hist and histHerd by histYears; output in
results/exp020_ledger-early/checks/identity.txt):
- REF s1-8 against exp018's REF: 533 records each (years 2-1598, 1600 vs 1333), 72 shared keys, 0 differ.
- LOAD05 s1-8 against exp010's LOAD05: 533 records each (years 2-1598), 65-69 shared keys, 0 differ.
- hist and histHerd: 106 rows each (years 14-1589), 12 traits, 0 differ, in all 16.
- The ledger is output only, and these runs are the earlier batches' runs over 1-1600.

**Ledger closure** (tools/ledger_check.py; output in results/exp020_ledger-early/checks/ledger_check.txt):
- PASS on all 16. Each run has 9594 camp-origin-year pairs, 0 with goats differing, 0 with summed R off by more than
  1e-3. The largest summed-R gap is 0.0002 in 12 runs and 0.0003 in 4.
- Every counter matched its year-row field in every row: cap, born + bornW, lostRun, lostRun + lostNight, spooked,
  caught, ranOff, rejoined, refetched, stock, exIn, exOut, walk goat-days = density.c[1].n, and bornW against
  wildSiredShare.
- Printed only, not failed (the ledger skips camps with no herder): kept goat-days fall below density.c[2].n in 1-21
  rows per run, by 1-24 goat-days in total. Other goat-days fall below density.c[3].n in 3-66 rows, by 3-89 in total.
  The ledger is never above density.
- The bad cases, on REF s1: --bad died, --bad walk and --bad bornW each FAIL.

**The standing control** (cited, not rerun; the reviewer's d8b477e):
- The 4000-year HUNT check ran at c91c20b src: results/_scratch/exp055_probe/HUNT4000check_seed1.json against exp018's
  HUNT_seed1.
- Its result: 1333 of 1333 records compared, 0 differ; hist 0 of 266 rows differ (histHerd cannot fail for HUNT, which
  has no herd).
- The src diff from c91c20b to 700f5d4 is only the five diagnostic switches (src/params.js, DIAG_FIELDS in
  src/datamanager.js). They default to 1, so no draw and no field of a HUNT run changes. 700f5d4 to 7cf6888 is empty
  over src (above).

**The scorer on the J probe** (amendment 3; the reviewer accepted it in d8b477e):
- Command, at tools/ledger_tab.py 7e1d753: `python tools/ledger_tab.py results/_scratch/exp056_probe REFledger1000
  --as REFledger1000=REF --perseed --timeline 10 --refJ "results/exp018_density-hunt=REF"`.
- Rerun at 7cf6888, its output is identical to analysis's results/_scratch/exp056_probe/ledger_tab_s6.txt (diff
  empty).
- It prints "checks passed on 1 runs" and J 587, against exp018's 588, which it reports and does not fix. Its phases
  are A 401-487, T 488-587, B 588-687, C 688-1000.

**Disclosures for the scored entry, beside the predictions:**
- **REF s6 was seen before results.** It is one of the 8 REF seeds, run with the J probe's seed, code and arguments.
  The switches are output only, and the identity check above shows the run unchanged, so it reproduces the probe over
  1-1000. Its J (587) and its A, T and B (to 687) all lie inside the probe, so its values for P1a, P1b, P2a, P2b and P3
  were fixed beforehand.
- What was seen (analysis's probe report):
  - Pooled change in mean R: A −0.1942, T −0.2219, B −0.2257, C −0.0858.
  - Lost is the most negative channel in A, T and B, both pooled and on the herd-born stock alone.
  - In B: load 4.111, walking R×fear 0.035, and captured vs herd-born loss 0.560 vs 0.236 per exposure goat-year.
- P2a and P2b are therefore also scored `--without 6`, and the scored entry says whether they read the same.
- **"8.7 MB" in amendment 3** is the length of Python's spaced JSON serialisation of the probe. The probe's file on disk
  is 7,074,340 bytes. Its BSON size, 13.4 MB, is the db client's measure and the one the 16 MB limit applies to.

## exp020 results (raw), note 2026-11-25 (the reviewer's 713ca0f; corrections, no result changes)
**1. The standing control's stamp.** The raw entry says the HUNT check ran "at c91c20b src". It did not:
- The packet is stamped v0.1.0-347-gdc480b8-dirty. The run started at 07:03:19Z, 39 s before c91c20b was committed
  (07:03:58Z).
- c91c20b changed only EXPLOG.md, tools/cmp_years.py and tools/ledger_check.py. `git diff --stat dc480b8 c91c20b --
  src` is empty, so the run used the same src either way.
- It ran with logLedger 0 and histPeriod 15, exp018 HUNT's settings.
- Its result stands as given: 1333 of 1333 records, 75 shared keys, 0 differ; hist and histHerd 0 of 266 rows.
- The comparison was read before the batch was launched, by hand and not by script. The HUNT run finished at 07:31:41Z.
  Its cmp_years output was read at 07:31:50Z, and the submit was issued as a separate command at 07:31:57Z (session
  transcript).

**2. REF s6 against the probe, directly.** `python tools/cmp_years.py results/exp020_ledger-early/REF_seed6.json
results/_scratch/exp056_probe/REFledger1000_seed6.json --by-year`:
- 1000 records compared (years 0-999), 73 shared keys including the ledger, 0 differ.
- hist and histHerd: 200 rows each (years 4-999), 0 differ.
- Output in results/exp020_ledger-early/checks/s6_vs_probe.txt. The batch's REF s6 is therefore the probe over
  0-999, ledger included.

**3. The check files** now carry each command above its output (identity.txt, ledger_check.txt). Each of the three bad
cases has its own command line and exits 1. results/ is gitignored, so these files are kept on disk, not committed; the
lines quoted here are the record.

**4. Three ledger checks are not exercised.** caught, exIn and exOut are 0 in every row of all 16 runs, and the year
rows' alarmCaught and exchanged are 0 too. Their equality checks pass trivially and test nothing in this batch.

**5. LOAD05's shared keys.** The 65-69 shared keys against exp010 vary because exp010's eight LOAD05 files were made
at six commits (4afb749-dirty for 3 seeds; 65e8cc0, bbd6259, 06c97bc, b64a201 and a659a59-dirty for 1 each). Their
year rows carry different field sets.

## [RETROSPECTIVE 2026-10-25] Trials before this ledger existed (not pre-registered)

Backfilled from `results/*/batch.log` launch times matched to the git history, the settings files, and
the raw outputs (tables regenerated with `tools/trial_summary.py`, last 100 years of each run, means
over seeds with per-seed values in brackets; herd − wild R is the yearly difference averaged). These
were **not pre-registered**; their settings were chosen as we went, and their conclusions were written
into DEVLOG (cited per entry). Times are PDT. **Status:** *current* = run on today's defaults;
*historic* = valid for its code, but the model has changed since; *invalid* = its code had a bug that
affects the result (fix named). DEVLOG headings carry the session's date stamps, which run up to a
day ahead of the PDT commit times; entries are cited by heading.

### replace — with food sites redrawn every year and no dump heap, does a herd build up?
**Launched:** 2026-10-24 22:50 · **code:** 3e3bc55 · **status:** current
**Settings:** tools/cal_replace.json (E1r, E2r: economy, 10 people/camp, plantValue 1, foodReplace 1, heapSeed 0, cropDamage 0, siteGrass 1; E2r herderAlarm 0.02, penning, provision 0.6, opportunity cull)
**Method:** batch 800 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG entry headed 2026-10-26 (misdated; written 2026-10-25).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1r | 3 | 800 | 426 | 0 (0 0 0) | 0.89 | — (— — —) | 2.4 | 0.73/0.27/0.00 |
| E2r | 3 | 800 | 432 | 8 (8 7 8) | 0.87 | -0.02 (-0.02 -0.02 -0.03) | 3.8 | 0.53/0.15/0.33 |

### crop — what do land competition and crop damage do?
**Launched:** 2026-10-24 17:13 · **code:** 42b8606 · **status:** historic (crop damage and land competition switched off, 3e3bc55)
**Settings:** tools/cal_crop.json (E2 with land competition siteGrass 0.5 + cropDamage 1, heapSeed 2e-5 or 0; control without either)
**Method:** batch 800 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-25 (late).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E2crop_h0 | 3 | 800 | 969 | 52 (86 37 32) | 0.67 | -0.03 (-0.03 -0.03 -0.03) | 1.6 | 0.34/0.19/0.47 |
| E2crop_h2e-5 | 3 | 800 | 1041 | 115 (134 93 116) | 0.64 | -0.04 (-0.04 -0.04 -0.04) | 0.1 | 0.27/0.15/0.58 |
| E2nocrop_h2e-5 | 3 | 800 | 514 | 65 (96 33 65) | 0.81 | -0.05 (-0.08 -0.03 -0.04) | 0.4 | 0.36/0.10/0.54 |

### heap — dump-heap rate; slop-only control
**Launched:** 2026-10-24 16:48 · **code:** e4642ea · **status:** historic (dump heap off, 3e3bc55)
**Settings:** tools/cal_heap.json (E2 heapSeed 0 / 1e-4 / 3e-4; E1 heapSeed 1e-4)
**Method:** batch 800 y × 3 seeds; near-camp sites from `econ.nearSites`; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-25 (late).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1h1e-4 | 3 | 800 | 428 | 0 (0 0 0) | 0.89 | — (— — —) | 0.0 | 0.75/0.25/0.00 |
| E2h0 | 3 | 800 | 460 | 19 (35 13 9) | 0.87 | -0.03 (-0.05 -0.01 -0.03) | 2.7 | 0.48/0.13/0.38 |
| E2h1e-4 | 3 | 800 | 518 | 86 (117 83 57) | 0.79 | -0.11 (-0.12 -0.16 -0.04) | 0.1 | 0.32/0.09/0.59 |
| E2h3e-4 | 3 | 800 | 528 | 89 (115 69 82) | 0.77 | -0.08 (-0.10 -0.10 -0.04) | 0.1 | 0.31/0.09/0.59 |

### cascade — what does the spoilage cascade do?
**Launched:** 2026-10-24 16:16 · **code:** e4642ea · **status:** historic (heap rate later lowered, then heap off)
**Settings:** tools/cal_cascade.json (E1c, E2c: spoilage cascade with heapSeed 0.002, foodPatches 120)
**Method:** batch 800 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-25 (night).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1c | 3 | 800 | 437 | 0 (0 0 0) | 0.88 | — (— — —) | 0.0 | 0.75/0.25/0.00 |
| E2c | 3 | 800 | 522 | 89 (115 62 90) | 0.78 | -0.11 (-0.17 -0.05 -0.10) | 0.1 | 0.31/0.09/0.59 |

### plantfood_wet — plant food placed by wetness
**Launched:** 2026-10-24 11:59 · **code:** 910fe5d · **status:** historic (cascade added after)
**Settings:** tools/cal_plantfood_wet.json (E1/E2 at foodPatches 60/120, centres by wetness)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-25 (evening).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1p120 | 3 | 600 | 429 | 0 (0 0 0) | 0.89 | — (— — —) | 1.8 | 0.74/0.26/0.00 |
| E1p60 | 3 | 600 | 406 | 0 (0 0 0) | 0.89 | — (— — —) | 25.5 | 0.68/0.32/0.00 |
| E2p120 | 3 | 600 | 452 | 19 (37 10 10) | 0.87 | -0.02 (-0.02 -0.02 -0.04) | 2.7 | 0.48/0.13/0.39 |
| E2p60 | 3 | 600 | 423 | 6 (11 1 6) | 0.87 | -0.03 (-0.03 -0.03 -0.02) | 25.5 | 0.53/0.22/0.24 |

### plantfood — a second resource: human plant food
**Launched:** 2026-10-24 11:38 · **code:** 74d8629 · **status:** historic (placement by wetness, 910fe5d)
**Settings:** tools/cal_plantfood.json (E1 foodPatches 60/120; E2 120 at spook 0.02/0.05; uniform placement)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-25 (later).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1p120 | 3 | 600 | 418 | 0 (0 0 0) | 0.89 | — (— — —) | 16.9 | 0.70/0.30/0.00 |
| E1p60 | 3 | 600 | 408 | 0 (0 0 0) | 0.89 | — (— — —) | 44.7 | 0.59/0.41/0.00 |
| E2p120_a0.02 | 3 | 600 | 428 | 10 (27 1 1) | 0.87 | -0.03 (-0.04 -0.04 -0.02) | 17.7 | 0.56/0.20/0.24 |
| E2p120_a0.05 | 3 | 600 | 430 | 8 (22 1 1) | 0.88 | -0.03 (-0.03 -0.02 -0.03) | 17.2 | 0.57/0.20/0.23 |

### gatherrate — does a faster gathering rate make a surplus?
**Launched:** 2026-10-24 11:12 · **code:** aed7e0f · **status:** historic (two resources since 74d8629)
**Settings:** tools/cal_gatherrate.json (forageCut/forageLoad ×1.5 and ×2, plantValue 1; one plant resource)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-25.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1x15 | 3 | 600 | 416 | 0 (0 0 0) | 0.83 | — (— — —) | 0.0 | 0.82/0.18/0.00 |
| E1x2 | 3 | 600 | 411 | 0 (0 0 0) | 0.83 | — (— — —) | 0.0 | 0.79/0.21/0.00 |
| E2x15_a0.02 | 3 | 600 | 432 | 16 (15 14 18) | 0.81 | -0.02 (-0.04 -0.02 -0.01) | 0.0 | 0.55/0.09/0.36 |
| E2x15_a0.05 | 3 | 600 | 427 | 13 (11 14 13) | 0.81 | -0.04 (-0.04 -0.03 -0.03) | 0.0 | 0.57/0.09/0.34 |
| E2x2_a0.02 | 3 | 600 | 424 | 10 (10 10 10) | 0.81 | -0.03 (-0.05 -0.02 -0.03) | 0.0 | 0.54/0.10/0.36 |
| E2x2_a0.05 | 3 | 600 | 416 | 7 (6 7 9) | 0.82 | -0.04 (-0.04 -0.04 -0.03) | 0.0 | 0.56/0.11/0.33 |

### loose — loose run-offs
**Launched:** 2026-10-24 10:32 · **code:** b1e6adb · **status:** historic (plantValue > 1 retired; second resource since)
**Settings:** tools/cal_loose.json (refetchRunOffs 2 with chaseDelay 2; H5 fixed policy and E2 plantValue 1.0/1.5 at spook 0.05/0.02; H5off reference)
**Method:** batch 600 y × 3 seeds (rerun after the chase-delay fix; the first run chased in the same sub-tick); raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-24 (night).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E2pv100loose_a0.02 | 3 | 600 | 441 | 15 (15 14 17) | 0.82 | -0.04 (-0.04 -0.04 -0.03) | 0.0 | 0.59/0.08/0.33 |
| E2pv100loose_a0.05 | 3 | 600 | 426 | 10 (9 10 12) | 0.82 | -0.04 (-0.03 -0.05 -0.04) | 0.0 | 0.63/0.08/0.29 |
| E2pv150loose_a0.02 | 3 | 600 | 477 | 54 (55 56 51) | 0.80 | -0.09 (-0.08 -0.09 -0.12) | 0.0 | 0.47/0.07/0.46 |
| E2pv150loose_a0.05 | 3 | 600 | 440 | 21 (24 12 26) | 0.82 | -0.06 (-0.10 -0.03 -0.06) | 0.0 | 0.60/0.08/0.32 |
| H5loose_a0.02 | 3 | 600 | 525 | 92 (94 93 90) | 0.81 | -0.09 (-0.09 -0.13 -0.04) | — | — |
| H5loose_a0.05 | 3 | 600 | 487 | 58 (66 52 55) | 0.81 | -0.13 (-0.18 -0.12 -0.09) | — | — |
| H5off | 3 | 600 | 528 | 100 (100 101 101) | 0.85 | -0.05 (-0.04 -0.05 -0.05) | — | — |

### econ_p10c — does herd size follow the surplus?
**Launched:** 2026-10-24 08:45 · **code:** 91d8f1c · **status:** historic (plantValue fixed at 1 later; refetch default changed)
**Settings:** tools/cal_econ_p10c.json (E2 plantValue 0.75–1.5, feed signal = hungry goats)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-24 (evening).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E2pv100 | 3 | 600 | 437 | 19 (15 18 24) | 0.82 | -0.03 (-0.02 -0.02 -0.03) | 0.0 | 0.56/0.08/0.36 |
| E2pv125 | 3 | 600 | 457 | 37 (32 32 46) | 0.82 | -0.02 (-0.01 -0.04 -0.01) | 0.0 | 0.52/0.07/0.41 |
| E2pv150 | 3 | 600 | 485 | 54 (51 50 62) | 0.81 | -0.03 (-0.03 -0.02 -0.04) | 0.0 | 0.49/0.07/0.44 |
| E2pv75 | 3 | 600 | 413 | 3 (3 3 3) | 0.83 | -0.03 (-0.03 -0.04 -0.03) | 1.8 | 0.75/0.10/0.14 |

### econ_p10b — economy with the new gathering rule
**Launched:** 2026-10-24 07:55 · **code:** 46651a6 · **status:** historic
**Settings:** tools/cal_econ_p10b.json (E1/E2 plantValue 0.75/1.0, distance-vs-yield gathering, groupSink 0; E2 rerun after the herding-return fix)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-24 (later).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1pv100 | 3 | 600 | 420 | 0 (0 0 0) | 0.83 | — (— — —) | 0.0 | 0.86/0.14/0.00 |
| E1pv75 | 3 | 600 | 414 | 0 (0 0 0) | 0.83 | — (— — —) | 1.6 | 0.85/0.15/0.00 |
| E2pv100 | 3 | 600 | 429 | 14 (14 13 14) | 0.82 | -0.02 (-0.02 -0.03 -0.02) | 0.0 | 0.61/0.08/0.31 |
| E2pv75 | 3 | 600 | 415 | 3 (3 3 3) | 0.83 | -0.03 (-0.03 -0.03 -0.03) | 1.8 | 0.76/0.10/0.14 |

### econ_p10 — 10 people per camp; herding sub-roles
**Launched:** 2026-10-23 23:36 · **code:** c6009ed · **status:** E1 historic; **E2 invalid** (herding return was the camp total, not ÷ herders; fixed 46651a6)
**Settings:** tools/cal_econ_p10.json (10 people/camp; E1 plantValue 0.75/1.0/1.5; E2 1.0/1.5 with herding sub-roles; gatherers claim cells)
**Method:** batch 600 y × 3 seeds (rerun after the claim fix); raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-24.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1p10pv100 | 3 | 600 | 404 | 0 (0 0 0) | 0.86 | — (— — —) | 25.2 | 0.74/0.26/0.00 |
| E1p10pv150 | 3 | 600 | 411 | 0 (0 0 0) | 0.87 | — (— — —) | 8.5 | 0.77/0.23/0.00 |
| E1p10pv75 | 3 | 600 | 407 | 0 (0 0 0) | 0.87 | — (— — —) | 36.6 | 0.74/0.26/0.00 |
| E2p10pv100 | 3 | 600 | 408 | 0 (0 0 0) | 0.86 | +0.03 (+0.05 — +0.02) | 23.7 | 0.64/0.16/0.20 |
| E2p10pv150 | 3 | 600 | 421 | 3 (3 2 3) | 0.87 | -0.02 (-0.03 -0.02 -0.03) | 6.5 | 0.65/0.14/0.22 |

### econ_e2 — does surplus go to herding?
**Launched:** 2026-10-23 22:31 · **code:** 69e176a · **status:** **invalid** (herding-return bug, fixed 46651a6)
**Settings:** tools/cal_econ_e2.json (E2 plantValue 0.75/1.0, 5 people/camp)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-23 (night).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E2pv100 | 3 | 600 | 432 | 5 (5 5 6) | 0.82 | -0.03 (-0.04 -0.04 -0.02) | 0.1 | 0.66/0.09/0.25 |
| E2pv75 | 3 | 600 | 424 | 2 (2 2 2) | 0.82 | -0.02 (-0.03 -0.02 -0.02) | 5.7 | 0.80/0.13/0.07 |

### econ_pv — calibrate plant value so gathering + hunting meet demand
**Launched:** 2026-10-23 22:23 · **code:** 69e176a · **status:** historic
**Settings:** tools/cal_econ_pv.json (E1 plantValue 0.5/0.75/1.0, 5 people/camp)
**Method:** batch 500 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-23 (night).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1pv100 | 3 | 500 | 423 | 0 (0 0 0) | 0.82 | — (— — —) | 0.0 | 0.86/0.14/0.00 |
| E1pv50 | 3 | 500 | 421 | 0 (0 0 0) | 0.84 | — (— — —) | 23.8 | 0.83/0.17/0.00 |
| E1pv75 | 3 | 500 | 421 | 0 (0 0 0) | 0.82 | — (— — —) | 5.1 | 0.84/0.16/0.00 |

### econ_e1 — does the economy cycle (Lotka–Volterra) or equilibrate?
**Launched:** 2026-10-23 ~22:00 · **code:** 69e176a · **status:** historic
**Settings:** direct `runyears.mjs 700` × 3 seeds, economy=1 econHerd=0 herdingAt 1e9
**Method:** 3 runs; raw table: last 100 y. **Conclusions:** DEVLOG (reported in chat 2026-10-23).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| E1 | 3 | 700 | 434 | 0 (0 0 0) | 0.84 | — (— — —) | 60.3 | 0.80/0.20/0.00 |

### crep1 — wild type vs hunting with crepuscular wolves
**Launched:** 2026-10-23 19:47 · **code:** 4360353 · **status:** historic (gatherer rules changed c6009ed/46651a6, affecting H1)
**Settings:** tools/conditions.json H0, H1 (crepuscular wolves, goats flee wolves)
**Method:** batch 500 y × 10 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-23 (later).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H0 | 10 | 500 | 499 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.66 | — (— — — — — — — — — —) | — | — |
| H1 | 10 | 500 | 408 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.85 | — (— — — — — — — — — —) | — | — |

### h1diag — which hunting channel raises wild R?
**Launched:** 2026-10-23 ~19:00 · **code:** a8fe869 · **status:** historic (crepuscular wolves since 4360353)
**Settings:** direct `runyears.mjs 400`, H1 (herdingAt 1e9) base / huntFlee 0 / stalkDetect 0 / huntEffort 0 / humanFieldR −1 (± huntFlee 0)
**Method:** runs 400 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-23 (later).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| base | 3 | 400 | 277 | 0 (0 0 0) | 0.81 | — (— — —) | — | — |
| nofield | 3 | 324 | 209 | 0 (0 0 0) | 0.67 | — (— — —) | — | — |
| nofieldnoflee | 3 | 318 | 223 | 0 (0 0 0) | 0.66 | — (— — —) | — | — |
| noflee | 3 | 400 | 212 | 0 (0 0 0) | 0.84 | — (— — —) | — | — |
| nohunt | 3 | 400 | 369 | 0 (0 0 0) | 0.64 | — (— — —) | — | — |
| nostalk | 3 | 400 | 250 | 0 (0 0 0) | 0.82 | — (— — —) | — | — |

### sweep_spook — spook-rate sweep with refetch
**Launched:** 2026-10-22 08:38 · **code:** c0f2eda · **status:** historic (refetch default is now loose run-offs, mode 2)
**Settings:** tools/sweep_spook.json (H3/H4/H5 × refetch off + herderAlarm 0.002–0.05 with refetch 1) and tools/cal_h4prov.json (H4 + fodder)
**Method:** batch 800 y × 4 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-22, 2026-10-23.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H3_a0.002 | 4 | 800 | 391 | 102 (112 85 102 110) | 0.85 | -0.03 (-0.05 -0.04 -0.05 +0.02) | — | — |
| H3_a0.005 | 4 | 800 | 379 | 85 (80 64 93 103) | 0.83 | -0.05 (-0.03 -0.04 -0.07 -0.07) | — | — |
| H3_a0.01 | 4 | 800 | 318 | 18 (17 5 17 33) | 0.89 | -0.02 (-0.04 -0.02 -0.03 -0.02) | — | — |
| H3_a0.02 | 4 | 800 | 312 | 5 (3 13 2 3) | 0.90 | -0.02 (-0.01 -0.03 -0.01 -0.02) | — | — |
| H3_a0.03 | 4 | 800 | 309 | 5 (5 5 2 7) | 0.90 | -0.03 (-0.03 -0.02 -0.02 -0.05) | — | — |
| H3_a0.05 | 4 | 800 | 317 | 3 (3 4 2 2) | 0.90 | -0.02 (-0.02 -0.02 -0.02 -0.03) | — | — |
| H3_off | 4 | 800 | 407 | 117 (110 121 117 121) | 0.84 | -0.03 (-0.02 +0.01 -0.08 -0.03) | — | — |
| H4_a0.002 | 4 | 800 | 319 | 24 (23 23 27 21) | 0.91 | -0.03 (-0.01 -0.03 -0.05 -0.01) | — | — |
| H4_a0.005 | 4 | 800 | 313 | 20 (19 22 16 23) | 0.90 | -0.02 (-0.03 -0.02 -0.02 -0.02) | — | — |
| H4_a0.01 | 4 | 800 | 315 | 20 (23 20 16 21) | 0.90 | -0.02 (-0.02 -0.04 -0.01 -0.03) | — | — |
| H4_a0.02 | 4 | 800 | 312 | 14 (11 11 15 18) | 0.90 | -0.02 (-0.02 -0.03 -0.02 -0.02) | — | — |
| H4_a0.03 | 4 | 800 | 304 | 9 (7 14 10 5) | 0.90 | -0.02 (-0.03 -0.02 +0.00 -0.01) | — | — |
| H4_a0.05 | 4 | 800 | 314 | 6 (3 8 7 7) | 0.90 | -0.02 (-0.02 -0.01 -0.03 -0.01) | — | — |
| H4_off | 4 | 800 | 326 | 22 (20 25 21 24) | 0.90 | -0.02 (-0.03 -0.02 -0.02 -0.00) | — | — |
| H4prov_a0.02 | 4 | 800 | 364 | 75 (77 79 69 75) | 0.85 | -0.17 (-0.13 -0.23 -0.13 -0.20) | — | — |
| H4prov_off | 4 | 800 | 392 | 85 (85 89 87 81) | 0.89 | -0.04 (-0.03 -0.03 -0.02 -0.06) | — | — |
| H5_a0.002 | 4 | 800 | 394 | 85 (92 75 87 84) | 0.89 | -0.04 (-0.06 -0.03 -0.03 -0.04) | — | — |
| H5_a0.005 | 4 | 800 | 410 | 91 (93 86 94 90) | 0.89 | -0.04 (-0.08 -0.03 -0.03 -0.02) | — | — |
| H5_a0.01 | 4 | 800 | 408 | 87 (89 84 88 88) | 0.86 | -0.10 (-0.11 -0.10 -0.03 -0.14) | — | — |
| H5_a0.02 | 4 | 800 | 390 | 87 (89 83 84 90) | 0.84 | -0.19 (-0.21 -0.09 -0.13 -0.33) | — | — |
| H5_a0.03 | 4 | 800 | 396 | 77 (80 92 53 83) | 0.85 | -0.24 (-0.22 -0.44 -0.04 -0.28) | — | — |
| H5_a0.05 | 4 | 800 | 367 | 44 (23 24 39 91) | 0.88 | -0.16 (-0.04 -0.03 -0.12 -0.46) | — | — |
| H5_off | 4 | 800 | 404 | 90 (90 89 92 90) | 0.89 | -0.09 (-0.04 -0.15 -0.08 -0.08) | — | — |

### refetch — immediate refetch of run-offs
**Launched:** 2026-10-21 20:34 · **code:** c0f2eda · **status:** historic
**Settings:** tools/cal_refetch.json (H3/H4/H5 refetch 0/1) and tools/cal_alarm.json (refetch 1, herderAlarm 0.005–0.02)
**Method:** batch 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21 (later still).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H3a005 | 3 | 600 | 352 | 57 (51 77 42) | 0.87 | -0.04 (-0.06 -0.04 -0.02) | — | — |
| H3a01 | 3 | 600 | 319 | 20 (17 5 40) | 0.89 | -0.04 (-0.03 -0.02 -0.07) | — | — |
| H3a02 | 3 | 600 | 318 | 9 (12 7 9) | 0.90 | -0.01 (-0.00 -0.01 -0.01) | — | — |
| H3r0 | 3 | 600 | 408 | 113 (105 113 121) | 0.85 | -0.01 (-0.01 -0.01 -0.01) | — | — |
| H3r1 | 3 | 600 | 307 | 3 (4 2 2) | 0.90 | -0.02 (-0.03 -0.01 -0.02) | — | — |
| H4r0 | 3 | 600 | 320 | 22 (18 24 23) | 0.91 | -0.02 (-0.02 -0.02 -0.03) | — | — |
| H4r1 | 3 | 600 | 310 | 6 (4 4 11) | 0.90 | -0.02 (-0.02 -0.02 -0.01) | — | — |
| H5a005 | 3 | 600 | 409 | 90 (89 90 90) | 0.87 | -0.05 (-0.04 -0.07 -0.04) | — | — |
| H5a01 | 3 | 600 | 427 | 87 (86 85 89) | 0.87 | -0.05 (-0.04 -0.07 -0.05) | — | — |
| H5a02 | 3 | 600 | 404 | 79 (80 79 78) | 0.84 | -0.10 (-0.14 -0.09 -0.06) | — | — |
| H5r0 | 3 | 600 | 420 | 92 (94 89 92) | 0.89 | -0.07 (-0.06 -0.08 -0.08) | — | — |
| H5r1 | 3 | 600 | 357 | 24 (21 30 23) | 0.88 | -0.04 (-0.03 -0.07 -0.03) | — | — |

### diag_spook — dusk spooking: timing or rate?
**Launched:** 2026-10-21 ~19:00 · **code:** 1ab4576 · **status:** historic
**Settings:** direct `runyears.mjs 600`, H5 settings, offtake 0, spookAtDusk 0 (day) / 1 (dusk)
**Method:** runs 600 y × 3 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21 (later).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| day | 3 | 600 | 409 | 97 (97 96 98) | 0.88 | -0.08 (-0.11 -0.09 -0.04) | — | — |
| dusk | 3 | 600 | 410 | 82 (85 79 82) | 0.84 | -0.15 (-0.15 -0.11 -0.17) | — | — |

### diag_h5 — did culling or the bug fixes raise herd R?
**Launched:** 2026-10-21 18:46 · **code:** a621d40 · **status:** historic
**Settings:** tools/diag_h5.json (H5, offtake 0)
**Method:** batch 800 y × 10 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21 (later).
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H5o0 | 10 | 800 | 412 | 95 (98 92 95 97 90 94 93 96 94 98) | 0.88 | -0.08 (-0.11 -0.06 -0.05 -0.05 -0.10 -0.08 -0.21 -0.04 -0.07 -0.06) | — | — |

### stage4v3 — condition table after the cold-check fixes
**Launched:** 2026-10-21 14:13 · **code:** b381d31 · **status:** historic
**Settings:** tools/conditions.json (H0–H6, offtake 10%/y, keepHorizon 3)
**Method:** batch 800 y × 10 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H0 | 10 | 800 | 382 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.62 | — (— — — — — — — — — —) | — | — |
| H1 | 10 | 800 | 317 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.90 | — (— — — — — — — — — —) | — | — |
| H2 | 10 | 800 | 380 | 92 (79 109 57 91 103 98 93 96 87 108) | 0.86 | -0.02 (+0.00 -0.02 -0.05 -0.04 -0.01 -0.04 -0.00 +0.02 -0.01 -0.10) | — | — |
| H3 | 10 | 800 | 407 | 116 (110 117 121 117 121 113 113 119 105 119) | 0.84 | -0.03 (-0.02 -0.01 +0.01 -0.08 -0.03 -0.03 -0.02 -0.02 -0.00 -0.05) | — | — |
| H4 | 10 | 800 | 324 | 22 (20 24 25 21 24 24 22 21 18 25) | 0.90 | -0.02 (-0.03 -0.01 -0.02 -0.02 -0.00 -0.01 -0.03 -0.03 -0.02 -0.04) | — | — |
| H5 | 10 | 800 | 407 | 89 (90 88 89 92 90 86 82 94 93 91) | 0.89 | -0.06 (-0.04 -0.04 -0.15 -0.08 -0.08 -0.03 -0.04 -0.09 -0.01 -0.06) | — | — |
| H6 | 10 | 800 | 321 | 24 (26 28 22 24 25 21 25 25 22 24) | 0.90 | -0.02 (-0.03 -0.02 -0.02 -0.03 -0.03 -0.01 -0.02 -0.03 +0.00 -0.01) | — | — |

### offtake1 — offtake rate and keep horizon
**Launched:** 2026-10-21 13:39 · **code:** b381d31 (launched with the fixes uncommitted) · **status:** historic
**Settings:** tools/cal_offtake.json (H3/H5 offtake 0–0.3) and tools/cal_horizon.json (keepHorizon 3/5)
**Method:** batch 600 y × 6 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H3o00 | 6 | 600 | 412 | 125 (125 123 130 125 124 123) | 0.85 | -0.01 (-0.00 -0.01 -0.00 +0.01 -0.02 -0.06) | — | — |
| H3o10 | 6 | 600 | 345 | 57 (92 58 81 57 35 20) | 0.88 | -0.02 (-0.02 -0.02 -0.04 -0.02 +0.00 -0.03) | — | — |
| H3o10k3 | 6 | 600 | 402 | 114 (105 113 121 121 108 116) | 0.85 | -0.02 (-0.01 -0.01 -0.01 -0.07 -0.02 -0.02) | — | — |
| H3o10k5 | 6 | 600 | 402 | 114 (119 89 123 123 111 118) | 0.86 | -0.01 (-0.00 -0.02 -0.01 -0.00 +0.02 -0.06) | — | — |
| H3o20 | 6 | 600 | 305 | 4 (4 5 4 5 3 5) | 0.89 | -0.02 (-0.01 -0.01 -0.02 -0.01 -0.01 -0.02) | — | — |
| H3o20k3 | 6 | 600 | 313 | 11 (5 19 9 6 17 8) | 0.89 | -0.02 (-0.01 -0.03 -0.01 -0.02 -0.02 -0.01) | — | — |
| H3o20k5 | 6 | 600 | 327 | 26 (3 7 4 78 56 11) | 0.88 | -0.03 (-0.02 -0.01 -0.03 -0.02 -0.06 -0.01) | — | — |
| H3o30 | 6 | 600 | 312 | 3 (3 3 2 2 3 3) | 0.90 | -0.02 (-0.01 -0.01 -0.01 -0.03 -0.03 -0.02) | — | — |
| H5o00 | 6 | 600 | 410 | 95 (97 96 98 95 88 97) | 0.88 | -0.08 (-0.11 -0.09 -0.04 -0.10 -0.05 -0.10) | — | — |
| H5o10 | 6 | 600 | 409 | 91 (93 83 93 93 89 93) | 0.88 | -0.06 (-0.09 -0.03 -0.06 -0.06 -0.03 -0.07) | — | — |
| H5o20 | 6 | 600 | 405 | 79 (86 76 82 81 77 73) | 0.89 | -0.03 (-0.06 -0.04 -0.01 -0.01 -0.03 -0.05) | — | — |
| H5o20k3 | 6 | 600 | 405 | 86 (88 87 83 83 84 88) | 0.89 | -0.04 (-0.05 -0.01 -0.07 -0.07 -0.03 -0.02) | — | — |
| H5o20k5 | 6 | 600 | 401 | 78 (82 82 83 77 67 78) | 0.89 | -0.05 (-0.06 -0.02 -0.04 -0.09 -0.01 -0.06) | — | — |
| H5o30 | 6 | 600 | 330 | 9 (7 11 11 8 13 5) | 0.90 | -0.02 (-0.02 -0.02 -0.02 -0.03 -0.02 -0.02) | — | — |

### stage4v2 — condition table on the rebuilt model
**Launched:** 2026-10-21 13:21 · **code:** 7b7e356 · **status:** **invalid** (culling never ran: H3 ≡ H2, H6 ≡ H4; plus ~10 bugs; fixed b381d31)
**Settings:** tools/conditions.json at 7b7e356 (H0–H6, offtake 0)
**Method:** batch 800 y × 10 seeds, **stopped at 28/70**; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| H0 | 6 | 800 | 384 | 0 (0 0 0 0 0 0) | 0.63 | — (— — — — — —) | — | — |
| H1 | 6 | 800 | 314 | 0 (0 0 0 0 0 0) | 0.90 | — (— — — — — —) | — | — |
| H2 | 4 | 800 | 400 | 110 (117 100 102 120) | 0.75 | -0.13 (-0.19 -0.07 -0.05 -0.21) | — | — |
| H3 | 3 | 800 | 398 | 106 (117 100 102) | 0.76 | -0.10 (-0.19 -0.07 -0.05) | — | — |
| H4 | 3 | 800 | 331 | 20 (17 21 22) | 0.88 | -0.04 (-0.05 -0.04 -0.04) | — | — |
| H5 | 3 | 800 | 409 | 90 (88 93 89) | 0.86 | -0.53 (-0.49 -0.60 -0.52) | — | — |
| H6 | 3 | 800 | 331 | 20 (17 21 22) | 0.88 | -0.04 (-0.05 -0.04 -0.04) | — | — |

### stage2v4 — wild type after the rebuild
**Launched:** 2026-10-21 ~13:10 · **code:** 7b7e356 · **status:** historic (crepuscular wolves since 4360353)
**Settings:** defaults, no humans (H0); stage2v2/v3 were earlier calibration steps of the same day
**Method:** runs 500 y × 10 seeds; raw table: last 100 y. **Conclusions:** DEVLOG 2026-10-21.
| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |
|---|---|---|---|---|---|---|---|---|
| (all) | 10 | 500 | 363 | 0 (0 0 0 0 0 0 0 0 0 0) | 0.63 | — (— — — — — — — — — —) | — | — |

### Probe runs (single runs with diagnostic tools; outputs printed, not saved unless noted)
- `tools/filters.mjs` (R at each gate in and out of the herd), 2026-10-22 ~23:00, code 4ee5148; H5 off /
  0.02 / 0.03, H3 off / 0.005, 3 seeds × 800 y, from year 600; outputs `results/filters/*.txt`. Historic.
  DEVLOG 2026-10-23.
- `tools/kidfate.mjs`, `tools/herdcauses.mjs`, `tools/doestat.mjs`, `tools/campherds.mjs` (herd books,
  death causes, doe condition, per-camp herd sizes), 2026-10-21 to 10-24, various codes; DEVLOG 2026-10-21,
  10-23, 10-24.
- `tools/huntsel.mjs` (R selection by hunters vs wolves), 2026-10-23, on 6113dcf (old) and f006f20 /
  4360353 (new); DEVLOG 2026-10-23 (later).
- `tools/wolfmem.mjs` (wolves' prey memory), 2026-10-23, 4360353; DEVLOG 2026-10-23 (night).
- `tools/econprobe.mjs` (feeding gaps, shortfall timing), 2026-10-24, 46651a6 / 91d8f1c; DEVLOG 2026-10-24.
- Fix bisection (single cold-check fixes on 7b7e356, H5, 2 seeds × 600 y), 2026-10-21, scratch worktrees,
  outputs not kept; DEVLOG 2026-10-21 (later).

### Before the rebuild (model v1, commits b773d4c–11f9f07; superseded by the rebuild ed2d739)
`results/stage2` (wild type, Stage 2 close, bc8d90f), `results/stage3` (H0 vs H1, 6113dcf),
`results/stage4`, `stage4cal`, `stage4cal2`, `stage4opp`, `stage4opp2`, `stage4size` (Stage 4e condition
table and calibrations, 66b3b8c–11f9f07). Results in DEVPLAN Stages 2–4. Status: historic (model v1).
