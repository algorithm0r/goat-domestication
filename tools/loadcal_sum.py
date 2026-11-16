import json, glob, os, collections, sys
folder = sys.argv[1]; a, b = int(sys.argv[2]), int(sys.argv[3])
runs = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    runs[os.path.basename(f).rsplit('_seed', 1)[0]].append(json.load(open(f))['years'])
print(f'years {a+1}-{b}, means over seeds (n)')
print('| cond | n | goats | births/y | births per goat | median 1st kid age (d) | load | R | A | S | B | H | T | M | W |'); print('|---' * 15 + '|')
for c in sorted(runs):
    rs = runs[c]; m = lambda f: sum(sum(f(r) for r in ys[a:b]) / (b - a) for ys in rs) / len(rs)
    tm = {t: m(lambda r: r['traitMeans'][t]) for t in 'RASBHTMW'}
    fk = [r['medianFirstKidAge'] for ys in rs for r in ys[a:b] if r['medianFirstKidAge']]
    print(f'| {c} | {len(rs)} | {m(lambda r: r["goats"]):.0f} | {m(lambda r: r["births"]):.0f} | {m(lambda r: r["births"] / r["goats"]):.3f} | {sorted(fk)[len(fk)//2] if fk else "—"} | {sum(tm.values()):.2f} | ' + ' | '.join(f'{tm[t]:.2f}' for t in 'RASBHTMW') + ' |')
