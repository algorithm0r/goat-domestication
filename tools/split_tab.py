# split_tab.py: each trait's gap split into herd change and wild change, both against the founders' mean (exploratory;
# the design review's finding 2(a), notes/review/2026-11-20-design.md; named in the exp007 pre-registration). Analysis
# session, 2026-11-20.
#   python tools/split_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--founders F0-F1] [--min-herd N] [--perseed] [--show-founders] [--bad allgoats]
# Founders' mean F of a trait = the mean over the histogram rows in F0-F1 (default 301-400, 1-based: the last century
# before herding starts in year 400, when every goat is wild; the tool stops if any of those rows has a herd goat) of
# the all-goat genotype mean (20-bucket histogram, midpoints). Over Y0-Y1, per histogram row with herd and wild goats
# (the rows settle_tab.gaps uses): herd change = herd mean - F, wild change = wild mean - F (wild = hist - histHerd);
# each averaged over those rows. So gap = herd change - wild change, row by row and on average; the tool checks this
# identity against settle_tab.gaps for every run (1e-9) and stops if it fails.
# Per arm: seed means (SE over seeds) of herd change, wild change and gap; herd = mean of year rows' herded in Y0-Y1.
# --min-herd N keeps only runs whose herd over Y0-Y1 is N or more (exp007's "established", N = 100), and lists the
# runs left out. --perseed prints each run's herd beside its herd change, wild change and gap.
# --bad allgoats: herd means taken from hist instead of histHerd, which must break the identity check.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, "settle_tab.py"), encoding="utf-8").read().replace("\nmain()\n", "\n")
_ns = {"__file__": os.path.join(HERE, "settle_tab.py")}; exec(_src, _ns)
gaps, herd, CORE, TRAITS = _ns["gaps"], _ns["herd"], _ns["CORE"], _ns["TRAITS"]

def mc(c):
    n = sum(c); return None if n == 0 else sum((k + 0.5) / 20 * v for k, v in enumerate(c)) / n

def split(d, y0, y1, f0, f1, bad=None):
    # the founders are the century before herding: the window must end at the run's own herdingAt (the reviewer's exp013
    # prereg review, point 3: a late run read with the default 301-400 would take founders from before humans arrived)
    h = (d.get("_parameters") or {}).get("herdingAt")
    if h is not None and h < 1e8 and f1 != h: sys.exit(f"founders' window {f0}-{f1} does not end at the run's herdingAt {h}")
    fr = [i for i, y in enumerate(d["histYears"]) if f0 <= y + 1 <= f1]
    if not fr: sys.exit(f"no histogram row in the founders' window {f0}-{f1}")
    if any(sum(d["histHerd"]["R"][i]) for i in fr): sys.exit(f"herd goats in the founders' window {f0}-{f1}")
    F = {t: sum(mc(d["hist"][t][i]) for i in fr) / len(fr) for t in TRAITS}
    # founders' SD among goats of the genotypic value (mean of a goat's alleles for the trait), from the histograms at
    # midpoints, root of the mean within-row variance. NOT the spread of alleles: no record holds alleles.
    def sd(c):
        n = sum(c); m = mc(c); return sum(((k + 0.5) / 20 - m) ** 2 * v for k, v in enumerate(c)) / n
    Fsd = {t: (sum(sd(d["hist"][t][i]) for i in fr) / len(fr)) ** 0.5 for t in TRAITS}
    hc, wc = {t: [] for t in TRAITS}, {t: [] for t in TRAITS}
    for i, y in enumerate(d["histYears"]):
        if not y0 <= y + 1 <= y1: continue
        for t in TRAITS:
            a, h = d["hist"][t][i], d["histHerd"][t][i]; w = [x - z for x, z in zip(a, h)]
            if sum(h) and sum(w):
                hc[t].append(mc(a if bad == "allgoats" else h) - F[t]); wc[t].append(mc(w) - F[t])
    if not hc["R"]: return None
    out = {t: (sum(hc[t]) / len(hc[t]), sum(wc[t]) / len(wc[t])) for t in TRAITS}
    g = gaps(d, y0, y1)
    if any(abs(out[t][0] - out[t][1] - g[t]) > 1e-9 for t in TRAITS):
        sys.exit("identity check failed: herd change - wild change != settle_tab gap (" +
                 ", ".join(f"{t} {out[t][0] - out[t][1]:+.4f} vs {g[t]:+.4f}" for t in TRAITS if abs(out[t][0] - out[t][1] - g[t]) > 1e-9) + ")")
    return out, F, Fsd

