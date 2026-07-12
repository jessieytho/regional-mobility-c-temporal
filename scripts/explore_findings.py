"""Exploratory multivariate findings (PCA + rhythm metrics).

CAUTION on scale: with only ~5-7 systemwide modes, PCA structure is SUGGESTIVE, not
definitive. We lead with interpretable metrics and use PCA to confirm/quantify patterns
already visible in the raw ratios, not to discover latent structure on its own. vs-2019
is observed only for Subways and Bridges & Tunnels; all other vs-2019 baselines are
derived (directional only).
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, config as C
import pandas as pd, numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def pca_mode_comovement():
    modes = C.MTA_RIDER_MODES
    W = pd.DataFrame({m: io.mode_monthly(m, observed=True)
                      .set_index("period_start")["value"] for m in modes}).dropna()
    p = PCA().fit(StandardScaler().fit_transform(W.values))
    load = pd.DataFrame(p.components_[:2].T, index=modes, columns=["PC1", "PC2"])
    return p.explained_variance_ratio_, load, W.shape


def pca_rhythm_mix():
    dt = io.observed_only(io.load_daytype(grain="monthly"))
    dt = dt[dt["service"].isin(C.MTA_RIDER_MODES)]
    piv = dt.pivot_table(index=["service", "period_start"], columns="day_type",
                         values="avg_per_day")[C.DAY_TYPES].dropna()
    shares = piv.div(piv.sum(axis=1), axis=0)
    Z = StandardScaler().fit_transform(shares.values)
    p = PCA().fit(Z)
    score = pd.Series(PCA(n_components=1).fit_transform(Z).ravel(), index=shares.index)
    return p.explained_variance_ratio_, pd.DataFrame(
        p.components_[:2].T, index=C.DAY_TYPES, columns=["PC1", "PC2"]), score, piv


def main():
    ev, load, shape = pca_mode_comovement()
    print(f"[PCA-1 mode co-movement] {shape[0]} months x {shape[1]} modes")
    print(f"  variance: PC1={ev[0]:.1%}, PC2={ev[1]:.1%}")
    print("  PC2 loadings (divergence axis):")
    print(load["PC2"].round(2).to_string().replace("\n", "\n    "))

    ev2, load2, score, piv = pca_rhythm_mix()
    print(f"\n[PCA-2 rhythm mix] variance PC1={ev2[0]:.1%} (weekday<->weekend tilt)")
    g = score.loc["Subways"]
    print(f"  Subways rhythm index: pre-2020={g[g.index.year<2020].mean():+.2f} "
          f"-> 2024+={g[g.index.year>=2024].mean():+.2f}")

    print("\n[Weekday/Saturday premium, observed]")
    for m in C.MTA_RIDER_MODES:
        if m not in piv.index.get_level_values(0):
            continue
        r = (piv.loc[m]["Weekday"] / piv.loc[m]["Saturday"])
        pre = r[r.index.year.isin([2017, 2018, 2019])].mean()
        rec = r[r.index.year >= 2024].mean()
        pre_s = f"{pre:.2f}" if not np.isnan(pre) else "NA(obs2020+)"
        print(f"  {m:22s} pre={pre_s}  2024+={rec:.2f}")


if __name__ == "__main__":
    main()
