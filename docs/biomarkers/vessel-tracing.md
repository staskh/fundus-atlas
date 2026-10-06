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

The most complete reconstruction in this catalogue, and the only one that offers per-vessel as well
as per-segment measurement. *Traced stage by stage through the pinned commit, 2026-10-01*, because
what it does and does not join turns out to decide several biomarkers:

| Stage | What happens | Where |
| --- | --- | --- |
| **1. Binarise and fill** | threshold at 0.5, then `fill_small_holes(area_threshold=25)` — which fills a background region **only where it is fully enclosed** by vessel and smaller than 25 px | `shared/masks.py` |
| **2. Skeletonise** | `skimage.morphology.skeletonize`, with the optic disc masked out so the tangle over the nerve head cannot create spurious junctions | `fundus/layer.py` |
| **3. Graph** | `sknw.build_sknw` turns the skeleton into a graph, each edge carrying its ordered pixel run; degree-2 nodes are then collapsed so a run of pixels between two junctions is one edge | `shared/graph.py` |
| **4. Root** | `make_trees` takes **one tree per connected component**, rooted at whichever degree-1 node is nearest the disc centre | `fundus/layer.py` |
| **5. Direct and tidy** | a depth-first walk orders every edge away from the root; `correct_digraph(threshold=10)` then deletes spurs under 10 px and merges the two edges either side of the node it removed | `shared/graph.py` |
| **6. Type the nodes** | each node becomes a `Bifurcation`, an `Endpoint` or a plain `Node` by its in/out degree | `shared/graph.py` |
| **7. Spline** | a cubic smoothing spline per segment (default error fraction 0.05), used for arc length, curvature and perpendicular diameter sampling | `shared/segment.py` |
| **8. Resolve into vessels** | `_build_vessels` walks out from each root, and at every bifurcation continues the *vessel* along the daughter with the largest diameter-weighted `agg_value`, merging the remaining daughters as vessels of their own at greater depth | `fundus/layer.py` |

Stage 8 is what "resolved segment" means: a chain of edges concatenated into one `Segment`, so a
biomarker can be computed per branch (stage 5's output) or per whole vessel (stage 8's).

- **Ordering:** from the graph — each edge's points come out along the path by construction.
- **Consequence:** a short segment that cannot support a cubic spline falls back to a
  retipy-derived diameter method — a small piece of the old lineage surviving inside the new
  pipeline.
- **It joins across junctions and never across a gap.** See 3.2.1, which is the part that matters
  for VascX's numbers.
- **Source:** [VascX](../projects/vascx.md), `vascx/shared/masks.py`, `vascx/shared/graph.py`,
  `vascx/fundus/layer.py`, `vascx/shared/segment.py`.

  *Our finding, 2026-10-01:* `fundus/vessel_resolve.py` holds a `RecursiveWeightedAverageResolver`
  implementing stage 8, and `layer.py` builds a `default_vessels_resolver` from it at import — but
  **nothing calls either**. The live path is `_build_vessels`, an inline reimplementation of the
  same algorithm on the directed graph. A reader following the class name is reading dead code.

#### 3.2.1 A broken vessel stays broken — every gap, at every width

**VascX reconnects nothing.** A vessel severed in the mask is measured as two vessels, and no stage
above repairs it. Four stages could have and none does:

| Stage | Why it does not bridge |
| --- | --- |
| 1. `fill_small_holes` | fills only *enclosed* background. A gap in a vessel is open to the background on both sides, so it is never enclosed |
| 3. degree-2 collapse | operates inside the existing skeleton graph; two components have no node in common |
| 5. `correct_digraph` | merges the two edges either side of a node **it has just removed** — there has to be a node there already |
| 8. `_build_vessels` | `merge_edges` opens by checking the chain is consecutive and raises `ValueError("The edges are not consecutive!")` otherwise. It cannot join edges that do not share a node |

*Measured through VascX's own classes*, on one straight vein with a gap cut into it:

| Gap | Connected components | Trees | Segments | Resolved vessels | Longest vessel |
| --- | --- | --- | --- | --- | --- |
| none | 1 | 1 | 1 | **1** | 567 px |
| 1 px | 2 | 2 | 2 | **2** | 293 px |
| 9 px | 2 | 2 | 2 | **2** | 289 px |
| 40 px | 2 | 2 | 2 | **2** | 274 px |

