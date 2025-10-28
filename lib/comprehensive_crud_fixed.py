#!/usr/bin/env python3
"""
Comprehensive CRUD API - SCHEMA CORRECTED VERSION
Matches actual database schema exactly
"""
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import psycopg
from psycopg.types.json import Jsonb

load_dotenv()


class ComprehensiveCRUD:
    """Complete CRUD API matching actual schema"""
    
    def __init__(self, user_id: str, user_type: str = 'USER'):
        self.user_id = user_id
        self.user_type = user_type
        self.conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
            port=int(os.getenv('POSTGRES_PORT', '5434')),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB')
        )
    
    def _audit(self, reason: str = None):
        """Set audit context for tables that support it"""
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
    
    def list_characters(self, campaign_id: str = None) -> List[Dict]:
        """List all characters (optionally filtered by campaign)"""
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
    
    # ========== SKILLS (FIXED: base_rating + current_rating) ==========
    def get_skills(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_skills WHERE character_id = %s ORDER BY skill_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_skill(self, char_id: str, data: Dict, reason: str = None) -> Dict:
        """Add skill with base_rating and current_rating"""
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
    
    # ========== SPELLS (HAS AUDIT FIELDS) ==========
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
        """, (char_id, data['spell_name'], data.get('learned_force', 1), data['spell_category'],
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
    
    # ========== SPIRITS (NO AUDIT FIELDS) ==========
    def get_spirits(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_spirits WHERE character_id = %s ORDER BY spirit_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_spirit(self, char_id: str, data: Dict, reason: str = None) -> Dict:
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
    
    # ========== FOCI (NO AUDIT FIELDS) ==========
    def get_foci(self, char_id: str) -> List[Dict]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM character_foci WHERE character_id = %s ORDER BY focus_name", (char_id,))
        cols = [d[0] for d in cur.description]
        results = [dict(zip(cols, row)) for row in cur.fetchall()]
        cur.close()
        return results
    
    def add_focus(self, char_id: str, data: Dict, reason: str = None) -> Dict:
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
    
    # ========== GEAR (HAS AUDIT FIELDS) ==========
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
                   (
