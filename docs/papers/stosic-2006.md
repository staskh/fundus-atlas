# Stosic 2006

The paper that showed a single fractal dimension is not enough for a retinal vessel tree: the
vessels are geometrical multifractals, with a hierarchy of exponents D₀ > D₁ > D₂ and an f(α)
singularity spectrum. Every catalogued pipeline that reports D₀, D₁, D₂ or singularity length is
answering the question this paper posed — though not by the method it used.

## 1. Citation

| | |
| --- | --- |
| Title | Multifractal Analysis of Human Retinal Vessels |
| Authors | Stosić T, Stosić BD |
| Venue | IEEE Transactions on Medical Imaging 2006;25(8):1101–1107 |
| DOI | [10.1109/TMI.2006.879316](https://doi.org/10.1109/TMI.2006.879316) |
| Open copy | preprint — [arXiv:physics/0410076](https://arxiv.org/abs/physics/0410076) |
| PMID | [16895002](https://pubmed.ncbi.nlm.nih.gov/16895002/) |
| Code | none established |
| Dataset | none established |
| Other | none established |

The IEEE Xplore copy ([document 1661704](https://ieeexplore.ieee.org/document/1661704)) is
paywalled. A ResearchGate copy is also circulating:
[publication 301870195](https://www.researchgate.net/publication/301870195_Multifractal_Analysis_of_Human_Retinal_Vessels);
those URLs move. The arXiv abstract reverses the inequality D₀ > D₁ > D₂ compared with the
journal; the tables match the journal. Read the journal, or the tables, not that abstract.

## 2. What it is about

Earlier retinal work treated the vessel tree as one fractal — a single number, often compared with
diffusion-limited aggregation (DLA). Stosić and Stosić asked whether that is the right description.
They took the twenty [STARE](../datasets/stare.md) vessel photographs, both observers' hand
segmentations (AH and VK), and Rosenfeld skeletons of each, and measured a family of generalised
dimensions D_q and the f(α) singularity spectrum with the generalised sandbox method: random
points on the vessels, boxes grown around those points, repeated a hundred times.

In every image the capacity, information and correlation dimensions came out different, which is
the signature of a multifractal rather than a monofractal. Pathological STARE frames tended toward
lower dimensions and a spectrum shifted to smaller α. The authors themselves call that pathology
signal encouraging but not conclusive: ten mixed diseases against ten normals is a small sample.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the first published demonstration that the retinal vascular tree is a geometrical
  multifractal — the reason this atlas's [fractal dimension](../biomarkers/fractal-dimension.md)
  page carries D₀, D₁, D₂ and a singularity spectrum at all, rather than one box-counting number.
- [Fhima 2022](fhima-2022.md) / [PVBM](../projects/pvbm.md) is the implementation later pipelines
  actually run; that toolbox cites this paper for D₀ > D₁ > D₂, then computes those numbers by a
  different method (box-counting after Chhabra, not this paper's sandbox).

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| Human retinal vessels are geometrical multifractals: D₀ > D₁ > D₂ in every image, all three well below the DLA correlation dimension of about 1.71 | STARE's 20 vessel photographs (10 normal, 10 mixed pathology), both observers, with and without skeletonisation | Abstract; Fig. 2; Tables I–II |
| On observer AH's full-width masks, mean capacity dimension D₀ was 1.599 (normal) and 1.534 (pathological) | Same 20 STARE frames | Table II |
| Pathological images tend to lower generalised dimensions, an f(α) spectrum shifted toward smaller α, lower peaks, and sometimes a narrower range | Same 20 frames, both observers, original and skeletonised | Abstract; Figs. 4–5; Conclusion |
| Skeletonisation slightly lowers D₀ and narrows f(α); the two observers' level of detail moves the number more than skeletonisation does. Compare only within one observer | Four sets of 20 images | Table II; Discussion |

These are the authors' measurements on STARE. They state the pathology contrast is not statistically
conclusive. This atlas's own comparisons are separate. Exact per-image figures stay in the paper.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Fractal dimension](../biomarkers/fractal-dimension.md) | Defines the retinal multifractal set (D₀, D₁, D₂, f(α) spectrum) |
| [Fhima 2022](fhima-2022.md) / [PVBM](../projects/pvbm.md) | Implements D₀, D₁, D₂ and singularity length; cites this paper; uses box-counting, not the sandbox |
| [STARE](../datasets/stare.md) | The twenty vessel photographs and both observers' masks this paper measured |

## 6. Notes

- **Sandbox versus box-counting.** This paper uses the generalised sandbox method (boxes centred on
  randomly chosen vessel pixels). PVBM follows Chhabra and the ImageJ FracLac plugin: a grid of
  boxes, rotated to satisfy D₀ > D₁ > D₂. The numbers share names and the inequality; they are not
  the same computation.
- **What PVBM keeps and what it drops.** Stosić report D_q at q = −10, 0, 1, 2, 10 and the whole
  f(α) curve (peak location, peak height, width, shift). PVBM returns D₀, D₁, D₂ and singularity
  length Δα ≈ α(q=−10) − α(q=10). The shift of the spectrum — the contrast this paper emphasises —
  is not a catalogued output.
- **DLA is a comparison, not a biomarker.** Earlier monofractal papers had likened the retina to
  DLA (D₂ ≃ 1.71). This paper's point is that retinal D_q sit well below that value. Do not catalogue
  "distance to DLA" as a measurement.
- Family, Masters and Platt 1989 (*Physica D* 38:98–103) is the earlier retinal *monofractal* paper
  this work is answering; it is not a papers-catalogue entry yet. The monofractal box-counting
  variant on the fractal-dimension page still has no definition-of-record paper.

---

**Links last checked:** 2026-09-22
