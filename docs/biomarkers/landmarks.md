# landmarks

**The optic nerve head and the fovea.** The only family here that is not a measurement of blood
vessels — these describe the anatomy the vessels are arranged around, and are catalogued because
several vascular biomarkers are defined relative to them and cannot be read without them.

## 1. What it measures

The optic cup widens within the disc as glaucoma progresses, which makes the ratio between them the
most widely used structural measure in glaucoma screening. The distance between the disc and the
fovea is not a disease marker at all: it is a **per-eye ruler**, used to place measurement regions
and to normalise lengths on photographs whose scale is unknown.

**Centring** describes the photograph rather than the eye: whether it was aimed at the optic disc
or at the macula. It is catalogued because which other biomarkers a photograph can support — a
zone around the disc, a region around the fovea — depends on it.

## 2. The canonical names

| Name | What it is | Statistic |
| --- | --- | --- |
| `landmarks/CDR-vertical` | the cup's vertical diameter over the disc's | none |
| `landmarks/CDR-horizontal` | the cup's horizontal diameter over the disc's | none |
| `landmarks/CDR-area` | the cup's area over the disc's | none |
| `landmarks/disc-diameter-vertical` | the disc's vertical diameter, in µm | none |
| `landmarks/disc-diameter-horizontal` | the disc's horizontal diameter, in µm | none |
| `landmarks/cup-diameter-vertical` | the cup's vertical diameter, in µm | none |
| `landmarks/cup-diameter-horizontal` | the cup's horizontal diameter, in µm | none |
| `landmarks/disc-fovea-distance` | the straight-line distance between the disc centre and the fovea | none |
| `landmarks/centring` | what the photograph is centred on: `disc`, `macula` or `unknown` | none |

**`landmarks/centring` is the one name in the vocabulary whose answer is a category rather than a
number.** Its unit is `category`, its record lists the three answers it may take, and nothing
converts or averages it.

**This family has no `structure` part.** An optic disc is not an artery or a vein, so the name stops
after the biomarker — `landmarks/CDR-vertical` is a complete name. That is the family override
described in `PLAN-BIOMARKER.md` §2.1.1.

## 3. Definitions of record

- **Cup-to-disc ratio:** a clinical measurement that predates automated analysis, so there is **no
  defining paper** and the entry carries a detailed description instead. Divide a measure of the cup
  by the same measure of the disc — the vertical diameter for the vertical ratio, the horizontal
  diameter for the horizontal one, the areas for the area ratio. They are **not interchangeable**:
  a cup that is wide but shallow gives a large area ratio and a modest vertical one, and the disc is
  a vertical oval, so its horizontal diameter is the shorter.
- **Disc and cup diameters:** the sizes the vertical and horizontal ratios are made of, with no
  defining paper. *Vertical* and *horizontal* follow the photograph's rows and columns, as the
  ratios do, so a cup turned with the photograph changes them while a round disc does not. Unlike
  the ratios, they carry a length and depend on the camera's scale. *Added 2026-11-22*, because all
  three of the AutoMorph family return them beside the ratios, each as the height and width of a
  mask's bounding box.
- **Disc–fovea distance:** [Vargas 2026](../papers/vargas-2026.md). The straight-line distance
  between the centre of the segmented optic disc and the detected fovea.
- **Centring** has **no defining paper**. `disc` where the optic disc sits close to the centre of
  the frame, `macula` where it sits off to one side, and `unknown` where no plausible disc was
  found. How close counts as centred is the implementation's choice, and is recorded on its
  project page where it can be.

## 4. Inputs required

Disc and cup segmentations for the ratios; disc and fovea for the distance; the disc's position in
the frame for the centring. No vessel mask is used by anything on this page.

## 5. Measurement region

**Not applicable.** These are defined relative to landmarks rather than over an area, so the region
part does not apply and a name carrying one is an error.

## 6. Units and scale dependence

The three ratios are dimensionless and **scale-invariant** — they are the most robust numbers in this
catalogue for that reason, needing neither a scale nor a field of view.

The disc–fovea distance is a **length, in microns**. It is also the one biomarker whose relationship
to scale is circular in the common case: where a dataset publishes no microns-per-pixel figure, one
is inferred by assuming the disc is 1800 µm across — so a disc–fovea distance derived from that
scale is anchored to an assumption about the disc. It is reported, and the assumption is recorded
beside it.

The centring is a **category**, with no unit and no scale; it depends only on where the disc sits in
the frame.

## 7. Implementations

| Project | What it computes | Source | Lineage |
| --- | --- | --- | --- |
| [VascX](../projects/vascx.md) | disc–fovea distance, in two variants — to the retina's centre and to the fovea | `vascx/fundus/features/` | Original |
| [AutoMorph](../projects/automorph.md) | the vertical and horizontal cup-to-disc ratios and the four diameters behind them | `M2_lwnet_disc_cup/generate_av_results.py`, `optic_disc_centre` | Original |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | the same six, and the centring, as `macular_centred` | `automorph/measure/measure.py`, `get_disc_metrics` | AutoMorph |
| [AutoMorphClass](../projects/automorphclass.md) | the same six | `pytorch_automorph/feature_calculation.py`, `Optic_Disc_Cup_Features` | AutoMorph |
| [fundus-biomarkers](../projects/fundus-biomarkers.md) | the three cup-to-disc ratios, from disc and cup masks, and the centring, from the disc circle | private repository | Original |
| Others | **none** | — | — |

The three AutoMorph implementations share one recipe — bounding boxes of the disc and cup masks,
an extent being the last lit index minus the first — so their agreement is not independent
evidence. *Since 2026-11-22* the synthetic benchmark hands every adapter a cup, and measures all
three; fundus-biomarkers is no longer run by it. Several catalogued **models** segment the cup —
see [MODELS.md](../MODELS.md).

## 8. Sensitivity and failure modes

- **The cup boundary is the hard part.** Readers disagree about it far more than about the disc, so
  a cup-to-disc ratio inherits that disagreement. Datasets with several readers —
  [RIGA](../datasets/riga.md) with six ophthalmologists, [Chákṣu](../datasets/chaksu.md) — are the
  only way to measure it rather than assume it.
- **A displaced disc moves everything anchored to it**, including the equivalents' rings on the
  [calibre](calibre.md) page.
- **Fovea detection fails on poor-quality photographs** with no distinct macular darkening, and a
  wrong fovea gives a confidently wrong distance.

## 9. Known defects

None recorded as of 2026-11-22 — an absence of findings rather than a clean bill of health.

*Our measurement, 2026-11-22:* since the synthetic shapes gained an optic cup, the
[synthetic benchmark](../benchmarks/biomarker-synthetic-results.md) §3.2 has measured the AutoMorph
family's ratios, diameters and centring. The vertical and horizontal ratios land within 1.9%, the
disc's diameters within 1.3% and the cup's within 2.4%, for all three implementations at every
angle; AutoMorphalyzer's centring is right on all 91 renderings. A drawn ellipse with a hard rim is
the easiest cup there is, so this says the arithmetic is right and nothing about a real cup's
boundary. Nothing here has been measured for the area ratio or the disc–fovea distance.

---

**Links and definitions last checked:** 2026-11-22.
