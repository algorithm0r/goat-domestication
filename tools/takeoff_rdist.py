# takeoff_rdist.py: the herd's genotype distribution of one trait over time, one panel per run, each aligned on its own
# jump year J (the take-off analysis's definition: tools/jump_tab.py, the first year after 500 whose 100-year trailing
# mean herd reaches 100 and holds 400 years; as tools/takeoff_tab.py). Steward, 2026-11-22, for Chris ("the R
# distribution for herd goats in REF lined up by jump year ... each seed in its own plot"). Descriptive; no measure.
#   python tools/takeoff_rdist.py OUT.png [trait=R] [x0=-600] [x1=900] FILE.json [FILE.json ...]
# Colour: share of the herd's goats in each of the 20 genotype buckets, per histogram row (each column sums to 1; grey
# where the herd has no goats). Orange line: the wild's mean genotype (hist - histHerd). Grey line: J. Also prints, per
# run, J and the herd size at the first and last plotted rows.
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jump_tab
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

SEQ = ["#ffffff", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]   # dataviz sequential blue
WILD, INK, MUTED = "#eb6834", "#222222", "#888888"
NAMES = dict(R="Reactivity", A="Aggression", S="Gregariousness", B="Body size", H="Horn size", T="Season breadth",
             M="Milk yield", W="Pigmentation", L="Twinning", C="Coat marking (neutral)")

def jump_year(d):
    hs = [r for r in jump_tab.herd_series(d, 100) if r[0] > 500]
    return jump_tab.jump(hs, lambda v: v >= 100, 400)[0]

def series(d, trait):
    ys = d.get("histYears") or list(range(len(d["hist"][trait])))
    out = []
    for i, y in enumerate(ys):
        a, h = d["hist"][trait][i], d["histHerd"][trait][i]
        w = [x - z for x, z in zip(a, h)]; nw = sum(w); nh = sum(h)
        wm = sum((k + 0.5) / 20 * v for k, v in enumerate(w)) / nw if nw else None
        out.append((y + 1, h, nh, wm))                          # 1-based year, herd counts, herd n, wild mean
    return out

def main():
    args = sys.argv[1:]; out = args[0]
    opt = dict(a.split("=", 1) for a in args[1:] if "=" in a); files = [a for a in args[1:] if "=" not in a]
    trait = opt.get("trait", "R"); x0, x1 = int(opt.get("x0", -600)), int(opt.get("x1", 900))
    cmap = LinearSegmentedColormap.from_list("seq", SEQ)
    n = len(files); cols = 2; rws = (n + 1) // 2
    fig, axs = plt.subplots(rws, cols, figsize=(11, 2.3 * rws + 0.8), sharex=True, sharey=True, squeeze=False)
    im = None
    for i, f in enumerate(files):
        d = json.load(open(f, encoding="utf-8")); J = jump_year(d); ax = axs[i // cols][i % cols]
        name = os.path.basename(f).replace(".json", "")
        if J is None:
            ax.text(0.5, 0.5, f"{name}: no jump", transform=ax.transAxes, ha="center", color=MUTED); continue
        S = [s for s in series(d, trait) if x0 <= s[0] - J <= x1]
        xs = np.array([s[0] - J for s in S], float)
        Z = np.full((20, len(S)), np.nan)
        for j, (_, h, nh, _) in enumerate(S):
            if nh: Z[:, j] = np.array(h, float) / nh
        step = np.median(np.diff(xs)) if len(xs) > 1 else 15
        edges = np.concatenate([xs - step / 2, [xs[-1] + step / 2]])
        ax.set_facecolor("#e6e6e6")                             # no herd (NaN columns) shows grey, not white
        im = ax.pcolormesh(edges, np.linspace(0, 1, 21), Z, cmap=cmap, vmin=0, vmax=0.5, shading="flat")
        wm = [(s[0] - J, s[3]) for s in S if s[3] is not None]
        ax.plot([a for a, _ in wm], [b for _, b in wm], color=WILD, lw=2, label="wild mean")
        ax.axvline(0, color=MUTED, lw=1)
        ax.set_title(f"{name}  (jump year {J})", loc="left", fontsize=9, color=INK, pad=3)
        ax.set_ylim(0, 1); ax.set_xlim(x0, x1)
        for s in ("top", "right"): ax.spines[s].set_visible(False)
        for s in ("left", "bottom"): ax.spines[s].set_color("#bbbbbb")
        ax.tick_params(colors="#555555", labelsize=8)
        first = next((s for s in S if s[2]), None)
        print(f"{name}: J {J}; first herd row {first[0] - J if first else None} y from J (n {first[2] if first else 0}); "
              f"last row {S[-1][0] - J} (n {S[-1][2]})")
    for ax in axs[-1]: ax.set_xlabel("years from the jump year", fontsize=9, color="#444444")
    for r in axs: r[0].set_ylabel(f"herd {trait} genotype", fontsize=9, color="#444444")
    h, l = axs[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper right", frameon=False, fontsize=9, bbox_to_anchor=(0.99, 0.995))
    fig.suptitle(f"{NAMES.get(trait, trait)}: herd goats' genotype distribution, each run aligned on its jump year "
                 f"(colour = share of the herd in each bucket; grey = no herd yet)", fontsize=10, x=0.01, ha="left", y=0.995)
    fig.tight_layout(rect=(0, 0, 0.92, 0.975))
    cax = fig.add_axes([0.935, 0.12, 0.012, 0.76]); cb = fig.colorbar(im, cax=cax)
    cb.set_label("share of herd goats (capped at 0.5)", fontsize=8, color="#444444"); cb.ax.tick_params(labelsize=7)
    fig.savefig(out, dpi=150); print(f"wrote {out}")

main()
