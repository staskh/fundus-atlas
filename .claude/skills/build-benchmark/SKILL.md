---
name: build-benchmark
description: Build a benchmark — what it runs on, its loader, its metrics, what it keeps and how a re-run avoids measuring what has not changed. Use when adding or changing anything under src/benchmarks/.
---

# Building a benchmark

A **benchmark** measures a model or a pipeline **against what an expert annotated**. That is its
purpose and the standard everything in it is built to: the reference is a human judgement recorded
in a published dataset, the score says how far the software is from it, and every rule below exists
to keep that comparison honest.

**Comparing models with each other is the secondary goal**, and it answers a different kind of
question. Two models agreeing is not evidence that either is right; two models disagreeing on a
photograph the readers also disagreed about is a reason to look at the annotation rather than at the
software. So model-against-model numbers are for forming suspicions — about a dataset's ground
truth, about where the human ceiling actually sits — and never for crowning anything. Where a model
is right and the expert's grade says otherwise, that is a finding to chase, not an error to report
quietly.

A benchmark is one module, `src/benchmarks/<name>.py`, with a loader under
`src/benchmarks/loaders/`, and it produces committed per-image scores, a run record, two generated
documents and a notebook.

`PLAN-BENCHMARK.md` is the standing decision about what is benchmarked and in what order. This file
is how any benchmark is built. **What is true of one benchmark only lives in its own file beside
this one** — `quality.md`, and one per benchmark thereafter — and you load that file too before
building or changing that benchmark.

| Benchmark | Its rules |
| --- | --- |
| Quality | [quality.md](quality.md) |
| Disc and cup | [disc.md](disc.md) |

## 1. What you produce

1. **The benchmark module**, `src/benchmarks/<name>.py`, with `run(...)` and a `main()` offering
   the command-line contract of section 7.
2. **A loader**, `src/benchmarks/loaders/<name>.py`, subclassing `loaders.base.Photographs` and
   adding only *what counts as ground truth here*.
3. **Tests**, `tests/benchmarks/`, written first, against a small store written to `tmp_path` by
   the helpers in `tests/benchmarks/conftest.py` — never against a real store and never against a
   real model.
4. **Two generated documents**, per `report-benchmark`, and **an analysis notebook**, per
   `analyse-benchmark`.

## 2. A run scores a whole dataset

**The run's key is the dataset.** The model sees every photograph the store holds, in one pass, and
the per-image evidence carries the `subset` and `split` each photograph came from. Grouping — by
split, by camera, by anything the manifest records — is an **analysis** question, answered in the
report and the notebook from those columns.

Running instead over (dataset, subset, split) triples costs three things and buys nothing: a model
is loaded once per group rather than once per dataset, the grouping is fixed at run time so that
wanting a number per camera means running the models again, and the word *unit* ends up in
documents written for clinicians. **The word in every report is `dataset`.**

Two exclusions apply at load time, and they catch different things:

- **The size floor.** Photographs whose field of view is under `loaders.base.FLOOR` pixels are
  excluded, measured on `crop_side` — the field's own size, not the frame's.
- **The crop rule.** A dataset whose images are crops rather than photographs is excluded whole,
  declared in `loaders.base.CROPS` with the evidence, because no floor catches it: a crop can be
  large.

**The repository's own findings are applied too** — `src/datasets/exclusions/` — so a photograph
recorded as broken is out of every score without anyone remembering to exclude it.

### 2.1 What a benchmark declares may not exist yet

The datasets and models a benchmark names are **a statement of intent, not an inventory**. A run
therefore **never stops** at a dataset whose store has not been built or a model whose adapter has
not been written: it warns on the console, records what is missing and why, and measures everything
else. Adding a name to the list is how a benchmark asks for the work; the run is what keeps
reminding everyone the work is outstanding.

Three rules keep that from producing a table that quietly means less than it looks like:

- **The gap is published, not just logged.** The generated `-docs.md` names every declared dataset
  and model and says which ran, which could not, and why: **no store built**, **no adapter
  written**, or **excluded whole** by the crop rule. Those are three different statements and are
  never merged.
- **The results page says how many of how many**, in its first paragraph.
- **A run with nothing available is an error.** An empty document that looks like a report is worse
  than a failure.

In code this means asking before loading — a store without a `manifest.csv` and a slug without
`src/models/<slug>.py` are both ordinary conditions, not exceptions to let escape — and carrying the
list of what was skipped into the run record and both documents.

## 3. The loader is a PyTorch dataset

