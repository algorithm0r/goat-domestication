# Review of tools/capfear_tab.py at b7585bb, the exp021 scorer (2026-11-27)

On tools/capfear_tab.py at b7585bb, checked against exp021 as registered: 1acdee5 as amended by 7b0346a, with my
fe2f739 notes. Also on analysis's outputs in results/exp021_capture-fear/analysis/. The imports, load_tab, flow_tab and
split_tab, are unchanged by this commit. I read no exp021 outcome, and ran nothing that prints one.

**Reproduction.** Through cpuslot, at b7585bb, I reran:
- selftest, and selftest --bad weight, sign, unest, few and wild;
- --checks on the 32 runs, and --checks --bad hiafter and params;
- the full run with stdout discarded.

All ten outputs are identical to analysis's, apart from line endings:
- each selftest bad case fails;
- each data bad case stops the tool;
- the full run exits 0 with empty stderr.

**The runs.** I read only each run's parameters and year labels.
- All 32 have the seed their file name gives, and rows for years 2-3998.
- That gives 267 rows in 3201-4000 and 200 in 401-1000.
- Every row has the exp021 counters.
- The settings the tool doesn't check agree in all 32: captureFear 0.35, tetherNew 1, penning 1, alarmSpread 0,
  alarmLearn 0, economy 0, forgetRate 0.002, habAdult 0.02, kidShelter 1 and logLedger 0.

**The code against the registration.**
- **Established** (line 195) is `herd >= 100 and gap`, the same test as load_tab.summary (load_tab.py:81). The arm
  table and the predictions count the same seeds.
- **P1** (113-125, verdict at 234). CAPTAME against REFc:
  - csire must rise by at least 0.05 and the R gap by at least 0.20;
  - an unestablished CAPTAME seed counts against;
  - the verdict needs 6 or more of 8 seeds.
  This is 7b0346a point 3.
- **P2** (127-138):
  - It is not read if CAPWILD is established in 2 or fewer seeds.
  - Otherwise it reads the seeds established in both arms, with csire down by 0.05 or more and the R gap down by 0.20 or
    more, and holds at 6 or more of them.
  - The signs are right.
- **The reading rule** (243-246) is LOAD05c's capturedHi over captured over 3201-4000, held strictly below 0.5. That is
  "fewer than half of captives". The orphan share is printed beside it (fe2f739 note 1).
- **The pooled shares** (86-109):
  - capturedFear is weighted by captured. The row field is the year's mean over its captives (datamanager.js:169),
    rounded to 4 decimals, so the reconstruction is exact to that rounding.
  - capturedFearOrphan is weighted by orphans in the same way (170).
- **Wild fear** (78-84) is the registered formula on the fields settled in ca1b186 point 5.
- **P3** prints capturedFear for LOAD05c and REFc over 401-1000 and 3201-4000, per arm and per seed.
- **The checks** (56-76) stop on:
  - the wrong arm parameters;
  - a counter above captured;
  - capturedHiAfter ≠ capturedHi with the switch off;
  - capturedHiAfter ≠ 0 in CAPTAME.
  --bad hiafter now trips the equality, not the bound.

**On analysis's six reading choices:**
1. **Established is load_tab's.** Accepted. It is what exp010's predictions were read on.
2. **An unestablished REFc seed can't hold.** Accepted. With 6 or more of 8 required, a seed read out can't hold either,
   so the verdict is the same. In any case, every REF and LOAD05 seed is established over 3201-4000 (EXPLOG line 7550),
   and REFc and LOAD05c reproduce those runs (be9e46a).
3. **P2 is read literally as 6 or more seeds.** Accepted for the count. The label is point 1 below.
4. **The rule's share is a ratio of sums.** Accepted. That is what "fewer than half of captives" means.
5. **The thresholds are inclusive.** Accepted, since the text says "by 0.20 or more".
6. **Wild fear is an unweighted mean over rows,** and breadth is taken over the established seeds. Accepted, since both
   are descriptive. The scored text should say that wild fear is unweighted.

## 1. CAPWILD established in 3 to 5 seeds is not registered (moderate)
**The registration covers two cases:**
- With 2 or fewer established, P2 is not read, and the outcome is "naive captives prevent a herd at load 0.5". That is
  a reading in H's direction.
- With 6 or more read, P2 holds or fails on the cells.

**Between them.** LOAD05c is established in all 8 seeds (choice 2 above), so the seeds read are CAPWILD's established
seeds. With 3 to 5 of them, 6 cannot be met. The tool then prints "fails (only n read, so 6 cannot be met)" (line 252).
- That follows the text literally.
- But in this range, a "fails" is in part the establishment loss that the ≤ 2 case reads in H's direction.
- Under the decision rule it would still count as P2 not holding.

**Fix, the steward's, before the scored output is read:** register what 3 to 5 established CAPWILD seeds means. For
example: "P2 not read; the establishment count reported, as in the ≤ 2 case, without its reading".
- The tool should then print that label.
- If the steward keeps "fails", the scored text should give the establishment count beside it, and should not read the
  result against H without saying so.

## 2. The 6-seed edge is never exercised (minor)
**What the selftest covers.** P1 is planted at 5 of 8, and P2 at "not read" and at 5 of 6. No planted case reaches 6
holding, so a `> 6` or `>= 7` would pass the selftest.

**P1's verdict lies outside p1().** It is the `k >= 6` at line 234, which the selftest never calls.

The reading rule's 0.5 edge is not planted either.

**Fix:**
- Move P1's verdict into p1().
- Plant a case with exactly 6 holding for P1, and one for P2 with 6 read, each of which must print "holds".
- Plant the rule's share at exactly 0.5, which must not be read against H.

## 3. The counters are a one-in-three sample of the years (minor)
**The runs record every third year,** so each sum covers the recorded rows only: 267 of the window's 800 years, and 200
of the early window's 600.
- The shares are ratios over the same rows, so they estimate the all-year shares.
- tethered per herd goat is goat-nights per herd goat per recorded year.
- No count of captives should be quoted as the window's total.

**Fix:** one line in the tool's output, and in the scored text, saying the shares are over the recorded rows.

## 4. The header promises a window list that isn't printed (minor)
**The header.** Line 39 says "--checks runs only these and the window list".

**The code.** No window list is printed in either mode.

**Fix:** either drop the words, or print the rows per window, which point 3 asks for.

## Verdict
**capfear_tab at b7585bb is faithful to exp021 as registered.**
- The rules, signs and thresholds match 7b0346a.
- Both fe2f739 notes are in.
- The checks and bad cases reproduce exactly.
- Each selftest bad case can fail.

**Before the scored run:**
- **Point 1:** the steward registers the 3-5 case.
- **Point 2:** the selftest gains the 6-seed and 0.5 edges.

Points 3 and 4 are minor. None of them changes the code that computes a verdict. Once points 1 and 2 are in, analysis
may run the scored command.
