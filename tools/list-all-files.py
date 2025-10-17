#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
    port=os.getenv('POSTGRES_PORT', '5434'),
    database=os.getenv('POSTGRES_DB', 'postgres'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD', 'postgres')
)

cur = conn.cursor()

cur.execute('''
    SELECT source_file, COUNT(*) as chunk_count 
    FROM rules_content 
    GROUP BY source_file 
    ORDER BY source_file
''')

print('\n' + '='*70)
print('All Chunked Files in Database')
print('='*70)

results = cur.fetchall()
total = 0

for source, count in results:
    print(f'{source:50} {count:5} chunks')
    total += count

print('='*70)
print(f'{"TOTAL":50} {total:5} chunks')
print('='*70)

conn.close()
