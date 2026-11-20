# exp007_tab.py: the scorer for exp007 (the reviewer's design checks), from its pre-registration and amendments 1 and 2
# in EXPLOG (e20d071, 5157d3d and the amendment-2 commit). Analysis session, 2026-11-20.
#   python tools/exp007_tab.py EXP007_DIR REF_DIR[;REF_DIR...] [--alias ARM=SRC,...]
# EXP007_DIR holds LOADLO, LOADHI, CTLDEEP, CTLRAND, CTLSHAL, NOCULL (<ARM>_seed<S>.json); REF_DIR(s) hold REF (exp005 seeds
# 1-4 + exp006 seeds 5-8) and NONE (exp006). --alias maps an exp007 arm to another arm's files, only to test the scorer
# before exp007 exists (e.g. --alias LOADLO=noProv): an aliased table is a test, never a result.
# Window 3201-4000 (1-based) throughout. Registered measures: per arm herd (mean of year rows' herded), gaps
# (settle_tab.gaps), breadth n (core traits with abs(seed-mean gap) >= 0.10); established = herd >= 100 over the window;
# within each arm, the across-seed correlation of herd and R gap. Amendment measures: the herd/wild split
# (tools/split_tab.py, founders 301-400); realized offtake = sum of year rows' culledHerd / sum of their herded over the
# window (culled per year per herd goat); establishment year by herd size and by R (tools/jump_tab.py defaults: smoothed
# herd >= 100 held 400 y; R gap <= -0.30 held 300 y); the CTL arms on established seeds, each seed's herd beside its gaps.
# Prediction 3 (amended): CTLDEEP - CTLRAND on a core trait counts when abs(diff) > 0.10 AND > 2 SE (unpaired SE of the
# seed means), on established seeds if each CTL arm has at least 4, otherwise on all 8 (reported as not resolved on
# established herds); C's difference is the noise reference; "carried by" (amendment 2) = the component, herd change or
# wild change, that accounts for more than half of the gap difference (rule in carried() below); neither, or both: mixed.
import glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab, jump_tab
gaps, herd, CORE, TRAITS = split_tab.gaps, split_tab.herd, split_tab.CORE, split_tab.TRAITS
Y0, Y1 = 3201, 4000
ARMS = ["LOADLO", "LOADHI", "CTLDEEP", "CTLRAND", "CTLSHAL", "NOCULL"]

def files(folders):
    R = {}
    for folder in folders:
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    return R

def score_run(f):
    d = json.load(open(f, encoding="utf-8"))
    sp = split_tab.split(d, Y0, Y1, 301, 400)          # also checks herd - wild = settle_tab gap (stops if not)
    g = gaps(d, Y0, Y1); h = herd(d, Y0, Y1)
    rows = [r for r in d["years"] if Y0 <= r["year"] + 1 <= Y1]
    cul, hd = sum(r.get("culledHerd") or 0 for r in rows), sum(r.get("herded") or 0 for r in rows)
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    Jh = jump_tab.jump(hs, lambda v: v >= 100, 400)
    rr = [r for r in jump_tab.r_series(d) if r[0] > 400]
    Jr = jump_tab.jump(rr, lambda v: v is not None and v <= -0.30, 300)
    return dict(gap=g, herd=h, split=sp[0] if sp else None, offtake=cul / hd if hd else None, Jh=Jh, Jr=Jr)

def ms(xs):
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else float("nan"))

def corr(x, y):
    n = len(x)
    if n < 3: return None
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return None if sx == 0 or sy == 0 else sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)

def arm_row(name, runs):
    gs = [r["gap"] for r in runs if r["gap"]]
    mean = {t: sum(g[t] for g in gs) / len(gs) for t in TRAITS} if gs else None
    est = sum(1 for r in runs if r["herd"] >= 100)
    hm = sum(r["herd"] for r in runs) / len(runs)
    off = [r["offtake"] for r in runs if r["offtake"] is not None]
    n = sum(1 for t in CORE if abs(mean[t]) >= 0.10) if mean else "-"
    c = corr([r["herd"] for r in runs if r["gap"]], [r["gap"]["R"] for r in runs if r["gap"]])
    return (f"| {name} | {len(runs)} | {est} | {hm:.1f} | " + (" | ".join(f"{mean[t]:+.3f}" for t in TRAITS) if mean else " | ".join("-" for _ in TRAITS))
            + f" | {n} | {(sum(off) / len(off)) if off else float('nan'):.3f} | " + (f"{c:+.2f}" if c is not None else "-") + " |")

