import streamlit as st
import pandas as pd
import psycopg2

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MarketLens",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# DATABASE CONNECTION
# =========================================================

@st.cache_data
def load_data():

    conn = psycopg2.connect(
    st.secrets["database"]["url"]
)

    query = """
        SELECT
            state,
            state_name,
            urban_market,
            population,
            literate_population,
            census_records,
            source_names,
            name,
            geography_merged,
            literacy_rate,
            pcnsdp_2025_26,
            data_complete,
            population_log,
            market_size_score,
            human_capital_score,
            economic_capacity_score,
            market_opportunity_score,
            market_rank,
            market_tier
        FROM marketlens
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df

# =========================================================
# LOAD DATA
# =========================================================

try:
    df = load_data()

except Exception as e:

    st.error("Could not connect to PostgreSQL.")

    st.code(str(e))

    st.stop()


# =========================================================
# TITLE
# =========================================================

st.title("📊 MarketLens")
st.subheader("Indian Market Expansion Intelligence")

st.write(
    "A data-driven framework for identifying Indian markets "
    "with the strongest potential for business expansion."
)

st.divider()


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Filters")

# State filter

states = sorted(df["state_name"].dropna().unique())

selected_states = st.sidebar.multiselect(
    "Select State",
    states,
    default=[]
)

# Tier filter

tiers = [
    "Tier 1 - Highest Opportunity",
    "Tier 2 - Strong Opportunity",
    "Tier 3 - Emerging Opportunity",
    "Tier 4 - Lower Relative Opportunity"
]

selected_tiers = st.sidebar.multiselect(
    "Market Tier",
    tiers,
    default=[]
)

# Population filter

min_population = int(df["population"].min())
max_population = int(df["population"].max())

population_range = st.sidebar.slider(
    "Population Range",
    min_population,
    max_population,
    (min_population, max_population)
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df.copy()

if selected_states:
    filtered_df = filtered_df[
        filtered_df["state_name"].isin(selected_states)
    ]

if selected_tiers:
    filtered_df = filtered_df[
        filtered_df["market_tier"].isin(selected_tiers)
    ]

filtered_df = filtered_df[
    (filtered_df["population"] >= population_range[0]) &
    (filtered_df["population"] <= population_range[1])
]


# =========================================================
# KPI SECTION
# =========================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Markets Analyzed",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "Markets After Filters",
        f"{len(filtered_df):,}"
    )

with col3:
    st.metric(
        "States / UTs",
        f"{df['state_name'].nunique():,}"
    )

with col4:

    if len(filtered_df) > 0:

        top_market = filtered_df.sort_values(
            "market_opportunity_score",
            ascending=False
        ).iloc[0]

        st.metric(
            "Top Market",
            top_market["urban_market"]
        )

    else:

        st.metric(
            "Top Market",
            "No data"
        )


st.divider()


# =========================================================
# TOP MARKETS
# =========================================================

st.header("🏆 Top Expansion Markets")

top_markets = (
    filtered_df
    .sort_values("market_opportunity_score", ascending=False)
    .head(20)
    .copy()
)

top_markets["Opportunity Score"] = (
    top_markets["market_opportunity_score"].round(2)
)

top_markets["Population"] = (
    top_markets["population"].map(lambda x: f"{int(x):,}")
)

top_markets["Literacy Rate"] = (
    top_markets["literacy_rate"].round(2)
)

top_markets["PCNSDP"] = (
    top_markets["pcnsdp_2025_26"].round(2)
)

display_columns = [
    "market_rank",
    "urban_market",
    "state_name",
    "Population",
    "Literacy Rate",
    "PCNSDP",
    "Opportunity Score",
    "market_tier"
]

st.dataframe(
    top_markets[display_columns],
    use_container_width=True,
    hide_index=True
)


# =========================================================
# CHARTS
# =========================================================

st.divider()

chart_col1, chart_col2 = st.columns(2)


# ---------------------------------------------------------
# CHART 1 — TOP 10 OPPORTUNITY
# ---------------------------------------------------------

with chart_col1:

    st.subheader("Top 10 Markets by Opportunity")

    chart_data = (
        filtered_df
        .sort_values(
            "market_opportunity_score",
            ascending=False
        )
        .head(10)
        .set_index("urban_market")
    )

    st.bar_chart(
        chart_data["market_opportunity_score"]
    )


# ---------------------------------------------------------
# CHART 2 — POPULATION VS OPPORTUNITY
# ---------------------------------------------------------

with chart_col2:

    st.subheader("Market Size vs Opportunity")

    scatter_data = filtered_df[
        [
            "population",
            "market_opportunity_score"
        ]
    ].copy()

    scatter_data["population"] = (
        scatter_data["population"] / 1_000_000
    )

    scatter_data = scatter_data.rename(
        columns={
            "population": "Population (Millions)",
            "market_opportunity_score": "Opportunity Score"
        }
    )

    st.scatter_chart(
        scatter_data,
        x="Population (Millions)",
        y="Opportunity Score"
    )


# =========================================================
# STATE ANALYSIS
# =========================================================

st.divider()

st.header("🇮🇳 State-Level Market Opportunity")

state_summary = (
    filtered_df
    .groupby("state_name")
    .agg(
        markets=("urban_market", "count"),
        average_opportunity=(
            "market_opportunity_score",
            "mean"
        ),
        total_population=(
            "population",
            "sum"
        )
    )
    .reset_index()
    .sort_values(
        "average_opportunity",
        ascending=False
    )
)

state_summary["average_opportunity"] = (
    state_summary["average_opportunity"].round(2)
)

state_summary["total_population"] = (
    state_summary["total_population"]
    .map(lambda x: f"{int(x):,}")
)

st.dataframe(
    state_summary,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# MARKET TIER DISTRIBUTION
# =========================================================

st.divider()

st.header("📈 Market Tier Distribution")

tier_distribution = (
    filtered_df["market_tier"]
    .value_counts()
)

st.bar_chart(tier_distribution)


# =========================================================
# RECOMMENDATION
# =========================================================

st.divider()

st.header("💡 Expansion Recommendation")

if len(filtered_df) > 0:

    recommendation = filtered_df.sort_values(
        "market_opportunity_score",
        ascending=False
    ).iloc[0]

    score = float(recommendation["market_opportunity_score"])
    population = int(recommendation["population"])
    literacy = float(recommendation["literacy_rate"])

    st.success(
        f"""
**{recommendation['urban_market']}, {recommendation['state_name']}**

Opportunity Score: **{score:.2f}**

Population: **{population:,}**

Literacy Rate: **{literacy:.2f}%**

Market Tier: **{recommendation['market_tier']}**
"""
    )

else:

    st.warning(
        "No markets match the selected filters."
    )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "MarketLens | Indian Market Expansion Intelligence"
)