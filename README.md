# Fundus Atlas

A public reference for work on colour-fundus photographs — the colour photos taken of the back of
the eye during a routine eye exam.

Many groups have built software that traces the blood vessels and the optic nerve in these photos,
and then turns those tracings into numbers a researcher can use. The papers describing them report
scores that are hard to compare, because each one is measured on different images in different
ways. Fundus Atlas is the map: it records what exists, states what each piece of software claims
against what it actually does, and measures them on the same terms.

## 1. What is catalogued here

1. **Datasets** — the public collections of fundus photographs: who owns each one, the license it
   carries, and what has actually been annotated in it.
2. **Segmentation models** — software that traces anatomy in a photograph: the blood vessels,
   arteries as distinct from veins, and the optic disc and cup.
3. **Biomarker calculations** — methods that turn those tracings into numbers, such as vessel width
   and CRAE.
4. **Projects** — publicly available pipelines that combine several models and calculations into one
   end-to-end run, from photograph to table of numbers.
5. **Comparisons** — the same measurements applied on the same terms, so results from different
   papers and different projects can be read side by side.
6. **Checks** — the quality gates that decide whether a tracing is good enough to trust the numbers
   derived from it.

## 2. What this project is not

It is not another analysis tool, and it does not redistribute anyone else's work.

Every dataset, model, calculation, and pipeline described here stays with its original authors, at
its original source, under its own license. This project adds three things: the map, measurements
taken on common terms, and the citation pointing back to the original. It does not train new
networks, does not host other people's photographs or trained model weights, and does not relicense
anyone's data.

## 3. Reading the comparisons

The comparisons are a lookup table, not a leaderboard. Different pipelines were built for different
images, different populations, and different questions, so the useful question is which one suits a
particular study — not which one wins overall. Where a result depends on a choice we made, that
choice is stated next to the number.

Claims made by an author and measurements made here are always labelled separately.

## 4. Status

Early. The structure and conventions are being set up; catalogue entries are not yet published.

A summary paper is planned, under the working title:

> **Fundus Atlas: a living comparison of retinal segmentation and biomarker pipelines**

## 5. License

- Code in this repository: Apache License 2.0 (see [LICENSE](LICENSE)).
- Write-ups, tables, and comparison results: CC BY 4.0.
- Each catalogued dataset keeps its own license, recorded on that dataset's page.

## 6. Contributing

Contributions are welcome from everyone, and you do not need to be a programmer to make a useful
one. Helpful contributions include:

- A dataset, model, calculation, or pipeline that is missing from the map.
- A correction: a license recorded wrongly, a claim we have misread, a number that does not
  reproduce.
- An omission: something a page should say about a dataset or method and does not.
- A note from experience — where a pipeline worked well, and where it did not.

Open an issue at https://github.com/staskh/fundus-atlas/issues to raise anything, or send a pull
request if you would rather write the change yourself. Corrections are as valuable as additions;
please point out errors freely.

## 7. Sponsorship

This project is proudly sponsored by Pheno.AI .
