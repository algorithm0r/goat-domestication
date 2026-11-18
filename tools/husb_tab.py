# (moved from the session scratchpad 2026-11-18; EXPLOG entries that say "scratchpad husb_tab.py" mean this file)
# husb_tab.py: score the new-husbandry pilot against its controls.
# Windows are 1-based year ranges (3201-4000 = year records 3200..3999).
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from runio import hist_rows
SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/"
ARMS = [("HmaxH", "results/husb/HmaxH"), ("S0", "results/settle/S0"),
        ("HmaxIsoH", "results/husb/HmaxIsoH"), ("HmaxIso", "results/iso/HmaxIso")]
WINS = [(401, 500), (801, 900), (1201, 1300), (1501, 1600), (3201, 4000)]
if len(sys.argv) > 1:   # label=prefix ... [--wins a-b,c-d]
    a = sys.argv[1:]
    if "--wins" in a:
        k = a.index("--wins"); WINS = [tuple(int(x) for x in w.split("-")) for w in a[k + 1].split(",")]; a = a[:k] + a[k + 2:]
    ARMS = [tuple(x.split("=", 1)) for x in a]
GENES = "R A S B H T M W L C".split()
CORE = "R A S B H T M W L".split()

def load(p):
    with open(SIM + p, encoding="utf-8") as f: return json.load(f)

def mean(xs): return sum(xs) / len(xs) if xs else float("nan")

out = []
def say(*a): out.append(" ".join(str(x) for x in a))

for arm, pre in ARMS:
    runs = []
    for s in (1, 2, 3, 4):
        p = f"{pre}_seed{s}.json"
        if os.path.exists(SIM + p): runs.append((s, load(p)))
    say(f"\n== {arm}: {len(runs)} seeds")
    if not runs: continue
    for s, d in runs:
        last = max((r["year"] for r in d["years"] if (r.get("herded") or 0) > 0), default=None)
        say(f"  seed {s}: {len(d['years'])} years, last year with a herd {last}")
    for a, b in WINS:
        def win(d): return [r for r in d["years"] if a - 1 <= r["year"] <= b - 1]
        herd = mean([mean([r.get("herded") or 0 for r in win(d)]) for _, d in runs])
        per = [round(mean([r.get("herded") or 0 for r in win(d)]), 1) for _, d in runs]
        rows = [r for _, d in runs for r in win(d)]
        if not rows: continue
        hd = lambda k: mean([(r.get("herdDeaths") or {}).get(k, 0) for r in rows])
        g = lambda k: mean([r.get(k) or 0 for r in rows])
        say(f"  {a}-{b}: herd {herd:.1f} per seed {per} births {g('herdBirths'):.1f} culled {g('culledHerd'):.1f}"
            f" (surplus {g('surplusBucks'):.1f}, winter {g('winterCulled'):.1f}) starv {hd('starvation'):.1f}"
            f" other {sum(hd(k) for k in ('predation','age','other','fight','exposure','hunted')):.1f}"
            f" capt {g('captured'):.1f} esc {g('escaped'):.1f} lost {g('runOffLost'):.1f} milk {g('milk')/1e6:.2f}M")
        # gaps, depth, IBD over seeds with a herd in the window
        gaps = {t: [] for t in GENES}; dep = []; F = []
        for s, d in runs:
            ys = [r for r in win(d) if (r.get("herded") or 0) > 0]
            if not ys: continue
            gs = {t: [] for t in GENES}
            for r in ys:
                n = r["goats"]; nh = r.get("herded") or 0   # = the histogram counts (checked on credit CH seed 1, 1600 of 1600 years)
                if n - nh <= 0: continue
                for t in GENES:
                    hm = r["herdTraitMeans"][t]; am = r["traitMeans"][t]
                    gs[t].append(hm - (am * n - hm * nh) / (n - nh))
            for t in GENES: gaps[t].append(mean(gs[t]))
            dep.append(mean([r.get("herdAncDepth") or 0 for r in ys])); F.append(mean([r.get("herdF") or 0 for r in ys]))
        if dep:
            gm = {t: mean(gaps[t]) for t in GENES}
            br = sum(1 for t in CORE if abs(gm[t]) >= 0.10)
            say("     gaps " + " ".join(f"{t} {gm[t]:+.2f}" for t in GENES) + f" | breadth {br} depth {mean(dep):.1f} IBD {mean(F):.2f}")
            # overlap pooled over seeds with a herd
            ov = {}
            for t in GENES:
                H = [0] * 20; Wd = [0] * 20
                for s, d in runs:
                    for y in hist_rows(d, a - 1, b - 1):
                        hh = d["histHerd"][t][y]
                        if sum(hh) == 0: continue
                        for k in range(20): H[k] += hh[k]; Wd[k] += d["hist"][t][y][k] - hh[k]
                sh, sw = sum(H), sum(Wd)
                ov[t] = sum(min(H[k] / sh, Wd[k] / sw) for k in range(20)) if sh and sw else float("nan")
            Rh = 0; Rn = 0
            for s, d in runs:
                for y in hist_rows(d, a - 1, b - 1):
                    hh = d["histHerd"]["R"][y]; Rh += sum(hh[8:]); Rn += sum(hh)
            say("     overlap " + " ".join(f"{t} {ov[t]:.2f}" for t in GENES) + f" | herd R>=0.40 {Rh / Rn if Rn else float('nan'):.3f}")

print("\n".join(out))
