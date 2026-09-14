# Benchmarks: the plan

What we decided and why, before any of it is built. Sections marked **Decided** are settled;
**Open** needs Stas's call. Nothing here is code.

The catalogues answer *what exists*. The benchmarks answer the question the README promises and no
catalogue can: **do two of these agree, measured on the same images, on the same terms?**

## 1. The three kinds of benchmark

**Decided.**

1. **Segmentation and prediction.** A model is given photographs; its output is compared against the
   dataset's own annotation.
2. **Biomarkers.** The main one is a **paired comparison**: the same biomarker computed on the
   dataset's ground-truth mask and on a model's predicted mask, over the same photographs. The
   ground-truth value is the reference, and the difference is what the segmentation costs the
   measurement. This is the benchmark the atlas exists for — a Dice of 0.9 says nothing about
   whether the tortuosity derived from that mask is usable.

   Two secondary comparisons sit beside it:
   - **against a value the dataset itself published** — [ORIGA](docs/datasets/origa.md)'s `ExpCDR`,
     [Chákṣu](docs/datasets/chaksu.md)'s per-expert cup-to-disc ratios. A human-recorded target,
     and the strongest kind available;
   - **between implementations**, on one mask. See section 6 on why this is available for only
     some biomarkers.
3. **Synthetic validation.** Shapes whose biomarker values are known from theory, used to test an
   implementation against arithmetic rather than against another implementation. Section 7.

## 2. What is benchmarked, and what is not

**Decided.**

| | Status |
| --- | --- |
| [AutoMorphalyzer](docs/projects/automorphalyzer.md), [AutoMorphClass](docs/projects/automorphclass.md) | **Benchmarked.** They carry AutoMorph's models, with their own corrections |
| [AutoMorph](docs/projects/automorph.md) itself | **Not benchmarked** — superseded for our purposes by the two children above |
| [PVBM](docs/projects/pvbm.md), [VascX](docs/projects/vascx.md), [OCULARNet](docs/projects/ocularnet.md), [Fundus Image Toolbox](docs/models/fit-quality.md) models | **Benchmarked** |
| [retipy](docs/projects/retipy.md) | **Later**, low priority |
| [ARIA](docs/projects/aria.md) | **Not benchmarked** — MATLAB, and not worth the trouble |

