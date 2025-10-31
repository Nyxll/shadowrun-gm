#!/usr/bin/env python3
"""
Show all session history and user queries
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
    
    # Check session_logs structure
    print("=== session_logs table structure ===")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'session_logs'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    # Get all session logs
    print("\n=== All Session Logs ===")
    cur.execute("SELECT * FROM session_logs ORDER BY timestamp DESC LIMIT 50")
    
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    
    if rows:
        print(f"\nFound {len(rows)} session log entries:\n")
        for row in rows:
            data = dict(zip(col_names, row))
            print(f"[{data.get('timestamp', 'N/A')}] Session: {data.get('session_id', 'N/A')}")
            print(f"  Event: {data.get('event_type', 'N/A')}")
            
            # Try to parse event_data if it's JSON
            event_data = data.get('event_data')
            if event_data:
                try:
                    if isinstance(event_data, str):
                        parsed = json.loads(event_data)
                    else:
                        parsed = event_data
                    
                    # Look for user messages
                    if 'message' in parsed:
                        print(f"  MESSAGE: {parsed['message']}")
                    elif 'user_query' in parsed:
                        print(f"  QUERY: {parsed['user_query']}")
                    else:
                        print(f"  Data: {json.dumps(parsed, indent=4)[:200]}")
                except:
                    print(f"  Data: {str(event_data)[:200]}")
            print()
    else:
        print("No session logs found")
    
    # Check n8n_chat_histories
    print("\n=== n8n_chat_histories table ===")
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'n8n_chat_histories'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    for col in columns:
        print(f"  {col[0]}: {col[1]}")
    
    cur.execute("SELECT * FROM n8n_chat_histories ORDER BY id DESC LIMIT 20")
    rows = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    
    if rows:
        print(f"\nFound {len(rows)} chat history entries:\n")
        for row in rows:
            data = dict(zip(col_names, row))
            print(f"Session: {data.get('session_id', 'N/A')}")
            print(f"  Message: {str(data.get('message', 'N/A'))[:200]}")
            print()
    else:
        print("No chat histories found")
    
    conn.close()

if __name__ == "__main__":
    main()
