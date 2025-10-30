#!/usr/bin/env python3
"""
Spellcasting mechanics for Shadowrun 2nd Edition
Includes drain formula parsing and spell casting
"""

import re
import logging
from typing import Dict, Optional, Tuple
from lib.dice_roller import DiceRoller

logger = logging.getLogger(__name__)

class DrainFormulaParser:
    """Parse and calculate drain from spell formulas"""
    
    # Damage code mapping
    DAMAGE_CODES = {
        'L': 'Light',
        'M': 'Moderate', 
        'S': 'Serious',
        'D': 'Deadly'
    }
    
    @staticmethod
    def parse_formula(formula: str, force: int) -> Tuple[int, str]:
        """
        Parse drain formula and calculate drain value
        
        Args:
            formula: Drain formula string (e.g., "(F/2)S", "[(F/2)+1]D")
            force: Force at which spell is being cast
            
        Returns:
            Tuple of (drain_value, damage_code)
            
        Examples:
            parse_formula("(F/2)S", 6) -> (3, "S")
            parse_formula("[(F/2)+1]D", 6) -> (4, "D")
            parse_formula("[(F/2)-1]M", 6) -> (2, "M")
        """
        # Extract damage code (last character)
        damage_code = formula[-1]
        if damage_code not in DrainFormulaParser.DAMAGE_CODES:
            raise ValueError(f"Invalid damage code: {damage_code}")
        
        # Extract formula part (everything except last character)
        formula_part = formula[:-1]
        
        # Remove brackets if present
        formula_part = formula_part.strip('[]')
        
        # Replace F with actual force value
        formula_part = formula_part.replace('F', str(force))
        
        # Evaluate the expression
        try:
            # Use integer division for F/2
            drain_value = int(eval(formula_part))
        except Exception as e:
            raise ValueError(f"Invalid drain formula: {formula}") from e
        
        return drain_value, damage_code
    
    @staticmethod
    def format_drain(drain_value: int, damage_code: str) -> str:
        """Format drain as readable string"""
        damage_name = DrainFormulaParser.DAMAGE_CODES.get(damage_code, damage_code)
        return f"{drain_value}{damage_code} ({damage_name})"


