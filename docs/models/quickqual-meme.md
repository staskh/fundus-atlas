# QuickQual-MEME

The MEga Minified Estimator is the smallest model in this catalogue: nine numbers read off an
off-the-shelf network, multiplied by nine weights, added to one bias, and squashed into a single
probability that the photograph is bad. Nothing is trained, nothing is downloaded beyond the
ImageNet weights that any PyTorch installation already fetches, and the ten parameters that make it
itself are printed in its repository's README.

It is catalogued separately from [QuickQual](quickqual.md) because it answers a different question.
QuickQual returns three probabilities — Good, Usable, Bad — and this returns one number. A pipeline
built on this one cannot distinguish a merely usable photograph from a good one, because the model
it is asking never had that opinion. That matters here because
[AutoMorphalyzer](../projects/automorphalyzer.md) runs **this** model, not the classifier, and a
reader comparing the two pipelines' quality handling has to know which was which.

## 1. Code reference

- **Repository:** https://github.com/justinengelmann/QuickQual — the same repository as
  [QuickQual](quickqual.md).
- **Version described here:** commit `a94feb02` (2023-11-06). The parameters are published in the
  README and in `QuickQualMEME_inference_example.ipynb`.
- **Most recent commit:** 2023-11
- **Training code included:** No. The code that fitted the nine weights — and that chose those nine
  features out of the backbone's 1,024 — is not in the repository, so the model can be run but not
  refitted, and the feature selection cannot be inspected.
- **Language and how it runs:** Python. `timm` (or torchvision) supplies `densenet121.tv_in1k`; the
  rest is two lines of arithmetic. No file is loaded: the parameters are literals.

## 2. License

- **Code:** **None stated.** No LICENSE file and GitHub reports no license, so no reuse permission
  has been granted. The same position as [QuickQual](quickqual.md), and inherited by
  [AutoMorphalyzer](../projects/automorphalyzer.md), which copies the parameters into its own
  source.
- **Model weights:** not applicable in the usual sense — there is no weight file. The DenseNet121
  weights are torchvision's ImageNet weights under their own terms; the ten parameters are
  published in the README under no stated licence.

## 3. Major publications by the authors

- Engelmann J, et al. *QuickQual: Lightweight, convenient retinal image quality scoring with
  off-the-shelf pretrained models.* The repository is the primary reference; a preprint is linked
  from it. No DOI was established at the time of checking. The MEME variant is described in the
  same README rather than in a paper of its own.

## 4. What it produces

- **Purpose:** `quality`
- **Output classes:** **none.** One probability that the photograph is **bad**, from a sigmoid. It
  has no notion of *usable*, and any three-way judgement made downstream is the user's, not the
  model's.
- **Input grid:** shorter side 512 pixels, **aspect ratio preserved** — `F.resize(img, 512)` with a
  single integer, as in [QuickQual](quickqual.md).
- **Output grid:** not applicable — one number, no mask.
- **Grid set in:** the `F.resize(img, 512)` call in the README's MEME example.
- **Input expected:** a fundus photograph cropped square without large black borders, resized to
  512 and normalised with mean and standard deviation 0.5 per channel.
- **Preprocessing in the published code:** resize, normalise. No cropping is performed for you.

## 5. Architecture

- **Family:** a frozen DenseNet121 feature extractor, of whose outputs **nine are read by index**
  (71, 109, 121, 53, 55, 123, 29, 133, 84), followed by a linear model with nine weights and a
  bias. The published weights are large and of both signs — −1411.32 to 1442.09 — which is what a
  linear model fitted on unnormalised deep features looks like.
- **Parameters:** DenseNet121's, unchanged and not trained, plus **ten**.
- **Single model or ensemble:** single model.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [EyeQ](../datasets/eyeq.md) — quality-graded [EyePACS](../datasets/eyeq.md) images | Fitting the ten parameters, and evaluation | The EyeQ authors | Yes: EyeQ's train and test splits, as for [QuickQual](quickqual.md) |
| ImageNet | Pretraining of the frozen feature extractor | ImageNet's annotators | Not applicable — the network is used as published |

EyeQ cannot be used to benchmark this model, for the same reason it cannot benchmark
[QuickQual](quickqual.md) or the [AutoMorph quality grader](automorph-quality-grader.md).

## 7. Weights

- **Publicly available:** Yes — as text. The nine feature indices, nine weights and one bias are
  printed in the repository's README.
- **Download URL:** https://github.com/justinengelmann/QuickQual — no file to download. This atlas
  reads the parameters out of the README at the pinned commit rather than transcribing them, so
  what runs is what that commit publishes.
- **Format and size:** ten floating-point numbers and nine indices.
- **Files in an ensemble:** none.

## 8. Performance as reported by the authors

The README reports the three-class [QuickQual](quickqual.md) results on the EyeQ test set and
presents MEME as an even lighter alternative producing a one-dimensional score; it gives a worked
example whose output is `p(bad) = 0.9386` for one photograph. No accuracy for the MEME variant was
established from the repository, and none is invented here.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Its entire quality stage. The probability is written into the collated results as `QuickQual_quality`, **no photograph is refused, no threshold is recommended, and no code path reads the column again** | The ten parameters, copied into `preprocess/preprocess.py` |

## 10. Known defects

- **The nine features are unexplained.** Which of DenseNet121's 1,024 outputs were chosen, and why,
  is not recoverable from the repository: the selection code is not published (section 1). A user
  cannot tell whether those nine carry image quality or an artefact of the fitting set.
- **A model with no middle class is used where the middle class matters.** AutoMorphalyzer replaced
  a three-way grader that gated on its middle class with this one-number model and no gate at all,
  so the distinction between good and usable disappears from that pipeline entirely. That is a
  design choice of the pipeline rather than a defect of the model, and it is recorded here because
  a reader of that pipeline's output will otherwise assume a judgement was made.
- **The parameters are copied, not referenced.** AutoMorphalyzer transcribes them into its own
  source. Nothing checks them against the upstream, and the upstream states no licence.

## 11. Notes

- **This is the cheapest model in the catalogue by a wide margin** — one forward pass of a standard
  ImageNet network and nine multiplications — which is the point its authors are making: a task can
  be easier than the literature around it suggests.
- Being a scalar score, it is compared here on the one question every quality model can answer: how
  confident is it that the photograph is worth measuring. Its three-class siblings answer more, and
  are compared on that separately.

---

**Links and license last checked:** 2026-09-15
