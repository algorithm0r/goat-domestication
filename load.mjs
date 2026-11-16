// load.mjs — load the DOM-free sim core into the MAIN V8 realm via indirect eval (NOT vm —
// conventions §4: vm adds a ~7-10x hot-loop tax on per-tick global reads). Everything in src/ is
// `var` / `function` / `var X = class X`, so once the leading 'use strict' is stripped the top-level
// names attach to globalThis. The ONE list of headless sim files; runner.mjs and smoketest.mjs use it.
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import path from 'path';

export const SIM_FILES = ['util.js', 'params.js', 'engine.js', 'genome.js', 'animals.js', 'world.js', 'datamanager.js'];
const here = path.dirname(fileURLToPath(import.meta.url));

export function loadSim(overrides) {
  const indirectEval = eval;
  for (const f of SIM_FILES) {
    const src = readFileSync(path.join(here, 'src', f), 'utf8').replace(/^\s*(['"])use strict\1;?/, '');
    indirectEval(src);
  }
  if (overrides) Object.assign(globalThis.PARAMETERS, overrides);
  const P = globalThis.PARAMETERS;
  if (P.immigrationRate > 0) {   // the immigrant pool (tools/pool.mjs), path relative to this folder
    const pool = JSON.parse(readFileSync(path.resolve(here, P.immigrationPool), 'utf8'));
    globalThis.IMMIGRANT_POOL = pool.goats;
    P.immigrationPoolInfo = pool.info;   // saved with the run's parameters
  }
  return globalThis;
}
