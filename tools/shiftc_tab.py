# shiftc_tab.py: the shifted-neutral-marker test of mutational pull (analysis session, 2026-11-20). The neutral marker C
# starts from alleles U[cInitLo, cInitHi] (e.g. 0.6-1.0) instead of around 0.5. Its herd change toward 0.5 in an arm
# with no trait selected on C is then pure mutational pull at that arm's depth and Ne, to compare against the selected
# traits' own pull. Prediction stated before any run by the reviewer (notes/review/2026-11-20-exp007-results.md, 405e315);
# the steward's pre-registration governs where it differs.
#   python tools/shiftc_tab.py Y0-Y1 "DIR[;DIR...]" [ARM,ARM...] [--neutral C] [--vs A,H,T,R,B] [--force]
# Per run (tools/split_tab.py, founders 301-400): F per trait and herd change over Y0-Y1; fraction = herd change /
# (0.5 - F), the run's own F. Per arm: seed mean of the fraction with a 95% t interval (n-1 df), and the ratio of
# seed means (mean herd change / (0.5 - mean F), the form of split_tab --show-founders). Within runs: paired differences
# fraction(neutral) - fraction(trait), mean (SE). Then the reading as amended before any result (EXPLOG exp009
# amendments a2f5c04 and d9c3fbe): 1 validity (the neutral's herd fraction, CTLRAND - CTLDEEP, within 2 paired SE, with
# its 95% interval); 2 the pooled pull (each CTLDEEP and CTLRAND run's herd and wild fractions averaged within the run,
# 95% t interval over runs) with the width bar (half-width <= 0.20); 3 per trait, the paired within-run difference
# fraction(neutral) - fraction(trait) with its 95% interval over CTLDEEP runs, and over REF runs; 4 the thresholds on the
# pooled estimate; 5 CTLDEEP's herd neutral alone, secondary.
# Refuses runs whose neutral trait is not shifted: a run without cInitLo > 0.5 in its parameters, or with any seed's
# founders' F within 0.10 of 0.5 (the test needs a pull to measure). --force skips the parameter check only (to test the
# machinery on old runs with another trait as --neutral). Exploratory until a pre-registration names it.
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import split_tab
T7 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447, 8: 2.365, 9: 2.306, 10: 2.262, 12: 2.201, 16: 2.131, 20: 2.093}
def tcrit(n): return T7.get(n, 2.0 if n > 20 else T7[max(k for k in T7 if k <= n)])

def ms(xs):
    n = len(xs); m = sum(xs) / n
    return m, ((sum((x - m) ** 2 for x in xs) / (n - 1) / n) ** 0.5 if n > 1 else float("nan"))

def main():
    a = sys.argv[1:]; opt = {"--neutral": "C", "--vs": "A,H,T,R,B"}; force = "--force" in a
    if force: a.remove("--force")
    for k in list(opt):
        if k in a: i = a.index(k); opt[k] = a[i + 1]; del a[i:i + 2]
    y0, y1 = (int(v) for v in a[0].split("-")); arms = a[2].split(",") if len(a) > 2 else ["CTLDEEP", "CTLRAND", "REF"]
    nt, vs = opt["--neutral"], opt["--vs"].split(","); traits = [nt] + vs
    R = {}
    for folder in a[1].split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and m.group(1) in arms:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    print(f"years {y0}-{y1}; neutral {nt} against {', '.join(vs)}; founders 301-400; fraction = herd change / (0.5 - F), per run. Exploratory.")
    res = {}
    for arm in arms:
        if arm not in R: continue
        for s, f in sorted(R[arm].items()):
            d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
            if not force and not (P.get("cInitLo") or 0) > 0.5:
                sys.exit(f"{os.path.basename(f)}: cInitLo is {P.get('cInitLo')}, not a shifted-{nt} run (use --force only to test the machinery)")
            r = split_tab.split(d, y0, y1, 301, 400)
            if r is None: print(f"{arm} s{s}: no herd in the window, left out"); continue
            out, F = r[0], r[1]
            if abs(0.5 - F[nt]) < 0.10: sys.exit(f"{os.path.basename(f)}: founders' {nt} = {F[nt]:.3f}, within 0.10 of 0.5: no pull to measure")
            ok = lambda t: abs(0.5 - F[t]) >= 0.05
            # per trait: herd change, founders' F, herd fraction, wild fraction (fractions None when F within 0.05 of 0.5)
            res.setdefault(arm, {})[s] = {t: (out[t][0], F[t], out[t][0] / (0.5 - F[t]) if ok(t) else None,
                                              out[t][1] / (0.5 - F[t]) if ok(t) else None) for t in traits}
    print("| arm | seeds | trait | founders' F | herd change | fraction, seed mean [95% t interval] | ratio of means |\n|---|---|---|---|---|---|---|")
    summ = {}
    for arm, ss in res.items():
        for t in traits:
            fr = [v[t][2] for v in ss.values() if v[t][2] is not None]
            Fm = sum(v[t][1] for v in ss.values()) / len(ss); hm = sum(v[t][0] for v in ss.values()) / len(ss)
            if len(fr) >= 2:
                m, se = ms(fr); h = tcrit(len(fr)) * se; summ[(arm, t)] = (m, m - h, m + h)
                cell = f"{m:+.2f} [{m - h:+.2f}, {m + h:+.2f}] (n {len(fr)})"
            else: cell = "n/a (F within 0.05 of 0.5)"
            print(f"| {arm} | {len(ss)} | {t} | {Fm:.3f} | {hm:+.3f} | {cell} | {hm / (0.5 - Fm):+.2f} |" if abs(0.5 - Fm) >= 0.05 else
                  f"| {arm} | {len(ss)} | {t} | {Fm:.3f} | {hm:+.3f} | {cell} | n/a |")
    print(f"\nWithin runs, fraction({nt}) - fraction(trait), mean (SE) over seeds:")
    for arm, ss in res.items():
        cells = []
        for t in vs:
            dd = [v[nt][2] - v[t][2] for v in ss.values() if v[nt][2] is not None and v[t][2] is not None]
            cells.append(f"{t} {ms(dd)[0]:+.2f} ({ms(dd)[1]:.2f})" if len(dd) >= 2 else f"{t} n/a")
        print(f"  {arm}: " + ", ".join(cells))
    amended(res, summ, nt, vs)

