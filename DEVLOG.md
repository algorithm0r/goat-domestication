# Animal Domestication — DEVLOG
Newest entry on top. **Append only — never edit past entries.**

## 2026-11-12 — winter cull budgets breeding does and young only; dashboard labels for the new switches
**Done:** Chris: "budget fodder only for breeding does and young". `winterCull` (world.js cullToFodder) now budgets a
full ration through the lean season for each breeding-age doe and each goat under a year, and culls only among those
(lowest keep value first) while the store falls short; bucks and dry yearlings winter on grazing. dashboard/labels.js
describes surplusCull, fodderRation, winterCull and milkCondition. Chris: keep them as switches we can reset ("these
might be results after we rerun anchors"): each stays its own switch, off by default. **State:** all off reproduces
results/settle S0 seed 1 for 600 years (0 of 600 year records differ on shared fields; histograms identical). All four
on (milkCondition 0.5), 1101-1200 (scratchpad husb): open reference, seed 1: herd 103.2 and still rising (first form
61.4; old 237.2), births 121.0 (94.6), winter cull 55.9 and surplus 21.7 a year, no starvation (old 33.4), doe condition
0.97, three camps of 42-52 at the end of 1199. Isolated reference, seed 3: herd 78.7 (old 250.5), births 107.5,
winter cull 51.6, surplus 29.9, no starvation (old 52.0), doe condition 0.87, but one of its three camps had no herd by
1100 (when and why not logged). Single seeds, 1200 years. **Next:** pre-register a pilot of the new husbandry on the
anchors (open and isolated, 4 seeds, 4000 years) before using it.

## 2026-11-12 — milk yield by condition, winter cull to the fodder; surplusCull renamed (was buckCull)
**Done:** With Chris ("milk by condition, and cull does before feeding them over winter"). `milkCondition` (animals.js
milkCapacity): a doe's milk capacity is full at a reserve of milkCondition × cap or more and falls in proportion below,
so kids and herders both get less from a thin doe (Flores-Najera et al. 2021). `winterCull` (world.js cullToFodder): on
the first lean day the herder slaughters goats in the cull rule's order until the fodder store covers a full ration for
every goat kept through the lean days ahead, never below cullFloor; credited against the year's offtake. **Fix:** the
surplus-buck switch of the entry below was named `buckCull`, which is already the bucks' own cull rule (2026-11-10;
settle bCullRand sets buckCull=random). In params.js the older key came later and won, so defaults were unaffected, but
buckCull=random would have switched on the surplus cull, and buckCull=1 crashed the sex cull once the winter cull first
called the cull order. Renamed `surplusCull`; a check for duplicate keys in params.js finds the old clash and none now.
The surplus-cull smokes below were unaffected (the offtake was always zeroed by the credit, so the cull order never ran).
**State:** all four switches off reproduce results/settle S0 seed 1 for 600 years (0 of 600 year records differ on the
fields that run has; histograms identical). Smokes with surplusCull, fodderRation, winterCull 1 and milkCondition 0.5
(scratchpad husb), 1101-1200: open reference (S0 settings, seed 1) herd 61.4 (old 237.2), births 54.8 (94.6), winter
cull 13.1 and surplus 11.3 a year, no starvation (old 33.4), per camp 10.5 adult does, 2.3 adult bucks, doe condition
0.98, captures 14.0 (6.7); isolated reference (HmaxIso, seed 3) herd 104.0 and still rising (old 250.5), births 120.4
(125.8), winter cull 55.5 and surplus 29.2, no starvation (old 52.0), doe condition 0.90. In both the store never ran
out and fed the priority class in full; the rest got none and did not starve. **Next:** the winter cull budgets a full
ration for every goat, though grazing carries bucks and dry does, so it may cull deeper than a herder would; Chris to
decide what the herder plans fodder for. No pilot is pre-registered on these switches yet.

## 2026-11-12 — surplus-buck cull and rationed lean-season fodder (both off by default)
**Done:** With Chris, after the isolated-herd collapse diagnostic (EXPLOG 50f67d1: an isolated camp carried 1.0-5.6 adult
bucks per doe, one starvation year killed its does and left 30 bucks). Chris: "agreed on sire cull with a collection
of insurance bucks only", and fodder "should just be rationed and prioritized ... ration fodder in the lean months to
last instead of feeding full maintainence and then starving". `buckCull` + `insuranceBucks` (world.js
cullSurplusBucks): each night every weaned herd male beyond the sires and 2 spares is slaughtered, credited against the
same year's offtake draws. `fodderRation` (world.js rationFodder, Goat.rationClass): each lean day a camp's budget is its
store over the lean days left; pregnant or nursing does and goats under a year first, the rest after, each class in
proportion to want. **State:** off reproduces results/settle S0 seed 1 for 600 years (0 of 600 year records differ on
the fields that run has; histograms identical). Smoke, HmaxIso settings + both on, seed 3, 1200 years: herd about 200
from 701 (old run 210-250), births 185-198 a year (old 126-145), surplus bucks culled about 80 a year and no other
offtake. Diagnostic 1101-1200 (scratchpad feedchk): per camp 34 adult does, 3.4 adult bucks, 37 under a year; the store
lasts the lean season (0.2 empty lean days a camp-year); class 0 gets 46% of its want, class 1 none; buck condition
0.93, doe 0.56; starvation 52 a year, 5084 of 5166 pregnant or nursing does. The yearly credit cap was added after the
smoke (it then carried over); offtake was all surplus bucks in either form. **Next:** what kills the does is breeding
and milking cost against short fodder, not the allocation: Chris to decide milk yield by condition and whether herders
cull does to what the fodder can carry.

