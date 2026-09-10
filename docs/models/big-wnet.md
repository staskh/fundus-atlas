# Big W-Net

Big W-Net is the artery-vein sibling of [LWNet](lwnet.md), from the same paper and repository: the
same idea of chaining two small U-Nets, scaled up for the harder task of deciding which vessels are
arteries and which are veins.

It is documented separately because it is a different task with its own weights and its own training
data, and because a reader comparing artery-vein models needs to find it under that heading rather
than inside a vessel-segmentation entry.

## 1. Code reference

- **Repository:** https://github.com/agaldran/lwnet
- **Version described here:** commit `ce72ddab` (2024-01-16). No tags or releases.
- **Most recent commit:** 2024-01
- **Training code included:** Yes, in this repository — `train_cyclical.py`, with artery-vein split
  CSVs (`train_av.csv`, `val_av.csv`, `test_av.csv`) produced by `get_public_data.py`.
- **Language and how it runs:** Python with PyTorch. `predict_one_image_av.py` runs one photograph;
  `generate_av_results.py` runs a dataset.

## 2. License

- **Code:** MIT.
- **Model weights:** No separate license stated; committed in the repository.

## 3. Major publications by the authors

- Galdran A, Anjos A, Dolz J, Chakor H, Lombaert H, Ben Ayed I. *The Little W-Net That Could:
  State-of-the-Art Retinal Vessel Segmentation with Minimalistic Models.* 2020.
  [arXiv:2009.01907](https://arxiv.org/abs/2009.01907)

## 4. What it produces

- **Purpose:** `artery/vein`
- **Output classes:** multi-class — artery against vein.
- **Input grid:** depends on which published configuration you load — **512×512** for the DRIVE-AV
  weights, **1024×1024** for the HRF-AV weights. Two grids means two models in practice, and the
  1024 configuration costs four times the pixels.
- **Output grid:** the artery/vein mask at the input grid, resampled back to the original
  photograph's dimensions as in the vessel path.
- **Grid set in:** `"im_size"` in `experiments/big_wnet_drive_av/config.cfg` (512) and
  `experiments/big_wnet_hrf_av_1024/config.cfg` (1024).
- **Input expected:** a colour-fundus photograph. Two configurations are published, one for DRIVE
  and one for HRF at 1024 pixels, so the expected resolution depends on which weights are used.
- **Preprocessing in the published code:** per-dataset preparation by `get_public_data.py`, which
  for DRIVE also produces the Zone B masks used to score artery-vein performance in the region
  around the optic disc — a stricter and more clinically relevant evaluation than whole-image
  scoring.

## 5. Architecture

- **Family:** W-Net — two chained U-Nets — in its larger configuration.
- **Parameters:** Unknown; larger than the roughly 70,000 of the little W-Net.
- **Single model or ensemble:** a single model per configuration.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| DRIVE (artery/vein labels) | Training | The dataset's own authors | Yes, `train_av`/`val_av`/`test_av` CSVs |
| HRF (artery/vein labels) | Training, 1024 px configuration | The dataset's own authors | Yes |

DRIVE and HRF cannot be used to benchmark these weights — a limitation shared with
[BF-Net](bf-net.md), which trained on the same two datasets plus LES-AV, so those two models cannot
be compared on either dataset in a way that favours neither.

## 7. Weights

- **Publicly available:** Yes, committed in the repository.
- **Download URLs:**
  - https://github.com/agaldran/lwnet/tree/main/experiments/big_wnet_drive_av
  - https://github.com/agaldran/lwnet/tree/main/experiments/big_wnet_hrf_av_1024
- **Format and size:** PyTorch `model_checkpoint.pth`, with a `config.cfg` and validation metrics
  beside each.
- **Files in an ensemble:** one per configuration.

## 8. Performance as reported by the authors

The paper reports artery-vein results including performance within DRIVE's Zone B. Numbers are in
the paper and are not restated here.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| — | No catalogued pipeline runs this model | — |

It is catalogued because it is a well-licensed, well-documented artery-vein baseline that the
comparison tables should include, and because readers reach the repository looking for it.

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- Two published configurations means two models in practice; record which one produced a result.
- Like its smaller sibling, it runs on modest hardware, which makes it a reasonable baseline before
  reaching for a larger artery-vein model.

---

**Links and license last checked:** 2026-09-10
