# Grisan 2008

A tortuosity score that cares how the bending is distributed, not only how much extra length a
vessel has. It is the second definition of record under the word "tortuosity", and the one
AutoMorph reports as tortuosity density.

## 1. Citation

| | |
| --- | --- |
| Title | A novel method for the automatic grading of retinal vessel tortuosity |
| Authors | Grisan E, Foracchia M, Ruggeri A |
| Venue | IEEE Transactions on Medical Imaging 2008;27(3):310–319 |
| DOI | [10.1109/TMI.2007.904657](https://doi.org/10.1109/TMI.2007.904657) |
| Open copy | author copy — [ResearchGate](https://www.researchgate.net/publication/5518678_A_Novel_Method_for_the_Automatic_Grading_of_Retinal_Vessel_Tortuosity) |
| PMID | [18334427](https://pubmed.ncbi.nlm.nih.gov/18334427/) |
| Code | [enrigrisan/RET-Tortuosity](https://github.com/enrigrisan/RET-Tortuosity) |
| Dataset | none established |
| Other | none established |

The earlier conference version is *A novel method for the automatic evaluation of retinal vessel
tortuosity*, IEEE EMBS 2003, DOI
[10.1109/IEMBS.2003.1279902](https://doi.org/10.1109/IEMBS.2003.1279902) — the DOI retipy's code
cites. Both published versions are paywalled. The author-hosted copy that indexes once listed has
gone dead; ResearchGate is a browser copy that may move.

## 2. What it is about

Arc-chord tortuosity (Hart's τ1) scores a vessel with one gentle bend the same as a vessel with
many tight kinks of the same extra length. Grisan, Foracchia and Ruggeri split the vessel at the
points where its curvature changes sign, score each constant-sign piece by how much longer it is
than its own chord, and combine those pieces into one density. The result is meant to track a
clinician's grading of how tortuous a vessel looks, rather than how long its path is.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the other definition of record for [tortuosity](../biomarkers/tortuosity.md). AutoMorph's
  `td` column, AutoMorphalyzer's tortuosity density, and retipy's Grisan measure all point here —
  and retipy cites the 2003 conference DOI rather than this journal version.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| A tortuosity density over constant-sign-curvature subsegments tracks clinical grading of how twisted a vessel is, where a single arc-chord ratio does not | Retinal vessel segments graded for tortuosity; numbers are in the paper | this paper |

These are the authors' measurements and arguments. This atlas's own comparisons are separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Tortuosity](../biomarkers/tortuosity.md) | Defines Grisan τ (tortuosity density) |
| [Hart 1999](hart-1999.md) | The arc-chord measure this paper is answering |
| [retipy](../projects/retipy.md) | Implements it; cites the 2003 conference DOI |
| [AutoMorph](../projects/automorph.md) | Reports retipy's `td` |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Keeps tortuosity density after dropping other AutoMorph tortuosity columns |

## 6. Notes

- The 2003 conference paper and this 2008 journal paper are one work. Do not catalogue them twice.
  When a codebase cites 10.1109/IEMBS.2003.1279902, it means this definition.
- The GitHub repository is the practical source for the algorithm. It is not an open copy of the
  paper, and it states no licence.

---

**Links last checked:** 2026-09-21
