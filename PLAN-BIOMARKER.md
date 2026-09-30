# Biomarkers: the plan

What we decided and why, before any of it is built. Sections marked **Decided** are settled;
**Open** needs Stas's call. Nothing here is code.

This is the standing plan for **the biomarkers themselves** — what they are called, what defines
them, and what makes two of them comparable. It is separate from
[PLAN-BENCHMARK.md](PLAN-BENCHMARK.md), which is about what gets measured against what: a benchmark
consumes this vocabulary and does not decide it.

**The chapters below are the order the work happens in**, and each depends on the one above it. A
name cannot be agreed before the reason for naming is; an implementation cannot be mapped onto a
vocabulary that does not exist; and a reference implementation cannot be written against
definitions nobody has pinned down.

| Chapter | Question it settles |
| --- | --- |
| 1 | Why a canonical list at all |
| 2 | What every canonical biomarker must carry |
| 3 | How the existing implementations map onto it |
| 4 | What an implementation of one has to get right |
| 5 | The reference implementation: what it is for, and what may not cross into this repository |

---

## 1. Why a canonical list at all

**Decided.** Three reasons, and they want different things from the list, which is why it is worth
writing them down separately.

### 1.1 To compare implementations

Two pipelines both report "tortuosity" and the numbers differ by a factor of seven. Without a
vocabulary there is no way to tell whether they disagree about the vessel, about the formula, or
about the word — and the answer is usually the word. A canonical name is **a claim that two numbers
under it are comparable**, and the benchmark exists to test that claim.

This is the reason the list already half-exists: `src/biomarkers/canonical.py` was written to get
the first biomarker benchmark running, and it did.

### 1.2 To have a definition rather than a word

"Tortuosity" names at least eleven formulas in this catalogue alone, "CRAE" two, and a paper will
usually report the name and omit the choice. A canonical entry must therefore carry **what the
quantity is**, not only what it is called: the defining paper, the formula, the units, and enough
of an algorithm that two people implementing it separately would agree.

That is a different requirement from 1.1 and a stricter one. Comparison needs names that do not
collide; definition needs names that mean something on their own.

### 1.3 To make adding one a decision

New biomarkers arrive constantly, and most of them are a published variant of something already
here. Without a rule, the list grows by whatever an implementation happened to return, and the
distinction between "a new measurement" and "the same measurement computed differently" is lost —
which is precisely the distinction 1.1 depends on.

So the list needs a **way in**: what evidence a new entry needs, which axis it varies along, and
who decides. The same rule tells us when a family is needed rather than an entry.

---

## 2. What every canonical biomarker must carry

### 2.1 The name

**Decided.** Five parts, the last two optional:

```
family / biomarker / structure / [roi] / [statistic]
```

| Part | What it is | Examples | Default |
| --- | --- | --- | --- |
| `family` | the page in `docs/biomarkers/`, the kind of thing measured | `tortuosity`, `vessel-calibre` | required |
| `biomarker` | **the definition, not the word** — which formula | `hart-tau1`, `knudtson` | required |
| `structure` | what it was measured over | `artery`, `vein`, `vessels`, `both` | required |
| `roi` | the region it was measured within | `fov`, `B`, `C`, and any name added later | **`fov`** |
| `statistic` | how per-segment values were pooled | `mean`, `median`, `std`, `length-weighted` | **`median`** |

So `tortuosity/hart-tau1/artery` is the median τ1 over the whole field of view, and
`vessel-calibre/mean-width/artery/B/mean` says all five parts outright. Both optional parts may be
omitted, and **the statistic may be given while the region is not** — in which case the region is
the field of view.

That last rule creates the one thing this naming scheme has to be careful about.

#### 2.1.1 The family decides which parts apply

**Decided.** The table above gives the **global** defaults; a **family overrides them**. A family
record says which parts apply to it at all, and what each defaults to when omitted:

| Family | `structure` | `roi` | `statistic` |
| --- | --- | --- | --- |
| `vessel-calibre`, `tortuosity`, `vascular-density`, `fractal-dimension` | applies | defaults to `fov` | defaults to `median` |
| `central-retinal-equivalents`, `avr` | applies | **required** — there is no field-of-view-wide CRAE | none |
| `cup-to-disc-ratio`, `disc-fovea-distance`, `temporal-angle` | **none** — they are not measured over a vessel class | does not apply | none |

So `cup-to-disc-ratio/vertical` is a complete two-part name, and
`central-retinal-equivalents/knudtson/artery` is an **error** rather than a default, because the
region is part of what that number means and a reader who did not know there was a choice would
otherwise never learn there was one.

**This also removes most of the parsing problem.** A name's shape alone cannot say whether the
fourth token of `vessel-calibre/mean-width/artery/B` is a region or a statistic — but the family
record can, because it says which parts that family has. Where a family has **both** optional parts,
their two vocabularies must still be **provably disjoint**, and `check()` enforces it rather than
assuming it: a region named `mean` would make every such name ambiguous the day it was added, and
silently.

#### 2.1.2 What the measurement is taken over goes in the name

