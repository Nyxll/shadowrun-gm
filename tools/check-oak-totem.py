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

cursor = conn.cursor()
cursor.execute("""
    SELECT totem_name, favored_categories, opposed_categories, bonus_dice, penalty_dice
    FROM totems 
    WHERE LOWER(totem_name) = 'oak'
""")

result = cursor.fetchone()
if result:
    print("Oak totem data:")
    print(f"  Name: {result[0]}")
    print(f"  Favored: {result[1]}")
    print(f"  Opposed: {result[2]}")
    print(f"  Bonus: {result[3]}")
    print(f"  Penalty: {result[4]}")
else:
    print("Oak totem not found!")

conn.close()