## 2026-11-11 — dashboard in plain language
**Done:** With Chris ("fix labels for someone that maybe doesn't know all the arcane R, A, T, B, run labels/arms"):
`dashboard/labels.js` names every experiment folder (title and the question from its EXPLOG entry), every condition
(133, hand-written), and each gene (name and what reads it, from draft.tex Table 1); it turns settings into words and
lists how a condition differs from the reference culture. The page shows those, a "How to read this page" note,
plain chart titles, "current settings" / "older settings" badges with tooltips, and the raw settings behind a
disclosure. Builder: reads humansPerCamp (older no-human runs set it to 0, not humansAt) and a BUILD number in the
cache stamp forces a full rebuild when the digest changes. Staged runs carry a note that their stored settings are
the last stage's. **State:** checked at localhost:8000/goats on staged H0 and STAGED, ladder Hmin, settle noBuck,
depthcheck S0, desktop and phone width. **Next:** new folders or conditions need an entry in labels.js (they fall back
to their code names and the automatic differences line).

## 2026-11-11 — dashboard served by the Static Server; ladder pilot scored
**Done:** The dashboard is at http://localhost:8000/goats/ (Chris: use the port 8000 server): mount `goats` added to
`Claude's Space/Static Server/sites.json`, which the always-on server re-reads without a restart. Removed the
`goat-dashboard` launch config (port 8791), which the gene-dashboard entry below names. Experiment dates in the
dashboard are local dates (were UTC). Ladder pilot results in EXPLOG (6862367). **Why:** one server for viewing,
which no session's cleanup can kill. **Next:** the factorial decides the minimal rung (Chris, 2026-11-11).

