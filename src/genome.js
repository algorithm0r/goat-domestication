'use strict';
// Genome: heritable trait values for goats (and, inert in v1, wolves). DESIGN §4.
//
// Architecture (PARAMETERS.ploidy, PARAMETERS.loci) is a swept condition:
//   'diploid', L loci : each trait has L loci × 2 alleles. Meiosis passes one random allele per locus
//                       from each parent (free recombination). Default L = 2.
//   'haploid'         : one allele per trait; the offspring takes each trait from a random parent.
//                       (Not blending: no averaging, so variance survives.)
// Each allele is a real number in [0,1]. The genotypic value G of a trait is the mean of its
// alleles. Mutation happens ONCE, at meiosis: every allele the offspring receives moves by a
// uniform step in ±mutationStep (the grain model's ±0.04) and is clamped. Copies never mutate.
//
// There is no noise term between genotype and phenotype (DESIGN §4.1): the phenotype is what these
// values do through the agents' mechanisms. Switchable pleiotropy:
//   W (pigmentation) expressed = (1 − pleioW)·G_W + pleioW·G_R       (neural-crest link, default 0)
//   A (aggression)   expressed = (1 − pleioA)·G_A + pleioA·G_R       (shared HPA axis, default 0)
//
// Twinning (L, 2026-11-05, with Chris): a doe's chance of carrying twins is twinMax × L (params.js). Its
// alleles draw from rand2 (util.js), and it is left out of the genome cost (animals.js) and of IBD, so
// runs with twinMax 0 reproduce runs from before the gene existed. NT_CORE = the eight traits before it.
//
// Coat marking (C, 2026-11-10, with Chris): a neutral appearance trait. It does nothing in any mechanism; only
// sireRule 'marked' looks at it. Its alleles draw from rand3, and like L it is left out of the cost and of IBD,
// so runs that never select on it reproduce runs from before it existed.
//
// Layout: one Float32Array per genome, trait-major: trait t occupies [t*K, (t+1)*K), K = alleles per
// trait (2L diploid, 1 haploid). Within a diploid trait, locus l holds alleles 2l and 2l+1.

var TRAITS = ['R', 'A', 'S', 'B', 'H', 'T', 'M', 'W', 'L', 'C'];
var TRAIT_NAMES = {
  R: 'Reactivity', A: 'Aggression', S: 'Gregariousness', B: 'Body size',
  H: 'Horn size', T: 'Season breadth', M: 'Milk yield', W: 'Pigmentation', L: 'Twinning', C: 'Coat marking',
};
var NT = TRAITS.length, NT_CORE = 8;
var T_R = 0, T_A = 1, T_S = 2, T_B = 3, T_H = 4, T_T = 5, T_M = 6, T_W = 7, T_L = 8, T_C = 9;
function traitRand(t) { return t < NT_CORE ? rand : t === T_L ? rand2 : rand3; }   // each extra gene its own stream

function allelesPerTrait() {
  return PARAMETERS.ploidy === 'haploid' ? 1 : 2 * PARAMETERS.loci;
}

// Every allele also carries a lineage id (genome.ids, an Int32Array beside the values), inherited
// unchanged through meiosis (mutation changes the value, not the lineage). Two copies of one lineage
// at a locus = identical by descent; the share of such loci is the inbreeding measure (the ROH
// analogue). relabelGenome gives every allele a fresh id, so IBD is measured from that moment.
var _nextAllele = 1;

// Fresh random genome (world initialisation): every allele ~ U[0,1].
function randomGenome() {
  const K = allelesPerTrait(), g = new Float32Array(NT * K);
  for (let i = 0; i < g.length; i++) g[i] = traitRand((i / K) | 0)();
  relabelGenome(g);
  return g;
}

function relabelGenome(g) {
  if (!g.ids) g.ids = new Int32Array(g.length);
  for (let i = 0; i < g.length; i++) g.ids[i] = _nextAllele++;
}

// Share of diploid loci whose two alleles are identical by descent (null for haploid); the core traits only.
function ibd(g) {
  if (PARAMETERS.ploidy === 'haploid') return null;
  const ids = g.ids, end = NT_CORE * allelesPerTrait(); let same = 0, n = 0;
  for (let a = 0; a < end; a += 2) { if (ids[a] === ids[a + 1]) same++; n++; }
  return same / n;
}

function mutateAllele(v, r = rand) {
  const s = PARAMETERS.mutationStep;
  v += r() * 2 * s - s;
  return v < 0 ? 0 : (v > 1 ? 1 : v);
}

// Offspring genome from two parent genomes (one mutation per received allele).
function meiosis(mom, dad) {
  const K = allelesPerTrait(), g = new Float32Array(NT * K), ids = g.ids = new Int32Array(NT * K);
  if (PARAMETERS.ploidy === 'haploid') {
    for (let t = 0; t < NT; t++) { const r = traitRand(t), p = r() < 0.5 ? mom : dad; g[t] = mutateAllele(p[t], r); ids[t] = p.ids[t]; }
    return g;
  }
  const L = PARAMETERS.loci;
  for (let t = 0; t < NT; t++) {
    const base = t * K, r = traitRand(t);
    for (let l = 0; l < L; l++) {
      const a = base + 2 * l;
      const am = a + (r() < 0.5 ? 0 : 1); g[a] = mutateAllele(mom[am], r); ids[a] = mom.ids[am];
      const ad = a + (r() < 0.5 ? 0 : 1); g[a + 1] = mutateAllele(dad[ad], r); ids[a + 1] = dad.ids[ad];
    }
  }
  return g;
}

// Genotypic values G (mean of each trait's alleles) into `out` (Float32Array(NT)).
function genotypicValues(g, out) {
  const K = g.length / NT;
  for (let t = 0; t < NT; t++) {
    let s = 0;
    for (let k = t * K, e = k + K; k < e; k++) s += g[k];
    out[t] = s / K;
  }
  return out;
}

// Expressed trait values (genotype after the switchable pleiotropic links) into `out`.
function expressTraits(g, out) {
  genotypicValues(g, out);
  const P = PARAMETERS;
  if (P.pleioW > 0) out[T_W] = (1 - P.pleioW) * out[T_W] + P.pleioW * out[T_R];
  if (P.pleioA > 0) out[T_A] = (1 - P.pleioA) * out[T_A] + P.pleioA * out[T_R];
  return out;
}
