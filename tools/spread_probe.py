# spread_probe.py: how far a herder spook spreads under alarmSpread, by herd size (steward, 2026-11-23, for the
# alarm-spreading experiment's calibration; Chris: "the alarm should spread faster in denser herds"). Descriptive.
#   python tools/spread_probe.py [Y0-Y1] FILE.json [FILE.json ...]
# Reads each recorded year row from herding on (or Y0-Y1): herded (herd goats), spooked (goats the herder spooked),
# alarmCaught (goats that caught a spread alarm), ranOff. Rows are binned by herd size; per bin, summed over the rows:
#   bolts per spook = (spooked + alarmCaught) / spooked   (the cascade size: 1 = no spread)
#   bolts per herd goat-year = (spooked + alarmCaught) / herded, and run-offs per herd goat-year = ranOff / herded.
import json, os, sys

BINS = [(1, 9), (10, 29), (30, 99), (100, 199), (200, 10 ** 9)]

def main():
    args = sys.argv[1:]
    y0 = y1 = None
    if args and "-" in args[0] and not args[0].endswith(".json"):
        y0, y1 = map(int, args[0].split("-")); args = args[1:]
    for f in args:
        d = json.load(open(f, encoding="utf-8")); P = d["_parameters"]; H0 = int(P["herdingAt"])
        lo, hi = (y0, y1) if y0 is not None else (H0 + 1, 10 ** 9)
        rows = [r for r in d["years"] if lo <= r["year"] + 1 <= hi]
        if rows and "alarmCaught" not in rows[0]:
            print(f"{os.path.basename(f)}: no alarmCaught counter (run before c364a5f)"); continue
        print(f"{os.path.basename(f)}: alarmSpread {P.get('alarmSpread', 0)} minLoad {P.get('minLoad')} rows {len(rows)} ({lo}-{min(hi, rows[-1]['year'] + 1) if rows else hi})")
        print("  herd     rows  spooked  caught  bolts/spook  bolts/goat-yr  runoffs/goat-yr")
        for a, b in BINS:
            rs = [r for r in rows if a <= (r.get("herded") or 0) <= b]
            if not rs: continue
            sp = sum(r["spooked"] for r in rs); ca = sum(r["alarmCaught"] for r in rs)
            hd = sum(r["herded"] for r in rs); ro = sum(r.get("ranOff") or 0 for r in rs)
            bps = f"{(sp + ca) / sp:.2f}" if sp else "-"
            print(f"  {a:>3}-{'' if b > 10 ** 8 else b:<4} {len(rs):>5} {sp:>8} {ca:>7} {bps:>12} {(sp + ca) / hd:>14.3f} {ro / hd:>16.3f}")

main()
