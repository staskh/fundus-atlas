# ORVS

49 colour photographs of the back of the eye from a clinic in Calgary, Canada, each with a tracing
of its blood vessels drawn by one expert. ORVS — *Online Retinal image for Vessel Segmentation* —
was published in 2020 alongside a vessel-segmentation method, to add one more Canadian camera to
the handful of small vessel-tracing sets the field measures on. Its own tracing does not tell
arteries from veins; an artery/vein layer for all 49 photographs was later added by the
[OCULAR](../projects/ocularnet.md) project, drawn by a model and corrected by hand.

## 1. What it is

- **Images:** 49, divided by the authors into 42 for training and 7 for testing (but see section 7:
  the files as circulated split 41 and 8). No disease breakdown is published.
- **Collected at:** a clinic in Calgary, Alberta, Canada, through a collaboration between the
  Department of Computer Science and the Department of Ophthalmology and Visual Sciences at the
  University of Calgary.
- **Purpose:** a new vessel reference standard contributed with a paper on vessel segmentation by
  transfer learning, "to help increase the number of images available for researchers working in
  this field" (the authors' words).

## 2. Provenance

### 2.1 ORVS — the photographs and vessel tracings

| | |
| --- | --- |
| Home | The authors' GitHub repository, <https://github.com/AbdullahSarhan/ICPRVessels> (the paper's footnote link, <https://tinyurl.com/y3kr7o4j>, redirects there). **It answers 404**: the repository has been removed (checked 2026-10-12) |
| Download | **direct, no registration — from a third-party copy only.** <https://github.com/hitszsyl/ICPRVessels>, folder `Vessels-Datasets/ORVS`, which carries the authors' own commit history (last commit `421886be`, 2021-06-25). It is an uploader's copy, not the depositor's, and it has no licence of its own. A second copy is listed at <https://opendatalab.org.cn/ORVS> (route not checked) |
| Citation | Sarhan A, Rokne J, Alhajj R, Crichton A. *Transfer Learning Through Weighted Loss Function and Group Normalization for Vessel Segmentation from Retinal Images.* In: 2020 25th International Conference on Pattern Recognition (ICPR), IEEE, 2021:9211–9218. DOI: [10.1109/ICPR48806.2021.9412378](https://doi.org/10.1109/ICPR48806.2021.9412378) · preprint [arXiv:2012.09250](https://arxiv.org/abs/2012.09250) |
| Licence | **not stated.** Neither the paper nor the repository's README states one, and the surviving copy has no LICENSE file. The README asks only that users cite the paper |
| Content | 49 images at 1444×1444, JPEG |
| Annotations | Supplies one expert's binary vessel tracing per photograph |

The repository that carried ORVS also carried copies of six other datasets — ARIA,
[CHASE-DB1](chase-db1.md), [DR HAGIS](dr-hagis.md), [DRIVE](drive.md), [HRF](hrf.md) and [IOSTAR](iostar.md) —
split the way the paper used them. Those are other people's photographs under their own terms; only
the `ORVS` folder is this dataset. Several dataset indexes still point at the removed original,
including [openmedlab's Awesome-Medical-Dataset](https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/ORVS.md),
which is where the OCULAR README sends readers.

### 2.2 OCULAR — artery/vein labels

| | |
| --- | --- |
| Home | The OCULAR repository, <https://github.com/GonzaloPlaaza/OCULAR>, section "Release of New Artery-Vein Annotations" |
| Download | **direct, no registration** — a public Google Drive folder, <https://drive.google.com/drive/folders/1FvxSUEn-Md_0pWhN2QTxIKCEJX9eqx1L> |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030 — [Plaza 2026](../papers/plaza-2026.md) |
| Licence | **not stated** — the OCULAR repository has no LICENSE file |
| Content | 49 PNG label maps, one per photograph, named by the same numbers as the ORVS images (`2012.png` … `2146.png`) (checked 2026-10-12) |
| Annotations | Supplies artery, vein and crossing labels, drawn by [OCULARNet](../models/ocularnet.md) at 1024×1024, cut back to ORVS's own vessel tracing and corrected by hand |

These are the first artery/vein labels for ORVS, and they are a model's. OCULAR's README describes
the procedure: OCULARNet predicts artery, vein, crossing or background at 1024×1024; the ORVS
vessel tracing is resized to the same grid; model pixels outside the tracing are removed, traced
pixels the model missed are given its next most likely class; the authors then paint over errors in
their own annotation tool, which also offers an *uncertain* class; and the result is multiplied by
the vessel tracing again. Every vessel pixel is therefore one the ORVS expert drew; which class it
is, is OCULARNet's call wherever its authors did not overrule it. OCULAR states these annotations
were not used to train or evaluate OCULARNet.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1444×1444, as published (paper, Table I). Not checked by this repository, which has not downloaded the images |
| Microns per pixel | Unknown — not published, and no scale has been inferred here yet (no fetcher exists) |
| Camera | Zeiss Visucam 200 |
| Field of view | 30° |
| Centring | **Not stated by the authors.** OCULAR's README lists ORVS as disc-centred ("D") — OCULAR's claim, not checked here |
| Modality | Colour fundus photography; 24 bits per pixel, stored as JPEG "with low compression, which is common in ophthalmology practice" (the authors) |

OCULAR's README agrees with the paper on count (49), field (30°) and size (1444×1444), gives the
region as Canada and lists no pathology.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **One expert**, "working in the field of retinal-image analysis" and trained for the task | Native, as far as stated | Every vessel pixel marked by hand in Windows Paint 3D. No second reader, so no human agreement ceiling can be measured. Distributed as **JPEG**, not a lossless format (section 7) |
| Artery, vein and crossing, by [OCULAR](../projects/ocularnet.md) | One model, refined by OCULAR's authors | **1024×1024**, not this dataset's native 1444×1444 | A model's output corrected by hand, not an independent reader: where the model and the corrector agree on a mistake, it stays. The size at which the published PNGs are stored was not checked. Section 2.2 |

## 5. Inheritance

- **Reuses images from:** No shared images established. The photographs were collected for this
  dataset at a Calgary clinic.
- **Its images are reused by:** [OCULAR](../projects/ocularnet.md), which adds artery/vein labels to
  all 49 (section 2.2). It did not train or evaluate OCULARNet on them. No other catalogued dataset
  is established to contain them.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. No model page in this catalogue
  names ORVS, and OCULAR states its ORVS artery/vein labels were not used to train or evaluate
  [OCULARNet](../models/ocularnet.md). The paper's own model trained on 41–42 of the 49, but it is
  not catalogued here.
- **Below a model's measuring grid:** No — 1444×1444 is above the 912 and 1024 grids the catalogued
  models measure on. But the OCULAR artery/vein layer was drawn at 1024×1024, so its labels carry
  no finer detail than that grid.
- **What it can answer:** vessel segmentation on a narrow-field (30°) Zeiss camera from a Canadian
  clinic, held out for every catalogued model; and, with the OCULAR layer, artery/vein accuracy —
  with the caveat that the reference was itself drawn by OCULARNet, so scoring OCULARNet against it
  is not an independent test.

## 7. Known defects

- **The original distribution is gone.** *Our finding, 2026-10-12:*
  `github.com/AbdullahSarhan/ICPRVessels`, the paper's link, answers 404. The surviving copy at
  `hitszsyl/ICPRVessels` is a third party's, with no licence; its contents could differ from what
  the authors last published and nothing available can confirm they do not.
- **The split in the files is 41 / 8, not the paper's 42 / 7.** *Our finding, 2026-10-12*, from the
  copy's file listing: `Train/Original/Images` holds 41 photographs and `Test/Original/Images` 8, each
  with a matching label. The total, 49, agrees with the paper. The paper says the test images were
  chosen at random as 15% of the set, so the published split is one draw, not a fixed standard.
- **The vessel tracings are stored as JPEG.** *Our finding, 2026-10-12*, from the file listing: every
  label file is a `.jpg`. JPEG compression smears a black-and-white mask's edges into grey, so the
  tracing must be thresholded back to binary before use, and the threshold chosen moves the vessel
  edges. The [torch-em](https://github.com/constantinpape/torch-em) loader for ORVS reports the same
  and binarises with a fixed threshold.
- **A widely linked index misdescribes the files.** openmedlab's ORVS page gives a size range of
  584×565 to 3504×2336 and file names `ORVS_xx.png`. Neither matches the dataset: ORVS is
  1444×1444 throughout per the paper, and the files are numbered JPEGs. The extremes are exactly
  the sizes of [DRIVE](drive.md) and [HRF](hrf.md), which sat in the same repository, so — our
  reading — the statistics were computed over the whole bundle rather than ORVS alone.

## 8. Notes

- One reader, one camera, 49 images: a small held-out set, useful as a different clinic and device
  rather than as a precise yardstick.
- Treat the two layers as having different authors. The vessel tracing is a person's; the
  artery/vein colouring is a model's, checked by people. A model that resembles OCULARNet will look
  better against the second than it deserves.

---

**Links, licence and access last checked:** 2026-10-12
