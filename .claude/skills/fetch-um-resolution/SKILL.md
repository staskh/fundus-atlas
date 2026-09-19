---
name: fetch-um-resolution
description: Infer a camera-level microns-per-pixel scale from the median optic disc of a sampled subcollection, when a dataset published none. Use when adding or changing the fetch_um_resolution command, files under results/um_resolution/, or a biomarker that converts pixels to microns without a published scale.
---

# Inferring microns per pixel from the optic disc

A typical optic disc is about **1.8 mm (1,800 µm)** across. That is a population figure, not any
one eye, and it is stable enough to give a **camera** a scale when the authors published none.
It is not stable enough to give each photograph its own scale: disc diameter still varies about
10% between people on one device, and dividing 1,800 µm by each photograph's disc forces every
disc to 1.8 mm, erases true size differences, and puts that 10% onto every other micron
measurement on that photograph.

This command estimates the camera, not the person:

```
um_per_px = 1800 / median(disc_diameter_px)
```

taken over photographs that share a subset and a native size (section 4), measured by one catalogued
disc model, and kept only when those discs agree closely enough to be one camera.

The `fetch-dataset` skill, section 8, is what decides *whether* to run this. This skill is the
contract for the run itself, the JSON it commits, and what a biomarker may do with the number.

## 1. What you produce

1. **The command**, `uv run python -m datasets.fetch_um_resolution`, with the contract in section 3.
   The module is `src/datasets/fetch_um_resolution.py`. It is **not** a step inside
   `python -m datasets.<slug>`: a store build must not load a disc model.
2. **One committed JSON per dataset**, `results/um_resolution/<slug>.json`, with one entry per
   group (section 4). A summary table is a claim and this file is its evidence — the same rule as
   `results/` for benchmarks.
3. **The stamp into the manifest**, by `datasets.utils.resolution.stamp` — see section 9.
4. **Tests** against synthetic discs of known size, never against a download, in
   `tests/datasets/test_fetch_um_resolution.py`.

Load this skill before adding or changing any of those.

## 2. When it runs, and when it must run again

Run it for every catalogued dataset whose declared resolution source is not `published`. A dataset
that published a scale is exempt: replacing an author's figure with an assumption about disc size
is the error this split exists to prevent. Inheritance follows the parent; do not infer twice and
disagree.

**Measuring and writing down are different questions.** A store whose scale this repository derived
from a stated field angle is still measured — two independent derivations disagreeing is worth
knowing, and section 10 is what that check found — but the figure is not written into its manifest,
because `field_angle` outranks `disc_anchored`. Measure anything that is not `published`; stamp only
rows whose source is empty or `unknown`.

A fetcher that built a store with no published scale is **unfinished** until this command has
produced a current JSON for that slug, or has recorded, in the same JSON, that a group could not
be given a scale and why.

Re-run when any of these change: the store's builder version or crop, the disc model's identity,
the sample count, the seed, the 1,800 µm typical disc, or the spread gate. A fingerprint in the
JSON names those facts; a mismatch means the stored microns-per-pixel figure describes a camera
that no longer exists.

## 3. The command-line contract

```bash
uv run python -m datasets.fetch_um_resolution
uv run python -m datasets.fetch_um_resolution --dataset chaksu
uv run python -m datasets.fetch_um_resolution --dataset chaksu --subset bosch
uv run python -m datasets.fetch_um_resolution --force
```

| Option | Meaning |
| --- | --- |
| `--dataset SLUG` | One dataset, or omit to walk every catalogued store that has no published scale |
| `--subset NAME` | One subset of that dataset. Omit to do every group the grouping rule produces |
| `--data-root PATH` | The store root, same default as a fetcher |
| `--force` | Recompute even when the fingerprint still matches |

Behaviours that match the fetchers: idempotent without `--force`; a complete JSON whose
fingerprint still matches is left alone; a partial or stale JSON is finished, not started over.

## 4. What a group is

**One scale per group**, never one scale per dataset and never one scale per photograph.

A group is defined by **subset name and native width/height, with a 10% tolerance.** Photographs
belong together when they share:

- the dataset slug,
- the store's `subset` (a camera, a site, a challenge release; `main` when there is only one),
- and a native size whose `native_width` **and** `native_height` each lie within **10%** of that
  group's representative size — the median width and median height of the photographs already in
  it. A photograph that misses the 10% band on either side starts a new group.

