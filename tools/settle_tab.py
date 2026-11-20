# settle_tab.py: has each arm settled? The run-length rule of the 2026-11-11 pilot (EXPLOG c16de77), rebuilt 2026-11-19
# (the original lived in a scratchpad and was lost).
#   python tools/settle_tab.py DIR[;DIR...] [ENDS] [LONG0-LONG1]
# DIR holds <ARM>_seed<S>.json; several folders separated by ';' are pooled (2026-11-20). Gap of a trait = herd genotype mean - wild genotype mean, from the 20-bucket histograms
# (hist = all goats, histHerd = herd; wild = hist - histHerd) at bucket midpoints, per row, averaged over the rows in a window
# (hist_rows: thinned runs keep only some years). Per arm and seed: 200-year windows ending at each E (default 1600, 2000,
# 2400, 2800, 3200) against the long-run window (default 3201-4000); bias = seed mean of (window - long run), SE over
# seeds. An E is "ok" when every core trait (R A S B H T M W L) has abs(bias) <= 0.05. An arm's "settled at" is the
# first E from which every later E is ok. Herd = mean of year rows' "herded" in the long-run window.
# 2026-11-20 (analysis session's audit, tools/audit_scoring.py): a seed found in two folders now stops the tool (it was
# counted twice), and runs left out of a window for want of a herd row are listed at the end (none in exp005/exp006).
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runio import hist_rows

CORE = "R A S B H T M W L".split()
TRAITS = CORE + ["C"]

def gaps(d, y0, y1):                       # y0..y1 1-based, inclusive; returns {trait: gap} or None if no herd
    # gap per recorded row, then the mean over rows with a herd (a year-weighted mean, as the 11-11 tool; checked
    # 2026-11-19: reproduces its S0R6 and noMilk biases to the third decimal, where pooling counts did not)
    m = lambda c: sum((k + 0.5) / 20 * v for k, v in enumerate(c)) / sum(c)
    out = {}
    for t in TRAITS:
        v = []
        for i in hist_rows(d, y0 - 1, y1 - 1):
            a, h = d["hist"][t][i], d["histHerd"][t][i]; W = [x - y for x, y in zip(a, h)]
            if sum(h) and sum(W): v.append(m(h) - m(W))
        if not v: return None
        out[t] = sum(v) / len(v)
    return out

def herd(d, y0, y1):
    r = [x.get("herded") or 0 for x in d["years"] if y0 - 1 <= x["year"] <= y1 - 1]
    return sum(r) / len(r) if r else 0.0

def main():
    folders = sys.argv[1].split(";")
    ends = [int(e) for e in sys.argv[2].split(",")] if len(sys.argv) > 2 else [1600, 2000, 2400, 2800, 3200]
    l0, l1 = (int(v) for v in sys.argv[3].split("-")) if len(sys.argv) > 3 else (3201, 4000)
    arms, seen = {}, {}
    for f in sorted(f for folder in folders for f in glob.glob(os.path.join(folder, "*.json"))):
        m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
        if m:
            k = (m.group(1), int(m.group(2)))      # 2026-11-20 (audit): a seed found twice was counted twice
            if k in seen: sys.exit(f"{k[0]} seed {k[1]} found twice ({seen[k]}, {f})")
            seen[k] = f; arms.setdefault(m.group(1), []).append(f)
    dropped = []                                   # (arm, seed file, window) left out for want of a herd row
    print(f"long run {l0}-{l1}; 200-year windows ending at {ends}; ok = every core trait within 0.05 of the long run")
    print("\nLong run, seed means (n = core traits with abs(gap) >= 0.10):")
    print("| arm | seeds | herd | " + " | ".join(TRAITS) + " | n |\n|" + "---|" * (len(TRAITS) + 4))
    bias_rows = []
    for arm, files in arms.items():
        L, B, hs = [], {e: [] for e in ends}, []
        for f in files:
            d = json.load(open(f, encoding="utf-8"))
            g = gaps(d, l0, l1)
            if g is None: dropped.append((arm, os.path.basename(f), f"{l0}-{l1}")); continue
            L.append(g); hs.append(herd(d, l0, l1))
            for e in ends:
                w = gaps(d, e - 199, e)
                if w is not None: B[e].append({t: w[t] - g[t] for t in TRAITS})
                else: dropped.append((arm, os.path.basename(f), f"{e - 199}-{e}"))
        if not L:
            print(f"| {arm} | {len(files)} | no herd in the long run |"); continue
        mean = {t: sum(x[t] for x in L) / len(L) for t in TRAITS}
        n = sum(1 for t in CORE if abs(mean[t]) >= 0.10)
        print(f"| {arm} | {len(L)}/{len(files)} | {sum(hs) / len(hs):.1f} | " + " | ".join(f"{mean[t]:+.3f}" for t in TRAITS) + f" | {n} |")
        cells, oks = [], []
        for e in ends:
            xs = B[e]
            if len(xs) < 2: cells.append("n/a"); oks.append(False); continue
            mb = {t: sum(x[t] for x in xs) / len(xs) for t in CORE}
            se = {t: (sum((x[t] - mb[t]) ** 2 for x in xs) / (len(xs) - 1) / len(xs)) ** 0.5 for t in CORE}
            worst = max(CORE, key=lambda t: abs(mb[t]))
            ok = abs(mb[worst]) <= 0.05; oks.append(ok)
            cells.append(f"{abs(mb[worst]):.3f} {'ok' if ok else '[' + worst + ']'} (R {mb['R']:+.3f}, B {mb['B']:+.3f} +- {se['B']:.3f})")
        settled = next((ends[i] for i in range(len(ends)) if all(oks[i:])), None)
        bias_rows.append((arm, cells, settled if settled else "not settled"))
    print("\nBias (window ending E minus long run), largest abs over core traits [trait]; R and B bias, B +- SE:")
    print("| arm | " + " | ".join(str(e) for e in ends) + " | settled at |\n|" + "---|" * (len(ends) + 2))
    for arm, cells, s in bias_rows: print(f"| {arm} | " + " | ".join(cells) + f" | {s} |")
    if dropped: print("\nLeft out for want of a herd row (arm, run, window): " + "; ".join(" ".join(x) for x in dropped))

main()
