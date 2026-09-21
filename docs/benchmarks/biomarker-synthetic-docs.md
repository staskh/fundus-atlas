# Biomarkers against arithmetic benchmark — how it is run

This page says how the benchmark is configured: what it asks, which models and datasets take part, what it excludes, how to run it, and what every column of its evidence means. It is generated **before** a run measures anything, and again whenever the benchmark's code changes, so it describes the run that is happening rather than the one that happened to finish. A column added to the evidence and not explained here is a bug rather than an omission. What came out is a separate page: [biomarker-synthetic-results.md](biomarker-synthetic-results.md).

## 1. What this benchmark asks

**Does a biomarker implementation compute the quantity it is said to compute?** Every other benchmark here compares software with a human judgement; this one compares it with a number derived on paper. A straight vessel has a tortuosity of exactly 1, a circular arc a curvature of exactly 1/r, and an implementation that disagrees is wrong rather than different. It selects nothing: which implementations are fit to measure a real segmentation is a judgement made by a person on this evidence.

Every shape is drawn on a **2048²** grid at **5.0 µm per pixel**, at 0°, 30°, 60°, 90°. Each angle is a fresh rendering from continuous coordinates, never a turned picture: resampling a structure a few pixels wide destroys it, and a rotated bitmap would measure the resampler.

## 2. The implementations

| Implementation | Pinned at | Needs | Claims invariance under | Columns |
| --- | --- | --- | --- | --- |
| [pvbm](../projects/pvbm.md) | `5edb79a6eff5` | artery, vein, disc | rotation | 32 |

## 3. The shapes, and what each one settles

| Shape | Classes drawn | Quantities it defines |
| --- | --- | --- |
| `straight` | artery, vein | 25 |
| `arc` | artery, vein | 23 |
| `sinusoid` | artery, vein | 23 |
| `bifurcation` | artery, vein | 15 |
| `disjoint` | artery, vein | 19 |
| `artery-vein-pair` | artery, vein | 18 |
| `spokes-macula-centred` | artery, vein | 22 |
| `spokes-disc-centred` | artery, vein | 22 |

Every value a shape defines follows from its geometry and is written out in [the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb), so a reader can disagree with the arithmetic rather than with the code.

The shapes are **drawn before any of this runs**, by `python -m benchmarks.shapes`, into the committed store at `data/synthetic/av/`. How that works — the command, the two tables it writes, and what each family settles — is [biomarker-synthetic-shapes.md](biomarker-synthetic-shapes.md).
## 5. How to run it

```bash
python -m benchmarks --benchmark biomarker-synthetic
python -m benchmarks --benchmark biomarker-synthetic --model pvbm --dataset arc
python -m benchmarks --benchmark biomarker-synthetic --max-samples 20
```

`--model` and `--dataset` each take one name or a comma-separated list, and naming one of each re-measures a single pair. `--max-samples N` scores the first N photographs of each dataset — `--random-samples` chooses them at random from a recorded seed — which is for development: a sampled result says it is not complete, and a later run finishes it rather than starting again. `--force` discards what is stored and measures everything afresh.

## 6. What each column of the evidence means

`results/biomarker-synthetic/<model>/<dataset>.csv` holds one row per photograph:

| Column | Meaning |
| --- | --- |
| `key` | the rendering: the shape and the angle it was drawn at |
| `shape` | which shape was drawn — `straight`, `arc`, `spokes-macula-centred` and the rest |
| `rotation` | the angle it was drawn at, in degrees, generated afresh rather than turned |
| `side` | the grid it was drawn on, in pixels |
| `um_per_px` | the microns per pixel the shape was built with |
| `outcome` | `measured` if any quantity came back, else `failed`; `note` says what fell over |
| `seconds` | how long the implementation took over this rendering |
| `said_<key>` | what the implementation returned. `<key>` is a **catalogued biomarker name** — `biomarker/variant/structure` — wherever the implementation's adapter maps its own column to one, so two implementations' evidence lines up column by column. A column the catalogue has no name for yet keeps the implementation's own name, recognisable by carrying no `/`, and is measured and stored all the same |
| `theory_<key>` | what the shape's geometry requires for that quantity, where it defines one. A shape states its theory under catalogued names too, so the two meet without translation; a column under an implementation's own name therefore has no theory beside it |
| `note` | what an implementation failed with |

A model that has no opinion to record leaves a column **absent** rather than blank: a binary grader emits no class probabilities, and none are invented for it.

## 7. What a re-run repeats, and what it does not

Each `(model, dataset)` result is stored beside a **fingerprint** of everything that could change it: the facts the model declares — its grids, its ensemble, the thresholds it acts on — the sha256 of the weights actually loaded, the patches applied by content, the store's builder version, and this benchmark's own version. A fingerprint that differs means the stored scores describe something that no longer exists, and the pair is measured again from nothing.

**How much was done is not part of that**, because it does not change what any photograph scored. A complete result is never re-run; a partial one is finished by measuring only the photographs it is missing; and nothing is ever truncated — asking for twenty against a file that holds four hundred leaves all four hundred alone.

## 8. The counts every result carries

| Recorded | Means |
| --- | --- |
| `processed` | how many photographs this model has actually scored |
| `total` | how many the benchmark would ask about, after the exclusions of section 4 |
| `excluded` | how many those exclusions removed, by reason |
| `seconds_per_photograph` | how long the model itself took per photograph, on the device the result names |
| `timed_photographs` | how many photographs that timing covers |

`processed ≤ total`, and `total + excluded` is what the store holds: a photograph is either one the benchmark asks about or one it excluded, never both and never neither.

The timing covers the model's own call and nothing around it — not reading the photograph, not scoring the answer. The batch that loads the weights is left out of it whenever there is another batch to average over, and a run that measured nothing keeps the timing it already had rather than reporting none. It is **not** part of the fingerprint: how fast a model answered does not change what it said, and the same weights on another machine would give another number.

---

**Generated by `python -m benchmarks --benchmark biomarker-synthetic` on:** 2026-09-21
