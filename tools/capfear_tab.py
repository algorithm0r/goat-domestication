# capfear_tab.py: exp021's scorer, the fear a captive brings to the herd (analysis session, 2026-11-26; EXPLOG "exp021"
# 1acdee5 as amended by "exp021 amendment" 7b0346a, which governs; the reviewer's notes in fe2f739; Chris: "why does REF
# domesticate and LOAD not?").
#   python tools/capfear_tab.py DIR [--window 3201-4000] [--early 401-1000] [--checks] [--bad hiafter|params]
#   python tools/capfear_tab.py selftest [--bad weight|sign|unest|few|wild|edge|mid]
# DIR holds REFc, LOAD05c, CAPTAME and CAPWILD, seeds 1-8 (3-year rows). Each run's parameters are checked against its
# arm (capturedFearSet: REFc and LOAD05c -1, CAPTAME 0.05, CAPWILD 1; herdPerHerder / minLoad: REFc and CAPTAME 20 / 0.25,
# LOAD05c and CAPWILD 1e9 / 0.5); a mismatch stops the tool.
# Per run, over the window (default 3201-4000, 1-based labels, the recorded rows in it), the standing measures as exp010
# (tools/load_tab.py's score(), unchanged): herd (mean herded); established = herd >= 100 over the window (exp007's
# definition, the one load_tab reads predictions on), with jump_tab's J beside it; the R gap (settle_tab.gaps, histogram
# herd mean - wild mean); csire (flow_tab: herd conceptions by a sire captured himself); run-offs, fetched back and lost
# (ranOff, refetched, escaped) per herd goat-year; and from flow_tab.run_flow, depth (herdAncDepth) and wildHerdShare
# (feral). Breadth per arm: core traits with abs(mean gap over the arm's established seeds) >= 0.10 (load_tab.summary).
# From the year rows (exp021's counters, src/world.js capture(), herdNight; datamanager.js:169-171), summed over the recorded
# rows only (every 3rd year: ratios of sums, never window totals):
#   capturedFear   the mean fearOfHumans captives bring, before the switch: sum(capturedFear x captured) / sum(captured)
#                  (each row's capturedFear is that year's mean over its captives, so it is weighted by captured)
#   hi share       sum(capturedHi) / sum(captured): captives at R x fear >= captureFear on arrival, before the switch
#   hiAfter share  sum(capturedHiAfter) / sum(captured): the same after the switch
#   orphan share   sum(capturedOrphans) / sum(captured), with their mean arrival fear (capturedFearOrphan, weighted)
#   tethered       sum(tetheredDays) / sum(herded): goat-nights tethered per herd goat per recorded year
#   wild fear      per row (goats x learnedFear.humans - herded x herdFearOfHumans) / (goats - herded) (the registered
#                  formula; fields datamanager.js:121, 150, 151, 178, 180), mean over the rows
# capturedFear, hi share and orphan share are also given over the early window (default 401-1000), for P3.
# Arm-level shares (P2's reading rule, P3) pool the seeds: the sums over every row of every seed of the arm.
# Predictions (7b0346a point 3; a pair is the treatment seed against the same seed of its baseline):
#   P1, CAPTAME against REFc, 6+ of 8 seeds: CAPTAME established, csire(CAPTAME) - csire(REFc) >= +0.05, and
#       Rgap(CAPTAME) - Rgap(REFc) >= +0.20 (toward LOAD05's). An unestablished CAPTAME seed counts against. A seed whose
#       REFc baseline is not established cannot hold (reading choice; named in the output if it happens).
#   P2, CAPWILD against LOAD05c: the seeds read are those established in both arms; holds if 6+ of the seeds read have
#       csire(CAPWILD) - csire(LOAD05c) <= -0.05 and Rgap(CAPWILD) - Rgap(LOAD05c) <= -0.20 (toward REF's). The count read
#       is printed beside it. If CAPWILD is established in 2 or fewer seeds, P2 is not read, and the outcome is "naive
#       captives prevent a herd at load 0.5". If in 3 to 5 (the exp021 note f8d2045), P2 is not read: the count read and
#       how many meet both thresholds are printed, read neither for nor against H.
#       Read against H only if LOAD05c's pooled hi share over the window is < 0.5; otherwise P2 is "not read against H"
#       and is reported as descriptive. The orphan share is printed beside the rule (the reviewer's fe2f739 note 1).
#   P3 (descriptive): capturedFear, LOAD05c against REFc, over the early window and the window.
#   Decision rule (7b0346a point 4, f8d2045): both hold; neither; one; or P2 not read (2 or fewer, 3 to 5, or the
#   capturedHi rule not met), when H rests on P1 alone, in the note's words.
# Checks (each stops the tool): parameters per arm; per row capturedHi, capturedHiAfter and capturedOrphans each at
# most captured; with the switch off (REFc, LOAD05c) capturedHiAfter = capturedHi in every row; in CAPTAME
# capturedHiAfter = 0 in every row (R x 0.05 < 0.35 for R <= 1). --checks runs only these and lists the recorded rows per window, printing
# no outcome. --bad hiafter adds 1 to one baseline row's capturedHiAfter where it stays at most captured (must stop on the switch-off equality); --bad params reads CAPTAME's
# capturedFearSet as 0.5 (must stop).
# selftest: planted rows for the pooled shares (weighting by captured: a row-mean would differ), the wild-fear formula,
# and the P1 / P2 rules on planted pairs (threshold edges, an unestablished CAPTAME seed counting against, P2 with 2
# established CAPWILD seeds not read, P2 counted over the seeds read). --bad weight averages capturedFear over rows; --bad
# sign flips P2's direction; --bad unest drops unestablished CAPTAME seeds instead of counting them; --bad few reads P2
# at 2 established seeds; --bad wild takes the wild fear as learnedFear.humans; --bad edge makes 6 seeds (and a 0.5 share) fall
# the wrong side of their edges; --bad mid reads P2 at 3-5 established CAPWILD seeds as the literal fails. Each must fail. The selftest also plants exactly 6 holding (P1 of 8, P2 of 6 read), which
# must hold, and the reading rule's share at exactly 0.5, which must not be read against H.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import load_tab, flow_tab, split_tab

