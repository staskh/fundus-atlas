# Results

Committed evidence: a summary table is a claim and these files are what it rests on. They cannot
be reconstructed without re-running the work, and they are what lets somebody check a number
rather than take it on trust.

## 1. Benchmark scores

One file per model per evaluation unit, written by a benchmark run.

```
results/<benchmark>/<model-slug>/<dataset>-<subset>-<split>.csv    what the dataset said and what the model said, per photograph
results/<benchmark>/<model-slug>/<dataset>-<subset>-<split>.json   the summary, and the fingerprint of everything that produced it
```

**The fingerprint** in each `.json` names the model's pinned commit, the weights actually loaded,
the store's builder version, the photograph count, and the benchmark's own version. A re-run
recomputes a pair only when that fingerprint changes, which is why adding a dataset costs only that
dataset.

## 2. Inferred camera scales

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
