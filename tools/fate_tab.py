# fate_tab.py: exp020 follow-up scorer, what happens after the spook (analysis session, 2026-11-25; EXPLOG "exp020
# follow-up, 2026-11-25: what happens after the spook" fe1ba0d, its note c4dd5dd, and "exp020 follow-up amendment"
# ecc681e and "exp020 follow-up amendment 2" f0e1d2e, which govern; Chris: "check the run-off, rejoin and refetch R").
#   python tools/fate_tab.py "DIR[;DIR...]" ARM,ARM... [--perseed] [--checks] [--bad lostR|ranOff|walk|count|night|phase]
#   python tools/fate_tab.py selftest [--bad camp|d5|floor|phase|rule]
# Reads exp020's runs (logLedger=1, annual rows; src/world.js newLedger names every field). Phases per run as ledger_tab
# (its jJ and phases: A = 401..J-100, T = max(401, J-99)..J, B = J+1..J+100, C = J+101..last; no J: A runs to the end and
# the seed is named). Pooled over the three camps; origin o0 = captured itself (gsc 0), o1 = herd-born, as the ledger
# assigns it at each event. Settings printed per arm: alarmSpread (0: every ranOff is a spooked goat), alarmLearn (0: no
# fear lesson between spooked and ranOff, so their R x fear differ only by who bolts beyond keepRadius), penning, economy.
# Per seed, arm, phase and origin, summed over the phase's rows and camps:
#   walk     midday walking goat-days (day.walk[o] = [n, R, R x fear, rate]); mean R per goat-day
#   stock0   R0, pooled by goats (amendment 2 b): the summed R (and R x fear) of the origin's stock at each year Y-1 end
#            (stock[o] = [n, R, R x fear, fear], the row before), over the phase's years Y, / the summed stock count; its
#            n, for the floor, is that summed count (goat-years)
#   spooked, caught, ranOff, rejoined, refetched   events (ev[k][o] = [n, R, R x fear], logged at the event)
#   lostRun, lostNight   flows (flow[k][o] = [n, R]; R only)
#   ref+lost   refetched and lostRun pooled (the goats the herder reached and tested)
# Count floor (ecc681e): a mean is read only with n >= 20 (goat-days for walk; goat-years for stock0; events or goats
# otherwise; for ref+lost, the pooled count). A d is read only when both of its terms are read.
#   d0 = walk - stock0, d1 = spooked - walk, d2 = ranOff - spooked, d3 = rejoined - ranOff, d4 = refetched - ranOff,
#   d5 = lostRun - ranOff, d6 = lostNight - walk, d7 = lostRun - refetched, d8 = ref+lost - ranOff.
#   So lostRun - R0 = d0 + d1 + d2 + d5 and lostNight - R0 = d0 + d6 (checked in the selftest).
# The same differences in mean R x fear are printed beside each d where both terms log it (d0-d4; the flows log R only).
# Fates per ranOff (ranOff read): rejoined, refetched, lostRun, and the rest (1 - the three: let go near the herder,
# brought in at dusk, cleared without the stray test, lost at dusk, died while loose; ecc681e); and attempted = refetched
# + lostRun, printed beside E2 and E3b per seed (amendment 2 c).
# Over seeds: the median (min to max; seeds read) of read seeds' values: descriptive. Verdicts are per seed.
# Scored (ecc681e, f0e1d2e a; REF; herd-born): a seed holds an expectation only if every one of its cells holds; the
# verdict is the count of seeds that hold, 6+ of 8, an unread cell counting against; the per-cell counts and the seeds
# read in every cell are printed. E2: d5 > 0 and d3 < 0, each in A and in T (four cells). E3a: d7 > 0 in A and in T. E3b:
# d8 > 0 in A and in T. Beside each verdict, the f0e1d2e e disclosure (seed-mean signs largely visible; the per-seed
# count is the test). Reported, not scored: E1 (d2 by phase and origin; ecc681e
# struck fe1ba0d's |d2| < 0.01, so no count is printed), d5 > d1, d0, d4, d6, fates, R x fear by step, captured goats, LOAD05, and A+T pooled.
# Checks before any reading (each stops the tool):
#   - per row, the ledger's counts summed over camps and origins equal the year row's spooked, alarmCaught, ranOff,
#     rejoined, refetched and runOffLost, and lostNight = escaped - runOffLost;
#   - ledger_tab's own row checks (check_rows: annual rows, stock = herded, stock mean R = herdTraitMeans R, load);
#   - walk mean R per seed, phase and origin equals ledger_tab.summ's Rwalk (what ledger_tab prints), to 1e-12;
#   - the phases partition 401..last: in order, each starting the year after the last ends, none empty.
#   --checks runs only these and prints no event R (for use before the reviewer's pass).
# Bad cases (each must stop the tool, or print its expected shift beside the observed one and stop; not a reading):
#   --bad lostR raises one lostRun goat's R by 1 in one row (REF s1, the first row of phase A with a herd-born lostRun;
#     the first run read if no REF s1): d5 and d7 must move by +1 / n(lostRun) of that seed, phase and origin.
#   --bad ranOff raises one ranOff goat's R by 1 the same way: d2 must move by +1 / n(ranOff), d3, d4, d5 and d8
#     by -1 / n(ranOff).
#   --bad walk shifts fate_tab's own herd-born walk mean R by 1e-6 (must stop on the walk check against ledger_tab).
#   --bad count adds 1 to one row's ledger ranOff count; --bad night adds 1 to one row's ledger lostNight count (each must
#     stop on the count checks).
#   --bad phase starts B at J (ledger_tab.phases' own bad case), overlapping T (must stop on the phase check).
#   selftest: a planted three-row, three-camp ledger with known means (d0 0.5 - 54/110, which tells goat pooling from
#     walking-weighted pooling, d1 +0.02, d2 +0.02, d3 -0.04, d4 +0.01,
#     d5 +0.11, d6 unread under the floor, d7 +0.10, d8 +0.06; fates 3/8, 2/8, 2/8, 1/8), the two identities, the count
#     checks, the phase check, both plants (shifts against 1/n), and the verdict rule (two cells, each holding in 6 of 8
#     seeds but in different seeds: 4 seeds hold; one unread cell counts against). selftest --bad camp drops camp 2 from the sums;
#     --bad d5 takes d5 against spooked; --bad floor reads means at n >= 1; --bad phase starts B at J; --bad rule reads the unread cell as holding. Each must fail.
import json, os, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_tab

