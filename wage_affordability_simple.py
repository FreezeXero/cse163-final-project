"""Minimum-wage and rental affordability analysis for CSE 163.

Author: Rafay Farah
Run EDA.py first to create the team's cleaned rental CSV files.
"""

import pandas as pd
import plotly.express as px


def calculate_affordability(wages: pd.DataFrame,
                            rents: pd.DataFrame) -> pd.DataFrame:
    """Join rents with wages by city/year and calculate rent affordability."""
    # Match each city's rent to its wage for the same year.
    combined = wages.merge(rents, on=["city", "year"])

    # Assume 40 hours of paid work per week and 52 weeks per year.
    combined["monthly_income"] = (
        combined["minimum_wage_usd_per_hour"] * 40 * 52 / 12
    )

    # Percent of estimated gross (before-tax) monthly income spent on rent.
    combined["rent_share_pct"] = (
        combined["monthly_rent"] / combined["monthly_income"] * 100
    )
    return combined


def main() -> None:
    """Read team CSVs, compare rent affordability, and save a Plotly graph."""
    # Keep the wages and study years we need.
    wages = pd.read_csv("Datasets/minimum_wage.csv")
    wages = wages[["city", "year", "minimum_wage_usd_per_hour"]]
    wages = wages[(wages["year"] >= 2017) & (wages["year"] <= 2025)]

    # Roger's file already has average Seattle rent for each year.
    seattle = pd.read_csv("SEA_yearly_rent.csv")
    seattle = seattle[["year", "rental_price_unit"]]
    seattle.columns = ["year", "monthly_rent"]
    seattle["city"] = "Seattle"

    # Brooke's file has monthly NYC rents. Use only the citywide row.
    nyc = pd.read_csv("NYC_rental_cleaned.csv")
    nyc = nyc[(nyc["areaType"] == "city") & (nyc["areaName"] == "NYC")]
    nyc = nyc.groupby("Year")["Rental_Price"].mean().reset_index()
    nyc.columns = ["year", "monthly_rent"]
    nyc["city"] = "New York City"

    # Combine both cities, then match rent and wage using city and year.
    rents = pd.concat([seattle, nyc])
    combined = calculate_affordability(wages, rents)
    combined = combined.sort_values(["city", "year"])

    # Save the joined data so Roger and Brooke can use it in the report.
    combined.to_csv("affordability_by_year.csv", index=False)
    print("Joined city-year rows:", len(combined))
    print(combined.groupby("city")["rent_share_pct"].describe())

    # Note: Seattle contract rents and NYC asking rents are not identical.
    # Plot the descriptive comparison without treating it as a causal result.
    fig = px.line(combined, x="year", y="rent_share_pct", color="city",
                  markers=True,
                  title="Reported Rent as a Share of Gross Minimum-Wage Pay",
                  labels={"year": "Year",
                          "rent_share_pct": "Rent / gross income (%)",
                          "city": "City"})
    fig.write_html("rent_affordability.html")


if __name__ == "__main__":
    main()
