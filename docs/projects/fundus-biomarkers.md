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
- **Most recent commit:** 2026-11-03 (`348da1b`)
- **Language and how it runs:** Python library; a `Retina` record's `biomarkers` is one dictionary.
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

*The authors' claim, which no measurement in this atlas currently tests* — the synthetic benchmark
ran it until 2026-11-22 and no longer does: every entry below implements the catalogue's definition, on the structures `artery` and `vein` (`both` for the ratios). It reports
no `vessels` structure.

| Biomarker | Defined in | Regions | This project's version |
| --- | --- | --- | --- |
| `calibre/width` | [calibre](../biomarkers/calibre.md) | `fov`, `B`, `C` | Reimplemented, perpendicular width |
| `calibre/CRE-knudtson`, `calibre/AVR-knudtson` | [Knudtson 2003](../papers/knudtson-2003.md) | `B`, `C` | Reimplemented, six widest, widest paired with narrowest |
| `calibre/CRE-hubbard`, `calibre/AVR-hubbard` | [Hubbard 1999](../papers/hubbard-1999.md) | `B`, `C` | Reimplemented, constants applied to widths in microns |
| `calibre/AVR-ratio` | [calibre](../biomarkers/calibre.md) | `fov`, `B`, `C` | Reimplemented |
| `tortuosity/hart-tau1` … `hart-tau7` and their `vessel-` forms | [Hart 1999](../papers/hart-1999.md) | `fov`, `B`, `C` | Reimplemented; curvature by angle regression, its scale in microns |
| `tortuosity/grisan-density`, `inflection-count`, `arc-chord-times-inflections`, `spline-curvature` | [tortuosity](../biomarkers/tortuosity.md) | `fov`, `B`, `C` | Reimplemented |
| `density/*` (area, skeleton length and its rooted part, coverage, sparsity, box-counting, multifractal d0–d2) | [density](../biomarkers/density.md) | `fov`, `B`, `C` | Reimplemented; box sizes in microns |
| `topology/junctions`, `endpoints`, `components`, `branching-angle` | [topology](../biomarkers/topology.md) | `fov`, `B`, `C` | Reimplemented; branching angle between the two daughters |

**Zone C** — Cheung et al. 2010's Extended zone, 2–5 disc radii from the disc centre
([regions of interest](../biomarkers/regions-of-interest.md) §4) — is reported wherever zone B is.

`landmarks`: the three cup-to-disc ratios, vertical, horizontal and area, are computed only from
disc and cup **masks**, which the synthetic benchmark did not hand it while it ran it, so there
they were empty. The
library also answers the photograph's **centring** — `disc`, `macula` or `unknown` — from the disc
circle: [`landmarks/centring`](../biomarkers/landmarks.md), the vocabulary's one categorical name.

Every name it answers is catalogued.

Not implemented: `topology/temporal-angle` and `landmarks/disc-fovea-distance`, which need a fovea
the library is not given.

### 6.1 Every column it writes

*Added 2026-11-22.* Every number the implementation returns, under its own name, beside the
canonical name it answers to — or, where it answers to none, the nearest one and what keeps
it from being that name.

<!-- generated: columns -->
**633 columns**: 633 answer to a canonical name exactly, 0 are close to one and 0 to none. A close name is a pointer for a reader, never a mapping: nothing is compared against it. Rendered from the naming table in `src/biomarkers/fundus-biomarkers.py` by `python -m biomarkers.pages`.

<details><summary>All 633 columns</summary>

