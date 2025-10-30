#!/usr/bin/env python3
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()

# Check for attribute-related columns
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'characters' 
    AND (column_name LIKE '%will%' OR column_name LIKE '%magic%' OR column_name LIKE '%attribute%')
    ORDER BY column_name
""")

print("Attribute-related columns:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Get Oak's data to see what's available
cursor.execute("""
    SELECT * FROM characters WHERE street_name = 'Oak' LIMIT 1
""")
columns = [desc[0] for desc in cursor.description]
print(f"\nAll columns in characters table ({len(columns)} total):")
for col in columns[:30]:  # First 30
    print(f"  {col}")

conn.close()
