#!/usr/bin/env python3
import json

data = json.load(open('tools/platinum-api-response.json'))
print(f'Weapons: {len(data.get("weapons", []))}')
print(f'Armor: {len(data.get("armor", []))}')
print(f'Equipment: {len(data.get("equipment", []))}')
print(f'Vehicles: {len(data.get("vehicles", []))}')
