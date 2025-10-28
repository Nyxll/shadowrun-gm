#!/usr/bin/env python3
"""
Test API response for character data
"""
import requests
import json

# Test Platinum's data
response = requests.get('http://localhost:8001/api/character/Platinum')
data = response.json()

print("="*70)
print("CYBERWARE")
print("="*70)
for item in data.get('cyberware', []):
    print(f"{item['name']}: {item.get('essence_cost', 'MISSING')} ESS")

print("\n" + "="*70)
print("BIOWARE")
print("="*70)
for item in data.get('bioware', []):
    print(f"{item['name']}: {item.get('body_index_cost', 'MISSING')} B.I.")
