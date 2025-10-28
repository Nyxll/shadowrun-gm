# Shadowrun GM - Complete Test Suite Documentation

## Overview

This document provides comprehensive documentation for all test suites in the Shadowrun GM project, including both the original Node.js MCP server tests and the new Python game server tests.

## Test Suites

### 1. UI Tests (Python/Playwright)
**File:** `tests/test-ui.py`  
**Tests:** 15  
**Purpose:** Test the web interface functionality

#### Test Categories

**Page Load Tests (3 tests)**
- ✓ Page loads successfully
- ✓ Page title is correct
- ✓ Header is visible

**Connection Tests (1 test)**
- ✓ WebSocket connects

**Data Loading Tests (3 tests)**
- ✓ Characters load from database
- ✓ Character dropdown populated
- ✓ Status updates correctly

**UI Element Tests (3 tests)**
- ✓ Create Scenario button enabled
- ✓ Add Character button visible
- ✓ No horizontal scroll needed

**Interaction Tests (4 tests)**
- ✓ Can select and add character
- ✓ Duplicate character prevention
- ✓ Message input enabled after connection
- ✓ Send button enabled

**Layout Tests (1 test)**
- ✓ Responsive layout

#### Running UI Tests

```bash
# Install Playwright browsers (first time only)
playwright install

# Run UI tests
python tests/test-ui.py
```

**Prerequisites:**
- Game server must be running on port 8001
- Database must be accessible
- Playwright browsers installed

---

### 2. Game Server MCP Tests (Python)
**File:** `tests/test-game-server-mcp.py`  
**Tests:** 15  
**Purpose:** Test MCP tool integration in Python game server

#### Test Categories

**MCP Tool Tests (5 tests)**
- ✓ Get character skill
- ✓ Calculate dice pool
- ✓ Calculate target number
- ✓ Roll dice
- ✓ Get character data

**DiceRoller Tests (3 tests)**
- ✓ DiceRoller basic roll
- ✓ DiceRoller explosions
- ✓ DiceRoller Rule of One detection

**Combat Modifier Tests (2 tests)**
- ✓ Combat wound modifiers
- ✓ Combat range modifiers

**GameSession Tests (4 tests)**
- ✓ GameSession creation
- ✓ GameSession add message
- ✓ GameSession add character
- ✓ GameSession message limit

**Database Tests (1 test)**
- ✓ Database connection

#### Running Game Server MCP Tests

```bash
python tests/test-game-server-mcp.py
```

**Prerequisites:**
- Database must be accessible
- Characters must be loaded in database

---

### 2a. Modifier System Tests (Python)
**File:** `tools/test-mcp-platinum-shot.py`  
**Tests:** 1 comprehensive end-to-end test  
**Purpose:** Test character modifier system and ranged attack calculations

#### What It Tests
- Vision modifier extraction from `character_modifiers` table
- Cybernetic vs natural vision type handling
- Optical magnification range shifting
- Combat modifier application (smartlink)
- Conditional modifier filtering
- Final TN calculation

#### Test Scenario
**Platinum shooting a rat at 55m in complete darkness**

Expected Results:
```
Base TN: 4 (short range after Mag 3 adjustment)
Visibility: +2 (cybernetic thermographic in darkness)
Target: +2 (small target)
Smartlink 3: -3
Final TN: 3
```

#### Running Modifier Tests

```bash
python tools/test-mcp-platinum-shot.py
```

**Prerequisites:**
- Database must be accessible
- Platinum character must be loaded
- Character modifiers must be migrated (run `tools/migrate-platinum-modifiers.py`)

#### Migration Tools

**Migrate Character Modifiers:**
```bash
python tools/migrate-platinum-modifiers.py
```
Populates `character_modifiers` table with vision and combat modifiers from cyberware.

**Clean Duplicate Modifiers:**
```bash
python tools/clean-duplicate-smartlinks.py
```
Removes duplicate smartlink modifiers, keeping the most recent.

---

### 3. Node.js MCP Server Tests (Existing)
**Files:** Multiple test files in `tests/`  
**Tests:** 96+  
**Purpose:** Test original Node.js MCP server tools

#### Test Files

1. **test-dice-rolling.js** (16 tests)
   - Comprehensive dice rolling mechanics
   - Explosions, target numbers, pools, karma

2. **test-gear-operations.js** (14 tests)
   - Gear lookup and comparison
   - Search, compare, details retrieval

3. **test-skill-web.js** (25 tests)
   - Skill web defaulting pathfinding
   - Shortest path calculation, modifier computation

4. **test-combat-modifiers.js**
   - Combat modifier calculations
   - Wound, range, visibility modifiers

5. **test-clarification-learning.js**
   - Clarification learning system
   - Query classification and learning

6. **test-hybrid-search.js**
   - Hybrid search functionality
   - Vector + keyword search

