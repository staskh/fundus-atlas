# VEVIO

32 retinal images of **premature infants**, taken not with a fundus camera but from **video recorded
through an indirect ophthalmoscope** during bedside screening for retinopathy of prematurity (ROP):
16 single video frames and 16 wider composite pictures ("mosaics") stitched from several frames of
the same videos. An ophthalmologist traced every visible vessel on each image. A second group, the
authors of [OCULAR](../projects/ocularnet.md), has since coloured those vessels as arteries and veins.

The images look like fundus photographs in a file browser and are not: they are low-resolution,
video-compressed frames with reflections from the hand-held lens, of an infant's eye rather than an
adult's. That is their value — no other entry in this catalogue tests a model on that input — and the
reason they must not be pooled with camera photographs.

## 1. What it is

- **Images:** 32 — 16 manually selected video frames and 16 corresponding mosaics, from 16
  different premature infants, all of the **right eye**.
- **Collected at:** Duke Medical Center, Durham, North Carolina, USA, during ROP bedside examinations
  between August and October 2010, under Duke University Institutional Review Board approval with
  parental consent.
- **Purpose:** a benchmark for automatic vessel segmentation in video indirect ophthalmoscopy (VIO),
  where a physician wears a head-mounted camera during the standard ROP examination. The vessels'
  width and tortuosity at the back of the eye are what decide "plus disease", a marker of severe ROP.

## 2. Provenance

### 2.1 Original release — images and vessel tracings

