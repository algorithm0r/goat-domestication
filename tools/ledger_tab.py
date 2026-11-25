# ledger_tab.py: exp020's scorer over the herd ledger (analysis session, 2026-11-24; EXPLOG "exp020" 7b7d63d as amended
# by "exp020 amendment" c91c20b and "exp020 amendment 2" ffa8a83, which govern; Chris: "i want to look at the period when the R moves and the herd grows
# specifically. let's get detailed looks at those periods").
#   python tools/ledger_tab.py "DIR[;DIR...]" ARM,ARM... [--perseed] [--timeline [BIN]] [--bad died|load] [--testJ N]
#       [--as FILEARM=ARM,...] [--refJ "DIR=ARM[;DIR=ARM...]"] [--without S[,S...]]
#   --as reads a file arm under another name (the probe's REFledger470 as REF, so --testJ reaches the predictions).
#   --without S[,S] prints P2a and P2b again without those REF seeds (a seed seen before results: REF s6, the J probe).
#   --refJ prints each arm's J beside the J computed the same way from another batch's runs of that arm (exp018 REF,
#   exp010 LOAD05); a difference is reported, not fixed.
#   python tools/ledger_tab.py selftest [--bad died|phase]
# Reads year rows with a ledger (logLedger=1, src/world.js newLedger names every field) and annual rows (recordEvery 1).
# Pooled over the three camps; origin o0 = captured itself (gsc 0), o1 = herd-born. Year labels = index + 1.
# Phases per run, from J = jump_tab's establishment year as load_tab and density_tab compute it (jump_tab.herd_series(d,
# 100) after label 500, jump_tab.jump at >= 100 held 400 years), from this run's own annual rows:
#   A = 401..J-100 (the small herd; empty if J-100 < 401), T = max(401, J-99)..J (the climb), B = J+1..J+100,
#   C = J+101..last label. jump follows a run to its last label - 400 (1200 in a 1600-year run); with no J there, the seed
#   is named and A runs to the last label.
# 1. Timeline (--timeline, BIN years per line, default 1): herd N (year-end stock), mean R by origin and pooled, the
#    captured share of the stock; realized load (summed load / managed camp-days) and herders per managed camp-day; per
#    walking goat-day by origin, the rule's daily spook rate (herderAlarm x R x fear x load, expected spooks per walking
#    goat-day; it can exceed 1) and R x fear; the shares of each origin's goat-days walking, kept at camp and other; the
#    wild's mean R, (traitMeans R x goats - herdTraitMeans R x herded) / (goats - herded) (genotypic, exact to the
#    record's 4 places), with the histogram's binned wild R (split_tab.mc of hist - histHerd) beside it. Two comparisons each line (amendment point 5): the stock's mean R beside histHerd's binned mean R
#    (split_tab.mc), and herder spooks per walking goat-day (ev.spooked / walk goat-days, both origins) beside the rule's
#    rate (walk[3] / walk[0]); a run's summary gives the mean and widest stock - histHerd gap and the run's spooks / rate.
# 2. R accounting: with last year's pooled stock N0, mean R0 and this year's stock N, channel k, origin o (n goats, summed
#    R S) contributes +(S - n R0) / N for an in, - for an out; summed over channels and origins it is exactly R - R0.
#    Years with N0 < 5, or N = 0, are not split: their change is "restart" (from the last year with a herd; pooled over
#    origins and camps, so one camp's herd dying out and refounded is split as ordinary flows). Per phase, summed, three
#    ways (captured, herd-born, both): capture, born (herd sire), bornW (wild sire), lost (lostRun + lostNight, also apart),
#    culled (slaughter), died (any other death), gift (exIn - exOut, not registered, printed so the sum closes); restart
#    (both only). The phase's change runs from the last year with a herd before the phase to its last year with a herd,
#    and equals channels + restart. The first phase with a herd starts from the founders' mean (its first year with a
#    herd, whose captures are not split: there is no earlier mean to split them against).
#    The herd-born stock alone (amendment 2, C): the same split of the change in the herd-born mean R, with the herd-born
#    N, the herd-born last-year mean and the herd-born channels only (born, bornW, lost, culled, died, gift); restart when
#    the previous herd-born count is under 5. Checked per year and per phase like the pooled split.
# 3. Spook filter, per phase and origin: herder spooks per walking goat-day; spread-alarm catches per walking goat-day;
#    mean R of spooked goats minus mean R of walking goat-days; lost on refetch / ran off; mean R of goats lost (run-off and
#    night stray), fetched back, come back on their own, and walking; walking R x fear.
# 4. Captives, per phase: loss rate (lost) per goat-year of exposure by origin, exposure = midday goat-days (walk + kept +
#    other) / yearDays, with the year-end-stock rate beside; deaths and slaughter per exposure goat-year; the captured share
#    of goat-days kept at camp, and the share of captured goat-days kept; captures per year; captive-sire share
#    (flow_tab.run_flow's csire over the phase's rows).
# Predictions (amendments c91c20b and ffa8a83):
#   1. Over B, against the median of LOAD05's phase-B values (over the LOAD05 seeds with a B, named): (a) REF's walking R x
#      fear (walk[2] / walk[0], both origins) below it, (b) REF's rule rate per walking goat-day (walk[3] / walk[0], both
#      origins) above it, each in 6 or more of 8 REF seeds. Walking R (walk[1] / walk[0]) and the share of each origin's
#      goat-days kept beside, by origin; and, descriptive and following from herdN = 1 (economy 0), REF's load over B
#      above 2 (camp herd above 40).
#   2. (a) REF over A, T and B pooled: lost (both origins) the most negative channel among capture, born, bornW, lost,
#      culled and died, in 6 or more of 8 seeds. (b) Herd-born lost the most negative of the herd-born stock's own channels
#      (born, bornW, lost, culled, died; its own mean and N, amendment 2), in 6 or more of 8. Each printed per phase.
#   3. REF over B: captured lost per exposure goat-year above herd-born in every seed read, and the ratio above the median
#      of LOAD05's read seeds in 6 or more of 8 REF seeds. A seed is read with 20 or more captured exposure goat-years in B
#      and a herd-born loss rate above 0; scored only with 6 or more seeds of each arm read; kept shares beside.
#   A prediction needing 6 of 8 with fewer than 6 seeds readable is "not read".
# Checks (the tool stops on any): every row has a ledger with one entry per camp; rows annual; herdingAt 400; per row,
#    stock goats = herded and stock mean R = herdTraitMeans R (to 2e-4); per camp-row, the summed load is >= minLoad x
#    days, = it under a fixed load (herdPerHerder >= 1e8), and >= summed herd / herdPerHerder on a one-herder camp; per
#    split year, channels sum to the change in mean R (to 1e-3); per phase, channels + restart = its change (to 5e-3).
#    selftest runs first: planted herd series give J 767 with A 401-667, T 668-767, B 768-867, C 868-1600, and no J
#    without a jump; J 450 gives no A and T 401-450 (the clip); a planted ledger splits exactly (+0.1 = capture +0.0727 +
#    died +0.0273, by origin), a small previous stock goes to restart, and a planted phase sums. --bad died drops the died
#    channel (must stop, on data and in the selftest); --bad load divides each camp's summed load by 3 (must stop on the
#    load checks); selftest --bad phase starts B at J (must stop). On data the selftest runs without --bad. --testJ N sets
#    every run's J to N to run the T, B and C paths on a short probe; its output says so and is not a reading.
import glob, json, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jump_tab, flow_tab, split_tab

