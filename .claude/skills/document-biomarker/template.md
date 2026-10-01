# <family>

**<One line: what the family measures.>** <How many biomarkers, and what they have in common —
the sentence that justifies them sharing a page.>

*A new family needs Stas's agreement. Most of the time you are adding a row to one of the five that
exist, not using this template.*

## 1. What it measures

Plain language, for a clinician or researcher who will never open the code: what these numbers say
about the eye, which direction is treated as abnormal, and what they have been associated with. No
formulas.

## 2. The canonical names

| Name | What it is | Statistic |
| --- | --- | --- |
| `<family>/<biomarker>/{artery,vein,vessels}` | <one line> | `<which apply, or none>` |

State the family's **overrides**: whether any biomarker requires a region rather than defaulting to
`fov`, whether the family has a `structure` part at all, and which biomarkers have a `vessel-`
whole-vessel form.

Where two entries differ only by how values are pooled, say so — they are one biomarker and the
statistic part tells them apart.

## 3. Definitions of record

One bullet per biomarker, with the paper linked to `docs/papers/` where it has a page. **Where there
is no defining paper, write the formula out** — what it is computed over and the conventions it
assumes — and optionally point at an implementation as a worked example.

### 3.1 <Where two variants share a name, the subsection that separates them>

State plainly whether they are **numerically comparable**. If they are not, say that a value is
meaningless without its variant recorded.

## 4. Inputs required

Which segmentations are consumed, and what geometry is derived from them. Be specific: most
disagreement between implementations of one formula comes from this step, not the formula. Where a
centreline is needed, say so and link [vessel tracing](vessel-tracing.md) —
how it is obtained is the implementation's business and is documented on its project page.

## 5. Measurement region

The default, which biomarkers require one, and what the implementations actually use. Link
[regions of interest](regions-of-interest.md) rather than restating radii.

## 6. Units and scale dependence

**Microns, never pixels.** A table where the family spans more than one dimension. For each
biomarker say whether it survives a change of **camera** and whether it survives a change of
**field of view** — different questions, and a dimensionless number can fail the second.

Where curvature is involved, state that the **estimator** and its scale are part of the measurement.

## 7. Implementations

| Project | What it computes | Source | Lineage |
| --- | --- | --- | --- |

**Lineage matters more than presence.** Where implementations share code, say so — their agreement
is evidence about a common ancestor, not about the retina.

## 8. Sensitivity and failure modes

What moves the number for reasons unrelated to the eye: segmentation thickness, how segments are
split, image quality, resampling, rotation. Where a published reproducibility figure exists, give it
and attribute it.

## 9. Known defects

One bullet per defect, with its evidence, whose it is, and the date. Mark this repository's own
findings as ours. If nothing is known, write `None recorded as of <YYYY-MM-DD>` — an absence of
findings, not a clean bill of health.

---

**Links and definitions last checked:** <YYYY-MM-DD>
