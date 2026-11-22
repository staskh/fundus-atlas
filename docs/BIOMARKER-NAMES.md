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
| `density/skeleton-length-rooted/{artery,vein}` | centreline length on the vessels that reach the optic disc | µm | — | — |
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
| `landmarks/CDR-horizontal` | the cup's horizontal diameter over the disc's | 1 | — | — |
| `landmarks/CDR-area` | the cup's area over the disc's | 1 | — | — |
| `landmarks/disc-fovea-distance` | the straight-line distance from the disc centre to the fovea | µm | — | — |
| `landmarks/centring` | what the photograph is centred on | category: `disc`, `macula`, `unknown` | — | — |
<!-- /generated -->

## 3. What each project computes

**Each cell gives the project's own name for the column and a mark.** ✅ means a project implements
this and we believe its number is comparable. ⚠️ means it computes something close that is **not**
interchangeable, for a reason given in the note — a different region, a different unit, or a
formula that differs where it matters. A blank means it does not compute it at all.

**Both marks are claims, and the [synthetic benchmark](benchmarks/biomarker-synthetic-docs.md) is
what tests them.** A mapping says *we believe this column computes this quantity*, usually from
reading the source rather than the documentation, and this repository has been wrong three times
and withdrawn the mapping each time.

**[fundus-biomarkers](projects/fundus-biomarkers.md) has no column in these tables**, because it
needs none: it answers under the canonical names themselves. Section 3.6 says what that means and
what it does not.

**How to read a name.** Each cell spells the **artery** form of the column as the project's own
output writes it. Swap in the token from this table for the vein or all-vessel form, or for another
region:

| Project | Where the name comes from | Artery / vein / all vessels | Region |
| --- | --- | --- | --- |
| [AutoMorph](projects/automorph.md) | its output CSVs, `Results/M3/Disc_Features.csv` and `Macular_Features.csv` | `Artery_…` / `Vein_…` / no prefix | none = whole image; suffix `_zone_b`, `_zone_c` |
| [AutoMorphalyzer](projects/automorphalyzer.md) | its collated feature CSV, `<feature>_<map>_<zone>` | `_artery_` / `_vein_` / `_binary_` | suffix `_whole`, `_B`, `_C` |
| [AutoMorphClass](projects/automorphclass.md) | the feature dictionary `AutoMorphModel` returns | `Artery_…` / `Vein_…` / `Vessel_…` | none = whole image; prefix `ZoneB_`, `ZoneC_` |
| [PVBM](projects/pvbm.md) | the names its geometry and equivalents code gives each value, one call per class | the call, not the name | the equivalents are over zone B |
| [VascX](projects/vascx.md) | its feature names, shipped set `fs_od_centered` | `…_arteries` / `…_veins` / none | `{C}` = `crcl_multiplier_1p16666666667`, a circle at 2.33 disc radii |
| [OCULAR](projects/ocularnet.md) | a bare list from `compute_geomVBMs`, labelled from its `return` statement | the call, not the name | — |

**‡ marks a column the project's own pipeline writes but this repository's adapter does not
reach**, so the synthetic benchmark has not tested it. The mark beside it is a reading of the
source. The adapters store what they do reach under a key built from the upstream function's own
names — `average_width_artery` in AutoMorph and AutoMorphClass, `average_global_calibre@whole_artery`
in AutoMorphalyzer — and `src/biomarkers/<slug>.py` holds that table.

**Zones.** AutoMorph's and AutoMorphalyzer's zone B and zone C are 2–3 and 2–5 disc radii from the
disc centre: exactly this catalogue's `B` and `C` ([regions of
interest](biomarkers/regions-of-interest.md) §4). AutoMorphClass's `ZoneB_` is `B`, but its
`ZoneC_` is **3–5 radii**, a ring outside B rather than the Extended zone, so it has no canonical
name (§4).

**A number is in the units of §2 only after conversion.** Each project reports pixels on a grid
of its own choosing; §6 says which grid and how to convert.

### 3.1 [`calibre`](biomarkers/calibre.md) — how wide the vessels are

