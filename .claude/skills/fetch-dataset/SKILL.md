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
must agree: every fetcher is accompanied by an update to its dataset page (section 7 below).

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
3. **A "How to fetch" subsection** added to `docs/datasets/<slug>.md` section 2, per section 7.

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
  labels.csv            per-reader grades, only where a dataset publishes more than one — section 5.1
  raw/                  the untouched download — deleted after the build unless --keep-raw
  native/               field-of-view crop at full resolution
    images/<key>.png
    vessels/<key>.png   only the maps this dataset actually publishes
    av/<key>.png
    fov/<key>.png       the transported field-of-view mask — section 9
    contours/<key>.csv  optic disc and cup as polygons, not rasters — section 10
  512/                  the same tree, recomputed — one directory per requested size
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
- **Every map a dataset publishes is built at every requested size**, contours included — they are
  scaled from the native frame, never re-traced per size (section 10). Do not decide that a disc mask
  "belongs at 512": the grid belongs to the *model* being evaluated, not to the dataset, and the
  atlas evaluates models with grids from 256 to 1472 (see `docs/MODELS.md`). A fetcher that builds
  one size forces every consumer to resample, which is the thing the store exists to prevent.
- **`native/` is the derivation reference, and must be sufficient to build any future size on its
  own** — no network, no archive. Everything else in the store is a function of it.
- **`native/` is always built, and is not optional.** It is the reference every resampled size is
  derived from, and the only copy whose pixel count matches what the authors published. There is no
  flag to skip it: a store without it cannot answer what a measurement would have been at full
  resolution, and rebuilding it means downloading the dataset again. It costs disk — IDRiD's 516
  images at 4288×2848 are the worst case here — and that is the right trade against a download that
  may need a form, an account or a signed agreement.

- **`raw/` is deleted after a successful build**, unless `--keep-raw` is passed. It is the archive as
  downloaded, reconstructible from the URL and checksum in `build.json`, and it is the largest thing
  in the store. Keep it while developing a fetcher, when the download needs a human step you would
  rather not repeat, or when you suspect the extraction itself is wrong.
- **A dataset's own subcollections stay distinguishable** through the `subset` column, never through
  separate directories — one dataset is one store.

## 3. The command-line contract

Every fetcher is a module runnable as `uv run python -m datasets.<slug>` and accepts exactly these
options, with these meanings, so that a person who has used one fetcher has used all of them:

| Option | Meaning |
| --- | --- |
| `--sizes 512,1024` | The sizes that should **exist** besides `native/`, not the sizes to rebuild. Default `512,1024`. Any positive integers; the atlas's models span 256 to 1472, so intermediate sizes are ordinary. On an existing store this adds the missing ones from `native/` without downloading anything — section 11 |
| `--archive PATH` | Use an archive already on disk instead of downloading. **Required for every dataset whose Down column is not ✅** |
| `--raw PATH` | Use an already-extracted tree, skipping download and extraction |
| `--data-root PATH` | Override the store root. The default is `.atlas_data/` in the repository, git-ignored; `FUNDUS_ATLAS_DATA` moves every store at once |
| `--keep-raw` | Keep the downloaded archive in `raw/` after building. **Default is to delete it** — it is reconstructible from `build.json`, and it is the bulk of the store. `native/` is never affected by this flag and is always kept |
| `--force` | Rebuild even if the store looks complete |
| `--limit N` | Build only the first N images — for development, and it must mark the build as partial in `build.json` |
| `--jobs N` | How many images to build at once. Default is one per core; `1` builds in this process, which is what to use when a traceback matters more than the wall clock. Building an image is independent of every other image, so the store is identical either way — verified by building the same forty photographs on one core and on eight and comparing every byte |
| `--no-verify` | Skip checksum verification. Prints a warning; never the default |

And these behaviours:

- **Parallel by default.** Images are built across as many processes as the machine has cores.
  Nothing is shared between them but the disk: each reads its own bytes and writes its own files,
  so the rows keep the order the fetcher discovered them in and the store does not depend on how
  many cores built it.
- **Idempotent.** Running twice does nothing the second time. An existing archive is not
  re-downloaded, an existing store is not rebuilt without `--force`, and a size that already exists
  is not recomputed. Asking for a size that does not exist yet builds only that size, from
  `native/` — section 11.
- **Resumable.** A build interrupted halfway continues rather than restarting: an image whose
  outputs all exist and whose manifest row is present is skipped.
- **Verifying.** A download is checked against a recorded sha256 before extraction. A mismatch is an
  error, not a warning — a silently different archive is how a benchmark comes to measure something
  other than what it says.
