# hph_tab.py: exp022's scorer, the herdPerHerder sweep (analysis session, 2026-11-28; EXPLOG "exp022" 69e3109 as amended
# by "exp022 amendment" 53ee45e, which governs; the reviewer's c2fed28 notes for the scored text).
#   python tools/hph_tab.py DIR [--fixed "DIR;DIR;..."] [--window 3201-4000] [--checks] [--bad params|bounds]
#   python tools/hph_tab.py selftest [--bad weight|order|unest|edge|half|interp|band|above]
# DIR holds HPH5, HPH10, HPH20, HPH40, HPH80 and HPH160, seeds 1-8 (3-year rows). --fixed names the fixed-load folders
# (default results/exp007_design-checks, results/exp010_fixed-load, results/exp015_load-sweep-mid).
# Checks (each stops the tool):
#   parameters: each run's herdPerHerder is its arm's (5, 10, 20, 40, 80, 160), minLoad 0.25, economy 0, and every other
#   parameter but id equals HPH20's run of the same seed; id (the run's stamp) has HPH20's commit, dirty false and the seed;
#   the load bounds, per recorded row with loadDays > 0: herdLoad = max(minLoad, herdCount / herdPerHerder) with one herder
#   per camp at economy 0 (world.js:227-230), so a row's mean load lies between max(0.25, loadHerd / hpp) and
#   0.25 + loadHerd / hpp (tolerance 1e-4 + 0.005 / hpp for the fields' rounding);
#   the fixed-load gaps (53ee45e point 2): each fixed arm's R gap over its established seeds, recomputed here with
#   load_tab.score / load_tab.summary (load_tab's parameter guard on: herdPerHerder >= 1e8, minLoad = the level), equals the
#   registered value to three places: 0.25 -0.055, 0.5 -0.104, 0.6 -0.112, 0.7 -0.167, 0.8 -0.214, 0.9 -0.244, 1 -0.247.
# --checks runs only these, with the recorded rows per window, and prints no exp022 outcome. --bad params reads HPH40's
# herdPerHerder as 20 (must stop); --bad bounds adds 0.3 to one HPH160 row's loadMean (must stop).
# Per run, over the window (1-based labels, the recorded rows in it), the standing measures as exp010 (load_tab.score,
# unchanged): herd (mean herded, all camps); established = herd >= 100 (load_tab's reading), J (jump_tab) beside it; the
# R gap; csire; run-offs, fetched back and lost per herd goat-year. Breadth per arm (load_tab.summary, established seeds).
# The load counters (datamanager.js:171): loadMean and loadHerd pooled by loadDays over the recorded rows,
# sum(x * loadDays) / sum(loadDays). loadHerd is the herd of one camp on a herded camp-day, not the three-camp herd.
# Per arm they pool every row of every seed. Reading choice: P2 and Q read the arm's loadMean pooled over all 8 seeds (the
# prereg's "per arm"); the pooled value over the established seeds is printed beside it, and the tool says whether any
# read depends on the choice.
# Arms read (53ee45e point 4): an arm is established if 2+ of its 8 seeds are; P1's ordering, P2 and Q are read over the
# established arms among HPH20, HPH40, HPH80, HPH160. HPH5 and HPH10 are descriptive (establishment, J, herd).
#   P1: (a) over the arms read, the pooled R gap (load_tab.summary, established seeds) is less negative at the larger
#       herdPerHerder at every adjacent pair, a reversal of any size failing it; and (b) seed-paired, R(HPH160) - R(HPH20)
#       >= 0.20 in 6+ of 8 seeds, an unestablished seed in either arm counting against. If HPH20 or HPH160 is not
#       established, P1 fails.
#   P2 (manipulation check): (a) over the arms read, pooled loadMean is higher at the smaller herdPerHerder at every
#       adjacent pair (strict); and (b) HPH160's pooled loadMean is below half of HPH20's.
#   Q: each arm read with pooled loadMean L in 0.25-1 is matched to the fixed-load gap at L, linearly interpolated between
#       the fixed levels either side (the level itself if L is one). near: |R gap - fixed| <= 0.10; below: more negative by
#       more than 0.10; above: less negative by more than 0.10. An arm read with L above 1 is not matched (if established,
#       a herd persists at a mean load where no fixed-load herd has formed). Q: "level" if every matched arm is near,
#       "rise" if every matched arm is below, "mixed" otherwise (each named); not read with no arm matched. The matched-arm
#       count is printed beside Q (c2fed28 note 1).
#   Decision rule (53ee45e point 3): P2 first, then P1 with Q.
# selftest: pooled loadMean weighted by loadDays (a row mean differs), the load bounds, P1 and P2 on planted arms (strict
# orderings, an unestablished intermediate arm skipped, HPH160 unestablished failing P1, the 6-seed and 0.20 edges, the
# half edge), the interpolation, the band edges, an arm above load 1, the Q readings and the decision rule's cases.
# Bad cases, each must fail: weight (row-mean loadMean), order (a reversal under 0.01 tolerated), unest (an unestablished
# HPH160 not failing P1; unestablished seeds dropped from P1 b), edge (the 0.20 and 6-seed edges read strict), half (b read
# as <=), interp (the nearest fixed level instead of interpolation), band (near read as < 0.10), above (an arm above load
# 1 matched to load 1).
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import load_tab

