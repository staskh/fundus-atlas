# Biomarkers against arithmetic — how it is run

**What this benchmark does, in one paragraph.** It runs several biomarker-extraction programs over
the *same* set of **synthetic** fundus images — drawings rather than photographs — and compares
every number each one returns against the value that image is *known* to have. The images are
drawn from geometry, so their ground truth is not somebody's annotation of a real eye but a
quantity calculated in advance: a straight vessel has a tortuosity of exactly 1, a 90° circular arc
has a curvature of exactly 1/r, and twelve vessels of known width have a central retinal equivalent
that Knudtson's recursion fixes to the decimal. An implementation that disagrees with one of those
is **wrong**, not merely different from its neighbours — which is what no comparison of two
programs against each other can ever establish.

This page says how that is configured: what it asks, which programs take part, which images they
run on, how to run it, and what every column of its evidence means.

**It is part generated and part written.** The tables and lists between the `generated` markers are
rendered from what the benchmark reports about itself and are refreshed by
`python -m benchmarks --benchmark biomarker-synthetic --docs`, which measures nothing. Everything
else on the page is written by hand and is never overwritten. What *came out* of a run is written
up separately, on one page holding every implementation — section 8.

## 1. What this benchmark asks

<!-- generated: asks -->
**Does a biomarker implementation compute the quantity it is said to compute?** Every other benchmark here compares software with a human judgement; this one compares it with a number derived on paper. A straight vessel has a tortuosity of exactly 1, a circular arc a curvature of exactly 1/r, and an implementation that disagrees is wrong rather than different. It selects nothing: which implementations are fit to measure a real segmentation is a judgement made by a person on this evidence.
<!-- /generated -->

Its shapes and the derivations behind their values are in
[the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb); how the pictures are drawn
is [biomarker-synthetic-shapes.md](biomarker-synthetic-shapes.md).

## 2. What takes part

Each implementation is reached through an adapter that measures it **as it ships** — no defect is
corrected on its behalf, and each answers under catalogued biomarker names so that two of them line
up column by column. A column the catalogue cannot name yet is kept under the implementation's own
name rather than dropped.

<!-- generated: subjects -->
| Implementation | Pinned at | Columns it returns | Took part |
| --- | --- | --- | --- |
| [pvbm](../projects/pvbm.md) | `5edb79a` | 30 | yes |
| [ocular](../projects/ocularnet.md) | `34b1ecc` | 18 | yes |
| [automorph](../projects/automorph.md) | `9a953e5` | 18 | yes |
| [automorphalyzer](../projects/automorphalyzer.md) | `e68843e` | 54 | yes |
| [automorphclass](../projects/automorphclass.md) | `8f4d18f` | 18 | yes |
| [vascx](../projects/vascx.md) | `d0cde1c` | 20 | yes |
<!-- /generated -->

Three of them share a lineage and one does not: AutoMorph, AutoMorphalyzer and AutoMorphClass all
descend from retipy, OCULAR imports PVBM's helpers at runtime, and VascX reimplements every
measurement independently. That is why they are written up in families rather than one by one.

## 3. What they are measured on

Every shape is a drawing whose values follow from its geometry rather than from anybody's opinion,
so a disagreement is an error rather than a difference. Each carries both an artery and a vein,
and each is drawn at four angles — 0°, 30°, 60° and 90° — where the geometry is identical and only
the pixel grid differs.

<!-- generated: material -->
| Shape | What its geometry settles | Available |
| --- | --- | --- |
| `straight` | 247 quantities with a known value | yes |
| `arc` | 199 quantities with a known value | yes |
| `sinusoid` | 243 quantities with a known value | yes |
| `bifurcation` | 58 quantities with a known value | yes |
| `deep-bifurcation` | 58 quantities with a known value | yes |
| `disjoint` | 52 quantities with a known value | yes |
| `koch` | 72 quantities with a known value | yes |
| `spokes-macula-centred` | 56 quantities with a known value | yes |
| `spokes-disc-centred` | 56 quantities with a known value | yes |
<!-- /generated -->

## 4. How to run it

<!-- generated: running -->
```bash
python -m benchmarks --benchmark biomarker-synthetic
python -m benchmarks --benchmark biomarker-synthetic --model pvbm --dataset straight
python -m benchmarks --benchmark biomarker-synthetic --docs
```

| Flag | What it does |
| --- | --- |
| `--model` | one implementation, or several separated by commas |
| `--dataset` | one shape, or several separated by commas |
| `--max-samples` | draw only the first N of the four angles, for a development run |
| `--force` | discard what is stored and measure it all again |
| `--docs` | refresh this page from the declarations, measuring nothing |
<!-- /generated -->

## 5. What each column of the evidence means

<!-- generated: columns -->
`results/biomarker-synthetic/<implementation>/<shape>.csv` holds one row per rendering:

