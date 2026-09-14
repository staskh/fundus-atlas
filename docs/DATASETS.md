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

Sorted by image count, largest first. Two markers in the Dataset column: **←** means the photographs
come from another dataset, named after the arrow (section 2 has the detail); **(SLO)**, **(IR)**,
**+UWF**, **+OCT**, **+surgical** and **(dual-modal)** mean the collection is wholly or partly not
standard colour fundus photography (section 3). The date each page's links and licence were last
checked is on the page itself.

**Down** is how much effort it takes to actually get the data:

| | |
| --- | --- |
| ✅ | **Direct download.** Unattended, no account: a URL a script can fetch |
| 🟡 | **Public repository, trivial step.** Kaggle, IEEE DataPort, a challenge platform or a click-through licence — an account or a form, granted automatically |
| ⛔ | **Request or agreement.** An email to the authors, credentialed access with training, or a data transfer agreement signed by an institution |
| ❓ | **Unresolved.** The route could not be established; see the page |

A green mark says nothing about the **licence** — several ✅ datasets are research-use-only or
prohibit redistribution, and one ⛔ dataset is more permissively licensed than some ✅ ones. Getting
the data and being allowed to use it are separate questions, so read the Licence column beside it.

The annotation columns of the table are the same facts regrouped in 1.1–1.4: quality of the
photograph, arteries against veins, the optic disc (and whether the cup is there too), and disease
of the eye. Those lists do not add datasets; they make the same catalogue readable by what is
labelled.

