#!/usr/bin/env python3
"""Check Platinum's weapon data"""
import os
import json
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB'),
    row_factory=dict_row
)

cur = conn.cursor()
cur.execute("SELECT relationships FROM characters WHERE name = 'Kent Jefferies'")
result = cur.fetchone()

if result:
    relationships = result['relationships']
    weapons = relationships.get('weapons', [])
    vehicles = relationships.get('vehicles', [])
    
    print("=" * 60)
    print("PLATINUM'S WEAPONS (First 3):")
    print("=" * 60)
    for i, weapon in enumerate(weapons[:3], 1):
        print(f"\n{i}. {weapon['name']}")
        print(f"   Damage: {weapon.get('damage', 'N/A')}")
        print(f"   Conceal: {weapon.get('conceal', 'N/A')}")
        print(f"   Capacity: {weapon.get('capacity', 'N/A')}")
        print(f"   Mode: {weapon.get('mode', 'N/A')}")
        print(f"   TN Modifier: {weapon.get('tn_modifier', 'N/A')}")
        print(f"   Reach: {weapon.get('reach', 'N/A')}")
        if weapon.get('ammo'):
            print(f"   Ammo: {', '.join(weapon['ammo'])}")
        if weapon.get('modifications'):
            print(f"   Mods: {', '.join(weapon['modifications'])}")
    
    print("\n" + "=" * 60)
    print(f"TOTAL WEAPONS: {len(weapons)}")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("PLATINUM'S VEHICLES:")
    print("=" * 60)
    for i, vehicle in enumerate(vehicles, 1):
        print(f"\n{i}. {vehicle['name']}")
        print(f"   Handling: {vehicle.get('handling', 'N/A')}")
        print(f"   Speed: {vehicle.get('speed', 'N/A')}")
        print(f"   Body: {vehicle.get('body', 'N/A')}")
        print(f"   Armor: {vehicle.get('armor', 'N/A')}")
    
    print("\n" + "=" * 60)
    print(f"TOTAL VEHICLES: {len(vehicles)}")
    print("=" * 60)

conn.close()
