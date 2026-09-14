# Benchmarks: the plan

This file records what we decided and why, before any of it is built. It is a working document:
sections marked **Decided** are settled, sections marked **Open** need Stas's call, and nothing here
is code.

The catalogues answer *what exists*. The benchmarks answer the question the README promises and
nothing in the catalogue can: **do two of these actually agree, measured on the same images, on the
same terms?**

## 1. The two kinds of benchmark

**Decided.**

1. **Segmentation and prediction.** A model is given photographs and its output is compared against
   the dataset's own annotation. Vessel masks, artery/vein maps, disc and cup outlines, quality
   grades, landmark coordinates.
2. **Biomarker calculation.** A biomarker implementation is given a mask and its number is compared
   against something. There are three somethings, and they are not equally strong:
   - **against a value the dataset itself published** — [ORIGA](docs/datasets/origa.md)'s `ExpCDR`,
     [Chákṣu](docs/datasets/chaksu.md)'s per-expert cup-to-disc ratios. This is the only case with a
     human-recorded target, and it is the strongest thing available;
   - **against another implementation** of the same biomarker on the same mask — PVBM's tortuosity
     against AutoMorph's, on one set of vessels. This measures whether two papers reporting
     "tortuosity" report the same quantity, which is the atlas's original question;
   - **end to end**, biomarker on predicted masks rather than on the annotation, which measures the
     pipeline rather than the calculation and must be labelled as such.

Kind 2 is run on **ground-truth masks first**. A biomarker compared on predicted masks confounds two
errors, and we would not be able to say which one moved.

## 2. What a benchmark is run on

**Decided.**

The unit is **(dataset, subset, split)**, not the dataset. Three reasons, all of them already
visible in the stores built so far:

- **Contamination is per split.** [FIVES](docs/datasets/fives.md) publishes a 600/200 train/test
  division; a model trained on its training split can be scored honestly on its test split and not
  on the other. Per Stas: where the training half was used in training, the two halves are reported
  as if they were separate datasets.
- **Cameras are not interchangeable.** [Chákṣu](docs/datasets/chaksu.md) is three cameras, one of
  them an ellipse-fielded handheld; [MSHF](docs/datasets/mshf.md) is six groups, one of them
  thumbnails. A single number over a mixed dataset hides exactly the differences a map should show.
- **The store already carries both columns.** `subset` and `split` are in every manifest, so the
  unit needs no new bookkeeping.

Every result row therefore names the dataset, the subset, the split, and the model.

## 3. In-sample and out-of-sample

**Decided.**

Every result carries a contamination mark, from a fixed vocabulary:

| Mark | Meaning |
| --- | --- |
| `out-of-sample` | The model's published training data does not include this dataset |
| `in-sample` | This dataset **and this split** were trained on |
| `in-sample-unclear-split` | The dataset was trained on but the split was not stated, so the whole dataset is treated as in-sample |
| `unknown` | The model's training data could not be established |

`unknown` is not `out-of-sample`, and the two must never be merged in a table. The
[FR-UNet vessel ensemble](docs/models/frunet-fives.md) is the worked example: it trained on FIVES,
the wrapper does not say on which split, so every FIVES row for it reads
`in-sample-unclear-split` — and FIVES is the dataset it would otherwise be most natural to score it
on.

The marks come from the model pages' section 6, which is where each model's training data is already
recorded. **A model whose page does not name its training data cannot be marked**, which is a
reason to keep the catalogue current rather than a reason to guess.

## 4. What is measured

**Open — needs Stas's agreement on the metrics beyond Dice.**

Dice and F1 are the same number for a binary mask, so "Dice/F1" is one metric, not two. It does not
cover every purpose class, and the proposal is:

