#!/usr/bin/env python3
"""
Test Phase 1 MCP Operations
Tests: Character retrieval, skills, spells, gear
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from lib.mcp_operations import MCPOperations

async def test_phase1_operations():
    """Test all Phase 1 operations"""
    mcp = MCPOperations()
    
    print("=" * 80)
    print("PHASE 1 MCP OPERATIONS TEST")
    print("=" * 80)
    
    # Test character: Oak
    character_name = "Oak"
    
    try:
        # 1. Get Character
        print("\n1. GET CHARACTER")
        result = await mcp.get_character(character_name)
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
            print(f"   Character ID: {result['data']['id']}")
        
        # 2. Get Skills
        print("\n2. GET SKILLS")
        result = await mcp.get_skills(character_name)
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
            if result['skills']:
                print(f"   Sample: {result['skills'][0]['skill_name']} ({result['skills'][0]['current_rating']})")
        
        # 3. Get Specific Skill
        print("\n3. GET CHARACTER SKILL")
        result = await mcp.get_character_skill(character_name, "Sorcery")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 4. Get Spells
        print("\n4. GET SPELLS")
        result = await mcp.get_spells(character_name)
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
            if result['spells']:
                print(f"   Sample: {result['spells'][0]['spell_name']} (Force {result['spells'][0]['learned_force']})")
        
        # 5. Get Gear
        print("\n5. GET GEAR")
        result = await mcp.get_gear(character_name)
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
            if result['gear']:
                print(f"   Sample: {result['gear'][0]['gear_name']}")
        
        # 6. Get Gear by Type
        print("\n6. GET GEAR (weapons)")
        result = await mcp.get_gear(character_name, "weapon")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 7. Add Skill (test)
        print("\n7. ADD SKILL (test)")
        result = await mcp.add_skill(character_name, "Test Skill", 1, reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 8. Improve Skill (test)
        print("\n8. IMPROVE SKILL (test)")
        result = await mcp.improve_skill(character_name, "Test Skill", 2, reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 9. Add Specialization (test)
        print("\n9. ADD SPECIALIZATION (test)")
        result = await mcp.add_specialization(character_name, "Test Skill", "Testing", reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 10. Remove Skill (cleanup)
        print("\n10. REMOVE SKILL (cleanup)")
        result = await mcp.remove_skill(character_name, "Test Skill", reason="Phase 1 test cleanup")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 11. Add Spell (test)
        print("\n11. ADD SPELL (test)")
        result = await mcp.add_spell(character_name, "Test Spell", 3, spell_category="Combat", reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 12. Update Spell (test)
        print("\n12. UPDATE SPELL (test)")
        result = await mcp.update_spell(character_name, "Test Spell", learned_force=4, reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 13. Remove Spell (cleanup)
        print("\n13. REMOVE SPELL (cleanup)")
        result = await mcp.remove_spell(character_name, "Test Spell", reason="Phase 1 test cleanup")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 14. Add Gear (test)
        print("\n14. ADD GEAR (test)")
        result = await mcp.add_gear(character_name, "Test Item", "equipment", 5, reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 15. Update Gear Quantity (test)
        print("\n15. UPDATE GEAR QUANTITY (test)")
        result = await mcp.update_gear_quantity(character_name, "Test Item", 10, reason="Phase 1 test")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        # 16. Remove Gear (cleanup)
        print("\n16. REMOVE GEAR (cleanup)")
        result = await mcp.remove_gear(character_name, "Test Item", reason="Phase 1 test cleanup")
        if 'error' in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ {result['summary']}")
        
        print("\n" + "=" * 80)
        print("PHASE 1 TEST COMPLETE")
        print("=" * 80)
        
    finally:
        mcp.close()

if __name__ == "__main__":
    asyncio.run(test_phase1_operations())
