# Fhima 2022

The paper that introduced PVBM — a toolbox that takes artery and vein masks someone else has
already made, and returns a table of geometric measurements. It is the implementation later
pipelines actually run for junction counts and for vessel area and length, sitting on top of
[Martinez-Perez 2000](martinez-perez-2000.md), and the paper to cite for the PVBM software.

## 1. Citation

| | |
| --- | --- |
| Title | PVBM: A Python Vasculature Biomarker Toolbox Based on Retinal Blood Vessel Segmentation |
| Authors | Fhima J, Van Eijgen J, Stalmans I, Men Y, Freiman M, Behar JA |
| Venue | ECCV 2022 Workshops. Lecture Notes in Computer Science, 2023:296–312 |
| DOI | [10.1007/978-3-031-25066-8_15](https://doi.org/10.1007/978-3-031-25066-8_15) |
| Open copy | preprint — [arXiv:2208.00392](https://arxiv.org/abs/2208.00392) |
| PMID | None found |
| Code | [PVBM](../projects/pvbm.md) — https://github.com/aim-lab/PVBM |
| Dataset | none established — the 69 annotated photographs (UZFG) were not released with the paper |
| Other | none established |

The LNCS volume is dated 2023; the workshop is ECCV 2022. This atlas uses 2022, matching how the
authors and the rest of this catalogue already cite it.

## 2. What it is about

Pipelines that colour in the vessels still leave the researcher to compute the numbers. Fhima and
colleagues published eleven measurements that run on a finished arteriolar or venular mask: area,
perimeter, skeleton length, endpoints, intersections, a median tortuosity, branching angles, three
fractal dimensions, and singularity length. They present new algorithms for tortuosity and for
branching angle, then run the whole set on 69 expert-annotated disc-centred photographs from Leuven
— 19 with normal ophthalmic findings, 50 with glaucoma — as a proof that the toolbox can be used.

The software is catalogued separately as [PVBM](../projects/pvbm.md). It does not segment the
vessels; the masks have to come from somewhere else.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the toolbox that later pipelines actually run for [junction counts](../biomarkers/junction-counts.md)
  and [vessel area and length](../biomarkers/vessel-area-and-length.md). The first published
  measurement of those tree sums is [Martinez-Perez 2000](martinez-perez-2000.md); this paper is
  the implementation, plus new algorithms for tortuosity and branching angle, and the multifractal
  set whose retinal definition is [Stosic 2006](stosic-2006.md).
- The software is catalogued as [PVBM](../projects/pvbm.md); this page is the argument, not the
  code.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| Eleven vasculature biomarkers, computed separately on arterioles and venules; new algorithms for tortuosity and branching angles | The toolbox as published | Table 2; Methods |
| Benchmarked length, area, tortuosity and fractal measures agree with ImageJ plugins (NRMSE 0 to 0.316) | Arterioles on all 69 UZFG photographs | Table 3 |
| For arterioles and venules, all biomarkers were significant and lower in glaucoma than in controls except tortuosity, venular singularity length and venular branching angles | 19 NOR, 50 GLA disc-centred photographs, expert A/V masks | Abstract; Tables 4 and 5 |

These are the authors' measurements on their Leuven annotated subset. This atlas's own comparisons
are separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Junction counts](../biomarkers/junction-counts.md) | Implements [Martinez-Perez 2000](martinez-perez-2000.md)'s endpoint and intersection counts, and adds startpoints on the disc |
| [Vessel area and length](../biomarkers/vessel-area-and-length.md) | Implements the pixel-area and skeleton-length measures |
| [PVBM](../projects/pvbm.md) | The software this paper introduced |
| [Martinez-Perez 2000](martinez-perez-2000.md) | The tree-measurement paper this toolbox cites for length, area, endpoints, intersections, tortuosity and branching angle |
| [Tortuosity](../biomarkers/tortuosity.md) | Introduces a median tortuosity algorithm; not the definition of record |
| [Bifurcation angle](../biomarkers/bifurcation-angle.md) | Introduces a branching-angle algorithm; not the definition of record |
| [Fractal dimension](../biomarkers/fractal-dimension.md) | Implements D₀, D₁, D₂ and singularity length; the retinal definition is [Stosic 2006](stosic-2006.md) |
| [Stosic 2006](stosic-2006.md) | Cited for D₀ > D₁ > D₂; this toolbox then computes those numbers by box-counting, not the sandbox |
| [Leuven-Haifa](../datasets/leuven-haifa.md) | Later public high-resolution set from the same groups; not the 69 UZFG photographs |

## 6. Notes

- The paper describes **eleven** biomarkers. The current toolbox lists **fifteen** (central retinal
  equivalents were added later). Cite the paper for the eleven; read the project page for what the
  code computes today.
- Area and length in this paper are scaled by the 1444×1444 grid. The catalogued PVBM outputs are
  in pixels, not that scaling. A number quoted from the paper is not the number the library
  returns.
- The paper offered the code under GNU GPL 3. The repository is MIT. Use the repository's licence
  for the code as it stands.
- UZFG is not a catalogued dataset. Do not treat the later [Leuven-Haifa](../datasets/leuven-haifa.md)
  release as those 69 frames.

---

**Links last checked:** 2026-09-21
