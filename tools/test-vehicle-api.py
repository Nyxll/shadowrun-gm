#!/usr/bin/env python3
"""Test vehicle API response"""
import requests

r = requests.get('http://localhost:8001/api/character/Platinum')
data = r.json()

vehicles = data.get('vehicles', [])
print(f"Found {len(vehicles)} vehicle(s) from API:\n")

for v in vehicles:
    print(f"Vehicle: {v.get('name')}")
    print(f"  Type: {v.get('vehicle_type')}")
    print(f"  Handling: {v.get('handling')}")
    print(f"  Speed: {v.get('speed')}")
    print(f"  Body: {v.get('body')}")
    print(f"  Armor: {v.get('armor')}")
    print()