EV = ["spooked", "caught", "ranOff", "rejoined", "refetched"]
FL = ["lostRun", "lostNight"]
STEPS = ["stock0", "walk"] + EV + FL + ["ref+lost"]
SHOW = ["stock0", "walk", "spooked", "ranOff", "rejoined", "refetched", "lostRun", "lostNight", "ref+lost"]
ROWF = [("spooked", "ev", "spooked"), ("caught", "ev", "alarmCaught"), ("ranOff", "ev", "ranOff"),
        ("rejoined", "ev", "rejoined"), ("refetched", "ev", "refetched"), ("lostRun", "flow", "runOffLost")]
DEF = {"d0": ("walk", "stock0"), "d1": ("spooked", "walk"), "d2": ("ranOff", "spooked"), "d3": ("rejoined", "ranOff"),
       "d4": ("refetched", "ranOff"), "d5": ("lostRun", "ranOff"), "d6": ("lostNight", "walk"), "d7": ("lostRun", "refetched"),
       "d8": ("ref+lost", "ranOff")}
DS = list(DEF)
PH = ledger_tab.PH
FLOOR = 20
R0NOTE = ("R0 (stock0) over a phase, pooled by goats (amendment 2 b): the summed R (and R x fear) of the origin's stock at each"
          " year Y-1 end (the ledger's stock in the row before, summed over camps), over the phase's years Y, divided by the summed"
          " stock count; the floor applies to that summed count (goat-years).")

def tot(rows, o, prev, bad=None):
    """Sums over rows and camps, origin o: step -> [n, R, RF] (RF None for the flows and ref+lost). prev: label -> the
    previous year-end row (for stock0)."""
    t = {k: [0, 0.0, 0.0] for k in STEPS}
    w0 = [0, 0.0, 0.0]   # stock0 (amendment 2 b): summed count, R, R x fear of the origin's stock at each year Y-1 end
    for r in rows:
        Ls = r["ledger"][:2] if bad == "camp" else r["ledger"]
        for L in Ls:
            w = L["day"]["walk"][o]
            for i in range(3): t["walk"][i] += w[i]
            for k in EV:
                for i in range(3): t[k][i] += L["ev"][k][o][i]
            for k in FL:
                for i in range(2): t[k][i] += L["flow"][k][o][i]
        p = prev.get(r["year"])
        if p is not None:
            for L in (p["ledger"][:2] if bad == "camp" else p["ledger"]):
                for i in range(3): w0[i] += L["stock"][o][i]
    t["stock0"] = list(w0)
    for k in FL: t[k][2] = None
    t["ref+lost"] = [t["refetched"][0] + t["lostRun"][0], t["refetched"][1] + t["lostRun"][1], None]
    return t

