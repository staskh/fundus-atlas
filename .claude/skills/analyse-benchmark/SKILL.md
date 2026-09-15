---
name: analyse-benchmark
description: Write the notebook that explains a benchmark's numbers — the distributions behind each summary figure, where models disagree with each other and with the readers, and what the failures look like. Use when adding or changing anything under notebooks/.
---

# Analysing a benchmark

Every benchmark produces four things for three readers: `results/` holds the evidence, the two
generated documents in `docs/benchmarks/` hold the configuration and the facts, and **the notebook
holds the judgement**. They are separate artefacts because a table saying a model scores 0.82 cannot
say that the 0.82 is two populations and that one of them is a camera.

One notebook per benchmark, `notebooks/<name>.ipynb`, at least. **What only one benchmark's analysis
must show lives in its own file beside this one** — `quality.md`, and one per benchmark thereafter —
and you load that file too.

| Benchmark | Its analysis |
| --- | --- |
| Quality | [quality.md](quality.md) |

## 1. What a notebook may and may not do

- It **reads `results/`** and the store. It never runs a benchmark, never writes into `results/`,
  and never recomputes a summary number the run already computed — if a figure needs a number the
  run does not keep, that is a change to the benchmark, not a calculation in a notebook.
- It **may run a model** for a diagnostic the benchmark deliberately does not measure — the check
  that PAPILA's black bands were not what made the models reject it needed one — as long as the
  result is presented as a diagnostic and never written into `results/`.
- It **may draw on the photographs themselves**, from `.atlas_data/`, which is the point of section
  2.5 below.
- It is **committed with its outputs cleared**. Rendered figures are megabytes of base64 that change
  on every run and say nothing in a diff; anyone wanting the pictures runs the notebook.

## 2. What every benchmark's analysis must show

So that two analyses can be read against each other, cover these in this order, each under a
numbered heading:

1. **Coverage** — what each model was willing to answer for, before any accuracy is shown.
2. **The distribution behind each summary number** — not the number again as a bar, but what it is
   made of: the curve rather than the point on it, the spread rather than the mean.
3. **Where the models disagree with each other** — pairwise, on the same photographs. Say plainly
   where agreement is not evidence: two models fitted on the same labels agreeing is one piece of
   evidence, not two.
4. **Where the models disagree with the readers** — for a dataset that kept its readers apart,
   separate the photographs the humans were unanimous about from the ones they were not. Being wrong
   where the readers disagreed is different trouble from being wrong where they did not.
5. **What the hard cases look like** — the photographs every model got wrong, as images, with what
   the dataset said about each.
6. **What the benchmark cannot say** — contamination marks that are `unknown` rather than clean,
   ground truths that are not comparable across datasets, and anything the metrics hide.

## 3. Grouping is the notebook's job

A run scores a whole dataset and writes `subset` and `split` into every row, so the notebook is
where those become questions: does this model behave differently on the portable camera? Does the
training half score higher than the test half, and by how much? **A grouping that turns out to
matter belongs in the results document too** — tell the report generator about it rather than
leaving the finding in a notebook nobody regenerates.

## 4. Writing for the reader

The prose rules of `CLAUDE.md` §4 apply: the reader is a clinician or a researcher, not a software
engineer. Markdown cells carry the argument and code cells the arithmetic; a notebook that is only
code is a script. Number every heading. Do not crown a winner — the last cell of an analysis is what
the numbers do not say, not a ranking.

## 5. Practical shape

- Read the results with two small functions at the top — one returning the per-image rows, one the
  summaries — so every later cell is about the analysis rather than about file paths.
- Keep paths relative to the notebook (`Path('..').resolve()`), so it runs from `notebooks/`.
- **Read a column, do not assume its dtype.** A true/false column comes back as booleans from one
  file and as floats once concatenated with a file where it is empty; map the text and let blanks
  fall out of the mean.
- Prefer one figure that answers a question over four that decorate it.