| Purpose class | Metric | Why |
| --- | --- | --- |
| `vessels` | Dice; **clDice** alongside | Dice is dominated by the thick vessels. clDice scores the centreline, which is what tortuosity and calibre are computed from |
| `artery/vein` | Dice per class, and the artery/vein confusion between them | A model can segment vessels well and colour them wrongly |
| `disc/cup` | Dice per structure; **and the cup-to-disc ratio's own error** | The ratio is what anyone uses; a 0.9 Dice on the cup can still move the ratio |
| `quality` | Accuracy, ROC AUC, and Cohen's κ against the dataset's grade | Not a mask; Dice is meaningless |
| `other` (landmarks) | Distance in pixels **and in disc diameters** | Pixels are not comparable between cameras |

**Where the score is computed.** In the annotation's own frame — the store's `native/` — with the
model's output resampled back to it by nearest neighbour. The reasoning: the ground truth is the one
thing that must not be altered to make a comparison convenient, and resampling it to a model's grid
would do exactly that. Every result records the model's own grid beside the score, since a model
working at 512 on a 2048-pixel annotation is handicapped in a way the number alone does not show.

## 5. How third-party code is obtained

**Open — this is question 1, and the recommendation follows.**

Nothing third-party is committed to this repository. `CLAUDE.md` §2.1 forbids vendoring their code,
and half the projects could not be redistributed anyway: OCULAR, SuperRetina and the MIDL24 vessel
weights state **no licence at all**, and VascX's weights are AGPL-3.0.

**Recommended: fetch by pinned clone, exactly as datasets are fetched.** `utils/archives.GitSource`
already does this — sparse clone at a pinned commit, provenance recorded — and it is built, tested
and proven on DeepDRiD. A model runner declares its upstream the way a dataset fetcher declares its
archive:

```
src/models/automorph.py     declares repo + commit + weights URL
.atlas_code/automorph/      the clone, git-ignored, addressed by pinned commit
```

Why not the alternatives:

- **Git submodules** put the pointer in the tree, which is tidy, but they are awkward in daily use
  (detached heads, `--recursive` clones) and give nothing the pinned clone does not.
- **`pip install git+…@commit`** is right *where the upstream is a package* — PVBM and the Fundus
  Image Toolbox are on PyPI, and for those a version pin is simpler and better than a clone. Most of
  the others are research repositories with no packaging, so this cannot be the general rule.

**The harder half of this question is not fetching, it is environments.** AutoMorph, VascX, retipy
and the toolbox do not agree about the version of anything, and ARIA is **MATLAB**, which no Python
environment will host. The proposal is one isolated environment per upstream, created by `uv` from
the upstream's own lockfile or requirements, and a runner that shells into it — with ARIA recorded
as needing MATLAB or Octave and left until we decide it earns the trouble.

## 6. How our changes to their code are kept

**Open — this is question 2.**

Three kinds of change, and they should be kept in three different ways:

1. **Pre- and post-processing — most of what we will change.** Cropping, resizing, normalisation,
   how a mask is thresholded, how an output is mapped back. **Recommended: do not touch their code
   at all.** Write our own adapter in `src/models/<slug>.py` that prepares the input and interprets
   the output, and call the upstream's model or inference function from it. Our changes then live in
   our git as ordinary code of ours, reviewable and testable, with no patch to rot.