| Canonical name | AutoMorph | AutoMorphalyzer | AutoMorphClass | PVBM | VascX | OCULAR | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `calibre/width/{artery,vein,vessels}` | ✅ `Artery_Average_width`; ‡ `…_zone_b`, `…_zone_c` | ✅ `average_global_calibre_artery_whole` | ✅ `Artery_average_width`; ‡ `ZoneB_Artery_average_width` | | ✅ `lw_diam_{C}_full_arteries` | | Statistic `length-weighted` in all four: vessel area over centreline length in the AutoMorph family, VascX's own length weighting. VascX has no all-vessel form. AutoMorphalyzer's `average_local_calibre_*` is a second width, §4 |
| `calibre/CRE-knudtson/{artery,vein}` | ⚠️ ‡ `CRAE_Knudtson_zone_b`, `CRAE_Knudtson_zone_c` | ⚠️ `CRAE_Knudtson_artery_B`, `CRAE_Knudtson_artery_C` | | ⚠️ `crae_knudtson` (B) | ⚠️ `full_cre_arteries` | | Vein form `CRVE_…` throughout: `CRVE_Knudtson_zone_b`, `CRVE_Knudtson_vein_B`, `crve_knudtson`, `full_cre_veins`. AutoMorph's are in µm only when its pipeline is given a real resolution; the rest return pixels (§6). VascX medians over several circles at 2.33 radii, inside zone B rather than across it |
| `calibre/CRE-hubbard/{artery,vein}` | ⚠️ ‡ `CRAE_Hubbard_zone_b`, `CRAE_Hubbard_zone_c` | | | ⚠️ `crae_hubbard` (B) | | | Hubbard's constants were fitted in microns. AutoMorph applies them to widths already multiplied by its resolution, so they hold only when that resolution is real; PVBM applies them to **pixel** widths — a defect, not a unit conversion |
| `calibre/AVR-knudtson/both` | ⚠️ ‡ `AVR_Knudtson_zone_b`, `AVR_Knudtson_zone_c` | ⚠️ ‡ `AVR_B`, `AVR_C` | | ⚠️ `avr_knudtson` (B) | | | A ratio, so no conversion, but it inherits CRE-knudtson's caveats. AutoMorphalyzer's `AVR_B` is `CRAE_Knudtson_artery_B / CRVE_Knudtson_vein_B` |
| `calibre/AVR-hubbard/both` | ⚠️ ‡ `AVR_Hubbard_zone_b`, `AVR_Hubbard_zone_c` | | | ⚠️ `avr_hubbard` (B) | | | Inherits CRE-hubbard's caveats |
| `calibre/AVR-ratio/both` | | | | | | | Mean artery width over mean vein width, no ring. Nothing catalogued computes it |

### 3.2 [`tortuosity`](biomarkers/tortuosity.md) — the shape of a vessel's path

