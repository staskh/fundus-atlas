# topology

**Where the network branches, how many pieces it is in, and at what angles it divides.** These are
counts and angles rather than sizes — what the vascular tree is shaped like as a graph, rather than
how much of it there is.

## 1. What it measures

A healthy retinal tree branches according to principles that minimise the work of moving blood, and
disease changes that: rarefaction reduces the number of branch points, and branching angles have
been associated with hypertension and with cardiovascular risk. The counts are also the most
direct read-out of how good a segmentation is — a fragmented mask produces many components and many
free ends where an eye has few.

## 2. The canonical names

| Name | What it is | Statistic |
| --- | --- | --- |
| `topology/junctions/{artery,vein,vessels}` | how many places three or more branches meet | none |
| `topology/endpoints/{artery,vein,vessels}` | how many free ends the network has | none |
| `topology/components/{artery,vein,vessels}` | how many separate pieces it is in | none |
| `topology/branching-angle/{artery,vein}` | the angle between the two daughter vessels at a bifurcation, in degrees | `mean`, `median`, `std` |
| `topology/temporal-angle/{artery,vein}` | the angle between the superior and inferior temporal arcades | `median` |

**`mean`, `median` and `std` of a branching angle are one biomarker pooled three ways**, not three
biomarkers. PVBM returns all three from one call, and the statistic part is what tells them apart.

## 3. Definitions of record

- **Counts and branching angle:** [Martinez-Perez 2000](../papers/martinez-perez-2000.md), the first
  automatic measurement of branching geometry on a whole retinal tree here. The counts later
  pipelines run — including a third class of disc start-points — are
  [Fhima 2022](../papers/fhima-2022.md). The *idea* that branching angles carry information is older,
  from vascular-branching theory (Murray 1926).
- **Temporal angle:** [Vargas 2026](../papers/vargas-2026.md). On circles centred at the optic disc,
  starting two-thirds of the way to the fovea and moving outward, the two largest-calibre vessels on
  the fovea side are found and the angle between them taken.

### 3.1 A count depends on what a vessel is

`topology/endpoints` means **every free end the network has**. An implementation that traces from a
root at the optic disc calls the end *at* the disc a start point, and its endpoint count excludes it
— so a straight vessel reads 1 where the geometry requires 2. That is a different, nameable
quantity rather than an error, and `PLAN-BIOMARKER.md` §2.1.2 is where the rooted variants are
settled.

## 4. Inputs required

A centreline, and junctions identified on it. For the temporal angle, the optic disc and the fovea.
How the centreline is obtained is the implementation's business — see
[vessel tracing](vessel-tracing.md) — but **it dominates every number on this page**: spurs left by
skeletonising a sharp corner appear as free ends, and pruning them changes the count.

## 5. Measurement region

`fov` by default. A count over a zone is a different number and the region part says which.

## 6. Units and scale dependence

Counts are dimensionless integers; angles are **degrees**. Both are **scale-invariant** — they do
not change with the pixel grid or the microns per pixel.

They are **not** field-of-view-invariant. A wider field contains more retina and therefore more
branch points, so a count from a 45° photograph is not comparable with one from a 30° photograph.

## 7. Implementations

| Project | What it computes | Source | Lineage |
| --- | --- | --- | --- |
| [PVBM](../projects/pvbm.md) | junctions, endpoints, start-points, a median branching angle | `PVBM/GeometryAnalysis.py` | Original |
| [OCULARNet](../projects/ocularnet.md) | the same set | `utils/GeometricalVBMs.py` | **Fork of PVBM's current class** — 343 of 486 lines identical |
| [VascX](../projects/vascx.md) | temporal angle | `vascx/fundus/features/temporal_angles.py` | Original |
| [AutoMorph](../projects/automorph.md) and its two descendants | none of these | — | — |

**PVBM and OCULARNet return identical numbers on every biomarker they share**, once their recursion
limits match. Their agreement is evidence about a common ancestor, not about the retina.

## 8. Sensitivity and failure modes

- **Skeleton spurs are counted as free ends.** A drawn curve with two ends carries four to six
  skeleton endpoints where it has sharp corners, so the count measures the tracer as much as the
  tree.
- **Fragmentation inflates components and endpoints.** A mask broken by a faint vessel produces two
  components where the eye has one.
- **A recursive tree walk can exhaust the stack.** PVBM's raises on dense trees at CPython's default
  limit, losing the whole geometry call rather than returning what it managed — see its page.
- **The counts are unstable under rotation** in current implementations. On a single fork with one
  junction, PVBM's vein junction count has read 1, 4, 4, 3 across four angles of a shape that did
  not change.

## 9. Known defects

- **PVBM's `median_branching_angle` is not the angle between daughters.** *Our finding, 2026-09-20,
  from reading `compute_angles_dictionary`.* It medians **every pairwise angle at every particular
  point**, the trunk included, and reads about 120° where the daughters are 60° apart. Mapping
  withdrawn; the column is kept under PVBM's own name.
- **PVBM's endpoint count excludes the end at the disc** (§3.1). Mapping withdrawn 2026-09-26 for
  PVBM and OCULARNet both.
- **VascX's temporal angle declines on shapes with no arcade**, warning `Couldn't find valid angles
  for any circle` — correct behaviour, recorded because an empty column looks like a broken one.

---

**Links and definitions last checked:** 2026-09-30.
