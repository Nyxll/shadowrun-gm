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
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'characters' AND column_name LIKE '%totem%'
    ORDER BY column_name
""")

print("Totem columns in characters table:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()
