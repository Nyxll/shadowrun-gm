#!/usr/bin/env python3
"""
Test the character API endpoint to see what data is actually being returned
"""
import requests
import json

# Test Platinum's character data
print("=" * 70)
print("TESTING PLATINUM'S CHARACTER API RESPONSE")
print("=" * 70)

response = requests.get("http://localhost:8001/api/character/Platinum")

if response.status_code == 200:
    data = response.json()
    
    print("\n=== CYBERWARE ===")
    cyberware = data.get('cyberware', [])
    print(f"Number of cyberware items: {len(cyberware)}")
    for item in cyberware:
        print(f"\n{item['name']} ({item['essence_cost']} ESS)")
        effects = item.get('effects', [])
        if effects:
            for effect in effects:
                print(f"  • {effect}")
        else:
            print("  (no effects)")
    
    print("\n=== BIOWARE ===")
    bioware = data.get('bioware', [])
    print(f"Number of bioware items: {len(bioware)}")
    for item in bioware:
        print(f"\n{item['name']} ({item['body_index_cost']} B.I.)")
        effects = item.get('effects', [])
        if effects:
            for effect in effects:
                print(f"  • {effect}")
        else:
            print("  (no effects)")
    
    # Save full response for inspection
    with open('tools/platinum-api-response.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\n\nFull response saved to tools/platinum-api-response.json")
    
else:
    print(f"Error: {response.status_code}")
    print(response.text)

print("\n" + "=" * 70)
print("TESTING MANTICORE'S CHARACTER API RESPONSE")
print("=" * 70)

response = requests.get("http://localhost:8001/api/character/Manticore")

if response.status_code == 200:
    data = response.json()
    
    print("\n=== CYBERWARE ===")
    cyberware = data.get('cyberware', [])
    print(f"Number of cyberware items: {len(cyberware)}")
    for item in cyberware:
        print(f"\n{item['name']} ({item['essence_cost']} ESS)")
        effects = item.get('effects', [])
        if effects:
            for effect in effects:
                print(f"  • {effect}")
        else:
            print("  (no effects)")
    
    print("\n=== BIOWARE ===")
    bioware = data.get('bioware', [])
    print(f"Number of bioware items: {len(bioware)}")
    for item in bioware:
        print(f"\n{item['name']} ({item['body_index_cost']} B.I.)")
        effects = item.get('effects', [])
        if effects:
            for effect in effects:
                print(f"  • {effect}")
        else:
            print("  (no effects)")
    
    # Save full response for inspection
    with open('tools/manticore-api-response.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\n\nFull response saved to tools/manticore-api-response.json")
    
else:
    print(f"Error: {response.status_code}")
    print(response.text)
