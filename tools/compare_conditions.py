"""compare_conditions.py — compare conditions run per seed (files <COND>_seed<N>.json from runyears.mjs):
trait means over time (mean ± sd across seeds), a final-window table with a per-seed paired
difference, and the kill-off profile (age at death by sex) for one cause.

Usage: python tools/compare_conditions.py <dir> <condA> <condB> [window_years=100] [cause=hunted]
"""
import glob, json, os, sys
import numpy as np
import matplotlib.pyplot as plt

TRAITS = ['R', 'A', 'S', 'B', 'H', 'T', 'M', 'W']
NAMES = {'R': 'Reactivity', 'A': 'Aggression', 'S': 'Gregariousness', 'B': 'Body size',
         'H': 'Horn size', 'T': 'Season breadth', 'M': 'Milk yield', 'W': 'Pigmentation'}
d, A, B = sys.argv[1:4]
win = int(sys.argv[4]) if len(sys.argv) > 4 else 100
cause = sys.argv[5] if len(sys.argv) > 5 else 'hunted'
def load(c):
    runs = {}
    for f in glob.glob(os.path.join(d, f'{c}_seed*.json')):
        runs[int(os.path.basename(f).split('seed')[1][:-5])] = json.load(open(f))
    return runs
ra, rb = load(A), load(B)
seeds = sorted(set(ra) & set(rb))
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')
os.makedirs(out, exist_ok=True)
humansAt = rb[seeds[0]]['params'].get('humansAt')

fig, axes = plt.subplots(2, 5, figsize=(16, 6), constrained_layout=True)
for k, t in enumerate(TRAITS + ['goats']):
    ax = axes.flat[k]
    for runs, c, col in ((ra, A, '#888888'), (rb, B, '#d62728')):
        ys = np.array([[y['traitMeans'][t] if t != 'goats' else y['goats'] for y in runs[s]['years']] for s in seeds if not runs[s]['extinct']], float)
        if len(ys) == 0: continue
        m, sd = ys.mean(0), ys.std(0)
        ax.plot(m, color=col, lw=1.2, label=c); ax.fill_between(range(len(m)), m - sd, m + sd, color=col, alpha=0.2)
    if humansAt: ax.axvline(humansAt, color='k', ls='--', lw=0.6)
    ax.set_title(NAMES.get(t, 'Goats'), fontsize=9)
    if t != 'goats': ax.set_ylim(0, 1)
axes.flat[0].legend(fontsize=8)
# kill-off profile for `cause` in condition B, pooled over seeds and the final window
F = np.zeros(16); M = np.zeros(16)
for s in seeds:
    for y in rb[s]['years'][-win:]:
        ko = y.get('killoff', {}).get(cause)
        if ko: F += ko['F']; M += ko['M']
ax = axes.flat[9]
ax.bar(np.arange(16) - 0.2, F, 0.4, label='female'); ax.bar(np.arange(16) + 0.2, M, 0.4, label='male')
ax.set_title(f'{B}: age at death, {cause} (last {win} y)', fontsize=9); ax.set_xlabel('age (years)'); ax.legend(fontsize=8)
fig.suptitle(f'Animal Domestication — {A} vs {B}: trait means ± sd over {len(seeds)} seeds', fontsize=10)
fn = os.path.join(out, f'compare_{A}_vs_{B}.png'); fig.savefig(fn, dpi=130); print('wrote', fn)

print(f'final {win} years, mean over seeds (paired diff {B}−{A}: mean, seeds with diff > 0):')
for t in TRAITS + ['goats']:
    get = lambda r: np.mean([y['traitMeans'][t] if t != 'goats' else y['goats'] for y in r['years'][-win:]])
    va = np.array([get(ra[s]) for s in seeds]); vb = np.array([get(rb[s]) for s in seeds]); df = vb - va
    print(f'  {t:5s} {A} {va.mean():7.3f}  {B} {vb.mean():7.3f}  diff {df.mean():+7.3f}  ({(df > 0).sum()}/{len(seeds)} seeds up)')
for key in ('wolves', 'humans'):
    get = lambda r: np.mean([y['learnedFear'][key] for y in r['years'][-win:] if y.get('learnedFear')])
    va = np.array([get(ra[s]) for s in seeds]); vb = np.array([get(rb[s]) for s in seeds])
    print(f'  learned fear of {key:6s}: {A} {va.mean():.3f}  {B} {vb.mean():.3f}  (× R = effective: {A} {va.mean() * np.mean([np.mean([y["traitMeans"]["R"] for y in ra[s]["years"][-win:]]) for s in seeds]):.3f}, {B} {vb.mean() * np.mean([np.mean([y["traitMeans"]["R"] for y in rb[s]["years"][-win:]]) for s in seeds]):.3f})')
print(f'  extinct: {A} {sum(ra[s]["extinct"] for s in seeds)}/{len(seeds)}, {B} {sum(rb[s]["extinct"] for s in seeds)}/{len(seeds)}')
if F.sum() + M.sum() > 0:
    tot = F + M
    print(f'  {cause} kill-off: {int(tot.sum())} deaths; share under 1 y {tot[0] / tot.sum():.2f}, 1–2 y {tot[1] / tot.sum():.2f}; male share {M.sum() / tot.sum():.2f}')
