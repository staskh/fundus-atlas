# Analysing the quality benchmark

Load this beside `SKILL.md` when changing `notebooks/quality.ipynb`.

## 1. What this analysis must show beyond the common six

- **The whole ROC curve, per model per dataset**, not the single point the accuracy reports. Where
  two curves cross, which model is better depends on whether you would rather keep a bad photograph
  or discard a good one — which is the reader's decision, not ours. Datasets whose reference has one
  class carry no curve and are named as excluded from that figure.
- **Agreement between models, with the caveat attached.** QuickQual, QuickQual-MEME and the AutoMorph
  grader were all fitted on EyeQ labels; the toolbox ensemble was not. Print the matrix and say which
  agreements are expected.
- **Right where the readers agreed against right where they did not**, for MSHF and FQS, which keep
  their readers apart. In the first run every model was right 0.87–0.98 of the time where three
  annotators agreed and 0.0–0.76 where they did not: human disagreement predicts model error, and
  that is the most useful sentence the analysis produced.
- **What a model would throw away**, for the dataset with an assumed reference: the share kept by
  each model, and the share kept by each model's *pipeline*, side by side.

## 2. Diagnostics that belong here rather than in the benchmark

The benchmark measures models against references. Anything that asks *why* a number came out as it
did is a diagnostic, runs in the notebook, and is never written into `results/`:

- **Does the store's square crop explain a rejection rate?** Trim the black bands off the native
  image, hand the model the photograph's own rectangle instead, and compare. On PAPILA this moved
  QuickQual's keep-rate from 0.458 to 0.017 — the padding was helping, not hurting — which is the
  answer, and the reason the results page can state the canvas share without implying it is the
  cause.
- **Is a class order assumption right?** VascX emits three unnamed logits. A reversed order would
  turn a ROC AUC of 0.99 into 0.01; the analysis is where that is checked and shown.

## 3. What this analysis must not conclude

- That a model is best. Coverage, threshold and contamination differ; a model that keeps 62% of
  PAPILA is not thereby better than one that keeps 28%, because neither number is an error rate
  against a grade anybody published.
- That an `assumed` reference measures accuracy. It measures what a model discards.
