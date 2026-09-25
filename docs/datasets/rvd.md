# RVD — Retinal Vessel Dataset

635 short colour videos of the back of the eye, recorded not with a bench-top hospital camera but
with a **smartphone held up to a fundus lens**, in four clinics, from 415 people aged 50 to 75.
From each video two representative still frames were chosen and annotated, giving **1,270 annotated
frames** — each one carrying a vessel map, an artery/vein map, and a finer map that also sorts every
vessel into one of four width bands. On top of that the videos carry **timing** annotations: whether
the retinal veins visibly pulse, when in the video the pulse happens, and which frames are the peak
and the trough of it. That last part is what nothing else in this catalogue has — every other
dataset here is a still photograph, and a still photograph cannot show a pulse.

## 1. What it is

- **Images:** 635 videos, over 130,000 frames in total; **1,270 frames carry spatial annotations**
  (two keyframes per video). 335 videos show spontaneous venous pulsation and 300 do not.
- **Collected at:** four clinics, over about five years, by clinicians trained to operate the
  handheld device. 415 patients — 264 male, 151 female — aged 50 to 75. Australian institutions
  (the author list spans the University of Technology Sydney, the University of Queensland and
  others); the individual clinics are not named.
- **Purpose:** to make retinal vessel segmentation work on cheap portable equipment rather than
  bench-top cameras, and to support detection of **spontaneous retinal venous pulsation (SVP)** — a
  pulsing of the retinal veins whose absence is associated with raised intracranial pressure and
  with glaucoma. The authors describe it as the first video-based retinal vessel dataset.

## 2. Provenance

