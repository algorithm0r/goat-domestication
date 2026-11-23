# herd_time.py: herd size over time, one panel per run, aligned on the start of herding (herdingAt), in the same
# 2-column grid as tools/takeoff_rdist.py so the two figures can be read side by side. Steward, 2026-11-22, for Chris
# ("what were the herd sizes for those runs?", after takeoff_rdist's LOAD1 against REF). Descriptive; no measure.
#   python tools/herd_time.py OUT.png [x0=-100] [x1=3600] FILE.json [FILE.json ...]
# Grey: herd goats in each recorded year row (herded). Dark line: its 100-year trailing mean (tools/jump_tab.py's
# herd_series). Dashed line at 100: the jump criterion's level; grey vertical line: J (jump_tab's definition, as in
# takeoff_rdist.py), where there is one. Log scale, herd counts plus 1. Files fill the grid in the order given.
# Prints, per run: J (years since herding), the median herd over recorded rows before J (from herding on), and the
# mean herd over 3201-4000.
import json, os, sys, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jump_tab
import matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

INK, MUTED, LINE = "#222222", "#888888", "#184f95"

def main():
    args = sys.argv[1:]; out = args[0]
    opt = dict(a.split("=", 1) for a in args[1:] if "=" in a); files = [a for a in args[1:] if "=" not in a]
    x0, x1 = int(opt.get("x0", -100)), int(opt.get("x1", 3600))
    n = len(files); cols = 2; rws = (n + 1) // 2
    fig, axs = plt.subplots(rws, cols, figsize=(11, 1.9 * rws + 0.8), sharex=True, sharey=True, squeeze=False)
    for i, f in enumerate(files):
        d = json.load(open(f, encoding="utf-8")); ax = axs[i // cols][i % cols]
        name = os.path.basename(f).replace(".json", ""); H0 = int(d["_parameters"]["herdingAt"])
        hs = jump_tab.herd_series(d, 100)
        J = jump_tab.jump([r for r in hs if r[0] > 500], lambda v: v >= 100, 400)[0]
        S = [(y - H0, m, h) for y, m, h in hs if x0 <= y - H0 <= x1]
        ax.plot([s[0] for s in S], [s[2] + 1 for s in S], color="#bbbbbb", lw=0.6)
        ax.plot([s[0] for s in S], [s[1] + 1 for s in S], color=LINE, lw=1.8)
        ax.axhline(101, color=MUTED, lw=0.8, ls="--")
        if J is not None: ax.axvline(J - H0, color=MUTED, lw=1)
        ax.set_yscale("log"); ax.set_ylim(1, 1000); ax.set_xlim(x0, x1)
        ax.set_title(f"{name}  (" + (f"jump at {J - H0} y of herding" if J else "no jump") + ")", loc="left", fontsize=9, color=INK, pad=3)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        for s in ("left", "bottom"): ax.spines[s].set_color("#bbbbbb")
        ax.tick_params(colors="#555555", labelsize=8)
        pre = [h for y, m, h in hs if H0 < y < (J or 10 ** 9)]
        win = [h for y, m, h in hs if 3201 <= y <= 4000]
        print(f"{name}: J {J - H0 if J else None} y of herding; median herd before J {statistics.median(pre) if pre else None}; "
              f"mean herd 3201-4000 {sum(win) / len(win):.1f}" if win else f"{name}: no window rows")
    for ax in axs[-1]: ax.set_xlabel("years since herding began", fontsize=9, color="#444444")
    for r in axs: r[0].set_ylabel("herd goats + 1 (log)", fontsize=9, color="#444444")
    fig.suptitle("Herd size over time (grey: each recorded year; blue: 100-year trailing mean; dashed: 100 goats; "
                 "vertical: jump year)", fontsize=10, x=0.01, ha="left", y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.975)); fig.savefig(out, dpi=150); print(f"wrote {out}")

main()
