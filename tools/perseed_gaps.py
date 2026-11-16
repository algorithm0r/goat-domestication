# perseed_gaps.py — per seed, years 1101-1200: herd size, wild size, herd − wild gaps for R A S B, absolute herd and wild B.
#   python tools/perseed_gaps.py <results folder> [COND ...]   (default Prand Pmeat Pflight Preturn Pattack)
import json, glob, os, sys
folder = sys.argv[1]; conds = sys.argv[2:] or ['Prand','Pmeat','Pflight','Preturn','Pattack']
for c in conds:
    rows = []
    for f in sorted(glob.glob(os.path.join(folder, f'{c}_seed*.json'))):
        ys = json.load(open(f))['years'][1100:1200]
        hw = [r for r in ys if r['herded'] > 0]
        def wild(r, t):
            n, nh = r['goats'], r['herded']; a, h = r['traitMeans'][t], r['herdTraitMeans'][t]
            return (n*a - nh*h)/(n-nh) if n > nh else a
        g = {t: sum(r['herdTraitMeans'][t] - wild(r, t) for r in hw)/len(hw) for t in 'RASB'}
        hb = sum(r['herdTraitMeans']['B'] for r in hw)/len(hw); wb = sum(wild(r,'B') for r in hw)/len(hw)
        rows.append(f"s{f.rsplit('seed',1)[1][:-5]} herd {sum(r['herded'] for r in ys)/len(ys):5.1f} wild {sum(r['goats']-r['herded'] for r in ys)/len(ys):5.0f} " + ' '.join(f'{t}{g[t]:+.2f}' for t in 'RASB') + f'  B herd {hb:.2f} wild {wb:.2f}')
    print(c); print('\n'.join('  '+r for r in rows))
