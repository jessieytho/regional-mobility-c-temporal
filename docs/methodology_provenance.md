# Methodology & Provenance (cited external note)

> This note is cited from the manuscript and hosted in the repo because TRB Annual Meeting papers may
> not include appendices/supplemental material. Keep the paper's Methods section short and point here
> (and to the Zenodo DOI) for full detail.

## Provenance tiers
- **observed** — `observed_daily` (sayj-mze2, 2020-03→present), `observed_bt_daily` (dtj7, 2016–2020-02),
  `observed_tolling` (ebfx, cross-check), `observed_metrocard` (subway hourly 2017–2019),
  `observed_cordon` (t6yz).
- **derived** — `derived_from_monthly` (xfre), `derived_from_ntd` (NTD, rescaled to MTA level),
  `derived_from_paratransit` (fn46 completed→scheduled ≈1.15), `derived_regional_monthly` (sv2g, flat
  within month), `derived_sir_supply` (k3aj timetable → day-type levels).

## Rules carried into every analysis
1. Statistics on observed tiers only.
2. Never sum across `measure_type` (riders / vehicles / trips / train-trips / cordon entries / VMT).
3. Baselines: primary **2022** (observed-to-observed); structural **2019** observed only for Subways
   and Bridges & Tunnels (derived and labeled elsewhere). Subways is the across-shock anchor.
4. Derived daily shapes are never treated as measurements.

## Reconciliation metrics (to report)
- B&T dtj7 vs xfre annual agreement <1%/yr; rtih reconciled cross-check ≈0.9% (median 1.0086).
- ebfx 2019 launch-year undercount ~11–13% (demoted to cross-check).
- NTD→MTA scale stable for subway/bus/LIRR/MNR; AAR NTD scale unstable (2.9–4.8) → replaced by fn46.
- Day-type disaggregation preserves reported monthly totals exactly.

## Supply tiers (supply-vs-demand comparison, Section 4.3)
Supply series are always **derived** and kept on their own measurement axes (never summed with
riders or with each other); each is read only as an index against a stated base.

- **`derived_lirr_supply`** — LIRR operated train-trips reconstructed from trip-level occupancy
  (dataset 73th-g5ad), electric-multiple-unit fleet only, so held to that scope and used indexed.
  Service `LIRR Operated Trips`; measure_type `operated_service`; unit `train_trips`. Base 2022.
  Steps up ~43% at Grand Central Madison (Feb 2023), matching the operator's published ~41% weekday
  increase (independent of the ridership pipeline — genuine external corroboration).
- **`derived_ntd_vrm`** — operated vehicle revenue-miles from the FTA National Transit Database
  monthly module, giving a uniform systemwide supply measure back to 2002 (reaches 2019, enabling the
  subway structural-gap read). Services `Subways`, `Buses`, `LIRR`, `Metro-North` (these share names
  with rider modes, so the tier is identified by `data_basis`, not `service`). measure_type
  `vehicle_revenue_miles`; unit `car_revenue_miles` (rail) / `vehicle_revenue_miles` (bus). Indexed
  per mode; no rescaling to an agency total. Mode mapping: subway = NYCT Heavy Rail; buses = NYCT
  MB+CB+RB + MTA Bus MB (full bus family, mirrors the bus demand definition); LIRR/MNR = Commuter
  Rail; SIR is a separate NTD reporter and is excluded. **Validation:** the monthly subway series
  annualizes exactly to NTD's audited annual agency profile (2022 Heavy Rail VRM = 338,199,451
  car-mi), confirming parsing/mode-mapping/aggregation. Caveat: monthly module lags ~2 months and
  the most recent months are provisional; VRM is capacity, so for the LIRR (where an operated-trip
  count exists) the trip-count series is the primary reading.

## B&T vehicle-class split (WP-A2, Section 4.4)
`src/bt_vehicle_class.py` + `notebooks/probe_bt_vehicle_class.ipynb` split the observed B&T total
(dtj7-qync, already the B&T backbone) into **passenger cars (toll Class 1) vs all other classes**.
Class 1 = Cars (MTA 2-axle passenger definition) is ~92% of crossings and holds that share across the
recovery (92.4% in 2019 and 2022); cars return to about their 2019 level by 2023 while commercial
classes stay flat — so the road recovery is passenger-driven, not freight. Non-passenger is taken as
`total - class_1` (robust to the class_31–39 range). Caveat: dtj7 changes its class-coding scheme in
**late 2023** (`class_1` empties as cars move to class_31–39), so the class split is reliable through
mid-2023; `coding_break_month()` detects this and `recovery()` auto-truncates to the reliable window.
The crossing **total** (the recovery figure) remains valid to the data cut. This is an analysis
overlay, not a feed row (it decomposes the B&T total and must never be summed with it).

## Paratransit cost context (WP-A3, Section 4.5)
The paratransit deepening draws on two external sources, both cited in the manuscript and neither
merged into the daily feed (dollars are their own measure, firewalled from rider counts):

* **NYS Comptroller Report 12-2024, "MTA's Paratransit Program: An Overview"** — the authoritative,
  internally consistent source for the *total* Access-A-Ride program: ridership above the 2016-19
  average (6.9M -> 7.83M trips), total cost $467M (2016) -> $596M (2019) at ~8.5%/yr vs 3.6% for the
  MTA overall, blended cost per trip ~$57 (2022), by-carrier ~$116 (primary-carrier van) vs ~$40
  (broker) in 2023, and the primary->broker/e-hail trip shift (~68% -> ~23% primary) that held total
  cost near/below 2019 even as ridership passed 2019.
* **NTD TS2.1** (`scripts/paratransit_cost_context.py` -> `data/derived/ntd_nyct_cost_per_trip.csv`)
  — used ONLY for the reliable fixed-route per-trip benchmark: NYCT subway ~$1.92 (2019)/$2.99 (2022)
  and bus ~$3.88/$6.32 per trip, which put AAR an order of magnitude higher.

**Caveat (documented, deliberately not used for AAR totals):** NYCT's NTD "Demand Response" row tracks
essentially the primary-carrier slice; its trips DECLINE (4.83M 2019 -> 2.83M 2024) and cost/trip is
volatile ($107 -> $188 -> $96) because broker/for-hire/e-hail trips are reported outside it. It is
therefore NOT total AAR; paratransit ridership and total-cost claims use the MTA feed and the
Comptroller report, not this NTD row. The raw TS2.1 file (~89 MB) is not committed; the script
documents how to obtain it and the small derived extract is committed for reproducibility.
