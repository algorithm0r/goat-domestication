# late_tab.py: the exp013 scorer, to the registration (9522ce9) as amended (f752422, amendment 2 37df366): late herding
# (humans 2900, herding 3000) for REF, LARD and TAPER, a no-human control WTlate, read at equal time since herding
# against the year-400 arms. Analysis session, 2026-11-21.
#   python tools/late_tab.py LATE_DIR "BASE_DIR;..." [--alias ARM=SRC,...] [--perseed] [--bad nooffset|guard]
#   python tools/late_tab.py selftest [bad]
# Every time is set from the run's own saved herdingAt h (amendment 1, the reviewer's 92a6acd point 3), so the year-400
# and the late arms go through the same code:
#   founders  h-99..h (301-400 | 2901-3000); window h+2801..h+3600 (3201-4000 | 5801-6600)
#   establishment: jump_tab's herd-size criterion (100-year mean herd >= 100 held 400 years), testable after h+100,
#     followed to the last row - 400; in years since herding; KM at 400..3600 years since herding
#   P1's spans: h-599..h-400 and h-299..h-100 (2401-2600 and 2701-2900); the settling year (registration) over rows to
#     h-100 (2900)
# Generation records are not read by this tool (exp013 registers none), so there is nothing of them to offset.
# Arms: REFlate, LARDlate, TAPERlate and WTlate (humansAt 1e9: no humans, no herd; spans from its own herdingAt 3000)
# from LATE_DIR; REF (exp005 + exp006), LARD and TAPER (exp011) from the base folders.
# Guard (real runs): each late arm against its year-400 run of the same seed (humansAt 2900, herdingAt 3000, ibdFrom 3000;
# base 300, 400, 400); WTlate against REFlate of the same seed (humansAt 1e9, nothing else); thinning (recordEvery,
# histPeriod, reportingPeriod) and logHistDepth may differ and are listed; keys the base lacks are listed; anything else
# stops. --alias maps an arm to another arm's files to test the tool (guard printed, not enforced): a test, not a result.
# Measures:
#   wild change wcw = window mean of the wild genotype mean (hist - histHerd, rows with wild goats) - founders' all-goat
#     mean (no herd goat in the founders; checked). It needs no herd, so WTlate has one; for an established seed whose
#     every window row has herd and wild goats it equals split_tab's wild change (checked, 1e-9).
#   gap, herd change hc, wild change wc (split_tab, identity checked), established seeds; breadth = core traits (9, as in
#     exp011) with abs(gap) >= 0.10, per-seed vote (exp011 amendment 2): diverged if 6 or more established seeds have
#     breadth >= 3, not if 6 or more do not, else mixed. Beside it, exploratory: herd-carried breadth (exp007's more-than-
#     half carrier) and the 8 NT_CORE traits' breadth.
#   P1 (amendments 1-2): (i) for every core trait the seed-mean all-goat wild in 2701-2900 within 0.02 of 2401-2600, read
#     on WTlate (it shares each seed's history to 2900; the late arms print beside); (ii) WTlate's wcw under 0.05 in size
#     on each of A, S, H, W (seed mean); its drift on the other core traits printed, deciding nothing.
#   P2 (amendment 1): human-caused wild change per late arm and trait (A, S, H, W) = wcw(late) - wcw(WTlate), paired by
#     seed, mean and 95% t interval; holds if abs(mean) < 0.05. Beside it, the burn-in's share: wcw(year-400 arm) -
#     wcw(late arm), unpaired.
#   Primary (amendment 1): per arm and trait (A, S, H, W), late gap - year-400 gap over established seeds, unpaired 8 v 8,
#     95% interval with SE = hypot(SE late, SE 400) and t at min(n) - 1 df (conservative); predicted abs(late gap) < 0.10
#     and the interval excluding 0, on A S H W in LARDlate and TAPERlate, A S in REFlate.
#   P3 (registration): LARDlate, TAPERlate: csire < 0.05 in 6 or more of the 8 seeds (a seed not established counts as not
#     closed) and abs(hc) > abs(wc) on every arm-mean trait at 0.10 (vacuous if none). P4: REFlate R gap <= -0.30, abs(hc) >
#     abs(wc).
# Decision rule (amendments 1-2): P1 fails -> the settling time goes to Chris. P1 holds -> per closed arm and trait
#   (A, S, H, W): human-caused change 0.05 or more -> the herd sheltered from human-driven selection on the wild (a model
#   result); under 0.05 -> late gap < 0.10 with the interval excluding 0: burn-in; late gap >= 0.10: herd divergence from a
#   settled wild; otherwise unresolved. Herding moves later if burn-in holds on any of A S H W in either closed arm.
#   Every branch: LARDlate and TAPERlate's plain-breadth vote; mixed is reported as mixed; if they disagree each is
#   reported alone and a claim about closure rests on what both show. REFlate's per-trait readings print, not governing.
import glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, flow_tab, jump_tab, inflow_tab
from exp007_tab import carried
CORE, TRAITS, mc, tcrit = split_tab.CORE, split_tab.TRAITS, split_tab.mc, inflow_tab.tcrit
CORE8 = ["R", "A", "S", "B", "H", "T", "M", "W"]   # NT_CORE (genome.js:34): the core traits without L
WILD4 = ["A", "S", "H", "W"]
ARMS = [("REFlate", "REF"), ("LARDlate", "LARD"), ("TAPERlate", "TAPER")]
CLOSED_ARMS = ["LARDlate", "TAPERlate"]
PRIMARY_TRAITS = {"LARDlate": WILD4, "TAPERlate": WILD4, "REFlate": ["A", "S"]}
WT = "WTlate"
LATE = {"humansAt": 2900, "herdingAt": 3000, "ibdFrom": 3000}
EARLY = {"humansAt": 300, "herdingAt": 400, "ibdFrom": 400}
THIN, OUTPUT_ONLY = {"recordEvery", "histPeriod", "reportingPeriod"}, {"logHistDepth"}
TOL, P1_WT, P2_TOL, GAP_TOL, CS_CLOSED, OVERSHOOT = 0.02, 0.05, 0.05, 0.10, 0.05, 0.05
KM_T = list(range(400, 3601, 400))