def carried(dd, dh, dw):
    # dd = gap difference, dh / dw = herd-change / wild-change differences (dd = dh - dw). The component that accounts for
    # more than half of dd: herd if dh has dd's sign and abs(dh) > abs(dd)/2; wild if -dw has dd's sign and
    # abs(dw) > abs(dd)/2; both or neither -> "mixed" (amendment 2: no reading)
    h = dh * dd > 0 and abs(dh) > abs(dd) / 2; w = -dw * dd > 0 and abs(dw) > abs(dd) / 2
    return "herd" if h and not w else "wild" if w and not h else "mixed"

def main():
    a = sys.argv[1:]; alias = {}
    if "--alias" in a: i = a.index("--alias"); alias = dict(x.split("=") for x in a[i + 1].split(",")); del a[i:i + 2]
    E, B = files([a[0]]), files(a[1].split(";"))
    src = {**{k: B[v] for k, v in alias.items()}, **{k: E[k] for k in ARMS if k in E and k not in alias}}
    if alias: print(f"*** TEST ONLY: aliased arms {alias}; not exp007 results ***")
    S = {arm: {s: score_run(f) for s, f in sorted(src[arm].items())} for arm in ARMS if arm in src}
    for ref in ("REF", "NONE"): S[ref] = {s: score_run(f) for s, f in sorted(B[ref].items())}
    print(f"years {Y0}-{Y1}; seed means; est = seeds with herd >= 100; n = core traits with abs(seed-mean gap) >= 0.10;"
          " offtake = culled per year per herd goat; r(herd,R) = across-seed correlation of herd and R gap")
    print("| arm | seeds | est | herd | " + " | ".join(TRAITS) + " | n | offtake | r(herd,R) |\n|" + "---|" * (len(TRAITS) + 8))
    for arm in ["REF", "LOADLO", "LOADHI", "NONE", "NOCULL", "CTLDEEP", "CTLRAND", "CTLSHAL"]:
        if arm in S: print(arm_row(arm, list(S[arm].values())))
    print("\nHerd/wild split (founders 301-400), seed means (SE):")
    print("| arm | part | " + " | ".join(TRAITS) + " |\n|" + "---|" * (len(TRAITS) + 2))
    for arm in S:
        V = [r["split"] for r in S[arm].values() if r["split"]]
        for k, lab in ((0, "herd"), (1, "wild")):
            print(f"| {arm if k == 0 else ''} | {lab} | " + " | ".join("{:+.3f} ({:.3f})".format(*ms([v[t][k] for v in V])) for t in TRAITS) + " |")
    print("\nEstablishment year (herd: smoothed herd >= 100 held 400 y, follow-up to the last row - 400; R: R gap <= -0.30 held"
          " 300 y), per seed; '-' = not established in follow-up; 'late' = crosses after and holds to the end")
    for arm in S:
        f = lambda J: str(J[0]) if J[0] else (f"late {J[3]}" if J[3] else "-")
        print(f"{arm}: " + ", ".join(f"s{s} herd {f(r['Jh'])} / R {f(r['Jr'])}" for s, r in S[arm].items()))
    # per-seed table for the arms the predictions read
    print("\nPer seed (herd over the window; R and B gaps):")
    for arm in ["LOADLO", "LOADHI", "NOCULL", "CTLDEEP", "CTLRAND", "CTLSHAL"]:
        if arm in S: print(f"{arm}: " + "; ".join(f"s{s} {r['herd']:.0f} R {r['gap']['R']:+.2f} B {r['gap']['B']:+.2f}" if r["gap"] else f"s{s} {r['herd']:.0f} no herd" for s, r in S[arm].items()))
    print("\nCTL arms, established seeds only (herd >= 100), each seed's herd and gaps:")
    est = {arm: {s: r for s, r in S[arm].items() if r["herd"] >= 100 and r["gap"]} for arm in ["CTLDEEP", "CTLRAND", "CTLSHAL"] if arm in S}
    for arm, rs in est.items():
        print(f"{arm}: {len(rs)} established")
        for s, r in rs.items(): print(f"  s{s} herd {r['herd']:.0f}: " + " ".join(f"{t} {r['gap'][t]:+.3f}" for t in TRAITS))
    preds(S, est)