`torch.utils.data.Dataset`, so batching is ordinary. The base class holds the store, the two
exclusion rules, the sampling of section 7.1, the ordering, and the key, which travels with every
sample so that a prediction can never be attributed to the wrong photograph. A subclass adds the
ground truth and nothing else.

Three rules follow:

- **A loader is given a dataset, not a split.** It reads the whole store and hands `subset` and
  `split` along with each photograph.
- **Batch at the model's grid, score at the annotation's own frame.** The loader yields photographs
  at the size the model asked for — which is what the store's `512/` and `1024/` directories are
  for — and ground truth that needs native resolution is read by the scorer, not stacked into the
  batch.
- **Ground truth that does not stack travels as a list.** `loaders.base.collate` stacks the images
  and leaves everything else alone: five readers' contours are not a tensor.

The adapter's `prepare` is passed to the loader as its transform, so a batch arrives at the model in
the form its upstream expects. Keep `prepare` free of the loaded network, or workers cannot pickle
it.

## 4. What is measured

Each benchmark's metrics are in its own file. Two rules hold for all of them:

- **Coverage first, and never folded into accuracy.** Every prediction is `graded`, `declined` or
  `failed`. A model that answers the easy 60% and is right about all of them is not better than one
  that answers everything and is right about 85%. Declined predictions are excluded from accuracy
  and counted in coverage; failures are counted separately again.
- **Report a threshold-free metric beside a threshold-dependent one** wherever the model's
  threshold was set on other data. The toolbox's quality ensemble scores 0.97 by area under the ROC
  curve and 0.54 by accuracy on the same photographs: only one of those two numbers is about the
  model.

Ground truth a dataset never provided is not a failure of the model: those photographs are set
aside by the loader, counted, and reported.

## 5. Two questions before anything is measured

A run asks these of every (model, dataset) pair, in this order.

**First, is what is stored still valid?** That is the **fingerprint**, and it covers everything that
could change a score and nothing that cannot:

- the facts in the model's declaration that bear on its numbers — its grids, its ensemble size, the
  thresholds it acts on — and **not** the prose beside them. Rewording an explanation must not throw
  away hours of measurement; equally, a number the model acts on must be declared as a number of its
  own, or changing it would silently keep a stale score. The benchmark names these keys explicitly
  rather than hashing whatever the adapter happens to return;
- the sha256 of the weights actually loaded, and the patches applied, by content;
- the store's `builder_version`;
- the benchmark's name, its `VERSION`, and the metric-affecting constants such as the floor.

A fingerprint that differs means the stored scores describe something that no longer exists: discard
them and measure the pair again from nothing. **Increment `VERSION` whenever what is measured, or
how, changes** — anything left out of the fingerprint is something a stale score can outlive.

**Then, is it complete?** How much of a dataset was scored does not change what any photograph
scored, so it is *not* part of the fingerprint. It is recorded separately, and it decides the work:

- **a complete result is never re-run**;
- **a partial result is finished** — read the keys already scored, work out which photographs are
  missing, score **only those**, and merge them into the same file;
- **nothing is ever truncated.** `--max-samples 50` against a file that already holds 488 leaves all
  488 alone: a sample is a floor on the work, not a ceiling on the evidence.

## 6. What is kept

| Where | What | Committed |
| --- | --- | --- |
| `results/<benchmark>/<model>/<dataset>.csv` | per-image scores: what the dataset said, what the model said, and the subset and split it came from | **yes** — the evidence behind every table |
| `results/<benchmark>/<model>/<dataset>.json` | the fingerprint, the summary, and how much of the dataset is done | **yes** |
| `.atlas_runs/<benchmark>/<stamp>/run.json` | what ran, against what, with which pins and versions | no |
| `.atlas_runs/<benchmark>/…` | predicted masks, where the benchmark makes them | no — but **kept**, because the biomarker benchmark reads them |
| `docs/benchmarks/<benchmark>-docs.md` | how the benchmark is configured and run | **yes**, generated |
| `docs/benchmarks/<benchmark>-results.md` | what came out | **yes**, generated |

The benchmark's name leads the path so that two benchmarks scoring the same model on the same
photographs stay apart — the artery/vein segmentation benchmark and the biomarker one will do
exactly that. The model comes next because that is how the files are read: someone following a model
page wants that model's evidence across every dataset in one directory.

**Every result records three counts**, and they answer three different questions:

| Recorded | Means |
| --- | --- |
| `processed` | how many photographs this model has actually scored |
| `total` | how many the dataset holds, after the exclusions of section 2 |
| `excluded` | how many those exclusions removed, **broken down by reason**: below the size floor, a finding recorded against the image, no reference to score against |

