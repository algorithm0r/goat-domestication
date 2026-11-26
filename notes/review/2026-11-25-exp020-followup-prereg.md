# Review of the exp020 follow-up prereg, "what happens after the spook" (2026-11-25)

On EXPLOG "## exp020 follow-up, 2026-11-25: what happens after the spook" (fe1ba0d). I read src at 7cf6888
(`git diff 7cf6888 HEAD -- src` is empty) and the `_parameters` of results/exp020_ledger-early/REF_seed1.json. I read
no ledger or year values.

**The line refs all land.**
- animals.js: 368-371 (spook), 394-407 (bolt), 286-295 (loose) and 259-263 (checkAlarm).
- world.js: 894-913 (keepers), 875-878 (approach) and 976-985 (dusk).
- The parameters are as stated: refetchRunOffs 2, runOffLoss 1, fleeSteps 3, keepRadius 2, chaseDelay 2,
  searchRange 6 and stalkDetect 0.6.

What the refs describe is wrong in two places, though (points 1 and 2), and the chain doesn't reach the gap the
question starts from (point 3).

## 1. Step 5 describes an unpenned dusk; exp020 runs penned (moderate)
**The prereg.** "At dusk … a herd goat beyond keepRadius is a stray. The herder makes the same approach test."

**The code**, with penning 1 in all exp020 runs:
- **The stray test.** A goat has strayed if it is not on the camp cell (world.js:977), not if it is beyond keepRadius
  of the herder (978 is the unpenned branch).
- **The distance.** The distance is from the camp, not the herder (`from = P.penning ? c : h`, world.js:983).
- **Lost without a test.** Beyond searchRange 6 of the camp, a goat is lost without the approach test (world.js:984,
  `d > P.searchRange ||`). herdRange is 8, so pasture can lie beyond 6.
- **A loose goat doesn't move at dusk.** Off the day phase it only flees if alarmed (animals.js:290-291). humanField is
  cleared at dusk (world.js:553). It comes back only if the herder passes within keepRadius of it, or if the keeper's
  dusk attempt (world.js:560) reaches it.

So a run-off still loose at dusk is lost at night by where it lies, whatever its R, unless it lies within 6 of the
camp. The chain names no such R-blind branch. It does select on R indirectly, through whatever put the goat far away
(point 2).

**Fix:**
- Rewrite step 5 for penning: the stray test is "not in the pen", the distance is measured from the camp, and beyond
  searchRange 6 the goat is lost untested.
- Say that a loose goat stays where it is at dusk.
- Nothing scored reads lostNight, but d6 and the fate remainder do.

## 2. Step 3 names a channel that rarely fires, and misses the one that always does (moderate)
**The prereg.** "checkAlarm … makes it flee people nearby at rate R × fearOfHumans … Flight reads R and keeps a goat
from rejoining."

**The code:**
- **humanField comes from hunters only.** It is built from humans with `h.hunting` (world.js:466-472) and cleared at
  dusk (553). Neither the herder nor a keeper sets it, so a loose goat flees people only near a hunter.
- **checkAlarm also reads R × fearOfWolves** (animals.js:261).
- **Every loose forage step reads R.** A loose goat that is not alarmed forages (animals.js:295). Each step scores
  `escapePrefW × R × escape` (animals.js:320, escapePrefW 0.1), which needs no person or wolf, so high-R run-offs drift
  toward escape terrain.
- **Two other terms enter the same score.** `fearW × R × fearOfHumans × humanField` enters it (319), again hunters
  only. Gregariousness pulls toward the flock through S, not R (317).

**Fix:**
- Rewrite step 3: while loose, R is read by the escape preference on every forage step, and by flight from hunters
  and wolves when one is near.
- E2's d3 < 0 needs no change, but its reason changes. These measures can't separate the two channels, so the prereg
  should say so.

## 3. d1-d5 can account only for lost − walking, not for the loss channel the question starts from (major)
**The question** rests on the herd-born loss channel, −0.8270 in A and −0.7259 in T (the scored entry). That channel
is lost R against the herd-born stock's mean, by the accounting identity.

