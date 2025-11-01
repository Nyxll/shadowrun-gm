# Shadowrun GM MCP Server - Implementation Roadmap

## Project Overview
Create an MCP server to query a local Supabase/PostgreSQL database containing Shadowrun 2nd Edition rules, gear information, and setting lore.

---

## Phase 1: Rules System ✅ COMPLETED

### 1.1 Project Setup ✅
- [x] Create project directory structure
- [x] Initialize Node.js project with package.json
- [x] Install dependencies (@modelcontextprotocol/sdk, pg, dotenv)
- [x] Configure .env with Supabase credentials
- [x] Create comprehensive README.md
- [x] Create SETUP.md guide

### 1.2 Database Schema ✅
- [x] Design rules_content table schema
- [x] Add vector embedding support (pgvector)
- [x] Create full-text search indexes
- [x] Create category and tag indexes
- [x] Add timestamp triggers
- [x] Execute schema.sql on database
- [x] Verify table creation

### 1.3 MCP Server Implementation ✅
- [x] Create server.js with MCP SDK
- [x] Implement database connection pooling
- [x] Implement query_rules tool (natural language search)
- [x] Implement explain_mechanic tool (comprehensive explanations)
- [x] Implement list_rule_categories tool (browse categories)
- [x] Add error handling
- [x] Test database connectivity

### 1.4 Testing & Validation ✅
- [x] Create sample-data.sql with 13 test rules
- [x] Load sample data into database
- [x] Verify data insertion (7 categories, 13 rules)
- [x] Test server startup
- [x] Validate query functionality

### 1.5 Documentation ✅
- [x] Write comprehensive README.md
- [x] Create SETUP.md with configuration steps
- [x] Document all three MCP tools
- [x] Add troubleshooting section
- [x] Include usage examples

---

## Phase 2: Data Migration ✅ COMPLETED

### 2.1 Assessment & Planning ✅
- [x] Analyze existing RAG database structure
- [x] Identify data sources (OCR files)
- [x] Map existing data to rules_content schema
- [x] Determine embedding strategy (regenerate with OpenAI)
- [x] Plan data transformation pipeline

### 2.2 Migration Script Development ✅
- [x] Create migration script (Python - migrate.py)
- [x] Implement data extraction from OCR files
- [x] Transform data to match schema
  - [x] Extract titles from markdown headers
  - [x] AI-powered categorization (combat, magic, matrix, etc.)
  - [x] Generate subcategories
  - [x] Generate tags
  - [x] Preserve source file references
- [x] Handle embeddings (generate new with OpenAI API)
- [x] Implement batch insertion for performance
- [x] Create MIGRATION-GUIDE.md documentation

### 2.3 Data Quality ✅
- [x] Remove duplicates (grimoire duplicates removed)
- [x] Validate data completeness
- [x] Check for missing categories
- [x] Verify embedding dimensions (1536)
- [x] Test search quality with sample queries
- [x] Add content_type classification system
- [x] Migrate and validate content types

### 2.4 Migration Execution ✅
- [x] Backup existing database
- [x] Run migration script
- [x] Verify record counts
- [x] Test search functionality
- [x] Validate category distribution
- [x] Check for data integrity issues

---

## Phase 3: Cline Integration ✅ COMPLETED

### 3.1 MCP Configuration ✅
- [x] Edit cline_mcp_settings.json
- [x] Add shadowrun-gm server configuration
- [x] Verified server runs successfully
- [x] Confirmed database connection works
- [x] Restart VS Code
- [x] Verify server appears in Cline's MCP list
- [x] Test connection from Cline

### 3.2 Functional Testing ✅
- [x] Test query_rules from Cline
- [x] Test explain_mechanic from Cline
- [x] Test list_rule_categories from Cline
- [x] Verify response formatting
- [x] Test with various query types
- [x] Validate error handling

---

## Phase 4: Enhanced Search Capabilities ✅ COMPLETED

