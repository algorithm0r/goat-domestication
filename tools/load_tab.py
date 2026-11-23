# load_tab.py: the fixed-spook-load dose-response of exp010 (pre-registered 4aaf978), with exp007's LOADLO and LOADHI as
# its ends and REF as context. Analysis session, 2026-11-20.
#   python tools/load_tab.py "DIR[;DIR...]" [--alias ARM=SRC,...] [--window 3201-4000]
# Arms and their fixed load (herdPerHerder 1e9, minLoad = the load): LOADLO 0.25, LOAD05 0.5, LOAD1 1, LOAD2 2, LOAD3 3,
# LOADHI 4.8. The tool checks each run's own parameters against the arm's load (unless the arm is aliased) and stops on a
# mismatch. REF (load growing with the herd) is printed as context, not as a level.
# Per level, over the window: seeds; established = herd >= 100 over the window (exp007's definition) and, by the herd-size
# criterion of tools/jump_tab.py (100-year mean >= 100 held 400 y), the count established by the follow-up end and their
# upper median of the established runs' years (not the KM median: tools/jump_tab.py prints that); herd; R gap; breadth n (core traits with abs(seed-mean gap) >= 0.10); captive-sire share (flow_tab csire:
# herd conceptions by a sire captured himself); realized offtake. Gaps, breadth and csire are given over all seeds and over
# established seeds only (the prediction reads established seeds).
# Then the predictions and the decision rule as registered. --alias maps an arm to another arm's files to test the tool
# before the runs exist; an aliased table is a test, never a result.
# exp015 (pre-registered 68edd40, amended d377a7d, clarified 5dce596), with --exp015: the levels LOADLO 0.25, LOAD05 0.5, LOAD06 0.6, LOAD07 0.7, LOAD08 0.8,
# LOAD09 0.9, LOAD1 1, read with exp010's and exp007's folders. Added, in that mode only: the KM median year established
# (jump_tab's criterion and km); waited uncensored (under 60 for the span cut, established or not) at cuts 200/300/400, in
# two parts, with exact 95% intervals; per seed J, the longest span under 60 and its median herd, R gap, herd and wild
# change; the per-seed table over 0.5-1; the R gap of seeds that waited beside those that did not (descriptive); and
# exp015's predictions 1-4 and its two decision rules, the waiting rule read by resolution. Guard: each LOAD06-LOAD09 run's
# parameters equal exp010's LOAD1 run of the same seed except minLoad (= the level) and the keys added since exp010 at
# their identity values (spookFixed 0, spookSchedule ""); logHistDepth may differ (output only). Enforced except on
# aliased arms (--bad guard enforces it there too). Without --exp015 the output is exp010's, unchanged.
#   python tools/load_tab.py "results/exp015_load-sweep-mid;results/exp010_fixed-load;results/exp007_design-checks" --exp015
#   python tools/load_tab.py selftest [bad]
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, flow_tab, jump_tab
gaps, herd, CORE = split_tab.gaps, split_tab.herd, split_tab.CORE
LEVELS = [("LOADLO", 0.25), ("LOAD05", 0.5), ("LOAD1", 1.0), ("LOAD2", 2.0), ("LOAD3", 3.0), ("LOADHI", 4.8)]
LEVELS15 = [("LOADLO", 0.25), ("LOAD05", 0.5), ("LOAD06", 0.6), ("LOAD07", 0.7), ("LOAD08", 0.8), ("LOAD09", 0.9), ("LOAD1", 1.0)]
NEW15 = ["LOAD06", "LOAD07", "LOAD08", "LOAD09"]
SWEEP = ["LOAD05", "LOAD06", "LOAD07", "LOAD08", "LOAD09", "LOAD1"]          # 0.5 to 1, the Q1 table and prediction 2
LOADOF = dict(LEVELS15)
IDENT15 = {"spookFixed": 0, "spookSchedule": ""}                            # keys added since exp010, identity values

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def score(f, y0, y1, load, aliased, m15=False):
    d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
    if load is not None and not aliased and not ((P.get("herdPerHerder") or 0) >= 1e8 and abs((P.get("minLoad") or 0) - load) < 1e-9):
        sys.exit(f"{os.path.basename(f)}: parameters herdPerHerder {P.get('herdPerHerder')}, minLoad {P.get('minLoad')} do not fix the load at {load}")
    g = gaps(d, y0, y1); h = herd(d, y0, y1); fl = flow_tab.run_flow(d, y0, y1)
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    hd = sum(r.get("herded") or 0 for r in rows)
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    J = jump_tab.jump(hs, lambda v: v >= 100, 400)
    # Q1 (amendment 071fd3e): how the herd established. at once = at the first testable point; waited = a small-state
    # plateau before the jump (the 100-year herd mean below 60 for 300 consecutive years or more after year 500); grew =
    # established later without such a plateau; never = not established by the follow-up end (a late crossing listed)
    if J[0] is None: q1 = "never" + (f" (late {J[3]})" if J[3] else "")
    elif J[0] == hs[0][0]: q1 = "at once"
    else:
        run, best, start = 0, 0, None
        for y, H, _ in hs:
            if y >= J[0]: break
            if H < 60:
                start = y if start is None else start; best = max(best, y - start)
            else: start = None
        q1 = "waited" if best >= 300 else "grew"
    lr = lambda k: sum(r.get(k) or 0 for r in rows) / hd if hd else None
    return {"gap": g, "herd": h, "csire": fl["csire"] if fl else None, "off": lr("culledHerd"), "J": J[0], "late": J[3],
            "q1": q1, "ranOff": lr("ranOff"), "refetched": lr("refetched"), "escaped": lr("escaped"),
            "end": J[1], "R": g["R"] if g else None, "P": P, **(extra15(d, hs, J[0], y0, y1) if m15 else {})}

