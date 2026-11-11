# Reporting the real-segmentation biomarker benchmark

Load this beside `SKILL.md` before writing `docs/benchmarks/biomarker-real-results.md`.

- **The summary table** is one row per segmentation model, with the headline panel's ICC(A,1) and
  SNR as the reference implementation computes them, pooled on photographs. It says that it is
  pooled and from which implementation.
- **The detail** gives every model × dataset for the panel, then the families, then the
  implementations side by side on the panel.
- **The recommendation is per question.** Which model to use for calibre (CRAE, CRVE, AVR) is a
  different question from which to use for fractal dimension or tortuosity, and the answer differs.
  Name the runner-up and the margin, the contamination mark, and the seconds per photograph from
  the artery/vein benchmark, since that is where the model's own cost is.
- **Never call a biomarker "validated".** Agreement with one expert's map is agreement with one
  reference. The page says, every time it recommends, that no second reader exists to say where
  the ceiling is.
