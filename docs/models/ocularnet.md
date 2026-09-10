# OCULARNet

OCULARNet separates arteries from veins, and adds a class the other models in this catalogue leave
out: **crossings**, the points where an artery and a vein overlap. Those points are where
artery-vein classification usually fails and where several clinical signs are read, so making them
an explicit class rather than an ambiguity is the model's distinguishing choice.

Its second choice is what it optimises for. Its authors state they prioritise the fidelity of the
vascular measurements a clinician would derive — topology, junctions, vessel calibre — over
pixel-wise overlap with a reference mask, on the argument that a high overlap score does not
guarantee usable biomarkers.

## 1. Code reference

- **Repository:** https://github.com/GonzaloPlaaza/OCULAR
- **Version described here:** commit `34b1ecc3` (2026-08-06). No tags or releases.
- **Most recent commit:** 2026-08
- **Training code included:** Yes, in this repository — `train.py`, driven by split CSVs with
  templates under `data_splits/`. With the published training-set list this is the most reproducible
  artery-vein model here.
- **Language and how it runs:** Python with PyTorch.
  `python inference.py --input_dir data/images --output_dir segmentations/ --weights … --device cuda`,
  with `--ensemble` for the nano five-fold variant.

## 2. License

- **Code:** **None stated.** No LICENSE file, so no permission to reuse or redistribute has been
  granted regardless of intent. Ask the authors.
- **Model weights:** No license stated on either Hugging Face repository.

## 3. Major publications by the authors

Unknown — no publication was found, and the repository shows the marks of being under review: its
own clone instructions point at an anonymised repository, the weights sit under an anonymous Hugging
Face account, and further annotations are promised "upon paper publication". Check for a paper
before relying on this model.

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** four — background, artery, vein, **crossings**.
- **Input expected:** RGB fundus photographs **already cropped to the field of view**; the
  repository is explicit about this, and the OCULAR dataset ships field-of-view masks and optic
  disc annotations for datasets that lacked them, resized to 1024×1024.
- **Preprocessing in the published code:** none beyond loading — cropping is the user's
  responsibility, which is a real difference from pipelines that crop for you.

## 5. Architecture

- **Family:** U-Net with a RepVGG encoder, `base_unet_repvgg_b3`.
- **Parameters:** Unknown; `b3` is the larger of the two backbones the authors release.
- **Single model or ensemble:** a single model. The smaller five-fold variant is a separate model —
  see [ocularnet-nano.md](ocularnet-nano.md).
- **Other architectures are available for retraining.** The repository's model factory
  (`utils/model_factory_seg.py`) can build U-Net, FPN, **SegFormer** (`segf_<encoder>`) and PSPNet
  through `segmentation_models_pytorch`, with RepVGG and other encoders. Those are training options,
  not released models: the published weights are the U-Net configurations named above. Anyone
  reporting a SegFormer result from this repository has trained it themselves, and it is a different
  model from the one this page documents.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| AVRDB, DRIVE, ENRICH, FIVES-AV, Fundus-AVSeg, GAVE, GRAPE, HRF, INSPIRE, LES-AV, Leuven-Haifa, MAGREBHIA, MESSIDOR-AV, PAPILA | Training | Their own authors; the OCULAR release adds harmonised field-of-view and disc annotations | Yes — the README tabulates image count, field of view, resolution, country and pathologies per dataset |
| DualModal, UNAF | In-distribution test | Their own authors | Yes |
| TREND-AV, IOSTAR-AV, MBRSET | Near out-of-distribution test | Their own authors | Yes |
| AV-WIDE, RAVIR | Far out-of-distribution test | Their own authors | Yes |

Fourteen datasets are unavailable for a fair benchmark of this model — which is most of the public
artery-vein data. The compensating virtue is that the authors declare the split up front and
separate their test sets by degree of distribution shift, which is the clearest statement of
expected generalisation in this catalogue.

## 7. Weights

- **Publicly available:** Yes.
- **Download URL:** https://huggingface.co/Anon-User-Retina/OCULARNet/resolve/main/OCULARNet.pth —
  an anonymous review account, which may be renamed when a paper appears, so expect this URL to
  break.
- **Format and size:** PyTorch `.pth`.
- **Files in an ensemble:** one.

## 8. Performance as reported by the authors

The repository states that the model improves agreement in vascular topology, junctions and vessel
calibre across diverse datasets, evaluated in and out of distribution. No paper was found, so there
are no citable per-dataset numbers yet. Recorded as the authors' claim.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [OCULARNet](../projects/ocularnet.md) | The segmentation stage, ahead of PVBM-based zone and junction extraction | The published weights |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- **Crossings change what downstream code sees.** A four-class output is not a drop-in replacement
  for a three-class artery/vein mask; code expecting the latter needs to decide what to do with the
  crossings class rather than ignore it silently.
- With no license (section 2) this is currently readable but not reusable.

---

**Links and license last checked:** 2026-09-10