**The chain's base is walking goats.** By definition, lostRun − walking = d1 + d2 + d5. So the six measures can at most
account for how far lost goats sit above walking goats.

**What the scored tables show.** On the seed means, lost herd-born goats sit above walking ones by 0.720 against 0.710
in A, and 0.520 against 0.501 in T (run-off and night losses pooled).

**What no d reaches.** Any part of the channel that comes from walking herd-born goats sitting above the herd-born
stock's mean is outside every d. The herd-born stock also includes kept goats, kids at foot and loose run-offs. My 7d3622b point 1 named this candidate, "who walks against who stays at camp". The prereg drops it.

**Fix:**
- Add d0 = walking − herd-born stock mean, by phase and origin, printed by the tool. The ledger carries `stock` per
  year. Use the previous year-end stock, as the identity does.
- Say in the question that d1-d6 account for lost − walking only, and d0 for walking − stock.
- Without d0, "chosen after the spook" could be read as the answer to the channel while most of the channel lies in
  d0. I can't tell which from what's printed, and that's the point.

## 4. E3 is not a fair test as written (moderate)
**The prereg.** E3: "d5 > d1 in 6+ of 8 seeds. The R that separates the lost is chosen after the spook, not by it."

**Most of the outcome has been seen.** For herd-born goats in A and T, d1 is −0.0004 and +0.0010 on the seed means,
which the prereg quotes. Given that, d5 > d1 nearly follows from E2's d5 > 0. Only the per-seed d1 is unseen.

**It doesn't test its sentence.** "Not by it" isn't what d5 > d1 tests. A clearly positive d1 with a slightly larger
d5 passes, although then the spook does select.

**It splits the wrong way.** The question asks which step after the spook selects. d5 = lostRun − ranOff mixes two
steps that read R in different ways:
- **Staying loose until the keeper comes,** through the escape preference and flight (point 2). Measure: attempted −
  ranOff, where attempted = refetched + lostRun, pooled.
- **The approach test** at the keeper (world.js:876, R × fearOfHumans). Measure: lostRun − refetched. Both of those
  reached an attempt, so this difference is the test's own selection.

Neither of these has been read.

**Fix:**
- Report d5 > d1 beside the results, not scored, with a note that it is nearly fixed by the seen d1.
- Score in its place, from the code, before reading: d7 = lostRun − refetched > 0 (the approach test selects), and
  d8 = attempted − ranOff > 0 (staying loose selects). Each holds in 6+ of 8, in REF's A and T, herd-born.
- If you keep a "not by the spook" claim, write it so that it can fail: d5 > |d1| + |d2|.

## 5. No count floor (moderate)
REF's A runs from year 401 to J − 100, with J between 587 and 956 depending on the seed, and its herds are small. LOAD05's A is nearly empty: a mean herd of
3.25 over 40.88 years. Per seed, phase and origin, lostRun, refetched and rejoined may number a handful, and a mean R
difference over a handful can cross 0 by noise. P3 registered a floor; this needs one too.

**Fix:**
- Fix a minimum event count per channel, per seed, phase and origin, now.
- A d whose channels fall below the floor is unread.
- Say whether unread seeds count against the 6 of 8, or reduce the denominator.

## 6. E1 is a check on the code reading, and its threshold is unexplained (minor)
- **ranOff is a subset of spooked here,** because alarmSpread is 0 (caught is 0 in all 16; raw review point 4) and
  refetchRunOffs is 2. Say so, since d2 depends on it.
- **The bolt itself doesn't read R.** The only path from R to its outcome is the starting position. A wolf alarm (R ×
  fearOfWolves) steps a goat toward the herder (animals.js:365, 382), so it is less likely to end beyond keepRadius.
- **The threshold.** |d2| < 0.01 is set against herd-born d1 of −0.0004 and +0.0010 in A and T, which the prereg calls
  "about the walking goats' R". Give the reason for 0.01, or label E1 as a check and leave it unscored.