ARMS = {"REFc": (-1, 20, 0.25), "LOAD05c": (-1, 1e9, 0.5), "CAPTAME": (0.05, 20, 0.25), "CAPWILD": (1, 1e9, 0.5)}
BASE = {"CAPTAME": "REFc", "CAPWILD": "LOAD05c"}
DCS, DR = 0.05, 0.20

def check_params(P, arm, name, bad=None):
    cf, hpp, ml = ARMS[arm]
    got = P.get("capturedFearSet")
    if bad == "params" and arm == "CAPTAME": got = 0.5
    if got != cf or abs((P.get("herdPerHerder") or 0) - hpp) > 1e-9 * hpp or abs((P.get("minLoad") or 0) - ml) > 1e-12:
        sys.exit(f"check failed: {name}: capturedFearSet {got}, herdPerHerder {P.get('herdPerHerder')}, minLoad {P.get('minLoad')}; arm {arm} needs {cf}, {hpp}, {ml}")

def check_rows(d, arm, name, bad=None):
    ys = d["years"]
    if bad == "hiafter" and arm in ("REFc", "LOAD05c"):
        for r in ys:
            if (r.get("captured") or 0) > (r.get("capturedHiAfter") or 0): r["capturedHiAfter"] += 1; break   # stays <= captured: must trip the equality
    for r in ys:
        c = r.get("captured") or 0; lab = r["year"] + 1
        for k in ("capturedHi", "capturedHiAfter", "capturedOrphans"):
            if r.get(k) is None: sys.exit(f"check failed: {name} year {lab}: no {k}")
            if r[k] > c: sys.exit(f"check failed: {name} year {lab}: {k} {r[k]} above captured {c}")
        if arm in ("REFc", "LOAD05c") and r["capturedHiAfter"] != r["capturedHi"]:
            sys.exit(f"check failed: {name} year {lab}: switch off, but capturedHiAfter {r['capturedHiAfter']} != capturedHi {r['capturedHi']}")
        if arm == "CAPTAME" and r["capturedHiAfter"] != 0:
            sys.exit(f"check failed: {name} year {lab}: CAPTAME capturedHiAfter {r['capturedHiAfter']}, not 0")

