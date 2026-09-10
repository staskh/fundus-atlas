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
| [EyeQ](datasets/eyeq.md) *(quality labels over EyePACS photographs)* | 28,792 | **highly mixed** — many devices | 2019 | ✅ Good / Usable / Reject | — | — | — | — | ✅ DR 0–4, from EyePACS | — | labels **not stated**; images under EyePACS competition terms | 2026-09-11 |
| [BRSET](datasets/brset.md) | 16,266 | mixed | 2024 | ✅ focus / illumination / field / artefacts | — | — | — | — | ✅ multi-label + DR grades | anatomical flags, **demographics** | PhysioNet credentialed licence + DUA | 2026-09-11 |
| [mBRSET](datasets/mbrset.md) *(handheld companion to BRSET)* | 5,164 | mixed, handheld | 2024 | ✅ | — | — | — | — | ✅ DR | demographics | PhysioNet credentialed licence + DUA | 2026-09-11 |
| [DeepDRiD](datasets/deepdrid.md) *(+ ultra-wide split)* | ~2,256 | mixed; **dual view per eye** | 2020 | ✅ ×3 readers, + artefact / clarity / field | — | — | — | — | ✅ DR, per image and per patient | dual-view pairing | **CC BY-SA 4.0** — share-alike | 2026-09-11 |
| [FQS](datasets/fqs.md) | 2,246 | 1024×1024 (**authors' resize**) | 2025 | ✅ **continuous 0–100** + Good / Usable / Reject | — | — | — | — | — | — | paper CC BY 4.0; check the record | 2026-09-11 |
| [Chákṣu](datasets/chaksu.md) | 1,345 | 2448×3264 **portrait**, 2048×1536, 1920×1440 | 2023 | — | — | — | ✅ **×5 experts** | ✅ **×5 experts** | ✅ glaucoma, **×5 independent decisions** | three cameras incl. handheld | **CC BY 4.0** | 2026-09-11 |
| [MSHF](datasets/mshf.md) *(three device classes, incl. 200° UWF)* | 1,302 | mixed by device | 2023 | ✅ **×3 readers**, illumination / clarity / contrast / overall | — | — | — | — | ✅ DR, glaucoma, healthy | camera class per image | **CC BY 4.0** | 2026-09-11 |
| [REFUGE / REFUGE2](datasets/refuge.md) | 1,200 / 2,000 | mixed — 2124×2056, 1634×1634, + | 2020 | — | — | — | ✅ consensus | ✅ consensus | ✅ glaucoma | fovea coordinate | research and educational, challenge terms | 2026-09-11 |
| [MESSIDOR](datasets/messidor.md) | 1,200 | 1440×960, 2240×1488, 2304×1536 | 2014 | — | — | — | — | — | ✅ DR 0–3 and macular-oedema risk 0–2 | — | research and educational use, ADCIS agreement | 2026-09-11 |
| [G1020](datasets/g1020.md) | 1,020 | mixed — **41 sizes**, 1944×2108 to 2426×3007 | 2020 | — | — | — | ✅ | ✅ (791 of 1,020) | ✅ glaucoma 296 / normal 724 | vertical CDR, ISNT rim widths, disc box | research only, no standard grant | 2026-09-11 |
| [FIVES](datasets/fives.md) | 800 | 2048×2048 | 2022 | ✅ illumination / blur / contrast | ✅ consensus | — | — | — | ✅ AMD / DR / glaucoma / normal | — | **CC BY 4.0** | 2026-09-11 |
| [RIGA](datasets/riga.md) *(460 images are MESSIDOR's)* | 750 | mixed — three sources | 2018 | — | — | — | ✅ **×6 ophthalmologists** | ✅ **×6 ophthalmologists** | — | each annotator's CDR; RIGA+ domain splits | **CC BY-NC 4.0** | 2026-09-11 |
| [ORIGA](datasets/origa.md) | 650 | 2048 tall, 2426–2616 wide | 2010 | — | — | — | ✅ | ✅ | ✅ glaucoma 168 / normal 482 | **published expert CDR**, eye side | research use, request-based | 2026-09-11 |
| [GRAPE](datasets/grape.md) | 631 | full frames; **contours on an ROI crop** | 2023 | — | — | — | ✅ | ✅ | ✅ glaucoma, **longitudinal** | visual fields, OCT, IOP, visit dates | **CC BY 4.0** | 2026-09-11 |
| [REYIA](datasets/reyia.md) *(compiled from nine datasets)* | 589 | mixed, by source | 2025 | — | — | ✅ | — | — | mixed, by source | per-image source attribution | MIT on the compilation; **sources stricter** | 2026-09-11 |
| [IDRiD](datasets/idrid.md) | 516 | 4288×2848 | 2018 | — | — | — | ✅ (81 of 516) | — | ✅ DR 0–4 and macular oedema 0–2 | four lesion classes, fovea | **CC BY 4.0** | 2026-09-11 |
| [PAPILA](datasets/papila.md) | 488 | 2576×1934 | 2022 | — | — | — | ✅ ×2 experts | ✅ ×2 experts | ✅ healthy / suspect / glaucoma | full clinical record per eye | GPL-3.0 or later | 2026-09-11 |
| [RIM-ONE DL](datasets/rim-one-dl.md) *(unifies RIM-ONE r1–r3)* | 485 | not stated by the distributor | 2020 | — | — | — | ✅ | ✅ | ✅ normal 313 / glaucoma 172 | **hospital-based split** | research and educational use | 2026-09-11 |
| [GAMMA](datasets/gamma.md) *(fundus paired with OCT)* | 300 pairs, ~100 labelled | mixed | 2023 | — | — | — | ✅ | ✅ | ✅ normal / early / progressive glaucoma | fovea, paired OCT volume | challenge terms, research use | 2026-09-11 |
| [FunPiQ](datasets/funpiq.md) *(sampled from EyeQ, BRSET, mBRSET)* | 300 | mixed, by source | 2026 | ✅ **pixel-level** degraded-region masks | — | — | — | — | — | — | annotations per Zenodo record; **images inherit PhysioNet terms** | 2026-09-11 |
| [Leuven-Haifa (UZLF)](datasets/leuven-haifa.md) | 240 | 1444×1444 | 2024 | ✅ automated score | — | ✅ **×2 readers** (junior + senior correction) | — | — | ✅ glaucoma, three categories | age, sex, **12 published vessel measurements** | custom, **non-commercial**, signed agreement | 2026-09-11 |
| [RAV](datasets/rav.md) | 206 | 1024×1024 (**authors' crop and resize**) | 2025 | ✅ mixed by design | — | ✅ | — | — | — | Rotterdam Study population cohort | **CC BY-NC 4.0 per the README; CC0 per the record — contradictory** | 2026-09-11 |
| [UoA-DR](datasets/uoa-dr.md) | 200 | 2124×2056 | — | — | ✅ | — | ✅ boundary **and centre** | — | ✅ DR severity | **fovea centre** | custom signed agreement | 2026-09-11 |
| [MAPLES-DR](datasets/maples-dr.md) *(MESSIDOR's images)* | 198 | MESSIDOR natives; **labels drawn at 1500×1500** | 2024 | — | ✅ | — | ✅ | ✅ (192 of 198) | ✅ regraded DR and macular oedema | six lesion classes, macula | **CC BY 4.0** labels; images research-only | 2026-09-11 |
| [Drishti-GS](datasets/drishti-gs.md) | 101 | ~2896×1944 | 2015 | — | — | — | ✅ ×4 experts, **soft maps** | ✅ ×4 experts, soft maps | ✅ glaucoma | CDR, notching | "free to use" — not a standard licence | 2026-09-11 |
| [AVRDB](datasets/avrdb.md) | 100 | 1504×1000 | 2020 | — | ✅ | ✅ | ✅ optic nerve head | — | ✅ hypertensive retinopathy, papilloedema | **published AVR per image**, exudates, cotton-wool spots | **CC BY 4.0** | 2026-09-11 |
| [Fundus-AVSeg](datasets/fundus-avseg.md) | 100 | 2656×1992 (21), 1280×1280 (79) | 2025 | ✅ high / low | ✅ derived from A/V | ✅ | — | — | ✅ four classes | eye side | **CC BY 4.0** | 2026-09-11 |
| [RETA](datasets/reta.md) *(IDRiD's images, resized)* | 81 — **54 masks public** | 1024×1024 | 2022 | — | ✅ | — | — | — | — | inter- and intra-annotator disambiguation record | **CC BY 4.0** | 2026-09-11 |
| [FOVEA](datasets/fovea-dataset.md) *(pre- and intraoperative pairs)* | 80 (40 eyes ×2) | 1934×1960 and 1080×1920 | 2025 | — | ✅ **×2 readers** | — | ✅ **×2 readers** | — | — | paired preoperative / surgical-microscope views | **CC BY-NC-ND 4.0** — no derivatives | 2026-09-11 |
| [VICAVR](datasets/vicavr.md) | 58 | 768×584 | — | — | — | ✅ **×3 experts** | — | — | — | **published calibres at several radii** | research use, no standard licence | 2026-09-11 |
| [GAVE](datasets/gave.md) | 50 | 1536×1024 | 2025 | — | ✅ | ✅ | — | — | — | — | **CC BY 4.0** | 2026-09-11 |
| [HRF](datasets/hrf.md) *(three annotation layers)* | 45 | 3504×2336 | 2013 | — | ✅ | ✅ via HRF-AV | ✅ centres ×2 experts; contours via HRF-Seg+ | ✅ via HRF-Seg+ (40 of 45) | ✅ healthy / glaucoma / DR | field-of-view masks | CC BY 4.0 images; **layers vary, one unknown** | 2026-09-11 |
| [RITE](datasets/rite.md) *(= DRIVE's images)* | 40 | 565×584 | 2013 | — | ✅ (differs from DRIVE's) | ✅ | — | — | — | overlap and uncertain vessel classes | research use, citation required | 2026-09-11 |
| [DRIVE](datasets/drive.md) | 40 | 565×584 | 2004 | — | ✅ + **second observer** on the test split | — | — | — | ✅ 7 of 40 with mild DR | field-of-view masks | research use, registration terms | 2026-09-11 |
| [INSPIRE-AVR](datasets/inspire-avr.md) | 40 | 2392×2048 | 2011 | — | ✅ | AVR only, ×2 experts | ✅ | — | — | **published AVR per image** (IVAN) | research use; **redistribution prohibited** | 2026-09-11 |
| [RAVIR](datasets/ravir.md) **(infrared reflectance, not colour fundus)** | 36 | 768×768 | 2022 | — | — | ✅ | — | — | ✅ DR, hypertensive retinopathy | test masks withheld | usage protocol, not a standard grant | 2026-09-11 |
| [IOSTAR](datasets/iostar.md) **(scanning laser ophthalmoscopy, not colour fundus)** | 30 | 1024×1024 | 2016 | — | ✅ | ✅ | ✅ | — | — | **vessel junctions** — bifurcations and crossovers | research use | 2026-09-11 |
| [DualModal2019](datasets/dualmodal2019.md) *(dual-modal pairs)* | 30 | 1024×1024 | 2019 | — | — | ✅ | — | — | — | same eyes imaged two ways | **not stated** | 2026-09-11 |
| [CHASE-DB1](datasets/chase-db1.md) | 28 | 1280×960 distributor / 999×960 as circulated | 2012 | — | ✅ **×2 observers** | — | — | — | — | paediatric, multi-ethnic, hand-held camera | **not established** | 2026-09-11 |
| [LES-AV](datasets/les-av.md) | 22 | 1444×1620 (21), 1958×2196 (1) | 2018 | — | ✅ derived from A/V | ✅ | — | — | ✅ **glaucoma subtypes** | blood pressure, heart rate, IOP | research only, **no commercial use** | 2026-09-11 |
| [STARE](datasets/stare.md) | 20 (vessel subset of 397) | 700×605 | 2000 | — | ✅ **×2 observers** | — | — | — | ✅ 10 of 20 with pathology | — | **not stated** | 2026-09-11 |
| [UNAF](datasets/unaf.md) | 15 | 1444×1444 as redistributed | 2024 | — | — | ✅ | — | — | ✅ DR | Paraguay — geographic coverage | **not established** | 2026-09-11 |

## 2. Shared photographs

Two datasets built on the same photographs are one camera's worth of evidence. This section maps
that in both directions; each detail page repeats its own half of the link.

| | |
| --- | --- |
| **[DRIVE](datasets/drive.md) → [RITE](datasets/rite.md)** | **RITE *is* DRIVE** — the same 40 photographs, unresized, with an artery/vein reference standard added by a different group at a different institution. It is widely cited as "DRIVE-AV", so a training list naming DRIVE and DRIVE-AV separately has one set of images. Their *vessel* annotations differ, though: RITE's training split is a modified version of DRIVE's first observer and its test split follows DRIVE's second, so a Dice against one is not a Dice against the other. |
| **[HRF](datasets/hrf.md) ← HRF-AV, HRF-Seg+** | One set of 45 photographs annotated by three groups: the original vessel gold standard and two experts' disc centres, an artery/vein standard from a second group, and disc-and-cup contours from a third. Three papers, three downloads, three licence positions — catalogued as one dataset with three layers. |
| **[REFUGE](datasets/refuge.md) ⊃ REFUGE** | REFUGE2's 2,000 photographs **contain** the first edition's 1,200, of which 800 are the AutoMorph family's disc/cup training data. A number quoted on REFUGE2 is therefore partly in-sample and partly not, and pooling the editions hides which. |
| **[REYIA](datasets/reyia.md) ← nine datasets** | A compilation: 478 of its 589 photographs come from [FIVES](datasets/fives.md) (75), [PAPILA](datasets/papila.md) (78), MESSIDOR, Magrabia, mBRSET, GRAPE, TREND and AV-WIDE; only its 111-image ENRICH set is new. Every row carries its source, which is what makes the overlap traceable. |
| **[G1020](datasets/g1020.md), [ORIGA](datasets/origa.md), REFUGE** | Distributed together in one third-party Kaggle bundle, <https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets>. That is packaging, not shared photographs — the three are separate collections, and the bundle's licence field is the uploader's, not any depositor's. |

## 3. Not colour fundus photography

These look like fundus datasets in a file browser and cannot be pooled with them.

| Dataset | Modality | Why it matters anyway |
| --- | --- | --- |
| [RAVIR](datasets/ravir.md) | **Infrared reflectance** from a Heidelberg Spectralis — no colour information at all, so artery/vein separation cannot use the colour cues every model here relies on | [OCULARNet](models/ocularnet.md) uses it as a deliberate far out-of-distribution test. A poor score here is not a failure on the intended input |
| [MSHF](datasets/mshf.md) *(500 of its 1,302)* | **Ultra-wide-field** mosaics at 200°, alongside 45–60° photographs in the same archive | The colour-fundus portion is a valuable held-out quality cohort; the UWF portion must be separated first |
| [DeepDRiD](datasets/deepdrid.md) *(one split)* | An **ultra-wide-field** split accompanies the regular fundus photographs | Same caution: one archive, two modalities |
| [FOVEA](datasets/fovea-dataset.md) *(40 of its 80)* | **Surgical microscope video frames**, video-compressed, with the illumination and magnification of an operating theatre | The pairing with preoperative photographs of the same eye is the design's whole value |
| [IOSTAR](datasets/iostar.md) | **Scanning laser ophthalmoscopy** — the image is formed by scanning a laser, so vessel contrast, colour and noise all differ | It carries the only **vessel junction** annotation in this catalogue, which is the ground truth [bifurcation angles](biomarkers/bifurcation-angle.md) and [junction counts](biomarkers/junction-counts.md) need. It is also, unexpectedly, part of the AutoMorph vessel model's training data |

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
- **Known defects** are not in this table either. Every detail page carries a section 7 for errors
  in the distribution itself — mislabelled files, counts that disagree with the paper, annotations
  that do not match their own description.

## 5. Adding a dataset

Dataset pages follow a fixed structure so they can be read against each other. Load the
`document-dataset` skill, which defines that structure and this table's columns, before adding or
changing an entry.
