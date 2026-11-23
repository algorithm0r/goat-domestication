# sched_tab.py: the scorer for exp014 (run-off by a time schedule matched to REF's curve), from its pre-registration
# (536bc53), amendment 1 (3dfc9bb, the reviewer's 3c9ab09), amendment 2 (1a67ab6) and the calibration pass (1a81bb5) in
# EXPLOG. Analysis session, 2026-11-22.
#   python tools/sched_tab.py EXP014_DIR "BASE_DIR[;BASE_DIR...]" [--alias ARM=SRC,...] [--window 3201-4000]
#          [--perseed] [--bad KIND]
#   python tools/sched_tab.py selftest [bad]
# EXP014_DIR holds SCHED, SCHEDT and REFT (<ARM>_seed<S>.json, seeds 1-8). BASE_DIR(s) hold REF (exp005 seeds 1-4,
# exp006 seeds 5-8). --alias maps an exp014 arm to another arm's files in EXP014_DIR, only to test the scorer before
# exp014 exists: an aliased table is a test, never a result, and the parameter guard is then printed, not enforced.
# Parameter guard (same seed; id may differ everywhere; spookFixed must be 0 in every run):
#   SCHEDT = SCHED but captureTaper 1, selfDoes 10 (every key);  REFT = SCHEDT but spookSchedule '' (every key);
#   SCHED = REF but spookSchedule = amendment 2's string; keys REF lacks (code added since exp005/006) are allowed and
#   listed; an output-only switch (logHistDepth) may differ, listed. So REFT = REF + captureTaper 1, selfDoes 10.
# Definitions (registration, amendments; the standing measures):
#   window 3201-4000 (1-based); founders 301-400 (split_tab, which stops unless herdingAt is 400).
#   established = the herd-size criterion of tools/jump_tab.py (100-year mean herd >= 100 held 400 years, after year
#     500, followed to the last row - 400); Kaplan-Meier fraction; herd >= 100 over the window beside it. An arm's
#     gaps and changes are read over its established seeds, with 2 or more of them.
#   R gap = herd - wild genotype mean of R (settle_tab.gaps); herd change hc and wild change wc of R against the
#     founders' mean (split_tab, identity gap = hc - wc checked there).
#   breadth = core traits (R A S B H T M W L) with abs(arm-mean gap) >= 0.10, established seeds; per seed the same count,
#     and the per-seed vote: diverged if 6 or more established seeds have breadth >= 3, not if 6 or more do not, else mixed.
#   closure: csire (flow_tab: herd conceptions by a sire captured himself / herd conceptions) and depth (herdAncDepth);
#     closed arm (amendment 1) = csire under 0.05 in 6 or more of the 8 seeds (a seed with no herd conceptions in the
#     window is not closed).
#   loss rates: ranOff, refetched, escaped per herd goat-year over the window (runoff_rate.py's estimator: events
#     summed over the window's year rows / herded summed over them), mean over seeds with herd goats.
#   achieved run-off curve: ranOff per century of herding (401-500 .. 3901-4000), the mean over seeds of each seed's
#     rate (as runoff_rate.py --check). REFT's and SCHEDT's side by side; "differ by more than 15% in the window" =
#     abs(SCHEDT / REFT - 1) > 0.15 on the window rate (3201-4000, each the mean over seeds); the window's eight
#     centuries are listed beside, with those beyond 15% counted (not part of the flag).
#   paired by seed: SCHED - REF and SCHEDT - REFT, over seeds established in both, 95% t interval (inflow_tab.tcrit);
#     loss rates over seeds with herd goats in both.
#   recapture share (each branch, descriptive): SCHEDT's R gap as a share of REFT's = mean SCHEDT R gap / mean REFT R
#     gap over seeds established in both; per-seed ratios listed.
# Checks: REF's run-off rates per century recomputed from the base runs must match the registered values (1.440 .. 0.871)
# within 0.0005; every run's window ranOff equals runoff_rate.rates on the same file (1e-12). --bad founders (founders
# 201-300: split_tab must stop), --bad guard (an aliased arm's guard enforced: must stop), --bad target (one registered
# REF rate changed by 0.01: the REF check must say DIFFERS) must each fail.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, jump_tab, flow_tab
from genecost_tab import ms, ci, paired, files
gaps, herd, CORE, TRAITS = split_tab.gaps, split_tab.herd, split_tab.CORE, split_tab.TRAITS
_src = open(os.path.join(HERE, "runoff_rate.py"), encoding="utf-8").read().replace("\nmain()\n", "\n")
_ns = {"__file__": os.path.join(HERE, "runoff_rate.py")}; exec(_src, _ns); rates_file = _ns["rates"]

SCHEDULE = "0:0.00492,100:0.00642,200:0.00789,300:0.00826,400:0.00690,500:0.00593,600:0.00427,700:0.00315,800:0.00269"
ARMS = ["SCHED", "SCHEDT", "REFT"]; BASE = "REF"; SHOW = ["SCHED", "REF", "SCHEDT", "REFT"]
PAIRS = [("SCHED", "REF"), ("SCHEDT", "REFT")]
TARGET = [((401, 500), 1.440), ((501, 600), 1.820), ((601, 700), 2.254), ((701, 800), 2.341), ((801, 900), 2.052),
          ((901, 1000), 1.722), ((1001, 1100), 1.269), ((1101, 1200), 0.975), ((1201, 4000), 0.871)]
