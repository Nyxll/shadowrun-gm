#!/usr/bin/env python3
"""Test the actual API endpoint that the UI calls"""
import requests
import json

# Test the HTTP endpoint
response = requests.get('http://localhost:8001/api/character/Platinum')

if response.status_code == 200:
    data = response.json()
    
    cyberware = data.get('cyberware', [])
    bioware = data.get('bioware', [])
    
    print(f"Cyberware items: {len(cyberware)}")
    print(f"Bioware items: {len(bioware)}")
    
    print("\nCyberware:")
    for item in cyberware:
        print(f"  • {item['name']}")
        print(f"    Effects: {item.get('effects', [])}")
    
    print("\nBioware:")
    for item in bioware:
        print(f"  • {item['name']}")
        print(f"    Effects: {item.get('effects', [])}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
