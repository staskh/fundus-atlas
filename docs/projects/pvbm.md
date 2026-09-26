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
- **How this atlas runs it:** as a **pinned clone** rather than a pip install, from 2026-09-26.
  Installing it was equivalent and is no longer, for one reason: [OCULARNet](ocularnet.md)'s
  measuring class is a modified copy of PVBM's and imports the unmodified helpers at run time, so
  the two have to agree about which PVBM that is. With a clone both reach the same tree and the run
  records the commit; with an install the answer depended on the environment and was never written
  down.
- **Training code included:** No. The biomarker code needs no training, and the bundled optic disc
  segmenter is shipped as a ready-made ONNX model; training code for it would belong to
  [LUNet](https://github.com/aim-lab/LUNet).

## 2. License

- **Code:** MIT License (`LICENSE` in the repository).
- **Model weights:** No separate license is stated for the optic disc segmenter weights, which are
  downloaded from Google Drive at first use rather than shipped with the package.
- **A licensing trap worth knowing:** those weights are derived from
  [LUNet](../models/lunet.md), whose repository is licensed **CC BY-NC 4.0 — non-commercial**
  (see [the disc model's page](../models/lunetv2-odc.md)). This
  package is MIT, and nothing in it warns about the restriction, so a commercial user relying on
  PVBM's disc segmentation needs to resolve it with the LUNet authors.

## 3. Major publications by the authors

- Fhima J, Van Eijgen J, Stalmans I, Men Y, Freiman M, Behar JA. *[PVBM](../papers/fhima-2022.md):
  A Python Vasculature Biomarker Toolbox Based on Retinal Blood Vessel Segmentation.* In: Computer
  Vision – ECCV 2022 Workshops, Springer, 2023. DOI:
  [10.1007/978-3-031-25066-8_15](https://doi.org/10.1007/978-3-031-25066-8_15) ·
  [arXiv:2208.00392](https://arxiv.org/abs/2208.00392)

The toolbox has grown since that paper (the paper describes eleven biomarkers, the current README
lists fifteen), so the code and the publication do not match exactly.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| [LUNet v2 disc segmenter](../models/lunetv2-odc.md) (`DiscSegmenter`) | Optic disc | Borrowed — the README states it was produced using [LUNet](../models/lunet.md), by the same laboratory. Its training data is Unknown and the file is unversioned |
| Artery and vein segmentation | Arteries and veins | Not included. The user supplies these masks from another project |

This is the important thing to understand about PVBM: the vessel segmentation step, which is where
most of the disagreement between pipelines comes from, is outside the toolbox. Its numbers are only
as good as the masks fed into it, and the source of those masks must be recorded with any result.

## 5. Models introduced here

Not applicable — no new segmentation model is introduced; the disc segmenter is derived from LUNet
(see section 4). For completeness on the borrowed component:

- **Model file:** `lunetv2_odc.onnx`, downloaded on first use by `PVBM/DiscSegmenter.py`.
- **Download URL:** https://drive.google.com/file/d/11GE-M-VtIXb6X7_bU2nwH-8mMrSJAAbY — the
    Google Drive file named in [PVBM issue #5](https://github.com/aim-lab/PVBM/issues/5). The URL
    hardcoded in `PVBM/DiscSegmenter.py` no longer serves anything, so a fresh checkout of PVBM
    cannot fetch its own disc weights. It is not versioned in the repository, so the file
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
| [Area, Length](../biomarkers/vessel-area-and-length.md) | [Martinez-Perez 2000](../papers/martinez-perez-2000.md); [Fhima 2022](../papers/fhima-2022.md) | — | Implemented here (in pixels and square pixels, not physical units) |
| [Tortuosity index, median tortuosity](../biomarkers/tortuosity.md) | Arc-chord ratio; the algorithm is presented as new in [Fhima 2022](../papers/fhima-2022.md) | — | Introduced here |
| [Number of start points, end points, intersection points](../biomarkers/junction-counts.md) | [Martinez-Perez 2000](../papers/martinez-perez-2000.md); [Fhima 2022](../papers/fhima-2022.md) | — | Implemented here |
| [Median branching angle](../biomarkers/bifurcation-angle.md) | [Martinez-Perez 2000](../papers/martinez-perez-2000.md); algorithm presented as new in [Fhima 2022](../papers/fhima-2022.md) | — | Introduced here |
| [Capacity, entropy and correlation fractal dimensions; singularity length](../biomarkers/fractal-dimension.md) | [Stosic 2006](../papers/stosic-2006.md); [Fhima 2022](../papers/fhima-2022.md) | — | Implemented here (box-counting after Chhabra / FracLac, not Stosic's sandbox) |
| [CRAE and CRVE](../biomarkers/central-retinal-equivalents.md) (central retinal arteriolar and venular equivalents) | Knudtson and Hubbard formulas from prior literature | — | Both formulas implemented; the user chooses |
| [Arterio-venous ratio (AVR)](../biomarkers/avr.md) | Ratio of CRAE to CRVE | — | Derived by the user from CRAE and CRVE |

Areas and lengths are reported in pixels, so results are not comparable across cameras or image
sizes without a resolution conversion of the user's own.

## 7. Examples and notebooks

- [`pvbmtutorial.ipynb`](https://github.com/aim-lab/PVBM/blob/main/pvbmtutorial.ipynb) — start here.
  It walks through disc segmentation, region-of-interest extraction, and the geometrical and fractal
  biomarkers on a sample image, which is also the clearest statement of the expected input format.

## 8. Known defects

- **`compute_perimeter_` empties the mask it is given.** *Our finding, 2026-09-26, from reading
  `PVBM/helpers/perimeter.py`.* The helper walks the vasculature and sets each pixel it visits to
  zero, so it returns its input erased. The deprecated `GeometricalAnalysis.compute_perimeter`
  conceals this by passing a copy; anyone calling the helper directly — which is now the only way
  to get a perimeter, since the replacement class exposes none — gets an emptied array back with no
  error and no warning. A caller who then measures anything else from the same array gets an area
  of zero and a fractal analysis that fails an assertion, which is how this was found here. Not
  reported upstream by this atlas as of 2026-09-26. This repository passes a copy, in
  `src/upstreams/pvbm.py`.

### 8.1 Two classes called `GeometricalVBMs`, one of them deprecated

At the pinned commit the package ships **both** `PVBM/GeometricalAnalysis.py` and
`PVBM/GeometryAnalysis.py`, and both export a class named `GeometricalVBMs`. The first warns on
construction that it "is deprecated and will be removed in version 3.0", and names the second as
its replacement. An import that differs by one word therefore decides which of two different
measuring codes runs, and nothing but the warning distinguishes them.

**This atlas measures with `GeometryAnalysis`**, from 2026-09-26. It is not a rename, and what
changes is worth listing because it changes the evidence:

| | `GeometricalAnalysis` (deprecated) | `GeometryAnalysis` (used here) |
| --- | --- | --- |
| Shape of the interface | five methods, called separately | one `compute_geomVBMs`, returning a list of eight |
| Needs the optic disc | no | **yes** — centre and radius |
| How it finds vessels | over the whole mask | walks each tree from where it leaves the disc |
| Branching angle | mean, standard deviation **and** median | median only |
| Perimeter | `compute_perimeter` | **none** — see the defect above |
| New quantities | — | a tortuosity index, and a count of start points |

Two consequences for anyone reading numbers from this atlas. **A class whose vessels do not reach
the optic disc now measures as zero** rather than being measured where it lies — there are no
trunks to walk — which is a property of the measurement and not a failure. And the mean and the
standard deviation of the branching angle are **gone from the evidence**, because the code that
produced them no longer runs here.

## 9. Notes

- **Scope caveat.** By this atlas's definition PVBM sits at the boundary of a project: it combines
  one segmentation model (the disc) with many biomarker calculations, but it is not an end-to-end
  pipeline, since artery/vein masks come from elsewhere. It is catalogued here because in practice
  it is used as the biomarker half of a pipeline, most often paired with LUNet.
- The package can download the external test sets used in the LUNet paper ([Crop_HRF](../datasets/hrf.md), [INSPIRE](../datasets/inspire-avr.md), [UNAF](../datasets/unaf.md))
  through its `PVBMDataDownloader`. Those datasets keep their own licenses, which are not restated
  by the downloader — check each one before using the images in a publication.

---

**Links and license last checked:** 2026-09-26
