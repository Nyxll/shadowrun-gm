#!/usr/bin/env python3
"""
Compare heavy pistols vs sniper rifles for damage
"""

import psycopg2
import psycopg2.extras
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Database configuration
db_config = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', '')
}

def compare_weapons():
    """Compare heavy pistols vs sniper rifles"""
    conn = psycopg2.connect(**db_config)
    
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            print("=" * 80)
            print("HEAVY PISTOLS vs SNIPER RIFLES - DAMAGE COMPARISON")
            print("=" * 80)
            
            # Get heavy pistols
            cur.execute("""
                SELECT name, subcategory, base_stats, cost, availability
                FROM gear
                WHERE category = 'weapon' 
                AND (subcategory = 'heavy_pistol' OR subcategory LIKE '%heavy%pistol%')
                ORDER BY name
                LIMIT 10
            """)
            
            heavy_pistols = cur.fetchall()
            
            print("\n📍 HEAVY PISTOLS:")
            print("-" * 80)
            for pistol in heavy_pistols:
                stats = pistol['base_stats']
                damage = stats.get('damage', 'N/A')
                conceal = stats.get('concealability', stats.get('conceal', 'N/A'))
                mode = stats.get('mode', 'N/A')
                ammo = stats.get('ammunition', stats.get('ammo', 'N/A'))
                
                print(f"\n{pistol['name']}")
                print(f"  Damage: {damage}")
                print(f"  Conceal: {conceal}")
                print(f"  Mode: {mode}")
                print(f"  Ammo: {ammo}")
                print(f"  Cost: {pistol['cost']}¥")
            
            # Get sniper rifles
            cur.execute("""
                SELECT name, subcategory, base_stats, cost, availability
                FROM gear
                WHERE category = 'weapon' 
                AND (subcategory = 'sniper_rifle' OR subcategory LIKE '%sniper%')
                ORDER BY name
                LIMIT 10
            """)
            
            sniper_rifles = cur.fetchall()
            
            print("\n\n🎯 SNIPER RIFLES:")
            print("-" * 80)
            for rifle in sniper_rifles:
                stats = rifle['base_stats']
                damage = stats.get('damage', 'N/A')
                conceal = stats.get('concealability', stats.get('conceal', 'N/A'))
                mode = stats.get('mode', 'N/A')
                ammo = stats.get('ammunition', stats.get('ammo', 'N/A'))
                
                print(f"\n{rifle['name']}")
                print(f"  Damage: {damage}")
                print(f"  Conceal: {conceal}")
                print(f"  Mode: {mode}")
                print(f"  Ammo: {ammo}")
                print(f"  Cost: {rifle['cost']}¥")
            
            # Summary
            print("\n\n" + "=" * 80)
            print("VERDICT:")
            print("=" * 80)
            print("""
🎯 SNIPER RIFLES WIN for pure damage output:
   - Higher damage codes (typically 10S-12S vs 9M-10M)
   - Serious (S) wounds are more severe than Moderate (M)
   - Better range and accuracy
   
📍 HEAVY PISTOLS WIN for versatility:
   - Better concealability (3-4 vs 6-8)
   - Faster rate of fire (SA/BF vs SS/SA)
   - More practical for urban combat
   - Lower cost
   
RECOMMENDATION:
   - Street Samurai / Close Combat: Heavy Pistol
   - Sniper / Overwatch Role: Sniper Rifle
   - Maximum Damage: Sniper Rifle
   - Concealment & Versatility: Heavy Pistol
            """)
            print("=" * 80)
            
    finally:
        conn.close()

if __name__ == '__main__':
    compare_weapons()
