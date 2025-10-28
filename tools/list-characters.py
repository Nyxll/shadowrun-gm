#!/usr/bin/env python3
"""List all characters in database"""
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
cur.execute('SELECT name, street_name FROM characters ORDER BY name')
chars = cur.fetchall()

print('Characters in database:')
for c in chars:
    if c[1]:
        print(f'  - {c[0]} (Street Name: {c[1]})')
    else:
        print(f'  - {c[0]}')

conn.close()
