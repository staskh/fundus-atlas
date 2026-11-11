# Biomarkers on real segmentations — how it is run

**What this benchmark does, in one paragraph.** It takes photographs on which an expert drew every
artery and vein, and computes the same biomarkers twice on each: once from the **expert's drawing**
and once from **a segmentation model's** artery/vein map of the same photograph. Everything else is
held fixed: the same biomarker program, the same optic disc, the same field of view and the same
microns-per-pixel scale. Any difference between the two numbers therefore comes from the vessel map
alone. The question it answers is the one a Dice score cannot: **if a study replaced manual tracing
with this model, would the biomarker still tell one eye from another?**

This page says how that is configured: what it asks, what takes part, what it excludes, how to run
it, and what every column of its evidence means. What *came out* is written up separately, in
[biomarker-real-results.md](biomarker-real-results.md).

**It is part generated and part written.** The tables and lists between the `generated` markers are
rendered from what the benchmark reports about itself and are refreshed by
`python -m benchmarks --benchmark biomarker-real --docs`, which measures nothing. The dataset table
is read from the stores on the machine that refreshed it. Everything else is written by hand and is
never overwritten.

## 1. What this benchmark asks

<!-- generated: asks -->
**If a study replaced manual vessel tracing with a segmentation model, would its biomarkers still tell one eye from another?** Every biomarker is computed twice on each photograph an expert annotated — once on the expert's artery/vein map and once on a model's — with the same program, the same optic disc and the same scale, so any difference is the map's. The intraclass correlation says whether the two numbers agree; the signal-to-noise ratio says whether the difference between eyes outweighs the error the model introduces.
<!-- /generated -->

This is the **paired comparison** that `PLAN-BENCHMARK.md` §1.2 calls the benchmark the atlas exists
for. The two benchmarks it stands between each answer half of it:

- the [artery/vein benchmark](av-docs.md) says how far a model's **map** is from the expert's, by
  overlap (Dice) and by centreline (clDice);
- the [synthetic biomarker benchmark](biomarker-synthetic-docs.md) says whether a biomarker
  **program** computes the quantity it claims, on drawings whose answer is known exactly.

Neither says whether a model's map is good enough for a **number** derived from it. A model can
score Dice 0.80 and still shift every arteriolar width by a pixel. That costs nothing in overlap and
moves a central retinal artery equivalent by a fifth. Equally, a model can miss a third of the
capillary-calibre vessels without moving the arteriovenous ratio at all. This benchmark measures
that directly.

### 1.1 The expert's map is the reference, not the truth

The value measured on the expert's drawing is treated as the **reference**. It is not the true
value of the eye: the same program run on a second expert's drawing would not reproduce it either.
None of these datasets publishes a second annotator, so that inter-reader spread cannot be measured
here. It is the most important thing this benchmark cannot say (section 9).

### 1.2 Two statistics, and what each answers

Every catalogued biomarker, for every pair of (segmentation model, dataset), gets:

