---
name: fetch-dataset
description: Build a fetcher that downloads a catalogued fundus dataset, normalises it into the standard store at several rescalings, writes the manifest, and records how to fetch it in the dataset's own page. Use when adding or changing anything under src/datasets/.
---

# Fetching a dataset

A **fetcher** turns one published dataset into one directory that every other tool in this
repository can read without knowing which dataset it came from. It downloads, verifies, crops to the
field of view, resamples to each requested size, writes a manifest, and records the provenance of
what it built.

The catalogue in `docs/datasets/` says what a dataset *is*. A fetcher makes it *usable*, and the two
must agree: every fetcher is accompanied by an update to its dataset page (section 6 below).

**The reason the store is normalised rather than raw.** Forty-three datasets arrive as forty-three
layouts — RAR archives, per-split folders, spreadsheets of labels, masks in three palettes, images
from 565 to 4288 pixels across. Any comparison that reads them directly re-implements those
forty-three layouts in every consumer. One store means a consumer reads `manifest.csv`, asks for a
size, and gets pixels.

## 1. What you produce

Three things, in this order:

1. **A fetcher module**, `src/datasets/<slug>.py`, with the command-line contract in section 3. The
   slug matches the dataset page's slug exactly: `docs/datasets/hrf.md` ↔ `src/datasets/hrf.py`.
2. **Tests**, `tests/datasets/test_<slug>.py`, written **before** the fetcher and run against small
   synthetic fixtures — never against a download. Follow the repository's test-driven rule: a
   failing test first, then only enough code to pass it.
3. **A "How to fetch" subsection** added to `docs/datasets/<slug>.md` section 2, per section 6.

Common code goes in `src/datasets/utils/` and nowhere else. A helper that two fetchers need is a
`utils` module; a helper only one fetcher needs stays in that fetcher. Two fetchers holding their own
copy of a palette, a crop rule or a resize is how two datasets come to disagree about what they
contain.

## 2. The store

One directory per dataset, under a root resolved as: explicit `--data-root`, then
`$FUNDUS_ATLAS_DATA`, then `./.atlas_data/`. Everything in it is derived and gitignored — the store
is a cache, rebuildable from the sources named in `build.json`.

```
<root>/<slug>/
  build.json            what this build is: sources, sizes, completeness — section 4
  manifest.csv          one row per image — section 5
  raw/                  the untouched download, kept only with --keep-raw
  native/               field-of-view crop at full resolution, PNG
    images/<key>.png
    vessels/<key>.png   only the maps this dataset actually publishes
    av/<key>.png
    disc/<key>.png
    cup/<key>.png
    fov/<key>.png
  512/                  the same tree, resampled — one directory per requested size
    images/<key>.png
    ...
  1024/
    ...
```

Rules that make the store uniform:

- **`<key>` is stable, unique within the dataset, and derived from the source filename**, never from
  an enumeration index — a key must survive a partial rebuild and mean the same thing next year.
  Lowercase, `[a-z0-9_]`, with the published split in it where the dataset has one:
  `training_21`, `test_04`, `image13`.
- **Every map a dataset publishes is built at every requested size.** Do not decide that a disc mask
  "belongs at 512": the grid belongs to the *model* being evaluated, not to the dataset, and the
  atlas evaluates models with grids from 256 to 1472 (see `docs/MODELS.md`). A fetcher that builds
  one size forces every consumer to resample, which is the thing the store exists to prevent.
- **`native/` is always built.** It is the reference the resampled sizes are derived from, and the
  only copy whose pixel count matches what the authors published.
- **A dataset's own subcollections stay distinguishable** through the `subset` column, never through
  separate directories — one dataset is one store.

## 3. The command-line contract

Every fetcher is a module runnable as `uv run python -m datasets.<slug>` and accepts exactly these
options, with these meanings, so that a person who has used one fetcher has used all of them:

| Option | Meaning |
| --- | --- |
| `--sizes 512,1024` | Sizes to build besides `native/`. Default `512,1024`. Any positive integers; the atlas's models span 256 to 1472, so intermediate sizes are ordinary, not exceptional |
| `--archive PATH` | Use an archive already on disk instead of downloading. **Required for every dataset whose Down column is not ✅** |
| `--raw PATH` | Use an already-extracted tree, skipping download and extraction |
| `--data-root PATH` | Override the store root |
| `--keep-raw` | Keep `raw/` after building; default is to delete it |
| `--force` | Rebuild even if the store looks complete |
| `--limit N` | Build only the first N images — for development, and it must mark the build as partial in `build.json` |
| `--no-verify` | Skip checksum verification. Prints a warning; never the default |

And these behaviours:

- **Idempotent.** Running twice does nothing the second time. An existing archive is not
  re-downloaded, an existing store is not rebuilt without `--force`.
- **Resumable.** A build interrupted halfway continues rather than restarting: an image whose
  outputs all exist and whose manifest row is present is skipped.
- **Verifying.** A download is checked against a recorded sha256 before extraction. A mismatch is an
  error, not a warning — a silently different archive is how a benchmark comes to measure something
  other than what it says.