ARMS = [("HPH5", 5), ("HPH10", 10), ("HPH20", 20), ("HPH40", 40), ("HPH80", 80), ("HPH160", 160)]
READ = ["HPH20", "HPH40", "HPH80", "HPH160"]
HPP = dict(ARMS)
FIXED = [("LOADLO", 0.25, -0.055), ("LOAD05", 0.5, -0.104), ("LOAD06", 0.6, -0.112), ("LOAD07", 0.7, -0.167),
         ("LOAD08", 0.8, -0.214), ("LOAD09", 0.9, -0.244), ("LOAD1", 1.0, -0.247)]
DR, BAND, EPS = 0.20, 0.10, 1e-12

def check_params(P, arm, name, ref, bad=None):
    hpp = P.get("herdPerHerder")
    if bad == "params" and arm == "HPH40": hpp = 20
    if hpp != HPP[arm] or P.get("minLoad") != 0.25 or P.get("economy"):
        sys.exit(f"check failed: {name}: herdPerHerder {hpp}, minLoad {P.get('minLoad')}, economy {P.get('economy')}; arm needs {HPP[arm]}, 0.25, 0")
    if ref is not None:
        diff = sorted(k for k in set(P) | set(ref) if k not in ("herdPerHerder", "id") and P.get(k) != ref.get(k))
        if diff: sys.exit(f"check failed: {name}: parameters differ from HPH20's same seed in {diff}")
        i, j = P.get("id") or {}, ref.get("id") or {}
        if i.get("commit") != j.get("commit") or i.get("dirty") is not False or i.get("seed") != j.get("seed") or i.get("run") != name.replace(" s", "_seed"):
            sys.exit(f"check failed: {name}: stamp {i}; HPH20's {j}")

def check_bounds(rows, arm, name, bad=None):
    hpp = HPP[arm]; tol = 1e-4 + 0.005 / hpp; n = 0
    if bad == "bounds" and arm == "HPH160":
        for r in rows:
            if r.get("loadDays"): r["loadMean"] += 0.3; break
    for r in rows:
        if r.get("loadDays") is None: sys.exit(f"check failed: {name} year {r['year'] + 1}: no loadDays")
        if not r["loadDays"]: continue
        L, H = r.get("loadMean"), r.get("loadHerd")
        if L is None or H is None: sys.exit(f"check failed: {name} year {r['year'] + 1}: loadDays {r['loadDays']} but loadMean {L}, loadHerd {H}")
        lo, hi = max(0.25, H / hpp), 0.25 + H / hpp
        if not (lo - tol <= L <= hi + tol): sys.exit(f"check failed: {name} year {r['year'] + 1}: loadMean {L} outside [{lo:.4f}, {hi:.4f}] (loadHerd {H}, hpp {hpp})")
        n += 1
    return n

