#!/usr/bin/env python3
"""
Add Phase 1 operations to game-server.py
Adds tool definitions and handlers for all Phase 1 MCP operations
"""

# Phase 1 operations to add (excluding get_character which already exists)
PHASE1_TOOLS = [
    {
        "name": "get_skills",
        "description": "Get all skills for a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True}
        }
    },
    {
        "name": "get_character_skill",
        "description": "Get a specific skill rating for a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "skill_name": {"type": "string", "description": "Name of the skill to retrieve", "required": True}
        }
    },
    {
        "name": "add_skill",
        "description": "Add a new skill to a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "skill_name": {"type": "string", "description": "Name of the skill to add", "required": True},
            "base_rating": {"type": "number", "description": "Base rating for the skill (1-10)", "required": True},
            "specialization": {"type": "string", "description": "Optional specialization", "required": False},
            "skill_type": {"type": "string", "description": "Type of skill (e.g., 'active', 'knowledge')", "required": False},
            "reason": {"type": "string", "description": "Reason for adding the skill", "required": False}
        }
    },
    {
        "name": "improve_skill",
        "description": "Improve a character's skill rating",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "skill_name": {"type": "string", "description": "Name of the skill to improve", "required": True},
            "new_rating": {"type": "number", "description": "New rating for the skill", "required": True},
            "reason": {"type": "string", "description": "Reason for improvement", "required": False}
        }
    },
    {
        "name": "add_specialization",
        "description": "Add a specialization to a character's skill",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "skill_name": {"type": "string", "description": "Name of the skill", "required": True},
            "specialization": {"type": "string", "description": "Specialization to add", "required": True},
            "reason": {"type": "string", "description": "Reason for adding specialization", "required": False}
        }
    },
    {
        "name": "remove_skill",
        "description": "Remove a skill from a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "skill_name": {"type": "string", "description": "Name of the skill to remove", "required": True},
            "reason": {"type": "string", "description": "Reason for removal", "required": False}
        }
    },
    {
        "name": "get_spells",
        "description": "Get all spells for a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True}
        }
    },
    {
        "name": "add_spell",
        "description": "Add a new spell to a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "spell_name": {"type": "string", "description": "Name of the spell", "required": True},
            "learned_force": {"type": "number", "description": "Force at which the spell was learned", "required": True},
            "spell_category": {"type": "string", "description": "Category of spell (e.g., 'Combat', 'Detection')", "required": False},
            "spell_type": {"type": "string", "description": "Type of spell ('mana' or 'physical')", "required": False},
            "reason": {"type": "string", "description": "Reason for adding spell", "required": False}
        }
    },
    {
        "name": "update_spell",
        "description": "Update spell details for a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "spell_name": {"type": "string", "description": "Name of the spell to update", "required": True},
            "learned_force": {"type": "number", "description": "New learned force", "required": False},
            "spell_category": {"type": "string", "description": "New spell category", "required": False},
            "reason": {"type": "string", "description": "Reason for update", "required": False}
        }
    },
    {
        "name": "remove_spell",
        "description": "Remove a spell from a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "spell_name": {"type": "string", "description": "Name of the spell to remove", "required": True},
            "reason": {"type": "string", "description": "Reason for removal", "required": False}
        }
    },
    {
        "name": "get_gear",
        "description": "Get gear for a character, optionally filtered by type",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "gear_type": {"type": "string", "description": "Optional gear type filter (e.g., 'weapon', 'armor')", "required": False}
        }
    },
    {
        "name": "add_gear",
        "description": "Add gear to a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "gear_name": {"type": "string", "description": "Name of the gear", "required": True},
            "gear_type": {"type": "string", "description": "Type of gear", "required": False},
            "quantity": {"type": "number", "description": "Quantity to add", "required": False},
            "reason": {"type": "string", "description": "Reason for adding gear", "required": False}
        }
    },
    {
        "name": "update_gear_quantity",
        "description": "Update the quantity of a gear item",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "gear_name": {"type": "string", "description": "Name of the gear", "required": True},
            "quantity": {"type": "number", "description": "New quantity", "required": True},
            "reason": {"type": "string", "description": "Reason for update", "required": False}
        }
    },
    {
        "name": "remove_gear",
        "description": "Remove gear from a character",
        "params": {
            "character_name": {"type": "string", "description": "Character's street name or given name", "required": True},
            "gear_name": {"type": "string", "description": "Name of the gear to remove", "required": True},
            "reason": {"type": "string", "description": "Reason for removal", "required": False}
        }
    }
]

print("=" * 80)
print("PHASE 1 TOOLS TO ADD TO GAME-SERVER.PY")
print("=" * 80)
print(f"\nTotal tools to add: {len(PHASE1_TOOLS)}")
print("\nTools:")
for i, tool in enumerate(PHASE1_TOOLS, 1):
    print(f"{i:2}. {tool['name']}")

print("\n" + "=" * 80)
print("NOTE: This script generates the tool definitions.")
print("The actual handlers need to be added to game-server.py manually")
print("or via a separate script that modifies the file.")
print("=" * 80)
