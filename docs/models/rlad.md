# RLAD — Retinal Layout-Aware Diffusion

RLAD does not trace anything in a photograph. It **makes photographs**: given a layout — where the
blood vessels run, where the optic disc and cup sit, where the lesions are — it generates a
fundus image that follows that layout while varying everything else. Its purpose is training data.
Because the vessel map that went in is a correct segmentation of the image that comes out, every
generated photograph arrives with its label already attached, and its authors use those pairs to
make artery/vein segmentation models generalise better to cameras they were not trained on.

It is catalogued here because that claim is about models this atlas measures, and because the
dataset it introduced — [REYIA](../datasets/reyia.md) — is catalogued already. **It cannot be run:
no weights are published** (section 7), so nothing here is measurable and nothing here is measured.

## 1. Code reference

- **Repository:** https://github.com/aim-lab/RLAD
- **Version described here:** commit `a9d63987` (2025-07-25) — the repository's **only** commit, on
  branch `main`.
- **Most recent commit:** 2025-07
- **Training code included:** Yes, in this repository — `Scripts/train.py` with `Runs/train.sh`, and
  `Scripts/generate_new_data.py` with `Runs/generate_images.sh` for generation. The README states
  the published model was trained on **4 A100-40GB GPUs**.
- **Language and how it runs:** Python with PyTorch and Hugging Face `diffusers`, installed as a
  package (`pip install -e .`) and driven by one YAML file,
  `configs/configsDiT/RLAD.yaml`.

## 2. License

**The repository contradicts itself, and this is not a detail a reader can resolve alone:**

- **Code:** the `LICENSE` file is the **Apache License 2.0** — permissive, commercial use allowed.
- **README:** "This project is licensed under the Creative Commons Attribution-NonCommercial 4.0
  International License, [see LICENSE file](LICENSE), **which prohibits commercial use**" — pointing
  at that same Apache file, which prohibits no such thing.
- **Model weights:** not published, so no licence applies to anything downloadable.

The two statements cannot both govern. Until the authors say which, the safe reading is the more
restrictive one — **non-commercial** — and anyone with a commercial interest should ask them rather
than rely on the file. Recorded as a defect in section 10.

## 3. Major publications by the authors

