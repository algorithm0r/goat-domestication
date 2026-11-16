#!/usr/bin/env bash
# publish_public.sh: sync the public repo (github.com/algorithm0r/goat-domestication, served by GitHub Pages) with this
# checkout's HEAD, leaving out paper/ (the unsubmitted manuscript). The public repo has its own history, one commit per
# publish; its working copy is ../../sim-public (next to sim/).
#   bash tools/publish_public.sh "message"
set -euo pipefail
SIM="$(cd "$(dirname "$0")/.." && pwd)"
PUB="$SIM/../sim-public"
MSG="${1:-Sync from the working repo}"
EXCLUDE=(paper)
[ -d "$PUB/.git" ] || { echo "no public clone at $PUB"; exit 1; }
cd "$PUB"
git pull -q --ff-only </dev/null || true
# replace the tracked tree with HEAD of the working repo, minus the excluded paths
git ls-files -z </dev/null | xargs -0 -r rm -f
(cd "$SIM" && git archive --format=tar HEAD </dev/null) | tar -x -f - -C "$PUB"
for p in "${EXCLUDE[@]}"; do rm -rf "$PUB/$p"; done
touch "$PUB/.nojekyll"                      # serve every file as is (no Jekyll processing)
SRC=$(cd "$SIM" && git rev-parse --short HEAD </dev/null)
git add -A </dev/null
if git diff --cached --quiet </dev/null; then echo "nothing to publish"; exit 0; fi
git commit -q -m "$MSG (working repo $SRC, without paper/)" </dev/null
git push -q origin main </dev/null
git log --oneline -1 </dev/null