**Decided, 2026-09-30.** Where a quantity can be computed over a **segment** or over a **whole
vessel**, those are two biomarkers and they get two names:

| Name | Measured over |
| --- | --- |
| `tortuosity/hart-tau1` | **segments** — the pieces between intersection points, after pruning. What most implementations compute |
| `tortuosity/vessel-hart-tau1` | **whole vessels** — each start-to-end path through the tree taken as one vessel |

The `vessel-` prefix is the general convention, available to any family where the distinction
arises, and the unprefixed name is the segment form because that is what the field mostly does.

**This is Hart's own distinction, not a convenience.** The 1999 paper classified *vessel segments*
at about 91% and *vessel networks* at about 95% against ophthalmologists' judgement, and its
central argument is **compositionality** — that the score of a whole vessel should be recoverable
from the scores of its parts. Its table marks which of the seven compose and which do not, and that
is exactly the axis this naming exposes:

- For the **compositional** measures — τ4 and τ5, the pair Hart's argument favours — the two
  variants are related by construction, and a reader can move between them.
- For the **non-compositional** ones, including τ1 and τ3, they are simply different numbers.
  Reporting one under the other's name is the error this split exists to prevent.

It also settles what a **pooled statistic** pools. `tortuosity/hart-tau1/artery` with the default
statistic is the median over *segments*; `tortuosity/vessel-hart-tau1/artery` is the median over
*vessels*. Those were the same name until now, over different populations.

**A vessel is root-to-tip, as PVBM traces it.** Each path from the vessel's origin at the optic
disc to one leaf is one vessel, so a tree with *N* leaves has *N* vessels — not the *N(N−1)/2* that
taking every pair of free ends would give. Three consequences follow, and each is a requirement
rather than an observation:

- **The `vessel-` forms need a rooted trace, and therefore need the disc.** An implementation with
  no disc cannot compute them at all — the same kind of dependency the central retinal equivalents
  have on their ring, and it belongs in the family record beside them.
- **Vessels that never reach the disc are not vessels.** PVBM already behaves this way: on the
  `disjoint` shape, whose segments are nowhere near the disc, its rooted walk finds no trunks and
  returns zeros. Under this definition that is *correct* rather than a defect, and the synthetic
  shapes must settle the `vessel-` names accordingly — which means `disjoint` settles none of them.
- **It makes sense of a mapping this atlas withdrew.** Under a rooted model PVBM's `start_points`
  counts roots and its `endpoints` counts tips — and tips are exactly vessels. The endpoint mapping
  was withdrawn because the catalogued name meant *every free end* and PVBM's excluded the one at
  the disc; under the rooted definition that is not an error but a different, nameable quantity.
  Chapter 7 should look at whether `junction-counts` wants a rooted pair of names — free ends
  against tips — rather than leaving two implementations' columns unmapped.

### 2.2 Units — microns, never pixels

**Decided.** A canonical biomarker is **never expressed in pixels.** Anything with a length
dimension is in microns, anything with an area dimension in microns squared, and the inverses
likewise — `1/µm` for a curvature, `1/µm²` for the squared-curvature measures. Dimensionless stays
dimensionless, and `1` is a unit rather than a blank. This applies to the central retinal
equivalents and the tortuosity family exactly as it applies to calibre.

**Why it has to be a rule rather than a preference.** The same physical retina was built at
1024 px / 10 µm per pixel and at 2048 px / 5 µm per pixel — one eye, two cameras — and every
theoretical value compared:

| Behaviour | Count | Names |
| --- | --- | --- |
| **Scale-free** (×1) | 40 | τ1, τ2, Grisan density, inflection count, fractal dimensions, junction counts, densities, AVR, bifurcation angle, **Hubbard** equivalents |
| **Length in pixels** (×2) | 15 | calibre mean and median, skeleton length, sparsity, **Knudtson** equivalents |
| **Inverse length** (×0.5) | 8 | τ3, τ4, τ6, spline mean curvature |
| **Inverse area** (×0.25) | 4 | τ5, τ7 |
| **Area in pixels²** (×4) | 3 | vessel area |

**Thirty of seventy give a different answer for the same eye.** The rule removes that whole column
of the problem: in microns every one of those thirty is the same number at both resolutions.

It also settles a contradiction the catalogue has been carrying. **Hubbard and Knudtson equivalents
currently come out in different units** — Hubbard's constants are fitted in microns so an
implementation must convert, while Knudtson's formula is purely multiplicative and returns whatever
the widths were, which is pixels. Two variants, one family, incomparable. Under this rule both are
microns and the family is coherent.

**Three consequences, none of them free:**

- **A scale is always available, so nothing has to be refused.** Where a dataset publishes microns
  per pixel, that figure is used. Where it does not, one is **inferred from the optic disc on the
  assumption that a disc is 1800 µm across** — which is what `fetch-um-resolution` already does and
  what the synthetic shapes are already drawn to. A `None` scale is therefore a bug in the fetch
  rather than a state a biomarker has to cope with.

  The price is the one that assumption always carries, and it is recorded on every page that quotes
  an inferred scale: **a length derived from an inferred scale cannot then be used to say anything
  about disc size**, because the disc was defined to be 1800 µm to obtain it. Anything anchored to
  the disc — the equivalents' zones, the disc–fovea distance — inherits that circularity and must
  say so.
