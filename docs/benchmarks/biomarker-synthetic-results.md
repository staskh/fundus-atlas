# Synthetic biomarker benchmark — what came out

Seven biomarker implementations were run over the same **91 renderings**: thirteen drawn shapes at
seven angles each, every 15° from 0° to 90°. Each is drawn on a 2048² grid spanning a 45° field of
12,960 µm, so 6.33 µm per pixel. Arteries are 80 µm wide, veins 120 µm, and the optic disc is
1,800 µm across. Nothing here was photographed and nothing was annotated: every shape was *drawn*
from equations, so what it ought to measure follows from arithmetic rather than from anybody's
opinion.

Every number on this page comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb). How the benchmark
is configured is a separate page, [biomarker-synthetic-docs.md](biomarker-synthetic-docs.md), and
the shapes with their derivations are in
[the shapes page](biomarker-synthetic-shapes.md) and
[the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb).

**All seven are on this page together, and that is the point.** The question is whether these
programs compute the same quantity, and that question lives across a row — one biomarker, seven
columns. The columns stand in **lineage order**: [PVBM](../projects/pvbm.md) and
[OCULAR](../projects/ocularnet.md), which imports PVBM's helpers at runtime; then
[AutoMorph](../projects/automorph.md) and its two descendants,
[AutoMorphalyzer](../projects/automorphalyzer.md) and
[AutoMorphClass](../projects/automorphclass.md); then [VascX](../projects/vascx.md), which shares
code with none of them; and last [fundus-biomarkers](../projects/fundus-biomarkers.md), Pheno's own
reference implementation, which shares code with none of them either and whose owner is also this
atlas's owner — its numbers are published like everybody's and are **not independently verified**
(section 10). A difference **between neighbours** is a change somebody made on purpose; a
difference **across a boundary** is two independent readings of the same definition.

> **Every number on this page was re-measured from scratch on 2026-11-10**, against a rebuilt
> store, and they replace the 2026-10-21 set, which was 36 renderings: nine shapes at four angles,
> at 5 µm per pixel. The shapes are now stated in microns on a
> model camera and carry far more ground truth: up to 925 values per shape where there were 273,
> over zones B and C as well as the whole field, each marked with how it is known — and, for the
> first time, the values the geometry says **do not exist**. Section 11 says what that added and
> what it changed. Several conclusions moved, and each section says where.
>
> **PVBM measures with `GeometryAnalysis`**, from 2026-09-26, and **every catalogued number is in
> microns**, from 2026-09-30 — sections 3.1 and 9 are the history of both.

## Contents

