# Retina-MVP artery/vein head

Given a colour-fundus photograph, this network labels every pixel as background, artery or vein. It
is one of three networks shipped inside a single checkpoint by an independent developer's
"Retinal Vessel Analysis Pipeline — MVP": the other two mark the vessels as one class and their
centrelines, and are separate models (section 11).

What it does differently from the models already catalogued here is mostly a matter of packaging
rather than method: it is an off-the-shelf U-Net with a ResNet-34 encoder, trained by a script whose
default is three epochs, on images the author does not name. It is documented here because it is
publicly downloadable, runs in a browser demo anyone can use on their own photographs, and presents
its output as clinical decision support — and because **what it was trained on cannot be
established**, which is the single most important thing a reader can know about it.

## 1. Code reference

- **Repository:** https://github.com/adityaranjan2005/Retina-mvp — the training and inference code.
  A second copy of the model definition and the inference path is published as a Hugging Face Space:
  https://huggingface.co/spaces/adityaranjan2005/retinal-vessel-analysis
- **Version described here:** commit `893e2152` (2025-12-31) of the repository's `master` branch, and
  Space revision `ce96de16` (2025-12-30).
- **Most recent commit:** 2025-12
- **Training code included:** Yes, in this repository — `src/train.py`, with `--epochs` defaulting to
  **3** and no train/validation/test split. The README itself says that production use would want
  50 to 100 epochs and a split.
- **Language and how it runs:** Python with PyTorch and
  [segmentation-models-pytorch](https://github.com/qubvel-org/segmentation_models.pytorch);
  `python -m src.infer --checkpoint outputs/mvp_model.pt`, or through the Gradio demo, which runs on
  CPU.

## 2. License

- **Code:** **None stated.** The repository carries no licence file and GitHub reports no licence;
  the README says only "This project is for research and educational purposes." That is a statement
  of intent, not a licence, and it grants nothing — without a licence, default copyright applies and
  the code may not be redistributed or reused.
- **Model weights:** **None stated.** The Hugging Face model repository has no model card and no
  licence field.

## 3. Major publications by the authors

**None.** There is no paper, preprint, or technical report. Cite the repository and its commit.

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** three — background, artery, vein — as logits over three channels, read with a
  softmax and an argmax. The demo colours class 1 red and class 2 blue. Crossings are not a class.
- **Input grid:** 512×512, square, **resized with the aspect ratio ignored**, so a non-square
  photograph is stretched before the vessels are traced and every width measured on the result is
  stretched with it.
- **Output grid:** 512×512, resampled back to the photograph's own dimensions by the caller — the
  demo does it with `scipy.ndimage.zoom`, **nearest neighbour for the artery/vein map** (`order=0`)
  and bilinear for the other two heads.
- **Grid set in:** `IMG_SIZE = 512` in the Space's `app.py`, and `--img_size` (default `512`) in
  `src/train.py`.
- **Input expected:** a colour-fundus photograph, RGB. Nothing crops to the field of view, and
  nothing states whether the photograph should be disc-centred or macula-centred.
- **Preprocessing in the published code:** resize to 512², then standardise by ImageNet's statistics
  (mean 0.485/0.456/0.406, deviation 0.229/0.224/0.225), in `get_inference_transform`.

## 5. Architecture

- **Family:** U-Net with a ResNet-34 encoder initialised from ImageNet, via
  `segmentation_models_pytorch`.
- **Parameters:** not stated. The published checkpoint is 840 MB, which for three ResNet-34 U-Nets
  of roughly 24 million parameters each is consistent with a training checkpoint carrying optimiser
  state rather than weights alone.
- **Single model or ensemble:** one network per task. The class named `MultiHeadRetinaModel` is not
  multi-headed in the usual sense — it holds **three complete and independent U-Nets**, one per
  output, sharing no encoder. Nothing is combined or averaged.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| **Unknown** | Training | Unknown | No |

**Nothing names the data the published weights were trained on** — not the README, not the model
repository, not the Space. The code expects a `data/` directory of images, vessel masks and optional
artery/vein masks that the user supplies, and the author filled it with something before uploading
`mvp_model.pt`.

Two consequences follow, and neither can be argued away:

- **No dataset can be cleared as out-of-sample for this model.** Any score it earns on a public
  dataset here would be marked `unknown`, exactly as [VascX](vascx-artery-vein.md)'s is, and could
  not be compared with a model whose training list is published.
- **The artery/vein head may have seen very little.** Its loss is skipped for every sample without
  an artery/vein mask, and those masks are optional in the pipeline. How many of the author's images
  carried one is not recorded anywhere.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:**
  https://huggingface.co/adityaranjan2005/retina-vessel-segmentation/resolve/main/mvp_model.pt
- **Format and size:** one PyTorch checkpoint, `mvp_model.pt`, 880,588,497 bytes (840 MB), sha256
  `07718402…f277019` as served on 2026-09-16. It holds all three networks under
  `model_state_dict`.
- **Files in an ensemble:** one file, three networks, no ensemble.

## 8. Performance as reported by the authors

**None reported.** No metric is published for any dataset — not in the README, not on the model
repository, not in the demo. The repository states no validation split, so no held-out number exists
to report.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued project runs this model | — |

The author's own Gradio demo is the only consumer, and it is a demonstration rather than a pipeline:
it computes centreline length, branch points, endpoints and a tortuosity proxy, and writes no
biomarker table.

## 10. Known defects

None recorded as of 2026-09-16 — an absence of findings rather than a clean bill of health; with no
published metrics and no named training data, there is little here that can be checked. Two
properties of the published code are worth stating as facts rather than defects:

- **The checkpoint is loaded with `weights_only=False`** (`app.py`), which unpickles arbitrary
  Python. Anyone running it is executing whatever the file contains.
- **The artery/vein map is upsampled with nearest neighbour** while the vessel map is upsampled
  bilinearly, so at the original resolution the two disagree along every vessel edge: a pixel can be
  vessel in one map and background in the other.

## 11. Notes

- **This checkpoint holds three models, and this page describes one of them.** The vessel head
  (binary vessels) and the centreline head are separate models by this atlas's boundaries — a
  different task is a different page — and are not catalogued yet. They would each carry the same
  Unknown training data and the same absent licence.
- **The centreline head is trained against a mask the pipeline treats as ground truth**, and the
  demo then ignores it: `analyze_retinal_image` discards the predicted centreline and skeletonises
  the vessel mask instead. A network is trained, published and then not used by the code that ships
  with it.
- **"For research and educational purposes" is not a licence.** Anyone intending to use this model
  in anything they publish or ship should ask the author for an explicit licence; without one, the
  safest reading is that no permission has been granted.
- **The demo presents itself as clinical decision support** — "assisting ophthalmologists in
  diagnosis", "early disease detection" — while publishing no metric, no training data and no
  validation split. Those two facts belong side by side.

---

**Links and license last checked:** 2026-09-16
