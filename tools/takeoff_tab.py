# takeoff_tab.py: what triggers a herd's take-off? (EXPLOG "Take-off analysis", 72bcc06; exploratory, decides nothing in
# the design). Analysis session, 2026-11-22.
#   python tools/takeoff_tab.py "DIR[;DIR...]" ARM[,ARM...] [--waited] [--plateau20] [--minplateau N] [--out FILE.json] [--bad nodir|nostay]
# --minplateau N (Take-off analysis on REF, 3bb3e2a): a run whose plateau before J-300 is under N years is plotted (its
#   trajectory goes to --out) but gets no departure test, and is listed.
#   python tools/takeoff_tab.py selftest [bad]
# Each run is aligned on its own jump year J (tools/jump_tab.py: the first year after 500 whose 100-year trailing mean
# herd is >= 100 and stays so for 400 years). --waited keeps only runs load_tab's Q1 rule classes "waited" (exp010
# amendment 071fd3e: the 100-year herd mean under 60 for 300+ consecutive years after 500, then established);
# --plateau20 keeps runs whose 100-year herd mean stayed between 20 and 99 for 300+ consecutive years before J.
# Variables per year row (keys present in every exp005 and exp010 run):
#   size = herded; R = herdTraitMeans.R (the herd's mean R); does = herded x herdComp[1] / sum(herdComp) (does of breeding
#   age: home-born does are not recorded by sex); csire = herd conceptions by a captured sire (concOrigin column 1) /
#   herd conceptions; loss = escaped / herded.
# Smoothing: each variable as a trailing 30-year window ending at each row (ratios as summed numerators / summed
#   denominators; R weighted by herded); None where the window has no herd (or no conception, for csire).
# Departure, per variable and run: plateau = smoothed points in J-600..J-301 (from year 500 at the earliest, flagged
#   when shorter than 300 years); direction = the sign of the J..J+300 mean minus the plateau mean; "beyond" = deviation
#   from the plateau mean in that direction above 2 plateau SD (above 0 if the SD is 0, flagged); the departure year =
#   the first smoothed point from J-300 on such that every point from it through J+300 is beyond (a None point is not
#   beyond); none if no such point.
# "First": a variable among R, size and does whose departure is strictly earlier than both others'; a tie is no one's.
# Reading (stated before any data was read): R first in 5 or more of the 7 LOAD1 seeds: feedback; does or size first in
#   5 or more: demographic; otherwise mixed. Run against other folders, the counts print without the 7-seed verdict.
# --out writes the aligned smoothed trajectories (J-600..J+300) for tools/takeoff_plot.py. --bad nostay takes the first
#   point beyond, without staying (the selftest's planted dip must then fail); --bad nodir drops the direction.
import glob, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import jump_tab
VARS = ["size", "R", "does", "csire", "loss"]
TRIO = ["R", "size", "does"]
WIN, PRE, PLAT, POST, K = 30, 300, 600, 300, 2.0

def ms(xs):
    xs = [x for x in xs if x is not None]
    if not xs: return None, None
    n = len(xs); m = sum(xs) / n
    return m, (math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else 0.0)

def rows(d):
    out = []
    for r in d["years"]:
        h = r.get("herded") or 0; hc = r.get("herdComp"); co = r.get("concOrigin"); tm = r.get("herdTraitMeans")
        does = h * hc[1] / sum(hc) if hc and sum(hc) else (0.0 if h == 0 else None)
        cnum = (co[0][1] + co[1][1]) if co else 0; cden = sum(map(sum, co)) if co else 0
        out.append({"y": r["year"] + 1, "h": h, "R": tm["R"] if tm and h else None, "does": does,
                    "cn": cnum, "cd": cden, "esc": r.get("escaped") or 0})
    return out

def smooth(rs):
    out = []
    for i, r in enumerate(rs):
        w = [x for x in rs[:i + 1] if x["y"] > r["y"] - WIN]
        H = sum(x["h"] for x in w); n = len(w)
        Rw = [(x["R"], x["h"]) for x in w if x["R"] is not None and x["h"]]
        dz = [x["does"] for x in w if x["does"] is not None]
        cd = sum(x["cd"] for x in w)
        out.append({"y": r["y"], "size": H / n,
                    "R": sum(a * b for a, b in Rw) / sum(b for _, b in Rw) if Rw else None,
                    "does": sum(dz) / len(dz) if dz else None,
                    "csire": sum(x["cn"] for x in w) / cd if cd else None,
                    "loss": sum(x["esc"] for x in w) / H if H else None})
    return out

