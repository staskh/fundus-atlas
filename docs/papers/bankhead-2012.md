# Bankhead 2012

The paper that measures vessel width from the photograph itself — locating each edge on the
intensity profile — rather than from a binary mask. It is the definition of record for vessel
calibre in this atlas, and the paper to cite for the ARIA software.

## 1. Citation

| | |
| --- | --- |
| Title | Fast retinal vessel detection and measurement using wavelets and edge location refinement |
| Authors | Bankhead P, Scholfield CN, McGeown JG, Curtis TM |
| Venue | PLoS ONE 2012;7(3):e32435 |
| DOI | [10.1371/journal.pone.0032435](https://doi.org/10.1371/journal.pone.0032435) |
| Open copy | publisher — [PLoS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0032435) · [PMC3299657](https://pmc.ncbi.nlm.nih.gov/articles/PMC3299657/) |
| PMID | [22427837](https://pubmed.ncbi.nlm.nih.gov/22427837/) |
| Code | [ARIA](../projects/aria.md) — https://github.com/petebankhead/ARIA |
| Dataset | none established — evaluated on [DRIVE](../datasets/drive.md) and REVIEW, not released with the paper |
| Other | none established |

## 2. What it is about

Most later pipelines colour in the vessels first and then measure width on the mask. Bankhead and
colleagues detect vessels with a wavelet transform and then, at each point along a fitted spline,
step perpendicular to the centreline and refine each edge's position from the photograph's
brightness. The distance between those two edges is the width. They tested detection on
[DRIVE](../datasets/drive.md) and width against three observers on the REVIEW width-evaluation set,
and they released the MATLAB program as ARIA.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the definition of record for [vessel calibre](../biomarkers/vessel-calibre.md): everything
  contentious about calibre lives in "locate the two edges", and this paper locates them in the
  image. The software is catalogued separately as [ARIA](../projects/aria.md); this page is the
  argument, not the code.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| Vessel detection true-positive rate 70.27%, false-positive rate 2.83%, accuracy 0.9371 | [DRIVE](../datasets/drive.md), 40 photographs | this paper |
| Output diameters agree with three independent observers | REVIEW width-evaluation set | this paper |
| Speed and generality need not cost accuracy; source code is published | Authors' conclusion; MATLAB with a graphical interface | this paper |

These are the authors' measurements on their own test sets. This atlas's own comparisons are
separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Vessel calibre](../biomarkers/vessel-calibre.md) | Defines the edge-from-image variant |
| [ARIA](../projects/aria.md) | The software this paper introduced |
| [DRIVE](../datasets/drive.md) | Detection test set |
| [VascX](../projects/vascx.md), [AutoMorph](../projects/automorph.md) | Measure width on a binary mask, which is a different operation |

## 6. Notes

- REVIEW is a width-evaluation set, not a catalogued dataset in this atlas. Obtain it from its own
  source; ARIA's tests expect it.
- A width measured on a binary mask is a different operation from the one this paper describes,
  even when both are called calibre. The variants are on the biomarker page.

---

**Links last checked:** 2026-09-21