def summary(runs):
    est = [r for r in runs if r["herd"] >= 100 and r["gap"]]
    def part(rs):
        gs = [r["gap"] for r in rs if r["gap"]]
        if not gs: return None, None, None
        mean = {t: sum(g[t] for g in gs) / len(gs) for t in CORE}
        return mean["R"], sum(1 for t in CORE if abs(mean[t]) >= 0.10), ms([r["csire"] for r in rs])[0]
    js = sorted(r["J"] for r in runs if r["J"])
    q = {}
    for r in runs: k = r["q1"].split(" ")[0]; q[k] = q.get(k, 0) + 1
    return {"n": len(runs), "est": len(est), "J": len(js), "Jmed": js[len(js) // 2] if js else None,
            "late": sum(1 for r in runs if r["late"]), "herd": ms([r["herd"] for r in runs])[0],
            "off": ms([r["off"] for r in runs])[0], "all": part(runs), "estp": part(est),
            "loss": {k: ms([r[k] for r in runs]) for k in ("ranOff", "refetched", "escaped")},
            "q1": q, "q1runs": [r["q1"] for r in runs], "km": km_median(runs), "runs": runs}

def km_median(runs):   # jump_tab's KM median year established (as jump_tab prints it), None if under half by follow-up
    rr = [(r["J"], r["end"]) for r in runs]; js = sorted(J for J, _ in rr if J)
    return next((J for J in js if jump_tab.km(rr, J)[0] >= 0.5), None)

def main():
    a = sys.argv[1:]; alias = {}; y0, y1 = 3201, 4000
    if "--alias" in a: i = a.index("--alias"); alias = dict(x.split("=") for x in a[i + 1].split(",")); del a[i:i + 2]
    if "--window" in a: i = a.index("--window"); y0, y1 = (int(v) for v in a[i + 1].split("-")); del a[i:i + 2]
    m15 = "--exp015" in a; a = [x for x in a if x != "--exp015"]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    levels = LEVELS15 if m15 else LEVELS
    F = {}
    for folder in a[0].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(2)) in F.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                F[m.group(1)][int(m.group(2))] = f
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not {'exp015' if m15 else 'exp010'} results ***")
    S = {}
    for arm, load in levels + [("REF", None)]:
        src = alias.get(arm, arm)
        if src not in F: print(f"{arm}: no runs ({src})"); continue
        rs = []
        for s, f in sorted(F[src].items()):
            r = score(f, y0, y1, load, arm in alias, m15); r["seed"] = s; rs.append(r)
        S[arm] = summary(rs)
    if m15: guard15(S, alias, bad == "guard")
    print(f"\nyears {y0}-{y1}. est = seeds with herd >= 100 over the window; by-herd = established by the jump_tab criterion"
          " by the follow-up end (upper median of the established runs' years, not the KM median; late crossings); R, n, csire over all seeds | established seeds only")
    print("| arm | load | seeds | est | by-herd (upper median) | late | herd | R all | R est | n all | n est | csire all | csire est | offtake |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"
    for arm, load in levels + [("REF", "grows")]:
        if arm not in S: continue
        v = S[arm]; (Ra, na, ca), (Re, ne, ce) = v["all"], v["estp"]
        f3u = lambda x: "-" if x is None else f"{x:.3f}"
        print(f"| {arm} | {load} | {v['n']} | {v['est']} | {v['J']} ({v['Jmed'] or '-'}) | {v['late']} | {v['herd']:.1f} | {f3(Ra)} | {f3(Re)} | "
              f"{na if na is not None else '-'} | {ne if ne is not None else '-'} | {f3u(ca)} | {f3u(ce)} | {f3u(v['off'])} |")
    print("\nObservable rates (amendment 071fd3e), per herd goat per recorded year, seed mean (SE): run-offs (ranOff), fetched"
          " back (refetched), lost (escaped)")
    print("| arm | run-offs | fetched back | lost |\n|---|---|---|---|")
    for arm, _ in levels + [("REF", None)]:
        if arm in S: print(f"| {arm} | " + " | ".join("-" if S[arm]["loss"][k][0] is None else "{:.3f} ({:.3f})".format(*S[arm]["loss"][k]) for k in ("ranOff", "refetched", "escaped")) + " |")
    print("\nQ1, how herds established (amendment 071fd3e): at once = at the first testable year after 500; waited = a plateau"
          " first (the 100-year herd mean under 60 for 300+ consecutive years after 500, then established); grew = established"
          " later without such a plateau; never = not established by the follow-up end")
    for arm, _ in levels + [("REF", None)]:
        if arm in S: print(f"  {arm}: " + ", ".join(f"{k} {n}" for k, n in sorted(S[arm]["q1"].items())) + "  [" + "; ".join(S[arm]["q1runs"]) + "]")
    if m15: tables15(S); print("\n".join(read15(S)[0])); return
    w = {a: S[a]["q1"].get("waited", 0) for a in ("LOAD1", "LOAD2", "LOAD3") if a in S}
    print("  Q1 reading at loads 1-3: " + (f"herds waited in the small state and then jumped ({', '.join(f'{a} {n}' for a, n in w.items())} seeds):"
          " the waiting does not need the load to scale with herd size" if any(w.values()) else
          "no herd waited and then jumped (they established at once, grew, or never): the waiting in REF is the scaling rule's doing"))
    preds(S)

def preds(S):
    print("\nPredictions (registered, 4aaf978):")
    g = lambda arm, k: S[arm][k] if arm in S else None
    est = {arm: g(arm, "est") for arm, _ in LEVELS}
    p1 = all(est[a] is not None and est[a] >= 6 for a in ("LOAD05", "LOAD1", "LOAD2")) and est["LOAD3"] is not None and est["LOAD3"] <= 4
    print(f"1. established in >= 6 of 8 at 0.5, 1, 2 and <= 4 of 8 at 3: {'met' if p1 else 'not met'} "
          f"(LOAD05 {est['LOAD05']}, LOAD1 {est['LOAD1']}, LOAD2 {est['LOAD2']}, LOAD3 {est['LOAD3']})")
    # among established seeds, across the levels that have at least 2 established seeds, in load order
    lv = [(a, S[a]["estp"]) for a, _ in LEVELS if a in S and S[a]["est"] >= 2]
    names = " ".join(a for a, _ in lv)
    R = [p[0] for _, p in lv]; n = [p[1] for _, p in lv]; c = [p[2] for _, p in lv]
    mono = lambda xs, cmp: len(xs) >= 2 and all(cmp(x, y) for x, y in zip(xs, xs[1:]))
    print(f"   levels read (>= 2 established seeds), in load order: {names or 'none'}")
    print(f"2. R gap of established seeds more negative at each higher level: {'met' if mono(R, lambda x, y: y < x) else 'not met'} ("
          + ", ".join(f"{x:+.3f}" for x in R) + ")")
    r1 = S["LOAD1"]["estp"][0] if "LOAD1" in S else None
    print(f"3. LOAD1 R gap (established) between -0.50 and -0.20: {'met' if r1 is not None and -0.50 <= r1 <= -0.20 else 'not met'} ({'-' if r1 is None else f'{r1:+.3f}'})")
    # breadth (settled before any outcome, EXPLOG after 071fd3e): rising = non-decreasing across the levels read and higher
    # at the highest level read than at the lowest; R gap and captive-sire share stay strict at each step
    rise = mono(n, lambda x, y: y >= x) and n[-1] > n[0]
    print(f"4. breadth (established) rises with load: {'met' if rise else 'not met'} (" + ", ".join(str(x) for x in n) + "; non-decreasing, last above first)")
    print(f"5. captive-sire share (established) falls with load: {'met' if mono(c, lambda x, y: y < x) else 'not met'} (" + ", ".join(f"{x:.3f}" for x in c) + ")")
    div = [a for a, p in lv if p[0] is not None and p[0] <= -0.30 and p[1] >= 3]
    print(f"\nDecision rule: levels with established herds diverging (R gap <= -0.30 and breadth >= 3): {' '.join(div) or 'none'} -> "
          + ("the divergence needs a spook filter of that strength, not its scaling with herd size" if div else
             "no fixed load gives both a persisting herd and divergence; REF's divergence needs the load to grow with the herd"))

# ---- exp015 (pre-registered 68edd40, amended d377a7d, clarified 5dce596) ----
CUTS = (200, 300, 400)          # span cuts for "waited"; 300 is the registered one, 200 and 400 test cut dependence
FLOOR = 501                     # the first testable year after 500: a KM median here is a tie at the floor

def wait_span(hs, J):
    """Longest span under 60 of the 100-year herd mean after year 500, measured as exp010's Q1 measures it (last minus
    first year of the run of points under 60), before J if the run established, else to the end of the run (the
    amendment: waited no longer needs establishment). Returns (span, median raw herd over that span's points or None)."""
    best, bi, start, si = 0, None, None, None
    for i, (y, H, raw) in enumerate(hs):
        if J is not None and y >= J: break
        if H < 60:
            if start is None: start, si = y, i
            if bi is None or y - start > best: best, bi = y - start, (si, i)
        else: start = None
    if bi is None: return 0, None
    v = sorted(r[2] for r in hs[bi[0]:bi[1] + 1]); k = len(v)
    return best, (v[k // 2] if k % 2 else (v[k // 2 - 1] + v[k // 2]) / 2)

def extra15(d, hs, J, y0, y1):
    """The exp015 per-run additions: span and its median herd, herd and wild change of R against the 301-400 founders."""
    span, med = wait_span(hs, J)
    sp = split_tab.split(d, y0, y1, 301, 400)
    return {"span": span, "spanmed": med, "hc": sp[0]["R"][0] if sp else None, "wc": sp[0]["R"][1] if sp else None}

def cp(k, n):   # exact (Clopper-Pearson) 95% interval for k of n
    from scipy.stats import beta
    return (0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1)), 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k)))

