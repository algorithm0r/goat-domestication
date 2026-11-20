# Review of the author's responses to the design review (2026-11-20)

On outline.md "Design review 2026-11-20" and the draft.tex diff, both in commit 4ebc8ac. The responses to findings 1, 3,
4 and 10-20 do what the findings asked. I accept the qualification on finding 2: the herd failing to follow the wild is
an effect of isolation, but only herd change counts as a syndrome. Three points remain.

### A. The abstract still makes both claims the review withdrew (major)
draft.tex 35: "the divergence tracks the depth of the herd's own lineage measured in generations since the wild". The
only evidence for this is the depth-R correlation (r = -0.87 / -0.89). The author now flags that correlation in the
Discussion table as set by the spook rule (finding 1). draft.tex 36: "breeding the herd from its deepest lineage ...
moves most of the traits we measure". Under the author's own qualification, "moves" is not yet shown: the deep arm's
A, S, H and W gaps may be wild change. Neither sentence has a \todo. The Discussion sentence at 724 has one, and the
abstract is the more prominent of the two. **Fix:** put a \todo on both abstract sentences that points to findings 1 and 2,
or reword them to what is shown now ("herds bred from their deepest lineage end furthest from the wild").

### B. Herding from year 1600 removes only one of three sources of wild change (minor)
The outline's design note: "on the new base Wild Type I has settled by 1401-1600 ... so herding from about 1600 would
take most of the wild drift out of the gaps." The settling evidence is from WT, which has no humans: "WT (no humans)
whole-population means, 1401-1600 / 3201-4000" (EXPLOG 3471, run-length pilot). In every herding run humans
hunt from year 300, and hunting moves the wild by itself: R rises from about 0.62 to about 0.86 (MODEL.md 526). The wild
also takes in escaped herd goats once herding starts (finding 10c). A later herding start reduces wolf-only drift. It
leaves the hunting response and the feral inflow in place, and it changes the founders. The herd-change/wild-change
split is still needed whatever the start year. Starting later is a choice for the steward, and if made it should be
reported with the year-400 runs beside it.

### C. Restricting Fig. 5B to established herds leaves herd size as a confounder (minor)
Among established herds, herd size runs from about 110 (noProv) to about 500 (noPen) (EXPLOG 5285-5294). The R filter
scales with it (finding 1), and so do drift and the keep value's camp records (finding 5). So co-change across
established cells can still come from shared herd size. **Fix:** give the independence null within established herds
with herd size as a covariate, or within herd-size strata.