class GuardFail(Exception): pass

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def ci_paired(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2: return None
    m, se = ms(xs); t = tcrit(len(xs)); return m, m - t * se, m + t * se, len(xs)

def ci_unpaired(a, b):
    a, b = [x for x in a if x is not None], [x for x in b if x is not None]
    if len(a) < 2 or len(b) < 2: return None
    (ma, sa), (mb, sb) = ms(a), ms(b); se = math.hypot(sa, sb); t = tcrit(min(len(a), len(b)))
    return ma - mb, ma - mb - t * se, ma - mb + t * se, se

def frame(P, bad=None):
    h = 400 if bad == "nooffset" else P["herdingAt"]
    return {"h": h, "f0": h - 99, "f1": h, "y0": h + 2801, "y1": h + 3600, "test": h + 100,
            "p1a": (h - 599, h - 400), "p1b": (h - 299, h - 100), "pre": h - 100}

def guard(P, B, want, base_want):
    """Run parameters P against its base run B: keys in `want` must hold those values in P (and base_want in B); thinning
    and output-only keys are listed; keys B lacks are listed; anything else raises GuardFail."""
    eq = lambda a, b: a == b or (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= 1e-9)
    bad, out = [], []
    for k, v in want.items():
        if not eq(P.get(k), v): bad.append(f"{k} {P.get(k)} (want {v})")
    for k, v in base_want.items():
        if not eq(B.get(k), v): bad.append(f"base {k} {B.get(k)} (want {v})")
    for k in B:
        if k == "id" or k in want: continue
        if k not in P: bad.append(f"{k} missing (base {B[k]})")
        elif not eq(P[k], B[k]):
            if k in THIN | OUTPUT_ONLY: out.append(f"{k} {B[k]}->{P[k]}")
            else: bad.append(f"{k} {P[k]} (base {B[k]})")
    if bad: raise GuardFail(", ".join(bad))
    return out + [f"{k} added" for k in sorted(k for k in P if k not in B)]

def rows_in(d, a, b): return [i for i, y in enumerate(d["histYears"]) if a <= y + 1 <= b]

def allgoat_mean(d, a, b):
    """All-goat genotype mean per trait over the histogram rows in a..b (1-based); stops if a herd goat is in them."""
    rs = rows_in(d, a, b)
    if not rs: sys.exit(f"no histogram row in {a}-{b}")
    if any(sum(d["histHerd"]["R"][i]) for i in rs): sys.exit(f"herd goats in {a}-{b}, where the wild is read alone")
    return {t: sum(mc(d["hist"][t][i]) for i in rs) / len(rs) for t in TRAITS}

def wild_change(d, fr):
    F = allgoat_mean(d, fr["f0"], fr["f1"])
    out = {}
    for t in TRAITS:
        v = []
        for i in rows_in(d, fr["y0"], fr["y1"]):
            w = [x - z for x, z in zip(d["hist"][t][i], d["histHerd"][t][i])]
            if sum(w): v.append(mc(w))
        out[t] = sum(v) / len(v) - F[t] if v else None
    return out

def settle(d, end):
    """Per trait, the settling year: the start of the first century from which every century to the last (end-99..end)
    stays within 0.02 of the last; all-goat means over rows to `end` (no herd goat; checked)."""
    rs = [i for i, y in enumerate(d["histYears"]) if y + 1 <= end]
    if any(sum(d["histHerd"]["R"][i]) for i in rs): sys.exit("herd goats before the settling span ends")
    cents = end // 100; out = {}
    for t in TRAITS:
        by = [[] for _ in range(cents)]
        for i in rs:
            c = d["histYears"][i] // 100
            if c < cents: by[c].append(mc(d["hist"][t][i]))
        m = [sum(v) / len(v) if v else None for v in by]; ref = m[-1]; s = cents - 1
        while s > 0 and m[s - 1] is not None and all(abs(m[c] - ref) <= TOL for c in range(s - 1, cents)): s -= 1
        out[t] = 100 * s + 1
    return out

def core(d, bad=None):
    """Everything but gene flow. Separate so the selftest can plant runs. bad='nooffset' reads every time as if herding
    were at 400 and bypasses split_tab's founders guard, so the planted values themselves are compared."""
    P = d["_parameters"]; fr = frame(P, bad)
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > fr["test"]]
    J, end, falls, late = jump_tab.jump(hs, lambda v: v >= 100, 400)
    ds = d if bad != "nooffset" else {**d, "_parameters": {k: v for k, v in P.items() if k != "herdingAt"}}
    sp = split_tab.split(ds, fr["y0"], fr["y1"], fr["f0"], fr["f1"])
    yr = [r for r in d["years"] if fr["y0"] <= r["year"] + 1 <= fr["y1"]]
    r = {"fr": fr, "J": J, "Jrel": None if J is None else J - fr["h"], "end": end - fr["h"], "falls": falls, "late": late,
         "herd": sum(x.get("herded") or 0 for x in yr) / len(yr) if yr else 0.0, "hc": None, "wcw": wild_change(d, fr)}
    if sp:
        out, F, _ = sp
        r["hc"] = {t: out[t][0] for t in TRAITS}; r["wc"] = {t: out[t][1] for t in TRAITS}
        r["gap"] = {t: out[t][0] - out[t][1] for t in TRAITS}; r["F"] = F
        rs = rows_in(d, fr["y0"], fr["y1"])
        if all(sum(d["histHerd"]["R"][i]) and sum(d["hist"]["R"][i]) > sum(d["histHerd"]["R"][i]) for i in rs):
            bad_t = [t for t in TRAITS if abs(r["wcw"][t] - r["wc"][t]) > 1e-9]
            if bad_t: sys.exit("identity check failed: wild change from all rows != split_tab's wild change: " + ", ".join(bad_t))
        r["traits"] = [t for t in CORE if abs(r["gap"][t]) >= GAP_TOL]
        r["breadth"] = len(r["traits"]); r["b8"] = sum(1 for t in r["traits"] if t in CORE8)
        r["hcarry"] = {t: abs(r["hc"][t]) > abs(r["wc"][t]) for t in r["traits"]}
        r["carrier"] = {t: carried(r["gap"][t], r["hc"][t], r["wc"][t]) for t in r["traits"]}
        r["bherd"] = sum(1 for c in r["carrier"].values() if c == "herd")
    pre = min(P["humansAt"], fr["pre"]) if bad != "nooffset" else 300
    if pre >= 1000 and fr["p1a"][0] >= 1:
        a, b = allgoat_mean(d, *fr["p1a"]), allgoat_mean(d, *fr["p1b"])
        r["p1"] = {t: b[t] - a[t] for t in TRAITS}; r["settle"] = settle(d, fr["pre"])
    else: r["p1"], r["settle"] = None, None
    return r

