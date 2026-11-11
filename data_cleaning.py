"""
Cleaning data of rental price in both Seattle and New York City
"""

import pandas as pd

SEA_RENTAL_FILE = "Datasets/SEA_rental_price.csv"
NYC_RENTAL_FILE = "Datasets/NYC_rental_price.csv"

def main():
    # Data cleaning for Seattle rental price
    sea_rental = pd.read_csv(SEA_RENTAL_FILE)

    # print(sea_rental["Tract Median Apartment Contract Rent per Unit"].isnull().sum())

    sea_rental =\
        sea_rental[["Year",
                    "Community Reporting Area Name",
                    "Tract Median Apartment Contract Rent per Square Foot",
                    "Tract Median Apartment Contract Rent per Unit"]]
    sea_rental = sea_rental[sea_rental[
        "Tract Median Apartment Contract Rent per Square Foot"] > 0]

    sea_rental.columns = ["year", "area_name",
                          "rental_price_sqft", "rental_price_unit"]
    sea_rental = sea_rental.iloc[::-1].reset_index(drop=True)

    sea_rental.to_csv("SEA_rental_cleaned.csv")

    sea_yearly_rent = sea_rental.groupby("year")\
        [["rental_price_sqft", "rental_price_unit"]].mean().reset_index()

    sea_yearly_rent.to_csv("SEA_yearly_rent.csv")


    # Data cleaning for NYC rental price
    nyc_rental = pd.read_csv(NYC_RENTAL_FILE)
    nyc_rental.columns = nyc_rental.columns.str.strip()

    #for col in ["areaName", "Borough", "areaType"]:
    #    nyc_rental[col] = nyc_rental[col].astype("string").str.strip()

    id_columns = ["areaName", "Borough", "areaType"]
    date_columns = [
        col for col in nyc_rental.columns if col not in id_columns
    ]

    for col in date_columns:
        nyc_rental[col] = pd.to_numeric(nyc_rental[col], errors="coerce")

    nyc_long = nyc_rental.melt(
        id_vars=["areaName", "Borough", "areaType"],
        value_vars=date_columns,
        var_name="Date",
        value_name="Rental_Price"
    )

    nyc_long["Date"] = pd.to_datetime(nyc_long["Date"])
    nyc_long["Year"] = nyc_long["Date"].dt.year
    nyc_long["Month"] = nyc_long["Date"].dt.month

    nyc_long = nyc_long.sort_values(
        ["Year", "Borough", "areaName", "Month"]
    ).reset_index(drop=True)

    borough_data = nyc_long[
        nyc_long["areaType"] == "borough"
    ]

    nyc_yearly_rent = (
        borough_data.groupby(
            ["Year", "Borough"])["Rental_Price"].mean().reset_index()
    )

    #missing_by_year = (
    #    nyc_long.groupby("Year")["Rental_Price"].apply(lambda x: x.isnull().sum())
    #)

    nyc_long.to_csv("NYC_rental_cleaned.csv")
    nyc_yearly_rent.to_csv("NYC_yearly_rent.csv")


if __name__ == "__main__":
    main()
