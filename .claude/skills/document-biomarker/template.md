# <Biomarker name>

One paragraph, plain language: what this number says about the eye, which direction is treated as
abnormal, and what it has been associated with. No formulas.

## 1. What it measures

- **In one sentence:** <what a clinician would understand it to be>
- **Also known as:** <other names and abbreviations in the literature>
- **Direction of concern:** <higher / lower, and in what context>

## 2. Definition of record

- <Full citation of the publication that defined it.> DOI: <link>
- **The formula, in words:** <state it plainly before any symbols>

## 3. Variants

<One subsection per competing definition. If there is genuinely only one, say so explicitly.>

### 3.1 <Variant name>

- **Formula, in words:** <…>
- **Source:** <citation + DOI>
- **Implemented by:** <projects>

**Comparability:** <Are the variants numerically interchangeable? If not, say that a value without
its variant recorded is meaningless.>

## 4. Inputs required

- **Segmentations:** <vessels / artery-vein / disc / cup / fovea>
- **Derived geometry:** <skeleton, per-segment calibre profile, disc centre and diameter, segments split at junctions, …>
- **Why this matters:** <where implementations diverge in this step>

## 5. Measurement region

<Whole image, disc-centred zone with radii in disc diameters, ETDRS field, hemifield — and each
convention where implementations differ.>

## 6. Units and scale dependence

- **Unit as computed:** <pixels / microns / degrees / dimensionless>
- **Depends on the pixel grid:** <Yes/No — and which model grid produced the mask>
- **Depends on a physical scale:** <Yes/No — microns per pixel, or disc-diameter normalisation>
- **Depends on field of view:** <Yes/No>
- **Scale-invariant:** <Yes/No>

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [<project>](../projects/<slug>.md) | <variant> | <path in that project> | Original / reuses <project> / reimplemented |

## 8. Sensitivity and failure modes

- <What moves the number for reasons unrelated to the eye.>
- **Reported reproducibility:** <figure, with attribution, or Unknown>

## 9. Known defects

<One subsection or bullet per defect: what is wrong, which implementations it affects, the upstream
issue or commit, and its status. If nothing is known, write `None recorded as of <YYYY-MM-DD>.` — an
absence of findings, not a clean bill of health.>

## 10. Notes

Anything a reader needs in order not to be misled.

---

**Links and definitions last checked:** <YYYY-MM-DD>
