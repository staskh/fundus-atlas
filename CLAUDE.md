# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 1. What this repository is

Fundus Atlas is a public reference for colour-fundus photography work. A fundus photograph is a
colour photo of the back of the eye.

It maps the field:

- **1.1 Datasets** — which public fundus datasets exist, who owns them, what license they carry,
  what is actually annotated in them.
- **1.2 Segmentation models** — which models trace anatomy in a fundus photograph: blood vessels,
  arteries against veins, and the optic disc and cup.
- **1.3 Biomarker calculations** — which methods turn those traced outlines into numbers, such as
  vessel width, tortuosity, and CRAE.
- **1.4 Projects** — publicly available pipelines that combine several segmentation models and
  biomarker calculations into one end-to-end run, from photograph to table of numbers.
- **1.5 Comparisons** — side-by-side scores computed on the same terms, so numbers from different
  papers and different projects can be read against each other.
- **1.6 Checks** — quality gates that decide whether a segmentation is usable before anyone trusts
  the biomarkers derived from it.

Pages in sections 1.2 to 1.4 state what a model, calculation, or project *claims* against what it
*does*.

The repository's job is to **document, compare, and check**.

## 2. Scope boundaries

This project does not redistribute other people's work. It references that work at its original
source and compares results across it. Everything catalogued here stays upstream, under its own
owners and its own license; this repo adds the map, the common-terms measurements, and the citation.

Out of scope, without exception:

- **2.1** Shipping another segmentation model, biomarker calculation, or pipeline. The projects
  catalogued here are cited, not vendored and not replaced.
- **2.2** Training new networks.
- **2.3** Redistributing other people's fundus photographs or model weights.
- **2.4** Relicensing anyone else's data.

If a task appears to require any of the above, stop and raise it with Stas rather than working
around it.

## 3. Licensing

- **3.1** Code written here: Apache 2.0 (see `LICENSE`).
- **3.2** Write-ups, tables, and comparison results: CC BY 4.0.
- **3.3** Each catalogued dataset, model and code keeps its own license. Record that license on the component page and
  never restate it as more permissive than it is.

## 4. How to write the prose in this repo

- **4.1 Audience is not a software engineer.** Clinicians and researchers read these pages. Spell
  out jargon on first use; do not assume familiarity with segmentation tooling or Python.
- **4.2 Number every heading**, as this file does.
- **4.3 Build a map, not a leaderboard.** The reader should be able to look up a dataset, model, or
  project and understand its trade-offs. Do not crown a winner or rank entries into a single
  ordering.
- **4.4 Separate claim from observation.** An author's own claims and this repo's measurements are
  different kinds of statement and must be labelled as such.

## 5. Where the conventions live

The detailed rules are not in this file. Each kind of entry has its own Claude skill under
`.claude/skills/`, and that skill is the authority on it:

- **5.1** How to catalogue a dataset, a segmentation model, a biomarker calculation, or a project —
  the required fields, the page structure, and what evidence each claim needs.
- **5.2** How to implement the supporting code for an entry — dataset fetch utilities, model
  installation, and benchmark runs — so that every entry is fetched, installed, and measured the
  same way.

Skills that exist today:

- **5.3** `document-project` — cataloguing a project: the page structure in `docs/projects/` and the
  columns of the `docs/PROJECTS.md` summary table.

Before adding or changing an entry of any kind, load the matching skill and follow it. Where a skill
does not exist yet, stop and agree the convention with Stas, then write the skill — do not invent a
one-off format inline.

## 6. Branching and merging

- **6.1** Never commit to `main` directly, and never merge into it locally. `main` is protected on
  GitHub: it rejects direct pushes, and it rejects them for repository administrators too.
- **6.2** Work on a branch, push it, and merge through a pull request — `gh pr create`, then
  `gh pr merge`. A pull request is required even for a one-line documentation fix and even when you
  are the only person working in the repository; it is what leaves a reviewable record of a change
  to a public reference.
- **6.3** If a push to `main` is rejected, that is the protection working as intended. Open a pull
  request instead of looking for a way around it, and do not disable the protection to land a
  change.

## 7. Layout and commands

Not yet established — at the time of writing the repository contains only `LICENSE` and
`.gitignore`. Python is the intended language (per `.gitignore`); run Python through `uv`.

Fill this section in as real structure and commands appear; do not guess them.