2. **Changes that must be inside their code** — a bug in their inference that cannot be worked
   around from outside. **Recommended: a patch file**, `src/models/patches/<slug>/NNN-<what>.patch`,
   applied with `git apply` after the pinned clone. Small, reviewable, and it states exactly what we
   changed and why in the commit that adds it. A patch against a pinned commit cannot rot, because
   the commit cannot move. The atlas already has examples waiting: the
   [locator's un-undone centre crop](docs/models/fit-fovea-od.md) and
   [AutoMorph's tortuosity defects](docs/biomarkers/tortuosity.md).
3. **A fork on GitHub.** **Recommended against**, for a specific reason rather than taste: forking
   OCULAR, SuperRetina or the MIDL24 weights would republish code nobody licensed us to republish,
   and a fork of VascX's AGPL weights pulls copyleft onto whatever we publish beside it. Where an
   upstream is permissively licensed *and* we intend to offer the fix back, a fork and a pull
   request is the right thing — but it is the exception, and the patch stays in our tree either way
   so that the atlas's record of what it changed is complete.

**On updating weights — this one needs a decision from Stas, because the repository's own rules
currently forbid it.** `CLAUDE.md` §2.2 puts *training new networks* out of scope, and §2.3 forbids
redistributing model weights. Retraining a model for better results is training a new network, and
publishing the result is redistributing weights. There are three ways out and they are not equal:

- **Leave it out of scope.** Benchmarks measure models as their authors published them, which is the
  question a reader of this atlas is asking.
- **Amend `CLAUDE.md`** to allow retraining, and accept that the atlas then ships weights and owns
  the obligations that come with them — including AGPL on anything derived from VascX.
- **A middle course:** allow *fine-tuning experiments* as a documented finding — "this model gains
  N Dice when retrained on X" — with the weights **not** published, only the recipe and the numbers.

Recommendation: the middle course, and only after the first round of benchmarks exists. Fixing
pre-processing (item 1) already recovers a great deal, as the store work showed, and it does not
touch the scope rules at all.

## 7. Where things live

**Open — this is question 3. Proposed tree:**

```
src/
  datasets/            built: one fetcher per dataset, stores to .atlas_data/
  models/              one runner per catalogued model slug
    utils/             fetching upstreams, environments, running, output conventions
    patches/<slug>/    patch files, where their code must be changed
  biomarkers/          one implementation or adapter per catalogued biomarker
    utils/
  benchmarks/          benchmark definitions, the scorer, the report writer
    utils/
tests/
  datasets/ models/ biomarkers/ benchmarks/

.atlas_data/           git-ignored — the dataset stores (31 GB today)
.atlas_code/           git-ignored — third-party clones, each at its pinned commit
.atlas_runs/           git-ignored — predicted masks, which are large and reproducible

results/               committed — per-image scores as CSV, the evidence behind every table
docs/
  BENCHMARKS.md        committed — the summary tables, one row per model × evaluation unit
  benchmarks/<name>.md committed — what each benchmark asks, how it was run, what it found
```

The split between `.atlas_runs/` and `results/` is the important line. **Predicted masks are not
kept in git**: they are large, and they are reproducible from the model, the store and the run
record. **Per-image scores are kept in git**: a few megabytes, not reproducible without re-running
everything, and they are the atlas's actual contribution — a summary table is a claim, and the
per-image CSV is the evidence for it. They are CC BY 4.0 like the rest of the write-ups.

**Every run writes a `run.json`**, the same discipline as a store's `build.json`: model slug and
pinned commit, the sha256 of the weights actually loaded, the patches applied, the store's
`builder_version`, the evaluation unit, the environment's Python and framework versions, and the
date. A score without that is not a measurement, it is an anecdote.

## 8. What this depends on

- **The stores.** Seven datasets are built and verified. The benchmark reads them through
  `utils/manifest` and `utils/exclusions`, so a finding recorded as an exclusion is automatically
  out of every score.
- **The catalogues.** Contamination marks come from the model pages; the metrics come from the
  purpose classes; the biomarker definitions come from the biomarker pages. Where a page says
  `Unknown`, the benchmark says `unknown` too rather than filling it in.

## 9. Open questions for Stas

1. **Metrics beyond Dice** (section 4) — is clDice for vessels, the cup-to-disc error for disc/cup,
   and κ for quality the right set?
2. **Scoring frame** (section 4) — native, as proposed, or a common grid for everyone?
3. **Weights and retraining** (section 6) — leave out of scope, amend `CLAUDE.md`, or the middle
   course?
4. **ARIA** — it is MATLAB. Does it earn the trouble, or is it catalogued and not benchmarked?
5. **Which benchmark first?** The proposal is disc/cup on Chákṣu, RIGA and ORIGA: five and six
   readers give a human ceiling to compare models against, and ORIGA's published `ExpCDR` gives the
   biomarker side a target on the same photographs.

---

**Written:** 2026-09-14
