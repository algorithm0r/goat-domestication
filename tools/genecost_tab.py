# genecost_tab.py: the scorer for exp012 (the genome's cost on conception), from its pre-registration (5a2948f) and
# amendments 1 (e53d80f, the reviewer's 12e1e47) and 2 (the reviewer's 2caaf62) in EXPLOG. Analysis session, 2026-11-20.
#   python tools/genecost_tab.py EXP012_DIR "BASE_DIR[;BASE_DIR...]" [--alias ARM=SRC,...] [--window 3201-4000]
#          [--perseed] [--bad KIND]
#   python tools/genecost_tab.py selftest [bad]
# EXP012_DIR holds REF25, REF50, DEEP25, DEEP50, RAND50, DEEPFLAT50 (<ARM>_seed<S>.json). BASE_DIR(s) hold the cost-0
# arms: REF (exp005 seeds 1-4 + exp006 seeds 5-8), CTLDEEP and CTLRAND (exp007, seeds 1-8). --alias maps an exp012 arm to
# another arm's files in EXP012_DIR, only to test the scorer before exp012 exists: an aliased table is a test, never a
# result, and the parameter guard is then printed, not enforced.
# Parameter guard: every exp012 run's parameters must equal its cost-0 counterpart's (same seed) except id,
# reproCostFertility (= the arm's dose) and, for DEEPFLAT50, matingConception 0.356; keys the cost-0 run lacks (code
# added since) are allowed and listed; a key the exp012 run lacks, or any other difference, stops the tool.
# Definitions (registration and amendments; the standing measures of notes/batch1-plan.md):
#   p = mean of the eight core genotypes R A S B H T M W (the cost's p: src/animals.js, NT_CORE = 8; L and C left out).
#   mean core gap = herd p - wild p = the mean over the eight of settle_tab.gaps (row-mean of herd - wild genotype means).
#   wild p, wild T: the wild genotype means (hist - histHerd, every window row), all seeds.
#   selection differential on p: kids-weighted over the window's year rows, the mean over the eight of selDam (dams)
#     and of selSire (sires); the reading quantity is their average (the mid-parent differential), both printed.
#   established = the herd-size criterion of tools/jump_tab.py (as culture_tab); an arm is read with 2 or more
#     established seeds; at 0.5 an arm with fewer is read at 0.25 (DEEP50 -> DEEP25, REF50 -> REF25; RAND50 has none).
#   changes from cost 0 are paired by seed: mean core gap, per-trait gaps and the selection differential over seeds
#     established in both arms; wild p and wild T over every seed both have; 95% t intervals (inflow_tab.tcrit).
#   breadth = core traits (R A S B H T M W L) with abs(arm-mean gap) >= 0.10; below / above = core traits with the
#     herd 0.10 or more below / above the wild (the first registration's counts; still reported).
#   split: split_tab (founders 301-400, identity checked): herd change and wild change, per trait and for p.
#   demographic match (amendment 2): DEEP50 vs DEEPFLAT50 by seed on herd births per doe-year (sum herdBirths / sum of
#     herded x the breeding-doe share of herdComp), mean age at first kidding (firstKidStats a / n, herd and wild),
#     herd size and wild size (goats - herded); "beyond noise" = the paired 95% interval excludes 0.
# Checks: the cost-0 values the amendment quotes (mean core gap CTLDEEP -0.049, CTLRAND -0.006, REF -0.087; CTLDEEP's
# all-goat p 0.574) are recomputed and must match to the third decimal; the wild means over herd rows must equal
# split's F + wild change (1e-9). --bad core9 (L put into p), wild (wild taken as all goats), guard (an aliased arm's
# guard enforced) must each stop or show a mismatch.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, jump_tab, flow_tab, inflow_tab
gaps, herd, CORE, TRAITS = split_tab.gaps, split_tab.herd, split_tab.CORE, split_tab.TRAITS
CORE8 = "R A S B H T M W".split()
ARMS = {"REF25": ("REF", 0.25, {}), "REF50": ("REF", 0.5, {}), "DEEP25": ("CTLDEEP", 0.25, {}),
        "DEEP50": ("CTLDEEP", 0.5, {}), "RAND50": ("CTLRAND", 0.5, {}),
        "DEEPFLAT50": ("CTLDEEP", 0.0, {"matingConception": 0.356})}
BASES = ["REF", "CTLDEEP", "CTLRAND"]
FALLBACK = {"DEEP50": "DEEP25", "REF50": "REF25"}
PAIRS = [("DEEP50", "CTLDEEP"), ("DEEP25", "CTLDEEP"), ("RAND50", "CTLRAND"), ("DEEP50", "DEEPFLAT50"),
         ("DEEPFLAT50", "CTLDEEP"), ("REF50", "REF"), ("REF25", "REF")]