Excluding the AutoMorph pipeline does not exclude its models: SEGAN, BF-Net and the lwnet-derived
disc/cup model are all reached through the two children.
[AutoMorph's own quality grader](docs/models/automorph-quality-grader.md) is reached from neither —
AutoMorphalyzer replaced it with QuickQual — so it is **benchmarked as a standalone model**, run
from the AutoMorph repository without the pipeline around it. It is a model like any other; only the
pipeline is out of scope.

**The seven built stores are a beginning, not the set.** Datasets are fetched as a benchmark needs
them; every benchmark names the datasets it wants, and the ones not yet built are a work item rather
than a limitation. The same goes for models: **adding one must mean adding one file**, which is what
section 9 is designed around.

## 3. What a benchmark is run on

**Decided.**

The unit is **(dataset, subset, split)**, not the dataset:

- **Contamination is per split.** Where a model trained on a dataset's training half, that half and
  the test half are reported as if they were separate datasets.
- **Cameras are not interchangeable.** [Chákṣu](docs/datasets/chaksu.md) is three cameras, one an
  ellipse-fielded handheld; [MSHF](docs/datasets/mshf.md) is six groups. One number over a mixed
  dataset hides what a map should show.
- The store already carries both columns, so the unit needs no new bookkeeping.

Two exclusions apply, and they catch different things.

**A size floor: photographs whose field is under 512 pixels are excluded**, measured on `crop_side`
— the field's own size in the store, not the frame.

**A crop rule: a dataset whose images are crops rather than whole photographs is excluded whole.**
Measuring pixels on a crop of a resized photograph relates to nothing, and no floor catches it,
because a crop can be large. The evidence is in the manifest: the share of rows where no field
boundary could be found at all. It is declared per dataset rather than inferred per image, because
one image whose retina fills the frame is ordinary and a dataset where that is true of every image
is not.

Against what is built today:

| Store | Excluded | By which rule |
| --- | --- | --- |
| [RIGA](docs/datasets/riga.md) | **all 744** | the crop rule — **744 of 744** rows have no findable field boundary. Its 800-pixel images clear the floor easily; they are still crops |
| [MSHF](docs/datasets/mshf.md) | 229 of 802 | the floor — the DR-XJU thumbnails at 412×310. Six of the larger DR-XJU images clear 512 and stay. Two MSHF rows have no findable field, which is 0.2% and ordinary, not a crop dataset |
| DeepDRiD, FQS, Chákṣu, FIVES, GRAPE | none | — |

RIGA going is consistent rather than awkward — its images were already disqualified for anything
measured in pixels. It does mean **the six-reader disc/cup dataset is unavailable**, and Chákṣu's
five readers become the human ceiling instead.

**Exclusions recorded in `src/datasets/exclusions/` are applied too**, so a finding like Chákṣu's
three broken expert masks is automatically out of every score.

## 4. In-sample and out-of-sample

**Decided.** Every result carries one of four marks:

| Mark | Meaning |
| --- | --- |
| `out-of-sample` | The model's published training data does not include this dataset |
| `in-sample` | This dataset **and this split** were trained on |
| `in-sample-unclear-split` | The dataset was trained on, the split not stated, so the whole dataset counts as in-sample |
| `unknown` | The model's training data could not be established |

`unknown` is never merged with `out-of-sample`. The marks come from the model pages' section 6; a
model whose page does not name its training data cannot be marked, which is a reason to keep the
catalogue current rather than to guess.

## 5. The benchmarks, in order

**Decided.**

1. **Quality.** First because it needs no mask, four of the seven stores already carry quality
   labels — [DeepDRiD](docs/datasets/deepdrid.md), [FQS](docs/datasets/fqs.md),
   [MSHF](docs/datasets/mshf.md), [FIVES](docs/datasets/fives.md) — and the models are small.
   [EyeQ](docs/datasets/eyeq.md) and [DRIMDB](docs/datasets/drimdb.md) are fetched for it.
2. **Disc and cup: segmentation and biomarkers together**, as one benchmark, because the biomarkers
   are arithmetic on the same contours. Datasets: [Chákṣu](docs/datasets/chaksu.md),
   [GRAPE](docs/datasets/grape.md), and [ORIGA](docs/datasets/origa.md) once its archive arrives —
   ORIGA being the one with a published cup-to-disc ratio to check against.
3. **Arteries and veins: segmentation — artery/vein models only.** Vessel-only models are **not
   benchmarked for now** and are kept for later; an artery/vein model already produces a vessel mask
   as the union of its classes, so the question "how good are the vessels" is answered without them.
   Each A/V model is scored three ways on the same output:
   - **arteries** against the annotation's arteries,
   - **veins** against its veins,
   - **A+V**, both classes merged on each side, which is the vessel score.

   Three numbers, because a model can find the vessels and colour them wrongly, and one number
   cannot show that. None of the seven stores carries A/V, so this benchmark needs datasets fetched
   first: HRF-AV, LES-AV, RITE, IOSTAR, Leuven-Haifa and their kin.
4. **Arteries and veins: biomarkers**, separately from the segmentation, since the interesting
   result is the paired one — the same calibre, tortuosity and fractal dimension computed on the
   annotation and on each model's mask.

## 6. What is measured

**Decided, metrics accepted.**

| Level | Metrics |
| --- | --- |
| A+V — the two classes merged, which is the vessel score | Dice; **clDice** alongside, since Dice is dominated by thick vessels while every width and tortuosity figure comes from the centreline |
| Arteries, and veins, separately | Dice per class, plus the **swap rate**: the share of correctly-found vessel pixels given the wrong class |
| Disc and cup | Dice per structure; **centre offset** in pixels; **equivalent radius error**; and the **cup-to-disc ratio error**, which is what anyone actually uses |
| Quality | **Coverage first** — see below — then accuracy, ROC AUC and Cohen's κ on what was graded |
| Landmarks | Distance in pixels **and in disc diameters**, the latter being the only camera-independent form |

### 6.1 A model may decline, and that counts

Not every model answers every photograph. AutoMorph's grader declines images it judges ungradeable,
and a model that crashes on an input has also failed to answer. So **every prediction has one of
three outcomes** — `graded` with a value, `declined` by the model itself, or `failed` — and the
first number reported for any model is its **coverage**: the share of the evaluation unit it was
willing to answer at all.

Coverage is reported beside accuracy and **never folded into it**. A grader that answers the easy
60% of a dataset and is right about all of them is not better than one that answers everything and
is right about 85%, and a table that prints only accuracy makes the first look better than the
second. Declining is also not always wrong — refusing an ungradeable photograph is the job — which
is why the two numbers are reported together and neither is a score on its own. A declined
photograph is excluded from the accuracy metrics and counted in coverage; a failure is counted
separately again, because a crash is our problem or the model's, not a judgement about the image.

**Biomarker comparison between implementations is available for only some biomarkers, and the plan
must not pretend otherwise.** The atlas has already documented the reason: "tortuosity" names at
least eight different quantities — Hart's τ1 to τ7 and Grisan's density are different formulas, not
different code for one formula. So the comparison table declares, per biomarker, whether two
implementations compute *the same defined quantity*; where they do not, they appear in the same
table and are never subtracted from one another.

**Where the score is computed: the annotation's own frame** — the store's `native/`. The ground
truth is the one thing that must not be altered to make a comparison convenient. Every result
records the model's own grid beside the score, since a model working at 512 against a 2048-pixel
annotation is handicapped in a way the number alone does not show.

### 6.2 Resampling: the answer to "which approach?"

Three rules, in order of preference:

1. **If the model emits probabilities, upsample the probability map** to native — **bilinear** — and
   threshold or take the argmax **at native**. This is the fairest to the model: it recovers
   boundary detail that a coarse binary mask has already thrown away, and it is roughly what the
   model would have produced on a finer grid. Bilinear rather than bicubic, because bicubic
   overshoots past 0 and 1 and the overshoot lands exactly at the boundary the score turns on.
2. **If only a binary or label mask is available, nearest neighbour.** Blocky, and honest — no class
   is invented between two others.
3. **Never interpolate label indices.** For a multi-class A/V map, resample per class (one-hot or
   per-class probability) and take the argmax at native; interpolating the integers 0, 1, 2 invents
   a "1.4" that means nothing.

Which path was taken is recorded per run, because it moves the score.

**On the CPU cost**, which Stas asked to check: upsampling a 512² probability map to 2048² is a few
milliseconds, against seconds for the forward pass — call it under 1% of a run, and it will be
measured on the first benchmark rather than assumed. The real cost of scoring at native is memory
on the largest photographs (Chákṣu's Remidio is 2448×3264), not time.

## 7. Synthetic validation of biomarkers

**Decided — new, and it belongs before the dataset benchmarks rather than after.**

Many biomarker definitions are ambiguous and many implementations are undocumented, so comparing two
of them tells you they differ without telling you which is right. Shapes with **known** values fix
that: a benchmark against arithmetic rather than against another program.

The generator produces vessel masks and disc coordinates where the answer is derivable:

| Shape | Known value |
| --- | --- |
| A straight segment | Tortuosity index exactly 1; curvature 0 |
| A circular arc of radius r | Constant curvature 1/r; arc-to-chord ratio in closed form |
| A sinusoid of known amplitude and wavelength | Arc length, total curvature and squared-curvature integrals in closed form |
| A vessel of constant width w | Calibre exactly w, at every method |
| A symmetric bifurcation of known angle | Branching angle exactly that angle |
| A disc and cup as concentric circles | Cup-to-disc ratio exactly the radius ratio |

What this catches that no real dataset can: a factor-of-two in a curvature formula, a
centreline extractor that counts a pixel chain rather than arc length, an off-by-one in a
Douglas-Peucker step, a tortuosity that changes when a vessel is rotated by 45°. The atlas's
[tortuosity page](docs/biomarkers/tortuosity.md) already records defects of exactly this shape found
by reading code; synthetic shapes turn reading into measuring.

These fixtures are **ours**, small, and committed — they are not a dataset and redistribute nothing.

## 8. How third-party code is obtained and run

**Decided, per Stas's acceptance.**

- **Pip-installable upstreams are installed, not cloned**, at an **exact pinned version** — PVBM and
  the Fundus Image Toolbox today. A clone happens only if we need to patch.
- **Everything else is fetched by pinned clone**, the same mechanism the datasets use
  (`utils/archives.GitSource`: sparse clone at a pinned commit, provenance recorded), into a
  git-ignored `.atlas_code/<slug>/`.
- Nothing third-party is committed. `CLAUDE.md` §2.1 forbids it, and half of these could not be
  redistributed anyway: OCULAR, SuperRetina and the MIDL24 vessel weights state **no licence at
  all**; VascX's weights are AGPL-3.0.

### 8.1 One environment, and what that costs

**Decided: a single environment for everything**, with upstreams patched into compatibility where
they insist on old APIs. The alternative — one environment per upstream — is more robust and much
more machinery, and this atlas would rather patch in the open than hide the incompatibility in an
environment file.

The honest risk: one of these may need a framework version that genuinely cannot coexist with the
others. If that happens the model is recorded as **not benchmarkable in the shared environment**,
with what it needs written down, rather than the environment being quietly forked.

### 8.2 The dot in `.atlas_code` — the answer to "does it break imports?"

**No, with one rule.** A leading dot is nothing to Python's import machinery: any directory on
`sys.path` can be imported from, hidden or not. What a dot *cannot* be is part of a **package name**,
so `import .atlas_code.automorph` is impossible — the directory has to be **added to `sys.path`**
and the upstream imported by its own module name:

```
sys.path.insert(0, ".atlas_code/automorph")   # then: import automorph's own modules
```

That is the normal pattern for a checkout, and it has a bonus: hidden directories are skipped by
pytest collection, ruff and packaging, so third-party code never lands in our test run or our lint.
If the sys.path dance ever becomes tiresome, renaming to `atlas_code/` costs nothing and loses only
that bonus.

## 9. How our changes to their code are kept

**Decided: recommendations 1 and 2, and no forks in our git.**

1. **Pre- and post-processing goes in our adapter, not their code.** `src/models/<slug>.py` prepares
   the input and interprets the output, and calls their model. Our changes are then ordinary code of
   ours — reviewable, testable, no patch to rot.
2. **A change that must be inside their code is a patch file**, `src/models/patches/<slug>/NNN-*.patch`,
   applied after the pinned clone. Against a pinned commit it cannot rot, because the commit cannot
   move. Each patch's commit says what it fixes and why.
3. **No forks.** Forking OCULAR, SuperRetina or the MIDL24 weights would republish code nobody
   licensed us to republish, and forking VascX's AGPL weights pulls copyleft onto whatever we
   publish beside them.

**What the adapters will and will not have to do**, which is worth stating because the store work
already settled half of it: every photograph in a store is **already centred, squared and scaled** —
field of view cropped, square, available at native and at each built size. So no adapter needs to
crop or centre. What they *will* need is the per-model **illumination, colour and contrast**
preparation each upstream bakes into its own inference — CLAHE for the FR-UNet ensemble, the
contrast enhancement SuperRetina applies, whatever AutoMorph's children do — and getting that wrong
is the most common way a model underperforms its paper.

**Weights and retraining remain out of scope** under `CLAUDE.md` §2.2 and §2.3 until Stas says
otherwise. If it is ever wanted, the middle course is to allow fine-tuning as a documented finding —
"this model gains N Dice retrained on X" — publishing the recipe and the numbers but not the
weights.

## 10. Code structure

**Decided in shape; the detail is the first thing to build.**

```
src/
  datasets/             built: one fetcher per dataset → .atlas_data/<slug>/
  models/               ONE MODULE PER MODEL — adding a model is adding one file
    utils/              fetching upstreams, pinned installs, patch application, shared runner
    patches/<slug>/     patch files, where an upstream must be changed
  biomarkers/           one implementation or adapter per catalogued biomarker
    utils/
    synthetic/          the generators of section 7
  benchmarks/           one module per benchmark; the scorer; the report writer
    utils/
      loaders.py        the dataset loaders of section 10.1
tests/
  datasets/ models/ biomarkers/ benchmarks/

.atlas_data/            git-ignored — dataset stores
.atlas_code/            git-ignored — third-party clones at pinned commits
.atlas_runs/            git-ignored — predicted masks: large, and reproducible

results/                committed — per-image scores, the evidence behind every table
docs/
  BENCHMARKS.md         committed — summary tables, one row per model × evaluation unit
  benchmarks/<name>.md  committed — what each benchmark asks, how it ran, what it found
```

**One module per model** is the extensibility requirement made concrete: a model declares its
upstream, its weights, its input preparation and its output interpretation, and registers itself.
Nothing else in the tree changes when a model is added. The same holds for datasets — the fetchers
already work this way — and for biomarkers.

### 10.1 The loaders

**Decided: one extendable class per benchmark kind**, and new datasets need no loader code at all.

The stores make this possible: every one has the same manifest schema, the same layers, the same
contour format. So a loader reads `manifest.csv`, applies exclusions and the 1024 floor, filters to
an evaluation unit, and yields the photograph with the ground truth in the form that benchmark
needs:

| Loader | Yields |
| --- | --- |
| `QualityLoader` | photograph, the dataset's own grade, and the per-reader grades where `labels.csv` has them |
| `DiscCupLoader` | photograph, and the disc and cup contours per reader — plus the derived centre, radius and cup-to-disc ratio |
| `ArteryVeinLoader` | photograph, and the A/V map — as two classes, and as their union, which is the vessel ground truth |
| `VesselLoader` | photograph and a binary vessel mask, for datasets annotated that way. Written when vessel-only models come back into scope |

A base class holds what they share — the store, the unit, the exclusions, the size, the ordering —
and each subclass supplies only *what counts as ground truth here*. Adding a dataset means building
its store; the loaders already read it. Adding a **kind** of benchmark means one subclass.

## 11. What is recorded

**Decided.**

- **Predicted masks are not committed.** Large, and reproducible from the model, the store and the
  run record.
- **Per-image scores are committed.** A few megabytes, not reproducible without re-running
  everything, and they are the atlas's actual contribution — a summary table is a claim and the
  per-image scores are its evidence. CC BY 4.0, like the rest of the write-ups.
- **Every run writes a `run.json`**, the discipline a store's `build.json` already follows: model
  slug and pinned commit or pinned version, the sha256 of the weights actually loaded, the patches
  applied, the store's `builder_version`, the evaluation unit, the resampling path, the environment's
  versions, and the date. A score without that is an anecdote.

### 11.1 A re-run keeps what has already been measured

**Decided.** Datasets arrive as benchmarks need them, and a benchmark will be re-run many times —
after a new dataset is built, a model is added, a patch is written. Re-scoring everything each time
would make that unaffordable, so a run is **incremental by default**, on the same principle the
dataset stores already use.

Each (model, evaluation unit) pair is scored once and its scores are kept with a **fingerprint** of
everything that could change them:

- the model's pinned commit or version, and the sha256 of the weights actually loaded;
- the patches applied, by content;
- the store's `builder_version` and the unit's row count;
- the metric set and the resampling path;
- the benchmark's own version.

A re-run recomputes a pair only when its fingerprint differs; everything else is read from
`results/`. Adding a dataset therefore costs only the new dataset, and adding a model costs only
that model — while a changed patch or a rebuilt store correctly invalidates exactly what it touched.
`--force` recomputes regardless, and, as with the stores, the predicted masks are the expensive part
and are not what gets kept: the scores are.

The trap this design has to avoid is a stale score outliving the thing that produced it. That is
what the fingerprint is for, and why it covers the patches by content rather than by name.

## 12. Open questions

1. **Which datasets to fetch next**, in the order the benchmarks need them: EyeQ and DRIMDB for
   quality; REFUGE, PAPILA, Drishti-GS, G1020, RIM-ONE DL for disc and cup; HRF, RITE, LES-AV,
   IOSTAR, Leuven-Haifa for arteries and veins.
2. **ORIGA** still needs its archive by hand before the disc/cup benchmark can use its `ExpCDR`.
3. **Which A/V models exist to benchmark**, now that vessel-only models are deferred: BF-Net through
   AutoMorphClass and AutoMorphalyzer, VascX artery/vein, OCULARNet and OCULARNet-nano, LUNet. Worth
   confirming that list is the intended one before the datasets are fetched for it.

---

**Written:** 2026-09-14
