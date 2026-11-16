// merge.mjs — join per-seed pool files (tools/pool.mjs) into one pool: node tools/pools/merge.mjs <out.json> <in.json ...>
import fs from 'fs';
const [out, ...ins] = process.argv.slice(2);
const parts = ins.map(f => JSON.parse(fs.readFileSync(f, 'utf8')));
const goats = parts.flatMap(p => p.goats.map(g => ({ g: g.g, fw: g.fw, fh: g.fh })));
fs.writeFileSync(out, JSON.stringify({ info: { built: new Date().toISOString().slice(0, 10), from: ins.map(f => f.split('\\').join('/')), runs: parts.map(p => p.info), n: goats.length }, goats }));
console.log(`${out}: ${goats.length} goats from ${ins.length} runs`);
