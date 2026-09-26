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

Two findings fall out of the same experiment:

- **Hubbard and Knudtson equivalents come out in different units.** Hubbard's fitted constants are
  in microns, so an implementation must convert to microns to apply it, and the answer is physical
  (×1). Knudtson's formula is purely multiplicative, so it returns whatever unit the widths were in
  — pixels (×2). *These two variants sit on one page, under one biomarker, and a table holding both
  is incoherent.* This is the clearest single argument for the plan.
- **The τ family splits three ways.** τ1 and τ2 are dimensionless; τ3, τ4 and τ6 are inverse
  lengths; τ5 and τ7 are inverse areas. "Tortuosity" as a column heading spans three different
  physical dimensions.

**Every table in this section comes from a one-off script rather than from anything committed**,
which is a weakness in the document: nobody can re-run them. Section 8 makes turning them into a
test part of the work, because a claim about comparability that cannot be re-checked is the kind of
claim this repository exists to distrust.

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

### 3.4 With a boxcar smoother there is no common window

**Fact, measured.** 3.3 asked how long the window should be for one metric. Asking it for **all
seven at once**, against their theoretical values, on `straight`, `arc` and `sinusoid` at 1024,
2048 and 4096 px — 45 (shape, grid, metric) cases with a non-zero theoretical value — gives no such
window. Smoothing with a boxcar and differentiating by finite differences:

| Metric | Units | Best achievable | Reaches 10% at |
| --- | --- | --- | --- |
| τ1 | 1 | 0.4% | 40–549 µm |
| τ2 | 1 | 5.0% | 307–431 µm |
| τ6 | 1/L | 1.9% | 391–700 µm |
| τ4 | 1/L | 1.4% | 667–892 µm |
| τ3 | 1/L | 25.3% | **never** |
| τ7 | 1/L² | 23.2% | **never** |
| τ5 | 1/L² | 22.3% | **never** |

The best compromise over all seven is 34.5%; over the four that individually reach 10%, 14.1%. The
only group with a common band is the dimensionless pair τ1 and τ2, at 307–431 µm.

One part of that survives section 3.5 and is worth keeping: **τ2 and τ4 want incompatible windows**
— 307–431 µm against 667–892 µm — although they differ only by a division by arc length. Smoothing
shortens the measured arc length too, so in τ4 the error in ∫κ ds is partly cancelled by the error
in `s`. That is a property of the quantities, not of the smoother.

### 3.5 With a spline estimator there is one, and the earlier conclusion was wrong

**Fact, measured.** 3.4 concluded that the squared-curvature metrics were beyond recovery because
"squaring squares the estimation error". **That was wrong**, and it was wrong because it
generalised from one bad estimator. Replacing the boxcar and finite differences with a
**least-squares cubic spline** — knots at a physical spacing, derivatives taken analytically, which
is what VascX already does — on exactly the same paths, shapes and grids:

| Metric | Boxcar, best | **Spline, best** | |
| --- | --- | --- | --- |
| τ1 | 0.4% | **0.1%** | |
| τ2 | 5.0% | **2.3%** | |
| τ3 | 25.3% | **1.4%** | **recovered** |
| τ4 | 1.4% | **2.5%** | |
| τ5 | 22.3% | **2.0%** | **recovered** |
| τ6 | 1.9% | **1.4%** | |
| τ7 | 23.2% | **1.9%** | **recovered** |

**Every one of the seven now reaches 10%, and there is a common window: 711–1507 µm**, with the
best compromise 7.6% at 914 µm. At that spacing, the error per metric at each grid:

| Metric | 1024 px | 2048 px | 4096 px |
| --- | --- | --- | --- |
| τ1 | 3.3% | 3.8% | 3.8% |
| τ2 | 5.7% | 5.9% | 5.8% |
| τ3 | 7.5% | 7.2% | 6.9% |
| τ4 | 4.5% | 4.1% | 3.8% |
| τ5 | 7.4% | 6.9% | 6.5% |
| τ6 | 4.6% | 4.2% | 4.0% |
| τ7 | 7.6% | 7.0% | 6.6% |