def pool(rows, bad=None):
    """(sum loadMean x loadDays, sum loadHerd x loadDays, sum loadDays, row-mean sum, rows) over rows with loadDays > 0."""
    s = [0.0, 0.0, 0, 0.0, 0]
    for r in rows:
        w = r.get("loadDays") or 0
        if not w: continue
        s[0] += r["loadMean"] * w; s[1] += r["loadHerd"] * w; s[2] += w; s[3] += r["loadMean"]; s[4] += 1
    s.append(bad); return s

def addp(a, b): return [a[i] + b[i] for i in range(5)] + [a[5]]

def lm(s):   # pooled loadMean, pooled loadHerd
    if not s[2]: return None, None
    return (s[3] / s[4] if s[5] == "weight" else s[0] / s[2]), s[1] / s[2]

def win(d, y0, y1): return [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]

def ordered(vals, sign, bad=None):
    """vals: [(arm, v)] in herdPerHerder order. sign +1: v must rise with herdPerHerder; -1: fall. Strict at every
    adjacent pair. Returns (ok, the failing pairs)."""
    ok = (lambda x, y: sign * (y - x) > -0.01) if bad == "order" else (lambda x, y: sign * (y - x) > 0)
    fails = [(a, b) for (a, x), (b, y) in zip(vals, vals[1:]) if x is None or y is None or not ok(x, y)]
    return not fails, fails

def p1(S, bad=None):
    """S: arm -> {est arm (bool), R pooled, per seed {s: (est, R)}}. Returns (verdict, (a ok, failing pairs), (k, n), notes)."""
    notes = []
    rd = [a for a in READ if S[a]["est"]]
    ends = S["HPH20"]["est"] and S["HPH160"]["est"]
    if not ends and bad != "unest": notes.append("HPH20 or HPH160 not established: P1 fails (53ee45e point 4)")
    oa, fp = ordered([(a, S[a]["R"]) for a in rd], +1, bad)
    per = {}
    for s in range(1, 9):
        (e1, r1), (e0, r0) = S["HPH160"]["seeds"][s], S["HPH20"]["seeds"][s]
        if not (e1 and e0) or r1 is None or r0 is None: per[s] = None if bad == "unest" else False; continue
        per[s] = (r1 - r0 > DR + EPS) if bad == "edge" else (r1 - r0 >= DR - EPS)
    k = sum(1 for v in per.values() if v); n = sum(1 for v in per.values() if v is not None)
    ob = (k > 6) if bad == "edge" else (k >= 6)
    v = "holds" if ((ends or bad == "unest") and oa and ob) else "fails"
    return v, (oa, fp), (k, n), notes, per

def p2(S, bad=None):
    rd = [a for a in READ if S[a]["est"]]
    oa, fp = ordered([(a, S[a]["L"]) for a in rd], -1, bad)
    a20, a160 = S["HPH20"]["L"], S["HPH160"]["L"]
    hb = a20 is not None and a160 is not None and ((a160 <= 0.5 * a20 + EPS) if bad == "half" else (a160 < 0.5 * a20 - EPS))
    return ("holds" if oa and hb else "fails"), (oa, fp), hb

def fixed_at(L, bad=None):
    """The fixed-load gap at load L, linearly interpolated between the registered levels either side; None outside 0.25-1."""
    if bad == "above" and L > 1: L = 1.0
    if L < 0.25 - EPS or L > 1 + EPS: return None
    if bad == "interp": return min(FIXED, key=lambda t: abs(t[1] - L))[2]
    for (_, x0, g0), (_, x1, g1) in zip(FIXED, FIXED[1:]):
        if x0 - EPS <= L <= x1 + EPS:
            if abs(L - x0) <= EPS: return g0
            if abs(L - x1) <= EPS: return g1
            return g0 + (g1 - g0) * (L - x0) / (x1 - x0)
    return None