| Dataset&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Images | Resolution | Year | Quality | Vessels | A/V | Disc | Cup | Disease | Other labels | Licence | Down |
| :------------------------- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [EyeQ](datasets/eyeq.md) ← EyePACS | 28,792 | **highly mixed** — many devices | 2019 | ✅ Good / Usable / Reject | — | — | — | — | ✅ DR 0–4, from EyePACS | — | labels **not stated**; images under EyePACS competition terms | 🟡 |
| [BRSET](datasets/brset.md) | 16,266 | mixed | 2024 | ✅ focus / illumination / field / artefacts | — | — | — | — | ✅ multi-label + DR grades | anatomical flags, **demographics** | PhysioNet credentialed licence + DUA | ⛔ |
| [mBRSET](datasets/mbrset.md) | 5,164 | mixed, handheld | 2024 | ✅ | — | — | — | — | ✅ DR | demographics | PhysioNet credentialed licence + DUA | ⛔ |
| [DeepDRiD](datasets/deepdrid.md) +UWF | 2,000 (+256 UWF) | six sizes, 1592–2232 px; **dual view per eye** | 2020 | ✅ arbitrated, + artefact / clarity / field | — | — | — | — | ✅ DR, per image and per patient | dual-view pairing | **CC BY-SA 4.0** — share-alike | ✅ |
| [FQS](datasets/fqs.md) | 2,246 | ~1942×1942 originals, plus a 1024×1024 copy | 2025 | ✅ **continuous 0–100 ×6 doctors** + three-class ×3 graders | — | — | — | — | — | ten cross-validation folds | **CC BY 4.0** | ✅ |
| [Chákṣu](datasets/chaksu.md) | 1,345 | 2448×3264 **portrait**, 2048×1536, 1920×1440 | 2023 | — | — | — | ✅ **×5 experts** | ✅ **×5 experts** | ✅ glaucoma, **×5 independent decisions** | three cameras incl. handheld | **CC BY 4.0** | ✅ |
| [MSHF](datasets/mshf.md) +UWF | 1,302 | mixed by device | 2023 | ✅ **×3 readers**, illumination / clarity / contrast / overall | — | — | — | — | ✅ DR, glaucoma, healthy | camera class per image | **CC BY 4.0** | ✅ |
| [REFUGE / REFUGE2](datasets/refuge.md) | 1,200 / 2,000 | mixed — 2124×2056, 1634×1634, + | 2020 | — | — | — | ✅ consensus | ✅ consensus | ✅ glaucoma | fovea coordinate | research and educational, challenge terms | 🟡 |
| [ADAM](datasets/adam.md) | 1,200 | 2124×2056 (824), 1444×1444 (376) | 2022 | — | — | — | ✅ masks, **some blank** | — | ✅ AMD / non-AMD | fovea coordinates; lesion masks — drusen, exudates, haemorrhages, scars | not stated | 🟡 |
| [MESSIDOR](datasets/messidor.md) | 1,200 | 1440×960, 2240×1488, 2304×1536 | 2014 | — | — | — | — | — | ✅ DR 0–3 and macular-oedema risk 0–2 | — | research and educational use, ADCIS agreement | 🟡 |
| [G1020](datasets/g1020.md) | 1,020 | mixed — **41 sizes**, 1944×2108 to 2426×3007 | 2020 | — | — | — | ✅ | ✅ (791 of 1,020) | ✅ glaucoma 296 / normal 724 | vertical CDR, ISNT rim widths, disc box | research only, no standard grant | 🟡 |
| [FIVES](datasets/fives.md) | 800 | 2048×2048 | 2022 | ✅ illumination / blur / contrast | ✅ consensus | — | — | — | ✅ AMD / DR / glaucoma / normal | — | **CC BY 4.0** | ✅ |
| [RIGA](datasets/riga.md) ← MESSIDOR | 750 | mixed — three sources | 2018 | — | — | — | ✅ **×6 ophthalmologists** | ✅ **×6 ophthalmologists** | — | each annotator's CDR; RIGA+ domain splits | **CC BY-NC 4.0** | 🟡 |
| [ORIGA](datasets/origa.md) | 650 | 2048 tall, 2426–2616 wide | 2010 | — | — | — | ✅ | ✅ | ✅ glaucoma 168 / normal 482 | **published expert CDR**, eye side | research use, request-based | 🟡 |
| [GRAPE](datasets/grape.md) | 631 | full frames; **contours on an ROI crop** | 2023 | — | — | — | ✅ | ✅ | ✅ glaucoma, **longitudinal** | visual fields, OCT, IOP, visit dates | **CC BY 4.0** | ✅ |
| [REYIA](datasets/reyia.md) ← 9 sources | 589 | mixed, by source | 2025 | — | — | ✅ | — | — | mixed, by source | per-image source attribution | MIT on the compilation; **sources stricter** | ⛔ |
| [IDRiD](datasets/idrid.md) | 516 | 4288×2848 | 2018 | — | — | — | ✅ (81 of 516) | — | ✅ DR 0–4 and macular oedema 0–2 | four lesion classes, fovea | **CC BY 4.0** | ✅ |
| [PAPILA](datasets/papila.md) | 488 | 2576×1934 | 2022 | — | — | — | ✅ ×2 experts | ✅ ×2 experts | ✅ healthy / suspect / glaucoma | full clinical record per eye | GPL-3.0 or later | ✅ |
| [RIM-ONE DL](datasets/rim-one-dl.md) ← r1–r3 | 485 | not stated by the distributor | 2020 | — | — | — | ✅ | ✅ | ✅ normal 313 / glaucoma 172 | **hospital-based split** | research and educational use | ✅ |
| [GAMMA](datasets/gamma.md) +OCT | 300 pairs, ~100 labelled | mixed | 2023 | — | — | — | ✅ | ✅ | ✅ normal / early / progressive glaucoma | fovea, paired OCT volume | challenge terms, research use | 🟡 |
| [FunPiQ](datasets/funpiq.md) ← EyeQ, BRSET, mBRSET | 300 | mixed, by source | 2026 | ✅ **pixel-level** degraded-region masks | — | — | — | — | — | — | annotations per Zenodo record; **images inherit PhysioNet terms** | ⛔ |
| [Leuven-Haifa (UZLF)](datasets/leuven-haifa.md) | 240 | 1444×1444 | 2024 | ✅ automated score | — | ✅ **×2 readers** (junior + senior correction) | — | — | ✅ glaucoma, three categories | age, sex, **12 published vessel measurements** | custom, **non-commercial**, signed agreement | ⛔ |
| [DRIMDB](datasets/drimdb.md) | 216 | unknown | 2014 | ✅ good / bad / **outlier** | — | — | — | — | — | the outlier class: images that are not fundus photographs | not stated | ✅ |
| [RAV](datasets/rav.md) | 206 | 1024×1024 (**authors' crop and resize**) | 2025 | ✅ mixed by design | — | ✅ | — | — | — | Rotterdam Study population cohort | **CC BY-NC 4.0 per the README; CC0 per the record — contradictory** | ✅ |
| [UoA-DR](datasets/uoa-dr.md) | 200 | 2124×2056 | — | — | ✅ | — | ✅ boundary **and centre** | — | ✅ DR severity | **fovea centre** | custom signed agreement | ⛔ |
| [MAPLES-DR](datasets/maples-dr.md) ← MESSIDOR | 198 | MESSIDOR natives; **labels drawn at 1500×1500** | 2024 | — | ✅ | — | ✅ | ✅ (192 of 198) | ✅ regraded DR and macular oedema | six lesion classes, macula | **CC BY 4.0** labels; images research-only | 🟡 |
| [Drishti-GS](datasets/drishti-gs.md) | 101 | ~2896×1944 | 2015 | — | — | — | ✅ ×4 experts, **soft maps** | ✅ ×4 experts, soft maps | ✅ glaucoma | CDR, notching | "free to use" — not a standard licence | 🟡 |
| [AVRDB](datasets/avrdb.md) | 100 | 1504×1000 | 2020 | — | ✅ | ✅ | ✅ optic nerve head | — | ✅ hypertensive retinopathy, papilloedema | **published AVR per image**, exudates, cotton-wool spots | **CC BY 4.0** | ✅ |
| [Fundus-AVSeg](datasets/fundus-avseg.md) | 100 | 2656×1992 (21), 1280×1280 (79) | 2025 | ✅ high / low | ✅ derived from A/V | ✅ | — | — | ✅ four classes | eye side | **CC BY 4.0** | ✅ |
| [RETA](datasets/reta.md) ← IDRiD, resized | 81 — **54 masks public** | 1024×1024 | 2022 | — | ✅ | — | — | — | — | inter- and intra-annotator disambiguation record | **CC BY 4.0** | ✅ |
| [FOVEA](datasets/fovea-dataset.md) +surgical | 80 (40 eyes ×2) | 1934×1960 and 1080×1920 | 2025 | — | ✅ **×2 readers** | — | ✅ **×2 readers** | — | — | paired preoperative / surgical-microscope views | **CC BY-NC-ND 4.0** — no derivatives | ✅ |
| [VICAVR](datasets/vicavr.md) | 58 | 768×584 | — | — | — | ✅ **×3 experts** | — | — | — | **published calibres at several radii** | research use, no standard licence | ⛔ |
| [GAVE](datasets/gave.md) | 50 | 1536×1024 | 2025 | — | ✅ | ✅ | — | — | — | — | **CC BY 4.0** | ❓ |
| [HRF](datasets/hrf.md) *(three annotation layers)* | 45 | 3504×2336 | 2013 | — | ✅ | ✅ via HRF-AV | ✅ centres ×2 experts; contours via HRF-Seg+ | ✅ via HRF-Seg+ (40 of 45) | ✅ healthy / glaucoma / DR | field-of-view masks | CC BY 4.0 images; **layers vary, one unknown** | ✅ |
| [RITE](datasets/rite.md) ← DRIVE | 40 | 565×584 | 2013 | — | ✅ (differs from DRIVE's) | ✅ | — | — | — | overlap and uncertain vessel classes | research use, citation required | ⛔ |
| [DRIVE](datasets/drive.md) | 40 | 565×584 | 2004 | — | ✅ + **second observer** on the test split | — | — | — | ✅ 7 of 40 with mild DR | field-of-view masks | research use, registration terms | 🟡 |
| [INSPIRE-AVR](datasets/inspire-avr.md) | 40 | 2392×2048 | 2011 | — | ✅ | AVR only, ×2 experts | ✅ | — | — | **published AVR per image** (IVAN) | research use; **redistribution prohibited** | ✅ |
| [RAVIR](datasets/ravir.md) **(IR)** | 36 | 768×768 | 2022 | — | — | ✅ | — | — | ✅ DR, hypertensive retinopathy | test masks withheld | usage protocol, not a standard grant | 🟡 |
| [IOSTAR](datasets/iostar.md) **(SLO)** | 30 | 1024×1024 | 2016 | — | ✅ | ✅ | ✅ | — | — | **vessel junctions** — bifurcations and crossovers | research use | ⛔ |
| [DualModal2019](datasets/dualmodal2019.md) **(dual-modal)** | 30 | 1024×1024 | 2019 | — | — | ✅ | — | — | — | same eyes imaged two ways | **not stated** | 🟡 |
| [WIDE](datasets/wide.md) **(ultra-wide-field 200°)** | 30 | 3900×3072 | 2015 | — | — | ✅ **×2 raters** | — | — | ✅ healthy / AMD | **vascular graph annotations** | research and educational use; **redistribution prohibited** | ✅ |
| [CHASE-DB1](datasets/chase-db1.md) | 28 | 1280×960 distributor / 999×960 as circulated | 2012 | — | ✅ **×2 observers** | — | — | — | — | paediatric, multi-ethnic, hand-held camera | **not established** | ✅ |
| [LES-AV](datasets/les-av.md) | 22 | 1444×1620 (21), 1958×2196 (1) | 2018 | — | ✅ derived from A/V | ✅ | — | — | ✅ **glaucoma subtypes** | blood pressure, heart rate, IOP | research only, **no commercial use** | ✅ |
| [STARE](datasets/stare.md) | 20 (vessel subset of 397) | 700×605 | 2000 | — | ✅ **×2 observers** | — | — | — | ✅ 10 of 20 with pathology | — | **not stated** | ✅ |
| [UNAF](datasets/unaf.md) | 15 | 1444×1444 as redistributed | 2024 | — | — | ✅ | — | — | ✅ DR | Paraguay — geographic coverage | **not established** | ❓ |

### 1.1 Quality of the photograph

Quality grades the *photograph* — whether it is sharp enough, bright enough and well enough framed
to be read — not the *eye*. A Reject from [EyeQ](datasets/eyeq.md) and a glaucoma label from
[REFUGE](datasets/refuge.md) are different kinds of statement. These are the datasets that score the
image itself.

| Dataset | Images | What is scored | Readers |
| --- | --- | --- | --- |
| [EyeQ](datasets/eyeq.md) ← EyePACS | 28,792 | Three levels: Good / Usable / Reject | Graded by the EyeQ authors |
| [BRSET](datasets/brset.md) | 16,266 | Four separate flags: focus, illumination, image field, artefacts — not one overall grade | Per photograph |
| [mBRSET](datasets/mbrset.md) | 5,164 | Quality assessment per photograph, on handheld cameras | Per photograph |
| [DeepDRiD](datasets/deepdrid.md) +UWF | 2,000 | Overall (good enough to diagnose / not) plus artefact, clarity and field-definition subscores | Two ophthalmologists, confirmed or revised by a senior third. **Only the arbitrated result is published**, so the readers cannot be compared |
| [FQS](datasets/fqs.md) | 2,246 | A **continuous 0–100** score and a three-class grade (good / usable / reject) | Score: **six doctors, kept separate**. Class: **three graders, kept separate** |
| [MSHF](datasets/mshf.md) +UWF | 1,302 | Four binary components: illumination, clarity, contrast, overall | **Three readers, kept separate** as well as merged |
| [FIVES](datasets/fives.md) | 800 | Illumination, blur and contrast | Graded per photograph |
| [FunPiQ](datasets/funpiq.md) ← EyeQ, BRSET, mBRSET | 300 | **Pixel-level** masks of the degraded regions — which part of the image is unusable, not only how bad the whole frame is. The only such annotation here | Under a board-certified ophthalmologist |
| [Leuven-Haifa (UZLF)](datasets/leuven-haifa.md) | 240 | A quality **score from an automated network**, not a human grader | — |
| [DRIMDB](datasets/drimdb.md) | 216 | Three classes: good, bad, and **outlier** — photographs that are not of a retina | Unknown how many readers |
| [RAV](datasets/rav.md) | 206 | Not a grade: poor-quality photographs were **kept on purpose** rather than excluded | — |
| [Fundus-AVSeg](datasets/fundus-avseg.md) | 100 | High / low — 83 high-quality, 17 low-quality | Per photograph |

[FunPiQ](datasets/funpiq.md) re-annotates photographs already in EyeQ, BRSET and mBRSET, so it is
not a fourth camera. [DRIMDB](datasets/drimdb.md) is named for diabetic retinopathy and carries no
disease grade; its contribution is the quality classes, including the outlier class.

### 1.2 Arteries and veins

An **artery/vein** annotation colours arteries and veins as separate classes. That is what calibre
ratios such as CRAE and the arteriovenous ratio need: a vessel map that does not tell the two
apart cannot produce them. Datasets that only trace vessels, without saying which is which, stay
in the Vessels column of the summary and are not repeated here.

| Dataset | Images | What is labelled | Notes |
| --- | --- | --- | --- |
| [REYIA](datasets/reyia.md) ← 9 sources | 589 | Artery/vein maps | A compilation: 478 of the 589 photographs come from other datasets. Scoring REYIA and its sources counts the same eyes twice |
| [Leuven-Haifa (UZLF)](datasets/leuven-haifa.md) | 240 | Arterioles and venules | **Two readers kept separate** on the test split — a junior drawing and a senior's correction |
| [RAV](datasets/rav.md) | 206 | Artery/vein segmentation | Population cohort (Rotterdam Study); quality mixed by design |
| [AVRDB](datasets/avrdb.md) | 100 | Artery/vein network | Also publishes an **AVR number per image** |
| [Fundus-AVSeg](datasets/fundus-avseg.md) | 100 | Pixel-level artery/vein | Newer than the models in this catalogue, so it can evaluate them |
| [VICAVR](datasets/vicavr.md) | 58 | Artery/vein labels **near the disc**, not a dense whole-image map | **Three experts**; published calibres at several radii from the disc |
| [GAVE](datasets/gave.md) | 50 | Vessel and artery/vein labels | Reader count not stated |
| [HRF](datasets/hrf.md) | 45 | Arteries and veins as separate classes | The **HRF-AV** layer, added by a second group; the original release has vessels only |
| [RITE](datasets/rite.md) ← DRIVE | 40 | Four classes: artery, vein, overlap, uncertain | **RITE is DRIVE** — the same 40 photographs. Widely cited as "DRIVE-AV" |
| [INSPIRE-AVR](datasets/inspire-avr.md) | 40 | **AVR as a number per image**, from two experts using IVAN — not a pixel map of arteries and veins | In this list because it distinguishes arterioles from venules as a measurement, not as a mask |
| [RAVIR](datasets/ravir.md) **(IR)** | 36 | Artery and vein segmentations | **Infrared reflectance**, not colour fundus photography. Test masks withheld |
| [IOSTAR](datasets/iostar.md) **(SLO)** | 30 | Artery/vein | Scanning laser ophthalmoscopy, not a colour photograph |
| [DualModal2019](datasets/dualmodal2019.md) **(dual-modal)** | 30 | Artery/vein | Same eyes imaged two ways |
| [WIDE](datasets/wide.md) **(ultra-wide-field 200°)** | 30 | Artery/vein | **Two independent raters, kept separate**. A 200° Optos field, not a standard photograph |
| [LES-AV](datasets/les-av.md) | 22 | Artery/vein maps | Vessel masks are derived from the A/V labels, not drawn independently |
| [UNAF](datasets/unaf.md) | 15 | Artery/vein segmentation | Paraguay — the smallest set here; its value is geographic coverage |

### 1.3 Optic disc, and disc with cup

The **optic disc** is the visible head of the optic nerve. The **cup** is the depression in its
centre. A cup-to-disc ratio, used in glaucoma work, needs both outlines. Datasets that mark the
disc only cannot support that measurement; they are listed separately.

**Disc and cup.** Both structures are outlined. Where the cup is missing on some photographs, that
is noted in the Cup column.

| Dataset | Images | Disc | Cup | Notes |
| --- | --- | --- | --- | --- |
| [Chákṣu](datasets/chaksu.md) | 1,345 | ✅ **×5 experts**, kept separate | ✅ **×5 experts**, kept separate | Five independent glaucoma decisions as well |
| [REFUGE / REFUGE2](datasets/refuge.md) | 1,200 / 2,000 | ✅ consensus | ✅ consensus | REFUGE2 contains the first edition's 1,200 |
| [G1020](datasets/g1020.md) | 1,020 | ✅ | ✅ on **791 of 1,020** | Not disc-centred — a harder disc-segmentation test than a disc-centred set |
| [RIGA](datasets/riga.md) ← MESSIDOR | 750 | ✅ **×6 ophthalmologists**, kept separate | ✅ **×6 ophthalmologists**, kept separate | **No disease label**, despite being collected for glaucoma analysis |
| [ORIGA](datasets/origa.md) | 650 | ✅ | ✅ | Also publishes the graders' own cup-to-disc ratio as a number |
| [GRAPE](datasets/grape.md) | 631 | ✅ | ✅ | Contours are on a **crop around the nerve**, not the full 50° frame |
| [PAPILA](datasets/papila.md) | 488 | ✅ ×2 experts | ✅ ×2 experts | Both eyes of the same patient, with the clinical record |
| [RIM-ONE DL](datasets/rim-one-dl.md) ← r1–r3 | 485 | ✅ | ✅ | Hospital-based train/test split |
| [GAMMA](datasets/gamma.md) +OCT | 300 pairs, ~100 labelled | ✅ | ✅ | Only the training split has public labels |
| [MAPLES-DR](datasets/maples-dr.md) ← MESSIDOR | 198 | ✅ | ✅ on **192 of 198** | Labels drawn at 1500×1500, then stored at MESSIDOR's native size |
| [Drishti-GS](datasets/drishti-gs.md) | 101 | ✅ ×4 experts, **soft maps** | ✅ ×4 experts, soft maps | The value at each pixel is how many experts included it |
| [HRF](datasets/hrf.md) | 45 | Centres ×2 experts in the original release; contours via HRF-Seg+ | ✅ via HRF-Seg+, on **40 of 45** | Three annotation layers. The original authors marked disc **centres**, not contours; the cup arrives only with HRF-Seg+ |

**Disc only — no cup.** These mark the optic disc (or optic nerve head) and do not outline the
cup, so they cannot yield a cup-to-disc ratio.

| Dataset | Images | What is marked | Notes |
| --- | --- | --- | --- |
| [ADAM](datasets/adam.md) | 1,200 | Disc **masks**; some are entirely blank | A blank mask means no disc was annotated in that photograph, not that there is no disc. No cup |
| [IDRiD](datasets/idrid.md) | 516 | Disc masks on **81 of 516** — the segmentation subset only | The other 435 have disease grades and no disc outline. No cup |
| [UoA-DR](datasets/uoa-dr.md) | 200 | Disc **boundary and centre** | The centre is what a zone-based vessel measurement needs. No cup |
| [AVRDB](datasets/avrdb.md) | 100 | Optic **nerve head** | Alongside arteries, veins and a published AVR. No cup |
| [FOVEA](datasets/fovea-dataset.md) +surgical | 80 | Disc, **×2 readers**, on preoperative and surgical-microscope views | Paired views of the same eye. No cup |
| [INSPIRE-AVR](datasets/inspire-avr.md) | 40 | Disc reference | There so a zone-based calibre measurement has a centre. No cup |
| [IOSTAR](datasets/iostar.md) **(SLO)** | 30 | Disc | Scanning laser ophthalmoscopy, not a colour photograph. No cup |

### 1.4 Disease of the eye

Disease grades the *eye*, on a scheme that is **not interchangeable** between datasets: a 0–4
diabetic-retinopathy scale here, a glaucoma triple that includes "suspect" there, a binary AMD
flag elsewhere. A collection assembled in a disease clinic is not the same as a collection
*labelled* for that disease — [RIGA](datasets/riga.md) has six readers' disc and cup outlines and
no glaucoma label, so it is not in this table.

| Dataset | Images | Diabetic retinopathy | Glaucoma | AMD | Other labelled conditions |
| --- | --- | --- | --- | --- | --- |
| [EyeQ](datasets/eyeq.md) ← EyePACS | 28,792 | ✅ 0–4, inherited from EyePACS | — | — | — |
| [BRSET](datasets/brset.md) | 16,266 | ✅ present/absent, plus ICDR and SDRG grades 0–4 | increased cup–disc ratio as a flag, not a glaucoma diagnosis | ✅ present/absent | **Multi-label, each present/absent:** diabetic macular oedema, toxoplasmosis scar, nevus, vascular occlusion, hypertensive retinopathy, drusen, non-diabetic haemorrhage, retinal detachment, myopic fundus, other |
| [mBRSET](datasets/mbrset.md) | 5,164 | ✅ grades | — | — | — |
| [DeepDRiD](datasets/deepdrid.md) +UWF | 2,000 | ✅ 0–4, **per image and per patient** (worse eye) | — | — | — |
| [Chákṣu](datasets/chaksu.md) | 1,345 | — | ✅ `NORMAL` / `GLAUCOMA SUSPECT`, **×5 independent decisions** — not a severity grade | — | — |
| [MSHF](datasets/mshf.md) +UWF | 1,302 | ✅ on the colour-fundus portion | ✅ on the colour-fundus portion | — | Healthy, as a third class. Disease is by acquisition group, not a per-image grade overlapping the others |
| [REFUGE / REFUGE2](datasets/refuge.md) | 1,200 / 2,000 | — | ✅ yes/no; about 10% glaucomatous in REFUGE | — | — |
| [ADAM](datasets/adam.md) | 1,200 | — | — | ✅ AMD / non-AMD | Lesion masks: drusen, exudates, haemorrhages, scars |
| [MESSIDOR](datasets/messidor.md) | 1,200 | ✅ **0–3** (not the five-level ICDR scale) | — | — | Macular-oedema **risk 0–2** |
| [G1020](datasets/g1020.md) | 1,020 | — | ✅ 296 glaucoma / 724 normal | — | — |
| [FIVES](datasets/fives.md) | 800 | ✅ 200 | ✅ 200 | ✅ 200 | 200 normal. One class per eye, by design |
| [ORIGA](datasets/origa.md) | 650 | — | ✅ 168 glaucoma / 482 normal | — | — |
| [GRAPE](datasets/grape.md) | 631 | — | ✅ glaucoma, **longitudinal** — the same eyes followed over visits | — | Visual fields, OCT, intraocular pressure |
| [REYIA](datasets/reyia.md) ← 9 sources | 589 | by source (MESSIDOR, mBRSET) | by source (PAPILA, MAGREBHIA, GRAPE) | by source (AV-WIDE) | **No unified disease scheme** — each subset keeps its source's labels, and ENRICH has none |
| [IDRiD](datasets/idrid.md) | 516 | ✅ 0–4 on all 516 | — | — | Macular-oedema risk 0–2 on all 516; four lesion classes on 81 |
| [PAPILA](datasets/papila.md) | 488 | — | ✅ healthy / **suspect** / glaucoma | — | Full clinical record per eye |
| [RIM-ONE DL](datasets/rim-one-dl.md) ← r1–r3 | 485 | — | ✅ 313 normal / 172 glaucoma | — | — |
| [GAMMA](datasets/gamma.md) +OCT | 300 pairs, ~100 labelled | — | ✅ normal / **early** / **progressive** (intermediate and advanced) | — | Paired OCT volume |
| [Leuven-Haifa (UZLF)](datasets/leuven-haifa.md) | 240 | — | ✅ three categories, plus healthy | — | Twelve published vessel measurements |
| [UoA-DR](datasets/uoa-dr.md) | 200 | ✅ International Clinical Diabetic Retinopathy scale | — | — | — |
| [MAPLES-DR](datasets/maples-dr.md) ← MESSIDOR | 198 | ✅ **regraded** DR, not inherited from MESSIDOR | — | — | Macular oedema, **regraded**; six lesion classes |
| [Drishti-GS](datasets/drishti-gs.md) | 101 | — | ✅ glaucoma | — | Cup-to-disc ratio, notching |
| [AVRDB](datasets/avrdb.md) | 100 | — | — | — | **Hypertensive retinopathy** and **papilloedema**; published AVR |
| [Fundus-AVSeg](datasets/fundus-avseg.md) | 100 | ✅ 20 | ✅ 20 | ✅ 20 | 40 normal. One class per eye |
| [HRF](datasets/hrf.md) | 45 | ✅ 15 | ✅ 15 | — | 15 healthy. One class per eye |
| [DRIVE](datasets/drive.md) | 40 | 7 of 40 with mild early changes; 33 with none | — | — | A **collection description**, not a per-image grade file |
| [RAVIR](datasets/ravir.md) **(IR)** | 36 | ✅ represented | — | — | Hypertensive retinopathy. Infrared reflectance, not colour |
| [WIDE](datasets/wide.md) **(ultra-wide-field 200°)** | 30 | — | — | ✅ healthy / AMD, with the AMD subtype described | — |
| [LES-AV](datasets/les-av.md) | 22 | — | ✅ **subtypes**: normal, normal-tension, open-angle — the only subtype labels here | — | Blood pressure, heart rate, intraocular pressure |
| [STARE](datasets/stare.md) | 20 | — | — | — | **10 of 20 show pathology**, not named as a disease scheme |
| [UNAF](datasets/unaf.md) | 15 | ✅ represented | — | — | — |

## 2. Shared photographs

Two datasets built on the same photographs are one camera's worth of evidence. This section maps
that in both directions; each detail page repeats its own half of the link.

| | |
| --- | --- |
| **[DRIVE](datasets/drive.md) → [RITE](datasets/rite.md)** | **RITE *is* DRIVE** — the same 40 photographs, unresized, with an artery/vein reference standard added by a different group at a different institution. It is widely cited as "DRIVE-AV", so a training list naming DRIVE and DRIVE-AV separately has one set of images. Their *vessel* annotations differ, though: RITE's training split is a modified version of DRIVE's first observer and its test split follows DRIVE's second, so a Dice against one is not a Dice against the other. |
| **[HRF](datasets/hrf.md) ← HRF-AV, HRF-Seg+** | One set of 45 photographs annotated by three groups: the original vessel gold standard and two experts' disc centres, an artery/vein standard from a second group, and disc-and-cup contours from a third. Three papers, three downloads, three licence positions — catalogued as one dataset with three layers. |
| **[REFUGE](datasets/refuge.md) ⊃ REFUGE** | REFUGE2's 2,000 photographs **contain** the first edition's 1,200, of which 800 are the AutoMorph family's disc/cup training data. A number quoted on REFUGE2 is therefore partly in-sample and partly not, and pooling the editions hides which. |
| **[REYIA](datasets/reyia.md) ← nine datasets** | A compilation: 478 of its 589 photographs come from [FIVES](datasets/fives.md) (75), [PAPILA](datasets/papila.md) (78), MESSIDOR, Magrabia, mBRSET, GRAPE, TREND and AV-WIDE; only its 111-image ENRICH set is new. Every row carries its source, which is what makes the overlap traceable. |
| **[WIDE](datasets/wide.md) → [REYIA](datasets/reyia.md)** | REYIA's **AV-WIDE** is 26 of WIDE's 30 photographs, **resized from 3900×3072 to 829×1531** — under a quarter of the linear detail. Every "AV-WIDE" result in the literature is measured on that rendition, and WIDE's own licence prohibits redistribution. |
| **REYIA's subsets, counted six times** | ENRICH, FIVES-AV, MAGREBHIA, MESSIDOR-AV, AV-WIDE and TREND-AV are six of the fourteen training datasets [OCULARNet](models/ocularnet.md) lists — and all six are served from REYIA's single link-shared Kaggle URL. Two of them are annotations of FIVES and MESSIDOR photographs the list does not name separately. A count of datasets is not a count of independent evidence. |
| **[G1020](datasets/g1020.md), [ORIGA](datasets/origa.md), REFUGE** | Distributed together in one third-party Kaggle bundle, <https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets>. That is packaging, not shared photographs — the three are separate collections, and the bundle's licence field is the uploader's, not any depositor's. |

## 3. Not colour fundus photography

These look like fundus datasets in a file browser and cannot be pooled with them.

| Dataset | Modality | Why it matters anyway |
| --- | --- | --- |
| [RAVIR](datasets/ravir.md) | **Infrared reflectance** from a Heidelberg Spectralis — no colour information at all, so artery/vein separation cannot use the colour cues every model here relies on | [OCULARNet](models/ocularnet.md) uses it as a deliberate far out-of-distribution test. A poor score here is not a failure on the intended input |
| [MSHF](datasets/mshf.md) *(500 of its 1,302)* | **Ultra-wide-field** mosaics at 200°, alongside 45–60° photographs in the same archive | The colour-fundus portion is a valuable held-out quality cohort; the UWF portion must be separated first |
| [DeepDRiD](datasets/deepdrid.md) *(one split)* | An **ultra-wide-field** split accompanies the regular fundus photographs | Same caution: one archive, two modalities |
| [FOVEA](datasets/fovea-dataset.md) *(40 of its 80)* | **Surgical microscope video frames**, video-compressed, with the illumination and magnification of an operating theatre | The pairing with preoperative photographs of the same eye is the design's whole value |
| [WIDE](datasets/wide.md) | **Ultra-wide-field at 200°** on an Optos 200Tx — four times the field of a standard photograph, with heavy peripheral projection distortion | The only ultra-wide dataset here with vessel-level annotation, and the only one publishing a vascular **graph**. Its circulating AV-WIDE copy inside [REYIA](datasets/reyia.md) is 26 of 30 images at a fifth of the pixel count |
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
  is what lets a human agreement ceiling be measured rather than assumed. Sections **1.1–1.4**
  collect the same facts by annotation type, so a reader looking for a quality set, an artery/vein
  set, a disc/cup set or a disease-graded set does not have to scan every row.
- **Quality** grades the *photograph*; **Disease** grades the *eye*, and the schemes are not
  interchangeable between datasets — four classes here, three there, a glaucoma triple including
  "suspect" elsewhere. The cell names the scheme; the page explains it. Disc without cup cannot
  produce a cup-to-disc ratio; those datasets are separated in 1.3.
- **Other labels** — fovea locations, lesion classes, demographics, published biomarker values,
  vessel junctions. This is where the unusual and most valuable content hides.
- **Down** summarises the access route; the detail of it — the URL, the form, the agreement, which
  layer of a multi-part dataset each applies to — is in each page's provenance table. Where a
  dataset's images and its annotations arrive by different routes, the column shows the **harder** of
  the two: [FunPiQ](datasets/funpiq.md)'s annotations download freely but its photographs need
  PhysioNet credentialing, so it is marked ⛔.
- **Not in this table, on the detail pages instead:** camera and field of view, microns per pixel,
  the full download route, the describing paper, and inheritance. Each
  of those is a per-subcollection or per-annotation-layer fact that one cell would misrepresent —
  a dataset annotated by three institutions has three papers, three downloads and possibly three
  licences.
- **Known defects** are not in this table either. Every detail page carries a section 7 for errors
  in the distribution itself — mislabelled files, counts that disagree with the paper, annotations
  that do not match their own description.
- **When each entry was last checked** is recorded at the foot of its detail page rather than in a
  column here — licences and download routes change more often than the data, and the date belongs
  next to the facts it dates.

## 5. Adding a dataset

Dataset pages follow a fixed structure so they can be read against each other. Load the
`document-dataset` skill, which defines that structure and this table's columns, before adding or
changing an entry. A change to a row's Quality, A/V, Disc, Cup or Disease cell also updates the
matching regroup in sections 1.1–1.4.
