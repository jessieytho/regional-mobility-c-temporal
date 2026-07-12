"""Fig 1 - Regime change, not recovery (Introduction).

HONEST COMPOSITION: an observed-only systemwide rider total cannot span the shock,
because only Subways is observed before 2020 (Buses/LIRR/MNR/SIR observed from 2020-03).
So we plot:
  * the all-five-mode MTA rider total from 2020-03 onward (consistent composition), and
  * a Subways-only observed index carried back to 2017 as the pre-shock ANCHOR,
both indexed to 2022 = 100. The pre-2020 level therefore reads off Subways (observed),
not a composition-shifting total.

Feed: multigrain (grain='monthly'), measure_type=='estimated_ridership'.
"""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, viz, config as C
import matplotlib.pyplot as plt
import pandas as pd

SHOCK_START = pd.Timestamp("2020-03-01")


def main():
    viz.set_style()

    # Systemwide five-mode total, observed, from 2020-03 (consistent composition).
    total = io.rider_total_monthly(observed=True)
    total = total[total["period_start"] >= SHOCK_START]
    total = io.index_to_baseline(total, "value", C.BASELINE_PRIMARY)

    # Subways-only anchor, observed, full range (2017+): carries the pre-shock level.
    subway = io.mode_monthly(C.ANCHOR_MODE, observed=True)
    subway = io.index_to_baseline(subway, "value", C.BASELINE_PRIMARY)

    fig, ax = plt.subplots()
    ax.plot(subway["period_start"], subway["indexed"], color=viz.PALETTE[2], lw=1.2,
            ls="--", label="Subways only (observed, anchor)")
    ax.plot(total["period_start"], total["indexed"], color=viz.PALETTE[0], lw=1.8,
            label="MTA rider total, 5 modes (observed 2020-03+)")
    ax.axhline(100, color="grey", lw=0.8, ls=":")
    ax.set_ylabel("Index (2022 = 100)")
    ax.set_title("Recovery as regime change, not return to baseline")
    ax.legend(loc="lower right")
    viz.save(fig, "fig1_regime")

    # quick numeric read for the draft
    pre = subway[(subway["period_start"].dt.year.between(2017, 2019))]["indexed"].mean()
    recent = subway.tail(12)["indexed"].mean()
    print(f"Subways: 2017-2019 mean index = {pre:.1f}; trailing-12 mean = {recent:.1f} "
          f"(vs 2022=100). Pre-shock sat ~{pre-100:.0f} pts above the 2022 plateau.")
    print("wrote figures/fig1_regime.{png,pdf}")


if __name__ == "__main__":
    main()
