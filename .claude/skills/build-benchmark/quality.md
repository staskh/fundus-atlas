# The quality benchmark

Load this beside `SKILL.md` before building or changing `src/benchmarks/quality.py`. Everything
here is particular to quality; everything shared is in the main file.

**What it asks:** can a model tell whether a fundus photograph is good enough to measure?

```
python -m benchmarks --benchmark quality
python -m benchmarks --benchmark quality --model quickqual --dataset fives   # one pair
python -m benchmarks --benchmark quality --max-samples 20                    # a run that finishes in a minute
```

## 1. What takes part, and why

**Models** — every catalogued model whose purpose class is `quality`:

| Model | Emits |
| --- | --- |
| [fit-quality](../../../docs/models/fit-quality.md) | one probability that the photograph is gradeable |
| [vascx-quality](../../../docs/models/vascx-quality.md) | three class scores, read as good, usable and bad |
| [automorph-quality-grader](../../../docs/models/automorph-quality-grader.md) | three: good, usable, reject |
| [quickqual](../../../docs/models/quickqual.md) | three: good, usable, bad |
| [quickqual-meme](../../../docs/models/quickqual-meme.md) | one probability that the photograph is bad |

**Datasets** — those that grade the photograph itself, minus what section 2 of the main skill
excludes. [DeepDRiD](../../../docs/datasets/deepdrid.md) is held back because the toolbox ensemble
trained on it; [EyeQ](../../../docs/datasets/eyeq.md) and
[DRIMDB](../../../docs/datasets/drimdb.md) are in-sample for three of the five and are wanted for
exactly that reason.

**Declare a dataset before it is fetched.** EyeQ and DRIMDB belong in this benchmark's list now: the
run will warn that their stores are not built, say so on the documentation page, and measure the
rest. That warning is the benchmark asking for the fetcher, and it is better than a list that
silently describes only what happens to exist.

## 2. The three kinds of reference, and why the column exists

`quality_source` in the store says where a dataset's grade came from, and the three are not the
same statement:

| Source | What it is | Example |
| --- | --- | --- |
| `published` | the dataset's own verdict | FQS, MSHF |
| `derived` | this repository's, computed from the components the dataset published | FIVES |
| `assumed` | this repository's supposition that a curated dataset is all sound | PAPILA |

Three consequences the benchmark must respect:

- **A reference need not use all three grades.** MSHF publishes good and bad only, so a model's
  `usable` is counted as a mistake there however sensible it was. The scorer records which grades a
  reference actually used, and the report names the missing ones rather than letting a dash read as
  the model's failure.
- **A photograph the dataset never graded is `rejected`, with `no reference` as the reason** — 19 of
  MSHF's. It is not a failure of the model and is never counted as one; it is one of the three
  counts every result carries.
- **An `assumed` reference contains no bad photographs at all.** No ranking metric is defined on it,
  and what it measures instead is how much of a sound dataset a model would throw away.
- **A derived grade measures the derivation too.** Say so beside the number.

## 3. What is measured

Three levels, and a model appears in a level only if it can answer it:

1. **Worth measuring, or not** — the one question all five can be asked. Good and usable count as
   yes, bad as no. Accuracy, ROC AUC and Cohen's κ. The confidence ranked is `gradeable`: for a
   three-class model, `good + usable`; for a scalar model, its own number.
2. **The three grades** — only for models that name all three. Accuracy, quadratic κ, **per-grade
   recall** and the full confusion. Recall on `usable` is the number that shows whether the middle
   class means anything: a model can score well overall while never once getting it right.
3. **The gate its project applies** — section 4.

**Never invent a class a model does not have.** A scalar model has no `usable` to report, and
splitting its number into bands would put an opinion in the table that the model never held. Its
`good`/`usable`/`bad` columns are absent, not blank.

## 4. A grade is not a decision

What reaches measurement is decided by the **pipeline**, by a rule that belongs to it rather than to
the model — and sometimes a rule that overrides the model's own verdict. Each adapter declares the
gate its project applies, in prose and with any constant it acts on declared as a number, and the
benchmark scores those gates on the same question as level 1:

| Project | Its rule |
| --- | --- |
| AutoMorph | `good` passes; `usable` passes only while `p(bad) < 0.25`; everything else is dropped before any segmentation model sees it |
| Fundus Image Toolbox | its own default threshold of 0.5; it is a library, not a pipeline |
| AutoMorphalyzer | **carries every photograph**, whatever QuickQual-MEME says, and never reads the column again |
| VascX | none: three logits are written to `quality.csv` and nothing reads them |
| AutoMorphClass | no quality stage at all |

The column to read is **how often a pipeline disagrees with its own model** — 217 FQS photographs
and 48 PAPILA ones for AutoMorph, where the middle-class rule overrode the grade the network gave.

## 5. Declining, and who is declining

A model **declines** on its own judgement; none of these five does. Where a pipeline refuses a
photograph — AutoMorph's preprocessing dropping one whose fundus it cannot find — that refusal
belongs to the pipeline, and this benchmark runs the models without the pipelines around them, with
the store's field-of-view crop standing in. Coverage is therefore 1.00 throughout, and the report
says why rather than letting the reader assume the machinery did nothing.

## 6. Traps this benchmark has already fallen into

- **A threshold that does not transfer.** The toolbox ensemble ranks FIVES at 0.97 by ROC AUC and
  scores 0.54 by accuracy at its own default threshold. Both numbers are published, neither alone
  is "the score".
- **Two models agreeing is not two pieces of evidence.** QuickQual, QuickQual-MEME and the AutoMorph
  grader were all fitted on EyeQ labels. Their agreement is expected; agreement with the toolbox
  ensemble, trained elsewhere, is the informative number.
- **The black canvas is a fact about the store, not the dataset.** A fundus cut off at top and
  bottom leaves bands in a square crop — 18.8% of PAPILA's — and a quality model judges the square
  it is handed. The share is reported per dataset. When PAPILA's rejection rate was investigated,
  trimming the bands made it *worse*, so the canvas was not the cause; report the check, not the
  assumption.
