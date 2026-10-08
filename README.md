# MarketLens — Indian Market Expansion Intelligence

MarketLens is a data-driven market expansion intelligence platform designed to identify Indian cities with the strongest business expansion potential.

The project combines **Census demographics, literacy, state-level economic indicators, PostgreSQL analytics, and a weighted opportunity-scoring model** to rank urban markets across India.

> **Core Question:**  
> Which Indian cities are the best opportunities for business expansion, and why?

---

## 🚀 Live Demo

👉 **[Launch MarketLens Dashboard](https://marketlen.streamlit.app/)**

The interactive dashboard allows users to explore Indian markets, filter opportunities, compare cities, and identify the highest-scoring expansion markets.

---

## 📊 Project Overview

MarketLens transforms raw government datasets into an analytical decision-support system.

```text
Government Data
      ↓
Data Cleaning & Standardization
      ↓
City / Urban Market Aggregation
      ↓
Economic Data Integration
      ↓
Feature Engineering
      ↓
Market Opportunity Scoring
      ↓
Sensitivity Analysis
      ↓
PostgreSQL Analytics
      ↓
Interactive Streamlit Dashboard
```

---

## 🎯 Key Objectives

MarketLens was built to:

- Identify high-potential Indian urban markets
- Compare cities using population, literacy, and economic capacity
- Standardize fragmented Census geography
- Integrate demographic and economic datasets
- Rank markets using a transparent scoring methodology
- Test whether rankings remain stable under different scoring assumptions
- Store analytical results in PostgreSQL
- Provide an interactive dashboard for market exploration

---

## 🗂️ Data Sources

### 1. Census of India — 2011

**Dataset:**

`2011-IndiaStateDistSbDistTwn-0000.xlsx`

The Census dataset provides urban-level demographic information including:

- Population
- Literate population
- Literacy rate
- State
- District
- Urban geography

Literacy rate was calculated as:

```text
Literacy Rate =
Literate Population / Total Population × 100
```

---

### 2. Ministry of Statistics and Programme Implementation (MoSPI)

**Dataset:**

`State_wise_SDP-15042026_PCNSDP_Current.xlsx`

The dataset contains state-level:

**Per Capita Net State Domestic Product (PCNSDP)**

The project uses the latest available **2025–26 current-price PCNSDP** value available in the dataset.

---

## 🧹 Data Processing

The Census data required significant geographic standardization.

Examples of normalized city names include:

```text
Ahmadabad        → Ahmedabad
Mysore           → Mysuru
Mangalore        → Mangaluru
Belgaum          → Belagavi
Bangalore        → Bengaluru
Calicut          → Kozhikode
Cochin           → Kochi
Trivandrum       → Thiruvananthapuram
Baroda           → Vadodara
Poona             → Pune
```

Multiple Census records representing the same urban market were consolidated using:

```text
State + Urban Market
```

This produced a standardized urban-market dataset suitable for analysis.

---

## 📈 Dataset Summary

| Metric | Result |
|---|---:|
| Urban market records | 8,067 |
| Markets formed from multiple Census records | 198 |
| Markets matched with economic data | 5,199 |
| Economic-data match rate | 64.45% |
| Markets with complete model data | 5,199 |
| Markets excluded from ranking | 2,868 |

Markets without required economic data were excluded from the final ranking rather than assigning them an artificial zero score.

---

# 🧮 Market Opportunity Score

MarketLens calculates a composite **Market Opportunity Score** from three major dimensions.

### 1. Market Size — 50%

Population is transformed using a logarithmic scale:

```python
population_log = np.log1p(population)
```

This reduces the influence of extremely large cities while preserving their market-size advantage.

### 2. Human Capital — 20%

Measured using:

```text
Literacy Rate
```

Higher literacy is treated as an indicator of stronger human-capital potential.

### 3. Economic Capacity — 30%

Measured using:

```text
Per Capita Net State Domestic Product (PCNSDP)
```

Higher PCNSDP indicates greater state-level economic capacity.

### Final Formula

```text
Market Opportunity Score =

0.50 × Market Size Score
+ 0.20 × Human Capital Score
+ 0.30 × Economic Capacity Score
```

All normalized component scores are represented on a 0–100 scale.

---

# 🏆 Opportunity Tiers

Markets are categorized based on their overall ranking:

| Rank | Tier |
|---|---|
| 1–10 | Tier 1 — Highest Opportunity |
| 11–50 | Tier 2 — Strong Opportunity |
| 51–100 | Tier 3 — Emerging Opportunity |
| 101+ | Tier 4 — Lower Relative Opportunity |

---

# 🥇 Top Expansion Markets

Based on the current scoring model:

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

# 🔍 Key Insights

### 1. Market size is the strongest component

Population receives a **50% weighting**, making market scale the largest contributor to the final score.

However, population alone does not determine the ranking.

### 2. Karnataka performs strongly

Several Karnataka markets appear near the top because the state combines:

- Large urban populations
- High literacy levels
- Strong PCNSDP

This produces consistently strong composite scores.

### 3. Large cities do not automatically dominate

The scoring system combines market size with human capital and economic capacity.

This allows smaller but economically stronger and more literate markets to compete with significantly larger cities.

### 4. State-level economic indicators influence city rankings

PCNSDP is available at the state level rather than individual-city level.

Therefore, cities within the same state share the same economic-capacity input.

---

# 🔬 Sensitivity Analysis

To test the robustness of the ranking, MarketLens evaluates multiple weighting scenarios.

| Model | Market Size | Human Capital | Economic Capacity |
|---|---:|---:|---:|
| Current Model | 50% | 20% | 30% |
| Balanced | 40% | 30% | 30% |
| Market Size Focus | 60% | 20% | 20% |
| Economic Focus | 30% | 20% | 50% |
| Human Capital Focus | 30% | 50% | 20% |

The analysis measures how rankings change when the importance of each factor changes.

This helps identify markets whose performance is robust rather than dependent on a single arbitrary weighting scheme.

---

# 🗄️ PostgreSQL Analysis

MarketLens stores the final analytical dataset in **PostgreSQL**.

The database was used to perform analytical queries such as:

- Top expansion markets
- Best market in every state
- Opportunity-tier distribution
- Largest markets versus opportunity score
- Strongest economic markets

Example analytical workflow:

```sql
SELECT
    urban_market,
    state_name,
    population,
    market_opportunity_score,
    market_rank,
    market_tier
FROM marketlens
WHERE data_complete = TRUE
ORDER BY market_opportunity_score DESC
LIMIT 10;
```

---

# 📊 Interactive Dashboard

The project includes a **Streamlit dashboard** connected to PostgreSQL.

The dashboard allows users to:

- Explore ranked urban markets
- Filter by state
- Filter by opportunity tier
- Compare population
- Compare literacy rates
- View economic capacity
- Identify the highest-scoring market under selected filters
- Explore the Market Opportunity Score interactively

👉 **[Open the Live Dashboard](https://marketlen.streamlit.app/)**

---

# 🛠️ Tech Stack

### Programming & Analysis

- Python
- Pandas
- NumPy

### Database

- PostgreSQL
- SQL
- Psycopg2

### Visualization & Dashboard

- Streamlit

### Data Sources

- Government of India Census data
- Ministry of Statistics and Programme Implementation (MoSPI)

### Development Tools

- Git
- GitHub
- VS Code
- PostgreSQL / pgAdmin

---

# 📁 Project Structure

```text
MarketLens/
│
├── .streamlit/
│   └── secrets.toml
│
├── data/
│   ├── State_wise_SDP-15042026_PCNSDP_Current.xlsx
│   ├── clean_cities.csv
│   │
│   └── processed/
│       ├── clean_cities.csv
│       ├── marketlens_city_data.csv
│       ├── marketlens_model_data.csv
│       └── marketlens_sensitivity_analysis.csv
│
├── dashboard.py
├── load_database.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

# ⚙️ Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/aditya762/MarketLens.git
cd MarketLens
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure database credentials

Create:

```text
.streamlit/secrets.toml
```

and configure the PostgreSQL connection securely.

### 6. Run the dashboard

```bash
streamlit run dashboard.py
```

---

# ⚠️ Limitations

MarketLens is a decision-support model rather than a definitive prediction system.

### Census Data

The primary demographic dataset is based on the **2011 Census**, so population and literacy figures may not reflect current city conditions.

### Economic Data Granularity

PCNSDP is available at the **state level**, not city level.

Therefore, cities within the same state receive the same economic-capacity value.

### Market Definition

Urban geography can be fragmented across municipal corporations, extensions, and surrounding Census records.

The project applies geographic normalization and aggregation, but some real-world metropolitan boundaries may differ.

### Missing Economic Data

Markets without matching economic data are excluded from the final composite ranking.

---

# 🔮 Future Improvements

Potential future versions could include:

- Updated population estimates
- City-level GDP or income data
- Consumer spending indicators
- Internet penetration
- Workforce participation
- Business density
- Startup ecosystem indicators
- Real-estate costs
- Competitor density
- Infrastructure quality
- Logistics accessibility
- Distance to major transport hubs
- Machine-learning-based market potential prediction
- Automated data updates
- More advanced interactive visualizations

---

# 👨‍💻 Author

**Aditya Pratap Singh**

B.Tech Computer Science Engineering  
Minor in Data Science

GitHub:  
https://github.com/aditya762

---

# 🎯 Project Goal

MarketLens was built to demonstrate how **data engineering, statistical analysis, SQL, Python, and business intelligence** can be combined to solve a practical business problem.

The objective is not simply to identify the biggest cities.

It is to identify cities where **market scale, human capital, and economic capacity collectively create strong expansion potential.**

---

## ⭐ MarketLens

**Turning Indian market data into expansion intelligence.**