CENT = [(401 + 100 * k, 500 + 100 * k) for k in range(36)]
LOSS = ["ranOff", "refetched", "escaped"]
OUTPUT_ONLY = {"logHistDepth"}
# keys added since exp005/006 (REF lacks them): each must hold its identity value, the one that leaves REF's model as it
# was (src/params.js defaults; the reviewer's cdc7055: runOffLoss 0 would switch off loss by run-off, the mechanism under
# test). A key REF lacks that is not listed here stops the tool.
IDENTITY = {"runOffLoss": 1, "cInitHi": 1, "cInitLo": 0, "selfDoes": 0, "larder": 0, "captureTaper": 0, "nuisanceCost": 0,
            "buckPrefValue": 0, "doePrefValue": 0, "spookFixed": 0}

class GuardFail(Exception): pass

def eq(a, b): return a == b or (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= 1e-9)

def guard(P, B, want, allow_new=False, ident=IDENTITY):
    """Differences between run parameters P and its counterpart's B (same seed). want = {key: value P must have}; every
    other key must be equal. allow_new: keys B lacks are allowed if they hold their identity value (ident), returned as
    'key=value'. Raises GuardFail otherwise."""
    bad, out = [], []
    if not eq(P.get("spookFixed", 0), 0): bad.append(f"spookFixed {P.get('spookFixed')} (want 0)")
    for k, v in want.items():
        if not eq(P.get(k, "" if k == "spookSchedule" else 0), v): bad.append(f"{k} {P.get(k)!r} (want {v!r})")
    skip = {"id"} | set(want)
    for k in B:
        if k in skip: continue
        if k not in P: bad.append(f"{k} missing (counterpart: {B[k]})")
        elif not eq(P[k], B[k]):
            if k in OUTPUT_ONLY: out.append(f"{k} {B[k]}->{P[k]} (output only)")
            else: bad.append(f"{k} {P[k]!r} (counterpart: {B[k]!r})")
    new = sorted(k for k in P if k not in B and k not in skip)
    if new and not allow_new: bad.append("keys the counterpart lacks: " + ", ".join(new))
    if allow_new:
        for k in new:
            if k not in ident: bad.append(f"{k} {P[k]!r}: a key REF lacks with no identity value listed")
            elif not eq(P[k], ident[k]): bad.append(f"{k} {P[k]!r} (identity value {ident[k]!r})")
    if bad: raise GuardFail(", ".join(bad))
    return [f"{k}={P[k]!r}" for k in new] + out

def rate(d, y0, y1):   # runoff_rate.py's estimator on a loaded run: {ranOff, refetched, escaped} or None
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    hd = sum(r.get("herded") or 0 for r in rows)
    return {k: sum(r.get(k) or 0 for r in rows) / hd for k in LOSS} if rows and hd else None

def score(f, y0, y1, bad=None):
    d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
    g = gaps(d, y0, y1); h = herd(d, y0, y1)
    sp = split_tab.split(d, y0, y1, 201, 300) if bad == "founders" else split_tab.split(d, y0, y1, 301, 400)
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    J, end, _, late = jump_tab.jump(hs, lambda v: v >= 100, 400)
    fl = flow_tab.run_flow(d, y0, y1) or {}
    loss = rate(d, y0, y1)
    chk = rates_file(f, y0, y1)[3]   # the same estimator as runoff_rate.py, on the same file
    if (loss is None) != (chk is None) or (loss and any(abs(loss[k] - chk[k]) > 1e-12 for k in LOSS)):
        sys.exit(f"{os.path.basename(f)}: window rates differ from runoff_rate.rates")
    run = {"P": P, "gap": g, "herd": h, "J": J, "end": end, "late": late, "est": J is not None and g is not None,
           "hc": sp[0]["R"][0] if sp else None, "wc": sp[0]["R"][1] if sp else None, "F": sp[1]["R"] if sp else None,
           "csire": fl.get("csire"), "depth": fl.get("depth"), "loss": loss,
           "curve": {c: (rate(d, *c) or {}).get("ranOff") for c in CENT + [p for p, _ in TARGET] + [(y0, y1)]}}
    run["R"] = g["R"] if g else None
    run["breadth"] = sum(1 for t in CORE if abs(g[t]) >= 0.10) if g else None
    return run

def vote(k, n): return True if k >= 6 else False if n - k >= 6 else "mixed"

def closed_count(runs): return sum(1 for r in runs if r["csire"] is not None and r["csire"] < 0.05)

