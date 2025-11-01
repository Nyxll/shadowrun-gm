"""
MCP Tool Definitions for Grok Function Calling
All 60+ tool definitions organized by phase
"""

from typing import List, Dict


def get_mcp_tool_definitions() -> List[Dict]:
    """Get MCP tool definitions for Grok function calling"""
    return [
        {
            "type": "function",
            "function": {
                "name": "get_character_skill",
                "description": "Get a character's skill rating and associated attribute",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill (e.g., 'Street Etiquette', 'Firearms')"
                        }
                    },
                    "required": ["character_name", "skill_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_dice_pool",
                "description": "Calculate total dice pool from skill, attribute, and modifiers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_rating": {
                            "type": "integer",
                            "description": "Skill rating"
                        },
                        "attribute_rating": {
                            "type": "integer",
                            "description": "Attribute rating"
                        },
                        "modifiers": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "List of modifier values (e.g., [2, -1])"
                        }
                    },
                    "required": ["skill_rating", "attribute_rating"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_target_number",
                "description": "Calculate target number for a situation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "situation": {
                            "type": "string",
                            "description": "Description of the situation"
                        },
                        "difficulty": {
                            "type": "string",
                            "enum": ["trivial", "easy", "average", "difficult", "very_difficult"],
                            "description": "Difficulty level"
                        }
                    },
                    "required": ["situation"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "roll_dice",
                "description": "Roll dice pool against target number (Shadowrun style with exploding 6s)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pool": {
                            "type": "integer",
                            "description": "Number of dice to roll"
                        },
                        "target_number": {
                            "type": "integer",
                            "description": "Target number for successes"
                        }
                    },
                    "required": ["pool", "target_number"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_character",
                "description": "Get full character data including attributes, skills, and gear",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_combat_pool",
                "description": "Get character's combat pool and magic pool ratings. IMPORTANT: Call this BEFORE asking the user about pool dice allocation to show the correct maximum values.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "ranged_combat",
                "description": "Calculate ranged combat with SR2 rules including vision modifiers, smartlink bonuses, range categories, and automatic dice rolling. Uses official SR2 visibility table and supports variable smartlink ratings.\n\nIMPORTANT: Before calling this tool, you MUST ask the user:\n1. 'Do you want to commit combat pool dice to this attack?'\n2. If yes: 'How many combat pool dice?' (Max: character's combat pool rating)\n\nThen include the combat_pool parameter with their answer (0 if none). DO NOT make up or assume combat pool values.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character making the attack"
                        },
                        "weapon_name": {
                            "type": "string",
                            "description": "Name of the weapon being used"
                        },
                        "distance": {
                            "type": "integer",
                            "description": "Distance to target in meters"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Optional name of the target"
                        },
                        "target_size": {
                            "type": "string",
                            "enum": ["small", "normal", "large"],
                            "description": "Size of the target (small = +2 TN, normal = 0, large = -1 TN). Default: normal"
                        },
                        "target_moving": {
                            "type": "boolean",
                            "description": "Is the target moving/walking? (walking = +1 TN, running = +2 TN). Default: false"
                        },
                        "target_prone": {
                            "type": "boolean",
                            "description": "Is the target prone? (short range = -2 TN, long range = +1 TN). Default: false"
                        },
                        "light_level": {
                            "type": "string",
                            "enum": ["NORMAL", "PARTIAL", "DIM", "DARK"],
                            "description": "Light level (NORMAL, PARTIAL, DIM, DARK). DARK = pitch black (+8 TN without vision enhancement)"
                        },
                        "conditions": {
                            "type": "object",
                            "description": "Environmental conditions (glare, mist, smoke, fog, rain, etc.)"
                        },
                        "magnification": {
                            "type": "integer",
                            "description": "Optical magnification rating (affects range category calculation, each level stages range down one category)"
                        },
                        "called_shot": {
                            "type": "boolean",
                            "description": "Is this a called shot? (+4 TN). Default: false"
                        },
                        "combat_pool": {
                            "type": "integer",
                            "description": "Number of combat pool dice to add to the attack roll. Default: 0"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Optional reason for audit log"
                        }
                    },
                    "required": ["character_name", "weapon_name", "distance"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "cast_spell",
                "description": "Cast a spell in Shadowrun 2nd Edition",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "caster_name": {
                            "type": "string",
                            "description": "Name of the character casting the spell"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell being cast"
                        },
                        "force": {
                            "type": "integer",
                            "description": "Force level to cast the spell at"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Name of the target (optional)"
                        },
                        "spell_pool_dice": {
                            "type": "integer",
                            "description": "Number of Magic Pool dice to add to spellcasting"
                        },
                        "drain_pool_dice": {
                            "type": "integer",
                            "description": "Number of Magic Pool dice to add to drain resistance"
                        }
                    },
                    "required": ["caster_name", "spell_name", "force"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_karma",
                "description": "Add karma to a character's total and available pool",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of karma to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for karma award (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spend_karma",
                "description": "Spend karma from a character's available pool (with validation)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of karma to spend"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for karma expenditure (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_karma_pool",
                "description": "Update a character's karma pool (for in-game spending)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "new_pool": {
                            "type": "integer",
                            "description": "New karma pool value"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for change (optional)"
                        }
                    },
                    "required": ["character_name", "new_pool"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_karma",
                "description": "Set both total and available karma (for error correction)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "total": {
                            "type": "integer",
                            "description": "Total karma earned"
                        },
                        "available": {
                            "type": "integer",
                            "description": "Available karma to spend"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for correction (optional)"
                        }
                    },
                    "required": ["character_name", "total", "available"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_nuyen",
                "description": "Add nuyen to a character's account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of nuyen to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for payment (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "spend_nuyen",
                "description": "Spend nuyen from a character's account (with validation)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Name of the character"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "Amount of nuyen to spend"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for expenditure (optional)"
                        }
                    },
                    "required": ["character_name", "amount"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_skills",
                "description": "Get all skills for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_skill",
                "description": "Add a new skill to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to add"
                        },
                        "base_rating": {
                            "type": "integer",
                            "description": "Base rating for the skill (1-10)"
                        },
                        "specialization": {
                            "type": "string",
                            "description": "Optional specialization"
                        },
                        "skill_type": {
                            "type": "string",
                            "description": "Type of skill (e.g., 'active', 'knowledge')"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding the skill"
                        }
                    },
                    "required": ["character_name", "skill_name", "base_rating"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "improve_skill",
                "description": "Improve a character's skill rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to improve"
                        },
                        "new_rating": {
                            "type": "integer",
                            "description": "New rating for the skill"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for improvement"
                        }
                    },
                    "required": ["character_name", "skill_name", "new_rating"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_specialization",
                "description": "Add a specialization to a character's skill",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill"
                        },
                        "specialization": {
                            "type": "string",
                            "description": "Specialization to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding specialization"
                        }
                    },
                    "required": ["character_name", "skill_name", "specialization"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_skill",
                "description": "Remove a skill from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "skill_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_spells",
                "description": "Get all spells for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_spell",
                "description": "Add a new spell to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell"
                        },
                        "learned_force": {
                            "type": "integer",
                            "description": "Force at which the spell was learned"
                        },
                        "spell_category": {
                            "type": "string",
                            "description": "Category of spell (e.g., 'Combat', 'Detection')"
                        },
                        "spell_type": {
                            "type": "string",
                            "description": "Type of spell ('mana' or 'physical')"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding spell"
                        }
                    },
                    "required": ["character_name", "spell_name", "learned_force"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_spell",
                "description": "Update spell details for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell to update"
                        },
                        "learned_force": {
                            "type": "integer",
                            "description": "New learned force"
                        },
                        "spell_category": {
                            "type": "string",
                            "description": "New spell category"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "spell_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_spell",
                "description": "Remove a spell from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spell_name": {
                            "type": "string",
                            "description": "Name of the spell to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "spell_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_gear",
                "description": "Get gear for a character, optionally filtered by type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_type": {
                            "type": "string",
                            "description": "Optional gear type filter (e.g., 'weapon', 'armor')"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_gear",
                "description": "Add gear to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_name": {
                            "type": "string",
                            "description": "Name of the gear"
                        },
                        "gear_type": {
                            "type": "string",
                            "description": "Type of gear"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Quantity to add"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding gear"
                        }
                    },
                    "required": ["character_name", "gear_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_gear_quantity",
                "description": "Update the quantity of a gear item",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_name": {
                            "type": "string",
                            "description": "Name of the gear"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "New quantity"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "gear_name", "quantity"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_gear",
                "description": "Remove gear from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "gear_name": {
                            "type": "string",
                            "description": "Name of the gear to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "gear_name"]
                }
            }
        },
        # ========== PHASE 2: AUGMENTATIONS & EQUIPMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_cyberware",
                "description": "Get all cyberware for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_bioware",
                "description": "Get all bioware for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_cyberware",
                "description": "Add cyberware to a character with essence cost and modifiers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the cyberware"
                        },
                        "essence_cost": {
                            "type": "number",
                            "description": "Essence cost of the cyberware"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Attribute or skill this modifies (optional)"
                        },
                        "modifier_value": {
                            "type": "integer",
                            "description": "Modifier value (e.g., +2 for skill bonus)"
                        },
                        "modifier_data": {
                            "type": "object",
                            "description": "Additional modifier data (special abilities, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding cyberware"
                        }
                    },
                    "required": ["character_name", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_bioware",
                "description": "Add bioware to a character with essence cost and modifiers",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the bioware"
                        },
                        "essence_cost": {
                            "type": "number",
                            "description": "Essence cost of the bioware"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "Attribute or skill this modifies (optional)"
                        },
                        "modifier_value": {
                            "type": "integer",
                            "description": "Modifier value (e.g., +1 for attribute bonus)"
                        },
                        "modifier_data": {
                            "type": "object",
                            "description": "Additional modifier data"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding bioware"
                        }
                    },
                    "required": ["character_name", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_cyberware",
                "description": "Update cyberware properties",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the cyberware modifier"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (essence_cost, modifier_value, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "modifier_id", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_cyberware",
                "description": "Remove cyberware from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the cyberware modifier to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "modifier_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_bioware",
                "description": "Remove bioware from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the bioware modifier to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "modifier_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_vehicles",
                "description": "Get all vehicles owned by a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_vehicle",
                "description": "Add a vehicle to a character's inventory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "vehicle_name": {
                            "type": "string",
                            "description": "Name of the vehicle"
                        },
                        "vehicle_type": {
                            "type": "string",
                            "description": "Type of vehicle (car, bike, drone, etc.)"
                        },
                        "handling": {
                            "type": "integer",
                            "description": "Handling rating"
                        },
                        "speed": {
                            "type": "integer",
                            "description": "Speed rating"
                        },
                        "body": {
                            "type": "integer",
                            "description": "Body rating"
                        },
                        "armor": {
                            "type": "integer",
                            "description": "Armor rating"
                        },
                        "signature": {
                            "type": "integer",
                            "description": "Signature rating"
                        },
                        "pilot": {
                            "type": "integer",
                            "description": "Pilot rating (for drones)"
                        },
                        "modifications": {
                            "type": "object",
                            "description": "Vehicle modifications"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding vehicle"
                        }
                    },
                    "required": ["character_name", "vehicle_name", "vehicle_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_vehicle",
                "description": "Update vehicle properties",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "vehicle_name": {
                            "type": "string",
                            "description": "Name of the vehicle to update"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (handling, speed, armor, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "vehicle_name", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_vehicle",
                "description": "Remove a vehicle from a character's inventory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "vehicle_name": {
                            "type": "string",
                            "description": "Name of the vehicle to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
                    },
                    "required": ["character_name", "vehicle_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_cyberdecks",
                "description": "Get all cyberdecks owned by a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_cyberdeck",
                "description": "Add a cyberdeck to a character with full stats",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "deck_name": {
                            "type": "string",
                            "description": "Name of the cyberdeck"
                        },
                        "mpcp": {
                            "type": "integer",
                            "description": "MPCP rating"
                        },
                        "hardening": {
                            "type": "integer",
                            "description": "Hardening rating"
                        },
                        "memory": {
                            "type": "integer",
                            "description": "Memory in MP"
                        },
                        "storage": {
                            "type": "integer",
                            "description": "Storage in MP"
                        },
                        "io_speed": {
                            "type": "integer",
                            "description": "I/O speed"
                        },
                        "response_increase": {
                            "type": "integer",
                            "description": "Response increase"
                        },
                        "persona_programs": {
                            "type": "array",
                            "description": "List of persona programs"
                        },
                        "utilities": {
                            "type": "array",
                            "description": "List of utility programs"
                        },
                        "ai_companions": {
                            "type": "array",
                            "description": "List of AI companions"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding cyberdeck"
                        }
                    },
                    "required": ["character_name", "deck_name"]
                }
            }
        },
        # ========== PHASE 3: SOCIAL & MAGICAL ==========
        {
            "type": "function",
            "function": {
                "name": "get_contacts",
                "description": "Get all contacts for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_contact",
                "description": "Add a contact to a character's network",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the contact"
                        },
                        "archetype": {
                            "type": "string",
                            "description": "Contact's archetype/profession"
                        },
                        "loyalty": {
                            "type": "integer",
                            "description": "Loyalty rating (1-6)"
                        },
                        "connection": {
                            "type": "integer",
                            "description": "Connection rating (1-6)"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the contact"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding contact"
                        }
                    },
                    "required": ["character_name", "name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_contact_loyalty",
                "description": "Update a contact's loyalty rating",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "contact_name": {
                            "type": "string",
                            "description": "Name of the contact"
                        },
                        "loyalty": {
                            "type": "integer",
                            "description": "New loyalty rating (1-6)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for loyalty change"
                        }
                    },
                    "required": ["character_name", "contact_name", "loyalty"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_spirits",
                "description": "Get all spirits bound to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_spirit",
                "description": "Add a bound spirit to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spirit_name": {
                            "type": "string",
                            "description": "Name of the spirit"
                        },
                        "spirit_type": {
                            "type": "string",
                            "description": "Type of spirit (e.g., 'City', 'Nature', 'Elemental')"
                        },
                        "force": {
                            "type": "integer",
                            "description": "Force rating of the spirit"
                        },
                        "services": {
                            "type": "integer",
                            "description": "Number of services owed"
                        },
                        "special_abilities": {
                            "type": "array",
                            "description": "List of special abilities"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the spirit"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding spirit"
                        }
                    },
                    "required": ["character_name", "spirit_name", "spirit_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_spirit_services",
                "description": "Update the number of services a spirit owes",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "spirit_name": {
                            "type": "string",
                            "description": "Name of the spirit"
                        },
                        "services": {
                            "type": "integer",
                            "description": "New number of services"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
                    },
                    "required": ["character_name", "spirit_name", "services"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_foci",
                "description": "Get all magical foci owned by a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_focus",
                "description": "Add a magical focus to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "focus_name": {
                            "type": "string",
                            "description": "Name of the focus"
                        },
                        "focus_type": {
                            "type": "string",
                            "description": "Type of focus (e.g., 'Spell', 'Power', 'Weapon')"
                        },
                        "force": {
                            "type": "integer",
                            "description": "Force rating of the focus"
                        },
                        "spell_category": {
                            "type": "string",
                            "description": "Spell category if spell focus"
                        },
                        "specific_spell": {
                            "type": "string",
                            "description": "Specific spell if spell focus"
                        },
                        "bonus_dice": {
                            "type": "integer",
                            "description": "Bonus dice provided"
                        },
                        "tn_modifier": {
                            "type": "integer",
                            "description": "Target number modifier"
                        },
                        "bonded": {
                            "type": "boolean",
                            "description": "Whether the focus is bonded"
                        },
                        "karma_cost": {
                            "type": "integer",
                            "description": "Karma cost to bond"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the focus"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Additional notes"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding focus"
                        }
                    },
                    "required": ["character_name", "focus_name", "focus_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_powers",
                "description": "Get all adept powers for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_power",
                "description": "Add an adept power to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "power_name": {
                            "type": "string",
                            "description": "Name of the power"
                        },
                        "level": {
                            "type": "integer",
                            "description": "Level of the power"
                        },
                        "cost": {
                            "type": "number",
                            "description": "Power point cost"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding power"
                        }
                    },
                    "required": ["character_name", "power_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_power_level",
                "description": "Update the level of an adept power",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "power_name": {
                            "type": "string",
                            "description": "Name of the power"
                        },
                        "new_level": {
                            "type": "integer",
                            "description": "New level for the power"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for level change"
                        }
                    },
                    "required": ["character_name", "power_name", "new_level"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_edges_flaws",
                "description": "Get all edges and flaws for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_edge_flaw",
                "description": "Add an edge or flaw to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "name": {
                            "type": "string",
                            "description": "Name of the edge or flaw"
                        },
                        "type": {
                            "type": "string",
                            "description": "Type: 'edge' or 'flaw'"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the edge/flaw"
                        },
                        "cost": {
                            "type": "integer",
                            "description": "Point cost (positive for edges, negative for flaws)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding"
                        }
                    },
                    "required": ["character_name", "name", "type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_relationships",
                "description": "Get all relationships for a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        }
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_relationship",
                "description": "Add a relationship to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "relationship_type": {
                            "type": "string",
                            "description": "Type of relationship (e.g., 'ally', 'enemy', 'family')"
                        },
                        "relationship_name": {
                            "type": "string",
                            "description": "Name of the related person/entity"
                        },
                        "data": {
                            "type": "object",
                            "description": "Additional relationship data"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the relationship"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding relationship"
                        }
                    },
                    "required": ["character_name", "relationship_type", "relationship_name"]
                }
            }
        },
        # ========== PHASE 4: GAME STATE MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_active_effects",
                "description": "Get all active effects on a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"}
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_active_effect",
                "description": "Add an active effect to a character (buffs, debuffs, conditions)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "effect_name": {"type": "string", "description": "Name of the effect"},
                        "effect_type": {"type": "string", "description": "Type of effect"},
                        "duration": {"type": "integer", "description": "Duration in turns/minutes"},
                        "modifier_value": {"type": "integer", "description": "Modifier value"},
                        "target_attribute": {"type": "string", "description": "Attribute affected"},
                        "description": {"type": "string", "description": "Effect description"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["character_name", "effect_name", "effect_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_effect_duration",
                "description": "Update the duration of an active effect",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "effect_name": {"type": "string", "description": "Name of the effect"},
                        "new_duration": {"type": "integer", "description": "New duration value"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "effect_name", "new_duration"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_active_effect",
                "description": "Remove an active effect from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "effect_name": {"type": "string", "description": "Name of the effect to remove"},
                        "reason": {"type": "string", "description": "Reason for removal"}
                    },
                    "required": ["character_name", "effect_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_modifiers",
                "description": "Get all modifiers for a character, optionally filtered by type",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_type": {"type": "string", "description": "Optional filter by type"}
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_modifier",
                "description": "Add a generic modifier to a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_name": {"type": "string", "description": "Name of the modifier"},
                        "modifier_type": {"type": "string", "description": "Type of modifier"},
                        "target_name": {"type": "string", "description": "What this modifies"},
                        "modifier_value": {"type": "integer", "description": "Modifier value"},
                        "modifier_data": {"type": "object", "description": "Additional data"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["character_name", "modifier_name", "modifier_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_modifier",
                "description": "Update a modifier's properties",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_id": {"type": "string", "description": "UUID of the modifier"},
                        "updates": {"type": "object", "description": "Fields to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "modifier_id", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "remove_modifier",
                "description": "Remove a modifier from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "modifier_id": {"type": "string", "description": "UUID of the modifier to remove"},
                        "reason": {"type": "string", "description": "Reason for removal"}
                    },
                    "required": ["character_name", "modifier_id"]
                }
            }
        },
        # ========== PHASE 5: CAMPAIGN MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_house_rules",
                "description": "Get all house rules for the campaign",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_house_rule",
                "description": "Add a house rule to the campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule_name": {"type": "string", "description": "Name of the house rule"},
                        "rule_type": {"type": "string", "description": "Type of rule"},
                        "description": {"type": "string", "description": "Description of the rule"},
                        "mechanical_effect": {"type": "string", "description": "Mechanical effect"},
                        "is_active": {"type": "boolean", "description": "Whether active"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["rule_name", "rule_type", "description"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "toggle_house_rule",
                "description": "Toggle a house rule on or off",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rule_name": {"type": "string", "description": "Name of the house rule"},
                        "is_active": {"type": "boolean", "description": "New active status"},
                        "reason": {"type": "string", "description": "Reason for toggle"}
                    },
                    "required": ["rule_name", "is_active"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_campaign_npcs",
                "description": "Get all campaign NPCs",
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_campaign_npc",
                "description": "Add an NPC to the campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "npc_name": {"type": "string", "description": "Name of the NPC"},
                        "npc_type": {"type": "string", "description": "Type of NPC"},
                        "role": {"type": "string", "description": "Role in campaign"},
                        "stats": {"type": "object", "description": "NPC stats"},
                        "notes": {"type": "string", "description": "Notes about NPC"},
                        "reason": {"type": "string", "description": "Reason for adding"}
                    },
                    "required": ["npc_name", "npc_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_campaign_npc",
                "description": "Update campaign NPC information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "npc_name": {"type": "string", "description": "Name of the NPC"},
                        "updates": {"type": "object", "description": "Fields to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["npc_name", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_audit_log",
                "description": "Get audit log entries for a character or campaign",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character name (optional)"},
                        "limit": {"type": "integer", "description": "Max entries to return"}
                    },
                    "required": []
                }
            }
        },
        # ========== PHASE 6: CHARACTER MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "create_character",
                "description": "Create a new character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "street_name": {"type": "string", "description": "Character's street name"},
                        "given_name": {"type": "string", "description": "Character's given name"},
                        "archetype": {"type": "string", "description": "Character archetype"},
                        "metatype": {"type": "string", "description": "Metatype"},
                        "attributes": {"type": "object", "description": "Starting attributes"},
                        "reason": {"type": "string", "description": "Reason for creation"}
                    },
                    "required": ["street_name", "archetype"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_character_info",
                "description": "Update character biographical information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "updates": {"type": "object", "description": "Fields to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "updates"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_character",
                "description": "Delete a character from the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "reason": {"type": "string", "description": "Reason for deletion"}
                    },
                    "required": ["character_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_attribute",
                "description": "Update a character's attribute value",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "attribute_name": {"type": "string", "description": "Name of the attribute"},
                        "new_value": {"type": "integer", "description": "New attribute value"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "attribute_name", "new_value"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "update_derived_stats",
                "description": "Update character's derived statistics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {"type": "string", "description": "Character's street name or given name"},
                        "updates": {"type": "object", "description": "Derived stats to update"},
                        "reason": {"type": "string", "description": "Reason for update"}
                    },
                    "required": ["character_name", "updates"]
                }
            }
        }

    ]
