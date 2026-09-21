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
- **1.7 Papers** — published work a reader needs in order to interpret a measurement, a comparison
  or a pitfall: the formula papers, not a bibliography of every citation.

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
- **4.3 Build a map, not a leaderboard.** The reader should be able to look up a dataset, model,
  project or paper and understand its trade-offs. Do not crown a winner or rank entries into a
  single ordering.
- **4.4 Separate claim from observation.** An author's own claims and this repo's measurements are
  different kinds of statement and must be labelled as such.

## 5. Where the conventions live

The detailed rules are not in this file. Each kind of entry has its own Claude skill under
`.claude/skills/`, and that skill is the authority on it:

- **5.1** How to catalogue a dataset, a segmentation model, a biomarker calculation, a project, or a
  paper — the required fields, the page structure, and what evidence each claim needs.
- **5.2** How to implement the supporting code for an entry — dataset fetch utilities, model
  installation, and benchmark runs — so that every entry is fetched, installed, and measured the
  same way.

Skills that exist today:

- **5.3** `document-project` — cataloguing a project: the page structure in `docs/projects/` and the
  columns of the `docs/PROJECTS.md` summary table.
- **5.4** `document-model` — cataloguing a segmentation or classification model: the page structure
  in `docs/models/` and the columns of the `docs/MODELS.md` summary table.
- **5.5** `document-biomarker` — cataloguing a biomarker: the page structure in `docs/biomarkers/`
  and the columns of the `docs/BIOMARKERS.md` summary table.
- **5.6** `document-dataset` — cataloguing a dataset: the page structure in `docs/datasets/` and the
  columns of the `docs/DATASETS.md` summary table.
- **5.7** `document-paper` — cataloguing a paper: the page structure in `docs/papers/` and the
  columns of the `docs/PAPERS.md` summary table. A paper belongs here only when it changes how a
  reader should interpret something else in the atlas, not because another page cites it.
- **5.8** `fetch-dataset` — building a dataset fetcher: the command-line contract, the store layout,
  the manifest schema, how a published (or inherited, or field-angle) resolution is recorded, and
  the `How to fetch` subsection every fetcher adds to its dataset page. A dataset that published
  no scale is unfinished until `fetch-um-resolution` has been run.
- **5.9** `fetch-um-resolution` — inferring a camera-level microns-per-pixel scale from the
  median optic disc of a sampled subcollection, when the authors published none: the command,
  the grouping, the spread gate, and the JSON committed under `results/um_resolution/`.
- **5.10** `add-upstream` — bringing in somebody else's repository: pinned install or pinned clone,
  patches, imports, and the provenance a run records.
- **5.11** `add-model` — the adapter that lets a benchmark run one catalogued model: what it must
  declare, what it must not do, and the page it must match.
- **5.12** `build-benchmark` — a benchmark: what it runs on, its loaders, metrics, and the
  fingerprint that keeps a re-run cheap.
- **5.13** `analyse-benchmark` — the notebook every benchmark gets: what its analysis must show.
- **5.14** `report-benchmark` — the two documents a run generates — how the benchmark is configured,
  and what came out — and the rule that both are generated rather than written.

The three benchmark skills each hold the rules common to every benchmark, and **a file per
benchmark beside them** — `build-benchmark/quality.md` and its siblings — holding what is true of
that one only. Load both.

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

## 7. Layout

Catalogues live under `docs/`: `PROJECTS.md` and `projects/` for pipelines, `MODELS.md` and
`models/` for models, `BIOMARKERS.md` and `biomarkers/` for measurements, `DATASETS.md` and
`datasets/` for image collections, `PAPERS.md` and `papers/` for the publications that change how
those entries should be read. Each summary table and its detail pages are maintained together,
per the skills in section 5.

Code lives under `src/`, one layer per kind of thing, and each layer's own skill in section 5 is
the authority on it:

- `src/datasets/<slug>.py` — one fetcher per catalogued dataset, with everything they share in
  `src/datasets/utils/`, so that two datasets cannot disagree about a crop rule, a palette or a
  resize. Images found to be unusable are recorded in `src/datasets/exclusions/<slug>.json`, in the
  repository rather than in the downloaded store, so a finding survives rebuilding it.
- `src/upstreams/<project>.py` — one module per third-party **repository**: where its code comes
  from, pinned, and how it is imported. Patches to it live in `src/upstreams/patches/<project>/`.
- `src/models/<slug>.py` — one adapter per catalogued **model**, matching `docs/models/<slug>.md`.
  Five models from one repository are five adapters and one upstream.
- `src/benchmarks/` — one module per benchmark, its loaders, its scorer and its report writer.
- `results/` — committed evidence: per-image benchmark scores, and inferred camera scales under
  `results/um_resolution/` for datasets that published no microns-per-pixel figure.
- `notebooks/` — one analysis notebook per benchmark.

Tests are in `tests/`, mirroring `src/`, and run against synthetic fixtures rather than downloads.
Three directories are git-ignored caches: `.atlas_data/` for dataset stores, `.atlas_code/` for
third-party checkouts and weights, `.atlas_runs/` for what a benchmark run produces.
