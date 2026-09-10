# Junction counts

How many branch points, endpoints and crossings the vascular tree contains. These are counts rather
than measurements — the simplest description of a vessel network's topology, and the starting point
for anything that reasons about the tree's structure rather than its size.

They are also the most direct read-out of how well the segmentation resolved the network, which
makes them useful for quality control and fragile as clinical variables.

## 1. What it measures

- **In one sentence:** the number of places where vessels split, end, or cross.
- **Also known as:** branch points, bifurcation counts, intersection points, endpoints,
  startpoints, crossings.
- **Direction of concern:** context-dependent; fewer branch points can indicate vessel loss, while
  more can indicate a noisier segmentation rather than a different eye.

## 2. Definition of record

- Fhima J, Van Eijgen J, Stalmans I, Men Y, Freiman M, Behar JA. *PVBM: A Python Vasculature
  Biomarker Toolbox Based on Retinal Blood Vessel Segmentation.* ECCV 2022 Workshops. DOI:
  [10.1007/978-3-031-25066-8_15](https://doi.org/10.1007/978-3-031-25066-8_15)
- **The formula, in words:** skeletonise the vessels, then classify each skeleton pixel by how many
  neighbours it has: one neighbour is an endpoint, three or more is an intersection. PVBM adds a
  third class — skeleton points lying on the optic disc, treated as where the tree *starts*.

## 3. Variants

### 3.1 Startpoints, endpoints and intersection points (PVBM)

- **Formula, in words:** three counts per vessel class — skeleton points on the optic disc
  (startpoints), points where a vessel terminates (endpoints), and points where a vessel branches
  (intersection points).
- **Source:** [PVBM](../projects/pvbm.md) `PVBM/GeometryAnalysis.py` (`compute_geomVBMs`).
- **Implemented by:** PVBM, and [OCULARNet](../projects/ocularnet.md) via its copy of PVBM's code.

### 3.2 Bifurcation counts over a region (VascX)

- **Formula, in words:** the number of bifurcations in the region, from the same vessel graph that
  supplies the [bifurcation angles](bifurcation-angle.md).
- **Source:** [VascX](../projects/vascx.md) `vascx/fundus/features/bifurcation_counts.py`.
- **Implemented by:** VascX.

### 3.3 Bifurcation and crossing regions of interest (OCULAR)

- **Formula, in words:** rather than counting, mark them: 20-pixel-diameter circular masks at
  geometric bifurcation points for arteries and veins separately, and at the centroids of detected
  crossing regions. The masks are then used to evaluate whether a segmentation gets the topology
  right.
- **Source:** [OCULARNet](../projects/ocularnet.md) `extract_zones.py`, using PVBM's junction code
  for the bifurcations and its own crossings class for the crossings.
- **Implemented by:** OCULARNet.

**Comparability:** counts are comparable only between identical skeletonisation and junction rules,
which in practice means only within one pipeline. PVBM's "intersection points" and VascX's
"bifurcations" are not the same population: a four-way crossing is one intersection point to a
neighbour-counting rule and not a bifurcation at all to a graph-based one.

## 4. Inputs required

- **Segmentations:** vessels, or artery/vein per class; the optic disc for PVBM's startpoints;
  a crossings class for OCULAR's crossing masks.
- **Derived geometry:** a skeleton, and either a neighbour count per pixel (PVBM) or a resolved
  vessel graph (VascX).
- **Tracing:** this biomarker is a measurement of the trace, not of the mask — see
  [vessel-tracing.md](vessel-tracing.md) for how each project builds it, and which defects were
  fixed where.
- **Why this matters:** skeletonisation decides the answer. A one-pixel spur creates an endpoint; a
  slightly thick junction creates several intersection points where anatomy has one.

## 5. Measurement region

- **PVBM:** the annulus between 2 and 3 optic disc radii, except startpoints, which are by
  definition on the disc.
- **VascX:** full grid or any grid field.
- **OCULAR:** wherever the masks are generated, with a footprint width the user is advised to tune
  and inspect visually.

## 6. Units and scale dependence

- **Unit as computed:** counts (dimensionless integers).
- **Depends on the pixel grid:** **Yes, strongly.** A finer grid resolves more small vessels and
  therefore more branch points, and it also produces more skeleton artefacts. Counts are among the
  least portable numbers here despite having no units.
- **Depends on a physical scale:** No.
- **Depends on field of view:** Yes — more retina in frame means more junctions.
- **Scale-invariant:** No.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [PVBM](../projects/pvbm.md) | 3.1 | `PVBM/GeometryAnalysis.py` | Original |
| [VascX](../projects/vascx.md) | 3.2 | `vascx/fundus/features/bifurcation_counts.py` | Original |
| [OCULARNet](../projects/ocularnet.md) | 3.3, plus PVBM's junction code | `extract_zones.py`, `utils/junctions_utils.py` | Reuses PVBM |
| [retipy](../projects/retipy.md) | bifurcation detection, as a feature of the web service | `retipy/landmarks.py` | Original |

The AutoMorph family does not report junction counts, although retipy — the source of its
measurement code — implements bifurcation detection.

## 8. Sensitivity and failure modes

- **Spurious junctions from skeleton noise** are the dominant error, and they scale with
  segmentation roughness rather than with anatomy.
- **Crossings are the ambiguity.** In a binary mask an artery-over-vein crossing is
  indistinguishable from two bifurcations back to back; only a model with an explicit crossings
  class can separate them.
- **Counts reward recall and punish precision**, so a pipeline that segments aggressively will
  always report more junctions. Use them to compare segmentations, not patients, unless the
  pipeline is held fixed.
- **Reported reproducibility:** Unknown for counts specifically.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- These counts are the best available proxy in this catalogue for whether a vascular tree was
  reconstructed correctly, which is why OCULAR's authors measure agreement on junctions rather than
  pixel overlap — a segmentation can score well on Dice while getting the topology wrong.

---

**Links and definitions last checked:** 2026-09-10
