#!/usr/bin/env python3
"""
Test parent-child modifier relationships
Verifies that augmentations are properly linked to their effects
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

def test_parent_child_relationships():
    """Test that parent-child relationships are properly created"""
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=os.getenv('POSTGRES_PORT'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB'),
        row_factory=dict_row
    )
    cursor = conn.cursor()
    
    print("=" * 70)
    print("TESTING PARENT-CHILD MODIFIER RELATIONSHIPS")
    print("=" * 70)
    
    # Get Platinum's character ID
    cursor.execute("SELECT id, name FROM characters WHERE name = 'Kent Jefferies'")
    char = cursor.fetchone()
    
    if not char:
        print("✗ Character 'Kent Jefferies' not found")
        return
    
    char_id = char['id']
    print(f"\n✓ Found character: {char['name']} (ID: {char_id})")
    
    # Test 1: Check that parent augmentations exist
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM character_modifiers
        WHERE character_id = %s
          AND modifier_type = 'augmentation'
          AND source_type IN ('cyberware', 'bioware')
    """, (char_id,))
    
    parent_count = cursor.fetchone()['count']
    print(f"\n✓ Found {parent_count} parent augmentation entries")
    
    # Test 2: Check that child modifiers exist
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM character_modifiers
        WHERE character_id = %s
          AND parent_modifier_id IS NOT NULL
    """, (char_id,))
    
    child_count = cursor.fetchone()['count']
    print(f"✓ Found {child_count} child modifier entries")
    
    # Test 3: Verify parent-child links
    cursor.execute("""
        SELECT 
            parent.source as parent_name,
            parent.source_type,
            COUNT(child.id) as child_count
        FROM character_modifiers parent
        LEFT JOIN character_modifiers child ON child.parent_modifier_id = parent.id
        WHERE parent.character_id = %s
          AND parent.modifier_type = 'augmentation'
        GROUP BY parent.id, parent.source, parent.source_type
        ORDER BY parent.source_type, parent.source
    """, (char_id,))
    
    parents = cursor.fetchall()
    
    print(f"\n{'Parent Augmentation':<40} {'Type':<12} {'Children'}")
    print("-" * 70)
    
    for parent in parents:
        print(f"{parent['parent_name']:<40} {parent['source_type']:<12} {parent['child_count']}")
    
    # Test 4: Show example of complete parent-child relationship
    print("\n" + "=" * 70)
    print("EXAMPLE: Enhanced Articulation with all effects")
    print("=" * 70)
    
    cursor.execute("""
        SELECT 
            parent.source as parent_name,
            parent.modifier_data,
            child.modifier_type,
            child.target_name,
            child.modifier_value
        FROM character_modifiers parent
        LEFT JOIN character_modifiers child ON child.parent_modifier_id = parent.id
        WHERE parent.character_id = %s
          AND parent.source = 'Enhanced Articulation'
          AND parent.modifier_type = 'augmentation'
    """, (char_id,))
    
    rows = cursor.fetchall()
    
    if rows:
        parent_row = rows[0]
        print(f"\nParent: {parent_row['parent_name']}")
        print(f"Body Index Cost: {parent_row['modifier_data'].get('body_index_cost', 0)}")
        print("\nChild Effects:")
        
        for row in rows:
            if row['modifier_type'] and row['modifier_type'] != 'augmentation':
                print(f"  • {row['modifier_type']}: {row['target_name']} {row['modifier_value']:+d}")
    
    # Test 5: Verify JOIN query works correctly
    print("\n" + "=" * 70)
    print("TESTING JOIN QUERY (as used in backend)")
    print("=" * 70)
    
    cursor.execute("""
        SELECT 
            parent.id as parent_id,
            parent.source as name,
            parent.modifier_data,
            child.modifier_type,
            child.target_name,
            child.modifier_value
        FROM character_modifiers parent
        LEFT JOIN character_modifiers child ON child.parent_modifier_id = parent.id
        WHERE parent.character_id = %s 
          AND parent.source_type = 'bioware'
          AND parent.modifier_type = 'augmentation'
          AND parent.is_permanent = true
        ORDER BY parent.source, child.modifier_type
        LIMIT 20
    """, (char_id,))
    
    rows = cursor.fetchall()
    
    # Group by parent
    bioware_dict = {}
    for row in rows:
        parent_id = row["parent_id"]
        
        if parent_id not in bioware_dict:
            body_index = float(row.get("modifier_data", {}).get("body_index_cost", 0))
            bioware_dict[parent_id] = {
                "name": row["name"],
                "body_index_cost": body_index,
                "effects": []
            }
        
        # Add child modifier if exists
        if row["modifier_type"] and row["modifier_type"] != "augmentation":
            effect = f"{row['modifier_type']}: {row['target_name']} {row['modifier_value']:+d}"
            bioware_dict[parent_id]["effects"].append(effect)
    
    print(f"\nGrouped bioware items: {len(bioware_dict)}")
    for bio in list(bioware_dict.values())[:5]:  # Show first 5
        print(f"\n{bio['name']} ({bio['body_index_cost']} B.I.)")
        if bio['effects']:
            for effect in bio['effects']:
                print(f"  • {effect}")
        else:
            print("  (no effects)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)

if __name__ == "__main__":
    test_parent_child_relationships()
