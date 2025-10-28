#!/usr/bin/env python3
"""Check data types in existing schema"""
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

cursor = conn.cursor()

# Check characters table ID type
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'characters' AND column_name = 'id'
""")
print("Characters table ID:", cursor.fetchone())

# Check if campaigns table exists
cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_name = 'campaigns'
""")
result = cursor.fetchone()
if result:
    print("Campaigns table exists - checking ID type")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'campaigns' AND column_name = 'id'
    """)
    print("Campaigns table ID:", cursor.fetchone())
else:
    print("Campaigns table does not exist yet")

cursor.close()
conn.close()
