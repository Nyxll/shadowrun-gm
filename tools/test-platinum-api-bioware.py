#!/usr/bin/env python3
"""Test what the API is actually returning for Platinum's bioware"""
import requests
import json

response = requests.get('http://localhost:8001/api/character/Platinum')
data = response.json()

print("Platinum's Bioware from API:")
print("="*70)

for item in data.get('bioware', []):
    print(f"\n{item['name']} ({item['body_index_cost']} B.I.):")
    for effect in item.get('effects', []):
        print(f"  - {effect}")

print("\n" + "="*70)
print(f"Total bioware items: {len(data.get('bioware', []))}")
print(f"Total effects across all bioware: {sum(len(item.get('effects', [])) for item in data.get('bioware', []))}")
