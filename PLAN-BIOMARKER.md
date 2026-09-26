# Biomarkers: the plan

What we decided and why, before any of it is built. Sections marked **Decided** are settled;
**Open** needs Stas's call. Nothing here is code.

This is the standing plan for **the biomarkers themselves** — what they are called, what defines
them, and what makes two of them comparable. It is separate from
[PLAN-BENCHMARK.md](PLAN-BENCHMARK.md), which is about what gets measured against what: a benchmark
consumes this vocabulary and does not decide it.

The vocabulary in `src/biomarkers/canonical.py` is what lets two pipelines' columns be read against
each other. It was written to get the first biomarker benchmark running, and it did. This plan is
about the two things it cannot currently do:

1. **Name what implementations actually supply.** 73 columns across six implementations have no
   canonical name, and they are not exotic measurements — 60% of them are quantities the vocabulary
   already names, measured over a region it has no way to express.
2. **Survive a change of camera.** 30 of the 70 names the synthetic shapes settle **change value
   when the same eye is photographed at a different resolution**. A table pooling two datasets is
   currently adding pixels to pixels of a different size.

## 1. What exists today

**Fact, measured 2026-09-25.**

| | |
| --- | --- |
| Name shape | `biomarker/variant/structure`, three axes |
| Templates | 32, expanding to **90 names** over artery / vein / vessels |
| Claimed by at least one implementation | **37** |
| Claimed by none | **53** |
| Settled by a synthetic shape | 70 |
| Biomarker pages | 15 |
| Papers catalogued | 11 |

`canonical.py` carries, per name, **one sentence of prose and nothing else**. Not the units, not
the region, not the paper, not the formula. `docs/BIOMARKERS.md` carries a Units column and a
Defined in column, but nothing connects the two, so neither can check the other.

## 2. Gap A — the vocabulary has three axes and the measurements have five

**Fact.** Every unmapped column, by why it is unmapped:

| Count | Cause | Example |
| --- | --- | --- |
| **44** | **A region axis that does not exist** | `average_local_calibre@whole_binary`, `vd_crcl_multiplier_1p16666666667_full_arteries` |
| **15** | **A statistic axis that does not exist** | `mean_branching_angle_artery`, `pooled_tortuosity_artery` |
| 6 | Genuinely new quantity | `perimeter_artery`, `singularity_length_artery`, `start_points_artery` |
| 6 | Mapping withdrawn as wrong | `squared_curvature_tortuosity_*` — it squares nothing |
| 2 | Family exists as a page but not as a name | `disc_fovea_distance_retina` |

**Only six of seventy-three are measurements the catalogue has never heard of.** The rest are
things it already names, qualified along axes it cannot express:

- **Region.** AutoMorphalyzer reports every calibre and tortuosity measure three times — zone B,
  zone C, and whole image. VascX reports several over a disc-centred circle at 7/6 disc radii and
  over the "full" retina. Zone B and zone C are *the* conventional measurement annuli from the
  ARIC/Knudtson literature, so this is not an implementation quirk; it is the field's standard
  practice, and the vocabulary cannot say it.
- **Statistic.** PVBM reports the mean, median *and* standard deviation of its branching angle.
  OCULAR reports a pooled and a length-weighted tortuosity. Each is a different summary of the same
  per-segment quantity, and `bifurcation-angle/between-daughters/artery` can only name one of them.
- **Parameter.** Four VascX columns additionally carry `max_segment_len_0p15` / `0p25` — the same
  measure at two settings. A name with no parameter slot silently merges them.

## 3. Gap B — 30 of 70 names are expressed in pixels

**Fact, measured.** The same physical retina was built at 1024 px / 10 µm per pixel and at
2048 px / 5 µm per pixel — one eye, two cameras — and every theoretical value compared:

| Behaviour | Count | Names |
| --- | --- | --- |
| **Scale-free** (×1) | **40** | τ1, τ2, Grisan density, inflection count, all fractal dimensions, all junction counts, densities, AVR, bifurcation angle, **Hubbard** equivalents |
| **Length in pixels** (×2) | **15** | calibre mean and median, skeleton length, sparsity mean and max, **Knudtson** equivalents |
| **Inverse length** (×0.5) | **8** | τ3, τ4, τ6, spline mean curvature |
| **Inverse area** (×0.25) | **4** | τ5, τ7 |
| **Area in pixels²** (×4) | **3** | vessel area |

