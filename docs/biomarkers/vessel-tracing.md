# Vessel tracing

Before any biomarker about vessel *shape* can be computed, the software has to answer a question the
segmentation does not: **which pixels form which vessel, and in what order along it?** A mask says
only "this pixel is vessel". Tracing turns that into a set of centrelines, each an ordered sequence
of points from one end of a vessel to the other, cut apart or joined up at junctions.

This page is not a biomarker. It is catalogued here because it is the step where the pipelines in
this atlas differ most from each other, and because several biomarkers are measurements *of the
trace* rather than of the mask — so two pipelines running the same model on the same photograph can
disagree about tortuosity while agreeing exactly about density.

## 1. What it produces

- **In one sentence:** a set of vessel centrelines, each an ordered list of points, derived from a
  binary segmentation or directly from the image.
- **Also known as:** centreline extraction, skeletonisation, vessel segment extraction, tracking.
- **The four decisions every tracer makes:**
  1. **Centreline** — thin the mask to a one-pixel skeleton, or fit a curve in the image.
  2. **Junctions** — how branch points are found, and whether they are erased, kept, or used as
     graph nodes.
  3. **Ordering** — how the points of one vessel are put into path order. A flood fill visits pixels
     in an order that has nothing to do with the vessel's direction, so this step is required, not
     optional.
  4. **Smoothing and joining** — whether the centreline is smoothed before derivatives are taken,
     and whether branches are rejoined across junctions into whole vessels.

## 2. Definition of record

There is none: tracing is engineering rather than a published measurement. Two papers do prescribe
what it must deliver for their measures to be valid, and both are ignored by parts of this
catalogue:

