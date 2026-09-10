# ARIA (Automated Retinal Image Analyzer)

ARIA detects blood vessels in a fundus photograph and measures their diameter, using wavelet-based
detection followed by a refinement step that locates each vessel edge precisely. It is MATLAB
software with a graphical interface, written to be adapted: its author explicitly designed it so
that parameters can be retuned for other image types and individual algorithm pieces swapped out.

It is the oldest entry in this catalogue — last updated in 2016 — and it predates the deep-learning
pipelines. It remains useful as a reference point for vessel-width measurement, which is the
biomarker most sensitive to how the vessel edge is defined.

## 1. Code reference

- **Repository:** https://github.com/petebankhead/ARIA
- **Version described here:** commit `328853dc` (2016-05-18). No tags or releases are published.
- **Most recent commit:** 2016-05
- **Language and how it runs:** MATLAB. Open MATLAB in the repository folder and type `ARIA` at the
  prompt, or run `ARIA_setup` once to add the directories to the MATLAB path permanently. A user
  guide PDF is included in the repository.
- **Training code included:** Not applicable — the method is algorithmic, so there is nothing to
  train. `ARIA_run_tests` reproduces the paper's evaluation instead.

## 2. License

- **Code:** A BSD 2-clause style license, stated as a copyright notice in `Copyright.m`
  (Copyright 2011, Peter Bankhead) rather than in a LICENSE file. Because of that placement GitHub
  does not recognise a license for this repository, so automated license scans will report it as
  unlicensed even though permissive terms are stated in the source.
- **Model weights:** Not applicable — no trained model is used.

## 3. Major publications by the authors

- Bankhead P, Scholfield CN, McGeown JG, Curtis TM. *Fast Retinal Vessel Detection and Measurement
  Using Wavelets and Edge Location Refinement.* PLoS ONE 2012;7(3):e32435. DOI:
  [10.1371/journal.pone.0032435](https://doi.org/10.1371/journal.pone.0032435)

The author asks that this paper be cited in any publication using the software.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| Wavelet-based vessel detection with edge location refinement | Blood vessels, and the location of each vessel edge | Introduced here |

No artery/vein separation and no optic disc segmentation are included. The method is algorithmic —
wavelets and edge refinement, not a trained network — which is why it needs no training data and no
GPU, and why its behaviour on an unfamiliar camera depends on parameter tuning rather than on
retraining.

## 5. Models introduced here

### 5.1 Wavelet vessel detection and edge location refinement

- **Training data:** Not applicable — the method is not trained. The paper evaluates it on the [DRIVE](../datasets/drive.md)
  and REVIEW datasets.
- **Weights publicly available:** Not applicable.
- **Download URL:** Not applicable.
- **Training code:** Not applicable.

## 6. Biomarkers computed

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| [Vessel diameter (width)](../biomarkers/vessel-calibre.md) along each detected vessel | The paper in section 3 | This project | Introduced here |

Whether ARIA also outputs derived summary measures such as tortuosity or calibre equivalents was
not established at the time of checking. Treat vessel diameter as the measurement it is built to
provide.

## 7. Examples and notebooks

- Type `ARIA` in MATLAB and open any fundus image — start here; the graphical interface shows the
  detected vessels and the measured edges, which is the quickest way to judge whether the
  parameters suit your images.
- `ARIA_run_tests.m` — reproduces the results and timings reported in the paper. It requires the
  DRIVE and REVIEW datasets, which must be obtained from their own sources first.

## 8. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Nothing in this
project's issue tracker or code was found to change the numbers a user would report.

## 9. Notes

- Requires a MATLAB license, unlike every other entry in this catalogue.
- Dormant since 2016. The author's stated intent was that others fork and extend it, so derivative
  versions may be more current than this repository.

---

**Links and license last checked:** 2026-09-10