def score(f, bad=None):
    d = json.load(open(f, encoding="utf-8")); r = core(d, bad)
    fr = r["fr"]; r["flow"] = flow_tab.run_flow(d, fr["y0"], fr["y1"]) or {}; r["P"] = d["_parameters"]
    return r

def vote(n, of): return "diverged" if n >= 6 else "not" if of - n >= 6 else "mixed"

def summary(runs):
    E = [r for r in runs if r["J"] is not None and r["hc"]]
    v = {"n": len(runs), "nE": len(E), "E": E, "runs": runs, "read": len(E) >= 2,
         "win100": sum(1 for r in runs if r["herd"] >= 100), "herd": ms([r["herd"] for r in runs])[0],
         "late": sum(1 for r in runs if r["late"]), "falls": sum(r["falls"] for r in runs)}
    v["km"] = {t: jump_tab.km([(r["Jrel"], r["end"]) for r in runs], t) for t in KM_T}
    v["Jmed"] = sorted(r["Jrel"] for r in E)[(len(E) - 1) // 2] if E else None
    v["wcw"] = {t: ms([r["wcw"][t] for r in runs]) for t in TRAITS}
    if E:
        v["gap"] = {t: ms([r["gap"][t] for r in E]) for t in TRAITS}
        v["hc"] = {t: ms([r["hc"][t] for r in E]) for t in TRAITS}
        v["wc"] = {t: ms([r["wc"][t] for r in E]) for t in TRAITS}
        g0 = {t: v["gap"][t][0] for t in CORE}
        v["traits"] = [t for t in CORE if abs(g0[t]) >= GAP_TOL]; v["breadth"] = len(v["traits"])
        v["b8"] = sum(1 for t in v["traits"] if t in CORE8)
        v["hcarry"] = {t: abs(v["hc"][t][0]) > abs(v["wc"][t][0]) for t in v["traits"]}
        v["carrier"] = {t: carried(g0[t], v["hc"][t][0], v["wc"][t][0]) for t in v["traits"]}
        v["ndiv"] = sum(1 for r in E if r["breadth"] >= 3); v["div"] = vote(v["ndiv"], len(E))
        v["n8"] = sum(1 for r in E if r["b8"] >= 3); v["nherd3"] = sum(1 for r in E if r["bherd"] >= 3)
    v["flow"] = {k: ms([r["flow"].get(k) for r in E]) for k in ("capt", "csire", "cdam", "depth", "feral")}
    v["nclosed"] = sum(1 for r in E if r["flow"].get("csire") is not None and r["flow"]["csire"] < CS_CLOSED)
    v["nclosed11"] = sum(1 for r in E if (r["flow"].get("depth") or 0) >= 10 and r["flow"].get("csire") is not None and r["flow"]["csire"] <= 0.10)
    P1 = [r for r in runs if r["p1"]]
    v["p1"] = {t: ms([r["p1"][t] for r in P1])[0] for t in TRAITS} if P1 else None
    v["settle"] = {t: [r["settle"][t] for r in P1] for t in TRAITS} if P1 else None
    return v

def tests(S, R):
    """The registered quantities from the arm summaries and runs: P1, P2 (paired), the primary (unpaired), the burn-in's
    share, and what P3, P4 and the rule read. A plain dict, so the selftest can plant one."""
    T = {"p1": S[WT]["p1"] if WT in S else None, "wt": {t: S[WT]["wcw"][t][0] for t in TRAITS} if WT in S else None,
         "p2": {}, "prim": {}, "burn": {}, "arms": {}, "shared": None, "p1arms": {}}
    wt = {r["seed"]: r for r in R.get(WT, [])}
    # clarification 2: P1 is read on WTlate if every late run shares its seed's pre-2900 history (its P1 span changes equal
    # WTlate's); if any does not, P1's span clause is read on each late arm separately as well
    late = [r for a, _ in ARMS if a in R for r in R[a] if r["p1"]]
    if wt and late: T["shared"] = all(r["seed"] in wt and r["p1"] == wt[r["seed"]]["p1"] for r in late)
    T["p1arms"] = {a: S[a]["p1"] for a, _ in ARMS if a in S and S[a]["p1"]}
    for arm, base in ARMS:
        if arm not in S: continue
        s = S[arm]
        T["arms"][arm] = {"read": s["read"], "nE": s["nE"], "n": s["n"], "nclosed": s["nclosed"], "ndiv": s.get("ndiv"),
                          "div": s.get("div"), "traits": s.get("traits", []), "hcarry": s.get("hcarry", {}),
                          "gap": {t: s["gap"][t][0] for t in TRAITS} if s["read"] else None,
                          "hc": {t: s["hc"][t][0] for t in TRAITS} if s["read"] else None,
                          "wc": {t: s["wc"][t][0] for t in TRAITS} if s["read"] else None}
        if wt: T["p2"][arm] = {t: ci_paired([r["wcw"][t] - wt[r["seed"]]["wcw"][t] for r in R[arm] if r["seed"] in wt]) for t in WILD4}
        if base in S:
            T["prim"][arm] = {t: ci_unpaired([r["gap"][t] for r in S[arm]["E"]], [r["gap"][t] for r in S[base]["E"]]) for t in WILD4}
            T["burn"][arm] = {t: ci_unpaired([r["wcw"][t] for r in R[base]], [r["wcw"][t] for r in R[arm]]) for t in WILD4}
    return T

def read(T):
    """Predictions and the decision rule (as amended) from tests(). Returns (lines, verdicts)."""
    L, V = [], {}
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"
    iv = lambda c: "-" if c is None else f"{c[0]:+.3f} [{c[1]:+.3f}, {c[2]:+.3f}]"
    span = lambda p: p is not None and all(abs(p[t]) <= TOL for t in CORE)
    p1a = span(T["p1"])
    if T.get("shared") is False:   # clarification 2: a late arm that does not share the history is read on its own spans too
        V["p1arms"] = {a: span(p) for a, p in T["p1arms"].items()}; p1a = p1a and all(V["p1arms"].values())
    p1b = T["wt"] is not None and all(T["wt"][t] is not None and abs(T["wt"][t]) < P1_WT for t in WILD4)
    V["p1"] = p1a and p1b
    L.append(f"1. the wild settled before humans: {'met' if V['p1'] else 'not met'}"
             + {None: "", True: " (late arms share WTlate's history to 2900: read on WTlate's 8 histories)",
                False: " (a late arm does NOT share WTlate's history: span clause read on WTlate and on each late arm: "
                       + ", ".join(f"{a} {'yes' if v else 'no'}" for a, v in V.get("p1arms", {}).items()) + ")"}[T.get("shared")])
    L.append(f"   (i) WTlate seed-mean wild, 2701-2900 minus 2401-2600, within {TOL} on every core trait: {'yes' if p1a else 'no'} ("
             + (", ".join(f"{t} {f3(T['p1'][t])}" for t in CORE) if T["p1"] else "no WTlate record") + ")")
    L.append(f"   (ii) WTlate's wild change 2901-3000 -> 5801-6600 under {P1_WT} on A S H W: {'yes' if p1b else 'no'} ("
             + (", ".join(f"{t} {f3(T['wt'][t])}" for t in WILD4) if T["wt"] else "no WTlate") + "); other core traits, deciding nothing: "
             + (", ".join(f"{t} {f3(T['wt'][t])}" for t in CORE if t not in WILD4) if T["wt"] else "-"))
    V["p2"] = {}
    for arm in T["arms"]:
        c = T["p2"].get(arm)
        V["p2"][arm] = {t: c[t] is not None and abs(c[t][0]) < P2_TOL for t in WILD4} if c else None
    V["p2all"] = bool(T["p2"]) and all(V["p2"][a] and all(V["p2"][a].values()) for a in T["arms"])
    L.append(f"2. human-caused wild change (late - WTlate, paired by seed) under {P2_TOL} on A S H W in every late arm: {'met' if V['p2all'] else 'not met'}")
    for arm in T["arms"]:
        c = T["p2"].get(arm)
        L.append(f"   {arm}: " + (", ".join(f"{t} {iv(c[t])}" for t in WILD4) if c else "no WTlate pairing"))
    V["prim"] = {}
    L.append("Primary: late gap - year-400 gap (unpaired, 95% interval), predicted abs(late gap) < 0.10 with the interval excluding 0")
    for arm, ts in PRIMARY_TRAITS.items():
        a = T["arms"].get(arm); c = T["prim"].get(arm)
        if not a or not a["read"] or not c: L.append(f"   {arm}: not read"); continue
        V["prim"][arm] = {t: c[t] is not None and abs(a["gap"][t]) < GAP_TOL and (c[t][1] > 0 or c[t][2] < 0) for t in ts}
        L.append(f"   {arm}: " + ", ".join(f"{t} late {f3(a['gap'][t])}, diff {iv(c[t])} {'met' if V['prim'][arm][t] else 'not met'}" for t in ts))
    V["p3"] = {}
    for arm in CLOSED_ARMS:
        a = T["arms"].get(arm)
        if not a: continue
        closed = a["nclosed"] >= 6; carry = a["read"] and all(a["hcarry"].values())
        V["p3"][arm] = closed and carry
        V.setdefault("p3label", {})[arm] = ("met (vacuous)" if a["read"] and not a["traits"] else "met") if V["p3"][arm] else "not met"
        L.append(f"3. {arm}: csire < {CS_CLOSED} in >= 6 of 8 and abs(hc) > abs(wc) on every trait at 0.10: {V['p3label'][arm]} "
                 f"(closed {a['nclosed']} of {a['n']}; " + ((", ".join(f"{t} hc {f3(a['hc'][t])} wc {f3(a['wc'][t])}" for t in a["traits"]) or "no trait at 0.10: vacuous") if a["read"] else "not read") + ")")
    a = T["arms"].get("REFlate")
    V["p4"] = bool(a and a["read"] and a["gap"]["R"] <= -0.30 and abs(a["hc"]["R"]) > abs(a["wc"]["R"]))
    L.append(f"4. REFlate R gap <= -0.30, herd-carried: {'met' if V['p4'] else 'not met'}" + (f" (R {f3(a['gap']['R'])}, hc {f3(a['hc']['R'])}, wc {f3(a['wc']['R'])})" if a and a["read"] else ""))
    L.append("\nDecision rule (as amended, f752422 and 37df366):"); V["d"] = {}; V["replan"] = False
    if not V["p1"]:
        V["d"] = "settling"; L.append("- P1 fails: the wild's settling time on this code goes to Chris before any later design.")
    else:
        for arm in CLOSED_ARMS + ["REFlate"]:
            a = T["arms"].get(arm); c2 = T["p2"].get(arm); cp = T["prim"].get(arm)
            if not a or not a["read"] or not c2 or not cp: L.append(f"- {arm}: not read"); continue
            if arm in CLOSED_ARMS and a["nclosed"] < 6: L.append(f"- {arm}: not closed ({a['nclosed']} of {a['n']}); read below for the record")
            V["d"][arm] = {}
            for t in WILD4:
                if c2[t] is None or cp[t] is None: V["d"][arm][t] = "not read"; continue
                if abs(c2[t][0]) >= P2_TOL: k = "human"
                # burn-in also needs the gap to have shrunk (clarification 2, 810d5e6 and d72a69a): abs(late gap) <
                # abs(year-400 gap), and not an overshoot through zero: a late gap of the opposite sign 0.05 or more in size
                # reads unresolved (year-400 gap = late gap - difference)
                elif abs(a["gap"][t]) < GAP_TOL and (cp[t][1] > 0 or cp[t][2] < 0) and shrunk(a["gap"][t], a["gap"][t] - cp[t][0]): k = "burn-in"
                elif abs(a["gap"][t]) >= GAP_TOL: k = "herd"
                else: k = "unresolved"
                V["d"][arm][t] = k
            words = {"human": "humans move the wild; the gap is the herd sheltered from human-driven selection (a model result)",
                     "burn-in": "the year-400 gap was the burn-in's settling", "herd": "herd divergence from a settled wild",
                     "unresolved": "unresolved (late gap under 0.10, interval includes 0)", "not read": "not read"}
            L.append(f"- {arm}" + (" (not governing)" if arm not in CLOSED_ARMS else "") + ": " + "; ".join(f"{t} {words[V['d'][arm][t]]}" for t in WILD4))
        # amendment 2: "either closed arm"; an arm under 6 closed seeds does not trigger (the reviewer's 74b70f3 point 2)
        isc = lambda a: a in T["arms"] and T["arms"][a]["nclosed"] >= 6
        V["replan"] = any(isc(a) and V["d"].get(a, {}).get(t) == "burn-in" for a in CLOSED_ARMS for t in WILD4)
        L.append("- " + ("the burn-in reading holds on " + ", ".join(f"{a} {t}" for a in CLOSED_ARMS for t in WILD4 if isc(a) and V["d"].get(a, {}).get(t) == "burn-in")
                         + ": the re-plan moves herding to after the wild settles, for every arm" if V["replan"]
                         else "the burn-in reading holds on no trait of either closed arm"))
    votes = {a: T["arms"][a]["div"] for a in CLOSED_ARMS if a in T["arms"] and T["arms"][a]["read"]}
    V["votes"] = votes
    L.append("- plain breadth (per-seed vote), every branch: " + (", ".join(f"{a} {v} ({T['arms'][a]['ndiv']} of {T['arms'][a]['nE']})" for a, v in votes.items()) or "not read")
             + ("; they disagree: each is reported alone, and a claim about closure rests only on what both show" if len(set(votes.values())) > 1 else ""))
    return L, V

def shrunk(late, early):
    """Clarification 2 (d72a69a): the gap shrank, abs(late) < abs(early), without an overshoot through zero of 0.05 or more."""
    return abs(late) < abs(early) and not (late * early < 0 and abs(late) >= OVERSHOOT)

def files(folders):
    F = {}
    for folder in folders:
        if "exp012" in folder: sys.exit("refusing an exp012 folder")
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(2)) in F.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                F[m.group(1)][int(m.group(2))] = f
    return F

