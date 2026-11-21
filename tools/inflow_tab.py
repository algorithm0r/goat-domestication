# inflow_tab.py: inflow m and the mutational pull r behind exp011 amendment 3's divergence null, and that null's
# check on the neutral marker C (exploratory; analysis session, 2026-11-20, for the steward's amendment 3 and the
# reviewer's exp009 results review, notes/review/2026-11-20-exp009-results.md, requests (a)-(c)).
#   python tools/inflow_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--pull 0.843] [--bad depth]
#   python tools/inflow_tab.py selftest
# Per run over Y0-Y1 (1-based), seed means (SE) per arm:
#   depth     herdAncDepth, mean over rows. Capped: WV_DEPTH 24 slots (animals.js:24), the last open-ended, captives at 0
#   m_depth   inflow per generation that gives that mean depth if depths are geometric at steady state: share m(1-m)^d
#             at depth d < 23 and (1-m)^23 at 23; inverted by bisection (the reviewer's request (b)). The inversion is
#             checked to reproduce the depth to 1e-6; --bad depth adds 30 to every depth, beyond the cap, and must stop.
#   m_conc    inflow per herd cohort from the conception records: (captive-sire + captive-dam + wild-sire shares of
#             herd conceptions) / 2 (flow_tab csire, cdam, cwild); amendment 3 names the first two; cwild is added
#             because a wild sire's half is wild genome too (it is 0.000 in the CTL arms and REF)
#   own0      share of herd goats that were captured themselves (wild genomes in the herd directly; flow_tab own0)
#   fk        generation proxy: median age at first kidding, years (culture_tab.firstkid, herd and wild pooled, rows
#             401 to Y1). Mean parent age at birth is not in these records (parentAge from 0850eb3 on): request (a)
#             can be met only by this proxy, which is a lower bound on generation time
#   r         the pull per year from C: 1 - (1 - pull)^(1 / elapsed), elapsed = window midpoint - founders' midpoint
#             (founders 301-400); and per generation at T = fk: 1 - (1 - pull)^(fk / elapsed). Treats the clamped walk's
#             relaxation as exponential, which it is not exactly
#   share     r / (m + r), the amendment's balance factor, with m_depth (per generation, r per generation at fk)
#   C         the neutral marker's herd - wild gap: mean (SE), seeds below / above 0; the amendment's null for it
#             without the circular C term, share x (0.5 - wild C); and the two-population model's value, 0 (below)
# Why the C check has no power, stated here so the tables are read with it: a neutral trait is pulled in the wild too.
# With herd mean h and wild mean w, dh/dt = r(0.5 - h) + m(w - h) and dw/dt = r(0.5 - w) give d(h - w)/dt = -(r + m)(h - w):
# a herd founded at the wild mean keeps h - w = 0 whatever m and r. The r/(m + r) factor holds only for a trait the wild
# holds fixed by selection, which C is not; so C can test "nothing else reaches a neutral trait", not the balance factor.
# Also: selDam (dams' allele mean minus the herd does', world.js:1477-1495) on R A H B T, kids-weighted (request (c)).
import glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, flow_tab, culture_tab
CAP = 23
SELT = ["R", "A", "H", "B", "T", "C"]

def capped_mean(m):
    return sum(d * m * (1 - m) ** d for d in range(CAP)) + CAP * (1 - m) ** CAP

def m_from_depth(depth):
    if depth is None: return None
    if not 0 <= depth < CAP: sys.exit(f"check failed: depth {depth} outside [0, {CAP}) cannot be inverted")
    lo, hi = 1e-9, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if capped_mean(mid) > depth: lo = mid
        else: hi = mid
    m = (lo + hi) / 2
    if abs(capped_mean(m) - depth) > 1e-6: sys.exit(f"check failed: inversion of depth {depth} gives {capped_mean(m)}")
    return m

BINS = [(0, 0), (1, 1), (2, 4), (5, 9), (10, 19), (20, None)]   # datamanager.js GEN_BINS, as herdWildAnc records them

def geo_bins(m):
    """herdWildAnc's bins if depths were geometric at m (share m(1-m)^d at depth d; 20+ = (1-m)^20)."""
    return [sum(m * (1 - m) ** d for d in range(lo, hi + 1)) if hi is not None else (1 - m) ** lo for lo, hi in BINS]

