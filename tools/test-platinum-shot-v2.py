#!/usr/bin/env python3
"""
Test Platinum shooting at rat using new v2 schema
"""
import os
import sys
import asyncio
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.combat_modifiers import CombatModifiers

load_dotenv()

# Simplified MCP client for testing
class TestMCPClient:
    def __init__(self):
        self.db_config = {
            'host': os.getenv('POSTGRES_HOST'),
            'port': os.getenv('POSTGRES_PORT'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'dbname': os.getenv('POSTGRES_DB')
        }
    
    def get_connection(self):
        return psycopg.connect(**self.db_config, row_factory=dict_row)
    
    async def calculate_ranged_attack(self, character_name, weapon_name, target_distance, 
                                     target_description, environment, combat_pool=0):
        """Calculate ranged attack - simplified version for testing"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get character
            cursor.execute("""
                SELECT id, name, street_name
                FROM characters
                WHERE LOWER(name) = LOWER(%s) OR LOWER(COALESCE(street_name, '')) = LOWER(%s)
            """, (character_name, character_name))
            
            character = cursor.fetchone()
            if not character:
                return {"error": f"Character '{character_name}' not found"}
            
            char_id = character['id']
            
            # Get cyberware for vision
            cursor.execute("""
                SELECT gear_name, modifications, notes
                FROM character_gear
                WHERE character_id = %s 
                  AND gear_type = 'cyberware'
                  AND (LOWER(gear_name) LIKE '%%cybereye%%' OR LOWER(gear_name) LIKE '%%smartlink%%')
            """, (char_id,))
            
            cyberware = cursor.fetchall()
            
            # Parse vision enhancements
            vision_enhancements = {}
            smartlink_rating = 0
            
            for item in cyberware:
                full_text = (item["gear_name"] + " " + (item["notes"] or "")).lower()
                
                if "thermographic" in full_text:
                    vision_enhancements["thermographic"] = True
                if "low-light" in full_text or "lowlight" in full_text:
                    vision_enhancements["lowLight"] = True
                if "optical magnification" in full_text:
                    import re
                    mag_match = re.search(r'magnification\s+(\d+)', full_text)
                    if mag_match:
                        vision_enhancements["magnification"] = int(mag_match.group(1))
                
                if "smartlink" in full_text:
                    import re
                    rating_match = re.search(r'smartlink\s+(\d+)', full_text)
                    if rating_match:
                        smartlink_rating = int(rating_match.group(1))
                    else:
                        smartlink_rating = 1
                    
                    if "aegis" in full_text or "project aegis" in full_text:
                        smartlink_rating += 1
            
            # Determine weapon type
            weapon_type = "hold-out pistol" if "alta" in weapon_name.lower() else "heavy pistol"
            weapon_has_smartlink = True  # Alta has smartlink
            
            # Apply magnification to range
            mag = vision_enhancements.get("magnification", 1)
            effective_distance = target_distance // mag if mag > 1 else target_distance
            
            # Determine range category with magnification
            range_cat = CombatModifiers.determine_range(target_distance, weapon_type, mag)
            
            if not range_cat:
                return {"error": "Target out of range"}
            
            # Parse environment
            light_level = "DARK" if "dark" in environment.lower() else "NORMAL"
            
            # Target modifier
            target_modifier = 2 if "rat" in target_description.lower() else 0
            
            # Build combat parameters
            params = {
                'weapon': {'smartlink': weapon_has_smartlink, 'recoilComp': 0, 'gyroStabilization': 0},
                'range': range_cat,
                'attacker': {'movement': None, 'hasSmartlink': smartlink_rating > 0, 'vision': vision_enhancements},
                'defender': {'conscious': True, 'prone': False, 'movement': None, 'inMeleeCombat': False},
                'situation': {
                    'lightLevel': light_level,
                    'dualWielding': False,
                    'recoil': 0,
                    'calledShot': False,
                    'modifier': target_modifier,
                    'modifierReason': f"Target: {target_description}"
                }
            }
            
            # Calculate TN
            result = CombatModifiers.calculate_ranged_tn(params)
            
            # Apply smartlink bonus
            smartlink_bonus = 0
            if smartlink_rating > 0 and weapon_has_smartlink:
                smartlink_bonus = -(2 + (smartlink_rating - 1))
            
            final_tn = max(2, result['finalTN'] + smartlink_bonus)
            
            return {
                "character": character_name,
                "weapon": weapon_name,
                "weapon_type": weapon_type,
                "target_distance": target_distance,
                "effective_distance": effective_distance,
                "vision_magnification": mag,
                "range_category": range_cat,
                "environment": environment,
                "light_level": light_level,
                "target_description": target_description,
                "vision_enhancements": vision_enhancements,
                "smartlink_rating": smartlink_rating,
                "base_tn": result['baseTN'],
                "modifiers": result['modifiers'],
                "smartlink_bonus": smartlink_bonus,
                "total_modifier": result['totalModifier'] + smartlink_bonus,
                "final_tn": final_tn,
                "breakdown": result['summary']
            }
        
        finally:
            cursor.close()
            conn.close()

async def test_platinum_shot():
    """Test Platinum shooting at a rat 55 meters away in complete darkness"""
    
    client = TestMCPClient()
    
    print("=" * 70)
    print("TESTING: Platinum shoots at rat 55m away in complete darkness")
    print("=" * 70)
    print()
    
    # Test the calculate_ranged_attack method
    result = await client.calculate_ranged_attack(
        character_name='Platinum',
        weapon_name='Alta',
        target_distance=55,
        target_description='rat',
        environment='complete darkness',
        combat_pool=0  # Just calculate, don't roll
    )
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    print(f"Character: {result['character']}")
    print(f"Weapon: {result['weapon']} ({result['weapon_type']})")
    print()
    print(f"Distance: {result['target_distance']}m")
    print(f"Vision Magnification: {result['vision_magnification']}x")
    print(f"Effective Distance: {result['effective_distance']}m")
    print(f"Range Category: {result['range_category']}")
    print()
    print(f"Environment: {result['environment']}")
    print(f"Light Level: {result['light_level']}")
    print(f"Target: {result['target_description']}")
    print()
    print(f"Vision Enhancements: {result['vision_enhancements']}")
    print(f"Smartlink Rating: {result['smartlink_rating']}")
    print()
    print(f"Base TN: {result['base_tn']}")
    print(f"Smartlink Bonus: {result['smartlink_bonus']}")
    print(f"Total Modifier: {result['total_modifier']}")
    print(f"Final TN: {result['final_tn']}")
    print()
    print("Modifiers Breakdown:")
    for mod in result['modifiers']:
        print(f"  {mod['type']}: {mod['value']:+d}" + 
              (f" ({mod['explanation']})" if mod.get('explanation') else ""))
    print()
    print("=" * 70)
    print()
    
    # Expected results:
    print("EXPECTED RESULTS:")
    print("- Distance: 55m")
    print("- Optical Mag 3: 55m / 3 = 18.3m effective")
    print("- Range for hold-out pistol at 18m: short (≤15m is short, but close)")
    print("- Base TN for short range: 4")
    print("- Complete darkness: +4")
    print("- Small target (rat): +2")
    print("- Smartlink 3 (2 base + 1 Aegis): -4")
    print("- Total: 4 + 4 + 2 - 4 = 6")
    print()
    
    if result['final_tn'] == 6:
        print("✅ TEST PASSED! Final TN is 6 as expected")
    else:
        print(f"❌ TEST FAILED! Expected TN 6, got {result['final_tn']}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_platinum_shot())
