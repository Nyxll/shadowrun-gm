#!/usr/bin/env python3
"""Verify Body Index storage in modifier_data"""
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
cursor = conn.cursor()

# Get Platinum
cursor.execute("SELECT id FROM characters WHERE name = 'Kent Jefferies'")
char = cursor.fetchone()

print("=" * 70)
print("BIOWARE BODY INDEX STORAGE VERIFICATION")
print("=" * 70)

# Check bioware storage
cursor.execute("""
    SELECT 
        source,
        essence_cost,
        body_index_cost,
        modifier_data
    FROM character_modifiers
    WHERE character_id = %s
      AND modifier_type = 'augmentation'
      AND source_type = 'bioware'
    ORDER BY source
""", (char['id'],))

bioware_items = cursor.fetchall()

print(f"\n{'Bioware Item':<40} {'Column':<10} {'JSONB':<10}")
print("-" * 70)

for item in bioware_items:
    col_value = item['body_index_cost'] if item['body_index_cost'] else 0
    jsonb_value = item['modifier_data'].get('body_index_cost', 0) if item['modifier_data'] else 0
    print(f"{item['source']:<40} {col_value:<10} {jsonb_value}")

print("\n" + "=" * 70)
print("CYBERWARE ESSENCE STORAGE VERIFICATION")
print("=" * 70)

# Check cyberware storage
cursor.execute("""
    SELECT 
        source,
        essence_cost,
        modifier_data
    FROM character_modifiers
    WHERE character_id = %s
      AND modifier_type = 'augmentation'
      AND source_type = 'cyberware'
    ORDER BY source
""", (char['id'],))

cyberware_items = cursor.fetchall()

print(f"\n{'Cyberware Item':<40} {'Essence':<10}")
print("-" * 70)

for item in cyberware_items:
    essence = item['essence_cost'] if item['essence_cost'] else 0
    print(f"{item['source']:<40} {essence}")

print("\n✓ Verification complete!")
print("\nSUMMARY:")
print("- Cyberware: essence_cost in dedicated column ✓")
print("- Bioware: body_index_cost column exists")
print("  - Column values:", "populated" if any(item['body_index_cost'] for item in bioware_items) else "EMPTY")
print("  - JSONB values:", "populated" if any(item['modifier_data'].get('body_index_cost') if item['modifier_data'] else None for item in bioware_items) else "empty")

# Offer to migrate
if not any(item['body_index_cost'] for item in bioware_items) and any(item['modifier_data'].get('body_index_cost') if item['modifier_data'] else None for item in bioware_items):
    print("\n⚠ Data needs migration from JSONB to column!")
    print("Run: python tools/apply-body-index-migration.py")

cursor.close()
conn.close()
