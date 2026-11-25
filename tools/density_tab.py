# density_tab.py: goats per cell, wild and herd, by state, and exp018's predictions 1-4 (analysis session, 2026-11-24;
# EXPLOG "exp018" 281eae4 as amended by "exp018 amendment" 20db6e8 and "exp018 clarification" 513c1bc, which govern;
# Chris: "how many goats are there per grid cell in wild vs herds in both established and non-established herds?").
#   python tools/density_tab.py "DIR[;DIR...]" ARM,ARM... [--late W0-W1] [--perseed] [--bad swap|nopool|nohold]
# Year rows (src/world.js sampleDensity, src/datamanager.js) carry density = {c, cells}: c = four classes [wild, with
# herder (walksWithHerder), kept at camp (sheltered, tethered or guarded), other herd (kids following a mother, loose
# run-offs, captives being led, herd goats whose camp has no herder that day)], each {n, own, all, own9, all9} or null:
# n = goat-samples (each living goat once a day at the middle day sub-tick); own = mean goats of its own kind in its
# cell, itself included (wild goats for the wild class, herd goats of any class otherwise); all = mean goats of either
# kind in its cell; own9, all9 = the same over its 3x3 neighbourhood (clipped at the map edge). cells = occupied
# cell-samples [wild, herd]. own - 1 is "other goats nearby". Midday only: dawn and night crowding are not measured.
# The 1x1 and 3x3 windows are the counter's; the rule's radius is not chosen (the sim senses company over socialRange 4).
# Pooling over a state's rows, per class: own, all, own9, all9 weighted by n (exact). perCell for wild = sum of wild n /
# sum of cells[0]; for the herd as a whole = sum of the three herd classes' n / sum of cells[1]; never per herd class.
# per day = sum n / (rows x yearDays): the class's mean head count on a sample day, over all the state's rows.
# States, per run (year labels = index + 1):
#   baseline  indices 300-399 (labels 301-400; herding begins at index 400), printed once per seed (the arms are checked
#             to agree there, so it is read from the first arm given);
#   late      W0-W1 (3201-4000 unless --late), all seeds;
#   est       late, in herding seeds whose mean of herded over the late rows is >= 100 (load_tab's rule as exp017 scored);
#   small     rows after label 500 and before the seed's J (load_tab's J as it computes it: jump_tab.herd_series(d, 100)
#             after 500, jump_tab.jump at >= 100 with a 400-year hold; to the end if no J), whose own herded is < 60.
#   Floor: est and small are read only with 10 or more rows holding a with-herder sample; otherwise "not read".
# Predictions (as amended):
#   1. with-herder own > wild own and with-herder own9 > wild own9, in every seed-state (est, small) that meets the floor;
#      the kept class's share of herd goat-samples beside (a mechanism check, true nearly by construction).
#   2. SPR05: with-herder own over est > over small, in every established seed; with-herder goats per sample day beside.
#   3. In each of REF, SPR05, SPR10, the arm mean of wild own over late lies inside HUNT's per-seed min-max; wild all,
#      own9, all9, the wild population (wild n / yearDays) and wildNearCamp beside.
#   4. HUNT's wild R = the all-goat R from hist over late (the tool stops if any HUNT row's histHerd is non-empty); REF's
#      = the wild-only R (hist - histHerd; split_tab.split's F + wild change, as tools/wildr_tab.py). Holds if at least 6 of
#      HUNT's 8 per-seed values lie above REF's median per-seed value and the arm means differ by more than 0.04 (HUNT
#      above); a difference of 0.04 or less either way is "not read". huntTries (301-400, late) and the wild population
#      beside.
# Checks (the tool stops on any): every row has density {c, cells}; every non-null entry obeys 1 <= own <= all <= all9,
# own <= own9 <= all9 (3 places); cells[k] > 0 exactly when its class(es) have samples; per row, pooled own >= perCell
# for wild and for the herd (a goat-weighted mean of cell counts is at least the cell-weighted one); no herd sample and
# cells[1] = 0 in a run with herdingAt >= 1e8 and in every row before the run's herdingAt; the arms given agree on every
# shared key of every year row before index 400, per seed (as tools/cmp_years.py, restricted to those rows).
# --bad swap reads the wild and with-herder classes swapped (with-herder samples before herding) and must stop;
# --bad nopool pools perCell as the n-weighted mean of per-row ratios, and a two-row case must stop; --bad nohold
# computes J with no hold (the first year at >= 100) and its self-check against the 400-year J on a planted series must
# stop.
import glob, json, os, re, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import split_tab, jump_tab

