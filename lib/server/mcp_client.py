"""
MCP Client - Tool Routing Layer
Routes tool calls to MCPOperations
"""

from typing import Dict, Any
from lib.mcp_operations import MCPOperations


class MCPClient:
    """
    Thin wrapper around MCPOperations for backward compatibility
    All actual logic is in lib/mcp_operations.py
    """
    
    def __init__(self):
        self.ops = MCPOperations()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """
        Delegate tool calls to MCPOperations
        This maintains the same interface as before but uses the clean CRUD API
        """
        
        if tool_name == "get_character_skill":
            return await self.ops.get_character_skill(
                arguments.get('character_name'),
                arguments.get('skill_name')
            )
        
        elif tool_name == "calculate_dice_pool":
            return await self.ops.calculate_dice_pool(
                arguments.get('skill_rating'),
                arguments.get('attribute_rating'),
                arguments.get('modifiers', [])
            )
        
        elif tool_name == "calculate_target_number":
            return await self.ops.calculate_target_number(
                arguments.get('situation'),
                arguments.get('difficulty', 'average')
            )
        
        elif tool_name == "roll_dice":
            return await self.ops.roll_dice(
                arguments.get('pool'),
                arguments.get('target_number')
            )
        
        elif tool_name == "get_character":
            return await self.ops.get_character(arguments.get('character_name'))
        
        elif tool_name == "get_combat_pool":
            return await self.ops.get_combat_pool(arguments.get('character_name'))
        
        elif tool_name == "calculate_ranged_attack":
            return await self.ops.calculate_ranged_attack(
                arguments.get('character_name'),
                arguments.get('weapon_name'),
                arguments.get('target_distance'),
                arguments.get('target_description'),
                arguments.get('environment'),
                arguments.get('combat_pool', 0)
            )
        
        elif tool_name == "ranged_combat":
            return await self.ops.ranged_combat(
                arguments.get('character_name'),
                arguments.get('weapon_name'),
                arguments.get('distance'),
                arguments.get('target_name'),
                arguments.get('target_size', 'normal'),
                arguments.get('target_moving', False),
                arguments.get('target_prone', False),
                arguments.get('light_level', 'NORMAL'),
                arguments.get('conditions'),
                arguments.get('magnification', 0),
                arguments.get('called_shot', False),
                arguments.get('combat_pool', 0),
                arguments.get('reason')
            )
        
        elif tool_name == "cast_spell":
            return await self.ops.cast_spell(
                arguments.get('caster_name'),
                arguments.get('spell_name'),
                arguments.get('force'),
                arguments.get('target_name'),
                arguments.get('spell_pool_dice', 0),
                arguments.get('drain_pool_dice', 0)
            )
        
        elif tool_name == "add_karma":
            return await self.ops.add_karma(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "spend_karma":
            return await self.ops.spend_karma(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_karma_pool":
            return await self.ops.update_karma_pool(
                arguments.get('character_name'),
                arguments.get('new_pool'),
                arguments.get('reason')
            )
        
        elif tool_name == "set_karma":
            return await self.ops.set_karma(
                arguments.get('character_name'),
                arguments.get('total'),
                arguments.get('available'),
                arguments.get('reason')
            )
        
        elif tool_name == "add_nuyen":
            return await self.ops.add_nuyen(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "spend_nuyen":
            return await self.ops.spend_nuyen(
                arguments.get('character_name'),
                arguments.get('amount'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_skills":
            return await self.ops.get_skills(arguments.get('character_name'))
        
        elif tool_name == "add_skill":
            return await self.ops.add_skill(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('base_rating'),
                arguments.get('specialization'),
                arguments.get('skill_type'),
                arguments.get('reason')
            )
        
        elif tool_name == "improve_skill":
            return await self.ops.improve_skill(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('new_rating'),
                arguments.get('reason')
            )
        
        elif tool_name == "add_specialization":
            return await self.ops.add_specialization(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('specialization'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_skill":
            return await self.ops.remove_skill(
                arguments.get('character_name'),
                arguments.get('skill_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_spells":
            return await self.ops.get_spells(arguments.get('character_name'))
        
        elif tool_name == "add_spell":
            return await self.ops.add_spell(
                arguments.get('character_name'),
                arguments.get('spell_name'),
                arguments.get('learned_force'),
                arguments.get('spell_category'),
                arguments.get('spell_type', 'mana'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_spell":
            return await self.ops.update_spell(
                arguments.get('character_name'),
                arguments.get('spell_name'),
                arguments.get('learned_force'),
                arguments.get('spell_category'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_spell":
            return await self.ops.remove_spell(
                arguments.get('character_name'),
                arguments.get('spell_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_gear":
            return await self.ops.get_gear(
                arguments.get('character_name'),
                arguments.get('gear_type')
            )
        
        elif tool_name == "add_gear":
            return await self.ops.add_gear(
                arguments.get('character_name'),
                arguments.get('gear_name'),
                arguments.get('gear_type', 'equipment'),
                arguments.get('quantity', 1),
                arguments.get('reason')
            )
        
        elif tool_name == "update_gear_quantity":
            return await self.ops.update_gear_quantity(
                arguments.get('character_name'),
                arguments.get('gear_name'),
                arguments.get('quantity'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_gear":
            return await self.ops.remove_gear(
                arguments.get('character_name'),
                arguments.get('gear_name'),
                arguments.get('reason')
            )
        
        # ========== PHASE 2: AUGMENTATIONS & EQUIPMENT ==========
        
        elif tool_name == "get_cyberware":
            return await self.ops.get_cyberware(arguments.get('character_name'))
        
        elif tool_name == "get_bioware":
            return await self.ops.get_bioware(arguments.get('character_name'))
        
        elif tool_name == "add_cyberware":
            return await self.ops.add_cyberware(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('essence_cost', 0),
                arguments.get('target_name'),
                arguments.get('modifier_value', 0),
                arguments.get('modifier_data'),
                arguments.get('reason')
            )
        
        elif tool_name == "add_bioware":
            return await self.ops.add_bioware(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('essence_cost', 0),
                arguments.get('target_name'),
                arguments.get('modifier_value', 0),
                arguments.get('modifier_data'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_cyberware":
            return await self.ops.update_cyberware(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_cyberware":
            return await self.ops.remove_cyberware(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_bioware":
            return await self.ops.remove_bioware(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_vehicles":
            return await self.ops.get_vehicles(arguments.get('character_name'))
        
        elif tool_name == "add_vehicle":
            return await self.ops.add_vehicle(
                arguments.get('character_name'),
                arguments.get('vehicle_name'),
                arguments.get('vehicle_type'),
                arguments.get('handling'),
                arguments.get('speed'),
                arguments.get('body'),
                arguments.get('armor'),
                arguments.get('signature'),
                arguments.get('pilot'),
                arguments.get('modifications'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_vehicle":
            return await self.ops.update_vehicle(
                arguments.get('character_name'),
                arguments.get('vehicle_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_vehicle":
            return await self.ops.remove_vehicle(
                arguments.get('character_name'),
                arguments.get('vehicle_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_cyberdecks":
            return await self.ops.get_cyberdecks(arguments.get('character_name'))
        
        elif tool_name == "add_cyberdeck":
            return await self.ops.add_cyberdeck(
                arguments.get('character_name'),
                arguments.get('deck_name'),
                arguments.get('mpcp'),
                arguments.get('hardening'),
                arguments.get('memory'),
                arguments.get('storage'),
                arguments.get('io_speed'),
                arguments.get('response_increase'),
                arguments.get('persona_programs'),
                arguments.get('utilities'),
                arguments.get('ai_companions'),
                arguments.get('reason')
            )
        
        # ========== PHASE 3: SOCIAL & MAGICAL ==========
        
        elif tool_name == "get_contacts":
            return await self.ops.get_contacts(arguments.get('character_name'))
        
        elif tool_name == "add_contact":
            return await self.ops.add_contact(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('archetype'),
                arguments.get('loyalty', 1),
                arguments.get('connection', 1),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_contact_loyalty":
            return await self.ops.update_contact_loyalty(
                arguments.get('character_name'),
                arguments.get('contact_name'),
                arguments.get('loyalty'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_spirits":
            return await self.ops.get_spirits(arguments.get('character_name'))
        
        elif tool_name == "add_spirit":
            return await self.ops.add_spirit(
                arguments.get('character_name'),
                arguments.get('spirit_name'),
                arguments.get('spirit_type'),
                arguments.get('force', 1),
                arguments.get('services', 1),
                arguments.get('special_abilities'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_spirit_services":
            return await self.ops.update_spirit_services(
                arguments.get('character_name'),
                arguments.get('spirit_name'),
                arguments.get('services'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_foci":
            return await self.ops.get_foci(arguments.get('character_name'))
        
        elif tool_name == "add_focus":
            return await self.ops.add_focus(
                arguments.get('character_name'),
                arguments.get('focus_name'),
                arguments.get('focus_type'),
                arguments.get('force'),
                arguments.get('spell_category'),
                arguments.get('specific_spell'),
                arguments.get('bonus_dice', 0),
                arguments.get('tn_modifier', 0),
                arguments.get('bonded', True),
                arguments.get('karma_cost'),
                arguments.get('description'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_powers":
            return await self.ops.get_powers(arguments.get('character_name'))
        
        elif tool_name == "add_power":
            return await self.ops.add_power(
                arguments.get('character_name'),
                arguments.get('power_name'),
                arguments.get('level', 1),
                arguments.get('cost', 0),
                arguments.get('reason')
            )
        
        elif tool_name == "update_power_level":
            return await self.ops.update_power_level(
                arguments.get('character_name'),
                arguments.get('power_name'),
                arguments.get('new_level'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_edges_flaws":
            return await self.ops.get_edges_flaws(arguments.get('character_name'))
        
        elif tool_name == "add_edge_flaw":
            return await self.ops.add_edge_flaw(
                arguments.get('character_name'),
                arguments.get('name'),
                arguments.get('type'),
                arguments.get('description'),
                arguments.get('cost'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_relationships":
            return await self.ops.get_relationships(arguments.get('character_name'))
        
        elif tool_name == "add_relationship":
            return await self.ops.add_relationship(
                arguments.get('character_name'),
                arguments.get('relationship_type'),
                arguments.get('relationship_name'),
                arguments.get('data'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        # ========== PHASE 4: GAME STATE MANAGEMENT ==========
        
        elif tool_name == "get_active_effects":
            return await self.ops.get_active_effects(arguments.get('character_name'))
        
        elif tool_name == "add_active_effect":
            return await self.ops.add_active_effect(
                arguments.get('character_name'),
                arguments.get('effect_name'),
                arguments.get('effect_type'),
                arguments.get('duration'),
                arguments.get('modifier_value'),
                arguments.get('target_attribute'),
                arguments.get('description'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_effect_duration":
            return await self.ops.update_effect_duration(
                arguments.get('character_name'),
                arguments.get('effect_name'),
                arguments.get('new_duration'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_active_effect":
            return await self.ops.remove_active_effect(
                arguments.get('character_name'),
                arguments.get('effect_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_modifiers":
            return await self.ops.get_modifiers(
                arguments.get('character_name'),
                arguments.get('modifier_type')
            )
        
        elif tool_name == "add_modifier":
            return await self.ops.add_modifier(
                arguments.get('character_name'),
                arguments.get('modifier_name'),
                arguments.get('modifier_type'),
                arguments.get('target_name'),
                arguments.get('modifier_value', 0),
                arguments.get('modifier_data'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_modifier":
            return await self.ops.update_modifier(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "remove_modifier":
            return await self.ops.remove_modifier(
                arguments.get('character_name'),
                arguments.get('modifier_id'),
                arguments.get('reason')
            )
        
        # ========== PHASE 5: CAMPAIGN MANAGEMENT ==========
        
        elif tool_name == "get_house_rules":
            return await self.ops.get_house_rules()
        
        elif tool_name == "add_house_rule":
            return await self.ops.add_house_rule(
                arguments.get('rule_name'),
                arguments.get('rule_type'),
                arguments.get('description'),
                arguments.get('mechanical_effect'),
                arguments.get('is_active', True),
                arguments.get('reason')
            )
        
        elif tool_name == "toggle_house_rule":
            return await self.ops.toggle_house_rule(
                arguments.get('rule_name'),
                arguments.get('is_active'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_campaign_npcs":
            return await self.ops.get_campaign_npcs()
        
        elif tool_name == "add_campaign_npc":
            return await self.ops.add_campaign_npc(
                arguments.get('npc_name'),
                arguments.get('npc_type'),
                arguments.get('role'),
                arguments.get('stats'),
                arguments.get('notes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_campaign_npc":
            return await self.ops.update_campaign_npc(
                arguments.get('npc_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "get_audit_log":
            return await self.ops.get_audit_log(
                arguments.get('character_name'),
                arguments.get('limit', 100)
            )
        
        # ========== PHASE 6: CHARACTER MANAGEMENT ==========
        
        elif tool_name == "create_character":
            return await self.ops.create_character(
                arguments.get('street_name'),
                arguments.get('given_name'),
                arguments.get('archetype'),
                arguments.get('metatype', 'Human'),
                arguments.get('attributes'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_character_info":
            return await self.ops.update_character_info(
                arguments.get('character_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        elif tool_name == "delete_character":
            return await self.ops.delete_character(
                arguments.get('character_name'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_attribute":
            return await self.ops.update_attribute(
                arguments.get('character_name'),
                arguments.get('attribute_name'),
                arguments.get('new_value'),
                arguments.get('reason')
            )
        
        elif tool_name == "update_derived_stats":
            return await self.ops.update_derived_stats(
                arguments.get('character_name'),
                arguments.get('updates'),
                arguments.get('reason')
            )
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
