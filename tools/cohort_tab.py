# cohort_tab.py: viability selection between birth and first breeding, from the cohort counters of 434ee46 (exploratory;
# analysis session, 2026-11-20, for the reviewer's question in 7377feb / ed0c0a5: where is the selection that opposes
# the pull in a closed herd?).
#   python tools/cohort_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--pairs HI-LO,...] [--perseed] [--bad KIND]
#   python tools/cohort_tab.py selftest
# Year rows (434ee46 on) hold cohortBirth and cohortBreed, each [wild, herd][female, male] = [summed genotype per trait in
# TRAITS order (R A S B H T M W L C), n]: every kid at birth (wild or herd by its mother), every doe at her first kidding
# and every buck at his first siring (wild or herd by where it bred).
# Per run over the rows in Y0-Y1 (1-based): mean genotype at birth = summed sums / summed n, and at first breeding the
# same; the differential is first breeding - birth (positive = breeders above the kids born; selection between birth and
# first breeding: survival, maturing, and getting to breed). Per arm: seed mean of each run's differential, with the SE
# over seeds of those within-run differences (the paired SE). Also herd - wild differential, paired within run.
# --pairs HI-LO: arm differences of the herd differential over shared seeds (same seed = same history to year 400).
# Read with three caveats:
#   - herd first breeders include captives born wild: their birth was counted in the wild; capBred / cohortBreed n (the
#     captives' share of first breeders, printed) says how much of the herd's breeding cohort that is;
#   - births and first breedings in the same window are different cohorts (first breeders were born years earlier); at a
#     steady state this does not matter, in a changing herd it does;
#   - a buck enters at his first siring (conception), a doe at her first kidding.
# Checks (each must hold in every row read, or the tool stops): cohortBirth n summed over wild and herd, both sexes =
# births; cohortBirth herd n (both sexes) = herdBirths; cohortBreed does' n = firstKidStats n (wild, herd). The selftest
# plants a synthetic run with known means (recovered to 1e-9) and three broken ones (each must stop).
import glob, json, os, re, sys

TRAITS = ["R", "A", "S", "B", "H", "T", "M", "W", "L", "C"]
NT = len(TRAITS)

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
        12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 20: 2.086, 30: 2.042}

def tcrit(n):   # two-sided 95% t for n values
    df = n - 1
    return T975.get(df) or T975[max(k for k in T975 if k <= df)]

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

class CheckFailed(Exception): pass

def check(rows):
    for r in rows:
        cb, cr = r["cohortBirth"], r["cohortBreed"]
        if any(len(cb[h][s]) != NT + 1 or len(cr[h][s]) != NT + 1 for h in (0, 1) for s in (0, 1)):
            raise CheckFailed(f"year {r['year'] + 1}: a cohort row does not hold {NT} trait sums and n")
        nb = sum(cb[h][s][NT] for h in (0, 1) for s in (0, 1))
        if nb != r.get("births"): raise CheckFailed(f"year {r['year'] + 1}: cohortBirth n {nb} != births {r.get('births')}")
        nh = cb[1][0][NT] + cb[1][1][NT]
        if nh != r.get("herdBirths"): raise CheckFailed(f"year {r['year'] + 1}: herd cohortBirth n {nh} != herdBirths {r.get('herdBirths')}")
        for h, p in ((0, "wild"), (1, "herd")):
            fk = ((r.get("firstKidStats") or {}).get(p) or {}).get("n", 0)
            if cr[h][0][NT] != fk: raise CheckFailed(f"year {r['year'] + 1}: {p} does at first kidding {cr[h][0][NT]} != firstKidStats n {fk}")
            # firstSireAge (a659a59) counts the same first sirings as cohortBreed's bucks
            if r.get("firstSireAge") is not None and r["firstSireAge"][h][1] != cr[h][1][NT]:
                raise CheckFailed(f"year {r['year'] + 1}: {p} firstSireAge bucks {r['firstSireAge'][h][1]} != cohortBreed bucks {cr[h][1][NT]}")

def lag_sire(d, rows, h, step):
    """A buck's lag: mean age at first siring over the window's rows (firstSireAge [wild, herd] = [summed days, bucks],
    a659a59), or None where the rows do not all carry it."""
    if not rows or any(r.get("firstSireAge") is None for r in rows): return None
    A = sum(r["firstSireAge"][h][0] for r in rows); N = sum(r["firstSireAge"][h][1] for r in rows)
    if not N: return None
    lag = A / N / ((d.get("_parameters") or {}).get("yearDays") or 360)
    return round(lag / step), lag, "first-sire mean"

