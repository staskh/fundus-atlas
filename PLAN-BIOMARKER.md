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

**Decided.** Four parts:

```
family / biomarker / structure / [statistic]
```

| Part | What it is | Examples |
| --- | --- | --- |
| `family` | the page in `docs/biomarkers/`, the kind of thing being measured | `tortuosity`, `vessel-calibre`, `fractal-dimension` |
| `biomarker` | **the definition, not the word** — which formula | `hart-tau1`, `grisan-density`, `knudtson` |
| `structure` | what it was measured over | `artery`, `vein`, `vessels`, `both` |
| `statistic` | *optional* — how per-segment values were pooled | `mean`, `median`, `std`, `length-weighted` |

**The statistic is optional and that is deliberate.** Most biomarkers are one number per image and
carry none. Where an implementation reports the mean *and* the median *and* the standard deviation
of the same per-segment quantity — PVBM's branching angle does, OCULAR's tortuosity does — those
are three different numbers and the vocabulary has to say which is which. Omitting the part when
there is nothing to pool keeps the common case short.

**Region of interest is deliberately not in the name.** See 2.4, which is the hardest question in
this chapter.

This replaces the current three-part `biomarker/variant/structure`: `family` is today's
`biomarker`, `biomarker` is today's `variant`, and `statistic` is new.

### 2.2 Units, and the thirty names that do not carry one

**Fact, measured.** The same physical retina was built at 1024 px / 10 µm per pixel and at
2048 px / 5 µm per pixel — one eye, two cameras — and every theoretical value compared:

| Behaviour | Count | Names |
| --- | --- | --- |
| **Scale-free** (×1) | 40 | τ1, τ2, Grisan density, inflection count, all fractal dimensions, all junction counts, densities, AVR, bifurcation angle, **Hubbard** equivalents |
| **Length in pixels** (×2) | 15 | calibre mean and median, skeleton length, sparsity, **Knudtson** equivalents |
| **Inverse length** (×0.5) | 8 | τ3, τ4, τ6, spline mean curvature |
| **Inverse area** (×0.25) | 4 | τ5, τ7 |
| **Area in pixels²** (×4) | 3 | vessel area |

**Thirty of seventy give a different answer for the same eye**, and nothing in the name or the
stored evidence says which unit a column is in. Two consequences that make this chapter's
requirement non-negotiable:

- **Hubbard and Knudtson equivalents come out in different units.** Hubbard's constants are fitted
  in microns so an implementation must convert, and the answer is physical. Knudtson's formula is
  purely multiplicative so it returns whatever the widths were — pixels. *Two variants, one family,
  incomparable units.*
- **The τ family spans three dimensions.** τ1 and τ2 are dimensionless, τ3/τ4/τ6 are inverse
  lengths, τ5/τ7 are inverse areas. "Tortuosity" as a column heading is not one kind of quantity.

**Decided:** every entry declares a unit, and `1` (dimensionless) is a unit rather than a blank.

### 2.3 The definition

**Decided.** Every entry carries, and a benchmark may refuse an entry that does not:

| Field | Why |
| --- | --- |
| **Short definition** | one line, for a table |
| **Long definition** | enough that two people implementing it separately would agree — the formula, and what it is computed over |
| **Defining paper** | the primary goal of this plan; see the open question in 6.2 |
| **Units** | 2.2 |
| **Estimation requirements** | where the answer depends on how a derivative is taken — chapter 4 |

**Fact:** five biomarker pages have no canonical name at all today — `cup-to-disc-ratio`,
`disc-fovea-distance`, `temporal-angle`, `vascular-curvature-index`, `vessel-tracing` — and two
documented biomarkers have no defining paper: vascular density (`No single origin`) and cup-to-disc
ratio (`Clinical measure`). One, the vascular curvature index, is **proprietary and uncomputable**:
its paper declines to give a formula. It should never get a canonical name, and the vocabulary
should be able to record *why* rather than being silently short of it.

### 2.4 Region of interest — the hard case

**Open.** This is where the naming decision of 2.1 has to be paid for.

**Fact:** 44 of the 73 implementation columns the catalogue cannot name are quantities it *already*
names, measured over a region it cannot express. AutoMorphalyzer reports most quantities three
times — `@whole`, `@B`, `@C` — and VascX reports several over a disc-centred circle at 7/6 disc
radii. Zones B and C are the conventional annuli from the ARIC literature, so this is the field's
standard practice rather than an implementation's quirk.