def band(R, F, bad=None):
    d = R - F
    if (abs(d) < BAND - EPS) if bad == "band" else (abs(d) <= BAND + EPS): return "near"
    return "below" if d < 0 else "above"

def q_read(S, bad=None):
    """Returns (Q, per arm {arm: (L, fixed gap or None, band or None, note)}, matched count)."""
    per = {}
    for a in READ:
        if not S[a]["est"]: continue
        L, R = S[a]["L"], S[a]["R"]; F = fixed_at(L, bad) if L is not None else None
        if F is None:
            per[a] = (L, None, None, "above load 1: not matched; established at a mean load where no fixed-load herd has formed" if L is not None and L > 1 else "not matched")
        else: per[a] = (L, F, band(R, F, bad), "")
    m = [(a, v[2]) for a, v in per.items() if v[2]]
    if not m: return "not read", per, 0
    if all(b == "near" for _, b in m): q = "level"
    elif all(b == "below" for _, b in m): q = "rise"
    else: q = "mixed (" + ", ".join(f"{a} {b}" for a, b in m) + ")"
    return q, per, len(m)

def decision(v2, v1, q):
    if v2 != "holds": return "P2 fails: the sweep did not move the load as built. Nothing is read on L (53ee45e point 3)."
    if v1 == "holds": return f"P2 holds, P1 holds: the gap follows herdPerHerder. Q: {q}."
    return (f"P2 holds, P1 fails: the gap does not follow herdPerHerder over the arms read. Q: {q}."
            + (" \"Rise\" reads as the gap being set by the rule's rise with herd size more than by its level." if q == "rise" else ""))

