# Martínez-Pérez 2000

The paper that first published a worked set of geometrical and topological numbers on a whole
retinal vascular tree — lengths, areas, diameters, branching angles, tortuosity, and indexes of
how the tree is connected — rather than on a handful of hand-picked bifurcations. Later toolboxes
in this atlas, [PVBM](../projects/pvbm.md) included, still cite it for those measures.

## 1. Citation

| | |
| --- | --- |
| Title | Geometrical and Morphological Analysis of Vascular Branches from Fundus Retinal Images |
| Authors | Martínez-Pérez ME, Hughes AD, Stanton AV, Thom SA, Chapman N, Bharath AA, Parker KH |
| Venue | MICCAI 2000. Lecture Notes in Computer Science 1935:756–765 |
| DOI | [10.1007/978-3-540-40899-4_78](https://doi.org/10.1007/978-3-540-40899-4_78) |
| Open copy | publisher — [Springer](https://link.springer.com/chapter/10.1007/978-3-540-40899-4_78) |
| PMID | None found |
| Code | none established |
| Dataset | none established |
| Other | none established |

The later journal version of the same method is *Retinal vascular tree morphology: a semi-automatic
quantification*, IEEE Transactions on Biomedical Engineering 2002;49(8):912–917, DOI
[10.1109/TBME.2002.800789](https://doi.org/10.1109/TBME.2002.800789), PMID
[12148830](https://pubmed.ncbi.nlm.nih.gov/12148830/). The 2000 chapter is freely readable at
Springer; the 2002 journal version is paywalled. Do not catalogue them twice.

## 2. What it is about

Most retinal vascular studies of the time measured a few visible bifurcations by hand. Martínez-Pérez
and colleagues took a binary vessel map, thinned it to a skeleton, marked branch and crossing
points, and stored each segment as a chain code. An operator then chose a continuous arterial or
venous tree; the rest — lengths, areas and angles of every segment, and a set of derived
geometrical and topological indexes — ran automatically.

The geometrical set includes branch length, vessel area, diameter, branching angle, tortuosity and
expansion factors. The topological set includes Strahler branching ratio, tree altitude, total
external path length, and counts of terminal and external–internal edges. They compared arterial
and venous trees in people with and without hypertension.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the first published measurement of several quantities this atlas already catalogues as
  [vessel area and length](../biomarkers/vessel-area-and-length.md),
  [junction counts](../biomarkers/junction-counts.md) and
  [bifurcation angle](../biomarkers/bifurcation-angle.md). [Fhima 2022](fhima-2022.md) is the
  toolbox that later pipelines actually run; this paper is the source that toolbox cites.
- It also names measures this atlas has not catalogued yet — perimeter, expansion factors, Strahler
  ratio, altitude, external path length — so a reader can see what is missing rather than assuming
  PVBM's eleven numbers are the whole set.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| A semi-automatic process, from a binary mask, measures lengths, areas and angles of every segment of a selected arterial or venous tree and derives geometrical and topological indexes | Clinical fundus photographs; the operator selects the tree and its class | this paper; restated in the 2002 journal version |
| Vessel diameters and branching angles agree with manual measurements | Validation against hand measurements (numbers in the papers) | 2002 journal version |
| Several derived geometrical and topological properties differ between hypertensive and normotensive eyes, with the arterial tree the one that moves | 10 normotensive and 10 age- and sex-matched hypertensive subjects, red-free photographs | 2002 journal version |

These are the authors' measurements on their own photographs. This atlas's own comparisons are
separate. Exact figures stay in the papers; this page does not restate tables.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Vessel area and length](../biomarkers/vessel-area-and-length.md) | First published the tree-sum area and length measures |
| [Junction counts](../biomarkers/junction-counts.md) | First published branch, crossing and terminal-edge counts on the skeleton |
| [Bifurcation angle](../biomarkers/bifurcation-angle.md) | First published automatic branching angles on a whole retinal tree |
| [Vessel calibre](../biomarkers/vessel-calibre.md) | Measures diameters on the tree; not the image-edge method of [Bankhead 2012](bankhead-2012.md) |
| [Tortuosity](../biomarkers/tortuosity.md) | A derived geometrical property here; the formula papers remain [Hart 1999](hart-1999.md) and [Grisan 2008](grisan-2008.md) |
| [Fhima 2022](fhima-2022.md) / [PVBM](../projects/pvbm.md) | Implements a subset (area, length, endpoints, intersections, tortuosity, branching angle) |

## 6. Notes

- The method is **semi-automatic**: a person still has to pick which tree to measure and whether it
  is artery or vein. PVBM's later fully automatic counts on a whole mask are not the same
  operation, even when they cite this paper.
- Perimeter, expansion (daughter-to-parent calibre), Strahler branching ratio, altitude and
  external path length are named here and are **not** catalogued biomarker pages yet.
- [Fhima 2022](fhima-2022.md) cites this DOI as reference 32 for overall length, perimeter, area,
  endpoints, intersections, tortuosity and branching angle, then describes new algorithms for the
  last two.

---

**Links last checked:** 2026-09-22
