#!/usr/bin/env python3
"""
Add get_combat_pool method to MCPOperations
This is a simple helper to get just the combat pool rating
"""

print("""
To add get_combat_pool support:

1. Add to lib/mcp_operations.py after get_character method:

    async def get_combat_pool(self, character_name: str) -> Dict:
        \"\"\"Get character's combat pool rating\"\"\"
        logger.info(f"Getting combat pool for {character_name}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            combat_pool = character.get('combat_pool', 0)
            magic_pool = character.get('magic_pool', 0)
            
            return {
                "character": character_name,
                "combat_pool": combat_pool,
                "magic_pool": magic_pool,
                "summary": f"{character_name} has Combat Pool: {combat_pool}, Magic Pool: {magic_pool}"
            }
        except ValueError as e:
            return {"error": str(e)}

2. Add to lib/server/mcp_client.py in the tool routing:

    elif tool_name == "get_combat_pool":
        result = await self.mcp_ops.get_combat_pool(
            arguments.get('character_name')
        )

3. Add to lib/server/tool_definitions.py after get_character:

    {
        "type": "function",
        "function": {
            "name": "get_combat_pool",
            "description": "Get character's combat pool and magic pool ratings. Call this BEFORE asking about pool dice allocation to show correct maximums.",
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

4. Update ranged_combat description in tool_definitions.py:

    Change: "IMPORTANT: Before calling this tool, you MUST ask the user..."
    To: "IMPORTANT: Before calling this tool:\n1. Call get_combat_pool first\n2. Ask user with correct max value\n3. Include combat_pool parameter"

This gives the AI access to the correct combat pool value before asking the user.
""")
