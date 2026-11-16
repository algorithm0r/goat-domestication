# wolf_probe_rows.py — tables from tools/wolf_probe.mjs outputs, summed over seeds per condition.
#   python tools/wolf_probe_rows.py <folder>
import json, sys, glob, os, collections
runs = collections.defaultdict(list)
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*_seed*.json'))): runs[os.path.basename(f).rsplit('_seed', 1)[0]].append(json.load(open(f)))
def tot(rs, *ks):
    v = 0
    for r in rs:
        x = r
        for k in ks: x = x[k]
        v += x
    return v
print(f'results: {sys.argv[1]} | per goat-sub-tick during bouts (pre: after wolves move; post: after goats step) | sums over seeds')
print('| condition | n | group | goat-years | pre | post | post/pre | wolves within 3 | on escape terrain | cells to camp | strikes/goat-y | kills/strike |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for c, rs in runs.items():
    for g in ('herd', 'wild'):
        n = tot(rs, 'goatSubticks', g); gy = tot(rs, 'goatYears', g); st = tot(rs, 'strikes', g); kl = tot(rs, 'kills', g)
        pre, post = tot(rs, 'pre', g) / n, tot(rs, 'post', g) / n
        print(f'| {c} | {len(rs)} | {g} | {gy:.0f} | {pre:.4f} | {post:.4f} | {post / pre if pre else 0:.2f} | {tot(rs, "near3", g) / n:.3f} | {tot(rs, "escapeShare", g) / n:.2f} | {tot(rs, "campDist", g) / n:.1f} | {st / gy if gy else 0:.2f} | {kl / st if st else 0:.3f} |')
print('\n| condition | hunting wolves: cells to camp | wolf-bouts hunting goats | wolf-bouts striking a herd | herd strikes in bouts of 1 / 2 / 3-5 / 6-10 / 11+ | share of herd bouts with a herd kill | share ended by a guard kill |')
print('|---|---|---|---|---|---|---|')
for c, rs in runs.items():
    hb = tot(rs, 'herdBouts'); byrun = collections.Counter()
    for r in rs: byrun.update(r['herdStrikesByRun'])
    hs = sum(byrun.values())
    sh = ' / '.join(f'{byrun.get(b, 0) / hs:.2f}' for b in ['1', '2', '3-5', '6-10', '11+']) if hs else '—'
    print(f'| {c} | {tot(rs, "wolfCampDist") / tot(rs, "wolfN"):.1f} | {tot(rs, "boutsHuntingGoats")} | {hb} | {sh} | {tot(rs, "herdBoutKill") / hb if hb else 0:.2f} | {tot(rs, "herdBoutGuardKilled") / hb if hb else 0:.2f} |')
