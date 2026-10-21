# Disc and cup benchmark — how it is run

This page says how the benchmark is configured: what it asks, which models and datasets take part,
what it excludes, how to run it, and what every column of its evidence means.

**It is part generated and part written.** The tables and lists between the `generated` markers are
rendered from what the benchmark reports about itself and are refreshed by
`python -m benchmarks --benchmark disc --docs`, which measures nothing. The dataset table is read
from the stores on the machine that refreshed it. Everything else on the page is written by hand and
is never overwritten. What came out is a separate page: [disc-results.md](disc-results.md).

## 1. What this benchmark asks

<!-- generated: asks -->
**Where exactly are the optic disc and the cup inside it?** Each model's outline is compared with the one an ophthalmologist drew on the same photograph — every ophthalmologist separately, never an averaged consensus — and with the cup-to-disc ratio computed from it, which is the number a glaucoma referral rests on.
<!-- /generated -->

How close a model's optic disc and optic cup are to **the outline an ophthalmologist drew on that
photograph**, and how far the difference travels into the numbers a clinic would read off it.
Overlap is measured as the Dice score — twice the area the two outlines share, divided by the sum of
their areas, so 1 is perfect agreement and 0 no overlap at all. Beside it are the measurements a
report actually quotes: where the centre of the disc sits, how wide and how tall each structure is,
the radius of a circle of the same area, and the **cup-to-disc ratio**, which is the number a
glaucoma referral rests on. Comparing the models with each other is a second, weaker question, and
it is there to raise suspicions about the outlines rather than to rank the software.

**Every measurement is made in the crop frame** — the full-resolution square the store built, which
is where the expert drew (see [DATASETS.md](../DATASETS.md) section 5). A model working at 512
pixels has its answer carried back there first, and how it was carried is recorded per photograph:
a probability map is resampled and thresholded **after** it arrives, because thresholding first and
resampling the mask throws away the boundary detail the model produced, and the boundary is what
every one of these numbers turns on.

**Signed errors are kept signed.** A model whose discs are three pixels too wide and one whose discs
are three pixels too narrow do not average to agreement, and a cup-to-disc ratio that reads high
sends the wrong patients to a clinic.

**The outlines themselves are kept**, one image per structure per photograph, under
`.atlas_runs/disc/<model>/<dataset>/` beside the fingerprint of the model that drew them. A score is
a summary of a shape, and the shape is what the next benchmark measures biomarkers from; a mask
whose fingerprint no longer matches its model is drawn again rather than read.

## 2. The models

<!-- generated: subjects -->
| Model | Pinned at | Grid it reads | Grid the network sees | Finds | Emits | Took part |
| --- | --- | --- | --- | --- | --- | --- |
| [vascx-disc](../models/vascx-disc.md) | `d0cde1c7` | 1024² | 512² | disc | probabilities, thresholded in the crop frame | yes |
| [automorph-disc-cup](../models/automorph-disc-cup.md) | `9a953e5e` | 512² | 512² | disc, cup | probabilities, thresholded in the crop frame | yes |
| [segformer-disc-cup](../models/segformer-disc-cup.md) | `a0463fb6` | 512² | 512² | disc, cup | probabilities, thresholded in the crop frame | yes |
| [beal](../models/beal.md) | — | — | — | — | — | **no** — no adapter yet: its weights are an unversioned Google Drive folder, so nothing can be pinned, and its inference expects the authors' own preprocessed directory layout |
| [lunetv2-odc](../models/lunetv2-odc.md) | `f72f6c9e` | 512² | 512² | disc, cup | probabilities, thresholded in the crop frame | yes |
| [isfa](../models/isfa.md) | — | — | — | — | — | **no** — its repository publishes an ImageNet backbone under `pretrained_model/`, not trained weights — checked against the repository, and its own weights link now 404s |
<!-- /generated -->

A model named here that has not taken part is **declared, not forgotten**: the benchmark asks for
it, and the run says so every time until somebody writes it.

A model that finds only the disc is scored on the disc alone. Its rows carry no cup columns rather
than empty ones, and it is never counted as having got the cup wrong.

## 3. The datasets

<!-- generated: material -->
| Dataset | Photographs | Readers | Black canvas | Excluded, and why | Available |
| --- | --- | --- | --- | --- | --- |
| [chaksu](../datasets/chaksu.md) | 1345 | 5: expert1, expert2, expert3, expert4, expert5 | 0.000 | none | yes |
| [grape](../datasets/grape.md) | 631 | 1: expert1 | 0.000 | none | yes |
| [papila](../datasets/papila.md) | 488 | 2: expert1, expert2 | 0.188 | none | yes |
| [refuge](../datasets/refuge.md) | — | — | — | — | **no** — no store built |
| [drishti-gs](../datasets/drishti-gs.md) | — | — | — | — | **no** — no store built |
| [origa](../datasets/origa.md) | — | — | — | — | **no** — no store built |
| [rim-one-dl](../datasets/rim-one-dl.md) | — | — | — | — | **no** — no store built |
<!-- /generated -->

