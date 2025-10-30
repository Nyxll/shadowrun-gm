"""
Test utilities for isolated, transaction-based testing

This module provides test isolation to prevent database locking
and test pollution. All changes made within test contexts are
automatically rolled back.
"""
import psycopg2
from contextlib import contextmanager
from typing import Generator, Dict, Any, Optional
from .db_utils import get_db_config

@contextmanager
def isolated_test_db() -> Generator[psycopg2.extensions.connection, None, None]:
    """Provide isolated database connection with automatic rollback
    
    All changes made within this context are rolled back after the test.
    This prevents test pollution and database locking issues.
    
    Usage:
        def test_something():
            with isolated_test_db() as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO characters ...")
                # Test assertions here
            # Automatic rollback - no permanent changes!
    
    Yields:
        psycopg2 connection object in transaction mode
    """
    conn = None
    try:
        config = get_db_config()
        conn = psycopg2.connect(**config)
        conn.autocommit = False
        
        # Start transaction
        cur = conn.cursor()
        cur.execute("BEGIN")
        
        yield conn
        
    finally:
        if conn:
            # Always rollback - never commit test data
            conn.rollback()
            conn.close()

def create_test_character(
    conn, 
    name: str = "Test Character",
    **kwargs
) -> int:
    """Create a test character and return ID
    
    Args:
        conn: Database connection (from isolated_test_db)
        name: Character name (default "Test Character")
        **kwargs: Additional character attributes
    
    Returns:
        Character ID
    
    Example:
        with isolated_test_db() as conn:
            char_id = create_test_character(conn, "Test Mage", base_magic=6)
            # Use char_id in tests
        # Automatic cleanup via rollback
    """
    # Default attributes (using actual schema column names)
    defaults = {
        'street_name': name,
        'character_type': 'PC',
        'archetype': 'Test',
        'base_body': 3,
        'base_quickness': 3,
        'base_strength': 3,
        'base_charisma': 3,
        'base_intelligence': 3,
        'base_willpower': 3,
        'base_essence': 6.0,
        'base_magic': 0,
        'base_reaction': 3,
        'current_body': 3,
        'current_quickness': 3,
        'current_strength': 3,
        'current_charisma': 3,
        'current_intelligence': 3,
        'current_willpower': 3,
        'current_essence': 6.0,
        'current_magic': 0,
        'current_reaction': 3
    }
    
    # Override with kwargs
    defaults.update(kwargs)
    
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO characters (
            name, street_name, character_type, archetype,
            base_body, base_quickness, base_strength, base_charisma,
            base_intelligence, base_willpower, base_essence, base_magic, base_reaction,
            current_body, current_quickness, current_strength, current_charisma,
            current_intelligence, current_willpower, current_essence, current_magic, current_reaction
        )
        VALUES (
            %(name)s, %(street_name)s, %(character_type)s, %(archetype)s,
            %(base_body)s, %(base_quickness)s, %(base_strength)s, %(base_charisma)s,
            %(base_intelligence)s, %(base_willpower)s, %(base_essence)s, %(base_magic)s, %(base_reaction)s,
            %(current_body)s, %(current_quickness)s, %(current_strength)s, %(current_charisma)s,
            %(current_intelligence)s, %(current_willpower)s, %(current_essence)s, %(current_magic)s, %(current_reaction)s
        )
        RETURNING id
    """, {'name': name, **defaults})
    
    return cur.fetchone()[0]

def create_test_mage(
    conn,
    name: str = "Test Mage",
    magic: int = 6,
    totem: Optional[str] = None
) -> int:
    """Create a test mage character
    
    Args:
        conn: Database connection
        name: Character name
        magic: Magic attribute (default 6)
        totem: Totem name (optional)
    
    Returns:
        Character ID
    """
    char_id = create_test_character(
        conn,
        name=name,
        base_magic=magic,
        current_magic=magic,
        base_intelligence=5,
        current_intelligence=5,
        base_willpower=6,
        current_willpower=6
    )
    
    # Add totem if specified
    if totem:
        cur = conn.cursor()
        cur.execute("""
            UPDATE characters 
            SET totem = %s 
            WHERE id = %s
        """, (totem, char_id))
    
    return char_id

def create_test_spell(
    conn,
    character_id: int,
    spell_name: str = "Manabolt",
    learned_force: int = 3
) -> int:
    """Add a spell to a test character
    
    Args:
        conn: Database connection
        character_id: Character ID
        spell_name: Spell name (must exist in master_spells)
        learned_force: Force at which spell was learned
    
    Returns:
        character_spells ID
    """
    cur = conn.cursor()
    
    # Get spell_id from master_spells
    cur.execute("""
        SELECT id FROM master_spells 
        WHERE LOWER(name) = LOWER(%s)
    """, (spell_name,))
    
    result = cur.fetchone()
    if not result:
        raise ValueError(f"Spell '{spell_name}' not found in master_spells")
    
    spell_id = result[0]
    
    # Add to character_spells
    cur.execute("""
        INSERT INTO character_spells (character_id, spell_id, learned_force)
        VALUES (%s, %s, %s)
        RETURNING id
    """, (character_id, spell_id, learned_force))
    
    return cur.fetchone()[0]

def cleanup_test_data(conn, character_id: int):
    """Clean up test character and related data
    
    Note: This is usually not needed when using isolated_test_db()
    since everything is rolled back automatically. Use this only
    when you need explicit cleanup in non-isolated contexts.
    
    Args:
        conn: Database connection
        character_id: Character ID to clean up
    """
    cur = conn.cursor()
    
    # Delete in order to respect foreign keys
    tables = [
        'character_spells',
        'character_modifiers',
        'character_gear',
        'character_skills',
        'character_contacts',
        'character_vehicles',
        'characters'
    ]
    
    for table in tables:
        cur.execute(f"DELETE FROM {table} WHERE character_id = %s", (character_id,))

def assert_character_exists(conn, character_id: int) -> bool:
    """Assert that a character exists
    
    Args:
        conn: Database connection
        character_id: Character ID
    
    Returns:
        True if character exists
    
    Raises:
        AssertionError if character doesn't exist
    """
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM characters WHERE id = %s", (character_id,))
    count = cur.fetchone()[0]
    
    assert count == 1, f"Character {character_id} not found"
    return True

def assert_spell_learned(conn, character_id: int, spell_name: str) -> bool:
    """Assert that a character has learned a spell
    
    Args:
        conn: Database connection
        character_id: Character ID
        spell_name: Spell name
    
    Returns:
        True if spell is learned
    
    Raises:
        AssertionError if spell not learned
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) 
        FROM character_spells cs
        JOIN master_spells ms ON cs.spell_id = ms.id
        WHERE cs.character_id = %s 
          AND LOWER(ms.name) = LOWER(%s)
    """, (character_id, spell_name))
    
    count = cur.fetchone()[0]
    assert count > 0, f"Character {character_id} has not learned '{spell_name}'"
    return True
