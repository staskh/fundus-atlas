# VascX artery/vein segmentation

Separates arteries from veins in a colour-fundus photograph. This is the model behind VascX's calibre, central retinal equivalent and artery-vein ratio biomarkers, and the one whose errors matter most to them, because an artery mislabelled as a vein moves both sides of that ratio.

It is one of five models released together as the VascX ensembles; each is catalogued separately.
The others are [vessels](vascx-vessels.md), [artery/vein](vascx-artery-vein.md),
[disc](vascx-disc.md), [fovea](vascx-fovea.md) and [quality](vascx-quality.md) — minus this one.

## 1. Code reference

- **Repository:** https://github.com/Eyened/retinalysis-vascx (inference and biomarkers); model
  execution lives in the companion package `retinalysis-inference`.
- **Version described here:** commit `d0cde1c7` (2026-08-07), tag `v0.2.0`; PyPI
  `retinalysis-vascx` 1.4.0.
- **Most recent commit:** 2026-08
- **Training code included:** No. No training script was found in the repository; the training
  procedure is described in the paper only, so this model can be run but not retrained.
- **Language and how it runs:** Python with PyTorch, as part of `vascx run-models`. This model can
  be replaced with `--av-model`, or by placing a file at `artery_vein/av_july24.pt` inside a directory given by
  `--model-dir` or the `VASCX_MODEL_DIR` environment variable.

## 2. License

- **Code:** Not stated — the repository has no LICENSE file and the PyPI metadata leaves the field
  empty.
