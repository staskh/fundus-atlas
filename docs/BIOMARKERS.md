# Biomarkers

Measurements computed from the segmentations of a colour-fundus photograph — the numbers that end up
in a spreadsheet column. **Five families**, each a page describing what it measures, which competing
definitions share its name, what it needs as input, and which pipelines compute it.

**A biomarker name is not a definition.** "Tortuosity" names eleven formulas here and "CRAE" two,
and papers usually report the name and omit the choice. So every measurement carries a **canonical
name** of the form `family / biomarker / structure / [roi] / [statistic]`, fixed in
`src/biomarkers/canonical.py` and mapped to each project's own column in
[BIOMARKER-NAMES.md](BIOMARKER-NAMES.md) — which is where to look before reading two projects'
numbers against each other.

**Every length is in microns, never pixels**, and every family page says what its units are and
whether the number survives a change of camera.

## 1. The five families

<!-- generated: families -->
| Family | What it measures | Biomarkers | Structures | Units |
| --- | --- | --- | --- | --- |
| [calibre](biomarkers/calibre.md) | how wide the vessels are, and everything built from widths | 6 | `artery`, `vein`, `vessels` | 1, µm |
| [tortuosity](biomarkers/tortuosity.md) | the shape of a vessel's path | 11 | `artery`, `vein`, `vessels` | 1, 1/µm, 1/µm² |
| [density](biomarkers/density.md) | how much vasculature there is, and how it is spread | 9 | `artery`, `vein`, `vessels` | 1, µm, µm² |
| [topology](biomarkers/topology.md) | where the network branches and how it connects | 5 | `artery`, `vein`, `vessels` | 1, degrees |
| [landmarks](biomarkers/landmarks.md) | the optic nerve head and the fovea | 3 | — | 1, µm |

**828 canonical names** in all, once each biomarker is expanded over the structures it applies to, the regions it admits and the statistics it can be pooled by.
<!-- /generated -->

Each family page says which competing definitions share its name, what the formula is, what it
needs as input, and which pipelines compute it. The **papers of record** are on those pages, beside
the definition each one fixes.

**Two pages here are not biomarkers**, and are catalogued because several biomarkers cannot be read
without them:

| Page | Why it is here |
| --- | --- |
| [vessel tracing](biomarkers/vessel-tracing.md) | every biomarker beyond area and density is computed from a centreline, and this is the step where the pipelines differ most |
| [regions of interest](biomarkers/regions-of-interest.md) | the `roi` part of every canonical name points here for what a zone denotes |

## 2. What to read before comparing two numbers

- **The variant.** Two values under one family name are comparable only if they are the same
  biomarker. Hubbard's and Knudtson's equivalents are not convertible; Hart's seven span three
  physical dimensions.
- **The region.** The same formula over a different annulus is a different number, and the classical
  convention is stated in disc *diameters* where much code uses disc *radii* — a factor-of-two trap.
- **The statistic.** A mean and a median over the same segments are two numbers, and over
  *different* segments they are not comparable at all.
- **Whether it survives a change of camera.** Thirty of the seventy names this catalogue held before
  the microns rule gave a different answer for the same eye at a different resolution.
- **What the implementation actually computes.** Three mappings in this catalogue have been
  withdrawn after a synthetic shape showed a column computing something other than its name — they
  are listed in [BIOMARKER-NAMES.md](BIOMARKER-NAMES.md) §5.

## 3. How these are measured here

The [synthetic biomarker benchmark](benchmarks/biomarker-synthetic-docs.md) runs every catalogued
implementation over shapes drawn from equations, whose values follow from geometry rather than from
anybody's annotation. A straight vessel has a tortuosity of exactly 1, a circular arc a curvature of
exactly 1/r, and an implementation that disagrees is wrong rather than different.

[What came out](benchmarks/biomarker-synthetic-results.md) · [The analysis](../notebooks/biomarker-synthetic.ipynb)

---

**Last checked:** 2026-09-30.
