# Papers

Published work a reader of this atlas needs in order to interpret something else in it: a formula,
a comparison, a pitfall, or a map of a subfield. Each row in section 1 links to a detail page
recording the citation, what the paper is about in plain language, why it is here, and which
catalogued datasets, models, biomarkers or projects to open next.

This is not a bibliography of every paper the other catalogues cite. The describing paper of a
dataset, model or project stays on that entry's page. A paper gets a **detail page** only when a
reader would change how they interpret a number, a mask or a comparison after reading it. Every
other publication this atlas already mentions is listed in section 4, pointing at the page that
holds the citation.

Four things about this catalogue are worth reading before the table.

**A name is not a definition.** "Tortuosity" and "CRAE" each point at more than one paper, and the
pipelines in [PROJECTS.md](PROJECTS.md) do not all implement the same one. The definition rows below
are the reason those biomarker pages exist.

**Claim and observation stay apart.** What a paper reports about its own sample is its authors'
claim, on the detail page. What this atlas measured is in [BENCHMARKS.md](BENCHMARKS.md).

**Open is effort to read, not permission to reuse.** A green mark is a publisher or PMC copy. A
yellow mark is a copy off the publisher — an author PDF or ResearchGate — that may move. A paper
behind a paywall can still be the definition of a measurement this atlas catalogues.

**One paper, one page.** A preprint and its journal version are one entry. A conference paper that
was later expanded is noted on the journal page, not given a row of its own.

## 1. Summary

Grouped by kind. Within each group, alphabetical by the first author's surname. Groups with no rows
yet are omitted; they appear when the first paper of that kind is added.

**Open** is how a reader actually gets the text:

| | |
| --- | --- |
| ✅ | **Publisher or PMC.** A stable, freely readable copy |
| 🟡 | **Off the publisher.** An author PDF, a preprint, or ResearchGate — usable, liable to move |
| ⛔ | **Paywalled**, and no stable free copy was established; see the page |

### 1.1 Definitions — papers that first published a measurement this atlas catalogues

| Paper | Year | What it is for | Relates to | Open | Last checked |
| --- | --- | --- | --- | --- | --- |
| [Bankhead 2012](papers/bankhead-2012.md) | 2012 | Vessel width from image edges, not from a mask | Calibre; ARIA; DRIVE | ✅ | 2026-09-21 |
| [Fhima 2022](papers/fhima-2022.md) | 2022 | Junction counts, vessel area and length; the PVBM toolbox | Junctions; area/length; PVBM | 🟡 | 2026-09-21 |
| [Giesser 2024](papers/giesser-2024.md) | 2024 | A proprietary tortuosity score (VCI) and its five-minute retest | Tortuosity; AutoMorph | ✅ | 2026-09-21 |
| [Grisan 2008](papers/grisan-2008.md) | 2008 | Tortuosity as density of constant-sign bends | Tortuosity; retipy; AutoMorph | 🟡 | 2026-09-21 |
| [Hart 1999](papers/hart-1999.md) | 1999 | Seven tortuosity formulas, and which of them compose | Tortuosity; tracing | 🟡 | 2026-09-21 |
| [Hubbard 1999](papers/hubbard-1999.md) | 1999 | Central retinal equivalents and AVR, for ARIC | CRAE/CRVE; AVR | ⛔ | 2026-09-21 |
| [Knudtson 2003](papers/knudtson-2003.md) | 2003 | The scale-invariant revision most pipelines actually run | CRAE/CRVE; AVR; AutoMorphalyzer | ⛔ | 2026-09-21 |
| [Vargas 2026](papers/vargas-2026.md) | 2026 | Sparsity, temporal angle, disc–fovea distance; VascX toolbox | Sparsity; temporal angle; VascX | 🟡 | 2026-09-21 |

### 1.2 Findings — a result that changes how a number in this atlas should be read

| Paper | Year | What it is for | Relates to | Open | Last checked |
| --- | --- | --- | --- | --- | --- |
| [Naim 2026](papers/naim-2026.md) | 2026 | Dice can look fine while tortuosity is wrong | Tortuosity; tracing; DRIVE | ✅ | 2026-09-21 |

## 2. How to read this table

- **Kind** — why the paper is here, not a field-wide taxonomy. `definition` is a first formula;
  `method` is a method whose artefact, if catalogued, lives on its own page; `comparison` is prior
  work this atlas's own scores should be read against; `finding` is a result that changes how a
  number here should be read (reproducibility, scale, a unit trap); `review` maps a subfield. A
  paper has one kind.
- **What it is for** — one phrase. The reason we kept it is on the page, in section 3.
- **Relates to** — the catalogued entry to open next. A paper with no such link does not belong
  yet.
- **Open** — effort to *read*. It says nothing about whether figures or text may be reused.
- **Known caveats** are not in this table. Every detail page carries a Notes section: an unpublished
  formula, a unit that only works in microns, a conference DOI a codebase cites instead of the
  journal's.