FRAC = 0.25   # the matched-scale reading's fraction of a variable's own change (the reviewer's a5a0b06; fixed before reading)

def noise(sm, var, J, start=500):
    """Plateau SD / abs(post mean - plateau mean): how far, in units of its own change, a variable's plateau noise reaches."""
    p0 = max(J - PLAT, start); m, sd = ms([p[var] for p in sm if p0 <= p["y"] <= J - PRE - 1 and p[var] is not None])
    post = ms([p[var] for p in sm if J <= p["y"] <= J + POST])[0]
    return None if m is None or post is None or post == m else sd / abs(post - m)

def departure(sm, var, J, start=500, bad=None, frac=None):
    """(departure year or None, flags) for one smoothed variable around jump year J. With frac (exploratory, matched
    scale), "beyond" is having covered at least frac of the variable's own change (post mean - plateau mean)."""
    flags = []
    p0 = max(J - PLAT, start); plat = [p[var] for p in sm if p0 <= p["y"] <= J - PRE - 1 and p[var] is not None]
    if J - PRE - p0 < PLAT - PRE: flags.append(f"plateau {J - PRE - p0} y")
    if len(plat) < 3: return None, flags + ["no plateau"]
    m, sd = ms(plat)
    post = ms([p[var] for p in sm if J <= p["y"] <= J + POST])[0]
    if post is None: return None, flags + ["no post-jump values"]
    sgn = 1 if post >= m else -1
    if sd == 0: flags.append("plateau SD 0")
    beyond = (lambda v: v is not None and abs(v - m) > K * sd) if bad == "nodir" else \
             (lambda v: v is not None and (v - m) * sgn > (K * sd if sd > 0 else 0))
    if frac is not None:
        need = frac * abs(post - m) if bad != "fracsd" else K * sd   # bad fracsd: falls back to the 2-SD bar
        beyond = lambda v: v is not None and (v - m) * sgn >= need
    win = [p for p in sm if J - PRE <= p["y"] <= J + POST]
    for i, p in enumerate(win):
        if (beyond(p[var]) if bad == "nostay" else all(beyond(q[var]) for q in win[i:])):
            # the clarification (the steward): a departure at the search start (J-300) may have begun earlier
            return p["y"], flags + (["at the search start, possibly earlier"] if i == 0 else [])
    return None, flags

def plateau_len(J, start=500):
    """Years of plateau before the search start: J-300 minus the plateau's first year (J-600, or 500 if later)."""
    return J - PRE - max(J - PLAT, start)

def lead(dep):
    """R's departure minus the earlier of size's and does's, in years (negative = R first); None if R or both never depart."""
    o = [dep[v] for v in ("size", "does") if dep.get(v) is not None]
    return None if dep.get("R") is None or not o else dep["R"] - min(o)

def first(dep):
    """The one of R, size, does that departs strictly before both others; None on a tie or if none departs."""
    have = {v: dep[v] for v in TRIO if dep.get(v) is not None}
    for v, y in have.items():
        if all(y < dep[o] if dep.get(o) is not None else True for o in TRIO if o != v): return v
    return None

def analyse(d, start=500, bad=None):
    sm = smooth(rows(d)); hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > start]
    J = jump_tab.jump(hs, lambda v: v >= 100, 400)[0]
    if J is None: return None
    dep, fl, dq = {}, {}, {}
    for v in VARS: dep[v], fl[v] = departure(sm, v, J, start, bad); dq[v] = departure(sm, v, J, start, bad, FRAC)[0]
    return {"J": J, "dep": dep, "flags": fl, "first": first(dep), "lead": lead(dep),
            "depq": dq, "firstq": first(dq), "leadq": lead(dq), "noise": {v: noise(sm, v, J, start) for v in VARS},
            "traj": [{**p, "t": p["y"] - J} for p in sm if J - PLAT <= p["y"] <= J + POST]}