## 2026-11-11 — lineage depth through wild births; gene histograms by lineage; dashboard depth view
**Done:** With Chris. `src/world.js` bornKid: a wild-born kid of escaped herd stock now gets `wv` (its parents' herd-born
generations at the same depths, a fully wild parent's half at 0); conception keeps the sire's `wv` whether he is herd
or wild. Herd births, capture's reset to null and a herd kid's wild sire counting as fully wild are unchanged, so the
deep and shallow sire rules see what they saw. `src/datamanager.js`: `histDepth` (every 10 years, per trait: herd goats
by mean depth rounded in GEN_BINS, wild goats by herd-born genome share in SHARE_BINS 0 | 1/16 | 1/8 | 1/4 | 1/2 | more),
and year fields `wildHerdShare`, `wildAnyHerd`; `tools/runyears.mjs` saves `histDepth`. Dashboard: a "By lineage" section
(one heatmap per gene, a column per lineage class, window of years chosen; builder pools to 100-year records).
**Why:** Chris: plot the gene distributions by depth, the analogue of the grain paper's generations since planting, which
reads no trait; and see feral lines in the wild. **State:** identity checks (settle arms, seed 1, 600 years, against
results/settle): S0, Ldeep, noPen, R3bRandom: 0 of 600 year records and 0 histogram years differ; S0 and noPen re-run
after the wild share bins: 0 differ (new fields left out); histDepth sums equal hist/histHerd in every record. First look,
S0 seed 1, years 500-599: wild goats' mean herd-born share 0.59, 94% of wild goats have some (noPen 0.67, 91%); a
first binning of wild goats by mean depth called 93% "feral" and was replaced (it mixes share with depth). The ladder
pilot ran on the code before this change and has no histDepth. results/depthcheck holds the two re-check runs (1 seed,
600 years) so the dashboard has a depth example. **Next:** score the ladder pilot.

## 2026-11-11 — gene dashboard (dashboard/), anchor ladder pilot queued
**Done:** With Chris, a data dashboard: `dashboard/index.html` + `dashboard/dashboard.js`, Claude Basic 0.6.0
(v0.6.0-1-g3279460) vendored in `dashboard/vendor/claude-basic/`. Per arm: herd and wild goats, herd lineage depth and
IBD, and for each of the 10 genes the wild and herd genotype distributions over time (histogram heatmaps, 20 buckets on
0-1) and their means (lines). `node tools/dashboard.mjs [folder ...]` builds `dashboard/data/` (git-ignored) from every
results/ run that recorded herd histograms (histHerd, from 2026-11-02): pooled over seeds, columns of 10 years (20 for
runs over 2000 years); re-reads only changed files. First build: 129 arms from 1,760 files (211 older arms have no herd
histograms), 28 MB. Serve with the `goat-dashboard` launch config (python http.server on 8791 over dashboard/).
Pre-registered and queued the anchor ladder pilot (3cf8105): WT2 (hunting, no herds) and Hmin (factorial all-off).
**Why:** Chris wants the genetic distributions of every gene, wild and domesticated, in one place, from the data we
already have; the ladder (wild type 1, wild type 2, minimal herding, maximal herding) is the set of anchors the suite
plans from. **State:** checked in the browser pane on settle S0, noBuck and WT (dark, paper, phone width); arms with
no humans draw all goats only. Base label: new = leanBuffer 12000 and herdTravel 2 (range swept). **Next:** score the
ladder pilot, add a ladder view to the dashboard; ask Chris whether "separated by R" means herd membership or R genotype.

## 2026-11-11 — new standard settings: leanBuffer 12000, herdRange 8, herdTravel 2; perf-speedup merged; cell ~1 km
**Done:** merged perf-speedup (4f1d7b6; merged code checked against saved results, four 600-year runs equal in every
year record). Added `herdTravel` (82085e2): a herd and its herder walk herdTravel cells per sub-tick out at dawn and
home at dusk. Relabelled the cell as nominally ~1 km (ebb57e5; no code reads the scale). With Chris, made three
settings standard in src/params.js: leanBuffer 0 -> 12000, herdRange 4 -> 8, herdTravel 1 -> 2 (MODEL C24, C55, G11).
**Why:** herdRange 6 and 8 at herdTravel 1 lost every herd (goats short of camp at the night check); at herdTravel 2
herds hold about 102 / 145 / 224 at range 4 / 6 / 8 (EXPLOG 2026-11-11). Chris wants the largest separation, with
range reported as a key sweep variable; the buffer is the starvation rule he chose (Turner et al. 1993).
**State:** a 40-year run at the new defaults equals results/lean S0on seed 1 (leanBuffer 12000 set explicitly) in all
40 years and differs from results/pilot S0 seed 1 in all 40. Every result before this commit ran leanBuffer 0,
herdRange 4, herdTravel 1 unless its condition file says otherwise; condition files that rely on defaults now give
different runs. **Next:** the run-length pilot on the new base.

## 2026-11-10 — headless runs ~2.5x faster on herding years, outputs identical (branch perf-speedup)
**Done:** Speed audit before the ~5,800-run paper suite (goat-perf side session, for the experiment session to
merge). Base b46dbe1. Profile (`node --cpu-prof`, tools/pilot.json S0, seed 1, 520 y, split at year 400): before
herding buildIndex 40% (19 rebuilds a day; its socialField box sum alone was read only by foraging goats), Goat.step
14%, wolfTick 14% (goatsNear box sums, inlined), forage + score 12%, graze 7%. From year 400 the same per-goat loops
ran 3-12x slower per year with the population flat (~400-600 goats): goats acquired fields after construction
(fetusFather*, _kidsAtYearStart, _milkAtYearStart, capturedYear, _cullKey, _sireKey, _sireRank, _sexKey, _sexTie,
_seenRate) in varying orders, so by the herding years they had 12 hidden classes (counted with %HaveSameMap) and
every property read in the hot loops went megamorphic. Herding mechanics proper (culls, sires, stores) were < 4%.
**Changed:** src/animals.js, src/world.js (no RNG draw, iteration order or float operation order changed; no
parameter added):
(1) every field a goat ever gets is declared in the Goat constructor as `undefined` (likewise Human), so all goats
share one hidden class (1 map, was 12) and every read behaves as before;
(2) Goat.score reads its socialRange company from a summed-area table of goatCount (integer sums, the same values);
World.socialField is now a getter that builds the old field only when something else reads it (tools/herdstat.mjs);
(3) goatsNear / goats3x3 read the same table, built at most once per index rebuild and only when read;
(4) size^0.75 cached per size (Goat.p75), log1p of the company count and the wolves' Math.pow(near, wolfAttractExp)
from tables of the same Math values;
(5) buildIndex's cell starts from a running total in a local (the start[i+1] = start[i] + cnt[i] chain was half its
time); buildSat with hoisted offsets; keepersRefetch skips its scan when no camp has a keeper.
New tools: tools/samerun.mjs (two runs identical in every field but `seconds`, else the first difference, exit 1);
tools/perfcases.mjs (the check list below as a cpuslot --list, for any tree).
**State:** identical outputs, branch 0905f2d against b46dbe1, every field but `seconds`, through cpuslot:
S0 seeds 1, 2, 3 (520 y); seed 1 at 520 y with one change each: sireRule random, deep, homebred + herdMemory 3,
marked; exchangeN 2; humansAt 1e9; buckManagement 0; guarding 0; penning 0; cullRule random; milkIntensity 0;
smokes (300 y, humansAt 5, herdingAt 10): buckCull calm, youngMales; doeCull large, homebred; wildSireBlock 1;
captureUntil 150. **20 of 20 SAME** (also 20 of 20 at f6b5bce; fresh base reruns equal the first base runs 20 of
20). samerun fails where it should: S0 vs sireRule random (params, and with params removed `years.401.goats` 392 vs
381), seed 1 vs 2, and one trait mean changed by 1e-12. Browser: index.html src runs in strict-mode scripts; a seeded
6-year herding run gives the same SHA-256 of years/hist/histHerd/samples on main and branch, in Chromium and Firefox.
Engines: headless Firefox (SpiderMonkey) and headless Chromium give output identical to Node for S0 520 y and
60 herding years, base and branch: Math.pow/log1p/cos/exp agree across engines here.
Timings (wall s, base vs branch back to back in one slot, order alternating by case, --no-pause; all 20 at once on
a full pool, so absolute times are inflated): S0-type 520 y cases 612-653 vs 358-372 (x1.71-1.79); smokes 739-754
vs 282-288 (x2.59-2.66), captureUntil 150 604 vs 308 (x1.96); wild only 461 vs 335 (x1.38). Repeats on a lighter
pool: S0 seed 1 520 y 648 vs 252 (x2.57), r2 447 vs 213 (x2.10); wild only 300 y x1.20, x1.52, r2 x2.11. Single pairs
vary ~±25% on this hybrid CPU. Per year (the full-pool batch; before herding from the wild-only run, with herding from the
smokes): base ~0.89 s and ~2.48 s; branch ~0.64 and ~0.95, so a 4000-y run with herding from 400 should take ~2.5x less (estimate, not yet a measured 4000-y pair).
Not attempted: anything that changes draws or order (fewer sub-ticks, per-goat noise, threads); what remains is
mostly the per-goat sub-tick work those draws define.
**Next:** experiment session: check and merge perf-speedup between batches (queued runs load src/ at start).
Found on the way, not touched: World.draw(c, k, x) (the shelf-life store draw) shadows the engine's draw(ctx) hook,
so the browser view throws on its first frame (`c.q is undefined`, main and branch alike).