- **Every conversion is the adapter's job**, per 3.2. An implementation reporting pixels has its
  output multiplied by the scale the store recorded; one reporting millimetres is converted; one
  applying micron-fitted constants to pixel widths is **wrong**, and the benchmark reports the
  number rather than repairing it.
- **The synthetic shapes are rebuilt, not converted.** Their ground truth is in pixels today and
  the whole store is redrawn to emit microns, so the committed `ground_truth.csv` is in the units
  the vocabulary requires rather than in units plus a note. It changes every stored theoretical
  value and therefore every comparison drawn against it.

### 2.3 The definition

**Decided.** Every entry carries:

| Field | Why |
| --- | --- |
| **Short definition** | one line, for a table |
| **Long definition** | enough that two people implementing it separately would agree — the formula, and what it is computed over |
| **Defining paper**, *or* the substitute below | the primary goal of this plan |
| **Units** | 2.2 |
| **Estimation requirements** | where the answer depends on how a derivative is taken — chapter 4 |

#### 2.3.1 A paper is not mandatory, and what replaces it is heavier

Some real measurements have no single origin. Vascular density is one, cup-to-disc ratio another —
both are clinical practice rather than somebody's proposal, and demanding a citation would either
block them or invite a dishonest one.

**Where there is no defining paper, the page carries a detailed description in its place**: the
formula written out, what it is computed over, the conventions it assumes, and **optionally a
pointer to an open-source implementation** that can be read as a worked example. That is a heavier
obligation than a citation, not a lighter one — a reader following a DOI gets the authors' own
account, and a reader following this gets ours, which had better be good enough to implement from.

An implementation is a *pointer*, never the definition. Code changes and the entry must not, which
is 5.3's rule pointing the other way.

#### 2.3.2 A name with no implementation is kept if a paper asks for it

**Fact:** 53 of 90 canonical names are claimed by no implementation in this catalogue.

They stay, on one condition: **a paper names or recommends the quantity.** Hart's τ4 and τ5 are in
his table and marked compositional whether or not anybody has written code for them; the vocabulary
records what the literature asks for rather than what happens to exist in Python today. Some of them
may end up implemented in `fundus-biomarkers` precisely because nothing else implements them, which
is a reason to name them now and not later.

A name that no paper asks for and no implementation computes is clutter, and goes.

**Fact, and the exception that proves the rule:** five biomarker pages have no canonical name at all
— `cup-to-disc-ratio`, `disc-fovea-distance`, `temporal-angle`, `vascular-curvature-index`,
`vessel-tracing`. Four should get one. The fifth, the vascular curvature index, should never: its
paper declines to give a formula, so it cannot be defined under 2.3.1 either, and the page must say
that rather than leaving the absence to be guessed at.

### 2.4 Region of interest — what the decision costs

**Decided** in 2.1: the region is **its own optional name part**, defaulting to the field of view.
This section records what that buys and what it leaves to do.

**Fact:** 44 of the 73 implementation columns the catalogue cannot name are quantities it *already*
names, measured over a region it could not express. AutoMorphalyzer reports most quantities three
times — `@whole`, `@B`, `@C` — and VascX reports several over a disc-centred circle at 7/6 disc
radii. Zones B and C are the conventional annuli from the ARIC literature, so this is the field's
standard practice rather than an implementation's quirk. **That is the single largest gap in the
vocabulary and the region part closes it.**

Two things it does *not* settle, both of which need a per-family judgement when chapter 7 rewrites
the pages:

- **Whether the region is definitional or a choice.** For the central retinal equivalents it is part
  of what the number means — there is no CRAE without a ring — which is why 2.1.2 proposes that
  family require it. For calibre, tortuosity, density and the fractal dimensions the same
  measurement is simply restricted to an area, and the default is right. For the temporal angle and
  the disc–fovea distance the region does not apply at all: they are defined relative to landmarks,
  not over an area, and should refuse a region rather than accept one that means nothing.
- **Where the region vocabulary is written down.** Zones B and C are **well defined in the
  literature** — the ARIC convention behind Hubbard's and Knudtson's equivalents — and this
  repository already encodes one of them (`ZONE_B_RADII = (2.0, 3.0)`, in disc radii) and records
  what each implementation does in `docs/biomarkers/central-retinal-equivalents.md` §5. What is
  missing is a **single page that states the vocabulary**, so that the `roi` part of a name points
  at a definition rather than at a convention everybody is assumed to know. See 2.4.1.

#### 2.4.1 The regions get their own reference page

**Decided, 2026-09-30.** `docs/biomarkers/regions-of-interest.md`, a sibling of
`vessel-tracing.md` — which is also not a biomarker and is catalogued there for the same reason,
that several biomarkers cannot be read without it. It carries:

- **Each standard zone**, with its inner and outer bound and the paper that fixed them. Zone A, B
  and C come from the ARIC convention behind [Hubbard 1999](docs/papers/hubbard-1999.md) and
  [Knudtson 2003](docs/papers/knudtson-2003.md); the bounds must be **checked against those papers
  when the page is written** rather than copied from this plan.
- **The units, unambiguously, in both forms.** The classical convention is stated in disc
  *diameters* from the disc margin and this repository's code in disc *radii* from the disc centre.
  `docs/biomarkers/central-retinal-equivalents.md` §5 already calls that "a factor-of-two trap when
  reading code", and it is the single most likely way for two implementations to look like they
  disagree about vessels while agreeing about everything except arithmetic.
- **`fov`**, the default: the whole field of view, which is a region like any other and needs
  saying so.
- **The non-standard regions implementations actually use**, because they exist and the vocabulary
  has to accommodate them. VascX measures over several concentric circles between a configurable
  inner and outer radius, keeping the largest six vessels per circle and taking the median across
  them; its `crcl_multiplier_1p16666666667` column is 7/6 written as a float. A region that is not
  one of the standard zones gets a name that says what it is, or the number is reported under the
  implementation's own column name and mapped to nothing.

The page is reference, not plan: it is where `check()`'s region vocabulary comes from, and adding a
region means adding it there first.

## 3. How the existing implementations map onto it

### 3.1 What they supply today

**Fact.** 73 columns across six implementations have no canonical name, and only **six** are
quantities the catalogue has never heard of:

| Count | Cause | Example |
| --- | --- | --- |
| **44** | a **region** axis that does not exist (2.4) | `average_local_calibre@whole_binary` |
| **15** | a **statistic** axis that does not exist (2.1) | `mean_branching_angle_artery`, `pooled_tortuosity_artery` |
| 6 | genuinely new quantity | `perimeter_artery`, `singularity_length_artery` |
| 6 | mapping withdrawn as wrong | `squared_curvature_tortuosity_*` — it squares nothing |
| 2 | family exists as a page but not as a name | `disc_fovea_distance_retina` |

**The vocabulary is not missing biomarkers. It is missing axes** — one of which 2.1 adds and one of
which 2.4 must settle.

**Settled 2026-09-30, and the count is now 67 of a larger total.** Both axes exist: a name carries
a region and a statistic, and `length-weighted` joined `mean`, `median` and `std` because three
implementations report it. What remains uncatalogued, by cause:

| Count | Cause | Example |
| --- | --- | --- |
| **25** | a quantity computed over a **region the catalogue does not define**: zone C, which is 2–5 disc radii, and an equivalent over the whole image, which is not what an equivalent means | `tortuosity_density@C_artery`, `CRAE_Knudtson@whole_artery` |
| **12** | a **class the column was not computed for** — AutoMorphalyzer runs every column over all three maps, so CRAE over the veins and CRVE over the arteries exist and answer nothing | `CRAE_Knudtson@B_vein` |
| 9 | an **aggregation or variant the catalogue does not separate**: a mean of per-vessel widths that excludes branch points, a ratio of sums, two further segment caps | `average_local_calibre@*`, `pooled_tortuosity_artery` |
| 8 | **withdrawn as wrong**, each with its date and its reason | `squared_curvature_tortuosity_*`, `mean_sparsity_vessels` |
| 6 | **anchored to a fovea** this fixture invents, so nothing here can settle it | `median_temporal_angle_arteries`, `disc_fovea_distance_retina` |
| 4 | a **rooted walk's own vocabulary** — start points and the free ends that exclude them | `start_points_artery`, `endpoints_artery` |
| 3 | genuinely new quantity | `singularity_length_artery`, `tortuosity_index_artery` |

The two axes did their work: AutoMorphalyzer's zone-B tortuosity columns are now catalogued, the
AutoMorph group's width and tortuosity aggregations are named apart, OCULAR's third tortuosity has
a name, and the perimeter left with PVBM's deprecated class. **What is left is mostly not a
missing axis but a region nobody has defined** — 25 of the 67 — which is 2.4's remaining work.

### 3.2 Conversion rules

**Open.** Mapping an implementation's column onto a canonical name is **a claim that has to be
testable**, and this repository has already been wrong about several:

- `squared_curvature_tortuosity` was mapped to Hart τ3 until a shape showed it off by five orders of
  magnitude — it squares nothing. *Withdrawn.*
- `median_branching_angle` was mapped to the angle between daughters until a shape showed it medians
  every pairwise angle at every junction, trunk included. *Withdrawn.*
- `endpoints` was mapped to the catalogued endpoint count until PVBM's replacement class began
  calling the end at the disc a *start point*. *Withdrawn for PVBM and OCULAR both.*
- `mean_sparsity_vessels` was mapped to `density/sparsity` the day that name existed, and the
  shapes disagreed by a factor of 3,900. VascX normalises it by the optic-disc-to-fovea distance,
  so it is a dimensionless ratio rather than a distance in microns — and on a synthetic shape that
  denominator is a convention this repository supplied. *Withdrawn 2026-09-30, and the fastest of
  these withdrawals: the shapes caught it within one run of the mapping being written.*

