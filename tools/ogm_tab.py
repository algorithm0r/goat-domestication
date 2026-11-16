"""ogm_tab.py: age at first kid against the mother's B and growth multiplier (EXPLOG 2026-11-14, coupled growth).

    python tools/ogm_tab.py Y0 Y1 LABEL=GLOB [LABEL=GLOB ...]

Per arm and population (wild, herd), years Y0..Y1 pooled over seeds, from firstKidStats: first kids per year, the mean
of yearly quartiles of age at first kid (q25, q50, q75) and of the yearly interquartile range, and pooled correlations
of age at first kid with the mother's B (r_B) and with her growth multiplier (r_g; undefined when growSD is 0).
"""
import glob, json, math, sys

def mean(xs):
    xs = [x for x in xs if x is not None and x == x]
    return sum(xs) / len(xs) if xs else float("nan")

def corr(n, x, xx, y, yy, xy):
    vx, vy = n * xx - x * x, n * yy - y * y
    return (n * xy - x * y) / math.sqrt(vx * vy) if vx > 1e-12 and vy > 1e-12 else float("nan")

def main():
    y0, y1 = int(sys.argv[1]), int(sys.argv[2])
    for arg in sys.argv[3:]:
        label, pat = arg.split("=", 1)
        files = sorted(glob.glob(pat))
        if not files:
            print(f"{label}: no files for {pat}"); continue
        print(f"== {label}: {len(files)} runs, years {y0}-{y1}")
        for pop in ("wild", "herd"):
            S = dict(n=0, a=0, aa=0, b=0, bb=0, ab=0, g=0, gg=0, ag=0); q = {"q25": [], "q50": [], "q75": [], "iqr": []}
            years = 0
            for f in files:
                d = json.load(open(f))
                for r in d["years"]:
                    if not (y0 <= r["year"] + 1 <= y1): continue
                    years += 1
                    o = (r.get("firstKidStats") or {}).get(pop)
                    if not o: continue
                    for k in S: S[k] += o[k]
                    for k in ("q25", "q50", "q75"): q[k].append(o[k])
                    q["iqr"].append(o["q75"] - o["q25"])
            if S["n"] == 0:
                print(f"   {pop}: no first kids"); continue
            n = S["n"]
            rB = corr(n, S["b"], S["bb"], S["a"], S["aa"], S["ab"])
            rg = corr(n, S["g"], S["gg"], S["a"], S["aa"], S["ag"])
            print(f"   {pop:4s} first kids/yr {n / years:.1f}  age q25 {mean(q['q25']):.0f} q50 {mean(q['q50']):.0f}"
                  f" q75 {mean(q['q75']):.0f}  IQR {mean(q['iqr']):.0f}  mean {S['a'] / n:.0f}"
                  f"  r_B {rB:+.3f}  r_g {rg:+.3f}  mean B {S['b'] / n:.3f}")

main()
