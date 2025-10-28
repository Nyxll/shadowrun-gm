#!/usr/bin/env python3
"""
Test edge/flaw auto-cost lookup from RAG
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.comprehensive_crud import ComprehensiveCRUD

load_dotenv()

def test_edge_auto_cost():
    """Test adding an edge without cost - should auto-lookup from RAG"""
    print("\n" + "="*80)
    print("TEST: Edge Auto-Cost Lookup")
    print("="*80)
    
    crud = ComprehensiveCRUD(user_id='test-user-id')
    
    try:
        # Get Oak's character ID
        oak = crud.get_character_by_street_name('Oak')
        print(f"\n✓ Found character: {oak['name']} (ID: {oak['id']})")
        
        # Add edge WITHOUT cost - should auto-lookup
        print("\nAdding edge 'Aptitude (Sorcery)' without cost...")
        edge = crud.add_edge_flaw(
            char_id=oak['id'],
            data={
                'name': 'Aptitude (Sorcery)',
                'type': 'edge',
                'description': '-1 TN to all Sorcery tests'
            }
        )
        
        print(f"\n✓ Edge added:")
        print(f"  Name: {edge['name']}")
        print(f"  Type: {edge['type']}")
        print(f"  Cost: {edge['cost']:+d} karma")
        print(f"  Description: {edge['description']}")
        
        # Verify cost is negative (edges cost karma)
        assert edge['cost'] < 0, f"Edge cost should be negative, got {edge['cost']}"
        print(f"\n✓ Cost is negative (edge costs karma to buy)")
        
        # Clean up
        crud.conn.execute("DELETE FROM character_edges_flaws WHERE id = %s", (edge['id'],))
        crud.conn.commit()
        print(f"\n✓ Cleaned up test data")
        
    finally:
        crud.close()

def test_flaw_auto_cost():
    """Test adding a flaw without cost - should auto-lookup from RAG"""
    print("\n" + "="*80)
    print("TEST: Flaw Auto-Cost Lookup")
    print("="*80)
    
    crud = ComprehensiveCRUD(user_id='test-user-id')
    
    try:
        # Get Oak's character ID
        oak = crud.get_character_by_street_name('Oak')
        print(f"\n✓ Found character: {oak['name']} (ID: {oak['id']})")
        
        # Add flaw WITHOUT cost - should auto-lookup
        print("\nAdding flaw 'Weak Immune System' without cost...")
        flaw = crud.add_edge_flaw(
            char_id=oak['id'],
            data={
                'name': 'Weak Immune System',
                'type': 'flaw',
                'description': '-1 Body vs. diseases'
            }
        )
        
        print(f"\n✓ Flaw added:")
        print(f"  Name: {flaw['name']}")
        print(f"  Type: {flaw['type']}")
        print(f"  Cost: {flaw['cost']:+d} karma")
        print(f"  Description: {flaw['description']}")
        
        # Verify cost is positive (flaws give karma)
        assert flaw['cost'] > 0, f"Flaw cost should be positive, got {flaw['cost']}"
        print(f"\n✓ Cost is positive (flaw gives karma back)")
        
        # Clean up
        crud.conn.execute("DELETE FROM character_edges_flaws WHERE id = %s", (flaw['id'],))
        crud.conn.commit()
        print(f"\n✓ Cleaned up test data")
        
    finally:
        crud.close()

def test_manual_cost():
    """Test adding edge/flaw WITH manual cost - should use provided cost"""
    print("\n" + "="*80)
    print("TEST: Manual Cost Override")
    print("="*80)
    
    crud = ComprehensiveCRUD(user_id='test-user-id')
    
    try:
        # Get Oak's character ID
        oak = crud.get_character_by_street_name('Oak')
        print(f"\n✓ Found character: {oak['name']} (ID: {oak['id']})")
        
        # Add edge WITH manual cost
        print("\nAdding edge with manual cost of -5...")
        edge = crud.add_edge_flaw(
            char_id=oak['id'],
            data={
                'name': 'Custom Edge',
                'type': 'edge',
                'description': 'A custom edge for testing',
                'cost': -5  # Manual cost
            }
        )
        
        print(f"\n✓ Edge added:")
        print(f"  Name: {edge['name']}")
        print(f"  Cost: {edge['cost']:+d} karma (manual)")
        
        # Verify manual cost was used
        assert edge['cost'] == -5, f"Expected cost -5, got {edge['cost']}"
        print(f"\n✓ Manual cost was used (not auto-looked up)")
        
        # Clean up
        crud.conn.execute("DELETE FROM character_edges_flaws WHERE id = %s", (edge['id'],))
        crud.conn.commit()
        print(f"\n✓ Cleaned up test data")
        
    finally:
        crud.close()

def main():
    print("\n" + "="*80)
    print("EDGE/FLAW AUTO-COST TESTS")
    print("="*80)
    
    try:
        test_edge_auto_cost()
        test_flaw_auto_cost()
        test_manual_cost()
        
        print("\n" + "="*80)
        print("✓ ALL TESTS PASSED")
        print("="*80)
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
