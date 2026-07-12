"""Single source of truth for paths, mode lists, baselines, and tier rules.

Every analysis script imports from here so the locked scope decisions live in one place.
"""
from pathlib import Path

# --- paths ---
ROOT = Path(__file__).resolve().parent.parent
FEEDS = ROOT / "data" / "feeds"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

DAILY_CSV = FEEDS / "mta_chart_feed_daily.csv"
MULTIGRAIN_CSV = FEEDS / "mta_chart_feed_multigrain.csv"
DAYTYPE_CSV = FEEDS / "mta_chart_feed_daytype.csv"

# --- baselines (locked) ---
BASELINE_PRIMARY = 2022      # observed-to-observed trajectory read, all modes
BASELINE_STRUCTURAL = 2019   # structural gap; observed only for the modes below
OBSERVED_2019_MODES = ["Subways", "Bridges and Tunnels"]  # everyone else: 2019 is DERIVED
ANCHOR_MODE = "Subways"      # only rider mode with observed 2017-2019 structure

# --- mode groupings ---
# Core MTA rider modes (measure_type == 'estimated_ridership', unit 'riders').
# These are the only series summable into a rider total / mode-share (unit firewall).
MTA_RIDER_MODES = ["Subways", "Buses", "LIRR", "Metro-North", "Staten Island Railway"]

# Regional comparators — also 'estimated_ridership', but derived + flat-disaggregated:
# LEVEL comparison only, never day-type/rhythm. Several are stale (check per series).
REGIONAL_RIDER_MODES = [
    "PATH", "NJ Transit Rail", "NJ Transit Bus", "NJ Transit Demand Response",
    "NYC Ferry", "Staten Island Ferry", "Roosevelt Island Tram",
]

# Own-axis measures (never summed with riders or each other):
AAR = "Staten Island Railway"  # placeholder guard; AAR handled explicitly below
PARATRANSIT_AAR = "Access-A-Ride"          # measure_type 'scheduled_trips', unit 'trips'
BT = "Bridges and Tunnels"                 # measure_type 'vehicle_traffic', unit 'vehicles'
SIR_DEMAND = "Staten Island Railway"       # measure_type 'estimated_ridership'
SIR_SUPPLY = "SIR Scheduled Trips"         # measure_type 'scheduled_service', DERIVED (timetable)

# Study B services present in the feed but OUT OF SCOPE for C:
STUDY_B_EXCLUDE = ["CBD Entries", "CRZ Entries", "CBD For-Hire Trips", "CBD VMT"]

# --- day types ---
DAY_TYPES = ["Weekday", "Saturday", "Sunday-Holiday"]
DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# --- pre-shock / current analysis windows ---
PRESHOCK_YEARS = (2017, 2019)   # observed only for ANCHOR_MODE and BT
CURRENT_WINDOW_MONTHS = 12      # trailing months for "current era" profiles/ratios
LIRR_SUPPLY = "LIRR Operated Trips"  # operated_service/train_trips, derived_lirr_supply (73th-g5ad)

# --- systemwide supply from NTD vehicle revenue-miles (derived_ntd_vrm) ---
# measure_type 'vehicle_revenue_miles'; unit car_revenue_miles (rail) / vehicle_revenue_miles (bus)
NTD_VRM_SERVICES = ["Subways", "Buses", "LIRR", "Metro-North"]  # service names in the feed
NTD_VRM_BASIS = "derived_ntd_vrm"
