#!/usr/bin/env python3
"""
Test Platinum's shot at a rat in complete darkness with Smartlink 3
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.combat_modifiers import CombatModifiers
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("PLATINUM'S SHOT CALCULATION")
print("=" * 70)
print("\nScenario:")
print("  Character: Platinum (Kent Jefferies)")
print("  Weapon: Morrissey Alta (heavy pistol)")
print("  Target: Rat (small)")
print("  Range: 55 meters")
print("  Visibility: Complete darkness (sewer)")
print()

# Initialize combat modifiers
cm = CombatModifiers()

# Calculate the shot
result = cm.calculate_ranged_tn({
    "character_name": "Platinum",
    "weapon_name": "Morrissey Alta",
    "range_meters": 55,
    "visibility": "complete_darkness",
    "target_size": "small"
})

# Debug: print the raw result
print("DEBUG - Raw result:")
import json
print(json.dumps(result, indent=2, default=str))
print()

if result.get('error'):
    print(f"ERROR: {result['error']}")
    sys.exit(1)

print("CALCULATION BREAKDOWN:")
print("-" * 70)
print(f"Base Target Number: {result.get('baseTN', 'N/A')}")
print(f"\nModifiers Applied:")

if result.get('modifiers'):
    for mod in result['modifiers']:
        sign = '+' if mod.get('value', 0) > 0 else ''
        print(f"  {mod.get('source', 'Unknown'):.<50} {sign}{mod.get('value', 0)}")
else:
    print(f"  {result.get('summary', 'No modifiers')}")

print(f"\n{'FINAL TARGET NUMBER':.<50} {result.get('finalTN', 'N/A')}")
print("=" * 70)

print(f"\nSmartlink 3 Active:")
print(f"  Base Smartlink 2: -2 TN")
print(f"  Project AEGIS Enhancement: -1 TN")
print(f"  Total Smartlink Bonus: -3 TN")
print(f"  Special Abilities:")
print(f"    - Grenade launcher bonus")
print(f"    - No magnification penalty")
print(f"    - Called shot assistance")

print("\n" + "=" * 70)
print("ANSWER")
print("=" * 70)
print(f"Target Number: {result.get('finalTN', 'N/A')}")
print()
print("Note: This is just the base TN. The combat_modifiers library")
print("is not finding character-specific modifiers (smartlink, skills, etc.)")
print("The actual TN would be lower with Platinum's Smartlink 3 (-3 TN),")
print("visibility modifiers (+8 for complete darkness), range modifiers,")
print("and target size modifiers (+2 for small target).")
print("=" * 70)
