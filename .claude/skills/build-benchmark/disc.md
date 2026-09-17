# The disc-and-cup benchmark

Load this beside `SKILL.md` before building or changing `src/benchmarks/disc.py`. Everything here
is particular to disc and cup; everything shared is in the main file.

**What it asks:** how close is a model's outline of the optic disc and cup to the one an
ophthalmologist drew — and how far does the difference travel into the numbers anyone computes from
it.

```
python -m benchmarks --benchmark disc
python -m benchmarks --benchmark disc --model automorph-disc-cup --dataset papila
python -m benchmarks --benchmark disc --max-samples 20
```

## 1. Two questions, one run

A segmentation benchmark that stops at Dice answers the easier half. The disc and cup exist to be
measured — a cup-to-disc ratio decides whether a patient is referred — so **the shapes and the
numbers derived from them are scored in the same run**, per photograph, and reported side by side.
A model can score 0.95 Dice on the cup and still be wrong about the ratio, because the ratio is a
quotient of two boundaries and the errors need not cancel.

## 2. Score in the annotation's own frame

**Everything is measured at native resolution**, in the store's `native/` frame, because that is
where the expert drew. The store's contours are already there, as floating-point polygons.

The path from a model's output to that frame is the part to get right:

- **Where the model emits probabilities, resample the probability map to native — bilinear — and
  threshold at native.** Not the other way round. Thresholding first and resampling a binary mask
  throws away the boundary detail the model actually produced, and it is the boundary that every
  metric here turns on. Bilinear rather than bicubic, because bicubic overshoots past 0 and 1 and
  the overshoot lands exactly where the threshold sits.
- **Where only a binary or label mask is available, nearest neighbour**, and say so in the run.
- **Never interpolate label indices.** Disc and cup arrive as a three-level map in some models;
  resample per class and take the argmax at native.
- **The disc and the cup are separate structures**, not two levels of one. Some models emit a cup
  that is not inside its own disc; do not quietly repair it — measure it and report it, because a
  cup outside its disc is a fact about the model.

Which path was taken is recorded per run, and it belongs in the results page: it moves the score.

## 3. What is measured

Per photograph, per structure, per reader:

| Metric | What it says |
| --- | --- |
| **Dice** | overlap with the expert's outline; the usual number, and the least informative here |
| **Centre offset** | distance between the two centroids, in native pixels **and in disc diameters** — the second is the only camera-independent form |
| **Width, height** | the bounding extent of each structure, and the model's error in each |
| **Equivalent radius** | the radius of a circle of the same area, which is what most clinical software reports |
| **Vertical cup-to-disc ratio** | cup height over disc height, the number a referral is made on |
| **Area cup-to-disc ratio** | cup area over disc area, reported where a project computes it that way |

**The ratio is scored as an error against the expert's own ratio**, not as two Dice scores. Report
the signed error, so that a model which systematically over-calls the cup is distinguishable from
one that is merely noisy — those are different clinical failures.

**Where a dataset publishes its own ratio** — ORIGA's `ExpCDR`, Chákṣu's per-expert cup-to-disc
ratios — score against that too, and say which of the two references a number is against. A value
computed from a contour and a value the authors published are not the same statement even when they
agree.

## 4. Multi-reader ground truth is the point, not a complication

Chákṣu publishes five ophthalmologists' outlines, PAPILA two. So:

- **Score against each reader separately**, and keep all of it in the evidence: one row per
  photograph per reader.
- **Report the spread between readers** as the ceiling, exactly as the quality benchmark does with
  its graders. A model within the readers' own disagreement is not distinguishable from a reader.
- **Where a consensus is needed**, say how it was made — mean outline, majority raster, or the
  dataset's own — and never invent one the dataset did not publish.

The exclusions of `src/datasets/exclusions/` are scoped per reader, so a single broken expert mask
removes that reader's outline and leaves the other four standing.

## 5. Where a model must not be measured

- **A dataset whose images are crops** — RIGA — is excluded whole by the crop rule, which is
  painful here because it is the six-reader dataset. Chákṣu's five readers are the ceiling instead.
- **A photograph whose disc is not in the frame.** Some datasets are macula-centred and the disc
  runs off the edge; a model cannot be scored on a structure the photograph does not contain.
  Exclude on the annotation, not on a guess: no contour, no score.
- **A model that emits only the disc** — VascX disc, LUNet v2 — is scored on the disc and absent
  from every cup table. Absent, not zero.

## 6. What is kept

The common rules apply, with one addition: **the predicted masks are kept** in `.atlas_runs/`, not
just the scores. The biomarker benchmark's input is exactly these masks (`PLAN-BENCHMARK.md` §11),
and a mask whose fingerprint no longer matches its model is recomputed before anything is measured
from it.

Per-image evidence carries, beyond the common columns: the reader, the structure, every metric of
section 3, and the resampling path that produced it.

## 7. Where the code goes

- `src/benchmarks/disc.py` — the run.
- **`src/benchmarks/metrics/disc.py` — the measurements of section 3, and nothing else.** They are
  pure functions over two masks or two polygons: no model, no store, no file. That is what lets the
  same functions serve the synthetic fixtures of `PLAN-BENCHMARK.md` §7, where the answer is known
  from arithmetic rather than from another program.
- `src/benchmarks/loaders/disc.py` — `DiscCupLoader`, yielding the photograph and the contours per
  reader, with the multi-reader lists kept as lists.
- `src/models/<slug>.py` — one adapter per catalogued model, as always.

Test the metrics against shapes whose answer is known before testing them against a dataset: two
identical circles are Dice 1 and offset 0; a circle inside another of twice the radius is a
cup-to-disc ratio of exactly 0.5.