def plateau20(d):
    hs = [(y, H) for y, H, _ in jump_tab.herd_series(d, 100) if y > 500]
    J = jump_tab.jump([(y, H, 0) for y, H in hs], lambda v: v >= 100, 400)[0]
    if J is None: return None
    run = best = 0; prev = None
    for y, H in hs:
        if y >= J: break
        if 20 <= H < 100: run = run + (y - prev) if prev is not None and 20 <= prevH < 100 else 0; best = max(best, run)
        else: run = 0
        prev, prevH = y, H
    return best >= 300

def reading(res, n_expected=7):
    c = {v: sum(1 for r in res if r["first"] == v) for v in TRIO}
    demo = c["does"] + c["size"]
    if len(res) != n_expected: return c, f"counts only ({len(res)} runs, the stated reading is for {n_expected})"
    return c, ("feedback" if c["R"] >= 5 else "demographic" if demo >= 5 else "mixed")

def main():
    a = sys.argv[1:]; out = None; bad = None
    waited, p20 = "--waited" in a, "--plateau20" in a
    a = [x for x in a if x not in ("--waited", "--plateau20")]
    if "--out" in a: i = a.index("--out"); out = a[i + 1]; del a[i:i + 2]
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    minplat = None
    if "--minplateau" in a: i = a.index("--minplateau"); minplat = int(a[i + 1]); del a[i:i + 2]
    arms = a[1].split(",")
    F = jump_tab.runs(a[0].split(";"), arms)
    res, skipped = [], []
    import load_tab
    for arm in sorted(F):
        for s, f in sorted(F[arm].items()):
            if waited:
                q1 = load_tab.score(f, 3201, 4000, None, True)["q1"]
                if q1 != "waited": skipped.append(f"{arm} s{s} ({q1})"); continue
            d = json.load(open(f, encoding="utf-8"))
            if p20 and not (p := plateau20(d)): skipped.append(f"{arm} s{s} (" + ("never established" if p is None else "no 20-99 plateau of 300 y") + ")"); continue
            r = analyse(d, bad=bad)
            if r is None: skipped.append(f"{arm} s{s} (never established)"); continue
            r["run"] = f"{arm} s{s}"
            if minplat is not None and plateau_len(r["J"]) < minplat:   # REF (3bb3e2a): plotted, not tested
                r["notest"] = plateau_len(r["J"]); r["first"] = r["firstq"] = r["lead"] = r["leadq"] = None
                r["dep"] = {v: None for v in VARS}; r["depq"] = {v: None for v in VARS}
            res.append(r)
    allres = res; res = [r for r in allres if "notest" not in r]
    print(f"Take-off (EXPLOG 72bcc06; exploratory): runs aligned on the jump year J; smoothed over {WIN} y; departure = first"
          f" point from J-{PRE} on staying beyond {K:g} plateau SD (plateau J-{PLAT}..J-{PRE + 1}) through J+{POST}, in the"
          " direction the variable moves across the jump. Years are relative to J.")
    if skipped: print("left out: " + "; ".join(skipped))
    nt = [r for r in allres if "notest" in r]
    if nt: print(f"plotted, departure test not run (plateau before J-{PRE} under {minplat} y, counted from year 500): "
                 + "; ".join(f"{r['run']} J {r['J']} ({max(0, r['notest'])} y)" for r in nt))
    print("| run | J | " + " | ".join(VARS) + " | first of R / size / does | R lead (y; negative = R first) | flags |\n|---|---|"
          + "---|" * len(VARS) + "---|---|---|")
    for r in res:
        fl = "; ".join(f"{v}: {', '.join(x)}" for v, x in r["flags"].items() if x)
        ld = "-" if r["lead"] is None else f"{r['lead']:+d}"
        print(f"| {r['run']} | {r['J']} | " + " | ".join("-" if r["dep"][v] is None else f"{r['dep'][v] - r['J']:+d}" for v in VARS)
              + f" | {r['first'] or 'none (tie or no departure)'} | {ld} | {fl or '-'} |")
    c, verdict = reading(res)
    print(f"\nFirst to depart: R {c['R']}, size {c['size']}, does {c['does']}, none {len(res) - sum(c.values())} of {len(res)}")
    print(f"Reading (stated before the data): {verdict}")
    print("Caution: J is set by the 100-year trailing mean of herd size, so raw herd size must rise before J; size departing"
          " first is partly built into the alignment.")
    # exploratory (the reviewer's a5a0b06), beside the stated reading, not replacing it
    print(f"\nEXPLORATORY, matched scale (the reviewer's a5a0b06; not the stated reading): noise ratio = plateau SD /"
          f" abs(post-jump mean - plateau mean), per variable; departure = the first point from J-{PRE} from which the variable"
          f" has covered {FRAC:g} of its own change and stays there through J+{POST}")
    print("| run | noise " + " | noise ".join(VARS) + " | " + " | ".join(f"{v} at {FRAC:g}" for v in VARS)
          + " | first | R lead |\n|---|" + "---|" * (2 * len(VARS) + 2))
    f2 = lambda x: "-" if x is None else f"{x:.2f}"
    for r in res:
        ld = "-" if r["leadq"] is None else f"{r['leadq']:+d}"
        print(f"| {r['run']} | " + " | ".join(f2(r["noise"][v]) for v in VARS) + " | "
              + " | ".join("-" if r["depq"][v] is None else f"{r['depq'][v] - r['J']:+d}" for v in VARS)
              + f" | {r['firstq'] or 'none'} | {ld} |")
    cq = {v: sum(1 for r in res if r["firstq"] == v) for v in TRIO}
    print(f"Matched scale, first to depart: R {cq['R']}, size {cq['size']}, does {cq['does']}, none {len(res) - sum(cq.values())} of {len(res)}")
    print("Caution (the reviewer's a5a0b06): as home-born goats replace captives, herd R falls with growth on composition"
          " alone, so a tie or an R lag is what the demographic hypothesis predicts; only R well ahead points to feedback.")
    if out:
        json.dump([{"run": r["run"], "J": r["J"], "dep": r["dep"], "traj": r["traj"]} for r in allres], open(out, "w"), indent=0)
        print(f"trajectories written to {out}")

