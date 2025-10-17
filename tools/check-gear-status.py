#!/usr/bin/env python3
"""
Quick check to see if gear data has been loaded
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

try:
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()
    
    # Check if gear table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'gear'
        );
    """)
    table_exists = cur.fetchone()[0]
    
    if not table_exists:
        print("❌ Gear table does not exist yet.")
        print("   Run: psql -U postgres -d shadowrun -f schema/gear_system.sql")
    else:
        print("✅ Gear table exists")
        
        # Count total gear items
        cur.execute("SELECT COUNT(*) FROM gear;")
        total = cur.fetchone()[0]
        print(f"   Total gear items: {total}")
        
        if total == 0:
            print("\n⚠️  No gear loaded yet.")
            print("   Run: python tools/gear_loader.py")
        else:
            # Show breakdown by category
            cur.execute("""
                SELECT category, COUNT(*) as count 
                FROM gear 
                GROUP BY category 
                ORDER BY count DESC;
            """)
            
            print("\n📊 Gear by category:")
            for row in cur.fetchall():
                print(f"   {row[0]}: {row[1]} items")
            
            # Show data sources
            cur.execute("""
                SELECT data_source, COUNT(*) as count 
                FROM gear 
                GROUP BY data_source;
            """)
            
            print("\n📁 Data sources:")
            for row in cur.fetchall():
                print(f"   {row[0]}: {row[1]} items")
            
            # Check for load history
            cur.execute("SELECT COUNT(*) FROM gear_load_history;")
            history_count = cur.fetchone()[0]
            print(f"\n📝 Load history entries: {history_count}")
            
            if history_count > 0:
                cur.execute("""
                    SELECT action, COUNT(*) 
                    FROM gear_load_history 
                    GROUP BY action;
                """)
                print("   Actions:")
                for row in cur.fetchall():
                    print(f"   - {row[0]}: {row[1]}")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure:")
    print("1. PostgreSQL is running")
    print("2. Database 'shadowrun' exists")
    print("3. .env file has correct credentials")
