# Quality benchmark — how it is run

This page says how the benchmark is configured: what it asks, which models and datasets take part,
what it excludes, how to run it, and what every column of its evidence means.

**It is part generated and part written.** The tables and lists between the `generated` markers are
rendered from what the benchmark reports about itself and are refreshed by
`python -m benchmarks --benchmark quality --docs`, which measures nothing. The dataset table is read
from the stores on the machine that refreshed it. Everything else on the page is written by hand and
is never overwritten. What came out is a separate page: [quality-results.md](quality-results.md).

## 1. What this benchmark asks

<!-- generated: asks -->
**Is this photograph good enough to measure?** Every quality model here is asked that of the same photographs, and its answer is compared with the grade the dataset's own readers wrote down. A gate that throws away usable photographs costs a study its sample; one that lets bad photographs through costs it every biomarker computed from them.
<!-- /generated -->

Whether a model's judgement of a photograph matches **what an expert recorded about that
photograph**. The reference is a human grade published with the dataset; the score says how far the
software is from it. Comparing the models with each other is a second, weaker question, and it is
there to raise suspicions about the reference rather than to rank the software.

## 2. The models

<!-- generated: subjects -->
| Model | Pinned at | Grid it reads | Grid the network sees | Ensemble | Emits | Took part |
| --- | --- | --- | --- | --- | --- | --- |
| [fit-quality](../models/fit-quality.md) | `d7757e28` | 512² | 512² | 10 | one probability that the photograph is gradeable: at or above 0.5 it counts as gradeable, below it as ungradeable | yes |
| [vascx-quality](../models/vascx-quality.md) | `d0cde1c7` | 1024² | 224² | one checkpoint holding several folds | three classes, read as good, usable and bad | yes |
| [automorph-quality-grader](../models/automorph-quality-grader.md) | `9a953e5e` | 512² | 512² | 8 | good, usable, reject | yes |
| [quickqual](../models/quickqual.md) | `a94feb02` | 512² | 512² | 1 | good, usable, bad | yes |
| [quickqual-meme](../models/quickqual-meme.md) | `a94feb02` | 512² | 512² | 1 | one probability that the photograph is bad | yes |
<!-- /generated -->

A model named here that has not taken part is **declared, not forgotten**: the benchmark asks for
it, and the run says so every time until somebody writes it.

### 2.1 What each model's own project does with its answer

A grade is not a decision. Which photographs reach a segmentation model is decided by a rule
belonging to the **pipeline** rather than to the model, and sometimes by a rule that overrides the
model's own verdict. Each adapter declares the rule its project applies, and the
`carried_by_its_pipeline` column of the evidence records what that rule did to each photograph.

<!-- generated: subject_notes -->
- **fit-quality** — the toolbox's own default threshold of 0.5 on its confidence. No catalogued pipeline runs this model; the toolbox is a library, and the threshold is what its own inference applies
- **vascx-quality** — none. VascX writes the three outputs to `quality.csv` as raw logits named q1, q2 and q3, and nothing in the pipeline reads them again: no photograph is refused and no biomarker is withheld on their account
- **automorph-quality-grader** — AutoMorph's own rule, which is not this model's argmax: a `good` verdict is carried into measurement, a `usable` one only while the probability of `bad` stays under 0.25, and everything else is dropped before any segmentation model sees it
- **quickqual** — none. AutoMorphalyzer is the only catalogued pipeline that reaches for QuickQual, and it runs the MEME variant — a nine-feature linear model emitting one probability of `bad` — not this three-class classifier, and it writes that number into its results table without ever acting on it
- **quickqual-meme** — AutoMorphalyzer carries **every** photograph into measurement. It writes this number into its results table as `QuickQual_quality`, recommends no threshold, and no code path filters on it — so every biomarker it publishes was computed whatever this model said. Measuring everything is a decision, and this is what it costs
<!-- /generated -->

## 3. The datasets

<!-- generated: material -->
| Dataset | Photographs | Reference | Black canvas | Excluded, and why | Available |
| --- | --- | --- | --- | --- | --- |
| [fives](../datasets/fives.md) | 800 | derived | 0.000 | none | yes |
| [fqs](../datasets/fqs.md) | 2245 | published | 0.036 | none | yes |
| [mshf](../datasets/mshf.md) | 546 | published | 0.000 | 237 below the size floor; 19 no reference to score against | yes |
| [papila](../datasets/papila.md) | 488 | assumed | 0.188 | none | yes |
| [eyeq](../datasets/eyeq.md) | — | — | — | — | **no** — no store built |
| [drimdb](../datasets/drimdb.md) | — | — | — | — | **no** — no store built |
<!-- /generated -->

**Reference** says where the grade came from. `published` is the dataset's own verdict; `derived` is
this repository's, computed from components the dataset did publish; `assumed` is this repository's
supposition that a curated dataset is all sound, which means that dataset contains no bad
photographs by construction and no ranking metric is defined on it.

