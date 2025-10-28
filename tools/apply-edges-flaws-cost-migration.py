#!/usr/bin/env python3
"""
Apply migration to add cost field to character_edges_flaws
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    print("Applying migration 020: Add cost field to character_edges_flaws...")
    
    with open('migrations/020_add_edges_flaws_cost.sql', 'r') as f:
        migration_sql = f.read()
    
    cur = conn.cursor()
    cur.execute(migration_sql)
    conn.commit()
    cur.close()
    
    print("✓ Migration applied successfully")
    
    # Verify the column was added
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'character_edges_flaws' AND column_name = 'cost'
    """)
    result = cur.fetchone()
    
    if result:
        print(f"✓ Verified: cost column exists ({result[1]})")
    else:
        print("✗ Warning: cost column not found after migration")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
