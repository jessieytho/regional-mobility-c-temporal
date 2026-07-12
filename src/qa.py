"""QA assertions run before/after analysis to keep the invariants honest.

Run `python -m src.qa` for a quick health check on the feeds.
"""
import pandas as pd
from . import config as C
from . import dataio as io


def check_no_cross_measure_totals() -> None:
    """The rider total must be built from a single measure_type. Supply series (e.g. NTD VRM)
    may share service names with rider modes but are a different measure_type and a different axis;
    verify the rider-total path isolates estimated_ridership, and that any other measure_type found
    under a rider-mode name is a documented supply measure rather than an accidental contaminant."""
    df = io.load_multigrain(grain="monthly")
    rider = df[df["service"].isin(C.MTA_RIDER_MODES)]
    io.assert_single_measure(rider[rider["measure_type"] == "estimated_ridership"])
    stray = set(rider["measure_type"].dropna().unique()) - {"estimated_ridership", "vehicle_revenue_miles"}
    if stray:
        raise AssertionError(
            f"Unexpected measure_type(s) {sorted(stray)} under rider-mode service names; only "
            "documented supply measures (NTD VRM) may share those names."
        )


def check_observed_windows() -> None:
    """Confirm the documented observed-coverage constraint: pre-2020 observed
    exists only for the anchor mode and B&T."""
    dt = io.load_daytype(grain="monthly")
    obs = io.observed_only(dt)
    for svc, g in obs.groupby("service"):
        has_pre2020 = g["period_start"].dt.year.min() < 2020
        flagged = svc in (C.OBSERVED_2019_MODES + [C.ANCHOR_MODE])
        if has_pre2020 and not flagged:
            raise AssertionError(
                f"{svc} has observed pre-2020 day-type data but is not in the "
                "documented observed-2019 set — revisit the baseline rule."
            )


def check_sir_supply_is_derived() -> None:
    mg = io.load_multigrain()
    sir = mg[mg["service"] == C.SIR_SUPPLY]
    if "evidence" in sir.columns and (sir["evidence"] == "observed").any():
        raise AssertionError("SIR supply has observed rows; it should be 100% derived (timetable).")


def check_lirr_supply_is_derived() -> None:
    """LIRR operated-trip supply (derived_lirr_supply) must carry no observed rows."""
    mg = io.load_multigrain()
    lirr = mg[mg["service"] == C.LIRR_SUPPLY]
    if "evidence" in lirr.columns and (lirr["evidence"] == "observed").any():
        raise AssertionError("LIRR operated-trip supply has observed rows; it should be 100% derived.")


def check_ntd_vrm_is_derived() -> None:
    """NTD VRM supply shares service names with rider modes, so it is identified by
    data_basis, must be a single measure_type, carry no observed rows, and cover only
    the documented services."""
    mg = io.load_multigrain()
    if "data_basis" not in mg.columns:
        return
    vrm = mg[mg["data_basis"] == C.NTD_VRM_BASIS]
    if vrm.empty:
        return
    if "evidence" in vrm.columns and (vrm["evidence"] == "observed").any():
        raise AssertionError("NTD VRM supply has observed rows; it should be 100% derived.")
    if set(vrm["measure_type"].unique()) != {"vehicle_revenue_miles"}:
        raise AssertionError("NTD VRM rows carry an unexpected measure_type — check the firewall.")
    stray = set(vrm["service"].unique()) - set(C.NTD_VRM_SERVICES)
    if stray:
        raise AssertionError(f"NTD VRM covers unexpected services {stray}.")


def main() -> None:
    check_no_cross_measure_totals()
    check_observed_windows()
    check_sir_supply_is_derived()
    check_lirr_supply_is_derived()
    check_ntd_vrm_is_derived()
    print("QA passed: firewall holds, observed windows match the documented constraint, "
          "SIR/LIRR/NTD-VRM supply series are derived.")


if __name__ == "__main__":
    main()
