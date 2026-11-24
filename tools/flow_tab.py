# flow_tab.py: gene flow between herd and wild, and herd turnover, from the year rows (exploratory; analysis session,
# 2026-11-20, for the steward's question after exp007: why do LOADLO's and CTLRAND's herds track the wild while REF's and
# CTLDEEP's do not?).
#   python tools/flow_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--perseed] [--bad shift]
#   (a folder given as DIR=TAG names its arms ARM+TAG, so one arm from two folders can sit side by side, e.g.
#   "results/exp009_mutation-pull=9" gives REF9; tools/ref_match.py shows whether two such folders hold the same runs)
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
#                   hsw   = wild does' conceptions by a herd sire / all wild does' conceptions   (wildConc, from 8dd84a2)
#                   hout  = wild does' conceptions by a herd sire / herded: the herd-to-wild mating flow per herd goat
#   captive fate    bredF, bredM = first breedings by captives / captures, does and bucks (capBred / capIn, from
#                   8dd84a2): a ratio of events, not a cohort share (a captive taken before the window can breed in it;
#                   a recapture is a new entry)
#   (hsw, hout, bredF, bredM print "-" for runs without these keys, i.e. before exp009.)
#   turnover        birth = herdBirths / herded;  death = herd deaths of every cause / herded;  cull = culledHerd / herded
# Checks: herdMatGen (herd goats by maternal generations since capture) sums to herded in every row read; capIn sums to
# captured; concOrigin + wildConc sums to conceptions. The tool stops if any fails. --bad shift: herded taken from the next
# row; --bad capin: one doe added to capIn; each must fail.
# --pairs HI-LO[,HI-LO...]: paired differences HI - LO over the seeds both arms have (same seed = same history to year
# 400), mean (SE of the paired differences), for every measure.
# Not in the records: a captive's survival to its first breeding. Year rows count herd deaths, losses and conceptions,
# but not by whether the goat was captured itself, and no record follows individuals; it needs new output from the sim.
import glob, json, os, re, sys

def run_flow(d, y0, y1, bad=None):
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    if bad == "shift": rows = [dict(r, herded=rows[i + 1]["herded"]) for i, r in enumerate(rows[:-1])]
    if bad == "capin": rows = [dict(r, capIn=[r["capIn"][0] + 1, r["capIn"][1]]) if r.get("capIn") else r for r in rows]
    for r in rows:
        if r.get("herdMatGen") is not None and sum(r["herdMatGen"]) != r["herded"]:
            sys.exit(f"check failed: year {r['year'] + 1}: herdMatGen sums to {sum(r['herdMatGen'])}, herded {r['herded']}")
        # counters from 8dd84a2 on (absent in older runs): capIn counts captures by sex, so it sums to captured; every
        # conception is a herd dam's (concOrigin) or a wild dam's (wildConc), so the two sum to conceptions
        if r.get("capIn") is not None and sum(r["capIn"]) != r["captured"]:
            sys.exit(f"check failed: year {r['year'] + 1}: capIn sums to {sum(r['capIn'])}, captured {r['captured']}")
        if r.get("wildConc") is not None and sum(map(sum, r["concOrigin"])) + sum(r["wildConc"]) != r["conceptions"]:
            sys.exit(f"check failed: year {r['year'] + 1}: concOrigin + wildConc = {sum(map(sum, r['concOrigin'])) + sum(r['wildConc'])}, conceptions {r['conceptions']}")
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
    new = all(r.get("wildConc") is not None for r in rows)
    wc = [sum(r["wildConc"][k] for r in rows) for k in (0, 1)] if new else None
    ci = [sum(r["capIn"][k] for r in rows) for k in (0, 1)] if new else None
    cb = [sum(r["capBred"][k] for r in rows) for k in (0, 1)] if new else None
    return {"hsw": wc[1] / sum(wc) if new and sum(wc) else None, "hout": wc[1] / H if new else None,
            "bredF": cb[0] / ci[0] if new and ci[0] else None, "bredM": cb[1] / ci[1] if new and ci[1] else None,"herd": H / len(rows), "capt": S("captured") / H, "wsire": wsired / births if births else None,
            "cwild": (co[0][0] + co[1][0]) / conc if conc else None,
            "csire": (co[0][1] + co[1][1]) / conc if conc else None, "cdam": sum(co[0]) / conc if conc else None,
            "own0": sum(r["herdMatGen"][0] for r in rows if r.get("herdMatGen")) / H,
            "depth": sum(dep) / len(dep) if dep else None, "esc": S("escaped") / H,
            "feral": sum(fer) / len(fer) if fer else None, "anyh": sum(anyh) / len(anyh) if anyh else None,
            "birth": births / H, "death": deaths / H, "cull": S("culledHerd") / H}

KEYS = ["herd", "capt", "wsire", "cwild", "csire", "cdam", "own0", "depth", "esc", "feral", "anyh", "hsw", "hout",
        "bredF", "bredM", "birth", "death", "cull"]

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
        folder, _, tag = folder.partition("=")   # DIR=TAG: arms in DIR are named ARM+TAG (2026-11-24, exp009's REF as REF9)
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            arm = m.group(1) + tag if m else None
            if m and (not arms or arm in arms):
                if int(m.group(2)) in R.setdefault(arm, {}): sys.exit(f"duplicate {f}")
                R[arm][int(m.group(2))] = f
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