### 4.1 Vector Search Implementation ✅
- [x] Ensure all rules have embeddings
- [x] Implement semantic search function
- [x] Add hybrid search (vector + full-text)
- [x] Tune search relevance
- [x] Add similarity threshold configuration

### 4.2 Advanced Query Features ✅
- [x] Add multi-category search
- [x] Implement tag-based filtering
- [x] Add source book filtering
- [x] Create related rules suggestions
- [x] Add search result ranking
- [x] Implement AI-powered query classification
- [x] Create unified query system

### 4.3 Performance Optimization ✅
- [x] Analyze query performance
- [x] Optimize index usage
- [x] Implement query caching (AI classification cache)
- [x] Add connection pooling tuning
- [x] Monitor database performance
- [x] Add query logging system
- [x] Create query analytics tools

---

## Phase 5: Gear & Equipment Database ✅ COMPLETED

### 5.1 Schema Design ✅
- [x] Design gear table with JSONB stats
  - [x] Weapons (damage, range, ammo)
  - [x] Armor (ballistic, impact ratings)
  - [x] Cyberware (essence cost, effects)
  - [x] Equipment (cost, availability)
- [x] Add gear categories and subcategories
- [x] Create indexes for common queries
- [x] Add full-text search support
- [x] Create gear_chunks linking table

### 5.2 MCP Tools ✅
- [x] Implement lookup_gear tool
- [x] Implement compare_gear tool
- [x] Implement get_gear_details tool
- [x] Add availability/cost filtering
- [x] Add ranking/sorting capabilities

### 5.3 Data Population ✅
- [x] Extract gear data from source files
- [x] Categorize all equipment
- [x] Add stats and descriptions
- [x] Link to relevant rules chunks
- [x] Load DAT files (weapons, armor, cyberware, etc.)
- [x] Validate gear data quality

---

## Phase 6: Magical Systems ✅ COMPLETED

### 6.1 Schema Design ✅
- [x] Design spells table
- [x] Design powers table (adept/critter)
- [x] Design totems table
- [x] Add appropriate indexes

### 6.2 Data Population ✅
- [x] Load spell data
- [x] Load power data
- [x] Load totem data
- [x] Validate magical data

### 6.3 Query Integration ✅
- [x] Integrate spell queries into unified system
- [x] Integrate power queries into unified system
- [x] Integrate totem queries into unified system
- [x] Test magical system queries

---

## Phase 7: Dice Rolling Integration ✅ COMPLETED

### 7.1 Dice API Integration ✅
- [x] Integrate shadowrun2.com dice API
- [x] Implement basic dice rolling (roll_dice)
- [x] Implement multiple dice rolling
- [x] Implement advantage/disadvantage rolls

### 7.2 Shadowrun-Specific Rolling ✅
- [x] Implement target number rolls
- [x] Implement opposed rolls
- [x] Implement initiative rolling
- [x] Implement initiative tracking
- [x] Implement dice pool system
- [x] Implement opposed pool rolls

### 7.3 Karma Pool System ✅
- [x] Implement reroll failures
- [x] Implement avoid disaster (Rule of One)
- [x] Implement buy karma dice
- [x] Implement buy successes
- [x] Document Karma Pool mechanics

---

## Phase 8: Unified Server ✅ COMPLETED

### 8.1 Server Consolidation ✅
- [x] Create server-unified.js
- [x] Merge all query systems
- [x] Merge all dice rolling tools
- [x] Merge all gear tools
- [x] Test unified server

### 8.2 Query Router Enhancement ✅
- [x] Implement AI-powered query classification
- [x] Support multi-source queries (structured + chunks)
- [x] Intelligent result formatting
- [x] Create QUERY-ROUTER-DESIGN.md
- [x] Create QUERY-SYSTEM-GUIDE.md

### 8.3 Analytics & Monitoring ✅
- [x] Create query_logs schema
- [x] Implement query logging
- [x] Create analytics tools
- [x] Monitor query performance

