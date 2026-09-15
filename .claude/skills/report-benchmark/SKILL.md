---
name: report-benchmark
description: Generate the two documents a benchmark run writes into docs/benchmarks/ — how it is configured, and what came out — their sections, and the rule that they are generated rather than written. Use when adding or changing src/benchmarks/report.py or a generated benchmark page.
---

# Reporting a benchmark

Every benchmark writes **two** documents, and they answer different questions:

```
docs/benchmarks/<slug>-docs.md      how this benchmark is configured and run
docs/benchmarks/<slug>-results.md   what came out
```

Both are **written by the run**, not by hand, so that they cannot drift from the numbers. That is
the whole rule, and everything else follows from it: if a sentence cannot be produced from
`results/` and the run's own record, it does not belong in either document — it belongs in the
notebook, where judgement lives.

**They are written at different moments, and that is deliberate:**

| Document | Written |
| --- | --- |
| `<slug>-docs.md` | **before the measuring starts**, and again after any change to the benchmark's code |
| `<slug>-results.md` | **after the measuring finishes** |

The configuration page describes what is *about to* happen — which models, which datasets, what is
excluded, what the columns will mean — and every word of it is known before a single photograph is
scored. Writing it first buys three things: somebody can read what a run is going to do before
committing hours of it, a run that dies halfway still leaves an accurate account of itself, and the
page cannot quietly describe a configuration other than the one that ran. The results page needs
the numbers, so it waits.

A change to the benchmark's code is therefore a change to the configuration page in the same
commit, run or no run: a column added to the evidence, a model added to the declared list, an
exclusion rule altered. Regenerating it costs nothing — it measures nothing.

`src/benchmarks/report.py` holds the generators. A benchmark calls them at the end of a run, and
`--no-report` skips them. **What only one benchmark's documents say lives in its own file beside
this one** — `quality.md`, and one per benchmark thereafter — and you load that file too.

| Benchmark | Its documents |
| --- | --- |
| Quality | [quality.md](quality.md) |

## 1. Never hand-edit a generated page

Anyone may regenerate one; a hand edit is lost the next time somebody does, and a page that has been
hand-edited is no longer evidence of anything. The first paragraph of each document says it is
generated and where its numbers come from. To change what a page says, change the generator.

## 2. `<slug>-docs.md` — how it is configured

This is what a reader opens **before** looking at a number. Numbered sections, in this order:

1. **What this benchmark asks** — the question, in one paragraph a clinician can read.
2. **Which models take part**, one row each: the page it links to, the pinned commit or version, the
   store grid it reads, the grid its network actually sees, its ensemble size, and what it emits.
   **Every declared model appears, including the ones that did not run**, with the reason — no
   adapter written yet — because a benchmark's list is what it asks for, not what it has.
3. **Which datasets take part**, one row each: photographs, where their reference grade comes from,
   what the run set aside and why, and anything about the store that bears on the result. **Every
   declared dataset appears, including the ones that did not run**, marked *no store built* or
   *excluded whole* — two different statements, never merged.
4. **What is excluded, and by which rule** — the size floor, the crop rule, the repository's own
   findings, and any dataset declared out whole.
5. **How to run it** — the command (`python -m benchmarks --benchmark <name>`), its options,
   how to re-measure a single model on a single dataset, and what a sampled run is for.
6. **What each column of the result CSV means** — every column, including the ones a given model
   leaves absent and why a model might have no opinion to record there.
7. **What a re-run would and would not repeat** — what the fingerprint covers, and the separate
   question of completeness: a complete result is never re-run, a partial one is finished, and
   nothing is truncated.
8. **The three counts every result carries** — `processed`, `total` and `excluded` with its reasons
   — and the warning that our `excluded` and the model's `declined` are different statements and are
   never added together.

**This page is updated whenever the benchmark's code changes.** A column added to the evidence that
section 6 does not explain is a bug, and so is a model added to the run that section 2 does not
list. Both come from the code, so both are generated rather than remembered.

## 3. `<slug>-results.md` — what came out

**Open with the summary, then descend into the detail.** Numbered sections:

1. **Model × dataset** — the headline table, one row per model and dataset, carrying the handful of
   numbers that matter for this benchmark, how many photographs each is measured on, and the
   contamination mark on every row.
2. **Coverage** — what each model was willing to answer for, before any accuracy is read.
3. **The detail** — the same models and datasets broken out by split, by subset, by camera, by
   whatever kinds the benchmark defines. Where a dataset's splits carry different contamination
   marks, the breakdown is **required**, not optional: one number over a training and a test half is
   not a result.
4. **Anything only some models can answer** — clearly marked as a smaller comparison than section 1.
5. **What these numbers do not say** — what each mark means, which models are `unknown` rather than
   cleared, and any assumption the run rests on.

**The model is the primary index and the dataset, split or kind the secondary one, in every table.**
A reader arriving from a model page finds that model's rows together; two tables can be read against
each other because they are ordered alike.

## 4. And one index across every benchmark

`docs/BENCHMARKS.md` is generated as well, from what is on disk rather than from the run that has
just finished — so running one benchmark cannot blank another's section. It holds one section per
benchmark, each linking to that benchmark's two pages, and one row per model and dataset carrying
the same headline numbers as that benchmark's own section 1. It is the page somebody arrives at
from the README, so it repeats the two warnings that matter: that a row is comparable only with
rows carrying the same mark, and that a dash is a metric with nothing to measure rather than a
score of zero.

## 5. What both documents must always carry

- **The contamination mark on every result**, never aggregated away, and `unknown` never written as
  if it were `out-of-sample`.
- **The pins**: a number with no commit behind it is an anecdote.
- **Coverage beside every accuracy**, never folded into it.
- **A dash for a metric that does not exist** — a ROC AUC on a dataset with one class, a three-class
  score from a binary model — never a zero, and never an omitted row.
- **A partial run says so**, in the first paragraph and in every table it touches, with how many of
  the dataset were scored out of how many it holds.
- **A run missing a declared piece says so in its first paragraph** — how many models of how many
  declared, how many datasets of how many — so that nobody reads four models as the whole field.

## 6. What they must never do

- **Rank.** A benchmark page is a map, not a leaderboard: no "best", no ordering by score, no bold
  winner. Sort by model and dataset, which is an order nobody can read as a verdict.
- **Restate an author's claim as ours**, or ours as theirs.
- **Average across datasets.** One number over four collections hides exactly what the datasets
  exist to show.
- **Explain away a bad number.** If a result needs an argument, the argument goes in the notebook.

## 7. Prose

Written for a clinician or a researcher (`CLAUDE.md` §4.1): every metric expanded on first use, no
jargon assumed, and the reason a number matters stated before the number. The generators hold those
sentences as literal text, which is the point — they are reviewed once, in a diff, rather than
rewritten differently in every run.
