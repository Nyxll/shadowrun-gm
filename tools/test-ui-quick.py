#!/usr/bin/env python3
"""
Quick UI test - just verify character sheet loads without errors
"""
import requests
import sys

def test_character_load(character_name):
    """Test loading a single character"""
    try:
        response = requests.get(f'http://localhost:8001/api/character/{character_name}')
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {character_name}: Loaded successfully")
            print(f"  - Name: {data.get('name')}")
            print(f"  - Skills: {len(data.get('skills', []))}")
            print(f"  - Gear: {len(data.get('gear', []))}")
            return True
        else:
            print(f"✗ {character_name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {character_name}: {e}")
        return False

def main():
    print("Quick UI Test - Character Loading")
    print("=" * 50)
    
    characters = ['Manticore', 'Platinum', 'Oak', 'Block', 'Axel', 'Wraith']
    
    passed = 0
    failed = 0
    
    for char in characters:
        if test_character_load(char):
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All characters load successfully!")
        sys.exit(0)
    else:
        print(f"✗ {failed} character(s) failed to load")
        sys.exit(1)

if __name__ == "__main__":
    main()
