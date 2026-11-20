# jump_tab.py: when is a herd established? Time to event, by herd size (analysis session, 2026-11-20; revised the same
# day to use herd size, not the R gap, after the design review, notes/review/2026-11-20-design.md finding 1: the R gap
# is written by the spook rule, whose hazard scales with herd size, so it cannot define establishment).
#   python tools/jump_tab.py dist "DIR[;DIR...]" [ARM,ARM...] [--smooth 100]
#       Pooled over the named arms (default all): the count of points (year rows after year 400 + smooth) by smoothed herd
#       size (20-goat bins). The threshold below is set from the empty band this shows.
#   python tools/jump_tab.py selftest [HOLD]
#       Planted series (a jump, a short excursion, a fall-back, a late crossing, none); a HOLD under 200 must FAIL.
#   python tools/jump_tab.py "DIR[;DIR...]" [ARM,ARM...] [--thr 100] [--hold 400] [--smooth 100] [--marker herd|r]
#       Per run: the jump year, herd before and after, fall-backs; per arm: Kaplan-Meier fraction established by year t,
#       runs not established by the end of follow-up censored there, with a 95% interval (Greenwood, log-log).
# Marker herd (default): smoothed herd H(y) = mean of the year rows' "herded" over the `smooth` years ending at y (1-based).
# Established at J = the first year row after 400 + smooth with H >= thr there and at every year row in the next `hold`
# years. Only a point with `hold` years of record after it can confirm a jump, so every run is followed to its last year
# row - hold; a crossing after that which holds to the end is listed as "late" and not counted. A fall-back is a later
# stretch of `hold` years with H < thr. Marker r (cross-check only): the R gap per histogram row, established when
# <= thr (pass --thr -0.30), as the first version of this tool.
import glob, json, math, os, re, sys

def mean_counts(c):
    n = sum(c); return None if n == 0 else sum((k + 0.5) / 20 * v for k, v in enumerate(c)) / n

def herd_series(d, smooth):                          # [(year 1-based, smoothed herd)] from the year rows
    ys = [(r["year"] + 1, r.get("herded") or 0) for r in d["years"]]; out, j, s = [], 0, 0.0
    for i, (y, h) in enumerate(ys):
        s += h
        while ys[j][0] <= y - smooth: s -= ys[j][1]; j += 1
        out.append((y, s / (i - j + 1), h))
    return out

def r_series(d):                                     # [(year 1-based, R gap or None, herd)] per histogram row
    yr = {r["year"]: r for r in d["years"]}; out = []
    for i, y in enumerate(d["histYears"]):
        h = d["histHerd"]["R"][i]; w = [a - b for a, b in zip(d["hist"]["R"][i], h)]
        mh, mw = mean_counts(h), mean_counts(w)
        out.append((y + 1, None if mh is None or mw is None else mh - mw, yr[y]["herded"] if y in yr else None))
    return out

def runs(folders, arms):
    R = {}
    for folder in folders:
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and (not arms or m.group(1) in arms):
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    return R

def jump(rs, on, hold):
    # rs: [(year, value, ...)]; on(value) -> the established state. Returns (J or None, follow-up end, fall-backs, late)
    last = rs[-1][0]; end = last - hold
    def held(i, test):
        y = rs[i][0]; return all(test(r[1]) for r in rs[i:] if r[0] <= y + hold)
    J = next((rs[i][0] for i in range(len(rs)) if rs[i][0] <= end and on(rs[i][1]) and held(i, on)), None)
    falls = 0
    if J:
        k = next(i for i in range(len(rs)) if rs[i][0] == J)
        while k < len(rs):
            if rs[k][0] <= end and not on(rs[k][1]) and held(k, lambda v: not on(v)):
                falls += 1; k = next((j for j in range(k, len(rs)) if on(rs[j][1])), len(rs))
            else: k += 1
    late = None
    if J is None:
        late = next((rs[i][0] for i in range(len(rs)) if rs[i][0] > end and all(on(r[1]) for r in rs[i:])), None)
    return J, end, falls, late

def km(res, t):
    # res: [(J or None, end)]. Kaplan-Meier fraction established by t, and its 95% interval (Greenwood, log-log on S)
    S, v = 1.0, 0.0
    for tj in sorted({J for J, _ in res if J and J <= t}):
        d = sum(1 for J, _ in res if J == tj)
        n = sum(1 for J, end in res if (J is not None and J >= tj) or (J is None and end >= tj))
        S *= 1 - d / n; v += d / (n * (n - d)) if n > d else float("inf")
    if S in (0.0, 1.0) or v == float("inf"): return 1 - S, None
    c = 1.96 * math.sqrt(v) / abs(math.log(S))
    lo, hi = S ** math.exp(c), S ** math.exp(-c)       # interval on S; the fraction established is 1 - S
    return 1 - S, (1 - hi, 1 - lo)