def planted(J0, r_at, does_at, size_at, Y=4000):
    """Year rows every 3 years. Herd ~8 (+-1) until size_at, then rising to 250 over 150 years; R 0.80 (+-0.005) until
    r_at, then 0.70; does 2 (+-0.2) until does_at, then 6; no conceptions or escapes. J0 is unused by the generator; the
    tool finds J itself."""
    rs = []
    for y in range(2, Y, 3):
        Y1 = y + 1; wob = math.sin(Y1 * 0.7)
        h = 8 + wob if Y1 < size_at else min(250, 8 + (Y1 - size_at) * 242 / 150)
        R = 0.80 + 0.005 * wob if Y1 < r_at else 0.70
        dz = 2 + 0.2 * wob if Y1 < does_at else 6
        if Y1 >= size_at: dz = max(dz, h * 0.3)
        rs.append({"year": y, "herded": h, "herdTraitMeans": {"R": R}, "herdComp": [0, dz, h - dz, 0] if h else None,
                   "concOrigin": [[0, 0, 0, 0], [0, 0, 0, 0]], "escaped": 0})
    return {"years": rs}

def selftest(bad=False):
    ok = True
    def check(name, got, want):
        nonlocal ok; res = got == want; ok &= res
        print(f"{'ok  ' if res else 'FAIL'} {name}" + ("" if res else f": got {got}, want {want}"))
    # size rises from 2000 (J near 2130, so the plateau is about 1530-1829 and the search starts near 1830).
    # feedback: R falls at 1850, before size; does follow size
    r = analyse(planted(0, r_at=1850, does_at=2600, size_at=2000))
    check("feedback: R departs first", (r["first"], r["dep"]["R"] is not None and r["dep"]["R"] < r["dep"]["size"]), ("R", True))
    # demographic: does rise at 1880, before size; R falls after the post-jump window
    r = analyse(planted(0, r_at=2600, does_at=1880, size_at=2000))
    check("demographic: does depart first", r["first"], "does")
    # direction: R moves down across the jump, but first rises to 0.85 (1850-2099) and then falls to 0.70. The upward
    # excursion is not its departure; with --bad nodir it would count from 1850
    d = planted(0, r_at=99999, does_at=2600, size_at=2000)
    for x in d["years"]:
        if 1850 <= x["year"] + 1: x["herdTraitMeans"]["R"] = 0.85 if x["year"] + 1 < 2100 else 0.70
    r = analyse(d)
    check("direction: an upward excursion before a fall is not R's departure", r["dep"]["R"] is not None and r["dep"]["R"] >= 2100, True)
    # "stays": a temporary dip of R (1850-1909) that returns to the plateau is not the departure; the real fall comes at
    # 2200. With --bad nostay (first point beyond, no staying) the dip would count
    d = planted(0, r_at=2200, does_at=2600, size_at=2000)
    for x in d["years"]:
        if 1850 <= x["year"] + 1 < 1910: x["herdTraitMeans"]["R"] = 0.70
    r = analyse(d, bad="nostay" if bad else None)
    check("stays: a temporary dip is not R's departure", r["dep"]["R"] is not None and r["dep"]["R"] >= 2200, True)
    # tie: R and does depart on the same smoothed point -> no one first
    check("tie is no one's", first({"R": 1900, "does": 1900, "size": 1950}), None)
    check("first ignores a variable that never departs", first({"R": 1900, "does": None, "size": 1950}), "R")
    # plateau shortened before year 500, flagged
    sm = [{"y": y, "v": 1.0 + 0.01 * math.sin(y)} for y in range(400, 2000, 3)]
    for p in sm:
        if p["y"] >= 900: p["v"] = 2.0
    dep, fl = departure(sm, "v", 1000)
    check("plateau before year 500 is shortened and flagged", (dep, fl), (901, ["plateau 200 y"]))
    check("plateau length before the search start", (plateau_len(700), plateau_len(1000), plateau_len(2000)), (-100, 200, 300))
    # the clarification: R's signed lead, and a departure at the search start flagged as possibly earlier
    check("R lead: R minus the earlier of size and does", (lead({"R": 1850, "size": 2003, "does": 2010}),
          lead({"R": 2100, "size": None, "does": 1900}), lead({"R": None, "size": 2000, "does": 2000})), (-153, 200, None))
    sm = [{"y": y, "v": 1.0 + 0.01 * math.sin(y)} for y in range(400, 2000, 3)]
    for p in sm:
        if p["y"] >= 700: p["v"] = 2.0
    check("a departure at the search start is flagged", departure(sm, "v", 1000), (700, ["plateau 200 y", "at the search start, possibly earlier"]))
    c, v = reading([{"first": "R"}] * 5 + [{"first": "size"}] * 2); c2, v2 = reading([{"first": "does"}] * 3 + [{"first": "size"}] * 2 + [{"first": "R"}] * 2)
    c3, v3 = reading([{"first": "R"}] * 4 + [{"first": "size"}] * 3)
    check("reading: feedback, demographic, mixed", (v, v2, v3), ("feedback", "demographic", "demographic" if bad else "mixed"))
    # matched scale (a5a0b06): a quiet and a noisy variable ramp from 1 to 2 over the same years (700-900). The 2-SD rule
    # dates the noisy one later; the matched-scale departure dates them the same. With --bad fracsd (matched scale using
    # the 2-SD bar) they differ again
    sm = []
    for y in range(400, 2000, 3):
        ramp = 1.0 if y < 700 else min(2.0, 1.0 + (y - 700) / 200)
        sm.append({"y": y, "a": ramp + (0.01 * math.sin(y) if y < 700 else 0), "b": ramp + (0.2 * math.sin(y) if y < 700 else 0)})
    d2a, d2b = departure(sm, "a", 1000, 400)[0], departure(sm, "b", 1000, 400)[0]
    qa, qb = (departure(sm, x, 1000, 400, "fracsd" if bad else None, FRAC)[0] for x in ("a", "b"))
    check("matched scale removes the noise lag that the 2-SD rule has", (d2a < d2b, qa == qb, round(noise(sm, "b", 1000, 400), 2) > round(noise(sm, "a", 1000, 400), 2)), (True, True, True))
    print("selftest " + ("passes" if ok else "FAILS")); return ok

if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]: sys.exit(0 if selftest(sys.argv[2:3] == ["bad"]) else 1)
    main()