**Black canvas** is the share of the square the store built that is not photograph, at the median.
A fundus cut off at top and bottom leaves bands there, and a model judges the square it is handed.

## 4. What is excluded, and by which rule

<!-- generated: exclusions -->
- **Below the size floor** — a photograph whose field of view is under 512 pixels, measured on the field's own size rather than the frame's
- **A finding recorded against the image** — anything in `src/datasets/exclusions/`, so that a finding survives deleting and rebuilding a store
- **No reference to score against** — a photograph the dataset published but never graded. It is not a failure of the model and is never counted as one
- **Excluded whole** — a dataset whose images are crops rather than photographs. No size floor catches that, because a crop can be large
<!-- /generated -->

These are **ours**: the benchmark would not ask. A model's own refusal to answer is `declined`,
which is a different statement, and the two are never added together.

## 5. How to run it

<!-- generated: running -->
```bash
python -m benchmarks --benchmark quality
python -m benchmarks --benchmark quality --model fit-quality --dataset fives
python -m benchmarks --benchmark quality --max-samples 20
python -m benchmarks --benchmark quality --docs
```

| Flag | What it does |
| --- | --- |
| `--model` | one model, or several separated by commas |
| `--dataset` | one dataset, or several separated by commas; one of each re-measures a pair |
| `--device` | cuda, mps or cpu; the fastest available by default |
| `--batch` | how many photographs go to the model at once; 8 by default |
| `--max-samples` | score at most the first N photographs of each dataset, for development; a sampled result says it is not complete, and a later run finishes it |
| `--random-samples` | choose those photographs at random rather than first |
| `--seed` | the seed a random sample uses, recorded in the run |
| `--data-root` | read the stores from somewhere other than `.atlas_data/` |
| `--force` | discard what is stored and measure it all again |
| `--no-report` | skip refreshing `docs/BENCHMARKS.md` after the run |
| `--config` | print what this benchmark reports about itself, as JSON, measuring nothing |
| `--docs` | refresh this page from that JSON, measuring nothing |
<!-- /generated -->

## 6. What each column of the evidence means

<!-- generated: columns -->
`results/quality/<model>/<dataset>.csv` holds one row per photograph:

| Column | Meaning |
| --- | --- |
| `key` | the photograph, as the store names it — it joins to the manifest and to the image |
| `subset` | the dataset's own subcollection: a camera, an acquisition site, a challenge release |
| `split` | the split the dataset published, or `unspecified` where it published none |
| `grade` | the reference grade: `good`, `usable` or `bad` |
| `grade_source` | where that grade came from: `published`, `derived` or `assumed` |
| `pad_fraction` | how much of the square the store built is canvas rather than photograph |
| `readers` | each reader's own grade, where the dataset keeps its readers apart |
| `outcome` | `graded`, `declined` by the model itself, or `failed` with the reason in `note` |
| `verdict` | the model's own hard call, in the atlas's words. Empty for a model with no classes |
| `carried_by_its_pipeline` | whether the model's **own project** would carry this photograph into measurement, which is not the same as its verdict. Empty where no catalogued pipeline gates on this model |
| `gradeable` | the model's confidence that the photograph is worth measuring — the one question every quality model can be asked, and what the ranking metrics use |
| `good` | the probability of that grade, where the model emits three. Absent where it does not |
| `usable` | as above |
| `bad` | as above |
| `note` | why the model declined, or what it failed with |
<!-- /generated -->

A model that has no opinion to record leaves a column **absent** rather than blank: a binary grader
emits no class probabilities, and none are invented for it.

## 7. What a re-run repeats, and what it does not

<!-- generated: fingerprint -->
A stored result is kept only while everything it depends on is unchanged. This benchmark fingerprints:

- the facts each model declares that bear on its numbers: slug, purpose, grid, network_grid, ensemble, emits_probabilities, threshold, gate_threshold, backbone
- the sha256 of the weights actually loaded
- the store's slug and builder version
- this benchmark's name, `VERSION` (3) and size floor (512 pixels)

A fingerprint that differs means the stored result describes something that no longer exists, and it is measured again from nothing. **How much was done is not part of it**, because that does not change what any photograph scored: a complete result is never re-run, and a partial one is finished rather than restarted.
<!-- /generated -->

## 8. The counts every result carries

<!-- generated: counts -->
| Count | What it answers |
| --- | --- |
| `processed` | how many photographs this model has actually scored |
| `total` | how many the benchmark would ask about, after the exclusions |
| `excluded` | how many those exclusions removed, by reason; `total + excluded` is what the store holds |
| `seconds_per_photograph` | how long the model's own call took per photograph, on the device the result names — not part of the fingerprint |
| `timed_photographs` | how many photographs that timing covers |
<!-- /generated -->

`processed ≤ total`, and `total + excluded` is what the store holds: a photograph is either one the
benchmark asks about or one it excluded, never both and never neither. The timing covers the model's
own call and nothing around it, and leaves out the batch that loaded the weights whenever there is
another to average over.
