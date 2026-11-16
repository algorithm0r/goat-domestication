"""sexsize_tab.py: sex differences in size and growth (EXPLOG 2026-11-14), scored against Ganj Dareh.

    python tools/sexsize_tab.py Y0 Y1 LABEL=GLOB [LABEL=GLOB ...]

Per arm (means over seeds, years Y0..Y1): goats, herd, herd starvation, mean size by sex and age (wild and herd), and
the Ganj Dareh measures on herd deaths older than 6 months (herdDeathHalf), for slaughter only and for all causes:
  m<2.5   share of male deaths before 2.5 years            (Ganj Dareh 0.60-0.70)
  f>=2.5  share of female deaths at 2.5 years or older     (0.60-0.70)
  >=4     share of all deaths at 4 years or older          (about 0.20; scored as 0.15-0.25)
  F:M     female to male deaths                            (1.11-1.86)
"""
import glob, json, sys

def mean(xs):
    xs = [x for x in xs if x is not None and x == x]
    return sum(xs) / len(xs) if xs else float("nan")

BANDS = {"m<2.5": (0.60, 0.70), "f>=2.5": (0.60, 0.70), ">=4": (0.15, 0.25), "F:M": (1.11, 1.86)}

def measures(D):
    """D[sex][half] death counts, half-years 0..29; deaths under 6 months (half 0) left out."""
    F, M = D[0], D[1]
    nf, nm = sum(F[1:]), sum(M[1:])
    if nf + nm == 0: return None
    return {"m<2.5": sum(M[1:5]) / nm if nm else float("nan"),
            "f>=2.5": sum(F[5:]) / nf if nf else float("nan"),
            ">=4": (sum(F[8:]) + sum(M[8:])) / (nf + nm),
            "F:M": nf / nm if nm else float("inf"),
            "n": (nf + nm)}

def score(m):
    return sum(1 for k, (lo, hi) in BANDS.items() if lo <= m[k] <= hi)

def main():
    y0, y1 = int(sys.argv[1]), int(sys.argv[2])
    for arg in sys.argv[3:]:
        label, pat = arg.split("=", 1)
        files = sorted(glob.glob(pat))
        if not files:
            print(f"{label}: no files for {pat}"); continue
        goats, herd, starv = [], [], []
        dS = [[0] * 30 for _ in range(2)]; dA = [[0] * 30 for _ in range(2)]
        size = {}  # (where, sex, age) -> list
        for f in files:
            d = json.load(open(f))
            rows = [r for r in d["years"] if y0 <= r["year"] + 1 <= y1]
            goats.append(mean([r.get("goats") for r in rows]))
            herd.append(mean([r.get("herded") or 0 for r in rows]))
            starv.append(mean([(r.get("herdDeaths") or {}).get("starvation", 0) for r in rows]))
            for r in rows:
                H = r.get("herdDeathHalf")
                if H:
                    for s in (0, 1):
                        for h in range(30):
                            dS[s][h] += H[0][s][h]; dA[s][h] += H[0][s][h] + H[1][s][h] + H[2][s][h]
                for w in (0, 1):
                    for s in (0, 1):
                        for a, v in enumerate(r["sizeByAge"][w][s]):
                            size.setdefault((w, s, a), []).append(v)
        print(f"== {label}: {len(files)} runs, years {y0}-{y1}")
        print(f"   goats {mean(goats):.1f}  herd {mean(herd):.1f}  herd starvation/yr {mean(starv):.1f}")
        for w, name in ((0, "wild"), (1, "herd")):
            ages = (0, 1, 2, 3, 5, 8)
            fs = [mean(size.get((w, 0, a), [])) for a in ages]; ms = [mean(size.get((w, 1, a), [])) for a in ages]
            print(f"   size {name}: age " + " ".join(f"{a}:{f:.2f}/{m:.2f}" for a, f, m in zip(ages, fs, ms))
                  + f"  (F/M)  M:F at 5+ {mean([mean(size.get((w, 1, a), [])) for a in range(5, 13)]) / mean([mean(size.get((w, 0, a), [])) for a in range(5, 13)]):.2f}")
        for nm, D in (("slaughter", dS), ("all causes", dA)):
            m = measures(D)
            if not m: print(f"   {nm}: no herd deaths"); continue
            print(f"   {nm:10s} m<2.5 {m['m<2.5']:.2f}  f>=2.5 {m['f>=2.5']:.2f}  >=4 {m['>=4']:.2f}  F:M {m['F:M']:.2f}"
                  f"  deaths/yr {m['n'] / (len(files) * (y1 - y0 + 1)):.1f}  Ganj Dareh {score(m)}/4")

main()
