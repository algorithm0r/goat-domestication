# perseed_tab.py: per seed, R gap / herd in fixed blocks of years, to see when a herd "jumps" (2026-11-20; the exp006 per-seed
# table in EXPLOG was made by this code, then inline).
#   python tools/perseed_tab.py ARM[,ARM...] DIR[;DIR...] [BLOCK] [YEARS]
# Gaps and herd as settle_tab (gaps(), herd()). BLOCK years per cell (default 400), over 1..YEARS (default 4000).
import glob, json, os, re, sys
_here = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(_here, "settle_tab.py"), encoding="utf-8").read().replace("\nmain()\n", "\n")
_ns = {"__file__": os.path.join(_here, "settle_tab.py")}; exec(_src, _ns)
gaps, herd = _ns["gaps"], _ns["herd"]

def main():
    arms, folders = sys.argv[1].split(","), sys.argv[2].split(";")
    block = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    years = int(sys.argv[4]) if len(sys.argv) > 4 else 4000
    print(f"R gap / herd per {block}-year block, years 1-{years}")
    for a in arms:
        fs = [f for d in folders for f in glob.glob(os.path.join(d, f"{a}_seed*.json"))]
        fs.sort(key=lambda f: int(re.search(r"_seed(\d+)\.json$", f).group(1)))
        print(a)
        for f in fs:
            d = json.load(open(f, encoding="utf-8")); s = re.search(r"_seed(\d+)\.json$", f).group(1)
            cells = []
            for y0 in range(1, years + 1, block):
                g = gaps(d, y0, y0 + block - 1)
                cells.append(f"{(g or {'R': 0})['R']:+.2f}/{herd(d, y0, y0 + block - 1):.0f}")
            print(f"  s{s}: " + " ".join(cells))

main()
