# wildr_tab.py: the wild's R and the herd's R by window, beside feral (exploratory; analysis session, 2026-11-24, for
# Chris's "in REF wild moves with the herd at first but then springs back", added after the exp017 gene-flow entry was
# read, at the steward's request).
#   python tools/wildr_tab.py "DIR[;DIR...]" SCORED.txt ARM,ARM... W0-W1[,W0-W1...] [--perseed] [--bad allgoats|jcol]
# Per run and window, from tools/split_tab.py's split (histogram rows with herd and wild goats; founders = the run's
# 301-400 all-goat mean F): wild R = F + wild change, herd R = F + herd change (genotype means of R, 20-bucket
# histograms at midpoints); feral = wildHerdShare, mean over the window's year rows (as tools/flow_tab.py).
# The founders' R (F, the run's 301-400 all-goat mean) is printed as its mean over all seeds, the level the wild started from.
# Per arm and window: the seeds established by the window's start (jump_tab's J <= W0, from SCORED.txt's per-seed
# table, as tools/flow_est.py), their mean and min-max of wild R, herd R and feral, and the same means over all seeds.
# Checks: split's own identity (herd change - wild change = settle_tab's gap, every run); at 3201-4000 each run's herd
# and wild change of R, to three places, must equal SCORED.txt's per-seed "herd change R" and "wild change R"; for
# every arm, the seeds with a J must equal SCORED.txt's est column (herd >= 100 over 3201-4000; flow_est.check_est, run
# whenever SCORED.txt is read, for any window, before any output, from 2026-11-24). The tool stops if any fails.
# --timeline (2026-11-24, the steward): 100-year bins 401-500 ... 1501-1600, then 3201-4000, in place of the windows
# argument; per arm and bin, wild R and herd R as the mean over all seeds (min-max over seeds), with how many seeds are
# established at the bin's start; the founders' R (301-400) heads each arm. The checks above run as before.
# With --timeline each arm also shows its runs' humansAt/herdingAt and, before herding (every goat wild), the all-goat
# R by bin 101-200, 201-300, 301-350, 351-400 (the tool stops if any of those rows has a herd goat); with --perseed,
# each seed's bin holding J, how many bins after it the low comes, and the highest of the next three bins after the low
# (the reviewer's 497d6ea). --bad prebin stretches the last pre-herding bin to 351-450, into herding, and must stop.
# --bad allgoats: herd means from all goats (split's own bad case); --bad jcol: the span column read as J. Each must stop.
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import split_tab, flow_est

def scored_change(S):
    C = {}
    for l in S:
        c = [x.strip() for x in l.strip("|").split("|")] if l.startswith("| ") else []
        if len(c) == 9 and c[1].isdigit() and re.match(r"[-+]\d\.\d{3}$", c[7] or "") and re.match(r"[-+]\d\.\d{3}$", c[8] or ""):
            C.setdefault(c[0], {})[int(c[1])] = (c[7], c[8])
    return C

