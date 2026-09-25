# Biomarker names, and what each project calls them

**A biomarker name is not a definition.** "Tortuosity" names at least three incompatible formulas,
"CRAE" two, and papers usually report the name and omit the choice. Two numbers under the same
heading are comparable only when the definition, the region they were measured over, and the
structure they were measured on all match.

So this repository fixes a **canonical name** for each measurement it can compare, and maps every
project's own column onto one. The canonical names live in `src/biomarkers/canonical.py`, where a
typo is an error rather than a row that silently matches nothing.

**Each project's mapping lives in its own adapter** — `src/biomarkers/<slug>.py`, beside the calls
it describes — and the adapter answers under the canonical names, so the evidence a benchmark
writes is already comparable between implementations without a translation step. The table below is
that mapping, for a reader.

## 1. How a canonical name is built

```
biomarker / variant / structure
```

| Part | Meaning |
| --- | --- |
| **biomarker** | a page in [biomarkers/](biomarkers/) — the measurement family |
| **variant** | *which definition*, from that page's numbered variants, because the family name does not say |
| **structure** | what it was measured over: `artery`, `vein`, `vessels` for the two together, or `both` for a measurement that is inherently a ratio of the two |

`central-retinal-equivalents/knudtson/artery` is CRAE; the same name ending `/vein` is CRVE. They
are one definition applied to two structures rather than two biomarkers, which is why the catalogue
holds one page for both.

## 2. What each project calls them

**This table is a claim, not a record.** A mapping says *we believe this column computes this
quantity*, usually from reading the implementation's source rather than its documentation. The
[synthetic benchmark](benchmarks/biomarker-synthetic-docs.md) is what tests the belief: a shape
where two variants give different known values separates them by measurement, and a column that
matches no variant's value is a finding rather than a mislabelled row.

Each mapping carries how far that has got:

| | Meaning |
| --- | --- |
| 🟢 | **confirmed** — a synthetic shape returned the value this variant requires |
| 🟡 | **claimed** — mapped from reading the code or the paper; not yet measured against a shape |
| 🔴 | **contradicted** — a shape returned a value this variant does not permit; the note says what |
| — | this project computes nothing under this canonical name |

Names are written with `<structure>` where the same definition applies to arteries, veins and the
two together; a project that runs separately on each reports one column per structure. A column is
added per implementation as its adapter is written, and PVBM is the first.

**A dash is not the whole story.** A project may compute something this catalogue has no name for
at all, and those columns are measured and stored under the project's own name rather than dropped
— section 3 lists them, because they are what the catalogue is missing.

