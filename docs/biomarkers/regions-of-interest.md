# Regions of interest

**This page is not a biomarker.** It is catalogued here because the `roi` part of every canonical
name points at it, and because the same formula over a different region is a different number —
which is the most common reason two implementations appear to disagree about an eye when they
disagree about an annulus.

## 1. Why a region has to be named

Most vascular biomarkers can be computed over the whole retina or over a ring around the optic
disc, and for the [central retinal equivalents](calibre.md) the ring is not optional — it is part of
what the number means. The ARIC studies fixed a convention; implementations have drifted from it and
from each other.

`family / biomarker / structure / **roi** / [statistic]`, defaulting to `fov`.

## 2. The vocabulary

| Region | What it denotes | Status |
| --- | --- | --- |
| `fov` | the whole lit field of view. **The default** | settled |
| `A` | the innermost annulus of the ARIC convention | bounds to verify — §4 |
| `B` | the annulus the equivalents are conventionally measured over | **1.0 to 1.5 disc diameters from the disc centre**, equivalently 2 to 3 disc radii — corroborated in §3 |
| `C` | the extended annulus, from the inner edge of `B` out to two disc diameters | **0.5 to 2.0 disc diameters from the disc margin**, equivalently 2 to 5 disc radii from the centre — §4 |

A region not on this list is not a canonical region. An implementation measuring over one of its own
keeps that column under its own name and maps to nothing, per
[BIOMARKER-NAMES.md](../BIOMARKER-NAMES.md) §3.

## 3. The factor-of-two trap

**The classical convention is stated in disc *diameters* from the disc *margin*. Much code is
written in disc *radii* from the disc *centre*.** Those differ by a factor of two and an offset, and
nothing in a variable called `zone_b` says which is meant.

Zone B is the one place this repository can state with confidence, because three independent sources
agree:

| Source | How it states zone B |
| --- | --- |
| This repository's synthetic shapes | `ZONE_B_RADII = (2.0, 3.0)`, in **disc radii from the centre** |
| [PVBM](../projects/pvbm.md) | the annulus between **2 and 3 optic disc radii**, built as zone C minus zone B in `DiscSegmenter.post_processing` |
| The classical convention | 0.5 to 1.0 disc **diameters from the margin** — which is the same annulus, since the margin sits at half a diameter from the centre |

**PVBM's own zone names are not the ARIC zone names.** It builds filled circles at 1, 2 and 3 disc
radii and calls them A, B and C, then takes its region of interest as *C minus B* — the annulus from
2 to 3 radii. So PVBM's "zone C" is a disc of radius 3, not an annulus, and the region it actually
measures over is what ARIC calls zone B. Reading its code against the convention without noticing
that produces a confident mis-mapping.

## 4. Zone C, and what is still open

**Zone C is the Extended zone of Cheung et al. 2010**, introduced with the Singapore "I" Vessel
Assessment (SIVA) program to measure calibre over more of the fundus than zone B:

> Measurements were made at the Standard zone (from 0.5 to 1.0 disk diameter) and an Extended zone
> (from 0.5 to 2.0 disk diameter).

— Cheung CY, Hsu W, Lee ML, Wang JJ, Mitchell P, Lau QP, Hamzah H, Ho M, Wong TY. *A new method to
measure peripheral retinal vascular caliber over an extended area.* Microcirculation
2010;17(7):495–503. [doi:10.1111/j.1549-8719.2010.00048.x](https://doi.org/10.1111/j.1549-8719.2010.00048.x),
PMID 21040115. The authors report the Extended zone's CRAE and CRVE as reliable (intraclass
correlation above 0.90) and their associations with blood pressure as the same as the Standard
zone's — their claim, not a measurement here.

**The reference point is inferred, and the inference is stated rather than hidden.** The abstract
gives the bounds in disc diameters without saying from where. Its Standard zone, 0.5 to 1.0 disc
diameter, is zone B, which §3 corroborates as measured **from the disc margin**; the Extended zone
shares its inner bound, so it is read the same way. In both conventions:

| Region | From the disc margin | From the disc centre |
| --- | --- | --- |
| `B` | 0.5 – 1.0 disc diameters | 2 – 3 disc radii |
| `C` | 0.5 – 2.0 disc diameters | 2 – 5 disc radii |

So **zone C contains zone B**: it is not the ring outside it. A number over `C` is a number over a
larger annulus with the same inner edge, which is why it is a different measurement and not a
continuation of the `B` one. An implementation that builds its zone C as a ring outside its zone B
measures something else under the same letter, and its mapping must be read from its code.

**Still open:** zone `A`. Its bounds have not been read out of [Hubbard 1999](../papers/hubbard-1999.md)
or [Knudtson 2003](../papers/knudtson-2003.md), so it stays reserved rather than defined.

## 5. What the implementations actually use

| Project | Region | Notes |
| --- | --- | --- |
| [AutoMorph](../projects/automorph.md), [AutoMorphClass](../projects/automorphclass.md) | whole image | no zone restriction |
| [AutoMorphalyzer](../projects/automorphalyzer.md) | `@whole`, `@B`, `@C` | reports most quantities three times. **`@whole` is not an ARIC zone** — it is the whole image, and maps to `fov` |
| [PVBM](../projects/pvbm.md) | 2–3 disc radii | ARIC zone B under another name, per §3 |
| [VascX](../projects/vascx.md) | several concentric circles between a configurable inner and outer radius | its `crcl_multiplier_1p16666666667` is **7/6 written as a float**, a region the convention does not name. It keeps the largest six vessels per circle in full mode and four in temporal or nasal mode, and takes the median across circles; a circle not wholly inside the retinal mask is discarded |

## 6. Regions and the field of view

A region defined in disc diameters is a **per-eye ruler**: it scales with that eye's disc, so it
needs no camera calibration and is comparable between photographs of different magnification. That
is its advantage over a region in microns.

It is also why a length measured within such a region **cannot then be used to say anything about
disc size** — the disc was the ruler. Where a scale has itself been inferred by assuming a 1800 µm
disc, that circularity is doubled, and the page quoting the number must say so.

---

**Last checked:** 2026-10-05.
