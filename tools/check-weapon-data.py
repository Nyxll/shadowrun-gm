#!/usr/bin/env python3
"""Check weapon data in relationships field"""
import os
import json
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

cur = conn.cursor()
cur.execute("SELECT relationships FROM characters WHERE street_name = 'Platinum'")
rel = cur.fetchone()[0]

weapons = rel.get('weapons', [])
vehicles = rel.get('vehicles', [])
magical_items = rel.get('magical_items', [])

print(f"Weapons in relationships: {len(weapons)}")
if weapons:
    print("\nFirst weapon:")
    print(json.dumps(weapons[0], indent=2))

print(f"\n\nVehicles in relationships: {len(vehicles)}")
if vehicles:
    print("\nFirst vehicle:")
    print(json.dumps(vehicles[0], indent=2))

print(f"\n\nMagical items in relationships: {len(magical_items)}")
if magical_items:
    print("\nFirst magical item:")
    print(json.dumps(magical_items[0], indent=2))

conn.close()
