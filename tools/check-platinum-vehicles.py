#!/usr/bin/env python3
"""Check Platinum's vehicle data in database"""
import os
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

# Get character ID
cur.execute("""
    SELECT id, name, street_name 
    FROM characters 
    WHERE street_name = 'Platinum'
""")
char = cur.fetchone()

if not char:
    print("Platinum not found!")
    conn.close()
    exit(1)

print(f"Character: {char['name']} ({char['street_name']})")
print(f"ID: {char['id']}\n")

# Get vehicles
cur.execute("""
    SELECT * 
    FROM character_vehicles 
    WHERE character_id = %s
""", (char['id'],))

vehicles = cur.fetchall()

if vehicles:
    print(f"Found {len(vehicles)} vehicle(s):\n")
    for v in vehicles:
        print(f"Vehicle: {v['vehicle_name']}")
        print(f"  Type: {v.get('vehicle_type')}")
        print(f"  Handling: {v.get('handling')}")
        print(f"  Speed: {v.get('speed')}")
        print(f"  Body: {v.get('body')}")
        print(f"  Armor: {v.get('armor')}")
        print(f"  Signature: {v.get('signature')}")
        print(f"  Autopilot: {v.get('autopilot')}")
        print(f"  Pilot: {v.get('pilot')}")
        print(f"  Sensor: {v.get('sensor')}")
        print(f"  Cargo: {v.get('cargo')}")
        print(f"  Load: {v.get('load')}")
        print(f"  Seating: {v.get('seating')}")
        print(f"  Notes: {v.get('notes')}")
        print()
else:
    print("No vehicles found in character_vehicles table")

conn.close()
