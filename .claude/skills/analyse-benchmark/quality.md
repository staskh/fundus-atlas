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
  their readers apart. Expect the gap to be wide, and treat it as the analysis's most useful output:
  where three annotators disagreed and a model was wrong, the suspicion belongs on the annotation as
  much as on the software, which is the whole reason model-against-model numbers exist.
- **What a model would throw away**, for the dataset with an assumed reference: the share kept by
  each model, and the share kept by each model's *pipeline*, side by side.

## 2. Diagnostics that belong here rather than in the benchmark

The benchmark measures models against references. Anything that asks *why* a number came out as it
did is a diagnostic, runs in the notebook, and is never written into `results/`:

- **Does the store's square crop explain a rejection rate?** Trim the black bands off the native
  image, hand the model the photograph's own rectangle instead, and compare. Do this before
  concluding anything from a dataset whose canvas share is large: the answer has come out the
  opposite way round from the obvious guess, with the square helping rather than hurting.
- **Is a class order assumption right?** VascX emits three unnamed logits. A reversed order would
  turn a ROC AUC of 0.99 into 0.01; the analysis is where that is checked and shown.

## 3. What this analysis must not conclude

- That a model is best. Coverage, threshold and contamination differ, and on a dataset with an
  assumed reference no number is an error rate against a grade anybody published.
- That an `assumed` reference measures accuracy. It measures what a model discards.
