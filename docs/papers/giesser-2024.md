# Giesser 2024

A tenth tortuosity number, the vascular curvature index (VCI), reported as more stable on a
five-minute retest of healthy eyes than the published formulas the authors compared it against. The
formula itself is unpublished: the paper calls it proprietary. No catalogued pipeline computes it.

## 1. Citation

| | |
| --- | --- |
| Title | A new retest-stable tortuosity metric for retinal vessel analyses |
| Authors | Giesser SD, Turgut F, Saad A, Sommer C, Zhou Y, Wagner SK, Keane PA, Becker M, Cabrera DeBuc D, Somfai GM |
| Venue | Investigative Ophthalmology & Visual Science 2024;65(12):30 |
| DOI | [10.1167/iovs.65.12.30](https://doi.org/10.1167/iovs.65.12.30) |
| Open copy | publisher — [IOVS](https://doi.org/10.1167/iovs.65.12.30) (CC BY 4.0) · [PMC11500049](https://pmc.ncbi.nlm.nih.gov/articles/PMC11500049/) |
| PMID | [39436374](https://pubmed.ncbi.nlm.nih.gov/39436374/) |
| Code | none established |
| Dataset | none established |
| Other | none established |

## 2. What it is about

Published tortuosity formulas disagree with each other and, on a second photograph of the same
healthy eye a few minutes later, often disagree with themselves. Giesser and colleagues ran
[AutoMorph](../projects/automorph.md) on paired 45° photographs of 44 people without ocular disease,
scored the masks with several of the usual measures, and introduced VCI as a proprietary score
based on change of angular momentum along the vessel. They report that VCI moved less between the
two photographs than every comparator except inverse-radius tortuosity, and that it correlated with
that comparator and almost not at all with an angle-based measure.

## 3. Why it is in this atlas

- **Kind:** definition
- It names a tortuosity measure that a reader will meet in the literature, and it is the reason this
  atlas has to say that a VCI value cannot be reproduced from the public description. The retest
  numbers are also why: even on healthy eyes, five minutes apart, AutoMorph's published tortuosity
  columns moved more than this unpublished one.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| VCI Spearman retest correlation 0.92 / 0.86 / 0.87 on arteries / veins / vessels | 44 people, paired 45° photographs five minutes apart, Zeiss Visucam Pro NM | this paper |
| VCI Pearson retest correlation 0.86 / 0.94 / 0.89 on arteries / veins / vessels | Same sample | this paper |
| VCI's absolute test–retest difference was significantly smaller than every comparator except inverse-radius tortuosity (p = 0.14 vs that one) | Same sample, paired one-sided t-test on Box–Cox z-scores | this paper |
| VCI correlated most with inverse-radius tortuosity (Pearson 0.7, Spearman 0.72) and almost not at all with angle-based tortuosity (Pearson 0.05, Spearman 0.07) | Same sample | this paper |
| The formula is proprietary; it is sketched as change of angular momentum (`L = Iω`) | Methods | this paper |

These are the authors' measurements on healthy retest photographs. This atlas's own comparisons are
separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Tortuosity](../biomarkers/tortuosity.md) | Names a tenth measure under the same word; AutoMorph's columns were the comparators, not VCI |
| [AutoMorph](../projects/automorph.md) | Produced the vessel and artery/vein masks; did not compute VCI |
| [Hart 1999](hart-1999.md) | One of the comparator families (squared curvature) |
| [Grisan 2008](grisan-2008.md) | Tortuosity density was a comparator |

## 6. Notes

- The same three letters also name an unrelated OCT-angiography *vessel complexity index*. That is
  a different quantity.
- A VCI value found in a paper cannot be compared with any published tortuosity formula, because
  the mapping from the mask to the number is not public.
- AutoMorph's own tracer returns points in discovery order rather than path order; whether VCI was
  computed on those traces or on a separate reconstruction is unknown. See
  [vessel tracing](../biomarkers/vessel-tracing.md).
- The study is a short-interval retest on healthy eyes. The authors state that long-term stability
  and performance in disease were not tested.

---

**Links last checked:** 2026-09-21
