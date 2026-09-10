# Tortuosity

How twisted a vessel is compared with the straight line between its ends. Excessive tortuosity has
been associated with hypertension, diabetes and retinopathy of prematurity, and a straightening or
twisting of the arcades is one of the changes clinicians describe qualitatively.

**This is the biomarker where the atlas's central problem is worst.** The literature defines at
least nine distinct measures under the single word "tortuosity", they are not rescalings of one
another, and the pipelines in this catalogue each output a different subset. A tortuosity value
without its measure named cannot be interpreted, let alone compared.

## 1. What it measures

- **In one sentence:** the extent to which a vessel deviates from a straight path.
- **Also known as:** tortuosity index, arc-chord ratio, tortuosity density, curvature tortuosity.
- **Direction of concern:** higher is generally treated as adverse, though straightened arterioles
  are also described in hypertensive retinopathy.

Two quantities recur below. **Arc length** `s(C)` is the distance travelled along the vessel;
**chord length** `chord(C)` is the straight-line distance between its endpoints. **Curvature** κ at
a point is how sharply the vessel is turning there — the reciprocal of the radius of the circle that
best fits the curve at that point, so a tight bend has large κ and a straight stretch has κ = 0.

### 1.1 Every tortuosity measure in this catalogue

Hart et al. 1999 define seven measures, τ1 to τ7, and name their properties; Grisan et al. define a
different one; three more appear only in implementations. "Scale response" is what happens when the
same shape is photographed γ times larger: 1 means unchanged, 1/γ means it shrinks in proportion.
"Compositional" means the tortuosity of a whole vessel can be recovered from its parts, which Hart
argues is what a clinician's judgement does.

| Measure | Formula | Scale response | Compositional | Implemented in this catalogue as |
| --- | --- | --- | --- | --- |
| **τ1** arc-chord ratio | `s(C) / chord(C)` | 1 | no | retipy/AutoMorph `t2`; VascX `Distance`; PVBM tortuosity index and median tortuosity |
| **τ2** total curvature | `∫κ ds` | 1/γ | no | — |
| **τ3** total squared curvature | `∫κ² ds` | 1/γ² | no | retipy/AutoMorph squared-curvature column (removed by AutoMorphalyzer) |
| **τ4** mean curvature | `∫κ ds / s(C)` | 1/γ | **yes** | — |
| **τ5** mean squared curvature | `∫κ² ds / s(C)` | 1/γ² | **yes** | — |
| **τ6** total curvature over chord | `∫κ ds / chord(C)` | 1/γ | no | — |
| **τ7** total squared curvature over chord | `∫κ² ds / chord(C)` | 1/γ² | no | — |
| **Grisan τ** tortuosity density | `((n−1)/n) · (1/L_c) · Σᵢ (L_c,sᵢ / L_χ,sᵢ − 1)` over `n` constant-sign-curvature subsegments | 1/γ | no | retipy/AutoMorph `td`; AutoMorphalyzer tortuosity density |
| arc-chord × inflection count | `τ1 × (number of curvature sign changes)` | 1 | no | retipy/AutoMorph `t4` |
| mean curvature on a spline | mean of κ sampled along a fitted spline | 1/γ | no | VascX `Curvature` |
| inflection count | number of curvature sign changes | 1 | no | VascX `Inflections` |
| linear-regression tortuosity | R² of a line fitted to sampled points | 1 | no | retipy internal (`t1`), not reported by AutoMorph |

Two things stand out. **Hart's own recommendation — τ4 and τ5, the compositional pair — is
implemented by nobody here.** And AutoMorph reports τ3, which Hart's table marks non-compositional
and which grows with vessel length by construction: for a circular arc of angle θ and radius r,
τ3 = θ/r, so measuring more of the same arc raises it, while τ5 = 1/r² depends on the radius alone.

## 2. Definitions of record

Two papers define everything in the table above.