**Thirty names out of seventy give a different answer for the same eye.** They are not wrong — a
length measured in pixels is a real measurement — but nothing in the name, and nothing in the
stored evidence, says which unit a column is in. Two datasets at different resolutions cannot be
pooled, and nothing currently stops someone doing it.

### 3.1 Why the tortuosity family splits three ways

Curvature κ is one over the radius of curvature, so it carries units **1/L**; the arc element `ds`
carries **L**. Every one of Hart's seven is built from two integrals, and the dimensions follow
mechanically:

| | Formula | Dimensions | Units | Measured ratio at 2× resolution |
| --- | --- | --- | --- | --- |
| τ1 | arc / chord | L / L | **1** | ×1.000 |
| τ2 | ∫κ ds | (1/L)·L | **1** | ×1.000 |
| τ3 | ∫κ² ds | (1/L²)·L | **1/L** | ×0.500 |
| τ4 | ∫κ ds / s | 1 / L | **1/L** | ×0.500 |
| τ5 | ∫κ² ds / s | (1/L) / L | **1/L²** | ×0.250 |
| τ6 | ∫κ ds / chord | 1 / L | **1/L** | ×0.500 |
| τ7 | ∫κ² ds / chord | (1/L) / L | **1/L²** | ×0.250 |

- **τ2 is dimensionless because the single κ cancels exactly against ds.** It is the total turning
  angle in radians — the 90° arc gives 1.5708 = π/2, which is the check that the derivation is
  right rather than merely plausible.
- **τ3 is 1/L because the square leaves one κ uncancelled.** It is the elastic bending energy.
- **τ4 and τ6 are τ2 divided by a length**, so a pure number over a length: 1/L. τ4 divides by arc
  length and τ6 by the chord, which makes them different numbers of the same dimension.
- **τ5 and τ7 are τ3 divided by a length again**, so 1/L².

τ4 is the case worth holding on to: for a circular arc of radius R subtending θ, `s = Rθ`, so
`τ4 = θ/(Rθ) = 1/R`. **τ4 is literally the curvature.** Its unit is an inverse length because that
is what the quantity is, not because of anything Hart did — which is an argument for converting it
to physical units rather than for dropping it.

### 3.2 Physical units are necessary and not sufficient

**Fact, measured.** The obvious fix for section 3 is to report lengths in microns. It is required,
and on its own it does almost nothing. The same arc was drawn at four grids covering one physical
retina, every value converted to microns before comparison:

| | τ1 | τ2 *(already dimensionless)* | τ3 | τ4 | τ5 |
| --- | --- | --- | --- | --- | --- |
| Spread across grids, curvature from adjacent pixels | 1.1% | **145%** | **241%** | **145%** | **241%** |
| Spread, curvature estimated over a fixed **150 µm** window | 0.8% | **12%** | **16%** | **12%** | **17%** |

**τ2 is the proof that this is not a units problem.** It is dimensionless, there is nothing to
convert, and it still moves by 145%. What moves it is that a skeleton is a staircase: curvature
estimated from adjacent pixels is about 1/h for a pixel of size h, so τ2 grows like 1/h and τ3 like
1/h². Halving the pixel doubles τ2 and quadruples τ3, which is what the measurement shows.

**The 150 µm window in that table is consistent and wrong**, which is worth dwelling on. Measured
against the arc's exact curvature — for a circular arc τ4 is exactly 1/R, so there is a right
answer — a 150 µm window overestimates by **79%, 72% and 81%** at the three grids. It agrees with
itself to about 11% and is three-quarters too large everywhere. **Agreement across resolutions is
not accuracy**, and a normalisation validated only by consistency would have shipped this.

So a curvature-family number is comparable only when **both** hold: the unit is physical, *and* the
curvature was estimated over a declared physical scale. An implementation smoothing over 50 µm and
one smoothing over 500 µm are not comparable however carefully either reports its units.

The implementations already know this and the vocabulary does not: VascX emits
`lw_tort_dist_max_segment_len_0p15…` and `…0p25`, the same tortuosity at two segment lengths. That
parameter *is* the estimation scale.