1. [Summary](#1-summary)
2. [What could be compared, and what could not](#2-what-could-be-compared-and-what-could-not)
3. [What raised: AutoMorphalyzer, on vessels that never reach the disc](#3-what-raised-automorphalyzer-on-vessels-that-never-reach-the-disc)
4. [Turning the picture changes the answer](#4-turning-the-picture-changes-the-answer)
5. [Disagreement with the geometry](#5-disagreement-with-the-geometry)
6. [The Koch curve, redrawn](#6-the-koch-curve-redrawn)
7. [Which to reach for, and at what question](#7-which-to-reach-for-and-at-what-question)
8. [What these numbers do not say](#8-what-these-numbers-do-not-say)
9. [What changed, and what it did not](#9-what-changed-and-what-it-did-not)
10. [fundus-biomarkers, the seventh implementation](#10-fundus-biomarkers-the-seventh-implementation)
11. [The shapes rebuilt in microns, with every value they settle](#11-the-shapes-rebuilt-in-microns-with-every-value-they-settle)

## 1. Summary

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx | fundus-biomarkers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Biomarkers produced | 30 | 18 | 18 | 54 | 18 | 20 | 633 |
| …matching a canonical name | 20 | 10 | 15 | 23 | 15 | 6 | 633 |
| Comparable measurements | 1,748 | 882 | 1,344 | 1,763 | 1,344 | **153** | 47,203 |
| Median disagreement | 4.9% | 0.0% | 8.6% | 6.4% | 6.7% | **0.0%** | **0.0%** |
| Within 25% of the geometry | 93% | **97%** | 78% | 78% | 81% | 91% | 92% |
| Quantities that move when the image turns | 24 / 30 | 13 / 18 | 16 / 18 | 23 / 40 | 10 / 18 | **8 / 20** | 139 / 629 |
| Biomarkers disagreeing with the geometry | 15 / 20 | 4 / 10 | 11 / 15 | 12 / 23 | 7 / 15 | 2 / 6 | 168 / 629 |
| Exceptions | 0 | 0 | 0 | **28** | 0 | 0 | 0 |
| Seconds per image | **62.7** | 4.7 | 1.7 | 6.7 | **1.2** | 5.0 | 8.2 |

**Every figure here is taken against a noise floor of 1% of the biomarker's own size**, meaning the
largest value the shapes require of it anywhere in the store. A difference smaller than that counts
as agreement, and no percentage is divided by anything smaller. It is a deliberately high floor:
these shapes are drawn onto a pixel lattice and skeletonised, and below that quantisation a
percentage compares two noises.

*The floor was an absolute 0.01 until 2026-09-30, when it stopped working.* Once every canonical
length became physical, this benchmark's quantities came to span an area of about 250,000 µm² and a
squared curvature of about 10⁻⁸ /µm², and one constant cannot be a noise floor for both.

**The floor exposed a defect in our own ground truth on this run, now fixed.** A standard deviation
over values that are equal — the Hart τ1 of six identical spokes — was stored as about 10⁻¹⁶ of
floating-point rounding rather than as 0. That made the biomarker's own size 10⁻¹⁶, its floor 10⁻¹⁸,
and an honest answer of 0.000001 a "66,522,575,148,840%" fault. The truth now stores an exact 0 when
the values are equal to rounding, and a test holds it there; the figures on this page are after
that fix, which moved fundus-biomarkers from 174 disagreeing biomarkers to 168 and touched no other
column.

**Read this table down a column, not across a row.** The accuracy rows are not a score and the
columns are not ranked by them, because the columns are not answering the same question: VascX's
0.0% median is over **153** measurements of six biomarkers, and PVBM's 4.9% is over **1,748** of
twenty. Measuring less, more carefully, is a defensible engineering choice and it is not the
same achievement as measuring more. Section 7 says what can actually be concluded.

**Every row moved from the 2026-10-21 page, and the reason is the shapes rather than the programs.**
Four more shapes, three more angles and values over zones B and C put more of each
implementation's output in front of a truth, and the shapes added — a clothoid, a tree, a spur and
a crossing — include the hardest here. Two shifts stand out.
**Agreement fell for the AutoMorph group**, from 80–92% within 25% to 78–81%, and the worst of
it is calibre on the new `crossing` and `spur` (section 5). **Rotation
moved PVBM from 9 of 30 to 24 of 30** — with seven angles instead of four a spread has more chances
to show, and nothing about PVBM changed.

PVBM takes about **fifty times** longer per image than AutoMorphClass — 62.7 seconds against 1.2.
The timings are the one figure here that does not reproduce (section 8), but the ratio does.

## 2. What could be compared, and what could not

Three different things stand between a quantity a program computes and a number this benchmark can
judge, and the counts above only mean something once they are kept apart:

- **The catalogue may have no name for it.** AutoMorphalyzer returns 17 quantities with no
  canonical name — `average_local_calibre` at every zone, `tortuosity_density` and
  `tortuosity_distance` at zone C, and two Knudtson equivalents at zone C. VascX returns 14,
  PVBM 10, OCULAR 8, AutoMorph and AutoMorphClass 3 each, fundus-biomarkers none. These are
  measured and stored under the implementation's own name and appear in **no** comparison, because
  a canonical name exists to make two numbers comparable and there is nothing yet to compare them
  with. The notebook's section 1.1 lists them by name.
- **No shape may settle it.** *This used to be the bigger gap and it has nearly closed.* The
  2026-10-21 page judged 194 canonical biomarkers; this one judges **638**, because the rebuilt
  truth settles every value over zones B and C as well as the field, over the artery-and-vein
  union the vocabulary calls `vessels`, and under every pooling statistic. AutoMorphalyzer's zone-B
  columns, which section 2 used to say were "judged against nothing", now are judged, and so are its
  zone-B Knudtson equivalents.
- **The program may simply never answer.** AutoMorphalyzer returns 54 columns of which 40 ever
  carry a value; fundus-biomarkers returns 633 of which 630 do — the three cup-to-disc ratios stay
  empty, since no shape hands it a cup.

## 3. What raised: AutoMorphalyzer, on vessels that never reach the disc

*This section was called "Nothing raised, once PVBM was given the same recursion limit as its
fork", and that was true of the 2026-10-21 run. It is no longer true of the benchmark, so the
heading changed; the question it answers — what raised, and why — is the same.*

**AutoMorphalyzer raised 28 times, all on `disjoint`, at every one of the seven angles.** Each
of its three measuring calls — artery, vein and the two together — raises
`ZeroDivisionError('division by zero')`, and the whole rendering is lost with them, including the
field-wide values that did not need a zone. Nothing else raised anywhere.

`disjoint` is the shape whose parallel vessels never reach the optic disc, and as redrawn it puts
nothing inside zone B or zone C at all — a fact the ground truth now records as *no value* for
every zone biomarker (section 11). The likeliest reading is that AutoMorphalyzer divides by the
count of what it found in a zone rather than declining when the zone is empty. *That is our reading
of the traceback's shape and has not been traced through its code.* It is the right kind of shape
to have found it with: a real photograph with a disc misplaced, or a crop that cuts the zone off,
asks the same question.

**PVBM still raises nothing**, at the same recursion limit as OCULAR's fork. The history of that is
below, kept because it is what the benchmark learned about a program that fails on the hard cases
and looks steady on the rest:

PVBM's geometry walks each vessel tree with mutual recursion — one Python frame per skeleton pixel
— so the depth it needs is a function of how much vessel there is. At CPython's default limit of
1000 it raised on the two densest shapes, `koch` and `deep-bifurcation`, losing the whole geometry
call at every angle. OCULAR never raised, and not because it measures differently: its fork sets
`sys.setrecursionlimit(5000)` at module import, and PVBM does not. From 2026-09-26 this atlas raises
the limit to the same 5000 around PVBM's call, puts it back afterwards, and declares the number.
PVBM's apparent steadiness before then — 3 of 30 quantities moving under rotation — was steadiness
over the shapes it could still measure, and was withdrawn.

### 3.1 PVBM's measuring class changed, and it is not a rename

*The figures in this subsection are as they stood on 2026-09-26, when the class changed; section
3.2 has the current ones.*

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

### 3.2 PVBM and OCULAR return the same numbers

With the recursion limit equalised, **every canonical biomarker the two share comes back
identical** — not close, identical, on all 91 renderings:

| Biomarker | PVBM | OCULAR |
| --- | --- | --- |
| `topology/junctions/artery`, worst error | 4,286% | 4,286% |
| `topology/junctions/vein`, worst error | 5,714% | 5,714% |
| `tortuosity/hart-tau1/artery/median`, worst error | 15.0% | 15.0% |
| `tortuosity/hart-tau1/vein/median`, worst error | 30.4% | 30.4% |
| …the artery junctions and τ1 under rotation | 210%, 19.0% | 210%, 19.0% |

*The junction figures were 42.9% and 85.7% on the 2026-10-21 page, and they are not worse
measurements.* Both are on `koch`, a single curve with no junction at all, where PVBM and OCULAR
count three or four — the spurs a skeleton leaves at a 60° corner. The geometry requires nought, so
the percentage is taken against the noise floor and reads as *how many floors out*; the values,
4 against 0, are the finding (section 5).

**OCULAR's extra column has a catalogued name**, `tortuosity/hart-tau1/<structure>/length-weighted`.
It is 9.5% out at worst on veins against the shared median's 30.4%, so on veins the arc-weighted
mean is still the better of OCULAR's two answers; on arteries it is now 23.9% against 15.0%, and
the advantage is gone.

OCULAR's geometry is a fork of the same `GeometryAnalysis`, 343 of its 486 lines identical, and its
edits are a raised recursion limit, one extra returned quantity, a `try`/`except` around the tree
walk and an optional iterative replacement that is off by default. **None of those change a shared
number**, and the pair is therefore a **control**: if a future change moves one and not the other,
the change is in the fork rather than in the measurement.

## 4. Turning the picture changes the answer

The same shape is drawn again at each angle in continuous coordinates, never by turning a picture,
so the geometry at 30° is *identical* to the geometry at 0°. **Any spread at all is the
implementation or the pixel grid beneath it** — and this check needs no ground truth, which is why
it is also the only check the unnamed quantities of section 2 ever get.

181 of 641 canonical biomarkers move by more than 10% somewhere, over seven angles where there were
four. The worst of it, as the widest spread on any one shape:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx | fundus-biomarkers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/grisan-density/vein/…` | — | — | 700.0% | 241.3% | 265.4% | — | 0.8% |
| `tortuosity/hart-tau1/artery/…` | 19.0% | 12.9% | 449.4% | 11.9% | 10.0% | 12.8% | 0.0% |
| `topology/junctions/artery` | 210.0% | 210.0% | — | — | — | — | 0.0% |
| `calibre/width/vein/length-weighted` | — | — | 48.8% | 33.4% | 37.5% | **1.9%** | 2.2% |
| `density/box-counting/artery` | — | — | 24.9% | 7.1% | 8.9% | — | 8.1% |

Three findings, each legible only because the columns are ordered by lineage:

- **Within the AutoMorph group, the descendants fixed their ancestor's tortuosity and inherited its
  Grisan density.** AutoMorph's Hart τ1 moves by 449% on a shape that did not change;
  AutoMorphalyzer's and AutoMorphClass's by 10–12%. Grisan density is the part nobody touched, and
  all three move by 241% to 700% on it.
- **The box-counting finding reversed.** The 2026-10-21 page reported the descendants *less*
  stable than AutoMorph on box-counting dimension, 80.7% and 80.8% against 20.1%, and concluded that
  something one of them changed made it unstable. On the rebuilt store they are the steadier ones —
  7.1% and 8.9% against 24.9%. Nothing in their code changed; the shapes did, and that conclusion is
  withdrawn rather than explained.
- **Across the boundary, VascX and fundus-biomarkers are steadiest on calibre** — 1.9% and 2.2% on
  vein width where the AutoMorph group is at 33% to 49%. fundus-biomarkers is the steadiest on
  tortuosity too, at 0.0% on Hart τ1, but section 10 is where it moves most.

The unnamed quantities are no better, and nothing else checks them. AutoMorphalyzer's
`tortuosity_density` at zone C moves by **350%**; AutoMorph's `squared_curvature_tortuosity` by
**697%** and AutoMorphClass's by **285%**; VascX's own `lw_tort_curv` columns — dimensionless, and
normalised by a fovea this repository supplies (§9.6) — by **494%**.

## 5. Disagreement with the geometry

54,437 measurements have a theoretical value to be judged against, over 638 canonical biomarkers;
191 of the 638 are out by more than 25% somewhere. The worst case each implementation produced over
all shapes and all angles, for the rows the earlier page carried and the zone values it could not:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx | fundus-biomarkers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `calibre/CRE-knudtson/artery/B` | 28.5% | — | — | 52.3% | — | **2.9%** | 5.1% |
| `calibre/CRE-knudtson/vein/B` | 30.4% | — | — | 67.4% | — | **2.4%** | 2.0% |
| `calibre/CRE-hubbard/vein/B` | 55.8% | — | — | — | — | — | 2.3% |
| `calibre/AVR-hubbard/both/B` | 47.0% | — | — | — | — | — | 3.0% |
| `calibre/width/artery/length-weighted` | — | — | 71.3% | 67.7% | 71.2% | **2.7%** | 5.1% |
| `calibre/width/vein/length-weighted` | — | — | 32.7% | 40.3% | 46.9% | **2.2%** | 2.1% |
| `tortuosity/hart-tau1/vein/…` | 30.4% | 9.5% | 1,225.7% | 14.6% | **8.6%** | 43.4% | 15.5% |
| `density/box-counting/artery` | — | — | 23.1% | 22.2% | 22.2% | — | 48.2% |
| `tortuosity/grisan-density/vein/…` | — | — | 16,458,731% | 17,136,413% | 332,512% | — | 8.8% |

**The central retinal equivalents are settled by the spokes.** Six vessels per class leave the disc, every one the same width, so every pairing order Knudtson's
or Hubbard's method could take agrees. On them PVBM's Knudtson equivalents are 13.5% out at both
framings and its Hubbard venular equivalent **55.8%** — the mechanism of §9.2, Hubbard's +450 µm
venular constant applied to pixel widths, now on a shape built to test it. AutoMorphalyzer's
Knudtson equivalents are 2.9% and 3.6% on the spokes and 52–67% on `deep-bifurcation`, where several
vessels share a zone at different widths.

**Calibre on `crossing` is where the AutoMorph group fails most.** One artery passes over another,
and all three read the length-weighted artery width 68–71% out there, against 2–18% on the smooth
shapes. VascX returns no comparable width there; fundus-biomarkers reads 5.1%.

**The Grisan figures are against a truth of exactly nought** — a curve that bends one way
throughout has no inflections — so the percentage is taken against the noise floor. Read the values:

| | truth | AutoMorph | AutoMorphalyzer | AutoMorphClass | fundus-biomarkers |
| --- | --- | --- | --- | --- | --- |
| Grisan density on `straight` or `arc`, worst, per µm | 0 | 0.151 | 0.158 | 0.0031 | 0 |
| …as its own returned figure, per px | 0 | 0.958 | 0.998 | 0.019 | 0 |

AutoMorph and AutoMorphalyzer return roughly `(n−1)/n`, retipy's documented departure from Grisan's
formula, and on a shape with one turn curve that is about 1 rather than about 0. AutoMorphClass is
about fifty times closer, which is still wrong. *The per-µm figures are smaller than the 0.19 and
0.20 the earlier page gave because the scale changed from 5 to 6.33 µm per pixel; the returned
figures did not change.*

Reading one shape at a time (notebook §4.1):

- On **`straight`**, AutoMorph's Hart τ1 reads 1.0 at 0°, 45° and 90° and **0.0 at 15°, 30°, 60°
  and 75°** — an impossible value, since arc over chord cannot fall below 1. Its vessel detector
  finds nothing long enough on the off-axis renderings and it reports the empty sum rather than
  declining. That one behaviour is most of its 449% rotation spread.
- On **`koch`**, a single curve, PVBM and OCULAR report 3 or 4 junctions where there are none —
  the spurs a skeleton leaves at a 60° corner.
- On **`deep-bifurcation`**, PVBM's Knudtson artery equivalent is 28.5% out, its worst anywhere.

## 6. The Koch curve, redrawn

The shape exists to pin a **fractal dimension**: every other shape here is smooth, and a smooth
curve's dimension is exactly 1, which no box count returns from a bounded raster. A Koch curve's is
`log 4 / log 3` ≈ 1.2619, stored as `asymptotic` because no finite raster reaches it.

*Before 2026-09 it was drawn at four generations, finer than the vessel painted along it, and the
picture did not carry the value derived beside it; every implementation was charged with the
difference.* It is now drawn at two generations and half the usual width, which the rebuilt store
keeps.

**Mean Hart τ1 over the seven angles, against the derived 1.778:**

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx | fundus-biomarkers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Mean τ1 on `koch`, arteries | 1.699 | 1.723 | 1.228 | 1.549 | 1.682 | 1.061 | 1.506 |
| Against 1.778 | −4% | **−3%** | −31% | −13% | −5% | −40% | −15% |

PVBM's and OCULAR's figures are their median and length-weighted columns respectively, which is why
the two differ here and nowhere else.

**VascX returns about 1.06 on a curve whose truth is 1.78** — within a few percent of calling it a
straight line — and AutoMorph's 1.23 is little better. Every implementation
undershoots, and the reason is not a bug in any of them: skeletonising a curve with 60° corners
leaves short spurs, and an implementation that prunes them before measuring gets a shorter arc. So
the **ordering** is more trustworthy than the absolute percentages.

The box-counting dimension on this shape is the one place the AutoMorph group and fundus-biomarkers
trade places: fundus-biomarkers reads within 5.6% here and 30–48% on every smooth shape, while the
AutoMorph group is 22–23% out here and better elsewhere (section 10).

## 7. Which to reach for, and at what question

There is no best implementation here, and pretending otherwise would mean comparing a column of 153
measurements with a column of 1,748 as though they answered the same question. What can be said:

- **For vessel calibre, VascX**: 2.7% and 2.2% worst error on the length-weighted artery and vein
  widths, and 2.9% and 2.4% on the zone-B Knudtson equivalents, against 33% to 71% for the AutoMorph
  group and 28% to 56% for PVBM's equivalents. It moves by 1.9% under rotation. The runner-up is
  fundus-biomarkers, within a few points on every one of those (5.1%, 2.1%, 5.1%, 2.0%) — close
  enough that it is not a margin, and **not independently verified** (section 10). The caveat is
  scope: VascX yields six judged biomarkers, and a comparable calibre only on `deep-bifurcation` and
  the two spoke shapes.
- **For the central retinal equivalents with Hubbard's formula, not PVBM.** It is the only one of
  the six independent implementations that computes them, and it is 55.8% out on the venular one
  on the shape built to settle it, for the documented reason that it applies Hubbard's micron
  constants to pixel widths. Knudtson's version, which is scale-free, is the safer choice from any
  of them.
- **For tortuosity, AutoMorphClass**: 8.6% and 9.5% worst on length-weighted Hart τ1 over every
  shape and angle, 10% under rotation, and the fastest thing here at 1.2 seconds an image. OCULAR's
  length-weighted column is level on veins (9.5%) and no longer on arteries (23.9%).
  AutoMorphalyzer is 14.6–17%, fundus-biomarkers 15.5%, PVBM's and OCULAR's median 15.0–30.4%,
  VascX 43%. *The earlier page put AutoMorphClass and OCULAR level; the artery figure is what
  separated them.*
- **For breadth among the independent six, PVBM**, the one that puts twenty canonical biomarkers on
  the table, including Hubbard's equivalents and the AVR. *The earlier page said PVBM alone computed
  the central retinal equivalents; AutoMorphalyzer's and VascX's Knudtson equivalents now carry
  catalogued names and are judged too, so that claim is withdrawn.* It is also the slowest, at 62.7
  seconds an image.
- **Do not use Grisan density from AutoMorph or AutoMorphalyzer**, which return about 0.96 and 1.00
  for a quantity the geometry puts at nought and move by 700% and 241% when the image is turned.
  AutoMorphClass's is about fifty times less wrong, and still wrong.
- **Between PVBM and OCULAR there is nothing to choose on any shared number** (section 3.2). PVBM
  adds the fractal dimensions and the central retinal equivalents at 62.7 seconds an image; OCULAR
  adds a length-weighted tortuosity at 4.7.
- **Do not use AutoMorph's own measuring stage for tortuosity** where either descendant is
  available: its Hart τ1 is out by up to 1,226% and moves by 449% under rotation, and both rewrites
  fixed exactly that.
- **Do not hand AutoMorphalyzer a picture where zones B and C may be empty** — a misplaced disc, a
  tight crop — without catching the exception: it raises and loses the whole picture (section 3).

## 8. What these numbers do not say

- **That any of this transfers to photographs.** Every shape here is clean, complete, unbroken and
  drawn to a known scale, with no lesions, no crossings mislabelled and no segmentation error
  upstream. A program that measures a drawn arc correctly has cleared the lowest bar there is.
- **That a quantity with no ground truth is right.** It is unchecked, which is a third thing.
- **That agreement between two implementations means either is correct.** PVBM and OCULAR share
  code, and so do the three AutoMorph entries; where siblings agree, that is evidence about their
  common ancestor.
- **That 25% and 10% are standards.** They are reporting conveniences, chosen so that a table shows
  the handful of quantities worth looking at rather than six hundred rows of nothing. Nothing here
  passes or fails.
- **That a `convention` or `asymptotic` fault is the same as an `exact` one.** Section 11 splits
  them, and most of fundus-biomarkers' dimension faults are asymptotic.
- **That the timings are a property of the software alone.** They are the only figures here that do
  not reproduce: an earlier full re-run on the same machine moved them by 5% to 40% with every
  measured value identical, and this run's are 1.7 to 3.6 times the 2026-10-21 page's, on the same
  grid. Treat the **ratios** as the finding — PVBM is about fifty
  times AutoMorphClass — and a figure like "62.7 seconds an image" as describing this machine on
  one afternoon.

## 9. What changed, and what it did not

From 2026-09-30 every catalogued biomarker states a physical unit and none of them is in pixels.
Each implementation still reports what it measured on the pixel grid, under its own column names,
and that number is converted once — by the rule the ground truth was built with — before the two
meet. Six things changed on this page, and only the first is cosmetic. **None of them was a
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

**9.6 A second VascX mapping went the same way as the first, and a photograph is what caught it.**
`lw_tort_curv` was mapped to `tortuosity/spline-curvature`, which means a curvature in 1/µm.
Reading `fundus/features/tortuosity.py` says it is not one: `_compute_for_segment` returns
`np.mean(spline.curvatures()) * self._get_curvature_scale(...)`, and that scale is
`layer.retina.disc_fovea_distance`. A curvature times a length is **dimensionless**, in
disc-to-fovea units — the same normalisation that took `mean_sparsity` out in §9.3, in a second
feature.

**The synthetic shapes could not see it and a real photograph could.** On these shapes the column
reads 0.0002 to 0.013 and merely looked noisy, which is why this page spent nine days reporting a
280% rotation spread as a finding about VascX's curvature when it was a finding about the fovea
this repository invents for a drawn shape. Run on an HRF photograph the same column reads about
**1.5**, which as 1/µm would be a vessel turning through a radius of two thirds of a micron —
impossible on sight, and the reason the mapping is now withdrawn
([BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) §5). Nothing was re-measured; VascX's 80 comparable
measurements and its 2-of-6 disagreements are unchanged, because the column never had a ground
truth to be judged against. What changed is a claim this page was making about it.

*The general lesson, now paid for twice.* Where an upstream carries an internal length it
normalises by, every mapping of its columns onto a unit-bearing name is suspect — not only the one
that misbehaved.

**9.7 PVBM's and OCULAR's length is the rooted length, and the shapes now say so.** *2026-10-23.*
Both walk each vessel tree from the optic disc, so a vessel that never reaches the disc is not
counted, and on `disjoint` — the one shape not on the disc — they read 0 where
`density/skeleton-length` is the whole network: 100% wrong, on every angle. The vocabulary now has
`density/skeleton-length-rooted`, the shapes settle it (the full length on every shape but
`disjoint`, and nothing there), and both columns agree with it on every shape to within 6%. So the
mapping moved, and the 100% left section 5. PVBM disagrees on 5 of 20 biomarkers where it disagreed
on 7, and OCULAR on 3 of 10 where it disagreed on 5. PVBM's values did not change; its stored
results were re-measured once, because its declared units name the column by its catalogued name
and that declaration is fingerprinted.

## 10. fundus-biomarkers, the seventh implementation

*Added 2026-10-21 at commit `571bc81`; measured here at `348da1b`, 2026-11-03.* Pheno's reference
implementation answers under the catalogue's own names, which is why its column is so much longer
than the rest: 633 quantities, every one of them catalogued, over the field of view and zones B
and C. It is published here like every other implementation, and **none of it is independently
verified**: the implementation and the atlas share an owner (`PLAN-BIOMARKER.md` §5.6). The rebuilt
shapes and their ground truth were ported from its own synthetic evaluation (section 11), so on the
quantities it was written against it is being tested on shapes its authors chose — another reason
to read its column as a measurement rather than a confirmation.

**Where the shapes settle a value, it mostly agrees.** Of 47,203 comparable measurements the median
disagreement is 0.0% and 92% fall within 25% of the geometry. 168 of its 629 judged biomarkers are
out by more than 25% somewhere (notebook section 4); grouped by family:

- **Box-counting and multifractal dimensions, 48% to 74%** — 24 names, every region. It reads 1.3 to
  1.5 on a straight vessel whose dimension is 1, where the AutoMorph group reads within 6–18%; on
  `koch` it is within 5.6%. The truth is `asymptotic`, and these are most of its 1,896 asymptotic
  faults (section 11.2). *Our observation, not traced in its code:* a count that rises above 1 on a
  straight band of constant width is what box-counting the filled vessel rather than its centreline
  at scales near the vessel's width would give.
- **Spline curvature, per vessel and per segment** — 36 names, 210% to 8,588%, on shapes whose
  curvature is nought or constant.
- **The higher Hart tortuosities, τ2, τ4 and τ6, and the inflection-based ones** — 72 names
  between them, from 25% to 60,000% where the truth is nought and the floor is the denominator. On `deep-bifurcation` it counts 6 vessel inflections in zone B where there are none.
- **Standard deviations** — 30 names. `calibre/width/*/std` reads 1,761% to 2,836% out and
  `topology/branching-angle/*/std` 2,523% to 14,697%, against truths of nought or a few microns.
  *Before the truth's rounding defect was fixed (section 1) six more std rows were here, and the
  worst of them read 66 trillion per cent.*
- **Counts** — endpoints out by 94% to 100% and junctions by 57% to 100%, `deep-bifurcation`
  among them, whose four-way junctions make the count rest on a `convention`.
- **Grisan density by zone** — 12 names at 100%, though its whole-field figure is within 8.8%.

**Turning the picture moves 139 of its 629 quantities by more than 10%** across the seven angles.
21 are standard deviations; most of the rest are spline curvatures (185% to 308%) and the Hart τ5
and τ7 family (11% to 37%). Its length-weighted widths, Hart τ1 and Grisan density means move by under 6%.

**Its two non-numeric answers.** The photograph's centring,
[`landmarks/centring`](../biomarkers/landmarks.md), is now judged: **all 91 renderings correct** —
`disc` on the 7 renderings of `spokes-disc-centred`, `macula` on the other 84. The cup-to-disc
ratios stay empty, because no shape hands it a cup.

It takes 8.2 seconds per image, on the CPU.

## 11. The shapes rebuilt in microns, with every value they settle

*Added 2026-11-10.* The store under `data/synthetic/av/` was rebuilt, and everything above was
measured against the new one. The shapes page,
[biomarker-synthetic-shapes.md](biomarker-synthetic-shapes.md), carries the derivations; this is
what the rebuild changed in the results.

**Where it came from.** The scene model and the derivations follow fundus-biomarkers' own synthetic
evaluation, brought into this repository because a ground truth is a reading of the catalogue's
definitions, which belong in the open (`PLAN-BIOMARKER.md` §5.3). Only the geometry and its
arithmetic came across; none of that library's tracing or measuring code did, and nothing on this
page calls it except through its adapter.

### 11.1 More shapes, more angles, more truth

| | 2026-10-21 | 2026-11-10 |
| --- | --- | --- |
| Shapes | 9 | **13** — `clothoid`, `tree`, `spur` and `crossing` added; all nine redrawn in microns |
| Angles | 4, every 30° | **7, every 15°** |
| Scale | 5 µm per pixel, stated | **6.33 µm per pixel**, a 45° field of 12,960 µm across the 2048² frame |
| Values settled per shape | 273 | **565 to 925** |
| Regions | whole field | whole field, **zone B** (2–3 disc radii) and **zone C** (2–5) |
| Structures | artery, vein | artery, vein, **the two together**, and **both** for the ratios |
| Values that do not exist | not recorded | **5,999**, recorded as *none* |

Two shapes exist for one quantity each. **`spokes-macula-centred` and `spokes-disc-centred`**
send six vessels per class from the disc, every one the same width, so the
central retinal equivalents have a value that does not depend on which pairing order an
implementation takes — and a disc-anchored measurement that differs between the two framings is
reading the framing rather than the eye; the disc-centred one reaches 5.4 disc radii, so zone C is settled
too. Of the new shapes, **`crossing`** puts one artery over another, which is two
vessels and not a junction; every count resting on that is marked `convention`.

**The pixel convention was made one.** Pixel `i`'s centre is at `i`, the convention of
`results/disc_estimation/`, and the disc handed to an adapter now sits exactly on the disc the
masks were drawn around. VascX's and AutoMorphalyzer's adapters had been building their disc mask
half a pixel off it; both were corrected with the store.

### 11.2 How each value is known

Every value carries a kind. Measurements out by more than 25%, against all comparable measurements
of that kind (notebook §4.3):

| Kind | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx | fundus-biomarkers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `exact` | 59 / 808 | 19 / 854 | 282 / 1,071 | 378 / 1,511 | 254 / 1,071 | 14 / 153 | 1,839 / 41,624 |
| `asymptotic` | 61 / 546 | — | 11 / 273 | 7 / 252 | 8 / 273 | — | 1,896 / 2,072 |
| `convention` | 7 / 394 | 7 / 28 | — | — | — | — | 135 / 2,415 |
| `numerical` | — | — | — | — | — | — | 0 / 1,092 |

A fault against an `exact` value is a fault. One against a `convention` — a crossing read as two
vessels, a lone vessel passed through Knudtson's pairing, which branches of a four-way junction are
its daughters — may be a different reading of the definition. An `asymptotic` value, a fractal
dimension, is a limit no finite raster reaches, so an honest implementation lands near it rather
than on it; fundus-biomarkers' column is the one where that distinction carries the weight.

### 11.3 Where the geometry gives no value, nobody invented one

On `disjoint` nothing reaches zone B; on `straight` there is no junction to take an angle at; a
vessel that never reaches the disc has no whole-vessel tortuosity. The right answer there is
*nothing*, and a number is a fault. **Over 4,564 such cases across 476 canonical biomarkers, no
implementation returned a number** — PVBM declined 42, VascX 14, AutoMorphalyzer 56 and
fundus-biomarkers 4,452. That was checked a second time directly against `results/`, because a
count of zero is also what a broken join produces, and it held.

It is not the same as getting the defined values right: PVBM's empty branching angle on `straight`
comes with a numpy "mean of empty slice" warning rather than a decision, and AutoMorphalyzer's
empty zones raise (section 3).

---

**Compiled from** [notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb)
on 2026-11-10.
