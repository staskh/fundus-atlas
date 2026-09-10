# retipy

retipy processes fundus photographs to segment vessels, detect vessel bifurcations, and compute
tortuosity measures, exposed as a web application: a browser front end, a REST service that stores
images and clinical evaluations, and a Python service that does the image processing. It matters to
this atlas out of proportion to its size, because AutoMorph's biomarker measurements are taken from
retipy's code.

It has not been updated since May 2019.

## 1. Code reference

- **Repository:** https://github.com/alevalv/retipy — a meta-repository that assembles the whole
  application with Docker Compose. The parts live separately:
  - Image processing: https://github.com/alevalv/retipy-python
  - REST service: https://github.com/alevalv/retipy-rest
  - Web front end: https://github.com/alevalv/retipy-react
- **Version described here:** commit `8b4f73b9` (2019-05-05) of the meta-repository. No tags or
  releases are published.
- **Most recent commit:** 2019-05
- **Language and how it runs:** Python with OpenCV for the processing service, Kotlin for the REST
  layer, TypeScript for the front end. `docker-compose up --build` starts a local instance.
- **Training code included:** Not applicable — no trained model is used, so there is nothing to
  train.

## 2. License

- **Code:** GNU General Public License v3.0 or later, stated in the README of the meta-repository
  and reported for `retipy-python` as well. GPL-3.0 is a copyleft license; combining this code with
  differently licensed code has consequences, which is worth noting given that AutoMorph
  (Apache-2.0) uses it for feature measurement.
- **Model weights:** Not applicable — no distributed trained weights were found.

## 3. Major publications by the authors

Unknown. No publication by the project's authors describing retipy was established at the time of
checking. Cite the repository itself, and cite the original sources of any measure you use.

## 4. Segmentation models used

| Model | Segments | Origin |
| --- | --- | --- |
| retipy vessel segmentation | Blood vessels | Introduced here |

The method used is documented as classical image processing with OpenCV rather than a trained
network; the exact algorithm was not established from the repository at the time of checking. No
artery/vein separation and no optic disc segmentation were found.

## 5. Models introduced here

### 5.1 retipy vessel segmentation

- **Training data:** Not applicable — no trained model was found; the processing is algorithmic.
- **Weights publicly available:** Not applicable.
- **Download URL:** Not applicable.
- **Training code:** Not applicable.

## 6. Biomarkers computed

| Biomarker | Defined in | Original implementation | This project's version |
| --- | --- | --- | --- |
| Tortuosity measures (several) | Prior literature; the specific definitions were not established at the time of checking | This project | Implemented here |
| Vessel bifurcation detection | Prior literature | This project | Implemented here |

These implementations have downstream reach: AutoMorph's README names retipy as its
feature-measurement component, so AutoMorph's tortuosity, calibre and fractal-dimension columns
descend from this code. A shared implementation means two pipelines agreeing on a number is weaker
evidence than it looks.

## 7. Examples and notebooks

- `docker-compose up --build` in the meta-repository — start here; it brings up the full
  application, which ships with a demo login (`alevalv` / `mypassword`). The authors note the
  default deployment has no persistence, so processed data is lost on restart.

## 8. Notes

- Dormant since 2019 and built on 2019-era dependencies. Expect installation friction, and treat it
  as a reference implementation to read rather than software to deploy.
- The demo credentials above are published in the project's own README. Do not expose an instance
  configured that way to a network, and never load patient images into one.

---

**Links and license last checked:** 2026-09-10
