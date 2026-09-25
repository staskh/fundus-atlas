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
a paragraph of hedging, the shape is not a test, it is another opinion.

| Family | What is known |
| --- | --- |
| `straight` — a segment of width `w`, length `L` per class | τ1 exactly 1; curvature 0; calibre exactly `w`; skeleton length `L` |
| `arc` — concentric circular arcs, radius `r`, subtending `θ` | curvature exactly `1/r`; τ1 = `θ / (2 sin(θ/2))` in closed form, and equal for both classes because `r` cancels |
| `sinusoid` — amplitude `a`, wavelength `λ` | arc length, total curvature and `∫κ² ds` by integration |
| `bifurcation` — a symmetric Y of angle `φ` per class | branching angle exactly `φ`; one junction and three endpoints per class |
| `disjoint` — `n` parallel segments per class, alternating | junction count 0; `2n` components; and a neighbour of the other class for every vessel |
| `artery-vein-pair` — one vessel per class, widths `wa`, `wv` | AVR exactly `wa / wv`; Knudtson passes a lone vessel through; Hubbard has nothing to pair it with and must decline |
| `spokes-macula-centred` — 6 vessels per class from the disc | the central retinal equivalents: every spoke crosses the annulus at 2–3 disc radii, and all the widths of a class are equal so every pairing order agrees |
| `spokes-disc-centred` — the same, disc in the middle of the frame | the same values exactly. A disc-anchored measurement that differs between the two framings is reading the framing rather than the eye |

Each shape is rendered as an **artery mask and a vein mask** — the two an adapter is handed — with
an explicit **field of view** and an explicit **disc centre and radius**, because the
implementations need them and because a measurement over an unstated region is not reproducible.

**Every shape draws both classes.** A segmentation of a real eye has arteries and veins in it, so a
shape offering one would test a case no implementation ever meets — and it means every family pins
the ratio of the two calibres, which is the one arteriovenous quantity needing neither a disc nor a
ring. Where the two classes trace the same curve, only their widths tell them apart, and every
shape-only quantity must come back the same for both.

**A ratio of the two classes needs both.** The arteriovenous ratio is in scope, so shapes carrying
arteries and veins of known width are too: a pair of straight vessels of widths `wa` and `wv` has
an AVR of exactly `wa / wv` under any variant that is a ratio of calibres, which is what separates
an implementation that computes the ratio from one that computes two equivalents and divides them
at a different stage.

### 2.1 Everything is stated in microns

A vessel is 80 µm across and a vein 120 µm; an optic disc is 1800 µm **across**, so the radius
every zone is counted in is 900 µm. Those become pixels through the scale the shape is drawn at, so
the same shape at 5 µm/px and at 10 µm/px is one retina photographed twice rather than two retinas.

Two consequences are worth stating because they are easy to get backwards:

- **Knudtson's equivalent moves with the resolution** and Hubbard's does not. Knudtson computed on
  pixel widths comes out in pixels, so halving the microns per pixel doubles it; Hubbard computed
  on micron widths comes out in microns and does not move, because the eye did not change.
- **A frame can be too small to hold the ring.** Three disc radii is 2700 µm, so a field of view
  under about 5.5 mm across cannot carry a shape testing the equivalents however many pixels it
  has. The generator refuses rather than drawing a truncated annulus, because every width measured
  in a clipped ring is measured on a fragment.

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

- `src/benchmarks/biomarker_synthetic.py` — the run.
- `src/benchmarks/shapes/library.py` — one function per shape, returning masks, field of view,
  disc, and the theoretical values it defines. Pure geometry, no implementation, no scoring.
- `src/benchmarks/shapes/store.py` and `__main__.py` — writing that to `data/synthetic/av/` and
  reading it back, and the `python -m benchmarks.shapes` command that does it.
- `src/biomarkers/<slug>.py` — one adapter per implementation, per `add-biomarker`.
- `src/biomarkers/naming.py` — the table joining their names to catalogued biomarkers.
- `tests/benchmarks/shapes/` — the theory, tested against itself: a shape whose derivation is wrong
  makes every result wrong and nothing else would catch it.
