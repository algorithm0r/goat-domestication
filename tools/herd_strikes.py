# herd_strikes.py — wolf strikes on herd goats, wolves chased off, and herd predation per year (all camps), window means over seeds.
#   python tools/herd_strikes.py <results folder> [window=100]
# Needs year records with `wolfAtk` (code a6f486e on); wolvesChased from 686c2e2 (0 before).
import json, sys, glob, os, collections
folder = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100
R = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    c = os.path.basename(f).rsplit('_seed', 1)[0]
    for r in json.load(open(f))['years'][-win:]:
        t = R[c]; t[0] += sum(v[0] for k, v in (r.get('wolfAtk') or {}).items() if k.startswith('herd'))
        t[1] += r['herded']; t[2] += r.get('wolvesChased', 0); t[3] += (r.get('herdDeaths') or {}).get('predation', 0); t[4] += 1
print(f'results: {folder} | window: last {win} y | per year, all camps, means over seeds')
print('| condition | herded | herd strikes | wolves chased | herd predation | strikes per herd goat-year |'); print('|---|---|---|---|---|---|')
for c, (a, h, ch, pr, n) in R.items():
    print(f'| {c} | {h / n:.1f} | {a / n:.1f} | {ch / n:.1f} | {pr / n:.2f} | {a / h if h else 0:.2f} |')
