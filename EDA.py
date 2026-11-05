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