---

## Phase 9: Character Management ✅ COMPLETED

### 9.1 Schema Design ✅
- [x] Design characters table
- [x] Design character_skills table
- [x] Design character_gear table
- [x] Design character_cyberware table
- [x] Add character progression tracking
- [x] Create character_system.sql schema
- [x] Document shapeshifter design
- [x] Migrate to normalized schema
- [x] Fix character_history table

### 9.2 Data Import Analysis ✅
- [x] Analyze NSRCG character format
- [x] Create import compatibility report
- [x] Design import strategy
- [x] Document character import process

### 9.3 MCP Tools ✅
- [x] Implement create_character tool
- [x] Implement update_character tool
- [x] Implement get_character tool
- [x] Add karma/experience tracking
- [x] Add house rules integration

### 9.4 Character Features ✅
- [x] Attribute management
- [x] Skill tracking (learn, improve, specialize)
- [x] Gear inventory
- [x] Essence tracking
- [x] Condition monitor (damage tracking)
- [x] Karma pool management
- [x] Character history logging
- [x] Campaign integration

---

## Phase 10: Campaign Management System ✅ COMPLETED

### 10.1 Database Schema ✅
- [x] Design campaigns table (fluid narrative state)
- [x] Design campaign_npcs table (dynamic NPC tracking)
- [x] Design campaign_characters table (character-campaign links)
- [x] Create migration 016_add_campaign_management.sql
- [x] Apply migration with UUID support

### 10.2 MCP Tools (Campaign State) ✅
- [x] Implement register_npc tool
- [x] Implement update_npc tool
- [x] Implement get_campaign_npcs tool
- [x] Implement update_campaign_state tool
- [x] All campaign management tools tested and working

### 10.3 Testing & Validation ✅
- [x] Test NPC registration during gameplay
- [x] Test NPC relevance transitions
- [x] Test campaign state updates
- [x] Validate context management
- [x] Comprehensive test suite passing (100%)

---

## Phase 11: Game Server & UI Integration 🚧 IN PROGRESS

### 11.1 Spellcasting System Implementation ✅ COMPLETED
**Status:** Fully Implemented and Tested  
**Documentation:** `docs/SPELLCASTING-SPEC.md`, `docs/SPELLCASTING-COMPLETE.md`

#### Phase 11.1.1: Core Mechanics (MVP) ✅
- [x] Implement `cast_spell()` method in `lib/mcp_operations.py`
- [x] Create master_spells table (migration 021)
- [x] Import 108 spells from SPELLS.csv
- [x] Implement DrainFormulaParser (handles all SR2 formulas)
- [x] Implement SpellcastingEngine with complete casting flow
- [x] Force validation against learned_force
- [x] Drain calculation with formula parsing
- [x] Willpower resistance rolls with Rule of 6
- [x] Damage calculation (drain - successes)
- [x] Comprehensive test suite (all tests passing)
- [x] Link character spells to master_spells database

**Completed:** 2025-10-28

#### Phase 11.1.2: Totem & Foci Support
- [ ] Implement totem bonus/penalty system (+2/-2 dice)
- [ ] Power foci integration (adds to Magic Pool)
- [ ] Spell foci support (specific & category)
- [ ] Fetish requirements and dice
- [ ] Enhanced dice pool calculation with all modifiers

**Estimated Effort:** 2 days

#### Phase 11.1.3: Spell Effects & Sustained Spells
- [ ] Combat spell damage calculation (Force + net successes)
- [ ] Detection spell information levels
- [ ] Health spell healing mechanics
- [ ] Illusion spell resistance
- [ ] Manipulation spell control
- [ ] Sustained spell tracking in `character_active_effects`
- [ ] Active effects creation and management

**Estimated Effort:** 3-4 days

