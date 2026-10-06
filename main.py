import pandas as pd
import numpy as np
import re
from pathlib import Path


# ============================================================
# MARKETLENS
# Indian Market Expansion Intelligence
#
# Census + MoSPI Economic Data
# Geographic normalization
# Market opportunity scoring
# Sensitivity analysis
# ============================================================


# ============================================================
# 1. FILE PATHS
# ============================================================

CENSUS_FILE = Path(
    "c:/Users/ADITYA PRATAP SINGH/Downloads/"
    "2011-IndiaStateDistSbDistTwn-0000.xlsx"
)

ECONOMIC_FILE = Path(
    "data/State_wise_SDP-15042026_PCNSDP_Current.xlsx"
)

OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


CITY_OUTPUT = OUTPUT_DIR / "marketlens_city_data.csv"
MODEL_OUTPUT = OUTPUT_DIR / "marketlens_model_data.csv"
SENSITIVITY_OUTPUT = (
    OUTPUT_DIR / "marketlens_sensitivity_analysis.csv"
)


# ============================================================
# 2. LOAD CENSUS DATA
# ============================================================

print("Loading Census data...")

df = pd.read_excel(CENSUS_FILE)

print(f"Raw Census records: {len(df):,}")


# ============================================================
# 3. SELECT REQUIRED COLUMNS
# ============================================================

city_data = df[
    [
        "State",
        "District",
        "Name",
        "Level",
        "TRU",
        "TOT_P",
        "P_LIT"
    ]
].copy()


# ============================================================
# 4. KEEP TOWN / CITY RECORDS
# ============================================================

city_data = city_data[
    city_data["Level"] == "TOWN"
].copy()


# ============================================================
# 5. CLEAN NUMERIC DATA
# ============================================================

for column in [
    "State",
    "District",
    "TOT_P",
    "P_LIT"
]:
    city_data[column] = pd.to_numeric(
        city_data[column],
        errors="coerce"
    )


city_data["Name"] = (
    city_data["Name"]
    .astype(str)
    .str.strip()
)


# ============================================================
# 6. REMOVE INVALID RECORDS
# ============================================================

city_data = city_data.dropna(
    subset=[
        "State",
        "District",
        "Name",
        "TOT_P",
        "P_LIT"
    ]
).copy()


city_data = city_data[
    city_data["TOT_P"] > 0
].copy()


# Literacy population cannot be negative
city_data["P_LIT"] = (
    city_data["P_LIT"].clip(lower=0)
)


# Literacy population cannot exceed total population
city_data["P_LIT"] = np.minimum(
    city_data["P_LIT"],
    city_data["TOT_P"]
)


# ============================================================
# 7. STATE CODE → STATE NAME
# ============================================================

state_names = {

    1: "Jammu and Kashmir",
    2: "Himachal Pradesh",
    3: "Punjab",
    4: "Chandigarh",
    5: "Uttarakhand",
    6: "Haryana",
    7: "Delhi",
    8: "Rajasthan",
    9: "Uttar Pradesh",
    10: "Bihar",
    11: "Sikkim",
    12: "Arunachal Pradesh",
    13: "Nagaland",
    14: "Manipur",
    15: "Mizoram",
    16: "Tripura",
    17: "Meghalaya",
    18: "Assam",
    19: "West Bengal",
    20: "Jharkhand",
    21: "Odisha",
    22: "Chhattisgarh",
    23: "Madhya Pradesh",
    24: "Gujarat",
    25: "Daman and Diu",
    26: "Dadra and Nagar Haveli",
    27: "Maharashtra",
    28: "Andhra Pradesh",
    29: "Karnataka",
    30: "Goa",
    31: "Lakshadweep",
    32: "Kerala",
    33: "Tamil Nadu",
    34: "Puducherry",
    35: "Andaman and Nicobar Islands",
    36: "Telangana",
    37: "Ladakh"
}


city_data["State"] = pd.to_numeric(
    city_data["State"],
    errors="coerce"
)

city_data = city_data[
    city_data["State"].notna()
].copy()

city_data["State"] = (
    city_data["State"]
    .astype(int)
)

city_data["state_name"] = (
    city_data["State"]
    .map(state_names)
)

city_data = city_data[
    city_data["state_name"].notna()
].copy()


# ============================================================
# 8. URBAN MARKET NORMALIZATION
# ============================================================

