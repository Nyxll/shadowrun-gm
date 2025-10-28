#!/usr/bin/env python3
"""
Enhance character_modifiers table with new columns for cyberware tracking
"""
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cursor = conn.cursor()

print("=" * 70)
print("ENHANCING CHARACTER_MODIFIERS TABLE")
print("=" * 70)

# Add new columns
migrations = [
    ("source_type", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS source_type TEXT"),
    ("source_id", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS source_id UUID"),
    ("modifier_data", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS modifier_data JSONB DEFAULT '{}'::jsonb"),
    ("is_homebrew", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS is_homebrew BOOLEAN DEFAULT FALSE"),
    ("is_experimental", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS is_experimental BOOLEAN DEFAULT FALSE"),
    ("is_unique", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS is_unique BOOLEAN DEFAULT FALSE"),
    ("house_rule_id", "ALTER TABLE character_modifiers ADD COLUMN IF NOT EXISTS house_rule_id INTEGER"),
]

for col_name, sql in migrations:
    try:
        cursor.execute(sql)
        print(f"✓ Added column: {col_name}")
    except Exception as e:
        print(f"✗ Error adding {col_name}: {e}")

# Create indexes
indexes = [
    ("idx_modifiers_source", "CREATE INDEX IF NOT EXISTS idx_modifiers_source ON character_modifiers(source_type)"),
    ("idx_modifiers_data", "CREATE INDEX IF NOT EXISTS idx_modifiers_data ON character_modifiers USING gin(modifier_data)"),
]

for idx_name, sql in indexes:
    try:
        cursor.execute(sql)
        print(f"✓ Created index: {idx_name}")
    except Exception as e:
        print(f"✗ Error creating {idx_name}: {e}")

conn.commit()

print("\n" + "=" * 70)
print("MIGRATION COMPLETE")
print("=" * 70)

# Verify new structure
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'character_modifiers' 
    ORDER BY ordinal_position
""")

print("\nUpdated character_modifiers structure:")
for col in cursor.fetchall():
    print(f"  {col[0]:<30} {col[1]}")

cursor.close()
conn.close()
