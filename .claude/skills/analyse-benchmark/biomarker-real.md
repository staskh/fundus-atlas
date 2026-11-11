# Analysing the real-segmentation biomarker benchmark

Load this beside `SKILL.md` before writing or changing `notebooks/biomarker-real.ipynb`.

The notebook reads `results/biomarker-real/<implementation>/agreement/*.csv` for every statistic,
and the per-map evidence only for what a statistic cannot show: a scatter, a difference against a
mean, a photograph. It never recomputes an ICC the run wrote.

## 1. The model is the primary index, the biomarker the secondary

A row per segmentation model, biomarkers within it. Where implementations are compared, it is
**on one biomarker under one model**, never a ranking of implementations across biomarkers.

## 2. What it must show, in the order of `SKILL.md` §4

1. **Coverage** — per model and dataset, how many photographs each map produced a number for, and
   how often the model's map produced none where the expert's did.
2. **The distribution behind each ICC** — for the headline panel (`biomarker_real.PANEL`),
   expert against model scatter plots and Bland–Altman plots (difference against mean). One ICC
   can hide a cloud that is tight except for a few photographs, or a constant offset.
3. **ICC and SNR across every catalogued biomarker** — by family, so a reader sees which families
   survive a model's map (calibre, density, tortuosity, topology) and which do not.
4. **Where the implementations disagree** — the same biomarker, the same model, different
   programs. A biomarker robust in one program and fragile in another is a finding about the
   program's tracing, not about the model.
5. **What the hard cases look like** — the photographs with the largest difference on a headline
   biomarker, the expert's map beside the model's, the dataset named on each.
6. **What it costs** — seconds per map per implementation, on one core.
7. **What it cannot say** — no second reader, contamination, scale-free photographs, pooled versus
   per-dataset.

## 3. Read SNR and ICC together

A high SNR with a low ICC(A,1) is a **bias**: correctable in principle, and named as such. A low SNR
is **scatter**, which nothing downstream can correct. Say which, wherever a biomarker is called
fragile.
