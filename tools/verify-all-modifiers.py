#!/usr/bin/env python3
"""
Verify all character modifiers have been loaded
"""
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

print("\nCharacter Modifier Summary")
print("=" * 80)

cursor.execute("""
    SELECT 
        c.name,
        c.street_name,
        COUNT(cm.id) as modifier_count
    FROM characters c
    LEFT JOIN character_modifiers cm ON c.id = cm.character_id
    GROUP BY c.id, c.name, c.street_name
    ORDER BY c.street_name
""")

characters = cursor.fetchall()

for char in characters:
    print(f"{char['street_name']:15s} ({char['name']:30s}): {char['modifier_count']:3d} modifiers")

print("\n" + "=" * 80)

# Show total counts
cursor.execute("SELECT COUNT(*) as total FROM characters")
char_count = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as total FROM character_modifiers")
mod_count = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as total FROM character_skills")
skill_count = cursor.fetchone()['total']

cursor.execute("SELECT COUNT(*) as total FROM character_gear")
gear_count = cursor.fetchone()['total']

print(f"\nDatabase Summary:")
print(f"  Characters: {char_count}")
print(f"  Modifiers:  {mod_count}")
print(f"  Skills:     {skill_count}")
print(f"  Gear:       {gear_count}")

conn.close()
