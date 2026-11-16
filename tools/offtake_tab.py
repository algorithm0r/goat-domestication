# offtake_tab.py: the offtake rate and timing sweep (results/offtake): counters per arm and window, herd composition,
# the S0 reproduction check, and captures against herd size.
import json, os
SIM = "D:/Chris's Documents/Documents/Research/Animal Domestication/sim/"
ARMS = [("S0", "offtake"), ("R10", "offtake"), ("R15", "offtake"), ("R20", "offtake"), ("R30", "offtake"),
        ("P10", "offtake"), ("P20", "offtake"), ("noWC", "winterbudget"), ("Wb100", "winterbudget")]
WINS = [(801, 900), (1501, 1600)]
def load(p):
    with open(SIM + p, encoding="utf-8") as f: return json.load(f)
runs = {a: [load(f"results/{d}/{a}_seed{s}.json") for s in (1, 2, 3, 4) if os.path.exists(SIM + f"results/{d}/{a}_seed{s}.json")] for a, d in ARMS}
for s, d in enumerate(runs["S0"], 1):
    r = load(f"results/winterbudget/S0_seed{s}.json")["years"]
    bad = sum(1 for y in range(len(d["years"])) if any(k != "chosenSiredShare" and d["years"][y].get(k) != v for k, v in r[y].items()))
    print(f"repro S0 seed {s} vs results/winterbudget: {bad} of {len(d['years'])} years differ")
def rank(xs):
    o = sorted(range(len(xs)), key=lambda i: xs[i]); r = [0] * len(xs)
    for k, i in enumerate(o): r[i] = k
    return r
for a0, b0 in WINS:
    print(f"\n== {a0}-{b0}  (per year, 4 seeds; comp = mean per camp: kids/does/bucks/other)")
    print("arm    seeds herd  starv culled off(k/d/b/o/capt)        comp(k/d/b/o)          buck:doe  tries  capt  capt/1000  wildNear  esc")
    H, C = [], []
    for a, _ in ARMS:
        R = [r for d in runs[a] for r in d["years"] if a0 - 1 <= r["year"] <= b0 - 1]
        if not R: continue
        n = len(R); m = lambda f: sum(f(r) for r in R) / n
        tal = [m(lambda r, i=i: ((r.get("cullTally") or {}).get("offtake") or [0] * 5)[i]) for i in range(5)]
        cr = [r for r in R if r.get("herdComp")]
        comp = [sum(r["herdComp"][i] for r in cr) / len(cr) for i in range(4)] if cr else None
        fmt = lambda v: "/".join(f"{x:.1f}" for x in v)
        tries = m(lambda r: r.get("huntTries") or 0); capt = m(lambda r: r.get("captured") or 0); herd = m(lambda r: r.get("herded") or 0)
        if a in ("S0", "R10", "R15", "R20", "R30", "P10", "P20"): H.append(herd); C.append(capt)
        print(f"{a:6s} {len(runs[a]):5d} {herd:5.1f} {m(lambda r: (r.get('herdDeaths') or {}).get('starvation', 0)):6.1f} {m(lambda r: r.get('culledHerd') or 0):6.1f}"
              f"  {fmt(tal):24s} {fmt(comp) if comp else '-':22s} {comp[2] / comp[1] if comp and comp[1] else float('nan'):6.2f}"
              f"  {tries:5.0f} {capt:5.1f} {1000 * capt / tries if tries else float('nan'):8.1f} {m(lambda r: r.get('wildNearCamp') or 0):9.2f} {m(lambda r: r.get('escaped') or 0):5.1f}")
    if len(H) > 2:
        rh, rc = rank(H), rank(C); k = len(H)
        print(f"rank correlation, captures vs herd (S0, R, P arms): {1 - 6 * sum((x - y) ** 2 for x, y in zip(rh, rc)) / (k * (k * k - 1)):.2f}")
