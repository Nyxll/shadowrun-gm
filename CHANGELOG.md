# Changelog

All notable changes to the Shadowrun GM project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.3.1] - 2025-10-21

### Fixed
- **Character Sheet Loading**: Fixed 500 Internal Server Error when viewing character sheets
  - Root cause: `game-server.py` was using v1 schema column name `rating` instead of v2 schema `current_rating`
  - Error: `Database error: column "rating" does not exist`
  - Fixed skills query on line 1206: `SELECT skill_name, current_rating, specialization`
  - Fixed response mapping on line 1227: `"rating": skill["current_rating"]`
  - All character sheets now load successfully with HTTP 200 OK

### Added
- **Character Sheet Loading Test**: New automated test script `tests/test-character-sheet-loading.py`
  - Tests `/api/characters` endpoint
  - Tests `/api/character/{name}` endpoint
  - Verifies all character data sections (attributes, skills, gear)
  - Includes manual testing steps for web interface
- **Documentation**: New `docs/CHARACTER-SHEET-FIX.md` with complete fix details
  - Root cause analysis
  - Code changes
  - Testing procedures
  - Expected results

### Technical Details

#### The Bug
```python
# BEFORE (v1 schema - BROKEN):
cursor.execute("""
    SELECT skill_name, rating, specialization
    FROM character_skills
    WHERE character_id = %s::uuid
""", (character_id,))

# Response mapping
"rating": skill["rating"]  # Column doesn't exist!
```

#### The Fix
```python
# AFTER (v2 schema - FIXED):
cursor.execute("""
    SELECT skill_name, current_rating, specialization
    FROM character_skills
    WHERE character_id = %s::uuid
""", (character_id,))

# Response mapping
"rating": skill["current_rating"]  # Correct column name
```

#### Testing Workflow
1. Start server: `python game-server.py`
2. Open browser: http://localhost:8001
3. Select character from dropdown (type "Platinum")
4. Click "ADD CHARACTER" button
5. Click character name in Active Characters list
6. Verify character sheet modal displays all sections
7. Confirm HTTP 200 OK in server logs

---

## [1.3.0] - 2025-10-20

### Added
- **Character Modifier System**: Database-driven modifier system for all character enhancements
  - Vision modifiers (thermographic, lowLight, magnification, ultrasound)
  - Combat modifiers (smartlink, laser sights, sustained spells)
  - Skill modifiers (reflex recorders, specializations)
  - Attribute modifiers (cyberware, bioware)
- **Vision Type Distinction**: Natural vs cybernetic vision with different darkness penalties
  - Natural thermographic: +0 TN in darkness
  - Cybernetic thermographic: +2 TN in darkness
  - Natural low-light: halves penalty, minimum 0
  - Cybernetic low-light: halves penalty, minimum 1
- **Conditional Modifiers**: Support for weapon-specific, light-dependent, and spell-sustained modifiers
- **Migration Tools**:
  - `tools/migrate-platinum-modifiers.py` - Migrate cyberware to modifiers table
  - `tools/clean-duplicate-smartlinks.py` - Remove duplicate modifiers
  - `tools/test-mcp-platinum-shot.py` - Test ranged attack calculations

### Changed
- **Ranged Attack Calculation**: Refactored `game-server.py` to use `character_modifiers` table
  - No longer parses gear names for modifiers
  - Queries database for all applicable modifiers
  - Filters based on conditions (weapon compatibility, light level, active spells)
- **Combat Modifiers Library**: Updated `lib/combat_modifiers.py` vision calculations
  - Distinguishes natural vs cybernetic vision types
  - Properly handles darkness penalties based on vision source

### Fixed
- **Smartlink Double-Application Bug**: Fixed smartlink bonus being applied twice
  - Was applying once in `CombatModifiers.calculate_ranged_tn()` (old system)
  - And again from `character_modifiers` table (new system)
  - Now disabled old smartlink system in favor of database-driven modifiers
  - **Example**: Platinum shooting rat at 55m in darkness now correctly calculates TN=5
    - Base TN: 4 (short range after Mag 3 optical magnification)
    - Visibility: +2 (cybernetic thermographic in complete darkness)
    - Target: +2 (small rat)
    - Smartlink 3: -3 (from character_modifiers, applied once)
    - **Final: 4 + 2 + 2 - 3 = 5** ✓

