# fundus-biomarkers

Pheno's reference implementation of this catalogue's canonical biomarkers. A user gives it an
artery mask, a vein mask, the field of view, the optic disc and the image scale; it gives back every
biomarker it implements under the catalogue's own names, in microns or dimensionless, with artery
and vein measured separately. It carries no segmentation model. It exists to turn the definitions
in [PLAN-BIOMARKER.md](../../PLAN-BIOMARKER.md) into something executable, against which other
implementations' answers can be measured (`PLAN-BIOMARKER.md` §5.1).

**It is proprietary, and its owner is also this atlas's owner.** Every number it produced is
published here like any other project's, and none of them is independently verified: the
implementation and the verification share an owner (`PLAN-BIOMARKER.md` §5.6). A reader without
access to the private repository can check every published number and comparison, but cannot
re-derive the measurements from the masks.

## 1. Code reference

- **Repository:** `git@github.com:PhenoAI/fundus-biomarkers.git` — **private**; access on request.
- **Version described here:** the commit pinned in `src/upstreams/fundus_biomarkers.py`.
- **Most recent commit:** 2026-10
- **Language and how it runs:** Python library; `measure(retina)` returns one dictionary.
- **Training code included:** Not applicable — no model is trained or shipped.

## 2. License

- **Code:** Proprietary (Pheno). Not redistributable; cloned, never installed, by the benchmark.
- **Model weights:** Not applicable.

## 3. Major publications by the authors

None yet.

## 4. Segmentation models used

Not applicable — masks in, numbers out (`PLAN-BIOMARKER.md` §5.7).

## 5. Models introduced here

Not applicable — no models.

## 6. Biomarkers computed

*The authors' claim, which the synthetic benchmark tests:* every entry below implements the
catalogue's definition, on the structures `artery` and `vein` (`both` for the ratios). It reports
no `vessels` structure.

| Biomarker | Defined in | Regions | This project's version |
| --- | --- | --- | --- |
| `calibre/width` | [calibre](../biomarkers/calibre.md) | `fov`, `B`, C | Reimplemented, perpendicular width |
| `calibre/CRE-knudtson`, `calibre/AVR-knudtson` | [Knudtson 2003](../papers/knudtson-2003.md) | `B`, C | Reimplemented, six widest, widest paired with narrowest |
| `calibre/CRE-hubbard`, `calibre/AVR-hubbard` | [Hubbard 1999](../papers/hubbard-1999.md) | `B`, C | Reimplemented, constants applied to widths in microns |
| `calibre/AVR-ratio` | [calibre](../biomarkers/calibre.md) | `fov`, `B`, C | Reimplemented |
| `tortuosity/hart-tau1` … `hart-tau7` and their `vessel-` forms | [Hart 1999](../papers/hart-1999.md) | `fov`, `B`, C | Reimplemented; curvature by angle regression, its scale in microns |
| `tortuosity/grisan-density`, `inflection-count`, `arc-chord-times-inflections`, `spline-curvature` | [tortuosity](../biomarkers/tortuosity.md) | `fov`, `B`, C | Reimplemented |
| `density/*` (area, skeleton length, coverage, sparsity, box-counting, multifractal d0–d2) | [density](../biomarkers/density.md) | `fov`, `B`, C | Reimplemented; box sizes in microns |
| `topology/junctions`, `endpoints`, `components`, `branching-angle` | [topology](../biomarkers/topology.md) | `fov`, `B`, C | Reimplemented; branching angle between the two daughters |

**Zone C** (2–5 disc radii from the disc centre) is reported wherever zone B is. The catalogue
reserves `C` without defining it (`regions-of-interest.md`), so the adapter stores those columns
under the library's own spelling and they claim nothing until the region page defines it.

Not implemented: `topology/temporal-angle` and the `landmarks` family, which need a fovea or an
optic cup the library is not given.

## 7. Examples and notebooks

Private — the repository carries one notebook per development stage under `notebooks/wip/`.

## 8. Known defects

None recorded as of 2026-10-05.

## 9. Notes

- **How it traces is not documented here**, by design: `PLAN-BIOMARKER.md` §5.4 keeps every
  algorithm and constant of a proprietary implementation out of this repository, and its commit id
  is the fingerprint that covers them (§5.5). That is the one respect in which this page cannot
  meet §4.1's requirement that an implementation document its tracing.
- **The scale is required.** The library refuses to guess one; with no microns-per-pixel figure
  every value is empty.

---

**Links and license last checked:** 2026-10-05
