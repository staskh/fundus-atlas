# OCULARNet-nano

The small sibling of [OCULARNet](ocularnet.md): the same four-class artery-vein-and-crossings task,
the same training data, but built on the smallest RepVGG backbone and published as a five-fold
ensemble rather than a single network. It exists for users who need the model to run on modest
hardware or at volume.

It is documented separately because it has its own weights and its own behaviour. A result produced
by the nano ensemble is not a result produced by OCULARNet, and the two should never be pooled.

## 1. Code reference

- **Repository:** https://github.com/GonzaloPlaaza/OCULAR
- **Version described here:** commit `34b1ecc3` (2026-08-06). No tags or releases.
- **Most recent commit:** 2026-08
- **Training code included:** Yes, in this repository — `train.py`, driven by split CSVs with
  templates under `data_splits/`.
- **Language and how it runs:** Python with PyTorch. Inference needs the `--ensemble` flag:
  `python inference.py --input_dir data/images --output_dir segmentations/ --weights
  pretrained_weights/OCULARNet-nano/nano_f1.pth --ensemble --device cuda`. Passing a single fold
  without that flag runs one fold, which is a different model again.

## 2. License

- **Code:** **None stated.** No LICENSE file, so no reuse or redistribution permission has been
  granted. Ask the authors.
- **Model weights:** No license stated on the Hugging Face repository.

## 3. Major publications by the authors

Unknown — no publication was found. The repository shows the marks of being under review: anonymised
clone instructions, an anonymous weights account, and further annotations promised "upon paper
publication".

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** four — background, artery, vein, **crossings**.
- **Input expected:** RGB fundus photographs **already cropped to the field of view**; cropping is
  the user's responsibility.
- **Preprocessing in the published code:** none beyond loading.

## 5. Architecture

- **Family:** U-Net with a RepVGG encoder, `base_unet_repvgg_a0` — the smallest backbone in that
  family.
- **Parameters:** Unknown; smaller than OCULARNet's `b3` backbone.
- **Single model or ensemble:** **ensemble of five**, one per cross-validation fold, combined by the
  `--ensemble` flag.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| AVRDB, DRIVE, ENRICH, FIVES-AV, Fundus-AVSeg, GAVE, GRAPE, HRF, INSPIRE, LES-AV, Leuven-Haifa, MAGREBHIA, MESSIDOR-AV, PAPILA | Training | Their own authors, plus harmonised field-of-view and disc annotations from the OCULAR release | Yes — five folds, with template split CSVs in the repository |
| DualModal, UNAF | In-distribution test | Their own authors | Yes |
| TREND-AV, IOSTAR-AV, MBRSET | Near out-of-distribution test | Their own authors | Yes |
| AV-WIDE, RAVIR | Far out-of-distribution test | Their own authors | Yes |

The same fourteen training datasets are therefore unavailable for a fair benchmark of this model as
for OCULARNet.

## 7. Weights

- **Publicly available:** Yes.
- **Download URLs:** https://huggingface.co/Anon-User-Retina/OCULARNet-nano/resolve/main/nano_f1.pth
  through `nano_f5.pth` in the same repository — an anonymous review account, so expect these URLs
  to break when a paper appears.
- **Format and size:** PyTorch `.pth`, five files.
- **Files in an ensemble:** five.

## 8. Performance as reported by the authors

No paper was found, and the repository publishes no separate numbers for the nano variant. Whether
it matches the full model is Unknown, which is the first thing to establish before using it in place
of OCULARNet.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [OCULARNet](../projects/ocularnet.md) | Offered as the lightweight alternative in the inference script | The published five-fold weights |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- **Three ways to run this and two of them are undocumented models:** the five-fold ensemble as
  intended, a single fold by omitting `--ensemble`, or a subset. Record which was used.
- With no license (section 2) this is readable but not reusable.

---

**Links and license last checked:** 2026-09-10
