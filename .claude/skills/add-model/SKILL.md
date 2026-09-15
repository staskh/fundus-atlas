---
name: add-model
description: Write the adapter that lets a benchmark run one catalogued model — how to prepare a photograph for it, how to call it, and how to read its answer into the atlas's own vocabulary. Use when adding or changing anything under src/models/.
---

# Adding a model adapter

An **adapter** is the only place in this repository allowed to know that a model is peculiar.
Everything downstream — the loader, the scorer, the report — sees one interface, so adding a model
changes nothing but its own file.

**One file per catalogued model**, `src/models/<slug>.py`, where the slug matches the catalogue
page exactly: `docs/models/vascx-quality.md` ↔ `src/models/vascx-quality.py`. A model with no page
cannot be benchmarked, and that is deliberate — the page is where the contamination marks come
from. Model slugs carry hyphens, which no module name may, so adapters are loaded from their path
by `models.utils.catalogue.load(slug)` rather than imported. Anything two adapters share lives in
`src/models/utils/`.

Where the model's code comes from is **not** this file's business: that is an upstream
(`add-upstream`), one per repository, and five sibling models import from one checkout.

## 1. What you produce

1. **The adapter**, `src/models/<slug>.py`, with the four duties of section 2 and a module-level
   `model(**arguments)` returning it.
2. **Tests**, `tests/models/`, written first. Every adapter is swept up by the parametrised tests
   already there — declaration, preparation, interpretation — so a new adapter that satisfies the
   interface is tested by existing tests the moment it exists. Add a test of its own for anything
   peculiar to it.
3. **Corrections to `docs/models/<slug>.md`**, in the same commit, for whatever reading the code
   taught you that its documentation does not say.

## 2. What an adapter does, and what it must not

Four duties, in this order:

1. **Prepares the input.** The store has already cropped every photograph to its field of view,
   squared it and built it at each size, so **no adapter crops, centres or rescales to the field**.
   What each one does do is the preparation its upstream bakes into its own inference: the grid it
   wants, its colour space, its normalisation, its contrast step, the tensor layout and dtype.
   `prepare` takes one photograph as a `H×W×3` uint8 array and returns the tensor the model wants.
2. **Calls the model**, through the upstream it declares.
3. **Interprets the output into the atlas's convention** — the vocabulary in
   `models/utils/grading.py` for quality, a fixed class order for artery/vein, probabilities where
   the model emits them — and the `graded` / `declined` / `failed` outcome.
4. **Declares itself**: purpose class, the store grid it reads, the grid the network sees, whether
   it emits probabilities, its ensemble size, and its upstream's provenance, so that the run can
   record all of it without asking the model.

It must **not** score anything, choose a dataset, write a result, or read the ground truth. Those
are the benchmark's job, and keeping them out is what makes two adapters comparable.

## 3. The interface

```python
class SomethingQuality:
    slug = "something-quality"     # exactly the catalogue page's slug
    purpose = "quality"            # one of the five purpose classes
    grid = 512                     # the store size it reads

    def declare(self) -> dict      # static facts; no disk, no network
    def identity(self) -> str      # sha256 of the weights it will load, fetching them if needed
    def prepare(self, pixels: np.ndarray) -> torch.Tensor
    def grade(self, images: torch.Tensor, keys: list[str]) -> list[Grade]
    @staticmethod
    def interpret(keys, raw) -> list[Grade]   # pure, and therefore testable without weights
```

Three rules about this shape, each learned from one of the four models built first:

- **`declare()` touches nothing.** It is called to build a fingerprint, possibly to then skip the
  work. `identity()` is where weights are located and hashed — and it locates them *without loading
  them*, which is why the upstream publishes `<model>_weights()` separately.
- **Every number the adapter acts on is declared as a number.** A benchmark fingerprints the facts
  in a declaration, not the sentences: a threshold left inside a description can be changed without
  invalidating a single stored score, which is exactly the stale result the fingerprint exists to
  prevent. Declare the rule in prose *and* the constant beside it.
- **A model that loads weights publishes `release()`**, clearing what it loaded and calling
  `utils.device.forget()`. A run holds five models otherwise, and ten networks plus eight is how a
  machine comes to kill it.
- **`interpret()` is a pure function**, kept apart from `grade()`. It is where a model's codes
  become the atlas's grades, it is the part most likely to be silently wrong, and separating it is
  what lets a test check the mapping without a gigabyte of weights.
- **Loading is lazy.** Build nothing in `__init__` but the device and empty slots.

## 4. A crash is an answer about nothing

`grade()` catches whatever the model raises and returns `FAILED` grades carrying the exception, one
per key in the batch. It never lets an exception escape: one unreadable photograph must not lose a
run of three thousand. A model that refuses a photograph on its own judgement returns `DECLINED`
instead — a different statement, counted separately, and never scored as a mistake.

Every batch returns exactly one grade per key, in order. The benchmark checks this and treats a
missing answer as a lost result rather than a decline.

## 5. Read the checkpoint, not the documentation

The grid, the normalisation and the class order are the facts most often absent or wrong in a model
card. Get them from the code and the checkpoint:

- VascX's quality checkpoint carries its own training configuration, which resizes the 1024-pixel
  square to **224** before the network and names EyeQ as what it learned from. Neither is in its
  documentation. The adapter reads that configuration on load and **raises if it disagrees with the
  adapter's own constants**, so the two cannot drift apart.
- AutoMorph's grader standardises each photograph by the mean and deviation of its own lit pixels,
  jointly across channels. Reimplementing that faithfully is the difference between its numbers and
  somebody else's.
- The Fundus Image Toolbox turns each photograph back into a PIL image inside its own inference and
  moves the batch to its own device afterwards, so its batch must be handed over on the CPU.

## 6. An assumption that cannot be checked is not allowed

Where a model's output order is not stated anywhere — VascX emits three unnamed logits — say so in
a comment, say what the assumption is and where it comes from, and make sure the benchmark reports
something that would expose it if it were wrong. A reversed class order turns a ROC AUC of 0.99
into 0.01; an assumption with a visible consequence is a different thing from a guess.

## 7. Rules

- **7.1** The slug matches the catalogue page. No page, no adapter.
- **7.2** No adapter scores, chooses datasets, or writes files.
- **7.3** No adapter crops or centres a photograph; the store already did.
- **7.4** Every number a run should be able to record comes from `declare()` or `identity()`.
- **7.5** Whatever reading their code taught you goes back onto the model page in the same commit,
  labelled as this atlas's observation rather than as the authors' claim.
