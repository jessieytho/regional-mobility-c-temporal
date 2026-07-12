"""Fig 5 - Trend and seasonal restructuring, anchor mode (Subways) [R2].

Classical additive decomposition (centered 12-month MA trend; month-of-year seasonal).
statsmodels is unavailable offline, so this uses pandas/numpy; roll12_mean in the feed is
a trailing-trend cross-check. Two findings:
  A) trend collapses in 2020 and plateaus well below the 2019 level (permanent gap), and
  B) the annual seasonal swing compresses (the fall-peak / winter-trough cycle flattens),
     shown as the month-of-year shape pre-shock vs recent.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, viz, config as C
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


def main():
    viz.set_style()
    s = io.mode_monthly("Subways", observed=True).set_index("period_start")["value"].sort_index().asfreq("MS")
    s = s.interpolate(limit_direction="both")
    trend = s.rolling(12, center=True).mean()
    detr = s - trend

    def seasonal(yrs):
        sub = detr[detr.index.year.isin(yrs)]
        m = sub.groupby(sub.index.month).mean()
        return (m - m.mean()).reindex(range(1, 13))

    pre = seasonal([2017, 2018, 2019])
    post = seasonal([2023, 2024, 2025])
    t19 = trend[trend.index.year == 2019].mean()

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.5, 4.2))
    axA.plot(s.index, s / 1e6, color="0.7", lw=0.8, label="observed monthly")
    axA.plot(trend.index, trend / 1e6, color=viz.PALETTE[0], lw=2, label="trend (centered 12-mo MA)")
    axA.axhline(t19 / 1e6, color=viz.PALETTE[6], lw=1, ls="--", label="2019 trend level")
    axA.set_ylabel("monthly riders (millions)")
    axA.set_title("Subways: trend collapse and sub-2019 plateau")
    axA.legend(fontsize=8, loc="lower right")

    axB.plot(range(1, 13), pre / 1e6, color=viz.PALETTE[2], marker="o", lw=1.6, label="pre-shock 2017-2019")
    axB.plot(range(1, 13), post / 1e6, color=viz.PALETTE[0], marker="s", lw=1.8, label="recent 2023-2025")
    axB.axhline(0, color="grey", lw=0.7, ls=":")
    axB.set_xticks(range(1, 13)); axB.set_xticklabels(MONTHS)
    axB.set_ylabel("seasonal effect (millions, vs annual mean)")
    axB.set_title("Annual seasonal swing compressed")
    axB.legend(fontsize=8, loc="upper left")
    viz.save(fig, "fig5_decomposition")

    rel_pre = (pre.max() - pre.min()) / t19
    rel_post = (post.max() - post.min()) / trend[trend.index.year.isin([2024, 2025])].mean()
    print(f"trend 2019={t19/1e6:.1f}M -> 2024-25={trend[trend.index.year.isin([2024,2025])].mean()/1e6:.1f}M")
    print(f"seasonal amplitude (relative to trend): {rel_pre:.1%} -> {rel_post:.1%}")
    print("wrote figures/fig5_decomposition.{png,pdf}")


if __name__ == "__main__":
    main()
