# pip install psycopg2-binary sqlalchemy pandas

import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine
import time
from sqlalchemy import text

#----LOAD DATA----

canada = pd.read_csv('canada.csv')
usa = pd.read_csv('usa.csv')

canada.head()
usa.head()

#-----MERGE DATASET FIRST U BTCH-----
dataset = pd.concat([canada, usa], ignore_index=True)

#---Send it Render first mwehihi----

from sqlalchemy import create_engine

# Render
db_url = "postgresql://cloudcomputing_ngy9_user:n64n2DQKL9UpSi2NohaQJNoCjwstZqur@dpg-d070d99r0fns7382jqsg-a.singapore-postgres.render.com/cloudcomputing_ngy9"

# Create the database engine
engine = create_engine(db_url)

dataset.to_sql('NeedStaged', engine, schema='public', if_exists='replace', index=False)

#---- Retrieve your memories ----

DATABASE_URL = "postgresql://cloudcomputing_ngy9_user:n64n2DQKL9UpSi2NohaQJNoCjwstZqur@dpg-d070d99r0fns7382jqsg-a.singapore-postgres.render.com/cloudcomputing_ngy9"

engine = create_engine(DATABASE_URL, client_encoding='utf8')
connection = engine.connect()

start = time.perf_counter()
query = text('SELECT * FROM "NeedStaged";')
result = connection.execute(query)
data_toClean = pd.DataFrame(result.fetchall(), columns=result.keys())
end = time.perf_counter()

print(f"Query took {end - start:.6f} seconds")
print(f"Rows retrieved: {len(data_toClean)}")

print(data_toClean.isnull().sum())

#---- Drop rows with no ambag-----
data = data_toClean.dropna()

print("Cleaned dataset shape:", data.shape)

#---Checking Cleaned---

print(data.isnull().sum())

data.info()

# Clean 'Quantity Ordered' column: keep only numeric rows
data = data[data['Quantity Ordered'].str.isnumeric()]

# Clean 'Price Each' column: allow only one decimal point for valid float conversion
data = data[data['Price Each'].str.replace('.', '', 1).str.isnumeric()]

# Convert types
data['Quantity Ordered'] = data['Quantity Ordered'].astype(int)
data['Price Each'] = data['Price Each'].astype(float)

# Filter valid date format rows
data = data[data['Order Date'].str.match(r'\d{2}/\d{2}/\d{2} \d{2}:\d{2}', na=False)]

# Convert to datetime
data['Order Date'] = pd.to_datetime(data['Order Date'], format='%m/%d/%y %H:%M')

# Ensure 'Order Date' is already in datetime (this line is safe even if already done)
data['Order Date'] = pd.to_datetime(data['Order Date'], format='%m/%d/%y %H:%M')

# Create separate 'Date' and 'Time' columns
data['Date'] = data['Order Date'].dt.date
data['Time'] = data['Order Date'].dt.time

# --- Conversion rate ng yaman ----
CAD_TO_USD = 0.74

# Create 'Price in Dollar' column: only convert Canadian rows, leave USA rows unchanged
data['Price in Dollar'] = data.apply(
    lambda row: row['Price Each'] * CAD_TO_USD if row['source'].lower() == 'canada' else row['Price Each'],
    axis=1
)

# Keep only rows where 'Order ID' is fully numeric
data = data[data['Order ID'].str.isnumeric()]

# Convert to integer type
data['Order ID'] = data['Order ID'].astype(int)

#----Delete kambals---

data = data.drop_duplicates()

# Render 2
db_url = "postgresql://whiplash_user:6EoohkmGo5ziA3qJMhsBYHl5P6yS9UKL@dpg-d0amg66uk2gs73busq9g-a.oregon-postgres.render.com/whiplash"

# Create the database engine
engine = create_engine(db_url)

data.to_sql('data_ETL', engine, schema='public', if_exists='replace', index=False)

#---- Retrieve your memories ----

DUCK_DB = "postgresql://whiplash_user:6EoohkmGo5ziA3qJMhsBYHl5P6yS9UKL@dpg-d0amg66uk2gs73busq9g-a.oregon-postgres.render.com/whiplash"

engine = create_engine(DUCK_DB, client_encoding='utf8')
connection = engine.connect()

start = time.perf_counter()
query = text('SELECT * FROM "data_ETL";')
end = time.perf_counter()

print(f"Query took {end - start:.6f} seconds")
print(f"Rows retrieved: {len(data_toClean)}")

cursor.execute('SELECT * FROM pg_extension;')
rows = cursor.fetchall()

for row in rows:
    print(row)
    
    conn = psycopg2.connect(
    dbname="whiplash",
    user="whiplash_user",
    password="6EoohkmGo5ziA3qJMhsBYHl5P6yS9UKL",
    host="dpg-d0amg66uk2gs73busq9g-a.oregon-postgres.render.com",
    port="5432"
)
cursor = conn.cursor()
cursor.execute('SELECT * FROM "data_ETL";')
rows = cursor.fetchall()

for row in rows:
    print(row)
    
    
