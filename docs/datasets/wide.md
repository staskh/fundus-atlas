# WIDE (AV-WIDE)

30 **ultra-wide-field** retinal images with artery and vein labels from two independent raters — the
original release behind the "AV-WIDE" subset that circulates inside [REYIA](reyia.md) and, through
it, inside several models' training and test sets. At 200° it captures the whole retina including the
far periphery, where almost no other dataset in this catalogue looks at all.

The distinction between this release and the copy in circulation matters: the originals are
3900×3072, and the widely used AV-WIDE subset is **26 of them at 829×1531** — under a quarter of the
linear detail.

## 1. What it is

- **Images:** 30, each from a different individual — healthy eyes and eyes with age-related macular
  degeneration showing geographic atrophy, drusen, or fibrotic scarring from neovascular AMD.
- **Collected at:** Duke University Medical Center, between August 2010 and October 2012 and again
  between November 2013 and July 2014.
- **Purpose:** to support artery/vein classification across the *whole* vasculature, peripheral
  vessels included, which narrow-field photographs cannot show.

## 2. Provenance

| | |
| --- | --- |
| Home | <https://people.duke.edu/~sf59/Estrada_TMI_2015_dataset.htm> (the lab's [software page](https://people.duke.edu/~sf59/software.html) lists it among its releases) |
| Download | **direct, no registration** — `AV_Paper_TMI_2015.zip` at <http://www.duke.edu/~sf59/Datasets/AV_Paper_TMI_2015.zip>, verified serving. The archive holds the images, the annotations and a MATLAB interface, plus graph annotations for the other datasets analysed in the paper |
| Citation | Estrada R, Allingham MJ, Mettu PS, Cousins SW, Tomasi C, Farsiu S. *Retinal artery-vein classification via topology estimation.* IEEE Transactions on Medical Imaging 2015;34(12):2518–2534. DOI: [10.1109/TMI.2015.2443117](https://doi.org/10.1109/TMI.2015.2443117) · [PMC4685460](https://pmc.ncbi.nlm.nih.gov/articles/PMC4685460/) |
| Licence | **Research and educational purposes only.** "Commercialization/redistribution of the images is prohibited." Copyright 2015 Duke University; the citation above is required, and users are asked to destroy copies and notify the lab if any identifiers are discovered |
| Content | 30 uncompressed TIFF images at 3900×3072 |
| Annotations | Artery/vein labels from **two independent raters**, plus vascular graph annotations |

The redistribution prohibition is worth reading twice, because the copy most people actually use is
a redistribution — see section 5.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **3900×3072**, uncompressed TIFF — the Optos device's highest setting. The paper's own analysis downsamples by a factor of two, to 1950×1536 |
| Microns per pixel | Unknown — not published, and unusually hard to state for a 200° field, where the projection means a micron-per-pixel figure varies across the image |
| Camera | **Optos 200Tx** ultra-wide-field device |
| Field of view | **200°** — the widest in this catalogue by a factor of four |
| Centring | Whole-retina, not centred on disc or macula |
| Modality | **Ultra-wide-field scanning imaging, not standard colour fundus photography.** The peripheral geometry is heavily distorted by the projection, and vessel appearance differs from a 45° photograph of the same eye |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Artery/vein | **Two independent raters, kept separate** | Native | The second rater — a fellowship-trained medical retina specialist — is taken as ground truth, and the first therefore gives a human agreement figure |
| Other labels | — | Native | Vascular **graph** annotations: the topology, not just the pixels, which is what the paper's method estimates and what nothing else here publishes |
| Disease | Per eye | — | Healthy or AMD, with the AMD subtype described |

## 5. Inheritance

- **Reuses images from:** No shared images established — an original collection.
- **Its images are reused by:** **[REYIA](reyia.md)**, which carries **26 of the 30 photographs,
  resized to 829×1531** and distributed under the name **AV-WIDE**. That copy is what reaches
  [OCULARNet](../models/ocularnet.md)'s far out-of-distribution test set. A result reported on
  "AV-WIDE" is therefore a result on a downsized rendition, redistributed by a third party under a
  licence that prohibits redistribution.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None — but [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) use the AV-WIDE copy as a **far out-of-distribution
  test**, which is the right use for it.
- **Below a model's measuring grid:** No at native resolution — far above every grid in
  [MODELS.md](../MODELS.md). The circulating AV-WIDE copy at 829×1531 is a different matter, and
  sits below the 1024 grid on one axis.
- **What it can answer:** how an artery/vein method behaves on the peripheral retina, and — through
  the graph annotations — whether it reconstructs the vascular *tree* rather than merely the pixels.
  Both are questions no other dataset here supports.

## 7. Known defects

- **The circulating copy is not this dataset.** AV-WIDE as redistributed is 26 of 30 images at about
  a fifth of the pixel count, which no paper reporting an "AV-WIDE" score tends to mention.
- The licence prohibits redistribution, and the copy in [REYIA](reyia.md) is a redistribution. That
  is the authors' matter to raise, not this atlas's, but anyone building on the REYIA copy should
  know the terms attached to the originals.

## 8. Notes

- Ultra-wide-field imaging is where retinal photography is heading clinically, and this is the only
  ultra-wide dataset here with vessel-level annotation. It is also the clearest example in the whole
  catalogue of a dataset whose reputation rests on a degraded copy of itself.
- The graph annotations deserve more use than they get: [bifurcation angles](../biomarkers/bifurcation-angle.md)
  and [junction counts](../biomarkers/junction-counts.md) are measured against nothing at all in this
  catalogue apart from [IOSTAR](iostar.md)'s junction points, and this release publishes a full tree.

---

**Links, licence and access last checked:** 2026-09-11