## 3. Adding a paper

Paper pages follow a fixed structure so they can be read against each other. Load the
`document-paper` skill, which defines that structure and this table's columns, before adding or
changing an entry. A describing paper of a dataset, model or project does not get a detail page
unless it also does one of the jobs in section 1; it does get a row in section 4.

## 4. Publications recorded elsewhere

Every other publication mentioned in this atlas, arranged by where the citation already lives.
These rows are a lookup, not a second catalogue: the full citation is on the linked page. Papers
from section 1 are not repeated.

A dataset, model or project with **no describing publication established** is listed at the end of
its group, so a missing paper is visible rather than silent.

### 4.1 Dataset papers

| Paper | Year | What it described | Recorded on |
| --- | --- | --- | --- |
| Akram 2020 | 2020 | AVRDB | [AVRDB](datasets/avrdb.md) |
| Almazroa 2018 | 2018 | RIGA | [RIGA](datasets/riga.md) |
| Bajwa 2020 | 2020 | G1020 | [G1020](datasets/g1020.md) |
| Budai 2013 | 2013 | HRF vessels | [HRF](datasets/hrf.md) |
| Chalakkal et al. | — | UoA-DR (deposit citation) | [UoA-DR](datasets/uoa-dr.md) |
| Decencière 2014 | 2014 | Messidor | [Messidor](datasets/messidor.md); [MAPLES-DR](datasets/maples-dr.md) |
| Estrada 2015 | 2015 | WIDE; REYIA photographs | [WIDE](datasets/wide.md); [REYIA](datasets/reyia.md) |
| Fang 2022 | 2022 | ADAM challenge | [ADAM](datasets/adam.md) |
| Fang et al. | 2022 | REFUGE2 | [REFUGE](datasets/refuge.md) |
| Fhima 2024 | 2024 | UNAF, with LUNet | [UNAF](datasets/unaf.md); [LUNet](models/lunet.md) |
| Fhima 2025 | 2025 | REYIA; RLAD | [REYIA](datasets/reyia.md); [RLAD](models/rlad.md) |
| FOVEA | 2025 | FOVEA | [FOVEA](datasets/fovea-dataset.md) |
| FQS | 2025 | FQS | [FQS](datasets/fqs.md) |
| Fraz 2012 | 2012 | CHASE-DB1 | [CHASE-DB1](datasets/chase-db1.md) |
| Fu 2019 | 2019 | EyeQ; MCF-Net quality | [EyeQ](datasets/eyeq.md); [AutoMorph quality](models/automorph-quality-grader.md) |
| Fumero 2020 | 2020 | RIM-ONE DL | [RIM-ONE DL](datasets/rim-one-dl.md) |
| Fundus AVSeg | 2025 | Fundus AVSeg | [Fundus AVSeg](datasets/fundus-avseg.md) |
| Hatamizadeh 2022 | 2022 | RAVIR | [RAVIR](datasets/ravir.md) |
| Hemelings 2019 | 2019 | HRF artery/vein | [HRF](datasets/hrf.md) |
| Hoover 2000 | 2000 | STARE | [STARE](datasets/stare.md) |
| HRF-Seg+ | 2025 | HRF disc, cup, zones | [HRF](datasets/hrf.md) |
| Hu 2013 | 2013 | RITE artery/vein | [RITE](datasets/rite.md) |
| Hu 2021 | 2021 | VC-Net; Tongren layers | [VC-Net](models/vc-net.md); [HRF](datasets/hrf.md); [LES-AV](datasets/les-av.md); [RITE](datasets/rite.md) |
| Huang 2023 | 2023 | GRAPE | [GRAPE](datasets/grape.md) |
| Jin 2022 | 2022 | FIVES | [FIVES](datasets/fives.md) |
| Jin 2023 | 2023 | MSHF | [MSHF](datasets/mshf.md) |
| Kaggle EyePACS | 2015 | EyeQ photographs (competition, not a paper) | [EyeQ](datasets/eyeq.md) |
| Kovalyk 2022 | 2022 | PAPILA | [PAPILA](datasets/papila.md) |
| Kumar 2023 | 2023 | Chákṣu | [Chákṣu](datasets/chaksu.md) |
| Lepetit-Aimon 2024 | 2024 | MAPLES-DR | [MAPLES-DR](datasets/maples-dr.md) |
| Liu 2022 | 2022 | DeepDRiD | [DeepDRiD](datasets/deepdrid.md) |
| Lyu 2022 | 2022 | RETA | [RETA](datasets/reta.md) |
| Nakayama 2024 | 2024 | BRSET | [BRSET](datasets/brset.md) |
| Niemeijer 2011 | 2011 | INSPIRE-AVR | [INSPIRE-AVR](datasets/inspire-avr.md) |
| Orlando 2018 | 2018 | LES-AV | [LES-AV](datasets/les-av.md) |
| Orlando 2020 | 2020 | REFUGE challenge | [REFUGE](datasets/refuge.md) |
| Porwal 2018 | 2018 | IDRiD | [IDRiD](datasets/idrid.md); [RETA](datasets/reta.md) |
| Şevik 2014 | 2014 | DRIMDB | [DRIMDB](datasets/drimdb.md) |
| Sivaswamy 2015 | 2015 | Drishti-GS | [Drishti-GS](datasets/drishti-gs.md) |
| Staal 2004 | 2004 | DRIVE; RITE photographs | [DRIVE](datasets/drive.md); [RITE](datasets/rite.md) |
| Van Eijgen 2024 | 2024 | Leuven-Haifa | [Leuven-Haifa](datasets/leuven-haifa.md) |
| Vargas 2025 | 2025 | RAV | [RAV](datasets/rav.md) |
| Wang 2026 | 2026 | FunPiQ | [FunPiQ](datasets/funpiq.md) |
| Wu 2023 | 2023 | GAMMA challenge | [GAMMA](datasets/gamma.md) |
| Zhang 2010 | 2010 | ORIGA | [ORIGA](datasets/origa.md) |
| Zhang 2016 | 2016 | IOSTAR | [IOSTAR](datasets/iostar.md) |
| Zhang 2019 | 2019 | DualModal2019 | [DualModal2019](datasets/dualmodal2019.md) |
| — | — | GAVE: no describing publication established | [GAVE](datasets/gave.md) |
| — | — | VICAVR: no canonical dataset publication | [VICAVR](datasets/vicavr.md) |
| — | — | mBRSET: cite PhysioNet and the paper listed there | [mBRSET](datasets/mbrset.md) |

