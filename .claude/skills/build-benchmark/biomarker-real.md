# The real-segmentation biomarker benchmark

Load this beside `SKILL.md` before building or changing `src/benchmarks/biomarker_real.py`.
Everything here is particular to measuring biomarkers on real photographs; everything shared is in
the main file.

**What it asks:** if a study replaced the expert's artery/vein map with a model's, how far would
each biomarker move, and would it still separate one eye from another? It is the paired comparison
of `PLAN-BENCHMARK.md` §1.2.

```
python -m benchmarks --benchmark biomarker-real --workers 15
python -m benchmarks --benchmark biomarker-real --model vascx --dataset hrf
```

The name carries a hyphen, so the module is `biomarker_real.py`.

## 1. Two kinds of subject, filed by the implementation

The **implementations** — the seven biomarker adapters of `src/biomarkers/` — play the part a model
plays elsewhere: `--model` names them and `results/biomarker-real/<implementation>/` files them.
The **segmentation models** are the maps they are run on, declared in `SEGMENTERS`. One file per
(implementation, dataset) holds every map of every photograph, so the expert's row and each model's
row for one photograph sit together, and the pairing the statistics need is a join on `key`.

## 2. Hold everything fixed but the map

The two numbers of a pair differ in the map and in nothing else:

- **the same disc**, from `results/disc_estimation/<dataset>.csv` — never one estimated per map;
- **the same field of view**, the store's `fov` layer;
- **the same scale**, the manifest's `um_per_px`, or `None` for both;
- **the same program**, at the same pin.

A photograph without a disc estimate is excluded rather than given a guessed disc.

## 3. It segments nothing

The maps are the ones the artery/vein benchmark kept (`SKILL.md` §6.1). Before reading a model's
masks the run recomputes that model's **drawing fingerprint** with `av.drawing` and compares it with
the kept `fingerprint.txt`. A mismatch refuses that model, with a warning naming the `av` command
that redraws it. Redrawing is not done here, so the two benchmarks cannot each own a copy of a
model's output. The fingerprint travels **per row** (`drawing`), so a redrawn model re-measures its
own rows and nobody else's.

A photograph a model failed on in the artery/vein run has no kept files, and so no row here. Its
`model_only`/`expert_only` counts in the agreement tables show the gap.

## 4. The run computes the agreement, once

Pairing, unit conversion and the statistics are done by the run, in
`benchmarks/metrics/agreement.py` (pure functions over two lists) and `agreement_rows`, and written
to `results/biomarker-real/<implementation>/agreement/<dataset>.csv` and `pooled.csv`. The
notebook and both pages quote those tables rather than computing the statistics again, so they
cannot disagree.

- **Units.** Values are compared in the catalogued unit — `canonical.from_pixels` — where the
  adapter's naming table gives a name, unless the adapter declares that column already in microns.
  A length on a photograph with no scale is left out of its statistic, not compared in pixels.
  An unnamed column is compared as returned.
- **ICC(A,1) and ICC(C,1)**, two-way, single measurement, McGraw and Wong (1996), from the
  analysis of variance of the n × 2 table.
- **SNR** = SD across photographs of the expert-map value ÷ SD of (model − expert). The bias is
  reported on its own and is not part of the noise.
- **Pooled** is pooled on photographs across every dataset with evidence, never a mean of
  per-dataset statistics.

## 5. Parallel, because it is slow

Every implementation is single-threaded Python over one skeleton. The run spawns `--workers`
processes, each loading the adapter once, with BLAS threads pinned to one. `--workers 1` measures
in-process, which is what tests and debuggers use. Third-party checkouts are obtained under a file
lock (`archives.GitSource.obtain`), because several workers obtaining one clone at once collide on
git's index lock.

## 6. Where the code goes

- `src/benchmarks/biomarker_real.py` — the run, the agreement tables, `config()`, the index section.
- `src/benchmarks/loaders/biomarker_real.py` — `BiomarkerLoader`: photographs with both classes,
  uncondemned, and a disc; it reads no photograph.
- `src/benchmarks/metrics/agreement.py` — ICC, SNR, bias.
- `tests/benchmarks/test_biomarker_real.py`, `test_metrics_agreement.py`.