def ms(xs):
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def main():
    a = sys.argv[1:]; opt = {"--founders": "301-400", "--min-herd": None, "--bad": None}; flags = {"--perseed": False}
    for k in list(opt):
        if k in a: i = a.index(k); opt[k] = a[i + 1]; del a[i:i + 2]
    flags["--show-founders"] = False
    for k in flags:
        if k in a: flags[k] = True; a.remove(k)
    y0, y1 = (int(v) for v in a[0].split("-")); f0, f1 = (int(v) for v in opt["--founders"].split("-"))
    arms = a[2].split(",") if len(a) > 2 else None; minh = float(opt["--min-herd"]) if opt["--min-herd"] else None
    R = {}
    for folder in a[1].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and (not arms or m.group(1) in arms):
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    print(f"years {y0}-{y1}; founders' mean over {f0}-{f1} (all goats wild); herd change = herd mean - founders, wild change = "
          f"wild mean - founders, gap = herd change - wild change; seed means (SE)" + (f"; runs with herd >= {minh:g} only" if minh else ""))
    print("| arm | seeds | herd | part | " + " | ".join(TRAITS) + " |\n|" + "---|" * (len(TRAITS) + 4))
    left, per, FS, HC, FSD = [], [], {}, {}, {}
    for arm in sorted(R):
        V = []
        for s, f in sorted(R[arm].items()):
            d = json.load(open(f, encoding="utf-8")); r = split(d, y0, y1, f0, f1, opt["--bad"]); h = herd(d, y0, y1)
            if r is None or (minh is not None and h < minh): left.append(f"{arm}_s{s} (herd {h:.0f})"); continue
            V.append((s, h, r[0])); FS.setdefault(arm, []).append(r[1]); FSD.setdefault(arm, []).append(r[2])
            per.append(f"{arm} s{s} herd {h:.0f}: " + "  ".join(f"{t} {r[0][t][0]:+.3f}/{r[0][t][1]:+.3f}/{r[0][t][0] - r[0][t][1]:+.3f}" for t in TRAITS))
        if not V: print(f"| {arm} | 0 | - | none kept |"); continue
        hm = sum(h for _, h, _ in V) / len(V)
        HC[arm] = {t: ms([o[t][0] for _, _, o in V])[0] for t in TRAITS}
        for lab, fn in (("herd", lambda x: x[0]), ("wild", lambda x: x[1]), ("gap", lambda x: x[0] - x[1])):
            cells = [ms([fn(o[t]) for _, _, o in V]) for t in TRAITS]
            print(f"| {arm if lab == 'herd' else ''} | {len(V) if lab == 'herd' else ''} | {f'{hm:.1f}' if lab == 'herd' else ''} | {lab} | "
                  + " | ".join(f"{m:+.3f} ({se:.3f})" for m, se in cells) + " |")
    if left: print("\nLeft out (no herd row in the window" + (f", or herd under {minh:g}" if minh else "") + "): " + ", ".join(left))
    if flags["--perseed"]: print("\nPer run, each trait herd change / wild change / gap:\n" + "\n".join(per))
    if flags["--show-founders"]:
        # 2026-11-20, for the reviewer's clamp hypothesis (alleles move +-mutationStep and are clamped to [0,1],
        # src/genome.js:69-73): the founders' mean F per trait, seed mean (SE), and whether the herd change points toward
        # 0.5 (sign of herd change = sign of 0.5 - F). Exploratory.
        print("\nFounders' mean F (seed mean (SE)); 'to 0.5' marks traits whose seed-mean herd change has the sign of 0.5 - F:")
        print("| arm | " + " | ".join(TRAITS) + " |\n|" + "---|" * (len(TRAITS) + 1))
        for arm, Fs in FS.items():
            cells = []
            for t in TRAITS:
                m, se = ms([F[t] for F in Fs]); hc = HC[arm][t]
                cells.append(f"{m:.3f} ({se:.3f}){' to 0.5' if hc * (0.5 - m) > 0 else ''}")
            print(f"| {arm} | " + " | ".join(cells) + " |")
        print("\nFounders' SD of the genotypic value among goats (seed mean), and herd change as a fraction of (0.5 - F)"
              " (seed-mean herd change / (0.5 - seed-mean F)). The SD is of goats' allele means, not of alleles:")
        print("| arm | " + " | ".join(TRAITS) + " |\n|" + "---|" * (len(TRAITS) + 1))
        for arm, Fs in FS.items():
            cells = []
            for t in TRAITS:
                m = ms([F[t] for F in Fs])[0]; sdm = ms([x[t] for x in FSD[arm]])[0]; dist = 0.5 - m
                cells.append(f"SD {sdm:.3f}, " + (f"{HC[arm][t] / dist:+.2f}" if abs(dist) >= 0.05 else "n/a (F within 0.05 of 0.5)"))
            print(f"| {arm} | " + " | ".join(cells) + " |")

if __name__ == "__main__": main()
