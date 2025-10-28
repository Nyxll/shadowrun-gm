#!/usr/bin/env python3
"""
Test campaign management and NPC tracking functionality
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import json

load_dotenv()

# Database connection
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

def test_campaign_creation():
    """Test creating a new campaign"""
    print("\n=== Test 1: Campaign Creation ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Create test campaign
    cursor.execute("""
        INSERT INTO campaigns (title, description, theme)
        VALUES (%s, %s, %s)
        RETURNING *
    """, [
        "Test Campaign: Shadows of Seattle",
        "A test campaign for validating the campaign management system",
        "Corporate espionage in the Seattle sprawl"
    ])
    
    campaign = cursor.fetchone()
    conn.commit()
    
    print(f"✓ Created campaign: {campaign['title']}")
    print(f"  ID: {campaign['id']}")
    print(f"  Theme: {campaign['theme']}")
    print(f"  Created: {campaign['created_at']}")
    
    cursor.close()
    return campaign['id']

def test_npc_registration(campaign_id):
    """Test registering NPCs"""
    print("\n=== Test 2: NPC Registration ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Register multiple NPCs
    npcs = [
        {
            'name': 'Guard Alpha',
            'role': 'guard',
            'location': 'Seamstress Union - Main Entrance',
            'relevance': 'current',
            'description': 'Heavily armed security guard at the main entrance',
            'stats': {'body': 5, 'quickness': 4, 'strength': 5, 'armor': '5/3'}
        },
        {
            'name': 'Guard Beta',
            'role': 'guard',
            'location': 'Seamstress Union - Main Entrance',
            'relevance': 'current',
            'description': 'Second guard at main entrance',
            'stats': {'body': 4, 'quickness': 5, 'strength': 4, 'armor': '5/3'}
        },
        {
            'name': 'Crusher',
            'role': 'bartender',
            'location': 'Seamstress Union - Bar',
            'relevance': 'background',
            'description': 'Troll bartender, knows everyone in the building',
            'notes': 'Friendly to regulars, suspicious of newcomers'
        },
        {
            'name': 'Mr. Johnson',
            'role': 'johnson',
            'location': 'Unknown',
            'relevance': 'future',
            'description': 'Mysterious fixer who hired the team',
            'notes': 'Has not been met in person yet'
        }
    ]
    
    registered = []
    for npc_data in npcs:
        cursor.execute("""
            INSERT INTO campaign_npcs (
                campaign_id, name, role, location, relevance, description, stats, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, [
            campaign_id,
            npc_data['name'],
            npc_data['role'],
            npc_data['location'],
            npc_data['relevance'],
            npc_data.get('description'),
            json.dumps(npc_data.get('stats')) if npc_data.get('stats') else None,
            npc_data.get('notes')
        ])
        
        npc = cursor.fetchone()
        registered.append(npc)
        print(f"✓ Registered NPC: {npc['name']} ({npc['role']}) - {npc['relevance']}")
    
    conn.commit()
    cursor.close()
    
    return registered

