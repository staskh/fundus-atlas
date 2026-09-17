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

**What it is worth:** two datasets state a field angle, which gives an independent scale. On
[PAPILA](../../docs/datasets/papila.md) the two derivations agree to **5.8%**; on
[HRF](../../docs/datasets/hrf.md) they differ by **21%** — under HRF's stated 45° its median disc
would be 1,490 µm rather than the 1,800 µm assumed here, and under the disc figure its field would
span 54°. Treat a figure from this directory as a camera scale good to somewhere between a
twentieth and a fifth, never as a calibration.

Nothing here is a photograph.
