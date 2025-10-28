#!/usr/bin/env python3
"""Check API response structure"""
import requests
import json

response = requests.get('http://localhost:8001/api/character/Oak')
data = response.json()

print("=== API Response Structure ===\n")
print(f"Top-level keys: {list(data.keys())}\n")

if 'skills' in data:
    print(f"Skills count: {len(data['skills'])}")
    if data['skills']:
        print(f"First skill: {json.dumps(data['skills'][0], indent=2)}\n")

if 'gear' in data:
    print(f"Gear count: {len(data['gear'])}")
    if data['gear']:
        print(f"First gear: {json.dumps(data['gear'][0], indent=2)}\n")

if 'cyberware' in data:
    print(f"Cyberware count: {len(data.get('cyberware', []))}")
if 'bioware' in data:
    print(f"Bioware count: {len(data.get('bioware', []))}")

print("\n=== Full Response (first 50 lines) ===")
print(json.dumps(data, indent=2)[:2000])
