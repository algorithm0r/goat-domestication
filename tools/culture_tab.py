# culture_tab.py: the herder-culture rules of exp011 (pre-registered 65e8cc0; amended 945313b and ecaf9d3), scored as
# registered. Analysis session, 2026-11-20.
#   python tools/culture_tab.py "DIR[;DIR...]" [--alias ARM=SRC,...] [--window 3201-4000] [--pull 0.843]
#          [--gen ARM=RATIO,...] [--perseed] [--bad KIND]
#   python tools/culture_tab.py selftest [bad]
# Arms (seeds 1-8): FLAT (spook load fixed at 1: herdPerHerder >= 1e8, minLoad 1; runOffLoss 0; logHistDepth 1), and
# on that base NUIS03/NUIS10/NUIS30 (nuisanceCost 0.03/0.1/0.3), LARD (larder 1, selfDoes 10), TAPER (captureTaper 1,
# selfDoes 10). The tool checks every run's own parameters against its arm and stops on a mismatch, unless the arm is
# aliased (--alias maps an arm to another arm's files to test the tool; an aliased table is a test, never a result).
# Context arms, read if their files are in the folders given: REF, LOADLO, and exp010's LOAD1 (checked: load fixed at 1,
# runOffLoss 1 or absent), for FLAT - LOAD1 by seed; the arms of exp007 and exp010 for branch 2's breadth against depth.
# Definitions (registration, amendments 945313b and ecaf9d3, notes/batch1-plan.md's standing measures):
#   established = the herd-size criterion of tools/jump_tab.py (100-year mean herd >= 100, held 400 years, testable
#     after year 500, followed to the last row - 400); Kaplan-Meier fraction with a Greenwood log-log interval; the herd
#     >= 100 count over the window beside it; established seeds under 100 in the window are listed (they fell back).
#   gap = herd - wild genotype mean (settle_tab.gaps). Split (split_tab.split, founders 301-400, identity checked):
#     herd change hc and wild change wc against the founders' mean F.
#   breadth (amendment 8, d68a794, Chris): core traits with abs(gap) >= 0.10, as registered; it alone feeds the
#     predictions and the decision rule. Exploratory only (amendments 1, 3-7, demoted by amendment 8; not for the
#     paper): the closed-herd null breadth, traits with abs(gap) >= 0.10 AND abs(hc) > abs(wc) AND hc beyond
#     E = pull x gen x (0.5 - F) (signed), pull 0.95; 0.939, the generation-scaled pull, the C offset and the
#     inflow-aware null are further exploratory lines. The tool stops if the reading moves with any of them.
#   closed (seed) = depth (herdAncDepth) >= 10 generations AND captive-sire share (flow_tab csire) <= 0.10;
#   diverged (seed) = breadth >= 3 (plain, amendment 8). Per arm (ecaf9d3) the per-seed count governs: closed (diverged) if 6 or
#     more established seeds are, not if 6 or more are not, "mixed" otherwise; the arm-mean reading prints beside.
#     An arm is read with 2 or more established seeds.
#   R gaps are read paired against FLAT by seed (seeds established in both; FLAT itself against 0). "R near the wild"
#     = R above -0.30, "R diverged" = -0.30 or below. The reading against 0 prints where it differs.
#   selection on R: selSire and selDam R (year rows, kids-weighted over the window), every arm.
#   nuisance dose-response: FLAT, NUIS03, NUIS10, NUIS30 among the levels read; "falls" = strictly lower at each step.
#     If NUIS30 establishes in 2 or fewer seeds, the dose-response is read over FLAT, NUIS03, NUIS10.
#   loss rates: ranOff, refetched, escaped, looseDeaths per herd goat per recorded year; escaped = 0 in every exp011
#     run (runOffLoss 0), checked as a count.
#   selfMaintDays: share of camp-days self-maintaining over the window (selfMaintDays / (rows x camps x yearDays)), LARD
#     and TAPER established seeds: >= 0.95 -> no selfDoes sweep, else the follow-up at selfDoes 5 and 20.
#   Generation time: not built yet (no parent age at birth in the records); --gen carries the ratio once settled.
# --bad allgoats (split identity), shift / capin (flow checks), esc (one escape added): each must stop or flag.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, flow_tab, jump_tab, inflow_tab
from exp007_tab import carried
gaps, herd, CORE = split_tab.gaps, split_tab.herd, split_tab.CORE
CORE8 = ["R", "A", "S", "B", "H", "T", "M", "W"]   # NT_CORE (genome.js:34): the core traits without L
BASE = {"minLoad": 1, "runOffLoss": 0, "logHistDepth": 1}
OFF = {"nuisanceCost": 0, "larder": 0, "captureTaper": 0}
ARMS = [("FLAT", OFF), ("NUIS03", {**OFF, "nuisanceCost": 0.03}), ("NUIS10", {**OFF, "nuisanceCost": 0.1}),
        ("NUIS30", {**OFF, "nuisanceCost": 0.3}), ("LARD", {**OFF, "larder": 1, "selfDoes": 10}),
        ("TAPER", {**OFF, "captureTaper": 1, "selfDoes": 10})]
NAMES = [a for a, _ in ARMS]
CONTEXT = ["REF", "LOADLO", "LOAD1"]
BRANCH2 = ["LOADLO", "LOADHI", "CTLRAND", "CTLSHAL", "CTLDEEP", "NOCULL", "LOAD05", "LOAD1", "LOAD2", "LOAD3", "REF"]
DOSE = ["FLAT", "NUIS03", "NUIS10", "NUIS30"]
FLOW = ["capt", "csire", "cdam", "depth", "feral", "hsw", "hout", "bredF", "bredM"]
# The primary null's pull: 0.95 as registered (amendment 7, 511fe10; the steward, 2026-11-20: the registered and more
# conservative value). Sensitivity: the measured core C fraction in exp009's CTLDEEP, 0.939 (SE 0.085; tools/inflow_tab.py
# two-pool table, results/exp009_mutation-pull/inflow_3201-4000.txt). The pooled C fraction, herd and wild (EXPLOG exp009
# scored, 9cd6950), gives the inflow null's r.
PULL, PULL_CORE, PULL_POOLED = 0.95, 0.939, 0.843

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def guard(P, want, name):
    bad = [] if (P.get("herdPerHerder") or 0) >= 1e8 else [f"herdPerHerder {P.get('herdPerHerder')}"]
    for k, v in want.items():
        ok = P.get(k) in v if isinstance(v, tuple) else (P.get(k) is not None and abs(P[k] - v) <= 1e-9)
        if not ok: bad.append(f"{k} {P.get(k)} (want {v})")
    if bad: sys.exit(f"{name}: parameters do not match its arm: " + ", ".join(bad))