def waited(runs, cut=300): return [r for r in runs if r["span"] >= cut]

def guard15(S, alias, force=False):
    """Each LOAD06-LOAD09 run against exp010's LOAD1 run of the same seed: only minLoad differs (= the level), keys added
    since exp010 at their identity values, logHistDepth output only. Stops on a mismatch."""
    import sched_tab
    if "LOAD1" not in S or "LOAD1" in alias: sys.exit("exp015 guard: needs exp010's own LOAD1 runs (not aliased)")
    B = {r["seed"]: r["P"] for r in S["LOAD1"]["runs"]}; extra = set()
    for arm in NEW15:
        if arm not in S or (arm in alias and not force): continue
        for r in S[arm]["runs"]:
            if r["seed"] not in B: sys.exit(f"exp015 guard: {arm} seed {r['seed']} has no LOAD1 run of the same seed")
            try: extra.update(sched_tab.guard(r["P"], B[r["seed"]], {"minLoad": LOADOF[arm]}, True, IDENT15))
            except sched_tab.GuardFail as e: sys.exit(f"exp015 guard: {arm} seed {r['seed']} against LOAD1 seed {r['seed']}: {e}")
    checked = [a for a in NEW15 if a in S and (a not in alias or force)]
    print(f"\nexp015 guard against exp010 LOAD1, same seed: {' '.join(checked) or 'no arm checked (all aliased)'} pass; "
          f"only minLoad differs, plus {', '.join(sorted(extra)) or 'nothing'}")

