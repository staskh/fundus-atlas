# Synthetic biomarker benchmark — what came out

Seven biomarker implementations were run over the same **91 renderings**: thirteen drawn shapes at
seven angles each, every 15° from 0° to 90°. Each is drawn on a 2048² grid spanning a 45° field of
12,960 µm, so 6.33 µm per pixel. Arteries are 80 µm wide, veins 120 µm, and the optic disc is
1,800 µm across. Nothing here was photographed and nothing was annotated: every shape was *drawn*
from equations, so what it ought to measure follows from arithmetic rather than from anybody's
opinion.

Every number on this page comes from `results/biomarker-synthetic/`; the reading of them comes from
[the summary notebook](../../notebooks/synthetic/biomarker-synthetic.ipynb) and, one lineage each,
[AutoMorph's](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb),
[PVBM's](../../notebooks/synthetic/biomarker-synthetic-pvbm.ipynb) and
[VascX's](../../notebooks/synthetic/biomarker-synthetic-vascx.ipynb). How the benchmark
is configured is a separate page, [biomarker-synthetic-docs.md](biomarker-synthetic-docs.md), and
the shapes with their derivations are in
[the shapes page](biomarker-synthetic-shapes.md) and
[the shapes notebook](../../notebooks/synthetic/biomarker-synthetic-shapes.ipynb).

**All six are on this page together, and that is the point.** The question is whether these
programs compute the same quantity, and that question lives across a row — one biomarker, six
columns. The columns stand in **lineage order**: [PVBM](../projects/pvbm.md) and
[OCULAR](../projects/ocularnet.md), which imports PVBM's helpers at runtime; then
[AutoMorph](../projects/automorph.md) and its two descendants,
[AutoMorphalyzer](../projects/automorphalyzer.md) and
[AutoMorphClass](../projects/automorphclass.md); and last [VascX](../projects/vascx.md), which
shares code with none of them. A difference **between neighbours** is a change somebody made on purpose; a
difference **across a boundary** is two independent readings of the same definition.

> **Every number on this page was re-measured from scratch on 2026-11-10**, against a rebuilt
> store, and they replace the 2026-10-21 set, which was 36 renderings: nine shapes at four angles,
> at 5 µm per pixel. The shapes are now stated in microns on a
> model camera and carry far more ground truth: up to 925 values per shape where there were 273,
> over zones B and C as well as the whole field, each marked with how it is known — and, for the
> first time, the values the geometry says **do not exist**. Section 10 says what that added and
> what it changed. Several conclusions moved, and each section says where.
>
> **Re-measured again on 2026-11-22, with an optic cup.** The store gained a drawn cup, and two of the AutoMorph group now compute
> cup-to-disc ratios from it (section 11). Every vessel measurement came back **identical** to the
> 2026-11-10 run, value for value; what moved is the new cup columns, the timings, and
> AutoMorphalyzer's count of catalogued names, which the zone mapping of 2026-11-20 raised from 23
> to 31 before the cup added two more. The analysis is now split by **lineage**, one notebook per
> group beside a summary comparing the three (sections 12 and 13), and the columns the catalogue
> cannot name are now checked against what their own authors say they compute (section 14).
>
> **Re-measured a third time on 2026-11-22, with every column each project writes.** An audit found
> four adapters returning less than their project's own run: AutoMorph 18 of 72 numbers,
> AutoMorphClass 24 of 60, VascX 20 of the 132 its two shipped feature sets compute, and
> AutoMorphalyzer without its two ratios. All four now return everything, and AutoMorph and
> AutoMorphClass are run through their own pipelines' steps after segmentation, which hand every map
> on at 912 × 912. That also fixed a unit error in this repository's AutoMorph adapter, whose widths
> had been read 2.25 times too small. **AutoMorph's and AutoMorphClass's figures in sections 3 to 10
> predate this and are kept as history; section 15 has the current ones**, and sections 1, 7 and 11
> are updated. PVBM's, OCULAR's and AutoMorphalyzer's existing figures did not move, and neither did
> VascX's six judged biomarkers.
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
10. [The shapes rebuilt in microns, with every value they settle](#10-the-shapes-rebuilt-in-microns-with-every-value-they-settle)
11. [The optic cup, and the cup-to-disc ratios](#11-the-optic-cup-and-the-cup-to-disc-ratios)
12. [Each lineage on its own](#12-each-lineage-on-its-own)
13. [The three lineages compared, by canonical name](#13-the-three-lineages-compared-by-canonical-name)
14. [The unnamed columns, held to their own description](#14-the-unnamed-columns-held-to-their-own-description)
15. [Every column each project writes](#15-every-column-each-project-writes)

## 1. Summary

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Biomarkers produced | 30 | 18 | 72 | 66 | 60 | 132 |
| …matching a canonical name | 20 | 10 | 53 | 35 | 29 | 6 |
| Comparable measurements | 1,748 | 882 | 3,782 | 2,649 | 2,513 | **153** |
| Median disagreement | 4.9% | 0.0% | 10.4% | 6.3% | 8.0% | **0.0%** |
| Within 25% of the geometry | 93% | **97%** | 75% | 73% | 77% | 91% |
| Quantities that move when the image turns | 24 / 30 | 13 / 18 | 54 / 70 | 24 / 45 | 48 / 56 | 38 / 109 |
| Biomarkers disagreeing with the geometry | 15 / 20 | 4 / 10 | 43 / 53 | 19 / 35 | 18 / 29 | 2 / 6 |
| Exceptions | 0 | 0 | **42** | **21** | 0 | 0 |
| Seconds per image | **64.9** | 4.8 | 8.5 | 7.2 | **0.5** | 9.3 |

*Updated again 2026-11-22, after the adapters were extended (section 15).* AutoMorph's 42
exceptions are its zone stage finding no window in the empty zones of `disjoint`, where its own
drivers write −1; they are read as no answer, which is the right one there.

*Updated 2026-11-22.* AutoMorphalyzer's and AutoMorphClass's columns grew by their disc and cup
figures (section 11) and, for AutoMorphalyzer, by the zone mapping that now names its zone-C
tortuosities and equivalents. That is why its comparable measurements rose from 1,763 to 2,483 and
its disagreeing biomarkers from 12 to 17: more of what it always computed is now in front of a
truth, and none of its numbers changed. AutoMorphClass's median fell from 6.7% to 5.6% because two
exact ratios joined it.

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
that fix.

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

PVBM takes about **forty times** longer per image than AutoMorphClass — 64.9 seconds against 1.5 on
this run, 62.7 against 1.2 on the last.
The timings are the one figure here that does not reproduce (section 8), but the ratio does.

## 2. What could be compared, and what could not

Three different things stand between a quantity a program computes and a number this benchmark can
judge, and the counts above only mean something once they are kept apart:

- **The catalogue may have no name for it.** AutoMorphalyzer returns 17 quantities with no
  canonical name — `average_local_calibre` at every zone, `tortuosity_density` and
  `tortuosity_distance` at zone C, and two Knudtson equivalents at zone C. VascX returns 109 that
  carry a value, AutoMorphClass 31, AutoMorph 19, PVBM 10 and OCULAR 8. These are
  measured and stored under the implementation's own name and appear in **no** comparison, because
  a canonical name exists to make two numbers comparable and there is nothing yet to compare them
  with. The notebook's section 1.1 lists them by name.
- **No shape may settle it.** *This used to be the bigger gap and it has nearly closed.* The rebuilt
  truth settles every value over zones B and C as well as the field, over the artery-and-vein
  union the vocabulary calls `vessels`, and under every pooling statistic, so **57** of the
  canonical biomarkers these six implementations answer are judged. AutoMorphalyzer's zone-B
  columns, which section 2 used to say were "judged against nothing", now are judged, and so are its
  zone-B Knudtson equivalents.
- **The program may simply never answer.** AutoMorphalyzer returns 66 columns of which 52 ever
  carry a value, and VascX 132 of which 115 do.

## 3. What raised: AutoMorphalyzer, on vessels that never reach the disc

*This section was called "Nothing raised, once PVBM was given the same recursion limit as its
fork", and that was true of the 2026-10-21 run. It is no longer true of the benchmark, so the
heading changed; the question it answers — what raised, and why — is the same.*

**AutoMorphalyzer raised 21 times, all on `disjoint`, at every one of the seven angles.** Each
of its three measuring calls — artery, vein and the two together — raises
`ZeroDivisionError('division by zero')`, and every vessel value is lost with them, including the
field-wide values that did not need a zone. Nothing else raised anywhere.

*Until 2026-11-22 this read "28 times, and the whole rendering is lost": the seven renderings were
also counted as lost outright. They are not any more, because AutoMorphalyzer's disc and cup
figures (section 11) come from a separate call that does not raise.*

`disjoint` is the shape whose parallel vessels never reach the optic disc, and as redrawn it puts
nothing inside zone B or zone C at all — a fact the ground truth now records as *no value* for
every zone biomarker (section 10). The likeliest reading is that AutoMorphalyzer divides by the
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

42 of 55 canonical biomarkers move by more than 10% somewhere, over seven angles where there were
four. The worst of it, as the widest spread on any one shape:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/grisan-density/vein/…` | — | — | 700.0% | 241.3% | 265.4% | — |
| `tortuosity/hart-tau1/artery/…` | 19.0% | 12.9% | 449.4% | 11.9% | 10.0% | 12.8% |
| `topology/junctions/artery` | 210.0% | 210.0% | — | — | — | — |
| `calibre/width/vein/length-weighted` | — | — | 48.8% | 33.4% | 37.5% | **1.9%** |
| `density/box-counting/artery` | — | — | 24.9% | 7.1% | 8.9% | — |

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
- **Across the boundary, VascX is steadiest on calibre** — 1.9% on vein width where the AutoMorph
  group is at 33% to 49%.

The unnamed quantities are no better, and nothing else checks them. AutoMorphalyzer's
`tortuosity_density` at zone C moves by **350%**; AutoMorph's `squared_curvature_tortuosity` by
**697%** and AutoMorphClass's by **285%**; VascX's own `lw_tort_curv` columns — dimensionless, and
normalised by a fovea this repository supplies (§9.6) — by **494%**.

## 5. Disagreement with the geometry

8,136 measurements have a theoretical value to be judged against, over 57 canonical biomarkers;
39 of the 57 are out by more than 25% somewhere. The worst case each implementation produced over
all shapes and all angles, for the rows the earlier page carried and the zone values it could not:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `calibre/CRE-knudtson/artery/B` | 28.5% | — | — | 52.3% | — | **2.9%** |
| `calibre/CRE-knudtson/vein/B` | 30.4% | — | — | 67.4% | — | **2.4%** |
| `calibre/CRE-hubbard/vein/B` | 55.8% | — | — | — | — | — |
| `calibre/AVR-hubbard/both/B` | 47.0% | — | — | — | — | — |
| `calibre/width/artery/length-weighted` | — | — | 71.3% | 67.7% | 71.2% | **2.7%** |
| `calibre/width/vein/length-weighted` | — | — | 32.7% | 40.3% | 46.9% | **2.2%** |
| `tortuosity/hart-tau1/vein/…` | 30.4% | 9.5% | 1,225.7% | 14.6% | **8.6%** | 43.4% |
| `density/box-counting/artery` | — | — | 23.1% | 22.2% | 22.2% | — |
| `tortuosity/grisan-density/vein/…` | — | — | 16,458,731% | 17,136,413% | 332,512% | — |

**The central retinal equivalents are settled by the spokes.** Six vessels per class leave the disc, every one the same width, so every pairing order Knudtson's
or Hubbard's method could take agrees. On them PVBM's Knudtson equivalents are 13.5% out at both
framings and its Hubbard venular equivalent **55.8%** — the mechanism of §9.2, Hubbard's +450 µm
venular constant applied to pixel widths, now on a shape built to test it. AutoMorphalyzer's
Knudtson equivalents are 2.9% and 3.6% on the spokes and 52–67% on `deep-bifurcation`, where several
vessels share a zone at different widths.

**Calibre on `crossing` is where the AutoMorph group fails most.** One artery passes over another,
and all three read the length-weighted artery width 68–71% out there, against 2–18% on the smooth
shapes. VascX returns no comparable width there.

**The Grisan figures are against a truth of exactly nought** — a curve that bends one way
throughout has no inflections — so the percentage is taken against the noise floor. Read the values:

| | truth | AutoMorph | AutoMorphalyzer | AutoMorphClass |
| --- | --- | --- | --- | --- |
| Grisan density on `straight` or `arc`, worst, per µm | 0 | 0.151 | 0.158 | 0.0031 |
| …as its own returned figure, per px | 0 | 0.958 | 0.998 | 0.019 |

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

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Mean τ1 on `koch`, arteries | 1.699 | 1.723 | 1.228 | 1.549 | 1.682 | 1.061 |
| Against 1.778 | −4% | **−3%** | −31% | −13% | −5% | −40% |

PVBM's and OCULAR's figures are their median and length-weighted columns respectively, which is why
the two differ here and nowhere else.

**VascX returns about 1.06 on a curve whose truth is 1.78** — within a few percent of calling it a
straight line — and AutoMorph's 1.23 is little better. Every implementation
undershoots, and the reason is not a bug in any of them: skeletonising a curve with 60° corners
leaves short spurs, and an implementation that prunes them before measuring gets a shorter arc. So
the **ordering** is more trustworthy than the absolute percentages.

## 7. Which to reach for, and at what question

There is no best implementation here, and pretending otherwise would mean comparing a column of 153
measurements with a column of 1,748 as though they answered the same question. What can be said:

- **For vessel calibre, VascX**: 2.7% and 2.2% worst error on the length-weighted artery and vein
  widths, and 2.9% and 2.4% on the zone-B Knudtson equivalents, against 33% to 71% for the AutoMorph
  group and 28% to 56% for PVBM's equivalents. It moves by 1.9% under rotation. The runner-up is
  PVBM on the equivalents, at 28.5% and 30.4%, so the margin is wide. The caveat is
  scope: VascX yields six judged biomarkers, and a comparable calibre only on `deep-bifurcation` and
  the two spoke shapes.
- **For Hubbard's arteriovenous ratio, AutoMorph; for Hubbard's equivalents themselves, neither
  clearly.** *Rewritten 2026-11-22, when AutoMorph's zone stage was first measured.* AutoMorph's
  zone-B `AVR_Hubbard` is never more than 13.8% out, where PVBM's is 47.0%, because AutoMorph
  applies Hubbard's micron constants to widths it has put in microns and PVBM applies them to
  pixels. The equivalents are far out at worst in both: PVBM 30.9–55.8%, AutoMorph 52.9–63.0%, with
  AutoMorph's medians at 3–12% (section 15). Knudtson's version, which is scale-free, remains the
  safer choice, and VascX's is the closest.
- **For tortuosity, AutoMorphClass**: 9.2% and 9.5% worst on length-weighted Hart τ1 over every
  shape and angle, and the fastest thing here at 0.5 seconds an image (figures since 2026-11-22,
  through its own pipeline at 912 × 912; they were 8.6% and 9.5% before). OCULAR's
  length-weighted column is level on veins (9.5%) and no longer on arteries (23.9%).
  AutoMorphalyzer is 14.6–17%, PVBM's and OCULAR's median 15.0–30.4%,
  VascX 43%. *The earlier page put AutoMorphClass and OCULAR level; the artery figure is what
  separated them.*
- **For breadth among the independent six, PVBM**, the one that puts twenty canonical biomarkers on
  the table, including Hubbard's equivalents and the AVR. *The earlier page said PVBM alone computed
  the central retinal equivalents; AutoMorphalyzer's and VascX's Knudtson equivalents now carry
  catalogued names and are judged too, so that claim is withdrawn.* It is also the slowest, at 64.9
  seconds an image.
- **Do not use Grisan density from AutoMorph or AutoMorphalyzer**, which return about 0.96 and 1.00
  for a quantity the geometry puts at nought and move by 700% and 241% when the image is turned.
  AutoMorphClass's is about fifty times less wrong, and still wrong.
- **Between PVBM and OCULAR there is nothing to choose on any shared number** (section 3.2). PVBM
  adds the fractal dimensions and the central retinal equivalents at 64.9 seconds an image; OCULAR
  adds a length-weighted tortuosity at 4.8.
- **Do not use AutoMorph's own measuring stage for tortuosity** where either descendant is
  available: measured as its pipeline runs it, its mean Hart τ1 is up to 161 times the geometry's
  value and moves by 350–640% under rotation (section 15), and both rewrites fixed exactly that.
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
- **That a `convention` or `asymptotic` fault is the same as an `exact` one.** Section 10 splits
  them.
- **That the timings are a property of the software alone.** They are the only figures here that do
  not reproduce: an earlier full re-run on the same machine moved them by 5% to 40% with every
  measured value identical, and this run's are 1.7 to 3.6 times the 2026-10-21 page's, on the same
  grid. Treat the **ratios** as the finding — PVBM is forty to fifty
  times AutoMorphClass — and a figure like "64.9 seconds an image" as describing this machine on
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

## 10. The shapes rebuilt in microns, with every value they settle

*Added 2026-11-10.* The store under `data/synthetic/av/` was rebuilt, and everything above was
measured against the new one. The shapes page,
[biomarker-synthetic-shapes.md](biomarker-synthetic-shapes.md), carries the derivations; this is
what the rebuild changed in the results.

**Where it lives.** The scene model and the derivations are written out in this repository, because
a ground truth is a reading of the catalogue's definitions, which belong in the open
(`PLAN-BIOMARKER.md` §5.3).

### 10.1 More shapes, more angles, more truth

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

### 10.2 How each value is known

Every value carries a kind. Measurements out by more than 25%, against all comparable measurements
of that kind (notebook §4.3):

| Kind | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `exact` | 59 / 808 | 19 / 854 | 282 / 1,071 | 560 / 2,203 | 254 / 1,253 | 14 / 153 |
| `asymptotic` | 61 / 546 | — | 11 / 273 | 7 / 252 | 8 / 273 | — |
| `convention` | 7 / 394 | 7 / 28 | — | 28 / 28 | — | — |

A fault against an `exact` value is a fault. One against a `convention` — a crossing read as two
vessels, a lone vessel passed through Knudtson's pairing, which branches of a four-way junction are
its daughters — may be a different reading of the definition. An `asymptotic` value, a fractal
dimension, is a limit no finite raster reaches, so an honest implementation lands near it rather
than on it.

### 10.3 Where the geometry gives no value, nobody invented one

On `disjoint` nothing reaches zone B; on `straight` there is no junction to take an angle at; a
vessel that never reaches the disc has no whole-vessel tortuosity. The right answer there is
*nothing*, and a number is a fault. **Over 168 such cases across 20 canonical biomarkers, asked of
AutoMorphalyzer, PVBM and VascX, no implementation returned a number.** That was checked a second time directly against `results/`, because a
count of zero is also what a broken join produces, and it held.

It is not the same as getting the defined values right: PVBM's empty branching angle on `straight`
comes with a numpy "mean of empty slice" warning rather than a decision, and AutoMorphalyzer's
empty zones raise (section 3).

## 11. The optic cup, and the cup-to-disc ratios

*Added 2026-11-22.* Every shape now carries an **optic cup** inside its disc: an ellipse on the
disc's centre, 0.40 of the disc's diameter across and 0.55 up and down, turned with the rest of the
scene, and each adapter is handed it as a mask beside the disc.

A **cup-to-disc ratio** compares the cup's size with the disc's. The vertical one is read along the
photograph's columns and the horizontal one along its rows, so, unlike every vessel measure here,
**turning the picture is meant to move them**: at 0° the vertical ratio is 0.55 and the horizontal
0.40, at 90° they have swapped, and in between the geometry gives each exactly. They are therefore
left out of every rotation check, and judged against the value for their own angle.

| | automorphalyzer | automorphclass |
| --- | --- | --- |
| `landmarks/CDR-vertical`, worst error over 91 renderings | **0.0%** | **0.0%** |
| `landmarks/CDR-horizontal`, worst error over 91 renderings | **0.0%** | **0.0%** |

Both land inside the noise floor on every shape at every angle, and follow the swap
([AutoMorph group notebook](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb) §6).
Both read the ratio as the cup's extent over the disc's along one image axis, which is exactly what
a drawn ellipse is easiest for; **a real cup, irregular and with a soft rim, is a much harder
test**, and this one says only that the arithmetic is right.

**AutoMorph's own ratios are measured too, since 2026-11-22.** They are computed in a driver,
`optic_disc_centre`, that reads its inputs from files; the adapter now lays those files out in a
temporary directory and runs it as shipped. On its 912 × 912 maps it lands within 1.9% everywhere,
as AutoMorphClass now does through its own pipeline (section 15). **PVBM, OCULAR and VascX compute
no cup-to-disc ratio.**

**The sizes behind the ratios, and the centring, since 2026-11-22.** The catalogue now names the
disc's and cup's vertical and horizontal diameters, in microns, and all three of the AutoMorph
family were already returning them as heights and widths beside the ratios. Against the shapes the
disc's land within 1.3% and the cup's within 2.4% at worst, for all three, on every rendering
(AutoMorphalyzer, measuring on the frame it is handed rather than at 912, within 1.3% on both).
AutoMorphalyzer's `macular_centred` answers the catalogue's centring — `macula`, `disc`, or
`unknown` when its disc metrics fail — and is right on all 91 renderings. Its rule is the
geometry's own, a disc within a tenth of the frame of its centre, so this is a check that the
answer is passed through faithfully rather than a hard test.

AutoMorphalyzer also returns the disc's and cup's heights and widths, the cup's centre, whether the
photograph is macula-centred, and which eye it is. Those are checked against their own description
in section 14; the eye is a word, from which side of the disc has more vessel, and has no value on a
drawn shape.

## 12. Each lineage on its own

*Added 2026-11-22.* The implementations fall into three **lineages** — groups that share code — and
each has a notebook of its own, with the same sections in the same order: coverage, failures,
rotation, agreement by canonical name, agreement with the columns' own description, best and worst
biomarkers, and what the evidence shows. A difference **inside** a lineage is a change somebody made
on purpose; agreement inside one is evidence about the code they share, not separate confirmation.

| Lineage | Members | Notebook |
| --- | --- | --- |
| AutoMorph | AutoMorph, and its two rewrites AutoMorphalyzer and AutoMorphClass | [biomarker-synthetic-automorph.ipynb](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb) |
| PVBM | PVBM, and OCULAR, which runs PVBM's code | [biomarker-synthetic-pvbm.ipynb](../../notebooks/synthetic/biomarker-synthetic-pvbm.ipynb) |
| VascX | VascX, which shares code with neither | [biomarker-synthetic-vascx.ipynb](../../notebooks/synthetic/biomarker-synthetic-vascx.ipynb) |

The tables below give each member's **best** biomarkers (smallest worst error over every shape and
angle) and its **worst** (of those out by more than 25% somewhere), as each notebook prints them.
An error above ten times the truth is written as a multiple; where the truth is nought it is taken
against the noise floor, so read those as "wrong", not as a size.

### 12.1 AutoMorph, AutoMorphalyzer, AutoMorphClass

| | automorph | automorphalyzer | automorphclass |
| --- | --- | --- | --- |
| Canonical biomarkers judged | 15 | 33 | 17 |
| …out by more than 25% somewhere | 11 | 17 | 7 |
| Unnamed columns out against their own description | 3 / 3 | 0 / 16 | 3 / 7 |
| Exceptions | 0 | 21 | 0 |
| Best | vein area over the image, 16.3% | both cup-to-disc ratios, 0.0% | both cup-to-disc ratios, 0.0% |
| Worst | Grisan density, up to 164,587× | Grisan density in zone B, up to 335,084× | Grisan density, length-weighted, up to 3,325× |

- **The cup-to-disc ratios are exact** in both rewrites (section 11).
- **The rewrites fixed AutoMorph's tortuosity and kept its Grisan density.** AutoMorph's Hart τ1
  is out by up to 1,226% and moves by 449% under rotation; the rewrites move by 7–26% and are out
  by 15–17% (AutoMorphalyzer) and under 10% (AutoMorphClass, length-weighted). Grisan density is
  wrong in all three and moves by 180–700% (sections 4 and 5).
- **Calibre is the lineage's weak family**: length-weighted width 33–71% out in every member, worst
  on `crossing`, and AutoMorphalyzer's zone-B and zone-C Knudtson equivalents 52–179% on
  `deep-bifurcation`.
- **Density is its strong one**: vessel area over the image within 5.0–5.3% for the rewrites and
  29% for AutoMorph.

### 12.2 PVBM and OCULAR

| | pvbm | ocular |
| --- | --- | --- |
| Canonical biomarkers judged | 20 | 10 |
| …out by more than 25% somewhere | 15 | 4 |
| Unnamed columns out against their own description | 5 / 8 | 5 / 8 |
| Exceptions | 0 | 0 |
| Best | vein area, 1.7% | vein area, 1.7% |
| Worst | vein junctions, 57× | vein junctions, 57× |

- **The two return the same number wherever they share a column** (section 3.2). OCULAR is the
  same answer about thirteen times faster, 4.8 seconds an image against 64.9.
- **Area and length are where the lineage is trustworthy**: vessel area within 1.7% (veins) and
  5.0% (arteries), rooted vein length within 4.5%.
- **Junction counts are where it fails**: 3 or 4 junctions on the Koch curve, which has none, and a
  count that moves by 200–210% as the picture turns.
- **PVBM's central retinal equivalents** are 55.8% out (Hubbard, venular) and 47.0% (Hubbard AVR)
  on the spoke shapes, and 28.5–30.4% (Knudtson) on `deep-bifurcation`; all of them move by 10–27%
  under rotation.

### 12.3 VascX

| | vascx |
| --- | --- |
| Canonical biomarkers judged | 6 |
| …out by more than 25% somewhere | 2 |
| Unnamed columns out against their own description | 6 / 6 |
| Exceptions | 0 |
| Best | vein width, length-weighted, 2.2% |
| Worst | artery Hart τ1, length-weighted, 43.5% |

- **Calibre is within 2.2–2.9%** on the length-weighted widths and the zone-B Knudtson equivalents,
  moving by at most 4.1% under rotation — but it is judged on three shapes only.
- **Tortuosity fails on one shape**: about 1.05 on the Koch curve against 1.78, and within
  tolerance on every other.
- **Its own unnamed columns all miss somewhere** — the six the shapes can settle. The segment-capped
  tortuosities fail on the Koch curve as the canonical one does, and the vessel density inside its
  own circle fails on `deep-bifurcation` (section 14). Eight more need a fovea and cannot be
  settled at all.

## 13. The three lineages compared, by canonical name

*Added 2026-11-22, from the [summary notebook](../../notebooks/synthetic/biomarker-synthetic.ipynb)
§6.* Each lineage is represented by its **closest member** on each name — the one whose worst error
is smallest — so a cell says what the best of that code can do, not what every member does.

**The lineages barely overlap.** Of 57 canonical names with a ground truth, 51 are answered by one
lineage alone, 2 by two and 4 by all three. A reader choosing software is mostly choosing which
questions can be asked at all:

| Family | AutoMorph lineage | PVBM lineage | VascX |
| --- | --- | --- | --- |
| Calibre | 7 names, 0 within 25% everywhere | 6, 1 | 4, **4** |
| Density | 6, **5** | 10, 3 | — |
| Landmarks (cup-to-disc) | 2, **2** | — | — |
| Topology | — | 2, 0 | — |
| Tortuosity | 24, 12 | 4, 3 | 2, 0 |

*Updated 2026-11-22, after every adapter returned every column its project writes and the disc's
and cup's diameters were named:* the summary notebook now finds **83** names with a ground truth —
4 answered by all three lineages, 6 by two, 73 by one. Per family, names answered and how many
within 25% everywhere: AutoMorph lineage calibre 21, 3; density 12, 5; **landmarks 6, 6** (the two
ratios and four diameters); tortuosity 30, 13. PVBM's and VascX's rows are unchanged. The table
above is kept as it was first written.

**Where they overlap, they disagree by an order of magnitude**, and not in the same direction on
every family. The six names two or more lineages answer, worst error of the closest member:

| Biomarker | AutoMorph lineage | PVBM lineage | VascX |
| --- | --- | --- | --- |
| `calibre/width/artery/length-weighted` | 67.7% | — | **2.7%** |
| `calibre/width/vein/length-weighted` | 32.7% | — | **2.2%** |
| `calibre/CRE-knudtson/artery/B` | 52.3% | 28.5% | **2.9%** |
| `calibre/CRE-knudtson/vein/B` | 67.4% | 30.4% | **2.4%** |
| `tortuosity/hart-tau1/artery/length-weighted` | **9.5%** | 23.9% | 43.5% |
| `tortuosity/hart-tau1/vein/length-weighted` | **8.6%** | 9.5% | 43.4% |

**Each lineage has one failure the others do not share**: Grisan density in AutoMorph's, which
moves by 180–700% under rotation even in its steadiest member; junction counts in PVBM's, which
move by 200–210% and appear on an unbranched curve; tortuosity on a kinked curve in VascX's.

### 13.1 Which lineage to reach for, per question

| Question | Reach for | Its worst error | Runner-up, and the margin | What would change the answer | Seconds an image |
| --- | --- | --- | --- | --- | --- |
| Vessel width, central retinal equivalents | VascX | 2.2–2.9% | PVBM lineage, 28.5–30.4% (Knudtson); about ten times worse | judged on three shapes only | 5.2 |
| Arc-over-chord tortuosity | AutoMorph lineage (AutoMorphClass) | 8.6–9.5% | PVBM lineage (OCULAR): level on veins at 9.5%, 23.9% on arteries | on veins it is not a margin | 1.5, OCULAR 4.8 |
| Cup-to-disc ratio | AutoMorph lineage (either rewrite) | inside the noise floor | none — no other lineage computes it | a drawn ellipse is the easiest cup there is | 1.5 or 7.0 |
| Vessel area | AutoMorph rewrites or PVBM lineage | 1.7–5.3%, each on its own name | — | different canonical names, not compared directly | 1.5, 4.8 |
| Junctions, branching | none | 43–57× on `koch` | — | only PVBM's lineage answers, and it fails | — |
| Grisan density | none | 3,297–3,325× even in AutoMorphClass | — | only AutoMorph's lineage answers, and it fails | — |

This agrees with section 7, which makes the same calls implementation by implementation; it adds
only the cup-to-disc ratio, which did not exist here before. The timings are this machine on one
run (section 8). And none of it says anything about photographs.

## 14. The unnamed columns, held to their own description

*Added 2026-11-22.* Until now a column the catalogue could not name was measured, stored, and
checked only for rotation (section 2). It is now also held to **what its authors say it computes** —
in its name, its docstring or the paper it cites — worked out on the same geometry
(`src/benchmarks/shapes/claims.py`, and `ground_truth_claimed.csv` beside the store). That is a test
of the authors' description, not of the catalogue's: a column can fail it while being exactly what
a different definition asks for.

48 such columns can be settled; 11 cannot, because they need a fovea (VascX's eight), a
multifractal spectrum with no closed form (PVBM's two singularity lengths), or are a word (which eye,
AutoMorphalyzer). Every family of claim, with its worst and median error over the shapes that settle
it:

| Column, and what it claims | Implementations | Worst | Median |
| --- | --- | --- | --- |
| `tortuosity_index` — total arc over total chord, over every segment | pvbm, ocular (as `pooled_tortuosity`) | 15.8% | 5.5% |
| `average_local_calibre` — mean local width, sampled along the vessels | automorphalyzer, nine regions | within 25% | — |
| the cup's centre | automorphalyzer | within 25% | — |
| `start_points` — vessels leaving the disc | pvbm, ocular | 33.3% (one rendering) | 0.0% |
| `endpoints` — vessel ends | pvbm, ocular | 100% | 50% |
| `median_branching_angle` — between a branch's two daughters | pvbm, ocular | 129% | 7–13% |
| `squared_curvature_tortuosity` — Hart's ∫κ² ds | automorph, automorphclass | 18,923–44,552× | 100% to 4,916× |
| `vd` — vessel area over a disc-centred circle of 7/6 disc diameters | vascx | 57–59% | 0.0% |
| `lw_tort_dist` — length-weighted arc over chord, segments capped | vascx, four variants | 41–43% | 0.0% |

Four findings, each ours, and each a statement about a column rather than about the catalogue:

- **PVBM's tortuosity index is what its description says** — a ratio of sums, not a length-weighted
  mean — and lands within 15.8%. This is the reading the catalogue adopted on 2026-11-20; the shapes
  now support it.
- **PVBM's endpoint count leaves out the end at the disc.** It answers 1 on a straight vessel with
  two ends, 2 on a bifurcation with three, 6 on six spokes with twelve, and 0 on vessels that never
  reach the disc: the free tips of disc-rooted trees, not every end.
- **The squared-curvature column of AutoMorph and AutoMorphClass is not Hart's ∫κ² ds** on any
  reading the shapes support: it is tens to tens of thousands of times that value, and non-zero on a
  straight vessel, which has no curvature at all.
- **VascX's circle density fails on one shape.** It reads 0.018 for arteries on `deep-bifurcation`
  where its own description gives 0.011, and 0.026 against 0.017 for veins, and is exact on every
  other shape. The cause is not diagnosed.

The full tables, with every column and every shape, are §5 of each group notebook.


## 15. Every column each project writes

*Added 2026-11-22.* Each adapter now returns every number its project's own run writes, and each
project page lists them with the canonical name each answers to, or the nearest one and what
differs ([AutoMorph](../projects/automorph.md) §6.1, [AutoMorphalyzer](../projects/automorphalyzer.md)
§6.1, [AutoMorphClass](../projects/automorphclass.md) §6.1, [PVBM](../projects/pvbm.md) §6.1,
[OCULAR](../projects/ocularnet.md) §6.2, [VascX](../projects/vascx.md) §6.4).

| | before | now | what was missing |
| --- | --- | --- | --- |
| AutoMorph | 18 | **72** | zones B and C, Hubbard's and Knudtson's equivalents and both ratios, the disc and cup |
| AutoMorphClass | 24 | **60** | its zones B and C |
| AutoMorphalyzer | 64 | **66** | its two ratios, `AVR_B` and `AVR_C` |
| VascX | 20 | **132** | every column of `od_centered` but 20, and all of `full_v3`, the set its README recommends |
| PVBM, OCULAR | 30, 18 | 30, 18 | nothing |

**How they are run.** AutoMorph through its own steps after segmentation, on a temporary copy of
the files they pass: the two M2 stages' `filter_frag`, which resize every map to 912 × 912 and
skeletonise it; `optic_disc_centre`, which measures the disc and cup and cuts the zones; and both
vendored copies of retipy. AutoMorphClass through its pipeline's `forward`, with the masks
supplied so none of its networks runs. VascX runs both shipped sets on one retina.

**What the new evidence shows** — the
[AutoMorph group notebook](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb) §9 has it
in full, with every row under AutoMorph's own column names:

- **AutoMorph's widths were read 2.25 times too small** by this repository's adapter until this
  run: it measures at 912, and its widths were converted as if they were pixels of the 2048 frame.
  The median width error is now 10–13% in all three members.
- **On vessels at 45°, AutoMorph and AutoMorphClass are 59–184% out on width**, and their widths
  move by 63–132% as the picture turns. Both measure the same 912 maps and return the same
  whole-picture widths. AutoMorphalyzer, which measures at the size it is handed, is 40–68% out at
  worst.
- **AutoMorph's zone-B equivalents** have medians of 3–12% and worst cases of 42–73%, and move by at
  most 10.4% under rotation; its Hubbard ratio is within 13.8% (section 7).
- **AutoMorph's mean Hart τ1 is up to 161 times the geometry's value.** On its own 912 skeleton,
  retipy finds vessel pieces with almost no chord, and a mean over vessels lets one dominate. The
  thresholds in `retipy.config`, which every driver reads, made no difference to it on the one
  rendering checked both ways (`arc` at 45°).
- **AutoMorphClass returns 0.0 for arc over chord in an empty zone**, on `disjoint` in zone B — a
  value no curve can have, where the right answer is none.
- **AutoMorphalyzer's ratios are 50% out at the median**: where both equivalents failed,
  `merge_results` divides −1 by −1 and keeps the 1.
- **All three AutoMorph-lineage cup-to-disc ratios are within 1.9%** everywhere.
- **VascX's 109 named-by-itself columns** are mostly its calibre, tortuosity, density, sparsity
  and branching angle over regions on the disc-to-fovea axis, which a synthetic shape does not
  have; 36 move by more than 10% under rotation, the hemifield and half-circle densities by up to
  700%. Running both sets costs 9.3 seconds an image. Its whole-image `full_v3` columns name
  catalogued biomarkers outright and are held to them: widths within 2.4–5.1%, whole-vessel arc
  over chord within 8.6%, and its mean branching angle 48–60% out at worst.

---

**Compiled from** [the summary notebook](../../notebooks/synthetic/biomarker-synthetic.ipynb) and
the three group notebooks in [notebooks/synthetic/](../../notebooks/synthetic/) on 2026-11-22;
sections 1–11 were first compiled on 2026-11-10. Their PVBM, OCULAR, AutoMorphalyzer and VascX
vessel figures were re-measured unchanged; their AutoMorph and AutoMorphClass figures are history,
superseded by section 15.
