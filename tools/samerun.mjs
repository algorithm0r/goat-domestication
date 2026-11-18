// samerun.mjs — are two runyears outputs the same run? Everything but `seconds` must match exactly
// (numbers by ===, key sets and array lengths too). Exit 0 if identical, 1 with the first difference.
// Either file may be plain .json or compact .json.gz (2026-11-13): both are read through loadRun as the plain object.
//   node tools/samerun.mjs <a.json[.gz]> <b.json[.gz]>
import { loadRun } from './loadrun.mjs';
const [fa, fb] = process.argv.slice(2);
const load = f => { const o = loadRun(f); delete o.seconds; return o; };
function diff(a, b, at) {
  if (a === b) return null;
  if (typeof a !== typeof b || a === null || b === null || typeof a !== 'object') return `${at}: ${JSON.stringify(a)} vs ${JSON.stringify(b)}`;
  if (Array.isArray(a) !== Array.isArray(b)) return `${at}: array vs object`;
  const ka = Object.keys(a), kb = Object.keys(b);
  if (ka.length !== kb.length) return `${at}: ${ka.length} keys vs ${kb.length}`;
  for (const k of ka) {
    if (!(k in b)) return `${at}.${k}: missing in second`;
    const d = diff(a[k], b[k], `${at}.${k}`); if (d) return d;
  }
  return null;
}
const d = diff(load(fa), load(fb), '$');
console.log(d ? `DIFFER ${d}` : 'SAME');
process.exit(d ? 1 : 0);