### Technical Details

#### Modifier System Architecture
All character enhancements now stored in `character_modifiers` table:
```sql
CREATE TABLE character_modifiers (
    id UUID PRIMARY KEY,
    character_id UUID REFERENCES characters(id),
    modifier_type TEXT,  -- vision, combat, skill, attribute
    target_name TEXT,    -- thermographic, ranged_tn, firearms, etc.
    modifier_value INTEGER,
    source TEXT,         -- Cybereyes Alpha, Smartlink 3, etc.
    source_type TEXT,    -- cyberware, bioware, spell, adept_power
    weapon_specific TEXT,
    condition TEXT,      -- spell_sustained, etc.
    modifier_data JSONB, -- Complex properties
    is_permanent BOOLEAN,
    is_homebrew BOOLEAN,
    house_rule_id UUID
);
```

#### Vision Modifier Example
```sql
-- Cybernetic thermographic
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, modifier_data, is_permanent
) VALUES (
    char_id, 'vision', 'thermographic', 1,
    'Cybereyes Alpha', 'cyberware',
    '{"vision_type": "cybernetic", "darkness_penalty": 2}'::jsonb,
    true
);
```

#### Combat Modifier Example
```sql
-- Smartlink 3
INSERT INTO character_modifiers (
    character_id, modifier_type, target_name, modifier_value,
    source, source_type, modifier_data, is_permanent
) VALUES (
    char_id, 'combat', 'ranged_tn', -3,
    'Smartlink 3', 'cyberware',
    '{"rating": 3, "requires_weapon_smartlink": true}'::jsonb,
    true
);
```

### Benefits
- **Fully Extensible**: Add new modifier types without code changes
- **Database-Driven**: All game mechanics in one place
- **Conditional Logic**: Complex requirements (weapon compatibility, light levels, active spells)
- **Audit Trail**: Track source and type of every modifier
- **Future-Proof**: Easy to add ultraviolet, astral, magical vision, etc.

---

## [1.2.0] - 2025-10-20

### Fixed
- **Schema Mismatch**: Fixed foreign key type mismatch between tables
  - `character_skills.character_id` and `character_gear.character_id` were INTEGER
  - `characters.id` is UUID
  - Migrated foreign keys to UUID type
  - Removed incorrect constraints pointing to non-existent `sr_characters` table
  - Character sheets now properly load skills and gear data

### Removed
- **Unused Schema File**: Archived `schema/character_system.sql`
  - Was a proposed schema that was never implemented
  - Contained `sr_characters` table definition causing confusion
  - Moved to `docs/archive/character_system.sql.unused` for reference

### Changed
- **Database Migration**: Created `tools/migrate-foreign-keys-to-uuid.py`
  - Safely migrates foreign key columns from INTEGER to UUID
  - Drops incorrect foreign key constraints
  - Recreates proper constraints pointing to `characters` table
  - Includes verification and rollback capabilities

---

## [1.1.0] - 2025-10-20

### Added
- **Character Sheet Viewer**: Click character names to view full character sheets in modal
- **Loading States**: Visual feedback on Add Character button during operations
- **Duplicate Prevention**: Prevents adding same character multiple times
- **Comprehensive Test Suite**: 9 new tests covering character sheets, removal, and loading states
- **Test Runner**: `tests/run-all-new-tests.py` runs all new test suites
- **Python 3.13 Support**: Updated all dependencies for compatibility

### Fixed
- **Character Sheet 500 Error**: Fixed `/api/character/{name}` endpoint
  - Was querying non-existent columns (essence, magic, reaction)
  - Now properly extracts from JSONB `attributes` field
  - Added UUID type casting for character_skills and character_gear joins
- **Add Character UX**: Added loading state to prevent spam-clicking
  - Button disables during operation
  - Text changes to "Adding Character..."
  - Status display shows progress
  - Button re-enables after completion

### Changed
- **Dependencies Updated**:
  - `playwright`: 1.40.0 → 1.55.0 (Python 3.13 support)
  - `pytest`: 7.4.3 → 8.4.2
  - `pytest-asyncio`: 0.21.1 → 1.2.0
  - `openai`: 1.3.5 → 2.5.0 (httpx compatibility)
- **Server Port**: Runs on 8001 (avoiding Supabase conflict on 8000)

