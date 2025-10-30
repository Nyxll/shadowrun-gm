#!/usr/bin/env python3
"""
Check full API response for Platinum to see what data is available
"""
import requests
import json

print("="*80)
print("PLATINUM FULL API RESPONSE CHECK")
print("="*80)

response = requests.get('http://localhost:8001/api/character/Platinum')
data = response.json()

# Extract the actual character data
char_data = data.get('data', {})

print(f"\n1. TOP-LEVEL FIELDS:")
print(f"   Character: {data.get('character')}")
print(f"   Summary: {data.get('summary')}")

print(f"\n2. CHARACTER DATA KEYS:")
for key in sorted(char_data.keys()):
    value = char_data[key]
    if isinstance(value, (list, dict)):
        print(f"   {key}: {type(value).__name__} (length: {len(value)})")
    else:
        print(f"   {key}: {value}")

print(f"\n3. CHECKING SPECIFIC SECTIONS:")

# Skills
print(f"\n   SKILLS:")
if 'skills' in char_data:
    skills = char_data['skills']
    print(f"   - Found {len(skills)} skills")
    if skills:
        print(f"   - First skill: {json.dumps(skills[0], indent=6)}")
else:
    print(f"   - NO SKILLS FIELD")

# Gear
print(f"\n   GEAR:")
if 'gear' in char_data:
    gear = char_data['gear']
    print(f"   - Found {len(gear)} gear items")
    if gear:
        print(f"   - First gear: {json.dumps(gear[0], indent=6)}")
else:
    print(f"   - NO GEAR FIELD")

# Cyberware
print(f"\n   CYBERWARE:")
if 'cyberware' in char_data:
    cyberware = char_data['cyberware']
    print(f"   - Found {len(cyberware)} cyberware items")
    if cyberware:
        print(f"   - First cyberware: {json.dumps(cyberware[0], indent=6)}")
else:
    print(f"   - NO CYBERWARE FIELD")

# Bioware
print(f"\n   BIOWARE:")
if 'bioware' in char_data:
    bioware = char_data['bioware']
    print(f"   - Found {len(bioware)} bioware items")
    if bioware:
        print(f"   - First bioware: {json.dumps(bioware[0], indent=6)}")
else:
    print(f"   - NO BIOWARE FIELD")

# Spells
print(f"\n   SPELLS:")
if 'spells' in char_data:
    spells = char_data['spells']
    print(f"   - Found {len(spells)} spells")
    if spells:
        print(f"   - First spell: {json.dumps(spells[0], indent=6)}")
else:
    print(f"   - NO SPELLS FIELD")

# Contacts
print(f"\n   CONTACTS:")
if 'contacts' in char_data:
    contacts = char_data['contacts']
    print(f"   - Found {len(contacts)} contacts")
    if contacts:
        print(f"   - First contact: {json.dumps(contacts[0], indent=6)}")
else:
    print(f"   - NO CONTACTS FIELD")

# Vehicles
print(f"\n   VEHICLES:")
if 'vehicles' in char_data:
    vehicles = char_data['vehicles']
    print(f"   - Found {len(vehicles)} vehicles")
    if vehicles:
        print(f"   - First vehicle: {json.dumps(vehicles[0], indent=6)}")
else:
    print(f"   - NO VEHICLES FIELD")

print("\n" + "="*80)
print("CONCLUSION:")
print("="*80)
missing = []
if 'skills' not in char_data or not char_data['skills']:
    missing.append('skills')
if 'gear' not in char_data or not char_data['gear']:
    missing.append('gear')
if 'cyberware' not in char_data or not char_data['cyberware']:
    missing.append('cyberware')
if 'bioware' not in char_data or not char_data['bioware']:
    missing.append('bioware')

if missing:
    print(f"MISSING OR EMPTY: {', '.join(missing)}")
else:
    print("ALL EXPECTED FIELDS PRESENT")

print("\n" + "="*80)