**The difficulty is that ROI is sometimes part of the definition and sometimes a choice**, and the
two need opposite treatment:

| Family | How the region enters | Consequence |
| --- | --- | --- |
| Central retinal equivalents, AVR | **Definitional.** CRAE *is* the equivalent over zone B; the same formula over zone C is a different published quantity | a name that omits it is ambiguous |
| Calibre, tortuosity, density, fractal dimension | **A choice.** The same measurement restricted to a region | a name that includes it multiplies by three |
| Temporal angle, disc–fovea distance | **Anchored, not regional.** Defined relative to landmarks, not over an area | region does not apply |

Three candidate rules, and the plan needs one:

1. **Region in the name for every family.** Explicit and self-describing; multiplies the list by the
   number of regions and most combinations are never computed.
2. **Region beside the name, as a required field on every measurement.** Names stay short; a column
   heading no longer identifies a measurement on its own, which is what 1.1 wanted from it.
3. **Region in the `biomarker` part where it is definitional, beside the name where it is a
   choice.** `central-retinal-equivalents/knudtson-zone-b/artery` is one entry and
   `vessel-calibre/mean-width/artery` measured over zone B is one entry with a field. Follows the
   distinction above and asks a person to make a judgement per family.

My reading is (3): it is the only one that treats CRAE@B and CRAE@C as the different published
quantities they are, without tripling the families where the region is genuinely a knob. It costs a
per-family decision, which chapter 3 has to make anyway.

---

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

### 3.2 Conversion rules

**Open.** Mapping an implementation's column onto a canonical name is **a claim that has to be
testable**, and this repository has already been wrong about several:

- `squared_curvature_tortuosity` was mapped to Hart τ3 until a shape showed it off by five orders of
  magnitude — it squares nothing. *Withdrawn.*
- `median_branching_angle` was mapped to the angle between daughters until a shape showed it medians
  every pairwise angle at every junction, trunk included. *Withdrawn.*
- `endpoints` was mapped to the catalogued endpoint count until PVBM's replacement class began
  calling the end at the disc a *start point*. *Withdrawn for PVBM and OCULAR both.*

So the rules a mapping must satisfy:

1. **Read from the code, not the name.** Every withdrawal above came from reading somebody's source
   and finding it computed something other than what it was called.
2. **A unit conversion is part of the mapping, not a correction to the number.** VascX reports
   calibre in millimetres and the canonical name says microns; the adapter converts. PVBM computes
   Hubbard's equivalents from pixel widths where the constants are fitted in microns; that is a
   *defect of the implementation* and the benchmark reports the number rather than fixing it. **The
   difference between those two cases is the whole of this section**, and each mapping has to say
   which it is.
3. **A withdrawn mapping is a finding, not an omission**, and is recorded as such with its date.
4. **The evidence stores the implementation's own names**, and the mapping is applied in the
   analysis. *Fact:* this is why the three withdrawals above cost a notebook re-run and **no
   re-measurement** — confirmed in practice, not merely argued.

---

## 4. What an implementation of one has to get right

Chapters 2 and 3 are about names. This one is about the numbers, and it is where most of the
measurement in this plan has gone.

### 4.1 Vessel tracing

**Open.** Every biomarker beyond area and density is computed from a **centreline**, and nothing in
the catalogue currently specifies how that centreline is obtained. What is known:

- Skeletonisation of a thick vessel leaves **spurs** at every sharp corner. The drawn Koch curve
  carries four to six endpoints where the curve has two, which is why the catalogued endpoint count
  is unmeasurable on it.
- **Pruning strategy changes tortuosity.** On the Koch shape every implementation undershoots the
  drawn arc-to-chord ratio, and the ordering between them is partly an ordering of how aggressively
  each prunes.
- PVBM's walk is **recursive, one Python frame per skeleton pixel**, and raises on a dense tree at
  CPython's default limit. OCULAR's fork sets 5000 and does not. *Fact:* with the limits equalised
  the two return **identical numbers on every shared biomarker** — so that setting, not the code,
  was the whole of the difference this atlas had been reporting between them.

A canonical definition that does not constrain tracing is not a definition. What it should
constrain, and how tightly, is open.

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
  repository without access to that remote is a repository that cannot run one benchmark column —
  which is the honest failure rather than a confusing one.
- **What the adapter declares is a digest, not the constants.** See 5.5, which is the part of this
  that is not yet solved.

### 5.5 The fingerprint problem, and the proposed way round it