#### Phase 11.1.4: Advanced Features (Future)
- [ ] Metamagic: Shielding
- [ ] Metamagic: Reflecting
- [ ] Metamagic: Centering
- [ ] Spell stacking (+2 TN per stacked spell)
- [ ] Multiple targets (split Force dice)
- [ ] Background count effects
- [ ] Attuned power sites

**Estimated Effort:** 4-5 days

### 11.2 Campaign Integration with Grok-4 ⏳
- [ ] Add campaign context injection to Grok-4 system prompt
- [ ] Implement dual-output pattern (narrative + state updates)
- [ ] Build campaign API endpoints in game-server.py
  - [ ] POST /api/campaign/create
  - [ ] GET /api/campaign/:id
  - [ ] PUT /api/campaign/:id/state
  - [ ] POST /api/campaign/:id/npc
  - [ ] PUT /api/campaign/:id/npc/:npc_id
- [ ] Test campaign state management during gameplay
- [ ] Validate NPC context in AI responses

### 11.3 UI Components for Campaign Management ⏳
- [ ] Create campaign creation modal
- [ ] Add campaign loading/selection interface
- [ ] Display active NPCs in sidebar
- [ ] Show current objectives/complications panel
- [ ] Add milestone tracking display
- [ ] Implement session linking to campaigns
- [ ] Add NPC quick-add from chat

### 11.4 Combat System Enhancement ⏳
- [ ] Expand ranged attack UI
  - [ ] Visual range calculator
  - [ ] Modifier breakdown display
  - [ ] Combat pool allocation interface
- [ ] Add melee combat support
  - [ ] Melee attack calculations
  - [ ] Reach and positioning
  - [ ] Called shots interface
- [ ] Implement full initiative tracker
  - [ ] Initiative order display
  - [ ] Turn management
  - [ ] Action tracking
  - [ ] Wound modifiers

### 11.4.1 Pool Allocation UI (Future Enhancement) 📋
**Goal:** Visual controls for allocating dice from various pools during actions

- [ ] **Combat Pool Sliders**
  - [ ] Add slider control to character sheet showing current combat pool
  - [ ] Integrate slider into ranged/melee attack UI
  - [ ] Show remaining pool after allocation
  - [ ] Validate allocation doesn't exceed maximum
  - [ ] Reset pool allocation between actions
  
- [ ] **Magic Pool Sliders** (for spellcasters)
  - [ ] Add slider for spellcasting dice allocation
  - [ ] Add slider for drain resistance dice allocation
  - [ ] Show total magic pool and remaining after allocation
  - [ ] Validate total allocation doesn't exceed magic rating
  
- [ ] **Hacking Pool Sliders** (for deckers)
  - [ ] Add slider for hacking action dice allocation
  - [ ] Show remaining hacking pool
  - [ ] Integrate with Matrix action UI
  - [ ] Validate allocation limits

- [ ] **Karma Pool Controls**
  - [ ] Add karma pool display to character sheet
  - [ ] Quick-access buttons for karma pool actions:
    - [ ] Reroll failures
    - [ ] Avoid disaster (Rule of One)
    - [ ] Buy extra dice
    - [ ] Buy successes
  - [ ] Show karma pool depletion in real-time

**Current Workaround:** AI asks user for pool allocation via chat  
**Estimated Effort:** 3-4 days for full implementation  
**Priority:** Medium (quality-of-life improvement)

**Related Issues:**
- Combat pool showing incorrect value (4 instead of 18) - FIXED in database
- Need `get_combat_pool` tool for AI to read correct values

### 11.5 Character Sheet Enhancements ⏳
- [ ] Complete character sheet renderer
  - [ ] Add spell list display
  - [ ] Add bound spirits display
  - [ ] Add foci display with bonuses
- [ ] Real-time updates via WebSocket
  - [ ] Damage tracking
  - [ ] Pool usage
  - [ ] Condition changes
- [ ] Character editing interface
  - [ ] Inline attribute editing
  - [ ] Skill improvement
  - [ ] Gear management
