"""Fig 8 — systemwide supply vs demand from NTD vehicle revenue-miles (derived_ntd_vrm).

Left: subway supply vs demand indexed to 2019 (the structural-gap anchor; service-per-rider ~1.3).
Right: service-per-rider indexed to 2022 for subway/bus/LIRR/MNR. See Section 4.3.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import pandas as pd
from src import config as C, viz


def main():
    viz.set_style()
    df = pd.read_csv(C.MULTIGRAIN_CSV, parse_dates=["period_start"])
    m = df[df.grain == "monthly"]
    def dem(s): return m[(m.service == s) & (m.measure_type == "estimated_ridership") & (m.evidence == "observed")].set_index("period_start")["value"].sort_index()
    def sup(s): return m[(m.service == s) & (m.data_basis == "derived_ntd_vrm")].set_index("period_start")["value"].sort_index()
    def idx(x, yr): return x / x[x.index.year == yr].mean() * 100
    def spr(s, yr):
        d = idx(dem(s), yr).rolling(3, min_periods=1).mean(); v = idx(sup(s), yr).rolling(3, min_periods=1).mean()
        c = d.index.intersection(v.index); return d.loc[c], v.loc[c], v.loc[c] / d.loc[c]

    import matplotlib.pyplot as plt
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.5, 4.2))
    d19, s19, r19 = spr("Subways", 2019)
    axA.plot(d19.index, d19, color=viz.PALETTE[5], lw=1.9, label="Subway demand: ridership (observed)")
    axA.plot(s19.index, s19, color=viz.PALETTE[1], lw=1.9, ls="--", label="Subway supply: NTD VRM (derived)")
    axA.axhline(100, color="grey", lw=0.7, ls=":")
    axA.annotate(f"service per rider = {r19.tail(3).mean():.2f}\n(2019 base)",
                 xy=(pd.Timestamp("2022-03-01"), 88), fontsize=9, color=viz.PALETTE[6])
    axA.set_ylabel("index (2019 = 100)"); axA.set_title("Subway: service held ahead of demand (2019 base)")
    axA.legend(fontsize=8, loc="lower left", framealpha=0.9)
    for svc, col in [("Subways", viz.PALETTE[5]), ("Buses", viz.PALETTE[3]), ("LIRR", viz.PALETTE[1]), ("Metro-North", viz.PALETTE[7])]:
        _, _, r = spr(svc, 2022); r = r[r.index >= "2022-01-01"]
        axB.plot(r.index, r, color=col, lw=1.8, label=f"{svc} ({r.tail(3).mean():.2f})")
    axB.axhline(1.0, color="k", lw=0.9, ls=":")
    axB.set_ylabel("service per rider (VRM/ridership, 2022=1)"); axB.set_title("Systemwide, post-2022 (2022 base)")
    axB.legend(fontsize=8, loc="upper right", title="latest 3-mo")
    import matplotlib.dates as mdates
    for ax in (axA, axB):
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator((1, 7)))  # unlabeled half-year minors
        ax.tick_params(axis="x", labelsize=8)
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(45); lbl.set_ha("right")
    viz.save(fig, "fig4_supply_demand_systemwide")
    print("wrote figures/fig4_supply_demand_systemwide.{png,pdf}")


if __name__ == "__main__":
    main()
