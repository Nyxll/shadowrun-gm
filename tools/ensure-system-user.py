#!/usr/bin/env python3
"""
Ensure SYSTEM user exists in users table
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
    
    # Check if users table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'users'
        )
    """)
    
    if not cur.fetchone()[0]:
        print("Creating users table...")
        cur.execute("""
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email TEXT UNIQUE NOT NULL,
                display_name TEXT,
                user_type TEXT DEFAULT 'USER',
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        print("✓ Users table created")
    
    # Check if SYSTEM user exists
    cur.execute("SELECT id FROM users WHERE user_type = 'SYSTEM' LIMIT 1")
    result = cur.fetchone()
    
    if result:
        print(f"✓ SYSTEM user already exists: {result[0]}")
    else:
        print("Creating SYSTEM user...")
        cur.execute("""
            INSERT INTO users (email, display_name, user_type)
            VALUES ('system@shadowrun-gm.local', 'System', 'SYSTEM')
            RETURNING id
        """)
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"✓ SYSTEM user created: {user_id}")
    
    # Check if AI user exists
    cur.execute("SELECT id FROM users WHERE user_type = 'AI' LIMIT 1")
    result = cur.fetchone()
    
    if result:
        print(f"✓ AI user already exists: {result[0]}")
    else:
        print("Creating AI user...")
        cur.execute("""
            INSERT INTO users (email, display_name, user_type)
            VALUES ('ai@shadowrun-gm.local', 'AI Assistant', 'AI')
            RETURNING id
        """)
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"✓ AI user created: {user_id}")
    
    cur.close()
    conn.close()
    
    print("\n✓ All system users ready")

if __name__ == "__main__":
    main()
