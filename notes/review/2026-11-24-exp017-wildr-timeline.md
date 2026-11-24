# Review of "exp017 gene flow: the wild's R in 100-year bins" (exploratory; 2026-11-24)

On EXPLOG 003bf80, tools/wildr_tab.py --timeline (e11a205, 8dcebc8), and
results/exp017_alarm-spread/{wildr_timeline.txt, wildr_timeline_bad.txt}. It is read together with the window entry
(a2eb2d6; my 598a467 and 54f3c87) and gene-flow correction 2 (e0c0ff9, settled in 598a467).

**Reproduction and checks.**
- I reran the entry's command through cpuslot. The output is byte-identical to wildr_timeline.txt.
- The window mode at 8dcebc8 is byte-identical to wildr.txt.
- wildr_timeline_bad.txt shows both bad cases stopping: allgoats on split's identity check, and jcol with "SPR05: 8
  seeds with a J, scored est 7".
- The --timeline code only changes the bins. It goes through the same split, with the identity check on every run and
  the 3201-4000 checks against scored.txt.
- The low is the minimum over the 401-1600 bins (8dcebc8, the `--perseed` branch).
- **The label is right.** The entry says the timeline is exploratory and was added at the steward's request.

**The finding holds in the per-seed lines** (wildr_timeline.txt, lines 123-170):
- **REF.** In all 8 seeds, the wild's R reaches its low in the bin holding J or the next, then rises within one to three
  bins. For example: s3 0.581 then 0.649, 0.694; s7 0.569 then 0.625, 0.702; s6 0.640 then 0.713.
- **LOAD05.** Its seeds fall to a plateau, and their lows sit three to nine bins after J (801-900 to 1401-1500).
- **SPR02.** It dips and returns like REF, a bin or two later.

So the window entry's reading 1 is superseded, and my point 1 on it (54f3c87) is answered.

## 1. "In each seed the later bins are higher than the low" is true by construction (moderate)
The low is each seed's minimum over 401-1600, so every other bin in 401-1600 is at or above it, in any arm. LOAD05's
seeds satisfy the same sentence, and they have no return. As written, the per-seed bullet is not evidence for a
spring-back.

The evidence is the contrast above:
- In REF the low sits at J's bin or the next, and a rise follows within a few bins.
- In LOAD05 the low falls anywhere on a flat plateau, far from J.

**Fix:**
- Replace the sentence with that contrast, quoting REF's and LOAD05's per-seed values from the lines.
- If a number is wanted, have the tool print it per seed for every arm, as a committed number:
  - bins from J to the low;
  - the highest of the next three bins.

## 2. The return is partial, and arms differ in timing more than in whether the wild returns (moderate)
- **REF returns part of the way.** Its all-seed mean returns to 0.732 (1201-1300) and 0.712 (3201-4000), against 0.836
  in 401-500 and the founders' 0.791. Per seed, REF's 3201-4000 values (0.696-0.725) are all below their 401-500
  values (0.789-0.864).
- **The other arms, from all-seed mean low to 3201-4000:**
  - SPR01 0.585 to 0.658;
  - SPR02 0.635 to 0.681;
  - REF 0.670 to 0.712;
  - LOAD05 0.645 to 0.661.

  "Slow and only partly" describes SPR01 well, and REF also returns only partly. What separates REF in the bins is
  how soon the return comes after J. SPR01's mean barely moves over 801-1100 (0.585-0.590), and SPR01 s7 stays on a plateau through 1600.
- **The line for Chris** says the wild "returns within the next few centuries", which reads as a return to where it
  was. Write it as a return part of the way. Replace it with: "In REF the wild's R falls with each herd's establishment
  and recovers part of the way within two or three centuries, while the herd's keeps falling. At the fixed load
  without spreading it falls to a plateau and stays. With spreading at 0.1 the dip is deeper and the recovery comes
  later. At 0.2 the dip and recovery are like REF's, a little later. What drives the recovery is not checked."
- **Small bin-to-bin changes are not readings.** LOAD05's plateau moves by up to about 0.04 within a seed (s1
  0.634-0.675 over 1101-1600), so changes that size in one seed aren't readings, nor is REF's drift from 0.732 to
  0.712 after 1300.

## 3. The wild's baseline is not fixed: humans hunt from year 300 (moderate; the cause is a question)
REF_seed1's parameters have humansAt 300, econHunt 1, stalkDetect 0.6 and shotChance 0: stalk hunting from year 300.
So the founders' window, 301-400, is the wild's first century under hunting, not a settled pre-human wild. The ledger
records that stalk hunting raises the wild's R, because a goat escapes by spotting the hunter (EXPLOG line 643, the
2026-10-30 stalk-vs-shot entry, on older code).

In 401-500 every arm's wild R is 0.827-0.846, above the founders' 0.791, before any herd establishes (all J ≥ 501).
That fits a wild whose R was still being pushed up by hunting through and after the founders' window. If so:
- the rise in reading 6 is not a herding effect;
- the level the wild recovers toward is set by hunting against the herd's outflow, not by the founders.

