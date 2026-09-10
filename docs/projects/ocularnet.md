# OCULARNet (OCULAR)

OCULAR is two things released together: a harmonised collection of publicly available
artery-vein annotations drawn from twenty-one datasets, and **OCULARNet**, an artery-vein
segmentation model trained on it. Its stated design goal separates it from the other entries here —
the authors optimise for the fidelity of the vascular measurements a clinician would derive
(topology, junctions, vessel calibre) rather than for pixel-wise overlap with a reference mask,
arguing that a high Dice score does not guarantee usable biomarkers.

It also segments a fourth class most pipelines ignore: vessel **crossings**, where an artery and a
vein overlap. Those points are where artery/vein classification usually fails, and where
crossing-specific clinical signs are read.

## 1. Code reference

- **Repository:** https://github.com/GonzaloPlaaza/OCULAR
- **Version described here:** commit `34b1ecc3` (2026-08-06). No tags or releases are published.
- **Most recent commit:** 2026-08
- **Training code included:** **Yes** — `train.py` trains artery-vein segmentation models from CSV
  split files, with example split templates under `data_splits/`. This is one of only two entries in
  this catalogue that ships training code.
- **Language and how it runs:** Python with PyTorch. `python inference.py --input_dir data/images
  --output_dir segmentations/ --weights … --device cuda` produces segmentations; `extract_zones.py`
  then derives junction and vessel-zone masks. Input images are expected already cropped to the
  field of view.

## 2. License

- **Code:** **None stated.** The repository contains no LICENSE file and GitHub reports no license,
  which means no permission to reuse or redistribute has been granted, whatever the intent. Ask the
  authors before building on it.
- **Model weights:** No license stated on either Hugging Face repository.
- **Datasets:** each aggregated dataset keeps its own license, and the authors link to the original
  source of every one rather than redistributing images. The optic-disc and field-of-view masks they
  add are their own contribution, distributed from Google Drive.

## 3. Major publications by the authors

Unknown — no publication was found, and the repository carries clear signs of being under peer
review: the README's own clone instructions point at an anonymised repository (`anon-retina/OCULAR`),
the weights are hosted under an anonymous Hugging Face account, and the release of new annotations
is promised "upon paper publication". Cite the repository for now, and check for a paper before
relying on it.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| OCULARNet (`base_unet_repvgg_b3`) | Four classes: background, artery, vein, crossings | Introduced here |
| OCULARNet-nano (`base_unet_repvgg_a0`), a five-fold ensemble | The same four classes, from a smaller backbone | Introduced here |
| Optic disc segmenter (`utils/DiscSegmenter.py`) | Optic disc | Borrowed — the same disc segmenter used by [PVBM](pvbm.md) |

## 5. Models introduced here

### 5.1 OCULARNet and OCULARNet-nano

- **Training data:** the OCULAR training collection — fourteen public datasets: AVRDB, DRIVE,
  ENRICH, FIVES-AV, Fundus-AVSeg, GAVE, GRAPE, HRF, INSPIRE, LES-AV, Leuven-Haifa, MAGREBHIA,
  MESSIDOR-AV and PAPILA. Evaluation is split deliberately into in-distribution test sets
  (DualModal, UNAF) and out-of-distribution ones, further divided into near-OoD (TREND-AV,
  IOSTAR-AV, MBRSET) and far-OoD (AV-WIDE, RAVIR). The README tabulates each dataset's image count,
  field of view, resolution, country and pathologies, which makes it the most explicit statement of
  training-data diversity of any entry in this catalogue.
- **Weights publicly available:** Yes.
- **Download URLs:**
  - OCULARNet: https://huggingface.co/Anon-User-Retina/OCULARNet/resolve/main/OCULARNet.pth
  - OCULARNet-nano, five folds:
    https://huggingface.co/Anon-User-Retina/OCULARNet-nano/resolve/main/nano_f1.pth through
    `nano_f5.pth` in the same repository
  - Both accounts are anonymous review accounts and may be renamed once a paper appears.
- **Training code:** Yes, `train.py` in this repository.

## 6. Biomarkers computed

OCULAR does not output a biomarker table. `extract_zones.py` produces the intermediate masks from
which biomarkers are computed, and it does so using **PVBM's code**: the file
`utils/GeometricalVBMs.py` is a modified copy of PVBM's class and imports `PVBM.helpers.tortuosity`,
`PVBM.helpers.perimeter`, `PVBM.helpers.branching_angle` and PVBM's graph regularisation at runtime.

| Output | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| Bifurcation points, arteries and veins separately, as 20-pixel regions of interest | The PVBM method | [PVBM](pvbm.md) (MIT) | Reused, via a modified copy of PVBM's `GeometricalVBMs` |
| Major vasculature regions, arteries and veins | This project | — | Two modes: morphological opening scaled to optic disc size, or largest connected components; the authors recommend a footprint width of 2–4 with visual inspection |
| Crossing regions of interest | This project | — | Circular masks around the centroids of detected crossings — enabled by the crossings class, and not available from the other pipelines here |
| Tortuosity, perimeter, branching angles | Prior literature via PVBM | PVBM | Imported from PVBM directly |

So OCULAR's numbers are, by construction, PVBM's numbers computed on OCULARNet's segmentations.
That makes them directly comparable to PVBM results on other segmentations, and it means the
segmentation is the only variable being changed — which is precisely the comparison the authors set
out to make.

## 7. Examples and notebooks

- The inference command in the README against the provided
  [example data](https://drive.google.com/file/d/1x01n3sbI_QUy8DxjQ2KSqKypHZpYw8Wy/view) — start
  here to get artery, vein and crossings masks from a handful of images.
- `extract_zones.py --data_root … --image_type ODC --fw 3` — the second step, and the one to inspect
  visually; the authors explicitly recommend checking the major-vessel masks by eye rather than
  trusting the default footprint width.
- `annotation-tool.html` — a self-contained browser tool for annotating artery-vein masks, useful if
  you need to produce or correct reference annotations of your own.

## 8. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Nothing in this
project's issue tracker or code was found to change the numbers a user would report.

## 9. Notes

- **Scope note.** By this atlas's definition OCULAR sits at the boundary of a project: it combines
  segmentation models with the region and junction extraction that biomarkers are computed from, but
  the biomarker step itself is PVBM's. It is catalogued here because it is used as a pipeline, and
  it will also belong in the dataset catalogue for the OCULAR annotation collection.
- **Promised release.** The authors state that upon publication they will release artery-vein
  segmentations for 1,791 images across several open datasets, produced with OCULARNet and
  semi-automatically refined against ground-truth binary vessel annotations. If that lands, it
  becomes a dataset entry of its own.
- The `--ensemble` flag runs the five nano folds together; a single-fold run and an ensemble run are
  different models and should not be pooled in one analysis.
- Absent a license (section 2), this is currently readable but not reusable. That is the single
  thing to watch on this project.

---

**Links and license last checked:** 2026-09-10
