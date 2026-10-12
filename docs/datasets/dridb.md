# DRiDB

50 colour photographs of diabetic patients' retinas from a university hospital in Zagreb, Croatia,
each marked by **five independent experts** for the lesions of diabetic retinopathy — microaneurysms,
haemorrhages, hard and soft exudates — and for the blood vessels, the optic disc and the macula.
It is small and low-resolution, but five readers per image on both lesions and anatomy is rare. A
second group, the authors of [OCULAR](../projects/ocularnet.md), has since added artery/vein
colouring to all 50 photographs.

**Not to be confused with [DRIMDB](drimdb.md)**, a Turkish image-quality collection whose name
differs by one letter. DRiDB is the **D**iabetic **R**etinopathy **i**mage **D**ata**B**ase from the
University of Zagreb; the two share no photographs and answer different questions.

## 1. What it is

- **Images:** 50. The distributor's page does not give a split by disease. Two third-party
  summaries disagree: one says 36 show signs of diabetic retinopathy and 14 show none (openmedlab
  Awesome-Medical-Dataset, <https://github.com/openmedlab/Awesome-Medical-Dataset/blob/main/resources/DRiDB.md>);
  a 2025 review says the collection consists entirely of patients diagnosed with diabetic
  retinopathy (Conquer et al., *Sensors* 2025;25(18):5658, DOI:
  [10.3390/s25185658](https://doi.org/10.3390/s25185658)). The describing paper's full text, which
  would settle it, is behind the publisher's paywall and was not read. **Unknown.**
- **Collected at:** a university hospital in Zagreb, Croatia, with the Image Processing Group of the
  University of Zagreb, Faculty of Electrical Engineering and Computing (FER).
- **Purpose:** in the authors' words, "to help scientists from around the world to test and develop
  new image processing methods for early diabetic retinopathy detection" — a reference for
  automated diabetic-retinopathy screening, with every image carrying both lesion and anatomy
  labels.

## 2. Provenance

### 2.1 DRiDB — images and the original five-expert annotations

| | |
| --- | --- |
| Home | Image Processing Group, University of Zagreb FER, <https://ipg.fer.hr/ipg/resources/image_database> |
| Download | **request, then agreement** — the page says "Please send an e-mail to Pavle Prentašić to request access to the dataset". There is no direct URL. The address is hidden behind a script on the page rather than printed |
| Citation | Prentašić P, Lončarić S, Vatavuk Z, Benčić G, Subašić M, Petković T, Dujmović L, Malenica-Ravlić M, Budimlija N, Tadić R. *Diabetic retinopathy image database (DRiDB): a new database for diabetic retinopathy screening programs research.* 8th International Symposium on Image and Signal Processing and Analysis (ISPA 2013), Trieste, 2013, pp. 711–716. DOI: [10.1109/ISPA.2013.6703830](https://doi.org/10.1109/ISPA.2013.6703830) |
| Licence | As stated by the distributor: "can be used, free of charge, for research and educational purposes. Copy, redistribution, and any unauthorized commercial use is prohibited." Users must cite the publication above. No standard licence |
| Content | 50 images at 720×576, uncompressed BMP |
| Annotations | Supplies microaneurysms, haemorrhages, hard exudates, soft exudates, blood vessels, optic disc and macula, each marked by five independent experts |

The distributor's page gives the paper's pages as **704–709**. IEEE Xplore and Crossref give
**711–716**, and the row above follows them.

The licence matters more than usual here because a second group now publishes annotations for
these photographs (section 2.2). DRiDB's own terms forbid copying and redistribution, so anyone
using that layer still has to get the photographs from Zagreb.

### 2.2 OCULAR artery/vein layer

| | |
| --- | --- |
| Home | The OCULAR repository, section "Release of New Artery-Vein Annotations", <https://github.com/GonzaloPlaaza/OCULAR> (README read at commit `3f13a8b5`, 2026-10-09) |
| Download | **direct, no registration** — a publicly viewable Google Drive folder, <https://drive.google.com/drive/folders/1QL7H_jVmFdTszZWGSpVUS2H2lqmvxya_>. It lists 50 files, `OrigImg0001.png` to `OrigImg0050.png` (our listing, 2026-10-12; contents not opened) |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030. <https://papers.miccai.org/miccai-2026-sat/OMIA_030> — see [Plaza 2026](../papers/plaza-2026.md). No DOI established |
| Licence | **Not stated.** The OCULAR repository has no LICENSE file, and the Drive folder carries no terms. The photographs these labels describe stay under DRiDB's terms (section 2.1) |
| Content | Labels for the same 50 photographs. No photographs are supplied |
| Annotations | Supplies artery, vein and crossing classes, plus an "uncertain" class, drawn at 1024×1024 |

The OCULAR authors say they release these annotations "upon paper publication". The paper has been
published, and the folder is public. Their README tabulates DRiDB as **50 images, macula-centred,
45°, 576×720, region "CR", diabetic retinopathy**. 576×720 is the same size as the distributor's
720×576, written height first. "CR" is the ISO code for Costa Rica. Croatia's is HR.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 720×576 (as published) |
| Microns per pixel | Unknown — not published. No inferred figure, because this atlas has no fetcher for DRiDB |
| Camera | Zeiss VISUCAM 200 |
| Field of view | 45° |
| Centring | Macula-centred **per the OCULAR README**. The distributor's page does not say. **Unknown** from the original source |
| Modality | Colour fundus photography, RGB, 8 bits per channel, uncompressed BMP |

The camera, field of view, size and file format come from summaries of the paper. One is the 2018
survey by Asiri et al. (*Deep Learning based Computer-Aided Diagnosis Systems for Diabetic
Retinopathy: A Survey*, <https://arxiv.org/abs/1811.01238>, Table 2). The others are the openmedlab
page and the 2025 review cited in section 1. All three agree. The paper itself was not read.

According to the openmedlab summary, the photographs were "selected and captured by medical
experts", range "from minimal signs of DR to visible new fragile blood vessels", and "exhibit varying
degrees of image noise".

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **Five, independently** | Native (720×576) | Whether the five are distributed as separate files or merged is **Unknown**. The openmedlab summary says "each image has a set of ground truth images". The 2025 review calls them masks "of several doctors to establish a consensus" |
| Optic disc | Five, independently | Native | Same caveat on separate or merged. No cup |
| Macula | Five, independently | Native | Marked as a region. Whether it is a point or an outline is not established |
| Lesions — microaneurysms, haemorrhages, hard exudates, soft exudates | Five, independently | Native | Pixel-level areas of findings |
| Disease | Unknown | — | No per-image grade of diabetic retinopathy was established from the distributor. See section 1 for the two third-party claims that disagree |
| Artery/vein (OCULAR layer, section 2.2) | One standard, machine-drafted and corrected by hand | **1024×1024**, an upsized rendition of the 720×576 photographs | Classes: artery, vein, crossing, uncertain. Drafted by [OCULARNet](../models/ocularnet.md), then pruned to the dataset's own binary vessel annotation (resized to 1024×1024 and thresholded). Missing vessels were filled from the model's next most likely class, then corrected with brush strokes in the authors' annotation tool. **Which of DRiDB's five vessel annotations was used as the reference is not stated** |

The OCULAR layer was drawn on a grid **larger than the photographs**: 720×576 enlarged to 1024×1024
changes the aspect ratio as well as the scale. Its masks do not carry more detail than the
photographs. To lay them over the native images, they must be resized back, and that resampling is
the user's own.

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established as a separate image collection. The
  [OCULAR](../projects/ocularnet.md) artery/vein layer (section 2.2) annotates these photographs
  without republishing them, and is catalogued here as a layer rather than a dataset.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. DRiDB does not appear in the
  OCULAR README's training, in-distribution test or out-of-distribution test tables, which list what
  [OCULARNet](../models/ocularnet.md) was developed and evaluated on (our reading at commit
  `3f13a8b5`). It appears only in the list of datasets given new annotations. No other catalogued
  model page names DRiDB.
- **Below a model's measuring grid:** **Yes** — 720×576 is below the 912 vessel grid and the 1024
  grid of the newer models, so scores here are computed on enlarged images.
- **What it can answer:** with the OCULAR layer, artery/vein accuracy on a Croatian Zeiss camera
  that no catalogued model trained on. With the original labels, how five experts disagree on
  vessels, disc and lesions — if the five are distributed separately (section 4).

## 7. Known defects

- **Page numbers differ between distributor and publisher.** The distributor's citation gives pp.
  704–709. IEEE Xplore and Crossref give 711–716.
- **Third-party summaries disagree on the disease split** (section 1), and the openmedlab page's
  own metadata table contradicts its text. The text says 50 images at 720×576. The table says 648
  files in three categories, sized from 75×100 to 2272×1704. That table describes something other
  than DRiDB as distributed and should not be relied on.
- **The OCULAR README labels the region "CR"**, which is Costa Rica's code. The photographs are
  from Croatia (HR).
- None recorded in the original distribution itself as of 2026-10-12. This atlas has not obtained
  the archive.

## 8. Notes

- The access route is an e-mail to one named person, which makes availability depend on that
  person. Anyone planning to use DRiDB should allow for a slow or absent reply.
- The OCULAR artery/vein layer is freely downloadable, but it is useless without the photographs,
  and those come only by request under no-redistribution terms. Getting this dataset is as hard as
  its harder route, the e-mail request.

---

**Links, licence and access last checked:** 2026-10-12
