#!/usr/bin/env python3
"""
Check UI state data in characters table
"""
import os
from dotenv import load_dotenv
import psycopg2
import json

load_dotenv()

def main():
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # Check for ui_state column
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'characters' 
        AND column_name LIKE '%ui%'
    """)
    
    ui_columns = cur.fetchall()
    print("UI-related columns in characters table:")
    for col, dtype in ui_columns:
        print(f"  - {col}: {dtype}")
    
    if not ui_columns:
        print("  (No UI columns found)")
    
    print()
    
    # Check characters with ui_state
    cur.execute("""
        SELECT character_name, ui_state 
        FROM characters 
        WHERE ui_state IS NOT NULL 
        LIMIT 5
    """)
    
    rows = cur.fetchall()
    print(f"Characters with ui_state data: {len(rows)}")
    for name, ui in rows:
        print(f"\n{name}:")
        if ui:
            print(json.dumps(ui, indent=2))
        else:
            print("  NULL")
    
    # Count NULL ui_state
    cur.execute("SELECT COUNT(*) FROM characters WHERE ui_state IS NULL")
    null_count = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM characters")
    total_count = cur.fetchone()[0]
    
    print(f"\n\nSummary:")
    print(f"  Total characters: {total_count}")
    print(f"  With ui_state: {total_count - null_count}")
    print(f"  Without ui_state (NULL): {null_count}")
    
    conn.close()

if __name__ == "__main__":
    main()
