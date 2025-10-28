#!/usr/bin/env python3
"""Check Block's attributes"""
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

cur = conn.cursor()
cur.execute("""
    SELECT name, base_body, base_quickness, base_strength, 
           base_charisma, base_intelligence, base_willpower,
           current_body, current_quickness, current_strength,
           current_charisma, current_intelligence, current_willpower
    FROM characters 
    WHERE street_name = 'Block'
""")

char = cur.fetchone()
if char:
    print("Block's Attributes:")
    print(f"  Body: {char['base_body']} -> {char['current_body']}")
    print(f"  Quickness: {char['base_quickness']} -> {char['current_quickness']}")
    print(f"  Strength: {char['base_strength']} -> {char['current_strength']}")
    print(f"  Charisma: {char['base_charisma']} -> {char['current_charisma']}")
    print(f"  Intelligence: {char['base_intelligence']} -> {char['current_intelligence']}")
    print(f"  Willpower: {char['base_willpower']} -> {char['current_willpower']}")
else:
    print("Block not found!")

conn.close()
