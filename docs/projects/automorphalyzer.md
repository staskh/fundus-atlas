# AutoMorphalyzer

AutoMorphalyzer is a rewritten version of [AutoMorph](automorph.md), produced at the University of
Edinburgh because its authors wanted a faster, more usable and — in their own words — "correct"
version of that pipeline. It performs the same job: colour-fundus photographs in, a table of
vascular measurements out, using the same segmentation models. What changed is everything around
them — how it is run, how quality is handled, and how the measurements are computed.

Two changes matter most to anyone comparing results. First, its authors state that AutoMorph
extracted some vessel segments incorrectly, which exaggerated tortuosity, and that this is
corrected here. Second, it keeps only the Knudtson formula for calibre equivalents and drops the
Hubbard one. Numbers from the two pipelines are therefore not interchangeable, and their authors
say so themselves: the README notes that a comparison between the two is still to be published.

## 1. Code reference

- **Repository:** https://github.com/jaburke166/AutoMorphalyzer
- **Version described here:** commit `e68843e2` (2026-03-24). Releases exist but hold model weights
  rather than versions of the code (see section 5).
- **Most recent commit:** 2026-03
- **Training code included:** No — inference only. Segmentation uses the weights inherited from
  AutoMorph; training those models belongs to
  [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) and
  [lwnet](https://github.com/agaldran/lwnet).
- **Language and how it runs:** Python 3.11 via Miniconda. The user edits two paths in `config.txt`
  (`input_directory`, `output_directory`) and runs `python automorph/main.py`. The authors report
  testing on Windows and macOS, and recommend a GPU for the segmentation stage. Model weights
  download automatically on first run.

## 2. License

- **Code:** Apache License 2.0 (`LICENSE` in the repository), the same license as the AutoMorph
  codebase it adapts.
- **Model weights:** No separate license is stated. The weights are published as assets on this
  repository's own releases, so the repository license is the only statement available. Note that
  the artery/vein and vessel weights derive from a GPL-3.0 project upstream.

## 3. Major publications by the authors

None describing AutoMorphalyzer itself. The README asks users to cite the original AutoMorph paper
and to note that this is an adapted version:

- Zhou Y, Wagner SK, Chia MA, Zhao A, Xu M, Struyven R, Alexander DC, Keane PA, et al. *AutoMorph:
  Automated Retinal Vascular Morphology Quantification Via a Deep Learning Pipeline.* Translational
  Vision Science & Technology 2022;11(7):12.
  [Article](https://tvst.arvojournals.org/article.aspx?articleid=2783477) ·
  [PMC9290317](https://pmc.ncbi.nlm.nih.gov/articles/PMC9290317/)

The authors state the codebase is still in development and that further tests are needed to compare
its output against AutoMorph's. Read any result from it with that caveat attached.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| [SEGAN vessel segmenter](../models/segan-vessel.md) | Blood vessels, one class | Borrowed via AutoMorph, which trained the weights |
| [BF-Net](../models/bf-net.md) | Arteries against veins | Borrowed from [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) (GPL-3.0), via AutoMorph |
| [AutoMorph disc-and-cup model](../models/automorph-disc-cup.md) | Optic disc and cup | Borrowed via AutoMorph, which retrained the [lwnet](../models/lwnet.md) architecture (MIT) for this task |
| [QuickQual](../models/quickqual.md) | Image quality, as a probability of rejection | Borrowed from [QuickQual](https://github.com/justinengelmann/QuickQual), which states no license |

The quality stage is the visible difference. AutoMorph's EyeQ-based module graded images and could
reject them; here every image goes through the pipeline and receives a QuickQual rejection
probability in the output file instead. That moves the decision from the software to the analyst,
which is a defensible choice but means the output table contains rows that AutoMorph would have
discarded.

## 5. Models introduced here

No new model is introduced. The weights are AutoMorph's, repackaged for automatic download.

### 5.1 Repackaged AutoMorph weights

- **Training data:** unchanged from AutoMorph — see [automorph.md](automorph.md) section 5 for the
  datasets behind each model.
- **Weights publicly available:** Yes, downloaded automatically on first run.
- **Download URLs** (release `v1.0`, published 2025-03-12):
  - https://github.com/jaburke166/AutoMorphalyzer/releases/download/v1.0/binary_model_weights.zip
  - https://github.com/jaburke166/AutoMorphalyzer/releases/download/v1.0/arteryvein_model_weights.zip
  - https://github.com/jaburke166/AutoMorphalyzer/releases/download/v1.0/opticdisc_model_weights.zip
- **Also published:** release `v1.0_PVBM` (2025-04-02) carries `lunetv2_odc.onnx` and
  `lunet_modelbest.h5` — the LUNet weights also used by [PVBM](pvbm.md). Whether the main pipeline
  uses them is Unknown; no reference to them was found in `automorph/main.py`.
- **Training code:** Not in this repository.

## 6. Biomarkers computed

The measurement module was rewritten rather than reused, so this is where AutoMorphalyzer and
AutoMorph diverge most.

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| [Fractal dimension](../biomarkers/fractal-dimension.md), [vessel density](../biomarkers/vascular-density.md), [global vessel calibre](../biomarkers/vessel-calibre.md) | Prior literature, as in AutoMorph | [retipy](retipy.md) via AutoMorph | Unchanged, but computed for the whole image only — not for zones B and C |
| [Tortuosity](../biomarkers/tortuosity.md) (distance, and density) | Prior literature | retipy via AutoMorph | **Corrected.** The authors state AutoMorph extracted some vessel segments incorrectly, exaggerating tortuosity; segment extraction was rewritten with Numba and a depth-first search. Computed across all zones |
| Tortuosity (squared curvature) | Prior literature | retipy via AutoMorph | **Removed** as redundant with the other tortuosity measures |
| [Local calibre](../biomarkers/vessel-calibre.md) | Prior literature | retipy via AutoMorph | Corrected and made faster |
| [CRAE, CRVE](../biomarkers/central-retinal-equivalents.md) | Knudtson formula only | retipy via AutoMorph | **Hubbard formula removed.** Measured in zones B and C only |
| [Arteriovenous ratio (AVR)](../biomarkers/avr.md) | Ratio of the above | — | Added, in zones B and C |
| Quality (probability of rejection) | QuickQual | [QuickQual](https://github.com/justinengelmann/QuickQual) | Reused, and written into the collated results file |

All measurements are in pixels at a fixed working size of 912×912, because the pipeline assumes no
knowledge of pixel resolution. Its authors note that both codebases measure at that universal size,
so values remain comparable between AutoMorph and AutoMorphalyzer populations — a useful property,
but it is not the same as physical units, and AutoMorph's micron-based columns are.

Failures are recorded rather than hidden: a traceback goes to the terminal and to a log file under
`M3`, and affected metrics are written as `-1` in the output CSV. Filter on that before analysis.

## 7. Examples and notebooks

- `quickstart.txt` with the bundled `example_data/` — start here. Point `config.txt` at the example
  images and run `python automorph/main.py` to get a full output tree.
- The composite segmentation images written to `{output_directory}/M3/segmentations` — the practical
  way to check the vessel, artery, vein and disc masks by eye for every processed photograph.

## 8. Known defects

### 8.1 The inherited tortuosity defect, reported as fixed here

- **What was wrong:** AutoMorph's tortuosity values are invalidated by the vessel-segment ordering
  bug described in [retipy.md](retipy.md) section 8.1 and
  [automorph.md](automorph.md) section 8.1.
- **What the authors state:** the README says the original codebase "extracted some vessel segments
  incorrectly, leading to exaggerated values in tortuosity" and that this has been corrected, with
  segment extraction rewritten using Numba and a depth-first search. Squared-curvature tortuosity
  was removed as redundant with the other measures, so the affected column no longer exists.
- **Status:** reported fixed by the authors; **not verified** here or, as far as could be
  established, by anyone independent. The authors themselves note that a comparison of output
  against AutoMorph is still to be published.
- **Consequence for a reader:** tortuosity from this pipeline is not comparable with tortuosity from
  AutoMorph, nor with [AutoMorphClass](automorphclass.md), which fixed the same defect separately.

## 9. Notes

- **Resumable by design.** Each stage skips images it has already processed, judged by entries in
  the intermediate CSV files and by the presence of the mask files. Convenient for long runs;
  remember that stale outputs are silently kept, so delete the output tree when changing anything
  that should alter results.
- **Manual correction loop.** Segmentations can be edited by hand in ITK-Snap and fed back in to
  recompute the measurements — the only entry in this catalogue with an explicit human-in-the-loop
  path, and the reason images are downsized to 912×912.
- **Laterality** (left or right eye) is inferred from vessel density on either side of the optic
  cup, not read from image metadata.
- Uncertainty maps from the model ensembles are not saved, unlike in AutoMorph.

---

**Links and license last checked:** 2026-09-10