def cls15(r, cut=300):
    if r["span"] >= cut:
        return f"waited, est {r['J']}" if r["J"] else ("waited, late " + str(r["late"]) if r["late"] else "waited, still")
    return r["q1"] if r["q1"] != "waited" else "grew"      # an exp010 'waited' under this cut's span is a plateau too short

def tables15(S):
    print("\nWaited (amendment d377a7d: 100-year herd mean under 60 for the cut's span or more after year 500, before J if"
          " established, else to the run's end; established or not), by cut; at 300: fraction with exact 95% interval, in two"
          " parts (waited then established | still waiting or crossing late)")
    print("| arm | load | seeds | waited @200 | waited @300 | waited @400 | @300 fraction [95% CP] | @300 then established | @300 still waiting / late |")
    print("|---|---|---|---|---|---|---|---|---|")
    for arm, load in LEVELS15:
        if arm not in S: continue
        rs = S[arm]["runs"]; n = len(rs); w = waited(rs); lo, hi = cp(len(w), n)
        e = [r for r in w if r["J"]]; st = [r for r in w if not r["J"]]
        print(f"| {arm} | {load} | {n} | {len(waited(rs, 200))} | {len(w)} | {len(waited(rs, 400))} | {len(w) / n:.3f} [{lo:.3f}, {hi:.3f}] | "
              f"{len(e)} | {len(st)}" + (" (" + ", ".join(f"s{r['seed']}" + (f" late {r['late']}" if r["late"] else " still") for r in st) + ")" if st else "") + " |")
    print("\nEstablished by jump_tab's herd-size criterion: KM median year (jump_tab.km: the first event year where the established"
          f" fraction reaches 0.5; '-' = under half by the follow-up end; {FLOOR} = the floor, the first testable year)")
    print("| arm | load | seeds | by-herd | KM median year |\n|---|---|---|---|---|")
    for arm, load in LEVELS15:
        if arm in S: print(f"| {arm} | {load} | {S[arm]['n']} | {S[arm]['J']} | {S[arm]['km'] or '-'} |")
    arms = [a for a in SWEEP if a in S]
    seeds = sorted({r["seed"] for a in arms for r in S[a]["runs"]})
    print("\nPer seed over loads 0.5-1, at the 300 cut: waited then established (J) / waited, still waiting or crossing late /"
          " exp010's Q1 otherwise (at once, grew, never)")
    print("| seed | " + " | ".join(f"{a} ({LOADOF[a]})" for a in arms) + " |\n|---|" + "---|" * len(arms))
    for s in seeds:
        cells = []
        for a in arms:
            r = next((r for r in S[a]["runs"] if r["seed"] == s), None)
            cells.append("-" if r is None else cls15(r) + ("" if r["span"] >= 300 or r["J"] is None else f" {r['J']}"))
        print(f"| {s} | " + " | ".join(cells) + " |")
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"
    print("\nPer seed: J (jump_tab), longest span under 60 (100-year mean) after 500 and the median raw herd of the year rows in that span (read only for spans of 200 years or more), window R gap, herd and wild"
          " change of R against the 301-400 founders (open herds)")
    print("| arm | seed | at 300 | J | span <60 (y) | median raw herd (year rows) | R gap | herd change R | wild change R |\n|---|---|---|---|---|---|---|---|---|")
    for arm, _ in LEVELS15:
        if arm not in S: continue
        for r in S[arm]["runs"]:
            md = "-" if r["spanmed"] is None else f"{r['spanmed']:.1f}"
            print(f"| {arm} | {r['seed']} | {cls15(r)} | {r['J'] or '-'} | {r['span']} | {md} | {f3(r['R'])} | {f3(r['hc'])} | {f3(r['wc'])} |")
    print("\nWithin each level, window R gap of seeds that waited (300 cut) beside those that did not; descriptive, not a test (68edd40)")
    for arm, _ in LEVELS15:
        if arm in S: print(f"  {arm}: " + split_waited(S[arm]["runs"]))