Neither is checked.

**Fix:**
- In reading 6, name stalk hunting from year 300 as the unchecked candidate.
- Keep "recovers part of the way" in the line for Chris.

**Question:** is there a run on this code with humans but no herding, so that the wild's R after year 400 under hunting
alone can be read? Splitting the founders' window, for example 301-350 against 351-400, would at least show whether the
wild's R was still rising at 400.

## 4. Minor
- **SPR01 and SPR02 are read from all-seed means** that mix seeds before and after J until 901: SPR02 has 4 of 8
  established at 701 and 5 at 801. That is the reason SPR03 and SPR05 are not read. Readings 3 and 4 already quote
  per-seed lows, so rest them on the per-seed lines, as REF's reading is.
- **Reading 2's "no spring-back".** Say "falls to a plateau and stays (seeds' lows 0.614-0.650, scattered over
  801-1500)". Then it reads as an observation, not a null.

## The window entry (a2eb2d6), what remains
- Point 1 is answered by this entry: reading 1 is revised, and the per-seed lines show REF's dips.
- Point 2 is still open: reading 4's "the wild's herd-born share is not what sets how far the wild's R falls" stands
  in EXPLOG (line 7667), against the arms' own order.
- Point 3 (minor) is still open.

## Verdict
- **Gene-flow correction 2 (e0c0ff9):** settled, as in 598a467.
- **The window entry (a2eb2d6):** settled once its point 2 is in. Its reading 1 is superseded by 003bf80.
- **The timeline (003bf80):** the spring-back holds per seed, against LOAD05's plateau. It is settled once points 1-3
  are in:
  - replace the per-seed sentence that holds by construction with the REF-LOAD05 contrast;
  - call the recovery partial, and rewrite the line for Chris;
  - name hunting from year 300 as the unchecked candidate for the wild's moving baseline.

Point 4 is wording.

## On the correction (f15e544) and the tool (7a34b65)
**The tool.** I reran it through cpuslot at 7a34b65. wildr_timeline.txt and wildr.txt are byte-identical, and `--bad
prebin` stops with "LOAD05 s1: herd goats in 351-450". Per seed it adds J's bin, the bins from J's bin to the low, and the highest of the next three
bins. Per arm it adds the pre-herding all-goat R. It stops if a herd goat falls in a pre-herding bin.

**The numbers.** I checked every per-seed number against the lines by hand:
- REF's low is 0-1 bins after J's bin, 8 of 8, with rises of +0.054 to +0.159.
- LOAD05's low is 3-9 bins after, with rises of +0.018 to +0.041. LOAD05 s4's low (1401-1500) has only one bin after
  it before 1600, so its +0.018 is over one bin.
- SPR02's low is 0-3 bins after, with rises of +0.089 to +0.159.
- SPR01's low is 1-3 bins after, at 0.511-0.588, with rises of +0.018 to +0.104. The rise is 0.035 or less in s1, s4,
  s5 and s7.
- The pre-herding bins are 0.696, 0.678, 0.762 and 0.819.
- s3 and s7 go from 401-500 to 3201-4000 as stated.

The WT2 pointer is cited as older code, which is right. Its 401-500 R (0.824, EXPLOG WT2 table) is a no-herding level
near the 0.819 of 351-400 here, and that fits the hunting reading as a pointer only.

**Points 1-3 are in.** I judged analysis's change to the line for Chris, as asked.
- **SPR01's line is right, and better than mine.** "The dip is deeper, and in half the seeds it recovers little within
  three centuries" fits the per-seed lines: SPR01's lows come about as soon after J as REF's, and what differs is the
  size of the rise.
- **One addition makes it exact.** The four small rises (0.018-0.035) lie inside LOAD05's plateau range (0.018-0.041).
  "Recovers little" means no more than the fixed load's noise.
- **An optional clause for Chris.** By 3201-4000 every SPR01 seed is at 0.637-0.679 (wildr.txt), about LOAD05's
  0.644-0.677, so the slow seeds do rise later. The clause would read: "...recovers little within three centuries, and
  by 3201-4000 sits at the fixed load's level".

**Minor.**
- **Reading 5's heading.** "Hunting sets the baseline, and is the unchecked candidate" asserts what the body says is
  unchecked. The pre-herding rise is read (0.678 to 0.819 under hunting); its role after herding is not. Use "Hunting
  raises the wild's R before herding; whether it sets the level of recovery is not checked".
- **"Which plot Chris meant is still being asked"** is out of date. The plots he was sent draw this same wild-only
  series (takeoff_rdist.py; my 99dfa13). Say so, and leave his confirmation to the steward.

**The timeline (003bf80 as corrected by f15e544) is settled,** with the two minor wordings to go in before it reaches
Chris. With gene flow (598a467) and the window entry (99dfa13), all three pieces are settled.
