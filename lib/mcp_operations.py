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
    
    async def get_character_skill(self, character_name: str, skill_name: str) -> Dict:
        """Get character skill rating using CRUD API"""
        logger.info(f"[MCP] get_character_skill: character='{character_name}', skill='{skill_name}'")
        try:
            # Look up character by street name
            logger.debug(f"[MCP] Looking up character by street name: {character_name}")
            character = self.crud.get_character_by_street_name(character_name)
            char_id = character['id']
            logger.debug(f"[MCP] Found character ID: {char_id}")
            
            # Get skills
            logger.debug(f"[MCP] Fetching skills for character ID: {char_id}")
            skills = self.crud.get_skills(char_id)
            logger.debug(f"[MCP] Retrieved {len(skills)} skills")
            
            # Find the requested skill (case-insensitive)
            skill = next((s for s in skills if s['skill_name'].lower() == skill_name.lower()), None)
            
            if not skill:
                return {
                    "error": f"Skill '{skill_name}' not found for {character_name}",
                    "skill_rating": 0,
                    "attribute_rating": 0
                }
            
            # Determine which attribute the skill uses
            skill_attributes = {
                'street etiquette': 'charisma',
                'firearms': 'quickness',
                'unarmed combat': 'quickness',
                'sorcery': 'willpower',
                # Add more mappings as needed
            }
            
            attribute_name = skill_attributes.get(skill_name.lower(), 'charisma')
            attribute_rating = character.get(f'current_{attribute_name}', 0)
            
            return {
                "character": character_name,
                "skill": skill_name,
                "skill_rating": skill['current_rating'],
                "attribute": attribute_name,
                "attribute_rating": attribute_rating,
                "specialization": skill.get('specialization')
            }
        
        except ValueError as e:
            return {"error": str(e)}
    
    async def calculate_ranged_attack(
        self,
        character_name: str,
        weapon_name: str,
        target_distance: int,
        target_description: str,
        environment: str,
        combat_pool: int = 0
    ) -> Dict:
        """
        Calculate ranged attack using CRUD API
        Pulls character data, modifiers, and weapon modifications
        """
        logger.info(f"Calculating ranged attack for {character_name} with {weapon_name} at {target_distance}m")
        try:
            # Get character
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            char_id = character['id']
            
            # Get firearms skill
            skills = self.crud.get_skills(char_id)
            firearms_skill_data = next((s for s in skills if s['skill_name'].lower() == 'firearms'), None)
            firearms_skill = firearms_skill_data['current_rating'] if firearms_skill_data else 0
            
            # Get weapon from gear
            gear = self.crud.get_gear(char_id, gear_type='weapon')
            weapon = next((g for g in gear if weapon_name.lower() in g['gear_name'].lower()), None)
            
            if not weapon:
                return {"error": f"Weapon '{weapon_name}' not found for {character_name}"}
            
            # Get all modifiers
            modifiers = self.crud.get_modifiers(char_id)
            
            # Process vision enhancements
            vision_enhancements = {}
            for mod in modifiers:
                if mod['modifier_type'] == 'vision':
                    if mod['target_name'] == 'thermographic':
                        vision_enhancements['thermographic'] = 'cybernetic'
                    elif mod['target_name'] == 'lowLight':
                        vision_enhancements['lowLight'] = 'cybernetic'
                    elif mod['target_name'] == 'magnification':
                        vision_enhancements['magnification'] = mod['modifier_value']
            
            # Determine weapon type and range
            weapon_type = "heavy pistol"  # Default
            weapon_name_lower = weapon_name.lower()
            if "alta" in weapon_name_lower or "morrissey" in weapon_name_lower:
                weapon_type = "hold-out pistol"
            elif "predator" in weapon_name_lower or "ares" in weapon_name_lower:
                weapon_type = "heavy pistol"
            elif "alpha" in weapon_name_lower:
                weapon_type = "assault rifle"
            elif "sniper" in weapon_name_lower:
                weapon_type = "sniper rifle"
            
            magnification = vision_enhancements.get("magnification", 0)
            range_cat = CombatModifiers.determine_range(target_distance, weapon_type, magnification)
            
            if not range_cat:
                return {
                    "error": f"Target out of range",
                    "distance": target_distance,
                    "magnification": magnification,
                    "weapon_type": weapon_type
                }
            
            # Parse environment for light level
            light_level = "NORMAL"
            env_lower = environment.lower()
            if "dark" in env_lower or "pitch" in env_lower:
                light_level = "DARK"
            elif "dim" in env_lower or "shadows" in env_lower:
                light_level = "DIM"
            elif "partial" in env_lower or "twilight" in env_lower:
                light_level = "PARTIAL"
            
            # Parse target description
            target_modifier = 0
            target_desc_lower = target_description.lower()
            if "rat" in target_desc_lower or "small" in target_desc_lower:
                target_modifier = 2
            elif "large" in target_desc_lower or "big" in target_desc_lower:
                target_modifier = -1
            
            # Build combat parameters
            params = {
                'weapon': {
                    'smartlink': False,
                    'recoilComp': 0,
                    'gyroStabilization': 0
                },
                'range': range_cat,
                'attacker': {
                    'movement': None,
                    'hasSmartlink': False,
                    'vision': vision_enhancements
                },
                'defender': {
                    'conscious': True,
                    'prone': False,
                    'movement': None,
                    'inMeleeCombat': False
                },
                'situation': {
                    'lightLevel': light_level,
                    'dualWielding': False,
                    'recoil': 0,
                    'calledShot': False,
                    'modifier': target_modifier,
                    'modifierReason': f"Target: {target_description}"
                }
            }
            
            # Calculate base target number
            result = CombatModifiers.calculate_ranged_tn(params)
            
            # Apply combat modifiers from character_modifiers
            combat_mods = [m for m in modifiers if m['modifier_type'] == 'combat' and m['target_name'] == 'ranged_tn']
            total_combat_bonus = sum(m['modifier_value'] for m in combat_mods)
            
            final_tn = max(2, result['finalTN'] + total_combat_bonus)
            
            # Roll dice if combat pool specified
            roll_result = None
            if combat_pool > 0:
                roll_result = DiceRoller.roll_with_target_number(combat_pool, final_tn)
            
            return {
                "character": character_name,
                "weapon": weapon_name,
                "weapon_type": weapon_type,
                "target_distance": target_distance,
                "vision_magnification": magnification,
                "range_category": range_cat,
                "environment": environment,
                "light_level": light_level,
                "target_description": target_description,
                "vision_enhancements": vision_enhancements,
                "combat_modifiers": [
                    {
                        "source": m['source'],
                        "type": m['source_type'],
                        "value": m['modifier_value']
                    }
                    for m in combat_mods
                ],
                "base_tn": result['baseTN'],
                "modifiers": result['modifiers'],
                "combat_bonus": total_combat_bonus,
                "total_modifier": result['totalModifier'] + total_combat_bonus,
                "final_tn": final_tn,
                "combat_pool": combat_pool,
                "roll": {
                    "rolls": roll_result.rolls if roll_result else [],
                    "successes": roll_result.successes if roll_result else 0,
                    "all_ones": roll_result.all_ones if roll_result else False
                } if roll_result else None,
                "breakdown": result['summary']
            }
        
        except ValueError as e:
            return {"error": str(e)}
    
    async def calculate_dice_pool(self, skill: int, attribute: int, modifiers: List[int]) -> Dict:
        """Calculate total dice pool"""
        total_modifiers = sum(modifiers) if modifiers else 0
        pool = skill + attribute + total_modifiers
        
        return {
            "pool": pool,
            "breakdown": f"{skill} (skill) + {attribute} (attribute) + {total_modifiers} (modifiers)",
            "skill": skill,
            "attribute": attribute,
            "modifiers": total_modifiers
        }
    
    async def calculate_target_number(self, situation: str, difficulty: str) -> Dict:
        """Calculate target number for situation"""
        base_tns = {
            'trivial': 2,
            'easy': 4,
            'average': 5,
            'difficult': 6,
            'very_difficult': 8
        }
        
        tn = base_tns.get(difficulty.lower(), 5)
        
        return {
            "target_number": tn,
            "situation": situation,
            "difficulty": difficulty,
            "breakdown": f"Base TN {tn} for {difficulty} task"
        }
    
    async def roll_dice(self, pool: int, target_number: int) -> Dict:
        """Roll dice pool against target number using DiceRoller"""
        result = DiceRoller.roll_with_target_number(pool, target_number)
        
        return {
            "pool": result.pool_size,
            "target_number": result.target_number,
            "rolls": result.rolls,
            "successes": result.successes,
            "result": "success" if result.successes > 0 else "failure",
            "all_ones": result.all_ones,
            "critical_glitch": result.critical_glitch
        }
    
    async def list_characters(self) -> List[Dict]:
        """List all characters using CRUD API"""
        logger.info("Listing all characters")
        return self.crud.list_characters()
    
    async def get_character(self, character_name: str) -> Dict:
        """Get full character data with ALL related data using CRUD API"""
        logger.info(f"Getting full character data for '{character_name}'")
        try:
            # Try street name first
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                # Fall back to given name
                character = self.crud.get_character_by_given_name(character_name)
            
            char_id = character['id']
            
            # Fetch ALL related data using CRUD API
            character['skills'] = self.crud.get_skills(char_id)
            character['gear'] = self.crud.get_gear(char_id)
            character['spells'] = self.crud.get_spells(char_id)
            character['contacts'] = self.crud.get_contacts(char_id)
            character['vehicles'] = self.crud.get_vehicles(char_id)
            character['cyberdecks'] = self.crud.get_cyberdecks(char_id)
            character['foci'] = self.crud.get_foci(char_id)
            character['spirits'] = self.crud.get_spirits(char_id)
            character['edges_flaws'] = self.crud.get_edges_flaws(char_id)
            character['powers'] = self.crud.get_powers(char_id)
            character['relationships'] = self.crud.get_relationships(char_id)
            character['active_effects'] = self.crud.get_active_effects(char_id)
            character['modifiers'] = self.crud.get_modifiers(char_id)
            
            return character
        
        except ValueError:
            # Get list of available characters for better error message
            characters = self.crud.list_characters()
            char_list = [f"{c['name']} ({c['street_name']})" if c.get('street_name') else c['name'] 
                        for c in characters]
            
            return {
                "error": f"Character '{character_name}' not found",
                "available_characters": char_list,
                "hint": "Try using the character's street name or full name"
            }
    
    async def cast_spell(
        self,
        caster_name: str,
        spell_name: str,
        force: int,
        target_name: Optional[str],
        spell_pool_dice: int,
        drain_pool_dice: int
    ) -> Dict:
        """
        Cast spell using CRUD API
        All spell data comes from character_spells table via CRUD
        """
        logger.info(f"Casting spell: {caster_name} casts {spell_name} at Force {force}")
        import time
        start_time = time.time()
        timings = {}
        
        try:
            # Get caster character
            query_start = time.time()
            try:
                caster = self.crud.get_character_by_street_name(caster_name)
            except ValueError:
                caster = self.crud.get_character_by_given_name(caster_name)
            timings['get_character'] = time.time() - query_start
            
            char_id = caster['id']
            magic_rating = caster['current_magic']
            
            if not magic_rating or magic_rating == 0:
                return {"error": f"{caster_name} has no magic rating and cannot cast spells"}
            
            # Validate Magic Pool split
            total_pool_used = spell_pool_dice + drain_pool_dice
            if total_pool_used > magic_rating:
                return {
                    "error": f"Magic Pool exceeded: {total_pool_used} dice requested but only {magic_rating} available",
                    "magic_rating": magic_rating,
                    "spell_pool_dice": spell_pool_dice,
                    "drain_pool_dice": drain_pool_dice,
                    "hint": "Reduce spell_pool_dice and/or drain_pool_dice to total <= Magic rating"
                }
            
            # Get spells using CRUD API
            query_start = time.time()
            spells = self.crud.get_spells(char_id)
            spell_data = next((s for s in spells if s['spell_name'].lower() == spell_name.lower()), None)
            timings['check_spell'] = time.time() - query_start
            
            if not spell_data:
                return {
                    "error": f"{caster_name} does not know the spell '{spell_name}'",
                    "hint": "Add spell to character_spells table first"
                }
            
            spell_category = spell_data['spell_category']
            drain_modifier = spell_data.get('drain_modifier', 0)
            learned_force = spell_data.get('learned_force')
            
            # Validate force against learned_force
            if learned_force and force > learned_force:
                return {
                    "error": f"Cannot cast {spell_name} at Force {force}",
                    "learned_force": learned_force,
                    "requested_force": force,
                    "hint": f"{caster_name} knows {spell_name} at Force {learned_force}. You can cast at Force {learned_force} or lower, but not higher."
                }
            
            # Get Sorcery skill using CRUD API
            query_start = time.time()
            skills = self.crud.get_skills(char_id)
            sorcery_skill_data = next((s for s in skills if s['skill_name'].lower() == 'sorcery'), None)
            sorcery_skill = sorcery_skill_data['current_rating'] if sorcery_skill_data else 0
            timings['get_sorcery'] = time.time() - query_start
            
            if sorcery_skill == 0:
                return {"error": f"{caster_name} has no Sorcery skill"}
            
            # Check for totem bonus/penalty (direct SQL for totem lookup)
            query_start = time.time()
            totem_bonus = 0
            totem_penalty = 0
            totem_name = caster.get('totem')
            
            if totem_name:
                cursor = self.crud.conn.cursor()
                cursor.execute("""
                    SELECT favored_categories, opposed_categories, bonus_dice, penalty_dice
                    FROM totems
                    WHERE LOWER(totem_name) = LOWER(%s)
                """, (totem_name,))
                
                result = cursor.fetchone()
                
                if result:
                    # Convert tuple to dict manually (same pattern as comprehensive_crud.py)
                    cols = [d[0] for d in cursor.description]
                    totem_data = dict(zip(cols, result))
                    
                    favored_categories = totem_data['favored_categories'] or []
                    opposed_categories = totem_data['opposed_categories'] or []
                    
                    # Check if spell category is favored (+2 dice)
                    if any(spell_category.lower() == cat.lower() for cat in favored_categories):
                        totem_bonus = totem_data['bonus_dice'] or 2
                    
                    # Check if spell category is opposed (-2 dice)
                    if any(spell_category.lower() == cat.lower() for cat in opposed_categories):
                        totem_penalty = totem_data['penalty_dice'] or -2
                
                cursor.close()
            
            timings['check_totem'] = time.time() - query_start
            
            # Get foci using CRUD API
            query_start = time.time()
            foci = self.crud.get_foci(char_id)
            
            # Find applicable focus
            focus_bonus = 0
            focus_name = None
            focus_force = 0
            
            for focus in foci:
                # Focus must be bonded and force >= spell force
                if focus.get('bonded') and focus['force'] >= force:
                    # Check if focus applies to this spell
                    if focus.get('specific_spell'):
                        if focus['specific_spell'].lower() == spell_name.lower():
                            focus_bonus = focus.get('bonus_dice', 0)
                            focus_name = focus['focus_name']
                            focus_force = focus['force']
                            break
                    elif focus.get('spell_category'):
                        if focus['spell_category'].lower() == spell_category.lower():
                            focus_bonus = focus.get('bonus_dice', 0)
                            focus_name = focus['focus_name']
                            focus_force = focus['force']
                            break
            
            timings['get_foci'] = time.time() - query_start
            
            # Calculate dice pools
            spell_dice_pool = sorcery_skill + spell_pool_dice + totem_bonus + totem_penalty + focus_bonus
            drain_dice_pool = caster['current_willpower'] + drain_pool_dice
            
            # Target Number = Force of spell
            target_number = force
            
            # Drain calculation (Shadowrun 2nd Ed)
            base_drain = force // 2
            total_drain = base_drain + drain_modifier
            drain_code = "M" if force <= 6 else "S"
            
            # Roll spellcasting test
            roll_start = time.time()
            spell_result = DiceRoller.roll_with_target_number(spell_dice_pool, target_number)
            drain_result = DiceRoller.roll_with_target_number(drain_dice_pool, total_drain)
            timings['dice_rolls'] = time.time() - roll_start
            
            # Calculate damage taken
            drain_damage = max(0, total_drain - drain_result.successes)
            spell_success = spell_result.successes > 0
            
            timings['total'] = time.time() - start_time
            
            return {
                "caster": caster_name,
                "spell": spell_name,
                "spell_category": spell_category,
                "force": force,
                "target": target_name,
                
                # Magic Pool
                "magic_rating": magic_rating,
                "spell_pool_dice": spell_pool_dice,
                "drain_pool_dice": drain_pool_dice,
                "pool_remaining": magic_rating - total_pool_used,
                
                # Spellcasting
                "sorcery_skill": sorcery_skill,
                "totem_bonus": totem_bonus,
                "totem_penalty": totem_penalty,
                "totem_name": totem_name,
                "focus_bonus": focus_bonus,
                "focus_name": focus_name,
                "focus_force": focus_force,
                "spell_dice_pool": spell_dice_pool,
                "target_number": target_number,
                "spell_roll": {
                    "rolls": spell_result.rolls,
                    "successes": spell_result.successes,
                    "result": "success" if spell_success else "failure"
                },
                
                # Drain
                "drain": {
                    "base_level": base_drain,
                    "modifier": drain_modifier,
                    "total_level": total_drain,
                    "code": drain_code,
                    "resist_dice": drain_dice_pool,
                    "resist_roll": {
                        "rolls": drain_result.rolls,
                        "successes": drain_result.successes
                    },
                    "damage_taken": drain_damage,
                    "damage_type": drain_code
                },
                
                "summary": f"{caster_name} casts {spell_name} at Force {force}. " +
                          (f"Totem {totem_name} grants +{totem_bonus} dice. " if totem_bonus > 0 else "") +
                          (f"Totem {totem_name} imposes {totem_penalty} dice penalty. " if totem_penalty < 0 else "") +
                          (f"Using {focus_name} (Force {focus_force}). " if focus_name else "") +
                          f"Spell: {spell_dice_pool}d6 vs TN {target_number} = {spell_result.successes} successes. " +
                          f"Drain: {drain_dice_pool}d6 vs {total_drain}{drain_code} = {drain_result.successes} successes, {drain_damage} damage taken.",
                
                # Performance timing
                "performance": {
                    "timings_ms": {k: round(v * 1000, 2) for k, v in timings.items()},
                    "total_ms": round(timings['total'] * 1000, 2)
                }
            }
        
        except ValueError as e:
            return {"error": str(e)}