| Canonical name | AutoMorph | AutoMorphalyzer | AutoMorphClass | PVBM | VascX | OCULAR | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tortuosity/hart-tau1/{artery,vein,vessels}` | ⚠️ `Artery_Distance_tortuosity`; ‡ `…_zone_b`, `…_zone_c` | ✅ `tortuosity_distance_artery_whole`, `…_B`, `…_C` | ✅ `Artery_distance_tortuosity` | ✅ `median_tortuosity` | ⚠️ `lw_tort_dist_max_segment_len_0p2_{C}_full_arteries` | ✅ `median_tortuosity`, `length_weighted_tortuosity` | Statistics differ and are part of the name: `mean` in AutoMorph and AutoMorphalyzer, `length-weighted` in AutoMorphClass, `median` in PVBM, `median` and `length-weighted` in OCULAR. AutoMorph returns **0.0 on failure**, which is impossible for an arc over a chord and averages in as a measurement. VascX subdivides at a configurable `max_segment_len`, so it pools a different population |
| `tortuosity/hart-tau2/{artery,vein,vessels}` | | | | | | | Total curvature. In Hart's table; nothing catalogued computes it. The AutoMorph family's `squared_curvature_tortuosity` is the nearest thing, §4 |
| `tortuosity/hart-tau3/{artery,vein,vessels}` | | | | | | | Total squared curvature, in **1/µm** |
| `tortuosity/hart-tau4/{artery,vein,vessels}` | | | | | | | Mean curvature, in **1/µm**. Compositional, and the closest thing to what VascX's spline curvature attempts |
| `tortuosity/hart-tau5/{artery,vein,vessels}` | | | | | | | Mean squared curvature, in **1/µm²** |
| `tortuosity/hart-tau6/{artery,vein,vessels}` | | | | | | | Total curvature over chord, in **1/µm** |
| `tortuosity/hart-tau7/{artery,vein,vessels}` | | | | | | | Total squared curvature over chord, in **1/µm²** |
| `tortuosity/grisan-density/{artery,vein,vessels}` | ⚠️ `Artery_Tortuosity_density`; ‡ `…_zone_b`, `…_zone_c` | ⚠️ `tortuosity_density_artery_whole`, `…_B`, `…_C` | ⚠️ `Artery_tortuosity_density` | | | | Non-zero where the geometry requires exactly nought: AutoMorph and AutoMorphalyzer keep retipy's `(n−1)/n` term and read about 1 on a straight vessel; AutoMorphClass is much closer but still not nought. Statistic `mean`, `length-weighted` in AutoMorphClass |
| `tortuosity/inflection-count` | | | | | | | |
| `tortuosity/arc-chord-times-inflections` | | | | | | | |
| `tortuosity/spline-curvature/{artery,vein}` | | | | | ⚠️ `lw_tort_curv_{C}_full_arteries` | | **Dimensionless**: a mean curvature multiplied by VascX's disc-to-fovea distance. Dividing by that distance recovers a curvature (§6); the mapping was withdrawn (§5) |
| `tortuosity/vessel-*` | | | | | | | The whole-vessel forms. Nothing catalogued computes them yet |

### 3.3 [`density`](biomarkers/density.md) — how much vasculature there is, and how it is spread

| Canonical name | AutoMorph | AutoMorphalyzer | AutoMorphClass | PVBM | VascX | OCULAR | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `density/over-fov/{artery,vein,vessels}` | | | | | ⚠️ `vd_{C}_full_arteries` | | VascX measures over its disc-centred circle, not the field of view |
| `density/over-image/{artery,vein,vessels}` | ✅ `Artery_Vessel_density` | ✅ `vessel_density_artery_whole` | ✅ `Artery_vessel_density` | | | | Over every pixel of the frame, lit or not. The zone forms count only the zone's vessels and still divide by the whole frame, §4 |
| `density/area/{artery,vein,vessels}` | | | | ⚠️ `area` | | ⚠️ `area` | Returned in **pixels squared**; convert with p = 2 (§6) |
| `density/skeleton-length/{artery,vein,vessels}` | | | | | | | PVBM's and OCULAR's length used to be mapped here; it is the rooted length below (§5) |
| `density/skeleton-length-rooted/{artery,vein}` | | | | ✅ `length` | | ✅ `length` | Only the centreline that can be followed back to the optic disc; needs the disc. Returned in **pixels**. Also [fundus-biomarkers](projects/fundus-biomarkers.md) |
| `density/sparsity/{artery,vein,vessels}` | | | | | ⚠️ `mean_sparsity_vessels` | | **Not comparable as it stands**: normalised by the optic-disc-to-fovea distance, so a dimensionless ratio. Multiplying back recovers a distance (§6) |
| `density/box-counting/{artery,vein,vessels}` | ✅ `Artery_Fractal_dimension` | ✅ `fractal_dimension_artery_whole` | ✅ `Artery_fractal_dimension` | | | | Has no unit but depends on the grid it was counted on; compare runs on one grid only |
| `density/multifractal-d0/{artery,vein}` | | | | ✅ `capacity_dimension` | | | PVBM's three dimensions are of the **multifractal** analysis, not a plain box count |
| `density/multifractal-d1/{artery,vein}` | | | | ✅ `entropy_dimension` | | | |
| `density/multifractal-d2/{artery,vein}` | | | | ✅ `correlation_dimension` | | | |

### 3.4 [`topology`](biomarkers/topology.md) — where the network branches and how it connects

| Canonical name | AutoMorph | AutoMorphalyzer | AutoMorphClass | PVBM | VascX | OCULAR | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `topology/junctions/{artery,vein,vessels}` | | | | ✅ `intersections` | | ✅ `intersections` | |
| `topology/endpoints/{artery,vein,vessels}` | | | | ⚠️ `endpoints` | | ⚠️ `endpoints` | The rooted walk calls the end at the disc a *start point*, so a straight vessel reads 1 where the geometry requires 2. `endpoints + start_points` is the catalogued count |
| `topology/components/{artery,vein,vessels}` | | | | | | | |
| `topology/branching-angle/{artery,vein}` | | | | ⚠️ `median_branching_angle` | | ⚠️ `median_branching_angle` | The median of **every pairwise angle at every junction**, the trunk included — not the angle between daughters. OCULAR inherits PVBM's function |
| `topology/temporal-angle/{artery,vein}` | | | | | ✅ `median_temporal_angle_arteries` | | VascX only, statistic `median`. It needs a real fovea, so the adapter leaves it unmapped on the synthetic shapes, which have none |

### 3.5 [`landmarks`](biomarkers/landmarks.md) — the optic nerve head and the fovea

| Canonical name | AutoMorph | AutoMorphalyzer | AutoMorphClass | PVBM | VascX | OCULAR | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `landmarks/CDR-vertical` | ✅ ‡ `CDR_vertical` | ✅ `CDR_vertical` | ✅ `cdr_vertical` | | | | Cup height over disc height, from the bounding boxes of the disc and cup masks, an extent being the last lit index minus the first. *Since 2026-11-22* every adapter is handed the synthetic cup, so AutoMorphalyzer's and AutoMorphClass's are measured; AutoMorph's stays ‡, inside a driver that reads its own result files. AutoMorphClass answers −1 when its sense checks fail, read as no answer; AutoMorphalyzer computes the ratio before its checks and returns it regardless. [fundus-biomarkers](projects/fundus-biomarkers.md) computes it when handed both masks |
| `landmarks/CDR-horizontal` | ✅ ‡ `CDR_horizontal` | ✅ `CDR_horizontal` | ✅ `cdr_horizontal` | | | | The same along the horizontal |
| `landmarks/CDR-area` | | | | | | | fundus-biomarkers, as above |
| `landmarks/centring` | | ⚠️ ‡ `macular_centred` | | | | | **A category, not a number**: `disc`, `macula` or `unknown`. AutoMorphalyzer's is a yes/no for macula-centred, with no `unknown`. fundus-biomarkers computes the canonical one |
| `landmarks/disc-fovea-distance` | | | | | ⚠️ `disc_fovea_distance_retina` | | VascX returns pixels, or mm when given a scale, and reports a second variant, `disc_fovea_distance_center_retina`, to a different reference point |

### 3.6 fundus-biomarkers — the canonical implementation

[fundus-biomarkers](projects/fundus-biomarkers.md) is Pheno's reference implementation of this
catalogue. **It is written against these names**: every one of its 633 answers is spelled as a
canonical name, `family/biomarker/structure/[roi]/[statistic]`, and every one is in the vocabulary.
So there is nothing to map. Where the tables above need a column per project, because each
project's own column has to be matched to a name, this project's column would match every name it
covers exactly, and it is left out rather than filled with ✅.

**What it covers:**

- every catalogued biomarker of `calibre`, `tortuosity`, `density` and `topology`, on `artery` and
  `vein` (and `both` for the ratios), over the field of view and zones `B` and `C`, with every
  statistic each one admits, and the `vessel-` whole-vessel forms of tortuosity — except
  `density/over-image`, which it answers over the field of view only, the whole frame being its
  denominator;
- in `landmarks`, the three cup-to-disc ratios, computed only when it is handed disc and cup masks,
  and the photograph's `landmarks/centring`;
- **not** `topology/temporal-angle` or `landmarks/disc-fovea-distance`, which need a fovea it is
  not given, and no `vessels` structure, since it measures each class separately.

**An exact name is a claim, not a check.** That its answers carry canonical names is the
implementation's own statement about what it computes, and its owner is also this atlas's owner
(`PLAN-BIOMARKER.md` §5.6): nothing about it is independently verified. *Since 2026-11-22* it is
not part of the synthetic benchmark either, so no measurement in this atlas tests the claim.

**Its mapping, and its units.** The adapter answers each name as itself and converts the library's
microns back to pixels, as every adapter here reports pixels; `canonical.from_pixels` turns them
into the units of section 2. Its one categorical answer, the centring, is passed through untouched.

## 4. What each project computes that has no canonical name

A quantity here is **measured and stored under the project's own name**, and appears in no
comparison. That is a gap in the catalogue rather than a reason to discard a measurement: each one
is either a biomarker nobody else computes, or a mapping nobody has made yet.

**The nearest canonical name is our best match, not a mapping.** It says which comparison a reader
is most likely to want and what stands between the column and that name. Where the gap is a
conversion, §6 says how to make it; where it is a definition, no conversion closes it.

### 4.1 AutoMorph, AutoMorphalyzer, AutoMorphClass

| Their name | Nearest canonical name | What stands between them |
| --- | --- | --- |
| `squared_curvature_tortuosity` — AutoMorph `Artery_Squared_curvature_tortuosity`, AutoMorphClass `Artery_squared_curvature_tortuosity` | `tortuosity/hart-tau2` | It integrates the **signed** discrete curvature over the sample index, `abs(np.trapz(curvatures, x_values))`, where τ2 integrates its magnitude over arc length. It squares nothing, which is why the τ3 mapping was withdrawn (§5). No constant relates it to either |
| `average_local_calibre_artery_{whole,B,C}` (AutoMorphalyzer) | `calibre/width/artery/length-weighted` | Also a mean over every width sample along every vessel, so length-weighted, but it **leaves out branch points**. It differs from `average_global_calibre` by a third of a vessel's width at some angles; the vocabulary does not separate junction handling, so the two cannot share a name |
| `CRAE_Knudtson_artery_whole`, `CRVE_Knudtson_vein_whole` (AutoMorphalyzer) | `calibre/CRE-knudtson/{artery,vein}/B` | An equivalent over the whole image, a region the literature does not define. Its B and C forms are mapped |
| AutoMorph `…_zone_b` and `…_zone_c` forms of `Vessel_density` and `Fractal_dimension`; AutoMorphClass `ZoneB_…` forms of the same | `density/over-image`, `density/box-counting` | The zone's vessels over **the whole frame**: neither the zone's own area nor the field of view. A box count over a ring is not one the vocabulary names |
| AutoMorphClass `ZoneC_…`, every feature | the same feature over `C` | Its zone C is **3–5 disc radii**, a ring outside zone B. The catalogue's `C` is 2–5 radii and contains B, so the two cover different retina |
| AutoMorph `Disc_height`, `Disc_width`, `Cup_height`, `Cup_width`; AutoMorphalyzer and AutoMorphClass the same in lower case | — | The bounding-box sizes the cup-to-disc ratios are built from, in pixels. No canonical name holds a disc diameter |

### 4.2 PVBM

| Their name | Nearest canonical name | What stands between them |
| --- | --- | --- |
| `tortuosity_index` | `tortuosity/hart-tau1/{artery,vein}/length-weighted` | *Our finding, 2026-11-20, from reading `GeometryAnalysis.py`:* total arc over total chord for the whole map, the same ratio of sums as OCULAR's `pooled_tortuosity`. That equals each segment's ratio weighted by its **chord** length, where the `length-weighted` statistic weights by arc length. The vocabulary has no statistic for a ratio of sums |
| `start_points` | `topology/endpoints` | Where the rooted walk begins: one per vessel leaving the optic disc, a count of trunks. `endpoints + start_points` is the catalogued free-end count |
| `singularity_length` | `density/multifractal-d0`, `-d1`, `-d2` | The width of the singularity spectrum from the same multifractal analysis. Nothing else here computes it |
| `median_branching_angle` | `topology/branching-angle/median` | Listed above as ⚠️; every pairwise angle at a junction, the trunk included |
| `endpoints` | `topology/endpoints` | Listed above as ⚠️; the rooted tip count rather than every free end |

### 4.3 VascX

`{C}` is `crcl_multiplier_1p16666666667`: **7/6 disc diameters written as a float**, a circle at 2.33
disc radii, which the ARIC convention does not name. See [regions of
interest](biomarkers/regions-of-interest.md).

| Their name | Nearest canonical name | What stands between them |
| --- | --- | --- |
| `lw_tort_dist_max_segment_len_{0p15,0p25}_{C}_full_{arteries,veins}` | `tortuosity/hart-tau1/{artery,vein}/length-weighted` | The same measure at the two other segment caps. The cap is the segment definition itself, so one canonical name holds one cap, and 0.2 is the one mapped |
| `lw_tort_curv_{C}_full_{arteries,veins}` | `tortuosity/spline-curvature/{artery,vein}/length-weighted` | Multiplied by the disc-to-fovea distance. **Convertible** on a real photograph: divide by `disc_fovea_distance_retina`, then scale as a 1/length (§6). Not on the synthetic shapes, whose fovea is a convention |
| `mean_sparsity_vessels`, `mean_sparsity_{C}_full_vessels` | `density/sparsity/vessels/mean` | Divided by the disc-to-fovea distance. **Convertible** the same way: multiply by `disc_fovea_distance_retina`, then scale as a length. The second is over VascX's circle, which no region names |
| `vd_{C}_full_{arteries,veins}` | `density/over-fov` | Vessel area over the area of VascX's disc-centred circle, neither the field of view nor the frame |
| `median_temporal_angle_{arteries,veins}` | `topology/temporal-angle/{artery,vein}/median` | Listed above as ✅ on a real photograph; unmapped in the adapter because the synthetic shapes have no fovea |
| `disc_fovea_distance_retina`, `disc_fovea_distance_center_retina` | `landmarks/disc-fovea-distance` | Listed above as ⚠️; two reference points, and pixels unless VascX is given a scale |

### 4.4 OCULAR

| Their name | Nearest canonical name | What stands between them |
| --- | --- | --- |
| `pooled_tortuosity` | `tortuosity/hart-tau1/{artery,vein}/length-weighted` | Total arc over total chord for the whole map: a ratio of sums, where the length-weighted statistic is a weighted mean of each vessel's ratio. The vocabulary has no statistic for a ratio of sums |
| `start_points`, `endpoints` | `topology/endpoints` | As PVBM's, whose code OCULAR forks |
| `median_branching_angle` | `topology/branching-angle/median` | As PVBM's |

## 5. Where a mapping has been withdrawn

Five, each found by a measurement disagreeing with something, never by rereading a name, and one
moved to the name it always meant:

| Column | Was mapped to | Withdrawn because |
| --- | --- | --- |
| `squared_curvature_tortuosity` | `tortuosity/hart-tau3` | off by five orders of magnitude; it squares nothing |
| `median_branching_angle` | the angle between daughters | it medians every pairwise angle at every junction, trunk included, and reads ~120° where the daughters are 60° apart |
| `endpoints` (PVBM, OCULAR) | `topology/endpoints` | their rooted walk excludes the end at the disc |
| `mean_sparsity` (VascX) | `density/sparsity` | **normalised by the optic-disc-to-fovea distance**, so a dimensionless ratio rather than a distance in microns |
| `lw_tort_curv` (VascX) | `tortuosity/spline-curvature` | **multiplied by the optic-disc-to-fovea distance**, so dimensionless rather than the 1/µm the name means |
| `length` (PVBM, OCULAR) | `density/skeleton-length` | **moved, 2026-10-23, to `density/skeleton-length-rooted`**: their walk starts at the disc, so a vessel that never reaches it reads 0. On every synthetic shape it agrees with the rooted ground truth to within 6%, and on `disjoint` it reads 0 where the plain length is the whole network |

**Two of the five are the same defect in one project.** VascX normalises against its disc-to-fovea
axis in more than one feature, and a canonical name that declares a physical unit cannot hold a
quantity measured in disc-to-fovea distances. The lesson is cheap to state and was expensive to
learn twice: **where an upstream has an internal length it normalises by, check every mapping to a
unit-bearing name, not the one that misbehaved.**

**A withdrawn mapping is a finding, not an omission.** Each is recorded with its date on the
relevant family page, and the column is still measured and stored under the implementation's own
name — see §4.

## 6. Converting a project's number into canonical units

**Multiply a pixel value by the microns per pixel of the grid the project actually measured on,
raised to the powers of length its canonical unit carries.** That is `canonical.from_pixels`, and
every adapter here reports pixels so that this is the one place a unit changes. The trap is the
grid: a project that resized the picture measured in its own pixels, not the photograph's.

```
value_in_canonical_units = value_in_pixels × s ** p
s = um_per_px × crop_side / N
```

`um_per_px` and `crop_side` are the manifest's own columns for that photograph (`fetch-dataset`
skill §8), and `N` is the side of the square grid the project measured on. The power `p` comes from
the unit in §2:

| Canonical unit | p | Examples |
| --- | :-: | --- |
| µm | 1 | `calibre/width`, `calibre/CRE-*`, `density/skeleton-length-rooted`, `landmarks/disc-fovea-distance` |
| µm² | 2 | `density/area` |
| 1/µm | −1 | `tortuosity/grisan-density`, `tortuosity/spline-curvature` |
| 1, degrees, a count | 0 | `tortuosity/hart-tau1`, `density/box-counting`, `density/over-image`, `topology/*`, the AVRs and CDRs |

**What each project measures on, and what it hands back:**

| Project | Grid N | What it returns | What to do |
| --- | --- | --- | --- |
| AutoMorph | **912, always.** retipy resizes every file it opens to 912×912, bicubically, whatever it was given | Widths and equivalents are multiplied by a per-image `Scale_resolution` read from `M0/crop_info.csv`, which its preprocessing stage derives from `resolution_information.csv`; everything else is in 912-pixels. The adapter writes a scale of 1, so its widths are pixels too | Use N = 912 even for a 2048 mask. Do not rescale widths from AutoMorph's own CSV — but trust them as microns only when a real resolution went into `resolution_information.csv`: `generate_resolution.py` writes the same default, 0.008, for every image |
| AutoMorphalyzer | The mask it is handed. Its own pipeline resizes to 912 first | Pixels throughout; its authors state it assumes no physical resolution | N = the mask's side, 912 inside its pipeline |
| AutoMorphClass | The mask it is handed. Its own pipeline resizes to 920 | Pixels throughout | N = the mask's side, 920 inside its pipeline |
| PVBM | The mask it is handed | Pixels; `area` in px² | N = the mask's side. Its Hubbard equivalents cannot be converted: the constants were applied to pixels |
| VascX | The mask it is handed. Its shipped pipeline works at 1024 | Widths, equivalents and the disc-to-fovea distance in **mm** when given `mm_per_pixel`, pixels without. Tortuosity is dimensionless | Given a scale, mm × 1000 = µm and no grid factor. The adapter divides back to pixels with the same scale, so its stored values take N = the mask's side |
| OCULAR | The mask it is handed | Pixels; `area` in px² | N = the mask's side |

**A worked example.** [HRF](datasets/hrf.md) photograph `01_dr` has `um_per_px` 4.7398 and
`crop_side` 3271. On AutoMorph's 912 grid, s = 4.7398 × 3271 / 912 = 17.0 µm per pixel, so an
AutoMorph width of 7 px is 119 µm.

**Two of VascX's dimensionless columns convert through its own disc-to-fovea distance**, measured
on the same retina in the same units:

```
spline curvature (1/length) = lw_tort_curv / disc_fovea_distance_retina
sparsity (length)           = mean_sparsity × disc_fovea_distance_retina
```

then scale the result with p = −1 and p = 1. This is a conversion on a real photograph only. On a
synthetic shape the fovea is a convention of the fixture, which is why neither is mapped (§5).

**Where scaling is not enough:**

- **Knudtson's equivalents scale linearly**, because their constants (0.88 and 0.95) are
  dimensionless: a pixel CRAE times s is the micron CRAE. **Hubbard's do not** — the formula
  carries additive constants fitted in microns (−10.76 for arterioles, +450.05 for venules), so a
  Hubbard equivalent computed on pixel widths cannot be rescaled afterwards.
- **A dimensionless number can still depend on resolution.** Box-counting dimension and the
  densities change with the grid they were counted on; no factor undoes that, so compare them only
  between runs on one grid.
- **AutoMorph's resize blurs a binary mask.** Bicubic interpolation gives a mask grey edges and
  thin vessels lose contrast, so its widths are biased by the resize as well as being in another
  unit.
- **No scale, no microns.** Where a dataset's `resolution_source` is `unknown`, report pixels and
  say so; never borrow another camera's figure.

---

**Last checked:** 2026-11-19.
