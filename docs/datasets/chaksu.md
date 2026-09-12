# Chákṣu

1,345 photographs from an Indian glaucoma population with the optic disc and cup outlined by **five
expert ophthalmologists each**, plus five independent glaucoma decisions per eye. After
[RIGA](riga.md)'s six readers it is the deepest multi-reader disc/cup annotation in this catalogue,
and it is CC BY 4.0 — the more permissive of the two.

It also spans three cameras, one of which produces **portrait** photographs, taller than wide, which
nothing else here does.

## 1. What it is

- **Images:** 1,345 across three devices.
- **Collected at:** Indian eye clinics; annotated by five expert Indian ophthalmologists.
- **Purpose:** a glaucoma-specific database with per-expert boundaries and decisions retained rather
  than merged.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.20123135](https://doi.org/10.6084/m9.figshare.20123135) |
| Download | **direct, no registration** |
| Citation | Kumar JRH, Seelamantula CS, et al. *Chákṣu: A glaucoma specific fundus image database.* Scientific Data 2023;10:70. DOI: [10.1038/s41597-023-01943-4](https://doi.org/10.1038/s41597-023-01943-4) — note the published author correction |
| Licence | **CC BY 4.0** |
| Content | 1,345 images across three cameras — see section 3 — published as two archives, `Train.zip` and `Test.zip` |
| Annotations | Optic disc and cup boundaries from **five experts**, and five independent glaucoma decisions, all kept separate. The archives also carry four fusions of the five outlines — mean, median, majority and STAPLE — and each expert's own cup-to-disc measurements |

### 2.1 How to fetch

```bash
uv run python -m datasets.chaksu                          # downloads and builds 512 and 1024
uv run python -m datasets.chaksu --sizes 512,720,1024     # any sizes a model needs
```

- **Downloads:** `Train.zip` (8.6 GB) and `Test.zip` (2.7 GB) from figshare. No account, no form.
  Both are read where they lie: the per-expert masks are uncompressed TIFFs that come to about
  70 GB unpacked, and each is read once and turned into a polygon.
- **Builds:** the photograph, its field-of-view mask, and **ten contours per image** — disc and cup
  from each of the five experts — in one `contours/<key>.csv` per photograph, at `native/` plus
  each requested size.
- **Not built:** the four fused masks (mean, median, majority, STAPLE), because each is a function
  of the five outlines the store keeps; the per-expert cup-to-disc measurements, for the same
  reason; and the annotation overlays, which are the photographs with a boundary drawn on them.
- **Subsets:** `bosch`, `forus` and `remidio`, one per camera, because they are not the same shape
  and Remidio is portrait.
- **Splits:** `train` and `test`, as the two archives divide them.
- **Per-reader values:** `labels.csv` holds all five glaucoma decisions under the field `disease`,
  with the published majority as the `consensus` reader; `multi_reader` names `disease` on every
  row. The verdicts are lowercased and the misspelling in section 7 is read as the verdict it is.
- **Grouping:** none. The dataset publishes no patient identity or laterality, so `patient`,
  `visit` and `eye` are empty.
- **Peculiarities:** the archive's folder capitalisation varies between experts, so the masks are
  indexed from what is in the archive rather than addressed by a composed path; the column holding
  the agreed verdict is headed differently in the two archives, so it is found by shape rather than
  by name (section 7).
- **Trace quality:** each outline is scored against the mask it came from, and a score below 0.95
  is recorded in the row's `notes`. Three of the 13,450 masks fall below it — all of them broken in
  the archive, not in the tracing (section 7). A faithful trace scores about 0.98.

The contours were checked against the dataset's own arithmetic rather than by eye. Chákṣu publishes
each expert's cup-to-disc ratios alongside their outlines, so the vertical ratio recomputed from the
stored polygons can be compared with the number the authors report for the same expert and the same
photograph. Over **6,721 expert-image pairs** the median difference is **+0.0003**, with 93% inside
0.01 and 98.8% inside 0.05. The handful outside that are the broken masks in section 7.

## 3. The images

Three subcollections, one per camera, and they are not the same shape.

### 3.1 Remidio — 1,074 images

| | |
| --- | --- |
| Resolution (pixels) | **2448×3264 — portrait**, taller than wide |
| Microns per pixel | Unknown — not published |
| Camera | Remidio |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography |

Portrait orientation is worth checking before any pipeline's cropping stage: code written for
landscape photographs may crop the wrong axis silently.

### 3.2 Forus 3Nethra Classic — 126 images

| | |
| --- | --- |
| Resolution (pixels) | 2048×1536 |
| Microns per pixel | Unknown |
| Camera | Forus 3Nethra Classic |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography |

### 3.3 Bosch handheld — 145 images

| | |
| --- | --- |
| Resolution (pixels) | 1920×1440 |
| Microns per pixel | Unknown |
| Camera | Bosch handheld |
| Field of view | Not stated |
| Centring | Disc-visible |
| Modality | Colour fundus photography, handheld |

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **Five, kept separate** | Native | Per-expert boundaries, published as binary masks at full resolution |
| Optic cup | **Five, kept separate** | Native | As above |
| Disease | **Five independent decisions per eye**, plus a published majority | — | Two verdicts only: `NORMAL` and `GLAUCOMA SUSPECT`. Not a severity grade |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** None established.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established — **held out of every model here**.
- **Below a model's measuring grid:** No.
- **What it can answer:** a five-reader human ceiling on disc, cup and the glaucoma decision itself,
  on an Indian population and three cameras including a handheld — with a permissive licence, which
  RIGA's CC BY-NC does not offer.

## 7. Known defects

- The paper carries a published author correction; cite the corrected version.
- Mixing the three cameras without separating them mixes a portrait 2448×3264 photograph with a
  landscape 1920×1440 one.
- **Two of the five experts misspell the verdict.** They write `GLAUCOMA  SUSUPECT` — a doubled
  space and a transposition — where the other three write `GLAUCOMA SUSPECT`. Counting the raw
  strings turns one verdict into two categories and makes those two experts look like they never
  agree with the rest.
- **The archive's own capitalisation is inconsistent.** One expert's folder is `Bosch/cup`,
  another's `Bosch/Cup`. Code that composes the path rather than listing what is there finds
  nothing for some of the five, and silently reports fewer readers than the dataset has.
- **The decision files name each photograph twice over**, as `Image101.jpg-Image101-1.jpg`, and the
  Remidio files use a `.tif` extension for photographs stored as `.JPG`. Match on the name before
  the first hyphen, without its extension.
- **The column holding the agreed verdict is not always called the same thing.** In `Train.zip` it
  is `Majority Decision`; in `Test.zip` the Forus and Remidio files head it `Glaucoma Decision`.
  Code that looks for the word *majority* silently loses the consensus for 109 photographs — a
  third of the test half — and leaves them looking ungraded.
- **One published cup-to-disc measurement is `NaN`** among the 7,450 in the per-expert files.
- **A few expert masks are outlines rather than filled regions, and broken ones at that.** Expert 2's
  disc for `Image145` (Bosch, train) is 38 disconnected fragments whose largest piece is 777 pixels,
  against about 39,000 for the same disc drawn by the other experts. Two more are flagged in the
  built store's `notes`: expert 3's disc on `Image162` (train) and on `p28_image1` (test). Anything
  taking the largest connected component of those masks gets a shape that is not the optic disc.

## 8. Notes

- Of the multi-reader disc/cup datasets here, this is the one to reach for first: five readers, three
  cameras, CC BY 4.0, and held out of everything.

---

**Links, licence and access last checked:** 2026-09-11