- **Honest about what it could not do.** A missing optional annotation layer is a warning and a
  built store; a missing required one is an error. Either way it is recorded in `build.json`.
- **Unmoved by a file the dataset published broken.** Datasets ship corrupt files — one of FQS's
  2,246 originals is a PNG cut short mid-image — and that is a fact about the dataset, not a reason
  to abandon the build. The image is skipped, named in `build.json`, warned about on the console
  and recorded on the dataset page. It is never loaded with its readable part padded out, which
  would put invented pixels in the store under the dataset's name.
- **Resumable in its downloading, too.** Large archives are fetched in ranged pieces that resume
  what is already on disk, because a single connection to a public host will accept a
  ten-gigabyte request, deliver three gigabytes and then go quiet indefinitely. A partial file
  larger than the archive it claims to be is an error, not something to resume from.
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
| `crop_x0`, `crop_y0`, `crop_side` | int | The square crop, in native pixels. `crop_x0`/`crop_y0` may be **negative** and the square may extend past the image: the source is pasted into a square canvas rather than sliced from it — section 9 |
| `pad_fraction` | float | Fraction of the square canvas with no source behind it. `0.0` when the crop fitted inside the image; a large value means much of the frame is invented |
| `um_per_px` | float | Native resolution in **microns per pixel**, empty when unknown — section 8 |
| `resolution_source` | str | `published`, `field_angle`, `disc_anchored`, `inherited`, or `unknown` |
| `maps` | str | Semicolon-separated list of what this row has: `vessels`, `av`, `fov`, `disc`, `cup` — the last two meaning contours in `contours/<key>.csv`, not a raster. Example: `vessels;fov;disc;cup` |
| `readers` | str | Semicolon-separated ids of every annotator who contributed anything to this image — a contour, a grade, or both: `expert1;expert2`. Empty where the dataset publishes one opinion and does not name who held it |
| `multi_reader` | str | Semicolon-separated names of the fields for which `labels.csv` holds more than one opinion: `quality;disease`. Empty for the common case — section 5.1 |
| `patient` | str | The dataset's own subject id, verbatim — the same value on every image of the same person. Empty where the dataset publishes none — section 5.3 |
| `visit` | str | The dataset's own session id or date where a person was photographed more than once. Empty otherwise — section 5.3 |
| `eye` | str | `od` (right), `os` (left), or empty |
| `disease` | str | The dataset's own label, verbatim, not remapped to a common vocabulary. One value: the published consensus, or the only reader's, or empty — section 5.1 |
| `quality` | str | Always `good`, `usable`, `bad` or empty — the dataset's own grade mapped, or derived from its component ratings — section 5.4. One value, on the same rule as `disease` |
| `quality_source` | str | `published` or `derived`, so the two are never pooled by accident. Empty where there is no grade at all |
| `source_image` | str | Path of the source file inside the archive, so a row can be traced back |
| `sha256` | str | Checksum of the source image file |
| `notes` | str | Per-image caveats: a stray file, an odd field angle, a mask that disagrees with its description |

Two deliberate absences. **No per-size columns**: the µm/px at any size is computed from `um_per_px`,
`crop_side` and the size (section 8), and storing it invites the stored and computed values to drift.
**No common disease vocabulary**: datasets grade differently and a mapping is a research decision, so
the manifest keeps what the authors wrote and any mapping lives in the consumer.

### 5.1 Labels that more than one person gave

Most datasets publish one disease label and one quality grade per photograph, and the manifest
columns hold them. But grading is a judgement, and some datasets keep each grader's judgement
separately — Chákṣu publishes five ophthalmologists' glaucoma decisions, DeepDRiD two graders per
image. Flattening those to one value throws away the only honest thing the dataset says about how
certain the label is, and it is the same problem the disc and cup contours have (section 10), so it
gets the same answer: **keep every opinion, and give the manifest one of them.**

Per-reader labels live in **`labels.csv` at the root of the store**, beside `manifest.csv` and not
inside any size directory — a grade does not change when the photograph is resampled:

```
<root>/<slug>/labels.csv:   key,field,reader,value
                            image_07,quality,grader1,good
                            image_07,quality,grader2,usable
                            image_07,quality,consensus,good
                            image_07,disease,expert3,glaucoma suspect
```

| Column | Meaning |
| --- | --- |
| `field` | The manifest column this is an opinion about: `disease`, `quality`, or any dataset-specific column from section 5.2 |
| `reader` | The dataset's own id for the grader, or `consensus` for a value the dataset itself publishes as agreed |
| `value` | Verbatim, exactly as in the manifest columns — never remapped |

