"""Fig 6 - Mode-mix evolution [R3].

Share of the MTA rider total by mode over time (riders only -> firewall-safe).
Observed 2020-03+ (pre-2020 mix would be derived; not shown). The composition story:
bus share swelled through the early recovery and has since receded as subway recovered
and bus ridership itself declined, while commuter rail steadily gained share.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, viz, config as C
import matplotlib.pyplot as plt


def main():
    viz.set_style()
    mg = io.observed_only(io.load_multigrain(grain="monthly"))
    mg = mg[(mg["measure_type"] == "estimated_ridership") & (mg["service"].isin(C.MTA_RIDER_MODES))]
    wide = mg.pivot_table(index="period_start", columns="service", values="value")[C.MTA_RIDER_MODES].dropna()
    share = wide.div(wide.sum(axis=1), axis=0) * 100
    share = share.rolling(3, min_periods=1).mean()  # light smoothing for readability
    # 2020 bus ridership was under-counted (fare-free rear-door boarding), which distorts the
    # mode mix; display from 2021 onward. Share-point stats below still use 2022 as the anchor.
    share = share[share.index >= "2021-01-01"]

    fig, ax = plt.subplots(figsize=(8, 4.3))
    ax.stackplot(share.index, [share[m] for m in C.MTA_RIDER_MODES],
                 labels=C.MTA_RIDER_MODES,
                 colors=[viz.PALETTE[i % len(viz.PALETTE)] for i in range(len(C.MTA_RIDER_MODES))],
                 alpha=0.9)
    ax.set_ylim(0, 100)
    ax.set_ylabel("share of MTA rider total (%)")
    ax.set_title("Mode-mix evolution (observed rider modes)")
    ax.legend(loc="center right", fontsize=8, framealpha=0.9)
    viz.save(fig, "fig6_modemix")

    base = share[share.index.year == 2022].mean()
    now = share[share.index.year == 2026].mean()
    print("share-pt change 2022->2026: " +
          "  ".join(f"{m[:4]}={now[m]-base[m]:+.1f}" for m in C.MTA_RIDER_MODES))
    print("wrote figures/fig6_modemix.{png,pdf}")


if __name__ == "__main__":
    main()