Exact equality is not required: field-of-view detection and slight crop differences move the
native dimensions by a few pixels on the same camera. More than 10% on either side is a
different resolution, and mixing those is how a "camera scale" becomes an average of two
magnifications.

Chákṣu's three cameras are three groups because they are three subsets. A 30° disc-centred
subset and a 50° macula-centred subset are not one group even at the same pixel size: they are
different subsets, and centering changes how large the disc is in pixels.

Record the representative `native_width` × `native_height` on the JSON row. A group with fewer
photographs than the sample size uses all of them and records that `n`.

## 5. How a group is measured

Defaults of record. Changing one is a change to this skill, and it invalidates every JSON.

| Default | Value | Why |
| --- | --- | --- |
| Sample size | **32** photographs, drawn with a recorded seed | enough for a median to settle; small enough to re-run |
| Disc model | [lunetv2-odc](../../docs/models/lunetv2-odc.md) | the disc segmenter the biomarker pipelines already use for zones |
| Disc diameter | equivalent diameter from area (twice the radius of a circle of the same area), measured in the **native** frame | the disc is a vertical oval; horizontal width alone is the wrong ruler |
| Typical disc | **1,800 µm** | a round population width (~1.7–1.8 mm horizontal, 1.8–1.9 mm vertical) |
| Spread gate | median absolute deviation **≤ 10% of the median** | on one camera, disc diameter already varies about 10%; more than that is mixed devices, mixed aiming, or a model that did not find the disc |

Procedure, in order:

1. List the group's keys from the store manifest.
2. Draw 32 (or all, if fewer) with the recorded seed. **A photograph the model declines or fails is
   replaced from the remainder** until 32 succeed or the group is exhausted; record how many were
   tried (`n_drawn`) beside how many were measured (`n_measured`). This is not bookkeeping: MSHF's
   portable camera was once refused on a draw where the model measured 21 of 32 discs and their
   spread read 11.4%, while the same discs pooled sat at 5.5%. A short sample makes the gate judge
   the draw rather than the camera.
3. Measure each accepted disc's equivalent diameter in native pixels.
4. Compute the median and the median absolute deviation.
5. If MAD / median ≤ 0.10 **and** at least 16 discs were measured, accept
   `um_per_px = 1800 / median`. Write it.
6. Otherwise write the attempt with `accepted: false` and the reason (`spread`, `too-few`,
   `model-failed`). Leave that group's scale absent. A biomarker then reports pixels for that
   group, which is honest.

Do not fall back to a field-angle guess inside this command. Do not average two groups that
failed the gate into a dataset-level number.

## 6. What the JSON holds

`results/um_resolution/<slug>.json`:

```json
{
  "dataset": "chaksu",
  "typical_disc_um": 1800,
  "model": "lunetv2-odc",
  "builder_version": 6,
  "n_requested": 32,
  "seed": 0,
  "spread_gate": 0.10,
  "fingerprint": "<sha256 of the facts in section 2>",
  "groups": [
    {
      "subset": "bosch",
      "native_width": 1920,
      "native_height": 1440,
      "n_drawn": 32,
      "n_measured": 32,
      "keys": ["…"],
      "median_disc_px": 209.0,
      "mad_disc_px": 12.0,
      "mad_over_median": 0.057,
      "accepted": true,
      "um_per_px": 8.61,
      "note": ""
    }
  ]
}
```

`keys` are the photographs actually measured, so a number in a paper can be traced to the
outlines. `builder_version` is the store those discs were measured on, and a stamp into a store
built under another one is refused (section 7). Nothing in this file is a photograph.

A group that was not accepted still occupies a row: `accepted` is false, `um_per_px` is absent,
and `note` says why. Omitting the row would look like the group had not been tried.

## 7. What the manifest carries, and who puts it there

The number lives in **two** places, and only one of them is its home.

- **`results/um_resolution/<slug>.json` is the measurement**, committed, with the provenance no CSV
  cell has room for: which model, which photographs, which gate, and a fingerprint of the facts
  behind it.
- **`manifest.csv` carries a copy**, in the `um_per_px` and `resolution_source` columns it already
  has, so that a consumer reads one file rather than joining two and re-implementing the group
  match. `resolution_source` is then `disc_anchored`, which is what tells a reader the figure is
  ours rather than an author's.