def test_npc_retrieval(campaign_id):
    """Test retrieving NPCs with filters"""
    print("\n=== Test 3: NPC Retrieval ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Test 1: Get all current NPCs
    print("\n--- Current NPCs ---")
    cursor.execute("""
        SELECT * FROM campaign_npcs
        WHERE campaign_id = %s AND relevance = 'current'
        ORDER BY name
    """, [campaign_id])
    
    current_npcs = cursor.fetchall()
    print(f"Found {len(current_npcs)} current NPCs:")
    for npc in current_npcs:
        print(f"  - {npc['name']} at {npc['location']}")
    
    # Test 2: Get NPCs by location
    print("\n--- NPCs at Main Entrance ---")
    cursor.execute("""
        SELECT * FROM campaign_npcs
        WHERE campaign_id = %s AND location LIKE %s
        ORDER BY name
    """, [campaign_id, '%Main Entrance%'])
    
    entrance_npcs = cursor.fetchall()
    print(f"Found {len(entrance_npcs)} NPCs at entrance:")
    for npc in entrance_npcs:
        print(f"  - {npc['name']} ({npc['role']})")
    
    # Test 3: Get background NPCs
    print("\n--- Background NPCs ---")
    cursor.execute("""
        SELECT * FROM campaign_npcs
        WHERE campaign_id = %s AND relevance = 'background'
        ORDER BY name
    """, [campaign_id])
    
    background_npcs = cursor.fetchall()
    print(f"Found {len(background_npcs)} background NPCs:")
    for npc in background_npcs:
        print(f"  - {npc['name']} ({npc['role']})")
    
    cursor.close()

def test_npc_updates(campaign_id):
    """Test updating NPC status and relevance"""
    print("\n=== Test 4: NPC Updates ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Update Guard Alpha - defeated
    print("\n--- Update Guard Alpha (defeated) ---")
    cursor.execute("""
        UPDATE campaign_npcs
        SET status = 'inactive',
            relevance = 'background',
            notes = COALESCE(notes, '') || E'\nDefeated in combat at main entrance'
        WHERE campaign_id = %s AND name = 'Guard Alpha'
        RETURNING *
    """, [campaign_id])
    
    updated = cursor.fetchone()
    print(f"✓ Updated {updated['name']}")
    print(f"  Status: {updated['status']}")
    print(f"  Relevance: {updated['relevance']}")
    print(f"  Notes: {updated['notes']}")
    
    # Move Guard Beta to new location
    print("\n--- Move Guard Beta ---")
    cursor.execute("""
        UPDATE campaign_npcs
        SET location = 'Seamstress Union - Garage Sublevel 2',
            notes = COALESCE(notes, '') || E'\nFell back to garage after partner defeated'
        WHERE campaign_id = %s AND name = 'Guard Beta'
        RETURNING *
    """, [campaign_id])
    
    moved = cursor.fetchone()
    print(f"✓ Moved {moved['name']}")
    print(f"  New location: {moved['location']}")
    
    # Update Crusher relevance (players entered bar)
    print("\n--- Update Crusher (now current) ---")
    cursor.execute("""
        UPDATE campaign_npcs
        SET relevance = 'current',
            notes = COALESCE(notes, '') || E'\nPlayers entered the bar'
        WHERE campaign_id = %s AND name = 'Crusher'
        RETURNING *
    """, [campaign_id])
    
    current = cursor.fetchone()
    print(f"✓ Updated {current['name']}")
    print(f"  Relevance: {current['relevance']}")
    
    conn.commit()
    cursor.close()

def test_campaign_state_updates(campaign_id):
    """Test updating campaign state"""
    print("\n=== Test 5: Campaign State Updates ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Update current situation
    print("\n--- Update Current Situation ---")
    cursor.execute("""
        UPDATE campaigns
        SET current_situation = %s,
            location = %s
        WHERE id = %s
        RETURNING *
    """, [
        "Team has infiltrated the Seamstress Union. Guards at main entrance defeated. Currently in the bar talking to Crusher.",
        "Seamstress Union - Bar",
        campaign_id
    ])
    
    campaign = cursor.fetchone()
    print(f"✓ Updated situation: {campaign['current_situation']}")
    print(f"✓ Current location: {campaign['location']}")
    
    # Add objectives
    print("\n--- Add Objectives ---")
    objectives = [
        {'objective': 'Find the stolen data chip', 'completed': False, 'order': 1},
        {'objective': 'Avoid alerting building security', 'completed': False, 'order': 2},
        {'objective': 'Extract without casualties', 'completed': False, 'order': 3}
    ]
    
    cursor.execute("""
        UPDATE campaigns
        SET objectives = %s
        WHERE id = %s
        RETURNING *
    """, [json.dumps(objectives), campaign_id])
    
    campaign = cursor.fetchone()
    print(f"✓ Added {len(campaign['objectives'])} objectives:")
    for obj in campaign['objectives']:
        status = '✓' if obj['completed'] else '○'
        print(f"  {status} {obj['objective']}")
    
    # Add complications
    print("\n--- Add Complications ---")
    complications = [
        "Building security has been alerted",
        "Backup guards en route to garage"
    ]
    
    cursor.execute("""
        UPDATE campaigns
        SET active_complications = %s
        WHERE id = %s
        RETURNING *
    """, [json.dumps(complications), campaign_id])
    
    campaign = cursor.fetchone()
    print(f"✓ Added {len(campaign['active_complications'])} complications:")
    for comp in campaign['active_complications']:
        print(f"  ! {comp}")
    
    # Complete an objective
    print("\n--- Complete Objective ---")
    updated_objectives = campaign['objectives'].copy()
    updated_objectives[1]['completed'] = True  # "Avoid alerting security" - failed
    
    cursor.execute("""
        UPDATE campaigns
        SET objectives = %s
        WHERE id = %s
        RETURNING *
    """, [json.dumps(updated_objectives), campaign_id])
    
    campaign = cursor.fetchone()
    print(f"✓ Updated objectives:")
    for obj in campaign['objectives']:
        status = '✓' if obj['completed'] else '○'
        print(f"  {status} {obj['objective']}")
    
    # Add milestone
    print("\n--- Add Milestone ---")
    milestones = ["Infiltrated Seamstress Union", "Defeated entrance guards"]
    
    cursor.execute("""
        UPDATE campaigns
        SET completed_milestones = %s
        WHERE id = %s
        RETURNING *
    """, [json.dumps(milestones), campaign_id])
    
    campaign = cursor.fetchone()
    print(f"✓ Added {len(campaign['completed_milestones'])} milestones:")
    for milestone in campaign['completed_milestones']:
        print(f"  ★ {milestone}")
    
    conn.commit()
    cursor.close()

def test_campaign_summary(campaign_id):
    """Display complete campaign summary"""
    print("\n=== Test 6: Campaign Summary ===")
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get campaign
    cursor.execute("SELECT * FROM campaigns WHERE id = %s", [campaign_id])
    campaign = cursor.fetchone()
    
    # Get NPCs grouped by relevance
    cursor.execute("""
        SELECT relevance, COUNT(*) as count
        FROM campaign_npcs
        WHERE campaign_id = %s
        GROUP BY relevance
        ORDER BY 
            CASE relevance
                WHEN 'current' THEN 1
                WHEN 'background' THEN 2
                WHEN 'future' THEN 3
            END
    """, [campaign_id])
    
    npc_counts = cursor.fetchall()
    
    print(f"\n{'='*60}")
    print(f"CAMPAIGN: {campaign['title']}")
    print(f"{'='*60}")
    print(f"Theme: {campaign['theme']}")
    print(f"Description: {campaign['description']}")
    print(f"\nCurrent Situation:")
    print(f"  {campaign['current_situation']}")
    print(f"\nLocation: {campaign['location']}")
    
    print(f"\nObjectives:")
    for obj in campaign['objectives']:
        status = '✓' if obj['completed'] else '○'
        print(f"  {status} {obj['objective']}")
    
    print(f"\nActive Complications:")
    for comp in campaign['active_complications']:
        print(f"  ! {comp}")
    
    print(f"\nCompleted Milestones:")
    for milestone in campaign['completed_milestones']:
        print(f"  ★ {milestone}")
    
    print(f"\nNPC Summary:")
    for row in npc_counts:
        print(f"  {row['relevance'].capitalize()}: {row['count']}")
    
    print(f"\n{'='*60}")
    
    cursor.close()

def cleanup_test_data(campaign_id):
    """Clean up test data"""
    print("\n=== Cleanup ===")
    
    cursor = conn.cursor()
    
    # Delete NPCs
    cursor.execute("DELETE FROM campaign_npcs WHERE campaign_id = %s", [campaign_id])
    npc_count = cursor.rowcount
    
    # Delete campaign
    cursor.execute("DELETE FROM campaigns WHERE id = %s", [campaign_id])
    
    conn.commit()
    cursor.close()
    
    print(f"✓ Deleted {npc_count} NPCs")
    print(f"✓ Deleted campaign")

def main():
    """Run all tests"""
    print("="*60)
    print("CAMPAIGN MANAGEMENT SYSTEM TESTS")
    print("="*60)
    
    try:
        # Run tests
        campaign_id = test_campaign_creation()
        test_npc_registration(campaign_id)
        test_npc_retrieval(campaign_id)
        test_npc_updates(campaign_id)
        test_campaign_state_updates(campaign_id)
        test_campaign_summary(campaign_id)
        
        # Cleanup
        cleanup_test_data(campaign_id)
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