def shape(obs, m):
    """Observed bins against geometric at m: per-bin ratios and the verdict. 'not geometric' if any bin holding >= 0.005
    of the genome is off by a factor of 2 or more either way (my threshold, fixed before any exp011 result)."""
    g = geo_bins(m); rat = [o / x if x > 0 else None for o, x in zip(obs, g)]
    off = any(r is not None and o >= 0.005 and (r >= 2 or r <= 0.5) for o, r in zip(obs, rat))
    return rat, ("not geometric" if off else "geometric")

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
        12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 30: 2.042}

def tcrit(n):   # two-sided 95% t for n values (n - 1 degrees of freedom)
    df = n - 1
    return T975.get(df) or T975[max(k for k in T975 if k <= df)]

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def run(f, y0, y1, pull, bad=None):
    d = json.load(open(f, encoding="utf-8"))
    fl = flow_tab.run_flow(d, y0, y1)
    if not fl: return None
    sp = split_tab.split(d, y0, y1, 301, 400)
    yd = (d.get("_parameters") or {}).get("yearDays") or 360
    depth = fl["depth"] + (30 if bad == "depth" else 0) if fl["depth"] is not None else None
    md = m_from_depth(depth)
    mc = sum(fl[k] or 0 for k in ("csire", "cdam", "cwild")) / 2
    fk = culture_tab.firstkid(d, y1); fk = fk / yd if fk else None
    elapsed = (y0 + y1) / 2 - 350.5
    ry = 1 - (1 - pull) ** (1 / elapsed); rg = 1 - (1 - pull) ** (fk / elapsed) if fk else None
    share = rg / (md + rg) if rg and md is not None else None
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    def sel(t, key, k):
        num = den = 0
        for r in rows:
            if r.get(key) and r.get("selN") and r["selN"][k]: num += r[key][t] * r["selN"][k]; den += r["selN"][k]
        return num / den if den else None
    anc = [r["herdWildAnc"] for r in rows if r.get("herdWildAnc")]
    bins = [sum(a[k] for a in anc) / len(anc) for k in range(len(BINS))] if anc else None
    if bad == "geo" and md is not None: bins = geo_bins(md)                   # planted: a truly geometric herd
    def fkk(k, lo):
        v = [r[k] for r in d["years"] if lo <= r["year"] + 1 <= y1 and r.get(k) is not None]
        return sum(v) / len(v) / yd if v else None
    out = {"depth": depth, "m_depth": md, "m_conc": mc, "own0": fl["own0"], "fk": fk, "r_year": ry, "r_gen": rg,
           "share": share, "selDam": {t: sel(t, "selDam", 0) for t in SELT}, "bins": bins,
           # persistent inflow: the genome share per generation of depth at depths 10-19. Equals m if depths are
           # geometric and nothing is lost after depth 10; it is the flow reaching the deep herd, not the flow arriving
           "m_deep": bins[4] / 10 if bins else None,
           "fkH": (fkk("medianFirstKidAgeHerd", y0), fkk("medianFirstKidAgeHerd", 401)),
           "fkW": (fkk("medianFirstKidAgeWild", y0), fkk("medianFirstKidAgeWild", 401))}
    if sp:
        hcC, wcC = sp[0]["C"]; FC = sp[1]["C"]
        out["Cgap"] = hcC - wcC; wild = FC + wcC
        out["Cnull"] = share * (0.5 - wild) if share is not None else None
        out["Cwild"] = wild
        # two pools (the reviewer's ed0c0a5 request 2): s = herd genome share at depths 0-4 (bins 0, 1, 2-4), taken as
        # near-wild; the core (the rest) relaxes C by f_core, solved from the herd's own C fraction:
        # f_herd = (1 - s) f_core + s f_wild, f = change / (0.5 - F). Pull-alone herd change for trait t:
        # (1 - s) x f_core x (0.5 - F_t) + s x wild change_t.
        if bins and abs(0.5 - FC) > 0.05:
            s = sum(bins[:3]); fh, fw = hcC / (0.5 - FC), wcC / (0.5 - FC)
            fcore = (fh - s * fw) / (1 - s)
            sp_ = s + (0.05 if bad == "pool" else 0)          # planted: the prediction uses a wrong s
            pred = {t: (1 - sp_) * fcore * (0.5 - sp[1][t]) + sp_ * sp[0][t][1] for t in SELT}
            # consistency of the code, not a test of the model: f_core is solved from C, so the prediction for C equals
            # C's observed herd change for any s by algebra (the reviewer's 7377feb); a wrong s in the prediction breaks it
            if abs(pred["C"] - hcC) > 1e-9: sys.exit(f"check failed (code consistency): two-pool prediction for C {pred['C']:+.4f} != observed {hcC:+.4f}")
            out["pool"] = {"s": s, "fh": fh, "fw": fw, "fcore": fcore, "pred": pred, "obs": {t: sp[0][t][0] for t in SELT}}
    return out

