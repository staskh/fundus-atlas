---
name: document-project
description: Catalogue a fundus-analysis project — a publicly available pipeline that combines segmentation models and biomarker calculations end to end — as a page in docs/projects/ plus a row in the docs/PROJECTS.md summary table. Use when adding, updating, or reviewing a project entry in Fundus Atlas.
---

# Documenting a project

A **project** here means a publicly available pipeline that takes a colour-fundus photograph and
returns numbers, by combining one or more segmentation models with one or more biomarker
calculations. Individual models and individual calculations are catalogued elsewhere, not here.

## 1. What you produce

Every project produces exactly two things:

1. **A detail page**, `docs/projects/<slug>.md`, following `template.md` in this skill directory.
   The slug is the project's own name, lowercased, spaces and underscores replaced by hyphens
   (`AutoMorph` becomes `automorph.md`).
2. **A row in `docs/PROJECTS.md`**, the summary table, linking to that detail page.

Never write one without the other. A page with no row is invisible; a row with no page is a claim
with no evidence behind it.

## 2. Required sections of the detail page

Use `template.md` verbatim as the starting point and keep its section numbering. The sections are:

1. **Code reference** — where the source actually lives: repository URL, and the commit, tag, or
   release the rest of the page describes. Pin a version; "latest main" ages badly. Record the date
   of the project's most recent commit as year and month (`2024-11`); it tells a reader at a glance
   whether the pipeline is still maintained. Keep it distinct from the last-checked date in §3.6:
   one is the authors' activity, the other is ours.
2. **License** — the license of the code, stated as the project itself states it. If the code and
   the model weights carry different licenses, record both separately; they often differ.
3. **Major publications by the authors** — the paper to cite for the project, plus any follow-ups
   that change what it does. Full citation and a DOI or stable link.
4. **Segmentation models used** — every model in the pipeline, and for each one whether it was
   **introduced by this project** or **borrowed**. If borrowed, name the project or paper it came
   from and link to that source. This distinction is the point of the section: it stops the same
   model from being credited to three different pipelines.
5. **Models introduced here** — one subsection per new model, each recording:
   - **Training data** — which datasets it was trained on, and which split, if stated.
   - **Weights** — whether trained weights are publicly available and, if so, exactly where to get
     them. Link to the original host. Do not copy weights into this repository.
6. **Biomarkers computed** — every biomarker the pipeline outputs, with the original publication
   that defined it and the original implementation if one exists. Say whether this project
   reimplemented the calculation or reused the original code, and note any deviation from the
   published definition.
7. **Examples and notebooks** — the one or two entry points a reader should run first to see the
   pipeline work, with a sentence on what each demonstrates. Point at the most useful, not all of
   them.

A section that does not apply stays in the page, marked `Not applicable` with a short reason. A
section whose answer you could not establish is marked `Unknown` — never filled with a guess.

## 3. Rules that apply to every entry

- **3.1 Reference, never redistribute.** Link to the authors' repository, weights, and datasets at
  their original source. Copying their code, weights, or images into this repository is out of
  scope (see `CLAUDE.md` §2).
- **3.2 Separate claim from observation.** What the authors say the pipeline does belongs in a
  sentence attributed to them. What this repo measured belongs in the comparison tables, labelled
  as ours. Never blend the two in one sentence.
- **3.3 Write for a non-engineer.** Clinicians and researchers read these pages. Expand jargon on
  first use.
- **3.4 Number every heading**, as the template does.
- **3.5 Record the license as written.** Never restate a license as more permissive than its source
  does, and flag it plainly when a project's license is absent or unclear.
- **3.6 Date what you checked.** Put the date you verified the links and license at the bottom of
  the page. These projects move.

## 4. The summary table

`docs/PROJECTS.md` holds one row per project, sorted alphabetically, with these columns:

| Column | Content |
| --- | --- |
| Project | Name, linked to `projects/<slug>.md` |
| What it produces | The biomarker families it outputs, in a few words |
| Segmentation models | Model names; mark borrowed ones as `(borrowed)` |
| New models introduced | Yes / No |
| Weights public | Yes / No / Unknown |
| Code license | As stated by the project |
| Last commit | Year and month of the project's most recent commit |
| Last checked | Date from the detail page |

Keep every cell short enough to read across — detail belongs on the page, not in the table. When a
detail page changes, update its row in the same commit.