| Column | Meaning |
| --- | --- |
| `key` | the rendering: the shape and the angle it was drawn at |
| `shape` | which shape was drawn — `straight`, `arc`, `spokes-macula-centred` and the rest |
| `rotation` | the angle it was drawn at, in degrees, generated afresh rather than turned |
| `side` | the grid it was drawn on, in pixels |
| `um_per_px` | the microns per pixel the shape was built with |
| `outcome` | `measured` if any quantity came back, else `failed`; `note` says what fell over |
| `seconds` | how long the implementation took over this rendering |
| `said_<key>` | what the implementation returned, under **its own** column name — what its authors call that number and what a reader checking against their documentation will look for. No value to compare against sits beside it: the ground truth lives in the store's `ground_truth.csv`, the catalogued name each column answers to is in the adapter's declaration, and joining the three is the analysis's work rather than the run's |
| `note` | what an implementation failed with |
<!-- /generated -->

A column an implementation does not compute is **absent** rather than blank, and one it computes
but the catalogue cannot name keeps its own name — recognisable by carrying no `/`.

## 6. What a re-run repeats, and what it does not

<!-- generated: fingerprint -->
A stored result is kept only while everything it depends on is unchanged. This benchmark fingerprints:

- this benchmark's name and `VERSION`
- a sha256 of the masks this shape is drawn as, so a redrawing re-measures it
- the facts each implementation declares that bear on its numbers: slug, needs, keys, units, recursion
- the pinned commit of the code that will run, as the adapter reports it
- the rendering: a 2048px grid at 5 µm per pixel, drawn at 0°, 30°, 60°, 90°

A fingerprint that differs means the stored result describes something that no longer exists, and it is measured again from nothing. **How much was done is not part of it**, because that does not change what any rendering scored: a complete result is never re-run, and a partial one is finished rather than restarted.
<!-- /generated -->

## 7. The counts every result carries

<!-- generated: counts -->
| Count | What it answers |
| --- | --- |
| `processed` | how many angles of this shape the implementation has measured |
| `total` | how many it was asked for |
| `complete` | whether those are all of them |
| `seconds_per_rendering` | how long the implementation took, on the device named beside it |
<!-- /generated -->

## 8. Where the results are written up

In **one** page, [biomarker-synthetic-results.md](biomarker-synthetic-results.md), compiled from
the single notebook [`notebooks/biomarker-synthetic.ipynb`](../../notebooks/biomarker-synthetic.ipynb).

Every implementation appears in it together, and that is the point rather than a convenience. The
question this benchmark asks is whether these programs compute the same quantity, and that question
lives **across** a row — one catalogued biomarker, one column per implementation — so a page per
implementation would have nothing left to compare. The columns stand in lineage order, siblings
beside each other, so that a difference between neighbours reads as a change somebody made on
purpose and a difference across a boundary reads as two independent programs.

## 9. The biomarkers it can name

Every implementation here answers under **catalogued names**, so that two of them can be read
against each other. This is that vocabulary — the fixed list in `src/biomarkers/canonical.py`,
where a name is a claim that two numbers under it are comparable, and adding one is a decision
rather than a side effect of whatever an implementation happened to return.

**What the last column means.** A biomarker has a *ground truth* here when at least one synthetic
image carries a pre-computed value for it — the answer its geometry requires, derived on paper
before anything was drawn and stored beside the image in `ground_truth.csv` — see
[how the images are made](biomarker-synthetic-shapes.md). Those are the only biomarkers this benchmark
can judge: an implementation's number is compared with that value, and a disagreement is an error
with a size. A biomarker with no ground truth is still **measured and stored** — every
implementation's answer for it is in the evidence — but there is nothing to compare it against, so
the benchmark reports it and says nothing about whether it is right.

A name is `family / biomarker / structure / [roi] / [statistic]`, and
[BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) §1 is the authority on it. The **biomarker** is the
definition rather than the family name, because "tortuosity" names at least three incompatible
formulas and a table that merged them would be comparing different quantities. The **structure** is
what the measurement was taken over; `both` is reserved for a measurement that is inherently a
ratio of the two classes, which is the arteriovenous ratio and nothing else. The **region** and the
**statistic** may be left off a name a reader writes, and are spelt out in every name this
benchmark records — `tortuosity/hart-tau1/artery/median` and `.../length-weighted` are two
statistics of one measurement, and three of the implementations here differ in exactly that.

The table below lists each definition once, in its short form. The whole field of view is the
region unless one is named, and the shapes settle values over the field of view only — nothing
here is drawn to pin a zone-B measurement except the equivalents, which are defined over that
ring and nowhere else.

<!-- generated: biomarkers -->
34 definitions, most applying to one or more structures (`artery`, `vein`, `vessels`, `both`) and taking a region and a statistic besides — see [BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) §1. **30 of them have a ground truth here** — a value computed from the geometry of at least one synthetic image, which is what an implementation's answer is compared against. The rest are measured and stored, and compared against nothing. **Every unit below is physical**: a length in microns, never in pixels, so one number is comparable with another taken at a different resolution.

**[calibre](../biomarkers/calibre.md)**

