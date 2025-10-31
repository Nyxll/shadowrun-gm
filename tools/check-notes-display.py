#!/usr/bin/env python3
"""
Check if character notes are in the database and being returned by API
"""
import os
from dotenv import load_dotenv
import psycopg2
import json

load_dotenv()

def check_notes():
    """Check notes for all characters"""
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    try:
        cur = conn.cursor()
        
        # Check if notes column exists and has data
        cur.execute("""
            SELECT name, notes, char_length(notes) as note_length
            FROM characters
            WHERE notes IS NOT NULL AND notes != ''
            ORDER BY name
        """)
        
        characters_with_notes = cur.fetchall()
        
        print("=" * 60)
        print("CHARACTERS WITH NOTES")
        print("=" * 60)
        
        if characters_with_notes:
            for name, notes, length in characters_with_notes:
                print(f"\n{name}:")
                print(f"  Length: {length} characters")
                print(f"  Preview: {notes[:100]}...")
        else:
            print("No characters have notes in the database")
        
        # Check all characters
        print("\n" + "=" * 60)
        print("ALL CHARACTERS - NOTES STATUS")
        print("=" * 60)
        
        cur.execute("""
            SELECT name, 
                   CASE 
                       WHEN notes IS NULL THEN 'NULL'
                       WHEN notes = '' THEN 'EMPTY STRING'
                       ELSE 'HAS NOTES (' || char_length(notes) || ' chars)'
                   END as notes_status
            FROM characters
            ORDER BY name
        """)
        
        all_chars = cur.fetchall()
        for name, status in all_chars:
            print(f"{name}: {status}")
        
        cur.close()
        
    finally:
        conn.close()

if __name__ == "__main__":
    check_notes()
