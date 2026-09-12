# Fundus Image Toolbox fovea and disc locator

Given a fundus photograph, this returns four numbers: the x and y of the fovea and the x and y of
the optic disc centre. It does not segment either — no mask, no boundary, just where the two
landmarks are — which is enough for the jobs landmarks are actually used for: deciding whether a
photograph is macula-centred or disc-centred, and providing the disc-fovea distance that several
biomarkers are normalised by.

One network predicts both points at once, which is the point of it: the two landmarks constrain
each other, and a model that knows where the disc is has a better idea where the fovea is.

## 1. Code reference

- **Repository:** https://github.com/berenslab/fundus_image_toolbox
- **Version described here:** commit `d7757e28` (2026-08-13)
- **Most recent commit:** 2026-08
- **Training code included:** **Yes, in this repository** —
  `0_example_usage/training and evaluation/training_fovea-od_cli.py`, with notebooks for preparing
  the three training datasets into one table.
- **Language and how it runs:** Python with PyTorch. `load_fovea_od_model()` then `model.predict()`.
  Weights are fetched from Zenodo on first use. Batch prediction is supported.

## 2. License

- **Code:** **MIT**.
- **Model weights:** not stated separately in the repository; the Zenodo record
  ([11174642](https://zenodo.org/records/11174642)) carries its own licence field, which is what
  governs redistribution.

## 3. Major publications by the authors

- Gervelmeyer J, Müller S, Huang Z, Berens P. *Fundus Image Toolbox: A Python package for fundus
  image processing.* Journal of Open Source Software 2025;10(108):7101. DOI:
  [10.21105/joss.07101](https://doi.org/10.21105/joss.07101)

## 4. What it produces

- **Purpose:** `other` — landmark coordinates, not a segmentation.
- **Output classes:** four numbers per image: fovea x, fovea y, disc x, disc y. The network emits
  them as **fractions of the frame**, and the published code multiplies them by the original
  image's width and height before returning.
- **Input grid:** **350×350**, reached by resizing the **shorter** side to 350 with the aspect ratio
  kept and then taking a **centre crop** of 350×350.
- **Output grid:** not applicable — points, not a mask. The coordinates come back in the original
  photograph's pixels.
- **Grid set in:** `fundus_image_toolbox/fovea_od_localization/default.py`, `"img_size": 350`;
  applied in `model_multi.py` as `Resize(self.config.img_size), CenterCrop(self.config.img_size)`.
- **Input expected:** a whole fundus photograph. Nothing requires the field of view to be cropped
  first, and **a square photograph is the case the geometry is exact for** — see section 10.
- **Preprocessing in the published code:** resize, centre crop, tensor conversion. No contrast
  enhancement and no field-of-view detection.

## 5. Architecture

- **Family:** EfficientNet-B3 with an ImageNet-initialised backbone, multi-task: one trunk, four
  regression outputs.
- **Parameters:** about 12 million, EfficientNet-B3's own count; not stated by the authors.
- **Single model or ensemble:** **one model**, the checkpoint named `2024-05-07 11_13.05`. The code
  supports EfficientNet-B0 to B7 and ResNets for retraining, but one B3 is what is published.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| ADAM | Training, validation, test | Optic disc masks, converted by the authors into centre coordinates | Yes: a combined test split across the three |
| [REFUGE](../datasets/refuge.md) | Training, validation, test | Optic disc masks, converted the same way | As above |
| [IDRiD](../datasets/idrid.md) | Training, validation, test | Fovea and disc centre coordinates as published | As above |

The three are pooled into one table and split together, so **[REFUGE](../datasets/refuge.md) and
[IDRiD](../datasets/idrid.md) are unavailable for a fair benchmark of this model**, as is ADAM,
which is not yet catalogued here.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://zenodo.org/records/11174642/files/weights.tar.gz — fetched automatically
  on first use.
- **Format and size:** a tar archive holding one PyTorch checkpoint and its config.
- **Files in an ensemble:** not applicable — a single model.

## 8. Performance as reported by the authors

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| Combined ADAM + REFUGE + IDRiD test split | Mean distance to both targets | 0.88% of image size — about 3.08 pixels at 350×350 | `1_read_more/Readmore_fovea_od_localization.md` |

For scale the authors quote the ADAM challenge's winning fovea model at 18.55 pixels, which they
normalise to 0.98% of image size — while noting that their own figure is on a different test set and
covers the disc as well as the fovea. Two numbers normalised from different test sets are not a
head-to-head result, and the authors say so.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued project runs it | — |

## 10. Known defects

- **The centre crop is not undone when the coordinates are mapped back.** Inference resizes the
  shorter side to 350 and centre-crops to 350×350, so on a **non-square** photograph a strip of the
  long axis is discarded before the network sees anything. The returned coordinates are then
  computed as `fraction × original width` and `fraction × original height`
  (`model_multi.py`, `predict`), which is the mapping that would be correct had no crop happened.
  The consequence is geometric, not statistical: on a 2000×1500 photograph the discarded strip is
  about 250 original pixels at each side, and a landmark away from the centre is placed further
  out than it is. On a **square** photograph the crop removes nothing and the mapping is exact —
  and square is what ADAM, REFUGE and IDRiD largely are, which is consistent with the reported
  accuracy. No upstream issue records this; it is read from the published inference code, dated
  2026-09-12, and has not been confirmed by running the model.
- **A landmark outside the centre crop cannot be predicted at all** on a non-square photograph,
  for the same reason: it is not in the image the network receives.

## 11. Notes

- Points, not masks. Anything needing a disc **boundary** — a cup-to-disc ratio, a disc diameter in
  microns — needs a disc/cup segmenter such as [VascX disc](vascx-disc.md) or
  [AutoMorph's](automorph-disc-cup.md); this gives the centre only.
- The disc-fovea distance it yields is the ruler that
  [several VascX biomarkers](../biomarkers/disc-fovea-distance.md) are normalised by, which is why
  a landmark model earns a page of its own rather than a footnote.
- It is the only model in this catalogue trained to find the fovea and the disc **jointly**;
  [VascX fovea](vascx-fovea.md) finds the fovea alone.

---

**Links and license last checked:** 2026-09-12
