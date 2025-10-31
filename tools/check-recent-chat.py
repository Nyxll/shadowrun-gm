#!/usr/bin/env python3
"""Check recent chat history"""
import os
import psycopg2
from dotenv import load_dotenv
import json

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Get recent messages about Platinum shooting
cur.execute("""
    SELECT session_id, message 
    FROM n8n_chat_histories 
    WHERE message::text LIKE '%Platinum%shoot%'
    ORDER BY id DESC 
    LIMIT 10
""")

rows = cur.fetchall()

print("=== Recent Chat Messages about Platinum Shooting ===\n")
for session_id, message in rows:
    msg_data = json.loads(message) if isinstance(message, str) else message
    print(f"Session: {session_id}")
    print(f"Type: {msg_data.get('type', 'unknown')}")
    print(f"Content: {msg_data.get('content', 'N/A')[:200]}")
    if 'tool_calls' in msg_data and msg_data['tool_calls']:
        print(f"Tool Calls: {len(msg_data['tool_calls'])}")
        for tc in msg_data['tool_calls']:
            print(f"  - {tc.get('function', {}).get('name', 'unknown')}")
    print("---\n")

conn.close()
