# Biomarker names, and what each project calls them

**A biomarker name is not a definition.** "Tortuosity" names at least eleven formulas in this
catalogue, "CRAE" two, and papers usually report the name and omit the choice. Two numbers under
the same heading are comparable only when the definition, the region they were measured over, the
structure they were measured on and the statistic that pooled them all match.

So this repository fixes a **canonical name** for each measurement it can compare, and maps every
project's own column onto one. The canonical names live in `src/biomarkers/canonical.py`, where a
typo is an error rather than a row that silently matches nothing.

**Each project's mapping lives in its own adapter** — `src/biomarkers/<slug>.py`, beside the calls
it describes. The evidence a run writes is keyed by the **project's own column names**, and the
mapping is applied in the analysis, so a mapping that turns out to be wrong is corrected without
re-measuring anything.

## 1. How a canonical name is built

```
family / biomarker / structure / [roi] / [statistic]
```

| Part | Meaning | Default |
| --- | --- | --- |
| **family** | one of the five pages in [biomarkers/](biomarkers/) — the kind of thing being measured | required |
| **biomarker** | *which definition*, because the family name does not say | required |
| **structure** | `artery`, `vein`, `vessels` for the two together, or `both` for a measurement that is inherently a ratio | required where the family has one |
| **roi** | the region it was measured within — see [regions of interest](biomarkers/regions-of-interest.md) | `fov` |
| **statistic** | how per-segment or per-vessel values were pooled | `median` |

So `tortuosity/hart-tau1/artery` is the median τ1 over the arteries in the whole field of view, and
`calibre/width/vein/B/mean` says all five parts outright.

**What may be left out, and what is written out.** A short form is a name a reader may *write*, and
`tortuosity/hart-tau1/artery` and `tortuosity/hart-tau1/artery/median` are the same measurement. But
where this repository *records* a number — the synthetic shapes' ground truth, an adapter's mapping,
a results table — it spells the statistic out, because a file holding both spellings would look like
two quantities and join against neither.

**The statistics.** `mean`, `median`, `std`, `max`, `min` — and `length-weighted`, which is a mean
weighting each segment by its own arc length, so a long vessel counts for more than a short one. It
is a different number from the plain mean rather than a better one, and it is what VascX's
`lw_diam` and `lw_tort_*` columns report; PVBM and OCULAR return it beside a median. Which
statistics a biomarker admits is on its family page: a quantity measured *along* a vessel takes the
length-weighted one, an angle at a junction does not.

**A family overrides these rules.** `calibre`'s equivalents *require* a region — there is no
field-of-view-wide CRAE — and `landmarks` has no structure at all, because the optic disc is not an
artery or a vein.

**Segments or whole vessels goes in the name, not in the tracing.** `tortuosity/hart-tau1` is
measured over segments between intersection points; `tortuosity/vessel-hart-tau1` is measured over
whole vessels, each root-to-tip path from the optic disc counting as one. They pool different
populations and are different numbers. How an implementation finds either is its own business, and
is documented on its project page.

**Every length is in microns.** Never pixels — see each family page's units section, and
`PLAN-BIOMARKER.md` §2.2 for why.

## 2. Every name, and the unit it is in

Generated from `src/biomarkers/canonical.py`, which is the record. A unit stated here and a unit
the shapes convert by cannot drift apart, because both are read from the same field — and that is
not hypothetical: Grisan's density was declared dimensionless in a table for a week while its own
derivation two pages away called it an inverse length.

A **whole-vessel form** means the biomarker also exists as `family/vessel-<biomarker>`, measured
over root-to-tip paths rather than over segments between intersection points.

<!-- generated: units -->
**[`calibre`](biomarkers/calibre.md)**

| Canonical name | What it measures | Unit | Statistics | Whole-vessel form |
| --- | --- | --- | :-: | :-: |
| `calibre/width/{artery,vein,vessels}` | the width of a vessel, measured along it | µm | `mean`, `median`, `std`, `length-weighted` | — |
| `calibre/CRE-knudtson/{artery,vein}` | Knudtson's equivalent — CRAE on arteries, CRVE on veins | µm | — | — |
| `calibre/CRE-hubbard/{artery,vein}` | Hubbard's equivalent over the same ring | µm | — | — |
| `calibre/AVR-knudtson/both` | arteriolar over venular equivalent, both Knudtson | 1 | — | — |
| `calibre/AVR-hubbard/both` | the same, both Hubbard | 1 | — | — |
| `calibre/AVR-ratio/both` | mean artery width over mean vein width, no ring and no equivalent | 1 | — | — |

**[`tortuosity`](biomarkers/tortuosity.md)**

