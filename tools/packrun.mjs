// packrun.mjs — convert old plain run files (.json) to the compact form (.json.gz), checked, and report sizes.
// Never deletes or changes the source. A file is written only if reading it back with loadRun gives the source
// text byte for byte (JSON.stringify(loadRun(new)) === the old file's text).
//   node tools/packrun.mjs <outdir> <a.json> [b.json ...]     writes <outdir>/<name>.json.gz
//   node tools/packrun.mjs --check <a.json> [...]             no output files; only the check and the sizes
// Prints one tab-separated line per file: name, plain bytes, compact bytes (gzipped), compact bytes (not gzipped), gzip
// of the plain JSON (bytes), ratio, OK/FAIL.
import fs from 'fs'; import os from 'os'; import path from 'path'; import zlib from 'zlib';
import { compactText, loadRun, FORMAT } from './runformat.mjs';

const args = process.argv.slice(2), check = args[0] === '--check', outdir = args.shift();
if (!check) fs.mkdirSync(outdir, { recursive: true });
const hb = process.env.CPUSLOT_HEARTBEAT;
let bad = 0, k = 0;
console.log('file\tplain\tcompact_gz\tcompact\tplain_gz\tratio\tcheck');
for (const f of args) {
  const legacy = fs.readFileSync(f, 'utf8').replace(/\s+$/, '');
  const { text, format } = compactText(legacy);
  const gz = zlib.gzipSync(text, { level: 9 }), plainGz = zlib.gzipSync(legacy, { level: 9 }).length;
  const out = check ? path.join(os.tmpdir(), `packrun-check-${process.pid}.json.gz`) :path.join(outdir, path.basename(f).replace(/\.json$/, '') + '.json.gz');
  fs.writeFileSync(out, gz);
  const ok = format === FORMAT && JSON.stringify(loadRun(out)) === legacy;
  if (check || !ok) fs.unlinkSync(out);
  if (!ok) bad++;
  console.log([path.basename(f), Buffer.byteLength(legacy), gz.length, Buffer.byteLength(text), plainGz, (Buffer.byteLength(legacy) / gz.length).toFixed(1), ok ? 'OK' : 'FAIL'].join('\t'));
  if (hb) try { fs.writeFileSync(hb, JSON.stringify({ done: ++k, total: args.length })); } catch (e) {}
}
process.exit(bad ? 1 : 0);
