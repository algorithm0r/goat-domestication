# spring_tab.py: the spring feeding sweep (results/spring): herd, starvation by class and month, fodder fed in spring,
# herd composition, with the R15 reproduction check against results/starve.
import json
SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/"
import os
ARMS = [a for a in ["R15", "F30", "F60", "D60", "DY"] if os.path.exists(SIM + f"results/spring/{a}_seed4.json")]; WINS = [(801, 900), (1501, 1600)]
CL = ["unweaned", "weaned<1y", "doe preg/nurs", "doe dry", "buck", "other"]
def load(p):
    with open(SIM + p, encoding="utf-8") as f: return json.load(f)["years"]
runs = {a: [load(f"results/spring/{a}_seed{s}.json") for s in (1, 2, 3, 4)] for a in ARMS}
for s, d in enumerate(runs["R15"], 1):
    r = load(f"results/starve/R15_seed{s}.json")
    bad = sum(1 for y in range(len(d)) if any(k != "chosenSiredShare" and d[y].get(k) != v for k, v in r[y].items()))
    print(f"repro R15 seed {s} vs results/starve: {bad} of {len(d)} years differ")
st = lambda x: (x.get("herdDeaths") or {}).get("starvation", 0)
for a0, b0 in WINS:
    print(f"\n== {a0}-{b0}, per year, 4 seeds")
    print("arm   herd   starv  d30-89  late-lean  fodder(M)  spring(M)  births  culled  capt  comp(k/d/b/o)        classes(" + "/".join(CL) + ")")
    for a in ARMS:
        R = [x for d in runs[a] for x in d if a0 - 1 <= x["year"] <= b0 - 1]; n = len(R); m = lambda f: sum(f(x) for x in R) / n
        mon = [m(lambda x, i=i: x["herdStarveMonth"][i]) for i in range(12)]
        cls = [m(lambda x, i=i: x["herdStarve"]["lean"][i] + x["herdStarve"]["grow"][i]) for i in range(6)]
        comp = [m(lambda x, i=i: (x.get("herdComp") or [0] * 4)[i]) for i in range(4)]
        print(f"{a:5s} {m(lambda x: x.get('herded') or 0):5.1f} {m(st):6.1f} {mon[1] + mon[2]:6.1f} {mon[10] + mon[11] + mon[0]:8.1f}"
              f"  {m(lambda x: x['fodder']) / 1e6:8.2f}  {m(lambda x: x.get('fodderSpring', 0)) / 1e6:8.2f}  {m(lambda x: x['births']):6.1f} {m(lambda x: x.get('culledHerd') or 0):6.1f} {m(lambda x: x.get('captured') or 0):5.1f}"
              f"  {'/'.join(f'{v:.1f}' for v in comp):20s} {'/'.join(f'{v:.1f}' for v in cls)}")
        print(f"      by month: {' '.join(f'{v:.1f}' for v in mon)}")