- Hart WE, Goldbaum M, Côté B, Kube P, Nelson MR. *Measurement and classification of retinal
  vascular tortuosity.* International Journal of Medical Informatics 1999;53(2–3):239–252. DOI:
  [10.1016/S1386-5056(98)00163-4](https://doi.org/10.1016/S1386-5056%2898%2900163-4). The publisher's
  copy is paywalled; a **freely readable copy** is hosted at
  [siue.edu](https://www.siue.edu/~sumbaug/RetinalProjectPapers/Measurement%20and%20classification%20of%20retinal%20vascular%20tortuosity.pdf),
  and the paper's record is on
  [Semantic Scholar](https://www.semanticscholar.org/paper/885dc5636c6a8ce038a9b0756f6695f3db15bb5c).
  Defines τ1–τ7, their scale and compositionality properties, the curvature estimator, and how to
  combine segments.
- Grisan E, Foracchia M, Ruggeri A. *A novel method for the automatic grading of retinal vessel
  tortuosity.* IEEE Transactions on Medical Imaging 2008;27(3):310–319. DOI:
  [10.1109/TMI.2007.904657](https://doi.org/10.1109/TMI.2007.904657) ·
  [PubMed 18334427](https://pubmed.ncbi.nlm.nih.gov/18334427/). The earlier conference version is
  *A novel method for the automatic evaluation of retinal vessel tortuosity*, IEEE EMBS 2003, DOI
  [10.1109/IEMBS.2003.1279902](https://doi.org/10.1109/IEMBS.2003.1279902) — the DOI retipy's code
  cites. **Both published versions are paywalled** and the author-hosted copy that indexes list has
  gone dead; the practical routes are the authors' copy on
  [ResearchGate](https://www.researchgate.net/publication/5518678_A_Novel_Method_for_the_Automatic_Grading_of_Retinal_Vessel_Tortuosity)
  (browser access) and, more usefully for implementers, the authors' own MATLAB reference code at
  [enrigrisan/RET-Tortuosity](https://github.com/enrigrisan/RET-Tortuosity), which carries the
  formula and the algorithm. That repository states no licence.

## 3. Variants

### 3.1 Arc-chord ratio — Hart τ1

- **Formula:** `s(C) / chord(C)`. A straight vessel gives exactly 1; anything curved gives more.
- **Algorithm:** sum the distances between consecutive centreline points for the arc; take the
  distance between the first and last point for the chord.
- **Implemented by:** [AutoMorph](../projects/automorph.md) and [retipy](../projects/retipy.md)
  (`distance_measure_tortuosity`, reported as `t2`), [AutoMorphalyzer](../projects/automorphalyzer.md),
  [VascX](../projects/vascx.md) (`TortuosityMeasure.Distance`), [PVBM](../projects/pvbm.md) (as
  "tortuosity index" over the whole vasculature and "median tortuosity" per vessel).
- **Known weakness, and why the other measures exist:** it is blind to how the curving is
  distributed. One gentle bend and a dozen tight kinks of the same total excess length score
  identically.

### 3.2 Total squared curvature — Hart τ3

- **Formula:** `∫κ² ds` — integrate the square of the curvature along the vessel, so sharp bends
  dominate and the sign of the bend does not matter.
- **Algorithm as the paper prescribes it:** Hart is explicit that the centreline must be smoothed
  first, because a vessel at 45° to the pixel grid is stored as a zigzag whose local derivatives are
  meaningless. The paper low-pass filters the `x` and `y` coordinate sequences independently (two
  passes of the `smooft` routine of Press et al.), then estimates κ as the slope of a least-squares
  line fitted to the tangent angle against arc length over a **sliding window of ten points** —
  not by differencing adjacent pixels.
- **Implemented by:** retipy (`squared_curvature_tortuosity`), reported by AutoMorph.
  **AutoMorphalyzer removed it**, its authors judging it redundant with the other measures — so this
  column exists in AutoMorph output and not in AutoMorphalyzer output.
- **Implementation note:** retipy's version follows neither half of that recipe; see section 9.2.

### 3.3 Arc-chord ratio times inflection count

- **Formula:** τ1 multiplied by the number of times the curvature changes sign, so many small
  wiggles score higher than one smooth arc.
- **Implemented by:** AutoMorph and retipy (`distance_inflection_count_tortuosity`, `t4`).
- Not one of Hart's seven, and no source publication was established for it.

### 3.4 Tortuosity density — Grisan

- **Formula:** `τ = ((n−1)/n) · (1/L_c) · Σᵢ [ L_c,sᵢ / L_χ,sᵢ − 1 ]`, where the vessel is
  partitioned into `n` subsegments of constant curvature sign (the paper calls them *turn curves*),
  `L_c` is the vessel's total arc length, and `L_c,sᵢ` and `L_χ,sᵢ` are subsegment `i`'s arc and
  chord lengths.
- **What it is designed to capture:** two things a clinician reacts to — how far each twist departs
  from its chord (through the ratio term) and how many twists there are (through the partition and
  the count factor). Consequences worth holding onto:
  - **n = 1 gives exactly 0.** A curve that never changes the direction of its bending is
    non-tortuous *by definition* — a straight line, and equally a broad semicircular sweep. This
    measure is about serpentine structure, not curvature magnitude, which is what distinguishes it
    from Hart's τ2–τ7.
  - The count factor `(n−1)/n` is **bounded**, rising 0, ½, ⅔, ¾ … toward 1, so beyond a few twists
    the value is carried by the amplitude term.
  - **Its units are 1/length**, since the ratio term is dimensionless and the only dimension comes
    from `1/L_c`.
- **Algorithm as the paper prescribes it:**
  1. fit a **cubic smoothing spline** through the centreline samples, giving a curve that is at
     least continuously differentiable — the stated reason is that raw pixel samples give poor
     information about vessel direction and its derivatives;
  2. evaluate curvature on the spline against the curvilinear coordinate;
  3. partition by **hysteretic thresholding of the curvature sign**, so each subsegment has
     quasi-constant sign and a tolerance band absorbs noise around zero;
  4. **split runs of near-zero curvature in half**, giving one half to the preceding turn curve and
     one to the following. The paper is explicit that straight stretches must not be discarded:
     two twists joined by a long straight run would otherwise score the same however far apart they
     sit.
- **Implemented by:** AutoMorph and retipy (`tortuosity_density`, `td`), AutoMorphalyzer.
- **Implementation note:** retipy's version departs from the formula and skips steps 1, 3 and 4; see
  section 9.4. The count factor also differs between the authors' own sources — the journal paper's
  `(n−1)/n`, and `n−1` in their MATLAB code — a reweighting by twist count rather than a different
  measure, but one that changes the ordering between images because `n` varies per vessel.

### 3.5 Mean curvature on a spline, and inflection count — VascX

- **Formula:** the mean of κ sampled along a fitted spline; and, separately, the count of curvature
  sign changes.
- **Implemented by:** VascX (`TortuosityMeasure.Curvature` and `TortuosityMeasure.Inflections`).
- Closest in spirit to Hart's τ4, but normalised by sample count rather than arc length, and no
  source publication is claimed for the exact form.

**Comparability:** none of these are interchangeable, and the differences are not monotonic — two
vessels can be ranked one way by τ1 and the other way by tortuosity density, because one measures
total excess length and the other serpentine structure per unit length. On top of the measure, VascX
exposes three further choices that change the number: per **segment** or per whole **vessel**
(`TortuosityMode`), arc length from a **spline** or from the **skeleton** (`LengthMeasure`), and
optional caps on segment length and on implausible values. A VascX column name encodes those
choices; a value quoted without them is not reproducible.

### 3.6 Example code

- [retipy `tortuosity_measures.py`](https://github.com/alevalv/retipy-python/blob/master/retipy/retipy/tortuosity_measures.py)
  — τ1, τ1×inflections, τ3 and tortuosity density, the lineage behind the whole AutoMorph family.
- [VascX `tortuosity.py`](https://github.com/Eyened/retinalysis-vascx/blob/main/vascx/fundus/features/tortuosity.py)
  — distance, curvature and inflection variants with the mode and length options.
- [PVBM `GeometryAnalysis.py`](https://github.com/aim-lab/PVBM/blob/main/PVBM/GeometryAnalysis.py)
  — tortuosity index and median tortuosity.
- [enrigrisan/RET-Tortuosity](https://github.com/enrigrisan/RET-Tortuosity) — the Grisan authors'
  own MATLAB implementation, the closest thing to a reference for tortuosity density.

## 4. Inputs required

- **Segmentations:** vessels, or artery/vein for per-class tortuosity.
- **Derived geometry:** a skeleton; **vessel segments split at junctions**; the ordered sequence of
  points along each segment; often a spline fit; inflection points for variants 3.2, 3.3 and 3.6.
- **Tracing:** this biomarker is a measurement of the trace, not of the mask — see
  [vessel-tracing.md](vessel-tracing.md) for how each project builds it, and which defects were
  fixed where.
- **Why this matters:** the ordered point sequence is where tortuosity is won or lost. Every formula
  above assumes the points arrive in path order, and a segmentation offers no such ordering — the
  code must trace it. Section 9 is what happens when that tracing is wrong.

## 5. Measurement region

- **AutoMorph:** whole image, and zones B and C.
- **AutoMorphalyzer:** all zones — its authors specifically extended tortuosity to every zone while
  leaving fractal dimension, density and global calibre whole-image only.
- **VascX:** whole image or any grid field, including hemifields.
- **PVBM:** the annulus between 2 and 3 optic disc radii.

## 6. Units and scale dependence

- **Unit as computed:** dimensionless for 3.1–3.3 and 3.5; a count for 3.6; a mixed quantity for
  3.2.
- **Depends on the pixel grid:** **Yes, subtly.** The ratio itself is scale-free, but the skeleton
  is not: at a coarser grid a gentle curve becomes a staircase of pixels, and arc length measured
  along a staircase is systematically longer than the true curve. Tortuosity therefore drifts with
  grid size even though its units cancel — worse for thin vessels and coarse grids.
- **Depends on a physical scale:** No.
- **Depends on field of view:** Yes, in aggregate: a wider field admits more peripheral vessels,
  which are more tortuous.
- **Scale-invariant:** in principle yes, in practice only when comparing masks from the same grid.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [retipy](../projects/retipy.md) | 3.1, 3.2, 3.3, 3.4 | `retipy/tortuosity_measures.py` | Original |
| [AutoMorph](../projects/automorph.md) | 3.1, 3.2, 3.3 (paper also cites 3.4) | retipy's module, vendored | Reuses retipy |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | 3.1, 3.3 | `automorph/measure/get_vessel_coords.py`, `measure.py` | Rewritten from retipy with Numba and a depth-first traversal |
| [AutoMorphClass](../projects/automorphclass.md) | AutoMorph's set | `src/pytorch_automorph/tortuosity_utils.py` | Reimplemented |
| [VascX](../projects/vascx.md) | 3.1, 3.5, 3.6, each with mode and length options | `vascx/fundus/features/tortuosity.py` | Original |
| [PVBM](../projects/pvbm.md) | 3.1, as index and median | `PVBM/GeometryAnalysis.py`, `PVBM/helpers/tortuosity.py` | Original; presented as a contribution of the PVBM paper |
| [OCULARNet](../projects/ocularnet.md) | via PVBM | `utils/GeometricalVBMs.py` | Modified copy of PVBM |

## 8. Sensitivity and failure modes

- **Segment splitting is decisive.** Tortuosity is computed per segment, so a junction missed or
  invented changes what is being measured, not just how precisely.
- **Skeleton staircasing** inflates arc length, as in section 6.
- **Short segments are unstable:** a few pixels' worth of vessel has a meaningless arc-chord ratio,
  which is why implementations impose minimum lengths (VascX's `min_numpoints`) and maximum
  plausible values (`max_tortuosity`).
- **Reported reproducibility:** the VascX toolbox paper reports intraclass correlations above 0.5
  for most biomarkers, while noting "important differences in the level of robustness of different
  biomarkers" — their words, and tortuosity variants are exactly where such differences would show.

## 9. Known defects

### 9.1 Vessel points returned in discovery order, invalidating every retipy tortuosity measure

- **What is wrong:** retipy's `vessel_extractor` collects each segment with a breadth-first flood
  fill (`pending_pixels.pop(0)`), so the points come back in the order they were *discovered*, not
  in path order along the vessel — and the raster scan seeds each segment mid-vessel rather than at
  an end, so the fill expands both ways at once. Every measure above consumes those points as an
  ordered curve.
- **What it affects:** all retipy-derived tortuosity outputs — arc length, chord length, squared
  curvature and the inflection-point splitting in tortuosity density. In AutoMorph that is the `t2`,
  `t4` and `td` columns.
- **Evidence:** [rmaphoh/AutoMorph#19](https://github.com/rmaphoh/AutoMorph/issues/19), with a
  before-and-after benchmark against FIVES expert annotations.
- **Status:** **open** in retipy (dormant since 2019) and in AutoMorph. **Fixed in both
  derivatives, verifiably in their code:** [AutoMorphalyzer](../projects/automorphalyzer.md) walks
  each branch depth-first from an endpoint (`_reorder_coords` in
  `automorph/measure/get_vessel_coords.py`), and [AutoMorphClass](../projects/automorphclass.md)
  walks an occupancy grid from a degree-one endpoint (`order_vessel_points`, applied in
  `_tortuosity_per_window` before any measure is computed). The two repairs were made independently
  and neither validated against the other, so **AutoMorph, AutoMorphalyzer and AutoMorphClass
  tortuosity values must not be pooled.** See
  [vessel-tracing.md](vessel-tracing.md) section 6 for the full defect-by-fork matrix.

### 9.2 The squared-curvature estimator differences raw pixels, which Hart's paper forbids

- **What is wrong:** `squared_curvature_tortuosity` computes κ from three-point centred differences
  applied directly to the integer skeleton coordinates. Hart's paper prescribes smoothing the
  coordinate sequences first and then estimating κ by least-squares regression over a ten-point
  window, precisely because an unsmoothed pixel chain zigzags (section 3.2).
- **What it affects:** AutoMorph's squared-curvature column.
- **Our own check:** transcribing retipy's stencils and running them on a rasterised semicircle,
  where `∫κ² ds = π/r` exactly, returns values between roughly 1× and 90× the analytic answer across
  radii from 50 to 400 pixels, with no consistent relationship to `r`. The error is not a calibration
  factor that could be divided out — it is quantisation noise, and because κ² cannot be negative the
  noise accumulates as a one-sided bias, so longer vessels are affected more rather than averaging
  out. This is our measurement, from public code; it is not reported by the projects themselves.
- **Status:** open.

### 9.3 The second-derivative stencil divides by 4 instead of by the step size squared

- **What is wrong:** retipy's `derivative2_centered_h1` returns
  `(y[i+1] − 2y[i] + y[i−1]) / 4`. The centred second difference at unit spacing divides by `h² = 1`,
  so the value is four times too small.
- **What it affects:** the same squared-curvature column.
- **Our own check:** correcting the divisor multiplies the reported value by exactly 4 on the
  synthetic curves above — which makes it **further** from the analytic answer, because the error in
  9.2 dominates and the wrong divisor happens to damp it. **Do not fix this one on its own.**
- **Status:** open in retipy and AutoMorph; not applicable to AutoMorphalyzer, which removed the
  squared-curvature measure; **fixed** in AutoMorphClass, which computes curvature with
  `np.gradient` and so uses the correct spacing.

### 9.4 Tortuosity density adds the count factor where the paper multiplies, and drops the last subsegment

- **What is wrong:** retipy's `tortuosity_density` returns `(n−1)/n + (1/L_c)·Σ(Rᵢ − 1)`. Grisan's
  formula **multiplies** the amplitude sum by `(n−1)/n` (section 3.4). Because the amplitude term
  carries units of 1/length it is numerically small, so the reported value is dominated by the
  additive constant — that is, mostly a function of how many sign changes were counted, with the
  vessel's actual twisting a minor correction. Separately, the loop iterates over the inflection
  points only, so the stretch of vessel after the last inflection is never included in the sum.
- **Also missing:** the spline fit, the hysteresis band on the curvature sign, and the halving of
  zero-curvature runs — steps 1, 3 and 4 of the published algorithm. Inflections are instead taken
  from sign changes of a first difference of the raw pixel coordinates.
- **What it affects:** the `td` column in AutoMorph and in AutoMorphalyzer.
- **Status:** open in retipy and AutoMorph. **AutoMorphalyzer keeps it knowingly** — its source
  carries the correct formula as a comment above the incorrect line, annotated "This is the proper
  formula" and "This is not" — and still drops the final segment. **AutoMorphClass fixed both**: it
  multiplies by `(n−1)/n` and includes the stretch after the last inflection. Established by reading
  the public code against the paper.

### 9.5 Whole-image aggregation is an unweighted mean, where the paper requires arc-length weighting

- **What is wrong:** Hart's paper states that a whole vessel's tortuosity must weight each segment
  by the fraction of arc length it contributes — "weighted additivity" — and says explicitly that
  averaging the tortuosities of constituent segments is inconsistent with the definition. retipy's
  `evaluate_window` takes a plain mean over vessels.
- **Why it matters here:** junction splitting cuts each tree into many branches of very different
  lengths, so an unweighted mean lets a three-pixel twig count as much as a major arcade.
- **Status:** open in retipy, AutoMorph and AutoMorphalyzer, which divides its totals by a plain
  vessel count. **Fixed in AutoMorphClass**, whose `_tortuosity_per_window` weights each vessel by
  its curve length by default. VascX also offers a length-weighted aggregator, which is the
  behaviour Hart prescribes.

## 10. Notes

- Of everything in this catalogue, this is the biomarker where "same name, different number" does
  the most damage, and the one where an independent comparison would be most valuable.
- A practical rule for reading a paper: if it reports "tortuosity" from AutoMorph and names no
  measure, it means one of `t2`, `t4` or `td`, computed with the defects in section 9 still in
  place.
- If you are choosing a measure rather than inheriting one, Hart's τ4 and τ5 are the pair the
  original paper recommends and the pair nobody here implements — which makes them the obvious
  candidate for this atlas's own comparison work.

---

**Links and definitions last checked:** 2026-09-10
