# takeoff_plot.py: the aligned take-off trajectories from tools/takeoff_tab.py --out FILE.json, one panel per variable
# (herd size, herd R, breeding does, captured-sire share, loss rate), one line per run, years relative to its jump year J,
# each run's departure year marked. Analysis session, 2026-11-22. Draws only what takeoff_tab computed.
#   python tools/takeoff_plot.py FILE.json OUT.png [TITLE]
import json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LABELS = [("size", "herd size (goats)"), ("R", "herd mean R"), ("does", "breeding does"),
          ("csire", "captured-sire share of conceptions"), ("loss", "goats lost per herd goat-year")]

def main():
    src, out = sys.argv[1], sys.argv[2]; title = sys.argv[3] if len(sys.argv) > 3 else "Take-off, aligned on the jump year"
    runs = json.load(open(src, encoding="utf-8"))
    fig, axes = plt.subplots(len(LABELS), 1, figsize=(8, 13), sharex=True)
    cmap = plt.get_cmap("tab10")
    for k, (var, lab) in enumerate(LABELS):
        ax = axes[k]
        for i, r in enumerate(runs):
            pts = [(p["t"], p[var]) for p in r["traj"] if p[var] is not None]
            if not pts: continue
            ax.plot([t for t, _ in pts], [v for _, v in pts], color=cmap(i % 10), lw=1.1, label=r["run"] if k == 0 else None)
            dep = r["dep"].get(var)
            if dep is not None: ax.axvline(dep - r["J"], color=cmap(i % 10), lw=0.8, ls=":")
        ax.axvline(0, color="black", lw=0.8); ax.axvspan(-600, -301, color="0.92", zorder=0)
        ax.set_ylabel(lab, fontsize=9)
        if var == "size": ax.set_yscale("log")
    axes[-1].set_xlabel("years from the jump year J (grey: the plateau the departure is measured against; dotted: departure)")
    axes[0].legend(fontsize=7, ncol=4, loc="upper left"); fig.suptitle(title, fontsize=11)
    fig.tight_layout(); fig.savefig(out, dpi=130); print(f"wrote {out}")
    # the plotted values at J-300, J and J+300 (the reviewer's 9a18d2e: figures quoted from the plot come from here): per
    # run the smoothed point nearest each time (within 3 years), then the mean over runs that have it
    print("smoothed values at J-300 / J / J+300, mean over runs (n):")
    for var, lab in LABELS:
        cells = []
        for T in (-300, 0, 300):
            vs = []
            for r in runs:
                near = [p for p in r["traj"] if abs(p["t"] - T) <= 3 and p[var] is not None]
                if near: vs.append(min(near, key=lambda p: abs(p["t"] - T))[var])
            cells.append(f"{sum(vs) / len(vs):.3f} ({len(vs)})" if vs else "- (0)")
        print(f"  {var}: " + " / ".join(cells))

if __name__ == "__main__": main()
