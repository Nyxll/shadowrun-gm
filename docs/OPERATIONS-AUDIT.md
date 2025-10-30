# Operations Audit - Complete Inventory

This document lists ALL operations available in the system across all layers.

## COMPREHENSIVE_CRUD.PY - 60+ Operations

### Character Management (5)
- `create_character(data, reason)` - Create new character
- `get_character(char_id)` - Get character by UUID
- `update_character(char_id, updates, reason)` - Update character
- `delete_character(char_id, reason)` - Delete character (hard delete)
- `list_characters(campaign_id)` - List all characters

### Character Lookup (3)
- `get_character_by_name(name, campaign_id)` - Lookup by name
- `get_character_by_street_name(street_name, campaign_id)` - Lookup by street name
- `get_character_by_given_name(given_name, campaign_id)` - Lookup by given name

### Karma Management (6)
- `add_karma(char_id, amount, reason)` - Add karma to total and available
- `spend_karma(char_id, amount, reason)` - Spend from available pool
- `update_karma_pool(char_id, new_pool, reason)` - Set karma pool
- `set_karma_available(char_id, new_available, reason)` - Set available karma
- `set_karma_total(char_id, new_total, reason)` - Set total karma
- `set_karma(char_id, total, available, reason)` - Set both total and available

### Nuyen Management (2)
- `add_nuyen(char_id, amount, reason)` - Add nuyen
- `spend_nuyen(char_id, amount, reason)` - Spend nuyen

### Spells (4)
- `get_spells(char_id)` - Get all spells
- `add_spell(char_id, data, reason)` - Add spell
- `update_spell(char_id, spell_name, updates, reason)` - Update spell
- `delete_spell(char_id, spell_name, reason)` - Soft delete spell
- `remove_spell(char_id, spell_name, reason)` - Alias for delete_spell

### Spirits (3)
- `get_spirits(char_id)` - Get all spirits
- `add_spirit(char_id, data, reason)` - Add spirit
- `update_spirit_services(char_id, spirit_name, services, reason)` - Update services

### Foci (2)
- `get_foci(char_id)` - Get all foci
- `add_focus(char_id, data, reason)` - Add focus

### Gear (6)
- `get_gear(char_id, gear_type)` - Get gear
- `add_gear(char_id, data, reason)` - Add gear
- `update_gear_quantity(char_id, gear_name, quantity, reason)` - Update quantity
- `update_gear(char_id, gear_name, updates, reason)` - Update gear
- `remove_gear(char_id, gear_name, reason)` - Soft delete gear
- `get_character_gear(char_id, gear_type)` - Alias for get_gear

### Contacts (3)
- `get_contacts(char_id)` - Get all contacts
- `add_contact(char_id, data, reason)` - Add contact
- `update_contact_loyalty(char_id, name, loyalty, reason)` - Update loyalty

### Vehicles (4)
- `get_vehicles(char_id)` - Get all vehicles
- `add_vehicle(char_id, data, reason)` - Add vehicle
- `update_vehicle(char_id, vehicle_name, updates, reason)` - Update vehicle
- `delete_vehicle(char_id, vehicle_name, reason)` - Soft delete vehicle

### Cyberdecks (2)
- `get_cyberdecks(char_id)` - Get all cyberdecks
- `add_cyberdeck(char_id, data, reason)` - Add cyberdeck

### Skills (7)
- `get_skills(char_id)` - Get all skills
- `add_skill(char_id, data, reason)` - Add skill
- `improve_skill(char_id, skill_name, new_rating, reason)` - Improve skill
- `add_specialization(char_id, skill_name, specialization, reason)` - Add specialization
- `update_skill(char_id, skill_name, updates, reason)` - Update skill
- `remove_skill(char_id, skill_name, reason)` - Remove skill
- `get_character_skills(char_id)` - Alias for get_skills

### Edges & Flaws (2)
- `get_edges_flaws(char_id)` - Get all edges/flaws
- `add_edge_flaw(char_id, data, reason)` - Add edge/flaw (auto-populates cost from RAG)

### Powers (3)
- `get_powers(char_id)` - Get all powers
- `add_power(char_id, data, reason)` - Add power
- `update_power_level(char_id, power_name, new_level, reason)` - Update power level

### Relationships (3)
- `get_relationships(char_id)` - Get all relationships
- `add_relationship(char_id, data, reason)` - Add relationship
- `update_relationship_data(char_id, relationship_name, new_data, reason)` - Update relationship