INS, OUTS = ["cap", "born", "bornW", "exIn"], ["lostRun", "lostNight", "culled", "died", "exOut"]
FCH = ["capture", "born", "bornW", "lost", "lostRun", "lostNight", "culled", "died", "gift"]   # flow channels, by origin
SUMCH = ["capture", "born", "bornW", "lost", "culled", "died", "gift"]                         # the ones that sum
P2A, P2B = ["capture", "born", "bornW", "lost", "culled", "died"], ["born", "bornW", "lost", "culled", "died"]
PH = ("A", "T", "B", "C")
TOL_Y, TOL_P, TOL_M = 1e-3, 5e-3, 2e-4

def params(d): return d.get("_parameters") or d.get("params") or {}
def fs(r, k, o, i): return sum(L["flow"][k][o][i] for L in r["ledger"])
def es(r, k, o, i): return sum(L["ev"][k][o][i] for L in r["ledger"])
def st(r, o, i): return sum(L["stock"][o][i] for L in r["ledger"])
def dy(r, k): return sum(L["day"][k] for L in r["ledger"])
def dyo(r, k, o, i=None): return sum((L["day"][k][o] if i is None else L["day"][k][o][i]) for L in r["ledger"])

def jJ(d):
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    return jump_tab.jump(hs, lambda v: v >= 100, 400)[0] if hs else None

def phases(J, last, bad=None):
    if J is None: return {"A": (401, last)}
    ph = {}
    if J - 100 >= 401: ph["A"] = (401, J - 100)
    ph["T"] = (max(401, J - 99), J)
    ph["B"] = (J if bad == "phase" else J + 1, min(J + 100, last))
    if J + 101 <= last: ph["C"] = (J + 101, last)
    return ph

def account(rows, bad=None, og=(0, 1)):
    """Per row label -> (c: channel -> [o0, o1], restart, split?, R or None), for the stock of origins og (both: the
    pooled herd; (1,): the herd-born stock on its own). Stops if a split year does not close."""
    res, lastR = {}, None
    for i, r in enumerate(rows):
        N = sum(st(r, o, 0) for o in og); S = sum(st(r, o, 1) for o in og); R = S / N if N else None
        c = {k: [0.0, 0.0] for k in FCH}; rs = 0.0
        if i and rows[i - 1]["year"] == r["year"] - 1:
            p = rows[i - 1]; N0 = sum(st(p, o, 0) for o in og); S0 = sum(st(p, o, 1) for o in og)
            if N0 >= 5 and N > 0:
                R0 = S0 / N0
                f = lambda k, o: (fs(r, k, o, 1) - fs(r, k, o, 0) * R0) / N
                for o in og:
                    c["capture"][o], c["born"][o], c["bornW"][o] = f("cap", o), f("born", o), f("bornW", o)
                    c["lostRun"][o], c["lostNight"][o] = -f("lostRun", o), -f("lostNight", o)
                    c["lost"][o] = c["lostRun"][o] + c["lostNight"][o]
                    c["culled"][o] = -f("culled", o); c["died"][o] = 0.0 if bad == "died" else -f("died", o)
                    c["gift"][o] = f("exIn", o) - f("exOut", o)
                tot = sum(sum(c[k]) for k in SUMCH)
                if abs(tot - (R - R0)) > TOL_Y:
                    sys.exit(f"check failed: year {r['year'] + 1}{' (herd-born stock)' if og == (1,) else ''}: channels sum to {tot:+.5f}, mean R changes {R - R0:+.5f}")
                res[r["year"] + 1] = (c, 0.0, True, R); lastR = R; continue
        if R is not None and lastR is not None: rs = R - lastR
        res[r["year"] + 1] = (c, rs, False, R)
        if R is not None: lastR = R
    return res

