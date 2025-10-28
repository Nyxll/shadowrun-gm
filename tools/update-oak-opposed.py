#!/usr/bin/env python3
"""Update Oak totem to oppose Illusion spells for testing"""
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

# Update Oak to oppose Illusion
cur.execute("""
    UPDATE totems 
    SET opposed_categories = ARRAY['Illusion']
    WHERE totem_name = 'Oak'
""")

conn.commit()
print("✓ Updated Oak totem to oppose Illusion spells")

# Verify
cur.execute("""
    SELECT totem_name, favored_categories, opposed_categories
    FROM totems
    WHERE totem_name = 'Oak'
""")

row = cur.fetchone()
print(f"\nOak totem configuration:")
print(f"  Favored: {row[1]}")
print(f"  Opposed: {row[2]}")

cur.close()
conn.close()
