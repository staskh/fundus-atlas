# Projects

Publicly available pipelines that take a colour-fundus photograph and return numbers, by combining
segmentation models with biomarker calculations. Each row links to a detail page describing that
pipeline: its code, license, models, biomarkers, and examples.

This is a lookup table, not a ranking. Different pipelines were built for different images and
different questions.

## 1. Summary

| Project | What it produces | Segmentation models | New models introduced | Weights public | Code license | Last commit | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [OCULARNet](projects/ocularnet.md) | Segmentations plus junction, crossing and major-vessel zone masks; biomarkers via PVBM | OCULARNet and OCULARNet-nano, four classes including vessel crossings (introduced here); disc segmenter borrowed | Yes | Yes, on Hugging Face | None stated — no LICENSE file | 2026-08 | 2026-09-10 |
| [VascX](projects/vascx.md) | Central retinal equivalents, calibers, AVR, density, bifurcation and temporal angles, tortuosity, sparsity, quality metrics | VascX ensembles: vessels, artery/vein, disc, fovea, quality (all introduced here) | Yes | Yes, on Hugging Face | Not stated — no LICENSE file; weights are AGPL-3.0 | 2026-08 | 2026-09-10 |
| [AutoMorphClass](projects/automorphclass.md) | AutoMorph's vascular features, returned as a PyTorch tensor or named dict | AutoMorph's vessel, artery/vein and disc models (all borrowed) | No | Yes, committed in the repository | Unclear — MIT declared in the README and `pyproject.toml`, but no LICENSE file | 2026-05 | 2026-09-10 |
| [AutoMorphalyzer](projects/automorphalyzer.md) | Corrected AutoMorph measurements: tortuosity, calibre, density, fractal dimension, CRAE/CRVE/AVR (Knudtson only), quality probability | SEGAN vessels, BF-Net artery/vein and the lwnet-derived disc/cup model (all borrowed via AutoMorph), QuickQual quality (borrowed) | No | Yes, from this repository's releases | Apache-2.0 | 2026-03 | 2026-09-10 |
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
- **Known defects** are not in this table. Every detail page carries a section 8 recording bugs that
  change the numbers a user would report, with the upstream issue documenting each one and whether
  it is fixed. Read it before trusting a biomarker from any project here. Four of the nine pages
  currently record a defect; `None recorded` on the others means no finding, not a clean bill of
  health.

## 3. Considered and not included

Not everything found in a search belongs in this table. These were looked at and left out, with the
reason, so nobody repeats the search:

- **QUARTZ** (Quantitative Analysis of Retinal vessel Topology and siZe) — published and widely
  cited, but no public code repository was found. An annotation tool and a branching-angle benchmark
  set from the same group are public; the pipeline itself is not.
- **Individual models** — LWNet, LUNet, BF-Net (Learning-AVSegmentation), QuickQual and EyeQ are
  single models, not pipelines. They are catalogued in [MODELS.md](MODELS.md), and are named on the
  pages of the projects that use them.
- **retinalysis-fundusprep** — preprocessing only (image bounds, cropping, contrast). It is a
  component of VascX, recorded on that page.
- **BEAL and ISFA** — optic disc and cup segmentation across cameras by domain adaptation. Both
  compute no biomarkers, so neither is a pipeline; both are catalogued as models instead, at
  [models/beal.md](models/beal.md) and [models/isfa.md](models/isfa.md).

### 3.1 Kaggle (searched 2026-09-10)

Kaggle was searched for pipelines that take a colour-fundus photograph and return vascular
biomarkers — central retinal arteriolar and venular equivalents (CRAE / CRVE), the artery-to-vein
ratio (AVR), vessel width, tortuosity, or the fractal dimension of the vessel tree. The search used
Kaggle's public dataset list for those terms and for the names of the pipelines already in this
table (AutoMorph, PVBM, VAMPIRE). Queries that name those biomarkers or pipelines returned no
matching dataset and no hosted copy of those pipelines.

What Kaggle does hold is useful as a pointer, not as a project. It falls into four groups.

**Competitions that grade disease, not biomarkers.** These are large public collections of fundus
photographs labelled for diabetic-retinopathy severity. Winning notebooks classify the photograph;
they do not trace vessels and measure them.

| Competition | What it asks for | Link |
| --- | --- | --- |
| Diabetic Retinopathy Detection (EyePACS, 2015) | Five-level diabetic-retinopathy grade | https://www.kaggle.com/competitions/diabetic-retinopathy-detection |
| APTOS 2019 Blindness Detection | Five-level diabetic-retinopathy grade | https://www.kaggle.com/competitions/aptos2019-blindness-detection |

The Retinal Image Analysis for multi-Disease Detection (RIADD) challenge, which released the
Retinal Fundus Multi-Disease Image Dataset (RFMiD), was hosted on Grand Challenge, not on Kaggle.
Kaggle holds unofficial copies of that dataset (see the table below).

