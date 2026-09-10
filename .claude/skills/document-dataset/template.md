# <Dataset name>

One paragraph, plain language: how many photographs, of whom and why they were collected, what is
annotated, and what the collection is typically used for.

## 1. What it is

- **Images:** <count, and the split by class or site>
- **Collected at:** <institution, country, study name>
- **Purpose:** <why it was made — a challenge, a clinical study, a teaching set>

## 2. Provenance

| | |
| --- | --- |
| Home | <URL> |
| Download | <direct, no registration / registration / request, then agreement / no> — <URL where one exists> |
| Citation | <Full citation.> DOI: <link> |
| Licence | <exactly as stated, or `not stated`> |
| Content | <image count and resolution, one line> |
| Annotations | <what this provenance supplies, one line> |

<Prose under the table for anything that does not fit a row: restrictions worth knowing, a licence
conflict between two sources, a deposit titled differently from the dataset.>

<Where the annotations were added by different groups over time, repeat the whole table once per
provenance:>

### 2.1 <Base dataset — images and original annotations>

| | |
| --- | --- |
| Home | <URL> |
| Download | <route> — <URL> |
| Citation | <citation + DOI> |
| Licence | <as stated> |
| Content | <images> |
| Annotations | Supplies <which annotations> |

### 2.2 <Add-on layer name>

| | |
| --- | --- |
| Home | <URL> |
| Download | <route> — <URL> |
| Citation | <citation + DOI> |
| Licence | <as stated, or `not stated` — layers frequently differ from the images> |
| Content | <same images> |
| Annotations | Supplies <which annotations> |

## 3. The images

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

### 3.1 <Subcollection name> — <n> images

<the same table>

## 4. Annotations

| Annotation | Readers | Drawn at | Notes |
| --- | --- | --- | --- |
| <vessels / artery-vein / disc / cup / quality / disease> | <n, separate or merged> | <resolution, if different from the images> | <…> |

## 5. Inheritance

- **Reuses images from:** <dataset, how many, and whether resized — or `No shared images established`>
- **Its images are reused by:** <datasets, or `None established`>

## 6. Use as a benchmark

- **Catalogued models trained on these images:** <links to model pages, or `None established`>
- **Below a model's measuring grid:** <Yes, at <resolution> / No>
- **What it can answer:** <one or two lines>

## 7. Known defects

<One bullet per defect in the distribution itself, with evidence and status. If nothing is known,
write `None recorded as of <YYYY-MM-DD>.` — an absence of findings, not a clean bill of health.>

## 8. Notes

Anything a reader needs in order not to be misled.

---

**Links, licence and access last checked:** <YYYY-MM-DD>