- [ ] Vehicle/cyberdeck displays
  - [ ] Vehicle stats and modifications
  - [ ] Cyberdeck programs and MPCP
  - [ ] Drone control interface

### 11.6 Testing & Validation ⏳
- [ ] End-to-end gameplay testing
- [ ] Campaign state persistence testing
- [ ] Multi-character combat testing
- [ ] WebSocket performance testing
- [ ] UI responsiveness testing

---

## Phase 12: Documentation Cleanup 📚 HIGH PRIORITY

### 12.1 Documentation Audit & Consolidation ⏳
**Goal:** Reduce 50+ markdown files to essential documentation

**ULTRATHINK REQUIRED:** The docs/ directory has become cluttered with:
- Status reports from every phase (PHASE-1-COMPLETE.md, PHASE-2-COMPLETE.md, etc.)
- Multiple overlapping guides (SCHEMA-FIX-GUIDE.md, SCHEMA-FIX-PLAN.md, SCHEMA-FIX-STATUS.md)
- Obsolete implementation plans
- Duplicate reference documents

#### Documentation Categories
- [ ] **Core Documentation** (Keep & Update)
  - README.md - Project overview
  - SETUP.md - Installation guide
  - ARCHITECTURE.md - System architecture
  - ROADMAP.md - Development roadmap
  - .clinerules - AI assistant rules
  
- [ ] **Reference Documentation** (Keep & Update)
  - docs/MCP-TOOLS-REFERENCE.md - MCP tool documentation
  - docs/ORCHESTRATOR-REFERENCE-V2.md - Orchestrator guide
  - docs/UI-REFERENCE.md - UI component reference
  - schema.sql - Authoritative database schema
  
- [ ] **Implementation Guides** (Consolidate)
  - Merge all SPELLCASTING-*.md → docs/guides/SPELLCASTING-GUIDE.md
  - Merge all SCHEMA-*.md → docs/guides/SCHEMA-GUIDE.md
  - Merge all CRUD-*.md → docs/guides/CRUD-API-GUIDE.md
  - Create docs/guides/TESTING-GUIDE.md
  - Create docs/guides/TOOL-DEVELOPMENT-GUIDE.md

- [ ] **Archive** (Move to docs/archive/)
  - All PHASE-*-COMPLETE.md files
  - All *-STATUS.md files (except FINAL-STATUS-REPORT.md)
  - All *-PLAN.md files (except CLEANUP-MASTER-PLAN.md)
  - All obsolete implementation docs

#### Consolidation Strategy
```
docs/
├── README.md (project overview)
├── MCP-TOOLS-REFERENCE.md (keep)
├── ORCHESTRATOR-REFERENCE-V2.md (keep)
├── UI-REFERENCE.md (keep)
├── FINAL-STATUS-REPORT.md (keep - current state)
├── CLEANUP-MASTER-PLAN.md (keep - active work)
├── guides/
│   ├── SETUP-GUIDE.md (installation & configuration)
│   ├── SPELLCASTING-GUIDE.md (consolidated)
│   ├── SCHEMA-GUIDE.md (consolidated)
│   ├── CRUD-API-GUIDE.md (consolidated)
│   ├── TESTING-GUIDE.md (new)
│   └── TOOL-DEVELOPMENT-GUIDE.md (new)
└── archive/
    ├── phase-reports/ (all PHASE-*.md)
    ├── status-reports/ (all *-STATUS.md)
    ├── implementation-plans/ (all *-PLAN.md)
    └── obsolete/ (outdated docs)
```

**Estimated Reduction: 50+ files → 15 files (70% reduction)**

---

## Phase 13: Tool Cleanup & Test Infrastructure 🔧 HIGH PRIORITY

### 13.1 Tool Consolidation & Refactoring ⏳
**Goal:** Reduce duplication, improve maintainability

