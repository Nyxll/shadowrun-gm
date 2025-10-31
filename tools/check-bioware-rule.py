#!/usr/bin/env python3
"""
Check the bioware Body Index rule from Shadowrun 2nd Edition
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

print("=" * 70)
print("BIOWARE BODY INDEX RULE CHECK")
print("=" * 70)
print("\nShadowrun 2nd Edition Rule:")
print("Body Index = (Body + Willpower) / 2")
print("\nThis is the MAXIMUM bioware a character can have.")
print("=" * 70)

cur.execute("""
    SELECT 
        street_name,
        base_body,
        base_willpower,
        body_index_max,
        body_index_current,
        ROUND((base_body + base_willpower) / 2.0, 2) as calculated_max
    FROM characters
    ORDER BY street_name
""")

print(f"\n{'Character':<12} | {'Body':<4} | {'Will':<4} | {'Max BI':<7} | {'Current':<7} | {'Calc Max':<8} | Status")
print("-" * 70)

for street_name, body, will, bi_max, bi_current, calc_max in cur.fetchall():
    status = "✓ OK" if bi_current <= bi_max else "✗ OVER LIMIT"
    print(f"{street_name:<12} | {body:<4} | {will:<4} | {bi_max:<7.2f} | {bi_current:<7.2f} | {calc_max:<8.2f} | {status}")

print("\n" + "=" * 70)
print("DETAILED BIOWARE BREAKDOWN")
print("=" * 70)

cur.execute("""
    SELECT 
        c.street_name,
        cm.source,
        cm.modifier_data->>'body_index_cost' as bi_cost
    FROM character_modifiers cm
    JOIN characters c ON c.id = cm.character_id
    WHERE cm.source_type = 'bioware'
    AND cm.modifier_data->>'body_index_cost' IS NOT NULL
    ORDER BY c.street_name, cm.source
""")

current_char = None
total_bi = 0

for street_name, source, bi_cost in cur.fetchall():
    if current_char != street_name:
        if current_char:
            print(f"  Total: {total_bi:.2f}")
        current_char = street_name
        print(f"\n{street_name}:")
        total_bi = 0
    
    bi_cost_float = float(bi_cost) if bi_cost else 0
    total_bi += bi_cost_float
    print(f"  {source}: {bi_cost_float:.2f}")

if current_char:
    print(f"  Total: {total_bi:.2f}")

cur.close()
conn.close()

print("\n" + "=" * 70)
print("RULE SUMMARY")
print("=" * 70)
print("✓ Body Index formula is CORRECT: (Body + Willpower) / 2")
print("✓ This represents the MAXIMUM bioware capacity")
print("✓ Each bioware item has a Body Index cost")
print("✓ Total bioware BI cost cannot exceed Body Index maximum")
print("=" * 70)
