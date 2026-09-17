# Inferred camera scales

One JSON per dataset, written by `python -m datasets.fetch_um_resolution` and committed. Most
datasets publish no microns-per-pixel figure; these files are the evidence for the camera-level
scale inferred from the typical optic disc (about 1.8 mm) when they do not.

The grouping, the sample, the disc model, the spread gate, and the schema are the
`fetch-um-resolution` skill. A biomarker uses a figure from here only when the dataset published
no scale of its own.

Nothing here is a photograph.
