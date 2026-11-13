# Analysing the real-segmentation biomarker benchmark

Load this beside `SKILL.md` before writing or changing `notebooks/biomarker-real.ipynb`.

The notebook reads `results/biomarker-real/<implementation>/agreement/*.csv` for every statistic,
and the per-map evidence only for what a statistic cannot show: a scatter, a difference against a
mean, a photograph. It never recomputes an ICC the run wrote.

## 1. Each project on its own model; the project is the primary index, the dataset the secondary

**Read each project only on the segmentation model it ships with** — `biomarker_real.NATIVE`, which
the configuration page publishes in §2.3. A project is judged as its authors ship it, not on a map
it was never paired with. PVBM ships no artery/vein model and is not read; LUNet's and BF-Net's maps
belong to no project and are not read. The run still measures every pair, and those rows stay in
`results/`, but no table or figure here quotes them.

This overrides `SKILL.md` §3's model-first rule for this benchmark: **every table and figure is
indexed by project first, dataset second**, and the results page follows the same order. Where
programs are compared, it is on **one map shared by several projects** — OCULARNet under ocular and
fundus-biomarkers, AutoMorph's model under the three AutoMorph projects — so that the difference is
the program's alone. The headline panel is read per project with `biomarker_real.panel_for`, which
says which of the project's columns stands in where it has no column as the panel defines it.

## 2. What it must show, in the order of `SKILL.md` §4

1. **Coverage** — per model and dataset, how many photographs each map produced a number for, and
   how often the model's map produced none where the expert's did.
2. **The distribution behind each ICC** — for the headline panel as each project answers it,
   expert against own-model scatter plots and Bland–Altman plots (difference against mean), one row
   per project, a colour per dataset. One ICC can hide a cloud that is tight except for a few
   photographs, or a constant offset.
3. **ICC and SNR across every catalogued biomarker** — by family, project by project and dataset
   by dataset, so a reader sees which families survive a project's own map and which do not. With
   it, IQR against MAPE per project, a dot per column and dataset and a drop-down per family. Say
   that the IQR comes from the expert's maps alone, so a dot's height is the dataset and the kind of
   measure, and only its MAPE is the pipeline's.
4. **Where the programs disagree** — the same biomarker on one model's maps, read by the projects
   that share it. A biomarker robust in one program and fragile in another is a finding about the
   program's tracing, not about the model.
5. **What the hard cases look like** — per project, per dataset, the photograph with the largest
   difference on the project's first panel biomarker, the expert's map beside its own model's.
6. **What it costs** — per project and dataset, the program's seconds per map on one core, and its
   own model's seconds per photograph from the artery/vein benchmark, with that device.
7. **What it cannot say** — no second reader, contamination, scale-free photographs, pooled versus
   per-dataset.

## 3. Read SNR and ICC together

A high SNR with a low ICC(A,1) is a **bias**: correctable in principle, and named as such. A low SNR
is **scatter**, which nothing downstream can correct. Say which, wherever a biomarker is called
fragile.