So the rules a mapping must satisfy:

1. **Read from the code, not the name.** Every withdrawal above came from reading somebody's source
   and finding it computed something other than what it was called.
2. **A unit conversion is part of the mapping, not a correction to the number.** VascX reports
   calibre in millimetres and the canonical name says microns; the adapter converts. PVBM computes
   Hubbard's equivalents from pixel widths where the constants are fitted in microns; that is a
   *defect of the implementation* and the benchmark reports the number rather than fixing it. **The
   difference between those two cases is the whole of this section**, and each mapping has to say
   which it is.

   *Implemented 2026-09-30 as one rule in one place:* every adapter reports pixels, and
   `canonical.from_pixels` raises them to the power of length the name declares. VascX, the only
   upstream that hands back a physical length, converts *towards* pixels so that it lines up with
   its five siblings. The shapes' ground truth is built by the same rule, so the two sides of
   every comparison cannot disagree about the conversion.
3. **A withdrawn mapping is a finding, not an omission**, and is recorded as such with its date.
4. **The evidence stores the implementation's own names**, and the mapping is applied in the
   analysis. *Fact:* this is why the three withdrawals above cost a notebook re-run and **no
   re-measurement** — confirmed in practice, not merely argued.

---

## 4. What an implementation of one has to get right

Chapters 2 and 3 are about names. This one is about the numbers, and it is where most of the
measurement in this plan has gone.

### 4.1 Vessel tracing — the implementation's, and documented

**Decided, 2026-09-30.** A canonical definition **does not specify how the centreline is obtained.**
Tracing is engineering rather than a published measurement — `docs/biomarkers/vessel-tracing.md`
says so already, and there is no paper to cite for it. Fixing it in a definition would make the
benchmark a conformance test for one algorithm and forbid a better skeletoniser.

What is required instead is that **every implementation documents its tracing**, on its project
page, in the terms that page already sets out: how the centreline is extracted, how junctions are
treated, how points are put into path order, and whether the centreline is smoothed or branches
rejoined before derivatives are taken.

**The one decision that does not stay with the implementation is what the measurement is taken
over**, and 2.1.2 moves that into the name rather than into the tracer. Segments and whole vessels
are two biomarkers; how you find either is yours.

What this leaves genuinely open, and what the benchmark is for measuring rather than legislating:

- **Spur pruning.** Skeletonising sharp corners leaves spurs — the drawn Koch curve carries four to
  six endpoints where the curve has two. Pruning shortens the arc and lowers tortuosity, and the
  ordering of the six implementations on that shape is partly an ordering of how aggressively each
  prunes.
- **Inclusion thresholds.** PVBM's current class requires a subgraph of at least 50 pixels beginning
  within `100 + radius` of the disc. That is why `disjoint` returns zeros for it — a definitional
  consequence of a disc-anchored walk, not a failure.
- **The centreline algorithm itself**, worth about 4–5% on arc length from staircase inflation alone
  on shapes drawn here.

**Fact, and the reason documentation is not a soft requirement:** PVBM and OCULAR return *identical*
numbers on every shared biomarker once their recursion limits match. Everything this atlas had been
reporting as a difference between two programs was one interpreter setting that neither had written
down. A tracing difference that nobody documents is the same failure waiting to happen with more
digits.

### 4.2 Curvature, smoothing, and the scale it is estimated at

**Fact, measured, and the most consequential finding in this document.**

**Why the τ family splits three ways.** Curvature κ is one over a radius, so it carries **1/L**; the
arc element `ds` carries **L**. τ2 = ∫κ ds is dimensionless because the single κ cancels exactly —
it is the total turning angle, and the 90° arc returns π/2. τ3 = ∫κ² ds leaves one κ uncancelled, so
it is 1/L. τ4 and τ6 are τ2 over a length; τ5 and τ7 are τ3 over a length. **τ4 is literally the
curvature**: for an arc of radius R, τ4 = 1/R exactly.

**Physical units are necessary and not sufficient.** The same arc at four grids, all values
converted to microns:

| | τ1 | τ2 *(already dimensionless)* | τ3 | τ4 |
| --- | --- | --- | --- | --- |
| curvature from adjacent pixels | 1.1% | **145%** | **241%** | **145%** |
| curvature over a fixed 150 µm window | 0.8% | 12% | 16% | 12% |

**τ2 is the proof that this is not a units problem**: it is dimensionless, there is nothing to
convert, and it still moves by 145%. A skeleton is a staircase, and curvature from adjacent pixels
measures the staircase.

**The estimator matters more than the window.** Same paths, same shapes, same grids, each method at
its best setting, worst case over all seven metrics:

| Estimator | Its scale | Worst error |
| --- | --- | --- |
| Boxcar + finite differences | — | 34.5% |
| Least-squares cubic spline | knots every 928 µm | 8.1% |
| **Angle regression — κ = dα/ds by least squares, Hart's own recipe** | **σ = 45 µm** | **6.9%** |