def selftest(bad):
    # pooled loadMean: rows (loadDays 100, loadMean 0.30, loadHerd 6) and (300, 0.70, 14): (30 + 210) / 400 = 0.60 (row
    # mean 0.50); loadHerd (600 + 4200) / 400 = 12; a row with loadDays 0 is skipped
    rows = [{"year": 0, "loadDays": 100, "loadMean": 0.30, "loadHerd": 6.0}, {"year": 3, "loadDays": 300, "loadMean": 0.70, "loadHerd": 14.0},
            {"year": 6, "loadDays": 0, "loadMean": None, "loadHerd": None}]
    L, H = lm(pool(rows, bad))
    if abs(L - 0.60) > 1e-12 or abs(H - 12.0) > 1e-12: sys.exit(f"selftest failed: pooled loadMean {L}, loadHerd {H}; planted 0.60, 12")
    # bounds at hpp 20: loadHerd 6 -> [0.30, 0.55]; 0.30 and 0.55 pass (rows above use other hpp, so plant fresh)
    if check_bounds([{"year": 0, "loadDays": 10, "loadMean": 0.30, "loadHerd": 6.0}, {"year": 3, "loadDays": 10, "loadMean": 0.55, "loadHerd": 6.0}], "HPH20", "plant") != 2:
        sys.exit("selftest failed: bounds count")
    # planted arms: R pooled, loadMean, est, seeds
    def mk(est, R, L, seeds=None): return {"est": est, "R": R, "L": L, "seeds": seeds or {s: (True, R) for s in range(1, 9)}}
    def arms(**kw):
        S = {"HPH5": mk(False, None, 3.0), "HPH10": mk(True, -0.70, 2.0),
             "HPH20": mk(True, -0.64, 1.40, {s: (True, -0.64) for s in range(1, 9)}), "HPH40": mk(True, -0.40, 0.73),
             "HPH80": mk(True, -0.20, 0.55), "HPH160": mk(True, -0.10, 0.40)}
        S.update(kw); return S
    # P1 b: HPH160 seeds: s1-s5 at +0.30, s6 exactly +0.20 (R -0.44), s7 HPH160 unestablished, s8 +0.19 -> 6 of 8: holds
    sd = {s: (True, -0.34) for s in range(1, 6)}; sd[6] = (True, -0.44); sd[7] = (False, -0.10); sd[8] = (True, -0.45)
    S = arms(HPH160=mk(True, -0.10, 0.40, sd))
    v1, (oa, _), (k, n), _, per = p1(S, bad)
    if (v1, oa, k, n) != ("holds", True, 6, 8) or per[7] is not False: sys.exit(f"selftest failed: P1 gives {v1}, ordered {oa}, {k} of {n}, per {per}; planted holds, 6 of 8, s7 against")
    # s6 just under: 5 of 8 fails
    sd2 = dict(sd); sd2[6] = (True, -0.4401)
    if p1(arms(HPH160=mk(True, -0.10, 0.40, sd2)), bad)[0] != "fails": sys.exit("selftest failed: P1 at 5 of 8 holds")
    # P1 a: a reversal of 0.001 between HPH40 and HPH80 fails; an unestablished HPH80 is skipped (HPH40 -> HPH160 ordered)
    if p1(arms(HPH80=mk(True, -0.401, 0.55), HPH160=mk(True, -0.10, 0.40, sd)), bad)[1][0]: sys.exit("selftest failed: a 0.001 reversal passes P1's ordering")
    if not p1(arms(HPH80=mk(False, -0.90, 0.55), HPH160=mk(True, -0.10, 0.40, sd)), bad)[1][0]: sys.exit("selftest failed: an unestablished HPH80 is not skipped")
    # HPH160 unestablished: P1 fails
    if p1(arms(HPH160=mk(False, -0.10, 0.40, sd)), bad)[0] != "fails": sys.exit("selftest failed: P1 holds with HPH160 not established")
    # P2: ordered 1.40 > 0.73 > 0.55 > 0.40, and 0.40 < 0.70: holds; HPH160 at exactly 0.70 (half): fails; a tie fails the ordering
    if p2(arms(), bad)[0] != "holds": sys.exit("selftest failed: P2 on planted ordered loads")
    if p2(arms(HPH160=mk(True, -0.10, 0.70)), bad)[2]: sys.exit("selftest failed: HPH160 at exactly half of HPH20 passes P2 b")
    if p2(arms(HPH80=mk(True, -0.20, 0.73)), bad)[1][0]: sys.exit("selftest failed: a tie passes P2's ordering")
    # interpolation: L 0.73 -> -0.167 + 0.3 x (-0.047) = -0.1811; L 0.5 -> -0.104; L 0.25 -> -0.055; L 1.2 -> None
    for x, want in ((0.73, -0.1811), (0.5, -0.104), (0.25, -0.055), (1.0, -0.247), (0.55, -0.108)):
        g = fixed_at(x, bad)
        if g is None or abs(g - want) > 1e-9: sys.exit(f"selftest failed: fixed gap at {x} is {g}, planted {want}")
    if fixed_at(1.2, bad) is not None or fixed_at(0.2, bad) is not None: sys.exit("selftest failed: a load outside 0.25-1 is matched")
    # bands: -0.27 against -0.1811 is near (nearest-level -0.167 would give below); exactly 0.10 off is near
    if band(-0.27, fixed_at(0.73, bad), bad) != "near": sys.exit("selftest failed: band at 0.73")
    if band(-0.204, -0.104, bad) != "near" or band(-0.004, -0.104, bad) != "near": sys.exit("selftest failed: the 0.10 band edge")
    if band(-0.2041, -0.104, bad) != "below" or band(-0.0039, -0.104, bad) != "above": sys.exit("selftest failed: outside the band")
    # Q: planted arms (HPH20 L 1.40 not matched; HPH40 L 0.73 R -0.40 below; HPH80 L 0.55 R -0.20 near; HPH160 L 0.40 R -0.10 near)
    q, per, m = q_read(arms(), bad)
    if m != 3 or per["HPH20"][2] is not None or not q.startswith("mixed"): sys.exit(f"selftest failed: Q gives {q}, {m} matched, {per}; planted mixed, 3 matched, HPH20 not")
    q, _, m = q_read(arms(HPH40=mk(True, -0.27, 0.73)), bad)
    if (q, m) != ("level", 3): sys.exit(f"selftest failed: Q gives {q} ({m}); planted level (3)")
    q, _, m = q_read(arms(HPH40=mk(True, -0.40, 0.73), HPH80=mk(True, -0.30, 0.55), HPH160=mk(True, -0.25, 0.40)), bad)
    if (q, m) != ("rise", 3): sys.exit(f"selftest failed: Q gives {q} ({m}); planted rise (3)")
    q, _, m = q_read(arms(HPH40=mk(True, -0.40, 1.5), HPH80=mk(True, -0.30, 1.2), HPH160=mk(True, -0.25, 1.05)), bad)
    if (q, m) != ("not read", 0): sys.exit(f"selftest failed: Q with no arm at or under load 1 gives {q} ({m})")
    dd = [decision("fails", "holds", "level"), decision("holds", "holds", "level"), decision("holds", "fails", "rise"), decision("holds", "fails", "mixed (x)")]
    if not ("Nothing is read" in dd[0] and "follows herdPerHerder. Q: level" in dd[1] and "more than by its level" in dd[2]
            and "Q: mixed (x)." in dd[3] and "more than by its level" not in dd[3]): sys.exit(f"selftest failed: decision wording {dd}")
    print("selftest: pooled loadMean weighted by loadDays (0.60 where a row mean gives 0.50), the load bounds, P1 (6 of 8 at the"
          " 0.20 edge with an unestablished seed against; 5 of 8 fails; a 0.001 reversal fails; an unestablished middle arm"
          " skipped; HPH160 unestablished fails), P2 (ordered; exactly half fails; a tie fails), the interpolation (0.73 ->"
          " -0.1811), the 0.10 band edges, an arm above load 1 not matched, Q level / rise / mixed / not read, the decision"
          " rule's cases: ok")

