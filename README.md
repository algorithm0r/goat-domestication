# Animal Domestication

Agent-based simulation of goat (and possibly wolf) domestication; follow-up to AgriGin / grain domestication work

A browser-based agent-based simulation (vanilla JS + Canvas, no build step), scaffolded from
the shared engine v2.

**Live:** https://algorithm0r.github.io/goat-domestication/ (the public copy leaves out `paper/`; sync with
`bash tools/publish_public.sh "message"`).

## Run
- **Browser:** open `index.html`.
- **Experiments:** `node tools/runyears.mjs --register <slug> "<question>"` claims the next `expNNN`; pre-register it in
  `EXPLOG.md` as `## expNNN — <question>`; then `node tools/runyears.mjs <years> --exp expNNN --run <ARM>_seed<S> seed=S
  key=value ...` (through `cpuslot`). Each run goes to Mongo `animalDomestication.expNNN_<slug>` (the record) and
  `results/expNNN_<slug>/<run>.json` (the plain JSON copy), with `PARAMETERS.id` naming it. Same sim core, main V8 realm
  (indirect `eval`, not `vm`; `~/.claude/conventions.md` §4). Probes: `--scratch --run <name>`. Needs `npm install`
  (the mongodb driver) and mint's MongoDB on 127.0.0.1:27017: on the desktop the Mint Tunnel forwards that port, and runs on mint
  (cpuslot --anywhere) reach the same database directly. The desktop's own MongoDB service was retired 2026-11-20, after
  its databases were merged into mint's. If the tunnel is down, the desktop's 27017 refuses connections.
- `runner.mjs` is the scaffold's original batch runner (legacy `batch`-style packets); not used for experiments.
- **Smoke test:** `node smoketest.mjs` — no DB; asserts the model invariant and prints metrics.

## Layout
- `src/` — sim core (`engine`, `params`, `world`, `agent`, `observer`, `datamanager`, `charts`,
  `util`) + `db.js` (vendored standard DB client) + `ui.js`/`main.js` (browser-only, all DOM).
- `tools/runyears.mjs` (experiments), `smoketest.mjs`, `runner.mjs` (legacy) — headless entry points; `tools/` also
  holds the table and plotting tools (`tools/runio.py` reads old and new run files).
- `DEVPLAN.md` / `DEVLOG.md` — the plan (forward) and the log (backward, append-only).

See `~/.claude/conventions.md` for the shared standards this follows.
