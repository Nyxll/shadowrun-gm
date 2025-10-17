#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD')
)

cur = conn.cursor()
cur.execute("""
    SELECT category, subcategory, COUNT(*) 
    FROM gear 
    GROUP BY category, subcategory 
    ORDER BY category, subcategory
""")

print("\nActual data loaded in gear table:")
print("-" * 60)
for row in cur.fetchall():
    cat = row[0]
    subcat = row[1] or "(none)"
    count = row[2]
    print(f"{cat:15} {subcat:25} {count:4} items")

conn.close()