**A single pixel is enough**, and no larger gap behaves differently. One 567-pixel vessel becomes
two of about 293 and 274, each rooted and splined and measured separately, with two extra free ends
between them.

Stage 4 is why the pieces are not simply lost: one tree per *connected component* means the orphan
is kept and rooted at its own nearest end, rather than discarded for not reaching the disc the way
[PVBM's](../projects/pvbm.md) walk discards a vessel that never touches the nerve head. Keeping it
is the better behaviour; it is still two vessels where the retina has one.

**Why this is not hypothetical for VascX specifically.** Its own artery/vein model emits a four-way
softmax, so a pixel is artery *or* vein and an arteriovenous crossing cannot be represented — the
losing vessel is cut at every crossing. The model page has the evidence
([vascx-artery-vein](../models/vascx-artery-vein.md) §10). Compare **AutoMorphClass**, which bridges
gaps up to 22 pixels before tracing (3.6), and **OCULARNet**, whose model segments crossings as
their own class (3.4). VascX does neither, and is the only artery/vein model in this atlas whose
two masks never overlap.

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
| [Branching angle](topology.md) | **Critically** | Needs junctions found and branch directions sampled along ordered branches |
| [Junction counts](topology.md) | **Critically** | It is a count *of* the trace's topology |
| [Vessel calibre](calibre.md) | Strongly, for per-segment values | Perpendicular sampling needs a local direction; whole-image averages need segments to average over |
| [Central retinal equivalents](calibre.md) | Moderately | Needs a width per vessel crossing a ring, so segments must be identified, but not ordered end to end |
| [Temporal angle](topology.md) | Moderately | Needs resolved whole vessels to identify the dominant arcades |
| [Vessel area and length](density.md) | Length only | Skeleton length depends on the thinning algorithm, not on ordering |
| [Vascular density](density.md) | **No** | Counts mask pixels |
| [Fractal dimension](density.md) | **No** | Box-counting on the mask |
| [Sparsity](density.md) | **No** | Distance transform of the mask |
| [Cup-to-disc ratio](landmarks.md) | **No** | Disc and cup masks only |
| [Disc-fovea distance](landmarks.md) | **No** | Two landmarks |

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

Six of these belong to the retipy lineage and one, 6.8, cuts across every pipeline here.
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

### 6.8 Gaps and crossings — a different axis, and VascX sits at one end of it

The six above are the retipy lineage's. This one cuts across every pipeline on the page, because a
tracer's behaviour at a **break in the mask** is a choice nobody documents:

| Pipeline | At a gap in the mask | At an arteriovenous crossing |
| --- | --- | --- |
| [AutoMorphClass](../projects/automorphclass.md) | **bridges** up to 22 px, and connects nearby endpoints, before tracing | treats it as a junction |
| [OCULARNet](../projects/ocularnet.md) | no bridging | **segments crossings as their own class** and dilates each into a region |
| [VascX](../projects/vascx.md) | **never bridges** — one pixel severs a vessel permanently (3.2.1) | **cannot represent one**: its model is a four-way softmax, so the two masks never overlap |
| AutoMorph, AutoMorphalyzer, retipy, ARIA | no bridging | treats it as a junction |

VascX is at the exposed end of both columns, and the two compound: its own segmentation cuts the
losing vessel at every crossing, and its own tracer then measures the two pieces as two vessels.
*Our finding, 2026-10-01*, measured in
[vascx-artery-vein](../models/vascx-artery-vein.md) §10 and §3.2.1 above.

**The direction of the bias is worth stating.** Bridging and non-bridging are not better and worse —
a bridge can join two vessels that were never one, and refusing to bridge can split one that was.
What they are is **incomparable**: a vessel count, an endpoint count or a per-vessel tortuosity from
a bridging pipeline cannot be read against one from a pipeline that refuses, and nothing in either's
output says which you are holding.

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
- [Naim 2026](../papers/naim-2026.md) measured that gap directly on conjunctival
  photographs: networks whose Dice sat in the same band as theirs still missed the annotators'
  centreline by more than a hundred pixels. Overlap is not a proxy for a usable trace.

---

**Links and definitions last checked:** 2026-09-21