def split_waited(runs):
    def cell(rs):
        xs = [r["R"] for r in rs if r["R"] is not None]
        return f"{sum(xs) / len(xs):+.3f} (n {len(xs)}: " + ", ".join(f"s{r['seed']} {r['R']:+.3f}" for r in rs if r["R"] is not None) + ")" if xs else "- (n 0)"
    w = waited(runs); o = [r for r in runs if r["span"] < 300]
    return f"waited {cell(w)}; did not wait {cell(o)}"

def wait_reading(counts, ns):
    """The waiting rule by resolution (d377a7d, 5dce596) on waited counts over 0.5-1 in load order. Not monotone is read
    first: a fall of 2 or more seeds between neighbouring levels. Then by the number of intermediate levels (2 to n-2)."""
    falls = [(SWEEP[i], SWEEP[i + 1]) for i in range(len(counts) - 1) if counts[i] - counts[i + 1] >= 2]
    if falls: return ("not monotone", tuple((LOADOF[x], LOADOF[y]) for x, y in falls))
    mid = [SWEEP[i] for i, (w, n) in enumerate(zip(counts, ns)) if 2 <= w <= n - 2]
    if len(mid) >= 2: return ("graded", tuple(LOADOF[a] for a in mid))
    if len(mid) == 1: return ("located", LOADOF[mid[0]])
    hi = [i for i, (w, n) in enumerate(zip(counts, ns)) if w >= n - 1]
    if not hi: return ("no switch in 0.5-1", "all 0-1")
    if hi[0] == 0: return ("no switch in 0.5-1", "all 7-8")
    return ("switch", LOADOF[SWEEP[hi[0] - 1]], LOADOF[SWEEP[hi[0]]])

def say_reading(R):
    if R[0] == "not monotone": return "not monotone in load (a fall of 2+ between " + ", ".join(f"{a} and {b}" for a, b in R[1]) + "): no single threshold"
    if R[0] == "graded": return f"two or more levels intermediate ({', '.join(str(x) for x in R[1])}): graded over at least 0.1-0.2"
    if R[0] == "located": return f"one level intermediate ({R[1]}): the switch is located there, its width unresolved at this spacing"
    if R[0] == "switch": return f"no level intermediate: a switch narrower than 0.1, between {R[1]} and {R[2]}"
    return f"no level intermediate and no switch within 0.5-1 ({R[1]})"

