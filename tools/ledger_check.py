# ledger_check.py: does the herd ledger (logLedger, World.newLedger) close? (steward, 2026-11-24, for exp020's probe)
#   python tools/ledger_check.py FILE.json [--bad died|walk|bornW]
# Needs annual year rows (recordEvery 1). For each camp and each pair of consecutive years Y-1, Y, by origin pooled:
#   stock(Y) - stock(Y-1) = ins(Y) - outs(Y), in goats (exact) and in summed R (to rounding, tolerance 1e-3).
# Ins: cap, born, bornW, exIn; outs: lostRun, lostNight, culled, died, exOut. Origin moves (a captive's kid is herd-born,
# but the captive stays captured) do not cross within a goat, so the identity holds per origin as well, and is checked so.
# Then the ledger summed over camps against the year row's own counters (each must be equal): cap = captured, born +
# bornW = herdBirths, lostRun = runOffLost, lostRun + lostNight = escaped, spooked = spooked, caught = alarmCaught,
# ranOff = ranOff, rejoined = rejoined, refetched = refetched, stock goats = herded, exIn = exOut = exchanged.
# --bad shows each check can fail (each must then FAIL): died drops the 'died' channel (the closure); walk adds one
# walking goat-day to the first ledger row (walk = density.c[1].n); bornW moves one birth from born to bornW in the first
# row with a herd birth (bornW against wildSiredShare).
import json, sys

INS = ["cap", "born", "bornW", "exIn"]; OUTS = ["lostRun", "lostNight", "culled", "died", "exOut"]

def main():
    f = sys.argv[1]; bad = sys.argv[sys.argv.index("--bad") + 1] if "--bad" in sys.argv else None
    if bad not in (None, "died", "walk", "bornW"): print("--bad wants died, walk or bornW"); sys.exit(2)
    d = json.load(open(f, encoding="utf-8")); ys = [y for y in d["years"] if "ledger" in y]
    outs = [k for k in OUTS if not (bad == "died" and k == "died")]
    if bad == "walk" and ys: ys[0]["ledger"][0]["day"]["walk"][0][0] += 1
    if bad == "bornW":
        y = next(y for y in ys if y["herdBirths"] and y["herdBirths"] > 4 * sum(L["flow"]["bornW"][o][0] for L in y["ledger"] for o in (0, 1)))
        L = next(L for L in y["ledger"] if L["flow"]["born"][1][0]); L["flow"]["born"][1][0] -= 1; L["flow"]["bornW"][1][0] += 1
    if len(ys) < 2: print(f"{f}: fewer than 2 rows with a ledger"); sys.exit(1)
    if any(b["year"] - a["year"] != 1 for a, b in zip(ys, ys[1:])): print("rows are not annual (recordEvery must be 1)"); sys.exit(1)
    nbad_n = nbad_r = 0; worst = 0.0; first = None; pairs = 0
    for a, b in zip(ys, ys[1:]):
        for c, (La, Lb) in enumerate(zip(a["ledger"], b["ledger"])):
            for o in (0, 1):
                dn = Lb["stock"][o][0] - La["stock"][o][0]; dr = Lb["stock"][o][1] - La["stock"][o][1]
                fn = sum(Lb["flow"][k][o][0] for k in INS) - sum(Lb["flow"][k][o][0] for k in outs)
                fr = sum(Lb["flow"][k][o][1] for k in INS) - sum(Lb["flow"][k][o][1] for k in outs)
                pairs += 1
                if dn != fn: nbad_n += 1; first = first or (b["year"], c, o, "goats", dn, fn)
                e = abs(dr - fr); worst = max(worst, e)
                if e > 1e-3: nbad_r += 1; first = first or (b["year"], c, o, "R", round(dr, 4), round(fr, 4))
    print(f"{f}: {len(ys)} annual rows {ys[0]['year']}-{ys[-1]['year']}, {pairs} camp-origin-year pairs; goats differ {nbad_n}, "
          f"summed R differs (> 1e-3) {nbad_r}, largest R gap {worst:.5f}; first {first}" + (f"  [--bad {bad}]" if bad else ""))
    S = lambda y, part, k, i=0: sum(L[part][k][o][i] for L in y["ledger"] for o in (0, 1))
    checks = [("cap = captured", lambda y: S(y, "flow", "cap"), lambda y: y["captured"]),
              ("born + bornW = herdBirths", lambda y: S(y, "flow", "born") + S(y, "flow", "bornW"), lambda y: y["herdBirths"]),
              ("lostRun = runOffLost", lambda y: S(y, "flow", "lostRun"), lambda y: y["runOffLost"]),
              ("lostRun + lostNight = escaped", lambda y: S(y, "flow", "lostRun") + S(y, "flow", "lostNight"), lambda y: y["escaped"]),
              ("spooked", lambda y: S(y, "ev", "spooked"), lambda y: y["spooked"]),
              ("caught = alarmCaught", lambda y: S(y, "ev", "caught"), lambda y: y["alarmCaught"]),
              ("ranOff", lambda y: S(y, "ev", "ranOff"), lambda y: y["ranOff"]),
              ("rejoined", lambda y: S(y, "ev", "rejoined"), lambda y: y["rejoined"]),
              ("refetched", lambda y: S(y, "ev", "refetched"), lambda y: y["refetched"]),
              ("stock goats = herded", lambda y: sum(L["stock"][o][0] for L in y["ledger"] for o in (0, 1)), lambda y: y["herded"]),
              ("exIn = exchanged", lambda y: S(y, "flow", "exIn"), lambda y: y["exchanged"]),
              ("exOut = exchanged", lambda y: S(y, "flow", "exOut"), lambda y: y["exchanged"])]
    # the midday block (2026-11-24, the reviewer's exp020 point 5): walking goat-days = density's with-herder samples, taken
    # at the same sub-tick by the same walksWithHerder test; bornW against wildSiredShare x herdBirths (the row rounds the
    # share to 3 places, so equal within 0.0005 x herdBirths + 0.5)
    D = lambda part, c: (lambda y: sum(L["day"][part][o][0] for L in y["ledger"] for o in (0, 1)) if part != "other" else sum(L["day"]["other"][o] for L in y["ledger"] for o in (0, 1)))
    dens = lambda c: (lambda y: (y.get("density") or {}).get("c", [None] * 4)[c]["n"] if (y.get("density") or {}).get("c", [None] * 4)[c] else 0)
    checks.append(("walk goat-days = density.c[1].n", D("walk", 1), dens(1)))
    fails = 0
    bw = [y for y in ys if y["herdBirths"] and abs(S(y, "flow", "bornW") - (y["wildSiredShare"] or 0) * y["herdBirths"]) > 0.0005 * y["herdBirths"] + 0.5]
    print(f"  {'bornW = wildSiredShare x births':<30} rows differing {len(bw):>5}  (ledger total {sum(S(y, 'flow', 'bornW') for y in ys)})"); fails += len(bw) > 0
    for part, c in (("kept", 2), ("other", 3)):                  # printed, not failed: the ledger skips camps with no herder
        dd = [D(part, c)(y) - dens(c)(y) for y in ys]
        print(f"  {part} goat-days - density.c[{c}].n: rows differing {sum(1 for v in dd if v):>5}, total difference {sum(dd)} (camps with no herder are not sampled)")
    for name, L, R in checks:
        n = sum(1 for y in ys if L(y) != R(y)); fails += n > 0
        tot = sum(L(y) for y in ys)
        print(f"  {name:<30} rows differing {n:>5}  (ledger total {tot})")
    ok = nbad_n == 0 and nbad_r == 0 and fails == 0
    print("PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)

main()
