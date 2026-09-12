<!-- The "How to fetch" subsection to add at the end of section 2 of docs/datasets/<slug>.md.
     Number it after the page's existing provenance subsections. -->

### 2.N How to fetch

```bash
uv run python -m datasets.<slug>                          # downloads and builds 512 and 1024
uv run python -m datasets.<slug> --sizes 512,720,1024     # any sizes a model needs
uv run python -m datasets.<slug> --archive ~/<file>.zip   # an archive obtained by hand
```

- **Downloads:** <which layers, how large, which are optional and what is lost by skipping them>.
- **Builds:** <the maps, at `native/` plus each requested size>.
- **Needs a human:** <the account, form or agreement, and what to pass to `--archive`. Omit this
  bullet only for a dataset whose Down column is ✅>.
- **Extra columns:** <each dataset-specific manifest column and what it holds, one line each —
  `age`, `sex`, `iop_mmhg`. Omit this bullet where the fetcher adds none>.
- **Not built:** <any subcollection the fetcher leaves in the archive and why — an ultra-wide-field
  split, per rule 13.7. Omit where it builds everything>.
- **Quality:** <whether `quality` is the dataset's own grade or derived from component ratings, and
  which components those are. Omit where the dataset grades nothing>.
- **Grouping:** <whether `patient` and `visit` are filled and how they were established, so a reader
  knows whether a by-person split is possible. Omit where the dataset publishes no identity>.
- **Peculiarities:** <archive format needing an external tool, a legacy spreadsheet, a palette, files
  to skip, anything a person running it will hit>.
