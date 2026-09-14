---
name: report-benchmark
description: Generate the summary document a benchmark run writes into docs/benchmarks/ — its sections, what it must carry, and the rule that it is generated rather than written. Use when adding or changing src/benchmarks/report.py or a generated benchmark page.
---

# Reporting a benchmark

The document in `docs/benchmarks/<name>.md` is **written by the run**, not by hand, so that it
cannot drift from the numbers it describes. That is the whole rule, and everything else follows
from it: if a sentence in the document cannot be produced from `results/` and the run's own record,
it does not belong in the document — it belongs in the notebook, where judgement lives.

`src/benchmarks/report.py` holds the generator. A benchmark calls `write_report(name, scored)` at
the end of a run, and `--no-report` skips it.

## 1. Never hand-edit a generated page

Anyone may regenerate it; a hand edit is lost the next time anyone does, and a page that has been
hand-edited is no longer evidence of anything. The first paragraph of every generated document says
it is generated and where its numbers come from. To change what the page says, change the
generator.

## 2. The sections

Numbered, as `CLAUDE.md` §4.2 requires, and in this order:

1. **What ran** — one row per model: the page it links to, the pinned commit or version, the store
   grid it read, the grid its network actually saw, its ensemble size, and the processor it ran on.
   The pin is what makes a number attributable; the two grids are what make two numbers comparable.
2. **What it ran on** — one row per evaluation unit: how many photographs, and how many the dataset
   itself never gave a reference for. State the exclusions that applied, in one sentence.
3. **Coverage** — graded, declined and failed per model and unit, before any accuracy.
4. **The comparable question** — the one thing every model in this benchmark can be asked, with a
   threshold-free metric beside the threshold-dependent one, and **the contamination mark on every
   row**.
5. **Anything only some models can answer** — a three-class grade, a second structure, a variant of
   a biomarker — clearly marked as a smaller comparison than section 4.
6. **What these numbers do not say** — what each mark means, which models are `unknown` rather than
   cleared, and any assumption the run rests on.

Close with the command that generated the page and the date it was generated.

## 3. What it must always carry

- **The contamination mark on every result**, never aggregated away, and `unknown` never written as
  if it were `out-of-sample`.
- **The pins**: a number with no commit behind it is an anecdote.
- **Coverage beside every accuracy**, never folded into it.
- **A dash for a metric that does not exist** — a ROC AUC on a unit with one class, a three-class
  score from a binary model — never a zero, and never an omitted row.

## 4. What it must never do

- **Rank.** A benchmark page is a map, not a leaderboard: no "best", no ordering by score, no bold
  winner. Sort rows by model and unit, which is an order nobody can read as a verdict.
- **Restate an author's claim as ours**, or ours as theirs.
- **Average across units.** One number over three cameras and two splits hides exactly what the
  unit exists to show.
- **Explain away a bad number.** If a result needs an argument, the argument goes in the notebook.

## 5. Prose

Written for a clinician or a researcher (`CLAUDE.md` §4.1): every metric expanded on first use, no
jargon assumed, and the reason a number matters stated before the number. The generator holds those
sentences as literal text, which is the point — they are reviewed once, in a diff, rather than
rewritten differently in every run.