def main():
    a = sys.argv[1:]; bad = None; per = "--perseed" in a; tl = "--timeline" in a
    if per: a.remove("--perseed")
    if tl: a.remove("--timeline")
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    dirs, S = a[0], open(a[1], encoding="utf-8").read().splitlines()
    arms = a[2].split(",")
    wins = ([(y, y + 99) for y in range(401, 1601, 100)] + [(3201, 4000)]) if tl else \
        [tuple(int(v) for v in w.split("-")) for w in a[3].split(",")]
    J, est = flow_est.scoredJ(S, "jcol" if bad == "jcol" else None); SC = scored_change(S)
    flow_est.check_est(J, est, arms)   # whenever SCORED.txt is read, before any output (the reviewer's 54f3c87)
    R = {}
    for folder in dirs.split(";"):
        for f in glob.glob(os.path.join(folder, "*.json")):
            m = re.match(r"(.+)_seed(\d+)\.json$", os.path.basename(f))
            if m and m.group(1) in arms:
                if int(m.group(2)) in R.setdefault(m.group(1), {}): sys.exit(f"duplicate {f}")
                R[m.group(1)][int(m.group(2))] = f
    PRE = [(101, 200), (201, 300), (301, 350), (351, 450 if bad == "prebin" else 400)]; PV, HA = {}, {}
    V = {}   # V[arm][seed][win] = (wildR, herdR, feral, herd change R, wild change R)
    for arm in arms:
        for s, f in sorted(R.get(arm, {}).items()):
            d = json.load(open(f, encoding="utf-8"))
            if tl:   # before herding every goat is wild: all-goat R by pre-herding bin (humans hunt from humansAt)
                for b in PRE:
                    ix = [i for i, y in enumerate(d["histYears"]) if b[0] <= y + 1 <= b[1]]
                    if any(sum(d["histHerd"]["R"][i]) for i in ix): sys.exit(f"{arm} s{s}: herd goats in {b[0]}-{b[1]}")
                    if ix: PV.setdefault(arm, {}).setdefault(s, {})[b] = sum(split_tab.mc(d["hist"]["R"][i]) for i in ix) / len(ix)
                HA.setdefault(arm, set()).add((d["_parameters"].get("humansAt"), d["_parameters"].get("herdingAt")))
            for w in wins:
                r = split_tab.split(d, w[0], w[1], 301, 400, "allgoats" if bad == "allgoats" else None)
                if r is None: continue
                out, F, _ = r; hc, wc = out["R"]
                fer = [x["wildHerdShare"] for x in d["years"] if w[0] <= x["year"] + 1 <= w[1] and x.get("wildHerdShare") is not None]
                V.setdefault(arm, {}).setdefault(s, {})[w] = (F["R"] + wc, F["R"] + hc, sum(fer) / len(fer) if fer else None, hc, wc, F["R"])
            if (3201, 4000) in V.get(arm, {}).get(s, {}) and arm in SC:
                hc, wc = V[arm][s][(3201, 4000)][3:5]
                if (f"{hc:+.3f}", f"{wc:+.3f}") != SC[arm].get(s): sys.exit(f"check failed: {arm} s{s}: herd/wild change R {hc:+.3f}/{wc:+.3f}, scored {SC[arm].get(s)}")
    f3 = lambda x: "-" if x is None else f"{x:.3f}"
    rng = lambda xs: f"{f3(sum(xs) / len(xs))} ({f3(min(xs))}-{f3(max(xs))})" if xs else "-"
    mean = lambda xs: f3(sum(xs) / len(xs)) if xs else "-"
    if tl:
        print("Wild R and herd R (genotype means of R) in 100-year bins over herding years 1-1200 (401-1600), then 3201-4000;"
              " exploratory, added after the exp017 gene-flow entry was read. Per bin: the mean over all seeds (min-max over"
              f" seeds); established = seeds with J <= the bin's start (from {a[1]}).")
        for arm in arms:
            if arm not in V: continue
            Fs = [v[w][5] for v in V[arm].values() for w in wins[:1] if w in v]
            print(f"\n{arm}: founders (301-400, all goats wild) R {rng(Fs)}; humansAt/herdingAt {sorted(HA.get(arm, []))}"
                  "\n  before herding, all-goat R by bin: " + "; ".join(f"{b[0]}-{b[1]} {rng([PV[arm][x][b] for x in PV.get(arm, {}) if b in PV[arm][x]])}" for b in PRE)
                  + "\n| years | seeds | established | wild R | herd R |\n|---|---|---|---|---|")
            for w in wins:
                if w == (3201, 4000) and arm in est:
                    nJ = sum(1 for s in J.get(arm, {}) if J[arm][s] is not None)
                    if nJ != est[arm]: sys.exit(f"check failed: {arm}: {nJ} seeds with a J, scored est {est[arm]}")
                rows = {s: v[w] for s, v in V[arm].items() if w in v}
                E = [s for s in rows if J.get(arm, {}).get(s) is not None and J[arm][s] <= w[0]]
                print(f"| {w[0]}-{w[1]} | {len(rows)} | {len(E)} | {rng([r[0] for r in rows.values()])} | {rng([r[1] for r in rows.values()])} |")
        # the same all-seed means, bins by arms: wild R / herd R (established seeds at the bin's start in brackets)
        sh = [arm for arm in arms if arm in V]
        print("\nAll-seed means, wild R / herd R (established at the bin's start)\n| years | " + " | ".join(sh) + " |\n|" + "---|" * (len(sh) + 1))
        for w in wins:
            cells = []
            for arm in sh:
                rows = {s: v[w] for s, v in V[arm].items() if w in v}
                E = [s for s in rows if J.get(arm, {}).get(s) is not None and J[arm][s] <= w[0]]
                cells.append(f"{mean([r[0] for r in rows.values()])} / {mean([r[1] for r in rows.values()])} ({len(E)})")
            print(f"| {w[0]}-{w[1]} | " + " | ".join(cells) + " |")
        if per:   # each seed's wild R by bin, with its lowest bin over 401-1600 and its J
            print("\nPer seed, wild R by bin (401-500 ... 1501-1600, then 3201-4000); low = the lowest bin over 401-1600")
            for arm in sh:
                for s, v in sorted(V[arm].items()):
                    xs = [(w, v[w][0]) for w in wins if w in v]; early = [x for x in xs if x[0][1] <= 1600]
                    lo = min(early, key=lambda x: x[1]) if early else None
                    j = J.get(arm, {}).get(s); jb = next((k for k, (w, _) in enumerate(early) if j is not None and w[0] <= j <= w[1]), None)
                    li = early.index(lo) if lo else None; nx = [x for _, x in early[li + 1:li + 4]] if lo else []
                    rec = ""
                    if lo:
                        rec = (f"; J's bin {early[jb][0][0]}-{early[jb][0][1]}, low {li - jb:+d} bins after it" if jb is not None else "; J outside 401-1600")
                        rec += f"; highest of the next three bins {f3(max(nx))} ({max(nx) - lo[1]:+.3f} on the low)" if nx else "; no bin after the low"
                    print(f"  {arm} s{s} (J {j or '-'}): " + " ".join(f3(x) for _, x in xs)
                          + (f"; low {f3(lo[1])} at {lo[0][0]}-{lo[0][1]}" if lo else "") + rec)
        return
    print("Wild R and herd R (genotype means of R) by window, beside feral (the wild genome's share from herd-born goats);"
          " exploratory, added after the exp017 gene-flow entry was read. Established = J <= the window's start (from "
          f"{a[1]}): mean (min-max); then the mean over all seeds.")
    for w in wins:
        print(f"\nyears {w[0]}-{w[1]}\n| arm | established | wild R est | herd R est | feral est | wild R all | herd R all | feral all | founders R all |\n|---|---|---|---|---|---|---|---|---|")
        for arm in arms:
            if arm not in V: continue
            if w == (3201, 4000) and arm in est:
                nJ = sum(1 for s in J.get(arm, {}) if J[arm][s] is not None)
                if nJ != est[arm]: sys.exit(f"check failed: {arm}: {nJ} seeds with a J, scored est {est[arm]}")
            rows = {s: v[w] for s, v in V[arm].items() if w in v}
            E = [s for s in rows if J.get(arm, {}).get(s) is not None and J[arm][s] <= w[0]]
            col = lambda k, ss: [rows[s][k] for s in ss if rows[s][k] is not None]
            print(f"| {arm} | {len(E)} of {len(rows)} | {rng(col(0, E))} | {rng(col(1, E))} | {rng(col(2, E))} | "
                  f"{mean(col(0, rows))} | {mean(col(1, rows))} | {mean(col(2, rows))} | {mean(col(5, rows))} |")
    if per:
        print("\nPer run: window wild R / herd R / feral" + "".join(
            f"\n  {arm} s{s}: " + "; ".join(f"{w[0]}-{w[1]} {f3(v[w][0])} / {f3(v[w][1])} / {f3(v[w][2])}" for w in wins if w in v)
            for arm in arms if arm in V for s, v in sorted(V[arm].items())))

if __name__ == "__main__": main()