def read15(S):
    """exp015's predictions 1-4 and decision rules (68edd40, d377a7d, 5dce596) on level summaries S. Returns (lines, verdicts)."""
    L, V = ["\nPredictions (registered 68edd40, amended d377a7d, clarified 5dce596):"], {}
    est = {a: S[a]["est"] if a in S else None for a in NEW15}
    V["p1"] = all(est[a] is not None and est[a] >= 6 for a in NEW15)
    L.append(f"1. every new level established (herd >= 100 over the window) in >= 6 of 8: {'holds' if V['p1'] else 'fails'} ("
             + ", ".join(f"{a} {'-' if est[a] is None else est[a]}" for a in NEW15) + ")")
    have = all(a in S for a in SWEEP)
    ns = [len(S[a]["runs"]) if a in S else 0 for a in SWEEP]
    rd = {c: wait_reading([len(waited(S[a]["runs"], c)) for a in SWEEP], ns) if have else None for c in CUTS}
    w = {a: len(waited(S[a]["runs"])) if a in S else None for a in SWEEP}
    wl = [w[a] for a in SWEEP]
    nd = None not in wl and all(y >= x for x, y in zip(wl, wl[1:]))
    mid = [a for a in NEW15 if w[a] is not None and 2 <= w[a] <= 6]
    V["p2"] = bool(have and rd[300][0] == "graded" and nd and len(mid) >= 2)
    L.append(f"2. waiting graded (300 cut): 'waited' non-decreasing over 0.5-1 ({', '.join(f'{a} {w[a]}' for a in SWEEP)}: {'yes' if nd else 'no'}),"
             f" >= 2 new levels with 2-6 waited ({' '.join(mid) or 'none'}), and the waiting reading 'graded'"
             f" ({rd[300][0] if have else 'not read'}): {'holds' if V['p2'] else 'fails'}")
    km = [S[a]["km"] if a in S else "x" for a in SWEEP]
    key = lambda m: float("inf") if m is None else m     # no median (under half established): above every median; two tie
    V["p3"] = "x" not in km and all(key(y) >= key(x) for x, y in zip(km, km[1:]))
    floor = [a for a, m in zip(SWEEP, km) if m == FLOOR]
    L.append(f"3. KM median year established non-decreasing with load over 0.5-1 ({', '.join(f'{a} ' + ('-' if m is None else str(m)) for a, m in zip(SWEEP, km))};"
             f" '-' = under half, above every median, two '-' tie): {'holds' if V['p3'] else 'fails'}"
             + (f". Ties at the {FLOOR} floor carry no information: {' '.join(floor)}" if len(floor) >= 2 else ""))
    R = {a: S[a]["estp"][0] if a in S else None for a in NEW15}
    inb = all(R[a] is not None and -0.30 <= R[a] <= -0.05 for a in NEW15)
    order = R["LOAD09"] is not None and R["LOAD06"] is not None and R["LOAD09"] < R["LOAD06"]
    V["p4"] = inb and order
    L.append(f"4. new levels' R gap, arm mean over established seeds, within [-0.30, -0.05] ({', '.join(f'{a} ' + ('-' if R[a] is None else f'{R[a]:+.3f}') for a in NEW15)}:"
             f" {'yes' if inb else 'no'}) and LOAD09 more negative than LOAD06 ({'yes' if order else 'no'}): {'holds' if V['p4'] else 'fails'}")
    L.append("\nDecision rules (68edd40, amended d377a7d, clarified 5dce596):")
    V["wait"] = rd[300]
    if have:
        L.append(f"- Waiting, by resolution (300 cut; waited {', '.join(f'{a} {w[a]}' for a in SWEEP)}): {say_reading(rd[300])}.")
        same = rd[200] == rd[300] == rd[400]
        V["cutdep"] = not same
        L.append("  At the 200 and 400 cuts: " + "; ".join(f"{c}: {say_reading(rd[c])}" for c in (200, 400))
                 + (". The reading is the same at all three cuts." if same else ". CUT-DEPENDENT: the reading differs between the 200, 300 and 400 cuts."))
    else:
        V["cutdep"] = None
        L.append("- Waiting: not read (a level of 0.5-1 is missing)")
    L.append("  Either way to Chris with the per-seed table above.")
    lv = [a for a, _ in LEVELS15 if a in S and S[a]["est"] >= 2]
    div = [a for a in lv if S[a]["estp"][0] is not None and S[a]["estp"][0] <= -0.30 and S[a]["estp"][1] >= 3]
    V["div"] = div
    L.append(f"- Divergence: levels read (>= 2 established seeds): {' '.join(lv) or 'none'}; with R gap <= -0.30 and breadth >= 3: {' '.join(div) or 'none'} -> "
             + ("exp010's registered conclusion is revised and goes to Chris" if div else
                "exp010's conclusion stands over 0.25-1: no fixed load gives both a persisting herd and divergence"))
    return L, V