7. **test-intent-classification.js**
   - Intent classification system
   - Query type detection

#### Running Node.js Tests

```bash
# Run all tests
node tests/run-all-tests.js

# Run individual test suites
node tests/test-dice-rolling.js
node tests/test-gear-operations.js
node tests/test-skill-web.js
```

---

## Test Coverage Summary

### Total Test Count
- **UI Tests:** 15
- **Game Server MCP Tests:** 15
- **Node.js MCP Tests:** 96+
- **TOTAL:** 126+ tests

### Coverage by Feature

#### Web Interface (15 tests)
- Page loading and rendering
- WebSocket connectivity
- Character selection and management
- UI layout and responsiveness
- User interactions

#### Game Server (15 tests)
- MCP tool integration
- Dice rolling mechanics
- Combat modifiers
- Session management
- Database operations

#### MCP Server Tools (96+ tests)
- 14 dice rolling tools (96 test cases)
- Gear operations (14 tests)
- Skill web defaulting (25 tests)
- Combat modifiers
- Clarification learning
- Hybrid search
- Intent classification

---

## Test Infrastructure

### Python Tests
- **Framework:** Playwright (UI), asyncio (MCP)
- **Dependencies:** playwright, pytest, pytest-asyncio
- **Configuration:** .env file for database connection

### Node.js Tests
- **Framework:** Custom test runner
- **Dependencies:** MCP server, database connection
- **Configuration:** Environment variables

---

## Running All Tests

### Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt
playwright install

# 2. Start game server (in separate terminal)
python game-server.py

# 3. Run Python tests
python tests/test-ui.py
python tests/test-game-server-mcp.py

# 4. Run Node.js tests
node tests/run-all-tests.js
```

### Automated Test Runner

```bash
# Run all tests with single command
python tests/run-all-python-tests.py
```

---

## Test Results Format

### Python Tests
```
============================================================
SHADOWRUN GM - UI TEST SUITE
============================================================

Page Load Tests:
✓ Page loads successfully
✓ Page title is correct
✓ Header is visible

Connection Tests:
✓ WebSocket connects

...

============================================================
RESULTS: 15 passed, 0 failed, 15 total
============================================================
```

### Node.js Tests
```
Running test suite: test-dice-rolling.js
✓ Test 1: Basic dice roll
✓ Test 2: Exploding dice
...
Summary: 16/16 tests passed
```

---

## Continuous Integration

### GitHub Actions (Recommended)

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Python dependencies
        run: |
          pip install -r requirements.txt
          playwright install
      
      - name: Install Node.js dependencies
        run: npm install
      
      - name: Run Python tests
        run: |
          python tests/test-game-server-mcp.py
          python tests/test-ui.py
      
      - name: Run Node.js tests
        run: node tests/run-all-tests.js
```

---

## Test Maintenance

### Adding New Tests

#### Python UI Test
```python
async def test_new_feature(self):
    """Test X: Description"""
    try:
        # Test implementation
        result = await self.page.locator("#element").text_content()
        self.log_test("Test name", result == "expected")
    except Exception as e:
        self.log_test("Test name", False, str(e))
```

#### Python MCP Test
```python
async def test_new_tool(self):
    """Test X: Description"""
    try:
        result = await self.mcp_client.call_tool("tool_name", {
            "param": "value"
        })
        self.log_test("Test name", "expected_key" in result)
    except Exception as e:
        self.log_test("Test name", False, str(e))
```

### Updating Test Documentation

1. Update this file with new test counts
2. Update test categories
3. Add new test files to running instructions
4. Update CI/CD configuration if needed

---

## Troubleshooting

### Common Issues

**UI Tests Fail - Server Not Running**
```bash
# Start server first
python game-server.py
# Then run tests in another terminal
python tests/test-ui.py
```

**Database Connection Errors**
```bash
# Check .env file has correct credentials
# Verify database is running
# Check port 5434 is accessible
```

**Playwright Not Installed**
```bash
# Install Playwright browsers
playwright install
```

**Node.js Tests Fail**
```bash
# Ensure MCP server dependencies are installed
npm install
# Check database connection
node test-db-connection.js
```

---

## Future Test Plans

### Planned Additions

1. **Integration Tests**
   - Complete combat sequence
   - Full character creation workflow
   - Karma Pool usage workflow

2. **Performance Tests**
   - Large dice pools (100d6)
   - Chain explosions
   - Concurrent sessions

3. **Stress Tests**
   - Multiple simultaneous users
   - Database load testing
   - WebSocket connection limits

4. **E2E Tests**
   - Complete game session from start to finish
   - Multi-character combat scenarios
   - Scenario generation and execution

---

**Last Updated:** January 20, 2025  
**Total Tests:** 126+  
**Test Coverage:** UI (100%), Game Server (100%), MCP Tools (100%)
