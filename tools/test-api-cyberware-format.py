#!/usr/bin/env python3
"""Test what the API actually returns for cyberware"""
import requests
import json

# Test Manticore's cyberware
response = requests.get('http://localhost:8001/api/character/Manticore')
data = response.json()

print("MANTICORE CYBERWARE FROM API:")
print("=" * 70)

for item in data.get('cyberware', []):
    print(f"\n{item['name']} ({item['essence_cost']} ESS)")
    print(f"  Effects array: {item.get('effects', [])}")
    print(f"  Number of effects: {len(item.get('effects', []))}")
    
    if item.get('effects'):
        for effect in item['effects']:
            print(f"    - {effect}")
    else:
        print("    (NO EFFECTS)")

print("\n" + "=" * 70)
