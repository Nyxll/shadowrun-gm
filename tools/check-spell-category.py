#!/usr/bin/env python3
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
cur.execute("SELECT spell_name, spell_category FROM character_spells WHERE LOWER(spell_name) = 'treat' LIMIT 1")
row = cur.fetchone()
if row:
    print(f"Spell: {row[0]}, Category: {row[1]}")
else:
    print("Treat spell not found")

# Also check Oak's favored categories
cur.execute("SELECT favored_categories FROM totems WHERE totem_name = 'Oak'")
row = cur.fetchone()
if row:
    print(f"Oak favored categories: {row[0]}")
    print(f"Type: {type(row[0])}")

cur.close()
conn.close()
