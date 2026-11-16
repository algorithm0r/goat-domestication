# Human economy — rough design (draft, 2026-10-23)

Working notes from the 2026-10-23 conversation with Chris. Nothing here is built yet.

## Purpose

Replace fixed human policies (hunt 30% of days, offtake 10%/y) with a camp that allocates labour by
what pays. Two questions then share one model: what lets goats change (domestication), and why a
human group would move from hunting to herding, penning, and the rest (cultural evolution of
husbandry). Human numbers stay fixed (no Lotka–Volterra); the economy is about income, not survival.

## Currency and stores

One currency, **fu**, the unit the goats already run on.

| Store | In | Out | Decay |
|---|---|---|---|
| Plant food / fodder | gatherers' cut | eaten by people (?) and fed to the herd | slow (fodder spoils, as now) |
| Meat | hunters' carcasses, slaughtered herd goats | eaten by people | **loss of nutrition, gradual, no cliff** (a lower rate can later stand for drying/preserving) |
| Herd (the stock) | captures, births, growth | slaughter, deaths, escapes | none: goats are the store that does not spoil; they eat instead |

**Herd stock value** = Σ over herd goats of edible energy, e.g. `meatYield × size` fu per goat
(meatYield to calibrate). The herd is the colony's fat: drawn on in lean times, grown in rich ones.

## The sink

Each day the camp consumes a demand **D = (people × need) + groupSink** (groupSink: the social group
beyond the labourers). Taken in order: meat store first, then slaughter from the herd (keep-value cull
rule picks who) while meat falls short. There is no shortage state: unmet demand has no consequence.
So **offtake becomes an outcome**, set by the demand, meat income, and spoilage.

## Roles and returns (per labour-day)

| Role | Return per labour-day |
|---|---|
| Gatherer | fu of fodder/plant food delivered to the store |
| Hunter | fu of meat delivered; a capture is credited with the captive's stock value (?) |
| Herder | **offtake + Δ stock value + meatDecay × stock value**, per herder-day |

Herding is measured like the others: its output relative to its effort. *Agreed with Chris
2026-10-23:* counting the stock itself as daily income would harvest every live goat every day.
Income = what is taken + the change in what is saved (offtake + Δ stock: births, growth, captures up;
deaths, escapes, weight loss down; slaughter moves value from stock to meat, so it nets to zero), plus
the storage service: holding S fu as live goats instead of meat avoids meatDecay × S fu of spoilage a
day. The weight on the stock is therefore the spoilage rate of meat, not a free knob. Prediction: lower
meat spoilage (drying, preserving) shrinks herding's storage advantage. Each return is divided by the
number doing that role that day, so per-person returns fall as more people take it up.

## Choosing a role (after Marriott & Gershenson 2011, "Polyethism in a colony of artificial ants")

- Each person chooses at dawn, on leaving camp (as their ants did).
- P(role) ∝ the role's recent return per labour-day, the camp's shared estimate, with a floor share
  for every available role so the camp keeps measuring what it is not doing (the queen's "at least
  one of each").
- Memory decays (exponential average, timescale τ of weeks), so the camp responds to grazed-out
  pasture and warier goats. τ is the key knob: short adapts fast and oscillates (their age
  polyethism), long is stable and slow (their caste polyethism).
- Returns fall with effort on their own (hunting and cutting deplete locally), so matching should
  settle near an ideal-free split rather than piling into one role.

## Staged conditions (replacing H0–H6 step by step)

| Stage | Roles available | Notes |
|---|---|---|
| E0 | gather | humans present as plant-food gatherers; the new "wild" baseline with people |
| E1 | gather, hunt | hunting turned on; labour moves as wild goats get scarce or wary |
| E2 | gather, hunt, herd | herding turned on (capture, a herder, the herd as store) |
| E3 | herding split into roles | e.g. herder, guard, penner, fodder-feeder, milker: each with its own return |

H0 (no humans) stays as the reference wild type.

## Parameters vs outcomes

- **Become outcomes:** labour shares, offtake, herd size, whether herding/penning is taken up.
- **Parameters:** need per person, groupSink, meatYield, decay rates (meat, fodder), τ, floor share,
  number of people.

## Human plant food and plant domestication (2026-10-25, with Chris)

Built: a second resource, human plant food (seeds, tubers, fruit) that goats do not eat: patches of
sites with site-level capacity, a yearly masting factor per patch, a fruiting window, rot outside it,
and a slowly spoiling camp store. Gatherers harvest it; feeders (a herding task) cut vegetation as fodder.

Future stage, plant domestication: relocating sites near camp for less travel time. Two routes:
1. Deliberate: a tending/sowing role spends labour to create or move a site near camp, scored like
   herding (change in the value of the camp's near food stock).
2. Emergent ("dump-heap"): harvest carried home seeds new sites near camp with some chance, drawn from
   the source patch, so near-camp patches accumulate without anyone choosing to plant. The same
   carried-seed logic as the grain model's bottom-of-the-bag planting.

## Open questions

1. What do people eat in E0? If gathering is plant food edible to people *and* usable as fodder,
   one resource has two uses; if gathering is fodder only, E0 has no human income.
2. Is a capture credited to the hunter (its stock value) or to herding?
3. Does a herder's return use the change in stock value over a day (noisy: births, deaths) or a
   smoothed one?
4. How does the herder role divide in E3, and what is each sub-role's measurable return?
5. Is there a rest/camp role, or does everyone work every day?
