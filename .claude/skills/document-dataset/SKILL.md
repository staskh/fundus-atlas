---
name: document-dataset
description: Catalogue a colour-fundus dataset — the images, their camera and resolution, what is annotated, which other dataset's photographs it reuses, its licence and whether it can be downloaded directly — as a page in docs/datasets/ plus a row in the docs/DATASETS.md summary table. Use when adding, updating, or reviewing a dataset entry in Fundus Atlas.
---

# Documenting a dataset

A **dataset** here means a published collection of colour-fundus photographs, with or without
annotations, that someone can obtain and use. The networks trained on it are **models**
(`document-model`), the software that runs them is a **project** (`document-project`), and the
numbers computed from them are **biomarkers** (`document-biomarker`).

Datasets are where this atlas's other three catalogues bottom out. Every model page names the
datasets it trained on; every comparison depends on whether a test set was one of them. So a dataset
page answers three questions the other catalogues cannot: **may I use these images**, **what do the
pixels actually represent**, and **are these photographs already somewhere else in the catalogue
under a different name**.

## 1. What you produce

Every dataset produces exactly two things:

1. **A detail page**, `docs/datasets/<slug>.md`, following `template.md` in this skill directory.
   The slug is the dataset's published name, lowercased, spaces and punctuation replaced by hyphens
   (`RIM-ONE DL` becomes `rim-one-dl.md`, `Chákṣu` becomes `chaksu.md`).
2. **A row in `docs/DATASETS.md`**, the summary table, linking to that detail page.

One page per published dataset. An add-on that annotates another dataset's photographs without
adding images of its own — an artery/vein reference standard drawn on someone else's images, say —
goes **on that dataset's page** as an annotation layer, not on a page of its own, with the
inheritance recorded per section 2.5.

## 2. Required sections of the detail page

Use `template.md` verbatim and keep its section numbering.

1. **What it is** — in plain language: how many photographs, of whom, why the collection was made,
   and what it is used for. A clinician should be able to read this section alone.
2. **Original publication** — the paper that describes the dataset, with a full citation and a DOI or
   other stable link. **This is required for every entry**: a dataset without a describing
   publication is a download, and the page must say so explicitly rather than leave the field blank.

   **Where a dataset's annotations come from several groups, give sections 2, 3 and 4 one subsection
   per layer** — 2.1, 2.2, 2.3 and so on — because a layer added by another institution has its own
   paper, its own download and, often, its own licence. HRF is the worked example: one set of 45
   photographs, with the vessel gold standard and disc centres from the original authors, an
   artery/vein standard from a second group and disc-and-cup contours from a third. Presenting that
   as one citation, one link and one licence would be wrong three times over. Name the layer in each
   subsection heading, state which annotations it supplies, and say plainly when a layer's licence
   is unknown or differs from the images'.
3. **Access** — the home page; whether the data can be downloaded **directly** or requires
   registration, a signed agreement, or an email request; the direct URL when one exists; and the
   form it arrives in. The summary table carries a direct-link column, so this determination must be
   made for every entry, not skipped.
4. **Licence** — as stated by the distributor, quoted or named exactly. **Always attempt to
   establish it**, and where it cannot be established say so in those words rather than implying
   permissiveness. Record separately when the **images** and the **annotations** carry different
   terms, which is common where a second group annotated someone else's photographs, and when a
   challenge's terms restrict use to the challenge.
5. **The images** — the physical facts about the pixels. **Where a dataset has well-defined
   subcollections — different cameras, different acquisition sites, a challenge's separate training
   and test releases, or an ultra-wide split alongside a standard one — repeat this section once per
   subcollection** (5.1, 5.2, …), naming each and giving its image count. Do not flatten them into
   a single row of ranges: a reader needs to know which camera produced which photographs, and a
   mixed-resolution dataset averaged into one line cannot be matched against a model's grid. The
   facts to record, per subcollection:
   - **Count**, and how it splits by class or by acquisition site.
   - **Resolution in pixels**, every distinct size present. Where a dataset mixes sizes, list them;
     do not average.
   - **Microns per pixel**, where the dataset or its paper publishes it, or the information needed
     to derive it. This is the only route from a pixel measurement to a physical one, so record it
     when available and record `Unknown` when not — most datasets do not publish it.
   - **Camera and equipment** — the make and model, and the acquisition site where stated.
   - **Field of view** in degrees. A 30°, 45° and 200° photograph of the same eye contain different
     proportions of central and peripheral retina, so this decides which datasets can be pooled.
   - **Centring** — disc-centred, macula-centred, or mixed.
   - **Modality**, where it is not colour fundus photography: scanning laser ophthalmoscopy,
     infrared reflectance and ultra-wide-field images look like fundus photographs in a file
     browser and are not interchangeable with them. Say so prominently.
