#!/usr/bin/env python3
"""
Update combat pool for all characters using correct formula:
Combat Pool = (current_quickness + current_intelligence + current_willpower) / 2
"""
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def main():
    """Update combat pools for all characters"""
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        cursor_factory=RealDictCursor
    )
    
    cursor = conn.cursor()
    
    try:
        # Get all characters with their current attributes
        cursor.execute("""
            SELECT 
                id,
                name,
                current_quickness,
                current_intelligence,
                current_willpower,
                combat_pool as old_combat_pool
            FROM characters
            ORDER BY name
        """)
        
        characters = cursor.fetchall()
        
        print(f"Updating combat pools for {len(characters)} characters...\n")
        
        updated = 0
        for char in characters:
            quickness = char['current_quickness'] or 1
            intelligence = char['current_intelligence'] or 1
            willpower = char['current_willpower'] or 1
            
            # Calculate new combat pool
            new_combat_pool = (quickness + intelligence + willpower) // 2
            old_combat_pool = char['old_combat_pool']
            
            # Update if different
            if new_combat_pool != old_combat_pool:
                cursor.execute("""
                    UPDATE characters
                    SET combat_pool = %s
                    WHERE id = %s
                """, (new_combat_pool, char['id']))
                
                print(f"{char['name']:20} Q:{quickness} I:{intelligence} W:{willpower} -> Combat Pool: {old_combat_pool} → {new_combat_pool}")
                updated += 1
            else:
                print(f"{char['name']:20} Q:{quickness} I:{intelligence} W:{willpower} -> Combat Pool: {new_combat_pool} (unchanged)")
        
        conn.commit()
        print(f"\n✓ Updated {updated} characters")
        
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
        raise
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()