**Readers are never merged.** A photograph five ophthalmologists outlined makes five rows of
evidence, one per reader, and a model is scored against each of them separately. Averaging the
outlines first would invent a consensus nobody drew and would hide the range the readers themselves
disagree over — which, on these structures, is often wider than the gap between two models.

**Black canvas** is the share of the square the store built that is not photograph, at the median.
A fundus cut off at top and bottom leaves bands there, and a model sees the square it is handed.

**Every reference here is a contour somebody drew**, and the ratios are computed from it.
[Chákṣu](../datasets/chaksu.md) also publishes each expert's own cup-to-disc ratio **as a number**,
which would be the strongest available check that a ratio derived from a contour means what this
benchmark thinks it means — but its store does not carry those numbers yet, so nothing here is
scored against them. That is a gap in the fetcher rather than in the dataset.

### 3.1 What is worth fetching next, and what each would settle

<!-- generated: worth_fetching -->
| Dataset | What it would settle | Cost |
| --- | --- | --- |
| [refuge](../datasets/refuge.md) | three of the models here trained on it, so it is what turns an in-sample suspicion into a measured contrast | registration |
| [drishti-gs](../datasets/drishti-gs.md) | four experts **and soft probability maps** — the only dataset here publishing annotator uncertainty as a map rather than as separate outlines | direct |
| [origa](../datasets/origa.md) | publishes `ExpCDR`, an expert cup-to-disc ratio **as a number**, which is the strongest available check that a ratio derived from contours means what this benchmark thinks | needs an archive by hand |
| [rim-one-dl](../datasets/rim-one-dl.md) | BEAL's other unlabelled target domain; it completes the contamination picture for that model once there is an adapter for it | direct |
<!-- /generated -->

[RIGA](../datasets/riga.md) is the painful exclusion: 750 photographs each outlined by **six**
ophthalmologists, and every one of its images is a crop rather than a photograph, so the crop rule
of section 4 excludes it whole.

## 4. What is excluded, and by which rule

<!-- generated: exclusions -->
- **Below the size floor** — a photograph whose field of view is under 512 pixels, measured on the field's own size rather than the frame's
- **A finding recorded against the image** — anything in `src/datasets/exclusions/`, so that a finding survives deleting and rebuilding a store. An outline a finding condemns is dropped on its own, leaving the other readers' outlines of that photograph in place
- **No outline to score against** — a photograph the dataset published but nobody outlined. It is not a failure of the model and is never counted as one
- **Excluded whole** — a dataset whose images are crops rather than photographs. No size floor catches that, because a crop can be large
<!-- /generated -->

These are **ours**: the benchmark would not ask. A model's own refusal to answer is `declined`,
which is a different statement, and the two are never added together.

## 5. How to run it

<!-- generated: running -->
```bash
python -m benchmarks --benchmark disc
python -m benchmarks --benchmark disc --model vascx-disc --dataset chaksu
python -m benchmarks --benchmark disc --max-samples 20
python -m benchmarks --benchmark disc --docs
```

| Flag | What it does |
| --- | --- |
| `--model` | one model, or several separated by commas |
| `--dataset` | one dataset, or several separated by commas; one of each re-measures a pair |
| `--device` | cuda, mps or cpu; the fastest available by default |
| `--batch` | how many photographs go to the model at once; 4 by default |
| `--max-samples` | score at most the first N photographs of each dataset, for development; a sampled result says it is not complete, and a later run finishes it |
| `--random-samples` | choose those photographs at random rather than first |
| `--seed` | the seed a random sample uses, recorded in the run |
| `--data-root` | read the stores from somewhere other than `.atlas_data/` |
| `--force` | discard what is stored and measure it all again |
| `--rescore` | measure the kept masks afresh without running any model — for a new measurement of the same masks |
| `--no-report` | skip refreshing `docs/BENCHMARKS.md` after the run |
| `--config` | print what this benchmark reports about itself, as JSON, measuring nothing |
| `--docs` | refresh this page from that JSON, measuring nothing |
<!-- /generated -->

## 6. What each column of the evidence means

<!-- generated: columns -->
`results/disc/<model>/<dataset>.csv` holds one row per photograph:

