# herd_wild_means.py — absolute genetic means per trait, herd and wild, years 1901-2200, with their sums (the gene load).
#   python tools/herd_wild_means.py [folder:COND ...]   (default: the growth-cost set listed below)
import json,glob,os,sys,collections
TR='RASBHTMW'
SETS=[tuple(a.rsplit(':',1)) for a in sys.argv[1:]] or [('results/staged','H5'),('results/growherd','H5c033'),('results/growherd','H5c1'),('results/staged','STAGED'),('results/growherd','STAGEDc1')]
for folder,cond in SETS:
    acc=collections.defaultdict(list)
    for f in sorted(glob.glob(f'{folder}/{cond}_seed*.json')):
        ys=json.load(open(f))['years'][1900:2200]
        for r in ys:
            n,nh=r['goats'],r['herded']
            for t in TR:
                h=(r['herdTraitMeans'] or {}).get(t,0); a=r['traitMeans'][t]
                acc['h'+t].append(h); acc['w'+t].append((n*a-nh*h)/(n-nh) if n>nh else a)
            acc['goats'].append(n); acc['herd'].append(nh)
    m=lambda k:sum(acc[k])/len(acc[k])
    print(cond, 'goats %.0f herd %.0f'%(m('goats'),m('herd')),
      '| herd', ' '.join(f'{t}{m("h"+t):.2f}' for t in TR), 'sum %.2f'%sum(m('h'+t) for t in TR),
      '| wild', ' '.join(f'{t}{m("w"+t):.2f}' for t in TR), 'sum %.2f'%sum(m('w'+t) for t in TR))
