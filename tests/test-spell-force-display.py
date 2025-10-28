#!/usr/bin/env python3
"""
Test spell force display in character sheet API
Verifies that learned_force is properly returned and displayed
"""
import os
import sys
import json
from dotenv import load_dotenv
import requests

load_dotenv()

# Test configuration
API_BASE_URL = "http://localhost:8001"
TEST_CHARACTERS = ["Simon Stalman", "Test Leviathan"]

def test_spell_force_in_api():
    """Test that spell force is included in API response"""
    print("Testing Spell Force in API Response")
    print("=" * 80)
    
    all_passed = True
    
    for char_name in TEST_CHARACTERS:
        print(f"\nTesting character: {char_name}")
        print("-" * 80)
        
        try:
            # Get character data from API
            response = requests.get(f"{API_BASE_URL}/api/character/{char_name}")
            
            if response.status_code != 200:
                print(f"  [FAIL] API request failed: {response.status_code}")
                all_passed = False
                continue
            
            data = response.json()
            spells = data.get('spells', [])
            
            if not spells:
                print(f"  ⚠ No spells found for {char_name}")
                continue
            
            print(f"  Found {len(spells)} spells")
            
            # Check each spell
            spells_with_force = 0
            spells_without_force = 0
            
            for spell in spells:
                spell_name = spell.get('spell_name')
                learned_force = spell.get('learned_force')
                spell_category = spell.get('spell_category')
                
                if learned_force:
                    print(f"    [PASS] {spell_name:30} Force {learned_force} ({spell_category})")
                    spells_with_force += 1
                else:
                    print(f"    [FAIL] {spell_name:30} NO FORCE ({spell_category})")
                    spells_without_force += 1
                    all_passed = False
            
            print(f"\n  Summary for {char_name}:")
            print(f"    Spells with force: {spells_with_force}")
            print(f"    Spells without force: {spells_without_force}")
            
            if spells_without_force > 0:
                print(f"    [FAIL] FAILED: {spells_without_force} spells missing force values")
                all_passed = False
            else:
                print(f"    [PASS] PASSED: All spells have force values")
        
        except Exception as e:
            print(f"  [FAIL] Error testing {char_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
        return 0
    else:
        print("[FAIL] SOME TESTS FAILED")
        return 1

def test_spell_force_data_structure():
    """Test that spell data structure includes all required fields"""
    print("\n\nTesting Spell Data Structure")
    print("=" * 80)
    
    char_name = TEST_CHARACTERS[0]
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/character/{char_name}")
        data = response.json()
        spells = data.get('spells', [])
        
        if not spells:
            print(f"[FAIL] No spells found for {char_name}")
            return 1
        
        # Check first spell for all required fields
        spell = spells[0]
        required_fields = [
            'spell_name',
            'spell_category',
            'spell_type',
            'target_type',
            'duration',
            'drain_modifier',
            'learned_force',  # NEW FIELD
            'description',
            'notes'
        ]
        
        print(f"Checking spell: {spell.get('spell_name')}")
        print("-" * 80)
        
        all_present = True
        for field in required_fields:
            value = spell.get(field)
            status = "[PASS]" if field in spell else "[FAIL]"
            
            # Special handling for learned_force - it's the critical new field
            if field == 'learned_force':
                if value:
                    print(f"  {status} {field:20} = {value} (CRITICAL)")
                else:
                    print(f"  [FAIL] {field:20} = MISSING (CRITICAL)")
                    all_present = False
            else:
                print(f"  {status} {field:20} = {value if value else 'null'}")
        
        print("\n" + "-" * 80)
        if all_present:
            print("[PASS] All required fields present")
            return 0
        else:
            print("[FAIL] Some required fields missing")
            return 1
    
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return 1

def test_spell_force_values():
    """Test that spell force values are reasonable"""
    print("\n\nTesting Spell Force Value Ranges")
    print("=" * 80)
    
    all_valid = True
    
    for char_name in TEST_CHARACTERS:
        try:
            response = requests.get(f"{API_BASE_URL}/api/character/{char_name}")
            data = response.json()
            spells = data.get('spells', [])
            
            print(f"\n{char_name}:")
            print("-" * 80)
            
            for spell in spells:
                spell_name = spell.get('spell_name')
                force = spell.get('learned_force')
                
                if not force:
                    print(f"  [FAIL] {spell_name}: No force value")
                    all_valid = False
                elif force < 1 or force > 12:
                    print(f"  [FAIL] {spell_name}: Invalid force {force} (must be 1-12)")
                    all_valid = False
                else:
                    print(f"  [PASS] {spell_name}: Force {force} (valid)")
        
        except Exception as e:
            print(f"[FAIL] Error testing {char_name}: {e}")
            all_valid = False
    
    print("\n" + "=" * 80)
    if all_valid:
        print("[PASS] All spell force values are valid (1-12)")
        return 0
    else:
        print("[FAIL] Some spell force values are invalid")
        return 1

def main():
    """Run all tests"""
    print("SPELL FORCE DISPLAY TEST SUITE")
    print("=" * 80)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test Characters: {', '.join(TEST_CHARACTERS)}")
    print("=" * 80)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_BASE_URL}/api/characters", timeout=2)
        if response.status_code != 200:
            print(f"\n[FAIL] Server not responding properly (status {response.status_code})")
            print("  Make sure the game server is running: python game-server.py")
            return 1
    except requests.exceptions.ConnectionError:
        print(f"\n[FAIL] Cannot connect to server at {API_BASE_URL}")
        print("  Make sure the game server is running: python game-server.py")
        return 1
    except Exception as e:
        print(f"\n[FAIL] Error connecting to server: {e}")
        return 1
    
    # Run tests
    results = []
    results.append(test_spell_force_in_api())
    results.append(test_spell_force_data_structure())
    results.append(test_spell_force_values())
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r == 0)
    failed_tests = total_tests - passed_tests
    
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n[PASS] ALL TESTS PASSED")
        return 0
    else:
        print(f"\n[FAIL] {failed_tests} TEST(S) FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
