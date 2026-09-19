# AutoMorph artery/vein model

This is the model that decides which vessels are arteries and which are veins in AutoMorph and the
two pipelines derived from it — and therefore every artery-to-vein measurement they report, the
arteriovenous ratio among them. It is [BF-Net](bf-net.md)'s network retrained by AutoMorph's authors
on three artery/vein datasets at once, and shipped as eight independently trained copies whose
answers are averaged.

It is catalogued separately from BF-Net for the reason that separates any two sets of weights: the
training data is different and the ensemble size is different, so a score earned by one is not
evidence about the other. BF-Net's published weights saw one dataset and are one network;
these saw three and are eight. Citing BF-Net's paper as evidence for these masks would mean citing
measurements made with other weights on data these weights trained on.

## 1. Code reference

- **Repository:** the inference code and weights are distributed inside
  https://github.com/rmaphoh/AutoMorph, module `M2_Artery_vein`. The code is a copy of
  [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation), which is
  [BF-Net](bf-net.md)'s own repository, by the same first author.
- **Version described here:** AutoMorph commit `9a953e5e` (2025-06-21).
- **Most recent commit:** 2025-06 (of the host repository)
- **Training code included:** No, not in the host repository — it ships `test_outside.sh` and
  `test_outside.py` for inference only. Training code for the architecture is `train.py` in
  [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation); the configuration
  behind this particular retraining was not found, and the seed folders are dated `20210724`, more
  than a year before the BF-Net commit that publishes that script.
- **Language and how it runs:** Python with PyTorch, as the artery/vein stage of AutoMorph's
  `run.sh`. The stage's script is headed "This is SH file for LearningAIM", a name from the
  originating project.

## 2. License

- **Code:** stated as Apache-2.0, which is the host repository's only licence file. **The code in
  this module is a copy of a GPL-3.0 repository**, and no licence file accompanies it inside the
  module. The two cannot both govern; recorded as a defect in section 10.
- **Model weights:** No separate license stated; committed in the AutoMorph repository.

## 3. Major publications by the authors

- The weights are described as part of: Zhou Y, Wagner SK, Chia MA, Zhao A, Xu M, Struyven R,
  Alexander DC, Keane PA, et al. *AutoMorph: Automated Retinal Vascular Morphology Quantification
  Via a Deep Learning Pipeline.* Translational Vision Science & Technology 2022;11(7):12.
  [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)
- The architecture: Zhou Y, Xu M, Hu Y, Lin H, Jacob J, Keane PA, Alexander DC. *Learning to
  Address Intra-segment Misclassification in Retinal Imaging.* MICCAI 2021, pp. 482–492. DOI:
  [10.1007/978-3-030-87193-2_46](https://doi.org/10.1007/978-3-030-87193-2_46)

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** four, exclusive — background, artery, vein, and a fourth class the authors'
  own evaluation code calls *uncertainty*. **On the annotations these weights were trained on, that
  fourth class is the crossings**: where an artery passes over a vein, an annotator marks the
  pixels as belonging to both vessels, and a network emitting exclusive classes has to put them
  somewhere. This atlas measured it rather than assuming it — see section 11 — and reads an artery
  as the artery class plus that fourth class, which is what AutoMorph's own postprocessing does.
- **Input grid:** 720×720, square, with the aspect ratio ignored. AutoMorph's own pipeline hands it
  a photograph already cropped and resized by its preprocessing stage.
- **Output grid:** a four-class map at 720×720, argmaxed, then resampled to the original
  photograph's dimensions with **nearest-neighbour** interpolation before being saved.
- **Grid set in:** `--uniform=True` in `M2_Artery_vein/test_outside.sh`, which selects `(720, 720)`
  in `Define_image_size` in `M2_Artery_vein/scripts/utils.py`. Without that flag the same function
  has no branch for this module's `ALL-AV` dataset name and the script fails — see section 10.
- **Input expected:** a colour-fundus photograph, RGB. Nothing in the module crops to the field of
  view; the host pipeline does that upstream.
- **Preprocessing in the published code:** resize to 720², then **scale** each channel by the
  statistics of the photograph's own lit pixels — those with any red in them. The expression is
  `(image - mean) / 1.0 * std`, whose operator precedence multiplies by the standard deviation
  rather than dividing by it, so a low-contrast photograph is scaled towards zero rather than
  stretched. **Both** of the module's dataset classes carry the same expression, so the weights were
  trained through it and it is reproduced rather than corrected; it is recorded in section 10
  because it means the network's input is not standardised in the usual sense.

## 5. Architecture

- **Family:** GAN-based segmentation, BF-Net's binary-to-multi fusion. Two branch generators — one
  for arteries, one for veins — each emit a segmentation and a fusion map, and it is the **fusion**
  maps that condition a main generator alongside the photograph. A U-Net discriminator takes part in
  training only. `Generator_main` and `Generator_branch` in `scripts/model.py`, both with 32 filters
  and four output classes.
- **Parameters:** not stated. The three checkpoints of one seed are 35, 35 and 37 MB.
- **Single model or ensemble:** **ensemble of eight**, one per random seed, in folders named
  `20210724_ALL-AV_randomseed_28` through `_42`. Each seed is three checkpoints — the artery branch,
  the vein branch and the main generator — so the ensemble is twenty-four files. The seeds' softmax
  outputs are averaged, and their standard deviation is saved as an uncertainty map the pipeline
  publishes beside the mask.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE-AV](../datasets/rite.md) | Training | The dataset's own authors | No — the host repository restates no split for the combined set |
