# Inferred camera scales

One JSON per dataset, written by `python -m datasets.fetch_um_resolution` and committed. Most
datasets publish no microns-per-pixel figure; these files are the evidence for the camera-level
scale inferred from the typical optic disc (about 1.8 mm) when they do not.

The grouping, the sample, the disc model, the spread gate, and the schema are the
`fetch-um-resolution` skill.

**This is the measurement; the manifest carries a copy.** A store's `um_per_px` is stamped from the
accepted group here, with `resolution_source` set to `disc_anchored`, so a consumer reads one file
rather than joining two — and a rebuilt store recovers the figure without measuring anything again.
A published or field-angle figure is never overwritten.

**What it is worth:** on [PAPILA](../../docs/datasets/papila.md), the one dataset here whose stated
field angle gives an independent scale, the two derivations agree to **8.7%** — its median disc
measures 1,656 µm under the field-angle scale, against the 1,800 µm assumed here. Treat a figure
from this directory as a camera scale good to roughly a tenth, not a calibration.

Nothing here is a photograph.