def lag_rows(d, rows, h, lag, step):
    """Rows to shift the birth window back so births and first breeders are one cohort (the reviewer's 6c1cc76): lag in
    years = the given --lag; else the MEAN age at first kidding over the window's rows (firstKidStats' age sum a / n,
    herd or wild; under a linear trend the cohort's birth mean sits at the mean age, and the age is right-skewed, so a
    median would bias the correction low: the reviewer's note after c562194); else, where no age sum is recorded, the
    mean over rows of the median first-kid age, labelled. Does' ages, used for bucks too (no age at first siring is
    recorded). In rows = round(lag / the row step). Returns (rows, lag in years, basis)."""
    yd = (d.get("_parameters") or {}).get("yearDays") or 360
    if lag is not None: return round(lag / step), lag, "given"
    p = "herd" if h else "wild"
    st = [(r.get("firstKidStats") or {}).get(p) for r in rows]
    A = sum(s["a"] for s in st if s and "a" in s); N = sum(s["n"] for s in st if s and "a" in s)
    if N: lag = A / N / yd; return round(lag / step), lag, "mean"
    k = "medianFirstKidAgeHerd" if h else "medianFirstKidAgeWild"
    v = [r[k] for r in rows if r.get(k) is not None]
    lag = (sum(v) / len(v) / yd) if v else 0
    return round(lag / step), lag, "median (no age sum recorded)"

def run_cohort(d, y0, y1, bad=None, lag=None):
    allr = d["years"]
    idx = [i for i, r in enumerate(allr) if y0 <= r["year"] + 1 <= y1]
    if not idx: return None
    rows = [allr[i] for i in idx]
    out = {"lag": {}}
    if any("cohortBirth" not in r or "cohortBreed" not in r for r in rows):
        raise CheckFailed("rows without cohortBirth / cohortBreed (runs before 434ee46)")
    if bad == "births": rows = [dict(r, births=r["births"] + 1) if i == 0 else r for i, r in enumerate(rows)]
    check(rows)
    step = allr[1]["year"] - allr[0]["year"] if len(allr) > 1 else 1
    for h, p in ((0, "wild"), (1, "herd")):
        for s, sx in ((0, "F"), (1, "M")):
            # does: the mean first-kid age; bucks: their own first-sire age where recorded (a659a59), else the does' lag,
            # labelled lag-uncertain
            ld = lag_rows(d, rows, h, lag, step)
            k, ly, basis = (lag_sire(d, rows, h, step) or (ld[0], ld[1], ld[2] + ", does' lag: lag-uncertain")) if (s == 1 and lag is None) else ld
            out["lag"][(p, sx)] = (ly, k, basis)
            if idx[0] - k < 0: raise CheckFailed(f"the birth window shifted back {k} rows starts before the first row")
            brow = [allr[i - k] for i in idx]
            if any("cohortBirth" not in r or "cohortBreed" not in r for r in brow):
                raise CheckFailed("rows without cohortBirth / cohortBreed (runs before 434ee46)")
            check(brow)
            b = [sum(r["cohortBirth"][h][s][j] for r in brow) for j in range(NT + 1)]
            q = [sum(r["cohortBreed"][h][s][j] for r in rows) for j in range(NT + 1)]
            b0 = [sum(r["cohortBirth"][h][s][j] for r in rows) for j in range(NT + 1)]
            out[(p, sx)] = {"nb": b[NT], "nq": q[NT], "bs": b, "qs": q,
                            "birth": {t: b[j] / b[NT] for j, t in enumerate(TRAITS)} if b[NT] else None,
                            "breed": {t: q[j] / q[NT] for j, t in enumerate(TRAITS)} if q[NT] else None}
            v = out[(p, sx)]
            v["diff"] = {t: v["breed"][t] - v["birth"][t] for t in TRAITS} if v["birth"] and v["breed"] else None
            # residual-lag correction by trend (the reviewer's c562194): breeders in year t were born at t - L (L = the
            # lag in years) but births are read at t - K (K = the shift in rows x the row step). With the birth mean's
            # slope b per year over the birth window, birth(t - L) = birth(t - K) - b (L - K), so the corrected
            # differential is the raw one + b (L - K). A second estimate of b: (diff at lag K - diff at lag 0) / K.
            pts = [(r["year"], r["cohortBirth"][h][s][NT], r["cohortBirth"][h][s]) for r in brow if r["cohortBirth"][h][s][NT]]
            slope = {}
            if len(pts) >= 2:
                W = sum(n for _, n, _ in pts); xm = sum(y * n for y, n, _ in pts) / W
                sxx = sum(n * (y - xm) ** 2 for y, n, _ in pts)
                for j, t in enumerate(TRAITS):
                    ym = sum(c[j] for _, _, c in pts) / W
                    slope[t] = sum(n * (y - xm) * (c[j] / n - ym) for y, n, c in pts) / sxx if sxx else None
            v["slope"] = slope; v["L_K"] = ly - k * step
            v["diffc"] = {t: v["diff"][t] + (slope.get(t) or 0) * v["L_K"] for t in TRAITS} if v["diff"] else None
            v["slope2"] = ({t: (v["diff"][t] - (v["breed"][t] - b0[j] / b0[NT])) / (k * step) for j, t in enumerate(TRAITS)}
                           if v["diff"] and b0[NT] and k else None)
    rows = [allr[i] for i in idx]
    cb = [sum((r.get("capBred") or [0, 0])[k] for r in rows) for k in (0, 1)]
    out["capshare"] = tuple(cb[k] / out[("herd", sx)]["nq"] if out[("herd", sx)]["nq"] else None for k, sx in ((0, "F"), (1, "M")))
    return out