def wild_fear(r, bad=None):
    lf = (r.get("learnedFear") or {}).get("humans"); g, h = r.get("goats") or 0, r.get("herded") or 0
    if lf is None or g <= h: return None
    if bad == "wild": return lf
    hf = r.get("herdFearOfHumans") if h else 0
    if h and hf is None: return None
    return (g * lf - h * (hf or 0)) / (g - h)

def sums(rows, bad=None):
    """Sums over rows for the pooled shares: captured, capturedFear x captured (or the row-mean sum, --bad weight), hi,
    hiAfter, orphans, orphan fear x orphans, tetheredDays, herded, wild-fear sum and count."""
    s = {"cap": 0, "fear": 0.0, "fearRows": 0.0, "fearN": 0, "hi": 0, "hiA": 0, "orph": 0, "ofear": 0.0, "teth": 0, "herd": 0, "wf": 0.0, "wn": 0}
    for r in rows:
        c = r.get("captured") or 0; s["cap"] += c
        if c and r.get("capturedFear") is not None:
            s["fear"] += r["capturedFear"] * c; s["fearRows"] += r["capturedFear"]; s["fearN"] += 1
        s["hi"] += r.get("capturedHi") or 0; s["hiA"] += r.get("capturedHiAfter") or 0
        o = r.get("capturedOrphans") or 0; s["orph"] += o
        if o and r.get("capturedFearOrphan") is not None: s["ofear"] += r["capturedFearOrphan"] * o
        s["teth"] += r.get("tetheredDays") or 0; s["herd"] += r.get("herded") or 0
        w = wild_fear(r, bad)
        if w is not None: s["wf"] += w; s["wn"] += 1
    s["bad"] = bad
    return s

def add(a, b): return {k: (a[k] + b[k] if k != "bad" else a[k]) for k in a}

def shares(s):
    q = lambda x, y: x / y if y else None
    fear = q(s["fearRows"], s["fearN"]) if s["bad"] == "weight" else q(s["fear"], s["cap"])
    return {"capFear": fear, "hi": q(s["hi"], s["cap"]), "hiA": q(s["hiA"], s["cap"]), "orph": q(s["orph"], s["cap"]),
            "orphFear": q(s["ofear"], s["orph"]), "teth": q(s["teth"], s["herd"]), "wild": q(s["wf"], s["wn"]), "cap": s["cap"]}

def win(d, y0, y1): return [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]

def p1(pairs, bad=None):
    """pairs: seed -> (treatment run, baseline run), each {est, gap R, csire}. Returns (k holding of n, per seed, notes)."""
    per, notes = {}, []
    for s, (t, b) in sorted(pairs.items()):
        if not b["est"]: per[s] = None; notes.append(f"s{s} REFc not established"); continue
        if not t["est"]:
            per[s] = None if bad == "unest" else False; continue
        if None in (t["csire"], b["csire"], t["R"], b["R"]): per[s] = False; notes.append(f"s{s} a value missing"); continue
        dc, dr = t["csire"] - b["csire"], t["R"] - b["R"]
        per[s] = dc >= DCS - 1e-12 and dr >= DR - 1e-12
    n = sum(1 for v in per.values() if v is not None) if bad == "unest" else len(per)
    k = sum(1 for v in per.values() if v)
    return ("holds" if (k > 6 if bad == "edge" else k >= 6) else "fails"), k, n, per, notes

