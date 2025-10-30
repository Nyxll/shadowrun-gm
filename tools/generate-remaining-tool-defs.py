#!/usr/bin/env python3
"""
Generate remaining tool definitions for Phases 3-6
This outputs Python code that can be added to game-server.py
"""

# Phase 3: Social & Magical (15 tools)
phase3_tools = """
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
"""

print("Phase 3 tool definitions ready to add to game-server.py")
print("Add these after the Phase 2 definitions, before the closing ]")
print(phase3_tools)
