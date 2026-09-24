---
name: analyse-benchmark
description: Write the notebook that explains a benchmark's numbers — the distributions behind each summary figure, where models disagree with each other and with the readers, and what the failures look like. Use when adding or changing anything under notebooks/.
---

# Analysing a benchmark

Every benchmark produces four things for three readers: `results/` holds the evidence, the two
generated documents in `docs/benchmarks/` hold the configuration and the facts, and **the notebook
holds the judgement**. They are separate artefacts because a table saying a model scores 0.82 cannot
say that the 0.82 is two populations and that one of them is a camera.

One notebook per results page, `notebooks/<stem>.ipynb`, and usually that is one per benchmark,
named by the stems its `REPORTS` declares so that a notebook and the page compiled from it carry
the same name.

**A benchmark may instead analyse every subject in one notebook**, where the question it asks is
whether they agree with each other rather than how each behaves. The synthetic biomarker benchmark
is the case: its rows are catalogued biomarker names and its columns are implementations, because
a reader asking "do these programs compute the same quantity" reads across a row, and splitting
that table by implementation would destroy the comparison the benchmark exists to make. **What only one benchmark's analysis
must show lives in its own file beside this one** — `quality.md`, and one per benchmark thereafter —
and you load that file too.

| Benchmark | Its analysis |
| --- | --- |
| Quality | [quality.md](quality.md) |
| Disc and cup | [disc.md](disc.md) |
| Biomarkers against arithmetic | [biomarker-synthetic.md](biomarker-synthetic.md) |

## 1. An existing notebook is extended, never rewritten

A notebook that already exists carries work this skill does not know about: sections added in
conversation, a diagnostic somebody wrote for one afternoon, a cell that answers a question nobody
wrote down. **Edit it in place — add sections, extend cells, renumber what follows — and remove
nothing.** Regenerating the file from a template destroys exactly the material that made it worth
keeping, and it does so silently, because the diff of a rebuilt notebook is unreadable.

Three practical consequences:

- **Add, then renumber.** A new subsection under section 2 pushes 2.1 to 2.2; fix the headings and
  leave the content alone.
- **Where a section must change, change what is wrong with it** rather than replacing the section.
- **If a rewrite really is needed** — the analysis has been superseded outright — say so and ask
  first. The notebook is the one artefact here that is not reproducible from the code.

## 2. What a notebook may and may not do

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

## 3. The model is the primary index

**Every table and every figure is indexed by model first, dataset second.** The question this
repository asks is how a piece of software compares with an expert's judgement, so the reader is
looking for a model — a row per model, datasets within it — and two analyses can only be read
against each other if they are ordered alike. A table indexed by dataset with models inside it
answers a question nobody asked: it compares datasets.

The same ordering holds in the generated results page, so a figure in a notebook and a table in a
document line up.

## 4. What every benchmark's analysis must show

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
   the dataset said about each, **and with the dataset named beside every one**. Take them from
   each dataset in turn rather than from the pile: a grid drawn from whichever dataset happens to
   have the most failures is a picture of that dataset, not of the benchmark.
6. **What each model costs to run** — the seconds per photograph every result records, beside the
   device it was measured on. A model twice as slow for a hundredth of agreement is a different
   proposition at fifty thousand photographs than at fifty, and that trade is invisible in an
   agreement table. Say plainly that the number measures this machine as much as the model.
7. **What the benchmark cannot say** — contamination marks that are `unknown` rather than clean,
   ground truths that are not comparable across datasets, and anything the metrics hide.

## 5. A benchmark may need a second notebook, about the reference

`<name>.ipynb` asks how the models did. Where a benchmark's datasets publish **each reader's own
opinion**, a companion notebook — `<name>-humans.ipynb` — asks what the reference itself is worth,
and it belongs beside the first rather than inside it:

- how often the readers simply agree, and how often beyond chance;
- whether the published consensus is the majority, and what happens where it is not;
- what they disagree *about*, where a dataset rates components separately;
- and the comparison the benchmark cannot make on its own: **model against the consensus, beside
  reader against reader, on the same κ scale.** A model at or above the reader band is matching a
  committee rather than beating an expert; a model below it has room that is unambiguously its own.

Keep it separate because it answers a different question and has a different audience: the first
notebook is read by somebody choosing a model, the second by somebody deciding whether to trust a
dataset. Findings about a dataset go on that dataset's page, in the same commit.

## 6. Grouping is the notebook's job

A run scores a whole dataset and writes `subset` and `split` into every row, so the notebook is
where those become questions: does this model behave differently on the portable camera? Does the
training half score higher than the test half, and by how much? **A grouping that turns out to
matter belongs in the results document too** — tell the report generator about it rather than
leaving the finding in a notebook nobody regenerates.

## 7. Writing for the reader

The prose rules of `CLAUDE.md` §4 apply: the reader is a clinician or a researcher, not a software
engineer. Markdown cells carry the argument and code cells the arithmetic; a notebook that is only
code is a script. Number every heading. Do not crown a winner — the last cell of an analysis is what
the numbers do not say, not a ranking.

## 8. It must run top to bottom in a clean kernel

A notebook is read by somebody who opens it and presses run. Two failures follow from forgetting
that, and both have already happened here:

- **A cell that uses a name a later cell defines.** It works while you are editing, because the
  name is still in the kernel from the run before, and fails for everybody else. Define shared
  names — the frames, the model and dataset lists — **in the first code cell**, and let later cells
  only read them.
- **A path that assumes where the reader started.** An editor opens a notebook with the workspace
  root as the working directory, a terminal opens it from `notebooks/`, and `Path('..')` is right
  in one and wrong in the other. **Find the repository** by walking up for a marker, and say so in
  a sentence when nothing above the working directory looks like it.

**Verify by running it that way**, in a fresh process, stopping at the first cell that raises.
A harness that catches each exception, prints it and carries on will report success while a cell in
the middle is broken — which is exactly how both of these reached the repository.

Say what is missing rather than what broke: a notebook with no results to read should name the
directory it looked in and the command that fills it, not raise "No objects to concatenate".

## 9. Practical shape

- Read the results with two small functions at the top — one returning the per-image rows, one the
  summaries — so every later cell is about the analysis rather than about file paths.
- **Read a column, do not assume its dtype.** A true/false column comes back as booleans from one
  file and as floats once concatenated with a file where it is empty; map the text and let blanks
  fall out of the mean.
- Prefer one figure that answers a question over four that decorate it.