def p2(pairs, bad=None):
    """Returns (status, k, n read, per seed). Status 'not read' if CAPWILD is established in 2 or fewer seeds (the prereg);
    'not read (3-5)' if in 3 to 5 (the exp021 note f8d2045: the counts are reported, read neither for nor against H);
    otherwise 'holds' or 'fails' on 6+ of the seeds read."""
    nest = sum(1 for t, _ in pairs.values() if t["est"])
    if nest <= 2 and bad != "few": return "not read", 0, 0, {}
    per = {}
    for s, (t, b) in sorted(pairs.items()):
        if not (t["est"] and b["est"]): continue
        if None in (t["csire"], b["csire"], t["R"], b["R"]): per[s] = False; continue
        dc, dr = t["csire"] - b["csire"], t["R"] - b["R"]
        per[s] = (dc >= DCS - 1e-12 and dr >= DR - 1e-12) if bad == "sign" else (dc <= -DCS + 1e-12 and dr <= -DR + 1e-12)
    k = sum(1 for v in per.values() if v)
    if 3 <= nest <= 5 and bad != "mid": return "not read (3-5)", k, len(per), per
    return ("holds" if (k > 6 if bad == "edge" else k >= 6) else "fails"), k, len(per), per

def decision(v1, st2, rule):
    """7b0346a point 4 and the exp021 note f8d2045: the decision rule as registered."""
    if st2 in ("not read", "not read (3-5)") or not rule:
        why = {"not read": "CAPWILD established in 2 or fewer seeds", "not read (3-5)": "CAPWILD established in 3 to 5 seeds"}.get(st2, "the capturedHi rule is not met")
        return (f"P2 is not read against H ({why}), so H rests on P1 alone (f8d2045): "
                + ("\"captive fear is a lever on closure and the R gap in REF; not tested at load 0.5\"; H is not read as settled." if v1 == "holds"
                   else "\"learned captive fear is not what closes REF's herd\" (the prereg's neither-holds case)."))
    if v1 == "holds" and st2 == "holds": return "P1 and P2 hold: \"captive fear is a lever on closure and on the R gap\" (7b0346a point 4); the tether confound is the next question."
    if v1 != "holds" and st2 != "holds": return "Neither holds: \"learned captive fear is not what closes REF's herd\"; look next at captive R or at capture inflow."
    return f"One holds ({'P1' if v1 == 'holds' else 'P2'}): report which; H is not read as settled."

def h_rule(share, bad=None):
    """7b0346a point 2: P2 is read against H only if LOAD05c's pooled hi share is below 0.5."""
    return share is not None and (share <= 0.5 if bad == "edge" else share < 0.5)

