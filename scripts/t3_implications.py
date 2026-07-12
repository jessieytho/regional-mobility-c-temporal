"""Table 3 - Findings -> planning lever -> real agency move [Discussion].

The synthesis table that lands the "so what": each empirical finding from this study is
paired with the service-planning decision it informs and the actual MTA action already
taken (or, for SIR, the action the data implies). Not computed from the feeds; the agency
actions are cited from public MTA / NYS sources (see source tags; format Chicago
author-date in the manuscript). Writes tables/t3_implications.csv and prints markdown.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import config as C
import pandas as pd

ROWS = [
    dict(
        finding="Weekday peak flattened; weekday/Saturday gap narrowed (Subways 1.80x->1.51x); "
                "Mon/Fri sag with a Tue-Thu core (Fig 2, 3).",
        lever="Shift peak-only resources toward all-day / bidirectional service; flatter service "
              "profile to match a flatter demand profile.",
        agency_action="Grand Central Madison enabled a ~41% LIRR service increase (all-day + reverse "
                      "commute); weekend/off-peak service added on 12 subway lines, 2023-2024.",
        source="MTA/NYS 2025; GCM"),
    dict(
        finding="Weekend rose relative to weekday; annual seasonal swing compressed ~22%->~18% "
                "(Fig 3, 5) - the rhythm flattened at weekly and annual scales.",
        lever="Invest in weekend and off-peak frequency and span; stop keying service standards to "
              "pre-2020 peak-commute patterns.",
        agency_action="FY2024 budget added ~$35M for weekday-midday, weeknight, and weekend subway "
                      "service (multi-phase increases on 12 lines).",
        source="NYS FY2024; MTA/NYS 2025"),
    dict(
        finding="Mode-mix shift and hybrid commuting break the 5-day monthly-pass math (Fig 6; "
                "day-of-week core in Fig 2).",
        lever="Redesign fare products for infrequent / hybrid riders rather than 5-day commuters.",
        agency_action="CityTicket made permanent; 20-trip ticket introduced (2022) then discontinued; "
                      "pay-as-you-go fare capping (11th trip free in 14 days); monthlies held below "
                      "pre-COVID.",
        source="MTA fares"),
    dict(
        finding="Bus is the only rider mode below its 2022 level (-4.2% in 2024) and shed ~6 share "
                "points (Fig 4, 6).",
        lever="Redesign the bus network to match routes to changed travel; restore fare compliance.",
        agency_action="Queens Bus Network Redesign (largest in US, ~$34M/yr, all-day service, fully "
                      "implemented Sep 2025); Brooklyn redesign in draft; fare-free pilot (5 routes, "
                      "2023-24); fare-enforcement teams (2025 bus ridership +12%).",
        source="MTA 2025 (Queens BNR); MTA 2024 ridership"),
    dict(
        finding="Paratransit (AAR) surged ~+87% vs 2022 and is the only transit mode above its 2019 "
                "level (Fig 4) - the costliest, ADA-mandated, non-sheddable service.",
        lever="Manage paratransit capacity and cost as a growing, legally-required obligation; it "
              "cannot be shed to save money.",
        agency_action="Paratransit reached ~1.3M riders / 904k completed trips (June 2025), above "
                      "pre-COVID peaks, at 92% on-time.",
        source="MTA/NYS 2025"),
    dict(
        finding="Permanent modal shift to car: Bridges & Tunnels fully recovered to 2019 (~1.00) "
                "while every transit mode remains below 2019 (Fig 4).",
        lever="Use demand management / pricing to rebalance road vs transit and fund transit.",
        agency_action="Congestion pricing began Jan 5, 2025 ($9 cordon after a 2024 pause and revival); "
                      "early effect: reduced gridlock improved bus speeds.",
        source="MTA/NYS 2024-2025 (congestion pricing)"),
    dict(
        finding="Subway held service near 2019 while ridership sits ~76% of 2019: service-per-rider "
                "~1.3 vs 2019 (Fig 8, NTD VRM). Read against 2022, demand has outpaced VRM on every "
                "rail mode (Subway 0.81, LIRR 0.84, MNR 0.69).",
        lever="Maintain backbone coverage/reliability, but review all-day service intensity against "
              "unevenly recovered demand.",
        agency_action="Service largely maintained and selectively added (off-peak/weekend frequency "
                      "on ~12 lines, 2023-24).",
        source="NTD monthly VRM; NYS 2025"),
    dict(
        finding="SIR service now lags demand: service-per-rider fell from ~1.8x (trough) to ~0.83 as "
                "demand grew ~19% past 2022 while scheduled service stayed flat (Fig 7).",
        lever="Scale SIR scheduled service up to match rebounded demand (data-implied; no specific "
              "agency action identified).",
        agency_action="[Recommendation from this analysis - not an observed agency action.]",
        source="this study"),
]


def main():
    df = pd.DataFrame(ROWS)[["finding", "lever", "agency_action", "source"]]
    C.TABLES.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.TABLES / "t3_implications.csv", index=False)
    print(df.to_markdown(index=False))
    print("\nwrote tables/t3_implications.csv")


if __name__ == "__main__":
    main()