**The columns barely differ.** One declared physical window, one estimator, and all seven
tortuosity measures hold their value to within about 8% over a sixteenfold change in pixel area.
That is the demonstration section 6 needed: normalising by physical units is not just
dimensionally correct, it *works* — provided the estimator is stated too.

Which is the conclusion that replaces 3.4's: **the estimator matters more than the window.** Going
from a boxcar to a spline improved τ3 by a factor of eighteen; no choice of window could do
anything comparable. Two implementations reporting τ3 at the same declared scale can differ by
twenty percentage points purely from how they take a second derivative.

**So an estimation scale is not enough for a name to promise comparability — the estimator has to
be named as well.** That is a heavier requirement than section 5 first recorded, and it is the main
thing these four subsections have established.

**What this is still evidence about.** Two curved synthetic shapes, one spline variant, one knot
placement rule. It shows the τ family *can* be made comparable, not that 914 µm is the number for
retinal vessels — which, as 3.3 says, has to be measured on vessels.

### 3.6 A better estimator than either, and the one thing it gets wrong

**Fact, measured.** Pheno AutoMorph's `tortuosity_calculations.py` estimates curvature a third way,
and it is Hart's own recipe rather than anybody's improvisation: low-pass the coordinates with a
Gaussian, then take **κ = dα/ds as the slope of a least-squares line through a window of (arc
length, tangent angle) samples**. Curvature comes out of a *first* derivative of the tangent angle
rather than a second derivative of position, which is where the difference comes from — every
differentiation amplifies quantisation noise, and this one does it once instead of twice.

On the same paths, shapes and grids as 3.4 and 3.5, each method at its own best setting, worst case
over all seven metrics:

| Estimator | Its scale | Worst error |
| --- | --- | --- |
| Boxcar + finite differences | — | 34.5% |
| Least-squares cubic spline | knots every 928 µm | 8.1% |
| **Angle regression (Pheno AutoMorph)** | **σ = 45 µm** | **6.9%** |

That σ is **not a constant**, and 3.7 shows what it is a fraction of. It is the best value *for the
shapes in this test*, whose features are thousands of microns across.

**But as shipped its parameters are in pixels**, `σ = 6 px` and a 10-sample window, and that is the
whole difference between working and not:

| | 1024 px | 2048 px | 4096 px |
| --- | --- | --- | --- |
| Angle regression **as shipped** (σ = 6 px) | 10.4% | 4.5% | **40.4%** |
| Angle regression at **σ = 45 µm** | 6.9% | 6.9% | 6.9% |
| Cubic spline, knots 928 µm | 7.6% | 7.2% | 8.1% |

The shipped configuration is excellent at 2048 — 4.5%, better than anything else here — and six
times worse at 4096, because 6 px is 15 µm there and no longer suppresses the raster staircase.
**It is tuned to a grid, not to an eye.** Converting the same two constants to microns makes the
error identical at all three resolutions, to the decimal. That is the strongest evidence in this
document for the whole normalisation argument, and it cost two divisions.

Three things follow for the plan:

- **The estimation scale is meaningless without the estimator.** Angle regression wants σ = 45 µm
  and the spline wants knots every 928 µm — a factor of twenty apart, both correct for their
  method. A canonical name recording "estimated at 500 µm" and nothing else has recorded nothing.
- **Hart's own recipe beats the obvious numerical one.** The paper specifies the angle regression;
  implementations that differentiate coordinates instead are not computing a worse approximation of
  the same thing, they are measuring the raster.
- **A pixel-parameterised estimator is the defect this plan exists to catch.** It is invisible on
  the grid it was tuned on, and nothing in a results table would reveal it.

### 3.7 One σ cannot serve every feature scale, and the failures are not where they looked

**Fact, measured.** 3.6 found σ = 45 µm best on shapes whose features are thousands of microns
across. Testing it on sinusoids of six wavelengths — three grids, four rotations, all seven
metrics, against theory, with the drawing checked first — gives this:

