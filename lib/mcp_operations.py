#!/usr/bin/env python3

"""
MCP Operations using Comprehensive CRUD API
Replaces direct SQL queries with CRUD API calls
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

from lib.comprehensive_crud import ComprehensiveCRUD, get_ai_user_id
from lib.dice_roller import DiceRoller
from lib.combat_modifiers import CombatModifiers
from lib.spellcasting import SpellcastingEngine

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class MCPOperations:

    """MCP operations using comprehensive CRUD API"""
    def __init__(self):
        """Initialize with AI user for MCP operations"""
        # Get database connection for AI user lookup

        conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
            port=int(os.getenv('POSTGRES_PORT', '5434')),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )

        

        # Get AI user ID
        self.ai_user_id = get_ai_user_id(conn)
        conn.close()

        # Create CRUD API instance
        self.crud = ComprehensiveCRUD(user_id=self.ai_user_id, user_type='AI')

    def close(self):
        """Close CRUD API connection"""
        self.crud.close()

    async def list_characters(self) -> List[Dict]:
        """List all characters using CRUD API"""
        logger.info("Listing all characters")
        return self.crud.list_characters()

    async def add_karma(self, character_name: str, amount: int, reason: str = None) -> Dict:
        """Add karma to character's total and available pool"""
        logger.info(f"Adding {amount} karma to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)

            result = self.crud.add_karma(character['id'], amount, reason)

            return {
                "character": character_name,
                "karma_added": amount,
                "reason": reason,
                "karma_total": result['karma_total'],
                "karma_available": result.get('karma_available', 0),
                "karma_pool": result['karma_pool'],
                "summary": f"Added {amount} karma to {character_name}. Total: {result['karma_total']}, Available: {result.get('karma_available', 0)}"
            }

        except ValueError as e:
            return {"error": str(e)}

    

    async def spend_karma(self, character_name: str, amount: int, reason: str = None) -> Dict:
        """Spend karma from character's available pool"""
        logger.info(f"Spending {amount} karma for {character_name}")

        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)

            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            result = self.crud.spend_karma(character['id'], amount, reason)
            return {
                "character": character_name,
                "karma_spent": amount,
                "reason": reason,
                "karma_available": result.get('karma_available', 0),
                "karma_total": result['karma_total'],
                "summary": f"Spent {amount} karma for {character_name}. Remaining: {result.get('karma_available', 0)}"
            }

        except ValueError as e:
            return {"error": str(e)}

    async def update_karma_pool(self, character_name: str, new_pool: int, reason: str = None) -> Dict:
        """Update character's karma pool (for in-game spending)"""
        logger.info(f"Setting karma pool to {new_pool} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)

            result = self.crud.update_karma_pool(character['id'], new_pool, reason)

            return {
                "character": character_name,
                "karma_pool": result['karma_pool'],
                "reason": reason,
                "summary": f"Set {character_name}'s karma pool to {new_pool}"
            }

        except ValueError as e:
            return {"error": str(e)}

    async def set_karma(self, character_name: str, total: int, available: int, reason: str = None) -> Dict:
        """Set both total and available karma (for error correction)"""
        logger.info(f"Setting karma to total={total}, available={available} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            result = self.crud.set_karma(character['id'], total, available, reason)
            return {
                "character": character_name,
                "karma_total": total,
                "karma_available": available,
                "reason": reason,
                "summary": f"Set {character_name}'s karma to total={total}, available={available}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== PHASE 2: AUGMENTATIONS & EQUIPMENT ==========
    
    # Cyberware & Bioware (7 operations)
    async def get_cyberware(self, character_name: str) -> Dict:
        """Get all cyberware for character"""
        logger.info(f"Getting cyberware for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_character_cyberware(character['id'])
            
            return {
                "character": character_name,
                "cyberware": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} cyberware items for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_bioware(self, character_name: str) -> Dict:
        """Get all bioware for character"""
        logger.info(f"Getting bioware for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_character_bioware(character['id'])
            
            return {
                "character": character_name,
                "bioware": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} bioware items for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_cyberware(self, character_name: str, name: str, essence_cost: float = 0,
                           target_name: str = None, modifier_value: int = 0, 
                           modifier_data: Dict = None, reason: str = None) -> Dict:
        """Add cyberware to character"""
        logger.info(f"Adding cyberware {name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_cyberware(
                character['id'],
                {
                    "name": name,
                    "target_name": target_name,
                    "modifier_value": modifier_value,
                    "modifier_data": modifier_data or {}
                },
                reason
            )
            
            return {
                "character": character_name,
                "cyberware_added": name,
                "essence_cost": essence_cost,
                "summary": f"Added cyberware {name} to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_bioware(self, character_name: str, name: str, essence_cost: float = 0,
                         target_name: str = None, modifier_value: int = 0,
                         modifier_data: Dict = None, reason: str = None) -> Dict:
        """Add bioware to character"""
        logger.info(f"Adding bioware {name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_bioware(
                character['id'],
                {
                    "name": name,
                    "target_name": target_name,
                    "modifier_value": modifier_value,
                    "modifier_data": modifier_data or {}
                },
                reason
            )
            
            return {
                "character": character_name,
                "bioware_added": name,
                "essence_cost": essence_cost,
                "summary": f"Added bioware {name} to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_cyberware(self, character_name: str, modifier_id: str, updates: Dict, reason: str = None) -> Dict:
        """Update cyberware details"""
        logger.info(f"Updating cyberware {modifier_id} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_cyberware(character['id'], modifier_id, updates, reason)
            
            return {
                "character": character_name,
                "cyberware_updated": modifier_id,
                "updates": updates,
                "summary": f"Updated cyberware for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_cyberware(self, character_name: str, modifier_id: str, reason: str = None) -> Dict:
        """Remove cyberware from character"""
        logger.info(f"Removing cyberware {modifier_id} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_cyberware(character['id'], modifier_id, reason)
            
            return {
                "character": character_name,
                "cyberware_removed": modifier_id,
                "summary": f"Removed cyberware from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_bioware(self, character_name: str, modifier_id: str, reason: str = None) -> Dict:
        """Remove bioware from character"""
        logger.info(f"Removing bioware {modifier_id} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_bioware(character['id'], modifier_id, reason)
            
            return {
                "character": character_name,
                "bioware_removed": modifier_id,
                "summary": f"Removed bioware from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Vehicles (4 operations)
    async def get_vehicles(self, character_name: str) -> Dict:
        """Get all vehicles for character"""
        logger.info(f"Getting vehicles for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_vehicles(character['id'])
            
            return {
                "character": character_name,
                "vehicles": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} vehicles for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_vehicle(self, character_name: str, vehicle_name: str, vehicle_type: str = None,
                         handling: int = None, speed: int = None, body: int = None,
                         armor: int = None, signature: int = None, pilot: int = None,
                         modifications: Dict = None, reason: str = None) -> Dict:
        """Add vehicle to character"""
        logger.info(f"Adding vehicle {vehicle_name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_vehicle(
                character['id'],
                {
                    "vehicle_name": vehicle_name,
                    "vehicle_type": vehicle_type,
                    "handling": handling,
                    "speed": speed,
                    "body": body,
                    "armor": armor,
                    "signature": signature,
                    "pilot": pilot,
                    "modifications": modifications or {}
                },
                reason
            )
            
            return {
                "character": character_name,
                "vehicle_added": vehicle_name,
                "vehicle_type": vehicle_type,
                "summary": f"Added vehicle {vehicle_name} to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_vehicle(self, character_name: str, vehicle_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update vehicle details"""
        logger.info(f"Updating vehicle {vehicle_name} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_vehicle(character['id'], vehicle_name, updates, reason)
            
            return {
                "character": character_name,
                "vehicle": vehicle_name,
                "updates": updates,
                "summary": f"Updated vehicle {vehicle_name} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_vehicle(self, character_name: str, vehicle_name: str, reason: str = None) -> Dict:
        """Remove vehicle from character"""
        logger.info(f"Removing vehicle {vehicle_name} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.delete_vehicle(character['id'], vehicle_name, reason)
            
            return {
                "character": character_name,
                "vehicle_removed": vehicle_name,
                "summary": f"Removed vehicle {vehicle_name} from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Cyberdecks (2 operations)
    async def get_cyberdecks(self, character_name: str) -> Dict:
        """Get all cyberdecks for character"""
        logger.info(f"Getting cyberdecks for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_cyberdecks(character['id'])
            
            return {
                "character": character_name,
                "cyberdecks": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} cyberdecks for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_cyberdeck(self, character_name: str, deck_name: str, mpcp: int = None,
                           hardening: int = None, memory: int = None, storage: int = None,
                           io_speed: int = None, response_increase: int = None,
                           persona_programs: List = None, utilities: List = None,
                           ai_companions: List = None, reason: str = None) -> Dict:
        """Add cyberdeck to character"""
        logger.info(f"Adding cyberdeck {deck_name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_cyberdeck(
                character['id'],
                {
                    "deck_name": deck_name,
                    "mpcp": mpcp,
                    "hardening": hardening,
                    "memory": memory,
                    "storage": storage,
                    "io_speed": io_speed,
                    "response_increase": response_increase,
                    "persona_programs": persona_programs or [],
                    "utilities": utilities or [],
                    "ai_companions": ai_companions or []
                },
                reason
            )
            
            return {
                "character": character_name,
                "cyberdeck_added": deck_name,
                "mpcp": mpcp,
                "summary": f"Added cyberdeck {deck_name} to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== PHASE 3: SOCIAL & MAGICAL ==========
    
    # Contacts (3 operations)
    async def get_contacts(self, character_name: str) -> Dict:
        """Get all contacts for character"""
        logger.info(f"Getting contacts for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_contacts(character['id'])
            
            return {
                "character": character_name,
                "contacts": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} contacts for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_contact(self, character_name: str, name: str, archetype: str = None,
                         loyalty: int = 1, connection: int = 1, notes: str = None, reason: str = None) -> Dict:
        """Add contact to character"""
        logger.info(f"Adding contact {name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_contact(
                character['id'],
                {
                    "name": name,
                    "archetype": archetype,
                    "loyalty": loyalty,
                    "connection": connection,
                    "notes": notes
                },
                reason
            )
            
            return {
                "character": character_name,
                "contact_added": name,
                "loyalty": loyalty,
                "connection": connection,
                "summary": f"Added contact {name} (Loyalty {loyalty}, Connection {connection}) to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_contact_loyalty(self, character_name: str, contact_name: str, loyalty: int, reason: str = None) -> Dict:
        """Update contact loyalty rating"""
        logger.info(f"Updating loyalty for contact {contact_name} to {loyalty} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_contact_loyalty(character['id'], contact_name, loyalty, reason)
            
            return {
                "character": character_name,
                "contact": contact_name,
                "loyalty": loyalty,
                "summary": f"Updated {contact_name}'s loyalty to {loyalty} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Spirits & Foci (5 operations)
    async def get_spirits(self, character_name: str) -> Dict:
        """Get all spirits for character"""
        logger.info(f"Getting spirits for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_spirits(character['id'])
            
            return {
                "character": character_name,
                "spirits": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} spirits for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_spirit(self, character_name: str, spirit_name: str, spirit_type: str = None,
                        force: int = 1, services: int = 1, special_abilities: List = None,
                        notes: str = None, reason: str = None) -> Dict:
        """Add spirit to character"""
        logger.info(f"Adding spirit {spirit_name} (Force {force}) to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_spirit(
                character['id'],
                {
                    "spirit_name": spirit_name,
                    "spirit_type": spirit_type,
                    "force": force,
                    "services": services,
                    "special_abilities": special_abilities or [],
                    "notes": notes
                },
                reason
            )
            
            return {
                "character": character_name,
                "spirit_added": spirit_name,
                "force": force,
                "services": services,
                "summary": f"Added {spirit_type or 'spirit'} {spirit_name} (Force {force}, {services} services) to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_spirit_services(self, character_name: str, spirit_name: str, services: int, reason: str = None) -> Dict:
        """Update spirit services remaining"""
        logger.info(f"Updating services for spirit {spirit_name} to {services} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_spirit_services(character['id'], spirit_name, services, reason)
            
            return {
                "character": character_name,
                "spirit": spirit_name,
                "services": services,
                "summary": f"Updated {spirit_name}'s services to {services} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_foci(self, character_name: str) -> Dict:
        """Get all foci for character"""
        logger.info(f"Getting foci for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_foci(character['id'])
            
            return {
                "character": character_name,
                "foci": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} foci for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_focus(self, character_name: str, focus_name: str, focus_type: str,
                       force: int, spell_category: str = None, specific_spell: str = None,
                       bonus_dice: int = 0, tn_modifier: int = 0, bonded: bool = True,
                       karma_cost: int = None, description: str = None, notes: str = None,
                       reason: str = None) -> Dict:
        """Add focus to character"""
        logger.info(f"Adding focus {focus_name} (Force {force}) to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_focus(
                character['id'],
                {
                    "focus_name": focus_name,
                    "focus_type": focus_type,
                    "force": force,
                    "spell_category": spell_category,
                    "specific_spell": specific_spell,
                    "bonus_dice": bonus_dice,
                    "tn_modifier": tn_modifier,
                    "bonded": bonded,
                    "karma_cost": karma_cost,
                    "description": description,
                    "notes": notes
                },
                reason
            )
            
            return {
                "character": character_name,
                "focus_added": focus_name,
                "focus_type": focus_type,
                "force": force,
                "bonded": bonded,
                "summary": f"Added {focus_type} focus {focus_name} (Force {force}) to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Powers (3 operations)
    async def get_powers(self, character_name: str) -> Dict:
        """Get all powers for character"""
        logger.info(f"Getting powers for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_powers(character['id'])
            
            return {
                "character": character_name,
                "powers": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} powers for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_power(self, character_name: str, power_name: str, level: int = 1,
                       cost: int = 0, reason: str = None) -> Dict:
        """Add power to character"""
        logger.info(f"Adding power {power_name} (Level {level}) to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_power(
                character['id'],
                {
                    "power_name": power_name,
                    "level": level,
                    "cost": cost
                },
                reason
            )
            
            return {
                "character": character_name,
                "power_added": power_name,
                "level": level,
                "cost": cost,
                "summary": f"Added power {power_name} (Level {level}) to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_power_level(self, character_name: str, power_name: str, new_level: int, reason: str = None) -> Dict:
        """Update power level"""
        logger.info(f"Updating power {power_name} to level {new_level} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_power_level(character['id'], power_name, new_level, reason)
            
            return {
                "character": character_name,
                "power": power_name,
                "new_level": new_level,
                "summary": f"Updated {power_name} to level {new_level} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Edges & Flaws (2 operations)
    async def get_edges_flaws(self, character_name: str) -> Dict:
        """Get all edges and flaws for character"""
        logger.info(f"Getting edges/flaws for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_edges_flaws(character['id'])
            
            edges = [e for e in result if e['type'] == 'edge']
            flaws = [f for f in result if f['type'] == 'flaw']
            
            return {
                "character": character_name,
                "edges": edges,
                "flaws": flaws,
                "total_count": len(result),
                "summary": f"Retrieved {len(edges)} edges and {len(flaws)} flaws for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_edge_flaw(self, character_name: str, name: str, type_: str,
                           description: str = None, cost: int = None, reason: str = None) -> Dict:
        """Add edge or flaw to character"""
        logger.info(f"Adding {type_} {name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_edge_flaw(
                character['id'],
                {
                    "name": name,
                    "type": type_,
                    "description": description,
                    "cost": cost
                },
                reason
            )
            
            return {
                "character": character_name,
                f"{type_}_added": name,
                "cost": cost,
                "summary": f"Added {type_} {name} to {character_name}" + (f" ({cost:+d} karma)" if cost else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Relationships (2 operations)
    async def get_relationships(self, character_name: str) -> Dict:
        """Get all relationships for character"""
        logger.info(f"Getting relationships for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_relationships(character['id'])
            
            return {
                "character": character_name,
                "relationships": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} relationships for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_relationship(self, character_name: str, relationship_type: str, relationship_name: str,
                              data: Dict = None, notes: str = None, reason: str = None) -> Dict:
        """Add relationship to character"""
        logger.info(f"Adding {relationship_type} relationship {relationship_name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_relationship(
                character['id'],
                {
                    "relationship_type": relationship_type,
                    "relationship_name": relationship_name,
                    "data": data or {},
                    "notes": notes
                },
                reason
            )
            
            return {
                "character": character_name,
                "relationship_added": relationship_name,
                "relationship_type": relationship_type,
                "summary": f"Added {relationship_type} relationship {relationship_name} to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== PHASE 4: GAME STATE MANAGEMENT ==========
    
    # Active Effects (4 operations)
    async def get_active_effects(self, character_name: str) -> Dict:
        """Get all active effects for character"""
        logger.info(f"Getting active effects for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_active_effects(character['id'])
            
            return {
                "character": character_name,
                "active_effects": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} active effects for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_active_effect(self, character_name: str, effect_name: str, effect_type: str,
                               duration: int = None, modifier_value: int = None,
                               target_attribute: str = None, description: str = None,
                               reason: str = None) -> Dict:
        """Add active effect to character"""
        logger.info(f"Adding active effect {effect_name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_active_effect(
                character['id'],
                {
                    "effect_name": effect_name,
                    "effect_type": effect_type,
                    "duration": duration,
                    "modifier_value": modifier_value,
                    "target_attribute": target_attribute,
                    "description": description
                },
                reason
            )
            
            return {
                "character": character_name,
                "effect_added": effect_name,
                "effect_type": effect_type,
                "duration": duration,
                "summary": f"Added {effect_type} effect {effect_name} to {character_name}" + (f" (duration: {duration})" if duration else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_effect_duration(self, character_name: str, effect_name: str, new_duration: int, reason: str = None) -> Dict:
        """Update active effect duration"""
        logger.info(f"Updating duration for effect {effect_name} to {new_duration} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_effect_duration(character['id'], effect_name, new_duration, reason)
            
            return {
                "character": character_name,
                "effect": effect_name,
                "new_duration": new_duration,
                "summary": f"Updated {effect_name} duration to {new_duration} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_active_effect(self, character_name: str, effect_name: str, reason: str = None) -> Dict:
        """Remove active effect from character"""
        logger.info(f"Removing active effect {effect_name} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_active_effect(character['id'], effect_name, reason)
            
            return {
                "character": character_name,
                "effect_removed": effect_name,
                "summary": f"Removed active effect {effect_name} from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Modifiers (4 operations)
    async def get_modifiers(self, character_name: str, modifier_type: str = None) -> Dict:
        """Get all modifiers for character"""
        logger.info(f"Getting modifiers for {character_name}" + (f" (type: {modifier_type})" if modifier_type else ""))
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_modifiers(character['id'], modifier_type)
            
            return {
                "character": character_name,
                "modifiers": result,
                "count": len(result),
                "modifier_type": modifier_type,
                "summary": f"Retrieved {len(result)} modifiers for {character_name}" + (f" (type: {modifier_type})" if modifier_type else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_modifier(self, character_name: str, modifier_name: str, modifier_type: str,
                          target_name: str = None, modifier_value: int = 0,
                          modifier_data: Dict = None, reason: str = None) -> Dict:
        """Add modifier to character"""
        logger.info(f"Adding {modifier_type} modifier {modifier_name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_modifier(
                character['id'],
                {
                    "modifier_name": modifier_name,
                    "modifier_type": modifier_type,
                    "target_name": target_name,
                    "modifier_value": modifier_value,
                    "modifier_data": modifier_data or {}
                },
                reason
            )
            
            return {
                "character": character_name,
                "modifier_added": modifier_name,
                "modifier_type": modifier_type,
                "target": target_name,
                "value": modifier_value,
                "summary": f"Added {modifier_type} modifier {modifier_name} to {character_name}" + (f" (target: {target_name})" if target_name else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_modifier(self, character_name: str, modifier_id: str, updates: Dict, reason: str = None) -> Dict:
        """Update modifier details"""
        logger.info(f"Updating modifier {modifier_id} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_modifier(character['id'], modifier_id, updates, reason)
            
            return {
                "character": character_name,
                "modifier_updated": modifier_id,
                "updates": updates,
                "summary": f"Updated modifier {modifier_id} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_modifier(self, character_name: str, modifier_id: str, reason: str = None) -> Dict:
        """Remove modifier from character"""
        logger.info(f"Removing modifier {modifier_id} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_modifier(character['id'], modifier_id, reason)
            
            return {
                "character": character_name,
                "modifier_removed": modifier_id,
                "summary": f"Removed modifier {modifier_id} from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== PHASE 5: CAMPAIGN MANAGEMENT ==========
    
    # House Rules (3 operations)
    async def get_house_rules(self) -> Dict:
        """Get all house rules"""
        logger.info("Getting house rules")
        try:
            result = self.crud.get_house_rules()
            
            return {
                "house_rules": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} house rules"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_house_rule(self, rule_name: str, rule_type: str, description: str,
                            mechanical_effect: Dict = None, is_active: bool = True,
                            reason: str = None) -> Dict:
        """Add house rule"""
        logger.info(f"Adding house rule {rule_name}")
        try:
            result = self.crud.add_house_rule(
                {
                    "rule_name": rule_name,
                    "rule_type": rule_type,
                    "description": description,
                    "mechanical_effect": mechanical_effect or {},
                    "is_active": is_active
                },
                reason
            )
            
            return {
                "house_rule_added": rule_name,
                "rule_type": rule_type,
                "is_active": is_active,
                "summary": f"Added house rule {rule_name} ({rule_type})"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def toggle_house_rule(self, rule_name: str, is_active: bool, reason: str = None) -> Dict:
        """Toggle house rule active status"""
        logger.info(f"Toggling house rule {rule_name} to {'active' if is_active else 'inactive'}")
        try:
            result = self.crud.toggle_house_rule(rule_name, is_active, reason)
            
            return {
                "house_rule": rule_name,
                "is_active": is_active,
                "summary": f"Set house rule {rule_name} to {'active' if is_active else 'inactive'}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Campaign NPCs (3 operations)
    async def get_campaign_npcs(self) -> Dict:
        """Get all campaign NPCs"""
        logger.info("Getting campaign NPCs")
        try:
            result = self.crud.get_campaign_npcs()
            
            return {
                "npcs": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} campaign NPCs"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_campaign_npc(self, npc_name: str, npc_type: str = None, role: str = None,
                              stats: Dict = None, notes: str = None, reason: str = None) -> Dict:
        """Add campaign NPC"""
        logger.info(f"Adding campaign NPC {npc_name}")
        try:
            result = self.crud.add_campaign_npc(
                {
                    "npc_name": npc_name,
                    "npc_type": npc_type,
                    "role": role,
                    "stats": stats or {},
                    "notes": notes
                },
                reason
            )
            
            return {
                "npc_added": npc_name,
                "npc_type": npc_type,
                "role": role,
                "summary": f"Added campaign NPC {npc_name}" + (f" ({role})" if role else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_campaign_npc(self, npc_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update campaign NPC"""
        logger.info(f"Updating campaign NPC {npc_name}")
        try:
            result = self.crud.update_campaign_npc(npc_name, updates, reason)
            
            return {
                "npc": npc_name,
                "updates": updates,
                "summary": f"Updated campaign NPC {npc_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Audit (1 operation)
    async def get_audit_log(self, character_name: str = None, limit: int = 100) -> Dict:
        """Get audit log entries"""
        logger.info(f"Getting audit log" + (f" for {character_name}" if character_name else ""))
        try:
            character_id = None
            if character_name:
                try:
                    character = self.crud.get_character_by_street_name(character_name)
                    character_id = character['id']
                except ValueError:
                    character = self.crud.get_character_by_given_name(character_name)
                    character_id = character['id']
            
            result = self.crud.get_audit_log(character_id, limit)
            
            return {
                "character": character_name,
                "audit_entries": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} audit log entries" + (f" for {character_name}" if character_name else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== PHASE 6: CHARACTER MANAGEMENT ==========
    
    # Character CRUD (3 operations)
    async def create_character(self, street_name: str, given_name: str = None,
                              archetype: str = None, metatype: str = "Human",
                              attributes: Dict = None, reason: str = None) -> Dict:
        """Create new character"""
        logger.info(f"Creating character {street_name}")
        try:
            result = self.crud.create_character(
                {
                    "street_name": street_name,
                    "given_name": given_name,
                    "archetype": archetype,
                    "metatype": metatype,
                    "body": attributes.get('body', 1) if attributes else 1,
                    "quickness": attributes.get('quickness', 1) if attributes else 1,
                    "strength": attributes.get('strength', 1) if attributes else 1,
                    "charisma": attributes.get('charisma', 1) if attributes else 1,
                    "intelligence": attributes.get('intelligence', 1) if attributes else 1,
                    "willpower": attributes.get('willpower', 1) if attributes else 1,
                    "essence": attributes.get('essence', 6.0) if attributes else 6.0,
                    "magic": attributes.get('magic', 0) if attributes else 0,
                    "reaction": attributes.get('reaction', 1) if attributes else 1
                },
                reason
            )
            
            return {
                "character_created": street_name,
                "character_id": result['id'],
                "metatype": metatype,
                "archetype": archetype,
                "summary": f"Created character {street_name}" + (f" ({archetype})" if archetype else "")
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_character_info(self, character_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update character basic info"""
        logger.info(f"Updating character info for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_character_info(character['id'], updates, reason)
            
            return {
                "character": character_name,
                "updates": updates,
                "summary": f"Updated character info for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def delete_character(self, character_name: str, reason: str = None) -> Dict:
        """Delete character (soft delete)"""
        logger.info(f"Deleting character {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.delete_character(character['id'], reason)
            
            return {
                "character_deleted": character_name,
                "summary": f"Deleted character {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # Character Updates (2 operations)
    async def update_attribute(self, character_name: str, attribute_name: str, new_value: int, reason: str = None) -> Dict:
        """Update character attribute"""
        logger.info(f"Updating {attribute_name} to {new_value} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_attribute(character['id'], attribute_name, new_value, reason)
            
            return {
                "character": character_name,
                "attribute": attribute_name,
                "new_value": new_value,
                "summary": f"Updated {attribute_name} to {new_value} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_derived_stats(self, character_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update derived stats (initiative, condition monitor, etc.)"""
        logger.info(f"Updating derived stats for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_derived_stats(character['id'], updates, reason)
            
            return {
                "character": character_name,
                "updates": updates,
                "summary": f"Updated derived stats for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== PHASE 1: CORE CHARACTER DATA OPERATIONS ==========
    
    async def get_character(self, character_name: str) -> Dict:
        """Get full character sheet with all related data"""
        logger.info(f"Getting character {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            char_id = character['id']
            
            # Fetch all related data
            character['skills'] = self.crud.get_skills(char_id)
            character['spells'] = self.crud.get_spells(char_id)
            character['gear'] = self.crud.get_gear(char_id)
            character['cyberware'] = self.crud.get_character_cyberware(char_id)
            character['bioware'] = self.crud.get_character_bioware(char_id)
            character['contacts'] = self.crud.get_contacts(char_id)
            character['vehicles'] = self.crud.get_vehicles(char_id)
            character['cyberdecks'] = self.crud.get_cyberdecks(char_id)
            character['spirits'] = self.crud.get_spirits(char_id)
            character['foci'] = self.crud.get_foci(char_id)
            character['powers'] = self.crud.get_powers(char_id)
            character['edges_flaws'] = self.crud.get_edges_flaws(char_id)
            character['relationships'] = self.crud.get_relationships(char_id)
            character['active_effects'] = self.crud.get_active_effects(char_id)
            character['modifiers'] = self.crud.get_modifiers(char_id)
            
            return {
                "character": character_name,
                "data": character,
                "summary": f"Retrieved character {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_character_skill(self, character_name: str, skill_name: str) -> Dict:
        """Get specific skill rating"""
        logger.info(f"Getting skill {skill_name} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            skills = self.crud.get_skills(character['id'])
            skill = next((s for s in skills if s['skill_name'].lower() == skill_name.lower()), None)
            
            if not skill:
                return {"error": f"Skill '{skill_name}' not found for {character_name}"}
            
            return {
                "character": character_name,
                "skill": skill_name,
                "base_rating": skill['base_rating'],
                "current_rating": skill['current_rating'],
                "specialization": skill.get('specialization'),
                "summary": f"{character_name} has {skill_name} at rating {skill['current_rating']}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_skills(self, character_name: str) -> Dict:
        """Get all character skills"""
        logger.info(f"Getting skills for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_skills(character['id'])
            
            return {
                "character": character_name,
                "skills": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} skills for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_skill(self, character_name: str, skill_name: str, base_rating: int, 
                       specialization: str = None, skill_type: str = None, reason: str = None) -> Dict:
        """Add a new skill to character"""
        logger.info(f"Adding skill {skill_name} ({base_rating}) to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_skill(
                character['id'],
                {
                    "skill_name": skill_name,
                    "base_rating": base_rating,
                    "specialization": specialization,
                    "skill_type": skill_type
                },
                reason
            )
            
            return {
                "character": character_name,
                "skill_added": skill_name,
                "rating": base_rating,
                "specialization": specialization,
                "summary": f"Added skill {skill_name} ({base_rating}) to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def improve_skill(self, character_name: str, skill_name: str, new_rating: int, reason: str = None) -> Dict:
        """Improve a skill rating"""
        logger.info(f"Improving {skill_name} to {new_rating} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.improve_skill(character['id'], skill_name, new_rating, reason)
            
            return {
                "character": character_name,
                "skill": skill_name,
                "new_rating": new_rating,
                "summary": f"Improved {skill_name} to {new_rating} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_specialization(self, character_name: str, skill_name: str, specialization: str, reason: str = None) -> Dict:
        """Add specialization to a skill"""
        logger.info(f"Adding specialization '{specialization}' to {skill_name} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_specialization(character['id'], skill_name, specialization, reason)
            
            return {
                "character": character_name,
                "skill": skill_name,
                "specialization": specialization,
                "summary": f"Added specialization '{specialization}' to {skill_name} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_skill(self, character_name: str, skill_name: str, reason: str = None) -> Dict:
        """Remove a skill from character"""
        logger.info(f"Removing skill {skill_name} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_skill(character['id'], skill_name, reason)
            
            return {
                "character": character_name,
                "skill_removed": skill_name,
                "summary": f"Removed skill {skill_name} from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_spells(self, character_name: str) -> Dict:
        """Get all character spells"""
        logger.info(f"Getting spells for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_spells(character['id'])
            
            return {
                "character": character_name,
                "spells": result,
                "count": len(result),
                "summary": f"Retrieved {len(result)} spells for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_spell(self, character_name: str, spell_name: str, learned_force: int,
                       spell_category: str = None, spell_type: str = "mana", reason: str = None) -> Dict:
        """Add a new spell to character"""
        logger.info(f"Adding spell {spell_name} (Force {learned_force}) to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_spell(
                character['id'],
                {
                    "spell_name": spell_name,
                    "learned_force": learned_force,
                    "spell_category": spell_category,
                    "spell_type": spell_type
                },
                reason
            )
            
            return {
                "character": character_name,
                "spell_added": spell_name,
                "force": learned_force,
                "category": spell_category,
                "summary": f"Added spell {spell_name} (Force {learned_force}) to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_spell(self, character_name: str, spell_name: str, learned_force: int = None,
                          spell_category: str = None, reason: str = None) -> Dict:
        """Update spell details"""
        logger.info(f"Updating spell {spell_name} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            updates = {}
            if learned_force is not None:
                updates['learned_force'] = learned_force
            if spell_category is not None:
                updates['spell_category'] = spell_category
            
            result = self.crud.update_spell(character['id'], spell_name, updates, reason)
            
            return {
                "character": character_name,
                "spell": spell_name,
                "updates": updates,
                "summary": f"Updated spell {spell_name} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_spell(self, character_name: str, spell_name: str, reason: str = None) -> Dict:
        """Remove a spell from character"""
        logger.info(f"Removing spell {spell_name} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_spell(character['id'], spell_name, reason)
            
            return {
                "character": character_name,
                "spell_removed": spell_name,
                "summary": f"Removed spell {spell_name} from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def get_gear(self, character_name: str, gear_type: str = None) -> Dict:
        """Get character gear"""
        logger.info(f"Getting gear for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.get_gear(character['id'], gear_type)
            
            return {
                "character": character_name,
                "gear": result,
                "count": len(result),
                "gear_type": gear_type,
                "summary": f"Retrieved {len(result)} gear items for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_gear(self, character_name: str, gear_name: str, gear_type: str = "equipment",
                      quantity: int = 1, reason: str = None) -> Dict:
        """Add gear to character"""
        logger.info(f"Adding {quantity}x {gear_name} to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_gear(
                character['id'],
                {
                    "gear_name": gear_name,
                    "gear_type": gear_type,
                    "quantity": quantity
                },
                reason
            )
            
            return {
                "character": character_name,
                "gear_added": gear_name,
                "quantity": quantity,
                "gear_type": gear_type,
                "summary": f"Added {quantity}x {gear_name} to {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def update_gear_quantity(self, character_name: str, gear_name: str, quantity: int, reason: str = None) -> Dict:
        """Update gear quantity"""
        logger.info(f"Updating {gear_name} quantity to {quantity} for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.update_gear_quantity(character['id'], gear_name, quantity, reason)
            
            return {
                "character": character_name,
                "gear": gear_name,
                "quantity": quantity,
                "summary": f"Updated {gear_name} quantity to {quantity} for {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def remove_gear(self, character_name: str, gear_name: str, reason: str = None) -> Dict:
        """Remove gear from character"""
        logger.info(f"Removing {gear_name} from {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.remove_gear(character['id'], gear_name, reason)
            
            return {
                "character": character_name,
                "gear_removed": gear_name,
                "summary": f"Removed {gear_name} from {character_name}"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def add_nuyen(self, character_name: str, amount: int, reason: str = None) -> Dict:
        """Add nuyen to character's account"""
        logger.info(f"Adding {amount}¥ to {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.add_nuyen(character['id'], amount, reason)
            
            return {
                "character": character_name,
                "nuyen_added": amount,
                "reason": reason,
                "nuyen": result['nuyen'],
                "summary": f"Added {amount:,}¥ to {character_name}. Total: {result['nuyen']:,}¥"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    async def spend_nuyen(self, character_name: str, amount: int, reason: str = None) -> Dict:
        """Spend nuyen from character's account"""
        logger.info(f"Spending {amount}¥ for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.spend_nuyen(character['id'], amount, reason)
            
            return {
                "character": character_name,
                "nuyen_spent": amount,
                "reason": reason,
                "nuyen": result['nuyen'],
                "summary": f"Spent {amount:,}¥ for {character_name}. Remaining: {result['nuyen']:,}¥"
            }
        except ValueError as e:
            return {"error": str(e)}
    
    # ========== SPELLCASTING ==========
    
    async def cast_spell(self, character_name: str, spell_name: str, force: int = None, reason: str = None) -> Dict:
        """
        Cast a spell with drain calculation
        
        Args:
            character_name: Character casting the spell
            spell_name: Name of spell to cast
            force: Force to cast at (None = use learned force)
            reason: Optional reason for audit log
        """
        logger.info(f"{character_name} casting {spell_name}" + (f" at Force {force}" if force else ""))
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            # Create spellcasting engine with database connection
            conn = psycopg.connect(
                host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
                port=int(os.getenv('POSTGRES_PORT', '5434')),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'),
                dbname=os.getenv('POSTGRES_DB')
            )
            
            engine = SpellcastingEngine(conn)
            result = engine.cast_spell(character['id'], spell_name, force)
            conn.close()
            
            if 'error' in result:
                return result
            
            # Log to audit if reason provided
            if reason:
                self.crud.log_audit(
                    character['id'],
                    'cast_spell',
                    {
                        'spell_name': spell_name,
                        'force': result['force'],
                        'drain_taken': result['drain_resistance']['damage_taken'],
                        'damage_code': result['drain_calculation']['damage_code']
                    },
                    reason
                )
            
            return {
                "character": character_name,
                **result
            }
        except ValueError as e:
            return {"error": str(e)}
