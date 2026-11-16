"""attr_table.py — raw tables for the rebuild attribution commit walk (EXPLOG 2026-10-25).

  python tools/attr_table.py <results/attr> [window=100] [commit ...]

For each condition, one row per code point (in the order given, else folder order): goats, herded,
wild R, herd − wild R (per seed), wild S/B/A, herd − wild B, herd and wild IBD, wild-sired share; for
herding conditions the herd kill-off profile (deaths ≥ 1 y, all causes; Ganj Dareh check as in
condition_table.py). Means over seeds; numbers only.
"""
import json, glob, os, sys, statistics as st
import numpy as np

root = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
commits = sys.argv[3:] or sorted(d for d in os.listdir(root) if not d.startswith('_') and os.path.isdir(os.path.join(root, d)))

def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None
def f(x, p='%.2f'): return '—' if x is None else p % x

def wild_mean(y, t):
    n, nh, hm = y['goats'], y.get('herded') or 0, y.get('herdTraitMeans')
    if n <= nh or y['traitMeans'].get(t) is None: return None
    return (y['traitMeans'][t] * n - (hm[t] * nh if hm and nh else 0)) / (n - nh)

def run_stats(path):
    d = json.load(open(path)); ys = d['years'][-win:]
    r = {}
    r['goats'] = mean([y['goats'] for y in ys]); r['herded'] = mean([y.get('herded') or 0 for y in ys])
    for t in ('R', 'S', 'B', 'A'): r['w' + t] = mean([wild_mean(y, t) for y in ys])
    gapR, gapB = [], []
    for y in ys:
        hm = y.get('herdTraitMeans')
        if hm and (y.get('herded') or 0) > 0:
            wR, wB = wild_mean(y, 'R'), wild_mean(y, 'B')
            if wR is not None: gapR.append(hm['R'] - wR)
            if wB is not None: gapB.append(hm['B'] - wB)
    r['gapR'] = mean(gapR); r['gapB'] = mean(gapB)
    r['hF'] = mean([y.get('herdF') for y in ys]); r['wF'] = mean([y.get('wildF') for y in ys])
    r['ws'] = mean([y.get('wildSiredShare') for y in ys])
    r['fH'] = mean([(y.get('learnedFear') or {}).get('humans') for y in ys]); r['fW'] = mean([(y.get('learnedFear') or {}).get('wolves') for y in ys])
    r['hfH'] = mean([y.get('herdFearOfHumans') for y in ys])
    F = np.zeros(16); M = np.zeros(16)
    for y in ys:
        ko = y.get('herdKilloff')
        if ko: F += ko['F']; M += ko['M']
    r['ko'] = (F, M)
    return r

conds = None
for c in commits:
    fs = glob.glob(os.path.join(root, c, '*_seed*.json'))
    cs = sorted({os.path.basename(x).split('_seed')[0] for x in fs})
    conds = conds or cs
print(f'results: {root} | window: last {win} y | means over seeds (per seed in brackets)')
for k in conds:
    print(f'\n### {k}')
    print('| code | n | goats | herded (per seed) | wild R | herd − wild R (per seed) | wild S | wild B | wild A | herd − wild B | IBD herd / wild | wild-sired | fear humans (all / herd) | fear wolves | males dead < 2.5 y | does past 2.5 y | past 4 y |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for c in commits:
        fs = sorted(glob.glob(os.path.join(root, c, f'{k}_seed*.json')))
        rs = []
        for x in fs:
            try: rs.append(run_stats(x))
            except Exception: pass
        if not rs: print(f'| {c} | 0 |' + ' |' * 15); continue
        g = lambda key: mean([r[key] for r in rs])
        per = lambda key, p: ' '.join(f(r[key], p) for r in rs)
        F = sum(r['ko'][0] for r in rs); M = sum(r['ko'][1] for r in rs)
        F1, M1 = F[1:], M[1:]
        if (F1 + M1).sum() > 0 and M1.sum() > 0 and F1.sum() > 0:
            m25 = (M1[0] + 0.5 * M1[1]) / M1.sum(); f25 = 1 - (F1[0] + 0.5 * F1[1]) / F1.sum(); p4 = (F1[3:] + M1[3:]).sum() / (F1 + M1).sum()
            ko = f'{m25:.2f} | {f25:.2f} | {p4:.2f}'
        else: ko = '— | — | —'
        print(f"| {c} | {len(rs)} | {f(g('goats'), '%.0f')} | {f(g('herded'), '%.0f')} ({per('herded', '%.0f')}) | {f(g('wR'))} | {f(g('gapR'), '%+.2f')} ({per('gapR', '%+.2f')}) | "
              f"{f(g('wS'))} | {f(g('wB'))} | {f(g('wA'))} | {f(g('gapB'), '%+.2f')} | {f(g('hF'))} / {f(g('wF'))} | {f(g('ws'))} | {f(g('fH'))} / {f(g('hfH'))} | {f(g('fW'))} | {ko} |")
