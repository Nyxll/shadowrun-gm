#!/usr/bin/env python3
"""
Insert data via Supabase REST API
"""
import os
import sys
import json
import requests
import time
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
from decimal import Decimal

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

# Old database connection (local)
OLD_DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'database': os.getenv('POSTGRES_DB')
}

def get_old_db_connection():
    """Connect to old database"""
    return psycopg2.connect(**OLD_DB_CONFIG)

def serialize_data(obj):
    """Convert datetime and Decimal objects to JSON-serializable types"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: serialize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_data(item) for item in obj]
    return obj

def insert_via_api(table, data):
    """Insert data via Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    # Serialize datetime objects
    data = serialize_data(data)
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print(f"✓ Inserted into {table}: {data.get('name', data.get('id'))}")
        return True, None
    else:
        error_msg = f"Failed to insert into {table}: {response.status_code}\n  Error: {response.text}"
        print(f"✗ {error_msg}")
        return False, error_msg

def test_single_inserts():
    """Test inserting 1 record of each type"""
    print("=== Testing Single Inserts ===\n")
    
    conn = get_old_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Insert one metatype
    print("1. Testing metatypes...")
    cur.execute("SELECT * FROM metatypes WHERE name = 'Human' LIMIT 1")
    metatype = dict(cur.fetchone())
    # Convert to API format
    metatype_data = {k: v for k, v in metatype.items() if v is not None}
    insert_via_api('metatypes', metatype_data)
    
    # Test 2: Insert one power
    print("\n2. Testing powers...")
    cur.execute("SELECT * FROM powers WHERE name = 'Astral Perception' LIMIT 1")
    power = dict(cur.fetchone())
    power_data = {k: v for k, v in power.items() if v is not None}
    insert_via_api('powers', power_data)
    
    # Test 3: Insert one gear item
    print("\n3. Testing gear...")
    cur.execute("SELECT * FROM gear WHERE name = 'Chipjack' LIMIT 1")
    gear = dict(cur.fetchone())
    gear_data = {k: v for k, v in gear.items() if v is not None}
    insert_via_api('gear', gear_data)
    
    cur.close()
    conn.close()
    
    print("\n=== Test Complete ===")

def insert_all_data():
    """Insert all data from old database with rate limiting"""
    print("=== Inserting All Data ===\n")
    print("Rate limit: 1 request every 3 seconds\n")
    
    conn = get_old_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    tables = ['metatypes', 'powers', 'spells', 'totems', 'gear', 'rules_content']
    
    for table in tables:
        print(f"\nInserting {table}...")
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        
        success_count = 0
        fail_count = 0
        total = len(rows)
        
        for i, row in enumerate(rows, 1):
            data = {k: v for k, v in dict(row).items() if v is not None}
            
            success, error = insert_via_api(table, data)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
                # Stop on first error
                print(f"\n❌ STOPPED: Error at record {i}/{total}")
                print(f"Table: {table}, ID: {data.get('id')}, Name: {data.get('name', 'N/A')}")
                print(f"\nProgress: {success_count} succeeded, {fail_count} failed")
                print(f"\nFix the issue and re-run to continue")
                cur.close()
                conn.close()
                sys.exit(1)
            
            # Progress indicator
            if i % 10 == 0 or i == total:
                print(f"  Progress: {i}/{total} ({success_count} succeeded)")
            
            # Rate limiting: wait 3 seconds between requests
            if i < total:
                time.sleep(3)
        
        print(f"  {table} complete: {success_count} succeeded, {fail_count} failed")
    
    cur.close()
    conn.close()
    
    print("\n=== All Data Inserted ===")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'all':
        insert_all_data()
    else:
        test_single_inserts()
        print("\nTo insert all data, run: python tools/insert-via-api.py all")