**The residual matters too.** A fixed physical window takes the spread from 241% to 16%, not to
zero, and the coarsest grid is the worst of the four. That is enough to make these numbers arguable
and not enough to call them interchangeable, and the plan should not pretend otherwise.

### 3.3 How long the window should be

**Fact, measured against the exact answer.** Sweeping the window from 40 µm to 3 mm on the arc,
whose true curvature is known, and recording the band of windows that land within a tolerance:

| Shape | Its radius of curvature | Grid | Within 1% | Within 5% |
| --- | --- | --- | --- | --- |
| `arc` | 2253 µm | 1024 px, h=10 µm | 522–1251 µm | 443–1557 µm |
| | | 2048 px, h=5 µm | 615–1251 µm | 494–1557 µm |
| | | 4096 px, h=2.5 µm | 686–1396 µm | 494–1557 µm |
| `sinusoid` | 597 µm | 1024 px | 765 µm only | 724–808 µm |
| | | 2048 px | **nothing qualifies** | 724–808 µm |
| | | 4096 px | **nothing qualifies** | 724–854 µm |

Four things follow, and the first is the one the plan needs:

- **The right window does not depend on the resolution.** The three bands for the arc are nearly
  the same physical length — 522–1251, 615–1251, 686–1396 µm — over a sixteenfold change in pixel
  area. *One physical window serves every grid*, which is exactly the property a normalisation
  needs and is not something to take on faith.
- **It depends strongly on the curvature being measured.** In units of the curve's own radius the
  arc wants 0.23R–0.56R and the sinusoid 1.21R–1.43R. There is no universal fraction-of-radius
  rule, and a single number cannot be right for every vessel in an image.
- **There is a plateau, not an optimum.** Anywhere from about 600 to 1200 µm puts the arc within
  1%, and the best window inside that range moves around — 762, 594, 1061 µm at the three grids —
  because within the plateau the error is dominated by fluctuation rather than by the window. So
  the useful output of this experiment is a **range**, and the useful instruction is *stay off the
  short end*: below 300 µm the error runs from 16% to 350%.
- **For a curve whose curvature varies, no window may be right at all.** The sinusoid cannot be
  brought within 1% at 2048 or 4096 px by any window. The band that works at 5% works because two
  errors cancel, not because the estimate is good, which is why it is narrow and why it fails as
  the pixels get finer.

Two practical consequences for retinal vessels, neither yet measured here and both worth being
explicit about before any number is written into code:

- A window of 600–1200 µm is a **large fraction of a real vessel segment**. Segments between
  branch points are often shorter than that, so the window cannot be applied to them at all —
  which is very likely why VascX parameterises `max_segment_len` rather than fixing it.
- The values above come from two synthetic curves of known curvature, not from retinal vasculature.
  **They fix the method, not the number.** What window suits real arterioles has to be measured on
  real arterioles, and this plan should not pretend otherwise.

### 3.4 At a 10% tolerance there is no common window, and that is the finding

**Fact, measured.** 3.3 asked how long the window should be for one metric. Asking it for **all
seven at once**, against their theoretical values, on `straight`, `arc` and `sinusoid` at 1024,
2048 and 4096 px — 45 (shape, grid, metric) cases with a non-zero theoretical value — gives a
different answer: there is no such window.

Each metric alone, at its best window, worst case over every shape and grid:

| Metric | Units | Best achievable | At window | Reaches 10% at |
| --- | --- | --- | --- | --- |
| τ1 | 1 | **0.4%** | 40 µm | 40–549 µm |
| τ2 | 1 | **5.0%** | 338 µm | 307–431 µm |
| τ6 | 1/L | **1.9%** | 577 µm | 391–700 µm |
| τ4 | 1/L | **1.4%** | 771 µm | 667–892 µm |
| τ3 | 1/L | 25.3% | 498 µm | **never** |
| τ7 | 1/L² | 23.2% | 635 µm | **never** |
| τ5 | 1/L² | 22.3% | 667 µm | **never** |

And the best compromise window for each group:

| Group | Best worst-case | At | Common 10% window |
| --- | --- | --- | --- |
| All seven | 34.5% | 577 µm | **none** |
| The four that individually reach 10% | 14.1% | 391 µm | **none** |
| The 1/L group — τ3, τ4, τ6 | 25.3% | 498 µm | **none** |
| τ1 + τ4 | 11.2% | 635 µm | **none** |
| **τ1 + τ2 — the dimensionless pair** | **5.4%** | 338 µm | **307–431 µm** |

Three conclusions, and they point the same way:

- **The only group with a common window is the dimensionless pair.** τ1 and τ2 agree within 10%
  anywhere from 307 to 431 µm. Every group containing a dimensioned metric has an empty band. *The
  measurements that need no unit conversion are also the only ones a single smoothing choice can
  pin down*, which is a tidier result than it has any right to be.
- **τ2 and τ4 want incompatible windows** — 307–431 µm against 667–892 µm — although they differ
  only by a division by arc length. That is not an estimator artefact: smoothing shortens the
  measured arc length too, so in τ4 the error in ∫κ ds is partly cancelled by the error in `s`,
  and the two quantities are optimal at different places. Nothing can reconcile them.
- **The squared-curvature metrics never reach 10%** — τ3, τ5 and τ7 bottom out at 22–25%. Squaring
  squares the estimation error, and no window recovers it.

**What this is evidence about.** One estimator — a boxcar smoother and finite differences — on two
curved synthetic shapes. A spline-based estimator will do better, and the plan should not conclude
that τ3, τ5 and τ7 are unmeasurable in principle. What it can conclude is that **a single declared
window is not enough to make the τ family comparable**, because the requirement is not one number
but a different number per metric, and two of them conflict outright. If the vocabulary is going to
carry an estimation scale (section 5), that scale belongs **per name, not per implementation**.

Both tables above come from a one-off script rather than from anything committed, which is a
weakness in this document: nobody can re-run them. Section 8 makes turning them into a test part of
the work, because a claim about comparability that cannot be re-checked is the kind of claim this
repository exists to distrust. The same applies to 3.3 and 3.4.

Two findings fall out of the same experiment:

- **Hubbard and Knudtson equivalents come out in different units.** Hubbard's fitted constants are
  in microns, so an implementation must convert to microns to apply it, and the answer is physical
  (×1). Knudtson's formula is purely multiplicative, so it returns whatever unit the widths were in
  — pixels (×2). *These two variants sit on one page, under one biomarker, and a table holding both
  is incoherent.* This is the clearest single argument for the plan.
- **The τ family splits three ways.** τ1 and τ2 are dimensionless; τ3, τ4 and τ6 are inverse
  lengths; τ5 and τ7 are inverse areas. "Tortuosity" as a column heading spans three different
  physical dimensions.

## 4. Gap C — a definition is a sentence, not a reference

**Fact.**

- Five biomarker pages have **no canonical name at all**: `cup-to-disc-ratio`,
  `disc-fovea-distance`, `temporal-angle`, `vascular-curvature-index`, `vessel-tracing`. Two of
  them are computed by VascX today and land in the unmapped list.
- Two documented biomarkers have **no defining paper**: vascular density (`No single origin`) and
  cup-to-disc ratio (`Clinical measure`). Both may be honest answers; both need saying explicitly
  rather than by omission.
- One is **proprietary and uncomputable**: the vascular curvature index, whose paper declines to
  give the formula. It should never get a canonical name, and the vocabulary should be able to
  record *why* rather than being silently short of it.
- `canonical.py` names **eleven** tortuosity variants; `docs/biomarkers/tortuosity.md` says
  "**9+**". Nothing checks that the code and the page agree.

## 5. What a name has to carry

**Proposed.** A canonical name is a claim that two numbers under it are comparable. For that claim
to hold, five things have to match, and today only three of them are in the name:

| Axis | In the name today | Example values |
| --- | --- | --- |
| Biomarker | ✅ | `tortuosity` |
| Variant — *the formula, not the word* | ✅ | `hart-tau1` |
| **Region** — *what part of the retina* | ❌ | whole, zone-b, zone-c, disc-ring |
| **Statistic** — *how per-segment values were pooled* | ❌ | mean, median, std, length-weighted |
| Structure | ✅ | artery, vein, vessels, both |

And three things have to be recorded *about* the name, none of which are today:

