# wintercull2_tab.py: the partial winter cull sweep (results/wintercull2) against R15 (results/spring): herd, starvation by class and month, culls.
# (Derived from tools/spring_tab.py.)
import json
SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/"

DIRS = {"R15": "results/spring", "W50A": "results/wintercull2", "W25A": "results/wintercull2", "W50": "results/wintercull2"}
ARMS = list(DIRS); WINS = [(801, 900), (1501, 1600)]
CL = ["unweaned", "weaned<1y", "doe preg/nurs", "doe dry", "buck", "other"]
def load(p):
    with open(SIM + p, encoding="utf-8") as f: return json.load(f)["years"]
runs = {a: [load(f"{DIRS[a]}/{a}_seed{s}.json") for s in (1, 2, 3, 4)] for a in ARMS}
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
        wt = [m(lambda x, i=i: ((x.get("cullTally") or {}).get("winter") or [0] * 5)[i]) for i in range(5)]
        print(f"      winter cull k/d/b/o/capt: {'/'.join(f'{v:.1f}' for v in wt)}")
        print(f"      by month: {' '.join(f'{v:.1f}' for v in mon)}")