| Its column | Canonical name | Match | What differs |
| --- | --- | :-: | --- |
| `calibre/AVR-hubbard/both/B` | `calibre/AVR-hubbard/both/B` | exact |  |
| `calibre/AVR-hubbard/both/C` | `calibre/AVR-hubbard/both/C` | exact |  |
| `calibre/AVR-knudtson/both/B` | `calibre/AVR-knudtson/both/B` | exact |  |
| `calibre/AVR-knudtson/both/C` | `calibre/AVR-knudtson/both/C` | exact |  |
| `calibre/AVR-ratio/both` | `calibre/AVR-ratio/both` | exact |  |
| `calibre/AVR-ratio/both/B` | `calibre/AVR-ratio/both/B` | exact |  |
| `calibre/AVR-ratio/both/C` | `calibre/AVR-ratio/both/C` | exact |  |
| `calibre/CRE-hubbard/artery/B` | `calibre/CRE-hubbard/artery/B` | exact |  |
| `calibre/CRE-hubbard/artery/C` | `calibre/CRE-hubbard/artery/C` | exact |  |
| `calibre/CRE-hubbard/vein/B` | `calibre/CRE-hubbard/vein/B` | exact |  |
| `calibre/CRE-hubbard/vein/C` | `calibre/CRE-hubbard/vein/C` | exact |  |
| `calibre/CRE-knudtson/artery/B` | `calibre/CRE-knudtson/artery/B` | exact |  |
| `calibre/CRE-knudtson/artery/C` | `calibre/CRE-knudtson/artery/C` | exact |  |
| `calibre/CRE-knudtson/vein/B` | `calibre/CRE-knudtson/vein/B` | exact |  |
| `calibre/CRE-knudtson/vein/C` | `calibre/CRE-knudtson/vein/C` | exact |  |
| `calibre/width/artery/B/length-weighted` | `calibre/width/artery/B/length-weighted` | exact |  |
| `calibre/width/artery/B/mean` | `calibre/width/artery/B/mean` | exact |  |
| `calibre/width/artery/B/median` | `calibre/width/artery/B/median` | exact |  |
| `calibre/width/artery/B/std` | `calibre/width/artery/B/std` | exact |  |
| `calibre/width/artery/C/length-weighted` | `calibre/width/artery/C/length-weighted` | exact |  |
| `calibre/width/artery/C/mean` | `calibre/width/artery/C/mean` | exact |  |
| `calibre/width/artery/C/median` | `calibre/width/artery/C/median` | exact |  |
| `calibre/width/artery/C/std` | `calibre/width/artery/C/std` | exact |  |
| `calibre/width/artery/length-weighted` | `calibre/width/artery/length-weighted` | exact |  |
| `calibre/width/artery/mean` | `calibre/width/artery/mean` | exact |  |
| `calibre/width/artery/median` | `calibre/width/artery/median` | exact |  |
| `calibre/width/artery/std` | `calibre/width/artery/std` | exact |  |
| `calibre/width/vein/B/length-weighted` | `calibre/width/vein/B/length-weighted` | exact |  |
| `calibre/width/vein/B/mean` | `calibre/width/vein/B/mean` | exact |  |
| `calibre/width/vein/B/median` | `calibre/width/vein/B/median` | exact |  |
| `calibre/width/vein/B/std` | `calibre/width/vein/B/std` | exact |  |
| `calibre/width/vein/C/length-weighted` | `calibre/width/vein/C/length-weighted` | exact |  |
| `calibre/width/vein/C/mean` | `calibre/width/vein/C/mean` | exact |  |
| `calibre/width/vein/C/median` | `calibre/width/vein/C/median` | exact |  |
| `calibre/width/vein/C/std` | `calibre/width/vein/C/std` | exact |  |
| `calibre/width/vein/length-weighted` | `calibre/width/vein/length-weighted` | exact |  |
| `calibre/width/vein/mean` | `calibre/width/vein/mean` | exact |  |
| `calibre/width/vein/median` | `calibre/width/vein/median` | exact |  |
| `calibre/width/vein/std` | `calibre/width/vein/std` | exact |  |
| `density/area/artery` | `density/area/artery` | exact |  |
| `density/area/artery/B` | `density/area/artery/B` | exact |  |
| `density/area/artery/C` | `density/area/artery/C` | exact |  |
| `density/area/vein` | `density/area/vein` | exact |  |
| `density/area/vein/B` | `density/area/vein/B` | exact |  |
| `density/area/vein/C` | `density/area/vein/C` | exact |  |
| `density/box-counting/artery` | `density/box-counting/artery` | exact |  |
| `density/box-counting/artery/B` | `density/box-counting/artery/B` | exact |  |
| `density/box-counting/artery/C` | `density/box-counting/artery/C` | exact |  |
| `density/box-counting/vein` | `density/box-counting/vein` | exact |  |
| `density/box-counting/vein/B` | `density/box-counting/vein/B` | exact |  |
| `density/box-counting/vein/C` | `density/box-counting/vein/C` | exact |  |
| `density/multifractal-d0/artery` | `density/multifractal-d0/artery` | exact |  |
| `density/multifractal-d0/artery/B` | `density/multifractal-d0/artery/B` | exact |  |
| `density/multifractal-d0/artery/C` | `density/multifractal-d0/artery/C` | exact |  |
| `density/multifractal-d0/vein` | `density/multifractal-d0/vein` | exact |  |
| `density/multifractal-d0/vein/B` | `density/multifractal-d0/vein/B` | exact |  |
| `density/multifractal-d0/vein/C` | `density/multifractal-d0/vein/C` | exact |  |
| `density/multifractal-d1/artery` | `density/multifractal-d1/artery` | exact |  |
| `density/multifractal-d1/artery/B` | `density/multifractal-d1/artery/B` | exact |  |
| `density/multifractal-d1/artery/C` | `density/multifractal-d1/artery/C` | exact |  |
| `density/multifractal-d1/vein` | `density/multifractal-d1/vein` | exact |  |
| `density/multifractal-d1/vein/B` | `density/multifractal-d1/vein/B` | exact |  |
| `density/multifractal-d1/vein/C` | `density/multifractal-d1/vein/C` | exact |  |
| `density/multifractal-d2/artery` | `density/multifractal-d2/artery` | exact |  |
| `density/multifractal-d2/artery/B` | `density/multifractal-d2/artery/B` | exact |  |
| `density/multifractal-d2/artery/C` | `density/multifractal-d2/artery/C` | exact |  |
| `density/multifractal-d2/vein` | `density/multifractal-d2/vein` | exact |  |
| `density/multifractal-d2/vein/B` | `density/multifractal-d2/vein/B` | exact |  |
| `density/multifractal-d2/vein/C` | `density/multifractal-d2/vein/C` | exact |  |
| `density/over-fov/artery` | `density/over-fov/artery` | exact |  |
| `density/over-fov/artery/B` | `density/over-fov/artery/B` | exact |  |
| `density/over-fov/artery/C` | `density/over-fov/artery/C` | exact |  |
| `density/over-fov/vein` | `density/over-fov/vein` | exact |  |
| `density/over-fov/vein/B` | `density/over-fov/vein/B` | exact |  |
| `density/over-fov/vein/C` | `density/over-fov/vein/C` | exact |  |
| `density/over-image/artery` | `density/over-image/artery` | exact |  |
| `density/over-image/vein` | `density/over-image/vein` | exact |  |
| `density/skeleton-length-rooted/artery` | `density/skeleton-length-rooted/artery` | exact |  |
| `density/skeleton-length-rooted/artery/B` | `density/skeleton-length-rooted/artery/B` | exact |  |
| `density/skeleton-length-rooted/artery/C` | `density/skeleton-length-rooted/artery/C` | exact |  |
| `density/skeleton-length-rooted/vein` | `density/skeleton-length-rooted/vein` | exact |  |
| `density/skeleton-length-rooted/vein/B` | `density/skeleton-length-rooted/vein/B` | exact |  |
| `density/skeleton-length-rooted/vein/C` | `density/skeleton-length-rooted/vein/C` | exact |  |
| `density/skeleton-length/artery` | `density/skeleton-length/artery` | exact |  |
| `density/skeleton-length/artery/B` | `density/skeleton-length/artery/B` | exact |  |
| `density/skeleton-length/artery/C` | `density/skeleton-length/artery/C` | exact |  |
| `density/skeleton-length/vein` | `density/skeleton-length/vein` | exact |  |
| `density/skeleton-length/vein/B` | `density/skeleton-length/vein/B` | exact |  |
| `density/skeleton-length/vein/C` | `density/skeleton-length/vein/C` | exact |  |
| `density/sparsity/artery/B/max` | `density/sparsity/artery/B/max` | exact |  |
| `density/sparsity/artery/B/mean` | `density/sparsity/artery/B/mean` | exact |  |
| `density/sparsity/artery/C/max` | `density/sparsity/artery/C/max` | exact |  |
| `density/sparsity/artery/C/mean` | `density/sparsity/artery/C/mean` | exact |  |
| `density/sparsity/artery/max` | `density/sparsity/artery/max` | exact |  |
| `density/sparsity/artery/mean` | `density/sparsity/artery/mean` | exact |  |
| `density/sparsity/vein/B/max` | `density/sparsity/vein/B/max` | exact |  |
| `density/sparsity/vein/B/mean` | `density/sparsity/vein/B/mean` | exact |  |
| `density/sparsity/vein/C/max` | `density/sparsity/vein/C/max` | exact |  |
| `density/sparsity/vein/C/mean` | `density/sparsity/vein/C/mean` | exact |  |
| `density/sparsity/vein/max` | `density/sparsity/vein/max` | exact |  |
| `density/sparsity/vein/mean` | `density/sparsity/vein/mean` | exact |  |
| `landmarks/CDR-area` | `landmarks/CDR-area` | exact |  |
| `landmarks/CDR-horizontal` | `landmarks/CDR-horizontal` | exact |  |
| `landmarks/CDR-vertical` | `landmarks/CDR-vertical` | exact |  |
| `landmarks/centring` | `landmarks/centring` | exact |  |
| `topology/branching-angle/artery/B/mean` | `topology/branching-angle/artery/B/mean` | exact |  |
| `topology/branching-angle/artery/B/median` | `topology/branching-angle/artery/B/median` | exact |  |
| `topology/branching-angle/artery/B/std` | `topology/branching-angle/artery/B/std` | exact |  |
| `topology/branching-angle/artery/C/mean` | `topology/branching-angle/artery/C/mean` | exact |  |
| `topology/branching-angle/artery/C/median` | `topology/branching-angle/artery/C/median` | exact |  |
| `topology/branching-angle/artery/C/std` | `topology/branching-angle/artery/C/std` | exact |  |
| `topology/branching-angle/artery/mean` | `topology/branching-angle/artery/mean` | exact |  |
| `topology/branching-angle/artery/median` | `topology/branching-angle/artery/median` | exact |  |
| `topology/branching-angle/artery/std` | `topology/branching-angle/artery/std` | exact |  |
| `topology/branching-angle/vein/B/mean` | `topology/branching-angle/vein/B/mean` | exact |  |
| `topology/branching-angle/vein/B/median` | `topology/branching-angle/vein/B/median` | exact |  |
| `topology/branching-angle/vein/B/std` | `topology/branching-angle/vein/B/std` | exact |  |
| `topology/branching-angle/vein/C/mean` | `topology/branching-angle/vein/C/mean` | exact |  |
| `topology/branching-angle/vein/C/median` | `topology/branching-angle/vein/C/median` | exact |  |
| `topology/branching-angle/vein/C/std` | `topology/branching-angle/vein/C/std` | exact |  |
| `topology/branching-angle/vein/mean` | `topology/branching-angle/vein/mean` | exact |  |
| `topology/branching-angle/vein/median` | `topology/branching-angle/vein/median` | exact |  |
| `topology/branching-angle/vein/std` | `topology/branching-angle/vein/std` | exact |  |
| `topology/components/artery` | `topology/components/artery` | exact |  |
| `topology/components/artery/B` | `topology/components/artery/B` | exact |  |
| `topology/components/artery/C` | `topology/components/artery/C` | exact |  |
| `topology/components/vein` | `topology/components/vein` | exact |  |
| `topology/components/vein/B` | `topology/components/vein/B` | exact |  |
| `topology/components/vein/C` | `topology/components/vein/C` | exact |  |
| `topology/endpoints/artery` | `topology/endpoints/artery` | exact |  |
| `topology/endpoints/artery/B` | `topology/endpoints/artery/B` | exact |  |
| `topology/endpoints/artery/C` | `topology/endpoints/artery/C` | exact |  |
| `topology/endpoints/vein` | `topology/endpoints/vein` | exact |  |
| `topology/endpoints/vein/B` | `topology/endpoints/vein/B` | exact |  |
| `topology/endpoints/vein/C` | `topology/endpoints/vein/C` | exact |  |
| `topology/junctions/artery` | `topology/junctions/artery` | exact |  |
| `topology/junctions/artery/B` | `topology/junctions/artery/B` | exact |  |
| `topology/junctions/artery/C` | `topology/junctions/artery/C` | exact |  |
| `topology/junctions/vein` | `topology/junctions/vein` | exact |  |
| `topology/junctions/vein/B` | `topology/junctions/vein/B` | exact |  |
| `topology/junctions/vein/C` | `topology/junctions/vein/C` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/B/length-weighted` | `tortuosity/arc-chord-times-inflections/artery/B/length-weighted` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/B/mean` | `tortuosity/arc-chord-times-inflections/artery/B/mean` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/B/median` | `tortuosity/arc-chord-times-inflections/artery/B/median` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/B/std` | `tortuosity/arc-chord-times-inflections/artery/B/std` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/C/length-weighted` | `tortuosity/arc-chord-times-inflections/artery/C/length-weighted` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/C/mean` | `tortuosity/arc-chord-times-inflections/artery/C/mean` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/C/median` | `tortuosity/arc-chord-times-inflections/artery/C/median` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/C/std` | `tortuosity/arc-chord-times-inflections/artery/C/std` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/length-weighted` | `tortuosity/arc-chord-times-inflections/artery/length-weighted` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/mean` | `tortuosity/arc-chord-times-inflections/artery/mean` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/median` | `tortuosity/arc-chord-times-inflections/artery/median` | exact |  |
| `tortuosity/arc-chord-times-inflections/artery/std` | `tortuosity/arc-chord-times-inflections/artery/std` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/B/length-weighted` | `tortuosity/arc-chord-times-inflections/vein/B/length-weighted` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/B/mean` | `tortuosity/arc-chord-times-inflections/vein/B/mean` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/B/median` | `tortuosity/arc-chord-times-inflections/vein/B/median` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/B/std` | `tortuosity/arc-chord-times-inflections/vein/B/std` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/C/length-weighted` | `tortuosity/arc-chord-times-inflections/vein/C/length-weighted` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/C/mean` | `tortuosity/arc-chord-times-inflections/vein/C/mean` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/C/median` | `tortuosity/arc-chord-times-inflections/vein/C/median` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/C/std` | `tortuosity/arc-chord-times-inflections/vein/C/std` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/length-weighted` | `tortuosity/arc-chord-times-inflections/vein/length-weighted` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/mean` | `tortuosity/arc-chord-times-inflections/vein/mean` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/median` | `tortuosity/arc-chord-times-inflections/vein/median` | exact |  |
| `tortuosity/arc-chord-times-inflections/vein/std` | `tortuosity/arc-chord-times-inflections/vein/std` | exact |  |
| `tortuosity/grisan-density/artery/B/length-weighted` | `tortuosity/grisan-density/artery/B/length-weighted` | exact |  |
| `tortuosity/grisan-density/artery/B/mean` | `tortuosity/grisan-density/artery/B/mean` | exact |  |
| `tortuosity/grisan-density/artery/B/median` | `tortuosity/grisan-density/artery/B/median` | exact |  |
| `tortuosity/grisan-density/artery/B/std` | `tortuosity/grisan-density/artery/B/std` | exact |  |
| `tortuosity/grisan-density/artery/C/length-weighted` | `tortuosity/grisan-density/artery/C/length-weighted` | exact |  |
| `tortuosity/grisan-density/artery/C/mean` | `tortuosity/grisan-density/artery/C/mean` | exact |  |
| `tortuosity/grisan-density/artery/C/median` | `tortuosity/grisan-density/artery/C/median` | exact |  |
| `tortuosity/grisan-density/artery/C/std` | `tortuosity/grisan-density/artery/C/std` | exact |  |
| `tortuosity/grisan-density/artery/length-weighted` | `tortuosity/grisan-density/artery/length-weighted` | exact |  |
| `tortuosity/grisan-density/artery/mean` | `tortuosity/grisan-density/artery/mean` | exact |  |
| `tortuosity/grisan-density/artery/median` | `tortuosity/grisan-density/artery/median` | exact |  |
| `tortuosity/grisan-density/artery/std` | `tortuosity/grisan-density/artery/std` | exact |  |
| `tortuosity/grisan-density/vein/B/length-weighted` | `tortuosity/grisan-density/vein/B/length-weighted` | exact |  |
| `tortuosity/grisan-density/vein/B/mean` | `tortuosity/grisan-density/vein/B/mean` | exact |  |
| `tortuosity/grisan-density/vein/B/median` | `tortuosity/grisan-density/vein/B/median` | exact |  |
| `tortuosity/grisan-density/vein/B/std` | `tortuosity/grisan-density/vein/B/std` | exact |  |
| `tortuosity/grisan-density/vein/C/length-weighted` | `tortuosity/grisan-density/vein/C/length-weighted` | exact |  |
| `tortuosity/grisan-density/vein/C/mean` | `tortuosity/grisan-density/vein/C/mean` | exact |  |
| `tortuosity/grisan-density/vein/C/median` | `tortuosity/grisan-density/vein/C/median` | exact |  |
| `tortuosity/grisan-density/vein/C/std` | `tortuosity/grisan-density/vein/C/std` | exact |  |
| `tortuosity/grisan-density/vein/length-weighted` | `tortuosity/grisan-density/vein/length-weighted` | exact |  |
| `tortuosity/grisan-density/vein/mean` | `tortuosity/grisan-density/vein/mean` | exact |  |
| `tortuosity/grisan-density/vein/median` | `tortuosity/grisan-density/vein/median` | exact |  |
| `tortuosity/grisan-density/vein/std` | `tortuosity/grisan-density/vein/std` | exact |  |
| `tortuosity/hart-tau1/artery/B/length-weighted` | `tortuosity/hart-tau1/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau1/artery/B/mean` | `tortuosity/hart-tau1/artery/B/mean` | exact |  |
| `tortuosity/hart-tau1/artery/B/median` | `tortuosity/hart-tau1/artery/B/median` | exact |  |
| `tortuosity/hart-tau1/artery/B/std` | `tortuosity/hart-tau1/artery/B/std` | exact |  |
| `tortuosity/hart-tau1/artery/C/length-weighted` | `tortuosity/hart-tau1/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau1/artery/C/mean` | `tortuosity/hart-tau1/artery/C/mean` | exact |  |
| `tortuosity/hart-tau1/artery/C/median` | `tortuosity/hart-tau1/artery/C/median` | exact |  |
| `tortuosity/hart-tau1/artery/C/std` | `tortuosity/hart-tau1/artery/C/std` | exact |  |
| `tortuosity/hart-tau1/artery/length-weighted` | `tortuosity/hart-tau1/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau1/artery/mean` | `tortuosity/hart-tau1/artery/mean` | exact |  |
| `tortuosity/hart-tau1/artery/median` | `tortuosity/hart-tau1/artery/median` | exact |  |
| `tortuosity/hart-tau1/artery/std` | `tortuosity/hart-tau1/artery/std` | exact |  |
| `tortuosity/hart-tau1/vein/B/length-weighted` | `tortuosity/hart-tau1/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau1/vein/B/mean` | `tortuosity/hart-tau1/vein/B/mean` | exact |  |
| `tortuosity/hart-tau1/vein/B/median` | `tortuosity/hart-tau1/vein/B/median` | exact |  |
| `tortuosity/hart-tau1/vein/B/std` | `tortuosity/hart-tau1/vein/B/std` | exact |  |
| `tortuosity/hart-tau1/vein/C/length-weighted` | `tortuosity/hart-tau1/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau1/vein/C/mean` | `tortuosity/hart-tau1/vein/C/mean` | exact |  |
| `tortuosity/hart-tau1/vein/C/median` | `tortuosity/hart-tau1/vein/C/median` | exact |  |
| `tortuosity/hart-tau1/vein/C/std` | `tortuosity/hart-tau1/vein/C/std` | exact |  |
| `tortuosity/hart-tau1/vein/length-weighted` | `tortuosity/hart-tau1/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau1/vein/mean` | `tortuosity/hart-tau1/vein/mean` | exact |  |
| `tortuosity/hart-tau1/vein/median` | `tortuosity/hart-tau1/vein/median` | exact |  |
| `tortuosity/hart-tau1/vein/std` | `tortuosity/hart-tau1/vein/std` | exact |  |
| `tortuosity/hart-tau2/artery/B/length-weighted` | `tortuosity/hart-tau2/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau2/artery/B/mean` | `tortuosity/hart-tau2/artery/B/mean` | exact |  |
| `tortuosity/hart-tau2/artery/B/median` | `tortuosity/hart-tau2/artery/B/median` | exact |  |
| `tortuosity/hart-tau2/artery/B/std` | `tortuosity/hart-tau2/artery/B/std` | exact |  |
| `tortuosity/hart-tau2/artery/C/length-weighted` | `tortuosity/hart-tau2/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau2/artery/C/mean` | `tortuosity/hart-tau2/artery/C/mean` | exact |  |
| `tortuosity/hart-tau2/artery/C/median` | `tortuosity/hart-tau2/artery/C/median` | exact |  |
| `tortuosity/hart-tau2/artery/C/std` | `tortuosity/hart-tau2/artery/C/std` | exact |  |
| `tortuosity/hart-tau2/artery/length-weighted` | `tortuosity/hart-tau2/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau2/artery/mean` | `tortuosity/hart-tau2/artery/mean` | exact |  |
| `tortuosity/hart-tau2/artery/median` | `tortuosity/hart-tau2/artery/median` | exact |  |
| `tortuosity/hart-tau2/artery/std` | `tortuosity/hart-tau2/artery/std` | exact |  |
| `tortuosity/hart-tau2/vein/B/length-weighted` | `tortuosity/hart-tau2/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau2/vein/B/mean` | `tortuosity/hart-tau2/vein/B/mean` | exact |  |
| `tortuosity/hart-tau2/vein/B/median` | `tortuosity/hart-tau2/vein/B/median` | exact |  |
| `tortuosity/hart-tau2/vein/B/std` | `tortuosity/hart-tau2/vein/B/std` | exact |  |
| `tortuosity/hart-tau2/vein/C/length-weighted` | `tortuosity/hart-tau2/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau2/vein/C/mean` | `tortuosity/hart-tau2/vein/C/mean` | exact |  |
| `tortuosity/hart-tau2/vein/C/median` | `tortuosity/hart-tau2/vein/C/median` | exact |  |
| `tortuosity/hart-tau2/vein/C/std` | `tortuosity/hart-tau2/vein/C/std` | exact |  |
| `tortuosity/hart-tau2/vein/length-weighted` | `tortuosity/hart-tau2/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau2/vein/mean` | `tortuosity/hart-tau2/vein/mean` | exact |  |
| `tortuosity/hart-tau2/vein/median` | `tortuosity/hart-tau2/vein/median` | exact |  |
| `tortuosity/hart-tau2/vein/std` | `tortuosity/hart-tau2/vein/std` | exact |  |
| `tortuosity/hart-tau3/artery/B/length-weighted` | `tortuosity/hart-tau3/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau3/artery/B/mean` | `tortuosity/hart-tau3/artery/B/mean` | exact |  |
| `tortuosity/hart-tau3/artery/B/median` | `tortuosity/hart-tau3/artery/B/median` | exact |  |
| `tortuosity/hart-tau3/artery/B/std` | `tortuosity/hart-tau3/artery/B/std` | exact |  |
| `tortuosity/hart-tau3/artery/C/length-weighted` | `tortuosity/hart-tau3/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau3/artery/C/mean` | `tortuosity/hart-tau3/artery/C/mean` | exact |  |
| `tortuosity/hart-tau3/artery/C/median` | `tortuosity/hart-tau3/artery/C/median` | exact |  |
| `tortuosity/hart-tau3/artery/C/std` | `tortuosity/hart-tau3/artery/C/std` | exact |  |
| `tortuosity/hart-tau3/artery/length-weighted` | `tortuosity/hart-tau3/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau3/artery/mean` | `tortuosity/hart-tau3/artery/mean` | exact |  |
| `tortuosity/hart-tau3/artery/median` | `tortuosity/hart-tau3/artery/median` | exact |  |
| `tortuosity/hart-tau3/artery/std` | `tortuosity/hart-tau3/artery/std` | exact |  |
| `tortuosity/hart-tau3/vein/B/length-weighted` | `tortuosity/hart-tau3/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau3/vein/B/mean` | `tortuosity/hart-tau3/vein/B/mean` | exact |  |
| `tortuosity/hart-tau3/vein/B/median` | `tortuosity/hart-tau3/vein/B/median` | exact |  |
| `tortuosity/hart-tau3/vein/B/std` | `tortuosity/hart-tau3/vein/B/std` | exact |  |
| `tortuosity/hart-tau3/vein/C/length-weighted` | `tortuosity/hart-tau3/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau3/vein/C/mean` | `tortuosity/hart-tau3/vein/C/mean` | exact |  |
| `tortuosity/hart-tau3/vein/C/median` | `tortuosity/hart-tau3/vein/C/median` | exact |  |
| `tortuosity/hart-tau3/vein/C/std` | `tortuosity/hart-tau3/vein/C/std` | exact |  |
| `tortuosity/hart-tau3/vein/length-weighted` | `tortuosity/hart-tau3/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau3/vein/mean` | `tortuosity/hart-tau3/vein/mean` | exact |  |
| `tortuosity/hart-tau3/vein/median` | `tortuosity/hart-tau3/vein/median` | exact |  |
| `tortuosity/hart-tau3/vein/std` | `tortuosity/hart-tau3/vein/std` | exact |  |
| `tortuosity/hart-tau4/artery/B/length-weighted` | `tortuosity/hart-tau4/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau4/artery/B/mean` | `tortuosity/hart-tau4/artery/B/mean` | exact |  |
| `tortuosity/hart-tau4/artery/B/median` | `tortuosity/hart-tau4/artery/B/median` | exact |  |
| `tortuosity/hart-tau4/artery/B/std` | `tortuosity/hart-tau4/artery/B/std` | exact |  |
| `tortuosity/hart-tau4/artery/C/length-weighted` | `tortuosity/hart-tau4/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau4/artery/C/mean` | `tortuosity/hart-tau4/artery/C/mean` | exact |  |
| `tortuosity/hart-tau4/artery/C/median` | `tortuosity/hart-tau4/artery/C/median` | exact |  |
| `tortuosity/hart-tau4/artery/C/std` | `tortuosity/hart-tau4/artery/C/std` | exact |  |
| `tortuosity/hart-tau4/artery/length-weighted` | `tortuosity/hart-tau4/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau4/artery/mean` | `tortuosity/hart-tau4/artery/mean` | exact |  |
| `tortuosity/hart-tau4/artery/median` | `tortuosity/hart-tau4/artery/median` | exact |  |
| `tortuosity/hart-tau4/artery/std` | `tortuosity/hart-tau4/artery/std` | exact |  |
| `tortuosity/hart-tau4/vein/B/length-weighted` | `tortuosity/hart-tau4/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau4/vein/B/mean` | `tortuosity/hart-tau4/vein/B/mean` | exact |  |
| `tortuosity/hart-tau4/vein/B/median` | `tortuosity/hart-tau4/vein/B/median` | exact |  |
| `tortuosity/hart-tau4/vein/B/std` | `tortuosity/hart-tau4/vein/B/std` | exact |  |
| `tortuosity/hart-tau4/vein/C/length-weighted` | `tortuosity/hart-tau4/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau4/vein/C/mean` | `tortuosity/hart-tau4/vein/C/mean` | exact |  |
| `tortuosity/hart-tau4/vein/C/median` | `tortuosity/hart-tau4/vein/C/median` | exact |  |
| `tortuosity/hart-tau4/vein/C/std` | `tortuosity/hart-tau4/vein/C/std` | exact |  |
| `tortuosity/hart-tau4/vein/length-weighted` | `tortuosity/hart-tau4/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau4/vein/mean` | `tortuosity/hart-tau4/vein/mean` | exact |  |
| `tortuosity/hart-tau4/vein/median` | `tortuosity/hart-tau4/vein/median` | exact |  |
| `tortuosity/hart-tau4/vein/std` | `tortuosity/hart-tau4/vein/std` | exact |  |
| `tortuosity/hart-tau5/artery/B/length-weighted` | `tortuosity/hart-tau5/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau5/artery/B/mean` | `tortuosity/hart-tau5/artery/B/mean` | exact |  |
| `tortuosity/hart-tau5/artery/B/median` | `tortuosity/hart-tau5/artery/B/median` | exact |  |
| `tortuosity/hart-tau5/artery/B/std` | `tortuosity/hart-tau5/artery/B/std` | exact |  |
| `tortuosity/hart-tau5/artery/C/length-weighted` | `tortuosity/hart-tau5/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau5/artery/C/mean` | `tortuosity/hart-tau5/artery/C/mean` | exact |  |
| `tortuosity/hart-tau5/artery/C/median` | `tortuosity/hart-tau5/artery/C/median` | exact |  |
| `tortuosity/hart-tau5/artery/C/std` | `tortuosity/hart-tau5/artery/C/std` | exact |  |
| `tortuosity/hart-tau5/artery/length-weighted` | `tortuosity/hart-tau5/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau5/artery/mean` | `tortuosity/hart-tau5/artery/mean` | exact |  |
| `tortuosity/hart-tau5/artery/median` | `tortuosity/hart-tau5/artery/median` | exact |  |
| `tortuosity/hart-tau5/artery/std` | `tortuosity/hart-tau5/artery/std` | exact |  |
| `tortuosity/hart-tau5/vein/B/length-weighted` | `tortuosity/hart-tau5/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau5/vein/B/mean` | `tortuosity/hart-tau5/vein/B/mean` | exact |  |
| `tortuosity/hart-tau5/vein/B/median` | `tortuosity/hart-tau5/vein/B/median` | exact |  |
| `tortuosity/hart-tau5/vein/B/std` | `tortuosity/hart-tau5/vein/B/std` | exact |  |
| `tortuosity/hart-tau5/vein/C/length-weighted` | `tortuosity/hart-tau5/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau5/vein/C/mean` | `tortuosity/hart-tau5/vein/C/mean` | exact |  |
| `tortuosity/hart-tau5/vein/C/median` | `tortuosity/hart-tau5/vein/C/median` | exact |  |
| `tortuosity/hart-tau5/vein/C/std` | `tortuosity/hart-tau5/vein/C/std` | exact |  |
| `tortuosity/hart-tau5/vein/length-weighted` | `tortuosity/hart-tau5/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau5/vein/mean` | `tortuosity/hart-tau5/vein/mean` | exact |  |
| `tortuosity/hart-tau5/vein/median` | `tortuosity/hart-tau5/vein/median` | exact |  |
| `tortuosity/hart-tau5/vein/std` | `tortuosity/hart-tau5/vein/std` | exact |  |
| `tortuosity/hart-tau6/artery/B/length-weighted` | `tortuosity/hart-tau6/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau6/artery/B/mean` | `tortuosity/hart-tau6/artery/B/mean` | exact |  |
| `tortuosity/hart-tau6/artery/B/median` | `tortuosity/hart-tau6/artery/B/median` | exact |  |
| `tortuosity/hart-tau6/artery/B/std` | `tortuosity/hart-tau6/artery/B/std` | exact |  |
| `tortuosity/hart-tau6/artery/C/length-weighted` | `tortuosity/hart-tau6/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau6/artery/C/mean` | `tortuosity/hart-tau6/artery/C/mean` | exact |  |
| `tortuosity/hart-tau6/artery/C/median` | `tortuosity/hart-tau6/artery/C/median` | exact |  |
| `tortuosity/hart-tau6/artery/C/std` | `tortuosity/hart-tau6/artery/C/std` | exact |  |
| `tortuosity/hart-tau6/artery/length-weighted` | `tortuosity/hart-tau6/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau6/artery/mean` | `tortuosity/hart-tau6/artery/mean` | exact |  |
| `tortuosity/hart-tau6/artery/median` | `tortuosity/hart-tau6/artery/median` | exact |  |
| `tortuosity/hart-tau6/artery/std` | `tortuosity/hart-tau6/artery/std` | exact |  |
| `tortuosity/hart-tau6/vein/B/length-weighted` | `tortuosity/hart-tau6/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau6/vein/B/mean` | `tortuosity/hart-tau6/vein/B/mean` | exact |  |
| `tortuosity/hart-tau6/vein/B/median` | `tortuosity/hart-tau6/vein/B/median` | exact |  |
| `tortuosity/hart-tau6/vein/B/std` | `tortuosity/hart-tau6/vein/B/std` | exact |  |
| `tortuosity/hart-tau6/vein/C/length-weighted` | `tortuosity/hart-tau6/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau6/vein/C/mean` | `tortuosity/hart-tau6/vein/C/mean` | exact |  |
| `tortuosity/hart-tau6/vein/C/median` | `tortuosity/hart-tau6/vein/C/median` | exact |  |
| `tortuosity/hart-tau6/vein/C/std` | `tortuosity/hart-tau6/vein/C/std` | exact |  |
| `tortuosity/hart-tau6/vein/length-weighted` | `tortuosity/hart-tau6/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau6/vein/mean` | `tortuosity/hart-tau6/vein/mean` | exact |  |
| `tortuosity/hart-tau6/vein/median` | `tortuosity/hart-tau6/vein/median` | exact |  |
| `tortuosity/hart-tau6/vein/std` | `tortuosity/hart-tau6/vein/std` | exact |  |
| `tortuosity/hart-tau7/artery/B/length-weighted` | `tortuosity/hart-tau7/artery/B/length-weighted` | exact |  |
| `tortuosity/hart-tau7/artery/B/mean` | `tortuosity/hart-tau7/artery/B/mean` | exact |  |
| `tortuosity/hart-tau7/artery/B/median` | `tortuosity/hart-tau7/artery/B/median` | exact |  |
| `tortuosity/hart-tau7/artery/B/std` | `tortuosity/hart-tau7/artery/B/std` | exact |  |
| `tortuosity/hart-tau7/artery/C/length-weighted` | `tortuosity/hart-tau7/artery/C/length-weighted` | exact |  |
| `tortuosity/hart-tau7/artery/C/mean` | `tortuosity/hart-tau7/artery/C/mean` | exact |  |
| `tortuosity/hart-tau7/artery/C/median` | `tortuosity/hart-tau7/artery/C/median` | exact |  |
| `tortuosity/hart-tau7/artery/C/std` | `tortuosity/hart-tau7/artery/C/std` | exact |  |
| `tortuosity/hart-tau7/artery/length-weighted` | `tortuosity/hart-tau7/artery/length-weighted` | exact |  |
| `tortuosity/hart-tau7/artery/mean` | `tortuosity/hart-tau7/artery/mean` | exact |  |
| `tortuosity/hart-tau7/artery/median` | `tortuosity/hart-tau7/artery/median` | exact |  |
| `tortuosity/hart-tau7/artery/std` | `tortuosity/hart-tau7/artery/std` | exact |  |
| `tortuosity/hart-tau7/vein/B/length-weighted` | `tortuosity/hart-tau7/vein/B/length-weighted` | exact |  |
| `tortuosity/hart-tau7/vein/B/mean` | `tortuosity/hart-tau7/vein/B/mean` | exact |  |
| `tortuosity/hart-tau7/vein/B/median` | `tortuosity/hart-tau7/vein/B/median` | exact |  |
| `tortuosity/hart-tau7/vein/B/std` | `tortuosity/hart-tau7/vein/B/std` | exact |  |
| `tortuosity/hart-tau7/vein/C/length-weighted` | `tortuosity/hart-tau7/vein/C/length-weighted` | exact |  |
| `tortuosity/hart-tau7/vein/C/mean` | `tortuosity/hart-tau7/vein/C/mean` | exact |  |
| `tortuosity/hart-tau7/vein/C/median` | `tortuosity/hart-tau7/vein/C/median` | exact |  |
| `tortuosity/hart-tau7/vein/C/std` | `tortuosity/hart-tau7/vein/C/std` | exact |  |
| `tortuosity/hart-tau7/vein/length-weighted` | `tortuosity/hart-tau7/vein/length-weighted` | exact |  |
| `tortuosity/hart-tau7/vein/mean` | `tortuosity/hart-tau7/vein/mean` | exact |  |
| `tortuosity/hart-tau7/vein/median` | `tortuosity/hart-tau7/vein/median` | exact |  |
| `tortuosity/hart-tau7/vein/std` | `tortuosity/hart-tau7/vein/std` | exact |  |
| `tortuosity/inflection-count/artery` | `tortuosity/inflection-count/artery` | exact |  |
| `tortuosity/inflection-count/artery/B` | `tortuosity/inflection-count/artery/B` | exact |  |
| `tortuosity/inflection-count/artery/C` | `tortuosity/inflection-count/artery/C` | exact |  |
| `tortuosity/inflection-count/vein` | `tortuosity/inflection-count/vein` | exact |  |
| `tortuosity/inflection-count/vein/B` | `tortuosity/inflection-count/vein/B` | exact |  |
| `tortuosity/inflection-count/vein/C` | `tortuosity/inflection-count/vein/C` | exact |  |
| `tortuosity/spline-curvature/artery/B/length-weighted` | `tortuosity/spline-curvature/artery/B/length-weighted` | exact |  |
| `tortuosity/spline-curvature/artery/B/mean` | `tortuosity/spline-curvature/artery/B/mean` | exact |  |
| `tortuosity/spline-curvature/artery/B/median` | `tortuosity/spline-curvature/artery/B/median` | exact |  |
| `tortuosity/spline-curvature/artery/B/std` | `tortuosity/spline-curvature/artery/B/std` | exact |  |
| `tortuosity/spline-curvature/artery/C/length-weighted` | `tortuosity/spline-curvature/artery/C/length-weighted` | exact |  |
| `tortuosity/spline-curvature/artery/C/mean` | `tortuosity/spline-curvature/artery/C/mean` | exact |  |
| `tortuosity/spline-curvature/artery/C/median` | `tortuosity/spline-curvature/artery/C/median` | exact |  |
| `tortuosity/spline-curvature/artery/C/std` | `tortuosity/spline-curvature/artery/C/std` | exact |  |
| `tortuosity/spline-curvature/artery/length-weighted` | `tortuosity/spline-curvature/artery/length-weighted` | exact |  |
| `tortuosity/spline-curvature/artery/mean` | `tortuosity/spline-curvature/artery/mean` | exact |  |
| `tortuosity/spline-curvature/artery/median` | `tortuosity/spline-curvature/artery/median` | exact |  |
| `tortuosity/spline-curvature/artery/std` | `tortuosity/spline-curvature/artery/std` | exact |  |
| `tortuosity/spline-curvature/vein/B/length-weighted` | `tortuosity/spline-curvature/vein/B/length-weighted` | exact |  |
| `tortuosity/spline-curvature/vein/B/mean` | `tortuosity/spline-curvature/vein/B/mean` | exact |  |
| `tortuosity/spline-curvature/vein/B/median` | `tortuosity/spline-curvature/vein/B/median` | exact |  |
| `tortuosity/spline-curvature/vein/B/std` | `tortuosity/spline-curvature/vein/B/std` | exact |  |
| `tortuosity/spline-curvature/vein/C/length-weighted` | `tortuosity/spline-curvature/vein/C/length-weighted` | exact |  |
| `tortuosity/spline-curvature/vein/C/mean` | `tortuosity/spline-curvature/vein/C/mean` | exact |  |
| `tortuosity/spline-curvature/vein/C/median` | `tortuosity/spline-curvature/vein/C/median` | exact |  |
| `tortuosity/spline-curvature/vein/C/std` | `tortuosity/spline-curvature/vein/C/std` | exact |  |
| `tortuosity/spline-curvature/vein/length-weighted` | `tortuosity/spline-curvature/vein/length-weighted` | exact |  |
| `tortuosity/spline-curvature/vein/mean` | `tortuosity/spline-curvature/vein/mean` | exact |  |
| `tortuosity/spline-curvature/vein/median` | `tortuosity/spline-curvature/vein/median` | exact |  |
| `tortuosity/spline-curvature/vein/std` | `tortuosity/spline-curvature/vein/std` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/B/length-weighted` | `tortuosity/vessel-arc-chord-times-inflections/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/B/mean` | `tortuosity/vessel-arc-chord-times-inflections/artery/B/mean` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/B/median` | `tortuosity/vessel-arc-chord-times-inflections/artery/B/median` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/B/std` | `tortuosity/vessel-arc-chord-times-inflections/artery/B/std` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/C/length-weighted` | `tortuosity/vessel-arc-chord-times-inflections/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/C/mean` | `tortuosity/vessel-arc-chord-times-inflections/artery/C/mean` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/C/median` | `tortuosity/vessel-arc-chord-times-inflections/artery/C/median` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/C/std` | `tortuosity/vessel-arc-chord-times-inflections/artery/C/std` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/length-weighted` | `tortuosity/vessel-arc-chord-times-inflections/artery/length-weighted` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/mean` | `tortuosity/vessel-arc-chord-times-inflections/artery/mean` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/median` | `tortuosity/vessel-arc-chord-times-inflections/artery/median` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/artery/std` | `tortuosity/vessel-arc-chord-times-inflections/artery/std` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/B/length-weighted` | `tortuosity/vessel-arc-chord-times-inflections/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/B/mean` | `tortuosity/vessel-arc-chord-times-inflections/vein/B/mean` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/B/median` | `tortuosity/vessel-arc-chord-times-inflections/vein/B/median` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/B/std` | `tortuosity/vessel-arc-chord-times-inflections/vein/B/std` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/C/length-weighted` | `tortuosity/vessel-arc-chord-times-inflections/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/C/mean` | `tortuosity/vessel-arc-chord-times-inflections/vein/C/mean` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/C/median` | `tortuosity/vessel-arc-chord-times-inflections/vein/C/median` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/C/std` | `tortuosity/vessel-arc-chord-times-inflections/vein/C/std` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/length-weighted` | `tortuosity/vessel-arc-chord-times-inflections/vein/length-weighted` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/mean` | `tortuosity/vessel-arc-chord-times-inflections/vein/mean` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/median` | `tortuosity/vessel-arc-chord-times-inflections/vein/median` | exact |  |
| `tortuosity/vessel-arc-chord-times-inflections/vein/std` | `tortuosity/vessel-arc-chord-times-inflections/vein/std` | exact |  |
| `tortuosity/vessel-grisan-density/artery/B/length-weighted` | `tortuosity/vessel-grisan-density/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-grisan-density/artery/B/mean` | `tortuosity/vessel-grisan-density/artery/B/mean` | exact |  |
| `tortuosity/vessel-grisan-density/artery/B/median` | `tortuosity/vessel-grisan-density/artery/B/median` | exact |  |
| `tortuosity/vessel-grisan-density/artery/B/std` | `tortuosity/vessel-grisan-density/artery/B/std` | exact |  |
| `tortuosity/vessel-grisan-density/artery/C/length-weighted` | `tortuosity/vessel-grisan-density/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-grisan-density/artery/C/mean` | `tortuosity/vessel-grisan-density/artery/C/mean` | exact |  |
| `tortuosity/vessel-grisan-density/artery/C/median` | `tortuosity/vessel-grisan-density/artery/C/median` | exact |  |
| `tortuosity/vessel-grisan-density/artery/C/std` | `tortuosity/vessel-grisan-density/artery/C/std` | exact |  |
| `tortuosity/vessel-grisan-density/artery/length-weighted` | `tortuosity/vessel-grisan-density/artery/length-weighted` | exact |  |
| `tortuosity/vessel-grisan-density/artery/mean` | `tortuosity/vessel-grisan-density/artery/mean` | exact |  |
| `tortuosity/vessel-grisan-density/artery/median` | `tortuosity/vessel-grisan-density/artery/median` | exact |  |
| `tortuosity/vessel-grisan-density/artery/std` | `tortuosity/vessel-grisan-density/artery/std` | exact |  |
| `tortuosity/vessel-grisan-density/vein/B/length-weighted` | `tortuosity/vessel-grisan-density/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-grisan-density/vein/B/mean` | `tortuosity/vessel-grisan-density/vein/B/mean` | exact |  |
| `tortuosity/vessel-grisan-density/vein/B/median` | `tortuosity/vessel-grisan-density/vein/B/median` | exact |  |
| `tortuosity/vessel-grisan-density/vein/B/std` | `tortuosity/vessel-grisan-density/vein/B/std` | exact |  |
| `tortuosity/vessel-grisan-density/vein/C/length-weighted` | `tortuosity/vessel-grisan-density/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-grisan-density/vein/C/mean` | `tortuosity/vessel-grisan-density/vein/C/mean` | exact |  |
| `tortuosity/vessel-grisan-density/vein/C/median` | `tortuosity/vessel-grisan-density/vein/C/median` | exact |  |
| `tortuosity/vessel-grisan-density/vein/C/std` | `tortuosity/vessel-grisan-density/vein/C/std` | exact |  |
| `tortuosity/vessel-grisan-density/vein/length-weighted` | `tortuosity/vessel-grisan-density/vein/length-weighted` | exact |  |
| `tortuosity/vessel-grisan-density/vein/mean` | `tortuosity/vessel-grisan-density/vein/mean` | exact |  |
| `tortuosity/vessel-grisan-density/vein/median` | `tortuosity/vessel-grisan-density/vein/median` | exact |  |
| `tortuosity/vessel-grisan-density/vein/std` | `tortuosity/vessel-grisan-density/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/B/length-weighted` | `tortuosity/vessel-hart-tau1/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/B/mean` | `tortuosity/vessel-hart-tau1/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/B/median` | `tortuosity/vessel-hart-tau1/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/B/std` | `tortuosity/vessel-hart-tau1/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/C/length-weighted` | `tortuosity/vessel-hart-tau1/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/C/mean` | `tortuosity/vessel-hart-tau1/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/C/median` | `tortuosity/vessel-hart-tau1/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/C/std` | `tortuosity/vessel-hart-tau1/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/length-weighted` | `tortuosity/vessel-hart-tau1/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/mean` | `tortuosity/vessel-hart-tau1/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/median` | `tortuosity/vessel-hart-tau1/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau1/artery/std` | `tortuosity/vessel-hart-tau1/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/B/length-weighted` | `tortuosity/vessel-hart-tau1/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/B/mean` | `tortuosity/vessel-hart-tau1/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/B/median` | `tortuosity/vessel-hart-tau1/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/B/std` | `tortuosity/vessel-hart-tau1/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/C/length-weighted` | `tortuosity/vessel-hart-tau1/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/C/mean` | `tortuosity/vessel-hart-tau1/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/C/median` | `tortuosity/vessel-hart-tau1/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/C/std` | `tortuosity/vessel-hart-tau1/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/length-weighted` | `tortuosity/vessel-hart-tau1/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/mean` | `tortuosity/vessel-hart-tau1/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/median` | `tortuosity/vessel-hart-tau1/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau1/vein/std` | `tortuosity/vessel-hart-tau1/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/B/length-weighted` | `tortuosity/vessel-hart-tau2/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/B/mean` | `tortuosity/vessel-hart-tau2/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/B/median` | `tortuosity/vessel-hart-tau2/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/B/std` | `tortuosity/vessel-hart-tau2/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/C/length-weighted` | `tortuosity/vessel-hart-tau2/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/C/mean` | `tortuosity/vessel-hart-tau2/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/C/median` | `tortuosity/vessel-hart-tau2/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/C/std` | `tortuosity/vessel-hart-tau2/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/length-weighted` | `tortuosity/vessel-hart-tau2/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/mean` | `tortuosity/vessel-hart-tau2/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/median` | `tortuosity/vessel-hart-tau2/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau2/artery/std` | `tortuosity/vessel-hart-tau2/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/B/length-weighted` | `tortuosity/vessel-hart-tau2/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/B/mean` | `tortuosity/vessel-hart-tau2/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/B/median` | `tortuosity/vessel-hart-tau2/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/B/std` | `tortuosity/vessel-hart-tau2/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/C/length-weighted` | `tortuosity/vessel-hart-tau2/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/C/mean` | `tortuosity/vessel-hart-tau2/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/C/median` | `tortuosity/vessel-hart-tau2/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/C/std` | `tortuosity/vessel-hart-tau2/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/length-weighted` | `tortuosity/vessel-hart-tau2/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/mean` | `tortuosity/vessel-hart-tau2/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/median` | `tortuosity/vessel-hart-tau2/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau2/vein/std` | `tortuosity/vessel-hart-tau2/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/B/length-weighted` | `tortuosity/vessel-hart-tau3/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/B/mean` | `tortuosity/vessel-hart-tau3/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/B/median` | `tortuosity/vessel-hart-tau3/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/B/std` | `tortuosity/vessel-hart-tau3/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/C/length-weighted` | `tortuosity/vessel-hart-tau3/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/C/mean` | `tortuosity/vessel-hart-tau3/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/C/median` | `tortuosity/vessel-hart-tau3/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/C/std` | `tortuosity/vessel-hart-tau3/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/length-weighted` | `tortuosity/vessel-hart-tau3/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/mean` | `tortuosity/vessel-hart-tau3/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/median` | `tortuosity/vessel-hart-tau3/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau3/artery/std` | `tortuosity/vessel-hart-tau3/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/B/length-weighted` | `tortuosity/vessel-hart-tau3/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/B/mean` | `tortuosity/vessel-hart-tau3/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/B/median` | `tortuosity/vessel-hart-tau3/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/B/std` | `tortuosity/vessel-hart-tau3/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/C/length-weighted` | `tortuosity/vessel-hart-tau3/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/C/mean` | `tortuosity/vessel-hart-tau3/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/C/median` | `tortuosity/vessel-hart-tau3/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/C/std` | `tortuosity/vessel-hart-tau3/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/length-weighted` | `tortuosity/vessel-hart-tau3/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/mean` | `tortuosity/vessel-hart-tau3/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/median` | `tortuosity/vessel-hart-tau3/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau3/vein/std` | `tortuosity/vessel-hart-tau3/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/B/length-weighted` | `tortuosity/vessel-hart-tau4/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/B/mean` | `tortuosity/vessel-hart-tau4/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/B/median` | `tortuosity/vessel-hart-tau4/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/B/std` | `tortuosity/vessel-hart-tau4/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/C/length-weighted` | `tortuosity/vessel-hart-tau4/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/C/mean` | `tortuosity/vessel-hart-tau4/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/C/median` | `tortuosity/vessel-hart-tau4/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/C/std` | `tortuosity/vessel-hart-tau4/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/length-weighted` | `tortuosity/vessel-hart-tau4/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/mean` | `tortuosity/vessel-hart-tau4/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/median` | `tortuosity/vessel-hart-tau4/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau4/artery/std` | `tortuosity/vessel-hart-tau4/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/B/length-weighted` | `tortuosity/vessel-hart-tau4/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/B/mean` | `tortuosity/vessel-hart-tau4/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/B/median` | `tortuosity/vessel-hart-tau4/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/B/std` | `tortuosity/vessel-hart-tau4/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/C/length-weighted` | `tortuosity/vessel-hart-tau4/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/C/mean` | `tortuosity/vessel-hart-tau4/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/C/median` | `tortuosity/vessel-hart-tau4/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/C/std` | `tortuosity/vessel-hart-tau4/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/length-weighted` | `tortuosity/vessel-hart-tau4/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/mean` | `tortuosity/vessel-hart-tau4/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/median` | `tortuosity/vessel-hart-tau4/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau4/vein/std` | `tortuosity/vessel-hart-tau4/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/B/length-weighted` | `tortuosity/vessel-hart-tau5/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/B/mean` | `tortuosity/vessel-hart-tau5/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/B/median` | `tortuosity/vessel-hart-tau5/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/B/std` | `tortuosity/vessel-hart-tau5/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/C/length-weighted` | `tortuosity/vessel-hart-tau5/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/C/mean` | `tortuosity/vessel-hart-tau5/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/C/median` | `tortuosity/vessel-hart-tau5/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/C/std` | `tortuosity/vessel-hart-tau5/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/length-weighted` | `tortuosity/vessel-hart-tau5/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/mean` | `tortuosity/vessel-hart-tau5/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/median` | `tortuosity/vessel-hart-tau5/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau5/artery/std` | `tortuosity/vessel-hart-tau5/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/B/length-weighted` | `tortuosity/vessel-hart-tau5/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/B/mean` | `tortuosity/vessel-hart-tau5/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/B/median` | `tortuosity/vessel-hart-tau5/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/B/std` | `tortuosity/vessel-hart-tau5/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/C/length-weighted` | `tortuosity/vessel-hart-tau5/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/C/mean` | `tortuosity/vessel-hart-tau5/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/C/median` | `tortuosity/vessel-hart-tau5/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/C/std` | `tortuosity/vessel-hart-tau5/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/length-weighted` | `tortuosity/vessel-hart-tau5/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/mean` | `tortuosity/vessel-hart-tau5/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/median` | `tortuosity/vessel-hart-tau5/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau5/vein/std` | `tortuosity/vessel-hart-tau5/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/B/length-weighted` | `tortuosity/vessel-hart-tau6/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/B/mean` | `tortuosity/vessel-hart-tau6/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/B/median` | `tortuosity/vessel-hart-tau6/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/B/std` | `tortuosity/vessel-hart-tau6/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/C/length-weighted` | `tortuosity/vessel-hart-tau6/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/C/mean` | `tortuosity/vessel-hart-tau6/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/C/median` | `tortuosity/vessel-hart-tau6/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/C/std` | `tortuosity/vessel-hart-tau6/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/length-weighted` | `tortuosity/vessel-hart-tau6/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/mean` | `tortuosity/vessel-hart-tau6/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/median` | `tortuosity/vessel-hart-tau6/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau6/artery/std` | `tortuosity/vessel-hart-tau6/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/B/length-weighted` | `tortuosity/vessel-hart-tau6/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/B/mean` | `tortuosity/vessel-hart-tau6/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/B/median` | `tortuosity/vessel-hart-tau6/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/B/std` | `tortuosity/vessel-hart-tau6/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/C/length-weighted` | `tortuosity/vessel-hart-tau6/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/C/mean` | `tortuosity/vessel-hart-tau6/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/C/median` | `tortuosity/vessel-hart-tau6/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/C/std` | `tortuosity/vessel-hart-tau6/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/length-weighted` | `tortuosity/vessel-hart-tau6/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/mean` | `tortuosity/vessel-hart-tau6/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/median` | `tortuosity/vessel-hart-tau6/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau6/vein/std` | `tortuosity/vessel-hart-tau6/vein/std` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/B/length-weighted` | `tortuosity/vessel-hart-tau7/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/B/mean` | `tortuosity/vessel-hart-tau7/artery/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/B/median` | `tortuosity/vessel-hart-tau7/artery/B/median` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/B/std` | `tortuosity/vessel-hart-tau7/artery/B/std` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/C/length-weighted` | `tortuosity/vessel-hart-tau7/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/C/mean` | `tortuosity/vessel-hart-tau7/artery/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/C/median` | `tortuosity/vessel-hart-tau7/artery/C/median` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/C/std` | `tortuosity/vessel-hart-tau7/artery/C/std` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/length-weighted` | `tortuosity/vessel-hart-tau7/artery/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/mean` | `tortuosity/vessel-hart-tau7/artery/mean` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/median` | `tortuosity/vessel-hart-tau7/artery/median` | exact |  |
| `tortuosity/vessel-hart-tau7/artery/std` | `tortuosity/vessel-hart-tau7/artery/std` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/B/length-weighted` | `tortuosity/vessel-hart-tau7/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/B/mean` | `tortuosity/vessel-hart-tau7/vein/B/mean` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/B/median` | `tortuosity/vessel-hart-tau7/vein/B/median` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/B/std` | `tortuosity/vessel-hart-tau7/vein/B/std` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/C/length-weighted` | `tortuosity/vessel-hart-tau7/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/C/mean` | `tortuosity/vessel-hart-tau7/vein/C/mean` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/C/median` | `tortuosity/vessel-hart-tau7/vein/C/median` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/C/std` | `tortuosity/vessel-hart-tau7/vein/C/std` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/length-weighted` | `tortuosity/vessel-hart-tau7/vein/length-weighted` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/mean` | `tortuosity/vessel-hart-tau7/vein/mean` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/median` | `tortuosity/vessel-hart-tau7/vein/median` | exact |  |
| `tortuosity/vessel-hart-tau7/vein/std` | `tortuosity/vessel-hart-tau7/vein/std` | exact |  |
| `tortuosity/vessel-inflection-count/artery` | `tortuosity/vessel-inflection-count/artery` | exact |  |
| `tortuosity/vessel-inflection-count/artery/B` | `tortuosity/vessel-inflection-count/artery/B` | exact |  |
| `tortuosity/vessel-inflection-count/artery/C` | `tortuosity/vessel-inflection-count/artery/C` | exact |  |
| `tortuosity/vessel-inflection-count/vein` | `tortuosity/vessel-inflection-count/vein` | exact |  |
| `tortuosity/vessel-inflection-count/vein/B` | `tortuosity/vessel-inflection-count/vein/B` | exact |  |
| `tortuosity/vessel-inflection-count/vein/C` | `tortuosity/vessel-inflection-count/vein/C` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/B/length-weighted` | `tortuosity/vessel-spline-curvature/artery/B/length-weighted` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/B/mean` | `tortuosity/vessel-spline-curvature/artery/B/mean` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/B/median` | `tortuosity/vessel-spline-curvature/artery/B/median` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/B/std` | `tortuosity/vessel-spline-curvature/artery/B/std` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/C/length-weighted` | `tortuosity/vessel-spline-curvature/artery/C/length-weighted` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/C/mean` | `tortuosity/vessel-spline-curvature/artery/C/mean` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/C/median` | `tortuosity/vessel-spline-curvature/artery/C/median` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/C/std` | `tortuosity/vessel-spline-curvature/artery/C/std` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/length-weighted` | `tortuosity/vessel-spline-curvature/artery/length-weighted` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/mean` | `tortuosity/vessel-spline-curvature/artery/mean` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/median` | `tortuosity/vessel-spline-curvature/artery/median` | exact |  |
| `tortuosity/vessel-spline-curvature/artery/std` | `tortuosity/vessel-spline-curvature/artery/std` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/B/length-weighted` | `tortuosity/vessel-spline-curvature/vein/B/length-weighted` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/B/mean` | `tortuosity/vessel-spline-curvature/vein/B/mean` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/B/median` | `tortuosity/vessel-spline-curvature/vein/B/median` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/B/std` | `tortuosity/vessel-spline-curvature/vein/B/std` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/C/length-weighted` | `tortuosity/vessel-spline-curvature/vein/C/length-weighted` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/C/mean` | `tortuosity/vessel-spline-curvature/vein/C/mean` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/C/median` | `tortuosity/vessel-spline-curvature/vein/C/median` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/C/std` | `tortuosity/vessel-spline-curvature/vein/C/std` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/length-weighted` | `tortuosity/vessel-spline-curvature/vein/length-weighted` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/mean` | `tortuosity/vessel-spline-curvature/vein/mean` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/median` | `tortuosity/vessel-spline-curvature/vein/median` | exact |  |
| `tortuosity/vessel-spline-curvature/vein/std` | `tortuosity/vessel-spline-curvature/vein/std` | exact |  |

</details>
<!-- /generated -->

## 7. Examples and notebooks

Private — the repository carries one notebook per development stage under `notebooks/wip/`.

## 8. Known defects

None recorded as of 2026-11-10.

## 9. Notes

- **How it traces is not documented here**, by design: `PLAN-BIOMARKER.md` §5.4 keeps every
  algorithm and constant of a proprietary implementation out of this repository, and its commit id
  is the fingerprint that covers them (§5.5). That is the one respect in which this page cannot
  meet §4.1's requirement that an implementation document its tracing.
- **The scale is required.** The library refuses to guess one; with no microns-per-pixel figure
  every value is empty.

---

**Links and license last checked:** 2026-11-10
