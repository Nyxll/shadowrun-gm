#!/usr/bin/env python3
"""
Check current edges and flaws in database
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def main():
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    cur = conn.cursor()
    
    # Get all edges and flaws
    cur.execute("""
        SELECT 
            c.name as character_name,
            c.street_name,
            ef.name,
            ef.type,
            ef.cost,
            ef.description
        FROM character_edges_flaws ef
        JOIN characters c ON ef.character_id = c.id
        ORDER BY ef.type, ef.name
    """)
    
    results = cur.fetchall()
    
    print("=" * 80)
    print("CURRENT EDGES & FLAWS IN DATABASE")
    print("=" * 80)
    print(f"\nTotal: {len(results)} entries\n")
    
    edges = [r for r in results if r[3] == 'edge']
    flaws = [r for r in results if r[3] == 'flaw']
    
    print(f"EDGES ({len(edges)}):")
    print("-" * 80)
    for char, street, name, type_, cost, desc in edges:
        cost_str = f"{cost:+d}" if cost is not None else "NULL"
        print(f"  {name:<30} Cost: {cost_str:>5}  ({char}/{street})")
        if desc:
            print(f"    → {desc[:70]}")
    
    print(f"\nFLAWS ({len(flaws)}):")
    print("-" * 80)
    for char, street, name, type_, cost, desc in flaws:
        cost_str = f"{cost:+d}" if cost is not None else "NULL"
        print(f"  {name:<30} Cost: {cost_str:>5}  ({char}/{street})")
        if desc:
            print(f"    → {desc[:70]}")
    
    # Check for NULL costs
    cur.execute("SELECT COUNT(*) FROM character_edges_flaws WHERE cost IS NULL")
    null_count = cur.fetchone()[0]
    
    print(f"\n{'='*80}")
    print(f"Entries with NULL cost: {null_count}")
    if null_count > 0:
        print("⚠️  These need to be populated from RAG database")
    else:
        print("✓ All entries have cost values")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