- **Model weights:** AGPL-3.0, as stated on the
  [Hugging Face model page](https://huggingface.co/Eyened/vascx). Strong copyleft, with
  consequences for network services.

## 3. Major publications by the authors

- Vargas Quiros JD, Liefers B, van Garderen KA, Vermeulen JP, Klaver CCW. *VascX Models: Deep
  Ensembles for Retinal Vascular Analysis From Color Fundus Images.* Translational Vision Science &
  Technology 2025;14(7):19. [PMC12306690](https://pmc.ncbi.nlm.nih.gov/articles/PMC12306690/) ·
  [PubMed 40699175](https://pubmed.ncbi.nlm.nih.gov/40699175/)

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** four — `background`, `artery`, `vein`, `unclassified` — as a **softmax**, not
  as independent probabilities. *Our finding, 2026-10-01:* the four channels sum to exactly
  1.000000 at every pixel. A pixel therefore gets one label, and the consequence is §10.1.
- **Input grid:** 1024×1024. Preprocessing crops to the detected fundus bounds and resamples so the
  fundus diameter fills a 1024-pixel square, so every VascX model sees the retina at the same scale
  regardless of the camera's native resolution — which is what makes VascX biomarkers comparable
  across cameras without a per-image scale factor.
- **Output grid:** artery and vein masks at 1024×1024, the grid calibre and central retinal equivalents are measured on.
- **Grid set in:** `square_size=1024` in `rtnls_fundusprep/preprocessor.py` (the default passed by
  its batch entry point), with `rescale(image, resolution=1024)` in the same package's `utils.py`.
- **Input expected:** a colour-fundus photograph, in standard image formats or DICOM. Preprocessing
  is not optional: the pipeline crops to the field of view and enhances contrast first.
- **Preprocessing in the published code:** performed by
  [retinalysis-fundusprep](https://github.com/Eyened/retinalysis-fundusprep) (AGPL-3.0), which the
  authors report succeeds in detecting image bounds on 99.5% of a diverse set — their measurement.

## 5. Architecture

- **Family:** U-Net, per the paper, trained with a new preprocessing algorithm and strong data
  augmentation.
- **Parameters:** Unknown.
- **Single model or ensemble:** an ensemble; the member count is in the paper.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| More than fifteen published annotated datasets, combined | Training | Their own authors | In the paper; the per-model split is not restated here |
| Dutch cohort images, principally the Rotterdam Study | Training | The cohort's graders | In the paper |

The training set absorbs most of the public annotated data, so few public datasets remain for a
blind benchmark of this model. That cuts both ways: broad training is why it generalises, and also
why an independent evaluation is hard to construct.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://huggingface.co/Eyened/vascx — file `artery_vein/av_july24.pt`.
- **Format and size:** PyTorch `.pt`, fetched automatically by the inference code.
- **Files in an ensemble:** one file, itself an ensemble checkpoint.

## 8. Performance as reported by the authors

The VascX Models paper reports stronger correlation with biomarkers computed from ground-truth masks than AutoMorph, for 23 of 24 biomarkers, and better vascular-tree connectivity. These are the authors' own measurements of their own model, recorded as their claim.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [VascX](../projects/vascx.md) | One stage of `vascx run-models` | The published weights |

## 10. Known defects

### 10.1 Arteriovenous crossings cannot be represented, and are not

*Our finding, 2026-10-01.* The output is a four-way **softmax**: the channels sum to exactly
1.000000 at every pixel, so `artery ≥ 0.5` and `vein ≥ 0.5` at the same pixel is arithmetically
impossible. Where an artery crosses a vein, one wins and the other is cut.

This is a property of the model rather than of how this atlas runs it. The adapter thresholds each
class **independently** at 0.5 and would pass overlap through if the network produced any; measured
on five [HRF](../datasets/hrf.md) photographs it produced none at all. HRF's reference standard
marks crossings as their own colour and this atlas's store writes a crossing into *both* masks, so
there is something to miss:

| Model | artery ∩ vein, 5 HRF photographs |
| --- | --- |
| [bf-net](bf-net.md) | 4.04% of predicted vessel |
| [automorph-artery-vein](automorph-artery-vein.md) | 2.85% |
| [lunet](lunet.md) | 2.39% |
| [ocularnet](ocularnet.md) | 1.64% |
| **vascx-artery-vein** | **0.000%** |
| *expert — HRF-AV* | *3.39%* |

It is the only artery/vein model in this catalogue whose two masks never overlap.

**Where the crossing pixels go instead**, by argmax at the expert's crossing pixels:

| Photograph | artery | vein | background | unclassified |
| --- | --- | --- | --- | --- |
| 01_h | 41.8% | 22.3% | 28.0% | 7.9% |
| 01_dr | 25.4% | 38.2% | 23.7% | 12.7% |
| 01_g | 27.5% | 43.0% | 23.1% | 6.4% |

So one vessel always survives and the other is interrupted — and **31% to 39% of crossing pixels
reach neither mask**, falling into background or into the fourth channel. Crossing recall is 44% to
69% against 69% to 81% for plain vessel.

**Two things that look like remedies and are not.** The `unclassified` channel is an *uncertainty*
class, not a crossing class: it is enriched 4.3× to 11.6× at expert crossings but captures only 6%
to 13% of them. And no threshold recovers them — sweeping 0.50 down to 0.20 on one photograph
yields 4.9% of the expert's crossing pixels, with only 10.5% of the overlap produced sitting at a
crossing and both masks inflating by about a third.

### 10.2 What the cut costs downstream

VascX's tracer does not repair it: a vessel severed in the mask is resolved as **two vessels**, and
a single pixel of gap is enough — see
[vessel tracing](../biomarkers/vessel-tracing.md) §3.2.1 for the stage-by-stage reason and the
measurement. On real photographs, free vessel ends in this model's output are **4.4× to 16.7×
denser within 25 px of an expert crossing** than elsewhere.

The effect is uneven across biomarkers, and the pattern is itself evidence. Arc-over-chord
tortuosity is barely moved, because VascX already splits long segments on purpose — `max_segment_len`
defaults to 0.2 of the disc-fovea distance and is applied *only* to segment-mode distance
tortuosity, so one more accidental split changes little. Curvature and the vessel-level modes get
no such splitting and are measured on two straighter pieces instead of one curved vessel. Measured
on one HRF photograph against the expert's own map, τ1 moved −1.5% where the curvature column moved
−39%.

Nothing here is a reason to prefer another model on its own: a segmenter that emits overlap has
only recorded the ambiguity, not resolved it, and this atlas has no measurement saying whose
crossings are *right*. What it does mean is that **a VascX count of vessels, endpoints or
components is not comparable with one from a pipeline that bridges gaps**, such as
[AutoMorphClass](../projects/automorphclass.md).

## 11. Notes

- Stamped `july24`, like the other segmentation models here.
- Downstream biomarkers are region-aware, computed relative to the disc-fovea axis, so this model's
  output is combined with the disc and fovea models before any number is produced.

---

**Links and license last checked:** 2026-09-10