| Canonical name | Unit | [PVBM](projects/pvbm.md) |
| --- | --- | --- |
| [`vessel-area-and-length/area/<structure>`](biomarkers/vessel-area-and-length.md) | px² | `area` 🟢 — within 0.1% on four shapes at four angles |
| [`vessel-area-and-length/skeleton-length/<structure>`](biomarkers/vessel-area-and-length.md) | px | `length` 🔴 — it is a sum of **chords**, so it under-reports a curved vessel: −10.6% on a 90° arc, −18% on a sinusoid |
| [`tortuosity/hart-tau1/<structure>`](biomarkers/tortuosity.md) | — | `median tortuosity` 🟡 — the right quantity, measured with a naive chain code: a straight vessel reads 1.073 at 30° where it must read 1 |
| [`tortuosity/hart-tau2/<structure>`](biomarkers/tortuosity.md) | px⁻¹ | — |
| [`tortuosity/hart-tau3/<structure>`](biomarkers/tortuosity.md) | px⁻² | — |
| [`tortuosity/hart-tau4/<structure>`](biomarkers/tortuosity.md) | px⁻¹ | — |
| [`tortuosity/hart-tau5/<structure>`](biomarkers/tortuosity.md) | px⁻² | — |
| [`tortuosity/hart-tau6/<structure>`](biomarkers/tortuosity.md) | px⁻¹ | — |
| [`tortuosity/hart-tau7/<structure>`](biomarkers/tortuosity.md) | px⁻² | — |
| [`tortuosity/grisan-density/<structure>`](biomarkers/tortuosity.md) | px⁻¹ | — |
| [`tortuosity/arc-chord-times-inflections/<structure>`](biomarkers/tortuosity.md) | — | — |
| [`tortuosity/spline-mean-curvature/<structure>`](biomarkers/tortuosity.md) | px⁻¹ | — |
| [`tortuosity/inflection-count/<structure>`](biomarkers/tortuosity.md) | count | — |
| [`junction-counts/junctions/<structure>`](biomarkers/junction-counts.md) | count | `number of intersection points` 🔴 — exact where there are none; a single Y-junction counts as one, three or four depending on the angle |
| [`junction-counts/endpoints/<structure>`](biomarkers/junction-counts.md) | count | `number of end points` 🟢 — exact at every angle on all three shapes that pin one |
| [`junction-counts/components/<structure>`](biomarkers/junction-counts.md) | count | `number of start points` 🟡 — **suspected different**: a start point is where a skeleton walk begins, which need not be one per component |
| [`bifurcation-angle/between-daughters/<structure>`](biomarkers/bifurcation-angle.md) | degrees | — 🔴 — **the mapping was wrong, not the column.** `median branching angle` was mapped here until a shape showed it medians every pairwise angle at every particular point, including each daughter against the trunk, and reads ~120° where the daughters are 60° apart. It now maps to nothing and is measured under its own name (section 3) |
| [`fractal-dimension/multifractal-d0/<structure>`](biomarkers/fractal-dimension.md) | — | `capacity dimension` 🟡 — computed and recorded on every shape, but no shape pins a value to check it against |
| [`fractal-dimension/multifractal-d1/<structure>`](biomarkers/fractal-dimension.md) | — | `entropy dimension` 🟡 |
| [`fractal-dimension/multifractal-d2/<structure>`](biomarkers/fractal-dimension.md) | — | `correlation dimension` 🟡 |
| [`fractal-dimension/box-counting/<structure>`](biomarkers/fractal-dimension.md) | — | — PVBM's three are multifractal, which is a different measurement |
| [`central-retinal-equivalents/knudtson/<structure>`](biomarkers/central-retinal-equivalents.md) | px | `crae_knudtson`, `crve_knudtson` 🟢 — **measured**: within 3.1% (CRAE) and 3.8% (CRVE) of the recursion on twelve vessels of known width, always low by about a mask's worth of width. Two limits are the implementation's, not the mapping's: it keeps only vessels *starting* within 20 + 2·radius of the disc centre — a cutoff one vessel here missed by 1.1 px — and it raises `RecursionError` on a skeleton longer than ~1000 px |
| [`central-retinal-equivalents/hubbard/<structure>`](biomarkers/central-retinal-equivalents.md) | **µm** | `crae_hubbard`, `crve_hubbard` 🔴 — **measured**: −80% (CRAE) and −76% (CRVE). PVBM computes it from **pixel** widths and takes no scale at all, while Hubbard's constants were fitted in microns; at one 5 µm/px scale the arteries are out by 5.09× and the veins by 4.13×, so no single conversion recovers it — it is a different quantity rather than one awaiting conversion |
| [`avr/knudtson/both`](biomarkers/avr.md) | — | not reported; the user divides CRAE by CRVE 🟢 — **measured** at +0.8%, better than either calibre it is built from, the two deficits being in the same direction |
| [`avr/hubbard/both`](biomarkers/avr.md) | — | likewise 🔴 — **measured** at −18.8%, inheriting the dimensional error above |
| [`avr/ratio-of-calibres/both`](biomarkers/avr.md) | — | — |
| [`vessel-calibre/mean-width/<structure>`](biomarkers/vessel-calibre.md) | px | — PVBM reaches calibre only through the equivalents |
| [`vessel-calibre/median-width/<structure>`](biomarkers/vessel-calibre.md) | px | — |
| [`vascular-density/over-field-of-view/<structure>`](biomarkers/vascular-density.md) | — | — |
| [`vascular-density/over-image/<structure>`](biomarkers/vascular-density.md) | — | — |
| [`sparsity/mean-distance/<structure>`](biomarkers/sparsity.md) | px | — |
| [`sparsity/max-distance/<structure>`](biomarkers/sparsity.md) | px | — |

## 3. What each project computes that this catalogue cannot name

These columns are **measured and stored**, under the project's own name, and no row above claims
them. A quantity the catalogue has no name for is a gap in the catalogue rather than a thing to
throw away — and keeping it is what makes the gap visible.

| PVBM's column | What it is, and why it has no canonical name |
| --- | --- |
| `perimeter_<structure>` | the boundary length of the vessel mask. Nothing else catalogued computes it, and a name exists to make two numbers comparable, so it waits for a second implementation to need one |
| `singularity_length_<structure>` | part of the multifractal spectrum rather than a dimension of it — the width of the f(α) curve. Same reason |
| `median_branching_angle_<structure>` | the median of **every** pairwise angle at every particular point, the trunk against each daughter included. It is a real quantity, measured consistently; it is simply not the bifurcation angle it was once mapped to, and the catalogue has no page for what it actually is |
| `mean_branching_angle_<structure>` | the same collection of angles, averaged |
| `std_branching_angle_<structure>` | and their spread. PVBM returns it from the same call and its own docstring does not mention it |

## 4. What a missing row means

An em-dash in a project's column means that project does not compute that quantity — **not** that
it computes it badly. A canonical name with no project against it at all is a measurement this
catalogue can define and nobody here implements: Hart's τ4 and τ5, the compositional pair he
himself recommends, are the clearest case.