KEYS = ["own", "all", "own9", "all9"]
CLS = ["wild", "with herder", "kept", "other herd"]
EPS = 0.0015   # the record's 3 places

def jJ(d, bad=None):
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    return jump_tab.jump(hs, lambda v: v >= 100, 0 if bad == "nohold" else 400)[0] if hs else None   # no row after 500: no J

def selfcheck(bad):
    # perCell: row 1 has 10 wild goats in 10 cells, row 2 has 90 in 10; pooled 100 / 20 = 5.000 (n-weighted ratio: 8.200)
    rows = [{"density": {"c": [{"n": 10, "own": 1, "all": 1, "own9": 1, "all9": 1}, None, None, None], "cells": [10, 0]}},
            {"density": {"c": [{"n": 90, "own": 9, "all": 9, "own9": 9, "all9": 9}, None, None, None], "cells": [10, 0]}}]
    p = pool(rows, 360, bad)["perCell"][0]
    if abs(p - 5.0) > 1e-9: sys.exit(f"check failed: pooled perCell {p:.3f} on the two-row case, exact 5.000")
    # J: herded 0 to label 600, 150 for 100 years (labels 601-700), 0 to 1200, then 150 to 2000; the held J is past 1200
    d = {"years": [{"year": y, "herded": 150 if 600 <= y < 700 or y >= 1200 else 0} for y in range(0, 2000, 3)]}
    J = jJ(d, bad)
    if not (J and J > 1200): sys.exit(f"check failed: J {J} on the planted series, expected after 1200")

def pool(rows, yd, bad=None):
    c = [[r["density"]["c"][k] for r in rows if r["density"]["c"][k]] for k in range(4)]
    out = {"rows": len(rows), "N": [sum(e["n"] for e in es) for es in c]}
    out["m"] = [{k: sum(e["n"] * e[k] for e in es) / sum(e["n"] for e in es) for k in KEYS} if es else None for es in c]
    out["perDay"] = [n / (len(rows) * yd) for n in out["N"]]
    cw, ch = sum(r["density"]["cells"][0] for r in rows), sum(r["density"]["cells"][1] for r in rows)
    nh = sum(out["N"][1:])
    if bad == "nopool":
        rw = [(r["density"]["c"][0]["n"], r["density"]["c"][0]["n"] / r["density"]["cells"][0]) for r in rows if r["density"]["c"][0]]
        out["perCell"] = [sum(n * x for n, x in rw) / sum(n for n, _ in rw) if rw else None, nh / ch if ch else None]
    else: out["perCell"] = [out["N"][0] / cw if cw else None, nh / ch if ch else None]
    out["kept"] = out["N"][2] / nh if nh else None
    out["w1rows"] = sum(1 for r in rows if r["density"]["c"][1])
    hc = [sum(r["herdComp"]) for r in rows if r.get("herdComp")]   # head per managed camp-day (datamanager's herdComp), per row
    out["head"] = sum(hc) / len(hc) if hc else None
    return out

def check_row(r, where, herding, ha):
    D = r.get("density")
    if not D or "c" not in D or "cells" not in D or len(D["c"]) != 4: sys.exit(f"{where}: no density {{c, cells}} (code before 20db6e8)")
    for k, e in enumerate(D["c"]):
        if e and not (e["n"] > 0 and 1 - EPS <= e["own"] <= e["all"] + EPS and e["all"] <= e["all9"] + EPS and e["own"] <= e["own9"] + EPS and e["own9"] <= e["all9"] + EPS):
            sys.exit(f"check failed: {where} {CLS[k]}: entry breaks 1 <= own <= all <= all9, own <= own9 <= all9: {e}")
    nw = D["c"][0]["n"] if D["c"][0] else 0; nh = sum(e["n"] for e in D["c"][1:] if e)
    if (nw > 0) != (D["cells"][0] > 0) or (nh > 0) != (D["cells"][1] > 0): sys.exit(f"check failed: {where}: cells {D['cells']} against samples wild {nw}, herd {nh}")
    if nw and D["c"][0]["own"] < nw / D["cells"][0] - EPS * 2: sys.exit(f"check failed: {where}: wild own {D['c'][0]['own']} below perCell {nw / D['cells'][0]:.3f}")
    if nh:
        ho = sum(e["n"] * e["own"] for e in D["c"][1:] if e) / nh
        if ho < nh / D["cells"][1] - EPS * 2: sys.exit(f"check failed: {where}: herd own {ho:.3f} below perCell {nh / D['cells'][1]:.3f}")
    if nh and (not herding or r["year"] < ha): sys.exit(f"check failed: {where}: herd samples ({nh}) with herdingAt {ha}")

