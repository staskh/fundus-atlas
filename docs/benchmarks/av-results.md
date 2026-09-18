# Artery and vein benchmark — results

**Nothing has been measured yet.** The benchmark is configured and its models are built — five of
the six declared can be run — but no model has been scored on any photograph, so this page holds no
numbers. How it is configured, and what it will measure, is
[av-docs.md](av-docs.md).

This page exists rather than being absent because the configuration page links to it, and because a
page that says "not yet" is better than a link that goes nowhere. It will be written from
[notebooks/av.ipynb](../../notebooks/av.ipynb) once there is something to read, and the sections it
will carry are set out in `.claude/skills/report-benchmark/av.md`.

## 1. What is ready

| | |
| --- | --- |
| Datasets built | [HRF](../datasets/hrf.md) 45 · [Fundus-AVSeg](../datasets/fundus-avseg.md) 100 · [AVRDB](../datasets/avrdb.md) 100 · [REYIA](../datasets/reyia.md) 559 — **804 photographs** |
| Models with adapters | [vascx-artery-vein](../models/vascx-artery-vein.md) · [ocularnet](../models/ocularnet.md) · [lunet](../models/lunet.md) · [automorph-artery-vein](../models/automorph-artery-vein.md) · [bf-net](../models/bf-net.md) |
| Models declared and unrunnable | [ocularnet-nano](../models/ocularnet-nano.md), whose weights are withdrawn |
| Datasets declared and unbuilt | [RAV](../datasets/rav.md) · [LES-AV](../datasets/les-av.md) · [RITE](../datasets/rite.md) |
| Metrics | Dice and clDice, over arteries, veins and the vessels they make together |

## 2. What is not ready

The run itself: `src/benchmarks/av.py` declares the benchmark and generates this page's companion,
and the scoring loop that writes `results/av/` is not written yet.

---

**Measured by** `python -m benchmarks --benchmark av` · nothing recorded as of 2026-09-18
