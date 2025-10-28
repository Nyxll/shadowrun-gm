#!/usr/bin/env python3
"""
Create SQL functions for getting/creating system users
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
    
    print("Creating get_system_user_id() function...")
    cur.execute("""
        CREATE OR REPLACE FUNCTION get_system_user_id()
        RETURNS UUID AS $$
        DECLARE
            system_user_id UUID;
        BEGIN
            SELECT id INTO system_user_id 
            FROM users 
            WHERE user_type = 'SYSTEM' 
            LIMIT 1;
            
            IF system_user_id IS NULL THEN
                INSERT INTO users (email, user_type)
                VALUES ('system@shadowrun-gm.local', 'SYSTEM')
                RETURNING id INTO system_user_id;
            END IF;
            
            RETURN system_user_id;
        END;
        $$ LANGUAGE plpgsql;
    """)
    conn.commit()
    print("✓ get_system_user_id() function created")
    
    print("\nCreating get_ai_user_id() function...")
    cur.execute("""
        CREATE OR REPLACE FUNCTION get_ai_user_id()
        RETURNS UUID AS $$
        DECLARE
            ai_user_id UUID;
        BEGIN
            SELECT id INTO ai_user_id 
            FROM users 
            WHERE user_type = 'AI' 
            LIMIT 1;
            
            IF ai_user_id IS NULL THEN
                INSERT INTO users (email, user_type)
                VALUES ('ai@shadowrun-gm.local', 'AI')
                RETURNING id INTO ai_user_id;
            END IF;
            
            RETURN ai_user_id;
        END;
        $$ LANGUAGE plpgsql;
    """)
    conn.commit()
    print("✓ get_ai_user_id() function created")
    
    # Test the functions
    print("\nTesting functions...")
    cur.execute("SELECT get_system_user_id()")
    system_id = cur.fetchone()[0]
    print(f"✓ SYSTEM user ID: {system_id}")
    
    cur.execute("SELECT get_ai_user_id()")
    ai_id = cur.fetchone()[0]
    print(f"✓ AI user ID: {ai_id}")
    
    cur.close()
    conn.close()
    
    print("\n✓ User functions ready for CRUD API")

if __name__ == "__main__":
    main()
