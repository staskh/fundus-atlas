# Synthetic biomarker benchmark — results

One implementation was measured against eight shapes at four angles — **32 renderings, 262
comparable measurements** — on a 2048² grid at 5 µm per pixel, with arteries 80 µm wide, veins
120 µm and an optic disc 1800 µm across. The comparison is with what each
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
6. [The branching angle, which now claims to be nothing](#6-the-branching-angle-which-now-claims-to-be-nothing)
7. [The central retinal equivalents](#7-the-central-retinal-equivalents)
8. [A vessel too long to measure](#8-a-vessel-too-long-to-measure)
9. [A cutoff that a vessel can fall either side of](#9-a-cutoff-that-a-vessel-can-fall-either-side-of)
10. [What these numbers do not say](#10-what-these-numbers-do-not-say)

## 1. Summary

| Implementation | Renderings | Quantities with a known value | Within 2% of it | Largest movement across angles |
| --- | --- | --- | --- | --- |
| [pvbm](../projects/pvbm.md) | 32 | 262 | 144 | 75% |

Of the measurements that could be checked, PVBM lands on the geometry for **area and endpoint
counts**, comes within a few per cent on **the Knudtson equivalents**, and departs from it in five
distinct ways — each with a cause that
reading the source confirms, rather than a discrepancy to be noted and forgotten.

| Finding | Size | Whose |
| --- | --- | --- |
| Tortuosity of a straight vessel rises with its angle to the pixel grid | up to **+7.4%** measured, +7.9% possible | PVBM's |
| Reported length is a sum of chords, not arcs | **−0.1% to −18%**, worst on the curviest shape | PVBM's, and a definition rather than a defect |
| A single junction counted as one, three or four | **up to 300%** | PVBM's |
| Hubbard equivalents are computed from pixel widths with constants fitted in microns | **−73% to −81%** | PVBM's, and dimensional |
| The equivalents crash on a vessel longer than ~1000 skeleton pixels | **no answer on 10 of 32 renderings** | PVBM's |
| Knudtson equivalents are low by about a pixel of vessel width or less | **−1.3% to −6.3%**, worst on the narrower class | the raster's, not PVBM's |

## 2. What PVBM gets exactly right

| Quantity | Comparisons | Worst difference from geometry |
| --- | --- | --- |
| `vessel-area-and-length/area` | 56 — seven shapes, four angles, both classes | **0.29%**, and inside 0.05% on most |
| `junction-counts/endpoints` | 24 — three shapes, four angles, both classes | **exact every time** |

Area is the strongest result on the page, and an endpoint count is exact on a straight vessel, a Y
and four parallel lines alike, for arteries and veins equally.

**The Knudtson equivalents very nearly belong here too.** They are low by 1.3% to 6.3%, on every
shape at every angle, never high — which is what a rasterisation deficit looks like and not what
noise looks like. Knudtson's recursion is linear in the widths, so those percentages *are* the
width deficit: between **0.31 and 1.01 pixels** of width across the four measurements. The mask a
measurement sees is slightly narrower than the vessel that was drawn, and a fixed loss at the
boundary costs a thin vessel proportionally more, which is why the artery — 80 µm against the
vein's 120 — is always the worse of the two.

## 3. A straight vessel that is 7% tortuous

τ1 is arc length over chord length. On a straight vessel the arc **is** the chord, so the answer is
exactly 1 — whatever the vessel's width, length or orientation.

| Angle | PVBM | Geometry requires |
| --- | --- | --- |
| 0° | 1.0007 | 1 |
| 30° | **1.0740** | 1 |
| 60° | **1.0740** | 1 |
| 90° | 1.0003 | 1 |

*Our finding, 2026-09-20:* **that number is derivable, and deriving it says what the implementation
is doing.** Walking a digital straight line at angle θ takes `cos θ − sin θ` orthogonal steps and
`sin θ` diagonal ones per unit of travel; weighting a diagonal as √2 — the naive chain code — gives

`(cos 30° − sin 30°) + √2 sin 30° = 0.366 + 0.707 = 1.0731`

where the truth is 1. The measurement is **1.0740**. PVBM's arc length is a step count, and three
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
| disjoint | −0.02% |
| spokes-disc-centred | −0.10% |
| straight | −0.12% |
| spokes-macula-centred | −0.18% |
| artery-vein-pair | −0.24% |
| bifurcation | −0.70% |
| **arc** | **−9.9%** |
| **sinusoid** | **−18.0%** |

The error grows with how curved the shape is, which is the signature of a chord. PVBM's reported
length is `np.sum(chord)` — the straight-line distances between branch points — rather than the
distance travelled along the vessel.

The arc pins it: for a circular arc of angle θ the chord-to-arc ratio is `2 sin(θ/2) / θ`, which at
90° is **0.900**. A chord sum should therefore read 10.0% short, and PVBM reads 9.9% short.

**This is a definition rather than a defect**, but it is not the definition the name implies — its
own docstring says "the overall length (in pixel)" — and its direction matters: it under-reports
every curved vessel, and the curviest most, which is exactly the direction that would flatten a
difference between a healthy retina and a tortuous one.

## 5. One junction counted four times

The bifurcation shape has exactly one junction.

| Angle | 0° | 30° | 60° | 90° | Geometry |
| --- | --- | --- | --- | --- | --- |
| `junction-counts/junctions` | 4 | 4 | 3 | 1 | **1** |
| `junction-counts/endpoints` | 3 | 3 | 3 | 3 | 3 ✓ |

A skeleton of a Y-shaped vessel has a small cluster of pixels where the branches meet, and each
pixel of that cluster is counted. How many appear depends on how the branches fall on the lattice,
which is why turning the same shape changes the answer.

It is the easiest of these to correct — the cluster is a connected component a few pixels across —
and it propagates: a junction count is an input to branching-angle work and to any measure of how
complicated a network is.

## 6. The branching angle, which now claims to be nothing

PVBM reports **112° to 124°** where the bifurcation's daughters are **60°** apart. That was recorded
here as the largest error on the page, and it was not an error at all — it was this repository's
mapping being wrong.

*Our finding, 2026-09-20, from reading `compute_angles_dictionary`:* at every particular point it
takes **every pair** of connected neighbours and measures the angle between them, then reports the
median of all of them. On a symmetric Y the angles at the junction are 60° between the daughters
and 150° between each daughter and the trunk — so the median of what it collects is nothing like
the angle a reader of "branching angle" expects.

**So the mapping has been withdrawn.** `median_branching_angle` no longer claims to be
`bifurcation-angle/between-daughters`, nothing is compared against it, and no error is charged
against PVBM for it. The column is still measured and stored under PVBM's own name — together with
the mean and the spread it returns from the same call, which this run began keeping — because it is
a real quantity measured consistently. What is missing is a catalogued definition of what it
actually is, and [BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) §3 records that gap.

This is what the shapes are for: a mapping is a claim, and this is the first one a measurement has
overturned.

## 7. The central retinal equivalents

Three families reach the ring these are measured over — the two spokes framings and the artery/vein
pair. Section 2 has the Knudtson numbers: low by about a pixel of width or less, on every shape, in
one direction.

**Hubbard's variant is not a unit conversion away from being right.**

| Quantity | PVBM | Geometry requires | Difference |
| --- | --- | --- | --- |
| `central-retinal-equivalents/hubbard/artery` | 28.3 | 151.7 | **−81.4%** |
| `central-retinal-equivalents/hubbard/vein` | 61.8 | 225.0 | **−72.5%** |
| `avr/hubbard/both` | 0.458 | 0.674 | **−32.2%** |

*Our finding, 2026-09-20, from reading the source:* PVBM computes both variants from **pixel**
widths and accepts no scale at all. Knudtson's recursion is scale-free, so pixels are harmless
there. Hubbard's constants were fitted in microns **and its additive term does not scale**, so
feeding it pixels does not give a micron answer divided by anything: the arteries are out by a
factor of 5.37 and the veins by 3.64 at one and the same 5 µm per pixel. A single scale factor
cannot explain two different factors, which is the arithmetic proof that this is a dimensional
error rather than a unit the caller can convert.

The consequence is concrete: **`crae_hubbard` is not a Hubbard equivalent in pixels awaiting
conversion — it is a different quantity**, and it changes when the camera changes, so two studies
on different cameras cannot compare it even with each other. The AVR built from it is out by 32%,
where the Knudtson AVR is out by 3.8%.

The adapter reproduces all of this rather than correcting it, because a benchmark of corrected code
measures the correction.

### 7.1 The framing does not change the answer

`spokes-macula-centred` and `spokes-disc-centred` are the same retina photographed two ways — the
disc off to one side, as most fundus photography frames it, and in the middle of the frame. Every
disc-anchored measurement should therefore return the same number on both, and every one does:

| Quantity | Macula-centred | Disc-centred |
| --- | --- | --- |
| `central-retinal-equivalents/knudtson/artery` | 26.203 | 26.203 |
| `central-retinal-equivalents/knudtson/vein` | 49.946 | 49.949 |
| `avr/knudtson/both` | 0.5250 | 0.5250 |

**This is a negative result and it is worth having.** A measurement anchored on the disc could
easily have read the framing instead of the eye — by measuring in image coordinates, or by running
out of field of view on one side — and a difference between these two columns is what that would
have looked like. There is none beyond the third decimal place, where the raster differs.

## 8. A vessel too long to measure

***PVBM's central retinal equivalents raise `RecursionError: maximum recursion depth exceeded` on
any vessel whose skeleton is longer than Python's recursion limit — about 1000 pixels.*** They
cost **10 of the 32 renderings** their equivalents: every angle of the straight and sinusoid
families, and half of the artery/vein pair.

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
  the same distance — a diagonal step advances √2. The same vessel skeletonises to **1020 pixels at
  0° and 888 at 30°**, straddling the limit exactly. **The same vessel in the same eye is measurable
  or not according to how the camera was held.**

## 9. A cutoff that a vessel can fall either side of

PVBM keeps only vessels whose subgraph begins within `20 + 2 × radius` pixels of the disc centre.
It is a defensible rule — a central retinal equivalent is about vessels emanating from the disc —
and it is a **hard** cutoff, so a vessel a hair outside it contributes nothing while one a hair
inside contributes fully.

*How we found it:* on an earlier version of the artery/vein pair, drawn when the optic disc was
sized as a fraction of the picture rather than in microns, the threshold came to 265.8 pixels. The
artery's nearest skeleton pixel was 145.3 away and was kept; the vein's was 266.9 away and was
dropped. **It missed by 1.1 pixels**, and PVBM returned nothing for the vein at every angle without
raising anything.

*What this run shows:* with a clinically sized disc — 1800 µm across, so a radius of 180 pixels —
the threshold is 380 pixels, the vein's nearest skeleton pixel is 245, and **both classes are
kept**. The knife edge is no longer being stood on.

Both halves are worth recording. The rule is real and still there; whether a vessel falls the wrong
side of it depends on the disc radius, which on a real photograph is itself an estimate from another
model. This is a shape-found illustration of a sensitivity, not a claim that any published PVBM
result is wrong.

## 10. What these numbers do not say

- **Nothing about photographs.** Every shape here is clean, binary and noiseless. An implementation
  that measures a synthetic vessel exactly may still fail on a segmentation of a real eye, where the
  mask has holes, specks and a boundary nobody agrees on.
- **Nothing about which implementation to use**, there being one. The comparison this benchmark
  exists to make needs a second, and the naming table is built to take one as a column.
- **Nothing about the quantities no shape defines.** PVBM returns 32 columns and 16 of them can be
  checked. The rest are recorded in `results/` and compared against nothing, for three different
  reasons that this page keeps apart: the catalogue has no name for it (perimeter, singularity
  length, the three branching-angle statistics), or it has a name and no shape pins a value (the
  three fractal dimensions), or the shape states a value over the vessels as one class where PVBM
  measures each class separately. A shape with a known fractal dimension would be worth adding.
- **Nothing about a scale conversion**, since PVBM ignores the figure entirely.
- **Nothing about speed as a property of the software.** A rendering took about 250 seconds here,
  but that figure is close to meaningless: the eight shapes were measured **in parallel on eight
  cores**, so each was competing with seven others for the machine. The honest statement is that
  every family now costs roughly twice what it did, because every family now carries both classes
  and PVBM's multifractal analysis runs once per class.
- **Nothing that selects.** No implementation passes or fails here. The 2% in section 1 is a way of
  summarising 262 numbers in one, not a standard anybody agreed.

---

**Compiled from `notebooks/biomarker-synthetic.ipynb` on:** 2026-09-21 · **Measured by**
`python -m benchmarks --benchmark biomarker-synthetic`