### Active Effects (4)
- `get_active_effects(char_id, active_only)` - Get active effects
- `add_active_effect(char_id, data, reason)` - Add effect
- `deactivate_effect(char_id, effect_name, reason)` - Deactivate effect
- `remove_effect(char_id, effect_name, reason)` - Remove effect

### Modifiers (4)
- `get_modifiers(char_id, modifier_type)` - Get modifiers
- `add_modifier(char_id, data, reason)` - Add modifier
- `remove_modifier(modifier_id, reason)` - Remove modifier
- `remove_temporary_modifiers(char_id, reason)` - Remove all temporary modifiers

### Cyberware & Bioware (6)
- `get_character_cyberware(char_id)` - Get cyberware
- `get_character_bioware(char_id)` - Get bioware
- `add_cyberware(char_id, data, reason)` - Add cyberware
- `add_bioware(char_id, data, reason)` - Add bioware
- `update_cyberware(char_id, modifier_id, updates, reason)` - Update cyberware
- `remove_cyberware(char_id, modifier_id, reason)` - Remove cyberware
- `remove_bioware(char_id, modifier_id, reason)` - Remove bioware

### House Rules (3)
- `get_house_rules(campaign_id, active_only)` - Get house rules
- `add_house_rule(data, reason)` - Add house rule
- `toggle_house_rule(rule_id, is_active, reason)` - Toggle house rule

### Campaign NPCs (3)
- `get_campaign_npcs(campaign_id, relevance)` - Get NPCs
- `add_campaign_npc(campaign_id, data, reason)` - Add NPC
- `update_npc_relevance(npc_id, relevance, reason)` - Update NPC relevance

### Audit (1)
- `get_audit_log(table_name, record_id, limit)` - Get audit log

### Utility (1)
- `close()` - Close database connection

---

## MCP_OPERATIONS.PY - Currently Exposed

### Currently Implemented (7 + dice/campaign tools)
- `list_characters()` - List all characters
- `add_karma(character_name, amount, reason)` - Add karma
- `spend_karma(character_name, amount, reason)` - Spend karma
- `update_karma_pool(character_name, new_pool, reason)` - Update karma pool
- `set_karma(character_name, total, available, reason)` - Set karma
- `add_nuyen(character_name, amount, reason)` - Add nuyen
- `spend_nuyen(character_name, amount, reason)` - Spend nuyen

**NOTE**: The file was truncated when initially read. Need to verify full contents.

### MISSING FROM MCP_OPERATIONS (Should be added)

#### Character Data Retrieval
- `get_character(character_name)` - Get full character sheet
- `get_character_skill(character_name, skill_name)` - Get specific skill

#### Spells
- `get_spells(character_name)` - Get all spells
- `add_spell(character_name, spell_data, reason)` - Add spell
- `update_spell(character_name, spell_name, updates, reason)` - Update spell
- `remove_spell(character_name, spell_name, reason)` - Remove spell

#### Skills
- `get_skills(character_name)` - Get all skills
- `add_skill(character_name, skill_data, reason)` - Add skill
- `improve_skill(character_name, skill_name, new_rating, reason)` - Improve skill
- `add_specialization(character_name, skill_name, specialization, reason)` - Add specialization

#### Gear
- `get_gear(character_name, gear_type)` - Get gear
- `add_gear(character_name, gear_data, reason)` - Add gear
- `update_gear_quantity(character_name, gear_name, quantity, reason)` - Update quantity
- `remove_gear(character_name, gear_name, reason)` - Remove gear

#### Cyberware & Bioware
- `get_cyberware(character_name)` - Get cyberware
- `get_bioware(character_name)` - Get bioware
- `add_cyberware(character_name, data, reason)` - Add cyberware
- `add_bioware(character_name, data, reason)` - Add bioware
- `remove_cyberware(character_name, modifier_id, reason)` - Remove cyberware
- `remove_bioware(character_name, modifier_id, reason)` - Remove bioware

#### Vehicles
- `get_vehicles(character_name)` - Get vehicles
- `add_vehicle(character_name, vehicle_data, reason)` - Add vehicle
- `update_vehicle(character_name, vehicle_name, updates, reason)` - Update vehicle
- `remove_vehicle(character_name, vehicle_name, reason)` - Remove vehicle

#### Contacts
- `get_contacts(character_name)` - Get contacts
- `add_contact(character_name, contact_data, reason)` - Add contact
- `update_contact_loyalty(character_name, name, loyalty, reason)` - Update loyalty