def amended(res, summ, nt, vs):
    # The reading as amended before any result: EXPLOG "exp009 amendment" (a2f5c04) and "exp009 amendment 2" (d9c3fbe).
    D, Rn = res.get("CTLDEEP", {}), res.get("CTLRAND", {})
    sh = sorted(s for s in set(D) & set(Rn) if D[s][nt][2] is not None and Rn[s][nt][2] is not None)
    print(f"\nAs amended (a2f5c04, d9c3fbe), neutral {nt}:")
    # 1. validity: the neutral's herd fraction, CTLRAND - CTLDEEP, paired over shared seeds, within 2 SE; its 95% interval
    # beside the verdict (amendment 2), so a pass that comes only from noise shows as a wide interval
    if len(sh) < 2: print("  1. validity: fewer than 2 shared seeds; not scored"); return
    dm, dse = ms([Rn[s][nt][2] - D[s][nt][2] for s in sh]); valid = abs(dm) <= 2 * dse; dh = tcrit(len(sh)) * dse
    print(f"  1. validity: herd {nt} fraction CTLRAND - CTLDEEP = {dm:+.3f} [{dm - dh:+.3f}, {dm + dh:+.3f}] (paired SE {dse:.3f}, "
          f"{len(sh)} seeds): " + ("within 2 SE, valid reference" if valid else f"beyond 2 SE: {nt} not a valid reference; the experiment does not resolve the question"))
    # 2. pooled pull (amendment 2): each CTLDEEP and CTLRAND run's herd and wild fractions averaged within the run, then the
    # mean and 95% t interval over the runs. Same-seed runs share their history to year 400 and the wild's course is
    # seed-set (tools/pair_tab.py: wild change r 0.5-0.8 across arms), so the runs are not fully independent and this
    # interval may be somewhat narrow; that is the registered form.
    u = [(v[nt][2] + v[nt][3]) / 2 for arm in (D, Rn) for v in arm.values() if v[nt][2] is not None]
    pm, pse = ms(u); h = tcrit(len(u)) * pse; lo, hi = pm - h, pm + h
    print(f"  2. pooled {nt} fraction (per run: mean of herd and wild; interval over {len(u)} CTLDEEP + CTLRAND runs): "
          f"{pm:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    wide = h > 0.20
    print(f"     width test: pooled {nt} 95% half-width {h:.3f} " + ("> 0.20: FAILS, reading is unresolved" if wide else "<= 0.20: passes"))
    # 3. per trait (amendment 2): the paired within-run difference fraction(neutral) - fraction(trait), herd fractions, with
    # its 95% interval over CTLDEEP runs (REF runs for REF): spanning 0 = inside; entirely above 0 = the trait moved less
    # than the neutral (pull partly opposed by herd selection); entirely below 0 = moved more (selection beyond the pull)
    place = {}
    for an in ("CTLDEEP", "REF"):
        A_ = res.get(an, {})
        for t in vs:
            dd = [v[nt][2] - v[t][2] for v in A_.values() if v[nt][2] is not None and v[t][2] is not None]
            if len(dd) < 2: continue
            m, se = ms(dd); w = tcrit(len(dd)) * se
            p = "inside: the pull accounts for it" if m - w <= 0 <= m + w else ("moved less than " + nt + ": pull partly opposed by herd selection" if m - w > 0 else "moved more than " + nt + ": selection beyond the pull")
            place[(an, t)] = p.split(":")[0]
            print(f"  3. {an} {t}: fraction({nt}) - fraction({t}) = {m:+.3f} [{m - w:+.3f}, {m + w:+.3f}] ({len(dd)} runs): {p}")
    # 4. thresholds on the pooled estimate; "inside" for A, H, T is the paired reading of step 3 (amendment 2 replaces
    # the point-estimate reading)
    aht = {t: summ[("CTLDEEP", t)][0] for t in ("A", "H", "T") if ("CTLDEEP", t) in summ and t != nt}
    inside = [t for t in aht if place.get(("CTLDEEP", t)) == "inside"]
    def reading(pm, wide):
        if not valid: return "not resolved", f"not resolved ({nt} not a valid reference)"
        if 0.3 <= pm <= 0.6 and len(inside) == len(aht) == 3: k, v = "mutational", "mutational: pooled in 0.3-0.6 with A, H and T inside (paired differences span 0)"
        elif pm < 0.15: k, v = "selection", "selection: pooled below 0.15" + ("" if all(0.4 <= x <= 0.5 for x in aht.values()) else " (but A, H, T are not all near 0.4-0.5)")
        elif pm < 0.3: k, v = "unresolved", "unresolved: pooled between 0.15 and 0.3"
        else: k, v = "neither", f"neither stated case: pooled {pm:+.3f}, A/H/T inside (paired): {' '.join(inside) or 'none'}"
        return ("unresolved", f"unresolved (pooled interval wider than +-0.20); without the width bar: {v}") if wide else (k, v)
    k1, verdict = reading(pm, wide)
    print(f"  4. reading: {verdict}")
    # sensitivity (steward, 2026-11-20, before any outcome): each seed's CTLDEEP and CTLRAND runs averaged first (each run
    # already the mean of its herd and wild fractions), then the interval over seeds, the seed as the independent unit and
    # so the conservative width. If the reading differs from step 4's, the reading is reported as fragile.
    us = [((D[s][nt][2] + D[s][nt][3]) / 2 + (Rn[s][nt][2] + Rn[s][nt][3]) / 2) / 2 for s in sh]
    sm, sse = ms(us); shw = tcrit(len(us)) * sse; k2, v2 = reading(sm, shw > 0.20)
    print(f"  sensitivity: pooled {nt} by seed (each seed's two runs averaged; interval over {len(us)} seeds): {sm:+.3f} "
          f"[{sm - shw:+.3f}, {sm + shw:+.3f}], half-width {shw:.3f}; reading: {v2}")
    print("  sensitivity verdict: " + ("same reading as step 4" if k1 == k2 else f"READING CHANGES ({k1} -> {k2}): the reading is fragile"))
    # 5. secondary: CTLDEEP's herd neutral alone
    if ("CTLDEEP", nt) in summ:
        m, a_, b_ = summ[("CTLDEEP", nt)]
        print(f"  5. secondary: CTLDEEP herd {nt} alone {m:+.3f} [{a_:+.3f}, {b_:+.3f}], half-width {(b_ - a_) / 2:.3f}")

def selftest():
    # Planted synthetic fractions (no run files), to show the sensitivity verdict can fire. 16 seeds; each seed's CTLDEEP
    # and CTLRAND runs identical (so the validity check passes), the neutral's herd and wild fractions = 0.45 + e (e
    # alternating +-spread), A/H/T = the neutral's minus +-0.05 (paired differences span 0: inside). Spread 0.45: by-run
    # half-width about 0.16 (passes the bar: mutational), by-seed about 0.25 (fails it: unresolved) -> READING CHANGES.
    # Spread 0.05: both pass -> same reading.
    import io, contextlib
    def case(spread):
        res, summ = {"CTLDEEP": {}, "CTLRAND": {}, "REF": {}}, {}
        for s in range(1, 17):
            e = spread if s % 2 else -spread; d = 0.05 if (s // 2) % 2 else -0.05; c = 0.45 + e
            row = {"C": (0, 0.8, c, c), **{t: (0, 0.2, c - d, c - d) for t in ("A", "H", "T", "R", "B")}}
            for arm in res: res[arm][s] = row
        for t in ("A", "H", "T"): summ[("CTLDEEP", t)] = (0.45, 0.3, 0.6)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): amended(res, summ, "C", ["A", "H", "T", "R", "B"])
        return buf.getvalue()
    ok = True
    for spread, want in ((0.45, "READING CHANGES"), (0.05, "same reading as step 4")):
        out = case(spread); got = want in out
        ok &= got; print(f"{'PASS' if got else 'FAIL'} spread {spread}: expects '{want}'")
        print("  " + "\n  ".join(l.strip() for l in out.splitlines() if "reading" in l or "pooled" in l))
    return ok

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest": sys.exit(0 if selftest() else 1)
    main()
