# audit_scoring.py: a cold audit of the exp005/exp006 scoring (runio.hist_rows, settle_tab.gaps, the settling rule,
# corner_tab's effects), written from the raw run records without reusing that code (analysis session, 2026-11-20).
# Each check prints PASS or FAIL; --bad KIND feeds it a deliberately wrong input, which must make it FAIL.
#   python tools/audit_scoring.py rows FILE [--bad shift]
#       Every gene-histogram row: histYears[i] == histPeriod*(i+1) - 1; the row's counts sum to the year row's goats
#       (hist) and herded (histHerd) for every trait; wild counts never negative; and runio.hist_rows picks exactly the
#       rows whose year lies in a window, for 1401-1600, 3201-4000 and the 200-year windows ending 1600..3200.
#       --bad shift: histYears moved one row on (row i labelled with row i+1's year).
#   python tools/audit_scoring.py gaps FILE Y0-Y1 [--bad swap]
#       Gap per trait over the window three ways: (1) by hand from hist/histHerd (wild = hist - histHerd, midpoints
#       (k+0.5)/20), (2) exact, from the year rows' traitMeans/herdTraitMeans/goats/herded at the same years
#       (wild mean = (goats*all - herded*herd)/(goats - herded)), (3) settle_tab.gaps. PASS: (3) equals (1) to 1e-9,
#       and (1) is within 0.01 of (2) (the bucket error). --bad swap: settle_tab.gaps gets a record whose histHerd B
#       column is H's.
#   python tools/audit_scoring.py corner Y0-Y1 DIR [DIR ...] [--bad onlyexp006]
#       Recomputes corner_tab's arm table and effects (add = arm+X - NONE, drop = REF - REF-without-X, exchange
#       addExchREF - REF; SE = sqrt(sd1^2/n1 + sd2^2/n2)) with the hand gaps, runs corner_tab.py on the same folders and
#       compares every printed cell. --bad onlyexp006: corner_tab is given only the last folder.
#   python tools/audit_scoring.py settle "DIR[;DIR]" [--bad strict]
#       The rule as settle_tab's header states it, recomputed with the hand gaps; compares each arm's long-run row,
#       worst-trait bias per E and settled-at with settle_tab.py's output. --bad strict: the audit side uses 0.04.
#   python tools/audit_scoring.py explog SECTION OUTFILE [--bad edit]
#       Every markdown table row (headers left out) in EXPLOG's section SECTION (exact heading text after "## ") whose
#       first two cells and width match a row of OUTFILE (a tool's saved output) must agree cell by cell. Only tables
#       the section prints from that file can match; prose is not checked. --bad edit: one EXPLOG number altered.
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORE = "R A S B H T M W L".split()
TRAITS = CORE + ["C"]
NB = 20

def load(f): return json.load(open(f, encoding="utf-8"))

def under_test():                                   # settle_tab's functions, the code being audited
    src = open(os.path.join(HERE, "settle_tab.py"), encoding="utf-8").read().replace("\nmain()\n", "\n")
    ns = {"__file__": os.path.join(HERE, "settle_tab.py")}; exec(src, ns); return ns

def year_rows(d): return {r["year"]: r for r in d["years"]}

def hand_rows(d, y0, y1):                           # y0..y1 1-based inclusive -> row indices, by histYears
    return [i for i, y in enumerate(d["histYears"]) if y0 <= y + 1 <= y1]

def mean_counts(c):
    n = sum(c); return None if n == 0 else sum((k + 0.5) / NB * v for k, v in enumerate(c)) / n

def hand_gap_rows(d, y0, y1):                       # per row: {trait: gap} or None (no herd or no wild goats)
    out = []
    for i in hand_rows(d, y0, y1):
        g = {}
        for t in TRAITS:
            h = d["histHerd"][t][i]; w = [a - b for a, b in zip(d["hist"][t][i], h)]
            mh, mw = mean_counts(h), mean_counts(w)
            g[t] = None if mh is None or mw is None else mh - mw
        out.append((d["histYears"][i], None if any(v is None for v in g.values()) else g))
    return out

