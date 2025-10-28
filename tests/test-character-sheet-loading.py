#!/usr/bin/env python3
"""
Test script for character sheet loading via web interface
Tests the complete workflow from character selection to sheet display
"""
import requests
import json
import sys

def test_character_sheet_api():
    """Test the character sheet API endpoint"""
    print("Testing Character Sheet API Endpoint")
    print("=" * 60)
    
    # Test 1: Get list of available characters
    print("\n1. Testing /api/characters endpoint...")
    try:
        response = requests.get("http://localhost:8001/api/characters")
        if response.status_code == 200:
            data = response.json()
            characters = data.get('characters', [])
            print(f"   ✓ SUCCESS: Found {len(characters)} characters")
            for char in characters:
                print(f"     - {char['name']} ({char['archetype']})")
        else:
            print(f"   ✗ FAILED: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False
    
    # Test 2: Load Platinum's character sheet
    print("\n2. Testing /api/character/Platinum endpoint...")
    try:
        response = requests.get("http://localhost:8001/api/character/Platinum")
        if response.status_code == 200:
            character = response.json()
            print(f"   ✓ SUCCESS: Loaded character sheet")
            print(f"     - Name: {character.get('name')}")
            print(f"     - Street Name: {character.get('street_name')}")
            print(f"     - Archetype: {character.get('archetype')}")
            
            # Verify critical sections
            print("\n3. Verifying character data sections...")
            
            # Check attributes
            if 'attributes' in character:
                attrs = character['attributes']
                print(f"   ✓ Attributes: Body={attrs.get('body')}, Quickness={attrs.get('quickness')}")
            else:
                print("   ✗ Missing attributes section")
                return False
            
            # Check skills (this was the bug!)
            if 'skills' in character:
                skills = character['skills']
                print(f"   ✓ Skills: Found {len(skills)} skills")
                if len(skills) > 0:
                    first_skill = skills[0]
                    print(f"     - Example: {first_skill.get('skill_name')} = {first_skill.get('rating')}")
            else:
                print("   ✗ Missing skills section")
                return False
            
            # Check gear
            if 'gear' in character:
                gear = character['gear']
                print(f"   ✓ Gear: Found {len(gear)} items")
            else:
                print("   ✗ Missing gear section")
                return False
            
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED")
            print("=" * 60)
            return True
            
        else:
            error_data = response.json()
            print(f"   ✗ FAILED: HTTP {response.status_code}")
            print(f"     Error: {error_data.get('detail', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ✗ ERROR: {e}")
        return False

def print_manual_test_steps():
    """Print manual testing steps for the web interface"""
    print("\n" + "=" * 60)
    print("MANUAL WEB INTERFACE TEST STEPS")
    print("=" * 60)
    print("""
1. Start the game server:
   python game-server.py

2. Open browser to: http://localhost:8001

3. Verify initial state:
   - "Loaded 6 characters from database" message appears
   - "Connected to game server" message appears
   - Status shows "Characters loaded - Ready for scenario creation"

4. Select a character:
   - Click on the "Select a character..." dropdown
   - Type "Platinum" to filter/select
   - Verify "Platinum (null)" appears in dropdown

5. Add character to session:
   - Click the "ADD CHARACTER" button
   - Verify "Added Platinum to session" message appears
   - Verify "Platinum" appears in Active Characters list with red X button

6. View character sheet:
   - Click on "Platinum" name in Active Characters list
   - Verify character sheet modal opens
   - Verify all sections display:
     * BASIC INFORMATION (Name, Street Name, Archetype, etc.)
     * ATTRIBUTES (Body, Quickness, Strength, etc.)
     * DICE POOLS (Combat Pool)
     * SKILLS (Athletics, Cars, etc.) ← THIS WAS THE BUG
     * GEAR (weapons, armor, cyberware, etc.)

7. Verify no errors:
   - Check browser console (F12) for errors
   - Check server terminal for 500 errors
   - Should see: "GET /api/character/Platinum HTTP/1.1" 200 OK

8. Close character sheet:
   - Click the red "X CLOSE" button or click outside modal
   - Verify modal closes properly
""")

if __name__ == "__main__":
    print("\nShadowrun GM - Character Sheet Loading Test")
    print("=" * 60)
    
    # Run API tests
    success = test_character_sheet_api()
    
    # Print manual test steps
    print_manual_test_steps()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
