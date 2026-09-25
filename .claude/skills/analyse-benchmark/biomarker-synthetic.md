# Analysing the synthetic biomarker benchmark

Load this beside `SKILL.md` when changing the synthetic biomarker benchmark's notebook. **The
canonical biomarker name is the primary index** throughout, and the implementation is the column —
which is the opposite way round from every other benchmark here, where the model leads. It is that
way because the question is *do these programs compute the same quantity*, and a reader answering
it reads across a row.

## 1. What this benchmark is, and what the notebook opens by saying

The intro states, in this order and in plain terms:

- **It measures over synthetically generated segmentations** — drawn arteries, veins and an optic
  disc, not photographs. No eye was photographed and no annotator was consulted.
- **There are two kinds of benchmarking here, and they are different questions.**
  1. **Sensitivity to rotation.** The same shape is drawn at several angles. The geometry is
     identical at each, so anything that moves is the implementation or the pixel grid. This needs
     no ground truth at all — it is a self-consistency check, and an implementation can fail it
     while agreeing with the ground truth on average.
  2. **Agreement with ground truth.** The **ground truth is a theoretical value stored alongside
     the images**, derived from the geometry before anything was drawn — not an annotation, not
     another program's output. An implementation that disagrees with it is wrong rather than
     different.
- **How to read the tables.** Unless a section says otherwise, every result is a table whose
  **rows are canonical biomarker names** and whose **columns are implementations**. Where a
  quantity was measured on several shapes or at several angles, the cell is the **worst** of them,
  because a mean would hide the case that matters.

**One notebook holds every implementation, and one results page is compiled from it.** There is no
notebook per implementation and none per family: the comparison *is* the result, and a table split
by implementation cannot be read across. **Order the columns so that siblings stand together** —
implementations sharing a lineage beside each other, independent ones apart — so that a difference
between neighbours is a change somebody made on purpose, and a difference across the gap is two
programs that never shared a line of code.

### 1.1 The order of the columns

Take it from the benchmark's own `IMPLEMENTATIONS`, which is **kept in lineage order** for exactly
this reason, and never re-sort it alphabetically:

| Columns | Why they stand together |
| --- | --- |
| `pvbm`, `ocular` | OCULAR imports PVBM's measuring code, so a difference between these two is something OCULAR did on purpose |
| `automorph`, `automorphalyzer`, `automorphclass` | the two descendants both fork AutoMorph's measuring stage; reading them side by side is what shows what each changed |
| `vascx` | shares no code with any of the above — it reimplements every biomarker, so a disagreement across this boundary is two independent readings of the same definition |

A gap between groups therefore means something a reader can use: **within** a group, a difference is
an edit; **across** one, it is two programs that never shared a line.

### 1.2 Where the three inputs come from

The notebook does the join that the benchmark deliberately does not:

| Input | Where | What it gives |
| --- | --- | --- |
| Evidence | `results/biomarker-synthetic/<implementation>/<shape>.csv` | what each program returned, under **its own** column names |
| The mapping | each adapter's `declare()["names"]` | which catalogued biomarker each of those columns is believed to answer to, or `None` |
| Ground truth | the drawn store's `ground_truth.csv` | what the geometry requires, under canonical names |

A run records none of the second two. Joining them here is what lets the same evidence be re-read
against a corrected mapping or a corrected ground truth without measuring anything again.

## 2. The sections, in order

| # | Section | Must show |
| --- | --- | --- |
| 1 | General statistics | how much each implementation produced, and how much of it can be compared |
| 2 | Hard failures | every exception, with what raised it and on which image |
| 3 | Sensitivity to rotation | what moves when the same shape is turned |
| 4 | Agreement with ground truth | what is far from the value the geometry requires |
| 5 | Summary | the two counts a reader takes away |

### 2.1 Two tolerances, named once and used everywhere

| Constant | Value | Applies to |
| --- | --- | --- |
| `ROTATION_TOLERANCE` | **10%** | a spread across angles wider than this is a finding |
| `GROUND_TRUTH_TOLERANCE` | **25%** | a value further than this from the geometry is a fault |

