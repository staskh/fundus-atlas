# The synthetic biomarker benchmark's notebooks

The [synthetic biomarker benchmark](../../docs/benchmarks/biomarker-synthetic-docs.md) measures
biomarker software on shapes drawn from equations, whose values follow from geometry rather than
from anybody's annotation. Its analysis is split by **lineage**, the unit a reader chooses software
by, beside one notebook that compares the lineages:

| Notebook | What it holds |
| --- | --- |
| [biomarker-synthetic.ipynb](biomarker-synthetic.ipynb) | **The summary.** Every implementation of every group by canonical name, then the three groups compared |
| [biomarker-synthetic-automorph.ipynb](biomarker-synthetic-automorph.ipynb) | AutoMorph and its two rewrites, AutoMorphalyzer and AutoMorphClass, including their cup-to-disc ratios |
| [biomarker-synthetic-pvbm.ipynb](biomarker-synthetic-pvbm.ipynb) | PVBM and OCULAR, which imports PVBM's measuring code |
| [biomarker-synthetic-vascx.ipynb](biomarker-synthetic-vascx.ipynb) | VascX, which shares code with neither |
| [biomarker-synthetic-shapes.ipynb](biomarker-synthetic-shapes.ipynb) | The shapes themselves and the value each one settles: the specification, not an analysis |
| [wip/](wip/) | Readings of one AutoMorph implementation on a few shapes, not of record ([why](../wip/README.md)) |

Each group notebook asks the benchmark's two questions of its members — does a number move when the
same shape is turned, and does it agree with what the geometry requires — and a third that only a
group notebook asks: does each column the catalogue cannot name compute **what its own authors say
it computes**. Each ends with the best and the worst biomarkers of each member.

What came out is written up on one page,
[biomarker-synthetic-results.md](../../docs/benchmarks/biomarker-synthetic-results.md). All of them
read the same evidence through `src/benchmarks/synthetic_evidence.py`, so they cannot disagree
about what an error is.
