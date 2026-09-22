# Biomarkers against arithmetic — how it is run

This page says how the benchmark is configured: what it asks, what takes part, how to run it, and
what every column of its evidence means.

**It is part generated and part written.** The tables and lists between the `generated` markers are
rendered from what the benchmark reports about itself and are refreshed by
`python -m benchmarks --benchmark biomarker-synthetic --docs`, which measures nothing. Everything
else on the page is written by hand and is never overwritten. What *came out* of a run is written
up separately, per implementation — section 8.

## 1. What this benchmark asks

<!-- generated: asks -->
**Does a biomarker implementation compute the quantity it is said to compute?** Every other benchmark here compares software with a human judgement; this one compares it with a number derived on paper. A straight vessel has a tortuosity of exactly 1, a circular arc a curvature of exactly 1/r, and an implementation that disagrees is wrong rather than different. It selects nothing: which implementations are fit to measure a real segmentation is a judgement made by a person on this evidence.
<!-- /generated -->

Its shapes and the derivations behind their values are in
[the shapes notebook](../../notebooks/biomarker-synthetic-shapes.ipynb); how the pictures are drawn
is [biomarker-synthetic-shapes.md](biomarker-synthetic-shapes.md).

## 2. What takes part

Each implementation is reached through an adapter that measures it **as it ships** — no defect is
corrected on its behalf, and each answers under catalogued biomarker names so that two of them line
up column by column. A column the catalogue cannot name yet is kept under the implementation's own
name rather than dropped.

<!-- generated: subjects -->
| Implementation | Pinned at | Columns it returns | Took part |
| --- | --- | --- | --- |
| [pvbm](../projects/pvbm.md) | `5edb79a` | 32 | yes |
| [ocular](../projects/ocular.md) | `34b1ecc` | 18 | yes |
| [automorph](../projects/automorph.md) | `9a953e5` | 18 | yes |
| [automorphalyzer](../projects/automorphalyzer.md) | `e68843e` | 54 | yes |
| [automorphclass](../projects/automorphclass.md) | `8f4d18f` | 18 | yes |
| [vascx](../projects/vascx.md) | `d0cde1c` | 20 | yes |
<!-- /generated -->

Three of them share a lineage and one does not: AutoMorph, AutoMorphalyzer and AutoMorphClass all
descend from retipy, OCULAR imports PVBM's helpers at runtime, and VascX reimplements every
measurement independently. That is why they are written up in families rather than one by one.

## 3. What they are measured on

Every shape is a drawing whose values follow from its geometry rather than from anybody's opinion,
so a disagreement is an error rather than a difference. Each carries both an artery and a vein,
and each is drawn at four angles — 0°, 30°, 60° and 90° — where the geometry is identical and only
the pixel grid differs.

<!-- generated: material -->
| Shape | What its geometry settles | Available |
| --- | --- | --- |
| `straight` | 25 quantities with a known value | yes |
| `arc` | 23 quantities with a known value | yes |
| `sinusoid` | 23 quantities with a known value | yes |
| `bifurcation` | 15 quantities with a known value | yes |
| `disjoint` | 19 quantities with a known value | yes |
| `artery-vein-pair` | 18 quantities with a known value | yes |
| `spokes-macula-centred` | 22 quantities with a known value | yes |
| `spokes-disc-centred` | 22 quantities with a known value | yes |
<!-- /generated -->

## 4. How to run it

<!-- generated: running -->
```bash
python -m benchmarks --benchmark biomarker-synthetic
python -m benchmarks --benchmark biomarker-synthetic --model pvbm --dataset straight
python -m benchmarks --benchmark biomarker-synthetic --docs
```

| Flag | What it does |
| --- | --- |
| `--model` | one implementation, or several separated by commas |
| `--dataset` | one shape, or several separated by commas |
| `--max-samples` | draw only the first N of the four angles, for a development run |
| `--force` | discard what is stored and measure it all again |
| `--docs` | refresh this page from the declarations, measuring nothing |
<!-- /generated -->

## 5. What each column of the evidence means

<!-- generated: columns -->
`results/biomarker-synthetic/<implementation>/<shape>.csv` holds one row per rendering:

| Column | Meaning |
| --- | --- |
| `key` | the rendering: the shape and the angle it was drawn at |
| `shape` | which shape was drawn — `straight`, `arc`, `spokes-macula-centred` and the rest |
| `rotation` | the angle it was drawn at, in degrees, generated afresh rather than turned |
| `side` | the grid it was drawn on, in pixels |
| `um_per_px` | the microns per pixel the shape was built with |
| `outcome` | `measured` if any quantity came back, else `failed`; `note` says what fell over |
| `seconds` | how long the implementation took over this rendering |
| `said_<key>` | what the implementation returned. `<key>` is a **catalogued biomarker name** — `biomarker/variant/structure` — wherever the implementation's adapter maps its own column to one, so two implementations' evidence lines up column by column. A column the catalogue has no name for yet keeps the implementation's own name, recognisable by carrying no `/`, and is measured and stored all the same |
| `theory_<key>` | what the shape's geometry requires for that quantity, where it defines one. A shape states its theory under catalogued names too, so the two meet without translation; a column under an implementation's own name therefore has no theory beside it |
| `note` | what an implementation failed with |
<!-- /generated -->

A column an implementation does not compute is **absent** rather than blank, and one it computes
but the catalogue cannot name keeps its own name — recognisable by carrying no `/`.

## 6. What a re-run repeats, and what it does not

<!-- generated: fingerprint -->
A stored result is kept only while everything it depends on is unchanged. This benchmark fingerprints:

- this benchmark's name and `VERSION`
- the facts each implementation declares that bear on its numbers: slug, needs, keys, units
- the pinned commit of the code that will run, as the adapter reports it
- the rendering: a 2048px grid at 5 µm per pixel, drawn at 0°, 30°, 60°, 90°

A fingerprint that differs means the stored result describes something that no longer exists, and it is measured again from nothing. **How much was done is not part of it**, because that does not change what any rendering scored: a complete result is never re-run, and a partial one is finished rather than restarted.
<!-- /generated -->

## 7. The counts every result carries

<!-- generated: counts -->
| Count | What it answers |
| --- | --- |
| `processed` | how many angles of this shape the implementation has measured |
| `total` | how many it was asked for |
| `complete` | whether those are all of them |
| `seconds_per_rendering` | how long the implementation took, on the device named beside it |
<!-- /generated -->

## 8. Where the results are written up

One page per implementation or family, because each is a different piece of somebody else's code
and reading two in one document buries each under the other:

<!-- generated: reports -->
- **PVBM** — [biomarker-synthetic-pvbm-results.md](biomarker-synthetic-pvbm-results.md)
- **AutoMorph** — [biomarker-synthetic-automorph-results.md](biomarker-synthetic-automorph-results.md)
- **VascX** — [biomarker-synthetic-vascx-results.md](biomarker-synthetic-vascx-results.md)
<!-- /generated -->

## 9. What this benchmark does not do

- **It does not measure photographs.** Every shape is clean, binary and noiseless. An
  implementation that measures a synthetic vessel exactly may still fail on a segmentation of a
  real eye, which is a different benchmark's question.
- **It does not select.** No implementation passes or fails here. Which is fit to measure a real
  segmentation is a judgement made by a person on this evidence.
- **It cannot test anything anchored to the fovea**, because a synthetic shape has no macula and
  inventing one would make the answer a property of the fixture.
- **It checks only what a shape pins.** A quantity no shape defines is measured, stored, and
  compared against nothing — which is a gap in the shapes rather than a verdict on the
  implementation.
