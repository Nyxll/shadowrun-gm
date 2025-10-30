#!/usr/bin/env python3
"""
Check Platinum's body index values in database
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Get Platinum's body index values
cur.execute("""
    SELECT 
        name,
        street_name,
        base_essence,
        current_essence,
        body_index_current,
        body_index_max
    FROM characters 
    WHERE street_name = 'Platinum' OR name = 'Kent Jefferies'
""")

result = cur.fetchone()

if result:
    print("=" * 80)
    print("PLATINUM'S ESSENCE AND BODY INDEX IN DATABASE")
    print("=" * 80)
    print(f"\nName: {result[0]}")
    print(f"Street Name: {result[1]}")
    print(f"Base Essence: {result[2]}")
    print(f"Current Essence: {result[3]}")
    print(f"Body Index Current: {result[4]}")
    print(f"Body Index Max: {result[5]}")
    print("\n" + "=" * 80)
else:
    print("Platinum not found!")

cur.close()
conn.close()