class SpellcastingEngine:
    """Handle spellcasting mechanics"""
    
    def __init__(self, db_connection):
        """Initialize with database connection"""
        self.conn = db_connection
        self.dice_roller = DiceRoller()
        self.parser = DrainFormulaParser()
    
    def get_spell_info(self, spell_name: str) -> Optional[Dict]:
        """Look up spell in master_spells table"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT spell_name, spell_class, spell_type, duration, drain_formula,
                   book_reference, description, is_house_rule
            FROM master_spells
            WHERE LOWER(spell_name) = LOWER(%s)
        """, (spell_name,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return None
        
        return {
            'spell_name': result[0],
            'spell_class': result[1],
            'spell_type': result[2],
            'duration': result[3],
            'drain_formula': result[4],
            'book_reference': result[5],
            'description': result[6],
            'is_house_rule': result[7]
        }
    
    def get_character_spell(self, character_id: str, spell_name: str) -> Optional[Dict]:
        """Get character's learned spell"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT cs.spell_name, cs.force, cs.drain_code, cs.master_spell_id,
                   ms.drain_formula, ms.spell_class
            FROM character_spells cs
            LEFT JOIN master_spells ms ON cs.master_spell_id = ms.id
            WHERE cs.character_id = %s AND LOWER(cs.spell_name) = LOWER(%s)
            AND cs.deleted_at IS NULL
        """, (character_id, spell_name))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            return None
        
        return {
            'spell_name': result[0],
            'learned_force': result[1],
            'drain_code': result[2],
            'master_spell_id': result[3],
            'drain_formula': result[4],
            'spell_class': result[5]
        }
    
    def get_totem_modifier(self, character_id: str, spell_class: str) -> int:
        """
        Get totem modifier for spell class
        
        Returns:
            +2 if spell class is favored by totem
            -2 if spell class is opposed by totem
            0 if no totem or neutral
        """
        cursor = self.conn.cursor()
        
        # Get character's totem
        cursor.execute("""
            SELECT totem FROM characters WHERE id = %s
        """, (character_id,))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            cursor.close()
            return 0
        
        totem_name = result[0]
        
        # Look up totem modifiers
        cursor.execute("""
            SELECT favored_categories, opposed_categories, bonus_dice, penalty_dice
            FROM totems
            WHERE LOWER(totem_name) = LOWER(%s)
        """, (totem_name,))
        
        totem_data = cursor.fetchone()
        cursor.close()
        
        if not totem_data:
            return 0
        
        favored, opposed, bonus, penalty = totem_data
        
        # Check if spell class is favored (case-insensitive)
        if favored and any(spell_class.lower() == cat.lower() for cat in favored):
            return bonus or 2
        
        # Check if spell class is opposed (case-insensitive)
        if opposed and any(spell_class.lower() == cat.lower() for cat in opposed):
            return penalty or -2
        
        return 0
    
    def calculate_drain(self, drain_formula: str, force: int, totem_modifier: int = 0) -> Dict:
        """
        Calculate drain for spell
        
        Returns dict with:
            - drain_value: Base drain value
            - damage_code: Damage code (L/M/S/D)
            - modified_drain: Drain after totem modifier
            - totem_modifier: Applied modifier
        """
        drain_value, damage_code = self.parser.parse_formula(drain_formula, force)
        
        # Apply totem modifier (reduces drain for favored, increases for opposed)
        modified_drain = max(0, drain_value - totem_modifier)
        
        return {
            'drain_value': drain_value,
            'damage_code': damage_code,
            'modified_drain': modified_drain,
            'totem_modifier': totem_modifier,
            'drain_string': self.parser.format_drain(modified_drain, damage_code)
        }
    
    def roll_drain_resistance(self, character_id: str, drain_value: int, damage_code: str) -> Dict:
        """
        Roll drain resistance
        
        Uses Willpower for drain resistance
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT current_willpower, current_magic
            FROM characters
            WHERE id = %s
        """, (character_id,))
        
        result = cursor.fetchone()
        cursor.close()
        
        if not result:
            raise ValueError(f"Character {character_id} not found")
        
        willpower, magic = result
        
        # Drain resistance pool = Willpower (+ Magic for some traditions)
        # For now, using Willpower only (standard SR2 rule)
        resistance_pool = willpower
        
        # Target number is drain value
        tn = drain_value
        
        # Roll resistance
        roll_result = self.dice_roller.roll_with_target_number(resistance_pool, tn)
        
        # Calculate damage taken
        damage_taken = max(0, drain_value - roll_result.successes)
        
        return {
            'resistance_pool': resistance_pool,
            'target_number': tn,
            'successes': roll_result.successes,
            'damage_taken': damage_taken,
            'damage_code': damage_code,
            'roll_details': {
                'rolls': roll_result.rolls,
                'successes': roll_result.successes,
                'all_ones': roll_result.all_ones
            }
        }
    
    def cast_spell(self, character_id: str, spell_name: str, force: int = None) -> Dict:
        """
        Cast a spell
        
        Args:
            character_id: Character casting the spell
            spell_name: Name of spell to cast
            force: Force to cast at (None = use learned force)
            
        Returns:
            Dict with casting results including drain
        """
        # Get character's spell
        char_spell = self.get_character_spell(character_id, spell_name)
        if not char_spell:
            return {"error": f"Character does not know spell '{spell_name}'"}
        
        # Determine force to use
        if force is None:
            if char_spell['learned_force'] is None:
                return {"error": f"Must specify force for variable-force spell '{spell_name}'"}
            force = char_spell['learned_force']
        
        # Get drain formula (from master spell or cached)
        drain_formula = char_spell['drain_formula'] or char_spell['drain_code']
        if not drain_formula:
            return {"error": f"No drain formula found for spell '{spell_name}'"}
        
        # Get totem modifier
        totem_modifier = self.get_totem_modifier(character_id, char_spell['spell_class'])
        
        # Calculate drain
        drain_calc = self.calculate_drain(drain_formula, force, totem_modifier)
        
        # Roll drain resistance
        resistance = self.roll_drain_resistance(
            character_id,
            drain_calc['modified_drain'],
            drain_calc['damage_code']
        )
        
        return {
            'spell_name': spell_name,
            'force': force,
            'learned_force': char_spell['learned_force'],
            'drain_formula': drain_formula,
            'drain_calculation': drain_calc,
            'drain_resistance': resistance,
            'summary': (
                f"Cast {spell_name} at Force {force}. "
                f"Drain: {drain_calc['drain_string']} "
                f"(resisted {resistance['successes']} successes, "
                f"took {resistance['damage_taken']} {drain_calc['damage_code']} damage)"
            )
        }
    
    def get_sustained_spells(self, character_id: str) -> list:
        """
        Get all spells being sustained by a character
        
        Returns list of sustained spell info
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT source, spell_force, character_id
            FROM character_modifiers
            WHERE sustained_by = %s 
            AND is_sustained = true 
            AND source_type = 'spell'
            AND deleted_at IS NULL
        """, (character_id,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'spell_name': row[0],
                'force': row[1],
                'target_character_id': row[2]
            })
        
        cursor.close()
        return results
    
    def calculate_sustaining_penalty(self, character_id: str) -> int:
        """
        Calculate dice pool penalty for sustained spells
        
        Returns: -2 per sustained spell
        """
        sustained = self.get_sustained_spells(character_id)
        return len(sustained) * -2
    
    def drop_sustained_spell(self, character_id: str, spell_name: str) -> bool:
        """
        End a sustained spell (soft delete all related modifiers)
        
        Returns: True if spell was found and dropped
        """
        cursor = self.conn.cursor()
        
        # Soft delete all modifiers for this sustained spell
        cursor.execute("""
            UPDATE character_modifiers
            SET deleted_at = CURRENT_TIMESTAMP
            WHERE sustained_by = %s
            AND source = %s
            AND is_sustained = true
            AND source_type = 'spell'
            AND deleted_at IS NULL
        """, (character_id, spell_name))
        
        rows_affected = cursor.rowcount
        self.conn.commit()
        cursor.close()
        
        return rows_affected > 0