| Property | Why it matters |
| --- | --- |
| **Unit / dimension** | The pooling question of section 3. A name must say whether it is dimensionless, a length, an area, an inverse length, or an angle |
| **Defining paper** | The primary goal. A variant whose definition nobody can cite is a name two people will fill differently |
| **Normalisation** | What turns the raw number into something comparable — see section 6 |
| **Estimation scale** | For the curvature family, the physical window the derivative was taken over — see 3.2 and 3.3. It is a number in microns rather than a category, so it belongs beside the name rather than in it, but a curvature reported without it is not comparable with anything |

## 6. Normalisation — what "normalised" should mean

**Open.** Three routes, and they are not exclusive:

1. **Report in physical units.** Multiply lengths by µm/px, areas by µm/px². Requires a scale, which
   [most datasets do not publish](docs/DATASETS.md) — `fetch-um-resolution` infers one from the
   median optic disc for exactly this reason. **Honest, and unavailable for many datasets.**
2. **Normalise by an ocular landmark.** Express lengths as fractions of the disc diameter or the
   disc–fovea distance. Needs no camera calibration and is what VascX already does for sparsity.
   **Available everywhere, and changes what the number means.**
3. **Report the raw number and its unit, and let the analysis convert.** The benchmark stores
   pixels plus the scale it had; the notebook converts. **Least lossy, most room for error downstream.**

None of the three is sufficient on its own for the curvature family, which needs a declared
estimation scale as well (3.2). For calibre, area, length and sparsity — which are first-order
quantities — units alone do settle it.

My reading: (3) as the storage rule — the evidence stays raw and reversible — with (1) and (2) as
*declared, named* normalisations, so `vessel-calibre/mean-width/artery` in microns and in
disc-diameters are two different canonical names rather than one name with a footnote. That keeps
the rule that a name is a promise of comparability. It costs more names.

## 7. Open decisions

These change the work substantially and are Stas's call.

- **7.1 How many axes go in the name?** Five (`biomarker/variant/region/statistic/structure`) is
  explicit and makes every name self-describing, at the cost of long names and a combinatorial
  expansion — 90 names today would become several hundred, most of them never computed. The
  alternative is three axes plus **qualifiers carried beside the name** as structured fields, which
  keeps names short but means a column heading no longer identifies a measurement on its own.
- **7.2 Does the normalisation go in the name or beside it?** Same trade-off, and it should
  probably get the same answer as 7.1.
- **7.3 Do we keep names nothing implements?** 53 of 90 are claimed by no implementation. Some are
  aspirational and right to keep (τ4 and τ5 are in Hart's paper whether or not anybody computes
  them); some may be clutter. A rule is needed, not a case-by-case purge.
- **7.4 Is a defining paper mandatory?** Making it so is the primary goal, but it would block
  vascular density and cup-to-disc ratio, which are real measurements with no single origin. The
  alternative is a required field whose value may be `no single origin`, with the page saying so.
- **7.5 What happens to the stored evidence?** Renaming canonical names invalidates the mapping in
  every adapter, but **not the measurements** — the benchmark stores each implementation's own
  column names and the notebook joins. So a rename costs adapter edits and a notebook re-run, and
  **no re-measurement**. This is worth stating plainly because it makes the change much cheaper
  than it looks, and it is only true because of the own-names decision taken earlier.

## 8. Order of work

**Proposed**, once 7.1–7.4 are settled.

1. Extend `canonical.py` from a name→sentence map to a name→record map carrying unit, region,
   statistic, paper and normalisation. Keep `check()` as the single gate.
2. Add the axes agreed in 7.1, and re-map all six adapters — the 44 region-axis and 15
   statistic-axis columns are the measure of success.
3. Make every variant cite a paper, and catalogue the papers still missing.
4. Teach the synthetic shapes to settle the new names, so the benchmark can check them — and
   **turn 3.2 into a test**: one physical retina built at several grids, every name that claims to
   be normalised asserted to hold its value across them. That test is what stops a name silently
   returning to pixels, and it is the only part of this plan that can fail loudly.
5. Regenerate `BIOMARKERS.md`, `BIOMARKER-NAMES.md` and the benchmark's configuration page from the
   record, so code and prose cannot disagree again.
6. Re-run the analysis notebook. **No re-measurement** — see 7.5.

---

**Written:** 2026-09-25
