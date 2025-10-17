#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / '.env')

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    database=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

for table in ['spells', 'powers', 'totems']:
    cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table}' ORDER BY ordinal_position")
    columns = [r[0] for r in cur.fetchall()]
    print(f"\n{table.upper()} columns:")
    for col in columns:
        print(f"  - {col}")

conn.close()
