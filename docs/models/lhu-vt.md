# LHU-VT

LHU-VT takes a colour fundus photograph and returns one mask: vessel or not vessel, with no
separation of arteries from veins. Two ideas give it its name. **LHUN**, the Lightweight
Hypercomplex U-Net, replaces the ordinary convolutions of a U-Net with *octonion* ones — an eight-
component number system in which one multiplication mixes eight channels together, so that the
relationships a normal network has to learn separately for each pair of channels come built into
the arithmetic, and far fewer weights are needed. **VTDL**, the Vessel Thickness-Guided Dice Loss,
weights the training signal by how thick each vessel is, so that the thin vessels — which are a
small fraction of the pixels and most of the clinical interest — are not drowned out by the thick
ones during training.

It is catalogued here for its documentation rather than its use: **no code and no weights were
published**, so nothing about it can be checked or run (sections 1 and 7).

## 1. Code reference

- **Repository:** **None found.** *Our finding, 2026-09-19:* no repository is named in the paper's
  abstract or in its PubMed record, and searches of GitHub for the model name, for the authors, and
  for its distinguishing terms (hypercomplex, octonion, vessel-thickness-guided loss) return
  nothing that is this work. The publisher's page is behind a paywall, so a code-availability
  statement in the full text — if there is one — has not been read.
- **Version described here:** Not applicable.
- **Most recent commit:** Not applicable.
- **Training code included:** **No** — none located.
- **Language and how it runs:** Unknown. The paper reports FLOPs, parameter counts and model size,
  which implies a conventional deep-learning framework, but the framework is not established here.

## 2. License

- **Code:** Not applicable — no code located.
- **Model weights:** Not applicable — none published.

## 3. Major publications by the authors

- Ahmed W, Liatsis P. *LHU-VT: A Lightweight Hypercomplex U-Net with Vessel Thickness-Guided Dice
  Loss for retinal vessel segmentation.* Computers in Biology and Medicine 2025;185:109470. DOI:
  [10.1016/j.compbiomed.2024.109470](https://doi.org/10.1016/j.compbiomed.2024.109470) ·
  [PubMed 39667053](https://pubmed.ncbi.nlm.nih.gov/39667053/)

The authors are at Silo AI, Helsinki, and the Department of Computer Science, Khalifa University,
Abu Dhabi.

## 4. What it produces

- **Purpose:** `vessels`
- **Output classes:** one — vessel against background. The paper reports AUC, which is computed
  from a probability, so the network emits one per pixel.
- **Input grid:** **Unknown.** Not stated in the abstract, and the full text is paywalled. Vessel
  segmenters of this kind are usually trained on patches cut from the photograph rather than on
  whole images, but this repository has not established what LHU-VT does and does not guess.
- **Output grid:** Unknown, for the same reason.
- **Grid set in:** Not applicable — there is no code to read it out of, which is precisely why this
  section is unknown rather than merely unstated. Every other model in this catalogue had its grid
  settled by reading the inference code.
- **Input expected:** Unknown.
- **Preprocessing in the published code:** Unknown — no code located.

## 5. Architecture

- **Family:** a U-Net whose convolutions are **hypercomplex**, specifically octonion-valued. The
  saving is structural rather than a matter of pruning: an octonion convolution shares one set of
  weights across eight channel components, so a layer of a given width costs a fraction of the
  parameters an ordinary one would.
- **Parameters:** not stated as a count in the abstract. What is stated is a comparison: **4.4×
  fewer parameters, 2.4× fewer FLOPs and a 2.6× smaller model** than the methods the authors
  compare against, which are not named in the abstract.
- **Single model or ensemble:** Unknown; a single model is implied by the emphasis on size, and the
  abstract does not say.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| [CHASE-DB1](../datasets/chase-db1.md) | Training and test | The dataset's own authors | Unclear — not stated in the abstract |
| [DRIVE](../datasets/drive.md) | Training and test | The dataset's own authors | Unclear |
| [STARE](../datasets/stare.md) | Training and test | The dataset's own authors | Unclear |
| [HRF](../datasets/hrf.md) | Training and test | The dataset's own authors | Unclear |

**All four are unavailable for a fair benchmark of this model.** Which photographs of each were
held out is not established, so no split of them can be treated as out-of-sample either.

## 7. Weights

- **Publicly available:** **No** — none located.
- **Download URL:** none.
- **Format and size:** the paper states a model size as a ratio against its comparators rather than
  in megabytes; no file exists to measure.
- **Files in an ensemble:** Not applicable.

## 8. Performance as reported by the authors

Their measurements, on their own splits. **AUC** is the area under the ROC curve: how well the model
ranks vessel pixels above background ones, without committing to a threshold. The abstract gives AUC
and no other metric, so no overlap score is recorded here — an AUC without a Dice says how well the
probabilities are ordered and nothing about where the model would put the boundary.

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| CHASE-DB1 | AUC | 0.9938 | Ahmed & Liatsis 2025 |
| DRIVE | AUC | 0.9879 | Ahmed & Liatsis 2025 |
| STARE | AUC | 0.9988 | Ahmed & Liatsis 2025 |
| HRF | AUC | 0.9808 | Ahmed & Liatsis 2025 |

These are the authors' claims, read from the abstract rather than from the full text, and they are
not comparable with this repository's own figures: an AUC over the pixels of a dataset is a
different question from a Dice against an expert's tracing.

## 9. Used by

No catalogued project runs LHU-VT, and none could: there is nothing to run.

## 10. Known defects

- **Nothing is checkable.** *Our finding, 2026-09-19:* no code, no weights, and a paywalled full
  text. Every figure in section 8 rests on the authors' description of their own experiment. That is
  not a defect in the method — it may be an excellent method — but it is the reason no entry in this
  catalogue can say more about it. Open.

## 11. Notes

- **Octonion convolutions are the thing worth watching here**, independently of this paper's
  numbers: they are a structural way of making a network smaller, rather than a compression applied
  after the fact, and if the approach holds it applies to every model in this catalogue rather than
  to one of them.
- **An AUC of 0.9988 on STARE should be read carefully.** STARE is twenty photographs. Pixel-level
  AUC on a vessel segmentation is dominated by the enormous background class, which is why it runs
  so close to 1 for every published method; it is the least discriminating of the common metrics,
  and the abstract reports no other.

---

**Links and license last checked:** 2026-09-19
