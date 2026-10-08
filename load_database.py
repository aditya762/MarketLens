import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

CSV_FILE = "data/processed/marketlens_model_data.csv"

NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_Mbg3BDQRrJ1q@ep-royal-fire-b4tvv3u0-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

print("\nReading CSV...")
df = pd.read_csv(CSV_FILE)

print(f"Rows found: {len(df)}")
print(f"Columns found: {len(df.columns)}")

print("\nConnecting to PostgreSQL...")
conn = psycopg2.connect(NEON_CONNECTION_STRING)
cursor = conn.cursor()

print("Connected successfully.")

print("\nCreating table...")

cursor.execute("""
DROP TABLE IF EXISTS marketlens;

CREATE TABLE marketlens (
    state INTEGER,
    state_name TEXT,
    urban_market TEXT,
    population BIGINT,
    literate_population BIGINT,
    census_records INTEGER,
    source_names TEXT,
    name TEXT,
    geography_merged BOOLEAN,
    literacy_rate NUMERIC,
    pcnsdp_2025_26 NUMERIC,
    data_complete BOOLEAN,
    population_log NUMERIC,
    market_size_score NUMERIC,
    human_capital_score NUMERIC,
    economic_capacity_score NUMERIC,
    market_opportunity_score NUMERIC,
    market_rank INTEGER,
    market_tier TEXT
);
""")

columns = [
    "State",
    "state_name",
    "urban_market",
    "population",
    "literate_population",
    "census_records",
    "source_names",
    "Name",
    "geography_merged",
    "literacy_rate",
    "pcnsdp_2025_26",
    "data_complete",
    "population_log",
    "market_size_score",
    "human_capital_score",
    "economic_capacity_score",
    "market_opportunity_score",
    "market_rank",
    "market_tier"
]

df = df[columns]

df = df.where(pd.notna(df), None)

data = [
    tuple(row)
    for row in df.itertuples(index=False, name=None)
]

print("\nImporting data...")

insert_query = """
INSERT INTO marketlens (
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
)
VALUES %s
"""

execute_values(
    cursor,
    insert_query,
    data,
    page_size=1000
)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM marketlens;")
count = cursor.fetchone()[0]

print("\n================================")
print("MARKETLENS DATABASE IMPORT DONE")
print("================================")
print(f"Rows imported: {count}")

cursor.close()
conn.close()

print("\nPostgreSQL connection closed.")