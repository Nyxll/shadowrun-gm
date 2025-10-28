#!/usr/bin/env python3
"""Create a test Leviathan shaman for totem opposition testing"""
import os
import uuid
from dotenv import load_dotenv
import psycopg

load_dotenv()

conn = psycopg.connect(
    host=os.getenv('POSTGRES_HOST'),
    port=os.getenv('POSTGRES_PORT'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    dbname=os.getenv('POSTGRES_DB')
)

cur = conn.cursor()

# Delete existing Leviathan totem and character if they exist
cur.execute("DELETE FROM character_spells WHERE character_id IN (SELECT id FROM characters WHERE name = 'Test Leviathan')")
cur.execute("DELETE FROM character_skills WHERE character_id IN (SELECT id FROM characters WHERE name = 'Test Leviathan')")
cur.execute("DELETE FROM characters WHERE name = 'Test Leviathan'")
cur.execute("DELETE FROM totems WHERE totem_name = 'Leviathan'")

# Create Leviathan totem (favors Combat, opposes Illusion)
cur.execute("""
    INSERT INTO totems (totem_name, favored_categories, opposed_categories, bonus_dice, penalty_dice, spirit_type)
    VALUES ('Leviathan', ARRAY['Combat'], ARRAY['Illusion'], 2, -2, 'Water')
""")
print("✓ Created Leviathan totem")

# Create test character
char_id = uuid.uuid4()
cur.execute("""
    INSERT INTO characters (
        id, name, street_name, character_type, archetype,
        base_body, base_quickness, base_strength, base_charisma,
        base_intelligence, base_willpower, base_essence, base_magic, base_reaction,
        current_body, current_quickness, current_strength, current_charisma,
        current_intelligence, current_willpower, current_essence, current_magic, current_reaction,
        totem, nuyen, karma_pool
    ) VALUES (
        %s, 'Test Leviathan', 'Leviathan', 'Player Character', 'Shaman',
        5, 4, 4, 5,
        5, 6, 6.0, 6, 5,
        5, 4, 4, 5,
        5, 6, 6.0, 6, 5,
        'Leviathan', 5000, 3
    )
""", (char_id,))
print(f"✓ Created test character (ID: {char_id})")

# Add Sorcery skill
cur.execute("""
    INSERT INTO character_skills (character_id, skill_name, skill_type, base_rating, current_rating)
    VALUES (%s, 'Sorcery', 'active', 6, 6)
""", (char_id,))

# Add a Combat spell (Manabolt) at Force 6
cur.execute("""
    INSERT INTO character_spells (character_id, spell_name, spell_category, spell_type, drain_modifier, learned_force)
    VALUES (%s, 'Manabolt', 'combat', 'mana', 0, 6)
""", (char_id,))

# Add an Illusion spell (Invisibility) at Force 6
cur.execute("""
    INSERT INTO character_spells (character_id, spell_name, spell_category, spell_type, drain_modifier, learned_force)
    VALUES (%s, 'Invisibility', 'illusion', 'mana', 0, 6)
""", (char_id,))

conn.commit()

print("\n✓ Test shaman ready!")
print("\nCharacter details:")
print("  Name: Test Leviathan")
print("  Totem: Leviathan (favors Combat, opposes Illusion)")
print("  Magic: 6")
print("  Sorcery: 6")
print("  Willpower: 6")
print("  Spells: Manabolt (Combat), Invisibility (Illusion)")

cur.close()
conn.close()
