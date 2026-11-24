# flow_digest.py: one table, measure by window, from flow_tab.py outputs (analysis session, 2026-11-24, for the exp017
# gene-flow entry). It reformats only: each cell is the seed mean flow_tab printed (its SE dropped), so a digest cell can
# be traced to its flow_<window>.txt.
#   python tools/flow_digest.py "FILE[;FILE...]" ARM,ARM... KEY,KEY... [--bad swap]
# FILE is a flow_tab output (its first line names the window). --bad swap: the first two arms' columns are swapped, and
# the self-check (each digest cell equals the cell flow_tab printed for that arm, window and key) must stop.
import re, sys

def read(f):
    L = open(f, encoding="utf-8").read().splitlines()
    w = re.match(r"years (\d+-\d+);", L[0]).group(1)
    head = [c.strip() for c in L[1].strip("|").split("|")]
    T = {}
    for l in L[3:]:
        if not l.startswith("| "): break
        c = [x.strip() for x in l.strip("|").split("|")]
        T[c[0]] = {k: v.split(" ")[0] for k, v in zip(head, c)}
    return w, T

def main():
    a = sys.argv[1:]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    files, arms, keys = a[0].split(";"), a[1].split(","), a[2].split(",")
    W = [read(f) for f in files]
    cols = arms[:]
    if bad == "swap": cols[0], cols[1] = cols[1], cols[0]
    rows = []
    for k in keys:
        for w, T in W:
            rows.append((k, w, [T.get(arm, {}).get(k, "") or "-" for arm in cols]))
    for k, w, cells in rows:   # self-check against the source tables, by arm name
        for arm, v in zip(arms, cells):
            src = dict(W)[w].get(arm, {}).get(k, "") or "-"
            if v != src: sys.exit(f"check failed: {k} {w} {arm}: digest {v}, flow_tab {src}")
    print("| measure | years | " + " | ".join(arms) + " |\n|" + "---|" * (len(arms) + 2))
    for k, w, cells in rows: print(f"| {k} | {w} | " + " | ".join(cells) + " |")

if __name__ == "__main__": main()