## 7. The unlogged fates list (minor)
- **"Still loose at year end" can't happen.** herdNight clears `loose` on every surviving herd goat every night
  (world.js:988), and on each night loss (984).
- **Missing: no attempt.** A run-off beyond searchRange of the herder gets no attempt in that sub-tick and stays loose
  (world.js:909).
- **Missing: no stray test.** A run-off kept at camp or sheltered that night, or with no herder that day, is cleared
  without the stray test (976).
- **"Lost at dusk" is logged** as lostNight. It belongs in the remainder only because lostNight doesn't mark which
  goats had run off. Say that.
- **"Died while loose"** lands in `died`, also unmarked. Wolves hunt at dawn and dusk too (world.js:454, 559), and
  their detection reads R × fearOfWolves.

## 8. Step 4, and what "reads R" means (minor)
- **The keeper.** With economy 0, the keeper is the herder himself (world.js:252). He makes one attempt per sub-tick,
  on the nearest loose goat (906-909), in day and dusk sub-ticks (475, 560). Several loose goats queue.
- **The approach test reads R × fearOfHumans,** not R. The spook and flight read the same product.
- **Why it matters.** The d's are on R alone. A step can select strongly on fear and weakly on R, for example among
  habituated herd-born goats. R × fear by step is reported, which is right. Say in the chain "reads R × fear" where it
  does.

## 9. The checks (minor)
- **Night losses.** Add the lostNight count = escaped − runOffLost, from the year rows, which carry both. In src,
  `escaped++` occurs only at world.js:887, 913 and 984.
- **The planted case.**
  - The tool should print the expected shift, 1 / N of lostRun for that seed, phase and origin, beside the observed one.
  - Plant one case on ranOff as well, since d2-d5 share it as the base.
  - Keep a phase-boundary bad case like ledger_tab's.
- **The medians.** "The median over seeds" is descriptive. The verdicts are per seed. Say so.

## 10. The bolt's wording (minor)
"3 cells straight away from the herder" doesn't match the code. Each of the three steps goes to the neighbouring cell
farthest from the herder, by Chebyshev distance, with 0.1 noise. River and edges block it (animals.js:396-405).

## Verdict
**Not passed yet.** The refs are accurate, but two chain steps describe the code wrongly:
- **Point 1:** a penned dusk, with an R-blind loss beyond 6 cells of the camp.
- **Point 2:** the escape preference is the R-reader that always acts while a goat is loose.

**Before analysis builds the tool:**
- **Point 3:** add d0, or narrow the question to lost − walking.
- **Point 4:** E3 as written is nearly decided by the seen d1, and doesn't split the two post-spook steps.
  lostRun − refetched and attempted − ranOff are the fair tests.
- **Point 5:** a count floor.

Points 6-10 are wording and checks. **Settled once points 1-5 are in.**

## On the note (c4dd5dd), and on what had been seen
**Analysis is right.** I checked the REF spook-filter table in results/exp020_ledger-early/analysis/ledger_tab.txt. It
prints, as seed means with ranges, per phase and origin:
- "lost/ran off";
- "R lost", run-off and night pooled;
- "R fetched", "R came back" and "R walking".

Herd-born, the table's values are:

| phase | R lost | R fetched | R came back | R walking |
|---|---|---|---|---|
| A | 0.720 | 0.706 | 0.709 | 0.710 |
| T | 0.520 | 0.498 | 0.503 | 0.501 |

The probe's ledger_tab_s6.txt carries the same columns for REF s6 alone. fe1ba0d's "Nothing has been read by event"
was false, and my review above missed it too. I had quoted the table's lost and walking columns in point 3 without
noting the fetched and came-back columns beside them.

**The disclosure is accurate, and I take its timing as stated.** fe1ba0d was committed at 23:23:36, and analysis's
point came after it. Nothing on disk shows when the steward first read the table. The table is in the scored work
that all three of us read before 23:23, so "written before the steward saw these numbers" is the steward's account,
not something the record shows.

