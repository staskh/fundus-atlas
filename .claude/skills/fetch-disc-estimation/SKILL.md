---
name: fetch-disc-estimation
description: Estimate where each photograph's optic disc and cup sit, and how large they are, with the catalogued SegFormer disc-and-cup model — one committed CSV per dataset indexed by image key, in the native crop frame, with a sidecar JSON naming what measured it. Use when adding or changing the fetch_disc_estimation command or files under results/disc_estimation/.
---

# Estimating the optic disc and cup per photograph

`fetch-um-resolution` asks one question of a **camera**: how large is its typical disc. This asks
one of each **photograph**: where are its disc and cup, and how large. It is a model's estimate, not
an annotation, and every row says so by living under `results/` with the model named beside it.

## 1. What you produce

1. **The command**, `uv run python -m datasets.fetch_disc_estimation`, module
   `src/datasets/fetch_disc_estimation.py`. Like `fetch_um_resolution`, it is **not** a step inside
   `python -m datasets.<slug>`: a store build must not load a model.
2. **One committed CSV per dataset**, `results/disc_estimation/<slug>.csv`, one row per manifest
   key (section 4).
3. **One committed sidecar**, `results/disc_estimation/<slug>.json` (section 5).
4. **Tests** against synthetic discs at known places, never against a download, in
   `tests/datasets/test_fetch_disc_estimation.py`.

## 2. The command-line contract

```bash
uv run python -m datasets.fetch_disc_estimation --dataset hrf
uv run python -m datasets.fetch_disc_estimation          # every built store
uv run python -m datasets.fetch_disc_estimation --force
```

| Option | Meaning |
| --- | --- |
| `--dataset SLUG` | One dataset, or omit for every store with a manifest |
| `--data-root PATH` | The store root, same default as a fetcher |
| `--force` | Measure again even when the fingerprint still matches |

Without `--force`, a dataset whose sidecar fingerprint matches is left alone.

## 3. How a photograph is measured

| Default | Value | Why |
| --- | --- | --- |
| Model | [segformer-disc-cup](../../../docs/models/segformer-disc-cup.md) | one network for disc and cup; its disc is disc ∪ cup, the region an expert outlines |
| Input | `native/images/<key>.png`, resized to the model's grid by `datasets.utils.resample.photograph` | the store's own resize rule, so this input is bit-identical to the store's 512 grid |
| Back to native | the adapter's probabilities upsampled to `crop_side`, thresholded there | `Outlines.from_probabilities` |
| Which patch | the **largest connected patch** of each mask | a stray speck must not pull the centre off the disc |
| Centre | centroid of that patch | |
| Radius | **equivalent radius** — of a circle of the same area | the disc is a vertical oval; one axis alone is the wrong ruler |

Every photograph in the manifest is measured; there is no sample.

## 4. What the CSV holds

`key,outcome,disc_cx,disc_cy,disc_r,cup_cx,cup_cy,cup_r,note`, in manifest order, floats to two
decimals.

- **Frame: the native crop** — the store's `native/` square, `crop_side` pixels across, the same
  frame as `native/contours/`. To reach the source photograph add `crop_x0`, `crop_y0` from the
  manifest; to reach a built size multiply by `size / crop_side`.
- `outcome` is `graded`, or why there is no number: `no-disc` (the model drew nothing),
  `no-image`, `failed` (the model crashed), or the adapter's own `declined`. A photograph without
  a disc **keeps its row** with empty measurements; omitting it would look untried.
- A disc with no cup leaves the `cup_*` cells empty.

## 5. What the sidecar holds

`dataset`, `model`, `grid`, `builder_version`, `frame`, `n_images`, `n_disc`, `n_cup`, and a
`fingerprint` over the model slug, its weights digest, the grid, the store's builder version, the
frame and the manifest's keys. Any of those changing means the CSV describes photographs, or a
model, that no longer exist; re-run.

## 6. What a reader may do with it

- Use it to place the disc and the zones around it, or as a disc-centred crop.
- **Do not** report disc size in millimetres from `disc_r` and a `disc_anchored` `um_per_px`: that
  scale assumed the disc's size (`fetch-um-resolution`, section 8).
- `cup_r / disc_r` is a ratio of equivalent radii of a model's outline, not the vertical
  cup-to-disc ratio a clinician grades.
- Where a dataset ships expert disc contours, those are the reference; this is a model's estimate,
  labelled as such.
