# CRUD API Completion Plan

## Current State (Accurate Audit Results)

### Layer 1: CRUD Operations (lib/comprehensive_crud.py)
- **Status**: ✅ COMPLETE
- **Operations**: 80 public methods
- **Coverage**: All character data, karma, nuyen, spells, skills, gear, cyberware, bioware, vehicles, contacts, spirits, foci, powers, edges/flaws, active effects, modifiers, house rules, campaign NPCs, audit logs

### Layer 2: MCP Operations (lib/mcp_operations.py)
- **Status**: ⚠️ INCOMPLETE
- **Operations**: 7 async methods
- **Current**: list_characters, add_karma, spend_karma, update_karma_pool, set_karma, add_nuyen, spend_nuyen
- **Missing**: 73 operations

### Layer 3: Game Server Tools (game-server.py)
- **Status**: ⚠️ PARTIAL
- **Tools**: 13 MCP tools
- **Current**: Core game mechanics (dice, combat, spellcasting) + karma/nuyen
- **Missing**: CRUD operations for character data management

### Layer 4: Documentation (docs/MCP-TOOLS-REFERENCE.md)
- **Status**: ⚠️ NEEDS UPDATE
- **Documented**: 33 tools
- **Includes**: Dice rolling (20 tools), core mechanics, karma/nuyen
- **Missing**: New CRUD operations documentation

---

## Gap Analysis

```
CRUD Layer:     80 operations ✅
                    ↓ (73 missing)
MCP Layer:       7 operations ⚠️
                    ↓ (need to expose)
Game Server:    13 tools ⚠️
                    ↓ (need to document)
Documentation:  33 tools ⚠️
```

---

## Implementation Plan

### Phase 1: Core Character Data Operations (Priority 1)
**Estimated Time**: 2-3 hours

#### 1.1 Character Retrieval
- `get_character(character_name)` - Get full character sheet
- `get_character_skill(character_name, skill_name)` - Get specific skill

#### 1.2 Skills Management
- `get_skills(character_name)` - Get all skills
- `add_skill(character_name, skill_data, reason)` - Add skill
- `improve_skill(character_name, skill_name, new_rating, reason)` - Improve skill
- `add_specialization(character_name, skill_name, specialization, reason)` - Add specialization
- `remove_skill(character_name, skill_name, reason)` - Remove skill

#### 1.3 Spells Management
- `get_spells(character_name)` - Get all spells
- `add_spell(character_name, spell_data, reason)` - Add spell
- `update_spell(character_name, spell_name, updates, reason)` - Update spell
- `remove_spell(character_name, spell_name, reason)` - Remove spell

#### 1.4 Gear Management
- `get_gear(character_name, gear_type)` - Get gear
- `add_gear(character_name, gear_data, reason)` - Add gear
- `update_gear_quantity(character_name, gear_name, quantity, reason)` - Update quantity
- `remove_gear(character_name, gear_name, reason)` - Remove gear

**Deliverables**:
- Add 15 operations to mcp_operations.py
- Add 15 tool handlers to game-server.py
- Add 15 tool definitions to game-server.py
- Document 15 tools in MCP-TOOLS-REFERENCE.md

---

### Phase 2: Augmentations & Equipment (Priority 2)
**Estimated Time**: 1-2 hours

#### 2.1 Cyberware & Bioware
- `get_cyberware(character_name)` - Get cyberware
- `get_bioware(character_name)` - Get bioware
- `add_cyberware(character_name, data, reason)` - Add cyberware
- `add_bioware(character_name, data, reason)` - Add bioware
- `update_cyberware(character_name, modifier_id, updates, reason)` - Update cyberware
- `remove_cyberware(character_name, modifier_id, reason)` - Remove cyberware
- `remove_bioware(character_name, modifier_id, reason)` - Remove bioware

#### 2.2 Vehicles
- `get_vehicles(character_name)` - Get vehicles
- `add_vehicle(character_name, vehicle_data, reason)` - Add vehicle
- `update_vehicle(character_name, vehicle_name, updates, reason)` - Update vehicle
- `remove_vehicle(character_name, vehicle_name, reason)` - Remove vehicle

#### 2.3 Cyberdecks
- `get_cyberdecks(character_name)` - Get cyberdecks
- `add_cyberdeck(character_name, deck_data, reason)` - Add cyberdeck

**Deliverables**:
- Add 13 operations to mcp_operations.py
- Add 13 tool handlers to game-server.py
- Add 13 tool definitions to game-server.py
- Document 13 tools in MCP-TOOLS-REFERENCE.md

---

### Phase 3: Social & Magical (Priority 3)
**Estimated Time**: 1-2 hours

#### 3.1 Contacts
- `get_contacts(character_name)` - Get contacts
- `add_contact(character_name, contact_data, reason)` - Add contact
- `update_contact_loyalty(character_name, name, loyalty, reason)` - Update loyalty

#### 3.2 Spirits & Foci
- `get_spirits(character_name)` - Get spirits
- `add_spirit(character_name, spirit_data, reason)` - Add spirit
- `update_spirit_services(character_name, spirit_name, services, reason)` - Update services
- `get_foci(character_name)` - Get foci
- `add_focus(character_name, focus_data, reason)` - Add focus

