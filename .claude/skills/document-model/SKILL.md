---
name: document-model
description: Catalogue a fundus segmentation or classification model — a single trained network that turns a colour-fundus photograph into masks, landmarks or a grade, without computing biomarkers — as a page in docs/models/ plus a row in the docs/MODELS.md summary table. Use when adding, updating, or reviewing a model entry in Fundus Atlas.
---

# Documenting a model

A **model** here means one trained network doing one task: one architecture, one set of published
weights, one kind of output. Vessel segmenters, artery/vein classifiers, optic disc and cup
segmenters, fovea locators and image-quality graders are models. A pipeline that goes on to compute
vessel width or tortuosity is a **project**, catalogued by the `document-project` skill instead.

**One model, one page — even when several are released together.** A project that publishes five
models gets five pages, because a reader comparing artery/vein models needs to find one entry per
model, not one entry per release. Apply these boundaries:

- **Different task, different page.** A vessel segmenter and an artery/vein segmenter are two models
  even when they share an architecture, a repository and a paper.
- **Retrained for a different task, different page.** The same architecture retrained on other data
  for another purpose is a distinct model with its own training data, weights and provenance.
- **An ensemble of the same weights is one model.** Ten random seeds averaged for one output are one
  entry; record the count in the architecture section.
- **A smaller or larger variant released alongside is its own page** when it has its own weights,
  because a reader must be able to tell which one produced a result.

The two catalogues answer different questions. A project page answers "what will this software give
me?"; a model page answers "where did this mask come from, what was it trained on, and may I trust
it on my images?"

## 1. What you produce

Every model produces exactly two things:

1. **A detail page**, `docs/models/<slug>.md`, following `template.md` in this skill directory. The
   slug is the model's own name, lowercased, spaces and underscores replaced by hyphens (`BF-Net`
   becomes `bf-net.md`).
2. **A row in `docs/MODELS.md`**, the summary table, linking to that detail page.

Never write one without the other.

## 2. Required sections of the detail page

Use `template.md` verbatim and keep its section numbering. The sections are:

1. **Code reference** — repository URL, the commit or tag the page describes, the most recent commit
   as year and month, how it runs, and whether **training code** is published (in this repository or
   another). A model whose training code is public can be retrained on your own images; one whose is
   not can only be used as given.
2. **License** — the code license and the weights license, recorded separately and as stated at
   source. Weights are frequently the more restrictive of the two, and are what a user actually
   redistributes.
3. **Major publications by the authors** — the paper that introduced the model, with a DOI or stable
   link, plus any later paper that changed it.
4. **What it produces** — begins with the **purpose class**, which is one of exactly five values
   and never a new one:

   | Purpose | What belongs in it |
   | --- | --- |
   | `quality` | Judging whether a photograph is good enough to measure |
   | `vessels` | Blood vessels as a single class, artery and vein not distinguished |
   | `artery/vein` | Arteries separated from veins, including models that add a crossings class |
   | `disc/cup` | The optic disc, the optic cup, or both |
   | `other` | Anything else — fovea location, lesions, landmarks |

   A model that does two of these is two models and therefore two pages (see the boundaries above).
   Then record the output classes exactly as the model emits them (for example "background, artery,
   vein, crossings"), and the input it expects: resolution, whether the image must be cropped to the
   field of view, whether it assumes a disc-centred or macula-centred photograph, and any
   preprocessing baked into the published inference code. Mismatched expectations are the most
   common cause of a model behaving worse than its paper reports.
5. **Architecture** — the family (U-Net, W-Net, GAN-based, an encoder backbone), parameter count if
   stated, and whether the published weights are a single model or an ensemble. An ensemble is not
   interchangeable with one of its members: say how many, and how they are combined.
6. **Training data** — every dataset used for training, with the split if stated, and who produced
   the annotations. This is the section a reader checks before benchmarking, because **a model
   cannot be fairly evaluated on a dataset it was trained on**. Name the datasets even when the
   split is unclear, and say the split is unclear.
7. **Weights** — whether trained weights are published, the **full download URL** for each (a
   Hugging Face model page, a release asset, a Google Drive file, or the path inside the repository
   when they are committed there), the file format and size, and how many files make up an ensemble.
   If a script fetches them, read the URL out of that script. Never copy weights into this
   repository.
8. **Performance as reported by the authors** — their metrics, on their test sets, labelled as their
   claim. Give the metric, the dataset and the number; do not average across papers, do not compare
   two papers' numbers as though they were measured the same way, and do not present any of it as
   this atlas's finding. This repository's own measurements live in the comparison tables.
9. **Used by** — which catalogued projects run this model, linking to their pages, and which of them
   retrained it rather than using the published weights. This is the reverse of the project pages'
   segmentation-model section, and the two must agree.
10. **Known defects** — bugs that change the masks or the numbers derived from them, each with its
    evidence: the upstream issue or commit, the affected outputs, and whether it is fixed and in
    which version. Follow the same rules as the project skill: record a defect where it lives,
    attribute a claimed fix to whoever claims it rather than confirming it, and write `None
    recorded` with the date when nothing is known — an absence of findings, not a clean bill of
    health.

A section that does not apply stays in the page, marked `Not applicable` with a short reason. A
section whose answer could not be established is marked `Unknown` — never filled with a guess.

## 3. Rules that apply to every entry

- **3.1 Reference, never redistribute.** Link to the authors' repository, weights and datasets at
  their original source (see `CLAUDE.md` §2).
- **3.2 Separate claim from observation.** Section 8 is the authors' claims, and must read as such.
- **3.3 Write for a non-engineer.** Say what an architecture does in a sentence before naming it;
  expand every metric on first use (a Dice score measures overlap between a predicted mask and a
  reference one).
- **3.4 Number every heading**, as the template does.
- **3.5 Record the license as written**, and flag plainly when a project's license is absent or
  unclear.
- **3.6 Date what you checked**, at the bottom of the page.
- **3.7 Keep both catalogues consistent.** Adding a model that a project page names means updating
  that project page to link here, in the same commit. A model page claiming a project uses it, while
  that project's page does not name it, is a bug in the atlas.

## 4. The summary table

`docs/MODELS.md` groups models into one table per purpose class — quality, vessels, artery/vein,
disc/cup, other — in that order, so a reader looking for one kind of model sees only those. Within
each table, rows are sorted by last commit with the most recently committed model first; models
whose most recent commit falls in the same month are ordered alphabetically. The columns are:

| Column | Content |
| --- | --- |
| Model | Name, linked to `models/<slug>.md` |
| Produces | The output classes, in a few words |
| Architecture | The family, and `ensemble of N` where it applies |
| Trained on | Dataset names, short |
| Weights | Yes / No / Unknown |
| Training code | Yes / No — and where, if elsewhere |
| License | Code license as stated; note separately when the weights differ |
| Used by | Catalogued projects that run it, or `—` |
| Last commit | Year and month of the model repository's most recent commit |
| Last checked | Date from the detail page |

Keep every cell short enough to read across. When a detail page changes, update its row in the same
commit, and move the row if its last-commit date changed the ordering.
