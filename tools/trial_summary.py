"""trial_summary.py — raw-results table for an EXPLOG entry: one row per condition in a results folder.

  python tools/trial_summary.py <results/dir> [window_years=100]

Conditions are the file-name prefixes before _seed<N>.json or _s<N>.json. Over the last `window_years`
of each run, it reports means across seeds (per-seed values in brackets where they matter): goats,
herded goats, wild R, herd R − wild R, and, when the run had the economy, demand unmet and the
labour shares. Numbers only; no interpretation.
"""
import json, glob, os, re, sys, statistics as st

d = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
files = sorted(glob.glob(os.path.join(d, '*.json')))
groups = {}
for f in files:
    m = re.match(r'(.*?)_?(?:seed|s)(\d+)\.json$', os.path.basename(f))
    if m: groups.setdefault(m.group(1) or '(all)', []).append(f)

def mean(xs): xs = [x for x in xs if x is not None]; return st.mean(xs) if xs else None
def fmt(x, p='%.2f'): return '—' if x is None else p % x

print(f'results: {d} | window: last {win} y | seeds per condition in n')
print('| condition | n | years | goats | herded (per seed) | wild R | herd − wild R (per seed) | unmet % | gather/hunt/herd |')
print('|---|---|---|---|---|---|---|---|---|')
for c, fs in groups.items():
    rows = []
    for f in fs:
        try: dd = json.load(open(f))
        except Exception: continue
        ys = dd['years'] if isinstance(dd, dict) and 'years' in dd else dd
        if not ys: continue
        L = ys[-win:]
        wild, gap = [], []
        for y in L:
            n, nh, hm = y['goats'], y.get('herded', 0) or 0, y.get('herdTraitMeans')
            if n > nh:
                wr = (y['traitMeans']['R'] * n - (hm['R'] * nh if hm and nh else 0)) / (n - nh) if y['traitMeans']['R'] is not None else None
                wild.append(wr)
                if hm and nh: gap.append(hm['R'] - wr)
        e = [y['econ'] for y in L if y.get('econ')]
        unmet = 100 * sum(x['unmet'] for x in e) / sum(x['demand'] for x in e) if e and sum(x['demand'] for x in e) else None
        sh = None
        if e:
            tot = [sum(x['roleDays'].values()) or 1 for x in e]
            sh = tuple(mean([x['roleDays'][r] / t for x, t in zip(e, tot)]) for r in ('gather', 'hunt', 'herd'))
        rows.append(dict(years=ys[-1]['year'] + 1, goats=mean([y['goats'] for y in L]), herded=mean([y.get('herded', 0) for y in L]),
                         wild=mean(wild), gap=mean(gap), unmet=unmet, sh=sh))
    if not rows: continue
    g = lambda k: mean([r[k] for r in rows])
    per = lambda k, p: ' '.join(fmt(r[k], p) for r in rows)
    sh = '/'.join(fmt(mean([r['sh'][i] for r in rows if r['sh']])) for i in range(3)) if any(r['sh'] for r in rows) else '—'
    print(f"| {c} | {len(rows)} | {min(r['years'] for r in rows)} | {fmt(g('goats'), '%.0f')} | {fmt(g('herded'), '%.0f')} ({per('herded', '%.0f')}) | "
          f"{fmt(g('wild'))} | {fmt(g('gap'), '%+.2f')} ({per('gap', '%+.2f')}) | {fmt(g('unmet'), '%.1f')} | {sh} |")