- Fhima J, Van Eijgen J, Beeckmans L, Jacobs T, Freiman M, Nakayama LF, Stalmans I, Baskin C,
  Behar JA. *Enhancing Retinal Vessel Segmentation Generalization via Layout-Aware Generative
  Modelling.* arXiv:2503.01190, submitted 2025-03-03, revised 2025-04-05. DOI:
  [10.48550/arXiv.2503.01190](https://doi.org/10.48550/arXiv.2503.01190) · also on
  [OpenReview](https://openreview.net/forum?id=41dtT6feKo).

The same paper introduces [REYIA](../datasets/reyia.md), 586 manually segmented retinal images,
which **is** published.

## 4. What it produces

- **Purpose:** `other` — image synthesis. It is not a segmentation model and belongs in none of the
  four segmentation groups; what it produces is a photograph, not a mask.
- **Output classes:** Not applicable. Its output is a synthetic colour-fundus photograph, optionally
  paired with the vessel map it was conditioned on, which then serves as that image's ground truth.
- **Input grid:** 512×512 for generation (`resolution: 512` in `configs/configsDiT/RLAD.yaml`). The
  layout is extracted from a real photograph first: the blood-vessel map at **2048** pixels
  (`special_bv_res`), the disc-and-cup and lesion maps at the photograph's natural resolution padded
  to **1472** (`seg_pad`).
- **Output grid:** 512×512. Nothing resamples it back to any original, because there is no original —
  the image is new.
- **Grid set in:** `resolution`, `special_bv_res` and `seg_pad` in `configs/configsDiT/RLAD.yaml`.
- **Input expected:** a real colour-fundus photograph to take the layout from, plus two switches —
  `CD_cond` for whether to impose the optic cup and disc, `L_cond` for whether to impose lesions.
  With both off, the model invents those structures itself.
- **Preprocessing in the published code:** three segmentation networks are run over the source
  photograph to extract the layout it will be conditioned on (section 5).

## 5. Architecture

- **Family:** a **Diffusion Transformer (DiT)** — a diffusion model whose denoiser is a transformer
  rather than a U-Net — fine-tuned from Hugging Face's `facebook/DiT-XL-2-512`, with a custom
  `Transformer2DModel` carrying the layout conditioning, and the VAE and noise scheduler of the
  stock `DiTPipeline`.
- **Parameters:** not stated by the authors.
- **Single model or ensemble:** one generator — but it does not run alone. It loads **three SwinV2
  segmenters** (`microsoft/swinv2-tiny-patch4-window8-256` fine-tuned) to extract the layout: one for
  blood vessels, one for the optic disc and cup, one for lesions. Those three are models in their own
  right, none of them published, and RLAD cannot generate a conditioned image without them.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| UZLF_TRAIN | Training | — | Yes: the authors' train split |
| [GRAPE](../datasets/grape.md) | Training | — | No |
| [MESSIDOR](../datasets/messidor.md) | Training | — | No |
| [PAPILA](../datasets/papila.md) | Training | — | No |
| MAGREB | Training | — | No |
| ENRICH (part of [REYIA](../datasets/reyia.md)) | Training | — | No |
| 1000images | Training | — | No |
| DDR (lesion train split) | Training | — | Yes: the lesion training split |
| EyePACS | Training | — | No |
| [G1020](../datasets/g1020.md) | Training | — | No |
| [IDRiD](../datasets/idrid.md) (lesion train split) | Training | — | Yes: the lesion training split |
| ODIR | Training | — | Yes: `ODIR_Train` |
| UZLF_VAL | Validation | — | Yes |
| DRTiD | Test | — | Yes |

Read from `train_datasets`, `val_dataset` and `test_dataset` in `configs/configsDiT/RLAD.yaml`,
which is the authoritative list; the README links the download page for each.

**This is a generator, so "trained on" means something different here.** A segmentation model that
trained on a dataset cannot be fairly scored on it. A *generator* that trained on a dataset
contaminates every segmentation model afterwards trained on its output — so a model augmented with
RLAD images has indirectly seen all fourteen collections above, and cannot be called out-of-sample
on any of them. Anyone reporting a benchmark score for an RLAD-augmented model has to say so.

## 7. Weights

- **Publicly available:** **No.** This is the single most consequential fact on the page.
- **Download URL:** none. `configs/configsDiT/RLAD.yaml` sets
  `load_weights_from: "trained_checkpoints/RLAD/checkpoint-82560/model.safetensors"` and the three
  segmenters to `trained_checkpoints/Segmenter/{bv,od,lesion}/model.safetensors` — **local paths on
  the authors' machines**. No `trained_checkpoints/` directory exists in the repository, the README
  offers no link, and the authors' Hugging Face account
  ([aim-lab](https://huggingface.co/aim-lab)) holds one unrelated model. Checked 2026-09-17.
- **Format and size:** `model.safetensors`, size unknown.
- **Files in an ensemble:** four would be needed — the generator and its three layout segmenters.

The paper promises that "both our code and dataset will be made publicly accessible", and both are:
the code is this repository and the dataset is [REYIA](../datasets/reyia.md). **Weights are not part
of that promise**, and their absence is consistent with it rather than a broken commitment. The
practical consequence stands either way: the model can be retrained on 4 A100s, and cannot be run.

## 8. Performance as reported by the authors

Two claims, both theirs, both from the README of the pinned commit and the paper of section 3.

**Realism of the generated images**, on DRTiD — FID and RET-FD both measure how close a set of
generated images is to a set of real ones, lower being closer:

| Generative model | Conditioning | FID ↓ | RET-FD ↓ |
| --- | --- | --- | --- |
| StyleGAN | lesions | 138.0 | 120.8 |
| StyleGAN2 | demographics | 98.1 | 116.0 |
| StyleGAN2 (private data) | artery/vein | 122.8 | — |
| Pix2PixHD (private data) | artery/vein | 86.8 | — |
| **RLAD** | artery/vein + lesions + cup/disc | **30.3** | **79.7** |

**Artery/vein segmentation trained with RLAD augmentation**, as average Dice across in-domain,
near-domain and out-of-domain datasets:

| Backbone | In-domain | Near-domain | Out-of-domain |
| --- | --- | --- | --- |
| [Little W-Net](lwnet.md) | — | 67.9 | 45.5 |
| [AutoMorph](../projects/automorph.md)'s pipeline, i.e. [BF-Net](bf-net.md) | 80.2 | 71.7 † | 57.9 † |
| [VascX](vascx-artery-vein.md) | 81.2 | 76.0 | 60.5 |
| [LUNet](lunet.md) | 83.4 | 77.3 | 61.1 |
| RETFound | 81.8 | 76.9 | 65.2 |
| **RETFound + RLAD** | **83.4** | **79.9** | **69.9** |
| SwinV2-large | 83.4 | 80.5 | 72.1 |
| **SwinV2-large + RLAD** | 83.4 | **80.7** | **72.5** |

The abstract's headline is that RLAD data "improved generalization in retinal vessel segmentation by
up to 8.1%". The largest absolute gain in their own table is RETFound out-of-domain, 65.2 → 69.9.

**† is the authors' own mark, and it is a claim about software catalogued here**: they annotate the
AutoMorph rows as "indicates data leakage during training" — that is, they believe AutoMorph's
artery/vein numbers in their near- and out-of-domain columns are flattered by AutoMorph having seen
those images. The model in question is [BF-Net](bf-net.md), which
[AutoMorph](../projects/automorph.md) runs. This atlas has not verified the claim and records it as
theirs rather than as a finding.

None of the segmentation models in that second table are published either; the comparison is between
training recipes, not between downloadable models.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued project runs this model | — |

## 10. Known defects

- **The licence contradicts itself.** The README claims CC BY-NC 4.0 and points at a LICENSE file
  containing Apache-2.0 (section 2). Open, as of the only commit; a user cannot tell whether
  commercial use is permitted, and the two answers are opposite.
- **The published configuration points at weights nobody has.** Running generation as documented
  fails at `load_weights_from` and at each of the three `seg_load_weights_from` paths, all of which
  name directories absent from the repository (section 7). Nothing in the README says the weights
  are withheld, so the failure looks like a broken install rather than a deliberate omission.
- **One commit, no history.** The repository was published as a single "Initial commit", so there is
  no way to see what changed between the paper's versions, and the pinned commit is the only thing
  that can be cited.
- **IDE settings are committed** (`.idea/`), including `deployment.xml` and `sshConfigs.xml` — a
  cosmetic defect, but those files describe someone's remote hosts.

## 11. Notes

- **Read this page as being about data, not about masks.** Nothing RLAD produces is a measurement of
  a real eye. Its output is synthetic, and its value is entirely in what a segmentation model learns
  from it.
- **A generated photograph is not evidence about a patient**, and a benchmark must never mix
  generated images into a test set. This atlas measures models on published photographs of real eyes.
- **Its three conditioning segmenters are uncatalogued models.** A blood-vessel, a disc-and-cup and a
  lesion segmenter, all SwinV2-tiny, all unpublished. If their weights are ever released, each is a
  page here — the disc-and-cup one would be directly comparable with the models in the
  [disc-and-cup benchmark](../benchmarks/disc-results.md).
- **The dataset is the part you can use today.** [REYIA](../datasets/reyia.md) — 586 manually
  segmented photographs, including the 111-image ENRICH set — came from this work and is public.

---

**Links and license last checked:** 2026-09-17