def phase_acc(acc, lab0, lab1):
    """Summed channels (by origin) and restart over labels lab0..lab1, and the phase's change, checked against them."""
    labs = sorted(l for l in acc if lab0 <= l <= lab1)
    tot = {k: [sum(acc[l][0][k][o] for l in labs) for o in (0, 1)] for k in FCH}
    tot["restart"] = sum(acc[l][1] for l in labs)
    before = [acc[l][3] for l in sorted(acc) if l < lab0 and acc[l][3] is not None]
    inside = [acc[l][3] for l in labs if acc[l][3] is not None]
    if not inside: return tot
    ch = inside[-1] - (before[-1] if before else inside[0])   # no herd before: its first year's restart is 0
    s = sum(sum(tot[k]) for k in SUMCH) + tot["restart"]
    if abs(s - ch) > TOL_P: sys.exit(f"check failed: phase {lab0}-{lab1}: channels + restart {s:+.5f}, change {ch:+.5f}")
    tot["change"] = ch
    return tot

def selftest(bad):
    # phases on a planted herd series: herded 0 to index 699, 150 from 700 (label 701) to 1599; the 100-year mean
    # reaches 100 at label 767 (67 rows of 150)
    d = {"years": [{"year": i, "herded": 0 if i < 700 else 150} for i in range(1600)]}
    J = jJ(d); ph = phases(J, 1600, bad)
    if J != 767 or ph != {"A": (401, 667), "T": (668, 767), "B": (768, 867), "C": (868, 1600)}: sys.exit(f"selftest failed: J {J}, phases {ph}")
    d0 = {"years": [{"year": i, "herded": 40} for i in range(1600)]}
    if jJ(d0) is not None or phases(None, 1600) != {"A": (401, 1600)}: sys.exit("selftest failed: a series with no jump gave a J")
    if phases(450, 1600) != {"T": (401, 450), "B": (451, 550), "C": (551, 1600)}: sys.exit(f"selftest failed: clip {phases(450, 1600)}")
    if phases(501, 1600)["A"] != (401, 401) or phases(1550, 1600) != {"A": (401, 1450), "T": (1451, 1550), "B": (1551, 1600)}:
        sys.exit("selftest failed: J 501 or a B cut by the run's end")
    # accounting on a planted ledger. Year 1: stock 5 captured (summed R 2.5) and 5 herd-born (2.5), mean 0.5. Year 2: two
    # captures (R 1.8), one herd-born death (R 0.2): stock 7 (4.3) + 4 (2.3) = 11, R 6.6, mean 0.6; capture o0
    # +(1.8 - 1.0)/11 = +0.07273, died o1 -(0.2 - 0.5)/11 = +0.02727. Year 3: six captured (R 3.5) and two herd-born (R 1.0)
    # die: stock 1 (0.8) + 2 (1.3) = 3, R 2.1, mean 0.7; died o0 -(3.5 - 3.6)/3 = +0.03333, o1 -(1.0 - 1.2)/3 = +0.06667.
    # Year 4: previous stock 3 < 5, one capture (R 1.0): stock 4, R 3.1, mean 0.775, a restart of +0.075.
    def L(stock, **fl):
        flow = {k: [[0, 0], [0, 0]] for k in INS + OUTS}
        for k, v in fl.items(): flow[k] = v
        return {"flow": flow, "ev": {}, "stock": stock, "day": {}}
    rows = [{"year": 0, "ledger": [L([[5, 2.5, 0, 0], [5, 2.5, 0, 0]])]},
            {"year": 1, "ledger": [L([[7, 4.3, 0, 0], [4, 2.3, 0, 0]], cap=[[2, 1.8], [0, 0]], died=[[0, 0], [1, 0.2]])]},
            {"year": 2, "ledger": [L([[1, 0.8, 0, 0], [2, 1.3, 0, 0]], died=[[6, 3.5], [2, 1.0]])]},
            {"year": 3, "ledger": [L([[2, 1.8, 0, 0], [2, 1.3, 0, 0]], cap=[[1, 1.0], [0, 0]])]}]
    a = account(rows, bad)
    c, _, sp, R = a[2]
    if not sp or abs(c["capture"][0] - 0.8 / 11) > 1e-9 or abs(c["died"][1] - 0.3 / 11) > 1e-9 or c["died"][0] or abs(R - 0.6) > 1e-9:
        sys.exit(f"selftest failed: planted split {c}, R {R}")
    if not a[3][2] or abs(a[3][0]["died"][0] - 0.1 / 3) > 1e-9 or abs(a[3][0]["died"][1] - 0.2 / 3) > 1e-9: sys.exit(f"selftest failed: planted split, year 3: {a[3]}")
    if a[4][2] or abs(a[4][1] - 0.075) > 1e-9: sys.exit(f"selftest failed: small previous stock not a restart: {a[4]}")
    b = account(rows, bad, (1,))
    # (year 3's previous herd-born count is 4 < 5, so year 3 is a restart of +0.075 on the herd-born stock, though the
    # pooled stock splits it)
    if not b[2][2] or abs(b[2][0]["died"][1] - 0.075) > 1e-9 or b[2][0]["died"][0] or b[3][2] or abs(b[3][1] - 0.075) > 1e-9 or b[4][2]:
        sys.exit(f"selftest failed: herd-born split {b[2]}, {b[3]}, {b[4]}")
    tb = phase_acc(b, 1, 4)
    if abs(tb["change"] - 0.15) > 1e-9: sys.exit(f"selftest failed: herd-born phase {tb}")
    t = phase_acc(a, 1, 4)
    if abs(t["change"] - 0.275) > 1e-9 or abs(t["restart"] - 0.075) > 1e-9 or abs(t["died"][1] - (0.3 / 11 + 0.2 / 3)) > 1e-9:
        sys.exit(f"selftest failed: planted phase {t}")
    print("selftest: phases (J 767: A 401-667, T 668-767, B 768-867, C 868-1600; no jump; J 450 clip; J 501; B cut at the end), "
          "planted split by origin, restart and phase sum; herd-born stock alone: ok")

