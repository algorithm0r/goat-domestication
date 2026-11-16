# gene_heatmap.py — the grain paper's figure form: per row a trait (or learned fear), per column a condition
# and population, the share of goats in each of 20 value buckets each year, summed over seeds.
#   python tools/gene_heatmap.py <results folder> <out.png> <col> [<col> ...] [rows=R,A,S,B,H,T,M,W,fearW,fearH] [from=0]
#   col = COND:pop, pop all | herd | wild (wild = all − herd). Needs runs with histHerd (code of 2026-11-02 on).
# Dashed lines: humansAt, herdingAt, and each year in the run's schedule.
import json, sys, glob, os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
args = [a for a in sys.argv[1:] if '=' not in a]; opt = dict(a.split('=', 1) for a in sys.argv[1:] if '=' in a)
folder, out, cols = args[0], args[1], args[2:]
rows = opt.get('rows', 'R,A,S,B,H,T,M,W,fearW,fearH').split(','); y0 = int(opt.get('from', 0))
NAMES = {'R': 'Reactivity', 'A': 'Aggression', 'S': 'Sociability', 'B': 'Body size', 'H': 'Horns', 'T': 'Season\nbreadth',
         'M': 'Milk', 'W': 'Pigmentation', 'L': 'Twinning', 'fearW': 'Learned fear\nof wolves', 'fearH': 'Learned fear\nof humans'}
cmap = LinearSegmentedColormap.from_list('grain', ['#ffffff', '#3030ff', '#00e0ff', '#40ff40', '#ffff00', '#ff0000'])

def load(cond):
    fs = sorted(glob.glob(os.path.join(folder, f'{cond}_seed*.json')))
    if not fs: sys.exit(f'no runs for {cond} in {folder}')
    allc = herd = None; P = None
    for f in fs:
        d = json.load(open(f)); P = d['params']
        a = {k: np.array(v, float) for k, v in d['hist'].items()}; h = {k: np.array(v, float) for k, v in d['histHerd'].items()}
        allc = a if allc is None else {k: allc[k][:len(a[k])] + a[k][:len(allc[k])] for k in a}
        herd = h if herd is None else {k: herd[k][:len(h[k])] + h[k][:len(herd[k])] for k in h}
    lines = ([P['humansAt'], P['herdingAt']] if P['humansPerCamp'] > 0 else []) + [int(e.split(':')[0]) for e in (P.get('schedule') or '').split(';') if e.strip()]
    return {'all': allc, 'herd': herd, 'wild': {k: allc[k] - herd[k] for k in allc}}, len(fs), P, sorted({l for l in lines if l < 1e8})

data = {c.split(':')[0]: load(c.split(':')[0]) for c in cols}
fig, axs = plt.subplots(len(rows), len(cols), figsize=(2.6 * len(cols) + 1.6, 1.25 * len(rows) + 0.9), squeeze=False, sharex='col')
for j, col in enumerate(cols):
    cond, pop = col.split(':'); H, n, P, lines = data[cond]
    for i, r in enumerate(rows):
        m = H[pop][r][y0:]; tot = m.sum(1, keepdims=True)
        share = np.divide(m, tot, out=np.full_like(m, np.nan), where=tot > 0)
        ax = axs[i][j]; T = m.shape[0]
        ax.imshow(share.T, origin='lower', aspect='auto', cmap=cmap, vmin=0, vmax=1, extent=[y0, y0 + T, 0, 1], interpolation='nearest')
        for l in lines:
            if y0 < l < y0 + T: ax.axvline(l, color='k', ls='--', lw=0.8)
        ax.set_yticks([0, 1]); ax.set_yticklabels(['0', f'{P["fearMax"]:g}'] if r.startswith('fear') else ['Min', 'Max'], fontsize=7)
        ax.tick_params(axis='x', labelsize=7)
        if j == 0: ax.set_ylabel(NAMES.get(r, r), fontsize=8)
        if i == 0: ax.set_title(f'{cond} {pop} (n {n})', fontsize=9)
    axs[-1][j].set_xlabel('year', fontsize=8)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 100)); fig.colorbar(sm, ax=axs, fraction=0.025, pad=0.02, label='% of population')
fig.savefig(out, dpi=130, bbox_inches='tight'); print(out)
