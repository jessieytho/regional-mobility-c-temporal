"""Table 1 - Data & coverage [Methods].

Per service (C-temporal scope): measure_type/unit, full daily window, observed-only
window, and tier availability. Writes tables/t1_coverage.csv and prints markdown.
Full dictionary lives in docs/ (cited); this table is the compact in-paper version.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, config as C
import pandas as pd

SCOPE = (C.MTA_RIDER_MODES + ["Access-A-Ride", "Bridges and Tunnels",
                              "SIR Scheduled Trips"] + C.REGIONAL_RIDER_MODES)


def main():
    mg = io.load_multigrain(grain="daily")
    mg = mg[mg["service"].isin(SCOPE)]
    rows = []
    for svc, g in mg.groupby("service"):
        obs = g[g["evidence"] == "observed"] if "evidence" in g else g.iloc[0:0]
        rows.append(dict(
            service=svc,
            measure=g["measure_type"].iloc[0],
            unit=g["unit"].iloc[0],
            all_start=g["period_start"].min().date(),
            all_end=g["period_start"].max().date(),
            obs_start=(obs["period_start"].min().date() if len(obs) else "—"),
            obs_end=(obs["period_start"].max().date() if len(obs) else "—"),
            has_observed=("yes" if len(obs) else "no (derived only)"),
        ))
    df = pd.DataFrame(rows)
    # order: MTA rider, own-axis, regional
    df["ord"] = df["service"].apply(lambda s: SCOPE.index(s) if s in SCOPE else 99)
    df = df.sort_values("ord").drop(columns="ord").reset_index(drop=True)
    C.TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.TABLES / "t1_coverage.csv", index=False)
    print(df.to_markdown(index=False))
    print("\nwrote tables/t1_coverage.csv")


if __name__ == "__main__":
    main()
