# cmp_years.py A.json B.json [skip,keys]: count year records that differ between two runs (identity checks).
# (moved from the session scratchpad 2026-11-18; EXPLOG "scratchpad cmp_years.py" means this file)
import json, sys
a = json.load(open(sys.argv[1]))["years"]; b = json.load(open(sys.argv[2]))["years"]
skip = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()
n = min(len(a), len(b)); diff = 0; first = None; keys = set()
for i in range(n):
    ks = (set(a[i]) & set(b[i])) - skip; keys |= ks
    d = [k for k in ks if a[i][k] != b[i][k]]
    if d:
        diff += 1; first = first or (a[i]["year"], d[:5])
only_a = set(a[0]) - set(b[0]); only_b = set(b[0]) - set(a[0])
print(f"{n} records compared ({len(a)} vs {len(b)}), {len(keys)} shared keys, {diff} differ, first {first}; only in A {sorted(only_a)}, only in B {sorted(only_b)}")
