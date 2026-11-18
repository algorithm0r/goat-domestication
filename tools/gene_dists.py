# gene_dists.py: wild and herd genotype distributions of every trait, side by side for two or more arms.
#   python tools/gene_dists.py Y0 Y1 OUT.png LABEL=GLOB [LABEL=GLOB ...]
# Pools the 20-bucket histograms (hist = all goats, histHerd = herd; wild = hist - histHerd) over years Y0..Y1
# (1-based: 1501-1600 = year records 1500..1599) and over the arm's seeds; plots each population as a share of
# its own goats, so a small herd and a large wild population sit on one scale. Prints mean, sd, gap and overlap.
import glob, json, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TRAITS = "R A S B H T M W L C".split()
NAMES = dict(R="Reactivity", A="Aggression", S="Gregariousness", B="Body size", H="Horn size",
             T="Season breadth", M="Milk yield", W="Pigmentation", L="Twinning", C="Coat marking (neutral)")
WILD, HERD = "#2a78d6", "#eb6834"   # dataviz reference palette, categorical slots 1 and 2 (validated pair)

def pooled(pat, y0, y1):
    files = sorted(glob.glob(pat))
    if not files: sys.exit(f"no files for {pat}")
    W = {t: [0] * 20 for t in TRAITS}; H = {t: [0] * 20 for t in TRAITS}
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        for y in range(y0 - 1, y1):
            for t in TRAITS:
                a, h = d["hist"][t][y], d["histHerd"][t][y]
                for k in range(20): W[t][k] += a[k] - h[k]; H[t][k] += h[k]
    return len(files), W, H

def stats(c):
    n = sum(c); xs = [(k + 0.5) / 20 for k in range(20)]
    m = sum(x * v for x, v in zip(xs, c)) / n
    return m, (sum((x - m) ** 2 * v for x, v in zip(xs, c)) / n) ** 0.5

def main():
    y0, y1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    arms = [(a.split("=", 1)[0],) + pooled(a.split("=", 1)[1], y0, y1) for a in sys.argv[4:]]
    fig, axs = plt.subplots(len(TRAITS), len(arms), figsize=(4.2 * len(arms), 1.55 * len(TRAITS)), sharex=True, squeeze=False)
    xs = [k / 20 for k in range(20)]
    print(f"years {y0}-{y1}; mean (sd) of genotype, gap = herd - wild, overlap = shared area of the two share histograms")
    for j, (label, n, W, H) in enumerate(arms):
        print(f"== {label}: {n} seeds")
        for i, t in enumerate(TRAITS):
            ax = axs[i][j]; w = [v / sum(W[t]) for v in W[t]]; h = [v / sum(H[t]) for v in H[t]]
            ax.bar(xs, w, width=0.05, align="edge", color=WILD, alpha=0.45, linewidth=0)
            ax.step(xs + [1], w + [w[-1]], where="post", color=WILD, lw=1.6, label="wild")
            ax.step(xs + [1], h + [h[-1]], where="post", color=HERD, lw=2, label="herd")
            (mw, sw), (mh, sh) = stats(W[t]), stats(H[t]); ov = sum(min(a, b) for a, b in zip(w, h))
            print(f"   {t} {NAMES[t]:<24} wild {mw:.3f} ({sw:.3f})  herd {mh:.3f} ({sh:.3f})  gap {mh - mw:+.3f}  overlap {ov:.2f}")
            ax.set_title(f"{t}  {NAMES[t]}", loc="left", fontsize=8.5, color="#222", pad=2)
            ax.set_title(f"gap {mh - mw:+.2f}", loc="right", fontsize=8.5, color="#444", pad=2)
            ax.set_yticks([]); ax.set_xlim(0, 1)
            for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
            ax.spines["bottom"].set_color("#999")
    for j, (label, *_rest) in enumerate(arms):
        fig.text((j + 0.5) / len(arms), 0.968, label, ha="center", fontsize=10.5, weight="bold")
    h0, l0 = axs[0][0].get_legend_handles_labels(); fig.legend(h0, l0, loc="upper right", ncol=2, fontsize=8.5, frameon=False, bbox_to_anchor=(0.99, 0.995))
    for ax in axs[-1]: ax.set_xlabel("genotype value", fontsize=8.5)
    fig.suptitle(f"Genotypes, years {y0}-{y1}, pooled over seeds; each population as a share of itself", fontsize=9.5, x=0.01, ha="left", y=0.993)
    fig.tight_layout(rect=(0, 0, 1, 0.962)); fig.savefig(out, dpi=150)
    print(f"wrote {out}")

main()
