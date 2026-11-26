# Review of the exp020 follow-up's scored text (2026-11-26)

On analysis's draft "## exp020 follow-up results (scored)" (side-session notes, exp020-followup-scored.md), and on
results/exp020_ledger-early/analysis/fate_tab.txt and fate4_bad_ranOff.txt. The scorer is tools/fate_tab.py at
abf22cc. I passed 77fdfa4 in 48aa5c7, and its two later commits are read below. The registration is fe1ba0d, c4dd5dd,
ecc681e, f0e1d2e and d5e3c57.

**The tool since 77fdfa4.**
- **87b7bd5.** E1 is printed with no count, and labelled as struck. The ranOff plant checks d4 too, in the selftest
  and on the data.
- **abf22cc** relabels the stock0 count line, and changes nothing else.

Both are as I asked in 48aa5c7, and the diff touches nothing else.

**Reproduction.** Through cpuslot, I reran the draft's command, `python tools/fate_tab.py results/exp020_ledger-early
REF,LOAD05 --perseed` at abf22cc, and --bad ranOff. Both outputs are identical to fate_tab.txt and
fate4_bad_ranOff.txt, apart from cpuslot's wait lines and line endings. The plant moves d2 by +1/n, and d3, d4, d5 and
d8 by −1/n, with n = 34236.

**The verdicts, against the registered per-seed rule.**
- **E2 fails, 0 of 8.**
  - d5 > 0 holds in 8 of 8 seeds in A and in T.
  - d3 < 0 holds in A only in s3, s4 and s6, and in T only in s1.
- **E3a holds, 8 of 8.**
- **E3b fails, 2 of 8,** holding in s4 and s8. Per cell, A has 4 of 8 and T has 5 of 8.
- **Every cell is read in all 8 seeds.**

These are what fate_tab.txt prints, lines 287-295, and each is computed as registered.

**The numbers.** I checked every figure in the draft against fate_tab.txt:
- the checks;
- the floor and the R̄₀ notes;
- the verdict lines and the per-cell counts;
- the fate ranges, against the per-seed fate line at 296;
- E1's extremes, against the REF d2 column;
- the herd-born step table, against REF d-rows A o1 and T o1;
- the mean R values, and R × fear d4;
- B and C d7 and d1;
- LOAD05's read counts, d7, d5, d3, d8 and d1.

Each figure is where the draft says it is, except the sentence in point 1.

## 1. "d3 not below 0 goes with d8 not above 0" is false in five cells (moderate)
**The draft.** "With the rest about a tenth, amendment 2 c's coupling applies: d3 not below 0 goes with d8 not above 0."

**The per-seed lines** (fate_tab.txt 288 and 294) show d3 ≥ 0 together with d8 > 0:
- in A in s8;
- in T in s2, s4, s7 and s8.

**Why the coupling breaks.** The d's here are in the ten-thousandths, for example d8 −0.0002 and +0.0001 on the
median. The rest, 0.092-0.105 of ranOff, and the let-go goats carry enough R to break the coupling.

**My error.** f0e1d2e c took the coupling from my 4aca6af point c, "d3 < 0 makes d8 > 0 close to automatic". That
overstated it at this scale. I wrote it from the structure of the shares, without a check that could fail.

**Fix:**
- Replace the sentence with "d3 and d8 are both near 0. Their signs differ in A in s8 and in T in s2, s4, s7 and s8,
  so the two failures are not one sign read twice."
- Keep "read as one finding" only as "both say no step before the herder's attempt separates the goats by R".

## 2. What the approach test's separation is made of (moderate)
**The draft.** "The separation comes after the herder reaches a goat. … It is the step that reads R × fear (the approach
test, world.js:875-878)."

**What d7 does show.** Every herd-born goat the herder reaches either passes the approach test (refetched) or bolts
(lostRun), so d7 > 0 does place the separation at the test.

**What it doesn't show.** The test's outcome depends on more than R:
- **R × fear.** The bolt chance per step is stalkDetect × R × fearOfHumans. lostRun logs R only, so these measures
  can't say whether R or fear carries d7.
- **Distance.** The number of steps is the goat's distance from the herder (world.js:912, `approach(best, bd)`).
  Whether lost goats were farther, which the escape preference could bring about through R, is not measured.

**Fix:** one sentence after "the approach test": "Its outcome reads R × fear at each step, over as many steps as the
goat is far away. lostRun logs R only, and distance is not logged, so these measures do not split d7 between R, fear
and distance." For Chris needs the same clause: "the ones that bolt are higher in R" stands as printed, while why they
bolt is not separated.

## 3. Derived counts (minor; the analysis-in-tools rule)
**The draft.** "d3, in 5 of 8 seeds in A and 7 of 8 in T at or above zero."

The tool prints the complements, "A d3<0 3 of 8; T d3<0 1 of 8", not these.

**Fix:** "d3 < 0 in only 3 of 8 seeds in A and 1 of 8 in T".

## 4. d0 is below 0 in every seed (minor)
**The draft.** "Walking goats sit at the herd-born stock's mean (d0)."

d0 is −0.0005 (−0.0017 to −0.0002) in A and −0.0012 (−0.0020 to −0.0003) in T. It is small, but negative in every
seed.

**Fix:** "Walking goats sit slightly below the herd-born stock's mean, in every seed (d0)."

## 5. Two printed results the reading leaves out (minor)
- **The spook selects on R × fear, not on R.**
  - Herd-born d1 in R × fear is +0.0024 (+0.0004 to +0.0037) in A and +0.0016 (+0.0003 to +0.0031) in T, positive in
    every seed.
  - d1 in R is −0.0000 (−0.0119 to +0.0090) and +0.0013 (−0.0084 to +0.0075).
  - So in A and T, the spook takes the more fearful walkers, not the higher-R ones. The draft's "the spooked goats sit
    at the walking goats' R" is true, and incomplete without this.
- **Night losses are outside the answer.**
  - "For Chris" answers for run-off losses (lostRun).
  - Herd-born lostNight is a separate channel. Its median count is 1007 in A against lostRun's 1884, and 1343 in T
    against 1887.
  - Its d6 spans 0 in A and T.

**Fix:**
- Add the R × fear d1 line to the reading.
- In For Chris, say "of the goats lost on the run".
- Say that night losses are not separated by R at this step, as d6 spans 0.

## Verdict
The scoring reproduces byte for byte, and the tool is faithful to the registration as amended. **E2 fails, 0 of 8. E3a
holds, 8 of 8. E3b fails, 2 of 8. Every cell is read in all 8 seeds.**

Before the text goes to EXPLOG:
- **Point 1:** the coupling sentence is false in five cells.
- **Point 2:** what the approach test's separation is made of.
- **Points 3-5:** minor.

None of them moves a verdict. **Settled once points 1-5 are in.**

## On the revision (exp020-followup-scored.md as revised, 2026-11-26)
I checked each change against fate_tab.txt.
- **1.** The coupling sentence is replaced. The five cells, A s8 and T s2, s4, s7 and s8, match lines 288 and 294.
- **2.** The approach-test sentence names R × fear per step, over the steps to the goat (world.js:912). It says d7 is
  not split between R, fear and distance. For Chris carries the same clause.
- **3.** "d3 < 0 in only 3 of 8 seeds in A and 1 of 8 in T", as printed.
- **4.** d0 is "slightly below the herd-born stock's mean, in every seed".
- **5.** d1 in R × fear, +0.0024 (+0.0004 to +0.0037) and +0.0016 (+0.0003 to +0.0031), matches the R × fear table.
  For Chris says "of the goats lost on the run". Night losses are a separate channel, at the printed medians
  1007 / 1884 and 1343 / 1887, with d6 spanning 0.

**The exp020 follow-up's scored text is settled.** The steward may append it to EXPLOG as it stands. The verdicts:
E2 fails, 0 of 8. E3a holds, 8 of 8. E3b fails, 2 of 8.
