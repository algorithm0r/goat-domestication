# runio.py: shared reading helpers for run files, old (results/<name>/*.json, from runyears' legacy mode) and new
# (results/expNNN_slug/<run>.json, the db.js v2 JSON copy). 2026-11-18.
#   hist_rows(d, y0, y1): indices of the gene-histogram rows whose year lies in y0..y1 (0-based year records). Old runs
#   have a row every year (row i = year i); experiment runs may thin them (histPeriod) and list each row's year in
#   histYears.
#   params(d): the run's PARAMETERS (old files: "params"; db.js v2 copies: "_parameters").
def hist_rows(d, y0, y1):
    ys = d.get("histYears")
    if ys is None: return [y for y in range(y0, y1 + 1) if y < len(d["hist"]["R"])]
    return [i for i, y in enumerate(ys) if y0 <= y <= y1]

def params(d):
    return d.get("params") or d.get("_parameters") or {}
