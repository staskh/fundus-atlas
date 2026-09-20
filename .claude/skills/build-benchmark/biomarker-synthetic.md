# The synthetic biomarker benchmark

Load this beside `SKILL.md` before building or changing `src/benchmarks/biomarker_synthetic.py`.
Everything here is particular to measuring biomarker code against arithmetic; everything shared is
in the main file.

**What it asks:** does an implementation compute the quantity it is said to compute? Not *does it
agree with another implementation* — two programs can agree and both be wrong — but does it return
the value the definition requires, on a shape whose value is derivable.

```
python -m benchmarks --benchmark biomarker-synthetic
python -m benchmarks --benchmark biomarker-synthetic --model pvbm --dataset straight-vessel
```

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

| Shape | What is known |
| --- | --- |
| Straight segment of width `w`, length `L` | τ1 exactly 1; curvature 0; calibre exactly `w`; skeleton length `L` |
| Circular arc, radius `r`, subtending `θ` | curvature exactly `1/r`; τ1 = `θ / (2 sin(θ/2))` in closed form |
| Sinusoid, amplitude `a`, wavelength `λ` | arc length, total curvature and `∫κ² ds` in closed form |
| Constant-width tree of known total length | vessel area `w × L`; density `wL / |FOV|` |
| Symmetric bifurcation of angle `φ` | branching angle exactly `φ`; one junction; three endpoints |
| Concentric disc and cup | cup-to-disc ratio exactly the radius ratio |
| A network of `n` disjoint segments | junction count 0; `n` components |

Each shape is rendered with an explicit **field of view** and an explicit **disc centre and
radius**, because the implementations need them and because a measurement over an unstated region
is not reproducible.

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

## 4. Rotate the shape, not the picture

Every shape is generated again at each angle **in continuous coordinates and rasterised there**.
Rotating the rendered mask instead would resample it — and resampling a one-pixel-wide structure
destroys it, as this repository measured when a 1,024-pixel rescaling of HRF's tracing turned 19
connected components into 309. A rotated bitmap measures the resampler.

Rotation is about the **disc centre**, because that is the point the disc-anchored measurements are
defined around.

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
- `src/benchmarks/shapes/` — the generator: one function per shape, returning masks, field of view,
  disc, and the theoretical values it defines. Pure geometry, no implementation, no scoring.
- `src/biomarkers/<slug>.py` — one adapter per implementation, per `add-biomarker`.
- `src/biomarkers/naming.py` — the table joining their names to catalogued biomarkers.
- `tests/benchmarks/shapes/` — the theory, tested against itself: a shape whose derivation is wrong
  makes every result wrong and nothing else would catch it.
