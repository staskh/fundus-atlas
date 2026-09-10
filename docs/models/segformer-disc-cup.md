# SegFormer for optic disc and cup (pamixsun)

A SegFormer transformer fine-tuned on the REFUGE challenge dataset to outline the optic disc and the
optic cup. It is the most convenient disc-and-cup model in this catalogue: it lives on Hugging Face
in the standard `transformers` format, so four lines of Python download it and segment an image, with
no repository to clone, no environment to reconstruct and no weights to hunt for.

That convenience is why it is catalogued despite publishing no numbers. It is permissively licensed,
has non-trivial adoption, and states its architecture, training dataset and intended use — enough
for a reader to judge what it is, though not how well it performs. Measuring that is what this
atlas's comparison tables are for.

## 1. Code reference

- **Repository:** https://huggingface.co/pamixsun/segformer_for_optic_disc_cup_segmentation — a
  Hugging Face model repository. There is no accompanying code repository.
- **Version described here:** revision `main` as last modified on 2023-09-08. The repository
  publishes no tags, so a Hugging Face revision hash is the only way to pin a version.
- **Most recent commit:** 2023-09
- **Training code included:** No. Neither training nor evaluation code is published, so the model
  can be run but not retrained or reproduced.
- **Language and how it runs:** Python with `transformers`. `AutoImageProcessor` and
  `SegformerForSemanticSegmentation` load it by name; the card's example upsamples the logits back to
  the input resolution and takes an `argmax` to produce the mask. It runs on CPU.

## 2. License

- **Code:** Apache-2.0, declared in the model card.
- **Model weights:** Apache-2.0, the same declaration. That makes this the most permissively
  licensed disc-and-cup model here — worth noting beside the non-commercial
  [LUNet v2 disc segmenter](lunetv2-odc.md) that PVBM and OCULAR rely on.

## 3. Major publications by the authors

None. The model card's citation section is left as "[More Information Needed]". The author is given
as Xu Sun (https://pamixsun.github.io), with a contact email on the card. A companion model by the
same author, `pamixsun/swinv2_tiny_for_glaucoma_classification`, classifies glaucoma rather than
segmenting anatomy and is out of this catalogue's scope.

Absent a paper, cite the model repository and its revision.

## 4. What it produces

- **Purpose:** `disc/cup`
- **Output classes:** three, as declared in `config.json` — `Background`, `Optic disc`, `Optic cup`.
  Both structures come from one model in one pass, which is what allows a cup-to-disc ratio to be
  computed.
- **Input grid:** 512×512, square, applied automatically by the bundled image processor.
- **Output grid:** the model returns logits at **128×128** — one quarter of the input on each side,
  as SegFormer's all-MLP decode head does — and the card's example upsamples them bilinearly to the
  original photograph's dimensions before taking the class argmax. That upsampling is in *user*
  code, not in the model: skip it and the mask is a quarter-scale approximation, and its boundary
  precision never exceeds one 128-grid pixel however far it is upscaled — about 4 source pixels for
  a 512-wide photograph, more for a larger one.
- **Grid set in:** `{"do_resize": true, "size": 512}` in `preprocessor_config.json`; the upsample is
  the `nn.functional.interpolate(logits, size=image.shape[:2], mode="bilinear")` call in the model
  card's example.
- **Input expected:** a colour-fundus photograph in RGB. The card's example reads an image with
  OpenCV and converts colour space; the author states plainly that only fundus images should be fed
  to it. Whether the image should be cropped around the disc is not stated — REFUGE images are
  disc-centred, so behaviour on a wide macula-centred photograph is uncharacterised.
- **Preprocessing in the published code:** handled by the bundled `preprocessor_config.json`
  through `AutoImageProcessor`, which resizes and normalises. Nothing else is required of the
  caller.

## 5. Architecture

- **Family:** SegFormer — a hierarchical transformer encoder with a lightweight all-MLP decode head,
  proposed for general semantic segmentation by Xie et al.
  ([arXiv:2105.15203](https://arxiv.org/abs/2105.15203)) and fine-tuned here for fundus anatomy. It
  is the only transformer-based model in this catalogue; every other entry is a convolutional
  network.
- **Parameters:** Unknown — the specific SegFormer size (`b0` to `b5`) is not stated in the card.
- **Single model or ensemble:** a single model, published as `model.safetensors` with a
  `pytorch_model.bin` alongside.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| REFUGE challenge | Fine-tuning | The challenge organisers | No — the card says only that it was fine-tuned on REFUGE |

REFUGE cannot be used to benchmark this model. Note that [AutoMorph's disc-and-cup
model](automorph-disc-cup.md) was also trained on REFUGE, and [BEAL](beal.md) and
[ISFA](isfa.md) use it as their labelled source domain — so REFUGE is unusable for comparing any of
these four against each other. Drishti-GS and RIM-ONE-r3 are unusable for BEAL and ISFA but remain
available for this model, which makes them the practical common ground for a disc-and-cup
comparison.

## 7. Weights

- **Publicly available:** Yes, and this is the model's main advantage — they download automatically
  by model name.
- **Download URLs:**
  - https://huggingface.co/pamixsun/segformer_for_optic_disc_cup_segmentation/resolve/main/model.safetensors
  - https://huggingface.co/pamixsun/segformer_for_optic_disc_cup_segmentation/resolve/main/pytorch_model.bin
- **Format and size:** safetensors and PyTorch, with `config.json` and
  `preprocessor_config.json` in the repository.
- **Files in an ensemble:** one.

## 8. Performance as reported by the authors

**Unknown.** No metrics appear in the model card, no evaluation code is published and no paper
exists. Adoption is the only public signal: 630 downloads and 6 likes as of the last-checked date,
which is the highest of any fundus disc-and-cup model found on Hugging Face.

This is a gap, and an unusually clean one: a permissively licensed model with a plain interface and
no published performance is exactly the case where an independent measurement adds something. It
belongs in the comparison tables.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued pipeline runs this model | — |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health. Note that with
no published metrics, "no known defects" here carries even less reassurance than usual.

## 11. Notes

- **Trained on one dataset, so expect domain shift.** REFUGE is a single curated challenge set;
  performance on another clinic's camera is unmeasured. [BEAL](beal.md) and [ISFA](isfa.md) are the
  literature on that specific problem for this specific task, which makes the three a natural group
  to compare.
- **Cup inside disc is not enforced.** The three classes are predicted independently per pixel, so
  nothing guarantees the cup falls within the disc. Any cup-to-disc ratio computed from the raw
  output should be checked for that, since a violation makes the ratio meaningless rather than merely
  inaccurate.
- **No training code, no reproduction.** The model is a usable artefact, not a reproducible
  experiment.

---

**Links and license last checked:** 2026-09-10