def hand_gap(d, y0, y1):
    rows = [g for _, g in hand_gap_rows(d, y0, y1) if g]
    return None if not rows else {t: sum(r[t] for r in rows) / len(rows) for t in TRAITS}

def exact_gap(d, y0, y1):
    yr = year_rows(d); rows = []
    for y, g in hand_gap_rows(d, y0, y1):
        if not g: continue
        r = yr[y]; n, nh = r["goats"], r["herded"]
        rows.append({t: r["herdTraitMeans"][t] - (n * r["traitMeans"][t] - nh * r["herdTraitMeans"][t]) / (n - nh) for t in TRAITS})
    return None if not rows else {t: sum(r[t] for r in rows) / len(rows) for t in TRAITS}

def hand_herd(d, y0, y1):
    r = [x["herded"] for x in d["years"] if y0 <= x["year"] + 1 <= y1]
    return sum(r) / len(r) if r else 0.0

def verdict(ok, what): print(("PASS " if ok else "FAIL ") + what); return ok

# ---- rows
def cmd_rows(f, bad):
    d = load(f); P = d["_parameters"]; hp = P["histPeriod"]
    if bad == "shift": d["histYears"] = d["histYears"][1:] + [d["histYears"][-1] + hp]
    ys, yr = d["histYears"], year_rows(d)
    nrows = len(d["hist"]["R"])
    ok = verdict(len(ys) == nrows and all(len(d["hist"][t]) == nrows == len(d["histHerd"][t]) for t in TRAITS),
                 f"{nrows} rows in hist, histHerd and histYears")
    ok &= verdict(all(y == hp * (i + 1) - 1 for i, y in enumerate(ys)), f"histYears[i] == {hp}*(i+1)-1 (first {ys[:2]}, last {ys[-1]})")
    miss = [y for y in ys if y not in yr]
    ok &= verdict(not miss, f"every histogram year has a year row (recordEvery {P['recordEvery']}); missing {miss[:5]}")
    bad_n = [(y, t) for i, y in enumerate(ys) if y in yr for t in TRAITS
             if sum(d["hist"][t][i]) != yr[y]["goats"] or sum(d["histHerd"][t][i]) != yr[y]["herded"]]
    ok &= verdict(not bad_n, f"row counts equal the year row's goats and herded, all traits ({len(bad_n)} mismatches; first {bad_n[:3]})")
    neg = sum(1 for t in TRAITS for i in range(nrows) for a, b in zip(d["hist"][t][i], d["histHerd"][t][i]) if a < b)
    ok &= verdict(neg == 0, f"no negative wild bucket ({neg})")
    sys.path.insert(0, HERE); from runio import hist_rows
    wins = [(1401, 1600), (3201, 4000)] + [(e - 199, e) for e in (1600, 2000, 2400, 2800, 3200)]
    for y0, y1 in wins:
        mine, theirs = hand_rows(d, y0, y1), hist_rows(d, y0 - 1, y1 - 1)
        ok &= verdict(mine == theirs, f"hist_rows {y0}-{y1}: {len(theirs)} rows, years {d['histYears'][theirs[0]] + 1}..{d['histYears'][theirs[-1]] + 1} (1-based)")
    return ok

# ---- gaps
def cmd_gaps(f, win, bad):
    y0, y1 = (int(v) for v in win.split("-")); d = load(f); T = under_test()
    h, e = hand_gap(d, y0, y1), exact_gap(d, y0, y1)
    dt = d
    if bad == "swap":
        dt = json.loads(json.dumps(d)); dt["histHerd"]["B"] = dt["histHerd"]["H"]
    s = T["gaps"](dt, y0, y1)
    print(f"{os.path.basename(f)} {y0}-{y1}, {len(hand_rows(d, y0, y1))} rows")
    print("trait  hand      exact     settle_tab  hand-exact")
    for t in TRAITS: print(f"{t:5}  {h[t]:+.5f}  {e[t]:+.5f}  {s[t]:+.5f}    {h[t] - e[t]:+.5f}")
    ok = verdict(all(abs(s[t] - h[t]) < 1e-9 for t in TRAITS), "settle_tab.gaps equals the hand gap (1e-9)")
    ok &= verdict(all(abs(h[t] - e[t]) <= 0.01 for t in TRAITS), f"hand gap within 0.01 of the exact gap (max {max(abs(h[t] - e[t]) for t in TRAITS):.4f})")
    return ok

