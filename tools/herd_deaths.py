# herd_deaths.py — herd and wild deaths by cause, per year and per goat-year, window means over seeds.
#   python tools/herd_deaths.py <results folder> [window=100]
# Needs year records with `herdDeaths` (code 17958ef on). Wild = all goats minus the herd.
import json, sys, glob, os, collections
folder = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
runs = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    runs[os.path.basename(f).rsplit('_seed', 1)[0]].append(json.load(open(f))['years'])
causes = None
print(f'results: {folder} | window: last {win} y | herd deaths per year (per herd goat-year); wild deaths per wild goat-year')
for c, rs in runs.items():
    hd = collections.Counter(); wd = collections.Counter(); hy = wy = n = 0
    for ys in rs:
        for r in ys[-win:]:
            if causes is None: causes = list(r['deaths'])
            h = r.get('herdDeaths') or {}
            for k in causes: hd[k] += h.get(k, 0); wd[k] += r['deaths'][k] - h.get(k, 0)
            hy += r['herded']; wy += r['goats'] - r['herded']; n += 1
    if c == list(runs)[0]:
        print('| condition | n | herded | ' + ' | '.join(causes) + ' | all |'); print('|' + '---|' * (len(causes) + 4))
    cell = lambda d, k, g: f'{d[k] / n:.2f} ({d[k] / g:.3f})' if g else '—'
    tot = lambda d: sum(d.values())
    print(f'| {c} herd | {len(rs)} | {hy / n:.1f} | ' + ' | '.join(cell(hd, k, hy) for k in causes) + f' | {tot(hd) / n:.2f} ({tot(hd) / hy if hy else 0:.3f}) |')
    print(f'| {c} wild | {len(rs)} | — | ' + ' | '.join(f'({wd[k] / wy:.3f})' for k in causes) + f' | ({tot(wd) / wy:.3f}) |')
