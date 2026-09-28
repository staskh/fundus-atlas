# Synthetic biomarker benchmark — what came out

Six biomarker implementations were run over the same **36 renderings** — nine drawn shapes at four
angles each — on a 2048² grid at 5 µm per pixel, with arteries 80 µm wide, veins 120 µm and an
optic disc 1800 µm across. Nothing here was photographed and nothing was annotated: every shape was
*drawn* from equations, so what it ought to measure follows from arithmetic rather than from
anybody's opinion.

Every number on this page comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb). **The measurements
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

## 1. Summary

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Biomarkers produced | 30 | 18 | 18 | 54 | 18 | 20 |
| …matching a canonical name | 20 | 8 | 15 | 17 | 15 | 8 |
| Comparable measurements | 312 | 240 | 216 | 232 | 216 | **80** |
| Median disagreement | 3.8% | 2.2% | 3.9% | 6.5% | 5.3% | **0.7%** |
| Within 25% of the geometry | 87% | 93% | 79% | 91% | **98%** | 90% |
| Quantities that move when the image turns | 9 / 30 | 8 / 18 | 15 / 18 | 19 / 40 | 10 / 18 | **4 / 20** |
| Biomarkers disagreeing with the geometry | 8 / 20 | 5 / 8 | 6 / 10 | **2 / 12** | 2 / 10 | 2 / 6 |
| Exceptions | 0 | 0 | 0 | 0 | 0 | 0 |
| Seconds per image | **19.2** | 2.2 | 0.9 | 3.9 | **0.5** | 2.9 |

**Every figure here is taken against a noise floor of 0.01 in biomarker units**, added 2026-09-26.
A difference smaller than that counts as agreement, and no percentage is divided by anything
smaller. It is a deliberately high floor: these shapes are drawn onto a pixel lattice and
skeletonised, and below that quantisation a percentage compares two noises. It is also not free —
five catalogued biomarkers have typical values *under* 0.01, so their errors are understated here
and small ones are forgiven outright. The notebook's constant block names them.

**Read this table down a column, not across a row.** The accuracy rows are not a score and the
columns are not ranked by them, because the columns are not answering the same question: VascX's
0.7% median is over **80** measurements of six biomarkers, and PVBM's 3.8% is over **256** of
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

- **The catalogue may have no name for it.** AutoMorphalyzer returns 23 quantities with no
  canonical name — `average_local_calibre`, `tortuosity_density` and `tortuosity_distance`, each at
  zone B, zone C and whole-image and each for artery, vein and both, plus two Knudtson equivalents
  at zone C. VascX returns 12, PVBM 10. These are measured and stored under the implementation's
  own name and appear in **no** comparison, because a canonical name exists to make two numbers
  comparable and there is nothing yet to compare them with. Each one is either a gap in the
  catalogue or a mapping nobody has made — both are work somebody can do, and the notebook's
  section 1 lists them by name.
- **No shape may settle it.** A quantity can carry a catalogued name and still have no theoretical
  value here. This is why VascX's eight canonical names yield six judged biomarkers and AutoMorph's
  fifteen yield ten.
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
| Biomarkers disagreeing with the geometry | 5 / 20 | **8 / 20** |

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
| `junction-counts/junctions/artery`, worst error | 42.9% | 42.9% |
| `junction-counts/junctions/vein`, worst error | 85.7% | 85.7% |
| `tortuosity/hart-tau1/artery`, worst error | 16.5% | 16.5% |
| `tortuosity/hart-tau1/vein`, worst error | 31.2% | 31.2% |
| …and the same four under rotation | 240%, 66.7%, 20.1%, 30.2% | 240%, 66.7%, 20.1%, 30.2% |

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