QUOTED = {"CTLDEEP": -0.049, "CTLRAND": -0.006, "REF": -0.087}   # amendment e53d80f, mean core gap at cost 0
QUOTED_ALLP = ("CTLDEEP", 0.574)
FLOW = ["capt", "csire", "depth", "feral"]
# switches that change only what is logged (params.js: logHistDepth = the lineage-depth histograms); allowed to differ
OUTPUT_ONLY = {"logHistDepth"}

class GuardFail(Exception): pass

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def ci(xs):   # (mean, lo, hi, n): 95% t interval; lo = hi = None with fewer than 2 values
    xs = [x for x in xs if x is not None]; m, se = ms(xs)
    if m is None: return None, None, None, 0
    if len(xs) < 2: return m, None, None, len(xs)
    t = inflow_tab.tcrit(len(xs)); return m, m - t * se, m + t * se, len(xs)

def guard(P, B, dose, extra):
    """Differences between an exp012 run's parameters P and its cost-0 counterpart's B. Returns the keys P adds;
    raises GuardFail on anything not allowed."""
    eq = lambda a, b: a == b or (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= 1e-9)
    bad = []
    if not eq(P.get("reproCostFertility"), dose): bad.append(f"reproCostFertility {P.get('reproCostFertility')} (want {dose})")
    if not eq(P.get("reproCostGrowth"), 0): bad.append(f"reproCostGrowth {P.get('reproCostGrowth')} (want 0)")
    for k, v in extra.items():
        if not eq(P.get(k), v): bad.append(f"{k} {P.get(k)} (want {v})")
    skip = {"id", "reproCostFertility"} | set(extra)
    out = []
    for k in B:
        if k in skip: continue
        if k not in P: bad.append(f"{k} missing (cost 0: {B[k]})")
        elif not eq(P[k], B[k]):
            if k in OUTPUT_ONLY: out.append(f"{k} {B[k]}->{P[k]} (output only)")
            else: bad.append(f"{k} {P[k]} (cost 0: {B[k]})")
    if bad: raise GuardFail(", ".join(bad))
    return sorted(k for k in P if k not in B and k not in skip) + out

def mc(c):
    n = sum(c); return None if n == 0 else sum((k + 0.5) / 20 * v for k, v in enumerate(c)) / n

def wild_means(d, y0, y1, herd_rows=False, bad=None):
    """Window mean of the wild genotype mean per trait (hist - histHerd), over every row with wild goats, or (herd_rows)
    over the rows split_tab uses (herd and wild goats both)."""
    out = {}
    for t in TRAITS:
        v = []
        for i, y in enumerate(d["histYears"]):
            if not y0 <= y + 1 <= y1: continue
            a, h = d["hist"][t][i], d["histHerd"][t][i]
            w = a if bad == "wild" else [x - z for x, z in zip(a, h)]
            if sum(w) and (sum(h) or not herd_rows): v.append(mc(w))
        out[t] = sum(v) / len(v) if v else None
    return out

def all_p(d, y0, y1):   # all-goat mean core p (hist), window row mean
    v = [sum(mc(d["hist"][t][i]) for t in CORE8) / 8 for i, y in enumerate(d["histYears"]) if y0 <= y + 1 <= y1 and sum(d["hist"]["R"][i])]
    return sum(v) / len(v) if v else None

def wsel(rows, key, k):   # kids-weighted window mean of a selection differential, per trait (selN[1] sires, [0] dams)
    num = {t: 0.0 for t in TRAITS}; den = 0
    for r in rows:
        if r.get(key) and r.get("selN") and r["selN"][k]:
            for t in TRAITS: num[t] += r[key][t] * r["selN"][k]
            den += r["selN"][k]
    return {t: num[t] / den for t in TRAITS} if den else None

