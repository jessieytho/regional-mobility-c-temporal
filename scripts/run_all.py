"""Regenerate every exhibit end-to-end.

Runs QA first, then each exhibit script. Stubs raise NotImplementedError until filled;
run_all reports which exhibits are ready vs pending so the build state is always visible.
"""
import importlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import qa

EXHIBITS = [
    "01_fig1_regime", "02_fig2_dow_profile", "03_fig6_daytype_ratios",
    "04_fig4_recovery_ratio", "05_fig5_decomposition", "06_fig6_modemix",
    "07_fig7_supply_demand", "08_fig4_supply_demand_systemwide",
    "t1_coverage", "t2_breaks", "t2b_break_robustness", "t3_implications",
]


def main():
    print("== QA ==")
    qa.main()
    print("\n== Exhibits ==")
    ready, pending = [], []
    for name in EXHIBITS:
        mod = importlib.import_module(f"scripts.{name}")
        try:
            mod.main()
            ready.append(name)
        except NotImplementedError:
            pending.append(name)
            print(f"  [pending] {name}")
    print(f"\n{len(ready)} ready, {len(pending)} pending.")

    print("\n== Regression check (headline numbers) ==")
    try:
        import scripts.check_numbers as cn
        cn.main()
    except Exception as e:  # pragma: no cover
        print(f"  check_numbers failed: {e}")


if __name__ == "__main__":
    main()
