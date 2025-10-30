#!/usr/bin/env python3
"""
Fix missing essence_cost and body_index_cost by copying from modifier_data JSONB to proper columns
"""
import os
from dotenv import load_dotenv
import psycopg2

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
    
    print("=" * 80)
    print("FIXING CYBERWARE ESSENCE COSTS")
    print("=" * 80)
    
    # Fix cyberware: copy essence_cost from modifier_data to essence_cost column
    cur.execute("""
        UPDATE character_modifiers
        SET essence_cost = (modifier_data->>'essence_cost')::decimal(3,2)
        WHERE source_type = 'cyberware'
        AND essence_cost IS NULL
        AND modifier_data->>'essence_cost' IS NOT NULL
        AND deleted_at IS NULL
        RETURNING id, source, (modifier_data->>'essence_cost')::decimal(3,2) as cost
    """)
    
    updated_cyber = cur.fetchall()
    print(f"\nUpdated {len(updated_cyber)} cyberware rows:")
    for row_id, source, cost in updated_cyber:
        print(f"  {source}: {cost}")
    
    print("\n" + "=" * 80)
    print("FIXING BIOWARE BODY INDEX COSTS")
    print("=" * 80)
    
    # Bioware costs stay in modifier_data, but let's verify they're there
    cur.execute("""
        SELECT id, source, modifier_data->>'body_index_cost' as cost
        FROM character_modifiers
        WHERE source_type = 'bioware'
        AND modifier_data->>'body_index_cost' IS NOT NULL
        AND deleted_at IS NULL
        ORDER BY source
    """)
    
    bioware_with_costs = cur.fetchall()
    print(f"\nFound {len(bioware_with_costs)} bioware rows with costs in modifier_data:")
    for row_id, source, cost in bioware_with_costs:
        print(f"  {source}: {cost}")
    
    conn.commit()
    print("\n" + "=" * 80)
    print("COMMIT SUCCESSFUL")
    print("=" * 80)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
