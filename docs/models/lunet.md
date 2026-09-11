# LUNet

LUNet segments arterioles and venules — the small arteries and veins — in high-resolution fundus
photographs. Its authors' argument is that resolution matters: models trained on the small, older
public datasets learn to find only the larger vessels, so LUNet was trained on a purpose-built
high-resolution dataset from Leuven.

**Its license is the thing to know first: CC BY-NC 4.0, non-commercial.** Two pipelines in this
atlas distribute weights derived from it, and that restriction travels with them.

## 1. Code reference

- **Repository:** https://github.com/aim-lab/LUNet
- **Version described here:** commit `0b0f383e` (2024-12-11). No tags or releases.
- **Most recent commit:** 2024-12
- **Training code included:** Yes, in this repository — `main.py` trains the model in
  TensorFlow/Keras, with `eval_all.py` for evaluation and `install_pvbm_datasets.py` to fetch the
  external test sets.
- **Language and how it runs:** Python with TensorFlow. Unlike every other model in this catalogue,
  which are PyTorch.

## 2. License

- **Code:** **Creative Commons Attribution-NonCommercial 4.0 International** (`LICENSE` in the
  repository). A CC licence on code is unusual and awkward, but the operative term is plain:
  **no commercial use**. GitHub reports this as an unrecognised license, so automated scans will
  show "NOASSERTION" and miss the restriction.
- **Model weights:** Covered by the same repository license, in the absence of a separate statement.

## 3. Major publications by the authors

- Fhima J, Van Eijgen J, Billen Moulin-Romsée M-I, Brackenier H, Kulenovic H, Debeuf V, Vangilbergen
  M, Freiman M, Stalmans I, Behar JA. *LUNet: deep learning for the segmentation of arterioles and
  venules in high resolution fundus images.* Physiological Measurement, 2024. DOI:
  [10.1088/1361-6579/ad3d28](https://doi.org/10.1088/1361-6579/ad3d28)

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** artery and vein masks, produced as separate outputs.
- **Input grid:** 1472×1472 — the largest grid of any model in this catalogue, which is the point
  of the model: arterioles and venules only survive resampling at high resolution. Note it does not
  match the 1444×1444 native size of its training images, so even UZLF photographs are resampled.
- **Output grid:** artery and vein masks at 1472×1472.
- **Grid set in:** `final_shape = 1472` in `main.py`, commented "Shape on which the images will be
  processed by the model", and used to build the Keras input layer.
- **Input expected:** high-resolution fundus photographs. The training data is the UZLF
  ([Leuven-Haifa](../datasets/leuven-haifa.md)) dataset at 1444×1444; behaviour on smaller or lower-resolution images is not
  characterised here.
- **Preprocessing in the published code:** dataset preparation expects `images`, `artery` and
  `veins` folders per split, following the UZLF layout.

## 5. Architecture

- **Family:** a U-Net variant, implemented in TensorFlow/Keras with custom loss and metric modules
  under `src/`.
- **Parameters:** Unknown.
- **Single model or ensemble:** a single model; the repository ships one checkpoint.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [UZLF](../datasets/leuven-haifa.md) ([Leuven-Haifa](../datasets/leuven-haifa.md)), 1444×1444 | Training, validation and test | The dataset's authors at Leuven | Yes — `UZLF_TRAIN`, `UZLF_VAL`, `UZLF_TEST` |
| [Crop_HRF](../datasets/hrf.md), [INSPIRE](../datasets/inspire-avr.md), [UNAF](../datasets/unaf.md) | External test only, fetched through PVBM | Their own authors | Yes, test only |

UZLF cannot be used to benchmark these weights. The three external sets were used by the authors as
held-out tests, which makes them a reasonable basis for comparison but no longer a blind one.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://github.com/aim-lab/LUNet/blob/main/lunet_modelbest.h5 — committed in the
  repository. A differently-purposed relative, `lunetv2_odc.onnx`, segments the optic disc and is
  catalogued separately at [lunetv2-odc.md](lunetv2-odc.md).
- **Format and size:** Keras HDF5 (`.h5`).
- **Files in an ensemble:** one.

## 8. Performance as reported by the authors

The paper reports artery-vein segmentation performance on UZLF and on the external test sets, and
the repository links to Papers-with-Code leaderboards for artery-vein segmentation. Numbers are in
the paper and are not restated here.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued pipeline runs this artery/vein model. Three distribute or use its disc-segmenting relative: see [lunetv2-odc.md](lunetv2-odc.md) | — |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Not wired into the pipeline as far as could be established | Republishes `lunet_modelbest.h5` as a release asset |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- **The non-commercial term propagates.** PVBM is MIT-licensed but downloads a model derived from
  this work at runtime, and OCULAR uses the same segmenter. Anyone using either pipeline
  commercially needs to resolve that, and neither pipeline's own license statement warns about it.
  See [lunetv2-odc.md](lunetv2-odc.md).
- **High-resolution by design.** Trained at 1444×1444 on arterioles and venules, so behaviour on
  small or low-resolution photographs is not characterised.
- The only TensorFlow model in this catalogue, which makes it awkward to run beside the PyTorch
  pipelines.

---

**Links and license last checked:** 2026-09-10
