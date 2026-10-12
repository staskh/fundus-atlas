# ARIA (dataset)

> **Not the ARIA software.** This page is the **ARIA image collection** from Liverpool — *Automated
> Retinal Image Analysis*. The MATLAB vessel-measurement program by Peter Bankhead that is also
> called ARIA (*Automated Retinal Image Analyzer*) is a different thing, catalogued at
> [ARIA (project)](../projects/aria.md). They share a name and nothing else.

143 colour fundus photographs of adults from Liverpool, in three groups — 23 people with
age-related macular degeneration (AMD), 59 people with diabetes and 61 healthy controls — with every
photograph's blood vessels traced by **two independent graders**, and the optic disc and fovea
outlined on the diabetic and control photographs. It is one of the few older sets with a second
vessel reader, and one of very few with AMD eyes. The photographs are small (768×576) and its original
web page is gone, though its archives can still be downloaded. A second group,
[OCULAR](../projects/ocularnet.md), has since added artery/vein labels to all 143.

## 1. What it is

- **Images:** 143 — 23 AMD, 59 diabetic, 61 healthy control. All subjects adult. The groups are by
  subject, not a disease grading: "diabetic" means a person with diabetes, not a stated level of
  retinopathy.
- **Collected at:** St Paul's Eye Unit, Royal Liverpool University Hospital Trust, and the
  Department of Eye and Vision Science, University of Liverpool, UK, under the ARIA project (Liverpool
  Regional Ethics Committee number 04/Q1502/2).
- **Purpose:** the ARIA project aimed at an automated image capture and analysis platform that could
  flag people at risk of eye disease — diabetic retinopathy and AMD named — at the point of image
  capture in the community. The vessel tracings made it a vessel-segmentation reference set.

## 2. Provenance

### 2.1 ARIA — photographs, vessel tracings, disc and fovea outlines

