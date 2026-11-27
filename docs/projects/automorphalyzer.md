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
| [AutoMorph artery/vein](../models/automorph-artery-vein.md) | Arteries against veins | Borrowed from AutoMorph, which retrained [BF-Net](../models/bf-net.md)'s network from [Learning-AVSegmentation](https://github.com/rmaphoh/Learning-AVSegmentation) (GPL-3.0) |
| [AutoMorph disc-and-cup model](../models/automorph-disc-cup.md) | Optic disc and cup | Borrowed via AutoMorph, which retrained the [lwnet](../models/lwnet.md) architecture (MIT) for this task |
| [QuickQual-MEME](../models/quickqual-meme.md) — **not the [three-class classifier](../models/quickqual.md)** | Image quality, as one probability that the photograph is bad | Borrowed from [QuickQual](https://github.com/justinengelmann/QuickQual), which states no license. *(This atlas's observation: `preprocess/preprocess.py` builds a frozen DenseNet121, selects nine of its features by index, and applies the ten numbers of QuickQual-MEME written out in the source. The three-class support vector machine QuickQual's page describes is never downloaded and never loaded)* |

The quality stage is the visible difference, and it differs in two ways rather than one.
AutoMorph's EyeQ-based module graded images Good, Usable or Reject and dropped some of them before
segmentation; here every image goes through the pipeline and receives a single number —
`QuickQual_quality`, the probability that the photograph is bad — in the output file instead. That
moves the decision from the software to the analyst, which is a defensible choice but means the
output table contains rows that AutoMorph would have discarded.

**The three-way distinction disappears entirely.** The variant used here emits one probability and
no classes, so nothing in this pipeline distinguishes a merely *usable* photograph from a good one;
that judgement is left to whoever reads the column, with no threshold recommended anywhere in the
repository. Nothing downstream reads the column either: `measure.py` merges it into the results
table and no code path filters on it.

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
| [Fractal dimension](../biomarkers/density.md), [vessel density](../biomarkers/density.md), [global vessel calibre](../biomarkers/calibre.md) | Prior literature, as in AutoMorph | [retipy](retipy.md) via AutoMorph | Unchanged, but computed for the whole image only — not for zones B and C |
| [Tortuosity](../biomarkers/tortuosity.md) (distance, and density) | Prior literature | retipy via AutoMorph | **Corrected.** The authors state AutoMorph extracted some vessel segments incorrectly, exaggerating tortuosity; segment extraction was rewritten with Numba and a depth-first search. Computed across all zones |
| Tortuosity (squared curvature) | Prior literature | retipy via AutoMorph | **Removed** as redundant with the other tortuosity measures |
| [Local calibre](../biomarkers/calibre.md) | Prior literature | retipy via AutoMorph | Corrected and made faster |
| [CRAE, CRVE](../biomarkers/calibre.md) | Knudtson formula only | retipy via AutoMorph | **Hubbard formula removed.** Measured in zones B and C only |
| [Arteriovenous ratio (AVR)](../biomarkers/calibre.md) | Ratio of the above | — | Added, in zones B and C |
| Quality (probability that the photograph is bad) | [QuickQual-MEME](../models/quickqual-meme.md) | [QuickQual](https://github.com/justinengelmann/QuickQual) | Reused, and written into the collated results file as `QuickQual_quality`. Never thresholded, and never read again by the pipeline |

All measurements are in pixels at a fixed working size of 912×912, because the pipeline assumes no
knowledge of pixel resolution. Its authors note that both codebases measure at that universal size,
so values remain comparable between AutoMorph and AutoMorphalyzer populations — a useful property,
but it is not the same as physical units, and AutoMorph's micron-based columns are.

Failures are recorded rather than hidden: a traceback goes to the terminal and to a log file under
`M3`, and affected metrics are written as `-1` in the output CSV. Filter on that before analysis.

### 6.1 Every column it writes

*Added 2026-11-22.* Every number the implementation returns, under its own name, beside the
canonical name it answers to — or, where it answers to none, the nearest one and what keeps
it from being that name.

<!-- generated: columns -->
**66 columns**: 40 answer to a canonical name exactly, 23 are close to one and 3 to none. A close name is a pointer for a reader, never a mapping: nothing is compared against it. Rendered from the naming table in `src/biomarkers/automorphalyzer.py` by `python -m biomarkers.pages`.

| Its column | Canonical name | Match | What differs |
| --- | --- | :-: | --- |
| `fractal_dimension@whole_binary` | `density/box-counting/vessels` | exact |  |
| `vessel_density@whole_binary` | `density/over-image/vessels` | exact |  |
| `average_global_calibre@whole_binary` | `calibre/width/vessels/length-weighted` | exact |  |
| `tortuosity_distance@whole_binary` | `tortuosity/hart-tau1/vessels/mean` | exact |  |
| `tortuosity_density@whole_binary` | `tortuosity/grisan-density/vessels/mean` | exact |  |
| `average_local_calibre@whole_binary` | `calibre/width/vessels/length-weighted` | close | a mean over every width sample along every vessel, branch points left out; `average_global_calibre` is the column named this |
| `CRAE_Knudtson@whole_binary` | `calibre/CRE-knudtson/artery/B` | close | computed over the whole frame on the vessels map; an equivalent is defined in a zone |
| `CRVE_Knudtson@whole_binary` | `calibre/CRE-knudtson/vein/B` | close | computed over the whole frame on the vessels map; an equivalent is defined in a zone |
| `CRAE_Knudtson@B_binary` | `calibre/CRE-knudtson/artery/B` | close | Knudtson's arterial pairing applied to the vessels map, which upstream drops from its table |
| `CRVE_Knudtson@B_binary` | `calibre/CRE-knudtson/vein/B` | close | Knudtson's venular pairing applied to the vessels map, which upstream drops from its table |
| `tortuosity_distance@B_binary` | `tortuosity/hart-tau1/vessels/B/mean` | exact |  |
| `tortuosity_density@B_binary` | `tortuosity/grisan-density/vessels/B/mean` | exact |  |
| `average_local_calibre@B_binary` | `calibre/width/vessels/B/length-weighted` | close | a mean over every width sample along every vessel in the zone, branch points left out |
| `CRAE_Knudtson@C_binary` | `calibre/CRE-knudtson/artery/C` | close | Knudtson's arterial pairing applied to the vessels map, which upstream drops from its table |
| `CRVE_Knudtson@C_binary` | `calibre/CRE-knudtson/vein/C` | close | Knudtson's venular pairing applied to the vessels map, which upstream drops from its table |
| `tortuosity_distance@C_binary` | `tortuosity/hart-tau1/vessels/C/mean` | exact |  |
| `tortuosity_density@C_binary` | `tortuosity/grisan-density/vessels/C/mean` | exact |  |
| `average_local_calibre@C_binary` | `calibre/width/vessels/C/length-weighted` | close | a mean over every width sample along every vessel in the zone, branch points left out |
| `fractal_dimension@whole_artery` | `density/box-counting/artery` | exact |  |
| `vessel_density@whole_artery` | `density/over-image/artery` | exact |  |
| `average_global_calibre@whole_artery` | `calibre/width/artery/length-weighted` | exact |  |
| `tortuosity_distance@whole_artery` | `tortuosity/hart-tau1/artery/mean` | exact |  |
| `tortuosity_density@whole_artery` | `tortuosity/grisan-density/artery/mean` | exact |  |
| `average_local_calibre@whole_artery` | `calibre/width/artery/length-weighted` | close | a mean over every width sample along every vessel, branch points left out; `average_global_calibre` is the column named this |
| `CRAE_Knudtson@whole_artery` | `calibre/CRE-knudtson/artery/B` | close | computed over the whole frame on the artery map; an equivalent is defined in a zone |
| `CRVE_Knudtson@whole_artery` | `calibre/CRE-knudtson/vein/B` | close | computed over the whole frame on the artery map; an equivalent is defined in a zone |
| `CRAE_Knudtson@B_artery` | `calibre/CRE-knudtson/artery/B` | exact |  |
| `CRVE_Knudtson@B_artery` | `calibre/CRE-knudtson/vein/B` | close | Knudtson's venular pairing applied to the artery map, which upstream drops from its table |
| `tortuosity_distance@B_artery` | `tortuosity/hart-tau1/artery/B/mean` | exact |  |
| `tortuosity_density@B_artery` | `tortuosity/grisan-density/artery/B/mean` | exact |  |
| `average_local_calibre@B_artery` | `calibre/width/artery/B/length-weighted` | close | a mean over every width sample along every vessel in the zone, branch points left out |
| `CRAE_Knudtson@C_artery` | `calibre/CRE-knudtson/artery/C` | exact |  |
| `CRVE_Knudtson@C_artery` | `calibre/CRE-knudtson/vein/C` | close | Knudtson's venular pairing applied to the artery map, which upstream drops from its table |
| `tortuosity_distance@C_artery` | `tortuosity/hart-tau1/artery/C/mean` | exact |  |
| `tortuosity_density@C_artery` | `tortuosity/grisan-density/artery/C/mean` | exact |  |
| `average_local_calibre@C_artery` | `calibre/width/artery/C/length-weighted` | close | a mean over every width sample along every vessel in the zone, branch points left out |
| `fractal_dimension@whole_vein` | `density/box-counting/vein` | exact |  |
| `vessel_density@whole_vein` | `density/over-image/vein` | exact |  |
| `average_global_calibre@whole_vein` | `calibre/width/vein/length-weighted` | exact |  |
| `tortuosity_distance@whole_vein` | `tortuosity/hart-tau1/vein/mean` | exact |  |
| `tortuosity_density@whole_vein` | `tortuosity/grisan-density/vein/mean` | exact |  |
| `average_local_calibre@whole_vein` | `calibre/width/vein/length-weighted` | close | a mean over every width sample along every vessel, branch points left out; `average_global_calibre` is the column named this |
| `CRAE_Knudtson@whole_vein` | `calibre/CRE-knudtson/artery/B` | close | computed over the whole frame on the vein map; an equivalent is defined in a zone |
| `CRVE_Knudtson@whole_vein` | `calibre/CRE-knudtson/vein/B` | close | computed over the whole frame on the vein map; an equivalent is defined in a zone |
| `CRAE_Knudtson@B_vein` | `calibre/CRE-knudtson/artery/B` | close | Knudtson's arterial pairing applied to the vein map, which upstream drops from its table |
| `CRVE_Knudtson@B_vein` | `calibre/CRE-knudtson/vein/B` | exact |  |
| `tortuosity_distance@B_vein` | `tortuosity/hart-tau1/vein/B/mean` | exact |  |
| `tortuosity_density@B_vein` | `tortuosity/grisan-density/vein/B/mean` | exact |  |
| `average_local_calibre@B_vein` | `calibre/width/vein/B/length-weighted` | close | a mean over every width sample along every vessel in the zone, branch points left out |
| `CRAE_Knudtson@C_vein` | `calibre/CRE-knudtson/artery/C` | close | Knudtson's arterial pairing applied to the vein map, which upstream drops from its table |
| `CRVE_Knudtson@C_vein` | `calibre/CRE-knudtson/vein/C` | exact |  |
| `tortuosity_distance@C_vein` | `tortuosity/hart-tau1/vein/C/mean` | exact |  |
| `tortuosity_density@C_vein` | `tortuosity/grisan-density/vein/C/mean` | exact |  |
| `average_local_calibre@C_vein` | `calibre/width/vein/C/length-weighted` | close | a mean over every width sample along every vessel in the zone, branch points left out |
| `AVR_B` | `calibre/AVR-knudtson/both/B` | exact |  |
| `AVR_C` | `calibre/AVR-knudtson/both/C` | exact |  |
| `CDR_vertical` | `landmarks/CDR-vertical` | exact |  |
| `CDR_horizontal` | `landmarks/CDR-horizontal` | exact |  |
| `disc_height` | `landmarks/disc-diameter-vertical` | exact |  |
| `disc_width` | `landmarks/disc-diameter-horizontal` | exact |  |
| `cup_height` | `landmarks/cup-diameter-vertical` | exact |  |
| `cup_width` | `landmarks/cup-diameter-horizontal` | exact |  |
| `cup_centre_x` | — | none | a pixel position; the catalogue has no position for the cup |
| `cup_centre_y` | — | none | a pixel position; the catalogue has no position for the cup |
| `macular_centred` | `landmarks/centring` | exact |  |
| `laterality` | — | none | which eye, a word, inferred from where the vessels are; no canonical name |
<!-- /generated -->

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
  against AutoMorph is still to be published. *Our measurement, on the
  [synthetic benchmark](../benchmarks/biomarker-synthetic-results.md)'s run of 2026-11-22:* on
  drawn shapes its mean arc over chord is 15–23% from the geometry at worst and moves by at most
  26% as the picture turns, where AutoMorph's reaches 161 times the true value and moves by up to
  640% — consistent with the repair, on drawings rather than photographs.
- **What the code shows:** the ordering repair is real — `_reorder_coords` in
  `automorph/measure/get_vessel_coords.py` walks each branch depth-first from an endpoint, after
  branch points are erased and branches under 10 pixels dropped.
- **Consequence for a reader:** tortuosity from this pipeline is not comparable with tortuosity from
  AutoMorph, nor with [AutoMorphClass](automorphclass.md), which fixed the same defect separately.

### 8.2 The tortuosity-density formula is knowingly left incorrect

- **What is wrong:** Grisan's formula multiplies the amplitude sum by `(n−1)/n`; this pipeline adds
  it, inherited from retipy. Its own source states the position outright:

  ```python
  # return ((n - 1)/curve_length)*sum_segments  # This is the proper formula
  return (n - 1)/n + (1/curve_length)*sum_segments # This is not
  ```

- **What it affects:** the tortuosity-density column. Because the amplitude term carries units of
  1/length and is numerically small, the reported value is dominated by the additive constant — that
  is, mostly a function of how many curvature sign changes were counted.
- **Status:** open, and deliberate: the correct formula is written out and commented, presumably to
  keep continuity with AutoMorph's output. The final vessel stretch after the last inflection is
  also still dropped, and whole-image aggregation is still an unweighted mean over vessels. See
  [vessel-tracing.md](../biomarkers/vessel-tracing.md) section 6.

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
- **What this atlas measures of it.** *Our observation, 2026-11-22.* Its `feature_measurements.csv`
  carries two columns no measuring call returns, `AVR_B` and `AVR_C`, which `merge_results` derives
  as the zone's artery-map CRAE over its vein-map CRVE. This atlas's adapter now derives them the
  same way. When both equivalents fail, both are −1 and the ratio is a positive 1, which it keeps.

---

**Links and license last checked:** 2026-09-10
