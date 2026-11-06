"""CSE 163 final project: minimum wages and rental affordability.

Author: Rafay Farah

Combine annual Seattle/NYC rent data with minimum-wage records from
2017-2025. Wage estimates assume 40 paid hours per week, 52 weeks per year.
Income is gross (before tax); differences in rent definitions mean the
resulting city comparisons are descriptive, not directly equivalent.

Run EDA.py first to create SEA_yearly_rent.csv and NYC_rental_cleaned.csv.
Then run this file from the repository root.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go


WAGE_FILE = "Datasets/minimum_wage.csv"
SEATTLE_FILE = "SEA_yearly_rent.csv"
NYC_FILE = "NYC_rental_cleaned.csv"
OUTPUT_DIR = "wage_results"

START_YEAR = 2017
END_YEAR = 2025
HOURS_PER_WEEK = 40
WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12
CITIES = ["Seattle", "New York City"]


def check_columns(data: pd.DataFrame, required: list[str]) -> None:
    """Raise ValueError if data is missing any expected columns."""
    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def clean_minimum_wages(data: pd.DataFrame) -> pd.DataFrame:
    """Keep one valid minimum-wage observation per city and year.

    Preserve the January 1 snapshot and employer-category descriptions,
    which explain how the statutory wages should be interpreted.
    """
    required = ["city", "year", "minimum_wage_usd_per_hour",
                "snapshot_date", "employer_category", "source_url"]
    check_columns(data, required)

    wages = data[required].copy()
    wages = wages[wages["city"].isin(CITIES)]
    wages = wages[wages["year"].between(START_YEAR, END_YEAR)]

    if wages[required].isna().any().any():
        raise ValueError("Minimum-wage records contain missing values.")
    if wages.duplicated(subset=["city", "year"]).any():
        raise ValueError("Duplicate city-year minimum-wage records found.")
    if (wages["minimum_wage_usd_per_hour"] <= 0).any():
        raise ValueError("Minimum-wage values must be positive.")

    wages = wages.sort_values(["city", "year"]).copy()
    wages["gross_monthly_income_usd"] = (
        wages["minimum_wage_usd_per_hour"] * HOURS_PER_WEEK
        * WEEKS_PER_YEAR / MONTHS_PER_YEAR
    )
    return wages


def prepare_seattle_rent(data: pd.DataFrame) -> pd.DataFrame:
    """Use Roger's annual average of Seattle tract median contract rents."""
    check_columns(data, ["year", "rental_price_unit"])
    seattle = data[["year", "rental_price_unit"]].copy()
    seattle = seattle.rename(columns={"rental_price_unit": "monthly_rent_usd"})
    seattle["city"] = "Seattle"
    seattle["rent_definition"] = (
        "Unweighted mean of tract median contract rents"
    )
    return seattle


def prepare_nyc_rent(data: pd.DataFrame) -> pd.DataFrame:
    """Average monthly NYC-wide median asking rents within each year.

    Use StreetEasy's dedicated city-level row, not an unweighted mean
    of individual boroughs or neighborhoods.
    """
    check_columns(data, ["Year", "areaType", "areaName", "Rental_Price"])
    city_months = data[
        (data["areaType"] == "city") & (data["areaName"] == "NYC")
    ].copy()
    city_months = city_months[
        city_months["Year"].between(START_YEAR, END_YEAR)
    ]
    if city_months.empty:
        raise ValueError("No NYC city-wide rental records were found.")

    nyc = city_months.groupby("Year", as_index=False)["Rental_Price"].mean()
    nyc = nyc.rename(columns={"Year": "year",
                              "Rental_Price": "monthly_rent_usd"})
    nyc["city"] = "New York City"
    nyc["rent_definition"] = "Annual mean of monthly median asking rents"
    return nyc


def combine_wages_and_rents(wages: pd.DataFrame,
                            seattle_rent: pd.DataFrame,
                            nyc_rent: pd.DataFrame) -> pd.DataFrame:
    """Join annual rents to wages and calculate pretax affordability.

    The rent-share percentage describes how much gross monthly income
    would go toward the reported rent for a hypothetical full-time worker.
    It is not an estimate of disposable income or causal wage effects.
    """
    rents = pd.concat([seattle_rent, nyc_rent], ignore_index=True)
    rents = rents[rents["year"].between(START_YEAR, END_YEAR)].copy()
    if rents[["city", "year", "monthly_rent_usd"]].isna().any().any():
        raise ValueError("City-year rents contain missing values.")
    if rents.duplicated(subset=["city", "year"]).any():
        raise ValueError("Duplicate city-year rental records found.")
    if (rents["monthly_rent_usd"] <= 0).any():
        raise ValueError("Rents must be positive after cleaning.")

    combined = pd.merge(wages, rents, on=["city", "year"], how="inner")
    if len(combined) != len(wages):
        raise ValueError("Some wage years are missing matched rental data.")
    combined = combined.sort_values(["city", "year"]).copy()
    combined["rent_share_pct"] = (
        combined["monthly_rent_usd"]
        / combined["gross_monthly_income_usd"] * 100
    )
    combined["work_hours_for_rent"] = (
        combined["monthly_rent_usd"]
        / combined["minimum_wage_usd_per_hour"]
    )
    return combined


