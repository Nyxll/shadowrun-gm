#!/usr/bin/env python3
"""
Check essence and bio index fields in API response
"""
import requests
import json

# Get Platinum character data
response = requests.get('http://localhost:8001/api/character/Platinum')
data = response.json()['data']

print("=" * 80)
print("ESSENCE AND BIO INDEX FIELDS CHECK")
print("=" * 80)

print("\n1. ESSENCE FIELDS:")
print(f"   base_essence: {data.get('base_essence')}")
print(f"   current_essence: {data.get('current_essence')}")
print(f"   essence: {data.get('essence')}")

print("\n2. BIO INDEX FIELDS:")
print(f"   base_body_index: {data.get('base_body_index')}")
print(f"   current_body_index: {data.get('current_body_index')}")
print(f"   body_index: {data.get('body_index')}")

print("\n3. ALL KEYS WITH 'essence', 'body', OR 'index':")
for key, value in sorted(data.items()):
    if 'essence' in key.lower() or ('body' in key.lower() and 'index' in key.lower()):
        print(f"   {key}: {value}")

print("\n" + "=" * 80)
