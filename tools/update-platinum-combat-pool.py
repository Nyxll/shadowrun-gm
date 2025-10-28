#!/usr/bin/env python3
"""Update Platinum's combat pool to correct value"""
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

# Update Platinum's combat pool to 17 (from character file)
cur.execute("""
    UPDATE characters 
    SET combat_pool = 17
    WHERE street_name = 'Platinum'
""")

conn.commit()
print(f"Updated Platinum's combat pool to 17")

# Verify
cur.execute("""
    SELECT combat_pool, current_quickness 
    FROM characters 
    WHERE street_name = 'Platinum'
""")
row = cur.fetchone()
print(f"Verified - Combat Pool: {row[0]}, Quickness: {row[1]}")

conn.close()
