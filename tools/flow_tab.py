# flow_tab.py: gene flow between herd and wild, and herd turnover, from the year rows (exploratory; analysis session,
# 2026-11-20, for the steward's question after exp007: why do LOADLO's and CTLRAND's herds track the wild while REF's and
# CTLDEEP's do not?).
#   python tools/flow_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--perseed] [--bad shift]
# Over the year rows in Y0-Y1 (1-based), per run; ratios are sums over rows (every 3rd year in thinned runs), so they are
# per herd goat per recorded year:
#   into the herd   capt  = captured / herded             wild goats taken into the herd
#                   wsire = wild-sired herd births / herd births   (wildSiredShare x herdBirths, summed)
#                   cwild = herd conceptions by a wild sire / herd conceptions                    (concOrigin col 0)
#                   csire = conceptions by a sire captured himself (gsc < 1) / herd conceptions   (concOrigin col 1)
#                   cdam  = conceptions by a dam captured herself / herd conceptions                (concOrigin row 0)
#                   own0  = herd goats captured themselves (herdMatGen bin 0) / herded
#                   depth = herdAncDepth (mean generations since wild of the herd genome), mean over rows
#   out of the herd esc   = escaped / herded             herd goats lost to the wild (run-offs not refetched, strays)
#                   feral = wildHerdShare, mean over rows: the wild genome's share from herd-born goats
#                   anyh  = wildAnyHerd, mean over rows: the share of wild goats with any herd-born ancestry
#                   (feral and anyh are stocks, not flows. The flow from herd to wild by herd bucks siring wild kids is
#                   not recorded, and histDepth, which splits the wild by herd-born share, is empty in lean runs:
#                   runyears.mjs sets logHistDepth 0.)
#   turnover        birth = herdBirths / herded;  death = herd deaths of every cause / herded;  cull = culledHerd / herded
# Check: herdMatGen (herd goats by maternal generations since capture) sums to herded in every row read; the tool stops if
# not. --bad shift: herded taken from the next row, which must fail that check.
# --pairs HI-LO[,HI-LO...]: paired differences HI - LO over the seeds both arms have (same seed = same history to year
# 400), mean (SE of the paired differences), for every measure.
# Not in the records: a captive's survival to its first breeding. Year rows count herd deaths, losses and conceptions,
# but not by whether the goat was captured itself, and no record follows individuals; it needs new output from the sim.
import glob, json, os, re, sys

def run_flow(d, y0, y1, bad=None):
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    if bad == "shift": rows = [dict(r, herded=rows[i + 1]["herded"]) for i, r in enumerate(rows[:-1])]
    for r in rows:
        if r.get("herdMatGen") is not None and sum(r["herdMatGen"]) != r["herded"]:
            sys.exit(f"check failed: year {r['year'] + 1}: herdMatGen sums to {sum(r['herdMatGen'])}, herded {r['herded']}")
    H = sum(r["herded"] for r in rows)
    if H == 0: return None
    S = lambda k: sum(r.get(k) or 0 for r in rows)
    births = S("herdBirths"); wsired = sum((r.get("wildSiredShare") or 0) * (r.get("herdBirths") or 0) for r in rows)
    co = [[sum(r["concOrigin"][i][j] for r in rows if r.get("concOrigin")) for j in range(4)] for i in range(2)]
    conc = sum(map(sum, co))
    deaths = sum(sum((r.get("herdDeaths") or {}).values()) for r in rows)
    dep = [r["herdAncDepth"] for r in rows if r.get("herdAncDepth") is not None]
    fer = [r["wildHerdShare"] for r in rows if r.get("wildHerdShare") is not None]
    anyh = [r["wildAnyHerd"] for r in rows if r.get("wildAnyHerd") is not None]
    return {"herd": H / len(rows), "capt": S("captured") / H, "wsire": wsired / births if births else None,
            "cwild": (co[0][0] + co[1][0]) / conc if conc else None,
            "csire": (co[0][1] + co[1][1]) / conc if conc else None, "cdam": sum(co[0]) / conc if conc else None,
            "own0": sum(r["herdMatGen"][0] for r in rows if r.get("herdMatGen")) / H,
            "depth": sum(dep) / len(dep) if dep else None, "esc": S("escaped") / H,
            "feral": sum(fer) / len(fer) if fer else None, "anyh": sum(anyh) / len(anyh) if anyh else None,
            "birth": births / H, "death": deaths / H, "cull": S("culledHerd") / H}

KEYS = ["herd", "capt", "wsire", "cwild", "csire", "cdam", "own0", "depth", "esc", "feral", "anyh", "birth", "death", "cull"]

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def main():
    a = sys.argv[1:]; bad = None; per = "--perseed" in a; pairs = []
    if per: a.remove("--perseed")
    if "--pairs" in a: i = a.index("--pairs"); pairs = [p.split("-") for p in a[i + 1].split(",")]; del a[i:i + 2]
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    y0, y1 = (int(v) for v in a[0].split("-")); arms = a[2].split(",") if len(a) > 2 else None
    R = {}
    for folder in a[1].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and (not arms or m.group(1) in arms):
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    print(f"years {y0}-{y1}; per herd goat per recorded year unless a share; seed means (SE). Exploratory.")
    print("| arm | seeds | " + " | ".join(KEYS) + " |\n|" + "---|" * (len(KEYS) + 2))
    lines, ALL = [], {}
    for arm in (arms or sorted(R)):
        if arm not in R: continue
        V = ALL.setdefault(arm, {})
        for s, f in sorted(R[arm].items()):
            v = run_flow(json.load(open(f, encoding="utf-8")), y0, y1, bad)
            if v: V[s] = v; lines.append(f"{arm} s{s}: " + "  ".join(f"{k} {v[k]:.3f}" if v[k] is not None else f"{k} -" for k in KEYS))
        cells = []
        for k in KEYS:
            m, se = ms([v[k] for v in V.values()])
            cells.append("-" if m is None else (f"{m:.1f}" if k == "herd" else f"{m:.3f} ({se:.3f})" if k != "depth" else f"{m:.2f} ({se:.2f})"))
        print(f"| {arm} | {len(V)} | " + " | ".join(cells) + " |")
    if pairs:
        print("\nPaired differences HI - LO over shared seeds, mean (SE of the paired differences):")
        print("| pair | seeds | " + " | ".join(KEYS) + " |\n|" + "---|" * (len(KEYS) + 2))
        for hi, lo in pairs:
            sh = sorted(set(ALL.get(hi, {})) & set(ALL.get(lo, {})))
            cells = []
            for k in KEYS:
                m, se = ms([ALL[hi][s][k] - ALL[lo][s][k] for s in sh if ALL[hi][s][k] is not None and ALL[lo][s][k] is not None])
                cells.append("-" if m is None else f"{m:+.3f} ({se:.3f})" if k not in ("herd", "depth") else f"{m:+.2f} ({se:.2f})")
            print(f"| {hi} - {lo} | {len(sh)} | " + " | ".join(cells) + " |")
    if per: print("\nPer run:\n" + "\n".join(lines))

if __name__ == "__main__": main()
