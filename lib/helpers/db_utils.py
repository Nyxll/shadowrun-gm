"""
Database connection utilities for all tools and tests

This module provides THE ONLY WAY to connect to the database.
All tools and tests should use these utilities instead of
reimplementing database connections.
"""
import os
import psycopg2
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Optional, Dict, Any, Tuple, List

# Load environment variables
load_dotenv()

def get_db_config() -> Dict[str, str]:
    """Get database configuration from environment
    
    Returns:
        Dictionary with database connection parameters
    """
    return {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'dbname': os.getenv('POSTGRES_DB')
    }

@contextmanager
def get_db_connection(autocommit: bool = False):
    """Context manager for database connections
    
    This is the standard way to connect to the database.
    Automatically handles commit/rollback and connection cleanup.
    
    Args:
        autocommit: If True, disable transactions (default False)
    
    Usage:
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM characters")
            results = cur.fetchall()
        # Automatic commit and connection close
    
    Yields:
        psycopg2 connection object
    """
    conn = None
    try:
        config = get_db_config()
        conn = psycopg2.connect(**config)
        if autocommit:
            conn.autocommit = True
        yield conn
        if not autocommit:
            conn.commit()
    except Exception as e:
        if conn and not autocommit:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def execute_query(
    query: str, 
    params: Optional[Tuple] = None, 
    fetch: str = 'all'
) -> Any:
    """Execute a query and return results
    
    Convenience function for simple queries that don't need
    a persistent connection.
    
    Args:
        query: SQL query string
        params: Query parameters tuple (optional)
        fetch: 'all', 'one', or 'none'
    
    Returns:
        Query results based on fetch parameter:
        - 'all': List of all rows
        - 'one': Single row or None
        - 'none': None (for INSERT/UPDATE/DELETE)
    
    Example:
        # Fetch all characters
        chars = execute_query("SELECT * FROM characters")
        
        # Fetch one character
        char = execute_query(
            "SELECT * FROM characters WHERE id = %s",
            (char_id,),
            fetch='one'
        )
        
        # Execute update
        execute_query(
            "UPDATE characters SET name = %s WHERE id = %s",
            (new_name, char_id),
            fetch='none'
        )
    """
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        
        if fetch == 'all':
            return cur.fetchall()
        elif fetch == 'one':
            return cur.fetchone()
        else:
            return None

def get_character_id(character_name: str) -> Optional[int]:
    """Get character ID by name or street name
    
    Args:
        character_name: Character name or street name
    
    Returns:
        Character ID if found, None otherwise
    
    Example:
        char_id = get_character_id("Platinum")
        if char_id:
            print(f"Found character with ID: {char_id}")
    """
    query = """
        SELECT id FROM characters 
        WHERE LOWER(name) = LOWER(%s) 
           OR LOWER(street_name) = LOWER(%s)
        LIMIT 1
    """
    result = execute_query(query, (character_name, character_name), fetch='one')
    return result[0] if result else None

def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database
    
    Args:
        table_name: Name of the table to check
    
    Returns:
        True if table exists, False otherwise
    """
    query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = %s
        )
    """
    result = execute_query(query, (table_name,), fetch='one')
    return result[0] if result else False

def get_table_columns(table_name: str) -> List[str]:
    """Get list of column names for a table
    
    Args:
        table_name: Name of the table
    
    Returns:
        List of column names
    """
    query = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s
        ORDER BY ordinal_position
    """
    results = execute_query(query, (table_name,))
    return [row[0] for row in results] if results else []
