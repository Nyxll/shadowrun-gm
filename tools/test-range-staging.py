#!/usr/bin/env python3
"""Test range staging with magnification"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.combat_modifiers import CombatModifiers

# Test case: 57m with heavy pistol and 3x magnification
distance = 57
weapon_type = 'heavy pistol'
magnification = 3

print("=== Range Staging Test ===")
print(f"Distance: {distance}m")
print(f"Weapon: {weapon_type}")
print(f"Magnification: {magnification}x")
print()

# Get weapon ranges
ranges = CombatModifiers.WEAPON_RANGES[weapon_type]
print(f"Heavy Pistol Ranges:")
print(f"  Short: ≤{ranges['short']}m")
print(f"  Medium: ≤{ranges['medium']}m")
print(f"  Long: ≤{ranges['long']}m")
print(f"  Extreme: ≤{ranges['extreme']}m")
print()

# Determine base range
if distance <= ranges['short']:
    base_range = 'short'
elif distance <= ranges['medium']:
    base_range = 'medium'
elif distance <= ranges['long']:
    base_range = 'long'
elif distance <= ranges['extreme']:
    base_range = 'extreme'
else:
    base_range = 'OUT OF RANGE'

print(f"Base Range (no magnification): {base_range.upper()}")
print()

# Test with magnification
result = CombatModifiers.determine_range(distance, weapon_type, magnification)
print(f"Final Range (with {magnification}x mag): {result.upper() if result else 'OUT OF RANGE'}")
print()

# Show staging process
print("Staging Process:")
print(f"  1. Base range at {distance}m: EXTREME")
print(f"  2. Mag 1: EXTREME → LONG")
print(f"  3. Mag 2: LONG → MEDIUM")
print(f"  4. Mag 3: MEDIUM → SHORT")
print(f"  Final: SHORT")
print()

# Calculate TN for this range
base_tn = CombatModifiers.BASE_TN_BY_RANGE.get(result, 4)
print(f"Base TN for {result.upper()} range: {base_tn}")
