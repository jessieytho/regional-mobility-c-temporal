"""Fig 3 - The weekday/weekend gap narrowed (day-type ratios) [R1].

Saturday/Weekday and Sunday-Holiday/Weekday ratios over time, per mode. A rising
trajectory = weekend recovering relative to weekday = convergence / peak flattening.
Plotted as a 6-month trailing mean to reveal the trajectory through monthly noise.
Subways extends to 2017 (observed); the other modes are observed from 2020-03.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, viz, config as C
import matplotlib.pyplot as plt


def _ratios():
    dt = io.observed_only(io.load_daytype(grain="monthly"))
    dt = dt[dt["service"].isin(C.MTA_RIDER_MODES)]
    piv = dt.pivot_table(index=["service", "period_start"], columns="day_type",
                         values="avg_per_day")[C.DAY_TYPES]
    piv["sat_wkdy"] = piv["Saturday"] / piv["Weekday"]
    piv["sun_wkdy"] = piv["Sunday-Holiday"] / piv["Weekday"]
    return piv


def main():
    viz.set_style()
    piv = _ratios()
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.5, 4.2), sharey=True)
    for i, m in enumerate(C.MTA_RIDER_MODES):
        if m not in piv.index.get_level_values(0):
            continue
        g = piv.loc[m].sort_index()
        c = viz.PALETTE[i % len(viz.PALETTE)]
        ls = viz.LINESTYLES[i % len(viz.LINESTYLES)]
        axA.plot(g.index, g["sat_wkdy"].rolling(6, min_periods=3).mean(), color=c, ls=ls, lw=1.5, label=m)
        axB.plot(g.index, g["sun_wkdy"].rolling(6, min_periods=3).mean(), color=c, ls=ls, lw=1.5, label=m)
    axA.set_title("Saturday / Weekday ratio")
    axB.set_title("Sunday-Holiday / Weekday ratio")
    axA.set_ylabel("ratio (rising = weekend gaining on weekday)")
    axA.legend(fontsize=7.5, loc="lower left", ncol=2)
    for ax in (axA, axB):
        ax.axvspan(piv.index.get_level_values(1).min(),
                   __import__("pandas").Timestamp("2020-03-01"), color="0.9", alpha=0.5)
    import matplotlib.dates as mdates
    for ax in (axA, axB):
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.tick_params(axis="x", labelsize=8)
    viz.save(fig, "fig6_daytype_ratios")
    print("wrote figures/fig6_daytype_ratios.{png,pdf}")


if __name__ == "__main__":
    main()
