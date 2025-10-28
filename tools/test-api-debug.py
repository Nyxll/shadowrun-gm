#!/usr/bin/env python3
import requests
import json

response = requests.get('http://localhost:8001/api/character/Manticore')
data = response.json()

print("Cyberware from API:")
print("=" * 60)
for item in data.get('cyberware', []):
    print(f"\n{item['name']} ({item.get('essence_cost', 0)} ESS)")
    effects = item.get('effects', [])
    if effects:
        for effect in effects:
            print(f"  • {effect}")
    else:
        print("  (no effects)")
