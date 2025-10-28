#!/usr/bin/env python3
"""
Check Platinum character name in database
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def main():
    """Check Platinum character"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB'),
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        
        # Check all characters
        cursor.execute("""
            SELECT id, name, street_name
            FROM characters
            ORDER BY name
        """)
        
        print("\n=== ALL CHARACTERS ===")
        for char in cursor.fetchall():
            print(f"ID: {char['id']}")
            print(f"  Name: {char['name']}")
            print(f"  Street Name: {char['street_name']}")
            print()
        
        # Try to find Platinum
        cursor.execute("""
            SELECT id, name, street_name
            FROM characters
            WHERE LOWER(name) = LOWER(%s) 
               OR LOWER(COALESCE(street_name, '')) = LOWER(%s)
        """, ('platinum', 'platinum'))
        
        result = cursor.fetchone()
        
        print("\n=== PLATINUM LOOKUP ===")
        if result:
            print(f"FOUND!")
            print(f"ID: {result['id']}")
            print(f"Name: {result['name']}")
            print(f"Street Name: {result['street_name']}")
        else:
            print("NOT FOUND")
            
            # Try partial match
            cursor.execute("""
                SELECT id, name, street_name
                FROM characters
                WHERE LOWER(name) LIKE LOWER(%s) 
                   OR LOWER(COALESCE(street_name, '')) LIKE LOWER(%s)
            """, ('%platinum%', '%platinum%'))
            
            partial = cursor.fetchall()
            if partial:
                print("\nPartial matches:")
                for char in partial:
                    print(f"  {char['name']} / {char['street_name']}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
