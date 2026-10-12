# TREND

72 colour photographs of the back of the eye from 40 healthy medical and dental students in
Montenegro, aged 19 to 23, each with a hand-traced map of its blood vessels. It is the only
collection in this catalogue built to describe a **healthy young** retina, and the only one taken
entirely on a **hand-held, non-mydriatic** camera of this make — the kind of device a family doctor
can use without dilating the pupil. The deposit also carries 10 photographs of older healthy
adults, the 22 photographs rejected for quality, a quality grade for every photograph, and the
vessel measurements the authors computed on each tracing.

## 1. What it is

- **Images:** 72 good-quality photographs of young adults — both eyes of 32 students and one eye of
  8 — the collection proper. Alongside them: 10 good-quality photographs of 7 healthy adults aged 55
  to 60, included as a comparison set, and 22 photographs judged of inadequate quality (14 young,
  8 older). 104 photographs in all.
- **Collected at:** Faculty of Medicine, University of Montenegro, Podgorica. Young participants
  were recruited among medical and dental students between 18 February and 11 March 2020; the older
  group between 22 December 2020 and 21 January 2021. All photographs were taken by a family
  medicine physician after brief online training.
- **Purpose:** in the authors' words, a standard for "normal retinal anatomy and microvascular
  geometry as it appears when visualized by the portable fundus camera", for developing vessel
  segmentation, image-quality grading and biomarkers of ageing. The name stands for *Topological
  characterization of the Retinal microvascular nEtwork visualized by portable fuNDus camera*.

## 2. Provenance

### 2.1 TREND — photographs, vessel tracings and quality grades