def normalize_city_name(name):

    name = str(name).strip()

    # Remove Census administrative suffixes
    suffixes = [
        r"\s*\(M Corp\. \+ OG\)",
        r"\s*\(M Corp\.\)",
        r"\s*\(Part\)",
        r"\s*\(CMC \+ OG\)",
        r"\s*\(CMC\)",
        r"\s*\(M\)",
        r"\s*\(MC\)",
        r"\s*\(N\)"
    ]

    for suffix in suffixes:
        name = re.sub(
            suffix,
            "",
            name,
            flags=re.IGNORECASE
        )

    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    # Historical Census spellings
    aliases = {

        "Ahmadabad": "Ahmedabad",
        "Mysore": "Mysuru",
        "Mangalore": "Mangaluru",
        "Belgaum": "Belagavi",
        "Bangalore": "Bengaluru",
        "Calicut": "Kozhikode",
        "Cochin": "Kochi",
        "Trivandrum": "Thiruvananthapuram",
        "Baroda": "Vadodara",
        "Poona": "Pune"
    }

    return aliases.get(name, name)


city_data["urban_market"] = (
    city_data["Name"]
    .apply(normalize_city_name)
)


# ============================================================
# 9. AGGREGATE INTO URBAN MARKETS
#
# State + urban market is used rather than
# State + District + urban market so metropolitan
# areas split across Census districts can be combined.
# ============================================================

city_data = (
    city_data
    .groupby(
        [
            "State",
            "state_name",
            "urban_market"
        ],
        as_index=False
    )
    .agg(
        population=("TOT_P", "sum"),
        literate_population=("P_LIT", "sum"),
        census_records=("Name", "size"),
        source_names=(
            "Name",
            lambda x: " | ".join(
                sorted(set(x.astype(str)))
            )
        )
    )
)


# Final market name
city_data["Name"] = city_data["urban_market"]


# Flag markets created from multiple Census records
city_data["geography_merged"] = (
    city_data["census_records"] > 1
)


print("\n" + "=" * 75)
print("URBAN MARKET NORMALIZATION")
print("=" * 75)

print(
    f"Urban market records: {len(city_data):,}"
)

print(
    "Markets formed from multiple Census records:",
    f"{city_data['geography_merged'].sum():,}"
)


# ============================================================
# 10. CALCULATE LITERACY RATE
# ============================================================

city_data["literacy_rate"] = (
    city_data["literate_population"]
    /
    city_data["population"]
    * 100
)

city_data["literacy_rate"] = (
    city_data["literacy_rate"]
    .clip(0, 100)
)


# ============================================================
# 11. SAVE CLEAN CITY DATA
# ============================================================

city_data.to_csv(
    CITY_OUTPUT,
    index=False
)


# ============================================================
# 12. LOAD MoSPI ECONOMIC DATA
# ============================================================

print("Loading economic data...")

economic_raw = pd.read_excel(
    ECONOMIC_FILE,
    sheet_name="PC curr.",
    header=None
)

print("Economic dataset loaded.")


# ============================================================
# 13. FIND ECONOMIC HEADER
# ============================================================

header_row = None

for i in range(
    min(15, len(economic_raw))
):

    values = (
        economic_raw
        .iloc[i]
        .astype(str)
        .str.strip()
        .tolist()
    )

    if "State\\UT" in values:
        header_row = i
        break


if header_row is None:

    raise ValueError(
        "Could not find State\\UT in economic dataset."
    )


print(
    f"Economic data header found at row: {header_row}"
)


# ============================================================
# 14. EXTRACT ECONOMIC COLUMNS
# ============================================================

header_values = (
    economic_raw
    .iloc[header_row]
    .astype(str)
    .str.strip()
    .tolist()
)


state_index = None
year_index = None


for index, value in enumerate(header_values):

    if value == "State\\UT":
        state_index = index
        break


if state_index is None:

    raise ValueError(
        "State\\UT column not found."
    )


# First 2025-26 column = PCNSDP current-price series
for index, value in enumerate(header_values):

    if value == "2025-26":
        year_index = index
        break


if year_index is None:

    raise ValueError(
        "2025-26 column not found."
    )


economic = economic_raw.iloc[
    header_row + 1:
].copy()


economic = economic.iloc[
    :,
    [state_index, year_index]
].copy()


economic.columns = [
    "state_name",
    "pcnsdp_2025_26"
]


# ============================================================
# 15. CLEAN ECONOMIC DATA
# ============================================================

economic["state_name"] = (
    economic["state_name"]
    .astype(str)
    .str.strip()
)

economic["pcnsdp_2025_26"] = pd.to_numeric(
    economic["pcnsdp_2025_26"],
    errors="coerce"
)

economic = economic.dropna(
    subset=[
        "state_name",
        "pcnsdp_2025_26"
    ]
).copy()


# ============================================================
# 16. STANDARDIZE STATE NAMES
# ============================================================

state_name_fixes = {

    "Andaman & Nicobar Islands":
        "Andaman and Nicobar Islands",

    "Jammu & Kashmir":
        "Jammu and Kashmir",

    "NCT of Delhi":
        "Delhi",

    "Delhi UT":
        "Delhi",

    "Uttarakhand *":
        "Uttarakhand",

    "Uttaranchal":
        "Uttarakhand"
}


