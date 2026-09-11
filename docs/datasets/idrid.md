# IDRiD

516 photographs at 4288×2848 from an Indian diabetic-retinopathy screening population, with
diabetic-retinopathy and macular-oedema grades on all of them and **pixel-level lesion, optic disc
and fovea annotations on 81**. It is the highest-resolution dataset in this catalogue after
[HRF](hrf.md), it is CC BY 4.0, and its 81 annotated photographs are the images
[RETA](reta.md) re-annotated for vessels — at a quarter of the size.

## 1. What it is

- **Images:** 516 — 81 of them carrying pixel-level annotations, split 54 train / 27 test by the
  authors.
- **Collected at:** an eye clinic in Nanded, Maharashtra, India.
- **Purpose:** diabetic-retinopathy screening research on an Indian population, with lesion
  segmentation, disease grading and optic-disc/fovea localisation as separate tasks.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://ieee-dataport.org/open-access/indian-diabetic-retinopathy-image-dataset-idrid> — the authoritative copy, behind an IEEE DataPort account. A third-party open mirror is on [Zenodo](https://zenodo.org/records/17219542), DOI [10.5281/zenodo.17219542](https://doi.org/10.5281/zenodo.17219542) |
| Download | **registration** at IEEE DataPort; **direct, no registration** from the Zenodo mirror — whose own description states the uploader "is not the creator of the dataset and only uploads the files". Since IDRiD is CC BY 4.0 the redistribution is permitted, but cite the authors, not the mirror |
| Citation | Porwal P, Pachade S, Kamble R, Kokare M, Deshmukh G, Sahasrabuddhe V, Meriaudeau F. *Indian Diabetic Retinopathy Image Dataset (IDRiD): A Database for Diabetic Retinopathy Screening Research.* Data 2018;3(3):25. DOI: [10.3390/data3030025](https://doi.org/10.3390/data3030025) |
| Licence | **CC BY 4.0** |
| Content | 516 images at 4288×2848, about 1.0 GB across three archives |
| Annotations | DR and macular-oedema grades on all 516; on 81 images, lesion masks (microaneurysms, haemorrhages, hard and soft exudates), optic disc masks and fovea coordinates |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 4288×2848 |
| Microns per pixel | Unknown — not published |
| Camera | Kowa VX-10α, mydriatic |
| Field of view | 50° |
| Centring | Macula-centred |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | Expert annotators | Native | Masks, on all 81 of the segmentation subset |
| Disease | Graded per image | — | Diabetic retinopathy 0–4 and macular-oedema risk 0–2, on all 516 |
| Other labels | — | Native | Four lesion classes on the 81; fovea coordinates |

No vessel annotation ships with IDRiD — that is [RETA](reta.md)'s contribution to the same
photographs.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** **[RETA](reta.md)** — the same 81 segmentation photographs, and the
  same 54/27 split, re-annotated for vessels **at 1024×1024 renditions** rather than the 4288×2848
  originals. RETA therefore holds a downsized copy.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established for training. The AutoMorph paper
  reports IDRiD as the **validation** set for its disc-and-cup model, so it is not fully held out for
  that model.
- **Below a model's measuring grid:** No — far above every grid in [MODELS.md](../MODELS.md).
- **What it can answer:** disc segmentation at native high resolution on an Indian population, under
  a permissive licence; and, paired with RETA, how much a fourfold downsizing costs a vessel
  annotation.

## 7. Known defects

None recorded as of 2026-09-11 — an absence of findings, not a clean bill of health.

## 8. Notes

- IDRiD and RETA together are the only place in this catalogue where the *same* photographs exist at
  two resolutions with annotations at both. That makes the pair unusually well suited to measuring
  what the [grid](../MODELS.md) actually costs.

---

**Links, licence and access last checked:** 2026-09-11