A boxcar cannot bring τ3, τ5 or τ7 within 10% at any window; the spline takes τ3 from 25.3% to 1.4%.
**Hart's published recipe beats the obvious numerical one**, because it takes a *first* derivative
of the tangent angle rather than a second derivative of position.

**And a pixel-parameterised estimator is the defect this plan exists to catch.** Pheno AutoMorph's
implementation sets σ in **pixels**:

| | 1024 px | 2048 px | 4096 px |
| --- | --- | --- | --- |
| σ = 6 px, as shipped | 10.4% | **4.5%** | **40.4%** |
| σ = 45 µm | 6.9% | 6.9% | 6.9% |

Best in the table on the grid it was tuned on, six times worse one doubling later. Converting two
constants to microns makes the error identical at all three resolutions to the decimal.

**The scale is not a length either.** Sweeping sinusoids and arcs over an eightyfold range of
curvature, the optimum σ rises **sub-linearly** with the feature being measured, and one law fits
both shapes across nine points with no deviation over 17%:

> **σ ≈ 0.32 · R_eff^0.68**, where `R_eff = 1/τ4` is the effective radius of curvature.

So a fixed σ — in pixels *or* in microns — is choosing which vessels it measures correctly. At
retinal feature scales of 1 mm and up, angle regression holds all seven metrics to within 9%; at
feature scales under the vessel's own width, nothing works and the drawing does not carry the
geometry either.

**Decided, for chapter 2's requirements:** a curvature-family entry records **the estimator** and
**how its scale is set**, and a scale recorded without its estimator records nothing.

### 4.3 What the benchmark must fingerprint

**Decided**, from experience. A number an implementation acts on and does not declare is a number a
stale result can outlive. The recursion limit of 4.1 is the worked example: raising it turned 32
exceptions into measurements, so it is declared and fingerprinted, and a score taken at one limit
is not mistaken for one taken at another.

---

## 5. `fundus-biomarkers` — a reference implementation

**Decided, 2026-09-29.** It exists, it is **proprietary**, and it lives at
`git@github.com:PhenoAI/fundus-biomarkers.git`. Four decisions settle what that means here.

### 5.1 What it is for

Chapters 2 and 4 describe biomarkers precisely enough to implement. A reference implementation is
what turns that description into something testable: **the definition, executable**, against which a
catalogued project's answer is a measurable distance rather than a matter of reading its source. It
also settles chapter 3's conversion rules in the only way that really settles them, by being the
thing both sides convert *to*.

### 5.2 The scope boundary holds, because nothing is shipped from here

`CLAUDE.md` §2.1 rules out *"shipping another segmentation model, biomarker calculation, or
pipeline"* without exception, and this plan previously raised that as blocking. It is resolved
without amending anything: **the library is a separate repository that this atlas catalogues and
benchmarks like any other project.** An adapter in `src/biomarkers/`, a page in `docs/projects/`, a
column in the results table beside PVBM and VascX, and no special standing anywhere.

That is the more honest design as well as the compliant one. Our implementation is measured by the
same benchmark, on the same shapes, against the same derived ground truth, with the same
tolerances — and an implementation that marks its own homework is worth very little.

### 5.3 Definitions flow one way

**The public atlas is the source of truth for what a biomarker is; the private library implements
it.** Names, definitions, units, the papers, the region rule and the estimation requirements are all
decided here, in the open, and consumed there.

The rule that keeps that from eroding: **a definition that exists only in the private library is a
definition that does not exist.** If implementing something reveals that the definition is
ambiguous — and chapter 4 suggests it will, repeatedly — the fix belongs in this repository, where
anybody can read it and disagree with it.

### 5.4 Nothing proprietary enters this repository

No algorithm, no constant, no source. What may appear here is what appears for any catalogued
project: that it exists, what it claims to compute, the commit a result is attributable to, and what
it measured.

Two mechanisms keep that true rather than merely intended:

- **It is cloned, never installed.** `source.Checkout` against the SSH remote, into the git-ignored
  `.atlas_code/`, per `add-upstream` §2. It is deliberately **not** a dependency in
  `pyproject.toml`, so the private code never enters the public dependency graph and a clone of this
  repository without access to that remote is a repository that cannot **re-run** one benchmark
  column — though it can read every number that column produced, per 5.6.
- **What the adapter declares is a digest, not the constants.** See 5.5, which is the part of this
  that is not yet solved.

### 5.5 The fingerprint is the commit id

**Decided, 2026-09-30.** The adapter declares `fundus-biomarkers`' **commit**, and the benchmark
fingerprints that, exactly as it does for every other cloned upstream.

`add-model` §7.4 and `build-benchmark` §5 both require that every number an adapter acts on is
declared, because a constant that changes a result and is not fingerprinted is one a stale score
can outlive — and chapter 4 is that rule at its strongest, since the estimator and its scale move
τ3 by a factor of eighteen. For a library whose constants live **in its code**, the commit id
covers all of them at once: change any constant, change the commit, invalidate the scores. It
publishes nothing, and it needs no cooperation from the library beyond being a git repository.

