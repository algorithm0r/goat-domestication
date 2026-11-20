# The goat paper team: who owns what, and how we share one checkout

*Set by the experiment session as steward, 2026-11-20 (Chris: "you become the steward, the project manager, the lead ... you
can decide on protocol among you"). Every session on this project reads this file at start. Questions about it go to
the steward.*

## Sessions

| session | owns (writes) | does |
|---|---|---|
| **Steward / experiments** ("Animal domestication simulation") | `src/`, `index.html`, `load.mjs`, `smoketest.mjs`, the run tools (`tools/runyears.mjs`, `tools/batch.mjs`, `tools/*.jsonl` job lists, `tools/publish_public.sh`), EXPLOG pre-registrations and raw completion records, `README.md`, `MODEL.md`, `STATUS.md`, `DEVLOG.md`, `DEVPLAN.md`, `notes/` (except `notes/review/`), this file | Leads. Designs and pre-registers every experiment, runs every simulation (cpuslot), keeps the model and its docs, sets priorities, the only one who publishes the public repo |
| **Analysis** | the analysis scripts in `tools/` (`runio.py`, `settle_tab.py`, `corner_tab.py`, `perseed_tab.py`, `husb_tab.py`, `gene_dists.py`, and each new scorer), the scored sections of EXPLOG, the tables in `results/expNNN_*/` | Scores each experiment as it lands, by the measure its pre-registration names, and scores the predictions. Makes the tables the paper quotes |
| **Author** ("Draft the goat domestication paper") | `paper/` | Writes the paper. Asks the steward for runs and the analysis session for tables. Decides whether to have a literature helper; if so, that helper writes only where the author says |
| **Reviewer** | `notes/review/` | Reads everything and writes nothing else. Attacks the design, the claims and the draft as a hostile Proc B referee would. No stake in any result |

Only the steward runs simulations or writes to Mongo. The others read the JSON copies in `results/` (Mongo read-only if
needed). Analysis scripts over a whole experiment run through `cpuslot run --tag animal-domestication -- python ...`.

## Rules every session keeps

1. **Write only what you own.** To change another session's file, ask its owner (SendMessage) with the change you want.
2. **Every recorded number comes from a committed script** in `tools/` (or, for the author's own figures, in
   `paper/analysis/`), never inline code or a scratchpad. A table in EXPLOG or the paper names the command that made it.
3. **Measures are fixed before the data.** The pre-registration names the measure and the window. The analysis
   session implements it as written. A better measure found later is reported beside the registered one, labelled
   exploratory, never in its place.
4. **EXPLOG is append-only.** The steward appends `## expNNN — question` (pre-registration) and `## expNNN results (raw)`
   (completion: runs, exits, files, commits). The analysis session appends `## expNNN results (scored)`: the tables, by
   command, and each prediction met or not. Nobody edits an earlier entry; a correction is a new dated note.

## Git (one working tree, several sessions)

- **Commit only your own paths, by name:** `git add <your files>` then `git commit -m "..."`, or
  `git commit -m "..." -- <your files>`. Never `git add -A`, `git add .`, `git commit -a`, `git stash`, `git reset`,
  `git checkout <file>` or any rebase. They touch other sessions' work.
- **Commit as soon as an edit is finished**, above all EXPLOG, so no session's uncommitted lines sit in a shared file.
  Before editing EXPLOG, re-read it: another session may have appended since.
- **Never push, tag or publish.** Only the steward runs `tools/publish_public.sh`, after checking the tree.
- If a commit fails with `index.lock`, another session is mid-commit: wait a moment and retry. Never delete the lock.
- Messages end with the attribution line the harness gives you.

## Talking to each other

SendMessage by session name. Put the point in the first line. Requests for runs go to the steward, for tables to
analysis, for text to the author. Review findings go to the steward and the author together. Chris can see every
session. When he and the steward disagree, Chris decides.
