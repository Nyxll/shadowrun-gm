#!/usr/bin/env python3
"""
Calculate target number for Platinum shooting at a rat in complete darkness
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.combat_modifiers import CombatModifiers

def main():
    print("=" * 60)
    print("COMBAT SCENARIO: Platinum vs Rat in Sewer")
    print("=" * 60)
    print()
    
    # Weapon: Morrissey Alta (hold-out pistol)
    # Distance: 55 meters
    # Conditions: Complete darkness (sewer)
    
    weapon_type = 'hold-out pistol'
    distance = 55
    
    # Determine range category
    range_cat = CombatModifiers.determine_range(distance, weapon_type)
    
    print(f"Weapon: Morrissey Alta (Hold-out Pistol)")
    print(f"Target: Rat (small target)")
    print(f"Distance: {distance} meters")
    print(f"Range Category: {range_cat if range_cat else 'OUT OF RANGE'}")
    print(f"Environment: Complete darkness (sewer)")
    print()
    
    if not range_cat:
        print("⚠️  TARGET IS OUT OF RANGE!")
        print()
        print("Morrissey Alta ranges:")
        ranges = CombatModifiers.WEAPON_RANGES[weapon_type]
        print(f"  Short: 0-{ranges['short']}m")
        print(f"  Medium: {ranges['short']+1}-{ranges['medium']}m")
        print(f"  Long: {ranges['medium']+1}-{ranges['long']}m")
        print(f"  Extreme: {ranges['long']+1}-{ranges['extreme']}m")
        print(f"  Beyond {ranges['extreme']}m: Cannot engage")
        print()
        print("The rat at 55 meters is just within extreme range!")
        range_cat = 'extreme'
    
    # Calculate target number
    params = {
        'weapon': {
            'smartlink': False,
            'recoilComp': 0,
            'gyroStabilization': 0
        },
        'range': range_cat,
        'attacker': {
            'movement': None,  # Stationary
            'hasSmartlink': False,
            'vision': {}  # No vision enhancements specified
        },
        'defender': {
            'conscious': True,
            'prone': False,
            'movement': None,  # Rat is stationary
            'inMeleeCombat': False
        },
        'situation': {
            'lightLevel': 'DARK',  # Complete darkness
            'dualWielding': False,
            'recoil': 0,  # First shot
            'calledShot': False,
            'modifier': 2,  # Small target (rat)
            'modifierReason': 'Small target (rat)'
        }
    }
    
    result = CombatModifiers.calculate_ranged_tn(params)
    
    print("=" * 60)
    print("TARGET NUMBER CALCULATION")
    print("=" * 60)
    print()
    print(f"Base TN ({range_cat} range): {result['baseTN']}")
    print()
    
    if result['modifiers']:
        print("Modifiers:")
        for mod in result['modifiers']:
            sign = '+' if mod['value'] > 0 else ''
            exp = f" ({mod['explanation']})" if mod['explanation'] else ''
            print(f"  {mod['type']}: {sign}{mod['value']}{exp}")
        print()
        print(f"Total Modifier: {result['totalModifier']:+d}")
    else:
        print("No modifiers applied")
    
    print()
    print("=" * 60)
    print(f"FINAL TARGET NUMBER: {result['finalTN']}")
    print("=" * 60)
    print()
    
    # Additional notes
    print("NOTES:")
    print("• Complete darkness adds +4 to TN")
    print("• Extreme range (55m) has base TN of 9")
    print("• Small target (rat) adds +2 to TN")
    print("• Platinum has no vision enhancements to reduce darkness penalty")
    print("• This is an extremely difficult shot!")
    print()
    
    # Success probability estimate
    print("SUCCESS PROBABILITY (rough estimate):")
    tn = result['finalTN']
    if tn <= 4:
        prob = "~83% (5+ on d6)"
    elif tn <= 5:
        prob = "~67% (4+ on d6)"
    elif tn <= 6:
        prob = "~50% (3+ on d6)"
    elif tn <= 8:
        prob = "~33% (2+ on d6, need multiple successes)"
    else:
        prob = "~17% or less (very difficult)"
    
    print(f"  With TN {tn}: {prob}")
    print()

if __name__ == "__main__":
    main()
