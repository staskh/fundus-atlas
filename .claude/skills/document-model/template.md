# <Model name>

One paragraph, plain language: what this model is given, what it returns, and what it was built for.
Say in a sentence why it exists — what it does differently from the models that came before it.

## 1. Code reference

- **Repository:** <URL>
- **Version described here:** <commit / tag / release>
- **Most recent commit:** <YYYY-MM>
- **Training code included:** <Yes, in this repository / Yes, in <other repository> / No — inference only>
- **Language and how it runs:** <framework, entry point command, GPU expectations>

## 2. License

- **Code:** <license as stated by the project>
- **Model weights:** <license, if stated separately; otherwise `Same as code` or `Unknown`>

## 3. Major publications by the authors

- <Full citation.> DOI: <link>

## 4. What it produces

- **Purpose:** <quality | vessels | artery/vein | disc/cup | other>
- **Output classes:** <exactly as emitted, e.g. background, artery, vein, crossings>
- **Input expected:** <resolution; cropped to field of view or not; disc-centred or macula-centred; colour space>
- **Preprocessing in the published code:** <what the inference script does to an image before the model sees it>

## 5. Architecture

- **Family:** <U-Net / W-Net / GAN-based / encoder backbone>
- **Parameters:** <count, if stated; otherwise Unknown>
- **Single model or ensemble:** <one model, or ensemble of N and how they are combined>

## 6. Training data

| Dataset | Role | Annotations by | Split stated |
| --- | --- | --- | --- |
| <name> | Training / validation / test | <who annotated> | <Yes: … / Unclear> |

<A sentence naming which datasets are therefore unavailable for a fair benchmark of this model.>

## 7. Weights

- **Publicly available:** <Yes / No / Unknown>
- **Download URL:** <full URL per file or model page>
- **Format and size:** <e.g. PyTorch .pth, 35 MB per seed; ONNX>
- **Files in an ensemble:** <how many, and their names>

## 8. Performance as reported by the authors

| Dataset | Metric | Value | Reported in |
| --- | --- | --- | --- |
| <name> | <e.g. Dice> | <value> | <paper of section 3> |

<These are the authors' measurements on their own test sets. This atlas's own comparisons are
separate.>

## 9. Used by

| Project | How it is used | Weights |
| --- | --- | --- |
| [<project>](../projects/<slug>.md) | <which stage> | Published weights / retrained by that project |

## 10. Known defects

<One subsection or bullet per defect: what is wrong, which outputs it affects, the upstream issue or
commit documenting it, and its status (open / fixed in <version> / fixed by <project>, unverified).
If nothing is known, write `None recorded as of <YYYY-MM-DD>.` — an absence of findings, not a clean
bill of health.>

## 11. Notes

Anything a reader needs in order not to be misled: image types it expects, known failure modes the
authors state, domain shift between cameras, licensing traps.

---

**Links and license last checked:** <YYYY-MM-DD>
