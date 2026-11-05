import pandas as pd

SEA_RENTAL_NAME = "Datasets/SEA_rental_price.csv"

sea_rental_orig = pd.read_csv(SEA_RENTAL_NAME)
sea_rental =\
    sea_rental_orig[["Year",
                     "Tract Median Apartment Contract Rent per Square Foot",
                     "Tract Median Apartment Contract Rent per Unit"]]
sea_rental = sea_rental[sea_rental[
    "Tract Median Apartment Contract Rent per Square Foot"] > 0]
sea_rental = sea_rental.groupby("Year")
print(sea_rental.describe())


# Data cleaning for NY Dataset
ny_data = pd.read_csv("NYC_rental_price.csv")

ny_data.columns = ny_data.columns.str.strip()

for col in ["areaName", "Borough", "areaType"]:
    ny_data[col] = ny_data[col].astype("string").str.strip()


id_columns = ["areaName", "Borough", "areaType"]

date_columns = [
    col for col in ny_data.columns if col not in id_columns
]


for col in date_columns:
    ny_data[col] = pd.to_numeric(ny_data[col], errors="coerce")

ny_long = ny_data.melt(
    id_vars=["areaName", "Borough", "areaType"],
    value_vars=date_columns,
    var_name="Date",
    value_name="Rental_Price"
)


ny_long["Date"] = pd.to_datetime(ny_long["Date"])


ny_long["Year"] = ny_long["Date"].dt.year
ny_long["Month"] = ny_long["Date"].dt.month

ny_long = ny_long.sort_values(
    ["Year", "Borough", "areaName", "Month"]
)

borough_data = ny_long[
    ny_long["areaType"] == "borough"
]

yearly_rent = (
    borough_data.groupby(
        ["Year", "Borough"])["Rental_Price"].mean().reset_index()
)

missing_by_year = (
    ny_long.groupby("Year")["Rental_Price"].apply(lambda x: x.isnull().sum())
)

ny_long.to_csv("NYC_rental_cleaned.csv")

yearly_rent.to_csv("NYC_yearly_rent.csv")
