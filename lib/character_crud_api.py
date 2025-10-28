#!/usr/bin/env python3
"""
Character CRUD API with Audit Logging
Provides create, read, update, delete operations for character data
with complete audit trail and soft delete support
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv
import psycopg
from lib.hybrid_search import HybridSearch

load_dotenv()


class CharacterCRUDAPI:
    """
    CRUD API for character data with audit logging
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
        self.hybrid_search = HybridSearch(self.conn)
    
    def _set_audit_context(self, reason: Optional[str] = None):
        """
        Set PostgreSQL session variables for audit trigger
        
        Args:
            reason: Optional reason for the change
        """
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
    
    def get_character_spells(
        self, 
        character_id: int, 
        include_deleted: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all spells for a character
        
        Args:
            character_id: Character ID
            include_deleted: Include soft-deleted spells
            
        Returns:
            List of spell dictionaries
        """
        sql = "SELECT * FROM character_spells WHERE character_id = %s"
        params = [character_id]
        
        if not include_deleted:
            sql += " AND deleted_at IS NULL"
        
        sql += " ORDER BY spell_name"
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        return results
    
    def add_spell(
        self, 
        character_id: int, 
        spell_data: Dict[str, Any],
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new spell to a character
        
        Args:
            character_id: Character ID
            spell_data: Spell data dict with keys:
                - spell_name (required)
                - learned_force (optional)
                - spell_category (optional)
                - drain_code (optional)
                - target_type (optional)
                - totem_modifier (optional)
                - spell_notes (optional)
            reason: Reason for adding spell
            
        Returns:
            Created spell dictionary
        """
        self._set_audit_context(reason)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO character_spells (
                character_id, spell_name, learned_force, spell_category,
                drain_code, target_type, totem_modifier, spell_notes,
                created_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            character_id,
            spell_data['spell_name'],
            spell_data.get('learned_force'),
            spell_data.get('spell_category'),
            spell_data.get('drain_code'),
            spell_data.get('target_type'),
            spell_data.get('totem_modifier', 0),
            spell_data.get('spell_notes'),
            self.user_id
        ))
        
        result = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        
        self.conn.commit()
        cursor.close()
        
        return spell
    
    def update_spell_force(
        self,
        character_id: int,
        spell_name: str,
        new_force: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a spell's learned force
        
        Args:
            character_id: Character ID
            spell_name: Name of spell to update
            new_force: New force value
            reason: Reason for update
            
        Returns:
            Updated spell dictionary
        """
        self._set_audit_context(reason)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE character_spells
            SET learned_force = %s, 
                modified_by = %s, 
                modified_at = NOW()
            WHERE character_id = %s 
              AND spell_name = %s 
              AND deleted_at IS NULL
            RETURNING *
        """, (new_force, self.user_id, character_id, spell_name))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Spell '{spell_name}' not found for character {character_id}")
        
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        
        self.conn.commit()
        cursor.close()
        
        return spell
    
    def update_spell(
        self,
        character_id: int,
        spell_name: str,
        updates: Dict[str, Any],
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update multiple fields of a spell
        
        Args:
            character_id: Character ID
            spell_name: Name of spell to update
            updates: Dictionary of fields to update
            reason: Reason for update
            
        Returns:
            Updated spell dictionary
        """
        self._set_audit_context(reason)
        
        # Build dynamic UPDATE query
        set_clauses = []
        params = []
        
        for field, value in updates.items():
            if field in ['learned_force', 'spell_category', 'drain_code', 
                        'target_type', 'totem_modifier', 'spell_notes']:
                set_clauses.append(f"{field} = %s")
                params.append(value)
        
        if not set_clauses:
            raise ValueError("No valid fields to update")
        
        set_clauses.append("modified_by = %s")
        set_clauses.append("modified_at = NOW()")
        params.extend([self.user_id, character_id, spell_name])
        
        sql = f"""
            UPDATE character_spells
            SET {', '.join(set_clauses)}
            WHERE character_id = %s 
              AND spell_name = %s 
              AND deleted_at IS NULL
            RETURNING *
        """
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Spell '{spell_name}' not found for character {character_id}")
        
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        
        self.conn.commit()
        cursor.close()
        
        return spell
    
    def soft_delete_spell(
        self,
        character_id: int,
        spell_name: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Soft delete a spell (sets deleted_at timestamp)
        
        Args:
            character_id: Character ID
            spell_name: Name of spell to delete
            reason: Reason for deletion
            
        Returns:
            Deleted spell dictionary
        """
        self._set_audit_context(reason)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE character_spells
            SET deleted_at = NOW(), 
                deleted_by = %s
            WHERE character_id = %s 
              AND spell_name = %s 
              AND deleted_at IS NULL
            RETURNING *
        """, (self.user_id, character_id, spell_name))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Spell '{spell_name}' not found for character {character_id}")
        
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        
        self.conn.commit()
        cursor.close()
        
        return spell
    
    def restore_spell(
        self,
        character_id: int,
        spell_name: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore a soft-deleted spell
        
        Args:
            character_id: Character ID
            spell_name: Name of spell to restore
            reason: Reason for restoration
            
        Returns:
            Restored spell dictionary
        """
        self._set_audit_context(reason)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE character_spells
            SET deleted_at = NULL, 
                deleted_by = NULL,
                modified_by = %s,
                modified_at = NOW()
            WHERE character_id = %s 
              AND spell_name = %s 
              AND deleted_at IS NOT NULL
            RETURNING *
        """, (self.user_id, character_id, spell_name))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            raise ValueError(f"Deleted spell '{spell_name}' not found for character {character_id}")
        
        columns = [desc[0] for desc in cursor.description]
        spell = dict(zip(columns, result))
        
        self.conn.commit()
        cursor.close()
        
        return spell
    
    # ==================== RAG SUPPLEMENTATION ====================
    
    def supplement_spell_from_rag(
        self,
        spell_name: str
    ) -> Dict[str, Any]:
        """
        Query RAG database for spell details to supplement missing data
        
        Args:
            spell_name: Name of spell to look up
            
        Returns:
            Dictionary with supplemental spell data
        """
        # Search for spell in rules content
        results = self.hybrid_search.search_spells(f"spell {spell_name}", limit=3)
        
        if not results:
            return {}
        
        # Parse spell details from top result
        top_result = results[0]
        content = top_result['content']
        
        # Extract drain code (e.g., "6S", "(F/2)M")
        import re
        drain_match = re.search(r'Drain[:\s]+([^\n]+)', content, re.IGNORECASE)
        drain_code = drain_match.group(1).strip() if drain_match else None
        
        # Extract target type (e.g., "M/S/D")
        target_match = re.search(r'Target[:\s]+([^\n]+)', content, re.IGNORECASE)
        target_type = target_match.group(1).strip() if target_match else None
        
        # Extract category
        category_match = re.search(r'Category[:\s]+([^\n]+)', content, re.IGNORECASE)
        category = category_match.group(1).strip().lower() if category_match else None
        
        return {
            'drain_code': drain_code,
            'target_type': target_type,
            'spell_category': category,
            'spell_notes': content[:500]  # First 500 chars as notes
        }
    
    # ==================== AUDIT LOG ====================
    
    def get_audit_log(
        self,
        table_name: Optional[str] = None,
        record_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries
        
        Args:
            table_name: Filter by table name
            record_id: Filter by record ID
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        sql = """
            SELECT 
                a.*,
                u.email as changed_by_email,
                u.display_name as changed_by_name
            FROM audit_log a
            LEFT JOIN users u ON a.changed_by = u.id
            WHERE 1=1
        """
        params = []
        
        if table_name:
            sql += " AND a.table_name = %s"
            params.append(table_name)
        
        if record_id:
            sql += " AND a.record_id = %s"
            params.append(record_id)
        
        sql += " ORDER BY a.changed_at DESC LIMIT %s"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        cursor.close()
        return results


# Helper functions for common operations

def get_ai_user_id(conn: psycopg.Connection) -> str:
    """Get or create AI user ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT get_ai_user_id()")
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id


def get_system_user_id(conn: psycopg.Connection) -> str:
    """Get or create system user ID"""
    cursor = conn.cursor()
    cursor.execute("SELECT get_system_user_id()")
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id


def get_user_id_by_email(conn: psycopg.Connection, email: str) -> Optional[str]:
    """Get user ID by email"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    return result[0] if result else None


if __name__ == "__main__":
    # Test the CRUD API
    print("Testing Character CRUD API...")
    print("=" * 80)
    
    # Get AI user ID
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5434')),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB', 'postgres')
    )
    
    ai_user_id = get_ai_user_id(conn)
    print(f"AI User ID: {ai_user_id}")
    conn.close()
    
    print("\nCRUD API test complete!")
