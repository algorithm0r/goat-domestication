# admix_tab.py: the herd against the wild goats with little or no herd ancestry (exploratory; review finding 10's third
# number; analysis session, 2026-11-20). Needs runs with logHistDepth 1 (exp009 on); lean runs before that have an empty
# histDepth.
#   python tools/admix_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--perseed] [--bad swap]
# histDepth.wild[trait][record][bin][bucket]: wild goats' genotype histograms by the share of their genome from herd-born
# goats, bins with upper edges wildShareBins = [0, 1/16, 1/8, 1/4, 1/2, 1] (bin 0 = no herd-born ancestry). Each record
# pools every year of its `every` years (15 at k = 3), ending at histDepth.years[record] (0-based).
# Per run, over the records whose last year lies in Y0-Y1 (1-based):
#   share of wild goat-years in each bin (pooled counts);
#   per trait, the mean of wild goats with share <= 0, <= 1/16, <= 1/8, <= 1/4 (cumulative bins), pooled over the window;
#   herd mean = histHerd over the window's histogram rows (as split_tab and settle_tab); gap vs each low-admixture wild
#   = herd mean - that wild mean; and the registered gap (settle_tab.gaps, herd - all wild) beside it.
# Per arm: seed means (SE). A cumulative bin holding under 1% of wild goat-years in a run is reported "-" for that run.
# Check (approximate: histDepth pools 15 years, the histograms are year-end snapshots): all wild goats in histDepth (bins
# summed), pooled over the window, have a mean within 0.02 of the all-wild mean from hist - histHerd over the same window,
# on every trait; the tool stops if not. --bad swap: histDepth's herd and wild sides swapped, which must fail it.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab
gaps, herd, TRAITS = split_tab.gaps, split_tab.herd, split_tab.TRAITS
CUM = [(0, "<=0"), (1, "<=1/16"), (2, "<=1/8"), (3, "<=1/4")]

def mc(c):
    n = sum(c); return None if n == 0 else sum((k + 0.5) / 20 * v for k, v in enumerate(c)) / n

def run_admix(d, y0, y1, bad=None):
    hd = d.get("histDepth") or {}
    if not hd.get("years"): sys.exit("histDepth is empty in this run (logHistDepth 0); admix_tab needs logHistDepth 1")
    W = hd["herd"] if bad == "swap" else hd["wild"]
    recs = [i for i, y in enumerate(hd["years"]) if y0 <= y + 1 <= y1]
    if not recs: return None
    nb = len(hd["wildShareBins"])
    pooled = {t: [[sum(W[t][i][b][k] for i in recs) for k in range(20)] for b in range(nb)] for t in TRAITS}
    tot = [sum(pooled["R"][b]) for b in range(nb)]; N = sum(tot)
    if N == 0: return None
    # check against the year-end histograms
    rows = [i for i, y in enumerate(d["histYears"]) if y0 <= y + 1 <= y1]
    for t in TRAITS:
        allw = mc([sum(pooled[t][b][k] for b in range(nb)) for k in range(20)])
        ws = [mc([a - h for a, h in zip(d["hist"][t][i], d["histHerd"][t][i])]) for i in rows]
        ws = [w for w in ws if w is not None]
        if ws and abs(allw - sum(ws) / len(ws)) > 0.02:
            sys.exit(f"check failed: {t}: histDepth wild mean {allw:.4f} vs hist - histHerd {sum(ws) / len(ws):.4f}")
    hm = {}
    for t in TRAITS:
        hs = [mc(d["histHerd"][t][i]) for i in rows]; hs = [x for x in hs if x is not None]
        hm[t] = sum(hs) / len(hs) if hs else None
    out = {"share": [x / N for x in tot], "gap": gaps(d, y0, y1)}
    for b, lab in CUM:
        n = sum(tot[:b + 1])
        out[lab] = None if n < 0.01 * N or hm["R"] is None else \
            {t: hm[t] - mc([sum(pooled[t][bb][k] for bb in range(b + 1)) for k in range(20)]) for t in TRAITS}
    return out

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def main():
    a = sys.argv[1:]; bad = None; per = "--perseed" in a
    if per: a.remove("--perseed")
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    y0, y1 = (int(v) for v in a[0].split("-")); arms = a[2].split(",") if len(a) > 2 else None
    R = {}
    for folder in a[1].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and (not arms or m.group(1) in arms):
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    print(f"years {y0}-{y1}; wild goats by herd-born genome share (histDepth); gap = herd mean - wild mean; seed means (SE). Exploratory.")
    V, lines = {}, []
    for arm in (arms or sorted(R)):
        for s, f in sorted(R.get(arm, {}).items()):
            o = run_admix(json.load(open(f, encoding="utf-8")), y0, y1, bad)
            if o: V.setdefault(arm, {})[s] = o; lines.append(f"{arm} s{s}: share by bin " + " ".join(f"{x:.3f}" for x in o["share"]))
    print("\nShare of wild goat-years by herd-born share bin (0, <=1/16, <=1/8, <=1/4, <=1/2, <=1):")
    for arm, ss in V.items():
        nb = len(next(iter(ss.values()))["share"])
        print(f"  {arm}: " + " ".join(f"{ms([v['share'][b] for v in ss.values()])[0]:.3f}" for b in range(nb)))
    print("\n| arm | wild compared | seeds | " + " | ".join(TRAITS) + " |\n|" + "---|" * (len(TRAITS) + 3))
    for arm, ss in V.items():
        for lab in ["all wild (registered gap)"] + [l for _, l in CUM]:
            key = "gap" if lab.startswith("all") else lab
            got = [v[key] for v in ss.values() if v[key] is not None]
            if not got: print(f"| {arm} | {lab} | 0 | " + " | ".join("-" for _ in TRAITS) + " |"); continue
            print(f"| {arm} | {lab} | {len(got)} | " + " | ".join("{:+.3f} ({:.3f})".format(*ms([g[t] for g in got])) for t in TRAITS) + " |")
    if per: print("\nPer run:\n" + "\n".join(lines))

if __name__ == "__main__": main()
