---
name: add-biomarker
description: Write the adapter that lets a benchmark compute one project's biomarkers from a segmentation — what it is handed, what it returns, and why it never renames anything. Use when adding or changing anything under src/biomarkers/.
---

# Adding a biomarker adapter

A **biomarker adapter** is one project's measuring code, reached from this repository. It is handed
masks and the disc, and it answers with numbers **under that project's own names**.

**One adapter per implementation, not per biomarker.** PVBM computes a dozen numbers in one pass
over one skeleton; AutoMorph's feature stage does the same. Splitting that into a call per biomarker
would mean running the same work a dozen times, or pretending the numbers are independent when they
come from one traversal. So the unit here is the *implementation* — `src/biomarkers/<slug>.py`,
where the slug matches the project's catalogue page — and the unit in `docs/biomarkers/` stays the
*measurement*. The two are joined by the naming table of section 4.

This differs from the model layer, where one adapter is one model, and from an earlier draft of
`PLAN-BENCHMARK.md` §10.3, which said one adapter per biomarker implementation. The plan records
the change.

## 1. What you produce

1. **The adapter**, `src/biomarkers/<slug>.py`, with the interface of section 2 and a module-level
   `implementation(**arguments)` returning it.
2. **Rows in the naming table**, `src/biomarkers/naming.py`, mapping every key the adapter can
   return to a catalogued biomarker and variant — or to nothing, which is a finding rather than an
   omission.
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
    def measure(self, masks, fov, disc, um_per_px) -> dict[str, float | None]
```

`measure` is handed:

| Argument | What it is |
| --- | --- |
| `masks` | `artery`, `vein` and `vessels`, as boolean arrays in one frame. **All three, always** — an implementation that wants only the union takes `vessels`, one that measures the two separately takes the classes, and neither has to derive what the other needs |
| `fov` | the field of view, as a boolean mask: the region the photograph actually shows |
| `disc` | the optic disc as `(x, y, radius)` in pixels — the form every catalogued implementation asks for, rather than a mask |
| `um_per_px` | microns per pixel, or `None` where the caller has no scale. An implementation that needs one and is given `None` returns `None` for the measurements that depend on it, rather than assuming a number |

It returns **one dictionary, the implementation's own keys**. `CRAE_Knudtson` stays
`CRAE_Knudtson`; `t2` stays `t2`, however uninformative. A measurement the implementation could not
produce is `None` with the reason recorded by the run, never 0 and never absent.

## 3. What an adapter must not do

- **It must not rename.** The translation from `t2` to *Hart's τ1 arc-chord ratio* is the naming
  table's job, reviewed on its own, because that translation is a claim about what somebody's code
  computes and it is frequently wrong.
- **It must not convert units silently.** Return what the implementation returns and declare the
  unit. A pixel figure quietly multiplied by a scale is how two studies come to disagree by a
  factor nobody can find.
- **It must not repair its upstream.** Where an implementation has a defect — retipy's curvature,
  say — the adapter reproduces it and the defect is recorded on the biomarker page. A benchmark of
  fixed code measures the fix rather than the software anybody would actually run.
- **It must not score, choose shapes or datasets, or write files.**

## 4. The naming table is the whole problem

`src/biomarkers/naming.py` maps `(implementation, their key)` to
`(biomarker page, variant heading, unit)`:

```python
NAMES = {
    "pvbm": {
        "tortuosity_index": ("tortuosity", "hart-tau1", "dimensionless"),
        "median_tortuosity": ("tortuosity", "hart-tau1", "dimensionless"),
        ...
    },
}
```

Three rules keep it honest:

- **A mapping is a claim, and the synthetic benchmark is what tests it.** A shape where two variants
  give different known values separates them by measurement. Declare the mapping the documentation
  implies, then let the shapes agree or disagree with it.
- **An entry may map to no variant.** Where an implementation computes something no catalogued
  variant describes, the entry says so, and the biomarker page gains an implementation-only form.
  `docs/biomarkers/tortuosity.md` already records three.
- **Two keys may map to the same variant**, as PVBM's two tortuosity figures do. That is not a
  duplicate: they differ in the region or the aggregation, which the table's comment records.

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
- **7.3** Original names out of the adapter; translation only in the naming table.
- **7.4** Units declared, never silently applied.
- **7.5** An upstream's defect is reproduced and recorded, never quietly fixed.