**Open.** `add-model` §7.4 and `build-benchmark` §5 both require that *every number an adapter acts
on is declared as a number*, because a constant that changes a result and is not fingerprinted is
one a stale score can outlive. Chapter 4 is the argument for that rule at its strongest: the
estimator and its scale move τ3 by a factor of eighteen, and PVBM's recursion limit turned 32
exceptions into measurements.

**Those are exactly the constants a proprietary library would not publish.** So the fingerprint has
a hole precisely where it matters most.

Proposed: the library exposes a **configuration digest** — a hash over everything it acts on,
computed inside the library — which the adapter declares and the benchmark fingerprints in place of
the values. Any change to any constant changes the digest and invalidates the stored scores, which
is the whole guarantee the rule exists for, and nothing is published. It costs one thing worth
naming: a reader can see *that* the configuration changed and not *what* changed, so the results
page must carry the digest and say which runs share it.

### 5.6 Two things to decide before the first run lands

**Open**, and both are Stas's call rather than mine.

- **A results column nobody outside can reproduce.** Every other column in this benchmark can be
  checked by anyone who downloads the code. This one cannot. That is not a reason to leave it out —
  the atlas already catalogues datasets behind signed agreements — but it **is** a fact that changes
  how the column should be read, in the way a contamination mark is. It should be marked on the
  project page, in the results page, and in the index, and the atlas must never present that column
  as independently verified.
- **Whether the per-image evidence is published at all.** `results/` is committed and public, and
  for this column it would be the library's exact output on 36 renderings for every biomarker it
  computes. That is a great deal of information about an algorithm's behaviour. Publishing it is
  consistent with everything else here; withholding it while publishing the summary is defensible
  and would be the first exception to `build-benchmark` §6. Decide before the first run, not after.

### 5.7 What it must do

- Implement each canonical entry **to the definition in this repository**, citing the paper.
- Take a physical scale and refuse to guess one.
- Declare its estimator and how its scale is set, per 4.2, and expose the digest of 5.5.
- Carry no segmentation model: masks in, numbers out.
- Be measured by the synthetic benchmark **before** anybody's results are compared against it.

## 6. Open decisions

- **6.1 The region rule** (2.4). Three candidates; my reading is the third, region in the
  `biomarker` part where it is definitional and beside the name where it is a choice.
- **6.2 Is a defining paper mandatory** (2.3)? Making it so is this plan's primary goal and would
  block vascular density and cup-to-disc ratio, which are real measurements with no single origin.
  The alternative is a required field whose value may be `no single origin`.
- **6.3 Do we keep names nothing implements?** 53 of 90 are claimed by no implementation. Some are
  right to keep — τ4 and τ5 are in Hart's paper whether or not anybody computes them — and some may
  be clutter. A rule is needed, not a case-by-case purge.
- **6.4 How tightly does a definition constrain tracing** (4.1)? A definition that leaves the
  centreline open is not a definition; one that fixes it forbids a better skeletoniser.
- **6.5 How a proprietary library is fingerprinted** (5.5). The configuration-digest proposal keeps
  the guarantee without publishing the constants; it needs the library to cooperate.
- **6.6 Is the per-image evidence published for that column** (5.6)? And how the column is marked so
  that nobody reads it as independently verified.

## 7. Order of work

Once 6.1 and 6.2 are settled — the rest can follow later.

1. Extend `canonical.py` from a name→sentence map to a name→record carrying family, biomarker,
   structure, optional statistic, unit, definitions, paper and estimation requirements. `check()`
   stays the single gate.
2. Add the statistic part and whatever 6.1 decides for region, then re-map all six adapters. **The
   44 region columns and 15 statistic columns of 3.1 are the measure of success.**
3. Make every entry cite a paper, and catalogue the papers still missing.
4. Teach the synthetic shapes to settle the new names — and **turn 4.2 into a test**: one physical
   retina at several grids, every name claiming to be normalised asserted to hold its value across
   them. That test is what stops a name silently returning to pixels.
5. Regenerate `BIOMARKERS.md`, `BIOMARKER-NAMES.md` and the benchmark's configuration page from the
   record, so code and prose cannot disagree again.
6. Re-run the analysis notebook. **No re-measurement** — 3.2 rule 4, confirmed in practice.

Every table in chapters 2 and 4 comes from a one-off script rather than from anything committed,
which is a weakness in this document: nobody can re-run them. Step 4 is where that is repaid.

---

**Written:** 2026-09-25. **Reworked into chapters:** 2026-09-28. **Chapter 5 settled:** 2026-09-29.
