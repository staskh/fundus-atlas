# UoA-DR

200 photographs with a vessel mask, an optic disc boundary **and centre**, and a fovea centre on
every image, plus diabetic-retinopathy severity on the international clinical scale. That
combination — vessels and disc and fovea on the same eye — is what an end-to-end pipeline needs, and
only [MAPLES-DR](maples-dr.md) and [HRF](hrf.md) otherwise offer it here.

Access is the obstacle: a signed licence, negotiated case by case.

## 1. What it is

- **Images:** 200.
- **Collected at:** three Indian hospitals — Al-Salama Eye Hospital, Dr Tony Fernandez Eye Hospital
  and Giridhar Eye Institute — curated at the University of Auckland.
- **Purpose:** diabetic-retinopathy analysis with the anatomical landmarks a full pipeline needs.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare / University of Auckland, DOI [10.17608/k6.auckland.5985208.v3](https://doi.org/10.17608/k6.auckland.5985208.v3) |
| Download | **request, then a signed agreement.** Not a click: email the investigators from an institutional address, sign their licence, and receive a private link. About 500 MB |
| Citation | Chalakkal RJ, Abdulla WH, et al. *University of Auckland Diabetic Retinopathy Database (UoA-DR).* Hosted at the DOI above |
| Licence | **Custom signed agreement**, case by case, research use. The restrictions are in a licence PDF attached to the record — read it before planning anything |
| Content | 200 images at 2124×2056 |
| Annotations | Vessel mask, optic disc boundary and centre, fovea centre, DR severity |

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 2124×2056 |
| Microns per pixel | Unknown — not published |
| Camera | Not stated |
| Field of view | Not stated |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | Reference standard; reader count not stated | Native | — |
| Optic disc | Reference standard | Native | **Boundary and centre** — the centre is what a zone-based measurement needs |
| Disease | Per eye | — | DR severity on the International Clinical Diabetic Retinopathy scale |
| Other labels | — | Native | **Fovea centre** — a second landmark, so a disc-to-fovea axis can be built |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — held out of every model here.
- **Below a model's measuring grid:** No.
- **What it can answer:** held-out vessel accuracy *and* a disc boundary *and* a fovea on the same
  200 eyes — enough to build the [disc-to-fovea axis](../biomarkers/disc-fovea-distance.md) that
  VascX's region conventions depend on, and to check a whole pipeline rather than one stage.

## 7. Known defects

- The signed-agreement route makes reproducibility awkward: a result cannot be verified by anyone who
  has not negotiated their own access.

## 8. Notes

- Vessels, disc, disc centre and fovea on one photograph is the rarest annotation combination in this
  catalogue. If access were easier this would be among the most useful entries here.

---

**Links, licence and access last checked:** 2026-09-11
