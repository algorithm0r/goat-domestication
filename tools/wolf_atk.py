# wolf_atk.py — wolf attacks on herd and wild goats by circumstance, window sums over seeds.
#   python tools/wolf_atk.py <results folder> [window=100]
# Needs year records with `wolfAtk` (code a6f486e on): key herd/wild|phase|escape|camp|alarmed|loose|kid → [attacks, kills].
import json, sys, glob, os, collections
folder = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
FIELDS = ['phase', 'escape', 'camp', 'alarmed', 'loose', 'kid', 'nearHerder']   # nearHerder from code of 2026-10-31 (herderProtection)
runs = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    runs[os.path.basename(f).rsplit('_seed', 1)[0]].append(json.load(open(f))['years'])
print(f'results: {folder} | window: last {win} y | sums over seeds')
for c, rs in runs.items():
    A = collections.Counter(); K = collections.Counter(); gy = {'herd': 0, 'wild': 0}; n = 0
    for ys in rs:
        for r in ys[-win:]:
            gy['herd'] += r['herded']; gy['wild'] += r['goats'] - r['herded']; n += 1
            for key, (a, k) in (r.get('wolfAtk') or {}).items():
                A[tuple(key.split('|'))] += a; K[tuple(key.split('|'))] += k
    print(f'\n### {c} (n {len(rs)})')
    print('| group | goat-years | attacks/goat-y | kills/goat-y | kills/attack |'); print('|---|---|---|---|---|')
    for g in ('herd', 'wild'):
        a = sum(v for t, v in A.items() if t[0] == g); k = sum(v for t, v in K.items() if t[0] == g)
        print(f'| {g} | {gy[g]:.0f} | {a / gy[g] if gy[g] else 0:.3f} | {k / gy[g] if gy[g] else 0:.4f} | {k / a if a else 0:.3f} |')
    print('| group | field | value | share of attacks | kills/attack | kills/goat-y |'); print('|---|---|---|---|---|---|')
    for g in ('herd', 'wild'):
        a_all = sum(v for t, v in A.items() if t[0] == g)
        for fi, fname in enumerate(FIELDS, 1):
            if g == 'wild' and fname in ('loose', 'nearHerder'): continue
            for val in sorted({t[fi] for t in A if t[0] == g and len(t) > fi}):
                a = sum(v for t, v in A.items() if t[0] == g and len(t) > fi and t[fi] == val); k = sum(v for t, v in K.items() if t[0] == g and len(t) > fi and t[fi] == val)
                print(f'| {g} | {fname} | {val} | {a / a_all if a_all else 0:.3f} | {k / a if a else 0:.3f} | {k / gy[g] if gy[g] else 0:.4f} |')
