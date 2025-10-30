# Phase 1: Game Server Integration TODO

## Status
Phase 1 MCP operations are complete and tested, but need to be added to game-server.py

## What's Already in game-server.py
- ✅ `get_character` - Already exists
- ✅ `get_character_skill` - Already exists (in tools list)
- ✅ Karma operations (add_karma, spend_karma, update_karma_pool, set_karma)
- ✅ Nuyen operations (add_nuyen, spend_nuyen)

## What Needs to Be Added (13 tools)

### Skills (4 tools)
1. **get_skills** - Get all character skills
2. **add_skill** - Add new skill
3. **improve_skill** - Improve skill rating  
4. **add_specialization** - Add specialization
5. **remove_skill** - Remove skill

### Spells (4 tools)
6. **get_spells** - Get all spells
7. **add_spell** - Add new spell
8. **update_spell** - Update spell details
9. **remove_spell** - Remove spell

### Gear (4 tools)
10. **get_gear** - Get character gear
11. **add_gear** - Add gear
12. **update_gear_quantity** - Update quantity
13. **remove_gear** - Remove gear

## Implementation Pattern

Each tool needs TWO additions to game-server.py:

### 1. Tool Definition (in tools array)
```javascript
{
    "name": "tool_name",
    "description": "Tool description",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {
                "type": "string",
                "description": "Character's street name or given name"
            },
            // ... other parameters
        },
        "required": ["character_name", /* other required params */]
    }
}
```

### 2. Tool Handler (in handle_call_tool function)
```javascript
elif tool_name == "tool_name":
    character_name = arguments.get("character_name")
    # ... get other parameters
    result = await mcp_ops.tool_name(character_name, ...)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

## Detailed Tool Specifications

### get_skills
```javascript
// Tool Definition
{
    "name": "get_skills",
    "description": "Get all skills for a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"}
        },
        "required": ["character_name"]
    }
}

// Handler
elif tool_name == "get_skills":
    character_name = arguments.get("character_name")
    result = await mcp_ops.get_skills(character_name)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### add_skill
```javascript
// Tool Definition
{
    "name": "add_skill",
    "description": "Add a new skill to a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "skill_name": {"type": "string", "description": "Name of the skill to add"},
            "base_rating": {"type": "number", "description": "Base rating for the skill (1-10)"},
            "specialization": {"type": "string", "description": "Optional specialization"},
            "skill_type": {"type": "string", "description": "Type of skill (e.g., 'active', 'knowledge')"},
            "reason": {"type": "string", "description": "Reason for adding the skill"}
        },
        "required": ["character_name", "skill_name", "base_rating"]
    }
}

// Handler
elif tool_name == "add_skill":
    character_name = arguments.get("character_name")
    skill_name = arguments.get("skill_name")
    base_rating = arguments.get("base_rating")
    specialization = arguments.get("specialization")
    skill_type = arguments.get("skill_type")
    reason = arguments.get("reason")
    result = await mcp_ops.add_skill(character_name, skill_name, base_rating, 
                                     specialization, skill_type, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### improve_skill
```javascript
// Tool Definition
{
    "name": "improve_skill",
    "description": "Improve a character's skill rating",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "skill_name": {"type": "string", "description": "Name of the skill to improve"},
            "new_rating": {"type": "number", "description": "New rating for the skill"},
            "reason": {"type": "string", "description": "Reason for improvement"}
        },
        "required": ["character_name", "skill_name", "new_rating"]
    }
}

// Handler
elif tool_name == "improve_skill":
    character_name = arguments.get("character_name")
    skill_name = arguments.get("skill_name")
    new_rating = arguments.get("new_rating")
    reason = arguments.get("reason")
    result = await mcp_ops.improve_skill(character_name, skill_name, new_rating, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### add_specialization
```javascript
// Tool Definition
{
    "name": "add_specialization",
    "description": "Add a specialization to a character's skill",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "skill_name": {"type": "string", "description": "Name of the skill"},
            "specialization": {"type": "string", "description": "Specialization to add"},
            "reason": {"type": "string", "description": "Reason for adding specialization"}
        },
        "required": ["character_name", "skill_name", "specialization"]
    }
}

// Handler
elif tool_name == "add_specialization":
    character_name = arguments.get("character_name")
    skill_name = arguments.get("skill_name")
    specialization = arguments.get("specialization")
    reason = arguments.get("reason")
    result = await mcp_ops.add_specialization(character_name, skill_name, specialization, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### remove_skill
```javascript
// Tool Definition
{
    "name": "remove_skill",
    "description": "Remove a skill from a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "skill_name": {"type": "string", "description": "Name of the skill to remove"},
            "reason": {"type": "string", "description": "Reason for removal"}
        },
        "required": ["character_name", "skill_name"]
    }
}

