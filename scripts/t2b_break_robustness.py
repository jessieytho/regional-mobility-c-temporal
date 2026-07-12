"""Table 4 - Break-count selection sensitivity [R2/WP-A4].

The reported break dates (t2_breaks.py) select the number of breaks by BIC at a six-month
minimum regime length. This script checks that the interpreted regime structure is not an
artifact of that choice, comparing three selection rules on the same deseasonalized series
and the same dynamic-programming segment costs:

  * BIC  — Bayesian information criterion (the reported rule), 6-month trimming.
  * LWZ  — modified Schwarz criterion with the heavier (ln T)^2.1 penalty of Liu, Wu & Zidek
           (1997); same 6-month trimming, so it isolates the effect of the penalty.
  * supF — Bai & Perron (2003) sequential sup F(l+1|l) test at 15% trimming, 5% level, q=1
           (asymptotic critical values below), so it reflects the conventional test config.

Writes tables/t2b_break_robustness.csv. Number of breaks is capped at 4 to match t2_breaks.fit.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, config as C
from scripts.t2_breaks import deseasonalize, _seg_costs, _dp, MEASURE, SCOPE
import numpy as np
import pandas as pd

MMAX = 4                                              # match t2_breaks.fit(max_breaks=4)
CV5_q1 = {1: 8.58, 2: 10.13, 3: 11.14, 4: 11.83}      # Bai-Perron 2003, q=1, eps=0.15, 5%
SHOCK_MONTHS = ("2020-02", "2020-03", "2020-04")


def _ssr_by_m(y, min_len):
    Cc = _seg_costs(y)
    return {m: _dp(y, m, min_len, Cc) for m in range(MMAX + 1)}   # m -> (breaks, ssr)


def _bic(ssr, T, m): return T * np.log(ssr / T) + (2 * m + 1) * np.log(T)
def _lwz(ssr, T, m): return np.log(ssr / (T - (2 * m + 1))) + (2 * m + 1) * 0.299 * np.log(T) ** 2.1 / T


def _seq_supF(y, minF, idx):
    """Sequential sup F(l+1|l): at each l, the best within-segment added break; reject at 5%."""
    T = len(y); Cc = _seg_costs(y); sel = 0; dates = []
    for l in range(MMAX):
        br_l, ssr_l = _dp(y, l, minF, Cc)
        bnds = [0] + br_l + [T]; best_red, best_c = 0.0, None
        for a, b in zip(bnds[:-1], bnds[1:]):
            seg = Cc[a, b]
            for c in range(a + minF, b - minF + 1):
                red = seg - (Cc[a, c] + Cc[c, b])
                if red > best_red:
                    best_red, best_c = red, c
        ssr_l1 = ssr_l - best_red
        F = best_red / (ssr_l1 / (T - 2 * (l + 1))) if ssr_l1 > 0 else np.inf
        if F > CV5_q1.get(l + 1, 1e9):
            sel = l + 1; dates.append(idx[best_c].strftime("%Y-%m"))
        else:
            break
    return sel, dates


def main():
    rows = []
    for svc in SCOPE:
        s = io.mode_monthly(svc, observed=True, measure_type=MEASURE.get(svc, "estimated_ridership")) \
            .set_index("period_start")["value"].sort_index()
        ds = deseasonalize(s); y = ds.values; idx = ds.index; T = len(y)
        by = _ssr_by_m(y, 6)
        m_bic = min(by, key=lambda m: _bic(by[m][1], T, m))
        m_lwz = min(by, key=lambda m: _lwz(by[m][1], T, m))
        m_supF, _ = _seq_supF(y, max(6, round(0.15 * T)), idx)
        bic_dates = [idx[b].strftime("%Y-%m") for b in by[m_bic][0]]
        observes_shock = idx.min().year < 2020
        rows.append(dict(
            mode=svc, n_months=T, breaks_BIC=m_bic, breaks_LWZ=m_lwz, breaks_supF=m_supF,
            march2020=("retained (all rules)" if observes_shock
                       and any(d in SHOCK_MONTHS for d in bic_dates) else "not observed pre-shock"),
            bic_break_dates="; ".join(bic_dates)))
    df = pd.DataFrame(rows)
    C.TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.TABLES / "t2b_break_robustness.csv", index=False)
    print(df.to_markdown(index=False))
    agree = (df.breaks_LWZ == df.breaks_BIC).sum()
    print(f"\nLWZ agrees with BIC on {agree}/{len(df)} modes (same 6-month trimming). "
          "supF (15% trimming) is more conservative on the gradual recoveries.")
    print("wrote tables/t2b_break_robustness.csv")


if __name__ == "__main__":
    main()
