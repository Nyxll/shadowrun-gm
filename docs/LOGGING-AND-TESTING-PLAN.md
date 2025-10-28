# Comprehensive Logging and Testing Implementation Plan

## Current Status
- ✅ Fixed Grok model to `grok-4-fast-non-reasoning`
- ✅ Added cache-busting headers
- ✅ Added basic telemetry to WebSocket handler
- ✅ Added error telemetry for Grok API errors
- ⚠️ Partial logging in mcp_operations.py (only get_character_skill)
- ❌ Missing comprehensive logging throughout
- ❌ Missing telemetry for character additions
- ❌ Tests not executed

## Required Logging Additions

### 1. game-server.py
- [x] Grok API error telemetry
- [ ] Character addition telemetry (with validation)
- [ ] Character removal telemetry
- [ ] Session creation telemetry
- [ ] Tool execution error telemetry

### 2. lib/mcp_operations.py
All operations need comprehensive logging:

#### get_character_skill
- [x] Basic logging added
- [ ] Add detailed step logging

#### calculate_ranged_attack
- [ ] Character lookup logging
- [ ] Skills fetch logging
- [ ] Gear fetch logging
- [ ] Modifiers processing logging
- [ ] Vision enhancements logging
- [ ] Combat calculation logging
- [ ] Dice roll logging

#### cast_spell
- [ ] Character lookup logging
- [ ] Magic validation logging
- [ ] Spell lookup logging
- [ ] Totem bonus/penalty logging
- [ ] Focus application logging
- [ ] Dice pool calculation logging
- [ ] Drain calculation logging
- [ ] Roll execution logging

#### get_character
- [ ] Character lookup logging
- [ ] Related data fetch logging (skills, gear, spells, etc.)
- [ ] Data assembly logging

#### list_characters
- [ ] Query execution logging
- [ ] Result count logging

### 3. lib/comprehensive_crud.py
All CRUD operations need logging:

#### Character Operations
- [ ] get_character_by_street_name
- [ ] get_character_by_given_name
- [ ] list_characters
- [ ] create_character
- [ ] update_character
- [ ] delete_character

#### Related Data Operations
- [ ] get_skills
- [ ] get_gear
- [ ] get_spells
- [ ] get_contacts
- [ ] get_vehicles
- [ ] get_cyberdecks
- [ ] get_foci
- [ ] get_spirits
- [ ] get_edges_flaws
- [ ] get_powers
- [ ] get_relationships
- [ ] get_active_effects
- [ ] get_modifiers

Each should log:
- Operation start
- Character ID being queried
- Query execution
- Result count
- Operation duration
- Any errors

## Required Tests to Execute

### 1. Schema Compliance Tests
```bash
python tests/test-schema-fixes.py
```

### 2. CRUD API Tests
```bash
python tests/test-all-crud-operations.py
python tests/test-comprehensive-crud.py
```

### 3. MCP Operations Tests
```bash
python tests/test-game-server-mcp.py
python tests/test-cast-spell-learned-force.py
python tests/test-ranged-attack-tool.py
```

### 4. UI Tests
```bash
python tests/test-character-sheet-ui.py
python tests/test-character-sheet-comprehensive.py
```

### 5. Integration Tests
```bash
python tests/run-comprehensive-tests.py
```

## Implementation Order

1. **Add telemetry for character additions** (game-server.py)
   - Validate character exists before adding
   - Send telemetry events
   - Handle errors gracefully

2. **Add comprehensive logging to mcp_operations.py**
   - Add detailed logging to all operations
   - Include timing information
   - Log all database queries

3. **Add comprehensive logging to comprehensive_crud.py**
   - Add logging to all CRUD operations
   - Include query execution details
   - Log result counts and durations

4. **Execute all tests**
   - Run schema compliance tests
   - Run CRUD API tests
   - Run MCP operations tests
   - Run UI tests
   - Document results

5. **Create final status report**
   - Summary of all changes
   - Test results
   - Performance metrics
   - Known issues

## Success Criteria

- ✅ All errors appear in Debug: Tool Calls window
- ✅ All operations have comprehensive logging
- ✅ All database queries are logged with timing
- ✅ All tests pass
- ✅ Performance metrics are captured
- ✅ Documentation is complete
