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

## Phase 10: Setting & Lore Database ⏳ FUTURE

### 10.1 Schema Design ⏳
- [ ] Design lore_content table
  - [ ] Locations
  - [ ] Corporations
  - [ ] NPCs
  - [ ] Timeline events
  - [ ] Factions
- [ ] Add relationship mapping
- [ ] Create cross-reference system

### 10.2 MCP Tools ⏳
- [ ] Implement query_lore tool (already partially working via chunks)
- [ ] Implement get_location tool
- [ ] Implement get_corporation tool
- [ ] Implement timeline_lookup tool

### 10.3 Content Population ⏳
- [ ] Extract lore from source books
- [ ] Organize by category
- [ ] Add cross-references
- [ ] Link to relevant rules

---

## Phase 11: Advanced Features ⏳ FUTURE

### 11.1 Campaign Management ⏳
- [ ] Session notes storage
- [ ] NPC tracking
- [ ] Plot thread management
- [ ] Location/scene tracking

### 11.2 AI Enhancements ⏳
- [ ] Add rule interpretation assistance
- [ ] Implement scenario suggestions
- [ ] Create encounter generators
- [ ] Add house rule management

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

### ✅ Recently Completed (Phase 9)
- Character management system fully implemented
- Schema migrated to normalized structure
- All 3 character tools working (create, get, update)
- Comprehensive testing completed
- House rules integration working

### 🎯 Current Priority: Query Router Refinement

**Issue Identified:** Query classification needs improvement for spell/power/totem queries
- AI sometimes misclassifies structured queries as text chunk queries
- Need better examples in classification prompt
- See QUERY-SYSTEM-STATUS.md for details

**Next Steps:**
1. Fix query classification prompt with better examples
2. Add logging to track classification accuracy
3. Test with various query types
4. Fine-tune based on results

### ⏳ Next Major Phase (Phase 9)
1. **Implement Character Management Tools**
   - create_character
   - update_character
   - get_character
   - calculate_derived_stats
2. **Character Import System**
   - NSRCG file parser
   - Data validation
   - Import tool

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

### Campaign & House Rules Tools (2) ✅
22. ✅ manage_campaigns - Full campaign management
23. ✅ manage_house_rules - House rules with campaign support

**Total Tools:** 23 implemented

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
