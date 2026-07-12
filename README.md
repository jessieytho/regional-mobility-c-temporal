# Regional Mobility — Study C-Temporal (Post-COVID Travel Rhythm)

Reproducible analysis code and manuscript materials for a TRB 2027 Annual Meeting paper on the
post-pandemic restructuring of travel rhythm in the New York metropolitan region, built entirely on
public MTA / FTA open data.

**Thesis.** Recovery is a regime change, not a return to baseline: the weekday commute peak flattened,
the weekday/weekend gap narrowed, and mode composition shifted. A measured, systemwide service-per-rider
index (NTD vehicle revenue-miles) distinguishes modes that held service ahead of still-depressed demand
(the subway, near 2019) from those that scaled up (LIRR) or lagged (SIR) — each tied to a service lever.

## What's here

```
regional-mobility-c-temporal/
├── README.md                 # this file
├── LICENSE                   # MIT (code). Data are public MTA/FTA open data — see data/README.md
├── CITATION.cff              # citable metadata; drives the Zenodo DOI on release
├── requirements.txt          # Python dependencies (numpy/scipy/pandas/scikit-learn/matplotlib)
├── requirements.lock.txt     # lockfile scaffold (regenerate with pip freeze in the build venv)
├── .env.example              # template for the Socrata app token (never commit the real one)
├── .gitignore
├── data/
│   ├── feeds/                # the three presentation feeds (place the CSVs here; gitignored)
│   └── README.md             # data provenance, source dataset IDs, tiers, attribution
├── src/                      # importable library
│   ├── config.py             # paths, mode lists, baseline years, tier rules (single source of truth)
│   ├── dataio.py             # feed loaders + observed-only filter + unit-firewall guards
│   ├── qa.py                 # assertions: firewall holds, observed-only, supply series derived
│   ├── viz.py                # shared TRB-friendly plotting style (grayscale-safe, embeddable)
│   ├── ntd_vrm.py            # NTD monthly module → systemwide VRM supply (derived_ntd_vrm)
│   └── gtfs_supply.py        # GTFS scheduled-trip counting engine (parked subway-supply fallback)
├── scripts/                  # one script per exhibit; each writes to figures/ or tables/
│   ├── 01_fig1_regime.py ... 07_fig7_supply_demand.py  08_fig4_supply_demand_systemwide.py
│   ├── t1_coverage.py  t2_breaks.py  t3_implications.py
│   ├── check_numbers.py      # regression test: recompute headline stats from the feed
│   └── run_all.py            # QA → every exhibit → check_numbers, end-to-end
├── notebooks/                # NTD-VRM and subway-GTFS probe notebooks (data exploration)
├── figures/                  # generated figures (gitignored; run_all recreates them)
├── tables/                   # generated table data (CSV/TeX)
└── docs/
    ├── methodology_provenance.md   # the cited provenance note (replaces the barred appendix)
    └── data_dictionary.md          # full dictionary (cited from the paper, hosted here)
```

The manuscript (`main070201.tex`, `references.bib`, and its `.md` scaffolding) is distributed as a
**separate archive**, not part of this reproducibility repository.

## Reproduce

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# place the three feed CSVs in data/feeds/ (see data/README.md)
python scripts/run_all.py         # regenerates all figures/ and tables/
```

## Data

Three provenance-tiered presentation feeds derived from MTA Open Data (data.ny.gov) and FTA NTD.
Every value carries a provenance tier (observed vs derived); **all statistics are computed on observed
tiers only**, and units are never summed across `measure_type`. Full provenance in
`docs/methodology_provenance.md`; source dataset IDs in `data/README.md`.

## Scope (locked)

Observed tiers only for statistics · primary recovery baseline **2022** · structural-gap baseline
**2019** (observed for Subways and Bridges & Tunnels only; derived and labeled for the other modes) ·
**Subways** as the across-shock anchor · **SIR-only** supply-vs-demand · calendar covariates inline,
no weather/event stores this pass.
