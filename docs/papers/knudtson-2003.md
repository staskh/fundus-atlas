# Knudtson 2003

A revision of Hubbard's central retinal equivalents that stops the summary changing with how many
vessels the software happened to find, and that can be computed on pixel widths as honestly as on
microns. Most catalogued pipelines that report CRAE or CRVE are running this version, even when
they still say "Hubbard".

## 1. Citation

| | |
| --- | --- |
| Title | Revised formulas for summarizing retinal vessel diameters |
| Authors | Knudtson MD, Lee KE, Hubbard LD, Wong TY, Klein R, Klein BEK |
| Venue | Current Eye Research 2003;27(3):143–149 |
| DOI | [10.1076/ceyr.27.3.143.16049](https://doi.org/10.1076/ceyr.27.3.143.16049) |
| Open copy | none established |
| PMID | [14562179](https://pubmed.ncbi.nlm.nih.gov/14562179/) |
| Code | none established |
| Dataset | none established — Beaver Dam photographs are not a public download with this paper |
| Other | none established |

## 2. What it is about

Hubbard's pairing formulas, used in ARIC, had two practical faults: they moved when more or fewer
branches were measured, and the constants were not independent of the photograph's scale. Knudtson
and colleagues fitted a simpler pairing — a constant times the root of the sum of squares — on
vessel measurements from 44 young adults without hypertension or diabetes, then compared the old and
new summaries on thousands of Beaver Dam Eye Study photographs. They also fixed the count at the
six largest arterioles and six largest venules, so a missed small branch no longer changes the
number.

## 3. Why it is in this atlas

- **Kind:** definition
- It is the other definition of record for [central retinal equivalents](../biomarkers/central-retinal-equivalents.md).
  AutoMorphalyzer dropped Hubbard and kept only this one; VascX's "Hubbard-style" recursion uses
  these constants. A CRAE without the variant named is unusable; this paper is why.

## 4. What the authors claim

| Claim | Sample | Reported in |
| --- | --- | --- |
| The revised formulas correlate highly with Parr–Hubbard (Pearson 0.94 to 0.98) | 4,926 Beaver Dam Eye Study baseline photographs | this paper |
| Parr–Hubbard arteriolar and venular calibre rose as more vessels were measured; the revised formulas did not | Same Beaver Dam sample | this paper |
| The revision is independent of image scale, more robust to vessel count, and easier to implement | Authors' argument from the 44-person fit and the Beaver Dam comparison | this paper |

These are the authors' measurements and arguments. This atlas's own comparisons are separate.

## 5. Relates to

| Entry | Relationship |
| --- | --- |
| [Central retinal equivalents](../biomarkers/central-retinal-equivalents.md) | Defines the Knudtson variant (six largest vessels; 0.88 and 0.95 constants) |
| [AVR](../biomarkers/avr.md) | The ratio of those two equivalents |
| [Hubbard 1999](hubbard-1999.md) | The formulas this paper revises |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | Implements Knudtson only — its authors removed Hubbard |

## 6. Notes

- Being purely multiplicative, Knudtson **is** scale-invariant: it can be computed on pixel widths
  and converted afterwards. Hubbard cannot. That distinction is why two columns that both say "CRAE"
  are not the same quantity.
- An implementation that keeps a number of vessels other than six has changed the measurement, even
  if it uses these constants.

---

**Links last checked:** 2026-09-21
