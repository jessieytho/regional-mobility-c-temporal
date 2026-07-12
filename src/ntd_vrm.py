"""NTD Monthly Module parser -> MTA-mode monthly supply series (Vehicle Revenue Miles).

Tier-1 subway/systemwide supply for the supply-vs-demand index, with NO GTFS dependency.
The FTA NTD Monthly Module (the same product the paper uses for ridership backfill) reports
UPT, VRM, VRH, VOMS per agency x mode x type-of-service x month. VRM is a service-supply
measure available monthly back to 2002, so it gives a 2019 baseline for the anchor mode
(subway) directly. Pure pandas; no network.

Design notes:
  * We INDEX per mode (never rescale to "MTA level"): MTA publishes no VRM counterpart, and
    indexing to a base year cancels any definitional offset. VRM stays on its own measure
    axis and is never summed across modes.
  * NTD VRM is ACTUAL operated revenue-miles (not scheduled) -> label "operated", like LIRR.
  * For rail, VRM is passenger-car revenue miles (a capacity measure); for bus it is
    vehicle revenue miles. Units differ across modes but the per-mode index is unit-free.
"""
from __future__ import annotations
import re
import pandas as pd

_MON = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}


def _parse_month(col: str):
    """Return a Timestamp (month start) if the column header is a month label, else None."""
    s = str(col).strip().upper().replace(" ", "").replace("-", "").replace("_", "")
    m = re.match(r"^([A-Z]{3})(\d{2})$", s)          # JAN02 / JAN19
    if m and m.group(1) in _MON:
        yy = int(m.group(2))
        return pd.Timestamp(2000 + yy, _MON[m.group(1)], 1)
    try:                                              # 2019-01 / Jan 2019 / 1/2019 ...
        ts = pd.to_datetime(str(col), errors="raise")
        return pd.Timestamp(ts.year, ts.month, 1)
    except Exception:
        return None


def load_ntd_monthly(path: str, sheet: str | None = None, metric: str = "VRM") -> pd.DataFrame:
    """Read the NTD monthly module -> long: [ntd_id, agency, mode, tos, period_start, value].

    Handles both layouts:
      * LONG  (one row per agency/mode/month; metric columns UPT/VRM/VRH/VOMS + a Date column)
        -- this is the current 'Data'-sheet format on data.transportation.gov;
      * WIDE  (one metric per sheet; one column per month, e.g. JAN19) -- the legacy format.
    """
    xl = pd.ExcelFile(path)
    if sheet is None:
        sheet = ("Data" if "Data" in xl.sheet_names
                 else next((s for s in xl.sheet_names if str(s).strip().upper() == metric.upper()),
                           xl.sheet_names[0]))
    raw = pd.read_excel(xl, sheet_name=sheet)

    def pick(cols, *names):
        for n in names:
            for c in cols:
                if str(c).strip().lower().replace(" ", "") == n:
                    return c
        return None

    metric_col = next((c for c in raw.columns if str(c).strip().upper() == metric.upper()), None)
    date_col = pick(raw.columns, "date", "month", "period")

    if metric_col is not None and date_col is not None:            # LONG format
        out = pd.DataFrame({
            "ntd_id": raw[pick(raw.columns, "ntdid", "5digitntdid", "legacyntdid")],
            "agency": raw[pick(raw.columns, "agency", "agencyname")],
            "mode": raw[pick(raw.columns, "mode")],
            "tos": raw[pick(raw.columns, "tos", "typeofservice")],
            "period_start": pd.to_datetime(raw[date_col], errors="coerce").dt.to_period("M").dt.to_timestamp(),
            "value": pd.to_numeric(raw[metric_col], errors="coerce"),
        })
        return out

    # WIDE format (legacy): one column per month
    month_cols = {c: _parse_month(c) for c in raw.columns}
    month_cols = {c: d for c, d in month_cols.items() if d is not None}
    if not month_cols:
        raise ValueError(f"Sheet '{sheet}': neither a '{metric}'+Date long layout nor month columns. "
                         f"Headers: {list(raw.columns)[:14]}")
    id_cols = [c for c in raw.columns if c not in month_cols]
    long = raw.melt(id_vars=id_cols, value_vars=list(month_cols), var_name="_m", value_name="value")
    long["period_start"] = long["_m"].map(month_cols)
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    return pd.DataFrame({
        "ntd_id": long[pick(id_cols, "ntdid", "5digitntdid", "legacyntdid")],
        "agency": long[pick(id_cols, "agency", "agencyname")],
        "mode": long[pick(id_cols, "mode")],
        "tos": long[pick(id_cols, "tos", "typeofservice", "3mode")],
        "period_start": long["period_start"],
        "value": long["value"],
    })


def aggregate_service(long: pd.DataFrame, service: str, mode, agency_regex: str,
                      tos: str | None = None) -> pd.Series:
    """Sum matched (agency, mode(s)[, tos]) rows to a monthly series for one paper service.

    `mode` may be a single code ("MB") or a list of codes (["MB", "CB", "RB"] for the full
    bus family: motor bus + commuter bus + bus rapid transit).
    """
    modes = [mode] if isinstance(mode, str) else list(mode)
    modes = [x.upper() for x in modes]
    m = long["mode"].astype(str).str.upper().isin(modes) & \
        long["agency"].astype(str).str.contains(agency_regex, case=False, regex=True, na=False)
    if tos is not None:
        m &= long["tos"].astype(str).str.upper() == tos.upper()
    s = (long[m].groupby("period_start")["value"].sum().sort_index())
    s.name = service
    return s[s > 0]


RAIL_MODES = {"HR", "CR", "LR", "YR", "MG", "SR"}     # heavy/commuter/light rail etc.


def to_feed_rows(series: pd.Series, service: str, mode_class: str, mode_code=None) -> pd.DataFrame:
    is_rail = mode_class in ("subway", "rail") or (
        isinstance(mode_code, str) and mode_code.upper() in RAIL_MODES)
    unit = "car_revenue_miles" if is_rail else "vehicle_revenue_miles"
    df = series.rename("value").rename_axis("period_start").reset_index()
    df = df.assign(grain="monthly", service=service, mode_class=mode_class,
                   measure_type="vehicle_revenue_miles", unit=unit,
                   data_basis="derived_ntd_vrm", evidence="derived",
                   period_label=df["period_start"].dt.strftime("%Y-%m"))
    return df[["grain", "service", "mode_class", "measure_type", "unit",
               "data_basis", "period_start", "period_label", "value", "evidence"]]
