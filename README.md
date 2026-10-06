# MarketLens — Indian Market Expansion Intelligence

## Overview

MarketLens is a data analytics and business intelligence project designed to identify promising Indian urban markets for business expansion.

The project combines Indian Census population and literacy data with state-level economic data to create a composite **Market Opportunity Score** for Indian urban markets.

### Business Question

> **Which Indian cities are the strongest candidates for business expansion, and why?**

---

## Key Objectives

- Identify high-potential Indian urban markets
- Compare markets using population, literacy, and economic capacity
- Rank markets using a composite opportunity score
- Identify the strongest market in each state
- Analyze large markets versus their opportunity scores
- Test ranking stability through sensitivity analysis
- Build an interactive dashboard for business decision-making

---

## Data Sources

### Population & Literacy

**Government of India Census 2011 — Population Finder / Basic Population Figures**

The Census dataset provides population and literacy information for Indian towns and urban areas.

Key variables used:

- Population
- Literate Population
- State
- District
- Urban/Town classification

### Economic Data

**Ministry of Statistics and Programme Implementation (MoSPI)**

The project uses **Per Capita Net State Domestic Product (PCNSDP) at current prices for 2025–26**.

---

## Data Pipeline

```text
Census 2011 Data
       ↓
Python Data Cleaning
       ↓
Urban Market Aggregation
       ↓
Geographic Name Normalization
       ↓
MoSPI Economic Data
       ↓
Data Integration
       ↓
Market Opportunity Scoring
       ↓
Sensitivity Analysis
       ↓
PostgreSQL
       ↓
SQL Analysis
       ↓
Streamlit Dashboard
```

---

## Dataset Summary

| Metric | Value |
|---|---:|
| Urban markets | 8,067 |
| Markets formed from multiple Census records | 198 |
| Markets with economic matches | 5,199 |
| Economic match rate | 64.45% |
| Complete-data markets ranked | 5,199 |
| Markets excluded due to incomplete data | 2,868 |

---

# Market Opportunity Score

MarketLens evaluates markets using three major factors.

### Market Size — 50%

Population is transformed using a logarithmic scale:

```python
population_log = np.log1p(population)
```

This reduces the disproportionate influence of extremely large cities.

### Human Capital — 20%

Human capital is represented by the Census literacy rate.

### Economic Capacity — 30%

Economic capacity is represented by state-level PCNSDP.

### Final Formula

```text
Market Opportunity Score
=
50% Market Size
+
20% Human Capital
+
30% Economic Capacity
```

Markets with incomplete data are excluded from the final ranking.

---

## Opportunity Tiers

| Rank | Tier |
|---:|---|
| 1–10 | Tier 1 — Highest Opportunity |
| 11–50 | Tier 2 — Strong Opportunity |
| 51–100 | Tier 3 — Emerging Opportunity |
| 101+ | Tier 4 — Lower Relative Opportunity |

---

# Top 10 Expansion Markets

| Rank | Market | State | Population | Opportunity Score |
|---:|---|---|---:|---:|
| 1 | BBMP | Karnataka | 16,939,167 | 95.81 |
| 2 | Chennai | Tamil Nadu | 4,646,732 | 89.77 |
| 3 | Mysuru | Karnataka | 1,813,612 | 88.35 |
| 4 | Greater Mumbai | Maharashtra | 12,442,373 | 87.99 |
| 5 | Mangaluru | Karnataka | 988,455 | 87.51 |
| 6 | Belagavi | Karnataka | 978,202 | 86.43 |
| 7 | Hubli-Dharwad | Karnataka | 943,788 | 85.69 |
| 8 | Ahmedabad | Gujarat | 5,633,927 | 85.61 |
| 9 | Gulbarga | Karnataka | 1,076,734 | 85.06 |
| 10 | Coimbatore | Tamil Nadu | 1,050,721 | 85.00 |

---

## Key Insights

- Karnataka has several markets among the highest-ranked opportunities.
- Population alone does not determine the final ranking.
- Smaller markets can rank highly when they combine strong literacy and economic capacity.
- State-level economic performance has a significant influence on market scores.
- The sensitivity analysis identifies markets that remain strong under different weighting assumptions.

---

# Sensitivity Analysis

MarketLens tests five different weighting scenarios:

| Scenario | Market Size | Human Capital | Economic Capacity |
|---|---:|---:|---:|
| Current Model | 50% | 20% | 30% |
| Balanced | 40% | 30% | 30% |
| Market Size Focus | 60% | 20% | 20% |
| Economic Focus | 30% | 20% | 50% |
| Human Capital Focus | 30% | 50% | 20% |

This helps determine whether the ranking is robust or highly dependent on a particular weighting scheme.

The most consistently strong markets include **BBMP, Mysuru, Mangaluru, Chennai, and Belagavi**.

---

# PostgreSQL Analysis

The processed dataset is stored in PostgreSQL and analyzed using SQL.

Example analyses include:

- Top 10 expansion markets
- Best market in every state
- Opportunity tier distribution
- Largest markets versus opportunity score
- Strongest economic markets

Example query:

```sql
SELECT
    urban_market,
    state_name,
    population,
    literacy_rate,
    pcnsdp_2025_26,
    market_opportunity_score,
    market_rank
FROM marketlens
ORDER BY market_opportunity_score DESC
LIMIT 10;
```

---

# Interactive Dashboard

MarketLens includes a Streamlit dashboard connected to PostgreSQL.

The dashboard provides:

- Market rankings
- State filtering
- Opportunity tier filtering
- Population analysis
- Literacy analysis
- Economic capacity analysis
- Expansion recommendations

Run the dashboard locally:

```bash
streamlit run dashboard.py
```

---

# Tech Stack

- **Python**
- **Pandas**
- **NumPy**
- **PostgreSQL**
- **SQL**
- **Streamlit**
- **Git & GitHub**
- **pgAdmin**
- **Excel / XLSX data processing**

---

# Project Structure

```text
MarketLens/
│
├── data/
│   ├── State_wise_SDP-15042026_PCNSDP_Current.xlsx
│   ├── clean_cities.csv
│   └── processed/
│       ├── clean_cities.csv
│       ├── marketlens_city_data.csv
│       ├── marketlens_model_data.csv
│       └── marketlens_sensitivity_analysis.csv
│
├── dashboard.py
├── main.py
├── load_database.py
├── .gitignore
└── README.md
```

---

# Limitations

- Population and literacy data are based on Census 2011.
- Economic data is available at the state level rather than city level.
- Therefore, state-level PCNSDP is applied to urban markets within the corresponding state.
- 2,868 markets were excluded from the final ranking because of incomplete economic data.
- The scoring weights represent analytical assumptions rather than a universal definition of market opportunity.

---

# Future Improvements

Potential improvements include:

- More recent population estimates
- City-level GDP and income data
- Consumer spending data
- Business density
- Internet penetration
- Infrastructure indicators
- Competition intensity
- Logistics accessibility
- Real estate costs
- Historical market growth
- Predictive market-growth models

---

# Author

**Aditya Pratap Singh**

B.Tech Computer Science Engineering  
Data Science Focus

GitHub:  
https://github.com/aditya762

---

## Project Goal

MarketLens demonstrates how public data can be transformed into a structured business intelligence system for market expansion decisions.

**Data → Analysis → Database → Scoring Model → Decision Support**
```
