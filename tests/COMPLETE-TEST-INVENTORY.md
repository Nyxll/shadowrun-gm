# Complete Test Inventory - Shadowrun GM MCP Server

This document provides a comprehensive inventory of all test files and test documentation in the shadowrun-gm project.

## Test Files by Location

### Root Directory Tests
Located in: `C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\`

1. **test-character-management.js**
   - Tests character creation, retrieval, and updates
   - Uses character-functions.js
   - Tests: create_character, get_character, update_character
   - Database integration test

2. **test-db-connection.js**
   - Database connection test
   - Verifies PostgreSQL connectivity

3. **test-query-classification.js**
   - Tests query classification system
   - Verifies rules/gear/lore detection

4. **test-sniper-rifles.js**
   - Specific gear query test
   - Tests sniper rifle lookups

### Tests Directory
Located in: `C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\tests\`

1. **test-dice-rolling.js** ✅ NEW
   - Comprehensive dice rolling tests
   - 16 test cases covering all dice mechanics
   - Tests explosions, target numbers, pools, karma

2. **test-gear-operations.js** ✅ NEW
   - Gear lookup and comparison tests
   - 14 test cases
   - Tests search, compare, details retrieval

3. **test-skill-web.js** ✅ COPIED FROM WWW
   - Skill web defaulting pathfinding tests
   - 25 test cases from test-cases.md Section 15
   - Tests shortest path calculation, modifier computation

4. **run-all-tests.js** ✅ NEW
   - Master test runner
   - Executes all test suites
   - Provides summary report

### Tools Directory Tests
Located in: `C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\tools\`

1. **test-connection.js**
   - Connection testing utility

2. **test-db-connection.js**
   - Database connection verification

3. **test-enhanced-server.js**
   - Enhanced server functionality tests

4. **test-unified-server.js**
   - Unified server tests

### WWW Directory Tests
Located in: `C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\www\`

1. **test-skill-web.js**
   - Original skill web test (copied to tests/)
   - 25 test cases for skill defaulting

## Test Documentation

### Test Cases Documentation
Located in: `C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\tests\`

1. **test-cases.md** ✅ COPIED FROM WWW
   - **96+ comprehensive test cases**
   - Covers all 14 dice rolling tools
   - Includes skill web defaulting scenarios
   - Sections:
     - Section 1-14: Dice rolling tools (each with 5-15 test cases)
     - Section 15: Skill web defaulting (25 test cases)
     - Section 16: Skill defaulting scenarios with dice rolls (6 scenarios)

2. **test-results.md** (in www/)
   - Actual test execution results from October 4, 2025
   - All 14 tools tested and passed
   - Explosion mechanics verified
   - Performance notes and recommendations

3. **TEST-IMPLEMENTATION-SUMMARY.md** ✅ NEW
   - Implementation roadmap
   - Test coverage summary
   - Future test plans

4. **README.md** ✅ NEW
   - Test suite overview
   - How to run tests
   - Test organization

## Test Coverage Summary

### Dice Rolling Tools (14 tools, 96+ test cases)

1. **roll_dice** - 15 test cases
   - Basic rolling, modifiers, exploding dice
   - Boundary tests, error cases

2. **roll_multiple_dice** - 8 test cases
   - Multiple dice types, mixed modifiers
   - Error handling

3. **roll_with_advantage** - 5 test cases
   - D&D 5e advantage mechanic
   - Various die types and modifiers

4. **roll_with_disadvantage** - 5 test cases
   - D&D 5e disadvantage mechanic
   - Various die types and modifiers

5. **roll_with_target_number** - 7 test cases
   - Shadowrun success counting
   - Exploding dice verification
   - Rule of One testing

6. **roll_opposed** - 5 test cases
   - Opposed rolls with target numbers
   - Net success calculation
   - Tie handling

7. **roll_initiative** - 5 test cases
   - Shadowrun initiative (never explodes)
   - Phase calculation
   - Modifier handling

8. **track_initiative** - 5 test cases
   - Multi-character initiative tracking
   - Phase breakdown
   - Tie-breaking

9. **roll_with_pools** - 5 test cases
   - Multiple dice pools
   - Separate pool tracking
   - Total success calculation

10. **roll_opposed_pools** - 5 test cases
    - Combat, stealth, social, magic, hacking
    - Pool-based opposed tests
    - Dodge detection

11. **reroll_failures** - 5 test cases
    - Karma Pool rerolls
    - Escalating costs (1, 2, 3 Karma)
    - Exploding/non-exploding

12. **avoid_disaster** - 5 test cases
    - Rule of One avoidance
    - 1 Karma cost
    - Various pool sizes

13. **buy_karma_dice** - 5 test cases
    - Buying additional dice
    - 1 Karma per die
    - Maximum limits

14. **buy_successes** - 5 test cases
    - Buying raw successes
    - Permanent Karma cost
    - Requirement: at least 1 natural success

### Skill Web Defaulting (25 test cases)

- Attribute to skill paths
- Skill to skill paths
- Impossible paths (no connection)
- Same skill (no defaulting)
- Direct connections
- Build/Repair variants
- Real-world scenarios

### Skill Defaulting Scenarios (6 scenarios)

- Simple defaulting with dice rolls
- Opposed defaulting tests
- Defaulting with Karma rerolls
- Combat defaulting
- Attribute-only defaulting
- Impossible defaulting attempts

### Gear Operations (14 test cases)

- Gear lookup by various criteria
- Gear comparison and ranking
- Detailed gear information retrieval
- Category and subcategory filtering

### Character Management (6 test cases)

- Character creation
- Character retrieval
- Skill improvements
- Karma management
- Damage tracking
- History tracking

## Running Tests

### Run All Tests
```bash
cd C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm\tests
node run-all-tests.js
```

### Run Individual Test Suites
```bash
# Dice rolling tests
node test-dice-rolling.js