- **Honest about what it could not do.** A missing optional annotation layer is a warning and a
  built store; a missing required one is an error. Either way it is recorded in `build.json`.
- **Never fetches what the licence does not allow.** For a dataset behind credentialing, a request
  form or a signed agreement (`⛔` in `docs/DATASETS.md`), the fetcher must **not** attempt a
  download: it requires `--archive` and prints the page's own instructions. Automating around a human
  step is a licence violation dressed as convenience.

## 4. `build.json` — what this directory actually is

Written on every successful build, replaced on `--force`. It holds **only what cannot be recovered
from the manifest or from `docs/datasets/<slug>.md`** — the build's own state, not the dataset's
description:

```json
{
  "built_at": "2026-09-11T14:03:22Z",
  "builder_version": 1,
  "sizes": [512, 1024],
  "images": 45,
  "partial": false,
  "sources": [
    {"layer": "hrf", "url": "https://www5.cs.fau.de/.../all.zip", "sha256": "…"},
    {"layer": "hrf-av", "url": "https://github.com/rubenhx/av-segmentation", "sha256": "…"}
  ],
  "missing_layers": [],
  "warnings": ["512 exceeds the crop for 3 images; those rows are upsampled"]
}
```

Three of those fields are the reason the file exists at all:

- **`sources`** — *which copy you downloaded*. Several datasets have more than one route serving
  different bytes: [IDRiD](../../docs/datasets/idrid.md) from IEEE DataPort or a third-party Zenodo
  mirror, [G1020](../../docs/datasets/g1020.md) from DFKI or a Kaggle bundle,
  [REFUGE](../../docs/datasets/refuge.md) from the challenge or a mirror nobody guarantees is
  complete. The manifest's per-image checksums prove the files are intact; only this says where they
  came from.
- **`partial`** — *whether the store is the whole dataset*. A `--limit 5` build, an interrupted
  build and a genuinely small dataset are indistinguishable by listing directories, and a silently
  truncated store yields a plausible benchmark number. Set it for `--limit`, and clear it only when
  a build completes.
- **`builder_version`** — *whether the store predates a change in the rules*. When the crop or
  resample rule changes, every store built before it is stale; bumping this is what lets a consumer
  refuse to mix them.

**What must not go in it**, because it is already elsewhere and two copies drift: the dataset's name,
citation, licence or home page (the dataset page), the resolution and its source (copied into every
manifest row), and which maps exist (the manifest's `maps` column).

## 5. `manifest.csv` — the schema

One row per image. **These columns, these names, this order**, in every dataset's manifest. A
consumer can then read any store without special-casing. Missing values are empty, never `0`,
`-1` or `NaN`-as-string.

| Column | Type | Meaning |
| --- | --- | --- |
| `key` | str | Stable unique id, as in section 2 |
| `subset` | str | The dataset's own well-defined subcollection: a camera, a site, a challenge release. `main` where a dataset has only one |
| `split` | str | `train`, `val`, `test`, or `unspecified` — **only as the authors published it**, never invented |
| `native_width` | int | Source image width in pixels |
| `native_height` | int | Source image height |
| `fov_cx`, `fov_cy`, `fov_r` | float | Field-of-view circle in native pixels: centre and radius |
| `fov_source` | str | `mask` (the dataset ships one), `detected`, or `assumed_full_frame` |
| `crop_x0`, `crop_y0`, `crop_side` | int | The square crop taken from the native image, in native pixels |
| `mm_per_px` | float | Native resolution, empty when unknown — section 7 |
| `resolution_source` | str | `published`, `field_angle`, `disc_anchored`, `inherited`, or `unknown` |
| `maps` | str | Semicolon-separated list of the maps present for this row: `vessels;fov` |
| `readers` | str | Semicolon-separated reader ids where a dataset keeps annotators separate: `expert1;expert2`. Empty for a single consensus |
| `eye` | str | `od`, `os`, or empty |
| `disease` | str | The dataset's own label, verbatim, not remapped to a common vocabulary |
| `quality` | str | The dataset's own quality grade, verbatim |
| `source_image` | str | Path of the source file inside the archive, so a row can be traced back |
| `sha256` | str | Checksum of the source image file |
| `notes` | str | Per-image caveats: a stray file, an odd field angle, a mask that disagrees with its description |

Two deliberate absences. **No per-size columns**: the µm/px at any size is computed from `mm_per_px`,
`crop_side` and the size (section 7), and storing it invites the stored and computed values to drift.
**No common disease vocabulary**: datasets grade differently and a mapping is a research decision, so
the manifest keeps what the authors wrote and any mapping lives in the consumer.

## 6. The dataset page's "How to fetch"

Every fetcher adds a subsection at the end of section 2 of `docs/datasets/<slug>.md`, numbered after
the provenance tables (`### 2.3 How to fetch` where the page has 2.1 and 2.2). It contains:

- **The command**, including the human step where there is one:

  ```bash
  uv run python -m datasets.hrf                      # downloads and builds 512 and 1024
  uv run python -m datasets.hrf --sizes 512,720,1024
  uv run python -m datasets.hrf --archive ~/all.zip  # an archive fetched by hand
  ```

- **What it downloads** — which layers, how large, and which are optional.
- **What it builds** — the maps, and any layer that will be missing if an optional download is
  skipped.
- **What needs a human**, for a `🟡` or `⛔` dataset: the form, the account, the agreement, and what
  to pass `--archive`.
- **Anything peculiar** to this dataset that a person running it will hit: an archive format needing
  an external tool, a legacy spreadsheet, a mask palette, a file that must be skipped.

Keep it to what someone running the command needs. The *provenance* — citation, licence, home page —
is already in the tables above it and must not be repeated.

## 7. Resolution, and inferring it when it is missing

Every physical measurement is a pixel count times a scale, and a wrong scale produces numbers that
are wrong but plausible — nothing errors. Most catalogued datasets publish no scale at all, so
inference has to be systematic, visible and correctable.

**Where it lives.** `src/datasets/utils/resolution.py` holds one declared entry per dataset, and per
*subset* where a dataset's subcollections differ (Chákṣu's three cameras, LES-AV's one 45° image among
21 at 30°). The values are written in code, reviewed like code, and each carries its derivation as a
comment. A store's `manifest.csv` copies the value and its source into every row, so a consumer never
has to look it up and can always see where it came from.

