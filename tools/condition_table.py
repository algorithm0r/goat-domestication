"""condition_table.py — the DESIGN §2 condition table from a batch (results/<dir>/<COND>_seed<N>.json).

Prints, per condition, means over seeds of the final `win` years: herd size; herded and wild genetic
trait means and their difference; learned fear of humans; IBD (herd vs wild); sires per camp-year;
wild-sired share; R at capture. Then the Ganj Dareh kill-off check on the culled goats of `ganj`.
Writes figures/conditions_herd_minus_wild.png and figures/conditions_herd_R.png.

Usage: python tools/condition_table.py results/stage4 [win=100] [ganj=H3]
"""
import glob, json, os, sys
import numpy as np
import matplotlib.pyplot as plt

TRAITS = ['R', 'A', 'S', 'B', 'H', 'T', 'M', 'W']
d = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100; ganj = sys.argv[3] if len(sys.argv) > 3 else 'H3'
runs = {}
for f in glob.glob(os.path.join(d, '*_seed*.json')):
    c = os.path.basename(f).split('_seed')[0]
    runs.setdefault(c, []).append(json.load(open(f)))
conds = sorted(runs)
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures'); os.makedirs(out, exist_ok=True)

def tail(r): return r['years'][-win:]
def mean_of(r, f):
    v = [f(y) for y in tail(r)]; v = [x for x in v if x is not None]
    return np.mean(v) if v else np.nan
def wild_mean(y, t):   # all-goat mean minus the herded part
    n, nh = y['goats'], y.get('herded') or 0
    if n - nh <= 0: return None
    h = (y.get('herdTraitMeans') or {}).get(t, 0) if nh else 0
    return (y['traitMeans'][t] * n - h * nh) / (n - nh)

rows = {}
print(f'final {win} years, mean over seeds')
print(f"{'cond':5s} {'n':>2s} {'goats':>6s} {'herded':>6s} | " + ' '.join(f'{t + "h-w":>6s}' for t in TRAITS) + ' | fearH_h   F_herd F_wild sires wildSired R_capt R_herd')
for c in conds:
    rs = runs[c]
    goats = np.mean([mean_of(r, lambda y: y['goats']) for r in rs])
    herded = np.mean([mean_of(r, lambda y: y.get('herded') or 0) for r in rs])
    diffs = {}
    for t in TRAITS:
        per = [mean_of(r, lambda y, t=t: (y['herdTraitMeans'][t] - wild_mean(y, t)) if y.get('herdTraitMeans') and wild_mean(y, t) is not None else None) for r in rs]
        diffs[t] = (np.nanmean(per) if np.isfinite(per).any() else np.nan, np.nanstd(per) if np.isfinite(per).any() else np.nan)
    g = lambda key: np.nanmean([mean_of(r, lambda y: y.get(key)) for r in rs])
    rh = np.nanmean([mean_of(r, lambda y: (y.get('herdTraitMeans') or {}).get('R')) for r in rs])
    rows[c] = diffs
    print(f"{c:5s} {len(rs):2d} {goats:6.0f} {herded:6.1f} | " + ' '.join(f'{diffs[t][0]:+6.2f}' if np.isfinite(diffs[t][0]) else '     -' for t in TRAITS) +
          f" | {g('herdFearOfHumans'):6.3f}  {g('herdF'):6.3f} {g('wildF'):6.3f} {g('siresPerCamp'):5.2f} {g('wildSiredShare'):9.3f} {g('capturedR'):6.3f} {rh:6.3f}")

# Ganj Dareh check: the herd's own mortality profile (all causes), final `win` years, every condition.
# Kids dying in their first weeks are excluded (an archaeological assemblage of mandibles under-records
# them); counts are of goats ≥ 1 year (bins 1..15) — the profile is read from age at death.
print('\nGanj Dareh check — herd deaths ≥ 1 y, all causes. Targets: of males, 0.60–0.70 dead before 2.5 y;'
      ' of females, 0.60–0.70 surviving past 2.5 y; ~0.20 of all goats past 4 y')
for c in conds:
    F = np.zeros(16); M = np.zeros(16)
    for r in runs[c]:
        for y in tail(r):
            ko = y.get('herdKilloff')
            if ko: F += ko['F']; M += ko['M']
    if (F + M)[1:].sum() == 0: continue
    F1, M1 = F[1:], M[1:]                                   # index 0 here = age 1 y
    m25 = (M1[0] + 0.5 * M1[1]) / M1.sum(); f25 = 1 - (F1[0] + 0.5 * F1[1]) / F1.sum()
    past4 = (F1[3:] + M1[3:]).sum() / (F1 + M1).sum()
    print(f"  {c}: {int((F1 + M1).sum())} deaths | males dead < 2.5 y {m25:.2f} | females past 2.5 y {f25:.2f} | past 4 y {past4:.2f} | male share {M1.sum() / (F1 + M1).sum():.2f}")

# figure 1: herded − wild trait differences per condition
hc = [c for c in conds if np.isfinite(rows[c]['R'][0])]
if hc:
    fig, ax = plt.subplots(figsize=(10, 4), constrained_layout=True)
    w = 0.8 / len(hc)
    for k, c in enumerate(hc):
        ax.bar(np.arange(len(TRAITS)) + k * w, [rows[c][t][0] for t in TRAITS], w, yerr=[rows[c][t][1] for t in TRAITS], label=c, capsize=2)
    ax.axhline(0, color='k', lw=0.6); ax.set_xticks(np.arange(len(TRAITS)) + 0.4 - w / 2, TRAITS)
    ax.set_ylabel(f'herded − wild genotype (final {win} y)'); ax.legend(fontsize=8)
    ax.set_title('Animal Domestication — the domestic-minus-wild suite by condition (mean ± sd over seeds)', fontsize=10)
    fig.savefig(os.path.join(out, 'conditions_herd_minus_wild.png'), dpi=140)
    # figure 2: herded R over time
    fig, ax = plt.subplots(figsize=(9, 4), constrained_layout=True)
    for c in hc:
        L = max(len(r['years']) for r in runs[c])
        M_ = np.full((len(runs[c]), L), np.nan)
        for i, r in enumerate(runs[c]):
            for j, y in enumerate(r['years']):
                if y.get('herdTraitMeans'): M_[i, j] = y['herdTraitMeans']['R']
        ax.plot(np.nanmean(M_, 0), label=f'{c} herded')
    wildR = np.nanmean([[wild_mean(y, 'R') or np.nan for y in r['years']] for r in runs[hc[0]]], 0)
    ax.plot(wildR, 'k--', lw=0.8, label=f'{hc[0]} wild')
    ax.set_xlabel('year'); ax.set_ylabel('genetic R'); ax.set_ylim(0, 1); ax.legend(fontsize=8)
    ax.set_title('Animal Domestication — herded genetic reactivity by condition', fontsize=10)
    fig.savefig(os.path.join(out, 'conditions_herd_R.png'), dpi=140)
    print('figures written')
