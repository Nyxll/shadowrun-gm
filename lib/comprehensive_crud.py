#!/usr/bin/env python3
"""
Comprehensive CRUD API with Audit Logging
Complete operations for all character and campaign data
"""
import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
import psycopg
from psycopg.types.json import Jsonb

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ComprehensiveCRUD:
    """Complete CRUD API with audit logging"""
    
    def __init__(self, user_id: str, user_type: str = 'USER'):
        self.user_id = user_id
        self.user_type = user_type
        logger.info(f"Initializing CRUD API for user {user_id} (type: {user_type})")
        self.conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
            port=int(os.getenv('POSTGRES_PORT', '5434')),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
        logger.info("Database connection established")
    
    # ========== CHARACTER CRUD ==========
    def create_character(self, data: Dict, reason: str = None) -> Dict:
        """Create a new character"""
        self._audit(reason)
        logger.info(f"Creating character: {data.get('name')}")
        cur = self.conn.cursor()
        
        # Extract attributes - schema uses base_* and current_* prefixes
        attrs = data.get('attributes', {})
        
        # Default values
        body = attrs.get('body', 1)
        quickness = attrs.get('quickness', 1)
        strength = attrs.get('strength', 1)
        charisma = attrs.get('charisma', 1)
        intelligence = attrs.get('intelligence', 1)
        willpower = attrs.get('willpower', 1)
        essence = attrs.get('essence', 6.0)
        magic = attrs.get('magic')
        reaction = attrs.get('reaction', 1)
        
        cur.execute("""
            INSERT INTO characters (
                name, street_name, metatype, archetype, sex, age, height, weight,
                hair, eyes, skin, background, notes,
                base_body, base_quickness, base_strength, base_charisma,
                base_intelligence, base_willpower, base_essence, base_magic, base_reaction,
                current_body, current_quickness, current_strength, current_charisma,
                current_intelligence, current_willpower, current_essence, current_magic, current_reaction,
                nuyen, karma_pool, karma_total, lifestyle, combat_pool, magic_pool, totem
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            ) RETURNING *
        """, (
            data['name'], data.get('street_name'), data.get('metatype', 'Human'),
            data.get('archetype'), data.get('sex'), data.get('age'),
            data.get('height'), data.get('weight'), data.get('hair'),
            data.get('eyes'), data.get('skin'), data.get('background'), data.get('notes'),
            # Base attributes
            body, quickness, strength, charisma, intelligence, willpower, essence, magic, reaction,
            # Current attributes (start same as base)
            body, quickness, strength, charisma, intelligence, willpower, essence, magic, reaction,
            # Other fields
            data.get('nuyen', 0), data.get('karma_pool', 0), data.get('karma_total', 0),
            data.get('lifestyle'), data.get('combat_pool', 0), data.get('magic_pool', 0),
            data.get('totem')
        ))
        
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        logger.info(f"Created character {result['name']} with ID {result['id']}")
        return result
    
    def get_character(self, char_id: str) -> Dict:
        """Get character by UUID"""
        logger.info(f"Getting character by ID: {char_id}")
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM characters WHERE id = %s", (char_id,))
        result = cur.fetchone()
        
        if not result:
            cur.close()
            raise ValueError(f"Character with ID {char_id} not found")
        
        cols = [d[0] for d in cur.description]
        character = dict(zip(cols, result))
        cur.close()
        return character
    
    def update_character(self, char_id: str, updates: Dict, reason: str = None) -> Dict:
        """Update character attributes and basic info"""
        self._audit(reason)
        logger.info(f"Updating character {char_id}")
        
        # Build update query dynamically - schema uses base_* and current_* prefixes
        allowed_fields = [
            'name', 'street_name', 'metatype', 'archetype', 'sex', 'age',
            'height', 'weight', 'hair', 'eyes', 'skin', 'background', 'notes',
            'base_body', 'base_quickness', 'base_strength', 'base_charisma',
            'base_intelligence', 'base_willpower', 'base_essence', 'base_magic', 'base_reaction',
            'current_body', 'current_quickness', 'current_strength', 'current_charisma',
            'current_intelligence', 'current_willpower', 'current_essence', 'current_magic', 'current_reaction',
            'nuyen', 'karma_pool', 'karma_total', 'lifestyle', 'combat_pool', 'magic_pool', 'totem'
        ]
        
        sets = [f"{f} = %s" for f in allowed_fields if f in updates]
        if not sets:
            raise ValueError("No valid fields to update")
        
        params = [updates[f] for f in allowed_fields if f in updates] + [char_id]
        
        cur = self.conn.cursor()
        cur.execute(f"UPDATE characters SET {', '.join(sets)} WHERE id = %s RETURNING *", params)
        result = cur.fetchone()
        
        if not result:
            raise ValueError(f"Character {char_id} not found")
        
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        logger.info(f"Updated character {char_id}")
        return result
    
    def delete_character(self, char_id: str, reason: str = None) -> Dict:
        """Delete a character (hard delete - use with caution!)"""
        self._audit(reason)
        logger.warning(f"Deleting character {char_id}")
        
        cur = self.conn.cursor()
        cur.execute("DELETE FROM characters WHERE id = %s RETURNING *", (char_id,))
        result = cur.fetchone()
        
        if not result:
            raise ValueError(f"Character {char_id} not found")
        
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        logger.info(f"Deleted character {char_id}")
        return result
    
    def _audit(self, reason: str = None):
        """Set audit context"""
        cur = self.conn.cursor()
        cur.execute(f"SET app.current_user_id = '{self.user_id}'")
        cur.execute(f"SET app.current_user_type = '{self.user_type}'")
        if reason:
            cur.execute(f"SET app.change_reason = '{reason}'")
        cur.close()
    
    def close(self):
        if self.conn:
            self.conn.close()
    
    # ========== CHARACTER LOOKUP ==========
    def get_character_by_name(self, name: str, campaign_id: str = None) -> Dict:
        """
        Look up character by name (optionally scoped to campaign)
        Returns character with UUID for use in other operations
        """
        logger.info(f"Looking up character by name: {name}")
        sql = "SELECT * FROM characters WHERE name = %s"
        params = [name]
        
        if campaign_id:
            sql += """ AND id IN (
                SELECT character_id FROM character_campaign_links 
                WHERE campaign_id = %s
            )"""
            params.append(campaign_id)
        
        sql += " LIMIT 1"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()
        
        if not result:
            cur.close()
            raise ValueError(f"Character '{name}' not found" + (f" in campaign {campaign_id}" if campaign_id else ""))
        
        cols = [d[0] for d in cur.description]
        character = dict(zip(cols, result))
        cur.close()
        return character
    
    def get_character_by_street_name(self, street_name: str, campaign_id: str = None) -> Dict:
        """
        Look up character by street name (optionally scoped to campaign)
        Street names are typically unique identifiers for shadowrunners
        Returns character with UUID for use in other operations
        """
        sql = "SELECT * FROM characters WHERE street_name = %s"
        params = [street_name]
        
        if campaign_id:
            sql += """ AND id IN (
                SELECT character_id FROM character_campaign_links 
                WHERE campaign_id = %s
            )"""
            params.append(campaign_id)
        
        sql += " LIMIT 1"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()
        
        if not result:
            cur.close()
            raise ValueError(f"Character with street name '{street_name}' not found" + (f" in campaign {campaign_id}" if campaign_id else ""))
        
        cols = [d[0] for d in cur.description]
        character = dict(zip(cols, result))
        cur.close()
        return character
    
    def get_character_by_given_name(self, given_name: str, campaign_id: str = None) -> Dict:
        """
        Look up character by given name (optionally scoped to campaign)
        WARNING: Given names may not be unique!
        Returns character with UUID for use in other operations
        """
        sql = "SELECT * FROM characters WHERE name = %s"
        params = [given_name]
        
        if campaign_id:
            sql += """ AND id IN (
                SELECT character_id FROM character_campaign_links 
                WHERE campaign_id = %s
            )"""
            params.append(campaign_id)
        
        sql += " LIMIT 1"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()
        
        if not result:
            cur.close()
            raise ValueError(f"Character with given name '{given_name}' not found" + (f" in campaign {campaign_id}" if campaign_id else ""))
        
        cols = [d[0] for d in cur.description]
        character = dict(zip(cols, result))
        cur.close()
        return character
    
    def list_characters(self, campaign_id: str = None) -> List[Dict]:
        """
        List all characters (optionally filtered by campaign)
        Returns list with UUIDs and basic info
        """
        if campaign_id:
            sql = """
                SELECT c.* FROM characters c
                JOIN character_campaign_links ccl ON c.id = ccl.character_id
                WHERE ccl.campaign_id = %s
                ORDER BY c.name
            """
            params = [campaign_id]
        else:
            sql = "SELECT * FROM characters ORDER BY name"
            params = []
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    # ========== SPELLS ==========
    def get_spells(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_spells WHERE character_id = %s AND deleted_at IS NULL ORDER BY spell_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_spell(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO character_spells (character_id, spell_name, learned_force, spell_category, 
                spell_type, target_type, duration, drain_code, drain_modifier, description, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['spell_name'], data.get('learned_force', 1), data.get('spell_category'),
              data.get('spell_type', 'mana'), data.get('target_type'), data.get('duration'),
              data.get('drain_code'), data.get('drain_modifier', 0), data.get('description'),
              data.get('notes'), self.user_id))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_spell(self, char_id: str, spell_name: str, updates: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        fields = ['learned_force', 'spell_category', 'spell_type', 'target_type', 'duration', 
                  'drain_code', 'drain_modifier', 'description', 'notes']
        sets = [f"{f} = %s" for f in fields if f in updates]
        if not sets:
            raise ValueError("No valid fields")
        sets.append("modified_by = %s")
        sets.append("modified_at = NOW()")
        params = [updates[f] for f in fields if f in updates] + [self.user_id, char_id, spell_name]
        
        cur = self.conn.cursor()
        cur.execute(f"UPDATE character_spells SET {', '.join(sets)} WHERE character_id = %s AND spell_name = %s AND deleted_at IS NULL RETURNING *", params)
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Spell '{spell_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def delete_spell(self, char_id: str, spell_name: str, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE character_spells SET deleted_at = NOW(), deleted_by = %s WHERE character_id = %s AND spell_name = %s AND deleted_at IS NULL RETURNING *",
                   (self.user_id, char_id, spell_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Spell '{spell_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== SPIRITS (FIXED: no audit fields in schema) ==========
    def get_spirits(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_spirits WHERE character_id = %s ORDER BY spirit_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_spirit(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO character_spirits (character_id, spirit_name, spirit_type, force, services, special_abilities, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['spirit_name'], data.get('spirit_type'), data.get('force'), 
              data.get('services', 1), data.get('special_abilities', []), data.get('notes')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_spirit_services(self, char_id: str, spirit_name: str, services: int, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("UPDATE character_spirits SET services = %s WHERE character_id = %s AND spirit_name = %s RETURNING *",
                   (services, char_id, spirit_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Spirit '{spirit_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== FOCI (FIXED: no audit fields in schema) ==========
    def get_foci(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_foci WHERE character_id = %s ORDER BY focus_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_focus(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO character_foci (character_id, focus_name, focus_type, force, spell_category, specific_spell, 
                bonus_dice, tn_modifier, bonded, karma_cost, description, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['focus_name'], data['focus_type'], data['force'], data.get('spell_category'),
              data.get('specific_spell'), data.get('bonus_dice', 0), data.get('tn_modifier', 0),
              data.get('bonded', True), data.get('karma_cost'), data.get('description'), data.get('notes')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== GEAR ==========
    def get_gear(self, char_id: str, gear_type: str = None) -> List[Dict]:
        sql = "SELECT * FROM character_gear WHERE character_id = %s"
        params = [char_id]
        if gear_type:
            sql += " AND gear_type = %s"
            params.append(gear_type)
        sql += " AND deleted_at IS NULL ORDER BY gear_name"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_gear(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        mods = data.get('modifications')
        if mods and not isinstance(mods, Jsonb):
            mods = Jsonb(mods)
        cur.execute("""
            INSERT INTO character_gear (character_id, gear_name, gear_type, quantity, modifications, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['gear_name'], data.get('gear_type', 'equipment'), data.get('quantity', 1), mods, data.get('notes'), self.user_id))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_gear_quantity(self, char_id: str, gear_name: str, quantity: int, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE character_gear SET quantity = %s, modified_by = %s, modified_at = NOW() WHERE character_id = %s AND gear_name = %s AND deleted_at IS NULL RETURNING *",
                   (quantity, self.user_id, char_id, gear_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Gear '{gear_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== CONTACTS (FIXED: no audit fields in schema) ==========
    def get_contacts(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_contacts WHERE character_id = %s ORDER BY name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_contact(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO character_contacts (character_id, name, archetype, loyalty, connection, notes)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['name'], data.get('archetype'), data.get('loyalty', 1), data.get('connection', 1), data.get('notes')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_contact_loyalty(self, char_id: str, name: str, loyalty: int, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("UPDATE character_contacts SET loyalty = %s WHERE character_id = %s AND name = %s RETURNING *",
                   (loyalty, char_id, name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Contact '{name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== VEHICLES (HAS audit fields, sensor data in modifications JSONB) ==========
    def get_vehicles(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_vehicles WHERE character_id = %s AND deleted_at IS NULL ORDER BY vehicle_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_vehicle(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        # Schema has: pilot (not autopilot), modifications JSONB (for sensor data), audit fields
        pilot = data.get('pilot', data.get('autopilot'))  # Accept both for compatibility
        
        # Handle modifications JSONB (sensor data goes here)
        modifications = data.get('modifications', {})
        if data.get('sensor'):
            modifications['sensor'] = data['sensor']
        # Always wrap in Jsonb, even if empty
        if not isinstance(modifications, Jsonb):
            modifications = Jsonb(modifications) if modifications else None
        
        cur.execute("""
            INSERT INTO character_vehicles (character_id, vehicle_name, vehicle_type, handling, speed, 
                body, armor, signature, pilot, modifications, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['vehicle_name'], data.get('vehicle_type'), data.get('handling'), data.get('speed'),
              data.get('body'), data.get('armor'), data.get('signature'), pilot, modifications, 
              data.get('notes'), self.user_id))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_vehicle(self, char_id: str, vehicle_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update vehicle details"""
        self._audit(reason)
        fields = ['vehicle_type', 'handling', 'speed', 'body', 'armor', 'signature', 'pilot', 'modifications', 'notes']
        sets = [f"{f} = %s" for f in fields if f in updates]
        if not sets:
            raise ValueError("No valid fields to update")
        sets.append("modified_by = %s")
        sets.append("modified_at = NOW()")
        
        # Handle modifications JSONB
        if 'modifications' in updates and not isinstance(updates['modifications'], Jsonb):
            updates['modifications'] = Jsonb(updates['modifications'])
        
        params = [updates[f] for f in fields if f in updates] + [self.user_id, char_id, vehicle_name]
        
        cur = self.conn.cursor()
        cur.execute(f"UPDATE character_vehicles SET {', '.join(sets)} WHERE character_id = %s AND vehicle_name = %s AND deleted_at IS NULL RETURNING *", params)
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Vehicle '{vehicle_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def delete_vehicle(self, char_id: str, vehicle_name: str, reason: str = None) -> Dict:
        """Soft delete a vehicle"""
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE character_vehicles SET deleted_at = NOW(), deleted_by = %s WHERE character_id = %s AND vehicle_name = %s AND deleted_at IS NULL RETURNING *",
                   (self.user_id, char_id, vehicle_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Vehicle '{vehicle_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== CYBERDECKS (FIXED: memory/storage/response_increase, persona_programs/utilities/ai_companions) ==========
    def get_cyberdecks(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_cyberdecks WHERE character_id = %s ORDER BY deck_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_cyberdeck(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        # Schema has: memory, storage, response_increase, persona_programs, utilities, ai_companions
        # Accept old names for compatibility
        memory = data.get('memory', data.get('active_memory'))
        storage = data.get('storage', data.get('storage_memory'))
        response_increase = data.get('response_increase', data.get('reaction_increase'))
        persona_programs = data.get('persona_programs', data.get('programs', []))
        
        cur.execute("""
            INSERT INTO character_cyberdecks (character_id, deck_name, mpcp, hardening, memory, storage, io_speed, response_increase, persona_programs, utilities, ai_companions, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['deck_name'], data.get('mpcp'), data.get('hardening'), memory,
              storage, data.get('io_speed'), response_increase, persona_programs, 
              data.get('utilities', []), data.get('ai_companions', []), data.get('notes')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== HOUSE RULES ==========
    def get_house_rules(self, campaign_id: str = None, active_only: bool = True) -> List[Dict]:
        sql = "SELECT * FROM house_rules WHERE 1=1"
        params = []
        if campaign_id:
            sql += " AND campaign_id = %s"
            params.append(campaign_id)
        if active_only:
            sql += " AND is_active = true"
        sql += " ORDER BY rule_name"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_house_rule(self, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        config = data.get('rule_config')
        if config and not isinstance(config, Jsonb):
            config = Jsonb(config)
        cur.execute("""
            INSERT INTO house_rules (campaign_id, rule_name, rule_type, description, rule_config, is_active, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (data.get('campaign_id'), data['rule_name'], data['rule_type'], data.get('description'), config, data.get('is_active', True), self.user_id))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def toggle_house_rule(self, rule_id: str, is_active: bool, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE house_rules SET is_active = %s, modified_by = %s, modified_at = NOW() WHERE id = %s RETURNING *",
                   (is_active, self.user_id, rule_id))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"House rule {rule_id} not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== CAMPAIGN NPCs ==========
    def get_campaign_npcs(self, campaign_id: str, relevance: str = None) -> List[Dict]:
        sql = "SELECT * FROM campaign_npcs WHERE campaign_id = %s"
        params = [campaign_id]
        if relevance:
            sql += " AND relevance = %s"
            params.append(relevance)
        sql += " ORDER BY name"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_campaign_npc(self, campaign_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO campaign_npcs (campaign_id, name, role, relevance, location, status, notes, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (campaign_id, data['name'], data.get('role'), data.get('relevance', 'background'),
              data.get('location'), data.get('status'), data.get('notes'), self.user_id))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_npc_relevance(self, npc_id: str, relevance: str, reason: str = None) -> Dict:
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE campaign_npcs SET relevance = %s, modified_by = %s, modified_at = NOW() WHERE id = %s RETURNING *",
                   (relevance, self.user_id, npc_id))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"NPC {npc_id} not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== SKILLS (FIXED: base_rating + current_rating, NO audit fields) ==========
    def get_skills(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_skills WHERE character_id = %s ORDER BY skill_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_skill(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        """Add skill with base_rating and current_rating (NO audit fields in schema)"""
        cur = self.conn.cursor()
        base_rating = data.get('base_rating', data.get('rating', 1))
        current_rating = data.get('current_rating', base_rating)
        
        cur.execute("""
            INSERT INTO character_skills (character_id, skill_name, base_rating, current_rating, specialization, skill_type)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['skill_name'], base_rating, current_rating, 
              data.get('specialization'), data.get('skill_type')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def improve_skill(self, char_id: str, skill_name: str, new_rating: int, reason: str = None) -> Dict:
        """Improve skill - updates both base and current rating"""
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE character_skills 
            SET base_rating = %s, current_rating = %s 
            WHERE character_id = %s AND skill_name = %s 
            RETURNING *
        """, (new_rating, new_rating, char_id, skill_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Skill '{skill_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def add_specialization(self, char_id: str, skill_name: str, specialization: str, reason: str = None) -> Dict:
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE character_skills 
            SET specialization = %s 
            WHERE character_id = %s AND skill_name = %s 
            RETURNING *
        """, (specialization, char_id, skill_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Skill '{skill_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== EDGES & FLAWS (AUTO-POPULATE COST FROM RAG) ==========
    def get_edges_flaws(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_edges_flaws WHERE character_id = %s ORDER BY name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def _lookup_edge_flaw_cost(self, name: str, type_: str, description: str = None) -> int:
        """
        Query RAG database for edge/flaw cost
        Convention: 
        - Edges: negative cost (they cost karma to buy)
        - Flaws: positive cost (they give karma back)
        """
        import re
        try:
            from lib.hybrid_search import HybridSearch
            
            # Build search query
            query = f"{type_} {name}"
            if description:
                query += f" {description}"
            
            # Search RAG database using hybrid search
            searcher = HybridSearch(self.conn)
            results = searcher.hybrid_search(
                query=query,
                categories=['chargen'],  # Edges/flaws are in character generation
                limit=3
            )
            
            if results:
                content = results[0]['content']
                
                # Look for explicit point costs: "(-X point)" or "(+X point)"
                point_match = re.search(r'\(([+-]?\d+)\s*points?\)', content, re.IGNORECASE)
                if point_match:
                    points = int(point_match.group(1))
                    # Flaws with negative points → flip to positive (they give karma)
                    if type_ == 'flaw' and points < 0:
                        return abs(points)
                    # Edges with positive points → flip to negative (they cost karma)
                    elif type_ == 'edge' and points > 0:
                        return -points
                    return points
                
                # Look for "costs X karma"
                karma_match = re.search(r'(?:costs?|cost)\s+(\d+)\s+karma', content, re.IGNORECASE)
                if karma_match:
                    cost = int(karma_match.group(1))
                    return -cost if type_ == 'edge' else cost
        except Exception as e:
            print(f"Warning: RAG lookup failed for {name}: {e}")
        
        # Default costs if RAG lookup fails
        return -3 if type_ == 'edge' else 1
    
    def add_edge_flaw(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        
        # Auto-populate cost from RAG if not provided
        cost = data.get('cost')
        if cost is None:
            cost = self._lookup_edge_flaw_cost(
                data['name'], 
                data['type'], 
                data.get('description')
            )
            print(f"Auto-populated cost for {data['type']} '{data['name']}': {cost:+d} karma")
        
        cur = self.conn.cursor()
        # Schema has: id, character_id, name, type, description, cost, created_at
        # Cost convention: negative for edges (cost karma), positive for flaws (gain karma)
        cur.execute("""
            INSERT INTO character_edges_flaws (character_id, name, type, description, cost)
            VALUES (%s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['name'], data['type'], data.get('description'), cost))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== POWERS (FIXED: UUID character_id, no audit fields) ==========
    def get_powers(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_powers WHERE character_id = %s ORDER BY power_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_power(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO character_powers (character_id, power_name, level, cost)
            VALUES (%s, %s, %s, %s) RETURNING *
        """, (char_id, data['power_name'], data.get('level', 1), data.get('cost', 0)))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_power_level(self, char_id: str, power_name: str, new_level: int, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("UPDATE character_powers SET level = %s WHERE character_id = %s AND power_name = %s RETURNING *",
                   (new_level, char_id, power_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Power '{power_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== RELATIONSHIPS (FIXED: relationship_type, relationship_name, data JSONB) ==========
    def get_relationships(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_relationships WHERE character_id = %s ORDER BY relationship_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_relationship(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        # Schema: relationship_type, relationship_name, data (JSONB), notes (no audit fields)
        relationship_data = data.get('data', {})
        if not isinstance(relationship_data, Jsonb):
            relationship_data = Jsonb(relationship_data)
        
        cur.execute("""
            INSERT INTO character_relationships (character_id, relationship_type, relationship_name, data, notes)
            VALUES (%s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['relationship_type'], data['relationship_name'], relationship_data, data.get('notes')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def update_relationship_data(self, char_id: str, relationship_name: str, new_data: Dict, reason: str = None) -> Dict:
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        if not isinstance(new_data, Jsonb):
            new_data = Jsonb(new_data)
        cur.execute("UPDATE character_relationships SET data = %s WHERE character_id = %s AND relationship_name = %s RETURNING *",
                   (new_data, char_id, relationship_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Relationship '{relationship_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== ACTIVE EFFECTS (FIXED: effect_type, effect_name, target_type, target_name, modifier_value, duration_type, expires_at, caster_id, force, drain_taken) ==========
    def get_active_effects(self, char_id: str, active_only: bool = True) -> List[Dict]:
        sql = "SELECT * FROM character_active_effects WHERE character_id = %s"
        params = [char_id]
        if active_only:
            sql += " AND is_active = true"
        sql += " ORDER BY effect_name"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_active_effect(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        """Add active effect (sustained spell, curse, poison, etc.)"""
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        # Schema: effect_type, effect_name, target_type, target_name, modifier_value, duration_type, expires_at, is_active, caster_id, force, drain_taken, notes
        cur.execute("""
            INSERT INTO character_active_effects (character_id, effect_type, effect_name, target_type, target_name, 
                modifier_value, duration_type, expires_at, is_active, caster_id, force, drain_taken, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['effect_type'], data['effect_name'], data.get('target_type'), data.get('target_name'),
              data.get('modifier_value', 0), data.get('duration_type', 'sustained'), data.get('expires_at'),
              data.get('is_active', True), data.get('caster_id'), data.get('force'), data.get('drain_taken'), data.get('notes')))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def deactivate_effect(self, char_id: str, effect_name: str, reason: str = None) -> Dict:
        """Deactivate an active effect (spell ends, poison cured, etc.)"""
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("UPDATE character_active_effects SET is_active = false WHERE character_id = %s AND effect_name = %s RETURNING *",
                   (char_id, effect_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Effect '{effect_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_effect(self, char_id: str, effect_name: str, reason: str = None) -> Dict:
        """Permanently remove an effect"""
        self._audit(reason)  # Keep for future compatibility
        cur = self.conn.cursor()
        cur.execute("DELETE FROM character_active_effects WHERE character_id = %s AND effect_name = %s RETURNING *",
                   (char_id, effect_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Effect '{effect_name}' not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== MODIFIERS (FIXED: source not source_name, is_permanent not is_temporary) ==========
    def get_modifiers(self, char_id: str, modifier_type: str = None) -> List[Dict]:
        sql = "SELECT * FROM character_modifiers WHERE character_id = %s AND deleted_at IS NULL"
        params = [char_id]
        if modifier_type:
            sql += " AND modifier_type = %s"
            params.append(modifier_type)
        sql += " ORDER BY modifier_type, target_name"
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_modifier(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        """Add a modifier (from cyberware, spell, condition, etc.)"""
        self._audit(reason)
        cur = self.conn.cursor()
        
        modifier_data = data.get('modifier_data')
        if modifier_data and not isinstance(modifier_data, Jsonb):
            modifier_data = Jsonb(modifier_data)
        
        # Schema has: source (text), is_permanent (boolean), source_type, source_id
        # Accept both source/source_name for compatibility
        source = data.get('source', data.get('source_name'))
        # Convert is_temporary to is_permanent
        is_permanent = not data.get('is_temporary', False) if 'is_temporary' in data else data.get('is_permanent', True)
        
        cur.execute("""
            INSERT INTO character_modifiers (character_id, modifier_type, target_name, modifier_value,
                source, is_permanent, source_type, source_id, modifier_data, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
        """, (char_id, data['modifier_type'], data.get('target_name'), data.get('modifier_value', 0),
              source, is_permanent, data.get('source_type'), data.get('source_id'),
              modifier_data, self.user_id))
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_modifier(self, modifier_id: str, reason: str = None) -> Dict:
        """Remove a modifier by ID (soft delete)"""
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE character_modifiers SET deleted_at = NOW(), deleted_by = %s WHERE id = %s AND deleted_at IS NULL RETURNING *", 
                   (self.user_id, modifier_id))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Modifier {modifier_id} not found")
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_temporary_modifiers(self, char_id: str, reason: str = None) -> List[Dict]:
        """Remove all temporary modifiers for a character (soft delete)"""
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE character_modifiers SET deleted_at = NOW(), deleted_by = %s WHERE character_id = %s AND is_permanent = false AND deleted_at IS NULL RETURNING *", 
                   (self.user_id, char_id))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        self.conn.commit()
        cur.close()
        return results
    
    # ========== CYBERWARE & BIOWARE ==========
    def get_character_cyberware(self, char_id: str) -> List[Dict]:
        """Get all cyberware for a character"""
        logger.info(f"Getting cyberware for character {char_id}")
        return self.get_modifiers(char_id, modifier_type='cyberware')
    
    def get_character_bioware(self, char_id: str) -> List[Dict]:
        """Get all bioware for a character"""
        logger.info(f"Getting bioware for character {char_id}")
        return self.get_modifiers(char_id, modifier_type='bioware')
    
    def add_cyberware(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        """Add cyberware to character"""
        logger.info(f"Adding cyberware {data.get('name')} to character {char_id}")
        data['modifier_type'] = 'cyberware'
        data['source_type'] = 'cyberware'
        if 'source' not in data and 'name' in data:
            data['source'] = data['name']
        return self.add_modifier(char_id, data, reason)
    
    def add_bioware(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        """Add bioware to character"""
        logger.info(f"Adding bioware {data.get('name')} to character {char_id}")
        data['modifier_type'] = 'bioware'
        data['source_type'] = 'bioware'
        if 'source' not in data and 'name' in data:
            data['source'] = data['name']
        return self.add_modifier(char_id, data, reason)
    
    def update_cyberware(self, char_id: str, modifier_id: str, updates: Dict, reason: str = None) -> Dict:
        """Update cyberware modifier"""
        logger.info(f"Updating cyberware {modifier_id} for character {char_id}")
        # Get existing modifier
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_modifiers WHERE id = %s AND character_id = %s AND modifier_type = 'cyberware' AND deleted_at IS NULL", 
                   (modifier_id, char_id))
        existing = cur.fetchone()
        if not existing:
            cur.close()
            raise ValueError(f"Cyberware {modifier_id} not found")
        
        # Update allowed fields
        self._audit(reason)
        allowed_fields = ['target_name', 'modifier_value', 'source', 'modifier_data']
        sets = [f"{f} = %s" for f in allowed_fields if f in updates]
        if not sets:
            cur.close()
            raise ValueError("No valid fields to update")
        
        sets.append("modified_by = %s")
        sets.append("modified_at = NOW()")
        
        # Handle JSONB
        if 'modifier_data' in updates and not isinstance(updates['modifier_data'], Jsonb):
            updates['modifier_data'] = Jsonb(updates['modifier_data'])
        
        params = [updates[f] for f in allowed_fields if f in updates] + [self.user_id, modifier_id]
        
        cur.execute(f"UPDATE character_modifiers SET {', '.join(sets)} WHERE id = %s RETURNING *", params)
        result = dict(zip([d[0] for d in cur.description], cur.fetchone()))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_cyberware(self, char_id: str, modifier_id: str, reason: str = None) -> Dict:
        """Remove cyberware from character"""
        logger.info(f"Removing cyberware {modifier_id} from character {char_id}")
        return self.remove_modifier(modifier_id, reason)
    
    def remove_bioware(self, char_id: str, modifier_id: str, reason: str = None) -> Dict:
        """Remove bioware from character"""
        logger.info(f"Removing bioware {modifier_id} from character {char_id}")
        return self.remove_modifier(modifier_id, reason)
    
    # ========== CONVENIENCE GETTERS ==========
    def get_character_skills(self, char_id: str) -> List[Dict]:
        """Alias for get_skills"""
        return self.get_skills(char_id)
    
    def get_character_spells(self, char_id: str) -> List[Dict]:
        """Alias for get_spells"""
        return self.get_spells(char_id)
    
    def get_character_gear(self, char_id: str, gear_type: str = None) -> List[Dict]:
        """Alias for get_gear"""
        return self.get_gear(char_id, gear_type)
    
    # ========== UPDATE/REMOVE OPERATIONS ==========
    def update_skill(self, char_id: str, skill_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update skill details"""
        logger.info(f"Updating skill {skill_name} for character {char_id}")
        cur = self.conn.cursor()
        
        allowed_fields = ['base_rating', 'current_rating', 'specialization', 'skill_type']
        sets = [f"{f} = %s" for f in allowed_fields if f in updates]
        if not sets:
            raise ValueError("No valid fields to update")
        
        params = [updates[f] for f in allowed_fields if f in updates] + [char_id, skill_name]
        
        cur.execute(f"UPDATE character_skills SET {', '.join(sets)} WHERE character_id = %s AND skill_name = %s RETURNING *", params)
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_skill(self, char_id: str, skill_name: str, reason: str = None) -> Dict:
        """Remove a skill (hard delete)"""
        logger.warning(f"Removing skill {skill_name} from character {char_id}")
        cur = self.conn.cursor()
        cur.execute("DELETE FROM character_skills WHERE character_id = %s AND skill_name = %s RETURNING *",
                   (char_id, skill_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_spell(self, char_id: str, spell_name: str, reason: str = None) -> Dict:
        """Alias for delete_spell"""
        return self.delete_spell(char_id, spell_name, reason)
    
    def update_gear(self, char_id: str, gear_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update gear details"""
        logger.info(f"Updating gear {gear_name} for character {char_id}")
        self._audit(reason)
        
        allowed_fields = ['gear_type', 'quantity', 'modifications', 'notes']
        sets = [f"{f} = %s" for f in allowed_fields if f in updates]
        if not sets:
            raise ValueError("No valid fields to update")
        
        sets.append("modified_by = %s")
        sets.append("modified_at = NOW()")
        
        # Handle JSONB
        if 'modifications' in updates and not isinstance(updates['modifications'], Jsonb):
            updates['modifications'] = Jsonb(updates['modifications'])
        
        params = [updates[f] for f in allowed_fields if f in updates] + [self.user_id, char_id, gear_name]
        
        cur = self.conn.cursor()
        cur.execute(f"UPDATE character_gear SET {', '.join(sets)} WHERE character_id = %s AND gear_name = %s AND deleted_at IS NULL RETURNING *", params)
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Gear '{gear_name}' not found")
        
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    def remove_gear(self, char_id: str, gear_name: str, reason: str = None) -> Dict:
        """Remove gear (soft delete)"""
        logger.info(f"Removing gear {gear_name} from character {char_id}")
        self._audit(reason)
        cur = self.conn.cursor()
        cur.execute("UPDATE character_gear SET deleted_at = NOW(), deleted_by = %s WHERE character_id = %s AND gear_name = %s AND deleted_at IS NULL RETURNING *",
                   (self.user_id, char_id, gear_name))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Gear '{gear_name}' not found")
        
        result = dict(zip([d[0] for d in cur.description], result))
        self.conn.commit()
        cur.close()
        return result
    
    # ========== AUDIT LOG ==========
    def get_audit_log(self, table_name: str = None, record_id: str = None, limit: int = 100) -> List[Dict]:
        sql = "SELECT a.*, u.email as changed_by_email, u.display_name as changed_by_name FROM audit_log a LEFT JOIN users u ON a.changed_by = u.id WHERE 1=1"
        params = []
        if table_name:
            sql += " AND a.table_name = %s"
            params.append(table_name)
        if record_id:
            sql += " AND a.record_id = %s"
            params.append(record_id)
        sql += " ORDER BY a.changed_at DESC LIMIT %s"
        params.append(limit)
        
        cur = self.conn.cursor()
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results


# Helper functions
def get_ai_user_id(conn: psycopg.Connection) -> str:
    """Get or create AI user ID"""
    cur = conn.cursor()
    cur.execute("SELECT get_ai_user_id()")
    user_id = cur.fetchone()[0]
    cur.close()
    return user_id


def get_system_user_id(conn: psycopg.Connection) -> str:
    """Get or create system user ID"""
    cur = conn.cursor()
    cur.execute("SELECT get_system_user_id()")
    user_id = cur.fetchone()[0]
    cur.close()
    return user_id


if __name__ == "__main__":
    print("Comprehensive CRUD API - Ready for use")
    print("=" * 80)
    print("\nCHARACTER DATA:")
    print("  - Spells: get_spells, add_spell, update_spell, delete_spell")
    print("  - Spirits: get_spirits, add_spirit, update_spirit_services")
    print("  - Foci: get_foci, add_focus")
    print("  - Gear: get_gear, add_gear, update_gear_quantity")
    print("  - Contacts: get_contacts, add_contact, update_contact_loyalty")
    print("  - Vehicles: get_vehicles, add_vehicle")
    print("  - Cyberdecks: get_cyberdecks, add_cyberdeck")
    print("  - Skills: get_skills, add_skill, improve_skill, add_specialization")
    print("  - Edges/Flaws: get_edges_flaws, add_edge_flaw")
    print("  - Powers: get_powers, add_power, update_power_level")
    print("  - Relationships: get_relationships, add_relationship, update_relationship_status")
    print("\nGAMEPLAY STATE:")
    print("  - Active Effects: get_active_effects, add_active_effect, deactivate_effect, remove_effect")
    print("  - Modifiers: get_modifiers, add_modifier, remove_modifier, remove_temporary_modifiers")
    print("\nCAMPAIGN DATA:")
    print("  - House Rules: get_house_rules, add_house_rule, toggle_house_rule")
    print("  - Campaign NPCs: get_campaign_npcs, add_campaign_npc, update_npc_relevance")
    print("\nAUDIT:")
    print("  - Audit Log: get_audit_log")
    print("\n" + "=" * 80)
    print("Total: 40+ CRUD operations with full audit logging")
