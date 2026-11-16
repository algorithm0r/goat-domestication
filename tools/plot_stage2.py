"""plot_stage2.py — Stage 2 (H0, no humans) check: trait trajectories across seeds, one seed's
genotype heatmaps (the grain paper's form), and a life-history summary.

Usage: python tools/plot_stage2.py results/stage2   (writes figures/ and prints the summary)
"""
import glob, json, os, sys
import numpy as np
import matplotlib.pyplot as plt

TRAITS = ['R', 'A', 'S', 'B', 'H', 'T', 'M', 'W']
NAMES = {'R': 'Reactivity', 'A': 'Aggression', 'S': 'Gregariousness', 'B': 'Body size',
         'H': 'Horn size', 'T': 'Season breadth', 'M': 'Milk yield', 'W': 'Pigmentation'}
src = sys.argv[1] if len(sys.argv) > 1 else 'results/stage2'
runs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(src, 'seed*.json')), key=lambda f: int(os.path.basename(f)[4:-5]))]
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')
os.makedirs(out, exist_ok=True)

# 1. trait means over time, every seed
fig, axes = plt.subplots(2, 4, figsize=(13, 5.5), sharex=True, sharey=True, constrained_layout=True)
for k, t in enumerate(TRAITS):
    ax = axes.flat[k]
    for r in runs:
        ax.plot([y['traitMeans'][t] for y in r['years']], lw=0.8, alpha=0.7)
    ax.set_title(NAMES[t], fontsize=9); ax.set_ylim(0, 1)
for ax in axes[1]: ax.set_xlabel('year')
fig.suptitle(f'Animal Domestication — H0 wild type (no humans): trait means, {len(runs)} seeds', fontsize=10)
fig.savefig(os.path.join(out, 'stage2_trait_means.png'), dpi=140)

# 2. genotype heatmaps for seed 1
r = runs[0]
fig, axes = plt.subplots(2, 4, figsize=(13, 5.5), sharex=True, sharey=True, constrained_layout=True)
for k, t in enumerate(TRAITS):
    ax = axes.flat[k]
    h = np.asarray(r['hist'][t], float); h = h / np.maximum(1, h.sum(axis=1, keepdims=True))
    im = ax.pcolormesh(np.arange(h.shape[0] + 1), np.linspace(0, 1, 21), h.T, cmap='viridis', vmin=0, vmax=0.5, rasterized=True)
    ax.set_title(NAMES[t], fontsize=9)
for ax in axes[1]: ax.set_xlabel('year')
fig.colorbar(im, ax=axes, fraction=0.02).set_label('share of goats per bucket (clipped 50%)', fontsize=8)
fig.suptitle('Animal Domestication — H0 genotype distributions, seed 1', fontsize=10)
fig.savefig(os.path.join(out, 'stage2_heatmaps_seed1.png'), dpi=140)

# 3. life history over the last 100 years, pooled over seeds
def last(r, f): return [f(y) for y in r['years'][-100:] if f(y) is not None]
pool = lambda f: np.concatenate([np.asarray(last(r, f), float) for r in runs])
goats = pool(lambda y: y['goats'])
causes = list(runs[0]['years'][0]['deaths'].keys())
deaths = {c: pool(lambda y, c=c: y['deaths'][c]).mean() for c in causes}
print(f"H0, last 100 of 500 years, {len(runs)} seeds")
print(f"  goats            {goats.mean():.0f} (range {goats.min():.0f}–{goats.max():.0f}); extinct runs: {sum(r['extinct'] for r in runs)}")
print(f"  births / year    {pool(lambda y: y['births']).mean():.0f}")
print(f"  first kidding    median {np.median(pool(lambda y: y['medianFirstKidAge'])) / 360:.2f} years   (brief: wild ~2–3)")
print(f"  adult mortality  {pool(lambda y: y['adultMortality']).mean():.3f} / year (all goats ≥ 1 y)")
print('  deaths / year    ' + ', '.join(f'{c} {v:.0f}' for c, v in deaths.items() if v > 0))
fin = {t: [r['years'][-1]['traitMeans'][t] for r in runs] for t in TRAITS}
print('  final trait means (mean ± sd over seeds): ' + '  '.join(f"{t} {np.mean(v):.2f}±{np.std(v):.2f}" for t, v in fin.items()))
drift = {t: np.mean([abs(np.mean([y['traitMeans'][t] for y in r['years'][-50:]]) - np.mean([y['traitMeans'][t] for y in r['years'][-150:-100]])) for r in runs]) for t in TRAITS}
print('  settling: |mean(last 50 y) − mean(y350–400)|: ' + '  '.join(f'{t} {v:.3f}' for t, v in drift.items()))
