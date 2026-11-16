# wb_tab.py: the winter-budget sweep's counters per arm and window (results/winterbudget), plus reproduction checks.
import json, os
SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/"
ARMS = ["S0", "noWC", "Wb100", "Wb75", "Wb50", "Wb25"]
WINS = [(801, 900), (1501, 1600)]
def load(p):
    with open(SIM + p, encoding="utf-8") as f: return json.load(f)
runs = {a: [load(f"results/winterbudget/{a}_seed{s}.json") for s in (1, 2, 3, 4) if os.path.exists(SIM + f"results/winterbudget/{a}_seed{s}.json")] for a in ARMS}

# reproduction: Wb100 vs results/husb HmaxH, noWC vs results/husbablate noWC, S0 vs results/settle S0 (first 1600 years)
for a, ref in [("Wb100", "results/husb/HmaxH"), ("noWC", "results/husbablate/noWC"), ("S0", "results/settle/S0")]:
    for s, d in enumerate(runs[a], 1):
        r = load(f"{ref}_seed{s}.json")["years"]
        bad = sum(1 for y in range(len(d["years"])) if any(k != "chosenSiredShare" and d["years"][y].get(k) != v for k, v in r[y].items()))
        print(f"repro {a} seed {s} vs {ref}: {bad} of {len(d['years'])} years differ")

for a0, b0 in WINS:
    print(f"\n== {a0}-{b0}")
    print("arm    herd  starv  culled  due  credited  off(k/d/b/o/capt)        surplus(k/d/b/o/capt)    winter(k/d/b/o/capt)     huntTries  hunted  capt  capt/1000tries  wildNear  esc")
    for a in ARMS:
        R = [r for d in runs[a] for r in d["years"] if a0 - 1 <= r["year"] <= b0 - 1]
        if not R: continue
        n = len(R); m = lambda f: sum(f(r) for r in R) / n
        tal = lambda k: [m(lambda r, i=i: ((r.get("cullTally") or {}).get(k) or [0] * 5)[i]) for i in range(5)]
        fmt = lambda v: "/".join(f"{x:.1f}" for x in v)
        tries = m(lambda r: r.get("huntTries") or 0); capt = m(lambda r: r.get("captured") or 0)
        print(f"{a:6s} {m(lambda r: r.get('herded') or 0):5.1f} {m(lambda r: (r.get('herdDeaths') or {}).get('starvation', 0)):6.1f} {m(lambda r: r.get('culledHerd') or 0):6.1f}"
              f" {m(lambda r: r.get('offtakeDue') or 0):5.1f} {m(lambda r: r.get('offtakeCredited') or 0):6.1f}   {fmt(tal('offtake')):24s} {fmt(tal('surplus')):24s} {fmt(tal('winter')):24s}"
              f" {tries:7.0f} {m(lambda r: (r.get('deaths') or {}).get('hunted', 0)):7.1f} {capt:5.1f} {1000 * capt / tries if tries else float('nan'):8.1f}"
              f" {m(lambda r: r.get('wildNearCamp') or 0):9.2f} {m(lambda r: r.get('escaped') or 0):5.1f}")