def stats(t, bad=None):
    fl = 1 if bad == "floor" else FLOOR
    def m(k, i=1):
        n = t[k][0]
        if n < fl or (i == 2 and t[k][2] is None): return None
        return t[k][i] / n if n else None
    out = {"n": {k: t[k][0] for k in STEPS}, "R": {k: m(k) for k in STEPS}, "RF": {k: m(k, 2) for k in STEPS}}
    def dif(a, b, i):
        x, y = (out["R"] if i == 1 else out["RF"])[a], (out["R"] if i == 1 else out["RF"])[b]
        return x - y if x is not None and y is not None else None
    D = dict(DEF)
    if bad == "d5": D["d5"] = ("lostRun", "spooked")
    out["d"] = {k: dif(a, b, 1) for k, (a, b) in D.items()}
    out["dRF"] = {k: dif(a, b, 2) for k, (a, b) in D.items()}
    ro = t["ranOff"][0]
    out["fate"] = {k: (t[k][0] / ro if ro >= fl else None) for k in ("rejoined", "refetched", "lostRun")}
    out["fate"]["rest"] = (1 - sum(out["fate"].values())) if ro >= fl else None
    out["fate"]["attempted"] = (out["fate"]["refetched"] + out["fate"]["lostRun"]) if ro >= fl else None
    return out

def check_counts(d, name, bad=None):
    ys = d["years"]
    if bad in ("count", "night"):
        for r in ys:
            if bad == "count" and r["ledger"][0]["ev"]["ranOff"][0][0]: r["ledger"][0]["ev"]["ranOff"][0][0] += 1; break
            if bad == "night" and r["ledger"][0]["flow"]["lostNight"][0][0]: r["ledger"][0]["flow"]["lostNight"][0][0] += 1; break
    for r in ys:
        for lab, kind, rf in ROWF:
            v = sum(L[kind][lab][o][0] for L in r["ledger"] for o in (0, 1))
            if v != r.get(rf, 0): sys.exit(f"check failed: {name} year {r['year'] + 1}: ledger {lab} {v}, year row {rf} {r.get(rf)}")
        v = sum(L["flow"]["lostNight"][o][0] for L in r["ledger"] for o in (0, 1))
        if v != r.get("escaped", 0) - r.get("runOffLost", 0):
            sys.exit(f"check failed: {name} year {r['year'] + 1}: ledger lostNight {v}, escaped - runOffLost {r.get('escaped', 0) - r.get('runOffLost', 0)}")

def check_phases(ph, last, name):
    ks = [k for k in PH if k in ph]; at = 401
    for k in ks:
        a, b = ph[k]
        if a != at or b < a or b > last: sys.exit(f"check failed: {name}: phases {ph} do not partition 401..{last} (at {k})")
        at = b + 1
    if at != last + 1 and ks[-1] != "B": sys.exit(f"check failed: {name}: phases {ph} end at {at - 1}, not {last}")
    if ks[-1] == "B" and ph["B"][1] != last: sys.exit(f"check failed: {name}: phases {ph} end before {last}")

def plant(rows, a, b, o, kind, k):
    """Raise one goat's R by 1 in channel k (kind 'flow' or 'ev'), origin o, in the first row of a..b that has one."""
    for r in rows:
        if a <= r["year"] + 1 <= b:
            for L in r["ledger"]:
                if L[kind][k][o][0]: L[kind][k][o][1] += 1.0; return r["year"] + 1
    return None

def prevmap(rows): return {b["year"]: a for a, b in zip(rows, rows[1:])}

