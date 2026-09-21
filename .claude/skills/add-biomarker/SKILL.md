---
name: add-biomarker
description: Write the adapter that lets a benchmark compute one project's biomarkers from a segmentation — what it is handed, what it returns, and where the table naming its columns lives. Use when adding or changing anything under src/biomarkers/.
---

# Adding a biomarker adapter

A **biomarker adapter** is one project's measuring code, reached from this repository. It is handed
masks and the disc, and it answers with numbers **under that project's own names**.

**One adapter per implementation, not per biomarker.** PVBM computes a dozen numbers in one pass
over one skeleton; AutoMorph's feature stage does the same. Splitting that into a call per biomarker
would mean running the same work a dozen times, or pretending the numbers are independent when they
come from one traversal. So the unit here is the *implementation* — `src/biomarkers/<slug>.py`,
where the slug matches the project's catalogue page — and the unit in `docs/biomarkers/` stays the
*measurement*. The two are joined by the naming table of section 4, which lives **in the adapter**,
beside the calls whose output it describes.

This differs from the model layer, where one adapter is one model, and from an earlier draft of
`PLAN-BENCHMARK.md` §10.3, which said one adapter per biomarker implementation. The plan records
the change.

## 1. What you produce

1. **The adapter**, `src/biomarkers/<slug>.py`, with the interface of section 2 and a module-level
   `implementation(**arguments)` returning it.
2. **The naming table, in that same file**, mapping every column the implementation computes to a
   catalogued biomarker and variant — or to `None`, which is a finding rather than an omission.
3. **Tests**, `tests/biomarkers/`, written first.
4. **Corrections to the project and biomarker pages**, in the same commit, for whatever reading the
   code taught you that the documentation does not say.

## 2. The interface

```python
class Pvbm:
    slug = "pvbm"                    # the project's catalogue page
    needs = ("artery", "vein", "disc")   # what it cannot run without
    invariant = ("rotation",)        # the invariances it claims; see section 5

    def declare(self) -> dict        # static facts; no disk, no network
    def identity(self) -> str        # what pins the code that will run
    def measure(self, artery, vein, fov, disc, um_per_px) -> dict[str, float | None]
```

`measure` is handed:

| Argument | What it is |
| --- | --- |
| `artery`, `vein` | the two classes, as boolean arrays in one frame — **or `None` for either one**. There is no third vessel mask: an implementation that measures the vessels as one class takes the union of whichever classes it was given, which is how the artery/vein benchmark derives that map for every model. A separately drawn vessel mask would let two adapters measure two different things and call both "vessels" |
| `fov` | the field of view, as a boolean mask: the region the photograph actually shows |
| `disc` | the optic disc as `(x, y, radius)` in pixels — the form every catalogued implementation asks for, rather than a mask |
| `um_per_px` | microns per pixel, or `None` where the caller has no scale. An implementation that needs one and is given `None` returns `None` for the measurements that depend on it, rather than assuming a number |

It returns **one dictionary, keyed by catalogued name** — `biomarker/variant/structure` — for every
column its table maps, and by the implementation's own name for every column the catalogue cannot
name yet. The two are told apart by the `/`. A measurement the implementation could not produce is
`None` with the reason recorded by the run, never 0 and never absent.

**Measure under their names and translate once.** Compute with `CRAE_Knudtson` and `t2` as the
implementation calls them, and rename at the end in a single step, so that what was computed and
what it is called stay separable: a mapping that turns out to be wrong is then corrected in the
table without touching a line of the measuring.

## 3. What an adapter must not do

- **It must not rename anything its table does not cover.** The translation from `t2` to *Hart's τ1
  arc-chord ratio* is a claim about what somebody's code computes, and it is frequently wrong — so
  it is made in one reviewable table and nowhere else, never inline at the call site and never by
  guessing from a column's name.
- **It must not drop a column it cannot name.** A quantity the catalogue has no name for is a gap
  in the catalogue, not a thing to throw away: it is answered under the implementation's own name
  and measured like any other. Dropping it would make a benchmark quietly measure less than the
  implementation computes and hide what the catalogue is missing.
- **It must not convert units silently.** Return what the implementation returns and declare the
  unit. A pixel figure quietly multiplied by a scale is how two studies come to disagree by a
  factor nobody can find.
- **It must not take the union as given.** Where an implementation wants one vessel class, the
  adapter forms the union of the classes it was handed. That is the same derivation the artery/vein
  benchmark applies to every model, so a number measured here and a mask scored there describe the
  same vessels.
