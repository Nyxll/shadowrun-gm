#!/usr/bin/env python3
"""Check vehicles imported into database"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)

cur = conn.cursor()

# Get vehicle counts by character
cur.execute("""
    SELECT c.name, c.street_name, COUNT(v.id) as vehicle_count
    FROM characters c
    LEFT JOIN character_vehicles v ON c.id = v.character_id
    GROUP BY c.id, c.name, c.street_name
    ORDER BY c.name
""")

results = cur.fetchall()

print("VEHICLE COUNTS BY CHARACTER:")
print("=" * 60)
for r in results:
    display_name = r['street_name'] or r['name']
    print(f"{display_name}: {r['vehicle_count']} vehicles")

print("=" * 60)

# Get vehicle details
cur.execute("""
    SELECT c.street_name, c.name, v.vehicle_name, v.vehicle_type
    FROM characters c
    JOIN character_vehicles v ON c.id = v.character_id
    ORDER BY c.name, v.vehicle_name
""")

vehicles = cur.fetchall()

if vehicles:
    print("\nVEHICLE DETAILS:")
    print("=" * 60)
    for v in vehicles:
        display_name = v['street_name'] or v['name']
        print(f"{display_name}: {v['vehicle_name']} ({v['vehicle_type']})")
    print("=" * 60)
else:
    print("\nNo vehicles found in database")

conn.close()
