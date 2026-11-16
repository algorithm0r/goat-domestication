# stage_table.py — per 100-y window and condition: herded, herd − wild genetic mean per trait, and herd and wild
# learned fear of wolves and of humans. Means over seeds of window means. Needs herdFearOfWolves (code of 2026-11-02 on).
#   python tools/stage_table.py <results folder> [from=300] [win=100]
import json, sys, glob, os, collections
folder = sys.argv[1]; opt = dict(a.split('=', 1) for a in sys.argv[2:] if '=' in a)
y0 = int(opt.get('from', 300)); win = int(opt.get('win', 100))
runs = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(folder, '*_seed*.json'))):
    runs[os.path.basename(f).rsplit('_seed', 1)[0]].append(json.load(open(f))['years'])
TR = 'RASBHTMW' + ('L' if all('L' in ys[0]['traitMeans'] for rs in runs.values() for ys in rs) else '')   # L: twinning runs

def wild(r, a, h):                    # wild mean from the all-goat and herd means
    n, nh = r['goats'], r['herded']
    return (n * a - nh * h) / (n - nh) if h is not None and n > nh else a

print(f'results: {folder} | windows of {win} y from year {y0 + 1} | herd − wild genetic mean per trait | learned fear herd / wild | means over seeds')
for c, rs in runs.items():
    print(f'\n### {c} (n {len(rs)})')
    print('| years | herded | ' + ' | '.join(TR) + ' | fear of wolves h / w | fear of humans h / w |'); print('|---' * (len(TR) + 4) + '|')
    for a in range(y0, min(len(ys) for ys in rs), win):
        acc = collections.defaultdict(list)
        for ys in rs:
            w = ys[a:a + win]; acc['herded'].append(sum(r['herded'] for r in w) / len(w))
            hw = [r for r in w if r['herded'] > 0]
            for t in TR:
                if hw: acc[t].append(sum(r['herdTraitMeans'][t] - wild(r, r['traitMeans'][t], r['herdTraitMeans'][t]) for r in hw) / len(hw))
            for k, hk in (('wolves', 'herdFearOfWolves'), ('humans', 'herdFearOfHumans')):
                if hw: acc[k + 'h'].append(sum(r[hk] for r in hw) / len(hw))
                acc[k + 'w'].append(sum(wild(r, r['learnedFear'][k], r.get(hk)) for r in w) / len(w))
        m = lambda k: f'{sum(acc[k]) / len(acc[k]):+.2f}' if acc[k] else '—'
        f = lambda k: f'{sum(acc[k]) / len(acc[k]):.2f}' if acc[k] else '—'
        print(f'| {a + 1}-{a + win} | {sum(acc["herded"]) / len(acc["herded"]):.1f} | ' + ' | '.join(m(t) for t in TR)
              + f' | {f("wolvesh")} / {f("wolvesw")} | {f("humansh")} / {f("humansw")} |')