def load(folders, arms):
    F = {}
    for folder in folders.split(";"):
        for fn in glob.glob(os.path.join(folder, "*.json")):
            mt = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(fn))
            if mt and (arms is None or mt.group(1) in arms):
                if int(mt.group(2)) in F.setdefault(mt.group(1), {}): sys.exit(f"duplicate {fn}")
                F[mt.group(1)][int(mt.group(2))] = fn
    return F

def main(a):
    bad = None; pairs = []; perseed = "--perseed" in a; a = [x for x in a if x != "--perseed"]
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if "--pairs" in a: i = a.index("--pairs"); pairs = [p.split("-") for p in a[i + 1].split(",")]; del a[i:i + 2]
    lag = None
    if "--lag" in a: i = a.index("--lag"); lag = float(a[i + 1]); del a[i:i + 2]
    y0, y1 = (int(v) for v in a[0].split("-")); arms = a[2].split(",") if len(a) > 2 else None
    # exp010's runs span code versions and only the later ones carry the counters, a non-random subset (the reviewer's
    # 6c1cc76): not read
    if "exp010" in a[1]: sys.exit("exp010 is not read by this tool: only its later runs carry the cohort counters (6c1cc76)")
    F = load(a[1], arms); order = [x for x in (arms or sorted(F)) if x in F]
    R = {}
    for arm in order:
        R[arm] = {}
        for s, fn in sorted(F[arm].items()):
            try: v = run_cohort(json.load(open(fn, encoding="utf-8")), y0, y1, bad, lag)
            except CheckFailed as e: sys.exit(f"check failed: {os.path.basename(fn)}: {e}")
            if v: R[arm][s] = v
    print(f"years {y0}-{y1} for first breeders; births read from the window shifted back by the first-breeding lag (one"
          " cohort, the reviewer's 6c1cc76); differential = mean genotype at first breeding - at birth, per run, then seed"
          " mean (paired SE over seeds), and pooled over seeds (summed counts); herd first breeders include captives born"
          " wild (their share printed). Exploratory.")
    for arm in order:
        for p in ("herd", "wild"):
            for sx in ("F", "M"):
                ls = [v["lag"][(p, sx)] for v in R[arm].values()]
                if ls: print(f"  {arm} {p} {'does' if sx == 'F' else 'bucks'}: lag {ms([x[0] for x in ls])[0]:.2f} y, shift"
                             f" {sorted(set(x[1] for x in ls))} rows, basis {sorted(set(x[2] for x in ls))}")
    print("Read does first (the reviewer's c562194). Bucks take their own lag from the age at first siring (firstSireAge,"
          " a659a59) where the runs record it; where they borrow the does' lag the group is labelled lag-uncertain. C is"
          " the control that can fail: nothing selects it, so its corrected differential must hold 0 inside its 95%"
          " interval over seeds, or no trait of that arm and group is read. A null on a trait rules out viability"
          " selection before first breeding only, not opposing selection in general.")
    unc = lambda p: any("lag-uncertain" in v["lag"][(p, "M")][2] for a in order for v in R[a].values())
    for p, sx, lab in (("herd", "F", "herd does"), ("wild", "F", "wild does"),
                       ("herd", "M", "herd bucks" + (" (lag-uncertain)" if unc("herd") else "")),
                       ("wild", "M", "wild bucks" + (" (lag-uncertain)" if unc("wild") else ""))):
        print(f"\n{lab}: first breeding - birth, trend-corrected (raw differential + slope x (lag - rounded lag)), seed mean"
              " (paired SE); pooled over seeds (summed counts, plus the seed-mean correction); uncorrected")
        print("| arm | reading | seeds | born / first-bred per run | " + " | ".join(TRAITS) + " |\n|---|---|---|---|" + "---|" * NT)
        for arm in order:
            vs = [v[(p, sx)] for v in R[arm].values() if v[(p, sx)]["diff"]]
            if not vs: print(f"| {arm} | - | 0 | - |" + " - |" * NT); continue
            nb, nq = ms([v["nb"] for v in vs])[0], ms([v["nq"] for v in vs])[0]
            cC = [v["diffc"]["C"] for v in vs]; m, se = ms(cC); hw = tcrit(len(cC)) * se if len(cC) > 1 else None
            ctl = "C control: too few seeds" if hw is None else (f"C control passes ({m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}])"
                  if abs(m) <= hw else f"C control FAILS ({m:+.4f} [{m - hw:+.4f}, {m + hw:+.4f}]): read no trait here")
            print(f"| {arm} | corrected | {len(vs)} | {nb:.0f} / {nq:.0f} | " + " | ".join("{:+.4f} ({:.4f})".format(*ms([v["diffc"][t] for v in vs])) for t in TRAITS) + " |")
            B = [sum(v["bs"][j] for v in vs) for j in range(NT + 1)]; Q = [sum(v["qs"][j] for v in vs) for j in range(NT + 1)]
            corr = {t: ms([(v["slope"].get(t) or 0) * v["L_K"] for v in vs])[0] for t in TRAITS}
            print(f"| {arm} | pooled, corrected | {len(vs)} | {B[NT]:.0f} / {Q[NT]:.0f} total | " + " | ".join(f"{Q[j] / Q[NT] - B[j] / B[NT] + corr[t]:+.4f}" for j, t in enumerate(TRAITS)) + " |")
            print(f"| {arm} | uncorrected | {len(vs)} | | " + " | ".join("{:+.4f} ({:.4f})".format(*ms([v["diff"][t] for v in vs])) for t in TRAITS) + " |")
            s1 = {t: ms([v["slope"].get(t) for v in vs])[0] for t in ("C", "B", "T")}
            s2 = {t: ms([v["slope2"][t] for v in vs if v["slope2"]])[0] for t in ("C", "B", "T")}
            f6 = lambda x: "-" if x is None else f"{x * 1000:+.3f}"
            print(f"|  | {ctl}; lag - rounded lag {ms([v['L_K'] for v in vs])[0]:+.2f} y; birth-mean slope per 1000 y, regression / lag-0"
                  f" estimate: " + ", ".join(f"{t} {f6(s1[t])} / {f6(s2[t])}" for t in ("C", "B", "T")) + " |")
    for sx, lab in (("F", "does"), ("M", "bucks")):
        print(f"\nherd - wild differential, {lab}, paired within run")
        print("| arm | seeds | " + " | ".join(TRAITS) + " |\n|---|---|" + "---|" * NT)
        for arm in order:
            vs = [v for v in R[arm].values() if v[("herd", sx)]["diff"] and v[("wild", sx)]["diff"]]
            if not vs: continue
            print(f"| {arm} | {len(vs)} | " + " | ".join("{:+.4f} ({:.4f})".format(*ms([v[("herd", sx)]["diff"][t] - v[("wild", sx)]["diff"][t] for v in vs])) for t in TRAITS) + " |")
    print("\ncaptives' share of the herd's first breeders (capBred / cohortBreed herd n), seed mean (SE): does | bucks")
    for arm in order:
        vs = list(R[arm].values())
        print(f"  {arm}: " + " | ".join("-" if ms([v['capshare'][k] for v in vs])[0] is None else "{:.3f} ({:.3f})".format(*ms([v['capshare'][k] for v in vs])) for k in (0, 1)))
    for hi, lo in pairs:
        if hi not in R or lo not in R: print(f"\n{hi} - {lo}: arm missing"); continue
        sh = [s for s in R[hi] if s in R[lo]]
        print(f"\n{hi} - {lo}, herd differential, paired over {len(sh)} shared seeds: does / bucks per trait")
        for sx in ("F", "M"):
            cells = []
            for t in TRAITS:
                ds = [R[hi][s][("herd", sx)]["diff"][t] - R[lo][s][("herd", sx)]["diff"][t] for s in sh
                      if R[hi][s][("herd", sx)]["diff"] and R[lo][s][("herd", sx)]["diff"]]
                m = ms(ds); cells.append("-" if m[0] is None else f"{t} {m[0]:+.4f} ({m[1]:.4f})")
            print(f"  {sx}: " + ", ".join(cells))
    if perseed:
        print("\nper run, herd differential on R A H B T (does | bucks):")
        for arm in order:
            for s, v in sorted(R[arm].items()):
                f = lambda sx: " ".join("-" if not v[("herd", sx)]["diff"] else f"{v[('herd', sx)]['diff'][t]:+.4f}" for t in "RAHBT")
                print(f"  {arm} s{s}: {f('F')} | {f('M')}")

