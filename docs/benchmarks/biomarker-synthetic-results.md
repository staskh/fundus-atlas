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
3. [The one implementation that raised](#3-the-one-implementation-that-raised)
4. [Turning the picture changes the answer](#4-turning-the-picture-changes-the-answer)
5. [Disagreement with the geometry](#5-disagreement-with-the-geometry)
6. [The Koch curve, redrawn](#6-the-koch-curve-redrawn)
7. [Which to reach for, and at what question](#7-which-to-reach-for-and-at-what-question)
8. [What these numbers do not say](#8-what-these-numbers-do-not-say)

## 1. Summary

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Biomarkers produced | 32 | 18 | 18 | 54 | 18 | 20 |
| …matching a canonical name | 20 | 10 | 15 | 17 | 15 | 8 |
| Comparable measurements | 256 | 312 | 216 | 232 | 216 | **80** |
| Median disagreement | 3.8% | 4.6% | 8.0% | 7.0% | 7.3% | **0.7%** |
| Within 25% of the geometry | 88% | 74% | 76% | **91%** | 89% | 90% |
| Quantities that move when the image turns | **3 / 32** | 8 / 18 | 16 / 18 | 19 / 40 | 11 / 18 | 4 / 20 |
| Biomarkers disagreeing with the geometry | 5 / 20 | 7 / 10 | 6 / 10 | **2 / 12** | 3 / 10 | 2 / 6 |
| Exceptions | **32** | 0 | 0 | 0 | 0 | 0 |
| Seconds per image | **24.5** | 2.1 | 0.8 | 3.6 | **0.4** | 2.6 |

**Read this table down a column, not across a row.** The accuracy rows are not a score and the
columns are not ranked by them, because the columns are not answering the same question: VascX's
0.7% median is over **80** measurements of six biomarkers, and PVBM's 3.8% is over **256** of
twenty. Measuring less, more carefully, is a defensible engineering choice and it is not the
same achievement as measuring more. Section 7 says what can actually be concluded.

Two figures stand out on their own terms. **PVBM takes about sixty times longer per image than
AutoMorphClass** — 24.5 seconds against 0.4 — which over a study of fifty thousand photographs is
about two weeks of compute against six hours. And **PVBM is the only implementation that raised at
all**, now thirty-two times rather than sixteen (section 3).

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

## 3. The one implementation that raised

**Thirty-two** exceptions, all PVBM, all `RecursionError: maximum recursion depth exceeded`, and
all on exactly two shapes: **`koch` and `deep-bifurcation`**, at every one of the four angles.

PVBM walks a vessel tree recursively, so the failure is a function of how much vessel there is
rather than of anything being malformed — a real photograph of a densely vascularised retina can
trigger it, and a sparse one will not. The Koch curve now carries a skeleton a little over half its
former length — 1,238 pixels against 2,201 — and **still** raises: whatever the limit is, it is not
far above an ordinary branching vessel.

**It used to be sixteen, and the doubling is the cost of section 3.1.** Under the deprecated class
only the central retinal equivalents walked the tree recursively, so only they were lost. The
replacement walks it too, so on those two shapes the whole geometry call now goes with them — eight
quantities per class rather than one. Those renderings are still *measured*, because the fractal
analysis and the perimeter come back, but the geometry is gone from them.

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
| Perimeter | yes | **none** — see `docs/projects/pvbm.md` §8 |

**Mostly this made PVBM better, and in one case exactly right.** Its junction count was the worst
number on the previous version of this page — out by 785% and reading 1, 4, 4, 3 across four angles
of an unchanged shape. It is now **exact on every shape and every angle**, 0.0% error and 0.0%
spread. Hart τ1 went from 33% out to 7.8%, and the count of quantities that move when the image
turns fell from 13 of 32 to **3 of 32**.

**Three things got worse, and all three are honest.** The geometry now fails on dense shapes
(above). On **`disjoint`**, whose vessels never reach the optic disc, there are no trunks to walk
and the whole geometry call returns zeros — which reads as 100% error against a geometry that
requires otherwise, and is a real property of a disc-anchored measurement rather than a bug. And
the **mean and standard deviation of the branching angle no longer exist**: the code that produced
them is the code that was retired.

**One mapping was withdrawn.** The canonical endpoint count means every free end a network has. The
deprecated class counted those; the replacement calls the end at the disc a *start point*, so its
`endpoints` is the free ends **excluding** the one it started from — a straight vessel reads 1
where the geometry requires 2. `endpoints + start_points` is what answers the catalogued question,
but summing them here would report a number PVBM never returned, so the mapping is withdrawn and
both columns are kept under PVBM's own names. That is why PVBM names twenty canonical biomarkers on
this page and twenty-two on the last one.

An implementation that raises has at least told you it could not answer; the rest of this page is
about the harder case, where a program returns a confident number instead.

## 4. Turning the picture changes the answer

The same shape is drawn again at each angle in continuous coordinates, never by turning a picture,
so the geometry at 30° is *identical* to the geometry at 0°. **Any spread at all is the
implementation or the pixel grid beneath it** — and this check needs no ground truth, which is why
it is also the only check the unnamed quantities of section 2 ever get.

Nineteen of 37 canonical biomarkers move by more than 10% somewhere. The worst of it:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/grisan-density/vein` | — | — | 400.0% | 301.7% | 231.4% | — |
| `tortuosity/hart-tau1/artery` | **7.0%** | 20.1% | 202.1% | 7.1% | 7.5% | 10.9% |
| `tortuosity/spline-mean-curvature/artery` | — | — | — | — | — | 280.5% |
| `junction-counts/junctions/artery` | **0.0%** | 240.0% | — | — | — | — |
| `vessel-calibre/mean-width/vein` | — | — | 60.0% | 14.0% | 14.0% | **1.7%** |
| `fractal-dimension/box-counting/artery` | — | — | 20.1% | 80.7% | 80.8% | — |

Three findings, and each is legible only because the columns are ordered by lineage:

- **Within the AutoMorph group, the descendants fixed their ancestor's tortuosity and inherited its
  Grisan density.** AutoMorph's Hart τ1 moves by 202% on a shape that did not change;
  AutoMorphalyzer's and AutoMorphClass's move by about 7%. That is a change somebody made on
  purpose, and it worked. Grisan density moves by 231% to 400% in all three, which is the part
  nobody touched. The box-counting dimension is a third case again — **worse** in the descendants
  (80.7% and 80.8%) than in AutoMorph (20.1%), so something one of them changed made it unstable.
- **Across the boundary, VascX is steadiest where it measures at all** — 1.7% on vein calibre where
  its neighbours are at 14% to 60%. It also has its own unique failure: `spline-mean-curvature` at
  280.5%, a quantity only VascX computes and which nothing else here would have caught.
- **PVBM's junction count is now exact and OCULAR's is not**, 0.0% against 240%. They were 107%
  and 160% on the previous version of this page, when both ran the same deprecated class. PVBM has
  moved to its replacement and OCULAR — which is a *modified copy* of the deprecated one — cannot
  follow without its authors porting it. On `bifurcation`, a single fork with one junction, PVBM
  now answers 1 at every angle where it used to read **1, 4, 4, 3**.

The unnamed quantities are no better. AutoMorphalyzer's `tortuosity_density` at zones B and C moves
by **400%**; AutoMorph's and AutoMorphClass's `squared_curvature_tortuosity` by 400% and 203%.
PVBM's `std_branching_angle_vein` used to lead this list at 393.5% and is absent from it now, for
the blunt reason that PVBM no longer computes it. None of those appears anywhere else on this page,
and without this section none of them would be checked at all.

## 5. Disagreement with the geometry

1,312 measurements have a theoretical value to be judged against, over 30 canonical biomarkers.
Fifteen of the thirty are out by more than 25% somewhere. The worst case each implementation
produced, over all shapes and all angles:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `junction-counts/junctions/artery` | **0.0%** | 42.9% | — | — | — | — |
| `junction-counts/endpoints/vein` | — | 100.0% | — | — | — | — |
| `central-retinal-equivalents/hubbard/artery` | 81.4% | — | — | — | — | — |
| `tortuosity/hart-tau1/vein` | 8.1% | 31.2% | 542.2% | 13.4% | **7.4%** | 43.4% |
| `vessel-area-and-length/skeleton-length/vein` | 100.0% | 100.0% | — | — | — | — |
| `vessel-calibre/mean-width/vein` | — | — | 56.5% | 18.6% | 22.3% | **1.1%** |
| `avr/hubbard/both` | 32.2% | — | — | — | — | — |
| `tortuosity/grisan-density/artery` | — | — | **∞** | **∞** | **∞** | — |

`∞` is not a rounding artefact. It means the geometry requires **exactly nought** — a straight
vessel has no inflections, so its Grisan density is zero — and all three AutoMorph implementations
returned something else. On the sinusoid the same quantity is out by 67,796%, 89,966% and 940%. A
program that finds structure in a shape that has none is a more serious finding than any percentage
would be, and it is the clearest single result on this page.

Reading one shape at a time changes the picture in ways the worst-case column cannot show:

- On **`straight`**, the simplest shape there is, PVBM's worst error over everything comparable is
  7.5%, OCULAR's is 50%, AutoMorph's is 100%, and both AutoMorph descendants are at `∞`. A straight
  line is where an implementation has no excuse.
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
measurements with a column of 392 as though they answered the same question. What can be said:

- **For vessel calibre, VascX**, and not by a small margin: 1.1% worst error on vein width against
  18.6% to 56.5% for the AutoMorph group, and 1.7% movement under rotation against their 14% to
  60%. The caveat is scope — VascX yields six judged biomarkers against PVBM's twenty-two, and it
  produced nothing comparable at all on the `straight` shape.
- **For tortuosity, AutoMorphClass**: 8.5% worst on Hart τ1 over every shape and angle, against
  13.7% for its sibling, 31–33% for PVBM and OCULAR and 43% for VascX. It is also the fastest thing
  here, at 0.4 seconds an image. **AutoMorphalyzer is the better choice if the question is broader
  than tortuosity** — it has the higher share of measurements within tolerance overall, 91% against
  89%, and the two disagree about which is ahead depending on what is asked, which is exactly why
  this page does not order them.
- **For breadth, PVBM**, the only implementation that puts twenty canonical biomarkers on the
  table, including the central retinal equivalents and AVR that nothing else here computes. Since
  moving to `GeometryAnalysis` it is also the **steadiest under rotation of any implementation
  here** — 3 of its 32 quantities move by more than 10%, against 8 of 18 for OCULAR and 16 of 18
  for AutoMorph — and its junction count is exact. Two caveats remain, both real: it costs 24
  seconds an image, and it loses its whole geometry block on densely vascularised segmentations
  rather than just the equivalents (section 3).
- **Do not use Grisan density from any AutoMorph implementation.** It is non-zero where the
  geometry requires zero, out by up to 89,966% on the sinusoid, and moves by 231% to 400% when the
  image is turned. Nothing here suggests a threshold at which it becomes usable.
- **Use PVBM's junction count, not OCULAR's** — the reverse of the advice this page gave before
  2026-09-26. PVBM's is exact on every shape and angle since it moved to `GeometryAnalysis`;
  OCULAR's is a modified copy of the class PVBM retired, and is out by up to 85% and unstable by up
  to 240% under rotation. Neither's *endpoint* count answers the catalogued question: PVBM's now
  excludes the end at the disc (section 3.1) and OCULAR's is out by 100%.
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
  when the Koch curve was redrawn, because a shorter skeleton is less work. So treat the **ratios**
  as the finding — PVBM is about ninety times AutoMorphClass, on any run — and treat a figure like
  "36 seconds an image" as describing this machine on one afternoon, against this fixture, rather
  than the program.

---

**Compiled from** [notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb).