| | |
| --- | --- |
| Home | https://uq-cvlab.github.io/Retinal-Video-Dataset/ |
| Download | `direct, no registration` — https://zenodo.org/records/8287928 (26.1 GB: `Labels.zip` 3.6 GB, plus `videos_part0.zip` … `videos_part9.zip`) |
| Citation | Khan MDW, Sheng H, Zhang H, Du H, Wang S, Coroneo MT, Hajati F, Shariflou S, Kalloniatis M, Phu J, Agar A, Huang Z, Golzan M, Yu X. *RVD: A Handheld Device-Based Fundus Video Dataset for Retinal Vessel Segmentation.* Advances in Neural Information Processing Systems 36 (NeurIPS 2023), Datasets and Benchmarks Track. arXiv:[2307.06577](https://arxiv.org/abs/2307.06577). Data DOI: [10.5281/zenodo.8287928](https://doi.org/10.5281/zenodo.8287928) |
| Licence | **Creative Commons Attribution–NonCommercial–NoDerivatives 4.0 International (CC BY-NC-ND 4.0)** |
| Content | 635 colour videos at 25 frames per second, 2 to 30 seconds each, over 130,000 frames; 1800×1800 pixels as stated in the paper (see section 7) |
| Annotations | 1,270 annotated keyframes with three kinds of spatial mask, plus SVP presence, temporal localisation and peak/trough frames |

**The licence is the most restrictive kind in this catalogue, and in two separate ways.**
*NonCommercial* rules out commercial use. *NoDerivatives* is the one that catches people: a resized
copy, a re-encoded video, a set of extracted frames or a corrected mask is a derivative work, so
redistributing any of those is not permitted even with attribution. Using the data to train a model
and publishing the model is a different question that the licence does not settle cleanly — take
advice rather than assuming. This repository catalogues the dataset and does not redistribute it.

Ethics: the authors state the work follows the Declaration of Helsinki and that written consent was
obtained from every participant before collection.

## 3. The images

**These are videos, not photographs.** Everything below describes video frames.

| | |
| --- | --- |
| Resolution (pixels) | 1800×1800 as stated in the paper's comparison table. The deposit's video directory is named `1080_crop`, which does not agree — see section 7 |
| Microns per pixel | **Unknown**, and unlikely ever to be one number: a handheld device's distance and angle to the eye change from recording to recording, and the phones themselves differ between clinics |
| Camera | A **smartphone coupled to a fundus camera lens**. The authors state that because collection ran across four clinics over five years, *the phones used differ*, and they do not name any make or model |
| Field of view | **Unknown** — not stated by the authors |
| Centring | **Optic disc region**, by construction: segments where the disc could not be detected were discarded, and the remaining frames were stabilised so that the disc stays put across a video |
| Modality | **Colour fundus video from a handheld smartphone device.** Not bench-top still photography. Frames carry video compression, motion blur and illumination that a mydriatic table-top camera does not produce, so a score here is not comparable with a score on DRIVE or FIVES |

The dataset has no well-defined subcollections by camera, because the authors did not record which
clinic or which phone produced which video. The only published partition is by SVP presence
(335 / 300) and the train/test split described in section 6.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Binary vessel mask | **Six clinicians across the set**; the number who read each frame is not stated | frame resolution | One per annotated keyframe — 1,270 |
| General artery/vein mask | as above | frame resolution | Arteries against veins, two classes |
| Fine-grained artery/vein mask | as above | frame resolution | **Eight classes**: `AL0`–`AL3` and `VL0`–`VL3`, four increasing width bands for arteries and four for veins. Nothing else in this catalogue labels vessel width as a class |
| SVP present / absent | as above | per video | 335 present, 300 absent |
| SVP temporal localisation | as above | per video | *When* in the video the pulsation occurs |
| SVP peak and trough | as above | per frame | The frames of maximum and minimum pulse width, in the SVP-present videos |
| Optic disc region | machine-generated, then checked | per frame | Bounding **boxes**, not a segmentation — see section 8 |

**Do not read "six clinicians" as six readers per frame.** The paper says six clinicians were
involved in the annotation process to ensure quality; it does not say how the work was divided,
whether any frame was read more than once, or whether separate readings were kept. So this dataset
cannot be used to measure inter-reader agreement, which several smaller sets in this catalogue can.

## 5. Inheritance

- **Reuses images from:** No shared images established. The videos were collected for this dataset.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. No model in `docs/models/` names
  RVD as training data, so every catalogued model is out-of-sample here.
- **Below a model's measuring grid:** No, on either reading of the resolution. At 1800×1800 it is
  above every grid in this catalogue; at 1080×1080 it is still above the 1024 and 912 grids the
  catalogued segmenters use.
- **What it can answer:** two things nothing else here can.
  1. **Whether a vessel or artery/vein model trained on bench-top photographs survives contact with
     a phone.** Every other vessel dataset in this catalogue is mydriatic still photography from
     dedicated equipment. A model that scores well on DRIVE and badly here has learned the camera
     as much as the anatomy, and there is no other way in this catalogue to find that out.
  2. **Anything about vessel pulsation**, which needs a moving picture. No still dataset can pose
     the question.

  Its published protocol splits **by patient**: 517 videos for training and validation, 118 for
  testing, with every video of one patient kept on the same side so that the same eye cannot appear
  on both. The authors also report cross-validation over three different splits. Anyone benchmarking
  on RVD should keep that patient-disjoint discipline — 635 videos from 415 people means some people
  contributed several, and a naive random split would leak.

## 7. Known defects

- **The stated resolution and the deposit disagree, and this is unresolved.** The paper's
  comparison table gives RVD as `1800×1800`; the Zenodo deposit's video directory is named
  `1080_crop`, and the project site quotes no resolution at all. *This atlas has not downloaded the
  26 GB to check*, so the page records the published figure and this discrepancy rather than
  guessing which is right. Anyone who resolves it should correct section 3.
- **The camera is unidentified.** "A smartphone connected to a fundus camera lens", differing across
  four clinics and five years, with no make, model or lens recorded and no per-video attribution.
  That makes it impossible to say which frames came from which optics, so the resolution and
  field-of-view rows cannot be resolved per subcollection the way other datasets' can.

Nothing else recorded as of 2026-09-25 — an absence of findings rather than a clean bill of health.
This atlas has read the paper, the project site and the deposit's metadata; it has not inspected
the archives.

## 8. Notes

- **The optic disc boxes are mostly machine-generated.** The authors hand-labelled the disc region
  on one frame in every 25, trained a Faster R-CNN detector on those, and let it label the rest,
  with manual correction of errors that were spotted. They are also **bounding boxes**, not disc
  contours, so this dataset is not a disc-segmentation resource and is not listed as one.
- **Frames were filtered before annotation, in two ways.** Segments were dropped unless the disc
  was detectable for at least 30 consecutive frames, and frames with large optical flow — a proxy
  for motion blur — were discarded, with a further manual pass by non-expert annotators. So the
  distributed frames are the *usable* part of what was recorded, and the dataset is not a sample of
  raw handheld capture quality. A model's score here says how it does on handheld video that has
  already been screened.
- **The two annotated keyframes per video were chosen to be informative, not at random**: the frame
  with the most visible vessels, covering the disc, fovea and macula, and then a second frame
  maximally distant from the first. That is the right choice for annotation value and the wrong one
  for estimating average-case performance.
- **SVP is the reason this dataset exists**, and it is a dynamic sign rather than an anatomical one.
  Nothing in `docs/biomarkers/` currently covers it; it sits outside the calibre-and-tortuosity
  family this atlas catalogues.

---

**Links, licence and access last checked:** 2026-09-25