def main():
    a = sys.argv[1:]; alias = {}; bad = None; per = "--perseed" in a
    if per: a.remove("--perseed")
    if "--alias" in a: i = a.index("--alias"); alias = dict(x.split("=") for x in a[i + 1].split(",")); del a[i:i + 2]
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    Lf, Bf = files([a[0]]), files(a[1].split(";"))
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not exp013 results ***")
    S, R = {}, {}
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"
    u = lambda x: "-" if x is None else f"{x:.3f}"
    def load(arm, base, pool, want, base_want, basefiles):
        src = alias.get(arm, arm); pool = Bf if arm in alias else Lf
        if src not in pool: print(f"{arm}: no runs ({src})"); return
        rs, notes = [], set()
        for s, fn in sorted(pool[src].items()):
            if s not in basefiles:
                if arm in alias: continue
                sys.exit(f"{arm} seed {s}: no {base} run of that seed")
            r = score(fn, bad if arm != WT else None); r["seed"] = s
            Bp = json.load(open(basefiles[s], encoding="utf-8"))["_parameters"]
            P = dict(r["P"])
            if bad == "guard": P["offtakeRate"] = (P.get("offtakeRate") or 0) + 0.01   # a planted parameter difference
            try: notes.update(guard(P, Bp, want, base_want))
            except GuardFail as e:
                if arm in alias: notes.add(f"(guard, not enforced on an alias: {e})")
                else: sys.exit(f"parameter guard: {arm} seed {s}: {e}")
            rs.append(r)
        S[arm], R[arm] = summary(rs), rs
        print(f"{arm}: guard against {base}; listed: {', '.join(sorted(notes)) or 'none'}")
    for arm, base in ARMS:
        if base not in Bf: sys.exit(f"{arm}: no base arm {base} in the base folders")
        load(arm, base, None, LATE, EARLY, Bf[base])
    reff = (Bf.get(alias["REFlate"]) if "REFlate" in alias else Lf.get("REFlate")) or {}
    if WT in alias or WT in Lf: load(WT, "REFlate", None, {"humansAt": 1e9, "herdingAt": 3000, "ibdFrom": 3000}, LATE, reff)
    for _, base in ARMS:
        rs = []
        for s, fn in sorted(Bf[base].items()): r = score(fn); r["seed"] = s; rs.append(r)
        S[base], R[base] = summary(rs), rs
    order = [x for p in ARMS for x in p] + [WT]; show = [x for x in order if x in S]
    print("\nTimes from each run's herdingAt h: founders h-99..h, window h+2801..h+3600, establishment after h+100 (years since h).")
    print("| arm | h | seeds | established | KM at 400 / 800 / 1600 / 3200 | lower median of established (y since h) | late | herd>=100 in window | herd | breadth | traits | per-seed breadth >= 3 | depth | csire | csire < 0.05 | closed (exp011 def) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    km = lambda v, t: "-" if v["km"][t][0] is None else f"{v['km'][t][0]:.2f}"
    for arm in show:
        v = S[arm]; h = R[arm][0]["fr"]["h"]
        print(f"| {arm} | {h} | {v['n']} | {v['nE']} | {' / '.join(km(v, t) for t in (400, 800, 1600, 3200))} | {v['Jmed'] if v['Jmed'] is not None else '-'} | "
              f"{v['late']} | {v['win100']} | {v['herd']:.1f} | " + (f"{v['breadth']} | {' '.join(v['traits']) or '-'} | {v['ndiv']} of {v['nE']} ({v['div']}) | " if v["read"] else "- | - | - | ")
              + f"{u(v['flow']['depth'][0])} | {u(v['flow']['csire'][0])} | {v['nclosed']} of {v['n']} | {v['nclosed11']} of {v['nE']} |")
    print("\nPer trait, established seeds, arm mean: gap / herd change / wild change (split_tab) (SE of the gap)")
    print("| arm | " + " | ".join(TRAITS) + " |\n|---|" + "---|" * len(TRAITS))
    for arm in show:
        v = S[arm]
        if v["read"]: print(f"| {arm} | " + " | ".join(f"{f3(v['gap'][t][0])} / {f3(v['hc'][t][0])} / {f3(v['wc'][t][0])} ({v['gap'][t][1]:.3f})" for t in TRAITS) + " |")
    print("\nWild change from founders to window, all seeds (wcw: needs no herd), seed mean (SE)")
    print("| arm | " + " | ".join(TRAITS) + " |\n|---|" + "---|" * len(TRAITS))
    for arm in show: print(f"| {arm} | " + " | ".join(f"{f3(S[arm]['wcw'][t][0])} ({u(S[arm]['wcw'][t][1])})" for t in TRAITS) + " |")
    T = tests(S, R)
    print("\nThe burn-in's share: year-400 arm wild change - late arm wild change (unpaired), A S H W:")
    iv = lambda c: "-" if c is None else f"{c[0]:+.3f} [{c[1]:+.3f}, {c[2]:+.3f}]"
    for arm in T["burn"]: print(f"  {arm}: " + ", ".join(f"{t} {iv(T['burn'][arm][t])}" for t in WILD4))
    # exploratory (the reviewer's 5df38b3; added after exp013 was scored, read by no prediction or rule): absolute window
    # means over split's rows, herd = founders + herd change, wild = founders + wild change, established seeds; late arm
    # against its year-400 arm, unpaired 95% interval (SE hypot, t at min(n) - 1 df), with the founders beside
    print("\nEXPLORATORY (added after scoring; no prediction or rule reads it): absolute genotype means in the window, established"
          " seeds, late arm - year-400 arm, unpaired [95% interval]; herd | wild | founders (h-99..h), with each arm's mean")
    for arm, base in ARMS:
        if arm in S and base in S and S[arm]["read"] and S[base]["read"]:
            for lab, get in (("herd", lambda r, t: r["F"][t] + r["hc"][t]), ("wild", lambda r, t: r["F"][t] + r["wc"][t]), ("founders", lambda r, t: r["F"][t])):
                cells = []
                for t in WILD4:
                    a, b = [get(r, t) for r in S[arm]["E"]], [get(r, t) for r in S[base]["E"]]
                    c = ci_unpaired(a, b)
                    cells.append(f"{t} {ms(a)[0]:.3f} v {ms(b)[0]:.3f}: {iv(c)}")
                print(f"  {arm} - {base}, {lab}: " + "; ".join(cells))
    # how many histories P1 rests on: WTlate's seeds; the late arms add none where their pre-2900 span means equal WTlate's
    if WT in R:
        wts = {r["seed"]: r["p1"] for r in R[WT] if r["p1"]}
        same = {s: all(r["p1"] == p for a, _ in ARMS if a in R for r in R[a] if r["seed"] == s and r["p1"]) for s, p in wts.items()}
        nlate = sum(1 for a, _ in ARMS if a in R for r in R[a] if r["p1"])
        print(f"\nP1 rests on WTlate's {len(wts)} seeds (histories). Late arms' P1 span changes equal WTlate's, seed by seed: "
              + (", ".join(f"s{s} {'yes' if v else 'NO'}" for s, v in same.items()) or "no pre-human record")
              + (f" -> the {nlate} late runs add no history: n = {len(wts)}, not {len(wts) + nlate}" if same and all(same.values()) and nlate else
                 f" -> histories differ before 2900 in some seed: the shared-history premise fails there" if same and nlate else ""))
    print("\nBefore humans (rows to h-100): 2701-2900 minus 2401-2600, seed mean, and the settling year per trait (seed values)")
    for arm in show:
        v = S[arm]
        if v["p1"]: print(f"  {arm}: " + ", ".join(f"{t} {f3(v['p1'][t])}" for t in CORE) + " | settling " + "; ".join(f"{t} {'/'.join(str(x) for x in v['settle'][t])}" for t in CORE))
    print("\nEXPLORATORY (not registered): exp007's more-than-half carrier, herd-carried breadth, 8-trait (NT_CORE) breadth")
    print("| arm | traits (carrier) | herd-carried | seeds herd-carried >= 3 | 8-trait | seeds 8-trait >= 3 |\n|---|---|---|---|---|---|")
    for arm in show:
        v = S[arm]
        if v["read"]: print(f"| {arm} | {', '.join(f'{t} {c}' for t, c in v['carrier'].items()) or 'none'} | {sum(1 for c in v['carrier'].values() if c == 'herd')} | {v['nherd3']} of {v['nE']} | {v['b8']} | {v['n8']} of {v['nE']} |")
    if per:
        print("\n| arm | seed | J (y since h) | late | herd | breadth | traits | herd-carried (abs hc > abs wc) | csire | depth | R gap | wcw A S H W |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for arm in show:
            for r in R[arm]:
                print(f"| {arm} | {r['seed']} | {r['Jrel'] if r['Jrel'] is not None else '-'} | {r['late'] or '-'} | {r['herd']:.1f} | "
                      + (f"{r['breadth']} | {' '.join(r['traits']) or '-'} | {' '.join(t for t, x in r['hcarry'].items() if x) or '-'} | " if r["hc"] else "- | - | - | ")
                      + f"{u(r['flow'].get('csire'))} | {u(r['flow'].get('depth'))} | {f3(r['gap']['R']) if r['hc'] else '-'} | {' '.join(f3(r['wcw'][t]) for t in WILD4)} |")
    print("\nPredictions (registered 9522ce9, amended f752422 and 37df366):")
    L, _ = read(T)
    for line in L: print(line)

def planted(h, humans, Y=None, wild_at=2000, herd=True):
    """A synthetic run: histograms every 25 years, year rows every 5. The wild sits at bucket 8 (0.425) to year wild_at
    and at bucket 10 (0.525) after; with herd, 200 herd goats from h+1 (when humans < 1e8), at bucket 10 on every trait
    but R (bucket 4, 0.225)."""
    Y = Y or (6600 if h > 1000 else 4000)
    hy = list(range(24, Y, 25)); d = {"_parameters": {"herdingAt": h, "humansAt": humans}, "histYears": hy,
                                     "hist": {t: [] for t in TRAITS}, "histHerd": {t: [] for t in TRAITS}, "years": []}
    hz = herd and humans < 1e8
    for y in hy:
        wb = 10 if y + 1 > wild_at else 8
        for t in TRAITS:
            w = [0] * 20; w[wb] = 300; hh = [0] * 20
            if hz and y + 1 > h: hh[4 if t == "R" else 10] = 200
            d["hist"][t].append([a + b for a, b in zip(w, hh)]); d["histHerd"][t].append(hh)
    d["years"] = [{"year": y, "herded": 200 if hz and y + 1 > h else 0} for y in range(4, Y, 5)]
    return d

def selftest(bad=False):
    ok = True
    def check(name, got, want):
        nonlocal ok; res = got == want; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} {name}" + ("" if res else f": got {got}, want {want}"))
    rd = lambda x: None if x is None else round(x, 3)
    # a planted late run (herding 3000, humans 2900; the wild moves at 2000, settled after): established 105 years after
    # herding, founders 0.525, no wild change, R gap -0.30 herd-carried, breadth 1, P1 span change 0, settled from 2001.
    # With the offset removed (bad; split_tab's founders guard bypassed, so values are compared) it reads 2650 years,
    # founders 0.425, wild change +0.10 and no pre-human record.
    r = core(planted(3000, 2900), "nooffset" if bad else None)
    check("planted late run, times from herdingAt",
          (r["Jrel"], rd(r["F"]["A"]), rd(r["wc"]["A"]), rd(r["wcw"]["A"]), rd(r["gap"]["R"]), r["breadth"], r["hcarry"],
           None if r["p1"] is None else rd(r["p1"]["A"]), None if r["settle"] is None else r["settle"]["A"]),
          (105, 0.525, 0.0, 0.0, -0.3, 1, {"R": True}, 0.0, 2001))
    r = core(planted(400, 300))
    check("planted year-400 run", (r["Jrel"], rd(r["F"]["A"]), rd(r["wc"]["A"]), rd(r["wcw"]["A"]), r["p1"]), (105, 0.425, 0.1, 0.1, None))
    # a planted WTlate (no humans, herdingAt 3000): no herd, wild change read without one; a wild still moving at 2700
    # fails P1's span test (2701-2900 against 2401-2600: +0.1)
    r = core(planted(3000, 1e9))
    check("planted WTlate", (r["J"], r["hc"], rd(r["wcw"]["A"]), rd(r["p1"]["A"]), r["settle"]["A"]), (None, None, 0.0, 0.0, 2001))
    r = core(planted(3000, 1e9, wild_at=2700))
    check("planted WTlate, wild moving at 2700", (rd(r["p1"]["A"]), r["settle"]["A"]), (0.1, 2701))
    # the guard
    B = {"id": 1, "seed": 1, "humansAt": 300, "herdingAt": 400, "ibdFrom": 400, "recordEvery": 3, "histPeriod": 15, "offtakeRate": 0.15}
    P = dict(B, id=2, humansAt=2900, herdingAt=3000, ibdFrom=3000, recordEvery=5, histPeriod=25, cInitLo=0)
    check("guard passes, listing thinning and an added key", sorted(guard(P, B, LATE, EARLY)), ["cInitLo added", "histPeriod 15->25", "recordEvery 3->5"])
    for name, Q in (("another parameter", dict(P, offtakeRate=0.2)), ("herdingAt 2000", dict(P, herdingAt=2000)), ("a missing key", {k: v for k, v in P.items() if k != "offtakeRate"})):
        try: guard(Q, B, LATE, EARLY); check(f"guard stops on {name}", "passed", "stopped")
        except GuardFail: check(f"guard stops on {name}", "stopped", "stopped")
    W = dict(P, humansAt=1e9)
    check("WTlate guard against REFlate passes", guard(W, P, {"humansAt": 1e9, "herdingAt": 3000, "ibdFrom": 3000}, LATE), [])
    # the reading, from planted tests() dicts: per trait gap, P2 interval and primary interval
    def T(p1=0.0, wt=0.0, arms=None):
        out = {"p1": {t: p1 for t in TRAITS}, "wt": {t: wt for t in TRAITS}, "p2": {}, "prim": {}, "burn": {}, "arms": {}}
        for arm, (gaps, p2, prim, nclosed, ndiv) in (arms or {}).items():
            out["arms"][arm] = {"read": True, "nE": 8, "n": 8, "nclosed": nclosed, "ndiv": ndiv, "div": vote(ndiv, 8),
                                "traits": [t for t in CORE if abs(gaps.get(t, 0.0)) >= 0.10], "hcarry": {t: True for t in CORE if abs(gaps.get(t, 0.0)) >= 0.10},
                                "gap": {t: gaps.get(t, 0.0) for t in TRAITS}, "hc": {t: gaps.get(t, 0.0) for t in TRAITS}, "wc": {t: 0.0 for t in TRAITS}}
            out["p2"][arm] = {t: (p2.get(t, 0.0), p2.get(t, 0.0) - 0.02, p2.get(t, 0.0) + 0.02, 8) for t in WILD4}
            out["prim"][arm] = {t: (prim.get(t, -0.1), prim.get(t, -0.1) - 0.05, prim.get(t, -0.1) + 0.05, 0.02) for t in WILD4}
        return out
    # LARDlate: A burn-in (late 0.02, diff -0.10), S herd divergence (late 0.15), H human (P2 0.06), W unresolved (late
    # 0.05, diff -0.03, interval includes 0). TAPERlate: all burn-in, breadth vote not; LARDlate diverged -> disagree.
    t1 = T(arms={"LARDlate": ({"A": 0.02, "S": 0.15, "H": 0.0, "W": 0.05, "T": 0.3, "B": -0.2}, {"H": 0.06}, {"W": -0.03}, 8, 8),
                 "TAPERlate": ({"A": 0.01}, {}, {}, 8, 0), "REFlate": ({"R": -0.6, "A": 0.01, "S": 0.02}, {}, {}, 1, 8)})
    want = ({"LARDlate": {"A": "burn-in", "S": "herd", "H": "human", "W": "unresolved"},
             "TAPERlate": {t: "burn-in" for t in WILD4}, "REFlate": {t: "burn-in" for t in WILD4}}, True, True, False,
            {"LARDlate": "diverged", "TAPERlate": "not"})
    if bad: want = ({**want[0], "LARDlate": {**want[0]["LARDlate"], "W": "burn-in"}},) + want[1:]
    _, V = read(t1)
    check("per-trait branches, re-plan, P1 met, P2 fails on H, votes disagree", (V["d"], V["replan"], V["p1"], V["p2all"], V["votes"]), want)
    _, V = read(T(p1=0.03, arms={"LARDlate": ({"A": 0.02}, {}, {}, 8, 0)}))
    check("P1 fails on the span test -> settling to Chris", (V["p1"], V["d"]), (False, "settling"))
    _, V = read(T(wt=0.06, arms={"LARDlate": ({"A": 0.02}, {}, {}, 8, 0)}))
    check("P1 fails on WTlate's drift -> settling to Chris", (V["p1"], V["d"]), (False, "settling"))
    _, V = read(T(arms={"LARDlate": ({"A": 0.15, "S": 0.12, "H": 0.11, "W": 0.0}, {}, {}, 8, 5), "TAPERlate": ({}, {"A": 0.07, "S": 0.08, "H": 0.06, "W": 0.05}, {}, 8, 5)}))
    check("herd divergence, human-driven, burn-in on W alone still re-plans; mixed votes",
          (V["d"]["LARDlate"], V["d"]["TAPERlate"], V["replan"], V["votes"]),
          ({"A": "herd", "S": "herd", "H": "herd", "W": "burn-in"}, {t: "human" for t in WILD4}, True, {"LARDlate": "mixed", "TAPERlate": "mixed"}))
    _, V = read(t1)
    check("primary prediction per trait", V["prim"], {"LARDlate": {"A": True, "S": False, "H": True, "W": False},
                                                       "TAPERlate": {t: True for t in WILD4}, "REFlate": {"A": True, "S": True}})
    # direction (74b70f3 point 1): late gap -0.09, difference -0.08 [-0.13, -0.03]: the year-400 gap was -0.01, so the gap
    # grew; not burn-in but unresolved. Re-plan (point 2): LARDlate's burn-in on A does not count with 3 closed seeds.
    _, V = read(T(arms={"LARDlate": ({"A": 0.02}, {}, {}, 3, 0), "TAPERlate": ({"A": -0.09}, {"S": 0.06, "H": 0.06, "W": 0.06}, {"A": -0.08}, 8, 0)}))
    check("a gap that grew is not burn-in; an unclosed arm does not re-plan",
          (V["d"]["TAPERlate"]["A"], V["d"]["LARDlate"]["A"], V["replan"]), ("unresolved", "burn-in", False))
    # clarification 2 (d72a69a): an overshoot through zero. Year-400 -0.105 to late +0.09 (difference +0.195 [+0.145,
    # +0.245]) reads unresolved; to late +0.03 (under 0.05 the other side, +0.135 [+0.085, +0.185]) it reads burn-in.
    # P3 met only because no trait reaches 0.10 prints "met (vacuous)" (the reviewer's 4d3ba9c).
    _, V = read(T(arms={"LARDlate": ({"A": 0.09, "S": 0.03}, {}, {"A": 0.195, "S": 0.135}, 8, 0), "TAPERlate": ({"T": 0.3}, {}, {}, 8, 0)}))
    check("overshoot through zero 0.05 or more is unresolved, under 0.05 burn-in; P3 vacuous label",
          (V["d"]["LARDlate"]["A"], V["d"]["LARDlate"]["S"], V["p3label"]), ("unresolved", "burn-in", {"LARDlate": "met (vacuous)", "TAPERlate": "met"}))
    # clarification 2: a late arm not sharing WTlate's history is read on its own spans too
    t2 = T(arms={"LARDlate": ({"A": 0.02}, {}, {}, 8, 0)}); t2["shared"] = False; t2["p1arms"] = {"LARDlate": {t: 0.03 for t in TRAITS}}
    _, V = read(t2)
    check("history not shared: a late arm's own span fails P1", (V["p1"], V["p1arms"], V["d"]), (False, {"LARDlate": False}, "settling"))
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest(sys.argv[2:3] == ["bad"]) else 1)
    main()
