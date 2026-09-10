# Segmentation and classification models

Single trained networks that turn a colour-fundus photograph into masks, landmark locations or a
grade. Each row links to a detail page describing that model: what it produces, what it was trained
on, where its weights are, what its authors report about it, and which catalogued pipelines run it.

Models that go on to compute vessel width, tortuosity or other measurements are pipelines, and are
catalogued in [PROJECTS.md](PROJECTS.md) instead.

This is a lookup table, not a ranking. A model that scores well on the images it was trained on may
do poorly on yours, which is why the training data is a column here.

## 1. Summary

| Model | Produces | Architecture | Trained on | Weights | Training code | License | Used by | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| _No entries yet._ | | | | | | | | | |

## 2. How to read this table

- **Trained on** — the datasets used to fit the model. A model cannot be fairly evaluated on a
  dataset it was trained on, so this column decides which benchmarks mean anything for a given
  model. `Unclear` means the papers or code did not state a split.
- **Architecture** — `ensemble of N` matters: running one member of an ensemble is not the same model
  as the published one, and some pipelines do exactly that to save time.
- **Weights** — whether trained weights can be obtained from the authors. `Unknown` means we could
  not establish it, not that they are unavailable.
- **Training code** — whether the model can be retrained on your own images, and where that code
  lives. Weights and training code are often published in different repositories.
- **Used by** — which pipelines in [PROJECTS.md](PROJECTS.md) run this model. A model used by
  several pipelines is a shared dependency: those pipelines agreeing with each other is weaker
  evidence than it appears.
- **Last commit** — the year and month of the model repository's most recent commit, as a rough
  signal of maintenance. An old date is not a fault; a published model may need no changes.
- **Known defects** are not in this table. Every detail page carries a section 10 recording bugs
  that change the masks or the numbers derived from them. `None recorded` there means no finding,
  not a clean bill of health.

## 3. Adding a model

Model pages follow a fixed structure so they can be read against each other. Load the
`document-model` skill, which defines that structure and this table's columns, before adding or
changing an entry.
