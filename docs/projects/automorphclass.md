# AutoMorphClass

AutoMorphClass packages the [AutoMorph](automorph.md) pipeline as a single PyTorch module. Where
AutoMorph is run as a set of shell scripts over a folder of images and produces CSV files,
AutoMorphClass is called like any other neural network: hand it a batch of image tensors, get back a
tensor or dictionary of vascular features. Its purpose is integration — dropping retinal feature
extraction into an existing training or analysis pipeline without shelling out to another program.

It is a thin research wrapper, not a maintained product: one contributor, no publication, and a
license question described in section 2.

## 1. Code reference

- **Repository:** https://github.com/kikatuso/AutoMorphClass
- **Version described here:** commit `8f4d18fe` (2026-05-14). No tags or releases are published; the
  package version in `pyproject.toml` is 0.1.0.
- **Most recent commit:** 2026-05
- **Training code included:** No — inference only. The README states the model runs in evaluation
  mode and is designed for inference.
- **Language and how it runs:** Python, installed with `pip install -e .` after cloning, then
  `from pytorch_automorph import AutoMorphModel`. The module takes a `(B, 3, H, W)` tensor on the
  same device as the model and returns either a `(B, F)` feature tensor or a dictionary of named
  scalars.

## 2. License

- **Code:** **Unclear.** The README says "This project is licensed under the MIT License" and links
  to a `LICENSE` file, and `pyproject.toml` declares `license = { text = "MIT" }` — but no LICENSE
  file exists in the repository, so the link is broken and GitHub reports no license. Treat the MIT
  claim as the authors' stated intent, and ask them to add the file before relying on it.
- **Model weights:** No license stated. This is the more serious question: the repository
  redistributes AutoMorph's trained weights (section 5), which derive from a GPL-3.0 project
  upstream, inside a package that declares itself MIT. Anyone planning to redistribute this package
  should resolve that before doing so.

## 3. Major publications by the authors

None found. `pyproject.toml` names Zuzanna Wakefield-Skórniewska (Nuffield Department of Population
Health, University of Oxford) as author. The README asks readers to refer to the original AutoMorph
work:

- Zhou Y, Wagner SK, Chia MA, Zhao A, Xu M, Struyven R, Alexander DC, Keane PA, et al. *AutoMorph:
  Automated Retinal Vascular Morphology Quantification Via a Deep Learning Pipeline.* Translational
  Vision Science & Technology 2022;11(7):12.
  [Article](https://tvst.arvojournals.org/article.aspx?articleid=2783477) ·
  [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| Vessel segmenter (run at 912 px) | Blood vessels | Borrowed from AutoMorph, whose weights are copied into this repository |
| Artery/vein segmenter (720 px) | Arteries against veins | Borrowed from AutoMorph |
| Optic disc and cup segmenter (512 px) | Optic disc and cup | Borrowed from AutoMorph, which took it from [lwnet](lwnet.md) |
| Skeletonisation | Vessel skeleton, a processing step rather than anatomy | Included in the package |

The pipeline is AutoMorph's, reimplemented as PyTorch classes
(`Vessel_segmentation.py`, `AV_classification.py`, `Optic_disc_and_cup.py`) with the stage
resolutions fixed in code. A `lightweight=True` flag uses a single checkpoint instead of the full
ensemble, which the README describes as trading accuracy for speed — a meaningful difference to
record with any result, since AutoMorph's published behaviour is the ensemble.

## 5. Models introduced here

No new model is introduced; AutoMorph's weights are vendored into the package.

### 5.1 Vendored AutoMorph weights

- **Training data:** unchanged from AutoMorph — see [automorph.md](automorph.md) section 5.
- **Weights publicly available:** Yes, committed inside this repository.
- **Download URL:**
  https://github.com/kikatuso/AutoMorphClass/tree/main/src/pytorch_automorph/segmentation_models/checkpoints
  — with subfolders `vessel_segmentation/`, `AV_classification/`, `optic_disc_and_cup/` and
  `skeletonisation/`. The vessel checkpoints keep AutoMorph's `G_best_F1_epoch.pth` filenames, and
  the loader globs for several of them, which is how the ensemble is assembled.
- **Training code:** Not in this repository.

## 6. Biomarkers computed

The feature calculation is a reimplementation of AutoMorph's, in
`src/pytorch_automorph/feature_calculation.py` and `tortuosity_utils.py`.

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| Vascular features returned as a named feature vector — the set follows AutoMorph's measurements (calibre, tortuosity, density, fractal dimension, disc and cup geometry) | Prior literature, as cited by AutoMorph | [retipy](retipy.md) via AutoMorph | Reimplemented in this package's own code |

Two flags control coverage: `include_zones`, `include_artery_vein` and `include_optic_disc` switch
whole families of features on and off, so the width of the returned tensor depends on
configuration. Because the feature vector is positional when `return_as_tensor=True`, record the
flags and the version alongside any results; use `return_as_tensor=False` to get named values
instead, which is safer for analysis.

Exact per-feature agreement with AutoMorph has not been established, here or by the authors. Treat
these as AutoMorph-derived features, not as AutoMorph's numbers.

## 7. Examples and notebooks

- [`example.ipynb`](https://github.com/kikatuso/AutoMorphClass/blob/main/example.ipynb) — start
  here. It loads an image from `example_images/`, runs the module and shows how to read the
  extracted features.
- `example.py` — the same flow as a plain script, for use outside a notebook.

## 8. Known defects

### 8.1 The inherited tortuosity defect, claimed fixed

- **What was wrong:** the vessel-segment ordering bug in AutoMorph's tortuosity code — see
  [retipy.md](retipy.md) section 8.1 for the root cause.
- **What the author states:** in [rmaphoh/AutoMorph#18](https://github.com/rmaphoh/AutoMorph/issues/18)
  the author describes this project as including "fixed tortuosity measures (as the original
  pipeline has a bug when extracting these)".
- **Status:** claimed fixed; **unverified and undocumented in the code.** No comment or note
  describing the change was found in `tortuosity_utils.py` or `feature_calculation.py`, so a reader
  cannot tell from the source what was altered or how it differs from the fix in
  [AutoMorphalyzer](automorphalyzer.md).
- **Consequence for a reader:** three pipelines (AutoMorph, AutoMorphalyzer, this one) now compute
  tortuosity differently, with no cross-validation between them. Do not pool tortuosity values
  across them.

### 8.2 License file missing

Recorded in section 2 rather than here, but it belongs on any list of things to fix: the declared
MIT license has no LICENSE file, and the package redistributes weights derived from a GPL-3.0
project.

## 9. Notes

- **Batching is the point of this project.** It is the only entry in this catalogue that runs as an
  `nn.Module` on a tensor batch, which is what makes it usable inside a deep-learning training loop
  — for instance to compute retinal features as an auxiliary target.
- Single-contributor repository, first commit history under a year old at the time of checking, no
  tests or published validation. Suitable for research use with verification of your own; not a
  substitute for the upstream pipeline where provenance of numbers matters.

---

**Links and license last checked:** 2026-09-10
