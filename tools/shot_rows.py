# shot_rows.py: per-run window means for the stalk vs shot test (EXPLOG 2026-10-30).
#   python tools/shot_rows.py <results folder> [window=100]
import json,sys,glob,os
# per-run means over a window: wild goats, wild R, herded, herd R, hunted kills, shots, shot kills, captured
win=int(sys.argv[2]) if len(sys.argv)>2 else 100
for f in sorted(glob.glob(os.path.join(sys.argv[1],'*.json'))):
    d=json.load(open(f)); ys=d['years'] if 'years' in d else d['data']['years']
    w=ys[-win:]; m=lambda xs:sum(xs)/len(xs) if xs else float('nan')
    wild=[y['goats']-y['herded'] for y in w]
    # traitMeans cover all goats, herd included: take the herd out for wild R
    R=[(y['traitMeans']['R']*y['goats']-(y['herdTraitMeans']['R']*y['herded'] if y.get('herdTraitMeans') else 0))/(y['goats']-y['herded']) for y in w]
    hR=[y['herdTraitMeans']['R'] for y in w if y.get('herdTraitMeans')]
    print(f"{os.path.basename(f)[:-5]:12} y{w[0]['year']}-{w[-1]['year']} wild {m(wild):6.0f} R {m(R):.3f} herded {m([y['herded'] for y in w]):5.1f} herdR {m(hR):.3f} hunted {m([y['deaths'].get('hunted',0) for y in w]):5.1f} shots {m([y.get('shots',0) for y in w]):6.0f} shotKills {m([y.get('shotKills',0) for y in w]):4.1f} captured {m([y['captured'] for y in w]):4.1f}")
