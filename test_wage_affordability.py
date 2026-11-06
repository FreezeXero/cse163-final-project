"""Tests for the CSE 163 minimum-wage and affordability analysis.

Author: Rafay Farah

Run with: python test_wage_affordability.py
"""

import pandas as pd

from wage_affordability import (
    check_columns, clean_minimum_wages, prepare_seattle_rent,
    prepare_nyc_rent, combine_wages_and_rents, seven_number_summary
)


def test_clean_minimum_wages() -> None:
    """Test year filtering, monthly pay, and missing data handling."""
    data = pd.DataFrame({
        "city": ["Seattle", "New York City", "Seattle"],
        "year": [2017, 2017, 2016],
        "minimum_wage_usd_per_hour": [15.0, 11.0, 13.0],
        "snapshot_date": ["2017-01-01", "2017-01-01", "2016-01-01"],
        "employer_category": ["large", "large", "large"],
        "source_url": ["source", "source", "source"]
    })
    result = clean_minimum_wages(data)
    assert len(result) == 2
    assert result["year"].min() == 2017
    seattle = result[result["city"] == "Seattle"].iloc[0]
    assert seattle["gross_monthly_income_usd"] == 15 * 40 * 52 / 12

    missing = data.copy()
    missing.loc[0, "minimum_wage_usd_per_hour"] = None
    try:
        clean_minimum_wages(missing)
        assert False, "Missing wages should cause a ValueError"
    except ValueError:
        pass


def test_joins_and_affordability() -> None:
    """Test both city joins and the rent-to-income formula."""
    wages = pd.DataFrame({
        "city": ["Seattle", "New York City"],
        "year": [2017, 2017],
        "minimum_wage_usd_per_hour": [15.0, 11.0],
        "gross_monthly_income_usd": [2600.0, 1906.6666666666667]
    })
    seattle = prepare_seattle_rent(pd.DataFrame({
        "year": [2017], "rental_price_unit": [1300.0]
    }))
    nyc = prepare_nyc_rent(pd.DataFrame({
        "Year": [2017, 2017, 2017],
        "areaType": ["city", "city", "borough"],
        "areaName": ["NYC", "NYC", "Queens"],
        "Rental_Price": [2000.0, 2400.0, 1000.0]
    }))
    combined = combine_wages_and_rents(wages, seattle, nyc)
    assert len(combined) == 2
    sea_row = combined[combined["city"] == "Seattle"].iloc[0]
    assert sea_row["rent_share_pct"] == 50.0
    nyc_row = combined[combined["city"] == "New York City"].iloc[0]
    assert nyc_row["monthly_rent_usd"] == 2200.0
    assert abs(nyc_row["rent_share_pct"] - (2200 / (11 * 40 * 52 / 12))
               * 100) < 0.0001

    assert set(seven_number_summary(combined, "rent_share_pct").columns) == {
        "mean", "std", "min", "25%", "50%", "75%", "max"
    }


def test_missing_year_and_columns() -> None:
    """Ensure incomplete input cannot silently generate misleading joins."""
    try:
        check_columns(pd.DataFrame({"year": [2017]}), ["year", "city"])
        assert False, "Missing columns should cause a ValueError"
    except ValueError:
        pass

    wages = pd.DataFrame({
        "city": ["Seattle", "New York City"],
        "year": [2017, 2017],
        "minimum_wage_usd_per_hour": [15, 11],
        "gross_monthly_income_usd": [2600, 1906.6666666666667]
    })
    seattle = prepare_seattle_rent(pd.DataFrame({
        "year": [2017], "rental_price_unit": [1300]
    }))
    empty_nyc = pd.DataFrame({
        "year": [], "monthly_rent_usd": [], "city": [],
        "rent_definition": []
    })
    try:
        combine_wages_and_rents(wages, seattle, empty_nyc)
        assert False, "A missing NYC year should cause a ValueError"
    except ValueError:
        pass


def main() -> None:
    """Run tests for wage cleaning, city joins, and calculated results."""
    test_clean_minimum_wages()
    test_joins_and_affordability()
    test_missing_year_and_columns()
    print("All wage-affordability tests passed!")


if __name__ == "__main__":
    main()