**The one gap, recorded so it is not discovered later.** A commit id covers what is *baked in*, not
what is *passed in*. Any setting the adapter chooses at run time — a scale, a smoothing window, a
region — is invisible to it, and is exactly the kind of number chapter 4 shows changes everything.
So the rule that goes with this decision: **the adapter passes as little as possible**, and whatever
it does pass it declares as a number, publicly, because a parameter this repository chooses is this
repository's to publish. A constant that must stay private belongs inside the library and inside the
commit.

### 5.6 The results are published in full, like everybody else's

**Decided, 2026-09-29.** The **implementation** is private; the **measurements are not**. The
per-image evidence goes into `results/biomarker-synthetic/fundus-biomarkers/` exactly as every
other implementation's does, the column sits in the same tables, and the comparison against PVBM,
OCULAR, the three AutoMorph projects and VascX is the point of measuring it at all. No exception to
`build-benchmark` §6 is needed and none is taken.

That is the arrangement to aim for and not a concession: a proprietary implementation whose numbers
nobody may see is a claim, and one whose every number is on the table alongside its competitors' is
a measurement.

**One fact still needs stating on the page, and it is narrower than "unreproducible".** A reader can
check every number we publish, every comparison drawn from it and every conclusion on the results
page — all of that is as open as the rest. What they cannot do without access to the remote is
**re-derive the measurements from the masks**, because they cannot run the library. So the column
is marked the way access restrictions are marked elsewhere in this atlas — several catalogued
datasets need a signed agreement and several model weights need registration — and for the same
reason: it tells a reader what they would need in order to check it themselves, and nothing more.

What the atlas must not do is present that column as **independently verified** when the
verification and the implementation share an owner. That is not about disclosure, which is total;
it is the same rule that makes this repository refuse to let a model mark its own homework.

### 5.7 What it must do

- Implement each canonical entry **to the definition in this repository**, citing the paper.
- Take a physical scale and refuse to guess one.
- Declare its estimator and how its scale is set, per 4.2, and expose the digest of 5.5.
- Carry no segmentation model: masks in, numbers out.
- Be measured by the synthetic benchmark **before** anybody's results are compared against it.

## 6. Decisions

- ~~**6.1 The region rule**~~ **Decided 2026-09-29: its own optional name part, defaulting to the
  field of view** (2.1, 2.4). What remains is 6.1a and 6.1b below.
- ~~**6.1a Does a family declare a default region, or may it require one?**~~ **Decided 2026-09-30:
  a family declares which parts apply and what they default to, and may require one** (2.1.1). The
  equivalents require a region; three families carry no structure at all.
- ~~**6.1b What does each region name denote?**~~ **Decided 2026-09-30: they are defined in the
  literature and we document them** (2.4.1) — a reference page, `regions-of-interest.md`, stating
  each zone with its bounds and its paper, both unit conventions, `fov`, and the non-standard
  regions implementations use.

**None remain open.** What is left is the work in chapter 7.
- ~~**6.2 Is a defining paper mandatory?**~~ **Decided 2026-09-30: no, but the alternative is
  heavier, not lighter** (2.3).
- ~~**6.3 Do we keep names nothing implements?**~~ **Decided 2026-09-30: yes, where a paper names
  or recommends them** (2.3).
- ~~**6.4 How tightly does a definition constrain tracing?**~~ **Decided 2026-09-30: not at all —
  it is the implementation's, and must be documented** (4.1). The one decision that *is*
  definitional, segment against whole vessel, moves into the name instead (2.1.2).
- ~~**6.4a What is a start-to-end pair?**~~ **Decided 2026-09-30: root-to-tip, as PVBM traces it**
  (2.1.2) — one vessel per leaf, and the `vessel-` forms therefore require the optic disc.
- ~~**6.5 How a proprietary library is fingerprinted?**~~ **Decided 2026-09-30: by its commit id**
  (5.5).
- ~~**6.6 Is the per-image evidence published for that column?**~~ **Decided 2026-09-29: yes, in
  full, in the same tables as everybody else** (5.6). What remains is wording, not policy — the
  column says what access a reader needs to re-run it, and the atlas never calls it independently
  verified.

## 7. Order of work

**Decided.** Once chapter 6 is settled, **the documentation changes before any code does.** The
vocabulary is a set of claims about what quantities mean; writing those claims into Python before
they have been checked against the literature only means discovering they were wrong with an
adapter and a benchmark run already built on top of them.

### 7.1 First, the documentation

1. **Redefine the families.** `docs/biomarkers/` currently has fifteen pages, and the chapter 2
   naming makes `family` the first part of every name — so the pages *are* the families, and the
   split between them has to be right before anything maps onto it. Five pages have no canonical
   name at all today; one, the vascular curvature index, should never get one and needs the page to
   say why.
2. **Verify every definition against its paper**, and write the long form: the formula, **what it
   is measured over** per 2.1.2, and enough that two people implementing it separately would agree.
   Each project page gains its tracing description, per 4.1. This is where
   the withdrawals of 3.2 would have been caught before they cost a benchmark run.
