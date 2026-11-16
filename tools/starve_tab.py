# starve_tab.py: who starves in the herd (results/starve): herdStarve by season and class, by month, rates per head,
# with the reproduction check against results/offtake and the add-up check on every year.
import json
SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/"
ARMS = ["R15", "R10", "S0"]; WINS = [(801, 900), (1501, 1600)]
CL = ["unweaned", "weaned<1y", "doe preg/nurs", "doe dry", "buck", "other"]
def load(p):
    with open(SIM + p, encoding="utf-8") as f: return json.load(f)["years"]
runs = {a: [load(f"results/starve/{a}_seed{s}.json") for s in (1, 2, 3, 4)] for a in ARMS}
for a in ARMS:
    for s, d in enumerate(runs[a], 1):
        r = load(f"results/offtake/{a}_seed{s}.json")
        bad = sum(1 for y in range(len(d)) if any(k != "chosenSiredShare" and d[y].get(k) != v for k, v in r[y].items()))
        st = lambda x: (x.get("herdDeaths") or {}).get("starvation", 0)
        add = sum(1 for x in d if sum(x["herdStarve"]["lean"]) + sum(x["herdStarve"]["grow"]) == st(x) == sum(x["herdStarveMonth"]))
        print(f"{a} seed {s}: {bad} of {len(d)} years differ from results/offtake; totals add up in {add} of {len(d)} years; years with herd starvation {sum(1 for x in d if st(x) > 0)}")
for a0, b0 in WINS:
    print(f"\n== {a0}-{b0}, per year, 4 seeds")
    for a in ARMS:
        R = [x for d in runs[a] for x in d if a0 - 1 <= x["year"] <= b0 - 1]; n = len(R)
        lean = [sum(x["herdStarve"]["lean"][i] for x in R) / n for i in range(6)]
        grow = [sum(x["herdStarve"]["grow"][i] for x in R) / n for i in range(6)]
        mon = [sum(x["herdStarveMonth"][i] for x in R) / n for i in range(12)]
        tot = sum(lean) + sum(grow)
        cr = [x for x in R if x.get("herdComp")]; comp = [sum(x["herdComp"][i] for x in cr) / len(cr) for i in range(4)]
        camps = sum((x.get("herded") or 0) for x in R) / n / sum(comp)          # herded at year end / mean head per camp
        print(f"{a}: herd starvation {tot:.1f} ({100 * sum(lean) / tot if tot else 0:.0f}% lean), herd {sum((x.get('herded') or 0) for x in R) / n:.1f}, camps ~{camps:.1f}")
        for i, c in enumerate(CL): print(f"   {c:14s} lean {lean[i]:5.1f}  grow {grow[i]:5.1f}  share {100 * (lean[i] + grow[i]) / tot if tot else 0:4.0f}%")
        does, bucks = comp[1] * camps, comp[2] * camps
        print(f"   per head a year: breeding does {(lean[2] + lean[3] + grow[2] + grow[3]) / does if does else 0:.3f} ({does:.0f} head), bucks {(lean[4] + grow[4]) / bucks if bucks else 0:.3f} ({bucks:.0f} head)")
        print("   by month (0 = days 0-29; lean from day 172):", " ".join(f"{m:.1f}" for m in mon))
