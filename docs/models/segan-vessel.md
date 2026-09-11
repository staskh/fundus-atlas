# SEGAN vessel segmenter

This is the network that produces the binary vessel mask in AutoMorph and its derivatives: one
class, vessel or not, with no artery-vein distinction. It is a generative-adversarial segmenter — a
generator proposes a vessel mask and a discriminator judges it, which pushes the generator toward
masks that look like human annotations rather than merely scoring well pixel by pixel.

It is easily confused with [BF-Net](bf-net.md), the artery-vein model that runs beside it in the
same pipelines. They are separate networks, trained on different datasets, and they can disagree
about whether a given vessel exists.

## 1. Code reference

- **Repository:** the inference code and weights are distributed inside
  https://github.com/rmaphoh/AutoMorph, module `M2_Vessel_seg`. The GAN backbone comes from the
  SEGAN method (section 3); no standalone repository for the original method was found.
- **Version described here:** AutoMorph commit `9a953e5e` (2025-06-21).
- **Most recent commit:** 2025-06 (of the host repository)
- **Training code included:** No usable training code was found. `test_outside_integrated.py`
  accepts a `--train_test_mode` argument whose default is `trainandtest`, but the file contains no
  training loop, so the flag appears vestigial. The related
  [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) repository publishes
  training code for artery/vein models only.
- **Language and how it runs:** Python with PyTorch, invoked by
  `M2_Vessel_seg/test_outside.sh`, whose header reads "This is sh file for SEGAN".

## 2. License

- **Code:** Apache-2.0, as part of the AutoMorph repository. The upstream SEGAN method has no
  located code repository, so no separate license applies to it.
- **Model weights:** No separate license stated; they are committed in the AutoMorph repository.

## 3. Major publications by the authors

- Zhou Y, Chen Z, Shen H, et al. *A refined equilibrium generative adversarial network for retinal
  vessel segmentation.* Neurocomputing 2021;437:118–130.
  [arXiv:1909.11936](https://arxiv.org/abs/1909.11936) — the SEGAN method used as the backbone.
- The weights described here were trained for, and are described in, the AutoMorph paper: Zhou Y,
  Wagner SK, Chia MA, et al. Translational Vision Science & Technology 2022;11(7):12.
  [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)

## 4. What it produces

- **Purpose:** `vessels`
- **Output classes:** one class — blood vessel against background. AutoMorph writes both a raw
  probability map and a thresholded binary mask.
- **Input grid:** 912×912. AutoMorph's preprocessing stage crops to the fundus bounds and resamples
  so the fundus diameter is 912 pixels, then the module resizes to a square 912×912 with aspect
  ratio ignored.
- **Output grid:** 912×912 probability and binary masks, each then resampled back to the original
  photograph's width and height and saved at both sizes.
- **Grid set in:** `Define_image_size` in `M2_Vessel_seg/utils.py` (`(912, 912)` when `--uniform`,
  which is what the shipped script passes); the diameter convention is `scale_list = [a*2/912 …]` in
  `M0_Preprocess/EyeQ_process_main.py`.
- **Input expected:** a preprocessed colour-fundus photograph from the pipeline's own cropping
  stage; AutoMorph works at a fixed internal size of 912 px.
- **Preprocessing in the published code:** cropping and resizing by the host pipeline, plus a
  `--pre_threshold` of 40.0 in the shipped command.

## 5. Architecture

- **Family:** GAN-based U-Net. The code defines a `Segmenter` generator (five downsampling and five
  upsampling stages, width set by `n_filters`) trained against a `Discriminator`; the shipped
  checkpoints are the generator, named `G_best_F1_epoch.pth`.
- **Parameters:** Unknown; the checkpoint is about 35 MB per seed.
- **Single model or ensemble:** ensemble of ten, one per random seed, averaged by the pipeline.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE](../datasets/drive.md) | Training | The dataset's own authors | Combined set named `ALL-SIX`; per-dataset split not restated in the repository |
| [STARE](../datasets/stare.md) | Training | The dataset's own authors | As above |
| [CHASE-DB1](../datasets/chase-db1.md) | Training | The dataset's own authors | As above |
| [HRF](../datasets/hrf.md) | Training | The dataset's own authors | As above |
| [IOSTAR](../datasets/iostar.md) | Training | The dataset's own authors | As above |
| [LES-AV](../datasets/les-av.md) | Training | The dataset's own authors | As above |

All six are therefore unavailable for a fair benchmark of these weights — which rules out most of
the public vessel-segmentation benchmarks in common use. An independent evaluation needs a dataset
outside that list, such as [FIVES](../datasets/fives.md).

## 7. Weights

- **Publicly available:** Yes, committed in the host repository.
- **Download URL:**
  https://github.com/rmaphoh/AutoMorph/tree/main/M2_Vessel_seg/Saved_model/train_on_ALL-SIX — ten
  folders named `20210630_uniform_thres40_ALL-SIX_savebest_randomseed_<n>`, each holding
  `G_best_F1_epoch.pth`.
- **Format and size:** PyTorch, about 35 MB per seed.
- **Files in an ensemble:** ten.

## 8. Performance as reported by the authors

Unknown for these specific weights as a standalone model. The SEGAN paper reports vessel
segmentation performance for the original method, and the AutoMorph paper reports the pipeline's
segmentation results; neither is restated here, because the numbers are not measured on the same
images and pooling them would mislead.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | The `M2_Vessel_seg` module | Trained by AutoMorph, ten-seed ensemble |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Binary vessel stage, unchanged | AutoMorph's weights via a release asset |
| [AutoMorphClass](../projects/automorphclass.md) | `Vessel_segmentation.py` at 912 px | AutoMorph's weights, vendored; `lightweight=True` uses one seed instead of the ensemble |

## 10. Known defects

None recorded for the model as of 2026-09-10 — an absence of findings, not a clean bill of health.
Note that the vessel masks this model produces are the input to the defective tortuosity code
described in [retipy.md](../projects/retipy.md) section 8.1; the defect is in the measurement, not
in this segmentation.

## 11. Notes

- **Running one seed is not running this model.** The published behaviour is the ten-seed ensemble.
  A single-seed run, as AutoMorphClass offers for speed, is a different and undocumented model.
- Its ancestry is shared with [BF-Net](bf-net.md), whose repository describes its own GAN backbone
  as a revision of this method. Shared ancestry is a reason to expect correlated errors between the
  binary and artery-vein masks, not independent ones.

---

**Links and license last checked:** 2026-09-10
