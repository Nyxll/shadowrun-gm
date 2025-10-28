#!/usr/bin/env python3
"""
Export the actual database schema to update schema.sql
"""
import os
from dotenv import load_dotenv
import psycopg

load_dotenv()

def get_table_definition(conn, table_name):
    """Get CREATE TABLE statement for a table"""
    cur = conn.cursor()
    
    # Get columns
    cur.execute("""
        SELECT 
            column_name,
            data_type,
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = %s 
        ORDER BY ordinal_position
    """, (table_name,))
    
    columns = cur.fetchall()
    
    # Get constraints
    cur.execute("""
        SELECT
            tc.constraint_type,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
            ON tc.constraint_name = kcu.constraint_name
        LEFT JOIN information_schema.constraint_column_usage AS ccu
            ON ccu.constraint_name = tc.constraint_name
        WHERE tc.table_name = %s
    """, (table_name,))
    
    constraints = cur.fetchall()
    cur.close()
    
    # Build CREATE TABLE statement
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
    
    col_defs = []
    for col in columns:
        col_name, data_type, max_len, nullable, default = col
        
        # Build column definition
        col_def = f"    {col_name} "
        
        # Data type
        if data_type == 'character varying':
            col_def += f"VARCHAR({max_len})"
        elif data_type == 'timestamp without time zone':
            col_def += "TIMESTAMP"
        elif data_type == 'ARRAY':
            col_def += "TEXT[]"
        else:
            col_def += data_type.upper()
        
        # Nullable
        if nullable == 'NO':
            col_def += " NOT NULL"
        
        # Default
        if default:
            if 'gen_random_uuid' in default:
                col_def += " DEFAULT gen_random_uuid()"
            elif 'now()' in default.lower():
                col_def += " DEFAULT NOW()"
            elif default.startswith("'"):
                col_def += f" DEFAULT {default}"
            else:
                col_def += f" DEFAULT {default}"
        
        col_defs.append(col_def)
    
    sql += ",\n".join(col_defs)
    
    # Add constraints
    for constraint in constraints:
        const_type, col_name, foreign_table, foreign_col = constraint
        if const_type == 'PRIMARY KEY':
            sql += f",\n    PRIMARY KEY ({col_name})"
        elif const_type == 'FOREIGN KEY' and foreign_table:
            sql += f",\n    FOREIGN KEY ({col_name}) REFERENCES {foreign_table}({foreign_col}) ON DELETE CASCADE"
        elif const_type == 'UNIQUE':
            sql += f",\n    UNIQUE ({col_name})"
    
    sql += "\n);\n"
    
    return sql

def main():
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST'),
        port=int(os.getenv('POSTGRES_PORT')),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB')
    )
    
    # Get all tables
    cur = conn.cursor()
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY tablename
    """)
    
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    
    print("-- ============================================================================")
    print("-- SHADOWRUN GM - ACTUAL DATABASE SCHEMA")
    print("-- Exported from live database")
    print(f"-- Tables: {len(tables)}")
    print("-- ============================================================================\n")
    
    for table in tables:
        print(f"-- {table}")
        print(get_table_definition(conn, table))
        print()
    
    conn.close()

if __name__ == "__main__":
    main()
