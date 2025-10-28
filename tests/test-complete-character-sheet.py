#!/usr/bin/env python3
"""
Test Complete Character Sheet Display
Verifies ALL character data is returned by API and can be displayed
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Test configuration
BASE_URL = "http://localhost:8001"
TEST_CHARACTER = "Platinum"

def test_api_response():
    """Test that API returns all required fields"""
    print(f"\n{'='*80}")
    print(f"Testing API Response for {TEST_CHARACTER}")
    print(f"{'='*80}\n")
    
    url = f"{BASE_URL}/api/character/{TEST_CHARACTER}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"❌ FAILED: API returned status {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    data = response.json()
    
    # Required top-level fields
    required_fields = {
        'Basic Info': ['id', 'name', 'street_name', 'character_type', 'archetype'],
        'Physical Description': ['metatype', 'sex', 'age', 'height', 'weight', 'hair', 'eyes', 'skin'],
        'Resources': ['nuyen', 'karma_pool', 'karma_total', 'karma_available'],
        'Lifestyle': ['lifestyle', 'lifestyle_cost', 'lifestyle_months_prepaid'],
        'Essence': ['essence_hole'],
        'Initiative': ['initiative'],
        'Pools': ['combat_pool', 'magic_pool', 'body_index_current', 'body_index_max'],
        'Attributes': ['attributes'],
        'Skills': ['skills'],
        'Augmentations': ['cyberware', 'bioware'],
        'Gear': ['weapons', 'armor', 'equipment'],
        'Vehicles': ['vehicles'],
        'Contacts': ['contacts'],
        'Edges/Flaws': ['edges', 'flaws'],
        'Spells': ['spells'],
        'Background': ['background', 'notes']
    }
    
    print("Checking Required Fields:")
    print("-" * 80)
    
    all_present = True
    for category, fields in required_fields.items():
        print(f"\n{category}:")
        for field in fields:
            if field in data:
                value = data[field]
                if value is not None and value != [] and value != {}:
                    print(f"  ✓ {field}: {type(value).__name__}")
                else:
                    print(f"  ⚠ {field}: present but empty/null")
            else:
                print(f"  ❌ {field}: MISSING")
                all_present = False
    
    # Check nested structures
    print(f"\n{'='*80}")
    print("Checking Nested Structures:")
    print("-" * 80)
    
    # Attributes
    if 'attributes' in data and data['attributes']:
        attrs = data['attributes']
        print(f"\nAttributes ({len(attrs)} fields):")
        for key in ['body', 'quickness', 'strength', 'charisma', 'intelligence', 'willpower', 'essence', 'magic', 'reaction']:
            if key in attrs:
                base_key = f"{key}_base"
                if base_key in attrs and attrs[base_key] != attrs[key]:
                    print(f"  ✓ {key}: {attrs[key]} ({attrs[base_key]} base)")
                else:
                    print(f"  ✓ {key}: {attrs[key]}")
    
    # Skills
    if 'skills' in data and data['skills']:
        skills = data['skills']
        print(f"\nSkills:")
        for skill_type in ['active', 'knowledge', 'language']:
            if skill_type in skills:
                count = len(skills[skill_type])
                print(f"  ✓ {skill_type}: {count} skills")
                if count > 0:
                    # Show first skill as example
                    example = skills[skill_type][0]
                    print(f"    Example: {example.get('skill_name')} ({example.get('rating')})")
    
    # Cyberware
    if 'cyberware' in data and data['cyberware']:
        print(f"\nCyberware ({len(data['cyberware'])} items):")
        for item in data['cyberware'][:3]:  # Show first 3
            print(f"  ✓ {item['name']}: {item['essence_cost']} ESS")
    
    # Bioware
    if 'bioware' in data and data['bioware']:
        print(f"\nBioware ({len(data['bioware'])} items):")
        for item in data['bioware'][:3]:  # Show first 3
            print(f"  ✓ {item['name']}: {item['body_index_cost']} B.I.")
    
    # Weapons
    if 'weapons' in data and data['weapons']:
        print(f"\nWeapons ({len(data['weapons'])} items):")
        for weapon in data['weapons'][:3]:  # Show first 3
            print(f"  ✓ {weapon['name']}: {weapon.get('damage', 'N/A')}")
    
    # Armor
    if 'armor' in data and data['armor']:
        print(f"\nArmor ({len(data['armor'])} items):")
        for item in data['armor'][:3]:  # Show first 3
            rating = f"{item.get('ballistic_rating', 0)}/{item.get('impact_rating', 0)}"
            print(f"  ✓ {item['name']}: {rating}")
    
    # Equipment
    if 'equipment' in data and data['equipment']:
        print(f"\nEquipment ({len(data['equipment'])} items):")
        for item in data['equipment'][:3]:  # Show first 3
            qty = item.get('quantity', 1)
            print(f"  ✓ {item['name']}: ×{qty}")
    
    # Vehicles
    if 'vehicles' in data and data['vehicles']:
        print(f"\nVehicles ({len(data['vehicles'])} items):")
        for vehicle in data['vehicles']:
            print(f"  ✓ {vehicle['name']}: {vehicle.get('vehicle_type', 'N/A')}")
    
    # Contacts
    if 'contacts' in data and data['contacts']:
        print(f"\nContacts ({len(data['contacts'])} items):")
        for contact in data['contacts'][:3]:  # Show first 3
            print(f"  ✓ {contact['name']}: {contact.get('role', 'N/A')} (Level {contact.get('level', '?')})")
    
    # Edges and Flaws
    if 'edges' in data and data['edges']:
        print(f"\nEdges ({len(data['edges'])} items):")
        for edge in data['edges']:
            print(f"  ✓ {edge['name']}")
    
    if 'flaws' in data and data['flaws']:
        print(f"\nFlaws ({len(data['flaws'])} items):")
        for flaw in data['flaws']:
            print(f"  ✓ {flaw['name']}")
    
    # Spells
    if 'spells' in data and data['spells']:
        print(f"\nSpells ({len(data['spells'])} items):")
        for spell in data['spells'][:3]:  # Show first 3
            print(f"  ✓ {spell['spell_name']}: Force {spell.get('force', '?')}")
    
    print(f"\n{'='*80}")
    if all_present:
        print("✅ ALL REQUIRED FIELDS PRESENT")
    else:
        print("⚠️  SOME FIELDS MISSING (see above)")
    print(f"{'='*80}\n")
    
    return all_present


def print_manual_test_instructions():
    """Print manual testing instructions"""
    print(f"\n{'='*80}")
    print("MANUAL TESTING INSTRUCTIONS")
    print(f"{'='*80}\n")
    
    print("1. Open browser to: http://localhost:8001")
    print("2. Type 'Platinum' in the character dropdown")
    print("3. Click 'ADD CHARACTER' button")
    print("4. Click 'Platinum' in the Active Characters list")
    print("5. Verify the following sections appear in the character sheet modal:\n")
    
    sections = [
        "Basic Information (Name, Street Name, Archetype, Metatype)",
        "Physical Description (Sex, Age, Height, Weight, Hair, Eyes, Skin)",
        "Attributes (Body, Quickness, Strength, etc. with base values)",
        "Resources & Status (Nuyen, Karma, Lifestyle, Body Index, Initiative)",
        "Dice Pools (Combat Pool, Magic Pool if applicable)",
        "Edges & Flaws (if any)",
        "Skills (Active, Knowledge, Language - grouped separately)",
        "Cyberware (with essence costs and details)",
        "Bioware (with body index costs and details)",
        "Weapons (with damage, conceal, ammo, modifications)",
        "Armor (with ballistic/impact ratings)",
        "Equipment (other gear)",
        "Vehicles & Drones (if any)",
        "Magic & Spells (if applicable)",
        "Contacts (with roles and levels)",
        "Background (if present)",
        "Notes"
    ]
    
    for i, section in enumerate(sections, 1):
        print(f"   {i:2d}. {section}")
    
    print(f"\n{'='*80}")
    print("EXPECTED RESULTS FOR PLATINUM:")
    print(f"{'='*80}\n")
    
    print("✓ Should see 'Human Street Samurai' in subtitle")
    print("✓ Should see Physical Description section with height, weight, etc.")
    print("✓ Should see augmented attributes (e.g., Quickness 15 (10 base))")
    print("✓ Should see Body Index: 8.35/9")
    print("✓ Should see Combat Pool: 7 (Quickness 15 / 2)")
    print("✓ Should see Active Skills, Knowledge Skills, and Language Skills separately")
    print("✓ Should see Cyberware section with Wired Reflexes 3, Reaction Enhancers 6, etc.")
    print("✓ Should see Bioware section with Enhanced Articulation, Cerebral Booster 3, etc.")
    print("✓ Should see Weapons section with Morrissey Alta, Ares Alpha, Panther Assault Cannon, etc.")
    print("✓ Should see Armor section with ratings")
    print("✓ Should see Equipment section with grenades, medkits, etc.")
    print("✓ Should see Vehicles section with GMC Bulldog Stepvan and Eurocar Westwind")
    print("✓ Should see Contacts section with Tanis Driscol, Volaren, Fuzzy Eddy, etc.")
    print("✓ Should see Edges section with 'Exceptional Attribute' and 'Ambidexterity'")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("COMPLETE CHARACTER SHEET TEST")
    print("="*80)
    
    # Test API
    api_success = test_api_response()
    
    # Print manual test instructions
    print_manual_test_instructions()
    
    if api_success:
        print("✅ API TEST PASSED - All required data is being returned")
        print("📋 Follow the manual testing instructions above to verify display")
        sys.exit(0)
    else:
        print("❌ API TEST FAILED - Some data is missing")
        print("⚠️  Fix API issues before testing display")
        sys.exit(1)
