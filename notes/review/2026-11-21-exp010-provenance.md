# Review of the exp010 provenance check (2026-11-21, before scoring)

On EXPLOG "exp010 provenance check" (ca6d3ae), tools/exp010_prov.jsonl and tools/cmp_years.py.

**What I read from exp010's files.** To judge how much of each run an 800-year check covers, I read the following
from all 32 files in results/exp010_fixed-load:
- the saved parameters;
- the year-row key sets;
- the first year after 500 in which `herded` reaches 100.

That last figure is close to the establishment result. I read nothing else: no gaps and no trait means. The steward
should record that the reviewer saw it.

**Two free checks, both uninformative.**
- *Parameters:* identical across all 32 runs apart from id, seed and minLoad. The 11 runs started at 4afb749 with
  uncommitted edits already carry the five herder-culture keys (runOffLoss, selfDoes, larder, captureTaper,
  nuisanceCost) with the committed defaults. So the uncommitted params.js was already final.
- *Year-row keys:* the 11 runs from 4afb749 have the same 68 keys as the clean aab0e86 runs (LOAD05, LOAD1 and LOAD2
  seed 4). The later key sets follow the code record: LOAD3 seed 4 has 1dd4fa7's two counters, seeds 5-7 have
  434ee46's, and seed 8 has a659a59's.

Neither check can see the logic in world.js, so the rerun is still needed.

## 1. 800 years does not reach an established herd in four of the dirty runs (major)
The herder-culture code acts on herd events. The edits were in progress, so a misplaced switch guard or a changed
default path is most likely to show in the states those rules address: large herds with home-born breeding does,
culls at size, and the end of captures. The first year after 500 with 100 or more herd goats:

| dirty runs | first year with 100 or more herd goats | coverage of an 800-year check |
|---|---|---|
| LOAD05 seeds 1-3 and 8 | 503-623 | about 200-300 years of large herd |
| LOAD2 seeds 1-3 and 8, LOAD3 seeds 1-2 | never | their only state, for 400 years of herding |
| LOAD1 seed 2 | 935 | small-herd phase only |
| LOAD1 seed 3 | 1472 | small-herd phase only |
| LOAD1 seed 1 | 2288 | small-herd phase only |
| LOAD1 seed 8 | 2993 | small-herd phase only |

An 800-year check of the LOAD1 runs passes without ever running the code on the herds those runs will be scored on.

**Fix:** re-run the four dirty LOAD1 runs at 4000 years on clean code, and compare all 4000 years with the
originals. The comparison stays informative: if all rows match, the originals stand. The re-runs cost about the same
as checks long enough to cover seeds 1 and 8 (to 2600 and 3300 years). The other ten dirty runs can keep 800 years.

## 2. Add one clean run as a positive control (moderate)
The check assumes a re-run on clean code reproduces a clean original row for row with these arguments, recording
periods and skip list. That premise is not shown for this pipeline. The cross-host check behind `--anywhere` makes a
host difference unlikely, but it did not test these jobs.

**Fix:** add one clean run, for example LOAD1 seed 4 (aab0e86, clean), at 800 years on the same host as its original
if the record names the host. If it differs, every "differ" among the 14 is uninterpretable and the cause must be
found before the rule is applied. The other 17 clean runs need no check: their code is committed and identity-checked.

## 3. Minor
- **Shared keys only.** cmp_years compares only the year-row keys both files share and prints the rest. Record its
  "shared keys" count with each result, so a pass over very few keys can't go unnoticed. The dirty runs have 68.
- **The three runs dirty at a659a59 or ded6069** have no record of what was uncommitted. ded6069 committed only
  notes/review, but other files may have been dirty. Treat them like the rest (1 and 2), as the entry does.

## On the amendment (e9a4cbf), before any re-run finished
It answers points 1-3. The control's commit, 65e8cc0, has no src change since aab0e86, so it is the same code I named.
