# trait_gaps.py — herd − wild gap per trait, herd and wild IBD, wild-sired share, sires per camp, generations since
# capture, per window; means over seeds (years with a herd).
#   python tools/trait_gaps.py <results folder> [window=100] [from=400]
import json, sys, glob, os
folder = sys.argv[1]; win = int(sys.argv[2]) if len(sys.argv) > 2 else 100; y0 = int(sys.argv[3]) if len(sys.argv) > 3 else 400
runs = [json.load(open(f))['years'] for f in glob.glob(os.path.join(folder, '*_seed*.json'))]
T = 'RASBHTMW'; m = lambda L: sum(L) / len(L) if L else float('nan')
print(f'results: {folder} | windows of {win} y from year {y0 + 1} | herd − wild genetic mean per trait | means over {len(runs)} seeds')
print('| years | ' + ' | '.join(T) + ' | herd IBD | wild IBD | wild-sired | sires/camp | gens since capture |'); print('|---' * (len(T) + 6) + '|')
for a in range(y0, min(len(r) for r in runs), win):
    acc = {t: [] for t in T}; ex = {k: [] for k in ('herdF', 'wildF', 'wildSiredShare', 'siresPerCamp', 'herdGSC')}
    for ys in runs:
        for y in ys[a:a + win]:
            hm, n, nh = y.get('herdTraitMeans'), y['goats'], y['herded']
            if not hm or not nh: continue
            for t in T:
                if hm.get(t) is not None: acc[t].append(hm[t] - (y['traitMeans'][t] * n - hm[t] * nh) / (n - nh))
            for k in ex:
                if isinstance(y.get(k), (int, float)): ex[k].append(y[k])
    print(f'| {a + 1}-{a + win} | ' + ' | '.join(f'{m(acc[t]):+.2f}' for t in T) + f" | {m(ex['herdF']):.2f} | {m(ex['wildF']):.2f} | {m(ex['wildSiredShare']):.3f} | {m(ex['siresPerCamp']):.1f} | {m(ex['herdGSC']):.1f} |")