- **It must not substitute one class for the other.** Handed `vein=None`, an adapter measures what
  can be measured from arteries alone and returns `None` for everything else — an arteriovenous
  ratio above all, which is a ratio of two things and cannot be had from one. Returning the artery
  figure under a name that promises both is the worst failure available here, because it is
  invisible in the evidence.
- **It must not repair its upstream.** Where an implementation has a defect — retipy's curvature,
  say — the adapter reproduces it and the defect is recorded on the biomarker page. A benchmark of
  fixed code measures the fix rather than the software anybody would actually run.
- **It must not score, choose shapes or datasets, or write files.**

## 4. The naming table is the whole problem

It lives **in the adapter**, at the top of `src/biomarkers/<slug>.py`, mapping each column the
implementation computes to a catalogued `biomarker/variant/structure` or to `None`:

```python
PER_CLASS: dict[str, str | None] = {
    "area": "vessel-area-and-length/area/{side}",
    "median_tortuosity": "tortuosity/hart-tau1/{side}",
    "perimeter": None,          # nothing catalogued describes it — yet
    ...
}
```

It sits beside the calls it describes because the two are read together: what a column is worth
depends on how it was obtained, and a reader checking a mapping against the implementation's source
should not have to hold two files open. Adding an implementation therefore touches one file.

Four rules keep it honest:

- **A mapping is a claim, and the synthetic benchmark is what tests it.** A shape where two variants
  give different known values separates them by measurement. Declare the mapping the documentation
  implies, then let the shapes agree or disagree with it.
- **An entry may map to no variant.** Where an implementation computes something no catalogued
  variant describes, the entry says so, and the biomarker page gains an implementation-only form.
  `docs/biomarkers/tortuosity.md` already records three.
- **Two keys may map to the same variant**, as PVBM's two tortuosity figures do. That is not a
  duplicate: they differ in the region or the aggregation, which the table's comment records.
- **A mapping that a shape contradicts becomes `None`, with the reason beside it.** PVBM's
  `median_branching_angle` was mapped to the angle between a bifurcation's daughters until a shape
  showed it medians every pairwise angle at every junction, the trunk included. The column is still
  measured; it simply no longer claims to be that biomarker.

## 5. Declaring an invariance is declaring something testable

An adapter says which invariances its numbers claim. `rotation` means: rotate the shape about the
disc centre and the number should not move.

**It is not universal, and claiming it wrongly is the point of asking.** A measurement taken over
grid fields aligned to the image axes changes under rotation, correctly. So does anything anchored
to the fovea — which is why the fovea-dependent biomarkers are out of scope for the synthetic
benchmark. Claim what the definition implies; the run checks it.

## 6. Read their code, not their documentation

Same rule as `add-model` §5, and it bites harder here. A biomarker's name is not its definition:
"tortuosity" names at least three incompatible formulas, and papers report the name and omit the
choice. What the adapter declares must come from the implementation's source — which window it
smooths over, which region it measures in, whether it counts pixels or arc length — and whatever
that teaches goes onto the biomarker page in the same commit, marked as this repository's
observation.

## 7. Rules

- **7.1** The slug matches the project's catalogue page. No page, no adapter.
- **7.2** One adapter per implementation; one call returns everything it computes.
- **7.3** Measured under the implementation's names, answered under catalogued ones, translated in
  one table in the adapter — never inline, and never by guessing from a column's name.
- **7.3.1** Every column the implementation computes is stored, including those the catalogue
  cannot name, under the implementation's own name.
- **7.4** Units declared, never silently applied.
- **7.5** An upstream's defect is reproduced and recorded, never quietly fixed.
- **7.6** A class that was not handed over is `None` in every measurement that needs it, never
  replaced by the other class and never assumed empty.
- **7.7** **Hand the masks over in a wide dtype — never `uint8`.** Measuring code writes pixel
  coordinates, labels and running sums into arrays it derives from the mask it was given, and an
  8-bit array silently cannot hold a coordinate on a large frame. PVBM raised
  `OverflowError: Python integer 416 out of bounds for uint8` on a 2048² image and computed no
  equivalents and no fractal dimensions at all; the same call on `float64` answered normally. The
  dtype an adapter chooses is a decision about the numbers, so declare it as a constant with the
  reason beside it rather than writing it inline at each call.
- **7.8** **An adapter that catches an exception records why.** Catching is right — one measurement
  falling over must not lose the rest — but an empty cell with no reason beside it cannot be told
  apart from an implementation that declined, and that ambiguity is expensive: it let rule 7.7's
  defect read for a whole run as PVBM refusing to answer. Publish what was caught (`trouble`,
  keyed by where), and the benchmark writes it into the row's `note`.
