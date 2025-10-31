#!/usr/bin/env python3
"""
Test specific fuzzy matches to debug similarity scores
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

test_cases = [
    'Stunbolt',
    'Levitate',
    'Physical Mask',
    'Treat',
    'Silence'
]

print("=" * 70)
print("TESTING FUZZY MATCHING WITH ALL SIMILARITY SCORES")
print("=" * 70)

for char_spell in test_cases:
    print(f"\nSearching for: '{char_spell}'")
    
    # Get top 5 matches with any similarity
    cur.execute("""
        SELECT spell_name, similarity(spell_name, %s) as sim
        FROM master_spells
        ORDER BY sim DESC
        LIMIT 5
    """, (char_spell,))
    
    results = cur.fetchall()
    for spell_name, sim in results:
        marker = "✓" if sim > 0.6 else "✗"
        print(f"  {marker} {spell_name}: {sim:.3f}")

cur.close()
conn.close()

print("\n" + "=" * 70)
print("OBSERVATION")
print("=" * 70)
print("If similarity scores are low (< 0.6), we may need to:")
print("1. Lower the threshold (e.g., 0.4 or 0.5)")
print("2. Add the missing spells to master_spells")
print("3. Use different matching strategy (word-based)")
print("=" * 70)