def selftest(bad):
    def L(walk, ev, fl, stock=(0, 0.0, 0.0, 0.0)):
        return {"day": {"walk": [[0, 0, 0, 0], list(walk) + [0]]}, "ev": {k: [[0, 0, 0], list(ev.get(k, [0, 0, 0]))] for k in EV},
                "flow": {k: [[0, 0], list(fl.get(k, [0, 0]))] for k in FL}, "stock": [[0, 0.0, 0.0, 0.0], list(stock)]}
    # origin 1 totals over labels 401-402: walk 1000 R 500 (0.50) RF 100; spooked 100 R 52 (0.52) RF 10; ranOff 80 R 43.2
    # (0.54) RF 8; rejoined 30 R 15 (0.50) RF 1.5; refetched 20 R 11 (0.55) RF 1.1; lostRun 20 R 13 (0.65); lostNight 10 R 7
    # (0.70: under the floor); stock at the year ends before them 50 (R 24, RF 2.4) and 60 (R 30, RF 3.0), pooled by goats:
    # R0 54/110, RF0 5.4/110, n 110 (weighting by walking goat-days, 500 each, would give 0.49: the test tells them apart);
    # ref+lost 40 R 24 (0.60)
    rows = [{"year": 399, "ledger": [L([0, 0, 0], {}, {}, (50, 24.0, 2.4, 5.0)), L([0, 0, 0], {}, {}), L([0, 0, 0], {}, {})]},
            {"year": 400, "ledger": [L([400, 200.0, 40.0], {"spooked": [40, 20.0, 4.0], "ranOff": [30, 16.2, 3.0]}, {"lostRun": [10, 6.0]}, (40, 20.0, 2.0, 4.0)),
                                     L([100, 50.0, 10.0], {"rejoined": [10, 5.0, 0.5]}, {}, (20, 10.0, 1.0, 2.0)),
                                     L([0, 0.0, 0.0], {"refetched": [10, 5.0, 0.5]}, {"lostNight": [10, 7.0]})]},
            {"year": 401, "ledger": [L([300, 150.0, 30.0], {"spooked": [60, 32.0, 6.0], "ranOff": [50, 27.0, 5.0]}, {}),
                                     L([200, 100.0, 20.0], {"rejoined": [20, 10.0, 1.0]}, {"lostRun": [10, 7.0]}),
                                     L([0, 0.0, 0.0], {"refetched": [10, 6.0, 0.6]}, {})]}]
    pv = prevmap(rows); win = [r for r in rows if 401 <= r["year"] + 1 <= 402]
    s = stats(tot(win, 1, pv, bad), bad)
    want = {"d0": 0.5 - 54 / 110, "d1": 0.02, "d2": 0.02, "d3": -0.04, "d4": 0.01, "d5": 0.11, "d6": None, "d7": 0.10, "d8": 0.06}
    for k, v in want.items():
        g = s["d"][k]
        if (v is None) != (g is None) or (v is not None and abs(g - v) > 1e-9): sys.exit(f"selftest failed: {k} {g}, planted {v}")
    for k, v in {"rejoined": 3 / 8, "refetched": 2 / 8, "lostRun": 2 / 8, "rest": 1 / 8}.items():
        if abs(s["fate"][k] - v) > 1e-9: sys.exit(f"selftest failed: fate {k} {s['fate'][k]}, planted {v}")
    if abs(s["RF"]["ranOff"] - 0.1) > 1e-9 or s["RF"]["lostRun"] is not None or abs(s["dRF"]["d0"] - (0.1 - 5.4 / 110)) > 1e-9:
        sys.exit(f"selftest failed: R x fear (ranOff {s['RF']['ranOff']}, d0 {s['dRF']['d0']})")
    if s["n"]["stock0"] != 110: sys.exit(f"selftest failed: stock0 n {s['n']['stock0']}, planted 110")
    if abs(s["fate"]["attempted"] - 4 / 8) > 1e-9: sys.exit(f"selftest failed: attempted share {s['fate']['attempted']}, planted 0.5")
    D = s["d"]
    if abs(s["R"]["lostRun"] - s["R"]["stock0"] - (D["d0"] + D["d1"] + D["d2"] + D["d5"])) > 1e-9: sys.exit("selftest failed: lostRun - R0 identity")
    t1 = tot(win, 1, pv, bad); t1["lostNight"][0] = 20; s1 = stats(t1, bad)   # lift the floor to check the second identity
    if abs(s1["R"]["lostNight"] - s1["R"]["stock0"] - (s1["d"]["d0"] + s1["d"]["d6"])) > 1e-9: sys.exit("selftest failed: lostNight - R0 identity")
    # the count checks: matching year-row fields pass; one wrong count, or one wrong lostNight, must stop
    for r in rows:
        for lab, kind, rf in ROWF: r[rf] = sum(L[kind][lab][o][0] for L in r["ledger"] for o in (0, 1))
        r["escaped"] = r["runOffLost"] + sum(L["flow"]["lostNight"][o][0] for L in r["ledger"] for o in (0, 1))
    check_counts({"years": rows}, "selftest")
    for f in ("ranOff", "escaped"):
        rows[1][f] += 1
        try: check_counts({"years": rows}, "selftest"); sys.exit(f"selftest failed: count check passed a wrong {f}")
        except SystemExit as e:
            if "check failed" not in str(e): raise
        rows[1][f] -= 1
    # the phase check on ledger_tab's phases: J 767 to 1600 passes; B at J must stop (selftest --bad phase plants it)
    check_phases(ledger_tab.phases(767, 1600, "phase" if bad == "phase" else None), 1600, "selftest")
    check_phases(ledger_tab.phases(None, 1600), 1600, "selftest"); check_phases(ledger_tab.phases(450, 1600), 1600, "selftest")
    try: check_phases(ledger_tab.phases(767, 1600, "phase"), 1600, "selftest"); sys.exit("selftest failed: phase check passed B at J")
    except SystemExit as e:
        if "check failed" not in str(e): raise
    # the plants: lostRun +1 moves d5 and d7 by +1/20; ranOff +1 moves d2 by +1/80, d3, d4, d5 and d8 by -1/80
    for kind, k, n, mv in (("flow", "lostRun", 20, {"d5": 1, "d7": 1}), ("ev", "ranOff", 80, {"d2": 1, "d3": -1, "d4": -1, "d5": -1, "d8": -1})):
        r2 = json.loads(json.dumps(rows)); pv2 = prevmap(r2); w2 = [r for r in r2 if 401 <= r["year"] + 1 <= 402]
        a0 = stats(tot(w2, 1, pv2, bad), bad); plant(r2, 401, 402, 1, kind, k); a1 = stats(tot(w2, 1, pv2, bad), bad)
        for dk, sg in mv.items():
            if abs(a1["d"][dk] - a0["d"][dk] - sg / n) > 1e-9: sys.exit(f"selftest failed: {k} plant moved {dk} by {a1['d'][dk] - a0['d'][dk]}, expected {sg / n}")
    # the verdict rule: two cells over 8 seeds; each cell holds in 6 seeds, but in different seeds, so only 4 seeds hold both
    # (a per-cell count would say 6 and 6: the rule must give 4); one seed with a cell unread counts against
    pc = {"A": {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: False, 8: False},
          "T": {1: True, 2: True, 3: True, 4: True, 5: False, 6: None, 7: True, 8: True}}
    if bad == "rule": pc["T"][6] = True   # the unread cell read as holding: s6 joins, and the check must fail
    h, u, _ = seed_holds(lambda s_, p, f: pc[p][s_], range(1, 9), {"A": ("A", None), "T": ("T", None)})
    if h != [1, 2, 3, 4] or u != [6]: sys.exit(f"selftest failed: verdict rule gives holding {h}, unread {u}; planted [1, 2, 3, 4], [6]")
    print("selftest: planted means (d0-d8 with d6 under the floor, fates, R x fear), the two identities, the count checks (pass, and stop on a"
          " wrong count or lostNight), the phase check (passes; stops on B at J), the lostRun and ranOff plants (shifts = 1/n), the verdict rule (4 seeds hold both cells where each cell holds in 6; an unread cell counts against): ok")

