# loadrun.py: read any run file (old plain .json, compact .json.gz from runyears, or gzipped plain JSON) as the OLD plain
# dict, exactly what json.load of the plain file gives: same values, same key order, absent keys absent.
# The format is described in runformat.mjs; this is its decoder, kept in step with decodeValue/decodeCol there.
#   from loadrun import load_run          (with tools/ on sys.path)
#   run = load_run("results/offtake/R15_seed1.json.gz");  run["years"][0]["killoff"] ...
#   python tools/loadrun.py <file>        prints a summary
import gzip, json, sys

FORMAT = "adcol1"
_ABSENT = object()   # an absent key inside a record column


def _unrle(r):
    out, cur = [], True
    for n in r:
        out.extend([cur] * n)
        cur = not cur
    return out


def _reshape(flat, shape):
    pos = 0

    def build(d):
        nonlocal pos
        if d == len(shape) - 1:
            out = flat[pos:pos + shape[d]]
            pos += shape[d]
            return out
        return [build(d + 1) for _ in range(shape[d])]
    return build(0)


def _value(x):
    if not isinstance(x, dict):
        return x
    t = x["t"]
    if t == "F":
        return _reshape(x["v"], x["s"])
    if t == "L":
        return _col(x["c"], x["n"])
    if t == "O":
        return {k: _value(v) for k, v in zip(x["k"], x["v"])}
    raise ValueError(f"loadrun: unknown value tag {t}")


def _col(c, n):
    if isinstance(c, list):
        return c
    t = c["t"]
    if t == "F":
        return _reshape(c["v"], c["s"])
    if t in ("A", "N"):
        has = _unrle(c["r"])
        inner = iter(_col(c["c"], sum(has)))
        gap = _ABSENT if t == "A" else None
        return [next(inner) if h else gap for h in has]
    if t == "R":
        cols = [_col(cc, n) for cc in c["c"]]
        keys = c["k"]
        return [{k: col[r] for k, col in zip(keys, cols) if col[r] is not _ABSENT} for r in range(n)]
    if t == "M":
        vals = _col(c["c"], sum(c["n"]))
        keys, idx, out, p = c["k"], c["i"], [], 0
        for m in c["n"]:
            out.append({keys[idx[j]]: vals[j] for j in range(p, p + m)})
            p += m
        return out
    if t == "V":
        vals = _col(c["c"], sum(c["n"]))
        out, p = [], 0
        for m in c["n"]:
            out.append(vals[p:p + m])
            p += m
        return out
    if t == "X":
        return [_value(v) for v in c["v"]]
    raise ValueError(f"loadrun: unknown column tag {t}")


def unpack_run(f):
    """The plain run dict from a parsed file; a plain (old) run is returned as it is."""
    if isinstance(f, dict) and f.get("format") == FORMAT and "data" in f:
        return _value(f["data"])
    return f


def load_run(path):
    """Read a run file in any format as the old plain dict."""
    with open(path, "rb") as fh:
        raw = fh.read()
    if raw[:2] == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return unpack_run(json.loads(raw.decode("utf-8")))


# Years of the gene histograms (2026-11-13). Runs may record them every histPeriod years, and the census every
# reportingPeriod days, so index them by year, never by position. Census rows (samples) carry tick, year and day.
def hist_years(run):
    """Year of each row of run["hist"] / run["histHerd"]: run["histYears"] when the run has it; older runs recorded one
    row at every year end, so the years of run["years"] (checked on 40 saved runs: rows = year records, year = index)."""
    return run["histYears"] if "histYears" in run else [r["year"] for r in run["years"]]


def hist_index(run):
    """dict year -> row of run["hist"] / run["histHerd"], for the years that were recorded."""
    return {y: i for i, y in enumerate(hist_years(run))}


def depth_years(run):
    """Last year of each run["histDepth"] record (each covers histDepth["every"] years ending there)."""
    D = run.get("histDepth")
    if not D:
        return []
    if "years" in D:
        return D["years"]
    first = next(iter(D.get("herd", {}).values()), [])
    return [(k + 1) * D["every"] - 1 for k in range(len(first))]


if __name__ == "__main__":
    r = load_run(sys.argv[1])
    print(f"{sys.argv[1]}: {len(r['years'])} years, {len(r['samples'])} samples, "
          f"year keys: {len(r['years'][-1]) if r['years'] else 0}, extinct {r['extinct']}")
