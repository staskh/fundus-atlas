# RAV (Rotterdam Artery-Vein)

206 photographs from the Rotterdam Study with artery and vein annotation, published by the group
behind [VascX](../projects/vascx.md) — which makes it the dataset most likely to be **in-sample for
VascX** and held out of everything else. It is drawn from a population cohort of adults over 40
rather than a clinic series, and it is deliberately mixed in image quality.

Its licence is stated twice, and the two statements contradict each other.

## 1. What it is

- **Images:** 206, already cropped to the circular field and resized to 1024×1024.
- **Collected at:** the **Rotterdam Study** — four population cohorts of adults aged 40 and over —
  with oversampling from the AMD-Life and MYST studies. Annotated by the EyeNED Reading Center.
- **Purpose:** artery/vein reference data for population-scale retinal vascular analysis.

## 2. Provenance

| | |
| --- | --- |
| Home | DataverseNL, DOI [10.34894/9OIMWY](https://doi.org/10.34894/9OIMWY) — [record](https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/9OIMWY) |
| Download | **direct, no registration** for the public 206. Additional images exist under a separate agreement on request |
| Citation | Vargas Quiros JD, Liefers B, van Garderen KA, Vermeulen JP, EyeNED Reading Center, Klaver CCW. *Rotterdam artery-vein segmentation (RAV) dataset.* [arXiv:2512.17322](https://arxiv.org/abs/2512.17322), 2025 |
| Licence | **CC BY-NC 4.0 — attribution, non-commercial**, per the authors' own README inside the archive. ⚠️ **DataverseNL's structured licence field on the same record says `CC0-1.0`**, which would waive both conditions. See below |
| Content | 206 images at 1024×1024, pre-cropped and resized |
| Annotations | Artery/vein segmentation, with mixed image quality by design |

**The licence is stated twice and the two disagree.** The authors' README says CC BY-NC 4.0; the
repository's own metadata field says CC0-1.0 — public domain, no attribution, no non-commercial
clause. Nothing available settles which the depositors meant, so treat the **stricter** statement as
binding: a non-commercial clause written by the authors is not waived by a metadata field.

### 2.1 How to fetch

```bash
uv run python -m datasets.rav                                        # downloads and builds the crop
uv run python -m datasets.rav --archive ~/Downloads/doi-10.34894-9oimwy.zip   # the zip fetched by hand
uv run python -m datasets.fetch_disc_estimation --dataset rav
uv run python -m datasets.fetch_um_resolution --dataset rav
```

One zip of about 220 MB from DataverseNL, which builds it on request — so it carries no fixed
checksum, and the manifest's per-image checksums are the record of what was built. **DataverseNL
refuses automated requests from some networks**; where the download is refused, fetch the record's
"Download all" zip in a browser and pass it with `--archive`. The archive is read where it lies.

It builds all 206 photographs with three binary masks each — `artery`, `vein` and `vessels` — read
from the layers the annotators painted: **red is the artery layer, blue the vein layer, green the
unknown layer**, and a crossing is a pixel painted on both the artery and the vein layer. An unknown
vessel is in `vessels` and in neither class. `vessels` is the union of the three layers; the archive
publishes no independent vessel tracing.

**The subset is the camera**, read from `metadata.csv` and written as lowercase words —
`topcon_trc_50ex_dxc_950p` and eight more — because every photograph is a 1024×1024 rendition and the
camera is the only thing left that tells two magnifications apart. The split is `unspecified`: the
authors publish none. Two dataset-specific columns carry the participant: `patient_age`, in years
when photographed, and `patient_sex`, `M` or `F`, as the metadata writes them. 201 of the 206
photographs keep their frame, being already cropped square to the field; the other five are
cropped to their detected field.

The authors publish no scale. The two follow-on commands infer one per camera; see section 3.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 1024×1024 — **the authors' rendition**, cropped to the circular field and resized, not a camera native |
| Microns per pixel | Not published. **Inferred per camera**, each the median of every optic disc estimated with it ([evidence](../../results/um_resolution/rav.json)): TOPCON TRC-50EX **10.202 µm/px** (68 discs), 3D OCT-2000 **11.833** (60), 3D OCT-1000 Mark II **11.439** (27). The six other cameras hold 6 to 10 photographs each — too few discs for a median — and carry no scale, so 160 of the 206 photographs have one. Good to roughly a tenth (§9 of the `fetch-um-resolution` skill); a camera scale on the authors' rendition, not a per-eye calibration |
| Camera | **Nine Topcon models, named per photograph** in `metadata.csv`: TRC-50EX + DXC-950P 71, 3D OCT-2000 FA Plus 61, 3D OCT-1000 Mark II 28, DRI OCT Triton plus – Fundus 10, 3D OCT-1000 8, DRI OCT Triton plus 8, TRC-50VT analog 7, TRC-50IX + D7100 7, TRC-50DX + D7100 6 |
| Field of view | Not stated per image |
| Centring | Mixed |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | EyeNED Reading Center | 1024×1024 | **Three layers** — artery, vein, and vessels the grader could not classify — painted separately, so a crossing is on both the artery and the vein layer. **Not drawn from nothing**: per the README, graders started from a vessel segmentation model's output, corrected it, then coloured it and checked each tree's connectivity |
| Quality | — | — | **Mixed on purpose** — the selection includes poor-quality photographs rather than excluding them, which is unusual and useful |

## 5. Inheritance

- **Reuses images from:** the **Rotterdam Study** image archive, which is not itself a public dataset.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** none stated explicitly, but [VascX vessels](../models/vascx-vessels.md) and [VascX artery/vein](../models/vascx-artery-vein.md) train on
  352 and 215 unpublished Rotterdam Study images (VascX paper, Table 1) — these photographs' own cohort, annotated by
  the same group. Whether the two overlap is not established, so **RAV is treated as in-sample for
  VascX** unless its authors say otherwise, and as held out of the AutoMorph family.
- **Below a model's measuring grid:** No, at 1024 — which is also VascX's own grid.
- **What it can answer:** artery/vein accuracy on a population cohort rather than a clinic series,
  across a realistic quality range. For VascX, it answers a regression question rather than a
  generalisation one.

## 7. Known defects

- **Contradictory licence statements** (section 2), unresolved.
- The images are a pre-processed rendition, so a measurement in pixels is on the authors' grid, not
  the camera's.
- **The annotation began as a model's output.** The README says the vessel tracing was a vessel
  segmentation model's, "trained on publicly-available datasets", refined by hand before the arteries
  and veins were coloured. Which model is not named; if it was VascX's own, a VascX score here is
  measured against its own starting point. *Our reading of the README, not a stated fact.*
- **Two camera names may be one camera.** `TOPCON DRI OCT Triton plus` (8) and `TOPCON DRI OCT
  Triton plus - Fundus` (10) are kept as two subsets because the metadata writes them differently;
  pooled, they would hold 18 photographs, enough for a scale. *Our observation; not established.*

## 8. Notes

- Population cohorts and clinic series differ systematically — in age, in disease prevalence and in
  photograph quality. RAV is the only artery/vein dataset here from a population cohort, which makes
  it valuable and makes its likely in-sample status for VascX unfortunate.

---

**Links, licence and access last checked:** 2026-10-12
