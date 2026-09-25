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
4. Teach the synthetic shapes to settle the new names, so the benchmark can check them.
5. Regenerate `BIOMARKERS.md`, `BIOMARKER-NAMES.md` and the benchmark's configuration page from the
   record, so code and prose cannot disagree again.
6. Re-run the analysis notebook. **No re-measurement** — see 7.5.

---

**Written:** 2026-09-25
