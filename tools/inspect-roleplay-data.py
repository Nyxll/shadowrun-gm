#!/usr/bin/env python3
"""Inspect roleplay training data structure"""
import json

# Load training examples
with open('parsed-roleplay-data/training-examples.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Data type: {type(data)}")
print(f"Total items: {len(data)}")

if isinstance(data, dict):
    print(f"Top-level keys: {list(data.keys())}")
    print()
    
    # Check if it's organized by category
    for key, value in data.items():
        print(f"{key}:")
        print(f"  Type: {type(value)}")
        if isinstance(value, list):
            print(f"  Count: {len(value)}")
            if value:
                print(f"  First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else type(value[0])}")
                print(f"  Sample: {str(value[0])[:200]}...")
        elif isinstance(value, dict):
            print(f"  Keys: {list(value.keys())[:5]}")
        print()
elif isinstance(data, list):
    print(f"List of {len(data)} items")
    if data:
        print(f"First item type: {type(data[0])}")
        if isinstance(data[0], dict):
            print(f"First item keys: {list(data[0].keys())}")