def selftest(bad):
    # pooled shares: two rows, captured 10 (fear 0.2, hi 4, orphans 2 at 0.1) and 30 (fear 0.6, hi 24, orphans 0);
    # weighted fear (2 + 18) / 40 = 0.5 (a row mean would give 0.4); hi 28/40; orphans 2/40, their fear 0.1
    rows = [{"year": 0, "captured": 10, "capturedFear": 0.2, "capturedHi": 4, "capturedHiAfter": 4, "capturedOrphans": 2,
             "capturedFearOrphan": 0.1, "tetheredDays": 30, "herded": 100, "goats": 500, "learnedFear": {"humans": 0.8}, "herdFearOfHumans": 0.2},
            {"year": 3, "captured": 30, "capturedFear": 0.6, "capturedHi": 24, "capturedHiAfter": 24, "capturedOrphans": 0,
             "capturedFearOrphan": None, "tetheredDays": 10, "herded": 100, "goats": 300, "learnedFear": {"humans": 0.6}, "herdFearOfHumans": 0.1}]
    sh = shares(sums(rows, bad))
    # wild fear: row 1 (500 x 0.8 - 100 x 0.2) / 400 = 0.95; row 2 (300 x 0.6 - 100 x 0.1) / 200 = 0.85; mean 0.90
    want = {"capFear": 0.5, "hi": 0.7, "orph": 0.05, "orphFear": 0.1, "teth": 0.2, "wild": 0.9}
    for k, v in want.items():
        if sh[k] is None or abs(sh[k] - v) > 1e-9: sys.exit(f"selftest failed: {k} {sh[k]}, planted {v}")
    E = lambda est, R, cs: {"est": est, "R": R, "csire": cs}
    # P1: 8 pairs against REFc (R -0.60, csire 0.06): s1-s5 hold (s5 exactly at the edges +0.20, +0.05); s6 moves R
    # +0.19 only; s7 CAPTAME unestablished (counts against); s8 csire +0.04 only. So 5 of 8: fails. With --bad unest
    # (s7 dropped) the denominator is 7.
    b = E(True, -0.60, 0.06)
    pr = {1: (E(True, -0.30, 0.20), b), 2: (E(True, -0.20, 0.15), b), 3: (E(True, -0.35, 0.12), b), 4: (E(True, -0.10, 0.30), b),
          5: (E(True, -0.40, 0.11), b), 6: (E(True, -0.41, 0.20), b), 7: (E(False, -0.10, 0.30), b), 8: (E(True, -0.30, 0.10), b)}
    v1, k, n, per, _ = p1(pr, bad)
    if v1 != "fails" or (k, n) != (5, 8) or per[7] is not False or per[5] is not True: sys.exit(f"selftest failed: P1 gives {k} of {n}, per seed {per}; planted 5 of 8, s5 holds, s7 counts against")
    # P2: LOAD05c (R -0.10, csire 0.33); CAPWILD established in 2 seeds: not read
    bb = E(True, -0.10, 0.33)
    q = {s: (E(s <= 2, -0.40, 0.20), bb) for s in range(1, 9)}
    st = p2(q, bad)
    if st[0] != "not read": sys.exit(f"selftest failed: P2 with 2 established CAPWILD seeds gives {st[0]}, not 'not read'")
    # P2 over the seeds read: CAPWILD established in 7 (s8 not), LOAD05c s7 not: 6 read; 5 hold (R -0.20 exactly and
    # csire -0.05 exactly at s5 hold; s6 csire -0.04 fails): 5 of 6 read, fails
    q = {s: (E(s != 8, -0.40, 0.20), bb if s != 7 else E(False, -0.1, 0.33)) for s in range(1, 9)}
    q[5] = (E(True, -0.30, 0.28), bb); q[6] = (E(True, -0.50, 0.29), bb)
    st = p2(q, bad)
    if st[:3] != ("fails", 5, 6) or st[3].get(5) is not True: sys.exit(f"selftest failed: P2 gives {st[:3]}, per seed {st[3]}; planted fails, 5 of 6 read, s5 holds")
    # CAPWILD established in 4 seeds (the exp021 note): not read, with the counts (4 read, 4 meet both); --bad mid reads
    # it as the literal fails and must fail
    q4 = {s: (E(s <= 4, -0.40, 0.20), bb) for s in range(1, 9)}
    st4 = p2(q4, bad)
    if st4[:3] != ("not read (3-5)", 4, 4): sys.exit(f"selftest failed: P2 with 4 established CAPWILD seeds gives {st4[:3]}; planted 'not read (3-5)', 4 of 4 read")
    dd = [decision("holds", "not read (3-5)", True), decision("fails", "not read", True), decision("holds", "holds", False),
          decision("holds", "holds", True), decision("fails", "fails", True), decision("fails", "holds", True)]
    if not ("not tested at load 0.5" in dd[0] and "not what closes" in dd[1] and "P1 alone" in dd[2] and "lever on closure and on the R gap" in dd[3]
            and "Neither holds" in dd[4] and "One holds (P2)" in dd[5]): sys.exit(f"selftest failed: decision wording {dd}")
    # the 6-seed edges: P1 with s6 at the R edge too (6 of 8 hold) must hold; P2 with s6's csire at the edge (6 of 6 read
    # hold) must hold; the reading rule at a share of exactly 0.5 must not be read against H (0.499 must)
    pr[6] = (E(True, -0.40, 0.20), b)
    v1, k, n, _, _ = p1(pr, bad)
    if (v1, k, n) != ("holds", 6, 8): sys.exit(f"selftest failed: P1 at exactly 6 of 8 gives {v1}, {k} of {n}; planted holds")
    q[6] = (E(True, -0.50, 0.28), bb); st = p2(q, bad)
    if st[:3] != ("holds", 6, 6): sys.exit(f"selftest failed: P2 at exactly 6 of 6 read gives {st[:3]}; planted holds")
    if h_rule(0.5, bad) or not h_rule(0.499, bad) or h_rule(None, bad): sys.exit("selftest failed: the reading rule at 0.5 / 0.499 / None")
    print("selftest: pooled shares weighted by captured (fear 0.5 where a row mean gives 0.4), hi, orphans, tethered, the wild-fear"
          " formula (0.90), P1 (5 of 8 with edges holding and an unestablished CAPTAME seed counting against), P2 not read at 2"
          " established CAPWILD seeds, P2 counted over the seeds read (5 of 6),"
          " the 6-seed edges (P1 6 of 8 and P2 6 of 6 read hold), the reading rule at 0.5 (not read against H) and 0.499 (read),"
          " P2 not read at 4 established CAPWILD seeds with its counts, the decision rule's six cases: ok")

