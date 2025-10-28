#!/usr/bin/env python3
"""Check Tailored Pheromones modifiers for Manticore"""
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

cur = conn.cursor()

# Get Manticore's ID
cur.execute("SELECT id FROM characters WHERE street_name = 'Manticore'")
char_id = cur.fetchone()[0]

print(f"Manticore ID: {char_id}\n")

# Get all modifiers for Tailored Pheromones
cur.execute("""
    SELECT source, modifier_type, target_name, modifier_value, condition
    FROM character_modifiers 
    WHERE character_id = %s AND source LIKE %s
    ORDER BY id
""", (char_id, '%Pheromone%'))

rows = cur.fetchall()

print("Tailored Pheromones modifiers in database:")
if rows:
    for row in rows:
        print(f"  Source: {row[0]}")
        print(f"  Type: {row[1]}")
        print(f"  Target: {row[2]}")
        print(f"  Value: {row[3]}")
        print(f"  Condition: {row[4]}")
        print()
else:
    print("  ❌ NO MODIFIERS FOUND!")

print("\nExpected modifiers:")
print("  1. +4 social dice")
print("  2. 1/2 effect on non-dwarves (condition)")

conn.close()
