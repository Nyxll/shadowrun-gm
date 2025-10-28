#!/usr/bin/env python3
"""
Test Manticore's bioware display via API
"""
import requests
import json

response = requests.get('http://localhost:8001/api/character/Manticore')
data = response.json()

print("="*70)
print("MANTICORE BIOWARE FROM API")
print("="*70)

if 'bioware' in data:
    bioware_list = data['bioware']
    print(f"\nFound {len(bioware_list)} bioware items:\n")
    
    for item in bioware_list:
        print(f"  • {item['name']}")
        print(f"    Body Index: {item.get('body_index_cost', 0)}")
        
        if 'effects' in item and item['effects']:
            print(f"    Effects:")
            for effect in item['effects']:
                print(f"      - {effect}")
        else:
            print(f"    Effects: (none)")
        print()
    
    # Check specifically for Tailored Pheromones
    tailored = [b for b in bioware_list if 'Tailored' in b['name']]
    if tailored:
        print("="*70)
        print("TAILORED PHEROMONES FOUND!")
        print("="*70)
        for item in tailored:
            print(f"Name: {item['name']}")
            print(f"Effects: {item.get('effects', [])}")
            
            # Check for the specific effects we expect
            effects = item.get('effects', [])
            has_social_pool = any('Social Pool' in e for e in effects)
            has_condition = any('non-dwarves' in e for e in effects)
            
            print(f"\n✓ Has +4 Social Pool: {has_social_pool}")
            print(f"✓ Has '1/2 effect on non-dwarves': {has_condition}")
            
            if has_social_pool and has_condition:
                print("\n🎉 SUCCESS! Both modifiers are displaying!")
            else:
                print("\n❌ MISSING MODIFIERS")
    else:
        print("="*70)
        print("❌ TAILORED PHEROMONES NOT FOUND IN BIOWARE LIST")
        print("="*70)
else:
    print("No bioware data in response")
