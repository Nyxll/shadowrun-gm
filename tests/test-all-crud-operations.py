#!/usr/bin/env python3
"""
Comprehensive CRUD API Test Suite
Tests all 40+ operations in lib/comprehensive_crud.py
"""

import os
import sys
import uuid
from dotenv import load_dotenv
import psycopg

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.comprehensive_crud import ComprehensiveCRUD, get_system_user_id

load_dotenv()


class CRUDTestSuite:
    """Comprehensive test suite for all CRUD operations"""
    
    def __init__(self):
        # Get SYSTEM user ID using CRUD API helper
        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST'),
            port=int(os.getenv('POSTGRES_PORT')),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        user_id = get_system_user_id(conn)
        conn.close()
        
        self.crud = ComprehensiveCRUD(user_id)
        self.passed = 0
        self.failed = 0
        self.test_character_id = None
        self.test_character_name = "CRUD Test Character"
    
    def log(self, name, passed, msg="", result=None):
        """Log test result"""
        if passed:
            self.passed += 1
            print(f"  [PASS] {name}")
        else:
            self.failed += 1
            print(f"  [FAIL] {name}: {msg}")
            if result:
                print(f"    Result: {result}")
    
    def cleanup_test_character(self):
        """Remove test character if it exists"""
        try:
            char = self.crud.get_character_by_name(self.test_character_name)
            if char:
                self.crud.delete_character(char['id'])
                print(f"  Cleaned up existing test character")
        except:
            pass
    
    # ========================================
    # CHARACTER MANAGEMENT TESTS
    # ========================================
    
    def test_create_character(self):
        """Test creating a new character"""
        try:
            char_data = {
                'name': self.test_character_name,
                'street_name': 'TestRunner',
                'character_type': 'Player Character',
                'archetype': 'Street Samurai',
                'base_body': 5,
                'base_quickness': 6,
                'base_strength': 5,
                'base_charisma': 3,
                'base_intelligence': 4,
                'base_willpower': 4,
                'base_essence': 6.0,
                'base_magic': 0,
                'base_reaction': 5,
                'nuyen': 5000,
                'karma_pool': 3
            }
            
            result = self.crud.create_character(char_data)
            self.test_character_id = result['id']
            
            self.log("create_character", 
                    result is not None and 'id' in result,
                    result=result)
        except Exception as e:
            self.log("create_character", False, str(e))
    
    def test_get_character(self):
        """Test getting character by ID"""
        try:
            result = self.crud.get_character(self.test_character_id)
            self.log("get_character",
                    result is not None and result['name'] == self.test_character_name,
                    result=result)
        except Exception as e:
            self.log("get_character", False, str(e))
    
    def test_get_character_by_name(self):
        """Test getting character by name"""
        try:
            result = self.crud.get_character_by_name(self.test_character_name)
            self.log("get_character_by_name",
                    result is not None and result['id'] == self.test_character_id,
                    result=result)
        except Exception as e:
            self.log("get_character_by_name", False, str(e))
    
    def test_list_characters(self):
        """Test listing all characters"""
        try:
            result = self.crud.list_characters()
            has_test_char = any(c['id'] == self.test_character_id for c in result)
            self.log("list_characters",
                    isinstance(result, list) and has_test_char,
                    result=f"{len(result)} characters found")
        except Exception as e:
            self.log("list_characters", False, str(e))
    
    def test_update_character(self):
        """Test updating character"""
        try:
            updates = {'nuyen': 10000, 'karma_pool': 5}
            result = self.crud.update_character(self.test_character_id, updates)
            
            # Verify update
            char = self.crud.get_character(self.test_character_id)
            self.log("update_character",
                    char['nuyen'] == 10000 and char['karma_pool'] == 5,
                    result=result)
        except Exception as e:
            self.log("update_character", False, str(e))
    
    # ========================================
    # SKILLS TESTS
    # ========================================
    
    def test_add_skill(self):
        """Test adding a skill"""
        try:
            skill_data = {
                'skill_name': 'Firearms',
                'skill_type': 'active',
                'base_rating': 6,
                'current_rating': 6,
                'specialization': 'Pistols'
            }
            result = self.crud.add_skill(self.test_character_id, skill_data)
            self.log("add_skill", result is not None, result=result)
        except Exception as e:
            self.log("add_skill", False, str(e))
    
    def test_get_character_skills(self):
        """Test getting character skills"""
        try:
            result = self.crud.get_character_skills(self.test_character_id)
            has_firearms = any(s['skill_name'] == 'Firearms' for s in result)
            self.log("get_character_skills",
                    isinstance(result, list) and has_firearms,
                    result=f"{len(result)} skills found")
        except Exception as e:
            self.log("get_character_skills", False, str(e))
    
    def test_update_skill(self):
        """Test updating a skill"""
        try:
            updates = {'current_rating': 7}
            result = self.crud.update_skill(self.test_character_id, 'Firearms', updates)
            
            # Verify
            skills = self.crud.get_character_skills(self.test_character_id)
            firearms = next(s for s in skills if s['skill_name'] == 'Firearms')
            self.log("update_skill",
                    firearms['current_rating'] == 7,
                    result=result)
        except Exception as e:
            self.log("update_skill", False, str(e))
    
    def test_remove_skill(self):
        """Test removing a skill"""
        try:
            result = self.crud.remove_skill(self.test_character_id, 'Firearms')
            
            # Verify
            skills = self.crud.get_character_skills(self.test_character_id)
            has_firearms = any(s['skill_name'] == 'Firearms' for s in skills)
            self.log("remove_skill",
                    not has_firearms,
                    result=result)
        except Exception as e:
            self.log("remove_skill", False, str(e))
    
    # ========================================
    # SPELLS TESTS
    # ========================================
    
    def test_add_spell(self):
        """Test adding a spell"""
        try:
            spell_data = {
                'spell_name': 'Manabolt',
                'spell_category': 'combat',
                'spell_type': 'mana',
                'learned_force': 6,
                'drain_modifier': 0
            }
            result = self.crud.add_spell(self.test_character_id, spell_data)
            self.log("add_spell", result is not None, result=result)
        except Exception as e:
            self.log("add_spell", False, str(e))
    
    def test_get_character_spells(self):
        """Test getting character spells"""
        try:
            result = self.crud.get_character_spells(self.test_character_id)
            has_manabolt = any(s['spell_name'] == 'Manabolt' for s in result)
            self.log("get_character_spells",
                    isinstance(result, list) and has_manabolt,
                    result=f"{len(result)} spells found")
        except Exception as e:
            self.log("get_character_spells", False, str(e))
    
    def test_update_spell(self):
        """Test updating a spell"""
        try:
            updates = {'learned_force': 8}
            result = self.crud.update_spell(self.test_character_id, 'Manabolt', updates)
            
            # Verify
            spells = self.crud.get_character_spells(self.test_character_id)
            manabolt = next(s for s in spells if s['spell_name'] == 'Manabolt')
            self.log("update_spell",
                    manabolt['learned_force'] == 8,
                    result=result)
        except Exception as e:
            self.log("update_spell", False, str(e))
    
    def test_remove_spell(self):
        """Test removing a spell"""
        try:
            result = self.crud.remove_spell(self.test_character_id, 'Manabolt')
            
            # Verify
            spells = self.crud.get_character_spells(self.test_character_id)
            has_manabolt = any(s['spell_name'] == 'Manabolt' for s in spells)
            self.log("remove_spell",
                    not has_manabolt,
                    result=result)
        except Exception as e:
            self.log("remove_spell", False, str(e))
    
    # ========================================
    # GEAR TESTS
    # ========================================
    
    def test_add_gear(self):
        """Test adding gear"""
        try:
            gear_data = {
                'gear_name': 'Armor Vest',
                'gear_type': 'armor',
                'quantity': 1,
                'rating': 4,
                'description': 'Light ballistic protection'
            }
            result = self.crud.add_gear(self.test_character_id, gear_data)
            self.log("add_gear", result is not None, result=result)
        except Exception as e:
            self.log("add_gear", False, str(e))
    
    def test_get_character_gear(self):
        """Test getting character gear"""
        try:
            result = self.crud.get_character_gear(self.test_character_id)
            has_vest = any(g['gear_name'] == 'Armor Vest' for g in result)
            self.log("get_character_gear",
                    isinstance(result, list) and has_vest,
                    result=f"{len(result)} gear items found")
        except Exception as e:
            self.log("get_character_gear", False, str(e))
    
    def test_update_gear(self):
        """Test updating gear"""
        try:
            updates = {'quantity': 2}
            result = self.crud.update_gear(self.test_character_id, 'Armor Vest', updates)
            
            # Verify
            gear = self.crud.get_character_gear(self.test_character_id)
            vest = next(g for g in gear if g['gear_name'] == 'Armor Vest')
            self.log("update_gear",
                    vest['quantity'] == 2,
                    result=result)
        except Exception as e:
            self.log("update_gear", False, str(e))
    
    def test_remove_gear(self):
        """Test removing gear"""
        try:
            result = self.crud.remove_gear(self.test_character_id, 'Armor Vest')
            
            # Verify
            gear = self.crud.get_character_gear(self.test_character_id)
            has_vest = any(g['gear_name'] == 'Armor Vest' for g in gear)
            self.log("remove_gear",
                    not has_vest,
                    result=result)
        except Exception as e:
            self.log("remove_gear", False, str(e))
    
    # ========================================
    # CYBERWARE TESTS
    # ========================================
    
    def test_add_cyberware(self):
        """Test adding cyberware"""
        try:
            cyber_data = {
                'name': 'Smartlink II',
                'target_name': 'firearms',  # What it modifies
                'modifier_value': 2,
                'essence_cost': 0.5,
                'modifier_data': {
                    'rating': 2,
                    'body_location': 'eyes'
                }
            }
            result = self.crud.add_cyberware(self.test_character_id, cyber_data)
            self.test_cyberware_id = result['id']
            self.log("add_cyberware", result is not None, result=result)
        except Exception as e:
            self.log("add_cyberware", False, str(e))
    
    def test_get_character_cyberware(self):
        """Test getting character cyberware"""
        try:
            result = self.crud.get_character_cyberware(self.test_character_id)
            has_smartlink = any(c['source'] == 'Smartlink II' for c in result)
            self.log("get_character_cyberware",
                    isinstance(result, list) and has_smartlink,
                    result=f"{len(result)} cyberware items found")
        except Exception as e:
            self.log("get_character_cyberware", False, str(e))
    
    def test_update_cyberware(self):
        """Test updating cyberware"""
        try:
            updates = {'modifier_value': 3}
            result = self.crud.update_cyberware(self.test_character_id, self.test_cyberware_id, updates)
            
            # Verify
            cyber = self.crud.get_character_cyberware(self.test_character_id)
            smartlink = next(c for c in cyber if c['id'] == self.test_cyberware_id)
            self.log("update_cyberware",
                    smartlink['modifier_value'] == 3,
                    result=result)
        except Exception as e:
            self.log("update_cyberware", False, str(e))
    
    def test_remove_cyberware(self):
        """Test removing cyberware"""
        try:
            result = self.crud.remove_cyberware(self.test_character_id, self.test_cyberware_id)
            
            # Verify
            cyber = self.crud.get_character_cyberware(self.test_character_id)
            has_smartlink = any(c['id'] == self.test_cyberware_id for c in cyber)
            self.log("remove_cyberware",
                    not has_smartlink,
                    result=result)
        except Exception as e:
            self.log("remove_cyberware", False, str(e))
    
    # ========================================
    # BIOWARE TESTS
    # ========================================
    
    def test_add_bioware(self):
        """Test adding bioware"""
        try:
            bio_data = {
                'name': 'Muscle Replacement 2',
                'target_name': 'strength',
                'modifier_value': 2,
                'essence_cost': 0.4,
                'modifier_data': {
                    'rating': 2
                }
            }
            result = self.crud.add_bioware(self.test_character_id, bio_data)
            self.test_bioware_id = result['id']
            self.log("add_bioware", result is not None, result=result)
        except Exception as e:
            self.log("add_bioware", False, str(e))
    
    def test_get_character_bioware(self):
        """Test getting character bioware"""
        try:
            result = self.crud.get_character_bioware(self.test_character_id)
            has_muscle = any(b['source'] == 'Muscle Replacement 2' for b in result)
            self.log("get_character_bioware",
                    isinstance(result, list) and has_muscle,
                    result=f"{len(result)} bioware items found")
        except Exception as e:
            self.log("get_character_bioware", False, str(e))
    
    def test_remove_bioware(self):
        """Test removing bioware"""
        try:
            result = self.crud.remove_bioware(self.test_character_id, self.test_bioware_id)
            
            # Verify
            bio = self.crud.get_character_bioware(self.test_character_id)
            has_muscle = any(b['id'] == self.test_bioware_id for b in bio)
            self.log("remove_bioware",
                    not has_muscle,
                    result=result)
        except Exception as e:
            self.log("remove_bioware", False, str(e))
    
    # ========================================
    # CLEANUP
    # ========================================
    
    def test_delete_character(self):
        """Test deleting character (cleanup)"""
        try:
            result = self.crud.delete_character(self.test_character_id)
            
            # Verify deletion - should raise exception
            try:
                char = self.crud.get_character(self.test_character_id)
                self.log("delete_character", False, "Character still exists after deletion")
            except ValueError:
                # Expected - character should not exist
                self.log("delete_character", True, result=result)
        except Exception as e:
            self.log("delete_character", False, str(e))
    
    # ========================================
    # TEST RUNNER
    # ========================================
    
    def run_all(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("COMPREHENSIVE CRUD API TEST SUITE")
        print("="*60 + "\n")
        
        # Cleanup any existing test character
        self.cleanup_test_character()
        
        print("CHARACTER MANAGEMENT:")
        self.test_create_character()
        self.test_get_character()
        self.test_get_character_by_name()
        self.test_list_characters()
        self.test_update_character()
        
        print("\nSKILLS:")
        self.test_add_skill()
        self.test_get_character_skills()
        self.test_update_skill()
        self.test_remove_skill()
        
        print("\nSPELLS:")
        self.test_add_spell()
        self.test_get_character_spells()
        self.test_update_spell()
        self.test_remove_spell()
        
        print("\nGEAR:")
        self.test_add_gear()
        self.test_get_character_gear()
        self.test_update_gear()
        self.test_remove_gear()
        
        print("\nCYBERWARE:")
        self.test_add_cyberware()
        self.test_get_character_cyberware()
        self.test_update_cyberware()
        self.test_remove_cyberware()
        
        print("\nBIOWARE:")
        self.test_add_bioware()
        self.test_get_character_bioware()
        self.test_remove_bioware()
        
        print("\nCLEANUP:")
        self.test_delete_character()
        
        print("\n" + "="*60)
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        print("="*60 + "\n")
        
        return self.failed == 0


def main():
    """Main test runner"""
    suite = CRUDTestSuite()
    success = suite.run_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
