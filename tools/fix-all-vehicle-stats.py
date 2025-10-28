#!/usr/bin/env python3
"""Fix ALL characters' vehicle stats by parsing notes into proper columns"""
import os
import re
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    cursor_factory=RealDictCursor
)

cur = conn.cursor()

# Get ALL vehicles from ALL characters
cur.execute("""
    SELECT id, vehicle_name, notes, character_id
    FROM character_vehicles
    ORDER BY vehicle_name
""")

vehicles = cur.fetchall()

print(f"Processing {len(vehicles)} vehicles across all characters...\n")

updated_count = 0

for vehicle in vehicles:
    notes = vehicle['notes'] or ''
    
    # Skip if no notes to parse
    if not notes:
        continue
    
    print(f"Processing: {vehicle['vehicle_name']}")
    
    # Parse stats from notes
    handling = None
    speed = None
    body = None
    armor = None
    signature = None
    pilot = None
    modifications = None
    
    # Extract Handling (e.g., "Handling: 3/8")
    handling_match = re.search(r'Handling:\s*(\d+/\d+)', notes)
    if handling_match:
        handling = handling_match.group(1)
    
    # Extract Speed (e.g., "Speed: 210")
    speed_match = re.search(r'Speed:\s*(\d+)', notes)
    if speed_match:
        speed = int(speed_match.group(1))
    
    # Extract Body (e.g., "Body: 8")
    body_match = re.search(r'Body:\s*(\d+)', notes)
    if body_match:
        body = int(body_match.group(1))
    
    # Extract Armor (e.g., "Armor: 2")
    armor_match = re.search(r'Armor:\s*(\d+)', notes)
    if armor_match:
        armor = int(armor_match.group(1))
    
    # Extract Signature (e.g., "Signature: N/A" or "Signature: 2")
    signature_match = re.search(r'Signature:\s*(.+?)(?:\n|$)', notes)
    if signature_match:
        sig_value = signature_match.group(1).strip()
        signature = None if sig_value.upper() == 'N/A' else sig_value
    
    # Extract Pilot (e.g., "Pilot: N/A" or "Pilot: 3")
    pilot_match = re.search(r'Pilot:\s*(.+?)(?:\n|$)', notes)
    if pilot_match:
        pilot_value = pilot_match.group(1).strip()
        pilot = None if pilot_value.upper() == 'N/A' else pilot_value
    
    # Extract Modifications (e.g., "Modifications: N/A" or "Modifications: Smartlink")
    # Store as JSONB object
    mods_match = re.search(r'Modifications:\s*(.+?)(?:\n|$)', notes)
    if mods_match:
        mods_value = mods_match.group(1).strip()
        if mods_value.upper() == 'N/A':
            modifications = None
        else:
            # Convert to JSONB format
            import json
            modifications = json.dumps({"description": mods_value})
    
    # Only update if we found at least one stat
    if any([handling, speed, body, armor, signature, pilot, modifications]):
        print(f"  Parsed - Handling: {handling}, Speed: {speed}, Body: {body}, Armor: {armor}")
        print(f"           Signature: {signature}, Pilot: {pilot}, Mods: {modifications}")
        
        # Update vehicle with parsed stats
        cur.execute("""
            UPDATE character_vehicles
            SET handling = %s,
                speed = %s,
                body = %s,
                armor = %s,
                signature = %s,
                pilot = %s,
                modifications = %s
            WHERE id = %s
        """, (handling, speed, body, armor, signature, pilot, modifications, vehicle['id']))
        
        updated_count += 1
        print(f"  ✓ Updated")
    else:
        print(f"  ⚠ No stats found in notes")
    
    print()

conn.commit()
print(f"\n✓ Updated {updated_count} of {len(vehicles)} vehicles")

# Verify - show summary by character
cur.execute("""
    SELECT 
        c.street_name,
        COUNT(v.id) as vehicle_count,
        COUNT(CASE WHEN v.speed IS NOT NULL THEN 1 END) as with_stats
    FROM characters c
    LEFT JOIN character_vehicles v ON v.character_id = c.id
    WHERE v.id IS NOT NULL
    GROUP BY c.street_name
    ORDER BY c.street_name
""")

print("\nVehicles by character:")
for row in cur.fetchall():
    print(f"  {row['street_name']}: {row['with_stats']}/{row['vehicle_count']} vehicles have stats")

conn.close()