Declare both at the top of the notebook as named constants, not as numbers buried in a filter. They
are reporting conveniences rather than standards anybody agreed, and the notebook says so.

## 3. Section 1 — general statistics

One table, implementations as columns, these rows:

| Row | Meaning |
| --- | --- |
| Biomarkers produced | how many columns the implementation returns at all |
| …with a value | how many of those are not empty on at least one rendering |
| Matching a canonical name | how many its adapter maps onto the catalogue |
| …with a value | how many of *those* are not empty |
| Unnamed, with values | quantities it computes and returns that match no canonical name |
| Seconds per image | mean processing time, from the evidence |

The middle rows are the ones that matter: an implementation returning forty columns of which eight
can be compared is in a different position from one returning eight that all can, and a single
count of "columns" hides it.

**Then one subsection per implementation — 1.1, 1.2, and so on — listing the biomarkers that
matched no canonical name.** Naming them is the point: each is either a gap in the catalogue or a
mapping nobody has made yet, and the list is what turns "eleven unnamed columns" into work somebody
can do.

## 4. Section 2 — hard failures

Every exception, per implementation: **which biomarker, which image, which rotation**. A table, not
prose, and complete rather than summarised — it exists to be debugged from later, so a reader must
be able to reproduce one from the row alone.

A failure is not a bad measurement. An implementation that raises has told you it could not answer;
one that returns a confident wrong number has not. Keep the two apart here and everywhere.

## 5. Section 3 — sensitivity to rotation

The geometry is identical at every angle, so **any spread is the implementation or the grid**.

- Table indexed by canonical name, columns the implementations, **filtered to names where at least
  one implementation exceeds `ROTATION_TOLERANCE`**. Each cell is the **worst spread that quantity
  showed on any shape**, as a percentage of its mean on that shape — every shape pooled into one
  number, because a quantity that turns with the image on one shape turns with the image.
- Then **one subsection per implementation** doing the same for its **non-canonical** columns —
  the quantities nothing can compare against are as capable of turning with the image as the ones
  that can, and nothing else in this notebook would notice.

Filtering to the offenders is deliberate: a table of two hundred rows that are all zero hides the
five that are not.

## 6. Section 4 — agreement with ground truth

**The main table** is indexed by canonical name with the implementations as columns, **filtered to
those with at least one fault**, and each cell is the **worst disagreement over every shape and
every angle**, as a percentage of the ground truth. One number per implementation per biomarker:
the worst case it produced anywhere.

**Then one subsection per shape**, the same table for that shape alone — worst over its rotations.
The main table says *whether* a biomarker is trustworthy; the per-shape tables say *where* it
stopped being so, which is what turns a number into something to investigate. A biomarker wrong on
one shape and right on seven is a different finding from one wrong on all eight, and the main
table cannot tell them apart.

Only canonical names appear, because only they have a ground truth to disagree with. A quantity an
implementation computes under a name the catalogue does not know is measured, stored, and absent
from this section — which is a gap in the catalogue or in the shapes, and section 1's subsections
are where a reader is told which quantities those are.

## 7. Section 5 — summary

Two counts, each as a fraction so the denominator is visible:

- **biomarkers with a rotation problem**, over the total that returned a value;
- **biomarkers that disagreed with the ground truth**, over the total that match a canonical name.

The denominators are different on purpose and the summary says why: rotation can be checked on
anything that returned a number, and agreement only on what the catalogue can name and a shape can
settle.

## 8. What this analysis must not conclude

- **That an implementation is good or bad, as a ranking.** No column is scored and no order is
  published. What the notebook *may* do — and should — is **argue for the best at a named
  question**: which implementation to reach for if what matters is calibre, or tortuosity, or
  surviving a rotation, with the evidence for it and the caveats that would change the answer.
  That is `report-benchmark` §5's rule, and the difference is between an argument a reader can
  disagree with and a league table they cannot.
- **That a quantity with no ground truth is wrong**, or right. It is unchecked.
- **That agreement between two implementations means either is correct.** They can share a lineage,
  and two of these do — agreement is evidence about their common ancestor, not about the truth.
