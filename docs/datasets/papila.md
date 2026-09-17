# PAPILA

488 disc-centred photographs — both eyes of 244 patients — with the **optic disc and the optic cup
outlined by two independent experts**, plus a full clinical record per eye. It is the largest
two-reader disc-and-cup dataset in this catalogue, and the only one that can say what human
disagreement on the cup looks like at scale, which is exactly what a cup-to-disc ratio needs to be
read against.

## 1. What it is

- **Images:** 488 — both eyes of 244 patients: 333 healthy, 87 glaucoma-suspect, 68 glaucoma.
- **Collected at:** Hospital General Universitario Reina Sofía, Murcia, Spain.
- **Purpose:** glaucoma assessment with both eyes and the clinical record of the same patient, so
  that image findings can be read alongside the ophthalmologist's own data.

## 2. Provenance

| | |
| --- | --- |
| Home | figshare, DOI [10.6084/m9.figshare.14798004](https://doi.org/10.6084/m9.figshare.14798004) |
| Download | **direct, no registration** — about 591 MB |
| Citation | Kovalyk O, Morales-Sánchez J, Verdú-Monedero R, Sellés-Navarro I, Palazón-Cabanes A, Sancho-Gómez J-L. *PAPILA: Dataset with fundus images and clinical data of both eyes of the same patient for glaucoma assessment.* Scientific Data 2022;9:291. DOI: [10.1038/s41597-022-01388-1](https://doi.org/10.1038/s41597-022-01388-1) |
| Licence | **GPL 3.0 or later**, as recorded on figshare — a software licence applied to a data release, but what the distributor states, and it carries share-alike obligations a CC BY dataset does not |
| Content | 488 images at 2576×1934, JPEG |
| Annotations | Optic disc and cup contours from **two independent experts**, glaucoma assessment, full clinical record per eye |

### 2.1 How to fetch

```bash
uv run python -m datasets.papila                      # downloads and builds 512 and 1024
uv run python -m datasets.papila --sizes 512,1024,2048
uv run python -m datasets.papila --archive ~/PAPILA.zip
```

**What it downloads:** one 591 MB zip from figshare, checked against its sha256. Nothing here needs
a human.

**What it builds:** 488 photographs at native, 512 and 1024, with the field of view detected from
each frame, and **both experts' disc and cup contours** at every size. The clinical record travels
as this dataset's own manifest columns: `age`, `gender`, `dioptre_1`, `dioptre_2`, `astigmatism`,
`phakic`, `pneumatic`, `perkins`, `pachymetry`, `axial_length`, `vf_md`. Codes stay as the authors
wrote them, except the diagnosis, which is stored as `healthy`, `glaucoma suspect` or `glaucoma`.

**Both eyes of one patient share a `patient` id**, taken from the filename (`RET002OD` and
`RET002OS` are one person), so a split by person is possible and a split by image is not accidental.

**The quality grade is assumed, not published.** PAPILA grades no photograph. The store records
`good` for all 488 with `quality_source` set to `assumed` — this repository's supposition, on the
grounds that every frame here was taken with one camera, disc-centred, and outlined twice over by
ophthalmologists. It is never to be pooled with a dataset's own grade, and what it is useful for is
one question: how much of a sound dataset a quality model would discard.

**Left in the archive:** `ImagesWithContours/`, which is the photographs with the outlines drawn on
them, and `HelpCode/`, which is the authors' example code and their cross-validation folds — an
evaluation protocol rather than something published about an image.

**The resolution is derived from the field angle**, which the authors state as 30°: about 300
microns of retina to the degree, over each photograph's own detected field, which works out near
3.77 µm/px. It is an approximation that ignores eye length, and `resolution_source` says
`field_angle` on every row so nobody mistakes it for a published figure.

## 3. The images

| | |
| --- | --- |
| Resolution (pixels) | 2576×1934, JPEG |
| Microns per pixel | Not published. **Derived from the stated 30° field: ~3.777 µm/px** (per image, since the field's diameter in pixels varies), which is what this dataset's manifest carries |
| Camera | Topcon TRC-NW400, non-mydriatic |
| Field of view | 30° |
| Centring | **Disc-centred** (centred on the papilla) |
| Modality | Colour fundus photography |

This is one of very few datasets in this catalogue where both the camera and its field angle are
stated by the authors rather than inferred.

### 3.1 What this dataset settles about inferred scales

PAPILA is the only dataset in this catalogue where a microns-per-pixel figure can be **checked**
rather than assumed. Its authors state a 30° field, which gives a scale from the field's diameter in
pixels without any assumption about how large an optic disc is; this repository separately infers a
scale for every unscaled dataset from the median disc, taking a typical disc to be 1,800 µm. On
PAPILA both can be computed and compared:

| Derivation | µm/px |
| --- | --- |
| From the stated 30° field | 3.777 (median over the 488 photographs) |
| From the median optic disc, 32 photographs | 4.105 ([evidence](../../results/um_resolution/papila.json)) |

**They agree to 8.7%.** Read the other way: if the field angle is right, PAPILA's median disc is
**1,656 µm** rather than the 1,800 µm the inference assumes — inside the population range for a
disc, and a measure of what that assumption is worth everywhere it cannot be checked. Every
`disc_anchored` figure in this catalogue should be read as good to roughly a tenth.

The field-angle figure is the one PAPILA's manifest carries; the disc-derived one is kept as
evidence and is not written into it.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Optic disc | **Two experts, kept separate** | Native | Contours, published as floating-point coordinates |
| Optic cup | **Two experts, kept separate** | Native | The only two-reader cup annotation of this size here |
| Disease | Three assessments per eye | — | Healthy / suspect / glaucoma |
| Clinical record | — | — | Age, sex, refraction, intraocular pressure, visual-field indices, pachymetry and more |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [REYIA](reyia.md), whose compilation includes PAPILA photographs —
  so scoring both counts some of these images twice.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** [OCULARNet](../models/ocularnet.md) and
  [OCULARNet-nano](../models/ocularnet-nano.md) list PAPILA in their training data. It is **held out**
  of the AutoMorph family's disc-and-cup model, which trained on [REFUGE](refuge.md) and
  [GAMMA](gamma.md), and of the
  [Hugging Face SegFormer](../models/segformer-disc-cup.md), which trained on REFUGE. [RLAD](../models/rlad.md)
  generates from it, so any model augmented with RLAD images has seen these photographs indirectly.
- **Below a model's measuring grid:** No.
- **What it can answer:** genuine generalisation for the disc-and-cup models in this catalogue, and
  the human agreement ceiling those models should be read against. Of everything here it is the best
  candidate for a cup-to-disc ratio comparison.

## 7. Known defects

- The published contour coordinates are floating point; rounding them to pixels costs at most half a
  pixel on a 2576-pixel image, far below the distance between the two experts. Worth knowing, not
  worth worrying about.
- **The archive carries eleven contour files twice.** Beside `RET062OD_cup_exp2.txt` sits
  `RET062OD_cup_exp2 2.txt`, and ten more like it — the duplicate names macOS gives a second copy.
  Every one holds the same coordinates as its original, differing only in line endings, so nothing
  is lost; but code that globs for `*_cup_exp2*.txt` reads eleven cups twice and would weight those
  eleven eyes double in any average. *(This atlas's finding, from the archive downloaded
  2026-09-15; the fetcher matches the exact filename and ignores the copies.)*
- **The archive explains none of its codes.** Its README points at the paper, and its own helper
  code reads the diagnosis column without naming its values. This atlas establishes the legend —
  `0` healthy, `1` glaucoma suspect, `2` glaucoma — by counting: the codes fall 333, 87 and 68,
  which are exactly the counts the paper publishes for those three groups. Anyone assuming the
  obvious order (`1` glaucoma, `2` suspect) has the two glaucoma classes the wrong way round.

## 8. Notes

- Disc-centred at 30° means the disc fills much more of the frame than in a 45° macula-centred
  photograph. A disc model trained on wider fields will see a differently-scaled disc here even
  after resampling to its own grid.

---

**Links, licence and access last checked:** 2026-09-11
