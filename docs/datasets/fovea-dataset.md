# FOVEA (dataset)

40 eyes photographed **twice — before and during surgery** — with vessel and optic disc annotations
from two readers on each image. Nothing else in this catalogue pairs a clinic photograph with an
intraoperative view of the same eye, which is what makes 80 images interesting: it is a controlled
change of imaging conditions with the anatomy held fixed.

Its licence is the most restrictive here, and the restriction is the kind that affects processing,
not just redistribution.

## 1. What it is

- **Images:** 80 in total — 40 preoperative photographs and 40 frames extracted from
  intraoperative video, one per eye, from 40 patients.
- **Collected at:** Moorfields Eye Hospital, London.
- **Purpose:** to support registration and vessel/disc analysis between preoperative and
  intraoperative retinal views.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare; code at <https://github.com/rvimlab/FOVEA> |
| Download | **direct** from the figshare record |
| Citation | *FOVEA: Preoperative and intraoperative retinal fundus images with optic disc and retinal vessel annotations.* Scientific Data 2025. DOI: [10.1038/s41597-025-04965-2](https://doi.org/10.1038/s41597-025-04965-2) |
| Licence | **CC BY-NC-ND 4.0** — attribution, **non-commercial**, and **no derivatives** |
| Content | 40 preoperative images at 1934×1960 and 40 intraoperative frames at 1080×1920, plus the source video clips |
| Annotations | Vessel and optic disc masks, from **two readers** on all 80 images — 160 raw annotations, 320 binary masks |

**The NoDerivatives clause is the practical problem.** Every pipeline in this catalogue processes
images on import — cropping to the field of view, resampling onto a measuring grid, re-encoding —
which is plausibly the creation of a derivative work. Under `ND` such a copy may not be
redistributable, and depending on how "derivative" is read it may be a problem even for a private
analysis copy. Read the licence before building anything on it.

## 3. The images

Two subcollections, and they are different instruments.

### 3.1 Preoperative — 40 images

| | |
| --- | --- |
| Resolution (pixels) | 1934×1960 |
| Microns per pixel | Unknown — not published |
| Camera | Topcon 3D OCT-1000 |
| Field of view | Not stated |
| Centring | Posterior pole |
| Modality | Colour fundus photography |

### 3.2 Intraoperative — 40 frames

| | |
| --- | --- |
| Resolution (pixels) | 1080×1920 — **portrait-shaped video frames** |
| Microns per pixel | Unknown |
| Camera | Zeiss Lumera 700 with RESIGHT, through a surgical microscope |
| Field of view | Not stated; determined by the surgical viewing system |
| Centring | Whatever the surgeon was viewing |
| Modality | **Surgical microscope video, not fundus photography.** Illumination, magnification and colour balance are all different, and the frames are video-compressed |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **Two, kept separate** | Native | On both the preoperative and intraoperative images |
| Optic disc | **Two, kept separate** | Native | As above |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of every model here.
- **Below a model's measuring grid:** No for the preoperative images; the intraoperative frames are a
  different problem entirely.
- **What it can answer:** whether a vessel or disc model survives a change of imaging system on the
  *same* eye, with two readers on both sides so the human ceiling is available for each. It is the
  cleanest paired-modality design in this catalogue.

## 7. Known defects

- The `ND` clause (section 2) may block the ordinary processing that any measurement pipeline
  performs — a licence problem rather than a data problem, and the only one of its kind here.

## 8. Notes

- Same eye, two instruments, two readers each. As an experimental design for separating imaging
  effects from anatomy it is the best thing in this catalogue; the licence is what stops it being
  widely used.

---

**Links, licence and access last checked:** 2026-09-11
