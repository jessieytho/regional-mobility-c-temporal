"""GTFS scheduled-trip counting engine [WP-A1, Path 2].

Counts *scheduled* trips for a given service date from a static GTFS feed (.zip or dir).
Pure stdlib + pandas; no network. Correctly handles:
  * calendar.txt service patterns (weekday flags + start/end date window),
  * calendar_dates.txt exceptions (1 = added service, 2 = removed),
  * feeds with ONLY calendar_dates (no calendar.txt),
  * route_type filtering (subway = 1) via routes.txt,
  * frequencies.txt (headway-based trips) as well as explicit per-trip rows.

Yields a supply measure analogous to SIR scheduled_service: scheduled train-trips per day.
Because a static feed is point-in-time, build a trajectory from DATED snapshots (see notebook):
each snapshot's weekday/Saturday/Sunday counts hold until the next snapshot (step function).
"""
from __future__ import annotations
import io
import zipfile
import datetime as dt
import pandas as pd

_DOW = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def _read(src, name) -> pd.DataFrame | None:
    """Read one GTFS table from a zip path or a directory; None if absent."""
    if isinstance(src, zipfile.ZipFile):
        if name not in src.namelist():
            return None
        with src.open(name) as fh:
            return pd.read_csv(io.TextIOWrapper(fh, "utf-8-sig"), dtype=str)
    import pathlib
    p = pathlib.Path(src) / name
    return pd.read_csv(p, dtype=str) if p.exists() else None


def _open(src):
    import pathlib
    if str(src).endswith(".zip"):
        return zipfile.ZipFile(src)
    return pathlib.Path(src)


def active_service_ids(cal: pd.DataFrame | None, cald: pd.DataFrame | None,
                       target: dt.date) -> set[str]:
    """Service_ids running on `target`, per GTFS calendar semantics."""
    ymd = target.strftime("%Y%m%d")
    dow = _DOW[target.weekday()]
    base: set[str] = set()
    if cal is not None:
        m = (cal[dow].astype(int) == 1) & (cal["start_date"] <= ymd) & (cal["end_date"] >= ymd)
        base = set(cal.loc[m, "service_id"])
    if cald is not None:
        d = cald[cald["date"] == ymd]
        base |= set(d.loc[d["exception_type"].astype(int) == 1, "service_id"])   # added
        base -= set(d.loc[d["exception_type"].astype(int) == 2, "service_id"])   # removed
    return base


def _freq_trip_counts(freq: pd.DataFrame) -> dict[str, int]:
    """trips implied by frequencies.txt per trip_id (headway-based feeds)."""
    def n(row):
        t0 = _sec(row["start_time"]); t1 = _sec(row["end_time"]); h = int(row["headway_secs"])
        return max(0, (t1 - t0) // h)                    # departures in [start, end)
    freq = freq.copy()
    freq["n"] = freq.apply(n, axis=1)
    return freq.groupby("trip_id")["n"].sum().to_dict()


def _sec(hms: str) -> int:
    h, m, s = (int(x) for x in hms.split(":"))
    return h * 3600 + m * 60 + s


def count_trips(gtfs_src, target: dt.date, route_types=(1,)) -> dict:
    """Scheduled trips operating on `target`, optionally filtered to route_types (subway=1)."""
    src = _open(gtfs_src)
    cal, cald = _read(src, "calendar.txt"), _read(src, "calendar_dates.txt")
    trips, routes = _read(src, "trips.txt"), _read(src, "routes.txt")
    freq = _read(src, "frequencies.txt")
    if trips is None:
        raise ValueError("trips.txt missing — not a valid GTFS feed")

    services = active_service_ids(cal, cald, target)
    t = trips[trips["service_id"].isin(services)].copy()

    if route_types is not None and routes is not None and "route_id" in t.columns:
        rt = routes.set_index("route_id")["route_type"].astype(int)
        keep = t["route_id"].map(rt).isin(route_types)
        t = t[keep]

    if freq is not None and not freq.empty:                       # headway-based
        counts = _freq_trip_counts(freq)
        n = int(sum(counts.get(tid, 1) for tid in t["trip_id"]))  # non-freq trips count as 1
    else:                                                         # explicit trips
        n = int(len(t))

    return {"date": target.isoformat(),
            "day_type": _daytype(target),
            "n_trips": n,
            "n_service_ids": len(services),
            "route_types": route_types}


def _daytype(d: dt.date) -> str:
    wd = d.weekday()
    return "Weekday" if wd <= 4 else ("Saturday" if wd == 5 else "Sunday-Holiday")


def representative_counts(gtfs_src, ref: dt.date, route_types=(1,)) -> dict:
    """One weekday (Tue-Thu), one Saturday, one Sunday near `ref` -> the snapshot's day-type levels."""
    def nearest(target_dow):
        # walk forward from ref to the next date with the wanted dow
        d = ref
        for _ in range(14):
            if d.weekday() == target_dow:
                return d
            d += dt.timedelta(days=1)
        return ref
    wd = nearest(2)   # Wednesday
    sat = nearest(5)
    sun = nearest(6)
    return {"weekday": count_trips(gtfs_src, wd, route_types)["n_trips"],
            "saturday": count_trips(gtfs_src, sat, route_types)["n_trips"],
            "sunday": count_trips(gtfs_src, sun, route_types)["n_trips"],
            "sample_dates": {"weekday": wd.isoformat(), "saturday": sat.isoformat(), "sunday": sun.isoformat()}}
