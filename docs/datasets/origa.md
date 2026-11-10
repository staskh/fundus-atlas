# ORIGA

650 photographs from a population-based cohort with optic disc and cup masks — and, rarely, **the
cup-to-disc ratio its own graders recorded**, published as a column alongside the masks. That makes
ORIGA the one dataset in this catalogue whose geometry can be checked against an independent
published number rather than only against itself.

## 1. What it is

- **Images:** 650 — 168 glaucomatous, 482 normal.
- **Collected at:** the **Singapore Malay Eye Study**, a population-based cohort, so the imaging is
  not selected for photogenic discs. Its 26% glaucoma rate reflects sampling for a benchmark rather
  than a screening prevalence.
- **Purpose:** an online database for glaucoma analysis, published with grader-recorded measurements.

## 2. Provenance

| | |
| --- | --- |
| Home | Historically distributed on request through the study; no reliable open host was established |
| Download | **no** from the authors. In practice it arrives inside the third-party Kaggle bundle [`arnavjain1/glaucoma-datasets`](https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets), which also carries [G1020](g1020.md) and [REFUGE](refuge.md) |
| Citation | Zhang Z, Yin FS, Liu J, Wong WK, Tan NM, Lee BH, Cheng J, Wong TY. *ORIGA-light: An online retinal fundus image database for glaucoma analysis and research.* IEEE EMBC 2010:3065–3068. DOI: [10.1109/IEMBS.2010.5626137](https://doi.org/10.1109/IEMBS.2010.5626137) |
| Licence | **Research use**, historically request-based. No Creative Commons grant was established, and the licence field on the Kaggle bundle at <https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets> is the **uploader's**, not the study's |
| Content | 650 images. As the Kaggle bundle carries them: **159 sizes**, 2213–2764 wide and 2044–2048 tall, cropped by the uploader (section 7) |
| Annotations | Optic disc and cup masks, **`ExpCDR`** (the graders' vertical cup-to-disc ratio), glaucoma label, eye side, an A/B subset split |

### 2.1 How to fetch

```bash
uv run python -m datasets.origa --archive ~/dataset/glaucoma-datasets.zip
uv run python -m datasets.fetch_disc_estimation --dataset origa   # then, required
uv run python -m datasets.fetch_um_resolution --dataset origa     # and the scale
```

**Where this atlas's copy comes from: the third-party Kaggle bundle
<https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets>, not the Singapore Malay Eye Study's own
distribution**, which was not used. Everything this atlas measures on ORIGA — the store, the disc
estimates, the inferred scale — is measured on the uploader's copy, which is cropped (section 7).
`build.json` records the bundle's URL beside the path of the archive built.

**This fetcher never downloads.** ORIGA has no open host, and the Kaggle bundle it arrives in needs
an account, so the archive must be obtained by hand and handed over with `--archive`. Run without
it, the fetcher says so and stops rather than looking for a way round the login.

- **Reads:** the bundle as downloaded, about 6 GB, **where it lies** — it is not unpacked. The same
  file builds [G1020](g1020.md) and [REFUGE](refuge.md) with their own fetchers.
- **Builds:** all 650 photographs, each with its field-of-view mask and the disc and cup contours,
  in `crop/`. Both structures come out of the one published mask, which holds **0 outside the
  disc, 1 for the rim and 2 for the cup**: the cup is 2 and the disc is 1 and 2 together.
- **Reads only the folders named exactly `Images` and `Masks`.** The bundle also carries
  `Images_Cropped`, `Images_Square`, `Masks_Cropped` and `Masks_Square`, which are the uploader's
  own derived copies, and they are left alone.
- **Not built:** everything in the bundle that is not ORIGA, and `Semi-automatic-annotations`, 650
  MATLAB files that neither this page nor the bundle describes (section 7).
- **Found, not addressed:** the bundle is a third party's packaging and may be rearranged at any
  time, so the fetcher looks for whichever CSV carries an `ExpCDR` column (`OrigaList.csv` today)
  and matches photographs and masks to its rows by name. A bundle with no such sheet fails saying
  so, rather than building nothing and calling it success.
- **Subsets:** `a` and `b`, 325 each, the study's own division. Papers commonly use A to train and
  B to test, but the authors published them as sets rather than as a split, and that is how they
  are recorded.
- **Extra columns:** `expert_cdr`, the graders' own vertical cup-to-disc ratio.
- **Grouping:** `eye` comes from the sheet; no patient identity is published, so two photographs of
  one person cannot be told from two of different people.
- **Checks itself.** Every build recomputes the vertical cup-to-disc ratio — the cup's height over
  the disc's — from the stored contours and compares it with `expert_cdr`; the result is written
  into `build.json` under `verification`. On the build of 2026-11-10 all 650 agree, with a median
  difference of 0.000 and the largest 0.003. Had the mask encoding been read the wrong way round,
  this is where it would show.
- **Scale:** none is published, so `fetch_um_resolution` is a required follow-on (section 3).

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | As carried by the bundle: **159 sizes**, 2213–2764 wide and 2044–2048 tall — the uploader cropped each frame's sides (section 7). Set A spans 2300–2691 wide, set B 2213–2764 |
| Microns per pixel | Not published. **Inferred: 4.728 µm/px for set A and 4.655 µm/px for set B** — the medians of 325 and 322 optic discs estimated one per photograph, agreeing to 1.6% of each other ([evidence](../../results/um_resolution/origa.json)). Two photographs of set B, `018` at 2764 wide and `496` at 2213×2044, are too far from the rest in size to share their scale and carry **none**. Good to roughly a tenth (§9 of the `fetch-um-resolution` skill); a camera scale, not a per-eye calibration |
| Camera | Unknown make; the cohort's own retinal photography protocol |
| Field of view | Not stated |
| Centring | Disc-visible posterior pole |
| Modality | Colour fundus photography |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | Graders of the study | Native | Masks |
| Optic cup | Graders of the study | Native | Masks |
| Disease | One label per eye | — | Glaucoma 168 / normal 482 |
| Other labels | — | — | **`ExpCDR`**, the graders' vertical cup-to-disc ratio; eye side; an A/B subset split |

`ExpCDR` is the reason to reach for ORIGA. Measuring the vertical extents of the shipped masks
reproduces it closely — to within 0.003 on all 650, median 0.000, in the check every build of
this atlas's store runs (section 2.1) — which means the masks and the published ratio are consistent, and that a pipeline's own
[cup-to-disc ratio](../biomarkers/landmarks.md) can be compared against a human-recorded
value rather than against another algorithm's mask.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established. Its usual distribution bundles it with G1020 and
  REFUGE, which is packaging, not shared photographs.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [VascX disc](../models/vascx-disc.md), on all 650 (VascX paper, Table 1). Held out of every
  other model in this catalogue.
- **Below a model's measuring grid:** No.
- **What it can answer:** whether a computed cup-to-disc ratio agrees with a clinician's recorded
  one, on a population cohort. Nothing else here supports that check.

## 7. Known defects

Findings from building the store on 2026-11-10, from the Kaggle bundle. They are this atlas's
observations of that copy, not statements by the study.

- **The bundle's photographs are not the study's original frames.** The uploader's own sheet,
  `origa_info.csv`, marks every one `Cropped: True`, and they come in 159 different widths. The
  heights are unchanged at 2048 (one at 2044), so they look **cropped at the sides, not resized**:
  a pixel should cover the same retina as in the original, but the frames are not the original
  frames, and coordinates published against the originals would need an offset nobody records.
  This page's earlier figure of "2426–2616 wide" matches neither the bundle nor any source found.
- **`Semi-automatic-annotations`** holds 650 MATLAB files that no documentation in the bundle
  explains. They are not read; the masks are.
- **Disc estimation found no disc on photograph `511`.** That is the
  [SegFormer model](../models/segformer-disc-cup.md) failing, not the dataset; the published
  outline is there and is built.

## 8. Notes

- The published ratio is the asset. A disc/cup model can be evaluated against masks anywhere; being
  able to evaluate the *biomarker* against a human's number is what makes this dataset worth the
  awkward access route.

---

**Links, licence and access last checked:** 2026-11-10