def seed_holds(test, seeds, cells):
    """Amendment 2 a: a seed holds only if every cell holds (True); an unread cell (None) counts against.
    cells: key -> (phase, f); test(s, phase, f) -> True / False / None. Returns (seeds holding, seeds with a cell unread, per-seed results)."""
    hold, unread, R = [], [], {}
    for s in seeds:
        r = {key: test(s, p, f) for key, (p, f) in cells.items()}; R[s] = r
        if any(x is None for x in r.values()): unread.append(s)
        if all(x is True for x in r.values()): hold.append(s)
    return hold, unread, R

def med(xs):
    xs = [x for x in xs if x is not None]
    return (statistics.median(xs), min(xs), max(xs), len(xs)) if xs else None

def main():
    a = sys.argv[1:]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if a and a[0] == "selftest": selftest(bad); return
    selftest(None)
    per = "--perseed" in a; only = "--checks" in a
    a = [x for x in a if x not in ("--perseed", "--checks")]
    dirs, arms = a[0], a[1].split(",")
    R = ledger_tab.load_runs(dirs, arms); V, INFO, SET = {}, {}, {}
    pick = ("REF", 1) if 1 in R.get("REF", {}) else (arms[0], sorted(R[arms[0]])[0]); pl = None
    for arm in arms:
        for s, f in sorted(R.get(arm, {}).items()):
            d = json.load(open(f, encoding="utf-8")); name = f"{arm} s{s}"; P = ledger_tab.params(d)
            SET.setdefault(arm, set()).add(tuple((k, P.get(k)) for k in ("alarmSpread", "alarmLearn", "penning", "economy")))
            ledger_tab.check_rows(d, name); check_counts(d, name, bad)
            rows = d["years"]; last = rows[-1]["year"] + 1; J = ledger_tab.jJ(d)
            ph = ledger_tab.phases(J, last, "phase" if bad == "phase" else None); check_phases(ph, last, name)
            pv = prevmap(rows); acc = ledger_tab.account(rows)
            INFO.setdefault(arm, {})[s] = {"J": J, "ph": ph}
            if "T" in ph:   # A+T pooled (descriptive)
                lo, hi = (ph["A"][0] if "A" in ph else ph["T"][0]), ph["T"][1]
                INFO[arm][s]["AT"] = stats(tot([r for r in rows if lo <= r["year"] + 1 <= hi], 1, pv))
            for p, (x, y) in ph.items():
                rs = [r for r in rows if x <= r["year"] + 1 <= y]
                sm = ledger_tab.summ(d, rows, acc, x, y)
                for o in (0, 1):
                    t = tot(rs, o, pv); wr = t["walk"][1] / t["walk"][0] if t["walk"][0] else None
                    if bad == "walk" and o == 1 and wr is not None: wr += 1e-6   # must stop below
                    rw = sm[o]["Rwalk"]
                    if (rw is None) != (wr is None) or (rw is not None and abs(rw - wr) > 1e-12):
                        sys.exit(f"check failed: {name} phase {p} o{o}: walk R {wr}, ledger_tab Rwalk {rw}")
                    V.setdefault(arm, {}).setdefault(p, {}).setdefault(o, {})[s] = stats(t)
                if bad in ("lostR", "ranOff") and (arm, s) == pick and pl is None and p == ("A" if "A" in ph else "T"):
                    kind, k, mv = (("flow", "lostRun", {"d5": 1, "d7": 1}) if bad == "lostR" else ("ev", "ranOff", {"d2": 1, "d3": -1, "d4": -1, "d5": -1, "d8": -1}))
                    t0 = tot(rs, 1, pv); lab = plant(rows, x, y, 1, kind, k); t1 = tot(rs, 1, pv)
                    s0, s1 = stats(t0), stats(t1); n = t0[k][0]
                    pl = (name, p, k, lab, n, [(dk, (s1["d"][dk] - s0["d"][dk]) if s1["d"][dk] is not None and s0["d"][dk] is not None else None, sg / n) for dk, sg in mv.items()])
    if only:
        print(f"fate_tab --checks: {sum(len(v) for v in INFO.values())} runs; per row the ledger's spooked, caught, ranOff, rejoined, refetched"
              " and lostRun counts equal the year row's spooked, alarmCaught, ranOff, rejoined, refetched and runOffLost, and lostNight ="
              " escaped - runOffLost; ledger_tab's row checks pass; walk mean R equals ledger_tab's Rwalk in every seed, phase and origin;"
              " the phases partition 401..last. No event R printed.")
        print(R0NOTE)
        for arm in INFO: print(f"  {arm}: settings {sorted(SET[arm])}; J " + ", ".join(f"s{s} {v['J']}" for s, v in sorted(INFO[arm].items())))
        return
    if bad in ("lostR", "ranOff"):
        name, p, k, lab, n, sh = pl
        ok = all(o_ is not None and abs(o_ - e) < 1e-9 for _, o_, e in sh)
        print(f"*** --bad {bad}: {name} phase {p} herd-born, one {k} goat's R raised by 1 in year {lab} (n({k}) {n}): "
              + "; ".join(f"{dk} moved {'-' if o_ is None else f'{o_:+.6f}'}, expected {e:+.6f}" for dk, o_, e in sh)
              + f": {'as expected' if ok else 'NOT as expected'}. Not a reading. ***")
        sys.exit(1)
    f3 = lambda x: "-" if x is None else f"{x:.3f}"; f4 = lambda x: "-" if x is None else f"{x:+.4f}"
    fm = lambda m, f: "-" if m is None else f"{f(m[0])} ({f(m[1])} to {f(m[2])}; {m[3]})"
    print(f"\nexp020 follow-up (fate_tab; ecc681e): checks passed on {sum(len(v) for v in INFO.values())} runs. Pooled over camps; o0 captured"
          f" itself, o1 herd-born. Cells: median over read seeds (min to max; seeds read); a mean is read with n >= {FLOOR}.")
    print(R0NOTE)
    for arm in arms:
        if arm not in V: continue
        print(f"\n{arm}: settings {sorted(SET[arm])}; J per seed " + ", ".join(f"s{s} {v['J']}" for s, v in sorted(INFO[arm].items())))
        nj = [s for s, v in INFO[arm].items() if v["J"] is None]
        if nj: print(f"  no J (A runs to the end): {nj}")
        def table(title, cols, get, f):
            print(f"\n{arm} {title}\n| phase | origin | " + " | ".join(cols) + " |\n|---|---|" + "---|" * len(cols))
            for p in PH:
                for o in (0, 1):
                    if p not in V[arm]: continue
                    vs = list(V[arm][p][o].values())
                    print(f"| {p} | o{o} | " + " | ".join(fm(med([get(v, c) for v in vs]), f) for c in cols) + " |")
        table("counts (stock0: the summed year-end count over the phase, goat-years)", SHOW, lambda v, c: v["n"][c], lambda x: f"{x:.0f}")
        table("mean R (read at n >= 20)", SHOW, lambda v, c: v["R"][c], f3)
        table("mean R x fear (the flows log R only)", ["stock0", "walk", "spooked", "ranOff", "rejoined", "refetched"], lambda v, c: v["RF"][c], f3)
        table("fates per ranOff (rest = 1 - the three: unlogged fates)", ["rejoined", "refetched", "lostRun", "rest"], lambda v, c: v["fate"][c], f3)
        table("steps, mean R: d0 walk-stock0, d1 spooked-walk, d2 ranOff-spooked, d3 rejoined-ranOff, d4 refetched-ranOff, d5 lostRun-ranOff,"
              " d6 lostNight-walk, d7 lostRun-refetched, d8 (refetched+lostRun)-ranOff", DS, lambda v, c: v["d"][c], f4)
        table("steps, mean R x fear (where both terms log it)", ["d0", "d1", "d2", "d3", "d4"], lambda v, c: v["dRF"][c], f4)
        if per:
            print(f"\n{arm} per seed: phase origin | n stock0/walk/spooked/ranOff/rejoined/refetched/lostRun/lostNight/ref+lost | mean R the same |"
                  " d0-d8 | R x fear d0-d4 | fates rejoined/refetched/lostRun/rest")
            for s in sorted(INFO[arm]):
                for p in PH:
                    for o in (0, 1):
                        v = V[arm].get(p, {}).get(o, {}).get(s)
                        if not v: continue
                        print(f"  {arm} s{s} {p} o{o} | " + "/".join(f"{v['n'][k]:.0f}" for k in SHOW) + " | " + "/".join(f3(v['R'][k]) for k in SHOW)
                              + " | " + " ".join(f4(v['d'][k]) for k in DS) + " | " + " ".join(f4(v['dRF'][k]) for k in ("d0", "d1", "d2", "d3", "d4"))
                              + " | " + "/".join(f3(v['fate'][k]) for k in ("rejoined", "refetched", "lostRun", "rest")))
    if "REF" not in V: return
    Rf = V["REF"]; seeds = sorted(INFO["REF"])
    def tst(s, p, o, f):
        v = Rf.get(p, {}).get(o, {}).get(s)
        return None if v is None else f(v)
    gt = lambda dk: (lambda v: None if v["d"][dk] is None else v["d"][dk] > 0)
    lt = lambda dk: (lambda v: None if v["d"][dk] is None else v["d"][dk] < 0)
    def scored(lab, cells, note):
        # amendment 2 a: a seed holds only if every cell holds; an unread cell counts against; 6+ of 8 seeds
        hold, unread, R_ = seed_holds(lambda s, p, f: tst(s, p, 1, f), seeds, cells)
        per = []
        for s in seeds:
            r = R_[s]
            per.append(f"s{s} " + " ".join(f"{key} {'-' if x is None else ('y' if x else 'n')}" for key, x in r.items()))
        cc = "; ".join(f"{key} {sum(1 for s in seeds if tst(s, p, 1, f) is True)} of {len(seeds)}" for key, (p, f) in cells.items())
        print(f"{lab}: {len(hold)} of {len(seeds)} seeds hold every cell (read in every cell: {len(seeds) - len(unread)}"
              + (f"; unread cell in s{','.join(map(str, unread))}" if unread else "") + f"): {'holds' if len(hold) >= 6 else 'fails'}")
        print(f"   per cell: {cc}; per seed: " + ", ".join(per))
        print(f"   beside it (amendment 2 e): {note}")
    SEEN = "its terms' seed-mean signs were largely visible before scoring (c4dd5dd, f0e1d2e e); the per-seed count is the test."
    print("\nExpectations (exp020 follow-up as amended, ecc681e and f0e1d2e; REF; herd-born; a seed holds only if every cell holds;"
          " 6+ of 8 seeds, an unread cell counting against)")
    scored("E2. d5 > 0 and d3 < 0, in A and in T", {"A d5>0": ("A", gt("d5")), "T d5>0": ("T", gt("d5")), "A d3<0": ("A", lt("d3")), "T d3<0": ("T", lt("d3"))},
           "refetched and rejoined R (seed means) and lost R pooled over run-off and night had been printed; " + SEEN)
    scored("E3a. d7 > 0 (lostRun - refetched), in A and in T", {"A": ("A", gt("d7")), "T": ("T", gt("d7"))},
           "refetched R (seed means) and lost R pooled had been printed; lostRun apart had not; " + SEEN)
    scored("E3b. d8 > 0 ((refetched+lostRun) - ranOff), in A and in T", {"A": ("A", gt("d8")), "T": ("T", gt("d8"))},
           "refetched R and pooled lost R had been printed; ranOff R had not; " + SEEN)
    f3 = lambda x: "-" if x is None else f"{x:.3f}"
    print("   beside d3 and d8 (amendment 2 c), herd-born fates per ranOff, rejoined / attempted (refetched + lostRun) / rest, per seed: "
          + ", ".join(f"s{s} " + " ".join(f"{p} " + "/".join(f3((Rf.get(p, {}).get(1, {}).get(s) or {"fate": {}})["fate"].get(k)) for k in ("rejoined", "attempted", "rest")) for p in ("A", "T")) for s in seeds))
    def reported(lab, cells):
        print(f"{lab} (reported, not scored): " + "; ".join(f"{key} {k} of {len(seeds)} (read {n})" for key, (k, n) in cells.items()))
    def cnt(p, o, f):
        vs = [Rf.get(p, {}).get(o, {}).get(s) for s in seeds]; r = [f(v) for v in vs if v is not None and f(v) is not None]
        return sum(1 for x in r if x), len(r)
    print("E1 (reported, not scored; ecc681e struck fe1ba0d's threshold): d2 by phase and origin is in the steps tables above, per seed with --perseed.")
    reported("d5 > d1, herd-born, A and T", {p: cnt(p, 1, lambda v: None if v['d']['d5'] is None or v['d']['d1'] is None else v['d']['d5'] > v['d']['d1']) for p in ("A", "T")})
    f4 = lambda x: "-" if x is None else f"{x:+.4f}"
    at = {s: INFO["REF"][s].get("AT") for s in seeds}
    print("   A+T pooled, herd-born (descriptive; not scored), per seed d3 / d5 / d7 / d8: "
          + ", ".join(f"s{s} " + " / ".join(f4(v['d'][k]) for k in ("d3", "d5", "d7", "d8")) for s, v in at.items() if v))


if __name__ == "__main__":
    main()