### 4.2 Model papers

Papers that describe a catalogued model and are not already in section 4.1.

| Paper | Year | What it described | Recorded on |
| --- | --- | --- | --- |
| Ahmed 2025 | 2025 | LHU-VT | [LHU-VT](models/lhu-vt.md) |
| Engelmann et al. | — | QuickQual (no DOI established) | [QuickQual](models/quickqual.md); [QuickQual-MEME](models/quickqual-meme.md) |
| Galdran 2020 | 2020 | LWNet; Big W-Net | [LWNet](models/lwnet.md); [Big W-Net](models/big-wnet.md) |
| Gervelmeyer 2025 | 2025 | Fundus Image Toolbox | [FIT quality](models/fit-quality.md); [FIT fovea/OD](models/fit-fovea-od.md) |
| Jiang 2026 | 2026 | LCNet | [LCNet](models/lcnet.md) |
| Köhler 2024 | 2024 | FR-UNet ensemble; mask QC | [FR-UNet](models/frunet-fives.md) |
| Lei 2021 | 2021 | ISFA | [ISFA](models/isfa.md) |
| Liu 2022 | 2022 | FR-UNet architecture | [FR-UNet](models/frunet-fives.md) |
| Liu 2022 | 2022 | SuperRetina | [SuperRetina](models/superretina.md) |
| Sobhan 2026 | 2026 | LightVesselNet | [LightVesselNet](models/lightvesselnet.md) |
| Vargas 2025 | 2025 | VascX segmentation models | [VascX](projects/vascx.md); [VascX vessels](models/vascx-vessels.md) |
| Wang 2019 | 2019 | BEAL | [BEAL](models/beal.md) |
| Xie 2021 | 2021 | SegFormer (architecture only) | [SegFormer disc/cup](models/segformer-disc-cup.md) |
| Zhou 2021 | 2021 | BF-Net / Learning-AVSegmentation | [BF-Net](models/bf-net.md); [AutoMorph A/V](models/automorph-artery-vein.md) |
| Zhou 2021 | 2021 | SEGAN vessel segmenter | [SEGAN](models/segan-vessel.md) |
| Zhou 2022 | 2022 | AutoMorph pipeline | [AutoMorph](projects/automorph.md); [AutoMorphalyzer](projects/automorphalyzer.md); [AutoMorphClass](projects/automorphclass.md) |
| — | — | OCULARNet: no paper yet | [OCULARNet](models/ocularnet.md); [project](projects/ocularnet.md) |
| — | — | Retina-MVP A/V: no paper | [Retina-MVP A/V](models/retina-mvp-av.md) |
| — | — | SegFormer disc/cup weights: no paper | [SegFormer disc/cup](models/segformer-disc-cup.md) |

Two Liu 2022 rows and two Zhou 2021 rows are different papers. Vargas 2025 here is the TVST *VascX
Models* paper, not the RAV dataset preprint in 4.1.

### 4.3 Other project and incidental papers

| Paper | Year | What it described | Recorded on |
| --- | --- | --- | --- |
| arXiv:2512.16044 | 2025 | retinalysis-fundusprep | [VascX](projects/vascx.md) |
| Tummala 2023 | 2023 | FIT quality comparison cite | [FIT quality](models/fit-quality.md) |
| — | — | retipy: no project paper established | [retipy](projects/retipy.md) |