| Canonical name | What it measures | Unit | Statistics | Whole-vessel form |
| --- | --- | --- | :-: | :-: |
| `tortuosity/hart-tau1/{artery,vein,vessels}` | arc length over chord length; 1 for a straight vessel | 1 | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/hart-tau2/{artery,vein,vessels}` | total curvature, ∫κ ds — the total turning angle | 1 | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/hart-tau3/{artery,vein,vessels}` | total squared curvature, ∫κ² ds | 1/µm | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/hart-tau4/{artery,vein,vessels}` | mean curvature, ∫κ ds / s — compositional | 1/µm | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/hart-tau5/{artery,vein,vessels}` | mean squared curvature, ∫κ² ds / s — compositional | 1/µm² | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/hart-tau6/{artery,vein,vessels}` | total curvature over chord | 1/µm | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/hart-tau7/{artery,vein,vessels}` | total squared curvature over chord | 1/µm² | `mean`, `median`, `std`, `length-weighted` | yes |
| `tortuosity/grisan-density/{artery,vein,vessels}` | Grisan's density over constant-sign subsegments | 1/µm | `mean`, `median`, `std`, `length-weighted` | — |
| `tortuosity/inflection-count/{artery,vein,vessels}` | how many times the curvature changes sign | 1 | — | — |
| `tortuosity/arc-chord-times-inflections/{artery,vein,vessels}` | τ1 multiplied by the inflection count | 1 | `mean`, `median`, `std`, `length-weighted` | — |
| `tortuosity/spline-curvature/{artery,vein,vessels}` | curvature sampled along a fitted spline | 1/µm | `mean`, `median`, `std`, `length-weighted` | — |

**[`density`](biomarkers/density.md)**

| Canonical name | What it measures | Unit | Statistics | Whole-vessel form |
| --- | --- | --- | :-: | :-: |
| `density/area/{artery,vein,vessels}` | total vessel area | µm² | — | — |
| `density/skeleton-length/{artery,vein,vessels}` | total centreline length | µm | — | — |
| `density/over-fov/{artery,vein,vessels}` | vessel area as a fraction of the field of view | 1 | — | — |
| `density/over-image/{artery,vein,vessels}` | the same over the whole frame, lit or not — it names its own denominator | 1 | — | — |
| `density/sparsity/{artery,vein,vessels}` | distance from retina to the nearest vessel | µm | `mean`, `max` | — |
| `density/box-counting/{artery,vein,vessels}` | box-counting dimension | 1 | — | — |
| `density/multifractal-d0/{artery,vein,vessels}` | capacity dimension | 1 | — | — |
| `density/multifractal-d1/{artery,vein,vessels}` | information dimension | 1 | — | — |
| `density/multifractal-d2/{artery,vein,vessels}` | correlation dimension | 1 | — | — |

**[`topology`](biomarkers/topology.md)**

| Canonical name | What it measures | Unit | Statistics | Whole-vessel form |
| --- | --- | --- | :-: | :-: |
| `topology/junctions/{artery,vein,vessels}` | how many places three or more branches meet | 1 | — | — |
| `topology/endpoints/{artery,vein,vessels}` | how many free ends the network has | 1 | — | — |
| `topology/components/{artery,vein,vessels}` | how many separate pieces the network is in | 1 | — | — |
| `topology/branching-angle/{artery,vein}` | the angle between the two daughter vessels at a bifurcation | degrees | `mean`, `median`, `std` | — |
| `topology/temporal-angle/{artery,vein}` | the angle between the superior and inferior temporal arcades | degrees | `mean`, `median`, `std` | — |

**[`landmarks`](biomarkers/landmarks.md)**

| Canonical name | What it measures | Unit | Statistics | Whole-vessel form |
| --- | --- | --- | :-: | :-: |
| `landmarks/CDR-vertical` | the cup's vertical diameter over the disc's | 1 | — | — |
| `landmarks/CDR-area` | the cup's area over the disc's | 1 | — | — |
| `landmarks/disc-fovea-distance` | the straight-line distance from the disc centre to the fovea | µm | — | — |
<!-- /generated -->

## 3. What each project computes

**✅ means a project implements this and we believe its number is comparable.** ⚠️ means it computes
something close that is **not** interchangeable, for a reason given in the note — a different
region, a different unit, or a formula that differs where it matters. A blank means it does not
compute it at all.

**Both marks are claims, and the [synthetic benchmark](benchmarks/biomarker-synthetic-docs.md) is
what tests them.** A mapping says *we believe this column computes this quantity*, usually from
reading the source rather than the documentation, and this repository has been wrong three times
and withdrawn the mapping each time.

### 3.1 [`calibre`](biomarkers/calibre.md) — how wide the vessels are