- Hart et al. 1999 require the centreline to be **low-pass filtered** before curvature is
  estimated, because a vessel at 45° to the pixel grid is stored as a zigzag
  ([open copy](https://www.siue.edu/~sumbaug/RetinalProjectPapers/Measurement%20and%20classification%20of%20retinal%20vascular%20tortuosity.pdf)).
- Grisan et al. 2008 require a **cubic smoothing spline** through the centreline samples, for the
  same reason, before curvature signs are used to partition the vessel
  ([reference implementation](https://github.com/enrigrisan/RET-Tortuosity)).

## 3. Variants

One per project, in order of how much the trace is reconstructed rather than merely thinned.

### 3.1 ARIA — spline fit in the image, no skeleton

- **Centreline:** segmentation by isotropic undecimated wavelet transform, then centre lines and
  intensity profiles obtained by **spline fitting** (`centre_spline_fit`), followed by
  gradient-based edge localisation. There is no binary skeleton at any point.
- **Junctions:** handled as part of the vessel-tracking algorithm rather than by erasing pixels.
- **Ordering:** intrinsic — a fitted spline is parameterised along its length.
- **Smoothing:** intrinsic to the spline.
- **Consequence:** the only tracer here immune to pixel-grid staircasing, because it never quantises
  the centreline. It is also the oldest and the only one requiring MATLAB.
- **Source:** [ARIA](../projects/aria.md), `Vessel_Algorithms/aria_algorithm_general.m`.

### 3.2 VascX — skeleton graph with typed nodes, splines and resolved vessels

- **Centreline:** `skimage.morphology.skeletonize`, with the optic disc masked out of the skeleton
  so the tangle over the nerve head cannot create spurious junctions.
- **Junctions:** the skeleton is converted to a **graph** (`sknw.build_sknw`), each edge carrying its
  ordered pixel run, each node typed as a `Bifurcation` or an `Endpoint`.
- **Ordering:** from the graph — each edge's points come out along the path by construction.
- **Smoothing and joining:** a cubic **smoothing spline** per segment (default error fraction 0.05),
  used for arc length, curvature and perpendicular diameter sampling; a
  `RecursiveWeightedAverageResolver` then merges segments across bifurcations into *resolved
  segments*, so a biomarker can be computed per branch or per whole vessel.
- **Consequence:** the most complete reconstruction in this catalogue, and the only one that offers
  per-vessel as well as per-segment measurement. A short segment that cannot support a cubic spline
  falls back to a retipy-derived diameter method — a small piece of the old lineage surviving inside
  the new pipeline.
- **Source:** [VascX](../projects/vascx.md), `vascx/fundus/vessels_layer.py`,
  `vascx/shared/segment.py`, `vascx/fundus/vessel_resolve.py`.

### 3.3 PVBM — skeleton tree rooted at the optic disc

- **Centreline:** `skimage.morphology.skeletonize`.
- **Junctions:** `extract_subgraphs` labels each disconnected subgraph and simultaneously builds a
  map of each pixel's distance to the optic disc centre; `TreeReg` then stores the topology as a
  tree of parents and children.
- **Ordering:** by **traversal from the optic disc outward** — the vessel is followed in the
  direction blood flows, which is the one ordering with an anatomical meaning rather than an
  algorithmic one. The authors note the traversal was moved from recursion to iteration because deep
  vessels overflowed the stack.
- **Smoothing:** none before curvature-free measures; the biomarkers PVBM computes from the trace
  (tortuosity index, branching angle, junction counts) do not differentiate twice.
- **Consequence:** rooting the tree at the disc gives start points a meaning (its "number of start
  points" biomarker is exactly the skeleton points on the disc) and makes the parent-child relation
  available to biomarkers, at the cost of depending on the disc segmentation.
- **Source:** [PVBM](../projects/pvbm.md), `PVBM/GeometryAnalysis.py`,
  `PVBM/GraphRegularisation/GraphRegularisation.py`.

### 3.4 OCULARNet — PVBM's tracer, plus explicit junction and crossing regions

- **Centreline and ordering:** PVBM's, through a modified copy of its code.
- **Junctions:** `handle_interpoints` extracts geometric bifurcation points and dilates each into a
  20-pixel disc, producing a *region* per junction rather than a point; crossings — a class its own
  segmentation model predicts — become 20-pixel discs at their centroids.
- **Joining:** `extract_major_vessels` isolates the major vasculature either by morphological
  opening scaled to the optic disc size or by taking the largest connected components.
- **Consequence:** the only pipeline here that can distinguish a genuine bifurcation from an
  artery-vein crossing, because its model segments crossings explicitly. In a binary mask the two
  are indistinguishable, and every other tracer on this page treats a crossing as a junction.
- **Source:** [OCULARNet](../projects/ocularnet.md), `utils/junctions_utils.py`,
  `extract_zones.py`.

### 3.5 AutoMorphalyzer — skeleton, branch points removed, depth-first ordering

- **Centreline:** skeleton, then `_remove_branching_points` erases any pixel with three or more
  neighbours, then `_remove_small_branches` drops branches shorter than 10 pixels.
- **Junctions:** erased, so the tree becomes a set of independent branches.
- **Ordering:** `_reorder_coords` runs a **depth-first walk from an endpoint** (a pixel with exactly
  one neighbour) per connected component, which is what puts the points in path order.
- **Smoothing:** `_refine_path` with a 4-point window, and `_refine_coords`; Numba-compiled
  throughout, which its authors cite as the reason the stage is much faster.
- **Consequence:** repairs the ordering defect it inherited (section 4) while keeping the
  erase-the-junctions design, so measurements are per branch and short twigs are discarded rather
  than measured.
- **Source:** [AutoMorphalyzer](../projects/automorphalyzer.md),
  `automorph/measure/get_vessel_coords.py`.

### 3.6 AutoMorphClass — skeleton, stack-based labelling, endpoint-walk ordering, gap bridging

- **Centreline:** skeleton, with a preprocessing pass unique in this catalogue —
  `remove_small_components` (default minimum 700 pixels), `bridge_gaps` (default maximum 22 pixels)
  and `connect_nearby_endpoints`, then re-skeletonisation. It tries to repair the mask before
  tracing it.
- **Junctions:** `_label_vessels`, a Numba stack-based flood fill, labels components and returns
  detected bifurcation pixels.
- **Ordering:** `order_vessel_points` builds an occupancy grid over each component, finds a
  degree-one endpoint and walks the path — applied in the tortuosity routine before any measure is
  computed.
- **Smoothing:** none. Derivatives are taken with `np.gradient` on the ordered integer pixels.
- **Consequence:** the gap bridging is a real difference in kind: it changes which vessels exist,
  not just how they are traversed, so a broken vessel that other pipelines measure as two short
  segments may be measured here as one long one.
- **Source:** [AutoMorphClass](../projects/automorphclass.md),
  `src/pytorch_automorph/tortuosity_utils.py`, `vessel_postprocess.py`.

### 3.7 AutoMorph — skeleton, junctions erased, flood-fill discovery order

- **Centreline:** skeleton of the vessel mask.
- **Junctions:** `intersection()` counts eight-neighbours for every skeleton pixel and, where the
  count exceeds two, paints a radius-1 black disc into the mask — erasing a 3×3 hole at each
  junction and splitting the tree into branches.
- **Ordering:** **none.** A raster scan finds the first lit pixel of each branch and
  `vessel_extractor` performs a breadth-first flood fill (`pending_pixels.pop(0)`), appending pixels
  in the order they are *discovered*. A comment dated 2021-10-31 records that the inherited
  sort-and-deduplicate step was disabled, leaving raw discovery order.
- **Smoothing:** none.
- **Consequence:** the trace is a set of pixels per branch, not a path. Every shape measure computed
  from it is affected — see section 4.
- **Source:** [AutoMorph](../projects/automorph.md),
  `M3_feature_zone/retipy/retipy/retina.py`.

### 3.8 retipy — skeleton, flood fill, then sorted by x with duplicates dropped

- **Centreline:** skeleton (`apply_thinning` / `skeletonization`).
- **Junctions:** no junction removal in the upstream version.
- **Ordering:** breadth-first flood fill, then the points are **sorted by their x coordinate** and
  **every repeated x value is discarded** — a step whose own source comment ends in a row of
  question marks.
- **Consequence:** worse than no ordering. Sorting by x imposes a left-to-right sweep on a curve
  that may double back, and keeping one point per x row decimates any vessel running across rows:
  a near-vertical vessel collapses to a handful of points. This is the code every AutoMorph-family
  measurement descends from.
- **Source:** [retipy](../projects/retipy.md),
  [`retipy/retina.py`](https://github.com/alevalv/retipy-python/blob/master/retipy/retipy/retina.py).

**Comparability:** the four decisions in section 1 make these tracers genuinely different
instruments. Erasing junctions (3.5, 3.6, 3.7) yields many short branches; a graph or tree (3.2,
3.3) yields whole vessels; bridging gaps (3.6) invents connections the others do not have. Any
per-vessel or per-segment biomarker is therefore measured over a different population of objects in
each pipeline, before any formula is applied.

## 4. Which biomarkers depend on the trace

| Biomarker | Depends on tracing? | Why |
| --- | --- | --- |
| [Tortuosity](tortuosity.md) | **Critically** | Every variant needs points in path order; the variants that split at inflections need curvature signs along that path |
| [Bifurcation angle](bifurcation-angle.md) | **Critically** | Needs junctions found and branch directions sampled along ordered branches |
| [Junction counts](junction-counts.md) | **Critically** | It is a count *of* the trace's topology |
| [Vessel calibre](vessel-calibre.md) | Strongly, for per-segment values | Perpendicular sampling needs a local direction; whole-image averages need segments to average over |
| [Central retinal equivalents](central-retinal-equivalents.md) | Moderately | Needs a width per vessel crossing a ring, so segments must be identified, but not ordered end to end |
| [Temporal angle](temporal-angle.md) | Moderately | Needs resolved whole vessels to identify the dominant arcades |
| [Vessel area and length](vessel-area-and-length.md) | Length only | Skeleton length depends on the thinning algorithm, not on ordering |
| [Vascular density](vascular-density.md) | **No** | Counts mask pixels |
| [Fractal dimension](fractal-dimension.md) | **No** | Box-counting on the mask |
| [Sparsity](sparsity.md) | **No** | Distance transform of the mask |
| [Cup-to-disc ratio](cup-to-disc-ratio.md) | **No** | Disc and cup masks only |
| [Disc-fovea distance](disc-fovea-distance.md) | **No** | Two landmarks |

The practical reading: a disagreement between two pipelines in density or fractal dimension points
at the **segmentation model**; a disagreement in tortuosity, angles or counts points at the
**tracer**, and can occur with identical masks.

## 5. Units and scale dependence

Not a measurement, but two properties propagate into everything above:

- **Pixel grid:** every skeleton-based tracer inherits staircasing, which inflates arc length and
  corrupts local derivatives. Only 3.1 escapes it by never quantising the centreline.
- **Thresholds in pixels:** the 10-pixel minimum branch length (3.5), the 700-pixel component and
  22-pixel gap (3.6), the radius-1 junction erasure (3.7) and the 20-pixel junction discs (3.4) are
  all absolute pixel values, so their anatomical meaning changes with the model's grid — see the
  grid column in [MODELS.md](../MODELS.md).

## 6. Known defects and where they were fixed

The retipy lineage carries six documented defects in or around tracing. AutoMorph inherited all of
them; its two derivatives fixed different subsets, and neither fixed all. Established by reading the
public code of each project against the papers.

| Defect | retipy | AutoMorph | AutoMorphalyzer | AutoMorphClass |
| --- | --- | --- | --- | --- |
| **6.1** Points sorted by x, repeated x dropped | present | **removed** (2021-10-31) | not applicable — own tracer | not applicable — own tracer |
| **6.2** No path ordering: flood-fill discovery order | present | **present** | **fixed** — depth-first walk from an endpoint | **fixed** — `order_vessel_points` |
| **6.3** No smoothing before curvature, which Hart requires | present | present | **partly** — `_refine_path`, 4-point window | **not fixed** — `np.gradient` on raw pixels |
| **6.4** Second derivative divided by 4 instead of the step size squared | present | present | not applicable — squared curvature removed | **fixed** — `np.gradient` |
| **6.5** Tortuosity density **adds** the count factor where Grisan multiplies | present | present | **knowingly kept** | **fixed** — multiplies |
| **6.6** Tortuosity density drops the vessel after the last inflection | present | present | **present** | **fixed** — final segment included |
| **6.7** Whole-image aggregation is an unweighted mean, where Hart requires arc-length weighting | present | present | **present** — divides by vessel count | **fixed** — length-weighted by default |

Three of these deserve a note.

**6.2 is the headline defect.** It is reported upstream as
[rmaphoh/AutoMorph#19](https://github.com/rmaphoh/AutoMorph/issues/19), still open, and it
invalidates every tortuosity measure AutoMorph reports.

**6.5 is documented in AutoMorphalyzer's own source.** The two lines read:

```python
# return ((n - 1)/curve_length)*sum_segments  # This is the proper formula
return (n - 1)/n + (1/curve_length)*sum_segments # This is not
```

The correct formula is written out, commented, and deliberately not used — presumably to keep
continuity with AutoMorph's output. That is a known deviation rather than an oversight, and it is
the clearest evidence in this catalogue that these pipelines value comparability with their ancestor
over agreement with the paper they cite.

**AutoMorphClass's fixes are real but undocumented.** Its author's only public statement is that the
project "includes fixed tortuosity measures"
([issue #18](https://github.com/rmaphoh/AutoMorph/issues/18)); the code shows four of the six
defects addressed, with no comment saying so. A reader comparing its numbers with AutoMorph's would
have no way to know what changed without reading both implementations line by line.

## 7. Notes

- **The forks diverge, and nobody reconciled them.** AutoMorphalyzer fixed ordering and left the
  formula wrong on purpose; AutoMorphClass fixed the formula, the stencil and the aggregation but
  not the smoothing. Neither validated against the other. Three pipelines that describe themselves
  as AutoMorph therefore produce three different tortuosity numbers from one photograph.
- **Tracing is the cheapest place to improve a biomarker.** It needs no new model, no new data and
  no new annotation — only correct code — which makes it the most tractable target in this atlas.

---

**Links and definitions last checked:** 2026-09-10