def preds(S, est):
    print("\nPredictions:")
    def established(arm): return [r for r in S[arm].values() if r["herd"] >= 100 and r["gap"]]
    if "LOADLO" in S:
        e = established("LOADLO"); m = sum(r["gap"]["R"] for r in e) / len(e) if e else None
        ok = len(e) >= 6 and m is not None and -0.30 <= m <= 0
        print(f"1. LOADLO established in >= 6 of 8 and seed-mean R gap of established seeds in [-0.30, 0]: {'met' if ok else 'not met'} "
              f"({len(e)} of {len(S['LOADLO'])}; R {m:+.3f})" if m is not None else f"1. not met ({len(e)} established)")
    if "LOADHI" in S:
        h30 = [r for r in S["LOADHI"].values() if r["herd"] >= 30 and r["gap"]]
        if len(h30) < 4: print(f"2. LOADHI: not scored, {len(h30)} seeds keep a herd of 30 or more (the result: a fixed high load stops herds growing)")
        else:
            gs = [r["gap"]["R"] for r in S["LOADHI"].values() if r["gap"]]; m = sum(gs) / len(gs)
            ok = m <= -0.50 and all(r["gap"]["R"] <= -0.30 for r in h30)
            print(f"2. LOADHI seed-mean R gap <= -0.50 and every seed with herd >= 30 at R <= -0.30: {'met' if ok else 'not met'} "
                  f"(R {m:+.3f}; herd>=30 seeds' R " + ", ".join(f"{r['gap']['R']:+.2f}" for r in h30) + ")")
            mid = [r for r in h30 if r["herd"] < 100]
            print(f"   decision branch: LOADHI seeds with herds of 30-100: " + (", ".join(f"herd {r['herd']:.0f} R {r['gap']['R']:+.2f}" for r in mid) or "none"))
    if "CTLDEEP" in S and "CTLRAND" in S:
        on_est = len(est.get("CTLDEEP", {})) >= 4 and len(est.get("CTLRAND", {})) >= 4
        Ds = est["CTLDEEP"] if on_est else {s: r for s, r in S["CTLDEEP"].items() if r["gap"]}
        Rs = est["CTLRAND"] if on_est else {s: r for s, r in S["CTLRAND"].items() if r["gap"]}
        D, Rr = list(Ds.values()), list(Rs.values()); shared = sorted(set(Ds) & set(Rs))
        print(f"3. CTLDEEP - CTLRAND, {'established seeds' if on_est else 'all seeds (fewer than 4 established in a CTL arm: not resolved on established herds)'}"
              f" ({len(D)} vs {len(Rr)}); counts if abs(diff) > 0.10 and > 2 SE; carried by herd / wild change (> half):")
        passes = []
        for t in TRAITS:
            (md, sd), (mr, sr) = ms([r["gap"][t] for r in D]), ms([r["gap"][t] for r in Rr])
            dd, se = md - mr, math.sqrt(sd ** 2 + sr ** 2)
            dh = ms([r["split"][t][0] for r in D])[0] - ms([r["split"][t][0] for r in Rr])[0]
            dw = ms([r["split"][t][1] for r in D])[0] - ms([r["split"][t][1] for r in Rr])[0]
            p = abs(dd) > 0.10 and abs(dd) > 2 * se
            if p and t in CORE: passes.append(t)
            # added after registration (steward, 2026-11-20; tools/pair_tab.py: the split's components are seed-correlated):
            # paired SE of the herd- and wild-change differences over the seeds both arms keep; descriptive, not in any rule
            # the paired difference and its SE both come from the shared seeds only (steward, 2026-11-20)
            pd = lambda k: ms([Ds[s]["split"][t][k] - Rs[s]["split"][t][k] for s in shared]) if len(shared) >= 2 else (float("nan"), float("nan"))
            (ph, phs), (pw, pws) = pd(0), pd(1)
            print(f"   {t}: {dd:+.3f} (SE {se:.3f}){' PASSES' if p else ''}; all kept seeds: herd change {dh:+.3f}, wild change {dw:+.3f} -> {carried(dd, dh, dw)}"
                  + ("  [noise reference]" if t == "C" else "")
                  + f"\n      paired over the {len(shared)} shared seeds (added after registration, descriptive): herd change {ph:+.3f} (SE {phs:.3f}), wild change {pw:+.3f} (SE {pws:.3f})")
        print(f"   prediction 3 (no core trait passes both bars): {'met' if not passes else 'not met (' + ' '.join(passes) + ')'}")
    for arm in ["CTLDEEP", "CTLRAND", "CTLSHAL"]:
        if arm in S:
            gs = [r["gap"] for r in S[arm].values() if r["gap"]]; mean = {t: sum(g[t] for g in gs) / len(gs) for t in CORE}
            n = [t for t in CORE if abs(mean[t]) >= 0.10]
            print(f"4. {arm} breadth n <= 2: {'met' if len(n) <= 2 else 'not met'} (n = {len(n)}: {' '.join(n)})")
    if "NOCULL" in S:
        e = len(established("NOCULL")); print(f"5. NOCULL established in >= 6 of 8: {'met' if e >= 6 else 'not met'} ({e} of {len(S['NOCULL'])}); NONE {len(established('NONE'))} of {len(S['NONE'])}")

if __name__ == "__main__": main()
