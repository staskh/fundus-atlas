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
6. [The thirteen shapes](#6-the-thirteen-shapes)
7. [Everything is stated in microns](#7-everything-is-stated-in-microns)
8. [What the utility refuses to draw](#8-what-the-utility-refuses-to-draw)
9. [What this utility does not do](#9-what-this-utility-does-not-do)
10. [Where the shapes come from](#10-where-the-shapes-come-from)

## 1. Why drawing is a separate step

Drawing a shape and measuring it are different kinds of work. Separating them buys three things:

- **A run costs no drawing.** Rasterising a shape at 2048 × 2048 pixels takes a moment; repeating
  it for every implementation, on every re-run, is a moment spent again and again for no new
  information.
- **A re-measurement is of the same pictures.** If the drawings were made afresh each time, a
  change to the generator would quietly change what a stored result described. Now the pictures sit
  in files, a result describes those files, and a digest of them is part of every result's
  fingerprint.
- **Anybody can look at what is being measured** without running anything, which matters most for
  the reader who does not run Python at all.

The store is **committed to this repository** — the only generated pictures here that are. These
are shapes we drew ourselves rather than anybody else's photographs, so no licence question arises
(`CLAUDE.md` §2.3), and at 3.3 MB for 91 pictures the cost of keeping them is small against being
able to repeat a measurement on the exact images it was taken on.

## 2. How to run it

```
python -m benchmarks.shapes
```

That writes the whole store with the settings below. Every one can be overridden:

| Option | Default | What it means |
| --- | --- | --- |
| `--into` | `data/synthetic/av` | where the store is written |
| `--family` | all thirteen | one shape, or several separated by commas |
| `--side` | `2048` | the square grid, in pixels |
| `--rotations` | `0,15,30,45,60,75,90` | the angles each shape is drawn at, in degrees |

**The frame always shows the same retina**: a 45° camera at 288 µm of retina per degree, so the
frame is 12.96 mm across whatever its side. The side therefore decides the scale — **6.33 µm per
pixel** at 2048 — and there is no separate scale to set. At the default an artery is **12.6
pixels** across, a vein **19.0**, and the optic disc's radius is **142**.

**Running it again overwrites the store and produces identical pictures.** Nothing in the drawing
is random, so a regenerated store is the same store; that is what makes committing it meaningful.

### 2.1 The seven angles

Every 15° of a quarter turn, which holds every orientation of the pixel lattice: 0° and 90° sit
square with the grid, 45° is its diagonal, and the four between are where a staircase is least
regular. A measurement that walks the lattice instead of the vessel gives a different answer at 30°
than at 0°, and comparing the angles is how the benchmark catches it.

**The scene is turned before it is drawn, never after**, and **it turns as a whole, disc included,
about the frame centre.** Rotating a finished picture would resample it, and resampling a structure a
few pixels wide destroys it — elsewhere in this repository rescaling one dataset's tracing turned 19
connected pieces into 309. Turning the geometry and drawing again leaves the pixel grid as the only
difference between one angle and another, which is the difference being asked about.

## 3. What lands in the store

```
data/synthetic/av/
  manifest.csv
  ground_truth.csv
  ground_truth_kind.csv
  straight-2048-000-artery.png
  straight-2048-000-vein.png
  straight-2048-000-fov.png
  straight-2048-015-artery.png
  …
```

At the defaults that is **91 pictures** — thirteen shapes at seven angles — and **273 mask files**,
three per picture.

Each picture is named `<shape>-<side>-<angle>`, so `straight-2048-030` is the straight shape on a
2048-pixel grid turned 30°. That name is the key in all three tables and the stem of all three of
its files, so a row and a picture cannot drift apart.

The three masks are:

| File | What it holds |
| --- | --- |
| `…-artery.png` | the arteries, and nothing else |
| `…-vein.png` | the veins, and nothing else |
| `…-fov.png` | the field of view — the lit circle a fundus camera produces |

They are **one-bit PNGs**: every pixel is a yes or a no, lit when the pixel's centre lies inside the
drawn vessel. They are deliberately not saved as black and white greyscale, so that nobody can
mistake a mask for an image and threshold it at some value of their own choosing.

## 4. `manifest.csv` — how each picture was framed

One row per picture, seventeen columns.

| Column | What it means |
| --- | --- |
| `key` | the picture's name, `<shape>-<side>-<angle>` |
| `family` | which of the thirteen shapes it is |
| `side` | the square grid, in pixels |
| `rotation` | the angle it was turned through, in degrees |
| `um_per_px` | microns per pixel — 12,960 µm over the side |
| `disc_cx`, `disc_cy` | the centre of the optic disc, in pixels, **after** the turn |
| `disc_r` | the disc's radius, in pixels |
| `disc_diameter_um` | the disc's diameter in microns — 1800, a clinically ordinary size |
| `artery_width_um`, `vein_width_um` | how wide each class's trunk was drawn, in microns. A shape whose daughters narrow by Murray's law has more than one width; its ground truth carries every one |
| `fov_cx`, `fov_cy`, `fov_r` | the field of view, in pixels |
| `artery`, `vein`, `fov` | the three mask files, named outright |

**Pixel `i`'s centre is at `i`** — the convention an array index has, and the one every disc
estimate in `results/disc_estimation/` has — so the frame's centre is at 1023.5 on a 2048 grid, and
the disc handed to an implementation sits exactly on the disc the masks were drawn around.

## 5. `ground_truth.csv` — what each picture's geometry requires

One row per picture, `key` and then **one column per canonical biomarker name** some shape settles —
925 of them, 295 of those for the vessels as one class — each of the form `family/biomarker/structure/[region]/[statistic]` from
[BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md). So `tortuosity/hart-tau1/artery/B/median` is one
column, and a value in it is what that picture's arteries must measure under that definition of
tortuosity, pooled by median over the pieces inside zone B.

Every value is derived over **three regions** — the whole field of view, zone B (two to three disc
radii from the disc centre) and zone C (two to five) — and for **four structures**: arteries, veins,
the vessels as one class where the vocabulary defines a biomarker over them, and `both` for the
ratios of the two.

**`ground_truth_kind.csv`** has the same rows and columns and says how each value is known:

| Kind | Means |
| --- | --- |
| `exact` | a closed form, or integrated along the centreline to far below any measurement's error |
| `numerical` | averaged on a 20 µm grid — sparsity, the distance from the retina to its nearest vessel |
| `asymptotic` | a limit no finite raster reaches: a fractal dimension |
| `convention` | rests on a reading of the definition the geometry alone does not settle — a crossing read as two vessels, a lone vessel passed through Knudtson's pairing, the "daughters" of a junction of four |

Three things are kept apart, because they are different facts:

- **A value** — a number in `ground_truth.csv`, or a word for the photograph's centring.
- **No value** — a kind in `ground_truth_kind.csv` and an empty cell beside it. The geometry says
  there is nothing to measure: no junction to take an angle at, no vessel in zone C to pool, no whole
  vessel when nothing reaches the disc. An implementation is right to return nothing here and wrong
  to return a number.
- **Nothing settled** — empty in both. The shape says nothing about it: a Koch curve's squared
  curvature is infinite at every corner, so no tortuosity built on it is stated there.

**The values do not change with the angle.** All seven rotations of a shape carry identical
numbers, which is exactly the property the benchmark tests an implementation for; the shapes
notebook asserts it rather than trusting it.

These values are **derived, not measured**: they come from the geometry that was drawn — clipped,
integrated and counted in microns — never from the pixels that came out. Computing them from the
drawing would make them agree by construction and test nothing.

## 6. The thirteen shapes

All but one are photographed macula-centred, with the disc 2.6 mm right of the frame centre, and
every one but `disjoint` leaves the optic disc at its margin, as vessels do. Arteries are 80 µm and
veins 120 µm unless the shape says otherwise.

| Shape | What it settles |
| --- | --- |
| `straight` | tortuosity exactly 1, zero curvature, a calibre exactly the width drawn, and a lone vessel crossing zone B |
| `arc` | curvature exactly `1/r`; the arc-to-chord ratio `θ / (2 sin(θ/2))` in closed form. The two classes bend through the same 70° about different radii, so this ratio must come back **equal for both** while the curvature integrals must not |
| `clothoid` | an Euler spiral, curvature rising linearly along it: `∫κ ds = κL/2` and `∫κ² ds = κ²L/3` — the one shape whose curvature varies without changing sign |
| `sinusoid` | arc length and the curvature integrals by summing along the exact curve, three inflections, and Grisan's density — the one shape whose curvature changes sign |
| `bifurcation` | a fork per class at exactly 60°, its daughters narrowed by Murray's law: one junction, three ends, two widths to pool, and whole vessels that turn by 30° at the fork |
| `tree` | two generations of forks at 70°, Murray widths by generation: three junctions and five ends per class |
| `deep-bifurcation` | three generations of forks at one width, with a stub off every junction: seven junctions of four branches and sixteen ends, so an off-by-one in the counting shows. Which two branches of a four-way junction are its daughters is a reading, so its branching angle is a `convention` |
| `spur` | a 500 µm side branch at right angles: counted by the definition, dropped by any implementation keeping only leaves longer than that |
| `crossing` | an artery crossed by an artery that never reaches the disc — two vessels, not a junction — so every count resting on that reading is a `convention` while the widths and areas stay `exact` |
| `disjoint` | three parallel vessels per class that never reach the disc: no rooted length, no whole vessels, nothing in zone B or C |
| `koch` | the one shape with a **known fractal dimension**, `log 4 / log 3` ≈ 1.2619, and an arc-to-chord ratio of `(4/3)²`. Drawn at two generations and **half the usual width** — §6.1 |
| `spokes-macula-centred` | six vessels per class radiating to 3.4 disc radii, every one crossing zone B. All the widths of a class are equal, so every order of combining them gives the same central retinal equivalent and the shape tests the formula rather than a sorting convention |
| `spokes-disc-centred` | the same retina with the disc in the middle of the frame, the spokes reaching 5.4 disc radii and so crossing zone C too. Its zone-B values are the macula-centred shape's exactly; a disc-anchored measurement that differs between the two is reading the framing rather than the eye. Its centring is `disc`, every other shape's `macula` |

### 6.1 Why the Koch curve is drawn thinner, and shallower

It is the one shape whose parameters are not obvious, and getting them wrong is invisible: the
curve sits well inside the frame and looks exactly as intended.

Drawn at four generations and the usual width, its finest detail was narrower than the vein painted
along it — the brush wider than what it was painting — and the picture carried an arc-to-chord
ratio of 2.18 where the geometry beside it said 3.16, with a box dimension of 1.51 against 1.2619.
Every implementation measured against it duly disagreed, and an earlier version of this benchmark
reported six independent failures where there was one drawing defect.

Two facts decide the parameters:

- **The box dimension follows the vessel width, not the depth.** Thickening a curve adds area-like
  scaling at every box size below the width, which pulls the estimate up towards 2; only narrowing
  brings it down to the 1.2619 the geometry requires.
- **Depth buys arc length and costs everything else.** Each generation the drawing cannot resolve
  leaves a spurious endpoint where two spikes merged, and makes the measurement less stable under
  rotation.

So: two generations over 4.5 mm, at 40 and 60 µm. Its finest piece is 500 µm — over eight times
the wider vessel.

## 7. Everything is stated in microns

A vessel is 80 or 120 microns across; an optic disc is 1800 microns across; the field is 12,960. Those
become pixels through the scale the picture is drawn at, so **the same shape on a 1024 and on a 2048
grid is one retina photographed twice, not two retinas**, and every value in the ground truth is the
same for both.

Note that 1800 µm is the disc's **diameter**. Its radius — 900 µm — is what every zone around it is
counted in, and the two are confused often enough that
[calibre.md](../biomarkers/calibre.md) §5 records it as a trap.

Stating sizes physically makes one consequence visible that is easy to get backwards:

- **Knudtson's central retinal equivalent** is a purely multiplicative formula, so computed on pixel
  widths it comes out in pixels, and the same conversion turns it into microns.
- **Hubbard's** has constants fitted in microns — an additive +450.05 for venules — so it can only be
  computed on micron widths. An implementation that feeds *pixel* widths into it is not producing a
  Hubbard equivalent awaiting conversion; it is producing a different quantity, which is a defect
  this benchmark found in one of them.

## 8. What the utility refuses to draw

**A vessel that leaves the field of view.** Every shape is checked before it is drawn, and one whose
vessel — centreline plus half its width — reaches beyond the 6,480 µm radius of the field raises an
error naming the shape, the class and the distance:

```
out: an artery reaches 9040 µm from the centre, outside the field of view (6480 µm)
```

Drawing it anyway would truncate the vessel, and everything measured on a truncated vessel is
measured on a fragment — a length, a tortuosity, a width crossing zone C — so the ground truth beside
it would describe a vessel nobody drew, with nothing in the output to say so.

## 9. What this utility does not do

- **It measures nothing.** It draws pictures and states what their geometry requires. No
  implementation is called here, and no score is computed.
- **It contains no photographs.** Every mask is clean, binary and noiseless. A program that measures
  these exactly may still fail on a segmentation of a real eye, where masks have holes, specks and a
  boundary nobody agrees on — which is a different benchmark's question.
- **It does not hand over a cup.** An implementation is given the disc as a centre and a radius, so
  the cup-to-disc ratios cannot be formed and are not in the ground truth.
- **It defines nothing about the fovea**, so anything anchored to the macula — the disc-fovea
  distance, the temporal angle — is out of reach. Inventing a fovea would make the answer a property
  of the fixture.

## 10. Where the shapes come from

The scene model — a retina in microns, vessels as networks of centrelines whose curvature and
corners are carried exactly — and the derivation of every value from it follow `evaluation/synthetic`
in [fundus-biomarkers](../projects/fundus-biomarkers.md), at the commit the atlas pins. They are
brought here, rewritten against this catalogue's vocabulary, for the reason `PLAN-BIOMARKER.md` §5.3
gives: what a biomarker *is* is decided in the open, and a ground truth is a reading of those
definitions, so it belongs where anybody can disagree with it. None of that library's tracing or
measuring code is here, and none is needed: the ground truth reads the geometry, not a segmentation.

Two things are this repository's own: the `deep-bifurcation` shape, and the values for the vessels as
one class.

---

**The code:** `src/benchmarks/shapes/` — `scene.py` for the retina in microns, `library.py` for the
shapes, `truth.py` for the derivations, `render.py` for the drawing, `store.py` for writing and
reading, `__main__.py` for the command. **The pictures, drawn and explained:**
[notebooks/biomarker-synthetic-shapes.ipynb](../../notebooks/biomarker-synthetic-shapes.ipynb).

*Last checked: 2026-11-10.*