def wmean(rows, key, k):   # kids-weighted mean of selSire / selDam R over the rows (selN[1] sires, selN[0] dams)
    num = den = 0
    for r in rows:
        if r.get(key) and r.get("selN") and r["selN"][k]: num += r[key]["R"] * r["selN"][k]; den += r["selN"][k]
    return num / den if den else None

def score(f, y0, y1, want, bad=None):
    d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
    if want is not None: guard(P, want, os.path.basename(f))
    if bad == "esc":
        r = next(r for r in d["years"] if y0 <= r["year"] + 1 <= y1); r["escaped"] = (r.get("escaped") or 0) + 1
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    g = gaps(d, y0, y1); h = herd(d, y0, y1)
    fl = flow_tab.run_flow(d, y0, y1, bad if bad in ("shift", "capin") else None) or {}
    sp = split_tab.split(d, y0, y1, 301, 400, "allgoats" if bad == "allgoats" else None)
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    J, end, _, late = jump_tab.jump(hs, lambda v: v >= 100, 400)
    hd = sum(r.get("herded") or 0 for r in rows)
    lr = lambda k: sum(r.get(k) or 0 for r in rows) / hd if hd else None
    smd = [r.get("selfMaintDays") for r in rows]
    run = {"gap": g or None, "herd": h, "J": J, "end": end, "late": late, "flow": fl,
           "hc": {t: v[0] for t, v in sp[0].items()} if sp else None, "wc": {t: v[1] for t, v in sp[0].items()} if sp else None,
           "F": sp[1] if sp else None, "off": lr("culledHerd"), "ranOff": lr("ranOff"), "refetched": lr("refetched"),
           "escaped": lr("escaped"), "loose": lr("looseDeaths") if all("looseDeaths" in r for r in rows) else None,
           "escN": sum(r.get("escaped") or 0 for r in rows), "capN": sum(r.get("captured") or 0 for r in rows),
           "selS": wmean(rows, "selSire", 1), "selD": wmean(rows, "selDam", 0),
           "smd": sum(smd) / (len(rows) * (P.get("camps") or 3) * (P.get("yearDays") or 360))
                  if rows and (P.get("selfDoes") or 0) > 0 and None not in smd else None,
           "fk": firstkid(d, y1), "pa": parentage(d, y0, y1)}
    anc = [r["herdWildAnc"] for r in rows if r.get("herdWildAnc")]
    run["bins"] = [sum(x[k] for x in anc) / len(anc) for k in range(6)] if anc else None
    run["est"] = J is not None and run["gap"] is not None
    if run["gap"]:
        dp, cs = fl.get("depth"), fl.get("csire")
        run["closed"] = dp is not None and cs is not None and dp >= 10 and cs <= 0.10
    return run

def firstkid(d, y1):
    """Generation proxy (clarification f7773f2): median age at first kidding, days; per run the mean over year rows from
    401 to y1 of medianFirstKidAgeHerd and of medianFirstKidAgeWild, then the two averaged (herd and wild pooled within
    the run, as the pooled C is). None if neither is recorded."""
    rows = [r for r in d["years"] if 401 <= r["year"] + 1 <= y1]
    parts = [[r[k] for r in rows if r.get(k) is not None] for k in ("medianFirstKidAgeHerd", "medianFirstKidAgeWild")]
    parts = [sum(p) / len(p) for p in parts if p]
    return sum(parts) / len(parts) if parts else None

def parentage(d, y0, y1):
    """Mean parent age at birth in years, (dam + sire) / 2 per litter, from parentAge (0850eb3: [wild, herd] x [sum dam
    days, sum sire days, litters]): {"wild"|"herd": (window, 401-y1)}. None for runs without the key."""
    yd = (d.get("_parameters") or {}).get("yearDays") or 360
    out = {}
    for k, name in ((0, "wild"), (1, "herd")):
        vals = []
        for lo in (y0, 401):
            rs = [r["parentAge"][k] for r in d["years"] if lo <= r["year"] + 1 <= y1 and r.get("parentAge")]
            if not rs or len(rs) < len([r for r in d["years"] if lo <= r["year"] + 1 <= y1]): return None
            n = sum(x[2] for x in rs)
            vals.append((sum(x[0] for x in rs) + sum(x[1] for x in rs)) / (2 * n) / yd if n else None)
        out[name] = tuple(vals)
    return out

def counts(gap, hc, wc, F, pull, gen, off=0.0):
    """(0.10-only breadth, restated breadth, traits counted by the restated rule). Signed (clarification f7773f2): a
    trait counts if abs(gap) >= 0.10, abs(hc) > abs(wc), and hc goes beyond the expected pull E = pull x gen x (0.5 - F)
    in E's direction, or goes against it (away from 0.5)."""
    old = [t for t in CORE if abs(gap[t]) >= 0.10]
    def beyond(h, E): return (h * E > 0 and abs(h) > abs(E)) or h * E < 0 or (E == 0 and h != 0)
    # off (amendment 5, unvalidated): the arm's neutral offset as a fraction of the distance from the wild mean to 0.5
    new = [t for t in old if beyond(hc[t], pull * gen * (0.5 - F[t]) + off * (0.5 - (F[t] + wc[t])))
           and abs(hc[t]) > abs(wc[t])]
    return len(old), len(new), new, old

def vote(k, n):
    return True if k >= 6 else False if n - k >= 6 else "mixed"

def counts_inflow(gap, wc, F, share, off=0.0):
    """Secondary, model-dependent (amendments 3-4, 6): the inflow-aware null for the herd - wild gap,
    (share + off) x (0.5 - wild mean), share = r / (m + r); a trait counts if abs(gap) >= 0.10 and the gap goes beyond
    that null in its direction or against it (signed, as the clarification)."""
    def beyond(h, E): return (h * E > 0 and abs(h) > abs(E)) or h * E < 0 or (E == 0 and h != 0)
    tr = [t for t in CORE if abs(gap[t]) >= 0.10 and beyond(gap[t], (share + off) * (0.5 - (F[t] + wc[t])))]
    return len(tr), tr

