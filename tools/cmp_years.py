# cmp_years.py A.json B.json [skip,keys] [--by-year]: count year records that differ between two runs (identity checks).
# (moved from the session scratchpad 2026-11-18; EXPLOG "scratchpad cmp_years.py" means this file)
# --by-year (2026-11-24): pair the records by their year rather than by position, over the years both runs recorded
# (a 1600-year annual run against a 4000-year run kept every 3rd year).
import json, sys
args = [x for x in sys.argv[1:] if x != "--by-year"]; by_year = "--by-year" in sys.argv
a = json.load(open(args[0]))["years"]; b = json.load(open(args[1]))["years"]
skip = set(args[2].split(",")) if len(args) > 2 else set()
if by_year:
    bi = {r["year"]: r for r in b}; pairs = [(r, bi[r["year"]]) for r in a if r["year"] in bi]
else:
    pairs = list(zip(a, b))
n = len(pairs); diff = 0; first = None; keys = set()
for ra, rb in pairs:
    ks = (set(ra) & set(rb)) - skip; keys |= ks
    d = [k for k in ks if ra[k] != rb[k]]
    if d:
        diff += 1; first = first or (ra["year"], d[:5])
only_a = set(a[0]) - set(b[0]); only_b = set(b[0]) - set(a[0])
span = f", years {pairs[0][0]['year']}-{pairs[-1][0]['year']}" if by_year and pairs else ""
print(f"{n} records compared ({len(a)} vs {len(b)}){span}, {len(keys)} shared keys, {diff} differ, first {first}; only in A {sorted(only_a)}, only in B {sorted(only_b)}")
# gene histograms (2026-11-24): hist and histHerd rows paired by histYears, over the years both runs recorded
A = json.load(open(args[0])); B = json.load(open(args[1]))
if "histYears" in A and "histYears" in B:
    ib = {y: k for k, y in enumerate(B["histYears"])}
    common = [(ka, ib[y]) for ka, y in enumerate(A["histYears"]) if y in ib]
    for part in ("hist", "histHerd"):
        traits = sorted(set(A[part]) & set(B[part]))
        d = sum(1 for ka, kb in common if any(A[part][t][ka] != B[part][t][kb] for t in traits))
        yrs = f"years {A['histYears'][common[0][0]]}-{A['histYears'][common[-1][0]]}" if common else "no common years"
        print(f"{part}: {len(common)} rows compared ({yrs}), {len(traits)} traits, {d} differ")