def synthetic(births_off=0, herd_off=0, fk_off=0, short=False, sire=None):
    # two rows 3 years apart (0-based 3197, 3200); first-kid age 3 y, so births are read one row back. Row 3197: wild does
    # born 4 at 0.5, herd bucks born 2 at 0.3 (the cohort). Row 3200: births of a later cohort at 0.9 (wild does, 4) and
    # 0.8 (herd bucks, 2), which a same-year reading would wrongly use; first breeders: wild does 2 at 0.6, herd bucks 1 at 0.4.
    z = lambda: [0.0] * (NT + 1)
    def row(year, wb, hb, wq, hq, fkn):
        cb = [[z(), z()], [z(), z()]]; cr = [[z(), z()], [z(), z()]]
        cb[0][0] = [wb * 4] * NT + [4]; cb[1][1] = [hb * 2] * NT + [2]
        if wq is not None: cr[0][0] = [wq * 2] * NT + [2]; cr[1][1] = [hq * 1] * NT + [1]
        return {"year": year, "births": 6, "herdBirths": 2, "cohortBirth": cb, "cohortBreed": cr, "capBred": [0, 1] if wq else [0, 0],
                "firstKidStats": {"wild": {"n": fkn}, "herd": None}, "medianFirstKidAgeWild": 1080, "medianFirstKidAgeHerd": 1080}
    r0, r1 = row(3197, 0.5, 0.3, None, None, 0), row(3200, 0.9, 0.8, 0.6, 0.4, 2)
    r1["births"] += births_off; r1["herdBirths"] += herd_off; r1["firstKidStats"]["wild"]["n"] += fk_off
    if sire: r1["firstSireAge"] = [[0, 0], [sire[0] * sire[1], sire[1]]]   # (days, bucks): herd bucks' first siring
    if short: r1["cohortBirth"][1][1] = r1["cohortBirth"][1][1][:-2] + [2]
    return {"_parameters": {"yearDays": 360}, "years": [r0, r1]}

