#!/usr/bin/env python3
"""Check edges and flaws for all characters"""
import requests
import json

# Get list of characters
r = requests.get('http://localhost:8001/api/characters')
characters = r.json()['characters']

print("=" * 70)
print("EDGES AND FLAWS FOR ALL CHARACTERS")
print("=" * 70)

for char in characters:
    name = char['name']
    
    # Get character details
    r = requests.get(f'http://localhost:8001/api/character/{name}')
    data = r.json()
    
    edges = data.get('edges', [])
    flaws = data.get('flaws', [])
    
    print(f"\n{name} ({char['full_name']})")
    print("-" * 70)
    
    if edges:
        print("EDGES:")
        for e in edges:
            print(f"  - {e['name']}: {e['description']}")
    else:
        print("EDGES: None")
    
    if flaws:
        print("FLAWS:")
        for f in flaws:
            print(f"  - {f['name']}: {f['description']}")
    else:
        print("FLAWS: None")

print("\n" + "=" * 70)
