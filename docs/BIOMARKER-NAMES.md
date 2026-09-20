# Biomarker names, and what each project calls them

**A biomarker name is not a definition.** "Tortuosity" names at least three incompatible formulas,
"CRAE" two, and papers usually report the name and omit the choice. Two numbers under the same
heading are comparable only when the definition, the region they were measured over, and the
structure they were measured on all match.

So this repository fixes a **canonical name** for each measurement it can compare, and maps every
project's own column onto one. The canonical names live in `src/biomarkers/canonical.py`, where a
typo is an error rather than a row that silently matches nothing; the mapping is the table below.

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

| Canonical name | Unit | [PVBM](projects/pvbm.md) |
| --- | --- | --- |
| [`vessel-area-and-length/area/<structure>`](biomarkers/vessel-area-and-length.md) | px² | `area` 🟡 |
| [`vessel-area-and-length/skeleton-length/<structure>`](biomarkers/vessel-area-and-length.md) | px | `length` 🟡 |
| [`tortuosity/hart-tau1/<structure>`](biomarkers/tortuosity.md) | — | `tortuosity index`, `median tortuosity` 🟡 |
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
| [`junction-counts/junctions/<structure>`](biomarkers/junction-counts.md) | count | `number of intersection points` 🟡 |
| [`junction-counts/endpoints/<structure>`](biomarkers/junction-counts.md) | count | `number of end points` 🟡 |
| [`junction-counts/components/<structure>`](biomarkers/junction-counts.md) | count | `number of start points` 🟡 — **suspected different**: a start point is where a skeleton walk begins, which need not be one per component |
| [`bifurcation-angle/between-daughters/<structure>`](biomarkers/bifurcation-angle.md) | degrees | `median branching angle` 🟡 |
| [`fractal-dimension/multifractal-d0/<structure>`](biomarkers/fractal-dimension.md) | — | `capacity dimension` 🟡 |
| [`fractal-dimension/multifractal-d1/<structure>`](biomarkers/fractal-dimension.md) | — | `entropy dimension` 🟡 |
| [`fractal-dimension/multifractal-d2/<structure>`](biomarkers/fractal-dimension.md) | — | `correlation dimension` 🟡 |
| [`fractal-dimension/box-counting/<structure>`](biomarkers/fractal-dimension.md) | — | — PVBM's three are multifractal, which is a different measurement |
| [`central-retinal-equivalents/knudtson/<structure>`](biomarkers/central-retinal-equivalents.md) | px | `crae_knudtson`, `crve_knudtson` 🟡 |
| [`central-retinal-equivalents/hubbard/<structure>`](biomarkers/central-retinal-equivalents.md) | **µm** | `crae_hubbard`, `crve_hubbard` 🟡 — constants fitted in microns, so a pixel-fed value is a different number, not a rescaled one |
| [`avr/knudtson/both`](biomarkers/avr.md) | — | not reported; the user divides CRAE by CRVE 🟡 |
| [`avr/hubbard/both`](biomarkers/avr.md) | — | likewise 🟡 |
| [`avr/ratio-of-calibres/both`](biomarkers/avr.md) | — | — |
| [`vessel-calibre/mean-width/<structure>`](biomarkers/vessel-calibre.md) | px | — PVBM reaches calibre only through the equivalents |
| [`vessel-calibre/median-width/<structure>`](biomarkers/vessel-calibre.md) | px | — |
| [`vascular-density/over-field-of-view/<structure>`](biomarkers/vascular-density.md) | — | — |
| [`vascular-density/over-image/<structure>`](biomarkers/vascular-density.md) | — | — |
| [`sparsity/mean-distance/<structure>`](biomarkers/sparsity.md) | px | — |
| [`sparsity/max-distance/<structure>`](biomarkers/sparsity.md) | px | — |

**PVBM's own singularity length** has no canonical name yet: it is part of the multifractal spectrum
rather than a dimension, and nothing else in the catalogue computes it. It will get one when a
second implementation does, since a name exists to make two numbers comparable.

## 3. What a missing row means

An em-dash in a project's column means that project does not compute that quantity — **not** that
it computes it badly. A canonical name with no project against it at all is a measurement this
catalogue can define and nobody here implements: Hart's τ4 and τ5, the compositional pair he
himself recommends, are the clearest case.
