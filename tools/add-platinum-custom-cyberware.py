#!/usr/bin/env python3
"""
Add Platinum's custom cyberware to house rules
- Smartlink-3 AEGIS
- NeuroSync Processor
"""
import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=int(os.getenv('POSTGRES_PORT')),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

with conn.cursor(row_factory=dict_row) as cur:
    # Check if rules already exist
    cur.execute("SELECT rule_name FROM house_rules WHERE rule_name IN ('Smartlink-3 AEGIS', 'NeuroSync Processor')")
    existing = {row['rule_name'] for row in cur.fetchall()}
    
    # Add Smartlink-3 AEGIS
    if 'Smartlink-3 AEGIS' not in existing:
        cur.execute("""
            INSERT INTO house_rules (rule_name, rule_type, description, rule_config, is_active)
            VALUES (
                'Smartlink-3 AEGIS',
                'custom_cyberware',
                'Enhanced smartlink system with Project AEGIS software integration. Provides superior targeting assistance beyond standard smartlink-2 systems.',
                '{"tn_modifier": -3, "essence_cost": 0.5, "special_abilities": ["grenade_bonus", "no_mag_penalty", "advanced_targeting"]}'::jsonb,
                true
            )
        """)
        print("✓ Added Smartlink-3 AEGIS house rule")
    else:
        print("⊙ Smartlink-3 AEGIS already exists")
    
    # Add NeuroSync Processor
    if 'NeuroSync Processor' not in existing:
        cur.execute("""
            INSERT INTO house_rules (rule_name, rule_type, description, rule_config, is_active)
            VALUES (
                'NeuroSync Processor',
                'custom_cyberware',
                'Advanced neural processor that enhances Matrix initiative through optimized neural pathways and data processing.',
                '{"essence_cost": 0.5, "body_index_cost": 0.5, "matrix_initiative_bonus": "2D6"}'::jsonb,
                true
            )
        """)
        print("✓ Added NeuroSync Processor house rule")
    else:
        print("⊙ NeuroSync Processor already exists")
    
    conn.commit()
    
    # Verify
    cur.execute("""
        SELECT rule_name, rule_type, description, rule_config
        FROM house_rules
        WHERE rule_name IN ('Smartlink-3 AEGIS', 'NeuroSync Processor')
        ORDER BY rule_name
    """)
    
    print("\nVerification:")
    for row in cur.fetchall():
        print(f"\n{row['rule_name']} ({row['rule_type']}):")
        print(f"  Description: {row['description']}")
        print(f"  Rule Config: {row['rule_config']}")

conn.close()
print("\n✓ Custom cyberware house rules added successfully!")