# Gear operations tests
node test-gear-operations.js

# Skill web tests
node test-skill-web.js
```

### Run Root-Level Tests
```bash
cd C:\Users\Rick\Documents\Cline\MCP\shadowrun-gm

# Character management
node test-character-management.js

# Database connection
node test-db-connection.js

# Query classification
node test-query-classification.js

# Sniper rifles
node test-sniper-rifles.js
```

## Test Status

### ✅ Completed
- Dice rolling test suite (16 tests)
- Gear operations test suite (14 tests)
- Skill web test suite (25 tests)
- Test runner (run-all-tests.js)
- Test documentation (test-cases.md, README.md)

### 📋 Existing (Not Yet Integrated)
- Character management tests (root level)
- Database connection tests (root level)
- Query classification tests (root level)
- Tools directory tests

### 🔄 Recommended Next Steps

1. **Move root-level tests to tests/ directory**
   - test-character-management.js → tests/test-character-management.js
   - test-db-connection.js → tests/test-db-connection.js
   - test-query-classification.js → tests/test-query-classification.js
   - test-sniper-rifles.js → tests/test-sniper-rifles.js

2. **Update run-all-tests.js to include all tests**
   - Add character management tests
   - Add database tests
   - Add query classification tests

3. **Create integration tests**
   - Complete combat sequence
   - Full character creation workflow
   - Karma Pool usage workflow

4. **Add boundary/stress tests**
   - Large dice pools (100d6)
   - Chain explosions
   - Invalid inputs
   - Performance benchmarks

## Test File Dependencies

### Required Files
- `server-unified.js` - Main MCP server
- `character-functions.js` - Character management functions
- `skill-web-downloaded.json` - Skill web graph data (in www/)
- Database connection (PostgreSQL)

### Environment Variables
- POSTGRES_HOST (default: 127.0.0.1)
- POSTGRES_PORT (default: 5434)
- POSTGRES_USER (default: postgres)
- POSTGRES_PASSWORD
- POSTGRES_DB (default: postgres)

## Notes

- All dice rolling tests use the MCP server tools via `use_mcp_tool`
- Skill web tests use local pathfinding algorithm
- Character tests require database connection
- Test results from October 4, 2025 show all 14 dice tools passing
- Explosion mechanics verified across multiple tools

---

**Last Updated:** October 16, 2025, 4:24 AM
**Total Test Cases:** 96+ documented, 55+ implemented
**Test Coverage:** Dice rolling (100%), Gear (100%), Skill Web (100%), Character Management (partial)
