# Shadowrun GM - Current Status
**Last Updated**: 2025-10-28 02:13 AM

## ✅ COMPLETED WORK

### 1. Comprehensive CRUD API
- **File**: `lib/comprehensive_crud.py`
- **Status**: Complete and tested
- **Features**:
  - Full CRUD for all character data types
  - UUID-based operations
  - Proper schema alignment
  - Character lookup by name → UUID conversion
  - Support for: characters, skills, gear, spells, foci, spirits, contacts, vehicles, cyberdecks, modifiers

### 2. UI Fixes
- **Fixed telemetry error** in `www/app.js` (`.replace()` on undefined)
- **Fixed attribute display** in `www/character-sheet-renderer.js` (0 values now show correctly)
- **Base/Current ratings** properly displayed for skills

### 3. Test Infrastructure
- **Comprehensive test runner**: `tests/run-comprehensive-tests.py`
- **Unicode compatibility**: `tools/fix-test-unicode.py` (Windows cp1252 fix)
- **All test files updated** to use ASCII characters

## 🔧 IN PROGRESS

### Schema Mismatch Fixes
The user has emphasized the need to fix ALL schema mismatches in operations. Key issues:

1. **character_skills table**:
   - Operations must use BOTH `base_rating` AND `current_rating`
   - Never use just one or the other
   
2. **UUID consistency**:
   - All operations must look up character by name first
   - Then use the UUID for all subsequent operations
   - Never assume character_id type

3. **MCP Operations** (`lib/mcp_operations.py`):
   - Needs update to use `comprehensive_crud.py`
   - Must ensure all calls use proper schema

## 📋 NEXT STEPS (User's Priority Order)

1. **Fix ALL schema mismatches** in operations
   - Verify every call to character_skills uses base_rating AND current_rating
   - Ensure all operations do character lookup → UUID conversion
   - Test all operations with proper data

2. **Complete CRUD API integration**
   - Update MCP operations to use comprehensive CRUD
   - Remove old CRUD implementations

3. **Update Orchestrator**
   - Integrate new MCP operations
   - Ensure proper error handling

4. **Update UI**
   - Connect to new API endpoints
   - Test all character sheet functionality

5. **Documentation**
   - Update MCP tools reference
   - Update orchestrator reference
   - Create migration guide

## ⚠️ CRITICAL NOTES

### From .clinerules:
- **DO NOT modify spellcasting test** - uses Test Leviathan intentionally
- Leviathan totem: FAVORS Combat (+2), OPPOSES Illusion (-2)
- Oak totem: FAVORS Health (+2), OPPOSES Combat (-2)
- Test needs BOTH scenarios, Oak cannot provide both

### User's Emphasis:
> "calls to character_skills not having both base_rating/current_rating shows me that you have not fixed all calls. We have to fix all schema mismatches."

This is the TOP PRIORITY - every operation must be verified for schema compliance.

## 📊 Test Status

- **CRUD API Tests**: ✅ Passing (when run individually)
- **Comprehensive Test Runner**: 🔄 Running (Unicode fixes applied)
- **UI Tests**: ✅ Passing
- **Schema Validation**: ⏳ Pending full verification

## 🗂️ Key Files

### Core Implementation
- `lib/comprehensive_crud.py` - Complete CRUD API
- `lib/mcp_operations.py` - MCP tool operations (needs update)
- `game-server.py` - FastAPI server

### Tests
- `tests/test-all-crud-operations.py` - Full CRUD test suite
- `tests/run-comprehensive-tests.py` - Automated test runner
- `tests/test-schema-fixes.py` - Schema validation tests

### UI
- `www/app.js` - Main UI application
- `www/character-sheet-renderer.js` - Character sheet rendering

### Documentation
- `docs/CRUD-API-STATUS.md` - API implementation status
- `docs/SCHEMA-MISMATCHES-FOUND.md` - Known schema issues
- `docs/MCP-TOOLS-REFERENCE.md` - MCP tools documentation
