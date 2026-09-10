# Datasets

Published collections of colour-fundus photographs. Each row links to a detail page recording what
the images are — camera, resolution, field of view, microns per pixel where anyone published it —
what is annotated and by how many readers, whose photographs the collection reuses, its licence, and
whether it can be downloaded directly.

Three things about this catalogue are worth reading before the table.

**Every licence is different, and several are not stated at all.** A public download is not
permission to redistribute or to use commercially. The Licence column records what the distributor
says; the detail pages record where images and annotations carry different terms.

**Several of these datasets are the same photographs.** One dataset's images annotated by another
group is one camera's worth of evidence, not two. Section 2 maps that in both directions, including
where the reused copies were resized — a resized copy is a different set of pixels.

**A dataset a model trained on cannot measure that model.** Each detail page names the catalogued
models trained on its images, so a score can be read as in-sample or held out. That single fact
decides what any comparison in [MODELS.md](MODELS.md) is worth.

## 1. Summary

Sorted by image count, largest first.

| Dataset | Images | Resolution | Year | Quality | Vessels | A/V | Disc | Cup | Disease | Other labels | Licence | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [REFUGE / REFUGE2](datasets/refuge.md) | 1,200 / 2,000 | mixed — 2124×2056, 1634×1634, + | 2020 | — | — | — | ✅ consensus | ✅ consensus | ✅ glaucoma | fovea coordinate | research and educational, challenge terms | 2026-09-11 |
| [G1020](datasets/g1020.md) | 1,020 | mixed — **41 sizes**, 1944×2108 to 2426×3007 | 2020 | — | — | — | ✅ | ✅ (791 of 1,020) | ✅ glaucoma 296 / normal 724 | vertical CDR, ISNT rim widths, disc box | research only, no standard grant | 2026-09-11 |
| [FIVES](datasets/fives.md) | 800 | 2048×2048 | 2022 | ✅ illumination / blur / contrast | ✅ consensus | — | — | — | ✅ AMD / DR / glaucoma / normal | — | **CC BY 4.0** | 2026-09-11 |
| [ORIGA](datasets/origa.md) | 650 | 2048 tall, 2426–2616 wide | 2010 | — | — | — | ✅ | ✅ | ✅ glaucoma 168 / normal 482 | **published expert CDR**, eye side | research use, request-based | 2026-09-11 |
| [REYIA](datasets/reyia.md) *(compiled from nine datasets)* | 589 | mixed, by source | 2025 | — | — | ✅ | — | — | mixed, by source | per-image source attribution | MIT on the compilation; **sources stricter** | 2026-09-11 |
| [PAPILA](datasets/papila.md) | 488 | 2576×1934 | 2022 | — | — | — | ✅ ×2 experts | ✅ ×2 experts | ✅ healthy / suspect / glaucoma | full clinical record per eye | GPL-3.0 or later | 2026-09-11 |
| [Leuven-Haifa (UZLF)](datasets/leuven-haifa.md) | 240 | 1444×1444 | 2024 | ✅ automated score | — | ✅ **×2 readers** (junior + senior correction) | — | — | ✅ glaucoma, three categories | age, sex, **12 published vessel measurements** | custom, **non-commercial**, signed agreement | 2026-09-11 |
| [AVRDB](datasets/avrdb.md) | 100 | 1504×1000 | 2020 | — | ✅ | ✅ | ✅ optic nerve head | — | ✅ hypertensive retinopathy, papilloedema | **published AVR per image**, exudates, cotton-wool spots | **CC BY 4.0** | 2026-09-11 |
| [Fundus-AVSeg](datasets/fundus-avseg.md) | 100 | 2656×1992 (21), 1280×1280 (79) | 2025 | ✅ high / low | ✅ derived from A/V | ✅ | — | — | ✅ four classes | eye side | **CC BY 4.0** | 2026-09-11 |
| [GAVE](datasets/gave.md) | 50 | 1536×1024 | 2025 | — | ✅ | ✅ | — | — | — | — | **CC BY 4.0** | 2026-09-11 |
| [HRF](datasets/hrf.md) *(three annotation layers)* | 45 | 3504×2336 | 2013 | — | ✅ | ✅ via HRF-AV | ✅ centres ×2 experts; contours via HRF-Seg+ | ✅ via HRF-Seg+ (40 of 45) | ✅ healthy / glaucoma / DR | field-of-view masks | CC BY 4.0 images; **layers vary, one unknown** | 2026-09-11 |
| [RITE](datasets/rite.md) *(= DRIVE's images)* | 40 | 565×584 | 2013 | — | ✅ (differs from DRIVE's) | ✅ | — | — | — | overlap and uncertain vessel classes | research use, citation required | 2026-09-11 |
| [DRIVE](datasets/drive.md) | 40 | 565×584 | 2004 | — | ✅ + **second observer** on the test split | — | — | — | ✅ 7 of 40 with mild DR | field-of-view masks | research use, registration terms | 2026-09-11 |
| [LES-AV](datasets/les-av.md) | 22 | 1444×1620 (21), 1958×2196 (1) | 2018 | — | ✅ derived from A/V | ✅ | — | — | ✅ **glaucoma subtypes** | blood pressure, heart rate, IOP | research only, **no commercial use** | 2026-09-11 |

