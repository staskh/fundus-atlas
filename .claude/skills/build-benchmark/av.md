# The artery/vein benchmark

Load this beside `SKILL.md` before building or changing `src/benchmarks/av.py`. Everything here is
particular to arteries and veins; everything shared is in the main file.

**What it asks:** how close a model's arteries, veins, and the vessels they make together are to
what an expert drew on the same photograph.

```
python -m benchmarks --benchmark av
python -m benchmarks --benchmark av --model ocularnet --dataset hrf
python -m benchmarks --benchmark av --max-samples 20
```

## 1. Segmentation only

This benchmark scores **three binary maps and nothing else**: `artery`, `vein`, and `vessels`. It
does not compute a calibre, a CRAE, an arteriovenous ratio, a tortuosity or a fractal dimension.
Those are biomarkers — numbers derived from a mask by a further method that can be right or wrong on
its own terms — and they get their own benchmark, measured from the masks this one keeps (section
6). Mixing the two would make a model's segmentation and a pipeline's arithmetic indistinguishable
in one number.

**`vessels` is derived, not predicted.** It is the union of the model's own artery and vein masks. A
model that finds both has said where the vessels are, and scoring that union separates two kinds of
mistake: getting the network right and the classification wrong looks very different from missing
the vessel altogether. Where a model emits a vessel map of its own as well, that is **not** what
this column holds — the union is, so that every model is compared on the same derivation.

### 1.1 The one exception: a vessel-only reference

A model that does not separate arteries from veins has no union to take, so **its own vessel map is
its answer**. That breaks the guarantee above, and the break is the point: a vessel segmenter is
carried here as a **reference for the vessel column** — what a model built for that one job achieves
on these photographs — and never as an entry in the artery/vein ones.

Four rules keep it from being read as a competitor:

- **Its artery and vein cells are empty, never zero.** Empty says it was not asked; zero would say
  it answered and was wrong.
- **Every page carrying its vessel score says the column is not derived the same way for it.** A
  reader comparing 0.86 against 0.86 is comparing a prediction with a union.
- **It is declared in `MODELS` like any other model** and its adapter declares
  `structures = ("vessels",)`. Nothing else in the run knows it is peculiar.
- **A threshold this repository chose rather than inherited is declared as a number** and named on
  both generated pages beside the upstream's own. `segan-vessel` runs at 0.2 where AutoMorph ships
  0.5, so every score recorded for it is a score of the model at 0.2 and not of the model as its
  authors run it.

The same rule holds from the other side: a dataset that annotates vessels and neither class is
scored on the vessel column alone, for every model, and its class cells are empty for all of them.

## 2. Two scores, because neither is enough

| Metric | What it says |
| --- | --- |
| **Dice** | how much of the annotated area the model found, 0 to 1 — the familiar number |
| **clDice** | how much of each network's **centreline** falls inside the other, as a harmonic mean of the two directions |

They separate two failures that Dice alone confuses, and the difference is not small:

- a vessel drawn three times too wide around the same centre scores **0.50 Dice and 0.97 clDice** —
  wrong about width, right about the network;
- the same vessel thickened to one side scores **0.50 Dice and 0.03 clDice** — the same overlap, and
  its centreline no longer inside the expert's vessel at all.

A gap in a vessel costs both alike, which is worth knowing: clDice is often assumed to punish a
break harder, and it does not. Report both, always, and say which of the two a conclusion rests on.

clDice is `benchmarks/metrics/av.py`, after Shit et al., CVPR 2021.

## 3. Score in the annotation's own frame, and keep what was drawn

The same two rules as the disc benchmark, for the same reasons:

- **Everything is measured at native resolution**, in the store's `native/` frame. A model working
  at 512 or 1024 has its output carried back there first — probabilities resampled and thresholded
  **after** arrival, never a binary mask resampled — and the path taken is recorded per photograph.
- **The predicted masks are kept** under `.atlas_runs/av/<model>/<dataset>/`, as three files per
  photograph: `<key>-artery.png`, `<key>-vein.png`, `<key>-vessels.png`. The biomarker benchmark's
  input is exactly these, and a mask whose fingerprint no longer matches its model is drawn again
  rather than read.

## 4. What the ground truth is, and what it is not

The store holds `artery`, `vein` and `vessels` at native resolution, per the `fetch-dataset` skill's
section 12. Three things follow that this benchmark must not get wrong:

- **A crossing is in both masks.** Where an artery passes over a vein, the pixel is annotated as
  both, so a model that calls it either is right. Scoring against a ground truth that withheld those
  pixels from one class would count a correct answer as a false positive.
- **A vessel the annotator could not classify is in `vessels` and in neither of the others.** It is
  not evidence about artery or vein, and a model is neither rewarded nor punished for what it says
  there.
- **A derived vessel mask is not independent evidence.** In three of the datasets built here the
  vessel annotation *is* the artery/vein annotation — HRF's hand-drawn gold standard and the union
  of HRF-AV's maps differ by 0.004% of pixels, and Fundus-AVSeg and AVRDB derive theirs outright. So
  a model's vessel score and its artery/vein scores are **one measurement seen twice**, not two
  agreeing measurements, and the results page says so wherever both appear.

## 5. Which photographs are excluded

The common rules of `SKILL.md` section 2, plus:

- **No vessel annotation at all** — a photograph the dataset published with neither the two classes
  nor a vessel tracing, so there is nothing any model here could be scored against. Not a failure of
  the model, and never counted as one. A photograph carrying a vessel tracing and no classes is
  **not** excluded: it is scored on the vessel column and left out of the class ones (section 1.1).
- **An annotation a finding condemns**, from `src/datasets/exclusions/`. REYIA has four photographs
  whose two published encodings of the same annotation contradict each other; they are excluded per
  map rather than whole.
- **Excluded whole** — a dataset whose images are crops rather than photographs.

## 6. What is kept

Per photograph, per reader: the three Dice scores, the three clDice scores, the outcome, the
resampling path, and the counts of what each mask holds — the model's and the reader's — so that a
score can be read beside the size of the thing being scored.

Nothing derived from a mask beyond that. A width, a ratio or a tortuosity computed here would be a
biomarker measured inside a segmentation benchmark, and it belongs in the biomarker one, taking
these kept masks as its input.

## 7. Where the code goes

- `src/benchmarks/av.py` — the run.
- **`src/benchmarks/metrics/av.py` — Dice and clDice, and nothing else.** Pure functions over two
  masks: no model, no store, no file. That is what lets the same functions be tested against shapes
  whose answer is arithmetic.
- `src/benchmarks/loaders/av.py` — `ArteryVeinLoader`, yielding the photograph and the three masks
  in the native frame.
- `src/models/<slug>.py` — one adapter per catalogued model, as always.
