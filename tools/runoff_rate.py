# runoff_rate.py: observed run-off, fetch-back and loss rates per herd goat per year, per run (exp014's calibration of
# spookFixed to REF's run-off rate; steward, 2026-11-22). The same estimator as tools/load_tab.py's observable rates:
# events summed over the window's recorded year rows / herd goats (herded) summed over the same rows.
#   python tools/runoff_rate.py Y0-Y1 FILE.json [FILE.json ...]
# Prints, per file: spookFixed, herderAlarm, rows read, mean herd, ranOff, refetched, escaped; then the mean over files.
#   python tools/runoff_rate.py --check TARGETS FILE.json [...]   (exp014's calibration check, reviewer 3c9ab09)
# TARGETS = "Y0-Y1:rate,Y0-Y1:rate,...". Prints ONLY the mean ranOff over the files per period, its target, and pass
# (within 15%) or fail; no herd size, fetch-back or loss is printed, so the check reads nothing else of the runs.
import json, sys

def rates(f, y0, y1):
    d = json.load(open(f, encoding="utf-8")); P = d.get("_parameters") or {}
    rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
    hd = sum(r.get("herded") or 0 for r in rows)
    if not rows or hd == 0: return P, len(rows), 0, None
    return P, len(rows), hd / len(rows), {k: sum(r.get(k) or 0 for r in rows) / hd for k in ("ranOff", "refetched", "escaped")}

def check():
    targets = [(tuple(map(int, w.split("-"))), float(r)) for w, r in (p.split(":") for p in sys.argv[2].split(","))]
    ok = True
    for (y0, y1), tgt in targets:
        v = [r["ranOff"] for f in sys.argv[3:] for _, _, _, r in [rates(f, y0, y1)] if r is not None]
        if not v: print(f"{y0}-{y1}: no herd goats in any file: fail"); ok = False; continue
        m = sum(v) / len(v); good = abs(m / tgt - 1) <= 0.15; ok &= good
        print(f"{y0}-{y1}: ranOff {m:.3f} target {tgt:.3f} ratio {m / tgt:.2f} {'pass' if good else 'FAIL'}")
    print("calibration check: " + ("PASS" if ok else "FAIL"))

def main():
    if sys.argv[1] == "--check": return check()
    y0, y1 = map(int, sys.argv[1].split("-")); acc = []
    for f in sys.argv[2:]:
        P, n, mh, r = rates(f, y0, y1)
        name = f.replace("\\", "/").split("/")[-1]
        if r is None: print(f"{name}: no herd goats in {y0}-{y1} ({n} rows)"); continue
        acc.append(r)
        print(f"{name}: spookFixed {P.get('spookFixed', 0)} herderAlarm {P.get('herderAlarm')} rows {n} herd {mh:.1f}  "
              f"ranOff {r['ranOff']:.3f}  refetched {r['refetched']:.3f}  escaped {r['escaped']:.3f}")
    if acc:
        print("mean over files: " + "  ".join(f"{k} {sum(a[k] for a in acc) / len(acc):.3f}" for k in ("ranOff", "refetched", "escaped")))

main()
