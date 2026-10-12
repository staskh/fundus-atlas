# DR HAGIS

40 colour photographs of the back of the eye — **39 different photographs, because one appears
twice** — taken in an English NHS diabetic eye screening programme, each with a tracing of its blood
vessels drawn by one expert grader. Every patient is diabetic, and the photographs are grouped by a
second condition: glaucoma, hypertension, diabetic retinopathy, or age-related macular degeneration.
The name is an acronym of those four: *Diabetic retinopathy, Hypertension, Age-related macular
degeneration and Glaucoma ImageS*. It was published in 2017 to give vessel-tracing methods a test
set that looks like real screening work — high-resolution, several cameras, eyes with other
disease — rather than the small single-camera sets the field had. An artery/vein layer for all 40
files was later added by the [OCULAR](../projects/ocularnet.md) project, drawn by a model and
corrected by hand.

## 1. What it is

- **Images:** 40 files, 39 distinct photographs, in four groups of ten: glaucoma (images 1–10),
  hypertension (11–20), diabetic retinopathy (21–30) and age-related macular degeneration (31–40).
  **Images 24 and 32 are the same photograph**, of a patient with both diabetic retinopathy and
  macular degeneration, placed in both groups. No healthy eyes: screening programmes see only
  diabetic patients.
- **Collected at:** diabetic retinopathy screening centres in the UK run by Health Intelligence
  (Sandbach, UK), which supplied the photographs; the dataset was built at the Division of Pharmacy
  and Optometry, University of Manchester.
- **Purpose:** a vessel-tracing reference standard representative of NHS screening photographs — in
  the authors' words, "to aid the development of vessel extraction algorithms suitable for retinal
  screening programmes".

## 2. Provenance

### 2.1 DR HAGIS — the photographs, vessel tracings and field-of-view masks

