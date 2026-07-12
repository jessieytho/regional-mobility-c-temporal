# Feeds

Place the three presentation-feed CSVs here before running the pipeline:

    mta_chart_feed_daily.csv
    mta_chart_feed_multigrain.csv
    mta_chart_feed_daytype.csv

These files are gitignored and are **not redistributed** with the repository: they derive from
public MTA Open Data (data.ny.gov) and the FTA National Transit Database. See `../README.md` in the
`data/` folder for the exact source dataset IDs, the provenance tiers, and the reconciliation steps
used to build them.
