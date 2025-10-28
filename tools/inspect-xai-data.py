#!/usr/bin/env python3
"""Quick script to inspect xAI data structure"""
import json

# Load data
with open('parsed-xai-data/xai-parsed-all.json', 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

print("Top level keys:", list(data.keys()))
print()

# Check structure
if 'byType' in data:
    print("Type counts:")
    for type_name, count in data['byType'].items():
        print(f"  {type_name}: {count}")
    print()

# Check items array
if 'items' in data:
    items = data['items']
    print(f"Total items: {len(items)}")
    print(f"Items type: {type(items)}")
    
    if items:
        print(f"\nFirst item:")
        print(f"  Type: {type(items[0])}")
        if isinstance(items[0], dict):
            print(f"  Keys: {list(items[0].keys())}")
            print(f"  Content type: {items[0].get('type')}")
            print(f"  UUID: {items[0].get('uuid', 'N/A')[:8]}...")
            
        # Find a campaign_data item
        campaign = next((item for item in items if item.get('type') == 'campaign_data'), None)
        if campaign:
            print(f"\nSample campaign_data item:")
            print(f"  Keys: {list(campaign.keys())}")
            print(f"  Content preview: {str(campaign.get('content', ''))[:200]}")
        
        # Find a session_log item
        session = next((item for item in items if item.get('type') == 'session_log'), None)
        if session:
            print(f"\nSample session_log item:")
            print(f"  Keys: {list(session.keys())}")
            print(f"  Content preview: {str(session.get('content', ''))[:200]}")