| | |
| --- | --- |
| Home | Duke Vision and Image Processing (VIP) Laboratory, <https://people.duke.edu/~sf59/Estrada_BOE_2012.htm> (listed under "Indirect Ophthalmology Software" on the lab's [software page](https://people.duke.edu/~sf59/software.html)) |
| Download | **direct, no registration** — `VEVIO.7z` at <https://people.duke.edu/~sf59/Datasets/VEVIO.7z> (the page links the older `http://www.duke.edu/~sf59/…` address, which redirects there), verified serving, about 7.3 MB. The page describes it as "the full dataset including the original files with and without marking". The MATLAB code is a separate archive, `VESSEL_segmentation_2012.7z` |
| Citation | Estrada R, Tomasi C, Cabrera MT, Wallace DK, Freedman SF, Farsiu S. *Exploratory Dijkstra forest based automatic vessel segmentation: applications in video indirect ophthalmoscopy (VIO).* Biomedical Optics Express 2012;3(2):327–339. DOI: [10.1364/BOE.3.000327](https://doi.org/10.1364/BOE.3.000327) · [PMC3269849](https://pmc.ncbi.nlm.nih.gov/articles/PMC3269849/) |
| Licence | **Not stated.** The page carries only "COPYRIGHT (C) 2012 DUKE UNIVERSITY". The paper is open access under CC BY-NC-ND 3.0, but that licence covers the article, not the images |
| Content | 32 images: 16 video frames recorded at 720×576, and 16 mosaics whose size is not stated |
| Annotations | Supplies one ophthalmologist's binary vessel tracing per image |

The paper says the dataset and code were made "publically available"; it does not say on what terms.
A copyright line with no grant is not permission to redistribute.

### 2.2 OCULAR artery/vein layer

| | |
| --- | --- |
| Home | The "Release of New Artery-Vein Annotations" section of the OCULAR README, <https://github.com/GonzaloPlaaza/OCULAR#release-of-new-artery-vein-annotations> (commit `3f13a8b5`, 2026-10-09) |
| Download | **no public route established.** The README links a Google Drive folder, <https://drive.google.com/drive/folders/1b0ntI6mkpC9VQgcgp5R9ZThmc-e_gsTX>, which on 2026-10-12 redirected to a Google sign-in page rather than showing its contents. The README promises the release "upon paper publication"; the paper is published (below) |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030. No DOI; stable URL <https://papers.miccai.org/miccai-2026-sat/OMIA_030> — see [Plaza 2026](../papers/plaza-2026.md). The README names no separate publication for the annotations |
| Licence | **Not stated.** The OCULAR repository has no LICENSE file (GitHub API: no licence detected); OCULARNet's MIT licence is on its weights, not on these annotations |
| Content | The same 32 images; the README lists them as "640x480 + mosaics" — see section 3 |
| Annotations | Supplies artery, vein and crossing labels, plus an "uncertain" class, drawn at 1024×1024 |

How the layer was made, as the README describes it: OCULARNet predicted artery, vein and crossing
at 1024×1024; the original vessel tracing (2.1) was resized to 1024×1024 by bicubic interpolation
and thresholded; model pixels outside the tracing were removed and traced vessels the model missed
were given its next most probable class; a person then corrected errors by painting over the result
in the authors' own browser tool, which also offers an "uncertain" class; finally the result was
masked by the tracing again. The README does not say who corrected the VEVIO images or how many
people did.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | **Frames: 720×576** as recorded, per the paper. The OCULAR README lists **640×480** — the authors' figure and OCULAR's disagree, and this atlas has not opened the archive to check (section 7). **Mosaics: not stated** by either source |
| Microns per pixel | Unknown — not published, and not meaningful as one number: an indirect ophthalmoscope's magnification depends on the hand-held condensing lens and the infant's eye, and each mosaic is a composite of differently registered frames |
| Camera | **Keeler Wireless Digital Indirect Ophthalmoscope** (Keeler Instruments, Broomall, PA), head-mounted; video saved as interlaced, compressed AVI, 24-bit colour |
| Field of view | **Unknown from the original source** — the paper gives no angle. The OCULAR README states 30° (OCULAR's claim, unconfirmed). The mosaics are by construction wider than a single frame |
| Centring | Not stated by the authors; frames were captured when the video "was well-centered and in focus". The OCULAR README classes the set as macula-centred |
| Modality | **Video indirect ophthalmoscopy, not colour fundus photography.** Frames are video stills with interlacing, compression, lens reflections, saturation near the lens rim and motion blur; mosaics are computed composites of five frames each, not photographs at all |

### 3.1 Video frames — 16 images

One frame per infant, screen-captured by the bedside assistant when the live feed looked centred and
in focus, the best of each set then chosen by an ophthalmologist (MTC).

### 3.2 Mosaics — 16 images

One per infant, made by the authors' automatic mosaicing method (Estrada et al., *Enhanced video
indirect ophthalmoscopy (VIO) via robust mosaicing*, Biomedical Optics Express 2011;2:2871–2887,
[PMC3191451](https://pmc.ncbi.nlm.nih.gov/articles/PMC3191451/)): from the thousands of frames in
each video the method kept the 20 highest-scoring, and the authors hand-picked five of those to give
the widest field. The mosaic frames were chosen automatically, not from the manual captures in 3.1.
A mosaic has been filtered, colour-adjusted and blended by software before anyone traced it, so a
model scored on it is scored on that software's output as much as on the retina.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **One** — MTC, a practising ophthalmologist | Native | All visible vessels traced in Adobe Photoshop CS3 with a pressure-sensitive pen, so the stroke width follows the vessel width; one binary mask per image. The original release (2.1) |
| Artery/vein | OCULAR's model, corrected by hand; **number of correctors not stated** | **1024×1024** — larger than a 720×576 frame, so the extra pixels are interpolated, not extra detail | Classes artery, vein, crossing, uncertain. Bounded by the original tracing, so it can never contain a vessel MTC did not trace. Whether the frames were padded or stretched to the square is not stated. OCULAR's layer (2.2), not the original authors' |

The paper splits the 32 images into 10 for training and 22 for testing (11 frames and 11 mosaics),
keeping each infant's frame and mosaic on the same side. Disease grades (ROP stage, plus disease) are
**not** published per image.

## 5. Inheritance

- **Reuses images from:** No shared images established. Within the dataset, each mosaic and its
  frame come from the **same infant's same video**, so the 32 images are 16 eyes, not 32.
- **Its images are reused by:** None established. The OCULAR artery/vein layer (2.2) annotates
  these photographs without adding images, and is recorded here rather than as a dataset of its
  own.
- **Related, not shared:** [WIDE](wide.md) comes from the same Duke laboratory and first author
  (Estrada, Tomasi, Farsiu) but is a different population (adults, healthy and AMD), a different
  device (Optos 200Tx) and a different period (2010–2014). No images are shared between the two.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. VEVIO appears in the OCULAR
  README only in the artery/vein release list, not in the tables of datasets OCULARNet was trained
  or tested on, so it is held out for [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md). Its OCULAR artery/vein labels were, however, seeded
  by OCULARNet's own predictions, so scoring OCULARNet against them is **not** an independent test.
- **Below a model's measuring grid:** **Yes** for the frames — 720×576 sits below the 912 and 1024
  grids in [MODELS.md](../MODELS.md), and a field-of-view square is at most 576 pixels across, close
  to the atlas's 512-pixel floor ([DATASETS.md](../DATASETS.md) section 5.4). Unknown for the
  mosaics.
- **What it can answer:** how a model trained on adult camera photographs behaves on infant eyes and
  on handheld video — a far out-of-distribution test — and whether a frame and the mosaic built from
  the same video give the same vessels.

## 7. Known defects

- **The paper's counts disagree with themselves** (the authors' text, PMC3269849): it describes 32
  images, 16 frames and 16 mosaics, and a 10 + 22 split consistent with that, but section 3.1.3
  speaks of "the corresponding ten mosaics" and section 3.1.4 of tracing "each of the twenty VIO
  images". Which count the archive holds has not been checked by this atlas.
- **Frame resolution differs between sources:** 720×576 per the paper, 640×480 per the OCULAR README.
  Not checked against the archive.
- **One reader only:** the same ophthalmologist selected the frames and traced them, so there is no
  second tracing against which to measure human agreement.

## 8. Notes

- ROP screening is done in infants, often with an indirect ophthalmoscope rather than a fundus
  camera; that is the setting these images represent, and nothing else in this catalogue does.
- Reading a vessel width from these images in microns is not supported by anything the authors
  published.

---

**Links, licence and access last checked:** 2026-10-12
