#!/usr/bin/env python3
"""Check Platinum's combat pool value in database"""
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
cur.execute("""
    SELECT combat_pool, current_quickness 
    FROM characters 
    WHERE street_name = 'Platinum'
""")

row = cur.fetchone()
if row:
    print(f"Combat Pool in DB: {row[0]}")
    print(f"Current Quickness: {row[1]}")
    if row[1]:
        print(f"Quickness/2: {row[1] // 2}")
else:
    print("Platinum not found!")

conn.close()
