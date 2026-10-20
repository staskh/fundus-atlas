# Results

Committed evidence: a summary table is a claim and these files are what it rests on. They cannot
be reconstructed without re-running the work, and they are what lets somebody check a number
rather than take it on trust.

## 1. Benchmark scores

One pair of files per model per dataset, written by a benchmark run.

```
results/<benchmark>/<model-slug>/<dataset>.csv    what the dataset said and what the model said, per photograph
results/<benchmark>/<model-slug>/<dataset>.json   the summary, and the fingerprint of everything that produced it
```

The synthetic biomarker benchmark has no datasets: its unit is a drawn shape, so its files are
`results/biomarker-synthetic/<implementation>/<shape>.csv` and `.json`.

**The fingerprint** in each `.json` is a hash of everything that could change a score: what the
model or implementation declares, the weights or pinned commit actually loaded, the store's builder
version (or the drawn shape), and the benchmark's own version. It is a hash, so it names none of
these; it only changes when one of them does. A re-run recomputes a pair only when that fingerprint
changes, which is why adding a dataset costs only that dataset.

## 2. Estimated optic discs

Every photograph's optic disc and cup, centre and equivalent radius in the crop, estimated by the
[SegFormer disc-and-cup model](../docs/models/segformer-disc-cup.md):

```
results/disc_estimation/<dataset>.csv     one row per photograph
results/disc_estimation/<dataset>.json    what measured it, on which store, and its fingerprint
```

These are a model's estimates, not annotations. The contract is the `fetch-disc-estimation` skill.

## 3. Inferred camera scales

Most datasets publish no microns-per-pixel figure. When they do not, a camera-level scale is
inferred from the typical optic disc and committed here:

```
results/um_resolution/<dataset>.json
```

The contract — sample size, the disc model, the spread gate, what a biomarker may do with the
number — is the `fetch-um-resolution` skill. A published scale in the store always wins; this
file is used only when the authors published none.

Nothing here is a photograph or an annotation: the rows carry keys into the datasets' own images,
which stay with their owners.

Licensed CC BY 4.0, like the rest of this repository's write-ups and tables.
