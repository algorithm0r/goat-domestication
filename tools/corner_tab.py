# corner_tab.py: the two-corner sweep (exp006, with exp005 for REF's leave-one-out seeds 1-4), 2026-11-19.
#   python tools/corner_tab.py Y0-Y1 DIR [DIR ...]
# Pools <ARM>_seed<S>.json over the folders (a seed found twice is an error). Per arm, over window Y0-Y1 (1-based):
# herd (mean of year rows' herded), gap per trait (herd - wild genotype mean, per histogram row, averaged: settle_tab's
# gaps), breadth n (core traits with abs(seed-mean gap) >= 0.10), and "est" = seeds whose R gap is -0.30 or below.
# Effects of each behaviour: add = (NONE + it) - NONE; drop = REF - (REF without it); exchange's drop effect is
# REF - (REF + exchange) with the sign turned so both read "having it": (REF + exchange) - REF. Seed means, with the SE
# of the difference. "interacts" lists core traits where add and drop differ by more than 0.10.
# A run with no herd row in the window is scored as gap 0 (herd counted as it is); from 2026-11-20 such runs are listed
# at the end (none in exp005/exp006 at 1401-1600 or 3201-4000; audited with tools/audit_scoring.py).
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "settle_tab.py"), encoding="utf-8").read().replace("\nmain()\n", "\n")
_ns = {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "settle_tab.py")}; exec(_src, _ns)
gaps, herd, CORE, TRAITS = _ns["gaps"], _ns["herd"], _ns["CORE"], _ns["TRAITS"]

FACTORS = [("cull", "addCull", "RAND"), ("pen", "addPen", "noPen"), ("guard", "addGuard", "noGuard"),
           ("prov", "addProv", "noProv"), ("shelter", "addShelter", "noShelter"), ("buck", "addBuck", "noBuck"),
           ("tether", "addTether", "noTether"), ("milk", "addMilk", "noMilk"), ("exch", "addExch", None)]

def stats(xs):
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5 if n > 1 else 0.0)

def main():
    y0, y1 = (int(v) for v in sys.argv[1].split("-"))
    runs = {}
    for folder in sys.argv[2:]:
        for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if not m: continue
            a, s = m.group(1), int(m.group(2))
            if s in runs.setdefault(a, {}): sys.exit(f"{a} seed {s} found twice ({f})")
            runs[a][s] = f
    V = {}                                           # arm -> seed -> {herd, gaps...}
    for a, ss in runs.items():
        for s, f in ss.items():
            d = json.load(open(f, encoding="utf-8")); g = gaps(d, y0, y1)
            V.setdefault(a, {})[s] = dict(g or {t: 0.0 for t in TRAITS}, herd=herd(d, y0, y1), nohist=g is None)
    print(f"years {y0}-{y1}; seed means; est = seeds with R gap <= -0.30; n = core traits with abs(gap) >= 0.10")
    print("| arm | seeds | est | herd | " + " | ".join(TRAITS) + " | n |\n|" + "---|" * (len(TRAITS) + 5))
    order = ["NONE"] + [f[1] for f in FACTORS] + ["REF", "addExchREF"] + [f[2] for f in FACTORS if f[2]]
    for a in order + sorted(set(V) - set(order)):
        if a not in V: continue
        ss = V[a]; mean = {k: stats([v[k] for v in ss.values()])[0] for k in TRAITS + ["herd"]}
        est = sum(1 for v in ss.values() if v["R"] <= -0.30)
        n = sum(1 for t in CORE if abs(mean[t]) >= 0.10)
        print(f"| {a} | {len(ss)} | {est} | {mean['herd']:.1f} | " + " | ".join(f"{mean[t]:+.3f}" for t in TRAITS) + f" | {n} |")
    def eff(hi, lo, k):
        if hi not in V or lo not in V: return None
        a, sa = stats([v[k] for v in V[hi].values()]); b, sb = stats([v[k] for v in V[lo].values()])
        return a - b, (sa ** 2 / len(V[hi]) + sb ** 2 / len(V[lo])) ** 0.5
    print("\nEffects of having each behaviour (add = from NONE, drop = from REF), seed-mean difference (SE):")
    print("| behaviour | from | herd | " + " | ".join(CORE) + " | interacts |\n|" + "---|" * (len(CORE) + 4))
    for name, add, drop in FACTORS:
        pairs = [("add", add, "NONE"), ("drop", "REF", drop) if drop else ("drop", "addExchREF", "REF")]
        E = {}
        for lab, hi, lo in pairs:
            row = {k: eff(hi, lo, k) for k in ["herd"] + CORE}
            E[lab] = row
            if row["R"] is None: print(f"| {name} | {lab} | missing |"); continue
            cells = [f"{row['herd'][0]:+.1f}"] + [f"{row[t][0]:+.2f} ({row[t][1]:.2f})" for t in CORE]
            inter = ""
            if lab == "drop" and E["add"]["R"] is not None:
                inter = " ".join(t for t in CORE if abs(E["add"][t][0] - row[t][0]) > 0.10)
            print(f"| {name} | {lab} | " + " | ".join(cells) + f" | {inter} |")
    nh = [f"{a}_seed{s}" for a in V for s in sorted(V[a]) if V[a][s]["nohist"]]   # 2026-11-20 (audit): was silent
    if nh: print("\nNo herd row in the window, scored as gap 0: " + ", ".join(nh))

main()
