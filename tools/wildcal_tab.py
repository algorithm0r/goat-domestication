"""wildcal_tab.py: wild growth calibration (EXPLOG 2026-11-17, growth pace calibrated to wild goats).

    python tools/wildcal_tab.py Y0 Y1 LABEL=GLOB [LABEL=GLOB ...]

Per arm, wild goats, years Y0..Y1 pooled over seeds: mean size by age bin 0-12 for does and bucks, adult size A
(mean of bins 8-12), t95 (age where the bin means first reach 0.95 A, linear between bin midpoints a + 0.5), and the
wild median age at first kid (mean of yearly medians from firstKidStats). Bins with no goats are skipped.
"""
import glob, json, sys

def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None

def t95(bins):
    adult = mean([bins.get(a) for a in range(8, 13)])
    if adult is None: return None, None
    goal, prev = 0.95 * adult, None
    for a in sorted(bins):
        v = bins[a]
        if v is None: continue
        if v >= goal:
            if prev is None: return a + 0.5, adult
            pa, pv = prev
            return pa + 0.5 + (goal - pv) / (v - pv) * (a - pa), adult
        prev = (a, v)
    return None, adult

def main():
    y0, y1 = int(sys.argv[1]), int(sys.argv[2])
    for arg in sys.argv[3:]:
        label, pat = arg.split("=", 1)
        files = sorted(glob.glob(pat))
        size = {}; q50 = []
        for f in files:
            d = json.load(open(f))
            for r in d["years"]:
                if not (y0 <= r["year"] + 1 <= y1): continue
                for s in (0, 1):
                    for a, v in enumerate(r["sizeByAge"][0][s]):
                        if v is not None: size.setdefault((s, a), []).append(v)
                o = (r.get("firstKidStats") or {}).get("wild")
                if o: q50.append(o["q50"])
        out = [f"{label} ({len(files)} runs)"]
        for s, name in ((0, "F"), (1, "M")):
            bins = {a: mean(size.get((s, a), [])) for a in range(13)}
            t, A = t95(bins)
            out.append(f"{name} A {A:.3f} t95 {t:.2f}" if t is not None else f"{name} A {A} t95 none")
            out.append(f"{name} " + " ".join(f"{a}:{bins[a]:.2f}" for a in range(13) if bins[a] is not None))
        fk = mean(q50)
        out.append(f"wild first kid median {fk:.0f} d" if fk is not None else "wild first kid: none")
        print("\n   ".join(out))

main()
