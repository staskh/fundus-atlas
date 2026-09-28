# Work in progress

Notebooks that are **not** a benchmark's analysis. Everything in `notebooks/` one level up is: one
notebook per benchmark, holding every subject it measured, compiled into that benchmark's results
page. That rule is in the `analyse-benchmark` skill and these do not change it.

These are the other kind — a focused reading of **one** implementation, or one question somebody
asked once, written to be read rather than to be compiled into anything. Nothing generates them,
nothing links to them from `docs/`, and no test requires them to exist.

## What that means for a reader

- **Nothing here is a finding of record.** A conclusion that survives belongs on the benchmark's
  results page, where it is dated and can be argued with. A conclusion here has not been through
  that.
- **They may be stale.** The benchmark's own notebook is re-executed whenever the evidence changes;
  these are re-executed when somebody remembers. Check the numbers against
  `results/biomarker-synthetic/` before quoting one.
- **They may be deleted.** That is what makes them cheap to write.

## What is here

| Notebook | Asks |
| --- | --- |
| [biomarker-synthetic-automorph.ipynb](biomarker-synthetic-automorph.ipynb) | what AutoMorph returns on `straight`, `arc` and `sinusoid`, under its own column names, at each angle |
| [biomarker-synthetic-automorphalyzer.ipynb](biomarker-synthetic-automorphalyzer.ipynb) | the same of AutoMorphalyzer, whose 54 columns report most quantities once per measurement zone |
| [biomarker-synthetic-automorphclass.ipynb](biomarker-synthetic-automorphclass.ipynb) | the same of AutoMorphClass, read against the ancestor both rewrites share |

The comparison across all six implementations — the one the benchmark exists to make — is in
[../biomarker-synthetic.ipynb](../biomarker-synthetic.ipynb).
