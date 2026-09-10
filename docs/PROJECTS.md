# Projects

Publicly available pipelines that take a colour-fundus photograph and return numbers, by combining
segmentation models with biomarker calculations. Each row links to a detail page describing that
pipeline: its code, license, models, biomarkers, and examples.

This is a lookup table, not a ranking. Different pipelines were built for different images and
different questions.

## 1. Summary

| Project | What it produces | Segmentation models | New models introduced | Weights public | Code license | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [VascX](projects/vascx.md) | Central retinal equivalents, calibers, AVR, density, bifurcation and temporal angles, tortuosity, sparsity, quality metrics | VascX ensembles: vessels, artery/vein, disc, fovea, quality (all introduced here) | Yes | Yes, on Hugging Face | Not stated — no LICENSE file; weights are AGPL-3.0 | 2026-08 | 2026-09-10 |
| [PVBM](projects/pvbm.md) | 15 biomarkers per artery and vein mask: areas, lengths, tortuosity, branching angles, fractal dimensions, CRAE/CRVE | Optic disc only (borrowed from LUNet); artery/vein masks must come from elsewhere | No | Yes, downloaded at first use | MIT | 2026-01 | 2026-09-10 |
| [AutoMorph](projects/automorph.md) | Vessel width, tortuosity, fractal dimension, CRAE/CRVE/AVR, cup-to-disc ratio | Four separate borrowed models: EyeQ quality, SEGAN-style vessel segmenter, BF-Net artery/vein, lwnet disc/cup | No — borrowed architectures, retrained weights | Yes, committed in the repository | Apache-2.0 (two borrowed components are GPL-3.0 at source) | 2025-06 | 2026-09-10 |
| [retipy](projects/retipy.md) | Tortuosity measures, bifurcation detection | retipy vessel segmentation (classical image processing) | Yes — algorithmic | Not applicable | GPL-3.0 or later | 2019-05 | 2026-09-10 |
| [ARIA](projects/aria.md) | Vessel diameter | Wavelet vessel detection (not a trained model) | Yes — algorithmic | Not applicable | BSD 2-clause, stated in `Copyright.m` not a LICENSE file | 2016-05 | 2026-09-10 |

## 2. How to read this table

- **Segmentation models** — models marked `(borrowed)` came from another project; the detail page
  names the source. The same model appearing under several projects is normal.
- **New models introduced** — whether this project trained something of its own, which is where
  questions of training data and weight availability arise.
- **Weights public** — whether trained weights can be obtained from the authors. `Unknown` means we
  could not establish it, not that they are unavailable.
- **Last commit** — the year and month of the project's most recent commit, as a rough signal of
  whether it is still maintained. An old date is not a fault: a finished pipeline may need no
  changes.
- **Last checked** — when the links and license on the detail page were last verified. These
  projects move.

## 3. Considered and not included

Not everything found in a search belongs in this table. These were looked at and left out, with the
reason, so nobody repeats the search:

- **QUARTZ** (Quantitative Analysis of Retinal vessel Topology and siZe) — published and widely
  cited, but no public code repository was found. An annotation tool and a branching-angle benchmark
  set from the same group are public; the pipeline itself is not.
- **Kaggle material** — searching Kaggle returns fundus datasets and teaching notebooks that
  demonstrate vessel segmentation with U-Net and similar models. None found computes biomarkers, so
  none is a project by the definition above. The datasets belong in the dataset catalogue instead.
- **Individual models** — lwnet, LUNet, BF-Net (Learning-AVSegmentation) and EyeQ are single models,
  not pipelines. They belong in the segmentation-model catalogue, and are named on the pages of the
  projects that use them.
- **retinalysis-fundusprep** — preprocessing only (image bounds, cropping, contrast). It is a
  component of VascX, recorded on that page.

## 4. Adding a project

Project pages follow a fixed structure so they can be read against each other. Load the
`document-project` skill, which defines that structure and this table's columns, before adding or
changing an entry.