#### Spirits & Foci
- `get_spirits(character_name)` - Get spirits
- `add_spirit(character_name, spirit_data, reason)` - Add spirit
- `update_spirit_services(character_name, spirit_name, services, reason)` - Update services
- `get_foci(character_name)` - Get foci
- `add_focus(character_name, focus_data, reason)` - Add focus

#### Powers
- `get_powers(character_name)` - Get powers
- `add_power(character_name, power_data, reason)` - Add power
- `update_power_level(character_name, power_name, new_level, reason)` - Update level

#### Edges & Flaws
- `get_edges_flaws(character_name)` - Get edges/flaws
- `add_edge_flaw(character_name, data, reason)` - Add edge/flaw

#### Active Effects
- `get_active_effects(character_name, active_only)` - Get active effects
- `add_active_effect(character_name, effect_data, reason)` - Add effect
- `deactivate_effect(character_name, effect_name, reason)` - Deactivate effect
- `remove_effect(character_name, effect_name, reason)` - Remove effect

#### Modifiers
- `get_modifiers(character_name, modifier_type)` - Get modifiers
- `add_modifier(character_name, modifier_data, reason)` - Add modifier
- `remove_modifier(character_name, modifier_id, reason)` - Remove modifier
- `remove_temporary_modifiers(character_name, reason)` - Remove temporary modifiers

---

## GAME-SERVER.PY - MCP Tools Exposed to AI

### Currently Exposed (13 tools)
1. `get_character_skill` - Get skill rating
2. `calculate_dice_pool` - Calculate dice pool
3. `calculate_target_number` - Calculate TN
4. `roll_dice` - Roll dice
5. `get_character` - Get full character
6. `calculate_ranged_attack` - Calculate ranged attack
7. `cast_spell` - Cast spell
8. `add_karma` - Add karma
9. `spend_karma` - Spend karma
10. `update_karma_pool` - Update karma pool
11. `set_karma` - Set karma
12. `add_nuyen` - Add nuyen
13. `spend_nuyen` - Spend nuyen

### MISSING FROM GAME-SERVER (Should be added)
All the operations listed in "MISSING FROM MCP_OPERATIONS" section above need to be:
1. Added to mcp_operations.py
2. Added to game-server.py tool handlers
3. Added to game-server.py tool definitions
4. Documented in MCP-TOOLS-REFERENCE.md

---

## DOCUMENTATION STATUS

### MCP-TOOLS-REFERENCE.md - Currently Documented (33 tools)
1. get_character ✓
2. get_character_skill ✓
3. calculate_dice_pool ✓
4. calculate_target_number ✓
5. roll_dice ✓
6. calculate_ranged_attack ✓
7. cast_spell ✓
8. add_karma ✓
9. spend_karma ✓
10. update_karma_pool ✓
11. set_karma ✓
12. add_nuyen ✓
13. spend_nuyen ✓
14-33. Dice rolling tools (20 tools for comprehensive dice mechanics)
34+. Campaign management tools

**CORRECTION**: Initial audit was incorrect. The documentation is much more complete than initially stated.

### MISSING FROM DOCUMENTATION
- All CRUD operations for spells, skills, gear, cyberware, bioware, vehicles, contacts, spirits, foci, powers, edges/flaws, active effects, modifiers
- Approximately 40+ operations need documentation

---

## ORCHESTRATOR-REFERENCE.md
**STATUS**: Does not exist yet
**NEEDS**: Complete documentation of how the orchestrator layer works

---

## UI-REFERENCE.md
**STATUS**: Exists but may need updates for new operations
**NEEDS**: Review and update for karma/nuyen management UI

---

## PRIORITY ACTIONS

1. **Expand mcp_operations.py** - Add wrappers for all CRUD operations
2. **Update game-server.py** - Add tool handlers and definitions
3. **Update MCP-TOOLS-REFERENCE.md** - Document all new tools
4. **Create ORCHESTRATOR-REFERENCE.md** - Document orchestrator layer
5. **Update UI-REFERENCE.md** - Document UI for new operations

---

## ESTIMATED SCOPE

- **CRUD Operations**: 60+ operations
- **MCP Operations to Add**: ~50 operations
- **Game Server Tools to Add**: ~50 tools
- **Documentation Pages to Update**: 3-4 documents
- **Estimated Time**: 4-6 hours of focused work
