#!/usr/bin/env python3
"""
Verify body index values for all characters
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

print("=" * 80)
print("BODY INDEX VERIFICATION FOR ALL CHARACTERS")
print("=" * 80)

cur.execute("""
    SELECT 
        street_name,
        base_body,
        base_willpower,
        body_index_current,
        body_index_max
    FROM characters
    ORDER BY street_name
""")

for row in cur.fetchall():
    street_name, body, willpower, current, max_val = row
    calculated_max = (body + willpower) / 2.0
    
    print(f"\n{street_name}:")
    print(f"  Body: {body}, Willpower: {willpower}")
    print(f"  Body Index: {current}/{max_val}")
    print(f"  Calculated Max: {calculated_max}")
    
    if abs(max_val - calculated_max) > 0.01:
        print(f"  ⚠ WARNING: Max doesn't match calculated value!")
    else:
        print(f"  ✓ Correct")

print(f"\n{'='*80}")

cur.close()
conn.close()
