#!/usr/bin/env python3
"""
Show all user queries from query_logs and query_attempts
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
    
    # Get all query_logs entries
    print("=" * 80)
    print("QUERY LOGS - All User Queries (224 entries)")
    print("=" * 80)
    
    cur.execute("""
        SELECT 
            timestamp,
            query_text,
            intent,
            classification,
            gm_response,
            result_count,
            execution_time_ms
        FROM query_logs
        ORDER BY timestamp DESC
    """)
    
    rows = cur.fetchall()
    for i, row in enumerate(rows, 1):
        timestamp, query_text, intent, classification, gm_response, result_count, exec_time = row
        
        print(f"\n[{i}] {timestamp}")
        print(f"Query: {query_text}")
        print(f"Intent: {intent}")
        
        if classification:
            try:
                if isinstance(classification, str):
                    class_data = json.loads(classification)
                else:
                    class_data = classification
                print(f"Classification: {json.dumps(class_data, indent=2)}")
            except:
                print(f"Classification: {classification}")
        
        if gm_response:
            print(f"GM Response: {gm_response[:200]}{'...' if len(gm_response) > 200 else ''}")
        
        if result_count:
            print(f"Results: {result_count} | Execution: {exec_time}ms")
        
        print("-" * 80)
    
    # Get all query_attempts entries
    print("\n" + "=" * 80)
    print("QUERY ATTEMPTS - Conversation Attempts (8 entries)")
    print("=" * 80)
    
    cur.execute("""
        SELECT 
            timestamp,
            query_text,
            intent_detected,
            confidence,
            needed_clarification,
            clarification_shown,
            user_response,
            final_intent
        FROM query_attempts
        ORDER BY timestamp DESC
    """)
    
    rows = cur.fetchall()
    for i, row in enumerate(rows, 1):
        timestamp, query_text, intent, confidence, needed_clarif, clarif_shown, user_resp, final_intent = row
        
        print(f"\n[{i}] {timestamp}")
        print(f"Query: {query_text}")
        print(f"Intent Detected: {intent} (confidence: {confidence})")
        
        if needed_clarif:
            print(f"Needed Clarification: Yes")
            if clarif_shown:
                print(f"Clarification Shown: {json.dumps(clarif_shown, indent=2)}")
        
        if user_resp:
            print(f"User Response: {user_resp}")
        
        if final_intent:
            print(f"Final Intent: {final_intent}")
        
        print("-" * 80)
    
    # Get n8n chat histories
    print("\n" + "=" * 80)
    print("N8N CHAT HISTORIES (24 entries)")
    print("=" * 80)
    
    cur.execute("""
        SELECT 
            id,
            session_id,
            message
        FROM n8n_chat_histories
        ORDER BY id DESC
    """)
    
    rows = cur.fetchall()
    for row in rows:
        msg_id, session_id, message = row
        
        print(f"\n[{msg_id}] Session: {session_id}")
        
        if message:
            try:
                if isinstance(message, str):
                    msg_data = json.loads(message)
                else:
                    msg_data = message
                print(f"Message: {json.dumps(msg_data, indent=2)}")
            except:
                print(f"Message: {message}")
        
        print("-" * 80)
    
    conn.close()

if __name__ == "__main__":
    main()