def score(f, y0, y1, bad=None):
    d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    core = CORE8 + (["L"] if bad == "core9" else [])
    g = gaps(d, y0, y1); h = herd(d, y0, y1)
    sp = split_tab.split(d, y0, y1, 301, 400)
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    J, end, _, late = jump_tab.jump(hs, lambda v: v >= 100, 400)
    wm = wild_means(d, y0, y1, False, bad)
    if sp:   # identity: wild means over split's rows = F + wild change
        wh = wild_means(d, y0, y1, True, bad)
        miss = [t for t in TRAITS if abs(wh[t] - (sp[1][t] + sp[0][t][1])) > 1e-9]
        if miss: sys.exit(f"{os.path.basename(f)}: wild mean over herd rows != F + wild change for {' '.join(miss)} (split identity)")
    dam, sire = wsel(rows, "selDam", 0), wsel(rows, "selSire", 1)
    pd = sum(dam[t] for t in core) / len(core) if dam else None
    psr = sum(sire[t] for t in core) / len(core) if sire else None
    does = sum((r.get("herded") or 0) * r["herdComp"][1] / sum(r["herdComp"]) for r in rows if r.get("herdComp") and sum(r["herdComp"]))
    fk = {}
    for p in ("herd", "wild"):
        st = [(r.get("firstKidStats") or {}).get(p) for r in rows]; st = [s for s in st if s and s.get("n")]
        n = sum(s["n"] for s in st); fk[p] = sum(s["a"] for s in st) / n / (P.get("yearDays") or 360) if n and all("a" in s for s in st) else None
    fl = flow_tab.run_flow(d, y0, y1) or {}
    run = {"P": P, "gap": g, "herd": h, "J": J, "end": end, "late": late, "est": J is not None and g is not None,
           "pgap": sum(g[t] for t in core) / len(core) if g else None,
           "wild": wm, "wp": sum(wm[t] for t in core) / len(core) if all(wm[t] is not None for t in core) else None,
           "wT": wm["T"], "allp": all_p(d, y0, y1), "selD": pd, "selS": psr,
           "selp": (pd + psr) / 2 if pd is not None and psr is not None else None,
           "hc": {t: v[0] for t, v in sp[0].items()} if sp else None, "wc": {t: v[1] for t, v in sp[0].items()} if sp else None,
           "bpd": sum(r.get("herdBirths") or 0 for r in rows) / does if does else None,
           "fkh": fk["herd"], "fkw": fk["wild"], "wsize": sum((r.get("goats") or 0) - (r.get("herded") or 0) for r in rows) / len(rows) if rows else None,
           "flow": fl}
    if sp:
        run["hcp"] = sum(run["hc"][t] for t in core) / len(core); run["wcp"] = sum(run["wc"][t] for t in core) / len(core)
    else: run["hcp"] = run["wcp"] = None
    return run