The rules:

- **The file exists only when it has something to say.** A dataset with one opinion per image has no
  `labels.csv`, and a consumer must treat its absence as normal rather than as a broken store.
- **The manifest value is chosen, not summarised.** It is the `consensus` row where the dataset
  publishes one, the single reader's value where there is only one, and **empty where readers
  disagreed and the dataset declared no winner**. A fetcher never invents a majority vote: which
  grader to believe is the consumer's research decision, and the store must not make it for them.
- **`multi_reader` says when the manifest is hiding something.** An empty `quality` can mean the
  dataset graded nothing or that five people disagreed, and those are opposite facts. Listing the
  field in `multi_reader` distinguishes them without opening `labels.csv`.
- **One source, two renderings.** The fetcher hands `utils.manifest` every reading once; the helper
  writes both `labels.csv` and the manifest cell. Neither is typed twice, so they cannot drift.

### 5.2 Dataset-specific columns

Some datasets publish per-image facts that no other dataset has: BRSET records patient age, sex and
comorbidities; others carry intraocular pressure, refraction or an acquisition date. Discarding them
would make the store less useful than the archive it came from, and adding them to the fixed schema
would put forty empty columns in every other dataset's manifest.

So a fetcher may **append its own columns after `notes`**, and only after it:

- **The fixed schema keeps its names and its order**, unchanged and first. A consumer reading by
  column name is unaffected; one reading the tail must expect columns it has never seen and ignore
  them rather than fail.
- **Names are lowercase `[a-z0-9_]`, and must not restate something the schema already holds** under
  another name. A second spelling of the resolution or the split is a drift bug waiting to happen.
- **Values are verbatim**, on exactly the rule that governs `disease`: the dataset's own vocabulary,
  its own units, no remapping. `sex` holds whatever the authors wrote — `M`, `male`, `1` — and the
  consumer that needs a common vocabulary defines one.
- **Each column is declared in the fetcher with a one-line description**, and those descriptions go
  in the dataset page's *How to fetch* subsection. The manifest header says which columns exist; the
  page says what they mean. They are not listed in `build.json` as well — that is the third copy the
  rule at the end of section 4 exists to prevent.
- **A dataset-specific column can be multi-reader too.** Put the readings in `labels.csv` with
  `field` set to the column name; the manifest cell and `multi_reader` behave as in section 5.1.
- **These columns describe people.** The store is a local cache, is never committed to this
  repository, and the dataset's own licence governs what may be done with participant attributes —
  including whether they may be published in a table of results at all.

### 5.3 Images that belong to the same person

Rows in a manifest are not independent observations. A dataset may photograph both eyes of one
person, the same eye at several visits, or the same eye twice in one sitting, and three things break
quietly when that goes unrecorded:

- **A random train/test split puts one person on both sides.** The model is then scored partly on
  faces it has already seen, and the number comes out too good. Splitting must be done by person, not
  by image, which is impossible if the manifest does not say who is who.
- **Confidence intervals come out too narrow.** Two eyes of one person are more alike than two eyes
  of two people; counting them as two independent measurements overstates how much evidence there is.
- **A paired comparison is unavailable.** Left against right, or visit against visit, is often the
  most sensitive question a dataset can answer, and it needs the pairing.

Hence `patient`, `visit` and `eye`. The rules:

- **Verbatim, and unique within the store.** Use the dataset's own identifier. Where subcollections
  reuse the same numbering for different people, prefix it with the subset so that two rows sharing a
  `patient` really are one person.
- **Derive an id only where the authors document the convention.** Several datasets encode it in the
  filename — `21_left.png` and `21_right.png` are one person — and that is a fact to record, with the
  derivation stated in the dataset page. Inferring identity from a filename pattern the authors never
  described is a guess that silently merges or splits people; leave the column empty instead.
- **Empty means unknown, not unique.** A consumer must treat empty `patient` as *no grouping
  information*, and must not assume every such row is a different person.
- **Anything finer is a dataset-specific column.** Which retinal field a photograph is centred on,
  which device took it, which of two shots in a sitting it is — those belong in section 5.2's tail
  columns, not in the fixed schema.

### 5.4 Quality that arrives as a set of ratings

Some datasets do not publish an overall verdict on a photograph. They publish what an expert scored
each aspect of it: focus, illumination, contrast, the visibility of the optic disc and macula, the
presence of artefacts. That is more information than a single grade, not less, and it must not be
thrown away — but a consumer comparing datasets needs a grade, and one derived by each consumer
separately would make two papers using "good" mean different things.

