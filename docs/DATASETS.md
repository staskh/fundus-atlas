# Datasets

Published collections of colour-fundus photographs. Each row links to a detail page recording what
the images are — camera, resolution, field of view, microns per pixel where anyone published it —
what is annotated and by how many readers, whose photographs the collection reuses, its licence, and
whether it can be downloaded directly.

Three things about this catalogue are worth reading before the table.

**Every licence is different, and several are not stated at all.** A public download is not
permission to redistribute or to use commercially. The Licence column records what the distributor
says; the detail pages record where images and annotations carry different terms.

**Several of these datasets are the same photographs.** One dataset's images annotated by another
group is one camera's worth of evidence, not two. Section 2 maps that in both directions, including
where the reused copies were resized — a resized copy is a different set of pixels.

**A dataset a model trained on cannot measure that model.** Each detail page names the catalogued
models trained on its images, so a score can be read as in-sample or held out. That single fact
decides what any comparison in [MODELS.md](MODELS.md) is worth.

## 1. Summary

Sorted by image count, largest first.

| Dataset | Images | Resolution | Year | Quality | Vessels | A/V | Disc | Cup | Disease | Other labels | Licence | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _No entries yet._ | | | | | | | | | | | | |

## 2. Shared photographs

_No entries yet._ — this section maps which datasets are built on which others' images, in both
directions, because two datasets sharing photographs are not independent evidence.

## 3. Not colour fundus photography

_No entries yet._ — scanning laser ophthalmoscopy, infrared reflectance and ultra-wide-field
collections look like fundus datasets in a file browser and cannot be pooled with them.

## 4. How to read this table

- **Resolution** — every distinct size present; `mixed` where a dataset spans several, with the
  per-subcollection detail on its page. Compare it against the grid each model measures on, in
  [MODELS.md](MODELS.md): a dataset below that grid is upsampled before measurement, which flatters
  a segmentation score, and one far above it is downsampled, which destroys thin vessels.
- **Year** — the publication year of the describing paper, which is the quickest guide to what
  camera generation and what annotation conventions to expect.
- **The annotation columns** — quality, vessels, A/V, disc, cup — carry ✅ where the dataset supplies
  that label and `—` where it does not, with a reader count where more than one person annotated
  (`✅ ×5 experts`). **A reader count above one is the most useful property a dataset can have**: it
  is what lets a human agreement ceiling be measured rather than assumed.
- **Quality** grades the *photograph*; **Disease** grades the *eye*, and the schemes are not
  interchangeable between datasets — four classes here, three there, a glaucoma triple including
  "suspect" elsewhere. The cell names the scheme; the page explains it.
- **Other labels** — fovea locations, lesion classes, demographics, published biomarker values,
  vessel junctions. This is where the unusual and most valuable content hides.
- **Not in this table, on the detail pages instead:** camera and field of view, microns per pixel,
  the download route and whether a direct link exists, the describing paper, and inheritance. Each
  of those is a per-subcollection or per-annotation-layer fact that one cell would misrepresent —
  a dataset annotated by three institutions has three papers, three downloads and possibly three
  licences.
- **Known defects** are not in this table either. Every detail page carries a section 9 for errors
  in the distribution itself — mislabelled files, counts that disagree with the paper, annotations
  that do not match their own description.

## 5. Adding a dataset

Dataset pages follow a fixed structure so they can be read against each other. Load the
`document-dataset` skill, which defines that structure and this table's columns, before adding or
changing an entry.
