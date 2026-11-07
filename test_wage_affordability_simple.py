"""Basic tests for the CSE 163 wage and rental affordability analysis.

Author: Rafay Farah
"""

import pandas as pd
from wage_affordability_simple import calculate_affordability


def main() -> None:
    """Check city/year matching and the monthly affordability calculation."""
    wages = pd.DataFrame({
        "city": ["Seattle", "New York City"],
        "year": [2025, 2025],
        "minimum_wage_usd_per_hour": [20.0, 15.0]
    })
    rents = pd.DataFrame({
        "city": ["Seattle", "New York City", "Seattle"],
        "year": [2025, 2025, 2024],
        "monthly_rent": [2000.0, 1300.0, 1500.0]
    })

    # The unmatched Seattle 2024 rent should not appear in the result.
    result = calculate_affordability(wages, rents)
    assert len(result) == 2

    # Check the wage and rent formula for Seattle.
    seattle = result[result["city"] == "Seattle"].iloc[0]
    assert seattle["monthly_income"] == 20 * 40 * 52 / 12
    expected = 2000 / (20 * 40 * 52 / 12) * 100
    assert abs(seattle["rent_share_pct"] - expected) < 0.001

    # The NYC row must use the NYC rent, not Seattle's rent.
    nyc = result[result["city"] == "New York City"].iloc[0]
    assert nyc["monthly_rent"] == 1300.0
    print("Tests passed!")


if __name__ == "__main__":
    main()
