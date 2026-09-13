# ADAM

1,200 photographs released for the ISBI 2020 Automatic Detection challenge on Age-related Macular
degeneration, annotated four ways at once: whether the eye has AMD, where the optic disc is as a
pixel mask, where the fovea is as a coordinate, and where the AMD lesions are — drusen, exudates,
haemorrhages and scars — again as pixel masks. Few datasets carry a disease label, a landmark and
two kinds of segmentation on the same photographs.

It is the only collection in this catalogue built around **age-related macular degeneration**.
Everything else here is diabetic retinopathy, glaucoma, or nothing in particular, which makes ADAM
the one place a measurement can be asked whether it moves with a macular disease rather than a
vascular one.

## 1. What it is

- **Images:** 1,200 in the challenge as a whole. The openly circulated, labelled portion is
  **Training400** — 400 photographs, the ones named `A0001.jpg` onward, with the optic disc masks
  and fovea coordinates. What the other 800 carry publicly could not be established (section 2).
- **Collected at:** Chinese clinical sources, released by the challenge organisers at Baidu and
  collaborating hospitals; the challenge was a satellite event of ISBI 2020 in Iowa City.
- **Purpose:** to benchmark AMD detection and the characterisation that goes with it, across four
  tasks: detecting AMD, detecting and segmenting the optic disc, localising the fovea, and detecting
  and segmenting lesions.

## 2. Provenance

| | |
| --- | --- |
| Home | The challenge, <https://amd.grand-challenge.org/> |
| Download | **registration, and no single working route.** Three exist and each has a catch — see below. In practice the data reaches most people through the Baidu AI Studio copy at <https://ai.baidu.com/broad/download?dataset=amd>, which redirects to a PaddlePaddle AI Studio dataset page and needs a Baidu account |
| Citation | Fang H, Li F, Fu H, Sun X, Cao X, Lin F, Son J, Kim S, et al. *ADAM Challenge: Detecting Age-Related Macular Degeneration From Fundus Images.* IEEE Transactions on Medical Imaging 2022;41(10):2828–2847. DOI: [10.1109/TMI.2022.3172773](https://doi.org/10.1109/TMI.2022.3172773) · [arXiv:2202.07983](https://arxiv.org/abs/2202.07983) |
| Licence | **Not stated** anywhere this atlas could reach. The grand-challenge pages that would carry terms require sign-in, and the IEEE DataPort record the organisers cite for the dataset holds no files |
| Content | 1,200 photographs at two sizes — 2124×2056 and 1444×1444 — see section 3 |
| Annotations | AMD label per eye; optic disc masks; fovea coordinates; lesion masks for drusen, exudates, haemorrhages, scars and others |

**The three routes, and why none of them is simply a download.** The organisers' own citation points
at IEEE DataPort, [10.21227/dt4f-rt59](https://doi.org/10.21227/dt4f-rt59) — that record says
*Subscription Required* and, checked on 2026-09-13, also says **"Files have not been uploaded for
this dataset"**, so the citable route carries nothing. The challenge site's own *Download* page
returns not-found and its *Details* page returns forbidden to anyone not signed in and admitted to
the challenge. What remains is the Baidu AI Studio copy, which the
[Fundus Image Toolbox](../models/fit-fovea-od.md) points its users at and which requires a Baidu
account.

## 3. The images

Two cameras, and the sizes are the way to tell them apart.

| | |
| --- | --- |
| Resolution (pixels) | **2124×2056** for 824 of the 1,200, and **1444×1444** for the other 376 |
| Microns per pixel | Unknown — not published |
| Camera | Two devices, not named per image in anything this atlas could read; the two resolutions correspond to them |
| Field of view | Not stated |
| Centring | Macula-centred, as a dataset about macular disease would be |
| Modality | Colour fundus photography |

The per-size counts come from the arithmetic the Fundus Image Toolbox's authors published when they
normalised a competitor's fovea-localisation error by average image size, and they sum to 1,200.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Disease | Not stated | — | AMD against non-AMD, per eye. The AMD images are the `A`-prefixed files |
| Optic disc | Not stated | Native | Pixel masks, distributed as `.bmp` under `Disc_Masks`. **Not every image has one**: some masks are entirely blank, which is the dataset's way of saying no disc was annotated in that photograph — see section 7 |
| Fovea | Not stated | Native | Coordinates, not a mask |
| Lesions | Not stated | Native | Pixel masks for drusen, exudates, haemorrhages and scars, among others |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established among catalogued datasets.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** the
  [Fundus Image Toolbox fovea and disc locator](../models/fit-fovea-od.md), which pools ADAM with
  [REFUGE](refuge.md) and [IDRiD](idrid.md). It uses **265 of the 400** labelled photographs — the
  ones whose disc mask is not blank — so a score for that model on ADAM is in-sample.
- **Below a model's measuring grid:** No. At 2124×2056 and 1444×1444 it is above every measuring
  grid in this catalogue.
- **What it can answer:** whether anything measured here behaves differently in **age-related
  macular degeneration**, which no other catalogued dataset can ask. It is also one of the few
  places where a disc segmenter and a fovea locator can be scored on the same photographs.

## 7. Known defects

- **The citable route holds no data.** The organisers cite IEEE DataPort for the dataset; that
  record requires a subscription *and* reports that no files were ever uploaded (checked
  2026-09-13). A reader following the citation reaches nothing.
- **The challenge's own download and details pages are closed** to anyone not signed in and
  admitted, so the terms of use cannot be read without an account — which is why the licence row
  above says not stated rather than naming one.
- **Some optic disc masks are blank.** The Fundus Image Toolbox's preparation notebook explicitly
  looks for masks that are uniformly 255 and sets those images aside, which is how its ADAM
  contribution falls from 400 photographs to 265. Code that reads every mask as an annotation will
  train on 135 images whose disc is nowhere.

---

**Links, licence and access last checked:** 2026-09-13
