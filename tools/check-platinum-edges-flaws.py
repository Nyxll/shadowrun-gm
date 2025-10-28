#!/usr/bin/env python3
"""Check Platinum's edges and flaws"""
import requests
import json

r = requests.get('http://localhost:8001/api/character/Platinum')
data = r.json()

print('EDGES:')
for e in data.get('edges', []):
    print(f"  - {e['name']}: {e['description']}")

print('\nFLAWS:')
for f in data.get('flaws', []):
    print(f"  - {f['name']}: {f['description']}")