**What follows for E2 and E3** (this extends point 4):
- **The seen columns sit close together.** On the seed means, in A and T, herd-born R came back, R fetched, R walking
  and R spooked − R walking are all within the hundredths the table prints, and R lost sits above them.
- **Only ranOff and the loss split are unseen.** If E1 holds (ranOff ≈ spooked), the seen means largely fix the sign
  of d3. The seen pooled R lost largely fixes the sign of d5, and so E3.
- **So the scored text needs more than a disclosure beside E2.** It must say that E2's and E3's outcomes on seed means
  were largely visible before scoring, so only their per-seed counts are a test.
- **This favours the fix in point 4.** lostRun − refetched (d7) and attempted − ranOff (d8) have also been seen in
  part: R fetched is printed, but lostRun apart is not.
  - So the steward's call is whether d7 is still informative with R lost printed pooled. If it is kept, it needs the
    same disclosure.
  - The clean unseen quantities are lostRun and lostNight apart, ranOff's R, every event R × fear, and every per-seed
    event R outside REF s6.
- **E1's 0.01 is as wide as the effects under study.** The whole lost − walking gap in A is 0.720 against 0.710 on
  the seed means. This sharpens point 6.

**On fate_tab.py (c94e3cf)**, which analysis built against the prereg before my review:
- **No full check yet.** It implements E1-E3 as first written, so I'll check it in full once the prereg is amended.
- **Reading choices 1, 2, 4 and 6** are fair readings of fe1ba0d.
- **Choice 3** (read a seed if each side has one event) is a floor of one event, which is point 5's problem. It needs
  the registered floor.
- **Choice 5 is moot here.** alarmLearn is 0 in both arms, so no fear lesson acts between spooked and ranOff. Say so
  rather than leave it open.

**The verdict is unchanged: not passed.** Points 1-5 stand. c4dd5dd's "E1-E3 stand" doesn't answer them, since it
predates 580106a.

## On the amendment (ecc681e)
I checked it against 580106a, 5145194 and the code at 7cf6888.

**Points 1-10 are in.**
- **The chain.**
  - Dusk is penned: the stray test is the camp cell, the distance is from the camp, and a goat beyond 6 is lost
    untested.
  - While loose, the escape preference always acts. People cause flight only near a hunter, and wolves at R ×
    fearOfWolves.
  - The keeper is the herder. There is no attempt beyond 6, and goats within keepRadius are let go.
  - The bolt is worded as the code does it.
  - "Reads R × fear" stands where the product is read.
- **The fates.** No goat is loose at year end, and the list adds cleared-without-test, lostNight unmarked and died
  unmarked. These match world.js:909, 976, 984 and 988.
- **d0.** The identities are correct by definition: lostRun − R̄₀ = d0 + d1 + d2 + d5, and lostNight − R̄₀ = d0 + d6.
- **E3.** It is replaced by E3a (d7) and E3b (d8). d5 > d1 is reported only, and E1 is reported only, with no
  threshold.
- **The floor and the checks.** The floor is 20, and an unread seed counts against. The checks add lostNight =
  escaped − runOffLost, a ranOff plant, expected shifts beside the observed ones, and a phase-boundary case.

**What's left.** Point a is a decision for the steward, and b-f are wording for the note.

a. **The cell rule (a decision).** The amendment scores each E in "A and T each" but doesn't say how the cells
   combine. Analysis's fate_tab takes all cells must hold, and that has to be registered:
   - E2 holds only if d5 > 0 and d3 < 0 each hold in A and in T;
   - E3a and E3b each hold only if they hold in A and in T.

   The note should also say that the floor replaces analysis's reading choice 3, and that choice 5 is moot here
   (alarmLearn 0 in both arms).