- **ICC — the intraclass correlation coefficient.** It asks: of all the spread in this biomarker
  across photographs, how much is real difference between eyes rather than disagreement between the
  two maps? It runs from 0 (the two maps agree no better than chance) to 1 (they agree exactly).
  Two forms are reported (McGraw and Wong, 1996, for two "raters" — the expert's map and the
  model's map):
  - **ICC(A,1), absolute agreement.** It penalises a constant offset. This is the form that says
    whether the model's number can be **used in place of** the expert-map number.
  - **ICC(C,1), consistency.** It forgives a constant offset. This is the form that says whether
    the model **ranks** eyes the same way.

  A large gap between the two means the model is systematically biased but still orders eyes
  correctly. Conventional reading (Koo and Li, 2016): below 0.5 poor, 0.5–0.75 moderate, 0.75–0.9
  good, above 0.9 excellent.
- **Signal-to-noise ratio (SNR).** The **signal** is the standard deviation of the biomarker across
  photographs, measured on the expert's maps: how much eyes differ. The **noise** is the standard
  deviation of the paired difference, model minus expert: how much swapping the map moves the
  number, once any constant offset is set aside. An SNR of 3 means eyes differ three times as much
  as the segmentation error. An SNR below 1 means the model's error is larger than the difference
  the biomarker exists to detect.

Beside those are the **bias** (the mean of model minus expert, in the biomarker's own unit and as a
fraction of the expert mean) and the number of photographs both maps produced a value for. Coverage
is always shown beside agreement and never folded into it.

### 1.3 Why both, rather than one

ICC and SNR are related, but they come apart in exactly the case a reader needs warned about. A
biomarker with a large constant bias can have a high SNR, because the noise ignores offsets, and a
modest ICC(A,1), because absolute agreement does not. Read together, the two say whether the
problem is a correctable offset or a scatter nothing can correct.

## 2. What takes part

There are two kinds of subject, and the evidence is filed by the first.

### 2.1 The biomarker implementations

The programs that compute the numbers — the same seven adapters, measured as they ship, that the
synthetic benchmark checks against arithmetic. Their evidence is filed under
`results/biomarker-real/<implementation>/`.

<!-- generated: subjects -->
| Implementation | Pinned at | Columns it returns | Took part |
| --- | --- | --- | --- |
| [pvbm](../projects/pvbm.md) | `5edb79a` | 30 | yes |
| [ocular](../projects/ocularnet.md) | `34b1ecc`, `5edb79a` | 18 | yes |
| [automorph](../projects/automorph.md) | `9a953e5` | 18 | yes |
| [automorphalyzer](../projects/automorphalyzer.md) | `e68843e` | 54 | yes |
| [automorphclass](../projects/automorphclass.md) | `8f4d18f` | 18 | yes |
| [vascx](../projects/vascx.md) | `d0cde1c`, `e5823fe`, `ff47bfb`, `ec1ca00` | 20 | yes |
| [fundus-biomarkers](../projects/fundus-biomarkers.md) | `348da1b` | 633 | yes |
<!-- /generated -->

### 2.2 The segmentation models

The maps they are measured on. These are **not run here**. The [artery/vein benchmark](av-docs.md)
already drew them and kept them under `.atlas_runs/av/<model>/<dataset>/` (`build-benchmark` §6.1),
and this benchmark reads those kept masks. Before reading, it recomputes each model's **drawing
fingerprint** and compares it with the one kept beside the masks. Where the two differ, the masks
describe a model that no longer exists. That model is then not measured, and the warning says to
run the artery/vein benchmark first.

<!-- generated: segmenters -->
- [vascx-artery-vein](../models/vascx-artery-vein.md)
- [ocularnet](../models/ocularnet.md)
- [lunet](../models/lunet.md)
- [automorph-artery-vein](../models/automorph-artery-vein.md)
- [bf-net](../models/bf-net.md)
<!-- /generated -->

`segan-vessel` does not take part: it draws vessels without separating arteries from veins, and
every implementation here needs both classes.

## 3. The datasets

<!-- generated: material -->
| Dataset | Photographs | With a scale | Excluded, and why | Available |
| --- | --- | --- | --- | --- |
| [hrf](../datasets/hrf.md) | 45 | 45 | none | yes |
| [fundus-avseg](../datasets/fundus-avseg.md) | 100 | 100 | none | yes |
| [avrdb](../datasets/avrdb.md) | 99 | 99 | 1 no optic disc estimate | yes |
| [reyia](../datasets/reyia.md) | 554 | 486 | 4 no artery and vein annotation; 5 no optic disc estimate | yes |
| [rav](../datasets/rav.md) | 198 | 155 | 8 no optic disc estimate | yes |
<!-- /generated -->

**Two artery/vein datasets are left out on purpose.**

- **FIVES** annotates vessels and neither class.
- **AV-WIDE** photographs a 200° ultra-wide field. Every zone a calibre is measured in is defined in
  optic disc radii on a 45° photograph, and no microns-per-pixel scale exists for the instrument, so
  a number measured on it relates to none measured on the others.

**REYIA is a compilation**, and its subsets come from different cameras and, for OCULARNet, carry
different contamination marks. The analysis breaks it down by subset wherever that changes a
reading.

## 4. What is excluded, and by which rule

<!-- generated: exclusions -->
- **Below the size floor** — a photograph whose field of view is under 512 pixels, measured on the field's own size rather than the frame's
- **A finding recorded against the image** — anything in `src/datasets/exclusions/`, so that a finding survives deleting and rebuilding a store
- **No artery and vein annotation** — a photograph without both an artery and a vein map; every implementation here needs both
- **A finding condemns its artery or vein map** — an artery or vein map `src/datasets/exclusions/` records as wrong. Unlike the artery/vein benchmark the photograph goes, not the map: a biomarker needs both
- **No optic disc estimate** — a photograph the SegFormer disc model found no disc on, in `results/disc_estimation/`. Every implementation measures in zones counted in disc radii, and handing the two maps different discs would measure the discs
- **Excluded whole** — a dataset whose images are crops rather than photographs. No size floor catches that, because a crop can be large
<!-- /generated -->

**A photograph with no scale is kept.** Its scale-free biomarkers — the tortuosities, the fractal
dimensions, the ratios — are measured and compared as on any other. A biomarker carrying a length
is converted to microns before it is compared, so on such a photograph it is left out of the
agreement statistics, and the count of photographs beside each statistic shows it.

## 5. How to run it

<!-- generated: running -->
```bash
python -m benchmarks --benchmark biomarker-real --workers 15
python -m benchmarks --benchmark biomarker-real --model vascx --dataset hrf
python -m benchmarks --benchmark biomarker-real --max-samples 10
python -m benchmarks --benchmark biomarker-real --docs
```

| Flag | What it does |
| --- | --- |
| `--model` | one implementation, or several separated by commas |
| `--dataset` | one dataset, or several separated by commas |
| `--workers` | how many processes measure at once; 15 on this machine by default, one fewer than its cores |
| `--max-samples` | measure only the first N photographs of each dataset, for development; a sampled result says it is not complete, and a later run finishes it |
| `--random-samples` | choose those photographs at random rather than first |
| `--seed` | the seed a random sample uses |
| `--data-root` | read the stores from somewhere other than `.atlas_data/` |
| `--force` | discard what is stored and measure it all again |
| `--no-report` | skip refreshing `docs/BENCHMARKS.md` after the run |
| `--config` | print what this benchmark reports about itself, as JSON, measuring nothing |
| `--docs` | refresh this page from that JSON, measuring nothing |
<!-- /generated -->

**It is slow, and the `--workers` flag is how it is made tolerable.** On a photograph 2,200 pixels
across, one pass of all seven programs over one pair of masks takes about two and a half minutes on
one core. PVBM alone takes a minute, and fundus-biomarkers and AutoMorphalyzer half a minute each.
Six maps per photograph and about a thousand photographs make a full run several hours on sixteen
cores. Results are written every 50 measurements, so an interrupted run is finished rather than
restarted.

## 6. What each column of the evidence means

<!-- generated: columns -->
`results/biomarker-real/<implementation>/<dataset>.csv` holds one row per map of a photograph:

| Column | Meaning |
| --- | --- |
| `key` | the photograph, by the store's own key |
| `subset` | the part of the dataset it came from — a camera, or for REYIA the source collection |
| `split` | the split the dataset assigned it, where it assigned one |
| `source` | whose artery/vein map was measured: `expert` for the dataset's own annotation, else the segmentation model's slug |
| `drawing` | the drawing fingerprint of the model's kept masks (`build-benchmark` §6.2); empty for the expert's map, whose store version is in the result's fingerprint |
| `um_per_px` | the microns per pixel from the store's manifest; empty where none was published or inferred |
| `disc_x` | the optic disc centre's column in the crop, from `results/disc_estimation/` |
| `disc_y` | its row |
| `disc_r` | its equivalent radius, in pixels — the one disc every map of this photograph is measured with |
| `outcome` | `measured` if any number came back, else `failed`; `note` says what fell over |
| `seconds` | how long the implementation took over this one map, on one core |
| `note` | what the implementation complained about or failed with |
| `said_<key>` | what the implementation returned, under **its own** column name and in its own unit — pixels for a length, as the adapter declares. The catalogued name and the conversion to microns are applied in the agreement tables, never here |
<!-- /generated -->

The agreement statistics are written beside the evidence, one table per dataset and one pooled over
all of them:

<!-- generated: agreement_columns -->
`results/biomarker-real/<implementation>/agreement/<dataset>.csv and `pooled.csv`` hold one row per segmentation model and column:

| Column | Meaning |
| --- | --- |
| `model` | the segmentation model whose map was measured against the expert's |
| `column` | the implementation's own name for the number |
| `name` | the catalogued biomarker it answers to, from the adapter's naming table; empty where the catalogue has none |
| `unit` | the unit the statistics are in: the catalogued unit where there is a name — lengths in microns — and the implementation's own otherwise |
| `contamination` | whether this model trained on this dataset, from `contamination.py`; a dataset whose subsets differ is `mixed` |
| `n` | photographs both maps produced a value for — every statistic is over these |
| `expert_only` | photographs the expert's map produced a value for and the model's did not |
| `model_only` | photographs the model's map produced a value for and the expert's did not |
| `expert_mean` | the mean on the expert's maps |
| `expert_sd` | the standard deviation across photographs on the expert's maps — the signal |
| `model_mean` | the mean on the model's maps |
| `bias` | the mean of model minus expert, in the unit |
| `relative_bias` | that bias as a fraction of the expert mean |
| `sd_difference` | the standard deviation of model minus expert — the noise |
| `icc_agreement` | ICC(A,1): two-way, absolute agreement, one measurement |
| `icc_consistency` | ICC(C,1): two-way, consistency, one measurement — forgives a constant offset |
| `snr` | signal over noise: `expert_sd / sd_difference` |
<!-- /generated -->

**Pooled means pooled on the photographs**, not averaged over datasets. Pooling widens the signal:
eyes from five cohorts and nine cameras differ more than eyes from one, so a pooled ICC is higher
than most per-dataset ones. The per-dataset tables are the primary evidence. The pooled one answers
how a multi-cohort study would fare.

## 7. What a re-run repeats, and what it does not

<!-- generated: fingerprint -->
A stored result is kept only while everything it depends on is unchanged. This benchmark fingerprints:

- this benchmark's name, `VERSION` and size floor
- the facts each implementation declares that bear on its numbers: slug, needs, keys, units, recursion, upstream
- the pinned commit of the implementation's code and the content of every patch applied to it, as its declared `upstream` records them
- the store's slug and builder version, which pins the expert's maps and the field of view
- the fingerprint of the disc estimate in `results/disc_estimation/<dataset>.json`
- **per row**, the drawing fingerprint of the model's masks kept by the `av` benchmark. A model redrawn there has its rows here measured again, and only its rows

A fingerprint that differs means the stored result describes something that no longer exists, and it is measured again from nothing. **How much was done is not part of it**, because that does not change what any map of a photograph scored: a complete result is never re-run, and a partial one is finished rather than restarted.
<!-- /generated -->

## 8. The counts every result carries

<!-- generated: counts -->
| Count | What it answers |
| --- | --- |
| `processed` | how many photographs the expert's map has been measured on |
| `total` | how many the benchmark would ask about, after the exclusions |
| `excluded` | how many those exclusions removed, by reason |
| `complete` | whether every map of every photograph has been measured |
| `maps` | how many maps were measured: the expert's and each model's, per photograph |
| `failed` | how many of those returned nothing at all |
| `not_measured` | the segmentation models declared and not read, with the reason |
| `seconds_per_photograph` | how long the implementation took over every map of one photograph, on one core — not part of the fingerprint |
<!-- /generated -->

## 9. What this benchmark does not do

- **It does not measure the reference's own noise.** The expert's map is one person's drawing.
  Where a model disagrees with it by about as much as a second expert would, the model has matched
  the reference rather than failed it. No dataset here publishes a second reader, so that ceiling
  is unknown. A dataset that did would add the most informative row this benchmark could have.
- **It does not say a program is right.** Two maps agreeing under one program says the program is
  stable to the change of map. Whether it computes what it claims is the synthetic benchmark's
  question.
- **It does not select.** No model or program passes or fails. The results page may recommend, for
  a named question, per `report-benchmark` §5.
- **It does not test anything anchored to the fovea.** No fovea is located for these photographs,
  so VascX's fovea-dependent measurements come back empty, as they should.
- **It does not test the disc estimate.** Every map of a photograph is measured with one disc, so a
  wrong disc moves both numbers alike and is invisible here. The [disc benchmark](disc-docs.md)
  measures that.
