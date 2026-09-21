# Mohamed Naim 2026

A demonstration, on photographs of the white of the eye rather than of the fundus, that a
segmentation can overlap the vessels well and still be unusable for tortuosity. The authors' Dice
scores look respectable; their centreline errors do not. That distinction is why the paper is here.

## 1. Citation

| | |
| --- | --- |
| Title | Topology-preserving, diameter-specific framework for conjunctival vessel segmentation and tortuosity analysis in diabetes |
| Authors | Mohamed Naim A, Iroshan Kondarage A, Liyanaarachchi R, Jayasinghe S, De Silva AC |
| Venue | Scientific Reports 2026;16:20675 |
| DOI | [10.1038/s41598-026-48680-3](https://doi.org/10.1038/s41598-026-48680-3) |
| Open copy | publisher — [Scientific Reports](https://www.nature.com/articles/s41598-026-48680-3) (CC BY-NC-ND 4.0) · [PMC13333877](https://pmc.ncbi.nlm.nih.gov/articles/PMC13333877/) |
| PMID | [42086622](https://pubmed.ncbi.nlm.nih.gov/42086622/) |

A preprint of the same work is [10.21203/rs.3.rs-7871199/v1](https://doi.org/10.21203/rs.3.rs-7871199/v1).

## 2. What it is about

The vessels on the bulbar conjunctiva — the white of the eye — can be photographed without dilating
the pupil. Mohamed Naim and colleagues annotated those vessels at a chosen width (40 µm and wider)
on a new Sri Lankan collection, trained a dilated-attention U-Net to colour them in, and then
measured [arc-chord tortuosity](hart-1999.md) on the resulting centrelines. They compared that
network with several standard segmenters on the same 35 annotated photographs, and they compared
conjunctival and retinal tortuosity between people with diabetes and people without.

The photographs are **not fundus photographs**. The finding that matters for this atlas is
methodological: pixel overlap and a usable trace are different measurements.

## 3. Why it is in this atlas

- **Kind:** finding
- This atlas's artery/vein comparison already treats topology as a different question from overlap
  ([what topology says](../benchmarks/av-results.md#21-what-topology-says-that-neither-of-them-says)).
  Mohamed Naim 2026 is the same argument, written for tortuosity: several networks produced Dice
  scores in the same band as theirs, and still missed the ground-truth centreline by more than a
  hundred pixels and the tortuosity number by five times as much. A reader who trusts a biomarker
  because the mask "looks like vessels" is reading the wrong score.
- It is **not** catalogued as a model or a project. Those catalogues are for colour-fundus
  photographs; this network was trained on the conjunctiva.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| Proposed network Dice 0.759 ± 0.028, IoU 0.613 ± 0.033, MCC 0.760 ± 0.025 | 35 annotated conjunctival photographs, five-fold cross-validation | Table 1 |
| Mean arc-chord tortuosity 1.406 ± 0.084, indistinguishable from the annotators' 1.410 ± 0.128 (Wilcoxon p = 0.76) | Same 35 photographs | Table 6 |
| Tortuosity error 0.036 ± 0.029; centreline distance 30 ± 75 px. Comparators: tortuosity error ≥ 0.168 and centreline distance > 100 px, even when Dice was in a similar range | Same 35 photographs | Table 6 |
| Retraining the same architecture with a clDice loss **lowered** Dice (0.677 vs 0.714 on the N = 10 ablation set) and **worsened** tortuosity error and centreline distance | Held-out N = 10 | Tables 5 and 10 |
| Conjunctival arc-chord tortuosity higher in diabetes than in controls (median difference 0.178, Mann–Whitney p = 0.0026) | 20 controls, 25 people with diabetes, subject-level means of eight photographs | Fig. 8 |
| Retinal tortuosity, from a U-Net fine-tuned on [DRIVE](../datasets/drive.md), also higher in diabetes (median difference 0.0305, p = 0.0028) | Fundus photographs of the diabetic subjects only | Results |
| Inter-annotator Dice 0.92 ± 0.02 on the 40 µm inclusion rule | Second observer on the annotated set | Methods |

These are the authors' measurements on their conjunctival collection and on fundus photographs of
the same diabetic subjects. This atlas's own comparisons are separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Tortuosity](../biomarkers/tortuosity.md) | Uses Hart's arc-chord ratio (τ1); shows the number collapsing when the centreline fragments |
| [Vessel tracing](../biomarkers/vessel-tracing.md) | The step their topology metrics are actually scoring |
| [Hart 1999](hart-1999.md) | The formula they compute; they cite the 1997 AMIA version |
| [DRIVE](../datasets/drive.md) | Fine-tuning set for a **separate** retinal U-Net used as a diabetes-reference arm, not for the conjunctival network |
| [AV results](../benchmarks/av-results.md) | This atlas's fundus version of the same overlap-versus-topology split |

## 6. Notes

- **Not a fundus method.** The network, the 40 µm annotations, and the 5 µm/pixel calibration
  (150 mm camera-to-eye, Nikon D7200) all describe the conjunctiva. Do not drop its Dice scores
  into a fundus vessel table.
- **The public code is the segmenter, not the biomarker.**
  [amnaim7/Conj_Vessel_Extraction](https://github.com/amnaim7/Conj_Vessel_Extraction) (archived
  [10.5281/zenodo.19462245](https://doi.org/10.5281/zenodo.19462245), last commit 2026-04) trains
  and scores masks. Its metrics are Dice, IoU, precision, recall, MCC. Tortuosity error and
  centreline distance are described in the paper; they are not in the repository. No trained
  weights are committed. There is no LICENSE file; the README states research and academic use.
- **Loss versus claim.** The paper argues for topology-preserving extraction and cites clDice, then
  trains with Dice plus binary cross-entropy. Their own ablation says switching to clDice made the
  centreline worse. The published GitHub loss matches Dice–BCE.
- **Tiny labelled set.** The IEEE DataPort deposit
  ([10.21227/6583-ay07](https://doi.org/10.21227/6583-ay07), registration) has 108 people (57 with
  diabetes, 51 controls), eight conjunctival views each, and fundus photographs of the diabetic
  subjects. Only **30** conjunctival frames from diabetic subjects are released with masks, plus
  five extra healthy frames used in training, for 35 labelled images. Cross-validation is at image
  level on those 35; people contribute several frames, so folds can leak a person.
- **Calibre class.** Annotations keep vessels ≥ 40 µm. Owen et al. 2008, which this paper cites for
  that cutoff, reported *lower* tortuosity in that larger-vessel class with longer diabetes
  duration, and *higher* tortuosity in capillaries. The two findings are not interchangeable.
- **The retinal arm is a different pipeline.** A U-Net fine-tuned on DRIVE, then MATLAB opening,
  dilation, closing and skeletonisation to glue fragments before tortuosity. That is not the
  conjunctival network, and it is not a catalogued model.
- A Research Square preprint exists; this page describes the Scientific Reports version of record
  (received 2025-10-15, accepted 2026-04-09, published 2026-05-05).

---

**Links last checked:** 2026-09-21