def summary(runs):
    E = [r for r in runs if r["est"]]
    v = {"n": len(runs), "nE": len(E), "E": E, "runs": runs, "read": len(E) >= 2, "late": sum(1 for r in runs if r["late"]),
         "win100": sum(1 for r in runs if r["herd"] >= 100), "herd": ms([r["herd"] for r in runs])[0],
         "Jmed": sorted(r["J"] for r in E)[len(E) // 2] if E else None,
         "km": jump_tab.km([(r["J"], r["end"]) for r in runs], max(r["end"] for r in runs)) if runs else (None, None)}
    for k in ("R", "hc", "wc", "F"): v[k] = ms([r[k] for r in E])
    v["gap"] = {t: ms([r["gap"][t] for r in E]) for t in TRAITS} if E else None
    v["breadth"] = sum(1 for t in CORE if abs(v["gap"][t][0]) >= 0.10) if E else None
    v["btraits"] = [t for t in CORE if abs(v["gap"][t][0]) >= 0.10] if E else []
    v["ndiv"] = sum(1 for r in E if r["breadth"] >= 3)
    v["diverged"] = vote(v["ndiv"], len(E)) if v["read"] else "not read"
    v["nclosed"] = closed_count(runs); v["closed"] = v["nclosed"] >= 6
    v["csire"] = ms([r["csire"] for r in runs]); v["depth"] = ms([r["depth"] for r in runs])
    v["csireE"] = ms([r["csire"] for r in E]); v["depthE"] = ms([r["depth"] for r in E])
    v["loss"] = {k: ms([r["loss"][k] for r in runs if r["loss"]]) for k in LOSS}
    v["curve"] = {c: ms([r["curve"][c] for r in runs]) for c in runs[0]["curve"]} if runs else {}
    return v

def rate_flag(S, w):
    """SCHEDT vs REFT achieved run-off rate in the window w: (ratio, flagged, [(century, ratio)] in the window, n of
    those beyond 15%, n of all 36 centuries beyond 15%, n of the 36 compared, n of the 36 with SCHEDT above REFT).
    Only the window rate is the flag."""
    a, b = S["SCHEDT"]["curve"].get(w, (None,))[0], S["REFT"]["curve"].get(w, (None,))[0]
    ratio = a / b if a is not None and b else None
    cs = []
    for c in CENT:
        if c[0] >= w[0] and c[1] <= w[1]:
            x, y = S["SCHEDT"]["curve"][c][0], S["REFT"]["curve"][c][0]
            cs.append((c, x / y if x is not None and y else None))
    beyond = lambda q: q is not None and abs(q - 1) > 0.15
    al = [S["SCHEDT"]["curve"][c][0] / S["REFT"]["curve"][c][0] if S["SCHEDT"]["curve"][c][0] is not None and S["REFT"]["curve"][c][0] else None for c in CENT]
    return (ratio, (None if ratio is None else abs(ratio - 1) > 0.15), cs, sum(1 for _, q in cs if beyond(q)),
            sum(1 for q in al if beyond(q)), sum(1 for q in al if q is not None), sum(1 for q in al if q is not None and q > 1))

def read(S, C, flag):
    """Predictions and decision rule. S = arm summaries; C = {(A, B, measure): (mean, lo, hi, n)} paired; flag =
    rate_flag(...) or None. Returns (lines, verdicts)."""
    L, V = [], {}
    f = lambda x: "-" if x is None else f"{x:+.3f}"
    iv = lambda c: "not read" if c is None or c[0] is None else (f"{f(c[0])} [{f(c[1])}, {f(c[2])}], n {c[3]}" if c[1] is not None else f"{f(c[0])} (n {c[3]}, no interval)")
    rd = lambda a: a in S and S[a]["read"]
    gR = lambda a: S[a]["R"][0] if rd(a) else None
    # predictions (536bc53)
    nE = {a: S[a]["nE"] if a in S else None for a in ("SCHED", "SCHEDT")}
    V["p1"] = all(x is not None and x >= 6 for x in nE.values())
    L.append(f"1. SCHED and SCHEDT establish in 6 or more of 8 seeds: {V['p1']} (SCHED {nE['SCHED']}, SCHEDT {nE['SCHEDT']})")
    c = C.get(("SCHEDT", "REFT", "R")); gt, gr = gR("SCHEDT"), gR("REFT")
    if gt is None: V["p2"] = None; L.append("2. SCHEDT R gap <= -0.30 and smaller in size than REFT's: not read (SCHEDT under 2 established)")
    else:
        a2 = gt <= -0.30
        if gr is None or gr >= 0 or c is None or c[1] is None:
            b2 = None; why = "REFT not read" if gr is None else "REFT's R gap not negative" if gr >= 0 else "no paired interval"
        else: b2, why = c[1] > 0, ""
        V["p2"] = False if not a2 else b2
        L.append(f"2. SCHEDT R gap <= -0.30 ({f(gt)}, {S['SCHEDT']['nE']} established seeds: {a2}) and smaller in size than REFT's ({f(gr)}), paired SCHEDT - REFT"
                 f" interval above 0 ({iv(c)}: {'-' if b2 is None else b2}{'; ' + why if why else ''}): {V['p2']}")
    hc = S["SCHED"]["hc"][0] if rd("SCHED") else None
    V["p3"] = None if hc is None else hc <= -0.20
    L.append(f"3. SCHED's herd R falls from its founders by 0.20 or more (herd change of R, established seeds, {f(hc)}): {V['p3']}")
    # decision rule (536bc53 as amended by 3dfc9bb)
    fired = []
    T = S.get("SCHEDT")
    if T is None or T["nE"] < 2:
        fired.append(("3", "Fewer than 2 established seeds in SCHEDT: the schedule's rates, spread over all goats, do not let a"
                      " closed herd form; goes to Chris."))
    else:
        cl = T["closed"]
        if gr is None or gr > -0.30:
            fired.append(("REFT-above", "REFT R gap above -0.30" + (" (REFT not read)" if gr is None else f" ({f(gr)})") +
                          ": closing REF removes the reactive captives the filter acts on; no contrast is read, and SCHEDT is"
                          " reported alone."))
        if cl and gt <= -0.30:
            fired.append(("1", f"SCHEDT closed (csire under 0.05 in {T['nclosed']} of {T['n']} seeds) with R gap {f(gt)}: recapture alone"
                          " carries a filter strong enough for divergence on R; no per-herd load is needed for it, and the"
                          " run-off time course is REF's."))
        if cl and gt > -0.30 and gr is not None and gr <= -0.30:
            s = (f"SCHEDT closed (csire under 0.05 in {T['nclosed']} of {T['n']} seeds) with R gap {f(gt)} above -0.30, REFT's {f(gr)}"
                 f" (REFT csire under 0.05 in {S['REFT']['nclosed']} of {S['REFT']['n']} seeds):"
                 " the filter needs the run-off side to read the goat (R x fear) and its herd's load. Four things differ between"
                 " SCHEDT and REFT: R in the spook, fear in the spook, the per-herd load, and the run-off level.")
            if flag is None or flag[1] is None: s += " Run-off rates in the window: not compared."
            elif flag[1]: s += f" The reading carries a rate difference too: SCHEDT's run-off rate in the window is {flag[0]:.3f} x REFT's (more than 15% apart)."
            else: s += f" Run-off rates in the window within 15% (SCHEDT / REFT {flag[0]:.3f})."
            fired.append(("2", s))
        if not cl:
            fired.append(("not-closed", f"SCHEDT established ({T['nE']} seeds) but not closed (csire under 0.05 in {T['nclosed']} of"
                          f" {T['n']} seeds): no branch fires; reported with herd change against founders (SCHEDT herd change"
                          f" of R {f(T['hc'][0])}, wild change {f(T['wc'][0])})."))
    V["branches"] = [k for k, _ in fired]
    L.append("\nDecision rule (536bc53, amended 3dfc9bb), what fires:")
    L += [f"- {k}: {s}" for k, s in fired]
    if "REFT-above" in V["branches"] and "1" in V["branches"]:   # the reviewer's cdc7055: the amendment reads no contrast then
        L.append("- Recapture stage's share of the filter: not read (REFT R gap above -0.30: no contrast is read)")
    elif gt is not None and gr is not None and gr != 0 and any(k in ("1", "2") for k in V["branches"]):
        sh = C.get(("SCHEDT", "REFT", "share"))
        L.append(f"- Recapture stage's share of the filter (descriptive): SCHEDT's R gap / REFT's over seeds established in both = "
                 + ("-" if not sh or sh[0] is None else f"{sh[0]:.2f} (n {sh[1]}; per seed " + ", ".join(f"s{s} {q:.2f}" for s, q in sh[2]) + ")"))
    sc = S.get("SCHED")
    if sc and sc["read"]:
        L.append(f"- SCHED (open), beside the rule: herd change of R against founders {f(sc['hc'][0])}, wild change {f(sc['wc'][0])},"
                 f" R gap {f(sc['R'][0])}; paired SCHED - REF: R gap {iv(C.get(('SCHED', 'REF', 'R')))}, herd change"
                 f" {iv(C.get(('SCHED', 'REF', 'hc')))}, wild change {iv(C.get(('SCHED', 'REF', 'wc')))}.")
    else: L.append("- SCHED (open), beside the rule: not read (under 2 established seeds)")
    return L, V

def share(seeds):
    A, B = seeds.get("SCHEDT", {}), seeds.get("REFT", {})
    both = [s for s in A if s in B and A[s]["est"] and B[s]["est"]]
    if not both: return (None, 0, [])
    ma = sum(A[s]["R"] for s in both) / len(both); mb = sum(B[s]["R"] for s in both) / len(both)
    return (ma / mb if mb else None, len(both), [(s, A[s]["R"] / B[s]["R"]) for s in both if B[s]["R"]])

def ref_check(S, target):
    out = []
    for (y0, y1), t in target:
        got = S["REF"]["curve"].get((y0, y1), (None,))[0]
        out.append(((y0, y1), t, got, got is not None and abs(got - t) <= 0.0005))
    return out

def main():
    a = sys.argv[1:]; alias = {}; y0, y1 = 3201, 4000
    def opt(k):
        if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    if (v := opt("--alias")): alias = dict(x.split("=") for x in v.split(","))
    if (v := opt("--window")): y0, y1 = (int(x) for x in v.split("-"))
    bad = opt("--bad"); perseed = "--perseed" in a; a = [x for x in a if x != "--perseed"]
    if not alias and "exp014" not in a[0]: sys.exit("EXP014_DIR must be exp014's folder (or, with --alias, a stand-in folder)")
    X, Bf = files([a[0]]), files(a[1].split(";"))
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not exp014 results; the parameter guard is printed, not enforced ***")
    if bad: print(f"*** TEST ONLY: --bad {bad} ***")
    if BASE not in Bf: sys.exit(f"REF not found in {a[1]}")
    RS = {BASE: [dict(score(fn, y0, y1, bad), seed=s) for s, fn in sorted(Bf[BASE].items())]}
    for arm in ARMS:
        src = alias.get(arm, arm)
        if src not in X: print(f"{arm}: no runs ({src})"); continue
        RS[arm] = [dict(score(fn, y0, y1, bad), seed=s) for s, fn in sorted(X[src].items())]
    seeds = {k: {r["seed"]: r for r in rs} for k, rs in RS.items()}
    # the parameter guard, by seed: SCHEDT vs SCHED, REFT vs SCHEDT (every key), SCHED vs REF (new keys allowed, listed)
    rules = [("SCHEDT", "SCHED", {"captureTaper": 1, "selfDoes": 10}, False), ("REFT", "SCHEDT", {"spookSchedule": ""}, False),
             ("SCHED", "REF", {"spookSchedule": SCHEDULE}, True)]
    newkeys = set()
    for A, B, want, allow in rules:
        if A not in seeds or B not in seeds: print(f"guard {A} vs {B}: not checked (an arm is missing)"); continue
        for s, r in seeds[A].items():
            if r["P"].get("seed") is not None and r["P"]["seed"] != s and not (A in alias):
                sys.exit(f"{A} seed {s}: the run's own seed parameter is {r['P']['seed']}")
            if s not in seeds[B]:
                if A in alias: print(f"  guard {A} seed {s}: no {B} seed (aliased test only)"); continue
                sys.exit(f"{A} seed {s}: no {B} run with that seed")
            try: newkeys |= set(guard(r["P"], seeds[B][s]["P"], want, allow))
            except GuardFail as e:
                if (A in alias or B in alias) and bad != "guard": print(f"  guard (aliased, not enforced) {A} vs {B} seed {s}: {str(e)[:160]}")
                else: sys.exit(f"{A} seed {s}: parameters do not match {B}'s as registered: {e}")
    if newkeys: print("parameter keys SCHED adds over REF (code since exp005/006), each at its identity value: " + ", ".join(sorted(newkeys)))
    S = {k: summary(rs) for k, rs in RS.items()}
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"; u3 = lambda x: "-" if x is None else f"{x:.3f}"
    mse = lambda p, fmt=f3: "-" if p is None or p[0] is None else f"{fmt(p[0])} ({p[1]:.3f})"
    iv = lambda c: "-" if c is None or c[0] is None else (f"{f3(c[0])} [{f3(c[1])}, {f3(c[2])}] n{c[3]}" if c[1] is not None else f"{f3(c[0])} n{c[3]}")
    show = [x for x in SHOW if x in S]
    print(f"\nyears {y0}-{y1}; established = jump_tab herd-size criterion; R gap, changes and breadth over established seeds;"
          " closure over all seeds (csire under 0.05 = closed seed)")
    print("| arm | seeds | established (KM 95%) | median year | late | herd>=100 in window | herd | R gap (SE) | herd change R (SE) | wild change R (SE) | founders' R | breadth (traits) | per-seed breadth>=3 | closed seeds (csire<0.05) | csire all (SE) | depth all (SE) |")
    print("|---|" + "---|" * 15)
    for x in show:
        v = S[x]; k, cI = v["km"]
        kms = f"{v['nE']} ({k:.2f}" + (f" [{cI[0]:.2f}, {cI[1]:.2f}]" if cI else "") + ")"
        print(f"| {x} | {v['n']} | {kms} | {v['Jmed'] or '-'} | {v['late']} | {v['win100']} | {v['herd']:.1f} | {mse(v['R'])} | "
              f"{mse(v['hc'])} | {mse(v['wc'])} | {u3(v['F'][0])} | {v['breadth'] if v['breadth'] is not None else '-'} ({' '.join(v['btraits']) or '-'}) | "
              f"{v['ndiv']} of {v['nE']}: {v['diverged']} | {v['nclosed']} of {v['n']}: {'closed' if v['closed'] else 'not closed'} | "
              f"{mse(v['csire'], u3)} | {mse(v['depth'], lambda z: f'{z:.2f}')} |")
    print("\nGaps by trait, established seeds, arm mean (SE)")
    print("| arm | " + " | ".join(TRAITS) + " |\n|---|" + "---|" * len(TRAITS))
    for x in show:
        if S[x]["gap"]: print(f"| {x} | " + " | ".join(mse(S[x]["gap"][t]) for t in TRAITS) + " |")
    print("\nLoss rates per herd goat-year over the window, mean over seeds with herd goats (SE): run-offs, fetched back, lost")
    print("| arm | run-offs (ranOff) | fetched back | lost (escaped) | closure, established seeds: csire / depth |\n|---|---|---|---|---|")
    for x in show:
        print(f"| {x} | " + " | ".join(mse(S[x]["loss"][k], u3) for k in LOSS) + f" | {mse(S[x]['csireE'], u3)} / {mse(S[x]['depthE'], lambda z: f'{z:.2f}')} |")
    C = {}
    G = {"R": (lambda r: r["R"], True), "hc": (lambda r: r["hc"], True), "wc": (lambda r: r["wc"], True),
         "csire": (lambda r: r["csire"], False), "depth": (lambda r: r["depth"], False)}
    G.update({k: (lambda r, k=k: r["loss"][k] if r["loss"] else None, False) for k in LOSS})
    for A, B in PAIRS:
        for k, (g, est) in G.items(): C[(A, B, k)] = paired(seeds, A, B, g, est)
    C[("SCHEDT", "REFT", "share")] = share(seeds)
    print("\nPaired by seed, mean [95% interval] n: R gap, herd and wild change of R over seeds established in both; closure and"
          " loss rates over seeds both have (with herd goats)")
    print("| pair | R gap | herd change R | wild change R | csire | depth | run-offs | fetched back | lost |\n|---|---|---|---|---|---|---|---|---|")
    for A, B in PAIRS:
        if A in S and B in S: print(f"| {A} - {B} | " + " | ".join(iv(C[(A, B, k)]) for k in ("R", "hc", "wc", "csire", "depth") + tuple(LOSS)) + " |")
    # the achieved run-off curve
    print("\nAchieved run-off rate (ranOff per herd goat-year) per century of herding, mean over seeds with herd goats (n);"
          " REF's registered rate beside (536bc53; 401-1200 by century, 0.871 over 1201-4000)")
    tg = dict(TARGET)
    print("| years | REF registered | REF | SCHED | SCHED / registered | REFT | SCHEDT | SCHEDT / REFT |\n|---|---|---|---|---|---|---|---|")
    cell = lambda x, c: "-" if x not in S or S[x]["curve"][c][0] is None else f"{S[x]['curve'][c][0]:.3f} ({sum(1 for r in S[x]['runs'] if r['curve'][c] is not None)})"
    val = lambda x, c: S[x]["curve"][c][0] if x in S else None
    for c in CENT + [(1201, 4000), (y0, y1)]:
        t = tg.get(c, tg[(1201, 4000)] if c[0] >= 1201 else None)
        rs = val("SCHED", c); rt, rr = val("SCHEDT", c), val("REFT", c)
        lab = f"{c[0]}-{c[1]}" + (" (window)" if c == (y0, y1) else " (all)" if c == (1201, 4000) else "")
        print(f"| {lab} | {u3(t)} | {cell('REF', c)} | {cell('SCHED', c)} | {'-' if rs is None or not t else f'{rs / t:.2f}'} | "
              f"{cell('REFT', c)} | {cell('SCHEDT', c)} | {'-' if rt is None or not rr else f'{rt / rr:.2f}'} |")
    flag = rate_flag(S, (y0, y1)) if "SCHEDT" in S and "REFT" in S else None
    if flag:
        print(f"SCHEDT vs REFT in the window {y0}-{y1}: SCHEDT / REFT = {'-' if flag[0] is None else f'{flag[0]:.3f}'}: "
              + ("not compared" if flag[1] is None else "DIFFER by more than 15% (flagged)" if flag[1] else "within 15%")
              + f"; centuries beyond 15% (context, not part of the flag): {flag[3]} of the window's {len(flag[2])}, {flag[4]} of all {flag[5]}; SCHEDT above REFT in {flag[6]} of {flag[5]}")
    print("\nCheck: REF's run-off rate per period recomputed from the base runs against the registered values (match = within 0.0005):")
    tgt = [(p, t + (0.01 if bad == "target" and i == 0 else 0)) for i, (p, t) in enumerate(TARGET)]
    for (p0, p1), t, got, ok in ref_check(S, tgt):
        print(f"  {p0}-{p1}: {u3(got)} against {t:.3f}: {'matches' if ok else 'DIFFERS'}")
    print("  window ranOff = runoff_rate.rates on every file: passes (the tool stops otherwise)")
    if perseed:
        print("\n| arm | seed | J | herd | R gap | herd change R | wild change R | breadth | csire | depth | run-offs | fetched back | lost |")
        print("|---|" + "---|" * 12)
        for x in show:
            for r in S[x]["runs"]:
                dp = "-" if r["depth"] is None else f"{r['depth']:.2f}"
                print(f"| {x} | {r['seed']} | {r['J'] or '-'} | {r['herd']:.1f} | {f3(r['R'])} | {f3(r['hc'])} | {f3(r['wc'])} | "
                      f"{r['breadth'] if r['breadth'] is not None else '-'} | {u3(r['csire'])} | {dp} | "
                      + " | ".join(u3(r["loss"][k]) if r["loss"] else "-" for k in LOSS) + " |")
    print("\nPredictions (536bc53):")
    L, V = read(S, C, flag); print("\n".join(L))

def selftest(bad=False):
    ok = True
    def check(name, got, want):
        nonlocal ok; res = got == want; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} {name}" + ("" if res else f": got {got}, want {want}"))
    # guard
    B = {"id": {"run": "x"}, "seed": 1, "spookSchedule": "", "spookFixed": 0, "captureTaper": 0, "selfDoes": 0, "herdRange": 8}
    def g(P, Bx, want, allow=False):
        try: return guard(P, Bx, want, allow)
        except GuardFail: return "stop"
    SC = {**B, "spookSchedule": SCHEDULE}
    check("guard: SCHED = REF but the schedule", g({**SC, "id": {"run": "y"}}, B, {"spookSchedule": SCHEDULE}, True), [])
    check("guard: SCHED with a key REF lacks at its identity value, allowed and listed", g({**SC, "larder": 0}, B, {"spookSchedule": SCHEDULE}, True), ["larder=0"])
    check("guard: runOffLoss 1 (identity) allowed", g({**SC, "runOffLoss": 1}, B, {"spookSchedule": SCHEDULE}, True), ["runOffLoss=1"])
    # bad: a guard that accepts runOffLoss 0 (as 52ef90a's accepted any value) lets the planted run through, so this fails
    try: r0 = guard({**SC, "runOffLoss": 0}, B, {"spookSchedule": SCHEDULE}, True, {**IDENTITY, "runOffLoss": 0} if bad else IDENTITY)
    except GuardFail: r0 = "stop"
    check("guard: runOffLoss 0 (loss by run-off off) stops", r0, "stop")
    check("guard: selfDoes 10 on SCHED stops", g({**SC, "selfDoes": 10}, B, {"spookSchedule": SCHEDULE}, True), "stop")
    check("guard: a key REF lacks with no identity value stops", g({**SC, "newThing": 0}, B, {"spookSchedule": SCHEDULE}, True), "stop")
    check("guard: SCHED with the attempt-1 schedule stops",
          g({**B, "spookSchedule": SCHEDULE.replace("0:0.00492", "0:0.00600")}, B, {"spookSchedule": SCHEDULE}, True), "stop")
    check("guard: spookFixed set stops", g({**SC, "spookFixed": 0.02}, B, {"spookSchedule": SCHEDULE}, True), "stop")
    check("guard: SCHEDT = SCHED but taper", g({**SC, "captureTaper": 1, "selfDoes": 10}, SC, {"captureTaper": 1, "selfDoes": 10}), [])
    check("guard: SCHEDT without selfDoes stops", g({**SC, "captureTaper": 1}, SC, {"captureTaper": 1, "selfDoes": 10}), "stop")
    T = {**SC, "captureTaper": 1, "selfDoes": 10}
    check("guard: REFT = SCHEDT but no schedule", g({**T, "spookSchedule": ""}, T, {"spookSchedule": ""}), [])
    check("guard: REFT with a schedule stops", g(T, T, {"spookSchedule": ""}), "stop")
    check("guard: REFT with another change stops", g({**T, "spookSchedule": "", "herdRange": 6}, T, {"spookSchedule": ""}), "stop")
    check("guard: REFT with a new key stops (within exp014 every key)", g({**T, "spookSchedule": "", "zz": 1}, T, {"spookSchedule": ""}), "stop")
    # closure count: strict below 0.05; None is not closed
    cs = [0.0, 0.01, 0.049, 0.02, 0.03, 0.04 if not bad else 0.05, 0.2, None]
    check("closure: csire 0.0-0.04 in 6 seeds is closed", closed_count([{"csire": c} for c in cs]) >= 6, True)
    check("closure: csire exactly 0.05 is not closed", closed_count([{"csire": 0.05}]), 0)
    # achieved rate on a planted run: herded 100 every row; ranOff 150 per row in 401-500, 50 per row from 3201
    rows = [{"year": y - 1, "herded": 100 if y > 400 else 0, "ranOff": (150 if 401 <= y <= 500 else 50 if y >= 3201 else 80) if y > 400 else 0,
             "refetched": 0, "escaped": 0} for y in range(1, 4001, 3)]
    d = {"years": rows}
    check("rate: planted 401-500 rate 1.5", round(rate(d, 401, 500)["ranOff"], 9), 1.5)
    check("rate: planted 3201-4000 rate 0.5", round(rate(d, 3201, 4000)["ranOff"], 9), 0.5)
    check("rate: no herd in 1-400 gives None", rate(d, 1, 400), None)
    # the 15% flag: SCHEDT / REFT in the window
    def Sf(t, r):
        cur = {c: (t, 0) for c in CENT}; cur[(3201, 4000)] = (t, 0); cr = {c: (r, 0) for c in CENT}; cr[(3201, 4000)] = (r, 0)
        return {"SCHEDT": {"curve": cur}, "REFT": {"curve": cr}}
    check("flag: 14% apart is not flagged", rate_flag(Sf(1.14, 1.0), (3201, 4000))[1], False)
    check("flag: 16% apart is flagged", rate_flag(Sf(1.16 if not bad else 1.14, 1.0), (3201, 4000))[1], True)
    check("flag: 16% below is flagged", rate_flag(Sf(0.84, 1.0), (3201, 4000))[1], True)
    check("flag: window centuries counted", rate_flag(Sf(1.2, 1.0), (3201, 4000))[3], 8)
    check("flag: all 36 centuries counted", rate_flag(Sf(1.2, 1.0), (3201, 4000))[4:6], (36, 36))
    check("flag: centuries with SCHEDT above REFT counted", rate_flag(Sf(1.2 if not bad else 0.84, 1.0), (3201, 4000))[6], 36)
    check("flag: none above when SCHEDT is below", rate_flag(Sf(0.84, 1.0), (3201, 4000))[6], 0)
    # branches from hand-made summaries
    def Sx(nT=8, closedT=7, gT=-0.4, gR=-0.6, nR=8, hcS=-0.3):
        mk = lambda nE, R, ncl, hc=-0.3: {"n": 8, "nE": nE, "read": nE >= 2, "R": (R, 0.02), "hc": (hc, 0.02), "wc": (0.01, 0.01),
                                          "nclosed": ncl, "closed": ncl >= 6}
        return {"SCHED": mk(8, -0.5, 0, hcS), "SCHEDT": mk(nT, gT, closedT), "REFT": mk(nR, gR, 8), "REF": mk(8, -0.6, 0)}
    above = {("SCHEDT", "REFT", "R"): (0.2, 0.1, 0.3, 8), ("SCHEDT", "REFT", "share"): (0.67, 8, [])}
    span = {("SCHEDT", "REFT", "R"): (0.05, -0.05, 0.15, 8)}
    fl_no, fl_yes = (1.05, False, [], 0), (1.30, True, [], 3)
    cases = [("1: closed, R gap -0.40", Sx(), above, fl_no, ["1"]),
             ("1 at the boundary -0.30", Sx(gT=-0.30), above, fl_no, ["1"]),
             ("2: closed, -0.20, REFT -0.60", Sx(gT=-0.2), above, fl_no, ["2"]),
             ("3: SCHEDT one established", Sx(nT=1), above, fl_no, ["3"]),
             ("not closed (5 of 8)", Sx(closedT=5 if not bad else 6), above, fl_no, ["not-closed"]),
             ("REFT above -0.30, SCHEDT -0.40 closed: 1 with the note", Sx(gR=-0.25), above, fl_no, ["REFT-above", "1"]),
             ("REFT above -0.30, SCHEDT -0.20 closed: note only", Sx(gT=-0.2, gR=-0.25), above, fl_no, ["REFT-above"]),
             ("REFT under 2 established: note", Sx(nR=1, gT=-0.2), above, fl_no, ["REFT-above"]),
             ("not closed, REFT above", Sx(closedT=2, gR=-0.1), above, fl_no, ["REFT-above", "not-closed"])]
    for name, S, C, fl, want in cases:
        _, V = read(S, C, fl); check("branch " + name, V["branches"], want)
    L, V = read(Sx(gT=-0.2), above, fl_yes)
    check("branch 2 with rates more than 15% apart says so", any("carries a rate difference too" in x for x in L), True)
    L, V = read(Sx(gT=-0.2), above, fl_no)
    check("branch 2 with rates within 15% does not", any("carries a rate difference too" in x for x in L), False)
    L, V = read(Sx(gR=-0.25), above, fl_no)
    check("share not read when REFT-above fires (branch 1 beside it)", (any("share of the filter: not read" in x for x in L),
          any("share of the filter (descriptive)" in x for x in L)), (True, False))
    L, V = read(Sx(), above, fl_no)
    check("share printed with branch 1 alone", any("share of the filter (descriptive)" in x for x in L), True)
    _, V = read(Sx(), above, fl_no); check("prediction 1 holds at 8 and 8", V["p1"], True)
    _, V = read(Sx(nT=5), above, fl_no); check("prediction 1 fails at SCHEDT 5", V["p1"], False)
    _, V = read(Sx(), above, fl_no); check("prediction 2 holds: -0.40, interval above 0", V["p2"], True)
    _, V = read(Sx(), span, fl_no); check("prediction 2 fails when the interval spans 0", V["p2"], False)
    _, V = read(Sx(gT=-0.2), above, fl_no); check("prediction 2 fails when SCHEDT is above -0.30", V["p2"], False)
    _, V = read(Sx(gR=0.05), above, fl_no); check("prediction 2 not read when REFT's gap is not negative", V["p2"], None)
    _, V = read(Sx(hcS=-0.2), above, fl_no); check("prediction 3 holds at -0.20", V["p3"], True)
    _, V = read(Sx(hcS=-0.19), above, fl_no); check("prediction 3 fails at -0.19", V["p3"], False)
    # the share: ratio of the means over seeds established in both
    mk = lambda R, e=True: {"R": R, "est": e}
    sh = share({"SCHEDT": {1: mk(-0.2), 2: mk(-0.4), 3: mk(-0.9, False)}, "REFT": {1: mk(-0.5), 2: mk(-0.7), 3: mk(-0.6)}})
    check("share: ratio of means over seeds established in both", (round(sh[0], 9), sh[1]), (0.5, 2))
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest(sys.argv[2:3] == ["bad"]) else 1)
    main()
