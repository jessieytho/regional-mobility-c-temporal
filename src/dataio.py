"""Feed loaders, the observed-only filter, and unit-firewall guards.

Grounded in the actual feed columns:

  daily:      grain, service, operator, mode_class, measure_type, unit, year,
              period_start, plot_date, day_of_year, month_num, month, day_of_week,
              is_weekend, is_holiday, day_type, value, data_basis, methodology
              (NO 'evidence' column -> observed is derived from data_basis prefix)
  multigrain: grain, service, mode_class, measure_type, unit, data_basis,
              period_start, period_label, value, evidence, yoy_pct, roll12_mean,
              roll12_sd, cv, sm_mean, ctrl_lower, ctrl_upper, z_seasonal, z_yoy
              (variation stats populated at grain=='monthly'; NaN at daily)
  daytype:    grain, service, mode_class, measure_type, unit, data_basis,
              day_type, period_start, period_label, avg_per_day, n_days, evidence
              (grains: monthly, yearly)

Two hard rules enforced here:
  * observed-only statistics       -> observed_only()
  * never sum across measure_type  -> assert_single_measure() before any aggregation
"""
import pandas as pd
from . import config as C


def _load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # period_start is the TRUE date. NOTE: 'plot_date' is a seasonal-overlay device
    # (all years mapped onto 2020) and must never be used as a real date.
    if "period_start" in df.columns:
        df["period_start"] = pd.to_datetime(df["period_start"], errors="coerce")
    return df


def load_daily() -> pd.DataFrame:
    return _load(C.DAILY_CSV)


def load_multigrain(grain: str | None = None) -> pd.DataFrame:
    df = _load(C.MULTIGRAIN_CSV)
    if grain is not None:
        df = df[df["grain"] == grain].copy()
    return df


def load_daytype(grain: str = "monthly") -> pd.DataFrame:
    df = _load(C.DAYTYPE_CSV)
    return df[df["grain"] == grain].copy()


def observed_only(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict to observed tiers.

    daily feed: no 'evidence' column -> use data_basis prefix.
    multigrain/daytype: explicit 'evidence' column.
    """
    if "evidence" in df.columns:
        return df[df["evidence"] == "observed"].copy()
    if "data_basis" in df.columns:
        return df[df["data_basis"].astype(str).str.startswith("observed")].copy()
    raise ValueError("Frame has neither 'evidence' nor 'data_basis'; cannot determine tier.")


def drop_study_b(df: pd.DataFrame) -> pd.DataFrame:
    return df[~df["service"].isin(C.STUDY_B_EXCLUDE)].copy()


def assert_single_measure(df: pd.DataFrame) -> None:
    """Unit firewall: refuse to aggregate across measure types.

    Call this immediately before any sum/mean that pools multiple services.
    """
    measures = df["measure_type"].dropna().unique()
    if len(measures) > 1:
        raise ValueError(
            f"Unit-firewall violation: attempted to combine measure_types {sorted(measures)}. "
            "Sum only within a single measure_type (e.g. rider modes only)."
        )


def rider_total_monthly(observed: bool = True) -> pd.DataFrame:
    """Systemwide monthly total across rider modes (firewall-safe).

    Uses measure_type == 'estimated_ridership' only, so B&T (vehicles),
    AAR (trips), SIR supply (train_trips) and cordon measures are excluded.
    """
    df = load_multigrain(grain="monthly")
    df = df[df["measure_type"] == "estimated_ridership"]
    df = df[df["service"].isin(C.MTA_RIDER_MODES)]  # MTA core; add REGIONAL_RIDER_MODES only for a labeled regional total
    if observed:
        df = observed_only(df)
    assert_single_measure(df)
    return (
        df.groupby("period_start", as_index=False)["value"].sum()
          .sort_values("period_start")
          .reset_index(drop=True)
    )


def mode_monthly(service: str, observed: bool = True, measure_type: str = "estimated_ridership") -> pd.DataFrame:
    """Monthly series for a single service (no cross-measure summing needed)."""
    df = load_multigrain(grain="monthly")
    df = df[(df["service"] == service) & (df["measure_type"] == measure_type)]
    if observed:
        df = observed_only(df)
    return df.sort_values("period_start").reset_index(drop=True)


def index_to_baseline(series: pd.DataFrame, value_col: str, baseline_year: int,
                      date_col: str = "period_start") -> pd.DataFrame:
    """Index a monthly series to a baseline-year mean = 100."""
    s = series.copy()
    base = s[s[date_col].dt.year == baseline_year][value_col].mean()
    if pd.isna(base) or base == 0:
        raise ValueError(f"No usable {baseline_year} baseline in this series.")
    s["indexed"] = 100.0 * s[value_col] / base
    return s
