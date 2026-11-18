# Animal Domestication — Claude instructions

## Read first, every session
1. `STATUS.md` — where the system is right now (the 60-second orient)
2. `DEVLOG.md` — the top entry (what changed last)
3. `DEVPLAN.md` — the current `[ ACTIVE ]` stage
4. `EXPLOG.md` — the experiment ledger: pre-register every batch there before launching it, then append
   raw results only (protocol in its header). `MODEL.md` describes the model as built.

## What this is
Agent-based simulation of goat (and possibly wolf) domestication; follow-up to AgriGin / grain domestication work

## Stack (never violate)
- Vanilla JS + Canvas. No build step, no framework, no modules. `<script>` tags load
  `src/` in dependency order (`main.js` last).
- **Shared things are top-level `var`** — including `var Foo = class Foo {}`. This is what
  lets the SAME `src/` files run in the browser AND headless: the runners strip `'use strict'`
  and load them into the **main V8 realm via indirect `eval`** (not `vm`), where top-level
  `var` attaches to `globalThis` (a bare `class`/`const` would be block-scoped and never
  attach). Main-realm, not `vm`, because `vm` adds a ~7-10x hot-loop tax on per-tick global
  reads and we never need its sandbox isolation (conventions §4). Never fork the sim core.
- **All DOM lives in `ui.js` + `index.html`.** Sim classes (`world`, `agent`, `observer`,
  `datamanager`) touch zero DOM — that's what keeps them headless-safe.
- **Model/view split:** the world holds state and never draws; the `Observer` renders it.
- **Config:** one `PARAMETERS` global (`params.js`), serialized verbatim into every saved
  packet. `PARAM_SCHEMA` drives the control panel.
- **DB:** the vendored standard client `src/db.js` v2 (see `~/.claude/conventions.md` §4).
  Experiments via `db.experiment()` / `ex.run()` (tools/runyears.mjs does this); `db.scratch()` for throwaway work.

## Conventions
Follow `~/.claude/conventions.md`. STATUS is overwritten every close (present truth); DEVLOG is
append-only, newest on top (history); DEVPLAN stages carry `[ DONE ] / [ ACTIVE ] / [ PLANNED ]`
tokens and a `**Done when:**` criterion. `/log-session` rewrites STATUS — don't hand-edit its
`Verified:` line (that moves only on a cold `/audit`).

## Run
- Browser: open `index.html`.
- Experiments (data protocol, from 2026-11-18): `node tools/runyears.mjs --register <slug> "<question>"`, pre-register
  `## expNNN — ...` in EXPLOG, then `node tools/runyears.mjs <years> --exp expNNN --run <ARM>_seed<S> seed=S k=v ...`
  through `cpuslot`. Mongo is the record; `results/expNNN_slug/` holds the JSON copies. Probes use `--scratch`.
  Old `results/<name>/` folders and `tools/*.jsonl` job lists before exp001 are the pre-protocol archive.
- Smoke (no DB): `node smoketest.mjs` — prints the numbers that go in the DEVLOG entry.
