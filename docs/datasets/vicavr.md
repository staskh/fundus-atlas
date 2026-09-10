# VICAVR

58 disc-centred photographs with arteries and veins labelled by **three experts**, and — unusually —
**vessel calibres recorded at several radii from the optic disc**. Most artery/vein datasets give a
mask and leave the widths to be computed; this one publishes the widths, which makes it one of the
few places a calibre measurement can be checked against a human's.

## 1. What it is

- **Images:** 58.
- **Collected at:** the VARPA group, University of A Coruña, Spain.
- **Purpose:** arteriovenous ratio computation, which is why the calibres rather than only the masks
  are published.

## 2. Provenance

| | |
| --- | --- |
| Home | [VARPA ophthalmology page](http://www.varpa.org/research/ophtalmology.html). The `varpa.es` form of that URL, cited in much of the literature, now returns 404 |
| Download | **request** — email the group for an authentication password. No fee; the request is asked for statistical purposes only |
| Citation | **No canonical dataset publication established.** Papers using VICAVR typically cite the VARPA page itself; the group asks that VICAVR be cited in any paper using it |
| Licence | **Research use**, with no standard Creative Commons text and no statement permitting commercial use |
| Content | 58 images at 768×584 |
| Annotations | Artery/vein labels and **vessel calibres at several radii from the disc**, from three experts |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 768×584 |
| Microns per pixel | Unknown — not published |
| Camera | Topcon TRC-NW100 |
| Field of view | Not stated |
| Centring | Disc-centred |
| Modality | Colour fundus photography |

At 768×584 it sits only just above [DRIVE](drive.md)'s 565×584, so a width measured here spans few
pixels and inherits the same caution: see section 6.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | **Three experts** | Native | Labels near the disc rather than a dense whole-image map |
| Other labels | **Three experts** | Native | **Calibres at several radii from the disc** — the measurement itself, not just the mask |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of every model here.
- **Below a model's measuring grid:** **Effectively yes.** 768×584 is below the 912 vessel grid and
  the 1024 of the newer models, so measurement happens on an upsampled image and a vessel a few
  pixels wide carries most of the signal.
- **What it can answer:** whether a pipeline's [calibre](../biomarkers/vessel-calibre.md) agrees with
  three experts' measured widths at defined radii — a check only this dataset and
  [INSPIRE-AVR](inspire-avr.md) support.

## 7. Known defects

- **No canonical citation**, which makes attribution awkward and provenance harder to trace than for
  any other entry here.
- Access is by personal email, so availability depends on a group's continued responsiveness.

## 8. Notes

- Three readers *and* published calibres is a rare combination. Its size and low resolution mean it
  should be used to check a method's agreement with humans, not to rank methods.

---

**Links, licence and access last checked:** 2026-09-11