economic["state_name"] = (
    economic["state_name"]
    .replace(state_name_fixes)
)


# ============================================================
# 17. MERGE CENSUS + ECONOMIC DATA
# ============================================================

market_data = city_data.merge(
    economic,
    on="state_name",
    how="left"
)


# ============================================================
# 18. MERGE QUALITY
# ============================================================

matched = (
    market_data["pcnsdp_2025_26"]
    .notna()
    .sum()
)

total = len(market_data)

match_rate = (
    matched / total * 100
)


print("\nEconomic data matching:")

print(
    f"Cities matched: {matched:,}"
)

print(
    f"Total cities:   {total:,}"
)

print(
    f"Match rate:     {match_rate:.2f}%"
)


# ============================================================
# 19. DATA COMPLETENESS
# ============================================================

market_data["data_complete"] = (
    market_data[
        [
            "population",
            "literacy_rate",
            "pcnsdp_2025_26"
        ]
    ]
    .notna()
    .all(axis=1)
)


complete_data = market_data[
    market_data["data_complete"]
].copy()


print("\nModeling dataset:")

print(
    f"Cities with complete data: "
    f"{len(complete_data):,}"
)


# ============================================================
# 20. MARKET SIZE SCORE
# ============================================================

# Log transformation prevents very large cities
# from completely dominating the score.

complete_data["population_log"] = (
    np.log1p(
        complete_data["population"]
    )
)


pop_min = (
    complete_data["population_log"]
    .min()
)

pop_max = (
    complete_data["population_log"]
    .max()
)


complete_data["market_size_score"] = (
    (
        complete_data["population_log"]
        - pop_min
    )
    /
    (
        pop_max
        - pop_min
    )
    * 100
)


# ============================================================
# 21. HUMAN CAPITAL SCORE
# ============================================================

complete_data["human_capital_score"] = (
    complete_data["literacy_rate"]
)


# ============================================================
# 22. ECONOMIC CAPACITY SCORE
# ============================================================

income_min = (
    complete_data["pcnsdp_2025_26"]
    .min()
)

income_max = (
    complete_data["pcnsdp_2025_26"]
    .max()
)


complete_data["economic_capacity_score"] = (
    (
        complete_data["pcnsdp_2025_26"]
        - income_min
    )
    /
    (
        income_max
        - income_min
    )
    * 100
)


# ============================================================
# 23. MARKET OPPORTUNITY SCORE
#
# 50% Market Size
# 20% Human Capital
# 30% Economic Capacity
# ============================================================

complete_data["market_opportunity_score"] = (

    0.50
    * complete_data["market_size_score"]

    +

    0.20
    * complete_data["human_capital_score"]

    +

    0.30
    * complete_data["economic_capacity_score"]
)


# ============================================================
# 24. MARKET RANK
# ============================================================

complete_data["market_rank"] = (
    complete_data[
        "market_opportunity_score"
    ]
    .rank(
        method="min",
        ascending=False
    )
    .astype(int)
)


# ============================================================
# 25. SORT FINAL MODEL
# ============================================================

complete_data = (
    complete_data
    .sort_values(
        "market_opportunity_score",
        ascending=False
    )
    .reset_index(drop=True)
)


# ============================================================
# 26. MARKET TIER
# ============================================================

def assign_tier(rank):

    if rank <= 10:
        return "Tier 1 - Highest Opportunity"

    elif rank <= 50:
        return "Tier 2 - Strong Opportunity"

    elif rank <= 100:
        return "Tier 3 - Emerging Opportunity"

    else:
        return "Tier 4 - Lower Relative Opportunity"


complete_data["market_tier"] = (
    complete_data["market_rank"]
    .apply(assign_tier)
)


# ============================================================
# 27. SAVE FINAL MODEL DATASET
# ============================================================

complete_data.to_csv(
    MODEL_OUTPUT,
    index=False
)


# ============================================================
# 28. TOP 20 MARKET OPPORTUNITIES
# ============================================================

print("\n" + "=" * 75)
print(
    "MARKETLENS — TOP 20 MARKET OPPORTUNITIES"
)
print("=" * 75)


print(
    complete_data[
        [
            "market_rank",
            "state_name",
            "Name",
            "population",
            "literacy_rate",
            "pcnsdp_2025_26",
            "market_size_score",
            "human_capital_score",
            "economic_capacity_score",
            "market_opportunity_score",
            "market_tier"
        ]
    ]
    .head(20)
    .to_string(index=False)
)


# ============================================================
# 29. MODEL SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("MODEL SUMMARY")
print("=" * 75)

print(
    f"Total urban markets:       "
    f"{len(market_data):,}"
)

print(
    f"Complete-data markets:     "
    f"{len(complete_data):,}"
)

