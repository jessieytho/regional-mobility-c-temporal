# Data

This study uses three provenance-tiered presentation feeds derived from public data. Place the feed
CSVs in `data/feeds/` (they are gitignored; the repo does not redistribute them — cite the deposit):

- `mta_chart_feed_daily.csv` — raw daily series (has `day_of_week`; no `evidence` column — observed
  is read from the `data_basis` prefix)
- `mta_chart_feed_multigrain.csv` — daily/monthly/yearly totals + variation stats (yoy, roll12,
  control bands; populated at monthly grain)
- `mta_chart_feed_daytype.csv` — average ridership per Weekday / Saturday / Sunday-Holiday (monthly,
  yearly)

## Sources (attribution)

- **MTA Open Data** via data.ny.gov (Socrata). Core dataset IDs include: `sayj-mze2` (daily
  ridership/traffic), `xfre-bxip` (monthly), `ebfx-2m7v` / `dtj7-qync` / `rtih-nq26` (B&T),
  `t6yz-b64h` (CRZ entries), `sv2g-g4mz` (regional), `fn46-66ir` (paratransit), `k3aj-27se` (SIR
  scheduled service). Subway hourly `t69i-h2me` for 2017–2019 observed.
- **FTA National Transit Database (NTD)** Monthly Module — pre-MTA-window backfill, reconciled to
  MTA level at the overlap.

## Provenance & tiers

Every value carries a tier collapsed to `evidence` ∈ {observed, derived}. **All statistics are
computed on observed tiers only.** Units are never summed across `measure_type`. Full rules and the
reconciliation metrics are in `../docs/methodology_provenance.md`; the full dictionary is in
`../docs/data_dictionary.md`. These docs are the cited external material that replaces the appendix
(TRB bars appendices).
