"""Print EDA statistics and create the two wage-versus-rent graphs.

Run data_cleaning.py and wage_affordability.py before this script.
"""

import matplotlib.pyplot as plt
import pandas as pd


def main():
    data = pd.read_csv("affordability_by_year.csv")
    columns = ["minimum_wage_usd_per_hour", "monthly_rent",
               "monthly_income", "rent_share_pct"]

    print("Number of observations per city:")
    print(data["city"].value_counts())

    for city in ["Seattle", "New York City"]:
        # Sort years before plotting the lines.
        rows = data[data["city"] == city].sort_values("year")

        # These are the seven statistics used in the report tables.
        summary = rows[columns].describe().drop("count")
        print("\n" + city + " statistics:")
        print(summary.round(2))

        # Show each series' percentage change since 2017.
        wage = rows["minimum_wage_usd_per_hour"]
        rent = rows["monthly_rent"]
        wage_growth = (wage / wage.iloc[0] - 1) * 100
        rent_growth = (rent / rent.iloc[0] - 1) * 100

        plt.figure(figsize=(7.5, 3.7))
        plt.plot(rows["year"], wage_growth, marker="o",
                 label="Minimum wage")
        plt.plot(rows["year"], rent_growth, marker="o",
                 label="Reported rent")
        plt.title(city + ": Wage and Rent Growth, 2017–2025")
        plt.xlabel("Year")
        plt.ylabel("Change since 2017 (%)")
        plt.xticks(rows["year"])
        plt.grid(alpha=0.25)
        plt.legend()
        plt.tight_layout()

        if city == "Seattle":
            filename = "seattle_growth.png"
        else:
            filename = "nyc_growth.png"
        plt.savefig(filename, dpi=200)
        plt.close()
        print("Saved", filename)


if __name__ == "__main__":
    main()