| | |
| --- | --- |
| Home | The authors' page, <http://personalpages.manchester.ac.uk/staff/niall.p.mcloughlin> (cited as reference 23 of the paper). **It answers 404** (checked 2026-10-12), as do its download page and `DRHAGIS.zip`; the last archived working copy is from 2024-07-14 ([Wayback Machine](https://web.archive.org/web/20240714064511/https://personalpages.manchester.ac.uk/staff/niall.p.mcloughlin/)) |
| Download | **direct, no registration — from a Zenodo record whose depositor is not established.** <https://zenodo.org/records/10847157> (DOI [10.5281/zenodo.10847157](https://doi.org/10.5281/zenodo.10847157)), one file, `DRHAGIS.zip`, 10.5 MB, published 2024-03-21. The record names as creator "Faculty of Biology, Medicine and Health, University of Manchester" and has no description; nothing on it shows that the authors made the deposit |
| Citation | Holm S, Russell G, Nourrit V, McLoughlin N. *DR HAGIS — a fundus image database for the automatic extraction of retinal surface vessels from diabetic patients.* Journal of Medical Imaging 2017;4(1):014503. DOI: [10.1117/1.JMI.4.1.014503](https://doi.org/10.1117/1.JMI.4.1.014503) · [PMC5299858](https://pmc.ncbi.nlm.nih.gov/articles/PMC5299858/) · PMID 28217714 |
| Licence | **Conflicting.** The authors' page stated: "free to download for research and educational purposes only. Unauthorized use, redistribution or copying of the entire, or any part of, the database is prohibited", and required citing the paper. The Zenodo record is labelled **CC BY 4.0**. A record of unestablished origin cannot loosen the authors' terms, so treat the data as **research and educational use only, redistribution prohibited** |
| Content | 40 JPEG photographs (39 distinct) at five sizes, 2816×1880 to 4752×3168 |
| Annotations | Supplies one expert's binary vessel tracing per photograph, and a field-of-view mask per photograph |

The archive as listed on Zenodo (*our finding, 2026-10-12*, from its file index only — no image was
downloaded) holds three folders of 40 files each: `Fundus_Images/1.jpg … 40.jpg`,
`Manual_Segmentations/<n>_manual_orig.png` and `Mask_images/<n>_mask_orig.png`, plus macOS
metadata files. That matches the layout the authors' page described: fundus photographs as
"compressed JPEG files with 8 bits per colour plane", tracings and masks as "binary PNG files".

A third-party copy also circulates inside
[`hitszsyl/ICPRVessels`](https://github.com/hitszsyl/ICPRVessels/tree/master/Vessels-Datasets/DR-Hagis),
the repository that carries [ORVS](orvs.md), re-split into 34 training and 6 test photographs. It is
an uploader's copy, not the authors', with no licence of its own.

### 2.2 OCULAR — artery/vein labels

| | |
| --- | --- |
| Home | The OCULAR repository, <https://github.com/GonzaloPlaaza/OCULAR>, section "Release of New Artery-Vein Annotations" |
| Download | **direct, no registration** — a public Google Drive folder, <https://drive.google.com/drive/folders/1roUlNMqy5oGpfq53p6W17AIHcEXyPrk9> |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030 — [Plaza 2026](../papers/plaza-2026.md) |
| Licence | **not stated** — the OCULAR repository has no LICENSE file. The photographs underneath remain under DR HAGIS's own terms (section 2.1) |
| Content | 40 PNG label maps, `1.png` … `40.png`, numbered as the DR HAGIS photographs (checked 2026-10-12) |
| Annotations | Supplies artery, vein and crossing labels, drawn by [OCULARNet](../models/ocularnet.md) at 1024×1024, cut back to DR HAGIS's own vessel tracing and corrected by hand |

These are the first artery/vein labels for DR HAGIS, and they are a model's. OCULAR's README
describes the procedure: OCULARNet predicts artery, vein, crossing or background at 1024×1024; the
DR HAGIS vessel tracing is resized to the same grid; model pixels outside the tracing are removed,
traced pixels the model missed are given its next most likely class; the authors then paint over
errors in their own annotation tool, which also offers an *uncertain* class; and the result is
multiplied by the vessel tracing again. Every vessel pixel is therefore one the DR HAGIS grader
drew; which class it is, is OCULARNet's call wherever its authors did not overrule it. The README
announces the release "upon paper publication"; the paper is published and the folder is populated.
OCULAR states these annotations were not used to train or evaluate OCULARNet.

OCULAR's README links DR HAGIS's "Dataset Download" to
<https://www.kaggle.com/datasets/ba1b909c12dbe6c08df00b3ee6fc22d2fef632870359f91384b9001a870f67bf>.
That is the link-shared Kaggle URL of [REYIA](reyia.md), which does not contain DR HAGIS — our
reading is a copy-paste error in the README. The original distributor is the one in section 2.1.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **Five sizes:** 4752×3168, 3456×2304, 3216×2136, 2896×1944 and 2816×1880 (the paper). How many photographs are at each size, and which camera produced which, is not published. Not checked by this repository, which has not downloaded the images |
| Microns per pixel | Unknown — not published, and no scale has been inferred here yet (no fetcher exists) |
| Camera | Three non-mydriatic cameras: Canon CR DGi, Topcon TRC-NW6s and Topcon TRC-NW8, each with a digital back that sets the pixel size. Which photograph came from which is not stated |
| Field of view | 45°, horizontal |
| Centring | **Not stated by the authors.** OCULAR's README and the VascX paper both list DR HAGIS as macula-centred ("M") — their claims, not checked here |
| Modality | Colour fundus photography, stored as compressed JPEG |

OCULAR's README agrees with the paper on field (45°), region (UK) and the five sizes, which it
writes height first (`[1880x2816]` … `[3168x4752]`). It differs in two places: it counts **40**
images where the paper counts 39 distinct ones, and it lists the pathologies as glaucoma, diabetic
retinopathy, AMD and **HR — hypertensive retinopathy**, where the paper's group is **hypertension**,
a systemic diagnosis, with no statement that the retina shows hypertensive changes.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **One expert grader** with over 15 years' experience (G. Russell, an author) | Native | Traced in GIMP over the JPEG photograph with a line tool whose width was matched to each vessel, about 40 minutes per image. The authors chose not to provide a second reader, so no human agreement ceiling can be measured |
| Field of view | Automatic | Native | Sum of the three colour channels thresholded at 50 — a rule, not a person's outline |
| Disease group | Per photograph, by the screening programme | — | Glaucoma, hypertension, diabetic retinopathy or AMD, ten files each, on top of diabetes in every patient. **A comorbidity group, not a severity grade**: no retinopathy grade is given, even in the diabetic retinopathy group |
| Artery, vein and crossing, by [OCULAR](../projects/ocularnet.md) | One model, refined by OCULAR's authors | **1024×1024**, not this dataset's native 2816–4752 pixels across | A model's output corrected by hand, not an independent reader: where the model and the corrector agree on a mistake, it stays. The size at which the published PNGs are stored was not checked. Section 2.2 |

## 5. Inheritance

- **Reuses images from:** No shared images established. The photographs were supplied for this
  dataset by Health Intelligence's screening service.
- **Its images are reused by:** [OCULAR](../projects/ocularnet.md), which adds artery/vein labels to
  all 40 files (section 2.2). It did not train or evaluate OCULARNet on them. No other catalogued
  dataset is established to contain them.

## 6. Use as a benchmark

- **Catalogued models trained on these images:**
  [VascX vessel segmentation](../models/vascx-vessels.md). The VascX paper (Vargas Quiros et al.,
  [arXiv:2409.16016](https://arxiv.org/abs/2409.16016), Tables 1 and 4) lists DRHAGIS, all 40, among
  the public datasets used to develop its vessel model, trained by five-fold cross-validation; the
  released ensemble therefore saw every photograph in training, and a VascX vessel score here is
  in-sample. OCULAR states its artery/vein labels were not used to train or evaluate
  [OCULARNet](../models/ocularnet.md). The AutoMorph vessel code has a loader for DR-HAGIS, but the
  training set its [SEGAN vessel segmenter](../models/segan-vessel.md) lists, `ALL-SIX`, does not
  include it.
- **Below a model's measuring grid:** No — every size is above the 912 and 1024 grids the
  catalogued models measure on. The reverse applies: the photographs are three to five times wider
  than those grids, so thin vessels the grader traced at native size can vanish when the image is
  shrunk for a model. The OCULAR artery/vein layer was drawn at 1024×1024 and carries no finer
  detail than that grid.
- **What it can answer:** vessel segmentation on high-resolution UK screening photographs from three
  cameras, in eyes with glaucoma, hypertension, diabetic retinopathy or macular degeneration —
  held out for every catalogued model except VascX. With the OCULAR layer, artery/vein accuracy,
  with the caveat that the reference was itself drawn by OCULARNet, so scoring OCULARNet against it
  is not an independent test.

## 7. Known defects

- **One photograph is in the set twice.** Images 24 and 32 are identical (the authors). The authors
  ask that one be excluded when reporting over the whole set and both kept when reporting per
  group. Scoring all 40 counts that eye twice. *Our finding, 2026-10-12:* in the Zenodo archive the
  two JPEGs, the two tracings and the two masks have identical sizes, consistent with exact copies.
- **The original distribution is gone.** *Our finding, 2026-10-12:* the authors' page, its download
  page and `DRHAGIS.zip` all answer 404. The Zenodo copy predates the page going offline
  (published 2024-03-21; last archived working page 2024-07-14), but its depositor is not
  established and its CC BY 4.0 label contradicts the authors' prohibition on redistribution
  (section 2.1).
- **The authors' page gave one size wrongly.** It listed "3126x2136"; the paper gives **3216×2136**.
  The wrong figure is repeated in third-party loader documentation (Idiap's `bob.ip.binseg` and
  `mednet`). The paper's figure is the one recorded here; neither has been checked against the
  files.
- **Count: 39 or 40.** The paper and the authors' page say 39 photographs; the archive, OCULAR's
  README and the VascX paper count 40 files. Both are right — the difference is the duplicate above —
  but a "40-image" result has double-weighted one eye.
- **The vessel tracings were drawn on compressed JPEGs.** The photographs are distributed only as
  "compressed JPEG" (the authors), heavily so: the archive's 40 photographs of 5 to 15 megapixels
  average about 260 kB each (*our finding*, from the file index). Compression blurs the finest
  vessels, so the tracing's thinnest branches rest on degraded pixels.

## 8. Notes

- One reader, three cameras, 39 eyes: valuable as a held-out, high-resolution, multi-camera screening
  set, not as a precise yardstick. The authors justify a single reader by assuming disagreement
  between graders similar to DRIVE's; that is an assumption, not a measurement on these images.
- The disease groups are what the screening service recorded about the patient, not a grading of
  the photograph. "Hypertension" means a hypertensive patient, not necessarily a hypertensive
  retina.
- Treat the two layers as having different authors. The vessel tracing is a person's; the
  artery/vein colouring is a model's, checked by people. A model that resembles OCULARNet will look
  better against the second than it deserves.

---

**Links, licence and access last checked:** 2026-10-12
