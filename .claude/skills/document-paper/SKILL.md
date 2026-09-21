---
name: document-paper
description: Catalogue a paper that changes how a reader of Fundus Atlas should interpret a dataset, model, biomarker, project or comparison — as a page in docs/papers/ plus a row in the docs/PAPERS.md summary table. Use when adding, updating, or reviewing a paper entry, or when collecting interesting papers for the atlas.
---

# Documenting a paper

A **paper** here means a published work a reader of this atlas needs in order to interpret
something else in it: a formula, a comparison, a pitfall, or a map of a subfield. It is not a
bibliography of every paper the other catalogues cite.

The other catalogues record things you can download, run, or compute. The paper that *defined* a
measurement, or that showed why two numbers under the same name are not the same number, has no
home there except a citation line. This catalogue is that home.

**Do not catalogue** the describing paper of a dataset, model or project just because that entry
cites it. Those citations stay on those pages. A describing paper gets a papers page only when it
also does one of the jobs in section 2's kind table — Bankhead 2012 is the worked example: it is
the ARIA project paper *and* the definition of record for vessel calibre, so it has both pages,
cross-linked.

**One paper, one page.** A preprint and its journal version are one entry, with both links. An
earlier conference version of the same work is noted on that page, not given a page of its own.

## 1. What you produce

Every paper produces exactly two things:

1. **A detail page**, `docs/papers/<slug>.md`, following `template.md` in this skill directory. The
   slug is the first author's **surname** and the year — never a given name (`Knudtson 2003`
   becomes `knudtson-2003.md`; Mohamed Naim A becomes `naim-2026.md`, displayed as Naim 2026). If
   two papers collide, add a short topic (`hart-1999-tortuosity.md`). ASCII, lowercase, hyphens.
2. **A row in `docs/PAPERS.md`**, the summary table, linking to that detail page.

Never write one without the other.

## 2. Required sections of the detail page

Use `template.md` verbatim and keep its section numbering. The sections are:

1. **Citation** — a table, not prose, so the same facts sit in the same place on every page:

   | Row | Content |
   | --- | --- |
   | Title | The paper's own title |
   | Authors | As published |
   | Venue | Journal or conference, year, volume and pages |
   | DOI | Required. A stable link; if there is no DOI, say so and give the best stable URL |
   | Open copy | `publisher` / `PMC` / `preprint` / `author PDF` / `none established` — and the URL. **For Kaggle, ResearchGate and personal sites, give the full URL and treat it as liable to move.** A GitHub copy of the authors' code is not an open copy of the paper; it belongs in **Code** |
   | PMID / PMC | Where they exist, so a paywalled DOI still has a lookup |
   | Code | The authors' own repository or archive, full URL, or `none established`. If this atlas catalogues that software as a project, link the project page as well |
   | Dataset | The data deposit **released with this paper**, full URL, or `none established`. If catalogued here, link the dataset page. A public set the authors only *used* (DRIVE, say) belongs in Relates to, not here |
   | Other | Weights, a Zenodo snapshot, a MATLAB reference, a supplement — anything else they point at as accompanying material — or `none established` |

   The conference version of a later journal paper belongs as a line under the table, not as a
   second table. Caveats about those materials — no licence, no weights, a code dump that does not
   compute the number the paper reports — belong in Notes, not in the table.

2. **What it is about** — in plain language, for a clinician or researcher. What question the paper
   asked, what it did, and what a reader of this atlas would take from it. No formulas here; those
   belong on the biomarker page this paper defines, if it defines one.

3. **Why it is in this atlas** — the specific reason we kept it, in two or three sentences. This is
   the section that stops the catalogue becoming a bibliography. If you cannot fill it, the paper
   does not belong yet.

   Then record the **kind**, which is one of exactly five values and never a new one:

   | Kind | What belongs in it |
   | --- | --- |
   | `definition` | First published a measurement this atlas catalogues, or the revision the field actually uses |
   | `method` | Proposes a method whose artefact, if catalogued, lives on its own dataset, model or project page |
   | `comparison` | Compares methods or datasets on shared terms — prior work this atlas's own comparisons should be read against |
   | `finding` | A result that changes how a number in this atlas should be read: reproducibility, scale, a disc-size assumption, a unit trap |
   | `review` | Maps a subfield this atlas covers |

   A paper has **one** kind: the reason it is here. Bankhead 2012 introduced software *and* defined
   a measurement; it is a `definition` because that is why it has a papers page as well as a
   project page. Clinical association papers belong only as `finding`, and only when they are why
   this atlas treats a biomarker as worth measuring — not every epidemiology paper that used CRAE.

4. **What the authors claim** — their results, labelled as theirs. Give the claim, the sample it
   was measured on, and the number where there is one. Do not restate it as this atlas's finding,
   do not compare two papers' numbers as though they were measured the same way, and do not paste
   the abstract.

5. **Relates to** — every catalogued dataset, model, biomarker or project a reader should open next,
   with one short clause on the relationship (`defines`, `introduced`, `used as the comparator`,
   `masks came from`). A paper with no such link does not belong yet. Where this paper introduced
   a catalogued artefact, that artefact's page must link back, in the same commit.

6. **Notes** — anything a reader needs in order not to be misled: a formula that is unpublished, a
   unit that only works in microns, a free PDF that is not the publisher's copy, a conference
   version whose DOI a codebase cites instead of the journal's, code that does not compute the
   number the paper reports.

A section that does not apply stays in the page, marked `Not applicable` with a short reason. A
section whose answer could not be established is marked `Unknown` — never filled with a guess.

## 3. Rules that apply to every entry

- **3.1 Reference, never redistribute.** Link to the publisher, PMC, a preprint, or a stable author
  copy. Do not commit PDFs to this repository (see `CLAUDE.md` §2).
- **3.2 Separate claim from observation.** Section 4 is the authors' claims. A misuse this atlas
  has found in an implementation of their formula belongs on the biomarker or project page, with a
  pointer from Notes.
- **3.3 Write for a non-engineer.** Section 2 must be readable by someone who will never open the
  code.
- **3.4 Number every heading**, as the template does.
- **3.5 Date what you checked**, at the bottom of the page — DOIs and open copies move.
- **3.6 Keep the catalogues consistent.** A paper page that says it defines a biomarker requires
  that biomarker's definition-of-record section to link here, in the same commit. The same for a
  project, model or dataset this paper introduced.
- **3.7 Do not summarise copyrighted text at length.** Cite, paraphrase the claim, point at the
  DOI. The detail a reader needs to compute a number lives on the biomarker page.

## 4. The summary table

`docs/PAPERS.md` groups papers into one table per kind — definition, method, comparison, finding,
review — in that order, so a reader looking for the formula papers sees only those. Omit a group
that has no rows yet. Within each table, rows are sorted alphabetically by the first author's
surname. The columns are:

| Column | Content |
| --- | --- |
| Paper | Short name, linked to `papers/<slug>.md` — `Knudtson 2003`, not the full title |
| Year | Publication year of the version of record |
| What it is for | One short phrase, in plain language |
| Relates to | Catalogued biomarker, project, model or dataset names, short |
| Open | How a reader actually gets the text: `✅` publisher or PMC, `🟡` a copy off the publisher (author PDF, preprint, ResearchGate) that may move, `⛔` paywalled and no stable free copy established |
| Last checked | Date from the detail page |

Keep every cell short enough to read across. When a detail page changes, update its row in the
same commit. **Keep the Paper cell short enough that the name itself does not wrap.**

The authors, venue, DOI and the reason the paper is here are **not** table columns: they live on
the detail page. Open is effort to *read*, not permission to redistribute.
