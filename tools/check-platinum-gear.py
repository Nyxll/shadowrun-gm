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

cursor.execute("SELECT id FROM characters WHERE name = 'Kent Jefferies'")
char = cursor.fetchone()
char_id = char[0]

cursor.execute('SELECT gear_name, gear_type FROM character_gear WHERE character_id = %s', (char_id,))
rows = cursor.fetchall()

print('Platinum gear in database:')
for r in rows:
    print(f'  {r[0]}: {r[1]}')

cursor.close()
conn.close()
