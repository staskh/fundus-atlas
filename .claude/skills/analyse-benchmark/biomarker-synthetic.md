# Analysing the synthetic biomarker benchmark

Load this beside `SKILL.md` when changing any of the synthetic biomarker benchmark's notebooks. **The
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

**The notebooks are one per lineage, beside one across them, and one results page is compiled
from all four.** They live in `notebooks/synthetic/`:

| Notebook | Holds |
| --- | --- |
| `biomarker-synthetic.ipynb` | the **summary**: every implementation of every group, by canonical name (§2 below), then the three groups compared (§2.3) |
| `biomarker-synthetic-automorph.ipynb` | AutoMorph, AutoMorphalyzer, AutoMorphClass (§2.2) |
| `biomarker-synthetic-pvbm.ipynb` | PVBM, OCULAR |
| `biomarker-synthetic-vascx.ipynb` | VascX |
| `biomarker-synthetic-shapes.ipynb` | the shapes and the values each settles — the specification, not an analysis |
| `wip/` | readings of one implementation on a few shapes; not of record (`notebooks/wip/README.md`'s rules) |

*Why per lineage, when every other benchmark has one notebook* (agreed with Stas, 2026-11-22): a
lineage is the unit a reader chooses software by, and a group notebook can go further into its
members than a seven-column table can — its own columns held to their authors' descriptions, its
cup-to-disc ratios, the best and worst biomarker of each member. What it **cannot** do is compare
across lineages, so the summary keeps that, by canonical name, and no group notebook is a
substitute for it. The group is the benchmark's own `GROUPS`, never a notebook's private list.

**Shared arithmetic lives in `src/benchmarks/synthetic_evidence.py`** — the reading, the noise
floor, `spread`, `error`, the tables and the two figures. Four notebooks that each defined their own
error would disagree about it within a month. A notebook calls it and argues about what it shows.

**Order the columns so that siblings stand together** — implementations sharing a lineage beside
each other, independent ones apart — so that a difference between neighbours is a change somebody
made on purpose, and a difference across the gap is two programs that never shared a line of code.

### 1.1 The order of the columns

Take it from the benchmark's own `GROUPS`, which is **kept in lineage order** for exactly this
reason, and never re-sort it alphabetically:

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
| Claimed truth | the store's `ground_truth_claimed.csv` | what each **unnamed** column's own description requires (§2.1) |

A run records none of the last three. Joining them here is what lets the same evidence be re-read
against a corrected mapping or a corrected ground truth without measuring anything again.

### 1.3 Two kinds of ground truth

- **By canonical name**, for every column an adapter maps onto the vocabulary: the definition the
  catalogue records, from the paper that introduced it where there is one.
- **By the column's own description**, for every column the vocabulary cannot name:
  `src/benchmarks/shapes/claims.py` reads each one the way its authors describe it — its name, its
  docstring, the paper it cites — and either points at the catalogued biomarker that description
  *is* (AutoMorph's `squared_curvature_tortuosity` cites Hart and is named for his τ3, though the
  adapter withdrew that mapping because the code does not compute it) or derives the value from the
  geometry (PVBM's tortuosity index, total arc over total chord). A description the shapes cannot
  settle — anything needing a fovea — is listed with the reason, never silently skipped.

The two are never pooled. A canonical fault says a mapped number is wrong; a claimed fault says a
program's column does not compute what its own authors say it does, which is the claim-against-
observation comparison `CLAUDE.md` §1 asks of every catalogued project.

### 1.4 What turning the picture is meant to move

The vertical and horizontal cup-to-disc ratios are read along the image's axes, and so are a cup's
height in pixels and where its centre lands. Their truth changes with the angle **by design**, so
every rotation check leaves them out: the named ones by `truth.TURN_WITH_THE_IMAGE`, the unnamed
ones by `claims.turning`, which reads them off the claimed table rather than a hand-kept list. Their
agreement with the geometry is checked at each angle like anything else.

## 2. The sections, in order

These are the **summary** notebook's. §2.2 gives the group notebooks' and §2.3 the comparison the
summary adds across groups.

| # | Section | Must show |
| --- | --- | --- |
| 1 | General statistics | how much each implementation produced, and how much of it can be compared |
| 2 | Hard failures | every exception, with what raised it and on which image |
| 3 | Sensitivity to rotation | what moves when the same shape is turned |
| 4 | Agreement with ground truth | what is far from the value the geometry requires |
| 5 | Summary | the two counts a reader takes away |

### 2.1 Two tolerances, named once and used everywhere

*(Declared in `synthetic_evidence` and read from there by every notebook.)*

| Constant | Value | Applies to |
| --- | --- | --- |
| `ROTATION_TOLERANCE` | **10%** | a spread across angles wider than this is a finding |
| `GROUND_TRUTH_TOLERANCE` | **25%** | a value further than this from the geometry is a fault |

Declare both at the top of the notebook as named constants, not as numbers buried in a filter. They
are reporting conveniences rather than standards anybody agreed, and the notebook says so.

### 2.2 A group notebook's sections

| # | Section | Must show |
| --- | --- | --- |
| 1 | Coverage | per member, columns returned, named, unnamed, and how many unnamed ones are held to their own description; then every unnamed column with what it claims |
| 2 | Hard failures | as the summary's §2 |
| 3 | Sensitivity to rotation | by canonical name (table and heat map), then the unnamed columns |
| 4 | Agreement with ground truth, by canonical name | worst over everything (table and heat map), every signed error as a dot for what is out of tolerance, per shape, by kind, and where the geometry gives no value |
| 5 | Agreement with their own description | every unnamed column against its claim, worst and median, and the signed errors |
| 6 | Cup-to-disc ratios | *AutoMorph's group only*: measured against the required ratio at each angle |
| next | The best and the worst biomarkers | per member, its canonical biomarkers by worst then median error — every one inside the floor as *best*, the five furthest as *worst*, with the shape — then the same across the group by its closest member |
| last | Summary | per member: moving with the image, disagreeing by canonical name, disagreeing with its own description, median error, exceptions, seconds |

The findings are **written into the notebook as prose** beneath the tables they read, after it has
been run: a group notebook that only prints is a script.

**Best and worst order biomarkers, never implementations.** They say which of a program's numbers
can be taken at face value on these shapes; ranking the programs is §8's rule.

### 2.3 The summary's comparison across groups

After its §5, the summary compares the three lineages by canonical name. A group answers a name with
its **closest member** — the one whose worst error is smallest — so a cell says what the best of
that lineage can do, and the group notebook says what each member does. It shows, in order: how many
names each group answers, per family; the worst error per name and group where two or more groups
answer, as a table and a heat map; the same for rotation; a per-family count of names within
tolerance; and each group's best and worst names side by side. Then **which group to reach for, at a
named question** — calibre, tortuosity, density, topology, the cup — argued in prose with the
runner-up and the caveats (`report-benchmark` §5).

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
one shape and right on twelve is a different finding from one wrong on all thirteen, and the main
table cannot tell them apart. Number these beneath the main table's own subsection (4.1.1, 4.1.2,
…) so they cannot collide with the fixed subsections after it.

**Then three subsections the ground truth's own structure requires** (`build-benchmark`'s
`biomarker-synthetic.md` §2.2):

- **By how the value is known** — the faults counted separately against `exact`, `numerical`,
  `asymptotic` and `convention` values, read from `ground_truth_kind.csv`. A fault against an exact
  value is a fault; one against a convention is a question about the definition, and pooling them
  would make the second look like the first.
- **Where the geometry gives no value** — every number an implementation returned for a biomarker
  the shape settles as having none (`store.undefined`), per canonical name and implementation, as
  a fraction of the renderings it was asked about. Declining there is the right answer, and a
  number is invented.
- **The categorical answers** — the photograph's centring, a word rather than a number, compared
  with the framing it was drawn in. It never enters a numeric table.

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
