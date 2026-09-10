# Chákṣu

1,345 photographs from an Indian glaucoma population with the optic disc and cup outlined by **five
expert ophthalmologists each**, plus five independent glaucoma decisions per eye. After
[RIGA](riga.md)'s six readers it is the deepest multi-reader disc/cup annotation in this catalogue,
and it is CC BY 4.0 — the more permissive of the two.

It also spans three cameras, one of which produces **portrait** photographs, taller than wide, which
nothing else here does.

## 1. What it is

- **Images:** 1,345 across three devices.
- **Collected at:** Indian eye clinics; annotated by five expert Indian ophthalmologists.
- **Purpose:** a glaucoma-specific database with per-expert boundaries and decisions retained rather
  than merged.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.20123135](https://doi.org/10.6084/m9.figshare.20123135) |
| Download | **direct, no registration** |
| Citation | Kumar JRH, Seelamantula CS, et al. *Chákṣu: A glaucoma specific fundus image database.* Scientific Data 2023;10:70. DOI: [10.1038/s41597-023-01943-4](https://doi.org/10.1038/s41597-023-01943-4) — note the published author correction |
| Licence | **CC BY 4.0** |
| Content | 1,345 images across three cameras — see section 3 |
| Annotations | Optic disc and cup boundaries from **five experts**, and five independent glaucoma decisions, all kept separate |

## 3. The images

Three subcollections, one per camera, and they are not the same shape.

### 3.1 Remidio — 1,074 images

| | |
| --- | --- |
| Resolution (pixels) | **2448×3264 — portrait**, taller than wide |
| Microns per pixel | Unknown — not published |
| Camera | Remidio |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography |

Portrait orientation is worth checking before any pipeline's cropping stage: code written for
landscape photographs may crop the wrong axis silently.

### 3.2 Forus 3Nethra Classic — 126 images

| | |
| --- | --- |
| Resolution (pixels) | 2048×1536 |
| Microns per pixel | Unknown |
| Camera | Forus 3Nethra Classic |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography |

### 3.3 Bosch handheld — 145 images

| | |
| --- | --- |
| Resolution (pixels) | 1920×1440 |
| Microns per pixel | Unknown |
| Camera | Bosch handheld |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography, handheld |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **Five, kept separate** | Native | Per-expert boundaries |
| Optic cup | **Five, kept separate** | Native | Per-expert boundaries |
| Disease | **Five independent decisions per eye** | — | Glaucoma; the five may disagree, and that disagreement is preserved |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — **held out of every model here**.
- **Below a model's measuring grid:** No.
- **What it can answer:** a five-reader human ceiling on disc, cup and the glaucoma decision itself,
  on an Indian population and three cameras including a handheld — with a permissive licence, which
  RIGA's CC BY-NC does not offer.

## 7. Known defects

- The paper carries a published author correction; cite the corrected version.
- Mixing the three cameras without separating them mixes a portrait 2448×3264 photograph with a
  landscape 1920×1440 one.

## 8. Notes

- Of the multi-reader disc/cup datasets here, this is the one to reach for first: five readers, three
  cameras, CC BY 4.0, and held out of everything.

---

**Links, licence and access last checked:** 2026-09-11