def main():
    a = sys.argv[1:]; bad = None; per = "--perseed" in a; late = (3201, 4000)
    if per: a.remove("--perseed")
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if "--late" in a: i = a.index("--late"); late = tuple(int(v) for v in a[i + 1].split("-")); del a[i:i + 2]
    selfcheck(bad)
    dirs, arms = a[0], a[1].split(",")
    R = {}
    for folder in dirs.split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and m.group(1) in arms:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    V, INFO, PRE, RR, EMPTY = {}, {}, {}, {}, {}   # V[arm][state][seed] = pool; INFO[arm][seed]; PRE[seed][arm] = rows before 400
    # EMPTY[arm] = herding seeds whose small state has no row at all (2026-11-24, exp018 scoring: such a seed had been
    # dropped without a word; it is below the floor, so it is named and counted as not read)
    for arm in arms:
        for s, f in sorted(R.get(arm, {}).items()):
            d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
            ha = P.get("herdingAt"); herding = ha is not None and ha < 1e8; yd = P.get("yearDays")
            for r in d["years"]:
                if bad == "swap" and r.get("density") and "c" in r["density"]: r["density"]["c"][0], r["density"]["c"][1] = r["density"]["c"][1], r["density"]["c"][0]
                check_row(r, f"{arm} s{s} year {r['year'] + 1}", herding, ha)
            PRE.setdefault(s, {})[arm] = [r for r in d["years"] if r["year"] < 400]
            lab = lambda y0, y1: [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
            hl = split_tab.herd(d, *late); J = jJ(d, bad) if herding else None
            st = {"baseline": lab(301, 400), "late": lab(*late)}
            if herding:
                st["est"] = st["late"] if hl >= 100 else []
                st["small"] = [r for r in d["years"] if r["year"] + 1 > 500 and (J is None or r["year"] + 1 < J) and (r.get("herded") or 0) < 60]
            mean = lambda k, rows: (lambda xs: sum(xs) / len(xs) if xs else None)([r[k] for r in rows if r.get(k) is not None])
            INFO.setdefault(arm, {})[s] = {"ha": ha, "hl": hl, "J": J, "yd": yd, "hunt": (mean("huntTries", st["baseline"]), mean("huntTries", st["late"])),
                                           "near": mean("wildNearCamp", st["late"])}
            if herding and not st["small"]: EMPTY.setdefault(arm, []).append(s)
            for k, rows in st.items():
                if rows: V.setdefault(arm, {}).setdefault(k, {})[s] = pool(rows, yd, bad)
            if arm == "HUNT" or not herding:   # prediction 4: all-goat R, every goat wild
                ix = [i for i, y in enumerate(d["histYears"]) if late[0] <= y + 1 <= late[1]]
                if any(sum(d["histHerd"]["R"][i]) for i in range(len(d["histYears"]))): sys.exit(f"{arm} s{s}: histHerd non-empty in a no-herding run")
                if ix: RR.setdefault(arm, {})[s] = sum(split_tab.mc(d["hist"]["R"][i]) for i in ix) / len(ix)
            elif arm == "REF":   # prediction 4 reads REF only
                sp = split_tab.split(d, late[0], late[1], 301, 400)
                if sp: RR.setdefault(arm, {})[s] = sp[1]["R"] + sp[0]["R"][1]
    # the arms agree before index 400, per seed, on every shared key of every year row (cmp_years's comparison)
    for s, A in sorted(PRE.items()):
        names = [x for x in arms if x in A]
        for x in names[1:]:
            ra, rb = A[names[0]], A[x]
            if len(ra) != len(rb): sys.exit(f"check failed: s{s}: {names[0]} has {len(ra)} rows before 400, {x} {len(rb)}")
            for p, q in zip(ra, rb):
                dk = [k for k in set(p) & set(q) if p[k] != q[k]]
                if dk: sys.exit(f"check failed: s{s}: {names[0]} and {x} differ at year {p['year'] + 1} before herding on {sorted(dk)[:5]}")
    print(f"exp018: arms {', '.join(x for x in arms if x in R)} agree on every shared key of every year row before index 400, per seed"
          f" ({sum(len(A) - 1 for A in PRE.values())} arm pairs).")
    f3 = lambda x: "-" if x is None else f"{x:.3f}"
    f1 = lambda x: "-" if x is None else f"{x:.1f}"
    cell = lambda xs, f=f3: (lambda xs: f"{f(sum(xs) / len(xs))} ({f(min(xs))}-{f(max(xs))})" if xs else "-")([x for x in xs if x is not None])
    floor = lambda v: v["w1rows"] >= 10
    print(f"Goats per cell at midday, by class and state (descriptive). late = {late[0]}-{late[1]}; est = late in seeds with"
          " mean herded >= 100 over it; small = rows after 500, before J, with herded < 60; est and small read only with 10 or"
          " more rows holding a with-herder sample. Per cell: mean over seeds (min-max over seeds) of each seed's pooled value."
          " own - 1 = other goats nearby. Midday only; 1x1 and 3x3 windows (3x3 clipped at the map edge).")
    def table(title, src):
        print(f"\n{title}\n| state | class | seeds | rows/seed | per day | own | all | own9 | all9 | perCell |\n|---|---|---|---|---|---|---|---|---|---|")
        for k, ss in src:
            for c in range(4):
                xs = {s: v for s, v in ss.items() if v["m"][c]}
                if not xs: continue
                pc = [v["perCell"][0] for v in xs.values()] if c == 0 else [v["perCell"][1] for v in xs.values()] if c == 1 else []
                print(f"| {k} | {CLS[c]} | {len(xs)} of {len(ss)} | {sum(v['rows'] for v in xs.values()) / len(xs):.1f} | {cell([v['perDay'][c] for v in xs.values()], f1)} | "
                      + " | ".join(cell([v["m"][c][m] for v in xs.values()]) for m in KEYS) + f" | {cell(pc) + (' (herd, all classes)' if c == 1 else '') if pc else ''} |")
    first = next(x for x in arms if x in V)
    table(f"Baseline, indices 300-399 (labels 301-400), every goat wild; one run per seed, read from {first}", [("baseline", V[first].get("baseline", {}))])
    for arm in arms:
        if arm not in V: continue
        I = INFO[arm]
        print(f"\n{arm}: herdingAt {sorted({v['ha'] for v in I.values()})}; per seed mean herded over late / J: "
              + ", ".join(f"s{s} {v['hl']:.1f} / {v['J'] or '-'}" for s, v in sorted(I.items())))
        nr = {k: sorted(s for s, v in V[arm].get(k, {}).items() if not floor(v)) for k in ("est", "small")}
        src = [("late", V[arm].get("late", {}))] + [(k, {s: v for s, v in V[arm].get(k, {}).items() if floor(v)}) for k in ("est", "small") if k in V[arm]]
        table(f"{arm}" + "".join(f"; {k} not read (under 10 with-herder rows): {['s%d' % s for s in nr[k]]}" for k in nr if nr[k])
              + (f"; small not read (no row after 500 before J with herded < 60): {['s%d' % s for s in EMPTY[arm]]}" if EMPTY.get(arm) else ""), src)
        if any(k in V[arm] for k in ("est", "small")):
            print("  kept share of herd goat-samples: " + "; ".join(f"{k} {cell([v['kept'] for v in V[arm][k].values() if floor(v)])}" for k in ("est", "small") if k in V[arm]))
    if per:
        print("\nPer seed: state: class own all own9 all9 (per day); perCell wild / herd; kept share; rows (with-herder rows)")
        for arm in arms:
            for k in ("late", "est", "small"):
                for s, v in sorted(V.get(arm, {}).get(k, {}).items()):
                    print(f"  {arm} s{s} {k}: " + "; ".join(f"{CLS[c]} " + " ".join(f3(v['m'][c][m]) for m in KEYS) + f" ({f1(v['perDay'][c])})" for c in range(4) if v["m"][c])
                          + f"; perCell {f3(v['perCell'][0])} / {f3(v['perCell'][1])}; kept {f3(v['kept'])}; rows {v['rows']} ({v['w1rows']})" + ("" if k == "late" or floor(v) else " NOT READ"))
    print("\nPredictions (exp018 as amended, 20db6e8 and 513c1bc)")
    p1, nr1 = [], []
    for arm in arms:
        nr1 += [f"{arm} small s{s} (no row)" for s in EMPTY.get(arm, [])]
        for k in ("est", "small"):
            for s, v in sorted(V.get(arm, {}).get(k, {}).items()):
                if not floor(v): nr1.append(f"{arm} {k} s{s}"); continue
                if v["m"][0] and v["m"][1]: p1.append((f"{arm} {k} s{s}", v["m"][1]["own"] > v["m"][0]["own"] and v["m"][1]["own9"] > v["m"][0]["own9"], v))
    fl = [f"{n} (with herder own {f3(v['m'][1]['own'])}, wild {f3(v['m'][0]['own'])}; own9 {f3(v['m'][1]['own9'])}, {f3(v['m'][0]['own9'])})" for n, ok, v in p1 if not ok]
    print(f"1. with-herder own > wild own and own9 > wild own9, every seed-state at the floor (est, small): {len(p1) - len(fl)} of {len(p1)}"
          + (f"; fails: {'; '.join(fl)}" if fl else "") + (f"; not read (floor): {len(nr1)} ({', '.join(nr1)})" if nr1 else "")
          + (": holds" if p1 and not fl else ": fails" if fl else ": not testable") + " (a mechanism check)")
    if "SPR05" in V:
        E = {s: v for s, v in V["SPR05"].get("est", {}).items() if floor(v)}; S = {s: v for s, v in V["SPR05"].get("small", {}).items() if floor(v)}
        both = [(s, E[s], S[s]) for s in sorted(E) if s in S]; no = [s for s in sorted(E) if s not in S]
        ok = [x for x in both if x[1]["m"][1]["own"] > x[2]["m"][1]["own"]]
        print(f"2. SPR05, with-herder own est > small in every established seed: {len(ok)} of {len(both)} ("
              + ", ".join(f"s{s} {f3(e['m'][1]['own'])} (per day {f1(e['perDay'][1])}) vs {f3(m['m'][1]['own'])} (per day {f1(m['perDay'][1])})" for s, e, m in both) + ")"
              + (f"; established seeds with the small state not read: {['s%d' % s for s in no]}" if no else "")
              + (": holds" if both and len(ok) == len(both) and not no else ": fails" if len(ok) < len(both) else ": not testable on every established seed"))
    else: print("2. SPR05 not read")
    H = V.get("HUNT", {}).get("late", {})
    if H:
        hw = [v["m"][0]["own"] for v in H.values()]; lo, hi = min(hw), max(hw); res = []
        side = lambda arm, vs: (f"{arm}: wild own {f3(sum(v['m'][0]['own'] for v in vs) / len(vs))}; all {f3(sum(v['m'][0]['all'] for v in vs) / len(vs))}, own9 "
                                f"{f3(sum(v['m'][0]['own9'] for v in vs) / len(vs))}, all9 {f3(sum(v['m'][0]['all9'] for v in vs) / len(vs))}, wild population "
                                f"{f1(sum(v['perDay'][0] for v in vs) / len(vs))}, wildNearCamp {cell([INFO[arm][s]['near'] for s in V[arm]['late']], f1)}")
        print(f"3. late wild own, each arm mean inside HUNT's per-seed range {f3(lo)}-{f3(hi)}:\n   " + side("HUNT", list(H.values())))
        for arm in ("REF", "SPR05", "SPR10"):
            vs = list(V.get(arm, {}).get("late", {}).values())
            if not vs: res.append(None); print(f"   {arm} not read"); continue
            m = sum(v["m"][0]["own"] for v in vs) / len(vs); res.append(lo <= m <= hi)
            print(f"   {side(arm, vs)}: {'inside' if lo <= m <= hi else 'outside'}")
        print("   " + ("holds" if all(res) else "fails" if any(x is False for x in res) else "not every arm read"))
    else: print("3. HUNT's late state not read")
    if "HUNT" in RR and "REF" in RR:
        h, r = RR["HUNT"], RR["REF"]; med = statistics.median(r.values()); k = sum(1 for x in h.values() if x > med)
        dm = sum(h.values()) / len(h) - sum(r.values()) / len(r)
        verdict = "not read (arm means within 0.04)" if abs(dm) <= 0.04 else ("holds" if k >= 6 and dm > 0.04 else "fails")
        print(f"4. wild R over late: HUNT (all-goat R) per seed " + ", ".join(f"s{s} {f3(x)}" for s, x in sorted(h.items()))
              + f"; REF (wild-only R) per seed " + ", ".join(f"s{s} {f3(x)}" for s, x in sorted(r.items()))
              + f"; REF's median {f3(med)}; HUNT above it in {k} of {len(h)}; arm means {f3(sum(h.values()) / len(h))} vs {f3(sum(r.values()) / len(r))} ({dm:+.3f}): {verdict}")
        for arm in ("HUNT", "REF"):
            I = INFO[arm]
            print(f"   {arm}: huntTries 301-400 {cell([v['hunt'][0] for v in I.values()], f1)}, late {cell([v['hunt'][1] for v in I.values()], f1)}; wild population late "
                  f"{cell([v['perDay'][0] for v in V[arm]['late'].values()], f1)}")
    else: print("4. HUNT or REF not read")
    # Derived lines (2026-11-24, the reviewer's b2dabf0 point 4: numbers headed for Chris are printed here, not computed by
    # hand). Per arm, state and class (at the floor for est and small): own - 1 (others of its kind in its cell) and
    # own9 - own (others of its kind in the 8 cells around), each the mean over seeds (min-max) of the seed's pooled
    # values; the widest own9 - own of the with-herder class, with its seed; the herd's head per managed camp-day
    # (herdComp summed: kids, does, bucks, other; mean over the state's rows that have one, unweighted), the per-herd head
    # count the reviewer's point 2 asks for. Then wild own over every arm, state and seed; each arm's late wild population
    # and huntTries beside HUNT's (difference, and ratio for huntTries).
    print(chr(10) + "Derived (printed for the record; descriptive)")
    allw = []
    for arm in arms:
        for k in ("baseline", "late", "est", "small"):
            ss = {s: v for s, v in V.get(arm, {}).get(k, {}).items() if k in ("baseline", "late") or floor(v)}
            if not ss or (k == "baseline" and arm != first): continue
            allw += [v["m"][0]["own"] for v in ss.values() if v["m"][0]]
            parts = []
            for c in range(4):
                xs = [v for v in ss.values() if v["m"][c]]
                if not xs: continue
                parts.append(f"{CLS[c]} own-1 {cell([v['m'][c]['own'] - 1 for v in xs])}, own9-own {cell([v['m'][c]['own9'] - v['m'][c]['own'] for v in xs])}")
            w = [(v["m"][1]["own9"] - v["m"][1]["own"], s) for s, v in ss.items() if v["m"][1]]
            if w: parts.append(f"widest with-herder own9-own {max(w)[0]:.3f} (s{max(w)[1]})")
            hd = [v["head"] for v in ss.values() if v.get("head") is not None]
            if hd: parts.append(f"head per managed camp-day {cell(hd, f1)}")
            print(f"  {arm} {k}: " + "; ".join(parts))
    if allw: print(f"  wild own over every arm, state and seed printed above: {min(allw):.3f}-{max(allw):.3f}")
    if "SPR05" in V:
        E = {s: v for s, v in V["SPR05"].get("est", {}).items() if floor(v)}; S = {s: v for s, v in V["SPR05"].get("small", {}).items() if floor(v)}
        print("  SPR05 head per managed camp-day, est vs small: " + ", ".join(f"s{s} {f1(E[s]['head'])} vs {f1(S[s]['head'])}" for s in sorted(E) if s in S))
    if H:
        hp = sum(v["perDay"][0] for v in H.values()) / len(H); ht = [INFO["HUNT"][s]["hunt"][1] for s in H if INFO["HUNT"][s]["hunt"][1] is not None]
        for arm in ("REF", "SPR05", "SPR10"):
            vs = V.get(arm, {}).get("late", {})
            if not vs: continue
            ap = sum(v["perDay"][0] for v in vs.values()) / len(vs); at = [INFO[arm][s]["hunt"][1] for s in vs if INFO[arm][s]["hunt"][1] is not None]
            tr = f"; late huntTries {f1(sum(at) / len(at))} against HUNT's {f1(sum(ht) / len(ht))} ({sum(at) / len(at) - sum(ht) / len(ht):+.1f}, ratio {sum(at) / len(at) / (sum(ht) / len(ht)):.3f})" if at and ht else ""
            print(f"  {arm}: late wild population {f1(ap)} against HUNT's {f1(hp)} ({ap - hp:+.1f}){tr}")

if __name__ == "__main__": main()