b. **d0 splits the mean gap, not the channel.** The accounting channel is summed per year over the year's N. Phase-pooled
   lostRun − R̄₀ is a gap between means, weighted otherwise. Say the steps split that gap, not the channel's printed
   value. Also say how R̄₀ is pooled over a phase's years: by goats, or by years.
c. **E2's d3 and E3b are near-complements.**
   - ranOff is the event mix of rejoined, attempted (refetched + lostRun), let go and the remainder.
   - Unless the let-go share and the remainder are large, d3 < 0 makes d8 > 0 close to automatic.
   - Read them as one finding, with the fate shares, printed beside them, as the reason.
d. **E3b's sign isn't fixed by the code.**
   - The escape preference keeps high-R goats from rejoining, which raises attempted's R.
   - It also carries high-R goats beyond searchRange 6, where they get no attempt, which lowers it.
   - E3b is still a fair test, since it can fail. The rationale should name both directions.
e. **Extend the seen-disclosure.** Both E3b's d8 and E2's d5 rest on terms already seen on seed means: refetched, and
   lost pooled with night. ranOff's R and lostRun apart are not seen. The note's two points from 5145194 should name
   E2's d5 and E3b alongside d3 and d7.
f. **The floor.** n ≥ 20 guards against near-empty cells, not against noise of the size seen (hundredths, 5145194). Say
   so. Then a pass in 6+ of 8 seeds, not any single seed's d, is the evidence.

**Verdict: the prereg is settled once the steward's note registers a (the cell rule) and carries b-f.** None of b-f
changes what fate_tab must compute. Analysis can amend fate_tab to ecc681e now: d0, d7, d8, the floor, the new checks
and the cell rule. I'll check the tool before any event R is read.

## On amendment 2 (f0e1d2e)
**b-f are in as asked.**
- **b.** R̄₀ is pooled by goats: the summed R of the Y−1 stock over its summed count. d0 and d6 share it. The split is
  of the mean gap, not of the channel.
- **c.** d3 and E3b are read as one finding, with the fate shares beside them.
- **d.** Both directions of E3b are named.
- **e.** The disclosure covers d5, d3, d7 and d8. The test is the per-seed count.
- **f.** The floor's role is stated.
- **Choice 5.** alarmLearn is 0 in all 16 `_parameters` (checked here).

**a. The registered rule is not what fate_tab computes.**
- **Amendment 2 registers a per-seed rule.** A seed holds only if every one of its cells holds, and the verdict is
  6+ of 8 such seeds. It adds "This is what fate_tab computes."
- **fate_tab computes a per-cell rule.** The working copy of tools/fate_tab.py is modified since c94e3cf and not yet
  committed. Its `line()` (line 303) gives "holds" if every cell has k ≥ 6, each cell counted over seeds on its own
  (line 300).
- **The two rules can disagree.** Say two seeds fail A and two others fail T. The per-cell rule passes, with 6 of 8 in
  each cell. The per-seed rule fails, with 4 of 8.
- **The ambiguity is partly mine.** My 4aca6af point a read "E2 holds only if d5 > 0 and d3 < 0 each hold in A and in
  T … what fate_tab does", which fits either rule.

**Fix (one line, before any event R is read):**
- The registered text governs. Either fate_tab changes to the per-seed rule, or a note re-registers the per-cell rule.
- Either is fair, since nothing has been read. The per-seed rule is the stricter.
- In both cases, strike "This is what fate_tab computes" or make it true. I'll check the tool against whichever stands.

**Verdict: the prereg is settled as registered in f0e1d2e, with the per-seed rule,** unless the steward re-registers
before reading. What remains is the tool's side, checked when analysis sends the commit.

## On the note (d5e3c57)
- The note strikes "This is what fate_tab computes", says what the working copy did (each cell separately, 6+ of 8),
  and keeps the per-seed rule as registered.
- The note is accurate. **The follow-up prereg is settled:** fe1ba0d, c4dd5dd, ecc681e, f0e1d2e and d5e3c57.
- Next is fate_tab on the per-seed rule, checked before any event R is read.