`excluded` is ours and `declined` is the model's, and the two are never added together: one says
the benchmark would not ask, the other says the model would not answer. The word matches the rules
it counts — the exclusions of section 2. The three relate as `processed ≤ total`, and
`total + excluded` is what the store holds: a photograph is either one the benchmark asks about
or one it excluded, never both and never neither.

**Every result also records how long the model took**, as `seconds_per_photograph` and the
`timed_photographs` that number covers. A gate that takes a tenth of a second and one that takes
four are not interchangeable in front of a study of fifty thousand photographs, whatever their
agreement scores say, so the run measures it rather than leaving a reader to guess.

Three rules keep the number honest. It times **the model's own call and nothing around it** — not
reading the photograph, not scoring the answer. It **leaves out the batch that loaded the weights**
whenever there is another batch to average over, because those seconds belong to starting the model
rather than to measuring a photograph. And it is **never part of the fingerprint**: how fast a model
answered does not change what it said, so a faster machine must not throw away a stored score. A
resumed run that measured nothing keeps the timing it already had, and the device it ran on is
recorded beside it — this measures the machine as much as the model, and the results page must say
so wherever it quotes one.

**Every per-image row carries the same columns**, including for a photograph the model failed on: a
file whose columns depend on which photograph came first is not evidence of anything. Every column
is explained in the benchmark's `-docs.md` page; a column that page does not explain is a bug.

## 7. The command line

One entry point, with the benchmark as a parameter, so that every benchmark is run the same way:

```
python -m benchmarks --benchmark <name> [--model … ] [--dataset …] [--device …] [--batch N]
                     [--max-samples N] [--random-samples] [--seed N]
                     [--data-root …] [--force] [--no-report]
```

- `--benchmark` names the benchmark; it is the only required option.
- `--model` and `--dataset` narrow the run, each taking one name or a comma-separated list.
  Naming one of each is how a single pair is re-measured, which is what debugging an adapter needs.
- Omitting them runs the models and datasets that benchmark's own file declares, so the command
  with no narrowing does the intended thing.

### 7.1 Running on part of a dataset

`--max-samples N` scores at most N photographs of each dataset: **the first N of the manifest**, in
the store's own order, so that two development runs see the same photographs. `--random-samples`
chooses them at random instead, from a seed the run records and which `--seed` can set.

A sample is an unfinished run, not a different one, so it is written to the same file as a full run
and a later run finishes it (section 5). A result that is not complete **says so in its own file and
in every table that quotes it**, so that a sample can never be read as a measurement.

## 8. The order a run does things in

1. **Work out the configuration**: which declared models have adapters, which declared datasets
   have stores, and for each of those how many photographs it holds and what the exclusions took
   out. All of that is known without scoring anything — a loader reads a manifest, not an image.
2. **Write `<slug>-docs.md`**, before any measuring. A run that dies halfway then still leaves an
   accurate account of what it was going to do, and anybody can read what is about to happen before
   committing hours of it.
3. **Measure**, model by model, dataset by dataset.
4. **Write `<slug>-results.md`** and the index, from what is now in `results/`.

`--no-report` skips steps 2 and 4. Nothing else about a run depends on the order, but this order is
what makes the configuration page trustworthy: it describes the run that is happening rather than
the run that happened to finish.

**A change to the benchmark's code means regenerating the configuration page in the same commit**,
whether or not anything is measured. It costs nothing: it measures nothing.

## 9. Testing a benchmark without a model

Write a small **real adapter** in the test — one that grades by mean brightness, say — and run the
benchmark against it. It satisfies the same interface the catalogued models do, so what the test
exercises is the run rather than a rehearsal of one. Never mock an adapter, and never test a
benchmark against a downloaded store.

## 10. Rules

- **10.1** The benchmark never knows which model it is running; the adapter never knows which
  benchmark is running it.
- **10.2** Every result carries its contamination mark, from `benchmarks/contamination.py`, whose
  entries cite the model page's training-data section. `unknown` is never merged with
  `out-of-sample`, and where a model trained on one split only, the report breaks that dataset into
  its splits rather than publishing one number over both.
- **10.3** Nothing is scored against a dataset's own published value without saying so.
- **10.4** A benchmark measures; the **report** may recommend, and must do so as an argument
  rather than as an ordering: which model is best *at a named question*, the runner-up where it is
  close, and the caveats that would change the answer (`report-benchmark` §5). What is forbidden is
  a column sorted by score with nothing said about what the score answers.
