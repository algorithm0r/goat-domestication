"""store_table.py — the camp economy's food books by season (shelf-life stores, EXPLOG 2026-10-28).

  python tools/store_table.py <results/dir> [window_years=100] [file ...]

One row per condition (file-name prefix before _seed<N>.json), means over seeds of yearly values over the
last `window_years`: unmet share of demand (year, and by quarter of the year: days 0–91, 91–182,
182–274, 274–365), slaughter per year (and by quarter), herding share of labour (year, by quarter), herd
births per year, mean herd, and, per camp-year, fu dried, dried meat lost, plant food to slop, slop to
the heap, fodder lost. Quarter columns need runs from the windows code (blank otherwise). Numbers only.
"""
import json, glob, os, re, sys, statistics as st

d = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
files = sys.argv[3:] or sorted(glob.glob(os.path.join(d, '*.json')))
groups = {}
for f in files:
    m = re.match(r'(.*?)_?(?:seed|s)(\d+)\.json$', os.path.basename(f))
    if m: groups.setdefault(m.group(1), []).append(f)

def mean(xs): xs = [x for x in xs if x is not None]; return st.mean(xs) if xs else None
def fmt(x, p='%.2f'): return '—' if x is None else p % x
def q4(xs, p): return '/'.join(fmt(x, p) for x in xs) if xs and all(x is not None for x in xs) else '—'

print(f'results: {d} | window: last {win} y | means over seeds')
print('| condition | n | herded | unmet % (Q1/Q2/Q3/Q4) | slaughter/y (Q1/Q2/Q3/Q4) | herding share (Q1/Q2/Q3/Q4) | herd births/y | dried | dried lost | plant → slop | slop → heap | fodder lost |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for c, fs in groups.items():
    R = []
    for f in fs:
        try: dd = json.load(open(f))
        except Exception: continue
        P = dd['params']; ys = [y for y in dd['years'][-win:] if y.get('econ')]
        if not ys: continue
        camps = P['camps']; E = [y['econ'] for y in ys]
        r = {}
        r['herded'] = mean([y.get('herded') or 0 for y in ys])
        r['unmet'] = 100 * sum(e['unmet'] for e in E) / sum(e['demand'] for e in E)
        qd = sum(e['demand'] for e in E) / 4   # demand is flat over the year
        r['unmetQ'] = [100 * sum(e['unmetQ'][k] for e in E) / qd for k in range(4)] if 'unmetQ' in E[0] else None
        r['sl'] = mean([y.get('culledHerd') or 0 for y in ys])
        r['slQ'] = [mean([e['slaughterQ'][k] for e in E]) for k in range(4)] if 'slaughterQ' in E[0] else None
        rd = [sum(e['roleDays'].values()) for e in E]
        r['herd'] = sum(e['roleDays']['herd'] for e in E) / max(1, sum(rd))
        r['herdQ'] = [sum(e['herdQ'][k] for e in E) / max(1, sum(e['labourQ'][k] for e in E)) for k in range(4)] if 'herdQ' in E[0] else None
        r['births'] = mean([y.get('herdBirths') or 0 for y in ys])
        for k in ('dried', 'driedLost', 'slopMade', 'heap', 'fodderLost'): r[k] = mean([e.get(k) for e in E]) / camps if E[0].get(k) is not None else None
        R.append(r)
    if not R: continue
    g = lambda k: mean([r[k] for r in R])
    gq = lambda k: [mean([r[k][i] for r in R]) for i in range(4)] if all(r[k] for r in R) else None
    print(f"| {c} | {len(R)} | {fmt(g('herded'), '%.1f')} | {fmt(g('unmet'), '%.1f')} ({q4(gq('unmetQ'), '%.1f')}) | {fmt(g('sl'), '%.1f')} ({q4(gq('slQ'), '%.1f')}) | "
          f"{fmt(g('herd'))} ({q4(gq('herdQ'), '%.2f')}) | {fmt(g('births'), '%.1f')} | {fmt(g('dried'), '%.0f')} | {fmt(g('driedLost'), '%.0f')} | "
          f"{fmt(g('slopMade'), '%.0f')} | {fmt(g('heap'), '%.0f')} | {fmt(g('fodderLost'), '%.0f')} |")