| [HRF-AV](../datasets/hrf.md) | Training | The dataset's own authors | No |
| [LES-AV](../datasets/les-av.md) | Training | The dataset's own authors | No |

The three are combined into a training set the repository calls `ALL-AV`, which is what the seed
folders are named for. **None of [DRIVE](../datasets/drive.md)/[RITE](../datasets/rite.md),
[HRF](../datasets/hrf.md) or [LES-AV](../datasets/les-av.md) can be used to benchmark these
weights**, and because no split is restated, a score on any part of those datasets is in-sample with
an unclear split rather than cleanly in or out.

[RLAD](rlad.md)'s authors go further and mark AutoMorph's artery/vein numbers in their own
comparison as affected by "data leakage during training" — their claim about this model, recorded on
their page rather than verified here.

## 7. Weights

- **Publicly available:** Yes, committed in the host repository.
- **Download URL:**
  https://github.com/rmaphoh/AutoMorph/tree/main/M2_Artery_vein/ALL-AV — eight seed folders, each
  with a `Discriminator_unet/` directory holding `CP_best_F1_A.pth` (the artery branch),
  `CP_best_F1_V.pth` (the vein branch) and `CP_best_F1_all.pth` (the main generator).
- **Format and size:** PyTorch state dictionaries, about 101 MB per seed and **808 MB for the
  ensemble** — the largest set of weights in this catalogue, and the reason a shallow clone of
  AutoMorph is not a small download.
- **Files in an ensemble:** twenty-four: three per seed, eight seeds.

## 8. Performance as reported by the authors

The AutoMorph paper reports artery/vein segmentation performance for this module. Those numbers are
in that paper and are not restated here, and the BF-Net paper's numbers do **not** apply to these
weights: they were measured with one seed trained on one dataset.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | The `M2_Artery_vein` module | These weights, eight-seed ensemble |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Artery/vein stage, unchanged from AutoMorph | The same weights, republished as a release asset |
| [AutoMorphClass](../projects/automorphclass.md) | `AV_classification.py` | The same weights, vendored into the package |

## 10. Known defects

- **The licences conflict.** GPL-3.0 code is redistributed inside an Apache-2.0 repository with no
  licence file of its own in the module (section 2). Anyone building on AutoMorph's artery/vein
  stage has to answer to the stricter of the two, and the repository does not say so.
- **The default grid crashes.** `--uniform` defaults to `False`, and `Define_image_size` has no
  branch for this module's own `ALL-AV` dataset name, so running `test_outside.py` without the flag
  the shipped shell script passes raises before inference starts. The failure looks like a broken
  install rather than a missing argument.
- **The input is scaled, not standardised** (section 4). `(image - mean) / 1.0 * std` multiplies by
  the standard deviation. It is consistent between training and inference, so it is not a bug that
  breaks these weights — but it means the network's sensitivity to a photograph's contrast is the
  opposite of what the code reads as, and anyone retraining from this code inherits it silently.
- **Specks are deleted from the mask, not from the probability.** The module removes connected
  components under thirty pixels from the argmaxed artery and vein classes — `remove_small_objects(…,
  30, connectivity=5)` — and its biomarker stage does it again at 912. A small vessel and a stray
  speck are indistinguishable to that rule.

## 11. Notes

- **The fourth class is the crossings, and this atlas measured that.** Scored against
  [HRF](../datasets/hrf.md)'s artery/vein annotation, the class matches this repository's own
  crossing layer pixel for pixel: 56,690 pixels on `09_dr`, with none left over and none of it in
  either single-vessel class. The authors' own evaluation calls it *uncertainty* and scores it as a
  class in its own right, while AutoMorph's biomarker stage folds it into both vessels — so the two
  halves of the same project read the same channel two ways. This atlas follows the latter, because
  it is what an annotator drew.
- **[RITE](../datasets/rite.md) also publishes vessels of uncertain type**, distinct from its
  crossings, and a four-class network trained on it has nowhere else to put them. On HRF, where
  there are none, the fourth class is crossings exactly; on the DRIVE-trained weights of
  [BF-Net](bf-net.md) it may carry both.
- **Eight seeds is not eight times the evidence.** They differ only in initialisation and in the
  order they saw the same three datasets, so their agreement says nothing about whether the answer
  is right — which is exactly what the published uncertainty map is and is not good for.
- **This model and [BF-Net](bf-net.md) are the same architecture at the same grid**, so a
  difference between their scores is a difference in training data and ensemble size, and nothing
  else.

---

**Links and license last checked:** 2026-09-18
