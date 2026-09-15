---
name: build-benchmark
description: Build a benchmark — its evaluation units, its loader, its metrics, what it keeps and how a re-run avoids measuring what has not changed. Use when adding or changing anything under src/benchmarks/.
---

# Building a benchmark

A **benchmark** answers the question the catalogues cannot: do two of these agree, measured on the
same images, on the same terms? It is one module, `src/benchmarks/<name>.py`, with a loader under
`src/benchmarks/loaders/`, and it produces committed per-image scores, a run record, and a
generated write-up.

`PLAN-BENCHMARK.md` is the standing decision about what is benchmarked and in what order. This
skill is how one is built.

## 1. What you produce

1. **The benchmark module**, `src/benchmarks/<name>.py`, with `run(...)` and a `main()` offering
   the command-line contract of section 7.
2. **A loader**, `src/benchmarks/loaders/<name>.py`, subclassing `loaders.base.Photographs` and
   adding only *what counts as ground truth here*.
3. **Tests**, `tests/benchmarks/`, written first, against a small store written to `tmp_path` by
   the helpers in `tests/benchmarks/conftest.py` — never against a real store and never against a
   real model.
4. **The generated write-up**, per `report-benchmark`, and **an analysis notebook**, per
   `analyse-benchmark`.

## 2. The evaluation unit

The unit is **(dataset, subset, split)** — `loaders.base.Unit` — never a whole dataset.
Contamination is per split, and cameras are not interchangeable: Chákṣu is three cameras, MSHF is
six groups, and one number over a mixed dataset hides what a map should show. `loaders.base.units`
reads a store's own units from its manifest.

Two exclusions apply to every benchmark, and they catch different things:

- **The size floor.** Photographs whose field of view is under `loaders.base.FLOOR` pixels are
  excluded, measured on `crop_side` — the field's own size, not the frame's.
- **The crop rule.** A dataset whose images are crops rather than photographs is excluded whole,
  declared in `loaders.base.CROPS` with the evidence, because no floor catches it: a crop can be
  large.

**The repository's own findings are applied too** — `src/datasets/exclusions/` — so a photograph
recorded as broken is out of every score without anyone remembering to exclude it.

## 3. The loader is a PyTorch dataset

`torch.utils.data.Dataset`, so batching is ordinary. The base class holds the store, the unit, the
two exclusion rules, the ordering and the key, which travels with every sample so that a prediction
can never be attributed to the wrong photograph. A subclass adds the ground truth and nothing else.

Two rules follow from batching:

- **Batch at the model's grid, score at the annotation's own frame.** The loader yields photographs
  at the size the model asked for — which is what the store's `512/` and `1024/` directories are
  for — and the ground truth that needs native resolution is read by the scorer, not stacked into
  the batch.
- **Ground truth that does not stack travels as a list.** `loaders.base.collate` stacks the images
  and leaves everything else alone: five readers' contours are not a tensor.

The adapter's `prepare` is passed to the loader as its transform, so a batch arrives at the model
in the form its upstream expects. Keep `prepare` free of the loaded network, or workers cannot
pickle it.

## 4. What is measured

`PLAN-BENCHMARK.md` §6 fixes the metrics per benchmark kind. Two rules are not negotiable:

- **Coverage first, and never folded into accuracy.** Every prediction is `graded`, `declined` or
  `failed`. A grader that answers the easy 60% and is right about all of them is not better than
  one that answers everything and is right about 85%, and a table printing only accuracy makes the
  first look better. Declined photographs are excluded from accuracy and counted in coverage;
  failures are counted separately again.
- **Report a threshold-free metric beside a threshold-dependent one** wherever the model's
  threshold was set on other data. The toolbox's quality ensemble scores 0.97 by area under the ROC
  curve and 0.54 by accuracy on the same photographs: only one of those two numbers is about the
  model.

Ground truth a dataset never provided is not a failure of the model. Photographs with no reference
are set aside by the loader, counted, and reported.

## 5. The fingerprint, and why a re-run is cheap

Each (model, unit) pair is scored once and kept with a fingerprint of **everything that could
change it, and nothing that cannot**:

- the facts in the model's declaration that bear on its numbers — its grids, its ensemble size,
  the thresholds it acts on — and **not** the prose beside them. Rewording an explanation must not
  throw away hours of measurement; equally, a number the model acts on must be declared as a number
  of its own rather than left inside a sentence, or changing it would silently keep a stale score.
  The benchmark names these keys explicitly rather than hashing whatever the adapter happens to
  return;
- the sha256 of the weights actually loaded;
- the patches applied, by content (carried in the upstream's provenance);
- the store's `builder_version` and the unit's photograph count;
- the benchmark's name, its `VERSION`, and the metric-affecting constants such as the floor.

A re-run recomputes a pair only when this differs; everything else is read from `results/`. So
adding a dataset costs only that dataset and adding a model costs only that model, while a changed
patch or a rebuilt store correctly invalidates exactly what it touched. `--force` recomputes
regardless.

**Increment `VERSION` whenever what is measured, or how, changes.** Anything left out of the
fingerprint is something a stale score can outlive.

## 6. What is kept

| Where | What | Committed |
| --- | --- | --- |
| `results/<name>/<model>/<unit>.csv` | per-image scores: what the dataset said, what the model said | **yes** — the evidence behind every table |
| `results/<name>/<model>/<unit>.json` | the fingerprint and the summary | **yes** |
| `.atlas_runs/<name>/<stamp>/run.json` | what ran, against what, with which pins and versions | no |
| `.atlas_runs/<name>/…` | predicted masks, where the benchmark makes them | no — but **kept**, because the biomarker benchmark reads them |
| `docs/benchmarks/<name>.md` | the generated write-up | **yes** |

A per-image row carries the key, the dataset's grade, the per-reader grades where there are any,
the outcome, and whatever the model actually emitted. It is the only artefact that cannot be
reconstructed without re-running everything.

## 7. The command line

```
python -m benchmarks.<name> [--models …] [--datasets …] [--device …] [--batch N]
                            [--data-root …] [--force] [--no-report]
```

Defaults name the models and datasets the plan chose for that benchmark, so running it with no
arguments does the intended thing.

## 8. Testing a benchmark without a model

Write a small **real adapter** in the test — one that grades by mean brightness, say — and run the
benchmark against it. It satisfies the same interface the catalogued models do, so what the test
exercises is the run rather than a rehearsal of one. Never mock an adapter, and never test a
benchmark against a downloaded store.

## 9. Rules

- **9.1** The benchmark never knows which model it is running; the adapter never knows which
  benchmark is running it.
- **9.2** Every result carries its contamination mark, from `benchmarks/contamination.py`, whose
  entries cite the model page's training-data section. `unknown` is never merged with
  `out-of-sample`.
- **9.3** Nothing is scored against a dataset's own published value without saying so.
- **9.4** A benchmark reports; it does not rank. No "best", no ordering, no crowning.