def seven_number_summary(data: pd.DataFrame,
                         value: str) -> pd.DataFrame:
    """Report mean, std, min, quartiles, and max for each city."""
    check_columns(data, ["city", value])
    stats = data.groupby("city")[value].describe()
    return stats[["mean", "std", "min", "25%", "50%", "75%", "max"]]


def save_interactive_plots(combined: pd.DataFrame) -> None:
    """Save Plotly HTML charts, including an absolute/relative rent toggle."""
    fig_rent = go.Figure()
    for city in CITIES:
        rows = combined[combined["city"] == city].sort_values("year")
        baseline = rows.loc[rows["year"] == START_YEAR,
                            "monthly_rent_usd"].iloc[0]
        percent_change = (rows["monthly_rent_usd"] / baseline - 1) * 100
        fig_rent.add_trace(go.Scatter(
            x=rows["year"], y=rows["monthly_rent_usd"],
            name=city, mode="lines+markers"
        ))
        fig_rent.add_trace(go.Scatter(
            x=rows["year"], y=percent_change,
            name=city, mode="lines+markers", visible=False
        ))

    fig_rent.update_layout(
        title="Reported Rent Trends (Two Different Rent Definitions)",
        xaxis_title="Year", yaxis_title="Monthly rent (USD)",
        updatemenus=[{"buttons": [
            {"label": "Rent (USD/month)", "method": "update",
             "args": [{"visible": [True, False, True, False]},
                      {"yaxis": {"title": "Monthly rent (USD)"}}]},
            {"label": "Change since 2017 (%)", "method": "update",
             "args": [{"visible": [False, True, False, True]},
                      {"yaxis": {"title": "Change since 2017 (%)"}}]}
        ]}]
    )
    fig_rent.write_html(f"{OUTPUT_DIR}/rent_toggle.html")

    fig_afford = go.Figure()
    fig_wage = go.Figure()
    for city in CITIES:
        rows = combined[combined["city"] == city].sort_values("year")
        fig_afford.add_trace(go.Scatter(
            x=rows["year"], y=rows["rent_share_pct"],
            name=city, mode="lines+markers"
        ))
        fig_wage.add_trace(go.Scatter(
            x=rows["year"], y=rows["minimum_wage_usd_per_hour"],
            name=city, mode="lines+markers"
        ))
    fig_afford.update_layout(
        title="Reported Rent as % of Gross Minimum-Wage Income",
        xaxis_title="Year", yaxis_title="Rent / gross monthly income (%)"
    )
    fig_wage.update_layout(
        title="Statutory Minimum Wage (January 1 Snapshots)",
        xaxis_title="Year", yaxis_title="Hourly wage (USD)"
    )
    fig_afford.write_html(f"{OUTPUT_DIR}/affordability.html")
    fig_wage.write_html(f"{OUTPUT_DIR}/minimum_wages.html")


def save_report_plots(combined: pd.DataFrame) -> None:
    """Save static figures for embedding in the EDA PDF report."""
    for filename, column, title, ylabel in [
        ("minimum_wages.png", "minimum_wage_usd_per_hour",
         "Minimum Wages, 2017-2025", "Hourly wage (USD)"),
        ("rent_affordability.png", "rent_share_pct",
         "Reported Rent / Gross Minimum-Wage Income", "Percent (%)"),
        ("reported_rent.png", "monthly_rent_usd",
         "Reported Rents (Different Definitions)", "Monthly rent (USD)"),
    ]:
        fig, ax = plt.subplots(figsize=(8, 4.8))
        for city in CITIES:
            rows = combined[combined["city"] == city].sort_values("year")
            ax.plot(rows["year"], rows[column], marker="o", label=city)
        ax.set_title(title)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.legend()
        fig.tight_layout()
        fig.savefig(f"{OUTPUT_DIR}/{filename}", dpi=160)
        plt.close(fig)


def main() -> None:
    """Load collaborator outputs, analyze joined records, and save results."""
    wages_raw = pd.read_csv(WAGE_FILE)
    seattle_raw = pd.read_csv(SEATTLE_FILE)
    nyc_raw = pd.read_csv(NYC_FILE)

    wages = clean_minimum_wages(wages_raw)
    seattle = prepare_seattle_rent(seattle_raw)
    nyc = prepare_nyc_rent(nyc_raw)
    combined = combine_wages_and_rents(wages, seattle, nyc)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    combined.to_csv(f"{OUTPUT_DIR}/affordability_by_year.csv", index=False)
    for column in ["minimum_wage_usd_per_hour", "monthly_rent_usd",
                   "rent_share_pct"]:
        seven_number_summary(combined, column).to_csv(
            f"{OUTPUT_DIR}/{column}_summary.csv"
        )

    save_interactive_plots(combined)
    save_report_plots(combined)

    print(f"Minimum-wage dataset: {len(wages_raw)} rows, "
          f"{len(wages_raw.columns)} columns")
    print("Missing wage values by column:")
    print(wages_raw.isna().sum().to_string())
    print(f"Joined city-year dataset: {len(combined)} rows, "
          f"{len(combined.columns)} columns")
    print("Missing joined values by column:")
    print(combined.isna().sum().to_string())
    print("2025 affordability snapshot (gross income, not take-home pay):")
    print(combined.loc[combined["year"] == 2025, [
        "city", "minimum_wage_usd_per_hour", "monthly_rent_usd",
        "gross_monthly_income_usd", "rent_share_pct"
    ]].to_string(index=False))
    print(f"Saved plots, summaries, and combined data to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
