#!/usr/bin/env python3
"""Check what the API returns for Manticore's cyberware/bioware"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row
import json

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

# Get Manticore's ID
cur.execute("SELECT id FROM characters WHERE street_name = 'Manticore'")
char = cur.fetchone()

if not char:
    print("Manticore not found")
    exit(1)

char_id = char['id']

# Get cyberware (mimicking the API query)
cur.execute("""
    SELECT 
        source as name,
        essence_cost,
        COALESCE(
            json_agg(
                DISTINCT jsonb_build_object(
                    'type', modifier_type,
                    'target', target_name,
                    'value', modifier_value
                )
            ) FILTER (WHERE modifier_type IS NOT NULL),
            '[]'::json
        ) as effects_raw
    FROM character_modifiers
    WHERE character_id = %s 
    AND source_type = 'cyberware'
    AND parent_modifier_id IS NULL
    GROUP BY source, essence_cost
    ORDER BY source
""", (char_id,))

cyberware = cur.fetchall()

print("CYBERWARE FROM API QUERY:")
print("=" * 70)
for item in cyberware:
    print(f"\n{item['name']} ({item['essence_cost']} ESS)")
    effects = item['effects_raw'] if item['effects_raw'] else []
    for effect in effects:
        print(f"  • {effect['type']}: {effect['target']} = {effect['value']}")

# Get bioware (mimicking the API query)
cur.execute("""
    SELECT 
        source as name,
        body_index_cost,
        COALESCE(
            json_agg(
                DISTINCT jsonb_build_object(
                    'type', modifier_type,
                    'target', target_name,
                    'value', modifier_value
                )
            ) FILTER (WHERE modifier_type IS NOT NULL),
            '[]'::json
        ) as effects_raw
    FROM character_modifiers
    WHERE character_id = %s 
    AND source_type = 'bioware'
    AND parent_modifier_id IS NULL
    GROUP BY source, body_index_cost
    ORDER BY source
""", (char_id,))

bioware = cur.fetchall()

print("\n\nBIOWARE FROM API QUERY:")
print("=" * 70)
for item in bioware:
    print(f"\n{item['name']} ({item['body_index_cost']} B.I.)")
    effects = item['effects_raw'] if item['effects_raw'] else []
    for effect in effects:
        print(f"  • {effect['type']}: {effect['target']} = {effect['value']}")

print("\n" + "=" * 70)

conn.close()
