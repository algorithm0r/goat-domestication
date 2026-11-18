// runformat.mjs — the compact run file: a lossless columnar re-encoding of runyears' output, gzipped (.json.gz).
// (2026-11-13) A 4000-year run was 32 MB of JSON, three quarters of it repeated key names and punctuation. This file
// holds the codec, the writer (saveRun) and the reader (loadRun). loadRun returns EXACTLY the object JSON.parse gives
// for the old plain .json file: same values, same key order, same absent keys. saveRun checks that before it writes:
// it decodes what it encoded and requires JSON.stringify of the result to equal the plain JSON text byte for byte,
// and falls back to the plain JSON (gzipped) if not. The DB packet (DataManager.flush) is untouched.
//
// Which format is written is chosen by the output name: `x.json` writes the plain JSON exactly as before;
// `x.json.gz` writes the compact form. loadRun reads either (and a gzipped plain JSON), by content, not name.
// Scope since the experiment data protocol (conventions §4, 2026-11-13): there, Mongo is the record and the JSON copy
// is plain, never gzipped, so this compact form is for files outside it (the pre-protocol results/ archive, runs
// written by runyears before it moves to db.js v2). It does not shrink a Mongo document: BSON stores every array
// element with its own index key, so the columnar form is no smaller in BSON than the plain one (measured on
// husb/HmaxH_seed1: 54 MB plain vs 60 MB columnar).
//
// The encoding, value by value (a value is JSON as JSON.parse returns it):
//   scalar, or an array with no objects inside      → itself; a rectangular array nest of depth ≥ 2 → {t:'F', s: shape, v: flat}
//   object                                          → {t:'O', k: keys, v: encoded values}
//   array containing objects                        → {t:'L', n: length, c: column}
// A column is a list of values encoded together (the years, the samples, one field across the years, ...):
//   no objects inside        → the list itself, or {t:'F'} when rectangular (e.g. [attacks, kills] pairs)
//   some keys absent         → {t:'A', r: run lengths of present/absent (starting with present), c: the present values}
//   nulls among objects/arrs → {t:'N', r: run lengths of non-null/null, c: the non-null values}
//   objects, keys in one consistent order (a fixed record, or one whose keys come and go in a fixed order,
//   e.g. killoff's causes in CAUSE_NAMES order)
//                            → {t:'R', k: keys, c: one column per key}  (columnar: the key names once per file)
//   objects with keys in varying order (the cross-tabs: wolfAtk keys arrive in event order)
//                            → {t:'M', k: key legend, n: keys per row, i: key indices, c: the values}
//   arrays containing objects→ {t:'V', n: lengths, c: the elements}
//   anything else            → {t:'X', v: each value encoded on its own}
import fs from 'fs'; import zlib from 'zlib';

export const FORMAT = 'adcol1';
const MAX_RECORD_KEYS = 64;   // an object column with more distinct keys than this is stored as a map, not a record

const isObj = x => x !== null && typeof x === 'object' && !Array.isArray(x);
const hasObj = x => Array.isArray(x) ? x.some(hasObj) : isObj(x);
const own = (o, k) => Object.prototype.hasOwnProperty.call(o, k);

// run lengths of a boolean list, alternating, the first run counting `true`
function rle(flags) { const r = []; let cur = true, n = 0; for (const f of flags) { if (f === cur) n++; else { r.push(n); cur = !cur; n = 1; } } r.push(n); return r; }
function unrle(r) { const out = []; let cur = true; for (const n of r) { for (let i = 0; i < n; i++) out.push(cur); cur = !cur; } return out; }

// shape of a rectangular array nest whose leaves are scalars, or null
function rectShape(a) {
  if (!Array.isArray(a) || a.length === 0) return null;
  if (!Array.isArray(a[0])) return a.every(x => !Array.isArray(x) && !isObj(x)) ? [a.length] : null;
  const s0 = rectShape(a[0]); if (!s0) return null;
  for (let i = 1; i < a.length; i++) {
    const s = rectShape(a[i]);
    if (!s || s.length !== s0.length) return null;
    for (let k = 0; k < s.length; k++) if (s[k] !== s0[k]) return null;
  }
  return [a.length, ...s0];
}
function reshape(flat, shape) {
  let pos = 0;
  const build = d => { const out = new Array(shape[d]); for (let i = 0; i < shape[d]; i++) out[i] = d === shape.length - 1 ? flat[pos++] : build(d + 1); return out; };
  return build(0);
}
const plain = a => { const s = rectShape(a); return s && s.length >= 2 ? { t: 'F', s, v: a.flat(Infinity) } : a; };

// one key order that every object's keys follow as a subsequence, or null if there is none (greedy; null is always safe)
function keyOrder(objs) {
  const master = []; let pos = new Map();
  for (const o of objs) {
    let last = -1;
    for (const k of Object.keys(o)) {
      const p = pos.get(k);
      if (p !== undefined) { if (p <= last) return null; last = p; continue; }
      if (master.length >= MAX_RECORD_KEYS) return null;
      master.splice(last + 1, 0, k); last++;
      pos = new Map(master.map((key, i) => [key, i]));
    }
  }
  return master;
}

function encodeValue(x) {
  if (Array.isArray(x)) return hasObj(x) ? { t: 'L', n: x.length, c: encodeCol(x) } : plain(x);
  if (isObj(x)) { const k = Object.keys(x); return { t: 'O', k, v: k.map(key => encodeValue(x[key])) }; }
  return x;
}