def main():
    a = sys.argv[1:]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if a and a[0] == "selftest": selftest(bad); return
    selftest(None)
    rng = lambda k, dv: tuple(int(x) for x in (a[a.index(k) + 1] if k in a else dv).split("-"))
    W, EW = rng("--window", "3201-4000"), rng("--early", "401-1000")
    only = "--checks" in a
    folder = a[0]
    runs = {}
    for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
        m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
        if not m or m.group(1) not in ARMS: continue
        arm, s = m.group(1), int(m.group(2))
        d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}; name = f"{arm} s{s}"
        check_params(P, arm, name, bad); check_rows(d, arm, name, bad)
        if only: runs.setdefault(arm, {})[s] = (len(win(d, *W)), len(win(d, *EW))); continue
        sc = load_tab.score(f, W[0], W[1], None, True)
        fl = flow_tab.run_flow(d, W[0], W[1])
        runs.setdefault(arm, {})[s] = {"est": sc["herd"] >= 100 and bool(sc["gap"]), "herd": sc["herd"], "J": sc["J"], "R": sc["R"],
                                       "csire": sc["csire"], "gap": sc["gap"], "depth": fl["depth"] if fl else None, "feral": fl["feral"] if fl else None,
                                       "ranOff": sc["ranOff"], "refetched": sc["refetched"], "escaped": sc["escaped"],
                                       "sW": sums(win(d, *W)), "sE": sums(win(d, *EW)), "sc": sc}
    missing = [f"{arm} s{s}" for arm in ARMS for s in range(1, 9) if s not in runs.get(arm, {})]
    if missing: sys.exit(f"missing runs: {missing}")
    if only:
        print(f"capfear_tab --checks: 32 runs; parameters match each arm (capturedFearSet, herdPerHerder, minLoad); per row capturedHi,"
              " capturedHiAfter and capturedOrphans at most captured; capturedHiAfter = capturedHi in every REFc and LOAD05c row;"
              " capturedHiAfter = 0 in every CAPTAME row. No outcome printed.")
        for arm in ARMS:
            nw = sorted({v[0] for v in runs[arm].values()}); ne = sorted({v[1] for v in runs[arm].values()})
            print(f"  {arm}: recorded rows in the window {W[0]}-{W[1]}: {nw}; in the early window {EW[0]}-{EW[1]}: {ne}")
        return
    f3 = lambda x: "-" if x is None else f"{x:.3f}"; f4 = lambda x: "-" if x is None else f"{x:+.3f}"; f1 = lambda x: "-" if x is None else f"{x:.1f}"
    print(f"\nexp021 (capfear_tab; 1acdee5 as amended by 7b0346a): checks passed on 32 runs. Window {W[0]}-{W[1]}, early {EW[0]}-{EW[1]};"
          " established = herd >= 100 over the window (load_tab's reading); J is jump_tab's (100-year mean >= 100 held 400 y)."
          " The counters' shares are ratios of sums over the recorded rows only (every 3rd year), not window totals; wild fear is"
          " an unweighted mean over the recorded rows.")
    print("\nPer seed, over the window: established | herd | J | R gap | csire | depth | wildHerdShare | run-offs / fetched back / lost per herd"
          " goat-year | capturedFear | hi share | hiAfter share | orphan share (their fear) | tethered per herd goat | wild fear")
    for arm in ARMS:
        for s in range(1, 9):
            v = runs[arm][s]; w = shares(v["sW"])
            print(f"  {arm} s{s} | {'yes' if v['est'] else 'no'} | {f1(v['herd'])} | {v['J'] or '-'} | {f4(v['R'])} | {f3(v['csire'])} | {f1(v['depth'])}"
                  f" | {f3(v['feral'])} | {f3(v['ranOff'])} / {f3(v['refetched'])} / {f3(v['escaped'])} | {f3(w['capFear'])} | {f3(w['hi'])}"
                  f" | {f3(w['hiA'])} | {f3(w['orph'])} ({f3(w['orphFear'])}) | {f3(w['teth'])} | {f3(w['wild'])}")
    print("\nPer arm (pooled shares over every row of every seed; R gap, csire and breadth over established seeds, load_tab.summary)")
    print("| arm | established | herd | R gap (est) | breadth (est) | csire (est) | capturedFear early | capturedFear window | hi share early | hi share window"
          " | orphan share window | tethered window | wild fear window |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    pooled = {}
    for arm in ARMS:
        sm = load_tab.summary([runs[arm][s]["sc"] for s in range(1, 9)])
        sW = sE = None
        for s in range(1, 9):
            sW = runs[arm][s]["sW"] if sW is None else add(sW, runs[arm][s]["sW"]); sE = runs[arm][s]["sE"] if sE is None else add(sE, runs[arm][s]["sE"])
        w, e = shares(sW), shares(sE); pooled[arm] = (w, e)
        R, br, cs = sm["estp"]
        print(f"| {arm} | {sm['est']} of 8 | {f1(sm['herd'])} | {f4(R)} | {br if br is not None else '-'} | {f3(cs)} | {f3(e['capFear'])} | {f3(w['capFear'])}"
              f" | {f3(e['hi'])} | {f3(w['hi'])} | {f3(w['orph'])} | {f3(w['teth'])} | {f3(w['wild'])} |")
    print("\nPredictions (7b0346a point 3: R gap moves 0.20 or more toward the other arm, csire 0.05 or more in the predicted direction)")
    pr = {s: (runs["CAPTAME"][s], runs["REFc"][s]) for s in range(1, 9)}
    v1, k, n, per, notes = p1(pr)
    print(f"P1, CAPTAME against REFc (csire up by 0.05+, R gap up by 0.20+; an unestablished CAPTAME seed counts against): {k} of {n} seeds: "
          f"{v1}" + (f" ({'; '.join(notes)})" if notes else ""))
    for s in range(1, 9):
        t, b = pr[s]
        dc = t["csire"] - b["csire"] if t["csire"] is not None and b["csire"] is not None else None
        dr = t["R"] - b["R"] if t["R"] is not None and b["R"] is not None else None
        print(f"   s{s}: CAPTAME {'est' if t['est'] else 'not est'}, REFc {'est' if b['est'] else 'not est'}; csire {f3(t['csire'])} vs {f3(b['csire'])}"
              f" ({f4(dc)}); R gap {f4(t['R'])} vs {f4(b['R'])} ({f4(dr)}): {'-' if per[s] is None else ('holds' if per[s] else 'no')}")
    def crit(pairs, sg):   # each criterion on its own, over the seeds with both values (descriptive, beside the verdict)
        xs = [(t["csire"] - b["csire"], t["R"] - b["R"]) for t, b in pairs.values() if t["est"] and b["est"] and None not in (t["csire"], b["csire"], t["R"], b["R"])]
        return (sum(1 for dc, _ in xs if sg * dc >= DCS - 1e-12), sum(1 for _, dr in xs if sg * dr >= DR - 1e-12), len(xs))
    c = crit(pr, 1)
    print(f"   each criterion alone (descriptive): csire up by 0.05+ in {c[0]} of {c[2]} seeds; R gap up by 0.20+ in {c[1]} of {c[2]}")
    q = {s: (runs["CAPWILD"][s], runs["LOAD05c"][s]) for s in range(1, 9)}
    st, k2, n2, per2 = p2(q)
    hi = pooled["LOAD05c"][0]["hi"]; orph = pooled["LOAD05c"][0]["orph"]
    rule = h_rule(hi)
    print(f"P2 reading rule (7b0346a point 2): LOAD05c's pooled hi share over {W[0]}-{W[1]} is {f3(hi)} (orphan share beside it {f3(orph)}):"
          f" {'below 0.5, so P2 is read against H' if rule else 'not below 0.5, so P2 is not read against H and is reported as descriptive'}")
    nest = sum(1 for t, _ in q.values() if t["est"])
    if st == "not read":
        print(f"P2, CAPWILD against LOAD05c: CAPWILD established in {nest} of 8 seeds (2 or fewer): not read; the outcome is \"naive captives prevent a herd at load 0.5\"")
    elif st == "not read (3-5)":
        print(f"P2, CAPWILD against LOAD05c: CAPWILD established in {nest} of 8 seeds (3 to 5): P2 not read (the exp021 note f8d2045); {n2} seeds"
              f" read, {k2} of them meet both thresholds (csire down by 0.05+, R gap down by 0.20+); read neither for nor against H")
    else:
        print(f"P2, CAPWILD against LOAD05c (csire down by 0.05+, R gap down by 0.20+; 6+ of the seeds read, the seeds established in both arms):"
              f" {k2} of {n2} seeds read: {st}" + ("" if n2 >= 6 else f" (only {n2} read, so 6 cannot be met)")
              + ("" if rule else " (descriptive: not read against H)"))
    for s in range(1, 9):
        t, b = q[s]
        dc = t["csire"] - b["csire"] if t["csire"] is not None and b["csire"] is not None else None
        dr = t["R"] - b["R"] if t["R"] is not None and b["R"] is not None else None
        print(f"   s{s}: CAPWILD {'est' if t['est'] else 'not est'}, LOAD05c {'est' if b['est'] else 'not est'}; csire {f3(t['csire'])} vs {f3(b['csire'])}"
              f" ({f4(dc)}); R gap {f4(t['R'])} vs {f4(b['R'])} ({f4(dr)}): {('holds' if per2[s] else 'no') if s in per2 else 'not read'}")
    c = crit(q, -1)
    print(f"   each criterion alone (descriptive): csire down by 0.05+ in {c[0]} of {c[2]} seeds; R gap down by 0.20+ in {c[1]} of {c[2]}")
    print(f"Decision rule: {decision(v1, st, rule)}")
    (wR, eR), (wL, eL) = pooled["REFc"], pooled["LOAD05c"]
    print(f"P3 (descriptive): capturedFear, LOAD05c against REFc: {EW[0]}-{EW[1]} {f3(eL['capFear'])} against {f3(eR['capFear'])};"
          f" {W[0]}-{W[1]} {f3(wL['capFear'])} against {f3(wR['capFear'])}. Per seed over the window: "
          + ", ".join(f"s{s} {f3(shares(runs['LOAD05c'][s]['sW'])['capFear'])} / {f3(shares(runs['REFc'][s]['sW'])['capFear'])}" for s in range(1, 9)))

if __name__ == "__main__":
    main()
