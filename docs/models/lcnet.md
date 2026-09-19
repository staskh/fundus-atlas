# LCNet

LCNet takes a colour fundus photograph and returns one mask: vessel or not vessel, with no
separation of arteries from veins. It is another entry in the lightweight line — a U-shaped network
built from **depthwise-separable convolutions**, which split an ordinary convolution into two
cheaper steps and cut the parameter count several-fold. What it adds to that base is a **coordinate
attention** module, which lets the network weight features by where they sit in the frame as well as
by what they look like, and an **atrous spatial pyramid pooling** block, which looks at the same
features through several dilations at once so that a thin vessel and a thick one are seen at the
scale each needs. Four side-output layers supervise intermediate depths during training, which is a
standard way of pushing a network to get the fine structure right rather than only the bulk.

The problem the authors name is **cross-connection redundancy** — where vessels cross, a network
tends to smear the two together and lose the thin, fuzzy boundaries between them.

It is catalogued here for its documentation rather than its use: **no code and no weights were
located** (sections 1 and 7).

## 1. Code reference

- **Repository:** **None found.** *Our finding, 2026-09-19:* no repository is named in the
  abstract or the PubMed record, and GitHub searches for the model name and its distinguishing
  terms return nothing that is this work. `LCNet` is also a common name — there is an unrelated
  PaddlePaddle classification backbone called PP-LCNet — so a search hit under that name is not
  this model. The publisher's full text is paywalled and has not been read.
- **Version described here:** Not applicable.
- **Most recent commit:** Not applicable.
- **Training code included:** **No** — none located.
- **Language and how it runs:** Unknown.

## 2. License

- **Code:** Not applicable — no code located.
- **Model weights:** Not applicable — none published.

## 3. Major publications by the authors

- Jiang M, Xie C, Huang S, Zhang Y, Mao J, Zhang X, Xu X. *LCNet: lightweight segmentation network
  for blood vessel segmentation in retinal imaging.* Medical Engineering & Physics 2026. DOI:
  [10.1088/1873-4030/ae4a13](https://doi.org/10.1088/1873-4030/ae4a13) ·
  [PubMed 41788037](https://pubmed.ncbi.nlm.nih.gov/41788037/)

The authors are at the Shanghai Key Laboratory of Contemporary Optics System, University of
Shanghai for Science and Technology.

## 4. What it produces

- **Purpose:** `vessels`
- **Output classes:** one — vessel against background. Four side outputs supervise the network
  during training; whether any of them is part of the published answer is not established.
- **Input grid:** **Unknown.** Not stated in the abstract, and the full text is paywalled. The
  reported cost — 21.2 GFLOPs on DRIVE — is a figure that only means something at a stated input
  size, and the size is not stated in what has been read.
- **Output grid:** Unknown.
- **Grid set in:** Not applicable — no code located.
- **Input expected:** Unknown. The abstract reports results on **OCT angiography** images as well
  as fundus photographs, so the network is not specific to colour fundus input.
- **Preprocessing in the published code:** Unknown.

## 5. Architecture

- **Family:** a U-shaped encoder–decoder using depthwise-separable convolutions, with a synergistic
  coordinate-attention module, atrous spatial pyramid pooling for multi-scale features, and four
  side-output layers for deep supervision.
- **Parameters:** **2.65 million**, as stated by the authors, at **21.2 GFLOPs on DRIVE**. That is
  light against a full U-Net and heavy against [LightVesselNet](lightvesselnet.md)'s claimed 75,000
  or [LWNet](lwnet.md)'s ~70,000 — "lightweight" spans two orders of magnitude in this literature,
  which is worth knowing before comparing two papers that both use the word.
- **Single model or ensemble:** a single model, as described.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [DRIVE](../datasets/drive.md) | Training and test | The dataset's own authors | Unclear — not stated in the abstract |
| [STARE](../datasets/stare.md) | Training and test | The dataset's own authors | Unclear |
| [CHASE-DB1](../datasets/chase-db1.md) | Training and test | The dataset's own authors | Unclear |
| [IOSTAR](../datasets/iostar.md) | Training and test | The dataset's own authors | Unclear |

**All four are unavailable for a fair benchmark of this model.** The abstract also reports results
on fundus images with lesions and on OCT angiography images without naming those collections, so
what else it saw is not established.

## 7. Weights

- **Publicly available:** **No** — none located.
- **Download URL:** none.
- **Format and size:** Not applicable.
- **Files in an ensemble:** Not applicable.

## 8. Performance as reported by the authors

Their measurements, on their own splits. The abstract reports **global accuracy** — the share of all
pixels classified correctly — and nothing else.

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| DRIVE | Accuracy | 96.02% | Jiang et al. 2026 |
| STARE | Accuracy | 97.95% | Jiang et al. 2026 |
| CHASE-DB1 | Accuracy | 97.95% | Jiang et al. 2026 |
| IOSTAR | Accuracy | 97.77% | Jiang et al. 2026 |

**Accuracy is the weakest of the common metrics on this task, and these numbers should not be read
as strong.** Vessels occupy roughly a tenth of a fundus photograph, so a model that marked *nothing*
as vessel would score about 90% by this measure. The interesting figure is the overlap with the
expert's tracing — Dice or F1 — which the abstract does not give, and which the full text may.

These are the authors' claims and are not comparable with this repository's figures.

## 9. Used by

No catalogued project runs LCNet, and none could: there is nothing to run.

## 10. Known defects

- **Nothing is checkable.** *Our finding, 2026-09-19:* no code, no weights, a paywalled full text,
  and a model name shared with an unrelated well-known network. Open.
- **The reported metric cannot separate good from mediocre.** *Our observation, 2026-09-19:*
  section 8. This is a defect of what was published rather than of the method.

## 11. Notes

- **Cross-connection redundancy is a real problem and a rarely named one.** Where an artery crosses
  a vein, most vessel segmenters thicken and merge the two; a model that states this as its target
  is worth testing on exactly those regions, which this repository can measure — its artery/vein
  benchmark already counts what share of each dataset's vessel pixels are annotated as crossings.
- **Its OCT-angiography results are outside this catalogue's scope.** Fundus Atlas maps
  colour-fundus work; the abstract's OCTA claims are recorded here only to say that the model is not
  exclusively a fundus one.

---

**Links and license last checked:** 2026-09-19
