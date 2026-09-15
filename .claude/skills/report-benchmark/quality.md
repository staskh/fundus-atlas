# The quality benchmark's two documents

Load this beside `SKILL.md` when changing what `docs/benchmarks/quality-docs.md` or
`docs/benchmarks/quality-results.md` say.

## 1. What `quality-docs.md` must explain that no other benchmark has

- **The three kinds of reference** — `published`, `derived`, `assumed` — with the derivation rule
  spelled out for each dataset that uses one, and the warning that an `assumed` reference contains
  no bad photographs at all.
- **The black canvas share per dataset**: how much of the square the store built is not photograph.
  A quality model judges the square it is handed.
- **Every column of the evidence**, including the four that a model may leave absent —
  `verdict`, `good`, `usable`, `bad` — and why: a scalar model has no classes to report and none are
  invented for it.
- **`carried_by_its_pipeline`**, which is not the model's verdict but its project's decision, with
  each project's rule quoted.

## 2. What `quality-results.md` leads with

Section 1 is **model × dataset**, and the numbers in it are, in this order: photographs, coverage,
accuracy on *worth measuring*, ROC AUC, and the contamination mark. Nothing else belongs in the
headline table — the three-class scores and the gates are sections of their own, because only some
models have them.

The detail section breaks each dataset into its splits and subsets, which for this benchmark means:
FIVES by split, FQS whole (it publishes none), MSHF by camera **and** split — its portable and
tabletop groups behave differently enough that one number over them would hide the finding — and
PAPILA whole.

## 3. Sections this benchmark's results page must carry

Beyond the common shape:

- **Coverage, with its explanation.** It is 1.00 everywhere, and the page says why: none of these
  models declines on its own judgement, and a pipeline's refusal is not the model's.
- **The three grades**, with per-grade recall and the confusion behind it, for the three models that
  name all three — and a line naming the datasets whose reference never uses `usable`, so that a
  dash reads as the reference's silence rather than the model's failure.
- **What each project would carry into measurement**, with the rule quoted per project and the count
  of photographs where the pipeline disagreed with its own model.
- **Where a model and the expert disagree most**, which is the benchmark's primary question and the
  place a reader looks to judge whether the reference itself deserves a second look.
- **What a model would throw away**, from the dataset with an assumed reference: the share each
  model, and each pipeline, would keep of a curated collection.

## 4. Sentences this page has needed, and why

- *"No model declined a photograph in this run"* — otherwise a column of zeros reads as broken
  machinery rather than as a fact about where refusal happens.
- *"An `assumed` reference contains no bad photographs at all"* — otherwise its accuracy reads as a
  score rather than as a keep-rate.
- *"Black canvas is the share of the square that is not photograph"* — otherwise a dataset with a
  large share invites the guess that the bands caused its rejection rate. Whether they did is a
  diagnostic, and it belongs in the notebook, not here.