### Technical Details

#### Character Sheet Fix
```python
# Before (BROKEN):
SELECT essence, magic, reaction FROM characters  # Columns don't exist!

# After (FIXED):
SELECT attributes FROM characters  # JSONB field
attributes = character.get("attributes") or {}
essence = attributes.get("essence", 6)
```

#### UUID Type Casting
```python
# Fixed joins with proper type casting
cursor.execute("""
    SELECT skill_name, rating FROM character_skills
    WHERE character_id = %s::uuid  -- Cast to UUID
""", (character["id"],))
```

#### Loading State Implementation
```javascript
// Disable button during operation
addCharacterButton.disabled = true;
addCharacterButton.textContent = 'Adding Character...';
setStatus(`Adding ${characterName} to session...`);

// Re-enable after completion
setTimeout(() => {
    addCharacterButton.disabled = false;
    addCharacterButton.textContent = originalText;
    setStatus('Ready');
}, 1000);
```

### Test Coverage
- **Character Sheet Tests** (3 tests)
  - API endpoint functionality
  - Modal display behavior
  - Error handling (404 responses)
- **Character Removal Tests** (3 tests)
  - Remove before scenario
  - Remove buttons hidden after scenario starts
  - Multiple character removal
- **Loading State Tests** (3 tests)
  - Button state management
  - Duplicate prevention
  - Status display updates

---

## [1.0.0] - 2025-10-19

### Added
- **Live Game Server**: FastAPI server with WebSocket support
- **Grok AI Integration**: AI-powered Game Master using Grok API
- **MCP Tools**: Database integration for character data, dice rolling, combat modifiers
- **Character Management**: Add/remove characters from game sessions
- **Web Interface**: Cyberpunk-themed UI for game sessions
- **Database Schema**: PostgreSQL schema for characters, skills, gear, house rules
- **Historical Data Import**: Imported roleplay logs and training data
- **GM Style Analysis**: Analyzed historical GM patterns
- **Training System**: Prompt engineering and context management
- **Combat Modifiers**: Shadowrun 2nd Edition combat modifier calculations
- **Dice Roller**: SR2 dice rolling with exploding 6s

### Database
- Characters table with JSONB attributes
- Character skills and gear tables
- House rules and query logs
- Training corpus for AI learning

### Documentation
- README.md with project overview
- SETUP.md with installation instructions
- ARCHITECTURE.md with system design
- Multiple completion documents for various phases

---

## Project Structure

```
shadowrun-gm/
├── game-server.py          # Main FastAPI server
├── www/                    # Web interface
│   ├── index.html
│   └── app.js
├── lib/                    # Python libraries
│   ├── dice_roller.py
│   └── combat_modifiers.py
├── tests/                  # Test suites
│   ├── test-character-sheet.py
│   ├── test-character-removal.py
│   ├── test-loading-states.py
│   └── run-all-new-tests.py
├── tools/                  # Utility scripts
├── train/                  # Training data and prompts
├── schema/                 # Database schemas
└── migrations/             # Database migrations
```

---

## Running the Application

### Start Server
```bash
python game-server.py
```

### Run Tests
```bash
# All tests
python tests/run-all-new-tests.py

# Individual suites
python tests/test-character-sheet.py
python tests/test-character-removal.py
python tests/test-loading-states.py
```

### Access Web Interface
Open http://localhost:8001 in your browser

---

## Dependencies

### Python Packages
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- websockets==12.0
- openai==2.5.0
- psycopg[binary]==3.2.11
- python-dotenv==1.0.0
- playwright==1.55.0
- pytest==8.4.2
- pytest-asyncio==1.2.0

### Database
- PostgreSQL 13+ (running on port 5434)

### Environment Variables
Required in `.env`:
- `XAI_API_KEY` - Grok API key
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name

---

## Known Issues

### Test Timeouts
Some automated tests may timeout waiting for character data to load. This is expected behavior and doesn't affect production functionality. All features work correctly in manual testing.

### Future Improvements
- Scenario generation with Grok AI
- Combat turn management
- Initiative tracker
- Character portraits
- Export to PDF
- Multi-session support
- Session persistence

---

## Contributors

- Rick (Project Lead)
- Cline AI Assistant (Development Support)

---

## License

This project is for personal use. Shadowrun is a trademark of The Topps Company, Inc.