| Canonical name | AutoMorph | PVBM | VascX | Note |
| --- | :-: | :-: | :-: | --- |
| `calibre/width/{artery,vein,vessels}` | ✅ | | ✅ | AutoMorph's `average_width`, VascX's calibre. Statistic `mean` in both |
| `calibre/CRE-knudtson/{artery,vein}` | ⚠️ | ⚠️ | ⚠️ | All three return **pixels**, not microns; AutoMorphalyzer reports it per zone and VascX medians across several circles |
| `calibre/CRE-hubbard/{artery,vein}` | | ⚠️ | | PVBM applies **micron-fitted constants to pixel widths** — a defect, not a unit conversion |
| `calibre/AVR-knudtson/both` | | ⚠️ | | Inherits CRE-knudtson's units |
| `calibre/AVR-hubbard/both` | | ⚠️ | | Inherits CRE-hubbard's defect |
| `calibre/AVR-ratio/both` | | | | Mean artery width over mean vein width, no ring. Nothing catalogued computes it |

### 3.2 [`tortuosity`](biomarkers/tortuosity.md) — the shape of a vessel's path

| Canonical name | AutoMorph | PVBM | VascX | Note |
| --- | :-: | :-: | :-: | --- |
| `tortuosity/hart-tau1/{artery,vein,vessels}` | ⚠️ | ✅ | ⚠️ | AutoMorph returns **0.0 on failure**, which is impossible for an arc over a chord and averages in as a measurement. VascX subdivides at a configurable `max_segment_len`, so it pools a different population |
| `tortuosity/hart-tau2/{artery,vein,vessels}` | | | | Total curvature. In Hart's table; nothing catalogued computes it |
| `tortuosity/hart-tau3/{artery,vein,vessels}` | | | | Total squared curvature, in **1/µm** |
| `tortuosity/hart-tau4/{artery,vein,vessels}` | | | | Mean curvature, in **1/µm**. Compositional, and the closest thing to what VascX's spline curvature attempts |
| `tortuosity/hart-tau5/{artery,vein,vessels}` | | | | Mean squared curvature, in **1/µm²** |
| `tortuosity/hart-tau6/{artery,vein,vessels}` | | | | Total curvature over chord, in **1/µm** |
| `tortuosity/hart-tau7/{artery,vein,vessels}` | | | | Total squared curvature over chord, in **1/µm²** |
| `tortuosity/grisan-density/{artery,vein,vessels}` | ⚠️ | | | Non-zero where the geometry requires exactly nought, by up to 1.00 on a straight vessel |
| `tortuosity/inflection-count` | | | | |
| `tortuosity/arc-chord-times-inflections` | | | | |
| `tortuosity/spline-curvature/{artery,vein}` | | | ⚠️ | VascX only; moves by 280% under rotation |
| `tortuosity/vessel-*` | | | | The whole-vessel forms. Nothing catalogued computes them yet |

### 3.3 [`density`](biomarkers/density.md) — how much vasculature there is, and how it is spread

| Canonical name | AutoMorph | PVBM | VascX | Note |
| --- | :-: | :-: | :-: | --- |
| `density/over-fov/{artery,vein,vessels}` | | | ⚠️ | VascX measures over a disc-centred circle, not the field of view |
| `density/over-image/{artery,vein,vessels}` | ✅ | | | |
| `density/area/{artery,vein,vessels}` | | ⚠️ | | PVBM returns **pixels squared** |
| `density/skeleton-length/{artery,vein,vessels}` | | ⚠️ | | PVBM returns **pixels**, and its rooted walk excludes vessels that do not reach the disc |
| `density/sparsity/{artery,vein,vessels}` | | | ⚠️ | VascX only, and **not comparable**: its `mean_sparsity` is normalised by the optic-disc-to-fovea distance, so it is a dimensionless ratio rather than the distance in microns this name means |
| `density/box-counting/{artery,vein,vessels}` | ✅ | | | |
| `density/multifractal-d0/{artery,vein}` | | ✅ | | PVBM's `capacity_dimension`. Its three dimensions are of the **multifractal** analysis, not a plain box count |
| `density/multifractal-d1/{artery,vein}` | | ✅ | | PVBM's `entropy_dimension` |
| `density/multifractal-d2/{artery,vein}` | | ✅ | | PVBM's `correlation_dimension` |

### 3.4 [`topology`](biomarkers/topology.md) — where the network branches and how it connects

| Canonical name | AutoMorph | PVBM | VascX | Note |
| --- | :-: | :-: | :-: | --- |
| `topology/junctions/{artery,vein,vessels}` | | ✅ | | |
| `topology/endpoints/{artery,vein,vessels}` | | ⚠️ | | PVBM's rooted walk calls the end at the disc a *start point*, so its count excludes it — a straight vessel reads 1 where the geometry requires 2 |
| `topology/components/{artery,vein,vessels}` | | | | |
| `topology/branching-angle/{artery,vein}` | | ⚠️ | | PVBM medians **every pairwise angle at every junction**, the trunk included — not the angle between daughters |
| `topology/temporal-angle/{artery,vein}` | | | ✅ | VascX only, statistic `median` |

