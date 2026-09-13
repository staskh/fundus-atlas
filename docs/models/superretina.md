# SuperRetina

Given two fundus photographs of the same eye, SuperRetina finds the points that correspond between
them — vessel crossings and bifurcations, mostly — and returns the matches from which an alignment
can be computed. It segments nothing and measures nothing. It is in this catalogue because
alignment is the step that makes two photographs of one eye comparable, which is what any
longitudinal question needs: a biomarker that moves between visits has to be measured in the same
frame at both.

Its contribution is how it was trained. Keypoint detectors need labelled keypoints, and nobody
labels vessel junctions at scale, so it learns from a small labelled set and expands its own labels
as it trains.

## 1. Code reference

- **Repository:** https://github.com/ruc-aimc-lab/SuperRetina — the authors' own.
  Wrapped by the [Fundus Image Toolbox](https://github.com/berenslab/fundus_image_toolbox), which
  is how it is reached in this catalogue.
- **Version described here:** the toolbox's wrapper at commit `d7757e28` (2026-08-13); the upstream
  repository was last pushed in 2023-02.
- **Most recent commit:** 2023-02 upstream; 2026-08 for the wrapper.
- **Training code included:** Yes, in the upstream repository.
- **Language and how it runs:** Python with PyTorch. Through the toolbox:
  `load_registration_model()` then `register(fixed, moving)`. Weights are fetched from Zenodo on
  first use.

## 2. License

- **Code:** **none stated** on the upstream repository. The toolbox's wrapper around it is MIT,
  which does not extend to the model it wraps.
- **Model weights:** served from
  [Zenodo record 11241985](https://zenodo.org/records/11241985) by the toolbox; no licence is stated
  in the wrapper.

## 3. Major publications by the authors

- Liu J, Li X, Wei Q, Xu J, Ding D. *Semi-supervised Keypoint Detector and Descriptor for Retinal
  Image Matching.* ECCV 2022:593–609. [arXiv:2207.07932](https://arxiv.org/abs/2207.07932)

## 4. What it produces

- **Purpose:** `other` — keypoints and their descriptors, for matching one photograph to another.
- **Output classes:** not classes. Detected keypoints, their descriptors, the matches between two
  images, and the transform derived from those matches.
- **Input grid:** **512×512**. Both photographs are brought to it before the network sees them.
- **Output grid:** not applicable — points and a transform, not a raster. The toolbox's output image
  size is independent of the model's input size.
- **Grid set in:** `fundus_image_toolbox/registration/inference.py`, `IMG_SIZE = 512`.
- **Input expected:** two photographs of the **same eye**; the pair is what it operates on, not a
  single image. Greyscale internally.
- **Preprocessing in the published code:** contrast enhancement with CLAHE
  (`enhance`), conversion to greyscale, and the resize to 512.

## 5. Architecture

- **Family:** a keypoint detector and descriptor network in the SuperPoint tradition — one trunk,
  two heads, one locating points and one describing them so they can be matched across images.
- **Parameters:** Unknown; not stated.
- **Single model or ensemble:** one model, `SuperRetina.pth`.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| Unknown to this atlas | Training | The paper's own semi-supervised scheme, which expands a small set of labelled keypoints during training | See the paper |

Read the paper before benchmarking it on any catalogued dataset; this page has not established
which images it saw.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://zenodo.org/records/11241985/files/SuperRetina.pth — fetched
  automatically by the toolbox on first use.
- **Format and size:** one PyTorch `.pth` checkpoint.
- **Files in an ensemble:** not applicable — a single model.

## 8. Performance as reported by the authors

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| — | — | Not restated here | Liu et al. 2022 |

The paper reports matching accuracy on retinal image-matching benchmarks. Those are its authors'
measurements on their own test sets, and nothing is reproduced here that this atlas has not checked.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued project runs it | — |

## 10. Known defects

None recorded as of 2026-09-12 — an absence of findings, not a clean bill of health. The toolbox's
issue tracker carries one report of a registration failure
([issue 24](https://github.com/berenslab/fundus_image_toolbox/issues/24)), since closed, which
concerned the wrapper rather than the model.

## 11. Notes

- **It needs a pair.** Everything else in this catalogue takes one photograph; this takes two of the
  same eye and is meaningless on one.
- The obvious use here is [GRAPE](../datasets/grape.md), the only catalogued dataset with repeat
  visits of the same eyes — 263 eyes over one to seven visits. Whether a biomarker tracks change in
  an individual is a question that needs those visits in a common frame.
- Unlicensed upstream (section 2), like the
  [FR-UNet vessel ensemble](frunet-fives.md), and reached through the same MIT-licensed wrapper.
  The wrapper's licence is not the model's.

---

**Links and license last checked:** 2026-09-12
