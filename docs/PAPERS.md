# Papers

Published work a reader of this atlas needs in order to interpret something else in it: a formula,
a comparison, a pitfall, or a map of a subfield. Each row links to a detail page recording the
citation, what the paper is about in plain language, why it is here, and which catalogued datasets,
models, biomarkers or projects to open next.

This is not a bibliography of every paper the other catalogues cite. The describing paper of a
dataset, model or project stays on that entry's page. A paper gets a row here only when a reader
would change how they interpret a number, a mask or a comparison after reading it.

Four things about this catalogue are worth reading before the table.

**A name is not a definition.** "Tortuosity" and "CRAE" each point at more than one paper, and the
pipelines in [PROJECTS.md](PROJECTS.md) do not all implement the same one. The definition rows below
are the reason those biomarker pages exist.

**Claim and observation stay apart.** What a paper reports about its own sample is its authors'
claim, on the detail page. What this atlas measured is in [BENCHMARKS.md](BENCHMARKS.md).

**Open is effort to read, not permission to reuse.** A green mark is a publisher or PMC copy. A
yellow mark is a copy off the publisher — an author PDF or ResearchGate — that may move. A paper
behind a paywall can still be the definition of a measurement this atlas catalogues.

**One paper, one page.** A preprint and its journal version are one entry. A conference paper that
was later expanded is noted on the journal page, not given a row of its own.

## 1. Summary

Grouped by kind. Within each group, alphabetical by the first author's surname. Groups with no rows
yet are omitted; they appear when the first paper of that kind is added.

**Open** is how a reader actually gets the text:

| | |
| --- | --- |
| ✅ | **Publisher or PMC.** A stable, freely readable copy |
| 🟡 | **Off the publisher.** An author PDF, a preprint, or ResearchGate — usable, liable to move |
| ⛔ | **Paywalled**, and no stable free copy was established; see the page |

### 1.1 Definitions — papers that first published a measurement this atlas catalogues

| Paper | Year | What it is for | Relates to | Open | Last checked |
| --- | --- | --- | --- | --- | --- |
| [Bankhead 2012](papers/bankhead-2012.md) | 2012 | Vessel width from image edges, not from a mask | Calibre; ARIA; DRIVE | ✅ | 2026-09-21 |
| [Giesser 2024](papers/giesser-2024.md) | 2024 | A proprietary tortuosity score (VCI) and its five-minute retest | Tortuosity; AutoMorph | ✅ | 2026-09-21 |
| [Grisan 2008](papers/grisan-2008.md) | 2008 | Tortuosity as density of constant-sign bends | Tortuosity; retipy; AutoMorph | 🟡 | 2026-09-21 |
| [Hart 1999](papers/hart-1999.md) | 1999 | Seven tortuosity formulas, and which of them compose | Tortuosity; tracing | 🟡 | 2026-09-21 |
| [Hubbard 1999](papers/hubbard-1999.md) | 1999 | Central retinal equivalents and AVR, for ARIC | CRAE/CRVE; AVR | ⛔ | 2026-09-21 |
| [Knudtson 2003](papers/knudtson-2003.md) | 2003 | The scale-invariant revision most pipelines actually run | CRAE/CRVE; AVR; AutoMorphalyzer | ⛔ | 2026-09-21 |

## 2. How to read this table

- **Kind** — why the paper is here, not a field-wide taxonomy. `definition` is a first formula;
  `method` is a method whose artefact, if catalogued, lives on its own page; `comparison` is prior
  work this atlas's own scores should be read against; `finding` is a result that changes how a
  number here should be read (reproducibility, scale, a unit trap); `review` maps a subfield. A
  paper has one kind.
- **What it is for** — one phrase. The reason we kept it is on the page, in section 3.
- **Relates to** — the catalogued entry to open next. A paper with no such link does not belong
  yet.
- **Open** — effort to *read*. It says nothing about whether figures or text may be reused.
- **Known caveats** are not in this table. Every detail page carries a Notes section: an unpublished
  formula, a unit that only works in microns, a conference DOI a codebase cites instead of the
  journal's.

## 3. Adding a paper

Paper pages follow a fixed structure so they can be read against each other. Load the
`document-paper` skill, which defines that structure and this table's columns, before adding or
changing an entry. A describing paper of a dataset, model or project does not get a row here unless
it also does one of the jobs in section 1.
