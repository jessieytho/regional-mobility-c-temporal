"""Shared plotting style, tuned for TRB embedding.

TRB papers are single-column, Times New Roman >=10pt, often printed grayscale.
Figures are embedded near their discussion and count toward the 20-page limit, so
keep them compact and legible at column width.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

# Colorblind- and grayscale-safe palette (Okabe-Ito), plus distinct line styles
# so series remain distinguishable in a printed grayscale copy.
PALETTE = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
LINESTYLES = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]

# Distinguish observed vs derived at a glance (derived = hollow / dashed).
OBSERVED_KW = dict(linestyle="-", marker="o", markerfacecolor="full")
DERIVED_KW = dict(linestyle="--", marker="o", markerfacecolor="none")


def set_style() -> None:
    mpl.rcParams.update({
        "figure.figsize": (6.5, 4.0),   # ~column width
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 9,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save(fig, name: str, tables_dir=None):
    from .config import FIGURES
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / f"{name}.png", bbox_inches="tight")
    fig.savefig(FIGURES / f"{name}.pdf", bbox_inches="tight")  # vector for the PDF submission
    plt.close(fig)
