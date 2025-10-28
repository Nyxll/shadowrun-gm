#!/usr/bin/env python3
"""Migrate body_index_cost data from JSONB to column"""
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

cursor = conn.cursor()

print("Migrating body_index_cost from JSONB to column")
print("=" * 70)

try:
    # Migrate data from modifier_data JSONB to body_index_cost column
    cursor.execute("""
        UPDATE character_modifiers
        SET body_index_cost = (modifier_data->>'body_index_cost')::DECIMAL(4,2)
        WHERE modifier_type = 'augmentation'
          AND source_type = 'bioware'
          AND modifier_data IS NOT NULL
          AND modifier_data->>'body_index_cost' IS NOT NULL
    """)
    
    migrated = cursor.rowcount
    conn.commit()
    
    print(f"✓ Migrated {migrated} bioware items")
    
    # Verify
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM character_modifiers
        WHERE modifier_type = 'augmentation'
          AND source_type = 'bioware'
          AND body_index_cost IS NOT NULL
    """)
    
    count = cursor.fetchone()[0]
    print(f"✓ Migrated {count} bioware items to body_index_cost column")
    
    # Show sample
    cursor.execute("""
        SELECT source, body_index_cost
        FROM character_modifiers
        WHERE modifier_type = 'augmentation'
          AND source_type = 'bioware'
          AND body_index_cost IS NOT NULL
        ORDER BY source
        LIMIT 5
    """)
    
    print("\nSample bioware with body_index_cost:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} B.I.")

except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
    raise

finally:
    cursor.close()
    conn.close()

print("\n✓ Migration complete!")