#### 3.3 Powers
- `get_powers(character_name)` - Get powers
- `add_power(character_name, power_data, reason)` - Add power
- `update_power_level(character_name, power_name, new_level, reason)` - Update level

#### 3.4 Edges & Flaws
- `get_edges_flaws(character_name)` - Get edges/flaws
- `add_edge_flaw(character_name, data, reason)` - Add edge/flaw (auto-populates cost from RAG)

#### 3.5 Relationships
- `get_relationships(character_name)` - Get relationships
- `add_relationship(character_name, data, reason)` - Add relationship
- `update_relationship_data(character_name, relationship_name, new_data, reason)` - Update relationship

**Deliverables**:
- Add 15 operations to mcp_operations.py
- Add 15 tool handlers to game-server.py
- Add 15 tool definitions to game-server.py
- Document 15 tools in MCP-TOOLS-REFERENCE.md

---

### Phase 4: Game State Management (Priority 4)
**Estimated Time**: 1 hour

#### 4.1 Active Effects
- `get_active_effects(character_name, active_only)` - Get active effects
- `add_active_effect(character_name, effect_data, reason)` - Add effect
- `deactivate_effect(character_name, effect_name, reason)` - Deactivate effect
- `remove_effect(character_name, effect_name, reason)` - Remove effect

#### 4.2 Modifiers
- `get_modifiers(character_name, modifier_type)` - Get modifiers
- `add_modifier(character_name, modifier_data, reason)` - Add modifier
- `remove_modifier(character_name, modifier_id, reason)` - Remove modifier
- `remove_temporary_modifiers(character_name, reason)` - Remove temporary modifiers

**Deliverables**:
- Add 8 operations to mcp_operations.py
- Add 8 tool handlers to game-server.py
- Add 8 tool definitions to game-server.py
- Document 8 tools in MCP-TOOLS-REFERENCE.md

---

### Phase 5: Campaign Management (Priority 5)
**Estimated Time**: 1 hour

#### 5.1 House Rules
- `get_house_rules(campaign_id, active_only)` - Get house rules
- `add_house_rule(data, reason)` - Add house rule
- `toggle_house_rule(rule_id, is_active, reason)` - Toggle house rule

#### 5.2 Campaign NPCs
- `get_campaign_npcs(campaign_id, relevance)` - Get NPCs
- `add_campaign_npc(campaign_id, data, reason)` - Add NPC
- `update_npc_relevance(npc_id, relevance, reason)` - Update NPC relevance

#### 5.3 Audit
- `get_audit_log(table_name, record_id, limit)` - Get audit log

**Deliverables**:
- Add 7 operations to mcp_operations.py
- Add 7 tool handlers to game-server.py
- Add 7 tool definitions to game-server.py
- Document 7 tools in MCP-TOOLS-REFERENCE.md

---

### Phase 6: Character Management (Priority 6)
**Estimated Time**: 1 hour

#### 6.1 Character CRUD
- `create_character(data, reason)` - Create new character
- `update_character(character_name, updates, reason)` - Update character
- `delete_character(character_name, reason)` - Delete character

#### 6.2 Character Updates
- `update_skill(character_name, skill_name, updates, reason)` - Update skill details
- `update_gear(character_name, gear_name, updates, reason)` - Update gear details

**Deliverables**:
- Add 5 operations to mcp_operations.py
- Add 5 tool handlers to game-server.py
- Add 5 tool definitions to game-server.py
- Document 5 tools in MCP-TOOLS-REFERENCE.md

---

## Testing Strategy

### Per-Phase Testing
After each phase:
1. Create test file: `tests/test-mcp-phase-N.py`
2. Test all new operations with real character data
3. Verify error handling
4. Verify audit logging
5. Test through MCP server

### Integration Testing
After all phases:
1. Run comprehensive test suite
2. Test operation chaining (e.g., add karma → spend karma → improve skill)
3. Test with multiple characters
4. Verify UI integration

---

## Documentation Updates

### Per-Phase Documentation
After each phase:
1. Update MCP-TOOLS-REFERENCE.md with new tools
2. Add examples for each tool
3. Document parameters and return values
4. Add common use cases

### Final Documentation
After all phases:
1. Create ORCHESTRATOR-REFERENCE.md
2. Update UI-REFERENCE.md
3. Update README.md with new capabilities
4. Create CRUD-API-COMPLETE.md summary

---

## Total Effort Estimate

- **Phase 1**: 2-3 hours (15 operations)
- **Phase 2**: 1-2 hours (13 operations)
- **Phase 3**: 1-2 hours (15 operations)
- **Phase 4**: 1 hour (8 operations)
- **Phase 5**: 1 hour (7 operations)
- **Phase 6**: 1 hour (5 operations)
- **Testing**: 2 hours
- **Documentation**: 2 hours

**Total**: 11-15 hours of focused work

---

## Success Criteria

✅ All 80 CRUD operations exposed through MCP layer
✅ All operations tested and working
✅ All operations documented
✅ UI can use all operations
✅ Audit logging works for all operations
✅ Error handling is consistent
✅ Character lookup (by name/street name) works for all operations

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (Core Character Data Operations)
3. Complete each phase sequentially
4. Test thoroughly after each phase
5. Update documentation continuously
6. Final integration testing
7. Update ROADMAP.md with completion status