6. **Annotations** — what is labelled, by how many readers, and whether readers are kept separate or
   merged. Record **the resolution the labels were drawn at** when it differs from the images'
   own — a mask drawn on a downsized rendition does not carry the detail its dimensions suggest.
7. **Inheritance** — required, and in both directions:
   - **Images this dataset reuses** from another, naming the source dataset and how many, and
     **whether they were resized** — a resized copy is a different set of pixels, and a model
     evaluated on the copy has not been evaluated on the original.
   - **Datasets that reuse these images**, so a reader arriving from either side sees the link.
   - Where neither applies, state `No shared images established` rather than leaving it empty.
   The reason this section exists: two datasets built on the same photographs are not two cameras'
   worth of evidence, and scoring both looks like independent confirmation when it is not.
8. **Use as a benchmark** — which catalogued models trained on these images, linking to their pages,
   so a reader can tell at a glance whether a score on this dataset is in-sample. Note also where a
   dataset's own native resolution is **below the grid** a model measures on, since a score there is
   not comparable with a score on a larger dataset.
9. **Known defects** — errors and traps in the distribution itself: mislabelled files, archives whose
   contents do not match their documentation, counts that differ from the paper, annotations that
   disagree with their own description. Same rules as the other skills: record it where it lives,
   attribute a claimed fix, and write `None recorded` with the date when nothing is known.

A section that does not apply stays in the page, marked `Not applicable` with a short reason. A
section whose answer could not be established is marked `Unknown` — never filled with a guess, and
never softened into a maybe.

## 3. Rules that apply to every entry

- **3.1 Reference, never redistribute.** Link to the distributor. Never copy images, annotations or
  archives into this repository, and never mirror a dataset that requires registration (see
  `CLAUDE.md` §2).
- **3.2 Each dataset keeps its own licence.** Record it as written; never restate it as more
  permissive; never imply that a public download implies permission to redistribute or to use
  commercially.
- **3.3 Separate claim from observation.** Counts and properties as published are the authors'
  statements; where this repository has checked an archive and found something different, label that
  as our finding and put it in section 9.
- **3.4 Write for a non-engineer.** Section 1 must not require knowing what a mask is.
- **3.5 Number every heading**, as the template does.
- **3.6 Date what you checked** at the bottom of the page — licences and download routes change more
  often than the data.
- **3.7 Keep the catalogues consistent.** A dataset page naming a model that trained on it requires
  that model's page to name the dataset, in the same commit, and inheritance must be recorded on
  both datasets' pages.

## 4. The summary table

`docs/DATASETS.md` holds one row per dataset, sorted by image count with the largest first. The
columns are:

| Column | Content |
| --- | --- |
| Dataset | Name, linked to `datasets/<slug>.md` |
| Images | Count |
| Resolution | Pixel dimensions; `mixed` plus the range where a dataset has several |
| Year | Publication year of the describing paper |
| Quality | ✅ where the photograph itself is graded, with the scale in a word |
| Vessels | ✅ where a vessel segmentation is provided |
| A/V | ✅ where arteries and veins are distinguished |
| Disc | ✅ where the optic disc is annotated |
| Cup | ✅ where the optic cup is annotated |
| Disease | ✅ and the grading, where eyes are graded for disease |
| Other labels | Anything else of use — fovea, lesions, demographics, published biomarker values, junctions |
| Licence | As stated, or `not stated` |
| Last checked | Date from the detail page |

Use `—` for an annotation a dataset does not carry, and add a reader count in the cell where more
than one person annotated (`✅ ×5 experts`) — a dataset with several readers is the only kind that
can measure human agreement rather than assume it.

The camera, field of view, microns per pixel, access route, describing paper and inheritance are
**not** table columns: they are per-subcollection or per-layer facts that a single cell would
misrepresent, and they live on the detail pages. Two conventions do belong in the table. **Mark
modalities that are not colour fundus photography in the Dataset cell**, so nobody pools them by
accident. And where a dataset's photographs come from another dataset, say so in the Dataset cell
too, briefly — section 2 of `DATASETS.md` carries the full map in both directions.
