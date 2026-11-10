# The synthetic biomarker benchmark

Load this beside `SKILL.md` before building or changing `src/benchmarks/biomarker_synthetic.py`.
Everything here is particular to measuring biomarker code against arithmetic; everything shared is
in the main file.

**What it asks:** does an implementation compute the quantity it is said to compute? Not *does it
agree with another implementation* — two programs can agree and both be wrong — but does it return
the value the definition requires, on a shape whose value is derivable.

**It is two steps, and they are separate commands.** Drawing a shape is rasterising; measuring one
is running somebody's code over it. Keeping them apart means a run costs no rasterising, a change
to an implementation re-measures the *same* pictures rather than pictures redrawn from a generator
that may have moved underneath, and anybody can look at what is being measured without running
anything.

```
python -m benchmarks.shapes                      # draw the store, once
python -m benchmarks --benchmark biomarker-synthetic          # measure what is in it
python -m benchmarks --benchmark biomarker-synthetic --model pvbm --dataset straight
```

The store is `data/synthetic/av/`, committed: a binary mask per class, a field of view, a
`manifest.csv` of how each rendering was framed, and a `ground_truth.csv` of what its geometry
requires. It is committed because these are our own shapes, so a measurement can be repeated
against the exact pictures it was taken on.

The benchmark's name carries a hyphen and a Python module name cannot, so the module is
`biomarker_synthetic.py` and `report._module` translates. The name with the hyphen is what appears
in `results/`, in `docs/benchmarks/` and on every page.

## 1. It measures against theory, not against an annotator

Every other benchmark here compares software with a human judgement recorded in a dataset. This one
compares software with a number derived on paper. That changes two things:

- **There is no ground truth to be uncertain about.** A straight vessel has tortuosity exactly 1.
  Where an implementation disagrees, the implementation is wrong — subject to section 3.
- **There is no contamination question**, and no `unknown` mark. A shape nobody trained on cannot
  be in-sample.

What it catches that no dataset can: a factor of two in a curvature formula, a centreline extractor
that counts pixels where it should measure arc length, a tortuosity that moves when a vessel is
rotated by 45°.

## 2. The shapes, and what each one settles

A shape earns its place only if its value can be **written down plainly**. If the derivation needs
a paragraph of hedging, the shape is not a test, it is another opinion — and where one quantity on
an otherwise plain shape does rest on a reading, that value is marked `convention` rather than the
shape being dropped (section 2.2).

**Each shape is a retina stated in microns** (`shapes/scene.py`): a 45° camera whose frame spans
12,960 µm, a disc 1,800 µm across, and each class a network of centreline paths — nodes, segments of
constant width, and the angle at each fork — whose curvature and corners are carried exactly. The
model and the derivations follow `evaluation/synthetic` in fundus-biomarkers, brought into the open
because a ground truth is a reading of the catalogue's definitions (`PLAN-BIOMARKER.md` §5.3); no
tracing or measuring code of that library comes with them.

| Shape | What is known |
| --- | --- |
| `straight` — one vessel per class from the disc | τ1 exactly 1; curvature 0; calibre exactly `w`; one vessel crossing zone B |
| `arc` — one angle, two radii | curvature exactly `1/r`; τ1 = `θ / (2 sin(θ/2))`, equal for both classes because `r` cancels |
| `clothoid` — curvature linear in arc length | `∫κ ds = κL/2`, `∫κ² ds = κ²L/3` |
| `sinusoid` — amplitude `a`, wavelength `λ` | arc length and the curvature integrals by summation; three inflections; Grisan's density |
| `bifurcation` — a fork per class, Murray daughters | branching angle exactly `φ`; one junction, three ends; two widths, so mean, median and length-weighted mean differ |
| `tree` — two generations of forks | three junctions and five ends per class; whole vessels sharing their trunk |
| `deep-bifurcation` — three generations, a stub per junction | seven four-way junctions, sixteen ends; the branching angle a `convention` |
| `spur` — a 500 µm side branch | counted by the definition, dropped by a minimal leaf length |
| `crossing` — an artery over an artery | two vessels, not a junction; every count resting on that a `convention` |
| `disjoint` — parallel orphans | no rooted length, no whole vessels, nothing in either zone |
| `koch` — two generations, half width | box-counting and multifractal dimensions `log 4 / log 3` (`asymptotic`); τ1 = `(4/3)²` |
| `spokes-macula-centred` — 6 vessels per class to 3.4 disc radii | the central retinal equivalents in zone B; every width of a class equal, so every pairing order agrees |
| `spokes-disc-centred` — the same, disc in the middle, to 5.4 radii | the same zone-B values exactly, zone C as well, and the centring `disc`. A disc-anchored measurement that differs between the two framings is reading the framing rather than the eye |

