# Synthetic biomarker benchmark — what came out

Six biomarker implementations were run over the same **36 renderings** — nine drawn shapes at four
angles each — on a 2048² grid at 5 µm per pixel, with arteries 80 µm wide, veins 120 µm and an
optic disc 1800 µm across. Nothing here was photographed and nothing was annotated: every shape was
*drawn* from equations, so what it ought to measure follows from arithmetic rather than from
anybody's opinion.

Every number on this page comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb). **Nothing was
re-measured for the 2026-09-30 revision**: not one stored value changed, because a run records
what an implementation returned and records no mapping at all. What changed is the names those
values answer to and the units they are compared in — which is the whole point of keeping the two
apart, and the reason a correction to the catalogue costs no compute. **The measurements
are reproducible**: clearing `results/` and running all 54 pairs again reproduces every stored value
exactly, to the last decimal, and the only columns that move are the timings. How the benchmark
is configured is a separate page, [biomarker-synthetic-docs.md](biomarker-synthetic-docs.md), and
the shapes with their derivations are in
[the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb).

**All six are on this page together, and that is the point.** The question is whether these
programs compute the same quantity, and that question lives across a row — one biomarker, six
columns. The columns stand in **lineage order**: [PVBM](../projects/pvbm.md) and
[OCULAR](../projects/ocularnet.md), which imports PVBM's helpers at runtime; then
[AutoMorph](../projects/automorph.md) and its two descendants,
[AutoMorphalyzer](../projects/automorphalyzer.md) and
[AutoMorphClass](../projects/automorphclass.md); then [VascX](../projects/vascx.md), which shares
code with none of them. A difference **between neighbours** is a change somebody made on purpose; a
difference **across a boundary** is two independent readings of the same definition.

> **PVBM now measures with `GeometryAnalysis`**, from 2026-09-26, having used the deprecated
> `GeometricalAnalysis` before. That is not a rename — the replacement takes the optic disc and
> walks each tree from where it leaves it — and section 3.1 says what it changed. PVBM's row in
> every table below is the new class.
>
> **Every catalogued number on this page is now in microns**, from 2026-09-30, and none of them
> was before. A canonical biomarker states a physical unit — µm, µm², 1/µm — so an implementation's
> pixel measurement is converted once before it meets the ground truth, and the ground truth itself
> was rebuilt the same way. Section 9 is what that changed, and it is not only presentational: one
> figure this page reported as an 81% error in somebody's code was an error in *ours*.
>
> **These numbers replace an earlier set, and several conclusions moved.** The Koch curve was
> previously drawn at four generations, finer than the vessel painted along it, so the picture did
> not carry the value derived beside it and every implementation was charged with the difference.
> It is now drawn at two generations and half width, verified against its own skeleton. Section 6
> says what changed and what it changed. Where a conclusion below differs from the one this page
> carried before, that is why.

## Contents

