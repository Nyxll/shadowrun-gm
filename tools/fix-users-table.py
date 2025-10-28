#!/usr/bin/env python3
"""
Fix users table to add user_type column if missing
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
    
    cur = conn.cursor()
    
    # Check current users table schema
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'users'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print("Current users table columns:")
    for col_name, data_type in columns:
        print(f"  - {col_name}: {data_type}")
    
    # Check if user_type column exists
    column_names = [col[0] for col in columns]
    
    if 'user_type' not in column_names:
        print("\nAdding user_type column...")
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN user_type TEXT DEFAULT 'USER'
        """)
        conn.commit()
        print("✓ user_type column added")
    else:
        print("\n✓ user_type column already exists")
    
    # Now ensure SYSTEM user exists
    cur.execute("SELECT id, email FROM users WHERE user_type = 'SYSTEM' LIMIT 1")
    result = cur.fetchone()
    
    if result:
        print(f"✓ SYSTEM user already exists: {result[0]} ({result[1]})")
    else:
        print("Creating SYSTEM user...")
        cur.execute("""
            INSERT INTO users (email, user_type)
            VALUES ('system@shadowrun-gm.local', 'SYSTEM')
            RETURNING id
        """)
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"✓ SYSTEM user created: {user_id}")
    
    # Ensure AI user exists
    cur.execute("SELECT id, email FROM users WHERE user_type = 'AI' LIMIT 1")
    result = cur.fetchone()
    
    if result:
        print(f"✓ AI user already exists: {result[0]} ({result[1]})")
    else:
        print("Creating AI user...")
        cur.execute("""
            INSERT INTO users (email, user_type)
            VALUES ('ai@shadowrun-gm.local', 'AI')
            RETURNING id
        """)
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"✓ AI user created: {user_id}")
    
    cur.close()
    conn.close()
    
    print("\n✓ Users table ready for imports")

if __name__ == "__main__":
    main()