def selftest():
    ok = True
    v = run_cohort(synthetic(), 3201, 3201)
    got = (v[("wild", "F")]["diff"]["R"], v[("herd", "M")]["diff"]["C"], v["capshare"][1], v["lag"][("wild", "F")][1])
    res = all(abs(x - y) < 1e-9 for x, y in zip(got, (0.1, 0.1, 1.0, 1))); ok &= res
    print(f"{'ok  ' if res else 'FAIL'} planted cohort means recovered: wild does R {got[0]:+.4f} (want +0.1), herd bucks C"
          f" {got[1]:+.4f} (want +0.1), captive share of herd bucks {got[2]}, shift {got[3]} row")
    v0 = run_cohort(synthetic(), 3201, 3201, lag=0)
    res = abs(v0[("wild", "F")]["diff"]["R"] - (-0.3)) < 1e-9; ok &= res
    print(f"{'ok  ' if res else 'FAIL'} with --lag 0 the same-year births are used: wild does R {v0[('wild', 'F')]['diff']['R']:+.4f} (want -0.3)")
    for name, kw, y in (("births off by one", {"births_off": 1}, 3201), ("herdBirths off by one", {"herd_off": 1}, 3201),
                        ("firstKidStats off by one", {"fk_off": 1}, 3201), ("a short cohort row", {"short": True}, 3201),
                        ("a birth window before the first row", {}, 3198)):
        try: run_cohort(synthetic(**kw), y, y); res = False
        except CheckFailed: res = True
        ok &= res; print(f"{'ok  ' if res else 'FAIL'} {name}: check {'stops' if res else 'does NOT stop'}")
    # trend: births rise 0.1 per row (3 y), the true lag is 3.3 y (rounded to one row, 3 y), breeders sit 0.05 above
    # their true cohort; the raw differential is +0.04 and the corrected one must be +0.05
    v = run_cohort(trended(), 3198, 3201)
    raw, cor = v[("wild", "F")]["diff"]["R"], v[("wild", "F")]["diffc"]["R"]
    res = abs(raw - 0.04) < 1e-9 and abs(cor - 0.05) < 1e-9; ok &= res
    print(f"{'ok  ' if res else 'FAIL'} trend correction: raw {raw:+.4f} (want +0.04), corrected {cor:+.4f} (want +0.05)")
    # the same run read with the median's 3.0 y (what a median-based lag gives here) must miss the planted 0.3 y
    cm = run_cohort(trended(), 3198, 3201, lag=3.0)[("wild", "F")]["diffc"]["R"]
    res = abs(cm - 0.04) < 1e-9 and v["lag"][("wild", "F")][2] == "mean"; ok &= res
    print(f"{'ok  ' if res else 'FAIL'} mean basis used ({v['lag'][('wild', 'F')][2]}); a median-based 3.0 y lag would read {cm:+.4f} (want +0.04, low by b x 0.3)")
    # bucks: without firstSireAge they borrow the does' 3 y (one row back: +0.1, labelled lag-uncertain); with a first-sire
    # age of 300 days they shift 0 rows and read the same-year births (0.4 - 0.8 = -0.4) under their own basis
    vb = run_cohort(synthetic(), 3201, 3201); vs = run_cohort(synthetic(sire=(300, 1)), 3201, 3201)
    res = (abs(vb[("herd", "M")]["diff"]["C"] - 0.1) < 1e-9 and "lag-uncertain" in vb["lag"][("herd", "M")][2]
           and abs(vs[("herd", "M")]["diff"]["C"] + 0.4) < 1e-9 and vs["lag"][("herd", "M")][2] == "first-sire mean"
           and abs(vs[("wild", "F")]["diff"]["R"] - 0.1) < 1e-9); ok &= res
    print(f"{'ok  ' if res else 'FAIL'} buck lag: borrowed {vb[('herd', 'M')]['diff']['C']:+.4f} ({vb['lag'][('herd', 'M')][2]});"
          f" own first-sire age {vs[('herd', 'M')]['diff']['C']:+.4f} ({vs['lag'][('herd', 'M')][2]}); does unchanged {vs[('wild', 'F')]['diff']['R']:+.4f}")
    try: run_cohort(synthetic(sire=(300, 2)), 3201, 3201); res = False
    except CheckFailed: res = True
    ok &= res; print(f"{'ok  ' if res else 'FAIL'} firstSireAge buck count off by one: check {'stops' if res else 'does NOT stop'}")
    print("selftest " + ("passes" if ok else "FAILS")); return ok