def fixed_check(folders, W):
    F = {}
    for folder in folders:
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and m.group(1) in {a for a, _, _ in FIXED}: F.setdefault(m.group(1), {})[int(m.group(2))] = f
    out = []
    for arm, x, g in FIXED:
        fs = F.get(arm, {})
        if sorted(fs) != list(range(1, 9)): sys.exit(f"check failed: fixed arm {arm}: seeds {sorted(fs)} in {folders}")
        sm = load_tab.summary([load_tab.score(fs[s], W[0], W[1], x, False) for s in range(1, 9)])
        R = sm["estp"][0]
        if R is None or round(R, 3) != g: sys.exit(f"check failed: fixed arm {arm} (load {x}): R gap over established seeds {R}, registered {g}")
        out.append((arm, x, g, R, sm["est"]))
    return out

def main():
    a = sys.argv[1:]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if a and a[0] == "selftest": selftest(bad); return
    selftest(None)
    W = tuple(int(x) for x in (a[a.index("--window") + 1] if "--window" in a else "3201-4000").split("-"))
    fixed = (a[a.index("--fixed") + 1] if "--fixed" in a else "results/exp007_design-checks;results/exp010_fixed-load;results/exp015_load-sweep-mid").split(";")
    only = "--checks" in a; folder = a[0]
    files = {}
    for f in glob.glob(os.path.join(folder, "*.json")):
        m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
        if m and m.group(1) in HPP: files.setdefault(m.group(1), {})[int(m.group(2))] = f
    missing = [f"{arm} s{s}" for arm, _ in ARMS for s in range(1, 9) if s not in files.get(arm, {})]
    if missing: sys.exit(f"missing runs: {missing}")
    refP = {s: (json.load(open(files["HPH20"][s], encoding="utf-8")).get("_parameters") or {}) for s in range(1, 9)}
    runs, nrows = {}, {}
    for arm, _ in ARMS:
        for s in range(1, 9):
            f = files[arm][s]; d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}; name = f"{arm} s{s}"
            check_params(P, arm, name, None if arm == "HPH20" else refP[s], bad)
            rows = win(d, *W); nb = check_bounds(d["years"], arm, name, bad)
            nrows.setdefault(arm, set()).add((len(rows), nb))
            if only: continue
            sc = load_tab.score(f, W[0], W[1], None, True); sc["seed"] = s
            runs.setdefault(arm, {})[s] = {"est": sc["herd"] >= 100 and bool(sc["gap"]), "sc": sc, "p": pool(rows)}
    fx = fixed_check(fixed, W)
    if only:
        print(f"hph_tab --checks: 48 runs; parameters match each arm (herdPerHerder, minLoad 0.25, economy 0) and equal HPH20's same"
              " seed apart from herdPerHerder; every recorded row with loadDays > 0 lies within the load bounds. No exp022 outcome printed.")
        for arm, _ in ARMS: print(f"  {arm}: (recorded rows in {W[0]}-{W[1]}, rows with loadDays > 0 over the run) per seed: {sorted(nrows[arm])}")
        print("Fixed-load gaps over established seeds, recomputed (load_tab.score / summary, parameter guard on) against the registered values:")
        for arm, x, g, R, ne in fx: print(f"  {arm} load {x}: {R:+.4f} ({ne} of 8 established), registered {g:+.3f}: match")
        return
    f3 = lambda x: "-" if x is None else f"{x:.3f}"; fs = lambda x: "-" if x is None else f"{x:+.3f}"; f1 = lambda x: "-" if x is None else f"{x:.1f}"
    print(f"\nexp022 (hph_tab; 69e3109 as amended by 53ee45e): checks passed on 48 runs. Window {W[0]}-{W[1]}; established = herd >= 100"
          " over the window (load_tab's reading); an arm is established at 2+ of 8 seeds. loadMean and loadHerd are pooled by loadDays"
          " over the recorded rows (every 3rd year); loadHerd is one camp's herd on a herded camp-day, herd is the three camps' mean herded.")
    print("\nPer seed: established | herd | J | R gap | csire | run-offs / fetched back / lost per herd goat-year | loadMean | loadHerd | loadDays")
    for arm, _ in ARMS:
        for s in range(1, 9):
            v = runs[arm][s]; sc = v["sc"]; L, H = lm(v["p"])
            print(f"  {arm} s{s} | {'yes' if v['est'] else 'no'} | {f1(sc['herd'])} | {sc['J'] or '-'} | {fs(sc['R'])} | {f3(sc['csire'])}"
                  f" | {f3(sc['ranOff'])} / {f3(sc['refetched'])} / {f3(sc['escaped'])} | {f3(L)} | {f1(H)} | {v['p'][2]}")
    S = {}
    print("\nPer arm (R gap, breadth and csire over established seeds, load_tab.summary; loadMean and loadHerd pooled over every row of"
          " every seed, and over the established seeds' rows)")
    print("| arm | herdPerHerder | established | arm established | herd | J (upper median) | R gap | breadth | csire | run-offs | lost"
          " | loadMean | loadMean (est seeds) | loadHerd | loadHerd (est seeds) |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for arm, hpp in ARMS:
        sm = load_tab.summary([runs[arm][s]["sc"] for s in range(1, 9)])
        pa = pe = None
        for s in range(1, 9):
            p = runs[arm][s]["p"]; pa = p if pa is None else addp(pa, p)
            if runs[arm][s]["est"]: pe = p if pe is None else addp(pe, p)
        (L, H), (Le, He) = lm(pa), (lm(pe) if pe else (None, None))
        R, br, cs = sm["estp"]
        S[arm] = {"est": sm["est"] >= 2, "R": R, "L": L, "Le": Le, "seeds": {s: (runs[arm][s]["est"], runs[arm][s]["sc"]["R"]) for s in range(1, 9)}}
        print(f"| {arm} | {hpp} | {sm['est']} of 8 | {'yes' if S[arm]['est'] else 'no'} | {f1(sm['herd'])} | {sm['J']} ({sm['Jmed'] or '-'}) | {fs(R)}"
              f" | {br if br is not None else '-'} | {f3(cs)} | {f3(sm['loss']['ranOff'][0])} | {f3(sm['loss']['escaped'][0])} | {f3(L)} | {f3(Le)} | {f1(H)} | {f1(He)} |")
    print("\nFixed-load gaps (53ee45e point 2; recomputed here, each equal to the registered value to three places): "
          + ", ".join(f"{x} {g:+.3f}" for _, x, g, _, _ in fx) + ". At 2 and above no herd (exp010).")
    rd = [a for a in READ if S[a]["est"]]
    print(f"\nArms read (established among HPH20-HPH160): {', '.join(rd) if rd else 'none'}. HPH5 and HPH10 are descriptive.")
    v2, (o2, fp2), hb = p2(S)
    print(f"P2 (manipulation check): pooled loadMean ordered (higher at smaller herdPerHerder, strict) over the arms read: {'yes' if o2 else 'no, at ' + str(fp2)};"
          f" HPH160's {f3(S['HPH160']['L'])} below half of HPH20's {f3(S['HPH20']['L'])}: {'yes' if hb else 'no'}. P2 {v2}.")
    v1, (o1, fp1), (k, n), notes, per = p1(S)
    print(f"P1 (a): pooled R gap ordered (less negative at larger herdPerHerder, strict) over the arms read: {'yes' if o1 else 'no, at ' + str(fp1)}"
          " (" + ", ".join(a + " " + fs(S[a]["R"]) for a in rd) + ")")
    print(f"P1 (b): R(HPH160) - R(HPH20) >= 0.20, seed-paired, an unestablished seed in either arm counting against: {k} of 8 seeds")
    for s in range(1, 9):
        (e1, r1), (e0, r0) = S["HPH160"]["seeds"][s], S["HPH20"]["seeds"][s]
        dr = r1 - r0 if r1 is not None and r0 is not None else None
        print(f"   s{s}: HPH160 {'est' if e1 else 'not est'} {fs(r1)}, HPH20 {'est' if e0 else 'not est'} {fs(r0)} ({fs(dr)}): {'holds' if per[s] else 'no'}")
    print(f"P1 {v1}" + (f" ({'; '.join(notes)})" if notes else "") + ".")
    q, qp, m = q_read(S)
    print(f"Q (level or rise; matched to the fixed-load gap at the arm's pooled loadMean, linearly interpolated; near = within 0.10):")
    for a, (L, F, b, note) in qp.items():
        print(f"   {a}: loadMean {f3(L)}, R gap {fs(S[a]['R'])}" + (f", fixed-load gap at {f3(L)} {F:+.4f}: {b}" if F is not None else f": {note}"))
    print(f"Q: {q}; {m} arm{'s' if m != 1 else ''} matched (c2fed28 note 1).")
    qe = q_read({a: dict(S[a], L=S[a]["Le"]) for a in S})[0]; v2e = p2({a: dict(S[a], L=S[a]["Le"]) for a in S})[0]
    print(f"Reading choice (loadMean over all 8 seeds): with the established seeds' loadMean instead, P2 {v2e} and Q {qe}:"
          + (" the same reads." if (qe, v2e) == (q, v2) else " the reads DIFFER."))
    print(f"Decision rule (53ee45e point 3): {decision(v2, v1, q)}")

if __name__ == "__main__":
    main()
