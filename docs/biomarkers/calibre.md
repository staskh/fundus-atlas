# calibre

**How wide the vessels are, and everything built from widths.** Six biomarkers at three levels of
aggregation: the width of a vessel, the equivalent of several widths combined into one trunk-calibre
estimate, and the ratio of two such equivalents.

They are one family because they are one quantity. A central retinal equivalent *is* a weighted
combination of vessel widths, and an arteriovenous ratio *is* one equivalent divided by another — so
an error in a width propagates into both, and reading them apart hides that.

## 1. What it measures

Retinal arterioles narrow and venules widen with systemic vascular disease, and the two move
independently, which is why the ratio between them carries information neither width does alone.
Narrowed arterioles have been associated with hypertension and with stroke risk; widened venules
with inflammation and with diabetic retinopathy. A single vessel's width is noisy; the equivalents
exist to summarise the six largest of each class into one number per eye.

## 2. The canonical names

| Name | What it is | Statistic |
| --- | --- | --- |
| `calibre/width/{artery,vein,vessels}` | the width of a vessel, measured along it | `mean`, `median`, `std` |
| `calibre/CRE-knudtson/{artery,vein}` | Knudtson's equivalent — CRAE on arteries, CRVE on veins | none |
| `calibre/CRE-hubbard/{artery,vein}` | Hubbard's equivalent over the same ring | none |
| `calibre/AVR-knudtson/both` | arteriolar over venular equivalent, both Knudtson | none |
| `calibre/AVR-hubbard/both` | the same, both Hubbard | none |
| `calibre/AVR-ratio/both` | mean artery width over mean vein width, **no ring and no equivalent** | none |

**`mean` and `median` are statistics, not biomarkers.** `calibre/width/artery` with statistic
`mean` and the same name with `median` are one measurement pooled two ways, and the name says which.
Width also admits `length-weighted` — each segment counted in proportion to its own arc length,
which is what VascX's `lw_diam` columns report and a materially different number wherever the wide
vessels are the short ones.

**The equivalents require a region.** There is no field-of-view-wide CRAE: it is defined over an
annulus around the disc, and a name without one is an error rather than a default. See
[regions of interest](regions-of-interest.md).

## 3. Definitions of record

- **Width** has no single origin — it is what every calibre paper measures. The closest thing to a
  definition of record for the *edge-based* approach is [Bankhead 2012](../papers/bankhead-2012.md),
  which measures from image edges rather than from a mask.
- **The equivalents** are [Hubbard 1999](../papers/hubbard-1999.md), from the ARIC study, revised by
  [Knudtson 2003](../papers/knudtson-2003.md).

### 3.1 Hubbard against Knudtson — they are not interchangeable

| | Hubbard 1999 | Knudtson 2003 |
| --- | --- | --- |
| Form | fitted constants **and an additive term** | purely multiplicative, `k·√(w₁²+w₂²)` with k = 0.88 arteries, 0.95 veins |
| Vessel count | drifts with how many branches were found | fixed at the **six largest** of each class |
| Scale | constants fitted **in microns** — the input must be microns | scale-free by construction |

Knudtson's revision exists because Hubbard's drifts with vessel count. **A value under either name
is meaningless without saying which**, and the two are not convertible.

## 4. Inputs required

Artery/vein masks, and for the equivalents an optic disc segmentation to place the ring. Width
needs a centreline and a way to measure across it — see [vessel tracing](vessel-tracing.md), which
is the implementation's business and documented on each project page.

## 5. Measurement region

`fov` by default for width. **Required** for the equivalents, and the conventions differ between
implementations by a factor of two depending on whether radii are stated in disc *radii* from the
centre or disc *diameters* from the margin. That trap, and each implementation's choice, is on the
[regions of interest](regions-of-interest.md) page.

## 6. Units and scale dependence

**Microns.** Width, and both equivalents, are lengths and are reported in µm — never pixels. The
two AVR forms and `AVR-ratio` are dimensionless.

This rule fixes an incoherence the catalogue carried: **Hubbard's equivalents come out in microns
and Knudtson's in pixels**, because Hubbard's constants force a conversion and Knudtson's
multiplicative form returns whatever the widths were. Two variants of one biomarker in different
units. Under this family's rule both are microns, and an implementation returning pixels is
converted by its adapter using the store's scale.

A length in microns needs a scale, and `PLAN-BIOMARKER.md` §2.2 records where one comes from when a
dataset publishes none — and the circularity that carries.

## 7. Implementations

