# herd_rgap_traj.py — per run, 50-year means of herd size and herd − wild R gap over time, one line per run,
# coloured by condition.   python tools/herd_rgap_traj.py <results folder> <out.png> [from=400] [conds=A,B,...] [trait=R]
# conds: only these conditions, in this order (at most 5 colours); trait: the gap plotted in the lower panel.
import json, sys, glob, os
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
folder, out = sys.argv[1], sys.argv[2]; opt = dict(a.split('=', 1) for a in sys.argv[3:] if '=' in a); y0 = int(opt.get('from', 400))
only = opt['conds'].split(',') if 'conds' in opt else None; T = opt.get('trait', 'R')
cols = {c: None for c in only} if only else {}; pal = ['#2a6fdb', '#e8590c', '#2b8a3e', '#862e9c', '#c92a2a']
fig, axs = plt.subplots(2, 1, figsize=(9, 6), sharex=True)
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    c = os.path.basename(f).rsplit('_seed', 1)[0]
    if only and c not in only: continue
    if cols.get(c) is None: cols[c] = pal[(only.index(c) if only else len(cols)) % len(pal)]
    Y = json.load(open(f))['years']; xs, hs, gs = [], [], []
    for a in range(y0, len(Y) - 49, 50):
        ys = [r for r in Y[a:a + 50] if r['herded'] > 0 and r['goats'] > r['herded']]
        if not ys: continue
        w = lambda r: (r['goats'] * r['traitMeans'][T] - r['herded'] * r['herdTraitMeans'][T]) / (r['goats'] - r['herded'])
        xs.append(a + 25); hs.append(np.mean([r['herded'] for r in ys])); gs.append(np.mean([r['herdTraitMeans'][T] - w(r) for r in ys]))
    axs[0].plot(xs, hs, color=cols[c], lw=1, alpha=0.8); axs[1].plot(xs, gs, color=cols[c], lw=1, alpha=0.8)
for c, k in cols.items(): axs[0].plot([], [], color=k, label=c)
axs[0].legend(fontsize=8, frameon=False); axs[0].set_ylabel('herd size'); axs[1].set_ylabel(f'{T} gap (herd − wild)'); axs[1].set_xlabel('year')
for ax in axs: ax.spines[['top', 'right']].set_visible(False)
fig.savefig(out, dpi=130, bbox_inches='tight'); print(out)