def selftest(bad=False):
    import sched_tab
    ok = True
    def check(name, got, want):
        nonlocal ok
        good = got == want; ok &= good
        print(("ok   " if good else "FAIL ") + name + ("" if good else f": got {got!r}, want {want!r}"))
    def mk(wt, est=8, km=600, R=-0.15, n=1, span=350):
        runs = [{"seed": s, "q1": "grew", "span": span if s <= wt else 0, "R": R, "J": km, "late": None, "end": 3600} for s in range(1, 9)]
        return {"est": est, "km": km, "estp": (R, n, 0.3), "runs": runs}
    def build(w=(0, 0, 2, 4, 6, 7), est=(8, 8, 8, 8, 8, 8), km=(528, 600, 700, 900, 1200, 1614),
              R=(-0.104, -0.12, -0.15, -0.2, -0.22, -0.247), n=(1,) * 6, span=(350,) * 6):
        S = {a: mk(w[i], est[i], km[i], R[i], n[i], span[i]) for i, a in enumerate(SWEEP)}
        S["LOADLO"] = mk(0, 8, 501, -0.055, 0); return S
    V = lambda **k: read15(build(**k))[1]
    # the span, against exp010's Q1 code on a planted series (100-year means under 60 from 600 to 950, J 1200)
    hs = [(y, 30 if 600 <= y <= 950 else 80, 10 if 600 <= y <= 950 else 90) for y in range(501, 2000, 3)]
    check("span: planted 600-950 under 60 before J", wait_span(hs, 1200), (348, 10))
    check("span: the run after J is not counted", wait_span(hs, 700)[0], 99)
    hs2 = [(y, 30 if y >= 1000 else 80, 5) for y in range(501, 4000, 3)]
    check("span: unestablished run counted to the end", wait_span(hs2, None)[0] >= 2900, True)
    check("cp: 4 of 8", tuple(round(x, 3) for x in cp(4, 8)), (0.157, 0.843))
    check("cp: 0 of 8", tuple(round(x, 3) for x in cp(0, 8)), (0.0, 0.369))
    check("cp: 8 of 8", tuple(round(x, 3) for x in cp(8, 8)), (0.631, 1.0))
    check("p1 holds at 6 in every new level", V(est=(8, 6, 6, 6, 6, 8))["p1"], True)
    check("p1 fails at 5 in one new level", V(est=(8, 6, 6, 5, 6, 8))["p1"], False)
    check("p2 holds: 0 1 3 5 7 7", V(w=(0, 1, 3, 5, 7, 7))["p2"], True)
    check("p2 fails: a fall of 1, 0 3 2 5 7 7 (graded, not non-decreasing)", V(w=(0, 3, 2, 5, 7, 7))["p2"], False)
    check("p2 fails: one new level in 2-6", V(w=(0, 0, 0, 3, 7, 7))["p2"], False)
    check("p2 fails: not monotone overrides graded, 0 4 6 3 5 8", V(w=(0, 4, 6, 3, 5, 8))["p2"], False)
    check("p3 holds with ties and '-' last", V(km=(528, 600, 600, None, None, None))["p3"], True)
    check("p3 fails: 700 before 600", V(km=(528, 700, 600, 900, 1200, 1614))["p3"], False)
    check("p3 fails: '-' before a median", V(km=(528, 600, (700 if bad else None), 900, 1200, 1614))["p3"], False)
    check("p3 floor note", "floor carry no information: LOAD05 LOAD06" in "\n".join(read15(build(km=(501, 501, 600, 900, 1200, 1614)))[0]), True)
    check("p4 holds", V()["p4"], True)
    check("p4 holds at the bounds -0.05 and -0.30", V(R=(-0.104, -0.05, -0.1, -0.2, -0.30, -0.247))["p4"], True)
    check("p4 fails at -0.31", V(R=(-0.104, -0.12, -0.15, -0.2, (-0.30 if bad else -0.31), -0.247))["p4"], False)
    check("p4 fails at -0.04", V(R=(-0.104, -0.04, -0.15, -0.2, -0.22, -0.247))["p4"], False)
    check("p4 fails: LOAD09 not more negative than LOAD06", V(R=(-0.104, -0.20, -0.15, -0.2, -0.20, -0.247))["p4"], False)
    check("p4 fails: a new level with no established seed", V(R=(-0.104, None, -0.15, -0.2, -0.22, -0.247))["p4"], False)
    check("waiting: no level intermediate, switch between 0.8 and 0.9", V(w=(0, 0, 1, (2 if bad else 1), 8, 7))["wait"], ("switch", 0.8, 0.9))
    check("waiting: switch between 0.5 and 0.6", V(w=(0, 7, 8, 8, 8, 7))["wait"], ("switch", 0.5, 0.6))
    check("waiting: one intermediate level located at 0.8", V(w=(0, 0, 1, 4, 8, 7))["wait"], ("located", 0.8))
    check("waiting: two intermediate levels graded", V(w=(0, 0, 2, 6, 8, 8))["wait"], ("graded", (0.7, 0.8)))
    check("waiting: a fall of 2 is not monotone, read first", V(w=(0, 4, 6, (5 if bad else 4), 6, 8))["wait"], ("not monotone", ((0.7, 0.8),)))
    check("waiting: a fall of 1 is not 'not monotone'", V(w=(0, 4, 6, 5, 6, 8))["wait"][0], "graded")
    check("waiting: none in 0.5-1 when all low", V(w=(0, 0, 1, 1, 0, 1))["wait"][0], "no switch in 0.5-1")
    check("waiting: cut-dependent when spans sit between 300 and 400", V(w=(0, 0, 2, 4, 6, 7), span=(350,) * 6)["cutdep"], True)
    check("waiting: not cut-dependent when spans are all 450", V(w=(0, 0, 2, 4, 6, 7), span=(450,) * 6)["cutdep"], False)
    check("divergence: -0.30 and breadth 3 revises", V(R=(-0.104, -0.12, -0.15, -0.2, -0.30, -0.247), n=(1, 1, 1, 1, 3, 1))["div"], ["LOAD09"])
    check("divergence: -0.29 and breadth 3 stands", V(R=(-0.104, -0.12, -0.15, -0.2, -0.29, -0.247), n=(1, 1, 1, 1, 3, 1))["div"], [])
    check("divergence: -0.35 and breadth 2 stands", V(R=(-0.104, -0.12, -0.15, -0.2, -0.35, -0.247), n=(1, 1, 1, 1, 2, 1))["div"], [])
    check("divergence: a level with 1 established is not read", V(R=(-0.104, -0.12, -0.15, -0.2, -0.35, -0.247), n=(1, 1, 1, 1, 4, 1), est=(8, 8, 8, 8, 1, 8))["div"], [])
    rs = [{"seed": 1, "span": 400, "R": -0.3}, {"seed": 2, "span": 300, "R": -0.1}, {"seed": 3, "span": 299, "R": -0.1},
          {"seed": 4, "span": 0, "R": -0.05}]
    check("waited split at 300 (300 counts, 299 does not)", split_waited(rs), "waited -0.200 (n 2: s1 -0.300, s2 -0.100); did not wait -0.075 (n 2: s3 -0.100, s4 -0.050)")
    check("cls: waited, still waiting", cls15({"span": 3000, "J": None, "late": None, "q1": "never"}), "waited, still")
    check("cls: waited, crossing late", cls15({"span": 3000, "J": None, "late": 3708, "q1": "never (late 3708)"}), "waited, late 3708")
    B = {"seed": 1, "minLoad": 1, "herdPerHerder": 1e9, "offtakeRate": 0.15, "runOffLoss": 1, "logHistDepth": 400}
    P = dict(B, minLoad=0.6, spookFixed=0, spookSchedule="", logHistDepth=800)
    g = lambda P: (lambda: sched_tab.guard(P, B, {"minLoad": 0.6}, True, IDENT15))
    def stops(f):
        try: f(); return False
        except sched_tab.GuardFail: return True
    check("guard: LOAD06 = LOAD1 but minLoad passes", stops(g(P)), False)
    check("guard: minLoad 0.7 for LOAD06 stops", stops(g(dict(P, minLoad=(0.6 if bad else 0.7)))), True)
    check("guard: offtakeRate changed stops", stops(g(dict(P, offtakeRate=0.2))), True)
    check("guard: spookSchedule set stops", stops(g(dict(P, spookSchedule="0:0.005"))), True)
    check("guard: spookFixed set stops", stops(g(dict(P, spookFixed=0.02))), True)
    check("guard: a new key with no identity value stops", stops(g(dict(P, newKey=1))), True)
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__" and sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest(sys.argv[2:3] == ["bad"]) else 1)
if __name__ == "__main__": main()