print(
    f"Excluded incomplete data:  "
    f"{len(market_data) - len(complete_data):,}"
)

print(
    f"Geographies merged:        "
    f"{market_data['geography_merged'].sum():,}"
)

print(
    "\nWeights:"
)

print("Market Size:        50%")
print("Human Capital:      20%")
print("Economic Capacity:  30%")

print(
    "\nModel dataset saved to:"
)

print(MODEL_OUTPUT)


# ============================================================
# 30. SENSITIVITY ANALYSIS
# ============================================================

scenarios = {

    "Current Model": {
        "market_size": 0.50,
        "human_capital": 0.20,
        "economic_capacity": 0.30
    },

    "Balanced": {
        "market_size": 0.40,
        "human_capital": 0.30,
        "economic_capacity": 0.30
    },

    "Market Size": {
        "market_size": 0.60,
        "human_capital": 0.20,
        "economic_capacity": 0.20
    },

    "Economic Focus": {
        "market_size": 0.30,
        "human_capital": 0.20,
        "economic_capacity": 0.50
    },

    "Human Capital": {
        "market_size": 0.30,
        "human_capital": 0.50,
        "economic_capacity": 0.20
    }
}


sensitivity_results = complete_data[
    [
        "state_name",
        "Name",
        "population",
        "literacy_rate",
        "pcnsdp_2025_26",
        "market_size_score",
        "human_capital_score",
        "economic_capacity_score"
    ]
].copy()


# ============================================================
# 31. CALCULATE SCENARIO SCORES
# ============================================================

for scenario_name, weights in scenarios.items():

    prefix = (
        scenario_name
        .lower()
        .replace(" ", "_")
    )

    score_column = (
        prefix + "_score"
    )

    sensitivity_results[score_column] = (

        weights["market_size"]
        * sensitivity_results[
            "market_size_score"
        ]

        +

        weights["human_capital"]
        * sensitivity_results[
            "human_capital_score"
        ]

        +

        weights["economic_capacity"]
        * sensitivity_results[
            "economic_capacity_score"
        ]
    )


# ============================================================
# 32. CALCULATE SCENARIO RANKS
# ============================================================

for scenario_name in scenarios:

    prefix = (
        scenario_name
        .lower()
        .replace(" ", "_")
    )

    score_column = (
        prefix + "_score"
    )

    rank_column = (
        prefix + "_rank"
    )

    sensitivity_results[rank_column] = (
        sensitivity_results[score_column]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )


# ============================================================
# 33. TOP 10 BY SCENARIO
# ============================================================

print("\n" + "=" * 75)
print("SENSITIVITY ANALYSIS — TOP 10")
print("=" * 75)


for scenario_name in scenarios:

    prefix = (
        scenario_name
        .lower()
        .replace(" ", "_")
    )

    score_column = (
        prefix + "_score"
    )

    print("\n" + "-" * 75)
    print(scenario_name)
    print("-" * 75)

    top10 = (
        sensitivity_results
        .sort_values(
            score_column,
            ascending=False
        )
        .head(10)
    )

    print(
        top10[
            [
                "state_name",
                "Name",
                score_column
            ]
        ]
        .to_string(index=False)
    )


# ============================================================
# 34. RANK STABILITY
# ============================================================

rank_columns = [

    scenario_name
    .lower()
    .replace(" ", "_")
    + "_rank"

    for scenario_name in scenarios
]


sensitivity_results["average_rank"] = (
    sensitivity_results[
        rank_columns
    ].mean(axis=1)
)


sensitivity_results["rank_std"] = (
    sensitivity_results[
        rank_columns
    ].std(axis=1)
)


stable_cities = (
    sensitivity_results
    .sort_values(
        [
            "average_rank",
            "rank_std"
        ]
    )
    .head(20)
)


print("\n" + "=" * 75)
print("MOST ROBUST MARKETS")
print("=" * 75)


print(
    stable_cities[
        [
            "state_name",
            "Name",
            "average_rank",
            "rank_std"
        ]
    ]
    .to_string(index=False)
)


# ============================================================
# 35. SAVE SENSITIVITY RESULTS
# ============================================================

sensitivity_results.to_csv(
    SENSITIVITY_OUTPUT,
    index=False
)


print(
    "\nSensitivity analysis saved to:"
)

print(SENSITIVITY_OUTPUT)


# ============================================================
# 36. FINAL OUTPUT SUMMARY
# ============================================================

print("\n" + "=" * 75)
print("MARKETLENS PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 75)

print("\nGenerated files:")

print(
    f"1. {CITY_OUTPUT}"
)

print(
    f"2. {MODEL_OUTPUT}"
)

print(
    f"3. {SENSITIVITY_OUTPUT}"
)

print("\nCore analysis is complete.")