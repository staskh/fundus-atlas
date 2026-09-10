---
name: document-biomarker
description: Catalogue a retinal vascular biomarker — one measurement computed from fundus segmentations, such as vessel calibre, CRAE, tortuosity or fractal dimension — as a page in docs/biomarkers/ plus a row in the docs/BIOMARKERS.md summary table. Use when adding, updating, or reviewing a biomarker entry in Fundus Atlas.
---

# Documenting a biomarker

A **biomarker** here means one measurement derived from a colour-fundus photograph's
segmentations: a number, or a small family of numbers, that a researcher would put in a
spreadsheet column. Vessel calibre, the central retinal arteriolar equivalent, tortuosity, vascular
density, fractal dimension and bifurcation angle are biomarkers. The network that produced the mask
is a **model** (`document-model`); the software that runs models and biomarkers end to end is a
**project** (`document-project`).

**The reason this catalogue exists:** a biomarker name is not a definition. "Tortuosity" names at
least three incompatible formulas, "CRAE" two, and "vessel density" differs by what counts as the
denominator. Papers report the name and omit the choice. A biomarker page's job is to make the
choices visible, so that two numbers carrying the same label can be told apart.

## 1. What you produce

Every biomarker produces exactly two things:

1. **A detail page**, `docs/biomarkers/<slug>.md`, following `template.md` in this skill directory.
   The slug is the biomarker's common name, lowercased, spaces replaced by hyphens (`Vessel
   calibre` becomes `vessel-calibre.md`, `CRAE` becomes `crae.md`).
2. **A row in `docs/BIOMARKERS.md`**, the summary table, linking to that detail page.

One page per biomarker, not per variant: the variants of one measurement belong together on its
page, because comparing them is the point. Two measurements that merely share a family (calibre and
the artery-vein ratio derived from it) are separate pages, cross-linked.

## 2. Required sections of the detail page

Use `template.md` verbatim and keep its section numbering.

1. **What it measures** — in plain language, for a clinician or researcher: what the number
   describes about the eye, which direction is considered abnormal, and what it has been associated
   with. No formulas here.
2. **Definition of record** — the publication that first defined it, with a DOI or stable link, and
   the formula as that paper states it. Where the field has no single origin, say so and name the
   paper each variant traces to.
3. **Variants** — one subsection per competing definition under this name, each with its formula in
   words, its source publication, and which catalogued projects implement it. This is the most
   important section on the page. State plainly whether the variants are **numerically comparable**:
   if they are not, say that a value is meaningless without its variant recorded.
4. **Inputs required** — which segmentations it consumes (vessels, artery/vein, disc, cup, fovea),
   and what geometry it derives from them: a skeleton, a calibre profile along each segment, the
   disc centre and diameter, individual vessel segments split at junctions. Be specific: most
   disagreement between implementations of one formula comes from this step, not the formula.
5. **Measurement region** — whole image, a disc-centred zone (name it and give its radii in disc
   diameters), an ETDRS grid field, a hemifield. Where the convention varies between
   implementations, list each.
6. **Units and scale dependence** — the unit as computed (pixels, microns, degrees, a
   dimensionless ratio), and whether the number depends on:
   - **the pixel grid** the segmentation was produced on (see the grid field on each model page —
     a width in pixels means nothing without it);
   - **a physical scale** (camera resolution in microns per pixel, or a disc-diameter normalisation);
   - **the field of view**, which changes how much retina is inside the frame.
   Say explicitly whether the biomarker is scale-invariant. A dimensionless ratio usually is; a
   width, area or length usually is not.
7. **Implementations** — one row per catalogued project that computes it, with the source file, the
   variant implemented, and whether it reuses another project's code or reimplements it. Shared
   code means correlated errors, so record lineage, not just presence.
8. **Sensitivity and failure modes** — what makes the number move for reasons unrelated to the eye:
   segmentation errors, how segments are split at junctions, image quality, how few vessels are
   found, resampling. Where a published reproducibility figure exists (an intraclass correlation
   between two photographs of one eye, say), give it and attribute it.
9. **Known defects** — bugs in specific implementations that change the number, each with its
   evidence: the upstream issue or commit, which outputs it affects, whether it is fixed and where.
   Follow the project skill's rules: record a defect where it lives, attribute a claimed fix to
   whoever claims it, and write `None recorded` with the date when nothing is known — an absence of
   findings, not a clean bill of health.

A section that does not apply stays in the page, marked `Not applicable` with a short reason. A
section whose answer could not be established is marked `Unknown` — never filled with a guess.

## 3. Rules that apply to every entry

- **3.1 Reference, never redistribute.** Link to publications and to implementations at their
  original source (see `CLAUDE.md` §2).
- **3.2 Separate claim from observation.** A paper's reported reproducibility or clinical
  association is its authors' claim, attributed as such. This repository's own measurements live in
  the comparison tables.
- **3.3 Write for a non-engineer.** Section 1 must be readable by someone who will never open the
  code. Formulas belong in sections 2 and 3, stated in words before symbols.
- **3.4 Number every heading**, as the template does.
- **3.5 Never present one variant as *the* definition** because it is the most common. Name it as a
  variant like any other, and say which projects use it.
- **3.6 Date what you checked**, at the bottom of the page.
- **3.7 Keep the catalogues consistent.** A biomarker page listing a project as an implementer
  requires that project's page to name the biomarker, in the same commit — and the same for the
  models a biomarker's inputs come from. Disagreement between catalogues is a bug in the atlas.

## 4. The summary table

`docs/BIOMARKERS.md` groups biomarkers by family — calibre, tortuosity, density and complexity,
junctions and angles, other — in that order. Within each family, order alphabetically. The columns
are:

| Column | Content |
| --- | --- |
| Biomarker | Name, linked to `biomarkers/<slug>.md` |
| What it measures | One short phrase, in plain language |
| Inputs | The segmentations it needs (vessels, A/V, disc, fovea) |
| Region | Whole image, a named zone, or `varies` |
| Units | As computed, and `scale-invariant` where it applies |
| Variants | How many competing definitions, e.g. `3 (arc-chord, curvature, inflections)` |
| Computed by | Catalogued projects that implement it |
| Defined in | Short citation of the definition of record |
| Last checked | Date from the detail page |

Keep every cell short. When a detail page changes, update its row in the same commit.
