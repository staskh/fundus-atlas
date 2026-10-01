---
name: document-biomarker
description: Catalogue a retinal vascular biomarker — one measurement computed from fundus segmentations, such as vessel calibre, CRAE, tortuosity or fractal dimension — by adding it to one of the five family pages in docs/biomarkers/ and to the docs/BIOMARKER-NAMES.md vocabulary. Use when adding, updating, or reviewing a biomarker entry in Fundus Atlas.
---

# Documenting a biomarker

A **biomarker** here means one measurement derived from a colour-fundus photograph's segmentations:
a number a researcher would put in a spreadsheet column. The network that produced the mask is a
**model** (`document-model`); the software that runs models and biomarkers end to end is a
**project** (`document-project`).

**The reason this catalogue exists:** a biomarker name is not a definition. "Tortuosity" names
eleven formulas here, "CRAE" two, and "vessel density" differs by what counts as the denominator.
Papers report the name and omit the choice. The catalogue's job is to make the choices visible, so
that two numbers carrying the same label can be told apart.

## 1. There are five families, and you are almost certainly adding to one

**The page is the family, not the biomarker.** `docs/biomarkers/` holds exactly five:

| Family | What belongs in it |
| --- | --- |
| [`calibre`](../../../docs/biomarkers/calibre.md) | vessel width, and anything built from widths — the central retinal equivalents, the arteriovenous ratios |
| [`tortuosity`](../../../docs/biomarkers/tortuosity.md) | the shape of a vessel's path: Hart's seven, Grisan's density, inflection counts, curvature on a fitted spline |
| [`density`](../../../docs/biomarkers/density.md) | how much vasculature there is and how it is spread: area, length, the densities, sparsity, the fractal dimensions |
| [`topology`](../../../docs/biomarkers/topology.md) | the network as a graph: junctions, endpoints, components, branching and temporal angles |
| [`landmarks`](../../../docs/biomarkers/landmarks.md) | the optic nerve head and the fovea — the only family that measures no vessel |

**Adding a sixth family needs Stas's agreement**, and the bar is that the measurement answers a
question none of the five asks. A new *variant* of tortuosity is a row on the tortuosity page; a new
*way of pooling* is a statistic, not a biomarker; a new *region* is a row on the regions page.

**Two pages there are not families and take no biomarkers:**
[`vessel-tracing`](../../../docs/biomarkers/vessel-tracing.md) and
[`regions-of-interest`](../../../docs/biomarkers/regions-of-interest.md). They are catalogued because
several biomarkers cannot be read without them.

## 2. What you produce

1. **An entry in `src/biomarkers/canonical.py`**, which is what `check()` gates on and what every
   generated table is rendered from. Prose without a name is a page nothing can be measured
   against, so this comes first.
2. **A row in the family page's canonical-names table**, plus a `### 3.x` variant subsection if the
   biomarker is a competing definition of something already there.
3. **A row in [`docs/BIOMARKER-NAMES.md`](../../../docs/BIOMARKER-NAMES.md)** §3, under its family,
   with the ✅ / ⚠️ coverage marks of §5 below. That section is hand-written because the marks are
   judgements; a test checks its left-hand column against the vocabulary in **both** directions, so
   a biomarker with no row fails just as loudly as a row with no biomarker.
4. **`python -m biomarkers.pages`**, which refreshes the generated blocks in
   `docs/BIOMARKERS.md` and `docs/BIOMARKER-NAMES.md` §2 — the family counts, the units, the
   statistics each biomarker admits. Never type those by hand; §8.8.

Then `python -m benchmarks --benchmark biomarker-synthetic --docs`, which regenerates the
benchmark's own vocabulary table from the same record.

## 3. The canonical name

```
family / biomarker / structure / [roi] / [statistic]
```

| Part | Meaning | Default |
| --- | --- | --- |
| `family` | one of the five above | required |
| `biomarker` | **which definition**, because the family name does not say | required |
| `structure` | `artery`, `vein`, `vessels`, or `both` for an inherent ratio | required where the family has one |
| `roi` | the region, from [regions of interest](../../../docs/biomarkers/regions-of-interest.md) | `fov` |
| `statistic` | how per-segment or per-vessel values were pooled | `median` |

Four rules, each of which has already been got wrong here at least once:

- **3.1 A statistic is never part of the biomarker name.** `mean-width` and `median-width` are one
  biomarker, `calibre/width`, pooled two ways. Writing the statistic into the biomarker is how a
  catalogue ends up with three names for one measurement.
- **3.2 A family may override the defaults**, and says so on its page. `calibre`'s equivalents
  *require* a region — there is no field-of-view-wide CRAE. `landmarks` has no structure at all.
- **3.3 Where the same quantity can be measured over a segment or a whole vessel, those are two
  biomarkers**, and the whole-vessel one takes the `vessel-` prefix. A vessel is **root-to-tip**
  from the optic disc, so the `vessel-` forms require a disc. They pool different populations.
- **3.4 Where a family has both optional parts, their vocabularies must be disjoint** — a region
  named `mean` would make every four-part name ambiguous, silently. `check()` enforces it.

## 4. Required sections of a family page

1. **What it measures** — plain language, for a clinician. What the numbers describe about the eye
   and what they have been associated with. No formulas.
2. **The canonical names** — the table of every biomarker in the family, with its units and which
   statistics apply. Plus the family's overrides per 3.2, and its `vessel-` forms per 3.3.
