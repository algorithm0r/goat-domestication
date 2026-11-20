# pair_tab.py: are outcomes of the same seed correlated across arms? (analysis session, 2026-11-20; the check before
# choosing unpaired SEs, plan for review finding 9). Arms run with the same seed share every random draw until their
# settings first differ (herding starts in year 400), so the founders are the same goats and later outcomes may covary.
#   python tools/pair_tab.py Y0-Y1 "DIR[;DIR...]" [--perm 2000] [--seed 1] [--bad shuffle]
# Per run, over Y0-Y1: gap, herd change and wild change of each trait (tools/split_tab.py, founders 301-400). For each
# pair of arms (both with seeds 1..n, n >= 4) and each measure: Pearson r across the shared seeds. Reported per measure:
# mean r over all arm pairs, and its permutation null (seeds shuffled within one arm of each pair, independently per
# pair, --perm times): the null's mean and 95% range, and p = share of null means >= the observed mean.
# Also the paired/unpaired variance ratio of a difference, 1 - mean r (the factor by which a paired SE^2 shrinks).
# --bad shuffle: the observed values are themselves computed with seeds shuffled, which must bring mean r into the null.
import glob, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab
TRAITS = split_tab.TRAITS

def pearson(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = sum((a - mx) ** 2 for a in x) ** 0.5; sy = sum((b - my) ** 2 for b in y) ** 0.5
    return None if sx == 0 or sy == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)

def main():
    a = sys.argv[1:]; opt = {"--perm": "2000", "--seed": "1", "--bad": None}
    for k in list(opt):
        if k in a: i = a.index(k); opt[k] = a[i + 1]; del a[i:i + 2]
    y0, y1 = (int(v) for v in a[0].split("-")); rng = random.Random(int(opt["--seed"]))
    R = {}
    for folder in a[1].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    V = {}                                            # arm -> seed -> measure -> value
    for arm, ss in R.items():
        for s, f in ss.items():
            r = split_tab.split(json.load(open(f, encoding="utf-8")), y0, y1, 301, 400)
            if r is None: continue
            o = r[0]; V.setdefault(arm, {})[s] = {**{f"gap {t}": o[t][0] - o[t][1] for t in TRAITS},
                                                  **{f"herd {t}": o[t][0] for t in TRAITS}, **{f"wild {t}": o[t][1] for t in TRAITS}}
    arms = sorted(V); pairs = []
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            sh = sorted(set(V[arms[i]]) & set(V[arms[j]]))
            if len(sh) >= 4: pairs.append((arms[i], arms[j], sh))
    meas = list(next(iter(next(iter(V.values())).values())))
    print(f"years {y0}-{y1}; {len(pairs)} arm pairs with >= 4 shared seeds; r across shared seeds, mean over pairs; null: "
          f"seeds shuffled within one arm per pair, {opt['--perm']} times" + ("; *** --bad shuffle: observed values shuffled ***" if opt["--bad"] else ""))
    print("| measure | mean r | null mean | null 95% | p | 1 - mean r |\n|---|---|---|---|---|---|")
    P = int(opt["--perm"])
    for mname in meas:
        def mean_r(shuffle):
            rs = []
            for a1, a2, sh in pairs:
                x = [V[a1][s][mname] for s in sh]; y = [V[a2][s][mname] for s in sh]
                if shuffle: y = y[:]; rng.shuffle(y)
                r = pearson(x, y)
                if r is not None: rs.append(r)
            return sum(rs) / len(rs) if rs else float("nan")
        obs = mean_r(opt["--bad"] == "shuffle")
        null = sorted(mean_r(True) for _ in range(P))
        p = sum(1 for v in null if v >= obs) / P
        print(f"| {mname} | {obs:+.3f} | {sum(null) / P:+.3f} | {null[int(0.025 * P)]:+.3f} to {null[int(0.975 * P) - 1]:+.3f} | {p:.3f} | {1 - obs:.2f} |")

if __name__ == "__main__": main()
