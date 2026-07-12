"""Paratransit cost context (WP-A3, Section 4.5).

Regenerates data/derived/ntd_nyct_cost_per_trip.csv: NYC Transit (NTD ID 20008) annual operating
expense, unlinked trips, and cost per trip by mode, from the NTD TS2.1 time series
("Service Data and Operating Expenses Time Series by Mode", report years 2015-2024).

Source file (NOT committed; ~89 MB): FTA NTD "2024 TS2.1" at transit.dot.gov, or the Socrata mirror
data.transportation.gov/.../npsm-38gk exported as CSV. Point TS21_CSV at it and run.

IMPORTANT CAVEAT — why AAR *program* figures come from the Comptroller, not this file:
NYCT's NTD "Demand Response" (DR) row tracks essentially the primary-carrier (van) slice, so its
trips DECLINE (4.83M in 2019 -> 2.83M in 2024) and its cost/trip is volatile ($107 -> $188 -> $96).
The broker / for-hire / e-hail trips that are now the majority of Access-A-Ride are reported outside
this row, so DR here is NOT total AAR and must not be used for paratransit ridership or total cost.
Total-program figures (ridership above 2019, ~$467M->$596M cost 2016-19, ~$57 blended and
$116/$40 by-carrier cost per trip, the primary->broker shift) come from NYS Comptroller Report
12-2024 and are cited in the manuscript. This file is used ONLY for the reliable fixed-route
benchmark: subway ~$2-3 and bus ~$4-6 per trip, which put AAR's per-trip cost an order of magnitude
higher. These are annual dollar context, firewalled from the daily rider feed (never a feed row).
"""
from __future__ import annotations
import os
import pandas as pd

TS21_CSV = os.environ.get("TS21_CSV", "")  # path to the NTD TS2.1 CSV export
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "derived", "ntd_nyct_cost_per_trip.csv")
NYCT = "20008"
MODES = {"DR": "AAR_demand_response", "HR": "subway_heavy_rail", "MB": "bus_motor_bus"}


def build(ts21_csv: str) -> pd.DataFrame:
    df = pd.read_csv(ts21_csv, dtype={"NTD ID": str}, low_memory=False)
    df["Value"] = pd.to_numeric(df["Value"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    df["Report Year"] = pd.to_numeric(df["Report Year"], errors="coerce")
    n = df[df["NTD ID"] == NYCT]
    rows = []
    for mode, label in MODES.items():
        oe = n[(n["Mode"] == mode) & (n["Field"] == "Operating Expenses")].groupby("Report Year")["Value"].sum()
        upt = n[(n["Mode"] == mode) & (n["Field"] == "Unlinked Passenger Trips")].groupby("Report Year")["Value"].sum()
        for y in oe.index:
            rows.append({"ntd_id": NYCT, "mode": label, "report_year": int(y),
                         "operating_expenses": round(oe[y], 0), "unlinked_trips": round(upt[y], 0),
                         "cost_per_trip": round(oe[y] / upt[y], 2) if upt.get(y) else None})
    return pd.DataFrame(rows).sort_values(["mode", "report_year"])


if __name__ == "__main__":
    if not TS21_CSV:
        raise SystemExit("Set TS21_CSV to the NTD TS2.1 CSV path (see module docstring). "
                         "The committed data/derived/ntd_nyct_cost_per_trip.csv is the pre-extracted result.")
    out = build(TS21_CSV)
    out.to_csv(os.path.abspath(OUT), index=False)
    print(f"wrote {OUT} ({len(out)} rows)")
    print(out[out.report_year.isin([2019, 2022, 2024])].to_string(index=False))