## 2026-10-31 — ranged shot for fixed-policy hunters (off); fodder defaults from the economy work
**Done:** With Chris. (1) The ranged shot now works with economy 0: per attempt, the capture draw first,
then a shot if a wild goat is seen within shotRange, else a stalk (89d7ab6; shotChance 0 bit-identical).
Stalk vs shot (EXPLOG 2026-10-30, `results/shots`): shots keep wild R near the pre-human 0.67 (0.68 vs
0.86) with more learned fear; herd − wild R the same (−0.32 vs −0.31). Default stays stalking (shotChance
0): a cell is ~2 km and bows shoot at tens of metres, so a real archer still has to close in unseen; the
shot stands for ambush hunting, kept as a condition. (2) Fodder (EXPLOG 2026-10-31, `results/fodder`):
storeWindows 1 (cut fodder keeps 270 days) and forageLoad 36,000 (was 72,000) are now the defaults.
**Changed:** src/world.js, src/datamanager.js (shots, shotKills in the year record when shotChance > 0
and economy 0), src/params.js (storeWindows 1, forageLoad 36000); tools/cal_shots.json,
cal_fodder.json, shot_rows.py, cond_rows.py.
**State:** smoke PASS (40 y, 485 goats). New defaults reproduce H1f and H5f seed 1 (0 of 450 years differ).
H5 herd 89 → 82, herd − wild R −0.31 → −0.22. H2, H3, H4, H6 hold only 2–4 herded goats on current code
(the 10-21 table, stage4v3, had 22–116): only H5 keeps a herd.
**Next:** why H2–H4, H6 herds collapse (G13 and what changed since stage4v3); hunter prey choice (Asiab:
~70% of hunted goats older than 4 y; model 33–38%); keepers per herd as a set level; MODEL.md to kcal.