Each shape is rendered as an **artery mask and a vein mask** — the two an adapter is handed — with
an explicit **field of view** and an explicit **disc centre and radius**, because the
implementations need them and because a measurement over an unstated region is not reproducible.
**Pixel `i`'s centre is at `i`**, the convention of an array index and of every disc estimate in
`results/disc_estimation/`, so the disc handed over sits exactly on the disc the masks were drawn
around.

**Every shape draws both classes.** A segmentation of a real eye has arteries and veins in it, so
a shape offering one would test a case no implementation ever meets — and it means every shape
pins the ratio of the two calibres, the one arteriovenous quantity needing neither a disc nor a
zone.

### 2.1 Every value, over every region it is defined in

The ground truth is derived **per region** — the field of view, zone B (2–3 disc radii) and zone C
(2–5) — by clipping each centreline in continuous coordinates, and **per structure**: `artery`,
`vein`, `vessels` where the vocabulary defines a biomarker over both classes as one, and `both` for
the ratios. Nothing is derived that the vocabulary does not name, and a name derived for an artery
or a vein that the vocabulary rejects is an error rather than a column.

The cup-to-disc ratios are not derived: an adapter is handed the disc as a circle and no cup.

### 2.2 How a value is known, and when there is none

Every value carries one of four kinds, in `ground_truth_kind.csv` beside `ground_truth.csv`:
`exact`, `numerical` (sparsity, on a 20 µm grid), `asymptotic` (a fractal dimension, which no finite
raster reaches) and `convention` (rests on a reading the geometry alone does not settle). The
analysis may weigh them differently; it must not pool them silently.

**No value is a value.** Where the geometry offers nothing to measure — no junction to take an
angle at, no vessel in zone C, no whole vessel when nothing reaches the disc — the truth is *none*: a
kind with an empty cell. That is not zero and it is not "not settled", and an implementation that
returns a number there is wrong. Where the shape settles nothing at all — a Koch curve's squared
curvature, infinite at its corners — both cells are empty.

### 2.3 Everything is stated in microns

A vessel is 80 µm across and a vein 120 µm; an optic disc is 1800 µm **across**, so the radius
every zone is counted in is 900 µm. The frame always spans the same field, so the side decides the
scale — 6.33 µm per pixel at 2048 — and the same shape on two grids is one retina photographed twice
rather than two retinas.

- **Knudtson's equivalent is scale-free** and Hubbard's is not. Knudtson computed on pixel widths
  comes out in pixels and converts like any length; Hubbard's additive constants were fitted in
  microns and only mean anything on micron widths.
- **A vessel that leaves the field is refused**, not clipped: every width, length and count
  measured on a truncated vessel is measured on a fragment.

## 3. A rasterised shape is not the shape

The theory describes a continuous curve; the implementation sees pixels. The difference is real and
it is nobody's bug: a vessel of width 3 has a boundary that a square grid cannot represent, and a
diagonal line is a staircase.

**So the benchmark renders every shape at several resolutions and reports the error at each.** The
shape of that error is the finding:

