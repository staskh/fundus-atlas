# Synthetic biomarker benchmark — results

One implementation was measured against seven shapes at four angles — **28 renderings, 138
comparable measurements** — on a 2048² grid at 5 µm per pixel. The comparison is with what each
shape's geometry requires, not with another program: a straight vessel has a tortuosity of exactly
1, and an implementation that says otherwise is wrong rather than different.

Every number here comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb). How the benchmark
is configured is a separate page: [biomarker-synthetic-docs.md](biomarker-synthetic-docs.md), and
the shapes with their derivations are in
[the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb).

**1 of 1 declared implementations** took part. [PVBM](../projects/pvbm.md) is the first; the naming
table is built so a second adds a column rather than a rewrite.

***This benchmark selects nothing.*** Which implementations are fit to measure a real segmentation
is a judgement made by a person on this evidence. There is no pass mark here, and the 2% used below
to call a measurement "agreeing" is a reporting convenience rather than a standard. The movement
column is the widest spread one quantity showed across the four angles, as a fraction of its largest
value — the junction count, which reads 4, 3, 1, 4 on one unchanged shape.

## Contents

1. [Summary](#1-summary)
2. [What PVBM gets exactly right](#2-what-pvbm-gets-exactly-right)
3. [A straight vessel that is 7% tortuous](#3-a-straight-vessel-that-is-7-tortuous)
4. [A length that is a sum of chords](#4-a-length-that-is-a-sum-of-chords)
5. [One junction counted four times](#5-one-junction-counted-four-times)
6. [Where the disagreement is ours](#6-where-the-disagreement-is-ours)
7. [The central retinal equivalents](#7-the-central-retinal-equivalents)
8. [A vessel too long to measure](#8-a-vessel-too-long-to-measure)
9. [A vein excluded by one pixel](#9-a-vein-excluded-by-one-pixel)
10. [What these numbers do not say](#10-what-these-numbers-do-not-say)

## 1. Summary

| Implementation | Renderings | Quantities with a known value | Within 2% of it | Largest movement across angles |
| --- | --- | --- | --- | --- |
| [pvbm](../projects/pvbm.md) | 28 | 138 | 76 | 75% |

Of the measurements that could be checked, PVBM lands on the geometry for **area, endpoint counts
and the Knudtson equivalents**, and departs from it in five distinct ways — each with a cause that
reading the source confirms, rather than a discrepancy to be noted and forgotten.

| Finding | Size | Whose |
| --- | --- | --- |
| Tortuosity of a straight vessel rises with its angle to the pixel grid | up to **+7.3%** measured, +7.9% possible | PVBM's |
| Reported length is a sum of chords, not arcs | **−0.5% to −18%**, worst on the curviest shape | PVBM's, and a definition rather than a defect |
| A single junction counted as one, three or four | **up to 300%** | PVBM's |
| Hubbard equivalents are computed from pixel widths with constants fitted in microns | **−76% to −80%** | PVBM's, and dimensional |
| The equivalents crash on a vessel longer than ~1000 pixels | **no answer on 4 of 7 shapes** | PVBM's |
| Branching angle reads ~120° where the daughters are 60° apart | — | **ours**: the canonical name does not describe its column |

## 2. What PVBM gets exactly right

| Quantity | Shapes | Worst difference from geometry |
| --- | --- | --- |
| `area` | straight, arc, sinusoid, disjoint | **0.1%** |
| `endpoints` | straight, bifurcation, disjoint | **exact at every angle** |
| `intersections` | straight, disjoint (no junctions) | **exact at every angle** |
| `crae`/`crve` (Knudtson) | disc-spokes, artery-vein-pair | **−3.8%**, always low |
| `avr` (Knudtson) | disc-spokes | **+0.8%** |

Area is the strongest result on the page: four shapes, four angles each, never worse than a tenth
of a per cent, and the residue is the boundary pixels a raster cannot avoid. An endpoint count is
exact on a straight vessel, a Y and four parallel lines alike.

**The Knudtson equivalents are the substantive agreement.** The recursion is the hardest arithmetic
in this benchmark — six widths, paired widest-with-narrowest, folded repeatedly — and PVBM tracks
it to within four per cent on both classes and to within one per cent on their ratio:

| Shape | Quantity | PVBM | Geometry requires | Difference |
| --- | --- | --- | --- | --- |
| disc-spokes | `crae_knudtson` | 41.66 | 42.97 | **−3.1%** |
| disc-spokes | `crve_knudtson` | 67.40 | 70.05 | **−3.8%** |
| disc-spokes | `avr_knudtson` | 0.618 | 0.613 | **+0.8%** |
| artery-vein-pair | `crae_knudtson` | 35.95 | 36.86 | **−2.5%** |

The residue is a width measurement: PVBM measures each vessel's calibre from the mask, and a mask
is a pixel or so narrower than the shape that was drawn. It is low on every shape at every angle,
which is what a rasterisation deficit looks like and not what noise looks like. **The ratio is
better than either number it is made of**, the two deficits being in the same direction — which is
an argument for the ratio and not for the calibres.

## 3. A straight vessel that is 7% tortuous

τ1 is arc length over chord length. On a straight vessel the arc **is** the chord, so the answer is
exactly 1 — whatever the vessel's width, length or orientation.

| Angle | PVBM | Geometry requires |
| --- | --- | --- |
| 0° | 1.000 | 1 |
| 30° | **1.073** | 1 |
| 60° | **1.073** | 1 |
| 90° | 1.000 | 1 |

*Our finding, 2026-09-20:* **that number is derivable, and deriving it says what the implementation
is doing.** Walking a digital straight line at angle θ takes `cos θ − sin θ` orthogonal steps and
`sin θ` diagonal ones per unit of travel; weighting a diagonal as √2 — the naive chain code — gives

`(cos 30° − sin 30°) + √2 sin 30° = 0.366 + 0.707 = 1.0731`

where the truth is 1. The measurement is **1.0730**. PVBM's arc length is a step count, and three
things follow:

- **The bias is zero at 0°, 45° and 90°** and largest near 26.6°, where it reaches 7.9%. A test at
  axis-aligned angles alone would have found nothing at all.
- **It is always upward.** A straight vessel is never reported as straighter than straight.
- **It does not average away.** A bias is not noise, so a study of many vessels carries it intact,
  and a comparison between two groups is safe only if their vessels are oriented alike — an
  assumption nobody states because nobody knows they are making it.

In plain terms: **the tortuosity PVBM reports depends on how the eye happened to sit in the
camera.** Two photographs of one retina, one of them rotated, give different numbers.

## 4. A length that is a sum of chords

Each figure is the mean across the shape's four angles.

| Shape | PVBM's length against geometry |
| --- | --- |
| straight | −0.5% |
| disjoint (four straight lines) | −0.5% |
| artery-vein-pair | −0.5% |
| disc-spokes | −1.0% |
| bifurcation | −1.1% |
| **arc** | **−10.6%** |
| **sinusoid** | **−18.3%** |

The error grows with how curved the shape is, which is the signature of a chord. PVBM's reported
length is `np.sum(chord)` — the straight-line distances between branch points — rather than the
distance travelled along the vessel.

The arc pins it: for a circular arc of angle θ the chord-to-arc ratio is `2 sin(θ/2) / θ`, which at
90° is **0.900**. A chord sum should therefore read 10.0% short, and PVBM reads 10.6% short, the
remainder being the segment ends its walk discards.

**This is a definition rather than a defect**, but it is not the definition the name implies — its
own docstring says "the overall length (in pixel)" — and its direction matters: it under-reports
every curved vessel, and the curviest most, which is exactly the direction that would flatten a
difference between a healthy retina and a tortuous one.

## 5. One junction counted four times

The bifurcation shape has exactly one junction.

| Angle | 0° | 30° | 60° | 90° | Geometry |
| --- | --- | --- | --- | --- | --- |
| `intersections` | 4 | 3 | 1 | 4 | **1** |
| `endpoints` | 3 | 3 | 3 | 3 | 3 ✓ |

A skeleton of a Y-shaped vessel has a small cluster of pixels where the branches meet, and each
pixel of that cluster is counted. How many appear depends on how the branches fall on the lattice,
which is why turning the same shape changes the answer.

It is the easiest of these to correct — the cluster is a connected component a few pixels across —
and it propagates: a junction count is an input to branching-angle work and to any measure of how
complicated a network is.

## 6. Where the disagreement is ours

PVBM reports **112° to 124°** where the bifurcation's daughters are **60°** apart. That is the
largest apparent error on this page and it is not an error.

*Our finding, 2026-09-20, from reading `compute_angles_dictionary`:* at every particular point it
takes **every pair** of connected neighbours and measures the angle between them, then reports the
median of all of them. On a symmetric Y the angles at the junction are 60° between the daughters
and 150° between each daughter and the trunk — so the median of what it collects is nothing like
the angle a reader of "branching angle" expects.

**So the canonical name `bifurcation-angle/between-daughters` does not describe PVBM's column**, and
the mapping in [BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) is marked contradicted. The shape found
that, which is what the shapes are for: a mapping is a claim, and this is the first one a
measurement has overturned.

## 7. The central retinal equivalents

The two variants behave completely differently, and section 2 has already given the Knudtson
numbers: within four per cent on both classes, within one on their ratio.

**Hubbard's variant is not a unit conversion away from being right.**

| Shape | Quantity | PVBM | Geometry requires | Difference |
| --- | --- | --- | --- | --- |
| disc-spokes | `crae_hubbard` | 45.8 | 233.2 | **−80.4%** |
| disc-spokes | `crve_hubbard` | 73.7 | 304.8 | **−75.8%** |
| disc-spokes | `avr_hubbard` | 0.622 | 0.765 | **−18.8%** |

*Our finding, 2026-09-20, from reading the source:* PVBM computes both variants from **pixel**
widths and accepts no scale at all. Knudtson's recursion is scale-free, so pixels are harmless
there. Hubbard's constants were fitted in microns **and its additive term does not scale**, so
feeding it pixels does not give a micron answer divided by anything: the arteries are out by a
factor of 5.09 and the veins by 4.13 at one and the same 5 µm per pixel. A single scale factor
cannot explain two different factors, which is the arithmetic proof that this is a dimensional
error rather than a unit the caller can convert.

The consequence is concrete: **`crae_hubbard` is not a Hubbard equivalent in pixels awaiting
conversion — it is a different quantity**, and it changes when the camera changes, so two studies
on different cameras cannot compare it even with each other. The AVR built from it inherits this
and is out by 19%, where the Knudtson AVR is out by 0.8%.

The adapter reproduces all of this rather than correcting it, because a benchmark of corrected code
measures the correction.

## 8. A vessel too long to measure

***PVBM's central retinal equivalents raise `RecursionError: maximum recursion depth exceeded` on
any vessel whose skeleton is longer than Python's recursion limit — about 1000 pixels.*** They
returned no answer at all on **four of the seven shapes**, and on the artery/vein pair at two of its
four angles.

*Our finding, 2026-09-20.* `compute_central_retinal_equivalents` walks each vessel with
`tree.recursive_reg`, which calls itself **once per skeleton pixel**. The straight shape's artery
skeletonises to **1220 pixels** against a default limit of **1000**, and the call dies. Raising the
limit to 50,000 and changing nothing else makes the same call return 40.0, which is the test of the
diagnosis.

Three things follow, and the third is the one that matters clinically:

- **It is a function of image size, not of the retina.** The same vessel measured on a 512-pixel
  frame skeletonises to 400 pixels and is measured without complaint. Anyone running PVBM on a
  modern 2048-pixel photograph is nearer this cliff than anyone running it on the small images its
  examples use.
- **It fails loudly**, raising rather than returning a wrong number — which is much the better of
  the two failure modes, and is why this is reported as a limit rather than as a silent corruption.
- **Whether it happens depends on the orientation.** On the artery/vein pair the equivalents die at
  0° and 90° and succeed at 30° and 60°, because a tilted digital line spends fewer pixels covering
  the same distance — a diagonal step advances √2. **The same vessel in the same eye is measurable
  or not according to how the camera was held.**

## 9. A vein excluded by one pixel

On the artery/vein pair, PVBM measured the artery and returned nothing for the vein — at every
angle, with no error raised.

*Our finding, 2026-09-20, from reading the source and then measuring it:* PVBM keeps only vessels
whose subgraph begins within `20 + 2 × radius` pixels of the disc centre. On this shape that
threshold is **265.8 pixels**. The artery's nearest skeleton pixel is **145.3** away and is kept;
the vein's is **266.9** away and is dropped.

**The vein misses by 1.1 pixels.** The rule itself is defensible — a central retinal equivalent is
about vessels emanating from the disc — but a hard cutoff means a vessel a hair outside it
contributes nothing while one a hair inside contributes fully. On a real photograph, where the disc
radius is itself an estimate from another model, a vessel near the boundary is in or out according
to a number nobody measured precisely. This is a shape-found illustration of a sensitivity, not a
claim that any published PVBM result is wrong.

## 10. What these numbers do not say

- **Nothing about photographs.** Every shape here is clean, binary and noiseless. An implementation
  that measures a synthetic vessel exactly may still fail on a segmentation of a real eye, where the
  mask has holes, specks and a boundary nobody agrees on.
- **Nothing about which implementation to use**, there being one. The comparison this benchmark
  exists to make needs a second, and the naming table is built to take one as a column.
- **Nothing about the quantities no shape defines.** PVBM's three fractal dimensions, its
  singularity length and its perimeter are computed and recorded in `results/` on every shape, and
  **not one of them is compared here**, because no shape in the library pins a value they could be
  compared against. A shape with a known fractal dimension would be worth adding.
- **Nothing about a scale conversion**, since PVBM ignores the figure entirely.
- **Nothing about speed as a property of the software.** A rendering took 26–56 seconds on this
  machine, the two disc-centred shapes being the slow ones because only they run the equivalents.
- **Nothing that selects.** No implementation passes or fails here. The 2% in section 1 is a way of
  summarising 138 numbers in one, not a standard anybody agreed.

---

**Compiled from `notebooks/biomarker-synthetic.ipynb` on:** 2026-09-20 · **Measured by**
`python -m benchmarks --benchmark biomarker-synthetic`