3. **Fix the units on every page** to microns per 2.2, and mark which biomarkers a dataset without a
   scale cannot support at all.
4. **Write `docs/biomarkers/regions-of-interest.md`** per 2.4.1 — each zone with its bounds checked
   against the ARIC papers, both unit conventions stated so the factor-of-two trap cannot be walked
   into, `fov`, and the non-standard regions implementations use. Record which families require a
   region rather than defaulting. **Record which families have a `vessel-`
   form**, per 2.1.2, and that those require the disc. Revisit `junction-counts` while there: a
   rooted pair of names — free ends against tips — may recover the PVBM and OCULAR mappings this
   atlas withdrew.
5. **Build the mapping tables**: canonical name → each implementation's own column, **with the
   conversion rule beside it**, for PVBM, OCULAR, the three AutoMorph projects, VascX and
   `fundus-biomarkers`. Each row must now also say whether the implementation's column is the
   **segment** or the **whole-vessel** form of 2.1.2 — which requires reading its tracing, and is
   where several of today's mappings will turn out to be the wrong one of the two. A conversion is a unit change or nothing; where an implementation's number
   is *wrong* rather than differently scaled — Hubbard's constants on pixel widths — the table says
   so and the benchmark still reports what it returned.
6. **Say what evidence a new entry needs**, per 1.3, so the list grows by decision.

The output of this stage is prose a person can disagree with, and every disagreement is cheaper
here than it is in step 7.2.

### 7.2 Then the code

7. ✅ **Done 2026-09-30.** Extend `canonical.py` from a name→sentence map to a name→record
   carrying family, biomarker, structure, region, statistic, unit, the paper and the whole-vessel
   flag — and **add the `vessel-` variants of 2.1.2** for every family where the distinction
   arises. `check()` stays the single gate, and gained the disjointness check of 2.1.1.
   *34 biomarkers; 551 names once structure, region and statistic are expanded.*
8. ✅ **Done 2026-09-30.** Re-map all six adapters. The statistic turned out to be the part that
   mattered: reading the code showed AutoMorph and AutoMorphalyzer divide by vessel count while
   AutoMorphClass weights by length, so `length-weighted` was added to the vocabulary and names
   three implementations' columns plus VascX's `lw_` family and OCULAR's third aggregation.
   *One mapping was made on a name and withdrawn on the code — VascX's sparsity, which is
   normalised by the disc-fovea distance and is not a length at all.*
9. ✅ **Done 2026-09-30.** Restate the synthetic shapes' ground truth in microns, per 2.2. The
   conversion is driven by each name's own declared unit, so a biomarker cannot be converted one
   way and declared another. *It found two defects: Grisan's density is an inverse length, and
   Hubbard's equivalent was being converted to microns twice.*
10. ✅ **Done 2026-09-30.** Teach the shapes to settle the new names — 271 of the 280 whole-field
    names, the remaining nine needing an optic cup, a fovea or the temporal arcades, which these
    shapes do not draw — and **turn 4.2 into a test**:
    `test_one_retina_photographed_at_two_resolutions_gives_one_set_of_numbers` asserts every
    settled value over 1024/10 µm against 2048/5 µm. That test is what stops a name silently
    returning to pixels.
11. ✅ **Done 2026-09-30.** Regenerate `BIOMARKERS.md`, `BIOMARKER-NAMES.md` and the benchmark's
    configuration page **from the record**, so that after this the code and the prose cannot
    disagree again. `src/biomarkers/pages.py` renders the family summary and the units table into
    marked blocks with `python -m biomarkers.pages`, reusing the benchmark pages' machinery.

    *What could not be generated, and what was done instead.* The ✅ and ⚠️ marks against each
    project are judgements a person makes from reading somebody's source; rendering them would be
    inventing them. So they stay hand-written and are **tested** against the record in both
    directions: every biomarker named in those tables must exist in the vocabulary, and every
    biomarker in the vocabulary must have a row. The second direction caught two abbreviated rows
    — `hart-tau2 … tau7` and `multifractal-d0/d1/d2` — which hid that τ3 is in 1/µm and τ5 in
    1/µm², the very distinction the catalogue exists to make. Generating the count caught another:
    the density family was described as ten biomarkers and enumerated as nine.
12. ✅ **Done 2026-09-30.** Re-run the analysis notebook. **No re-measurement** — 3.2 rule 4,
    confirmed in practice: not one stored value in `results/` changed.

Every table in chapters 2 and 4 comes from a one-off script rather than from anything committed,
which is a weakness in this document: nobody can re-run them. Step 10 is where that is repaid.

---

**Written:** 2026-09-25. **Reworked into chapters:** 2026-09-28. **Chapter 5 settled:** 2026-09-29. **Naming, units and the order of work:** 2026-09-29. **Family overrides, scale, tracing, regions — every open question closed:** 2026-09-30. **Chapter 7.2 carried out but for step 11:** 2026-09-30.
