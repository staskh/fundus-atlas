# Analysing the quality benchmark

Load this beside `SKILL.md` when changing `notebooks/quality.ipynb`. It defines what that notebook
must contain, section by section. The model is the primary index throughout (`SKILL.md` §2): a
reader is looking for a model, and the datasets sit inside it.

## 1. The sections, in order

| # | Section | Must show |
| --- | --- | --- |
| 1 | Coverage | graded, declined and failed per model and dataset, before any accuracy |
| 2 | Against the expert's grade | the confusion matrix of section 2 below — tabulated **and** drawn — accuracy and κ as bars, the ROC curves, and the component analysis of section 3 |
| 3 | In-sample and out-of-sample | the same confusion, split by what each model trained on — section 4 |
| 4 | Model against model | pairwise agreement, with the caveat attached |
| 5 | Model against the readers | right where the readers agreed, against right where they did not |
| 6 | What a model would throw away | the dataset with an assumed reference, model by model |
| 7 | The hard cases | photographs as images, up to eight **per dataset**, each labelled with its dataset |
| 8 | What this cannot say | the marks, the incomparable references, and the refusal to rank |

## 2. The confusion matrix is the primary figure

The benchmark's question is whether a model agrees with what an expert recorded, and the honest
form of that answer is **a two-by-two table per model**: what the dataset called worth measuring
against what the model called worth measuring.

|  | model says keep | model says discard |
| --- | --- | --- |
| **expert says worth measuring** | agreed | the model throws away a usable photograph |
| **expert says not** | the model keeps an unusable one | agreed |

Report it per model and dataset, as counts and as shares, because the two errors are not
interchangeable: discarding a good photograph costs a study its sample size, and keeping a bad one
costs it its measurements. A single accuracy hides which of the two a model does.

**Draw it as well as tabulating it.** A grid of two-by-two heatmaps — models down, datasets
across — is read in a glance where twenty rows of counts are not, and it is the figure that makes
two models with the same accuracy and opposite behaviour obviously different. Annotate each cell
with its count.

**Report Cohen's κ beside accuracy, everywhere accuracy appears.** Accuracy flatters a model on a
dataset where one class dominates: a grader that keeps everything scores 0.9 on a collection that
is 90% gradeable while agreeing with nobody about anything. κ measures agreement beyond what
guessing the common answer would achieve, so the pair together says what neither says alone. It is
undefined where a reference has only one class — report a dash, never a zero.

**Plot both.** Accuracy and κ as bars, model by model with the datasets inside each model, so that
the eye compares models rather than datasets (`SKILL.md` §2). Where the two disagree — a high
accuracy beside a low κ — that is the finding, and the bars put it next to each other.

**Where a model's threshold comes from matters here.** Several of these models publish a hard call
directly; the Fundus Image Toolbox ensemble publishes only a confidence and calls everything at or
above **0.5** gradeable and everything below it ungradeable. That is the toolbox's own default, its
authors say plainly that it does not transfer between datasets, and the confusion matrix is where
its consequences become visible. State the rule beside the table rather than leaving a reader to
assume one.

## 3. FIVES: which defect a model is actually reacting to

[FIVES](../../../docs/datasets/fives.md) publishes no overall grade. It publishes **three binary
component scores** — `illumination_contrast`, `blur`, `low_contrast` — from which this repository
derives the grade the benchmark scores against (all three sound is `good`, one short is `usable`,
worse is `bad`).

That makes FIVES the one dataset here that can say **which defect a model notices**. Join the
store's manifest to the evidence and cross-tabulate the keep-rate per model against every
combination of the three components, with the photograph count beside it:

- all three sound is the reference for "a model should keep this";
- a single defect is where a model's usefulness lives — a grader that keeps everything with one
  defect is not gating, and one that discards everything with one defect will halve a study;
- the rare combinations have few photographs and their rates are noise: print the count so nobody
  reads a rate of 0.00 over one photograph as a finding.

Do this per model. A model that reacts to blur and ignores illumination is a different instrument
from one that does the reverse, and no summary number distinguishes them.

## 4. In-sample and out-of-sample, with the training data named

Repeat the confusion matrix of section 2, grouped by the contamination mark — and **name what each
model trained on**, in the notebook, rather than making the reader open five catalogue pages:

| Model | Trained on |
| --- | --- |
| fit-quality | DeepDRiD and DRIMDB, split not stated |
| automorph-quality-grader | EyeQ's training split |
| quickqual | EyeQ's training split |
| quickqual-meme | EyeQ's training split, the same parameters |
| vascx-quality | not published; its own checkpoint names EyeQ |

Where a dataset's splits carry different marks, group by split too: a model's number on the half it
trained on is not comparable with its number on the half it did not, and putting the two side by
side is the only way to see what the difference is worth.

## 5. Model against model, and model against reader

- **Agreement between models, with the caveat attached.** Three of the five were fitted on EyeQ
  labels; their agreement is expected. Agreement with a model trained elsewhere is the informative
  number, and disagreement is where to go looking for a bad annotation.
- **Right where the readers agreed against right where they did not**, for the datasets that keep
  their readers apart. Expect the gap to be wide, and treat it as the analysis's most useful
  output: where readers disagreed and a model was wrong, the suspicion belongs on the annotation as
  much as on the software.

## 6. The hard cases

Up to **eight photographs per dataset**, each drawn from that dataset's own failures and each
labelled with **the dataset it came from** and the grade it was given. Photographs pooled across
datasets and then taken in whatever order they arrive make a picture of whichever dataset fails
most, which is not the question.

## 7. Diagnostics that belong here rather than in the benchmark

The benchmark measures models against references. Anything that asks *why* a number came out as it
did is a diagnostic, runs in the notebook, and is never written into `results/`:

- **Does the store's square crop explain a rejection rate?** Trim the black bands off the native
  image, hand the model the photograph's own rectangle instead, and compare. Do this before
  concluding anything from a dataset whose canvas share is large: the answer has come out the
  opposite way round from the obvious guess, with the square helping rather than hurting.
- **Is a class order assumption right?** VascX emits three unnamed logits. A reversed order would
  turn a ROC AUC of 0.99 into 0.01; the analysis is where that is checked and shown.

## 8. What this analysis must not conclude

- That a model is best. Coverage, threshold and contamination differ, and on a dataset with an
  assumed reference no number is an error rate against a grade anybody published.
- That an `assumed` reference measures accuracy. It measures what a model discards.
