# PVBM (Python Vasculature Biomarker toolbox)

PVBM computes vascular biomarkers from artery and vein segmentations that the user already has: it
does not segment the vessels itself. Give it a binary artery mask and a vein mask and it returns
fifteen measurements — areas, lengths, tortuosity, branching angles, several fractal dimensions, and
the central retinal calibre equivalents. It does include an optic disc segmenter, because most of
these measurements are defined relative to the optic disc. Its authors present it as a toolbox and
an API rather than a whole-image pipeline.

## 1. Code reference

- **Repository:** https://github.com/aim-lab/PVBM
- **Version described here:** commit `5edb79a6` (2026-01-01). The repository publishes no tags; the
  documentation site is versioned separately (3.0.0.0 at the time of checking) and the package is on
  PyPI as `pvbm`.
- **Most recent commit:** 2026-01
- **Language and how it runs:** Python, `pip install pvbm`, used as a library from a script or
  notebook. Documentation at https://pvbm.readthedocs.io/.
- **Training code included:** No. The biomarker code needs no training, and the bundled optic disc
  segmenter is shipped as a ready-made ONNX model; training code for it would belong to
  [LUNet](https://github.com/aim-lab/LUNet).

## 2. License

- **Code:** MIT License (`LICENSE` in the repository).
- **Model weights:** No separate license is stated for the optic disc segmenter weights, which are
  downloaded from Google Drive at first use rather than shipped with the package.

## 3. Major publications by the authors

- Fhima J, Van Eijgen J, Stalmans I, Men Y, Freiman M, Behar JA. *PVBM: A Python Vasculature
  Biomarker Toolbox Based on Retinal Blood Vessel Segmentation.* In: Computer Vision – ECCV 2022
  Workshops, Springer, 2023. DOI: [10.1007/978-3-031-25066-8_15](https://doi.org/10.1007/978-3-031-25066-8_15) ·
  [arXiv:2208.00392](https://arxiv.org/abs/2208.00392)

The toolbox has grown since that paper (the paper describes eleven biomarkers, the current README
lists fifteen), so the code and the publication do not match exactly.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| Optic disc segmenter (`DiscSegmenter`) | Optic disc | Borrowed — the README states it was produced using [LUNet](https://github.com/aim-lab/LUNet), by the same laboratory |
| Artery and vein segmentation | Arteries and veins | Not included. The user supplies these masks from another project |

This is the important thing to understand about PVBM: the vessel segmentation step, which is where
most of the disagreement between pipelines comes from, is outside the toolbox. Its numbers are only
as good as the masks fed into it, and the source of those masks must be recorded with any result.

## 5. Models introduced here

Not applicable — no new segmentation model is introduced; the disc segmenter is derived from LUNet
(see section 4). For completeness on the borrowed component:

- **Model file:** `lunetv2_odc.onnx`, downloaded on first use by `PVBM/DiscSegmenter.py`.
- **Download URL:** https://drive.google.com/uc?id=116EEFBn7qr_LpCBb8GBuyzpa_KGp4xPX — a Google
  Drive file, read out of the download code. It is not versioned in the repository, so the file
  behind that link can change without a commit.
- **Source project:** https://github.com/aim-lab/LUNet, for which GitHub reports no recognised
  license.
- **Training code:** Not in PVBM.

## 6. Biomarkers computed

Fifteen biomarkers, each computed independently on the arteriole and the venule segmentation. The
PVBM paper (section 3) states that the tortuosity and branching-angle algorithms are new
contributions of the toolbox.

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| Area, Length | Standard measures | — | Implemented here (in pixels and square pixels, not physical units) |
| Tortuosity index, median tortuosity | Arc-chord ratio; the algorithm is presented as new in the PVBM paper | — | Introduced here |
| Number of start points, end points, intersection points | Skeleton-based counts | — | Implemented here |
| Median branching angle | Presented as new in the PVBM paper | — | Introduced here |
| Capacity, entropy and correlation fractal dimensions; singularity length | Established fractal-analysis measures | — | Implemented here |
| CRAE and CRVE (central retinal arteriolar and venular equivalents) | Knudtson and Hubbard formulas from prior literature | — | Both formulas implemented; the user chooses |
| Arterio-venous ratio (AVR) | Ratio of CRAE to CRVE | — | Derived by the user from CRAE and CRVE |

Areas and lengths are reported in pixels, so results are not comparable across cameras or image
sizes without a resolution conversion of the user's own.

## 7. Examples and notebooks

- [`pvbmtutorial.ipynb`](https://github.com/aim-lab/PVBM/blob/main/pvbmtutorial.ipynb) — start here.
  It walks through disc segmentation, region-of-interest extraction, and the geometrical and fractal
  biomarkers on a sample image, which is also the clearest statement of the expected input format.

## 8. Notes

- **Scope caveat.** By this atlas's definition PVBM sits at the boundary of a project: it combines
  one segmentation model (the disc) with many biomarker calculations, but it is not an end-to-end
  pipeline, since artery/vein masks come from elsewhere. It is catalogued here because in practice
  it is used as the biomarker half of a pipeline, most often paired with LUNet.
- The package can download the external test sets used in the LUNet paper (Crop_HRF, INSPIRE, UNAF)
  through its `PVBMDataDownloader`. Those datasets keep their own licenses, which are not restated
  by the downloader — check each one before using the images in a publication.

---

**Links and license last checked:** 2026-09-10
