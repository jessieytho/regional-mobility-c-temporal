"""Fig 7 — supply vs demand for two rail modes (LIRR operated trips + SIR scheduled trips).

Indexed to 2022. LIRR supply = electric-MU operated train-trips (derived_lirr_supply); SIR
supply = scheduled train-trips (derived). Demand = observed ridership. See Section 4.3.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import pandas as pd
from src import config as C, viz

LIRR_BASE_START = "2022-08-01"   # drop partial Jul-2022 from the LIRR base


def _m(df, service, mt, observed=False):
    q = df[(df.grain == "monthly") & (df.service == service) & (df.measure_type == mt)]
    if observed:
        q = q[q.evidence == "observed"]
    return q.set_index("period_start")["value"].sort_index()


def main():
    viz.set_style()
    df = pd.read_csv(C.MULTIGRAIN_CSV, parse_dates=["period_start"])
    idx = lambda s: s / s[s.index.year == 2022].mean() * 100
    dl = idx(_m(df, "LIRR", "estimated_ridership", True)).rolling(3, min_periods=1).mean()
    sl = _m(df, C.LIRR_SUPPLY, "operated_service"); sl = idx(sl[sl.index >= LIRR_BASE_START]).rolling(3, min_periods=1).mean()
    ds = idx(_m(df, "Staten Island Railway", "estimated_ridership", True)).rolling(3, min_periods=1).mean()
    ss = idx(_m(df, C.SIR_SUPPLY, "scheduled_service")).rolling(3, min_periods=1).mean()
    cl = dl.index.intersection(sl.index); rl = sl.loc[cl] / dl.loc[cl]
    cs = ds.index.intersection(ss.index); rs = ss.loc[cs] / ds.loc[cs]

    import matplotlib.pyplot as plt
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.6, 4.2))
    axA.plot(dl.index, dl, color=viz.PALETTE[5], lw=1.9, label="LIRR demand: ridership (observed)")
    axA.plot(sl.index, sl, color=viz.PALETTE[1], lw=1.9, ls="--", label="LIRR supply: electric-MU operated trips (derived)")
    axA.axhline(100, color="grey", lw=0.7, ls=":"); axA.axvline(pd.Timestamp("2023-02-27"), color=viz.PALETTE[3], lw=1.0, alpha=0.7)
    axA.set_ylabel("index (2022 = 100)"); axA.set_title("LIRR supply vs demand"); axA.legend(fontsize=7.5, loc="lower right")
    axB.plot(rl.index, rl, color=viz.PALETTE[5], lw=2.0, label="LIRR (electric-MU operated)")
    axB.plot(rs.index, rs, color=viz.PALETTE[1], lw=1.7, ls="--", label="SIR (scheduled)")
    axB.axhline(1.0, color="k", lw=0.9, ls=":")
    axB.set_ylabel("service per rider (supply/demand, 2022=1)"); axB.set_title("Service ahead of (>1) vs lagging (<1) demand")
    axB.legend(fontsize=7.5, loc="upper right")
    viz.save(fig, "fig7_supply_demand")
    print("wrote figures/fig7_supply_demand.{png,pdf}")


if __name__ == "__main__":
    main()