#### Audit & Categorization
- [ ] Audit all Python scripts in `/tools/`
- [ ] Identify duplicate functionality
- [ ] Document tool dependencies
- [ ] Create tool inventory spreadsheet

#### Reorganization
- [ ] Create `/tools/import/` - Data import scripts
- [ ] Create `/tools/check/` - Validation/diagnostic scripts
- [ ] Create `/tools/fix/` - Repair/migration scripts
- [ ] Create `/tools/test/` - Test utilities
- [ ] Move scripts to appropriate categories
- [ ] Update all import paths

#### Consolidation
- [ ] Merge duplicate database connection patterns
- [ ] Create shared utilities library (`/tools/lib/`)
  - [ ] `db_utils.py` - Database connection helpers
  - [ ] `logging_utils.py` - Standardized logging
  - [ ] `validation_utils.py` - Common validation patterns
- [ ] Refactor scripts to use shared utilities
- [ ] Remove obsolete scripts (archive first)

#### Documentation
- [ ] Create `/tools/README.md` with tool catalog
- [ ] Document each tool's purpose and usage
- [ ] Add examples for common workflows
- [ ] Create troubleshooting guide

**Estimated Effort:** 3-4 days

### 12.2 Test Suite Infrastructure ⏳
**Goal:** Prevent database locking, enable parallel testing

#### Test Isolation
- [ ] Create separate test database configuration
- [ ] Implement transaction-based test isolation
  - [ ] Begin transaction before each test
  - [ ] Rollback after each test
  - [ ] Prevent permanent data changes
- [ ] Add test data fixtures
- [ ] Create test database reset script

#### Test Runner
- [ ] Create unified test runner (`tests/run_all_tests.py`)
- [ ] Implement sequential execution (no parallel)
- [ ] Add test categorization:
  - [ ] Unit tests (fast, no DB)
  - [ ] Integration tests (with DB)
  - [ ] End-to-end tests (full system)
- [ ] Add test filtering by category
- [ ] Implement proper cleanup between tests
- [ ] Add comprehensive reporting

#### Test Organization
- [ ] Reorganize tests by category
  - [ ] `/tests/unit/` - Pure logic tests
  - [ ] `/tests/integration/` - Database tests
  - [ ] `/tests/e2e/` - Full system tests
- [ ] Create test base classes with common setup
- [ ] Add test utilities for common operations
- [ ] Document testing best practices

#### CI/CD Preparation
- [ ] Create test database Docker container
- [ ] Add GitHub Actions workflow (future)
- [ ] Create test coverage reporting
- [ ] Add performance benchmarks

**Estimated Effort:** 4-5 days

### 12.3 Code Quality Improvements ⏳
- [ ] Add type hints to Python code
- [ ] Implement linting (pylint, flake8)
- [ ] Add code formatting (black)
- [ ] Create pre-commit hooks
- [ ] Document coding standards

**Estimated Effort:** 2-3 days

---

## Phase 13: Setting & Lore Database ⏳ FUTURE

### 12.1 Schema Design ⏳
- [ ] Design lore_content table
  - [ ] Locations
  - [ ] Corporations
  - [ ] Timeline events
  - [ ] Factions
- [ ] Add relationship mapping
- [ ] Create cross-reference system

### 12.2 MCP Tools ⏳
- [ ] Implement query_lore tool (already partially working via chunks)
- [ ] Implement get_location tool
- [ ] Implement get_corporation tool
- [ ] Implement timeline_lookup tool

### 12.3 Content Population ⏳
- [ ] Extract lore from source books
- [ ] Organize by category
- [ ] Add cross-references
- [ ] Link to relevant rules

---

## Phase 14: Advanced AI Features ⏳ FUTURE

### 13.1 AI Enhancements ⏳
- [ ] Add rule interpretation assistance
- [ ] Implement scenario suggestions
- [ ] Create encounter generators
- [ ] Improve query classification accuracy
- [ ] Add NPC personality generation
- [ ] Implement plot twist suggestions

