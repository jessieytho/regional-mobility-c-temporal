# Data Dictionary

Full column-level dictionary for the three feeds. (Stub — expand from the project's
`01_data_dictionary.md`; this is the citable reference hosted with the repo.)

## Feed columns
- **daily**: grain, service, operator, mode_class, measure_type, unit, year, period_start, plot_date,
  day_of_year, month_num, month, day_of_week, is_weekend, is_holiday, day_type, value, data_basis,
  methodology. (`plot_date` = seasonal overlay, all years mapped to 2020; not a real date.)
- **multigrain**: grain, service, mode_class, measure_type, unit, data_basis, period_start,
  period_label, value, evidence, yoy_pct, roll12_mean, roll12_sd, cv, sm_mean, ctrl_lower, ctrl_upper,
  z_seasonal, z_yoy. (variation stats at grain='monthly'.)
- **daytype**: grain, service, mode_class, measure_type, unit, data_basis, day_type, period_start,
  period_label, avg_per_day, n_days, evidence. (grains: monthly, yearly.)

## Services & measures (C-temporal scope)
Rider modes (estimated_ridership/riders): Subways, Buses, LIRR, Metro-North, Staten Island Railway
(+ regional comparators: PATH, NJ Transit Rail/Bus/Demand Response, NYC Ferry, Staten Island Ferry,
Roosevelt Island Tram — level-only). Own axes: Access-A-Ride (scheduled_trips/trips), Bridges &
Tunnels (vehicle_traffic/vehicles), SIR Scheduled Trips (scheduled_service/train_trips, derived).
Study B services (excluded from C): CBD Entries, CRZ Entries, CBD For-Hire Trips, CBD VMT.

## Supply series (derived; own axes; never summed)
- **LIRR Operated Trips** — measure_type `operated_service`, unit `train_trips`,
  data_basis `derived_lirr_supply` (electric-MU occupancy census, 73th-g5ad). Base 2022.
- **Subways / Buses / LIRR / Metro-North (VRM)** — measure_type `vehicle_revenue_miles`, unit
  `car_revenue_miles` (rail) or `vehicle_revenue_miles` (bus), data_basis `derived_ntd_vrm`
  (NTD monthly module). Identified by data_basis (service names overlap the rider modes). Indexed
  per mode; subway anchored to 2019, others to 2022. Variation-stat columns are NaN for all derived
  supply rows by design (observed-only discipline).