- **converging towards theory** as the grid refines — the implementation computes the quantity, and
  the residue is discretisation;
- **flat at a constant offset** — a systematic error in the formula, which no resolution will fix;
- **growing** — a bug that the grid makes worse, usually a per-pixel step treated as unit length.

A single tolerance at a single resolution cannot tell these apart, which is why this benchmark does
not have one.

**Expect a sawtooth, not a smooth curve.** What separates a drawn shape from its geometry is at
most about one row of pixels along the vessel, and whether that row is taken depends on where the
centreline falls between pixel centres. So the error can rise between two resolutions without
anything being wrong; the generator's own tests bound it by one row rather than asserting it
falls. Read the trend across four resolutions, never the step between two.

## 4. Rotate the shape, not the picture

Every shape is generated again at each angle **in continuous coordinates and rasterised there**.
Rotating the rendered mask instead would resample it — and resampling a one-pixel-wide structure
destroys it, as this repository measured when a 1,024-pixel rescaling of HRF's tracing turned 19
connected components into 309. A rotated bitmap measures the resampler.

**Seven angles, every 15° of a quarter turn**, which holds every orientation of the pixel lattice.

**Rotation turns the whole scene about the frame centre, disc included.** Turning about the disc
was the first idea and building it showed it to be wrong: the disc sits near the top of the frame,
so a vessel a third of a frame away sweeps a circle wide enough to leave the field of view, and a
clipped vessel measures something other than the shape. Turning everything together keeps every
distance — vessel to vessel, vessel to disc — exactly as it was, and a circular field of view is
unchanged by the turn.

**An invariance is checked only where the adapter claims it** (`add-biomarker` §5). A measurement
over axis-aligned grid fields changes under rotation and is right to.

## 5. What is kept

`results/biomarker-synthetic/<implementation>/<shape>.csv`, one row per rendering — per resolution,
per rotation, per parameter setting — holding:

- the shape and its parameters, so a row can be re-derived without the generator;
- the resolution and the rotation;
- **every key the implementation returned, under its own name**, and the theoretical value where
  the shape defines one;
- the seconds it took.

The theoretical value sits **beside** the returned one rather than being subtracted from it in the
evidence: a difference is an analysis, and the analysis belongs in the notebook.

## 6. What this benchmark does not do

- **It does not select.** Which implementations are fit for the dataset benchmark is a judgement
  made by a person, later, on the evidence this produces. No pass mark, no ranking, no automated
  bound. A benchmark that also chose would be choosing by a rule nobody agreed.
- **It does not say a number is wrong because it disagrees with another implementation.** That is
  the comparison this benchmark exists to make unnecessary.
- **It says nothing about photographs.** An implementation that measures a synthetic vessel exactly
  may still fail on a segmentation of a real eye, which is the next benchmark's question.

## 7. Where the code goes

- `src/benchmarks/biomarker_synthetic.py` — the run. It measures the **stored** renderings, read
  back by `store.load`, never a fresh drawing: the store is what the fingerprint's digest describes.
- `src/benchmarks/shapes/scene.py` — the retina in microns: paths, networks, the camera and the disc.
- `src/benchmarks/shapes/library.py` — one function per shape, returning a scene; `build` draws one
  and attaches its truth. Pure geometry, no implementation, no scoring.
- `src/benchmarks/shapes/truth.py` — every value a scene settles, by canonical name, with its kind.
- `src/benchmarks/shapes/render.py` — a scene drawn on a frame of any side at any angle.
- `src/benchmarks/shapes/store.py` and `__main__.py` — writing that to `data/synthetic/av/` and
  reading it back, and the `python -m benchmarks.shapes` command that does it.
- `src/biomarkers/<slug>.py` — one adapter per implementation, per `add-biomarker`, each holding the
  table joining its names to catalogued biomarkers.
- `tests/benchmarks/shapes/` — the theory, tested against itself: a shape whose derivation is wrong
  makes every result wrong and nothing else would catch it.