| Project | What it computes | Source | Lineage |
| --- | --- | --- | --- |
| [ARIA](../projects/aria.md) | width, from image edges | `Vessel_Algorithms/` | Original |
| [VascX](../projects/vascx.md) | width per-segment median; Knudtson equivalents over configurable rings, median across circles | `vascx/fundus/features/caliber.py`, `cre_knudtson.py` | Original |
| [PVBM](../projects/pvbm.md) | both equivalents; AVR left to the user to divide | `PVBM/CentralRetinalAnalysis.py` | Original |
| [OCULARNet](../projects/ocularnet.md) | **no equivalents** — its copy keeps the graph machinery and returns geometry only | `utils/GeometricalVBMs.py` | Modified copy of PVBM |
| [AutoMorph](../projects/automorph.md) | width, both equivalents, both AVRs | retipy's `tortuosity_measures.py` | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Knudtson only, **per zone**; a second "local" calibre beside the global one | `automorph/measure/` | Rewritten from retipy |
| [AutoMorphClass](../projects/automorphclass.md) | width, whole picture and per zone; **no equivalents** — its `main.py` ends `# todo: add calibre features` | `src/pytorch_automorph/feature_calculation.py` | Reimplemented |

**Lineage matters more here than presence.** Three of these run retipy's code or a rewrite of it, so
their errors are correlated and their agreement is not evidence.

## 8. Sensitivity and failure modes

- **Segmentation thickness dominates.** A model that draws slightly thicker vessels shifts every
  calibre value — a property of the model, not the eye.
- **Artery-vein confusion hurts the ratio twice.** A venule counted as an arteriole raises the
  numerator and lowers the denominator at once.
- **Vessel count** drifts Hubbard's equivalents; Knudtson's fixed six exists to stop that, so an
  implementation keeping a different number has changed the measurement.
- **Ring placement** depends on the disc segmentation; a displaced disc moves the ring onto a
  different part of the tree.
- **AVR has a narrow dynamic range**, roughly 0.6 to 0.9, so a few percent of measurement error
  consumes a large share of the between-subject spread. **Report CRAE and CRVE beside it** or the
  finding cannot be interpreted.
- **Small vessels near the resolution limit** are missed or measured at the minimum detectable
  width, biasing whole-image averages upward.
- **Reported reproducibility:** the VascX paper reports intraclass correlation above 0.5 for most
  of its biomarkers between repeat photographs — their measurement, not ours.

## 9. Known defects

- **PVBM applies Hubbard's micron-fitted constants to pixel widths.** *Our finding, 2026-09-20.*
  The additive term does not scale, so the result is not a Hubbard equivalent in any unit. The
  benchmark reports the number rather than repairing it, and the mapping is marked ⚠️ in
  [BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md).
- **AutoMorphalyzer reports two calibres that disagree with each other.** *Our finding, 2026-09-26.*
  `average_global_calibre` and `average_local_calibre` differ by a third of the vessel's width at
  the diagonal angles of a synthetic straight vessel, while agreeing to two decimals at the
  axis-aligned ones. Which of the two answers `calibre/width` is unresolved, so only one is mapped.
  *Re-measured on the run of 2026-11-22:* on the straight vein they now agree to within 3% at 0°
  and 90° and part by about a third of the vessel's width at 45° (global 26.6 px, local 19.8 px,
  against 19.0 px drawn). The global calibre is the one mapped.
- **AutoMorph's width depends on the angle the eye sat at.** *Our finding, 2026-09-27,* on an
  earlier drawing of the shapes: on a straight vein drawn at 24 µm-equivalent width it read
  14.15 px at 0° and 90° and about 25 px at 30° and 60°, and AutoMorphClass showed the same pattern
  in the opposite direction. *Re-measured on the run of 2026-11-22,* the dependence remains but has
  changed shape: on a straight vein the geometry requires to be 120 µm wide, AutoMorph reads 131 µm
  at 0°, 126–141 µm at 15°–30° and 60°–75°, and **340 µm at 45°** — the width taken along the
  image's rows or columns rather than across the vessel. AutoMorphClass now measures the same maps
  and returns the same widths; AutoMorphalyzer shows the same pattern, smaller. AutoMorph's
  length-weighted width moves by up to 132% (veins) as the picture turns, and is up to 184% out
  against the geometry. See the
  [AutoMorph group notebook](../../notebooks/synthetic/biomarker-synthetic-automorph.ipynb) §3.3 and
  the [synthetic results page](../benchmarks/biomarker-synthetic-results.md) §2.2.

---

**Links and definitions last checked:** 2026-09-30.
