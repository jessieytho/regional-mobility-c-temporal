"""Reproducibility regression test — recompute headline statistics from the feed and
assert they match the values reported in the manuscript (within tolerance).

Run: `python scripts/check_numbers.py`  (exit 0 = all pass, 1 = drift).

This is deterministic and feed-only (no figures, no RNG), so it is a robust guard against
feed corruption or logic drift — the kind of check a reproducibility reviewer runs. Figure
byte-hashes are intentionally NOT tested (matplotlib rendering is environment-dependent);
the numbers behind the figures are what matter and are tested here.
"""
import sys
import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import config as C  # noqa: E402

FEED = C.MULTIGRAIN_CSV

# (value_as_reported, absolute_tolerance)
EXPECTED = {
    # recovery ratio = trailing-12 observed mean / baseline-year mean
    ("Subways", "recov_2022"): (1.270, 0.005),
    ("Subways", "recov_2019_obs"): (0.756, 0.005),
    ("Buses", "recov_2022"): (0.975, 0.005),
    ("LIRR", "recov_2022"): (1.560, 0.010),
    ("Metro-North", "recov_2022"): (1.518, 0.010),
    ("Staten Island Railway", "recov_2022"): (1.175, 0.010),
    ("Bridges and Tunnels", "recov_2022"): (1.012, 0.010),
    ("Access-A-Ride", "recov_2022"): (1.869, 0.010),
    # measured supply-vs-demand: latest 3-mo service-per-rider (indexed 2022)
    ("LIRR", "spr_latest"): (0.97, 0.03),
    ("Staten Island Railway", "spr_latest"): (0.83, 0.03),
}

MEASURE = {"Bridges and Tunnels": "vehicle_traffic", "Access-A-Ride": "scheduled_trips"}
SUPPLY = {"LIRR": ("LIRR Operated Trips", "operated_service"),
          "Staten Island Railway": ("SIR Scheduled Trips", "scheduled_service")}
LIRR_SUPPLY_BASE_START = "2022-08-01"   # drop partial Jul-2022


def _monthly(df, service, measure_type, observed=None):
    q = df[(df.grain == "monthly") & (df.service == service) & (df.measure_type == measure_type)]
    if observed is True:
        q = q[q.evidence == "observed"]
    return q.set_index("period_start")["value"].sort_index()


def compute(df, service, stat):
    mt = MEASURE.get(service, "estimated_ridership")
    if stat == "recov_2022":
        o = _monthly(df, service, mt, observed=True)
        return o.tail(12).mean() / o[o.index.year == 2022].mean()
    if stat == "recov_2019_obs":
        o = _monthly(df, service, mt, observed=True)
        return o.tail(12).mean() / o[o.index.year == 2019].mean()
    if stat == "spr_latest":
        dem = _monthly(df, service, "estimated_ridership", observed=True)
        sup_svc, sup_mt = SUPPLY[service]
        sup = _monthly(df, sup_svc, sup_mt)
        if service == "LIRR":
            sup = sup[sup.index >= LIRR_SUPPLY_BASE_START]
        di = (dem / dem[dem.index.year == 2022].mean() * 100).rolling(3, min_periods=1).mean()
        si = (sup / sup[sup.index.year == 2022].mean() * 100).rolling(3, min_periods=1).mean()
        common = di.index.intersection(si.index)
        return (si.loc[common] / di.loc[common]).tail(3).mean()
    raise ValueError(stat)


def main():
    df = pd.read_csv(FEED, parse_dates=["period_start"])
    fails = 0
    print(f"{'metric':40s} {'computed':>10s} {'reported':>10s}  status")
    for (svc, stat), (expected, tol) in EXPECTED.items():
        got = compute(df, svc, stat)
        ok = abs(got - expected) <= tol
        fails += not ok
        print(f"{svc+' / '+stat:40s} {got:10.3f} {expected:10.3f}  {'PASS' if ok else 'FAIL'}")
    if fails:
        print(f"\n{fails} metric(s) drifted beyond tolerance.")
        sys.exit(1)
    print("\nAll headline numbers reproduce within tolerance.")


if __name__ == "__main__":
    main()