`datasets.utils.resolution.stamp` is the only thing that writes that copy, and it is called from
exactly two places: this command, straight after it commits the JSON, and a store build, which
copies from the committed file. **Neither computes anything.** Three rules keep the copy honest:

- **A published figure is never overwritten.** A `field_angle` figure is, because it is also this
  repository's and it is the weaker of the two: the angle is what the camera is sold as, the disc is
  what is in the photograph. A previous `disc_anchored` figure is replaced too — it is this
  command's own copy, and the JSON is the source of truth.
- **A withdrawn measurement withdraws its copy.** A group that passed the gate once and fails it now
  leaves its rows with no scale rather than with the number the evidence has taken back. MSHF's
  `local2` did exactly that between two runs.
- **A scale measured on a differently built store is refused**, by comparing the JSON's
  `builder_version` with the store's: a changed crop changes the discs it was measured from.
- **The grouping tolerance and the stamping tolerance are one constant**
  (`resolution.SIZE_TOLERANCE`). They were briefly two, and the photographs whose discs made a
  measurement possible were the ones left without it.

A rebuilt store therefore comes back with the column filled and nothing re-measured, which is the
whole reason the measurement is committed rather than cached.

## 8. What a biomarker may and may not do with it

Load `document-biomarker` as well. The rule here is only the scale:

- **Read `resolution_source` before `um_per_px`.** The manifest carries both, and the source is
  what says whether the number is an author's measurement, a field-angle derivation, or this
  repository's disc assumption. A pipeline that reads the value and ignores the source is the
  failure this column exists to prevent.
- **Use `um_per_px` from the manifest**, whatever its source, scaled to the working size with
  `um_per_px_at` from `datasets.utils.resolution`. The JSON is where to look for *how* a
  `disc_anchored` figure was arrived at, not where to read it from.
- **An empty `um_per_px` means pixels.** A group that failed its gate leaves its photographs with
  no scale, which is honest; never invent a number to fill the gap.

It **may** convert other measurements — vessel width, lesion size, disc–fovea distance — into
microns for that camera.

It **may not** then report disc size in millimetres: by construction the group's median disc is
1.8 mm. Relative disc size in pixels is still meaningful.

It is a typical scale for the camera, not a per-eye millimetre calibration. Axial length still
changes magnification. A high-myopia or paediatric subset will bias the 1,800 µm assumption; a
glaucoma clinic usually will not, because glaucoma changes the cup, not the disc diameter.

## 9. What the method is worth

Two datasets state a field angle, which gives a scale without any assumption about disc size, so
they are the only places this method can be checked at all:

| Dataset | From its stated field angle | From the median optic disc | They differ by |
| --- | --- | --- | --- |
| [PAPILA](../../docs/datasets/papila.md), 30° | 3.777 | 3.994 | **5.8%** |
| [HRF](../../docs/datasets/hrf.md), 45° | 4.130 | 4.980 | **21%** |

Read the second row the other way: under HRF's stated field its median disc is **1,490 µm**, not the
1,800 µm this method assumes; under the disc figure its field spans **54°**, not the stated 45°.
Nothing here can say which of the two is wrong, and both derivations are this repository's rather
than an author's — the 300 µm per degree constant is a posterior-pole approximation, and a camera's
quoted angle is not always the angle subtended at the retina.

**So a `disc_anchored` figure is good to somewhere between a twentieth and a fifth**, on the two
datasets where it could be checked at all. Quote it as an order of magnitude for a camera, never as
a calibration, and never report a disc size in millimetres from it — that number was assumed.

Re-run this comparison whenever the typical disc, the disc model or the gate changes, and record
what it becomes.

## 10. Where this is documented for a reader

- **`docs/DATASETS.md`** — that most datasets publish no scale, and that inference is per camera
  from the typical disc, with evidence in `results/um_resolution/`.
- **The dataset page**, section 2 *How to fetch* and section 3's microns-per-pixel row — an
  inferred figure named as inferred, never as published, pointing at this JSON.
- **This skill** — the command, the grouping, the gate, and the JSON. There is no separate page
  under `docs/` for the utility: it is supporting code, not a catalogued model, biomarker, or
  dataset. A reader who needs the millimetre figure finds it on the dataset page and in the JSON.
  A reader who needs the method finds it here.
