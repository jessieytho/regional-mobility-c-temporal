"""Fig 2 - The new weekly shape (day-of-week profile) [R1].

Mean ridership by day-of-week, normalized to each profile's own mean (shape, not level).
Holidays are excluded so the working-week shape isn't distorted by holiday Mondays.

Panel A: Subways, pre-shock (2017-2019) vs current (trailing 12mo) -- the across-shock
         change (observed both sides; Subways is the only rider mode with pre-2020 observed).
Panel B: current-era profiles for the five MTA rider modes -- who is flat, who stays peaked.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, viz, config as C
import matplotlib.pyplot as plt
import pandas as pd

SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _profiles():
    d = io.observed_only(io.load_daily())
    d = d[(d["is_holiday"] == False) & (d["measure_type"] == "estimated_ridership")]
    end = d["period_start"].max()
    cur_start = end - pd.DateOffset(months=12)

    def prof(service, start, stop):
        g = d[(d["service"] == service) & (d["period_start"] >= start) & (d["period_start"] <= stop)]
        p = g.groupby("day_of_week")["value"].mean().reindex(C.DOW_ORDER)
        return p / p.mean()
    return d, prof, cur_start, end


def main():
    viz.set_style()
    d, prof, cur_start, end = _profiles()
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.5, 4.2), sharey=True)

    # Panel A: Subways across the shock
    pre = prof("Subways", "2017-01-01", "2019-12-31")
    cur = prof("Subways", cur_start, end)
    axA.plot(SHORT, pre.values, color=viz.PALETTE[2], marker="o", lw=1.6, label="Pre-shock (2017-2019)")
    axA.plot(SHORT, cur.values, color=viz.PALETTE[0], marker="s", lw=1.8, label="Current (trailing 12 mo)")
    axA.set_title("Subways: weekly shape, pre-shock vs now")
    axA.set_ylabel("ridership relative to weekly mean")
    axA.legend(fontsize=8, loc="lower center")

    # Panel B: current-era, five modes
    for i, m in enumerate(C.MTA_RIDER_MODES):
        p = prof(m, cur_start, end)
        if p.isna().all():
            continue
        axB.plot(SHORT, p.values, marker=".", lw=1.4,
                 color=viz.PALETTE[i % len(viz.PALETTE)], label=m)
    axB.set_title("Current weekly shape by mode")
    axB.legend(fontsize=7, loc="lower center", ncol=2)

    for ax in (axA, axB):
        ax.axhline(1.0, color="grey", lw=0.7, ls=":")
    viz.save(fig, "fig2_dow_profile")

    core = pre[["Tuesday", "Wednesday", "Thursday"]].mean()
    corec = cur[["Tuesday", "Wednesday", "Thursday"]].mean()
    print(f"Subways Mon/core {pre['Monday']/core:.2f}->{cur['Monday']/corec:.2f}, "
          f"Fri/core {pre['Friday']/core:.2f}->{cur['Friday']/corec:.2f}, "
          f"weekend/core {(pre[['Saturday','Sunday']].mean())/core:.2f}->"
          f"{(cur[['Saturday','Sunday']].mean())/corec:.2f}")
    print("wrote figures/fig2_dow_profile.{png,pdf}")


if __name__ == "__main__":
    main()
