#!/usr/bin/env python3
"""
Test what the API actually returns
"""
import requests
import json

response = requests.get('http://localhost:8001/api/character/Platinum')
data = response.json()

print("CYBERWARE from API:")
print(json.dumps(data.get('cyberware', [])[:2], indent=2))

print("\nBIOWARE from API:")
print(json.dumps(data.get('bioware', [])[:2], indent=2))