1. [Summary](#1-summary)
2. [What could be compared, and what could not](#2-what-could-be-compared-and-what-could-not)
3. [Nothing raised, once PVBM was given the same recursion limit as its fork](#3-nothing-raised-once-pvbm-was-given-the-same-recursion-limit-as-its-fork)
4. [Turning the picture changes the answer](#4-turning-the-picture-changes-the-answer)
5. [Disagreement with the geometry](#5-disagreement-with-the-geometry)
6. [The Koch curve, redrawn](#6-the-koch-curve-redrawn)
7. [Which to reach for, and at what question](#7-which-to-reach-for-and-at-what-question)
8. [What these numbers do not say](#8-what-these-numbers-do-not-say)
9. [What changed, and what it did not](#9-what-changed-and-what-it-did-not)

## 1. Summary

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Biomarkers produced | 30 | 18 | 18 | 54 | 18 | 20 |
| …matching a canonical name | 20 | 10 | 15 | 23 | 15 | 8 |
| Comparable measurements | 312 | 304 | 372 | 388 | 372 | **80** |
| Median disagreement | 3.7% | 3.0% | 8.2% | 6.1% | 5.5% | **0.0%** |
| Within 25% of the geometry | 90% | **95%** | 80% | 92% | 91% | 90% |
| Quantities that move when the image turns | 9 / 30 | 8 / 18 | 16 / 18 | 19 / 40 | 11 / 18 | **4 / 20** |
| Biomarkers disagreeing with the geometry | 7 / 20 | 5 / 10 | 9 / 15 | **3 / 17** | 4 / 15 | 2 / 6 |
| Exceptions | 0 | 0 | 0 | 0 | 0 | 0 |
| Seconds per image | **19.2** | 2.2 | 0.9 | 3.9 | **0.5** | 2.8 |

**Every figure here is taken against a noise floor of 1% of the biomarker's own size**, meaning the
largest value the shapes require of it anywhere in the store. A difference smaller than that counts
as agreement, and no percentage is divided by anything smaller. It is a deliberately high floor:
these shapes are drawn onto a pixel lattice and skeletonised, and below that quantisation a
percentage compares two noises.

*The floor was an absolute 0.01 until 2026-09-30, when it stopped working.* Once every canonical
length became physical, this benchmark's quantities came to span an area of about 250,000 µm² and a
squared curvature of about 10⁻⁸ /µm², and one constant cannot be a noise floor for both — the same
0.01 that ignores rasterisation on an area forgives every answer τ7 can give. Making it relative
also removed the caveat this paragraph used to carry, that five biomarkers had typical values under
the floor and so were graded more kindly than the rest.

**Read this table down a column, not across a row.** The accuracy rows are not a score and the
columns are not ranked by them, because the columns are not answering the same question: VascX's
0.0% median is over **80** measurements of six biomarkers, and PVBM's 3.7% is over **312** of
twenty. Measuring less, more carefully, is a defensible engineering choice and it is not the
same achievement as measuring more. Section 7 says what can actually be concluded.

Two figures stand out on their own terms. **PVBM takes about forty times longer per image than
AutoMorphClass** — 19.2 seconds against 0.5 — which over a study of fifty thousand photographs is
about eleven days of compute against seven hours. **Nothing raises any more**, which took giving
PVBM the recursion limit its own fork sets, and cost it the appearance of being the steadiest thing
here (section 3).

## 2. What could be compared, and what could not

Three different things stand between a quantity a program computes and a number this benchmark can
judge, and the counts above only mean something once they are kept apart:

- **The catalogue may have no name for it.** AutoMorphalyzer returns 17 quantities with no
  canonical name — `average_local_calibre` at every zone, `tortuosity_density` and
  `tortuosity_distance` at zone C, and two Knudtson equivalents at zone C. VascX returns 12,
  PVBM 10. *That count fell from 23 when the vocabulary gained a region: AutoMorphalyzer's zone-B
  tortuosity columns now have a catalogued name, because the region is part of the name rather
  than a thing the catalogue could not express.* These are measured and stored under the implementation's
  own name and appear in **no** comparison, because a canonical name exists to make two numbers
  comparable and there is nothing yet to compare them with. Each one is either a gap in the
  catalogue or a mapping nobody has made — both are work somebody can do, and the notebook's
  section 1 lists them by name.
- **No shape may settle it.** A quantity can carry a catalogued name and still have no theoretical
  value here. This is why VascX's eight canonical names yield six judged biomarkers, and why
  AutoMorphalyzer's zone-B columns — newly nameable — are still judged against nothing: no shape
  here is drawn to pin a value inside that annulus, only across it.
- **The program may simply never answer.** AutoMorphalyzer returns 54 columns of which 40 ever
  carry a value.

## 3. Nothing raised, once PVBM was given the same recursion limit as its fork

*This section used to be called "the one implementation that raised" and counted thirty-two
exceptions, all PVBM's. There are now none, and how that happened is more interesting than the
exceptions were.*

PVBM's geometry walks each vessel tree with mutual recursion — one Python frame per skeleton pixel
— so the depth it needs is a function of how much vessel there is. At CPython's default limit of
1000 it raised on the two densest shapes, `koch` and `deep-bifurcation`, losing the whole geometry
call at every angle.

**OCULAR never raised, and not because it measures differently.** Its fork sets
`sys.setrecursionlimit(5000)` at module import; PVBM does not. Measuring the two side by side with
one at Python's default and one at 5000 was reporting a difference in interpreter settings as a
difference between the programs. From 2026-09-26 this atlas raises the limit to the same 5000
around PVBM's call and puts it back afterwards, and declares the number so that a stored score
taken at another limit is not mistaken for this one.

**What that revealed is the point.** PVBM did not become worse; it stopped being absent:

| | when it raised | now |
| --- | --- | --- |
| Exceptions | 32 | **0** |
| Comparable measurements | 256 | **312** |
| Quantities that move when the image turns | 3 / 30 | **9 / 30** |
| Biomarkers disagreeing with the geometry | 5 / 20 | **7 / 20** |

The previous version of this page called PVBM "the steadiest implementation here" on the strength
of 3 of 30. That was 3 of 30 **over the shapes it could still measure**, and the two it could not
are the two where the vessels are dense enough to be hard. A program that fails on the difficult
cases and is steady on the rest is not steady.

### 3.1 PVBM's measuring class changed, and it is not a rename

PVBM ships two classes named `GeometricalVBMs` at the pinned commit. The one in
`GeometricalAnalysis` warns on construction that it goes in version 3.0 and names the one in
`GeometryAnalysis` as its replacement. **This atlas measured with the deprecated one until
2026-09-26 and now measures with the replacement.** The difference is not cosmetic:

| | Deprecated | Used here now |
| --- | --- | --- |
| Interface | five methods | one call returning eight numbers |
| Needs the optic disc | no | **yes** |
| Finds vessels by | scanning the whole mask | walking each tree from where it leaves the disc |
| Branching angle | mean, deviation **and** median | median only |
| Perimeter | yes | **none**, so this atlas stopped reporting one |

**The change is real and the improvement is smaller than it first looked.** Its junction count was
out by 785% under the deprecated class and reading 1, 4, 4, 3 across four angles of an unchanged
shape; it is now out by 42.9% and moves by 240%. An earlier version of this page reported 0.0% on
both, which was true of the single shape PVBM could then measure and false of the shape it could
not.

**The perimeter went too.** `GeometryAnalysis` has no equivalent of the deprecated
`compute_perimeter`, and the helper both classes call underneath is not an interface either of them
offers — so measuring one meant transcribing four lines out of the retired code, which is not what
a benchmark of the current version should report. Nothing in the catalogue named it, so no
comparison is lost; PVBM produces 30 columns here rather than 32, and runs 8 seconds an image
faster for it.

**Two mappings were withdrawn — PVBM's and OCULAR's.** The canonical endpoint count means every
free end a network has. The deprecated class counted those; the replacement calls the end at the
disc a *start point*, so its `endpoints` is the free ends **excluding** the one it started from — a
straight vessel reads 1 where the geometry requires 2. `endpoints + start_points` is what answers
the catalogued question, but summing them here would report a number PVBM never returned, so the
mapping is withdrawn and both columns are kept under PVBM's own names. OCULAR forks the same class
and inherits the same split, so its mapping goes for the same reason.

**On `disjoint`**, whose vessels never reach the optic disc, there are no trunks to walk and the
geometry call returns zeros — 100% out against a geometry that requires otherwise. That is a real
property of a disc-anchored measurement rather than a bug, and it is the one place where moving to
the replacement made a number worse.

### 3.2 PVBM and OCULAR now return the same numbers

With the recursion limit equalised, **every canonical biomarker the two share comes back
identical** — not close, identical:

| Biomarker | PVBM | OCULAR |
| --- | --- | --- |
| `topology/junctions/artery`, worst error | 42.9% | 42.9% |
| `topology/junctions/vein`, worst error | 85.7% | 85.7% |
| `tortuosity/hart-tau1/artery/median`, worst error | 16.5% | 16.5% |
| `tortuosity/hart-tau1/vein/median`, worst error | 31.2% | 31.2% |
| …and the same four under rotation | 240%, 66.7%, 20.1%, 30.2% | 240%, 66.7%, 20.1%, 30.2% |

**OCULAR's extra column now has a catalogued name.** Its `length_weighted_tortuosity` was kept
under OCULAR's own name because the vocabulary had no way to say *which* aggregation a tortuosity
was. It does now — the statistic is part of the name — so the column maps to
`tortuosity/hart-tau1/<structure>/length-weighted`, beside PVBM's and OCULAR's shared
`.../median`, and is judged like anything else. It is 8.5% out at worst against the median's 16.5%,
so on these shapes the arc-weighted mean is the better of OCULAR's two answers.

That is what reading the two files predicted. OCULAR's geometry is a fork of the same
`GeometryAnalysis`, 343 of its 486 lines identical, and its edits are a raised recursion limit, one
extra returned quantity, a `try`/`except` around the tree walk and an optional iterative
replacement that is off by default. **None of those change a shared number.** The recursion limit
was the whole of the difference this benchmark was reporting.

Two useful consequences. The pair is now a **control**: if a future change moves one and not the
other, the change is in the fork rather than in the measurement. And OCULAR's extra
`length_weighted_tortuosity` is the only thing it adds that PVBM does not have, which is a much
smaller claim than a page full of differing numbers implied.

## 4. Turning the picture changes the answer

The same shape is drawn again at each angle in continuous coordinates, never by turning a picture,
so the geometry at 30° is *identical* to the geometry at 0°. **Any spread at all is the
implementation or the pixel grid beneath it** — and this check needs no ground truth, which is why
it is also the only check the unnamed quantities of section 2 ever get.

Twenty-seven of 49 canonical biomarkers move by more than 10% somewhere. The worst of it — and
note that the *statistic* is now part of the name, so a row is one aggregation rather than a
family of them:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/grisan-density/vein/…` | — | — | 400.0% | 301.7% | 231.4% | — |
| `tortuosity/hart-tau1/artery/…` | 20.1% | 11.8% | 202.1% | 7.1% | 7.5% | 10.9% |
| `tortuosity/spline-curvature/artery/length-weighted` | — | — | — | — | — | 280.5% |
| `topology/junctions/artery` | 240.0% | 240.0% | — | — | — | — |
| `calibre/width/vein/length-weighted` | — | — | 60.0% | 14.0% | 14.0% | **1.7%** |
| `density/box-counting/artery` | — | — | 20.1% | 80.7% | 80.8% | — |

Three findings, and each is legible only because the columns are ordered by lineage:

- **Within the AutoMorph group, the descendants fixed their ancestor's tortuosity and inherited its
  Grisan density.** AutoMorph's Hart τ1 moves by 202% on a shape that did not change;
  AutoMorphalyzer's and AutoMorphClass's move by about 7%. That is a change somebody made on
  purpose, and it worked. Grisan density is the part nobody touched, and all three move by 231% to
  400% on it. *Earlier versions of this page reported AutoMorphClass at 0.0% here and called the
  gap hundredfold; that figure was the absolute noise floor of 0.01 doing the work, not
  AutoMorphClass. Against a floor set by Grisan density's own range it moves by 231%, which is
  better than its siblings and not in a different class from them. The hundredfold gap is real in
  the ground-truth comparison of section 5, where it is still about eightyfold, and it was never
  real here.* The box-counting dimension is a third case again — **worse** in the descendants
  (80.7% and 80.8%) than in AutoMorph (20.1%), so something one of them changed made it unstable.
- **Across the boundary, VascX is steadiest where it measures at all** — 1.7% on vein calibre where
  its neighbours are at 14% to 60%. It also has its own unique failure: `spline-curvature` at
  280.5% on arteries and 225.0% on veins, a quantity only VascX computes and which nothing else
  here would have caught.
- **PVBM and OCULAR now move by exactly the same amount**, 240% on the artery junction count and
  20.1% on Hart τ1, because they are running the same code at the same recursion limit (section
  3.2). The gap this page used to report between them was the limit and nothing else.

The unnamed quantities are no better. AutoMorphalyzer's `tortuosity_density` at zone C moves by
**400%** — its zone B is now catalogued and moves by the same 400% in the table above;
AutoMorph's and AutoMorphClass's `squared_curvature_tortuosity` move by 400% and 203%.
PVBM's `std_branching_angle_vein` used to lead this list at 393.5% and is absent from it now, for
the blunt reason that PVBM no longer computes it. None of those appears anywhere else on this page,
and without this section none of them would be checked at all.

## 5. Disagreement with the geometry

1,828 measurements have a theoretical value to be judged against, over 41 canonical biomarkers.
Twenty-one of the forty-one are out by more than 25% somewhere. The worst case each implementation
produced, over all shapes and all angles:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `topology/junctions/artery` | 42.9% | 42.9% | — | — | — | — |
| `topology/junctions/vein` | 85.7% | 85.7% | — | — | — | — |
| `calibre/CRE-hubbard/vein/B` | 37.4% | — | — | — | — | — |
| `calibre/AVR-hubbard/both/B` | 32.2% | — | — | — | — | — |
| `tortuosity/hart-tau1/vein/…` | 31.2% | **8.7%** | 542.2% | 13.4% | 7.4% | 43.4% |
| `density/skeleton-length/vein` | 100.0% | 100.0% | — | — | — | — |
| `calibre/width/vein/length-weighted` | — | — | 56.5% | 18.6% | 22.3% | **1.1%** |
| `tortuosity/grisan-density/vein/…` | — | — | 8,406,156% | 8,241,992% | **90,265%** | — |

**Those Grisan figures are against a truth of exactly nought** — a curve that bends one way
throughout has no inflections, so its tortuosity density is zero by definition — and the
percentage is therefore taken against the noise floor. Read them as *how many noise floors out*
rather than as a percentage of anything, and read the values instead. Asked for a quantity the
geometry puts at zero, on a straight vessel or a circular arc:

| | truth | AutoMorph | AutoMorphalyzer | AutoMorphClass |
| --- | --- | --- | --- | --- |
| Grisan density, per µm | 0 | 0.19 | 0.20 | 0.0021 |
| …as its own returned figure, per px | 0 | 0.93 | 1.00 | 0.010 |

The numbers are eight digits because Grisan's density is an inverse length: its entire range across
these shapes is about 0.0002 /µm, so a wrong answer of 0.19 is a thousand times the largest right
one. **What the comparison settles is that these are not the same quantity.** AutoMorph and
AutoMorphalyzer return roughly `(n−1)/n`, which is retipy's documented departure from Grisan's
formula — it *adds* the count factor where Grisan multiplies — and on a shape with one turn curve
that is about 1 rather than about 0. AutoMorphClass is out by eighty times less, which is still
wrong and is about the amount a rasteriser could explain.

A program that finds structure in a shape that has none remains the clearest single result on this
page. It is now clear that two of the three do it to a degree that puts them in a different unit.

Reading one shape at a time changes the picture in ways the worst-case column cannot show:

- On **`straight`**, the simplest shape there is, ten biomarkers are still out by more than 25%.
  AutoMorphalyzer's Grisan density reads 0.998 where the geometry requires nought and
  AutoMorphClass's reads 0.010, while **AutoMorph's reads exactly nought there** and is instead
  100% out on Hart τ1. That row is worth stating outright: AutoMorph returns 1.003 and 1.002 at 0°
  and 90°, and **0.0 at 30° and 60°** — and a τ1 of zero is not a wrong answer, it is an
  impossible one, since arc over chord cannot fall below 1. The diagonal renderings are the two
  where its vessel detector finds nothing long enough to measure, and it reports the empty sum
  rather than declining. That single behaviour is also most of its 202% rotation spread in section
  4. PVBM and OCULAR are inside tolerance on everything they measure here. A straight line is
  where an implementation has no excuse, and three of the six still find something on it.
- On **`disjoint`**, whose vessels never reach the optic disc, PVBM's and OCULAR's skeleton
  lengths are out by 100% — both return zero, having no trunk to walk from. That is the price of
  the disc-anchored class of section 3.1, and it is the one place where the change made a number
  worse rather than better. AutoMorph is 100% out on Hart τ1 here too, for the reason above: it
  returns 0.0 rather than declining.
- On **`deep-bifurcation`**, the densest shape here, PVBM and OCULAR are out by 42.9% and 85.7% on
  the junction count — identically, as everywhere. *PVBM's figures on this shape used to be absent
  altogether, its geometry having raised; section 3 is how that was fixed and what it cost the
  page's earlier conclusions.* **VascX's tortuosity there is the best figure anywhere on this
  page: 0.0%**, inside the noise floor at every angle, on the shape with the most branching.

## 6. The Koch curve, redrawn

**This section previously reported a defect in the fixture. It has been fixed, and what is left is
a finding about the implementations.**

The shape exists to pin a **fractal dimension**: every other shape here is smooth, and a smooth
curve's dimension is exactly 1, which no box count returns from a bounded raster. A Koch curve's is
`log 4 / log 3` ≈ 1.2619 — exact, not an integer, and reachable.

It was drawn at four generations, which made its finest detail 8.6 pixels under a 24-pixel vein.
The brush was wider than what it was painting, so two of the four generations were not in the
picture at all: the image carried an arc-to-chord ratio of 2.18 where the theory derived beside it
said 3.160, and a box dimension of 1.51 against 1.2619. All six implementations returned about 1.3,
and the benchmark duly reported six independent failures where there was one drawing defect.

It is now drawn at **two generations and half the usual vessel width** — 40 µm and 60 µm, recorded
as such in the manifest. Two facts decided that, and only one is the obvious one: the box dimension
follows the **vessel width** rather than the depth, because thickening adds area-like scaling below
the width; and each generation the drawing cannot resolve leaves a spurious endpoint where two
spikes merged, costing rotation stability with it. The drawing now carries an arc-to-chord ratio of
1.84 against a derived 1.778, and a box dimension of 1.28 against 1.2619. `library.koch` refuses to
draw a curve whose finest generation is under three times the vessel, and a test skeletonises the
result and compares it with its own theory, so this cannot silently come back.

**With the picture carrying its value, the disagreement is the implementations'.** Mean Hart τ1 over
the four angles, against a drawing that measurably has 1.84:

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Mean τ1 on `koch` | 1.726 | 1.726 | 1.021 | 1.544 | 1.684 | 1.069 |
| Against the derived 1.778 | **−3%** | **−3%** | −43% | −13% | −5% | −40% |

*PVBM read 1.412 here until the recursion limit was equalised, because it raised on two of the
four angles and the mean was taken over the two it survived. It now reads OCULAR's number
exactly, which is what section 3.2 predicts.*

**AutoMorph and VascX return about 1.02 and 1.07 on a curve whose drawn skeleton is 1.84** — within
a few percent of calling it a straight line. That is the finding the broken fixture was hiding, and
it is not a small one: a measurement blind to this much structure is blind to tortuosity.

Every implementation undershoots, and the reason is worth stating because it is not a bug in any of
them. Skeletonising a curve with 60° corners leaves short spurs, and an implementation that prunes
them before measuring gets a shorter arc and therefore a lower ratio. The drawn skeleton carries
four to six endpoints where the curve has two. So the ranking in that row is partly a ranking of
pruning strategies — which is a real difference between these programs, but it means the
**ordering** is more trustworthy than the absolute percentages.

Two caveats remain on this shape:

- **The −3% mean is excellent and the worst case is not.** PVBM and OCULAR are −3% on average,
  but 31.2% off at their worst angle and a 20.1% spread across the four. A steady wrong number and
  a jittery right one are different diseases, and this is the second.
- **PVBM's endpoint count on `koch` counts the skeleton's spurs as vessel ends**, and OCULAR's
  does the same. Neither appears as an error above, because both mappings are withdrawn (section
  3.1): the catalogued name means every free end the network has, and what these two return is the
  free ends excluding the one they started from. The behaviour is still there under their own
  column names, and the shape is still where it shows.

## 7. Which to reach for, and at what question

There is no best implementation here, and pretending otherwise would mean comparing a column of 80
measurements with a column of 312 as though they answered the same question. What can be said:

- **For vessel calibre, VascX**, and not by a small margin: 1.1% worst error on the
  length-weighted vein width against 18.6% to 56.5% for the AutoMorph group, and 1.7% movement
  under rotation against their 14% to 60%. The caveat is scope — VascX yields six judged biomarkers against PVBM's twenty, and it
  produced nothing comparable at all on the `straight` shape.
- **For tortuosity, AutoMorphClass or OCULAR's length-weighted column**: both are 8.5% worst on
  Hart τ1 over every shape and angle, against 13.7% for AutoMorphalyzer, 31% for the median PVBM
  and OCULAR both report, and 43% for VascX. AutoMorphClass is also the fastest thing here at half
  a second an image. *This page previously gave AutoMorphClass the highest share of measurements
  within tolerance, at 98%; it now reads 91%, level with AutoMorphalyzer, and OCULAR leads at 95%.
  Nothing about any of them changed. The 98% was the absolute noise floor forgiving small wrong
  answers on the biomarkers whose values are small, and AutoMorphClass has more of those than its
  siblings because it is the one that weights by length.*
- **For breadth, PVBM**, the only implementation that puts twenty canonical biomarkers on the
  table, including the central retinal equivalents and AVR that nothing else here computes. It is
  also the slowest by a wide margin, at 19 seconds an image against half a second for
  AutoMorphClass.

  *An earlier version of this section called PVBM the steadiest implementation here, on 3 of 30
  quantities moving under rotation.* It now reads 9 of 30, and nothing about PVBM changed except
  that it stopped raising on the two densest shapes and had to answer for them (section 3). The
  claim was an artefact of a failure, and it is withdrawn.
- **Do not use Grisan density from AutoMorph or AutoMorphalyzer**, which return about 0.93 and
  1.00 for a quantity the geometry puts at nought — roughly `(n−1)/n`, retipy's documented
  departure from the published formula — and move by 400% and 302% when the image is turned.
  **AutoMorphClass's is wrong by eighty times less**, returning 0.010 on the same question, which
  is about what a rasteriser could account for. None of the three is usable as Grisan's measure;
  only one of them is in the right order of magnitude.
- **Between PVBM and OCULAR there is nothing to choose on any shared number**, because they now
  return the same ones — identically, not approximately (section 3.2). Pick on what surrounds the
  geometry instead: PVBM adds the fractal dimensions and the central retinal equivalents and costs
  19 seconds an image; OCULAR adds a length-weighted tortuosity — now catalogued, and its own best
  answer on these shapes at 8.5% against the shared median's 16.5% — and costs two. Neither's
  **endpoint** count answers the catalogued question at all, and both mappings are withdrawn
  (section 3.1).
- **Do not use AutoMorph's own measuring stage for tortuosity** where either descendant is
  available. Its Hart τ1 is out by 542% on a circular arc and moves by 202% under rotation; both
  rewrites fixed exactly that.

Where two are close on accuracy, cost decides: AutoMorphClass at 0.5 seconds an image and
AutoMorphalyzer at 3.9 are one percentage point apart on agreement and eight times apart on time.

**And one caution about this page's own history.** Two of the recommendations above are the
opposite of what it said a week ago, and nothing about the eyes changed — one import did. A
benchmark that compares somebody else's code is measuring a moving target, and the useful habit is
to read the date beside a claim rather than the claim alone.

## 8. What these numbers do not say

- **That any of this transfers to photographs.** Every shape here is clean, complete, unbroken and
  drawn to a known scale, with no lesions, no crossings mislabelled and no segmentation error
  upstream. A program that measures a drawn arc correctly has cleared the lowest bar there is.
- **That a quantity with no ground truth is right.** It is unchecked, which is a third thing. Half
  of AutoMorphalyzer's returned columns are in that position.
- **That agreement between two implementations means either is correct.** PVBM and OCULAR share
  code, and so do the three AutoMorph entries; where siblings agree, that is evidence about their
  common ancestor. The only agreement on this page that means anything is agreement across the
  lineage boundaries — and section 6 is what that looked like when it happened for a bad reason.
- **That 25% and 10% are standards.** They are reporting conveniences, chosen so that a table shows
  the handful of quantities worth looking at rather than two hundred rows of nothing. Nothing here
  passes or fails.
- **That the timings are a property of the software alone.** Of everything recorded here they are
  the only figures that are not reproducible, and the gap is wide: running the whole benchmark
  again on the same machine, against the same pictures, with every measured value coming back
  identical, moved the per-implementation timings by **5% to 40%**. They also fell across the board
  when the Koch curve was redrawn, and again when PVBM changed measuring class. So treat the **ratios**
  as the finding — PVBM is forty-odd times AutoMorphClass, on any run — and treat a figure like
  "16 seconds an image" as describing this machine on one afternoon, against this fixture, rather
  than the program.

## 9. What changed, and what it did not

From 2026-09-30 every catalogued biomarker states a physical unit and none of them is in pixels.
Each implementation still reports what it measured on the pixel grid, under its own column names,
and that number is converted once — by the rule the ground truth was built with — before the two
meet. Five things changed on this page, and only the first is cosmetic. **None of them was a
re-measurement of anything but VascX, and that one reproduced its own numbers exactly** (§9.4).

**9.1 The names got longer, and one of them split in two.** A canonical name now carries the
statistic that pooled it, so `tortuosity/hart-tau1/artery/mean` and
`.../artery/length-weighted` are different rows. That is not tidying: reading the three AutoMorph
implementations showed that **AutoMorph and AutoMorphalyzer divide by the vessel count while
AutoMorphClass multiplies each vessel by its own curve length**, so a row that used to hold all
three was holding two different measurements. The same distinction gave OCULAR's third tortuosity
column a name (section 3.2) and named VascX's `lw_` columns for what they are.

**9.2 A defect was found in this repository's own ground truth, and one of this page's findings
was ours.** Hubbard's equivalent carries constants fitted in microns, so it can only be evaluated
on micron widths — and the shape library converted its answer to microns a *second* time at the
end. Against that inflated truth, PVBM's arteriolar equivalent read **81.4% out**; against the
corrected one it reads **6.8%**. The arteriolar figure is withdrawn. The venular one survives at
37.4%, and its asymmetry is the mechanism itself: Hubbard's additive constant is −10.76 µm for
arterioles and **+450.05 µm** for venules, so computing on pixel widths — which PVBM does, and
which its own page records — hurts the vein far more than the artery. Its AVR inherits that at
32.2%.

**9.3 A mapping was made on the strength of a name, and withdrawn on the strength of the code.**
`density/sparsity` — how far the retina is from the nearest vessel — became catalogued when the
families were rebuilt, and VascX's `mean_sparsity_vessels` was mapped to it. The shapes disagreed
by a factor of about 3,900. Reading `vascx/fundus/features/sparsity.py` says why: its constructor
takes `normalize=True` by default and "sparsity is normalized by the OD-fovea distance", so the
number is a dimensionless ratio rather than a distance — and on a synthetic shape the fovea is a
convention this repository supplied. The mapping is withdrawn. VascX's share of measurements
within tolerance was 62% with it and is 90% without, which is what a wrong mapping costs.

**9.4 VascX is now four pinned clones**, from 2026-10-01, where it was four pip installs —
`retinalysis-vascx` and the three Eyened packages it runs on, one of which, `retinalysis-enface`,
supplies the optic disc and the fundus that every VascX measurement here is built on. Its project
page §1 carries the pins and what the choice costs.

**Every measured value is unchanged**, which is the point of recording it: re-running all nine
shapes against the clones reproduced each of VascX's numbers exactly, and only the fingerprint and
the timing moved — 2.9 seconds an image to 2.8, inside the run-to-run spread §8 already warns
about. What did change is what a stored score is pinned to. VascX's row in the configuration page
now names all four commits rather than one, and the adapter's identity hashes all four, because a
change in `rtnls_enface` moves these numbers exactly as a change in `vascx` would and the old
fingerprint could not have seen it. OCULAR's row gained PVBM's commit beside its own for the same
reason.

**9.5 Grisan's density turned out to be an inverse length**, which its own catalogue page said in
its derivation and denied in its vocabulary table. Its units row now reads `1/µm`. Nothing any
implementation returns changed; what changed is that a value computed at 1024 pixels and one
computed at 2048 are now the same number, and the noise floor beneath it is set by its own range
rather than by a constant meant for an area (section 1).

---

**Compiled from** [notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb).