def dist(folders, arms, smooth):
    hb, n = {}, 0
    for a, ss in sorted(runs(folders, arms).items()):
        for s, f in ss.items():
            for y, H, _ in herd_series(json.load(open(f, encoding="utf-8")), smooth):
                if y <= 400 + smooth: continue
                n += 1; hb[int(H // 20)] = hb.get(int(H // 20), 0) + 1
    print(f"{n} year rows after year {400 + smooth}; herd = mean of year rows' herded over the {smooth} years ending there; arms {arms or 'all'}")
    print("herd bin   points")
    for k in range(0, max(hb) + 1): print(f"{k * 20:3d}-{k * 20 + 19:3d}  {hb.get(k, 0):6d}")

def main(a):
    opt = {"--thr": None, "--hold": 400, "--smooth": 100, "--marker": "herd"}
    for k in list(opt):
        if k in a: i = a.index(k); opt[k] = a[i + 1]; del a[i:i + 2]
    marker, hold, smooth = opt["--marker"], int(opt["--hold"]), int(opt["--smooth"])
    thr = float(opt["--thr"]) if opt["--thr"] is not None else (100.0 if marker == "herd" else -0.30)
    folders, arms = a[0].split(";"), (a[1].split(",") if len(a) > 1 else None)
    R = runs(folders, arms)
    if marker == "herd":
        on = lambda v: v >= thr; desc = f"smoothed herd ({smooth}-year mean of year rows' herded) >= {thr:g}"
    else:
        on = lambda v: v is not None and v <= thr; desc = f"R gap per histogram row <= {thr:g} (cross-check only)"
    ts = list(range(800, 4001, 400))
    print(f"established = the first point after year {400 + smooth if marker == 'herd' else 400} with {desc},")
    print(f"held at every point for the next {hold} years. A run is followed to its last point - {hold}; not established by")
    print("then = censored there. late = crosses after that and holds to the end (not counted).")
    print("Kaplan-Meier fraction established by year t [95% interval, Greenwood log-log; none where the estimate is 0 or 1]")
    print("| arm | runs | established | " + " | ".join(str(t) for t in ts) + " | median | late | fall-backs |\n|" + "---|" * (len(ts) + 6))
    detail = []
    for arm in sorted(R):
        res = []
        for s, f in sorted(R[arm].items()):
            d = json.load(open(f, encoding="utf-8"))
            if marker == "herd": rs = [r for r in herd_series(d, smooth) if r[0] > 400 + smooth]
            else: rs = [r for r in r_series(d) if r[0] > 400]
            J, end, falls, late = jump(rs, on, hold); res.append((J, end, falls, late))
            hs = herd_series(d, smooth)
            hb = lambda lo, hi: [h for y, _, h in hs if lo < y <= hi]
            m = lambda v: f"{sum(v) / len(v):.0f}" if v else "-"
            hh = f", herd {m(hb(J - 400, J - 100))} in J-400..J-100, {m(hb(J + 100, J + 400))} in J+100..J+400" if J else ""
            detail.append(f"{arm} s{s}: established {J or '-'}, follow-up to {end}, fall-backs {falls}" + (f", late crossing {late}" if late else "") + hh)
        rr = [(J, end) for J, end, _, _ in res]; endmax = max(e for _, e in rr)
        cells = []
        for t in ts:
            if t > endmax: cells.append("-"); continue
            p, ci = km(rr, t); cells.append(f"{p:.2f}" + (f" [{ci[0]:.2f}-{ci[1]:.2f}]" if ci else ""))
        js = sorted(J for J, _ in rr if J); med = next((J for J in js if km(rr, J)[0] >= 0.5), None)
        print(f"| {arm} | {len(res)} | {len(js)} | " + " | ".join(cells) + f" | {med or '-'} | {sum(1 for r in res if r[3])} | {sum(r[2] for r in res)} |")
    print("\nPer run:"); print("\n".join(detail))

def selftest(hold):
    # planted smoothed-herd series on a 3-year grid from 503 to 3998: expected (J, fall-backs, late) at thr 100, hold 400
    ys = list(range(503, 3999, 3)); ser = lambda f: [(y, f(y), 0) for y in ys]
    lo, hi = 30, 250
    cases = {"jump at 1505": (ser(lambda y: hi if y >= 1505 else lo), (1505, 0, None)),
             "excursion of 200 y at 1001, jump at 2000": (ser(lambda y: hi if 1001 <= y < 1201 or y >= 2000 else lo), (2000, 0, None)),
             "jump at 800, back at 2000": (ser(lambda y: hi if 800 <= y < 2000 else lo), (800, 1, None)),
             "late crossing at 3800": (ser(lambda y: hi if y >= 3800 else lo), (None, 0, 3800)),
             "never": (ser(lambda y: lo), (None, 0, None))}
    ok = True
    for name, (rs, want) in cases.items():
        J, end, falls, late = jump(rs, lambda v: v >= 100, hold); got = (J, falls, late)
        ok &= got == want; print(f"{'PASS' if got == want else 'FAIL'} {name}: got {got}, want {want}")
    return ok

if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "selftest": sys.exit(0 if selftest(int(a[1]) if len(a) > 1 else 400) else 1)
    if a[0] == "dist":
        sm = int(a[a.index("--smooth") + 1]) if "--smooth" in a else 100
        dist(a[1].split(";"), a[2].split(",") if len(a) > 2 and not a[2].startswith("--") else None, sm); sys.exit()
    main(a)
