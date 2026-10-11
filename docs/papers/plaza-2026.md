# Plaza 2026

This paper introduces OCULARNet and the OCULAR collection, and it is the closest published precedent for the
comparison this atlas is built around. It scores artery/vein models by whether the biomarkers
computed from their masks agree with those computed from the expert's, on the same photographs,
and it shows that ranking differs from the ranking by Dice.

## 1. Citation

| | |
| --- | --- |
| Title | Beyond Dice: Clinically Meaningful Large-Scale Retinal Artery/Vein Segmentation |
| Authors | Plaza G, Sanchez M, Serra-Castanera A, Valls-Esteve A, Mata Miquel C, Camara O, Galdran A |
| Venue | MICCAI 2026 Satellite Events, Ophthalmic Medical Image Analysis (OMIA) workshop, paper OMIA_030, published 2026-09-21 |
| DOI | none established — the open-access satellite proceedings give no DOI; the stable URL is https://papers.miccai.org/miccai-2026-sat/OMIA_030 |
| Open copy | publisher — [MICCAI 2026 Satellite Events open access](https://papers.miccai.org/miccai-2026-sat/OMIA_030) · [PDF](https://papers.miccai.org/miccai-2026-sat/paper/OMIA_030.pdf) |
| PMID | None found |
| Code | [OCULARNet](../projects/ocularnet.md) — https://github.com/GonzaloPlaaza/OCULAR |
| Dataset | The OCULAR collection — about 1,200 harmonised artery/vein annotations from public datasets, plus 1,791 refined annotations derived from binary vessel masks — announced for release at https://github.com/GonzaloPlaaza/OCULAR. Not catalogued as a dataset here |
| Other | Weights: [OCULARNet](../models/ocularnet.md) on Hugging Face, https://huggingface.co/Anon-User-Retina/OCULARNet |

## 2. What it is about

Artery/vein models are usually judged by how many pixels they colour the same as the expert. The
authors argue that this is the wrong test, because what a clinician uses is the biomarker computed
from the mask, and they show two cases where the overlap barely moves while the biomarker does: one
vein segment given the wrong colour drops the arteriovenous ratio from 0.67 to 0.61 at a Dice of
98.7, and corrupting most venous bifurcations moves the mean branching angle from 62.9° to 47.1° at
a centreline Dice of 98.1.

They then do two things. They pool about 1,200 public artery/vein annotations from fourteen
datasets into one harmonised training collection, OCULAR. And they train a model, OCULARNet, whose
loss gives extra weight to the regions biomarkers are read from: small discs around every junction,
and the centrelines of the major arcades. They compare it against three released models, AutoMorph,
RRWNet and VascX, on test sets kept apart from training and graded by how far each is from the
training conditions. The yardstick is how well each biomarker computed from the model's mask agrees
with the same biomarker computed from the expert's, across photographs.

## 3. Why it is in this atlas

- **Kind:** comparison
- It runs the comparison this atlas's artery/vein biomarker benchmark is planned around: the same
  biomarker on the expert's mask and on each model's mask, over the same photographs. It
  includes two models this atlas benchmarks, [AutoMorph's artery/vein model](../models/automorph-artery-vein.md)
  and [VascX](../models/vascx-artery-vein.md). It is the prior work this atlas's own numbers should
  be read against, and the source of OCULARNet's training and test split.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| Overlap and centreline overlap can stay near 98% while a biomarker shifts by a clinically meaningful amount | Two constructed corruptions of one annotated photograph (Fig. 1) | this paper |
| Models trained on the OCULAR collection agree with expert-derived biomarkers better than the three released models, which vary more between datasets | Out-of-distribution test sets: mBRSET, TREND-AV, IOSTAR-AV, RAVIR, AV-WIDE | this paper, Table 1 |
| OCULARNet has the highest agreement for almost every biomarker; venous branching angle is the exception | The same test sets; agreement as intraclass correlation, bootstrapped over photographs | this paper, Table 1 |
| OCULARNet does not have the best overlap: its out-of-distribution Dice is 71.8 for arteries and 75.0 for veins, against 72.3 and 75.7 for the same network trained with overlap losses only | The same test sets | this paper, Table 1 |
| Each region-focused loss term helps the biomarkers it targets and hurts others; the combination has the best overall agreement | Ablation on the same test sets | this paper |

These are the authors' measurements on their own split. This atlas's own comparisons are separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [OCULARNet](../models/ocularnet.md) | Introduced |
| [OCULARNet-nano](../models/ocularnet-nano.md) | Same authors and repository; the paper does not describe it |
| [OCULARNet project](../projects/ocularnet.md) | The code this paper describes |
| [AutoMorph artery/vein](../models/automorph-artery-vein.md), [VascX artery/vein](../models/vascx-artery-vein.md) | Used as comparators |
| [mBRSET](../datasets/mbrset.md), [IOSTAR](../datasets/iostar.md), [RAVIR](../datasets/ravir.md), [WIDE](../datasets/wide.md), [REYIA](../datasets/reyia.md) (its `trend` subset is TREND-AV) | Out-of-distribution test sets |
| [DualModal](../datasets/dualmodal2019.md), [UNAF](../datasets/unaf.md) | In-distribution test sets |
| [Tortuosity](../biomarkers/tortuosity.md), [Calibre](../biomarkers/calibre.md), [Regions of interest](../biomarkers/regions-of-interest.md) | Biomarkers it measures agreement on |
| [Naim 2026](naim-2026.md) | The same argument made for tortuosity |

## 6. Notes

- **Its tortuosity is normalised by the disc–fovea distance.** The tortuosity it scores is total
  absolute curvature over a segment's length multiplied by the distance from the optic disc to the
  fovea, length-weighted over segments. That makes it dimensionless, but it is not one of Hart's
  formulas as this atlas names them. Its numbers are not comparable with a tortuosity in 1/µm.
- **Zone B is stated as "0.5–1.0 OD diameters centered at the OD"**, which does not say whether the
  half-diameter is measured from the disc's centre or its margin. Read
  [regions of interest](../biomarkers/regions-of-interest.md) before comparing its CRAE/CRVE with
  anyone else's.
- **Which software computed the biomarkers is not named** beyond "the same pipeline" for model and
  expert masks. The project's README points at [PVBM](../projects/pvbm.md).
- **Every photograph was cropped to its field-of-view bounding box and resized to 1024×1024** before
  training and testing. Optic disc and fovea annotations that datasets lacked were drawn by the
  authors as ellipses.
- **Test-time augmentation is used** for the reported predictions, which matches the adapter's averaging
  over the photograph and its three flips.
- **The weights and code live under accounts and URLs set up for anonymous review**, which may move
  now that the paper is published.

---

**Links last checked:** 2026-10-11
