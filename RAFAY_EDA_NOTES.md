# Rafay's Part 2 EDA Contribution — Minimum Wages and Rental Affordability

## Running the analysis

From the GitHub repository root, with the three provided raw CSVs inside `Datasets/`:

```bash
python EDA.py
python test_wage_affordability.py
python wage_affordability.py
```

The first command is Roger/Brooke's existing script and generates `SEA_yearly_rent.csv` and `NYC_rental_cleaned.csv`. The last command writes results into `wage_results/`. Install `plotly`, `pandas`, and `matplotlib` in the environment if needed. **Do not replace the teammates' `EDA.py` with any file from this folder.**

## Approach and joins

- `Datasets/minimum_wage.csv` contains **18 rows × 6 columns**, covering two cities and nine years (2017–2025); none of its six columns contain null values. One row represents a city and year, with a minimum-wage rate **as of January 1** and employer-category notes. All city/year pairs are unique and hourly wages are positive.
- Seattle rent comes from the team's `SEA_yearly_rent.csv`, which averages positive-rent census-tract *median contract rents per unit* by year. Tracts are **not weighted by number of rental units**. Roger's existing `EDA.py` filters on positive rent per square foot before averaging. Among **1,620 original Seattle tract-year rows for 2017–2025, 187 (11.5%) have zero rent per square foot and are excluded** by that existing cleaning step. These are zero/sentinel values, not pandas `NaN` cells.
- NYC rent comes from the `areaType == 'city'`, `areaName == 'NYC'` records of the team's `NYC_rental_cleaned.csv`, aggregated across the 12 months of each year. The selected **108 city-month observations from 2017–2025 contain no missing rent values** (even though the wider NYC neighborhood dataset has some). This is an **annual average of monthly median asking rents**, *not* an average of the five boroughs; a distinct citywide row exists in the raw StreetEasy data.
- Combine rent and minimum wages on `city` and `year`. The result is **18 city-year rows × 11 columns**, with **zero missing values**. A check raises an exception if any expected city-year has no matching rent, avoiding accidental omissions.
- `gross_monthly_income_usd` = hourly minimum wage × 40 hours/week × 52 weeks/year ÷ 12 months/year.
- `rent_share_pct` = 100 × reported monthly rent ÷ estimated **gross** monthly minimum-wage income.
- `work_hours_for_rent` = reported monthly rent ÷ hourly minimum wage.

**Critical limitations for the report:** These are descriptive hypothetical affordability ratios, not real household budgets. They omit taxes, hours worked, benefits, additional earners, and other housing costs. The wage schedule uses January 1 snapshots rather than a weighted annual average of changing legal rates. The Seattle **contract-rent** metric and NYC **asking-rent** metric are not interchangeable, so **do not treat the absolute cross-city gap as an apples-to-apples estimate**. For a more comparable cross-city affordability result, obtain ACS median gross rent for both cities, as proposed. This contribution therefore supports *exploratory* results and reveals a measurement limitation central to Research Question 3.

## Preliminary descriptive results (based on supplied data and existing cleaning code)

| City | 2017 hourly wage | 2025 hourly wage | 2017 rent | 2025 rent | 2017 rent share | 2025 rent share |
|---|---:|---:|---:|---:|---:|---:|
| Seattle | $15.00 | $20.76 | $1,629.91 | $1,858.75 | 62.69% | 51.65% |
| New York City | $11.00 | $16.50 | $2,774.50 | $3,873.33 | 145.52% | 135.43% |

From 2017 to 2025, Seattle's snapshot minimum wage rose **38.4%** while its unweighted tract-median rent measure increased **14.0%**; its hypothetical rent share declined approximately **11.0 percentage points**. NYC's snapshot minimum wage rose **50.0%** while its median-asking-rent measure rose **39.6%**; its rent share declined approximately **10.1 percentage points**. Do not interpret these as evidence of causation or of identical rental markets.

The three exported `*_summary.csv` files contain each city's seven-number summary (mean, sample standard deviation, minimum, 25th percentile, median, 75th percentile, maximum) for wages, rents, and rent shares.

## Visualizations for report

1. `wage_results/minimum_wages.png` — **Figure: Statutory Minimum Wage by City, 2017–2025.** *Caption:* Both cities raised their January 1 hourly minimum wages over the study window, with Seattle retaining a higher reported rate. This line chart uses a common USD/hour scale and shows the wage component of Research Question 1.
2. `wage_results/reported_rent.png` — **Figure: Reported Monthly Rent Trends, 2017–2025.** *Caption:* Reported rents rose across the study period, but the Seattle and NYC measures follow different rent definitions. This comparison is useful for describing within-series trends; direct dollar differences should not be interpreted as matched-city estimates.
3. `wage_results/rent_affordability.png` — **Figure: Rent as a Percentage of Estimated Gross Minimum-Wage Earnings.** *Caption:* Rent burdens calculated using January 1 minimum wages and reported rental statistics were lower in 2025 than 2017 within both measurement series. This derived-variable graph combines wage and rental data for Research Question 2; the comparability caveats still apply.

Plotly interactive versions are `minimum_wages.html`, `rent_toggle.html` (dropdown toggling USD prices vs change relative to 2017), and `affordability.html`. Use screenshots or the companion static PNGs inside `eda.pdf`; HTML interactivity does not transfer into PDFs.

## Tests and verification

Run `python test_wage_affordability.py` to check filtering, zero/null/duplicate protections, two-city merging, NYC citywide monthly-to-yearly aggregation (excluding borough rows), calculation of 40-hour full-time income and rent share, and incomplete-year failures. The script was also executed end to end with the supplied three CSVs and with Roger's current `EDA.py` logic. This verifies that the raw data produce the 18-row joined result and graphs. In the final report, cite this explicit test strategy; do not claim tests cover unverified ACS or causal analysis.

## Remaining group work

- Make sure the two original rental CSVs and wage CSV are available under the `Datasets/` folder when running from GitHub. The existing repo's `EDA.py` expects those exact paths, but the rental CSVs were not yet in `main` at the time this contribution was created.
- Add comparable ACS gross-rent data from the proposal, or explain any scope change in the report.
- Integrate the text, figures, initial dataset sizes/missingness and seven-number summaries into the group's `eda.pdf` and add its public GitHub URL.
- Remember: Part 2 asks for at least one analysis Python module and one test module; the final project will require at least two substantial **non-test** modules.
