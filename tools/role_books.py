"""role_books.py — per camp-year food books and returns by role (EXPLOG 2026-10-28, need-relative returns).

  python tools/role_books.py <results/dir> [window_years=100] [dir ...]

One row per condition (file-name prefix before _seed<N>.json, over every dir given), sums over seeds and
the last `window_years`, divided by camp-years: demand, plant food gathered and as scored, meat hunted and
as scored, plant and meat eaten, unmet; labour-days by role; mean return per labour-day by role (the
estimate's input as the run recorded it). Numbers only.
"""
import json, glob, os, re, sys

win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
dirs = [sys.argv[1]] + sys.argv[3:]
groups = {}
for d in dirs:
    for f in sorted(glob.glob(os.path.join(d, '*.json'))):
        m = re.match(r'(.*?)_?(?:seed|s)(\d+)\.json$', os.path.basename(f))
        if m: groups.setdefault(m.group(1), []).append(f)

R = ('gather', 'hunt', 'herd')
print(f'results: {", ".join(dirs)} | window: last {win} y | per camp-year, sums over seeds')
print('| condition | n | demand | gathered (scored) | hunted (scored) | plant eaten | meat eaten | unmet | labour-days gather/hunt/herd | return per labour-day gather/hunt/herd |')
print('|---|---|---|---|---|---|---|---|---|---|')
for c, fs in groups.items():
    T, cy, n = {}, 0, 0
    for f in fs:
        try: dd = json.load(open(f))
        except Exception: continue
        n += 1; ys = [y for y in dd['years'][-win:] if y.get('econ')]; cy += len(ys) * dd['params']['camps']
        for y in ys:
            e = y['econ']
            for k in ('demand', 'foodGathered', 'gatherScored', 'meatHunted', 'huntScored', 'plantEaten', 'meatEaten', 'unmet'):
                if e.get(k) is not None: T[k] = T.get(k, 0) + e[k]
            for r in R:
                T['d' + r] = T.get('d' + r, 0) + e['roleDays'][r]
                T['r' + r] = T.get('r' + r, 0) + (e['roleReturn'][r] or 0) * e['roleDays'][r]
    if not cy: continue
    g = lambda k: '—' if k not in T else '%.0f' % (T[k] / cy)
    ret = '/'.join('%.2f' % (T['r' + r] / T['d' + r]) if T['d' + r] else '—' for r in R)
    print(f"| {c} | {n} | {g('demand')} | {g('foodGathered')} ({g('gatherScored')}) | {g('meatHunted')} ({g('huntScored')}) | {g('plantEaten')} | {g('meatEaten')} | {g('unmet')} | "
          f"{'/'.join(g('d' + r) for r in R)} | {ret} |")