**The four sources, in order of preference:**

1. **`published`** — the dataset or its paper states microns or millimetres per pixel. Use it.
2. **`field_angle`** — the dataset states a field of view. At the posterior pole a degree of field is
   about **0.3 mm** of retina, so `mm_per_px = 0.3 * degrees / fov_diameter_px`. State the assumption
   in the comment; it is an approximation that ignores eye length and projection.
3. **`disc_anchored`** — no field angle, but the dataset (or a reader) marks the optic disc. A real
   optic disc is about **1.8 mm** across, so `mm_per_px = 1.8 / disc_diameter_px`. Prefer this to a
   guessed field angle: it is anchored on the eye rather than on the camera.
4. **`inherited`** — the photographs are another dataset's, so the scale is too. RITE inherits DRIVE's;
   RETA inherits IDRiD's **divided by the resize factor**, because RETA ships a 1024-pixel rendition
   of a 4288-pixel original.

And the fifth case: **`unknown`**. Leave `mm_per_px` empty. A consumer then reports pixels, which is
honest, rather than microns, which is not. **Never invent a plausible number to fill the column.**

**From native to any size.** One pixel at a built size spans `crop_side / size` native pixels, so:

```
um_per_px(size) = mm_per_px * crop_side / size * 1000
```

`crop_side` varies per image, so this is per row, not per dataset — which is why the manifest records
the crop. `utils/resolution.py` exposes exactly this as a function; no consumer recomputes it.

## 8. Field of view, crop and resampling

These three decisions are shared by every fetcher and therefore live in `utils`, not in fetchers.

- **Field of view.** Use the dataset's own mask when it ships one (`fov_source: mask`). Otherwise
  detect the illuminated circle (`detected`). Only when neither is possible does a fetcher assume the
  whole frame (`assumed_full_frame`), and that assumption is recorded per row because it changes
  every area-based measurement.
- **Crop.** A square centred on the field-of-view circle, side equal to its diameter, clipped to the
  image. Square, because every model in `docs/MODELS.md` resamples to a square grid, and doing it
  once here means a consumer never resamples twice.
- **Resampling.** Images with area-averaging when downsizing and Lanczos when upsizing; masks with
  **nearest-neighbour only** — a mask interpolated with anything else invents classes that were never
  annotated. A multi-class artery/vein map is resampled per class, never as an RGB image.
- **Never upsample silently.** When a requested size exceeds the crop, build it, but record a
  `notes` entry on the row and a warning in `build.json`: a Dice measured on an upsampled image is
  not comparable with one measured on a downsampled image, as `docs/datasets/drive.md` explains.

## 9. Rules that apply to every fetcher

- **9.1 Reference, never redistribute.** The store is a local cache. Nothing built here is published,
  mirrored or committed — that includes fixtures: tests use synthetic images, never real ones.
- **9.2 Honour the access route.** `⛔` datasets require `--archive`. Never embed credentials, never
  scrape a form, never mirror a credentialed archive.
- **9.3 Record provenance, not just data.** Anything a consumer would need in order to trust a number
  goes in the manifest, or — when it is a property of the build rather than of an image — in
  `build.json`. Put each fact in exactly one of them: a value kept in both will eventually disagree
  with itself.
- **9.4 Fail loudly, build partially only on request.** A missing required layer aborts. `--limit`
  marks the build partial. A store must never look complete when it is not.
- **9.5 Keep the catalogue and the code in step.** A fetcher whose behaviour contradicts its dataset
  page is a bug in one of them; fix both in the same commit. If building the dataset teaches you
  something the page does not say — a count that differs, a mask that disagrees with its
  documentation — that is a finding for the page's section 7, `Known defects`.
- **9.6 Every file starts with the two-line `ABOUTME:` comment** the repository requires, and
  functions carry the docstring style of the surrounding code.