So both are stored:

- **Every component rating is its own column**, on section 5.2's rules: verbatim, in the dataset's own
  scale, named as the authors named it. Where the ratings are per-grader they go in `labels.csv`
  (section 5.1) with `field` set to the component's column name.
- **`quality` then holds a three-value grade**, and **`quality_source` records how it got there**.

**`quality` holds one of three words in every dataset** — `good`, `usable`, `bad` — or is empty
where the dataset grades nothing. A column whose vocabulary changes per dataset cannot be filtered
across datasets, which is the only reason to have the column at all.

**Where the dataset publishes its own overall grade, that grade is mapped, not recomputed.** The
fetcher declares the mapping — `quality.Published({"1": "good", "0": "bad"})` — and **the authors'
own token is kept verbatim in a dataset-specific column**, so the mapping is auditable and
reversible. A two-level dataset simply has no `usable`; inventing a middle level it never graded
would be worse than lacking one.

**Where the dataset publishes only component ratings, the grade is derived:**

| Components | `quality` |
| --- | --- |
| All at their scale's best value | `good` |
| Exactly one short of best | `usable` |
| Anything else — two or more short, or a component not rated at all | `bad` |

Because "best" differs per dataset and per component — and is not always the highest number, since a
rating of *artefacts* is best at zero — the fetcher declares it rather than the helper guessing:
`quality.FromComponents({"artifact": "0", "clarity": "10", ...})`, each entry naming the value that
counts as full marks. A component the dataset left blank counts as short of best, which is
deliberately pessimistic: an unrated aspect is not evidence of a good one.

The rules around it:

- **A published grade wins over a derived one.** Where the dataset states an overall verdict, that
  verdict — mapped — is what `quality` holds, even when component ratings are also present, and
  `quality_source` is `published`. Deriving one instead would overwrite the authors' judgement with
  ours, which section 4.4 of `CLAUDE.md` forbids. The difference is not academic: in
  [DeepDRiD](../../docs/datasets/deepdrid.md), which publishes both, the all-at-best rule calls 295
  of the 576 photographs its ophthalmologists judged good enough for diagnosis `bad`, because a
  perfect field-definition score there means the disc and macula both sit within one disc diameter
  of the centre — excellent framing, not a precondition for reading the image.
- **`quality_source` exists so the two are never pooled silently.** A study filtering on
  `quality == "good"` across several datasets is mixing authors' grades with ours unless it checks
  this column, and that mixture is invisible without it.
- **Derive per grader, not from an average.** Where each grader rated the components, the rule runs
  once per grader into `labels.csv`; the manifest cell then follows section 5.1 — the graders' value
  where they agree, empty with `quality` listed in `multi_reader` where they do not. Averaging
  ratings across graders before applying the rule would manufacture a verdict nobody gave.
- **The derivation is stored, and therefore versioned.** It is computed at build time and written
  into the row. If the rule ever changes, every store built under the old one is stale, which is what
  `builder_version` in `build.json` is for.

### 5.5 Codes the dataset itself explains

Datasets label in integers and explain them in a Readme: DeepDRiD's `3` means severe non-proliferative
diabetic retinopathy, its `0` means no apparent retinopathy. **Store the explanation, not the code.**

- `disease` holds `severe npdr`, not `3`. A reader of the manifest should not need the dataset's
  documentation open to know whether one row is worse than another, and `0` is one misreading away
  from being taken for "no value" — which, in a column where empty genuinely means *ungraded*, is a
  mistake that changes results rather than just confusing someone.
- **This is not a common vocabulary.** The words stay the dataset's own, lowercased and otherwise
  untouched; nothing is mapped onto another dataset's terms. It is the difference between storing a
  label and storing a footnote marker.
- **A code the legend does not explain is an error**, never passed through. A dataset that has grown
  a grade since its fetcher was written is a thing to look at, not to record as `7`.
- **Ordinal scores stay numeric.** Where the dataset publishes a graded scale rather than named
  categories — DeepDRiD's artefact, clarity and field-definition scores run 0 to 10, each step a
  sentence long — the number is the label, and the sentence belongs in the column's description and
  on the dataset page. Say which direction is better there: a score whose best value is zero is
  otherwise read backwards.

`utils.manifest.spell_out` does this, given the legend the fetcher declares.

## 6. Exclusions — images that turned out to be unusable

