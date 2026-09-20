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

**Status** says how far that has got:

| Status | Meaning |
| --- | --- |
| **claimed** | mapped from reading the code or the paper; not yet measured against a shape |
| **confirmed** | a synthetic shape returned the value this variant requires |
| **contradicted** | a synthetic shape returned a value this variant does not permit; see the note |
| **—** | this project does not compute anything under this canonical name |

A column is added per implementation as its adapter is written. PVBM is the first.

| Canonical name | Unit | [PVBM](projects/pvbm.md) | Status |
| --- | --- | --- | --- |
| `vessel-area-and-length/area/artery` | px² | `area` (arteriole run) | claimed |
| `vessel-area-and-length/area/vein` | px² | `area` (venule run) | claimed |
| `vessel-area-and-length/skeleton-length/artery` | px | `length` (arteriole run) | claimed |
| `vessel-area-and-length/skeleton-length/vein` | px | `length` (venule run) | claimed |
| `tortuosity/hart-tau1/artery` | — | `tortuosity index`, `median tortuosity` | claimed |
| `tortuosity/hart-tau1/vein` | — | the same two, venule run | claimed |
| `tortuosity/hart-tau2/…` | px⁻¹ | — | — |
| `tortuosity/hart-tau3/…` | px⁻² | — | — |
| `tortuosity/hart-tau4/…` | px⁻¹ | — | — |
| `tortuosity/hart-tau5/…` | px⁻² | — | — |
| `tortuosity/hart-tau6/…`, `hart-tau7/…` | px⁻¹, px⁻² | — | — |
| `tortuosity/grisan-density/…` | px⁻¹ | — | — |
| `junction-counts/junctions/artery` | count | `number of intersection points` | claimed |
| `junction-counts/endpoints/artery` | count | `number of end points` | claimed |
| `junction-counts/components/artery` | count | `number of start points` — **suspected different**: a start point is where the skeleton begins a walk, which need not be one per component | claimed |
| `junction-counts/*/vein` | count | the same three, venule run | claimed |
| `bifurcation-angle/between-daughters/artery` | degrees | `median branching angle` | claimed |
| `bifurcation-angle/between-daughters/vein` | degrees | the same, venule run | claimed |
| `fractal-dimension/multifractal-d0/artery` | — | `capacity dimension` | claimed |
| `fractal-dimension/multifractal-d1/artery` | — | `entropy dimension` | claimed |
| `fractal-dimension/multifractal-d2/artery` | — | `correlation dimension` | claimed |
| `fractal-dimension/box-counting/…` | — | — — PVBM's three are multifractal, which is not the same measurement | — |
| `central-retinal-equivalents/knudtson/artery` | px | `crae_knudtson` | claimed |
| `central-retinal-equivalents/knudtson/vein` | px | `crve_knudtson` | claimed |
| `central-retinal-equivalents/hubbard/artery` | **µm** | `crae_hubbard` — its constants were fitted in microns, so a pixel-fed value is a different number, not a rescaled one | claimed |
| `central-retinal-equivalents/hubbard/vein` | **µm** | `crve_hubbard` | claimed |
| `avr/knudtson/both` | — | not reported; the user divides CRAE by CRVE | claimed |
| `avr/hubbard/both` | — | likewise | claimed |
| `avr/ratio-of-calibres/both` | — | — | — |
| `vessel-calibre/mean-width/…` | px | — — PVBM measures calibre only through the equivalents | — |
| `vascular-density/…` | — | — | — |
| `sparsity/…` | px | — | — |

**PVBM's own singularity length** has no canonical name yet: it is part of the multifractal spectrum
rather than a dimension, and nothing else in the catalogue computes it. It will get one when a
second implementation does, since a name exists to make two numbers comparable.

## 3. What a missing row means

An em-dash in a project's column means that project does not compute that quantity — **not** that
it computes it badly. A canonical name with no project against it at all is a measurement this
catalogue can define and nobody here implements: Hart's τ4 and τ5, the compositional pair he
himself recommends, are the clearest case.