Seventeen of 35 canonical biomarkers move by more than 10% somewhere. The worst of it:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/grisan-density/vein` | — | — | 400.0% | 301.7% | **0.0%** | — |
| `tortuosity/hart-tau1/artery` | 20.1% | 20.1% | 202.1% | 7.1% | 7.5% | 10.9% |
| `tortuosity/spline-mean-curvature/artery` | — | — | — | — | — | 280.5% |
| `junction-counts/junctions/artery` | 240.0% | 240.0% | — | — | — | — |
| `vessel-calibre/mean-width/vein` | — | — | 60.0% | 14.0% | 14.0% | **1.7%** |
| `fractal-dimension/box-counting/artery` | — | — | 20.1% | 80.7% | 80.8% | — |

Three findings, and each is legible only because the columns are ordered by lineage:

- **Within the AutoMorph group, the descendants fixed their ancestor's tortuosity and inherited its
  Grisan density.** AutoMorph's Hart τ1 moves by 202% on a shape that did not change;
  AutoMorphalyzer's and AutoMorphClass's move by about 7%. That is a change somebody made on
  purpose, and it worked. Grisan density is the part nobody touched — and **only two of the three
  are badly wrong about it**. AutoMorph moves by 400% and AutoMorphalyzer by 302%, while
  AutoMorphClass now reads **0.0%**, because everything it does there falls under the noise floor.
  On shapes whose Grisan density must be exactly nought, AutoMorphalyzer reaches 0.998 and
  AutoMorph 0.295, while AutoMorphClass reaches 0.00998 — a hundredfold difference between
  siblings, which every earlier version of this page reported as one finding shared by all three. The box-counting dimension is a third case again — **worse** in the descendants
  (80.7% and 80.8%) than in AutoMorph (20.1%), so something one of them changed made it unstable.
- **Across the boundary, VascX is steadiest where it measures at all** — 1.7% on vein calibre where
  its neighbours are at 14% to 60%. It also has its own unique failure: `spline-mean-curvature` at
  280.5%, a quantity only VascX computes and which nothing else here would have caught.
- **PVBM and OCULAR now move by exactly the same amount**, 240% on the artery junction count and
  20.1% on Hart τ1, because they are running the same code at the same recursion limit (section
  3.2). The gap this page used to report between them was the limit and nothing else.

The unnamed quantities are no better. AutoMorphalyzer's `tortuosity_density` at zones B and C moves
by **400%**; AutoMorph's and AutoMorphClass's `squared_curvature_tortuosity` by 400% and 203%.
PVBM's `std_branching_angle_vein` used to lead this list at 393.5% and is absent from it now, for
the blunt reason that PVBM no longer computes it. None of those appears anywhere else on this page,
and without this section none of them would be checked at all.

## 5. Disagreement with the geometry

1,296 measurements have a theoretical value to be judged against, over 28 canonical biomarkers.
Thirteen of the twenty-eight are out by more than 25% somewhere. The worst case each implementation
produced, over all shapes and all angles:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `junction-counts/junctions/artery` | 42.9% | 42.9% | — | — | — | — |
| `junction-counts/endpoints/vein` | — | 100.0% | — | — | — | — |
| `central-retinal-equivalents/hubbard/artery` | 81.4% | — | — | — | — | — |
| `tortuosity/hart-tau1/vein` | 31.2% | 31.2% | 542.2% | 13.4% | **7.4%** | 43.4% |
| `vessel-area-and-length/skeleton-length/vein` | 100.0% | 100.0% | — | — | — | — |
| `vessel-calibre/mean-width/vein` | — | — | 56.5% | 18.6% | 22.3% | **1.1%** |
| `avr/hubbard/both` | 32.2% | — | — | — | — | — |
| `tortuosity/grisan-density/artery` | — | — | 8,286% | 9,977% | **104%** | — |

**Those Grisan figures are against a truth of exactly nought** — a straight vessel has no
inflections — so the percentage is taken against the noise floor and reflects the floor as much as
the fault. What the floor *does* settle is that the three implementations are not doing the same
thing. Asked for a quantity the geometry puts at zero, AutoMorph returns 0.93, AutoMorphalyzer
returns 1.00, and **AutoMorphClass returns 0.011** — a hundredfold gap between siblings, which the
previous version of this page reported as three identical infinities. AutoMorphClass is still
wrong; it is wrong by about the amount the rasteriser could explain, and the other two are not.

A program that finds structure in a shape that has none remains the clearest single result on this
page. It is now clear that only two of the three do it to a degree that matters.

Reading one shape at a time changes the picture in ways the worst-case column cannot show:

- On **`straight`**, the simplest shape there is, five biomarkers are still out by more than 25%.
  AutoMorphalyzer's Grisan density reads 0.998 where the geometry requires nought; AutoMorph's
  reads exactly nought there and 100% out on Hart τ1; AutoMorphClass clears the noise floor on one
  of the two classes and not the other. PVBM and OCULAR sit at 7.3%. A straight line is where an
  implementation has no excuse, and three of the six still find something on it.
- On **`disjoint`**, whose vessels never reach the optic disc, PVBM's skeleton length is out by
  100% — it returns zero, having no trunk to walk from. That is the price of the disc-anchored
  class of section 3.1, and it is the one place where the change made a number worse rather than
  better.
- On **`deep-bifurcation`**, OCULAR's junctions are out by 42.9% and PVBM's are absent, its
  geometry having raised. VascX's tortuosity there is the best figure anywhere on this page: 0.8%.

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
| Mean τ1 on `koch` | 1.412 | 1.726 | 1.021 | 1.544 | 1.684 | 1.069 |
| Against the derived 1.778 | −21% | **−3%** | −43% | −13% | −5% | −40% |

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

- **OCULAR's mean is excellent and its worst case is not.** −3% on average, but 31.2% off at its
  worst angle and a 20.1% spread across the four. A steady wrong number and a jittery right one are
  different diseases, and this is the second.
- **PVBM's endpoint count on `koch` is out by 200% to 250%**, counting the skeleton's spurs as
  vessel ends. OCULAR, measuring with PVBM's own helpers, is out by 50%.

## 7. Which to reach for, and at what question

There is no best implementation here, and pretending otherwise would mean comparing a column of 80
measurements with a column of 312 as though they answered the same question. What can be said:

- **For vessel calibre, VascX**, and not by a small margin: 1.1% worst error on vein width against
  18.6% to 56.5% for the AutoMorph group, and 1.7% movement under rotation against their 14% to
  60%. The caveat is scope — VascX yields six judged biomarkers against PVBM's twenty, and it
  produced nothing comparable at all on the `straight` shape.
- **For tortuosity, AutoMorphClass**: 8.5% worst on Hart τ1 over every shape and angle, against
  13.7% for its sibling, 31–33% for PVBM and OCULAR and 43% for VascX. It is also the fastest thing
  here, at half a second an image, **and now has the highest share of measurements within tolerance
  of anything on this page** — 98%, against 91% for AutoMorphalyzer. That last figure changed when
  the noise floor was introduced and is worth reading carefully: what improved was not
  AutoMorphClass but this page's ability to tell it apart from a sibling that is genuinely
  a hundred times further out on the same quantity.
- **For breadth, PVBM**, the only implementation that puts twenty canonical biomarkers on the
  table, including the central retinal equivalents and AVR that nothing else here computes. It is
  also the slowest by a wide margin, at 19 seconds an image against half a second for
  AutoMorphClass.

  *An earlier version of this section called PVBM the steadiest implementation here, on 3 of 30
  quantities moving under rotation.* It now reads 9 of 30, and nothing about PVBM changed except
  that it stopped raising on the two densest shapes and had to answer for them (section 3). The
  claim was an artefact of a failure, and it is withdrawn.
- **Do not use Grisan density from AutoMorph or AutoMorphalyzer**, which return 0.93 and 1.00 for
  a quantity the geometry puts at nought and move by 400% and 302% when the image is turned.
  **AutoMorphClass's is a different matter**: it returns 0.011 on the same question and holds still
  under rotation, which is wrong by about what the rasteriser could account for rather than wrong
  outright. That distinction only became visible once a noise floor was applied (section 1); before
  it, all three read as the same infinite failure.
- **Between PVBM and OCULAR there is nothing to choose on any shared number**, because they now
  return the same ones — identically, not approximately (section 3.2). Pick on what surrounds the
  geometry instead: PVBM adds the fractal dimensions and the central retinal equivalents and costs
  19 seconds an image; OCULAR adds a length-weighted tortuosity and costs two. Neither's
  **endpoint** count answers the catalogued question at all, and both mappings are withdrawn
  (section 3.1).
- **Do not use AutoMorph's own measuring stage for tortuosity** where either descendant is
  available. Its Hart τ1 is out by 542% on a circular arc and moves by 202% under rotation; both
  rewrites fixed exactly that.

Where two are close on accuracy, cost decides: AutoMorphClass at 0.4 seconds an image and
AutoMorphalyzer at 3.6 are two percentage points apart on agreement and nine times apart on time.

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

---

**Compiled from** [notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb).
