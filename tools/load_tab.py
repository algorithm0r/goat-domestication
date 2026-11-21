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
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, flow_tab, jump_tab
gaps, herd, CORE = split_tab.gaps, split_tab.herd, split_tab.CORE
LEVELS = [("LOADLO", 0.25), ("LOAD05", 0.5), ("LOAD1", 1.0), ("LOAD2", 2.0), ("LOAD3", 3.0), ("LOADHI", 4.8)]

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else 0.0)

def score(f, y0, y1, load, aliased):
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
            "q1": q1, "ranOff": lr("ranOff"), "refetched": lr("refetched"), "escaped": lr("escaped")}

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
            "q1": q, "q1runs": [r["q1"] for r in runs]}

def main():
    a = sys.argv[1:]; alias = {}; y0, y1 = 3201, 4000
    if "--alias" in a: i = a.index("--alias"); alias = dict(x.split("=") for x in a[i + 1].split(",")); del a[i:i + 2]
    if "--window" in a: i = a.index("--window"); y0, y1 = (int(v) for v in a[i + 1].split("-")); del a[i:i + 2]
    F = {}
    for folder in a[0].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(2)) in F.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                F[m.group(1)][int(m.group(2))] = f
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not exp010 results ***")
    S = {}
    for arm, load in LEVELS + [("REF", None)]:
        src = alias.get(arm, arm)
        if src not in F: print(f"{arm}: no runs ({src})"); continue
        S[arm] = summary([score(f, y0, y1, load, arm in alias) for s, f in sorted(F[src].items())])
    print(f"\nyears {y0}-{y1}. est = seeds with herd >= 100 over the window; by-herd = established by the jump_tab criterion"
          " by the follow-up end (upper median of the established runs' years, not the KM median; late crossings); R, n, csire over all seeds | established seeds only")
    print("| arm | load | seeds | est | by-herd (upper median) | late | herd | R all | R est | n all | n est | csire all | csire est | offtake |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    f3 = lambda x: "-" if x is None else f"{x:+.3f}"
    for arm, load in LEVELS + [("REF", "grows")]:
        if arm not in S: continue
        v = S[arm]; (Ra, na, ca), (Re, ne, ce) = v["all"], v["estp"]
        f3u = lambda x: "-" if x is None else f"{x:.3f}"
        print(f"| {arm} | {load} | {v['n']} | {v['est']} | {v['J']} ({v['Jmed'] or '-'}) | {v['late']} | {v['herd']:.1f} | {f3(Ra)} | {f3(Re)} | "
              f"{na if na is not None else '-'} | {ne if ne is not None else '-'} | {f3u(ca)} | {f3u(ce)} | {f3u(v['off'])} |")
    print("\nObservable rates (amendment 071fd3e), per herd goat per recorded year, seed mean (SE): run-offs (ranOff), fetched"
          " back (refetched), lost (escaped)")
    print("| arm | run-offs | fetched back | lost |\n|---|---|---|---|")
    for arm, _ in LEVELS + [("REF", None)]:
        if arm in S: print(f"| {arm} | " + " | ".join("-" if S[arm]["loss"][k][0] is None else "{:.3f} ({:.3f})".format(*S[arm]["loss"][k]) for k in ("ranOff", "refetched", "escaped")) + " |")
    print("\nQ1, how herds established (amendment 071fd3e): at once = at the first testable year after 500; waited = a plateau"
          " first (the 100-year herd mean under 60 for 300+ consecutive years after 500, then established); grew = established"
          " later without such a plateau; never = not established by the follow-up end")
    for arm, _ in LEVELS + [("REF", None)]:
        if arm in S: print(f"  {arm}: " + ", ".join(f"{k} {n}" for k, n in sorted(S[arm]["q1"].items())) + "  [" + "; ".join(S[arm]["q1runs"]) + "]")
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

if __name__ == "__main__": main()
