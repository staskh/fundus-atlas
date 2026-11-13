# Reporting the real-segmentation biomarker benchmark

Load this beside `SKILL.md` before writing `docs/benchmarks/biomarker-real-results.md`.

- **Each project is read on its own model only** (`biomarker_real.NATIVE`; configuration page
  §2.3), and **the project is the primary index, the dataset the secondary** — overriding
  `SKILL.md` §4's model-first rule for this benchmark. PVBM, which ships no model, and the maps of
  models no project ships (LUNet, BF-Net) are named as not read, in the first paragraph.
- **The summary table** is one row per project, naming its model, with the headline panel's
  ICC(A,1) and SNR as that project computes it (`biomarker_real.panel_for`), pooled on photographs.
  A dash is a biomarker the project does not compute, and a stand-in summary — a mean where the
  panel asks for a median — is marked in the cell.
- **The detail** gives every project × dataset for the panel, then the families, then the programs
  that share one model side by side.
- **The recommendation is per question.** Which project to use for calibre (CRAE, CRVE, AVR) is a
  different question from which to use for fractal dimension or tortuosity, and the answer differs.
  Name the runner-up and the margin, the contamination mark, and both costs: the program's seconds
  per map and its model's seconds per photograph from the artery/vein benchmark. **Say which
  projects a reader cannot obtain** — fundus-biomarkers is private — and answer for the public ones
  as well.
- **Never call a biomarker "validated".** Agreement with one expert's map is agreement with one
  reference. The page says, every time it recommends, that no second reader exists to say where
  the ceiling is.