def summary(runs, pull=PULL, gen=1.0, use_off=False, r_gen=None):
    E = [r for r in runs if r["est"]]
    # per-arm C check (amendments 4-5): C's herd - wild gap over established seeds within 2 SE of 0 = validated; else
    # the arm's C gap is an empirical neutral offset (unvalidated), carried to each trait as the same fraction of its
    # distance to 0.5 (Cgap / (0.5 - wild C), so it keeps its direction on traits on either side of 0.5)
    Ec = [r for r in E if r["hc"]]
    Cg = ms([r["gap"]["C"] for r in Ec])
    wC = ms([r["F"]["C"] + r["wc"]["C"] for r in Ec])[0]
    Cok = Cg[0] is None or Cg[1] is None or abs(Cg[0]) <= 2 * Cg[1]
    Cfrac = Cg[0] / (0.5 - wC) if Cg[0] is not None and wC is not None and abs(0.5 - wC) > 0.02 else None
    off = Cfrac if (use_off and not Cok and Cfrac is not None) else 0.0
    for r in E:   # amendment 8: per-seed breadth and "diverged" from abs(gap) >= 0.10 alone; the null count exploratory
        r["traits10"] = [t for t in CORE if abs(r["gap"][t]) >= 0.10]
        r["breadth"] = r["b10"] = len(r["traits10"])
        if r["hc"]: _, r["bnull"], r["tnull"], _ = counts(r["gap"], r["hc"], r["wc"], r["F"], pull, gen, off)
        r["diverged"] = r["breadth"] >= 3
        # exploratory (the reviewer's 8fee17d; not read by the predictions or the rule): the pool carrying each breadth
        # trait by exp007's more-than-half rule within the arm (gap = herd change - wild change), and breadth over the
        # 8 NT_CORE traits (genome.js:34; L excluded)
        r["carrier"] = {t: carried(r["gap"][t], r["hc"][t], r["wc"][t]) for t in r["traits10"]} if r["hc"] else {}
        r["bherd"] = sum(1 for c in r["carrier"].values() if c == "herd") if r["hc"] else None
        r["b8"] = sum(1 for t in r["traits10"] if t in CORE8)
    v = {"n": len(runs), "nE": len(E), "E": E, "runs": runs, "late": sum(1 for r in runs if r["late"]),
         "fell": [r for r in E if r["herd"] < 100], "win100": sum(1 for r in runs if r["herd"] >= 100),
         "herd": ms([r["herd"] for r in runs])[0], "off": ms([r["off"] for r in runs])[0], "gen": gen,
         "Jmed": sorted(r["J"] for r in E)[len(E) // 2] if E else None}
    v["km"] = jump_tab.km([(r["J"], r["end"]) for r in runs], max(r["end"] for r in runs))
    v["read"] = len(E) >= 2
    keys = CORE + ["C"]
    v["gap"] = {t: ms([r["gap"][t] for r in E]) for t in keys} if E else None
    Es = [r for r in E if r["hc"]]
    v["hc"] = {t: ms([r["hc"][t] for r in Es])[0] for t in keys} if Es else None
    v["wc"] = {t: ms([r["wc"][t] for r in Es])[0] for t in keys} if Es else None
    v["F"] = {t: ms([r["F"][t] for r in Es])[0] for t in keys} if Es else None
    v["flow"] = {k: ms([r["flow"].get(k) for r in E]) for k in FLOW}
    v["sel"] = {k: ms([r[k] for r in E]) for k in ("selS", "selD")}
    v["R"] = v["gap"]["R"][0] if E else None
    g0 = {t: v["gap"][t][0] for t in CORE} if E else None
    v["traits"] = [t for t in CORE if abs(g0[t]) >= 0.10] if E else []
    v["breadth"] = v["b10"] = len(v["traits"]) if E else None
    if Es: _, v["bnull"], v["tnull"], _ = counts(g0, v["hc"], v["wc"], v["F"], pull, gen, off)
    else: v["bnull"], v["tnull"] = None, []
    # exploratory (8fee17d): carrier of each arm-mean breadth trait, herd-carried and 8-trait breadth, with per-seed votes
    v["carrier"] = {t: carried(g0[t], v["hc"][t], v["wc"][t]) for t in v["traits"]} if Es else {}
    v["bherd"] = sum(1 for c in v["carrier"].values() if c == "herd") if Es else None
    v["b8"] = sum(1 for t in v["traits"] if t in CORE8) if E else None
    v["nherd3"] = sum(1 for r in Es if r["bherd"] >= 3); v["n8"] = sum(1 for r in E if r["b8"] >= 3)
    v["Cgap"], v["Cok"], v["Cfrac"], v["offset"] = Cg, Cok, Cfrac, off
    # secondary: inflow-aware null at two m from herdWildAnc (window means): arrival = the depth-0 share (equal to m
    # per generation if depths were geometric); core = the depth 10-19 share / 10 (flow reaching the deep herd); with
    # inflow_tab's shape check against geometric at the depth-implied m (depth cap 23 undone)
    Eb = [r for r in E if r["bins"]]
    v["bins"] = [sum(r["bins"][k] for r in Eb) / len(Eb) for k in range(6)] if Eb else None
    v["m"] = {"arrive": v["bins"][0], "core": v["bins"][4] / 10} if Eb else None
    dp = v["flow"]["depth"][0]
    v["shape"] = None
    if Eb and dp is not None:
        if dp >= inflow_tab.CAP - 1e-6: v["shape"] = "at the depth cap"
        else: v["shape"] = inflow_tab.shape(v["bins"], inflow_tab.m_from_depth(dp))[1]
    v["sec"] = {}
    if Eb and Es and r_gen:
        g0 = {t: v["gap"][t][0] for t in CORE}
        for k, m in v["m"].items():
            v["sec"][k] = counts_inflow(g0, v["wc"], v["F"], r_gen / (m + r_gen), off)
    dp, cs = v["flow"]["depth"][0], v["flow"]["csire"][0]
    v["closed_mean"] = v["read"] and dp is not None and cs is not None and dp >= 10 and cs <= 0.10
    v["div_mean"] = v["read"] and v["breadth"] is not None and v["breadth"] >= 3
    v["nclosed"] = sum(1 for r in E if r.get("closed")); v["ndiv"] = sum(1 for r in E if r.get("diverged"))
    v["closed"] = vote(v["nclosed"], len(E)) if v["read"] else "not read"
    v["diverged"] = vote(v["ndiv"], len(E)) if v["read"] else "not read"
    sm = [r["smd"] for r in E if r["smd"] is not None]
    v["smd"] = sum(sm) / len(sm) if sm else None
    v["Rp"] = None; v["RpSE"] = None; v["Rpn"] = 0
    return v

def pair_R(S, seeds):   # R gap paired against FLAT by seed, over seeds established in both (FLAT itself: 0)
    if "FLAT" in S and S["FLAT"]["nE"]: S["FLAT"]["Rp"], S["FLAT"]["Rpn"] = 0.0, S["FLAT"]["nE"]
    for a in S:
        if a == "FLAT" or "FLAT" not in S: continue
        ds = [seeds[a][s]["gap"]["R"] - seeds["FLAT"][s]["gap"]["R"] for s in seeds[a]
              if s in seeds["FLAT"] and seeds[a][s]["est"] and seeds["FLAT"][s]["est"]]
        m = ms(ds); S[a]["Rp"], S[a]["RpSE"], S[a]["Rpn"] = m[0], m[1], len(ds)

def mono(xs):   # strictly falling at each step, over at least two levels
    return len(xs) >= 2 and None not in xs and all(y < x for x, y in zip(xs, xs[1:]))

def read(S, rmode="paired"):
    """The registered predictions and decision rule, from arm summaries. Returns (lines, verdicts)."""
    L, V = [], {}
    f = lambda x: "-" if x is None else f"{x:+.3f}"
    u = lambda x: "-" if x is None else f"{x:.3f}"
    rd = lambda a: a in S and S[a]["read"]
    # R for thresholds: FLAT against 0; every other arm paired against FLAT (or against 0 with rmode "zero")
    Rof = lambda a: S[a]["R"] if (a == "FLAT" or rmode == "zero") else S[a]["Rp"]
    gt = lambda a: Rof(a) is not None and Rof(a) > -0.30
    le = lambda a: Rof(a) is not None and Rof(a) <= -0.30
    fl = S.get("FLAT")
    V["p1"] = bool(rd("FLAT") and fl["nE"] >= 6 and fl["breadth"] is not None and fl["breadth"] <= 2 and fl["R"] > -0.20)
    L.append(f"1. FLAT established in >= 6 of 8, breadth <= 2, R gap above -0.20: {'met' if V['p1'] else 'not met'} "
             f"(established {fl['nE'] if fl else '-'}, breadth {fl['breadth'] if fl else '-'}, R {f(fl['R']) if fl else '-'})")
    p2 = {}
    for a in ("LARD", "TAPER"):
        s = S.get(a)
        p2[a] = bool(rd(a) and s["closed"] is True and gt(a) and s["breadth"] >= 3)
        L.append(f"2. {a}: closed, R gap above -0.30, breadth >= 3: {'met' if p2[a] else 'not met'} ("
                 + (f"{s['nE']} established; closed {s['closed']} ({s['nclosed']} of {s['nE']} seeds; arm means depth "
                    f"{u(s['flow']['depth'][0])}, csire {u(s['flow']['csire'][0])}); R {f(Rof(a))}"
                    f"{' vs FLAT' if rmode == 'paired' else ''}; breadth {s['breadth']} ({', '.join(s['traits']) or 'none'})"
                    if rd(a) else f"not read: {s['nE'] if s else 0} established seeds") + ")")
    V["p2"] = p2["LARD"] and p2["TAPER"]
    L.append(f"   prediction 2 (both arms): {'met' if V['p2'] else 'not met'}")
    n30 = S.get("NUIS30")
    V["n30low"] = bool(n30 and n30["nE"] <= 2)
    dose = DOSE[:3] if V["n30low"] else DOSE
    lv = [a for a in dose if rd(a)]
    R = [(S[a]["R"] if rmode == "zero" else S[a]["Rp"]) for a in lv]; c = [S[a]["flow"]["csire"][0] for a in lv]
    V["p3R"], V["p3c"] = mono(R), mono(c)
    V["p3n30"] = bool(rd("NUIS30") and n30["closed"] is True and le("NUIS30"))
    V["p3"] = V["p3R"] and V["p3c"] and (V["p3n30"] or V["n30low"])
    L.append(f"3. nuisance dose-response, levels read (>= 2 established seeds) in dose order: {' '.join(lv) or 'none'}"
             + (" (NUIS30 established in 2 or fewer seeds: read over FLAT, NUIS03, NUIS10)" if V["n30low"] else ""))
    L.append(f"   R gap falls with nuisanceCost: {'met' if V['p3R'] else 'not met'} (" + ", ".join(f(x) for x in R) + ")")
    L.append(f"   captive-sire share falls with nuisanceCost: {'met' if V['p3c'] else 'not met'} (" + ", ".join(u(x) for x in c) + ")")
    L.append("   NUIS30 closed with R gap -0.30 or below: " + ("not applicable (NUIS30 not established)" if V["n30low"] else
             f"{'met' if V['p3n30'] else 'not met'}" + (f" (closed {n30['closed']}, R {f(Rof('NUIS30'))})" if rd("NUIS30") else " (not read)")))
    L.append(f"   prediction 3: {'met' if V['p3'] else 'not met'}")
    cl = lambda a: rd(a) and S[a]["closed"] is True
    d1 = [a for a in ("LARD", "TAPER") if cl(a) and S[a]["diverged"] is True and gt(a)]
    d2 = [a for a in ("LARD", "TAPER") if cl(a) and S[a]["diverged"] is False]
    dx = [a for a in ("LARD", "TAPER") if cl(a) and S[a]["diverged"] is True and le(a)]
    d3 = [a for a in DOSE[1:] if cl(a) and le(a)]
    d4 = not any(cl(a) for a in NAMES)
    mixed = [f"{a} ({'closed' if S[a]['closed'] == 'mixed' else 'diverged'} mixed)" for a in NAMES if rd(a)
             and ("mixed" in (S[a]["closed"], S[a]["diverged"]))]
    V["d"] = {"d1": d1, "d2": d2, "dx": dx, "d3": d3, "d4": d4, "d5": V["n30low"]}
    L.append("\nDecision rule (registered, as amended):")
    if d1: L.append(f"- {' '.join(d1)} closed and diverged with R near the wild: closure by herder culture gives divergence "
                    "without any rule reading reactivity; tameness is then a separate question, answered by NUIS.")
    if d2: L.append(f"- {' '.join(d2)} closed but not diverged: closure is necessary (exp007) but not sufficient; read with "
                    "breadth against depth across exp007, exp010 and exp011 (table below).")
    if dx: L.append(f"- {' '.join(dx)} closed and diverged with R at -0.30 or below: closure without any rule built for it "
                    "still made herds tamer; read through selection on R (selSire, selDam) and the remaining R-reading rules.")
    if d3: L.append(f"- {' '.join(d3)} closed with R diverged: herder culture can replace the spook filter's loss and its "
                    "herd-size scaling, not the spooking itself.")
    if V["n30low"]: L.append("- NUIS30 established in 2 or fewer seeds: the cost exceeds what a herd can bear.")
    if d4: L.append("- No arm closes: these rules, at these settings, do not close a herd; selfDoes and the nuisance levels "
                    "go to Chris.")
    if mixed: L.append(f"- mixed per-seed counts (no branch read on them): {', '.join(mixed)}")
    return L, V

def main():
    a = sys.argv[1:]; alias = {}; y0, y1 = 3201, 4000; bad = None; pull = PULL; gens = {}
    def opt(k):
        if k in a: i = a.index(k); v = a[i + 1]; del a[i:i + 2]; return v
    if (v := opt("--alias")): alias = dict(x.split("=") for x in v.split(","))
    if (v := opt("--window")): y0, y1 = (int(x) for x in v.split("-"))
    if (v := opt("--pull")): pull = float(v)
    if (v := opt("--gen")): gens = {k: float(x) for k, x in (y.split("=") for y in v.split(","))}
    refdir = opt("--ref") or os.path.join(os.path.dirname(HERE), "results", "exp009_mutation-pull")
    bad = opt("--bad")
    perseed = "--perseed" in a; a = [x for x in a if x != "--perseed"]
    F = {}
    for folder in a[0].split(";"):
        for fn in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(fn))
            if m:
                if int(m.group(2)) in F.setdefault(m.group(1), {}): sys.exit(f"duplicate {fn}")
                F[m.group(1)][int(m.group(2))] = fn
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not exp011 results ***")
    if bad: print(f"*** TEST ONLY: --bad {bad} ***")
    S, seeds, RS = {}, {}, {}
    want = {arm: {**BASE, **w} for arm, w in ARMS}
    want["LOAD1"] = {"minLoad": 1, "runOffLoss": (None, 1)}
    order = NAMES + [c for c in CONTEXT if c not in NAMES]
    extra = [b for b in BRANCH2 if b not in order]
    for arm in order + extra:
        src = alias.get(arm, arm)
        if src not in F:
            if arm in order: print(f"{arm}: no runs ({src})")
            continue
        rs = []
        for s, fn in sorted(F[src].items()):
            r = score(fn, y0, y1, None if (arm not in want or arm in alias) else want[arm], bad); r["seed"] = s; rs.append(r)
        RS[arm] = rs; seeds[arm] = {r["seed"]: r for r in rs}
    # generation ratio (clarification f7773f2): exp009's first-kid proxy (CTLDEEP and CTLRAND runs) / the arm's, so the
    # expectation scales with the arm's generations from year 400 relative to exp009's. --gen overrides (tests only).
    ref = [firstkid(json.load(open(fn, encoding="utf-8")), y1) for arm in ("CTLDEEP", "CTLRAND")
           for fn in sorted(glob.glob(os.path.join(refdir, f"{arm}_seed*.json")))]
    ref = [x for x in ref if x is not None]
    refk = sum(ref) / len(ref) if ref else None
    if refk is None and not gens: sys.exit(f"no exp009 reference runs with first-kid ages in {refdir}; give --ref DIR")
    armk = {arm: ms([r["fk"] for r in rs])[0] for arm, rs in RS.items()}
    for arm in RS:
        if arm not in gens: gens[arm] = refk / armk[arm] if refk and armk[arm] else 1.0
    print(f"primary null (amendment 7): E = {pull:.3f} x (0.5 - F), the registered closed-core pull, unscaled; reference"
          f" first-kid age {'-' if refk is None else f'{refk:.0f}'} days (exp009 CTLDEEP + CTLRAND, {len(ref)} runs,"
          f" {refdir}); generation ratios (exp009 / arm, first-kid proxy): " + ", ".join(f"{a} {g:.3f}" for a, g in gens.items()))
    # pull per generation for the inflow null: the pooled C fraction (herd and wild) over exp009's generations
    elapsed = (y0 + y1) / 2 - 350.5
    r_gen = 1 - (1 - PULL_POOLED) ** (refk / 360 / elapsed) if refk else None
    # sensitivities first (summary sets per-run fields; the main reading last): the measured core C fraction 0.939; the
    # generation-scaled pull, 1 - (1 - pull)^ratio; the unvalidated C offset
    SENS = []
    for name, pulls, off in ((f"pull at the measured core C fraction {PULL_CORE}", {a: PULL_CORE for a in RS}, False),
                             ("pull scaled by the generation ratio, 1 - (1 - pull)^ratio", {a: 1 - (1 - pull) ** gens[a] for a in RS}, False),
                             ("with the unvalidated C offset (arms failing the C check)", {a: pull for a in RS}, True)):
        Sx = {arm: summary(rs, pulls[arm], 1.0, off, r_gen) for arm, rs in RS.items()}; pair_R(Sx, seeds)
        SENS.append((name, read(Sx, "paired"), Sx))
    So = SENS[2][2]
    S = {arm: summary(rs, pull, 1.0, False, r_gen) for arm, rs in RS.items()}
    pair_R(S, seeds)
    show = [x for x in order if x in S]
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"
    u3 = lambda x: "-" if x is None else f"{x:.3f}"
    mse = lambda p, fmt=u3: "-" if p[0] is None else f"{fmt(p[0])} ({p[1]:.3f})"
    print(f"\nyears {y0}-{y1}; established = jump_tab herd-size criterion by the follow-up end; everything after 'herd' over"
          " established seeds; breadth = core traits with abs(gap) >= 0.10 (amendment 8; the exploratory closed-herd null count in brackets); closed / diverged = per-seed vote"
          " (seeds closed or diverged of established), arm-mean reading after the slash")
    print("| arm | seeds | established (KM 95%) | median year | late | herd>=100 in window | fell back | herd | R gap (SE) | R vs FLAT (SE, n) | breadth | depth | csire | closed | diverged | offtake |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for arm in show:
        v = S[arm]; k, ci = v["km"]
        kms = f"{v['nE']} ({k:.2f}" + (f" [{ci[0]:.2f}, {ci[1]:.2f}]" if ci else "") + ")"
        rp = "-" if arm == "FLAT" or v["Rp"] is None or v["RpSE"] is None else f"{v['Rp']:+.3f} ({v['RpSE']:.3f}, {v['Rpn']})"
        print(f"| {arm} | {v['n']} | {kms} | {v['Jmed'] or '-'} | {v['late']} | {v['win100']} | "
              f"{', '.join(str(r['seed']) for r in v['fell']) or '-'} | {v['herd']:.1f} | "
              f"{mse(v['gap']['R'], f3) if v['gap'] else '-'} | {rp} | "
              f"{v['breadth'] if v['breadth'] is not None else '-'} [{v['bnull'] if v['bnull'] is not None else '-'}] | "
              f"{mse(v['flow']['depth'], lambda x: f'{x:.2f}')} | {mse(v['flow']['csire'])} | "
              f"{v['closed']} ({v['nclosed']}/{v['nE']}) / {v['closed_mean']} | {v['diverged']} ({v['ndiv']}/{v['nE']}) / {v['div_mean']} | {u3(v['off'])} |")
    print("\nGaps by trait, established seeds, arm mean (SE); * = counted by the breadth, abs(gap) >= 0.10 (C is neutral, not counted)")
    print("| arm | " + " | ".join(CORE + ["C"]) + " |\n|---|" + "---|" * (len(CORE) + 1))
    for arm in show:
        if S[arm]["gap"]: print(f"| {arm} | " + " | ".join(mse(S[arm]["gap"][t], f3) + ("*" if t in S[arm]["traits"] else "") for t in CORE + ["C"]) + " |")
    print("\nEXPLORATORY (the reviewer's 8fee17d; not read by the predictions or the decision rule). Carrier of each breadth trait"
          " by exp007's more-than-half rule within the arm (herd: herd change has the gap's sign and is more than half of it;"
          " wild: minus the wild change does; mixed: both or neither); herd-carried breadth; breadth over the 8 NT_CORE"
          " traits (L excluded). Arm means over established seeds; per-seed counts = seeds at 3 or more of established")
    print("| arm | breadth | traits (carrier) | herd-carried | seeds herd-carried >= 3 | 8-trait | seeds 8-trait >= 3 |\n|---|---|---|---|---|---|---|")
    for arm in show:
        v = S[arm]
        if not v["read"]: continue
        tc = ", ".join(f"{t} {v['carrier'].get(t, '-')}" for t in v["traits"]) or "none"
        print(f"| {arm} | {v['breadth']} | {tc} | {v['bherd']} | {v['nherd3']} of {v['nE']} | {v['b8']} | {v['n8']} of {v['nE']} |")
    print("  per seed, herd-carried / 8-trait breadth: " + "; ".join(
        f"{arm} " + " ".join(f"s{r['seed']} {r['bherd']}/{r['b8']}" for r in S[arm]["E"]) for arm in show if S[arm]["read"]))
    print(f"\nWithin-arm split (split_tab, founders 301-400), established seeds, arm means: herd change / wild change / "
          f"mutational expectation E = {pull:.3f} x gen x (0.5 - F) (E exploratory)")
    print("| arm | " + " | ".join(CORE + ["C"]) + " |\n|---|" + "---|" * (len(CORE) + 1))
    for arm in show:
        v = S[arm]
        if v["hc"]: print(f"| {arm} | " + " | ".join(f"{v['hc'][t]:+.3f} / {v['wc'][t]:+.3f} / {pull * v['gen'] * (0.5 - v['F'][t]):+.3f}" for t in CORE + ["C"]) + " |")
    print("\nSelection on R (year rows' selSire and selDam, kids-weighted over the window), established seeds, mean (SE)")
    print("| arm | selSire R | selDam R |\n|---|---|---|")
    for arm in show: print(f"| {arm} | {mse(S[arm]['sel']['selS'], f3)} | {mse(S[arm]['sel']['selD'], f3)} |")
    print("\nGene flow (flow_tab), established seeds, mean (SE): capt = captures per herd goat-year; csire, cdam = captive"
          " sire and dam shares of herd conceptions; depth = generations since wild; feral = wildHerdShare (stock); hsw ="
          " wild does' conceptions by a herd sire / all; hout = the same per herd goat; bredF, bredM = first breedings by"
          " captives per capture (a ratio of events, not a cohort share)")
    print("| arm | " + " | ".join(FLOW) + " |\n|---|" + "---|" * len(FLOW))
    for arm in show: print(f"| {arm} | " + " | ".join(mse(S[arm]["flow"][k]) for k in FLOW) + " |")
    def paired(A, B, keys, getter):
        cells = []
        for k in keys:
            ds = [getter(seeds[A][s], k) - getter(seeds[B][s], k) for s in seeds[A] if s in seeds[B]
                  and getter(seeds[A][s], k) is not None and getter(seeds[B][s], k) is not None]
            m = ms(ds); cells.append("-" if m[0] is None else f"{m[0]:+.3f} ({m[1]:.3f}, n {len(ds)})")
        return cells
    print("\nGene flow paired against FLAT by seed (same seed = same history to year 400), every seed both arms have the"
          " measure for; mean difference (paired SE)")
    print("| arm - FLAT | " + " | ".join(FLOW) + " |\n|---|" + "---|" * len(FLOW))
    for arm in NAMES[1:]:
        if arm in S and "FLAT" in S: print(f"| {arm} | " + " | ".join(paired(arm, "FLAT", FLOW, lambda r, k: r["flow"].get(k))) + " |")
    if "FLAT" in S and "LOAD1" in S:
        ks = ["R gap", "herd", "csire", "depth", "ranOff", "escaped"]
        get = lambda r, k: (r["gap"]["R"] if r["gap"] else None) if k == "R gap" else r[k] if k in ("herd", "ranOff", "escaped") else r["flow"].get(k)
        print("\nFLAT - exp010 LOAD1 by seed (they differ only in runOffLoss), every seed both have the measure for")
        print("| pair | " + " | ".join(ks) + " |\n|---|" + "---|" * len(ks))
        print("| FLAT - LOAD1 | " + " | ".join(paired("FLAT", "LOAD1", ks, get)) + " |")
    print("\nNuisance dose-response (nuisanceCost 0 = FLAT): established seeds | all seeds with a herd")
    print("| arm | dose | established | R est | R vs FLAT | csire est | R all | csire all |\n|---|---|---|---|---|---|---|---|")
    for arm, dose in zip(DOSE, (0, 0.03, 0.1, 0.3)):
        if arm not in S: continue
        v = S[arm]; A = [r for r in v["runs"] if r["gap"]]
        print(f"| {arm} | {dose} | {v['nE']} | {f3(v['R'])} | {f3(v['Rp'])} | {u3(v['flow']['csire'][0])} | "
              f"{f3(ms([r['gap']['R'] for r in A])[0])} | {u3(ms([r['flow'].get('csire') for r in A])[0])} |")
    print("\nLoss rates per herd goat per recorded year, all seeds, mean (SE); escapes also as a count over the window")
    print("| arm | run-offs | fetched back | lost | died loose | escapes (count) |\n|---|---|---|---|---|---|")
    for arm in show:
        rs = S[arm]["runs"]
        print(f"| {arm} | " + " | ".join(mse(ms([r[k] for r in rs])) for k in ("ranOff", "refetched", "escaped", "loose")) + f" | {sum(r['escN'] for r in rs)} |")
    esc = [(arm, r["seed"], r["escN"]) for arm in NAMES if arm in S for r in S[arm]["runs"] if r["escN"]]
    print("Check, escaped = 0 in every exp011 run (runOffLoss 0): " + ("passes" if not esc else
          "FAILS: " + ", ".join(f"{a} seed {s} ({n})" for a, s, n in esc)))
    print("\nself-maintaining share of camp-days over the window (selfMaintDays / (rows x camps x yearDays)), LARD and TAPER,"
          " established seeds; >= 0.95 -> no selfDoes sweep, else the follow-up at selfDoes 5 and 20:")
    for arm in ("LARD", "TAPER"):
        if arm not in S: continue
        v = S[arm]
        print(f"  {arm}: {u3(v['smd'])} [" + "; ".join(f"s{r['seed']} {u3(r['smd'])}" for r in v["E"]) + "] -> "
              + ("not recorded (runs without selfMaintDays, or selfDoes 0)" if v["smd"] is None else
                 "no selfDoes sweep" if v["smd"] >= 0.95 else "follow-up at selfDoes 5 and 20"))
    print("\nCaptures over the window per seed, with first breedings per captured doe and buck:")
    for arm in ("FLAT", "LARD", "TAPER"):
        if arm in S: print(f"  {arm}: " + "; ".join(f"s{r['seed']} {r['capN']} (bredF {u3(r['flow'].get('bredF'))}, bredM {u3(r['flow'].get('bredM'))})" for r in S[arm]["runs"]))
    b2 = [x for x in BRANCH2 + NAMES if x in S and S[x]["read"]]
    print("\nBranch 2, breadth against depth (exp007, exp010, exp011 arms present; established seeds; arm means)")
    print("| arm | established | depth | csire | breadth | closed-herd null breadth (exploratory) |\n|---|---|---|---|---|---|")
    for x in dict.fromkeys(b2):
        v = S[x]; print(f"| {x} | {v['nE']} | {u3(v['flow']['depth'][0])} | {u3(v['flow']['csire'][0])} | {v['breadth']} | {v['bnull']} |")
    if perseed:
        print("\n| arm | seed | J | late | herd | R gap | breadth (null, exploratory) | traits | depth | csire | closed | diverged | selSire R | selfMaint | captures | escapes |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for arm in show:
            for r in S[arm]["runs"]:
                fl = r["flow"]
                tr = r.get("traits10", [])
                print(f"| {arm} | {r['seed']} | {r['J'] or '-'} | {r['late'] or '-'} | {r['herd']:.1f} | {f3(r['gap']['R'] if r['gap'] else None)} | "
                      f"{r.get('breadth', '-')} ({r.get('bnull', '-')}) | {' '.join(tr) or '-'} | {u3(fl.get('depth'))} | {u3(fl.get('csire'))} | "
                      f"{r.get('closed', '-')} | {r.get('diverged', '-')} | {f3(r['selS'])} | {u3(r['smd'])} | {r['capN']} | {r['escN']} |")
    print(f"\nEXPLORATORY (amendment 8: not for the predictions, the decision rule or the paper). Null-based divergence"
          f" readings (amendments 6-7), established seeds, arm means. Closed-herd null (pull x (0.5 - F)). C check: C's herd - wild gap within 2 SE of 0; where it fails, the offset (C gap as"
          f" a fraction of wild C's distance to 0.5) is applied, unvalidated, in the 'with offset' columns. Inflow-aware"
          f" null (amendment 7: a finding beside the primary where the ancestry shape is geometric, else secondary and model-dependent): r/(m + r) x (0.5 - wild mean), r = {'-' if r_gen is None else f'{r_gen:.5f}'}"
          f" per generation, at m = arrival (depth-0 share) and m = core (depths 10-19 share / 10)")
    print("| arm | C gap (SE) | C check | offset | null breadth | null, with offset | m arrive | m core | shape: inflow reading is | inflow null at arrive | inflow null at core |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for arm in show:
        v, o = S[arm], So[arm]
        if not v["read"]: print(f"| {arm} | not read ({v['nE']} established) |"); continue
        sc = lambda w, k: "-" if k not in w["sec"] else f"{w['sec'][k][0]} ({' '.join(w['sec'][k][1]) or 'none'})"
        wo = lambda k: sc(v, k) + ("" if v["Cok"] else f"; with offset {sc(o, k)}")
        print(f"| {arm} | {mse(v['Cgap'], f3)} | {'passes' if v['Cok'] else 'FAILS'} | {f3(v['Cfrac']) if not v['Cok'] else '-'} | "
              f"{v['bnull']} ({' '.join(v['tnull']) or 'none'}) | "
              f"{'-' if v['Cok'] else str(o['bnull']) + ' (' + (' '.join(o['tnull']) or 'none') + ')'} | "
              f"{'-' if not v['m'] else format(v['m']['arrive'], '.4f')} | {'-' if not v['m'] else format(v['m']['core'], '.5f')} | "
              f"{v['shape'] or '-'}: {'a finding, beside the primary' if v['shape'] == 'geometric' else 'secondary, model-dependent'} | {wo('arrive')} | {wo('core')} |")
    print("\nExploratory null breadth under each further null line (arm means; not read by the predictions):")
    for name, _, Sx in SENS:
        print(f"  {name}: " + "; ".join(f"{x} {Sx[x]['bnull']} ({' '.join(Sx[x]['tnull']) or 'none'})" for x in show if Sx[x]["read"]))
    print("\nPredictions (registered 65e8cc0; amended 945313b, ecaf9d3, 97d156a; divergence by plain breadth, amendment 8"
          " d68a794); R thresholds paired against FLAT by seed:")
    L, V = read(S, "paired"); print("\n".join(L))
    L0, V0 = read(S, "zero")
    diff = [y for x, y in zip(L, L0) if x != y]
    print("\nRead against 0 instead of paired against FLAT: " + ("the same reading" if V0 == V else "differs on these lines:\n" + "\n".join(diff)))
    # amendment 8: the reading must not move with the exploratory nulls; a difference here is a scorer fault
    moved = [name for name, (Lx, Vx), _ in SENS if Vx != V or Lx != L]
    if bad == "nullread": moved = [SENS[0][0]]
    if moved: sys.exit("scorer fault: the registered reading moved with an exploratory null: " + ", ".join(moved))
    print("Check, the registered reading is the same under every exploratory null line: passes")

def selftest(bad=False):
    # synthetic arm summaries for each branch of the reading; expected verdicts written by hand. 'bad' flips one
    # expectation, which must make the selftest fail. Rp = R paired against FLAT.
    def arm(nE, R, breadth, depth, csire, nclosed=None, ndiv=None, Rp=None):
        mc = nE >= 2 and depth >= 10 and csire <= 0.10; md = nE >= 2 and breadth is not None and breadth >= 3
        nclosed = (nE if mc else 0) if nclosed is None else nclosed; ndiv = (nE if md else 0) if ndiv is None else ndiv
        return {"nE": nE, "read": nE >= 2, "R": R, "Rp": R if Rp is None else Rp, "breadth": breadth, "b10": breadth,
                "traits": [], "flow": {"depth": (depth, 0), "csire": (csire, 0)}, "nclosed": nclosed, "ndiv": ndiv,
                "closed": vote(nclosed, nE) if nE >= 2 else "not read", "diverged": vote(ndiv, nE) if nE >= 2 else "not read"}
    D = lambda d1=(), d2=(), dx=(), d3=(), d4=False, d5=False: {"d1": list(d1), "d2": list(d2), "dx": list(dx), "d3": list(d3), "d4": d4, "d5": d5}
    cases = [
        ("all as predicted",
         {"FLAT": arm(8, -0.05, 1, 5, 0.25), "NUIS03": arm(8, -0.15, 2, 7, 0.18), "NUIS10": arm(8, -0.25, 3, 9, 0.12),
          "NUIS30": arm(8, -0.40, 4, 12, 0.05), "LARD": arm(8, -0.10, 4, 14, 0.04), "TAPER": arm(8, -0.12, 3, 15, 0.03)},
         {"p1": True, "p2": True, "p3": True, "d": D(d1=["LARD", "TAPER"], d3=["NUIS30"])}),
        ("closed, not diverged; dose not monotone",
         {"FLAT": arm(8, -0.05, 1, 5, 0.25), "NUIS03": arm(8, -0.20, 2, 7, 0.18), "NUIS10": arm(8, -0.15, 2, 9, 0.12),
          "NUIS30": arm(3, -0.50, 5, 12, 0.05), "LARD": arm(6, -0.10, 2, 14, 0.04), "TAPER": arm(1, -0.10, 4, 14, 0.04)},
         {"p1": True, "p2": False, "p3": False, "d": D(d2=["LARD"])}),
        ("closed and tamer; near-misses on depth and csire",
         {"FLAT": arm(5, -0.25, 3, 5, 0.25), "NUIS30": arm(8, -0.40, 4, 9.9, 0.05), "LARD": arm(8, -0.40, 4, 14, 0.11),
          "TAPER": arm(8, -0.40, 4, 14, 0.10)},
         {"p1": False, "p2": False, "p3": False, "d": D(dx=["TAPER"])}),
        ("none closes",
         {"FLAT": arm(8, -0.05, 1, 5, 0.25), "LARD": arm(8, -0.10, 4, 9, 0.04), "TAPER": arm(0, None, None, 0, 1)},
         {"p1": True, "p2": False, "p3": False, "d": D(d4=True)}),
        ("per-seed vote mixed beats the arm mean; NUIS30 not established",
         {"FLAT": arm(8, -0.05, 1, 5, 0.25), "NUIS03": arm(8, -0.15, 2, 7, 0.18), "NUIS10": arm(8, -0.25, 3, 9, 0.12),
          "NUIS30": arm(2, -0.50, 5, 12, 0.05), "LARD": arm(8, -0.10, 4, 14, 0.04, nclosed=5),
          "TAPER": arm(8, -0.10, 4, 14, 0.04, ndiv=4)},
         {"p1": True, "p2": False, "p3": True, "d": D(d5=True)}),
        ("paired R decides: near the wild against 0, diverged against FLAT",
         {"FLAT": arm(8, +0.10, 1, 5, 0.25), "LARD": arm(8, -0.25, 4, 14, 0.04, Rp=-0.35), "TAPER": arm(8, -0.10, 4, 14, 0.04)},
         {"p1": True, "p2": False, "p3": False, "d": D(d1=["TAPER"], dx=["LARD"])}),
    ]
    if bad: cases[0][2]["d"]["d3"] = []
    ok = True
    for name, S, want in cases:
        _, V = read(S)
        got = {"p1": V["p1"], "p2": V["p2"], "p3": V["p3"], "d": V["d"]}
        res = got == want; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} {name}" + ("" if res else f": got {got}, want {want}"))
    # amendment 8, through summary(): 8 seeds with R, A, S at gap -0.12 whose herd change sits inside the closed-herd
    # null (F 0.8, E = 0.95 x -0.3 = -0.285): plain breadth 3, diverged; the exploratory null counts none.
    def run(seed):
        g = {t: (-0.12 if t in ("R", "A", "S") else 0.01) for t in CORE}; g["C"] = 0.0
        return {"seed": seed, "est": True, "gap": g, "hc": dict(g), "wc": {t: 0.0 for t in g}, "F": {t: 0.8 for t in g},
                "herd": 150.0, "J": 1000, "end": 3600, "late": None, "flow": {k: (12.0 if k == "depth" else 0.02) for k in FLOW},
                "selS": None, "selD": None, "bins": None, "smd": None, "off": 0.1, "closed": True, "fk": None}
    v = summary([run(s) for s in range(1, 9)])
    got = (v["breadth"], v["bnull"], v["ndiv"], v["diverged"])
    want = (3, 0, 8, True) if not bad else (0, 0, 0, False)
    res = got == want; ok &= res
    print(f"{'ok  ' if res else 'FAIL'} amendment 8: diverged from plain breadth, null exploratory" + ("" if res else f": got {got}, want {want}"))
    # exploratory carrier and 8-trait breadth (8fee17d), gap = hc - wc, by hand: A -0.105 = -0.011 - 0.094 -> wild;
    # T +0.352 = 0.353 - 0.001 -> herd; B -0.12 = -0.06 - 0.06 -> mixed (neither more than half); L +0.11 = 0.11 - 0 ->
    # herd. Breadth 4 (A T B L), herd-carried 2 (T L), 8-trait 3 (L out); no seed herd-carried >= 3, all 8-trait >= 3.
    def run2(seed):
        hc = {t: 0.01 for t in CORE}; wc = {t: 0.0 for t in CORE}
        for t, h, w in (("A", -0.011, 0.094), ("T", 0.353, 0.001), ("B", -0.06, 0.06), ("L", 0.11, 0.0)): hc[t], wc[t] = h, w
        hc["C"] = wc["C"] = 0.0; g = {t: hc[t] - wc[t] for t in hc}
        return {**run(seed), "gap": g, "hc": hc, "wc": wc}
    v = summary([run2(s) for s in range(1, 9)])
    got = (v["breadth"], v["carrier"], v["bherd"], v["b8"], v["nherd3"], v["n8"], v["diverged"])
    want = (4, {"A": "wild", "B": "mixed", "T": "herd", "L": "herd"}, 2, 3, 0, 8, True)
    if bad: want = (4, {"A": "herd", "B": "mixed", "T": "herd", "L": "herd"}, 3, 4, 8, 8, True)
    res = got == want; ok &= res
    print(f"{'ok  ' if res else 'FAIL'} exploratory carrier and 8-trait breadth" + ("" if res else f": got {got}, want {want}"))
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest(sys.argv[2:3] == ["bad"]) else 1)
    main()
