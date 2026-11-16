# gen_trace.py — generations since wild in the herd, per window, means over seeds: maternal line (herd goats), sire line
# (herd males), herd genome share by depth (mean ancestry depth); per condition.
#   python tools/gen_trace.py <results folder> [window=100] [from=400]
# Needs year records with herdMatGen / herdPatGen / herdWildAnc (code of 2026-11-01 on). Bins 0 | 1 | 2-4 | 5-9 | 10-19 | 20+.
import json, sys, glob, os, collections
folder = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100; y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 400
BINS = ['0', '1', '2-4', '5-9', '10-19', '20+']
runs = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    runs[os.path.basename(f).rsplit('_seed', 1)[0]].append(json.load(open(f))['years'])
print(f'results: {folder} | windows of {win} y from year {y0 + 1} | shares in bins of generations since wild: ' + ' / '.join(BINS))
for c, rs in runs.items():
    print(f'\n### {c} (n {len(rs)})')
    print('| years | herded | maternal line (herd goats) | sire line (herd males) | genome by depth | mean genome depth |'); print('|---|---|---|---|---|---|')
    for a in range(y0, min(len(r) for r in rs), win):
        mat = [0] * 6; pat = [0] * 6; anc = [0.0] * 6; dep = h = n = 0
        for ys in rs:
            for y in ys[a:a + win]:
                if not y.get('herdMatGen'): continue
                n += 1; h += y['herded']
                for b in range(6): mat[b] += y['herdMatGen'][b]; pat[b] += y['herdPatGen'][b]; anc[b] += y['herdWildAnc'][b] * y['herded']
                dep += y['herdAncDepth'] * y['herded']
        if not n: continue
        sh = lambda v: ' / '.join(f'{x / sum(v):.2f}' for x in v) if sum(v) else '—'
        print(f'| {a + 1}-{a + win} | {h / n:.1f} | {sh(mat)} | {sh(pat)} | {sh(anc)} | {dep / h:.1f} |')
