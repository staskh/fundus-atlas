# Arteriolar-venular ratio (AVR)

How wide the arterioles are relative to the venules — one number, normally a little below 1. It is
the best-known retinal vascular biomarker and the one most often reported in cardiovascular and
hypertension research, because dividing one calibre summary by the other cancels out the camera's
magnification and the patient's refraction.

That cancellation is also its weakness: a fall in AVR cannot say whether the arterioles narrowed or
the venules widened, and those have different causes.

## 1. What it measures

- **In one sentence:** the ratio of arteriolar calibre to venular calibre near the optic disc.
- **Also known as:** artery-vein ratio, arteriole-to-venule ratio, AVR.
- **Direction of concern:** lower is treated as adverse, and has been associated with raised blood
  pressure and cardiovascular risk.

## 2. Definition of record

- **The formula, in words:** CRAE divided by CRVE — the arteriolar equivalent over the venular
  equivalent, both computed on the same ring around the disc.
- The definition therefore lives on the [central retinal equivalents](central-retinal-equivalents.md)
  page: Hubbard LD et al., Ophthalmology 1999, and Knudtson MD et al., Current Eye Research 2003.

## 3. Variants

AVR has only one formula, and inherits its variants entirely from its two inputs.

### 3.1 Knudtson AVR

- **Formula, in words:** the ratio of the two Knudtson equivalents.
- **Implemented by:** [AutoMorphalyzer](../projects/automorphalyzer.md) (zones B and C),
  [VascX](../projects/vascx.md), and derivable in [PVBM](../projects/pvbm.md) by dividing its two
  outputs, as its README instructs.

### 3.2 Hubbard AVR

- **Formula, in words:** the ratio of the two Hubbard equivalents.
- **Implemented by:** [AutoMorph](../projects/automorph.md), which reports both variants.

**Comparability:** a Knudtson AVR and a Hubbard AVR are different numbers. The ratio cancels
*scale*, not *formula* — so while AVR is refreshingly free of unit problems, it is not free of the
variant problem, and published AVR values are frequently reported without saying which formula
produced them.

## 4. Inputs required

- **Segmentations:** artery/vein and the optic disc — everything the equivalents need.
- **Derived geometry:** as for the equivalents: disc centre and radius, a measurement ring, vessel
  widths at the crossings.
- **Why this matters:** AVR is a quotient of two quantities that share every upstream error, so
  correlated errors partly cancel — and uncorrelated ones, such as one vessel class being
  systematically mislabelled, are amplified.

## 5. Measurement region

Whatever ring the two equivalents used, and it must be the same ring for both. AutoMorphalyzer
reports AVR in zones B and C; VascX over its configured circles; PVBM over the annulus between 2 and
3 disc radii.

## 6. Units and scale dependence

- **Unit as computed:** dimensionless.
- **Depends on the pixel grid:** No — the grid cancels in the ratio.
- **Depends on a physical scale:** No, for Knudtson. For Hubbard the ratio still inherits the
  micron-fitted constants of its inputs, so a Hubbard AVR computed from pixel widths is not simply a
  rescaled one.
- **Depends on field of view:** No.
- **Scale-invariant:** **Yes** — the reason this biomarker travels between studies better than
  calibre does.

## 7. Implementations

| Project | Variant | Source file | Lineage |
| --- | --- | --- | --- |
| [AutoMorph](../projects/automorph.md) | both | retipy's `tortuosity_measures.py` | Reuses [retipy](../projects/retipy.md) |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Knudtson, zones B and C | `automorph/measure/` | Added by this project — AutoMorph reported the equivalents but its AVR handling differed |
| [VascX](../projects/vascx.md) | Knudtson constants | `vascx/fundus/features/cre.py` | Original |
| [PVBM](../projects/pvbm.md) | either, by division | `PVBM/CentralRetinalAnalysis.py` | Left to the user, per its README |
| [AutoMorphClass](../projects/automorphclass.md) | AutoMorph's set | `src/pytorch_automorph/feature_calculation.py` | Reimplemented |

## 8. Sensitivity and failure modes

- **Artery-vein labelling errors are the main risk**, and they hurt twice: a venule counted as an
  arteriole raises the numerator and lowers the denominator at once.
- **A narrow dynamic range.** AVR values cluster in a band roughly between 0.6 and 0.9, so a
  measurement error of a few percent consumes a large share of the between-subject spread.
- **It hides direction.** Report CRAE and CRVE alongside it, or the finding cannot be interpreted.
- **Reported reproducibility:** see the equivalents' page; AVR's repeatability follows theirs.

## 9. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 10. Notes

- AVR is the biomarker most likely to be compared across pipelines, and the most nearly safe to
  compare — provided the variant matches. Of everything in this catalogue, it is the best candidate
  for the comparison tables to start with.

---

**Links and definitions last checked:** 2026-09-10