### 13.2 Session Management ⏳
- [ ] Session notes storage
- [ ] Plot thread management
- [ ] Location/scene tracking
- [ ] Session recap generation
- [ ] Automatic session summaries
- [ ] Player action tracking

### 13.3 Advanced Combat AI ⏳
- [ ] Tactical AI for NPCs
- [ ] Cover and positioning suggestions
- [ ] Optimal action recommendations
- [ ] Threat assessment

---

## Current Status Summary

### ✅ Completed (Phases 1-8)
- **Phase 1:** Complete rules system with MCP server
- **Phase 2:** Full data migration from OCR files
- **Phase 3:** Cline integration and testing
- **Phase 4:** Enhanced search with AI classification
- **Phase 5:** Complete gear database with 3 tools
- **Phase 6:** Magical systems (spells, powers, totems)
- **Phase 7:** Complete dice rolling system (15 tools)
- **Phase 8:** Unified server with 19 total tools

### ✅ Recently Completed (Phase 10)
- Campaign management system fully implemented
- All campaign MCP tools working and tested
- NPC tracking with relevance system operational
- Campaign state management (objectives, complications, milestones)
- Comprehensive test suite passing (100%)

### ✅ Magic System Enhancements (Recent)
- Totem support fully implemented (migration 015)
- Spellcasting MCP tool with drain calculation
- Totem bonus/penalty system with case-insensitive matching
- Magic fields added to character schema (migration 017)
- All spellcasting tests passing (7/7)

### 🎯 Current Priorities

**IMMEDIATE: CRUD API & MCP Operations (Phase 11.6)**
- [x] Migration 019: Audit system with users table
- [x] Migration 020: Fix character_powers UUID
- [x] Python CRUD API (`lib/comprehensive_crud.py`) with full schema compliance
- [x] All schema mismatches fixed (11 tables)
- [x] Karma & Nuyen management functions added
- [x] Hybrid Search (`lib/hybrid_search.py`) for RAG supplementation
- [x] Updated MCP-TOOLS-REFERENCE.md (added Python libraries section)
- [x] Created comprehensive CRUD test suite (45+ operations tested)
- [ ] **TODO: Split magical items (foci, fetishes, talismans) from gear table**
  - [ ] Create character_magical_items table
  - [ ] Migrate foci/fetishes/talismans from gear
  - [ ] Update CRUD API with magical item operations
  - [ ] Update UI to display magical items separately
- [ ] **IN PROGRESS: Update MCP operations to use new CRUD API**
  - [ ] Update lib/mcp_operations.py to use comprehensive_crud.py
  - [ ] Add karma/nuyen management MCP tools
  - [ ] Test all MCP operations with new CRUD backend
- [ ] **UPDATE: docs/ORCHESTRATOR-REFERENCE.md**
- [ ] **UPDATE: docs/UI-REFERENCE.md**
- [ ] **UPDATE: README.md with architecture overview**

**1. Game Server Integration (Phase 11)**
- Integrate campaign management into game-server.py
- Add campaign context to Grok-4 AI calls
- Build UI components for campaign management
- Test end-to-end gameplay with campaigns
- **Integrate Python CRUD API and Hybrid Search into game-server.py MCP tools**

**2. Combat System Enhancement**
- Expand ranged attack calculations
- Add melee combat support
- Implement full initiative system
- Add combat pool management UI

**3. Character Sheet UI Polish**
- Complete character sheet renderer
- Add real-time updates via WebSocket
- Implement character editing interface
- Add vehicle/cyberdeck displays

### 🔮 Future Enhancements (Phases 10-11)
- Dedicated lore database
- Campaign management tools
- AI-powered GM assistance
- Encounter generators

---

## Tool Inventory

### Query & Search Tools (4)
1. ✅ query_shadowrun - Unified query with AI routing

### Gear Tools (3)
2. ✅ lookup_gear - Search gear by criteria
3. ✅ compare_gear - Compare and rank gear
4. ✅ get_gear_details - Get complete gear info with chunks

