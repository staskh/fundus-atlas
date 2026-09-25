# Synthetic shapes — how the pictures are made

The synthetic biomarker benchmark does not measure photographs. It measures **drawings whose
answers are known**: a straight vessel has a tortuosity of exactly 1, and a program that says
otherwise is wrong rather than merely different.

This page describes the utility that draws them. What the benchmark then does with them is a
separate page — [biomarker-synthetic-docs.md](biomarker-synthetic-docs.md) — and what came out of
measuring every implementation against them is a third:
[biomarker-synthetic-results.md](biomarker-synthetic-results.md).

## Contents

1. [Why drawing is a separate step](#1-why-drawing-is-a-separate-step)
2. [How to run it](#2-how-to-run-it)
3. [What lands in the store](#3-what-lands-in-the-store)
4. [`manifest.csv` — how each picture was framed](#4-manifestcsv--how-each-picture-was-framed)
5. [`ground_truth.csv` — what each picture's geometry requires](#5-ground_truthcsv--what-each-pictures-geometry-requires)
6. [The nine families](#6-the-nine-families)
7. [Everything is stated in microns](#7-everything-is-stated-in-microns)
8. [What the utility refuses to draw](#8-what-the-utility-refuses-to-draw)
9. [What this utility does not do](#9-what-this-utility-does-not-do)

## 1. Why drawing is a separate step

Drawing a shape and measuring it are different kinds of work, and they used to happen in one
command. Separating them buys three things:

- **A run costs no drawing.** Rasterising a shape at 2048 × 2048 pixels takes a moment; repeating
  it for every implementation, on every re-run, is a moment spent again and again for no new
  information.
- **A re-measurement is of the same pictures.** If the drawings were made afresh each time, a
  change to the generator would quietly change what a stored result described. Now the pictures sit
  in files, and a result describes those files.
- **Anybody can look at what is being measured** without running anything, which matters most for
  the reader who does not run Python at all.

The store is **committed to this repository** — the only generated pictures here that are. These
are shapes we drew ourselves rather than anybody else's photographs, so no licence question arises
(`CLAUDE.md` §2.3), and at 864 KB for 36 pictures the cost of keeping them is small against being
able to repeat a measurement on the exact images it was taken on.

## 2. How to run it

```
python -m benchmarks.shapes
```

That writes the whole store with the settings below. Every one can be overridden:

| Option | Default | What it means |
| --- | --- | --- |
| `--into` | `data/synthetic/av` | where the store is written |
| `--family` | all nine | one family, or several separated by commas |
| `--side` | `2048` | the square grid, in pixels |
| `--um-per-px` | `5` | microns per pixel — how much retina one pixel covers |
| `--rotations` | `0,30,60,90` | the angles each family is drawn at, in degrees |
| `--artery-um` | `80` | how wide an artery is, in microns |
| `--vein-um` | `120` | how wide a vein is, in microns |

At those defaults the frame covers **10.2 mm** of retina, an artery is **16 pixels** across, a vein
**24**, and the optic disc's radius is **180**.

**Running it again overwrites the store and produces byte-identical files.** Nothing in the drawing
is random, so a regenerated store is the same store; that is what makes committing it meaningful.

### 2.1 The four angles, and why there are four

0° and 90° sit square with the pixel grid; 30° and 60° do not. That is the whole reason for
drawing more than one: a measurement that walks the pixel lattice instead of the vessel gives a
different answer at 30° than at 0°, and comparing the two is how the benchmark caught exactly that
in one implementation's tortuosity.

**The shape is turned before it is drawn, never after.** Rotating a finished picture would resample
it, and resampling a structure a few pixels wide destroys it — elsewhere in this repository
rescaling one dataset's tracing turned 19 connected pieces into 309. Turning the geometry and
drawing again leaves the pixel grid as the only difference between one angle and another, which is
the difference being asked about.

## 3. What lands in the store

```
data/synthetic/av/
  manifest.csv
  ground_truth.csv
  straight-2048-000-artery.png
  straight-2048-000-vein.png
  straight-2048-000-fov.png
  straight-2048-030-artery.png
  …
```

At the defaults that is **36 pictures** — nine families at four angles — and **108 mask files**,
three per picture.

Each picture is named `<family>-<side>-<angle>`, so `straight-2048-030` is the straight family on a
2048-pixel grid turned 30°. That name is the key in both tables and the stem of all three of its
files, so a row and a picture cannot drift apart.

The three masks are:

| File | What it holds |
| --- | --- |
| `…-artery.png` | the arteries, and nothing else |
| `…-vein.png` | the veins, and nothing else |
| `…-fov.png` | the field of view — the lit circle a fundus camera produces |

They are **one-bit PNGs**: every pixel is a yes or a no. They are deliberately not saved as black
and white greyscale, so that nobody can mistake a mask for an image and threshold it at some value
of their own choosing.

## 4. `manifest.csv` — how each picture was framed

One row per picture, seventeen columns.

| Column | What it means |
| --- | --- |
| `key` | the picture's name, `<family>-<side>-<angle>` |
| `family` | which of the nine shapes it is |
| `side` | the square grid, in pixels |
| `rotation` | the angle it was turned through, in degrees |
| `um_per_px` | microns per pixel |
| `disc_cx`, `disc_cy` | the centre of the optic disc, in pixels, **after** the turn |
| `disc_r` | the disc's radius, in pixels |
| `disc_diameter_um` | the disc's diameter in microns — 1800, a clinically ordinary size |
| `artery_width_um`, `vein_width_um` | how wide each class was drawn, in microns |
| `fov_cx`, `fov_cy`, `fov_r` | the field of view, in pixels |
| `artery`, `vein`, `fov` | the three mask files, named outright |

The disc is given **both** in pixels and in microns on purpose: a measurement needs pixels, and a
reader needs to know whether the disc is a plausible size. The three filenames are written out
rather than left to be reconstructed from the key, so nothing has to know the naming convention in
order to read the store.

## 5. `ground_truth.csv` — what each picture's geometry requires

One row per picture, `key` and then **70 columns**, each a canonical biomarker name of the form
`biomarker/variant/structure` — the vocabulary in [BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md). So
`tortuosity/hart-tau1/artery` is one column, and a value in it is what that picture's arteries
must measure under that particular definition of tortuosity.

Two rules matter more than the rest:

- **An empty cell is not a zero.** A straight vessel does not have a central retinal equivalent of
  nought; it has none, because nothing here reaches the ring such an equivalent is measured over. A
  zero in that cell would be averaged into somebody's table as though it were a measurement. Each
  family fills between 30 and 50 of the 70 columns.
- **The values do not change with the angle.** All four rotations of a family carry identical
  numbers, which is exactly the property the benchmark tests an implementation for. The shapes
  notebook asserts it rather than trusting it.

These values are **derived, not measured**: they come from the geometry of the curve that was
drawn, never from counting the pixels that came out. Computing them from the drawing would make
them agree by construction and test nothing.

## 6. The nine families

| Family | What it settles |
| --- | --- |
| `straight` | tortuosity exactly 1, zero curvature, and a calibre that is exactly the width drawn |
| `arc` | curvature exactly `1/r`; the arc-to-chord ratio `θ / (2 sin(θ/2))` in closed form. The two classes are concentric arcs sharing an angle, so this ratio must come back **equal for both** while the curvature must not |
| `sinusoid` | arc length and the curvature integrals, by numerical integration — there is no elementary formula for the length of a sine wave |
| `bifurcation` | a Y per class splitting at exactly 60°: one junction and three ends each |
| `disjoint` | four parallel vessels per class, alternating artery and vein: no junctions, eight separate pieces, and a neighbour of the other class for every vessel |
| `deep-bifurcation` | three generations of forking per class, some branches forked again and some carrying a short spur, so the junction and endpoint counts are large enough that an off-by-one shows and a skeleton with a defect cannot pass by luck |
| `koch` | the one family with a **known fractal dimension**, `log 4 / log 3` ≈ 1.2619 — every other shape here is smooth, and a smooth curve's dimension is exactly 1, which no box count returns from a bounded raster. It is drawn at **two generations and half the usual vessel width** (40 µm and 60 µm, recorded as such in the manifest): a drawn curve's box dimension is governed by how thick the vessel is rather than how many generations it has, and a generation finer than the vessel is painted over rather than measured. §6.1 |
| `spokes-macula-centred` | twelve vessels radiating from the disc, six per class, every one crossing the ring the central retinal equivalents are measured over. All the widths of a class are equal, so every order of combining them gives the same answer and the shape tests the formula rather than a sorting convention |
| `spokes-disc-centred` | the same retina photographed with the disc in the middle of the frame instead of off to one side |

### 6.1 Why the Koch curve is drawn thinner, and shallower

It is the one family whose parameters are not obvious, and getting them wrong is invisible: the
curve sits well inside the frame and looks exactly as intended.

Drawn at four generations and the usual width, its finest detail was 8.6 pixels under a 24-pixel
vein — the brush wider than what it was painting. Two of the four generations were therefore not in
the picture, and the picture carried an arc-to-chord ratio of 2.18 where the geometry beside it
said 3.16, with a box dimension of 1.51 against 1.2619. Every implementation measured against it
duly disagreed, and the benchmark reported six independent failures where there was one drawing
defect.

Two facts decide the parameters, and only one is the obvious one:

- **The box dimension follows the vessel width, not the depth.** Thickening a curve adds area-like
  scaling at every box size below the width, which pulls the estimate up towards 2: at full width a
  box count returns about 1.41 at every depth tried, and only narrowing brings it down to the
  1.2619 the geometry requires.
- **Depth buys arc length and costs everything else.** Each generation the drawing cannot resolve
  leaves a spurious endpoint where two spikes merged — four generations leave a skeleton with about
  sixty endpoints where the curve has two — and makes the measurement less stable under rotation.

So: the fewest generations that still make the curve self-similar over a useful range, at the width
where the dimension lands. Two and half-width gives an arc-to-chord ratio of 1.84 against a derived
1.78, a box dimension of 1.28 against 1.2619, and about 1% movement when the picture is turned.
`library.koch` refuses to draw a curve whose finest generation is under three times the vessel,
so this cannot silently come back.

**Every family draws both an artery and a vein.** A segmentation of a real eye has both, so a shape
offering one would test a case no implementation ever meets — and it means every family pins the
ratio of the two calibres, the one arteriovenous quantity that needs neither a disc nor a ring.

**The two spokes families are the same eye, framed two ways.** Most fundus photography is
macula-centred, with the disc off to one side; some is disc-centred. The retina is identical, so
their ground truth is identical, and a disc-anchored measurement that comes out differently on the
two is reading the framing rather than the eye.

## 7. Everything is stated in microns

A vessel is 80 or 120 microns across; an optic disc is 1800 microns across. Those become pixels
through the scale the picture is drawn at, so **the same family at 5 µm/px and at 10 µm/px is one
retina photographed twice, not two retinas**.

Note that 1800 µm is the disc's **diameter**. Its radius — 900 µm — is what every zone around it is
counted in, and the two are confused often enough that
[central-retinal-equivalents.md](../biomarkers/central-retinal-equivalents.md) §5 records it as a
trap.

Stating sizes physically makes one consequence visible that is easy to get backwards:

- **Knudtson's central retinal equivalent moves with the resolution.** It is a purely multiplicative
  formula, so computed on pixel widths it comes out in pixels: halve the microns per pixel and it
  doubles. It is the same calibre reported in a different unit.
- **Hubbard's does not move**, because its constants were fitted in microns, so it is computed on
  micron widths and returns microns. The eye did not change, and neither does the number.

An implementation that feeds *pixel* widths into Hubbard's formula is not producing a Hubbard
equivalent awaiting conversion — it is producing a different quantity, which is a defect this
benchmark found in one of them.

## 8. What the utility refuses to draw

The central retinal equivalents are measured over a ring reaching **three disc radii** from the disc
centre — 2700 microns. A frame smaller than about 5.5 mm across cannot contain that ring, **however
many pixels it has**, because the limit is the amount of retina in view rather than the resolution.

Asked for such a frame, the utility raises an error naming the distance and the frame, and draws
nothing:

```
the ring the equivalents are measured over reaches 745 px from the centre of a 1024 px frame,
which is outside its field of view: widen the frame, lower the scale, or move the disc in
```

Drawing it anyway would truncate every vessel crossing the ring, and a width measured on a
truncated vessel is measured on a fragment — so every equivalent derived from it would describe a
ring nobody intended, with nothing in the output to say so.

## 9. What this utility does not do

- **It measures nothing.** It draws pictures and states what their geometry requires. No
  implementation is called here, and no score is computed.
- **It contains no photographs.** Every mask is clean, binary and noiseless. A program that measures
  these exactly may still fail on a segmentation of a real eye, where masks have holes, specks and a
  boundary nobody agrees on — which is a different benchmark's question.
- **It does not choose what is worth measuring.** A quantity no family pins is simply absent from
  the ground truth; that is a gap in the shapes, not a judgement about the quantity.
- **It defines nothing about the fovea**, so anything anchored to the macula — the disc-fovea
  distance, the temporal angle — is out of reach. Inventing a fovea would make the answer a property
  of the fixture.

---

**The code:** `src/benchmarks/shapes/` — `library.py` for the geometry and the derivations,
`store.py` for writing and reading, `__main__.py` for the command. **The pictures, drawn and
explained:** [notebooks/biomarker-synthetic-shapes.ipynb](../../notebooks/biomarker-synthetic-shapes.ipynb).