def main(a):
    pull = 0.843; bad = None
    if "--pull" in a: i = a.index("--pull"); pull = float(a[i + 1]); del a[i:i + 2]
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    y0, y1 = (int(v) for v in a[0].split("-")); arms = a[2].split(",") if len(a) > 2 else None
    F = {}
    for folder in a[1].split(";"):
        for fn in glob.glob(os.path.join(folder, "*.json")):
            mt = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(fn))
            if mt and (arms is None or mt.group(1) in arms):
                if int(mt.group(2)) in F.setdefault(mt.group(1), {}): sys.exit(f"duplicate {fn}")
                F[mt.group(1)][int(mt.group(2))] = fn
    order = [x for x in (arms or sorted(F)) if x in F]
    R = {arm: [x for x in (run(fn, y0, y1, pull, bad) for _, fn in sorted(F[arm].items())) if x] for arm in order}
    print(f"years {y0}-{y1}; pull {pull} (C fraction, exp009 pooled); elapsed = window midpoint - 350.5; seed means (SE). Exploratory.")
    f = lambda p, n=4: "-" if p[0] is None else f"{p[0]:.{n}f} ({p[1]:.{n}f})"
    print("| arm | runs | depth | m_depth /gen | m_conc /cohort | own0 | fk (y) | r /year | r /gen at fk | r/(m_depth+r) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for arm in order:
        rs = R[arm]; g = lambda k: ms([r[k] for r in rs])
        print(f"| {arm} | {len(rs)} | {f(g('depth'), 2)} | {f(g('m_depth'))} | {f(g('m_conc'))} | {f(g('own0'), 3)} | "
              f"{f(g('fk'), 2)} | {f(g('r_year'), 5)} | {f(g('r_gen'), 5)} | {f(g('share'), 3)} |")
    print("\nNeutral C, herd - wild gap: observed mean (SE), seeds below 0 / above 0; the amendment's null without the circular"
          " C term, r/(m_depth+r) x (0.5 - wild C); the two-population model for a neutral trait gives 0 whatever m and r")
    print("| arm | runs | wild C | C gap observed | below / above 0 | null r/(m+r) x (0.5 - wild C) | null within 2 SE of observed | 0 within 2 SE of observed |")
    print("|---|---|---|---|---|---|---|---|")
    for arm in order:
        rs = [r for r in R[arm] if "Cgap" in r]
        if not rs: continue
        o = ms([r["Cgap"] for r in rs]); nl = ms([r["Cnull"] for r in rs])
        within = "-" if nl[0] is None or o[1] is None else ("yes" if abs(o[0] - nl[0]) <= 2 * o[1] else "no")
        print(f"| {arm} | {len(rs)} | {ms([r['Cwild'] for r in rs])[0]:.3f} | {o[0]:+.4f} ({o[1]:.4f}) | "
              f"{sum(1 for r in rs if r['Cgap'] < 0)} / {sum(1 for r in rs if r['Cgap'] > 0)} | "
              f"{'-' if nl[0] is None else f'{nl[0]:+.4f}'} | {within} | {'yes' if abs(o[0]) <= 2 * o[1] else 'no'} |")
    print("\nHerd wild ancestry by generations since wild (herdWildAnc, mean over the window's rows; bins 0, 1, 2-4, 5-9,"
          " 10-19, 20+), against geometric depths at m_depth (ratio observed / geometric); m_deep = bin 10-19 / 10")
    print("| arm | observed bins | geometric at m_depth | ratios | shape | m_deep /gen |\n|---|---|---|---|---|---|")
    SHAPE = {}
    for arm in order:
        rs = [r for r in R[arm] if r["bins"] and r["m_depth"] is not None]
        if not rs: continue
        ob = [sum(r["bins"][k] for r in rs) / len(rs) for k in range(len(BINS))]
        md = ms([r["m_depth"] for r in rs])[0]; rat, verdict = shape(ob, md); SHAPE[arm] = verdict
        print(f"| {arm} | {' '.join(f'{x:.4f}' for x in ob)} | {' '.join(f'{x:.4f}' for x in geo_bins(md))} | "
              f"{' '.join('-' if x is None else f'{x:.2f}' for x in rat)} | {verdict} | {f(ms([r['m_deep'] for r in rs]), 5)} |")
    print("\nTwo pools (needs a C started away from 0.5, as exp009's): s = herd genome share at depths 0-4; C fractions"
          " (change / (0.5 - F)) of herd and wild; the core's f_core = (f_herd - s f_wild) / (1 - s); then per trait the"
          " observed herd change against the pull-alone prediction (1 - s) f_core (0.5 - F) + s x wild change. Seed means (SE)")
    print("Applies only to arms whose ancestry fails the geometric shape test (two pools); an arm that passes it is marked"
          " 'does not apply' and its line is printed for reference only (the reviewer's 7377feb).")
    print("| arm | applies | runs | s | f_herd C | f_wild C | f_core | " + " | ".join(f"{t} obs / pull-alone" for t in SELT[:-1]) + " |")
    print("|---|---|---|---|---|---|---|" + "---|" * (len(SELT) - 1))
    for arm in order:
        rs = [r for r in R[arm] if "pool" in r]
        if not rs: continue
        g = lambda k: ms([r["pool"][k] for r in rs])
        ap = "yes" if SHAPE.get(arm) == "not geometric" else "does not apply (geometric shape)"
        print(f"| {arm} | {ap} | {len(rs)} | {f(g('s'), 3)} | {f(g('fh'), 3)} | {f(g('fw'), 3)} | {f(g('fcore'), 3)} | "
              + " | ".join(f"{ms([r['pool']['obs'][t] for r in rs])[0]:+.3f} / {ms([r['pool']['pred'][t] for r in rs])[0]:+.3f}" for t in SELT[:-1]) + " |")
    print("\nObserved - pull-alone herd change, paired within seed (each run's own s and f_core), mean [95% t interval over"
          " seeds]; entirely above 0 for a trait whose wild sits above 0.5 (R A H B), or below 0 for T (below 0.5), = less change"
          " than the pull alone (opposed)")
    print("| arm | applies | " + " | ".join(SELT[:-1]) + " |\n|---|---|" + "---|" * (len(SELT) - 1))
    for arm in order:
        rs = [r for r in R[arm] if "pool" in r]
        if len(rs) < 2: continue
        cells = []
        for t in SELT[:-1]:
            ds = [r["pool"]["obs"][t] - r["pool"]["pred"][t] for r in rs]; m, se = ms(ds); h = tcrit(len(ds)) * se
            cells.append(f"{m:+.3f} [{m - h:+.3f}, {m + h:+.3f}]")
        print(f"| {arm} | {'yes' if SHAPE.get(arm) == 'not geometric' else 'does not apply'} | " + " | ".join(cells) + " |")
    print("\nMedian age at first kidding, herd and wild (years; mean over rows of medianFirstKidAgeHerd / Wild), seed mean (SE):"
          " over the window, and over 401 to the window's end")
    print("| arm | herd, window | wild, window | herd, 401- | wild, 401- |\n|---|---|---|---|---|")
    for arm in order:
        rs = R[arm]
        print(f"| {arm} | " + " | ".join(f(ms([r[k][i] for r in rs]), 3) for i, k in ((0, "fkH"), (0, "fkW"), (1, "fkH"), (1, "fkW"))) + " |")
    print("\nselDam (dams' allele mean - herd does' mean, kids-weighted over the window), seed mean (SE)")
    print("| arm | " + " | ".join(SELT) + " |\n|---|" + "---|" * len(SELT))
    for arm in order:
        print(f"| {arm} | " + " | ".join(f(ms([r['selDam'][t] for r in R[arm]]), 4) for t in SELT) + " |")

def selftest():
    # the inversion reproduces known geometric depths; an impossible depth must stop it
    ok = True
    for m in (0.005, 0.015, 0.044, 0.086, 0.3):
        back = m_from_depth(capped_mean(m)); res = abs(back - m) < 1e-6; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} m {m}: depth {capped_mean(m):.3f} -> m {back:.6f}")
        _, v = shape(geo_bins(m), m); res = v == "geometric"; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} m {m}: planted geometric bins read '{v}'")
    # planted mixture: 10% of the genome fresh from the wild (depths 0-1) that never persists, the rest founders' (20+)
    mix = [0.05, 0.05, 0.0, 0.0, 0.0, 0.90]                       # mean depth 0.05 x 1 + 0.90 x 23 (founders at the cap)
    _, v = shape(mix, m_from_depth(0.05 * 1 + 0.90 * CAP)); res = v == "not geometric"; ok &= res
    print(f"{'ok  ' if res else 'FAIL'} planted transient-inflow mixture reads '{v}'")
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest() else 1)
    main(sys.argv[1:])
