#!/usr/bin/env python3
"""
Check for duplicate records in remote Supabase database
"""
import os
import requests
from dotenv import load_dotenv
from collections import Counter

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL')
SUPABASE_KEY = os.getenv('NEXT_PUBLIC_SUPABASE_ANON_KEY')

def query_table(table):
    """Query all records from a table"""
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=*"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error querying {table}: {response.status_code}")
        print(f"  {response.text}")
        return []

def check_duplicates(table):
    """Check for duplicate IDs and names in a table"""
    print(f"\n{'='*60}")
    print(f"Checking {table}...")
    print(f"{'='*60}")
    
    records = query_table(table)
    total = len(records)
    print(f"Total records: {total}")
    
    if not records:
        print("  No records found or error occurred")
        return
    
    # Check for duplicate IDs
    ids = [r['id'] for r in records]
    id_counts = Counter(ids)
    duplicates_by_id = {id: count for id, count in id_counts.items() if count > 1}
    
    if duplicates_by_id:
        print(f"\n⚠️  DUPLICATE IDs FOUND: {len(duplicates_by_id)}")
        for id, count in sorted(duplicates_by_id.items()):
            print(f"  ID {id}: appears {count} times")
    else:
        print(f"✓ No duplicate IDs (all {total} IDs are unique)")
    
    # Check for duplicate names (if name field exists)
    if records and 'name' in records[0]:
        names = [r['name'] for r in records if r.get('name')]
        name_counts = Counter(names)
        duplicates_by_name = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicates_by_name:
            print(f"\n⚠️  DUPLICATE Names FOUND: {len(duplicates_by_name)}")
            for name, count in sorted(duplicates_by_name.items())[:10]:  # Show first 10
                print(f"  '{name}': appears {count} times")
            if len(duplicates_by_name) > 10:
                print(f"  ... and {len(duplicates_by_name) - 10} more")
        else:
            print(f"✓ No duplicate names (all {len(names)} names are unique)")
    
    # Show sample records
    print(f"\nSample records (first 3):")
    for i, record in enumerate(records[:3], 1):
        print(f"  {i}. ID: {record.get('id')}, Name: {record.get('name', 'N/A')}")

def main():
    """Check all tables for duplicates"""
    print("="*60)
    print("CHECKING REMOTE SUPABASE FOR DUPLICATES")
    print("="*60)
    
    tables = ['metatypes', 'powers', 'spells', 'totems', 'gear', 'rules_content']
    
    for table in tables:
        check_duplicates(table)
    
    print(f"\n{'='*60}")
    print("DUPLICATE CHECK COMPLETE")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
