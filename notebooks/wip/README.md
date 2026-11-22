# Work in progress

Notebooks that are **not** a benchmark's analysis. Everything in `notebooks/` one level up is: one
notebook per benchmark, holding every subject it measured, compiled into that benchmark's results
page. That rule is in the `analyse-benchmark` skill and these do not change it.

These are the other kind — a focused reading of **one** implementation, or one question somebody
asked once, written to be read rather than to be compiled into anything. Nothing generates them,
no test requires them to exist, and the one link from `docs/` — in
[calibre.md](../../docs/biomarkers/calibre.md) §9 — points at a finding they show rather than at a
result of record.

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
| [vascx-features-on-photographs.ipynb](vascx-features-on-photographs.ipynb) | what VascX's features read on a few photographs, from the expert's artery/vein map and from VascX's own |
| [vascx-tracing-one-artery.ipynb](vascx-tracing-one-artery.ipynb) | how VascX traces one artery of one HRF photograph, stage by stage, through its own objects |

The synthetic biomarker benchmark's notebooks, including its three work-in-progress readings of
one AutoMorph implementation each, are in [../synthetic/](../synthetic/README.md).