function encodeCol(vals) {
  if (vals.some(v => v === undefined)) return { t: 'A', r: rle(vals.map(v => v !== undefined)), c: encodeCol(vals.filter(v => v !== undefined)) };
  if (vals.some(v => v === null) && vals.some(v => v !== null && typeof v === 'object'))
    return { t: 'N', r: rle(vals.map(v => v !== null)), c: encodeCol(vals.filter(v => v !== null)) };
  if (!vals.some(hasObj)) return plain(vals);
  if (vals.every(isObj)) {
    const k = keyOrder(vals);
    if (k) return { t: 'R', k, c: k.map(key => encodeCol(vals.map(o => own(o, key) ? o[key] : undefined))) };
    const legend = [], index = new Map(), n = [], i = [], flat = [];
    for (const o of vals) {
      const ks = Object.keys(o); n.push(ks.length);
      for (const key of ks) { let j = index.get(key); if (j === undefined) { j = legend.length; index.set(key, j); legend.push(key); } i.push(j); flat.push(o[key]); }
    }
    return { t: 'M', k: legend, n, i, c: encodeCol(flat) };
  }
  if (vals.every(Array.isArray)) return { t: 'V', n: vals.map(a => a.length), c: encodeCol(vals.flat(1)) };
  return { t: 'X', v: vals.map(encodeValue) };
}

function decodeValue(x) {
  if (!isObj(x)) return x;
  if (x.t === 'F') return reshape(x.v, x.s);
  if (x.t === 'L') return decodeCol(x.c, x.n);
  if (x.t === 'O') { const o = {}; x.k.forEach((k, j) => { o[k] = decodeValue(x.v[j]); }); return o; }
  throw new Error(`runformat: unknown value tag ${x.t}`);
}

// a column back to its list of n values (undefined marks an absent key, only ever inside a record column)
function decodeCol(c, n) {
  if (Array.isArray(c)) return c;
  switch (c.t) {
    case 'F': return reshape(c.v, c.s);
    case 'A': case 'N': {
      const has = unrle(c.r), m = has.reduce((a, h) => a + (h ? 1 : 0), 0), inner = decodeCol(c.c, m), gap = c.t === 'A' ? undefined : null;
      let j = 0; return has.map(h => h ? inner[j++] : gap);
    }
    case 'R': {
      const cols = c.k.map((k, j) => decodeCol(c.c[j], n)), out = new Array(n);
      for (let r = 0; r < n; r++) { const o = {}; for (let j = 0; j < c.k.length; j++) { const v = cols[j][r]; if (v !== undefined) o[c.k[j]] = v; } out[r] = o; }
      return out;
    }
    case 'M': {
      const total = c.n.reduce((a, b) => a + b, 0), vals = decodeCol(c.c, total), out = new Array(c.n.length);
      let p = 0; for (let r = 0; r < c.n.length; r++) { const o = {}; for (let j = 0; j < c.n[r]; j++, p++) o[c.k[c.i[p]]] = vals[p]; out[r] = o; }
      return out;
    }
    case 'V': {
      const total = c.n.reduce((a, b) => a + b, 0), vals = decodeCol(c.c, total), out = new Array(c.n.length);
      let p = 0; for (let r = 0; r < c.n.length; r++) { out[r] = vals.slice(p, p + c.n[r]); p += c.n[r]; }
      return out;
    }
    case 'X': return c.v.map(decodeValue);
  }
  throw new Error(`runformat: unknown column tag ${c.t}`);
}

/** Encode a run object (as JSON.parse returns it) into the compact form. */
export function packRun(run) { return { format: FORMAT, data: encodeValue(run) }; }
/** Inverse of packRun; anything not in the compact form is returned as it is (an old plain run). */
export function unpackRun(f) { return isObj(f) && f.format === FORMAT && own(f, 'data') ? decodeValue(f.data) : f; }

/** Read a run file in any format (plain .json, compact .json.gz, or gzipped plain JSON) as the old plain object. */
export function loadRun(file) {
  let buf = fs.readFileSync(file);
  if (buf[0] === 0x1f && buf[1] === 0x8b) buf = zlib.gunzipSync(buf);
  return unpackRun(JSON.parse(buf.toString('utf8')));
}

/** The compact text for a run, checked: decoding it must give back `legacy` (the plain JSON text) byte for byte.
 *  Returns { text, format }; on any failure the plain text itself, with format 'json'. */
export function compactText(legacy) {
  try {
    const text = JSON.stringify(packRun(JSON.parse(legacy)));
    if (JSON.stringify(unpackRun(JSON.parse(text))) !== legacy) throw new Error('round trip differs from the plain JSON');
    return { text, format: FORMAT };
  } catch (e) {
    console.error(`[runformat] compact encoding failed (${e.message}); writing the plain JSON instead`);
    return { text: legacy, format: 'json' };
  }
}

/** Write a run: `*.gz` → compact and gzipped (written to a temp name, then renamed); anything else → the plain JSON
 *  exactly as runyears always wrote it. Returns { format, bytes }. */
export function saveRun(file, run) {
  const legacy = JSON.stringify(run);
  if (!file.endsWith('.gz')) { fs.writeFileSync(file, legacy); return { format: 'json', bytes: Buffer.byteLength(legacy) }; }
  const { text, format } = compactText(legacy), gz = zlib.gzipSync(text, { level: 9 });
  fs.writeFileSync(file + '.tmp', gz); fs.renameSync(file + '.tmp', file);
  return { format, bytes: gz.length };
}
