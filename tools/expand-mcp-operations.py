#!/usr/bin/env python3
"""
Generate complete mcp_operations.py with all CRUD wrappers
"""

# Template for each operation type
TEMPLATE = '''
    async def {method_name}(self, character_name: str{extra_params}) -> Dict:
        """{docstring}"""
        logger.info(f"{log_message}")
        try:
            try:
                character = self.crud.get_character_by_street_name(character_name)
            except ValueError:
                character = self.crud.get_character_by_given_name(character_name)
            
            result = self.crud.{crud_method}(character['id']{crud_params})
            
            return {{
                "character": character_name,
                {return_fields}
                "summary": f"{summary}"
            }}
        except ValueError as e:
            return {{"error": str(e)}}
'''

# Define all operations to add
operations = [
    # Character retrieval
    {
        'method_name': 'get_character',
        'extra_params': '',
        'docstring': 'Get full character sheet',
        'log_message': 'Getting character {character_name}',
        'crud_method': 'get_character',
        'crud_params': '',
        'return_fields': '"data": result,',
        'summary': 'Retrieved character {character_name}'
    },
    
    # Skills
    {
        'method_name': 'get_skills',
        'extra_params': '',
        'docstring': 'Get all character skills',
        'log_message': 'Getting skills for {character_name}',
        'crud_method': 'get_skills',
        'crud_params': '',
        'return_fields': '"skills": result,',
        'summary': 'Retrieved {len(result)} skills for {character_name}'
    },
    {
        'method_name': 'add_skill',
        'extra_params': ', skill_name: str, base_rating: int, specialization: str = None, skill_type: str = None, reason: str = None',
        'docstring': 'Add a new skill to character',
        'log_message': 'Adding skill {skill_name} to {character_name}',
        'crud_method': 'add_skill',
        'crud_params': ', {"skill_name": skill_name, "base_rating": base_rating, "specialization": specialization, "skill_type": skill_type}, reason',
        'return_fields': '"skill_added": skill_name, "rating": base_rating,',
        'summary': 'Added skill {skill_name} ({base_rating}) to {character_name}'
    },
    {
        'method_name': 'improve_skill',
        'extra_params': ', skill_name: str, new_rating: int, reason: str = None',
        'docstring': 'Improve a skill rating',
        'log_message': 'Improving {skill_name} to {new_rating} for {character_name}',
        'crud_method': 'improve_skill',
        'crud_params': ', skill_name, new_rating, reason',
        'return_fields': '"skill": skill_name, "new_rating": new_rating,',
        'summary': 'Improved {skill_name} to {new_rating} for {character_name}'
    },
    
    # Spells
    {
        'method_name': 'get_spells',
        'extra_params': '',
        'docstring': 'Get all character spells',
        'log_message': 'Getting spells for {character_name}',
        'crud_method': 'get_spells',
        'crud_params': '',
        'return_fields': '"spells": result,',
        'summary': 'Retrieved {len(result)} spells for {character_name}'
    },
    {
        'method_name': 'add_spell',
        'extra_params': ', spell_name: str, learned_force: int, spell_category: str = None, spell_type: str = "mana", reason: str = None',
        'docstring': 'Add a new spell to character',
        'log_message': 'Adding spell {spell_name} (Force {learned_force}) to {character_name}',
        'crud_method': 'add_spell',
        'crud_params': ', {"spell_name": spell_name, "learned_force": learned_force, "spell_category": spell_category, "spell_type": spell_type}, reason',
        'return_fields': '"spell_added": spell_name, "force": learned_force,',
        'summary': 'Added spell {spell_name} (Force {learned_force}) to {character_name}'
    },
    
    # Gear
    {
        'method_name': 'get_gear',
        'extra_params': ', gear_type: str = None',
        'docstring': 'Get character gear',
        'log_message': 'Getting gear for {character_name}',
        'crud_method': 'get_gear',
        'crud_params': ', gear_type',
        'return_fields': '"gear": result,',
        'summary': 'Retrieved {len(result)} gear items for {character_name}'
    },
    {
        'method_name': 'add_gear',
        'extra_params': ', gear_name: str, gear_type: str = "equipment", quantity: int = 1, reason: str = None',
        'docstring': 'Add gear to character',
        'log_message': 'Adding {quantity}x {gear_name} to {character_name}',
        'crud_method': 'add_gear',
        'crud_params': ', {"gear_name": gear_name, "gear_type": gear_type, "quantity": quantity}, reason',
        'return_fields': '"gear_added": gear_name, "quantity": quantity,',
        'summary': 'Added {quantity}x {gear_name} to {character_name}'
    },
    
    # Cyberware
    {
        'method_name': 'get_cyberware',
        'extra_params': '',
        'docstring': 'Get character cyberware',
        'log_message': 'Getting cyberware for {character_name}',
        'crud_method': 'get_character_cyberware',
        'crud_params': '',
        'return_fields': '"cyberware": result,',
        'summary': 'Retrieved {len(result)} cyberware items for {character_name}'
    },
    {
        'method_name': 'add_cyberware',
        'extra_params': ', name: str, target_name: str = None, modifier_value: int = 0, essence_cost: float = 0, reason: str = None',
        'docstring': 'Add cyberware to character',
        'log_message': 'Adding cyberware {name} to {character_name}',
        'crud_method': 'add_cyberware',
        'crud_params': ', {"name": name, "target_name": target_name, "modifier_value": modifier_value, "modifier_data": {"essence_cost": essence_cost}}, reason',
        'return_fields': '"cyberware_added": name, "essence_cost": essence_cost,',
        'summary': 'Added cyberware {name} to {character_name} (Essence: {essence_cost})'
    },
    
    # Contacts
    {
        'method_name': 'get_contacts',
        'extra_params': '',
        'docstring': 'Get character contacts',
        'log_message': 'Getting contacts for {character_name}',
        'crud_method': 'get_contacts',
        'crud_params': '',
        'return_fields': '"contacts": result,',
        'summary': 'Retrieved {len(result)} contacts for {character_name}'
    },
    {
        'method_name': 'add_contact',
        'extra_params': ', name: str, archetype: str = None, loyalty: int = 1, connection: int = 1, reason: str = None',
        'docstring': 'Add contact to character',
        'log_message': 'Adding contact {name} to {character_name}',
        'crud_method': 'add_contact',
        'crud_params': ', {"name": name, "archetype": archetype, "loyalty": loyalty, "connection": connection}, reason',
        'return_fields': '"contact_added": name, "loyalty": loyalty, "connection": connection,',
        'summary': 'Added contact {name} (L{loyalty}/C{connection}) to {character_name}'
    },
]

print("Generated operation templates:")
print("=" * 80)
for op in operations:
    print(f"\n{op['method_name']}: {op['docstring']}")

print("\n" + "=" * 80)
print(f"Total operations to add: {len(operations)}")
print("\nNOTE: This is a template generator. The actual implementation")
print("should be done carefully with proper error handling and validation.")