def summary(runs):
    E = [r for r in runs if r["est"]]
    v = {"n": len(runs), "nE": len(E), "E": E, "runs": runs, "read": len(E) >= 2, "late": sum(1 for r in runs if r["late"]),
         "win100": sum(1 for r in runs if r["herd"] >= 100), "fell": [r for r in E if r["herd"] < 100],
         "herd": ms([r["herd"] for r in runs])[0], "Jmed": sorted(r["J"] for r in E)[len(E) // 2] if E else None}
    v["km"] = jump_tab.km([(r["J"], r["end"]) for r in runs], max(r["end"] for r in runs))
    v["gap"] = {t: ms([r["gap"][t] for r in E]) for t in TRAITS} if E else None
    for k in ("pgap", "selp", "selD", "selS", "hcp", "wcp"): v[k] = ms([r[k] for r in E])
    for k in ("wp", "wT", "allp", "wsize"): v[k] = ms([r[k] for r in runs])
    v["flow"] = {k: ms([r["flow"].get(k) for r in E]) for k in FLOW}
    if E:
        g0 = {t: v["gap"][t][0] for t in CORE}
        v["breadth"] = sum(1 for t in CORE if abs(g0[t]) >= 0.10)
        v["below"] = [t for t in CORE if g0[t] <= -0.10]; v["above"] = [t for t in CORE if g0[t] >= 0.10]
    else: v["breadth"], v["below"], v["above"] = None, [], []
    return v

def paired(seeds, A, B, get, est=True):
    if A not in seeds or B not in seeds: return None, None, None, 0
    xs = [get(seeds[A][s]) - get(seeds[B][s]) for s in seeds[A] if s in seeds[B]
          and (not est or (seeds[A][s]["est"] and seeds[B][s]["est"])) and get(seeds[A][s]) is not None and get(seeds[B][s]) is not None]
    return ci(xs)

def read(S, C):
    """Predictions and decision rule. S = arm summaries; C = {(A, B, measure): (mean, lo, hi, n)} paired changes.
    Returns (lines, verdicts). A verdict is True / False, or None where it cannot be read."""
    L, V = [], {}
    f = lambda x: "-" if x is None else f"{x:+.3f}"
    iv = lambda c: "not read" if c is None or c[0] is None else (f"{f(c[0])} [{f(c[1])}, {f(c[2])}], n {c[3]}" if c[1] is not None else f"{f(c[0])} (n {c[3]}, no interval)")
    rd = lambda a: a in S and S[a]["read"]
    below = lambda c: None if c is None or c[1] is None else c[2] < 0
    above = lambda c: None if c is None or c[1] is None else c[1] > 0
    incl = lambda c: None if c is None or c[1] is None else c[1] <= 0 <= c[2]
    use = {}
    for a in ("DEEP50", "REF50", "RAND50"):
        use[a] = a if rd(a) else (FALLBACK.get(a) if rd(FALLBACK.get(a, "")) else None)
    V["fallback"] = [f"{a} -> {use[a]}" for a in use if use[a] and use[a] != a] + [f"{a}: not read (no 0.25 arm or it fails too)" for a in use if not use[a]]
    # 1. wild p lower at 0.5 than at cost 0 (every 0.5 arm read); T separately, predicted to rise
    w1 = {}
    L.append("1. wild mean core p lower at cost 0.5 than at cost 0, interval excluding 0 (all seeds, paired); T to rise:")
    for a, b in (("REF50", "REF"), ("DEEP50", "CTLDEEP"), ("RAND50", "CTLRAND")):
        cp, cT = C.get((a, b, "wp")), C.get((a, b, "wT"))
        w1[a] = (below(cp), above(cT))
        L.append(f"   {a} - {b}: wild p {iv(cp)}: {'-' if w1[a][0] is None else 'lower' if w1[a][0] else 'not lower'}; "
                 f"wild T {iv(cT)}: {'-' if w1[a][1] is None else 'rises' if w1[a][1] else 'does not rise'}")
    rp = [x[0] for x in w1.values() if x[0] is not None]; rT = [x[1] for x in w1.values() if x[1] is not None]
    V["p1"] = all(rp) if rp else None; V["p1T"] = all(rT) if rT else None
    L.append(f"   prediction 1 (wild p, every 0.5 arm with data): {V['p1']}; T rises in every 0.5 arm: {V['p1T']}")
    def one(key, a, b, test, text):
        if use.get(a) is None: V[key] = None; L.append(f"{text}: not read ({a} not established, no fallback)"); return
        aa = use.get(a, a); c = C.get((aa, b, "pgap"))
        V[key] = test(c) if rd(b) else None
        L.append(f"{text}: {V[key]} ({aa} - {b}, mean core gap {iv(c)})")
    one("p2", "DEEP50", "CTLDEEP", below, "2. DEEP50 - CTLDEEP below 0, interval excluding 0")
    one("p3", "RAND50", "CTLRAND", incl, "3. RAND50 - CTLRAND interval including 0")
    V["p4"] = all(a in S and S[a]["nE"] >= 6 for a in ("REF25", "DEEP25"))
    L.append(f"4. established in >= 6 of 8 at 0.25 in every arm: {V['p4']} ("
             + ", ".join(f"{a} {S[a]['nE'] if a in S else '-'}" for a in ("REF25", "DEEP25")) + ")")
    if use.get("DEEP50") != "DEEP50":   # amendment 2: no flat arm at 0.25
        V["p5"] = None; L.append("5. DEEP50 - DEEPFLAT50: not read (DEEP read at 0.25 or not at all; no flat arm at 0.25)")
    else:
        c = C.get(("DEEP50", "DEEPFLAT50", "pgap")); V["p5"] = below(c) if rd("DEEPFLAT50") else None
        L.append(f"5. DEEP50 - DEEPFLAT50 below 0, interval excluding 0: {V['p5']} (mean core gap {iv(c)})"
                 + (" -- carries part of the demographic effect (DEEP50 and DEEPFLAT50 differ beyond noise on: "
                    + ", ".join(S["_demog"]) + ")" if S.get("_demog") else ""))
    if use.get("REF50") is None: V["p6"] = None; L.append("6. REF50 - REF: not read")
    else:
        a6 = use["REF50"]; c = C.get((a6, "REF", "pgap")); c25 = C.get(("REF25", "REF", "pgap"))
        btw = None
        if a6 == "REF50" and c and c25 and c[0] is not None and c25[0] is not None: btw = min(0, c[0]) < c25[0] < max(0, c[0])
        # the reviewer (20eb50f, point 2): a missing REF25 pair leaves 'between' unread, so prediction 6 reads None
        b6 = below(c)
        V["p6"] = None if b6 is None else False if not b6 else True if a6 != "REF50" else btw
        L.append(f"6. REF50 - REF below 0, interval excluding 0, REF25 between REF and REF50: {V['p6']} ({a6} - REF {iv(c)}"
                 + (f"; REF25 - REF {iv(c25)}; between: {btw})" if a6 == "REF50" else "; read at 0.25, 'between' does not apply)"))
    if use.get("DEEP50") is None: V["p7"] = None; L.append("7. selection on p: not read")
    else:
        aa = use["DEEP50"]; c = C.get((aa, "CTLDEEP", "selp")); V["p7"] = below(c)
        L.append(f"7. selection differential on p more negative in {aa} than CTLDEEP (paired, interval below 0): {V['p7']} "
                 f"({iv(c)}; point reading {'-' if not c or c[0] is None else c[0] < 0})")
    p2, p3, p5, p7 = V["p2"], V["p3"], V["p5"], V["p7"]
    fired = []
    if p2 is True and p3 is True and p5 is True:
        fired.append("A: 2, 3 and 5 hold: the cost gives directional change toward lower trait values through selection in a"
                     " closed herd and not in an open one: the grain model's mechanism in goats. To Chris for the re-plan."
                     # the reviewer (20eb50f, point 1): A does not test 7; a label, not a change to the rule
                     + ("" if p7 is True else f" [prediction 7 {'fails' if p7 is False else 'not read'}: the selective"
                        " reading rests on DEEP50 - DEEPFLAT50 alone]"))
    if p2 is True and p5 is False: fired.append("B: 2 holds and 5 fails: the change is the cost's demographic effect, not its gradient.")
    if p2 is False and p7 is False:
        fired.append("C: 2 fails and 7 fails: the cost does not select here (possibly diluted by retries, a doe retrying each"
                     " cycle: a candidate cause, untested, no counter; the reviewer 20eb50f point 3); the null says nothing"
                     " about the mechanism.")
    if p2 is False and p7 is True: fired.append("D: 2 fails and 7 holds: selection on p is present but swamped in the herd.")
    if p2 is True and p3 is False: fired.append("E: 2 holds and 3 fails (RAND50 also below 0): the change is not specific to closed herds.")
    if V["fallback"]: fired.append("F: herds fail to establish at 0.5 in an arm: read at 0.25 (" + "; ".join(V["fallback"]) + ")")
    V["branches"] = [x[0] for x in fired]
    L.append("\nDecision rule (amendment e53d80f), branches that fire:")
    L += [f"- {x}" for x in fired] or ["- none fires (" + ", ".join(f"{k} {V[k]}" for k in ("p2", "p3", "p5", "p7")) + ")"]
    return L, V

def files(folders):
    R = {}
    for folder in folders:
        for fn in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(fn))
            if m:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {fn}")
                R[m.group(1)][int(m.group(2))] = fn
    return R

def main():
    a = sys.argv[1:]; alias = {}; y0, y1 = 3201, 4000
    def opt(k):
        if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    if (v := opt("--alias")): alias = dict(x.split("=") for x in v.split(","))
    if (v := opt("--window")): y0, y1 = (int(x) for x in v.split("-"))
    bad = opt("--bad"); perseed = "--perseed" in a; a = [x for x in a if x != "--perseed"]
    if "exp010" in a[0] or "exp011" in a[0]: sys.exit("EXP012_DIR must be exp012's folder (or exp009's, for stand-ins)")
    X, Bf = files([a[0]]), files(a[1].split(";"))
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not exp012 results; the parameter guard is printed, not enforced ***")
    if bad: print(f"*** TEST ONLY: --bad {bad} ***")
    RS, seeds = {}, {}
    for b in BASES:
        if b not in Bf: sys.exit(f"cost-0 arm {b} not found in {a[1]}")
        RS[b] = [dict(score(fn, y0, y1, bad), seed=s) for s, fn in sorted(Bf[b].items())]
    newkeys = set()
    for arm, (base, dose, extra) in ARMS.items():
        src = alias.get(arm, arm)
        if src not in X: print(f"{arm}: no runs ({src})"); continue
        rs = []
        for s, fn in sorted(X[src].items()):
            r = score(fn, y0, y1, bad); r["seed"] = s
            B = next((x["P"] for x in RS[base] if x["seed"] == s), None)
            if B is None:
                if arm in alias: print(f"  {arm} seed {s}: no cost-0 {base} seed, left out (aliased test only)"); continue
                sys.exit(f"{arm} seed {s}: no cost-0 {base} run with that seed")
            try: newkeys |= set(guard(r["P"], B, dose, extra))
            except GuardFail as e:
                if arm in alias and bad != "guard": print(f"  guard (aliased, not enforced) {arm} seed {s}: {str(e)[:160]}")
                else: sys.exit(f"{arm} seed {s}: parameters do not match {base} at cost 0 but for the dose: {e}")
            rs.append(r)
        RS[arm] = rs
    if newkeys: print("parameter keys the exp012 runs add over their cost-0 runs (allowed): " + ", ".join(sorted(newkeys)))
    for k, rs in RS.items(): seeds[k] = {r["seed"]: r for r in rs}
    S = {k: summary(rs) for k, rs in RS.items()}
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"; u3 = lambda x: "-" if x is None else f"{x:.3f}"
    mse = lambda p, fmt=f3: "-" if p is None or p[0] is None else f"{fmt(p[0])} ({p[1]:.3f})"
    iv = lambda c: "-" if c[0] is None else (f"{f3(c[0])} [{f3(c[1])}, {f3(c[2])}] n{c[3]}" if c[1] is not None else f"{f3(c[0])} n{c[3]}")
    order = list(ARMS) + BASES; show = [x for x in order if x in S]
    print(f"\nyears {y0}-{y1}; p = mean of the eight core genotypes (R A S B H T M W); established = jump_tab herd-size"
          " criterion; gap columns over established seeds, wild columns over all seeds")
    print("| arm | seeds | established (KM 95%) | median year | late | herd>=100 in window | fell back | herd | wild size | mean core gap (SE) | wild p (SE) | wild T (SE) | sel p dam / sire / mid (SE) | breadth | below | above | depth | csire |")
    print("|---|" + "---|" * 18)
    for x in show:
        v = S[x]; k, cI = v["km"]
        kms = f"{v['nE']} ({k:.2f}" + (f" [{cI[0]:.2f}, {cI[1]:.2f}]" if cI else "") + ")"
        print(f"| {x} | {v['n']} | {kms} | {v['Jmed'] or '-'} | {v['late']} | {v['win100']} | {', '.join(str(r['seed']) for r in v['fell']) or '-'} | "
              f"{v['herd']:.1f} | {u3(v['wsize'][0]) if v['wsize'][0] is None else format(v['wsize'][0], '.1f')} | {mse(v['pgap'])} | {mse(v['wp'], u3)} | {mse(v['wT'], u3)} | "
              f"{f3(v['selD'][0])} / {f3(v['selS'][0])} / {mse(v['selp'])} | {v['breadth'] if v['breadth'] is not None else '-'} | "
              f"{len(v['below'])} ({' '.join(v['below']) or '-'}) | {len(v['above'])} ({' '.join(v['above']) or '-'}) | "
              f"{mse(v['flow']['depth'], lambda z: f'{z:.2f}')} | {mse(v['flow']['csire'], u3)} |")
    print("\nGaps by trait, established seeds, arm mean (SE); L and C are outside p")
    print("| arm | " + " | ".join(TRAITS) + " |\n|---|" + "---|" * len(TRAITS))
    for x in show:
        if S[x]["gap"]: print(f"| {x} | " + " | ".join(mse(S[x]["gap"][t]) for t in TRAITS) + " |")
    print("\nSplit (split_tab, founders 301-400), established seeds, arm means: herd change / wild change")
    print("| arm | p | " + " | ".join(TRAITS) + " |\n|---|---|" + "---|" * len(TRAITS))
    for x in show:
        E = [r for r in S[x]["E"] if r["hc"]]
        if not E: continue
        m = lambda k, t: sum(r[k][t] for r in E) / len(E)
        print(f"| {x} | {f3(S[x]['hcp'][0])} / {f3(S[x]['wcp'][0])} | " + " | ".join(f"{m('hc', t):+.3f} / {m('wc', t):+.3f}" for t in TRAITS) + " |")
    C = {}
    G = {"pgap": (lambda r: r["pgap"], True), "wp": (lambda r: r["wp"], False), "wT": (lambda r: r["wT"], False),
         "selp": (lambda r: r["selp"], True), "selD": (lambda r: r["selD"], True), "selS": (lambda r: r["selS"], True),
         "hcp": (lambda r: r["hcp"], True), "wcp": (lambda r: r["wcp"], True)}
    for A, B in PAIRS:
        for k, (g, est) in G.items(): C[(A, B, k)] = paired(seeds, A, B, g, est)
    print("\nChanges paired by seed, mean [95% interval] n: mean core gap, herd change p, wild change p and the selection"
          " differential over seeds established in both; wild p and wild T over every seed both have")
    print("| pair | mean core gap | herd change p | wild change p | wild p | wild T | sel p (mid) | sel p dam | sel p sire |\n|---|---|---|---|---|---|---|---|---|")
    for A, B in PAIRS:
        if A in S and B in S: print(f"| {A} - {B} | " + " | ".join(iv(C[(A, B, k)]) for k in ("pgap", "hcp", "wcp", "wp", "wT", "selp", "selD", "selS")) + " |")
    print("\nPer-trait signed gap change, paired by seed over seeds established in both, mean [95% interval]")
    print("| pair | " + " | ".join(TRAITS) + " |\n|---|" + "---|" * len(TRAITS))
    for A, B in PAIRS:
        if A in S and B in S:
            print(f"| {A} - {B} | " + " | ".join(iv(paired(seeds, A, B, lambda r, t=t: r["gap"][t] if r["gap"] else None)) for t in TRAITS) + " |")
    # amendment 2: the demographic match of DEEP50 and DEEPFLAT50
    S["_demog"] = []
    if "DEEP50" in S and "DEEPFLAT50" in S:
        DM = [("herd births per doe-year", "bpd", True), ("mean first-kid age, herd (y)", "fkh", True),
              ("mean first-kid age, wild (y)", "fkw", False), ("herd size", "herd", False), ("wild size", "wsize", False)]
        print("\nDemographic match (amendment 2): DEEP50 and DEEPFLAT50 by seed; paired difference [95% interval]; herd measures"
              " over seeds established in both, sizes and the wild over all seeds")
        print("| measure | DEEP50 | DEEPFLAT50 | DEEP50 - DEEPFLAT50 | beyond noise |\n|---|---|---|---|---|")
        for name, k, est in DM:
            c = paired(seeds, "DEEP50", "DEEPFLAT50", lambda r, k=k: r[k], est)
            pick = lambda arm: ms([r[k] for r in (S[arm]["E"] if est else S[arm]["runs"])])
            beyond = c[1] is not None and not (c[1] <= 0 <= c[2])
            if beyond: S["_demog"].append(name)
            print(f"| {name} | {mse(pick('DEEP50'), u3)} | {mse(pick('DEEPFLAT50'), u3)} | {iv(c)} | {'yes' if beyond else 'no' if c[1] is not None else '-'} |")
        print("Demographic match: " + ("incomplete; prediction 5's difference carries part of the demographic effect ("
              + ", ".join(S["_demog"]) + ")" if S["_demog"] else "no measure differs beyond noise"))
    # the amendment quotes 3 decimals of values that sit at -0.0485 and -0.0865 by every method tried (hist row means,
    # pooled hist, year-row trait means), rounded away from zero; "matches" = within 0.001 (L put into p misses by 0.013+)
    print("\nChecks (the amendment's quoted cost-0 values; match = within 0.001):")
    for b, q in QUOTED.items():
        got = S[b]["pgap"][0]; ok = got is not None and abs(got - q) <= 0.001
        print(f"  cost-0 mean core gap {b}: {'-' if got is None else f'{got:+.5f}'} against the amendment's {q:+.3f}: {'matches' if ok else 'DIFFERS'}")
    b, q = QUOTED_ALLP; got = S[b]["allp"][0]
    print(f"  cost-0 all-goat p {b}: {'-' if got is None else f'{got:.5f}'} against the amendment's {q:.3f}: {'matches' if got is not None and abs(got - q) <= 0.001 else 'DIFFERS'}")
    print("  wild means over split's rows = F + wild change, every run: passes (the tool stops otherwise)")
    if perseed:
        print("\n| arm | seed | J | herd | wild size | mean core gap | wild p | wild T | sel p mid | births/doe-yr | first-kid herd | breadth |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for x in show:
            for r in S[x]["runs"]:
                br = sum(1 for t in CORE if abs(r["gap"][t]) >= 0.10) if r["gap"] else "-"
                print(f"| {x} | {r['seed']} | {r['J'] or '-'} | {r['herd']:.1f} | {u3(r['wsize'])} | {f3(r['pgap'])} | {u3(r['wp'])} | {u3(r['wT'])} | "
                      f"{f3(r['selp'])} | {u3(r['bpd'])} | {u3(r['fkh'])} | {br} |")
    print("\nPredictions (5a2948f; replaced by amendment e53d80f, 4 standing; amendment 2):")
    L, V = read(S, C); print("\n".join(L))

def selftest(bad=False):
    ok = True
    def check(name, got, want):
        nonlocal ok; res = got == want; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} {name}" + ("" if res else f": got {got}, want {want}"))
    # guard
    B = {"id": {"run": "x"}, "seed": 1, "reproCostFertility": 0, "reproCostGrowth": 0, "matingConception": 0.7, "sireRule": "deep"}
    def g(P, dose, extra=None):
        try: return guard(P, B, dose, extra or {})
        except GuardFail as e: return "stop"
    check("guard: the dose alone differs", g({**B, "reproCostFertility": 0.5, "id": {"run": "y"}}, 0.5), [])
    check("guard: a new key is allowed and listed", g({**B, "reproCostFertility": 0.5, "firstSireAge": 1}, 0.5), ["firstSireAge"])
    check("guard: wrong dose stops", g({**B, "reproCostFertility": 0.25}, 0.5), "stop")
    check("guard: another parameter changed stops", g({**B, "reproCostFertility": 0.5, "sireRule": "random"}, 0.5), "stop")
    check("guard: a key missing stops", g({k: v for k, v in B.items() if k != "sireRule"} | {"reproCostFertility": 0.5}, 0.5), "stop")
    check("guard: an output-only switch may differ, listed",
          guard({**B, "reproCostFertility": 0.5, "logHistDepth": 1}, {**B, "logHistDepth": 0}, 0.5, {}), ["logHistDepth 0->1 (output only)"])
    check("guard: DEEPFLAT50 conception",g({**B, "matingConception": 0.356}, 0.0, {"matingConception": 0.356}), [])
    check("guard: DEEPFLAT50 conception wrong stops", g({**B}, 0.0, {"matingConception": 0.356}), "stop")
    # decision branches from hand-made summaries and paired intervals
    def Sx(nE=None):
        nE = nE or {}
        return {a: {"read": nE.get(a, 8) >= 2, "nE": nE.get(a, 8)} for a in list(ARMS) + BASES}
    neg, zero, pos = (-0.05, -0.08, -0.02, 8), (-0.01, -0.03, 0.01, 8), (0.04, 0.01, 0.07, 8)
    def Cx(deep, rand, flat, sel, ref=neg, ref25=(-0.02, -0.04, -0.005, 8)):
        C = {}
        for a, b in (("REF50", "REF"), ("DEEP50", "CTLDEEP"), ("RAND50", "CTLRAND")):
            C[(a, b, "wp")] = neg; C[(a, b, "wT")] = pos
        C[("DEEP50", "CTLDEEP", "pgap")] = deep; C[("DEEP25", "CTLDEEP", "pgap")] = deep
        C[("RAND50", "CTLRAND", "pgap")] = rand; C[("DEEP50", "DEEPFLAT50", "pgap")] = flat
        C[("DEEP50", "CTLDEEP", "selp")] = sel; C[("DEEP25", "CTLDEEP", "selp")] = sel
        C[("REF50", "REF", "pgap")] = ref; C[("REF25", "REF", "pgap")] = ref25
        return C
    cases = [("A: the grain mechanism", Sx(), Cx(neg, zero, neg, neg), ["A"]),
             ("B: demographic", Sx(), Cx(neg, zero, zero, neg), ["B"]),
             ("C: the cost does not select", Sx(), Cx(zero, zero, zero, zero), ["C"]),
             ("D: swamped", Sx(), Cx(zero, zero, neg, neg), ["D"]),
             ("E: not specific to closed herds", Sx(), Cx(neg, neg, neg, neg), ["E"]),
             ("B and E together", Sx(), Cx(neg, neg, zero, neg), ["B", "E"]),
             ("F: DEEP50 fails, read at 0.25; 5 not read", Sx({"DEEP50": 1}), Cx(neg, zero, neg, neg), ["F"])]
    if bad: cases[0] = (cases[0][0], cases[0][1], cases[0][2], ["B"])
    for name, S, C, want in cases:
        _, V = read(S, C); check(name, V["branches"], want)
    _, V = read(Sx({"DEEP50": 1}), Cx(neg, zero, neg, neg)); check("fallback: prediction 5 not read at 0.25", V["p5"], None)
    _, V = read(Sx(), Cx(neg, zero, neg, neg, ref=neg, ref25=(-0.07, -0.09, -0.05, 8)))
    check("prediction 6 fails when REF25 is not between REF and REF50", V["p6"], False)
    C6 = Cx(neg, zero, neg, neg); del C6[("REF25", "REF", "pgap")]
    _, V = read(Sx(), C6); check("prediction 6 not read when REF25 has no paired value", V["p6"], None)
    L, V = read(Sx(), Cx(neg, zero, neg, zero))
    check("A with prediction 7 failing carries the label", (V["branches"], any("rests on DEEP50 - DEEPFLAT50 alone" in x for x in L)), (["A"], True))
    L, V = read(Sx(), Cx(neg, zero, neg, neg))
    check("A with prediction 7 holding has no label", any("rests on DEEP50 - DEEPFLAT50 alone" in x for x in L), False)
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest(sys.argv[2:3] == ["bad"]) else 1)
    main()
