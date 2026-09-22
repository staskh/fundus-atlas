---
name: document-benchmark
description: Write and regenerate a benchmark's configuration page — docs/benchmarks/<slug>-docs.md — from the JSON a benchmark reports about itself, including before that benchmark exists. Use when adding or changing a benchmark's configuration page, or when planning a benchmark that has not been built yet.
---

# Documenting how a benchmark is configured

Every benchmark has a page saying **how it is set up and run**: what it asks, what takes part, what
it excludes, how to run it, and what every column of its evidence means. That page is
`docs/benchmarks/<slug>-docs.md`, and this skill owns it.

It does **not** own the other two documents. What came out of a run is `report-benchmark`; the
notebook behind that is `analyse-benchmark`; how to implement the thing in the first place is
`build-benchmark`. Load this one to write or refresh the configuration page, and that one to build
what it describes.

## 1. The page is part generated and part written, and the two never mix

A configuration page has two kinds of content and they are kept physically apart:

- **Generated blocks**, rendered from what the benchmark reports about itself. Nobody edits these
  by hand: an edit is overwritten the next time the page is refreshed, and a test fails first.
- **Written prose**, everything else. Judgement, caveats, why the benchmark exists, what it
  deliberately does not do. Regenerating the page **never touches it**.

The boundary is a marker, not a section number, because numbers shift the moment somebody inserts
a section:

```markdown
<!-- generated: implementations -->
| Implementation | Pinned at | Columns |
| --- | --- | --- |
| [pvbm](../projects/pvbm.md) | `5edb79a` | 32 |
<!-- /generated -->
```

Everything between the two markers belongs to the generator. Everything outside belongs to
whoever wrote it. **A block with no closing marker is an error**, not an invitation to guess.

## 2. `--config` is the contract

A benchmark describes itself as **JSON**, never as prose:

```
python -m benchmarks --benchmark <slug> --config
```

That is the whole interface between a benchmark and its page. It matters because the alternative —
a benchmark yielding finished sentences — is how a page comes to assert things that are not true of
it: prose written for one benchmark gets applied to another, and nothing catches it. A number, a
list or a flag cannot be quietly wrong in the same way.

**It reports what the benchmark *is*, never what a run did.** No results, no counts of what has
been measured, nothing read from `results/`. Three consequences, and each is the point:

- it answers in seconds, so refreshing a page costs nothing and needs no measuring;
- a narrowed invocation cannot change it, so `--dataset straight` cannot rewrite the page as though
  the benchmark had one dataset;
- the page can be written, and checked, before a single number exists.

### 2.1 What the JSON carries

| Key | What it is |
| --- | --- |
| `benchmark`, `title`, `version` | the slug, the heading, and the benchmark's own version |
| `asks` | the question it exists to answer, in a sentence or two |
| `unit_of_work` | what one row of evidence is — a *photograph* for some, a *rendering* for others. Every generated sentence uses this word, so no page calls a drawing a photograph |
| `subjects` | what is measured: the label to call them, and one entry per declared subject with its page, its pin, and whether it took part — **including those that did not**, with the reason |
| `material` | what they are measured on, in the same shape |
| `fingerprint` | what a stored result is invalidated by, as a list. The generated paragraph is built from this, so it cannot claim a benchmark hashes weights it has none of |
| `flags` | **only the flags this benchmark honours**, each with what it does. A flag it accepts and ignores does not appear |
| `columns` | every column of the evidence, and what each means |
| `counts` | the counts each result carries and what each answers |
| `exclusions` | what is left out, and by which rule |
| `reports` | the written pages this benchmark produces |

## 3. Writing the page before the benchmark exists

This is the order to prefer, not a fallback. A page written first is a specification, and one
written afterwards is a description of whatever happened.

1. **Write the prose.** What the benchmark asks, why it is worth asking, what it will not answer.
   This is the part no generator can produce and the part worth thinking about first.
2. **Leave the generated blocks empty**, each with its marker pair and a line saying what will fill
   it. An empty marked block is a legitimate state: it says the benchmark has not been built.
3. **Build it**, following `build-benchmark`, which is where the run, the loaders, the fingerprint
   and the evidence are specified. That skill is the authority on implementation; this one only
   says what the page must end up able to report.
4. **Refresh the page**, which fills every marked block and leaves the prose alone.

A page whose blocks are empty and whose prose is written is exactly what a benchmark proposal looks
like, and it is reviewable before anybody spends a day building it.

## 4. Refreshing

```
python -m benchmarks --benchmark <slug> --docs
```

Reads the page, replaces the contents of every marked block, writes it back. It measures nothing
and needs no results.

**A run never writes this page.** Generating documents from inside a run couples two unrelated
things and costs more than it sounds: parallel runs race on the file, a narrowed run narrows the
page, and refreshing after a code change means either measuring for hours or calling the writer by
hand. The page depends on the code, so the code is what refreshes it.

**Refresh it in the same commit as the change that makes it stale.** A test compares every marked
block against what `--config` currently reports, so a stale page fails the suite rather than
sitting wrong in a public reference.

## 5. What the generator may say, and what it may not

The generator renders **only what the JSON gives it**. It may not assert anything about a benchmark
that the benchmark did not report — not about what it fingerprints, not about what a row of its
evidence is, not about which flags it honours.

This is the rule the page existed without, and it cost: a shared writer once told readers of the
synthetic biomarker benchmark that its fingerprint covered the sha256 of loaded weights, the
patches applied and a store's builder version, that each row was a photograph, and that
`--random-samples` drew from a recorded seed. It has no weights, no patches, no store, no
photographs, and ignores that flag. Every sentence came from prose written for a different
benchmark and applied to this one by a writer that had no way of knowing better.

## 6. Rules

- **6.1** One page per benchmark, `docs/benchmarks/<slug>-docs.md`, owned by this skill.
- **6.2** Generated content lives between markers; everything else is written and never overwritten.
- **6.3** A benchmark describes itself in JSON, never in prose.
- **6.4** The JSON describes the benchmark, never a run: no results, no measured counts.
- **6.5** The generator asserts nothing the JSON did not give it.
- **6.6** A run never writes this page; `--docs` does.
- **6.7** The page is refreshed in the commit that makes it stale, and a test enforces it.
- **6.8** Write the prose and the empty blocks before building the benchmark, not after.
