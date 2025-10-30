#!/usr/bin/env python3
"""
Test API response for all characters
"""
import requests
import json

BASE_URL = "http://localhost:8001"

# All characters to test
characters = ["Platinum", "Manticore", "Block", "Axel", "Oak"]

print("="*80)
print("TESTING ALL CHARACTERS API RESPONSES")
print("="*80)

for char_name in characters:
    print(f"\n{'='*80}")
    print(f"CHARACTER: {char_name}")
    print(f"{'='*80}")
    
    try:
        response = requests.get(f"{BASE_URL}/api/character/{char_name}")
        
        if response.status_code != 200:
            print(f"❌ ERROR: Status {response.status_code}")
            print(response.text)
            continue
        
        data = response.json()
        
        if 'error' in data:
            print(f"❌ ERROR: {data['error']}")
            continue
        
        char_data = data.get('data', {})
        
        # Check key fields
        print(f"\n✓ Name: {char_data.get('name')} ({char_data.get('street_name')})")
        print(f"✓ Archetype: {char_data.get('archetype')}")
        print(f"✓ Metatype: {char_data.get('metatype')}")
        
        # Check data completeness
        cyberware = char_data.get('cyberware', [])
        bioware = char_data.get('bioware', [])
        skills = char_data.get('skills', [])
        spells = char_data.get('spells', [])
        gear = char_data.get('gear', [])
        contacts = char_data.get('contacts', [])
        vehicles = char_data.get('vehicles', [])
        powers = char_data.get('powers', [])
        
        print(f"\n📊 DATA SUMMARY:")
        print(f"   Cyberware: {len(cyberware)} items")
        print(f"   Bioware: {len(bioware)} items")
        print(f"   Skills: {len(skills)} items")
        print(f"   Spells: {len(spells)} items")
        print(f"   Gear: {len(gear)} items")
        print(f"   Contacts: {len(contacts)} items")
        print(f"   Vehicles: {len(vehicles)} items")
        print(f"   Powers: {len(powers)} items")
        
        # Show sample cyberware if present
        if cyberware:
            print(f"\n   Sample Cyberware:")
            for item in cyberware[:3]:
                print(f"      - {item.get('source')} (essence: {item.get('modifier_data', {}).get('essence_cost', 'N/A')})")
        
        # Show sample bioware if present
        if bioware:
            print(f"\n   Sample Bioware:")
            for item in bioware[:3]:
                print(f"      - {item.get('source')} (body index: {item.get('modifier_data', {}).get('body_index_cost', 'N/A')})")
        
        # Show sample spells if present
        if spells:
            print(f"\n   Sample Spells:")
            for spell in spells[:3]:
                print(f"      - {spell.get('spell_name')} (Force {spell.get('learned_force')})")
        
        # Show sample powers if present
        if powers:
            print(f"\n   Sample Powers:")
            for power in powers[:3]:
                print(f"      - {power.get('power_name')} (Level {power.get('level')})")
        
        print(f"\n✅ {char_name} - API RESPONSE COMPLETE")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERROR: Cannot connect to server at {BASE_URL}")
        print("   Make sure the game server is running!")
        break
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("TEST COMPLETE")
print("="*80)
