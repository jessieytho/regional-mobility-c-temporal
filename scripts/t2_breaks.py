"""Table 2 - Structural break dates [R2].

Bai-Perron least-squares multiple-break estimation: the SSR-minimizing partition is
found by dynamic programming (Bai & Perron 2003), the number of breaks is chosen by BIC,
and each break date carries a 90% CI from a moving-block residual bootstrap (statsmodels
is unavailable offline; this implements the estimator directly in numpy).

Detection runs on the DESEASONALIZED monthly level (month-of-year effect removed).
Only Subways (2017+) and B&T (2016+) observe the pre-shock window, so only they can date
the March-2020 break; the other modes are observed from 2020-03, so their breaks are
recovery-era transitions only. Writes tables/t2_breaks.csv and prints markdown.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import dataio as io, config as C
import numpy as np
import pandas as pd

MEASURE = {"Access-A-Ride": "scheduled_trips", "Bridges and Tunnels": "vehicle_traffic"}
SCOPE = C.MTA_RIDER_MODES + ["Access-A-Ride", "Bridges and Tunnels"]
RNG = np.random.default_rng(42)


def deseasonalize(s):
    s = s.asfreq("MS").interpolate(limit_direction="both")
    detr = s - s.rolling(12, center=True).mean()
    seas = detr.groupby(detr.index.month).transform("mean")
    return (s - seas).dropna()


def _seg_costs(y):
    n = len(y); C_ = np.full((n, n + 1), np.inf)
    for i in range(n):
        cs = cs2 = 0.0
        for j in range(i + 1, n + 1):
            v = y[j - 1]; cs += v; cs2 += v * v; L = j - i
            C_[i, j] = cs2 - cs * cs / L
    return C_


def _dp(y, m, min_len, C_=None):
    n = len(y); C_ = _seg_costs(y) if C_ is None else C_; K = m + 1
    dp = np.full((K + 1, n + 1), np.inf); pt = np.full((K + 1, n + 1), -1, int)
    dp[0, 0] = 0.0
    for k in range(1, K + 1):
        for j in range(k * min_len, n + 1):
            for i in range((k - 1) * min_len, j - min_len + 1):
                c = dp[k - 1, i] + C_[i, j]
                if c < dp[k, j]: dp[k, j] = c; pt[k, j] = i
    j = n; k = K; bnds = []
    while k > 0:
        i = pt[k, j]; bnds.append((i, j)); j = i; k -= 1
    bnds = bnds[::-1]
    return [b[0] for b in bnds[1:]], dp[K, n]


def fit(y, max_breaks=4, min_len=6):
    C_ = _seg_costs(y); n = len(y); best = {}
    for m in range(max_breaks + 1):
        br, ssr = _dp(y, m, min_len, C_)
        bic = n * np.log(ssr / n) + (2 * m + 1) * np.log(n)
        best[m] = (bic, br)
    m_opt = min(best, key=lambda k: best[k][0])
    return m_opt, best[m_opt][1]


def bootstrap_ci(y, breaks, min_len=6, reps=200, block=6):
    if not breaks:
        return []
    bnds = [0] + breaks + [len(y)]
    fitted = np.concatenate([np.full(b - a, y[a:b].mean()) for a, b in zip(bnds[:-1], bnds[1:])])
    resid = y - fitted; n = len(y); m = len(breaks)
    samples = []
    for _ in range(reps):
        rb = []
        while len(rb) < n:
            st = RNG.integers(0, n - block + 1); rb.extend(resid[st:st + block])
        ystar = fitted + np.array(rb[:n])
        br, _ = _dp(ystar, m, min_len)
        if len(br) == m: samples.append(sorted(br))
    arr = np.array(samples)
    return [(int(np.percentile(arr[:, k], 5)), int(np.percentile(arr[:, k], 95))) for k in range(m)]


def main():
    rows = []
    for svc in SCOPE:
        s = io.mode_monthly(svc, observed=True, measure_type=MEASURE.get(svc, "estimated_ridership")) \
            .set_index("period_start")["value"].sort_index()
        ds = deseasonalize(s); y = ds.values; idx = ds.index
        m_opt, breaks = fit(y)
        cis = bootstrap_ci(y, breaks)
        pre_obs = idx.min().year < 2020
        for k, b in enumerate(breaks):
            lo, hi = cis[k] if k < len(cis) else (b, b)
            rows.append(dict(
                mode=svc, break_date=idx[b].strftime("%Y-%m"),
                ci90=f"{idx[min(lo,len(idx)-1)].strftime('%Y-%m')} to {idx[min(hi,len(idx)-1)].strftime('%Y-%m')}",
                pre_shock_observed="yes" if pre_obs else "no (obs from 2020-03)",
            ))
    df = pd.DataFrame(rows)
    C.TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.TABLES / "t2_breaks.csv", index=False)
    print(df.to_markdown(index=False))
    print("\nwrote tables/t2_breaks.csv")


if __name__ == "__main__":
    main()