def load_runs(dirs, arms):
    R = {}
    for folder in dirs.split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and m.group(1) in arms:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    return R

def check_rows(d, name, bad=None):
    P = params(d); ys = d["years"]; mL, hpp = P.get("minLoad"), P.get("herdPerHerder")
    if bad == "load":   # the summed load read as if pooled over the three camps: must stop on the load checks
        for r in ys:
            for L in r.get("ledger") or []: L["day"]["load"] /= 3
    if P.get("herdingAt") != 400: sys.exit(f"{name}: herdingAt {P.get('herdingAt')}, not 400")
    for a, b in zip(ys, ys[1:]):
        if b["year"] - a["year"] != 1: sys.exit(f"{name}: rows not annual at year {b['year'] + 1}")
    for r in ys:
        L = r.get("ledger")
        if not L or len(L) != P.get("camps", 3): sys.exit(f"{name} year {r['year'] + 1}: no ledger, or not one per camp")
        N = st(r, 0, 0) + st(r, 1, 0)
        if N != r["herded"]: sys.exit(f"check failed: {name} year {r['year'] + 1}: stock {N}, herded {r['herded']}")
        if N:
            m = (st(r, 0, 1) + st(r, 1, 1)) / N; h = (r.get("herdTraitMeans") or {}).get("R")
            if h is None or abs(m - h) > TOL_M: sys.exit(f"check failed: {name} year {r['year'] + 1}: stock mean R {m:.5f}, herdTraitMeans R {h}")
        for c, Lc in enumerate(L):   # the realized load against herdLoad's rule, per camp
            D = Lc["day"]
            if not D["days"] or mL is None: continue
            w = f"check failed: {name} year {r['year'] + 1} camp {c}: summed load {D['load']}"
            if D["load"] < mL * D["days"] - 1e-3: sys.exit(f"{w} below minLoad x days {mL * D['days']:.4f}")
            if hpp and hpp >= 1e8 and abs(D["load"] - mL * D["days"]) > 1e-3: sys.exit(f"{w}, fixed load {mL} x days {D['days']}")
            if hpp and hpp < 1e8 and D["herders"] == D["days"] and D["load"] < D["herd"] / hpp - 1e-3: sys.exit(f"{w} below summed herd / herdPerHerder {D['herd'] / hpp:.4f}")

def wildR(r):
    t, h, g, n = (r.get("traitMeans") or {}).get("R"), (r.get("herdTraitMeans") or {}).get("R"), r.get("goats"), r.get("herded") or 0
    if t is None or not g or g <= n: return None
    return (t * g - (h or 0) * n) / (g - n)

def summ(d, rows, acc, a, b, acc1=None):
    rs = [r for r in rows if a <= r["year"] + 1 <= b]
    if not rs: return None
    yd = params(d).get("yearDays", 360); days = sum(dy(r, "days") for r in rs)
    q = lambda x, y: x / y if y else None
    S = lambda f: sum(f(r) for r in rs)
    o = {"years": len(rs), "lab": (a, b), "herd": S(lambda r: st(r, 0, 0) + st(r, 1, 0)) / len(rs),
         "load": q(S(lambda r: dy(r, "load")), days), "herders": q(S(lambda r: dy(r, "herders")), days),
         "campHerd": q(S(lambda r: dy(r, "herd")), days), "acc": phase_acc(acc, a, b), "acc1": phase_acc(acc1, a, b) if acc1 else None}
    NN = [S(lambda r: st(r, k, 0)) for k in (0, 1)]
    o["captShare"] = q(NN[0], sum(NN))
    for k in (0, 1):
        wn, wr, wf = (S(lambda r: dyo(r, "walk", k, i)) for i in (0, 1, 2))
        kn, on_ = S(lambda r: dyo(r, "kept", k, 0)), S(lambda r: dyo(r, "other", k))
        sn, sr = S(lambda r: es(r, "spooked", k, 0)), S(lambda r: es(r, "spooked", k, 1))
        cn = S(lambda r: es(r, "caught", k, 0)); ro = S(lambda r: es(r, "ranOff", k, 0))
        ln, lr = S(lambda r: fs(r, "lostRun", k, 0) + fs(r, "lostNight", k, 0)), S(lambda r: fs(r, "lostRun", k, 1) + fs(r, "lostNight", k, 1))
        lrun = S(lambda r: fs(r, "lostRun", k, 0))
        fn, fr = S(lambda r: es(r, "refetched", k, 0)), S(lambda r: es(r, "refetched", k, 1))
        jn, jr = S(lambda r: es(r, "rejoined", k, 0)), S(lambda r: es(r, "rejoined", k, 1))
        dn = S(lambda r: fs(r, "died", k, 0)); un = S(lambda r: fs(r, "culled", k, 0))
        ex = (wn + kn + on_) / yd
        o[k] = {"spk": q(sn, wn), "cau": q(cn, wn), "dR": (sr / sn - wr / wn) if sn and wn else None, "lostShare": q(lrun, ro),
                "Rlost": q(lr, ln), "Rfetch": q(fr, fn), "Rjoin": q(jr, jn), "Rwalk": q(wr, wn), "RFwalk": q(wf, wn),
                "exp": ex, "loss": q(ln, ex), "lossStock": q(ln, NN[k]), "death": q(dn, ex), "cull": q(un, ex),
                "keptOwn": q(kn, wn + kn + on_), "wn": wn, "wf": wf, "kn": kn, "wt": S(lambda r: dyo(r, "walk", k, 3))}
    o["RFwalkBoth"] = q(o[0]["wf"] + o[1]["wf"], o[0]["wn"] + o[1]["wn"])
    o["rateBoth"] = q(o[0]["wt"] + o[1]["wt"], o[0]["wn"] + o[1]["wn"])
    o["keptCap"] = q(o[0]["kn"], o[0]["kn"] + o[1]["kn"])
    o["capsYr"] = S(lambda r: fs(r, "cap", 0, 0)) / len(rs)
    fl = flow_tab.run_flow(d, a, b); o["csire"] = fl["csire"] if fl else None
    o["ratio"] = (o[0]["loss"] / o[1]["loss"]) if o[0]["loss"] is not None and o[1]["loss"] else None
    o["read3"] = o[0]["exp"] >= 20 and bool(o[1]["loss"])
    return o