// Handler
elif tool_name == "remove_skill":
    character_name = arguments.get("character_name")
    skill_name = arguments.get("skill_name")
    reason = arguments.get("reason")
    result = await mcp_ops.remove_skill(character_name, skill_name, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### get_spells
```javascript
// Tool Definition
{
    "name": "get_spells",
    "description": "Get all spells for a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"}
        },
        "required": ["character_name"]
    }
}

// Handler
elif tool_name == "get_spells":
    character_name = arguments.get("character_name")
    result = await mcp_ops.get_spells(character_name)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### add_spell
```javascript
// Tool Definition
{
    "name": "add_spell",
    "description": "Add a new spell to a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "spell_name": {"type": "string", "description": "Name of the spell"},
            "learned_force": {"type": "number", "description": "Force at which the spell was learned"},
            "spell_category": {"type": "string", "description": "Category of spell (e.g., 'Combat', 'Detection')"},
            "spell_type": {"type": "string", "description": "Type of spell ('mana' or 'physical')"},
            "reason": {"type": "string", "description": "Reason for adding spell"}
        },
        "required": ["character_name", "spell_name", "learned_force"]
    }
}

// Handler
elif tool_name == "add_spell":
    character_name = arguments.get("character_name")
    spell_name = arguments.get("spell_name")
    learned_force = arguments.get("learned_force")
    spell_category = arguments.get("spell_category")
    spell_type = arguments.get("spell_type", "mana")
    reason = arguments.get("reason")
    result = await mcp_ops.add_spell(character_name, spell_name, learned_force,
                                     spell_category, spell_type, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### update_spell
```javascript
// Tool Definition
{
    "name": "update_spell",
    "description": "Update spell details for a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "spell_name": {"type": "string", "description": "Name of the spell to update"},
            "learned_force": {"type": "number", "description": "New learned force"},
            "spell_category": {"type": "string", "description": "New spell category"},
            "reason": {"type": "string", "description": "Reason for update"}
        },
        "required": ["character_name", "spell_name"]
    }
}

// Handler
elif tool_name == "update_spell":
    character_name = arguments.get("character_name")
    spell_name = arguments.get("spell_name")
    learned_force = arguments.get("learned_force")
    spell_category = arguments.get("spell_category")
    reason = arguments.get("reason")
    result = await mcp_ops.update_spell(character_name, spell_name, learned_force,
                                       spell_category, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### remove_spell
```javascript
// Tool Definition
{
    "name": "remove_spell",
    "description": "Remove a spell from a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "spell_name": {"type": "string", "description": "Name of the spell to remove"},
            "reason": {"type": "string", "description": "Reason for removal"}
        },
        "required": ["character_name", "spell_name"]
    }
}

// Handler
elif tool_name == "remove_spell":
    character_name = arguments.get("character_name")
    spell_name = arguments.get("spell_name")
    reason = arguments.get("reason")
    result = await mcp_ops.remove_spell(character_name, spell_name, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### get_gear
```javascript
// Tool Definition
{
    "name": "get_gear",
    "description": "Get gear for a character, optionally filtered by type",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "gear_type": {"type": "string", "description": "Optional gear type filter (e.g., 'weapon', 'armor')"}
        },
        "required": ["character_name"]
    }
}

// Handler
elif tool_name == "get_gear":
    character_name = arguments.get("character_name")
    gear_type = arguments.get("gear_type")
    result = await mcp_ops.get_gear(character_name, gear_type)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### add_gear
```javascript
// Tool Definition
{
    "name": "add_gear",
    "description": "Add gear to a character",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "gear_name": {"type": "string", "description": "Name of the gear"},
            "gear_type": {"type": "string", "description": "Type of gear"},
            "quantity": {"type": "number", "description": "Quantity to add"},
            "reason": {"type": "string", "description": "Reason for adding gear"}
        },
        "required": ["character_name", "gear_name"]
    }
}

// Handler
elif tool_name == "add_gear":
    character_name = arguments.get("character_name")
    gear_name = arguments.get("gear_name")
    gear_type = arguments.get("gear_type", "equipment")
    quantity = arguments.get("quantity", 1)
    reason = arguments.get("reason")
    result = await mcp_ops.add_gear(character_name, gear_name, gear_type, quantity, reason)
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
```

### update_gear_quantity
```javascript
// Tool Definition
{
    "name": "update_gear_quantity",
    "description": "Update the quantity of a gear item",
    "inputSchema": {
        "type": "object",
        "properties": {
            "character_name": {"type": "string", "description": "Character's street name or given name"},
            "gear_name": {"type": "string", "description": "Name of the gear"},
            "quantity": {"type": "number", "description": "New quantity"},
            "reason": {"type": "string", "description": "Reason for update"}
        },
        "required": ["character_name", "gear_name", "quantity"]
    }
}

// Handler
elif tool_name == "update_gear_quantity":
    character_name = arguments.get("character_name")
    gear_name = arguments.get("gear_name")
    quantity = arguments.get("quantity")
    reason = arguments.get("reason")
    result = await mcp_ops.update_gear_quantity(character_name, gear_name, quantity, reason)
    return [types.
