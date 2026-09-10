# REYIA

589 photographs with artery/vein annotation — **compiled from nine other datasets**, not collected.
That makes it the clearest case in this catalogue of why the inheritance question is asked: 153 of
its photographs are already here under their own names, so scoring REYIA and its sources counts the
same eyes twice.

What it genuinely adds is artery/vein colouring on photographs that had none — PAPILA has disc and
cup but no A/V, FIVES has binary vessels but no A/V — plus a new 111-image set.

## 1. What it is

- **Images:** 589 complete image-and-annotation sets (the paper reports 586).
- **Assembled from:** nine sources — [FIVES](fives.md) (75 photographs), [PAPILA](papila.md) (78),
  MESSIDOR, Magrabia, mBRSET, GRAPE, TREND, a re-annotated AV-WIDE, and **ENRICH**, a new 111-image
  set appearing here first.
- **Purpose:** training data for a generative approach to vessel-segmentation generalisation.

## 2. Original publication

- Fhima J, et al. *Enhancing Retinal Vessel Segmentation Generalization via Layout-Aware Generative
  Modelling.* [arXiv:2503.01190](https://arxiv.org/abs/2503.01190)

## 3. Access

- **Home:** Kaggle, shared by link rather than published openly; the canonical slug is
  `fhimjo15/reyia-dataset`.
- **Direct download:** **No.** The dataset is private and link-shared: the Kaggle API answers 403
  for an account that has not been granted access, and the web endpoint wants a browser session
  rather than an API key. The archive has to be fetched by hand once.
- **Arrives as:** a zip with the images, A/V annotations and a per-row source attribution.

## 4. Licence

- **The compilation:** **MIT**, as stated on the Kaggle record.
- **The images:** **each source keeps its own terms, and they are stricter.** mBRSET is
  PhysioNet-credentialed, MESSIDOR is research-only, PAPILA is GPL-3.0. Anything redistributed from
  REYIA inherits the strictest of the nine, not REYIA's own MIT — a mirror cannot grant rights its
  depositor never had.

## 5. The images

Mixed by construction — nine sources, nine cameras, nine resolutions. The per-source detail belongs
to those datasets' own pages; what matters here is that no single row of camera, field or resolution
describes REYIA.

| | |
| --- | --- |
| Resolution (pixels) | **Mixed** — inherited from nine sources |
| Microns per pixel | Unknown |
| Camera | **Mixed** — nine sources |
| Field of view | **Mixed**, including a wide-field set (AV-WIDE) |
| Centring | Mixed |
| Modality | Colour fundus photography |

Annotation was done with the same tool used for [Leuven-Haifa](leuven-haifa.md).

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | One standard | Per-source native size | The dataset's contribution |
| Other labels | — | — | A source-dataset attribution per photograph, which is what makes the overlap traceable |

## 7. Inheritance

- **Reuses images from:** **FIVES (75), PAPILA (78), MESSIDOR, Magrabia, mBRSET, GRAPE, TREND and
  AV-WIDE** — 478 of its 589 photographs come from elsewhere; only the 111-image ENRICH set is new.
  No resizing was established, but each source arrives at its own native size.
- **Its images are reused by:** None established.

## 8. Use as a benchmark

- **Catalogued models trained on these images:** None established directly. But because its
  photographs come from datasets that *are* training data for several models here, a REYIA score is
  **partly in-sample for reasons that have nothing to do with REYIA** — which is exactly the trap
  the per-photograph source attribution exists to expose.
- **Below a model's measuring grid:** Mixed, by source.
- **What it can answer:** artery/vein accuracy across nine cameras at once, provided the overlapping
  153 photographs are excluded when its sources are also scored.

## 9. Known defects

- **Not downloadable programmatically** (section 3), which makes reproducible use awkward.
- The paper's count (586) and the archive's (589) disagree.
- 153 photographs duplicate other datasets in this catalogue; pooling without exclusion
  double-counts them.

## 10. Notes

- A compilation is not a camera. REYIA's value is breadth of appearance in one place, and its risk is
  that breadth looking like independence.

---

**Links, licence and access last checked:** 2026-09-11