| | |
| --- | --- |
| Home | Zenodo, <https://zenodo.org/records/4521044> — DOI [10.5281/zenodo.4521044](https://doi.org/10.5281/zenodo.4521044) (version 1.1, the only version; the paper cites the concept DOI [10.5281/zenodo.4521043](https://doi.org/10.5281/zenodo.4521043), which resolves to it) |
| Download | **direct, no registration** — six zip archives and two spreadsheets, about 380 MB in all; the largest, `1_HEALTHY YOUNG_RAW_GOOD_QUALITY.zip`, is 270 MB |
| Citation | Popovic N, Vujosevic S, Radunović M, Radunović M, Popovic T. *TREND database: Retinal images of healthy young subjects visualized by a portable digital non-mydriatic fundus camera.* PLoS ONE 2021;16(7):e0254918. DOI: [10.1371/journal.pone.0254918](https://doi.org/10.1371/journal.pone.0254918) · [PMC8301647](https://pmc.ncbi.nlm.nih.gov/articles/PMC8301647/) |
| Licence | **CC BY 4.0** in the Zenodo licence field. The record's description says: "The database can be used freely for research purposes and it is released under Creative Commons 4.0 Attribution License" |
| Content | 104 photographs as TIFF, 2560×1920 per the distributor and the paper: 72 young good-quality, 14 young rejected, 10 older good-quality, 8 older rejected |
| Annotations | Supplies one binary vessel tracing per good-quality photograph (82, as PNG), a four-criterion quality grade for all 104, and a spreadsheet of per-photograph vessel measurements with demographic classes |

The description's "used freely for research purposes" sits beside a licence that does not itself
restrict use to research. Read the two together and attribute the authors; do not read the CC BY
grant as overriding the description's wording without asking them.

### 2.2 OCULAR — announced artery/vein layer

| | |
| --- | --- |
| Home | <https://github.com/GonzaloPlaaza/OCULAR>, README section *Release of New Artery-Vein Annotations* (checked at commit `3f13a8b`, 2026-10-09) |
| Download | **no** — the README lists TREND with an empty *A/V Annotations* cell: nothing is linked yet. Other datasets in the same list link to Google Drive folders |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030. No DOI established; stable URL <https://papers.miccai.org/miccai-2026-sat/OMIA_030>. Catalogued at [Plaza 2026](../papers/plaza-2026.md) |
| Licence | `not stated` — the OCULAR repository carries no licence file. The photographs underneath stay under TREND's own terms (2.1) |
| Content | The README's release list gives TREND as 72 photographs — the young good-quality set |
| Annotations | Supplies, once released, artery, vein and crossing classes plus an *uncertain* class, drawn at 1024×1024 |

The README says these labels are released "upon paper publication"; the paper was published on
2026-09-21 and the TREND link was still empty when checked. How they are made, per the README: the
[OCULARNet](../models/ocularnet.md) model predicts artery, vein and crossing at 1024×1024; TREND's
own vessel tracing is resized to 1024×1024 and thresholded; pixels outside the tracing are removed,
missed vessels are filled from the model's next most likely class, and the result is corrected by
hand in the authors' painting tool, then multiplied by the tracing again. The labels are therefore
**OCULARNet's output, constrained to TREND's vessel tracing and hand-corrected** — not an
independent artery/vein reading. Who corrected them, and how many people, is not stated.

The README's release-list row for TREND reads: centring **M** (macula-centred), field 45°,
resolution **2560×1960**, region **BE** (Belgium), pathology **G** (glaucoma). The resolution, region
and pathology disagree with the distributor and the paper, which give 2560×1920, Montenegro and
healthy participants; see section 7.

## 3. The images

### 3.1 Healthy young — 72 good-quality photographs (+14 rejected)

| | |
| --- | --- |
| Resolution (pixels) | **2560×1920**, per the Zenodo description and the paper (Table 1 and Methods). Not checked against the files by this repository |
| Microns per pixel | Unknown — not published, and not yet inferred for TREND's own files (no fetcher exists). [REYIA](reyia.md) carries an inferred 6.098 µm/px for its 48-photograph TREND-AV rendition at 2560×2560; whether that transfers to these files depends on how the rendition was made, which is not established |
| Camera | **MiiS HORUS Scope DEC 200** (Medimaging Integrated Solutions, Taiwan), **hand-held, non-mydriatic**; automatic focus and capture, aiming/capture light set to IR/White LED 3/7 |
| Field of view | 45° |
| Centring | Between the macula and the optic disc, per the paper ("FOV centered between the macula and the optic disc"). The OCULAR README tabulates it as macula-centred |
| Modality | Colour fundus photography |

Participants: mean age 19.9 (19–23), 61% female, mean BMI 22.4; 28 of the 72 photographed eyes with refractive error
(21 myopic, 7 hypermetropic, −4.95 D to +1.5 D). High myopia beyond −5 D was an exclusion. One
participant's eye with a choroidal naevus was excluded; three participants were excluded because
neither eye gave an adequate photograph.

### 3.2 Healthy older — 10 good-quality photographs (+8 rejected)

| | |
| --- | --- |
| Resolution (pixels) | Same camera and stated settings as 3.1; not stated separately |
| Microns per pixel | Unknown |
| Camera | MiiS HORUS Scope DEC 200, hand-held, non-mydriatic |
| Field of view | 45° |
| Centring | As 3.1 |
| Modality | Colour fundus photography |

Seven participants aged 55 to 60 (both eyes of 3, one eye of 4). Two had hypertension controlled
by medication; none had diabetes, coronary or cerebrovascular disease. The authors present this set
as a proof of concept, **not as part of the TREND database proper** — the Zenodo files label it
`HEALTHY OLD`, and the photographs are named `N<n>C_<eye>`.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **One** — a family medicine doctor, verified by an ophthalmologist | Not stated | Binary 8-bit PNG, traced in the VAMPIRE software; 82 tracings (72 young, 10 older). Rejected photographs have none |
| Quality | One ophthalmologist | Per photograph | All 104 graded good or bad against four criteria — third-generation vessels visible around the macula, illumination/blur/contrast, field definition, obvious retinal abnormality — with a free-text reason for every rejection |
| Artery/vein (OCULAR, 2.2) | Not stated | **1024×1024** — a rendition, not the 2560×1920 original | Announced, not yet linked. Derived from OCULARNet's prediction inside TREND's vessel tracing, hand-corrected; classes artery, vein, crossing, uncertain |
| Artery/vein (TREND-AV, in [REYIA](reyia.md)) | One standard | REYIA's rendition (section 5) | 48 photographs; documented on the REYIA page, not distributed by TREND |
| Other labels | — | — | Per photograph: box-counting, lacunarity and multifractal dimensions (D0–D2), vessel percentage area, junction count, total vessel length, end-point count; age group, BMI class, sex, refractive error, alcohol and smoking flags |

The published vessel measurements were computed by the authors from **skeletonised** tracings in
ImageJ (FracLac plugin) and AngioTool, in pixels. They are the authors' figures, not this
repository's.

## 5. Inheritance

- **Reuses images from:** No shared images established — TREND collected its own photographs.
- **Its images are reused by:** **[REYIA](reyia.md)**, as its **TREND-AV** subset of 48 photographs
  with artery/vein maps. *Our finding, 2026-10-12, by file name:* all 48 REYIA keys match TREND file
  names — **41 from the 72 young good-quality photographs and 7 from the 10 older ones**
  (`N3C_R`, `N4C_L`, `N5C_R`, `N9C_R`, `N10C_R`, `N11C_L`, `N11C_R`). So TREND-AV is not a subset of
  the TREND database proper: it mixes in the authors' older comparison set. The OCULAR paper cites
  this TREND paper (its reference 15) for TREND-AV, which agrees.
  **Whether resized:** TREND states 2560×1920; this atlas's REYIA store holds the 48 at **2560×2560**,
  and the OCULAR README tabulates TREND-AV at **1444×1444**. The 2560×2560 frame keeps the width and
  adds height, which would fit padding to a square rather than rescaling, but this repository has not
  compared the two sets of pixels, so the relationship is **not established**. A TREND-AV result is
  measured on REYIA's rendition, not on TREND's files.
- **Announced reuse:** OCULAR's artery/vein layer (2.2) covers the 72 young photographs at
  1024×1024. Once released, 41 photographs will carry **two artery/vein annotations from different
  groups** — TREND-AV's and OCULAR's — which is a chance to compare readers, and a reason not to
  count them as two datasets.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. [OCULARNet](../models/ocularnet.md)
  and [OCULARNet-nano](../models/ocularnet-nano.md) did not train on TREND, and the Plaza 2026 paper
  states its ~1,800 released annotations, TREND's among them, "were not used to either train or
  evaluate OCULAR-Net". But both models **were evaluated on TREND photographs** — through TREND-AV,
  their near out-of-distribution test set for hand-held cameras. This atlas's artery/vein benchmark
  also scores TREND-AV inside [REYIA](reyia.md) (`results/av/*/reyia.csv`).
- **Below a model's measuring grid:** No — 2560×1920 is above every grid in this catalogue. The
  OCULAR artery/vein labels, however, exist only at 1024×1024.
- **What it can answer:** how a model trained on tabletop cameras handles a hand-held,
  non-mydriatic camera; vessel segmentation on young healthy eyes; quality grading, with the
  rejected photographs and their reasons published; and, through the authors' per-photograph
  measurements, whether this repository's fractal and density calculations reproduce theirs on the
  same tracings.

## 7. Known defects

- **The OCULAR README misdescribes TREND.** Its release-list row gives 2560×1960, region BE
  (Belgium) and pathology G (glaucoma). The distributor and the paper give 2560×1920, Montenegro,
  and healthy participants selected for having no chronic disease. The 1960 resembles the paper's
  Table 1 entry for two *other*, proprietary collections taken on the same camera (LOCAL1 and LOCAL2,
  at 2500×1960), which may be where it came from. The same README's TREND-AV row gives region **ME** and pathology **H**
  (healthy), consistent with Montenegro — though its legend defines ME only as macular oedema. Treat
  the README's TREND row as unreliable; the distributor's figures are the authors'.
- **The paper's Table 6 has its group sizes swapped against its labels.** The column headed
  "Old" carries n = 72 and the column headed "Young" carries n = 10, whereas there are 72 young and
  10 older photographs. Which of the two — label or count — is wrong is not stated.
- **Image dimensions not verified.** This repository has not downloaded TREND, so the 2560×1920
  figure is the authors' statement, not a measurement.

No defects in the archive itself recorded as of 2026-10-12. *Our finding, from the Zenodo file
listing and the quality spreadsheet:* the archive's counts — 72, 14, 10 and 8 photographs, 82
tracings, 104 graded rows — match the description and the paper.

## 8. Notes

- **Hand-held and non-mydriatic** is the point of this dataset, not a flaw: illumination and framing
  vary more than on a tabletop camera, and 22 of 104 photographs were rejected. A model scoring well
  on DRIVE or HRF has not shown it can handle these.
- **Healthy and young** means no disease labels and a narrow range of vessel appearance; it is a
  reference for normal, not a test of pathology.
- **TREND, TREND-AV and OCULAR's TREND layer are three different things**: the authors' 104
  photographs with binary tracings; REYIA's 48-photograph artery/vein rendition mixing young and
  older eyes; and OCULAR's announced 1024×1024 artery/vein labels on the 72 young photographs.

---

**Links, licence and access last checked:** 2026-10-12