**Closest items, still not pipelines.** Three uploads compute or ship numbers, but none is an
end-to-end biomarker pipeline under the definition at the top of this page.

| Item | What it actually is | Why it is not a project | Link |
| --- | --- | --- | --- |
| Feature Extraction (fractal dimensions and topological data analysis) | A 2019 script that turns APTOS photographs into fractal-dimension and persistent-homology features, then classifies diabetic-retinopathy grade with a simpler model than a neural net | The fractal number is taken from the photograph as a whole, not from a traced vessel tree; CRAE, CRVE, AVR and tortuosity are not computed | https://www.kaggle.com/datasets/jclchan/feature-extraction |
| Chákṣu (Kaggle subset) | A 440-image subset of the Chákṣu glaucoma dataset, with optic-disc and optic-cup masks and a table of precomputed glaucoma features (cup-to-disc ratios and related geometry) | It is a data release. The numbers are already in a spreadsheet; there is no runnable pipeline that starts from a new photograph. The full dataset (1,345 images) lives at its original source | https://www.kaggle.com/datasets/fahad20ali/chaksu · paper: https://doi.org/10.1038/s41597-023-01943-4 |
| Diabetic Retinopathy Debrecen | A tabular copy of the UCI features extracted from MESSIDOR photographs (image-quality scores, microaneurysm counts, exudate measures, disc diameter) | Lesion and quality features, not vascular morphology. No segmentation code, no CRAE / CRVE / tortuosity | https://www.kaggle.com/datasets/namigabbasov/diabetic-retinopathy-debrecen |

**Dataset mirrors.** These are community re-uploads of public fundus collections. They are inputs
to a pipeline, not pipelines. Prefer the original host when cataloguing a dataset: several Kaggle
copies carry a more permissive license statement than the source does, and this atlas records the
license as the owner stated it.

| Collection | Typical Kaggle copy | Original host to prefer |
| --- | --- | --- |
| DRIVE (vessel outlines) | https://www.kaggle.com/datasets/andrewmvd/drive-digital-retinal-images-for-vessel-extraction | https://drive.grand-challenge.org/ |
| FIVES (vessel outlines) | https://www.kaggle.com/datasets/nikitamanaenkov/fundus-image-dataset-for-vessel-segmentation | https://doi.org/10.6084/m9.figshare.19688169.v1 |
| RITE (artery / vein labels on DRIVE) | https://www.kaggle.com/datasets/priyanagda/ritedataset | https://eye.medicine.uiowa.edu/rite-dataset |
| DRIVE + STARE + CHASE_DB1 + HRF + FIVES together | https://www.kaggle.com/datasets/umairinayat/retinal-vessel-segmentation-datasets | each dataset's own host |
| RFMiD (46-condition labels) | https://www.kaggle.com/datasets/andrewmvd/retinal-disease-classification | https://ieee-dataport.org/open-access/retinal-fundus-multi-disease-image-dataset-rfmid |
| IDRiD (diabetic-retinopathy lesions and grades) | https://www.kaggle.com/datasets/aaryapatel98/indian-diabetic-retinopathy-image-dataset | https://idrid.grand-challenge.org/ |
| ORIGA + REFUGE + G1020 (disc and cup outlines) | https://www.kaggle.com/datasets/arnavjain1/glaucoma-datasets | each challenge's own host |
| SMDG-19 (nineteen glaucoma sets, some with vessel and disc/cup outlines) | https://www.kaggle.com/datasets/deathtrooper/multichannel-glaucoma-benchmark-dataset | each constituent dataset's own host |
| MESSIDOR-2 grades (labels only; photographs are elsewhere) | https://www.kaggle.com/datasets/google-brain/messidor2-dr-grades | the MESSIDOR authors' release |
| APTOS 2019 photographs (competition data re-hosted) | https://www.kaggle.com/datasets/mariaherrerot/aptos2019 | https://www.kaggle.com/competitions/aptos2019-blindness-detection |

**Teaching notebooks.** Popular kernels on those vessel-segmentation datasets train a U-Net or a
similar network to colour in the vessels. They stop at the mask. Representative examples:

- https://www.kaggle.com/code/ipythonx/medicai-retinal-vessel-segmentation-with-gradcam
- https://www.kaggle.com/code/mohamedadlyi/retinal-vessel-segmentation
- https://www.kaggle.com/code/avikumart/healthcare-datasci-retinal-fundus-segmentation
- https://www.kaggle.com/code/likithps/retinal-vessel-segmentation

None of these was added as a project. The datasets belong in the dataset catalogue, at their
original hosts.

## 4. Adding a project

Project pages follow a fixed structure so they can be read against each other. Load the
`document-project` skill, which defines that structure and this table's columns, before adding or
changing an entry.
