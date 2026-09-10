# LUNet v2 optic disc segmenter (`lunetv2_odc`)

This model segments the optic disc, and it is the disc segmenter used by PVBM and by OCULAR. It is
also the least well documented model in this catalogue, which is why it has a page of its own rather
than a line inside [LUNet](lunet.md): a reader needs to know how little is established about it.

What is known: PVBM's code downloads a file named `lunetv2_odc.onnx` from Google Drive on first use,
and PVBM's README states the disc segmenter "has been done using LUNet". Everything else — the
training data, the exact architecture, the version, who produced this file — is Unknown.

## 1. Code reference

- **Repository:** none of its own. The model file is fetched by
  [PVBM](https://github.com/aim-lab/PVBM)'s `PVBM/DiscSegmenter.py`, and is also republished as a
  release asset by [AutoMorphalyzer](https://github.com/jaburke166/AutoMorphalyzer). Its stated
  ancestor is [aim-lab/LUNet](https://github.com/aim-lab/LUNet).
- **Version described here:** the file served by the Google Drive link in section 7, as of the
  last-checked date below. There is no version identifier, so this page cannot pin one.
- **Most recent commit:** Not applicable — the file is not held in any repository. PVBM's download
  code was last touched in the 2026-01 state of that repository.
- **Training code included:** No. LUNet's repository publishes training code for its artery/vein
  model; whether this disc model was produced with it is Unknown.
- **Language and how it runs:** ONNX, executed through `onnxruntime` at 512 pixels by PVBM's
  `DiscSegmenter`, which then post-processes the mask into a disc centre, radius and the zones used
  for biomarker regions.

## 2. License

- **Code:** the loading code is PVBM's, MIT.
- **Model weights:** No license statement accompanies the file. Its stated ancestor, LUNet, is
  licensed **CC BY-NC 4.0 — non-commercial**, and nothing indicates the derivative is licensed more
  permissively. Treat it as non-commercial until the authors say otherwise.

## 3. Major publications by the authors

Unknown for this specific model. The most closely related publication is the one for its stated
ancestor:

- Fhima J, Van Eijgen J, Billen Moulin-Romsée M-I, et al. *LUNet: deep learning for the segmentation
  of arterioles and venules in high resolution fundus images.* Physiological Measurement, 2024. DOI:
  [10.1088/1361-6579/ad3d28](https://doi.org/10.1088/1361-6579/ad3d28)

That paper is about arterioles and venules, not the optic disc, so it does not evidence this model's
performance.

## 4. What it produces

- **Purpose:** `disc/cup`
- **Output classes:** the optic disc. The filename's `odc` suggests disc *and cup*, but PVBM uses
  only the disc, taking the largest contour and fitting a centre and radius; whether a cup channel
  exists in the file was not established.
- **Input grid:** 512×512, square, resized with aspect ratio ignored — so a non-square photograph
  is distorted before the disc is found, and the disc comes back elliptical in proportion to that
  distortion.
- **Output grid:** the disc mask at 512×512, resampled back to the original image size with
  nearest-neighbour interpolation before the centre and radius are fitted.
- **Grid set in:** `self.img_size = 512` in PVBM's `PVBM/DiscSegmenter.py`, with the round trip at
  `img_orig.resize((self.img_size, self.img_size))` and
  `.resize(original_size, PIL.Image.Resampling.NEAREST)`.
- **Input expected:** a colour-fundus photograph, resized to 512 pixels by the caller.
- **Preprocessing in the published code:** resizing and normalisation inside PVBM's
  `DiscSegmenter`, then contour selection and post-processing into zones A, B and C around the disc.

## 5. Architecture

- **Family:** Unknown, beyond the name suggesting a second version of LUNet's U-Net variant.
- **Parameters:** Unknown.
- **Single model or ensemble:** a single ONNX file.

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| Unknown | — | Unknown | No |

No training-data statement was found. This is the practical consequence: **no dataset can be ruled
in or out for benchmarking it**, so any evaluation of this disc segmenter carries an unquantified
risk that the test images were in its training set. For work where disc geometry matters — and in
PVBM every calibre and central-retinal-equivalent measurement depends on it — that is a real
limitation, not a formality.

## 7. Weights

- **Publicly available:** Yes, though not from a versioned source.
- **Download URLs:**
  - https://drive.google.com/uc?id=116EEFBn7qr_LpCBb8GBuyzpa_KGp4xPX — the Google Drive file
    fetched by PVBM, read out of `PVBM/DiscSegmenter.py`.
  - https://github.com/jaburke166/AutoMorphalyzer/releases/download/v1.0_PVBM/lunetv2_odc.onnx —
    a copy republished by AutoMorphalyzer, which at least has a fixed release tag.
- **Format and size:** ONNX, saved locally as `lunetv2_odc.onnx`.
- **Files in an ensemble:** one.

## 8. Performance as reported by the authors

Unknown. No performance figures for this model were found in any publication or repository.

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [PVBM](../projects/pvbm.md) | `DiscSegmenter`, which supplies the disc centre, radius and zones for every geometric biomarker | Downloaded from Google Drive at first use |
| [OCULARNet](../projects/ocularnet.md) | The same segmenter, through its copy of PVBM's code in `utils/DiscSegmenter.py` | As above |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Not wired into the pipeline as far as could be established | Republished as a release asset |

## 10. Known defects

None recorded as of 2026-09-10 — an absence of findings, not a clean bill of health.

## 11. Notes

- **It can change without notice.** An unversioned Google Drive file can be replaced at any time,
  and PVBM caches whatever it downloaded first. Two users running the same PVBM version may
  therefore be running different disc models, and neither could tell. Anyone publishing PVBM
  biomarkers should keep a copy of the file they used, with its checksum.
- **Unknown here is the finding, not a gap to be filled by inference.** The temptation is to assume
  it inherits LUNet's training data; nothing supports that, and the ancestor model performs a
  different task.

---

**Links and license last checked:** 2026-09-10
