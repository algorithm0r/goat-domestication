# ref_match.py: are two folders' runs of one arm the same runs? (analysis session, 2026-11-24, for the exp017 gene-flow
# plan: may exp009's REF stand in for exp005/006's REF on the counters the older runs lack?)
#   python tools/ref_match.py "A_DIR[;A_DIR...]" "B_DIR[;B_DIR...]" ARM [--bad param|rec|noskip]
# Per seed both have:
#   parameters: equal apart from id, the output-only logHistDepth, cInitLo/cInitHi (exp009's neutral marker C, which has
#     its own random stream), and keys B has that A lacks, each at its identity value (IDENT). Anything else stops.
#   year records: compared record by record over the keys both have; inside a dict value the key "C" (the marker's
#     field in traitMeans, herdTraitMeans, selSire, selDam) is left out. Printed: records compared, how many differ, the
#     first differing year and keys, and the keys only in B.
# --bad param: B's minLoad changed (must stop); rec: A's herded changed in one record (must show 1 differing record);
# noskip: C kept (must show differing records, so the C exclusion is what makes a match).
import glob, json, os, re, sys

SKIP_PARAMS = {"id", "logHistDepth", "cInitLo", "cInitHi"}
IDENT = {"buckPrefValue": 0, "doePrefValue": 0}   # keys added after exp005 (1468afe); 0 = no preference term

def runs(dirs, arm):
    R = {}
    for d in dirs.split(";"):
        for f in glob.glob(os.path.join(d, f"{arm}_seed*.json")):
            m = re.match(rf"{re.escape(arm)}_seed(\d+)\.json$", os.path.basename(f))
            if m:
                if int(m.group(1)) in R: sys.exit(f"duplicate seed {m.group(1)}: {f}")
                R[int(m.group(1))] = f
    return R

def strip(v, skip):
    return {k: x for k, x in v.items() if k != "C"} if skip and isinstance(v, dict) else v

def compare(a, b, bad=None):
    pa, pb = a["_parameters"], dict(b["_parameters"])
    if bad == "param": pb["minLoad"] = (pb.get("minLoad") or 0) + 0.5
    for k in sorted(set(pa) | set(pb)):
        if k in SKIP_PARAMS: continue
        if k not in pa:
            if k not in IDENT or pb[k] != IDENT[k]: return f"STOP: parameter {k}={pb[k]!r} only in B, not at identity"
        elif k not in pb: return f"STOP: parameter {k} only in A"
        elif pa[k] != pb[k]: return f"STOP: parameter {k} differs: {pa[k]!r} against {pb[k]!r}"
    ya, yb = a["years"], b["years"]
    if bad == "rec": ya = [dict(r, herded=r["herded"] + 1) if i == len(ya) // 2 else r for i, r in enumerate(ya)]
    skip = bad != "noskip"
    n = min(len(ya), len(yb)); diff = 0; first = None
    for i in range(n):
        ks = set(ya[i]) & set(yb[i])
        d = sorted(k for k in ks if strip(ya[i][k], skip) != strip(yb[i][k], skip))
        if d:
            diff += 1
            if first is None: first = (ya[i]["year"] + 1, d[:6])
    onlyb = sorted(set(yb[0]) - set(ya[0])); onlya = sorted(set(ya[0]) - set(yb[0]))
    return (f"{n} records compared ({len(ya)} against {len(yb)}), {diff} differ"
            + (f", first at year {first[0]} in {first[1]}" if first else "")
            + f"; keys only in B {onlyb}" + (f"; only in A {onlya}" if onlya else ""))

def main():
    a = sys.argv[1:]; bad = None
    if "--bad" in a: i = a.index("--bad"); bad = a[i + 1]; del a[i:i + 2]
    A, B = runs(a[0], a[2]), runs(a[1], a[2])
    shared = sorted(set(A) & set(B))
    print(f"{a[2]}: A {a[0]} (seeds {sorted(A)}); B {a[1]} (seeds {sorted(B)}); shared {shared}"
          + (f"; --bad {bad}" if bad else ""))
    for s in shared:
        print(f"  seed {s}: " + compare(json.load(open(A[s], encoding="utf-8")), json.load(open(B[s], encoding="utf-8")), bad))

if __name__ == "__main__": main()
