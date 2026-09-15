---
name: add-upstream
description: Bring a third-party repository into this project at a pinned version — installed or cloned, patched if it must be, imported, and recorded — so a benchmark can run somebody else's model. Use when adding or changing anything under src/upstreams/.
---

# Adding an upstream

An **upstream** is one published repository: one clone or one install, one pinned version, one set
of dependencies. It is **not** one model. VascX is one repository holding five models; AutoMorph is
one repository whose stages are separate programs. So the rule is **one module per repository**,
`src/upstreams/<project>.py`, and the model adapters in `src/models/` import from it.

Nothing third-party is ever committed here (`CLAUDE.md` §2.1), and several of these could not be
redistributed anyway: some state no licence at all, and VascX's weights are AGPL-3.0. The upstream
module's job is to say exactly where the code came from, get it onto this machine, and hand the
adapter something it can call.

## 1. What you produce

1. **An upstream module**, `src/upstreams/<project>.py`, named for the repository as the catalogue
   names it (`docs/projects/vascx.md` ↔ `src/upstreams/vascx.py`). Where the repository has no
   project page — a library rather than a pipeline — use the short name the model pages use.
2. **Tests** where the module does anything of its own beyond declaring constants. The machinery in
   `src/upstreams/utils/` is already tested; a module that only declares a pin and a loader needs
   no test of its own, and one that reshapes an upstream's output does.
3. **A pin in `pyproject.toml`**, for an upstream that is installed rather than cloned.

## 2. Installed, or cloned

- **Pip-installable upstreams are installed**, at an exact pinned version, declared in the
  `benchmarks` extra of `pyproject.toml`. Use `source.Installed`.
- **Everything else is cloned** at a pinned commit into the git-ignored `.atlas_code/<slug>/`, with
  `source.Checkout`. A clone also happens when an upstream must be patched.

**Pin the commit the model page describes, not the latest release.** These two are often months
apart: the Fundus Image Toolbox's PyPI release trailed the commit its pages describe by three
months. Installing from a repository at a commit is still installing, and it is what keeps a result
attributable to the code the catalogue documents:

```
"fundus-image-toolbox @ git+https://github.com/berenslab/fundus_image_toolbox@<full sha>"
```

`Installed.provenance()` reads the installer's own `direct_url.json`, so the commit a run records is
the commit that is actually there rather than the one we meant to ask for. It raises when they
differ. Give the **full** forty-character SHA in the pin and in the module.

## 3. Undeclared dependencies are yours to pin

An upstream that does not declare what it needs will import something that is not there. VascX runs
its models entirely through `retinalysis-inference` and `retinalysis-fundusprep` and declares
neither. When this happens:

- pin the missing package yourself, at the **release contemporary with the pinned commit** — the
  one published before it and closest to it — rather than at the newest;
- declare it in the upstream module beside the repository's own pin, so the run records it;
- say in a comment that the upstream does not declare it, because a later reader will otherwise
  assume the pin is arbitrary.

## 4. One environment, and what to do when it nearly does not hold

Everything shares one environment (`PLAN-BENCHMARK.md` §8.1). When two upstreams cannot both be
satisfied, the order of preference is:

1. **A dependency override** in `[tool.uv] override-dependencies`, with a comment saying what
   breaks without it. This is what settled the first conflict in this repository: VascX's inference
   package pins `albumentations==1.3.1`, whose import reaches for `imgaug`, which reaches for a
   NumPy attribute removed in NumPy 2 — and the Fundus Image Toolbox is what puts `imgaug` in the
   environment at all. Albumentations 1.4 carries the same API the inference package uses and no
   `imgaug` import, so one override lets both upstreams share one environment.
2. **A patch**, per section 5.
3. **Recording the model as not benchmarkable in the shared environment**, with what it needs
   written down. Never fork the environment quietly.

Record what a pinned dependency's own history costs you. QuickQual's classifier was pickled with
scikit-learn 1.2.2, which cannot be installed on this Python, so it is unpickled by a much later
release which warns that it may be invalid. That is a finding for the benchmark's write-up and for
the model page, not something to silence.

## 5. Patches

A change that must be inside their code is a patch file, `src/upstreams/patches/<slug>/NNN-what-it-fixes.patch`,
applied after the clone. Against a pinned commit a patch cannot rot, because the commit cannot move.
`Checkout` applies each patch once, records it in the working tree, and fingerprints it **by
content** — so editing a patch invalidates exactly the results it could have changed.

Prefer doing it in the adapter. A patch is for what an adapter cannot reach: a hard-coded path, an
import that fails, a device assumption inside their loop.

## 6. What the module publishes

Keep it small and predictable. Three kinds of function, named for what they return:

| Function | Returns |
| --- | --- |
| `<model>_weights()` | the weight **files**, downloading them if needed, **without loading them** |
| `<model>_ensemble()` / `<model>_stage()` | the loaded thing an adapter calls |
| `provenance()` | what the run records: the pin, and any package the upstream needed but did not declare |

The split between the first two matters: a benchmark fingerprints the weights before it decides
whether it needs to run anything, and loading ten checkpoints to then skip the unit is waste.

Weights go under `.atlas_code/weights/<slug>/` when we fetch them; when the upstream fetches its
own, pass it that directory as its cache so everything lands in one git-ignored place.

**A file we download is pinned by digest.** `utils.weights.fetch` refuses anything else and deletes
it — some of these are pickles, and loading a pickle runs the code inside it.

## 7. Importing a clone

A leading dot is nothing to the import machinery, but it cannot be part of a package name, so a
checkout is reached by putting it on `sys.path` and importing the upstream's **own** module names.
`Checkout.on_path()` does this. Where a repository is a pipeline of stages rather than a package —
AutoMorph — give `imports_from` the stage's directory, and import the stage's own modules from it.

Import inside the function that needs it, never at module import time: an upstream module must be
importable for its provenance alone, on a machine where nothing has been cloned yet.

## 8. Do not let an upstream phone home

A benchmark run makes the network calls it declares and no others. Where a library checks for its
own updates on import, disable it in the upstream module (`NO_ALBUMENTATIONS_UPDATE`), with a
comment saying why.

## 9. Rules

- **9.1** Never commit third-party code, weights or archives, and never add `.atlas_code/` to git.
- **9.2** Pin by full commit SHA or exact release. Never `main`, never a range.
- **9.3** Record a licence finding on the model or project page, not here — but do check it before
  you pin, and refuse to vendor anything.
- **9.4** Whatever you learn from reading their code that contradicts their documentation belongs
  on the catalogue page, in the same commit. Reading VascX's shipped checkpoint is how this
  repository learned that its quality model sees a 224-pixel image and names EyeQ as its training
  data; neither is in its documentation.