Occasionally an image in a published dataset is wrong: a mask belonging to a different photograph, a
file that is not a fundus image at all, a pair whose halves do not match, an annotation that
contradicts its own documentation. These are findings, and they need somewhere to live that is not a
code comment and not a person's memory.

**They live in the repository, not in the store:** `src/datasets/exclusions/<slug>.json`, version
controlled, reviewed like code, and travelling with the fetcher. The store is a cache that anyone can
delete and rebuild; a finding that took an afternoon to establish must survive that.

```json
{
  "dataset": "example",
  "exclusions": [
    {
      "key": "training_21",
      "maps": "*",
      "reason": "ground-truth-wrong",
      "detail": "The vessel mask does not correspond to this photograph — it matches a different image in the same split.",
      "evidence": "docs/datasets/example.md, section 7",
      "found": "2026-09-11"
    },
    {
      "key": "image_31",
      "maps": ["av"],
      "reason": "annotation-incomplete",
      "detail": "The artery/vein map covers only the superior half; the vessel mask is fine and stays usable.",
      "evidence": "visual inspection against the source archive",
      "found": "2026-09-11"
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `key` | The manifest key, so an exclusion survives a rebuild |
| `maps` | `"*"` for the whole image, or a list naming only the broken maps — an image whose A/V map is wrong may still be a perfectly good vessel case |
| `readers` | `"*"`, or a list naming only the annotators whose work is wrong. Chákṣu's `Image145` has five experts' discs and one of them is a broken mask; excluding `disc` for that image would throw away four good outlines to be rid of one bad one. A finding scoped to readers leaves the row and its `maps` alone — the image still has that structure, drawn by everyone else — and only `utils.exclusions.trusted_outlines` drops the condemned pair |
| `reason` | One of a fixed vocabulary: `ground-truth-wrong`, `annotation-incomplete`, `image-corrupt`, `not-a-fundus`, `duplicate-within-dataset`, `mismatched-pair`, `wrong-modality` |
| `detail` | What is actually wrong, in a sentence a stranger can act on |
| `evidence` | Where the finding is written up: a section of the dataset page, an upstream issue, or how it was checked |
| `found` | The date, so a reader can tell a finding from 2015 from one from last week |

Three rules decide how this behaves, and each is chosen against a specific way of getting it wrong:

- **An image that cannot be built is not an exclusion.** A file the dataset published broken never
  becomes a row, and there is nothing for a read-time filter to remove: `build.json` names it and
  the dataset page explains it, which is the one place that fact lives. Exclusions are for images
  that are in the store and should not be trusted.
- **Exclusions are applied when the store is read, never when it is built.** The build writes every
  image the dataset published, including the broken ones. A store that quietly omits them cannot be
  used to re-examine the finding, and its image count stops matching the dataset page — which is how
  a mistaken exclusion becomes permanent. `utils.manifest.load(slug)` filters by default and takes
  `include_excluded=True` for anyone checking the finding itself.
- **The JSON is the only copy.** No `excluded` column in the manifest: a fact kept in two places
  eventually disagrees with itself, and a new finding must take effect without rebuilding a store
  that may have taken a signed agreement to download.
- **An exclusion is also a catalogue finding.** Anything excluded here appears in that dataset's
  page, section 7, in prose, with the same reason. The JSON is what the code reads; the page is what
  a person reads; a discrepancy between them is a bug in the atlas.

**What is not an exclusion.** A photograph shared with another dataset is *inheritance*, recorded in
the dataset page's section 5 — excluding it would silently shrink a dataset because of something true
about a different one. A dataset being training data for some model is *contamination*, which is the
consumer's business, not the store's. And an image you simply do not want — too dark, too small, the
wrong disease — is a *filter*, which belongs in the analysis that wants it, not in a file that
declares the image unusable for everyone.

## 7. The dataset page's "How to fetch"

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

## 8. Resolution, and inferring it when it is missing

Every physical measurement is a pixel count times a scale, and a wrong scale produces numbers that
are wrong but plausible — nothing errors. Most catalogued datasets publish no scale at all, so
inference has to be systematic, visible and correctable.

**Where it lives.** `src/datasets/utils/resolution.py` holds one declared entry per dataset, and per
*subset* where a dataset's subcollections differ (Chákṣu's three cameras, LES-AV's one 45° image among
21 at 30°). The values are written in code, reviewed like code, and each carries its derivation as a
comment. A store's `manifest.csv` copies the value and its source into every row, so a consumer never
has to look it up and can always see where it came from.

**The four sources, in order of preference:**

1. **`published`** — the dataset or its paper states microns or millimetres per pixel. Use it,
   converting to microns.
2. **`field_angle`** — the dataset states a field of view. At the posterior pole a degree of field is
   about **300 µm** of retina, so `um_per_px = 300 * degrees / fov_diameter_px`. State the assumption
   in the comment; it is an approximation that ignores eye length and projection.
3. **`disc_anchored`** — no field angle, but the dataset (or a reader) marks the optic disc. A real
   optic disc is about **1800 µm** across, so `um_per_px = 1800 / disc_diameter_px`. Prefer this to a
   guessed field angle: it is anchored on the eye rather than on the camera.
4. **`inherited`** — the photographs are another dataset's, so the scale is too. RITE inherits DRIVE's;
   RETA inherits IDRiD's **divided by the resize factor**, because RETA ships a 1024-pixel rendition
   of a 4288-pixel original.

And the fifth case: **`unknown`**. Leave `um_per_px` empty. A consumer then reports pixels, which is
honest, rather than microns, which is not. **Never invent a plausible number to fill the column.**

**From native to any size.** One pixel at a built size spans `crop_side / size` native pixels, so:

```
um_per_px_at(size) = um_per_px * crop_side / size
```

`crop_side` varies per image, so this is per row, not per dataset — which is why the manifest records
the crop. `utils/resolution.py` exposes exactly this as a function; no consumer recomputes it.

## 9. Field of view: a true crop and paste, not a redrawn circle

**What counts as surround.** Not "the dark part" — cameras and exporters disagree, and the same
dataset can hold both conventions: twenty of DeepDRiD's photographs write the area outside the
field **white**, the rest write it black, and others in this catalogue write a flat grey. What every
surround has in common is that it is **one colour and it reaches the edge of the frame**, so that is
the test `utils/fov.py` applies: learn the colour from the border ring, then take the
surround-coloured region *connected to* the border. Two consequences worth stating, because both
are easy to get wrong in the other direction:

- **A patch inside the retina is not surround, even in the surround's own colour.** It fails the
  connectivity test, stays inside the mask, and the mask keeps meaning *where the camera was
  looking* rather than *where the photograph came out well*.
- **A burnt-in index or timestamp out in the surround is not field.** It is not surround-coloured,
  so only taking the field's largest connected region excludes it.

A photograph with no uniform border at all — retina reaching the frame's edge the whole way round —
has no circle to find, and is recorded as `assumed_full_frame` rather than guessed at.


The field-of-view mask is **the authority on which pixels are real**, and it is produced by putting
a real mask through exactly the transformation the photograph goes through — never by drawing a
circle from the stored centre and radius.

- **Where the mask comes from.** The dataset's own mask when it ships one (`fov_source: mask`),
  otherwise the illuminated region detected from the photograph (`detected`), and only when neither
  is possible the whole frame (`assumed_full_frame`). The last case is recorded per row because it
  changes every area-based measurement.
- **Crop and paste.** The crop is a square centred on the field-of-view circle with side equal to its
  diameter — and that square frequently **extends past the edge of the source image**, because a
  fundus is often cut off at top and bottom. The source is therefore *pasted* into a square canvas
  rather than sliced out of it, and the region with no source behind it is padding.
- **The mask travels with the image, pixel for pixel.** The same crop, the same paste, the same
  canvas, resampled with nearest-neighbour. Padding is `0` in the field-of-view mask, so a consumer
  can tell invented pixels from photographed ones without knowing anything about the crop geometry.
- **Why not redraw the circle.** A redrawn circle is a different shape from the mask it replaces: it
  loses the flat edges where the fundus was cut off, the notches some cameras leave, and the
  distinction between padding and dark-but-real retina. Measurements taken over a redrawn circle
  count padding as retina, which inflates every density and every area.
- `fov_cx`, `fov_cy` and `fov_r` stay in the manifest as the **geometry that produced the crop**.
  They describe the circle that was fitted; they are not a substitute for the mask.

## 10. Optic disc and cup: contours, not rasters

Disc and cup are stored as **polygon nodes in a CSV per image**, one file holding every structure and
every reader, present at every size alongside the other maps.

```
<size>/contours/<key>.csv:   structure,reader,node,x,y
                             disc,expert1,0,412,388
                             disc,expert1,1,418,376
                             cup,expert2,0,455,402
