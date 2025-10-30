#!/usr/bin/env python3
"""
Generate tool definitions for Phases 4, 5, and 6
Complete the remaining 20 tool definitions
"""

print("""
=============================================================================
REMAINING TOOL DEFINITIONS - PHASES 4, 5, 6
=============================================================================

Add these after Phase 3 definitions in game-server.py get_mcp_tool_definitions()

PHASE 4: GAME STATE MANAGEMENT (8 tools)
PHASE 5: CAMPAIGN MANAGEMENT (7 tools)
PHASE 6: CHARACTER MANAGEMENT (5 tools)

Total: 20 tool definitions

=============================================================================
""")

phase4_5_6 = '''
        # ========== PHASE 4: GAME STATE MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_active_effects",
                "description": "Get all active effects on a character",
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
                "name": "add_active_effect",
                "description": "Add an active effect to a character (buffs, debuffs, conditions)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "effect_name": {
                            "type": "string",
                            "description": "Name of the effect"
                        },
                        "effect_type": {
                            "type": "string",
                            "description": "Type of effect (e.g., 'buff', 'debuff', 'condition')"
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Duration in combat turns or minutes"
                        },
                        "modifier_value": {
                            "type": "integer",
                            "description": "Modifier value (e.g., +2, -1)"
                        },
                        "target_attribute": {
                            "type": "string",
                            "description": "Attribute or skill affected"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the effect"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding effect"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "effect_name": {
                            "type": "string",
                            "description": "Name of the effect"
                        },
                        "new_duration": {
                            "type": "integer",
                            "description": "New duration value"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "effect_name": {
                            "type": "string",
                            "description": "Name of the effect to remove"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for removal"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_type": {
                            "type": "string",
                            "description": "Optional filter by type (e.g., 'cyberware', 'spell', 'gear')"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_name": {
                            "type": "string",
                            "description": "Name of the modifier"
                        },
                        "modifier_type": {
                            "type": "string",
                            "description": "Type of modifier"
                        },
                        "target_name": {
                            "type": "string",
                            "description": "What this modifies (attribute, skill, etc.)"
                        },
                        "modifier_value": {
                            "type": "integer",
                            "description": "Modifier value"
                        },
                        "modifier_data": {
                            "type": "object",
                            "description": "Additional modifier data"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding modifier"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the modifier"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update"
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
                "name": "remove_modifier",
                "description": "Remove a modifier from a character",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "modifier_id": {
                            "type": "string",
                            "description": "UUID of the modifier to remove"
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
        # ========== PHASE 5: CAMPAIGN MANAGEMENT ==========
        {
            "type": "function",
            "function": {
                "name": "get_house_rules",
                "description": "Get all house rules for the campaign",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
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
                        "rule_name": {
                            "type": "string",
                            "description": "Name of the house rule"
                        },
                        "rule_type": {
                            "type": "string",
                            "description": "Type of rule (e.g., 'combat', 'magic', 'social')"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the rule"
                        },
                        "mechanical_effect": {
                            "type": "string",
                            "description": "Mechanical effect of the rule"
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "Whether the rule is currently active"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding rule"
                        }
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
                        "rule_name": {
                            "type": "string",
                            "description": "Name of the house rule"
                        },
                        "is_active": {
                            "type": "boolean",
                            "description": "New active status"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for toggle"
                        }
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
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
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
                        "npc_name": {
                            "type": "string",
                            "description": "Name of the NPC"
                        },
                        "npc_type": {
                            "type": "string",
                            "description": "Type of NPC (e.g., 'ally', 'enemy', 'neutral')"
                        },
                        "role": {
                            "type": "string",
                            "description": "Role in the campaign"
                        },
                        "stats": {
                            "type": "object",
                            "description": "NPC stats and abilities"
                        },
                        "notes": {
                            "type": "string",
                            "description": "Notes about the NPC"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for adding NPC"
                        }
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
                        "npc_name": {
                            "type": "string",
                            "description": "Name of the NPC"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character name (optional, omit for campaign-wide)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of entries to return"
                        }
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
                        "street_name": {
                            "type": "string",
                            "description": "Character's street name"
                        },
                        "given_name": {
                            "type": "string",
                            "description": "Character's given name"
                        },
                        "archetype": {
                            "type": "string",
                            "description": "Character archetype"
                        },
                        "metatype": {
                            "type": "string",
                            "description": "Metatype (Human, Elf, Dwarf, Ork, Troll)"
                        },
                        "attributes": {
                            "type": "object",
                            "description": "Starting attributes"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for creation"
                        }
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
                        "character_name": {
                            "type": "string",
                            "description": "Character's street name or given name"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Fields to update (street_name, given_name, etc.)"
                        },
                        "reason": {
                            "type": "string",
                            "description": "Reason for update"
                        }
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
                    "
