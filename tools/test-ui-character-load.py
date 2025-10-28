#!/usr/bin/env python3
"""
Test that UI can load character data from API
"""
import requests
import json

API_BASE = "http://localhost:8001"

def test_character(name):
    """Test loading a character"""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print('='*80)
    
    try:
        response = requests.get(f"{API_BASE}/api/character/{name}")
        
        if response.status_code != 200:
            print(f"❌ ERROR: Status {response.status_code}")
            print(response.text)
            return False
        
        data = response.json()
        
        # Check key sections
        checks = {
            'Basic Info': data.get('name') and data.get('street_name'),
            'Attributes': data.get('attributes') and len(data['attributes']) > 0,
            'Skills': data.get('skills') and len(data['skills'].get('active', [])) > 0,
            'Cyberware': 'cyberware' in data,
            'Bioware': 'bioware' in data,
            'Weapons': 'weapons' in data and len(data.get('weapons', [])) > 0,
            'Vehicles': 'vehicles' in data,
            'Contacts': 'contacts' in data
        }
        
        print(f"\n✓ Status: {response.status_code} OK")
        print(f"✓ Name: {data.get('name')} ({data.get('street_name')})")
        print(f"✓ Archetype: {data.get('archetype')}")
        
        print(f"\nData Sections:")
        for section, present in checks.items():
            status = "✓" if present else "✗"
            print(f"  {status} {section}")
        
        # Show counts
        print(f"\nCounts:")
        print(f"  Cyberware: {len(data.get('cyberware', []))}")
        print(f"  Bioware: {len(data.get('bioware', []))}")
        print(f"  Active Skills: {len(data.get('skills', {}).get('active', []))}")
        print(f"  Weapons: {len(data.get('weapons', []))}")
        print(f"  Vehicles: {len(data.get('vehicles', []))}")
        print(f"  Contacts: {len(data.get('contacts', []))}")
        
        # Check for essence costs in cyberware
        if data.get('cyberware'):
            print(f"\nCyberware Essence Costs:")
            for item in data['cyberware'][:3]:  # Show first 3
                ess = item.get('essence_cost', 'MISSING')
                print(f"  - {item.get('name')}: {ess}")
        
        # Check for body index in bioware
        if data.get('bioware'):
            print(f"\nBioware Body Index:")
            for item in data['bioware'][:3]:  # Show first 3
                bi = item.get('body_index_cost', 'MISSING')
                print(f"  - {item.get('name')}: {bi}")
        
        all_present = all(checks.values())
        if all_present:
            print(f"\n✅ ALL SECTIONS PRESENT")
        else:
            print(f"\n⚠️  Some sections missing")
        
        return all_present
        
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("="*80)
    print("UI CHARACTER LOAD TEST")
    print("="*80)
    
    # Get list of characters
    try:
        response = requests.get(f"{API_BASE}/api/characters")
        if response.status_code != 200:
            print(f"❌ Failed to get character list: {response.status_code}")
            return
        
        characters = response.json().get('characters', [])
        print(f"\nFound {len(characters)} characters")
        
        # Test each character
        results = {}
        for char in characters:
            name = char.get('name')
            success = test_character(name)
            results[name] = success
        
        # Summary
        print(f"\n{'='*80}")
        print("SUMMARY")
        print('='*80)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, success in results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {name}")
        
        print(f"\nPassed: {passed}/{total}")
        
        if passed == total:
            print("\n🎉 ALL CHARACTERS LOAD SUCCESSFULLY!")
        else:
            print(f"\n⚠️  {total - passed} character(s) failed to load")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
