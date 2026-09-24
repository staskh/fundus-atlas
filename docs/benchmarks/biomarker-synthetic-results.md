# Synthetic biomarker benchmark — what came out

Six biomarker implementations were run over the same **36 renderings** — nine drawn shapes at four
angles each — on a 2048² grid at 5 µm per pixel, with arteries 80 µm wide, veins 120 µm and an
optic disc 1800 µm across. Nothing here was photographed and nothing was annotated: every shape was
*drawn* from equations, so what it ought to measure follows from arithmetic rather than from
anybody's opinion.

Every number on this page comes from `results/biomarker-synthetic/`; the reading of them comes from
[notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb). How the benchmark
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

## Contents

1. [Summary](#1-summary)
2. [What could be compared, and what could not](#2-what-could-be-compared-and-what-could-not)
3. [The one implementation that raised](#3-the-one-implementation-that-raised)
4. [Turning the picture changes the answer](#4-turning-the-picture-changes-the-answer)
5. [Disagreement with the geometry](#5-disagreement-with-the-geometry)
6. [Where the fixture is the limit, not the software](#6-where-the-fixture-is-the-limit-not-the-software)
7. [Which to reach for, and at what question](#7-which-to-reach-for-and-at-what-question)
8. [What these numbers do not say](#8-what-these-numbers-do-not-say)

## 1. Summary

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Biomarkers produced | 32 | 18 | 18 | 54 | 18 | 20 |
| …matching a canonical name | 22 | 10 | 15 | 17 | 15 | 8 |
| Comparable measurements | 392 | 312 | 216 | 232 | 216 | **83** |
| Median disagreement | 4.9% | 5.8% | 8.2% | 7.2% | 8.3% | **0.7%** |
| Within 25% of the geometry | 82% | 70% | 72% | 84% | 82% | **87%** |
| Quantities that move when the image turns | 15 / 32 | 10 / 18 | 16 / 18 | 25 / 40 | 12 / 18 | **4 / 20** |
| Biomarkers disagreeing with the geometry | 11 / 22 | 8 / 10 | 6 / 10 | 6 / 12 | 6 / 10 | 3 / 6 |
| Exceptions | **16** | 0 | 0 | 0 | 0 | 0 |
| Seconds per image | **106.3** | 4.4 | 2.0 | 7.9 | **1.0** | 5.3 |

**Read this table down a column, not across a row.** The accuracy rows are not a score and the
columns are not ranked by them, because the columns are not answering the same question: VascX's
0.7% median is over **83** measurements of six biomarkers, and PVBM's 4.9% is over **392** of
twenty-two. Measuring less, more carefully, is a defensible engineering choice and it is not the
same achievement as measuring more. Section 7 says what can actually be concluded.

Two figures stand out on their own terms. **PVBM takes a hundred times longer per image than
AutoMorphClass** — 106 seconds against 1.0 — which over a study of fifty thousand photographs is
about **two months of compute against fourteen hours**. And **PVBM is the only implementation that
raised at all**, sixteen times, always on the same thing (section 3).

## 2. What could be compared, and what could not

Three different things stand between a quantity a program computes and a number this benchmark can
judge, and the counts above only mean something once they are kept apart:

- **The catalogue may have no name for it.** AutoMorphalyzer returns 23 quantities with no
  canonical name — `average_local_calibre`, `tortuosity_density` and `tortuosity_distance`, each at
  zone B, zone C and whole-image and each for artery, vein and both, plus two Knudtson equivalents
  at zone C. VascX returns 12, PVBM 10. These are
  measured and stored under the implementation's own name and appear in **no** comparison, because
  a canonical name exists to make two numbers comparable and there is nothing yet to compare them
  with. Each one is either a gap in the catalogue or a mapping nobody has made — both are work
  somebody can do, and the notebook's section 1 lists them by name.
- **No shape may settle it.** A quantity can carry a catalogued name and still have no theoretical
  value here. This is why VascX's eight canonical names yield six judged biomarkers and AutoMorph's
  fifteen yield ten.
- **The program may simply never answer.** AutoMorphalyzer returns 54 columns of which 40 ever
  carry a value.

## 3. The one implementation that raised

Sixteen exceptions, all PVBM, all `RecursionError: maximum recursion depth exceeded`, all from its
central retinal equivalents, and all on exactly two shapes: **`koch` and `deep-bifurcation`**, at
every one of the four angles.

Those are the two shapes with the most skeleton in them. PVBM walks a vessel tree recursively, so
the failure is a function of how much vessel there is rather than of anything being malformed —
which means a real photograph of a densely vascularised retina can trigger it, and a sparse one
will not. An implementation that raises has at least told you it could not answer; the rest of this
page is about the harder case, where a program returns a confident number instead.

## 4. Turning the picture changes the answer

The same shape is drawn again at each angle in continuous coordinates, never by turning a picture,
so the geometry at 30° is *identical* to the geometry at 0°. **Any spread at all is the
implementation or the pixel grid beneath it** — and this check needs no ground truth, which is why
it is also the only check the unnamed quantities of section 2 ever get.

Twenty-one of 37 canonical biomarkers move by more than 10% somewhere. The worst of it:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/grisan-density/vein` | — | — | 400.0% | 301.7% | 231.4% | — |
| `tortuosity/hart-tau1/vein` | 12.4% | 13.6% | 258.8% | 11.5% | 10.0% | **1.6%** |
| `tortuosity/spline-mean-curvature/artery` | — | — | — | — | — | 280.5% |
| `junction-counts/junctions/vein` | 100.0% | 160.0% | — | — | — | — |
| `vessel-calibre/mean-width/vein` | — | — | 60.0% | 14.0% | 14.0% | **1.7%** |
| `fractal-dimension/box-counting/artery` | — | — | 20.1% | 80.7% | 80.8% | — |

Three findings, and each is legible only because the columns are ordered by lineage:

- **Within the AutoMorph group, the descendants fixed their ancestor's tortuosity and inherited its
  Grisan density.** AutoMorph's Hart τ1 moves by 258.8% on a shape that did not change;
  AutoMorphalyzer's and AutoMorphClass's move by 11.5% and 10.0%. That is a change somebody made on
  purpose, and it worked. Grisan density moves by 231% to 400% in all three, which is the part
  nobody touched.
- **Across the boundary, VascX is in a different regime** — 1.6% and 1.7% where its neighbours are
  at 10% to 60%. It also has its own unique failure: `spline-mean-curvature` at 280.5%, a quantity
  only VascX computes and which nothing else here would have caught.
- **PVBM and OCULAR both count junctions unstably**, 100% and 160%, which is the same defect
  surviving the fork. On `bifurcation` — a single fork, one junction — PVBM's vein junction count
  reads **1, 4, 4, 3** across the four angles of a shape that did not change.

The unnamed quantities are no better. AutoMorphalyzer's `tortuosity_density` at zones B and C moves
by **400%**; PVBM's `std_branching_angle_vein` by 393.5%; AutoMorph's and AutoMorphClass's
`squared_curvature_tortuosity` by 400% and 203%. None of those appears anywhere else on this page,
and without this section none of them would be checked at all.

## 5. Disagreement with the geometry

1,451 measurements have a theoretical value to be judged against, over 30 canonical biomarkers.
Fifteen of the thirty are out by more than 25% somewhere. The worst case each implementation
produced, over all shapes and all angles:

| Biomarker | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| `junction-counts/junctions/artery` | 785.7% | 42.9% | — | — | — | — |
| `junction-counts/endpoints/artery` | 650.0% | 100.0% | — | — | — | — |
| `central-retinal-equivalents/hubbard/artery` | 81.4% | — | — | — | — | — |
| `vessel-area-and-length/skeleton-length/vein` | 60.8% | 100.0% | — | — | — | — |
| `tortuosity/hart-tau1/vein` | 62.3% | 48.9% | 542.2% | 60.0% | 55.9% | 61.6% |
| `vessel-calibre/mean-width/vein` | — | — | 56.5% | 50.9% | 52.1% | **1.1%** |
| `avr/hubbard/both` | 32.2% | — | — | — | — | — |
| `tortuosity/grisan-density/artery` | — | — | **∞** | **∞** | **∞** | — |

`∞` is not a rounding artefact. It means the geometry requires **exactly nought** — a straight
vessel has no inflections, so its Grisan density is zero — and all three AutoMorph implementations
returned something else. On the disc-centred spokes the same quantity is out by 67,796%, 89,966%
and 940%. A program that finds structure in a shape that has none is a more serious finding than
any percentage would be, and it is the clearest single result on this page.

Reading one shape at a time changes the picture in ways the worst-case column cannot show:

- On **`straight`**, the simplest shape there is, PVBM's worst error over everything comparable is
  7.5%, OCULAR's is 50%, AutoMorph's is 100%, and both AutoMorph descendants are at `∞`. A straight
  line is where an implementation has no excuse.
- On **`bifurcation`**, PVBM's junction counts are out by 300% while OCULAR's — measuring with
  PVBM's own helpers — are exactly right. The fork changed something that mattered.
- On **`deep-bifurcation`**, PVBM's junctions are out by 785.7% and OCULAR's by 42.9%.

## 6. Where the fixture is the limit, not the software

**All six implementations fail the Koch curve's Hart τ1 in the same direction and by roughly the
same amount**, and that is evidence about the benchmark rather than about any of them:

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Worst `hart-tau1` on `koch` | 1.19 | 1.45 | 1.20 | 1.26 | 1.39 | 1.14 |

The stored ground truth is **3.160**, which is (4/3)⁴ — the arc-to-chord ratio of a
fourth-generation Koch curve. Every implementation returned between 1.14 and 1.45. Six programs
that disagree with each other about almost everything else do not independently make the same
mistake, and the arithmetic says why they could not have done otherwise. The curve spans
0.34 × 2048 ≈ 696 pixels, so at four generations its finest segment is 696 / 3⁴ ≈ **8.6 pixels**,
while the artery drawn along it is 80 µm at 5 µm per pixel = **16 pixels wide**. The brush is
nearly twice the size of the detail it is painting. Generations three and four are not in the
image, and (4/3)¹ = 1.33 is almost exactly the band every implementation landed in.

**So this row is a defect in the fixture**, and the implementations should not be marked down for
it. The shape needs a coarser generation, a longer reach or a much narrower vessel before its τ1
means anything, and this page will keep saying so until one of those changes.

It follows that the **fractal dimension** stored for this shape deserves the same suspicion, even
though nobody fails it: if only the first generation survives the brush, the drawn object is not a
level-four Koch curve and its box-counting dimension is not log 4 / log 3. Every implementation
lands within tolerance of 1.2619 — which may be agreement, or may be a thick smooth line scoring
about 1.26 for reasons that have nothing to do with the Koch construction. This is a question to
settle, not a finding.

AutoMorph's 542.2% on `hart-tau1` is a separate matter and is **not** this: its worst case is on
the **arc**, where it returns 7.13 against a required 1.11 — a smooth circular arc, at a single
angle, with nothing subtle about it and nothing eroded by the brush.

## 7. Which to reach for, and at what question

There is no best implementation here, and pretending otherwise would mean comparing a column of 83
measurements with a column of 392 as though they answered the same question. What can be said:

- **For vessel calibre, VascX**, and not by a small margin: 1.1% worst error on vein width against
  50.9% to 56.5% for the AutoMorph group, and 1.7% movement under rotation against their 14% to
  60%. The caveat is scope — VascX yields six judged biomarkers against PVBM's twenty-two, and it
  produced nothing comparable at all on the `straight` shape. It is the right tool if calibre is
  what you need and the wrong one if you need breadth.
- **For breadth, PVBM**, which is the only implementation that puts twenty-two canonical biomarkers
  on the table, including the central retinal equivalents and AVR that nothing else here computes.
  Three caveats, all real: it costs 106 seconds an image, it raises on densely vascularised
  segmentations (section 3), and its junction and endpoint counts are unusable — out by up to 785%
  and unstable under rotation besides.
- **For tortuosity, prefer either AutoMorph descendant over AutoMorph itself.** AutoMorphalyzer and
  AutoMorphClass reduced τ1's rotation sensitivity from 258.8% to about 10% and its worst error
  from 542.2% to about 57%. Between the two there is little to choose on accuracy (84% against 82%
  within tolerance), and AutoMorphClass is eight times faster.
- **Do not use Grisan density from any AutoMorph implementation.** It is non-zero where the
  geometry requires zero, out by up to 89,966% on the spokes, and moves by 231% to 400% when the
  image is turned. Nothing here suggests a threshold at which it becomes usable.
- **Do not use junction or endpoint counts from PVBM.** Use OCULAR's, which are measured with
  PVBM's own helpers and are exactly right on `bifurcation` where PVBM's are out by 300%.

Where two are close on accuracy, cost decides: AutoMorphClass at 1.0 second an image and
AutoMorphalyzer at 7.9 are two percentage points apart on agreement, and a hundred times apart from
PVBM on time.

## 8. What these numbers do not say

- **That any of this transfers to photographs.** Every shape here is clean, complete, unbroken and
  drawn to a known scale, with no lesions, no crossings mislabelled and no segmentation error
  upstream. A program that measures a drawn arc correctly has cleared the lowest bar there is.
- **That a quantity with no ground truth is right.** It is unchecked, which is a third thing. Half
  of AutoMorphalyzer's returned columns are in that position.
- **That agreement between two implementations means either is correct.** PVBM and OCULAR share
  code, and so do the three AutoMorph entries; where siblings agree, that is evidence about their
  common ancestor. The only agreement on this page that means anything is agreement across the
  lineage boundaries — and section 6 is what that looks like when it happens for a bad reason.
- **That 25% and 10% are standards.** They are reporting conveniences, chosen so that a table shows
  the handful of quantities worth looking at rather than two hundred rows of nothing. Nothing here
  passes or fails.
- **That the timings are a property of the software alone.** They were measured on one machine, and
  the ratios between them are more trustworthy than any of the absolute figures.

---

**Compiled from** [notebooks/biomarker-synthetic.ipynb](../../notebooks/biomarker-synthetic.ipynb).