3. **Definitions of record** — the paper each biomarker traces to, linked to `docs/papers/` where
   one exists. **A paper is not mandatory**; see 6.
4. **Inputs required** — which segmentations, and what geometry is derived from them. Most
   disagreement between implementations of one formula comes from this step, not the formula.
5. **Measurement region** — the default, which families require one, and the conventions
   implementations actually use.
6. **Units and scale dependence** — see 5 below. Say explicitly whether each biomarker survives a
   change of camera, and whether it survives a change of field of view, which is a different
   question.
7. **Implementations** — one row per catalogued project, with the source file and **the lineage**.
   Shared code means correlated errors, so agreement between a project and its fork is not evidence.
8. **Sensitivity and failure modes** — what moves the number for reasons unrelated to the eye.
9. **Known defects** — one bullet per defect with its evidence and date, or `None recorded as of
   <date>` — an absence of findings, not a clean bill of health.

## 5. Units: microns, never pixels

**A canonical biomarker is never expressed in pixels.** Lengths in µm, areas in µm², curvature in
1/µm, and `1` is a unit rather than a blank.

This is not a preference. Thirty of the seventy names this catalogue held before the rule gave a
different answer for the same eye at a different resolution, and Hubbard's equivalents came out in
microns while Knudtson's came out in pixels — two variants of one biomarker, incomparable.

An implementation reporting pixels has its output converted **by its adapter**, using the store's
scale. An implementation applying micron-fitted constants to pixel widths is **wrong**, and the
benchmark reports what it returned rather than repairing it. Those two cases look alike and are not,
and the mapping must say which it is.

**For the curvature family, the estimator is part of the measurement.** Swapping a boxcar for a
spline moves τ3 by a factor of eighteen, and a smoothing scale fixed in pixels fails across
resolutions. An entry there records the estimator and how its scale is set; a scale without its
estimator records nothing.

## 6. A defining paper is not mandatory, and the substitute is heavier

Some real measurements have no single origin — vascular density and the cup-to-disc ratio are
clinical practice rather than somebody's proposal. Demanding a citation would block them or invite
a dishonest one.

**Where there is no paper, write the formula out**: what it is computed over, the conventions it
assumes, and optionally a pointer to an open-source implementation as a worked example. A reader
following a DOI gets the authors' account; a reader following this gets ours, which had better be
good enough to implement from. **An implementation is a pointer, never the definition** — code
changes and the entry must not.

**Keep a name nothing implements** where a paper names or recommends it. Hart's τ4 and τ5 are in his
table whether or not anybody computes them. A name no paper asks for and no implementation computes
is clutter, and goes.

## 7. Marking coverage in BIOMARKER-NAMES.md

| Mark | Means |
| --- | --- |
| ✅ | the project implements this and we believe its number is **comparable** |
| ⚠️ | it computes something close that is **not interchangeable** — and the note says why: a different region, a different unit, or a formula differing where it matters |
| blank | it does not compute it |

**Both marks are claims.** A mapping says *we believe this column computes this quantity*, read out
of the source rather than the documentation — and this catalogue has been wrong three times and
withdrawn the mapping each time. The [synthetic benchmark](../../../docs/benchmarks/biomarker-synthetic-docs.md)
is what tests a claim; a shape where two variants give different known values separates them.

**A withdrawn mapping is a finding.** Record it in §5 of that file with its date and the evidence,
and keep the column under the implementation's own name in §4. Never delete the measurement.

## 8. Rules that apply to every entry

- **8.1 Reference, never redistribute.** Link to publications and implementations at their source.
- **8.2 Separate claim from observation.** A paper's reported reproducibility is its authors' claim.
  This repository's measurements are labelled as ours, with a date.
- **8.3 Write for a non-engineer.** Section 1 must be readable by someone who will never open the
  code. Formulas belong in sections 2 and 3, stated in words before symbols.
- **8.4 Number every heading.**
- **8.5 Never present one variant as *the* definition** because it is the most common.
- **8.6 Date what you checked**, at the foot of the page.
- **8.7 Keep the catalogues consistent.** A family page naming a project as an implementer requires
  that project's page to name the biomarker, in the same commit — and the same for a definition
  paper that has a page under `docs/papers/`.
- **8.8 Never hand-edit a generated block.** Three pages carry them, all rendered from
  `canonical.py`: `docs/benchmarks/*-docs.md`, `docs/BIOMARKERS.md` §1 and
  `docs/BIOMARKER-NAMES.md` §2. Everything between `<!-- generated: … -->` and `<!-- /generated -->`
  is replaced on the next run, and a test fails meanwhile. Change the record and regenerate.

  *Why there is a generator at all.* Grisan's tortuosity density was declared dimensionless in a
  vocabulary table for a week while its own derivation, two sections below on the same page, gave
  it as an inverse length. Nothing caught it until the units became physical and one shape
  disagreed with itself across two resolutions. A unit is a fact the record holds; a table that
  restates a fact is a table that can contradict it.
- **8.9 A unit is never pixels.** A length is in microns, an area in µm², a curvature in 1/µm.
  `PLAN-BIOMARKER.md` §2.2 is the decision and
  `test_one_retina_photographed_at_two_resolutions_gives_one_set_of_numbers` is what holds it: the
  same retina at 1024/10 µm and 2048/5 µm must settle every name to the same number.
