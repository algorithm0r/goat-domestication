# flow_est.py: flow_tab's per-seed values over the seeds established by a window's start (analysis session, 2026-11-24,
# for the reviewer's bc24350 point 1 on the exp017 gene-flow entry: an arm mean over all seeds mixes established herds
# with a herd that never formed).
#   python tools/flow_est.py FLOW.txt SCORED.txt ARM,ARM... KEY,KEY... [--alias A=B,...] [--bad jcol]
# FLOW.txt is a flow_tab output made with --perseed (its first line names the window Y0-Y1). SCORED.txt is a
# load_tab scored output: its per-seed table gives each seed's J (jump_tab's establishment year, '-' = never). A seed is
# established for the window if J <= Y0. --alias REF9=REF reads REF9's per-seed rows with REF's J (same runs).
# Per arm: the established seeds, then per key their mean and min-max, and the all-seed mean (checked against the arm
# mean flow_tab printed, to its printed precision; the tool stops if they differ).
# --against ARM (2026-11-24, the reviewer's 5ff5134): for every other arm, per key, how many of its established seeds
# lie below, inside and above ARM's established min-max (values as flow_tab prints them), naming the seeds inside.
# Check: the number of seeds with a J must equal the scored table's est column (herd >= 100 over 3201-4000) for each
# arm, or the tool stops (check_est; from 2026-11-24 it runs whenever SCORED.txt is read, for any window, before any
# output). --bad jcol reads the span column as J, and must stop.
import re, sys

def perseed(L):
    P = {}
    for l in L:
        m = re.match(r"(\S+) s(\d+): (.*)$", l)
        if m:
            kv = re.findall(r"(\w+) (-|[-+]?\d+\.\d+)", m.group(3))
            P.setdefault(m.group(1), {})[int(m.group(2))] = {k: (None if v == "-" else float(v)) for k, v in kv}
    return P

def armtable(L):
    head, T = None, {}
    for l in L:
        if l.startswith("| arm |"): head = [c.strip() for c in l.strip("|").split("|")]; continue
        if head and l.startswith("| ") and not l.startswith("| arm"):
            c = [x.strip() for x in l.strip("|").split("|")]
            if len(c) != len(head): head = None; continue
            T[c[0]] = dict(zip(head, c))
        elif head and not l.startswith("|"): head = None
    return T

def scoredJ(S, bad):
    J, est = {}, {}
    for l in S:
        c = [x.strip() for x in l.strip("|").split("|")] if l.startswith("| ") else []
        # per-seed table: | arm | seed | at 300 | J | span <60 (y) | ...
        if len(c) >= 9 and c[1].isdigit() and (c[3] == "-" or c[3].isdigit()):
            v = c[4] if bad == "jcol" else c[3]
            J.setdefault(c[0], {})[int(c[1])] = None if v == "-" else int(v)
        # main table: | arm | alarmSpread | seeds | est | by-herd ... |
        if len(c) >= 14 and c[2].isdigit() and c[3].isdigit() and "(" in c[4]: est[c[0]] = int(c[3])
    return J, est

def check_est(J, est, arms, alias=None):
    """The parsed J column against the scored est column (herd >= 100 over 3201-4000): the seeds with a J must number
    est for every arm read that has both, whatever window is asked for. Stops on a mismatch (2026-11-24, the reviewer's
    54f3c87: the check had fired only for the window 3201-4000)."""
    for arm in arms:
        src = (alias or {}).get(arm, arm)
        if src in J and src in est:
            nJ = sum(1 for s in J[src] if J[src][s] is not None)
            if nJ != est[src]: sys.exit(f"check failed: {src}: {nJ} seeds with a J, scored est {est[src]}")

def main():
    a = sys.argv[1:]; bad = None; alias = {}
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    if "--alias" in a: i = a.index("--alias"); alias = dict(p.split("=") for p in a[i + 1].split(",")); del a[i:i + 2]
    against, EV = None, {}
    if "--against" in a: i = a.index("--against"); against = a[i + 1]; del a[i:i + 2]

    F = open(a[0], encoding="utf-8").read().splitlines(); S = open(a[1], encoding="utf-8").read().splitlines()
    arms, keys = a[2].split(","), a[3].split(",")
    y0, y1 = (int(v) for v in re.match(r"years (\d+)-(\d+);", F[0]).groups())
    P, T = perseed(F), armtable(F); J, est = scoredJ(S, bad)
    check_est(J, est, arms, alias)
    print(f"years {y0}-{y1}: seeds established by {y0} (jump_tab's J <= {y0}, from {a[1]}); per key the established "
          f"seeds' mean (min-max), then the mean over all seeds. Descriptive.")
    for arm in arms:
        src = alias.get(arm, arm)
        if arm not in P or src not in J: print(f"{arm}: no per-seed rows or no J"); continue
        if (y0, y1) == (3201, 4000) and src in est:
            nJ = sum(1 for s in J[src] if J[src][s] is not None)
            if nJ != est[src]: sys.exit(f"check failed: {src}: {nJ} seeds with a J, scored est {est[src]}")
        E = sorted(s for s in P[arm] if J[src].get(s) is not None and J[src][s] <= y0)
        print(f"\n{arm}: established {len(E)} of {len(P[arm])} (seeds {E}; J " + ", ".join(f"s{s} {J[src].get(s) or '-'}" for s in sorted(P[arm])) + ")")
        for k in keys:
            allv = [P[arm][s].get(k) for s in P[arm] if P[arm][s].get(k) is not None]
            ev = [P[arm][s].get(k) for s in E if P[arm][s].get(k) is not None]
            am = sum(allv) / len(allv) if allv else None
            if am is not None and arm in T and k in T[arm]:   # all-seed mean against flow_tab's printed arm mean
                cell = T[arm][k].split(" ")[0]
                dec = len(cell.split(".")[1]) if "." in cell else 0
                if abs(am - float(cell)) > 0.5 * 10 ** -dec + 0.0005: sys.exit(f"check failed: {arm} {k}: per-seed mean {am:.4f}, flow_tab {cell}")
            f = (lambda x: f"{x:.1f}") if k == "herd" else (lambda x: f"{x:.2f}") if k == "depth" else (lambda x: f"{x:.3f}")
            es = f"{f(sum(ev) / len(ev))} ({f(min(ev))}-{f(max(ev))})" if ev else "-"
            print(f"  {k}: established {es}; all seeds {f(am) if am is not None else '-'}")
            EV.setdefault(arm, {})[k] = [(s, P[arm][s].get(k)) for s in E if P[arm][s].get(k) is not None]
    if against:   # each established seed against the reference arm's established min-max, at printed precision
        print(f"\nEstablished seeds against {against}'s established range (min-max), per key: seeds below / inside / above")
        for arm in arms:
            if arm == against or arm not in EV or against not in EV: continue
            cells = []
            for k in keys:
                ref = [v for _, v in EV[against][k]]
                if not ref or not EV[arm][k]: continue
                lo, hi = min(ref), max(ref)
                b = [s for s, v in EV[arm][k] if v < lo]; i = [s for s, v in EV[arm][k] if lo <= v <= hi]
                u = [s for s, v in EV[arm][k] if v > hi]
                cells.append(f"{k} {len(b)}/{len(i)}/{len(u)}" + (f" (inside: s{', s'.join(map(str, i))})" if i else ""))
            print(f"  {arm}: " + "; ".join(cells))

if __name__ == "__main__": main()