### 3.5 [`landmarks`](biomarkers/landmarks.md) — the optic nerve head and the fovea

| Canonical name | AutoMorph | PVBM | VascX | Note |
| --- | :-: | :-: | :-: | --- |
| `landmarks/CDR-vertical` | | | | Computed from disc and cup masks; no biomarker adapter here computes it yet |
| `landmarks/CDR-area` | | | | |
| `landmarks/disc-fovea-distance` | | | ⚠️ | VascX returns pixels, and reports two variants — to the retina's centre and to the fovea |

## 4. What each project computes that has no canonical name

A quantity here is **measured and stored under the project's own name**, and appears in no
comparison. That is a gap in the catalogue rather than a reason to discard a measurement: each one
is either a biomarker nobody else computes, or a mapping nobody has made yet.

### 4.1 AutoMorph, AutoMorphalyzer, AutoMorphClass

| Their name | What it appears to be |
| --- | --- |
| `squared_curvature_tortuosity` | *AutoMorph and AutoMorphClass.* Mapped to Hart τ3 until a shape showed it off by five orders of magnitude — **it squares nothing**. Mapping withdrawn; what it computes is unread |
| `average_local_calibre@{B,C,whole}` | *AutoMorphalyzer.* A second calibre beside `average_global_calibre`, disagreeing with it by a third of the vessel's width at some angles. Which of the two answers `calibre/width` is unresolved |
| `tortuosity_distance@{B,C}` | *AutoMorphalyzer.* τ1 restricted to a zone — these **will map** once the `roi` part exists |
| `tortuosity_density@{B,C}` | *AutoMorphalyzer.* Grisan density per zone — likewise |
| `CRAE_Knudtson@{B,C,whole}`, `CRVE_Knudtson@{B,C,whole}` | *AutoMorphalyzer.* The equivalents per zone — likewise, and `@whole` is a region the literature does not define |

**Nine of AutoMorphalyzer's fourteen unmapped quantities are region variants** of something already
named, and close when the `roi` part lands.

### 4.2 PVBM

| Their name | What it appears to be |
| --- | --- |
| `tortuosity_index` | Returned beside the median by `GeometryAnalysis` and called a "tortuosity index" in its docstring. The definition is not stated and it is not one of Hart's seven |
| `start_points` | Where the rooted walk begins — one per vessel leaving the optic disc. A count of trunks. With `endpoints` it sums to the catalogued free-end count |
| `singularity_length` | From the multifractal analysis — the width of the singularity spectrum. Nothing else here computes it |
| `median_branching_angle` | Listed above as ⚠️ against `topology/branching-angle`; kept under its own name because it is not the angle between daughters |
| `endpoints` | Listed above as ⚠️; the rooted tip count rather than every free end |

### 4.3 VascX

| Their name | What it appears to be |
| --- | --- |
| `lw_tort_dist_max_segment_len_{0p15,0p25}_…` | Length-weighted τ1 at **two segment-length settings**. The parameter is the segment definition itself, which is why one canonical name cannot hold both |
| `mean_sparsity`, `mean_sparsity_crcl_multiplier_…` | Sparsity over the whole retina and over a disc-centred circle — the second maps once `roi` exists |
| `vd_crcl_multiplier_1p16666666667_full` | Vascular density over that same circle — likewise |
| `median_temporal_angle_{arteries,veins}` | Listed above against `topology/temporal-angle` |
| `disc_fovea_distance_{retina,center_retina}` | Two disc–fovea distances, to different reference points |

`crcl_multiplier_1p16666666667` is **7/6 disc radii written as a float**, and is a region the ARIC
convention does not name. See [regions of interest](biomarkers/regions-of-interest.md).

## 5. Where a mapping has been withdrawn

Three, each found by a synthetic shape rather than by reading a name:

| Column | Was mapped to | Withdrawn because |
| --- | --- | --- |
| `squared_curvature_tortuosity` | `tortuosity/hart-tau3` | off by five orders of magnitude; it squares nothing |
| `median_branching_angle` | the angle between daughters | it medians every pairwise angle at every junction, trunk included, and reads ~120° where the daughters are 60° apart |
| `endpoints` (PVBM, OCULAR) | `topology/endpoints` | their rooted walk excludes the end at the disc |

**A withdrawn mapping is a finding, not an omission.** Each is recorded with its date on the
relevant family page.

---

**Last checked:** 2026-09-30.
