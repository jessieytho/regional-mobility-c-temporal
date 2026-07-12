"""B&T vehicle-class split — passenger cars vs the rest [WP-A2].

Source: dtj7-qync, "MTA B&T Daily Traffic Rates by Vehicle Class: 2005-2024" (data.ny.gov, static).
Real layout (confirmed from a live pull): WIDE, one row per (plaza, collection_date), with numeric
per-toll-class columns ``class_1 ... class_21, class_31 ... class_39`` and a ``total`` column.

Split strategy (deliberately low-assumption):
  * MTA authoritatively defines toll **Class 1 = Cars** (2-axle passenger vehicles <=7,000 lbs,
    incl. SUVs/vans), which are ~90% of B&T crossings. We trust only ``class_1`` (cars) and the
    already-validated ``total``. Non-passenger ("other") = ``total - class_1`` -- robust to whatever
    classes 2-39 represent and to any overlap between the class_1-21 and class_31-39 ranges.
  * ``class_shares`` and ``partition_check`` let the caller CONFIRM empirically that class_1 is the
    dominant (~88%) stream (i.e. that it really is cars) before trusting the split.

All series are OBSERVED (direct agency counts). Indexed per group; never pooled with rider modes.
"""
from __future__ import annotations
import re
import pandas as pd

SOCRATA_DOMAIN = "data.ny.gov"
DATASET_ID = "dtj7-qync"

DATE_CANDIDATES = ["collection_date", "date", "plaza_date", "traffic_date", "day"]
TOTAL_CANDIDATES = ["total", "daily_total", "grand_total"]
CLASS_RE = re.compile(r"^class_\d+$", re.IGNORECASE)

# Toll Class 1 = Cars (passenger). Configurable if the data dictionary later identifies other
# light-vehicle classes (e.g. a motorcycle class) to fold into passenger.
PASSENGER_CLASSES = ["class_1"]


def _find(cols, candidates):
    low = {c.lower(): c for c in cols}
    for cand in candidates:
        for lc, orig in low.items():
            if cand == lc or cand in lc:
                return orig
    return None


def class_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if CLASS_RE.match(str(c))]


def _month(df, date_c):
    return pd.to_datetime(df[date_c], errors="coerce").dt.to_period("M").dt.to_timestamp()


def to_monthly(df: pd.DataFrame, passenger_classes=PASSENGER_CLASSES) -> pd.DataFrame:
    """Monthly crossings: passenger (sum of passenger_classes), other (=total-passenger), total."""
    date_c = _find(df.columns, DATE_CANDIDATES)
    total_c = _find(df.columns, TOTAL_CANDIDATES)
    if date_c is None or total_c is None:
        raise ValueError(f"need a date and a total column; got {list(df.columns)}")
    pax_cols = [c for c in passenger_classes if c in df.columns]
    if not pax_cols:
        raise ValueError(f"passenger class columns {passenger_classes} not found in {list(df.columns)}")
    w = pd.DataFrame({"period_start": _month(df, date_c)})
    w["passenger"] = df[pax_cols].apply(pd.to_numeric, errors="coerce").sum(axis=1)
    w["total"] = pd.to_numeric(df[total_c], errors="coerce")
    w = w.dropna(subset=["period_start"])
    m = w.groupby("period_start")[["passenger", "total"]].sum().sort_index()
    m["other"] = m["total"] - m["passenger"]
    return m[["passenger", "other", "total"]]


def class_shares(df: pd.DataFrame, year: int = 2019) -> pd.DataFrame:
    """Each class column's share of summed `total` in `year` -- to confirm class_1 is dominant."""
    date_c = _find(df.columns, DATE_CANDIDATES)
    total_c = _find(df.columns, TOTAL_CANDIDATES)
    cls = class_columns(df)
    yr = pd.to_datetime(df[date_c], errors="coerce").dt.year == year
    sub = df[yr]
    tot = pd.to_numeric(sub[total_c], errors="coerce").sum()
    rows = [{"class": c, f"sum_{year}": pd.to_numeric(sub[c], errors="coerce").sum()} for c in cls]
    out = pd.DataFrame(rows)
    out[f"share_{year}"] = out[f"sum_{year}"] / tot
    return out.sort_values(f"share_{year}", ascending=False).reset_index(drop=True)


def partition_check(df: pd.DataFrame) -> dict:
    """Does sum over class columns equal `total`? (Detects overlap between class ranges.)"""
    total_c = _find(df.columns, TOTAL_CANDIDATES)
    cls = class_columns(df)
    s_classes = df[cls].apply(pd.to_numeric, errors="coerce").sum().sum()
    s_total = pd.to_numeric(df[total_c], errors="coerce").sum()
    return {"sum_all_classes": float(s_classes), "sum_total": float(s_total),
            "ratio_classes_over_total": float(s_classes / s_total) if s_total else float("nan")}


def coding_break_month(monthly: pd.DataFrame, min_share: float = 0.5):
    """First month where the passenger (class_1) share collapses while total stays positive.

    dtj7 changes its vehicle-class coding scheme in late 2023 (cars move out of class_1), so
    class_1 is only a valid 'cars' proxy before this month. Returns None if no break is found.
    """
    share = monthly["passenger"] / monthly["total"].where(monthly["total"] > 0)
    bad = monthly.index[(monthly["total"] > 0) & (share < min_share)]
    return bad.min() if len(bad) else None


def recovery(monthly: pd.DataFrame, bases=(2019, 2022), auto_truncate: bool = True) -> pd.DataFrame:
    """Recovery = trailing-12-month mean / base-year mean, per group.

    If a coding break is detected (class_1 no longer = cars), the series is truncated to the
    reliable window so 'latest12' is the last 12 months before the break, not post-break noise.
    """
    m = monthly
    brk = coding_break_month(m) if auto_truncate else None
    if brk is not None:
        m = m[m.index < brk]
    rows = []
    tail = m.tail(12)
    for col in ("passenger", "other", "total"):
        row = {"group": col, "latest12_mean": tail[col].mean(),
               "reliable_through": (None if brk is None else str(brk.date()))}
        for b in bases:
            base = m[m.index.year == b][col]
            row[f"recov_{b}"] = tail[col].mean() / base.mean() if len(base) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def annual(monthly: pd.DataFrame, years=(2019, 2022, 2024)) -> pd.DataFrame:
    rows = [{"year": y, **{g: monthly[monthly.index.year == y][g].mean()
                           for g in ("passenger", "other", "total")}} for y in years]
    return pd.DataFrame(rows)


def pull_dtj7(app_token=None, timeout: int = 120) -> pd.DataFrame:
    """Pull the full dtj7-qync table from Socrata (run on a networked machine)."""
    import requests
    from io import StringIO
    url = f"https://{SOCRATA_DOMAIN}/resource/{DATASET_ID}.csv"
    headers = {"X-App-Token": app_token} if app_token else {}
    frames, offset, limit = [], 0, 50000
    while True:
        r = requests.get(url, headers=headers,
                         params={"$limit": limit, "$offset": offset, "$order": ":id"}, timeout=timeout)
        r.raise_for_status()
        chunk = pd.read_csv(StringIO(r.text))
        if chunk.empty:
            break
        frames.append(chunk)
        offset += limit
        if len(chunk) < limit:
            break
    return pd.concat(frames, ignore_index=True)