| | |
| --- | --- |
| Home | Originally the *ARIA online* page of the Foundation for the Prevention of Blindness (St Paul's Eye Appeal), `http://www.eyecharity.com/aria_online.html` — **now gone** (HTTP 404, checked 2026-10-12). The page survives in the Internet Archive, e.g. the capture of 2015-01-02: <https://web.archive.org/web/20150102052201/http://www.eyecharity.com/aria_online.html> |
| Download | **direct, no registration** — eight zip archives that the lost page linked to, still served from the University of Liverpool at `http://pcwww.liv.ac.uk/~yzheng/aria/`: photographs in `aria_a_markups.zip`, `aria_c_markups.zip`, `aria_d_markups.zip`; vessel tracings in `aria_a_markup_vessel.zip`, `aria_c_markup_vessel.zip`, `aria_d_markup_vessel.zip`; disc and fovea in `aria_c_markupdiscfovea.zip`, `aria_d_markupdiscfovea.zip`. All eight answered HTTP 200 on 2026-10-12 (about 88 MB together, last modified January 2014). The directory itself is not listable (403), so the file names have to be known |
| Citation | Farnell DJJ, Hatfield FN, Knox P, Reakes M, Spencer S, Parry D, Harding SP. *Enhancement of blood vessels in digital fundus photographs via the application of multiscale line operators.* Journal of the Franklin Institute 2008;345(7):748–765. DOI: [10.1016/j.jfranklin.2008.04.009](https://doi.org/10.1016/j.jfranklin.2008.04.009). The distributor asks that **both** this and Zheng Y, Hijazi MHA, Coenen F. *Automated "disease/no disease" grading of age-related macular degeneration by an image mining approach.* Investigative Ophthalmology & Visual Science 2012;53(13):8310–8318. DOI: [10.1167/iovs.12-9576](https://doi.org/10.1167/iovs.12-9576) be cited by anyone using an image |
| Licence | **not stated.** The archived page grants no licence; it asks for the two citations above "if you use any image of this dataset for research purposes", and marks its pages "© Dr Yalin Zheng, St Paul's Eye Unit and University of Liverpool". Research use with citation is what the page contemplates; nothing permits redistribution or commercial use |
| Content | 143 photographs, uncompressed TIFF, 768×576 |
| Annotations | Supplies vessel tracings by two independent observers on all 143, kept separate; optic disc and fovea outlines on the 120 control and diabetic photographs |

The distributor's page was maintained by Dr Yalin Zheng (contact given as `yzheng@liv.ac.uk`), was
"available from 2006" and "last reviewed on the 7th January 2014". The archives' own modification
dates are 7–8 January 2014, matching that review.

**Why it looks unobtainable.** OCULAR's README, asked where to download ARIA, links a ResearchGate
question titled *How can I find the ARIA (Automatic Retinal Image Analysis) Dataset?* rather than a
distributor
(<https://www.researchgate.net/post/How_can_I_find_the_ARIA_Automatic_Retinal_Image_Analysis_Dataset>;
ResearchGate refused our fetch, so the answers there were not read). The page that indexed the
archives is gone. *Our finding, 2026-10-12:* the archives behind it are not — the eight URLs above
were taken from the archived page and each still serves its zip. Nothing guarantees they stay up; a
personal university directory is the most fragile kind of host.

### 2.2 OCULAR — artery/vein labels

| | |
| --- | --- |
| Home | The OCULAR repository, <https://github.com/GonzaloPlaaza/OCULAR>, section "Release of New Artery-Vein Annotations" |
| Download | **direct, no registration** — a public Google Drive folder, <https://drive.google.com/drive/folders/1VnjsKo7SCTfC7t4N7wBhGz9qf2KprC3s> |
| Citation | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A. *Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation.* MICCAI 2026 Satellite Events, OMIA workshop, paper OMIA_030 — [Plaza 2026](../papers/plaza-2026.md) |
| Licence | **not stated** — the OCULAR repository has no LICENSE file, and the Drive folder states none |
| Content | 143 PNG label maps, one per photograph — 23 AMD, 61 control, 59 diabetic by file name (folder listed 2026-10-12; files dated 2026-09-30) |
| Annotations | Supplies artery, vein and crossing labels, drawn by [OCULARNet](../models/ocularnet.md) at 1024×1024, cut back to this dataset's own vessel tracing and corrected by hand |

These are the first artery/vein labels for ARIA, and they are a model's. OCULAR's stated procedure:
OCULARNet's four-class probability map (background, artery, vein, crossing) is computed at
1024×1024; the dataset's binary vessel tracing is resized to 1024×1024 and thresholded; model vessel
pixels outside the tracing are removed and traced pixels the model missed are given its next most
likely vessel class; the authors then repaint errors in their own browser tool, which also offers an
*uncertain* class, and the result is multiplied by the tracing again. Every vessel pixel is therefore
one an ARIA grader drew; what OCULAR adds is which class each is, and that is OCULARNet's call
wherever its authors did not overrule it.

**Which ARIA grader's tracing was used is not stated.** ARIA has two per photograph (section 4);
OCULAR's README speaks of "the" ground-truth vessel map. Unknown.

**OCULAR's description of ARIA, against the distributor's** — the README's row reads: 143 images,
macula-centred, 50°, 576×768, UK, pathologies "DR, AMD". Count, field, country and size agree with
the distributor (576×768 is height × width of the same 768×576 frame). Two entries are OCULAR's
claim and not the distributor's: **centring** is not stated by the distributor at all, and
**"DR"** — diabetic retinopathy — overstates the diabetic group, which the distributor describes as
"diabetic subjects" with no retinopathy grade.

## 3. The images

| | |
| --- | --- |
| Count | 143: 23 AMD (`aria_a_…`), 61 control (`aria_c_…`), 59 diabetic (`aria_d_…`) |
| Resolution (pixels) | 768×576, all 143. The distributor's page gives no size; 768×576 is the size reported in the literature and by OCULAR. *Our finding, 2026-10-12:* every photograph in the archives is a 1,327,808- or 1,327,872-byte uncompressed TIFF, which is 768 × 576 × 3 colour bytes plus a header — consistent with that size, read from the archives' directories without extracting an image |
| Microns per pixel | Unknown — not published, and not yet inferred here (no fetcher exists, so `results/um_resolution/` has no ARIA entry) |
| Camera | Zeiss FF450+ fundus camera |
| Field of view | 50° |
| Centring | **Not stated by the distributor.** OCULAR's README calls it macula-centred; that is OCULAR's claim |
| Modality | Colour fundus photography, originally stored as uncompressed TIFF |

One camera, one field and one size throughout, so the three groups are classes, not subcollections.
A 50° field on 768 pixels is coarse: each pixel spans more retina than in any 45° set at 1,000 pixels
or more, so fine capillaries sit at or below a pixel wide.

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| Vessels | **Two, kept separate** — files ending `_BDP` and `_BSS`, for observers "DP" and "SS", described as graders accredited to grade retinal images | Native, 768×576 | All 143 photographs, 286 tracings. The initials match co-authors D Parry and S Spencer of Farnell 2008; the page does not say so |
| Optic disc and fovea | One file per photograph; who drew which is not stated (the files end `_dfs` or `_dfd`, which may be the same two observers — Unknown) | Native, 768×576 | **Control and diabetic only — 120 of 143.** The page says "where relevant"; no disc or fovea archive exists for the AMD group. Outlines, per the distributor; whether the fovea is a point or a region was not checked |
| Group | Per subject | — | AMD / diabetic / control, from the file name. A cohort label, **not a disease grade** |
| Artery, vein and crossing, by [OCULAR](../projects/ocularnet.md) | One model, refined by OCULAR's authors | **1024×1024**, not this dataset's native size — upsampled from 768×576 | A model's output corrected by hand, not an independent reader: where the model and the corrector agree on a mistake, it stays. Also has an *uncertain* class. Section 2.2 |

## 5. Inheritance

- **Reuses images from:** No shared images established.
- **Its images are reused by:** [OCULAR](../projects/ocularnet.md), which adds artery/vein labels
  to all 143 (section 2.2). ARIA is not among the datasets OCULAR lists for training or evaluating
  OCULARNet; it appears only in the annotation-release list. No other catalogued dataset was found to
  contain ARIA photographs.

## 6. Use as a benchmark

- **Catalogued models trained on these images:** None established. No page in `docs/models/` names
  ARIA as training data, and OCULARNet's training and test lists do not include it.
- **Below a model's measuring grid:** **Yes** — 576 pixels tall, below the 912 vessel grid and the
  1024 of the newer models, so every score here is on an upsampled image. OCULAR's artery/vein labels
  are themselves drawn on an upsampled rendition (section 4).
- **What it can answer:** held-out vessel segmentation on an older 50° camera, with a human ceiling
  from the second grader; whether vessel models trained mostly on diabetic and healthy eyes hold up
  on AMD eyes; and, through OCULAR's layer, artery/vein accuracy on a set no catalogued model has
  seen — bearing in mind those labels started as OCULARNet's own output.

## 7. Known defects

All *our findings, 2026-10-12*, from the archives' zip directories, read without extracting an image.

- **The index page is gone, the files are not.** See section 2.1. Anyone citing a download route
  should give the archive URLs, not the dead `eyecharity.com` page.
- **File names break the published convention.** The distributor documents
  `aria_<group>_<subject>_<image>.tif`, and many files do not follow it:
  - nine diabetic photographs and one control photograph are named with a numeric prefix and **no
    image number** — `(0001)aria_d_26.tif`, `(0018)aria_d_26.tif`, `(0031)aria_c_37.tif` and so on.
    Subjects 26, 27 and 28 each have two such files, told apart only by the prefix (`(0001)aria_d_26`
    and `(0018)aria_d_26`, for instance), and `aria_d_29.tif` has neither prefix nor image number;
  - nine control photographs carry a space before the image number (`aria_c_2_ 2.tif`) while their
    vessel tracings do not (`aria_c_2_2_BDP.tif`), so photograph and tracing do not pair by name;
  - one control tracing is upper-case (`aria_C_26_15_BSS.tif`), and three control files carry an extra
    letter (`aria_c_39_a_10`, `aria_c_40_a_6`, `aria_c_40_b_14`);
  - the diabetic disc/fovea archive writes the prefixes in square brackets (`[0001]aria_d_26_dfs.tif`)
    where the photographs use parentheses, mixes `_dfd` (42) and `_dfs` (16) endings, and includes
    one file with no ending at all, `aria_d_29.tif` — a name that collides with the photograph's.
  A script that pairs files by pattern will silently drop or mismatch some of them.
- **Stray files.** Every archive includes a Windows `Thumbs.db`, and the control vessel archive
  contains an empty Excel lock file, `total_control.xls~RF5abc7d2.TMP` — a sign that a
  `total_control.xls` spreadsheet existed alongside the data. It is not distributed, and what it
  held is Unknown.
- **No disc or fovea for AMD.** The page's "where relevant" covers it, but a disc model can only be
  checked on 120 of the 143.
- The describing paper is closed access and its own image counts were not checked against the
  archives.

## 8. Notes

- **Two ARIAs.** Searching the literature for "ARIA" returns both this dataset and Bankhead's
  [ARIA software](../projects/aria.md). Check which one a paper means before following a citation.
- "Diabetic" is a cohort, not a diagnosis of retinopathy. Do not read the 59 as diabetic-retinopathy
  cases, as some secondary sources (OCULAR's README among them) do.
- AMD eyes with vessel tracings are rare in this catalogue; that, more than size, is why the set is
  worth keeping.

---

**Links, licence and access last checked:** 2026-10-12
