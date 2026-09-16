# Analysing the disc-and-cup benchmark

Load this beside `SKILL.md` when changing `notebooks/disc.ipynb`. The model is the primary index
throughout; the dataset, the reader and the structure sit inside it.

## 1. The sections, in order

| # | Section | Must show |
| --- | --- | --- |
| 1 | Coverage | what each model produced an outline for, and what it failed or declined on |
| 2 | Overlap | Dice per structure, pooled and then per dataset — the familiar number, first and briefly |
| 3 | Where the boundary actually sits | centre offset, width, height, equivalent radius — section 3 below |
| 4 | The number anyone uses | cup-to-disc ratio error, signed — section 4 |
| 5 | Against the readers' own disagreement | the ceiling, per dataset — section 5 |
| 6 | Model against model | agreement on the same photographs, and where they diverge |
| 7 | The hard cases | outlines drawn over the photograph, up to eight per dataset, each labelled |
| 8 | What this cannot say | contamination, resampling, references that are not comparable |

## 2. Dice is the least informative number here, so do not lead with it

Two models with the same Dice can put the boundary in different places: one inflating the cup
evenly, one missing a sector. Show Dice, then show the metrics that say **where** the difference is,
and let the prose say which of them a reader should act on.

## 3. Where the boundary sits

- **Centre offset in disc diameters**, never only in pixels: a 10-pixel error means different things
  on a 2,576-pixel PAPILA photograph and a 1,444-pixel one.
- **Width and height errors separately.** A model that is systematically short vertically and right
  horizontally is making an elliptical error, and the vertical cup-to-disc ratio will inherit it.
- **Signed, not absolute**, for every one of these. A systematic bias and random scatter are
  different problems and the mean of an absolute error hides which you have.

## 4. The cup-to-disc ratio is the result that leaves the building

Plot the model's ratio against the expert's, per photograph, one panel per model, with the identity
line drawn. Then say, in words:

- **the bias** — does this model call cups larger or smaller than the expert;
- **the scatter** — the spread around that bias;
- **how many photographs cross a referral threshold** in one direction or the other. A ratio error
  of 0.05 matters at 0.65 and not at 0.3, and this is the section where that is said.

Where the dataset publishes its own ratio, plot against that as well and say which reference each
panel uses.

## 5. The readers' own disagreement is the ceiling

Compute every reader-against-reader figure the models are scored on — Dice, centre offset,
cup-to-disc ratio difference — and show the models against that band, per dataset. Chákṣu's five
ophthalmologists and PAPILA's two are the only ceilings available; a model inside the band is not
distinguishable from a reader, and the page must not claim it beat one.

Where a dataset has one reader, say that no ceiling can be computed for it rather than leaving the
absence to be inferred.

## 6. Drawing the failures

An outline is a picture, and this is the benchmark where the images matter most. For the hard
cases, draw the expert's contour and the model's over the photograph, same axes, labelled, up to
eight per dataset. A reader learns more from one such panel than from a column of Dice scores.

## 7. What this analysis must not conclude

- That a model is best because its Dice is highest. Say what it is best at: overlap, centring, or
  the ratio — and note where those disagree.
- That a model beat the experts, on a dataset where the experts disagree with each other by more
  than the model disagrees with them.
- That a ratio error is small because its mean is small. Report the spread and the crossings.