## 2. Shared photographs

Two datasets built on the same photographs are one camera's worth of evidence. This section maps
that in both directions; each detail page repeats its own half of the link.

| | |
| --- | --- |
| **[DRIVE](datasets/drive.md) → [RITE](datasets/rite.md)** | **RITE *is* DRIVE** — the same 40 photographs, unresized, with an artery/vein reference standard added by a different group at a different institution. It is widely cited as "DRIVE-AV", so a training list naming DRIVE and DRIVE-AV separately has one set of images. Their *vessel* annotations differ, though: RITE's training split is a modified version of DRIVE's first observer and its test split follows DRIVE's second, so a Dice against one is not a Dice against the other. |
| **[HRF](datasets/hrf.md) ← HRF-AV, HRF-Seg+** | One set of 45 photographs annotated by three groups: the original vessel gold standard and two experts' disc centres, an artery/vein standard from a second group, and disc-and-cup contours from a third. Three papers, three downloads, three licence positions — catalogued as one dataset with three layers. |
| **[REFUGE](datasets/refuge.md) ⊃ REFUGE** | REFUGE2's 2,000 photographs **contain** the first edition's 1,200, of which 800 are the AutoMorph family's disc/cup training data. A number quoted on REFUGE2 is therefore partly in-sample and partly not, and pooling the editions hides which. |
| **[REYIA](datasets/reyia.md) ← nine datasets** | A compilation: 478 of its 589 photographs come from [FIVES](datasets/fives.md) (75), [PAPILA](datasets/papila.md) (78), MESSIDOR, Magrabia, mBRSET, GRAPE, TREND and AV-WIDE; only its 111-image ENRICH set is new. Every row carries its source, which is what makes the overlap traceable. |
| **[G1020](datasets/g1020.md), [ORIGA](datasets/origa.md), REFUGE** | Distributed together in one third-party Kaggle bundle. That is packaging, not shared photographs — the three are separate collections, and the bundle's licence field is the uploader's, not any depositor's. |

## 3. Not colour fundus photography

_No entries yet._ — scanning laser ophthalmoscopy, infrared reflectance and ultra-wide-field
collections look like fundus datasets in a file browser and cannot be pooled with them.

## 4. How to read this table

- **Resolution** — every distinct size present; `mixed` where a dataset spans several, with the
  per-subcollection detail on its page. Compare it against the grid each model measures on, in
  [MODELS.md](MODELS.md): a dataset below that grid is upsampled before measurement, which flatters
  a segmentation score, and one far above it is downsampled, which destroys thin vessels.
- **Year** — the publication year of the describing paper, which is the quickest guide to what
  camera generation and what annotation conventions to expect.
- **The annotation columns** — quality, vessels, A/V, disc, cup — carry ✅ where the dataset supplies
  that label and `—` where it does not, with a reader count where more than one person annotated
  (`✅ ×5 experts`). **A reader count above one is the most useful property a dataset can have**: it
  is what lets a human agreement ceiling be measured rather than assumed.
- **Quality** grades the *photograph*; **Disease** grades the *eye*, and the schemes are not
  interchangeable between datasets — four classes here, three there, a glaucoma triple including
  "suspect" elsewhere. The cell names the scheme; the page explains it.
- **Other labels** — fovea locations, lesion classes, demographics, published biomarker values,
  vessel junctions. This is where the unusual and most valuable content hides.
- **Not in this table, on the detail pages instead:** camera and field of view, microns per pixel,
  the download route and whether a direct link exists, the describing paper, and inheritance. Each
  of those is a per-subcollection or per-annotation-layer fact that one cell would misrepresent —
  a dataset annotated by three institutions has three papers, three downloads and possibly three
  licences.
- **Known defects** are not in this table either. Every detail page carries a section 9 for errors
  in the distribution itself — mislabelled files, counts that disagree with the paper, annotations
  that do not match their own description.

## 5. Adding a dataset

Dataset pages follow a fixed structure so they can be read against each other. Load the
`document-dataset` skill, which defines that structure and this table's columns, before adding or
changing an entry.
