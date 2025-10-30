#!/usr/bin/env python3
"""
Check if character_powers UUID migration was successful
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    cur = conn.cursor()
    
    # Check if character_powers table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'character_powers'
        );
    """)
    table_exists = cur.fetchone()[0]
    
    if not table_exists:
        print("❌ character_powers table does not exist")
        conn.close()
        exit(1)
    
    # Check column type for character_id
    cur.execute("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = 'character_powers' 
        AND column_name = 'character_id';
    """)
    result = cur.fetchone()
    
    if result:
        data_type = result[0]
        print(f"✓ character_powers.character_id type: {data_type}")
        
        if data_type == 'uuid':
            print("✅ Migration successful - character_id is now UUID")
        else:
            print(f"⚠️  Migration may not have completed - character_id is {data_type}, not UUID")
    else:
        print("❌ character_id column not found in character_powers")
    
    # Check if there's data
    cur.execute("SELECT COUNT(*) FROM character_powers;")
    count = cur.fetchone()[0]
    print(f"✓ character_powers has {count} records")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error checking migration status: {e}")
    exit(1)