```

| Column | Meaning |
| --- | --- |
| `structure` | `disc` or `cup` |
| `reader` | The annotator's id where a dataset keeps them separate — `expert1`, `expert2` — or `consensus` |
| `node` | Node index within that structure and reader, in traced order |
| `x`, `y` | Integer pixel coordinates **in this directory's frame** |

Three reasons this beats a raster:

- **Multi-reader annotation is the normal case here, not the exception.** RIGA publishes six
  ophthalmologists per image and Chákṣu five; as rasters that is six PNGs per structure per image per
  size, and as polygons it is a few dozen rows. The catalogue's most valuable disc/cup property —
  that human disagreement can be measured — stops being expensive to store.
- **A polygon is what the expert actually drew.** Most of these datasets publish coordinates, and
  rasterising them to store them, then re-tracing them to use them, loses precision in both
  directions for no gain.
- **Comparing against a model is a subtraction.** With the nodes already in the frame the model
  predicts on, an evaluation is arithmetic rather than a coordinate transform, which is what keeps
  scoring hundreds of images cheap.

**A contour is traced or transformed exactly once, into the native frame. Every size is then scaled
from that.**

- **Native carries float coordinates.** `native/contours/<key>.csv` is the annotation of record and
  stores `x` and `y` as floats, because it is the thing every other size is computed from and
  rounding it would round every size with it.
- **Getting into the native frame** depends on what the dataset published:
  - **Coordinates** (PAPILA, GRAPE, RIGA): put them through the same crop and paste as the
    photograph — which for a coordinate is a **translation and nothing else**, because the native
    frame *is* the crop square at full resolution:

    ```
    x_native = x_raw - crop_x0
    y_native = y_raw - crop_y0
    ```

    Exact, and reversible. Nodes may come out negative or beyond `crop_side`; see the last rule in
    this section.
  - **Rasters** (REFUGE, G1020, HRF-Seg+): trace the native-resolution mask once — largest external
    component, Douglas-Peucker at **0.001 of the contour's own perimeter**, which gives about 45
    nodes for an optic disc, the range a hand-drawn outline occupies. Record the tracing's fidelity
    (an IoU against the mask it came from) in the row's `notes` rather than assuming it was faithful.
- **Getting from native to a size is a scale, and only a scale.** The native canvas is `crop_side`
  pixels across and the sized one is `size`, so every node is `native × size / crop_side`, rounded to
  integers. The crop is already in the native coordinates and is not applied again; `native_width`
  and `native_height` play no part. One multiplication, no re-tracing, no second code path. On a
  2576-pixel photograph the rounding costs at most half a pixel and far less once resampled — orders
  of magnitude below the distance between two experts on the same structure.

Scaling rather than re-tracing at each size is deliberate, and it is what makes section 11 possible:
a size added a year later, from `native/` alone, is **bit-identical** to the same size built on the
first run. Re-tracing would need the original raster — which is in `raw/`, which is deleted by
default — so the two routes would silently produce different polygons.

**Coordinates that fall outside the frame are kept, not clipped.** A disc near the edge can have nodes
in the padding; clipping them silently changes the shape. A consumer that needs a clipped polygon can
clip it.

## 11. Adding a size to an existing store

Sizes are not decided once. A new model enters the catalogue with a grid nothing was built at, a
comparison needs an intermediate size to separate resampling effects from model effects, or a run at
2048 is wanted to check what the downsizing cost. **None of that may require the download again** —
several of these datasets are behind a form, an account or a signed agreement, and some of those
routes will not exist in five years.

```bash
uv run python -m datasets.hrf --sizes 512,1024        # first build
uv run python -m datasets.hrf --sizes 512,1024,2048   # later: builds 2048 only, from native/
```

The rule that makes this work:

- **`native/` must be sufficient to build any future size**, on its own, with no network and no
  archive. That is the reason it is never optional (section 2) and the reason a contour is traced
  once into the native frame and scaled thereafter (section 10). A fetcher that needs `raw/` to add a
  size has a bug.
- **Missing sizes are built; existing sizes are left alone.** `--sizes` names the sizes that should
  exist, not the sizes to rebuild. A size already present and complete is skipped, so the command is
  safe to repeat and cheap to extend.
- **No download, no archive, no checksum check** on this path — there is nothing to verify, and a
  fetcher must not reach for the network when `native/` can answer.
- **`build.json` is updated, not replaced:** `sizes` gains the new entry, `built_at` is refreshed,
  and `sources` and `partial` keep their existing values, because nothing about where the data came
  from has changed.
- **A `builder_version` mismatch blocks it.** When the crop, paste or resample rules have changed
  since `native/` was built, deriving a new size from it would mix two conventions in one store.
  Refuse, and say that a `--force` rebuild from the archive is needed.
- **`--force` is the other path entirely**: it re-downloads and rebuilds everything, including
  `native/`. Use it when the rules changed or the store is suspect — not to add a size.

Removing a size is a directory deletion plus an edit to `build.json`; no fetcher option does it,
because nothing is at risk of being got wrong.

## 12. Resampling

Resampling is shared by every fetcher and therefore lives in `utils`, not in fetchers. Square frames
throughout, because every model in `docs/MODELS.md` resamples to a square grid, and doing it once
here means a consumer never resamples twice.

- **Images** with area-averaging when downsizing and Lanczos when upsizing; **masks** with
  **nearest-neighbour only** — a mask interpolated with anything else invents classes that were never
  annotated. A multi-class artery/vein map is resampled per class, never as an RGB image.
- **Never upsample silently.** When a requested size exceeds the crop, build it, but record a
  `notes` entry on the row and a warning in `build.json`: a Dice measured on an upsampled image is
  not comparable with one measured on a downsampled image, as `docs/datasets/drive.md` explains.

## 13. Rules that apply to every fetcher

- **13.1 Reference, never redistribute.** The store is a local cache. Nothing built here is published,
  mirrored or committed — that includes fixtures: tests use synthetic images, never real ones.
- **13.2 Honour the access route.** `⛔` datasets require `--archive`. Never embed credentials, never
  scrape a form, never mirror a credentialed archive.
- **13.3 Record provenance, not just data.** Anything a consumer would need in order to trust a number
  goes in the manifest, or — when it is a property of the build rather than of an image — in
  `build.json`. Put each fact in exactly one of them: a value kept in both will eventually disagree
  with itself.
- **13.4 Never make `raw/` a dependency of anything but the first build.** If adding a size, fixing
  a manifest column or rebuilding a contour needs the archive, the store is missing something it
  should have kept — several of these datasets cannot be downloaded again without a form, an account
  or an agreement, and one of them may not be obtainable at all in a few years.
- **13.5 Fail loudly, build partially only on request.** A missing required layer aborts. `--limit`
  marks the build partial. A store must never look complete when it is not.
- **13.6 Keep the catalogue and the code in step.** A fetcher whose behaviour contradicts its dataset
  page is a bug in one of them; fix both in the same commit. If building the dataset teaches you
  something the page does not say — a count that differs, a mask that disagrees with its
  documentation — that is a finding for the page's section 7, `Known defects`.
- **13.7 Standard colour fundus photographs only, for now.** Several datasets ship an
  **ultra-wide-field** subcollection alongside their ordinary photographs — DeepDRiD's third
  sub-challenge, REYIA's AV-WIDE subset, [MSHF](../../docs/datasets/mshf.md)'s 500 Optos mosaics —
  and one, [WIDE](../../docs/datasets/wide.md), is ultra-wide-field throughout. A fetcher **skips
  those subcollections** and builds the standard photographs. They are a different
  instrument: a 200° frame beside a 45° one makes every measurement in the store mean two things at
  once, and the crop and resolution rules in sections 8 and 9 were written for the narrow field. This
  is a deferral, not a judgement — when the atlas has somewhere honest to put them, they get built.
  Until then a fetcher that skips one **says so**: a warning on the console, the same warning in
  `build.json`, and a line in the page's *How to fetch* naming what was left in the archive. A
  silently smaller store is how someone concludes a dataset is smaller than it is. A dataset that is
  ultra-wide-field **throughout** has no fetcher at all yet, rather than one that builds nothing.

- **13.8 Read an archive where it lies when unpacking it would cost more than it saves.** Chakshu's
  per-expert masks are uncompressed TIFFs: 70 GB extracted against 11 GB in the archive, and every
  one is read once and turned into a polygon. A source can declare that it stays packed, and the
  fetcher addresses its members directly. The same goes for an archive holding a copy of its own
  photographs, as FQS does at a second size.

- **13.9 Index what the archive contains; never compose a path and trust it.** Chakshu's own
  capitalisation varies between experts — one's folder is `Bosch/cup`, the next's `Bosch/Cup` — and
  its decision files name photographs with an extension the photographs do not have. A fetcher that
  builds the path it expects finds nothing for some readers and reports a dataset with fewer
  annotators than it has, without erroring. List what is there, key it on something stable, and let
  a missing entry be visible.

- **13.10 Every file starts with the two-line `ABOUTME:` comment** the repository requires, and
  functions carry the docstring style of the surrounding code.
