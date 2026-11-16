# h5_trend.py — herd size, births, captures, herd R, wild R and the gap per window, means over seeds; last window by seed.
#   python tools/h5_trend.py <results folder> [window=100] [from=400]
import json, sys, glob, os
folder = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100; y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 400
runs = {os.path.basename(f): json.load(open(f))['years'] for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json')), key=lambda f: int(f.rsplit('_seed', 1)[1][:-5]))}
def row(ys):
    h = b = c = 0; hr = []; wr = []
    for y in ys:
        n, nh, hm = y['goats'], y['herded'], y.get('herdTraitMeans')
        h += nh; b += y.get('herdBirths', 0); c += y.get('captured', 0)
        w = (y['traitMeans']['R'] * n - (hm['R'] * nh if hm and nh else 0)) / (n - nh); wr.append(w)
        if hm and nh: hr.append(hm['R'])
    k = len(ys); H = sum(hr) / len(hr) if hr else float('nan'); Wr = sum(wr) / len(wr)
    return h / k, b / k, c / k, H, Wr, H - Wr
print(f'results: {folder} | windows of {win} y from year {y0 + 1} | means over {len(runs)} seeds (herd R: years with a herd)')
print('| years | herded | herd births/y | captures/y | herd R | wild R | herd − wild R | gap range over seeds |'); print('|---|---|---|---|---|---|---|---|')
L = min(len(v) for v in runs.values())
for a in range(y0, L, win):
    rs = [row(v[a:a + win]) for v in runs.values()]
    m = [sum(r[i] for r in rs) / len(rs) for i in range(6)]; g = [r[5] for r in rs]
    print(f'| {a + 1}-{a + win} | {m[0]:.1f} | {m[1]:.1f} | {m[2]:.1f} | {m[3]:.3f} | {m[4]:.3f} | {m[5]:+.3f} | {min(g):+.2f} to {max(g):+.2f} |')
print(f'\nlast {win} y by seed:'); print('| seed | herded | herd births/y | captures/y | herd R | wild R | herd − wild R |'); print('|---|---|---|---|---|---|---|')
for f, v in runs.items():
    r = row(v[-win:]); print(f'| {f.rsplit("_seed", 1)[1][:-5]} | {r[0]:.0f} | {r[1]:.1f} | {r[2]:.1f} | {r[3]:.3f} | {r[4]:.3f} | {r[5]:+.3f} |')
