# Synthetic biomarker benchmark — what came out

Six biomarker implementations were run over the same **91 renderings**: thirteen drawn shapes, each
at seven angles from 0° to 90° in steps of 15°. Each rendering is a 2048 × 2048 picture of a 45°
field 12,960 µm across, so 6.33 µm per pixel. It holds arteries 80 µm wide, veins 120 µm wide, and
an optic disc 1,800 µm across with a cup inside it. Nothing here was photographed and nothing was
annotated. Every shape was *drawn* from equations, so the value it ought to give is a matter of
arithmetic rather than of anybody's opinion.

Every number on this page comes from `results/biomarker-synthetic/`, measured on 2026-11-22. The
reading of those numbers comes from [the summary
notebook](../../notebooks/synthetic/biomarker-synthetic.ipynb) and from one notebook per family of
code: [AutoMorph's](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb),
[PVBM's](../../notebooks/synthetic/biomarker-synthetic-pvbm.ipynb) and
[VascX's](../../notebooks/synthetic/biomarker-synthetic-vascx.ipynb). All four were re-run on
2026-11-25. How the benchmark is configured, and the commit each implementation is pinned at, is on
[biomarker-synthetic-docs.md](biomarker-synthetic-docs.md). The shapes and how their values are
derived are on [the shapes page](biomarker-synthetic-shapes.md) and in [the shapes
notebook](../../notebooks/synthetic/biomarker-synthetic-shapes.ipynb).

> **This page was rewritten from scratch on 2026-11-25**, from the current evidence only. Earlier
> versions drew conclusions from earlier runs and earlier adapters; those conclusions are withdrawn
> rather than carried forward, and the earlier pages remain in the repository's history. Where a
> finding here repeats an old one, it is because the current numbers show it again.

**The six implementations come from three families of code, and the page keeps them in that
order.** [PVBM](../projects/pvbm.md) and [OCULAR](../projects/ocularnet.md) form one family, because
OCULAR calls PVBM's measuring code. [AutoMorph](../projects/automorph.md) and its two rewrites,
[AutoMorphalyzer](../projects/automorphalyzer.md) and
[AutoMorphClass](../projects/automorphclass.md), form a second. [VascX](../projects/vascx.md)
shares code with none of them. When two members of one family differ, somebody changed something on
purpose. When two families differ, two programs that never shared a line of code read the same
definition differently. When two members of one family agree, that is one piece of evidence about
their shared code, not two.

## Contents

1. [Summary](#1-summary)
2. [Does the answer change when the picture is turned?](#2-does-the-answer-change-when-the-picture-is-turned)
3. [Does the answer agree with the geometry?](#3-does-the-answer-agree-with-the-geometry)
4. [What raised an error instead of answering](#4-what-raised-an-error-instead-of-answering)
5. [Each family on its own](#5-each-family-on-its-own)
6. [The unnamed columns, held to their own description](#6-the-unnamed-columns-held-to-their-own-description)
7. [Which to reach for, and at what question](#7-which-to-reach-for-and-at-what-question)
8. [What these numbers do not say](#8-what-these-numbers-do-not-say)

## 1. Summary

The benchmark asks two questions of every number a program returns:

- **Is it steady?** The same shape is drawn again at seven angles. The geometry is identical every
  time, so a number that moves is the program (or the pixel grid under it) and not the eye. This
  check needs no right answer, so it covers every column a program returns.
- **Is it right?** Each shape comes with the value its geometry requires for every biomarker the
  [catalogue](../BIOMARKER-NAMES.md) has a name for. This check covers only the columns that can be
  matched to such a name.

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Columns returned | 30 | 18 | 72 | 66 | 60 | 132 |
| …that move by more than 10% when the picture turns | 24 / 30 | 13 / 18 | 52 / 68 | 24 / 44 | 48 / 56 | 38 / 109 |
| …matching a catalogued biomarker | 20 | 10 | 57 | 40 | 33 | 6 |
| …of those, more than 25% from the geometry somewhere | 15 / 20 | 4 / 10 | 43 / 57 | 19 / 39 | 18 / 33 | 2 / 6 |
| Measurements with a value to compare against | 1,748 | 882 | 4,146 | 3,013 | 2,877 | 153 |
| …within 25% of the geometry | 93% | 97% | 77% | 76% | 80% | 91% |
| …median distance from the geometry | 4.9% | 0.0% | 8.6% | 5.6% | 6.7% | 0.0% |
| Exceptions raised | 0 | 0 | 42 | 21 | 0 | 0 |
| Seconds per image | 64.9 | 4.8 | 8.5 | 7.3 | 0.5 | 9.3 |

*From the summary notebook, §1 and §5.* The two counts in the second and fourth rows have different
denominators on purpose. Steadiness can be checked on every column that returned a number, except
the vertical and horizontal cup-to-disc ratios, which are *meant* to change when the picture turns
(they are read along the image's axes). Agreement can be checked only on the columns with a
catalogued name and a shape that settles their value.

**Read the table down a column, not across a row.** The columns are not answering the same
question: VascX's 0.0% median covers 153 measurements of six biomarkers, and AutoMorph's 8.6% covers
4,146 of fifty-seven. Measuring a little, carefully, is a defensible choice and a different
achievement from measuring a lot.

**Two thresholds decide which rows the tables show, and neither is a standard.** A number "moves"
when its spread across the seven angles — the highest value minus the lowest, as a share of their
mean — exceeds 10% on some shape. A number "disagrees" when it is more than 25% from the geometry's
value on some shape at some angle. Both are reporting conveniences. Nothing here passes or fails.

**Under both sits a noise floor of 1% of each biomarker's own size**, meaning the largest value the
shapes require of it anywhere. A difference below the floor counts as agreement, and no percentage
is divided by anything smaller. Where the geometry requires exactly nought (a straight vessel has no
tortuosity), the percentage is taken against the floor instead, so an error there reads as a large
multiple such as "329,877×". Read those against the values themselves, which §3 gives.

## 2. Does the answer change when the picture is turned?

A fundus photograph is never taken at exactly the same angle twice: the head tilts, the camera is
set differently, and left and right eyes are mirror images. A biomarker that changes when the same
eye is turned in the frame mixes the eye's geometry with the photographer's. This is the check that
needs no ground truth, so it is the one every column gets.

**The headline: most biomarkers move, and the ones that move most are tortuosity and vessel width
in the AutoMorph family.** 57 of the 79 catalogued biomarkers checked here move by more than 10% in
at least one family, *even counting only that family's steadiest member* (summary notebook, §6.3).

### 2.1 By family, at the steadiest member

Each family answers a biomarker with whichever of its members moves least, so a cell is the best
that family's code can do. A dash means no member of that family computes it. Selected rows from the
summary notebook's §6.3, which lists all 57:

| Biomarker | AutoMorph family | PVBM family | VascX |
| --- | --- | --- | --- |
| Vessel width, arteries, length-weighted | 63.0% | — | 4.0% |
| Vessel width, veins, length-weighted | 33.4% | — | 1.9% |
| Vessel width, veins, zone C | 163.6% | — | — |
| Knudtson's arterial equivalent (CRAE), zone B | 4.3% | 27.0% | 4.1% |
| Knudtson's venular equivalent (CRVE), zone B | 4.1% | 11.9% | 1.9% |
| Hubbard's arteriovenous ratio (AVR), zone B | 8.1% | 26.3% | — |
| Arc over chord (Hart τ1), arteries, length-weighted | 11.2% | 12.9% | 12.8% |
| Arc over chord (Hart τ1), veins, length-weighted | 7.4% | 8.4% | 10.4% |
| Arc over chord (Hart τ1), veins, median | — | 36.7% | — |
| Grisan's tortuosity density, veins, zone B | 364.0% | — | — |
| Grisan's tortuosity density, all vessels | 182.6% | — | — |
| Box-counting dimension, arteries, zone B | 45.7% | — | — |
| Skeleton length from the disc, arteries | — | 34.7% | — |
| Junction count, arteries | — | 210.0% | — |
| Junction count, veins | — | 200.0% | — |

*Terms.* The central retinal arterial and venular equivalents (CRAE, CRVE) summarise the widths of
the six largest arteries or veins around the disc into one figure each, by Hubbard's or Knudtson's
formula, and their ratio is the AVR. Zone B is the ring half a disc diameter to one disc diameter
from the disc's edge, and zone C extends it to two. Hart's τ1 is a vessel's length along its course
over the straight distance between its ends: 1 for a straight vessel, more for a winding one.
Grisan's tortuosity density counts and weighs the changes in a vessel's direction.

The same table, by family of biomarker (summary notebook, §6.4): of the biomarkers each family
answers, how many hold within 10% under rotation at its steadiest member.

| Family of biomarker | AutoMorph family | PVBM family | VascX |
| --- | --- | --- | --- |
| Calibre (width, CRAE, CRVE, AVR) | 9 / 21 | 0 / 6 | 4 / 4 |
| Density (area, fractal dimension) | 5 / 12 | 5 / 10 | — |
| Landmarks (disc and cup diameters) | 2 / 2 | — | — |
| Topology (junctions) | — | 0 / 2 | — |
| Tortuosity | 8 / 30 | 1 / 4 | 0 / 2 |

VascX's two tortuosity columns miss the 10% line by 2.8 and 0.4 points (12.8% and 10.4%). The
AutoMorph family's eight are all arc over chord, from the two rewrites; none of its Grisan densities
holds.

### 2.2 Why things move

Comparing the values at each angle in the group notebooks (§3.3 of each) shows where the movement
comes from. It comes from a handful of mechanisms, and each is visible on the simplest shapes.

**Width measured along the image's axes (AutoMorph family).** On a straight vessel AutoMorph's
`average_width_artery` is 72 px at 0°, 98 px at 45° and 72 px again at 90°. AutoMorphalyzer goes
from 77 to 106 and back. The ratio, about 1.36, is close to √2 (1.41): what a width measured along
the image's rows or columns, instead of straight across the vessel, gives on a diagonal. It shows
wherever vessels are straight and nearly disappears on curved shapes, which run in every direction
so the error averages out. AutoMorph and AutoMorphClass share this code and return the same widths.
AutoMorph's equivalents (CRAE, CRVE) do not show it: its zone-B ones move by 9.5% at most.

**A diagonal line read as tortuous (AutoMorph family).** On the same straight vessel AutoMorph's
Grisan density is 0 at 0° and 90° and about 0.15 at most angles in between. A diagonal line drawn in
pixels is a staircase, and the measurement counts the steps as changes of direction. All three
members do it. AutoMorphClass's values are about fifty times smaller and swing the same way.

**AutoMorph's own arc over chord breaks on curved shapes at some angles only.** On the arc shape the
vein's arc over chord is 1.15 at 0° and 167 at 45°, and the squared-curvature column next to it goes
from 1.17 to 1,585. No arc is 167 times longer than its chord, so at those angles the program is not
measuring the drawn vessel. Both rewrites fixed this: their arc over chord moves by 7–12% over the
whole picture.

**Junction counts on a self-approaching curve (PVBM family).** On the Koch curve, a single unbranched
vessel folded back close to itself, PVBM reports 0 to 4 junctions depending on the angle. Whether two
folds touch in the pixel picture depends on the turn. Counts that small make a difference of two read
as 200%. OCULAR returns the same numbers because it runs PVBM's code. On every other shape the count
does not move.

**Regions that do not turn with the picture (VascX).** VascX's density split into superior and
inferior halves moves by 117% or 700%, the signature of a whole vessel changing halves: 700% is one
angle in seven with a value, and 117% is six. On the straight shape the vein's density is 0.0075 in
the inferior half at 0–75°, then 0 there and 0.0075 in the superior half at 90°. The density of the
whole field does not move. None of these columns has a catalogued name.

**Curvature on axis-aligned vessels (VascX).** VascX's curvature-based tortuosity reads a straight
artery as 0.19 at 0°, almost 0 at 30–60°, and 0.07 at 90°: a straight vessel looks curved when it
lies *along* the image's axes. On the macula-centred spokes it is about 0.003 at six angles and 0.41
at the seventh. These columns have no catalogued name either. VascX's arc over chord, which does,
moves by 12.8% at most.

**Without a diagnosed mechanism:** PVBM's Hubbard and Knudtson equivalents move by 10–27%, its median
arc over chord by up to 37%, and its multifractal dimensions by about 10%. PVBM's singularity length
(an unnamed multifractal measure) mirrors itself around 45° on a straight vessel, which points at
the pixel grid, as one would expect of box counting on a shape this simple.

### 2.3 What holds steady

These move by no more than about 10% on any shape:

- **VascX's calibre**: length-weighted artery and vein widths and its zone-B Knudtson equivalents,
  1.9–4.1%.
- **AutoMorph's zone-B equivalents**: Hubbard's and Knudtson's CRAE and CRVE and both AVRs,
  3.5–9.5%. Its zone-C ones reach 10.4%.
- **The rewrites' arc over chord**: AutoMorphalyzer's means over the whole picture and zone C,
  7.0–11.9%, and AutoMorphClass's whole-picture length-weighted one, 7.4–11.2%. Both are worse in
  zone B (up to 25.9% and 45.5%).
- **The disc and the cup**: AutoMorph's family reads the disc's diameters to within 1.3% at every
  angle, and follows the cup-to-disc ratios through the swap that turning requires to within 1.9%.
- **PVBM's vessel area** for arteries and veins, and AutoMorphalyzer's box-counting dimension
  (6.1–10.6%).

### 2.4 The columns nothing can check against the geometry

Most of what VascX returns, and some of every other program, has no catalogued name. Rotation is the
only check those columns get (summary notebook, §3.1). Of VascX's 109 unnamed columns, 36 move by
more than 10%: the hemifield and half-circle densities and the curvature tortuosities described
above. Of AutoMorph's 15, 12 move, nine of them squared-curvature columns that swing by 418–700%.
AutoMorphClass's 27 include 25 that move. PVBM's branching angle, endpoint and singularity columns
move by 25–67%; OCULAR's, which are the same code, move identically.

## 3. Does the answer agree with the geometry?

Here the comparison is with the value the shape's equations require, worked out before anything was
drawn. A disagreement is a fault, not a difference of opinion — with one qualification. Each value
says how it is known: `exact` (a closed form), `numerical` (averaged on a 20 µm grid), `asymptotic`
(a limit, such as a fractal dimension, that no finite picture reaches) or `convention` (a choice the
definition leaves open, such as reading a crossing as two vessels). A fault against an exact value
is a fault; one against a convention is a question about the definition.

### 3.1 Where two or more families answer the same biomarker

Only ten biomarkers are answered by more than one family, and four by all three (summary notebook,
§6.2). Each cell is the closest member's worst error over every shape and angle.

| Biomarker | AutoMorph family | PVBM family | VascX |
| --- | --- | --- | --- |
| Knudtson's CRAE, zone B | 42.4% | 28.5% | 2.9% |
| Knudtson's CRVE, zone B | 67.4% | 30.4% | 2.4% |
| Vessel width, arteries, length-weighted | 58.7% | — | 2.7% |
| Vessel width, veins, length-weighted | 40.3% | — | 2.2% |
| Hubbard's CRAE, zone B | 52.9% | 30.9% | — |
| Hubbard's CRVE, zone B | 63.0% | 55.8% | — |
| Hubbard's AVR, zone B | 13.8% | 47.0% | — |
| Knudtson's AVR, zone B | 19.6% | 17.9% | — |
| Arc over chord, arteries, length-weighted | 9.2% | 23.9% | 43.5% |
| Arc over chord, veins, length-weighted | 9.5% | 9.5% | 43.4% |

**On calibre VascX is ten times closer than either other family.** Its worst case is under 3%; the
PVBM family's Knudtson equivalents are 28–30% out at worst and the AutoMorph family's 42–67%. The
AutoMorph family's worst calibre cases are diagonal vessels, the √2 of §2.2.

**On arc over chord the order reverses.** AutoMorphClass is within 9.5%, OCULAR level with it on
veins and 23.9% out on arteries, and VascX 43% out. VascX's whole error is on the Koch curve, where
it reads 1.005 for a value of 1.778: it calls a crinkled curve straight. On the other twelve shapes
it is within tolerance.

**On Hubbard's ratio AutoMorph is within 13.8% where PVBM is 47.0% out**, although both are far out
on the equivalents themselves. PVBM's Hubbard CRVE (225 µm required, 350.6 returned on the disc-centred
spokes at 45°) and its AVR are worst on the shapes built to settle them.

### 3.2 What each family gets right and wrong on its own

- **AutoMorph family.** Right: the cup-to-disc ratios, within 1.9% on every shape and angle
  (AutoMorphalyzer exactly), and the disc's diameters, within 1.3%. Vessel density over the image, within 1.3% for all
  vessels. Wrong: Grisan's tortuosity density, 170,000–335,000 times the floor in AutoMorph and
  AutoMorphalyzer and 3,300–6,300 times in AutoMorphClass, on shapes whose geometry requires 0 — on a
  straight vessel AutoMorph returns about 0.15. AutoMorph's own mean arc over chord, up to 161 times
  the true value. Width, 59–184% out over the whole picture and up to 233% in zone C.
  AutoMorphalyzer's AVRs are 50% out at the median: where both of its equivalents failed, it divides
  −1 by −1, gets 1, and keeps it. That accounts for 120 of its 148 faults against `convention`
  values; its zone-C Knudtson equivalents account for the other 28.
- **PVBM family.** Right: vessel area, within 1.7% (veins) and 5.0% (arteries); skeleton length of
  veins, within 4.5%. Wrong: the junction count, 3 or 4 junctions on the Koch curve, which has
  none, and 10 for 7 on the deep bifurcation. Hubbard's equivalents, consistent with Hubbard's
  micron constants applied to pixel widths. The multifractal dimensions, 26–33% from their
  asymptotic value of 1 on the spokes.
- **VascX.** Right: its four calibre biomarkers, within 2.2–2.9%. Wrong: arc over chord on the Koch
  curve only.

### 3.3 By how the value is known

Faults (more than 25% out) over all comparable measurements, by kind (summary notebook, §4.3):

| Kind | automorph | automorphalyzer | automorphclass | pvbm | ocular | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| exact | 777 / 3,285 | 560 / 2,600 | 496 / 2,352 | 59 / 808 | 19 / 854 | 14 / 153 |
| asymptotic | 95 / 777 | 7 / 252 | 91 / 525 | 61 / 546 | — | — |
| convention | 63 / 84 | 148 / 161 | — | 7 / 394 | 7 / 28 | — |

### 3.4 Where the geometry gives no value

Some biomarkers have no value on some shapes: a straight vessel has no branching angle, and on the
`disjoint` shape nothing reaches zone B. The right answer there is nothing. Of 518 such chances, 42
were answered with a number, all by AutoMorphClass: its six zone-B tortuosity columns on `disjoint`,
at all seven angles, including an arc over chord of 0.0 — a value no curve can have. Every other
implementation declined every time (summary notebook, §4.4).

### 3.5 The one answer that is a word

AutoMorphalyzer is the only implementation that reports whether a photograph is centred on the disc
or the macula. It answered correctly on every rendering of every shape.

## 4. What raised an error instead of answering

63 exceptions in all, every one on the `disjoint` shape, whose vessels never reach the disc
(summary notebook, §2). **AutoMorph** raised 42: its zone stage finds no measuring window in the
empty zones B and C, at every angle, for arteries, veins and both together. Its own pipeline writes
−1 there, which this benchmark reads as no answer — the right answer for an empty zone.
**AutoMorphalyzer** raised 21: a division by zero in each of its three measuring passes at every
angle. No other implementation raised anything.

An exception and a wrong number are different failures. A program that raises has said it could not
answer. One that returns a confident wrong number, as AutoMorphClass does on the same shape (§3.4),
has not.

## 5. Each family on its own

**AutoMorph family** ([notebook](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb)). The
three return 72, 66 and 60 columns. The cup-to-disc ratios and the zone-B equivalents are their
strongest results, and both are steady. Width and Grisan density are their weakest, and both move
with the picture for reasons §2.2 traces to the pixel grid. Between the members: the rewrites fixed
AutoMorph's arc over chord (from up to 161 times out to 15–23% in AutoMorphalyzer and under 10% in
AutoMorphClass's whole-picture value) and kept its Grisan density. AutoMorphClass is the fastest
program here at 0.5 s an image.

**PVBM family** ([notebook](../../notebooks/synthetic/biomarker-synthetic-pvbm.ipynb)). PVBM and
OCULAR return the same number wherever they share a column. PVBM adds the central retinal
equivalents, the AVRs and the multifractal dimensions, and takes 64.9 s an image; OCULAR adds a
length-weighted arc over chord, at 4.8 s. Area and length are where this family is trustworthy;
junction counts are where it fails, and they are also its least steady numbers.

**VascX** ([notebook](../../notebooks/synthetic/biomarker-synthetic-vascx.ipynb)). VascX returns 132
columns, of which only six have a catalogued name. Its four calibre biomarkers are the most accurate
and the steadiest of their kind here. Most of the rest are the same few quantities over regions
built on the line from the disc to the fovea. On a synthetic shape that line is this benchmark's
convention, so those columns are checked only for rotation, and the half-field ones fail it.

## 6. The unnamed columns, held to their own description

A column the catalogue cannot name is still checked against the geometry when what its authors say
it computes is something a shape can settle. This compares the authors' claim with what the program
does (group notebooks, §5).

| | pvbm | ocular | automorph | automorphalyzer | automorphclass | vascx |
| --- | --- | --- | --- | --- | --- | --- |
| Checked against their own description | 8 | 8 | 15 | 11 | 12 | 20 |
| …more than 25% out somewhere | 5 | 5 | 9 | 0 | 6 | 13 |

- **PVBM's tortuosity index** (total arc length over total chord length) is within 15.8% at worst.
  Its **endpoint count** leaves out the end at the disc, so it counts the free tips of vessels
  rather than every end, and its **median branching angle** is up to 129% out.
- **AutoMorph's and AutoMorphClass's squared-curvature column** is named for Hart's integral of
  squared curvature and returns tens to tens of thousands of times that value.
- **AutoMorphalyzer's** unnamed columns all land within 25%.
- **VascX's** density inside its own disc-centred circle is right on every shape but the deep
  bifurcation (57–59% out there). Its mean branching angle is 29–49% out at the median, and its
  segment-capped arc over chord fails on the Koch curve as the catalogued one does.

## 7. Which to reach for, and at what question

*Our reading of the evidence above, on the run of 2026-11-22.* There is no overall best program here.
Each family answers different questions, they overlap on only ten biomarkers, and each has one
failure the others do not share. So the answer depends on the question, and steadiness under
rotation is given equal weight with agreement, because a photograph's angle is never controlled.

| Question | Reach for | Its worst error / worst movement | Runner-up, and the margin | Caveat that would change the answer | Seconds an image |
| --- | --- | --- | --- | --- | --- |
| Vessel calibre (width, Knudtson's CRAE and CRVE) | VascX | 2.2–2.9% / 1.9–4.1% | PVBM family, 28.5–30.4% / 11.9–27.0%: not close | judged on three shapes only; VascX answers four calibre biomarkers, the AutoMorph family twenty-one | 9.3 |
| Hubbard's AVR | AutoMorph | 13.8% / 8.1% | PVBM, 47.0% / 26.3%: not close | AutoMorph's Hubbard equivalents themselves are 53–63% out at worst | 8.5 (PVBM 64.9) |
| Arc over chord, whole picture | AutoMorphClass (length-weighted) | 9.2–9.5% / 7.4–11.2% | OCULAR: level on veins (9.5% / 8.4%), 23.9% on arteries | AutoMorphClass is 60% out in zone B and invents a value where zone B is empty | 0.5 (OCULAR 4.8) |
| Cup-to-disc ratio | any AutoMorph member; AutoMorphalyzer is exact | 0–1.9% | no other family computes it | a drawn ellipse is the easiest cup there is | 0.5–8.5 |
| Vessel area | PVBM family (OCULAR for speed) | 1.7–5.0% / steady | AutoMorph family's density over the image, a different biomarker | the two families measure differently named things and are not directly compared | 4.8 |
| A number that does not depend on how the eye sat in the frame | VascX's six catalogued columns | 2.2–43.5% / 1.9–12.8% | AutoMorph's zone-B equivalents: steadier (3.5–9.5%) but 42–73% out at worst | VascX's unnamed half-field and curvature columns move by up to 700% | 9.3 |
| Junctions, branching | none | PVBM family 43–57× on `koch`, 210% movement | — | only one family answers, and it fails | — |
| Grisan's tortuosity density | none | up to 335,000× and 364% movement | — | only one family answers, and it fails | — |

**The timings measure the machine as much as the program.** They come from the seconds each result
records on one run; the evidence does not record the device. Read the ratios — PVBM takes about 130
times as long as AutoMorphClass, and OCULAR about a fourteenth of PVBM's time for the numbers they
share — rather than the absolute figures.

## 8. What these numbers do not say

- **That any of this transfers to photographs.** Every shape here is clean, complete, unbroken and
  drawn to a known scale, with no lesions and no segmentation error upstream. A program that
  measures a drawn arc correctly has cleared the lowest bar there is.
- **That a column with no ground truth is right, or wrong.** It is unchecked, apart from rotation.
- **That two implementations agreeing means either is right.** PVBM and OCULAR share code, and so do
  the three AutoMorph members.
- **That 10% and 25% are standards.** They choose which rows a table shows.
- **That a fault against a `convention` or `asymptotic` value is the same as one against an `exact`
  value.** §3.3 keeps them apart.
- **That every rotation fault matters equally.** Turning the picture moves a few quantities by
  design: the cup-to-disc ratios read along the image's axes, which are left out of every rotation
  count. The half-field columns of VascX are not left out, because their halves are meant to follow
  the disc and fovea, which turn with the picture.
- **That the angles tested cover every case.** Seven angles from 0° to 90° cover a quarter turn.
  Mirror images, as between a left and a right eye, are not tested.