def comparisons(d, rows):
    """Per row: stock mean R - histHerd's binned mean R (rows with a herd and a histogram row); the run's herder spooks per
    walking goat-day and the rule's rate, both origins."""
    hi = {y: i for i, y in enumerate(d.get("histYears") or [])}; gaps = []
    for r in rows:
        N = st(r, 0, 0) + st(r, 1, 0)
        if N and r["year"] in hi:
            h = split_tab.mc(d["histHerd"]["R"][hi[r["year"]]])
            if h is not None: gaps.append((st(r, 0, 1) + st(r, 1, 1)) / N - h)
    wn = sum(dyo(r, "walk", k, 0) for r in rows for k in (0, 1)); sp = sum(es(r, "spooked", k, 0) for r in rows for k in (0, 1))
    rt = sum(dyo(r, "walk", k, 3) for r in rows for k in (0, 1))
    return gaps, (sp / wn if wn else None), (rt / wn if wn else None)

def main():
    a = sys.argv[1:]; bad = None; per = "--perseed" in a; tl = None; testJ = None
    if "--testJ" in a: i = a.index("--testJ"); testJ = int(a[i + 1]); del a[i:i + 2]   # code-path test only
    alias, refJ, without = {}, [], []
    if "--without" in a: i = a.index("--without"); without = [int(x) for x in a[i + 1].split(",")]; del a[i:i + 2]
    if "--as" in a: i = a.index("--as"); alias = dict(x.split("=") for x in a[i + 1].split(",")); del a[i:i + 2]
    if "--refJ" in a: i = a.index("--refJ"); refJ = [x.split("=") for x in a[i + 1].split(";")]; del a[i:i + 2]
    if per: a.remove("--perseed")
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if "--timeline" in a:
        i = a.index("--timeline"); tl = 1
        if i + 1 < len(a) and a[i + 1].isdigit(): tl = int(a[i + 1]); del a[i + 1]
        del a[i]
    if a and a[0] == "selftest": selftest(bad); return
    selftest(None)
    dirs, arms = a[0], a[1].split(",")
    R = load_runs(dirs, arms); V, INFO = {}, {}
    f3 = lambda x: "-" if x is None else f"{x:.3f}"; f4 = lambda x: "-" if x is None else f"{x:+.4f}"; f2 = lambda x: "-" if x is None else f"{x:.2f}"
    f5 = lambda x: "-" if x is None else f"{x:.5f}"
    for farm in arms:
        arm = alias.get(farm, farm)
        for s, f in sorted(R.get(farm, {}).items()):
            d = json.load(open(f, encoding="utf-8")); check_rows(d, f"{arm} s{s}", bad)
            rows = d["years"]; last = rows[-1]["year"] + 1; J = jJ(d) if testJ is None else testJ; ph = phases(J, last)
            acc = account(rows, bad); acc1 = account(rows, bad, (1,)); gaps, spk, rate = comparisons(d, rows)
            INFO.setdefault(arm, {})[s] = {"J": J, "last": last, "ph": ph, "gaps": gaps, "spk": spk, "rate": rate}
            for p, (x, y) in ph.items():
                v = summ(d, rows, acc, x, y, acc1)
                if v: V.setdefault(arm, {}).setdefault(p, {})[s] = v
            if tl:
                hi = {y: i for i, y in enumerate(d.get("histYears") or [])}
                print(f"\nTimeline {arm} s{s} (J {J or '-'}; phases {ph}; {tl}-year lines; o0 captured, o1 herd-born): year | herd | R o0 / o1 / all | "
                      "histHerd R | capt share | load | herders | spook rate o0 / o1 | spooks per walk-day (both) / rate (both) | R x fear o0 / o1 | "
                      "walk / kept / other o0 | walk / kept / other o1 | wild R (trait means) / (histogram)")
                for y0 in range(401, last + 1, tl):
                    rs = [r for r in rows if y0 <= r["year"] + 1 < y0 + tl]
                    n = [sum(st(r, k, 0) for r in rs) / len(rs) for k in (0, 1)]; sr = [sum(st(r, k, 1) for r in rs) / len(rs) for k in (0, 1)]
                    days = sum(dy(r, "days") for r in rs)
                    w = [[sum(dyo(r, "walk", k, i) for r in rs) for i in range(4)] for k in (0, 1)]
                    ke = [sum(dyo(r, "kept", k, 0) for r in rs) for k in (0, 1)]; ot = [sum(dyo(r, "other", k) for r in rs) for k in (0, 1)]
                    sh = lambda k: " / ".join(f2(x / (w[k][0] + ke[k] + ot[k])) if w[k][0] + ke[k] + ot[k] else "-" for x in (w[k][0], ke[k], ot[k]))
                    wr = [x for x in (wildR(r) for r in rs) if x is not None]
                    hh = [split_tab.mc(d["histHerd"]["R"][hi[r["year"]]]) for r in rs if r["year"] in hi]; hh = [x for x in hh if x is not None]
                    wh = [split_tab.mc([x - y for x, y in zip(d["hist"]["R"][hi[r["year"]]], d["histHerd"]["R"][hi[r["year"]]])]) for r in rs if r["year"] in hi]
                    wh = [x for x in wh if x is not None]
                    wb = w[0][0] + w[1][0]; spb = sum(es(r, "spooked", k, 0) for r in rs for k in (0, 1))
                    print(f"  {y0}{'' if tl == 1 else '-' + str(y0 + tl - 1)} | {sum(n):.1f} | " + " / ".join(f3(sr[k] / n[k] if n[k] else None) for k in (0, 1))
                          + f" / {f3(sum(sr) / sum(n) if sum(n) else None)} | {f3(sum(hh) / len(hh) if hh else None)} | {f2(n[0] / sum(n) if sum(n) else None)} | "
                          f"{f3(sum(dy(r, 'load') for r in rs) / days if days else None)} | {f2(sum(dy(r, 'herders') for r in rs) / days if days else None)} | "
                          + " / ".join(f5(w[k][3] / w[k][0] if w[k][0] else None) for k in (0, 1))
                          + f" | {f5(spb / wb if wb else None)} / {f5((w[0][3] + w[1][3]) / wb if wb else None)} | "
                          + " / ".join(f3(w[k][2] / w[k][0] if w[k][0] else None) for k in (0, 1)) + f" | {sh(0)} | {sh(1)} | {f3(sum(wr) / len(wr) if wr else None)} / {f3(sum(wh) / len(wh) if wh else None)}")
    cell = lambda xs, f=f3: (lambda xs: f"{f(sum(xs) / len(xs))} ({f(min(xs))} to {f(max(xs))})" if xs else "-")([x for x in xs if x is not None])
    if testJ is not None: print(f"\n*** --testJ {testJ}: every run's J is set to {testJ}, not computed. A code-path test only; nothing here is a reading. ***")
    print(f"\nexp020 ledger: checks passed on {sum(len(v) for v in INFO.values())} runs (stock = herded and = herdTraitMeans R every row; load against"
          f" the rule; every split year closes to {TOL_Y}; every phase to {TOL_P}). Pooled over camps; o0 captured itself, o1 herd-born.")
    RJ = {}
    for dr, ra in refJ:   # J computed the same way from another batch's runs of an arm
        for s, f in sorted(load_runs(dr, [ra]).get(ra, {}).items()): RJ.setdefault(ra, {})[s] = (jJ(json.load(open(f, encoding="utf-8"))), dr)
    for arm in [alias.get(x, x) for x in arms]:
        if arm not in INFO: continue
        I = INFO[arm]; noJ = [s for s, v in I.items() if v["J"] is None]
        print(f"\n{arm}: J per seed " + ", ".join(f"s{s} {v['J'] or '-'}" for s, v in sorted(I.items())) + (f"; no J (A runs to the end): {['s%d' % s for s in noJ]}" if noJ else ""))
        if arm in RJ:
            df = [s for s in I if s in RJ[arm] and RJ[arm][s][0] != I[s]["J"]]
            print(f"  beside {arm}'s J in {sorted({v[1] for v in RJ[arm].values()})}: " + ", ".join(f"s{s} {I[s]['J'] or '-'} / {RJ[arm][s][0] or '-'}" for s in sorted(I) if s in RJ[arm])
                  + (f"; differ in {['s%d' % s for s in df]} (reported, not fixed)" if df else "; equal in every seed"))
        print("  comparisons per run (amendment point 5): stock mean R - histHerd binned mean R, mean (widest) over rows with a herd; herder spooks per walking goat-day / the rule's rate, whole run: "
              + "; ".join(f"s{s} {f4(sum(v['gaps']) / len(v['gaps']) if v['gaps'] else None)} ({f4(max(v['gaps'], key=abs) if v['gaps'] else None)}), {f5(v['spk'])} / {f5(v['rate'])}" for s, v in sorted(I.items())))
        print("| phase | seeds | years | herd | herd per camp-day | load | herders | captured share | captures/yr | csire | captured share of kept | walking R x fear |\n|" + "---|" * 12)
        for p in PH:
            vs = list(V.get(arm, {}).get(p, {}).values())
            if vs: print(f"| {p} | {len(vs)} | {cell([v['years'] for v in vs], f2)} | {cell([v['herd'] for v in vs], f2)} | {cell([v['campHerd'] for v in vs], f2)} | {cell([v['load'] for v in vs])} | {cell([v['herders'] for v in vs], f2)} | "
                         f"{cell([v['captShare'] for v in vs])} | {cell([v['capsYr'] for v in vs], f2)} | {cell([v['csire'] for v in vs])} | {cell([v['keptCap'] for v in vs])} | {cell([v['RFwalkBoth'] for v in vs])} |")
        print(f"\n{arm} R accounting, summed over each phase, by origin (mean over seeds (min to max)); change = channels (both) + restart")
        print("| phase | origin | change | " + " | ".join(FCH) + " | restart |\n|---|---|---|" + "---|" * (len(FCH) + 1))
        for p in PH:
            vs = [v["acc"] for v in V.get(arm, {}).get(p, {}).values() if "change" in v["acc"]]
            if not vs: continue
            for oi, on in ((0, "o0"), (1, "o1"), (None, "both")):
                g = (lambda v, k: v[k][oi]) if oi is not None else (lambda v, k: sum(v[k]))
                print(f"| {p} | {on} | {cell([v['change'] for v in vs], f4) if oi is None else ''} | " + " | ".join(cell([g(v, k) for v in vs], f4) for k in FCH)
                      + f" | {cell([v['restart'] for v in vs], f4) if oi is None else ''} |")
        print(f"\n{arm} herd-born stock alone (its own mean and N; amendment 2), summed over each phase; change = channels + restart")
        print("| phase | change | " + " | ".join(FCH) + " | restart |\n|---|---|" + "---|" * (len(FCH) + 1))
        for p in PH:
            vs = [v["acc1"] for v in V.get(arm, {}).get(p, {}).values() if v["acc1"] and "change" in v["acc1"]]
            if vs: print(f"| {p} | {cell([v['change'] for v in vs], f4)} | " + " | ".join(cell([v[k][1] for v in vs], f4) for k in FCH) + f" | {cell([v['restart'] for v in vs], f4)} |")
        print(f"\n{arm} spook filter and captives, per phase and origin (exposure = midday goat-days / yearDays)")
        cols = (("spk", f3), ("cau", f3), ("dR", f4), ("lostShare", f3), ("Rlost", f3), ("Rfetch", f3), ("Rjoin", f3), ("Rwalk", f3), ("RFwalk", f3),
                ("exp", f2), ("loss", f3), ("lossStock", f3), ("death", f3), ("cull", f3), ("keptOwn", f3))
        print("| phase | origin | spooks/walk-day | caught/walk-day | R spooked - R walking | lost/ran off | R lost | R fetched | R came back | R walking | "
              "R x fear walking | exposure goat-yr | lost/exposure goat-yr | lost/stock goat-yr | deaths/exposure | culled/exposure | share of own goat-days kept |\n|" + "---|" * 17)
        for p in PH:
            vs = list(V.get(arm, {}).get(p, {}).values())
            for k in (0, 1):
                if vs: print(f"| {p} | o{k} | " + " | ".join(cell([v[k][m] for v in vs], f) for m, f in cols) + " |")
            if vs: print(f"| {p} | o0/o1 | lost/exposure ratio {cell([v['ratio'] for v in vs])} |" + " |" * 15)
    if per:
        print("\nPer seed: phase (labels) years herd load herders | change; channels both (o0 / o1) | lost/exposure o0 o1 ratio (read for P3) | walking R x fear | csire")
        for arm in [alias.get(x, x) for x in arms]:
            for s in sorted(INFO.get(arm, {})):
                for p, (x, y) in INFO[arm][s]["ph"].items():
                    v = V.get(arm, {}).get(p, {}).get(s)
                    if not v: continue
                    ac = v["acc"]
                    print(f"  {arm} s{s} {p} ({x}-{y}): {v['years']} y, herd {v['herd']:.1f}, load {f3(v['load'])}, herders {f2(v['herders'])} | change {f4(ac.get('change'))}; "
                          + ", ".join(f"{k} {f4(sum(ac[k]))} ({f4(ac[k][0])} / {f4(ac[k][1])})" for k in FCH) + f", restart {f4(ac['restart'])}"
                          + f" | {f3(v[0]['loss'])} {f3(v[1]['loss'])} {f3(v['ratio'])} ({'read' if v['read3'] else 'not read'}) | {f3(v['RFwalkBoth'])} | {f3(v['csire'])}"
                          + (f" | herd-born alone: change {f4(v['acc1'].get('change'))}; " + ", ".join(f"{k} {f4(v['acc1'][k][1])}" for k in P2B) + f", restart {f4(v['acc1']['restart'])}" if v["acc1"] else ""))
    print("\nPredictions (exp020 as amended, c91c20b and ffa8a83)")
    B, LB = V.get("REF", {}).get("B", {}), V.get("LOAD05", {}).get("B", {})
    noB = [s for s in INFO.get("LOAD05", {}) if s not in LB]
    for tag, key, below, what in (("1a", "RFwalkBoth", True, "walking R x fear (walk[2]/walk[0]) below"), ("1b", "rateBoth", False, "rule rate per walking goat-day (walk[3]/walk[0]) above")):
        lv = [v[key] for v in LB.values() if v[key] is not None]
        if not (B and lv): print(f"{tag}. REF or LOAD05 has no phase B: not read"); continue
        med = statistics.median(lv); ok = lambda x: x is not None and (x < med if below else x > med)
        k = sum(1 for v in B.values() if ok(v[key])); nb = [s for s, v in sorted(B.items()) if v[key] is None]
        print(f"{tag}. REF over B, {what} LOAD05's phase-B median {f5(med)} (over {len(lv)} LOAD05 seeds with a B"
              + (f"; without one: {['s%d' % s for s in noB]}" if noB else "") + "; LOAD05 per seed " + ", ".join(f"s{s} {f5(v[key])}" for s, v in sorted(LB.items()))
              + f"): {k} of {len(B)} REF seeds with a B (" + ", ".join(f"s{s} {f5(v[key])}" for s, v in sorted(B.items())) + ")"
              + (f"; no walking goat-day in B, not read: {['s%d' % s for s in nb]}" if nb else "") + ": "
              + ("holds" if k >= 6 else "fails" if len(B) >= 6 else "not read (under 6 REF seeds with a B)"))
    if B or LB:
        print("   beside 1a/1b, over B: walking R (walk[1]/walk[0]) o0 / o1 and the share of each origin's goat-days kept o0 / o1: "
              + "; ".join(f"{arm} s{s} {f3(v[0]['Rwalk'])} / {f3(v[1]['Rwalk'])}, kept {f3(v[0]['keptOwn'])} / {f3(v[1]['keptOwn'])}" for arm, X in (("REF", B), ("LOAD05", LB)) for s, v in sorted(X.items())))
    if B:
        k = sum(1 for v in B.values() if v["load"] is not None and v["load"] > 2)
        print(f"   descriptive (follows from herdN = 1: load above 2 is a camp herd above 40): REF load over B above 2 in {k} of {len(B)} ("
              + ", ".join(f"s{s} {f3(v['load'])}" for s, v in sorted(B.items())) + ")")
    if "REF" in INFO:
        sj = [s for s, v in sorted(INFO["REF"].items()) if v["J"] is not None]
        for tag, chans, oi in (("2a", P2A, None), ("2b", P2B, 1)):
            win, lines, wins = 0, [], {}
            for s in sj:
                src = "acc" if oi is None else "acc1"   # (b): the herd-born stock's own split (amendment 2)
                g = lambda p, k: (lambda t: (sum(t[k]) if oi is None else t[k][oi]) if t else 0.0)(V["REF"].get(p, {}).get(s, {}).get(src))
                tot = {k: sum(g(p, k) for p in ("A", "T", "B")) for k in chans}
                m = min(chans, key=lambda k: tot[k]); win += m == "lost"; wins[s] = m == "lost"
                pp = "; ".join(f"{p} {min(chans, key=lambda k: g(p, k))}" for p in ("A", "T", "B") if V["REF"].get(p, {}).get(s))
                lines.append(f"s{s} {m} {f4(tot[m])} (lost {f4(tot['lost'])}; per phase most negative: {pp})")
            what = "lost (both origins) the most negative channel of the pooled mean" if oi is None else "herd-born lost the most negative channel of the herd-born stock's own mean"
            print(f"{tag}. REF over A+T+B, {what}: {win} of {len(sj)} seeds with a J ({'; '.join(lines)})"
                  + (f"; no J: {[s for s in INFO['REF'] if s not in sj]}" if len(sj) < len(INFO["REF"]) else "") + ": "
                  + ("holds" if win >= 6 else "fails" if len(sj) >= 6 else "not read (under 6 seeds with a J)"))
            for x in without:   # the verdict without a seed seen before results (the reviewer's a94d79d: REF s6, the J probe)
                ws = [s for s in sj if s != x]; k = sum(1 for s in ws if wins[s])
                v0 = "holds" if win >= 6 else "fails" if len(sj) >= 6 else None
                v1 = "holds" if k >= 6 else "fails" if len(ws) >= 6 else None
                print(f"   {tag} without s{x} (seen before results; descriptive): {k} of {len(ws)} seeds with a J; "
                      + (v1 or "not read (under 6 seeds with a J)")
                      + (f" (the verdict above {'does not depend' if v0 == v1 else 'depends'} on s{x})" if v0 and v1 else " (no comparison: a verdict is not read)"))
    if B or LB:
        rr = {s: v for s, v in B.items() if v["read3"]}; lr = {s: v for s, v in LB.items() if v["read3"]}
        nr = lambda X: [s for s, v in X.items() if not v["read3"]]
        desc = (f"REF read {sorted(rr)} (not read {nr(B)}), LOAD05 read {sorted(lr)} (not read {nr(LB)}); per seed captured vs herd-born lost/exposure goat-yr (ratio; captured exposure goat-yr; kept: share of captured goat-days, captured share of kept): "
                + "; ".join(f"{arm} s{s} {f3(v[0]['loss'])} vs {f3(v[1]['loss'])} ({f3(v['ratio'])}; {f2(v[0]['exp'])}; {f3(v[0]['keptOwn'])}, {f3(v['keptCap'])}; stock rates {f3(v[0]['lossStock'])} vs {f3(v[1]['lossStock'])})"
                            for arm, X in (("REF", B), ("LOAD05", LB)) for s, v in sorted(X.items())))
        if len(rr) >= 6 and len(lr) >= 6:
            every = all(v[0]["loss"] > v[1]["loss"] for v in rr.values()); med = statistics.median(v["ratio"] for v in lr.values())
            k = sum(1 for v in rr.values() if v["ratio"] > med)
            print(f"3. REF over B: captured above herd-born in every read seed: {'yes' if every else 'no'}; ratio above LOAD05's read median {f3(med)} in {k} of {len(INFO.get('REF', {}))} REF seeds ({len(B)} with a B): "
                  + ("holds" if every and k >= 6 else "fails") + f". {desc}")
        else: print(f"3. not read (6 or more read seeds needed in each arm). {desc}")
    else: print("3. no phase B in REF or LOAD05: not read")

if __name__ == "__main__": main()
