# Results

One file per model per evaluation unit, written by a benchmark run and committed.

```
results/<benchmark>/<model-slug>/<dataset>-<subset>-<split>.csv    what the dataset said and what the model said, per photograph
results/<benchmark>/<model-slug>/<dataset>-<subset>-<split>.json   the summary, and the fingerprint of everything that produced it
```

**Why these are committed.** A summary table is a claim and these are its evidence. They are a few
megabytes, they cannot be reconstructed without re-running every model on every photograph, and
they are what lets somebody check a number in `docs/benchmarks/` rather than take it on trust.

**The fingerprint** in each `.json` names the model's pinned commit, the weights actually loaded,
the store's builder version, the photograph count, and the benchmark's own version. A re-run
recomputes a pair only when that fingerprint changes, which is why adding a dataset costs only that
dataset.

Nothing here is a photograph or an annotation: the rows carry keys into the datasets' own images,
which stay with their owners.

Licensed CC BY 4.0, like the rest of this repository's write-ups and tables.
