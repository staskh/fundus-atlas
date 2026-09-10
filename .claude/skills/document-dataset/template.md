# <Dataset name>

One paragraph, plain language: how many photographs, of whom and why they were collected, what is
annotated, and what the collection is typically used for.

## 1. What it is

- **Images:** <count, and the split by class or site>
- **Collected at:** <institution, country, study name>
- **Purpose:** <why it was made — a challenge, a clinical study, a teaching set>

## 2. Original publication

- <Full citation.> DOI: <link>

<If no describing publication exists, say so explicitly: "No describing publication — distributed as
a download only.">

<Where the annotations come from several groups, split sections 2, 3 and 4 into one subsection per
layer, named after the layer, like this:>

### 2.1 <Base dataset — images and the original annotations>

- <Full citation.> DOI: <link>
- **Supplies:** <which annotations>

### 2.2 <Add-on layer name>

- <Full citation.> DOI: <link>
- **Supplies:** <which annotations, on the same images>

## 3. Access

- **Home:** <URL>
- **Direct download:** <Yes — unattended / Registration required / Request by email / No>
- **URL:** <direct link where one exists>
- **Arrives as:** <archive format and layout, in one line>

<Repeat as 3.1, 3.2, … per layer where the layers are distributed separately — each has its own home
and its own download route.>

## 4. Licence

- **Images:** <licence exactly as stated, or `Not stated`>
- **Annotations:** <licence, where it differs; otherwise `Same as images`>
- **Restrictions worth knowing:** <challenge-only use, non-commercial, no redistribution, …>

<Repeat as 4.1, 4.2, … per layer. A layer added by another institution frequently carries different
terms from the images it annotates, and a page that states one licence for all of it is wrong.>

## 5. The images

| | |
| --- | --- |
| Resolution (pixels) | <every distinct size> |
| Microns per pixel | <value, or `Unknown` — most datasets do not publish it> |
| Camera | <make and model> |
| Field of view | <degrees> |
| Centring | <disc-centred / macula-centred / mixed> |
| Modality | <colour fundus photography, or state prominently when it is not> |

<Where the dataset has well-defined subcollections — different cameras, sites, challenge releases, or
an ultra-wide split — repeat this section once per subcollection, with its own count:>

### 5.1 <Subcollection name> — <n> images

<the same table>

### 5.2 <Subcollection name> — <n> images

<the same table>

## 6. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| <vessels / artery-vein / disc / cup / quality / disease> | <n, separate or merged> | <resolution, if different from the images> | <…> |

## 7. Inheritance

- **Reuses images from:** <dataset, how many, and whether resized — or `No shared images established`>
- **Its images are reused by:** <datasets, or `None established`>

## 8. Use as a benchmark

- **Catalogued models trained on these images:** <links to model pages, or `None established`>
- **Below a model's measuring grid:** <Yes, at <resolution> / No>
- **What it can answer:** <one or two lines>

## 9. Known defects

<One bullet per defect in the distribution itself, with evidence and status. If nothing is known,
write `None recorded as of <YYYY-MM-DD>.` — an absence of findings, not a clean bill of health.>

## 10. Notes

Anything a reader needs in order not to be misled.

---

**Links, licence and access last checked:** <YYYY-MM-DD>
