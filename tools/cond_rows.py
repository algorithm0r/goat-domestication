# cond_rows.py: condition means (over seeds) of per-run window means: wild goats, wild R (herd taken out),
# herded, herd R, fodder fed and cut, hunted, captured (EXPLOG 2026-10-31).
#   python tools/cond_rows.py <results folder> [window=100]
import json, sys, glob, os
from collections import defaultdict
win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
def wildR(y):
    h = y['herdTraitMeans']['R'] * y['herded'] if y.get('herdTraitMeans') else 0
    return (y['traitMeans']['R'] * y['goats'] - h) / (y['goats'] - y['herded'])
def m(xs): return sum(xs) / len(xs) if xs else None
cols = {'wild goats': lambda y: y['goats'] - y['herded'], 'wild R': wildR, 'herded': lambda y: y['herded'],
        'herd R': lambda y: y['herdTraitMeans']['R'] if y.get('herdTraitMeans') else None,
        'fodder fed': lambda y: y['fodder'], 'fodder cut': lambda y: y['foraged'],
        'hunted': lambda y: y['deaths'].get('hunted', 0), 'captured': lambda y: y['captured']}
rows = defaultdict(lambda: defaultdict(list))
for f in glob.glob(os.path.join(sys.argv[1], '*.json')):
    c = os.path.basename(f).split('_seed')[0]; w = json.load(open(f))['years'][-win:]
    for k, fn in cols.items():
        v = m([x for x in map(fn, w) if x is not None])
        if v is not None: rows[c][k].append(v)
fmt = lambda v: '—' if v is None else (f'{v:.3f}' if abs(v) < 5 else f'{v:,.0f}' if abs(v) >= 1000 else f'{v:.1f}')
print(f'results: {sys.argv[1]} | window: last {win} y | means over seeds (n)')
print('| condition | n | ' + ' | '.join(cols) + ' |'); print('|---' * (len(cols) + 2) + '|')
for c in sorted(rows):
    n = len(rows[c]['wild goats'])
    print(f'| {c} | {n} | ' + ' | '.join(fmt(m(rows[c][k])) for k in cols) + ' |')