| Canonical name | What it measures | Units | Ground truth here |
| --- | --- | --- | --- |
| `calibre/width/<structure>` | the width of a vessel, measured along it | µm | yes |
| `calibre/CRE-knudtson/<structure>` | Knudtson's equivalent — CRAE on arteries, CRVE on veins | µm | yes |
| `calibre/CRE-hubbard/<structure>` | Hubbard's equivalent over the same ring | µm | yes |
| `calibre/AVR-knudtson/<structure>` | arteriolar over venular equivalent, both Knudtson | 1 | yes |
| `calibre/AVR-hubbard/<structure>` | the same, both Hubbard | 1 | yes |
| `calibre/AVR-ratio/<structure>` | mean artery width over mean vein width, no ring and no equivalent | 1 | yes |

**[tortuosity](../biomarkers/tortuosity.md)**

| Canonical name | What it measures | Units | Ground truth here |
| --- | --- | --- | --- |
| `tortuosity/hart-tau1/<structure>` | arc length over chord length; 1 for a straight vessel | 1 | yes |
| `tortuosity/hart-tau2/<structure>` | total curvature, ∫κ ds — the total turning angle | 1 | yes |
| `tortuosity/hart-tau3/<structure>` | total squared curvature, ∫κ² ds | 1/µm | yes |
| `tortuosity/hart-tau4/<structure>` | mean curvature, ∫κ ds / s — compositional | 1/µm | yes |
| `tortuosity/hart-tau5/<structure>` | mean squared curvature, ∫κ² ds / s — compositional | 1/µm² | yes |
| `tortuosity/hart-tau6/<structure>` | total curvature over chord | 1/µm | yes |
| `tortuosity/hart-tau7/<structure>` | total squared curvature over chord | 1/µm² | yes |
| `tortuosity/grisan-density/<structure>` | Grisan's density over constant-sign subsegments | 1/µm | yes |
| `tortuosity/inflection-count/<structure>` | how many times the curvature changes sign | 1 | yes |
| `tortuosity/arc-chord-times-inflections/<structure>` | τ1 multiplied by the inflection count | 1 | yes |
| `tortuosity/spline-curvature/<structure>` | curvature sampled along a fitted spline | 1/µm | yes |

**[density](../biomarkers/density.md)**

| Canonical name | What it measures | Units | Ground truth here |
| --- | --- | --- | --- |
| `density/area/<structure>` | total vessel area | µm² | yes |
| `density/skeleton-length/<structure>` | total centreline length | µm | yes |
| `density/over-fov/<structure>` | vessel area as a fraction of the field of view | 1 | yes |
| `density/over-image/<structure>` | the same over the whole frame, lit or not — it names its own denominator | 1 | yes |
| `density/sparsity/<structure>` | distance from retina to the nearest vessel | µm | yes |
| `density/box-counting/<structure>` | box-counting dimension | 1 | yes |
| `density/multifractal-d0/<structure>` | capacity dimension | 1 | yes |
| `density/multifractal-d1/<structure>` | information dimension | 1 | yes |
| `density/multifractal-d2/<structure>` | correlation dimension | 1 | yes |

**[topology](../biomarkers/topology.md)**

| Canonical name | What it measures | Units | Ground truth here |
| --- | --- | --- | --- |
| `topology/junctions/<structure>` | how many places three or more branches meet | 1 | yes |
| `topology/endpoints/<structure>` | how many free ends the network has | 1 | yes |
| `topology/components/<structure>` | how many separate pieces the network is in | 1 | yes |
| `topology/branching-angle/<structure>` | the angle between the two daughter vessels at a bifurcation | degrees | yes |
| `topology/temporal-angle/<structure>` | the angle between the superior and inferior temporal arcades | degrees | — |

**[landmarks](../biomarkers/landmarks.md)**

| Canonical name | What it measures | Units | Ground truth here |
| --- | --- | --- | --- |
| `landmarks/CDR-vertical` | the cup's vertical diameter over the disc's | 1 | — |
| `landmarks/CDR-area` | the cup's area over the disc's | 1 | — |
| `landmarks/disc-fovea-distance` | the straight-line distance from the disc centre to the fovea | µm | — |
<!-- /generated -->

**A biomarker without a ground truth is a gap in the images, not a verdict on an implementation.**
It means no shape drawn so far defines what the answer should be — so the fix is a new shape whose
geometry settles it, not a change to anybody's code. Which implementation answers under which name
is a separate table, in [BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md).

## 10. What this benchmark does not do

- **It does not measure photographs.** Every shape is clean, binary and noiseless. An
  implementation that measures a synthetic vessel exactly may still fail on a segmentation of a
  real eye, which is a different benchmark's question.
- **It does not select.** No implementation passes or fails here. Which is fit to measure a real
  segmentation is a judgement made by a person on this evidence.
- **It cannot test anything anchored to the fovea**, because a synthetic shape has no macula and
  inventing one would make the answer a property of the fixture.
- **It checks only what a shape pins.** A quantity no shape defines is measured, stored, and
  compared against nothing — which is a gap in the shapes rather than a verdict on the
  implementation.
