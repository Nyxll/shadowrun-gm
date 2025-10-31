#!/usr/bin/env python3
"""
Check for conversation history in database and logs
"""
import os
from dotenv import load_dotenv
import psycopg2

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
    
    # Check for session/conversation tables
    print("=== Checking for conversation-related tables ===")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public' 
        AND (table_name LIKE '%session%' 
             OR table_name LIKE '%conversation%' 
             OR table_name LIKE '%message%'
             OR table_name LIKE '%chat%')
    """)
    
    tables = cur.fetchall()
    if tables:
        print("Found tables:")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("No conversation tables found in database")
    
    print("\n=== Checking query_logs for user queries ===")
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'query_logs'
        )
    """)
    
    if cur.fetchone()[0]:
        cur.execute("""
            SELECT 
                created_at,
                user_query,
                intent_category
            FROM query_logs
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        logs = cur.fetchall()
        if logs:
            print(f"\nFound {len(logs)} recent queries:")
            for log in logs:
                print(f"\n[{log[0]}] Category: {log[2]}")
                print(f"Query: {log[1][:200]}{'...' if len(log[1]) > 200 else ''}")
        else:
            print("No queries found in query_logs")
    else:
        print("query_logs table does not exist")
    
    conn.close()

if __name__ == "__main__":
    main()