# ---- corner
FACTORS = [("cull", "addCull", "RAND"), ("pen", "addPen", "noPen"), ("guard", "addGuard", "noGuard"),
           ("prov", "addProv", "noProv"), ("shelter", "addShelter", "noShelter"), ("buck", "addBuck", "noBuck"),
           ("tether", "addTether", "noTether"), ("milk", "addMilk", "noMilk"), ("exch", "addExch", None)]

def runs_in(folders):
    R = {}
    for folder in folders:
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    return R

def md_rows(text):                                   # markdown table rows -> lists of stripped cells
    return [[c.strip() for c in l.strip().strip("|").split("|")] for l in text.splitlines()
            if l.strip().startswith("|") and not set(l.strip()) <= set("|-: ")]

def msd(xs):
    n = len(xs); m = sum(xs) / n
    return m, (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5

def cmd_corner(win, folders, bad):
    y0, y1 = (int(v) for v in win.split("-")); R = runs_in(folders); V = {}
    for a, ss in R.items():
        for s, f in ss.items():
            d = load(f); g = hand_gap(d, y0, y1)
            V.setdefault(a, {})[s] = dict(g or {t: 0.0 for t in TRAITS}, herd=hand_herd(d, y0, y1), nohist=g is None)
    nohist = sorted(f"{a}_s{s}" for a in V for s in V[a] if V[a][s]["nohist"])
    print(f"runs with no herd row in {y0}-{y1} (scored as gap 0 by corner_tab): {nohist or 'none'}")
    mine = {}
    for a, ss in V.items():
        m = {k: sum(v[k] for v in ss.values()) / len(ss) for k in TRAITS + ["herd"]}
        mine[a] = [a, str(len(ss)), str(sum(1 for v in ss.values() if v["R"] <= -0.30)), f"{m['herd']:.1f}"] + \
                  [f"{m[t]:+.3f}" for t in TRAITS] + [str(sum(1 for t in CORE if abs(m[t]) >= 0.10))]
    def eff(hi, lo, k):
        (a, sa), (b, sb) = msd([v[k] for v in V[hi].values()]), msd([v[k] for v in V[lo].values()])
        return a - b, (sa ** 2 / len(V[hi]) + sb ** 2 / len(V[lo])) ** 0.5
    for name, add, drop in FACTORS:
        rows = {}
        for lab, hi, lo in [("add", add, "NONE"), ("drop", "REF", drop) if drop else ("drop", "addExchREF", "REF")]:
            rows[lab] = {k: eff(hi, lo, k) for k in ["herd"] + CORE}
        for lab, r in rows.items():
            inter = " ".join(t for t in CORE if abs(rows["add"][t][0] - r[t][0]) > 0.10) if lab == "drop" else ""
            mine[(name, lab)] = [name, lab, f"{r['herd'][0]:+.1f}"] + [f"{r[t][0]:+.2f} ({r[t][1]:.2f})" for t in CORE] + [inter]
    tf = folders[-1:] if bad == "onlyexp006" else folders
    out = subprocess.run([sys.executable, os.path.join(HERE, "corner_tab.py"), win] + tf, capture_output=True, text=True).stdout
    theirs = {}
    for r in md_rows(out):
        if r[0] in ("arm", "behaviour"): continue
        theirs[(r[0], r[1]) if r[1] in ("add", "drop") else r[0]] = r
    diffs = [(k, mine[k], theirs.get(k)) for k in mine if theirs.get(k) != mine[k]]
    for k, a, b in diffs[:8]: print(f"  differs {k}:\n    audit      {a}\n    corner_tab {b}")
    return verdict(not diffs and len(theirs) == len(mine), f"corner_tab {win} on {len(tf)} folder(s): {len(mine)} rows recomputed, {len(diffs)} differ")

# ---- settle
def cmd_settle(folders, bad):
    thr = 0.04 if bad == "strict" else 0.05
    ends, L0, L1 = [1600, 2000, 2400, 2800, 3200], 3201, 4000
    R = runs_in(folders.split(";")); mine = {}
    for a in sorted(R):
        long, bias = [], {e: [] for e in ends}
        for s, f in sorted(R[a].items()):
            d = load(f); g = hand_gap(d, L0, L1)
            if g is None: continue
            long.append(g)
            for e in ends:
                w = hand_gap(d, e - 199, e)
                if w is not None: bias[e].append({t: w[t] - g[t] for t in CORE})
        oks, worst = [], []
        for e in ends:
            xs = bias[e]
            if len(xs) < 2: oks.append(False); worst.append(None); continue
            mb = {t: sum(x[t] for x in xs) / len(xs) for t in CORE}
            wt = max(CORE, key=lambda t: abs(mb[t])); worst.append(f"{abs(mb[wt]):.3f}"); oks.append(abs(mb[wt]) <= thr)
        settled = next((str(ends[i]) for i in range(len(ends)) if all(oks[i:])), "not settled")
        mine[a] = (worst, settled)
    out = subprocess.run([sys.executable, os.path.join(HERE, "settle_tab.py"), folders], capture_output=True, text=True).stdout
    theirs = {}
    for r in md_rows(out):
        if len(r) == len(ends) + 2 and r[0] != "arm":
            theirs[r[0]] = ([c.split()[0] if c != "n/a" else None for c in r[1:-1]], r[-1])
    diffs = [(a, mine[a], theirs.get(a)) for a in mine if theirs.get(a) != mine[a]]
    for a, x, y in diffs: print(f"  differs {a}: audit {x}, settle_tab {y}")
    for a in mine: print(f"  {a}: worst |bias| by E {mine[a][0]}, settled at {mine[a][1]}")
    return verdict(not diffs, f"settle rule (threshold {thr}) recomputed for {len(mine)} arms, {len(diffs)} differ from settle_tab")

# ---- explog
def cmd_explog(section, outfile, bad):
    text = open(os.path.join(HERE, "..", "EXPLOG.md"), encoding="utf-8").read()
    m = re.search(r"^## " + re.escape(section) + r"\n(.*?)(?=^## )", text, re.S | re.M)
    if not m: sys.exit("section not found")
    sec = m.group(1)
    if bad == "edit": sec = sec.replace("| -0.338 |", "| -0.339 |", 1)
    key = lambda r: tuple(r[:2]) + (len(r),)       # first two cells and the row's width (tables differ in columns)
    body = lambda rows: [r for r in rows if r[0] not in ("arm", "behaviour")]
    log = body(md_rows(sec)); out = {key(r): r for r in body(md_rows(open(outfile, encoding="utf-8").read()))}
    hits = [(r, out[key(r)]) for r in log if key(r) in out]
    diffs = [(a, b) for a, b in hits if a != b]
    for a, b in diffs[:8]: print(f"  differs:\n    EXPLOG {a}\n    tool   {b}")
    return verdict(hits and not diffs, f"{os.path.basename(outfile)}: {len(hits)} EXPLOG rows matched by their first two cells, {len(diffs)} differ")

def main():
    a = sys.argv[1:]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    ok = {"rows": lambda: cmd_rows(a[1], bad), "gaps": lambda: cmd_gaps(a[1], a[2], bad),
          "corner": lambda: cmd_corner(a[1], a[2:], bad), "settle": lambda: cmd_settle(a[1], bad),
          "explog": lambda: cmd_explog(a[1], a[2], bad)}[a[0]]()
    sys.exit(0 if ok else 1)

main()