| Column | Meaning |
| --- | --- |
| `key` | the photograph, as the store names it |
| `subset` | the dataset's own subcollection: a camera, a site, a challenge release |
| `split` | the split the dataset published, or `unspecified` |
| `reader` | **which expert drew the outline this row is scored against**; a photograph with five readers makes five rows |
| `crop_side` | the side of the crop square, in pixels — every measurement below is in it |
| `outcome` | `graded`, or `failed` with the reason in `note` |
| `resampling` | how the model's output reached the crop frame: probabilities interpolated and then thresholded, a binary mask resampled nearest, or — where a later run measured new things about outlines an earlier one drew — the note that these came from the kept masks |
| `disc_dice` | overlap with this reader's disc, 0 to 1 |
| `cup_dice` | overlap with this reader's cup; absent for a model that finds no cup |
| `said_disc_width` | **how wide the model's disc is**, in crop pixels — a measurement in its own right rather than a distance from somebody else's |
| `said_disc_height` | how tall the model's disc is |
| `said_disc_radius` | the radius of a circle of the same area as the model's disc |
| `said_disc_center_x` | where the model puts the disc's centre, in crop pixels from the left |
| `said_disc_center_y` | and from the top |
| `said_cup_width` | how wide the model's cup is |
| `said_cup_height` | how tall |
| `said_cup_radius` | the radius of a circle of the same area as the model's cup |
| `said_cup_center_x` | where the model puts the cup's centre |
| `said_cup_center_y` | and from the top |
| `disc_center_offset` | distance between the two disc centres, in crop pixels |
| `cup_center_offset` | as above, for the cup |
| `disc_center_offset_diameters` | the same distance **in the expert's own disc diameters**, which is the only camera-independent form: ten pixels means one thing on a 2,576-pixel photograph and another on a 1,444-pixel one |
| `cup_center_offset_diameters` | the cup's offset, measured in that same disc diameter rather than in the cup's own — the disc is the ruler |
| `disc_width_error` | signed: the model's disc width less the reader's, in pixels |
| `disc_height_error` | signed, likewise |
| `cup_width_error` | signed, for the cup |
| `cup_height_error` | signed, for the cup |
| `disc_radius_error` | signed: the radius of a circle of the same area, less the reader's |
| `cup_radius_error` | as above, for the cup |
| `truth_disc_width` | how wide **this reader** drew the disc, in crop pixels — the size every error above is an error of |
| `truth_disc_height` | how tall, likewise |
| `truth_disc_radius` | the radius of a circle of the same area as the reader's disc |
| `truth_disc_center_x` | where the reader put the disc's centre |
| `truth_disc_center_y` | and from the top |
| `truth_cup_width` | how wide the reader drew the cup |
| `truth_cup_height` | how tall |
| `truth_cup_radius` | the radius of a circle of the same area as the reader's cup |
| `truth_cup_center_x` | where the reader put the cup's centre |
| `truth_cup_center_y` | and from the top |
| `said_vertical_ratio` | the model's cup height over its disc height |
| `truth_vertical_ratio` | this reader's own vertical cup-to-disc ratio |
| `cup_vertical_ratio_error` | **signed**: the model's vertical ratio less the reader's — the number a referral rests on |
| `said_area_ratio` | the model's cup area over its disc area |
| `truth_area_ratio` | this reader's own area ratio |
| `cup_area_ratio_error` | signed, likewise |
| `cup_outside_its_disc` | the share of the model's cup that falls outside its own disc, measured rather than repaired |
| `note` | what the model failed with |
<!-- /generated -->

A model that has no opinion to record leaves a column **absent** rather than blank, and none is
invented for it.

## 7. What a re-run repeats, and what it does not

<!-- generated: fingerprint -->
A stored result is kept only while everything it depends on is unchanged. This benchmark fingerprints:

- the facts each model declares that bear on its numbers: slug, purpose, grid, network_grid, structures, emits_probabilities, resampling, threshold, ensemble, upstream
- the sha256 of the weights actually loaded
- the upstream code they run in — its pinned commit and the content of every patch applied
- the store's slug and builder version
- this benchmark's name, `VERSION` (2) and size floor (512 pixels)
- the first three alone also name the masks kept under `.atlas_runs/disc/<model>/<dataset>/`, so `--rescore` measures them afresh without running a model, and a mask its model no longer agrees with is drawn again

A fingerprint that differs means the stored result describes something that no longer exists, and it is measured again from nothing. **How much was done is not part of it**, because that does not change what any photograph scored: a complete result is never re-run, and a partial one is finished rather than restarted.
<!-- /generated -->

Asking for twenty photographs against a file that already holds four hundred leaves all four hundred
alone: a sample is a floor on the work, not a ceiling on the evidence.

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
own call and nothing around it — not reading the photograph, not scoring the answer — and leaves out
the batch that loaded the weights whenever there is another to average over.