## 2026-10-29 — main fast-forwarded to exp/gather-hunt; back to fixed-policy conditions
**Done:** Chris re-set the direction: human behaviour is the controlled variable (policies fixed per
condition; each act's outcome still turns on the goat), goat genotype and phenotype are the outcome.
The camp economy (`economy` 1, roles chosen by return) is parked behind its switch. Since 10-21 the
work ran on experiment branches, recorded in EXPLOG only: rebuild attribution, alarm-driven fear,
escapee and cull tests, shelf-life store windows, need-relative returns, kcal units, seen gathering,
ranged shots, other game. On Chris's approval main was fast-forwarded 7aac26c → 71752e3; it now
contains every exp/ and diag/ branch (exp/kcal's one extra commit is the same H5 fix).
**Changed:** main only (no code change in this entry). Fix carried in: tools/conditions.json H5
`provision` 0.6 → 2160, since the kcal change had left H5 with effectively no fodder.
**State:** smoke PASS (40 y, 485 goats). H5 seed 1 × 600 y rerun from main is identical to the
exp/gather-hunt run apart from wall-clock time. Economy-off check (2 seeds × 600 y, last 100 y):
H1 wild R 0.87; H3 herds collapse to 2–3 (G13, herderAlarm 0.05); H5 herds 52–66, herd − wild R
−0.12 to −0.18.
**Next:** ranged shot as a hunting-method condition (ungate from `economy`; order against capture);
H5 fodder store on the windows and the 36,000 kcal load; MODEL.md to kcal and the new switches;
EXPLOG conclusions for windows, needScore, kcal, gatherSee, altgame.

## 2026-10-21 — model rebuild (MODEL v2), cold check (v2.1), offtake calibration, condition table
**Done:** Stages 1–3 (wild type, wolves, hunting, learned fear) and 4a–4e (herding, culling, husbandry)
were built 2026-10-18 → 10-20; see the commits ed2d739 → 7b7e356 and DEVPLAN. Today: the rebuild
Chris asked for. Localised and emergent replacements for stand-ins (sub-day ticks, spatial mating,
oestrous cycles, sequential-assessment contests, wolves switching prey on their own success, foragers
with a fodder store, herder labour load, camp-record keep value, capture and retrieval as approach
tests, maternal fear), a reproductive cost of the genome, and lean-season forage quality.
Recalibrated (growth 0.0035, breeding size 0.8). MODEL.md v2 written, then cold-checked by a subagent
against source: 17 discrepancies, 15 omissions, 14 bugs. The largest was that culling never ran
(offtake 0, no cap), so H3 = H2 and H6 = H4. Fixed (b381d31): hunters' gradient counted herd goats;
the index was stale after the herd night; unpenned retrieved strays were not brought in; the herder
spooked at dusk too; kept goats froze in place; rut pull used dawn positions; contest chain ended on a
double death; immigrant wolves kept the old memory; a forager's target was stale; the camp record and
wild-sired share miscounted captured does. Offtake sweep → 10%/y for the table. Keep horizon of 3 y for
does → female Ganj Dareh side in range.
**Changed:** src/world.js, src/animals.js, src/params.js (keepHorizon 3, offtakeRate 0.1),
src/observer.js (forager, captive-leader colours), tools/conditions.json, MODEL.md v2.1, DEVPLAN 4e;
new tools herdcauses.mjs, doestat.mjs, campherds.mjs, cal_offtake.json, cal_horizon.json.
**State:** smoke PASS (40 y, 307 goats). Wild type unchanged by the fixes (2 seeds × 300 y: 350–380
goats, R 0.62, A 0.75, B 0.90, T 0.37). Condition table @ b381d31, 10 seeds × 800 y, final 100 y
(`results/stage4v3`): all persist; herded H2 92, H3 116, H4 22, H5 89, H6 24; herded − wild R −0.02 to
−0.06; Ganj Dareh does past 2.5 y 0.66–0.69 ✓, males dead < 2.5 y 0.30–0.58 (H3 0.58), past 4 y
0.33–0.47 ✗ (target ~0.20).
**Next:** G12 (why penned herds stay small) and G13 (ablate habituation to see whether the filters
act on learned fear rather than R), then G9 (doe reproductive senescence) and the Stage 4 close.

## 2026-10-21 (later) — why herd R rose after the cold check
**Done:** H5 herd R was ~0.3 before the fixes, ~0.83 after. H5 with offtake 0 on fixed code: 0.69–0.84
(10 seeds), so not culling. Bisected the 12 fixes singly on 7b7e356 (H5, 2 seeds × 600 y): only B3
(herder spooks at dusk) matters: 0.50 → 0.77, escapes 22 → 6/y. Rate vs timing: `spookAtDusk 1` (new,
same daily chance spread over day + dusk) gives 0.67–0.72 and ~21 escapes/y (3 seeds). Timing drives it:
a goat spooked on the walk home is still out at the nightly stray test.
**Changed:** src/animals.js, src/params.js (`spookAtDusk`, default 0); MODEL G13.
**State:** smoke PASS. Wild R also rises under hunting (0.62 → 0.86 by y400), so herds start reactive.
**Next:** decide with Chris whether the nightly stray test should be replaced by retrieval when a goat
strays (any sub-tick), which would make day spooks count too.

## 2026-10-21 (later still) — refetching run-offs
**Done:** with Chris: a spook that carries a goat away needs the herder to refetch it. Built
`World.refetch` (approach test over the distance when a spooked goat is beyond keepRadius; lost if it
bolts) behind `refetchRunOffs`. At herderAlarm 0.05 it collapses herds (H3 3, H5 24; 3 seeds × 600 y).
Spook-rate sweep with refetch: H5 holds 79–90 goats at 0.005–0.02, and herd R separates from wild only
at 0.02 (0.74 vs 0.84, 19 run-offs lost/y); H3 shrinks at every rate (57 at 0.005). Full numbers in
MODEL G13.
**Changed:** src/world.js (`refetch`, ys.runOffLost, ys.refetched), src/animals.js, src/params.js
(`refetchRunOffs` default 0), src/datamanager.js; tools/cal_refetch.json, tools/cal_alarm.json.
**State:** smoke PASS; the condition table (stage4v3) is still the refetch-off model.
**Next:** Chris to choose the herder's spook rate and whether refetch keeps the hunter's stalk test.

## 2026-10-22 — spook-rate sweep with refetch
**Done:** H3/H4/H5 × refetch off + herderAlarm 0.002–0.05 with refetch, 4 seeds × 800 y (84 runs,
`tools/sweep_spook.json`, `results/sweep_spook`). H5's herd − wild R gap grows with the spook rate to
−0.24 at 0.03 (herds still 77), then the herd shrinks (44 at 0.05). Generations since capture fall as
the rate rises (10 → 3.5), so the high-rate gap is mostly retention sorting. H3 collapses from 0.01;
H4 is unaffected (small herds, gap −0.02). Numbers in MODEL G13.
**State:** smoke PASS (unchanged code). Defaults unchanged (refetch off, herderAlarm 0.05).
**Next:** choose a spook rate with Chris; separate sorting from in-herd evolution (R of herd-born vs
captured goats).

## 2026-10-23 — what makes the herd R gap, and why penned herds stay small
**Done:** new probes `tools/filters.mjs` (R at each gate in and out of the herd) and
`tools/kidfate.mjs` (a herd's books per goat-year). G12 solved: penned herds without fodder are
food-limited by the daily commute (H4 + fodder: 22 → 87 goats; wider range makes it worse). G13: at
spook rate 0.02 the herd − wild R gap is heritable selection by retention (herd-born 0.69 < captured
0.73; kids = parents); ~61% of captures are habituated escapees coming back, which partly closes the
herd's lineage pool; the capture filter proper is −0.04. Recycling through a low-R near-camp wild pool
was tested and rejected (near-camp wild 0.833 ≈ all wild). H4 + fodder alone reproduces H5's gap
(−0.17 vs −0.19).
**Changed:** MODEL G12, G13; new tools filters.mjs, kidfate.mjs, cal_h4prov.json. No model code changed.
**State:** defaults unchanged (refetch off, herderAlarm 0.05); the stage4v3 table is the refetch-off model.
**Next:** with Chris: adopt refetch and pick a spook rate (0.01–0.03 gives H5 gaps −0.10 to −0.24); then
rerun the condition table; then G9 (old does) and the Stage 4 close.

## 2026-10-23 (later) — hunting raises R; crepuscular wolves
**Done:** Diagnosed why wild R now rises under hunting (0.62 → ~0.86; Stage 3 had it neutral):
`tools/huntsel.mjs` on old (6113dcf) and new code. Since the sub-tick rebuild goats see a hunter arrive
and flee before he attempts, so hunters reach low-R goats (reach R 0.06–0.08 below population; before:
equal). Old model had the reverse asymmetry (goats dodged wolves in real time, hunters a day late).
With Chris: dawn sub-ticks (herds walk out), wolves hunt in every dusk/night/dawn sub-tick until fed,
goats flee wolves in real time by the same rule as hunters.
**Changed:** src/world.js (`dawnSub`, `wolfTick`, `wolfAttack`, `buildWolfField(hunting)`),
src/animals.js (goats flee at dawn/dusk/night; herd goats follow the herder out at dawn), src/params.js
(`dawnSteps` 4; wolfAttempts unused); MODEL v2.2.
**State:** smoke PASS (~990 ticks/s, half the old speed). H0/H1 × 10 seeds × 500 y (`results/crep1`),
years 400–500, new vs old: H0 goats 499 vs 379, R 0.66 vs 0.61, S 0.31 vs 0.41, predation 26 vs 55/y,
starvation 40 vs 8/y, first kidding 2.85 vs 2.64 y, in groups ≥ 5 0.78–0.87 vs 0.88; H1 R 0.85 vs 0.87,
predation 4 vs 23/y, hunted 19 vs 12/y.
**Next:** report to Chris; recalibrate predation (goats now food-limited, S fell) only on his say.

## 2026-10-23 (evening) — the camp economy (first build)
**Done:** with Chris, a camp economy behind `economy` (off by default; notes/human-economy.md). Stores in
fu: plant food/fodder (people get plantValue of it), meat (loses meatDecay of its nutrition a day),
the herd (stock = meatYield × size). Nightly sink: people × need + groupSink, from meat, then plants,
then slaughter by keep value. Returns per labour-day: gather = plantValue × fu delivered, hunt = meat
fu, herd = (offtake + Δ stock + meatDecay × stock) per herder. Each person picks a role at dawn in
proportion to the camp's decaying return estimates (returnTau 30 d) with a random floor (roleFloor
0.1), after Marriott & Gershenson 2011. Several herders per camp share the load. Fix in passing: an
unpenned herd's position is now remembered by the camp, so a stand-in herder finds it (before, a
substitute herder started at camp); verified as the only change to the non-economy path (penned run
bit-identical to HEAD; unpenned identical once the old code got the same camp memory).
**State:** smoke PASS. Sanity runs, seed 1, humans from year 0, 60 y: E0 (gather only) feeds 39% of
demand (gather return ~2 fu/day < need 2.5); E1 hunting starts at 2.2 fu/day, crashes goats 441 → 66,
returns fall to ~0.5 and labour shifts to gathering (hunting share 0.39 → 0.05–0.25), goats recover;
E2 never builds a herd: demand is always unmet, so every captive is slaughtered the night it arrives
(herding's return, when measured, 8–42 fu/day).
**Next:** calibrate yields against need with Chris (a worker should out-produce their own need).

## 2026-10-23 (night) — economy calibration, wolves' memory, herd predation
**Done:** E1 plantValue sweep (3 seeds, years 400–500): 0.5 → 24% of demand unmet, 0.75 → 5%, 1.0 → 0%
(surplus spoils); hunting pays ~0.9 fu/hunter-day (≈3% of food) yet takes 14–17% of labour (matching +
floor) and still drives wild R to 0.82. E1 settles (no cycles): goats ~440, hunting ~15% of labour.
Wolf memory (`tools/wolfmem.mjs`): wolves flip in and out of goats constantly (~1 recovery per wolf per
3–4 y), but under hunting the guild drifts off goats (memory s 0.17 → 0.07; kills −80% for −25% goats),
probably because reactive goats flee before the attack and count as unseen. Selection on R now
(`huntsel.mjs`, crepuscular code): wolf-killed −0.04 vs population, starved +0.02; in H0 the two
balance (starvation ≈ 2× predation), hunting adds kills and eases starvation, so R climbs.
E2 economy (plantValue 0.75/1.0): herds stay at 2–6 goats; wolves kill 0.3 per goat-year, kid
survival 0.56. Fixed-policy H4 + fodder on the current code: predation 0.07–0.13 (was 0.008 before the
crepuscular change), herds 18–44 (was 87); with guarding 0.003 and 88. Crepuscular wolves catch herds
walking out and home; guarding becomes necessary.
**Next:** with Chris: guarding as part of herding or a separate role; credit for captures.

## 2026-10-24 — herding sub-roles; gatherers spread out; 10 people per camp
**Done:** with Chris: hunters only hunt; herding (available once herding is allowed, herd or not) splits
into keeper (leads, keeps together, strays; herder load counts keepers), guard (protects herd goats
within 1 cell; replaces the global guarding switch in the economy), feeder (carries up to feedCapacity
40 fu/day of fodder to the herd; no feeding without feeders) and capturer (walks out like a hunter, takes
goats alive only). Camp-level priority allocation: first herder keeps; each further herder takes the
task with the largest decaying signal ÷ (1 + already on it) (keep: fu run off or straying; guard: fu
attacked by wolves; feed: fodder wanted; capture: fu captured per capturer-day), roleFloor random.
Gatherers now claim distinct cells for the day and move on when a spot is spent (all modes).
**State:** smoke PASS. 10 people/camp, 3 seeds, years 500–600: E1 unmet 37/25/9% at plantValue
0.75/1.0/1.5 (gather return 3.9/5.2/7.4 fu/day vs 8.9 at 5 people, pv 1.0: the 4-cell gathering area
runs out); E2 at pv 1.0/1.5: herds 0/2–3 goats, captives eaten as they come (captures 3.6–4.4 ≈ culls);
tasks spread k/g/f/c 0.16/0.19/0.22/0.43 at pv 1.5. Hunting holds 23–26% of labour at 0.3 fu/day,
more than its return explains (not yet checked; possibly lean-season gathering slumps).
**Next:** with Chris: how to give the camp a surplus (wider gathering range, plant value, group sink).

## 2026-10-24 (later) — gatherers weigh distance against lushness; group sink 0; herding return bug
**Done:** gatherers claim the unclaimed cell (within a day's walk, forageRange 6) with the best
min(load room, forageCut × sub-ticks left after walking, what it holds); re-choose when a spot is spent.
groupSink default 0 (with Chris: add it only to drive offtake once herds are robust). Bug fixed:
herding's daily return was the camp total, not ÷ herders (overstated it by the crew size).
**State:** smoke PASS. 10 people/camp, 3 seeds, years 500–600: E1 unmet 2% / 0% at plantValue 0.75 /
1.0 (gather 4.1 / 5.4 fu/day; fodder surplus 3,300 / 8,000 fu at year end; hunting 14–15% of labour at
0.4–0.5 fu/day). E2 at pv 1.0: herding 31% of labour at 3.0 fu/herder-day (gather 7.0), herds ~14 goats
(4–31), tasks keep/guard/feed/capture 0.32/0.27/0.36/0.05. Herd books (2 seeds, years 500–560):
predation 0.05 per goat-year (guards work), but culls 0.12–0.15, starvation 0.05–0.09, births only
0.20–0.22 per goat-year (0.49–0.65 per doe-year): herds hold, they do not grow.
**Next:** why herd goats starve with fodder in store; when the small shortfalls that eat the herd occur.

## 2026-10-24 (evening) — what limits herd size in the economy
**Done:** `tools/econprobe.mjs`. Herd starvation was a feeding gap (98–100% on days with no feeder,
90% lean season, fodder in store): the feed signal (a day's ration) was on a different scale from guard
and keep (a whole goat at risk). Feed signal is now the fu value of hungry herd goats (reserve below
growCondition), so all three count goats at risk. Starvation → 0. Remaining limiter: shortfall
slaughters, all in the first quarter of the year (late lean, early growth) with meat and plant stores
empty: the herd eats the stored fodder through the lean season, then people eat the herd.
**State:** smoke PASS. E2, 10 people/camp, 3 seeds, years 500–600, herd size against plantValue: 0.75
→ 3, 1.0 → 19 (15–24), 1.25 → 37 (32–46), 1.5 → 54 (50–62); herding share 0.14 → 0.44, herd births 0.2
→ 20/y, slaughter 3 → 8/y (offtake emerges). Herd size is set by the economy's surplus. Herd R ≈ wild
(0.78–0.80 vs 0.81–0.83): no R signal with refetch off.
**Next:** with Chris: choose the surplus calibration; then domestication signals (refetch, spook rate).

## 2026-10-24 (night) — loose run-offs
**Done:** with Chris: a run-off between "always comes back" and "always needs fetching"
(`refetchRunOffs` 2, now the default). A goat spooked beyond keepRadius is loose: still the herd's, but
moving as a wild goat (its gregariousness may bring it back); it rejoins if it comes within keepRadius of
the herd's leader; each keeper makes one approach-test attempt per sub-tick on the nearest loose goat
loose for ≥ chaseDelay (2) sub-ticks; anything still loose at dusk gets the night stray test. First
build chased in the same sub-tick (0% self-rejoin); the delay fixed that. Counters ranOff, rejoined.
**State:** smoke PASS. 3 seeds × 600 y, final 100 y: fate of run-offs ~20% rejoin, 53–59% refetched,
15–24% lost on the chase. Fixed-policy H5: herd 100 / 58 / 92 and R gap −0.05 / −0.13 / −0.09 (off /
spook 0.05 / 0.02). Economy E2 pv 1.5: herd 21 / 54, R gap −0.06 / −0.09 (spook 0.05 / 0.02; seeds −0.08
to −0.12 at 0.02); pv 1.0: herds 10–15, gap −0.04. S gap ≈ 0 everywhere (no selection on S yet).
Runs take ~16 min each at 19 parallel since the crepuscular change.
**Next:** with Chris: surplus and spook-rate calibration for the economy; why S is not selected.

## 2026-10-25 — plantValue 1; the gathering rate does not make a surplus
**Done:** plantValue default 1 (with Chris: a unit of vegetation is worth no more to people than to
goats; raise the gathering rate instead). Sweep, 10 people/camp, 3 seeds, years 500–600: forageCut/
forageLoad ×1.5 (6/30) and ×2 (8/40). E1: gather return 5.8 / 6.0 fu/day (5.4 at ×1): supply-limited, the
day's-walk area regrows no faster. E2 (loose run-offs): herds 16 / 13 (×1.5, spook 0.02 / 0.05) and
10 / 7 (×2), R gap −0.02 to −0.05: faster cutting strips the pasture the penned herd needs.
**State:** smoke PASS. With one plant resource, human gathering and the herd compete for the same grass.
**Next:** with Chris: a separate human plant food (not eaten by goats), fodder cut by feeders.

## 2026-10-25 (later) — a second resource: human plant food
**Done:** with Chris: human plant food that goats don't eat (economy only): `foodPatches` patches of sites
(radius 2, fill 0.5), site capacity foodSiteK 800 × lognormal(0.5), a yearly masting factor per patch
(lognormal 0.6), fruiting window day 150 ± 45, rot 3%/day outside it, camp store spoils 0.3%/day.
Gatherers harvest it (claiming sites, distance vs yield); feeders cut vegetation as fodder; people eat
meat, then plant food, then the herd. Design notes: plant domestication by relocating sites near camp,
deliberate or "dump-heap".
**State:** smoke PASS. 10 people/camp, 3 seeds, years 500–600. Reach is very patchy: 0 to ~31,000 fu/y
within a day's walk of a camp (need 9,000). E1: unmet 45% (60 patches; seeds 9/53/72%) and 17% (120;
seeds 5/23/23%), masting moves a camp's shortfall 0–21% between decades; hunting share 0.30–0.41, wild R
0.89. E2 (120 patches): herds 22–27 in the rich seed, 1 in the others (chronic shortfall eats them);
R gap −0.03.
**Next:** with Chris: place food by wetness (riparian), and whether a shortfall may eat breeding stock.

## 2026-10-25 (evening) — plant food placed by wetness
**Done:** patch centres drawn in proportion to cell wetness (denser in the valley, where camps are);
capacity unchanged. Within reach of a camp: 60 patches 2,000–39,000 fu/y, 120 patches 22,000–56,000
(need 9,000 at 10 people).
**State:** smoke PASS. 3 seeds, years 500–600: E1 unmet 25% (60 patches; seeds 3/40/34) and 2% (120;
0/4/2). E2 (spook 0.02, loose run-offs): 60 patches herds 1–11, unmet 26%; 120 patches herds 10–37
(19), unmet 3%, herding 39% of labour (tasks keep/guard/feed/capture 0.32/0.42/0.11/0.15), fodder cut
6,000 fu/y, R gap −0.02 to −0.04.
**Next:** with Chris: the spoilage cascade (store → slop fodder → dump heap seeding sites).

## 2026-10-25 (night) — the spoilage cascade
**Done:** with Chris: human plant store → slop → dump heap. Spoiled plant food becomes goat fodder
(slopValue 1), eaten before cut fodder; spoiling slop goes on the dump heap, where each fu seeds a new
food site within heapRadius 2 of camp with chance heapSeed 0.002 (its own patch, own masting).
foodPatches default 120.
**State:** smoke PASS. 3 seeds × 800 y, years 700–800. E2 (spook 0.02, loose run-offs): herds 115 / 62 /
90 (vs 10–37 without the cascade), R gap −0.17 / −0.05 / −0.10, herding ~60% of labour, slop 12,000–
15,000 fu/y, fodder fed 9,000–21,000 fu/y, slaughter 9–13/y, unmet ~0%. E1: slop 30,000–37,000 fu/y,
all to the heap. Near-camp sites (radius 2): 3–19 at year 300, saturated at 19–20 per camp by year 500
in both E1 and E2 (the heap fills every free cell within ~200 y of humans arriving): heapSeed too high.
**Next:** with Chris: dump-heap rate (slower), and separating slop's effect from the gardens'.

## 2026-10-25 (late) — heap rate; land competition and crop damage
**Done:** heap-rate calibration (3 seeds × 800 y, years 700–800): heap off (slop only) herds 19, R gap
−0.03, slop mostly uneaten; heapSeed 1e-4 / 3e-4 herds 86 / 89, R gap −0.11 / −0.08. Gardens, not slop,
drive herd growth (they make plant food reliable: unmet 2.7% → 0.1%, so nothing eats the herd; a big
herd then eats the slop). Near-camp sites saturate (56–59, every free cell within radius 2) within
~100 y even at 1e-4. Added land competition (siteGrass 0.5) and crop damage (cropDamage 1: goats on a
food site eat the plant food first and seek it out). MODEL.md v2.3 documents the economy (§7.12,
C67–C77, C56a).
**State:** smoke PASS. heapSeed 2e-5 builds gardens over centuries (24–36 → 49–56 near-camp sites by
year 800). With crop damage on, wild goats eat 120,000–130,000 fu/y of plant food map-wide (4× what
people gather) and the goat population doubles (514 → 1,041); herds 115 / 52 (heap 2e-5 / 0); R gap
−0.03 to −0.04 (vs −0.05 without crop damage).
**Next:** with Chris: crop damage only on cultivated (near-camp) sites, or at a reduced rate.

## 2026-10-26 — backed off: food sites redrawn each year, cascade without heaps
**Done:** with Chris: food sites redrawn every year (day 0) from the same distribution (wetness-weighted
patch centres, capacity lognormal, masting), none persist (`foodReplace` 1); spoilage cascade kept
(plant store → slop) but no dump heap (heapSeed 0); crop damage and land competition off (switches kept).
**State:** smoke PASS. 3 seeds × 800 y, years 700–800: E1 unmet 2.4% (worst year 21%), gather 5.8
fu/day, hunting 27% of labour, wild R 0.89. E2 (spook 0.02): herds 7–8 goats, R gap −0.02, unmet 3.8%
(worst year 22%), slop 16,800 fu/y but only ~400 fed (no herd to eat it), slaughter 3.3/y: bad years
eat the herd before it can grow.
**Next:** with Chris: whether a shortfall may eat the breeding stock (keep a breeding core).

## 2026-10-25 (EXPLOG) — experiment ledger started
**Done:** with Chris: `EXPLOG.md` in RLLayers' format and protocol (pre-register settings before a run;
raw results only after; conclusions separately). Backfilled a RETROSPECTIVE block of 24 batch trials
(plus probe runs and pre-rebuild folders), each with launch time, code commit, settings file, results
folder, raw table and status (current / historic / invalid: stage4v2, econ_e2 and econ_p10 E2 invalid).
New `tools/trial_summary.py` prints a trial's raw table from its folder. CLAUDE.md read-first list and
`~/.claude/conventions.md` (optional add-ons) now name EXPLOG. Correction: the entry below headed
2026-10-26 was written on 2026-10-25 (left as written: append-only).
**State:** smoke PASS. No model change.
**Next:** pre-register the breeding-core question in EXPLOG before running it.

<!-- append new entries above this line -->

## 2026-10-18 — scaffolded
**Done:** project scaffolded from engine v2 — vanilla-JS canvas microframework with
model/view split, the vendored standard DB client, a headless `runner.mjs`, and `smoketest.mjs`.
**Changed:** initial file tree.
**State:** runs (demo drifters model, in-browser + headless); `smoketest.mjs` passes.
**Next:** replace the demo model with the real Animal Domestication dynamics (DEVPLAN Stage 1).
