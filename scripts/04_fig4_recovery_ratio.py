"""Fig 4 - Recovery ratio by mode (permanent-loss vs transitional) [R2].

Per mode: trailing-12-month mean / 2022 mean (primary, observed) and / 2019 mean
(structural gap). vs-2019 is OBSERVED for Subways and Bridges & Tunnels only; for the
other modes the 2019 baseline is DERIVED and drawn with hollow markers + labeled.
Ratios are unit-free, so cross-mode comparison is firewall-safe.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, viz, config as C
import matplotlib.pyplot as plt
import numpy as np

MEASURE = {"Access-A-Ride": "scheduled_trips", "Bridges and Tunnels": "vehicle_traffic"}


def _ratios(service):
    measure = MEASURE.get(service, "estimated_ridership")
    s = io.mode_monthly(service, observed=True, measure_type=measure)
    if s.empty:
        return None
    recent = s.sort_values("period_start").tail(12)["value"].mean()
    m2022 = s[s["period_start"].dt.year == 2022]["value"].mean()
    obs2019 = service in C.OBSERVED_2019_MODES
    if obs2019:
        m2019 = s[s["period_start"].dt.year == 2019]["value"].mean()
    else:  # derived baseline: use all tiers for 2019
        a = io.mode_monthly(service, observed=False, measure_type=measure)
        m2019 = a[a["period_start"].dt.year == 2019]["value"].mean()
    return dict(service=service, vs2022=recent / m2022, vs2019=recent / m2019,
                obs2019=obs2019)


def main():
    viz.set_style()
    order = C.MTA_RIDER_MODES + ["Access-A-Ride", "Bridges and Tunnels"]
    rows = [r for r in (_ratios(m) for m in order) if r]
    rows.sort(key=lambda r: r["vs2019"])
    y = np.arange(len(rows))

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for i, r in enumerate(rows):
        ax.plot([r["vs2019"], r["vs2022"]], [i, i], color="0.7", lw=1, zorder=1)
        mfc19 = viz.PALETTE[6] if r["obs2019"] else "none"
        ax.scatter(r["vs2019"], i, s=55, color=viz.PALETTE[6], facecolor=mfc19,
                   zorder=3, label="_")
        ax.scatter(r["vs2022"], i, s=55, color=viz.PALETTE[5], zorder=3, label="_")
    ax.axvline(1.0, color="k", lw=0.9, ls=":")
    ax.set_yticks(y); ax.set_yticklabels([r["service"] for r in rows])
    ax.set_xlabel("recovery ratio (recent trailing-12 / baseline)")
    ax.set_title("Recovery by mode: vs 2019 (structural gap) and vs 2022 (trajectory)")
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="w", markerfacecolor=viz.PALETTE[6], label="vs 2019 (observed)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="none", markeredgecolor=viz.PALETTE[6], label="vs 2019 (derived baseline)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=viz.PALETTE[5], label="vs 2022 (observed)"),
    ], loc="lower right", fontsize=8)
    viz.save(fig, "fig4_recovery_ratio")
    for r in rows:
        print(f"  {r['service']:22s} vs2019={r['vs2019']:.3f} "
              f"({'obs' if r['obs2019'] else 'derived'})  vs2022={r['vs2022']:.3f}")
    print("wrote figures/fig4_recovery_ratio.{png,pdf}")


if __name__ == "__main__":
    main()
