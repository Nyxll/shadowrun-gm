#!/usr/bin/env python3
"""
Update Platinum's body index directly via SQL
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Get current values
cur.execute("""
    SELECT 
        street_name,
        body_index_current,
        body_index_max
    FROM characters
    WHERE street_name = 'Platinum'
""")

result = cur.fetchone()

print("=" * 80)
print("PLATINUM BODY INDEX UPDATE")
print("=" * 80)
print(f"\nBEFORE: Body Index {result[1]}/{result[2]}")

# Update Platinum's body index
# From character file: Body Index 8.35/9
cur.execute("""
    UPDATE characters
    SET body_index_current = %s,
        body_index_max = %s
    WHERE street_name = 'Platinum'
""", (8.35, 9.0))

conn.commit()

# Verify update
cur.execute("""
    SELECT 
        street_name,
        body_index_current,
        body_index_max
    FROM characters
    WHERE street_name = 'Platinum'
""")

result = cur.fetchone()
print(f"AFTER:  Body Index {result[1]}/{result[2]}")
print("\n✓ Body Index updated successfully!")
print("=" * 80)

cur.close()
conn.close()