def trended(c_sel=0.05, seed=None):
    # four rows, 0-based 3191-3200 every 3 y; wild does born 4 a row at 0.3, 0.4, 0.5, 0.6 (C the same); first-kid age
    # 3.3 y as the MEAN (firstKidStats age sum), 3.0 y as the median (so a median-based lag would miss the 0.3 y); breeders (2 a row, in rows 3197 and 3200) at their true cohort's birth mean + 0.05 (C: + c_sel) + seed noise
    z = lambda: [0.0] * (NT + 1); yrs = [3191, 3194, 3197, 3200]; bm = lambda y: 0.3 + (y - 3191) * 0.1 / 3
    out = []
    for y in yrs:
        cb = [[z(), z()], [z(), z()]]; cr = [[z(), z()], [z(), z()]]
        cb[0][0] = [bm(y) * 4] * NT + [4]
        if y >= 3197:
            e = 0 if seed is None else 0.004 * ((seed * 7 + y) % 5 - 2)
            cr[0][0] = [(bm(y - 3.3) + (c_sel if t == "C" else 0.05) + e) * 2 for t in TRAITS] + [2]
        out.append({"year": y, "births": 4, "herdBirths": 0, "cohortBirth": cb, "cohortBreed": cr, "capBred": [0, 0],
                    "firstKidStats": {"wild": {"n": cr[0][0][NT], "a": cr[0][0][NT] * 1188}, "herd": None}, "medianFirstKidAgeWild": 1080})
    return {"_parameters": {"yearDays": 360}, "years": out}

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest() else 1)
    main(sys.argv[1:])
