#!/usr/bin/env python3
"""
Comprehensive CRUD API with Audit Logging
Provides create, read, update, delete operations for all character and campaign data
with complete audit trail and soft delete support
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import psycopg
from psycopg.types.json import Jsonb

load_dotenv()


class ComprehensiveCRUDAPI:
    """
    Complete CRUD API for character and campaign data with audit logging
    """
    
    def __init__(self, user_id: str, user_type: str = 'USER'):
        """
        Initialize CRUD API
        
        Args:
            user_id: UUID of the user making changes
            user_type: Type of user ('USER', 'AI', 'SYSTEM')
        """
        self.user_id = user_id
        self.user_type = user_type
        self.conn = psycopg.connect(
            host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
            port=int(os.getenv('POSTGRES_PORT', '5434')),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD'),
            dbname=os.getenv('POSTGRES_DB', 'postgres')
        )
    
    def _set_audit_context(self, reason: Optional[str] = None):
        """Set PostgreSQL session variables for audit trigger"""
        cursor = self.conn.cursor()
        cursor.execute(f"SET app.current_user_id = '{self.user_id}'")
        cursor.execute(f"SET app.current_user_type = '{self.user_type}'")
        if reason:
            cursor.execute(f"SET app.change_reason = '{reason}'")
        cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    # ==================== SPELL CRUD ====================
    
    def get_spells(self, character_id: str, include_deleted: bool = False) -> List[Dict]:
        """Get all spells for a character"""
        sql = "SELECT * FROM character_spells WHERE character_id = %s"
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        sql += " ORDER BY spell_name"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, (character_id,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    def add_spell(self, character_id: str, spell_data: Dict, reason: str = None) -> Dict:
        """Add a spell to a character"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO character_spells (
                character_id, spell_name, learned_force, spell_category,
                spell_type, target_type, duration, drain_code, drain_modifier,
                description, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            character_id, spell_data['spell_name'], spell_data.get('learned_force', 1),
            spell_data.get('spell_category'), spell_data.get('spell_type', 'mana'),
            spell_data.get('target_type'), spell_data.get('duration'),
            spell_data.get('drain_code'), spell_data.get('drain_modifier', 0),
            spell_data.get('description'), spell_data.get('notes'), self.user_id
        ))
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return spell
    
    def update_spell(self, character_id: str, spell_name: str, updates: Dict, reason: str = None) -> Dict:
        """Update a spell"""
        self._set_audit_context(reason)
        set_clauses = []
        params = []
        
        for field in ['learned_force', 'spell_category', 'spell_type', 'target_type', 
                     'duration', 'drain_code', 'drain_modifier', 'description', 'notes']:
            if field in updates:
                set_clauses.append(f"{field} = %s")
                params.append(updates[field])
        
        if not set_clauses:
            raise ValueError("No valid fields to update")
        
        set_clauses.append("modified_by = %s")
        set_clauses.append("modified_at = NOW()")
        params.extend([self.user_id, character_id, spell_name])
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            UPDATE character_spells SET {', '.join(set_clauses)}
            WHERE character_id = %s AND spell_name = %s AND deleted_at IS NULL
            RETURNING *
        """, params)
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Spell '{spell_name}' not found")
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return spell
    
    def delete_spell(self, character_id: str, spell_name: str, reason: str = None) -> Dict:
        """Soft delete a spell"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE character_spells SET deleted_at = NOW(), deleted_by = %s
            WHERE character_id = %s AND spell_name = %s AND deleted_at IS NULL
            RETURNING *
        """, (self.user_id, character_id, spell_name))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Spell '{spell_name}' not found")
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return spell
    
    # ==================== SPIRIT CRUD ====================
    
    def get_spirits(self, character_id: str, include_deleted: bool = False) -> List[Dict]:
        """Get all bound spirits for a character"""
        sql = "SELECT * FROM character_spirits WHERE character_id = %s"
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        sql += " ORDER BY spirit_name"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, (character_id,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    def add_spirit(self, character_id: str, spirit_data: Dict, reason: str = None) -> Dict:
        """Add a bound spirit"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO character_spirits (
                character_id, spirit_name, spirit_type, force, services,
                special_abilities, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            character_id, spirit_data['spirit_name'], spirit_data.get('spirit_type'),
            spirit_data.get('force'), spirit_data.get('services', 1),
            spirit_data.get('special_abilities', []), spirit_data.get('notes'), self.user_id
        ))
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        spirit = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return spirit
    
    def update_spirit_services(self, character_id: str, spirit_name: str, services: int, reason: str = None) -> Dict:
        """Update spirit's remaining services"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE character_spirits SET services = %s, modified_by = %s, modified_at = NOW()
            WHERE character_id = %s AND spirit_name = %s AND deleted_at IS NULL
            RETURNING *
        """, (services, self.user_id, character_id, spirit_name))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Spirit '{spirit_name}' not found")
        columns = [desc[0] for desc in cursor.description]
        spirit = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return spirit
    
    # ==================== FOCI CRUD ====================
    
    def get_foci(self, character_id: str, include_deleted: bool = False) -> List[Dict]:
        """Get all foci for a character"""
        sql = "SELECT * FROM character_foci WHERE character_id = %s"
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        sql += " ORDER BY focus_name"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, (character_id,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    def add_focus(self, character_id: str, focus_data: Dict, reason: str = None) -> Dict:
        """Add a focus"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO character_foci (
                character_id, focus_name, focus_type, force, spell_category,
                specific_spell, bonus_dice, tn_modifier, bonded, karma_cost,
                description, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            character_id, focus_data['focus_name'], focus_data['focus_type'],
            focus_data['force'], focus_data.get('spell_category'),
            focus_data.get('specific_spell'), focus_data.get('bonus_dice', 0),
            focus_data.get('tn_modifier', 0), focus_data.get('bonded', True),
            focus_data.get('karma_cost'), focus_data.get('description'),
            focus_data.get('notes'), self.user_id
        ))
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        focus = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return focus
    
    # ==================== GEAR CRUD ====================
    
    def get_gear(self, character_id: str, gear_type: str = None, include_deleted: bool = False) -> List[Dict]:
        """Get character's gear"""
        sql = "SELECT * FROM character_gear WHERE character_id = %s"
        params = [character_id]
        
        if gear_type:
            sql += " AND gear_type = %s"
            params.append(gear_type)
        
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        
        sql += " ORDER BY gear_name"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    def add_gear(self, character_id: str, gear_data: Dict, reason: str = None) -> Dict:
        """Add gear"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        
        modifications = gear_data.get('modifications')
        if modifications and not isinstance(modifications, Jsonb):
            modifications = Jsonb(modifications)
        
        cursor.execute("""
            INSERT INTO character_gear (
                character_id, gear_name, gear_type, quantity,
                modifications, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            character_id, gear_data['gear_name'], gear_data.get('gear_type', 'equipment'),
            gear_data.get('quantity', 1), modifications, gear_data.get('notes'), self.user_id
        ))
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        gear = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return gear
    
    def update_gear_quantity(self, character_id: str, gear_name: str, quantity: int, reason: str = None) -> Dict:
        """Update gear quantity"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE character_gear SET quantity = %s, modified_by = %s, modified_at = NOW()
            WHERE character_id = %s AND gear_name = %s AND deleted_at IS NULL
            RETURNING *
        """, (quantity, self.user_id, character_id, gear_name))
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Gear '{gear_name}' not found")
        columns = [desc[0] for desc in cursor.description]
        gear = dict(zip(columns, result))
        self.conn.commit()
        cursor.close()
        return gear
    
    # ==================== CONTACT CRUD ====================
    
    def get_contacts(self, character_id: str, include_deleted: bool = False) -> List[Dict]:
        """Get all contacts"""
        sql = "SELECT * FROM character_contacts WHERE character_id = %s"
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        sql += " ORDER BY name"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, (character_id,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        return results
    
    def add_contact(self, character_id: str, contact_data: Dict, reason: str = None) -> Dict:
        """Add a contact"""
        self._set_audit_context(reason)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO character_contacts (
                character_id, name, archetype, loyalty, connection, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            character_id, contact_data['name'], contact_data.get('archetype'),
            contact_data.get('loyalty', 1), contact_data.get('connection', 1),
            contact_data.get('notes'), self.user_id
        ))
        result = cursor.fetchone
