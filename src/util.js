'use strict';
// Pure helpers — no DOM, no globals beyond these. Safe to load in the browser AND headless
// (declared as `var`/`function` so they attach to either global).
var TAU = Math.PI * 2;

// ── Random numbers ──────────────────────────────────────────────────────────
// ALL sim randomness goes through rand(), never Math.random(), so a run is reproducible from
// PARAMETERS.seed. seedRandom(null) falls back to Math.random (unseeded).
// rand2 is a second stream, used only for the twinning gene's alleles (genome.js), so that adding
// that gene left every draw of rand() where it was: runs with twinning off reproduce older runs exactly.
// rand3 likewise serves only the neutral coat-marking gene, and rand4 only each goat's growth-rate multiplier (growSD).
var rand = Math.random, rand2 = Math.random, rand3 = Math.random, rand4 = Math.random;
function mulberry32(seed) {
  let s = seed >>> 0;
  return function () {
    s = (s + 0x6D2B79F5) | 0;
    let t = Math.imul(s ^ (s >>> 15), 1 | s);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function seedRandom(seed) {
  if (seed == null) { rand = rand2 = rand3 = rand4 = Math.random; return; }
  rand = mulberry32(seed);
  rand2 = mulberry32((seed ^ 0x9E3779B9) >>> 0);
  rand3 = mulberry32((seed ^ 0x85EBCA6B) >>> 0);
  rand4 = mulberry32((seed ^ 0xC2B2AE35) >>> 0);
}

function randomInt(n) { return Math.floor(rand() * n); }
function clamp(x, lo, hi) { return x < lo ? lo : (x > hi ? hi : x); }
function distance(a, b) { return Math.hypot(a.x - b.x, a.y - b.y); }

// Box–Muller normal sample
function normalSample(mean, sd) {
  mean = mean || 0; sd = (sd == null) ? 1 : sd;
  const u = 1 - rand(), v = rand();
  return mean + sd * Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v);
}

// Smooth 2-D value noise on a W×H grid: random values on a coarse lattice (spacing `cell`),
// bilinearly interpolated with smoothstep. Returns a Float32Array in [0,1], row-major.
function valueNoise(W, H, cell) {
  const gw = Math.ceil(W / cell) + 2, gh = Math.ceil(H / cell) + 2;
  const g = new Float32Array(gw * gh);
  for (let i = 0; i < g.length; i++) g[i] = rand();
  const out = new Float32Array(W * H);
  const sm = (t) => t * t * (3 - 2 * t);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const fx = x / cell, fy = y / cell, x0 = fx | 0, y0 = fy | 0;
    const tx = sm(fx - x0), ty = sm(fy - y0);
    const a = g[y0 * gw + x0], b = g[y0 * gw + x0 + 1], c = g[(y0 + 1) * gw + x0], d = g[(y0 + 1) * gw + x0 + 1];
    out[y * W + x] = (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty;
  }
  return out;
}

function rgb(r, g, b) { return 'rgb(' + (r | 0) + ',' + (g | 0) + ',' + (b | 0) + ')'; }
function hsl(h, s, l) { return 'hsl(' + (h | 0) + ',' + (s | 0) + '%,' + (l | 0) + '%)'; }