### Dice Rolling Tools (15)
5. ✅ roll_dice - Basic dice rolling
6. ✅ roll_multiple_dice - Roll multiple dice types
7. ✅ roll_with_advantage - D&D advantage mechanic
8. ✅ roll_with_disadvantage - D&D disadvantage mechanic
9. ✅ roll_with_target_number - Shadowrun TN rolls
10. ✅ roll_opposed - Shadowrun opposed rolls
11. ✅ roll_initiative - Initiative rolling
12. ✅ track_initiative - Multi-character initiative
13. ✅ roll_with_pools - Dice pool system
14. ✅ roll_opposed_pools - Opposed pool rolls
15. ✅ reroll_failures - Karma Pool re-rolls
16. ✅ avoid_disaster - Rule of One protection
17. ✅ buy_karma_dice - Buy extra dice
18. ✅ buy_successes - Buy raw successes

### Character Tools (3) ✅
19. ✅ create_character - Create new characters with attributes, skills, resources
20. ✅ update_character - Update characters with karma tracking and house rules
21. ✅ get_character - Retrieve character data with history and modifiers

### Campaign & House Rules Tools (6) ✅
22. ✅ create_campaign - Create new campaigns with theme and description
23. ✅ update_campaign_state - Update situation, location, objectives, complications
24. ✅ add_campaign_milestone - Record major achievements
25. ✅ register_npc - Add NPCs with relevance tracking
26. ✅ update_npc - Update NPC status, location, relevance
27. ✅ get_campaign_npcs - Retrieve NPCs by relevance or location

### Magic & Spellcasting Tools (1) ✅
28. ✅ cast_spell - Full spellcasting with drain calculation and resistance

**Total Tools:** 28 implemented

**Latest Addition (2025-10-28):**
- ✅ cast_spell - Complete Shadowrun 2nd Edition spellcasting mechanics
  - Drain formula parsing (all SR2 formulas supported)
  - Force validation and variable-force spell handling
  - Willpower resistance rolls with Rule of 6
  - Damage calculation (drain - successes)
  - Integration with master_spells database (108 spells)
  - Comprehensive test coverage

---

## Success Metrics

### Phase 1-8 (Completed): ✅
- ✅ Server starts without errors
- ✅ Database connection successful
- ✅ All 18 tools functional
- ✅ Query response time < 500ms
- ✅ AI classification working (needs refinement)
- ✅ Gear database populated
- ✅ Magical systems integrated
- ✅ Dice rolling complete

### Phase 9 (Completed): ✅
- [x] Character schema applied and migrated
- [x] Character tools implemented and tested
- [x] House rules system integrated
- [x] Campaign management working
- [x] Character data validated

### Phase 10 (Completed): ✅
- [x] Campaign management schema implemented
- [x] All 6 campaign MCP tools working
- [x] NPC tracking with relevance system
- [x] Campaign state management operational
- [x] Comprehensive testing (100% pass rate)
- [x] Magic system with totem support
- [x] Spellcasting tool with drain calculation

---

## Known Issues & Improvements

### High Priority
1. **Query Classification Accuracy** (QUERY-SYSTEM-STATUS.md)
   - Spell/power/totem queries sometimes misrouted
   - Need better AI prompt examples
   - Add classification logging

### Medium Priority
2. **Character Management**
   - Implement remaining character tools
   - Build NSRCG import system
   - Add character validation

### Low Priority
3. **Documentation**
   - Update tool usage examples
   - Add video tutorials
   - Create migration guide updates

---

## Technology Stack

### Core Technologies
- **Database:** PostgreSQL via Supabase (local Docker)
- **Vector Search:** pgvector extension
- **MCP SDK:** @modelcontextprotocol/sdk v1.19.1
- **Node.js:** ES modules (type: "module")
- **AI:** OpenAI GPT-4o-