| Wavelength | Amplitude ÷ vessel width | Drawing's own τ1 error | Best σ | σ ÷ wavelength | Worst at best σ | Worst at σ = 45 µm |
| --- | --- | --- | --- | --- | --- | --- |
| 100 µm | 0.27 | **−21 to −27%** | 4 µm | 0.040 | **100%** | **100%** |
| 200 µm | 0.55 | −1.6 to −3.8% | 5 µm | 0.025 | 28% | 97% |
| 300 µm | 0.82 | +0.2 to +2.6% | 8 µm | 0.027 | 20% | 74% |
| 1000 µm | 2.73 | +3.8 to +4.1% | 20 µm | 0.020 | **7%** | 17% |
| 2000 µm | 5.47 | +4.0 to +4.3% | 25 µm | 0.013 | **9%** | 15% |
| 3000 µm | 8.20 | +4.2 to +4.5% | 31 µm | 0.010 | **7%** | 13% |

**The regime boundary is the amplitude against the vessel's own width, not the wavelength.** Where
the wave is narrower than the vessel drawn along it, the drawing loses a quarter of its arc length
before any estimator sees it — the Koch defect of 3.3 in another costume — and no σ helps. Where
the wave is two to eight times the vessel width, the drawing is faithful to about 4% and the
estimator reaches 7–9%.

**Retinal vessels live in the second regime**, so the practical news is better than the top of the
table suggests: at feature scales of 1 mm and above, Hart's angle regression at its best σ holds
every one of the seven metrics to within 9%, and even at an untuned σ = 45 µm to within 17%.

**But one σ still cannot serve them all.** The best σ runs from 4 µm to 31 µm across the range,
and σ = 45 µm — optimal for the 1638 µm shapes of 3.6 — reads 100% wrong at 100 µm and 13% wrong
at 3000 µm. A pipeline fixing σ once is choosing which vessels it measures correctly.

**How σ scales is not a fixed fraction.** σ ÷ wavelength falls from 0.040 to 0.010 as the
wavelength grows, so the optimum rises *sub-linearly* — about λ^0.6 over the thirtyfold range
measured. An earlier draft of this section claimed a constant three per cent; that was fitted to
the three shortest wavelengths, which is exactly the regime where the estimator was failing for a
different reason, and it does not survive the rest of the range.

So the three ways of setting a scale rank like this, and the third is still the only one that is a
property of the eye:

| Scale expressed as | Resolution-independent | Feature-scale-independent |
| --- | --- | --- |
| Pixels, as shipped | ❌ 4.5% → 40.4% (3.6) | ❌ |
| Microns | ✅ 16 / 16 / 16% across grids at 1 mm | ❌ 7% → 100% across feature scales |
| Tied to the feature scale | ✅ | ✅ *if the feature scale can be estimated first* |

Two smaller things this measured:

- **Resolution independence holds where the method works.** At 1000 µm the error reads 16, 16, 16%
  across the three grids; at 3000 µm, 13, 11, 11%. Converting σ to microns does what 3.6 said it
  does.
- **Rotation matters and is not noise.** At 3000 µm and 1024 px the four angles read 5, 9, 13, 4%,
  and at every short wavelength 0° and 90° beat 30° and 60°. It is second-order beside the feature
  scale and it is consistent.

**What the plan takes from this.** Not that the τ family is unusable — at retinal feature scales it
is good to within about 9%. What it cannot do is carry a **fixed** estimation scale: the number
that makes τ5 correct depends on the vessel, so two pipelines agreeing on σ are still not
comparable unless they also agree on what they pointed it at. That is an argument for recording
the estimator and its scale with every value, and against ever writing one σ into the vocabulary.

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
| **Estimation scale** | For the curvature family, the physical window the derivative was taken over — see 3.2 and 3.3. A number in microns rather than a category, so it belongs beside the name rather than in it |
| **Estimator** | *How* the derivative was taken — finite differences, a spline, or Hart's angle regression. Section 3.5 measures a factor of eighteen on this choice alone; 3.6 shows the scales are not commensurable between estimators; 3.7 shows the scale is not even a length. A scale recorded without its estimator records nothing |

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
