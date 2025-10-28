#!/usr/bin/env python3
"""Test all characters' data from API"""
import requests
import json

# Get list of all characters
r = requests.get('http://localhost:8001/api/characters')
characters = r.json().get('characters', [])

print(f"Testing {len(characters)} characters:\n")
print("=" * 80)

for char in characters:
    char_name = char['name']
    print(f"\n{char_name}")
    print("-" * 80)
    
    # Get full character data
    r = requests.get(f'http://localhost:8001/api/character/{char_name}')
    
    if r.status_code != 200:
        print(f"  ❌ ERROR: {r.status_code}")
        continue
    
    data = r.json()
    
    # Check key fields
    print(f"  Name: {data.get('name')}")
    print(f"  Street Name: {data.get('street_name')}")
    print(f"  Archetype: {data.get('archetype')}")
    
    # Attributes
    attrs = data.get('attributes', {})
    print(f"\n  Attributes:")
    print(f"    Body: {attrs.get('body')} (base: {attrs.get('body_base')})")
    print(f"    Quickness: {attrs.get('quickness')} (base: {attrs.get('quickness_base')})")
    print(f"    Intelligence: {attrs.get('intelligence')} (base: {attrs.get('intelligence_base')})")
    print(f"    Essence: {attrs.get('essence')} (base: {attrs.get('essence_base')})")
    
    # Pools
    print(f"\n  Pools:")
    print(f"    Combat Pool: {data.get('combat_pool')}")
    print(f"    Karma Pool: {data.get('karma_pool')}")
    
    # Cyberware
    cyberware = data.get('cyberware', [])
    if cyberware:
        print(f"\n  Cyberware ({len(cyberware)} items):")
        for item in cyberware[:3]:  # Show first 3
            print(f"    - {item['name']} ({item['essence_cost']} Essence)")
            if item.get('effects'):
                for effect in item['effects'][:2]:  # Show first 2 effects
                    print(f"      • {effect}")
    
    # Bioware
    bioware = data.get('bioware', [])
    if bioware:
        print(f"\n  Bioware ({len(bioware)} items):")
        for item in bioware[:3]:  # Show first 3
            print(f"    - {item['name']} ({item.get('body_index_cost', 0)} BI)")
            if item.get('effects'):
                for effect in item['effects'][:2]:  # Show first 2 effects
                    print(f"      • {effect}")
    
    # Skills
    skills = data.get('skills', {})
    active_skills = skills.get('active', [])
    if active_skills:
        print(f"\n  Active Skills ({len(active_skills)} total):")
        for skill in active_skills[:5]:  # Show first 5
            rating = skill.get('current_rating', skill.get('base_rating', 0))
            spec = f" ({skill['specialization']})" if skill.get('specialization') else ""
            print(f"    - {skill['skill_name']}: {rating}{spec}")
    
    # Vehicles
    vehicles = data.get('vehicles', [])
    if vehicles:
        print(f"\n  Vehicles ({len(vehicles)} total):")
        for v in vehicles:
            print(f"    - {v.get('name')}")
            print(f"      Type: {v.get('vehicle_type')}, Handling: {v.get('handling')}, Speed: {v.get('speed')}")
            print(f"      Body: {v.get('body')}, Armor: {v.get('armor')}")
            if v.get('signature'):
                print(f"      Signature: {v.get('signature')}")
            if v.get('pilot'):
                print(f"      Pilot: {v.get('pilot')}")
            if v.get('modifications'):
                print(f"      Modifications: {v.get('modifications')}")
    
    # Weapons
    weapons = data.get('weapons', [])
    if weapons:
        print(f"\n  Weapons ({len(weapons)} total):")
        for w in weapons[:3]:  # Show first 3
            print(f"    - {w.get('name')}")
    
    print()

print("=" * 80)
print("\n✓ Test complete")
